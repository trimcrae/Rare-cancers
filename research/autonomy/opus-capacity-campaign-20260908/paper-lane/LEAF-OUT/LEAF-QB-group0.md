# LEAF-QB-group0 — why selected cohort denominators exceed registered enrollment, 45 assigned trials

Leaf worker output, wave of 2026-09-08. Question B, group 0. Read-only work against the frozen cache;
no network request, no producer, no gate, no tracked-file edit.

## Provenance and coverage

- Cache: `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5/`,
  branch `literature-cache` @ `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`.
- `sha256sum -c SHA256-MANIFEST.txt` → all 13 files `OK`, **exit code 0**.
- Trials assigned: **45** (`LEAF-ASSIGNMENTS/QB-group0.txt`). Trials reached in the cache: **45/45**. None missing.
- Selected cohorts covered: **202**, summing to **16,113** participant-slots against **8,318** registered
  participants, i.e. **5,160 excess slots** in this group. (Job 2's global 180-trial / 22,578-slot figures are
  context only; the numbers here are my group's own subtotal, re-derived from
  `CURATION-endpoint-identity-and-overlap-artifacts/OVERLAP-enrollment-check.tsv`.)
- Every trial record was taken from the R0-canonical copy (most populated field set) as located in the payloads
  named per cohort row in the TSV. Pointers are `payload / NCT / outcome-measure index / results-group id`,
  where the outcome-measure index is the 0-based position in
  `resultsSection.outcomeMeasuresModule.outcomeMeasures` of that record, matching the `om` column Job 2 used.

## Enrollment type — answer to item 4, up front

**All 45 assigned trials record `enrollmentInfo.type == "ACTUAL"`. Not one is `ESTIMATED`.**
So the "estimated enrollment below a reported denominator" case does not arise anywhere in this group, and
nothing in this file needs to be separated out on that ground. The excesses below are all measured against a
registry field the sponsor marked as an actual count.

## Mechanism taxonomy used

Job 2 named five candidate mechanisms. Two of them (pooled-plus-components, cross-axis partitions) carry most of
this group; one (ESTIMATED enrollment) is empty here; per-measure denominators drawn at different timepoints was
**not** the driver in any of my 45 (where two outcome measures disagree, they disagree by population or by
reader, not by timepoint). Four mechanisms the record forced me to add are marked NEW.

| code | mechanism | trials (primary or contributing) | excess attributed to trials where it is primary |
|---|---|---|---|
| `M1_POOLED_PLUS_COMPONENTS` | An explicit `Total`/pooled results group is summed alongside its own components. | 20 | 2,068 |
| `M2_CROSS_AXIS_PARTITION` | Two outcome measures partition the same patients on different axes (factorial arms; phase vs prior therapy). | 2 | 1,308 |
| `M3_TITLE_VARIANT_DUPLICATE` | **NEW.** One cohort appears under two title spellings (comma, space, typo, or an added drug name), so the title-keyed identity rule counts it twice. | 8 | 283 |
| `M4_ASSESSOR_DUPLICATE` | **NEW.** One population reported once per reader — investigator vs independent/central review — as two results groups. | 2 | 415 |
| `M5_SEQUENTIAL_REENTRY` | **NEW (a species of overlap).** Crossover, extension or optional-rollover cohorts re-count patients already counted in a randomised-phase cohort. | 6 | 355 |
| `M6_REGISTRY_INCONSISTENCY` | Disjoint results groups whose sum still exceeds the registered ACTUAL enrollment. A genuine registry inconsistency. | 5 | 19 |
| `M7_NON_COHORT_GROUPS` | **NEW.** Results groups that are not patient cohorts at all — RECIST response categories, or named individual responders in a duration-of-response measure. | 2 | 32 |
| `M8_ANALYSIS_POPULATION_NESTING` | **NEW.** Nested analysis populations (ITT ⊃ PP; MITT ⊃ refractory / prior-therapy subsets; total ⊃ stage-1). | 5 | 474 |
| `M9_SEQUENTIAL_PARTS_RELATION_UNSTATED` | **NEW.** Sequential trial parts whose relation the record never states — cannot be classified as overlap or as inconsistency. | 1 | 206 |

Reducibility verdicts across the 45: **38 YES** (a non-overlapping set is derivable from the record alone),
**5 NO** (disjoint cohorts already exceed enrollment — a registry inconsistency, not an overlap),
**2 UNRESOLVED** (NCT00700258, NCT01085136).

## Per-trial findings

Ordered by excess, largest first. `OMk/OGnnn` = outcome-measure index k, results-group id OGnnn, in the record
shown in the `payload` column of the matching TSV rows.

### NCT00069095 — excess 1,269 (4 cohorts, sum 3,304 vs enrollment 2,035 ACTUAL)

- **Mechanism:** `M2_CROSS_AXIS_PARTITION`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM10/OG000 FOLFOX-4/FOLFOX-4+P/FOLFOX-4+BV 937; OM10/OG001 XELOX/XELOX+P/XELOX+BV 967} = 1904
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** 2x2 factorial design (`designInfo.interventionModel == "FACTORIAL"`). OM10 partitions the trial on the chemotherapy-backbone axis; OM11 partitions the SAME patients on the bevacizumab-vs-placebo axis (2x2 part only). Either axis alone is internally disjoint; summing both double-counts the 1,400 factorial-part patients.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM10/OG000 — "FOLFOX-4/FOLFOX-4+P/FOLFOX-4+BV" — denom **937** — `AXIS1_KEEP`
  - OM10/OG001 — "XELOX/XELOX+P/XELOX+BV" — denom **967** — `AXIS1_KEEP`
  - OM11/OG000 — "FOLFOX-4+P/XELOX+P" — denom **701** — `AXIS2_CROSS_AXIS`
  - OM11/OG001 — "FOLFOX-4+BV/XELOX+BV" — denom **699** — `AXIS2_CROSS_AXIS`

### NCT00806156 — excess 431 (6 cohorts, sum 609 vs enrollment 178 ACTUAL)

- **Mechanism:** `M8_ANALYSIS_POPULATION_NESTING`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM1/OG002 MITT Population 169} = 169 (registered enrollment 178)
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Every other selected cohort is a subset of the MITT population: the q14d arm (37), the q21d arm (104, which OM0 additionally restates under the second title "Primary Efficacy Population" with the same 104), the Platinum-Refractory Population (65, "Patients in the MITT Population with a PFI <= 6 weeks") and the Prior PLD Population (130, "Patients in the MITT Population..."). The record explicitly nests them.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM0/OG000 — "NKTR-102 q21d" — denom **104** — `NESTED_SUBSET`
  - OM0/OG001 — "Primary Efficacy Population" — denom **104** — `NESTED_SUBSET`
  - OM1/OG000 — "NKTR-102 q14d" — denom **37** — `NESTED_SUBSET`
  - OM1/OG002 — "MITT Population" — denom **169** — `KEEP_ITT`
  - OM3/OG002 — "Platinum-Refractory Population" — denom **65** — `NESTED_SUBSET`
  - OM4/OG002 — "Prior PLD Population" — denom **130** — `NESTED_SUBSET`

### NCT01024231 — excess 307 (11 cohorts, sum 434 vs enrollment 127 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM7/OG000 Cohort 1 14; OG001 Cohort 2 17; OG002 Cohort 2a 16; OG003 Cohort 3 6; OG005 Cohort 6 17; OG006 Cohorot 7 16; OG008 Cohort 8 41} = 127 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Nested pooling at three levels in ONE outcome measure: OG004 "Any BMS and Ipi Combo" 53 (= cohorts 1,2,2a,3), OG007 "Only BMS" 33 (= cohorts 6,7), OG009 "Any BMS/Ipi" 94 (= 53 + cohort 8), OG010 "Total" 127 (= all). The descriptions state each pooling explicitly.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM7/OG000 — "Cohort 1" — denom **14** — `COMPONENT`
  - OM7/OG001 — "Cohort 2" — denom **17** — `COMPONENT`
  - OM7/OG002 — "Cohort 2a" — denom **16** — `COMPONENT`
  - OM7/OG003 — "Cohort 3" — denom **6** — `COMPONENT`
  - OM7/OG004 — "Any BMS and Ipi Combo" — denom **53** — `POOLED_TOTAL`
  - OM7/OG005 — "Cohort 6" — denom **17** — `COMPONENT`
  - OM7/OG006 — "Cohorot 7" — denom **16** — `COMPONENT`
  - OM7/OG007 — "Only BMS" — denom **33** — `POOLED_TOTAL`
  - OM7/OG008 — "Cohort 8" — denom **41** — `COMPONENT`
  - OM7/OG009 — "Any BMS/Ipi" — denom **94** — `POOLED_TOTAL`
  - OM7/OG010 — "Total" — denom **127** — `POOLED_TOTAL`

### NCT01078662 — excess 298 (6 cohorts, sum 596 vs enrollment 298 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM0/OG000 Breast 62; OG001 Ovarian 193; OG002 Pancreatic 23; OG003 Prostate 8; OG004 Other 12} = 298 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM0/OG005 "All Patients" 298 is the pooled group; the five tumour-site cohorts partition it exactly.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM0/OG000 — "Breast Cancer" — denom **62** — `COMPONENT`
  - OM0/OG001 — "Ovarian Cancer" — denom **193** — `COMPONENT`
  - OM0/OG002 — "Pancreatic Cancer" — denom **23** — `COMPONENT`
  - OM0/OG003 — "Prostate Cancer" — denom **8** — `COMPONENT`
  - OM0/OG004 — "Other Cancers" — denom **12** — `COMPONENT`
  - OM0/OG005 — "All Patients" — denom **298** — `POOLED_TOTAL`

### NCT00502307 — excess 272 (2 cohorts, sum 544 vs enrollment 272 ACTUAL)

- **Mechanism:** `M4_ASSESSOR_DUPLICATE`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM1/OG000 Investigator Assessment 272} = 272 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM1 reports one all-treated population of 272 TWICE - once read by the investigator, once by the independent radiology reviewer. The two results groups are readers, not patient groups.
- **Cohorts driving it** (payload `ctg_placebo_onc_1999_2009`):
  - OM1/OG000 — "Investigator Assessment" — denom **272** — `KEEP_ITT`
  - OM1/OG001 — "Independent Radiology Reviewer Assessment" — denom **272** — `DUPLICATE_ASSESSOR`

### NCT00290771 — excess 231 (3 cohorts, sum 462 vs enrollment 231 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM0/OG000 131; OM0/OG001 100} = 231
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM0/OG002 "All Patients - Imatinib 600 or 1000 mg + Hydroxyurea 1000 mg" is the explicit pooled group (231 = 131+100 = registered enrollment).
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM0/OG000 — "Imatinib 600 mg + Hydroxyurea 1000 mg" — denom **131** — `COMPONENT`
  - OM0/OG001 — "Imatinib 1000 mg + Hydroxyurea 1000 mg" — denom **100** — `COMPONENT`
  - OM0/OG002 — "All Patients - Imatinib 600 or 1000 mg + Hydroxyurea 1000 mg" — denom **231** — `POOLED_TOTAL`

### NCT01085136 — excess 206 (3 cohorts, sum 1,360 vs enrollment 1,154 ACTUAL)

- **Mechanism:** `M9_SEQUENTIAL_PARTS_RELATION_UNSTATED`
- **Reducible to a non-overlapping set from the record alone:** **UNRESOLVED**
- **Reduced set:** UNRESOLVED — cannot be settled from this record
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Registered ACTUAL enrollment 1154 equals the Part A denominator exactly (OM3/OG000 "Afatinib Monotherapy (Part A)" 1154), while OM4 adds Part B cohorts of 138 and 68. The cached record (protocol arms, design and outcome-measures modules) never states whether Part B participants were drawn from Part A or enrolled separately, and no participant-flow module is present in this cache. Both readings - a nested re-randomisation of Part A progressors, or a registry enrollment field covering Part A only - fit the record equally. UNRESOLVED.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM3/OG000 — "Afatinib Monotherapy (Part A)" — denom **1154** — `UNRESOLVED_PART`
  - OM4/OG000 — "Afatinib Plus Paclitaxel (Part B)" — denom **138** — `UNRESOLVED_PART`
  - OM4/OG001 — "Investigators Choice of Chemotherapy (Part B)" — denom **68** — `UNRESOLVED_PART`

### NCT00804856 — excess 170 (18 cohorts, sum 350 vs enrollment 180 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** the thirteen Phase I dose groups (OM3/OG000-OG005 = 32, OM3/OG007-OG013 = 56) plus the two Phase II arms (OM1/OG000 45, OM1/OG001 42 = 87) = 175
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Three explicit pooled groups are summed alongside their own components: OM3/OG006 "Total Phase I Combined. Schedule A." 32, OM3/OG014 "Total Phase I Combined. Schedule B." 56, OM3/OG017 "Total Phase II Combined. Schedule A and C." 87. Selected sum 350 is exactly twice the reduced 175.
- **Cohorts driving it** (payload `ctg_accrual_completed_onc_phase2|ctg_results_bor_1999_2009`):
  - OM1/OG000 — "Phase II Schedule C. LDAC" — denom **45** — `COMPONENT`
  - OM1/OG001 — "Phase II Schedule A. Volasertib 350 mg+LDAC" — denom **42** — `COMPONENT`
  - OM3/OG000 — "Phase I Schedule A. Volasertib 150 mg+LDAC" — denom **4** — `COMPONENT`
  - OM3/OG001 — "Phase I Schedule A. Volasertib 200 mg+LDAC" — denom **3** — `COMPONENT`
  - OM3/OG002 — "Phase I Schedule A. Volasertib 250 mg+LDAC" — denom **5** — `COMPONENT`
  - OM3/OG003 — "Phase I Schedule A. Volasertib 300 mg+LDAC" — denom **9** — `COMPONENT`
  - OM3/OG004 — "Phase I Schedule A. Volasertib 350 mg+LDAC" — denom **8** — `COMPONENT`
  - OM3/OG005 — "Phase I Schedule A. Volasertib 400 mg+LDAC" — denom **3** — `COMPONENT`
  - OM3/OG006 — "Total Phase I Combined. Schedule A." — denom **32** — `POOLED_TOTAL`
  - OM3/OG007 — "Phase I Schedule B. Volasertib 150 mg" — denom **11** — `COMPONENT`
  - OM3/OG008 — "Phase I Schedule B. Volasertib 200 mg" — denom **2** — `COMPONENT`
  - OM3/OG009 — "Phase I Schedule B. Volasertib 350 mg" — denom **5** — `COMPONENT`
  - OM3/OG010 — "Phase I Schedule B. Volasertib 400 mg" — denom **6** — `COMPONENT`
  - OM3/OG011 — "Phase I Schedule B. Volasertib 450 mg" — denom **23** — `COMPONENT`
  - OM3/OG012 — "Phase I Schedule B. Volasertib 500 mg" — denom **5** — `COMPONENT`
  - OM3/OG013 — "Phase I Schedule B. Volasertib 550 mg" — denom **4** — `COMPONENT`
  - OM3/OG014 — "Total Phase I Combined. Schedule B." — denom **56** — `POOLED_TOTAL`
  - OM3/OG017 — "Total Phase II Combined. Schedule A and C." — denom **87** — `POOLED_TOTAL`

### NCT00191152 — excess 158 (4 cohorts, sum 633 vs enrollment 475 ACTUAL)

- **Mechanism:** `M5_SEQUENTIAL_REENTRY`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM7/OG000 Gemcitabine Plus Docetaxel 239; OM7/OG001 Docetaxel Plus Capecitabine 236} = 475 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Protocol-level CROSSOVER design. OM8 reports the crossover-treatment cohorts (Capecitabine 77, Gemcitabine 81); those participants are the same people already counted in the initial-treatment arms, re-counted after crossing over.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM7/OG000 — "Gemcitabine Plus Docetaxel" — denom **239** — `COMPONENT`
  - OM7/OG001 — "Docetaxel Plus Capecitabine" — denom **236** — `COMPONENT`
  - OM8/OG000 — "Capecitabine" — denom **77** — `SEQUENTIAL_REENTRY`
  - OM8/OG001 — "Gemcitabine" — denom **81** — `SEQUENTIAL_REENTRY`

### NCT01089413 — excess 155 (4 cohorts, sum 356 vs enrollment 201 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM2/OG000 Age <70 107; OG001 Age 70-80 58; OG002 Age >80 13} = 178 (registered enrollment 201)
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Observational cohort. OM2/OG003 "Bevacizumab: Overall" 178 is the pooled group and the three age strata partition it exactly (107+58+13=178). 178 < 201, so the response-evaluable population is smaller than registered enrollment.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM2/OG000 — "Bevacizumab: Age <70 Years" — denom **107** — `COMPONENT`
  - OM2/OG001 — "Bevacizumab: Age 70-80 Years" — denom **58** — `COMPONENT`
  - OM2/OG002 — "Bevacizumab: Age >80 Years" — denom **13** — `COMPONENT`
  - OM2/OG003 — "Bevacizumab: Overall" — denom **178** — `POOLED_TOTAL`

### NCT01084863 — excess 143 (4 cohorts, sum 286 vs enrollment 143 ACTUAL)

- **Mechanism:** `M4_ASSESSOR_DUPLICATE`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM4/OG000 CT-P6 & Paclitaxel ITRC 76; OM4/OG001 Herceptin & Paclitaxel ITRC 67} = 143 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** ONE outcome measure carries four groups that are two arms x two readers: independent tumour response committee (ITRC) and investigator, with identical denominators 76 and 67 in each pair. The excess equals the registered enrollment exactly (143), i.e. the population is counted twice.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM4/OG000 — "CT-P6 & Paclitaxel ITRC" — denom **76** — `COMPONENT`
  - OM4/OG001 — "Herceptin & Paclitaxel ITRC" — denom **67** — `COMPONENT`
  - OM4/OG002 — "CT-P6 & Paclitaxel Investigator" — denom **76** — `DUPLICATE_ASSESSOR`
  - OM4/OG003 — "Herceptin & Paclitaxel Investigator" — denom **67** — `DUPLICATE_ASSESSOR`

### NCT00146172 — excess 125 (6 cohorts, sum 198 vs enrollment 73 ACTUAL)

- **Mechanism:** `M3_TITLE_VARIANT_DUPLICATE + M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM1/OG002 All Subjects 60} = 60 (or the strata {25,14}=39, which do not exhaust it)
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM1 and OM4 report the same three cohorts under different titles (Breast Cancer Cohort/Breast Cancer, Lung Cancer Cohort/Lung Cancer, All Subjects/All Solid Tumors), so the title-keyed rule counts each twice; within each outcome measure a pooled All group is also summed with its two named strata. The two strata (25+14=39) do not sum to 60, so the pooled group additionally covers tumour types not broken out.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM1/OG000 — "Breast Cancer Cohort" — denom **25** — `COMPONENT`
  - OM1/OG001 — "Lung Cancer Cohort" — denom **14** — `COMPONENT`
  - OM1/OG002 — "All Subjects" — denom **60** — `POOLED_TOTAL`
  - OM4/OG000 — "Breast Cancer" — denom **25** — `DUPLICATE_TITLE_VARIANT`
  - OM4/OG001 — "Lung Cancer" — denom **14** — `DUPLICATE_TITLE_VARIANT`
  - OM4/OG002 — "All Solid Tumors" — denom **60** — `DUPLICATE_TITLE_VARIANT`

### NCT00790400 — excess 112 (3 cohorts, sum 230 vs enrollment 118 ACTUAL)

- **Mechanism:** `M5_SEQUENTIAL_REENTRY`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM0/OG000 Everolimus Randomized (Core Period) 79; OM0/OG001 Placebo Randomized (Core Period) 39} = 118 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM0/OG002 "Everolimus (Core and/or Extension Period)" 112 is described as "Patients initially randomized in everolimus and patients initially randomized in placebo but who crossed-over to everolimus" - i.e. a post-crossover re-count of patients already in both randomised groups.
- **Cohorts driving it** (payload `ctg_placebo_onc_1999_2009`):
  - OM0/OG000 — "Everolimus Randomized (Core Period)" — denom **79** — `COMPONENT`
  - OM0/OG001 — "Placebo Randomized (Core Period)" — denom **39** — `COMPONENT`
  - OM0/OG002 — "Everolimus (Core and/or Extension Period)" — denom **112** — `SEQUENTIAL_REENTRY`

### NCT00668148 — excess 109 (6 cohorts, sum 222 vs enrollment 113 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM2/OG000 18; OG001 17; OG002 22; OG003 37; OG004 17} = 111
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM2/OG005 "Total" is described as "Total of all reporting groups" (111 = sum of the five histology cohorts; registered enrollment 113).
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM2/OG000 — "Ewing's Sarcoma/PNET" — denom **18** — `COMPONENT`
  - OM2/OG001 — "Rhabdomyosarcoma" — denom **17** — `COMPONENT`
  - OM2/OG002 — "Leiomyosarcoma" — denom **22** — `COMPONENT`
  - OM2/OG003 — "Adipocytic Sarcoma" — denom **37** — `COMPONENT`
  - OM2/OG004 — "Synovial Sarcoma" — denom **17** — `COMPONENT`
  - OM2/OG005 — "Total" — denom **111** — `POOLED_TOTAL`

### NCT01251536 — excess 108 (4 cohorts, sum 216 vs enrollment 108 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM7/OG000 Arm A 8; OG001 Arm B 93; OG002 Not Allocated 7} = 108 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM7/OG003 "ITT / Safety Set" 108 is the pooled group; the two allocated arms plus the "Not Allocated" group partition it exactly.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM7/OG000 — "Arm A - Dose Escalation of Cetuximab" — denom **8** — `COMPONENT`
  - OM7/OG001 — "Arm B - Standard Dose of Cetuximab" — denom **93** — `COMPONENT`
  - OM7/OG002 — "Not Allocated" — denom **7** — `COMPONENT`
  - OM7/OG003 — "ITT / Safety Set" — denom **108** — `POOLED_TOTAL`

### NCT00152477 — excess 97 (4 cohorts, sum 262 vs enrollment 165 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM0/OG000 CP 50; OM0/OG002 CDP791 10mg 53; OM0/OG003 CDP791 20mg 53} = 156
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM0/OG001 is described in the record as "Pooled CDP791 10 mg/kg or 20 mg/kg + CT treatment arms" (106 = 53+53).
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM0/OG000 — "Carboplatin/Paclitaxel (Randomized Part II SjS)" — denom **50** — `COMPONENT`
  - OM0/OG001 — "Carboplatin/Paclitaxel/CDP791 (Randomized Part II SjS)" — denom **106** — `POOLED_TOTAL`
  - OM0/OG002 — "Carboplatin/Paclitaxel/CDP791 10mg (Randomized Part II SS)" — denom **53** — `COMPONENT`
  - OM0/OG003 — "Carboplatin/Paclitaxel/CDP791 20mg (Randomized Part II SjS)" — denom **53** — `COMPONENT`

### NCT01063907 — excess 95 (6 cohorts, sum 190 vs enrollment 95 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM0/OG001 3; OG002 3; OG003 3; OG004 6; OG005 Phase 2 80} = 95 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM0/OG000 "Phase 1 & 2: KW-2478 175 mg/m^2 and Bortezomib 1.3mg/m^2" 95 pools the four phase-1 dose cohorts and the phase-2 cohort.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM0/OG000 — "Phase 1 & 2: KW-2478 175 mg/m^2 and Bortezomib 1.3mg/m^2" — denom **95** — `POOLED_TOTAL`
  - OM0/OG001 — "Phase 1 Cohort 1: KW-2478 130 mg/m^2 and Bortezomib 1.0mg/m^2" — denom **3** — `COMPONENT`
  - OM0/OG002 — "Phase 1 Cohort 2: KW-2478 130 mg/m^2 and Bortezomib 1.3mg/m^2" — denom **3** — `COMPONENT`
  - OM0/OG003 — "Phase 1 Cohort 3: KW-2478 175 mg/m^2 and Bortezomib 1.0mg/m^2" — denom **3** — `COMPONENT`
  - OM0/OG004 — "Phase 1 Cohort 4: KW-2478 175 mg/m^2 and Bortezomib 1.3mg/m^2" — denom **6** — `COMPONENT`
  - OM0/OG005 — "Phase 2: KW-2478 175 mg/m^2 and Bortezomib 1.3mg/m^2" — denom **80** — `COMPONENT`

### NCT00451555 — excess 90 (4 cohorts, sum 246 vs enrollment 156 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM0/OG001 Enz+Fulv BID 39; OM0/OG002 Enz+Fulv QD 55; OM0/OG003 Fulvestrant+Placebo 58} = 152
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM0/OG000 "Enzastaurin + Fulvestrant QD + BID" 94 is the pooled experimental arm (94 = 39+55). Reduced set 152 sits 4 below registered enrollment 156 (randomised-but-not-treated).
- **Cohorts driving it** (payload `ctg_placebo_onc_1999_2009|ctg_results_bor_1999_2009`):
  - OM0/OG000 — "Enzastaurin + Fulvestrant QD + BID" — denom **94** — `POOLED_TOTAL`
  - OM0/OG001 — "Enzastaurin + Fulvestrant BID" — denom **39** — `COMPONENT`
  - OM0/OG002 — "Enzastaurin + Fulvestrant QD" — denom **55** — `COMPONENT`
  - OM0/OG003 — "Fulvestrant + Placebo" — denom **58** — `COMPONENT`

### NCT01217957 — excess 88 (3 cohorts, sum 153 vs enrollment 65 ACTUAL)

- **Mechanism:** `M3_TITLE_VARIANT_DUPLICATE + M8_ANALYSIS_POPULATION_NESTING`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM1/OG001 Phase 2: Ixazomib 4.0mg/2.23 + Len + Dex 52} = 52 (registered enrollment 65)
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** The 52-participant phase-2 population appears twice under titles differing by one space ("4.0mg/2.23" in OM1 vs "4.0 mg/2.23" in OM13). Its description states it "Includes 3 participants who received 2.23 mg/m^2 in Phase 1", so the 49-participant group is the same population minus those 3 - a nested subset, not a separate cohort.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM1/OG000 — "Phase 2: Ixazomib 4.0 mg + Lenalidomide + Dexamethasone" — denom **49** — `NESTED_SUBSET`
  - OM1/OG001 — "Phase 2: Ixazomib 4.0mg/2.23 + Lenalidomide + Dexamethasone" — denom **52** — `KEEP_ITT`
  - OM13/OG001 — "Phase 2: Ixazomib 4.0 mg/2.23 + Lenalidomide + Dexamethasone" — denom **52** — `DUPLICATE_TITLE_VARIANT`

### NCT00171834 — excess 81 (8 cohorts, sum 170 vs enrollment 89 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS + M3_TITLE_VARIANT_DUPLICATE`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM6/OG000 Patupilone Phase I 50; OM4/OG000 Patupilone 10 mg/m^2 (Phase II) NSCLC Cohort 35} = 85
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM6 pools Phase I (50 = 6+12+12+12+8 of the five OM0 dose bands) and restates Phase II (35) already carried by OM4 under a different title.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM0/OG000 — "Patupilone ≤7.0 mg/m^2 (Phase I)" — denom **6** — `COMPONENT`
  - OM0/OG001 — "Patupilone 7.5-8.0 mg/m^2 (Phase I)" — denom **12** — `COMPONENT`
  - OM0/OG002 — "Patupilone 8.5-9.5 mg/m^2 (Phase I)" — denom **12** — `COMPONENT`
  - OM0/OG003 — "Patupilone 10.0-11.5 mg/m^2 (Phase I)" — denom **12** — `COMPONENT`
  - OM0/OG004 — "Patupilone 12.0-13.0 mg/m^2 (Phase I)" — denom **8** — `COMPONENT`
  - OM4/OG000 — "Patupilone 10 mg/m^2 (Phase II) NSCLC Cohort" — denom **35** — `COMPONENT`
  - OM6/OG000 — "Patupilone (EPO906) Phase I" — denom **50** — `POOLED_TOTAL`
  - OM6/OG001 — "Patupilone (EPO906) Phase II" — denom **35** — `DUPLICATE_TITLE_VARIANT`

### NCT00462761 — excess 76 (13 cohorts, sum 152 vs enrollment 76 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** the twelve OM3 dose-schedule groups (OG000-OG011) = 76 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM3/OG012 "All Participants" 76 is described as "All participants who received quizartinib, regardless of dosage and dosing schedule".
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM3/OG000 — "Quizartinib 12 mg ID" — denom **3** — `COMPONENT`
  - OM3/OG001 — "Quizartinib 18 mg ID" — denom **8** — `COMPONENT`
  - OM3/OG002 — "Quizartinib 27 mg ID" — denom **6** — `COMPONENT`
  - OM3/OG003 — "Quizartinib 40 mg ID" — denom **5** — `COMPONENT`
  - OM3/OG004 — "Quizartinib 60 mg ID" — denom **5** — `COMPONENT`
  - OM3/OG005 — "Quizartinib 90 mg ID" — denom **3** — `COMPONENT`
  - OM3/OG006 — "Quizartinib 135 mg ID" — denom **5** — `COMPONENT`
  - OM3/OG007 — "Quizartinib 200 mg ID" — denom **6** — `COMPONENT`
  - OM3/OG008 — "Quizartinib 300 mg ID" — denom **4** — `COMPONENT`
  - OM3/OG009 — "Quizartinib 450 mg ID" — denom **6** — `COMPONENT`
  - OM3/OG010 — "Quizartinib 200 mg CD" — denom **17** — `COMPONENT`
  - OM3/OG011 — "Quizartinib 300 mg CD" — denom **8** — `COMPONENT`
  - OM3/OG012 — "All Participants" — denom **76** — `POOLED_TOTAL`

### NCT00137449 — excess 60 (3 cohorts, sum 120 vs enrollment 60 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM2/OG000 AM 30; OM2/OG001 PM 30} = 60
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Group title states the arithmetic: "Total (Equals AM Plus PM Dose)".
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM2/OG000 — "AM Dose Sunitinib Malate" — denom **30** — `COMPONENT`
  - OM2/OG001 — "PM Dose Sunitinib Malate" — denom **30** — `COMPONENT`
  - OM2/OG002 — "Total (Equals AM Plus PM Dose) Sunitinib Malate" — denom **60** — `POOLED_TOTAL`

### NCT00371345 — excess 58 (9 cohorts, sum 150 vs enrollment 92 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS + M3_TITLE_VARIANT_DUPLICATE + M7_NON_COHORT_GROUPS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM0/OG000 15; OM0/OG001 9; OM0/OG002 31; OM0/OG003 14} = 69
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Three drivers: (a) OM1/OG004 "All Response-evaluable Participants" 69 pools the four OM0 biomarker x dose cells (15+9+31+14=69); (b) OM1/OG001 restates OM0/OG001 under the title variant "...100 mg BID Dasatinib"; (c) OM7 (Duration of Objective Response) reports three groups that are named individual participants, each n=1 - responder listings, not cohorts.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM0/OG000 — "Her2/Neu-amplified Tumor, 70 mg Twice Daily (BID) Dasatinib" — denom **15** — `COMPONENT`
  - OM0/OG001 — "Her2/Neu-amplified Tumor, 100 mg BID" — denom **9** — `COMPONENT`
  - OM0/OG002 — "ER and/or PgR Positive Tumor, 70 mg BID Dasatinib" — denom **31** — `COMPONENT`
  - OM0/OG003 — "ER and/or PgR Positive Tumor, 100 mg BID Dasatinib" — denom **14** — `COMPONENT`
  - OM1/OG001 — "Her2/Neu-amplified Tumor, 100 mg BID Dasatinib" — denom **9** — `DUPLICATE_TITLE_VARIANT`
  - OM1/OG004 — "All Response-evaluable Participants" — denom **69** — `POOLED_TOTAL`
  - OM7/OG000 — "Participant CA180088-18-88009, HER-2 Group" — denom **1** — `SINGLE_PARTICIPANT`
  - OM7/OG001 — "Participant CA180088-16-88002, ER and/or PgR Group" — denom **1** — `SINGLE_PARTICIPANT`
  - OM7/OG002 — "Participant CA180088-29-88085, ER and/or PgR Group" — denom **1** — `SINGLE_PARTICIPANT`

### NCT01088984 — excess 43 (3 cohorts, sum 86 vs enrollment 43 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM3/OG000 Phase 1 11; OM1/OG000 Phase 2 32} = 43 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM3/OG002 "Total" 43 pools the two phase cohorts; OM1 restates the phase-2 cohort (32) which is counted once by the title key.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM1/OG000 — "Phase 2: Bendamustine 120 mg/m^2" — denom **32** — `COMPONENT`
  - OM3/OG000 — "Phase 1: Bendamustine 90 or 120 mg/m^2" — denom **11** — `COMPONENT`
  - OM3/OG002 — "Total" — denom **43** — `POOLED_TOTAL`

### NCT00243074 — excess 40 (2 cohorts, sum 94 vs enrollment 54 ACTUAL)

- **Mechanism:** `M3_TITLE_VARIANT_DUPLICATE`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM0/OG000 AZD2171 (Cediranib Maleate) 47} = 47
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM0 and OM3 report the same single treated cohort of 47 under titles "AZD2171 (Cediranib Maleate)" and "AZD2171"; the title-keyed rule treats them as two cohorts. 47 is also below registered enrollment 54 (evaluable subset), so there is no real excess once de-duplicated.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM0/OG000 — "AZD2171 (Cediranib Maleate)" — denom **47** — `COMPONENT`
  - OM3/OG000 — "AZD2171" — denom **47** — `DUPLICATE_TITLE_VARIANT`

### NCT00633594 — excess 39 (4 cohorts, sum 78 vs enrollment 39 ACTUAL)

- **Mechanism:** `M2_CROSS_AXIS_PARTITION`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** either axis alone: {OM2/OG000 13; OM2/OG001 26} = 39, or {OM3/OG000 10; OM3/OG001 29} = 39
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM2 partitions the 39 efficacy-evaluable participants by trial phase; OM3 partitions the SAME 39 by prior treatment. Both partitions sum to 39 = registered enrollment; the record does not cross-tabulate them, so either may be kept but not both.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM2/OG000 — "Phase I Participants (10 mg/15 mg Lenalidomide)" — denom **13** — `AXIS1_KEEP`
  - OM2/OG001 — "Phase II Participants (10 mg Lenalidomide)" — denom **26** — `AXIS1_KEEP`
  - OM3/OG000 — "Previously Treated Participants" — denom **10** — `AXIS2_CROSS_AXIS`
  - OM3/OG001 — "Previously Untreated Participants" — denom **29** — `AXIS2_CROSS_AXIS`

### NCT01227889 — excess 36 (3 cohorts, sum 287 vs enrollment 251 ACTUAL)

- **Mechanism:** `M5_SEQUENTIAL_REENTRY`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM4/OG000 GSK2118436 150 mg BID 187; OM4/OG001 DTIC 1000 mg/m^2 in RP 63} = 250 (registered enrollment 251)
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** CROSSOVER design. OM8/OG000 "GSK25118436 in Crossover Phase" 37 is described as "Participants who received DTIC in the RP and experienced DP had the option ... of [crossing over]" - a subset of the 63 DTIC participants, re-counted.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM4/OG000 — "GSK2118436 150 mg BID" — denom **187** — `COMPONENT`
  - OM4/OG001 — "DTIC 1000 mg/m^2 in RP" — denom **63** — `COMPONENT`
  - OM8/OG000 — "GSK25118436 in Crossover Phase" — denom **37** — `SEQUENTIAL_REENTRY`

### NCT00400803 — excess 32 (4 cohorts, sum 70 vs enrollment 38 ACTUAL)

- **Mechanism:** `M7_NON_COHORT_GROUPS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM1/OG000 Intent To Treat - Lung Cancer Patients 35} = 35
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM1 reports the ITT cohort (35) alongside three groups that are RECIST response CATEGORIES - Partial Response 19, Stable Disease 10, Progressive Disease 6 - whose descriptions are the RECIST definitions and which sum exactly to 35. These are outcome strata of one cohort, not cohorts.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM1/OG000 — "Intent To Treat - Lung Cancer Patients" — denom **35** — `KEEP_ITT`
  - OM1/OG001 — "Partial Response" — denom **19** — `OUTCOME_STRATUM`
  - OM1/OG002 — "Stable Disease" — denom **10** — `OUTCOME_STRATUM`
  - OM1/OG003 — "Progressive Disease" — denom **6** — `OUTCOME_STRATUM`

### NCT00606008 — excess 30 (3 cohorts, sum 60 vs enrollment 30 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM1/OG001 AA Cohort Patients 14; OM1/OG002 GB Cohort Patients 16} = 30 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM1/OG000 "Sutent Treatment" 30 is the pooled arm. Note a labelling defect in the source: OG001 is titled "AA Cohort Patients" but described as "Recurrent glioblastoma (GB) patients" and OG002 the reverse. The arithmetic is unaffected; the histology labels are not trustworthy from this record.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM1/OG000 — "Sutent Treatment" — denom **30** — `POOLED_TOTAL`
  - OM1/OG001 — "AA Cohort Patients" — denom **14** — `COMPONENT`
  - OM1/OG002 — "GB Cohort Patients" — denom **16** — `COMPONENT`

### NCT01077518 — excess 30 (3 cohorts, sum 376 vs enrollment 346 ACTUAL)

- **Mechanism:** `M5_SEQUENTIAL_REENTRY`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM2/OG000 Ofa+Benda (Arm A) 173; OM2/OG001 Benda (Arm B) 173} = 346 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM23/OG000 "Optional Ofa" 30 is described as "Eligible benda arm participants who were offered optional ofatumumab following disease progression" - a post-progression re-count of Arm B participants.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM2/OG000 — "Ofa + Benda (Arm A)" — denom **173** — `COMPONENT`
  - OM2/OG001 — "Benda (Arm B)" — denom **173** — `COMPONENT`
  - OM23/OG000 — "Optional Ofa" — denom **30** — `SEQUENTIAL_REENTRY`

### NCT00623766 — excess 24 (3 cohorts, sum 123 vs enrollment 99 ACTUAL)

- **Mechanism:** `M3_TITLE_VARIANT_DUPLICATE`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM0/OG000 corticosteroid-free 51; OM0/OG001 corticosteroid-dependent 21} = 72
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM0 and OM1 report the same two cohorts under two response criteria (mWHO and irRC); the corticosteroid-free group differs only by a comma ("Ipilimumab, 10 mg/kg IV," vs "Ipilimumab 10 mg/kg IV,") so the title key fails to merge it, while the corticosteroid-dependent group matched and was counted once.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM0/OG000 — "Ipilimumab, 10 mg/kg IV, in Corticosteroid-free Patients" — denom **51** — `COMPONENT`
  - OM0/OG001 — "Ipilimumab, 10 mg/kg IV, in Corticosteroid-dependent Patients" — denom **21** — `COMPONENT`
  - OM1/OG000 — "Ipilimumab 10 mg/kg IV, in Corticosteroid-free Patients" — denom **51** — `DUPLICATE_TITLE_VARIANT`

### NCT01199055 — excess 23 (5 cohorts, sum 39 vs enrollment 16 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM4/OG000 0.25 mg Initial 3; OG001 0.50 mg Initial 3; OG002 0.50 mg Additional 8} = 14 (registered enrollment 16)
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** TWO nested pooled groups in one outcome measure: OG003 "CS71017 0.5 mg BID; Initial and Additional Portion" 11 (= 3+8) and OG004 "Overall" 14 (= 3+3+8). Note the source typo "CS71017".
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM4/OG000 — "CS-7017 0.25 mg BID; Initial Portion" — denom **3** — `COMPONENT`
  - OM4/OG001 — "CS-7017 0.50 mg BID; Initial Portion" — denom **3** — `COMPONENT`
  - OM4/OG002 — "CS-7017 0.50 mg BID; Additional Portion" — denom **8** — `COMPONENT`
  - OM4/OG003 — "CS71017 0.5 mg BID; Initial and Additional Portion" — denom **11** — `POOLED_TOTAL`
  - OM4/OG004 — "Overall" — denom **14** — `POOLED_TOTAL`

### NCT01055067 — excess 21 (2 cohorts, sum 48 vs enrollment 27 ACTUAL)

- **Mechanism:** `M8_ANALYSIS_POPULATION_NESTING`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM0/OG001 Total 27} = 27 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM0/OG000 "Stage 1: ARQ 197 360 mg BID" 21 is the Simon stage-1 subset of the 27 enrolled.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM0/OG000 — "Stage 1: ARQ 197 360 mg BID" — denom **21** — `NESTED_SUBSET`
  - OM0/OG001 — "Total" — denom **27** — `KEEP_ITT`

### NCT01199068 — excess 19 (5 cohorts, sum 34 vs enrollment 15 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM4/OG000 0.25 mg Initial 2; OG003 0.50 mg Initial 3; OG002 0.50 mg Additional 7} = 12 (registered enrollment 15)
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Same structure as its sister trial: OG003(sic, title "Initial + Additional Portions") 10 (= 3+7) and OG004 "Overall" 12 (= 2+3+7) are pooled groups summed with their components.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM4/OG000 — "CS-7017 0.25 mg BID; Initial Portion" — denom **2** — `COMPONENT`
  - OM4/OG001 — "CS-7017 0.50 mg BID; Initial Portion" — denom **3** — `COMPONENT`
  - OM4/OG002 — "CS-7017 0.50 mg BID; Additional Portion" — denom **7** — `COMPONENT`
  - OM4/OG003 — "CS-7017 0.50 mg BID; Initial + Additional Portions" — denom **10** — `POOLED_TOTAL`
  - OM4/OG004 — "Overall" — denom **12** — `POOLED_TOTAL`

### NCT00598975 — excess 18 (3 cohorts, sum 36 vs enrollment 18 ACTUAL)

- **Mechanism:** `M1_POOLED_PLUS_COMPONENTS`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM2/OG000 12; OM2/OG001 6} = 18 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM2/OG002 "Total" is the explicit pooled group.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM2/OG000 — "NKTR-102 100 mg/m2 + Cetuximab" — denom **12** — `COMPONENT`
  - OM2/OG001 — "NKTR-102 125 mg/m2 + Cetuximab" — denom **6** — `COMPONENT`
  - OM2/OG002 — "Total" — denom **18** — `POOLED_TOTAL`

### NCT00792467 — excess 16 (2 cohorts, sum 40 vs enrollment 24 ACTUAL)

- **Mechanism:** `M8_ANALYSIS_POPULATION_NESTING`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM0/OG000 ITT Population 24} = 24 = registered enrollment
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM0 reports ITT (24) and per-protocol (16) denominators for the same trial; PP is a subset of ITT.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM0/OG000 — "ITT Population" — denom **24** — `KEEP_ITT`
  - OM0/OG001 — "PP Population" — denom **16** — `NESTED_SUBSET`

### NCT00918203 — excess 11 (3 cohorts, sum 148 vs enrollment 137 ACTUAL)

- **Mechanism:** `M5_SEQUENTIAL_REENTRY`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM4/OG000 Olaratumab+P+C 67; OM4/OG001 Paclitaxel+Carboplatin 64} = 131 (registered enrollment 137)
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** CROSSOVER design. OM4/OG002 "Crossover to Olaratumab" 17 are control-arm participants who later received olaratumab monotherapy - already counted in the 64.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM4/OG000 — "Olaratumab + Paclitaxel + Carboplatin" — denom **67** — `COMPONENT`
  - OM4/OG001 — "Paclitaxel + Carboplatin" — denom **64** — `COMPONENT`
  - OM4/OG002 — "Crossover to Olaratumab" — denom **17** — `SEQUENTIAL_REENTRY`

### NCT00700258 — excess 8 (5 cohorts, sum 1,528 vs enrollment 1,520 ACTUAL)

- **Mechanism:** `M5_SEQUENTIAL_REENTRY`
- **Reducible to a non-overlapping set from the record alone:** **UNRESOLVED**
- **Reduced set:** UNRESOLVED — partially: {OM2/OG000 mRCC-Temsirolimus 577; OM2/OG003 MCL-Temsirolimus 55; OM2/OG004 GIST-Sunitinib 24} are disjoint; the mRCC-Sunitinib 651 and mRCC-Axitinib 221 groups overlap by an amount the record does not state
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Observational cohort study. OM2/OG001 is described as "...received sunitinib (some of the participants stopped sunitinib and received axitinib...)" and OM2/OG002 as "...received axitinib (some of the participants initially received sunitinib)". The record states the overlap exists but never quantifies it, so no exact non-overlapping set can be derived. The 8-participant excess bounds the shared count from below only if 1,520 is the unique-participant total, which the record does not assert.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM2/OG000 — "mRCC - Temsirolimus" — denom **577** — `COMPONENT`
  - OM2/OG001 — "mRCC - Sunitinib" — denom **651** — `UNRESOLVED_PART`
  - OM2/OG002 — "mRCC - Axitinib" — denom **221** — `UNRESOLVED_PART`
  - OM2/OG003 — "MCL - Temsirolimus" — denom **55** — `COMPONENT`
  - OM2/OG004 — "GIST - Sunitinib" — denom **24** — `COMPONENT`

### NCT00756509 — excess 7 (1 cohorts, sum 41 vs enrollment 34 ACTUAL)

- **Mechanism:** `M6_REGISTRY_INCONSISTENCY`
- **Reducible to a non-overlapping set from the record alone:** **NO**
- **Reduced set:** not applicable - only ONE cohort is selected, so no overlap is possible
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** A single selected cohort, OM0/OG000 "Nilotinib", carries denom 41 while designModule.enrollmentInfo records count 34, type ACTUAL. With one cohort the excess cannot be overlap; it is an internal contradiction between the results denominator and the registered enrollment field. UNRESOLVED as to which is correct.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM0/OG000 — "Nilotinib" — denom **41** — `STANDALONE_EXCEEDS_ENROLLMENT`

### NCT00885755 — excess 6 (2 cohorts, sum 39 vs enrollment 33 ACTUAL)

- **Mechanism:** `M8_ANALYSIS_POPULATION_NESTING + M3_TITLE_VARIANT_DUPLICATE`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM9/OG000 Group A ... 20} = 20 (registered enrollment 33)
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** The same Group A appears in OM9 (ITT population, n=20) and OM11 (by-biomarker population, n=19), separated only by a typo in the source title ("Capcetabine" vs "Capecitabine"). The 19 is the biomarker-evaluable subset of the 20.
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM9/OG000 — "Group A: Trastuzumab+Taxane /Capcetabine (6 Weeks)" — denom **20** — `KEEP_ITT`
  - OM11/OG000 — "Group A: Trastuzumab+Taxane /Capecitabine (6 Weeks)" — denom **19** — `NESTED_SUBSET`

### NCT00928642 — excess 6 (2 cohorts, sum 14 vs enrollment 8 ACTUAL)

- **Mechanism:** `M3_TITLE_VARIANT_DUPLICATE`
- **Reducible to a non-overlapping set from the record alone:** **YES**
- **Reduced set:** {OM2/OG000 Oral Imatinib Plus IV Gemcitabine 7} = 7 (registered enrollment 8)
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** OM2 and OM4 report the same single-arm cohort of 7 under the titles "Oral Imatinib Plus IV Gemcitabine" and "Treatment".
- **Cohorts driving it** (payload `ctg_results_bor_1999_2009`):
  - OM2/OG000 — "Oral Imatinib Plus IV Gemcitabine" — denom **7** — `COMPONENT`
  - OM4/OG000 — "Treatment" — denom **7** — `DUPLICATE_TITLE_VARIANT`

### NCT01223027 — excess 6 (2 cohorts, sum 570 vs enrollment 564 ACTUAL)

- **Mechanism:** `M6_REGISTRY_INCONSISTENCY`
- **Reducible to a non-overlapping set from the record alone:** **NO**
- **Reduced set:** the two OM3 arms are disjoint by design; 284+286=570 vs registered enrollment 564
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Two-arm randomised trial with one central-review results group per arm and no pooled or duplicate group. The 6-participant excess is a field discrepancy, not overlap. UNRESOLVED as to which field is wrong.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM3/OG000 — "Dovitinib + Best Supportive Care (BSC)" — denom **284** — `COMPONENT`
  - OM3/OG001 — "Sorafenib + BSC" — denom **286** — `COMPONENT`

### NCT01232296 — excess 3 (2 cohorts, sum 165 vs enrollment 162 ACTUAL)

- **Mechanism:** `M6_REGISTRY_INCONSISTENCY`
- **Reducible to a non-overlapping set from the record alone:** **NO**
- **Reduced set:** the two OM2 arms are disjoint by design; 82+83=165 vs registered enrollment 162
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Two-arm randomised trial, one results group per arm, no pooled or duplicate group. The 3-participant excess is a field discrepancy, not overlap. UNRESOLVED as to which field is wrong.
- **Cohorts driving it** (payload `ctg_results_bor_2010_2013`):
  - OM2/OG000 — "TKI258" — denom **82** — `COMPONENT`
  - OM2/OG001 — "Sorafenib" — denom **83** — `COMPONENT`

### NCT00229723 — excess 2 (7 cohorts, sum 226 vs enrollment 224 ACTUAL)

- **Mechanism:** `M6_REGISTRY_INCONSISTENCY`
- **Reducible to a non-overlapping set from the record alone:** **NO**
- **Reduced set:** all seven OM0 groups are disjoint by design; their sum 226 already exceeds registered enrollment 224
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Seven-cell factorial (concomitant x maintenance); each results group is one distinct randomisation cell and no pooled or duplicate group is present. The 2-participant excess is a discrepancy between the results groups and the registered ACTUAL enrollment field, not overlap. UNRESOLVED as to which field is wrong.
- **Cohorts driving it** (payload `ctg_placebo_onc_1999_2009`):
  - OM0/OG000 — "Placebo/Placebo" — denom **60** — `COMPONENT`
  - OM0/OG001 — "250mg/Placebo" — denom **24** — `COMPONENT`
  - OM0/OG002 — "500mg/Placebo" — denom **31** — `COMPONENT`
  - OM0/OG003 — "250mg/250mg" — denom **31** — `COMPONENT`
  - OM0/OG004 — "500mg/500mg" — denom **24** — `COMPONENT`
  - OM0/OG005 — "Placebo/250mg" — denom **34** — `COMPONENT`
  - OM0/OG006 — "Placebo/500mg" — denom **22** — `COMPONENT`

### NCT01023308 — excess 1 (2 cohorts, sum 768 vs enrollment 767 ACTUAL)

- **Mechanism:** `M6_REGISTRY_INCONSISTENCY`
- **Reducible to a non-overlapping set from the record alone:** **NO**
- **Reduced set:** the two OM4 arms are disjoint by design; 387+381=768 vs registered enrollment 767
- **Enrollment type:** ACTUAL (not ESTIMATED)
- **Why:** Two-arm randomised trial, one results group per arm, no pooled or duplicate group. The 1-participant excess is a field discrepancy, not overlap. UNRESOLVED as to which field is wrong.
- **Cohorts driving it** (payload `ctg_placebo_onc_1999_2009|ctg_results_bor_1999_2009`):
  - OM4/OG000 — "Panobinostat + Bortezomib" — denom **387** — `COMPONENT`
  - OM4/OG001 — "Placebo + Bortezomib" — denom **381** — `COMPONENT`

## What I did not establish

- Nothing here concerns unique patients ACROSS trials; that is global and outside this leaf.
- I did not rebuild the selection rule, re-run the global scan, or restate Job 2 global counts as findings.
- The reduced sets are derived from the cached record only. Where a reduction leaves a sum BELOW registered
  enrollment (e.g. NCT00069095 1,904 vs 2,035; NCT01089413 178 vs 201), I make no claim about the missing
  participants — the record does not say whether they were unevaluable, withdrawn, or simply not reported.
- For the 5 `M6_REGISTRY_INCONSISTENCY` trials I do not adjudicate WHICH field is wrong; the record contains
  no third source to break the tie.
- Assertions about efficacy, safety, selectivity or clinical readiness: none made.
