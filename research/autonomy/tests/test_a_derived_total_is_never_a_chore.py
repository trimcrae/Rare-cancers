#!/usr/bin/env python3
"""The ledger's header totals are derived at write time, not asked for afterwards.

⛔⛔ WHY THIS EXISTS, MEASURED RATHER THAN REASONED. Across the eight committed PREFLIGHT_FULL logs
on 2026-09-02, LEDGER BOOKKEEPING is what failed the PUBLICATION gate in three of them — the header
totals and the score arithmetic beside them — and twice on that day alone, each costing a full
re-run of a gate that has taken between 11:46 and 51:28. The modalities suite, 72 % of every one of
those runs, failed in NONE of them. So the most expensive part of the publication gate has never
caught anything, and the part that most often blocks publishing a paper is the loop's own arithmetic
about itself.

★ THE FIX IS AT THE SOURCE, NOT AT THE GATE, AND THE DISTINCTION IS THE WHOLE POINT. Removing the
check would be the self-serving edit: it has fired three times, so it is doing its job. What was
wrong is that `header_problems` computed the right answer and then asked a HUMAN to go run
`priority.py --write`. CLAUDE.md §1 says a total is DERIVED, never typed — so it is derived, at the
one place every programmatic write already passes through.

⚠ WHAT IS DELIBERATELY NOT WEAKENED: `header_problems` still runs, still fails, and still guards the
hand-authored rows that never come through `write_ledger` at all. This narrows that guard's INPUT.
Narrowing a guard's input is not weakening the guard, and these tests hold both halves.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
LEDGER = os.path.join(AUTONOMY, "research-ledger.json")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(AUTONOMY, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _load("ledger_schema")


@pytest.fixture(scope="module")
def committed():
    with open(LEDGER, encoding="utf-8") as fh:
        return json.load(fh)


def test_a_clean_ledger_is_not_touched(committed):
    """⛔ A REPAIR THAT FIRES ON A CORRECT FILE IS A DIFF NOBODY CAN REVIEW. It must report exactly
    the totals that were wrong, and on a correct ledger that is none of them."""
    doc = copy.deepcopy(committed)
    assert S.derive_headers(doc) == []
    assert doc == committed, "a clean ledger was modified by the deriver"


def test_a_stale_total_is_re_derived_and_the_correction_is_reported(committed):
    """Both halves: the value is fixed, AND the caller is told which ones were wrong. A silent
    repair is the shape this repository refuses everywhere else — it makes a stale file and a
    correct one indistinguishable in the log."""
    doc = copy.deepcopy(committed)
    doc["n_clamped"] = 999
    doc["n_by_state"] = {"queued": 1}
    corrected = sorted(S.derive_headers(doc))
    assert corrected == ["n_by_state", "n_clamped"], corrected
    assert S.header_problems(doc) == []
    assert doc["n_clamped"] == committed["n_clamped"]
    assert doc["n_by_state"] == committed["n_by_state"]


def test_the_deriver_counts_the_rows_rather_than_copying_the_old_header(committed):
    """⛔⛔ THE ONE THAT WOULD MAKE THIS WORSE THAN USELESS. If it restored the PREVIOUS header
    instead of counting the rows, every append would keep the stale total AND silence the guard that
    would have caught it — a repair that manufactures the exact failure it claims to prevent."""
    doc = copy.deepcopy(committed)
    before_state = dict(doc["n_by_state"])
    doc["entries"] = doc["entries"] + [dict(doc["entries"][0], id="ZZZ-PROBE-0001",
                                            state="queued", kind="fix")]
    S.derive_headers(doc)
    assert doc["n_by_state"]["queued"] == before_state.get("queued", 0) + 1, (
        "adding a queued row did not move the queued count — the deriver is not counting rows")
    assert doc["n_by_kind"]["fix"] == committed["n_by_kind"].get("fix", 0) + 1
    assert S.header_problems(doc) == []


def test_the_guard_still_fails_a_hand_edited_ledger(committed):
    """⚠ THE HALF THAT MUST NOT HAVE BEEN WEAKENED. Most rows are hand-authored JSON that never
    passes through `write_ledger`, so `header_problems` is still the only thing standing between a
    hand edit and a committed file whose summary describes a different ledger."""
    doc = copy.deepcopy(committed)
    doc["n_unscored"] = doc["n_unscored"] + 7
    found = S.header_problems(doc)
    assert found and any("n_unscored" in f for f in found), (
        "a hand-edited total no longer fails header_problems — the deriver was allowed to replace "
        "the guard rather than narrow its input")


def test_write_ledger_derives_before_it_checks():
    """The wiring, pinned: `ledger_io.write_ledger` must call the deriver on the path that also
    calls the checks, or a programmatic append still lands stale and the whole measurement above
    stands unaddressed."""
    src = open(os.path.join(AUTONOMY, "ledger_io.py"), encoding="utf-8").read()
    assert "derive_headers" in src, "write_ledger no longer derives the header totals"
    body = src[src.index("def write_ledger"):]
    # ⛔ MATCH THE CALL SITES, NOT THE PROSE. `check_write` is named several times in this
    # function's docstring before it is ever called, so a naive `.index()` compares a derivation
    # against a paragraph and passes whatever the code does — the first version of this test did
    # exactly that and reported the wrong order on correct code.
    derive_at = body.index("ledger_schema.derive_headers(")
    check_at = min(body.index("admissibility.check_write(os.fspath"),
                   body.index("ledger_schema.check_write(os.fspath"))
    assert derive_at < check_at, (
        "the totals are derived AFTER the checks run, so a stale header still fails the write it "
        "was supposed to have been repaired by")
