---
id: DOC-SPRINT-S35-DRIFTGUARD
title: "S35-DRIFTGUARD — the merge-debt Stop hook had two always-green paths; both are closed, and it names 38 branches on arrival"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S35-DRIFTGUARD — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S35-DRIFTGUARD — both holes reproduced, both closed, and the fix fires immediately on 38 branches

**Item(s):** the mechanism finding in `S31-ORPHANS.md` §5 (GAP 1, GAP 2, GAP 3)
**Owned paths:** `.claude/hooks/merge-debt-at-turn-end.sh`, `scripts/tests/test_the_merge_debt_hook_can_see_a_branch_it_is_not_standing_on.py`, this file
**Refs read:** `HEAD` = `claude/max-token-usage-sprint-cwihvo`, local `origin/main` = `1d01f0790040d6b7107e58a98f5b8c81640247b2`
**Started/Finished (UTC):** 2026-09-01T20:10Z / 2026-09-01T20:35Z

## Verdict

**FIXED** — S31's mechanism finding is **CONFIRMED, not refuted**: both always-green paths reproduce
against a controlled fixture, and the hook had **no tests of its own at all**. Both are closed, the
classification that makes it possible costs **0.28 s where the obvious implementation costs 20.0 s
against a 15 s timeout**, and thirteen new tests plus eight mutations pin the result. **⛔ With the
fix in place the hook refuses the very next stop and names 38 branches carrying 153 unmerged
commits.** Nothing I changed makes stopping easier.

---

## ⭐ THE HEADLINE, FIRST

1. **Both holes are real, and I reproduced each with a control rather than by reading the source.**
   A single untracked file flips the hook from exit 2 to exit 0 with the merge debt unchanged; a
   branch pushed by a session that has ended draws **zero** mentions from the hook on any `HEAD`.
2. ⭐ **The hard part had a clean answer, and it was measured, not assumed.** The obvious
   implementation — `merge-base` per candidate ref — takes **20.0 s over 183 refs**, which is past
   the hook's **15 s** timeout in `.claude/settings.json`; a killed Stop hook is indistinguishable
   from a green one. One `git for-each-ref --no-merged=origin/main --contains=<root of main>` returns
   **the identical 37-ref set in 0.28 s**, compared as sets with `diff`, not as counts. Whole hook,
   live, three runs: **0.67 / 0.69 / 0.69 s**.
3. ⚠ **And I found a third thing neither S31 nor I was looking for: this clone is SHALLOW, grafted at
   2026-08-04.** That means S31's "133 branches share no common ancestor, so they are pre-rewrite
   history, not stranded work" is a conclusion the clone cannot support. **141 of those refs have
   tips below the graft: they are UNMEASURED, not merged.** The error direction is false silence, so
   every census figure here — S31's and mine — is a **lower bound**. The hook now says so in its own
   output.

---

## What I measured

### 1 · ⛔ First: the reproduction I got wrong, and the reading that corrected it

My first move was to run the old hook on the live tree — 17 dirty files, on a non-`main` branch — and
it exited 0. I was one sentence from reporting that as GAP 2 reproduced. It is not.

```
$ git rev-list --left-right --count origin/main...HEAD
29	0
```

`--left-right --count A...B` prints **left then right**: left = on `origin/main` only (BEHIND), right
= on `HEAD` only (AHEAD). This checkout is **29 BEHIND and 0 AHEAD**, so the old hook exited at
`[ "${AHEAD:-0}" -eq 0 ]` — one line *before* the dirty-tree check. **The dirty exit was never
reached, and attributing the silence to it would have been a "probably" dressed as a finding**
(CLAUDE.md §4). Everything below therefore runs against a throwaway fixture where I control the state.

⚠ This also refines S31's sentence *"the hook exits 0 at every stop tonight"*. It exits 0 at every
stop tonight; the **reason** is whichever early exit is reached first, and on this checkout it is the
AHEAD one. The dirty exit becomes load-bearing the moment the driver commits sprint work without
merging — which is the normal seat-wave shape, and which had already happened by the end of my seat
(`1 commit(s) off the trunk`, tree dirty).

### 2 · GAP 1 — a branch pushed by a session that has ended is unrepresentable

Fixture: an `origin` plus a clone; a seat branches, commits, pushes, and the session ends (we return
to `main`); the trunk then moves on.

```
-- origin/seat/s3-stranded is NOT an ancestor of origin/main  -> genuinely stranded
-- checkout is on 'main', tree clean
   OLD hook: EXIT=0, output lines: 0
-- and standing on a DIFFERENT branch with its own commit:
   mentions of 'seat/s3-stranded' in the hook's entire output: 0
```

**The mechanism, from the source rather than from the behaviour:**

```
$ grep -nE 'for-each-ref|ls-remote|refs/remotes|origin/\*' merge-debt-at-turn-end.sh
9:# ★ MEASURED THAT DAY ... `git for-each-ref` over `origin` found
```

**One hit, and it is in a comment.** The old file's only ref computation was `origin/main...HEAD`.
It had no concept of a branch on `origin`, so a branch whose session has ended has no stop left to
fire on. S31's GAP 1 is confirmed exactly as written.

### 3 · GAP 2 — one untracked file buys silence

Same fixture, same branch, same one unmerged commit. **The only variable is one untracked file:**

| tree | `git status --porcelain` | old hook exit |
|---|---|---|
| clean | *(empty)* | **2** — "⛔ 1 commit(s) on 'some-other-session' are NOT on main" |
| + one untracked file | `?? dirty-me.txt` | **0** — silent |

Confirmed as written.

### 4 · ⭐ The cost measurement — why the obvious fix would have been killed, not slow

The hook's configured timeout is **15 s** (`.claude/settings.json`). Measured on the live repository,
301 remote-tracking refs:

| formulation | processes | wall | result |
|---|---|---|---|
| `for-each-ref --no-merged=origin/main` alone | 1 | **0.106 s** | 183 refs — includes 146 that do not share this history |
| … then `git merge-base origin/main <ref>` per candidate | 183 | ⛔ **20.0 s** | 37 |
| **`for-each-ref --no-merged=origin/main --contains=<root>`** | **1** | ⭐ **0.284 s** | **37** |
| whole HALF B (root + census + distinct-commit count), 5 runs | 3 | **0.451 / 0.452 / 0.457 / 0.460 / 0.462 s** | 37 / 152 |

⭐ **The two methods were compared as SETS, not as counts** — `diff` of the sorted ref lists is empty.
A matching count would not have been evidence.

The naive form is slow for the exact reason it looks cheap: proving that **no** common ancestor exists
forces git to walk both histories to the end, and 146 of the 183 candidates are that case.

⭐ **And root-containment excludes the workflow data refs structurally rather than by name.** S31
proposed excluding `*-cache`, `email-outbox` and `figure-renders` by glob. They do not need it — all
13 `*-cache` refs plus `email-outbox` and `figure-renders` are **orphan refs sharing no root with the
trunk**, so they fall out of the query itself:

```
origin/email-outbox        disjoint   -        origin/literature-cache   disjoint   -
origin/figure-renders      disjoint   -        origin/modalities-cache   disjoint   -
origin/ci-input/tcip-…     shares     IN-37    (a real branch, correctly kept)
```

A name list would have been one more thing to keep in sync and one more place to widen quietly.

### 5 · ⚠ The shallow-clone finding — every census figure here is a LOWER BOUND

```
$ git rev-parse --is-shallow-repository        -> true
$ git rev-list --max-parents=0 origin/main     -> df0b8ee0  (2026-08-04, the GRAFT, not the root)
$ git rev-list --count origin/main             -> 11434
```

So `--contains=<root>` really asks *"does this ref contain main's earliest LOCALLY KNOWN commit?"*
That is sound for everything above the graft and **cannot classify anything below it**. Of the 146
refs this clone calls "no common ancestor":

| | refs |
|---|---|
| tip **below** the 2026-08-04 graft — **UNMEASURED, not merged** | **141** |
| tip above the graft, genuinely disjoint (orphan data refs) | 5 |

⛔ **This qualifies S31's census table.** Its "133 = pre-rewrite history, not stranded work" is a
claim resting on merge-base results that a shallow clone produces for a *different* reason. The
honest statement is that those refs are unclassifiable here. **All 37/38 branches the hook reports
today have tips from 2026-08-06 onward, well above the graft, so the reading is sound for every
branch it names** — but the number is a floor, and the hook prints that caveat rather than reasoning
it away.

### 6 · ⚠ Staleness — and why the old comment's argument does not transfer to the new half

The old file justified never fetching: *"a stale remote ref cannot produce a false silence."* **That
is true of HALF A and false of HALF B.** Measured with `git ls-remote` (read-only, no ref writes):

```
origin/main on the server : 105df270…
origin/main in this clone : 1d01f079…        FETCH_HEAD mtime: 8 minutes earlier
```

The trunk moved within eight minutes of the last fetch. For a census of *other people's* refs against
a last-known `origin/main`, a branch merged since the fetch reads as stranded and a branch pushed
since the fetch is invisible. **Fetching from a Stop hook would put a network round trip in the
stopping path, which the original comment correctly refused**, so the hook prints the age of the last
fetch and calls its number a reading rather than a truth.

⚠ The clone is otherwise near-complete: `ls-remote` shows 302 heads against 301 local, and the one
missing (`vaccine-calibration-cache`) is an orphan data ref that could not count either way.

### 7 · What the fixed hook does, run against the live repository

```
⚠ This checkout ('claude/max-token-usage-sprint-cwihvo') also has 1 commit(s) off the trunk. The
   worktree is dirty, so the merge instruction is deferred to the next clean stop … ⛔ The DEBT is
   not deferred, only the advice: it is printed here every stop.

⛔ 38 branch(es) on origin carry 153 unmerged commit(s). §7 calls this a DATA-LOSS BUG.
   Newest first (refs as last fetched, 13 min ago — no fetch is run from a Stop hook):

   1    2026-09-01  origin/claude/max-token-usage-sprint-cwihvo   ← this checkout (HALF A above)
   1    2026-09-01  origin/claude/s24-threshold-calibration
   1    2026-08-29  origin/claude/s76-sgk1
   3    2026-08-29  origin/claude/aut-pd-130-s4-CYC-0074
   …
   1    2026-08-28  origin/seat/s3-unscreened-endpoints
   … and 26 more
```

exit **2**, wall **0.67 / 0.69 / 0.69 s**.

---

## What I changed

### `.claude/hooks/merge-debt-at-turn-end.sh` — rewritten as two halves with different rules

The whole original file is preserved above a new section that records what was wrong with it. The
code is now:

- **HALF A — "does THIS session owe a merge?"** `origin/main...HEAD`, unchanged, **dirty-tree exit
  KEPT**. See the trade below.
- **HALF B — "does ANY branch on origin owe a merge?"** One `for-each-ref` over already-fetched
  remote refs. Runs on **every** `HEAD` including `main` and a detached HEAD, and is **not gated on
  the worktree at all**.

Other changes, each a widening:

- REPO discovery copied from `escalation-debt-at-turn-end.sh` (which I read but did not touch): the
  old `REPO="${CLAUDE_PROJECT_DIR:-/home/user/Rare-cancers}"` is the literal defect that made a
  sibling hook silently unreachable on a CI runner while its own tests all passed.
- An unresolvable `origin/main` in a repo that *has* remote refs now reports **UNMEASURED** and
  refuses, instead of exiting 0. A repo with no origin at all is still left alone.
- The census prints the age of the last fetch and, on a shallow clone, that its number is a floor.
- This checkout's own upstream branch is **marked**, not excluded, in HALF B's list.

### ⭐ THE TRADE, STATED PLAINLY — why HALF A keeps the dirty-tree exit

**What I kept and why**, both checked rather than assumed:

1. `~/.claude/stop-hook-git-check.sh` — a launcher-level user hook, **not ours**; it lives outside
   this repository and is wired through `launcher-settings.json`. I ran it on this tree: it exits 2
   on uncommitted changes **today**. That state is already alarmed, and two warnings for one state
   teaches the reader to skim both.
2. Mid-edit, HALF A's instruction — *"MERGE IT — not next turn"* — is genuinely the wrong advice.
   Twelve seats are editing this tree; a hook giving wrong advice at every stop is the wall the
   file's own header refuses to become.

**What I refused to trade:** the suppressed count is still **printed**, as a line inside HALF B's
block. A dirty tree now defers the merge *advice*; it no longer buys silence about the *debt*.

**And HALF B is not gated on the tree at all**, because the asymmetry is the whole of GAP 2: a dirty
worktree is a fact about this session's uncommitted edits and carries **no information whatever**
about whether somebody else's pushed branch is on the trunk.

⚠ **The residual, named rather than hidden:** if HALF B is empty *and* the tree is dirty *and* this
branch is ahead, the hook is silent — exactly as before. Verified in the fixture (`OLD=0 NEW=0`).
So the new hook is **never noisier than the old one in a repository with no stranded branches**, and
strictly louder in one that has them.

### `scripts/tests/…_can_see_a_branch_it_is_not_standing_on.py` — new, 13 tests

**The hook had no tests of its own.** `scripts/tests/` held tests for its two siblings and none for
it. Every test builds its own throwaway repository under `tmp_path`; **none reads the live tree's
state**, which is both charter §7 and the only way these assertions survive a twelve-seat sprint.

⭐ **Run against the OLD hook first, which is the demonstration that matters:**

```
7 failed, 6 passed
FAILED …::test_a_branch_pushed_by_a_session_that_has_ended_is_named
FAILED …::test_the_census_also_runs_from_a_detached_head
FAILED …::test_a_dirty_worktree_does_not_silence_the_origin_census
FAILED …::test_the_hook_finds_its_repository_without_being_told_where_it_is
FAILED …::test_an_unresolvable_origin_main_is_reported_as_unmeasured_not_clean
FAILED …::test_the_hook_writes_nothing_so_no_green_state_can_be_bought
FAILED …::test_the_classification_is_one_process_and_not_a_merge_base_loop
```

The **6 that pass against the old hook are the must-not-punish cases** — a fully merged repository,
an orphan data ref, the recursion guard, a repo with no origin, the preserved HALF A trade, the
timing floor. A test file that reds on everything would prove nothing.

Against the fixed hook: **13 passed in 2.97 s.**

### Mutation testing — 8 single-site mutations, all in scratch copies

⛔ The live tree was never mutated. Each run copies the hook, applies one edit, points a copy of the
test file at it, and runs pytest out of `/tmp`.

| mutation | result | caught by (first) |
|---|---|---|
| *baseline* (unmutated, redirected) | 13 passed | — |
| M1 put the dirty gate back in front of HALF B | 2 failed | `…dirty_worktree_does_not_silence_the_origin_census` |
| M2 restore `exit 0` on `main` / detached HEAD | 6 failed | `…branch_pushed_by_a_session_that_has_ended_is_named` |
| M3 drop `--contains=<root>` | 3 failed | `…orphan_workflow_data_ref_is_never_reported_as_stranded` |
| M4 swap the AHEAD/BEHIND pair | 1 failed | `…dirty_tree_trade_is_preserved_for_the_sessions_own_branch` |
| M5 render UNMEASURED as clean | 1 failed | `…unresolvable_origin_main_is_reported_as_unmeasured_not_clean` |
| M6 add a cache so the 2nd run goes quiet | 2 failed | `…hook_writes_nothing_so_no_green_state_can_be_bought` |
| M7 swap the classifier for the merge-base loop | 1 failed | `…classification_is_one_process_and_not_a_merge_base_loop` |
| M8 print the count but not the branch names | 5 failed | `…branch_pushed_by_a_session_that_has_ended_is_named` |

**Every mutation is caught, and by the semantically right test.** M6 is the one I care about most: it
is the cheapest way anyone will ever try to quiet this hook.

---

## ⛔ THE ANTI-GAMING TEST, PER CHANGE

*Does this make it EASIER for the loop to end a turn?* **No, for every change. Not one loosens.**

| change | easier to stop? | evidence |
|---|---|---|
| HALF B added at all | ⛔ **HARDER** | fixture S1: `OLD=0 → NEW=2`, naming the branch |
| HALF B not gated on a dirty tree | ⛔ **HARDER** | fixture S2: `OLD=0 → NEW=2` with one untracked file present |
| HALF B runs on `main` too | ⛔ **HARDER** | old hook's line 56 exited unconditionally on `main` |
| HALF B runs on a detached HEAD | ⛔ **HARDER** | old hook's line 55 exited unconditionally |
| unresolvable `origin/main` → UNMEASURED | ⛔ **HARDER** | old: silent exit 0; new: exit 2 |
| robust REPO discovery | ⛔ **HARDER** | the old form is the one that made a sibling silently unreachable in CI |
| HALF A keeps its dirty exit | **unchanged** | fixture S3 dirty: `OLD=0 NEW=0`, identical |
| the suppressed HALF A count is now printed | ⛔ **HARDER** | new line; there was no such report before |
| own branch marked, not excluded from HALF B | **unchanged** | nothing removed from the census |

**Is there any green state that recording can buy?** No. There is no marker file, no cache, no state
directory and no ledger field that quiets it — `test_the_hook_writes_nothing…` asserts the hook
leaves the repository byte-identical and that a second run says what the first run said. **The only
exits are the real ones: merge the branch, delete it, or it becomes an ancestor of `origin/main`.**

⛔ **Note specifically what `_stranded_work` does NOT do here.** S31 is right that it is the only
field that has ever actually recovered a stranded branch, and the hook's guidance tells you to write
it — but writing it **does not decrement the count**. A pointer is how the work gets found later; it
is not the work being merged, and letting it buy silence would rebuild GAP 2 in a nicer costume.

---

## What I could not do, and what it is actually waiting on

- **⛔ I did not merge, delete or touch a single one of the 38 branches.** Charter §1 forbids every
  git write command from a seat, and triaging them is real work with real judgement in it (five
  branches carry 12–22 commits each). **This is waiting on a driver or a dedicated seat, not on the
  outside world** — every read needed is local, already fetched and $0: `git log --oneline
  origin/main..<ref>` and `git diff origin/main...<ref>`.
- **S31's 13 unread seat-cohort branches are still unread.** I widened the instrument; I did not
  read the population. That remains a $0 job for a later seat.
- **I did not re-stamp the selector record**, so `affected_tests.py` still answers `FULL`. Adding a
  test file does not change that, and CLAUDE.md §6 reserves the `PREFLIGHT_FULL=1` run that would
  re-stamp it for publication. Not mine to spend.
- **I did not run `preflight.sh`.** Charter §6: that is the driver's, once, on a settled tree.
- ⚠ **`systems/tests/test_a_claude_hook_is_not_a_dead_pointer.py::test_no_committed_document_names_a_dead_hook`
  is RED on the live tree and it is NOT mine.** K3 flags names that **do not exist** under the scanned
  code directories. When I checked it named two, both from other seats' findings files:
  `s33_pmid_title_coverage.py` — which does not exist in this repository — from `S33-DEPOSIT.md`; and
  `stop-hook-git-check.sh` — a launcher-level user hook, not ours, outside this repository — from
  `S31-ORPHANS.md`. The guard's own message names the fix: the sentence that names an out-of-repo or
  absent file should say so on the same line, which is the convention the four `CODE_CITE_CLEARED`
  phrases encode. K3 scans `.md` documents only, so my `.sh` and `.py` changes add nothing to it, and
  every line of THIS file that names either one carries a clearing phrase. Raising it, not absorbing
  it (CLAUDE.md §6, the cascade rule).
  ⚠ **Re-read minutes later it had grown to four**: two more names, both from `S34-STRANDED.md`, one
  a test file and one a script, neither existing under the scanned directories. I do not repeat them
  here — naming them would add my file to their attribution list, which is the whole trap. **This is
  a convention several concurrent seats are unaware of, not one seat's slip**, and it will keep
  growing for as long as seats write findings files. Worth one line in the sprint charter.

---

## ⭐ THE NUMBER THE DRIVER NEEDS

**With the fix in place the hook names 38 branches carrying 153 unmerged commits, and it fires on the
very next stop.** It was 37/152 when I started; `origin/claude/max-token-usage-sprint-cwihvo` was
pushed during my seat. That is not a hook misbehaving on arrival — **it is a hook doing its job for
the first time on a population that grew from "20+" (2026-08-29) to 38 while it was green.**

Distribution of the 38 by tip date: **17 from 2026-08-28/29** (the archived seat cohort S31 found),
2 from tonight, and 19 spread over 2026-08-06 → 2026-08-25 including the five large ones (22, 20, 20,
13, 12 commits).

⚠ **Expect it at every stop until branches are actually merged or deleted.** That is the design and
it is the point, but the driver should decide deliberately rather than discover it. If the volume is
judged unusable, ⛔ **the honest lever is triaging branches, not softening the hook** — and the
repository's own precedent is that this shape works: `ready-work-at-turn-end.sh`'s header records
that a Stop hook "fired at the end of nearly every turn of a very long session and was acted on
EVERY time, without once being remembered in advance."

---

## Amendment record for the driver

⛔ I did not write these to `amendments.jsonl`. Ready to paste, one per governed path.

```json
{"cycle_id": "SPRINT-2026-09-01/S35-DRIFTGUARD", "utc": "2026-09-01T20:35:00Z", "path": ".claude/hooks/merge-debt-at-turn-end.sh", "what_changed": "Rewrote the hook as two halves. HALF A (this session's own merge debt via origin/main...HEAD) is unchanged including its dirty-tree exit. HALF B is new: one `git for-each-ref --no-merged=origin/main --contains=<root of main>` over already-fetched remote refs, run on every HEAD including `main` and a detached HEAD and NOT gated on worktree cleanliness. Also: robust REPO discovery copied from escalation-debt-at-turn-end.sh; an unresolvable origin/main now reports UNMEASURED and refuses instead of exiting 0; the census prints last-fetch age and, on a shallow clone, that its number is a floor; HALF A's dirty-suppressed count is now printed as a line rather than silently dropped.", "old_value": "Only ref computation was `origin/main...HEAD`; unconditional `exit 0` on branch==main, on detached HEAD, and on `git status --porcelain` non-empty; `REPO=\"${CLAUDE_PROJECT_DIR:-/home/user/Rare-cancers}\"`; silent exit 0 when origin/main did not resolve.", "new_value": "Reproduced against a throwaway fixture: a branch pushed by an ended session drew 0 mentions on any HEAD (OLD exit 0 -> NEW exit 2 naming it); one untracked file flipped exit 2 to exit 0 with merge debt unchanged (OLD 0 -> NEW 2). Classification measured: merge-base loop over 183 refs = 20.0 s against a 15 s configured timeout; for-each-ref --contains form = 0.284 s, identical 37-ref set compared by diff. Whole hook live: 0.67/0.69/0.69 s. Fires immediately on 38 branches / 153 unmerged commits.", "why": "CLAUDE.md §7 calls branch drift a DATA-LOSS BUG and cites this hook as its enforcement, stating it 'has no green state that recording can buy'. S31-ORPHANS found two always-green paths that need no recording at all, and the guarded population grew from '20+' (2026-08-29) to 38 while the hook was green. A branch pushed by a session that has ended was structurally unrepresentable, and nothing else in the repository enumerates origin.", "self_serving_check": "NOT self-serving: every change makes stopping strictly HARDER and none makes it easier, demonstrated per-change in a table in S35-DRIFTGUARD.md and by fixture runs where the old hook exits 0 and the new one exits 2 on the same tree. No bar was re-pinned, no threshold loosened, no exclusion list added (orphan workflow refs fall out structurally via root-containment rather than by name glob). The one thing NOT tightened — HALF A's dirty-tree exit — was kept deliberately and the reason is written into the file: `~/.claude/stop-hook-git-check.sh` (not ours; outside this repository) was RUN on this tree and exits 2 on uncommitted changes today, so the state is already alarmed, and 'MERGE IT now' is the wrong instruction mid-edit. The debt is still printed. No marker file, cache or ledger field can quiet the hook, and a test asserts it leaves the repository byte-identical."}
```

```json
{"cycle_id": "SPRINT-2026-09-01/S35-DRIFTGUARD", "utc": "2026-09-01T20:35:00Z", "path": "scripts/tests/test_the_merge_debt_hook_can_see_a_branch_it_is_not_standing_on.py", "what_changed": "New test file: 13 tests for merge-debt-at-turn-end.sh, which previously had none of its own (scripts/tests/ held tests for its two siblings only). Covers both closed holes as regressions, the four must-not-punish shapes (fully merged repo, orphan workflow data ref, recursion guard, repo with no origin), the preserved HALF A dirty-tree trade in both directions, UNMEASURED-is-not-clean, repository discovery without CLAUDE_PROJECT_DIR, the one-process classification constraint, and an anti-gaming test asserting the hook writes nothing.", "old_value": "No test file for this hook existed.", "new_value": "13 tests. Against the OLD hook: 7 failed / 6 passed, the 6 being the must-not-punish cases. Against the fixed hook: 13 passed in 2.97 s. Mutation-tested with 8 single-site mutations applied to scratch copies (never the live tree): all 8 caught, each by the semantically correct test, baseline green.", "why": "Charter §7 requires a widened guard to be mutation-tested, and CLAUDE.md's record for this family of hooks is that a rule measured by nothing fails silently — which is exactly what happened here. Every test builds its own throwaway repository under tmp_path so none reads the live tree's state, which is both charter §7 and the only way the assertions survive a twelve-seat concurrent sprint.", "self_serving_check": "NOT self-serving: this file only adds constraints. It cannot make any stop easier — it does not run at stop time at all — and it pins the specific properties that a future 'simplification' would remove, including the two that were just found missing. The negative cases were written so the file does not red on true input, which is the failure mode that gets a guard loosened; they are also the 6 that pass against the old hook, so the file is demonstrably not asserting 'everything is broken'."}
```

---

## Ledger rows the driver should write

| field | value |
|---|---|
| `what` | **Triage the 38 branches on `origin` carrying 153 unmerged commits.** The Stop hook now names them at every stop; nothing merges or deletes them. 17 are the 2026-08-28/29 archived seat cohort (1–5 commits each, mostly 1); 5 are large (22/20/20/13/12) and older. Every read is local and $0: `git log --oneline origin/main..<ref>`, `git diff origin/main...<ref>`. |
| `kind` | `hygiene` / `merge-debt` |
| `state` | `ready` — no blocker, no spend, no outside dependency |

| field | value |
|---|---|
| `what` | **The branch census is a LOWER BOUND because the working clone is shallow (grafted 2026-08-04).** 141 remote refs have tips below the graft and cannot be classified as merged or stranded from here; S31's reading of them as "pre-rewrite history, not stranded work" is not supported by a shallow clone. Resolve with one `git fetch --unshallow` (or a deepening fetch) in a context authorised for git writes, then re-run the census. |
| `kind` | `measurement-gap` |
| `state` | `ready` |

| field | value |
|---|---|
| `what` | **`systems_check` K3 is red on the trunk on two sprint findings files** — `s33_pmid_title_coverage.py` named by `S33-DEPOSIT.md`, and `stop-hook-git-check.sh` named by `S31-ORPHANS.md` (a launcher-level user hook that is not ours and lives outside the repository). The guard's message names the fix: the sentence that names an out-of-repo file should say so. Neither is S35's; raised, not absorbed. |
| `kind` | `gate-red` |
| `state` | `ready` |

| field | value |
|---|---|
| `what` | **Give `_stranded_work` a reader.** S31 measured it as the only mechanism that has ever recovered a stranded branch, and `grep` finds it only in `ledger_schema.py`'s allowed-keys list, seven ledger rows and one docstring — recorded, not enforced, the same shape as `subagent_width` before `fanout_is_governed`. `health.py` should count rows carrying it against the branch census the Stop hook now produces. ⛔ It must stay unable to silence the hook. |
| `kind` | `instrumentation` |
| `state` | `ready` |
