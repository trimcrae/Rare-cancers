#!/usr/bin/env python3
"""Build the prompt for a SUCCESSOR session, from committed state rather than from memory.

⛔⛔ THE GAP THIS CLOSES WAS IN THE ORIGINAL GOAL AND STAYED OPEN FOR A DAY. trimcrae's founding
brief asked for "proper usage of new session creation to manage context"; `research-loop` §3 then
said a full hardening cycle is a SPAWNED SESSION; `health.py`'s `cycles_are_sized` measured when a
session had run too long. Three layers of knowing, and **nothing that actually spawned anything**.
The session that hit the cap wrote "the next cycle should be a fresh session" in its final message
and stopped — a manual step, parked in the middle of a loop whose whole purpose is that no manual
step exists. trimcrae, 2026-08-27: *"You've flagged that a new session needs to start which is
correct. But then you stopped there. We should be automating the creation of new sessions."*

★ WHY THE PROMPT IS GENERATED AND NOT TYPED. A handoff written by the outgoing session is written
from ITS context — the thing that is running out and the reason for handing off at all. Anything it
remembers is exactly what it should not be trusted on. So every fact here is read from a committed
artifact at build time: the queue from `research-ledger.json`, what just happened from the newest
receipts, the posture from `autonomy-state.json`. A fresh session then reads the same files itself
and finds them unchanged, which is CLAUDE.md's "state lives in git, never in context" applied to the
one moment the context is being discarded on purpose.

⚠ AND IT DELIBERATELY CARRIES NO FINDINGS, NO CONCLUSIONS AND NO "WHAT I WAS THINKING". A successor
that inherits the predecessor's reasoning inherits its mistakes with it, and this repository has
already had a wrong seat finding propagate through two cycles because it was passed along as a
summary rather than re-derived. The successor is told WHERE TO LOOK, never WHAT IT WILL FIND.

Usage:
    python3 research/autonomy/handoff.py                  # print the prompt
    python3 research/autonomy/handoff.py --json           # prompt + title, for create_session
    python3 research/autonomy/handoff.py --reason "..."   # why the handoff is happening

⚠ THIS MODULE DOES NOT SPAWN ANYTHING. Creating a session is an MCP call, available to the agent and
not to a script; keeping the DETERMINISTIC half here means the part that can be tested is tested, and
the part that cannot be is one tool call with no judgement left in it.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
LEDGER = HERE / "research-ledger.json"
STATE = HERE / "autonomy-state.json"
RECEIPTS = HERE / "receipts"

#: How many queued items the successor is handed. Enough to choose from; not so many that the prompt
#: becomes a plan the successor follows instead of re-scoring the queue itself, which is step 2 of
#: its own contract.
TOP_N = 5

#: How many recent receipts to name. The successor READS them; they are not summarised here.
RECENT_N = 3


def _read(path: pathlib.Path):
    try:
        return json.loads(path.read_text()), None
    except Exception as exc:                                  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


def top_items(ledger: dict | None, n: int = TOP_N) -> list[dict]:
    """The highest-scoring TAKEABLE entries — the same predicate `queue_is_takeable` uses.

    ⚠ Takeable, not merely high-scoring: handing a successor an item that is owned, blocked or out of
    retry budget wastes its first act on discovering that, which is the cost the ledger exists to
    remove.
    """
    entries = (ledger or {}).get("entries") or []
    takeable = [e for e in entries
                if not e.get("owner")
                and str(e.get("state") or "queued") in {"queued", "blocked"}
                and int(e.get("retry_budget") or 0) > 0
                and e.get("score") is not None]
    return sorted(takeable, key=lambda e: -float(e.get("score") or 0))[:n]


def recent_receipts(n: int = RECENT_N) -> list[str]:
    try:
        return sorted(p.name for p in RECEIPTS.glob("*.json"))[-n:]
    except Exception:                                          # noqa: BLE001
        return []


def build(reason: str = "", ledger=None, state=None) -> str:
    """The successor's prompt. Standalone: a fresh session knows nothing about this one."""
    if ledger is None:
        ledger, _ = _read(LEDGER)
    if state is None:
        state, _ = _read(STATE)

    items = top_items(ledger)
    queue = "\n".join(
        f"  {e['id']}  score {e.get('score')}  [{e.get('kind')}]  {str(e.get('what') or '')[:150]}"
        for e in items) or "  (the ledger holds nothing takeable — that is itself the finding; see below)"

    interval = (state or {}).get("cycle_interval_hours", "?")
    backoff = (state or {}).get("backoff_level", "?")
    width = (state or {}).get("subagent_width", "?")
    cap = (state or {}).get("max_cycles_per_session", "?")

    return f"""Run the next cycle of the autonomous EMC research loop. You are a FRESH SESSION,
started deliberately so that this cycle gets a clean context.

WHY YOU EXIST: {reason or "the previous session reached its cycle cap (research-loop §3)."}

Confirm you have the repository before anything else:

    git -C . rev-parse --abbrev-ref HEAD && git pull --rebase -q origin main

⛔ IF THAT FAILS, SAY SO LOUDLY AS THE FIRST LINE OF YOUR FINAL MESSAGE AND STOP. Do not improvise
around it and do not clone. A session without the repo is the failure that ran every Friday for six
weeks delivering nothing.

Then load the cycle contract and follow it — do not work from this prompt alone:

    the `research-loop` skill, or if you have no Skill tool:  cat .claude/skills/research-loop/SKILL.md

⭐ WHAT IS WAITING, read from the committed ledger when this prompt was built. RE-SCORE IT YOURSELF
(`python3 research/autonomy/priority.py --write`) rather than trusting this list — it is a pointer,
not a plan:

{queue}

Posture at handoff, from autonomy-state.json: cycle interval {interval} h, backoff level {backoff},
subagent width {width} (CONCURRENT agents — read it, do not remember it), max cycles per session {cap}.

The last few receipts are {", ".join(recent_receipts()) or "(none)"} in research/autonomy/receipts/.
⛔ READ THEM RATHER THAN ASKING ME WHAT HAPPENED. This prompt deliberately carries no findings and no
conclusions from the previous session: a successor that inherits its predecessor's reasoning inherits
its mistakes, and a wrong review finding has already propagated through two cycles here by being
passed along as a summary instead of re-derived.

⛔ AND YOU INHERIT ITS CAP TOO. You are one session; `research-loop` §3 allows {cap} cycles in it. When
you reach that, HAND OFF THE SAME WAY YOU WERE STARTED — `python3 research/autonomy/handoff.py` builds
the next prompt, and you create the successor session yourself. A loop that needs a human to start its
next session is not automated; it just has a longer fuse.

Escalate only what the skill's §5 names. Everything else is silent. Your final message is short: what
you took, what changed, and `route_advanced`."""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reason", default="", help="why the handoff is happening")
    ap.add_argument("--json", action="store_true", help="emit {title, prompt} for create_session")
    a = ap.parse_args(argv)

    prompt = build(a.reason)
    if a.json:
        ledger, _ = _read(LEDGER)
        top = top_items(ledger, 1)
        focus = top[0]["id"] if top else "queue empty"
        print(json.dumps({"title": f"EMC research loop — cycle ({focus})", "prompt": prompt},
                         indent=2, ensure_ascii=False))
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
