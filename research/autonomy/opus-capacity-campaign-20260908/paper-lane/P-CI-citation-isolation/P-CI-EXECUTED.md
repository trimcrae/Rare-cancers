# P-CI — citation provenance/type axis isolation, and the seven inherited PMCID narratives

Owner: P-CI (sole exclusive). Date: 2026-09-08. **No commit, no push — the parent integrates.**
Files touched (only these three): `research/manuscripts/lint_citations.py`,
`research/manuscripts/citation-provenance-ledger.json`,
`research/modalities/tests/test_lint_citations.py`.

## 1 · What was changed

**(a) The seven inherited narratives.** Each of the seven `kind: PMCID` cross-form rows carried, in
`verified_by`, the DOI row's own narrative copied verbatim — a sentence describing a 2026-08-27 read
of a **DOI**. Standing in a PMCID row it reads as a check performed on that PMCID, which nobody
performed. Each of the seven now opens with:

> INHERITED FROM THE DOI ROW — NOT A CHECK PERFORMED ON THIS PMCID. Nothing was retrieved for this
> identifier and no fetch product in this repository carries it; the sentence that follows is the
> `verified_by` narrative of the DOI row named in `checked_by`, copied verbatim, and it describes a
> 2026-08-27 read of THAT DOI. Verbatim from the DOI row: …

Nothing else in the ledger changed: 7 lines changed, 244 rows before and after, no status, key,
metadata or class-field edit, and byte formatting (`indent=1`, insertion order) preserved.

**(b) The provenance-control isolation repair.** `lint_citations.check()` returned
`max(provenance_rc, type_rc)` and was the only observable either axis had. With the type guard red
for an unrelated reason — the state of this tree — the wrapper returned `1` for a fabricated
identifier **and** for an anchored one, so every negative control drove a constant.
`provenance_check(prose=None, anchors=None)` now carries the provenance axis alone, `_type_check(prose)`
is the single call site of the type axis, and `check()` remains the production wrapper.

⛔ **Production is unchanged in behaviour.** `check()` still calls `survey()` over the ENTIRE corpus
(one walk, prose handed to both axes), still runs BOTH axes, and still fails if EITHER fails —
`max(provenance_rc, type_rc)`. The missing-ledger short circuit (rc 2, type axis not run) is
preserved exactly as before the split. No skip, no exemption, no rebaseline, no weakening of the
type checks, and `survey()`'s self-exclusion of the ledger (and of the type cache and the sweep
artifact) from anchor scanning is untouched and now additionally pinned by a test.

## 2 · The verification that means something

Controlled fixtures; the type axis is stubbed to a known value so the provenance verdict is
attributable to anchoring rather than to the harness.

| test | what it shows |
| --- | --- |
| `test_fabricated_and_anchored_are_red_and_green_on_the_provenance_axis_whatever_the_type_axis_says` (type_rc = 0, 1, 2) | fabricated → 1, anchored → 0 on the provenance axis, **including while an unrelated type failure is live**. This is the defect fixed. |
| `test_the_wrapper_alone_cannot_tell_the_two_apart_when_the_type_axis_is_red` | the defect itself, recorded: with type_rc = 1 the wrapper returns 1 for both, so a control written against `check()` measures nothing about provenance. |
| `test_the_wrapper_fails_when_either_axis_fails` (6 cases: prov ∈ {0,1} × type ∈ {0,1,2}) | production's obligation across the matrix — green only when both axes are green; `prov=0, type≠0` still fails. |
| `test_the_wrapper_runs_the_type_axis_over_the_whole_prose_survey_it_computed` | the type axis runs exactly once, on `survey()`'s prose object itself — no narrowed corpus. |
| `test_a_missing_ledger_is_still_a_failure_and_still_short_circuits` | rc 2 preserved through the split. |
| `test_the_ledger_is_still_excluded_from_the_anchor_scan_after_the_split` | self-exclusion intact. |

The five pre-existing controls now drive `provenance_check` rather than `check`, each with the
reason recorded in place. Three of them were **red before this patch for a reason they do not test**
(see §3).

Binding scope, covered without claiming new verifications:
`test_the_cross_form_binding_is_exactly_seven_pmcid_keys_each_bound_to_one_prior_doi_row`
(7 rows, 7 distinct keys, each with exactly one prior `verified` DOI row whose `verified_pmcid` is
that identifier and which the row names in `checked_by`);
`test_every_inherited_metadata_field_is_the_doi_rows_own_value` (parametrised over
`verified_pmid`, `verified_title`, `verified_journal`, `verified_on`, `verified_source`,
`verified_pmcid`);
`test_the_inherited_narrative_cannot_be_read_as_a_check_of_the_pmcid`;
`test_the_binding_adds_rows_and_adds_no_new_verified_work` — **seven ROWS, zero new WORKS**: every
inherited row's `verified_pmid` is one another ledger row already carries, so the row count rises by
seven while the count of distinct verified works is unchanged. The two quantities are named as
distinct everywhere they appear;
`test_the_ledger_says_in_one_place_that_the_cross_form_rows_are_not_a_new_verification`.

⛔ **What none of this establishes**: it does not corroborate the inherited values from a new
independent source, and it does not make whole-corpus citation lint pass.

## 3 · Checks actually run (real exit codes, no pipes)

| capture | scope | exit |
| --- | --- | --- |
| `checks/PRE-test_lint_citations.txt` | pre-change, `-x` (stopped at first failure) | 1 |
| `checks/PRE-test_lint_citations-full.txt` | pre-change, full module: `F.FF.....F.........F..` = 22 tests, 5 failed | 1 |
| `checks/POST-test_lint_citations.txt` | post-change, full module: **45 tests, 43 passed, 2 failed, 0 skipped** | 1 |
| `checks/POST-manuscripts-citation-modules.txt` | `test_the_citation_scan_is_not_run_twice.py`, `test_the_citation_scan_cache_cannot_invent_an_anchor.py`, `test_citation_type_guard.py`: **56 tests, 54 passed, 2 failed, 0 skipped** | 1 |

The PRE full run also aborted in `pytest_sessionfinish` on the tracked-tree guard, because a
concurrent owner (P-AB) modified `research/manuscripts/tests/test_endpoint_manuscript_figures.py`
during the run. That is a concurrency artefact of the shared tree, not a property of this patch, and
it did not recur in the POST runs.

**Fixed by this patch** — red before, green after, all three testing provenance logic that was
already correct and failing only because the type axis was red:
`test_and_that_control_can_actually_pass_when_the_identifier_is_anchored`,
`test_a_ledgered_identifier_stays_green`,
`test_and_that_control_can_actually_pass_when_the_arxiv_id_is_anchored`.

## 4 · Remaining REAL failures — pre-existing, whole-tree, NOT this patch

1. `test_lint_citations.py::test_the_repository_currently_passes` — `lc.check() != 0`. The tree
   carries **417 NEW unanchored identifiers** (prose in `opus-capacity-campaign-20260908/reports/*`
   and `paper-lane/*` that is neither anchored in a fetch product nor ledgered) **and 13 type-claim
   errors**. Red before this patch (PRE captures) and red after, for the same reasons.
2. `test_lint_citations.py::test_the_ledger_does_not_anchor_itself` — part (b), the subset rule:
   the same 417 unanchored identifiers are absent from the ledger. This test never called `check()`,
   so the split cannot have moved it. Red before and after.
3. `test_citation_type_guard.py::test_the_live_tree_is_green_with_no_baseline_and_no_amnesty` —
   `lint_citation_types.check() != 0`, a module this patch does not touch, on 13 uncached type
   claims (e.g. `PMC9489176`, `PMID 29886600`, `PMID 41689087`). This is the live unrelated type
   failure the isolation repair exists to work around, and it is the independent evidence that
   failure 4 is not attributable to the split.
4. `test_citation_type_guard.py::test_the_guard_is_reached_by_the_gate_that_runs_in_the_commit_loop`
   — `lc.check() != 0` on the whole tree, i.e. `max(1, 1)` from failures 1 and 3.

None of these were masked, skipped, deselected or rebaselined, and no guard was changed to hide
them. Resolving them is ledger/prose work on other owners' documents and is out of P-CI's scope.

## 5 · Hashes

Pre: `checks/PRE-hashes.txt` — ledger `149a7265…4a9499b4` (matches root's stated current ledger).
Post: `checks/POST-hashes.txt`. Diff: `P-CI.diff` (439 lines, three files only).
