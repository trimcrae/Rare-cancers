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
UNAVAILABLE_FIELD = "handoff.mechanism_unavailable"

#: ⛔ The literal a scheduled session wrote instead of its real id, so nine sessions' receipts were
#: indistinguishable from one session's. Treated as NO id: an unreadable session id must never let a
#: session claim it is at its cap, because "at cap" is exactly the claim it would buy.
PLACEHOLDER_IDS = {"scheduled-routine-session", "unknown", "", None}


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
    refused = handoff.refusal_of(receipt)
    if refused:
        return refused
    block = receipt.get("handoff")
    if isinstance(block, dict):
        v = block.get("mechanism_unavailable")
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def verdict() -> tuple[bool, str]:
    """(may_stop, one-line reason). False is the safe direction and every unreadable input takes it."""
    c = cap()
    if c is None:
        return False, "max_cycles_per_session is unreadable, so no cap can be claimed"
    sid_read = session_id_read()
    if not sid_read.value:
        # ⚠ ONE DECISION, TWO REPORTS. `sid_read.detail` distinguishes "unset" from "exported empty";
        # the answer is MUST NOT STOP either way, and it always was.
        return False, (f"no usable session id, so this session cannot show which receipts are its "
                       f"own — {sid_read.detail}")
    sid = sid_read.value
    ours = mine(sid)
    if len(ours) < c:
        return False, (f"this session has written {len(ours)} receipt(s) against a cap of {c} — "
                       f"it has not yet done the work the cap is for")
    why = blocked_handoff(ours[-1])
    if not why:
        return False, (f"{len(ours)} receipt(s) written and the cap is {c}, but the latest receipt "
                       f"records no handoff attempt — an absent record is a session that did not try")
    return True, (f"{len(ours)} receipt(s) at a cap of {c}, and the handoff was attempted and "
                  f"blocked: {why}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 0 if this session may stop")
    args = ap.parse_args(argv)
    may, why = verdict()
    if args.check:
        print(("MAY STOP — " if may else "MUST NOT STOP — ") + why)
        return 0 if may else 1
    print(json.dumps({"may_stop": may, "why": why, "cap": cap(), "session_id": session_id()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
