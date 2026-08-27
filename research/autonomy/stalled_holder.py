#!/usr/bin/env python3
"""IS A LEDGER ITEM PARKED BY A WORKER THAT HAS STOPPED MOVING?

⛔⛔ MEASURED 2026-08-27, AND trimcrae FOUND IT BEFORE THE LOOP DID. A seat was dispatched, died on
its FIRST message, and `ListAgents` reported it `running` for 2 h 36 m. The driver relayed that
status as "in flight" seven times and held its claim on AUT-PROP-012 open the whole time. The seat's
entire output was: *"I'll start by reading the ledger entry and the relevant files."*

★ THE ERROR WAS ASKING THE WRONG QUESTION. `ListAgents` answers "is this agent alive?" — a LIVENESS
PING. A status field cannot tell a seat thinking hard from a seat that stopped existing. CLAUDE.md §4
already says an unproven pipeline gets PROGRESS checks, not liveness pings, and that "no error yet"
is not progress.

⭐ THE SHAPE IS BORROWED, NOT INVENTED, and reading the prior art first would have saved the build.
`research/method-watch-autonomy-prior-art.md` — written in this repository the same day and not read
until after the stall — ranks ARIS (15,294★, MIT) and names its two relevant mechanisms:
`tools/watchdog.py`, a SEPARATE process that checks whether an unattended loop "is still updating its
state file and writes an alert when it goes quiet" (filesystem writes, not pings), and
`tools/iteration_log.py`, where **two empty rounds force a change of direction and four call in a
human**. Its watchdog "only reports the problem, never restarts a verdict-bearing run".

⭐⭐ WHAT THIS CHANGES FROM A NAIVE PORT: the signal is not "which agents are alive" — that needs
`ListAgents`, which a hook cannot call, and which is the field that lied. It is the JOIN of two things
already observable from disk: **a ledger row with an open claim, whose holder's transcript has stopped
growing.** That names the actual harm — an item parked for every other worker — rather than the
symptom, and it needs no status field at all.

⛔ IT REPORTS AND NEVER ACTS, which is ARIS's own rule and the right one: a long single tool call is
legitimately silent (a modalities suite is ~20 minutes), so this is a prompt to LOOK. Killing a seat
and releasing its lease is a judgement, and a judgement made by a watchdog is how live work gets
thrown away.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "research-ledger.json")

#: Quiet longer than this is worth a look. The modalities suite is ~20 min and moves nothing while it
#: runs, so 25 clears the longest honest silence this repository produces. Below that a seat is
#: probably just working, and a watchdog that cries wolf is one that gets tuned out.
STALL_MINUTES = 25

OPEN_STATES = {None, "queued", "in_progress"}


def open_claims(ledger_path: str = LEDGER):
    """`[(entry_id, owner)]` for every item a worker currently holds."""
    try:
        with open(ledger_path, encoding="utf-8") as fh:
            entries = json.load(fh).get("entries", [])
    except (OSError, ValueError):
        return []
    return [(e.get("id"), e.get("owner")) for e in entries
            if e.get("state") in OPEN_STATES and e.get("owner")]


def quiet_minutes(tasks_dir: str):
    """`{agent_id: minutes since its transcript last grew}` for every transcript on disk."""
    out = {}
    if not os.path.isdir(tasks_dir):
        return out
    now = time.time()
    for name in os.listdir(tasks_dir):
        if name.endswith(".output"):
            try:
                out[name[:-len(".output")]] = (now - os.path.getmtime(name and
                                                os.path.join(tasks_dir, name))) / 60.0
            except OSError:
                pass
    return out


def stalled(tasks_dir: str, ledger_path: str = LEDGER, threshold: float = STALL_MINUTES):
    """`[(entry_id, owner, minutes_quiet)]` — claims whose holder has a frozen transcript.

    ⚠ A holder with NO transcript is NOT reported. Most owners are not subagents at all: a cycle id
    holds items across sessions, and reporting those every turn is the cry-wolf failure that gets a
    guard muted. Only a holder this session can actually observe going quiet is a finding.
    """
    ages = quiet_minutes(tasks_dir)
    out = []
    for entry_id, owner in open_claims(ledger_path):
        age = ages.get(owner)
        if age is not None and age >= threshold:
            out.append((entry_id, owner, age))
    return sorted(out, key=lambda t: -t[2])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tasks-dir", required=True)
    ap.add_argument("--ledger", default=LEDGER)
    ap.add_argument("--stall-minutes", type=float, default=STALL_MINUTES)
    ap.add_argument("--check", action="store_true", help="exit 1 if any claim has a frozen holder")
    a = ap.parse_args(argv)

    rows = stalled(a.tasks_dir, a.ledger, a.stall_minutes)
    for entry_id, owner, age in rows:
        print(f"   ⛔ {entry_id} is held by {owner}, whose transcript has not grown for "
              f"{age:.0f} min")
    if rows:
        print("   ⚠ That is a prompt to LOOK, not a verdict — one long tool call is legitimately "
              "silent. But `running` from ListAgents cannot tell you which: it reports whether the "
              "agent is ALIVE, and a seat that died on its first message stays `running` forever.")
        print("   ⭐ If it is dead: stop it, RELEASE THE CLAIM (`owner: null`), and say so. A dead "
              "holder parks the item for every other worker — measured 2026-08-27 at 2 h 36 m.")
    return 1 if (a.check and rows) else 0


if __name__ == "__main__":
    sys.exit(main())
