# LEAF-QA-group2 — recoverable corrected readings, 23 assigned NCTs

**Leaf:** QUESTION A, group 2. **Date:** 2026-09-08. **Status:** complete for the assigned selection.

Sole input: the immutable delivered cache copy at
`/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5/`
(branch `literature-cache` @ `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`). **No network request of any kind was made.**
Cache integrity: `sha256sum -c SHA256-MANIFEST.txt` -> 13/13 `OK`, **exit code 0**.

The endpoint manuscript is PARKED. Nothing here repairs a paper, recomputes a manuscript quantity, or
makes any claim about efficacy, safety, selectivity or clinical readiness. This is a reading of what
the source records state.

## 1 - Scope reached versus assigned

| quantity | value |
|---|---|
| NCTs assigned (`LEAF-ASSIGNMENTS/QA-group2.txt`) | 23 |
| NCTs with at least one row in the Job 1 shard tables | 23 |
| assigned NCTs with no row in the shard tables | 0 |
| rows in the shard tables for my NCTs (all classifications) | 152 |
| rows in my selection (`unsupported` or `ambiguous` or `overwrite_scope != none`) | 97 |
| rows I actually opened in the source payload and corrected | **97 / 97** |
| source categories enumerated across those rows | 546 |

Rows not in my selection (55 `valid`, `overwrite_scope=none`) were not corrected; they are outside the task.

### Independent replay check (not a restatement of Job 1)

I re-derived, straight from the payloads, the contributing class set, the four stored cells, the
reported participant denominator and the all-category class sum for each of the 97 rows, and compared
them against the corresponding shard-table columns: **0 mismatches on 97 rows**. The corrected readings
below are therefore about the same rows the derived corpus actually used.

## 2 - Structural findings for this group

1. **Every one of the 97 rows carries exactly one class in its outcome measure** (`n_classes_in_om = 1`),
   and exactly one contributing class. **There is no cross-class overwrite anywhere in my group**, and no
   non-contributing class holds content for the group that the producer discarded (checked on all 97).
   Question A item 2 (enumerate every collapsed class) therefore has one source class per row; the
   `CLASS` lines of the TSV carry that line per row, with kept / dropped / overwritten counts.
2. **Every one of the 97 rows has exactly one reported participant denominator** (`denoms[units =
   "Participants"].counts[groupId]`) in the same outcome measure, and **the residual is 0 in all 97**:
   the sum of all integer categories in the contributing class equals the reported denominator exactly.
   The denominator is therefore recoverable, by reading, for every row I hold.
3. **16 / 97 rows carry a within-class collision**: two or more distinct reported category titles match
   the same four-label regex and the last one written wins. In **7** of those the collided values differ,
   so a stored cell is a value the record does not report for that label.

## 3 - Corrected-reading status

| status | rows | meaning |
|---|---|---|
| `RECOVERABLE` | 81 | a single corrected reading exists: reported denominator + full category vector, residual 0 |
| `RECOVERABLE_FULL_VECTOR; FOUR_CELL_LABEL_NOT_IDENTIFYING` | 9 | denominator and full vector recoverable; the stored CR/PR/SD/PD label does not identify which reported category it is (collided values happened to agree) |
| `RECOVERABLE_FULL_VECTOR; FOUR_CELL_COLLAPSE_UNRESOLVED` | 7 | denominator and full vector recoverable; a single four-cell vector is UNRESOLVED - two distinct reported categories map to one label with different values and the record states no selection or pooling basis |

No row in my group is `UNRESOLVED` for its **denominator**. The `FOUR_CELL_COLLAPSE_UNRESOLVED` rows are
unresolved only for the collapse to four cells, and that is stated per row below rather than papered over.

## 3b - What the producer dropped, in my 97 rows

| dropped category title | rows it appears in | participants dropped (sum) |
|---|---|---|
| `Unknown` | 57 | 117 |
| `Non-CR/Non-PD (NCRNPD)` | 26 | 1 |
| `Not Evaluable` | 9 | 18 |
| `Not evaluable` | 7 | 9 |
| `Non CR/Non PD` | 4 | 0 |
| `Non-evaluable` | 3 | 99 |
| `Not evaluable/Not done` | 3 | 32 |
| `Missing` | 3 | 7 |
| `NE` | 3 | 25 |
| `Noncomplete response/non progressive disease` | 2 | 21 |
| `Non evaluable` | 2 | 57 |
| `Non-complete response/ Non-progressive disease` | 2 | 19 |
| `Not specified/ Not evaluable` | 2 | 11 |
| `Missing or not evaluable` | 2 | 5 |
| `Non-CR/Non-PD` | 2 | 6 |
| `Not Evaluable (NE)` | 2 | 82 |
| `UE` | 2 | 17 |
| `Not done` | 2 | 7 |
| `missing RECIST result` | 2 | 1 |
| `no restaging` | 2 | 21 |
| `Unevaluable (iUE)` | 1 | 6 |
| `Not Done` | 1 | 9 |
| `Off treatment before 8-wk scan` | 1 | 3 |
| `IN` | 1 | 8 |
| `Not Assessed` | 1 | 1 |
| **total** | | **582** |

Across my 97 rows the reported participant denominators sum to 4304 and the producer's `evaluable_n`
sums to 3693, a difference of 611 participants: 582 from the dropped categories tabulated above and
29 from values overwritten by a later same-label category (listed per row in section 4). The one
overwritten title in my group is `Progressive Disease (PD) as per tumor assessment` (16 rows, 29 participants).

None of the dropped titles in my group is a response category (no `VGPR`, `sCR`, `CRh` or `CRmrd-`
appears in these 97 rows); every dropped title here is a non-evaluable, unknown, missing or
`Non-CR/Non-PD` category. The overwritten `PD as per tumor assessment` values are, however, reported
progression counts that the stored cell does not carry.

## 4 - Per-row corrected readings

Full category vectors, every category title and count including those the producer dropped, are in
`LEAF-QA-group2.tsv` (`record_type=CATEGORY`, one line per source category, each with payload file, NCT,
outcome index, group id, class index and category title). Below is the per-row summary.

### NCT02608268 (`ctg_results_bor_2014_2017.txt`)

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG000 "Phase I Dose Escalation: MBG453 80mg Q2W ROW" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **14**; producer stored `evaluable_n` = **11** (shortfall 3)  
- stored cells: CR=0 PR=0 SD=4 PD=7  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 4 | Progressive Disease (PD) = 7 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 3  
- sum of all integer categories = **14**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG000]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG002 "Phase I Dose Escalation: MBG453 800mg Q2W ROW" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **16**; producer stored `evaluable_n` = **15** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=7 PD=8  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 7 | Progressive Disease (PD) = 8 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 1  
- sum of all integer categories = **16**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG002]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG008 "Phase I Dose Escalation: MBG453 240mg Q4W ROW" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **8**; producer stored `evaluable_n` = **6** (shortfall 2)  
- stored cells: CR=0 PR=0 SD=3 PD=3  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 3 | Progressive Disease (PD) = 3 | Non-CR/Non-PD (NCRNPD) = 1 | Unknown = 1  
- sum of all integer categories = **8**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG008]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG009 "Phase I Dose Escalation: MBG453 800mg Q4W ROW" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **9**; producer stored `evaluable_n` = **5** (shortfall 4)  
- stored cells: CR=0 PR=0 SD=1 PD=4  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 1 | Progressive Disease (PD) = 4 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 4  
- sum of all integer categories = **9**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG009]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG010 "Phase I Dose Escalation: MBG453 1200mg Q4W ROW" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **6**; producer stored `evaluable_n` = **4** (shortfall 2)  
- stored cells: CR=0 PR=0 SD=0 PD=4  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 0 | Progressive Disease (PD) = 4 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 2  
- sum of all integer categories = **6**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG010]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG013 "Phase Ib Dose Escalation: MBG453 80mg Q2W + PDR001 80mg Q2W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **13**; producer stored `evaluable_n` = **12** (shortfall 1)  
- stored cells: CR=0 PR=1 SD=7 PD=4  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 1 | Stable Disease (SD) = 7 | Progressive Disease (PD) = 4 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 1  
- sum of all integer categories = **13**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG013]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG016 "Phase Ib Dose Escalation: MBG453 800mg Q2W + PDR001 80mg Q2W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **5**; producer stored `evaluable_n` = **4** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=1 PD=3  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 1 | Progressive Disease (PD) = 3 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 1  
- sum of all integer categories = **5**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG016]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG017 "Phase Ib Dose Escalation: MBG453 800mg Q2W + PDR001 240mg Q2W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **6**; producer stored `evaluable_n` = **5** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=1 PD=4  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 1 | Progressive Disease (PD) = 4 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 1  
- sum of all integer categories = **6**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG017]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG019 "Phase Ib Dose Escalation: MBG453 80mg Q4W + PDR001 400mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **3**; producer stored `evaluable_n` = **2** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=1 PD=1  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 1 | Progressive Disease (PD) = 1 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 1  
- sum of all integer categories = **3**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG019]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG022 "Phase Ib Dose Escalation: MBG453 240mg Q4W + PDR001 400mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **7**; producer stored `evaluable_n` = **5** (shortfall 2)  
- stored cells: CR=0 PR=2 SD=2 PD=1  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 2 | Stable Disease (SD) = 2 | Progressive Disease (PD) = 1 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 2  
- sum of all integer categories = **7**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG022]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG024 "Phase Ib Dose Escalation: MBG453 1200mg Q4W + PDR001 400mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **6**; producer stored `evaluable_n` = **4** (shortfall 2)  
- stored cells: CR=0 PR=0 SD=1 PD=3  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 1 | Progressive Disease (PD) = 3 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 2  
- sum of all integer categories = **6**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG024]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG025 "Dose Ranging Part: MBG453 80mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **14**; producer stored `evaluable_n` = **11** (shortfall 3)  
- stored cells: CR=0 PR=0 SD=4 PD=7  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 4 | Progressive Disease (PD) = 7 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 3  
- sum of all integer categories = **14**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG025]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG026 "Dose Ranging Part: MBG453 240mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **17**; producer stored `evaluable_n` = **15** (shortfall 2)  
- stored cells: CR=0 PR=0 SD=2 PD=13  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 2 | Progressive Disease (PD) = 13 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 2  
- sum of all integer categories = **17**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG026]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG027 "Dose Ranging Part: MBG453 1200mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **15**; producer stored `evaluable_n` = **12** (shortfall 3)  
- stored cells: CR=0 PR=0 SD=4 PD=8  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 4 | Progressive Disease (PD) = 8 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 3  
- sum of all integer categories = **15**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG027]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG028 "Phase II: MBG453 + PDR001 NSCLC" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **17**; producer stored `evaluable_n` = **11** (shortfall 6)  
- stored cells: CR=0 PR=0 SD=6 PD=5  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 6 | Progressive Disease (PD) = 5 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 6  
- sum of all integer categories = **17**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG028]`

**OM[7] "Best Overall Response (BOR) Per RECIST v1.1" - group OG029 "Phase II: MBG453 + PDR001 Melanoma" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **16**; producer stored `evaluable_n` = **15** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=3 PD=12  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 3 | Progressive Disease (PD) = 12 | Non-CR/Non-PD (NCRNPD) = 0 | Unknown = 1  
- sum of all integer categories = **16**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD (NCRNPD) | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02608268] :: outcomeMeasures[7] :: groups[OG029]`

### NCT02625610 (`ctg_results_bor_2014_2017.txt`)

**OM[2] "Best Overall Response (BOR) by Investigator Assessment" - group OG000 "Chemotherapy + Best Supportive Care (BSC)" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **250**; producer stored `evaluable_n` = **211** (shortfall 39)  
- stored cells: CR=5 PR=31 SD=117 PD=58  
- FULL category vector (class 0, all 6 categories): Complete response = 5 | Partial response = 31 | Stable disease = 117 | Noncomplete response/non progressive disease = 11 | Progressive disease = 58 | Non evaluable = 28  
- sum of all integer categories = **250**; residual (denominator - sum) = **0**  
- categories the producer dropped: Noncomplete response/non progressive disease | Non evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02625610] :: outcomeMeasures[2] :: groups[OG000]`

**OM[2] "Best Overall Response (BOR) by Investigator Assessment" - group OG001 "Avelumab" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **249**; producer stored `evaluable_n` = **210** (shortfall 39)  
- stored cells: CR=8 PR=25 SD=92 PD=85  
- FULL category vector (class 0, all 6 categories): Complete response = 8 | Partial response = 25 | Stable disease = 92 | Noncomplete response/non progressive disease = 10 | Progressive disease = 85 | Non evaluable = 29  
- sum of all integer categories = **249**; residual (denominator - sum) = **0**  
- categories the producer dropped: Noncomplete response/non progressive disease | Non evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02625610] :: outcomeMeasures[2] :: groups[OG001]`

### NCT02625623 (`ctg_results_bor_2014_2017.txt`)

**OM[2] "Best Overall Response (BOR)" - group OG000 "Physician Choice Chemotherapy + Best Supportive Care (BSC)" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **186**; producer stored `evaluable_n` = **129** (shortfall 57)  
- stored cells: CR=1 PR=7 SD=62 PD=59  
- FULL category vector (class 0, all 6 categories): Complete Response = 1 | Partial response = 7 | Stable disease = 62 | Non-complete response/ Non-progressive disease = 12 | Progressive disease = 59 | Non-evaluable = 45  
- sum of all integer categories = **186**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-complete response/ Non-progressive disease | Non-evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02625623] :: outcomeMeasures[2] :: groups[OG000]`

**OM[2] "Best Overall Response (BOR)" - group OG001 "Avelumab + BSC" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **185**; producer stored `evaluable_n` = **128** (shortfall 57)  
- stored cells: CR=1 PR=3 SD=30 PD=94  
- FULL category vector (class 0, all 6 categories): Complete Response = 1 | Partial response = 3 | Stable disease = 30 | Non-complete response/ Non-progressive disease = 7 | Progressive disease = 94 | Non-evaluable = 50  
- sum of all integer categories = **185**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-complete response/ Non-progressive disease | Non-evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02625623] :: outcomeMeasures[2] :: groups[OG001]`

### NCT02626000 (`ctg_results_bor_2014_2017.txt`)

**OM[3] "Best Overall Confirmed Response" - group OG000 "Talimogene Laherparepvec + Pembrolizumab" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **32**; producer stored `evaluable_n` = **17** (shortfall 15)  
- stored cells: CR=0 PR=3 SD=10 PD=4  
- FULL category vector (class 0, all 6 categories): Complete Response (iCR) = 0 | Partial Response (iPR) = 3 | Stable Disease (iSD) = 10 | Progressive Disease (iPD) = 4 | Unevaluable (iUE) = 6 | Not Done = 9  
- sum of all integer categories = **32**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unevaluable (iUE) | Not Done  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02626000] :: outcomeMeasures[3] :: groups[OG000]`

### NCT02644278 (`ctg_results_bor_2014_2017.txt`)

**OM[11] "Part A: Number of Participants With Best Overall Response Evaluated by Response Criteria Evaluation (RECIST 1.1)" - group OG000 "VX-984 120 mg + PLD 40 mg/m^2" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **3**; producer stored `evaluable_n` = **2** (shortfall 1)  
- stored cells: CR=0 PR=1 SD=1 PD=0  
- FULL category vector (class 0, all 5 categories): Complete Response = 0 | Partial Response = 1 | Stable disease = 1 | Progressive disease = 0 | Not evaluable = 1  
- sum of all integer categories = **3**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02644278] :: outcomeMeasures[11] :: groups[OG000]`

**OM[11] "Part A: Number of Participants With Best Overall Response Evaluated by Response Criteria Evaluation (RECIST 1.1)" - group OG002 "VX-984 480 mg + PLD 40 mg/m^2" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **6**; producer stored `evaluable_n` = **4** (shortfall 2)  
- stored cells: CR=0 PR=0 SD=4 PD=0  
- FULL category vector (class 0, all 5 categories): Complete Response = 0 | Partial Response = 0 | Stable disease = 4 | Progressive disease = 0 | Not evaluable = 2  
- sum of all integer categories = **6**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02644278] :: outcomeMeasures[11] :: groups[OG002]`

**OM[11] "Part A: Number of Participants With Best Overall Response Evaluated by Response Criteria Evaluation (RECIST 1.1)" - group OG003 "VX-984 720 mg + PLD 40 mg/m^2" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **3**; producer stored `evaluable_n` = **2** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=1 PD=1  
- FULL category vector (class 0, all 5 categories): Complete Response = 0 | Partial Response = 0 | Stable disease = 1 | Progressive disease = 1 | Not evaluable = 1  
- sum of all integer categories = **3**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02644278] :: outcomeMeasures[11] :: groups[OG003]`

### NCT02644967 (`ctg_results_bor_2014_2017.txt`)

**OM[0] "Phase 2: Number of Participants With Objective Response Rate (ORR) Using RECIST v1.1" - group OG000 "Phase 2, 8 mg Tilso/Ipi" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **53**; producer stored `evaluable_n` = **49** (shortfall 4)  
- stored cells: CR=2 PR=9 SD=24 PD=14  
- FULL category vector (class 0, all 5 categories): Complete Response = 2 | Partial Response = 9 | Stable Disease = 24 | Progressive Disease = 14 | Non-evaluable = 4  
- sum of all integer categories = **53**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02644967] :: outcomeMeasures[0] :: groups[OG000]`

### NCT02658097 (`ctg_results_bor_2014_2017.txt`)

**OM[0] "Number of Patients With Each Response as Measured by RECIST 1.1" - group OG000 "Single Fraction Radiation Therapy (SFRT) + Pembrolizumab" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **13**; producer stored `evaluable_n` = **11** (shortfall 2)  
- stored cells: CR=0 PR=4 SD=5 PD=2  
- FULL category vector (class 0, all 5 categories): Complete Response = 0 | Partial Response = 4 | Progressive Disease = 2 | Stable Disease = 5 | Not Evaluable = 2  
- sum of all integer categories = **13**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not Evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02658097] :: outcomeMeasures[0] :: groups[OG000]`

### NCT02679170 (`ctg_results_bor_2014_2017.txt`)

**OM[8] "Number of Participants According to Treatment Response: ALK Treatment Sub-Study and ROS1 Treatment Sub-Study" - group OG000 "ALK Treatment Sub-study" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **91**; producer stored `evaluable_n` = **81** (shortfall 10)  
- stored cells: CR=8 PR=40 SD=22 PD=11  
- FULL category vector (class 0, all 6 categories): CR = 8 | PR = 40 | SD = 22 | PD = 11 | Not specified/ Not evaluable = 9 | Unknown = 1  
- sum of all integer categories = **91**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not specified/ Not evaluable | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02679170] :: outcomeMeasures[8] :: groups[OG000]`

**OM[8] "Number of Participants According to Treatment Response: ALK Treatment Sub-Study and ROS1 Treatment Sub-Study" - group OG001 "ROS1 Treatment Sub-study" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **50**; producer stored `evaluable_n` = **45** (shortfall 5)  
- stored cells: CR=2 PR=20 SD=12 PD=11  
- FULL category vector (class 0, all 6 categories): CR = 2 | PR = 20 | SD = 12 | PD = 11 | Not specified/ Not evaluable = 2 | Unknown = 3  
- sum of all integer categories = **50**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not specified/ Not evaluable | Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02679170] :: outcomeMeasures[8] :: groups[OG001]`

### NCT02762513 (`ctg_results_bor_2014_2017.txt`)

**OM[3] "Best Overall Response" - group OG000 "Axitinib" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **28**; producer stored `evaluable_n` = **25** (shortfall 3)  
- stored cells: CR=1 PR=11 SD=3 PD=10  
- FULL category vector (class 0, all 5 categories): Progressive disease = 10 | Stable disease = 3 | Partial response = 11 | Complete response = 1 | Off treatment before 8-wk scan = 3  
- sum of all integer categories = **28**; residual (denominator - sum) = **0**  
- categories the producer dropped: Off treatment before 8-wk scan  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02762513] :: outcomeMeasures[3] :: groups[OG000]`

### NCT02762981 (`ctg_results_bor_2014_2017.txt`)

**OM[7] "Best Response Rate in Participants With Tumor Glucocorticoid Receptor (GR) Above or Below the Median Overall Level" - group OG000 "GR H-score Above the Overall Median" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **16**; producer stored `evaluable_n` = **15** (shortfall 1)  
- stored cells: CR=1 PR=3 SD=7 PD=4  
- FULL category vector (class 0, all 5 categories): Complete response = 1 | Partial response = 3 | Stable disease = 7 | Progressive disease = 4 | Missing or not evaluable = 1  
- sum of all integer categories = **16**; residual (denominator - sum) = **0**  
- categories the producer dropped: Missing or not evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02762981] :: outcomeMeasures[7] :: groups[OG000]`

**OM[7] "Best Response Rate in Participants With Tumor Glucocorticoid Receptor (GR) Above or Below the Median Overall Level" - group OG001 "GR H-score Below the Overall Median" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **16**; producer stored `evaluable_n` = **12** (shortfall 4)  
- stored cells: CR=0 PR=1 SD=7 PD=4  
- FULL category vector (class 0, all 5 categories): Complete response = 0 | Partial response = 1 | Stable disease = 7 | Progressive disease = 4 | Missing or not evaluable = 4  
- sum of all integer categories = **16**; residual (denominator - sum) = **0**  
- categories the producer dropped: Missing or not evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02762981] :: outcomeMeasures[7] :: groups[OG001]`

### NCT02795429 (`ctg_results_bor_2014_2017.txt`)

**OM[6] "Phase Ib and Phase II: Best Overall Response (BOR) Per RECIST v1.1" - group OG001 "Phase Ib: Capmatinib 300 mg BID + Spartalizumab 300 mg Q3W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **10**; producer stored `evaluable_n` = **9** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=7 PD=2  
- FULL category vector (class 0, all 5 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 7 | Progressive Disease (PD) = 2 | Unknown = 1  
- sum of all integer categories = **10**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02795429] :: outcomeMeasures[6] :: groups[OG001]`

**OM[6] "Phase Ib and Phase II: Best Overall Response (BOR) Per RECIST v1.1" - group OG003 "Phase II: Capmatinib 400 mg BID + Spartalizumab 300 mg Q3W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **32**; producer stored `evaluable_n` = **28** (shortfall 4)  
- stored cells: CR=0 PR=3 SD=12 PD=13  
- FULL category vector (class 0, all 5 categories): Complete Response (CR) = 0 | Partial Response (PR) = 3 | Stable Disease (SD) = 12 | Progressive Disease (PD) = 13 | Unknown = 4  
- sum of all integer categories = **32**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02795429] :: outcomeMeasures[6] :: groups[OG003]`

**OM[6] "Phase Ib and Phase II: Best Overall Response (BOR) Per RECIST v1.1" - group OG004 "Phase II: Spartalizumab 300 mg Q3W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **30**; producer stored `evaluable_n` = **27** (shortfall 3)  
- stored cells: CR=0 PR=3 SD=9 PD=15  
- FULL category vector (class 0, all 5 categories): Complete Response (CR) = 0 | Partial Response (PR) = 3 | Stable Disease (SD) = 9 | Progressive Disease (PD) = 15 | Unknown = 3  
- sum of all integer categories = **30**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02795429] :: outcomeMeasures[6] :: groups[OG004]`

### NCT02825420 (`ctg_results_bor_2014_2017.txt`)

**OM[4] "Best Tumor Response" - group OG000 "Full Analysis Set" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **218**; producer stored `evaluable_n` = **202** (shortfall 16)  
- stored cells: CR=24 PR=57 SD=59 PD=62  
- FULL category vector (class 0, all 5 categories): Complete response = 24 | Partial response = 57 | Stable disease = 59 | Progressive disease = 62 | Not evaluable/Not done = 16  
- sum of all integer categories = **218**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not evaluable/Not done  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02825420] :: outcomeMeasures[4] :: groups[OG000]`

**OM[5] "Best Response by Prior Antiangiogenic Treatment" - group OG000 "Prior Use of Antiangiogenics" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **129**; producer stored `evaluable_n` = **116** (shortfall 13)  
- stored cells: CR=11 PR=27 SD=32 PD=46  
- FULL category vector (class 0, all 5 categories): Progressive disease = 46 | Stable disease = 32 | Partial response = 27 | Complete response = 11 | Not evaluable/Not done = 13  
- sum of all integer categories = **129**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not evaluable/Not done  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02825420] :: outcomeMeasures[5] :: groups[OG000]`

**OM[5] "Best Response by Prior Antiangiogenic Treatment" - group OG001 "No Prior Use of Antiangiogenics" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **89**; producer stored `evaluable_n` = **86** (shortfall 3)  
- stored cells: CR=13 PR=30 SD=27 PD=16  
- FULL category vector (class 0, all 5 categories): Progressive disease = 16 | Stable disease = 27 | Partial response = 30 | Complete response = 13 | Not evaluable/Not done = 3  
- sum of all integer categories = **89**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not evaluable/Not done  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02825420] :: outcomeMeasures[5] :: groups[OG001]`

### NCT02829723 (`ctg_results_bor_2014_2017.txt`)

**OM[13] "Phase I: Best Overall Response (BOR) With Confirmation Per RECIST v1.1" - group OG000 "Phase I: BLZ945 150 mg 7d on/7d Off QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **5**; producer stored `evaluable_n` = **4** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=3 PD=1  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 3 | Progressive Disease (PD) = 1 | Unknown = 1 | Non-CR/Non-PD (NCRNPD) = 0  
- sum of all integer categories = **5**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown | Non-CR/Non-PD (NCRNPD)  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[13] :: groups[OG000]`

**OM[13] "Phase I: Best Overall Response (BOR) With Confirmation Per RECIST v1.1" - group OG003 "Phase I: BLZ945 450 mg Q1W QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **6**; producer stored `evaluable_n` = **4** (shortfall 2)  
- stored cells: CR=0 PR=0 SD=4 PD=0  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 4 | Progressive Disease (PD) = 0 | Unknown = 2 | Non-CR/Non-PD (NCRNPD) = 0  
- sum of all integer categories = **6**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown | Non-CR/Non-PD (NCRNPD)  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[13] :: groups[OG003]`

**OM[13] "Phase I: Best Overall Response (BOR) With Confirmation Per RECIST v1.1" - group OG006 "Phase I: BLZ945 1600 mg Q1W QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **5**; producer stored `evaluable_n` = **3** (shortfall 2)  
- stored cells: CR=0 PR=0 SD=0 PD=3  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 0 | Progressive Disease (PD) = 3 | Unknown = 2 | Non-CR/Non-PD (NCRNPD) = 0  
- sum of all integer categories = **5**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown | Non-CR/Non-PD (NCRNPD)  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[13] :: groups[OG006]`

**OM[13] "Phase I: Best Overall Response (BOR) With Confirmation Per RECIST v1.1" - group OG008 "Phase I: BLZ945 600 mg 4d on/10d Off QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **8**; producer stored `evaluable_n` = **7** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=3 PD=4  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 3 | Progressive Disease (PD) = 4 | Unknown = 1 | Non-CR/Non-PD (NCRNPD) = 0  
- sum of all integer categories = **8**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown | Non-CR/Non-PD (NCRNPD)  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[13] :: groups[OG008]`

**OM[13] "Phase I: Best Overall Response (BOR) With Confirmation Per RECIST v1.1" - group OG010 "Phase I: BLZ945 1200 mg 4d on/10d Off QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **7**; producer stored `evaluable_n` = **6** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=2 PD=4  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 2 | Progressive Disease (PD) = 4 | Unknown = 1 | Non-CR/Non-PD (NCRNPD) = 0  
- sum of all integer categories = **7**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown | Non-CR/Non-PD (NCRNPD)  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[13] :: groups[OG010]`

**OM[13] "Phase I: Best Overall Response (BOR) With Confirmation Per RECIST v1.1" - group OG017 "Phase I: BLZ945 1000 mg Q1W QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **5**; producer stored `evaluable_n` = **4** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=1 PD=3  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 1 | Progressive Disease (PD) = 3 | Unknown = 1 | Non-CR/Non-PD (NCRNPD) = 0  
- sum of all integer categories = **5**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown | Non-CR/Non-PD (NCRNPD)  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[13] :: groups[OG017]`

**OM[13] "Phase I: Best Overall Response (BOR) With Confirmation Per RECIST v1.1" - group OG019 "Phase I: BLZ945 300 mg 4d on/10d Off QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **4**; producer stored `evaluable_n` = **3** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=2 PD=1  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 2 | Progressive Disease (PD) = 1 | Unknown = 1 | Non-CR/Non-PD (NCRNPD) = 0  
- sum of all integer categories = **4**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown | Non-CR/Non-PD (NCRNPD)  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[13] :: groups[OG019]`

**OM[13] "Phase I: Best Overall Response (BOR) With Confirmation Per RECIST v1.1" - group OG020 "Phase I: BLZ945 450 mg 4d on/10d Off QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **6**; producer stored `evaluable_n` = **5** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=2 PD=3  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 2 | Progressive Disease (PD) = 3 | Unknown = 1 | Non-CR/Non-PD (NCRNPD) = 0  
- sum of all integer categories = **6**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown | Non-CR/Non-PD (NCRNPD)  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[13] :: groups[OG020]`

**OM[13] "Phase I: Best Overall Response (BOR) With Confirmation Per RECIST v1.1" - group OG022 "Phase I: BLZ945 1200 mg 4d on/10d Off QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **3**; producer stored `evaluable_n` = **2** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=0 PD=2  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 0 | Progressive Disease (PD) = 2 | Unknown = 1 | Non-CR/Non-PD (NCRNPD) = 0  
- sum of all integer categories = **3**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown | Non-CR/Non-PD (NCRNPD)  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[13] :: groups[OG022]`

**OM[13] "Phase I: Best Overall Response (BOR) With Confirmation Per RECIST v1.1" - group OG023 "Phase I: BLZ945 600 mg Q1W BID + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **6**; producer stored `evaluable_n` = **5** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=1 PD=4  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 1 | Progressive Disease (PD) = 4 | Unknown = 1 | Non-CR/Non-PD (NCRNPD) = 0  
- sum of all integer categories = **6**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown | Non-CR/Non-PD (NCRNPD)  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[13] :: groups[OG023]`

**OM[14] "Phase I: Best Overall Response (BOR) With Confirmation Per irRC" - group OG000 "Phase I: BLZ945 150 mg 7d on/7d Off QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **5**; producer stored `evaluable_n` = **4** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=3 PD=1  
- FULL category vector (class 0, all 5 categories): Complete Response (irCR) = 0 | Partial Response (irPR) = 0 | Stable Disease (irSD) = 3 | Progressive Disease (irPD) = 1 | Unknown = 1  
- sum of all integer categories = **5**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[14] :: groups[OG000]`

**OM[14] "Phase I: Best Overall Response (BOR) With Confirmation Per irRC" - group OG003 "Phase I: BLZ945 450 mg Q1W QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **6**; producer stored `evaluable_n` = **4** (shortfall 2)  
- stored cells: CR=0 PR=0 SD=4 PD=0  
- FULL category vector (class 0, all 5 categories): Complete Response (irCR) = 0 | Partial Response (irPR) = 0 | Stable Disease (irSD) = 4 | Progressive Disease (irPD) = 0 | Unknown = 2  
- sum of all integer categories = **6**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[14] :: groups[OG003]`

**OM[14] "Phase I: Best Overall Response (BOR) With Confirmation Per irRC" - group OG006 "Phase I: BLZ945 1600 mg Q1W QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **5**; producer stored `evaluable_n` = **3** (shortfall 2)  
- stored cells: CR=0 PR=0 SD=0 PD=3  
- FULL category vector (class 0, all 5 categories): Complete Response (irCR) = 0 | Partial Response (irPR) = 0 | Stable Disease (irSD) = 0 | Progressive Disease (irPD) = 3 | Unknown = 2  
- sum of all integer categories = **5**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[14] :: groups[OG006]`

**OM[14] "Phase I: Best Overall Response (BOR) With Confirmation Per irRC" - group OG008 "Phase I: BLZ945 600 mg 4d on/10d Off QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **8**; producer stored `evaluable_n` = **7** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=3 PD=4  
- FULL category vector (class 0, all 5 categories): Complete Response (irCR) = 0 | Partial Response (irPR) = 0 | Stable Disease (irSD) = 3 | Progressive Disease (irPD) = 4 | Unknown = 1  
- sum of all integer categories = **8**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[14] :: groups[OG008]`

**OM[14] "Phase I: Best Overall Response (BOR) With Confirmation Per irRC" - group OG010 "Phase I: BLZ945 1200 mg 4d on/10d Off QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **7**; producer stored `evaluable_n` = **6** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=2 PD=4  
- FULL category vector (class 0, all 5 categories): Complete Response (irCR) = 0 | Partial Response (irPR) = 0 | Stable Disease (irSD) = 2 | Progressive Disease (irPD) = 4 | Unknown = 1  
- sum of all integer categories = **7**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[14] :: groups[OG010]`

**OM[14] "Phase I: Best Overall Response (BOR) With Confirmation Per irRC" - group OG017 "Phase I: BLZ945 1000 mg Q1W QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **5**; producer stored `evaluable_n` = **4** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=1 PD=3  
- FULL category vector (class 0, all 5 categories): Complete Response (irCR) = 0 | Partial Response (irPR) = 0 | Stable Disease (irSD) = 1 | Progressive Disease (irPD) = 3 | Unknown = 1  
- sum of all integer categories = **5**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[14] :: groups[OG017]`

**OM[14] "Phase I: Best Overall Response (BOR) With Confirmation Per irRC" - group OG019 "Phase I: BLZ945 300 mg 4d on/10d Off QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **4**; producer stored `evaluable_n` = **3** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=2 PD=1  
- FULL category vector (class 0, all 5 categories): Complete Response (irCR) = 0 | Partial Response (irPR) = 0 | Stable Disease (irSD) = 2 | Progressive Disease (irPD) = 1 | Unknown = 1  
- sum of all integer categories = **4**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[14] :: groups[OG019]`

**OM[14] "Phase I: Best Overall Response (BOR) With Confirmation Per irRC" - group OG020 "Phase I: BLZ945 450 mg 4d on/10d Off QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **6**; producer stored `evaluable_n` = **5** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=2 PD=3  
- FULL category vector (class 0, all 5 categories): Complete Response (irCR) = 0 | Partial Response (irPR) = 0 | Stable Disease (irSD) = 2 | Progressive Disease (irPD) = 3 | Unknown = 1  
- sum of all integer categories = **6**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[14] :: groups[OG020]`

**OM[14] "Phase I: Best Overall Response (BOR) With Confirmation Per irRC" - group OG022 "Phase I: BLZ945 1200 mg 4d on/10d Off QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **3**; producer stored `evaluable_n` = **2** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=0 PD=2  
- FULL category vector (class 0, all 5 categories): Complete Response (irCR) = 0 | Partial Response (irPR) = 0 | Stable Disease (irSD) = 0 | Progressive Disease (irPD) = 2 | Unknown = 1  
- sum of all integer categories = **3**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[14] :: groups[OG022]`

**OM[14] "Phase I: Best Overall Response (BOR) With Confirmation Per irRC" - group OG023 "Phase I: BLZ945 600 mg Q1W BID + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **6**; producer stored `evaluable_n` = **5** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=2 PD=3  
- FULL category vector (class 0, all 5 categories): Complete Response (irCR) = 0 | Partial Response (irPR) = 0 | Stable Disease (irSD) = 2 | Progressive Disease (irPD) = 3 | Unknown = 1  
- sum of all integer categories = **6**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[14] :: groups[OG023]`

**OM[15] "Phase I and II: Best Overall Response (BOR) (Sustained) Per RANO" - group OG008 "Phase I: BLZ945 600 mg 4d on/10d Off QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **1**; producer stored `evaluable_n` = **1** (shortfall 0)  
- stored cells: CR=0 PR=0 SD=0 PD=1  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 0 | Progressive Disease (PD) as per tumor assessment = 0 | Progressive Disease (PD) as per clinical assessment = 1 | Unknown = 0  
- sum of all integer categories = **1**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=0 ; "Progressive Disease (PD) as per clinical assessment"=1 -> stored 1 **values differ - content lost**  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_COLLAPSE_UNRESOLVED** - within-class collision with differing values on label(s) PD; source states the categories separately and no selection or pooling basis is stated  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[15] :: groups[OG008]`

**OM[15] "Phase I and II: Best Overall Response (BOR) (Sustained) Per RANO" - group OG010 "Phase I: BLZ945 1200 mg 4d on/10d Off QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **3**; producer stored `evaluable_n` = **1** (shortfall 2)  
- stored cells: CR=0 PR=1 SD=0 PD=0  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 1 | Stable Disease (SD) = 0 | Progressive Disease (PD) as per tumor assessment = 2 | Progressive Disease (PD) as per clinical assessment = 0 | Unknown = 0  
- sum of all integer categories = **3**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=2 ; "Progressive Disease (PD) as per clinical assessment"=0 -> stored 0 **values differ - content lost**  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_COLLAPSE_UNRESOLVED** - within-class collision with differing values on label(s) PD; source states the categories separately and no selection or pooling basis is stated  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[15] :: groups[OG010]`

**OM[15] "Phase I and II: Best Overall Response (BOR) (Sustained) Per RANO" - group OG012 "Phase I: BLZ945 600 mg Q1W BID" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **4**; producer stored `evaluable_n` = **3** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=2 PD=1  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 2 | Progressive Disease (PD) as per tumor assessment = 0 | Progressive Disease (PD) as per clinical assessment = 1 | Unknown = 1  
- sum of all integer categories = **4**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=0 ; "Progressive Disease (PD) as per clinical assessment"=1 -> stored 1 **values differ - content lost**  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_COLLAPSE_UNRESOLVED** - within-class collision with differing values on label(s) PD; source states the categories separately and no selection or pooling basis is stated  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[15] :: groups[OG012]`

**OM[15] "Phase I and II: Best Overall Response (BOR) (Sustained) Per RANO" - group OG013 "Phase I: BLZ945 600 mg 4d on/10d Off BID" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **3**; producer stored `evaluable_n` = **2** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=1 PD=1  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 1 | Progressive Disease (PD) as per tumor assessment = 1 | Progressive Disease (PD) as per clinical assessment = 1 | Unknown = 0  
- sum of all integer categories = **3**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=1 ; "Progressive Disease (PD) as per clinical assessment"=1 -> stored 1 (values agree)  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_LABEL_NOT_IDENTIFYING** - within-class collision on label(s) PD with equal values; stored label does not identify which reported category it is  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[15] :: groups[OG013]`

**OM[15] "Phase I and II: Best Overall Response (BOR) (Sustained) Per RANO" - group OG019 "Phase I: BLZ945 300 mg 4d on/10d Off QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **1**; producer stored `evaluable_n` = **1** (shortfall 0)  
- stored cells: CR=0 PR=0 SD=1 PD=0  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 1 | Progressive Disease (PD) as per tumor assessment = 0 | Progressive Disease (PD) as per clinical assessment = 0 | Unknown = 0  
- sum of all integer categories = **1**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=0 ; "Progressive Disease (PD) as per clinical assessment"=0 -> stored 0 (values agree)  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_LABEL_NOT_IDENTIFYING** - within-class collision on label(s) PD with equal values; stored label does not identify which reported category it is  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[15] :: groups[OG019]`

**OM[15] "Phase I and II: Best Overall Response (BOR) (Sustained) Per RANO" - group OG020 "Phase I: BLZ945 450 mg 4d on/10d Off QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **5**; producer stored `evaluable_n` = **2** (shortfall 3)  
- stored cells: CR=0 PR=0 SD=2 PD=0  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 2 | Progressive Disease (PD) as per tumor assessment = 3 | Progressive Disease (PD) as per clinical assessment = 0 | Unknown = 0  
- sum of all integer categories = **5**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=3 ; "Progressive Disease (PD) as per clinical assessment"=0 -> stored 0 **values differ - content lost**  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_COLLAPSE_UNRESOLVED** - within-class collision with differing values on label(s) PD; source states the categories separately and no selection or pooling basis is stated  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[15] :: groups[OG020]`

**OM[15] "Phase I and II: Best Overall Response (BOR) (Sustained) Per RANO" - group OG024 "Phase I: BLZ945 800 mg Q1W BID + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **2**; producer stored `evaluable_n` = **1** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=0 PD=1  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 0 | Progressive Disease (PD) as per tumor assessment = 1 | Progressive Disease (PD) as per clinical assessment = 1 | Unknown = 0  
- sum of all integer categories = **2**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=1 ; "Progressive Disease (PD) as per clinical assessment"=1 -> stored 1 (values agree)  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_LABEL_NOT_IDENTIFYING** - within-class collision on label(s) PD with equal values; stored label does not identify which reported category it is  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[15] :: groups[OG024]`

**OM[15] "Phase I and II: Best Overall Response (BOR) (Sustained) Per RANO" - group OG025 "Phase II: BLZ945 1200 mg 4d on/10d Off QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **22**; producer stored `evaluable_n` = **10** (shortfall 12)  
- stored cells: CR=0 PR=3 SD=3 PD=4  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 3 | Stable Disease (SD) = 3 | Progressive Disease (PD) as per tumor assessment = 10 | Progressive Disease (PD) as per clinical assessment = 4 | Unknown = 2  
- sum of all integer categories = **22**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=10 ; "Progressive Disease (PD) as per clinical assessment"=4 -> stored 4 **values differ - content lost**  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_COLLAPSE_UNRESOLVED** - within-class collision with differing values on label(s) PD; source states the categories separately and no selection or pooling basis is stated  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[15] :: groups[OG025]`

**OM[15] "Phase I and II: Best Overall Response (BOR) (Sustained) Per RANO" - group OG026 "Phase II: BLZ945 700 mg 4d on/10d Off QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **21**; producer stored `evaluable_n` = **6** (shortfall 15)  
- stored cells: CR=0 PR=0 SD=5 PD=1  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 5 | Progressive Disease (PD) as per tumor assessment = 11 | Progressive Disease (PD) as per clinical assessment = 1 | Unknown = 4  
- sum of all integer categories = **21**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=11 ; "Progressive Disease (PD) as per clinical assessment"=1 -> stored 1 **values differ - content lost**  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_COLLAPSE_UNRESOLVED** - within-class collision with differing values on label(s) PD; source states the categories separately and no selection or pooling basis is stated  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[15] :: groups[OG026]`

**OM[16] "Phase I and II: Best Overall Response (BOR) (Sustained) Per iRANO" - group OG010 "Phase I: BLZ945 1200 mg 4d on/10d Off QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **3**; producer stored `evaluable_n` = **1** (shortfall 2)  
- stored cells: CR=0 PR=1 SD=0 PD=0  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 1 | Stable Disease (SD) = 0 | Progressive Disease (PD) as per tumor assessment = 0 | Progressive Disease (PD) as per clinical assessment = 0 | Unknown = 2  
- sum of all integer categories = **3**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=0 ; "Progressive Disease (PD) as per clinical assessment"=0 -> stored 0 (values agree)  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_LABEL_NOT_IDENTIFYING** - within-class collision on label(s) PD with equal values; stored label does not identify which reported category it is  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[16] :: groups[OG010]`

**OM[16] "Phase I and II: Best Overall Response (BOR) (Sustained) Per iRANO" - group OG012 "Phase I: BLZ945 600 mg Q1W BID" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **4**; producer stored `evaluable_n` = **2** (shortfall 2)  
- stored cells: CR=0 PR=0 SD=2 PD=0  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 2 | Progressive Disease (PD) as per tumor assessment = 0 | Progressive Disease (PD) as per clinical assessment = 0 | Unknown = 2  
- sum of all integer categories = **4**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=0 ; "Progressive Disease (PD) as per clinical assessment"=0 -> stored 0 (values agree)  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_LABEL_NOT_IDENTIFYING** - within-class collision on label(s) PD with equal values; stored label does not identify which reported category it is  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[16] :: groups[OG012]`

**OM[16] "Phase I and II: Best Overall Response (BOR) (Sustained) Per iRANO" - group OG013 "Phase I: BLZ945 600 mg 4d on/10d Off BID" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **3**; producer stored `evaluable_n` = **1** (shortfall 2)  
- stored cells: CR=0 PR=0 SD=1 PD=0  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 1 | Progressive Disease (PD) as per tumor assessment = 0 | Progressive Disease (PD) as per clinical assessment = 0 | Unknown = 2  
- sum of all integer categories = **3**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=0 ; "Progressive Disease (PD) as per clinical assessment"=0 -> stored 0 (values agree)  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_LABEL_NOT_IDENTIFYING** - within-class collision on label(s) PD with equal values; stored label does not identify which reported category it is  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[16] :: groups[OG013]`

**OM[16] "Phase I and II: Best Overall Response (BOR) (Sustained) Per iRANO" - group OG019 "Phase I: BLZ945 300 mg 4d on/10d Off QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **1**; producer stored `evaluable_n` = **1** (shortfall 0)  
- stored cells: CR=0 PR=1 SD=0 PD=0  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 1 | Stable Disease (SD) = 0 | Progressive Disease (PD) as per tumor assessment = 0 | Progressive Disease (PD) as per clinical assessment = 0 | Unknown = 0  
- sum of all integer categories = **1**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=0 ; "Progressive Disease (PD) as per clinical assessment"=0 -> stored 0 (values agree)  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_LABEL_NOT_IDENTIFYING** - within-class collision on label(s) PD with equal values; stored label does not identify which reported category it is  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[16] :: groups[OG019]`

**OM[16] "Phase I and II: Best Overall Response (BOR) (Sustained) Per iRANO" - group OG020 "Phase I: BLZ945 450 mg 4d on/10d Off QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **5**; producer stored `evaluable_n` = **2** (shortfall 3)  
- stored cells: CR=0 PR=0 SD=2 PD=0  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 2 | Progressive Disease (PD) as per tumor assessment = 0 | Progressive Disease (PD) as per clinical assessment = 0 | Unknown = 3  
- sum of all integer categories = **5**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=0 ; "Progressive Disease (PD) as per clinical assessment"=0 -> stored 0 (values agree)  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_LABEL_NOT_IDENTIFYING** - within-class collision on label(s) PD with equal values; stored label does not identify which reported category it is  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[16] :: groups[OG020]`

**OM[16] "Phase I and II: Best Overall Response (BOR) (Sustained) Per iRANO" - group OG025 "Phase II: BLZ945 1200 mg 4d on/10d Off QD" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **22**; producer stored `evaluable_n` = **6** (shortfall 16)  
- stored cells: CR=0 PR=3 SD=3 PD=0  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 3 | Stable Disease (SD) = 3 | Progressive Disease (PD) as per tumor assessment = 1 | Progressive Disease (PD) as per clinical assessment = 0 | Unknown = 15  
- sum of all integer categories = **22**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=1 ; "Progressive Disease (PD) as per clinical assessment"=0 -> stored 0 **values differ - content lost**  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_COLLAPSE_UNRESOLVED** - within-class collision with differing values on label(s) PD; source states the categories separately and no selection or pooling basis is stated  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[16] :: groups[OG025]`

**OM[16] "Phase I and II: Best Overall Response (BOR) (Sustained) Per iRANO" - group OG026 "Phase II: BLZ945 700 mg 4d on/10d Off QD + PDR001 400 mg Q4W" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **21**; producer stored `evaluable_n` = **5** (shortfall 16)  
- stored cells: CR=0 PR=0 SD=5 PD=0  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 5 | Progressive Disease (PD) as per tumor assessment = 0 | Progressive Disease (PD) as per clinical assessment = 0 | Unknown = 16  
- sum of all integer categories = **21**; residual (denominator - sum) = **0**  
- categories the producer dropped: Unknown  
- collapsed onto stored `PD` (within class 0, last write wins): "Progressive Disease (PD) as per tumor assessment"=0 ; "Progressive Disease (PD) as per clinical assessment"=0 -> stored 0 (values agree)  
- status: **RECOVERABLE_FULL_VECTOR; FOUR_CELL_LABEL_NOT_IDENTIFYING** - within-class collision on label(s) PD with equal values; stored label does not identify which reported category it is  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02829723] :: outcomeMeasures[16] :: groups[OG026]`

### NCT02879162 (`ctg_results_bor_2014_2017.txt`)

**OM[0] "Objective Response Rate Measured by RECIST Version 1.1" - group OG000 "Durvalumab + Tremelimumab" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **136**; producer stored `evaluable_n` = **128** (shortfall 8)  
- stored cells: CR=1 PR=19 SD=32 PD=76  
- FULL category vector (class 0, all 5 categories): CR = 1 | PR = 19 | SD = 32 | PD = 76 | IN = 8  
- sum of all integer categories = **136**; residual (denominator - sum) = **0**  
- categories the producer dropped: IN  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02879162] :: outcomeMeasures[0] :: groups[OG000]`

### NCT02895360 (`ctg_results_bor_2014_2017.txt`)

**OM[6] "Anti-tumor Activity of BAL101553 by Best Response Rate Per RECIST / RANO Criteria" - group OG000 "Phase 1- in the FAP" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **20**; producer stored `evaluable_n` = **19** (shortfall 1)  
- stored cells: CR=1 PR=0 SD=3 PD=15  
- FULL category vector (class 0, all 5 categories): Complete response = 1 | Partial response = 0 | Stable disease = 3 | Progressive disease = 15 | Missing = 1  
- sum of all integer categories = **20**; residual (denominator - sum) = **0**  
- categories the producer dropped: Missing  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02895360] :: outcomeMeasures[6] :: groups[OG000]`

### NCT02994953 (`ctg_results_bor_2014_2017.txt`)

**OM[5] "Part B: Number of Participants With Confirmed Best Overall Response (BOR) Assessed by Investigator Using Response Evaluation Criteria in Solid Tumors (RECIST) Version 1.1" - group OG000 "Part B Cohort 1: UC Cohort Stage 1 Combination Therapy (Experimental)" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **16**; producer stored `evaluable_n` = **15** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=2 PD=13  
- FULL category vector (class 0, all 5 categories): Complete Response = 0 | Partial Response = 0 | Stable Disease = 2 | Progressive Disease = 13 | Not evaluable = 1  
- sum of all integer categories = **16**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02994953] :: outcomeMeasures[5] :: groups[OG000]`

**OM[23] "Part A: Number of Participants With Confirmed Best Overall Response (BOR) According to Response Evaluation Criteria in Solid Tumors Version 1.1" - group OG000 "Part A Cohort 1: M9241 4 mcg/kg + Avelumab 10 mg/kg" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **9**; producer stored `evaluable_n` = **8** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=2 PD=6  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 2 | Progressive Disease (PD) = 6 | Non CR/Non PD = 0 | Not Evaluable = 1  
- sum of all integer categories = **9**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non CR/Non PD | Not Evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02994953] :: outcomeMeasures[23] :: groups[OG000]`

**OM[23] "Part A: Number of Participants With Confirmed Best Overall Response (BOR) According to Response Evaluation Criteria in Solid Tumors Version 1.1" - group OG001 "Part A Cohort 2: M9241 8 mcg/kg + Avelumab 10 mg/kg" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **7**; producer stored `evaluable_n` = **6** (shortfall 1)  
- stored cells: CR=1 PR=0 SD=2 PD=3  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 1 | Partial Response (PR) = 0 | Stable Disease (SD) = 2 | Progressive Disease (PD) = 3 | Non CR/Non PD = 0 | Not Evaluable = 1  
- sum of all integer categories = **7**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non CR/Non PD | Not Evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02994953] :: outcomeMeasures[23] :: groups[OG001]`

**OM[23] "Part A: Number of Participants With Confirmed Best Overall Response (BOR) According to Response Evaluation Criteria in Solid Tumors Version 1.1" - group OG002 "Part A Cohort 3: M9241 12 mcg/kg + Avelumab 10 mg/kg" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **7**; producer stored `evaluable_n` = **6** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=2 PD=4  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 2 | Progressive Disease (PD) = 4 | Non CR/Non PD = 0 | Not Evaluable = 1  
- sum of all integer categories = **7**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non CR/Non PD | Not Evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02994953] :: outcomeMeasures[23] :: groups[OG002]`

**OM[23] "Part A: Number of Participants With Confirmed Best Overall Response (BOR) According to Response Evaluation Criteria in Solid Tumors Version 1.1" - group OG003 "Part A Cohort 4: M9241 16.8 mcg/kg +Avelumab 10 mg/kg" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **6**; producer stored `evaluable_n` = **4** (shortfall 2)  
- stored cells: CR=1 PR=0 SD=1 PD=2  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 1 | Partial Response (PR) = 0 | Stable Disease (SD) = 1 | Progressive Disease (PD) = 2 | Non CR/Non PD = 0 | Not Evaluable = 2  
- sum of all integer categories = **6**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non CR/Non PD | Not Evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02994953] :: outcomeMeasures[23] :: groups[OG003]`

### NCT03088540 (`ctg_results_bor_2014_2017.txt`)

**OM[3] "Best Overall Response (BOR) Per IRC" - group OG000 "Cemiplimab" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **357**; producer stored `evaluable_n` = **317** (shortfall 40)  
- stored cells: CR=30 PR=121 SD=90 PD=76  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 30 | Partial Response (PR) = 121 | Stable Disease (SD) = 90 | Non-CR/Non-PD = 2 | Progressive Disease (PD) = 76 | Not Evaluable (NE) = 38  
- sum of all integer categories = **357**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD | Not Evaluable (NE)  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT03088540] :: outcomeMeasures[3] :: groups[OG000]`

**OM[3] "Best Overall Response (BOR) Per IRC" - group OG001 "Chemotherapy" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **355**; producer stored `evaluable_n` = **307** (shortfall 48)  
- stored cells: CR=4 PR=72 SD=175 PD=56  
- FULL category vector (class 0, all 6 categories): Complete Response (CR) = 4 | Partial Response (PR) = 72 | Stable Disease (SD) = 175 | Non-CR/Non-PD = 4 | Progressive Disease (PD) = 56 | Not Evaluable (NE) = 44  
- sum of all integer categories = **355**; residual (denominator - sum) = **0**  
- categories the producer dropped: Non-CR/Non-PD | Not Evaluable (NE)  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT03088540] :: outcomeMeasures[3] :: groups[OG001]`

### NCT03093155 (`ctg_results_bor_2014_2017.txt`)

**OM[4] "Differences in Response to the Combination of Ixabepilone and Bevacizumab in Relationship to Previous Treatment With Bevacizumab and Taxanes" - group OG000 "Ixabepilone" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **13**; producer stored `evaluable_n` = **12** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=7 PD=5  
- FULL category vector (class 0, all 5 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 7 | Progressive Disease (PD) = 5 | Not Assessed = 1  
- sum of all integer categories = **13**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not Assessed  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT03093155] :: outcomeMeasures[4] :: groups[OG000]`

### NCT03146663 (`ctg_results_bor_2014_2017.txt`)

**OM[0] "Best Overall Response" - group OG000 "Arm A" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **24**; producer stored `evaluable_n` = **22** (shortfall 2)  
- stored cells: CR=0 PR=2 SD=8 PD=12  
- FULL category vector (class 0, all 6 categories): Complete response = 0 | Partial response = 2 | Stable disease = 8 | Progressive disease = 12 | Not evaluable = 1 | Missing = 1  
- sum of all integer categories = **24**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not evaluable | Missing  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT03146663] :: outcomeMeasures[0] :: groups[OG000]`

**OM[0] "Best Overall Response" - group OG001 "Arm B" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **26**; producer stored `evaluable_n` = **19** (shortfall 7)  
- stored cells: CR=1 PR=0 SD=8 PD=10  
- FULL category vector (class 0, all 6 categories): Complete response = 1 | Partial response = 0 | Stable disease = 8 | Progressive disease = 10 | Not evaluable = 2 | Missing = 5  
- sum of all integer categories = **26**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not evaluable | Missing  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT03146663] :: outcomeMeasures[0] :: groups[OG001]`

**OM[1] "Best Overall Response (in Evaluable for Response Set)" - group OG000 "Arm A" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **17**; producer stored `evaluable_n` = **16** (shortfall 1)  
- stored cells: CR=0 PR=2 SD=6 PD=8  
- FULL category vector (class 0, all 5 categories): Complete response = 0 | Partial response = 2 | Stable disease = 6 | Progressive disease = 8 | Not evaluable = 1  
- sum of all integer categories = **17**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT03146663] :: outcomeMeasures[1] :: groups[OG000]`

### NCT03164616 (`ctg_results_bor_2014_2017.txt`)

**OM[5] "Best Objective Response (BoR)" - group OG000 "T + D + SoC" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **335**; producer stored `evaluable_n` = **323** (shortfall 12)  
- stored cells: CR=2 PR=153 SD=120 PD=48  
- FULL category vector (class 0, all 5 categories): CR = 2 | PR = 153 | SD ≥6 weeks = 120 | PD = 48 | NE = 12  
- sum of all integer categories = **335**; residual (denominator - sum) = **0**  
- categories the producer dropped: NE  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT03164616] :: outcomeMeasures[5] :: groups[OG000]`

**OM[5] "Best Objective Response (BoR)" - group OG001 "D + SoC" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **330**; producer stored `evaluable_n` = **327** (shortfall 3)  
- stored cells: CR=3 PR=157 SD=107 PD=60  
- FULL category vector (class 0, all 5 categories): CR = 3 | PR = 157 | SD ≥6 weeks = 107 | PD = 60 | NE = 3  
- sum of all integer categories = **330**; residual (denominator - sum) = **0**  
- categories the producer dropped: NE  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT03164616] :: outcomeMeasures[5] :: groups[OG001]`

**OM[5] "Best Objective Response (BoR)" - group OG002 "SoC Alone" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **332**; producer stored `evaluable_n` = **322** (shortfall 10)  
- stored cells: CR=0 PR=111 SD=150 PD=61  
- FULL category vector (class 0, all 5 categories): CR = 0 | PR = 111 | SD ≥6 weeks = 150 | PD = 61 | NE = 10  
- sum of all integer categories = **332**; residual (denominator - sum) = **0**  
- categories the producer dropped: NE  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT03164616] :: outcomeMeasures[5] :: groups[OG002]`

### NCT03212274 (`ctg_results_bor_2018_2021.txt`)

**OM[0] "Overall Response Rate" - group OG000 "Cohort 1A-Glioma Naïve to IDH I" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **16**; producer stored `evaluable_n` = **15** (shortfall 1)  
- stored cells: CR=0 PR=0 SD=9 PD=6  
- FULL category vector (class 0, all 5 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 9 | Progressive Disease (PD) = 6 | Not Evaluable = 1  
- sum of all integer categories = **16**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not Evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2018_2021.txt :: studies[nct=NCT03212274] :: outcomeMeasures[0] :: groups[OG000]`

**OM[0] "Overall Response Rate" - group OG001 "Cohort 1B- Glioma Pretreated" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **16**; producer stored `evaluable_n` = **13** (shortfall 3)  
- stored cells: CR=0 PR=0 SD=8 PD=5  
- FULL category vector (class 0, all 5 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 8 | Progressive Disease (PD) = 5 | Not Evaluable = 3  
- sum of all integer categories = **16**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not Evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2018_2021.txt :: studies[nct=NCT03212274] :: outcomeMeasures[0] :: groups[OG001]`

**OM[0] "Overall Response Rate" - group OG003 "Cohort 2B-Cholangio- Pretreated" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **16**; producer stored `evaluable_n` = **12** (shortfall 4)  
- stored cells: CR=0 PR=0 SD=8 PD=4  
- FULL category vector (class 0, all 5 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 8 | Progressive Disease (PD) = 4 | Not Evaluable = 4  
- sum of all integer categories = **16**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not Evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2018_2021.txt :: studies[nct=NCT03212274] :: outcomeMeasures[0] :: groups[OG003]`

**OM[0] "Overall Response Rate" - group OG004 "Cohort 3A Other -Naive" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **25**; producer stored `evaluable_n` = **22** (shortfall 3)  
- stored cells: CR=0 PR=0 SD=7 PD=15  
- FULL category vector (class 0, all 5 categories): Complete Response (CR) = 0 | Partial Response (PR) = 0 | Stable Disease (SD) = 7 | Progressive Disease (PD) = 15 | Not Evaluable = 3  
- sum of all integer categories = **25**; residual (denominator - sum) = **0**  
- categories the producer dropped: Not Evaluable  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2018_2021.txt :: studies[nct=NCT03212274] :: outcomeMeasures[0] :: groups[OG004]`

### NCT03256344 (`ctg_results_bor_2018_2021.txt`)

**OM[2] "Best Overall Response (BOR)" - group OG000 "Talimogene Laherparepvec With Atezolizumab: Triple Negative Breast Cancer (TNBC)" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **10**; producer stored `evaluable_n` = **5** (shortfall 5)  
- stored cells: CR=0 PR=1 SD=1 PD=3  
- FULL category vector (class 0, all 6 categories): CR = 0 | PR = 1 | SD = 1 | PD = 3 | UE = 3 | Not done = 2  
- sum of all integer categories = **10**; residual (denominator - sum) = **0**  
- categories the producer dropped: UE | Not done  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2018_2021.txt :: studies[nct=NCT03256344] :: outcomeMeasures[2] :: groups[OG000]`

**OM[2] "Best Overall Response (BOR)" - group OG001 "Talimogene Laherparepvec With Atezolizumab: Colorectal Cancer (CRC)" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **24**; producer stored `evaluable_n` = **5** (shortfall 19)  
- stored cells: CR=0 PR=0 SD=1 PD=4  
- FULL category vector (class 0, all 6 categories): CR = 0 | PR = 0 | SD = 1 | PD = 4 | UE = 14 | Not done = 5  
- sum of all integer categories = **24**; residual (denominator - sum) = **0**  
- categories the producer dropped: UE | Not done  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2018_2021.txt :: studies[nct=NCT03256344] :: outcomeMeasures[2] :: groups[OG001]`

### NCT03386357 (`ctg_results_bor_2018_2021.txt`)

**OM[1] "Response Rate According to RECIST" - group OG000 "A (Pembrolizumab+RT)" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **57**; producer stored `evaluable_n` = **47** (shortfall 10)  
- stored cells: CR=6 PR=13 SD=9 PD=19  
- FULL category vector (class 0, all 6 categories): CR = 6 | PR = 13 | SD = 9 | PD = 19 | missing RECIST result = 0 | no restaging = 10  
- sum of all integer categories = **57**; residual (denominator - sum) = **0**  
- categories the producer dropped: missing RECIST result | no restaging  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2018_2021.txt :: studies[nct=NCT03386357] :: outcomeMeasures[1] :: groups[OG000]`

**OM[1] "Response Rate According to RECIST" - group OG001 "B (Pembrolizumab)" - class 0 "<untitled>"**  
- reported denominator (`denoms`, units Participants): **58**; producer stored `evaluable_n` = **46** (shortfall 12)  
- stored cells: CR=3 PR=11 SD=11 PD=21  
- FULL category vector (class 0, all 6 categories): CR = 3 | PR = 11 | SD = 11 | PD = 21 | missing RECIST result = 1 | no restaging = 11  
- sum of all integer categories = **58**; residual (denominator - sum) = **0**  
- categories the producer dropped: missing RECIST result | no restaging  
- status: **RECOVERABLE** - single class, denominator read from denoms, all integer categories sum exactly to it  
- pointer: `ctg_results_bor_2018_2021.txt :: studies[nct=NCT03386357] :: outcomeMeasures[1] :: groups[OG001]`

## 5 - What I did not reach

- The 55 `valid` / `overwrite_scope=none` rows for my NCTs were not opened; they are outside the selection.
- NCTs outside `QA-group2.txt` are outside my group and were not read.
- Cross-shard duplicate reconciliation is the parent's and was not attempted.
- I ran no producer, no build, no test, no gate; I edited no manuscript, producer or packet.

