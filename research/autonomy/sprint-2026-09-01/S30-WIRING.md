---
id: DOC-SPRINT-S30-WIRING
title: "S30-WIRING — the census check, wired into the three places that can refuse a commit"
level: L3
kind: memo
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
purpose: "The findings record of sprint seat S30-WIRING — what it measured, what it changed, and what it could not do. Written before the seat returned, so a seat that dies costs its own work and nothing else."
scope: "One seat of the 2026-09-01 sprint, bounded by the owned-paths list in its own prompt. It reports; it does not decide what lands."
last_verified: 2026-09-01
---

# S30-WIRING — a `--check` that nothing called now runs in the commit loop, in CI, and in the chain

**Item(s):** AUT-PD-130 (the wiring half S4-COVERAGE could not take)
**Owned paths:** `scripts/preflight.sh` (one row), `.github/workflows/tests.yml` (one step),
`scripts/regenerate_aso_chain.sh` (one row's verify command),
`research/manuscripts/claim-coverage.json` (regenerated), this file
**Started (UTC):** 2026-09-01T19:44Z   **Finished (UTC):** 2026-09-01T20:02Z

## Verdict

**FIXED** — S4's three RED wiring assertions are green; the file is `17 passed in 16.46s`. The census
row costs **1.85 s** in the gate (three standalone runs: 1.79 / 1.83 / 1.91 s), which confirms S4's
1.8 s to the second decimal, and it **stays in the default tier** — the reasoning is measured below.

⚠ **The regenerated census is a snapshot of a moving tree and is NOT final.** See
[§ The census is a snapshot](#the-census-is-a-snapshot-the-driver-must-re-run---check-on-the-settled-tree).

---

## What I measured

### 1 · The specification: S4's test, RED, before anything was changed

```
$ python3 -m pytest research/manuscripts/tests/test_the_census_artifact_and_the_guard_corpus_are_a_pair.py -q
F........EEEEFFF.                                                        [100%]
4 failed, 9 passed, 2 warnings, 4 errors in 6.64s
```

⚠ **Four failures and four errors, not the three the hand-off predicted — and the extra five are one
cause, not five.** The `clone` fixture asserts that the census reproduces *before* any mutation
("the clone does not reproduce before any mutation, so nothing below measures a mutation"), and the
committed artifact was stale from concurrent manuscript edits. That erred the four clone-scoped tests
at setup and failed `test_check_passes_on_the_committed_artifact`. All five cleared on the `--write`
in step 4; none of them was a wiring defect.

**The three wiring failures, verbatim** — this is the specification, written by the seat that built
the guard:

```
test_the_commit_loop_runs_the_census_check
  the census is not a row in preflight's generated-artifact gate, so a guard-pattern widening can
  again reach `main` and redden it on a clean tree. THE EDIT: add
      "research/manuscripts/claim_coverage.py|claim coverage census|--check" \
  to the `for g in ...` list in scripts/preflight.sh … Measured cost of the row: ~1.8 s.

test_ci_runs_the_census_check
  CI does not run the census check. THE EDIT: add
  `python3 research/manuscripts/claim_coverage.py --check` to the generated-artifact step of
  .github/workflows/tests.yml, beside the other `--check` producers.

test_the_regeneration_chain_verifies_the_census
  the regeneration chain writes the census but never verifies it. THE EDIT: give the
  'claim coverage census' row in scripts/regenerate_aso_chain.sh its verify command,
  `python3 $MAN/claim_coverage.py --check`, in the third field that every other row uses.
```

### 2 · ⛔ THE COST OF THE PREFLIGHT ROW, MEASURED RATHER THAN INHERITED

The seat prompt is right that a figure added to the commit loop tonight needs stating. Three
standalone runs on the live tree, and one run through preflight's own parse-and-execute line:

```
run1 rc=1 1.91s      gen=[research/manuscripts/claim_coverage.py]
run2 rc=1 1.79s      label=[claim coverage census] mode=[--check]
run3 rc=1 1.83s         OK   claim coverage census
                     row cost in the gate: 1.85s
```

**S4's 1.8 s is confirmed.** For the context the prompt asked for, I timed **every pre-existing row
of the same gate**, each exactly as `preflight.sh` invokes it:

| s | rc | generator |
|---|---|---|
| 0.79 | 0 | `research/manuscripts/submission_tables.py` |
| 0.05 | 0 | `research/manuscripts/submission_citations.py` |
| 0.11 | 0 | `research/manuscripts/submission_metrics.py` |
| 0.38 | 0 | `research/manuscripts/aso_sequence_manifest.py` |
| 0.04 | 0 | `research/manuscripts/aso_journal_tables.py` |
| 0.57 | 0 | `research/modalities/aso_offtarget_duplex_energy.py` |
| 0.11 | 0 | `research/manuscripts/submission_packet.py` |
| 0.04 | 0 | `research/manuscripts/vaccine_path_tables.py` |
| **1.48** | **1** | `research/manuscripts/aso_archive_manifest.py --check-archive` ⚠ **red, and not mine — see below** |
| 0.04 | 0 | `research/modalities/emc_condensate_report.py` |
| 0.70 | 0 | `research/modalities/atr_hrd_sarcoma_series.py` |
| 0.30 | 0 | `research/modalities/single_slot_identity.py` |
| 0.04 | 0 | `research/modalities/instrument_census.py` |
| 0.08 | 0 | `scripts/trigger_scan.py` |
| 0.03 | 0 | `scripts/citation_debt.py` |
| 0.04 | 0 | `scripts/news_match.py` |
| **4.80** | | **TOTAL of the sixteen pre-existing rows** |

★ **So the honest statement is stronger than "it is only 1.8 s": the new row is the MOST EXPENSIVE
SINGLE ROW IN THE GATE, and it is 38% of what the other sixteen cost put together.**

**It still belongs in the default tier, and the argument is not that 1.8 s is small.** It is:

1. **Against the loop's real cost it is small, and the honest framing is the stricter one.**
   [`S6-COMMITLOOP.md`](./S6-COMMITLOOP.md) measured the default loop tonight — **that file owns
   those figures and I did not re-measure them.** Against its quiet-box total the row is **~0.35%**;
   against its **fast-gate tier**, which is where this row actually lands and which is the part a
   session thinks of as cheap, it is **~2.3%**. ⚠ I am quoting the second number rather than the
   first because the first flatters the change: almost the whole loop is gate 13, and hiding a new
   row behind gate 13's size is an argument that would justify any row at all.
2. **The alternative placement is not "cheaper", it is "after the push".** The comparison itself is
   not new: it has existed since 2026-08-22 inside `test_claim_coverage_has_not_regressed`, in the
   manuscripts suite — opt-in locally behind `PREFLIGHT_TESTS=1`, and in CI only after the commit
   that ships the stale artifact. Moving it out of the default tier restores exactly the state
   AUT-PD-130 exists to end.
3. **It is the only row in this gate whose pair spans two directories.** `claim-coverage.json`
   harvests its guard patterns from `research/manuscripts/tests/`, so widening a guard's regex moves
   `covered` with **no manuscript byte touched**. `83aede1` did exactly that, `covered` went
   99 → 101, and `main` was red on a clean tree for ~35 minutes, during which every sentence
   witnessed only by the red module scored a false BLIND in the ablation harness.
4. **It has already paid for itself twice in one hour, and a third time for me.** S4 measured two
   independent stalings in ten minutes; my own first run of S4's test found a third, in 1.8 s.

⛔ **What I am NOT claiming:** any figure for the commit loop itself — that is
[`S6-COMMITLOOP.md`](./S6-COMMITLOOP.md)'s measurement and its number to own — nor that adding
1.85 s is free. It is a real 1.85 s on every commit, stated so the next session can re-decide with
the number in front of it rather than re-derive it.

### 3 · Each edit, checked against the thing it touches

```
$ bash -n scripts/preflight.sh                                          BASH -N CLEAN
$ python3 -c "yaml.safe_load(open('.github/workflows/tests.yml'))"       YAML PARSE OK; jobs: ['gates', 'pytest']
    STEP FOUND: The claim-coverage census reproduces from the live corpus
              | python3 research/manuscripts/claim_coverage.py --check
$ bash -n scripts/regenerate_aso_chain.sh                               BASH -N CLEAN
$ bash scripts/regenerate_aso_chain.sh --list | grep "claim coverage"    17:claim coverage census
$ bash scripts/regenerate_aso_chain.sh --check --only "claim coverage"
    == claim coverage census
       STALE                    <- a VERDICT. Before this edit the row printed
                                   "⚠ NOT VERIFIED -- this producer has no --check mode"
```

⭐ **The `STALE` there is the row working, not a defect**: the census genuinely was stale at that
moment, and the whole point of the third edit is that the chain can now say so.

### 4 · The census: red, regenerated, green — and what moved

```
$ python3 research/manuscripts/claim_coverage.py --check        rc=1
claim-coverage.json is stale — it is not what the live census computes:
  … 40 field disagreements across 11 of the 27 censused documents …
$ python3 research/manuscripts/claim_coverage.py --write        1.92s, "wrote research/manuscripts/claim-coverage.json"
$ python3 research/manuscripts/claim_coverage.py --check        rc=0
claim-coverage.json reproduces from the live census (27 documents)
```

⭐ **Which fields moved is the load-bearing observation, and it is the one that says no bar was
relaxed:**

```
$ grep -o "\.[a-z_]*: committed" <the --check output> | sort | uniq -c
     11 .sentences        11 .uncovered        9 .with_a_number        9 .uncovered_with_a_number
$ grep -E "\.covered: committed" <the --check output>
NONE — no document's `covered` count moved
```

`git diff` on the artifact agrees: **40 insertions, 40 deletions, and the only keys touched are
those same four count fields.** So this staleness is **manuscript growth from concurrent seats, not
a guard-pattern widening** — no `covered` moved, therefore **no coverage floor moved and none was
lowered.**

The eleven documents that grew:

```
care-delivery/emc-icdo-9231-classification.md          neoantigen/emc-vaccine-development-path.md
degrader/nr4a3-degrader-paper.md                       neoantigen/fusion-junction-neoantigen-paper.md
fusion-output/nr4a3-fusion-transcriptional-output.md   neoantigen/hla-coverage-emc.md
methods-record/closed-routes-negative-record.md        program/emc-treatment-roadmap.md
methods-record/degrader-methods-failure-record.md      surface-targets/emc-surface-target-landscape.md
modality-census/cancer-modality-census.md
```

⛔ **And my own three edits cannot have moved the census.** The census reads the 27 manuscripts and
the modules under `research/manuscripts/tests/`; `claim_coverage.py` mentions `tests.yml` only inside
a comment (line 811) and never opens it, and `grep -n "subprocess\|git " claim_coverage.py` returns
nothing, so it reads no git history either. None of `preflight.sh`, `tests.yml` or
`regenerate_aso_chain.sh` is in its input set.

### 5 · S4's test, green

```
$ python3 -m pytest research/manuscripts/tests/test_the_census_artifact_and_the_guard_corpus_are_a_pair.py -q
.................                                                        [100%]
17 passed, 3 warnings in 16.46s
```

⛔ **The test was not touched.** `git status --porcelain` on it is clean. The three assertions were
satisfied by moving the repository to what they describe, which is the only direction this
repository allows.

---

## What I changed

| path | what |
|---|---|
| `scripts/preflight.sh` | **one row** added to the `for g in` list of the generated-artifacts gate, plus the comment block the file's convention requires — carrying the measured cost, the `83aede1` incident, and why the placement (not the comparison) is the new thing. `bash -n` clean. Nothing else in the file touched; the seat that landed changes minutes ago (`c9583ea41`) is undisturbed — its work was already committed and my `git diff` is 16 added lines in one hunk. |
| `.github/workflows/tests.yml` | **one added step**, `The claim-coverage census reproduces from the live corpus`, in the `gates` job immediately after the ASO deposit-artifact step. YAML parses; both jobs still resolve. Nothing else touched. |
| `scripts/regenerate_aso_chain.sh` | the `claim coverage census` row's third field, `""` → `"python3 $MAN/claim_coverage.py --check"`. ⚠ **The row had moved again while I worked — 214 → 304 → 311** — so it was located by content, never by line number. |
| `research/manuscripts/claim-coverage.json` | regenerated (`--write`). 40 insertions / 40 deletions, four count fields only, no `covered`, no floor. **A snapshot — see below.** |
| `research/autonomy/sprint-2026-09-01/S30-WIRING.md` | this file |

⛔ Nothing outside that list was touched. No git write command was run. I did not open
`claim_coverage.py`, `claim_ablation.py`, S4's test file, or any manuscript for writing.

### ⚠ One correction I made to my own comment, recorded rather than tidied away

The first draft of the preflight comment said the new row cost "1.8 s against ~2.4 s for the other
fifteen rows put together". **I had not measured that number** — it was a placeholder shaped like a
fact, which is precisely the failure CLAUDE.md §4 names. I measured the sixteen rows (4.80 s, table
above) and corrected the comment before running anything else. The corrected sentence is a weaker
claim for the row, not a stronger one: it now says the row is the gate's most expensive.

### ⚠ Why the CI edit is its own step rather than a line in the existing one

S4's text says "beside the other `--check` producers", and the assertion only requires the string to
be in the file. I put it in its own step because the existing step is named **"ASO deposit artifacts
reproduce from their generators"** and the census is not an ASO deposit artifact — it covers all 27
censused manuscripts. The `gates` job exists precisely so that *"which KIND of failure occurred is
readable from the check name instead of from a traceback twenty minutes in"*; burying a whole-corpus
census under a step named for the ASO deposit would spend that. The prompt's "ONE ADDED STEP" reads
the same way. **If the driver disagrees, moving it is a one-line change and the assertion holds
either way.**

---

## What I could not do, and what it is actually waiting on

⛔ Nothing in this seat's scope is blocked. Three things I **found** are somebody else's, each with
a path and a reading rather than a guess:

1. ### ⛔ `aso_archive_manifest.py --check-archive` IS RED ON THIS TREE, AND THE DRIVER WILL HIT IT AT PREFLIGHT

   ```
   $ python3 research/manuscripts/aso_archive_manifest.py --check-archive
   STALE: the archive inventory would change — re-run without --check          rc=1
   ```

   This is a **pre-existing row of the same gate my row joins**, and it was red before my first
   edit — it is row 9 of the timing table above, measured before I touched anything. It is not
   staleness of the kind `--check-archive` was written to tolerate (that form already excludes
   `git_revision`), so *the inventory itself would change*: some seat regenerated a hashed artifact
   without re-running the manifest, which is exactly the ordering `regenerate_aso_chain.sh` exists
   to enforce. **Waiting on:** whoever owns the manifest / the driver's settled-tree regeneration.
   ⚠ Not mine to run — the manifest hashes files eleven seats are still writing, so regenerating it
   now produces a deposit describing files that will move again.

2. ### ⛔ `lint_style.py` HAS ONE ERROR, IN A MANUSCRIPT A SEAT IS WRITING RIGHT NOW

   ```
   $ python3 research/manuscripts/lint_style.py
   research/manuscripts/neoantigen/emc-vaccine-development-path.md:655:
     [bold-midsentence] bold inside a sentence: **less**
   lint_style: 1 ERROR across 14 file(s)
   ```

   That document is one of the eleven that grew under me during this seat. **Waiting on:** whoever
   owns `emc-vaccine-development-path.md`. One word's emphasis; not mine to edit.

3. ### ⛔ `test_no_guard_can_silently_not_run` IS RED ON COMMITTED CODE, AND ONE OFFENDER IS S4'S NEW FILE

   Found because it is one of the guards that reads `tests.yml`, so I ran it against my CI edit.
   It is **not** about my edit — it is an AST scan over the test corpus, and I edited no test file.

   ```
   $ python3 -m pytest research/manuscripts/tests/test_no_guard_can_silently_not_run.py -q
   FAILED …::test_every_remaining_skip_in_the_deposit_suite_is_a_decision_somebody_took
   these guards can decline to run and nothing at the site records that anyone decided they may:
       research/manuscripts/tests/test_the_census_artifact_and_the_guard_corpus_are_a_pair.py:279
       research/manuscripts/tests/test_the_deposit_the_papers_cite_is_current.py:270
   ```

   Both files are **clean in `git status`** — i.e. committed, so this red exists on HEAD independent
   of every uncommitted change in the tree. `git log -1` on each names `062a48ae1` ("sprint wave 1
   lands"). The census-pair offender is `pytest.skip(f"no sentence of {paper} yields a selective
   excerpt")` in `_selective_excerpt`, which needs `'SKIP IS DELIBERATE'` or `'NOT IN CI'` beside it
   with its reason — the excerpt search genuinely can come up empty, so it is a decision somebody
   should record rather than a guard evaporating. **Waiting on:** the driver, or a seat that owns
   `**/tests/**` under an amendment record. ⛔ **I did not fix it: it is a governed path, it is S4's
   file, and the two remaining seconds of my scope are not worth an amendment record for a change
   that is not mine to judge.**

⚠ **And the fourth thing is not a finding, it is the sprint's weather.** `tracked_tree_guard.
assert_tree_unchanged` reddened **three** of my pytest invocations, each naming a different file I
have never opened — `research/modalities/hla_coverage.py` + `systems/graph/artifacts.json`, then
`research/manuscripts/surface-targets/emc-surface-target-landscape.md`, then
`.claude/skills/repo-gates/SKILL.md`. It raises in `pytest_sessionfinish` and **eats the failure
list**, so `tail` shows a traceback and nothing else. The reading survives at the **head** of the
output (the `.....F....` progress line), which is how the 17-passed result above was read. Recorded
so nobody later reads one of those tracebacks as evidence about this change.

---

## The census is a snapshot — the driver must re-run `--check` on the settled tree

⛔ **The `claim-coverage.json` in this change is NOT final and must not be presented as such.**

I regenerated it at **2026-09-01T19:55Z** and it was green one second later. It was **still green at
20:00Z**, my last reading before returning:

```
$ python3 research/manuscripts/claim_coverage.py --check          # 2026-09-01T20:00Z
claim-coverage.json reproduces from the live census (27 documents)          rc=0
```

⛔ **That is a statement about the tree at 20:00Z and nothing more, and it must not be read as "the
census is done".** Eleven seats are writing manuscripts, and the census reads all 27 of them plus the
whole guard corpus. S4 measured two independent stalings in ten minutes from this same cause; my own
first run of S4's test found a third. **Green at 20:00Z is evidence that the check works, not that
the artifact the driver will commit is current.**

**The habit this whole item is about, in two lines, for the driver, on the settled tree:**

```
python3 research/manuscripts/claim_coverage.py --check     # 1.85 s
python3 research/manuscripts/claim_coverage.py --write     # 1.92 s, if the above is red
```

⭐ **And from this commit forward the driver does not have to remember**: the row I added to
`preflight.sh` refuses the commit, so a stale census cannot reach `main` unnoticed. That is the whole
of AUT-PD-130, and it is what "wired" means.

⚠ **One consequence worth stating plainly, because it is a real cost and not a free win:** every
commit made while manuscripts are moving will now go red on this row until the author re-runs
`--write`. That is the gate binding, not misfiring — but on a night like tonight it will bind often,
and a session that meets it should regenerate rather than reach for a way around it.

---

## Amendment record for the driver

**None needed.** `**/tests/**` is governed and I touched no test file — `git status --porcelain`
over `research/manuscripts/tests/` is clean of anything I did. The three assertions went green by
changing the repository to match the specification, never by changing the specification.

---

## Ledger rows the driver should write

⛔ A seat may not edit `research/autonomy/research-ledger.json` (AUT-PD-171). Proposed:

**AUT-PD-130** — `state: done`. S4 left it `in_progress` pending exactly these three edits; all three
are made and its test file is `17 passed`. Closing evidence: the `--check` now runs in the commit
loop (`scripts/preflight.sh`, 1.85 s measured), in CI (`.github/workflows/tests.yml`, its own named
step in the `gates` job), and in the regeneration chain (`scripts/regenerate_aso_chain.sh`, which
printed `NOT VERIFIED` for this row until tonight). ⚠ Carry into the closing note that the row is the
**most expensive single row in that gate** (1.85 s against 4.80 s for the sixteen pre-existing rows
together) — a later session deciding the commit loop is too slow should meet that number, not
rediscover it. Also update `_stranded_work` on this row: `seat/s1-aut-pd-130` is now **read and
superseded**, per S4.

**NEW ROW — proposed.** *"⛔ `aso_archive_manifest.py --check-archive` IS RED ON THE TRUNK'S WORKING
TREE — THE INVENTORY ITSELF WOULD CHANGE."* `kind: process_defect`, `state: queued`,
`cost_class: free`. Measured 2026-09-01T19:47Z, before this seat edited anything:
`STALE: the archive inventory would change — re-run without --check`, rc=1. `--check-archive` already
excludes the two repository-state fields, so this is not the commit-advances-git_revision false
positive that mode was built to remove — a hashed artifact moved without the manifest being re-run.
WHAT TO DO: on the settled tree, `python3 research/manuscripts/aso_archive_manifest.py` and commit,
or find which artifact moved out of chain order. ⚠ **It is red in the driver's own preflight path**,
so the driver will meet it regardless; filed so it is not mistaken for fallout from the census row
that now sits eight lines above it in the same gate.

**NEW ROW — proposed.** *"⚠ `test_every_remaining_skip_in_the_deposit_suite_is_a_decision_somebody_
took` IS RED ON COMMITTED CODE, ON TWO UNMARKED SKIPS."* `kind: process_defect`, `state: queued`,
`cost_class: free`. Measured 2026-09-01: two offenders, both in files clean in `git status` and both
last touched by `062a48ae1` —
`test_the_census_artifact_and_the_guard_corpus_are_a_pair.py:279` (`pytest.skip("no sentence of
{paper} yields a selective excerpt")`) and `test_the_deposit_the_papers_cite_is_current.py:270`.
WHAT TO DO: write `'SKIP IS DELIBERATE'` beside each with its reason, or turn it into a `pytest.fail`
— governed path, so it needs an amendment record. ⚠ **The guard is correct and the skips are
probably both legitimate**; what is missing is the recorded decision, which is the whole point of
that guard.

**NEW ROW — proposed, small.** *"⚠ `lint_style.py`: ONE `bold-midsentence` ERROR IN
`emc-vaccine-development-path.md:655`."* `kind: process_defect`, `state: queued`,
`cost_class: free`. It `serves` the neoantigen publication. Measured 2026-09-01 in a document a seat
was actively growing this evening, so it may already be fixed; it is one word's emphasis (`**less**`)
and the fix is to unbold it.

---

## In flight at hand-off

**Nothing in flight.** No GPU, no CI dispatch, no subagent, no background job. Every command in this
file ran to completion in the foreground and its output is quoted above.
