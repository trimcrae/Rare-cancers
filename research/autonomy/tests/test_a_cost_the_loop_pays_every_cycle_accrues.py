#!/usr/bin/env python3
"""A defect that taxes every cycle must climb the queue, and it must climb from a MEASUREMENT.

⛔⛔ THE EVENT THIS EXISTS FOR, AND IT IS NOT A HYPOTHETICAL. Between 2026-08-29 and 2026-09-01 six
cycles independently measured that the commit gate had grown 11x and filed six rows — AUT-PD-155,
-162, -164, -172, -174, -183. On 2026-09-02 every one of them was still `queued` with `attempts: 0`,
and trimcrae asked for the fix by hand. The loop's noticing worked six times; its acting worked
never.

★ AND THE CAUSE IS ON THE RECORD IN THE ROWS THEMSELVES, WHICH IS WHY A WEIGHT ALONE WOULD NOT HAVE
FIXED IT. AUT-PD-164's own `_score_basis`: *"It costs every cycle real wall-clock on every commit,
which is the complaint trimcrae has already made twice about this loop, but it breaks nothing — so
it ranks"* below. AUT-PD-183's: *"it silently taxes every commit in the loop, but nothing it
breaks"*. Each filer SAW the cost and judged ONE INSTANCE of it against things that break. Each was
right about the instance — 6.6 minutes is small. **Nobody multiplied.** The product was 2.7 hours.

⭐ SO THE PROPERTY UNDER TEST IS THAT THE MULTIPLICATION IS THE SCORER'S JOB AND NEVER THE FILER'S.
The row supplies minutes and a start date, both checkable; the debt and the score are derived. The
tests below are grouped by the three ways this could fail back into what it replaced: the term does
not actually move the queue, the term can be typed instead of measured, or the term moves a score
the ledger's own admissibility layer then refuses.
"""

from __future__ import annotations

import copy
import datetime
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
sys.path.insert(0, AUTONOMY)

import admissibility as A  # noqa: E402
import priority  # noqa: E402

TODAY = datetime.date(2026, 9, 2)


@pytest.fixture
def weights():
    return priority.load_weights()


def _row(**kw):
    base = {
        "id": "AUT-X", "state": "queued", "score": 116.0, "score_inputs": {},
        "what": "the gate is slow", "kind": "process",
    }
    base.update(kw)
    return base


#: The real measurement, from the row this term was built for: the commit gate cost 6.6 minutes
#: more per default run than it needed to, from 2026-08-29 (AUT-PD-155's filing) to 2026-09-02.
GATE = {"minutes_per_cycle": 6.6, "since_utc": "2026-08-29",
        "measured_by": "research/autonomy/sprint-2026-09-01/S6b-COMMITLOOP-FIXED.md"}


# --------------------------------------------------------------------------------------------
# 1 · it actually moves the queue, by the amount the debt justifies
# --------------------------------------------------------------------------------------------


def test_the_gate_row_would_have_outranked_the_paper_work_it_lost_to(weights):
    """⛔ THE ONE ASSERTION THAT MATTERS. Scored 116.0, it lost to paper rows at 198–201 for four
    days. With its measured debt accrued it must WIN, or this whole term is decoration."""
    row = _row(recurring_cost=GATE)
    priority.apply_recurring_cost([row], weights, today=TODAY)
    assert row["score"] > 201.0, (
        "AUT-PD-164 scored 116.0 and the paper rows it waited behind scored up to 201.11. After "
        "four days of a measured 6.6 min/cycle it reaches %.1f — if that is not above 201 the term "
        "changes nothing and the next six filings go the same way." % row["score"])


def test_one_day_of_a_small_tax_does_not_take_the_queue(weights):
    """⚠ THE OTHER DIRECTION, AND IT IS THE ONE AN UNBOUNDED TERM GETS WRONG. A cost seen once is
    not yet evidence of a standing tax; the paper work should still win on day one."""
    row = _row(recurring_cost=dict(GATE, since_utc="2026-09-01"))
    priority.apply_recurring_cost([row], weights, today=TODAY)
    assert row["score"] < 198.0, (
        "one day of a 6.6 min/cycle tax reached %.1f and displaced the paper work. The term is "
        "meant to win on a debt, not on a single reading." % row["score"])


def test_the_debt_saturates_so_a_trivial_nag_can_never_take_the_queue_forever(weights):
    """⛔ `age_saturates_days`' argument, applied here: an unbounded term does not fix a starving
    queue, it inverts it — into 'whatever nags most often', which given enough days would put a
    20-second annoyance above a live patient-facing route."""
    tiny = _row(recurring_cost={"minutes_per_cycle": 0.3, "since_utc": "2020-01-01"})
    big = _row(recurring_cost={"minutes_per_cycle": 55.0, "since_utc": "2020-01-01"})
    priority.apply_recurring_cost([tiny, big], weights, today=TODAY)
    assert tiny["score"] == big["score"], (
        "past saturation two very different taxes must score the same; an unsaturated term makes "
        "'how long has this nagged' beat 'how much does it cost'")
    f, _ = priority.recurring_cost_factor(tiny, weights, today=TODAY)
    assert f == 1.0


def test_a_row_with_no_block_is_untouched(weights):
    row = _row()
    priority.apply_recurring_cost([row], weights, today=TODAY)
    assert row["score"] == 116.0 and row["score_inputs"] == {}


def test_a_closed_row_stops_accruing(weights):
    """A fixed defect costs nothing more. Ageing it would raise the score of finished work."""
    row = _row(state="done", recurring_cost=GATE)
    priority.apply_recurring_cost([row], weights, today=TODAY)
    assert row["score"] == 116.0


# --------------------------------------------------------------------------------------------
# 2 · it cannot be typed — every input is checkable, and unreadable buys nothing
# --------------------------------------------------------------------------------------------


@pytest.mark.parametrize("block", [
    {"minutes_per_cycle": "6.6", "since_utc": "2026-08-29"},      # a string magnitude
    {"minutes_per_cycle": True, "since_utc": "2026-08-29"},        # a bool is not a number
    {"minutes_per_cycle": -6.6, "since_utc": "2026-08-29"},        # a negative debt
    {"minutes_per_cycle": 0, "since_utc": "2026-08-29"},
    {"minutes_per_cycle": 6.6},                                    # no start date
    {"minutes_per_cycle": 6.6, "since_utc": "the day it broke"},   # not a date
    {"minutes_per_cycle": 6.6, "since_utc": "2027-01-01"},         # a date in the FUTURE
    {"since_utc": "2026-08-29"},
    "a sentence about how slow the gate is",
    None,
])
def test_an_unreadable_claim_buys_nothing(weights, block):
    """⚠ THE DIRECTION EVERY CAP IN THIS LOOP FAILS. A filer who wants 90 points must supply
    something that can be checked; anything else is 0.0, never a guess and never a subtraction."""
    row = _row(recurring_cost=block)
    priority.apply_recurring_cost([row], weights, today=TODAY)
    assert row["score"] == 116.0, "an unreadable claim moved the score by %.1f" % (row["score"] - 116.0)


def test_an_absurd_magnitude_is_clamped_and_says_so(weights):
    """⛔ A TYPO MUST NOT TAKE THE QUEUE, AND A SILENT CLAMP IS A NUMBER THAT DISAGREES WITH ITS OWN
    BASIS. `minutes_per_cycle` is the one filer-supplied magnitude in the scorer."""
    cap = weights["recurring_cost_minutes_cap"]["value"]
    row = _row(recurring_cost={"minutes_per_cycle": cap * 1000, "since_utc": "2026-09-01"})
    priority.apply_recurring_cost([row], weights, today=TODAY)
    assert row["score_inputs"]["recurring_cost_clamped_from"] == cap * 1000, (
        "the clamp must be reported beside the score, not applied quietly")
    capped = _row(recurring_cost={"minutes_per_cycle": cap, "since_utc": "2026-09-01"})
    priority.apply_recurring_cost([capped], weights, today=TODAY)
    assert row["score"] == capped["score"]


def test_the_cadence_is_pinned_not_read_from_the_governor(weights):
    """⛔ A DEBT MUST NOT SHRINK BECAUSE THE LOOP SLOWED DOWN. `autonomy-state.json`'s
    `cycle_interval_hours` went 4 → 24 under a budget hold on 2026-08-29 and reddened a sibling test
    that read it live. A term that understates a cost exactly when the loop can least afford it is
    the wrong way round."""
    src = open(os.path.join(AUTONOMY, "priority.py"), encoding="utf-8").read()
    body = src.split("def recurring_cost_factor", 1)[1].split("\ndef ", 1)[0]
    assert "autonomy-state" not in body and "cycle_interval_hours" not in body
    assert "recurring_cost_cycles_per_day" in body


# --------------------------------------------------------------------------------------------
# 3 · the ledger still accepts the write — the AUT-PD-041 / AUT-PD-127 failure, twice measured
# --------------------------------------------------------------------------------------------


def test_a_move_this_term_accounts_for_is_admitted(weights):
    """⛔⛔ WIRING A TERM WITHOUT TEACHING `_explained_delta` MAKES THE FIRST ROW IT MOVES
    `refused_accumulated`, AND THEN NO LEDGER WRITE SUCCEEDS AT ALL. That has happened twice in this
    repository — `apply_fruitless_attempts` (AUT-PD-041) and `apply_requires_trimcrae` (AUT-PD-127).
    This term moves rows by up to 90 points, so it would have deadlocked the loop the way AUT-PD-152
    did: a cycle that can neither re-score nor claim, each failure blocking the other's fix."""
    before = _row(recurring_cost=GATE)
    after = copy.deepcopy(before)
    priority.apply_recurring_cost([after], weights, today=TODAY)
    assert after["score"] != before["score"], "the fixture must actually move, or this asserts nothing"
    assert A.write_verdict(before, after, weights)[0] != A.REFUSED_ACCUMULATED


def test_a_typed_factor_over_no_block_is_refused(weights):
    """⛔ THE ABUSE THE RECOMPUTATION EXISTS FOR: 90 points from a hand-written number."""
    row = _row(score=206.0, score_inputs={"recurring_cost_factor": 1.0,
                                          "recurring_cost_as_of": TODAY.isoformat()})
    got, why = A.verdict(row, weights, today=TODAY)
    assert got == A.REFUSED_STALE_INPUT, (got, why)


def test_a_factor_with_no_basis_date_is_refused(weights):
    """A term worth 90 points may not be unfalsifiable."""
    row = _row(recurring_cost=GATE, score_inputs={"recurring_cost_factor": 1.0})
    got, why = A.verdict(row, weights, today=TODAY)
    assert got == A.REFUSED_STALE_INPUT and "no `recurring_cost_as_of`" in why


def test_an_edited_block_is_caught_against_its_own_basis(weights):
    """The block was changed after scoring: the echo no longer reproduces from it."""
    row = _row(recurring_cost=GATE)
    priority.apply_recurring_cost([row], weights, today=TODAY)
    assert A.verdict(row, weights, today=TODAY)[0] != A.REFUSED_STALE_INPUT
    row["recurring_cost"] = dict(GATE, minutes_per_cycle=0.5)
    got, why = A.verdict(row, weights, today=TODAY)
    assert got == A.REFUSED_STALE_INPUT and "recomputing it" in why


def test_a_closed_rows_frozen_echo_is_not_graded_stale(weights):
    """`_stale_age`'s scope, mirrored: a finished row's echo is frozen by design."""
    row = _row(state="done", recurring_cost=GATE, score=206.0,
               score_inputs={"recurring_cost_factor": 1.0, "recurring_cost_as_of": "2026-08-01"})
    assert A.verdict(row, weights, today=TODAY)[0] != A.REFUSED_STALE_INPUT


def test_re_scoring_is_idempotent(weights):
    """⛔ AUT-PROP-036: the additive-instead-of-delta ratchet climbed a row 158.0 → 165.2 over eight
    commits in 92 minutes while nothing about its evidence changed."""
    row = _row(recurring_cost=GATE)
    priority.apply_recurring_cost([row], weights, today=TODAY)
    once = row["score"]
    for _ in range(3):
        priority.apply_recurring_cost([row], weights, today=TODAY)
    assert row["score"] == once


def test_the_term_is_reversible_when_the_cost_is_removed(weights):
    """Fixing the defect must give the points back, not leave a ratchet behind."""
    row = _row(recurring_cost=GATE)
    priority.apply_recurring_cost([row], weights, today=TODAY)
    assert row["score"] > 116.0
    row.pop("recurring_cost")
    priority.apply_recurring_cost([row], weights, today=TODAY)
    assert row["score"] == 116.0
    assert "recurring_cost_factor" not in row["score_inputs"]


def test_a_null_score_inputs_does_not_crash_the_scorer(weights):
    """⛔ AUT-PD-152: one row in a 265-row ledger carried `"score_inputs": null` and `setdefault`
    took the whole loop down — step 3 of every cycle — on state no cycle had touched."""
    row = _row(recurring_cost=GATE, score_inputs=None)
    priority.apply_recurring_cost([row], weights, today=TODAY)
    assert row["score_inputs"]["recurring_cost_factor"] > 0


def test_the_measurement_survives_a_rescore(weights):
    """⛔ `build_entries` reads only systems/graph, so a re-derived row carries no block. If
    `merge()` did not carry it, every `--write` would silently delete the debt and the term would
    reset to zero every cycle — measuring nothing, which is this repository's standing failure."""
    assert "recurring_cost" in priority.SESSION_OWNED
