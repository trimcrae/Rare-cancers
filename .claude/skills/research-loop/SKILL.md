---
name: research-loop
description: Run one cycle of the autonomous EMC research loop. Load when a scheduled Routine fires a research cycle, when resuming a cycle after a rate limit or a container restart, when you are about to pick what research to work on next, when running a retrospective on the loop's own process, AND — added 2026-08-26 after this was the gap that made the session-shape rule unreachable — whenever a human asks for loop work directly in an INTERACTIVE session: take a ledger item, run a hardening round, run blind seats, write a receipt, fix what a seat found. Every load trigger used to be a Routine firing, so the interactive path never reached this file and its section 3 never bound. Covers the ten-step cycle contract and the receipt that ends it; the three session shapes and when each is correct (fresh driver, parallel subagents, a spawned session); the stop conditions that make a cycle refuse to start; the rate-limit governor and why the limit is READ rather than inferred; the anti-gaming invariant that a bar may not be changed by the cycle it blocked; and which of the six existing skills to load at which step. It restates none of them — gates live in repo-gates, hardening in paper-hardening, posting in aixiv-submission, rentals in gpu-compute.
---

# One cycle of the research loop

**This skill is an ORCHESTRATOR and owns exactly two things: the cycle contract (§2) and the stop
conditions (§1).** Everything else it points at. The architecture, the invariants and the evidence
behind them live in
[`emc-autonomy-architecture.md`](../../../research/manuscripts/program/emc-autonomy-architecture.md) —
**that file wins over this one**, and this file is the operating procedure sitting on top of it.

⛔ **DO NOT RESTATE ANOTHER SKILL HERE.** CLAUDE.md rule 1 applies to skills exactly as to
manuscripts. If you need a gate, load `repo-gates`. A hardening round, `paper-hardening`. A post,
`aixiv-submission`. A rental, `gpu-compute`. Work out of the sandbox, `ci-escape-hatches`. A board,
`inflight-reporting`.

---

## 0 · What a cycle is

**One fired session, one item of research, one commit, one receipt.** It is deliberately small. A
cycle that tries to do five things is a cycle that loses five things to one rate limit.

★ **Fresh context is a feature, not a limitation.** You start each cycle knowing nothing, which is
precisely why you cannot inherit last cycle's stale belief. **Read the ledger, not the repository.**

---

## 1 · ⛔ REFUSE TO START if any of these holds

Check before anything else. A loop that works through its own alarm is the alarm failing.

| condition | how to see it | what to do |
|---|---|---|
| A **BLOCKING** §5.2 health condition is red | `python3 research/autonomy/health.py --check` (exit 1 = stop) | Write a receipt saying so, escalate per §5, stop. |
| ⛔ **A red that is NOT blocking — DO NOT STOP** | the board's `on_red`: `advises` or `redirects` | **Run the cycle.** `redirects` means fixing that row IS this cycle's work; `advises` means report it and carry on. ⚠ *Added 2026-08-27 after this row's absence killed the loop: every red used to stop a cycle, two conditions were then added whose subject is IMMUTABLE COMMITTED HISTORY (`cycles_are_sized`, `fanout_is_governed`), and no cycle in any session could clear them. The driver fired, refused, and pushed "health check permanently red, needs your call." A stop condition keyed to history that cannot change is an outage with a virtuous name.* |
| `backoff_level` is at maximum | `research/autonomy/autonomy-state.json` | Take one FREE item only, or stop. §4. |
| Preflight is red on `main` and not by your hand | `repo-gates` | Fixing that IS the cycle. Nothing else lands until it is green. |
| An unresolved escalation to trimcrae older than its deadline | the last receipts | Stop. He is the blocker and another cycle does not help. |
| ⛔ **Nothing in the queue is takeable** | `health.py`'s `queue_is_takeable` row | **This is a STALL, and it is the one that looks like a quiet week.** Do not fire and write "nothing to do" — that is what a stalled loop does forever. Find out WHY nothing is takeable (all owned? all blocked? retry budgets spent?), fix that, and if you cannot, escalate it as §5's trigger 4. |

---

## 2 · ★★ THE CYCLE CONTRACT — ten steps, and step 10 is not optional

**A cycle that cannot complete step 10 has failed, however much it wrote.**

1. **Orient cheaply.** Read `research/autonomy/autonomy-state.json` and `research-ledger.json`.
   Nothing else yet.
2. **Run §1's refusal checks.**
3. **Re-score.** `python3 research/autonomy/priority.py --write`. It is $0 and deterministic —
   never trust a score you inherited.
4. **Take the top item whose `cost_class` fits the current budget posture.** Free work always fits.
   Set `owner` to your cycle id **and `claimed_utc` to now**, and commit that before doing any work:
   an item with no owner is indistinguishable from an item in progress.
   ⛔ **A CLAIM IS A LEASE, NOT A DEED — STAMP IT.** An unstamped claim cannot be aged, so
   `priority.py` releases it on the very next re-score and another cycle may take the item out from
   under you. Worse, before the lease existed, an unstamped claim was IMMORTAL: CYC-0003 claimed an
   item, finished, and parked the queue's top entry permanently.
   ⭐ **AND RELEASE IT IN STEP 9** — set `owner` back to `null` whether you finished, failed or gave
   up. The lease is the backstop for a cycle that DIED; a cycle that lived and did not release is
   just leaving litter the backstop has to clean.
5. **⭐ TAKE THE FREE OBSERVATIONS FIRST.** Any `UNKNOWN` or `STALE` field on this item that a
   `git show`, a public Actions read or a `WebSearch` would settle is settled **now**, before you
   write a sentence about it. CLAUDE.md §4 — and `ci-escape-hatches` §0 for which rung to use.
6. **Do the work.** Load the owning skill for the step. §3 chooses the session shape.
7. **Self-check.** Gates per `repo-gates`. If the item was a paper heading outward,
   `python3 research/autonomy/publish_bar.py --paper <PUB> --sha <sha>` decides — not you.
8. **Commit.** Preflight must pass, exit code unmasked. **Checkpoint after THIS item, never batch** —
   the whole rate-limit design rests on it.
9. **Write back what you OBSERVED** onto the entry: **release your claim (`owner: null`)**, set the
   new state and `last_evidence_utc`, and for a failure the *diagnostic*. ⛔ CLAUDE.md §4: never a "probably". If you cannot diagnose it, record
   `UNKNOWN` and queue the diagnostic as its own entry.
10. **Write the receipt** — `research/autonomy/receipts/<cycle-id>.json`: what you took, what
    changed, what it cost, your session id, what is now queued, `blocked_by[]` (each with the
    **path** of whatever refused you — §6 depends on this), and **`route_advanced`**: the id of the
    live route you moved, or the literal `none`.

⭐ **`route_advanced: none` is the loop's own honesty instrument.** Three in a row means the loop is
doing documentation, not research, and the health checker escalates on exactly that. **Write it
honestly** — a cycle that inflates it has disabled the only alarm pointed at the failure mode
CLAUDE.md §0 cares most about.

---

## 3 · Session shapes — choose by context cost, not preference

| shape | when | how |
|---|---|---|
| **This session** | the ordinary case | You are the driver. Read narrowly. |
| **Parallel subagents** | ≥2 independent items, or the blind seats of a hardening round | Launch them in ONE message so they run concurrently. Each returns a **structured verdict, not prose** — you must not pay context for the search that produced it. Width is capped by `autonomy-state.json`. |
| **A spawned session** | anything that will not fit one context: a full hardening cycle, a large corpus read | Spawn it, record its session id on the entry, and **end your turn.** The child writes its own receipt. |

⛔ **THE DRIVER NEVER WAITS.** Dispatch, record, end. A cycle blocking on a subagent is a cycle a
rate limit can kill while holding uncommitted work. CLAUDE.md §1 and §6.

---

## 4 · Rate limits — READ the limit, never infer it

`get_session` on yourself (omit `session_id`) returns `external_metadata.rate_limit_info`:
`status`, `rateLimitType`, `resetsAt`, `isUsingOverage`. **All four, at $0, with no network.**

- **Before taking a non-free item**, read `status`.
- **On a limit**, read `resetsAt` and **self-bind a wake just past it** (`send_later`) — measured
  working 2026-08-26. Then stop. Do not retry into a wall.
- **You lose nothing by dying.** State is in git; the next cycle re-reads the ledger. There is no
  resume protocol because there is no in-context state worth resuming.
- **`isUsingOverage: true` is a SPEND EVENT**, not headroom — CLAUDE.md §5's "engineering is free"
  stops being true there. Escalate it.
- **At backoff ≥ 2, take only `fetch` and `regrade` items.** Those are dispatch-and-exit against
  Actions, which costs **no Claude budget at all**. ⭐ The loop keeps making progress on a spent
  budget — that is the point.

---

## 5 · Escalate exactly four things. Everything else is silent.

1. A **journal submission** is recommended — immediately, with the top three venue fits and their
   evidence (`venue_fit.py`).
2. Spend crossing **expensive**, or a `⚠ DRIFT` row (`gpu-compute`, `inflight-reporting`).
3. A genuinely **goal-changing** fact — the north-star route closes, a capability reorders the
   portfolio.
4. **The loop itself is unhealthy** — a health condition red past its deadline.

⛔ **Nothing else.** Not a finished cycle, not a green gate, not a clean commit, not "which should I
do first" when all of them are self-doable. CLAUDE.md §2's phrasing test applies inside a cycle
exactly as outside it: about to write *"want me to X?"* about something you can do — **do X**.

⚠ **An aiXiv post is NOT an escalation.** It is a notification after the fact, per the standing
grant. A journal submission is never anything but an escalation.

---

## 6 · ⛔⛔ Self-improvement, and the one edit you may not make

You may edit anything, commit, and merge to `main` unattended (granted 2026-08-26). **The price is
one invariant:**

> **A bar may not be changed by the cycle that the bar just blocked.**

Improving the mechanism and making your own success easier are both edits. The test: *does this
change make it easier for me to report success?* Run
`python3 research/autonomy/amendment_guard.py --receipt <receipt> --diff-from <base>` **before you
commit**. If it says REFUSED, file a proposal and escalate — a later cycle may make the identical
change.

- **Improvement comes from RECEIPTS, never introspection.** Hit friction → file a `process_defect`
  entry with the evidence. A retrospective reads the last N receipts for *patterns*.
  ⭐ **"Nothing to improve" is a valid retrospective**, and one that always finds something is itself
  a defect.
- **Governed edits are DECLARED** — append to `amendments.jsonl` with the `self_serving_check`
  **answered**. You may change anything; you may not change anything quietly.
- **Never weaken a guard test to make a change pass.** Mutation-test it instead — `paper-hardening`.

---

## 7 · Triggers you may make, and the one you cannot

- ✅ Delete, retime, rewrite, or fire **a trigger you created yourself**. ✅ Create self-bind triggers
  that wake a session already holding the repo — that is how a rate-limit resume works.
- ⛔ **You have NO control over the UI-created driver Routine from outside it** — not its prompt, not its cron, not a manual fire (`fire_trigger` refuses it too, measured 2026-08-26). Only a session THAT ROUTINE ITSELF FIRED may act on it, and only to disable it. Both `update_trigger` and
  `fire_trigger` refuse anything `created_via: http_api`. Disabling from inside a cycle is the one
  exception, and it exists so a loop which detects it is broken can stop itself — the right move when
  the alternative is looping on a fault.
  ⭐ **This is why the cycle contract lives HERE and not in the Routine's prompt.** This file you can
  edit; that prompt is frozen at whatever trimcrae last pasted. Improvements to the contract land in
  this file, and the prompt only ever says "read it".
- ⛔ **You cannot mint a fresh-session Routine that has the repo.** Agent-minted lineage carries no
  `sources`; it fires, reports SUCCEEDED, and delivers nothing. Only trimcrae can, from the
  claude.ai UI. Architecture §2.2.
- ⛔ **Name every trigger you create with your cycle id**, and reap your own orphans in the
  retrospective. This repo has paid twice for orphan pollers he had to spot himself.
- ⛔ **Never keep one long-lived hub session as the scheduler.** It works and it silently undoes §0.

---

## 8 · The five things this loop refuses to do

1. **Post any paper that fails one clause of the bar** — and never lower a clause to fit a paper.
2. **Treat an aiXiv Rating as evidence.** It is written by an unauthenticated endpoint —
   `aixiv-submission` §0.
3. **Write a negative because the live route is hard.** The scorer clamps it; do not route around it.
4. **Report a fire as a delivery.** Read the artifact, never the run record.
5. **Go quiet when broken.** A silent loop and a dead loop look identical from outside — escalation 4
   is what makes the difference visible.
