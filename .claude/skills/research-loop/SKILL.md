---
name: research-loop
description: Run one cycle of the autonomous EMC research loop. Load when a scheduled Routine fires a research cycle, when resuming a cycle after a rate limit or a container restart, when you are about to pick what research to work on next, when running a retrospective on the loop's own process, AND — added 2026-08-26 after this was the gap that made the session-shape rule unreachable — whenever a human asks for loop work directly in an INTERACTIVE session: take a ledger item, run a hardening round, run blind seats, write a receipt, fix what a seat found. Every load trigger used to be a Routine firing, so the interactive path never reached this file and its section 3 never bound. Covers the twelve-step cycle contract and the receipt that ends it; the three session shapes and when each is correct (fresh driver, parallel subagents, a spawned session); the stop conditions that make a cycle refuse to start; the rate-limit governor and why the limit is READ rather than inferred; the anti-gaming invariant that a bar may not be changed by the cycle it blocked; and which of the six existing skills to load at which step. It restates none of them — gates live in repo-gates, hardening in paper-hardening, posting in aixiv-submission, rentals in gpu-compute.
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

## 2 · ★★ THE CYCLE CONTRACT — twelve steps, and step 10 is not optional

**A cycle that cannot complete step 10 has failed, however much it wrote.**

1. **Orient cheaply.** Read `research/autonomy/autonomy-state.json` and `research-ledger.json`.
   Nothing else yet.
2. **Run §1's refusal checks.**
3. **Re-score.** `python3 research/autonomy/priority.py --write`. It is $0 and deterministic —
   never trust a score you inherited.
4. **Take the top item whose `cost_class` fits the current budget posture.** Free work always fits.
   ⭐ **CLAIM IT WITH THE TOOL, NOT BY HAND:**
   `python3 research/autonomy/claim.py --id <AUT-...> --me <your cycle id> --utc <now>`.
   It reads the row from **`origin/main`, never your working tree**, and the **push is the arbiter** —
   a rejected push means the remote moved, so the claim is withdrawn and the question re-asked. It
   prints `CLAIMED`, `YIELDED` (somebody else holds it — take the next item) or `RETRY`.
   ⛔ *Measured 2026-08-27 (AUT-PD-021): a seat claimed AUT-PROP-009 at 20:10:00Z and a concurrent
   session claimed the SAME item at 20:15:00Z from state fetched before that lease landed. Both
   worked; the collision surfaced as a merge conflict AFTER ~20 minutes of duplicated effort. A local
   commit is not an arbiter — two sessions can both make one and meet at the merge. `git push` is a
   compare-and-swap on the remote ref, so it is.*
   ⚠ **AND CLAIM AT DISPATCH, IN THE SAME ACTION THAT SPAWNS THE WORKER.** An unpushed claim protects
   nothing: every other session reads the trunk, and the trunk still says free. `claim.py --check`
   reports any claim you hold locally that the trunk cannot see — eight minutes of exactly that was
   measured the day this was written, on the author's own claim, while writing the fix for it.
   An item with no owner is indistinguishable from an item in progress.
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
10. **Write the receipt** — **allocate its id, never derive one by eye:**
    `python3 -c "import sys;sys.path.insert(0,'research/autonomy');import ids;print(ids.next_receipt('research/autonomy/receipts','<this session id>'))"`.
    ⛔ *Measured 2026-08-27 (AUT-PROP-013): every session computed `max(committed) + 1` from the same
    committed state, so concurrency was outside the derivation BY CONSTRUCTION. Two sessions 50 s
    apart both took `CYC-0016` and the second would have SILENTLY OVERWRITTEN the first; the same
    hour both filed `AUT-PROP-009` and `AUT-PROP-010` for four different items. And `AUT-PD-012` was
    issued twice by SEQUENTIAL cycles, which kills the comfortable reading that this is a race — the
    derivation collides on its own.* The id now carries a discriminator from your session id, so two
    cycles can share an ordinal (they are both genuinely the Nth cycle) and still never share a file.
    ⭐ **New ledger entries the same way** — `ids.next_entry_id("AUT-PD", entries)` — and
    `priority.py` now REFUSES a ledger with a duplicated id rather than ranking it.
    Contents of `research/autonomy/receipts/<cycle-id>.json`: what you took, what
    changed, what it cost, your session id, what is now queued, `blocked_by[]` (each with the
    **path** of whatever refused you — §6 depends on this), and **`route_advanced`**: the id of the
    live route you moved, or the literal `none`.
    - ⛔ **AND `subagents.max_concurrent` — SPELLED EXACTLY THAT, INCLUDING `0` FOR A CYCLE THAT
      SPAWNED NOBODY.** It is the only key `health.py`'s `fanout_is_governed` reads, and it is the
      dial the architecture records as having failed catastrophically. ⚠ *Measured 2026-08-27 over
      all 22 receipts (AUT-PD-013): seventeen of them used **three different schemas** —
      `max_concurrent`, then `concurrent_max`, then `launched` — so the row printed a FALSE ABSENCE
      for cycles whose fan-out was recorded plainly under another name.* **`launched` is not a
      substitute**: it is the serial total over the cycle, and the cap governs *concurrency* — five
      launched one at a time and five launched together are the same number and different acts.
      Record the serial total too if you like; record the width regardless.
      ⭐ **This is now a preflight gate, not a convention** — `python3
      research/autonomy/receipt_schema.py --check` owns the name for the writer and the reader both,
      and refuses the commit that lands a receipt without it. A field name agreed in prose between
      two files is a hope; this loop had already got this one right twice and lost it twice.

11. **Reap the finished sessions you left behind.** List sessions, pass them to the reaper, archive
    what it clears:

        python3 research/autonomy/session_reaper.py --self-id <this session's id>   # session list on stdin

    ⛔ **IT DECIDES, YOU ACT — AND IT ONLY EVER CLEARS A SESSION WHOSE RECEIPT IS ON THE TRUNK.**
    Archiving releases a container, so a session whose work never landed must stay visible: the reaper
    reports those as a FINDING (`idle with NO committed receipt`) and refuses to clear them, which is
    CLAUDE.md §7's branch-drift rule pointed at cleanup. It also never touches the calling session, a
    live one, or a status it does not recognise.
    ⚠ *Added 2026-08-27 because nothing ever closed a session and trimcrae had to ask: 32 archived by
    hand, 7 idle, 1 running — six new idle rows a day at a 4-hour cadence. A loop that cannot clean up
    after itself makes its owner the janitor.*
    ⚠ **And the reaper's first run against real data was WRONG in the dangerous direction** — it read
    `session_id` as if the field were an id, when cycles have written prose into it, and so reported
    three DELIVERED cycles as "died holding uncommitted work". Fixed, mutation-tested 5/5, and the
    regression is pinned by `test_session_reaper_refuses_to_lose_work.py`.

12. **Before you end the turn, prove the work survives you.** `python3 research/autonomy/continuity.py
    --check` must exit 0. Anything you are about to describe as a next step is a QUEUED LEDGER ITEM
    with a `closes_clause` link, or it is not real. ⚠ *Added 2026-08-27: three open bar clauses on the
    only paper with a public DOI existed solely as sentences in a reply, and a fresh cycle reads the
    ledger, not the reply.*

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

⛔⛔ **AND SPAWNING IS AN ACT, NOT A NOTE. THE CYCLE THAT REACHES THE CAP CREATES ITS OWN SUCCESSOR BEFORE IT ENDS.**

    python3 research/autonomy/handoff.py --json --reason "<why>"

builds the prompt **from committed state** — the queue from the ledger, the posture from `autonomy-state.json`. Pass it to `create_session` (claude-code-remote MCP) with this environment and repo, then record the child's id in your receipt under `handoff.child_session_id`. `health.py`'s `cycles_are_sized` reads that field: an over-cap session **with** a recorded handoff is GREEN, one without is RED.
⚠ *Added 2026-08-27. The brief asked for "proper usage of new session creation to manage context"; this section said a hardening cycle is a spawned session; `cycles_are_sized` measured when a session had run too long. **Three layers of knowing and nothing that could act** — so the session at the cap wrote "the next cycle should be a fresh session" in its final message and stopped. trimcrae: "You've flagged that a new session needs to start which is correct. But then you stopped there." A loop that needs a human to start its next session is not automated; it just has a longer fuse.*
⛔ **NEVER WRITE THE HANDOFF PROMPT FROM MEMORY.** It would be written from the context that is running out — the exact thing being discarded. And carry **no findings and no conclusions**: a successor that inherits its predecessor's reasoning inherits its mistakes, which is how a wrong seat finding propagated through two cycles here. Tell it where to look, never what it will find.

⛔⛔ **A SUBAGENT THAT WILL WRITE CODE WORKS IN A WORKTREE AND HANDS BACK A BRANCH. THE SHARED TREE
HAS ONE WRITER: THE DRIVER.** Put it in the seat prompt — worktree off `origin/main`, commit there,
push a branch, never touch the repository root.

⛔⛔ **AND ITS LOGS GO OUTSIDE THE WORKTREE, IN A DIRECTORY NAMED FOR THE SEAT — BECAUSE A WORKTREE
IS DELETED THE MOMENT ITS WORK LANDS, AND ITS EVIDENCE DIES WITH IT.** Two lines in every seat
prompt: *write every log to `scratchpad/<seat-name>/`, never inside the worktree, and NAME the log
paths in your final report.*
⚠ *Measured 2026-08-27 (AUT-PD-027), and it cost two wrong entries in the ledger.* Two seats
independently hit a preflight reporting **50 failures that did not exist** — `50 failed, 7901
passed` and `50 failed, 7933 passed`, `No module named 'pymbar'`. By the time the driver looked,
**both worktrees were gone and one log had already been truncated mid-write by a sibling writing to
the same filename.** The symptom survives only because it happens to be quoted inside the seats'
completion reports. ⛔ **So the driver could not reproduce it, and wrote TWO wrong mechanisms into
the ledger in sequence** — "a stale reading repaired between runs", then "a fresh worktree misses
the SessionStart hook" — neither checkable against the run that produced it, and the second
disproved only when someone finally made a worktree and looked. **A defect the driver cannot
reproduce immediately becomes unfalsifiable, and unfalsifiable defects attract guesses.**
⭐ *One seat did this unprompted — `scratchpad/aut015/aut015-devsetup-preflight3.log`, seat-unique
and outside its tree — and its run is the only one of the three still auditable.*
★ **AND A LOG WITH NO EXPLICIT EXIT MARKER IS NOT A RESULT.** The same day, a seat's monitor timed
out watching a preflight the seat had deliberately killed; that log never received its `EXIT=`
line, and the seat correctly reported nothing from it rather than quoting the tail. A truncated log
and a passing one look identical from the bottom.

⚠ *Measured 2026-08-27 across four agents in one afternoon, and it cost real time twice.* Two agents
were dispatched with "commit, do not push" and both ended up mid-write in the shared tree at once.
The consequences were not hypothetical:
  * **The driver could not gate its own work.** `preflight.sh` went red on `lint_citations` and the
    archive manifest — neither caused by the driver's staged change, whose own suite was green — so a
    driver holding verified work had no way to verify it, and committing anyway would have been
    committing into a mutation window. That is the morning's incident exactly (13 inverted claims).
  * **The manifest cannot be correct mid-flight.** `aso_archive_manifest.py` hashes the live tree, so
    while anyone else is writing it is *structurally* impossible to regenerate honestly. Any gate that
    reads it is red until the tree settles.
  * **A driver mis-measured because of it** — read the manifest from disk while an uncommitted
    regeneration sat there, and reported a defect on `main` that was not on `main`.
★ **THE TWO AGENTS THAT USED A WORKTREE HAD NONE OF THIS.** Each pushed a branch, the driver merged
both with zero conflicts, and the work survived a window in which the shared tree was ungateable —
including six verified P1s that would otherwise have lived only in `/tmp`, where a container restart
had already destroyed background work twice that day.
⛔ **A patch file in the scratchpad is NOT the durable form.** Push the branch. CLAUDE.md §7 calls
branch drift a data-loss bug; work that exists only in `/tmp` is the same bug with the branch missing.

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

## 5 · Escalate exactly five things. Everything else is silent.

1. A **journal submission** is recommended — immediately, with the top three venue fits and their
   evidence (`venue_fit.py`).
2. Spend crossing **expensive**, or a `⚠ DRIFT` row (`gpu-compute`, `inflight-reporting`).
3. A genuinely **goal-changing** fact — the north-star route closes, a capability reorders the
   portfolio.
4. **The loop itself is unhealthy** — a health condition red past its deadline.
5. **⛔⛔ A PAPER IS READY FOR trimcrae TO POST** — every bar clause passes and the only remaining act
   is one that belongs to him (`ready_to_post.py --new` exits 1 and names it).
   ⚠ *Added 2026-08-27, because the rule that should have covered it lived only in an agent's memory.
   trimcrae: "If you have a paper ready for me to post, you need a better way of contacting me with it
   than putting it in a thread of an unmonitored session." The ASO v2 was finished, gated and postable
   and the only notice of it was prose in a session he was not reading. CLAUDE.md §3 ALREADY required a
   PushNotification in the same turn — so this was not a missing rule, it was a rule nothing measured.*
   ★ **THE NOTIFICATION IS THE DELIVERABLE, NOT THE QUEUE FILE.** `research/autonomy/ready-to-post.json`
   exists so a cycle can DETECT the condition; a file nobody opens is the same failure one layer down.
   Send the `PushNotification` in the same turn, then `ready_to_post.py --mark-notified <PUB>` so the
   next cycle does not push again for the same commit — and DOES push again if the paper is revised.
   ⛔ **"Ready" means every clause passed.** A paper with one clause open is IN PROGRESS and must not be
   announced as ready; doing that once teaches him to ignore the channel, which costs more than the
   silence would have.

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
