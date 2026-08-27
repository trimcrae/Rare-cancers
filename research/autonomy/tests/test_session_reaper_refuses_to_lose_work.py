#!/usr/bin/env python3
"""The reaper's safety properties, asserted rather than trusted.

⛔ THIS GUARD EXISTS BECAUSE THE ACT IS IRREVERSIBLE-ISH AND SILENT. Archiving releases a session's
container. Every test below is a case where archiving would DESTROY something or MANUFACTURE a
finding, and each one is written as "the reaper must refuse", never as "the reaper usually refuses".

★ The regression at the bottom is the one that actually bit, on the reaper's first run.
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import session_reaper as R  # noqa: E402


def _sess(sid, status="SESSION_STATUS_IDLE", title="EMC research loop — cycle (x)", tags=None):
    return {"id": sid, "session_status": status, "title": title, "tags": tags}


def _classify(sessions, delivered, self_id=None, monkeypatch=None):
    monkeypatch.setattr(R, "committed_session_ids", lambda ref="HEAD": set(delivered))
    return R.classify(sessions, self_id)


def _ids(rows):
    return {r["id"] for r in rows}


def test_a_running_session_is_never_archived(monkeypatch):
    """⛔ Archiving a live cycle kills work in progress."""
    v = _classify([_sess("session_alive", "SESSION_STATUS_RUNNING")], {"session_alive"},
                  monkeypatch=monkeypatch)
    assert _ids(v["archive"]) == set(), "a RUNNING session was offered for archiving"


def test_the_calling_session_is_never_archived(monkeypatch):
    """A cycle that reaps itself releases the container it is still using."""
    v = _classify([_sess("session_me")], {"session_me"}, self_id="session_me", monkeypatch=monkeypatch)
    assert _ids(v["archive"]) == set()
    assert "never reaps itself" in v["keep"][0]["why"]


def test_an_unknown_status_defaults_to_alive(monkeypatch):
    """⛔ A status string this file has never seen is not evidence of finishedness.

    The platform may add states; the reaper must not archive on a state it cannot interpret.
    """
    v = _classify([_sess("session_weird", "SESSION_STATUS_SOMETHING_NEW")], {"session_weird"},
                  monkeypatch=monkeypatch)
    assert _ids(v["archive"]) == set(), "an unrecognised status was treated as safe to archive"


def test_a_non_loop_session_is_out_of_scope(monkeypatch):
    """The reaper cleans up after the loop, not after the account."""
    v = _classify([_sess("session_other", title="Regular screens status check")], {"session_other"},
                  monkeypatch=monkeypatch)
    assert _ids(v["archive"]) == set()


def test_an_idle_loop_session_with_no_committed_receipt_is_kept_as_a_finding(monkeypatch):
    """⛔⛔ THE CENTRAL SAFETY PROPERTY. A cycle that died holding uncommitted work looks exactly
    like a finished one. Archiving it converts a recoverable problem into a lost one, silently."""
    v = _classify([_sess("session_died")], delivered=set(), monkeypatch=monkeypatch)
    assert _ids(v["archive"]) == set()
    why = v["keep"][0]["why"]
    assert "NO committed receipt" in why and "finding" in why, (
        "a session with no committed receipt must be kept AND explained as a finding, so a human "
        f"sees it rather than losing it; got: {why}")


def test_an_idle_loop_session_whose_receipt_is_committed_is_archived(monkeypatch):
    """The positive control. Without this the suite would pass on a reaper that archives NOTHING —
    which is safe and useless, and is exactly the shape a gate rots into."""
    v = _classify([_sess("session_done")], {"session_done"}, monkeypatch=monkeypatch)
    assert _ids(v["archive"]) == {"session_done"}


def test_tagged_sessions_are_in_scope_even_with_an_unhelpful_title(monkeypatch):
    v = _classify([_sess("session_tagged", title="untitled", tags=[R.LOOP_TAG])],
                  {"session_tagged"}, monkeypatch=monkeypatch)
    assert _ids(v["archive"]) == {"session_tagged"}


# --------------------------------------------------------------------------------------------
# The regression that actually bit, on this reaper's first run against real data.
# --------------------------------------------------------------------------------------------

def test_a_session_id_field_carrying_prose_still_yields_its_id(tmp_path, monkeypatch):
    """⛔ `session_id` IS FREE TEXT AND CYCLES HAVE WRITTEN PROSE INTO IT.

    Measured 2026-08-27: comparing the whole field for equality reported CYC-0013, CYC-0014 and
    CYC-0015 — three cycles that delivered — as "idle with no committed receipt", i.e. as sessions
    that died holding work. That is a false alarm a human would go chase AND a refusal to clean up
    the sessions this reaper exists to close, from one bug.
    """
    real = ("session_016z8Nm7cZTaLN4smGWue75c (spawned session, no live user present — started by "
            "CYC-0012 at its 2-cycle cap)")
    assert R._SESSION_ID.findall(real) == ["session_016z8Nm7cZTaLN4smGWue75c"]


def test_committed_session_ids_EXTRACTS_from_a_prose_contaminated_field(monkeypatch):
    """⛔⛔ THE REGRESSION ITSELF, DRIVEN THROUGH THE FUNCTION THAT USES THE PATTERN.

    ⚠ Written after a mutation run: reverting `ids.update(_SESSION_ID.findall(sid))` to the original
    `ids.add(sid)` — the precise bug that misreported three delivered cycles — SURVIVED all fourteen
    tests, because the only coverage of it asserted the REGEX rather than the function. A pattern
    proven correct in isolation says nothing about the consumer that was supposed to call it
    (paper-hardening §8b.1e: two consumers of one expression, and only one was checked).
    """
    receipt = ('{"session_id": "session_016z8Nm7cZTaLN4smGWue75c (spawned session, no live user '
               'present — started by CYC-0012 at its 2-cycle cap)"}')

    def fake_run(args, cwd=None, capture_output=None, text=None):
        class _R:
            returncode = 0
            stderr = ""
        r = _R()
        r.stdout = "CYC-9002.json\n" if args[1] == "ls-tree" else receipt
        return r

    monkeypatch.setattr(R.subprocess, "run", fake_run)
    assert "session_016z8Nm7cZTaLN4smGWue75c" in R.committed_session_ids(), (
        "the id was not recovered from a session_id field carrying prose, so a cycle that DID "
        "deliver would be reported as one that died holding uncommitted work")


@pytest.mark.parametrize("field,expected", [
    ("session_01ABCDEFGHIJ", ["session_01ABCDEFGHIJ"]),
    ("session_01ABCDEFGHIJ (spawned session, no live user present)", ["session_01ABCDEFGHIJ"]),
    ("unknown -- fired by the UI-created autonomy Routine, no session_id surfaced", []),
    ("66dab3ca-b11c-5d0b-a0d9-9babe135276e (interactive, trimcrae present)", []),
    ("top-level scheduled Routine session (not a spawned child of any prior CYC)", []),
])
def test_every_session_id_shape_this_repository_has_actually_written(field, expected):
    """⚠ These five shapes are transcribed from the committed receipts, not invented. A sixth shape
    appearing tomorrow is a reason to extend this list, not to loosen the pattern."""
    assert R._SESSION_ID.findall(field) == expected


def test_a_recorded_child_id_is_not_treated_as_delivery(tmp_path, monkeypatch):
    """⛔ `handoff.child_session_id` proves a child was CREATED, never that it DELIVERED.

    Counting it would archive a spawned session that died before writing anything — the one case
    that must stay visible, and the exact case AUT-PD-003 describes.
    """
    receipts = tmp_path / "receipts"
    receipts.mkdir()
    (receipts / "CYC-9001.json").write_text(
        '{"session_id": "session_parentAAAAAA", '
        '"handoff": {"child_session_id": "session_childBBBBBB"}}')

    def fake_ls(args, cwd=None, capture_output=None, text=None):
        class R_:
            returncode = 0
            stderr = ""
        r = R_()
        if args[1] == "ls-tree":
            r.stdout = "CYC-9001.json\n"
        else:
            r.stdout = (receipts / "CYC-9001.json").read_text()
        return r

    monkeypatch.setattr(R.subprocess, "run", fake_ls)
    ids = R.committed_session_ids()
    assert "session_parentAAAAAA" in ids, "the writing session must count as delivered"
    assert "session_childBBBBBB" not in ids, (
        "a child id recorded by its PARENT was counted as delivered work; a child that died before "
        "writing a receipt would then be archived and its container released")
