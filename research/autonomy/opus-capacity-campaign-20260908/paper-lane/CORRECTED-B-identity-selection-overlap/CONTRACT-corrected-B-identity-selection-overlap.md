---
id: DOC-OPUS-CAMPAIGN-CORRECTED-B-IDENTITY-SELECTION-OVERLAP
title: "Corrected contract B — endpoint identity, observation selection and cohort overlap"
level: L4
kind: contract
status: live
supersedes: nothing
relation_to_job2: new sibling with an explicit disposition map; job2's artifacts are untouched
purpose: >
  Replace job2's single-selected-record-per-cohort model with a source-bound long-form evidence
  ledger that keeps competing records as an explicitly related set, keeps the three denominator
  states apart, and records pooled/component and enrollment conflicts without manufacturing
  independent patient groups.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Corrected contract B — identity / selection / overlap

⛔ **This contract states no response rate, no unique-patient total, no capacity bound, no control
comparison and no clinical comparison.** The endpoint manuscript stays **parked** and was neither
read nor edited. Nothing here was committed or pushed.

## 0 · Status of the evidence this contract builds on

⚠ **job2 and job3 were never independently confirmed.** No row of either was verified as correct,
and nothing below asserts that any job2 or job3 output is right. job1/job2/job3 results and the 16
leaf analyses remain **immutable evidence of their actual runs**; not one byte of them was edited or
re-run. This contract is a **new sibling** whose relationship to job2 is recorded row by row in
`artifacts/CHANGE-MAP-vs-job2.tsv` (16,891 rows: every job2 selected row, tie, exclusion and
enrollment row).

Where a job2 quantity appears here it is labelled a **job2 output**, not a fact.

## 1 · Inputs — exactly the delivered bytes

| item | value |
|---|---|
| cache | `…/scratchpad/ctg-cache-216bd1b5/`, revision `216bd1b5fb25a56b90ef3cc2373e1fe68322708f` |
| integrity | `sha256sum -c SHA256-MANIFEST.txt` → 13/13 `OK`, **exit code 0** (check `C1`) |
| payloads read | the 12 cached `ctg_*.txt` |
| leaf evidence reused | `LEAF-OUT/LEAF-QB-group[0-3].{md,tsv}`, `LEAF-OUT/LEAF-QC-group[0-3].{md,tsv}` |
| job2 artifacts read (read-only) | `SELECTED-…tsv`, `TIES.tsv`, `EXCLUSIONS.tsv`, `OVERLAP-enrollment-check.tsv` |
| network | **none.** No re-fetch of `participantFlowModule`, of intervention back-pointers, or of any absent content |

## 2 · D-SEL — the quantities are separated before any observation is considered

**The unit of the ledger is one *observation*: `(nctId, outcome-measure index, results-group id)`.**
16,116 observations across 2,642 trials. Every observation keeps, as **separate source fields**:
outcome identifier and title, description, response definition text, assessment criteria and version
tokens, time frame, population description, `paramType`, `unitOfMeasure`, `dispersionType`,
denominator units, result-group id / title / description, and class/category identity.

⚠ **ORR, DCR, CBR and response-category distributions are recorded as distinct constructs and are
never merged.** Construct census over the 16,116 observations: response-category distribution 14,977,
best overall response 9,608, overall response 9,175, generic response rate 7,555, ORR 7,474,
DCR 2,384, objective response 2,159, CBR 921, duration of response 289, time to response 23. **2,607
cohort keys carry both a response-rate construct and a DCR/CBR construct**, and **5,718 carry both an
ORR-family construct and a response-category distribution.** Collapsing those into one endpoint would
be an invention; this contract does not do it.

Assessment criteria are recorded as tokens with versions (RECIST 8,822 observations, IMWG 503,
mRECIST+RECIST 352, irRC 337, Lugano 268, RANO 228, IWG 217; version `1.1` 8,206, `1.0` 916,
mixed `1.0|1.1` 105). **1,033 cohort keys carry more than one criteria version.**
⛔ No RECIST version, time point, subgroup or endpoint is preferred, and none was chosen from
registration order or from which choice yields more usable data.

### Competing records are retained as an explicitly related set

`artifacts/RELATED-SETS-unresolved.tsv` holds **8,740 cohort keys**; **4,464 have more than one
competing observation** (maximum 17). Each carries machine-readable unresolved states:

| state | cohort keys |
|---|---|
| `UNRESOLVED_MULTIPLE_MEASURE_TITLES` | 4,441 |
| `UNRESOLVED_MULTIPLE_ENDPOINT_CONSTRUCTS` | 3,944 |
| `UNRESOLVED_MULTIPLE_POPULATION_DESCRIPTIONS` | 2,238 |
| `UNRESOLVED_MULTIPLE_TIME_FRAMES` | 1,797 |
| `UNRESOLVED_MULTIPLE_OUTCOME_TYPES` | 1,504 |
| `UNRESOLVED_MULTIPLE_PARAMTYPE_OR_UNIT` | 1,481 |
| `UNRESOLVED_MULTIPLE_ASSESSMENT_CRITERIA` | 1,457 |
| `UNRESOLVED_MULTIPLE_DENOMINATORS` | 1,248 |
| `NO_OBSERVATION_USABLE_FOR_A_PROPORTION` | 376 |
| `SINGLE_OBSERVATION` | 4,063 |
| `DUPLICATE_ENCODING_CANDIDATE` | **0** |
| `UNRESOLVED_NO_DISTINGUISHING_FIELD_FOUND` | **0** |

**Genuinely duplicate encodings do not occur in this cache.** Every one of the 4,464 competing sets
differs on at least one preserved identity field, so every one of them is a **distinct outcome, time
point or population** rather than a re-encoding of the same measurement. `selection_status` is
`NOT_SELECTED_BY_DESIGN` on all 8,740 rows.

⛔ **This contract approves no preferred endpoint and no new single-record-per-arm selection
algorithm.** An unresolved choice stays unresolved.

### The withdrawn step-f claim

**Accepted and recorded: job2's claim that step-`f` ties carry no distinguishing metadata is
WITHDRAWN.** The delivered leaf evidence adjudicates all 1,590 step-`f` tie rows and finds
**1,589 `BASIS_EXISTS` and 1 `NO_BASIS`** (check `C9`; harmonised in
`artifacts/LEAF-QC-harmonised-ties.tsv`). Every such tie is dispositioned in the change map as
`WITHDRAWN__…`; **the tie-break is not adopted and no replacement selection is made.**

### Zero, absent and nonparticipant denominators are three different things

| state | observations | treatment |
|---|---|---|
| `PRESENT` (positive Participants count) | 14,834 | usable for a proportion |
| `REPORTED_ZERO` | **1,282** (287 trials) | **retained as a source fact, marked unusable.** Never a divisor; never read as an observed zero-response cohort |
| `ABSENT_*` (no denoms / no Participants unit / none for this group / empty) | **0 observed** | vocabulary defined and enforced (`C12`) |
| `NONPARTICIPANT_UNITS_ONLY` | **0 observed** | vocabulary defined and enforced (`C12`) |

⚠ **job2's own selected set carried 509 zero-denominator rows across 216 trials** as if they were
selected analyzable observations (425 resolved at ladder steps a–d, 84 at step f). Those rows are
retained here, marked unusable, and never divided by. **364 cohort keys have no non-zero observation
at all**; a further 12 are unusable only because the record carries no `reportingStatus` field.

**639 observations carry a source statement that data were not collected, not analysed, or that the
study terminated** (`noncollection_statement` / `noncollection_evidence`). Those statements are
preserved verbatim rather than being reduced to a missing value.

### Records job2 dropped that this contract reinstates

**15 observations in 10 trials** carry fully populated, POSTED-shaped results with **no
`reportingStatus` field**. job2's rule required `reportingStatus == "POSTED"` and dropped every one
of them; none appears in its selection (check `C19`). They are reinstated here as source records with
`reporting_status_state = ABSENT_FIELD` and `usable_for_proportion = False`, because a missing
metadata field is a metadata gap, not evidence that data are absent.

### An identity-key defect in job2, reported at its true size

6 of job2's 8,728 selected rows do not join this ledger on `(nct, normalised group title)`. The cause
is exact and reproducible: **job2's normalisation strips a trailing `-` but not a trailing `+`**, so
biomarker-negative cohorts (`Part 1: Non-tBRCA LOH-`, `Phase II PD-L1-`, `… (Part 2): ER-`,
`TRT B -`, `SCLC Arm N-I Dose Level 1 -`) lose the sign that makes them negative, while their `+`
siblings keep it (check `C6`). ⚠ **This is a key-formation defect, not an observed merge**: across the
whole cache the strip would merge two distinct source group titles in **0 trials** (check `C7`). The
defect affects 11 source titles in 5 trials. It is reported at that size and no further.

## 3 · D-OVL — relationships and inconsistency are preserved, independence is not manufactured

⛔ **No row of this contract claims to be one independent arm, and no sum of denominators is offered
as a count of unique patients.** Neither 552, nor 465, nor 138, nor 8,728 was used as a target,
input or check.

**Pooled parent / component relations.** 63 pooled-labelled cohort keys in 57 trials;
`artifacts/GROUP-RELATIONS-pooled-parent-component.tsv` records 47 parent→component relations where
both exist in the same trial. `component_sum` appears there **only to expose the double counting
against the parent**; parent and components are the same people and are never added together
(check `C18`).

**Repeated assessments and repeated outcomes** are explicit: the related-set file names the competing
observation ids, their measure indices, and the number of distinct time frames, criteria, populations
and denominators, instead of collapsing them.

**Overlapping group relationships.** `artifacts/RESULTS-GROUP-ID-REUSE.tsv` records **3,813**
`(trial, results-group id)` pairs where one `OGnnn` carries more than one group title across a
trial's measures — the id is not a study-level cohort key, so a join on id across measures is wrong.

### Enrollment: recorded, conflicted, not repaired

`enrollmentInfo.count` and `.type` are kept exactly as recorded. **No clipping, no invented corrected
enrollment, no declaration of which field is wrong.** Per trial the ledger reports the largest single
cohort denominator and the largest sum **within one outcome measure**; **no cross-measure sum is
emitted anywhere** (recomputed and verified, check `C13`).

| finding | trials |
|---|---|
| `NO_CONFLICT_DETECTED` | 2,536 |
| `WITHIN_MEASURE_SUM_EXCEEDS_ENROLLMENT` | 70 |
| … and that measure contains a pooled/total group | 35 |
| `SINGLE_COHORT_EXCEEDS_ENROLLMENT__INTERNAL_INCONSISTENCY__INFERENCE_STOPPED` | **1** |

The single-cohort case is `NCT00756509`: one registered arm, `enrollmentInfo.count = 34` type
`ACTUAL`, and `outcomeMeasures[0]/OG000` reporting a Participants denominator of **41**. ⚠ **The
conflicting fields are recorded and the inference stops there.** The source does not say which field
is wrong, and this contract does not decide.

⚠ **job2's headline that 180 trials "prove overlap" is selection-dependent.** Those 180 excesses come
from summing **one selected record per cohort key across different outcome measures**. Within a single
outcome measure only **106** trials exceed enrollment, 35 of them because that very measure contains a
pooled group, and only **1** trial has a single cohort larger than its enrollment (check `C15`). The
job2 excess figures are carried in the change map as **`NOT_ADOPTED__CROSS_MEASURE_SUM_IS_NOT_A_PATIENT_COUNT`**.
The QB leaf mechanism findings for all 180 trials are harmonised in
`artifacts/LEAF-QB-harmonised-trials.tsv` and are reported as **leaf findings about job2's selected
set**, not as confirmation of it.

### Missing participant flow limits every disjointness claim

**The cache contains no `participantFlowModule`, no `baselineCharacteristicsModule` and no
`eligibilityModule`** — `grep -l participantFlowModule` over all 12 payloads returns no file, exit
code 1 (check `C21`), and the only results module present is `outcomeMeasuresModule`. ⛔ Nothing was
re-fetched to fill this in. Every trial row therefore carries
`disjointness_status = DISJOINTNESS_UNVERIFIABLE__NO_participantFlowModule_IN_CACHE`, and **no claim
that two cohorts are disjoint patient sets appears anywhere in this contract.**

## 4 · Checks — real exit codes

`checks.py` runs 22 deterministic checks over schema/key compatibility, actual row coverage and the
specific prior counterexamples. Transcript: `artifacts/CHECKS.log`; machine-readable:
`artifacts/CHECKS.json`.

```
$ python3 checks.py ; echo CHECKS_EXIT=$?
22/22 checks passed
CHECKS_EXIT=0
```

No check was skipped or deselected; a check that cannot run is a FAIL, and the process exits 1 on any
failure. `C20` was **strengthened, not relaxed**, when it first failed on the boolean flag columns
`usable_for_proportion` / `denominator_usable` / `n_usable_for_proportion`: the check now proves their
value domain is boolean-or-count, so no response proportion, numerator or rate exists in any emitted
column. The build itself ran to completion with exit 0.

Coverage established by the checks: 16,116 observations with unique complete keys; 8,740 related sets
that exactly partition them; 29,305 measurement-cell rows with no orphan; all 8,728 job2 selected
rows, all 2,001 ties, all 3,530 exclusions and all 2,632 job2 enrollment rows dispositioned; all 1,590
step-`f` ties covered by leaf QC; all 180 job2 excess trials covered by leaf QB.

⚠ **The eight delivered leaf TSVs are schema-incompatible as delivered** — QB has 4 distinct headers
across its 4 files and QC has 4 distinct headers across its 4 files (check `C16b`). Harmonisation was
required; the column mapping is recorded literally in `build_ledger.py` (`QB_MAP`, `QC_BASIS`,
`QC_CHANGE`) so it can be re-derived.

## 5 · What this contract does NOT do

1. It defines **no** preferred endpoint, criteria version, time point, population or arm.
2. It defines **no** single-record-per-cohort selection algorithm, and does not repair job2's.
3. It computes **no** response proportion, numerator or rate, and **no** unique-patient total.
4. It does **not** confirm job2 or job3, and does not treat any of their rows as verified.
5. It does **not** force the data into the 552-row or one-arm model.
6. It does **not** decide which of two conflicting source fields is wrong.
7. It makes **no** manuscript change. The endpoint manuscript stays parked.

## 6 · Artifacts

| file | rows | bytes |
|---|---|---|
| `artifacts/LEDGER-response-observations.tsv` | 16,116 | 26,651,089 |
| `artifacts/LEDGER-measurement-cells.tsv` | 29,305 | 7,088,385 |
| `artifacts/RELATED-SETS-unresolved.tsv` | 8,740 | 3,895,981 |
| `artifacts/ENROLLMENT-CONFLICT.tsv` | 2,642 | 749,267 |
| `artifacts/RESULTS-GROUP-ID-REUSE.tsv` | 3,813 | 561,377 |
| `artifacts/GROUP-RELATIONS-pooled-parent-component.tsv` | 47 | 25,094 |
| `artifacts/CHANGE-MAP-vs-job2.tsv` | 16,891 | 5,233,001 |
| `artifacts/LEAF-QB-harmonised-trials.tsv` | 180 | 20,030 |
| `artifacts/LEAF-QC-harmonised-ties.tsv` | 1,590 | 221,621 |
| `artifacts/BUILD-SUMMARY.json`, `artifacts/CHECKS.json`, `artifacts/CHECKS.log` | — | — |
| `build_ledger.py`, `checks.py`, `SCHEMA.json`, `DATA-SUFFICIENCY.md` | — | — |

Exact byte sizes and sha256 of every artifact are recorded in `SCHEMA.json`.
