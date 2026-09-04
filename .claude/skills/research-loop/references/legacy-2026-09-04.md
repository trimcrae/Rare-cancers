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
| ⛔⛔ **THE CADENCE GATE — RUN IT FIRST, BEFORE THE HEALTH BOARD** | `python3 research/autonomy/cadence.py --check` (exit 3 = too soon; exit 4 = a hold is active and the last cycle cannot be dated) | **Exit immediately. Write no receipt, take no item, claim nothing; say in one line when the next fire is eligible.** A skipped fire is the cadence working, not a failure. ⚠ *Added 2026-08-29, and it is HERE rather than in the driver prompt because an agent cannot edit that prompt.* Measured that day against the live API: the driver Routine was created via `http_api`, so `update_trigger` refuses both a cron change and a plain `enabled: false`. Its cron is `13 */4 * * *` — six fires a day — while `autonomy-state.json` declares `cycle_interval_hours: 24`. **This gate is the only place those two are reconciled**; without it the declared cadence is `subagent_width` all over again, a governed number read by nothing. It is first for a second reason: the health board is several tool calls of orientation, and a fire that should not have started must cost two. |
| ⛔ **A `budget_hold` is active** | `autonomy-state.json` `budget_hold`; `health.py`'s `budget_recovering` row | **Honour the floor and every dial it declares, and do NOT lift it because it is inconvenient to the work you wanted** — §10.4, and `health.py` goes red if the live dials are looser than the declared posture. A hold expires into a REVIEW, never into full cadence: past `review_after_utc`, take a fresh utilisation reading, write it to `last_utilisation_report`, and only then lift it — with no fresh reading, step it down ONE level (2 → 1) rather than dropping it. **A stamp passing is not evidence that the budget recovered.** |
| A **BLOCKING** §5.2 health condition is red | `python3 research/autonomy/health.py --check` (exit 1 = stop) | Write a receipt saying so, escalate per §5, stop. |
| ⛔⛔ **The board lists an ESCALATION — do NOT just refuse again** | `python3 research/autonomy/health.py --escalations` (exit 1 = a restart budget is spent), or the board's `escalations` list | **Produce a CLAUDE.md §3 block and stop, and say in it that the loop's automated response is exhausted** — not another receipt reading "health red, refused". ⚠ *Added 2026-08-28 (AUT-PROP-034). A `blocks` red used to produce the same answer forever: refuse, write a receipt, die; the driver Routine fires again and a fresh session refuses identically. Nothing counted, so nothing ever rose above another refusal — the exact behaviour OTP's `intensity`/`period` and systemd's `StartLimitBurst` both exist to prevent, and the one Kubernetes' CrashLoopBackOff is the cautionary example of. `health.py` now counts consecutive RED board runs per condition (`RESTART_INTENSITY`, systemd's default of 5) and marks the row when the budget is spent; `stall_alarm.py` mails it from the Actions clock. **The refusal is still correct; a twelfth identical refusal is not a response, it is a loop.*** |
| ⛔ **A red that is NOT blocking — DO NOT STOP** | the board's `on_red`: `advises` or `redirects` | **Run the cycle.** `redirects` means fixing that row IS this cycle's work; `advises` means report it and carry on. ⚠ *Added 2026-08-27 after this row's absence killed the loop: every red used to stop a cycle, two conditions were then added whose subject is IMMUTABLE COMMITTED HISTORY (`cycles_are_sized`, `fanout_is_governed`), and no cycle in any session could clear them. The driver fired, refused, and pushed "health check permanently red, needs your call." A stop condition keyed to history that cannot change is an outage with a virtuous name.* |
| `backoff_level` is at maximum | `research/autonomy/autonomy-state.json` | Take one FREE item only, or stop. §4. |
| Preflight is red on `main` and not by your hand | `repo-gates` | Fixing that IS the cycle. Nothing else lands until it is green. |
| An unresolved escalation to trimcrae older than its deadline | the last receipts | Stop. He is the blocker and another cycle does not help. |
| ⛔ **Nothing in the queue is takeable** | `health.py`'s `queue_is_takeable` row | **This is a STALL, and it is the one that looks like a quiet week.** Do not fire and write "nothing to do" — that is what a stalled loop does forever. Find out WHY nothing is takeable (all owned? all blocked? retry budgets spent?), fix that, and if you cannot, escalate it as §5's trigger 4. |

---

## 2 · ★★ THE CYCLE CONTRACT — twelve steps, and step 10 is not optional

**A cycle that cannot complete step 10 has failed, however much it wrote.**

1. **Orient cheaply, and stamp the start.** Read `research/autonomy/autonomy-state.json` and
   `research-ledger.json`. Nothing else yet. Once §1 clears, run
   `python3 research/autonomy/cadence.py --stamp` — it records `last_cycle_started_utc`, which is
   what the cadence gate measures against. ⭐ **Stamped at the START, not at the receipt**, so a
   cycle that dies mid-flight still counts as a fire; otherwise a crashing cycle is re-fired every
   four hours forever, which is the herd the gate exists to stop.
2. **Run §1's refusal checks.**
3. **Re-score.** `python3 research/autonomy/priority.py --write`. It is $0 and deterministic —
   never trust a score you inherited.
4. **Take the top item whose `cost_class` fits the current budget posture.** Free work always fits.
   ⭐ **CLAIM IT WITH THE TOOL, NOT BY HAND:**
   `python3 research/autonomy/claim.py --id <AUT-...> --me <your cycle id> --utc <now>`.
   It reads the row from **`origin/main`, never your working tree**, and the **push is the arbiter** —
   ⭐ **a rejected push means "I LOST THE LEASE", never "retry harder"** (AUT-PROP-030): the claim is
   withdrawn, the base re-read, and the claim **re-applied to the base just read** before the next
   attempt. It prints one of four verdicts, and each has a different correct response — the exit code
   carries the same distinction (`0/1/2/3`):
   **`CLAIMED`** (exit 0) · **`YIELDED`** (1 — somebody else holds it, take the next item) ·
   **`UNREACHABLE`** (2 — the remote could not be reached, so *nothing was decided*; the one verdict
   a plain retry answers) · **`SUSPENDED`** (3 — ⛔ terminal, automation has stopped and a human
   clears it: an exhausted attempt bound, a merge only a person should resolve, or **a HEAD that
   carries commits `origin/main` does not**).
   ⛔ *That last one is AUT-PD-160 and it is the one you will actually hit, because it fires on the
   ordinary shape of a driver mid-cycle. A push publishes the BRANCH, not the claim: measured on
   origin/main 2026-08-29, a claim run over unpushed commits carried them to `main` along with a
   merge git made on the spot — a tree no gate ever saw, benign that time and invisible either way.
   **Push your gated work first, or claim from a checkout of `origin/main`.** The refusal names the
   remedy; it is not a retry.*
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
    `python3 -c "import sys;sys.path.insert(0,'research/autonomy');import ids,session_cap;print(ids.next_receipt('research/autonomy/receipts',session_cap.session_id() or ''))"`,
    **and put that same `session_cap.session_id()` in the receipt's `session_id` field.**
    ⛔⛔ **READ IT FROM THE ENVIRONMENT; NEVER TYPE IT, AND NEVER INVENT A LABEL.** Measured
    2026-08-28: scheduled cycles typed the literal `"scheduled-routine-session"` into that field, so
    nine consecutive cycles were INDISTINGUISHABLE FROM ONE SESSION'S to every reader — and the two
    readers that matter are `health.py:c_cycles_are_sized`, which grades the session-shape rule, and
    `session_cap.py`, which decides whether this session has earned the right to stop. A session
    whose receipts do not name it cannot show it is at its cap, so the hook keeps demanding another
    cycle and it runs nine. `CLAUDE_CODE_SESSION_ID` is set in this harness — checked, not assumed.
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
    **path** of whatever refused you — §6 depends on this), **`ended_utc`** (below), and
    **`route_advanced`**: the id of the live route you moved, or the literal `none`.
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

    - ⛔ **AND `ccr_session_id` — THE *OTHER* SESSION ID, WHICH IS NOT AN ALTERNATIVE TO
      `session_id` BUT A SECOND FIELD ALONGSIDE IT.** From
      `receipt_schema.FIRST_CCR_GOVERNED_CYCLE` onward, a receipt without it FAILS PREFLIGHT and
      therefore the commit. **Two id spaces, two sets of readers, and neither substitutes for the
      other:** `session_id` stays the harness `CLAUDE_CODE_SESSION_ID` — a bare UUID — because
      `health.py`'s `cycles_are_sized` and `session_cap.py` both key on it; `ccr_session_id` is the
      `session_01…` id the SESSION LIST speaks, and it is the only thing `session_reaper.py` and
      `holder_liveness.py` can use to join this receipt to a session row.
      ⭐ **READ IT, NEVER TYPE IT, exactly as for `session_id`** — the claude-code-remote
      `get_session` tool called with **no arguments** returns your own row and the value is
      `.ccr.id` (re-verified 2026-08-29).
      ⚠ *Measured 2026-08-28 (AUT-PD-124): most committed receipts carried no joinable id at all,
      so the reaper could not show that a single modern session had delivered — it archived nothing
      and reported delivered cycles as ones that may have died holding uncommitted work.*
      ⭐ **Spell the receipt's own id in `cycle_id` too.** `receipt_schema.audit` falls back to the
      FILENAME when that key is absent, so a receipt whose two disagree is graded under whichever
      one the reader reached for.
    - ⛔ **AND `ended_utc` — THE RECEIPT'S OWN CLOCK, WRITTEN WHEN THE CYCLE ENDS, AS AN ISO-8601
      UTC INSTANT (`2026-09-02T15:13:00Z`).** Required from
      `receipt_schema.FIRST_CLOCK_GOVERNED_CYCLE` onward; earlier receipts are grandfathered.
      ⛔ **`started_utc` IS NOT A SUBSTITUTE AND NEITHER IS ANY OTHER SPELLING.**
      `health.py:c_cycle_delivering` asks whether a fired cycle *delivered*, and the start is
      already owned by `cadence.py --stamp` in step 1 — writing it here too gives one fact two
      homes, and dates the firing rather than the delivery.
      ⚠ *Measured 2026-09-02: every receipt from CYC-0084 on carried `started_utc` and none of the
      end-time spellings health.py reads, so all fifteen sorted to the FRONT of a `(timestamp or
      "", filename)` sort and `receipts[-1]` resolved to the newest receipt still using the OLD
      name. The board reported `LATE — the last receipt is 103.5 h old` for seven consecutive runs
      while twelve receipts had landed inside that window, the newest 2.7 h old — and
      `advancing_live_work` read the same stale tail and reported NOT-ADVANCING against three
      four-day-old receipts. One field name, two false reds.* ⭐ **It was omission, not a redesign:
      this contract had never named a receipt clock in any of its 25 versions, and the two
      spellings interleaved within the same hours rather than switching over.* **A field name
      agreed in prose between two files is a hope** — this is the fifth time that has cost
      something here, so the clock is now a `*_KEY` constant the gate refuses a receipt without.

    - ⭐⭐ **AND THIS PARAGRAPH IS NOW MEASURED AGAINST THE GATE, WHICH IS WHY AUT-PD-146 COULD NOT BE
      CLOSED BY WRITING IT** (2026-08-29). `python3 research/autonomy/contract_check.py --check`
      DERIVES — by deleting fields from receipts the enforcer accepts and re-running it — the set of
      fields `receipt_schema.py` refuses a receipt for, and fails the build when THIS STEP does not
      name every one of them. ⚠ *`ccr_session_id` has been a commit-failing requirement since
      CYC-0070 while this text never mentioned it. All seven receipts written since do carry it —
      so the gap cost no build — but CYC-0073-d4ccfde4 recorded that it wrote the field only
      because it had opened `receipt_schema.py` for an unrelated reason. That is compliance by
      luck, and luck is not a mechanism.* **A field name agreed in prose between two files
      is a hope** — this repository has now lost that agreement four separate times (AUT-PD-013's
      fan-out key, AUT-PROP-013's ids, AUT-PD-037's serialization, AUT-PD-146's) — **so the
      agreement is checked rather than restated, and a new requirement in the enforcer reds the
      build until this step names it.**


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

builds the prompt **from `origin/main`** — the queue from the ledger, the posture from `autonomy-state.json`, the receipts from what the trunk carries. Pass it to `create_session` (claude-code-remote MCP) with this environment and repo, then record the child's id in your receipt under `handoff.child_session_id`. `health.py`'s `cycles_are_sized` reads that field: an over-cap session **with** a recorded handoff is GREEN, one without is RED.
⛔ **AND IT EXITS 3 RATHER THAN HANDING OVER WORK THE SUCCESSOR CANNOT SEE (AUT-PD-166). THE REMEDY IS THE COMMIT IT NAMES, NEVER THE ESCAPE FLAG.** The successor clones the trunk, so a ledger row or receipt you filed and did not push dies with your container — and it dies *after* being named in the prompt, which is worse than never filing it. ⚠ *Measured 2026-08-29: CYC-0079 handed CYC-0080 a queue whose top item, `AUT-PD-165` at score 134.0, had never existed on the trunk. That row was recovered only because the predecessor session happened to come back and push it forty minutes later — which is luck, since a session hands off precisely when its container is about to be reclaimed.* `--allow-divergence` exists for a builder that genuinely cannot commit — it emits the prompt with the lost ids named in it, and it is a way to make a loss legible, not a way past the check.
⚠ *Added 2026-08-27. The brief asked for "proper usage of new session creation to manage context"; this section said a hardening cycle is a spawned session; `cycles_are_sized` measured when a session had run too long. **Three layers of knowing and nothing that could act** — so the session at the cap wrote "the next cycle should be a fresh session" in its final message and stopped. trimcrae: "You've flagged that a new session needs to start which is correct. But then you stopped there." A loop that needs a human to start its next session is not automated; it just has a longer fuse.*
⛔ **NEVER WRITE THE HANDOFF PROMPT FROM MEMORY.** It would be written from the context that is running out — the exact thing being discarded. And carry **no findings and no conclusions**: a successor that inherits its predecessor's reasoning inherits its mistakes, which is how a wrong seat finding propagated through two cycles here. Tell it where to look, never what it will find.

⛔⛔ **A SUBAGENT THAT WILL WRITE CODE WORKS IN A WORKTREE AND HANDS BACK A BRANCH. THE SHARED TREE
HAS ONE WRITER: THE DRIVER.** Put it in the seat prompt — worktree off `origin/main`, commit there,
push a branch, never touch the repository root.

⛔⛔ **AND ITS LOGS GO OUTSIDE THE WORKTREE, IN A DIRECTORY NAMED FOR THE SEAT — BECAUSE A WORKTREE
IS DELETED THE MOMENT ITS WORK LANDS, AND ITS EVIDENCE DIES WITH IT.**

★★ **THE CONVENTION, AND IT COVERS EVERY FILE THE SEAT WRITES, NOT ONLY ITS LOGS.** Four lines in
every seat prompt — the same four for a blind review seat, a fix seat and a hardening seat, and this
section is where they live so no seat has to rediscover them:

> * Your scratch directory is `<SESSION-SCRATCHPAD>/<seat-id>-<item>/`, spelled as the **absolute**
>   path the system prompt gives — and **everything** you write outside the worktree goes there:
>   logs, scripts, clones, diffs, intermediate data. **Nothing at the scratchpad root.**
> * **Every filename inside it starts with your seat id** — `s55-preflight.log`, never `preflight.log`.
> * Every command whose result you will quote ends with `; echo "EXIT=$?" >> <log>`, and every log
>   you will quote opens with the stamp from
>   `python3 research/autonomy/seat_scratch.py --stamp <seat-id> <worktree>`.
> * **NAME the log paths in your final report.** The worktree is gone by then; the scratchpad is not.

⛔ **THE SCRATCHPAD ROOT IS SHARED BY EVERY CONCURRENT SEAT AND BY THE DRIVER.** It is not a private
directory that happens to be reused — it is one directory with N writers and no owner, so a generic
name there is not a name at all. It is a lock every writer takes and nobody releases.
⛔ **AND WRITE THE PATH ABSOLUTE, BECAUSE `scratchpad/` IS AMBIGUOUS IN THIS REPOSITORY AND RESOLVES
THE WRONG WAY.** There is a **tracked, repo-relative `scratchpad/`** — 4 committed files, and a
`.gitignore` rule (`scratchpad/lane10-*`) written to keep one lane's scratch out of the tree. So a
seat told to write to `scratchpad/<seat>/` and sitting in its worktree creates the
directory **inside the worktree**, which is precisely what the rule above forbids, and the evidence
dies with the worktree exactly as if the rule had never been written. `.gitignore` already says the
right home is *"the session scratchpad"*; say which one, in full, every time.

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

⚠ *Measured twice independently on 2026-08-28 (AUT-PD-055), and the rule as it then stood did not
stop it — because it said **logs**, and the file that collided was a **script**.* A seat's
`scratchpad/mutate.py` was overwritten by a sibling's. Its next run executed the sibling's file and
reported **`4 caught / 4` against a module in ANOTHER WORKTREE**, in a log that read exactly like a
clean run of its own: nothing failed, nothing was empty, and it was caught only because a human
noticed the module name was wrong. ⛔ **A mutation verdict fabricated in substance and finished in
appearance** — CLAUDE.md §4's *"a plausible-looking record is more dangerous than an empty one"*,
with a verdict attached. **Two seats hitting it independently makes it a container property, not
bad luck.**

⭐ **AND THE CONVENTION IS NOW MEASURED, BECAUSE THE SENTENCE ABOVE IT HAD ALREADY DECAYED ONCE.**
[`research/autonomy/seat_scratch.py`](../../../research/autonomy/seat_scratch.py) reads the two
halves of that incident, and they fail differently:
`--audit-root <scratchpad>` reports every regular file at the shared root — the path two writers can
both take — and every file inside a seat directory that does not carry its owner's id;
`--verify-log <log>` reads the log's own `SEAT=`/`WORKTREE=` stamp back against the absolute paths
the log names, and reports one belonging to a sibling's tree. **A log with no stamp is `UNSTAMPED`,
never `OK`** (§4: an absent reading is not a reading of absence). Its logic is asserted by
`research/autonomy/tests/test_a_seats_log_is_provably_its_own.py`, which gate 13 runs on every
commit; **its header names the four things it cannot see**, and a green audit is not proof a result
is the seat's own.
⛔ **It is NOT wired into `preflight.sh`, and must not be.** Preflight is offline, deterministic and
scoped to the tree; the scratchpad is per-session state no commit contains, so a gate reading it
would go red or green on facts the repository does not hold. **A seat runs it before it reports; a
driver runs it before it believes a seat.**
⚠ *Run against the live root the day it was written it returned four findings, and every one was the
DRIVER's:* `ci-main.log`, `mainsha.txt`, `prio.log` and `s0-ci-main-110a337.log`, all at the shared
root. **The driver is a writer like any other**, and three of those four are names any cycle reaches
for.
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
- **⛔⛔ WHAT `rate_limit_info` DOES NOT SAY IS THE HALF THAT BIT.** It returned
  `status: allowed`, `rateLimitType: five_hour`, `isUsingOverage: false` on 2026-08-29 —
  a clean verdict on the FIVE-HOUR window — at the same moment the WEEKLY budget was 71%
  spent three days into seven. **The weekly window is invisible to every instrument this
  loop has**, so a governor reading only this endpoint sees green all the way into the wall,
  and the only reading that has ever existed came from trimcrae in conversation. Treat a
  green `status` as saying nothing whatever about the week (`last_utilisation_report` in
  `autonomy-state.json` carries the reading and its derivation), and read `budget_hold`
  before concluding there is headroom.
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
- ⛔ **You cannot mint a FRESH-SESSION Routine that has the repo.** Agent-minted lineage carries no
  `sources`; it fires, reports SUCCEEDED, and delivers nothing. Architecture §2.2.
  ⚠ *Re-measured 2026-08-29 and the first half holds exactly:* a `create_trigger` with
  `create_new_session_on_fire` ran **26 minutes reporting `RUNNING`**, then `FAILED`, having pushed
  nothing — `session_context.sources` **absent**, against `[{git_repository: …}]` on a UI-created
  Routine in the same environment.
  ⭐ **BUT "ONLY trimcrae CAN, FROM THE UI" IS NO LONGER TRUE, AND THAT SENTENCE COST A SESSION AN
  EVENING.** `create_trigger` has no `source_url`; **`create_session` does**. So a Routine CAN be
  minted with the repo, in two calls:

      create_session(source_url=…, source_revision="main", outcome_branch="main", model=…)
      create_trigger(persistent_session_id=<that session>, cron_expression=…)

  Measured working: the runner came up with `sources` populated and `last_served_model` matching the
  pinned model, and a **scheduled** firing reached that same session.
  ⛔ **THREE MECHANICS THAT WILL BITE, ALL MEASURED THE SAME NIGHT.**
  (1) **`fire_trigger` IGNORES THE BINDING** — a force-fire spawns a fresh unattached session on the
  default model, so it is *not* a test of the schedule and answers the opposite of the truth. Probe
  a schedule with a schedule (`run_once_at`).
  (2) **`update_trigger` REFUSES to edit the prompt** of a Routine bound to a session that is not
  your own, so changing the prompt means delete-and-recreate.
  (3) **Deleting its only trigger ARCHIVES the bound session**, and an archived session cannot be
  bound — so a prompt change costs a new runner too.
  ★ **And source it from `main`, never a feature branch** — a scheduled job whose only source is a
  branch is CLAUDE.md §7's data-loss bug with a timer attached.
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
