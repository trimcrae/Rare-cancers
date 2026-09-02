---
id: DOC-SPRINT-S31-ORPHANS
title: "S31-ORPHANS — the four stranded seat branches, what is still on them, and what would notice the fifth"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S31-ORPHANS — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S31-ORPHANS — three of four branches still carry live work, and nothing in this repository would notice the fifth

**Item(s):** AUT-PD-151 (re-verified), and the branch census behind it
**Owned paths:** `research/autonomy/sprint-2026-09-01/S31-ORPHANS.md` (this file only)
**Refs read:** `HEAD` = `b6397c5666efbf7d6755dfaedabc6a4bef24a8ee`, `origin/main` = `508de213956b27935c7de605718ce032c5cd5a21`
**Started/Finished (UTC):** 2026-09-01T19:41Z / 2026-09-01T20:05Z

## Verdict

**PARTIAL** — all four branches are genuinely unmerged by commit; **one (`seat/s1`) is superseded by
content, ported tonight**; the other three carry work that reproduces at HEAD and is not on main, and
all three patches apply clean to the live tree. **The mechanism answer is the larger result: the
`Stop` hook §7 cites cannot see a seat branch at all, and is additionally silent whenever the tree is
dirty — which is every stop of this sprint.**

---

## ⭐ THE HEADLINE, FIRST

Three things, in the order they matter.

1. **`seat/s3-unscreened-endpoints` is the one branch nothing points at, and its defect is still
   live at HEAD, exactly as measured four days ago: 18 of 25 publication endpoints sit outside the
   register screen.** I re-measured it tonight, not inherited it. It has no ledger row on the trunk
   because **its row-id collided**: `AUT-PD-141` means one thing on `seat/s3` and a completely
   different thing on `main`, and tonight's S7-CHAIN refuted *main's* AUT-PD-141 — which says
   nothing at all about s3's.
2. **`seat/s1-aut-pd-130` is superseded and must NOT be applied.** Tonight's S4-COVERAGE read it,
   ported it, and corrected a real defect in it. Its `claim_coverage.py` functions are byte-identical
   on HEAD. Applying the branch would **revert** that correction.
3. **The reason s1 was rescued and the other three were not is a single ledger field.** `AUT-PD-130`
   carries `_stranded_work` naming the branch and sha; S4-COVERAGE followed it. `seat/s3` has no such
   field anywhere. That field — not the Stop hook — is the only thing in this repository that has
   ever actually recovered a stranded branch.

---

## What I measured

### 1 · Re-verification of the four branches (CLAUDE.md §4 — the row is a claim, not a fact)

`git fetch origin <branch>` for each, then `git merge-base --is-ancestor <sha> origin/main`.
**All four return false. The row is CONFIRMED, not refuted.**

| branch | head sha | head date (UTC) | author | ahead / behind main | `--is-ancestor` |
|---|---|---|---|---|---|
| `seat/s1-aut-pd-130` | `e0847032` | 2026-08-28T23:07:53Z | Claude | 2 / 596 | **false** |
| `seat/s3-unscreened-endpoints` | `88ac1c7c` | 2026-08-28T23:09:54Z | Claude | 1 / 597 | **false** |
| `seat/s4-aut-045` | `c8944f76` | 2026-08-28T23:09:04Z | Claude | 1 / 591 | **false** |
| `seat/s5-retest-blocks` | `da4247dc` | 2026-08-28T22:52:45Z | Claude | 2 / 587 | **false** |

⛔ **Ancestry is not the question the row is really asking, so I checked the DIFF for each** — the
prompt is right that a change can land on main by a different route. Verdicts below are from reading
the content, not the graph. **One of the four turns out to be exactly that case, and only one.**

### 2 · Per branch: what is on it, and is it still worth having

#### `seat/s1-aut-pd-130` — ⛔ **SUPERSEDED. DO NOT APPLY.**

Carries AUT-PD-130's repair: a real `--check` mode for `claim_coverage.py` (a `build_report` /
`render` / `disagreements` refactor so `--write` and `--check` share one producer), a 17-test guard,
and three wiring edits (preflight, `tests.yml`, `regenerate_aso_chain.sh`).

**The discriminating observation:** every function it adds is **byte-identical** on HEAD.

```
def build_report   IDENTICAL      def disagreements  IDENTICAL
def render(        IDENTICAL      STALE_HEADER =     IDENTICAL      def main()  IDENTICAL
```

That is not coincidence, and I did not have to guess — `S4-COVERAGE.md` says so in its own words:
the test file is *"ported from `seat/s1-aut-pd-130` with one real correction"*, and it records
`_stranded_work` as the field that told it to look. Its verdict, which I confirm:
**"the branch `seat/s1-aut-pd-130` can now be considered read and superseded."**

⛔ **AND THE PORT IS BETTER THAN THE BRANCH, WHICH IS WHY APPLYING IT WOULD BE A REGRESSION.** The
branch's clone fixture swapped a symlink to the tracked census artifact for a copy;
`tracked_tree_guard` (AUT-PD-186) landed **2026-08-29 — after that branch** — and refuses it, because
it resolves write paths through symlinks. S4 corrected it. Applying the branch reintroduces a fixture
that writes through a symlink into the live tree.

**Residue: the third wiring edit.** Of s1's three, preflight and `tests.yml` are in tonight's
worktree; `scripts/regenerate_aso_chain.sh` was landed by a live seat **while I was working** (see
§4). Nothing of s1 is owed.

#### `seat/s3-unscreened-endpoints` — ⭐ **STILL VALUABLE. THE ONE WITH NO POINTER ANYWHERE.**

Carries `lint_style.UNSCREENED_ENDPOINT_DECISIONS`: an 18-row record of every graph publication
endpoint the register screen does not read, each row either `not_a_submission_text` (the graph's own
`target_venue` says no outside reader) or `unscreened_debt` (aimed outward, never screened), plus a
guard asserting every endpoint is in one set or the other and in neither twice, plus one
`readability-baseline.json` key.

**Re-measured live at HEAD, 2026-09-01 (not inherited):**

```
lint_style.TARGETS                                    12
graph endpoints resolving to an existing .md          25
        of those, OUTSIDE TARGETS                     18     ← the branch's claim, unchanged
        of those, IN TARGETS                           7
```

The branch's 18 recorded rows match HEAD's 18 exactly — **none in both sets, none missing, none
stale.** Four days on, the defect has neither moved nor been fixed.

⭐ **And the second half of its finding is ALSO live at HEAD.** `fusion-junction-aso-journal-references.md`
**is** in `TARGETS` and **is not** pinned in `readability-baseline.json` (11 pins, 12 targets). That
is the exact state the branch describes: `publish_bar` clause 7's caution half reads
`baseline.get(doc) is None` and returns **PASS reading "(no baseline pinned)"** — a clause that cannot
fail, reported as passing, on a component of the paper at doi 10.32388/VL3LJR.

⛔ **ITS ROW-ID COLLIDES, AND THAT IS WHY IT LOOKS ALREADY-HANDLED WHEN IT IS NOT.**

| ref | `AUT-PD-141` means |
|---|---|
| `origin/main` | "a rebase silently invalidates the archive manifest's provenance" (queued) |
| `seat/s3` | "the register and readability screens are scoped by a hand-typed list, and 18 of 25 publication endpoints are outside it" (done) |

Tonight's `S7-CHAIN` returned **"AUT-PD-141 — REFUTED as written"**. That refutation is of *main's*
row and is correct. **It does not touch s3's finding, which I have just reproduced.** This is
`AUT-PD-171` (the id allocator collides across concurrent sessions) caught in the wild, and the
orphaning is what let it sit undetected: two rows, one id, four days, on refs that never met.

⭐⭐ **THE RATCHET IT WOULD HAVE HELD, IN NUMBERS.** `findings_when_filed` pins each debt row's
count on 2026-08-28 and the guard fails if a count **rises**. Re-measured at HEAD with
`len(lint_style.lint_file(p)['findings'])`:

| document | pinned | now | Δ |
|---|---|---|---|
| `degrader/nr4a3-degrader-paper.md` | 1170 | **1176** | **+6** |
| `program/emc-treatment-roadmap.md` | 112 | **115** | **+3** |
| `fusion-partner/emc-fusion-partner-stratification.md` | 188 | **189** | **+1** |
| `neoantigen/fusion-junction-neoantigen-paper.md` | 107 | **108** | **+1** |
| the other 11 debt rows | — | — | 0 |

**Eleven findings of register debt were added to four outward-aimed manuscripts in four days with
nothing noticing.** That is the cost of this branch being orphaned, stated as a measurement rather
than as a worry. ⚠ Two of the four (`emc-treatment-roadmap.md`, `fusion-junction-neoantigen-paper.md`)
are being edited **tonight** and are in the current `git status`; the other two drifted on main.

⚠ **This is also the one correction the patch needs before it lands** — see §"sequencing".

#### `seat/s4-aut-045` — ⭐ **STILL VALUABLE. Not superseded; main and the live worktree both still carry the stale row.**

Carries an AUT-045 re-test: the `RT-MONOVALENT` route's `best_next_action` had said *"write down the
selectivity requirement"* since the graph was created on 2026-08-05, and that action was **done on
2026-08-07** (REQ-MONO-1/2/3, `selectivity-requirement-sizing.md` §2). The row therefore re-derived a
discharged action for three weeks. The branch retires `BLK-UNSIZED-REQUIREMENT` from that one
`required_validation` slot, replaces the next action with a $0 trace, and moves `last_verified`.

**The discriminating observation — three refs, same field:**

| ref | `state.last_verified` | `next.blocked_on` | `best_next_action` |
|---|---|---|---|
| `origin/main` | 2026-08-06 | `['BLK-UNSIZED-REQUIREMENT']` | "Write down the selectivity requirement…" |
| `seat/s4` | 2026-08-28 | `[]` | "Trace whether the covalent sub-form's negative…" |
| **live worktree** | **2026-08-06** | **`['BLK-UNSIZED-REQUIREMENT']`** | **"Write down the selectivity requirement…"** |

**Not superseded. Still stale tonight.**

⭐ **It also carries a genuine new $0 lead** — `research/modalities/nr4a3-monovalent-reach.json`
contains no exposure/RSA/C7 term at all, so whether the covalent negative inherits the defective
exposure criterion is untraced, and that trace decides whether this route's one computed result
stands. That is live-route work (CLAUDE.md §0), not bookkeeping.

⚠ **It touches `systems/graph/routes.json`, which two seats are editing tonight — and the collision
does not happen.** Measured, not assumed: tonight's worktree hunks in that file are **all eleven**
inside `RT-TRABECTEDIN` (lines ~1725–1815); s4's are inside `RT-MONOVALENT` (lines ~1373–1425).
Disjoint, and `git apply --check` confirms clean.

#### `seat/s5-retest-blocks` — **VALUABLE BUT SMALL. A CI re-read main never got.**

Two `research/modalities/` prechecks re-run from CI egress. Most of the diff is timing noise
(`seconds` fields) and a regenerated `_generated_utc`. **One real content change:**

```
nr4a3-thiol-environment.json  →  ★_part_A_known_answer_precheck
   PMC6389863   was: UNREACHABLE (tunnel 403)   now: 200, 154,073 bytes
   n_reachable_in_this_run   0  →  1
   verdict  REFERENCE_DATABASE_EXISTS_BUT_UNREAD  →  REFERENCE_READ
   pkad over http/https      403 / tunnel-403   →   404 / 404
```

Main still carries the 2026-08-07 `REFERENCE_DATABASE_EXISTS_BUT_UNREAD` / `n_reachable: 0` state,
and `git log origin/main --since=2026-08-27` on both files is **empty** — nothing has re-run them.
So this converts a sandbox-proxy silence into a real reading, which is precisely what CLAUDE.md §4's
*"an absent reading is not a reading of absence"* asks for.

⚠ **The `403 → 404` on pkad is a finding, not noise.** From an unblocked network the database URL
returns **404**, which is a statement about the endpoint rather than about our proxy. It weakens the
"reference database exists and is reachable" half. Keep it at that strength; do not let the
`REFERENCE_READ` verdict beside it round it up.

### 3 · The census — the whole space, not just the four

`git fetch --filter=blob:none --no-tags origin '+refs/heads/*:refs/remotes/origin/*'`, then
`merge-base --is-ancestor` against `origin/main` for every ref.

⛔ **The raw number is misleading and I am not reporting it as the answer.** 184 of 300 non-main
branches are "not an ancestor of main" — but `git merge-base origin/main <branch>` returns **empty**
for 133 of them: they share **no common ancestor at all** with today's main. Those are a pre-rewrite
history (last commits 2026-06-24 → 2026-08-03), not unmerged work. Counting their
"commits ahead" would have manufactured a 372,965-commit figure out of a history rewrite.

**The honest split:**

| class | branches | note |
|---|---|---|
| merged into `origin/main` | 116 | fine |
| **no common ancestor with main** | **133** | pre-rewrite history, ≤ 2026-08-03. Not stranded work. |
| **workflow data refs** | **14** | `*-cache`, `email-outbox`, `figure-renders` — never merge **by design** |
| ⛔ **genuinely stranded: share history, carry unmerged commits** | **37** | **157 commits** |
| total non-main | 300 | |

**The 2026-08-29 census said "20+". The current number is 37 branches / 157 commits.** It has grown.

⭐⭐ **AND THE SEAT-BRANCH COHORT IS NOT FOUR, IT IS SEVENTEEN.** Of the 37, seventeen were pushed on
2026-08-28/29 and carry 1–5 commits each — the same shape, the same two days, the same cause:

```
2026-08-29   5  cyc0073-d4ccfde4-work            2026-08-28   2  seat/s5-retest-blocks
2026-08-29   3  claude/aut-pd-130-s4-CYC-0074    2026-08-28   2  seat/s1-aut-pd-130
2026-08-29   2  claude/aut071-s1-CYC-0074        2026-08-28   1  seat/s4-aut-045
2026-08-29   1  claude/s76-sgk1                  2026-08-28   1  seat/s3-unscreened-endpoints
2026-08-29   1  claude/aut-pd-148-s5-CYC-0074    2026-08-28   1  s3/aut-pd-031-line-citations-…
2026-08-29   1  claude/aut-pd-147-s3-CYC-0074    2026-08-28   1  s1-aut-pd-050-unscored-rows
2026-08-29   1  claude/aut-pd-145-s2-CYC-0074    2026-08-28   1  aut-pd-058-deepen-ledger-history
2026-09-01   1  claude/s24-threshold-calibration 2026-08-28   1  aut-pd-052-ci-autonomy-tests
                                                 2026-08-28   1  aut-pd-037-ledger-serialization
                                                 2026-08-28   1  aut-pd-036-ls-files-scope
```

**AUT-PD-151 named four. There are thirteen more of exactly the same kind, and the row has never
mentioned them.** ⚠ I have read the content of the four the row names; **the other thirteen are
UNREAD** — that is an honest unknown, not a claim they are empty, and it is a $0 read for a later
seat. `origin/claude/s24-threshold-calibration` (2026-09-01) is **tonight's** and is the fifth
already happening.

⚠ Also unmerged and older, likely worth a separate look, not opened here: `claude/aws-budget-storage-shutdown-iq8oh7`
(22), `claude/gcc-nat-emc-aso-aq0eba` (20), `claude/best-paper-submission-tqa0cn` (20),
`claude/emc-symptom-treatment-742257` (13), `claude/preprint-host-unaffiliated-srzofd` (12).

### 4 · ⛔ An incident I caused, reported in full

**I ran `pytest research/manuscripts/tests/test_the_census_artifact_and_the_guard_corpus_are_a_pair.py`
in the shared tree. `tracked_tree_guard` failed reporting `M scripts/regenerate_aso_chain.sh`. I read
that as my test's doing and restored the file from `HEAD` — destroying about 90 seconds of another
seat's live work.** I then noticed the hunk cited *"1.79 / 1.83 / 1.91 s, measured 2026-09-01"* —
figures a test file ported from a 2026-08-28 branch cannot contain, and which appear verbatim in
tonight's `scripts/preflight.sh:778`. I had captured the diff before reverting (the guard's own
message says to), so I re-applied it with `patch(1)` and verified the result **byte-identical** to
what I had captured, mode `755` preserved. **`git diff` on that path is now exactly what it was.**

Three things follow, and the third is the one worth keeping:

1. **My error:** charter §6 says run the linter or test *scoped to your change*. My change is a
   findings file. I had no business running a suite in a twelve-seat tree.
2. **The tree is fine.** Verified by byte comparison, not by assertion.
3. ⭐ **`tracked_tree_guard` mis-attributes concurrent edits.** It compares a tree snapshot across a
   pytest session and names the delta *"the test run CHANGED tracked files"*. In a concurrent tree
   that sentence is **false whenever another seat writes during the run**, and it is phrased with
   enough certainty to make a reader revert someone else's work — which is what it made me do. The
   guard is right to fire; its message asserts a cause it cannot know. Ledger row proposed below.

### 5 · ★★ THE MECHANISM: why four branches went unmerged, and what would notice the fifth

**Proximate cause** (from `S21-UNSCORED.md`, and consistent with all four head timestamps falling
inside 17 minutes): the driver session that owned these seats was **archived mid-landing-loop** on
2026-08-28. The seats had pushed; the driver never merged.

**Why nothing caught it since — `merge-debt-at-turn-end.sh`, read line by line:**

```bash
BRANCH=$(git branch --show-current);  [ -z "$BRANCH" ] && exit 0;  [ "$BRANCH" = "main" ] && exit 0
git rev-parse --verify -q origin/main  || exit 0
read -r BEHIND AHEAD < <(git rev-list --left-right --count origin/main...HEAD)
[ "${AHEAD:-0}" -eq 0 ] && exit 0
if [ -n "$(git status --porcelain)" ]; then exit 0; fi     # ← dirty tree = silence
```

⛔ **GAP 1 — IT MEASURES `HEAD`, SO IT CAN ONLY SEE THE BRANCH THE STOPPING SESSION IS SITTING ON.**
`origin/main...HEAD` is this checkout's branch. A branch pushed by a *different* session is not
`HEAD` anywhere; once that session ends there is no stop for it to fire on. **The hook guards the
session's own merge debt. It has no concept of a branch on `origin` at all** — it never runs
`for-each-ref`, never runs `ls-remote`, and by its own comment deliberately never fetches. **Four
seat branches are precisely the case it cannot represent.**

⛔ **GAP 2 — A DIRTY TREE SILENCES IT COMPLETELY, AND THAT IS THIS SPRINT'S NORMAL STATE.** Measured
just now: `git status --porcelain | wc -l` = **36**. The hook exits 0 at every stop tonight. The
comment explains the choice (`stop-hook-git-check.sh`, not ours and in no repository directory —
it is a user-level harness hook in `~/.claude/` — already fires on uncommitted changes, and two
warnings for one state teaches skimming) and that reasoning is sound for a solo session — but in a
twelve-seat tree the tree is *never* clean, so the merge-debt hook is **unconditionally off for the
entire sprint**, which is exactly the window in which the most branches get created.

⛔ **GAP 3 — NOTHING ELSE SCANS `origin`.** I grepped every `.py`, `.sh` and `.yml`: the only
`for-each-ref`/`ls-remote` uses are `aso_archive_manifest.py` (asks which refs contain *one* sha) and
workflows probing for their own cache branch. **No instrument in this repository enumerates branches
and asks which carry unmerged work.** The 2026-08-29 census that produced the "20+" figure was run by
hand, by a session, once — and the number has since grown to 37 with nothing reporting it.

★★ **WHAT ACTUALLY RESCUED ONE OF THE FOUR, AND IT WAS NOT A HOOK.** The `_stranded_work` ledger
field. Seven rows carry it:

| rows carrying `_stranded_work` | branch named | outcome |
|---|---|---|
| `AUT-PD-130` | `seat/s1-aut-pd-130` | ⭐ **S4-COVERAGE followed it tonight and ported the work.** |
| `AUT-045` | `seat/s4-aut-045` | pointer intact; row `queued`, so no cycle was ever offered it |
| `AUT-007`, `AUT-008`, `AUT-011`, `AUT-016` | `seat/s5-retest-blocks` | same |
| `AUT-PD-133` | `null` — records that its seat pushed nothing | correct negative, working as intended |
| **— none —** | **`seat/s3-unscreened-endpoints`** | ⛔ **no pointer anywhere on the trunk** |

**That is the whole story in one table.** The pointer works — when it exists *and* the row it hangs
on is reachable by a cycle. s1 had both. s4 and s5 had the pointer but their rows sat in the 68
unscored rows S21 found. **s3 had neither, because its row-id collided with a different row already
on main, so writing `_stranded_work` onto "AUT-PD-141" would have attached it to the wrong defect.**

★ **What would notice the fifth, in the order I would build it** (⛔ none of these is mine to write —
each touches a path I do not own):

1. **Widen the Stop hook from `HEAD` to `origin/*`.** It already fires once per stop and already has
   the right prose. One `git for-each-ref refs/remotes/origin` plus `merge-base --is-ancestor`,
   excluding `*-cache`/`email-outbox`/`figure-renders` and refs with no common ancestor, reports
   "N branches on origin carry unmerged commits" from the last-known refs — **no fetch, so it stays
   fast and cannot fail the turn on a network hiccup**, exactly as its comment requires.
2. **Drop the dirty-tree early-exit for the `origin/*` half only.** GAP 2 is defensible for the
   session's own debt and indefensible for other sessions' branches: a dirty tree says nothing about
   whether `seat/s3` is merged. Keep the exit for the `HEAD` half; the two warnings are then about
   two genuinely different states.
3. **Make `_stranded_work` a required field on any row whose seat pushed a branch**, and have
   `health.py` count rows carrying it against branches on `origin` matching a seat pattern. **The
   field is the mechanism that demonstrably worked; today nothing writes it and nothing reads it
   except a human eye** — `grep -rn _stranded_work` finds it in `ledger_schema.py`'s allowed-keys
   list, in seven ledger rows, and in one test docstring. That is the same shape as `subagent_width`
   before `fanout_is_governed`: recorded, not enforced.
4. **Give the id allocator a session discriminator** (`AUT-PD-171` / `AUT-PD-097` / `AUT-PD-122`,
   already open and already this sprint's S1-IDS). s3's collision is what made its work invisible
   *and* what made tonight's refutation of a different row look like it had covered it. **This is
   not a bookkeeping defect — it is how a real finding got read as already-handled.**

---

## What I changed

**Nothing outside my one owned path.** No git write command was run. `git fetch` (ref-only, and
explicitly authorised in my prompt) and `git apply --check` (read-only) are the only two commands
that touched anything under `.git`, and neither creates, moves or deletes a local branch.

One file outside my paths was reverted and then restored byte-identically inside a ~90-second
window — `scripts/regenerate_aso_chain.sh`, fully reported in §4 above. Its current `git diff` is
exactly what it was before I touched it.

**Patches written to my scratchpad** (`/tmp/claude-0/-home-user-Rare-cancers/e71cf460-51bb-5657-a314-50a7b993acba/scratchpad/`).
All four were tested with `git apply --check` against the live worktree and **all four apply clean**:

| patch | touches | lines | verdict |
|---|---|---|---|
| `s4-routes-RT-MONOVALENT.patch` | `systems/graph/routes.json` **only** | 59 | clean |
| `s5-precheck-rereads.patch` | `research/modalities/cys-chemoproteomics-precheck.json`, `research/modalities/nr4a3-thiol-environment.json` | 143 | clean |
| `s3-unscreened-endpoints.patch` | `research/manuscripts/lint_style.py`, `lint_readability.py`, `readability-baseline.json` | 270 | clean |
| `s3-guard-test.patch` | `research/manuscripts/tests/test_every_publication_endpoint_is_style_screened_or_recorded.py` (new file) | 311 | clean |
| `AUT-PD-130-third-wiring-edit.patch` | `scripts/regenerate_aso_chain.sh` — **already applied by a live seat; kept only as the evidence record for §4** | 24 | n/a |

⛔ **No patch for `seat/s1` — it is superseded and applying it would revert AUT-PD-186's correction.**
⛔ **No patch includes `research/autonomy/research-ledger.json`.** All four branches modify it and it
is unownable this sprint (charter §2). Every ledger change is proposed as a row below instead.
⛔ **No patch includes `systems/views/*`.** s4's two view files are **generated**; a hand-edit fails
the build. The driver regenerates after applying the graph patch.

---

## ⛔ Conflict analysis and sequencing — per branch, plainly

**The general answer: none of the three patches conflicts textually with tonight's work, and I
verified that rather than assuming it.** The one real hazard is a stale pin, not a merge conflict.

| branch | could it revert tonight's work? | sequence |
|---|---|---|
| `seat/s1` | ⛔ **YES — do not apply.** It would reintroduce the symlinked fixture `tracked_tree_guard` (AUT-PD-186) refuses. | **Drop it.** Mark the branch read and superseded. |
| `seat/s4` | **No.** Tonight's routes.json hunks are all in `RT-TRABECTEDIN`; s4's are all in `RT-MONOVALENT`. Disjoint, `apply --check` clean. | Apply **after** the trabectedin seat's edits settle, then **regenerate `systems/views/`** — never hand-apply the two view hunks. Then `lint_consistency` + the systems-model gate. |
| `seat/s5` | **No.** Nothing tonight touches either file; main has not re-run them since 2026-08-07. | Apply any time. Lowest risk of the three. |
| `seat/s3` | **No textual conflict** — `apply --check` clean, and `lint_style.py` / `lint_readability.py` / the baseline are untouched tonight. ⚠ **But four of its 15 pins are now stale and the guard would go red on true input.** | ⛔ **Apply LAST, after tonight's prose edits are committed, and re-measure `findings_when_filed` from the settled tree before committing.** |

⛔ **THE ONE THING THAT MUST NOT BE DONE SILENTLY.** s3's four risen pins (`+6`, `+3`, `+1`, `+1`)
are the ratchet catching real register drift. **Re-pinning them is the correct act only if it is a
deliberate, recorded one** — it accepts eleven new findings as the new floor, which is the laundering
shape CLAUDE.md rule 1.2 exists for. Two of the four rises are tonight's own edits, so the honest
sequence is: land tonight's prose, re-measure, and record *in the same commit* that the pins moved
and by how much. **A blanket re-pin folded into a merge would erase the only evidence that the
branch being orphaned cost anything.**

⚠ Two of the three patches are derived from `origin/main`, while the tree is at `HEAD` (5 ahead).
They apply clean to `HEAD` — checked, not assumed — but if the driver merges main first, re-check.

---

## What I could not do, and what it is actually waiting on

- **Merging anything.** Correctly so: charter §1. The patches are ready and tested; this is a driver
  act, and AUT-PD-151's own text already says the s3 merge is a driver's job because of the row
  collision.
- **Writing the ledger rows.** Charter §2 — proposed below.
- **Building the `origin/*` half of the Stop hook.** `.claude/hooks/merge-debt-at-turn-end.sh` is not
  my path. It is ~15 lines of `for-each-ref` and is **not blocked on anything** — no network, no
  spend, no decision. It needs an owner, not a permission.
- **Reading the other thirteen 2026-08-28/29 branches.** Not blocked — it is a $0 read I ran out of
  turn for after the four I was asked for. Named above so the next seat does not have to re-census.
- ⛔ **Nothing here is waiting on trimcrae.** No §3 trigger applies: no spend, nothing outward-facing,
  no goal change. Every item is a gate a seat or the driver can resolve.

---

## Ledger rows the driver should write

| id | `what` (proposed) | `kind` | `state` |
|---|---|---|---|
| `AUT-PD-151` (update) | ⭐ RE-VERIFIED 2026-09-01 at `508de2139`: all four still unmerged. **`seat/s1` is SUPERSEDED** — S4-COVERAGE ported it tonight with a correction (AUT-PD-186); applying it would regress. The other three carry work that reproduces at HEAD, and clean patches exist. ⛔ **The row undercounts: 37 branches on `origin` carry 157 unmerged commits, 17 of them the same 2026-08-28/29 seat cohort.** | `process_defect` | `in_progress` |
| new | ⛔ THE MERGE-DEBT `Stop` HOOK CANNOT SEE A SEAT BRANCH, AND A DIRTY TREE SILENCES IT ENTIRELY. It measures `origin/main...HEAD` — the stopping session's own branch — so a branch pushed by a session that has ended is unrepresentable; and `git status --porcelain` non-empty exits 0, which is every stop of a concurrent sprint (36 entries, measured 2026-09-01). Nothing else in the repo enumerates `origin`. Fix: an `origin/*` half using `for-each-ref` + `merge-base --is-ancestor`, no fetch, excluding cache refs and no-common-ancestor refs, not gated on tree cleanliness. | `process_defect` | `queued` |
| new | ⛔ `_stranded_work` IS THE ONLY MECHANISM THAT HAS EVER RECOVERED A STRANDED BRANCH, AND NOTHING WRITES OR READS IT. `seat/s1` was rescued tonight because `AUT-PD-130` carried it; `seat/s3` was not, because it carries none. It appears only in `ledger_schema.py`'s allowed-keys list, 7 ledger rows and one test docstring — recorded, not enforced, the `subagent_width` shape. Make it required for any row whose seat pushed a branch and have `health.py` reconcile it against `origin`. | `process_defect` | `queued` |
| new | ⛔ `AUT-PD-141` NAMES TWO DIFFERENT DEFECTS ON TWO REFS, AND THE COLLISION MADE A LIVE FINDING LOOK HANDLED. On `main` it is the archive-manifest rebase row (refuted by S7-CHAIN tonight); on `seat/s3` it is the 18-of-25 unscreened-endpoints row, which **reproduces exactly at HEAD**. A reader seeing "AUT-PD-141 REFUTED" would conclude s3's work was covered. Live instance of `AUT-PD-171`. Needs a distinct id for s3's finding at merge time. | `process_defect` | `queued` |
| new | ⛔ `tracked_tree_guard` ASSERTS A CAUSE IT CANNOT KNOW. Its message — *"the test run CHANGED tracked files that it did not find changed"* — is false whenever another seat writes during the session, and it is phrased confidently enough to make a reader revert someone else's work. It did, 2026-09-01T19:52Z (S31-ORPHANS §4; restored byte-identically). Fire unchanged; reword to "tracked files changed DURING this run — this run, or a concurrent writer" and say to inspect before reverting. | `process_defect` | `queued` |
| `AUT-045` (update) | RE-TEST CONFIRMED and the fix is patch-ready: `RT-MONOVALENT.next.best_next_action` still re-derives an action discharged 2026-08-07, on both `main` and the live worktree. Clean patch at `s4-routes-RT-MONOVALENT.patch`; regenerate `systems/views/` after. Carries a live $0 lead: `nr4a3-monovalent-reach.json` has no exposure/RSA/C7 term. | `fetch` | `queued` |
| `AUT-007` / `AUT-008` / `AUT-011` / `AUT-016` (update) | The `seat/s5` re-reads are patch-ready and main has not re-run these files since 2026-08-07. Content: PMC6389863 reachable from CI (200, 154,073 B) → `n_reachable` 0→1, verdict `REFERENCE_DATABASE_EXISTS_BUT_UNREAD` → `REFERENCE_READ`. ⚠ pkad now returns **404** from an unblocked network — an endpoint statement, not a proxy one; do not let the verdict beside it round that up. | `fetch` | `queued` |
| new | ⭐ THIRTEEN MORE BRANCHES FROM THE SAME TWO DAYS ARE UNREAD. Beyond AUT-PD-151's four: `cyc0073-d4ccfde4-work` (5), `claude/aut-pd-130-s4-CYC-0074` (3), `claude/aut071-s1-CYC-0074` (2), and ten more at 1 commit each. Contents **UNKNOWN** — not a claim they are empty. A $0 read. | `process_defect` | `queued` |
