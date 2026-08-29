#!/usr/bin/env python3
"""An unscored ledger row is invisible work, not absent work (AUT-PD-143).

⛔⛔ THE DEFECT. `build_entries` is the ONLY place a `score` is created, and it derives rows from
`systems/graph`; `merge()` carries a hand-filed row forward verbatim. So a row filed without a
`score` key could never gain one on any re-score, ever. Four readers then treated that absence as
"not work" — the sort's -1e9 sentinel, `_table` (which CRASHED rather than printing such a row),
`health.py`'s `queue_is_takeable`, and `handoff.py`'s successor queue. Measured 2026-08-28 on the
committed ledger: 104 of 277 entries carried no score, 74 of them OPEN, including live in-silico
work on RT-SGK1, RT-ALK-HIT and RT-JUNCTION-NEOANTIGEN — none of it ever offered to a cycle, while
the ranked queue's top takeable rows were the loop's own process defects. CLAUDE.md §0's named
failure arriving as a missing dict key rather than as a judgement.

★ THE INVARIANTS THIS FILE BINDS, and each is a thing that was got wrong once before it was right:
  1. The pass is WIRED and runs BEFORE the sort — an unwired ranking term is dead code, the defect
     class this repository has paid for repeatedly.
  2. It runs AFTER every pass that moves a derived score. The first draft ran mid-pipeline and read
     a PRE-penalty floor: RT-PARTNER-STRAT read 195.0 while the sibling it cites, AUT-049, stands at
     105.0 in the ledger a reader holds, and five sandbox process defects would have entered ABOVE
     the live research the pass exists to surface.
  3. Replacing a score CLEARS the `score_inputs` flags that claim a penalty is already inside it.
     AUT-PROP-004 carried `blocked_with_evidence: True` beside `score: null`; without the clear, the
     penalty pass CREDITS 90 points to a score that never contained the penalty.
  4. The residue — a row whose route has no derived sibling — is REPORTED, never invented.
  5. `_table` renders a row it cannot fully describe instead of killing the whole view.

⛔ WHAT THIS FILE CANNOT SEE, said rather than left to be discovered: it does not check that any
inherited number is the RIGHT priority for the work — a score orders work and asserts nothing about
the science (`_scores_are_not_evidence`). It checks that the number is derived from a real sibling,
carries its basis in prose, and is charged the row's own penalties exactly once.
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import health as H  # noqa: E402
import priority as P  # noqa: E402


@pytest.fixture
def weights():
    return P.load_weights()


def _derived(rid, route, score):
    return {"id": rid, "_derived": True, "serves": {"route": route}, "score": score,
            "kind": "experiment", "cost_class": "free", "state": "queued", "what": rid}


def _hand(rid, route, **kw):
    e = {"id": rid, "serves": {"route": route}, "score": None, "kind": "fix",
         "cost_class": "free", "state": "queued", "what": rid}
    e.update(kw)
    return e


# ─── 1 · the pass exists, is wired, and is wired in the right place ──────────────────────────────

def test_the_pass_is_called_from_build_ledger():
    """⛔ AN UNWIRED RANKING TERM IS DEAD CODE. `subagent_width` governed nothing for a fortnight
    because no code read it; the census lane's exempt flag and the watchdog's env var were the same
    shape. `apply_age_factor`, `apply_fruitless_attempts` and `apply_requires_trimcrae` each carry
    this assertion for that reason and this pass is the fourth."""
    import inspect
    src = inspect.getsource(P.build_ledger)
    assert "apply_route_inheritance(entries, weights)" in src, (
        "apply_route_inheritance is not called from build_ledger, so no ledger anyone reads has "
        "ever been through it.")


def test_the_pass_runs_after_every_pass_that_moves_a_derived_score_and_before_the_sort():
    """⛔⛔ THE 90-POINT LESSON, BOUND SO IT CANNOT BE UNLEARNED BY A TIDY-UP. The floor this pass
    reads is a derived sibling's FINISHED score. Moved above `apply_requires_trimcrae` it reads a
    pre-penalty number instead: measured before either version was committed, RT-PARTNER-STRAT's
    floor read 195.0 against the 105.0 the ledger shows for the very row the basis string cites, and
    five hand-filed sandbox defects entered at ~195.9 — above RT-SGK1 and RT-ALK-HIT at 140.0, which
    is the §0 failure the whole item exists to cure. Moved below the sort it is dead code."""
    import inspect
    src = inspect.getsource(P.build_ledger)
    where = src.index("apply_route_inheritance(entries, weights)")
    for earlier in ("apply_age_factor(entries, weights)",
                    "apply_session_penalties(entries, weights)",
                    "apply_fruitless_attempts(entries, weights)",
                    "apply_requires_trimcrae(entries, weights)"):
        assert src.index(earlier) < where, (
            f"{earlier} runs AFTER apply_route_inheritance, so the floor it reads is not the score "
            "the ledger will show for that sibling.")
    assert where < src.index("entries.sort("), (
        "apply_route_inheritance runs after the sort, so the scores it assigns order nothing.")


# ─── 2 · what it assigns, and from what ──────────────────────────────────────────────────────────

def test_an_unscored_row_inherits_its_routes_floor(weights):
    entries = [_derived("D1", "RT-X", 100.0), _hand("H1", "RT-X")]
    P.apply_route_inheritance(entries, weights)
    assert entries[1]["score"] == 100.0
    assert "RT-X" in entries[1]["_score_basis"]
    assert entries[1]["_score_inherited_from_route"] == "RT-X"


def test_the_floor_is_the_lowest_sibling_not_the_highest(weights):
    """⚠ THE AGGREGATOR IS UNEXERCISED BY THE COMMITTED DATA and this test is the only thing that
    binds it: on the ledger the pass was written against, every route carrying a derived row carries
    EXACTLY ONE, so min, max and mean are the same number. A synthetic route is the only way to say
    which rule the code implements."""
    entries = [_derived("D1", "RT-X", 180.0), _derived("D2", "RT-X", 40.0),
               _derived("D3", "RT-X", 95.0), _hand("H1", "RT-X")]
    P.apply_route_inheritance(entries, weights)
    assert entries[-1]["score"] == 40.0, (
        "the floor must be the LOWEST derived sibling. A hand-filed row's per-step terms are "
        "unknown, so anything above the minimum is a number no sibling justifies.")


def test_a_row_whose_route_has_no_derived_sibling_keeps_no_score(weights):
    """⛔ THE RESIDUE IS REPORTED, NEVER INVENTED (CLAUDE.md §4). A fabricated number would rank the
    row AND tell every reader it had been valued, which is worse than the invisibility it cures.
    RT-AUTONOMY is the real case: it is not a route in systems/graph, so its rows can never inherit
    — which is also the measured reason this pass cannot flood the queue with process defects."""
    entries = [_derived("D1", "RT-X", 100.0), _hand("H1", "RT-AUTONOMY"), _hand("H2", None)]
    P.apply_route_inheritance(entries, weights)
    assert entries[1]["score"] is None
    assert entries[2]["score"] is None
    assert "_score_basis" not in entries[1]


def test_an_already_scored_row_is_never_re_derived(weights):
    """⛔ ASSIGNED ONCE. From the next re-score the row behaves like one whose filer typed a number,
    which is what keeps every downstream flag-guarded penalty single-applied. Re-deriving each run
    would overwrite a base those flags say has already been charged — the AUT-PD-063 ratchet."""
    entries = [_derived("D1", "RT-X", 100.0), _hand("H1", "RT-X", score=7.0)]
    P.apply_route_inheritance(entries, weights)
    assert entries[1]["score"] == 7.0
    assert "_score_inherited_from_route" not in entries[1]


def test_an_inherited_score_never_fabricates_score_inputs(weights):
    """★ THE INVARIANT `test_priority_ranks_the_hand_filed_entries_too` STATES: an entry with a full
    set of zeroed inputs LOOKS computed, and the arithmetic printed beside it would be arithmetic
    nobody did. An inherited score carries its basis in prose, exactly as a hand-scored row does."""
    entries = [_derived("D1", "RT-X", 100.0), _hand("H1", "RT-X")]
    P.apply_route_inheritance(entries, weights)
    inputs = entries[1].get("score_inputs") or {}
    for derived_only in ("live", "patient_path", "pursue_now", "tier_one", "endpoint_reachable",
                         "blocker_leverage"):
        assert derived_only not in inputs, (
            f"{derived_only} was written onto an inherited row, so its score reads as computed from "
            "the graph when nothing computed it.")


# ─── 3 · the row's own penalties, charged exactly once ───────────────────────────────────────────

def test_a_stale_penalty_flag_does_not_credit_a_fresh_base(weights):
    """⛔⛔ THE BUG THE FIRST DRAFT SHIPPED WITH, AND IT PAID 90 POINTS IN THE WRONG DIRECTION.
    AUT-PROP-004 sits on the committed ledger with `score: null` AND
    `score_inputs.blocked_with_evidence: true` — a flag from a previous life of these passes,
    asserting a penalty is inside a score that does not exist. Leave the flag and
    `apply_session_penalties` reads `evidenced != applied` the other way round and ADDS 90 to a base
    that never carried it: an escalation-only row blocked on a human would have entered the queue
    ~90 points above a live in-silico route."""
    penalty = weights["terms"]["blocked_with_evidence"]["weight"]
    entries = [_derived("D1", "RT-X", 100.0),
               _hand("H1", "RT-X",
                     blocked_evidence="publication-authority.json: outreach was never granted",
                     score_inputs={"blocked_with_evidence": True})]
    P.apply_route_inheritance(entries, weights)
    assert entries[1]["score"] == round(100.0 + penalty, 2), (
        f"an evidenced-blocked row must land at floor{penalty:+} — got {entries[1]['score']} "
        "against a floor of 100.0.")


def test_a_requires_trimcrae_row_is_charged_its_withholding(weights):
    """The penalty is applied by the pass that OWNS it, on the newly scored row — never
    re-implemented inside the inheritance pass, which is how the other three formulas stayed in one
    place each."""
    w = weights["terms"]["blocked_on_human"]["weight"]
    entries = [_derived("D1", "RT-X", 100.0), _hand("H1", "RT-X", requires_trimcrae=True)]
    P.apply_route_inheritance(entries, weights)
    assert entries[1]["score"] == round(100.0 + w, 2)
    assert entries[1]["score_inputs"]["blocked_on_human"] is True


def test_the_rows_own_age_bonus_is_a_term_its_score_contains(weights):
    """⭐ AUT-PD-063's LESSON, ON A SECOND ASSIGNMENT SITE. `apply_age_factor` echoes `age_factor`
    into `score_inputs` even on a row whose score is None while adding nothing to the score. Without
    `_own_age_bonus` the row would advertise a term its score does not contain — the one thing
    `_scores_are_not_evidence` promises never happens."""
    w = weights["terms"]["age"]["weight"]
    entries = [_derived("D1", "RT-X", 100.0),
               _hand("H1", "RT-X", score_inputs={"age_factor": 0.5})]
    P.apply_route_inheritance(entries, weights)
    assert entries[1]["score"] == round(100.0 + w * 0.5, 2)
    assert entries[1]["score_inputs"]["age_factor"] == 0.5


def test_the_pipeline_is_still_a_fixed_point():
    """Two builds of the real ledger must agree. A pass that assigns rather than accumulates is the
    only kind that can be run twice, and `apply_age_factor`'s ratchet (AUT-PROP-036) is what happens
    when one is not."""
    import json
    first = json.dumps(P.build_ledger(), sort_keys=True)
    second = json.dumps(P.build_ledger(), sort_keys=True)
    assert first == second, "re-scoring twice moved the ledger, so a score depends on the run count."


# ─── 4 · the renderer, and the reader that reports the residue ───────────────────────────────────

def test_the_table_renders_a_row_it_cannot_fully_describe(capsys):
    """⛔⛔ THE ONE-OF-A-PAIR DEFECT, MEASURED. AUT-PD-046 made `what` defensive and left `score`,
    `kind`, `cost_class` and `serves.route` indexed, on rows that same commit knew could lack them.
    `--limit 300` died with `TypeError: unsupported format string passed to NoneType.__format__` on
    the first unscored row, so the ranker's own view could not render a third of its ledger — and
    the existing regression test calls `main([])`, whose default limit of 20 never reached one."""
    assert P.main(["--limit", "300"]) == 0
    out = capsys.readouterr().out
    assert out.count("\n") > 100, "the full-depth table printed almost nothing"


# ─── 3b · an explicit `"score_inputs": null` must never crash the ranker ─────────────────────────

def _null_inputs_row(**kw):
    row = {"id": "NULLINPUTS", "serves": {"route": "RT-X"}, "score": 100.0, "kind": "fix",
           "cost_class": "free", "state": "queued", "what": "row", "score_inputs": None,
           "last_evidence_utc": "2020-01-01"}
    row.update(kw)
    return row


@pytest.mark.parametrize("pass_name, extra", [
    ("apply_age_factor", {}),
    ("apply_session_penalties", {"blocked_evidence": "an observation that blocked it"}),
    # ⚠ THE FINGERPRINT MUST MATCH THE ROW'S CURRENT ONE OR THE COUNT IS 0 AND THE SITE NEVER WRITES.
    # `fruitless_attempts_count` walks `dispatch_log` backwards and stops at the first entry whose
    # `fingerprint_at_dispatch` differs, so a placeholder value silently makes this case vacuous —
    # which is how the first draft of this test passed while the mutation survived. The value is
    # `evidence_fingerprint(row)` for the fixture below: last_evidence_utc, a pipe, and blocked_by.
    ("apply_fruitless_attempts",
     {"dispatch_log": [{"utc": "2020-01-01T00:00:00Z",
                        "fingerprint_at_dispatch": "2020-01-01|None"}]}),
    ("apply_requires_trimcrae", {"requires_trimcrae": True}),
])
def test_a_null_score_inputs_is_writable_at_every_site(weights, pass_name, extra):
    """⛔⛔ THE OUTAGE `setdefault` CAUSED, AND IT IS THE ONE-OF-A-PAIR CLASS ACROSS FOUR SITES.
    `e.setdefault("score_inputs", {})` returns the EXISTING value when the key is present, so a row
    carrying `"score_inputs": null` — AUT-COV-001, filed by CYC-0011 and on the trunk ever since —
    hands back None and `None["age_factor"] = f` raises TypeError. That kills `priority.py --write`,
    step 3 of the cycle contract, for EVERY session: the same total outage as the duplicate-id crash.
    ⚠ IT WAS LATENT BECAUSE EACH SITE ONLY WRITES A NON-ZERO TERM. Measured: that row's age factor is
    EXACTLY 0.0 as of 2026-08-28 and 0.0714 as of 2026-08-29, so it was skipped every run until a
    calendar boundary rolled it over mid-cycle. This test does not wait for a calendar.

    ⛔⛔ EACH PASS IS DRIVEN IN ISOLATION, AND THAT IS NOT A STYLE CHOICE — THE FIRST VERSION RAN ALL
    FOUR IN SEQUENCE AND MUTATION TESTING CAUGHT IT. Reverting the `apply_fruitless_attempts` and
    `apply_requires_trimcrae` sites to `setdefault` left the suite GREEN (4/6 caught), because
    `apply_age_factor` runs first and had already replaced the null with a dict, so the two later
    sites never met the value that breaks them. A shared fixture that repairs the defect before the
    code under test sees it is a test of the fixture. Parametrised, all six mutations are caught."""
    row = _null_inputs_row(**extra)
    # ⛔ VACUITY GUARD. Every case must actually reach its site's write; a fixture that makes the
    # term zero tests nothing and looks identical to a pass. The fruitless case is the one that was
    # vacuous, so its precondition is asserted rather than assumed.
    if pass_name == "apply_fruitless_attempts":
        assert P.fruitless_attempts_count(row) > 0, (
            "the fixture's dispatch fingerprint no longer matches evidence_fingerprint(row), so this "
            "case is vacuous — re-derive it rather than deleting the case.")
    getattr(P, pass_name)([row], weights)
    assert isinstance(row["score_inputs"], dict), (
        f"{pass_name} left score_inputs as {row['score_inputs']!r}, so it still indexes None and "
        "priority.py --write dies on the committed ledger.")


def test_a_null_score_inputs_is_treated_as_absent_and_never_filled_in(weights):
    """⭐ NULL IS THE SAME STATE AS ABSENT — nothing has been echoed yet — and the fix must not use
    the repair as an excuse to invent content. A row whose `score_inputs` was null must end up with
    exactly the terms the passes actually applied, and no derived-scorer inputs it never had."""
    null_row = _null_inputs_row(id="N")
    absent_row = dict(null_row, id="A")
    absent_row.pop("score_inputs")
    P.apply_age_factor([null_row, absent_row], weights)
    assert null_row["score_inputs"] == absent_row["score_inputs"], (
        "a null score_inputs and an absent one produced different results; they are the same state.")
    for derived_only in ("live", "patient_path", "pursue_now", "tier_one", "blocker_leverage"):
        assert derived_only not in null_row["score_inputs"]


def test_the_committed_ledger_still_re_scores(capsys):
    """⛔ THE REGRESSION AT FULL SCALE, ON THE ROW THAT ACTUALLY CARRIES THE DEFECT. A synthetic
    fixture would have passed on the broken code the day before the date rolled over; the committed
    ledger is what step 3 of every cycle actually reads."""
    assert P.main([]) == 0


def test_scores_are_reachable_is_a_declared_condition_that_never_stops_the_loop():
    """⛔ `advises`, and the alternative is the death spiral `CONDITION_ON_RED` itself warns about:
    most of the residue serves RT-AUTONOMY, which is not a route in systems/graph, so no cycle can
    clear it. `redirects` would hand every cycle the same unfixable errand instead of the research;
    `blocks` would stop the loop on a permanently red row, which is exactly how it died once."""
    assert "scores_are_reachable" in H.CONDITION_ORDER
    assert H.CONDITION_ON_RED["scores_are_reachable"] == "advises"
    assert H.CONDITION_AXIS["scores_are_reachable"] in H.AXES
    assert H.CONDITION_ON_RED["scores_are_reachable"] not in H.RETRIED_ON_RED, (
        "an advises row must spend no restart-intensity budget — nothing retries it.")


def test_scores_are_reachable_counts_open_rows_only_and_names_the_remedy():
    """A closed row nobody will ever take is not invisible work, and a red that names no remedy is an
    unanswered question wearing the costume of a status (CLAUDE.md §4)."""
    entries = [{"id": "A", "state": "done", "score": None, "serves": {"route": "RT-X"}},
               {"id": "B", "state": "queued", "score": None, "serves": {"route": "RT-X"}},
               {"id": "C", "state": "queued", "score": 5.0, "serves": {"route": "RT-X"}}]
    row = H.c_scores_are_reachable(entries, None)
    assert row["ok"] is False and row["payload"]["unrankable"] == 1
    assert row["payload"]["open"] == 2
    assert "systems/graph" in row["detail"]
    assert H.c_scores_are_reachable([e for e in entries if e["id"] != "B"], None)["ok"] is True


def test_the_closed_set_the_condition_skips_is_the_one_the_scorer_skips():
    """⛔ ONE HOME FOR THE CLOSED SET, CHECKED BY VALUE. This repository already carries four
    definitions of it (`stuck_clock`, `admissibility`, `priority`, and two modules aliasing the
    first), and AUT-PD-050 had just finished naming that in `priority.py` when this condition was
    written. The condition points at `stuck_clock.CLOSED_STATES`; this asserts the value it points at
    still equals the one the scorer itself skips, which a substring search of the source could not."""
    import stuck_clock
    assert set(stuck_clock.CLOSED_STATES) == set(P.CLOSED_STATES), (
        "health.c_scores_are_reachable and priority.apply_age_factor disagree about which states are "
        "closed, so one of them is counting or ageing a row the other has written off.")


def test_scores_are_reachable_is_unmeasured_when_the_ledger_is_unreadable():
    """⛔ An absent reading is not a reading of absence. An unreadable ledger must not print
    ALL-RANKABLE — that is the module docstring's own named failure."""
    row = H.c_scores_are_reachable(None, "research-ledger.json carries no `entries`")
    assert row["unmeasured"] is True and row["ok"] is False
