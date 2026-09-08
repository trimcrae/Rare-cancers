---
id: DOC-OPUS-CAMPAIGN-CORRECTED-A-DENOMINATOR-CATEGORY
title: "CORRECTED-A — denominator and category correction component"
level: L4
kind: curation
status: live
purpose: >
  A NEW sibling artifact that materialises the corrected denominator/category contract over the same
  552 delivered endpoint rows: the participant denominator is READ from the source with its exact
  hierarchical provenance and never inferred from a sum of response cells; every source category is
  preserved verbatim under its own definition; overlapping strata, multiples of a denominator and
  category collisions are marked unresolved or unsuitable in machine-readable form; and job 1's
  mislabelled column 26 is relabelled without altering a single value.
scope: >
  L4. Denominator and category only. It repairs no manuscript, computes no rate, proportion or
  percentage, asserts nothing about identity, selection, overlap, duplication, arm attribution,
  disease, phase, control status, capacity, efficacy, safety or clinical readiness.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
related: [DOC-OPUS-CAMPAIGN-CURATION-ENDPOINT-MEASUREMENT-CONTRACT, DOC-OPUS-CAMPAIGN-HOLD-ENDPOINT]
---

# CORRECTED-A — denominator and category

⛔ The response-endpoint manuscript stays **parked**. Nothing here reinstates, revises or
recomputes any manuscript quantity, and nothing here lifts a hold.

⚠ **Materialisation, not acceptance.** This component materialises a corrected contract over the
delivered rows. It does **not** accept the old job-1 / job-2 / job-3 logic, and it does **not**
certify any individual row as scientifically usable.

## 0 · What is immutable, and what this is

The 16 leaf analyses and the original job-1/2/3 results are immutable evidence of their actual runs.
Nothing here overwrites them, and no job was re-run to make its first result look correct. Job 1's
seven shard TSVs — including the mislabelled column 26 — are **left byte-for-byte untouched**
and re-hashed as a check (`C11`, 12 input files, 0 changed).

These outputs are **new siblings** carrying an explicit disposition / change map
(`corrected-a-change-map.tsv` / `.json`).

⚠ **Confirmation status, carried in the artifact itself**
(`corrected-a-schema.json → confirmation_status`, `corrected-a-summary.json`):

| | independently confirmed? |
|---|---|
| Job 1 arithmetic | **YES** — `VERIFY-job1-arithmetic.md`, and reproduced again here (`C9`, `C10`) |
| Job 2 (identity / selection / overlap) | **NO** |
| Job 3 (arm attribution) | **NO** |

No row in this component carries an identity, overlap, duplication, disease, phase or control-status
warrant of any kind.

## 1 · Inputs actually read

| input | use | integrity |
|---|---|---|
| Delivered payload cache copy, `ctg-cache-216bd1b5/`, 12 payloads + `_manifest.json`, revision `216bd1b5fb25a56b90ef3cc2373e1fe68322708f` | the only source of denominators and categories | `sha256sum -c SHA256-MANIFEST.txt` → 13/13 `OK`, **exit 0** |
| `CURATION-endpoint-measurement-contract-rows-*.tsv` (job 1, 552 rows) | the row set to correct; values carried, never altered | sha256 recorded in `corrected-a-input-manifest.json`, re-verified unchanged |
| `LEAF-OUT/LEAF-QA-group{0,1,2,3}.tsv` (completed leaf evidence) | independent cross-check of the read denominator | sha256 recorded and re-verified unchanged |

⛔ **No network request of any kind.** No `participantFlowModule` fetch, no intervention
back-pointer fetch, no re-fetch of absent source content, no new cache copy. No producer, gate,
preflight or test suite was run. Nothing was committed or pushed. No worker was spawned.

The four delivered LEAF-QA files use **four different schemas**; they are joined on the
`(nct_id, outcome_measure_index, group_id)` triple they share, and they cover **319 of the 552**
rows. That partial coverage is why the category vector here is read directly from the delivered
cache for all 552 rows, with the leaf evidence used as an independent agreement check rather than as
the vector source.

## 2 · The corrected contract, as implemented

1. **The denominator is read, never inferred.** Every row's denominator is
   `outcomeMeasures[i].denoms[units=="Participants"].counts[groupId].value`, stored with that exact
   path in `denominator_provenance`. **552 / 552** rows carry one. `evaluable_n` — the sum of the old
   producer's four cells — is retained only as `job1_evaluable_n_sum_of_four_producer_cells`,
   is labelled old evidence, and is **never used as a denominator**. In 253 rows the two coincide
   numerically; that coincidence is recorded as a coincidence, not as a derivation (`C5`).
2. **Every category is preserved under its own source definition.** `corrected-a-categories.tsv`
   holds **3,123** category measurements at the grain
   `(study, outcome measure, group, class, category)` — every category of every contributing and
   non-contributing class for the row's group, verbatim title and verbatim value, with class index.
   **123 distinct verbatim titles**; `corrected-a-category-inventory.tsv` lists each one with
   `folded = NO`. `sCR`, `VGPR`, `CRh`, `CRi`, `CRmrd-`, `PD`, `NE`, `Non-CR/Non-PD`, `Unknown`,
   `Missing`, `Not Done`, `UE`, `Died Before Evaluation` and the rest all survive under their own
   titles. **⚠ Categories from different response criteria are not one universal numerator
   taxonomy**: `CR`/`PR`/`SD`/`PD` appear here only as a description of what the OLD producer matched
   (`producer_label_assigned`), never as this component's vocabulary, and nothing is mapped,
   merged or renamed into a common vocabulary.
3. **Overlap, multiples and missing selection bases are marked, never resolved by preference.**
   Blocking codes in `unresolved_reason_codes` drive `proportion_suitability`. Nothing is rescaled,
   no favourable class is chosen, no overlapping stratum is collapsed, and no category is silently
   dropped.
4. **Raw numerator and denominator fields are recorded; no rate is derived.** `rate_derived` is the
   literal `NOT_DERIVED` on 552/552 rows, there is no rate/percent/proportion column anywhere, and
   every numeric diagnostic is an integer count (`C6`).
5. **The trace is preserved** to payload, study, outcome measure, group, class, category and
   measurement.

## 3 · The column-26 correction

Job 1's delivered header calls column 26 `sum_minus_reported_denominator`. Its value, in **all 552
rows**, is `evaluable_n` (the four producer cells) **minus** the reported denominator — not the
all-category sum minus the denominator. Verified on every row (`C4`).

| | in CORRECTED-A |
|---|---|
| the **label** | corrected to **`evaluable_n_minus_reported_denominator`**, derivation stated: `job1_evaluable_n_sum_of_four_producer_cells − reported_denominator_participants` |
| the **value** | **unchanged**. Also carried byte-identical as `job1_column26_value_carried_unchanged`, with `job1_column26_original_label` recording the misleading header verbatim |
| the **old file** | **untouched**, retained as original evidence, hash-verified unchanged |
| the diagnostic the old header **implied** | emitted as a **distinct** column, `all_categories_sum_minus_reported_denominator`, derivation stated: `all_categories_contributing_classes_sum − reported_denominator_participants` |

The two columns **differ on 299 of 552 rows**; they agree on the 253 rows whose records carry only
the four matched categories, which is why the misleading header was survivable in the first place.
⛔ No value was altered to fit the old header.

## 4 · Machine-readable state — what the 552 rows actually say

`denominator_state` = `READ_FROM_SOURCE` on **552 / 552**.
`category_preservation_state` = `FULL_VECTOR` on **552 / 552**.

**`proportion_suitability`** (enumerated):

| state | rows |
|---|---|
| `UNSUITABLE_FOR_PROPORTION` | **61** |
| `NOT_REFUTED_BY_THIS_COMPONENT` | **491** |

⚠ `NOT_REFUTED_BY_THIS_COMPONENT` means only that **this** component found no blocking
denominator/category defect. It is **not** an eligibility grant and **not** a suitability claim: the
identity/selection/overlap and arm-attribution conditions are owned by sibling components and are
unconfirmed.

**Blocking `unresolved_reason_codes`** (a row may carry more than one):

| code | rows |
|---|---|
| `PRODUCER_LABEL_COLLISION_WITHIN_CLASS` | 51 |
| `PRODUCER_LABEL_COLLISION_ACROSS_CLASSES` | 10 |
| `MULTIPLE_CONTRIBUTING_CLASSES_NO_SOURCE_SUPPORTED_SELECTION_BASIS` | 10 |
| `CATEGORY_SUM_IS_A_MULTIPLE_OF_REPORTED_DENOMINATOR_OVERLAPPING_STRATA` | 3 |
| `CATEGORY_SUM_EXCEEDS_REPORTED_DENOMINATOR` | 1 |
| `DENOMINATOR_NOT_REPORTED_AS_PARTICIPANTS` | 0 |

**Non-blocking `advisory_flag_codes`**, which travel with the row:

| code | rows |
|---|---|
| `NON_EVALUABLE_CATEGORY_DROPPED_BY_PRODUCER` | 464 |
| `RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER` | **101** |
| `UNCLASSIFIED_CATEGORY_DROPPED_BY_PRODUCER` | 65 |
| `REPORTED_CATEGORIES_DO_NOT_ACCOUNT_FOR_FULL_DENOMINATOR` | 0 |
| `NON_INTEGER_CATEGORY_VALUE_PRESENT` | 0 |

The 101 rows flagged `RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER` are rows where the old
extraction discarded a category that reports **responders** under its own criteria set —
`Non-CR/Non-PD (NCRNPD)` (54), `Non-CR/Non-PD` (26), `Very Good Partial Response (VGPR)` (15),
`Stringent Complete Response (sCR)` (13), `CRh` (8), `CRi` (8), `CRmrd-` (8), `Non-CR / Non-PD` (3),
`Minimal Response (MR)` (3), `Non-CR/Non-PD (NN)` (2), `MR` (1),
`Near Complete Response (nCR)` (1). The flag is a flag on the verbatim title; ⛔ none of these
titles is folded into `CR` or `PR` or into any other category here.

## 5 · Artifacts

| file | what it is |
|---|---|
| `corrected-a-rows.tsv` | 552 rows × 51 columns — one per delivered job-1 row, corrected |
| `corrected-a-categories.tsv` | 3,123 records × 18 columns — every source category, verbatim |
| `corrected-a-category-inventory.tsv` | 123 distinct verbatim titles × 10 columns, `folded = NO` |
| `corrected-a-schema.json` | full schema: column-by-column descriptions, actual input keys and join cardinalities, and every enumerated state code |
| `corrected-a-change-map.tsv` / `.json` | disposition of each of job 1's 30 columns + the added columns, with a disposition vocabulary |
| `corrected-a-summary.json` | machine-readable counts, including `job2_job3_independently_confirmed: false` |
| `corrected-a-input-manifest.json` | sha256 of the 12 original evidence files this component must not modify |
| `corrected-a-checks.json` | the 12 deterministic checks and their results |
| `CHECK-RUN-RECORD.txt` | the actual commands and **real captured exit codes** |
| `build_corrected_a.py`, `check_corrected_a.py` | working files; read-only over inputs, write only this directory |

## 6 · Checks actually run, with real exit codes

Recorded verbatim in `CHECK-RUN-RECORD.txt`. No pipes were used, so `$?` is the true exit code of
each command. No check was skipped, deselected or reported as a pass without being emitted.

| id | check | result |
|---|---|---|
| R0 | `sha256sum -c SHA256-MANIFEST.txt` — 13/13 `OK` | **exit 0** |
| R1 | `python3 build_corrected_a.py` | **exit 0** |
| R2 | `python3 check_corrected_a.py` — 12/12 checks passed | **exit 0** |

| id | deterministic check | result |
|---|---|---|
| C1 | key set is an exact bijection onto job 1's 552 delivered rows (0 missing, 0 extra) | PASS |
| C2 | every required field populated on every row (0 empty) | PASS |
| C3 | declared schema matches every emitted header exactly (51 / 18 / 10 columns) | PASS |
| C4 | column 26 relabelled with **every value byte-identical**; the implied diagnostic emitted as a separate column; the two differ on 299/552 | PASS |
| C5 | 552/552 denominators `READ_FROM_SOURCE` with well-formed hierarchical provenance; none inferred from cells | PASS |
| C6 | no rate / proportion / percentage anywhere; `rate_derived = NOT_DERIVED` on 552/552 | PASS |
| C7 | 3,123 category records = Σ`n_source_categories`; grain unique; 0 folded titles; `sCR`, `VGPR`, `CRh`, `CRi`, `PD`, `NE` all present verbatim | PASS |
| C8 | every state and code is in the declared enumeration and consistent with the row (0 inconsistencies) | PASS |
| C9 | this component's **own** source reading reproduces job 1's overwrite partition 10 / 51 / 491 / 22 exactly | PASS |
| C10 | delivered LEAF-QA evidence agrees on the denominator on **1937 / 1937** records over the 319 rows it covers, 0 disagreements | PASS |
| C11 | the 12 original job-1 and leaf evidence files re-hashed, **0 changed** | PASS |
| C12 | the artifact itself carries that job 2 and job 3 are **not** independently confirmed | PASS |

These are focused checks of the **new** corrected logic and of key/coverage compatibility. No
unchanged full re-audit of the source was performed, and no completed leaf task was repeated.

## 7 · Data sufficiency — what this component does and does not settle

**Sufficient, on the delivered evidence:**

- Every one of the 552 rows has an explicitly reported participant denominator, read with its exact
  path. The denominator question is **settled** for this row set (`DENOMINATOR_NOT_REPORTED_AS_
  PARTICIPANTS` = 0 rows).
- The complete category vector is recovered for all 552 rows — 3,123 measurements, 123 distinct
  verbatim titles, none folded. The category-preservation question is **settled** for this row set.
- The column-26 mislabelling is **settled**: label corrected, values untouched, old file intact, and
  the implied full-vector diagnostic emitted separately.

**Not sufficient — the ledger is complete, and that is not scientific eligibility:**

- **61 rows are `UNSUITABLE_FOR_PROPORTION`** on denominator/category grounds alone. For those the
  source supplies no selection basis between overlapping strata, subgroups, therapy lines, timepoints
  or tumour types, and none can be manufactured from the delivered payloads. Resolving them would
  need source content this component is forbidden to fetch and that the cache does not contain.
- **The 491 remaining rows are not certified.** `NOT_REFUTED_BY_THIS_COMPONENT` is the strongest
  statement the denominator/category evidence supports. Arm identity, repeated or duplicated
  assessment, cross-shard overlap, and arm-level disease / phase / control status are **outside this
  component**, and job 2 and job 3 remain **unconfirmed**.
- **Response criteria are not reconciled, by design.** A row's categories are valid under the
  criteria set its own record used. Whether counts from RECIST, IMWG, Lugano, ELN and IWG-style
  reporting may ever share a numerator definition is a scientific question this component
  deliberately leaves open, and the artifact preserves the distinction rather than deciding it.
- **101 rows lost responders in the old extraction.** That is recorded as a flag on verbatim titles.
  ⛔ No corrected numerator was constructed from them, because constructing one would require the
  cross-criteria decision above.

**Stop condition.** This component **stops at the finite corrected contract**, delivered and checked
— not at an input insufficiency. The residual insufficiency is scoped and stated above: 61 rows
whose selection basis the source does not supply, and the cross-criteria numerator question, which
is a scientific decision rather than a missing input.

⛔ No response rate, unique-patient total, cross-disease capacity bound, control comparison or
clinical comparison appears anywhere in this component, and no manuscript was touched.
