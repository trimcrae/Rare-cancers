"""Guards on how `priority.py` resolves a `prerequisite_of` CHAIN — AUT-PD-063.

⛔⛔ WHY THIS FILE EXISTS. `apply_session_penalties` used to run two linear passes over `entries` in
list order — the evidenced-block penalty, then the prerequisite inheritance — and both passes were
wrong in a way no synthetic two-row fixture could show. The two halves were found and fixed by two
different items on the same day, which is exactly why they are pinned here together:

  (a) THE INHERITANCE ASSIGNED, SO IT ERASED THE PENALTY — AUT-PD-063, fixed by the commit that adds
      this file. A row that is BOTH blocked-with-evidence AND a prerequisite of something had its
      -90 overwritten by the inherited value. On the committed ledger of 2026-08-28 that put
      AUT-PROP-018, -019, -020, -040 and -042 — five rows carrying their own recorded block — at
      ranks 6, 7, 9, 11 and 12 of a queue the penalty exists to remove them from.
      `test_an_evidenced_block_drops_out_of_the_queue` checks only the top THREE, so it watched this
      happen and stayed green.
  (b) A CHILD COULD READ ITS PARENT BEFORE THE PARENT WAS FINISHED — AUT-PROP-036, already fixed at
      a660303d1 by resolving the chain parents-first, together with making both score terms
      idempotent across re-scores. With no ordering, correctness depended on file position:
      AUT-PROP-021 sat at index 79 and its parent AUT-PROP-018 at 81, so the child inherited a value
      the parent was re-derived away from two iterations later. Pinned here because a parents-first
      resolution that nothing asserts is one refactor away from being a linear pass again.

⚠ (b)'s FIX ALONE DOES NOT CLOSE THE RED GUARD, MEASURED: at a660303d1,
`test_a_prerequisite_inherits_the_parents_value_not_its_penalty` still failed —
`assert 196.0 > (195.5 - (-90.0 / 2))`, the AUT-PROP-022 -> AUT-PROP-020 pair — because the erased
penalty is a different defect from the order it was erased in.

⚠ THE TESTS BELOW ARE SYNTHETIC ON PURPOSE, AND THAT IS THE POINT — the real-ledger guard
(`systems/tests/test_autonomy_priority.py::test_a_prerequisite_inherits_the_parents_value_not_its_penalty`)
fires only while some real parent happens to be blocked, so it is a guard whose coverage the LEDGER
decides. These bind the property directly, in both list orders, and cannot be turned off by a row
being edited.
"""

from __future__ import annotations

import importlib.util
import inspect
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[3]
PRIORITY_PY = REPO / "research" / "autonomy" / "priority.py"


def _import():
    spec = importlib.util.spec_from_file_location("autonomy_priority_chain", PRIORITY_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P = _import()
W = P.load_weights()
PENALTY = W["terms"]["blocked_with_evidence"]["weight"]
BONUS = W["prerequisite_bonus"]["value"]
AGE_W = W["terms"]["age"]["weight"]


def _chain(parent_blocked: bool):
    """root <- mid <- leaf, where `mid` is itself blocked when asked to be."""
    root = {"id": "R", "score": 100.0, "serves": {"route": "RT-X"}, "kind": "write",
            "state": "queued"}
    mid = {"id": "M", "score": 5.0, "prerequisite_of": "R", "serves": {"route": "RT-X"},
           "kind": "harden", "state": "queued",
           "blocked_evidence": "measured: the runner refused" if parent_blocked else None}
    leaf = {"id": "L", "score": 1.0, "prerequisite_of": "M", "serves": {"route": "RT-X"},
            "kind": "build", "state": "queued"}
    return root, mid, leaf


@pytest.mark.parametrize("order", [("R", "M", "L"), ("L", "M", "R"), ("M", "L", "R")])
def test_the_answer_does_not_depend_on_where_the_rows_sit_in_the_file(order):
    """⛔ THE ORDER BUG, DIRECTLY. A ledger is a list, and a session appends to it; which of a
    parent and its prerequisite lands first is an accident of who filed what when."""
    rows = {r["id"]: r for r in _chain(parent_blocked=False)}
    out = {e["id"]: e for e in P.apply_session_penalties([rows[i] for i in order], W)}
    assert out["M"]["score"] == round(100.0 + BONUS, 2)
    assert out["L"]["score"] == round(100.0 + 2 * BONUS, 2), (
        "the leaf did not inherit through the middle row — a two-hop chain resolved in one linear "
        "pass gives whichever answer the file order happens to produce"
    )


def test_a_blocked_prerequisite_still_answers_for_its_own_block():
    """⭐ THE PENALTY MUST SURVIVE THE INHERITANCE. Inheriting is what the row is WORTH; the block is
    what the row can be DONE about this cycle. Assigning one over the other loses the second."""
    out = {e["id"]: e for e in P.apply_session_penalties(list(_chain(parent_blocked=True)), W)}
    unblocked_value = round(100.0 + BONUS, 2)
    assert out["M"]["score"] == round(unblocked_value + PENALTY, 2), (
        "a row that is both a prerequisite and blocked-with-evidence came out of the pass without "
        "its penalty — the inheritance overwrote it"
    )
    assert out["L"]["score"] == round(unblocked_value + BONUS, 2), (
        "the leaf inherited its parent's PENALISED score; a prerequisite is worth what its parent "
        "is worth once unblocked"
    )
    assert out["L"]["score"] > out["M"]["score"], "the fix sorted below the thing it fixes"
    assert out["M"]["score"] > out["R"]["score"] + PENALTY - 1, "the chain lost its ordering"


def test_the_parents_wait_reaches_the_row_that_would_clear_it():
    """⛔ OTHERWISE THE ANTI-STARVATION TERM IS DEAD FOR EXACTLY THE ROWS IT IS FOR. You cannot take
    a blocked row, so raising its score buys nothing unless the prerequisite rises with it. Measured
    on the committed ledger: AUT-049 aged to +12.0 and AUT-PROP-018 — the only path to it — saw none
    of it, which left the prerequisite BELOW its parent once the parent's penalty stopped being
    erased. That is the pair of previously-passing tests a naive reorder broke."""
    import datetime as _dt
    today = _dt.date(2026, 8, 28)
    root, mid, leaf = _chain(parent_blocked=False)
    root["last_evidence_utc"] = "2026-01-01"          # long-waited: saturates the age factor
    mid["last_evidence_utc"] = "2026-08-28"           # no wait at all
    leaf["state"] = "done"                            # a closed row never ages on its own
    rows = [root, mid, leaf]
    P.apply_age_factor(rows, W, today=today)
    out = {e["id"]: e for e in P.apply_session_penalties(rows, W)}
    assert out["R"]["score"] == round(100.0 + AGE_W, 2)
    assert out["M"]["score"] == round(100.0 + AGE_W + BONUS, 2), (
        "the prerequisite did not inherit its parent's wait bonus"
    )
    assert out["L"]["score"] == round(100.0 + AGE_W + 2 * BONUS, 2)


def test_the_row_keeps_its_own_wait_across_the_inheritance():
    """⚠ THE ASSIGNMENT MUST NOT SILENTLY DISCARD WHAT `apply_age_factor` ALREADY ADDED, or
    `score_inputs["age_factor"]` advertises a term the printed score does not contain."""
    import datetime as _dt
    today = _dt.date(2026, 8, 28)
    root, mid, leaf = _chain(parent_blocked=False)
    root["last_evidence_utc"] = "2026-08-28"
    mid["last_evidence_utc"] = "2026-01-01"           # the CHILD is the starved one here
    rows = [root, mid, leaf]
    P.apply_age_factor(rows, W, today=today)
    out = {e["id"]: e for e in P.apply_session_penalties(rows, W)}
    assert out["M"]["score_inputs"]["age_factor"] == 1.0
    assert out["M"]["score"] == round(100.0 + BONUS + AGE_W, 2), (
        "the prerequisite's own age bonus was overwritten by the inherited value while its "
        "score_inputs went on claiming it"
    )


def test_the_block_flag_comes_back_off_when_the_evidence_goes():
    """⛔ MEASURED ON THE COMMITTED LEDGER: AUT-PROP-039 carried `blocked_evidence: null` and
    `score_inputs.blocked_with_evidence: true`, because `setdefault` wrote the key and nothing ever
    cleared it. The inheritance rule READ that flag to undo a penalty, so a stale true minted 90
    points from nothing — simulated 2026-08-28 on a copy of the committed ledger, clearing
    AUT-PROP-018's `blocked_evidence` alone took AUT-PROP-021 from 196.9 to 286.9, first in the
    queue by 87 points, on a row whose block had merely been resolved. AUT-PROP-036 fixed the
    write side; this pins it, because the flag is now load-bearing in BOTH directions."""
    row = {"id": "S", "score": 50.0, "serves": {"route": "RT-X"}, "kind": "fix",
           "blocked_evidence": None, "score_inputs": {"blocked_with_evidence": True}}
    out = P.apply_session_penalties([row], W)[0]
    assert "blocked_with_evidence" not in out["score_inputs"], (
        "a resolved row still advertises a penalty its score does not carry"
    )
    # ⭐ AND THE POINTS COME BACK WITH IT. The flag is the record that the carried score already
    # contains one application of the penalty, so clearing the evidence must REFUND it — otherwise
    # a row stays buried by a block that has been resolved, which is the mirror image of the defect
    # rule 1 exists for. (AUT-PROP-036's idempotence work is what makes the flag mean this.)
    assert out["score"] == round(50.0 - PENALTY, 2)


def test_a_cycle_in_the_chain_terminates_instead_of_killing_the_ranker():
    """⚠ THE RANKER DYING IS WORSE THAN THE DATA DEFECT — the loop then picks work by hand and
    nothing says so. A `prerequisite_of` cycle must not recurse forever and must not raise.

    ⛔ WHAT THIS DOES *NOT* ASSERT, AND WHY. It does not pin the scores a cycle produces. Two
    resolutions are defensible — refuse to inherit at all, or resolve each member once and stop —
    and `apply_session_penalties` takes the second (AUT-PROP-036's `resolving` set). Pinning the
    first here would be this guard legislating a design choice it was not written to decide. What
    the loop actually cannot survive is non-termination, so that is what is bound: every row comes
    back exactly once, with a finite score.
    """
    a = {"id": "A", "score": 10.0, "prerequisite_of": "B", "serves": {"route": "RT-X"}, "kind": "fix"}
    b = {"id": "B", "score": 20.0, "prerequisite_of": "A", "serves": {"route": "RT-X"}, "kind": "fix"}
    self_ref = {"id": "C", "score": 30.0, "prerequisite_of": "C", "serves": {"route": "RT-X"},
                "kind": "fix"}
    out = {e["id"]: e for e in P.apply_session_penalties([a, b, self_ref], W)}
    assert set(out) == {"A", "B", "C"}, "a row was dropped resolving a prerequisite cycle"
    for rid in ("A", "B", "C"):
        assert isinstance(out[rid]["score"], float) and abs(out[rid]["score"]) < 1e6, (
            f"{rid} came out of a prerequisite cycle with a runaway score"
        )


def test_the_scorer_ages_before_it_resolves_the_chain():
    """⛔⛔ THE CALL-SITE GUARD, BECAUSE THE PROPERTY LIVES IN `build_ledger` AND NOWHERE ELSE. The
    inheritance ASSIGNS, so anything added to a parent afterwards never reaches its child. This
    repository has shipped a governed constant no code read, an exempt flag nothing consulted and a
    watchdog wired to a missing env var; an ordering nothing asserts is the same defect."""
    src = inspect.getsource(P.build_ledger)
    # ⚠ THE CALL SITES, NOT THE BARE NAMES — the surrounding comment names both functions, so a
    # bare `index()` measures the prose rather than the code. The same trap sits in
    # `test_nothing_waits_forever.py::test_the_scorer_actually_calls_it`, which is still correct
    # only because nothing above its call happens to mention the name.
    assert src.index("entries = apply_age_factor(") < src.index("entries = apply_session_penalties("), (
        "the age factor is applied AFTER the prerequisite chain is resolved, so a starved parent's "
        "bonus never reaches the only row that could clear it"
    )
