#!/usr/bin/env python3
"""`holder_liveness.py`'s safety properties, asserted rather than trusted (AUT-PD-150).

⛔ THE ACT THIS INFORMS IS DESTRUCTIVE. Releasing another worker's lease hands its item to somebody
else; do it to a LIVE worker and two sessions work one row, which is AUT-PD-021's twenty wasted
minutes. So every test below is written as "the module must REFUSE to say DEAD", never as "it
usually refuses" — the false-positive direction is the one that costs work.

★ THE REGRESSION AT THE BOTTOM is the incident itself: seven leases held by four seats of a session
that had been archived, which `continuity.py` counted as live workers and used to park 109 rows.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import holder_liveness as H  # noqa: E402

ARCHIVED = "SESSION_STATUS_ARCHIVED"
SESS = "session_01SVfJ6HmD2f5u4Z2TPwfTCG"


def _write(tmp_path, ledger_rows, receipts, verdict=None):
    led = tmp_path / "ledger.json"
    led.write_text(json.dumps({"entries": ledger_rows}), encoding="utf-8")
    rdir = tmp_path / "receipts"
    rdir.mkdir(exist_ok=True)
    for i, r in enumerate(receipts):
        (rdir / f"CYC-{i:04d}-x.json").write_text(json.dumps(r), encoding="utf-8")
    vpath = None
    if verdict is not None:
        v = tmp_path / "verdict.json"
        v.write_text(json.dumps({"sessions": verdict}), encoding="utf-8")
        vpath = str(v)
    return str(led), str(rdir), vpath


def _row(eid, owner, state="queued"):
    return {"id": eid, "owner": owner, "state": state}


def _receipt(uuid8, ccr):
    return {"session_id": f"{uuid8}-529e-5b9e-9403-aa327556bed0", "ccr_session_id": ccr}


def _one(tmp_path, ledger_rows, receipts, verdict=None, me=None):
    led, rdir, vpath = _write(tmp_path, ledger_rows, receipts, verdict)
    return H.arbitrate(vpath, led, rdir, me)


# ── the finding it exists to make ────────────────────────────────────────────────────────────────

def test_an_archived_holder_is_dead_and_its_lease_is_releasable(tmp_path):
    rows = _one(tmp_path, [_row("AUT-PD-130", "SEAT-s1-ba841eee")],
                [_receipt("ba841eee", SESS)], {SESS: {"session_status": ARCHIVED}})
    assert [r["verdict"] for r in rows] == [H.DEAD]
    assert rows[0]["releasable"] is True
    assert H.dead_owners(rows) == {"SEAT-s1-ba841eee"}


# ── every way it must REFUSE to say DEAD ─────────────────────────────────────────────────────────

def test_no_verdict_is_unmeasured_and_never_alive_and_never_dead(tmp_path):
    """⛔ CLAUDE.md §4: an absent reading is not a reading of absence."""
    rows = _one(tmp_path, [_row("AUT-PD-130", "SEAT-s1-ba841eee")],
                [_receipt("ba841eee", SESS)], verdict=None)
    assert rows[0]["verdict"] == H.UNMEASURED
    assert rows[0]["releasable"] is False
    assert H.dead_owners(rows) == set()


def test_a_holder_missing_from_a_supplied_verdict_is_still_unmeasured(tmp_path):
    """A verdict that names OTHER sessions says nothing about this one."""
    rows = _one(tmp_path, [_row("AUT-PD-130", "SEAT-s1-ba841eee")],
                [_receipt("ba841eee", SESS)], {"session_other": {"session_status": ARCHIVED}})
    assert rows[0]["verdict"] == H.UNMEASURED
    assert rows[0]["releasable"] is False


@pytest.mark.parametrize("status", ["SESSION_STATUS_RUNNING", "SESSION_STATUS_IDLE"])
def test_a_live_holder_is_never_releasable(tmp_path, status):
    """⛔ THE EXPENSIVE DIRECTION. An IDLE session is between turns, not dead."""
    rows = _one(tmp_path, [_row("AUT-PD-130", "SEAT-s1-ba841eee")],
                [_receipt("ba841eee", SESS)], {SESS: {"session_status": status}})
    assert rows[0]["verdict"] == H.ALIVE
    assert rows[0]["releasable"] is False


def test_a_status_the_module_does_not_recognise_is_not_dead(tmp_path):
    """A new status the control plane invents must not silently become a release licence."""
    rows = _one(tmp_path, [_row("AUT-PD-130", "SEAT-s1-ba841eee")],
                [_receipt("ba841eee", SESS)], {SESS: {"session_status": "TOTALLY_NEW_THING"}})
    assert rows[0]["verdict"] == H.UNKNOWN_STATUS
    assert rows[0]["releasable"] is False


def test_terminal_statuses_is_exactly_what_was_observed(tmp_path):
    """⛔ Widening this set is a deliberate edit backed by an observation, not a drift."""
    assert H.TERMINAL_STATUSES == {"SESSION_STATUS_ARCHIVED"}
    assert H.RELEASABLE == {H.DEAD}


def test_an_owner_with_no_receipt_is_unresolved_not_dead(tmp_path):
    """A gap in the loop's own records is a finding about the records, not a verdict on a worker."""
    rows = _one(tmp_path, [_row("AUT-PD-143", "CYC-0072-1681f3fa")], [],
                {SESS: {"session_status": ARCHIVED}})
    assert rows[0]["verdict"] == H.UNRESOLVED
    assert rows[0]["releasable"] is False


def test_a_receipt_whose_session_id_is_prose_maps_nothing(tmp_path):
    """⚠ Cycles really have written prose into `session_id`; that is how the reaper went wrong."""
    rows = _one(tmp_path, [_row("AUT-PD-130", "SEAT-s1-ba841eee")],
                [{"session_id": "scheduled-routine-session", "ccr_session_id": SESS}],
                {SESS: {"session_status": ARCHIVED}})
    assert rows[0]["verdict"] == H.UNRESOLVED
    assert rows[0]["releasable"] is False


def test_a_session_id_that_merely_STARTS_hex_is_not_a_uuid(tmp_path):
    """⛔ THE MAPPING IS A UUID SHAPE, NOT A PREFIX MATCH. A prose `session_id` whose first eight
    characters happen to be hex would otherwise mint a bogus discriminator -> session mapping, and
    that mapping is what licenses the word DEAD. Caught by mutation on 2026-08-28: relaxing the
    match to `sid[:8]` survived every other test in this file."""
    rows = _one(tmp_path, [_row("AUT-PD-130", "SEAT-s1-ba841eee")],
                [{"session_id": "ba841eee was the seat that died", "ccr_session_id": SESS}],
                {SESS: {"session_status": ARCHIVED}})
    assert rows[0]["verdict"] == H.UNRESOLVED
    assert rows[0]["releasable"] is False


def test_your_own_lease_is_never_reported_against_you(tmp_path):
    rows = _one(tmp_path, [_row("AUT-PD-150", "CYC-0072-2e57571a")],
                [_receipt("2e57571a", "session_self")],
                {"session_self": {"session_status": ARCHIVED}}, me="CYC-0072-2e57571a")
    assert rows == []


def test_a_closed_row_is_not_a_lease(tmp_path):
    rows = _one(tmp_path, [_row("AUT-PD-130", "SEAT-s1-ba841eee", state="done")],
                [_receipt("ba841eee", SESS)], {SESS: {"session_status": ARCHIVED}})
    assert rows == []


# ── the exit code, which is the half a hook reads ────────────────────────────────────────────────

def test_check_exits_1_only_on_a_provably_dead_holder(tmp_path):
    led, rdir, v = _write(tmp_path, [_row("AUT-PD-130", "SEAT-s1-ba841eee")],
                          [_receipt("ba841eee", SESS)], {SESS: {"session_status": ARCHIVED}})
    assert H.main(["--ledger", led, "--receipts", rdir, "--verdict", v, "--check"]) == 1
    # the same tree with nothing observed must NOT exit 1 — silence is not a finding
    assert H.main(["--ledger", led, "--receipts", rdir, "--check"]) == 0


# ── the incident ─────────────────────────────────────────────────────────────────────────────────

def test_the_2026_08_28_incident_seven_leases_four_dead_seats(tmp_path):
    """⛔ Measured: `continuity.py` read 5 workers AT CAPACITY and parked 109 rows, while four of
    the five were seats of `session_01SVfJ6HmD2f5u4Z2TPwfTCG`, archived at 23:17:54Z."""
    ledger = [_row(i, o) for i, o in [
        ("AUT-PD-130", "SEAT-s1-ba841eee"), ("AUT-PD-133", "SEAT-s2-ba841eee"),
        ("AUT-045", "SEAT-s4-ba841eee"), ("AUT-007", "SEAT-s5-ba841eee"),
        ("AUT-008", "SEAT-s5-ba841eee"), ("AUT-011", "SEAT-s5-ba841eee"),
        ("AUT-016", "SEAT-s5-ba841eee"), ("AUT-PD-143", "CYC-0072-1681f3fa")]]
    rows = _one(tmp_path, ledger, [_receipt("ba841eee", SESS)], {SESS: {"session_status": ARCHIVED}})
    assert sum(1 for r in rows if r["releasable"]) == 7
    assert H.dead_owners(rows) == {f"SEAT-s{n}-ba841eee" for n in (1, 2, 4, 5)}
    # ★ and the one holder it could not map is NOT swept up in the finding
    unresolved = [r for r in rows if r["id"] == "AUT-PD-143"]
    assert unresolved[0]["verdict"] == H.UNRESOLVED and unresolved[0]["releasable"] is False
