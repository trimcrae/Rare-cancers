#!/usr/bin/env python3
"""IF THIS SESSION STOPPED RIGHT NOW, WOULD THE WORK CONTINUE? ($0, stdlib)

⛔⛔ WHY THIS EXISTS. trimcrae, 2026-08-27: "What's the mechanism that lets you say 'in flight:
nothing running' and end a turn? We want this to continue autonomously so we should fix that."

★ THE ANSWER, AND IT IS A REAL HOLE RATHER THAN A SLIP. The in-flight board reports RUNNING COMPUTE,
and `inflight-reporting` explicitly forbids listing wake mechanisms or scheduled Routines on it. So
"Nothing in flight" is a true statement about GPUs and CI, and says NOTHING about whether the work
resumes. A session could hold three pieces of unfinished work, report "nothing in flight", end, and
be perfectly compliant with every rule in the repository while the work died with the turn.

⚠ MEASURED THE SAME DAY, WHICH IS WHY THIS IS A FILE AND NOT A NOTE. PUB-ASO's bar read 4/7 with
three clauses open. NONE of the three was a ledger item — they existed only as sentences in a reply.
A fresh cycle re-scores the ledger and would have found nothing about them, so the entire "next, I'll
close these" plan was one session-death away from being lost, and the loop would have carried on
looking healthy: cycles firing, receipts landing, and the one paper with a public DOI parked forever.

★★ THE INVARIANT THIS CHECKS: **every blocking clause on a paper the loop intends to advance must be
a QUEUED LEDGER ITEM.** The ledger is the only thing a fresh session reads. Work that is not in it is
work that exists in a context window, and a context window is not a durable medium.

⛔ WHAT THIS DOES NOT DO: it does not verify that anything will actually run. That is the driver
Routine's job, and a cycle cannot inspect its own scheduler reliably (§7 — the loop has no control
over the UI-created Routine). It checks the half that IS checkable from the repository: whether the
work has been written down where the next cycle looks.

Usage:
  python3 research/autonomy/continuity.py            # report
  python3 research/autonomy/continuity.py --check    # exit 1 if in-hand work is unrecorded
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
LEDGER = os.path.join(HERE, "research-ledger.json")
QUEUE = os.path.join(HERE, "ready-to-post.json")

#: A clause is "covered" when a queued ledger item names it. ⚠ Matched on the clause NAME, which is
#: the identifier publish_bar emits — not on prose about it, because a row that merely mentions a
#: clause in passing is not a plan to close it.
def _clauses_the_ledger_is_closing() -> set[tuple[str, str]]:
    """(paper, clause) pairs that a QUEUED item explicitly declares it closes.

    ⛔ MATCHED ON A STRUCTURED FIELD, NOT ON PROSE, AND THE FIRST VERSION DID THE WRONG ONE.
    It grepped the item's text for the clause name; the three items filed minutes earlier said
    "publish_bar CLAUSE 2" while the clause is named `preflight_full_green`, so the check reported
    all three as unrecorded when all three were filed. ⚠ That direction is the safe one — it
    over-reported work as lost rather than under-reporting it — but a check that cries wolf is a
    check that gets ignored, and "the item mentions the word somewhere" was never the property
    worth testing. A row now declares what it closes, or it does not count.
    """
    with open(LEDGER, encoding="utf-8") as fh:
        d = json.load(fh)
    out: set[tuple[str, str]] = set()
    for e in d["entries"]:
        if e.get("state") not in (None, "queued", "in_progress"):
            continue
        c = e.get("closes_clause")
        if isinstance(c, dict) and c.get("paper") and c.get("clause"):
            out.add((c["paper"], c["clause"]))
    return out


def audit() -> dict:
    if not os.path.exists(QUEUE):
        return {"papers": {}, "note": "no ready-to-post queue yet — run ready_to_post.py --write"}
    with open(QUEUE, encoding="utf-8") as fh:
        waiting = json.load(fh).get("waiting", {})
    closing = _clauses_the_ledger_is_closing()
    out: dict[str, dict] = {}
    for pid, v in waiting.items():
        blocking = v.get("blocking_clauses") or []
        uncovered = [c for c in blocking if (pid, c) not in closing]
        out[pid] = {
            "state": v.get("state"),
            "blocking": blocking,
            "uncovered_by_the_ledger": uncovered,
            "act": v.get("what_he_does"),
        }
    return {"papers": out}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any blocking clause has no queued ledger item")
    args = ap.parse_args(argv)

    a = audit()
    if a.get("note"):
        print(a["note"])
        return 0

    bad = False
    for pid, v in sorted(a["papers"].items()):
        if v["state"] == "READY":
            print(f"✅ {pid}: READY — the remaining act is trimcrae's ({v['act']})")
            continue
        print(f"   {pid}: {v['state']}, blocked on {len(v['blocking'])} clause(s)")
        for c in v["blocking"]:
            covered = c not in v["uncovered_by_the_ledger"]
            print(f"      {'✅' if covered else '⛔'} {c}"
                  f"{'' if covered else '   ← NO QUEUED LEDGER ITEM CLOSES THIS'}")
        if v["uncovered_by_the_ledger"]:
            bad = True

    if bad:
        print("\n⛔ CONTINUITY FAILURE: a clause is blocking a paper and nothing in the ledger closes "
              "it.\n   If this session ends now, that work exists only in a context window and the "
              "next\n   cycle will not find it. File it before you end the turn — a reply is not a "
              "queue.")
        return 1
    print("\n✅ every blocking clause has a queued ledger item; the work survives this session.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
