---
id: DOC-SPRINT-S8-HANDOFF
title: "S8-HANDOFF — the three handoff/claim defects: one fixed, one refuted-and-corrected, one dissolved in a proven patch"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S8-HANDOFF — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S8-HANDOFF — the handoff knot, the lineage ceiling, and the claim deadlock

**Item(s):** AUT-PD-169, AUT-PD-173, AUT-PD-174
**Owned paths:** `research/autonomy/handoff.py`, `research/autonomy/continuity.py`,
`research/autonomy/session_cap.py`, `research/autonomy/session_reaper.py`,
`research/autonomy/stalled_holder.py`, `research/autonomy/holder_liveness.py`,
`.claude/hooks/ready-work-at-turn-end.sh`, `research/autonomy/tests/**`, this file
**Started (UTC):** 2026-09-01T18:45Z  **Finished (UTC):** 2026-09-01T19:14Z

## Verdict

**AUT-PD-169 — FIXED** in code (`session_cap.py` + the hook + tests), and the row's own preferred
remedy is **refuted**: no new ledger field is needed, because the falsifiable record it asked for
already exists and is already required.
**AUT-PD-173 — PARTIALLY REFUTED, and its recorded chain is wrong.** The ceiling is real and is
*not* in this repository's code. The present-tense claim "this loop now reaches it" does not hold:
the chain re-rooted on 2026-08-29 and the deepest loop lineage since is **3**. The row's open
question (a) — "does reaping an ancestor shorten the chain?" — is now **answered NO** by arithmetic
on the control plane's own numbers, which kills the cheap fix the row was hoping for.
**AUT-PD-174 — DISSOLVED, in a patch that is written, run and proven — but NOT LANDED, because
`claim.py` is not this seat's to edit.** The deadlock is removed by construction and the property the
pushed-trunk rule protects is held *more tightly* than before. The patch, its property suite and the
exact governed-test cost are all below.

---

## 1 · AUT-PD-169 — the turn-end hook told a spawner to claim for a successor that claims itself

### 1.1 The sequence, stated precisely (who holds the claim at each moment)

| t | actor | ledger row R (`owner` on the trunk) | what happens |
|---|---|---|---|
| t0 | — | `null` | R is the queue's top takeable row. |
| t1 | parent P | `null` | P runs `handoff.py --json`; the prompt names R, under a heading saying the queue "is a pointer, not a plan". |
| t2 | P | `null` | `create_session` returns a **CCR id** (`session_01…`). The child's **harness session uuid** is assigned inside the child's container and is never returned to the caller. |
| t3 | Stop hook | `null` | `continuity.py --check` sees R ready and unowned → exit 1. `session_cap.py --check` says **MUST NOT STOP** (see 1.2). The hook prints option 1: *"CLAIM THE ITEM FOR THE WORKER THAT IS RUNNING IT"*. |
| t4 | P (obeying) | `<any string P can write>` | P stamps `owner` + `claimed_utc` on R and pushes. |
| t5 | child C | unchanged | C runs the contract: step 3 re-scores, step 4 calls `claim.py --id R --me CYC-NNNN-<discriminator(C's own harness uuid)>`. |
| t6 | `claim.decide()` | unchanged | `owner` is set and is not `me` → **YIELDED** (exit 1), whose documented correct response is *"somebody else holds it, take the next item"*. |
| t7 | — | still P's string | R is leased to a session that has ended. Only `priority.release_stale_claims` frees it, `claim_lease.periods × cycle_interval` later. |

**The knot is at t2→t6 and it is structural, not careless.** `ids.discriminator()` hashes the
*harness* uuid; `create_session` hands back a *CCR* id. Two id spaces — so the parent cannot compute
the successor's owner string even in principle.

**Measured** (`s8-169-decide.log`, and pinned in the new test file):

```
owner='CYC-0089-11223344'          -> YIELDED
owner='session_01ABC'              -> YIELDED       # the child's CCR id: the one that LOOKS right
owner='CYC-0090-aabbccdd'          -> CLAIMED       # only the successor's own string
owner=None                         -> TAKEN
```

### 1.2 The part the row did not name, and it is the mechanism that made the hook reachable

`session_cap.verdict()` was the gate that should have stopped the loud branch, and it graded a
**successful** handoff as a session that never tried:

* `blocked_handoff()` returns `None` for a receipt carrying `handoff.child_session_id` — **by
  design**, and its docstring says so.
* Nothing else read that field.
* So `verdict()` fell through to *"the latest receipt records no handoff attempt — an absent record
  is a session that did not try"* → `--check` exit 1 → the hook printed the loud branch → option 1.

That behaviour was **pinned by a committed test**
(`test_a_capped_session_may_stop.py::test_a_session_that_did_hand_off_is_not_blocked`, which
asserted `not may` for exactly this receipt shape).

### 1.3 What I changed

* **`research/autonomy/session_cap.py`**
  * new `handed_off(receipt, sid)` — reads `handoff.child_session_id`, and **refuses a session that
    names itself** as its own successor (both id spaces: `session_id` and `ccr_session_id`), which
    is AUT-PD-140's shape one field over.
  * `_verdict()` returns `(may, code, why)` and checks `handed_off` **before** `blocked_handoff`.
    Ordering is the whole fix. `verdict()` is kept as the two-valued face.
  * reason codes `HANDED-OFF` / `HANDOFF-BLOCKED` / `MUST-NOT-STOP`, emitted by `--check` as
    `MAY STOP [CODE] — …` and in `--json` as `reason_code`, so the hook branches on a **machine
    token defined once** rather than on a sentence (AUT-PD-017).
  * ⛔ **Nothing is widened.** The `cap` receipt requirement, the placeholder-id rule, the
    unreadable-cap and unreadable-session-id refusals are untouched; a blank/non-string child id is
    an absent record and still buys nothing.
* **`.claude/hooks/ready-work-at-turn-end.sh`**
  * the MAY-STOP branch now prints different guidance for `[HANDED-OFF]` (a successor is running;
    do **not** claim rows for it) than for a blocked handoff (no successor; the Routine is it).
  * option 1 is split into **1a — a subagent or dispatched workflow** (claim at dispatch, text
    unchanged, its 2026-08-27 evidence intact) and **1b — a spawned session** (do NOT claim; the
    falsifiable record is `handoff.child_session_id`). 1b binds even when the verdict branch is not
    reached, which covers a session spawning a *sibling* worker rather than a successor.
* **`research/autonomy/tests/test_a_session_that_handed_off_is_not_a_session_that_did_not_try.py`**
  (new, 20 tests): the knot itself parameterised over every owner string a parent can write, the
  control that an unclaimed row is TAKEN, the two-id-space proof, the new verdict, six anti-gaming
  refusals, and the reader/writer contract asserted **in both directions** (every code the hook
  greps is one `session_cap` emits; every bracketed code the hook tests for exists) plus `bash -n`.
* **`research/autonomy/tests/test_a_capped_session_may_stop.py`** — one test amended, see §5.

### 1.4 Why NOT the row's preferred option (b), `dispatched_to`

AUT-PD-169 ranked `(b)` "a `dispatched_to` field, distinct from `owner`, that the hook reads and
`decide()` ignores" as the shape that adds a fact rather than overloading one. It is not needed, and
it is worse here:

1. **The fact already has a home and a reader.** `handoff.child_session_id` is required by
   `receipt_schema`-adjacent grading (`health.py:cycles_are_sized`) and is produced only by a real
   `create_session`. A second record of the same fact is AUT-PD-013's family again.
2. **It would need ageing, and the row says so itself** — "a `dispatched_to` that nothing ages out
   is the immortal-claim defect with a new field name".
3. **It could not be written at the moment it is needed.** A handoff is the last act of a session,
   and writing a ledger field means claiming/pushing — which is AUT-PD-174's deadlock. The fix for
   one row would have been blocked by the other.

### 1.5 What I measured

```
$ pytest research/autonomy/tests/test_a_session_that_handed_off_is_not_a_session_that_did_not_try.py \
         research/autonomy/tests/test_a_capped_session_may_stop.py -q
37 passed in 0.48s
```
Before the amendment, the collision was exactly one test and exactly the expected one:
`1 failed, 74 passed` — `test_a_session_that_did_hand_off_is_not_blocked … assert not True`
(`s8-169-pytest.log`).

---

## 2 · AUT-PD-173 — the lineage ceiling: real, not ours, and not where the row says

### 2.1 "A specific number in specific code" — it is not in this repository

```
$ grep -rnE "(depth|lineage).{0,30}8" --include=*.py --include=*.sh research/ .claude/ scripts/
research/autonomy/session_cap.py:23          (a quoted platform message, in a docstring)
research/autonomy/handoff.py:112             (the same message, in a docstring)
research/autonomy/health.py:883              (the same message, in a comment)
research/autonomy/tests/test_a_blocked_handoff_says_which_block.py:43   (a fixture string)
research/autonomy/tests/test_a_capped_session_may_stop.py:33,71         (a fixture string)
$ grep -rnE "^[A-Z_]*DEPTH[A-Z_]*\s*=" --include=*.py .
(no output)
```

**Every occurrence of `8` is the control plane's own refusal, quoted.** There is no constant, no
config key and no code path in this repository that sets, reads or can change it. No edit here moves
the ceiling; only where a chain *starts* moves it.

### 2.2 The row's recorded chain is wrong, and the correct one settles its open question

AUT-PD-173's `depends_on_evidence` transcribes the chain as
`01WPGnj7 → 01F6Xn8 → 017VDt2 → 01CYvZx1 → 01Fg7WnZ8 → 01HcEoAC → 01Mfu3su → 01CUYirs`.
Walked node by node against the control plane (`get_session`, `parent_session_id`), the real chain
of the refused session is:

```
session_01V57XfFBDdusymFL1K7x2C4   root (origin ios, no parent) — "ASO paper vs autonomy sessions"
 └ session_01GEFbqguVTYsLJrg8EAFYfG        (1)
   └ session_01G6maQEKfLfVi8TqsraQVse      (2)
     └ session_01NsMER9Gsh1jLUTPYS1561F    (3)
       └ session_01QozkfPFys7ferRoCACbdTU  (4)
         └ session_01Fg7WnZ8Kc3wmysc7tpAfTy(5)
           └ session_01HcEoACbH8wWVoTo2je896N (6)
             └ session_01Mfu3suzekFUhjmY5uB3spC (7)
               └ session_01CUYirsUYqbaxCWGsX3iYMq (8)  ← refused here
```

`01CYvZx1` is **not** `01Fg7WnZ8`'s parent (`01Qozkf` is), and `01WPGnj7` is a different root
entirely. ⭐ **The corrected chain has exactly 8 parent edges from its root, matching the platform's
reported depth exactly** — so "lineage depth" is the creation-chain edge count, root at 0.

⭐ **AND THAT ARITHMETIC ANSWERS THE ROW'S QUESTION (a).** The row asks whether depth is computed at
creation or over LIVE sessions, and calls its own evidence "suggestive, not a result", because it
archived two ancestors and then saw the refusal in the wrong order to prove anything. The ordering
does not matter once the chain length is known: **the reported depth equals the FULL creation chain,
so no ancestor was excluded.** CYC-0085's own receipt records that it had already archived two
ancestors of this chain before the refusal fired; had archived ancestors been dropped, the number
would have been ≤ 6, not 8. ⛔ **Reaping before handing off does not shorten the chain, and the
row's cheapest proposed fix is dead.**
⚠ *What this does NOT establish, stated rather than left to be assumed:* it is arithmetic on the
control plane's numbers plus a receipt's own account of what it archived, not a controlled
archive-then-retry experiment. Running that experiment costs seven real session creations from a
depth-1 root, which is not worth it now that the arithmetic points one way.

### 2.3 "This loop now reaches it" does not hold today — REFUTED as a present-tense claim

Read from `list_sessions` + `get_session` on 2026-09-01:

* The last session in that 8-deep chain, `01CUYirs`, is **ARCHIVED**; the chain is dead.
* The loop **re-rooted the same day**: `session_01MnFYhJxduBrMQ9H59s9wAH` is an **ios root** and is
  the parent of five separate loop sessions (`01FNtxKh`, `01Hz2k29`, `01CJoStj`, `01RLHV3t`,
  `01Kre2Fz`), all at depth 1.
* The deepest loop-cycle session since is `session_01QEP94zP9byx3aFnnbKFiTE`
  (2026-08-29T14:46Z, "EMC research loop — cycle (AUT-025)"), parent `01Hz2k29` → **depth 2**.
* **There has been no "EMC research loop — cycle" session since 2026-08-29T14:46Z.** The loop's
  cycle chain is three days idle — and that is a *different* condition from the ceiling, which is
  what makes reporting the ceiling as the loop's live problem misleading.

⭐ This corroborates, from an independent reading, `CYC-0087-4ce79c2a`'s `lineage_note` on the trunk:
*"the ceiling is a property of WHERE a chain STARTED, not of the loop … AUT-PD-173's remedy may be
're-root the chain' rather than anything in this repository."* That receipt was written **after**
AUT-PD-173 and the row was never updated — which is the recurring cost the charter's rule 4 names.

### 2.4 What I did NOT change, and why

Nothing. The honest remedy is re-rooting, the loop already re-roots (the UI driver Routine fires a
fresh depth-1 session), and every lever on the number is outside this repository. I considered
teaching `handoff.py` to predict the refusal from a depth reading, and rejected it:

* the depth must be supplied by the agent (`handoff.py` cannot call MCP), so it is judgement in a
  file whose whole point is that no judgement is left in it;
* pinning `8` as a repository constant would be CLAUDE.md §4's *"never let a remembered AI figure
  carry an argument"*, written into code;
* the cost it would save is one refused tool call and one receipt field per eight cycles, against a
  ceiling the loop reaches only when it chains eight deep — which, per 2.3, it currently does not.

**Proposed row rewrite is in §6.**

---

## 3 · AUT-PD-174 — claiming needs a trunk that is VISIBLE, not a trunk that is PUSHED

### 3.1 The defect, reproduced against a real bare remote

`s8_test_claim_needs_a_visible_trunk_not_a_pushed_one.py::test_the_live_module_cannot_claim_while_the_gate_has_not_been_pushed`
builds a driver mid-cycle — one gated-but-unpushed commit plus an uncommitted re-score, which
`claim.py`'s own AUT-PD-165 note calls "the ordinary shape, not an edge case" — and claims a free
row on a reachable remote:

```
SUSPENDED: AUT-X was not claimed: HEAD carries 1 commit(s) that origin/main does not (<sha>), …
exit code 3 (terminal — no retry answers it)
```

For the 8.5–16 minutes a gate runs, the correct number of claimable items is **zero**, for a seat,
a dispatched workflow and a successor session alike.

### 3.2 The question the row does not ask, and the answer

> **Does claiming need a PUSHED trunk, or a trunk another session can SEE?**

It needs a trunk it can **see**: a base to read and a compare-and-swap to win. The caller's own work
was never a requirement — it was only ever *implicated*, because `git commit` + `push HEAD:main`
publishes the branch, so HEAD's contents rode along.

### 3.3 ★ The property the pushed-trunk rule protects, written out

> **P.** Every commit `claim.py` causes to appear on `origin/main` differs from the previous tip in
> **exactly one path** — `research/autonomy/research-ledger.json` — and by **exactly** the one-row
> claim stamp applied to the trunk's own ledger. Nothing the caller holds (committed, staged, or in
> the working tree) and no merge tree reaches `origin/main` through this module.

That is AUT-PD-160 (the commit door) and AUT-PD-165 (the working-tree door and the index door)
stated as one sentence.

**How the live module holds P:** three preconditions read once at entry — `commits_not_on_trunk()`
empty, `staged_paths()` empty, and the ledger blob staged by plumbing — after which `git commit` +
`push HEAD:main` publishes a HEAD those preconditions have made equal to trunk + claim.

**How the patch holds P:** *by construction*. The pushed object is

```
commit-tree <tree> -p <the origin/main sha this attempt just fetched>
```

where `<tree>` is written from a **scratch index** (`GIT_INDEX_FILE`) seeded by
`read-tree <that same sha>` plus exactly one `update-index` for the ledger blob, and the refspec is
`<sha>:main`. The caller's HEAD, index and working tree are inputs to **none** of those four
commands, so there is nothing for them to leak through, and the published history is base + 1
commit with no merge ever.

⭐ **It is strictly tighter, not merely different, and the difference matters tonight.** The live
preconditions are read **once, before the retry loop**, and the commit happens later: anything that
lands in HEAD or the index in that window rides along. That is a TOCTOU window, and in a shared tree
with concurrent writers — twelve seats in one working tree, which is the state this repository is in
as this is written — it is not hypothetical. The patch has no window because the caller's tree is
never read.

⚠ **What is deliberately given up, said out loud.** The SUSPENDED-over-unpushed-commits refusal also
worked as a *nag* to push gated work. That is a side effect, not the property. `claim.py --check`
still reports the failure it was written for (a claim the trunk cannot see), and the `HeadUnverifiable`
refusal is demoted — correctly, because under the patch HEAD is not part of what is published; the
one reading that still fails closed is the **base sha** (`TrunkUnreadable` → SUSPENDED), because that
sha is both the parent of the commit and the value the remote compare-and-swaps against.

⚠ **One named consequence.** A caller that claims while holding uncommitted ledger edits gets its own
copy stamped and left otherwise alone — so it is behind the trunk on *other* rows, exactly as after
any concurrent push, and must fetch and merge before it commits (CLAUDE.md §7's "rebase before every
push"). That used to be masked by `integrate()`, which the patch no longer runs. For a **clean**
caller the patch writes the whole claim commit's ledger and fast-forwards the local branch, so the
ordinary case ends exactly where it ended before.

### 3.4 What I measured

Both prototype and patch run against a real bare `origin` with real worker clones on
`claude/worker-*` branches (never this repository's remote — the sibling suite's rule).

```
$ pytest s8_test_claim_needs_a_visible_trunk_not_a_pushed_one.py -q     # subclass prototype
10 passed in 3.78s
$ pytest s8_test_patched_claim_module.py -q                             # the PATCHED module itself
6 passed in 2.49s
```

The ten include, asserted against the **remote** rather than a verdict string:

* the claim lands from a tree holding an unpushed commit **and** an uncommitted re-score;
* the stray commit is **absent from the bare remote**; the trunk advanced by exactly one commit whose
  only parent is the base read; exactly one path changed; and the published ledger does **not**
  carry the caller's ungated re-score;
* the caller's local commit, its file and its re-score all survive, and its ledger carries the lease;
* **two single-site mutations**, each of which makes the leak reproduce — parenting the claim on
  `HEAD` instead of the trunk, and seeding the scratch tree from `HEAD` instead of the trunk. Both
  mutants publish the strays, which is what makes the construction load-bearing rather than
  decorative;
* the clean-checkout case still ends on the claim commit with a clean tree;
* a lost compare-and-swap converges on attempt 2 **with no merge commit on the trunk** and with the
  caller's tree untouched;
* a staged index neither blocks the claim nor reaches the trunk (and the live module is asserted to
  still refuse it, so the test is not measuring nothing);
* and the patched module wins a **two-real-worker race** on one row: one CLAIMED, one YIELDED.

⚠ **Mutation testing was done in a scratch copy, never in the live tree** (charter rule 7): the
prototype subclasses `claim.Git`, and the patched module lives at
`<scratch>/s8_claim_py_PATCHED.py`, loaded into `sys.modules` by a pytest plugin.

### 3.5 ⚠ A red run that was not mine — the coordinator's hazard, arriving by a second door

My first in-place run of the committed claim suites against the patch reported **5 extra failures**
as `ledger_schema.SchemaViolation: refusing to write research-ledger.json` — raised inside the test
**harness's own** `push_a_claim` helper, on its toy ids `AUT-X`/`AUT-Y`. Per the coordinator's
protocol I re-ran the identical command: **all five passed**, and the real module passed 26/26 on
the same tree. Cause: `research/autonomy/ledger_schema.py` is a sibling seat's **untracked, live**
file (S10), and it changed under the run — the message text I captured is the `require_parseable=True`
wording, while the file now calls `id_problems(..., require_parseable=False)` from `check_write`.
⛔ **Recorded so nobody reads those five as evidence about the patch.** The remaining failures below
reproduced identically twice with real assertions named.

### 3.6 The cost of landing the patch, measured exactly

`17 failed, 28 passed` across the two committed claim suites. **Not one is a property failure**;
every one is a test bound to the old *call sequence* or asserting a precondition the patch removes:

| n | tests | why it fails | what it needs |
|---|---|---|---|
| 8 | all of `test_claim_yields_to_the_trunk.py` that drive `claim()` | `AttributeError: 'FakeGit' object has no attribute 'path_is_clean'` | add `path_is_clean` / `trunk_sha` / `head_sha` / `is_ancestor` / `build_claim_commit` / `push_sha` to the `FakeGit` double. Mechanical. |
| 2 | `test_the_push_is_a_compare_and_swap…`, `test_an_exhausted_loop…` | stub `commit_ledger` / `push`, which the patch never calls → "the race never fired", "the loop made 0 attempts" | restub on `build_claim_commit` / `push_sha`. The prototype's `test_a_lost_compare_and_swap_converges_without_a_merge` is the working equivalent. |
| 2 | `test_the_withdrawal_keeps_an_unrelated_local_edit…`, `test_a_real_content_conflict…` | drive `withdraw_claim` / `integrate` **through** `claim()`, which no longer reaches them | drive those functions directly, the way `integrate`'s own note already says its test does. ⭐ The first one is **the fix visible in the committed suite**: its scenario (a genuinely dirty ledger) used to end SUSPENDED with the docstring calling that "a human's problem"; under the patch it ends CLAIMED and the unrelated `AUT-LOCAL` row still survives. |
| 5 | `…unpushed_work_refuses…`, `…someone_elses_staged_work_refuses…`, `…head_that_cannot_be_read_refuses…`, and the two `without_the_…_the_claim_publishes…` mutations | assert the removed preconditions and the mutations that defeat them | **replace** with the property assertions in §3.4, which are strictly stronger: they check the remote, not a refusal string. |

⭐ **One committed real-git test passes on the patch unmodified after a fix it forced:**
`test_a_worker_whose_base_moved_re_applies_its_claim_and_wins`. My first patch used
`head_sha() == base` to decide whether to fast-forward the caller's branch; that test caught the
consequence (*"the worker left the tree dirty after a successful claim"*), and the fix is
`is_ancestor(head, sha)` plus refreshing a **clean** caller's ledger from the claim commit. That is
the whole argument for running a patch against the committed suite rather than only its own.

### 3.7 ⛔ What I could not do: `claim.py` is not this seat's path

The fix lives in `research/autonomy/claim.py`, which is **not** in my OWNED PATHS, so per charter
rule 2 I did not take it. Deliverables for the driver, all durable:

* **the patched module, complete and runnable** —
  `<session-scratchpad>/s8-handoff/s8_claim_py_PATCHED.py` (814 lines; the live file plus one
  exception, five `Git` methods, one rewritten `claim()`, and the docstring paragraphs that carry
  the reasoning);
* **its property suite** — `<session-scratchpad>/s8-handoff/s8_test_patched_claim_module.py` and
  `…/s8_test_claim_needs_a_visible_trunk_not_a_pushed_one.py`;
* **the loader used to run the patch against the committed suites in place** —
  `…/s8_preload.py` (a pytest plugin; the copied-tests approach produced the false reds in §3.5);
* logs: `…/s8-174-pytest.log`, `…/s8-174-patched-pytest.log`,
  `…/s8-174-existing-suite-vs-patch.log`.

⚠ **The scratchpad is session state, not the repository.** If those files matter beyond tonight, the
authoritative summary is this section; the patch is small enough to re-derive from §3.3 alone, and
the two suites are the part worth keeping.

---

## 4 · What I changed, path by path

| path | change |
|---|---|
| `research/autonomy/session_cap.py` | `HANDED_OFF`/`HANDOFF_BLOCKED`/`MUST_NOT_STOP` codes + `CODES`; new `handed_off()` with the self-naming refusal; `_verdict()` (3-valued) checking it **before** `blocked_handoff`; `verdict()` kept as the 2-valued face; `--check` prints `MAY STOP [CODE] — …`; `--json` gains `reason_code`. |
| `.claude/hooks/ready-work-at-turn-end.sh` | MAY-STOP branch split on `[HANDED-OFF]`; option 1 split into 1a (subagent → claim at dispatch, unchanged) and 1b (spawned session → do NOT claim, record `handoff.child_session_id`). |
| `research/autonomy/tests/test_a_session_that_handed_off_is_not_a_session_that_did_not_try.py` | **new**, 20 tests. |
| `research/autonomy/tests/test_a_capped_session_may_stop.py` | one test amended — §5. |
| `research/autonomy/sprint-2026-09-01/S8-HANDOFF.md` | this file. |

**Not changed, deliberately:** `handoff.py` (§2.4), `continuity.py` (the fix needs no ledger field,
so `ready()` and the lease reader are correct as they stand), `session_reaper.py`,
`stalled_holder.py`, `holder_liveness.py` (the diagnosis does not implicate them — and §2.2 shows
reaping cannot shorten a lineage chain, which is the only reason they were in scope).

---

## 5 · Amendment record for the driver

`research/autonomy/tests/**` is GOVERNED. I did not append to `amendments.jsonl` (charter rule 4).
One committed test was amended; paste this, and run
`python3 research/autonomy/amendment_guard.py --receipt <receipt> --diff-from <base>` before the
commit.

```json
{"utc": "2026-09-01T20:40:00Z",
 "by": "SEAT-S8-HANDOFF",
 "item": "AUT-PD-169",
 "governed_paths": ["research/autonomy/tests/test_a_capped_session_may_stop.py"],
 "change": "test_a_session_that_did_hand_off_is_not_blocked: the assertion `not may` on the composite session_cap.verdict() is replaced by (i) a direct assertion that blocked_handoff() still returns None for a receipt carrying handoff.child_session_id, and (ii) an assertion that _verdict() reaches the NEW HANDED-OFF branch rather than the blocked one. The test's docstring records the change and the reason inline.",
 "why": "The test's stated guarantee is that a session holding a successor id may not use the BLOCKED branch to stop early. That guarantee is unchanged and is now asserted where it lives. The `not may` assertion was a PROXY for it, and the proxy held for the wrong reason: nothing read `handoff.child_session_id` at all, so a session that had successfully handed off scored identically to one that never tried, `--check` said MUST NOT STOP, and the turn-end hook fell through to a branch instructing the parent to claim a row for a successor that claims for itself (AUT-PD-169). The proxy was pinning the defect.",
 "self_serving_check": {
   "does_this_make_it_easier_for_me_to_report_success": "It makes it easier for a capped session to STOP, which is a form of success, so this must be answered rather than waved past. Three things bound it. (1) Nothing about WHEN a session may stop is widened except the one case the contract explicitly demands: `_verdict()` still requires `cap` receipts from THIS session, still rejects placeholder ids, still fails closed on an unreadable cap or session id, and a blank, non-string or self-naming child id still buys nothing — all asserted in the new test file. (2) The evidence is falsifiable and is not self-issued: `handoff.child_session_id` can only be produced by a real `create_session`, names a specific successor that `get_session` can verify, and is already the field `health.py:cycles_are_sized` grades an over-cap session on; typing a fake one is a false record with the same status as a fabricated receipt. (3) The seat making this change is not a cycle trying to stop — it wrote no receipt and took no ledger item, so the bar is not being changed by the run it blocked.",
   "who_benefits": "A session at its cap that did exactly what research-loop §3 requires. Before this it was told it 'did not try', and the only hook-satisfying moves left were to start a forbidden extra cycle or to pre-claim a row its successor is guaranteed to hand back.",
   "reviewed_by": "not yet — driver to run amendment_guard.py"
 }}
```

---

## 6 · Ledger rows the driver should write

I may not write these (charter rule 2).

| id | proposed change |
|---|---|
| **AUT-PD-169** | `state: done`, `closed_by: <this cycle>`, `last_evidence_utc: 2026-09-01`. Add to `what`: *"⭐ FIXED 2026-09-01 (seat S8-HANDOFF), and the mechanism was one layer deeper than the row: `session_cap.verdict()` graded a SUCCESSFUL handoff as 'a session that did not try', because `blocked_handoff()` returns None for a receipt carrying `child_session_id` by design and nothing else read that field — so the hook's loud branch, and its option 1, were reachable at every handoff. Fixed by ORDERING (`handed_off` is checked before `blocked_handoff`) plus a machine reason code the hook branches on, and by splitting the hook's option 1 into 1a (subagent → claim at dispatch) and 1b (spawned session → never claim). ⛔ OPTION (b) IS REFUTED, NOT DEFERRED: a `dispatched_to` field is unnecessary (the falsifiable record already exists and is already required), would need ageing (the row's own objection), and could not be written at the moment it is needed because a ledger write is a claim and a claim is AUT-PD-174. 20 tests; one governed test amended, record in the S8-HANDOFF findings file."* |
| **AUT-PD-173** | Keep OPEN but **re-scope and correct**, and drop the score. Corrections to record: (1) the ceiling is **not a repository constant** — every `8` in this repo is the platform's quoted refusal, so no edit here can move it; (2) the chain transcribed in `depends_on_evidence` is **wrong** — the real chain of `session_01CUYirs` is `01V57Xf → 01GEFbqg → 01G6maQE → 01NsMER9 → 01Qozkf → 01Fg7WnZ8 → 01HcEoAC → 01Mfu3su → 01CUYirs`, 8 parent edges from an ios root, matching the reported depth exactly; (3) **open question (a) is ANSWERED NO** — the reported depth equals the full creation chain including ancestors CYC-0085 had already archived, so reaping cannot shorten it and the cheap fix is dead; (4) "this loop now reaches it" is **not true today** — the chain re-rooted 2026-08-29 via the ios root `01MnFYh` and the deepest loop lineage since is 2, with no loop-cycle session at all since 2026-08-29T14:46Z. ⭐ The remaining live question is the one `CYC-0087-4ce79c2a` already named on the trunk and this row never absorbed: re-rooting, not depth. ⚠ Consider closing this row and filing the idle-loop observation (no cycle session in three days) as its own entry — that is a bigger fact than the ceiling and it is not what this row is about. |
| **AUT-PD-174** | Keep OPEN, `state: in_progress` is wrong — leave `queued`, and record the design as **decided and proven, awaiting a landing seat**: *"⭐ ANSWERED 2026-09-01 (seat S8-HANDOFF): claiming needs a trunk it can SEE, not one it has PUSHED. Build the claim commit detached — `commit-tree <tree> -p <fetched origin/main>` with `<tree>` written in a scratch `GIT_INDEX_FILE` seeded from that same sha — and push `<sha>:main`. The caller's HEAD, index and working tree are inputs to none of it, so property P (the pushed commit differs from the previous tip in exactly one path, by exactly the one-row stamp) holds BY CONSTRUCTION and strictly more tightly than the preconditions it replaces, which have a TOCTOU window between their single read and the commit. Patch written, run and mutation-tested against a real bare remote (16 tests, two single-site mutations both leak); the committed claim suites cost `17 failed, 28 passed`, none a property failure — 10 are test-double churn, 2 drive removed functions through `claim()`, 5 assert the removed preconditions and are replaced by strictly stronger remote-side assertions. NOT LANDED: `claim.py` was outside the seat's owned paths. Full analysis, the property statement and the per-test cost table: `research/autonomy/sprint-2026-09-01/S8-HANDOFF.md` §3."* |
| **new row (propose `AUT-PD-…`, `process_defect`, `free`, `queued`)** | *"Land AUT-PD-174's detached claim commit in `research/autonomy/claim.py` and re-point the two committed claim suites. The design is decided and proven (S8-HANDOFF §3); what remains is the edit plus ~17 test updates, itemised in §3.6. ⛔ Do not weaken the replaced tests into nothing: the five that assert the removed preconditions must be replaced by the remote-side property assertions, which are stronger than what they replace."* Should outscore AUT-PD-174 itself once that row is re-scoped to "decided". |

---

## 7 · What I could not do, and what it is actually waiting on

* **Landing AUT-PD-174.** Waiting on the driver assigning `research/autonomy/claim.py` to a seat, or
  taking it itself. Not blocked on anything external, not blocked on evidence — the evidence is done.
* **A controlled archive-then-retry experiment for AUT-PD-173's question (a).** Waiting on nothing
  but a judgement that it is worth seven session creations; §2.2 answers it by arithmetic, and I
  judged the experiment not warranted. Recorded as a decision, not a block.
* **Running `./scripts/preflight.sh`.** The driver's job on a settled tree (charter rule 6). Eleven
  other seats are mutating this tree; a preflight run from a seat measures nothing.
* ⚠ **Two items in the coordinator's mid-task message were addressed to a different seat** — the
  `lint_readability.sentences()` fix and the clause 1/2/6 sha-pinning both bear on `publish_bar.py`
  and AUT-PD-193, which are seat S9's. Nothing I wrote pins a clause-7 result or touches how seats
  are counted, so neither interacts with this seat's work. The sibling-seat red-run hazard **did**
  reach me and is recorded at §3.5.

---

## 8 · The wider autonomy suite: what the full run actually said, and why I do not report it as a result

⛔ **CORRECTED after the background run finished. My first reading of it was wrong, and the way it
was wrong is worth recording.** I read the log's visible tail, saw one cluster of nine `F`s, and
wrote that the suite showed "nine consecutive failures". Reconstructing the progress characters
programmatically gives **thirteen**, at positions `26–34, 219, 265, 380, 381` of 442 tests run.
Reading a pytest progress bar by eye is not a measurement.

**The run did not complete.** Its own marker says `EXIT=124` — killed by `timeout 900` at 53%.
⚠ Two method errors, both mine, both the kind this repository has already paid for:

* `grep -c "^EXIT="` returned **0** and I nearly took that for "no marker at all". pytest's progress
  output ends without a newline, so the marker landed mid-line as `..........EXIT=124`. The
  line-anchored grep is what the convention (`echo "EXIT=$?" >> log`) assumes and it is not safe
  against a writer that does not end its output with a newline — `grep -o "EXIT=[0-9]*"` is.
* the harness reported the background task as **"[exited with code 0]"** while the command's own
  marker said **124**. That is exactly the third of the three measured things the handoff prompt
  warns about — *"never trust the harness's reported exit code for a backgrounded gate; have the
  command write its own marker and read THAT"* — reproduced here on the first run that needed it.

**Cluster 1 (positions 26–34) is the sprint's own posture, diagnosed and reproducible.** All nine are
`test_a_cadence_nobody_enforces_is_not_a_cadence.py`:

```
E  AssertionError: loosening `cycle_interval_hours` past its declared bound went unnoticed
E  AssertionError: loosening `max_cycles_per_session` past its declared bound went unnoticed
E  AssertionError: loosening `items_per_cycle` past its declared bound went unnoticed
E  AssertionError: loosening `subagent_width` past its declared bound went unnoticed
E  … 'LEVEL-UNREADABLE' == 'HOLD-FLOOR-BREACHED'
```

They read `autonomy-state.json`, whose `budget_hold` carries `_SUSPENDED_FOR_THE_SPRINT_2026_09_01`
and whose `subagent_width` is **12** — the sprint's widened posture, authorised in the charter. That
file grep-matches none of this seat's paths (`grep -c "session_cap\|ready-work-at-turn-end\|handed_off"`
→ **0**) and this seat did not touch `autonomy-state.json`. ⛔ **Recorded, not fixed:** the guards are
working — they are detecting exactly the loosening the sprint declared — and the disagreement between
the declared bounds and the sprint posture is the driver's call for the length of the window. It must
not be "fixed" by widening a bound.

**The other four (219, 265, 380, 381) I cannot name, and did not reproduce.** Mapping a position to a
name needs the collection order of the tree the run saw, and sibling seats added test files to
`research/autonomy/tests/` between that run and my read — so every index past the first new file is
untrustworthy. Rather than guess, I ran every candidate file the current mapping points at, scoped:

```
$ pytest test_a_null_score_inputs_does_not_stop_the_loop.py test_a_reworded_idea_is_the_same_idea.py \
         test_an_unjoinable_history_cannot_switch_the_reapers_alarm_off.py \
         test_session_reaper_refuses_to_lose_work.py -q
60 passed in 3.04s   (EXIT=0)
```

⚠ **That is not proof those four were the same tests**, and it is not offered as one — it is the
strongest reading available from a truncated run over a tree eleven writers are mutating. What it
does establish is that the reaper and score-inputs suites are green on the tree as it stands, which
covers the only files in this seat's ownership list those positions could have implicated.

**A second full run was started and stopped (`TaskStop`) rather than finished**, for the same reason:
a full-suite run over a moving tree measures the tree, not the change. ★ **The scoped runs in §1.5,
§3.4 and here are what this seat reports**, and each of them is reproducible on demand.
