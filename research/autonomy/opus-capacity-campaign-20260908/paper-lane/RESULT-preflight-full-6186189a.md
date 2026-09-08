---
id: DOC-OPUS-CAMPAIGN-PREFLIGHT-RESULT-6186189A
title: "PREFLIGHT_FULL result for the ATR candidate commit 6186189a"
level: L4
kind: memo
status: live
purpose: >
  Record the actual outcome of the authorised CI PREFLIGHT_FULL run against the ATR candidate
  commit, across every section of the published log, and name exactly what failed.
scope: >
  L4. A result record. It fixes nothing, weakens no gate, classifies no failure as excusable, and
  claims no green state.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# ⛔ PREFLIGHT_FULL FAILED on `6186189a` — run 34250066740

**The run is complete and its conclusion is `failure`.** Started 2026-09-08T16:16:42Z, finished
17:22:38Z, one attempt. No duplicate run was dispatched and no polling worker was used.

- **Pinned sha:** `6186189abf5291fabdd45819ae42474eecb5ee74`.
- **Published log:** `research/autonomy/preflight-logs/6186189abf5291fabdd45819ae42474eecb5ee74.log`
  on `main` at `b4ff832bb75116e70d2f8431ef688e8dcc73d7a7`, Git blob
  `a2f8c55f9a1b5250d33a2eac2d7b3a482b1af9da`, **304,602 bytes / 992 lines**, sha256
  `ca79eba2fdf4df35e72d46ff6f4e93777a869baffcf38c264dd6024cc0df3c3f`. ⭐ Retrieved and hashed here;
  it matches the sole collector's retained copy exactly. The log ends
  `PREFLIGHT FAILED -- do not commit.` and `EXIT=1`.
- ⛔ **NO RECEIPT EXISTS.** `research/autonomy/preflight-receipts/6186189a….json` is absent on `main`,
  correctly: `record_bar_evidence.py` refuses a passing receipt when the log's `EXIT=` marker is not
  0. **`publish_bar`'s `preflight_full_green` clause has no evidence for this commit.**

## ⚠ CORRECTION, 2026-09-08 — this record was wrong, and materially so

**The first version of this record reported only "11 failed, 1780 passed, 1 skipped" and concluded
that "not one failure is in a manuscript, a producer or a paper guard; all eleven are campaign-record
repo-state findings". That conclusion is FALSE, and the count was one suite of three.** It was
written from the tail of the log rather than from the whole of it. The 11/1780/1 figure is the
**pure-logic and systems** suite alone.

⭐ **The superseded version is retained as history, not deleted.** It is the file exactly as committed
at **`6cd29f876b11492e01f4e2ea10752e1bf0dbc4f4`** — Git blob
`df990561132c1ed2df3846acefb0865c3f9693bb`, 4,070 bytes, sha256
`65ab5f85d9e72be2e71a8b7eb81b6f808b10b830632000d6e068264675c8eebc`, verified here by reading it back
out of Git. This dated correction supersedes it in place, so the record carries one document id and
no duplicate active document is created. The source full CI log is likewise unchanged: blob
`a2f8c55f9a1b5250d33a2eac2d7b3a482b1af9da`, 304,602 bytes, `ca79eba2…3c3f`.

The published log runs **three** pytest suites and three separate gate failures precede them. The
corrected reading is below, against this exact log. The original failure evidence and the earlier
observations are preserved rather than replaced: the eleven systems findings remain part of the
record, they are simply **not the only failures**.

## What actually failed, by section of the log

**Three gate failures, before any suite:**

| log line | gate | result |
|---:|---|---|
| 10 | systems model — `systems/systems_check.py --check` | **FAILED** |
| 12 | EMC systems map — `research/manuscripts/emc_systems_map_check.py --check` | **FAILED** |
| 693 | `research/manuscripts/lint_citations.py` | **FAILED** |

⚠ `lint_consistency` (line 7) and the R1–R5 claim-strength gate (line 13) were **OK** in this run;
this record does not turn those into failures any more than it excuses the ones above.

**Three pytest suites — 28 failures and 5 errors in total:**

| log lines | suite | result |
|---:|---|---|
| 851 → 878 | modalities, FULL (`PREFLIGHT_FULL=1`) | **8 failed**, 8,394 passed, 52 skipped, 25 warnings, 527.40s |
| 891 → 918 | manuscripts (endpoints, systems map, pooling, submission citations) | **9 failed**, 1,954 passed, 3 skipped, 24 warnings, **5 errors**, 3,051.16s |
| 934 → 961 | pure-logic suites, the selector's contract, the loop's instruments, the systems model | **11 failed**, 1,780 passed, 1 skipped, 1 warning, 20 subtests passed, 118.19s |

### Modalities, 8 failed — named in the log as NEW and not the known dependency gap

`test_instrument_register_prefix.py::test_the_migration_is_idempotent_over_the_repo`;
`test_lint_citations.py` × 5 (`test_a_ledgered_identifier_stays_green`,
`test_and_that_control_can_actually_pass_when_the_arxiv_id_is_anchored`,
`test_and_that_control_can_actually_pass_when_the_identifier_is_anchored`,
`test_the_ledger_does_not_anchor_itself`, `test_the_repository_currently_passes`);
`test_nr4a3_fusion_targets_figures.py::test_check_mode_reports_ok_on_a_clean_tree` and
`::test_the_provenance_stamp_matches_the_committed_artifacts`.

⛔ The log's own instruction stands and is not acted on here: a genuine missing-dependency failure
would be traced to its module and added to `sandbox-failure-baseline.txt` **with the reason, in the
same commit** — and **never** added to silence one. Nothing is baselined by this record.

### Manuscripts, 9 failed + 5 errors — the section the first version of this record missed entirely

1. `test_pdf_text_layer_is_orderable.py::test_every_stamped_pdf_renders_the_documents_its_stamp_names`
   — a committed PDF renders a version of its source that is no longer on disk.
2. `test_citation_type_guard.py::test_the_live_tree_is_green_with_no_baseline_and_no_amnesty`.
3. `test_citation_type_guard.py::test_the_guard_is_reached_by_the_gate_that_runs_in_the_commit_loop`
   — gate 6 must be green through the type guard.
4. `test_the_census_artifact_and_the_guard_corpus_are_a_pair.py::test_check_passes_on_the_committed_artifact`
   — the committed census does not reproduce from a live run.
5. `test_line_citations.py::test_no_resolvable_line_citation_points_at_the_wrong_line` — **17** line
   citations in the roadmap point at a line that does not contain the phrase they quote.
6. `test_the_paper_states_what_its_own_claims_depend_on.py::test_claim_coverage_has_not_regressed`.
7. `test_no_guard_can_silently_not_run.py::test_every_remaining_skip_in_the_deposit_suite_is_a_decision_somebody_took`
   — guards that can decline to run with nothing at the site recording that anyone decided they may.
8. `test_the_census_word_covered_survives_ablation.py` for the **ASO journal article** — **2 of 91**
   perturbed sentences changed their number and no witness the census names went red.
9. The same ablation test for the **endpoint** manuscript — **1 of 4** perturbed sentences, same
   failure mode.

**The 5 ERRORS are all one fixture**, `test_the_census_artifact_and_the_guard_corpus_are_a_pair.py`,
each reporting that **the clone does not reproduce before any mutation, so nothing below measures a
mutation**: `test_the_command_line_exits_non_zero_and_says_which_document_moved`,
`test_a_missing_artifact_is_refused`, `test_a_widened_guard_pattern_alone_turns_the_check_red`,
`test_a_guard_that_names_no_censused_document_leaves_the_check_green`,
`test_the_clone_left_the_working_tree_alone`.

⛔ **A manuscripts-suite failure does NOT by itself authorise editing frozen ASO or endpoint
science.** The ASO and endpoint ablation failures are findings about **witness coverage**, and the
endpoint manuscript is parked under its own accepted adverse hold. Neither is reopened here.

### Pure-logic and systems, 11 failed — the section this record originally reported alone

All eleven are repo-state checks tripped by files inside this campaign's own record directory, and
they remain part of the record: `DOC-CLOSED-ROUTES-NEGATIVE-RECORD` claimed by three files (the live
manuscript plus CR1's retained `BEFORE-`/`AFTER-` evidence copies); `MANIFEST.md` missing `scope` and
`audience`; `reports/W51-lint-consistency-coverage.md` linking to a self-anchor no heading makes;
`coverage-scan.json` cited by `reports/W57-graph-vs-artifact-stale-watchers.md` while absent with no
lane claiming it; `acceptor_blast_radius.py` named by `reports/W03b-acceptor-blast-radius.md` while
present in no code directory; and `test_cli_check_exits_zero`, which the others make non-zero.

## What this record does not do

⛔ It applies **no** fix, and it is **not** a classification of which failures are excusable. **Root
owns the classification of every failure above and the smallest legitimate repair**, and any repair
must respect three standing constraints: the campaign's `BEFORE-`/`AFTER-` copies are **retained
evidence**, no gate, guard, test or baseline may be weakened or extended to pass, and no
cited-absent, dead-pointer or skipped-guard finding may be silenced with a clearance phrase.

⛔ No new full CI run is dispatched, no failure amnesty is granted, no frozen paper is reopened, and
no broad repair is inferred from this correction. **Until a green `PREFLIGHT_FULL` receipt exists for
a candidate commit, the final-candidate gate coverage release requires is absent — which is unknown,
not passed.**
