#!/usr/bin/env python3
"""WHAT IS READY TO RUN RIGHT NOW? ($0, stdlib)

⛔⛔ THIS FILE WAS REWRITTEN 2026-08-27 BECAUSE ITS FIRST VERSION FAILED IN PRODUCTION, and the way
it failed is the whole design of the second. trimcrae, on being shown another turn that ended with
"Nothing in flight": *"There's that ending a message with 'nothing in flight' bug again. Whatever we
tried to change to fix it last time didn't work. Let's try another approach based on that outcome."*

★ THE DIAGNOSIS. Version 1 asked **"is this work written down where the next cycle will find it?"**
That is a real question, it was worth asking, and on the turn that failed the answer was YES — every
blocking clause had a queued ledger item, and this file printed

    ✅ every blocking clause has a queued ledger item; the work survives this session.

next to a turn that then ended with three pieces of free, ready, unblocked work and nothing running.
**The check passed over the bug.** That is worse than not existing: a session looking for a reason to
stop found a green tick with a citation attached.

⛔ SO THE FAILURE WAS NOT A MISSING CHECK. IT WAS THE WRONG QUESTION.
  * DURABILITY — "will this survive if the session dies?" — is what v1 measured. Recording is
    necessary and it is NOT sufficient.
  * MOMENTUM — "is this work MOVING?" — is what was actually broken, and nothing measured it.
A perfectly recorded backlog with nothing running is precisely the reported failure, and v1 was
built to call that state healthy.

★★ THE INVERSION, AND IT IS THE ONLY THING THAT MAKES THIS VERSION DIFFERENT:
**THERE IS NO GREEN STATE THAT RECORDING CAN BUY.** v1 had one and it was spent as a permission slip.
This version never prints "the work survives". It prints WHAT IS READY TO RUN, and it exits non-zero
whenever that list is non-empty. Filing an item does not clear it — filing an item is what puts it ON
the list. The only ways to exit 0 are that every remaining item is genuinely blocked, or that the
backlog is empty.

⚠ AND IT DELIBERATELY DOES NOT TRY TO OBSERVE RUNNING WORK. A checker cannot see a subagent, a
spawned session or a dispatched workflow, and a `--what-is-running` flag would be one more
self-issued declaration to satisfy — the same shape as the failure. So this tool answers only the
half it can measure honestly, and answers it in the direction that costs something: **here is work
that is ready; if nothing is running, that is the bug.**

⛔ WHAT "READY" MEANS, and every clause is a way an item is NOT ready:
  * state is queued or in_progress (done/superseded are finished),
  * `blocked_by` is empty — a declared dependency is a real stop,
  * no OTHER worker holds a claim lease (`owner` set) — that is someone else's item,
  * `cost_class` is free or cheap — expensive work needs a human (CLAUDE.md §2).
⚠ Note what is NOT on that list: "is it recorded". Every item here is recorded by construction.

Usage:
  python3 research/autonomy/continuity.py            # the ready list, ranked
  python3 research/autonomy/continuity.py --check    # exit 1 if ANY item is ready to run now
  python3 research/autonomy/continuity.py --clauses  # v1's durability view, kept as a SUBORDINATE check
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
LEDGER = os.path.join(HERE, "research-ledger.json")
QUEUE = os.path.join(HERE, "ready-to-post.json")

#: Cost classes a session may take without asking. CLAUDE.md §2: warranted, cheap and ready -> DO IT NOW.
SELF_DOABLE_COST = {"free", "cheap", None}
#: States that still represent outstanding work.
OPEN_STATES = {None, "queued", "in_progress"}


def _entries() -> list[dict]:
    with open(LEDGER, encoding="utf-8") as fh:
        return json.load(fh)["entries"]


def _why_not_ready(e: dict, me: str | None) -> str | None:
    """None if the item is ready to run now; otherwise the reason it is not.

    ⛔ EVERY BRANCH HERE IS A REAL STOP, NOT A PREFERENCE. If a future edit adds a branch that lets an
    item off this list for any reason other than "a human or the outside world has to move first",
    that edit has rebuilt v1's permission slip.
    """
    if e.get("state") not in OPEN_STATES:
        return "finished"
    if e.get("blocked_by"):
        return f"blocked_by {e['blocked_by']}"
    owner = e.get("owner")
    if owner and owner != me:
        return f"claimed by {owner}"
    if e.get("cost_class") not in SELF_DOABLE_COST:
        return f"cost_class {e.get('cost_class')} — needs a human (CLAUDE.md §2)"
    return None


def ready(me: str | None = None) -> list[dict]:
    """Every ledger item a session could start right now, best first."""
    out = [e for e in _entries() if _why_not_ready(e, me) is None]
    out.sort(key=lambda e: (-(e.get("score") or 0), e.get("id") or ""))
    return out


def blocked() -> list[tuple[dict, str]]:
    rows = [(e, _why_not_ready(e, None)) for e in _entries()]
    return [(e, why) for e, why in rows if why and why != "finished"]


# ---------------------------------------------------------------------------------------------
# v1's question, KEPT — but demoted. It is a real check and it is not the stopping condition.
# ---------------------------------------------------------------------------------------------

def _clauses_the_ledger_is_closing() -> set[tuple[str, str]]:
    """(paper, clause) pairs a QUEUED item explicitly declares it closes.

    ⛔ MATCHED ON A STRUCTURED FIELD, NOT ON PROSE. v1's first draft grepped the item's text for the
    clause name; three items filed minutes earlier said "publish_bar CLAUSE 2" while the clause is
    named `preflight_full_green`, so it reported all three as unrecorded when all three were filed.
    That direction was the safe one — over-reporting loss rather than under-reporting it — but a
    check that cries wolf is a check that gets ignored.
    """
    out: set[tuple[str, str]] = set()
    for e in _entries():
        if e.get("state") not in OPEN_STATES:
            continue
        c = e.get("closes_clause")
        if isinstance(c, dict) and c.get("paper") and c.get("clause"):
            out.add((c["paper"], c["clause"]))
    return out


def clause_audit() -> dict:
    if not os.path.exists(QUEUE):
        return {"papers": {}, "note": "no ready-to-post queue yet — run ready_to_post.py --write"}
    with open(QUEUE, encoding="utf-8") as fh:
        waiting = json.load(fh).get("waiting", {})
    closing = _clauses_the_ledger_is_closing()
    out: dict[str, dict] = {}
    for pid, v in waiting.items():
        blocking = v.get("blocking_clauses") or []
        out[pid] = {
            "state": v.get("state"),
            "blocking": blocking,
            "uncovered_by_the_ledger": [c for c in blocking if (pid, c) not in closing],
            "act": v.get("what_he_does"),
        }
    return {"papers": out}


def _print_clauses() -> bool:
    a = clause_audit()
    if a.get("note"):
        print(a["note"])
        return False
    bad = False
    for pid, v in sorted(a["papers"].items()):
        if v["state"] == "READY":
            print(f"✅ {pid}: READY — the remaining act is trimcrae's ({v['act']})")
            continue
        print(f"   {pid}: {v['state']}, blocked on {len(v['blocking'])} clause(s)")
        for c in v["blocking"]:
            covered = c not in v["uncovered_by_the_ledger"]
            print(f"      {'·' if covered else '⛔'} {c}"
                  f"{'' if covered else '   ← NO QUEUED LEDGER ITEM CLOSES THIS'}")
        if v["uncovered_by_the_ledger"]:
            bad = True
    if bad:
        print("\n⛔ A clause is blocking a paper and nothing in the ledger closes it. File it — a reply\n"
              "   is not a queue. ⚠ Filing it does NOT make this session free to stop; it puts the work\n"
              "   on the ready list, which is what --check reads.")
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any ledger item is ready to run right now")
    ap.add_argument("--clauses", action="store_true",
                    help="the subordinate durability view: is every blocking clause recorded?")
    ap.add_argument("--me", metavar="CYCLE", default=None,
                    help="your cycle id, so items YOU hold a lease on still count as yours to run")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args(argv)

    if args.clauses:
        return 1 if _print_clauses() else 0

    r = ready(args.me)
    b = blocked()

    if not r:
        print(f"no ledger item is ready to run: {len(b)} open item(s), every one of them blocked.")
        for e, why in sorted(b, key=lambda t: t[0].get("id") or "")[:args.limit]:
            print(f"   {e.get('id')}  {why}")
        print("\n★ THAT is the honest empty state — not 'it is all written down'. If a row above is\n"
              "  blocked on something you could clear yourself, it is not blocked (CLAUDE.md §0:\n"
              "  \"'Blocked' is a claim that needs evidence, and it is usually wrong\").")
        return 0

    print(f"⛔ {len(r)} ledger item(s) are READY TO RUN RIGHT NOW — free, unclaimed and unblocked.\n")
    for e in r[:args.limit]:
        what = " ".join((e.get("what") or "").split())
        print(f"   [{e.get('score', 0):>6.1f}]  {e.get('id')}  {what[:150]}")
    if len(r) > args.limit:
        print(f"   … and {len(r) - args.limit} more")

    if args.check:
        print("\n⛔⛔ THIS IS NOT A FAILURE TO RECORD THE WORK. The work is recorded — that is how it\n"
              "   appears above. This exits 1 because the work is READY AND NOT MOVING.\n"
              "   ★ Ending a turn here needs one of: something actually running (a subagent, a\n"
              "     dispatched workflow, a spawned session), an item genuinely blocked on a human or\n"
              "     the outside world, or an empty list. A scheduled Routine is a BACKSTOP AGAINST\n"
              "     STALENESS and is never the answer — trimcrae, 2026-08-27: \"that's more of a backup\n"
              "     to make sure things never get stale, not a reason to intentionally stall.\"\n"
              "   ⚠ v1 of this file printed a green tick in exactly this state, because it asked\n"
              "     whether the work was WRITTEN DOWN rather than whether it was MOVING. Filing an\n"
              "     item is not progress on it.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
