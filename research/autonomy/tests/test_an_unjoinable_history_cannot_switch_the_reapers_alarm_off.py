#!/usr/bin/env python3
"""The reaper's alarm must not be latched off by history nobody can fix (AUT-PD-124).

⛔⛔ THE DEFECT, MEASURED ON `origin/main` 2026-08-28. `session_reaper.py` exists to say one thing a
human must act on: *this idle session finished without its work reaching the trunk.* AUT-PD-129
correctly stopped it asserting that when the join is broken — if a committed receipt names no CCR
session id, "no receipt matched" is not evidence the cycle died. It measured that gap as a COUNT
over every committed receipt and softened the verdict whenever the count was non-zero.

⚠ THE COUNT IS TAKEN OVER IMMUTABLE COMMITTED HISTORY, SO IT CAN NEVER FALL. Re-measured this day
over 76 committed cycle receipts: 63 cannot join, and 39 of those name no session id ANYWHERE —
prose such as "unknown -- fired by the UI-created autonomy Routine" — so no future act can recover
which session wrote them. The softening therefore never expires and the death branch became
UNREACHABLE in production on the day it was written: `preflight.sh` and `receipt_schema.py` each
carry the same lesson in their own comments (a gate clearable only by an impossible act is a gate
that is permanently off).

★ THE FIX UNDER TEST. An unjoinable receipt can only excuse a session that could have WRITTEN one,
and a receipt lands after its author session starts. So the reaper derives a HORIZON — the commit
time of the newest unjoinable receipt — and softens the verdict only for sessions created at or
before it. It needs no new pinned constant, and it expires by itself: from
`receipt_schema.FIRST_CCR_GOVERNED_CYCLE` every receipt carries `ccr_session_id`, so the horizon
stops moving and every session created after it gets the real finding back.

⛔ WHAT MAY NEVER CHANGE, AND IS PINNED HERE TWICE OVER: none of this can archive anything. Both
branches are `keep`; the horizon only chooses which sentence the human reads. A session whose work
is genuinely not on the trunk must still be KEPT — that property is
`test_session_reaper_refuses_to_lose_work.py`'s, and it is re-asserted here against every new path.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
sys.path.insert(0, AUTONOMY)

import session_reaper as R  # noqa: E402

HORIZON = "2026-08-28T21:47:16+00:00"
BEFORE = "2026-08-28T19:35:54.328288Z"   # a real session's created_at shape, pre-horizon
AFTER = "2026-08-28T23:10:00Z"           # created after the last unjoinable receipt landed


def _sess(sid="session_01Orphan000000", created=None):
    s = {"id": sid, "session_status": "SESSION_STATUS_IDLE",
         "title": "EMC research loop — cycle (x)", "tags": ["emc-research-loop"]}
    if created is not None:
        s["created_at"] = created
    return s


def _verdict(monkeypatch, session, horizon, unjoinable=63):
    monkeypatch.setattr(R, "committed_session_ids", lambda ref="HEAD": set())
    return R.classify([session], None, unjoinable_receipts=unjoinable, join_horizon_utc=horizon)


# ---------------------------------------------------------------------------------------------
# (1) the horizon itself
# ---------------------------------------------------------------------------------------------

def _fake_git(unjoinable_payload, log_out):
    """A git that answers ls-tree / show / log from a fixed payload."""
    def run(cmd, **kw):
        class Out:
            returncode = 0
            stderr = ""
        o = Out()
        if cmd[1] == "ls-tree":
            o.stdout = " ".join(unjoinable_payload)
        elif cmd[1] == "show":
            o.stdout = json.dumps(unjoinable_payload[cmd[2].rsplit("/", 1)[-1]])
        elif cmd[1] == "log":
            o.stdout = log_out
        else:                                        # pragma: no cover - a shape we never issue
            o.stdout = ""
        return o
    return run


_TWO = {
    "CYC-0068-aaaaaaaa.json": {"session_id": "aaaaaaaa-1111-2222-3333-444444444444"},
    "CYC-0069-bbbbbbbb.json": {"session_id": "scheduled-routine-session"},
}
_LOG = ("\x012026-08-28T21:47:16+00:00\n"
        "research/autonomy/receipts/CYC-0069-bbbbbbbb.json\n"
        "\n"
        "\x012026-08-28T18:02:00+00:00\n"
        "research/autonomy/receipts/CYC-0068-aaaaaaaa.json\n")


def test_the_horizon_is_the_newest_unjoinable_receipts_commit(monkeypatch):
    monkeypatch.setattr(R.subprocess, "run", _fake_git(_TWO, _LOG))
    assert R.unjoinable_receipt_names() == list(_TWO)
    assert R.newest_unjoinable_receipt_commit() == "2026-08-28T21:47:16+00:00", (
        "the horizon must be the NEWEST unjoinable receipt's commit; an older one would soften the "
        "verdict for sessions the gap cannot excuse")


def test_a_fully_joinable_history_has_no_horizon(monkeypatch):
    """⛔ The healthy case must stay exactly as it was: no gap, no softening, no horizon."""
    payload = {"CYC-0070-cccccccc.json": {"session_id": "cccccccc-1111-2222-3333-444444444444",
                                          "ccr_session_id": "session_018A9rdUZLrexk1HJrKtDCd2"}}
    monkeypatch.setattr(R.subprocess, "run", _fake_git(payload, ""))
    assert R.unjoinable_receipt_names() == []
    assert R.receipts_that_cannot_join() == 0
    assert R.newest_unjoinable_receipt_commit() is None


def test_the_count_and_the_horizon_read_the_same_scan(monkeypatch):
    """One definition of 'can this receipt join?', not two — CLAUDE.md rule 1. A second copy is what
    went stale in this very module once already (the private receipt-filename regex)."""
    monkeypatch.setattr(R.subprocess, "run", _fake_git(_TWO, _LOG))
    assert R.receipts_that_cannot_join() == len(R.unjoinable_receipt_names()) == 2


# ---------------------------------------------------------------------------------------------
# (2) the verdict the horizon chooses
# ---------------------------------------------------------------------------------------------

def test_a_session_created_after_the_horizon_gets_the_real_finding_back(monkeypatch):
    """⛔⛔ THE DEFECT'S REGRESSION. This session cannot own any unjoinable receipt — every one of
    them landed before it existed — so 'no receipt names it' IS evidence, and the alarm must fire."""
    why = _verdict(monkeypatch, _sess(created=AFTER), HORIZON)["keep"][0]["why"]
    assert "died holding uncommitted work" in why, why
    assert "DEGRADED" not in why, (
        "63 unjoinable receipts from before this session existed are still switching its alarm off; "
        "that softening can never expire, because committed history never gains a CCR id: " + why)


def test_a_session_created_before_the_horizon_stays_degraded(monkeypatch):
    """The other half, and it is not optional: this session could be the author of an unjoinable
    receipt, so asserting a death would be the false finding AUT-PD-129 removed."""
    why = _verdict(monkeypatch, _sess(created=BEFORE), HORIZON)["keep"][0]["why"]
    assert "DEGRADED" in why and "63" in why, why
    assert "this is a finding, not litter" not in why, why


@pytest.mark.parametrize("session,horizon,why_it_must_soften", [
    (_sess(), HORIZON, "a row with no created_at cannot be shown to be younger than the gap"),
    (_sess(created="not a timestamp"), HORIZON, "an unparseable created_at is not a reading"),
    (_sess(created=""), HORIZON, "an empty created_at is not a reading"),
    (_sess(created=AFTER), None, "an unknown horizon cannot license a death claim"),
    (_sess(created=HORIZON), HORIZON, "created exactly at the horizon is not strictly after it"),
])
def test_every_uncertainty_fails_toward_silence(monkeypatch, session, horizon, why_it_must_soften):
    """⚠ CLAUDE.md §4: an absent reading is not a reading of absence. Each of these is a MISSING
    measurement, and none of them may be spent as evidence that a cycle died."""
    why = _verdict(monkeypatch, session, horizon)["keep"][0]["why"]
    assert "DEGRADED" in why, why_it_must_soften + " -- got: " + why


# ---------------------------------------------------------------------------------------------
# (3) the property that outranks the feature
# ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("created,horizon", [
    (AFTER, HORIZON), (BEFORE, HORIZON), (None, HORIZON), (AFTER, None), (None, None),
    ("not a timestamp", HORIZON),
])
def test_no_horizon_verdict_ever_archives_an_unmatched_session(monkeypatch, created, horizon):
    """⛔⛔ THE SAFETY PROPERTY, RE-ASSERTED ON EVERY PATH THIS CHANGE ADDS. A session whose work is
    not shown to be on the trunk is KEPT, whatever the join's health. Archiving releases the
    container, so a wrong answer here is unrecoverable and silent — the horizon may only choose
    between two sentences, never between keep and archive."""
    v = _verdict(monkeypatch, _sess(created=created), horizon)
    assert v["archive"] == [], (
        "the reaper archived a session no committed receipt names; that is the one failure this "
        "module may never have")
    assert len(v["keep"]) == 1


def test_a_delivered_session_is_still_archived_whatever_the_horizon_says(monkeypatch):
    """The positive control. Without it this suite would pass on a reaper that archives NOTHING,
    which is precisely the state AUT-PD-124 was filed against."""
    monkeypatch.setattr(R, "committed_session_ids", lambda ref="HEAD": {"session_01Delivered0000"})
    v = R.classify([_sess("session_01Delivered0000", created=BEFORE)], None,
                   unjoinable_receipts=63, join_horizon_utc=HORIZON)
    assert [r["id"] for r in v["archive"]] == ["session_01Delivered0000"], v


# ---------------------------------------------------------------------------------------------
# (4) against the real trunk, because the defect was invisible in fixtures
# ---------------------------------------------------------------------------------------------

def test_the_alarm_is_reachable_on_the_committed_tree():
    """⛔ THE MEASUREMENT, NOT A FIXTURE. The bug was that every fixture-level test passed while the
    death branch was unreachable over the ACTUAL receipts. So this runs the real scan: whatever the
    trunk's history looks like, a session created after the horizon must still be able to raise the
    alarm."""
    horizon = R.newest_unjoinable_receipt_commit()
    unjoinable = R.receipts_that_cannot_join()
    if unjoinable and horizon is None:
        pytest.fail("there are %d unjoinable committed receipts but no horizon could be derived "
                    "from git, so the reaper's death finding is switched off with no way back on"
                    % unjoinable)
    fresh = _sess(created="2099-01-01T00:00:00Z")
    v = R.classify([fresh], None, unjoinable_receipts=unjoinable, join_horizon_utc=horizon)
    assert v["archive"] == []
    assert "died holding uncommitted work" in v["keep"][0]["why"], (
        "on the real committed tree the reaper still cannot report a cycle that died holding work; "
        "unjoinable=%r horizon=%r" % (unjoinable, horizon))
