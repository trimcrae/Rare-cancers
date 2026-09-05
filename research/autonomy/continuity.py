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
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
LEDGER = os.path.join(HERE, "research-ledger.json")
QUEUE = os.path.join(HERE, "ready-to-post.json")

# ⚠ sys.path, not a package import — see priority.py's identical comment; this directory is a flat
# set of scripts run as `python3 research/autonomy/<tool>.py` from the repo root.
sys.path.insert(0, HERE)
import envread  # noqa: E402 — AUT-PD-140: the session id is READ three-valued
import handoff  # noqa: E402
import priority  # noqa: E402 — AUT-PD-014: reuses priority.py's progress-aware retry-budget
import bounded_review
# arithmetic (`fruitless_attempts_count`, `DEFAULT_RETRY_BUDGET`) so this file's exclusion and
# priority.py's own `retry_budget` field can never disagree about what "budget spent" means.
#: ⛔ The governed concurrency dial lives in ONE file and is READ, never remembered — CLAUDE.md §1
#: records that `subagent_width` governed nothing for a fortnight precisely because no code read it.
STATE = os.path.join(HERE, "autonomy-state.json")

#: Cost classes a session may take without asking. CLAUDE.md §2: warranted, cheap and ready -> DO IT NOW.
SELF_DOABLE_COST = {"free", "cheap", None}

#: ⛔⛔ AN OUTWARD-FACING ACT IS FREE IN DOLLARS AND STILL NOT MINE TO DO, AND THIS TOOL DID NOT KNOW
#: THAT. Found 2026-08-27 by the Stop hook that reads this file: its top two rows were "Publish the
#: assessment…" and "Post the preprint and put the MTAP stain in front of a group…" — both reserved
#: for trimcrae by CLAUDE.md §3, both offered as ready work because readiness was modelled on SPEND
#: and never on WHO MAY ACT. The hook surfaced a correctness bug in its own input, which is the loop
#: working; it is fixed here rather than answered in a reply.
#:
#: ⛔ IT IS AN EXPLICIT FIELD, NOT A KEYWORD MATCH. A regex over the item text finds 11 candidates and
#: is wrong about at least two — AUT-058 and AUT-065 open with "⛔ Do NOT …" and the verb is
#: incidental. Guessing here would either hide real work or offer a forbidden act, and both failures
#: are silent. A row declares `requires_trimcrae: true` or it does not.
#:
#: ★ AND AN UNDECLARED ROW THAT LOOKS OUTWARD-FACING IS REPORTED, NEVER SILENTLY OFFERED. The tool
#: cannot classify it and must not pretend the question does not exist — the same reason v1's green
#: tick was worse than no check at all.
#: ⚠ TWO ALTERNATIONS, BECAUSE THE FIRST ONE ONLY SAW VERBS. Found by the Stop hook on three
#: consecutive firings: AUT-042, AUT-057 and AUT-064 are all trimcrae's under §3 and none matched.
#: They do not say "publish the …"; they say "Decide whether X is worth publishing" and "a judgement
#: call about what we publish". ★ THE SECOND CLASS IS A DECISION *ABOUT* PUBLISHING RATHER THAN AN
#: ACT OF IT, and §2 reserves it just as firmly — a genuine goal-changing decision is one of the four
#: things that halts a session. A pattern that only matches verbs cannot see a decision.
_OUTWARD_LOOKING = re.compile(
    r"\b(publish|post the|submit|deposit|e-?mail|mint (?:a )?doi|release|outreach|put .{0,40} in front of)\b"
    r"|judgement call (?:about )?what we publish"
    r"|worth publishing|worth writing(?: up)?"
    r"|decide (?:what|whether).{0,80}(?:publish|writ)",
    re.I)
#: States that still represent outstanding work.
OPEN_STATES = {None, "queued", "in_progress"}


def _entries() -> list[dict]:
    with open(LEDGER, encoding="utf-8") as fh:
        return json.load(fh)["entries"]


def _retry_budget_spent(e: dict) -> bool:
    """AUT-PD-014 — a row automation has genuinely given up on: it has been dispatched
    `DEFAULT_RETRY_BUDGET` times in a row with the evidence fingerprint never moving.

    ⛔ RECOMPUTED LIVE FROM `dispatch_log`, NEVER READ FROM THE ON-DISK `retry_budget` FIELD ALONE.
    That field is only refreshed when `priority.py --write` runs; this file reads
    `research-ledger.json` directly and must not report a row as takeable just because nobody has
    re-scored since its last dispatch. The two can never disagree for long, because both are the
    same pure function of the same `dispatch_log`.
    """
    return priority.fruitless_attempts_count(e) >= priority.DEFAULT_RETRY_BUDGET


def _why_not_ready(e: dict, me: str | None, terminal: frozenset | None = None) -> str | None:
    """None if the item is ready to run now; otherwise the reason it is not.

    ⛔ EVERY BRANCH HERE IS A REAL STOP, NOT A PREFERENCE. If a future edit adds a branch that lets an
    item off this list for any reason other than "a human or the outside world has to move first",
    that edit has rebuilt v1's permission slip.

    ⛔⛔ `terminal` (AUT-PROP-029's stuck_clock, wired in here the same way as `handoff.top_items`):
    a row `stuck_clock.py` reports `stalled_needs_human` was retried, abandoned and re-claimed for
    `STUCK_AFTER_CYCLES` cycles with the advance clock never moving — it is not ready work a session
    should start, it is a human decision (re-scope, hand off, or close). Before this, AUT-PROP-012
    sat at the top of THIS tool's own ready list for a full session after it had already gone
    terminal, because nothing here read the verdict handoff.py had just started excluding elsewhere —
    the same "two files agree in prose, disagree in code" defect this function's own history already
    names twice above. Computed ONCE by the caller and threaded through (never re-derived per row),
    since it requires a `git log` walk stuck_clock.py itself does once for the whole ledger.
    """
    if e.get("state") not in OPEN_STATES:
        return "finished"
    review = bounded_review.task_review_decision(e, repo=REPO)
    if not review["allowed"]:
        return f"bounded review ({review['action']}): {review['reason']}"
    if terminal and e.get("id") in terminal:
        return "stalled_needs_human (stuck_clock.py) — a human decision, not queued work"
    # ⛔⛔ AUT-PD-014, WIRED IN THE SAME SHAPE AS `terminal` ABOVE: a row whose progress-aware retry
    # budget is spent is not ready work — it is automation that has already tried and produced
    # nothing new `fruitless_attempts_count()` times in a row. Unlike `terminal`, this needs no git
    # history walk and is cheap enough to recompute per row rather than threading through the caller.
    if _retry_budget_spent(e):
        return (f"retry budget spent ({priority.fruitless_attempts_count(e)} of "
                f"{priority.DEFAULT_RETRY_BUDGET} dispatches against unchanged evidence) — "
                "automation stopped retrying this row; a human clears it by advancing the evidence "
                "or filing a fresh item")
    if e.get("blocked_by"):
        return f"blocked_by {e['blocked_by']}"
    # ⛔⛔ AND `blocked_evidence` ALONE IS A STOP TOO, BECAUSE THIS FILE AND `priority.py` WERE
    # READING DIFFERENT FIELDS FOR THE SAME QUESTION (found 2026-08-27). `priority.py`'s
    # `apply_session_penalties` keys its -90 penalty on a non-empty `blocked_evidence` and says why
    # in as many words: "KEYED ON THE EVIDENCE, NOT ON `state`. The recorded observation IS the
    # block." This function keyed on `blocked_by`. So a row carrying evidence and no `blocked_by` was
    # PENALISED by the ranker and OFFERED by this checker at the same moment — AUT-PROP-018 sat at
    # the top of the ready list for an hour that way, with a recorded reason nobody was reading.
    # ⚠ THE SAME READER/WRITER MISMATCH FAMILY AS AUT-PD-013 AND AUT-PD-017: two files agreeing in
    # prose about which field carries a fact, and disagreeing in code.
    # ⭐ Hiding it is safe HERE and only here because the reason is NAMED in the blocked report
    # below — CLAUDE.md §0 wants a block to be checkable, not invisible, and an unread reason is
    # what this fixes rather than what it creates.
    if str(e.get("blocked_evidence") or "").strip():
        return f"blocked_evidence recorded: {str(e['blocked_evidence'])[:120]}"
    owner = e.get("owner")
    if owner and owner != me:
        return f"claimed by {owner}"
    if e.get("cost_class") not in SELF_DOABLE_COST:
        return f"cost_class {e.get('cost_class')} — needs a human (CLAUDE.md §2)"
    # ⛔ CLAUDE.md §3: an outward-facing or irreversible act is trimcrae's, whatever it costs.
    if e.get("requires_trimcrae"):
        return "outward-facing — trimcrae's act (CLAUDE.md §3)"
    return None


def ready(me: str | None = None) -> list[dict]:
    """Every ledger item a session could start right now, best first."""
    terminal = handoff.terminal_ids()
    out = [e for e in _entries() if _why_not_ready(e, me, terminal) is None]
    # ⛔⛔ THE SAME MISSING VALUE, RANKED TWO DIFFERENT WAYS BY THE TWO FILES THAT RANK IT
    # (AUT-PD-050). `priority.build_ledger` sorts unscored rows with `-1e9`, i.e. strictly below
    # every scored row; this line read `or 0`, i.e. as if the row had scored exactly zero — above
    # every negatively-scored row. Nothing diverged TODAY only because no currently-ready row holds
    # a negative score (measured 2026-08-28: ready scores run 36.0 to 152.0), and
    # `apply_fruitless_attempts` alone can take a ready row below zero, at which point the ranker
    # and the ready list would disagree about which work comes first with nothing saying so. ⚠ Same
    # reader/writer-mismatch family as the `blocked_by` vs `blocked_evidence` split fixed above:
    # two files agreeing in prose about a fact and disagreeing in code.
    # ⛔ AND `or 0` WAS ALSO WRONG FOR A REAL SCORE OF 0.0, which two committed rows carry — it made
    # a computed zero and an absent score indistinguishable at the one place that orders them.
    out.sort(key=lambda e: (priority.score_rank(e), e.get("id") or ""))
    return out


def live_leases() -> list[tuple[str, str]]:
    """`[(id, owner)]` for every open item a worker currently holds.

    ⚠ A LEASE IS FALSIFIABLE AND THAT IS WHY IT MAY BE COUNTED. It names WHICH worker holds WHICH
    item, with a timestamp `priority.py:release_stale_claims` ages out — so a session cannot quietly
    manufacture capacity pressure the way a self-issued "I am busy" flag would let it.
    """
    return [(e.get("id"), e.get("owner")) for e in _entries()
            if e.get("state") in OPEN_STATES and e.get("owner")]


def own_cycle_owners(me: str | None = None) -> set[str]:
    """Lease owners that are THIS SESSION'S OWN CYCLE — the caller itself, not a worker it sent.

    ⛔⛔ MEASURED 2026-08-28, AND THE STALL WAS MANUFACTURED BY THE CLAIM THAT WAS SUPPOSED TO PREVENT
    IT. A session finished one cycle, claimed `AUT-PD-132` for its second, wrote no code and stopped.
    The `Stop` hook that exists for exactly that moment said nothing, because this file returned 0:
    the claim had taken the lease count from four to five against a `subagent_width` of 5, so the
    tool read AT CAPACITY — "a WORKER must finish first" — and the worker it was waiting for was the
    session reading the message. 39 minutes, and trimcrae found it.

    ★ A WORKER IS NEVER BLOCKED BY ITSELF, which is the whole rule. `CYC-…-<session>` names the
    session as the worker: if that session is stopping, nothing is running for that row. A seat
    (`SEAT-s1-…`) or another session's cycle is a DIFFERENT worker and still counts — the capacity
    reading was right about them and is left exactly as it was.

    ⚠ AND THE HOOK'S OWN REMEDY POINTED HERE: "CLAIM THE ITEM, so this stops asking." That sentence
    was written for a driver that dispatched agents, where the claim records who is running. Applied
    to a session claiming for ITSELF it is a silencer, and the guard cannot tell the two apart from
    the ledger alone — so the owner-id shape is what tells them apart.
    """
    owners = {o for _, o in live_leases() if o}
    mine = {o for o in owners if me and o == me}
    read = envread.read("CLAUDE_CODE_SESSION_ID",
                        what="this session's id; its first 8 characters are the discriminator every "
                             "cycle id this session writes carries")
    sid = read.value or ""
    if len(sid) >= 8:
        mine |= {o for o in owners if o.startswith("CYC-") and o.endswith("-" + sid[:8])}
    return mine


def width_cap() -> int | None:
    """The governed concurrent-worker cap, READ rather than remembered (CLAUDE.md §1).

    ⛔ None when it cannot be read, and None means NO CAPACITY EXCUSE IS AVAILABLE — an unreadable
    dial must never buy a pass. That is the same failing-closed rule the publish bar uses, and it is
    the direction that costs nothing when wrong.
    """
    try:
        with open(STATE, encoding="utf-8") as fh:
            v = json.load(fh).get("subagent_width")
    except (OSError, ValueError):
        return None
    return v if isinstance(v, int) and not isinstance(v, bool) and v >= 1 else None


def unclassified_outward(me: str | None = None) -> list[dict]:
    """Ready rows that LOOK outward-facing and have not declared either way.

    ⚠ These are still counted as ready — the tool does not get to quietly withhold work on a guess.
    They are reported so somebody decides, because an undeclared row is a question, not a status.
    """
    return [e for e in ready(me)
            if "requires_trimcrae" not in e and _OUTWARD_LOOKING.search(e.get("what") or "")]


def blocked() -> list[tuple[dict, str]]:
    terminal = handoff.terminal_ids()
    rows = [(e, _why_not_ready(e, None, terminal)) for e in _entries()]
    return [(e, why) for e, why in rows if why and why != "finished"]


def lease_arbitration(me: str | None = None) -> list[dict]:
    """AUT-PD-049: the half neither `continuity.py` nor `stalled_holder.py` printed — for a row an
    OTHER worker's lease is holding back, is that lease still alive?

    ⛔ THE GAP THIS CLOSES. `priority.release_stale_claims` only runs inside `priority.py --write`,
    once a cycle period. Between writes, a row a dead seat claimed and never released reads
    identically to one a live seat is actively working — both just say "claimed by X" — which is
    exactly where the 2026-08-27 dead seat hid for 2 h 36 m. This computes the SAME arithmetic
    `release_stale_claims` uses (claim_lease.periods × the cycle interval) on demand, so the
    staleness is visible the moment anyone looks rather than only after the next re-score.

    ⭐ ONE VIEW, DERIVED, NO NEW STATE — it reads `claimed_utc` and the existing weights file; it
    writes nothing and reaps nothing. Reaping stays `priority.py`'s job so there is exactly one
    place a lease is actually released.
    """
    interval_h = priority._cycle_interval_hours() or 4.0
    weights = priority.load_weights()
    hours = interval_h * weights["claim_lease"]["periods"]
    now = priority._utcnow()
    terminal = handoff.terminal_ids()
    out = []
    for e in _entries():
        if e.get("state") not in OPEN_STATES:
            continue
        owner = e.get("owner")
        if not owner or owner == me:
            continue
        stamped = priority._parse_utc(e.get("claimed_utc"))
        age_h = None if stamped is None else (now - stamped).total_seconds() / 3600.0
        past_expiry = stamped is None or age_h >= hours
        # ⚠ THE ARBITRATION ITSELF: would this row read as ready RIGHT NOW if the lease were gone?
        # Checked against a copy — this view must never mutate the entry it read.
        unheld = dict(e, owner=None, claimed_utc=None)
        out.append({
            "id": e.get("id"),
            "held_by": owner,
            "claimed_utc": e.get("claimed_utc"),
            "age_h": age_h,
            "lease_hours": round(hours, 1),
            "past_expiry": past_expiry,
            "would_be_ready_if_released": _why_not_ready(unheld, me, terminal) is None,
        })
    # unstamped (age_h is None) first — an un-ageable claim is the most urgent to look at, not the
    # least, because `release_stale_claims` treats it as stale immediately (priority.py).
    out.sort(key=lambda r: -1e9 if r["age_h"] is None else -r["age_h"])
    return out


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
    ap.add_argument("--leases", action="store_true",
                    help="AUT-PD-049: every OTHER worker's lease holding a row back, and whether "
                         "that lease still looks alive")
    ap.add_argument("--me", metavar="CYCLE", default=None,
                    help="your cycle id, so items YOU hold a lease on still count as yours to run")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args(argv)

    if args.clauses:
        return 1 if _print_clauses() else 0

    if args.leases:
        rows = lease_arbitration(args.me)
        if not rows:
            print("no other worker holds a lease on an open row.")
            return 0
        stale = [r for r in rows if r["past_expiry"]]
        print(f"{len(rows)} open row(s) held by another worker, {len(stale)} past their lease "
              f"threshold (would be released by the next `priority.py --write`):\n")
        for r in rows[:args.limit]:
            age = "unstamped" if r["age_h"] is None else f"{r['age_h']:.1f} h"
            flag = "⛔ PAST EXPIRY" if r["past_expiry"] else "· within lease"
            unlock = " — would be READY if released" if r["would_be_ready_if_released"] else ""
            print(f"   {flag}  {r['id']}  held by {r['held_by']} for {age} "
                  f"(lease {r['lease_hours']:.1f} h){unlock}")
        if len(rows) > args.limit:
            print(f"   … and {len(rows) - args.limit} more")
        if stale:
            print("\n⚠ A row past expiry is not yet released — that only happens inside the next\n"
                  "  `priority.py --write`. If the holder is not actually running (ListAgents shows\n"
                  "  nothing), that is litter: release it by hand (`owner: null`) rather than wait.")
        return 0

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
        # ⛔⛔ AUT-PD-050, AND THIS LINE FAILED TWO DIFFERENT WAYS ON THE SAME COMMITTED LEDGER.
        # 91 rows omit `score` entirely, so `.get('score', 0)` printed a confident `[   0.0]` for a
        # row nobody scored — CLAUDE.md §4's "a populated field is not a measured one", in the list
        # the driver reads to CHOOSE WHAT TO WORK ON. Six other rows carry `"score": null`, for
        # which the default never fires and `None.__format__` raises: measured 2026-08-28,
        # `continuity.py --limit 30` died with `TypeError` at ready-rank 29, while the default
        # `--limit 10` never reached it. A view that works until you look past the top ten, and
        # crashes exactly on the starved rows, is how the starvation stayed invisible.
        # ⚠ THE LIMIT THAT REPRODUCES IT IS A MOVING TARGET, so do not read `30` as the property.
        # Re-measured on the pre-fix tree five hours later (seat s6): `--limit 30` exited 0, because
        # the ready list had grown past 30 SCORED rows and no longer reached an unscored one;
        # `--limit 300` raised the identical TypeError. The crash follows the starved rows, not a
        # number, and it gets HARDER to trip as the queue grows — which is the wrong direction.
        score = e.get("score")
        cell = f"{score:>6.1f}" if isinstance(score, (int, float)) else f"{priority.NO_SCORE:>6}"
        print(f"   [{cell}]  {e.get('id')}  {what[:150]}")
    if len(r) > args.limit:
        print(f"   … and {len(r) - args.limit} more")

    u = unclassified_outward(args.me)
    if u:
        print(f"\n⚠ {len(u)} ready row(s) read as OUTWARD-FACING and declare nothing. CLAUDE.md §3 "
              f"reserves\n   publishing, submitting, depositing and outreach for trimcrae — so each is "
              f"either his\n   act (set `requires_trimcrae: true`) or it is not (set it false and say "
              f"why). Undeclared,\n   it is a question wearing the costume of a ready item:")
        for e in u[:args.limit]:
            print(f"      {e.get('id')}  {' '.join((e.get('what') or '').split())[:88]}")

    # ⛔⛔ THE CAPACITY READING, ADDED 2026-08-27 AFTER THIS TOOL REPORTED CAPACITY THE LOOP DID NOT
    # HAVE. It offered 70 items as "READY TO RUN RIGHT NOW" while five workers were live at a
    # governed `subagent_width` of 5 — so every one of those 70 was ready in the ledger's sense and
    # startable by nobody. That is the same defect class as AUT-PD-023 one step out: a checker
    # reading a different set of facts than the thing it is checking.
    # ⭐ AND IT IS A REAL STOP, NOT A PERMISSION SLIP, WHICH IS THE LINE THIS FILE EXISTS TO HOLD.
    # A full cap means a WORKER must finish first — the same shape as waiting on a human or the
    # outside world, and unlike v1's green tick it is falsifiable: the holders are named, each lease
    # carries a `claimed_utc` that `priority.py:release_stale_claims` ages out, and one worker
    # finishing re-opens the list. ⚠ AN UNREADABLE CAP BUYS NOTHING (`width_cap()` returns None and
    # this branch is skipped), because a dial nobody can read must never excuse a stall.
    leases = live_leases()
    # ⛔⛔ DISTINCT WORKERS, NOT LEASES, AND THE FIRST VERSION OF THIS GOT IT WRONG IN THE SAME WAY
    # THE RECEIPT SCHEMA ALMOST DID. `subagent_width` caps CONCURRENT WORKERS (autonomy-state.json's
    # `_subagent_width_means` says so in as many words). One seat legitimately holds two items —
    # AUT-036 and AUT-037 were given to a single seat precisely because both re-curate one corpus —
    # so counting LEASES said 5-of-5 while four workers were running and there was room for a fifth.
    # ⚠ Counting the wrong unit here is not a miscount, it is a STALL: it would have manufactured a
    # capacity excuse out of good practice, and the excuse would have grown every time a seat was
    # sensibly given two related items.
    # ⛔⛔ AGENTS, NOT OWNER STRINGS — THE THIRD UNIT ERROR IN THIS FAMILY IN ONE DAY. First it
    # counted LEASES and one seat holding two items read as two workers. Fixed to distinct owners.
    # Then a FIVE-SEAT fan-out was claimed under ONE owner name and this read "1 worker against a
    # cap of 5" while ListAgents showed five running — under-counting by four and permitting a sixth
    # dispatch past the width cap the architecture calls the dial that failed catastrophically
    # (107 agents: 40 completed, 67 errored, the synthesis lost).
    # ⭐ A row may DECLARE how many concurrent agents its lease covers, via `claim_workers`. Absent
    # the field a lease counts as one agent, which is the honest default: most claims are one worker,
    # and a fan-out is the caller's to declare because only the caller knows it dispatched five.
    # ⚠ THIS IS A DECLARATION, NOT A MEASUREMENT, and it says so. The authoritative agent count lives
    # in ListAgents, which a Stop hook cannot call. An under-declared fan-out still under-counts —
    # so `claim_workers` is a floor on honesty, not a guarantee of it.
    # ⛔⛔ THIS SESSION'S OWN CYCLE IS NOT ONE OF THE WORKERS IT IS WAITING FOR (AUT-PD-140). See
    # `own_cycle_owners`: counting it let a session's own claim fill the cap and buy it a silent stop.
    mine = own_cycle_owners(args.me)
    by_owner = {}
    for entry_id, owner in leases:
        if owner in mine:
            continue
        by_owner.setdefault(owner, 1)
    for e in _entries():
        owner = e.get("owner")
        n = e.get("claim_workers")
        if owner in by_owner and isinstance(n, int) and not isinstance(n, bool) and n >= 1:
            by_owner[owner] = max(by_owner[owner], n)
    workers = sorted(by_owner)
    agent_count = sum(by_owner.values())
    cap = width_cap()
    at_capacity = cap is not None and agent_count >= cap
    if at_capacity:
        print(f"\n⚠ {agent_count} concurrent agent(s) across {len(workers)} holder(s) and "
              f"{len(leases)} lease(s), against a governed `subagent_width` of {cap} — the loop is AT "
              f"CAPACITY, so the rows above are ready in the ledger and startable by nobody until one "
              f"finishes:")
        for eid, owner in sorted(leases)[:args.limit]:
            print(f"      {eid}  held by {owner}")
        # ⛔⛔ THE WORDS AND THE EXIT CODE MUST SAY THE SAME THING (AUT-PD-140). This block used to
        # read "THIS IS NOT PERMISSION TO STOP WORKING" and then `return 0` four lines later — and
        # inside a `Stop` hook the exit code is the ONLY half that is read, because the hook exits
        # before it prints anything. A caveat the caller never sees is not a caveat.
        # ★ What a full cap actually licenses is narrow and is now said in those words: no NEW work
        # can start. It has never licensed leaving a row you already hold unworked.
        print("   ⛔ THIS STOPS NEW WORK STARTING; IT DOES NOT EXCUSE WORK ALREADY HELD. It is a\n"
              "      claim that a WORKER must finish first, and it is falsifiable: every holder is\n"
              "      named above, each lease carries a `claimed_utc` that priority.py ages out, and\n"
              "      one completion re-opens the list. If a lease above names a worker that is not\n"
              "      actually running, that is litter — release it (`owner: null`) and the work is\n"
              "      startable again.")

    if args.check:
        # ⛔⛔ A ROW THIS SESSION HOLDS IS WORK THAT HAS NO WORKER THE MOMENT THIS SESSION STOPS
        # (AUT-PD-140). It is checked BEFORE capacity because it is the case capacity was hiding.
        if mine:
            held = sorted(eid for eid, owner in leases if owner in mine)
            print(f"\n⛔⛔ YOU HOLD {len(held)} OPEN ROW(S) AND YOU ARE THE WORKER: "
                  f"{', '.join(held)}.\n"
                  "   A lease names WHICH worker holds WHICH item. These name THIS session, so if\n"
                  "   this session stops, nothing is running for them — the lease is then a hold on\n"
                  "   work nobody is doing, and every other worker reads the row as taken.\n"
                  "   ★ TWO HONEST ENDINGS, AND SILENCE IS NEITHER: work the row now, or release it\n"
                  "     (`owner: null`) so somebody else can. If the work IS running somewhere this\n"
                  "     cannot see — a subagent, a dispatched workflow, a spawned session — say so\n"
                  "     and say where.\n"
                  "   ⚠ Your own lease is NOT counted toward the capacity below: a worker is never\n"
                  "     blocked by itself, and counting it is what made this exit 0 on 2026-08-28\n"
                  "     while a claimed row sat untouched for 39 minutes.")
            return 1
        if at_capacity:
            return 0
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
