"""A session at its cycle cap with a blocked handoff may stop — and nothing else may.

⛔⛔ WHY THIS EXISTS, MEASURED 2026-08-28. The turn-end stop hook accepted three answers: something
running, something blocked on a human, or START ONE — with "A SCHEDULED ROUTINE IS NOT AN ANSWER"
written in. Those are exhaustive only for a session that CAN hand off. A Routine-fired session,
already at `max_cycles_per_session`, whose `create_session` was refused at the platform's lineage
depth limit, had NO legal answer, so the only move that satisfied the hook was another cycle in the
same context. Result: CYC-0033 … CYC-0041 — NINE cycles in one session against a cap of 2 — and one
receipt named the hook in its own `shape` field.

★ The loop never needed the handoff: the driver Routine fires `13 */4 * * *`, so a capped session
that stops is not stalling — the cron is the successor.

⛔ THE DANGER THIS FILE GUARDS IS THE OPPOSITE ONE. "I may stop" is the most attractive sentence in
the loop, and an unearned one turns the whole anti-stall apparatus off. So every test below is about
REFUSING it: an absent handoff record, a placeholder session id, too few receipts, an unreadable cap.
Only the last test grants it, and only with all four conditions met.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import session_cap as C  # noqa: E402

REFUSAL = ("create_session: caller session is at lineage depth 8 (limit 8); cannot spawn or "
           "re-arm further child sessions")


def _r(sid="sess-aaaa1111", refused=None, unavailable=None, child=None):
    h = {}
    if refused is not None:
        h["refused_by"] = refused
    if unavailable is not None:
        h["mechanism_unavailable"] = unavailable
    if child is not None:
        h["child_session_id"] = child
    return {"session_id": sid, "handoff": h}


@pytest.fixture
def env(monkeypatch, tmp_path):
    def install(receipts, sid="sess-aaaa1111", cap=2):
        d = tmp_path / "receipts"
        d.mkdir(exist_ok=True)
        for i, r in enumerate(receipts):
            (d / f"CYC-{i:04d}-x.json").write_text(json.dumps(r), encoding="utf-8")
        state = tmp_path / "autonomy-state.json"
        state.write_text(json.dumps({"max_cycles_per_session": cap}), encoding="utf-8")
        monkeypatch.setattr(C, "RECEIPTS", str(d))
        monkeypatch.setattr(C, "STATE", str(state))
        if sid is None:
            monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
        else:
            monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", sid)
    return install


def test_the_nine_cycle_session_would_have_been_allowed_to_stop(env):
    """⭐ THE POSITIVE CONTROL, and it is the incident itself: at the cap, handoff refused verbatim."""
    env([_r(refused=REFUSAL), _r(refused=REFUSAL)])
    may, why = C.verdict()
    assert may, why
    assert "lineage depth 8" in why


def test_an_absent_handoff_record_is_a_session_that_did_not_try(env):
    """⛔ THE CENTRAL REFUSAL. Without this, "I could not hand off" is claimable by any session that
    never called the tool — the same rule handoff.refusal_of states, for the same reason."""
    env([_r(), _r()])
    may, why = C.verdict()
    assert not may
    assert "did not try" in why


def test_a_placeholder_session_id_counts_as_no_receipts(env):
    """⛔⛔ THE EXACT LITERAL THE NINE CYCLES WROTE. If a placeholder matched, every scheduled session
    would inherit every other one's receipts and reach the cap on its FIRST cycle — the failure this
    module exists to end, inverted into a free pass."""
    env([_r(sid="scheduled-routine-session", refused=REFUSAL),
         _r(sid="scheduled-routine-session", refused=REFUSAL)],
        sid="scheduled-routine-session")
    may, why = C.verdict()
    assert not may
    assert "0 receipt" in why


def test_another_sessions_receipts_are_not_mine(env):
    env([_r(sid="sess-bbbb2222", refused=REFUSAL), _r(sid="sess-bbbb2222", refused=REFUSAL)],
        sid="sess-aaaa1111")
    may, why = C.verdict()
    assert not may and "0 receipt" in why


def test_below_the_cap_must_not_stop(env):
    """One cycle done against a cap of two is a session with work left in it."""
    env([_r(refused=REFUSAL)])
    may, why = C.verdict()
    assert not may
    assert "has not yet done the work" in why


def test_a_session_that_did_hand_off_is_not_blocked(env):
    """⛔ A child session means this module's BLOCKED branch does not apply. Claiming "blocked" while
    holding a successor id would let a healthy session use that branch to stop early.

    ⚠ AMENDED 2026-09-01 (AUT-PD-169, seat S8-HANDOFF), AND THE GUARANTEE IS UNCHANGED WHILE ONE
    ASSERTION IS. This test used to read the composite `verdict()` and assert `not may` — which
    checked the stated guarantee only by PROXY, and the proxy held for the wrong reason: nothing
    read `handoff.child_session_id` at all, so a session that had successfully handed off scored
    identically to one that never tried and was told MUST NOT STOP. The turn-end hook then fell
    through to its loud branch, whose option 1 instructs the parent to claim the row for its
    successor — and a successor claims for ITSELF under a cycle id derived from a harness uuid the
    parent never sees, so `claim.decide()` YIELDS on every owner string the parent can write.
    ⭐ SO THE GUARANTEE IS NOW ASSERTED WHERE IT LIVES — `blocked_handoff()` still returns None, and
    the verdict still does not take the blocked route — and the composite answer is asserted to be
    the SEPARATE handed-off one rather than a refusal. Nothing here is loosened: `_verdict()` still
    requires `cap` receipts from THIS session, and a self-named or blank child id still buys nothing
    (`test_a_session_that_handed_off_is_not_a_session_that_did_not_try.py`).
    """
    env([_r(refused=REFUSAL), _r(child="sess-cccc3333", refused=REFUSAL)])
    assert C.blocked_handoff(_r(child="sess-cccc3333", refused=REFUSAL)) is None, (
        "a receipt carrying a successor id is being read as a BLOCKED handoff — that is the branch "
        "this test exists to keep it out of")
    may, code, why = C._verdict()
    assert code == C.HANDED_OFF, f"the blocked branch was reached after all: {code} — {why}"
    assert may, why
    assert "sess-cccc3333" in why


def test_an_unreadable_cap_buys_nothing(env, monkeypatch, tmp_path):
    env([_r(refused=REFUSAL), _r(refused=REFUSAL)])
    monkeypatch.setattr(C, "STATE", str(tmp_path / "gone.json"))
    may, why = C.verdict()
    assert not may and "unreadable" in why


def test_an_unset_session_id_buys_nothing(env):
    env([_r(refused=REFUSAL), _r(refused=REFUSAL)], sid=None)
    may, why = C.verdict()
    assert not may
    assert "CLAUDE_CODE_SESSION_ID" in why


@pytest.mark.parametrize("bad", ["", "   ", None, 3, True])
def test_a_nonsense_refusal_is_not_a_refusal(env, bad):
    """The refusal must be the platform's words. A blank or a non-string is an absent record."""
    env([_r(refused=REFUSAL), _r(refused=bad)])
    may, _ = C.verdict()
    assert not may


def test_a_named_absent_mechanism_also_counts(env):
    """The other real shape: the tool was not reachable at all, named rather than quoted. This is
    what the scheduled sessions hit (AUT-PD-045), and it must be recorded, not inferred."""
    env([_r(unavailable="no create_session tool in a scheduled-Routine context"),
         _r(unavailable="no create_session tool in a scheduled-Routine context")])
    may, why = C.verdict()
    assert may and "no create_session tool" in why


def test_the_hook_consults_it_before_demanding_another_cycle():
    """⚠ A module nothing calls changes nothing — the defect this repository has recorded twice
    (`subagent_width` governed nothing for a fortnight; the census lane's exempt flag)."""
    repo = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
    hook = os.path.join(repo, ".claude", "hooks", "ready-work-at-turn-end.sh")
    with open(hook, encoding="utf-8") as fh:
        body = fh.read()
    live = [ln for ln in body.split("\n") if not ln.lstrip().startswith("#")]
    assert any("session_cap.py" in ln for ln in live), "the hook does not call session_cap.py"
    assert any("--check" in ln and "CAP_CHECK" in ln for ln in live), \
        "the hook does not run session_cap's --check"
    demand = body.index("THE TURN IS ENDING WITH READY WORK")
    call = body.index("CAP_CHECK")
    assert call < demand, "the cap check runs AFTER the demand, so it can never prevent one"
