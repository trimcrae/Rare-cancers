---
id: DOC-SPRINT-S37-BRANCH-DEBT
title: "S37-BRANCH-DEBT — the merge-debt hook's eighteen, discharged: thirteen superseded and recorded as such, two merged for content, three recorded as stranded with the measurement that blocks each"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  Give every branch in the merge-debt hook's ancestry-visible set a verdict backed by a reading, and
  either discharge it or record precisely what it waits on, so that "18 branches carrying 94 unmerged
  commits" stops being a warning nobody can act on.
scope: >
  The 18 refs returned by `git for-each-ref --no-merged=origin/main --contains=<root>` on 2026-09-02,
  which is the hook's HALF B. The other 149 unmerged refs are invisible to that ancestry query because
  the clone is shallow and grafted; they were read on the same day in S38-BRANCH-CENSUS.md and are not
  re-derived here.
last_verified: 2026-09-02
---

# S37 — the eighteen branches the merge-debt hook can see, and what happened to each

Read 2026-09-02 by seat `s37-branch-debt`. Every verdict below rests on a reading taken in this
session against `origin/main` as it stood that day, not on the prior census: S38 was written hours
earlier and `main` had moved under three of its verdicts.

The set was enumerated here rather than taken from a prompt:

    ROOT=$(git rev-list --max-parents=0 origin/main | tail -1)
    git for-each-ref --no-merged=origin/main --contains="$ROOT" refs/remotes/origin

**18 refs, 94 commits ahead of `origin/main`.** `--no-merged` alone returns **167**; the other
**149** do not contain `main`'s earliest known commit and are invisible to an ancestry test.

---

## §1 · THE TABLE

`A` superseded by content · `B` empty · `C` worth keeping, merged · `S` stranded, recorded

| ref | commits | verdict | the reading that settles it |
|---|---|---|---|
| `claude/s24-threshold-calibration` | 7 | **A** merged `-s ours` | 3 of 5 files byte-identical on `main`; `vaccine_threshold_calibration.py` is **1118 lines on main against 1040** here, and main's copy carries the `FUSION_EXCLUSIONS` adjudication this branch lacks |
| `cyc0073-d4ccfde4-work` | 5 | **S** recorded | every artifact its receipt calls branch-only is on `main`; only the receipt's own text diverges, and **both sides are richer in different fields** |
| `claude/aut071-s1-CYC-0074` | 2 | **A** merged `-s ours` | the trabectedin JSON S38 called branch-only is on `main`; main's `routes.json` has **12** trabectedin references against **10** |
| `claude/aut-pd-147-s3-CYC-0074` | 1 | **A** merged `-s ours` | 3 paths, 0 absent, 2 identical; the only diff is `research-ledger.json`, Lane 1, where the trunk is authoritative |
| `claude/aut-pd-130-s4-CYC-0074` | 3 | **A** merged `-s ours` | main's `claim_coverage.py` is **867 lines against 782**; the paired test **425 against 394** |
| `seat/s3-unscreened-endpoints` | 1 | **S** merged then **backed out** | the guard is real; its ratchet was pinned 2026-08-28 and **8 documents have drifted past it since**, and both remedies are barred to this seat |
| `seat/s1-aut-pd-130` | 2 | **A** merged `-s ours` | same file set as its sibling; main's `claim_coverage.py` **867 against 678** |
| `claude/nr4a3-gapmer-presubmission-d4vqmp` | 6 | **A** merged `-s ours` | main's ASO article is **4,695 words against 4,579**, and eight days newer — taking this branch would roll the submission back |
| `claude/preprint-host-unaffiliated-srzofd` | 12 | **C** merged (path-scoped) | 5 of its 7 branch-only paths recovered; the 2 build-stamps refused on a measurement |
| `claude/elink-probe-ci-fefnhh` | 2 | **A** merged `-s ours` | both files byte-identical; **861 of 861** added lines on `main` |
| `claude/aso-e13-tissue-expression` | 2 | **A** merged `-s ours` | **11,950 of 11,952** added lines on `main` |
| `claude/best-paper-submission-tqa0cn` | 20 | **C** merged (path-scoped) | 46 paths on 1 ref of 302, including a matcher bug that reported the wrong molecule |
| `claude/emc-symptom-treatment-742257` | 13 | **S** recorded | grafted, run, backed out — `PUB-MORTALITY-MECHANISM` needs four portfolio judgements nobody has made |
| `worktree-agent-ab0b548a575724822` | 1 | **A** merged `-s ours` | **5,451 of 5,452** added lines on `main` |
| `worktree-agent-a8e9ae2f991db8def` | 1 | **B** merged `-s ours` | `git diff --name-only origin/main...ref` returns **nothing**; the branch changes no file |
| `claude/ci-a3b5-lanes` | 10 | **A** merged `-s ours` | its 4 "absent" inputs are `main`'s **gzipped** copies, byte-identical when decompressed |
| `ci-input/tcip-interface-floor-2026-08-07` | 4 | **A** merged `-s ours` | all 4 byte-identical; **80 of 80** added lines on `main` |
| `claude/tcip-effector-stage-ci` | 2 | **A** merged `-s ours` | **5,713 of 5,713** added lines on `main` |

**Thirteen A/B · two C · three S.** Every one of the eighteen is now either an ancestor of `main` or
carries a record naming its branch and tip sha.

⚠ **`seat/s3-unscreened-endpoints` changed verdict during this session, and the gate is why.** It was
merged for content, the full run went red on 11 failures inside the merged module, and it was backed
out. §3a records the numbers. That is a better outcome than the merge would have been — the failures
name exactly what a later session must clear — but it means the branch still holds its work.

---

## §2 · WHY A SUPERSEDED BRANCH WAS MERGED `-s ours` RATHER THAN LEFT OR DELETED

The hook says the only ways past it are to be on `main`, to have nothing ahead of it, or to merge.
**Deleting is not available from this environment** — the remote refuses the delete RPC with a 403,
established earlier the same session — so a branch read and found superseded would otherwise keep
being re-read by every future session, which is the cost this document exists to stop.

`git merge -s ours` records the verdict in `main`'s history and takes **no content**, which is the
property that matters here: for eleven of these thirteen the branch's copy of a shared file is the
OLDER one, and an ordinary merge would regress it. Verified after all thirteen:
`git diff <base> HEAD` is **empty** — thirteen merge commits, zero bytes changed.

⛔ **The two that would have done real damage if merged normally**, both named in their commit
messages: `claude/nr4a3-gapmer-presubmission-d4vqmp` would have rolled the ASO submission manuscript
back eight days and 116 words, and `claude/s24-threshold-calibration` would have removed the
`FUSION_EXCLUSIONS` rule whose absence produced a fabricated calibration — a probe that returned 988
scoreable peptide-allele pairs of which **not one** was a fusion-oncoprotein breakpoint.

★ **This is not a claim that the branches may now be deleted by a rule.** It is a claim that nothing
on them is lost, each with the reading above. Deletion remains a manual act in the GitHub UI; §5
lists which are safe.

---

## §3 · THE TWO MERGED FOR CONTENT, AND THE ONE THAT WAS MERGED AND BACKED OUT

### 3a · `seat/s3-unscreened-endpoints` @ `88ac1c7c3` — merged, run, and BACKED OUT

⛔ **THE VERDICT ON THE BRANCH IS UNCHANGED — the guard is real and worth having — and it still
cannot land today. The gate established that, not a judgement call.** It merged cleanly, the full
run went red on **11 failures, every one inside the merged module**, and the content was reverted.
The branch adds
`research/manuscripts/tests/test_every_publication_endpoint_is_style_screened_or_recorded.py` (305
lines, on **1 ref of 302**, on no path of `main`) and a 210-line endpoint register in
`research/manuscripts/lint_style.py` — 522 lines on `main`, 718 here, so not a rename.

**The defect it guards.** `publish_bar.clause_7_readable_enough_to_review` has two halves. Its
caution-floor half compares against `readability-baseline.json`, which is written from
`lint_style.TARGETS`. For an endpoint absent from `TARGETS` the lookup returns `None` and the clause
returns **PASS reading "no baseline pinned"** — a clause that cannot fail, reported as passing.
Measured 2026-08-28: 25 graph endpoints resolve to a `.md`, 7 were in `TARGETS`, **18 were in
neither `TARGETS` nor any record saying why not**.

⭐ **And the obvious fix was measured and rejected before this one was written**, which is why the
branch was worth taking rather than re-deriving: adding the 18 paths to `TARGETS` returns **2,795
findings, 1,170 from the degrader paper alone**, because several are internal programme documents
whose callout glyphs are correct for their reader. So the guard does not assert that every endpoint
is screened; it asserts that every endpoint has been **decided about**, in a committed record.

⛔ **The ledger conflict was resolved to the trunk, deliberately, and `main` predicted it.**
`AUT-PD-151` says: *"MERGING (2) NAIVELY DESTROYS A LIVE ROW … The TRUNK's `AUT-PD-141` is a
DIFFERENT row … a clean auto-merge would silently overwrite one with the other."* `research-ledger.json`
was the merge's only conflict and was taken from `main` unchanged. Verified after resolution: **390
ledger ids, 0 duplicates**, trunk `AUT-PD-141` subject intact.

#### Why it was backed out — the numbers, which are the useful part

The register was measured on 2026-08-28 at `origin/main` `170314393`. `main` has moved for five days
underneath it, and the guard correctly noticed:

* **`test_a_recorded_debt_may_fall_and_may_not_rise` fails for 8 documents.** Verbatim, for one:
  *"`nr4a3-degrader-paper.md` was pinned at **1170** findings and now measures **1176** … Fix the
  DOCUMENT. Lowering the pinned number to match is the edit this test exists to make visible."*
* **`test_nothing_is_both_screened_and_recorded_as_unscreened` fails** because `main` has since added
  `care-delivery/emc-trial-reachability.md` to `lint_style.TARGETS`, so its recorded row *"has
  outlived its decision"*.
* **`test_the_caution_baseline_covers_every_screened_document` fails** for that same document.

⛔⛔ **BOTH REMEDIES ARE EDITS THIS SEAT MAY NOT MAKE.** *Fix the documents* — but two of the eight
are `dependency/emc-atr-vulnerability-assessment.md` and `care-delivery/emc-trial-reachability.md`,
both pinned under blind review and out of bounds. *Re-pin the numbers* — the edit the test's own
message names as the one it exists to expose, and the "raise a ceiling to land your own test" move
`amendment_guard` refuses. **Landing the guard by weakening it would turn a working ratchet into a
rubber stamp in the same commit that praises it for catching drift.**

⭐ **ONE FINDING SURVIVES THE BACKOUT AND MUST NOT BE LOST WITH IT.**
`emc-trial-reachability.md` is in `TARGETS` **with no readability baseline**, so `publish_bar`
clause 7's caution floor compares against nothing and returns PASS for it **on `main` today**. It
needs no part of this branch to fix — `python3 research/manuscripts/lint_readability.py
--write-baseline` — but it is a bar change on a paper under review, so it is recorded here rather
than taken silently.

### 3b · `claude/preprint-host-unaffiliated-srzofd` @ `06171eeee` — the submission record

Five of its seven branch-only paths recovered: the three PDFs of the **2026-08-21 Research Square
submission of PUB-ASO**, and `scripts/preprint_host_policy_fetch.py` + `scripts/arxiv_route_fetch.py`.

⛔ **The PDFs went into `aso/submitted-2026-08-21/`, not beside the live artifacts, and that was a
measurement too.** Dropped into `aso/` they are swept up by `aso_archive_manifest.py`, whose deposit
inventory globs `aso/*.pdf`: the manifest went **516 → 519 files, 50.7 → 55.5 MiB**, and listed all
three under `documents_with_no_build_stamp`. That silently redefines the **current** deposit of a
paper under live review to include a superseded version of it. The dated subdirectory keeps the
record and leaves the inventory alone — the glob does not recurse — and a `README.md` there says
which is which. Re-measured after the move: `n_files` back to **516**, the only inventory change
being `lint_style.py`'s new bytes, which belong to the deposit legitimately.
PUB-ASO is the one paper CLAUDE.md §3 excludes from the standing publication grant, so a submission
record for it is exactly the class of artifact that must not be dropped silently.

⛔ **The two build-stamps were refused, on a measurement rather than a preference.** A build-stamp is
a currency record — *"this PDF renders these documents at these sha256s"*. Checked against `main`'s
copies of the four sources each names, **3 of 4 are stale**. With the stamps present,
`test_every_stamped_pdf_renders_the_documents_its_stamp_names` **fails** — *"does not say which
artifact it stamps … written by a builder that was not updated"* — because the 2026-08-21 builder
predates the `artifact` key. **1 failed, 40 passed** with them; **41 passed** with the PDFs kept and
the stamps dropped. They remain at `06171eeee` if anyone wants them.

### 3c · `claude/best-paper-submission-tqa0cn` @ `e673afb88` — the largest single loss

**46 paths on 1 ref of 302 and on no path of `main`**: the complete 2026-08-10 review round for five
papers, the five `emc-mtap-prmt5-decline-review-*` seat reports, six analysis scripts with five JSON
results, five literature screens, three test modules, six figure files and two provenance records.
The manuscripts themselves were never lost and are untouched here.

⭐ **It also carried a scientific-correctness fix that never reached the trunk.**
`research/hypotheses/txgnn_predict.py` matched drug names by substring against a list sorted by
descending score, so it returned the highest-scoring compound *containing* the query. In the
committed artifacts' own `matched` fields: **doxorubicin resolved to 13-deoxydoxorubicin, apatinib to
Lapatinib, ifosfamide to Palifosfamide** — three of 33 queried agents reported against a different
molecule, and the highest-ranked hit of the whole exercise was one of them. `enumerate-drugs.mjs` had
guarded the identical collision since it was written. Safe to take whole: `main`'s copy of that file
is **byte-identical to the branch's merge-base `ce0405f0e`**, so the branch's version is `main`'s
plus the fix.

**Three repairs the recovery needed**, each measured:

1. The review files were written for `research/manuscripts/<name>.md` and `main` has foldered those
   manuscripts. Left at the root their sibling links broke (**12** `K1` errors); moved beside the
   paper each reviews they broke differently (**42**), every `../` link then one level short. 42
   links were rewritten by basename resolution against the real tree, **0 unresolved**.
   `systems_check`: 12 ERROR → 42 ERROR → **0 ERROR**.
2. `emc_fet_frame_and_composition.py` read `research/manuscripts/lit-targets-aso-verify.json`, which
   `main` keeps under `aso/`. Repointed; its suite went **8 errors → 0**. The artifact then
   reproduced with two provenance lines changed and **no scientific value moved**.
3. The recovered review response names `ACH-001519` — H-EMC-SS, identity **DISPUTED** for
   **not carrying the hallmark fusion on the curated record** — which gate 3's `O4`
   requires every tracked file to classify. Classified `unaffected` on the document's own words:
   *"nothing here reads it as EMC evidence, and it is named only as a reason a row was weakened."*

---

## §4 · THE TWO RECORDED AS STRANDED, AND WHAT EACH WAITS ON

Both were **read, attempted locally, run, and backed out** — neither is "probably nothing", and
`main` is unchanged by either attempt.

### 4a · `claude/emc-symptom-treatment-742257` @ `59bb15cbe` — recorded on `AUT-091-e71cf460-f664c8c1`

A row for this recovery already existed and is unusually good: it names the branch, the merge-base,
a 53-file verdict split and a five-part order. The graft confirmed its plan and found **three
blockers it did not yet name**, now written onto its `_stranded_work`:

1. ⛔ **Step 2 is not a re-path, it is four portfolio judgements.** The branch's
   `PUB-MORTALITY-MECHANISM` row predates four fields `main`'s `publications.json` now carries on
   **32 of 32** rows: `outcome_potential` (a controlled vocabulary), `outcome_potential_why`,
   `patient_path` and `unit`. They grade how far a route family could move a patient outcome. They
   cannot be derived from the branch, and authoring them is **grading a strategy family, not
   recovering lost work** — which is where this seat stopped.
2. ⚠ **Step 4 has a verification prerequisite.** With the branch's inputs against `main`'s registry,
   `test_the_real_inputs_still_resolve_against_the_real_registry` **fails** on two quoted strings,
   the first `masunaga2025_localized`'s `registry_verbatim`. The test names the fork itself: the
   registry figure changed since 2026-08-09, or the string was mistyped. Settle it **before**
   recovering the six `otherCauseDeath` keys, because it is the same numbers.
3. ⚠ **A sixth step is missing from the order.** `test_the_probe_is_actually_wired_into_the_fetch_literature_workflow`
   asserts `scripts/lit_mortality_probe.py` appears in `.github/workflows/fetch-literature.yml`. It
   does not on `main`, and `main` has moved that workflow. Landing the probes without that edit lands
   a red test.

**What the graft measured, so nobody repeats it:** the six `RT-*` rows and `ST-MORTALITY-MECHANISM`
append cleanly (`routes.json` 77 → 83, `strategies.json` 13 → 14); the four fields they lack are
optional, present on only 43–55 of 77 `main` routes. `systems_check` then fails with
`KeyError: 'PUB-MORTALITY-MECHANISM'`. With the graph rows reverted and only the 25 files present,
`systems_check` is **0 ERROR** and the four recovered test modules run **68 passed, 2 failed** — the
two named above and nothing else.

### 4b · `cyc0073-d4ccfde4-work` @ `9780481ad` — the code landed, the record diverged

⭐ **Its own receipt says the work is stranded, and that sentence is now false.** The branch's
`research/autonomy/receipts/CYC-0073-d4ccfde4.json` reads: *"THIS CYCLE'S WORK IS ON BRANCH
`cyc0073-d4ccfde4-work`, GATED GREEN … BUT NOT ON `main`. The successor's first job is to merge that
branch."* Checked one by one, every artifact it names **is** on `main` today —
`research/autonomy/push_guard.py`, `research/autonomy/contract_check.py`, `.githooks/pre-push`,
`test_the_unscored_population_can_only_shrink.py`, `.claude` inside `systems_check.py`'s `CODE_DIRS`,
and the reconciled `core.hooksPath` block in `scripts/dev-setup.sh` (byte-identical prose on both
sides). **0 of its 16 paths are absent from `main`; absorption is 97 %.**

⛔ **What has not landed is the receipt's own text, and it cannot be settled by taking one side.**
Four fields diverge and **neither copy is a superset**: the branch is longer on `changed`,
`now_queued` and `what_i_got_wrong`; `main` is longer on `subagents`, `_why` and `_corrected`.
A receipt is a historical record of what a cycle did, so overwriting either side loses evidence.
The branch-only text is reproduced verbatim in the appendix below, which makes `main` a home for it
— the thing CLAUDE.md §7 actually requires — without this seat deciding a governed artifact's
canonical wording.

---

## §5 · WHICH BRANCHES ARE SAFE TO DELETE FROM THE GitHub UI

⚠ **Deletion was not attempted.** The remote refuses the delete RPC with a **403** from this
environment, established earlier in this session; nothing below was deleted and none of it is
reported as deleted.

**Safe — merged `-s ours`, nothing on them is absent from `main`, verdict recorded in `main`'s history:**
`claude/s24-threshold-calibration` · `claude/aut071-s1-CYC-0074` · `claude/aut-pd-147-s3-CYC-0074` ·
`claude/aut-pd-130-s4-CYC-0074` · `seat/s1-aut-pd-130` · `claude/nr4a3-gapmer-presubmission-d4vqmp` ·
`claude/elink-probe-ci-fefnhh` · `claude/aso-e13-tissue-expression` ·
`worktree-agent-ab0b548a575724822` · `worktree-agent-a8e9ae2f991db8def` · `claude/ci-a3b5-lanes` ·
`ci-input/tcip-interface-floor-2026-08-07` · `claude/tcip-effector-stage-ci`

**Safe — content merged:** none beyond the `-s ours` set above; the two path-scoped recoveries and
`seat/s3` all still hold content.

⛔ **DO NOT DELETE — content still only on the branch:**
`claude/preprint-host-unaffiliated-srzofd` (two build-stamps, §3b) ·
`claude/best-paper-submission-tqa0cn` (the `txgnn_predict.py` history, and 77 paths not taken) ·
`claude/emc-symptom-treatment-742257` (§4a, everything) ·
`cyc0073-d4ccfde4-work` (the receipt text, §4b) ·
**`seat/s3-unscreened-endpoints` (§3a — merged, reverted, and the only home of the guard).**

---

## §6 · APPENDIX — the `CYC-0073-d4ccfde4` receipt text that exists only on the branch

Reproduced so `main` carries it. Field-level, sentence-level diff against `main`'s copy of the same
receipt; `subagents` is included because it is the field where **`main` is the fuller side**, which is
why neither copy may simply replace the other.

```
### FIELD `changed` — on the branch, not on main (4 sentence-units)
- ⭐ LATER IN THE CYCLE, ALL GATED: seat s1 delivered AUT-PD-144 (push_guard.py + pre-push hook, 21 tests, 12/12 mutants) and seat s2 delivered AUT-PD-146 (contract_check.py, gate 17, which DERIVES what receipt_schema requires by deleting each field and re-running the enforcer — 23 tests, 15/16, the survivor reported by the seat as its own judgement rather than a measurement).
- The trunk was RED and CLAUDE.md §1 made fixing it this cycle's job: `.claude` was missing from systems_check.py's CODE_DIRS, so a tracked, executable, wired hook read as a DEAD POINTER (6 tests, 6/6 mutants).
- ⛔⛔ AND AUT-PD-144 WAS SOLVED TWICE CONCURRENTLY — CYC-0074-bdf8c881 built the same guard — with both fixes arming `core.hooksPath` to DIFFERENT directories in the same dev-setup.sh. git honours one, so last-write-wins would have left one fully-tested guard permanently inert.
- Reconciled to a single armed path running both guards, taking the trunk's DIRECTORY but s1's PLACEMENT — the landed arming sat BELOW the `--if-needed` early exit that the SessionStart hook runs, so the trunk's own guard was inert on every ordinary session, and only s1's test pinned that.

### FIELD `now_queued` — on the branch, not on main (8 sentence-units)
- ALSO FILED: AUT-PD-160 (the seat/claim-push defect, twice re-allocated through real id collisions) and AUT-PD-161 (the commit loop is slower than the trunk's push interval — 9 gates, 8 push rejections, ~61 minutes, and this cycle's code never reached main by its own push).
- AUT-PD-144 and AUT-PD-146 are closed.
- ⛔ THIS CYCLE'S WORK IS ON BRANCH `cyc0073-d4ccfde4-work`, GATED GREEN (preflight EXIT=0, 655 s, read from the run's own marker) BUT NOT ON `main`.
- The successor's first job is to merge that branch — it carries the trunk-red CODE_DIRS fix, both seats' work and the hooksPath reconciliation, none of which is on the trunk.
- Nothing is lost: every commit is on the branch.
- ⚠ ID CORRECTION: those two rows are AUT-PD-160 and AUT-PD-161.
- They were filed as AUT-PD-154/155, renamed to 158/159, and renamed AGAIN to 160/161 when CYC-0072-1681f3fa landed different rows under 158/159 while this cycle's push was still being refused.
- THREE forced re-allocations for one cycle's two rows, every one caused by push latency rather than by the allocator — which is the substance of AUT-PD-161 itself. `priority.py:merge` refused the duplicated ledger and is what caught the third.

### FIELD `what_i_got_wrong` — on the branch, not on main (9 sentence-units)
- ⛔⛔ (5) THE WORST ONE, AND I REPORTED IT AS DONE BEFORE CHECKING: I said I had committed the hook reconciliation.
- The commit (7731501e3) contained ONE change — the deletion of s1's hook. `git add -- <paths> scripts/git-hooks/pre-push 2>/dev/null` failed wholesale because `git rm` had already removed that path and an unmatched pathspec aborts the entire `git add`; `2>/dev/null` swallowed the error.
- The tree was left STRICTLY WORSE than either starting point: s1's hook deleted and .githooks/pre-push not calling push_guard, so a 312-line mutation-tested guard was orphaned — and it was already on the pushed safety branch.
- ⭐ §6's 'diff the paths you did not touch' catches an EXTRA file; this was the mirror image, three files MISSING, and that check is blind to it.
- What catches it is reading `git diff --cached --name-only` before committing and never suppressing stderr on a staging command.
- ⚠ (6) I twice asserted a mechanism for the slow gate and was wrong twice — history-walking (refuted by arithmetic at ~2.5 s) and then 'no competitor on the second run', which I asserted without checking `ps` while two seats were in fact gating.
- No row was filed on either; the mechanism is recorded as UNKNOWN.
- ⚠ (7) I twice caught myself about to breach the gating rule under push starvation — once by writing a merge-then-push retry loop, once by nearly reasoning a ledger-only merge could not break a gate.
- Both were stopped before running, and AUT-PD-161 records that a starved driver will keep finding such arguments.

### FIELD `subagents` — MAIN is the fuller side, branch is NOT a superset
branch: {"max_concurrent": 2, "total": 2, "_why": "Two seats dispatched concurrently against a governed cap of 5 (autonomy-state.json subagent_width, READ this cycle): s1 on AUT-PD-144, s2 on AUT-PD-146. Each claimed its own row at dispatch under its own worker id. Both delivered branches and finished.", "_corrected": "⛔ FIRST WRITTEN AS 0 AND TRUE AT THE TIME. The receipt is written at step 10 and the se
main  : {"max_concurrent": 2, "total": 2, "_why": "Two seats dispatched concurrently against a governed cap of 5 (autonomy-state.json subagent_width, READ this cycle, not remembered): s1 on AUT-PD-144, s2 on AUT-PD-146. Each claimed its own row at dispatch with claim.py under its own worker id (s1-CYC-0073-d4ccfde4 / s2-CYC-0073-d4ccfde4), so neither item was left being offered to another cycle.", "_corre
```

⚠ **This appendix is a transcript, not a correction.** It does not amend the receipt on `main`, and
whoever reconciles the two should read both copies rather than this extract.
