#!/usr/bin/env python3
"""May this session stop? — the fourth answer the turn-end hook did not have.

⛔⛔ WHY THIS EXISTS, MEASURED 2026-08-28. `.claude/hooks/ready-work-at-turn-end.sh` accepted exactly
three answers at a turn end: something is running, something is blocked on a human, or START ONE —
with "⛔ A SCHEDULED ROUTINE IS NOT AN ANSWER" written into it. That sentence is right for the case
it was written for and catastrophic for the case it was not.

A session fired by the driver Routine, which has ALREADY run its cycle and CANNOT hand off, has no
legal answer under those three. The only move that satisfies the hook is to start another cycle in
the same context. Measured that morning: **CYC-0033 … CYC-0041, nine cycles, one session**, every
receipt recording `handoff.attempted: false` and `child_session_id: null`, and one of them naming
the cause in its own `shape` field — *"the ready-work-at-turn-end stop hook fired a third time
insisting on something running or claimed"*. The cap is `max_cycles_per_session` = 2. It ran nine.

⭐ AND THE LOOP DOES NOT NEED THE HANDOFF TO SURVIVE, WHICH IS THE WHOLE INSIGHT. The driver Routine
fires on `13 */4 * * *`. A session that runs its cycles and stops is not a stall — **the cron IS the
successor**. Handoff exists to make the next cycle start sooner than four hours, not to make it
happen at all. So "the Routine will fire" is a deferral when the session could still work, and is
the CORRECT terminal state when it cannot.

⛔ WHY HANDOFF FAILS IS ALREADY MEASURED AND IS NOT THIS SESSION'S FAULT (AUT-PD-032): `create_session`
refuses at a lineage depth limit — *"caller session is at lineage depth 8 (limit 8); cannot spawn or
re-arm further child sessions"* — so the longer the loop runs unattended the more certainly the
handoff fails, and the last generation is the one instructed most emphatically to do the impossible.
`health.py:c_cycles_are_sized` already grades this correctly and downgrades to UNMEASURED rather than
green. **It reports; the hook DRIVES.** This module puts the same rule where it changes behaviour.

★★ THE ANTI-GAMING HALF, AND IT IS THE REASON THIS IS A MODULE AND NOT A FLAG. "I may stop" must be
EARNED and FALSIFIABLE, never claimable by a session that simply did not try:

    1. this session must have WRITTEN AT LEAST `cap` RECEIPTS — it did the work it is capped for;
    2. its most recent receipt must record a handoff that was ATTEMPTED AND BLOCKED, in the
       platform's own words (`handoff.refused_by`) or as an explicitly named absent mechanism
       (`handoff.mechanism_unavailable`), non-empty either way;
    3. that receipt must carry NO `child_session_id` — a session that DID hand off is not blocked,
       and the ordinary path already covers it.

⛔ An ABSENT record is not a blocked handoff. It is a session that did not try, and it stays red —
the same rule `handoff.refusal_of` states, for the same reason: otherwise "I could not" becomes a
free pass. Presence is never evidence of provenance (CLAUDE.md §4).

⚠ UNKNOWN, AND IT IS THE ONE THAT DECIDES WHETHER THIS HELPS THE SESSIONS IT WAS WRITTEN FOR.
`CLAUDE_CODE_SESSION_ID` is set in an INTERACTIVE session — verified here, not assumed. Whether it is
set inside a scheduled-Routine session has NOT been verified, and cannot be from an interactive one.
If it is unset there, `verdict()` answers MUST NOT STOP and those sessions keep running cycles
exactly as before: the fix would be inert rather than wrong, which is the safe direction and the
reason the unreadable branch fails that way. **The next scheduled cycle settles it** — its receipt
either carries a real id or it does not, and `mine()` is what reads the answer. Do not record this
as fixed for the scheduled path until a receipt written by one shows a real session id.

USAGE
    python3 research/autonomy/session_cap.py --check     # exit 0 = may stop, 1 = must not
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import envread  # noqa: E402
import handoff  # noqa: E402

RECEIPTS = os.path.join(HERE, "receipts")
STATE = os.path.join(HERE, "autonomy-state.json")

#: The receipt field naming a mechanism that is absent rather than refused. A refusal quotes the
#: platform; this names what could not be reached. Both must be non-empty strings.
#: ⛔ RE-EXPORTED, NOT RE-SPELLED (AUT-PD-059 tightening AUT-PD-017). This module used to declare the
#: literal here AND hand-roll `block.get("mechanism_unavailable")` below, while `handoff.py` owned
#: every other handoff field — the same two-readers-agreeing-in-prose shape AUT-PD-017 fixed for
#: `child_session_id`, one field later. `handoff.py` now owns the name and the read; this is an alias
#: so nothing importing `session_cap.UNAVAILABLE_FIELD` breaks.
UNAVAILABLE_FIELD = handoff.UNAVAILABLE_FIELD

#: ⛔ The literal a scheduled session wrote instead of its real id, so nine sessions' receipts were
#: indistinguishable from one session's. Treated as NO id: an unreadable session id must never let a
#: session claim it is at its cap, because "at cap" is exactly the claim it would buy.
PLACEHOLDER_IDS = {"scheduled-routine-session", "unknown", "", None}

#: ⛔⛔ THE MACHINE HALF OF `--check`'s ANSWER (AUT-PD-169). The turn-end hook must print DIFFERENT
#: guidance for the two ways a session may stop — one has a successor running and one does not — and
#: it must not tell them apart by grepping a sentence somebody may reword. That is AUT-PD-017's
#: finding exactly ("a field name agreed in prose between two readers is not agreed at all"), and
#: this repository has lost that agreement four separate times. `--check` prints
#: `MAY STOP [<code>] — <why>`; `test_a_session_that_handed_off_is_not_a_session_that_did_not_try.py`
#: asserts, in BOTH directions, that every code the hook branches on is one this module emits.
HANDED_OFF = "HANDED-OFF"
HANDOFF_BLOCKED = "HANDOFF-BLOCKED"
MUST_NOT_STOP = "MUST-NOT-STOP"
CODES = (HANDED_OFF, HANDOFF_BLOCKED, MUST_NOT_STOP)


def cap() -> int | None:
    """`max_cycles_per_session`, READ rather than remembered. None when unreadable — and unreadable
    buys nothing, the same direction `continuity.width_cap` fails."""
    try:
        with open(STATE, encoding="utf-8") as fh:
            v = json.load(fh).get("max_cycles_per_session")
    except (OSError, ValueError):
        return None
    return v if isinstance(v, int) and not isinstance(v, bool) and v >= 1 else None


def session_id_read():
    """The three-valued read behind `session_id()` — AUT-PROP-034, and it answers a question this
    module's own docstring records as OPEN.

    ⛔ THE DECISION DOES NOT CHANGE, AND THAT IS DELIBERATE. `verdict()` already fails closed on both
    branches (`MUST NOT STOP`), which is why the two-valued read was not a defect here the way it is
    in `gates_verdict.py`. What changes is the REPORT, and the report is the whole reason to bother:
    the module docstring above says *"Whether `CLAUDE_CODE_SESSION_ID` is set inside a
    scheduled-Routine session has NOT been verified, and cannot be from an interactive one"*, and
    `os.environ.get(X) or ""` cannot tell **unset** (no harness variable at all — the open question)
    from **exported empty** (a harness that set it to nothing — a different bug in a different
    place). Collapsing them leaves the next reader of a scheduled session's output unable to settle
    the very question this module is waiting on.
    """
    return envread.read("CLAUDE_CODE_SESSION_ID", default=None,
                        what="which receipts belong to this session")


def session_id() -> str | None:
    return session_id_read().value or None


def _receipts() -> list[dict]:
    out = []
    for p in sorted(glob.glob(os.path.join(RECEIPTS, "*.json"))):
        try:
            with open(p, encoding="utf-8") as fh:
                r = json.load(fh)
        except (OSError, ValueError):
            continue
        if isinstance(r, dict):
            out.append(r)
    return out


def mine(sid: str, receipts: list[dict] | None = None) -> list[dict]:
    """Receipts this session wrote. A placeholder id matches nothing — see PLACEHOLDER_IDS."""
    if sid in PLACEHOLDER_IDS:
        return []
    out = []
    for r in receipts if receipts is not None else _receipts():
        got = r.get("session_id")
        if not isinstance(got, str) or got.strip() in PLACEHOLDER_IDS:
            continue
        # The receipt may carry the full id or the 8-char discriminator the cycle_id uses.
        got = got.strip()
        if got == sid or sid.startswith(got) or got.startswith(sid[:8]):
            out.append(r)
    return out


def blocked_handoff(receipt: dict) -> str | None:
    """The recorded reason this session could not hand off, or None.

    ⛔ A receipt that HANDED OFF is not blocked — `child_session_id` present means the ordinary path
    applies and this module has nothing to say.
    """
    if handoff.child_session_id_of(receipt):
        return None
    return handoff.refusal_of(receipt) or handoff.mechanism_unavailable_of(receipt)


def handed_off(receipt: dict, sid: str) -> str | None:
    """The successor session THIS session created, or None.

    ⛔⛔ AUT-PD-169, AND ITS ABSENCE IS WHAT MADE THE TURN-END HOOK INSTRUCT A LOGICAL IMPOSSIBILITY.
    `verdict()` used to reach a session that had done exactly what `research-loop` §3 demands — built
    the prompt with `handoff.py`, called `create_session`, recorded the child — and answer *"the
    latest receipt records no handoff attempt — an absent record is a session that did not try"*.
    Not a wording slip: `blocked_handoff()` deliberately returns None for a receipt carrying a child
    id, and NOTHING ELSE READ THAT FIELD. So the one success the contract asks for scored identically
    to never having tried, `--check` said MUST NOT STOP, and the hook fell through to its loud branch.

    ⛔ WHAT THE LOUD BRANCH THEN TELLS THE SESSION TO DO IS THE DEFECT. Its option 1 says to CLAIM
    THE ROW FOR THE WORKER THAT IS RUNNING IT. A spawned successor is not that kind of worker: it
    runs the twelve-step contract and claims for ITSELF at step 4, under a cycle id
    `CYC-NNNN-<discriminator(its own harness session uuid)>` — a uuid the control plane assigns
    inside the child's container and never returns to `create_session`'s caller. `claim.decide()`
    answers `YIELDED` for any `owner` that is set and is not the caller's own `me`, so **no owner
    string the parent is able to write can ever match**, and obeying the hook guarantees the
    successor hands back the one row it was created for — leaving that row leased to a session that
    has ended until `priority.release_stale_claims` ages it out.

    ⭐ WHY THIS FIELD AND NOT THE NEW ONE THE ROW PROPOSED. AUT-PD-169's preferred option (b) was a
    `dispatched_to` ledger field distinct from `owner`. It is not needed: the falsifiable record
    already exists and is already REQUIRED — `handoff.child_session_id` is what
    `health.py:cycles_are_sized` grades an over-cap session on, and only a real `create_session`
    produces it. A new ledger field would also need ageing (the row says so itself), and a field
    nothing ages out is CYC-0003's immortal claim with a new name; it would also need a ledger write
    at the one moment a handoff cannot make one (AUT-PD-174).

    ⛔ A SESSION MAY NOT NAME ITSELF AS ITS OWN SUCCESSOR — AUT-PD-140's shape, one field over. A
    self-referential record names no other worker, so it would buy a stop for work nobody is doing.
    Both id spaces are checked, because the receipt carries both (`session_id` is the harness uuid,
    `ccr_session_id` the `session_01…` id the session list speaks) and only one of them would be the
    obvious thing to type.
    """
    child = handoff.child_session_id_of(receipt)
    if not child:
        return None
    own = {str(sid).strip(), str(receipt.get("ccr_session_id") or "").strip(),
           str(receipt.get("session_id") or "").strip()}
    if child.strip() in own:
        return None
    return child


def _verdict() -> tuple[bool, str, str]:
    """(may_stop, reason code, one-line reason). False is the safe direction and every unreadable
    input takes it."""
    c = cap()
    if c is None:
        return False, MUST_NOT_STOP, "max_cycles_per_session is unreadable, so no cap can be claimed"
    sid_read = session_id_read()
    if not sid_read.value:
        # ⚠ ONE DECISION, TWO REPORTS. `sid_read.detail` distinguishes "unset" from "exported empty";
        # the answer is MUST NOT STOP either way, and it always was.
        return False, MUST_NOT_STOP, (
            f"no usable session id, so this session cannot show which receipts are its "
            f"own — {sid_read.detail}")
    sid = sid_read.value
    ours = mine(sid)
    if len(ours) < c:
        return False, MUST_NOT_STOP, (
            f"this session has written {len(ours)} receipt(s) against a cap of {c} — "
            f"it has not yet done the work the cap is for")
    # ⛔ CHECKED BEFORE THE BLOCKED BRANCH, BECAUSE A SESSION THAT HANDED OFF IS NOT A BLOCKED ONE
    # and `blocked_handoff()` returns None for it BY DESIGN. Order is the whole fix: without this
    # line the success falls through to the "did not try" refusal below.
    child = handed_off(ours[-1], sid)
    if child:
        return True, HANDED_OFF, (
            f"{len(ours)} receipt(s) at a cap of {c}, and this session HANDED OFF: its latest "
            f"receipt records successor {child} under `{handoff.CHILD_ID_FIELD}`, which only a real "
            f"create_session produces. The work continues in a fresh context.")
    why = blocked_handoff(ours[-1])
    if not why:
        return False, MUST_NOT_STOP, (
            f"{len(ours)} receipt(s) written and the cap is {c}, but the latest receipt "
            f"records no handoff attempt — an absent record is a session that did not try")
    return True, HANDOFF_BLOCKED, (
        f"{len(ours)} receipt(s) at a cap of {c}, and the handoff was attempted and "
        f"blocked: {why}")


def verdict() -> tuple[bool, str]:
    """(may_stop, one-line reason) — the two-valued face `_verdict` wraps, kept for every caller
    that does not branch on WHICH stop this is."""
    may, _code, why = _verdict()
    return may, why


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 0 if this session may stop")
    args = ap.parse_args(argv)
    may, code, why = _verdict()
    if args.check:
        # ⛔ THE CODE IS IN BRACKETS AND IT IS PART OF THE CONTRACT, NOT DECORATION. The hook reads
        # this line and prints different guidance for HANDED-OFF than for HANDOFF-BLOCKED; a test
        # asserts both directions of that agreement.
        print(("MAY STOP" if may else "MUST NOT STOP") + f" [{code}] — " + why)
        return 0 if may else 1
    print(json.dumps({"may_stop": may, "reason_code": code, "why": why, "cap": cap(),
                      "session_id": session_id()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
