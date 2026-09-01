#!/usr/bin/env python3
"""AUT-PD-169 — the turn-end hook told a spawning session to claim for a successor that claims itself.

⛔⛔ THE KNOT, STATED AS A SEQUENCE, BECAUSE A FIX THAT IS NOT OBVIOUSLY CORRECT ON IT IS NOT A FIX.

    t1  the parent builds `handoff.py --json`; the prompt names row R as the queue's top item.
    t2  `create_session` returns a CCR id (`session_01…`). The child's HARNESS session uuid — the
        value `ids.discriminator()` hashes into every cycle id it will write — is assigned inside
        the child's container and is never returned to the caller.
    t3  the parent's turn ends. `continuity.py --check` sees R ready and unowned and exits 1, and
        the hook prints option 1: "CLAIM THE ITEM FOR THE WORKER THAT IS RUNNING IT".
    t4  if the parent obeys, R's `owner` on the trunk is some string the parent could write.
    t5  the child runs the contract: step 3 re-scores, step 4 calls
        `claim.py --id R --me CYC-NNNN-<discriminator(ITS OWN uuid)>`.
    t6  `claim.decide()` → owner is set and is not `me` → **YIELDED**, whose documented correct
        response is "somebody else holds it, take the next item".
    t7  R is now leased to a session that has ended, and only `priority.release_stale_claims`
        releases it — CYC-0003's parked-queue defect, arriving through the hook's own advice.

★ THE FIX IS ORDERING PLUS WORDING, AND IT ADDS NO LEDGER FIELD. `session_cap._verdict()` now reads
`handoff.child_session_id` BEFORE `blocked_handoff()` — which returns None for a receipt carrying a
child id BY DESIGN, so the success used to fall through to "an absent record is a session that did
not try" — and the hook prints option 1 in two halves: claim for a subagent, never for a spawned
session. AUT-PD-169's own preferred option (b), a `dispatched_to` ledger field, is not built: the
falsifiable record already exists, is already required, and needs no ageing.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(AUTONOMY))
sys.path.insert(0, AUTONOMY)

import claim as CL  # noqa: E402
import ids  # noqa: E402
import session_cap as SC  # noqa: E402

HOOK = os.path.join(REPO, ".claude", "hooks", "ready-work-at-turn-end.sh")
REFUSAL = ("create_session: caller session is at lineage depth 8 (limit 8); cannot spawn or "
           "re-arm further child sessions")


def _r(sid="sess-aaaa1111", ccr=None, refused=None, unavailable=None, child=None):
    h = {}
    if refused is not None:
        h["refused_by"] = refused
    if unavailable is not None:
        h["mechanism_unavailable"] = unavailable
    if child is not None:
        h["child_session_id"] = child
    r = {"session_id": sid, "handoff": h}
    if ccr is not None:
        r["ccr_session_id"] = ccr
    return r


@pytest.fixture
def env(monkeypatch, tmp_path):
    def install(receipts, sid="sess-aaaa1111", cap=2):
        d = tmp_path / "receipts"
        d.mkdir(exist_ok=True)
        for i, r in enumerate(receipts):
            (d / f"CYC-{i:04d}-x.json").write_text(json.dumps(r), encoding="utf-8")
        state = tmp_path / "autonomy-state.json"
        state.write_text(json.dumps({"max_cycles_per_session": cap}), encoding="utf-8")
        monkeypatch.setattr(SC, "RECEIPTS", str(d))
        monkeypatch.setattr(SC, "STATE", str(state))
        monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", sid)
    return install


# =================================================================================================
# 1 · THE KNOT ITSELF — pinned so a future change to `decide()` cannot dissolve it silently
# =================================================================================================

@pytest.mark.parametrize("parent_writes", [
    "CYC-0089-11223344",            # the parent's own cycle id
    "session_01CUYirsUYqbaxCWGsX3iYMq",   # the child's CCR id, which the parent DOES know
    "successor",                    # a label
])
def test_no_owner_string_the_parent_can_write_lets_the_successor_claim(parent_writes):
    """⛔ THE MECHANISM. The successor's `me` is built from an id the parent never sees, so every
    pre-claim the parent is capable of making produces YIELDED — including the child's CCR id, which
    is the one value that LOOKS like it should work."""
    successor_me = f"CYC-0090-{ids.discriminator('9f3c1a02-0000-4000-8000-000000000000')}"
    trunk = {"entries": [{"id": "AUT-PD-999", "owner": parent_writes, "state": "queued"}]}
    verdict, why = CL.decide(trunk, "AUT-PD-999", successor_me)
    assert verdict == CL.YIELDED, f"expected the successor to hand the row back, got {verdict}: {why}"
    assert CL.EXIT_CODES[verdict] == 1


def test_the_row_is_takeable_by_the_successor_when_nobody_pre_claimed_it():
    """⭐ THE CONTROL. The same row, unclaimed, is TAKEN — so the yield above is caused by the
    pre-claim and by nothing else about the fixture."""
    successor_me = f"CYC-0090-{ids.discriminator('9f3c1a02-0000-4000-8000-000000000000')}"
    trunk = {"entries": [{"id": "AUT-PD-999", "owner": None, "state": "queued"}]}
    assert CL.decide(trunk, "AUT-PD-999", successor_me)[0] == CL.TAKEN


def test_the_childs_cycle_id_cannot_be_derived_from_anything_create_session_returns():
    """⛔ WHY (1) IS STRUCTURAL RATHER THAN AWKWARD. `ids.discriminator` hashes the HARNESS uuid;
    `create_session` hands back a `session_01…` CCR id. Two id spaces — so the parent cannot
    compute the string even in principle, and no amount of care closes the gap."""
    harness_uuid = "9f3c1a02-0000-4000-8000-000000000000"
    ccr_id = "session_01CUYirsUYqbaxCWGsX3iYMq"
    assert ids.discriminator(harness_uuid) != ids.discriminator(ccr_id)


# =================================================================================================
# 2 · THE FIX — a session that handed off may stop, and says so in a way the hook can branch on
# =================================================================================================

def test_a_session_at_its_cap_that_handed_off_may_stop(env):
    """⛔ THE DEFECT, INVERTED. Before this, the branch order sent a successful handoff to the
    "did not try" refusal — the loud branch, whose option 1 is the instruction above."""
    env([_r(), _r(child="session_01CUYirsUYqbaxCWGsX3iYMq")])
    may, code, why = SC._verdict()
    assert may, why
    assert code == SC.HANDED_OFF
    assert "session_01CUYirs" in why
    assert "did not try" not in why


def test_it_is_a_different_verdict_from_a_blocked_handoff(env):
    """★ THE TWO STOPS ARE NOT THE SAME STOP AND THE REMEDIES DIFFER: one has a successor running,
    the other has none and is relying on the driver Routine. Collapsing them is exactly what
    AUT-PD-059 measured going wrong one file over."""
    env([_r(refused=REFUSAL), _r(refused=REFUSAL)])
    may, code, _ = SC._verdict()
    assert may and code == SC.HANDOFF_BLOCKED


def test_the_two_valued_face_still_answers_for_callers_that_do_not_branch(env):
    env([_r(), _r(child="session_01CUYirsUYqbaxCWGsX3iYMq")])
    may, why = SC.verdict()
    assert may and isinstance(why, str)


# =================================================================================================
# 3 · THE ANTI-GAMING HALF — "I may stop" is the most attractive sentence in the loop
# =================================================================================================

def test_a_session_may_not_name_itself_as_its_own_successor(env):
    """⛔⛔ AUT-PD-140's SHAPE, ONE FIELD OVER. A self-referential record names no other worker, so
    it would buy a stop for work nobody is doing. Both id spaces are refused, because the receipt
    carries both and only one of them is the obvious thing to type."""
    env([_r(), _r(sid="sess-aaaa1111", child="sess-aaaa1111")])
    assert not SC._verdict()[0]
    env([_r(), _r(sid="sess-aaaa1111", ccr="session_01SELF", child="session_01SELF")])
    assert not SC._verdict()[0]


@pytest.mark.parametrize("bad", ["", "   ", None, 7, True])
def test_a_nonsense_child_id_is_not_a_handoff(env, bad):
    """A blank or a non-string is an ABSENT record, and an absent record is a session that did not
    try — the same rule `handoff.refusal_of` states, for the same reason."""
    env([_r(), _r(child=bad)])
    may, code, why = SC._verdict()
    assert not may and code == SC.MUST_NOT_STOP
    assert "did not try" in why


def test_below_the_cap_a_handoff_does_not_buy_a_stop(env):
    """⛔ THE CAP REQUIREMENT IS UNTOUCHED. Recording a child id must not let a session with work
    left in it stop early — that would be a widening, and this change is an ORDERING fix."""
    env([_r(child="session_01CUYirsUYqbaxCWGsX3iYMq")], cap=2)
    may, code, why = SC._verdict()
    assert not may and code == SC.MUST_NOT_STOP
    assert "has not yet done the work" in why


def test_another_sessions_handoff_is_not_mine(env):
    env([_r(sid="sess-bbbb2222", child="session_01X"), _r(sid="sess-bbbb2222", child="session_01X")],
        sid="sess-aaaa1111")
    assert not SC._verdict()[0]


def test_an_unreadable_cap_or_session_id_still_buys_nothing(env, monkeypatch, tmp_path):
    env([_r(), _r(child="session_01CUYirsUYqbaxCWGsX3iYMq")])
    monkeypatch.setattr(SC, "STATE", str(tmp_path / "gone.json"))
    assert not SC._verdict()[0]
    env([_r(), _r(child="session_01CUYirsUYqbaxCWGsX3iYMq")])
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    assert not SC._verdict()[0]


# =================================================================================================
# 4 · THE READER/WRITER CONTRACT — a code agreed in prose between two files is not agreed at all
# =================================================================================================

def _hook_body():
    with open(HOOK, encoding="utf-8") as fh:
        return fh.read()


def test_every_reason_code_the_hook_branches_on_is_one_session_cap_can_emit():
    """⛔ DIRECTION ONE (AUT-PD-017). The hook greps `[HANDED-OFF]`; if that literal ever stopped
    being emitted, the hook would silently print the wrong guidance forever."""
    body = _hook_body()
    branched = {c for c in SC.CODES if f"[{c}]" in body}
    assert branched, "the hook branches on no reason code at all — the contract is not wired"
    for code in branched:
        assert code in SC.CODES


def test_the_hook_does_not_branch_on_a_code_that_does_not_exist():
    """⛔ DIRECTION TWO, and it is the one that catches a rename. Any `[FOO]` the hook tests for
    must be a code this module actually emits."""
    import re
    body = _hook_body()
    tested = set(re.findall(r'capline"?\s*==\s*\*"\[([A-Z-]+)\]"\*', body))
    assert tested, "no bracketed code is tested in the hook — this assertion is measuring nothing"
    unknown = tested - set(SC.CODES)
    assert not unknown, f"the hook branches on code(s) session_cap.py never emits: {sorted(unknown)}"


def test_the_check_line_carries_the_code_the_hook_reads(env):
    """★ END TO END, THROUGH THE ACTUAL CLI, because the hook reads stdout and not a function."""
    env([_r(), _r(child="session_01CUYirsUYqbaxCWGsX3iYMq")])
    from io import StringIO
    import contextlib
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        rc = SC.main(["--check"])
    line = buf.getvalue().strip()
    assert rc == 0
    assert line.startswith("MAY STOP [HANDED-OFF] — "), line


def test_the_hook_is_valid_shell_after_the_split():
    """⚠ A HOOK THAT DOES NOT PARSE IS A HOOK THAT NEVER FIRES, and it fails silently — the
    unreachable-guard trap this repository has hit three times in one day."""
    proc = subprocess.run(["bash", "-n", HOOK], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


def test_option_one_tells_a_spawned_session_apart_from_a_subagent():
    """⛔ THE WORDING IS THE OTHER HALF OF THE FIX AND IT IS THE HALF THAT BINDS WHEN THE VERDICT
    BRANCH IS NOT REACHED — a session that spawns a SIBLING worker rather than a successor still
    lands in the loud branch, and must still not pre-claim for it."""
    body = _hook_body()
    live = "\n".join(ln for ln in body.split("\n") if not ln.lstrip().startswith("#"))
    assert "1a." in live and "1b." in live, "option 1 was not split"
    assert "DO NOT CLAIM" in live, "the spawned-session half does not say not to claim"
    assert "handoff.child_session_id" in live, (
        "the spawned-session half names no falsifiable alternative to a lease, which is what made "
        "the original instruction the only available answer")
