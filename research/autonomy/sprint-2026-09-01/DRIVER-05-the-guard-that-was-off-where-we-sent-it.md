---
id: DOC-SPRINT-DRIVER-05-WORKTREE-BLIND-HOOK
title: "The stall guard exited 0 without looking in every linked worktree — the one environment the archive-manifest ordering requires"
level: L3
kind: incident
status: live
purpose: "Record a Stop hook that could not run where this repository sends sessions, the discriminating observation that separated it from a merge regression, the test that binds the fix, and the governance hole that let a bar be edited undeclared."
scope: "Two hooks and one guard tuple, fixed 2026-09-02. Says nothing about whether a real stall was ever missed in the main checkout — that is recorded as UNMEASURED and is not recoverable from the artifacts kept."
audience: [autonomous research agents, maintainers]
date: 2026-09-02
last_verified: 2026-09-02
---

# DRIVER-05 — the stall guard was off in the one environment this repository *requires*

**2026-09-02, driver seat.** Found while merging round 3 to `main`; fixed the same hour. Every number
below was read from a command run in this session.

---

## 1 · ⛔⛔ The finding

`.claude/hooks/promised-work-at-turn-end.sh` — the `Stop` hook that refuses a turn which promises work,
moves no HEAD and prints no in-flight board — **exited 0 without looking, in every linked git worktree.**

The mechanism, in one line: in a linked worktree `.git` is a ~50-byte file holding `gitdir: <path>`,
not a directory. The hook's state path was

```sh
STATE_DIR="${REPO}/.git/emc-hooks"
mkdir -p "$STATE_DIR" 2>/dev/null || exit 0
```

`mkdir -p` under a *file* fails with `ENOTDIR`, and the line's own `|| exit 0` converted that into a
clean exit. **rc=0, empty stderr — indistinguishable from a turn with nothing to answer for.**

⭐ **The hook already knew.** Eleven lines above, the repo-finding loop reads

```sh
if [ -d "$cand/.git" ] || git -C "$cand" rev-parse --git-dir >/dev/null 2>&1; then
```

— the `||` branch exists *precisely because* the directory test fails in a worktree. The state path
then hardcoded the form the loop had just worked around. One function of one file, two lines apart,
disagreeing about what `.git` is.

## 2 · ★ Why this is not an edge case: the repository mandates the environment

`aso_archive_manifest.py --check-archive` refuses outright unless
`git_tree_is_clean_apart_from_this_manifest` holds. The manifest can therefore be regenerated **only**
in a pristine detached worktree at a pushed HEAD — an ordering applied **five times in this session
alone**, and the subject of DRIVER-03, where a missed regeneration reddened CI on every branch for
hours.

So the repository's own deposit discipline sends a session into the one environment where its stall
guard is off. The guard was not weak there; it was **absent, and silent about it**.

## 3 · ⭐ How it surfaced — from the test side, which had no `|| exit 0` to hide it

A default `./scripts/preflight.sh` run inside the merge worktree came back:

```
14 failed, 1059 passed in 62.35s
PREFLIGHT FAILED -- do not commit.
```

All fourteen were one file, `scripts/tests/test_a_promise_with_no_commit_stops_the_turn.py`, and the
first failure named the mechanism outright:

```
NotADirectoryError: [Errno 20] Not a directory:
  '/tmp/.../scratchpad/mm2/.git/emc-hooks'
```

⛔ **The discriminating observation, run both ways rather than argued.** The byte-identical file
(`cmp` → IDENTICAL) passed **14/14** in the ordinary checkout and failed **14/14** in the linked
worktree. That is what separated "my merge broke a suite" from "this suite cannot run here", and it
is why the merge was pushed rather than unpicked. Every other gate in that run — `lint_consistency`,
`systems_check`, citation provenance, the generated-artifact reproductions, the receipt-width census
— reported OK.

⚠ **And the harness's own exit code lied in the safe direction, which is worth recording.** The
background job was reported "completed (exit code 0)"; the compound command's status was the trailing
`echo`'s. The truth was in the artifact — `EXIT=1`, written by that echo — which is CLAUDE.md §6's
"wait on an artifact, not a process", holding for *reading* a result as much as for waiting on one.

## 4 · The fix

| file | change | scope chosen | why that scope |
|---|---|---|---|
| `promised-work-at-turn-end.sh` | `STATE_DIR` from `git rev-parse --absolute-git-dir` | **per-worktree** | the file holds the PREVIOUS HEAD, and HEAD is per-worktree — one shared baseline would make a commit in one worktree read as a stall in another |
| `merge-debt-at-turn-end.sh` | `FETCH_HEAD` via `git rev-parse --git-common-dir` | **shared** | one fetch updates one FETCH_HEAD for every worktree |

In an ordinary checkout `--absolute-git-dir` resolves to `<repo>/.git`, so the state path is
byte-identical to the one it replaces and **no baseline is lost**.

The second defect was found by grepping every hook for `.git/` once the first was root-caused, rather
than waiting for it to be paid for separately. Its symptom was milder and the same shape: the `-f`
test simply fails, so the fetch age reads `unknown` permanently — not a wrong number, a degraded
reading that looks exactly like a repository nobody has fetched in.

## 5 · ⭐ The test that binds it, and its mutation evidence taken from history

`test_the_hook_still_fires_inside_a_linked_worktree` builds a **real** linked worktree, asserts
`.git` is genuinely a file there (a worktree that handed back a directory would pass for the wrong
reason), copies in the **working-tree** hook, and asserts a stall is still refused.

⛔ **The other fourteen tests pass against the broken hook.** They all run in the ordinary checkout,
where `--absolute-git-dir` and `${REPO}/.git` are the same string. This one test is the only thing in
the file that can tell fixed from broken — that asymmetry is the point of it.

★ **Its mutation is the real pre-fix code, not a synthetic one.** Run before the fix was copied in,
against the hook *as committed at HEAD*, it returned exactly the defect:

```
AssertionError: the hook did not refuse a stall inside a linked worktree, where `.git` is a file —
rc=0, stderr=''.
```

Then, with the working-tree hook copied in: **15 passed in 5.14s**. No live file was mutated to get
that evidence, which is the §6 rule the 13-inverted-claims incident bought.

## 6 · ⭐⭐ The governance hole underneath it

`amendment_guard.GOVERNED` listed `.claude/skills/**` and **not** `.claude/hooks/**`. So
*instructions a session may or may not load* were protected, while *the bars the harness runs whether
or not anyone remembers* were free to edit undeclared.

This is the same one-of-a-pair shape the tuple's own comments already record twice — `priority-weights.json`
governed while `priority.py` was not; the weights governed while `admissibility.py` was not. And the
evidence that people already felt the gap: **two sessions declared hook edits in `amendments.jsonl`
voluntarily** (S35-DRIFTGUARD, and the merge-debt edit earlier the same day), each reasoning in its
own entry that a Stop hook is a bar and the guard should have required it. Compliance by good manners
is the state `subagent_width` was in when it governed nothing.

`.claude/hooks/**` is now on the tuple. **It is a tightening and only a tightening** — one glob added,
none removed — and it binds this session first: the two hook edits above became governed in the same
hour they were made, and are declared with their `self_serving_check` answered. Verified by running
`is_governed` over both hooks (True), the test file (True), the guard itself (True) and a control,
`research/compute/pricing.md` (False). No test pinned the tuple's contents.

## 7 · ⚠ What this does **not** claim

- It does not claim the hook ever missed a real stall **in the main checkout**. There is no evidence
  either way, and the state file cannot be read backwards for one. What is measured is that the guard
  could not run in a worktree.
- It does not claim the other three hooks are clean. Grepped for `.git`,
  `ready-work-at-turn-end.sh` and `no-detached-background.py` have **no** hits;
  `escalation-debt-at-turn-end.sh:57` has exactly one, and it is the *correct* form — the same
  `[ -d "$cand/.git" ] || git -C "$cand" rev-parse --git-dir` repo-finding loop, with no hardcoded
  path built underneath it. ⚠ That is a grep, not an audit, and none of the three has a worktree
  test, so "no hits" means no instance of *this* defect rather than a guard shown to run there.
- **UNMEASURED: 1** — whether any past turn ended inside a worktree with a promise unrefused. Not
  recoverable from the artifacts we keep.
