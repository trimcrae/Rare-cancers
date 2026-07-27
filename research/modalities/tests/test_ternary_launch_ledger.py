#!/usr/bin/env python3
"""Tests for the ternary launch-attempt ledger.

WHY THIS IS TESTED AT ALL, given it is "just a log". Because the thing it replaces was also just a log —
`_last_launch.json`, written by the launcher — and its gap is what produced a wrong report on 2026-07-27: a
launch that dies BEFORE the launcher runs leaves that file untouched and hours stale, which reads as "no
launch was attempted". A record whose absence is indistinguishable from a normal state is worse than none,
so the properties that make this one unambiguous are pinned here.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_launch_ledger as tll  # noqa: E402


@pytest.fixture()
def ledger(tmp_path):
    return str(tmp_path / "attempts.json")


def test_a_dispatched_launch_and_its_outcome_are_two_distinguishable_rows(ledger):
    """★ THE 2026-07-27 FAILURE, in one test. The gate cleared, dispatched, and the launch died — and
    afterwards every artifact looked like an ordinary hold. The ledger must make "authorised and dispatched"
    and "and then it died" two separate, explicit, still-present facts."""
    tll.record("dispatched", stage="market-gate", path=ledger,
               gate={"ratio_vs_basis": 1.261, "hold": False})
    tll.record("refused-on-price", stage="rent", path=ledger,
               gate={"ratio_vs_basis": 2.436, "hold": True}, n_requested=4, n_rented=0)
    rows = tll.load(ledger)["attempts"]
    assert [r["outcome"] for r in rows] == ["dispatched", "refused-on-price"]
    assert rows[0]["gate_ratio_vs_basis"] == 1.261, "the CLEAR that authorised it must survive"
    assert rows[1]["gate_ratio_vs_basis"] == 2.436
    # and the row explains itself without a second lookup
    assert "the guard working" in rows[1]["what_that_means"]


def test_the_outcome_vocabulary_is_closed_so_a_typo_cannot_invent_a_state(ledger):
    with pytest.raises(ValueError):
        tll.record("held", path=ledger)
    assert "refused-on-price" in tll.OUTCOMES and "launched" in tll.OUTCOMES


def test_history_is_appended_never_rewritten(ledger):
    """The defect the ledger exists to close was a MUTABLE single-snapshot file: the dead launch's HOLD
    overwrote the CLEAR that had authorised it, four minutes later, and the evidence was gone. Appending is
    the property that matters — an earlier row must never be editable by a later event."""
    for i in range(5):
        tll.record("dispatched", reason="n=%d" % i, path=ledger)
    rows = tll.load(ledger)["attempts"]
    assert [r["reason"] for r in rows] == ["n=%d" % i for i in range(5)], "newest LAST, nothing rewritten"


def test_the_ledger_is_bounded_so_it_stays_reviewable(ledger):
    for i in range(tll.MAX_ATTEMPTS + 12):
        tll.record("dispatched", reason="n=%d" % i, path=ledger)
    rows = tll.load(ledger)["attempts"]
    assert len(rows) == tll.MAX_ATTEMPTS
    assert rows[-1]["reason"] == "n=%d" % (tll.MAX_ATTEMPTS + 11), "the newest is always kept"


def test_times_are_us_eastern_12_hour_not_utc(ledger):
    """CLAUDE.md §1. The reader of this file is trimcrae, and a 24-hour UTC stamp is the exact thing that
    rule exists to stop. EDT = UTC-4, so 13:16 UTC is 9:16 AM ET — the timestamp of the launch this ledger
    was built because of."""
    import time
    e = tll.record("dispatched", path=ledger)
    assert e["et"].endswith(" ET") and (" AM " in e["et"] + " " or " PM " in e["et"] + " ")
    assert tll._et(time.strptime("2026-07-27T13:16:28Z", "%Y-%m-%dT%H:%M:%SZ")) == "9:16 AM ET"
    assert tll._et(time.strptime("2026-07-27T00:30:00Z", "%Y-%m-%dT%H:%M:%SZ")) == "8:30 PM ET"
    assert tll._et(time.strptime("2026-07-27T16:05:00Z", "%Y-%m-%dT%H:%M:%SZ")) == "12:05 PM ET"


def test_the_summary_line_says_what_happened_without_opening_the_file(ledger):
    """`collect` prints this. If it did not carry the outcome and the board it faced, a reader would still
    have to know the ledger exists and go find it — which is the same failure one indirection further out."""
    tll.record("refused-on-price", stage="rent", path=ledger, n_requested=4, n_rented=0,
               gate={"ratio_vs_basis": 1.904}, reason="every offer above the buy line")
    s = tll.summary_line(ledger)
    assert "refused-on-price" in s and "0/4 rented" in s and "1.904x basis" in s and "ET" in s


def test_an_empty_or_corrupt_ledger_reports_that_rather_than_crashing(tmp_path):
    missing = str(tmp_path / "nope.json")
    assert "no launch attempt" in tll.summary_line(missing)
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert "no launch attempt" in tll.summary_line(str(bad))


def test_the_committed_ledger_is_valid_and_records_the_lost_windows():
    """The real file in the repo. It is seeded with the two 2026-07-27 attempts reconstructed from the job
    logs — the evidence that the lane HAS lost cleared windows, which is the fact a future reader most needs
    and the one that no artifact carried at the time."""
    with open(tll.LEDGER) as fh:
        d = json.load(fh)
    rows = d["attempts"]
    assert rows, "the committed ledger must not be empty"
    assert all(r["outcome"] in tll.OUTCOMES for r in rows)
    lost = [r for r in rows if r["outcome"] == "refused-on-price"]
    assert len(lost) == 2, "both 9:16 AM ET and 9:26 AM ET refusals are recorded"
    assert {r["et"] for r in lost} == {"9:16 AM ET", "9:26 AM ET"}
    assert all(r.get("reconstructed_from_job_log") for r in lost), \
        "a retroactively reconstructed row must SAY it was reconstructed, never pass as live telemetry"


# ---------------------------------------------------------------- the 11:10 AM ET ledger defect
def test_the_gates_own_sentence_is_copied_because_it_carries_the_diagnosis(ledger):
    """★★ THE DEFECT THIS FILE'S OWN AUTHOR SHIPPED (2026-07-27, 11:10 AM ET).

    The gate readout handed to that row contained, verbatim, "could not read the board (RuntimeError: vast
    API GET /search/asks/ -> 403 ...) — an unreadable market is not a cheap one". The ledger copied the
    numeric fields and `hold` and dropped `reason` — the only field that was prose and the only one that
    said WHY. The row therefore recorded `gate_hold: true` with no ratio beside it, and answering "was this
    the price guard or a broken launcher?" still required the job log. That is the exact failure the ledger
    exists to prevent, one level in."""
    gate = {"hold": True,
            "reason": "could not read the board (RuntimeError: vast API GET /search/asks/ -> 403: "
                      "<html>403 Forbidden</html>) — an unreadable market is not a cheap one"}
    e = tll.record("board-unreadable", stage="rent", path=ledger, gate=gate, n_requested=4, n_rented=0)
    assert "403" in e["gate_reason"], "the sentence that carries the diagnosis must survive into the row"
    s = tll.summary_line(ledger)
    assert "403" in s and "⛔ FAULT" in s, "and must be legible in the one line collect prints"
    assert "\n" not in s, "a multi-line provider error page must not break the summary line"


def test_no_outcome_names_two_possibilities(ledger):
    """`rented-nothing` used to mean "every offer above the buy line, OR creates failed". An outcome that
    names two causes names neither, and it was the only thing the ledger said about the 403. Every value is
    now a single fact — enforced, so the disjunction cannot come back by a well-meaning merge."""
    for outcome, meaning in tll.OUTCOMES.items():
        assert " or " not in meaning.lower().replace("authorisation", ""), \
            f"{outcome!r} describes more than one situation: {meaning!r}"
    assert "rented-nothing" not in tll.OUTCOMES


def test_a_price_hold_is_not_a_fault_but_an_unreadable_board_is(ledger):
    """The distinction the CI signal now turns on. Nothing affordable = wait, the work is checkpointed and
    the next tick re-checks. Board unreadable = we never learned what the market cost, so a cleared window
    can be lost without anyone noticing — which is what happened."""
    tll.record("refused-on-price", path=ledger)
    assert not tll.is_fault(ledger)
    assert "⏸ held" in tll.summary_line(ledger)
    tll.record("board-unreadable", path=ledger)
    assert tll.is_fault(ledger)
    assert "⛔ FAULT" in tll.summary_line(ledger)
    tll.record("launched", path=ledger, n_requested=4, n_rented=4)
    assert not tll.is_fault(ledger) and "✅" in tll.summary_line(ledger)


# =============================================================================================================
# ★★ THE 12:39 PM ET ROW — a `launched` that rented nothing, beside a board reading over the buy line
# =============================================================================================================
# On 2026-07-27 the valB_mini lane recorded three `launched` rows in 25 minutes for a FOUR-unit job. Only the
# first rented anything; the 12:29 and 12:39 ticks found every unit already running and rented ZERO. Both were
# filed as `launched` — whose meaning is literally "hosts were actually rented" — because the workflow derived
# the word from the rent step's exit code, and a launch with nothing to do exits 0.
#
# The 12:39 row then carried the launch job's advisory board snapshot: `gate_ratio_vs_basis: 2.032`,
# `gate_mean_usd_per_ns: 0.006931`, both above trimcrae's $0.006539/ns buy line. Read together with the word
# `launched`, the lane's own ledger said we had bought at 2.032x basis. We had not: we bought nothing, and the
# four hosts actually held were billing between 0.80x and 1.08x basis.
#
# These tests pin the two halves of the fix — the word cannot contradict the rental, and the row must carry
# what was PAID and not only what the board cost.
def test_launched_cannot_be_recorded_when_nothing_was_rented(ledger):
    """`launched` means "hosts were actually rented". Zero rentals is therefore not a `launched` row."""
    e = tll.record("launched", path=ledger, n_requested=0, n_rented=0)
    assert e["outcome"] == "nothing-to-launch", \
        "a launch that rented nothing because nothing needed renting must not be filed as `launched`"
    assert "nothing was spent" in e["what_that_means"]
    assert not tll.is_fault(ledger), "a satisfied lane is a normal state, not a fault"


def test_wanting_units_and_renting_none_is_a_fault_not_the_benign_word(ledger):
    """The two zero-rental cases must not collapse. Wanting nothing is benign; wanting four and getting none
    is unexplained, and the file's own rule is that an unrecognised failure is never filed as benign."""
    e = tll.record("launched", path=ledger, n_requested=4, n_rented=0)
    assert e["outcome"] == "submit-failed" and tll.is_fault(ledger)


def test_the_row_records_what_was_paid_not_only_what_the_board_cost(ledger):
    """The board mean and the rented rate are DIFFERENT QUANTITIES, and the row must say which is which.

    A gate's `mean_usd_per_ns` prices the n cheapest offers on the market at some instant; it is a property
    of the board and is never conditioned on a purchase. What we pay is read back off the live instance.
    """
    receipt = {"n_requested": 2, "n_rented": 2, "rented": [
        {"unit_id": "u1", "instance": 1, "gpu": "RTX 5090", "usd_per_ns": 0.00273, "x_basis": 0.8,
         "over_buy_line": False},
        {"unit_id": "u2", "instance": 2, "gpu": "RTX 3090", "usd_per_ns": 0.003576, "x_basis": 1.048,
         "over_buy_line": False}]}
    # a board that was expensive at the moment of the snapshot...
    gate = {"ratio_vs_basis": 2.032, "mean_usd_per_ns": 0.006931, "hold": True, "reason": "board is dear"}
    e = tll.record("launched", path=ledger, gate=gate, receipt=receipt)
    assert e["outcome"] == "launched" and e["n_rented"] == 2
    # ...must not be mistakable for what we paid, which was well under the line
    assert e["rented_max_usd_per_ns"] == 0.003576
    assert e["rented_any_over_buy_line"] is False
    line = tll.summary_line(ledger)
    assert "PAID up to $0.003576/ns" in line, "the summary must lead with what was actually paid"
    assert "board(not paid)" in line, \
        "the board figure must be labelled as the market, or a reader takes it for the purchase"


def test_a_zero_rental_row_says_it_paid_nothing(ledger):
    """The precise misreading being fixed: a row whose only $/ns figure was a 2.032x board mean."""
    tll.record("launched", path=ledger, n_requested=0, n_rented=0,
               gate={"ratio_vs_basis": 2.032, "mean_usd_per_ns": 0.006931, "hold": True})
    line = tll.summary_line(ledger)
    assert "PAID $0 (nothing rented)" in line
    assert "board(not paid) 2.032x" in line


def test_the_receipt_supplies_the_counts_so_the_shell_need_not_guess(ledger):
    """The counts come from the launcher, which knows the rental, rather than from a workflow step's exit
    code, which cannot see it. That substitution is the whole root cause."""
    e = tll.record("launched", path=ledger,
                   receipt={"n_requested": 4, "n_rented": 4, "rented": [{"unit_id": "u", "usd_per_ns": 0.003}]})
    assert e["n_requested"] == 4 and e["n_rented"] == 4
