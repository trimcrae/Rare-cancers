# LEAF-QB-group2 — why selected cohort denominators exceed registered enrollment, 45 assigned trials

Leaf worker output. Question B, NCT group 2 (`LEAF-ASSIGNMENTS/QB-group2.txt`, 45 trials).
Written 2026-09-08. No network access was used. Every number below is read from the cached
ClinicalTrials.gov payloads or from Job 2's tables; nothing is fetched, recomputed globally, or estimated.

## Provenance and integrity

- Cache: `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5/`
  (branch `literature-cache` @ `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`).
- `sha256sum -c SHA256-MANIFEST.txt` -> all 13 files `OK`, **exit code 0**.
- Job 2 inputs used as given, not rebuilt: `CURATION-endpoint-identity-and-overlap-artifacts/OVERLAP-enrollment-check.tsv`
  (per-trial excess) and `.../SELECTED-cohort-response-measurements.tsv` (the selected cohorts and their denominators).
  The selection rule (`RULE-PREREGISTERED.md`) was read but not re-applied.
- Source pointers in this file are `(payload file, NCT, outcome-measure index `om[i]` as ordered in
  `resultsSection.outcomeMeasuresModule.outcomeMeasures`, results-group title, `denoms` value with `units == "Participants"`)`.
- **Coverage: 45 of 45 assigned trials reached.** Every assigned NCT was found in the cache and every one appears in
  `OVERLAP-enrollment-check.tsv`. No NCT outside the assigned list was examined.

## Cache limitation that bounds every 'UNRESOLVED' below

The cached queries requested only
`protocolSection.identificationModule.nctId, protocolSection.conditionsModule, protocolSection.designModule,`
`protocolSection.armsInterventionsModule.armGroups, resultsSection.outcomeMeasuresModule`.
The cache therefore contains **no `participantFlowModule` and no `baselineCharacteristicsModule`**. Where a trial's
excess is not explained by a pooled row, a nested subgroup, a cross-cutting partition, a title variant or an explicit
re-randomisation statement inside an outcome measure, the record as cached genuinely cannot settle it, and the answer
is `UNRESOLVED` rather than a guess. That is a limitation of this cache, not a claim that the information does not exist.

## Enrollment type — checked first, per the task

**All 45 assigned trials carry `enrollmentInfo.type == "ACTUAL"`.** None is `ESTIMATED`.
So for this group there is no trial whose 'excess' is the artefact of an estimated enrollment sitting below a reported
denominator; the estimated-enrollment category is empty here and nothing had to be separated out on that ground.
Verified per trial from `protocolSection.designModule.enrollmentInfo` in the cached record, and independently from the
`enrollment_type` column of `OVERLAP-enrollment-check.tsv`; the two agree for all 45.

## Mechanism vocabulary used

Job 2's candidate list was used where it fits, and extended where the record showed something the list did not name.

| code | mechanism |
| --- | --- |
| `M1` | an explicitly pooled/total/combined results cohort selected alongside its own component cohorts |
| `M2` | subgroup or restricted-analysis-population cohorts selected alongside the parent cohort that contains them |
| `M3` | two or more complete partitions of one population on different axes, all selected |
| `M4` | one patient set reported under different results-group titles in different outcome measures, so the title key counts it more than once |
| `M5` | the record states participants were re-randomised or crossed over and analysed under more than one group |
| `M6` | cohorts that are mutually exclusive as recorded whose denominators nonetheless exceed the ACTUAL enrollment field, with no overlap mechanism in the record |
| `M5+M6` | part of the excess is a documented crossover re-count, the remainder has no overlap mechanism in the record (NCT02754141 only) |

Two of Job 2's candidates did not occur in this group and are recorded as absent, not as unexamined:
`enrollment field recorded as ESTIMATED` (0 trials, all 45 are ACTUAL) and a stand-alone
`per-measure denominators drawn at different timepoints` cause. Timepoint divergence *was* observed, but in every case
it accompanied a title-variant duplication or a pooled row rather than driving the excess by itself; it is noted
inline for NCT02319044, NCT02347917, NCT02570308, NCT02711956 and NCT02983799.

## Distribution over the 45 assigned trials

| code | trials |
| --- | ---: |
| `M1` | 17 |
| `M4` | 9 |
| `M2` | 8 |
| `M3` | 4 |
| `M5` | 4 |
| `M6` | 2 |
| `M5+M6` | 1 |
| **total** | **45** |

Reducible to a non-overlapping set from the record alone: **39 YES**, **5 NO (UNRESOLVED)**, **1 PARTIAL (UNRESOLVED)**.

Of the 39 reducible trials, the reduced non-overlapping sum equals the registered ACTUAL enrollment **exactly** in
23 of them: NCT02335983, NCT02347917, NCT02391116, NCT02404441, NCT02411591, NCT02414139, NCT02451930, NCT02527434, NCT02551991, NCT02570308, NCT02592707, NCT02599402, NCT02606461, NCT02616393, NCT02625623, NCT02711956, NCT02735980, NCT02748564, NCT02759835, NCT02844439, NCT02895360, NCT02910583, NCT02963493.
In the rest the reduced sum is below registered enrollment, which is the expected direction (analysis sets are subsets
of the enrolled population).

## Scope statement

Nothing here is a claim about unique patients across trials, about any global count, or about efficacy, safety,
selectivity or clinical readiness. Job 2's global figures (8,728 selected cohorts; 180 trials with excess; 22,578
excess participant-slots) are cited only as the context this leaf was carved from; they are not re-derived and are not
findings of this file.

## Per-trial adjudication

### NCT02319044

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 267) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 4 selected cohorts, denominators sum 514, registered enrollment 267, excess **247**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** 'Total' 257 (om6 DCR, pooled_label=True) is the sum of the three arm cohorts selected from om1: 65+129+63=257.

**Note.** Also a timepoint mismatch: the pooled row is measured 'After 6 months' (om6) while the arm rows are 'After 12 months' (om1). 257 <= 267 registered.

**Non-overlapping set from the record alone: YES** — {Total 257} (om6) OR {MEDI4736 65, MEDI4736 + Tremelimumab 129, Tremelimumab 63} (om1) = 257 (sum 257, vs registered 267).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 129 | 1 | PRIMARY | MEDI4736 + Tremelimumab | Objective Response Rate at 12 Months | After 12 months | False |
| 65 | 1 | PRIMARY | MEDI4736 | Objective Response Rate at 12 Months | After 12 months | False |
| 63 | 1 | PRIMARY | Tremelimumab | Objective Response Rate at 12 Months | After 12 months | False |
| 257 | 6 | SECONDARY | Total | Disease Control Rate (DCR) | After 6 months | True |

### NCT02335983

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 107) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 8 selected cohorts, denominators sum 171, registered enrollment 107, excess **64**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** 'RRMM: Combined Carfilzomib 70 mg/m²' 46 = 'RRMM Dose-evaluation: Carfilzomib 70 mg/m²' 12 + 'RRMM Dose-expansion: Carfilzomib 70 mg/m²' 34; 'NDMM: Combined Carfilzomib 70 mg/m²' 18 = 'NDMM Dose-evaluation: Carfilzomib 56/70 mg/m²' 9 + 'NDMM Dose-expansion: Carfilzomib 70 mg/m²' 9. All 8 rows are om9.

**Note.** Excess 64 = 46 + 18 exactly. Removing both 'Combined' rows gives 107, equal to registered ACTUAL enrollment.

**Non-overlapping set from the record alone: YES** — the 6 non-'Combined' cohorts = 9+33+9+34+12+10 = 107 (sum 107, vs registered 107).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 46 | 9 | SECONDARY | RRMM: Combined Carfilzomib 70 mg/m² | Overall Response Rate (ORR) | Response assessments were performed on day 1 of each treatment cycle f… | False |
| 34 | 9 | SECONDARY | RRMM Dose-expansion: Carfilzomib 70 mg/m² | Overall Response Rate (ORR) | Response assessments were performed on day 1 of each treatment cycle f… | False |
| 33 | 9 | SECONDARY | NDMM Dose-expansion: Carfilzomib 56 mg/m² | Overall Response Rate (ORR) | Response assessments were performed on day 1 of each treatment cycle f… | False |
| 18 | 9 | SECONDARY | NDMM: Combined Carfilzomib 70 mg/m² | Overall Response Rate (ORR) | Response assessments were performed on day 1 of each treatment cycle f… | False |
| 12 | 9 | SECONDARY | RRMM Dose-evaluation: Carfilzomib 70 mg/m² | Overall Response Rate (ORR) | Response assessments were performed on day 1 of each treatment cycle f… | False |
| 10 | 9 | SECONDARY | RRMM Dose-evaluation: Carfilzomib 56 mg/m² | Overall Response Rate (ORR) | Response assessments were performed on day 1 of each treatment cycle f… | False |
| 9 | 9 | SECONDARY | NDMM Dose-evaluation: Carfilzomib 56/70 mg/m² | Overall Response Rate (ORR) | Response assessments were performed on day 1 of each treatment cycle f… | False |
| 9 | 9 | SECONDARY | NDMM Dose-expansion: Carfilzomib 70 mg/m² | Overall Response Rate (ORR) | Response assessments were performed on day 1 of each treatment cycle f… | False |

### NCT02337829

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 48) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 6 selected cohorts, denominators sum 94, registered enrollment 48, excess **46**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** 'Total Relapse/Refractory Subjects' 31 = 18 + 13; 'Total Treatment Naive Subjects' 16 = 6 + 10. All 6 rows are om0, pooled_label=True on both Total rows.

**Note.** Selected total 94; excess 46 = 94 - 48 = 31 + 16 - 1. The reduced set is 47, one below the registered 48; the record does not say which enrolled subject is absent from the ORR analysis.

**Non-overlapping set from the record alone: YES** — {Acalabrutinib 100 mg BID R/R 18, 200 mg QD R/R 13, 100 mg BID TN 6, 200 mg QD TN 10} = 47 (sum 47, vs registered 48).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 31 | 0 | PRIMARY | Total Relapse/Refractory Subjects | Response Based on Overall Response Rate | Cycle 1 (28 Days) to 6 months | True |
| 18 | 0 | PRIMARY | Acalabrutinib 100 mg BID Relapse/Refractory | Response Based on Overall Response Rate | Cycle 1 (28 Days) to 6 months | False |
| 16 | 0 | PRIMARY | Total Treatment Naive Subjects | Response Based on Overall Response Rate | Cycle 1 (28 Days) to 6 months | True |
| 13 | 0 | PRIMARY | Acalabrutinib 200 mg QD Relapse/Refractory | Response Based on Overall Response Rate | Cycle 1 (28 Days) to 6 months | False |
| 10 | 0 | PRIMARY | Acalabrutinib 200 mg QD Treatment Naive | Response Based on Overall Response Rate | Cycle 1 (28 Days) to 6 months | False |
| 6 | 0 | PRIMARY | Acalabrutinib 100 mg BID Treatment Naive | Response Based on Overall Response Rate | Cycle 1 (28 Days) to 6 months | False |

### NCT02347917

- Mechanism: **`M4`** — TITLE_VARIANT_DUPLICATE - one patient set reported under different results-group titles in different outcome measures, so the title key counts it more than once
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 28) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 6 selected cohorts, denominators sum 82, registered enrollment 28, excess **54**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om5 popDesc: 'mITT ... separately for Phase 1 part (n=4), Phase 2 part (n=24) and Phase 2 part including 1 participant with MPM in Phase 1 part (n=25)'. The 25 rows (om5 and om6) are the same 25 patients under two titles; 'NSCLC: ... (Phase 1 Part)' 3 and 'MPM: ... (Phase 1 Part)' 1 partition the Phase 1 row of 4.

**Note.** Reduced set equals registered enrollment 28 exactly. Note om6 (RR/DCR) and om5 (BOR) carry different timeframes for the same 25 patients.

**Non-overlapping set from the record alone: YES** — {'MPM or NSCLC: BBI608 + Pem + CDDP (Phase 1 Part)' 4, 'MPM: BBI608 + Pem + CDDP (Phase 2 Part)' 24} = 28 (sum 28, vs registered 28).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 25 | 5 | SECONDARY | MPM: BBI608 + Pem + CDDP (Phase 2 Part Including Participants With MPM in Phase 1 Part) | Best Overall Response | Every 6 weeks from the first dose of BBI608 until Week 30, and every 9… | False |
| 24 | 5 | SECONDARY | MPM: BBI608 + Pem + CDDP (Phase 2 Part) | Best Overall Response | Every 6 weeks from the first dose of BBI608 until Week 30, and every 9… | False |
| 4 | 5 | SECONDARY | MPM or NSCLC: BBI608 + Pem + CDDP (Phase 1 Part) | Best Overall Response | Every 6 weeks from the first dose of BBI608 until Week 30, and every 9… | False |
| 3 | 5 | SECONDARY | NSCLC: BBI608 + Pem + CDDP (Phase 1 Part) | Best Overall Response | Every 6 weeks from the first dose of BBI608 until Week 30, and every 9… | False |
| 1 | 5 | SECONDARY | MPM: BBI608 + Pem +CDDP (Phase 1 Part) | Best Overall Response | Every 6 weeks from the first dose of BBI608 until Week 30, and every 9… | False |
| 25 | 6 | SECONDARY | MPM: BBI608 + Pem + CDDP (Phase 2 Part Including 1 Participant With MPM in Phase 1 Part) | Response Rate (RR) and Disease Control Rate (DCR) | From BBI608 administration to death from any cause, about 17 months | False |

### NCT02370238

- Mechanism: **`M4`** — TITLE_VARIANT_DUPLICATE - one patient set reported under different results-group titles in different outcome measures, so the title key counts it more than once
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 194) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 4 selected cohorts, denominators sum 222, registered enrollment 194, excess **28**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om2 'Objective Response Rate (ORR)' groups 'Paclitaxel+Reparixin (Group 1) - ITT Population' 57 and 'Paclitaxel+Placebo (Group 2)' 54; om4 'Duration of Overall Response (DOR)' groups 'Group 1 - Response Evaluable Population' 57 and 'Group 2 - Response-Evaluable Population' 54.

**Note.** Same two randomised groups, same denominators, two title spellings. 111 <= 194 registered; the remaining 83 are enrolled patients outside the response-evaluable population.

**Non-overlapping set from the record alone: YES** — {Group 1 57, Group 2 54} = 111 (sum 111, vs registered 194).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 57 | 2 | SECONDARY | Paclitaxel+Reparixin (Group 1) - ITT Population | Objective Response Rate (ORR) | Baseline up to every 8 weeks until documented disease progression, up … | False |
| 54 | 2 | SECONDARY | Paclitaxel+Placebo (Group 2) | Objective Response Rate (ORR) | Baseline up to every 8 weeks until documented disease progression, up … | False |
| 57 | 4 | SECONDARY | Group 1 - Response Evaluable Population | Duration of Overall Response (DOR) | Baseline up to every 8 weeks until documented disease progression, up … | False |
| 54 | 4 | SECONDARY | Group 2 - Response-Evaluable Population | Duration of Overall Response (DOR) | Baseline up to every 8 weeks until documented disease progression, up … | False |

### NCT02391116

- Mechanism: **`M3`** — CROSSCUT_PARTITIONS - two or more complete partitions of one population on different axes, all selected
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 67) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 8 selected cohorts, denominators sum 201, registered enrollment 67, excess **134**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om0 total population 67; om1 partitions it by CD79b status (45 + 9 + 13 = 67); om2 partitions the same 67 by DLBCL cell-of-origin subtype (30 + 19 + 15 + 3 = 67).

**Note.** Three complete partitions of one 67-patient population on three axes. Excess 134 = 2 x 67.

**Non-overlapping set from the record alone: YES** — {'Copanlisib (Aliqopa, BAY80-6946)' 67} (om0) (sum 67, vs registered 67).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 67 | 0 | PRIMARY | Copanlisib (Aliqopa, BAY80-6946) | Objective Response Rate (ORR) in Total Population Based on Investigator Assessment | From start of study treatment assessed up to 24 weeks after the last p… | False |
| 45 | 1 | PRIMARY | CD79b Wild-type | ORR by CD79b Status Based on Investigator Assessment | From start of study treatment assessed up to 24 weeks after the last p… | False |
| 13 | 1 | PRIMARY | CD79b Status Missing | ORR by CD79b Status Based on Investigator Assessment | From start of study treatment assessed up to 24 weeks after the last p… | False |
| 9 | 1 | PRIMARY | CD79b Mutant | ORR by CD79b Status Based on Investigator Assessment | From start of study treatment assessed up to 24 weeks after the last p… | False |
| 30 | 2 | PRIMARY | Germinal Center B-cell-like (GCB) | ORR by DLBCL/COO Subtype Based on Investigator Assessment | From start of study treatment assessed up to 24 weeks after the last p… | False |
| 19 | 2 | PRIMARY | Activated B-cell-like (ABC) | ORR by DLBCL/COO Subtype Based on Investigator Assessment | From start of study treatment assessed up to 24 weeks after the last p… | False |
| 15 | 2 | PRIMARY | DLBCL/COO Subtype Missing | ORR by DLBCL/COO Subtype Based on Investigator Assessment | From start of study treatment assessed up to 24 weeks after the last p… | False |
| 3 | 2 | PRIMARY | Unclassifiable | ORR by DLBCL/COO Subtype Based on Investigator Assessment | From start of study treatment assessed up to 24 weeks after the last p… | False |

### NCT02399085

- Mechanism: **`M4`** — TITLE_VARIANT_DUPLICATE - one patient set reported under different results-group titles in different outcome measures, so the title key counts it more than once
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 81) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 2 selected cohorts, denominators sum 160, registered enrollment 81, excess **79**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om0 group 'Treatment (MOR00208, Lenalidomide)' 80 and om6 group 'Tafasitamab (MOR00208) + Lenalidomide (LEN)' 80; both popDesc name the same FAS ('all participants who received at least one dose of MOR00208 and at least one dose of LEN').

**Note.** Single-arm trial; one 80-patient analysis set counted twice because the results-group title differs between outcome measures. 80 <= 81 registered.

**Non-overlapping set from the record alone: YES** — {the single FAS of 80} (sum 80, vs registered 81).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 80 | 0 | PRIMARY | Treatment (MOR00208, Lenalidomide) | Number of Participants With Best Objective Response Rate (ORR) | Approximately 4.5 years after first participant enrolled; Approximatel… | False |
| 80 | 6 | SECONDARY | Tafasitamab (MOR00208) + Lenalidomide (LEN) | Disease Control Rate (DCR) by IRC Evaluation | Approximately 2.5 years after first participant enrolled | False |

### NCT02404441

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 319) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 14 selected cohorts, denominators sum 696, registered enrollment 319, excess **377**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** Three-level nesting. om2: 'All Phase II Patients' 261 = Melanoma 400 mg/q4w 61 + NSCLC 300 mg/q3w 59 + NSCLC 400 mg/q4w 59 + ATC 400 mg/q4w 42 + TNBC 400 mg/q4w 40. om11: 'All Phase I Patients' 58 = 'All Phase I q2w' 42 + 'All Phase I q4w' 16; 42 = 1mg/kg q2w 16 + 3mg/kg q2w 15 + 10mg/kg q2w 11; 16 = 5mg/kg q4w 10 + 3mg/kg q4w 6.

**Note.** None of the pooled rows carries a 'total'-vocabulary title, so pooled_label=False on all 14 rows. Reduced set equals registered enrollment 319 exactly.

**Non-overlapping set from the record alone: YES** — {'All Phase I Patients' 58, 'All Phase II Patients' 261} = 319 (sum 319, vs registered 319).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 261 | 2 | PRIMARY | All Phase II Patients | Phase ll: Overall Response Rate (ORR) Per Response Evaluation Criteria in Solid Tumors (RECIST v1.1) | 61 months | False |
| 61 | 2 | PRIMARY | Melanoma 400 mg/q4w | Phase ll: Overall Response Rate (ORR) Per Response Evaluation Criteria in Solid Tumors (RECIST v1.1) | 61 months | False |
| 59 | 2 | PRIMARY | NSCLC 300 mg/q3w | Phase ll: Overall Response Rate (ORR) Per Response Evaluation Criteria in Solid Tumors (RECIST v1.1) | 61 months | False |
| 59 | 2 | PRIMARY | NSCLC 400 mg/q4w | Phase ll: Overall Response Rate (ORR) Per Response Evaluation Criteria in Solid Tumors (RECIST v1.1) | 61 months | False |
| 42 | 2 | PRIMARY | ATC 400 mg/q4w | Phase ll: Overall Response Rate (ORR) Per Response Evaluation Criteria in Solid Tumors (RECIST v1.1) | 61 months | False |
| 40 | 2 | PRIMARY | TNBC 400 mg/q4w | Phase ll: Overall Response Rate (ORR) Per Response Evaluation Criteria in Solid Tumors (RECIST v1.1) | 61 months | False |
| 58 | 11 | SECONDARY | All Phase I Patients | Phase l: Overall Response Rate (ORR) as Per Investigator Based on RECIST v1.1 | 27 months | False |
| 42 | 11 | SECONDARY | All Phase I q2w | Phase l: Overall Response Rate (ORR) as Per Investigator Based on RECIST v1.1 | 27 months | False |
| 16 | 11 | SECONDARY | 1mg/kg q2w | Phase l: Overall Response Rate (ORR) as Per Investigator Based on RECIST v1.1 | 27 months | False |
| 16 | 11 | SECONDARY | All Phase I q4w | Phase l: Overall Response Rate (ORR) as Per Investigator Based on RECIST v1.1 | 27 months | False |
| 15 | 11 | SECONDARY | 3mg/kg q2w | Phase l: Overall Response Rate (ORR) as Per Investigator Based on RECIST v1.1 | 27 months | False |
| 11 | 11 | SECONDARY | 10mg/kg q2w | Phase l: Overall Response Rate (ORR) as Per Investigator Based on RECIST v1.1 | 27 months | False |
| 10 | 11 | SECONDARY | 5mg/kg q4w | Phase l: Overall Response Rate (ORR) as Per Investigator Based on RECIST v1.1 | 27 months | False |
| 6 | 11 | SECONDARY | 3mg/kg q4w | Phase l: Overall Response Rate (ORR) as Per Investigator Based on RECIST v1.1 | 27 months | False |

### NCT02411591

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 66) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 4 selected cohorts, denominators sum 132, registered enrollment 66, excess **66**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om7: 'Total Enrolled Participants (Necitumumab + Abemaciclib)' 66 (pooled_label=True) = Cohort 1 3 + Cohort 2 57 + Cohort 3 6.

**Note.** Excess 66 is exactly the pooled row. Reduced set equals registered enrollment 66.

**Non-overlapping set from the record alone: YES** — {'Total Enrolled Participants (Necitumumab + Abemaciclib)' 66} OR {Cohort 1 3, Cohort 2 57, Cohort 3 6} = 66 (sum 66, vs registered 66).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 66 | 7 | SECONDARY | Total Enrolled Participants (Necitumumab + Abemaciclib) | Percentage of Participants With a Best Overall Response of Complete Response (CR), Partial Response (PR), and Stable Disease (SD) (Disease Control Rate [DCR]) | Baseline to measured progressive disease or start of new anti-cancer t… | True |
| 57 | 7 | SECONDARY | Cohort 2 (Necitumumab 800 mg + Abemaciclib 150 mg) | Percentage of Participants With a Best Overall Response of Complete Response (CR), Partial Response (PR), and Stable Disease (SD) (Disease Control Rate [DCR]) | Baseline to measured progressive disease or start of new anti-cancer t… | False |
| 6 | 7 | SECONDARY | Cohort 3 (Necitumumab 800 mg + Abemaciclib 200 mg) | Percentage of Participants With a Best Overall Response of Complete Response (CR), Partial Response (PR), and Stable Disease (SD) (Disease Control Rate [DCR]) | Baseline to measured progressive disease or start of new anti-cancer t… | False |
| 3 | 7 | SECONDARY | Cohort 1 (Necitumumab 800 mg + Abemaciclib 100 mg) | Percentage of Participants With a Best Overall Response of Complete Response (CR), Partial Response (PR), and Stable Disease (SD) (Disease Control Rate [DCR]) | Baseline to measured progressive disease or start of new anti-cancer t… | False |

### NCT02414139

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 373) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 12 selected cohorts, denominators sum 533, registered enrollment 373, excess **160**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** All 12 rows are om0. 'Cohort 4 + Cohort 6.2: All Pre-treated Patients With MET Mutation Regardless of MET GCN (2/3L)' 100 = 'Cohort 4' 69 + 'Cohort 6.2 (Expansion of Cohort 4)' 31; 'Cohort 5b + Cohort 7: All Treatment-naive With MET Mutation Regardless of MET GCN (1L)' 60 = 'Cohort 5b' 28 + 'Cohort 7 (Expansion of Cohort 5b)' 32.

**Note.** Excess 160 = 100 + 60 exactly. The 10 individual cohorts (1a 69, 1b 42, 2 54, 3 30, 4 69, 5a 15, 5b 28, 6.1 3, 6.2 31, 7 32) sum to 373 = registered ACTUAL enrollment.

**Non-overlapping set from the record alone: YES** — the 10 individual cohorts (1a 69, 1b 42, 2 54, 3 30, 4 69, 5a 15, 5b 28, 6.1 3, 6.2 31, 7 32) = 373 (sum 373, vs registered 373).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 100 | 0 | PRIMARY | Cohort 4 + Cohort 6.2: All Pre-treated Patients With MET Mutation Regardless of MET GCN (2/3L) | Overall Response Rate (ORR) by Blinded Independent Review Committee (BIRC) Assessment | Up to approximately 5 years | False |
| 69 | 0 | PRIMARY | Cohort 1a: Pre-treated Patients With MET GCN ≥ 10 (2/3L) | Overall Response Rate (ORR) by Blinded Independent Review Committee (BIRC) Assessment | Up to approximately 5 years | False |
| 69 | 0 | PRIMARY | Cohort 4: Pre-treated Patients With MET Mutation Regardless of MET GCN (2/3L) | Overall Response Rate (ORR) by Blinded Independent Review Committee (BIRC) Assessment | Up to approximately 5 years | False |
| 60 | 0 | PRIMARY | Cohort 5b + Cohort 7: All Treatment-naive With MET Mutation Regardless of MET GCN (1L) | Overall Response Rate (ORR) by Blinded Independent Review Committee (BIRC) Assessment | Up to approximately 5 years | False |
| 54 | 0 | PRIMARY | Cohort 2: Pre-treated Patients With MET GCN ≥ 4 and < 6 (2/3L) | Overall Response Rate (ORR) by Blinded Independent Review Committee (BIRC) Assessment | Up to approximately 5 years | False |
| 42 | 0 | PRIMARY | Cohort 1b: Pre-treated Patients With MET GCN ≥ 6 and < 10 (2/3L) | Overall Response Rate (ORR) by Blinded Independent Review Committee (BIRC) Assessment | Up to approximately 5 years | False |
| 32 | 0 | PRIMARY | Cohort 7 (Expansion of Cohort 5b): Treatment-naïve With MET Mutation Regardless of MET GCN (1L) | Overall Response Rate (ORR) by Blinded Independent Review Committee (BIRC) Assessment | Up to approximately 5 years | False |
| 31 | 0 | PRIMARY | Cohort 6.2 (Expansion of Cohort 4): Pre-treated Patients With MET Mutation (2L) | Overall Response Rate (ORR) by Blinded Independent Review Committee (BIRC) Assessment | Up to approximately 5 years | False |
| 30 | 0 | PRIMARY | Cohort 3: Pre-treated Patients With MET GCN < 4 (2/3L) | Overall Response Rate (ORR) by Blinded Independent Review Committee (BIRC) Assessment | Up to approximately 5 years | False |
| 28 | 0 | PRIMARY | Cohort 5b: Treatment-naïve Patients With MET Mutation Regardless of MET GCN (1L) | Overall Response Rate (ORR) by Blinded Independent Review Committee (BIRC) Assessment | Up to approximately 5 years | False |
| 15 | 0 | PRIMARY | Cohort 5a: Treatment-naïve Patients With MET GCN ≥10 (1L) | Overall Response Rate (ORR) by Blinded Independent Review Committee (BIRC) Assessment | Up to approximately 5 years | False |
| 3 | 0 | PRIMARY | Cohort 6.1 (Expansion of Cohort 1a): Pre-treated Patients MET GCN ≥ 10 Without MET Mutation (2L) | Overall Response Rate (ORR) by Blinded Independent Review Committee (BIRC) Assessment | Up to approximately 5 years | False |

### NCT02432846

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 88) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 6 selected cohorts, denominators sum 140, registered enrollment 88, excess **52**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om5: 'Intuvax (INN: Ilixadencel) + Sunitinib, Total (Both Strata)' 45 = Intermediate-risk 32 + High-risk 13; 'Sunitinib-only, Total (Both Strata)' 25 = Intermediate-risk 19 + High-risk 6.

**Note.** Selected total 140; excess 52 = 140 - 88. The four stratum rows sum to 70, i.e. 18 registered patients are outside this ORR analysis, and the two pooled rows add another 70. Both pooled rows carry 'Total' inside a longer title, so pooled_label=False.

**Non-overlapping set from the record alone: YES** — {Intuvax+Sunitinib Intermediate-risk 32, High-risk 13, Sunitinib-only Intermediate-risk 19, High-risk 6} = 70 (sum 70, vs registered 88).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 45 | 5 | SECONDARY | Intuvax (INN: Ilixadencel) + Sunitinib, Total (Both Strata) | Objective Response Rate (ORR) From Start of Sunitinib Treatment and Duration of Response in Each Subgroup. | From start of sunitinib treatment up to 18 months | False |
| 32 | 5 | SECONDARY | Intuvax (INN: Ilixadencel) + Sunitinib, Intermediate-risk | Objective Response Rate (ORR) From Start of Sunitinib Treatment and Duration of Response in Each Subgroup. | From start of sunitinib treatment up to 18 months | False |
| 25 | 5 | SECONDARY | Sunitinib-only, Total (Both Strata) | Objective Response Rate (ORR) From Start of Sunitinib Treatment and Duration of Response in Each Subgroup. | From start of sunitinib treatment up to 18 months | False |
| 19 | 5 | SECONDARY | Sunitinib-only, Intermediate-risk | Objective Response Rate (ORR) From Start of Sunitinib Treatment and Duration of Response in Each Subgroup. | From start of sunitinib treatment up to 18 months | False |
| 13 | 5 | SECONDARY | Intuvax (INN: Ilixadencel) + Sunitinib, High-risk | Objective Response Rate (ORR) From Start of Sunitinib Treatment and Duration of Response in Each Subgroup. | From start of sunitinib treatment up to 18 months | False |
| 6 | 5 | SECONDARY | Sunitinib-only, High-risk | Objective Response Rate (ORR) From Start of Sunitinib Treatment and Duration of Response in Each Subgroup. | From start of sunitinib treatment up to 18 months | False |

### NCT02451930

- Mechanism: **`M2`** — NESTED_SUBGROUP - subgroup or restricted-analysis-population cohorts selected alongside the parent cohort that contains them
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 71) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 3 selected cohorts, denominators sum 132, registered enrollment 71, excess **61**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om1 'Part A Cohort 2, Part B: 800 mg Neci + 200 mg Pembro' 61 is nested inside om2 'Part A Cohort 2, Part B and Part C: 800 mg Neci + 200mg Pembro' 68 (the same patients plus the 7 Part C Japan patients).

**Note.** om1 popDesc and om2 popDesc both state that Part A cohort 2 patients are analysed together with Part B. Reduced set equals registered enrollment 71 exactly.

**Non-overlapping set from the record alone: YES** — {'Part A Cohort 1: 600 mg Neci + 200 mg Pembro' 3, 'Part A Cohort 2, Part B and Part C: 800 mg Neci + 200mg Pembro' 68} = 71 (sum 71, vs registered 71).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 61 | 1 | PRIMARY | Part A Cohort 2, Part B: 800 mg Neci + 200 mg Pembro | Percentage of Participants Who Achieve Best Overall Tumor Response of Complete Response (CR) or Partial Response (PR) (Objective Response Rates [ORR]) in Part A and Part B | Baseline to Measured Progressive Disease or Start of New Anti-Cancer T… | False |
| 3 | 1 | PRIMARY | Part A Cohort 1: 600 mg Neci + 200 mg Pembro | Percentage of Participants Who Achieve Best Overall Tumor Response of Complete Response (CR) or Partial Response (PR) (Objective Response Rates [ORR]) in Part A and Part B | Baseline to Measured Progressive Disease or Start of New Anti-Cancer T… | False |
| 68 | 2 | SECONDARY | Part A Cohort 2, Part B and Part C: 800 mg Neci + 200mg Pembro | Percentage of Participants Who Achieve Best Overall Tumor Response of Complete Response (CR) or Partial Response (PR) (Objective Response Rates [ORR]) in Part A Cohort 2, Part B and Part C | Baseline to Measured Progressive Disease or Start of New Anti-Cancer T… | False |

### NCT02494570

- Mechanism: **`M4`** — TITLE_VARIANT_DUPLICATE - one patient set reported under different results-group titles in different outcome measures, so the title key counts it more than once
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 34) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 2 selected cohorts, denominators sum 62, registered enrollment 34, excess **28**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om0 'Objective Overall Response Rate (ORR)' group 'Nab-Sirolimus' 31 and om5 (POST_HOC) 'Disease Control Rate' group 'Experimental: Nab-Sirolimus' 31 - one single-arm population, two title spellings.

**Note.** 31 <= 34 registered ACTUAL. Excess 28 is entirely the duplicated 31 minus the 3 enrolled patients outside the efficacy-evaluable set.

**Non-overlapping set from the record alone: YES** — {the single 31-patient efficacy-evaluable set} (sum 31, vs registered 34).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 31 | 0 | PRIMARY | Nab-Sirolimus | Objective Overall Response Rate (ORR) | through study completion (up to 72 months) | False |
| 31 | 5 | POST_HOC | Experimental: Nab-Sirolimus | Disease Control Rate | through study completion (up to 72 months) | False |

### NCT02500121

- Mechanism: **`M5`** — DOCUMENTED_REALLOCATION - the record states participants were re-randomised or crossed over and analysed under more than one group
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 108) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 3 selected cohorts, denominators sum 112, registered enrollment 108, excess **4**.
- Payload(s): `ctg_placebo_onc_2014_2017`

**What drives the excess.** om3 'Control Arm A' 42 and 'Experimental Arm B' 43; om4 'Crossover' 27, whose group description reads 'Arm A subjects that experienced progressive disease per RECIST 1.1 and opted to participate in the crossover portion of the trial'.

**Note.** The 27 crossover patients are a subset of the 42 Arm A patients, counted a second time. 85 <= 108 registered; om3 popDesc explains the shortfall (only measurable-disease subjects assessable).

**Non-overlapping set from the record alone: YES** — {'Control Arm A' 42, 'Experimental Arm B' 43} = 85 (sum 85, vs registered 108).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 43 | 3 | SECONDARY | Experimental Arm B | Objective Response Rate (ORR) Assessment of Subjects on Maintenance Pembrolizumab vs Placebo | Response assessed every 12 weeks from the date of randomization to the… | False |
| 42 | 3 | SECONDARY | Control Arm A | Objective Response Rate (ORR) Assessment of Subjects on Maintenance Pembrolizumab vs Placebo | Response assessed every 12 weeks from the date of randomization to the… | False |
| 27 | 4 | SECONDARY | Crossover | ORR Assessment of Subjects Receiving Pembrolizumab After Progressing on Placebo | Every 12 weeks from the first treatment on the crossover to the date o… | False |

### NCT02513472

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 258) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 3 selected cohorts, denominators sum 334, registered enrollment 258, excess **76**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om0: 'Overall: Eribulin Mesylate + Pembrolizumab' 167 (pooled_label=True) = 'Stratum 1' 66 + 'Stratum 2' 101.

**Note.** Selected total 167 + 101 + 66 = 334; excess 76 = 334 - 258. The reduced set 167 <= 258 registered.

**Non-overlapping set from the record alone: YES** — {'Overall: Eribulin Mesylate + Pembrolizumab' 167} OR {Stratum 1 66, Stratum 2 101} = 167 (sum 167, vs registered 258).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 167 | 0 | PRIMARY | Overall: Eribulin Mesylate + Pembrolizumab | Objective Response Rate (ORR) | From date of first dose of study drug administration to date of first … | True |
| 101 | 0 | PRIMARY | Stratum 2: Eribulin Mesylate + Pembrolizumab | Objective Response Rate (ORR) | From date of first dose of study drug administration to date of first … | False |
| 66 | 0 | PRIMARY | Stratum 1: Eribulin Mesylate + Pembrolizumab | Objective Response Rate (ORR) | From date of first dose of study drug administration to date of first … | False |

### NCT02527434

- Mechanism: **`M2`** — NESTED_SUBGROUP - subgroup or restricted-analysis-population cohorts selected alongside the parent cohort that contains them
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 64) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 8 selected cohorts, denominators sum 85, registered enrollment 64, excess **21**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om0 (monotherapy-phase FAS, 'all treated patients who received at least 1 dose of tremelimumab') 32 + 20 + 12 = 64. om6 reports the retreatment phase for the MEDI and COMBO analysis sets: UBC-COMBO 7, TNBC-COMBO 5, PDAC-COMBO 4, UBC-MEDI 4, PDAC-MEDI 1 = 21.

**Note.** Every retreatment-phase patient first received tremelimumab monotherapy, so the 21 are re-counted members of the 64. Reduced set equals registered enrollment 64 exactly.

**Non-overlapping set from the record alone: YES** — {'UBC - Tremelimumab Monotherapy' 32, 'PDAC - Tremelimumab Monotherapy' 20, 'TNBC - Tremelimumab Monotherapy' 12} = 64 (sum 64, vs registered 64).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 32 | 0 | PRIMARY | UBC - Tremelimumab Monotherapy | Percentage of Patients With Confirmed Overall Response During Tremelimumab Monotherapy Phase | From baseline to 12 months in the tremelimumab monotherapy phase | False |
| 20 | 0 | PRIMARY | PDAC - Tremelimumab Monotherapy | Percentage of Patients With Confirmed Overall Response During Tremelimumab Monotherapy Phase | From baseline to 12 months in the tremelimumab monotherapy phase | False |
| 12 | 0 | PRIMARY | TNBC - Tremelimumab Monotherapy | Percentage of Patients With Confirmed Overall Response During Tremelimumab Monotherapy Phase | From baseline to 12 months in the tremelimumab monotherapy phase | False |
| 7 | 6 | SECONDARY | UBC - COMBO | Percentage of Patients With Confirmed Overall Response During Retreatment Phase | From baseline to 12 months in retreatment phase | False |
| 5 | 6 | SECONDARY | TNBC - COMBO | Percentage of Patients With Confirmed Overall Response During Retreatment Phase | From baseline to 12 months in retreatment phase | False |
| 4 | 6 | SECONDARY | PDAC - COMBO | Percentage of Patients With Confirmed Overall Response During Retreatment Phase | From baseline to 12 months in retreatment phase | False |
| 4 | 6 | SECONDARY | UBC- MEDI | Percentage of Patients With Confirmed Overall Response During Retreatment Phase | From baseline to 12 months in retreatment phase | False |
| 1 | 6 | SECONDARY | PDAC - MEDI | Percentage of Patients With Confirmed Overall Response During Retreatment Phase | From baseline to 12 months in retreatment phase | False |

### NCT02551991

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 56) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 6 selected cohorts, denominators sum 88, registered enrollment 56, excess **32**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om2: 'Cohort -1: Pooled' 32 = 'Dose Expansion: Cohort -1' 25 + 'Dose Exploration: Cohort -1' 7.

**Note.** Excess 32 is exactly the pooled row; the remaining 5 rows sum to 56 = registered ACTUAL enrollment.

**Non-overlapping set from the record alone: YES** — the 5 non-pooled cohorts = 25+7+10+7+7 = 56 (sum 56, vs registered 56).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 32 | 2 | SECONDARY | Cohort -1: Pooled | Best Overall Response (BOR) | RECIST assessments performed at baseline (within 28 days before start … | False |
| 25 | 2 | SECONDARY | Dose Expansion: Cohort -1 | Best Overall Response (BOR) | RECIST assessments performed at baseline (within 28 days before start … | False |
| 10 | 2 | SECONDARY | Dose Exploration: Cohort -2B | Best Overall Response (BOR) | RECIST assessments performed at baseline (within 28 days before start … | False |
| 7 | 2 | SECONDARY | Dose Exploration: Cohort -1 | Best Overall Response (BOR) | RECIST assessments performed at baseline (within 28 days before start … | False |
| 7 | 2 | SECONDARY | Dose Exploration: Cohort -3 | Best Overall Response (BOR) | RECIST assessments performed at baseline (within 28 days before start … | False |
| 7 | 2 | SECONDARY | Dose Exploration: Cohort 1 | Best Overall Response (BOR) | RECIST assessments performed at baseline (within 28 days before start … | False |

### NCT02564900

- Mechanism: **`M6`** — REGISTRY_INCONSISTENCY - cohorts that are mutually exclusive as recorded whose denominators nonetheless exceed the ACTUAL enrollment field, with no overlap mechanism in the record
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 292) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 15 selected cohorts, denominators sum 304, registered enrollment 292, excess **12**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** All 15 rows come from one outcome measure (om0, ITT analysis set) and their group descriptions are mutually exclusive dose-escalation cohorts (0.8 / 1.6 / 3.2 / 5.4 / 6.4 / 8.0 mg/kg) and disease-plus-dose expansion cohorts; denoms sum to 304 against a registered ACTUAL enrollment of 292.

**Note.** UNRESOLVED. No pooled row, no nested subgroup, no re-treatment or crossover statement anywhere in the cached record; the cache holds only the outcomeMeasuresModule (no participantFlowModule or baselineCharacteristicsModule), so the 12-participant discrepancy between the ITT denominators and the enrollment field cannot be attributed from this record. The 15 cohorts are already non-overlapping as recorded.

**Non-overlapping set from the record alone: `UNRESOLVED`.** See the note above.

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 67 | 0 | PRIMARY | Dose Expansion: HER2-positive Breast Cancer, 6.4 mg/kg | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 51 | 0 | PRIMARY | Dose Expansion: HER2-positive Breast Cancer, 5.4 mg/kg | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 33 | 0 | PRIMARY | Dose Expansion: HER2-low Expressing Breast Cancer, 6.4 mg/kg | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 25 | 0 | PRIMARY | Dose Expansion: HER2-overexpressing Gastric or GEJ, 6.4 mg/kg | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 23 | 0 | PRIMARY | Dose Expansion: HER2-expressing Other Solid Tumors | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 21 | 0 | PRIMARY | Dose Expansion: HER2-low Expressing Breast Cancer, 5.4 mg/kg | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 20 | 0 | PRIMARY | Dose Expansion: HER2-expressing Colorectal Tumors | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 19 | 0 | PRIMARY | Dose Expansion: HER2-overexpressing Gastric or GEJ, 5.4 mg/kg | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 18 | 0 | PRIMARY | Dose Expansion: HER2-expressing NSCLC Tumors | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 6 | 0 | PRIMARY | Dose Escalation: Cohort 4, 5.4 mg/kg | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 6 | 0 | PRIMARY | Dose Escalation: Cohort 5, 6.4 mg/kg | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 6 | 0 | PRIMARY | Dose Escalation: Cohort 6, 8.0 mg/kg | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 3 | 0 | PRIMARY | Dose Escalation: Cohort 1, 0.8 mg/kg | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 3 | 0 | PRIMARY | Dose Escalation: Cohort 2, 1.6 mg/kg | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |
| 3 | 0 | PRIMARY | Dose Escalation: Cohort 3, 3.2 mg/kg | Objective Response Rate (ORR) Following Treatment With DS-8201a in Participants With Advanced Solid Malignant Tumors (Dose Escalation and Dose Expansion Phases) | From 6 months postdose of last participant up to 3 years 5 months | False |

### NCT02570308

- Mechanism: **`M4`** — TITLE_VARIANT_DUPLICATE - one patient set reported under different results-group titles in different outcome measures, so the title key counts it more than once
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 146) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 3 selected cohorts, denominators sum 273, registered enrollment 146, excess **127**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om1 'Objective Response Rate in Phase 2' group 'Phase 2 Dose Expansion: 68 mcg Tebentafusp' 127 and om8 'Minor Response Rate' group 'Phase 2 Dose Expansion' 127 are the same FAS population under two titles; om2 'Phase 1 Dose Escalation' 19.

**Note.** Excess 127 is exactly the duplicated Phase 2 row. Reduced set equals registered enrollment 146 exactly. om1 timeframe 'Up to 38 months' vs om8 'Up to 49 months' for the same 127 patients.

**Non-overlapping set from the record alone: YES** — {'Phase 1 Dose Escalation' 19, 'Phase 2 Dose Expansion' 127} = 146 (sum 146, vs registered 146).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 127 | 1 | PRIMARY | Phase 2 Dose Expansion: 68 mcg Tebentafusp | Objective Response Rate in Phase 2 | Up to 38 months | False |
| 19 | 2 | SECONDARY | Phase 1 Dose Escalation | Objective Response Rate in Phase 1 | Up to 49 months | False |
| 127 | 8 | SECONDARY | Phase 2 Dose Expansion | Minor Response Rate | Up to 49 months | False |

### NCT02592707

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 40) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 5 selected cohorts, denominators sum 80, registered enrollment 40, excess **40**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om19: 'All Participants' 40 (pooled_label=True) = 15 + 6 + 9 + 10.

**Note.** Excess 40 is exactly the pooled row; reduced set equals registered enrollment 40.

**Non-overlapping set from the record alone: YES** — {'All Participants' 40} OR {Part A 15, Part B C1 6, Part B C3 9, Part B C6 10} = 40 (sum 40, vs registered 40).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 40 | 19 | SECONDARY | All Participants | Overall Response Rate (ORR) | From the start of the first study medication (Cycle 1 Day 1) up to 2 y… | True |
| 15 | 19 | SECONDARY | Part A: 177Lu-IPN01072 4.5 GBq | Overall Response Rate (ORR) | From the start of the first study medication (Cycle 1 Day 1) up to 2 y… | False |
| 10 | 19 | SECONDARY | Part B Cohort 6: 177Lu-IPN01072 4.5 GBq | Overall Response Rate (ORR) | From the start of the first study medication (Cycle 1 Day 1) up to 2 y… | False |
| 9 | 19 | SECONDARY | Part B Cohort 3: 177Lu-IPN01072 4.5 GBq | Overall Response Rate (ORR) | From the start of the first study medication (Cycle 1 Day 1) up to 2 y… | False |
| 6 | 19 | SECONDARY | Part B Cohort 1: 177Lu-IPN01072 6 GBq | Overall Response Rate (ORR) | From the start of the first study medication (Cycle 1 Day 1) up to 2 y… | False |

### NCT02599402

- Mechanism: **`M3`** — CROSSCUT_PARTITIONS - two or more complete partitions of one population on different axes, all selected
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 533) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 9 selected cohorts, denominators sum 1640, registered enrollment 533, excess **1107**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om10 carries 'Total' 533 (pooled_label=True) plus two overlapping subgroup axes over the same participants: disease subtype (Cutaneous 365 + Ocular/Uveal 64 + Other 62 + Mucosal 32 + Acral 10 = 533) and ECOG performance status (PS0-1 477 + PS2 55 = 532), plus a cross-cutting 'Brain Metastasis' 42.

**Note.** All nine rows are the same outcome measure and the same intervention text. Excess 1107 = 533 + 532 + 42 - 0. The ECOG axis is one short of 533; the record does not say why.

**Non-overlapping set from the record alone: YES** — {'Total' 533} (om10) (sum 533, vs registered 533).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 533 | 10 | SECONDARY | Total | Objective Response Rate (ORR) | Up to approximately 37 months | True |
| 477 | 10 | SECONDARY | ECOG PS0-1 | Objective Response Rate (ORR) | Up to approximately 37 months | False |
| 365 | 10 | SECONDARY | Cutaneous | Objective Response Rate (ORR) | Up to approximately 37 months | False |
| 64 | 10 | SECONDARY | Ocular/Uveal | Objective Response Rate (ORR) | Up to approximately 37 months | False |
| 62 | 10 | SECONDARY | Other | Objective Response Rate (ORR) | Up to approximately 37 months | False |
| 55 | 10 | SECONDARY | ECOG PS2 | Objective Response Rate (ORR) | Up to approximately 37 months | False |
| 42 | 10 | SECONDARY | Brain Metastasis | Objective Response Rate (ORR) | Up to approximately 37 months | False |
| 32 | 10 | SECONDARY | Mucosal | Objective Response Rate (ORR) | Up to approximately 37 months | False |
| 10 | 10 | SECONDARY | Acral | Objective Response Rate (ORR) | Up to approximately 37 months | False |

### NCT02606461

- Mechanism: **`M5`** — DOCUMENTED_REALLOCATION - the record states participants were re-randomised or crossed over and analysed under more than one group
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 342) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 6 selected cohorts, denominators sum 429, registered enrollment 342, excess **87**.
- Payload(s): `ctg_placebo_onc_2014_2017`

**What drives the excess.** om13 group description: 'Participants in the placebo group who had PD during Phase 3 double-blinded treatment, were entered in open-label and received selinexor' - 'Phase 3 Open Label: Selinexor' 63 is therefore a subset of 'Phase 3 Double-blinded: Placebo' 97. Likewise om15 'Phase 2 Open Label: Selinexor' 24 is a subset of 'Phase 2 Double-blinded: Placebo' 30.

**Note.** Excess 87 = 63 + 24. The four double-blind rows sum to 342 = registered ACTUAL enrollment exactly.

**Non-overlapping set from the record alone: YES** — {Phase 3 DB Selinexor 188, Phase 3 DB Placebo 97, Phase 2 DB Selinexor 27, Phase 2 DB Placebo 30} = 342 (sum 342, vs registered 342).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 188 | 12 | SECONDARY | Phase 3 Double-blinded: Selinexor | Phase 3 Double Blind: Overall Response Rate (ORR) | From date of randomization until the documentation of CR or PR (up to … | False |
| 97 | 12 | SECONDARY | Phase 3 Double-blinded: Placebo | Phase 3 Double Blind: Overall Response Rate (ORR) | From date of randomization until the documentation of CR or PR (up to … | False |
| 63 | 13 | SECONDARY | Phase 3 Open Label: Selinexor | Phase 3 Open Label: Overall Response Rate (ORR) | From date of randomization in the Phase 3 open label period until the … | False |
| 30 | 14 | SECONDARY | Phase 2 Double-blinded: Placebo | Phase 2 Double Blind: Overall Response Rate (ORR) | From date of randomization until the documentation of CR or PR (up to … | False |
| 27 | 14 | SECONDARY | Phase 2 Double-blinded: Selinexor | Phase 2 Double Blind: Overall Response Rate (ORR) | From date of randomization until the documentation of CR or PR (up to … | False |
| 24 | 15 | SECONDARY | Phase 2 Open Label: Selinexor | Phase 2 Open Label: Overall Response Rate (ORR) | From date of randomization in the Phase 2 open-label period until the … | False |

### NCT02616393

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 36) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 4 selected cohorts, denominators sum 52, registered enrollment 36, excess **16**.
- Payload(s): `ctg_accrual_completed_onc_phase2|ctg_results_bor_2014_2017`

**What drives the excess.** om0: 'Overall BM' 16 (pooled_label=True) = 'Cohort A (BM)' 13 + 'Cohort C (BM-IP)' 3; om0 popDesc 'Subjects with BM only (Cohorts A and C). Subjects with LM (Cohort B) were excluded'. om1 'Cohort B (LM)' 20 is disjoint from these.

**Note.** Excess 16 is exactly the pooled row. Reduced set equals registered enrollment 36 exactly.

**Non-overlapping set from the record alone: YES** — {'Overall BM' 16, 'Cohort B (LM)' 20} = 36 (sum 36, vs registered 36).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 16 | 0 | PRIMARY | Overall BM | Best Overall Response Rate (ORR) of Subjects With BM | Until disease progression, unacceptable toxicity, or up to 2 years, wh… | True |
| 13 | 0 | PRIMARY | Cohort A (BM) | Best Overall Response Rate (ORR) of Subjects With BM | Until disease progression, unacceptable toxicity, or up to 2 years, wh… | False |
| 3 | 0 | PRIMARY | Cohort C (BM-IP) | Best Overall Response Rate (ORR) of Subjects With BM | Until disease progression, unacceptable toxicity, or up to 2 years, wh… | False |
| 20 | 1 | PRIMARY | Cohort B (LM) | Best ORR of Subjects With LM | Until disease progression, unacceptable toxicity, or up to 2 years, wh… | False |

### NCT02625623

- Mechanism: **`M4`** — TITLE_VARIANT_DUPLICATE - one patient set reported under different results-group titles in different outcome measures, so the title key counts it more than once
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 371) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 3 selected cohorts, denominators sum 556, registered enrollment 371, excess **185**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om2 'Best Overall Response (BOR)' group 'Avelumab + BSC' 185 and om3 'Objective Response Rate (ORR)' group 'Avelumab + SC' 185 are the same randomised arm written two ways (BSC vs SC).

**Note.** Excess 185 is exactly the duplicated avelumab arm. Reduced set equals registered enrollment 371 exactly.

**Non-overlapping set from the record alone: YES** — {Avelumab arm 185, 'Physician Choice Chemotherapy + Best Supportive Care (BSC)' 186} = 371 (sum 371, vs registered 371).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 185 | 2 | SECONDARY | Avelumab + BSC | Best Overall Response (BOR) | From randomization up to 627 days | False |
| 186 | 3 | SECONDARY | Physician Choice Chemotherapy + Best Supportive Care (BSC) | Objective Response Rate (ORR) | From randomization up to 627 days | False |
| 185 | 3 | SECONDARY | Avelumab + SC | Objective Response Rate (ORR) | From randomization up to 627 days | False |

### NCT02674568

- Mechanism: **`M2`** — NESTED_SUBGROUP - subgroup or restricted-analysis-population cohorts selected alongside the parent cohort that contains them
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 342) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 2 selected cohorts, denominators sum 525, registered enrollment 342, excess **183**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om0 group descriptions: DLL3 High = 'tumors with >=75% of cells expressing DLL3' 238; DLL3 Positive = 'tumors with >=25% of cells expressing DLL3' 287. The >=75% set is contained in the >=25% set.

**Note.** Two nested biomarker thresholds on one single-arm mITT population, both reported as results groups in the same outcome measure. 287 <= 342 registered.

**Non-overlapping set from the record alone: YES** — {'Rovalpituzumab Tesirine: DLL3 Positive' 287} (sum 287, vs registered 342).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 287 | 0 | PRIMARY | Rovalpituzumab Tesirine: DLL3 Positive | Objective Response Rate | up to 122.4 weeks; mean (SD) duration of follow-up was 29.0 (23.77) we… | False |
| 238 | 0 | PRIMARY | Rovalpituzumab Tesirine: DLL3 High | Objective Response Rate | up to 122.4 weeks; mean (SD) duration of follow-up was 29.0 (23.77) we… | False |

### NCT02708680

- Mechanism: **`M4`** — TITLE_VARIANT_DUPLICATE - one patient set reported under different results-group titles in different outcome measures, so the title key counts it more than once
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 89) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 4 selected cohorts, denominators sum 162, registered enrollment 89, excess **73**.
- Payload(s): `ctg_placebo_onc_2014_2017|ctg_results_bor_2014_2017`

**What drives the excess.** om4 (ORR) groups 'Phase 2 Expansion: Placebo Plus Atezolizumab' 41 / 'Phase 2 Expansion: Entinostat Plus Atezolizumab' 40; om5 (CBR) groups 'Placebo Plus Atezolizumab' 41 / 'Phase 2 Entinostat Plus Atezolizumab' 40. Same FAS, same denominators, title prefix dropped.

**Note.** Selected total 2 x 81 = 162; excess 73 = 162 - 89. 81 <= 89 registered; the 8-patient gap is not explained in the cached record.

**Non-overlapping set from the record alone: YES** — {Entinostat + Atezolizumab 40, Placebo + Atezolizumab 41} = 81 (sum 81, vs registered 89).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 41 | 4 | SECONDARY | Phase 2 Expansion: Placebo Plus Atezolizumab | Phase 2 Expansion: Overall Response Rate (ORR) Using RECIST 1.1 and irRECIST | Up to 1 year | False |
| 40 | 4 | SECONDARY | Phase 2 Expansion: Entinostat Plus Atezolizumab | Phase 2 Expansion: Overall Response Rate (ORR) Using RECIST 1.1 and irRECIST | Up to 1 year | False |
| 41 | 5 | SECONDARY | Placebo Plus Atezolizumab | Phase 2 Expansion: Clinical Benefit Rate (CBR) Using RECIST 1.1 and irRECIST | Up to 1 year | False |
| 40 | 5 | SECONDARY | Phase 2 Entinostat Plus Atezolizumab | Phase 2 Expansion: Clinical Benefit Rate (CBR) Using RECIST 1.1 and irRECIST | Up to 1 year | False |

### NCT02711956

- Mechanism: **`M4`** — TITLE_VARIANT_DUPLICATE - one patient set reported under different results-group titles in different outcome measures, so the title key counts it more than once
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 75) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 4 selected cohorts, denominators sum 140, registered enrollment 75, excess **65**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om2 (PSA response) 'DE/DC-A ZEN003694 + Enzalutamide' 45 and 'DE/DC-B ZEN003694 + Enzalutamide' 30; om3 (radiographic response) 'DE/DC A ZEN003694 + Enzalutamide' 39 and 'DE/DC B ZEN003694 + Enzalutamide' 26. Hyphen is the only title difference.

**Note.** Same two protocol cohorts measured twice with measure-specific denominators (45 vs 39, 30 vs 26): the radiographic denominators are smaller because fewer patients had measurable disease. Taking the larger denominators gives 75 = registered ACTUAL enrollment exactly.

**Non-overlapping set from the record alone: YES** — {Cohort A 45, Cohort B 30} = 75 (sum 75, vs registered 75).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 45 | 2 | SECONDARY | DE/DC-A ZEN003694 + Enzalutamide | Evaluate Prostate-specific Antigen (PSA) Response Rate by PCWG2 Criteria | Screening up to 35 months | False |
| 30 | 2 | SECONDARY | DE/DC-B ZEN003694 + Enzalutamide | Evaluate Prostate-specific Antigen (PSA) Response Rate by PCWG2 Criteria | Screening up to 35 months | False |
| 39 | 3 | SECONDARY | DE/DC A ZEN003694 + Enzalutamide | Evaluate Radiographic Response Rate (Overall Response Rate) by PCWG2 Criteria | Screening up to 35 months | False |
| 26 | 3 | SECONDARY | DE/DC B ZEN003694 + Enzalutamide | Evaluate Radiographic Response Rate (Overall Response Rate) by PCWG2 Criteria | Screening up to 35 months | False |

### NCT02735980

- Mechanism: **`M4`** — TITLE_VARIANT_DUPLICATE - one patient set reported under different results-group titles in different outcome measures, so the title key counts it more than once
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 133) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 6 selected cohorts, denominators sum 266, registered enrollment 133, excess **133**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om0 (ORR) groups 'Prexasertib (Platinum Resistant Disease)' 60, 'Prexasertib (Platinum Sensitive Disease)' 58, 'Prexasertib Exploratory Addendum (Platinum Sensitive Disease)' 15; om4 (DCR) groups 'Cohort 2 Prexasertib (Platinum Resistant Disease)' 60, 'Cohort 1 Prexasertib (Platinum Sensitive Disease)' 58, 'Cohort 3 Prexasertib Exploratory(Platinum Sensitive Disease)' 15.

**Note.** The three cohorts are counted twice under 'Cohort n' and un-prefixed titles. Excess 133 is exactly one full copy; reduced set equals registered enrollment 133.

**Non-overlapping set from the record alone: YES** — {Platinum Sensitive 58, Platinum Resistant 60, Exploratory 15} = 133 (sum 133, vs registered 133).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 60 | 0 | PRIMARY | Prexasertib (Platinum Resistant Disease) | Percentage of Participants With Complete Response (CR) or Partial Response (PR) (Objective Response Rate [ORR]) | Baseline to 10 months | False |
| 58 | 0 | PRIMARY | Prexasertib (Platinum Sensitive Disease) | Percentage of Participants With Complete Response (CR) or Partial Response (PR) (Objective Response Rate [ORR]) | Baseline to 10 months | False |
| 15 | 0 | PRIMARY | Prexasertib Exploratory Addendum (Platinum Sensitive Disease) | Percentage of Participants With Complete Response (CR) or Partial Response (PR) (Objective Response Rate [ORR]) | Baseline to 10 months | False |
| 60 | 4 | SECONDARY | Cohort 2 Prexasertib (Platinum Resistant Disease) | Disease Control Rate: Percentage of Participants With a Best Overall Response of CR, PR, or Stable Disease (SD) | Baseline through Disease Progression or Death from Any Cause to 28 mon… | False |
| 58 | 4 | SECONDARY | Cohort 1 Prexasertib (Platinum Sensitive Disease) | Disease Control Rate: Percentage of Participants With a Best Overall Response of CR, PR, or Stable Disease (SD) | Baseline through Disease Progression or Death from Any Cause to 28 mon… | False |
| 15 | 4 | SECONDARY | Cohort 3 Prexasertib Exploratory(Platinum Sensitive Disease) | Disease Control Rate: Percentage of Participants With a Best Overall Response of CR, PR, or Stable Disease (SD) | Baseline through Disease Progression or Death from Any Cause to 28 mon… | False |

### NCT02748564

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 10) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 4 selected cohorts, denominators sum 20, registered enrollment 10, excess **10**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om1 (Complete Response Rate) group 'Treatment (Pembrolizumab, Aldesleukin)' 10 is the whole study; om0 partitions the same 10 into dose levels 1 (3), 2 (3) and 3 (4).

**Note.** Excess 10 is exactly the pooled row. Reduced set equals registered enrollment 10. The pooled row's title carries no 'total' vocabulary, so pooled_label=False.

**Non-overlapping set from the record alone: YES** — {'Treatment (Pembrolizumab, Aldesleukin)' 10} OR {Level 1 3, Level 2 3, Level 3 4} = 10 (sum 10, vs registered 10).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 4 | 0 | PRIMARY | Level 3 Treatment Pembrolizumab 200mg IV Q3 wk IL-2 600,000 | Best Overall Response Rate as Assessed by Response (BORR) Evaluation Criteria in Solid Tumors Version 1.1, With the Modification That Progressive Disease Must be Confirmed on a Subsequent Scan | Four to six weeks later up to one year | False |
| 3 | 0 | PRIMARY | Level 1 Treatment Pembrolizumab 200mg IV Q3 wk IL-2 6,000 Aldesleukin) | Best Overall Response Rate as Assessed by Response (BORR) Evaluation Criteria in Solid Tumors Version 1.1, With the Modification That Progressive Disease Must be Confirmed on a Subsequent Scan | Four to six weeks later up to one year | False |
| 3 | 0 | PRIMARY | Level 2 Treatment Pembrolizumab 200mg IV Q3 wk IL-2 60,000 | Best Overall Response Rate as Assessed by Response (BORR) Evaluation Criteria in Solid Tumors Version 1.1, With the Modification That Progressive Disease Must be Confirmed on a Subsequent Scan | Four to six weeks later up to one year | False |
| 10 | 1 | SECONDARY | Treatment (Pembrolizumab, Aldesleukin) | Complete Response Rate | Four to six weeks later, up to three years | False |

### NCT02750514

- Mechanism: **`M5`** — DOCUMENTED_REALLOCATION - the record states participants were re-randomised or crossed over and analysed under more than one group
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 295) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 5 selected cohorts, denominators sum 309, registered enrollment 295, excess **14**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om0 popDesc, verbatim: 'All treated participants. 14 participants, after receiving initial treatment, were re-randomized to a second, different treatment. They were analyzed under both groups they received treatment for.' Denominators: Nivolumab 49, Nivolumab + Dasatinib 106, Nivolumab + BMS986016 18, Nivolumab + Ipilimumab 93, Nivolumab + BMS986205 43 = 309.

**Note.** The excess of 14 is exactly the stated number of doubly-analysed participants. UNRESOLVED as a reduction: the record names the count but not which arms the 14 appear in twice, so no non-overlapping subset of the five arm denominators can be formed from the record alone.

**Non-overlapping set from the record alone: `UNRESOLVED`.** See the note above.

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 106 | 0 | PRIMARY | Nivolumab + Dasatinib | Objective Response Rate (ORR) | From first dose to 2 years following last dose (up to 30 months) | False |
| 93 | 0 | PRIMARY | Nivolumab + Ipilimumab | Objective Response Rate (ORR) | From first dose to 2 years following last dose (up to 30 months) | False |
| 49 | 0 | PRIMARY | Nivolumab | Objective Response Rate (ORR) | From first dose to 2 years following last dose (up to 30 months) | False |
| 43 | 0 | PRIMARY | Nivolumab + BMS986205 | Objective Response Rate (ORR) | From first dose to 2 years following last dose (up to 30 months) | False |
| 18 | 0 | PRIMARY | Nivolumab + BMS986016 | Objective Response Rate (ORR) | From first dose to 2 years following last dose (up to 30 months) | False |

### NCT02754141

- Mechanism: **`M5+M6`** — DOCUMENTED_REALLOCATION for part of the excess, REGISTRY_INCONSISTENCY for the remainder
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 235) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 24 selected cohorts, denominators sum 290, registered enrollment 235, excess **55**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** All 24 rows are om1 ('Number of Participants With a Best Overall Response (BOR) at Week 24', popDesc 'All Treated Participants'). One row is an explicit re-count: 'P2 Combo RCC Crossover' 3 (BMS-986179 600mg Q2W + Nivo 480mg Q4W), i.e. participants who crossed over from 'P2 RCC Mono' 19.

**Note.** UNRESOLVED. The named crossover row accounts for at most 3 of the 55-participant excess; the other 52 are not explained by any pooled, nested, crossover or partition statement in the cached record (the dose-level and tumour-type group descriptions are mutually exclusive as written). The cache carries no participantFlowModule for this study.

**Non-overlapping set from the record alone: `UNRESOLVED` (partial).** See the note above.

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 31 | 1 | SECONDARY | P2 Combo Therapy NSCLC | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 19 | 1 | SECONDARY | P2 Combo Pancreatic | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 19 | 1 | SECONDARY | P2 RCC Mono | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 18 | 1 | SECONDARY | P1B BMS986-179 1600mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 18 | 1 | SECONDARY | P2 RCC Combo | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 15 | 1 | SECONDARY | P2 Combo Melanoma | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 15 | 1 | SECONDARY | P2 Combo SCCHN | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 14 | 1 | SECONDARY | P1A 150mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 14 | 1 | SECONDARY | P2 Combo Prostate | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 12 | 1 | SECONDARY | P1A 1600mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 12 | 1 | SECONDARY | P1A 300mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 12 | 1 | SECONDARY | P1A 600mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 12 | 1 | SECONDARY | P1A Combo Therapy 150mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 12 | 1 | SECONDARY | P1A Combo Therapy 600mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 11 | 1 | SECONDARY | P1A Combo Therapy 300mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 10 | 1 | SECONDARY | P1A Combo Therapy 1600mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 9 | 1 | SECONDARY | P1A 1200mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 9 | 1 | SECONDARY | P1B Combo Therapy 150mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 8 | 1 | SECONDARY | P1B Combo Therapy BMS-986179 1200mg + Nivo 360mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 7 | 1 | SECONDARY | P1A Combo Therapy 1200mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 7 | 1 | SECONDARY | P1B Combo Therapy BMS-986179 1200mg + Nivo 480mg | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 3 | 1 | SECONDARY | P2 Combo RCC Crossover | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 2 | 1 | SECONDARY | P2 Combo Unassiged | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |
| 1 | 1 | SECONDARY | P2 Monotherapy Unassigned | Number of Participants With a Best Overall Response (BOR) at Week 24 | from initial treatment to week 24 | False |

### NCT02759835

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 37) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 4 selected cohorts, denominators sum 73, registered enrollment 37, excess **36**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om9: 'All Participants in Cohorts 1, 2, and 3' 36 (pooled_label=True) against om8 cohorts 'Tyrosine Kinase Inhibitor Naive EGFR Mutated NSCLC' 25, 'EGFR Mutated NSCLC Progressed on Prior 1st/2nd Generation EGFR TKI Therapy & Acquired T790M Mutation' 9, 'EGFR Mutated NSCLC Progressed on Osimertinib' 3.

**Note.** Excess 36 is exactly the pooled row. The pooled denominator 36 is one below the component sum 37; om8/om9 popDesc says 'One participant was not evaluable for response in Cohort 1', which is consistent with the pooled row using the evaluable count. The component set 37 equals registered enrollment exactly.

**Non-overlapping set from the record alone: YES** — {Cohort 1 25, Cohort 2 9, Cohort 3 3} = 37 (or the pooled row alone, 36) (sum 37, vs registered 37).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 25 | 8 | SECONDARY | Tyrosine Kinase Inhibitor Naïve Epidermal Growth Factor Receptor *Mutated Non Small Cell Lung Cancer | Best Overall Response (BOR) | end of treatment, up to 693 days | False |
| 9 | 8 | SECONDARY | EGFR Mutated NSCLC Progressed on Prior 1st/2nd Generation EGFR TKI Therapy &Acquired T790M Mutation | Best Overall Response (BOR) | end of treatment, up to 693 days | False |
| 3 | 8 | SECONDARY | Epidermal Growth Factor Receptor Mutated Non Small Cell Lung Cancer Progressed on Osimertinib | Best Overall Response (BOR) | end of treatment, up to 693 days | False |
| 36 | 9 | SECONDARY | All Participants in Cohorts 1, 2, and 3 | Best Overall Response - All Participants | end of treatment, up to 693 days | True |

### NCT02762981

- Mechanism: **`M3`** — CROSSCUT_PARTITIONS - two or more complete partitions of one population on different axes, all selected
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 85) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 4 selected cohorts, denominators sum 105, registered enrollment 85, excess **20**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om2 partitions the treated population by dosing regimen (Segment I 54 + Segment II 19 = 73); om7 partitions a biopsy-assessed subset of the same patients by biomarker ('GR H-score Above the Overall Median' 16 + 'GR H-score Below the Overall Median' 16 = 32), per its popDesc 'all enrolled participants who received at least 1 dose of relacorilant and had tumor biopsy tissue assessed for GR'.

**Note.** Two partitions on different axes; the biomarker axis is a 32-patient subset of the 73. Selected total 73 + 32 = 105; excess 20 = 105 - 85. 73 <= 85 registered.

**Non-overlapping set from the record alone: YES** — {'Segment I: Continuous Dosing Regimens' 54, 'Segment II: Intermittent Dosing Regimens' 19} = 73 (sum 73, vs registered 85).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 54 | 2 | OTHER_PRE_SPECIFIED | Segment I: Continuous Dosing Regimens | Objective Response Rate | Up to 512 days | False |
| 19 | 2 | OTHER_PRE_SPECIFIED | Segment II: Intermittent Dosing Regimens | Objective Response Rate | Up to 512 days | False |
| 16 | 7 | OTHER_PRE_SPECIFIED | GR H-score Above the Overall Median | Best Response Rate in Participants With Tumor Glucocorticoid Receptor (GR) Above or Below the Median Overall Level | Up to 512 days | False |
| 16 | 7 | OTHER_PRE_SPECIFIED | GR H-score Below the Overall Median | Best Response Rate in Participants With Tumor Glucocorticoid Receptor (GR) Above or Below the Median Overall Level | Up to 512 days | False |

### NCT02844439

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 40) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 3 selected cohorts, denominators sum 75, registered enrollment 40, excess **35**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om5: 'Total' 40 (pooled_label=True) against 'Sub-population A' 24 and 'Sub-population B' 11.

**Note.** Selected total 40 + 24 + 11 = 75; excess 35 = 24 + 11. The two sub-populations sum to 35, not 40; the record does not say what the other 5 participants of the Total are. Reduced set {Total 40} equals registered enrollment exactly.

**Non-overlapping set from the record alone: YES** — {'Total' 40} (sum 40, vs registered 40).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 40 | 5 | SECONDARY | Total | Efficacy: Objective Response Rate (ORR) | Until disease progression, unacceptable toxicity, subject or investiga… | True |
| 24 | 5 | SECONDARY | Sub-population A | Efficacy: Objective Response Rate (ORR) | Until disease progression, unacceptable toxicity, subject or investiga… | False |
| 11 | 5 | SECONDARY | Sub-population B | Efficacy: Objective Response Rate (ORR) | Until disease progression, unacceptable toxicity, subject or investiga… | False |

### NCT02848651

- Mechanism: **`M3`** — CROSSCUT_PARTITIONS - two or more complete partitions of one population on different axes, all selected
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 153) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 7 selected cohorts, denominators sum 509, registered enrollment 153, excess **356**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om9 reports three overlapping dichotomies of the same biomarker-evaluable population: bTMB <10 70 / >=10 49; bTMB <16 91 / >=16 28; bTMF <20 100 / >=20 19. Each pair sums to 119. om0 'Atezolizumab' 152 is the whole treated population.

**Note.** The six bTMB rows sum to 357 = 3 x 119, i.e. the same 119 biomarker-evaluable patients counted three times; with the 152 treated-population row the selected total is 509 and the excess is 509 - 153 = 356. The three cut-points are nested thresholds on one variable, not three populations. Reduced set 152 <= 153 registered.

**Non-overlapping set from the record alone: YES** — {'Atezolizumab' 152} (om0) (sum 152, vs registered 153).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 152 | 0 | PRIMARY | Atezolizumab | Percentage of Participants With Objective Response Per Response Evaluation Criteria in Solid Tumors Version 1.1 (RECIST v1.1) as Determined by Investigator | Baseline up to 32 months | False |
| 100 | 9 | SECONDARY | bTMF <20 | Percentage of Participants With Objective Response (Per RECIST v1.1) by Various bTMB Quantiles | Baseline up to 32 months | False |
| 91 | 9 | SECONDARY | bTMB <16 | Percentage of Participants With Objective Response (Per RECIST v1.1) by Various bTMB Quantiles | Baseline up to 32 months | False |
| 70 | 9 | SECONDARY | bTMB <10 | Percentage of Participants With Objective Response (Per RECIST v1.1) by Various bTMB Quantiles | Baseline up to 32 months | False |
| 49 | 9 | SECONDARY | bTMB >=10 | Percentage of Participants With Objective Response (Per RECIST v1.1) by Various bTMB Quantiles | Baseline up to 32 months | False |
| 28 | 9 | SECONDARY | bTMB >=16 | Percentage of Participants With Objective Response (Per RECIST v1.1) by Various bTMB Quantiles | Baseline up to 32 months | False |
| 19 | 9 | SECONDARY | bTMF >=20 | Percentage of Participants With Objective Response (Per RECIST v1.1) by Various bTMB Quantiles | Baseline up to 32 months | False |

### NCT02872116

- Mechanism: **`M2`** — NESTED_SUBGROUP - subgroup or restricted-analysis-population cohorts selected alongside the parent cohort that contains them
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 2031) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 4 selected cohorts, denominators sum 2394, registered enrollment 2031, excess **363**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om4 groups 'Arm 1: Nivolumab + Chemotherapy (XELOX or FOLFOX)' 789 and 'Arm 2a: Chemotherapy (XELOX or FOLFOX)' 792; om8 groups 'Arm 2b: Chemotherapy (XELOX or FOLFOX)' 404 and 'Arm 3: Nivolumab + Ipilimumab' 409. The Arm 2a and Arm 2b group descriptions are the identical chemotherapy regimen text.

**Note.** UNRESOLVED as a reduction. Arm 2a and Arm 2b are two comparison-specific, overlapping slices of one chemotherapy control arm (each the concurrently randomised control for its own experimental arm). The cached record gives 792 and 404 but never their union, so the non-overlapping set {Arm 1 789, Arm 3 409, chemotherapy control = ?} cannot be completed from the record. Excess 363 = (792 + 404) - 833, where 833 would be the control-arm size implied by 2031 - 789 - 409; that subtraction is an inference, not a recorded value.

**Non-overlapping set from the record alone: `UNRESOLVED`.** See the note above.

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 792 | 4 | SECONDARY | Arm 2a: Chemotherapy (XELOX or FOLFOX) | Objective Response Rate in Participants Treated With Nivolumab Plus Chemotherapy vs Chemotherapy | From randomization to the date of objectively documented progression o… | False |
| 789 | 4 | SECONDARY | Arm 1: Nivolumab + Chemotherapy (XELOX or FOLFOX) | Objective Response Rate in Participants Treated With Nivolumab Plus Chemotherapy vs Chemotherapy | From randomization to the date of objectively documented progression o… | False |
| 409 | 8 | SECONDARY | Arm 3: Nivolumab + Ipilimumab | Objective Response Rate in Participants Treated With Nivolumab Plus Ipilimumab vs Chemotherapy | From randomization to the date of objectively documented progression o… | False |
| 404 | 8 | SECONDARY | Arm 2b: Chemotherapy (XELOX or FOLFOX) | Objective Response Rate in Participants Treated With Nivolumab Plus Ipilimumab vs Chemotherapy | From randomization to the date of objectively documented progression o… | False |

### NCT02872714

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 263) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 8 selected cohorts, denominators sum 700, registered enrollment 263, excess **437**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om3 reports three overlapping combined cohorts: 'Cohort A-ID + Cohort B-ID + Cohort A-CD' 248, 'Cohort A-ID + Cohort A-CD' 204, 'Cohort A-ID + Cohort B-ID' 147; om0 reports 'Cohort A-CD: FGFR3 Mutations or Fusions' 101 and four groups with a Participants denominator of 0 ('Cohort A-ID', 'Cohort B-ID', 'Other-CD', 'Other-ID').

**Note.** 248 + 204 + 147 + 101 + 0 + 0 + 0 + 0 = 700; excess 437 = 700 - 263. The widest combined row 248 contains all three component cohorts, so it is itself a non-overlapping selection. Solving a+b+c=248, a+c=204, a+b=147 gives A-ID 103, B-ID 44, A-CD 101, and the 101 matches the reported Cohort A-CD row - but 103 and 44 are derived, not reported. 248 <= 263 registered.

**Non-overlapping set from the record alone: YES** — {'Cohort A-ID + Cohort B-ID + Cohort A-CD' 248} plus the four zero-denominator rows (sum 248, vs registered 263).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 101 | 0 | PRIMARY | Cohort A-CD: FGFR3 Mutations or Fusions | Objective Response Rate (ORR) in Participants With FGFR3 Mutations or Fusions on a CD Regimen | up to 1138 days | False |
| 0 | 0 | PRIMARY | Cohort A-ID: FGFR3 Mutations or Fusions | Objective Response Rate (ORR) in Participants With FGFR3 Mutations or Fusions on a CD Regimen | up to 1138 days | False |
| 0 | 0 | PRIMARY | Cohort B-ID: All Other FGF/FGFR Alterations | Objective Response Rate (ORR) in Participants With FGFR3 Mutations or Fusions on a CD Regimen | up to 1138 days | False |
| 0 | 0 | PRIMARY | Other-CD | Objective Response Rate (ORR) in Participants With FGFR3 Mutations or Fusions on a CD Regimen | up to 1138 days | False |
| 0 | 0 | PRIMARY | Other-ID | Objective Response Rate (ORR) in Participants With FGFR3 Mutations or Fusions on a CD Regimen | up to 1138 days | False |
| 248 | 3 | SECONDARY | Cohort A-ID + Cohort B-ID + Cohort A-CD | ORR in All Participants on an ID or CD Regimen in Combined Cohorts | up to 1198 days | False |
| 204 | 3 | SECONDARY | Cohort A-ID + Cohort A-CD | ORR in All Participants on an ID or CD Regimen in Combined Cohorts | up to 1198 days | False |
| 147 | 3 | SECONDARY | Cohort A-ID + Cohort B-ID | ORR in All Participants on an ID or CD Regimen in Combined Cohorts | up to 1198 days | False |

### NCT02895360

- Mechanism: **`M2`** — NESTED_SUBGROUP - subgroup or restricted-analysis-population cohorts selected alongside the parent cohort that contains them
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 43) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 5 selected cohorts, denominators sum 59, registered enrollment 43, excess **16**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om6 reports each phase-2a disease cohort twice, once in the FAP (full analysis population) and once in the EEP (efficacy-evaluable population): Ovarian FAP 11 vs EEP 8; Glioblastoma FAP 12 vs EEP 8. The EEP rows are subsets of the matching FAP rows.

**Note.** Excess 16 = 8 + 8 exactly. The three FAP rows sum to 43 = registered ACTUAL enrollment exactly.

**Non-overlapping set from the record alone: YES** — {'Phase 1- in the FAP' 20, 'Phase 2a - Ovarian Cancer in the FAP' 11, 'Phase 2a - Recurrent Glioblastoma in the FAP' 12} = 43 (sum 43, vs registered 43).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 20 | 6 | SECONDARY | Phase 1- in the FAP | Anti-tumor Activity of BAL101553 by Best Response Rate Per RECIST / RANO Criteria | 28 day cycles | False |
| 12 | 6 | SECONDARY | Phase 2a - Patients With Recurrent Glioblastoma in the FAP | Anti-tumor Activity of BAL101553 by Best Response Rate Per RECIST / RANO Criteria | 28 day cycles | False |
| 11 | 6 | SECONDARY | Phase 2a - Patients With Ovarian Cancer in the FAP | Anti-tumor Activity of BAL101553 by Best Response Rate Per RECIST / RANO Criteria | 28 day cycles | False |
| 8 | 6 | SECONDARY | Phase 2a - Patients With Ovarian Cancer in the EEP | Anti-tumor Activity of BAL101553 by Best Response Rate Per RECIST / RANO Criteria | 28 day cycles | False |
| 8 | 6 | SECONDARY | Phase 2a - Patients With Recurrent Glioblastoma in the EEP | Anti-tumor Activity of BAL101553 by Best Response Rate Per RECIST / RANO Criteria | 28 day cycles | False |

### NCT02910583

- Mechanism: **`M2`** — NESTED_SUBGROUP - subgroup or restricted-analysis-population cohorts selected alongside the parent cohort that contains them
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 323) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 7 selected cohorts, denominators sum 608, registered enrollment 323, excess **285**.
- Payload(s): `ctg_placebo_onc_2014_2017|ctg_results_bor_2014_2017`

**What drives the excess.** om1: 'FD Cohort, Non-Del 17p Population' 136 is nested in 'Fixed Duration (FD) Cohort: All Treated' 159 (om1 popDesc: 'the primary analysis of the primary endpoint for the FD cohort was based on the FD Cohort, Non-Del 17p Population only'). om3: 'MRD Cohort: All Treated' 164 contains the four randomised MRD sub-rows (Confirmed uMRD ibrutinib 43, Confirmed uMRD placebo 43, uMRD-not-confirmed open-label ibrutinib+venetoclax 32, uMRD-not-confirmed open-label ibrutinib 31 = 149).

**Note.** Excess 285 = 136 + 149. The two 'All Treated' rows sum to 323 = registered ACTUAL enrollment exactly.

**Non-overlapping set from the record alone: YES** — {'Fixed Duration (FD) Cohort: All Treated' 159, 'MRD Cohort: All Treated' 164} = 323 (sum 323, vs registered 323).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 159 | 1 | PRIMARY | Fixed Duration (FD) Cohort: All Treated | FD Cohort: Complete Response Rate (CRR; Complete Response/Complete Response With Incomplete Blood Count Recovery [CR/CRi]) Rate | From the first dose of ibrutinib to the first confirmed PD, for a medi… | False |
| 136 | 1 | PRIMARY | FD Cohort, Non-Del 17p Population | FD Cohort: Complete Response Rate (CRR; Complete Response/Complete Response With Incomplete Blood Count Recovery [CR/CRi]) Rate | From the first dose of ibrutinib to the first confirmed PD, for a medi… | False |
| 164 | 3 | SECONDARY | MRD Cohort: All Treated | MRD Cohort: Overall Response Rate (ORR) | From the first dose of ibrutinib to the first confirmed PD, for an ove… | False |
| 43 | 3 | SECONDARY | MRD Cohort/Confirmed uMRD: Randomized to Ibrutinib (Blinded) | MRD Cohort: Overall Response Rate (ORR) | From the first dose of ibrutinib to the first confirmed PD, for an ove… | False |
| 43 | 3 | SECONDARY | MRD Cohort/Confirmed uMRD: Randomized to Placebo (Blinded) | MRD Cohort: Overall Response Rate (ORR) | From the first dose of ibrutinib to the first confirmed PD, for an ove… | False |
| 32 | 3 | SECONDARY | MRD Cohort/uMRD Not Confirmed: Randomized to Open-Label Ibrutinib + Venetoclax | MRD Cohort: Overall Response Rate (ORR) | From the first dose of ibrutinib to the first confirmed PD, for an ove… | False |
| 31 | 3 | SECONDARY | MRD Cohort/uMRD Not Confirmed: Randomized to Open-Label Ibrutinib | MRD Cohort: Overall Response Rate (ORR) | From the first dose of ibrutinib to the first confirmed PD, for an ove… | False |

### NCT02924376

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 147) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 5 selected cohorts, denominators sum 236, registered enrollment 147, excess **89**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om2 'Cohort A + Cohort B' 128 contains om0 'Cohort A: FGFR2 Rearrangements or Fusions' 108; om0 also contributes 'Cohort B', 'Cohort C' and 'Other' rows with a Participants denominator of 0.

**Note.** Selected total 128 + 108 + 0 + 0 + 0 = 236; excess 89 = 236 - 147. Cohort B = 128 - 108 = 20 is derivable but not reported. 128 <= 147 registered; om2 popDesc notes two participants were excluded from the Efficacy Evaluable Population as 'Other'.

**Non-overlapping set from the record alone: YES** — {'Cohort A + Cohort B' 128} plus the three zero-denominator rows (sum 128, vs registered 147).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 108 | 0 | PRIMARY | Cohort A: FGFR2 Rearrangements or Fusions | Objective Response Rate (ORR) in Participants With FGFR2 Rearrangements or Fusions | up to 1527 days | False |
| 0 | 0 | PRIMARY | Cohort B: FGF/FGFR Alterations Other Than FGFR2 Rearrangements or Fusions | Objective Response Rate (ORR) in Participants With FGFR2 Rearrangements or Fusions | up to 1527 days | False |
| 0 | 0 | PRIMARY | Cohort C: Negative for FGF/FGFR Alterations | Objective Response Rate (ORR) in Participants With FGFR2 Rearrangements or Fusions | up to 1527 days | False |
| 0 | 0 | PRIMARY | Other | Objective Response Rate (ORR) in Participants With FGFR2 Rearrangements or Fusions | up to 1527 days | False |
| 128 | 2 | SECONDARY | Cohort A + Cohort B | ORR in All Participants With FGF/FGFR Alterations | up to 1527 days | False |

### NCT02935634

- Mechanism: **`M6`** — REGISTRY_INCONSISTENCY - cohorts that are mutually exclusive as recorded whose denominators nonetheless exceed the ACTUAL enrollment field, with no overlap mechanism in the record
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 190) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 12 selected cohorts, denominators sum 195, registered enrollment 190, excess **5**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** All 12 rows come from om0 ('Objective Response Rate (ORR) by Investigator', popDesc 'All treated participants') and their group descriptions are mutually exclusive by construction - Track 1 = 'Treatment naive participants', Track 2 = 'Treatment experienced participants', six distinct regimens in each. Denominators sum to 195 against a registered ACTUAL enrollment of 190.

**Note.** UNRESOLVED. Unlike the two sibling records in this group, this record contains no re-randomisation statement, no pooled row and no nested subgroup; the cache holds only the outcomeMeasuresModule, so the 5-participant discrepancy cannot be attributed. The 12 cohorts are already non-overlapping as recorded. The wording found in NCT02750514 and NCT02996110 is not evidence about this trial.

**Non-overlapping set from the record alone: `UNRESOLVED`.** See the note above.

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 38 | 0 | PRIMARY | Track 1: Nivolumab + BMS-986205 | Objective Response Rate (ORR) by Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 36 | 0 | PRIMARY | Track 2: Nivolumab + BMS-986016 | Objective Response Rate (ORR) by Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 23 | 0 | PRIMARY | Track 1: Nivolumab + Ipilimumab | Objective Response Rate (ORR) by Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 23 | 0 | PRIMARY | Track 2: Nivolumab + Ipilimumab | Objective Response Rate (ORR) by Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 22 | 0 | PRIMARY | Track 2: Nivolumab + BMS-986205 | Objective Response Rate (ORR) by Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 20 | 0 | PRIMARY | Track 1: Nivolumab + BMS-986016 | Objective Response Rate (ORR) by Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 8 | 0 | PRIMARY | Track 1: Ipilimumab + Rucaparib | Objective Response Rate (ORR) by Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 7 | 0 | PRIMARY | Track 1: Nivolumab + Rucaparib | Objective Response Rate (ORR) by Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 6 | 0 | PRIMARY | Track 1: Nivolumab + Ipilimumab + Rucaparib | Objective Response Rate (ORR) by Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 6 | 0 | PRIMARY | Track 2: Nivolumab + Rucaparib | Objective Response Rate (ORR) by Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 4 | 0 | PRIMARY | Track 2: Nivolumab + Ipilimumab + Rucaparib | Objective Response Rate (ORR) by Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 2 | 0 | PRIMARY | Track 2: Ipilimumab + Rucaparib | Objective Response Rate (ORR) by Investigator | From first dose of study treatment until progression or subsequent ant… | False |

### NCT02963493

- Mechanism: **`M2`** — NESTED_SUBGROUP - subgroup or restricted-analysis-population cohorts selected alongside the parent cohort that contains them
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 157) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 3 selected cohorts, denominators sum 331, registered enrollment 157, excess **174**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om0 carries the FAS 157 plus two subgroups drawn from it: 'Patients With Triple Class Refractory Disease' 119 ('refractory to or intolerant of at least one immunomodulatory drug, at least one proteasome inhibitor...') and 'Patients With Extramedullary Disease' 55.

**Note.** Excess 174 = 119 + 55. The FAS row alone equals registered ACTUAL enrollment 157 exactly.

**Non-overlapping set from the record alone: YES** — {'Melphalan Flufenamide (Melflufen) + Dexamethasone: Full Analysis Set' 157} (sum 157, vs registered 157).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 157 | 0 | PRIMARY | Melphalan Flufenamide (Melflufen) + Dexamethasone: Full Analysis Set | Overall Response Rate (ORR) | Patients were followed until documented progression, unacceptable toxi… | False |
| 119 | 0 | PRIMARY | Melphalan Flufenamide (Melflufen) + Dexamethasone: Patients With Triple Class Refractory Disease | Overall Response Rate (ORR) | Patients were followed until documented progression, unacceptable toxi… | False |
| 55 | 0 | PRIMARY | Melphalan Flufenamide (Melflufen) + Dexamethasone: Patients With Extramedullary Disease | Overall Response Rate (ORR) | Patients were followed until documented progression, unacceptable toxi… | False |

### NCT02983799

- Mechanism: **`M2`** — NESTED_SUBGROUP - subgroup or restricted-analysis-population cohorts selected alongside the parent cohort that contains them
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 272) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 9 selected cohorts, denominators sum 423, registered enrollment 272, excess **151**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om0 carries the five primary cohorts (75 + 25 + 68 + 89 + 13 = 270). om7 partitions Cohorts 3 and 4 by HRRm status: 'Cohort 3, HRRm Neg' 56 + 'Cohort 3, HRRm Pos' 9 = 65 (of Cohort 3's 68); 'Cohort 4, HRRm Neg' 76 + 'Cohort 4, HRRm Pos' 12 = 88 (of Cohort 4's 89).

**Note.** Selected total 270 + 153 = 423; excess 151 = 423 - 272, of which 153 is the om7 duplication. The om7 rows are also drawn at a different timepoint ('At baseline') from the om0 rows ('From first dose up until progression'). Reduced set 270 <= 272 registered.

**Non-overlapping set from the record alone: YES** — {Cohort 1 75, Cohort 2 25, COHORT 3 68, COHORT 4 89, Unassigned 13} = 270 (sum 270, vs registered 272).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 89 | 0 | PRIMARY | COHORT 4 | Objective Response Rate, Defined as the Percentage of Subjects With a Best Overall Response of Confirmed Complete Response (CR) or Partial Response (PR) | From first dose up until progression, or last evaluable assessment in … | False |
| 75 | 0 | PRIMARY | Cohort 1 | Objective Response Rate, Defined as the Percentage of Subjects With a Best Overall Response of Confirmed Complete Response (CR) or Partial Response (PR) | From first dose up until progression, or last evaluable assessment in … | False |
| 68 | 0 | PRIMARY | COHORT 3 | Objective Response Rate, Defined as the Percentage of Subjects With a Best Overall Response of Confirmed Complete Response (CR) or Partial Response (PR) | From first dose up until progression, or last evaluable assessment in … | False |
| 25 | 0 | PRIMARY | Cohort 2 | Objective Response Rate, Defined as the Percentage of Subjects With a Best Overall Response of Confirmed Complete Response (CR) or Partial Response (PR) | From first dose up until progression, or last evaluable assessment in … | False |
| 13 | 0 | PRIMARY | Unassigned | Objective Response Rate, Defined as the Percentage of Subjects With a Best Overall Response of Confirmed Complete Response (CR) or Partial Response (PR) | From first dose up until progression, or last evaluable assessment in … | False |
| 76 | 7 | SECONDARY | Cohort 4, HRRm Neg | HRD Status as Per HRRm Gene Panel Assessment Will be Correlated With Clinical Outcome (ORR) for Subjects Enrolled in the 2 Cohorts With BRCAwt (Cohorts 3 and 4) | At baseline | False |
| 56 | 7 | SECONDARY | Cohort 3, HRRm Neg | HRD Status as Per HRRm Gene Panel Assessment Will be Correlated With Clinical Outcome (ORR) for Subjects Enrolled in the 2 Cohorts With BRCAwt (Cohorts 3 and 4) | At baseline | False |
| 12 | 7 | SECONDARY | Cohort 4, HRRm Pos | HRD Status as Per HRRm Gene Panel Assessment Will be Correlated With Clinical Outcome (ORR) for Subjects Enrolled in the 2 Cohorts With BRCAwt (Cohorts 3 and 4) | At baseline | False |
| 9 | 7 | SECONDARY | Cohort 3, HRRm Pos | HRD Status as Per HRRm Gene Panel Assessment Will be Correlated With Clinical Outcome (ORR) for Subjects Enrolled in the 2 Cohorts With BRCAwt (Cohorts 3 and 4) | At baseline | False |

### NCT02984995

- Mechanism: **`M1`** — POOLED_WITH_COMPONENTS - an explicitly pooled/total/combined results cohort selected alongside its own component cohorts
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 37) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 3 selected cohorts, denominators sum 54, registered enrollment 37, excess **17**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om2: 'Total' 27 (pooled_label=True) = 'Initial Dose 20 mg/Day Quizartinib' 3 + 'Initial Dose 30 mg/Day Quizartinib' 24.

**Note.** Selected total 27 + 24 + 3 = 54; excess 17 = 54 - 37. Reduced set 27 <= 37 registered.

**Non-overlapping set from the record alone: YES** — {'Total' 27} OR {20 mg/day 3, 30 mg/day 24} = 27 (sum 27, vs registered 37).

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 27 | 2 | SECONDARY | Total | Response Rate After Treatment With Quizartinib in Japanese Participants With FLT3-ITD Positive Relapsed or Refractory AML | Baseline, cycle 2 day 1, cycle 3 day 1, cycle 4 day 1 until the end of… | True |
| 24 | 2 | SECONDARY | Initial Dose 30 mg/Day Quizartinib | Response Rate After Treatment With Quizartinib in Japanese Participants With FLT3-ITD Positive Relapsed or Refractory AML | Baseline, cycle 2 day 1, cycle 3 day 1, cycle 4 day 1 until the end of… | False |
| 3 | 2 | SECONDARY | Initial Dose 20 mg/Day Quizartinib | Response Rate After Treatment With Quizartinib in Japanese Participants With FLT3-ITD Positive Relapsed or Refractory AML | Baseline, cycle 2 day 1, cycle 3 day 1, cycle 4 day 1 until the end of… | False |

### NCT02996110

- Mechanism: **`M5`** — DOCUMENTED_REALLOCATION - the record states participants were re-randomised or crossed over and analysed under more than one group
- `enrollment_type` = **ACTUAL** (`enrollmentInfo`: count 182) — **not ESTIMATED**, so this is an overlap finding, not an estimate artefact.
- Job 2 arithmetic: 5 selected cohorts, denominators sum 212, registered enrollment 182, excess **30**.
- Payload(s): `ctg_results_bor_2014_2017`

**What drives the excess.** om0 popDesc, verbatim: 'All treated participants. Some participants were re-randomized to receive multiple treatment options during the course of the study.' Denominators: Arm 1 Nivo+Ipi 76, Arm 2 Nivo+Relatlimab 62, Arm 3 Nivo+BMS-986205 31, Arm 4 Nivo+BMS-813160 150mg 21, Arm 5 Nivo+BMS-813160 300mg 22 = 212.

**Note.** UNRESOLVED as a reduction. The mechanism is named by the record but not quantified ('some participants'), so the 30-participant excess cannot be assigned to particular arms and no non-overlapping subset of the five arm denominators follows from the record.

**Non-overlapping set from the record alone: `UNRESOLVED`.** See the note above.

| denominator | om | type | results-group title | outcome-measure title | timeframe | pooled_label |
| ---: | ---: | --- | --- | --- | --- | :---: |
| 76 | 0 | PRIMARY | Arm 1: Nivolumab Plus Ipilimumab (BMS-734016) | Objective Response Rate (ORR) Per Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 62 | 0 | PRIMARY | Arm 2: Nivolumab Plus Relatlimab (BMS-986016) | Objective Response Rate (ORR) Per Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 31 | 0 | PRIMARY | Arm 3: Nivolumab Plus BMS-986205 | Objective Response Rate (ORR) Per Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 22 | 0 | PRIMARY | Arm 5: Nivolumab Plus BMS-813160 300mg | Objective Response Rate (ORR) Per Investigator | From first dose of study treatment until progression or subsequent ant… | False |
| 21 | 0 | PRIMARY | Arm 4: Nivolumab Plus BMS-813160 150 mg | Objective Response Rate (ORR) Per Investigator | From first dose of study treatment until progression or subsequent ant… | False |

## Reported vs assigned, and the integrity check

- Trials assigned: **45**. Trials reached in the cache and adjudicated: **45**. Not reached: **0**.
- Cohort detail rows emitted: **272** (one per selected cohort in `SELECTED-cohort-response-measurements.tsv` for these 45 trials).
- `sha256sum -c SHA256-MANIFEST.txt` exit code: **0** (13/13 files `OK`).
- Companion table: `LEAF-QB-group2.tsv` (one `TRIAL` row per trial plus one `COHORT` row per selected cohort).

