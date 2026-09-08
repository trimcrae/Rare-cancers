---
id: DOC-OPUS-CAMPAIGN-LEAF-QA-GROUP0
title: "LEAF QA group0 — recoverable corrected readings for 23 assigned NCTs"
level: L4
kind: curation
status: live
scope: >
  L4 source validation of one assigned NCT group only. Emits the corrected reading (reported
  denominator + full source category vector + residual) for every in-scope derived row.
  It repairs nothing, edits no manuscript or producer, and lifts no hold.
date: 2026-09-08
last_verified: 2026-09-08
---

# LEAF-QA-group0 — corrected readings

⛔ The response-endpoint manuscript stays parked. Nothing here reinstates a withdrawn claim, and
nothing here is a statement about efficacy, safety, selectivity or clinical readiness of any agent.

## 1 · Inputs, integrity and fences

- Cache read: `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5/`
  (branch `literature-cache` @ `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`). **No network request of any
  kind was made.** No payload was re-fetched, no second copy created, no producer/build/test/gate run.
- Integrity: `sha256sum -c SHA256-MANIFEST.txt` → 13/13 `OK`, **exit code 0**.
- Row tables read (context, not re-derived): `CURATION-endpoint-measurement-contract-rows-*.tsv`.
  Job 1's classification of the 552 rows is taken as given and is not restated as a finding here.
- Assigned group: the 23 NCTs in `LEAF-ASSIGNMENTS/QA-group0.txt`. No other NCT was read or reasoned
  about; every other NCT is **outside my group**.

## 2 · Coverage reached vs assigned

| Quantity | Value |
|---|---|
| NCTs assigned | 23 |
| NCTs with at least one in-scope row | 23 |
| In-scope derived rows (classification `unsupported`/`ambiguous` **or** `overwrite_scope != none`) | **76** |
| In-scope rows actually opened against the cached source and corrected | **76 / 76 (100%)** |
| Source classes enumerated for those rows | 86 |
| Source category readings emitted | (see TSV) |

All 23 assigned NCTs carry at least one in-scope row, so no assigned NCT was skipped. Rows of my
NCTs that are `valid` with `overwrite_scope=none` are correctly out of scope and were not opened.

## 3 · Verdict definitions

| Verdict | Meaning |
|---|---|
| `RECOVERABLE` | A single corrected reading exists. Exactly one source class contributed, and **all** of its integer categories sum exactly to the record's own reported `Participants` denominator for that group. Denominator and every category count are read directly from the record. |
| `RECOVERABLE_DENOM_ONLY` | The **denominator** is recoverable and exact, but the four-cell **numerator vector the derived row stores is not**, because two or more source categories collided onto one stored label with *different* values (last write wins), or because cells were drawn from several classes. The corrected denominator is stated; the corrected per-category vector is stated per source class, and the collapsed single vector is not recoverable. |
| `UNRESOLVED` | No single corrected reading exists from the assigned evidence. |

| Verdict | Rows |
|---|---|
| `RECOVERABLE` | **70** |
| `RECOVERABLE_DENOM_ONLY` | **5** |
| `UNRESOLVED` | **1** |
| total | **76** |

**Recoverability of the denominator, restricted to my 76 rows:** 75 / 76 rows have all categories of
their contributing class(es) summing exactly to the record's reported `Participants` denominator
(residual 0). One row (`NCT01790503` OG000, outcome 6) does not, and is `UNRESOLVED`. This is my
own re-derivation over my own rows only; it is not a restatement of Job 1's 548/552.

**Defect found in the Job 1 row tables (reported, not fixed here).** Column 26 is headed
`sum_minus_reported_denominator`, which reads as column 25 − column 24
(`all_categories_in_contributing_classes_sum` − `reported_denominator_participants`). It does not
hold that. Across all 552 rows of the shipped TSVs, column 26 == column 23 − column 24
(`evaluable_n_sum_of_cells` − `reported_denominator_participants`) in 552/552 rows, and equals
column 25 − column 24 in only 253/552. The residual a corrected reading needs is the *former*
column's arithmetic, and it is **not** in the shipped tables. The `residual_sum_minus_reported`
column of `LEAF-QA-group0.tsv` carries the true value (col25 − col24), computed from source.

## 4 · What the corrected reading is, per row

The full corrected readings — every source class, every category title, every count, matched and
dropped alike, each with a payload/NCT/outcome/group/class/category pointer — are in
`LEAF-OUT/LEAF-QA-group0.tsv`. Its records:

- `record_type=CLASS`: one line per **contributing source class** of a row. This is the
  "one output line per source class" enumeration required for cross-class and within-class
  overwrite rows: `class_index`, `class_title`, `class_all_category_sum`.
- `record_type=CATEGORY`: one line per **source category** of each contributing class, with
  `category_title`, `category_value`, `producer_label` (the four-cell label the producer's regex
  assigned, empty when the category was dropped) and `producer_kept` ∈ {`yes`, `overwritten`,
  `dropped`}. `dropped` is the content the derived row lost.

Column `reported_denominator` is read from the record's own `denoms` block
(`units == "Participants"`, that group's count). `contributing_class_sum` is the sum of every
integer category of every contributing class. `residual_sum_minus_reported` is their difference.

### 4.1 Row-level corrected readings

#### NCT00600340 — 8 in-scope row(s), payload `ctg_results_bor_1999_2009.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 3 | `OG000` Bevacizumab Plus Paclitaxel | 270 | **285** | 1 (0) | 285 | +0 | `Not evaluable`=15 | `RECOVERABLE` |
| 3 | `OG001` Bevacizumab Plus Capecitabine | 261 | **279** | 1 (0) | 279 | +0 | `Not evaluable`=18 | `RECOVERABLE` |
| 4 | `OG000` Bevacizumab Plus Paclitaxel | 255 | **266** | 1 (0) | 266 | +0 | `Not evaluable`=11 | `RECOVERABLE` |
| 4 | `OG001` Bevacizumab Plus Capecitabine | 249 | **265** | 1 (0) | 265 | +0 | `Not evaluable`=16 | `RECOVERABLE` |
| 5 | `OG000` Bevacizumab Plus Paclitaxel | 270 | **285** | 1 (0) | 285 | +0 | `Not evaluable`=15 | `RECOVERABLE` |
| 5 | `OG001` Bevacizumab Plus Capecitabine | 261 | **279** | 1 (0) | 279 | +0 | `Not evaluable`=18 | `RECOVERABLE` |
| 6 | `OG000` Bevacizumab Plus Paclitaxel | 255 | **266** | 1 (0) | 266 | +0 | `Not evaluable`=11 | `RECOVERABLE` |
| 6 | `OG001` Bevacizumab Plus Capecitabine | 249 | **265** | 1 (0) | 265 | +0 | `Not evaluable`=16 | `RECOVERABLE` |

#### NCT00654238 — 1 in-scope row(s), payload `ctg_results_bor_1999_2009.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 0 | `OG000` Sorafenib | 1 | **55** | 4 (0,1,2,3) | 55 | +0 | `Not Evaluable for Response`=5 (cl0); `Not Evaluable for Response`=2 (cl1); `Not Evaluable for Response`=0 (cl2); `Not Evaluable for Response`=1 (cl3) | `RECOVERABLE_DENOM_ONLY` |

#### NCT00942162 — 3 in-scope row(s), payload `ctg_results_bor_1999_2009.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 7 | `OG000` GSK2132231A GS+ Group | 57 | **71** | 1 (0) | 71 | +0 | `NE`=3; `Missing`=0 | `RECOVERABLE_DENOM_ONLY` |
| 7 | `OG001` GSK2132231A GS- Group | 45 | **50** | 1 (0) | 50 | +0 | `NE`=1; `Missing`=0 | `RECOVERABLE_DENOM_ONLY` |
| 7 | `OG002` GSK2132231A GS-unknown Group | 2 | **2** | 1 (0) | 2 | +0 | `NE`=0; `Missing`=0 | `RECOVERABLE` |

#### NCT00946153 — 1 in-scope row(s), payload `ctg_results_bor_1999_2009.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 2 | `OG000` Phase 1: Group 1: Lenvatinib: 12 mg | 5 | **6** | 1 (0) | 6 | +0 | `Not Evaluable`=1 | `RECOVERABLE` |

#### NCT01124734 — 1 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 0 | `OG001` Course 1 Cycle 2 | 16 | **17** | 1 (0) | 17 | +0 | `Minor Response`=1 | `RECOVERABLE` |

#### NCT01188876 — 1 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | `OG000` Carboplatin/Pralatrexate | 48 | **50** | 1 (0) | 50 | +0 | `Unevaluable`=2 | `RECOVERABLE` |

#### NCT01256359 — 3 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 3 | `OG000` Docetaxel and AZD6244 | 32 | **41** | 1 (0) | 41 | +0 | `Not applicable`=9 | `RECOVERABLE` |
| 3 | `OG001` Docetaxel and Placebo | 40 | **42** | 1 (0) | 42 | +0 | `Not applicable`=2 | `RECOVERABLE` |
| 50 | `OG000` Docetaxel and AZD6244 | 16 | **20** | 1 (0) | 20 | +0 | `Not applicable`=4 | `RECOVERABLE` |

#### NCT01296932 — 9 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 4 | `OG000` BI 836826 1 Milligram | 3 | **3** | 1 (0) | 3 | +0 | `Not evaluable`=0 | `RECOVERABLE` |
| 4 | `OG001` BI 836826 3 Milligram | 3 | **3** | 1 (0) | 3 | +0 | `Not evaluable`=0 | `RECOVERABLE` |
| 4 | `OG002` BI 836826 9 Milligram | 6 | **6** | 1 (0) | 6 | +0 | `Not evaluable`=0 | `RECOVERABLE` |
| 4 | `OG003` BI 836826 25 Milligram | 5 | **6** | 1 (0) | 6 | +0 | `Not evaluable`=1 | `RECOVERABLE` |
| 4 | `OG004` BI 836826 50 Milligram | 3 | **3** | 1 (0) | 3 | +0 | `Not evaluable`=0 | `RECOVERABLE` |
| 4 | `OG005` BI 836826 100 Milligram | 3 | **3** | 1 (0) | 3 | +0 | `Not evaluable`=0 | `RECOVERABLE` |
| 4 | `OG006` BI 836826 200 Milligram | 6 | **6** | 1 (0) | 6 | +0 | `Not evaluable`=0 | `RECOVERABLE` |
| 4 | `OG007` BI 836826 400 Milligram | 3 | **3** | 1 (0) | 3 | +0 | `Not evaluable`=0 | `RECOVERABLE` |
| 4 | `OG008` BI 836826 800 Milligram | 4 | **4** | 1 (0) | 4 | +0 | `Not evaluable`=0 | `RECOVERABLE` |

#### NCT01403948 — 20 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 3 | `OG000` BI 836826 1 mg iv (Caucasian Patients) | 1 | **1** | 1 (0) | 1 | +0 | `Missing`=0 | `RECOVERABLE` |
| 3 | `OG001` BI 836826 3 mg iv (Caucasian Patients) | 3 | **4** | 1 (0) | 4 | +0 | `Missing`=1 | `RECOVERABLE` |
| 3 | `OG002` BI 836826 9 mg iv (Caucasian Patients) | 3 | **3** | 1 (0) | 3 | +0 | `Missing`=0 | `RECOVERABLE` |
| 3 | `OG003` BI 836826 25 mg iv (Caucasian Patients) | 4 | **4** | 1 (0) | 4 | +0 | `Missing`=0 | `RECOVERABLE` |
| 3 | `OG004` BI 836826 50 mg iv (Caucasian Patients) | 5 | **6** | 1 (0) | 6 | +0 | `Missing`=1 | `RECOVERABLE` |
| 3 | `OG005` BI 836826 50mg iv (Korean Patients) | 6 | **7** | 1 (0) | 7 | +0 | `Missing`=0 | `RECOVERABLE_DENOM_ONLY` |
| 3 | `OG006` BI 836826 100 mg iv (Caucasian Patients) | 5 | **6** | 1 (0) | 6 | +0 | `Missing`=1 | `RECOVERABLE` |
| 3 | `OG007` BI 836826 100 mg iv (Korean Patients) | 4 | **4** | 1 (0) | 4 | +0 | `Missing`=0 | `RECOVERABLE` |
| 3 | `OG008` BI 836826 150 mg iv (Caucasian Patients) | 5 | **6** | 1 (0) | 6 | +0 | `Missing`=1 | `RECOVERABLE` |
| 3 | `OG009` BI 836826 200 mg iv (Caucasian Patients) | 6 | **7** | 1 (0) | 7 | +0 | `Missing`=1 | `RECOVERABLE` |
| 4 | `OG000` BI 836826 1 mg iv (Caucasian Patients) | 1 | **1** | 1 (0) | 1 | +0 | `Missing`=0 | `RECOVERABLE` |
| 4 | `OG001` BI 836826 3 mg iv (Caucasian Patients) | 3 | **4** | 1 (0) | 4 | +0 | `Missing`=1 | `RECOVERABLE` |
| 4 | `OG002` BI 836826 9 mg iv (Caucasian Patients) | 3 | **3** | 1 (0) | 3 | +0 | `Missing`=0 | `RECOVERABLE` |
| 4 | `OG003` BI 836826 25 mg iv (Caucasian Patients) | 4 | **4** | 1 (0) | 4 | +0 | `Missing`=0 | `RECOVERABLE` |
| 4 | `OG004` BI 836826 50 mg iv (Caucasian Patients) | 5 | **6** | 1 (0) | 6 | +0 | `Missing`=1 | `RECOVERABLE` |
| 4 | `OG005` BI 836826 50mg iv (Korean Patients) | 6 | **7** | 1 (0) | 7 | +0 | `Missing`=0 | `RECOVERABLE_DENOM_ONLY` |
| 4 | `OG006` BI 836826 100 mg iv (Caucasian Patients) | 5 | **6** | 1 (0) | 6 | +0 | `Missing`=1 | `RECOVERABLE` |
| 4 | `OG007` BI 836826 100 mg iv (Korean Patients) | 4 | **4** | 1 (0) | 4 | +0 | `Missing`=0 | `RECOVERABLE` |
| 4 | `OG008` BI 836826 150 mg iv (Caucasian Patients) | 5 | **6** | 1 (0) | 6 | +0 | `Missing`=1 | `RECOVERABLE` |
| 4 | `OG009` BI 836826 200 mg iv (Caucasian Patients) | 6 | **7** | 1 (0) | 7 | +0 | `Missing`=1 | `RECOVERABLE` |

#### NCT01478321 — 1 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 4 | `OG000` Treatment (Radiation, Chemotherapy, Monoclonal Antibody) | 50 | **54** | 1 (0) | 54 | +0 | `Not Evaluable`=4 | `RECOVERABLE` |

#### NCT01558661 — 1 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 0 | `OG000` AG-013736 (AXITINIB) | 32 | **33** | 1 (0) | 33 | +0 | `Non-evaluable`=1 | `RECOVERABLE` |

#### NCT01562028 — 2 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 3 | `OG000` T790M Positive | 36 | **37** | 1 (0) | 37 | +0 | `Non-Evaluable`=1 | `RECOVERABLE` |
| 3 | `OG001` T790M Negative | 69 | **72** | 1 (0) | 72 | +0 | `Non-Evaluable`=3 | `RECOVERABLE` |

#### NCT01648764 — 6 in-scope row(s), payload `ctg_results_bor_1999_2009.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 5 | `OG005` 90 mg LY - Arm A Dose Escalation | 2 | **5** | 1 (0) | 5 | +0 | `Unknown`=3 | `RECOVERABLE` |
| 5 | `OG006` 100 mg LY - Arm A Dose Escalation | 5 | **9** | 1 (0) | 9 | +0 | `Unknown`=4 | `RECOVERABLE` |
| 5 | `OG009` 60 mg LY - Arm B Dose Escalation | 5 | **7** | 1 (0) | 7 | +0 | `Unknown`=2 | `RECOVERABLE` |
| 5 | `OG011` 80 mg LY - Arm B Dose Escalation | 3 | **9** | 1 (0) | 9 | +0 | `Unknown`=6 | `RECOVERABLE` |
| 5 | `OG012` 90 mg LY - Arm B Dose Escalation | 4 | **7** | 1 (0) | 7 | +0 | `Unknown`=3 | `RECOVERABLE` |
| 5 | `OG013` 90 mg LY - Arm A Dose Confirmation | 10 | **12** | 1 (0) | 12 | +0 | `Unknown`=2 | `RECOVERABLE` |

#### NCT01740297 — 2 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 3 | `OG000` Phase 2: Ipilimumab | 75 | **100** | 1 (0) | 100 | +0 | `Unevaluable (UE)`=17; `Not Done (ND)`=8 | `RECOVERABLE` |
| 3 | `OG001` Phase 2: Talimogene Laherparepvec + Ipilimumab | 88 | **98** | 1 (0) | 98 | +0 | `Unevaluable (UE)`=4; `Not Done (ND)`=6 | `RECOVERABLE` |

#### NCT01744249 — 4 in-scope row(s), payload `ctg_placebo_onc_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | `OG000` Axitinib + Sandostatin LAR | 118 | **126** | 1 (0) | 126 | +0 | `Not evaluable`=8 | `RECOVERABLE` |
| 1 | `OG001` Placebo + Sandostatin LAR | 127 | **130** | 1 (0) | 130 | +0 | `Not evaluable`=3 | `RECOVERABLE` |
| 5 | `OG000` Axitinib + Sandostatin LAR | 114 | **117** | 1 (0) | 117 | +0 | `Not evaluable`=3 | `RECOVERABLE` |
| 5 | `OG001` Placebo + Sandostatin LAR | 125 | **126** | 1 (0) | 126 | +0 | `Not evaluable`=1 | `RECOVERABLE` |

#### NCT01746225 — 3 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 3 | `OG000` A: Nab-Paclitaxel 150 mg/m2 Days 1,15 | 81 | **83** | 1 (0) | 83 | +0 | `Not Evaluable (NE)`=2 | `RECOVERABLE` |
| 3 | `OG001` B: Nab-Paclitaxel 100 mg/m2 Days 1,8,15 | 85 | **86** | 1 (0) | 86 | +0 | `Not Evaluable (NE)`=1 | `RECOVERABLE` |
| 3 | `OG002` C: Nab-Paclitaxel 75 mg/m2 Days 1,8,15,22 | 81 | **86** | 1 (0) | 86 | +0 | `Not Evaluable (NE)`=5 | `RECOVERABLE` |

#### NCT01790503 — 1 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 6 | `OG000` Combined 800 mg, 5 Days/Week | 26 | **53** | 8 (0,1,2,3,4,5,6,7) | 197 | +144 | `Unable to access`=0 (cl0); `Unknown`=0 (cl0); `Unable to access`=0 (cl1); `Unknown`=0 (cl1); `Unable to access`=0 (cl2); `Unknown`=0 (cl2); `Unable to access`=0 (cl3); `Unknown`=0 (cl3); `Unable to access`=0 (cl4); `Unknown`=0 (cl4); `Unable to access`=0 (cl5); `Unknown`=0 (cl5); `Unable to access`=0 (cl6); `Unknown`=0 (cl6); `Unable to access`=0 (cl7); `Unknown`=0 (cl7) | `UNRESOLVED` |

#### NCT01832727 — 1 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 3 | `OG000` Phase 2 300 mg 2/7 Schedule | 13 | **18** | 1 (0) | 18 | +0 | `Stringent Complete Response (sCR)`=0; `Near Complete Response (nCR)`=0; `Very Good Partial Response (VGPR)`=2; `Minimal Response (MR)`=1; `Not Evaluable (NE)`=2; `Unknown`=0 | `RECOVERABLE` |

#### NCT01853644 — 1 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 4 | `OG000` Treatment (Tivozanib) | 24 | **30** | 1 (0) | 30 | +0 | `Not Evaluable`=6 | `RECOVERABLE` |

#### NCT01859741 — 2 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 3 | `OG000` P2: Placebo + CIS or CARB | 65 | **72** | 1 (0) | 72 | +0 | `Not Evaluable`=1; `No Post-Baseline Tumor Assessment Collected`=6 | `RECOVERABLE` |
| 3 | `OG001` P2: OMP-59R5 15 mg/kg + ETO and CIS or CARB | 61 | **73** | 1 (0) | 73 | +0 | `Not Evaluable`=1; `No Post-Baseline Tumor Assessment Collected`=11 | `RECOVERABLE` |

#### NCT01876446 — 2 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 3 | `OG000` A: Chemo Resistant | 19 | **20** | 1 (0) | 20 | +0 | `NE Not Evaluable`=1 | `RECOVERABLE` |
| 3 | `OG001` B: Chemo Sensitive | 16 | **18** | 1 (0) | 18 | +0 | `NE Not Evaluable`=2 | `RECOVERABLE` |

#### NCT01975519 — 1 in-scope row(s), payload `ctg_results_bor_2010_2013.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 6 | `OG001` 10 mg/kg TRC105 + Pazopanib | 74 | **78** | 1 (0) | 78 | +0 | `Not Evaluable`=4 | `RECOVERABLE` |

#### NCT02046733 — 2 in-scope row(s), payload `ctg_results_bor_2014_2017.txt`

| om | group | derived `evaluable_n` | corrected reported denom | contributing classes | all-categories sum | residual | dropped categories (title=count) | verdict |
|---|---|---|---|---|---|---|---|---|
| 2 | `OG000` Observation | 62 | **64** | 1 (0) | 64 | +0 | `Non-evaluable`=2 | `RECOVERABLE` |
| 2 | `OG001` Nivolumab + Ipilimumab | 63 | **69** | 1 (0) | 69 | +0 | `Non-evaluable`=6 | `RECOVERABLE` |

## 5 · Cross-class and within-class collapses — every class the producer collapsed

34 of my 76 rows have at least one repeated assignment. Each is enumerated below **per source class**, not per stored row. `prev → new` gives (class index, category index, category title, value).

**NCT00654238 · outcome 0 · group `OG000` (Sorafenib)** — `ctg_results_bor_1999_2009.txt :: studies[nct=NCT00654238] :: outcomeMeasures[0] :: groups[OG000]`  
contributing classes: 4; collisions: cross_class × 12; of which value-conflicting: 8. Verdict `RECOVERABLE_DENOM_ONLY`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | Differentiated | 44 | dropped `Not Evaluable for Response`=5 |
| 1 | Poorly Differenitated | 6 | dropped `Not Evaluable for Response`=2; `Complete Response`=0 overwrote CR=`Complete Response`=0 (cl0, cross_class, values agreed); `Partial response`=2 overwrote PR=`Partial response`=16 (cl0, cross_class, CONFLICT); `Stable Disease`=1 overwrote SD=`Stable Disease`=22 (cl0, cross_class, CONFLICT); `Progressive Disease`=1 overwrote PD=`Progressive Disease`=1 (cl0, cross_class, values agreed) |
| 2 | Medullary | 3 | dropped `Not Evaluable for Response`=0; `Complete Response`=0 overwrote CR=`Complete Response`=0 (cl1, cross_class, values agreed); `Partial response`=1 overwrote PR=`Partial response`=2 (cl1, cross_class, CONFLICT); `Stable Disease`=2 overwrote SD=`Stable Disease`=1 (cl1, cross_class, CONFLICT); `Progressive Disease`=0 overwrote PD=`Progressive Disease`=1 (cl1, cross_class, CONFLICT) |
| 3 | Anaplastic | 2 | dropped `Not Evaluable for Response`=1; `Complete Response`=0 overwrote CR=`Complete Response`=0 (cl2, cross_class, values agreed); `Partial response`=0 overwrote PR=`Partial response`=1 (cl2, cross_class, CONFLICT); `Stable Disease`=0 overwrote SD=`Stable Disease`=2 (cl2, cross_class, CONFLICT); `Progressive Disease`=1 overwrote PD=`Progressive Disease`=0 (cl2, cross_class, CONFLICT) |

Corrected reported denominator: **55** (from `denoms`, units `Participants`). All categories of the 4 contributing class(es) sum to 55 (residual +0). denominator recoverable (55, all categories of the 4 contributing classes sum exactly); but cells were collapsed across 4 classes with no stated selection basis, so the per-category numerator is NOT recoverable. See §5.1 for the conditional aggregate reading of this row.

**NCT00942162 · outcome 7 · group `OG000` (GSK2132231A GS+ Group)** — `ctg_results_bor_1999_2009.txt :: studies[nct=NCT00942162] :: outcomeMeasures[7] :: groups[OG000]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 1. Verdict `RECOVERABLE_DENOM_ONLY`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 71 | dropped `NE`=3; dropped `Missing`=0; `SD/ PR`=3 overwrote SD=`SD`=11 (cl0, within_class, CONFLICT) |

Corrected reported denominator: **71** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 71 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 71; 1 within-class category collision(s) with CONFLICTING values overwrote stored labels, numerator not recoverable from the stored row

**NCT00942162 · outcome 7 · group `OG001` (GSK2132231A GS- Group)** — `ctg_results_bor_1999_2009.txt :: studies[nct=NCT00942162] :: outcomeMeasures[7] :: groups[OG001]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 1. Verdict `RECOVERABLE_DENOM_ONLY`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 50 | dropped `NE`=1; dropped `Missing`=0; `SD/ PR`=0 overwrote SD=`SD`=4 (cl0, within_class, CONFLICT) |

Corrected reported denominator: **50** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 50 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 50; 1 within-class category collision(s) with CONFLICTING values overwrote stored labels, numerator not recoverable from the stored row

**NCT00942162 · outcome 7 · group `OG002` (GSK2132231A GS-unknown Group)** — `ctg_results_bor_1999_2009.txt :: studies[nct=NCT00942162] :: outcomeMeasures[7] :: groups[OG002]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 2 | dropped `NE`=0; dropped `Missing`=0; `SD/ PR`=0 overwrote SD=`SD`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **2** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 2 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 2; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01296932 · outcome 4 · group `OG000` (BI 836826 1 Milligram)** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01296932] :: outcomeMeasures[4] :: groups[OG000]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 3 | dropped `Not evaluable`=0; `Complete remission with incomplete marrow recovery`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **3** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 3 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 3; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01296932 · outcome 4 · group `OG001` (BI 836826 3 Milligram)** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01296932] :: outcomeMeasures[4] :: groups[OG001]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 3 | dropped `Not evaluable`=0; `Complete remission with incomplete marrow recovery`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **3** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 3 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 3; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01296932 · outcome 4 · group `OG002` (BI 836826 9 Milligram)** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01296932] :: outcomeMeasures[4] :: groups[OG002]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 6 | dropped `Not evaluable`=0; `Complete remission with incomplete marrow recovery`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **6** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 6 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 6; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01296932 · outcome 4 · group `OG003` (BI 836826 25 Milligram)** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01296932] :: outcomeMeasures[4] :: groups[OG003]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 6 | dropped `Not evaluable`=1; `Complete remission with incomplete marrow recovery`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **6** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 6 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 6; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01296932 · outcome 4 · group `OG004` (BI 836826 50 Milligram)** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01296932] :: outcomeMeasures[4] :: groups[OG004]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 3 | dropped `Not evaluable`=0; `Complete remission with incomplete marrow recovery`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **3** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 3 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 3; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01296932 · outcome 4 · group `OG005` (BI 836826 100 Milligram)** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01296932] :: outcomeMeasures[4] :: groups[OG005]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 3 | dropped `Not evaluable`=0; `Complete remission with incomplete marrow recovery`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **3** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 3 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 3; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01296932 · outcome 4 · group `OG006` (BI 836826 200 Milligram)** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01296932] :: outcomeMeasures[4] :: groups[OG006]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 6 | dropped `Not evaluable`=0; `Complete remission with incomplete marrow recovery`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **6** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 6 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 6; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01296932 · outcome 4 · group `OG007` (BI 836826 400 Milligram)** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01296932] :: outcomeMeasures[4] :: groups[OG007]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 3 | dropped `Not evaluable`=0; `Complete remission with incomplete marrow recovery`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **3** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 3 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 3; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01296932 · outcome 4 · group `OG008` (BI 836826 800 Milligram)** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01296932] :: outcomeMeasures[4] :: groups[OG008]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 4 | dropped `Not evaluable`=0; `Complete remission with incomplete marrow recovery`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **4** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 4 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 4; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 3 · group `OG000` (BI 836826 1 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[3] :: groups[OG000]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 1 | dropped `Missing`=0; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **1** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 1 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 1; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 3 · group `OG001` (BI 836826 3 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[3] :: groups[OG001]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 4 | dropped `Missing`=1; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **4** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 4 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 4; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 3 · group `OG002` (BI 836826 9 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[3] :: groups[OG002]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 3 | dropped `Missing`=0; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **3** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 3 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 3; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 3 · group `OG003` (BI 836826 25 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[3] :: groups[OG003]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 4 | dropped `Missing`=0; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **4** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 4 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 4; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 3 · group `OG004` (BI 836826 50 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[3] :: groups[OG004]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 6 | dropped `Missing`=1; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **6** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 6 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 6; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 3 · group `OG005` (BI 836826 50mg iv (Korean Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[3] :: groups[OG005]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 1. Verdict `RECOVERABLE_DENOM_ONLY`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 7 | dropped `Missing`=0; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=1 (cl0, within_class, CONFLICT) |

Corrected reported denominator: **7** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 7 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 7; 1 within-class category collision(s) with CONFLICTING values overwrote stored labels, numerator not recoverable from the stored row

**NCT01403948 · outcome 3 · group `OG006` (BI 836826 100 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[3] :: groups[OG006]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 6 | dropped `Missing`=1; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **6** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 6 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 6; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 3 · group `OG007` (BI 836826 100 mg iv (Korean Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[3] :: groups[OG007]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 4 | dropped `Missing`=0; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **4** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 4 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 4; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 3 · group `OG008` (BI 836826 150 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[3] :: groups[OG008]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 6 | dropped `Missing`=1; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **6** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 6 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 6; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 3 · group `OG009` (BI 836826 200 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[3] :: groups[OG009]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 7 | dropped `Missing`=1; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **7** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 7 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 7; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 4 · group `OG000` (BI 836826 1 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[4] :: groups[OG000]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 1 | dropped `Missing`=0; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **1** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 1 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 1; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 4 · group `OG001` (BI 836826 3 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[4] :: groups[OG001]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 4 | dropped `Missing`=1; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **4** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 4 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 4; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 4 · group `OG002` (BI 836826 9 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[4] :: groups[OG002]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 3 | dropped `Missing`=0; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **3** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 3 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 3; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 4 · group `OG003` (BI 836826 25 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[4] :: groups[OG003]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 4 | dropped `Missing`=0; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **4** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 4 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 4; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 4 · group `OG004` (BI 836826 50 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[4] :: groups[OG004]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 6 | dropped `Missing`=1; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **6** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 6 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 6; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 4 · group `OG005` (BI 836826 50mg iv (Korean Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[4] :: groups[OG005]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 1. Verdict `RECOVERABLE_DENOM_ONLY`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 7 | dropped `Missing`=0; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=1 (cl0, within_class, CONFLICT) |

Corrected reported denominator: **7** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 7 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 7; 1 within-class category collision(s) with CONFLICTING values overwrote stored labels, numerator not recoverable from the stored row

**NCT01403948 · outcome 4 · group `OG006` (BI 836826 100 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[4] :: groups[OG006]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 6 | dropped `Missing`=1; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **6** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 6 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 6; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 4 · group `OG007` (BI 836826 100 mg iv (Korean Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[4] :: groups[OG007]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 4 | dropped `Missing`=0; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **4** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 4 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 4; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 4 · group `OG008` (BI 836826 150 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[4] :: groups[OG008]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 6 | dropped `Missing`=1; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **6** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 6 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 6; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01403948 · outcome 4 · group `OG009` (BI 836826 200 mg iv (Caucasian Patients))** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01403948] :: outcomeMeasures[4] :: groups[OG009]`  
contributing classes: 1; collisions: within_class × 1; of which value-conflicting: 0. Verdict `RECOVERABLE`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | (untitled) | 7 | dropped `Missing`=1; `Complete remission unconfirmed`=0 overwrote CR=`Complete remission`=0 (cl0, within_class, values agreed) |

Corrected reported denominator: **7** (from `denoms`, units `Participants`). All categories of the 1 contributing class(es) sum to 7 (residual +0). single contributing class; all its categories sum exactly to the reported denominator 7; 1 within-class category collision(s) (values agreed) — stored label does not identify which source category

**NCT01790503 · outcome 6 · group `OG000` (Combined 800 mg, 5 Days/Week)** — `ctg_results_bor_2010_2013.txt :: studies[nct=NCT01790503] :: outcomeMeasures[6] :: groups[OG000]`  
contributing classes: 8; collisions: cross_class × 28, within_class × 8; of which value-conflicting: 35. Verdict `UNRESOLVED`.

| source class | class title | class category sum | content the stored row lost |
|---|---|---|---|
| 0 | Age group: 18-64 years | 39 | dropped `Unable to access`=0; dropped `Unknown`=0; `CR+PR`=6 overwrote CR=`Complete response (CR)`=2 (cl0, within_class, CONFLICT) |
| 1 | Age group: 65+ years | 11 | dropped `Unable to access`=0; dropped `Unknown`=0; `Complete response (CR)`=0 overwrote CR=`CR+PR`=6 (cl0, cross_class, CONFLICT); `Partial response (PR)`=1 overwrote PR=`Partial response (PR)`=4 (cl0, cross_class, CONFLICT); `CR+PR`=1 overwrote CR=`Complete response (CR)`=0 (cl1, within_class, CONFLICT); `Stable disease`=6 overwrote SD=`Stable disease`=18 (cl0, cross_class, CONFLICT); `Progressive disease`=3 overwrote PD=`Progressive disease`=9 (cl0, cross_class, CONFLICT) |
| 2 | Complete resection | 21 | dropped `Unable to access`=0; dropped `Unknown`=0; `Complete response (CR)`=1 overwrote CR=`CR+PR`=1 (cl1, cross_class, values agreed); `Partial response (PR)`=2 overwrote PR=`Partial response (PR)`=1 (cl1, cross_class, CONFLICT); `CR+PR`=3 overwrote CR=`Complete response (CR)`=1 (cl2, within_class, CONFLICT); `Stable disease`=10 overwrote SD=`Stable disease`=6 (cl1, cross_class, CONFLICT); `Progressive disease`=5 overwrote PD=`Progressive disease`=3 (cl1, cross_class, CONFLICT) |
| 3 | Partial resection | 27 | dropped `Unable to access`=0; dropped `Unknown`=0; `Complete response (CR)`=1 overwrote CR=`CR+PR`=3 (cl2, cross_class, CONFLICT); `Partial response (PR)`=3 overwrote PR=`Partial response (PR)`=2 (cl2, cross_class, CONFLICT); `CR+PR`=4 overwrote CR=`Complete response (CR)`=1 (cl3, within_class, CONFLICT); `Stable disease`=13 overwrote SD=`Stable disease`=10 (cl2, cross_class, CONFLICT); `Progressive disease`=6 overwrote PD=`Progressive disease`=5 (cl2, cross_class, CONFLICT) |
| 4 | Baseline KPS: 70-89 | 17 | dropped `Unable to access`=0; dropped `Unknown`=0; `Complete response (CR)`=0 overwrote CR=`CR+PR`=4 (cl3, cross_class, CONFLICT); `Partial response (PR)`=1 overwrote PR=`Partial response (PR)`=3 (cl3, cross_class, CONFLICT); `CR+PR`=1 overwrote CR=`Complete response (CR)`=0 (cl4, within_class, CONFLICT); `Stable disease`=7 overwrote SD=`Stable disease`=13 (cl3, cross_class, CONFLICT); `Progressive disease`=8 overwrote PD=`Progressive disease`=6 (cl3, cross_class, CONFLICT) |
| 5 | Baseline KPS: 90-100 | 33 | dropped `Unable to access`=0; dropped `Unknown`=0; `Complete response (CR)`=2 overwrote CR=`CR+PR`=1 (cl4, cross_class, CONFLICT); `Partial response (PR)`=4 overwrote PR=`Partial response (PR)`=1 (cl4, cross_class, CONFLICT); `CR+PR`=6 overwrote CR=`Complete response (CR)`=2 (cl5, within_class, CONFLICT); `Stable disease`=17 overwrote SD=`Stable disease`=7 (cl4, cross_class, CONFLICT); `Progressive disease`=4 overwrote PD=`Progressive disease`=8 (cl4, cross_class, CONFLICT) |
| 6 | MGMT status: methylated | 22 | dropped `Unable to access`=0; dropped `Unknown`=0; `Complete response (CR)`=1 overwrote CR=`CR+PR`=6 (cl5, cross_class, CONFLICT); `Partial response (PR)`=3 overwrote PR=`Partial response (PR)`=4 (cl5, cross_class, CONFLICT); `CR+PR`=4 overwrote CR=`Complete response (CR)`=1 (cl6, within_class, CONFLICT); `Stable disease`=11 overwrote SD=`Stable disease`=17 (cl5, cross_class, CONFLICT); `Progressive disease`=3 overwrote PD=`Progressive disease`=4 (cl5, cross_class, CONFLICT) |
| 7 | MGMT status: unmethylated | 27 | dropped `Unable to access`=0; dropped `Unknown`=0; `Complete response (CR)`=1 overwrote CR=`CR+PR`=4 (cl6, cross_class, CONFLICT); `Partial response (PR)`=2 overwrote PR=`Partial response (PR)`=3 (cl6, cross_class, CONFLICT); `CR+PR`=3 overwrote CR=`Complete response (CR)`=1 (cl7, within_class, CONFLICT); `Stable disease`=12 overwrote SD=`Stable disease`=11 (cl6, cross_class, CONFLICT); `Progressive disease`=9 overwrote PD=`Progressive disease`=3 (cl6, cross_class, CONFLICT) |

Corrected reported denominator: **53** (from `denoms`, units `Participants`). All categories of the 8 contributing class(es) sum to 197 (residual +144). categories of the 8 contributing classes sum to 197 vs reported 53 (residual +144): classes are overlapping subgroups/timepoints, no single corrected reading

## 5.1 · NCT00654238 — the one collapse where an aggregate reading is additionally available

`ctg_results_bor_1999_2009.txt :: studies[nct=NCT00654238] :: outcomeMeasures[0] :: groups[OG000]`
("Sorafenib"). The four classes are the four histologic subtypes of the enrolled population
(`Differentiated`, `Poorly Differenitated` [sic, as spelled in the record], `Medullary`,
`Anaplastic`); the record's population description is "Responses were calculated by total enrolled
to each group by histologic subtype." All integer categories over the four classes sum to exactly
the reported denominator 55, which is consistent with the four classes partitioning the arm.

Under that reading — and it is a **reading conditional on disjointness, which the record states
nowhere and which the exact sum supports but does not prove** — the whole-arm corrected vector is
the class-wise sum:

| category | cl0 Differentiated | cl1 Poorly Differenitated | cl2 Medullary | cl3 Anaplastic | arm total |
|---|---|---|---|---|---|
| `Complete Response` | 0 | 0 | 0 | 0 | **0** |
| `Partial response` | 16 | 2 | 1 | 0 | **19** |
| `Stable Disease` | 22 | 1 | 2 | 0 | **25** |
| `Progressive Disease` | 1 | 1 | 0 | 1 | **3** |
| `Not Evaluable for Response` (dropped by the producer) | 5 | 2 | 0 | 1 | **8** |
| class sum | 44 | 6 | 3 | 2 | **55** = reported denominator |

The derived row stores `CR=0, PR=0, SD=0, PD=1`, `evaluable_n = 1` — the `Anaplastic` class alone
(n=2, minus its dropped `Not Evaluable`=1), because it is the last class iterated. Against a
reported denominator of 55 that is a 54-participant loss, and it is the largest single-row
distortion in my group.

I record the aggregate vector as **conditional**, not as the verdict. The row's verdict stays
`RECOVERABLE_DENOM_ONLY`: the denominator 55 is read directly and is not conditional; the four-cell
vector requires the unstated disjointness assumption. No other multi-class row in my group admits
even a conditional aggregate — `NCT01790503`'s eight classes sum to 197 against 53 and are
overlapping stratifications (§6).

## 6 · The one UNRESOLVED row, stated in full

`NCT01790503` · payload `ctg_results_bor_2010_2013.txt` · outcome 6 · group `OG000`
("Combined 800 mg, 5 Days/Week"). Reported `Participants` denominator: **53**.

The outcome measure carries **8 classes** which are not one partition of the arm but **four
independent stratifications of the same participants**: age (18-64 / 65+), resection
(complete / partial), baseline KPS (70-89 / 90-100), and MGMT status (methylated / unmethylated).
Every one of the eight classes carries the same 7 category titles. Two further problems compound it:

1. Each class also carries a `CR+PR` category, which the producer's `CR` regex matches
   (`^\s*(complete response|complete remission|CR)\b`), so a **combined** responder count
   overwrites the class's own `Complete response (CR)` count in every class.
2. The producer then iterates all 8 classes and the last one wins, so the stored four cells are the
   MGMT-unmethylated stratum's values with `CR` replaced by that stratum's `CR+PR`.

Summing all integer categories over all 8 classes gives 197 against a reported 53
(residual **+144**). Excluding the double-counting `CR+PR` category, the four stratifications sum
to 43, 41, 43 and 42 participants respectively — mutually inconsistent, and none equal to 53.

**Verdict: `UNRESOLVED`.** The denominator the trial reported (53) is readable, but no single
corrected four-cell reading follows from this record: the strata do not reconcile to it, no
selection basis among the four stratifications is stated anywhere in the record, and the record
gives no un-stratified category vector for this group. Choosing one stratification would be an
invention. This is a result, not a gap to be papered over.

## 7 · Limits

- Everything above is a reading of what the **records report**. No patient-level data, no
  re-analysis, no efficacy/safety/selectivity/clinical-readiness claim of any kind.
- Cross-shard duplicate reconciliation is explicitly not attempted; it belongs to the parent.
- `RECOVERABLE` means the record supports one corrected reading. It is **not** a statement that the
  derived row should be repaired, nor that the parked manuscript may be reopened.
- Rows classified `valid` with `overwrite_scope=none` were out of scope and were not opened.

