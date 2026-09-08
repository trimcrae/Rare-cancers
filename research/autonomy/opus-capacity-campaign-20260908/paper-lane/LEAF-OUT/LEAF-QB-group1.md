# LEAF QB-group1 — why selected cohort denominators exceed registered enrollment (45 trials)

Leaf worker output. Question B, group 1. Scope: the 45 NCTs in
`LEAF-ASSIGNMENTS/QB-group1.txt` and nothing else.

## Provenance and verification

- Source: the immutable cache
  `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5/`
  (branch `literature-cache` @ `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`).
- `sha256sum -c SHA256-MANIFEST.txt` → all 13 files `OK`, **exit code 0**.
- No network request was made. No producer, gate, test or build was run. Nothing tracked was edited.
- Job 2 artifacts used as read-only context (its counts are its findings, not mine):
  `CURATION-endpoint-identity-and-overlap-artifacts/OVERLAP-enrollment-check.tsv`,
  `.../SELECTED-cohort-response-measurements.tsv`, `.../RULE-PREREGISTERED.md`.
- Per-trial source records were re-read from the cached payloads under Job 2's R0 canonicalisation
  (per `nctId`, the copy with the most populated fields). Every trial in this group canonicalised to
  a single payload; the payload name is carried in every row of the TSV.

**Coverage: 45 of 45 assigned trials reached.** 0 missing from the cache, 0 unreadable.
280 selected cohorts adjudicated (matches the `selected_cohorts` column of
`OVERLAP-enrollment-check.tsv` summed over these 45 trials).

## Item 4 first — enrollment type

**All 45 trials in this group carry `enrollment_type = ACTUAL`.** None is `ESTIMATED`.
The "estimated enrollment below a reported denominator" case therefore does **not** occur anywhere
in this group and nothing here needs separating out on that ground. (Source: `enrollment_type`
column of `OVERLAP-enrollment-check.tsv`, cross-checked against
`protocolSection.designModule.enrollmentInfo.type` in the cached payload for each trial.)

## Mechanism vocabulary used

Job 2's candidate list is used where it fits. Four codes were added because the record showed a
mechanism Job 2's list does not name; they are marked **[new]**.

| code | meaning |
|---|---|
| `POOLED_WITH_COMPONENTS` | an explicit total / pooled / combined cohort selected alongside its own components |
| `MULTI_AXIS_PARTITION` | two or more complete partitions of one population on different axes (age, taxane, ER status, mutation, prior lines) |
| `DENOM_VARIES_BY_MEASURE` | one cohort carries different `Participants` denominators in different outcome measures; the ladder's step **e** took the larger |
| `REGISTRY_INCONSISTENCY` | demonstrably disjoint cohorts whose results-section counts still exceed the registered enrollment field |
| `SEQUENTIAL_PHASE` **[new]** | cohorts are successive treatment periods / study parts of the *same* participants (mono → combination, Part A → Part B, core → extension, induction → maintenance) |
| `CROSSOVER_OR_SWITCH` **[new]** | a cohort made of participants who crossed over or switched out of another selected cohort of the same trial |
| `NESTED_SUBSET` **[new]** | a cohort that is a stated restriction of another selected cohort (biomarker-positive, RP2D-only, line-of-therapy-restricted) rather than a pooled parent |
| `DUPLICATE_COHORT_IDENTITY` **[new]** | one cohort enters twice because the record titles it two ways, so the `(nct, normalised group title)` key splits it |
| `COMPARISON_SET_REUSE` **[new]** | one randomised arm entered twice under two comparison-specific denominators |
| `PARTIAL_POPULATION_OVERLAP` **[new]** | two analysis sets share some but not all participants, so no whole cohort can be dropped |
| `UNRESOLVED` | the record cannot settle it |

`DUPLICATE_COHORT_IDENTITY` is the one that bears on Job 2's own key choice: the rule's key is the
normalised group title, and NFKC + casefold + whitespace collapse + outer-punctuation strip does not
merge `First Line` with `First-line` (NCT01698918) or `FGFR2 Fusions` with
`FGFR2 Fusion/Rearrangements` (NCT02150967). That is reported as an observation about these records,
not as a change to Job 2's rule, which is Job 2's to own.

## Distribution over the 45 trials (primary mechanism)

| primary mechanism | trials |
|---|---|
| `POOLED_WITH_COMPONENTS` | 18 |
| `CROSSOVER_OR_SWITCH` | 5 |
| `MULTI_AXIS_PARTITION` | 5 |
| `SEQUENTIAL_PHASE` | 5 |
| `DUPLICATE_COHORT_IDENTITY` | 4 |
| `NESTED_SUBSET` | 2 |
| `REGISTRY_INCONSISTENCY` (excess is *not* overlap) | 2 |
| `DENOM_VARIES_BY_MEASURE` | 2 |
| `COMPARISON_SET_REUSE` | 1 |
| `PARTIAL_POPULATION_OVERLAP` | 1 |

Counting every mechanism cited, not just the primary one, over the 45 trials:
`POOLED_WITH_COMPONENTS` 20, `SEQUENTIAL_PHASE` 7, `CROSSOVER_OR_SWITCH` 6,
`REGISTRY_INCONSISTENCY` 6, `DUPLICATE_COHORT_IDENTITY` 6, `MULTI_AXIS_PARTITION` 5,
`NESTED_SUBSET` 4, `DENOM_VARIES_BY_MEASURE` 3, `COMPARISON_SET_REUSE` 1,
`PARTIAL_POPULATION_OVERLAP` 1. No trial in this group needed `UNRESOLVED` as its *mechanism* —
the two `UNRESOLVED` verdicts below are about the reduction (item 3), not the mechanism (item 1).

Reducibility to a non-overlapping set from the record alone (TSV `reducible` column):
**`YES` 36, `NO_OVERLAP` 4, `PARTIAL` 3, `UNRESOLVED` 2.**

An important negative result: **in 4 of the 45 trials the excess is not an overlap finding at all.**
In NCT01577758, NCT01597388, NCT01661270 and NCT01852292 the selected cohorts are already
non-overlapping and their denominators still exceed registered enrollment — by 1, 1, 10 and 1
participant. Those excesses are registry/analysis-set inconsistencies inside the record, and must
not be reported as double-counted patients.

---

## Per-trial adjudication

Pointer convention: `payload · NCT · om[i] · 'group title' = denominator`. `om[i]` is the zero-based
index into `resultsSection.outcomeMeasuresModule.outcomeMeasures`. All enrollment types are ACTUAL
and are not repeated per trial.

### NCT01271725 — enroll 74, selected 2, sum 113, excess 39 — `SEQUENTIAL_PHASE`
`ctg_results_bor_2010_2013 · om[0]` (PRIMARY, "Percentage of Participants With Objective Response
(OR) … RECIST 1.1"): `'Afatinib Monotherapy' = 74`, `'Afatinib and Paclitaxel or Vinorelbine
Combination Therapy' = 39`. The arm descriptions settle it: paclitaxel and vinorelbine were given
"additionally … **on disease progression on afatinib monotherapy**", and the monotherapy treated set
(74) equals registered enrollment. The 39 are the subset who progressed and continued.
**Reducible: YES → {`Afatinib Monotherapy` 74} = 74 = enrollment.**

### NCT01289041 — enroll 70, selected 3, sum 140, excess 70 — `POOLED_WITH_COMPONENTS`
`om[0]` (PRIMARY, "Best Overall Response Rate (BORR) According to PI3K Activation Pathway Status"):
`'All Patients' = 70` (flagged pooled by Job 2) alongside `'Activated Pl3K' = 49` and
`'Non-Activated Pl3K' = 21`; 49 + 21 = 70 exactly.
**Reducible: YES → {49, 21} = 70 = enrollment.**

### NCT01324830 — enroll 69, selected 22, sum 207, excess 138 — `POOLED_WITH_COMPONENTS` + `DENOM_VARIES_BY_MEASURE`
`om[1]` (SECONDARY, "Best Overall Response") carries **three nested levels at once**:
`'Total Patients' = 69`, the two schedule totals `'Schedule A Total (Total A)' = 47` and
`'Schedule B Total (Total B)' = 22`, and the 19 individual dose cohorts `A1…A11`, `B1…B8`.
Secondary mechanism: the same dose groups carry different denominators across outcome measures —
e.g. `'…9 mg (A2)'` is 3 at `om[0]`/`om[2]`, 2 at `om[1]`; `'Total Patients'` is 64 at `om[0]`, 69 at
`om[1]`; and `'…90 mg (B5)'` is 3 at `om[1]`, 1 at `om[2]`.
**Reducible: YES → the 19 dose-level cohorts at their selected denominators = 69 = enrollment**
(A total 47 + B total 22), dropping `Total Patients`, `Total A`, `Total B`.

### NCT01325428 — enroll 26, selected 2, sum 36, excess 10 — `SEQUENTIAL_PHASE`
`om[2]` `'Part A: Afatinib Once Daily (OD).' = 26`; `om[3]` `'Part B: Afatinib Once Daily
(OD)+V (Vinorelbine).' = 10`. `om[2]`'s time frame states the Part A window runs until "start of
next treatment (**either Part B combination therapy** or new anti-cancer therapy)", and `om[10]`
carries a single combined group `'Afatinib Once Daily (OD). Afatinib+V (Vinorelbine).' = 26`.
Part B is the continuation subset of Part A.
**Reducible: YES → {`Part A` 26} = 26 = enrollment.**

### NCT01336634 — enroll 177, selected 4, sum 191, excess 14 — `CROSSOVER_OR_SWITCH`
`om[0]` (PRIMARY, ORR): `'Cohort A (Dabrafenib Monotherapy)' = 78`, `'Cohort B …' = 57`,
`'Cohort C …' = 36`, `'Crossover - Double Combination (Dabrafenib+Trametinib): DAB 150MG BID,
TRA 2mG QD' = 20`. The Cohort A arm description states participants "adequately tolerating
dabrafenib as a single agent … **had the option to switch to** Dabrafenib (150 mg BID) and
Trametinib (2 mg once daily) combination treatment", so the crossover group comes out of Cohort A.
**Reducible: YES → {78, 57, 36} = 171 ≤ 177.**

### NCT01420081 — enroll 67, selected 5, sum 91, excess 24 — `POOLED_WITH_COMPONENTS`
`om[3]` carries `'PF-05212384 (PI3K Basal + Activated)' = 38` **alongside its own components**
`'PF-05212384 (PI3K Activated)' = 19` and `'PF-05212384 (PI3K Basal)' = 19` (19+19 = 38 exactly).
Note the pooled parent is **not** flagged by Job 2's pooled vocabulary — "Basal + Activated" is not
in `{total, overall, all participants, all patients, combined}`.
**Reducible: YES → {PF-04691502 Activated 11, PF-04691502 Basal 4 (`om[2]`), PF-05212384 Activated
19, PF-05212384 Basal 19} = 53 ≤ 67.**

### NCT01465659 — enroll 29, selected 2, sum 39, excess 10 — `POOLED_WITH_COMPONENTS`
`om[6]` `'Cohort 1/Cohort -1/Cohort -2 - Temozolomide and Pazopanib' = 29` is the all-dose-cohort
pool (its population description says "dose cohorts were combined"), equal to enrollment;
`om[1]` `'Phase II -Temozolomide 75 mg/m2 and Pazopanib 400 mg' = 10` is a component of it.
Again the pooled parent is unflagged by the vocabulary.
**Reducible: YES → {pooled 29} = 29 = enrollment.**

### NCT01491672 — enroll 134, selected 4, sum 268, excess 134 — `POOLED_WITH_COMPONENTS`
`om[3]` (SECONDARY, CBR, FAS): `'All Participants' = 134` (flagged pooled) with
`'Other Prior Vascular Endothelial Growth Factor (VEGF)' = 62`, `'Prior Sunitinib' = 58`,
`'Prior Cytokines' = 14`; 62+58+14 = 134 exactly.
**Reducible: YES → {62, 58, 14} = 134 = enrollment.**

### NCT01494506 — enroll 417, selected 4, sum 536, excess 119 — `COMPARISON_SET_REUSE`
`om[2]` (SECONDARY, ORR, ITT): `'MM-398 Arm A (Mono Therapy Comparison)' = 151`,
`'5-FU + Leucovorin (Arm B) (Mono Therapy Comparison)' = 149`,
`'MM-398 + 5-FU + Leucovorin(Arm C) Combo Therapy Comparison' = 117`, and
`'5-FU + Leucovorin (Combo Therapy Comparison)' = 119`. The control arm is entered **twice**, once
per pairwise comparison. 151 + 149 + 117 = 417 = registered enrollment exactly, which identifies the
119 as the comparison-specific re-use rather than a fourth arm.
**Reducible: YES → {151, 149, 117} = 417 = enrollment.**

### NCT01519414 — enroll 78, selected 3, sum 90, excess 12 — `CROSSOVER_OR_SWITCH`
`om[3]`: `'Arm I (Tivantinib)' = 52`, `'Arm II (Placebo)' = 26`, `'Crossover From Placebo to
Tivantinib' = 12`. Design is CROSSOVER; 52 + 26 = 78 = enrollment.
**Reducible: YES → {52, 26} = 78 = enrollment.**

### NCT01572038 — enroll 1436, selected 6, sum 3587, excess 2151 — `MULTI_AXIS_PARTITION`
The largest excess in this group, and it is entirely subgroup partitions of one single-arm
population. `om[45]` `'Pertuzumab + Trastuzumab + Taxane' = 1198` (measurable disease at baseline);
`om[47]` partitions the *same* 1198 by age (`'Age ≤65 Years' = 968` + `'Age >65 Years' = 230` =
1198); `om[48]` partitions it by taxane (`'Docetaxel' = 657` + `'Paclitaxel' = 481` +
`'Nab-Paclitaxel' = 53` = 1191, the residual being participants without a recorded taxane).
**Reducible: YES → {`Pertuzumab + Trastuzumab + Taxane` 1198} = 1198 ≤ 1436**, or equivalently
either single partition.

### NCT01577758 — enroll 41, selected 2, sum 42, excess 1 — `REGISTRY_INCONSISTENCY` (not overlap)
`om[3]` (SECONDARY, "Best Overall Response", response-evaluable population):
`'MLN0264 1.8 mg/kg (mCRC Expansion)' = 24`, `'MLN0264 Dose Escalation Phase' = 18`. These are
disjoint by construction (escalation vs expansion). The record's own escalation-phase dose cohorts
at `om[0]` sum to 19 and the expansion is 25 at `om[1]`, i.e. 44 participants — above the registered
41 independent of any selection.
**Reducible: the selected set is ALREADY non-overlapping ({24, 18}); the +1 is a registry /
analysis-set inconsistency, NOT double-counted patients.**

### NCT01595009 — enroll 246, selected 4, sum 261, excess 15 — `SEQUENTIAL_PHASE`
Core phase `om[7]`: `'pNET (Core)' = 126` + `'Non-pNET (Core)' = 120` = 246 = enrollment exactly.
Extension phase `om[12]` ("… During the Extension Phase (E1)", "all participants who received at
least one dose of everolimus **during the extension**"): `'GI NET' = 11`, `'Lung NET (E1)' = 4`.
The extension cohorts are re-measurements of participants already inside the core cohorts.
**Reducible: YES → {126, 120} = 246 = enrollment.**

### NCT01597388 — enroll 99, selected 9, sum 100, excess 1 — `DENOM_VARIES_BY_MEASURE` + `REGISTRY_INCONSISTENCY`
The nine selected cohorts are disjoint dose/schedule/food-effect groups. The excess comes from the
selection mixing denominators across outcome measures: `'170 mg BID Intermittent Days 1 and 2
(Fasted)'` is taken as 5 from `om[28]` while the same title is 8 at `om[0]`, and `'125 mg BID
Intermittent Days 1 and 2 (Fed)'` is taken as 8 from `om[31]` while it is 4 at `om[0]`. The `om[31]`
group set alone sums to 100 against a registered 99.
**Reducible: the selected set is ALREADY non-overlapping; the +1 is denominator variation across
outcome measures plus a 1-participant registry inconsistency, NOT overlap.**

### NCT01602315 — enroll 179, selected 10, sum 408, excess 229 — `POOLED_WITH_COMPONENTS` + `DUPLICATE_COHORT_IDENTITY` + `CROSSOVER_OR_SWITCH`
Two pooled labels for the same Phase II randomised population are both selected:
`om[8]` `'All Patients' = 106` and `om[10]` `'All Patients (Phase II)' = 106`, each sitting beside
its own components `'Arm 1 - BYL719+Cetuximab (Randomized)' = 71` and `'Arm 2 - Monotherapy
Cetuximab (Randomized)' = 35` (71+35 = 106). `om[15]` `'Arm 2B - BYL719+Cetuximab' = 16` is the
cross-over arm — the protocol arm list contains "Phase II: Cross over" and `om[16]` is titled
"… for the Cross-over".
**Reducible: PARTIAL → {Phase Ib `Arm A - 300mg` 16, `Arm A - 400mg` 5, `Arm B … Oral Suspension`
18, `Arm C … Dispersible Tablets` 6, `Arm 1` 71, `Arm 2` 35, `Arm 3` 29} = 180, one participant
above the registered 179.** The residual +1 is not resolvable from the record.

### NCT01615029 — enroll 45, selected 6, sum 58, excess 13 — `POOLED_WITH_COMPONENTS`
`om[0]` (PRIMARY, Phase 1 ORR): `'Phase 1: Daratumumab (2-16 mg/kg) + Lenalidomide and
Dexamethasone' = 13` is the pool of its own four dose components (`2 mg/kg` 3 + `4 mg/kg` 3 +
`8 mg/kg` 4 + `16 mg/kg` 3 = 13). `om[1]` `'Phase 2: 16 mg/kg …' = 32`. 13 + 32 = 45 = enrollment.
Pooled parent again not caught by the vocabulary.
**Reducible: YES → {Phase 1 pool 13, Phase 2 32} = 45 = enrollment** (equivalently the four dose
components + Phase 2).

### NCT01621490 — enroll 170, selected 22, sum 680, excess 510 — `MULTI_AXIS_PARTITION` + `POOLED_WITH_COMPONENTS`
Two incompatible partitions of one population are both selected. `om[6]` (SECONDARY, ORR) partitions
by regimen and brain-metastasis status into 7 groups: `'N3 60M Prog' = 44`, `'N3 60M Naive' = 41`,
`'N1 60M+I3 90M' = 27`, `'N1 30M + I3 30M Non-BM' = 25`, `'N3 30M Non-BM' = 11`,
`'N1 30M + I3 30M BM' = 10`, `'N3 30M BM' = 10` (= 168). `om[11]` (ORR by PD-L1 expression)
re-partitions the same participants by biopsy timing and adds nested pools —
`'Total' = 140` (flagged pooled), `'N3 60M, W4' = 75` (= `'N3 60M NAIVE, W4'` 39 +
`'N3 60M PROG, W4'` 36), `'N1 + I3 NON-BM' = 49`, and 12 more.
**Reducible: YES → the `om[6]` set of 7 = 168 ≤ 170.**

### NCT01655693 — enroll 397, selected 4, sum 660, excess 263 — `POOLED_WITH_COMPONENTS`
`om[2]` (SECONDARY, ORR, ITT). The population description states it outright: "The DT at 20 mg/m2
and 30 mg/m2 are **combined into DT pooled** experimental group for comparison with the BSC group."
Selected: `'Doxorubicin Transdrug Pooled' = 263`, `'Doxorubicin Transdrug (DT) at 20 mg/m2' = 130`,
`'Doxorubicin Transdrug at 30 mg/m2' = 133`, `'Best Standard of Care' = 134`; 130+133 = 263.
**Reducible: YES → {130, 133, 134} = 397 = enrollment exactly.**

### NCT01661270 — enroll 332, selected 2, sum 342, excess 10 — `DENOM_VARIES_BY_MEASURE` + `REGISTRY_INCONSISTENCY` (not overlap)
Two disjoint randomised arms. All three outcome measures declare the same ITT population, yet
`om[0]` (PFS) reports `'Aflibercept' = 223` while `om[1]` (OS) and `om[2]` (ORR, the selected one)
report `'Aflibercept' = 233`; `'Placebo' = 109` throughout. 223 + 109 = 332 = registered enrollment
exactly, so the selection of the larger denominator (step **e**) is the whole of the excess.
**Reducible: the selected set is ALREADY non-overlapping; the enrollment-consistent denominators are
{223, 109}. NOT an overlap finding.**

### NCT01677741 — enroll 85, selected 10, sum 184, excess 99 — `POOLED_WITH_COMPONENTS` + `NESTED_SUBSET`
Tumour-type-specific outcome measures each contain a pool, a nested restriction of that pool, and
the pool's components. `om[11]` (LGG): `'All LGG Subjects' = 33`, `'All LGG Subjects at Recommended
Phase 2 Dose (RP2D)' = 24` (nested), plus components `Part 1 3.75 mg/kg` 4 + `4.5 mg/kg` 6 +
`5.25 mg/kg` 6 + `Part 2 Cohort 1 LGG` 17 = 33. `om[12]` (HGG): `'All HGG Subjects' = 35`,
`'All HGG Subjects at Recommended Phase 2 Dose (RP2D)' = 28`, components `3 mg/kg` 3 +
`3.75 mg/kg` 4 + `Part 2 Cohort 2 HGG` 28 = 35.
**Reducible: YES → {`All LGG Subjects` 33, `All HGG Subjects` 35} = 68 ≤ 85.**

### NCT01677858 — enroll 116, selected 6, sum 220, excess 104 — `POOLED_WITH_COMPONENTS`
`om[1]` (PRIMARY, ORR): `'Phase 1+2: Carfilzomib 70 mg/m²' = 104` is the pool of
`'Phase 1: Carfilzomib 70 mg/m²' = 15` and `'Phase 2: Carfilzomib 70 mg/m²' = 89` (15+89 = 104),
sitting beside them and beside `'Phase 1: Carfilzomib 45 mg/m²' = 3`, `'56 mg/m²' = 3`,
`'88 mg/m²' = 6`.
**Reducible: YES → {3, 3, 15, 6, 89} = 116 = enrollment exactly.**

### NCT01693562 — enroll 1022, selected 9, sum 1060, excess 38 — `NESTED_SUBSET` + `POOLED_WITH_COMPONENTS`
A large basket study whose expansion cohorts are reported at several nesting depths.
`om[11]` `'Expansion NSCLC Cohort (MEDI4736 10 mg/kg Q2W)' = 275` and `'Expansion SCCHN Cohort …'
= 55`; the NSCLC cohort is then re-cut by histology and prior-line in `om[5]`
(`'Expansion Non-squamous NSCLC 3L+ Cohort' = 68`) and `om[6]`
(`'Expansion Squamous NSCLC 2L+ Cohort' = 117`, `'Expansion Squamous NSCLC 3L+ Cohort' = 62` —
themselves nested, 3L+ inside 2L+). `om[21]` `'Expansion UC Total Cohort' = 199` sits beside
`'Expansion UC PD-L1 High Cohort' = 101` and `'… Low/Negative Cohort' = 85`; `om[7]`
`'Expansion UC PD-L1 High 2L+ Cohort' = 98` is nested inside the 101.
**Reducible: YES → {NSCLC 275, SCCHN 55, UC Total 199} = 529 ≤ 1022.**

### NCT01696032 — enroll 120, selected 5, sum 147, excess 27 — `CROSSOVER_OR_SWITCH`
`om[2]` (SECONDARY, ORR): `'Stage 1: Guadecitabine+Carboplatin 30 mg/m2' = 14`,
`'Stage 1: … 45 mg/m2' = 6`, `'Stage 2: Guadecitabine+Carboplatin 30 mg/m2' = 51`,
`'Stage 2: Treatment Choice' = 49`, `'Stage 2: Crossover Treatment Choice to
Guadecitabine+Carboplatin 30 mg/m2' = 27`. 14+6+51+49 = 120 = enrollment exactly; the crossover 27
are Treatment Choice participants re-counted.
**Reducible: YES → {14, 6, 51, 49} = 120 = enrollment.**

### NCT01698918 — enroll 202, selected 3, sum 454, excess 252 — `DUPLICATE_COHORT_IDENTITY` + `SEQUENTIAL_PHASE`
The clearest key-normalisation artefact in this group. `om[1]` titles the group
`'Everolimus+Letrozole (First Line Treatment)' = 202`; `om[2]` titles the *same* cohort
`'Everolimus+Letrozole (First-line Treatment)' = 202`. The two strings differ only by a hyphen,
which NFKC + casefold + whitespace collapse + outer-punctuation strip does not remove, so one cohort
enters twice. `om[4]` `'Everolimus+Exemestane (Second-line Treatment)' = 50` is the subset who went
on to second-line treatment ("all participants in the FAS who received at least one dose of
second-line study medication"); `om[6]` confirms one population with a single group
`'Everolimus+Letrozole/Exemestane (First-line Treatment and Second-line Treatment)' = 202`.
**Reducible: YES → {`Everolimus+Letrozole (First-line Treatment)` 202} = 202 = enrollment.**

### NCT01704287 — enroll 540, selected 5, sum 638, excess 98 — `CROSSOVER_OR_SWITCH`
`om[5]` ("BOR — **Initial Treatment Period**", all randomized): `'Pembrolizumab 10 mg/kg' = 181`,
`'Pembrolizumab 2 mg/kg' = 180`, `'Investigator-Choice Chemotherapy (ICC)' = 179`; sum 540 =
enrollment exactly. `om[6]` ("BOR — **Switch-to-Pembrolizumab** Treatment Period", "all randomized
participants in ICC who switched to receiving pembrolizumab"): `'ICC→Pembrolizumab 2 mg/kg' = 53`,
`'ICC→Pembrolizumab 10 mg/kg' = 45` — 98, exactly the excess, all of them ICC participants.
**Reducible: YES → {181, 180, 179} = 540 = enrollment.**

### NCT01708161 — enroll 47, selected 7, sum 115, excess 68 — `POOLED_WITH_COMPONENTS` + `DUPLICATE_COHORT_IDENTITY` + `REGISTRY_INCONSISTENCY`
Two pooled labels for the same Phase II FAS are both selected and both flagged pooled:
`om[1]` `'All Patients - Phase' = 23` (a truncated title) and `om[4]` `'All Patients - Phase II' =
23`, each beside components `'HR+BC - Phase II' = 16` and `'Ovarian - Phase II' = 6`. Separately,
`'BYL 300mg + AMG 12mg/kg'` is selected at **33** from `om[3]` although the same group title carries
**10** in the eight other outcome measures that report it (`om[2]`, `om[5]`–`om[10]`) — an
apparent record error, not a population difference.
**Reducible: PARTIAL.** Using the selected denominators the reduced set
{`BYL 200mg` 4, `BYL 300mg` 33, `BYL 350mg` 10, `HR+BC` 16, `Ovarian` 6} = 69, still above 47.
Using the value that `BYL 300mg` carries everywhere else (10) the same set = 46 ≤ 47, and
Phase Ib (4+10+10 = 24) + Phase II (23) = 47 = enrollment exactly. The record does not say which of
33 and 10 is correct, so the reduction is PARTIAL and the anomalous denominator is flagged.

### NCT01816594 — enroll 50, selected 6, sum 100, excess 50 — `MULTI_AXIS_PARTITION`
`om[3]` (all participants): `'Trastuzumab + BKM120 + Paclitaxel' = 25`,
`'Trastuzumab + BKM120 PBO + Paclitaxel' = 25` (= 50 = enrollment). `om[12]`/`om[13]` re-cut the
identical randomised population by hormone-receptor status: `'… (ER+)' = 16` / `'… PBO … (ER+)' =
15`, `'… (ER-)' = 9` / `'… PBO … (ER-)' = 10`. All four outcome measures declare the same
"Intent-to-treat set (ITT)/full analysis set (FAS) (pooled)".
**Reducible: YES → either axis; the finer non-overlapping set is the four ER cells
{16, 15, 9, 10} = 50 = enrollment.**

### NCT01852292 — enroll 157, selected 2, sum 158, excess 1 — `REGISTRY_INCONSISTENCY` (not overlap)
`om[2]` (SECONDARY, ORR, FAS = "all patients who were randomized"): `'Buparlisib + Paclitaxel' = 79`
and `'Buparlisib Matching Placebo + Paclitaxel' = 79`. Two disjoint randomised arms; the FAS totals
158 against a registered enrollment of 157, in every one of the eight outcome measures that report
both arms.
**Reducible: the selected set is ALREADY non-overlapping; the +1 is a registry inconsistency,
NOT overlap.**

### NCT01900652 — enroll 111, selected 4, sum 163, excess 52 — `NESTED_SUBSET`
`om[0]` (PRIMARY, ORR) carries both the randomised arms and their biomarker-defined subsets:
`'Arm A: Emibetuzumab Plus Erlotinib' = 66` with `'MET-High Analysis Population (Emibetuzumab +
Erlotinib)' = 53`, and `'Arm B: Emibetuzumab' = 23` with `'MET-High Analysis Population
(Emibetuzumab)' = 21`. `om[7]`/`om[8]` show the same nesting at larger denominators
(83 / 28 / MET-High 74).
**Reducible: YES → {`Arm A` 66, `Arm B` 23} = 89 ≤ 111.**

### NCT01909453 — enroll 921, selected 6, sum 1201, excess 280 — `POOLED_WITH_COMPONENTS`
`om[19]` (SECONDARY, "Part 1 and Part 2: ORR", FAS). The population description states the pooling:
"It was planned to report **combined result data of Part 1 and Part 2** for LGX818 300 mg arm."
Selected: `'Part 1 + Part 2: LGX818 300 mg' = 280` alongside `'Part 1: LGX818 300 mg' = 194` and
`'Part 2: LGX818 300 mg' = 86` (194+86 = 280), plus `'Part 1:LGX818 450 mg QD+MEK162 45 mg BID
(Combo 450)' = 192`, `'Part 1: Vemurafenib 960 mg BID' = 191`, `'Part 2: LGX818 300 mg QD+MEK162
45 mg BID (Combo 300)' = 258`.
**Reducible: YES → {194, 86, 192, 191, 258} = 921 = enrollment exactly.**

### NCT01915498 — enroll 345, selected 15, sum 558, excess 213 — `POOLED_WITH_COMPONENTS`
`om[8]` ("Combined Phase 1/2 … in Participants With R/R AML") contributes
`'Enasidenib 100 mg QD' = 214`, a cross-phase pool. The other 14 selected cohorts are the disjoint
building blocks: `om[6]` nine Phase 1 escalation dose groups (29+22+14+13+9+7+7+7+5 = 113),
`om[7]` four Phase 1 expansion arms (49+27+25+25 = 126), `om[3]` `'Phase 2: Enasidenib 100 mg QD' =
105`.
**Reducible: YES → those 14 = 344 ≤ 345** (dropping the 214 pool).

### NCT01928394 — enroll 1163, selected 25, sum 1533, excess 370 — `POOLED_WITH_COMPONENTS`
A single outcome measure `om[0]` (PRIMARY, ORR, "All Treated Participants") contains two pooled
groups beside their own components: `'SCLC Arm N- All Treated' = 245` = `'SCLC Arm N -
Pre-expansion' 98` + `'SCLC Arm N Expansion' 147`, and `'SCLC Arm N-I Dose Level 2 - All
Treated' = 157` = `'… Dose Level 2 - Pre-expansion' 61` + `'… Dose Level 2- Expansion' 96`.
Neither pooled title matches Job 2's pooled vocabulary.
**Reducible: YES → the other 23 cohorts = 1131 ≤ 1163.**

### NCT01981850 — enroll 125, selected 11, sum 151, excess 26 — `DUPLICATE_COHORT_IDENTITY`
`om[0]` reports four Stage-1 main-phase cohorts (8 + 7 + 6 + 6 = 27); `om[2]` reports the **same
four cohorts re-titled with their open-label-extension assignment appended** —
`'Main Phase Stage 1: RO7490677 10 mg/kg IV QW; OLE: RO7490677 10 mg/kg IV Q4W' = 8`, etc., with
identical denominators 8/7/6/6. The title key therefore doubles them. `om[1]` adds the three
disjoint Stage-2 cohorts (33 + 32 + 32 = 97).
**Reducible: YES → {four Stage-1 cohorts 27, three Stage-2 cohorts 97} = 124 ≤ 125.**

### NCT01993719 — enroll 33, selected 4, sum 37, excess 4 — `SEQUENTIAL_PHASE` + `REGISTRY_INCONSISTENCY` — **UNRESOLVED**
`om[2]` (PRIMARY, ORR): `'Arm 1P …' = 16`, `'Arm 2/Foll By Arm 1P …' = 12`, `'Arm 1N …' = 7`,
`'Arm 1P/Foll By Arm-1P/R …' = 2`. The "Foll By" labels are retreatment arms — participants who
received one regimen and then another — and `om[6]`/`om[7]` give a single combined group
`'All Participants in Arms 1N, 1P, Arm 2/Foll By Arm 1P, Arm 2, and Arm 1P/Foll By Arm 1P/R' = 32`,
i.e. 32 distinct treated participants against a registered 33. `om[8]` splits the same population
differently again (1N 7, 1P 11, 1P/Foll 2, Arm 2 9, Arm 2/Foll 3 = 32), which is not reconcilable
group-for-group with `om[2]`'s four groups.
**Reducible: UNRESOLVED.** The record establishes that only 32 distinct participants were treated
and that the retreatment arms re-count participants, but it does not license a specific
non-overlapping subset of the four *selected* cohorts.

### NCT02020577 — enroll 58, selected 3, sum 116, excess 58 — `POOLED_WITH_COMPONENTS`
`om[5]` (SECONDARY, "Best Overall Response", treated set): `'All Patients' = 58` (flagged pooled)
beside `'Afatinib 40mg+Cetuximab 250 mg/m²' = 55` and `'Afatinib 30mg+Cetuximab 250 mg/m²' = 3`;
55 + 3 = 58 = enrollment.
**Reducible: YES → {55, 3} = 58 = enrollment.**

### NCT02027428 — enroll 427, selected 3, sum 622, excess 195 — `POOLED_WITH_COMPONENTS` + `SEQUENTIAL_PHASE`
`om[6]` carries `'All Participants - Induction' = 420` (flagged pooled) alongside the two
maintenance-randomised groups `'Nab-Paclitaxel + BSC: Induction + Maintenance' = 136` and
`'BSC: Induction + Maintenance' = 66` (selected from `om[2]`). The population descriptions make the
nesting explicit: "Induction includes the ITT population of participants treated during Induction.
Entire Study includes the entire experience of the ITT population of participants **randomized to
maintenance**." The 202 maintenance participants are a subset of the 420 induction participants.
**Reducible: YES → {`All Participants - Induction` 420} = 420 ≤ 427.**

### NCT02031458 — enroll 667, selected 4, sum 1179, excess 512 — `POOLED_WITH_COMPONENTS`
`om[0]` (PRIMARY, ORR by IRF): `'Cohorts 2 + 3' = 520` is the pool of `'Cohort 2: Second Line
Atezolizumab' = 267` and `'Cohort 3: Third Line and Beyond Atezolizumab' = 253` (267+253 = 520),
selected beside them and beside `'Cohort 1: First Line Atezolizumab' = 139`. The pooled title is not
in the vocabulary.
**Reducible: YES → {139, 267, 253} = 659 ≤ 667.**

### NCT02047344 — enroll 31, selected 5, sum 52, excess 21 — `MULTI_AXIS_PARTITION`
`om[4]` `'Antroquinonol (Hocena)' = 26` is the whole full-analysis group; `om[2]` partitions the
same 26 by prior chemotherapy lines: `'More Than Two Lines Failed Prior Chemotherapies' = 11`,
`'Two Lines Failed Prior Chemotherapies' = 7`, `'Non- Prior Chemotherapies' = 5`,
`'One Line Failed Prior Chemotherapies' = 3` (11+7+5+3 = 26). `om[2]`'s population description
says "26 patients can be run the full analysis".
**Reducible: YES → {`Antroquinonol (Hocena)` 26} = 26 ≤ 31**, or equivalently the four line strata.

### NCT02048371 — enroll 131, selected 9, sum 157, excess 26 — `CROSSOVER_OR_SWITCH`
`om[3]` ("ORR. All Cohorts.") gives seven disease cohorts: `'Cohort A: Liposarcoma' = 24`,
`'Cohort A: Liposarcoma, Placebo' = 24`, `'Cohort B: Osteosarcoma' = 22`, `'Cohort B: Osteosarcoma,
Placebo' = 20`, `'Cohort C: Ewing Sarcoma' = 30`, `'Cohort D: Rhabdomyosarcoma' = 10`,
`'Cohort E: Mesenchymal Chondrosarcoma' = 1` — sum 131 = enrollment exactly. `om[5]` ("Response
Rate (RR), Cohorts A and B, **After Crossover**", population "Participants who started on placebo
then crossed over to active drug") adds `'Cohort A: Liposarcoma Crossover' = 15` and
`'Cohort B: Osteosarcoma Crossover' = 11` — 26, exactly the excess.
**Reducible: YES → the seven `om[3]` cohorts = 131 = enrollment.**

### NCT02150967 — enroll 143, selected 2, sum 216, excess 73 — `DUPLICATE_COHORT_IDENTITY`
One cohort, two titles, same denominator: `om[0]` (PRIMARY, ORR by BICR, "FAS, defined as all
subjects in Cohort 1 who had received at least one dose of infigratinib")
`'Cohort 1: FGFR2 Fusions' = 108`; `om[3]` (SECONDARY, DCR, *identical* population description)
`'Cohort 1: FGFR2 Fusion/Rearrangements' = 108`. The record contains no second cohort of 108.
**Reducible: YES → one of the two, 108 ≤ 143.**

### NCT02159066 — enroll 158, selected 6, sum 216, excess 58 — `SEQUENTIAL_PHASE` — **PARTIAL**
`om[24]` (Part I FAS): `'Part I: Encorafenib + Binimetinib (Non-naive)' = 83` and `'… (Naive)' =
75`; 83 + 75 = 158 = registered enrollment exactly. `om[0]` (Part II FAS, "all participants who
received at least 1 dose … **following the assignment of the triple combination treatment**") adds
`'Part II: Encorafenib + Binimetinib + Ribociclib' = 38`, `'… + Capmatinib' = 13`,
`'… + Buparlisib' = 6`, `'… + Infigratinib' = 1` — 58, exactly the excess.
**Reducible: PARTIAL → {83, 75} = 158 = enrollment.** The arithmetic identity and the "following
the assignment of" wording both point to Part II participants having come from Part I, but neither
the arm descriptions (which are empty) nor any group description states it. Flagged rather than
asserted.

### NCT02185690 — enroll 13, selected 4, sum 24, excess 11 — `MULTI_AXIS_PARTITION`
`om[1]` `'Binimetinib Dose Level 1 (30mg BID)' = 6` + `'Binimetinib Dose Level 2 (45mg BID)' = 6`;
`om[2]` re-cuts the same participants by genotype: `'KRAS/NRAS-mutated Patients' = 7` +
`'KRAS/NRAS Wild-type Patients' = 5`. `om[2]`'s population description states it: "**Dose levels are
combined** as mutation information was obtained for the 12 patients in total and segregated in the
results by these 2 groups only." `om[0]` confirms a single combined group of 12.
**Reducible: YES → either partition, 12 ≤ 13.**

### NCT02202746 — enroll 178, selected 3, sum 346, excess 168 — `POOLED_WITH_COMPONENTS`
`om[1]` (SECONDARY, ORR, efficacy population): `'All Patients' = 173` (flagged pooled) beside
`'Lucitanib (CO-3810) 10 mg QD' = 106` and `'Lucitanib (CO-3810) 15 mg QD' = 67`; 106 + 67 = 173.
**Reducible: YES → {106, 67} = 173 ≤ 178.**

### NCT02228096 — enroll 75, selected 3, sum 104, excess 29 — `DUPLICATE_COHORT_IDENTITY` + `NESTED_SUBSET`
One infused population reported under assessor-labelled titles that are then reused for a subgroup.
`om[0]` (PRIMARY, ORR per IRC, EAS) `'Tisagenlecleucel (CTL019) - All Participants' = 64`.
`om[15]` ("ORR by Baseline Extramedullary Disease Presence of **No**") keeps the title
`'Tisagenlecleucel (CTL019) - IRC Assessment'` but restricts the denominator to **40**, while the
same title carries 64 at `om[2]`, `om[4]`, `om[5]`, `om[7]`, `om[9]`. `om[1]`
`'Tisagenlecleucel (CTL019) - Local Assessment' = 0` — the record states "No patients with
Lymphoblastic Lymphoma were enrolled in this trial, hence there is no data to report."
Note for the parent: the selected denominator for the `IRC Assessment` cohort (40) is **not** the
largest one carrying that title in this record (64), so the priority ladder resolved this cohort
before step **e**.
**Reducible: YES → {`Tisagenlecleucel (CTL019) - All Participants` 64} = 64 ≤ 75.**

### NCT02296125 — enroll 674, selected 4, sum 692, excess 18 — `PARTIAL_POPULATION_OVERLAP` — **UNRESOLVED**
`om[4]` (SECONDARY, DCR): `'Osimertinib 80 mg (Global Cohort)' = 279`, `'SoC EGFR-TKI (Global
Cohort)' = 277`, `'Osimertinib 80 mg (China Cohort)' = 71`, `'SoC EGFR-TKI (China Cohort)' = 65`.
The population description states the overlap explicitly: "FAS included all randomized participants
prior to the end of global recruitment. The **China-only FAS included all China participants
randomized in mainland-China as part of the global study** and all additional China participants
recruited in mainland China after global recruitment was completed." The China cohorts therefore
partially, not wholly, overlap the Global cohorts; 692 − 674 = 18 is the size of the shared part.
**Reducible: UNRESOLVED.** No whole cohort can be dropped — the Global set (556) plus the
China-only additional participants would be the non-overlapping construction, but the record does
not report the China-only additional participants as a cohort, nor the per-arm split of the 18.

---

## Files

- `LEAF-OUT/LEAF-QB-group1.md` — this file.
- `LEAF-OUT/LEAF-QB-group1.tsv` — 45 `TRIAL` rows + 280 `COHORT` rows. `TRIAL` rows carry the
  mechanism, reducibility and non-overlapping-set size; `COHORT` rows carry
  `om_index`, `group_title`, `denominator`, `pooled_flag`, `outcome_measure_title`, `time_frame`
  and `cohort_role` (`KEEP` / `DROP:<reason>` / `UNRESOLVED`), plus the payload file, so every
  number here can be re-derived from the cache.

## What this leaf does NOT claim

Nothing about unique patients across trials — that is global and belongs to the parent.
Nothing about Job 2's global excess of 22,578 participant-slots across 180 trials; that figure is
context and remains Job 2's finding. No change is made to the selection rule. No claim of any kind
about efficacy, safety, selectivity, therapeutic window or clinical readiness.
