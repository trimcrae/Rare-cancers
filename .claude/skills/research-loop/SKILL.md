---
name: research-loop
description: Run one bounded EMC research cycle, select a useful deliverable, claim ownership, and preserve the outcome without overlapping writers.
---

# Research cycle

Read `research/autonomy/OPERATING_PROTOCOL.md` first. It supersedes historical work selection,
unbounded hardening, synchronization-after-every-edit, and generic mandatory maintenance detours.

1. Identify the execution backend and real repository revision. Read budget posture. A legacy
   scheduled fire uses `cadence.py --check`; a direct user task is not a scheduled fire. Diagnose
   relevant health failures, not every unrelated row. Never bypass spend or ownership constraints.
2. Prioritize PUB-ASO's concrete release tasks. Read existing evidence before commissioning work.
   Choose one finite deliverable with a stop condition. Do not launch another paper while the
   priority package has self-doable work. Independent read-only evidence tasks may run in parallel.
3. Claim before writing. A remote legacy cycle uses `claim.py` on current main and must successfully
   publish the claim. Local Codex runs use their runner lock only after the legacy scheduler has
   been paused/drained. These locks are not interchangeable. No remote claim means no remote owner.
4. Put writing workers in isolated worktrees; the coordinator owns shared state and integration.
   Keep logs in task-specific durable paths. Record model, duration, output, and validation scope.
5. Execute the task. For reviews use `paper-hardening` and its finite iteration rule. For changes
   use relevant checks then `repo-gates`. Process maintenance is a separate owned task.
6. Integrate at a settled checkpoint after checking current main. Preserve branches until work is
   integrated. Do not push each observation separately or silently overwrite concurrent state.
7. For an outward act, evaluate the existing authority and all applicable publication clauses on
   the actual package. PUB-ASO does not auto-post to aiXiv. Prepare any human submission handoff.
8. Record failures and unresolved work precisely. A task with no advance is a valid result; another
   review, a launch, and a queue update are not themselves scientific progress.
9. The next cycle starts from durable artifacts, not a copied narrative. Do not claim a replacement
   scheduler is running until its actual execution and output have been observed.
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


11. This receipt step applies to the existing remote Claude cycle. A local Codex receipt is a
    separate runner outcome, not a fabricated `CYC-*` record; do not invent `ccr_session_id`.
    Publish/notify only through authorized existing paths. End with the result and next action.

The [legacy reference](references/legacy-2026-09-04.md) preserves backend-specific trigger, claim,
and receipt mechanics. Consult only the relevant sections. It is not an instruction to resume
unbounded loops or apply Claude-only session APIs to Codex.
