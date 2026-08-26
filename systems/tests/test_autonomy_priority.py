"""Guards on the autonomy loop's scorer — research/autonomy/priority.py.

The scorer decides what an unattended research cycle works on next, so a defect here is not a
wrong number in a table: it is weeks of the program spent on the wrong thing, silently. These
tests bind the three properties that cannot be re-derived by reading the output.

⛔ WHY EACH ONE EXISTS — in every case a WEIGHT alone was insufficient:

1. `negative_never_outranks_live` — CLAUDE.md §0 ("a negative is a byproduct, never the
   objective"). The portfolio's highest-graded route today is RT-METHODS-PAPER, graded
   "Tier 1, rank 1 — DELIVERABLE", and it is a write-up of the program's own failure record.
   Any weighting generous enough to rank genuine deliverables will eventually rank that first.
2. `never reads Axis D` — the options memo grades partly on what we hold if the experiment
   never happens, which promotes finished work by construction. CLAUDE.md §0 calls it a
   tiebreaker, never a work queue.
3. `blocked without evidence becomes a check` — CLAUDE.md §0: "blocked" is a claim that needs
   evidence and it is usually wrong. Dropping such rows from the queue is how a route that
   needed one $0 fetch stays dead for months.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
PRIORITY_PY = REPO / "research" / "autonomy" / "priority.py"
WEIGHTS_JSON = REPO / "research" / "autonomy" / "priority-weights.json"


def _import_priority():
    spec = importlib.util.spec_from_file_location("autonomy_priority", PRIORITY_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def priority():
    return _import_priority()


@pytest.fixture(scope="module")
def entries(priority):
    return priority.build_entries()


def test_the_scorer_produces_an_entry_for_every_route(priority, entries):
    routes = json.loads((REPO / "systems" / "graph" / "routes.json").read_text())
    assert len(entries) == len(routes), (
        "every route must be visible in the queue. A route the scorer silently drops is a "
        "route no cycle will ever take."
    )


def test_no_negative_write_up_outranks_any_live_route(entries):
    """Clamp 1. The single most important property in the file."""
    live = [e["score"] for e in entries if e["score_inputs"]["live"]]
    negatives = [e["score"] for e in entries if e["kind"] == "negative"]
    assert live and negatives, "fixture is degenerate — this test would pass vacuously"
    assert max(negatives) < min(live), (
        f"a negative/methods entry scored {max(negatives)} against a live route at "
        f"{min(live)}. CLAUDE.md §0: negatives wait behind anything live."
    )


def test_the_clamp_is_load_bearing_and_not_merely_decorative(priority):
    """Mutation test: disable the clamp and the property must actually break.

    A guard that passes with the mechanism removed is guarding nothing. `paper-hardening`
    records seven one-of-a-pair defects found exactly this way.
    """
    weights = priority.load_weights()
    weights["clamps"]["negative_never_outranks_live"]["enabled"] = False
    weights["terms"]["tier_one"]["weight"] = 10_000.0  # a plausible mis-weighting
    unclamped = priority.build_entries(weights)

    live = [e["score"] for e in unclamped if e["score_inputs"]["live"]]
    negatives = [e["score"] for e in unclamped if e["kind"] == "negative"]
    assert max(negatives) > min(live), (
        "with the clamp disabled and Tier 1 over-weighted, a negative did NOT outrank a live "
        "route — so the clamp is not what is holding the property, and this suite is blind."
    )

    weights["clamps"]["negative_never_outranks_live"]["enabled"] = True
    reclamped = priority.build_entries(weights)
    live = [e["score"] for e in reclamped if e["score_inputs"]["live"]]
    negatives = [e["score"] for e in reclamped if e["kind"] == "negative"]
    assert max(negatives) < min(live), "re-enabling the clamp did not restore the property"


def test_the_scorer_never_reads_axis_d(priority, entries):
    """Clamp 2, asserted against the score_inputs rather than against the source text.

    Checking the source for a string would pass the moment someone renamed the field. The
    binding property is that no input to a score is an Axis-D-shaped judgement.
    """
    forbidden = set(json.loads(WEIGHTS_JSON.read_text())["_forbidden_inputs"])
    for entry in entries:
        leaked = forbidden & set(entry["score_inputs"])
        assert not leaked, f"{entry['id']} scored on a forbidden input: {leaked}"


def test_a_block_without_evidence_becomes_a_free_check_not_a_dropped_row(entries):
    """Clamp 3."""
    blocked_rows = [e for e in entries if e["blocked_by"] and not e["blocked_evidence"]]
    assert blocked_rows, "fixture is degenerate — no blocked-without-evidence rows to check"
    for entry in blocked_rows:
        assert entry["kind"] == "fetch", (
            f"{entry['id']} is blocked with no recorded evidence but was left as "
            f"kind={entry['kind']}. It must be re-emitted as a check that re-tests the block."
        )
        assert entry["cost_class"] == "free"
        assert entry["state"] == "queued", "a re-test is queued work, not a blocked row"


def test_no_dollar_figure_is_ever_written_into_the_ledger(priority):
    """CLAUDE.md rule 1: pricing.md owns every cost. A ledger that carries a price is a
    second home for it, and the two will disagree."""
    ledger = priority.build_ledger()
    blob = json.dumps(ledger)
    import re

    prices = {m for m in re.findall(r"\$[0-9][0-9,.]*", blob)} - {"$0"}
    assert not prices, (
        f"the ledger carries dollar figures {sorted(prices)}. Entries point at their rung via "
        "cost_points_at; they never restate a price."
    )


def test_every_weight_the_scorer_applies_is_declared_in_the_weights_file(priority):
    """No weight may be typed in the code. The weights file is the one home, so that changing
    a research priority is a reviewable diff rather than a buried constant."""
    weights = priority.load_weights()
    declared = set(weights["terms"])
    expected = {
        "live",
        "patient_path",
        "pursue_now",
        "tier_one",
        "endpoint_reachable",
        "blocker_leverage",
        "cost",
        "blocked_on_human",
        "fruitless_attempts",
    }
    assert declared == expected, (
        "the scorer's terms and the weights file have diverged — one of them was edited alone"
    )
    source = PRIORITY_PY.read_text()
    for term in expected:
        assert f'terms["{term}"]["weight"]' in source or term == "fruitless_attempts", (
            f"term {term} is declared but the scorer does not read its weight from the file"
        )


def test_the_ranking_is_deterministic(priority):
    """A cycle re-scores every time. Two runs that disagree make every receipt unreadable."""
    first = [e["serves"]["route"] for e in priority.build_entries()]
    second = [e["serves"]["route"] for e in priority.build_entries()]
    assert first == second


# ---------------------------------------------------------------- merge-on-write
#
# ⛔ THESE GUARD A DATA-LOSS BUG THAT WAS LIVE, not a hypothetical. Found by running the first real
# cycle by hand (receipt CYC-0001): step 3 of EVERY cycle re-scores with `--write`, which rebuilt all
# 77 entries from the graph and silently destroyed the hand-added entry, every `owner`, and every
# `attempts`/`blocked_evidence`. The ledger is the loop's only memory, and `--write` was erasing it
# on a four-hour cadence.


def test_a_hand_added_entry_survives_a_rescore(priority):
    """The ledger's own `_role` says a session may add an entry the graph cannot express. If a
    re-score deletes it, every filed proposal and process_defect evaporates within four hours."""
    existing = {"entries": [
        {"id": "AUT-PROP-999", "kind": "process_defect", "serves": {"route": None},
         "what": "a filed proposal", "state": "queued"},
    ]}
    merged = priority.merge(priority.build_entries(), existing)
    assert any(e["id"] == "AUT-PROP-999" for e in merged), (
        "a hand-filed entry was dropped by the re-score — the loop cannot remember its own findings"
    )


def test_claiming_an_item_survives_the_next_rescore(priority):
    """Step 4 of the contract says claim the item before working. If step 3 of the NEXT cycle wipes
    the owner, two cycles take the same item — which is exactly the 'work with no owner is
    indistinguishable from work in progress' failure the ledger exists to prevent."""
    generated = priority.build_entries()
    route = generated[0]["serves"]["route"]
    existing = {"entries": [dict(generated[0], owner="CYC-TEST", attempts=2, state="running")]}
    merged = priority.merge(priority.build_entries(), existing)
    row = [e for e in merged if e["serves"].get("route") == route][0]
    assert row["owner"] == "CYC-TEST"
    assert row["attempts"] == 2
    assert row["state"] == "running", "a session-set state must not be reverted to the derived one"


def test_blocked_evidence_is_never_discarded(priority):
    """`blocked_evidence` is the observation that justified a block. Losing it turns a
    substantiated block back into the unevidenced kind CLAUDE.md §0 says is usually wrong."""
    generated = priority.build_entries()
    route = generated[0]["serves"]["route"]
    existing = {"entries": [dict(generated[0], blocked_evidence="observed 2026-08-26: 404 at source")]}
    merged = priority.merge(priority.build_entries(), existing)
    row = [e for e in merged if e["serves"].get("route") == route][0]
    assert row["blocked_evidence"] == "observed 2026-08-26: 404 at source"


def test_an_entry_id_is_stable_when_the_graph_grows(priority):
    """⭐ THE QUIETER HALF OF THE BUG. Ids were `AUT-{index+1}` over sorted routes, so adding ONE
    route renumbered everything after it — and `AUT-049` written into a receipt would afterwards
    name a different route. That is a silent rewrite of the historical record."""
    generated = priority.build_entries()
    target = generated[10]
    route, original_id = target["serves"]["route"], target["id"]
    # Simulate a prior ledger in which this route already holds a very different id.
    existing = {"entries": [dict(target, id="AUT-777")]}
    merged = priority.merge(priority.build_entries(), existing)
    row = [e for e in merged if e["serves"].get("route") == route][0]
    assert row["id"] == "AUT-777", (
        f"the id was reassigned from AUT-777 to {row['id']} — receipts naming the old id now point "
        "at whatever route landed in that slot"
    )
    assert original_id != "AUT-777", "fixture is degenerate"


def test_a_new_route_gets_an_unused_id_rather_than_colliding(priority):
    generated = priority.build_entries()
    existing = {"entries": [{"id": "AUT-900", "serves": {"route": None}, "kind": "process_defect"}]}
    merged = priority.merge(priority.build_entries(), existing)
    ids = [e["id"] for e in merged]
    assert len(ids) == len(set(ids)), "id collision after a merge"
    assert "AUT-900" in ids


def test_the_merge_is_load_bearing_and_not_decorative(priority):
    """Mutation test: bypass merge entirely and the preservation must actually break."""
    existing = {"entries": [{"id": "AUT-PROP-999", "kind": "process_defect",
                             "serves": {"route": None}, "state": "queued"}]}
    unmerged = priority.build_entries()  # what --write did before the fix
    assert not any(e["id"] == "AUT-PROP-999" for e in unmerged), (
        "the hand-added entry survived WITHOUT merge() — so merge is not what preserves it and "
        "these tests are blind"
    )
