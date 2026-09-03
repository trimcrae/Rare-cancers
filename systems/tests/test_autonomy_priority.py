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
    second home for it, and the two will disagree.

    ⚠ THE REGEX MUST NOT SWALLOW TRAILING PUNCTUATION. `\\$[0-9][0-9,.]*` matched "$0," inside
    ordinary prose ("a $0, few-minutes fix") as if the comma were a thousands-separator digit
    group, which is not a restated price at all — a linter that flags true prose gets switched
    off (CLAUDE.md §6, `lint_claims`'s founding lesson). The pattern now requires every comma/
    period to be followed by more digits, so a figure like "$1,234.56" still matches in full
    while "$0," followed by a word does not.
    """
    ledger = priority.build_ledger()
    blob = json.dumps(ledger)
    import re

    prices = {m for m in re.findall(r"\$[0-9]+(?:[.,][0-9]+)*", blob)} - {"$0"}
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
        "blocked_with_evidence",
        "age",
        # ⛔ ADDED 2026-09-02. The accrued-debt term — see priority-weights.json's `why`, which
        # records the six rows that measured the same defect and the zero attempts they drew.
        "recurring_cost",
    }
    assert declared == expected, (
        "the scorer's terms and the weights file have diverged — one of them was edited alone"
    )
    source = PRIORITY_PY.read_text()
    # ⚠ "age" is read defensively (`((weights.get("terms") or {}).get("age") or {}).get("weight")`
    # in apply_age_factor) rather than by direct subscript, on purpose: a missing/malformed
    # weights file must disable the anti-starvation term rather than crash the ranker
    # (test_an_unreadable_saturation_disables_the_term_rather_than_dividing_by_zero pins this).
    # It still reads the weight from the file, just not via the literal bracket pattern the other
    # terms use inside the single weighted-sum expression in build_entries.
    # ⚠ `recurring_cost` joins these for `age`'s exact reason and by copying its shape: it is read
    # as `((weights.get("terms") or {}).get("recurring_cost") or {}).get("weight")` so that a
    # missing or malformed weights file DISABLES the term rather than crashing the ranker — which
    # matters more here than for `age`, because this term is what makes the loop take its own
    # infrastructure debt, and a ranker that will not run takes nothing at all.
    DEFENSIVE_READ_TERMS = {"fruitless_attempts", "age", "recurring_cost"}
    for term in expected:
        assert f'terms["{term}"]["weight"]' in source or term in DEFENSIVE_READ_TERMS, (
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


def test_adding_a_route_to_the_graph_changes_no_existing_id(priority, tmp_path):
    """⛔⛔ THE PROPERTY, TESTED DIRECTLY, BECAUSE TESTING THE REPAIR IS WHAT MISSED IT FOR A WEEK.

    ⚠ SUPERSEDED, RETAINED (CLAUDE.md rule 1.2). This test used to hand `merge()` a prior ledger in
    which one route held `AUT-777`, and assert the merged row kept it. That passed throughout, and
    the bug was live the whole time: it measured whether `merge()` DONATES a remembered id, not
    whether growing the graph moves one. `build_entries()` is what mints, three modules call it raw,
    and a fresh ledger has no prior row to donate anything — so the guard was one caller deep in the
    same way the code was.

    ⭐ Measured on the live graph, 2026-09-03 (AUT-PD-215), before any code changed: adding ONE route
    whose id sorts early moved 76 of 77 ids and took AUT-073 — the escalation trimcrae answered on
    2026-09-01 — from RT-TRIAL-REACH to RT-TRABECTEDIN-PPARG. This asserts the whole set, not a spot
    check, because 76 of 77 moving is what "a spot check would probably notice" looks like when the
    one that did not move is the one you happened to pick.
    """
    import copy, json, shutil, sys
    sys.path.insert(0, str(REPO / "research" / "autonomy"))
    import derived_ids

    real_load = priority._load
    routes = copy.deepcopy(real_load("routes.json"))
    before = {e["id"]: e["serves"]["route"] for e in priority.build_entries()}
    assert before.get("AUT-073"), "fixture is degenerate — no AUT-073 to move"

    extra = copy.deepcopy(routes[0])
    extra["id"] = "RT-AAA-A-ROUTE-THAT-SORTS-FIRST"
    grown = routes + [extra]

    map_path, ledger_path = tmp_path / "map.json", tmp_path / "ledger.json"
    routes_path = tmp_path / "routes.json"
    shutil.copy(REPO / "research" / "autonomy" / "derived-ledger-ids.json", map_path)
    shutil.copy(REPO / "research" / "autonomy" / "research-ledger.json", ledger_path)
    routes_path.write_text(json.dumps(grown))

    added = derived_ids.extend(map_path=map_path, ledger_path=ledger_path, routes_path=routes_path)
    assert [r for r, _ in added] == ["RT-AAA-A-ROUTE-THAT-SORTS-FIRST"]

    table = derived_ids.bindings(map_path)
    real_bindings = derived_ids.bindings
    priority._load = lambda name: grown if name == "routes.json" else real_load(name)
    derived_ids.bindings = lambda path=None: table
    try:
        after = {e["id"]: e["serves"]["route"] for e in priority.build_entries()}
    finally:
        priority._load = real_load
        derived_ids.bindings = real_bindings

    moved = sorted(i for i in before if before[i] != after.get(i))
    assert not moved, (
        f"{len(moved)} of {len(before)} ids came to name a different route when ONE route was added "
        f"— e.g. {moved[:3]}. Every receipt, commit message and cross-reference citing one of those "
        f"now means something else, and nothing anywhere goes red."
    )
    assert len(after) == len(before) + 1, "the new route got no row of its own"


def test_a_route_with_no_frozen_binding_is_refused_rather_than_minted_an_id(priority):
    """⛔ THE MINT IS THE DEFECT, SO THERE MUST BE NO FALLBACK MINT.

    ⚠ SUPERSEDED, RETAINED (rule 1.2): this asserted that a new route got an UNUSED id rather than
    colliding — the right question about the wrong mechanism. A number that is merely unused is
    still one nobody decided, and the id it does not collide with today is the one it silently
    becomes tomorrow. An unbound route now fails loudly and names `--extend`, because the remedy
    has to be reachable from the error or the next session invents a number instead.
    """
    import copy
    real_load = priority._load
    grown = copy.deepcopy(real_load("routes.json"))
    orphan = copy.deepcopy(grown[0])
    orphan["id"] = "RT-ZZZ-BOUND-TO-NOTHING"
    grown.append(orphan)
    priority._load = lambda name: grown if name == "routes.json" else real_load(name)
    try:
        with pytest.raises(KeyError) as caught:
            priority.build_entries()
    finally:
        priority._load = real_load
    message = str(caught.value)
    assert "RT-ZZZ-BOUND-TO-NOTHING" in message, "the refusal does not say which route"
    assert "--extend" in message, (
        "the refusal does not name the remedy, so the next session mints a number by hand — which "
        "is the defect wearing a different hat"
    )


def test_the_merge_is_load_bearing_and_not_decorative(priority):
    """Mutation test: bypass merge entirely and the preservation must actually break."""
    existing = {"entries": [{"id": "AUT-PROP-999", "kind": "process_defect",
                             "serves": {"route": None}, "state": "queued"}]}
    unmerged = priority.build_entries()  # what --write did before the fix
    assert not any(e["id"] == "AUT-PROP-999" for e in unmerged), (
        "the hand-added entry survived WITHOUT merge() — so merge is not what preserves it and "
        "these tests are blind"
    )


# ---------------------------------------------------------------- blocks and prerequisites
#
# ⛔ ALL THREE OF THESE WERE LIVE BUGS, found by CYC-0001 running the contract for real. Together
# they would have made the loop spend every cycle, forever, re-deriving the same block on the same
# top-ranked paper while the only work that could clear it stayed invisible.


def test_an_evidenced_block_drops_out_of_the_queue(priority):
    """Otherwise the next cycle re-derives the identical block, and the one after that, every four
    hours. An UNevidenced block is a different animal — its clamp turns it into a free re-test."""
    ledger = priority.build_ledger()
    blocked = [e for e in ledger["entries"]
               if str(e.get("blocked_evidence") or "").strip() and e.get("score") is not None]
    assert blocked, "fixture is degenerate — no evidenced block to check"
    top = [e for e in ledger["entries"] if e.get("score") is not None][:3]
    for entry in blocked:
        assert entry["id"] not in {t["id"] for t in top}, (
            f"{entry['id']} carries its own block evidence and is still in the top 3 — the next "
            "cycle will take it and re-derive the same block"
        )


def test_a_prerequisite_outranks_the_thing_it_unblocks(priority):
    ledger = priority.build_ledger()
    by_id = {e["id"]: e for e in ledger["entries"]}
    prereqs = [e for e in ledger["entries"] if e.get("prerequisite_of")]
    assert prereqs, "fixture is degenerate — no prerequisite filed"
    for entry in prereqs:
        parent = by_id[entry["prerequisite_of"]]
        assert entry["score"] > parent["score"], (
            f"{entry['id']} is the only path to {parent['id']} and scores below it — the driver "
            "would never take it, and the parent would stay blocked indefinitely"
        )


def test_a_prerequisite_inherits_the_parents_value_not_its_penalty(priority):
    """The prerequisite is worth what the parent is worth ONCE UNBLOCKED. Inheriting the penalised
    score would bury the fix underneath the problem it fixes.

    ⚠ THE COMPARISON IS AGAINST THE CHILD'S OWN UNBLOCKED VALUE, AND IT DID NOT USED TO BE — the
    correction is AUT-PD-063, 2026-08-28, and it is a CORRECTION rather than a relaxation: not one
    row leaves the loop, and the quantity compared is the one the docstring above always named.
    ⛔ THE SIGN IS NOT A TYPO. `penalty` is NEGATIVE (-90.0), so `parent["score"] - penalty / 2`
    reads parent + 45: the midpoint between the parent's PENALISED score and its UNPENALISED one.
    A child that inherited the penalty lands at the bottom of that interval and a child that
    inherited the value lands at the top, so the midpoint is exactly the discriminator, and it was
    checked before it was touched.
    ⛔ WHAT WAS WRONG WAS THE OTHER SIDE. The old form compared the parent's un-penalised value to
    the child's FINAL score — which includes any penalty the CHILD carries for a block of its own.
    A prerequisite may perfectly well record its own evidenced block (AUT-PROP-018 does), and such a
    row must still stand down: -90 for itself, on top of a correctly inherited value. The old form
    could not tell that apart from the defect it is named for, so it read a correct scorer as broken
    and would have been "fixed" by deleting the child's own penalty — which is the bug, not the fix.
    It never fired that way only because the penalty used to be ERASED by the inheritance, so no row
    ever reached it carrying one.
    """
    weights = priority.load_weights()
    penalty = weights["terms"]["blocked_with_evidence"]["weight"]
    ledger = priority.build_ledger()
    by_id = {e["id"]: e for e in ledger["entries"]}

    def _records_its_own_block(row):
        # The same key the scorer uses: the recorded observation IS the block.
        return bool(str(row.get("blocked_evidence") or "").strip())

    for entry in [e for e in ledger["entries"] if e.get("prerequisite_of")]:
        parent = by_id[entry["prerequisite_of"]]
        if parent["score_inputs"].get("blocked_with_evidence"):
            inherited = entry["score"] - (penalty if _records_its_own_block(entry) else 0)
            assert inherited > parent["score"] - penalty / 2, (
                "the prerequisite inherited the parent's PENALISED score"
            )


def test_a_hand_filed_row_never_steals_a_derived_rows_id(priority):
    """⛔ MEASURED: keying the merge's route map on ANY prior row let AUT-PROP-004 ('escalate the
    emails') hand its id to the graph's 'post the preprint' row, and the real AUT-PROP-004 vanished.
    Two rows legitimately serve one route — the work and the thing blocking it — so a route is not
    an identity."""
    generated = priority.build_entries()
    route, frozen_id = generated[0]["serves"]["route"], generated[0]["id"]
    # ⚠ THE PRIOR DERIVED ROW CARRIES ITS REAL ID, NOT AN INVENTED ONE. This fixture used to give it
    # `AUT-500`, which since AUT-PD-215 is itself a defect — the frozen map and the ledger
    # disagreeing about what an id means — and `merge()` now refuses it by name. The subject of this
    # test was never the derived row's number; it is that a hand-filed row serving the same route
    # neither donates its id nor disappears.
    existing = {"entries": [
        dict(generated[0]),                                                   # the derived row
        {"id": "AUT-PROP-777", "serves": {"route": route}, "kind": "harden",  # a hand-filed row
         "what": "unblock it", "state": "queued", "filed_by": "CYC-TEST"},
    ]}
    merged = priority.merge(priority.build_entries(), existing)
    derived_row = [e for e in merged if e["serves"].get("route") == route and e.get("_derived")][0]
    assert derived_row["id"] == frozen_id, (
        f"the derived row took id {derived_row['id']} from the hand-filed one"
    )
    assert any(e["id"] == "AUT-PROP-777" for e in merged), "the hand-filed row was lost"


def test_every_derived_entry_is_marked_as_derived(priority):
    """`_derived` is what lets merge tell the scorer's rows from a session's. If it stops being
    written, the id-theft bug above returns silently."""
    assert all(e.get("_derived") for e in priority.build_entries())
