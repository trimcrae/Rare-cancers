---
id: DOC-OPUS-CAMPAIGN-LEAF-QA-GROUP1
title: "Question A / group 1 — corrected readings for 23 NCTs of the endpoint measurement contract"
level: L4
kind: curation
status: live
purpose: >
  For 23 assigned NCTs, emit the CORRECTED reading of every derived endpoint row that Job 1 marked
  unsupported/ambiguous or that carried an overwrite: the participant denominator the trial actually
  reported (read from `denoms`), the FULL source category vector of every contributing class
  including the categories the producer dropped, the exact residual, and a per-row statement of
  whether a single corrected reading is recoverable or the source is genuinely ambiguous.
scope: >
  L4. Source validation only. It repairs nothing, edits no producer or manuscript, recomputes no
  manuscript quantity, proposes no replacement rate, and lifts no hold. It makes no claim about
  efficacy, safety, selectivity, therapeutic window or clinical readiness.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
related: [DOC-OPUS-CAMPAIGN-CURATION-ENDPOINT-MEASUREMENT-CONTRACT, DOC-OPUS-CAMPAIGN-HOLD-ENDPOINT]
---

# Question A, group 1 — recoverable corrected readings

⛔ The response-endpoint manuscript stays parked. Nothing here reinstates a withdrawn claim, and
nothing here is a corrected rate: this is a reading of what the source records state.

## 1 · Inputs, fences and integrity

- Sole input: the delivered immutable payload cache
  `.../scratchpad/ctg-cache-216bd1b5/` (branch `literature-cache` @ `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`).
  **No network request of any kind was made.** No payload was re-fetched and no second copy was made.
- `sha256sum -c SHA256-MANIFEST.txt` → 13/13 `OK`, **exit code 0**.
- No producer, manuscript build, test suite, gate or preflight was run. No tracked file was written.
- Row tables read (read-only, as context): `CURATION-endpoint-measurement-contract-rows-*.tsv`.
  Job 1's classification and its global counts are **not** restated as findings of this leaf.

## 2 · Assignment reached vs assigned

| quantity | value |
|---|---|
| NCTs assigned (`LEAF-ASSIGNMENTS/QA-group1.txt`) | **23** |
| NCTs found in the shard tables | **23** (none missing, none outside the group read) |
| stored rows in the shard tables belonging to my 23 NCTs | 104 |
| **rows in scope** (`classification` ∈ {unsupported, ambiguous} **or** `overwrite_scope` ≠ `none`) | **69** |
| **rows actually reached and corrected** | **69 / 69 (100%)** |
| output lines emitted (one per source class, not per stored row) | **80** |

In-scope composition: 69 `unsupported`, 0 `ambiguous` (my group holds none of Job 1's 19 ambiguous
rows); `overwrite_scope` = `none` 61, `cross_class` 7, `within_class` 1.

**Fidelity check before correcting anything.** A read-only replay of the producer's own
`_cells_for_groups` logic (category prefix regexes, integer test, last-write-wins assignment) against
the raw payloads reproduced the stored four-cell vector of **69 / 69** rows exactly: **0 mismatches**.
Every corrected reading below is therefore a correction of the row the paper actually used.

## 3 · What is established for my 23 NCTs

1. **A reported participant denominator exists for every one of the 69 rows** —
   `denoms[units=="Participants"].counts[groupId].value`, in the same outcome measure, always
   present, never read by the producer. 69/69.
2. **In 66 of 69 rows the corrected reading is fully recoverable.** All categories of the
   contributing class(es) sum **exactly** to the reported denominator (residual 0), so the
   denominator is the reported one and the full category vector is recovered including every
   category the producer dropped.
3. **In 3 of 69 rows a single corrected category vector is NOT recoverable** — `UNRESOLVED`,
   detailed in §5. The *denominator* is recoverable in all three; the *class selection* is not.
4. **The producer's `evaluable_n` is smaller than the reported denominator in all 69 rows**
   (min 1, median 6, max 112; 0 rows exceed it). Summed over the 69 rows the derived denominators
   are short by **1,047 participant-slots**.
5. **Not all dropped categories are non-evaluable.** Across the contributing classes of my rows the
   producer drops `Stringent Complete Response (sCR)` (12 class-lines, 36 participants),
   `Very Good Partial Response (VGPR)` (12 class-lines, 27 participants),
   `Non-complete Response/ Non-progressive Disease` (4 class-lines, 34 participants),
   `Non-CR/Non-PD (NN)` (2 class-lines, 27 participants) and `Partial Complete Response` (1, 1).
   These are **response** categories; dropping them removes responders from numerator and denominator
   alike. (`Non-CR/Non-PD` with 0 participants appears in 9 further class-lines.)

### 3.1 Dropped-category census, contributing classes of my 69 rows

Counted per class-line (so the four repeated-timepoint classes of NCT02440464 om 4 and the two
therapy-line classes of NCT02150967 om 11 each contribute their own line; those participants are the
same people re-reported and must not be added across classes).

| dropped category title | class-lines | participants |
|---|---|---|
| Unknown | 19 | 210 |
| Not Evaluable | 15 | 289 |
| Missing | 14 | 156 |
| Stringent Complete Response (sCR) | 12 | 36 |
| Very Good Partial Response (VGPR) | 12 | 27 |
| UE | 9 | 55 |
| Not Done | 9 | 9 |
| Non-CR/Non-PD | 9 | 0 |
| Died Before Evaluation | 8 | 7 |
| Not Evaluable (NE) | 7 | 24 |
| NE | 7 | 5 |
| Non-complete Response/ Non-progressive Disease | 4 | 34 |
| Not Done (ND) | 4 | 7 |
| Not evaluated (NE) | 3 | 8 |
| Unevaluable (iUE) | 2 | 99 |
| Non-CR/Non-PD (NN) | 2 | 27 |
| NA (Not applicable) | 2 | 19 |
| Unevaluable (UE) | 2 | 14 |
| Not evaluable | 2 | 7 |
| Not done | 2 | 4 |
| Unknown Response | 2 | 3 |
| Unable to Determine | 2 | 2 |
| NE (Not evaluable) | 2 | 1 |
| Not evaluable (NE) | 2 | 1 |
| Unable to Evaluate (UE) | 1 | 1 |
| Partial Complete Response | 1 | 1 |
| **total (class-lines, not distinct participants)** | **154** | **1,046** |

## 4 · Worked exhibits — the largest recoverable corrections

Each is a single-class outcome measure whose categories sum exactly to the stated denominator, so the
corrected reading is unambiguous.

**E1 · NCT02395172, outcome measure 4, "Number of Participants With Confirmed Best Overall Response
(BOR) as Assessed by an Independent Review Committee", `populationDescription` = "Full analysis set
(FAS) included all participants who were randomized to study."**
Pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02395172] :: outcomeMeasures[4] :: classes[0]`.

| group | reported denom (`denoms`) | full source vector (class[0], every category) | producer stored | residual |
|---|---|---|---|---|
| OG001 | **396** | Complete Response=2, Partial Response=42, Stable Disease=158, Non-complete Response/ Non-progressive Disease=13, Progressive Disease=82, Not Evaluable=99 | CR=2,PR=42,SD=158,PD=82 → n=284 | **396 − 284 = 112** (13 NCRNPD + 99 NE) |
| OG000 | **396** | Complete Response=5, Partial Response=54, Stable Disease=129, Non-complete Response/ Non-progressive Disease=5, Progressive Disease=150, Not Evaluable=53 | CR=5,PR=54,SD=129,PD=150 → n=338 | **396 − 338 = 58** (5 NCRNPD + 53 NE) |

**E2 · NCT02263508, outcome measure 19, "Phase 3: Best Overall Response Assessed Using Modified
irRC-RECIST", `populationDescription` = "All participants randomized in Phase 3".**
Pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02263508] :: outcomeMeasures[19] :: classes[0]`.

| group | reported denom | full source vector | producer stored | residual |
|---|---|---|---|---|
| OG000 | **346** | Complete response (iCR)=28, Partial response (iPR)=110, Stable disease (iSD)=57, Progressive disease (iPD)=56, Unevaluable (iUE)=69, Missing=26 | CR=28,PR=110,SD=57,PD=56 → n=251 | **346 − 251 = 95** |
| OG001 | **346** | Complete response (iCR)=50, Partial response (iPR)=120, Stable disease (iSD)=51, Progressive disease (iPD)=65, Unevaluable (iUE)=30, Missing=30 | CR=50,PR=120,SD=51,PD=65 → n=286 | **346 − 286 = 60** |

**E3 · NCT02566993, outcome measure 7, "Best Antitumor Response by Independent Review Committee".**
Pointer: `ctg_results_bor_2014_2017.txt :: … :: outcomeMeasures[7] :: classes[0]`.
OG000 denom **307**, vector `Complete response=8, Partial response=89, Stable disease=111,
Progressive disease=74, Unknown=25`, stored n=282, residual **25**.
OG001 denom **306**, vector `Complete response=4, Partial response=87, Stable disease=116,
Progressive disease=52, Unknown=47`, stored n=259, residual **47**.

## 5 · Every collapsed class, enumerated — the 8 overwrite rows

One subsection per stored row; **one enumerated line per source class**, which is why the TSV carries
80 lines for 69 stored rows.

### 5.1 NCT02431260 om 7, OG000 "Part 2 / Treatment Group A: 20 MG BID INCB054329" — `within_class`, conflicting
Pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02431260] :: outcomeMeasures[7] :: classes[0] :: groups[OG000]`.
Reported denominator **10**; class[0] (untitled) full vector: `Complete response (CR)=0,
Partial response (PR)=0, Stable disease (SD) >= 6 months=0, Stable disease (SD) < 6 months=4,
Progressive disease (PD)=5, Not evaluable (NE)=1`. Sum = 10 = denominator.
**Content lost:** the two distinct reported categories `SD ≥ 6 months` (0) and `SD < 6 months` (4)
both match the `SD` prefix regex; the second overwrites the first, so the stored `cells.SD=4` does not
identify which reported category it is. `NE=1` dropped. Stored n=9.
**Corrected reading:** denominator 10; CR 0, PR 0, SD(≥6mo) 0, SD(<6mo) 4, PD 5, NE 1. **RECOVERABLE**
— the collision is reversible because both source titles and both values are in the record.

### 5.2 NCT02212015 om 7, OG000 "Pazopanib + Paclitaxel", "Response Rate (RR), Subgroup1 Analysis" — `cross_class`
Pointer: `… :: outcomeMeasures[7] :: groups[OG000]`. Reported denominator **26**.
- `classes[0]` "cutaneous angiosarcoma": `CR=2, PR=6, SD=4, PD=6, NE=0` (sum 18). **Lost entirely** —
  every one of its four matched labels was overwritten by classes[1]; `NE=0` dropped.
- `classes[1]` "visceral angiosarcoma": `CR=0, PR=1, SD=2, PD=4, NE=1` (sum 8). Survived as the stored
  row (`CR=0,PR=1,SD=2,PD=4`, n=7); its `NE=1` dropped.
- 18 + 8 = 26 = the reported denominator: the two classes **partition** the arm.
**Corrected reading: RECOVERABLE.** Denominator 26; union CR 2, PR 7, SD 6, PD 10, NE 1.
A trial reporting 9 responses in 26 patients entered the corpus as 1 response in 7.

### 5.3 NCT02212015 om 8, OG000, "Response Rate (RR), Subgroup 2 Analysis" — `cross_class`
Pointer: `… :: outcomeMeasures[8] :: groups[OG000]`. Reported denominator **26**.
- `classes[0]` "primary angiosarcoma": `CR=0, PR=5, SD=3, PD=5, NE=0` (sum 13) — all four labels lost
  to classes[1].
- `classes[1]` "secondary angiosarcoma": `CR=2, PR=2, SD=3, PD=5, NE=1` (sum 13) — survived, stored
  n=12.
- 13 + 13 = 26: a **partition**, on a different axis than om 7.
**Corrected reading: RECOVERABLE.** Denominator 26; union CR 2, PR 7, SD 6, PD 10, NE 1.

> Cross-check within my own group (not a duplicate adjudication, which is the parent's): the same arm
> is reported three times in this record — om 6 (single class, `CR=2, PR=7, SD=6, PD=10, NE=1`),
> om 7 (cutaneous/visceral) and om 8 (primary/secondary). All three unions are **identical**:
> 2/7/6/10 with NE=1 over 26. The corrected readings of the two collapsed rows are confirmed by the
> record's own uncollapsed om 6. Whether these are one arm or three rows is Job 2's question.

### 5.4 NCT02440464 om 3, "Percentage of Participants With Best Response to Treatment After Randomization" — `cross_class`, both groups
Pointer: `… :: studies[nct=NCT02440464] :: outcomeMeasures[3]`.
The two classes are **baseline-response strata** that partition the randomized arm.

OG000 "Ixazomib Maintenance", reported denominator **21**:
- `classes[0]` "Participants in sCR/CR at Randomization": `sCR=6, CR=2, VGPR=0, PR=0, SD=0, PD=1`
  (sum 9). Lost: all four matched labels overwritten by classes[1]; `sCR=6`, `VGPR=0` dropped.
- `classes[1]` "Participants Not in sCR/CR at Randomization": `sCR=3, CR=2, VGPR=4, PR=2, SD=0, PD=1`
  (sum 12). Survived → stored `CR=2,PR=2,SD=0,PD=1`, n=5. Lost: `sCR=3`, `VGPR=4` dropped.
- 9 + 12 = 21 = denominator. **RECOVERABLE.** Union: sCR 9, CR 4, VGPR 4, PR 2, SD 0, PD 2 over 21.
  Under any myeloma reading of response, 19 of 21 are ≥PR; the stored row says 4 of 5.

OG001 "Placebo", reported denominator **22**:
- `classes[0]` "in sCR/CR at Randomization": `sCR=5, CR=4, VGPR=1, PR=0, SD=0, PD=1` (sum 11) — lost.
- `classes[1]` "Not in sCR/CR at Randomization": `sCR=4, CR=3, VGPR=4, PR=0, SD=0, PD=0` (sum 11) —
  survived → stored `CR=3,PR=0,SD=0,PD=0`, n=3.
- 11 + 11 = 22 = denominator. **RECOVERABLE.** Union: sCR 9, CR 7, VGPR 5, PR 0, SD 0, PD 1 over 22.

### 5.5 NCT02440464 om 4, "Percentage of Participants With Response to Treatment" — `cross_class`, both groups — **UNRESOLVED**
Pointer: `… :: outcomeMeasures[4]`. Four classes = **two timepoints × two baseline strata**.

OG000 "Ixazomib Maintenance", reported denominator **21**:
| class | title | full vector for OG000 | sum |
|---|---|---|---|
| [0] | 18 months, in sCR/CR at randomization | sCR=3, CR=2, VGPR=1, PR=0, SD=0, PD=1, Died Before Evaluation=1, Not Evaluable=1 | 9 |
| [1] | 18 months, not in sCR/CR | sCR=2, CR=1, VGPR=3, PR=1, SD=1, PD=0, Died=0, NE=4 | 12 |
| [2] | 24 months, in sCR/CR | sCR=2, CR=3, VGPR=1, PR=0, SD=0, PD=1, Died=1, NE=1 | 9 |
| [3] | 24 months, not in sCR/CR | sCR=2, CR=1, VGPR=3, PR=0, SD=1, PD=0, Died=0, NE=5 | 12 |

Classes [0]–[2] lost every matched label to the next class; `classes[3]` survived → stored
`CR=1,PR=0,SD=1,PD=0`, n=2. All four class sums total 42 = **2 × 21**: the 18-month and 24-month
classes re-report the **same 21 participants**.
**Verdict: UNRESOLVED.** The denominator is recoverable (**21**), and each timepoint's union is
recoverable (18 mo: sCR 5, CR 3, VGPR 4, PR 1, SD 1, PD 1, Died 1, NE 5 = 21; 24 mo: sCR 4, CR 4,
VGPR 4, PR 0, SD 1, PD 1, Died 1, NE 6 = 21). A **single** corrected reading is not: the record states
no basis for choosing the 18-month or the 24-month assessment as "the" response for this arm, and
this outcome measure is a landmark-response tabulation, not a best-overall-response table at all.

OG001 "Placebo", reported denominator **22**:
| class | title | full vector for OG001 | sum |
|---|---|---|---|
| [0] | 18 months, in sCR/CR | sCR=3, CR=3, VGPR=2, PR=0, SD=0, PD=1, Died=2, NE=0 | 11 |
| [1] | 18 months, not in sCR/CR | sCR=3, CR=2, VGPR=4, PR=0, SD=0, PD=0, Died=0, NE=2 | 11 |
| [2] | 24 months, in sCR/CR | sCR=1, CR=6, VGPR=0, PR=0, SD=0, PD=1, Died=2, NE=1 | 11 |
| [3] | 24 months, not in sCR/CR | sCR=2, CR=2, VGPR=4, PR=0, SD=0, PD=0, Died=1, NE=2 | 11 |

`classes[3]` survived → stored `CR=2,PR=0,SD=0,PD=0`, n=2. Sums 44 = **2 × 22**.
**Verdict: UNRESOLVED**, same reason. Denominator **22** is recoverable; 18 mo union sCR 6, CR 5,
VGPR 6, PR 0, SD 0, PD 1, Died 2, NE 2 = 22; 24 mo union sCR 3, CR 8, VGPR 4, PR 0, SD 0, PD 1,
Died 3, NE 3 = 22.

### 5.6 NCT02150967 om 11, OG000 "Cohort 1: FGFR2 Fusion/Rearrangements" — `cross_class` — **UNRESOLVED**
Pointer: `ctg_results_bor_2014_2017.txt :: studies[nct=NCT02150967] :: outcomeMeasures[11] :: groups[OG000]`.
Outcome measure title: "Retrospective Analysis of Post-second-line Antineoplastic Treatment Outcomes…".
Reported denominator **59**.
- `classes[0]` "After Second-Line Therapy (Prior to Infigratinib Treatment)":
  `Complete response=0, Partial response=0, Stable disease=19, Progressive disease=22, Unknown=18,
  Not done=0` (sum 59). All four matched labels lost to classes[1]; `Unknown=18` dropped.
- `classes[1]` "Third or Later-Line Therapy (Infigratinib)":
  `Complete response=0, Partial response=17, Stable disease=31, Progressive disease=7, Unknown=0,
  Not done=4` (sum 59). Survived → stored `CR=0,PR=17,SD=31,PD=7`, n=55; `Not done=4` dropped.
- 59 + 59 = 118 = **2 × 59**: the two classes are the **same 59 participants** assessed on two
  different lines of therapy, not a partition.
**Verdict: UNRESOLVED.** Denominator **59** recoverable, and each class's own corrected vector is
recoverable as listed. A single corrected reading for "this arm's best overall response" is not:
the record reports two distinct therapy-line response tables over one population and states no
selection basis. (The prior-line class is by construction not a response to the study drug; saying
so would be a selection rule this leaf is not authorised to adopt — see the parked selection-rule
requirement.)

## 6 · Per-row corrected readings — all 69

Full category vectors, per-class breakdowns, matched/dropped splits, surviving labels and
per-class source pointers are in `LEAF-QA-group1.tsv` (80 lines, one per contributing source class).
The table below is the stored-row roll-up.

| NCT | om | group | group title | rep. denom | producer `evaluable_n` | shortfall | classes contributing | corrected CR/PR/SD/PD (all contributing classes) | dropped categories (title=value) | recoverable |
|---|---|---|---|---|---|---|---|---|---|---|
| NCT02083653 | 1 | OG000 | Arm A: Sym004 (12 mg/kg) | **83** | 78 | 5 | 0 | 0/11/40/27 | Not Evaluable (NE)=5 | YES |
| NCT02083653 | 1 | OG001 | Arm B: Sym004 (9/6 mg/kg) | **86** | 83 | 3 | 0 | 0/8/47/28 | Not Evaluable (NE)=3 | YES |
| NCT02083653 | 1 | OG002 | Arm C: Investigator's Choice | **85** | 70 | 15 | 0 | 1/1/37/31 | Not Evaluable (NE)=15 | YES |
| NCT02089334 | 4 | OG000 | 125 mg/m^2 RX-0201 + Everolimus (S | **3** | 2 | 1 | 0 | 0/0/2/0 | Not Evaluable (NE)=0; Not Done (ND)=1 | YES |
| NCT02089334 | 4 | OG001 | 200 mg/m^2/Day RX-0201 + Everolimu | **4** | 3 | 1 | 0 | 0/0/1/2 | Not Evaluable (NE)=0; Not Done (ND)=1 | YES |
| NCT02089334 | 4 | OG002 | 250 mg/m^2/Day RX-0201 + Everolimu | **4** | 1 | 3 | 0 | 0/0/1/0 | Not Evaluable (NE)=1; Not Done (ND)=2 | YES |
| NCT02089334 | 4 | OG003 | RX-0201 Plus Everolimus (Stage 2) | **11** | 8 | 3 | 0 | 0/0/7/1 | Not Evaluable (NE)=0; Not Done (ND)=3 | YES |
| NCT02124772 | 10 | OG000 | Part A - TMT 0.0125 mg/kg/Day | **3** | 1 | 2 | 0 | 0/0/1/0 | Non-CR/Non-PD=0; Unknown=0; Missing=2 | YES |
| NCT02124772 | 10 | OG001 | Part A - TMT 0.025 mg/kg/Day | **19** | 3 | 16 | 0 | 0/1/2/0 | Non-CR/Non-PD=0; Unknown=0; Missing=16 | YES |
| NCT02124772 | 10 | OG002 | Part A - TMT 0.032 mg/kg/Day | **12** | 6 | 6 | 0 | 0/1/3/2 | Non-CR/Non-PD=0; Unknown=0; Missing=6 | YES |
| NCT02124772 | 10 | OG003 | Part A - TMT 0.04 mg/kg/Day | **16** | 4 | 12 | 0 | 0/0/4/0 | Non-CR/Non-PD=0; Unknown=2; Missing=10 | YES |
| NCT02124772 | 10 | OG004 | Part B - Neuroblastoma | **11** | 7 | 4 | 0 | 0/1/1/5 | Non-CR/Non-PD=0; Unknown=1; Missing=3 | YES |
| NCT02124772 | 10 | OG006 | Part B - NF-1 With PN | **10** | 8 | 2 | 0 | 0/0/8/0 | Non-CR/Non-PD=0; Unknown=0; Missing=2 | YES |
| NCT02124772 | 10 | OG010 | Part C - TMT 0.032 mg/kg/Day + 100 | **6** | 5 | 1 | 0 | 2/2/1/0 | Non-CR/Non-PD=0; Unknown=0; Missing=1 | YES |
| NCT02124772 | 10 | OG011 | Part D - LGG | **20** | 19 | 1 | 0 | 2/9/8/0 | Non-CR/Non-PD=0; Unknown=1; Missing=0 | YES |
| NCT02124772 | 10 | OG012 | Part D - LCH | **10** | 9 | 1 | 0 | 3/3/3/0 | Non-CR/Non-PD=0; Unknown=0; Missing=1 | YES |
| NCT02150967 | 11 | OG000 | Cohort 1: FGFR2 Fusion/Rearrangeme | **59** | 55 | 4 | 0,1 | UNRESOLVED | Unknown=18; Not done=0; Unknown=0; Not done=4 | **UNRESOLVED** |
| NCT02212015 | 6 | OG000 | Pazopanib + Paclitaxel | **26** | 25 | 1 | 0 | 2/7/6/10 | NE=1 | YES |
| NCT02212015 | 7 | OG000 | Pazopanib + Paclitaxel | **26** | 7 | 19 | 0,1 | 2/7/6/10 | NE=0; NE=1 | YES |
| NCT02212015 | 8 | OG000 | Pazopanib + Paclitaxel | **26** | 12 | 14 | 0,1 | 2/7/6/10 | NE=0; NE=1 | YES |
| NCT02259582 | 0 | OG002 | Demcizumab/Demcizumab Arm (Arm 3) | **29** | 26 | 3 | 0 | 0/6/15/5 | Not evaluable (NE)=0; Missing=3 | YES |
| NCT02263508 | 4 | OG000 | Phase 1b: Talimogene Laherparepvec | **21** | 20 | 1 | 0 | 9/4/1/6 | Unable to Evaluate (UE)=1 | YES |
| NCT02263508 | 14 | OG000 | Phase 3: Placebo + Pembrolizumab | **346** | 293 | 53 | 0 | 40/103/30/120 | Non-CR/Non-PD (NN)=16; Unevaluable (UE)=11; Missing=26 | YES |
| NCT02263508 | 14 | OG001 | Phase 3: Talimogene Laherparepvec  | **346** | 302 | 44 | 0 | 62/106/28/106 | Non-CR/Non-PD (NN)=11; Unevaluable (UE)=3; Missing=30 | YES |
| NCT02263508 | 19 | OG000 | Phase 3: Placebo + Pembrolizumab | **346** | 251 | 95 | 0 | 28/110/57/56 | Unevaluable (iUE)=69; Missing=26 | YES |
| NCT02263508 | 19 | OG001 | Phase 3: Talimogene Laherparepvec  | **346** | 286 | 60 | 0 | 50/120/51/65 | Unevaluable (iUE)=30; Missing=30 | YES |
| NCT02277093 | 2 | OG000 | Pacritinib | **11** | 7 | 4 | 0 | 0/0/1/6 | Not evaluable=4 | YES |
| NCT02336165 | 6 | OG003 | Cohort B3 | **33** | 32 | 1 | 0 | 0/3/18/11 | Unknown Response=1 | YES |
| NCT02336165 | 6 | OG004 | Cohort C | **22** | 20 | 2 | 0 | 0/0/6/14 | Unknown Response=2 | YES |
| NCT02347917 | 5 | OG002 | MPM or NSCLC: BBI608 + Pem + CDDP  | **4** | 3 | 1 | 0 | 0/0/3/0 | Not evaluated (NE)=1 | YES |
| NCT02347917 | 5 | OG003 | MPM: BBI608 + Pem + CDDP (Phase 2  | **24** | 21 | 3 | 0 | 0/8/11/2 | Not evaluated (NE)=3 | YES |
| NCT02347917 | 5 | OG004 | MPM: BBI608 + Pem + CDDP (Phase 2  | **25** | 21 | 4 | 0 | 0/8/11/2 | Not evaluated (NE)=4 | YES |
| NCT02395172 | 4 | OG000 | Avelumab | **396** | 338 | 58 | 0 | 5/54/129/150 | Non-complete Response/ Non-progressive Disease=5; Not Evaluable=53 | YES |
| NCT02395172 | 4 | OG001 | Docetaxel | **396** | 284 | 112 | 0 | 2/42/158/82 | Non-complete Response/ Non-progressive Disease=13; Not Evaluable=99 | YES |
| NCT02395172 | 5 | OG000 | Avelumab | **264** | 229 | 35 | 0 | 4/46/86/93 | Non-complete Response/ Non-progressive Disease=4; Not Evaluable=31 | YES |
| NCT02395172 | 5 | OG001 | Docetaxel | **265** | 192 | 73 | 0 | 1/30/104/57 | Non-complete Response/ Non-progressive Disease=12; Not Evaluable=61 | YES |
| NCT02421588 | 3 | OG000 | Lurbinectedin | **221** | 205 | 16 | 0 | 3/29/90/83 | Unknown=16 | YES |
| NCT02421588 | 3 | OG001 | Control (PLD or Topotecan) | **221** | 197 | 24 | 0 | 3/25/97/72 | Unknown=24 | YES |
| NCT02421588 | 4 | OG000 | Lurbinectedin | **221** | 205 | 16 | 0 | 3/32/107/63 | Unknown=16 | YES |
| NCT02421588 | 4 | OG001 | Control (PLD or Topotecan) | **221** | 199 | 22 | 0 | 2/35/94/68 | Unknown=22 | YES |
| NCT02421588 | 7 | OG000 | Lurbinectedin | **173** | 158 | 15 | 0 | 13/33/95/17 | Unknown=15 | YES |
| NCT02421588 | 7 | OG001 | Control (PLD or Topotecan) | **165** | 142 | 23 | 0 | 3/29/94/16 | Unknown=23 | YES |
| NCT02431260 | 7 | OG000 | Part 2 / Treatment Group A: 20 MG  | **10** | 9 | 1 | 0 | 0/0/4/5 | Not evaluable (NE)=1 | YES |
| NCT02440464 | 3 | OG000 | Ixazomib Maintenance | **21** | 5 | 16 | 0,1 | 4/2/0/2 | Stringent Complete Response (sCR)=6; Very Good Partial Response (VGPR)=0; Stringent Complete Response (sCR)=3; Very Good | YES |
| NCT02440464 | 3 | OG001 | Placebo | **22** | 3 | 19 | 0,1 | 7/0/0/1 | Stringent Complete Response (sCR)=5; Very Good Partial Response (VGPR)=1; Stringent Complete Response (sCR)=4; Very Good | YES |
| NCT02440464 | 4 | OG000 | Ixazomib Maintenance | **21** | 2 | 19 | 0,1,2,3 | UNRESOLVED | Stringent Complete Response (sCR)=3; Very Good Partial Response (VGPR)=1; Died Before Evaluation=1; Not Evaluable=1; Str | **UNRESOLVED** |
| NCT02440464 | 4 | OG001 | Placebo | **22** | 2 | 20 | 0,1,2,3 | UNRESOLVED | Stringent Complete Response (sCR)=3; Very Good Partial Response (VGPR)=2; Died Before Evaluation=2; Not Evaluable=0; Str | **UNRESOLVED** |
| NCT02472964 | 0 | OG000 | Herceptin© + Taxane | **228** | 215 | 13 | 0 | 0/146/49/20 | Not Evaluable=13 | YES |
| NCT02472964 | 0 | OG001 | MYL-1401O Trastuzumab + Taxane | **230** | 217 | 13 | 0 | 3/157/48/9 | Not Evaluable=13 | YES |
| NCT02475213 | 11 | OG000 | Cohort 1 | **6** | 5 | 1 | 0 | 0/0/4/1 | NE=1 | YES |
| NCT02475213 | 12 | OG000 | Cohort 1 | **6** | 5 | 1 | 0 | 0/0/4/1 | NE=1 | YES |
| NCT02509507 | 4 | OG000 | Part 1: Monotherapy Group A | **23** | 8 | 15 | 0 | 0/0/1/7 | UE=13; Not Done=2 | YES |
| NCT02509507 | 4 | OG001 | Part 1: Monotherapy Group B | **5** | 2 | 3 | 0 | 0/0/1/1 | UE=3; Not Done=0 | YES |
| NCT02509507 | 4 | OG002 | Part 1: Combination Therapy Group  | **24** | 16 | 8 | 0 | 0/2/4/10 | UE=7; Not Done=1 | YES |
| NCT02509507 | 4 | OG003 | Part 1: Combination Therapy Group  | **22** | 12 | 10 | 0 | 0/3/6/3 | UE=10; Not Done=0 | YES |
| NCT02509507 | 4 | OG004 | Part 2: Hormone Receptor Positive  | **10** | 5 | 5 | 0 | 0/1/1/3 | UE=5; Not Done=0 | YES |
| NCT02509507 | 4 | OG005 | Part 2: Triple Negative Breast Can | **18** | 9 | 9 | 0 | 2/1/1/5 | UE=6; Not Done=3 | YES |
| NCT02509507 | 4 | OG006 | Part 2: Cutaneous Squamous Cell Ca | **10** | 4 | 6 | 0 | 0/1/1/2 | UE=4; Not Done=2 | YES |
| NCT02509507 | 4 | OG007 | Part 2: Basal Cell Carcinoma (BCC) | **5** | 3 | 2 | 0 | 0/1/2/0 | UE=2; Not Done=0 | YES |
| NCT02509507 | 4 | OG008 | Part 2: Colorectal Adenocarcinoma  | **10** | 4 | 6 | 0 | 0/0/3/1 | UE=5; Not Done=1 | YES |
| NCT02536794 | 12 | OG000 | Treatment (MEDI4736, Tremelimumab) | **30** | 27 | 3 | 0 | 1/3/4/19 | Not evaluable=3 | YES |
| NCT02566993 | 7 | OG000 | Lurbinectedin/Doxorubicin | **307** | 282 | 25 | 0 | 8/89/111/74 | Unknown=25 | YES |
| NCT02566993 | 7 | OG001 | Topotecan or Cyclophosphamide/Doxo | **306** | 259 | 47 | 0 | 4/87/116/52 | Unknown=47 | YES |
| NCT02575807 | 4 | OG002 | Phase 1: CRS-207/IDO 300 mg | **13** | 10 | 3 | 0 | 0/0/4/6 | Not Evaluable=3 | YES |
| NCT02578641 | 4 | OG000 | Chemo + EBV-CTL | **164** | 154 | 10 | 0 | 6/94/45/9 | NE (Not evaluable)=1; NA (Not applicable)=9 | YES |
| NCT02578641 | 4 | OG001 | Chemo Only | **166** | 156 | 10 | 0 | 14/91/41/10 | NE (Not evaluable)=0; NA (Not applicable)=10 | YES |
| NCT02584829 | 2 | OG001 | Group 2 (Avelumab, MHC Class I Up- | **7** | 6 | 1 | 0 | 2/1/0/3 | Partial Complete Response=1 | YES |
| NCT02593786 | 3 | OG000 | Cohort A: Nivolumab 3 mg/kg Q2W | **15** | 14 | 1 | 0 | 0/3/2/9 | Unable to Determine=1 | YES |

## 7 · Summary of verdicts

| verdict | rows |
|---|---|
| corrected reading **RECOVERABLE** (denominator read from `denoms`, full category vector recovered) | **66** |
| **UNRESOLVED** — denominator recoverable, single category vector not (repeated assessment of one population across classes with no stated selection basis) | **3** |
| total in scope | **69** |

The 3 UNRESOLVED rows are NCT02440464 om 4 OG000, NCT02440464 om 4 OG001, and NCT02150967 om 11
OG000 (§5.5, §5.6). They are exactly the rows whose contributing-class categories sum to a
**multiple** of the reported denominator rather than to it.

## 8 · What this does and does not establish

**Establishes**, for my 23 NCTs only, from the raw records:
- The reported participant denominator is present in 69/69 in-scope rows and was not read.
- 66/69 corrected readings are fully recoverable from the delivered cache; 3 are not, for a stated
  and checkable reason.
- The producer's derived denominators are collectively short by 1,047 participant-slots on these 69
  rows, and the dropped content includes explicit **response** categories — sCR 36 and VGPR 27
  participant-entries, plus 62 in Non-CR/Non-PD-type categories (`Non-complete Response/
  Non-progressive Disease` 34, `Non-CR/Non-PD (NN)` 27, `Partial Complete Response` 1,
  `Non-CR/Non-PD` 0) — counted per class-line, so the NCT02440464 om 4 timepoint classes contribute
  the same participants more than once and these are not distinct-patient totals.
- In 7 rows the stored vector is one stratum, subgroup or timepoint of the arm, and the collapsed
  classes are enumerated above with everything lost.

**Does not establish:** any corrected response rate, any manuscript quantity, any statement about
arm identity, duplication or overlap (Job 2), arm-level disease or phase (Job 3), or anything about
efficacy, safety, selectivity or clinical readiness. Adopting any corrected reading as an input is a
separate authorised act that is not performed here.
