# LEAF-QA-group3 — recoverable corrected readings, QA group 3 (23 NCTs)

Leaf worker output. Question A, group 3. Sources are read-only from the pinned cache
`ctg-cache-216bd1b5/` (branch `literature-cache` @ `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`).
No network call, no producer run, no manuscript or tracked-file edit was made.

## Coverage and verification

| item | value |
|---|---|
| NCTs assigned | 23 |
| NCTs with rows in the Job-1 TSVs | 23 |
| stored rows in my group (all classifications) | 101 |
| stored rows in scope (`unsupported`/`ambiguous`, or `overwrite_scope != none`) | 77 |
| in-scope rows reached in the cached source | **77 / 77** |
| in-scope rows not reached | 0 |
| `sha256sum -c SHA256-MANIFEST.txt` exit code | **0** (13/13 files OK) |

All 23 assigned NCTs have rows in the TSVs and all 23 have at least one in-scope row, so all 23
appear in the per-row section below. The 24 remaining group rows are `valid` with
`overwrite_scope=none` and are out of scope for this question.
For each reached row the outcome-measure title in the cached record was asserted equal to the
stored `outcome_measure_title` before any number was read; all 77 assertions passed.

## Method

For each in-scope stored row I opened `resultsSection.outcomeMeasuresModule.outcomeMeasures[<outcome_measure_index>]`
in the named payload, read the reported denominator from that outcome measure's `denoms[].counts[]`
entry for the stored `group_id`, and enumerated **every** category of **every** contributing class
(`classes[<class_index>].categories[<category_index>]`), taking the `measurements[]` value for the
same `group_id`. The corrected reading is that full category vector. The residual is
`reported_denominator - sum(all categories of the contributing classes)`.

## Headline result

- **All 77 in-scope rows have residual exactly 0**: in every case the full category vector of the
  contributing class(es) sums exactly to the `denoms` participant count for that group. So a
  corrected reading is recoverable for all 77; none is `UNRESOLVED` for arithmetic reasons.
- **Every one of the 77 rows has exactly one** `denoms` entry for its group, so there is no
  denominator-selection ambiguity anywhere in my group.
- **469 participants** across the 77 rows sit in categories the producer dropped entirely
  (the `evaluable_n = sum(cells.values())` behaviour). These are real, posted counts, not gaps.
- 76 rows: `RECOVERABLE` (single contributing class).
- 1 row: `RECOVERABLE_PER_CLASS` — NCT04208958 OM 3 OG000, three disease-stratum classes collapsed
  by last-class-wins. Per-class readings are exact; a single collapsed vector is recoverable only
  as the sum over all three classes, which equals the denominator (54).

## Dropped-category inventory (contributing classes, in-scope rows only)

| dropped category title | rows | participants |
|---|---|---|
| `NE` | 24 | 94 |
| `Not Evaluable` | 20 | 188 |
| `Not Evaluable (NE)` | 10 | 53 |
| `CRmrd-` | 8 | 2 |
| `CRh` | 8 | 3 |
| `CRi` | 8 | 5 |
| `MLFS` | 8 | 0 |
| `Not evaluable` | 8 | 8 |
| `Non-CR/Non-PD` | 8 | 14 |
| `Not evaluable, unknown, or missing` | 7 | 21 |
| `Non-CR / Non-PD` | 3 | 4 |
| `UE` | 3 | 1 |
| `Not Done` | 3 | 11 |
| `Non-CR/Non-PR` | 2 | 0 |
| `No BOR Available` | 2 | 24 |
| `Very Good Partial Response (VGPR)` | 2 | 7 |
| `Minimal Response (MR)` | 2 | 8 |
| `Morphologic leukemia-free state (MLFS)` | 2 | 1 |
| `Not applicable (NA)` | 2 | 5 |
| `No Response` | 1 | 1 |
| `Missing` | 1 | 0 |
| `Not asssessable` | 1 | 9 |
| `MR` | 1 | 1 |
| `Non-evaluable` | 1 | 1 |
| `Not Assessed (NA)` | 1 | 2 |
| `Not evaluable (NE)` | 1 | 2 |
| `Unknown` | 1 | 4 |

Total participants in dropped categories: **469**.

## Overwrite rows — every collapsed source class enumerated

### R067 — NCT04208958, outcome measure 3, group OG000 (`cross_class`)

Pointer: `ctg_results_bor_2018_2021.txt :: studies[nct=NCT04208958] :: outcomeMeasures[3] :: groups[OG000]`

- OM title: Best Overall Response
- Group title: VE800 combination treatment with nivolumab
- Reported denominator (`denoms[0]`, units `Participants`): **54**
- Producer stored cells: `CR=0;PR=1;SD=2;PD=16` -> evaluable_n 19; conflicting_overwrite=True
- Producer reason: cross-class overwrite with conflicting values for PD,PR,SD (last class wins) ; cells drawn from 3 different classes (CRC; Melanoma; Gastric)

One line per source class the producer collapsed:

| class_index | class title | full category vector for OG000 | class sum | fate |
|---|---|---|---|---|
| 0 | CRC | [0] CR=0; [1] NE=0; [2] Unknown=1; [3] PR=0; [4] SD=3; [5] PD=10 | 14 | OVERWRITTEN — all content lost |
| 1 | Melanoma | [0] CR=0; [1] Unknown=2; [2] PR=0; [3] NE=0; [4] SD=9; [5] PD=9 | 20 | OVERWRITTEN — all content lost |
| 2 | Gastric | [0] CR=0; [1] NE=0; [2] Unknown=1; [3] SD=2; [4] PD=16; [5] PR=1 | 20 | KEPT (last class wins) |

Corrected reading (all contributing classes, summed by category title): `CR=0; NE=0; Unknown=4; PR=1; SD=14; PD=35` = 54, residual 0.

### R075 — NCT03671564, outcome measure 7, group OG000 (`within_class`)

Pointer: `ctg_results_bor_2018_2021.txt :: studies[nct=NCT03671564] :: outcomeMeasures[7] :: groups[OG000]`

- OM title: Number of Participants With Best Response Following Administration of Milademetan in Participants With Relapsed or Refractory Acute Myeloid Leukemia
- Group title: Milademetan (90 mg/Day)
- Reported denominator (`denoms[0]`, units `Participants`): **4**
- Producer stored cells: `CR=0;PR=0;SD=1;PD=1` -> evaluable_n 2; conflicting_overwrite=False
- Producer reason: repeated cross-class assignment (values agreed) for CR ; sum of cells 2 != reported denominator 4 (difference -2)

One line per source class the producer collapsed:

| class_index | class title | full category vector for OG000 | class sum | fate |
|---|---|---|---|---|
| 0 | &lt;untitled&gt; | [0] Complete remission (CR)=0; [1] CR with partial hematological recovery (CRh)=0; [2] CR with incomplete hematological recovery (CRi)=0; [3] Partial remission (PR)=0; [4] Morphologic leukemia-free state (MLFS)=0; [5] Stable disease (SD)=1; [6] Progressive disease (PD)=1; [7] Not applicable (NA)=2; [8] Not Evaluable (NE)=0 | 4 | kept, but multiple categories collapsed onto one cell |

Corrected reading (all contributing classes, summed by category title): `Complete remission (CR)=0; CR with partial hematological recovery (CRh)=0; CR with incomplete hematological recovery (CRi)=0; Partial remission (PR)=0; Morphologic leukemia-free state (MLFS)=0; Stable disease (SD)=1; Progressive disease (PD)=1; Not applicable (NA)=2; Not Evaluable (NE)=0` = 4, residual 0.

### R076 — NCT03671564, outcome measure 7, group OG001 (`within_class`)

Pointer: `ctg_results_bor_2018_2021.txt :: studies[nct=NCT03671564] :: outcomeMeasures[7] :: groups[OG001]`

- OM title: Number of Participants With Best Response Following Administration of Milademetan in Participants With Relapsed or Refractory Acute Myeloid Leukemia
- Group title: Milademetan (120 mg/Day)
- Reported denominator (`denoms[0]`, units `Participants`): **5**
- Producer stored cells: `CR=0;PR=0;SD=0;PD=1` -> evaluable_n 1; conflicting_overwrite=False
- Producer reason: repeated cross-class assignment (values agreed) for CR ; sum of cells 1 != reported denominator 5 (difference -4)

One line per source class the producer collapsed:

| class_index | class title | full category vector for OG001 | class sum | fate |
|---|---|---|---|---|
| 0 | &lt;untitled&gt; | [0] Complete remission (CR)=0; [1] CR with partial hematological recovery (CRh)=0; [2] CR with incomplete hematological recovery (CRi)=0; [3] Partial remission (PR)=0; [4] Morphologic leukemia-free state (MLFS)=1; [5] Stable disease (SD)=0; [6] Progressive disease (PD)=1; [7] Not applicable (NA)=3; [8] Not Evaluable (NE)=0 | 5 | kept, but multiple categories collapsed onto one cell |

Corrected reading (all contributing classes, summed by category title): `Complete remission (CR)=0; CR with partial hematological recovery (CRh)=0; CR with incomplete hematological recovery (CRi)=0; Partial remission (PR)=0; Morphologic leukemia-free state (MLFS)=1; Stable disease (SD)=0; Progressive disease (PD)=1; Not applicable (NA)=3; Not Evaluable (NE)=0` = 5, residual 0.

## Per-row corrected readings

Full machine-readable form, including one line per source class and one per category, is in
`LEAF-QA-group3.tsv` (record_type `CLASS` / `CATEGORY`).

### NCT03480646 (7 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R001 | ctg_results_bor_2014_2017.txt | 4 | OG001 | 0 | 7 | CR=0; PR=0; SD=3; PD=3; Not evaluable, unknown, or missing=1 | 7 | 0 | CR=0;PR=0;SD=3;PD=3 / 6 | 1 | RECOVERABLE |
| R002 | ctg_results_bor_2014_2017.txt | 4 | OG003 | 0 | 11 | CR=0; PR=0; SD=7; PD=1; Not evaluable, unknown, or missing=3 | 11 | 0 | CR=0;PR=0;SD=7;PD=1 / 8 | 3 | RECOVERABLE |
| R003 | ctg_results_bor_2014_2017.txt | 4 | OG004 | 0 | 25 | CR=0; PR=2; SD=10; PD=10; Not evaluable, unknown, or missing=3 | 25 | 0 | CR=0;PR=2;SD=10;PD=10 / 22 | 3 | RECOVERABLE |
| R004 | ctg_results_bor_2014_2017.txt | 4 | OG005 | 0 | 35 | CR=0; PR=2; SD=23; PD=9; Not evaluable, unknown, or missing=1 | 35 | 0 | CR=0;PR=2;SD=23;PD=9 / 34 | 1 | RECOVERABLE |
| R005 | ctg_results_bor_2014_2017.txt | 4 | OG006 | 0 | 38 | CR=0; PR=3; SD=24; PD=7; Not evaluable, unknown, or missing=4 | 38 | 0 | CR=0;PR=3;SD=24;PD=7 / 34 | 4 | RECOVERABLE |
| R006 | ctg_results_bor_2014_2017.txt | 4 | OG007 | 0 | 12 | CR=0; PR=0; SD=5; PD=0; Not evaluable, unknown, or missing=7 | 12 | 0 | CR=0;PR=0;SD=5;PD=0 / 5 | 7 | RECOVERABLE |
| R007 | ctg_results_bor_2014_2017.txt | 4 | OG008 | 0 | 28 | CR=0; PR=0; SD=21; PD=5; Not evaluable, unknown, or missing=2 | 28 | 0 | CR=0;PR=0;SD=21;PD=5 / 26 | 2 | RECOVERABLE |

OM titles: [4] Efficacy: Best Responses by Treatment Group

Group titles: OG001 = Phase 1b Dose Escalation: CPI-1205 400mg BID +Cobi+Abi/Pred; OG003 = Phase 1b Dose Escalation: CPI-1205 800mg TID +Abi/Pred; OG004 = Phase 1b HPEC [Heavily Pre-treated Expansion Cohort] CPI-1205 800mg TID +Enza; OG005 = Phase 2 Randomized Enza Contro; OG006 = Phase 2 Randomized Combination With Enza; OG007 = Phase 2 Randomized Crossover Period; OG008 = Phase 2 Single Arm CPI-1205 +Abi/Pred

### NCT03679754 (1 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R008 | ctg_results_bor_2018_2021.txt | 10 | OG000 | 0 | 36 | Complete Response=1; Partial Response=1; Stable Disease=27; Progressive Disease=6; Not Evaluable=0; No Response=1; Missing=0 | 36 | 0 | CR=1;PR=1;SD=27;PD=6 / 35 | 1 | RECOVERABLE |

OM titles: [10] Tumor Objective Response Rate (ORR)

Group titles: OG000 = Ad-RTS-hIL-12 + Veledimex

### NCT04099641 (2 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R009 | ctg_results_bor_2018_2021.txt | 2 | OG000 | 0 | 61 | Complete Response=2; Partial Response=6; Stable Disease=16; Progressive Disease=31; Not Evaluable=6 | 61 | 0 | CR=2;PR=6;SD=16;PD=31 / 55 | 6 | RECOVERABLE |
| R010 | ctg_results_bor_2018_2021.txt | 2 | OG001 | 0 | 19 | Complete Response=0; Partial Response=1; Stable Disease=9; Progressive Disease=8; Not Evaluable=1 | 19 | 0 | CR=0;PR=1;SD=9;PD=8 / 18 | 1 | RECOVERABLE |

OM titles: [2] Objective Response Rate (ORR)

Group titles: OG000 = Group 1 (CPI Naïve); OG001 = Group 2 (CPI Relapse)

### NCT04306900 (6 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R011 | ctg_results_bor_2018_2021.txt | 3 | OG000 | 0 | 7 | CR=0; PR=1; Stable Disease=2; PD=3; NE=1 | 7 | 0 | CR=0;PR=1;SD=2;PD=3 / 6 | 1 | RECOVERABLE |
| R012 | ctg_results_bor_2018_2021.txt | 3 | OG001 | 0 | 41 | CR=5; PR=18; Stable Disease=14; PD=2; NE=2 | 41 | 0 | CR=5;PR=18;SD=14;PD=2 / 39 | 2 | RECOVERABLE |
| R013 | ctg_results_bor_2018_2021.txt | 3 | OG005 | 0 | 27 | CR=0; PR=9; Stable Disease=13; PD=3; NE=2 | 27 | 0 | CR=0;PR=9;SD=13;PD=3 / 25 | 2 | RECOVERABLE |
| R014 | ctg_results_bor_2018_2021.txt | 3 | OG007 | 0 | 12 | CR=0; PR=0; Stable Disease=3; PD=8; NE=1 | 12 | 0 | CR=0;PR=0;SD=3;PD=8 / 11 | 1 | RECOVERABLE |
| R015 | ctg_results_bor_2018_2021.txt | 3 | OG008 | 0 | 5 | CR=0; PR=0; Stable Disease=3; PD=1; NE=1 | 5 | 0 | CR=0;PR=0;SD=3;PD=1 / 4 | 1 | RECOVERABLE |
| R016 | ctg_results_bor_2018_2021.txt | 3 | OG009 | 0 | 22 | CR=1; PR=1; Stable Disease=5; PD=11; NE=4 | 22 | 0 | CR=1;PR=1;SD=5;PD=11 / 18 | 4 | RECOVERABLE |

OM titles: [3] Best Response (BOR)

Group titles: OG000 = Cohort 1 - Safety Lead-in (TTX-030 + Budigalimab + mFOLFOX6); OG001 = Cohort 3B - Gastric (TTX-030 + Budigalimab + mFOLFOX6); OG005 = Cohort 9 - Pancreatic (TTX-030 + Budigalimab + Gemcitabine + Nab-Paclitaxel); OG007 = Cohort 4 - CRC (TTX-030 + Budigalimab); OG008 = Cohort 6 - HNSCC (TTX-030 + Budigalimab); OG009 = Cohort 8 - GEC (TTX-030 + Budigalimab)

### NCT04539327 (1 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R017 | ctg_results_bor_2018_2021.txt | 16 | OG000 | 0 | 28 | Progressive Disease=11; Stable Disease=4; Complete Response=4; Partial Response=0; Not asssessable=9 | 28 | 0 | CR=4;PR=0;SD=4;PD=11 / 19 | 9 | RECOVERABLE |

OM titles: [16] Objective Response Rate (ORR)

Group titles: OG000 = Rucaparib - Treatment

### NCT03829501 (15 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R018 | ctg_results_bor_2018_2021.txt | 6 | OG001 | 0 | 5 | CR=0; PR=0; SD=0; PD=3; NE=2 | 5 | 0 | CR=0;PR=0;SD=0;PD=3 / 3 | 2 | RECOVERABLE |
| R019 | ctg_results_bor_2018_2021.txt | 6 | OG003 | 0 | 8 | CR=0; PR=0; SD=2; PD=3; NE=3 | 8 | 0 | CR=0;PR=0;SD=2;PD=3 / 5 | 3 | RECOVERABLE |
| R020 | ctg_results_bor_2018_2021.txt | 6 | OG004 | 0 | 7 | CR=0; PR=0; SD=2; PD=4; NE=1 | 7 | 0 | CR=0;PR=0;SD=2;PD=4 / 6 | 1 | RECOVERABLE |
| R021 | ctg_results_bor_2018_2021.txt | 6 | OG006 | 0 | 5 | CR=0; PR=0; SD=3; PD=1; NE=1 | 5 | 0 | CR=0;PR=0;SD=3;PD=1 / 4 | 1 | RECOVERABLE |
| R022 | ctg_results_bor_2018_2021.txt | 6 | OG007 | 0 | 43 | CR=1; PR=3; SD=12; PD=20; NE=7 | 43 | 0 | CR=1;PR=3;SD=12;PD=20 / 36 | 7 | RECOVERABLE |
| R023 | ctg_results_bor_2018_2021.txt | 6 | OG008 | 0 | 36 | CR=0; PR=2; SD=8; PD=22; NE=4 | 36 | 0 | CR=0;PR=2;SD=8;PD=22 / 32 | 4 | RECOVERABLE |
| R024 | ctg_results_bor_2018_2021.txt | 6 | OG010 | 0 | 9 | CR=0; PR=0; SD=4; PD=2; NE=3 | 9 | 0 | CR=0;PR=0;SD=4;PD=2 / 6 | 3 | RECOVERABLE |
| R025 | ctg_results_bor_2018_2021.txt | 6 | OG012 | 0 | 14 | CR=0; PR=0; SD=0; PD=11; NE=3 | 14 | 0 | CR=0;PR=0;SD=0;PD=11 / 11 | 3 | RECOVERABLE |
| R026 | ctg_results_bor_2018_2021.txt | 6 | OG013 | 0 | 7 | CR=0; PR=0; SD=1; PD=5; NE=1 | 7 | 0 | CR=0;PR=0;SD=1;PD=5 / 6 | 1 | RECOVERABLE |
| R027 | ctg_results_bor_2018_2021.txt | 6 | OG014 | 0 | 14 | CR=0; PR=1; SD=4; PD=8; NE=1 | 14 | 0 | CR=0;PR=1;SD=4;PD=8 / 13 | 1 | RECOVERABLE |
| R028 | ctg_results_bor_2018_2021.txt | 6 | OG015 | 0 | 5 | CR=0; PR=0; SD=2; PD=2; NE=1 | 5 | 0 | CR=0;PR=0;SD=2;PD=2 / 4 | 1 | RECOVERABLE |
| R029 | ctg_results_bor_2018_2021.txt | 6 | OG016 | 0 | 5 | CR=0; PR=0; SD=1; PD=2; NE=2 | 5 | 0 | CR=0;PR=0;SD=1;PD=2 / 3 | 2 | RECOVERABLE |
| R030 | ctg_results_bor_2018_2021.txt | 6 | OG017 | 0 | 2 | CR=0; PR=0; SD=0; PD=1; NE=1 | 2 | 0 | CR=0;PR=0;SD=0;PD=1 / 1 | 1 | RECOVERABLE |
| R031 | ctg_results_bor_2018_2021.txt | 6 | OG020 | 0 | 6 | CR=0; PR=0; SD=2; PD=3; NE=1 | 6 | 0 | CR=0;PR=0;SD=2;PD=3 / 5 | 1 | RECOVERABLE |
| R032 | ctg_results_bor_2018_2021.txt | 6 | OG022 | 0 | 9 | CR=0; PR=0; SD=3; PD=4; NE=2 | 9 | 0 | CR=0;PR=0;SD=3;PD=4 / 7 | 2 | RECOVERABLE |

OM titles: [6] Best Overall Response (BOR) Per RECIST 1.1

Group titles: OG001 = Alomfilimab 2.4 mg; OG003 = Alomfilimab 24 mg; OG004 = Alomfilimab 80 mg; OG006 = Alomfilimab 0.8 mg + Atezolizumab; OG007 = Alomfilimab 2.4 mg + Atezolizumab; OG008 = Alomfilimab 8 mg + Atezolizumab; OG010 = Alomfilimab 80 mg + Atezolizumab; OG012 = Alomfilimab 8 mg + Atezolizumab in Anti-PD-(L)1 Naïve Pancreatic Cancer; OG013 = Alomfilimab 2.4 mg + Atezolizumab in Anti-PD-(L)1 Naïve Triple Negative BC; OG014 = Alomfilimab 8 mg + Atezolizumab in Anti-PD-(L)1 Naïve Triple Negative BC; OG015 = Alomfilimab 8 mg + Atezolizumab in Anti-PD-(L)1 Naïve HNSCC; OG016 = Alomfilimab 24 mg + Atezolizumab in Anti-PD-(L)1 Naïve HNSCC; OG017 = Alomfilimab 2.4 mg + Atezolizumab in Anti-PD-(L)1 Pre-treated Pancreatic Cancer; OG020 = Alomfilimab 8 mg + Atezolizumab in Anti-PD-(L)1 Pre-treated Triple Negative BC; OG022 = Alomfilimab 24 mg + Atezolizumab in Anti-PD-(L)1 Pre-treated HNSCC

### NCT04753658 (1 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R033 | ctg_results_bor_2018_2021.txt | 5 | OG000 | 0 | 15 | CR=5; PR=3; MR=1; SD=3; PD=3 | 15 | 0 | CR=5;PR=3;SD=3;PD=3 / 14 | 1 | RECOVERABLE |

OM titles: [5] Number of Participants With Best Overall Response Based on HCP Reported Objective Response

Group titles: OG000 = Lorlatinib

### NCT03455829 (3 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R034 | ctg_results_bor_2018_2021.txt | 2 | OG000 | 0 | 6 | Complete Response (CR)=0; Partial Response (PR)=2; Stable Disease (SD)=2; Progressive Disease (PD)=1; Not Evaluable (NE)=1 | 6 | 0 | CR=0;PR=2;SD=2;PD=1 / 5 | 1 | RECOVERABLE |
| R035 | ctg_results_bor_2018_2021.txt | 2 | OG003 | 0 | 7 | Complete Response (CR)=0; Partial Response (PR)=1; Stable Disease (SD)=3; Progressive Disease (PD)=2; Not Evaluable (NE)=1 | 7 | 0 | CR=0;PR=1;SD=3;PD=2 / 6 | 1 | RECOVERABLE |
| R036 | ctg_results_bor_2018_2021.txt | 2 | OG004 | 0 | 5 | Complete Response (CR)=0; Partial Response (PR)=3; Stable Disease (SD)=0; Progressive Disease (PD)=1; Not Evaluable (NE)=1 | 5 | 0 | CR=0;PR=3;SD=0;PD=1 / 4 | 1 | RECOVERABLE |

OM titles: [2] Best Overall Tumor Response

Group titles: OG000 = Part 1: Cohort 1 Lerociclib at 200 mg QD; OG003 = Part 1: Cohort 4 Lerociclib at 150 mg BID; OG004 = Part 1: Cohort 5 Lerociclib at 200 mg BID

### NCT04329949 (1 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R037 | ctg_results_bor_2018_2021.txt | 2 | OG000 | 0 | 31 | Complete response=0; Partial response=0; Stable disease=20; Progressive disease=10; Non-evaluable=1 | 31 | 0 | CR=0;PR=0;SD=20;PD=10 / 30 | 1 | RECOVERABLE |

OM titles: [2] Best Overall Response (BOR)

Group titles: OG000 = Relacorilant With Nab-paclitaxel

### NCT03965689 (1 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R038 | ctg_results_bor_2018_2021.txt | 0 | OG000 | 0 | 25 | Complete Response (CR)=0; Partial Response (PR)=4; Stable Disease (SD)=15; Progressive Disease (PD)=4; Not Assessed (NA)=2 | 25 | 0 | CR=0;PR=4;SD=15;PD=4 / 23 | 2 | RECOVERABLE |

OM titles: [0] Number of Participants With an Overall Response

Group titles: OG000 = Treatment (Paclitaxel, Carboplatin, Pevonedistat)

### NCT03451825 (2 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R039 | ctg_results_bor_2018_2021.txt | 2 | OG000 | 0 | 6 | Complete Response (CR)=0; Partial Response (PR)=0; Stable Disease (SD)=0; Non-CR/Non-PR=0; Progressive Disease (PD)=5; Not Evaluable=1 | 6 | 0 | CR=0;PR=0;SD=0;PD=5 / 5 | 1 | RECOVERABLE |
| R040 | ctg_results_bor_2018_2021.txt | 2 | OG001 | 0 | 15 | Complete Response (CR)=0; Partial Response (PR)=0; Stable Disease (SD)=4; Non-CR/Non-PR=0; Progressive Disease (PD)=9; Not Evaluable=2 | 15 | 0 | CR=0;PR=0;SD=4;PD=9 / 13 | 2 | RECOVERABLE |

OM titles: [2] Number of Participants With Confirmed Best Overall Response (BOR) as Per Response Evaluation Criteria in Solid Tumors (RECIST Version 1.1) and as Adjudicated by the Investigator

Group titles: OG000 = Avelumab 10 Miligram Per Kilogram (mg/kg); OG001 = Avelumab 20 mg/kg

### NCT04764474 (8 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R041 | ctg_results_bor_2018_2021.txt | 3 | OG000 | 0 | 3 | CRmrd-=0; CR=0; CRh=0; CRi=0; MLFS=0; PR=0; SD=1; PD=0; Not evaluable=2 | 3 | 0 | CR=0;PR=0;SD=1;PD=0 / 1 | 2 | RECOVERABLE |
| R042 | ctg_results_bor_2018_2021.txt | 3 | OG001 | 0 | 3 | CRmrd-=0; CR=0; CRh=0; CRi=0; MLFS=0; PR=0; SD=0; PD=1; Not evaluable=2 | 3 | 0 | CR=0;PR=0;SD=0;PD=1 / 1 | 2 | RECOVERABLE |
| R043 | ctg_results_bor_2018_2021.txt | 3 | OG002 | 0 | 10 | CRmrd-=0; CR=3; CRh=0; CRi=2; MLFS=0; PR=0; SD=1; PD=3; Not evaluable=1 | 10 | 0 | CR=3;PR=0;SD=1;PD=3 / 7 | 3 | RECOVERABLE |
| R044 | ctg_results_bor_2018_2021.txt | 3 | OG003 | 0 | 5 | CRmrd-=1; CR=0; CRh=1; CRi=0; MLFS=0; PR=0; SD=0; PD=2; Not evaluable=1 | 5 | 0 | CR=0;PR=0;SD=0;PD=2 / 2 | 3 | RECOVERABLE |
| R045 | ctg_results_bor_2018_2021.txt | 3 | OG004 | 0 | 5 | CRmrd-=0; CR=0; CRh=1; CRi=2; MLFS=0; PR=0; SD=0; PD=2; Not evaluable=0 | 5 | 0 | CR=0;PR=0;SD=0;PD=2 / 2 | 3 | RECOVERABLE |
| R046 | ctg_results_bor_2018_2021.txt | 3 | OG005 | 0 | 4 | CRmrd-=0; CR=0; CRh=0; CRi=0; MLFS=0; PR=0; SD=1; PD=2; Not evaluable=1 | 4 | 0 | CR=0;PR=0;SD=1;PD=2 / 3 | 1 | RECOVERABLE |
| R047 | ctg_results_bor_2018_2021.txt | 3 | OG006 | 0 | 3 | CRmrd-=0; CR=1; CRh=1; CRi=0; MLFS=0; PR=0; SD=0; PD=1; Not evaluable=0 | 3 | 0 | CR=1;PR=0;SD=0;PD=1 / 2 | 1 | RECOVERABLE |
| R048 | ctg_results_bor_2018_2021.txt | 3 | OG007 | 0 | 8 | CRmrd-=1; CR=3; CRh=0; CRi=1; MLFS=0; PR=0; SD=0; PD=2; Not evaluable=1 | 8 | 0 | CR=3;PR=0;SD=0;PD=2 / 5 | 3 | RECOVERABLE |

OM titles: [3] Number of Patients With Best Overall Response (BOR)

Group titles: OG000 = Cohort 1: HMPL-306 Dose Level 1; OG001 = Cohort 2: HMPL-306 Dose Level 2; OG002 = Cohort 3: HMPL-306 Dose Level 3; OG003 = Cohort 4: HMPL-306 Dose Level 4; OG004 = Cohort 5: HMPL-306 Dose Level 5; OG005 = Cohort 6: HMPL-306 Dose Level 6; OG006 = Cohort 7: HMPL-306 Dose Level 7; OG007 = Cohort 8: HMPL-306 Dose Level 8

### NCT03445533 (2 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R049 | ctg_results_bor_2018_2021.txt | 0 | OG000 | 0 | 243 | Complete Response=1; Partial Response=20; Stable Disease=45; Progressive Disease=110; Not Evaluable=67 | 243 | 0 | CR=1;PR=20;SD=45;PD=110 / 176 | 67 | RECOVERABLE |
| R050 | ctg_results_bor_2018_2021.txt | 0 | OG001 | 0 | 238 | Complete Response=1; Partial Response=20; Stable Disease=61; Progressive Disease=89; Not Evaluable=67 | 238 | 0 | CR=1;PR=20;SD=61;PD=89 / 171 | 67 | RECOVERABLE |

OM titles: [0] Summary of Independent Reviewer-Assessed Objective Response Rate (ORR) by RECIST v1.1

Group titles: OG000 = Arm A: Ipilimumab; OG001 = Arm B: IMO-2125 Plus Ipilimumab

### NCT03724890 (8 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R051 | ctg_results_bor_2018_2021.txt | 54 | OG001 | 0 | 11 | Complete Response=0; Partial Response=0; Stable Disease or Non-CR/Non-PD=1; Progressive Disease=7; Not Evaluable=3 | 11 | 0 | CR=0;PR=0;SD=1;PD=7 / 8 | 3 | RECOVERABLE |
| R052 | ctg_results_bor_2018_2021.txt | 54 | OG002 | 0 | 4 | Complete Response=0; Partial Response=0; Stable Disease or Non-CR/Non-PD=1; Progressive Disease=0; Not Evaluable=3 | 4 | 0 | CR=0;PR=0;SD=1;PD=0 / 1 | 3 | RECOVERABLE |
| R053 | ctg_results_bor_2018_2021.txt | 54 | OG003 | 0 | 6 | Complete Response=0; Partial Response=0; Stable Disease or Non-CR/Non-PD=0; Progressive Disease=2; Not Evaluable=4 | 6 | 0 | CR=0;PR=0;SD=0;PD=2 / 2 | 4 | RECOVERABLE |
| R054 | ctg_results_bor_2018_2021.txt | 54 | OG004 | 0 | 4 | Complete Response=0; Partial Response=0; Stable Disease or Non-CR/Non-PD=1; Progressive Disease=1; Not Evaluable=2 | 4 | 0 | CR=0;PR=0;SD=1;PD=1 / 2 | 2 | RECOVERABLE |
| R055 | ctg_results_bor_2018_2021.txt | 55 | OG002 | 0 | 4 | Complete Response=0; Partial Response=0; Stable Disease or Non-CR/Non-PD=2; Progressive Disease=1; Not Evaluable=1 | 4 | 0 | CR=0;PR=0;SD=2;PD=1 / 3 | 1 | RECOVERABLE |
| R056 | ctg_results_bor_2018_2021.txt | 55 | OG003 | 0 | 9 | Complete Response=0; Partial Response=0; Stable Disease or Non-CR/Non-PD=2; Progressive Disease=3; Not Evaluable=4 | 9 | 0 | CR=0;PR=0;SD=2;PD=3 / 5 | 4 | RECOVERABLE |
| R057 | ctg_results_bor_2018_2021.txt | 56 | OG000 | 0 | 4 | Complete Response=0; Partial Response=0; Stable Disease or Non-CR/Non-PD=2; Progressive Disease=1; Not Evaluable=1 | 4 | 0 | CR=0;PR=0;SD=2;PD=1 / 3 | 1 | RECOVERABLE |
| R058 | ctg_results_bor_2018_2021.txt | 56 | OG001 | 0 | 5 | Complete Response=0; Partial Response=1; Stable Disease or Non-CR/Non-PD=1; Progressive Disease=1; Not Evaluable=2 | 5 | 0 | CR=0;PR=1;SD=1;PD=1 / 3 | 2 | RECOVERABLE |

OM titles: [54] Part A: Number of Participants With Confirmed Best Overall Response (BOR) as Assessed by Response Evaluation Criteria in Solid Tumors Version 1.1 (RECIST v1.1); [55] Part B: Number of Participants With Confirmed Best Overall Response (BOR) as Assessed by Response Evaluation Criteria in Solid Tumors Version 1.1 (RECIST v1.1); [56] Part FE: Number of Participants With Confirmed Best Overall Response (BOR) as Assessed by Response Evaluation Criteria in Solid Tumors Version 1.1 (RECIST v1.1)

Group titles: OG000 = Part Food Effect: M3814 100 mg BID + Avelumab 800 mg Q2W; OG001 = Part A: M3814 200 mg BID + Avelumab 800 mg Q2W; OG001 = Part Food Effect: M3814 200 mg BID + Avelumab 800 mg Q2W; OG002 = Part A: M3814 250 mg BID + Avelumab 800 mg Q2W; OG002 = Part B: M3814 200 mg BID + Avelumab 800 mg Q2W + RT; OG003 = Part A: M3814 300 mg BID + Avelumab 800 mg Q2W; OG003 = Part B: M3814 250 mg BID + Avelumab 800 mg Q2W + RT; OG004 = Part A: M3814 400 mg BID + Avelumab 800 mg Q2W

### NCT03409614 (5 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R059 | ctg_results_bor_2018_2021.txt | 6 | OG000 | 0 | 108 | Complete Response (CR)=3; Partial Response (PR)=41; Stable Disease (SD)=41; Progressive Disease (PD)=4; Non-CR / Non-PD=3; Not Evaluable (NE)=16 | 108 | 0 | CR=3;PR=41;SD=41;PD=4 / 89 | 19 | RECOVERABLE |
| R060 | ctg_results_bor_2018_2021.txt | 6 | OG001 | 0 | 109 | Complete Response (CR)=5; Partial Response (PR)=35; Stable Disease (SD)=44; Progressive Disease (PD)=15; Non-CR / Non-PD=0; Not Evaluable (NE)=10 | 109 | 0 | CR=5;PR=35;SD=44;PD=15 / 99 | 10 | RECOVERABLE |
| R061 | ctg_results_bor_2018_2021.txt | 6 | OG002 | 0 | 106 | Complete Response (CR)=2; Partial Response (PR)=28; Stable Disease (SD)=51; Progressive Disease (PD)=8; Non-CR / Non-PD=1; Not Evaluable (NE)=16 | 106 | 0 | CR=2;PR=28;SD=51;PD=8 / 89 | 17 | RECOVERABLE |
| R062 | ctg_results_bor_2018_2021.txt | 7 | OG000 | 0 | 312 | CR=20; PR=116; SD=121; PD=22; Non-CR/Non-PD=3; NE=30 | 312 | 0 | CR=20;PR=116;SD=121;PD=22 / 279 | 33 | RECOVERABLE |
| R063 | ctg_results_bor_2018_2021.txt | 7 | OG001 | 0 | 154 | CR=0; PR=34; SD=75; PD=24; Non-CR/Non-PD=1; NE=20 | 154 | 0 | CR=0;PR=34;SD=75;PD=24 / 133 | 21 | RECOVERABLE |

OM titles: [6] Part 1: Best Overall Response (BOR) Per IRC; [7] Part 2: BOR Per IRC

Group titles: OG000 = Part 1: Cemiplimab + Chemotherapy; OG000 = Part 2: Cemiplimab + Chemotherapy; OG001 = Part 1: Cemiplimab+AbbrevChemo+Ipilimumab; OG001 = Part 2: Placebo + Chemotherapy; OG002 = Part 1: Chemotherapy

### NCT03750786 (2 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R064 | ctg_results_bor_2018_2021.txt | 0 | OG000 | 0 | 245 | Complete Response=2; Partial Response=116; Stable Disease=106; Progressive Disease=7; Non-CR/Non-PD=6; No BOR Available=6; Not Evaluable=2 | 245 | 0 | CR=2;PR=116;SD=106;PD=7 / 231 | 14 | RECOVERABLE |
| R065 | ctg_results_bor_2018_2021.txt | 0 | OG001 | 0 | 245 | Complete Response=5; Partial Response=116; Stable Disease=86; Progressive Disease=11; Non-CR/Non-PD=3; No BOR Available=18; Not Evaluable=6 | 245 | 0 | CR=5;PR=116;SD=86;PD=11 / 218 | 27 | RECOVERABLE |

OM titles: [0] Overall Response Rate

Group titles: OG000 = Group A; OG001 = Group B

### NCT03854227 (1 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R066 | ctg_results_bor_2018_2021.txt | 5 | OG000 | 0 | 11 | Complete response (CR)=0; Partial response (PR)=1; Stable disease (SD)=4; Non-CR/Non-PD=0; Progressive disease (PD)=4; Not evaluable (NE)=2 | 11 | 0 | CR=0;PR=1;SD=4;PD=4 / 9 | 2 | RECOVERABLE |

OM titles: [5] Part 2: Number of Participants With Best Overall Response (BOR) Based on Investigator Assessment (RECIST, Version 1.1)

Group titles: OG000 = Part 2A: [2L+ Non-small Cell Lung Cancer (NSCLC)] PF-06939999 6mg QD

### NCT04208958 (1 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R067 | ctg_results_bor_2018_2021.txt | 3 | OG000 | 0;1;2 | 54 | CR=0; NE=0; Unknown=4; PR=1; SD=14; PD=35 | 54 | 0 | CR=0;PR=1;SD=2;PD=16 / 19 | 4 | RECOVERABLE_PER_CLASS (aggregate also exact) |

OM titles: [3] Best Overall Response

Group titles: OG000 = VE800 combination treatment with nivolumab

### NCT04634825 (2 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R068 | ctg_results_bor_2018_2021.txt | 7 | OG000 | 0 | 48 | Complete Response=0; Partial Response=3; Stable Disease=20; Progressive Disease=15; Not Evaluable=10 | 48 | 0 | CR=0;PR=3;SD=20;PD=15 / 38 | 10 | RECOVERABLE |
| R069 | ctg_results_bor_2018_2021.txt | 7 | OG001 | 0 | 14 | Complete Response=0; Partial Response=2; Stable Disease=5; Progressive Disease=2; Not Evaluable=5 | 14 | 0 | CR=0;PR=2;SD=5;PD=2 / 9 | 5 | RECOVERABLE |

OM titles: [7] Best Overall Response (BOR)

Group titles: OG000 = Retifanlimab Cohort; OG001 = Tebotelimab Cohort

### NCT04649060 (2 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R070 | ctg_results_bor_2018_2021.txt | 3 | OG000 | 0 | 27 | Complete Response (CR)=1; Very Good Partial Response (VGPR)=4; Partial Response (PR)=11; Minimal Response (MR)=3; Stable Disease (SD)=3; Progressive Disease (PD)=1; Not Evaluable (NE)=4 | 27 | 0 | CR=1;PR=11;SD=3;PD=1 / 16 | 11 | RECOVERABLE |
| R071 | ctg_results_bor_2018_2021.txt | 3 | OG001 | 0 | 27 | Complete Response (CR)=0; Very Good Partial Response (VGPR)=3; Partial Response (PR)=5; Minimal Response (MR)=5; Stable Disease (SD)=5; Progressive Disease (PD)=5; Not Evaluable (NE)=4 | 27 | 0 | CR=0;PR=5;SD=5;PD=5 / 15 | 12 | RECOVERABLE |

OM titles: [3] Best Response

Group titles: OG000 = Arm A (Melflufen+Dexamethasone+Daratumumab); OG001 = Arm B (Daratumumab)

### NCT04068181 (3 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R072 | ctg_results_bor_2018_2021.txt | 3 | OG000 | 0 | 26 | CR=0; PR=1; SD=7; PD=11; UE=0; Non-CR/Non-PD=1; Not Done=6 | 26 | 0 | CR=0;PR=1;SD=7;PD=11 / 19 | 7 | RECOVERABLE |
| R073 | ctg_results_bor_2018_2021.txt | 3 | OG001 | 0 | 15 | CR=0; PR=1; SD=4; PD=5; UE=1; Non-CR/Non-PD=0; Not Done=4 | 15 | 0 | CR=0;PR=1;SD=4;PD=5 / 10 | 5 | RECOVERABLE |
| R074 | ctg_results_bor_2018_2021.txt | 3 | OG003 | 0 | 15 | CR=3; PR=4; SD=6; PD=1; UE=0; Non-CR/Non-PD=0; Not Done=1 | 15 | 0 | CR=3;PR=4;SD=6;PD=1 / 14 | 1 | RECOVERABLE |

OM titles: [3] BOR Per Modified RECIST v1.1

Group titles: OG000 = Cohort 1 - Locally Recurrent/Metastatic - Primary Resistance; OG001 = Cohort 2 - Locally Recurrent/Metastatic - Acquired Resistance; OG003 = Cohort 4 - Adjuvant Setting - Disease Free Interval ≥ 6 Months

### NCT03671564 (2 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R075 | ctg_results_bor_2018_2021.txt | 7 | OG000 | 0 | 4 | Complete remission (CR)=0; CR with partial hematological recovery (CRh)=0; CR with incomplete hematological recovery (CRi)=0; Partial remission (PR)=0; Morphologic leukemia-free state (MLFS)=0; Stable disease (SD)=1; Progressive disease (PD)=1; Not applicable (NA)=2; Not Evaluable (NE)=0 | 4 | 0 | CR=0;PR=0;SD=1;PD=1 / 2 | 2 | RECOVERABLE |
| R076 | ctg_results_bor_2018_2021.txt | 7 | OG001 | 0 | 5 | Complete remission (CR)=0; CR with partial hematological recovery (CRh)=0; CR with incomplete hematological recovery (CRi)=0; Partial remission (PR)=0; Morphologic leukemia-free state (MLFS)=1; Stable disease (SD)=0; Progressive disease (PD)=1; Not applicable (NA)=3; Not Evaluable (NE)=0 | 5 | 0 | CR=0;PR=0;SD=0;PD=1 / 1 | 4 | RECOVERABLE |

OM titles: [7] Number of Participants With Best Response Following Administration of Milademetan in Participants With Relapsed or Refractory Acute Myeloid Leukemia

Group titles: OG000 = Milademetan (90 mg/Day); OG001 = Milademetan (120 mg/Day)

### NCT05323656 (1 in-scope rows)

| row | payload | OM idx | group | class idx | denom (`denoms`) | corrected full category vector | cat sum | residual | producer cells / evaluable_n | dropped participants | recoverability |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R077 | ctg_results_bor_2022_2026.txt | 5 | OG000 | 0 | 27 | Complete Response=1; Partial Response=8; Stable Disease=10; Progressive Disease=7; Not Evaluable=1 | 27 | 0 | CR=1;PR=8;SD=10;PD=7 / 26 | 1 | RECOVERABLE |

OM titles: [5] Overall Response Rate (ORR)

Group titles: OG000 = Setanaxib 1600 mg and Pembrolizumab 200 mg

## UNRESOLVED rows

None. Every in-scope row in group 3 resolves to a single exact corrected reading, except
NCT04208958 OM 3 OG000, where the *class-level* readings are exact and unambiguous but the
producer's choice of one stratum out of three has no stated selection basis; the collapsed
single-vector reading is recoverable only as the three-class sum. No row required a guess, and
no denominator, category or count in this file was inferred — all are read directly from the
cached payloads at the pointers given.

## Scope statement

This file establishes what the cached registry records do and do not support for 23 NCTs. It makes
no claim about efficacy, safety, selectivity, therapeutic window or clinical readiness, and it does
not correct any manuscript. Job 1's classification and its global counts are context, not my result.
NCTs outside `QA-group3.txt` are outside my group and were not read.
