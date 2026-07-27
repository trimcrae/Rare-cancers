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
    tll.record("rented-nothing", stage="rent", path=ledger,
               gate={"ratio_vs_basis": 2.436, "hold": True}, n_requested=4, n_rented=0)
    rows = tll.load(ledger)["attempts"]
    assert [r["outcome"] for r in rows] == ["dispatched", "rented-nothing"]
    assert rows[0]["gate_ratio_vs_basis"] == 1.261, "the CLEAR that authorised it must survive"
    assert rows[1]["gate_ratio_vs_basis"] == 2.436
    # and the row explains itself without a second lookup
    assert "rented no host" in rows[1]["what_that_means"]


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
    tll.record("rented-nothing", stage="rent", path=ledger, n_requested=4, n_rented=0,
               gate={"ratio_vs_basis": 1.904}, reason="every offer above the buy line")
    s = tll.summary_line(ledger)
    assert "rented-nothing" in s and "0/4 rented" in s and "1.904x basis" in s and "ET" in s


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
