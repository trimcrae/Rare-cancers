# LEAF QB / group 3 — why selected cohort denominators exceed registered enrollment

Leaf worker output for QUESTION B, NCT group `LEAF-ASSIGNMENTS/QB-group3.txt` (45 trials).
Written 2026-09-08. Untracked artifact; nothing in the repository was edited to produce it.

## Scope and fences

- **My rows only.** The 45 NCTs in `QB-group3.txt`. Any other NCT is outside my group and is not
  reasoned about here.
- **Not redone:** Job 2's selection rule (`CURATION-endpoint-identity-and-overlap-artifacts/RULE-PREREGISTERED.md`),
  its global cohort selection, and its global excess measurement. Those are context. The global
  180-trial / 22,578-slot figure is Job 2's finding, not mine, and is not restated as a result here.
- **Nothing global is concluded.** No statement is made about unique patients across trials; that is
  the parent's reconciliation, after keys come back.
- **No network access was used.** All evidence is the frozen cache
  `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5/`
  (branch `literature-cache` @ `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`).
- **No efficacy, safety, selectivity or clinical claim** is made anywhere in this file. Every number
  below is a denominator or a participant count read out of a registry record.

## Cache verification

```
sha256sum -c SHA256-MANIFEST.txt   # 13 files, all OK
exit code: 0
```

## Coverage

| item | value |
|---|---|
| trials assigned | 45 |
| trials reached in the cache | **45** (100%) |
| trials not reached | 0 |
| distinct payload copies per trial | 1 for all 45 (no cross-payload duplicate to canonicalise) |
| selected cohorts adjudicated | 314 (one detail row each in the TSV) |
| sum of `excess` over my 45 trials | 5,154 participant-slots |
| sum of `sum_selected_denominators` over my 45 trials | 12,045 |
| sum of registered enrollment over my 45 trials | 6,891 |

Each trial appears in exactly one payload; the payload file and its line number are recorded per
trial in the TSV so every quoted denominator can be re-derived from the frozen cache.

## Answer to item 4 first — enrollment_type

**All 45 trials in my group carry `enrollmentInfo.type == "ACTUAL"` in the cached record. Zero are
`ESTIMATED`.** I re-read `protocolSection.designModule.enrollmentInfo` directly from each cached
record rather than trusting the `enrollment_type` column of `OVERLAP-enrollment-check.tsv`; the two
agree for all 45. So the "estimated enrollment below a reported denominator" case — which would not
be an overlap finding at all — **does not occur anywhere in this group**, and nothing here needs to
be separated out on that ground.

## Mechanism categories used

I did not force trials into Job 2's list. Job 2's candidates that occur here are kept with its
names; three categories are added because the records show mechanisms its two hand-adjudicated
exhibits did not cover. Per-measure-timepoint denominator drift and estimated-enrollment do **not**
occur as the driving mechanism for any trial in my group.

| code | meaning | trials (primary or contributing) |
|---|---|---|
| `DUPLICATE_TITLE_VARIANT` | **added.** The *same* cohort is written with a different punctuation, spacing, unit order, typo or abbreviation in a second outcome measure, so the rule's `(nct, normalised group title)` key splits it into two cohorts. Normalisation is NFKC + casefold + whitespace-collapse + edge-punctuation strip, which does not close `"HCC-1L"` vs `"HCC 1L"`, `"3.2 mg/kg"` vs `"3.2 kg/mg"`, or `"Ruxolitinib"` vs `"Ruxolitibin"`. | 16 |
| `NESTED_SUBSET` | A selected cohort is strictly contained in another selected cohort — a biomarker-confirmed analysis set, an evaluable subset, a crossover subset, or a first-line subset — as stated in the group description or population description. | 14 |
| `POOLED_UNFLAGGED` | A pooled/superset cohort summed alongside its own components, whose label falls **outside** the rule's pooled vocabulary (`total`, `overall`, `all participants`, `all patients`, `combined`) and is therefore not flagged: `"Part 2 - total"`, `"Part 1: PF-06863135 Total IV"`, `"All Treated Participants"`, `"Phase 1b + Phase 2"`, `"Part 1+2: ..."`, `"FL and MZL: ..."`, `"Physician's Choice Overall"`. | 10 |
| `POOLED_EXPLICIT` | An explicit `Total`/`All Participants` cohort summed alongside its own components. The rule *flags* these (`pooled_label=True`) but the enrollment check still sums them. | 7 |
| `CROSS_AXIS_DUPLICATE` | Two or more complete partitions of the same patients on different axes (arm × PD-L1 CPS × cisplatin-eligibility × Karnofsky; dose × IHC subtype × gene-expression subtype; cohort × ctDNA mutation status). | 5 |
| `CROSSOVER_DOUBLE_COUNT` | **added.** The record *declares* that the same participants are counted in two groups because of a crossover or a fed/fasted period design. | 2 |
| `NONCOHORT_METHOD_LABEL` | **added.** The results-group titles do not name patient cohorts at all — they name the assessment method — so the arm identity lives only in the group `description` field. | 1 |
| `MULTILINE_DOUBLE_COUNT` | **added.** A retrospective chart-review study whose groups are lines of therapy joined by "and/or", so a patient treated in both lines is in both groups. | 1 |

Per-cohort role tallies over the 314 selected cohorts: `COMPONENT_KEPT` 191, `DUPLICATE_TITLE_VARIANT` 31,
`CROSS_AXIS_DUPLICATE` 31, `NESTED_SUBSET` 26, `POOLED_UNFLAGGED` 14, `POOLED_EXPLICIT` 7,
`UNRESOLVED_DECLARED_OVERLAP` 5, `NONCOHORT_METHOD_LABEL` 5, `CROSSOVER_DOUBLE_COUNT` 4.

## Reducibility (item 3), summarised

| verdict | trials |
|---|---|
| `YES` — a non-overlapping set is nameable from the record alone | 42 |
| `PARTIAL` | 1 (NCT03363893) |
| `UNRESOLVED` | 2 (NCT03446040, NCT04033991) |

Across the 43 trials with a named set (42 `YES` + the 1 `PARTIAL`), the reduced sum equals the
registered enrollment **exactly** for 26 trials and falls below it for the other 17. **No trial in my
group has a reduced set that still exceeds its registered enrollment** — that is, wherever the record
settles the question, the whole excess is explained by re-counting, and none of it is left as an
unexplained registry inconsistency. The two `UNRESOLVED` trials are both cases where the record **states**
that participants are counted twice but never says how many, so no set can be named:

- **NCT03446040** — om3 populationDescription, verbatim: *"Participants who crossed over from part A1
  to Part B are accounted for in both arms."*
- **NCT04033991** — om6 populationDescription, verbatim: *"...received sunitinib as first-line
  treatment and/or axitinib as second-line treatment..."*, with 622 + 121 = 743 against 684 registered.

These two are the honest answer, not a gap in my reading: the excess is real and its cause is
recorded, but the record does not carry the information needed to remove it.

## One finding the parent should note

The excess in my group is dominated by **record-keeping form, not by disagreement about who was
enrolled**. Of the 45 trials, 16 owe some or all of their excess purely to the same cohort being
spelled differently in a second outcome measure, and a further 17 to a pooled or nested cohort being
summed with its own parts. Only three trials (`NCT03446040`, `NCT04033991`, plus the Module 4
crossover in `NCT03363893`) involve an overlap the sponsor itself declares in prose. This bears on
the selection rule's unit of analysis — a normalised group title is not a stable cohort identity
within a single study — but changing that rule is Job 2's, not mine.

## Per-trial adjudication

Ordered by excess, largest first. Every `om` index is the zero-based index into
`resultsSection.outcomeMeasuresModule.outcomeMeasures` of the cached record named in the trial's
`payload` / `payload_line`. Denominators are `denoms[units=="Participants"]` counts.

### NCT04680052 — excess 548 (selected 6 cohorts summing 1202 vs registered enrollment 654, ACTUAL)

- **Mechanism:** `NESTED_SUBSET`
- **Source:** `ctg_placebo_onc_2018_2021` line 178 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om23 pop: "The FL and MZL populations were combined for analysis into the Overall population". om22 FL-only groups (273/275) sit inside om23 (326/328); the MZL groups carry n=0. om23 sums to 654 = registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om22 `FL: Placebo + Rituximab + Lenalidomide` — n=275 — `NESTED_SUBSET`
  - om22 `FL: Tafasitamab + Rituximab + Lenalidomide` — n=273 — `NESTED_SUBSET`
  - om22 `MZL: Placebo + Rituximab + Lenalidomide` — n=0 — `NESTED_SUBSET`
  - om22 `MZL: Tafasitamab + Rituximab + Lenalidomide` — n=0 — `NESTED_SUBSET`
  - om23 `FL and MZL: Placebo + Rituximab + Lenalidomide` — n=328 — `COMPONENT_KEPT` **[kept]**
  - om23 `FL and MZL: Tafasitamab + Rituximab + Lenalidomide` — n=326 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **654** from om23 OG000-OG001 (326+328)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03096847 — excess 472 (selected 4 cohorts summing 974 vs registered enrollment 502, ACTUAL)

- **Mechanism:** `POOLED_EXPLICIT`
- **Source:** `ctg_results_bor_2014_2017` line 162 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om0 OG003 "Total" n=487 is exactly 307+26+154.
- **Selected cohorts (om index | denominator | role):**
  - om0 `Ribociclib + Letrozole Cohort A` — n=307 — `COMPONENT_KEPT` **[kept]**
  - om0 `Ribociclib + Letrozole Cohort B1` — n=26 — `COMPONENT_KEPT` **[kept]**
  - om0 `Ribociclib + Letrozole Cohort B2` — n=154 — `COMPONENT_KEPT` **[kept]**
  - om0 `Total` — n=487 — `POOLED_EXPLICIT`
- **Non-overlapping set:** YES — sum **487** from om0 OG000-OG002 (307+26+154)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04282109 — excess 423 (selected 16 cohorts summing 564 vs registered enrollment 141, ACTUAL)

- **Mechanism:** `CROSS_AXIS_DUPLICATE`
- **Source:** `ctg_results_bor_2018_2021` line 475 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Four complete partitions of the same 141 patients, each summing to exactly 141: arm (om2), PD-L1 CPS (om11), cisplatin-ineligibility group (om14), Karnofsky PS (om17).
- **Selected cohorts (om index | denominator | role):**
  - om2 `Arm 1` — n=93 — `COMPONENT_KEPT` **[kept]**
  - om2 `Arm 2` — n=48 — `COMPONENT_KEPT` **[kept]**
  - om11 `Arm 1 - CPS <1` — n=20 — `CROSS_AXIS_DUPLICATE`
  - om11 `Arm 1 - CPS >=1` — n=73 — `CROSS_AXIS_DUPLICATE`
  - om11 `Arm 2 - CPS <1` — n=11 — `CROSS_AXIS_DUPLICATE`
  - om11 `Arm 2 - CPS >=1` — n=37 — `CROSS_AXIS_DUPLICATE`
  - om14 `Arm 1 - Group 1` — n=25 — `CROSS_AXIS_DUPLICATE`
  - om14 `Arm 1 - Group 2` — n=53 — `CROSS_AXIS_DUPLICATE`
  - om14 `Arm 1 - Group 3` — n=15 — `CROSS_AXIS_DUPLICATE`
  - om14 `Arm 2 - Group 1` — n=13 — `CROSS_AXIS_DUPLICATE`
  - om14 `Arm 2 - Group 2` — n=27 — `CROSS_AXIS_DUPLICATE`
  - om14 `Arm 2 - Group 3` — n=8 — `CROSS_AXIS_DUPLICATE`
  - om17 `Arm 1 - Karnofsky-PS 70%` — n=36 — `CROSS_AXIS_DUPLICATE`
  - om17 `Arm 1 - Karnofsky-PS 80-100%` — n=57 — `CROSS_AXIS_DUPLICATE`
  - om17 `Arm 2 - Karnofsky-PS 70%` — n=16 — `CROSS_AXIS_DUPLICATE`
  - om17 `Arm 2 - Karnofsky-PS 80-100%` — n=32 — `CROSS_AXIS_DUPLICATE`
- **Non-overlapping set:** YES — sum **141** from om2 OG000-OG001 (93+48)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03195491 — excess 400 (selected 3 cohorts summing 800 vs registered enrollment 400, ACTUAL)

- **Mechanism:** `POOLED_UNFLAGGED`
- **Source:** `ctg_results_bor_2014_2017` line 597 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om7 OG002 "All Treated Participants" n=400 = 383+17 = registered enrollment; label is outside the rule pooled vocabulary so it was not flagged.
- **Selected cohorts (om index | denominator | role):**
  - om7 `All Treated Participants` — n=400 — `POOLED_UNFLAGGED`
  - om7 `HBV Participants` — n=17 — `COMPONENT_KEPT` **[kept]**
  - om7 `Non-HBV Participants` — n=383 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **400** from om7 OG000-OG001 (383+17)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03248492 — excess 360 (selected 5 cohorts summing 613 vs registered enrollment 253, ACTUAL)

- **Mechanism:** `NESTED_SUBSET+DUPLICATE_TITLE_VARIANT`
- **Source:** `ctg_results_bor_2014_2017` line 750 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Group descriptions state OG000 (Part 1 or 2a at 5.4 mg/kg, n=180) is contained in OG001 (Part 1 or 2a or 2b at 5.4 mg/kg, n=184). "Part 1 and Part 2a" (om0) and "Part 1 + Part 2a" (om3) are the same 180 patients under and/+ variants. 184+48+21=253=registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om0 `Part 1 + Part 2a + Part 2b: DS-8201a Low Dose` — n=184 — `COMPONENT_KEPT` **[kept]**
  - om0 `Part 1 and Part 2a: DS-8201a Low Dose` — n=180 — `NESTED_SUBSET`
  - om3 `Part 1 + Part 2a: DS-8201a Low Dose` — n=180 — `DUPLICATE_TITLE_VARIANT`
  - om3 `Part 1: DS-8201a High Dose` — n=21 — `COMPONENT_KEPT` **[kept]**
  - om3 `Part 1: DS-8201a Medium Dose` — n=48 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **253** from om0 OG001 (184) + om3 OG000 (48) + om3 OG001 (21)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03001882 — excess 301 (selected 10 cohorts summing 531 vs registered enrollment 230, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT+POOLED_UNFLAGGED+CROSS_AXIS_DUPLICATE`
- **Source:** `ctg_results_bor_2014_2017` line 250 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om0/om1 repeat the same PD-L1 subgroups with a space before the plus sign; om3 is the only OM whose group denominators sum to registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om0 `PART 1: Not Evaluable/Indeterminate PD-L1 Status` — n=0 — `COMPONENT_KEPT` **[kept]**
  - om0 `PART 1: PD-L1 + Status` — n=19 — `DUPLICATE_TITLE_VARIANT`
  - om0 `PART 1: PD-L1- Status` — n=16 — `COMPONENT_KEPT` **[kept]**
  - om0 `PART 2: PD-L1+ Status` — n=39 — `CROSS_AXIS_DUPLICATE`
  - om0 `PART 2: PD-L1- Status` — n=62 — `CROSS_AXIS_DUPLICATE`
  - om1 `PART 1: PD-L1+ Status` — n=19 — `COMPONENT_KEPT` **[kept]**
  - om1 `PART 2: PD-L1 + Status` — n=39 — `DUPLICATE_TITLE_VARIANT`
  - om3 `PART 2: PD-L1 Status Independent` — n=170 — `COMPONENT_KEPT` **[kept]**
  - om12 `PART 1` — n=36 — `POOLED_UNFLAGGED`
  - om12 `PART 2` — n=131 — `POOLED_UNFLAGGED`
- **Non-overlapping set:** YES — sum **230** from om3 OG000-OG003 (31+28+1+170)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03778229 — excess 275 (selected 6 cohorts summing 642 vs registered enrollment 367, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT+NESTED_SUBSET`
- **Source:** `ctg_placebo_onc_2018_2021` line 63 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om1 "Savo 300 mg QD + Osi" and om15 "300 mg QD + Osi" are the same 196 patients under two labels. om0 "Savo 300 mg BID + Osi" n=80 is the FISH-selected target population inside the 101-patient BID safety analysis set (om15).
- **Selected cohorts (om index | denominator | role):**
  - om0 `Savo 300 mg BID + Osi` — n=80 — `NESTED_SUBSET`
  - om1 `Savo 300 mg QD + Osi` — n=196 — `DUPLICATE_TITLE_VARIANT`
  - om9 `Savo 300 mg BID Monotherapy` — n=25 — `COMPONENT_KEPT` **[kept]**
  - om15 `300 mg BID + Osi` — n=101 — `COMPONENT_KEPT` **[kept]**
  - om15 `300 mg QD + Osi` — n=196 — `COMPONENT_KEPT` **[kept]**
  - om15 `Savo 600 mg QD + Osi` — n=44 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **366** from om15 OG000-OG002 (196+101+44) + om9 OG001 (25)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03176238 — excess 235 (selected 3 cohorts summing 470 vs registered enrollment 235, ACTUAL)

- **Mechanism:** `POOLED_EXPLICIT`
- **Source:** `ctg_results_bor_2010_2013` line 119 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om2 OG002 "Total" n=235 equals 199+36 and equals registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om2 `Asian Everolimus + Exemestane` — n=199 — `COMPONENT_KEPT` **[kept]**
  - om2 `Non-Asian Everolimus + Exemestane` — n=36 — `COMPONENT_KEPT` **[kept]**
  - om2 `Total` — n=235 — `POOLED_EXPLICIT`
- **Non-overlapping set:** YES — sum **235** from om2 OG000-OG001 (199+36)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03468426 — excess 224 (selected 9 cohorts summing 476 vs registered enrollment 252, ACTUAL)

- **Mechanism:** `POOLED_UNFLAGGED`
- **Source:** `ctg_results_bor_2018_2021` line 427 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om28 OG008 "Part 2 - total" (description "All patients in part 2") n=238 = 42+40+31+31+32+30+31+1. Lower-case "total" is outside the pooled vocabulary.
- **Selected cohorts (om index | denominator | role):**
  - om28 `Part 2 - Cohort A, 2nd line NSCLC` — n=42 — `COMPONENT_KEPT` **[kept]**
  - om28 `Part 2 - Cohort B, 3rd line NSCLC` — n=40 — `COMPONENT_KEPT` **[kept]**
  - om28 `Part 2 - Cohort C, SCLC` — n=31 — `COMPONENT_KEPT` **[kept]**
  - om28 `Part 2 - Cohort D, glioblastoma` — n=31 — `COMPONENT_KEPT` **[kept]**
  - om28 `Part 2 - Cohort E, Melanoma` — n=32 — `COMPONENT_KEPT` **[kept]**
  - om28 `Part 2 - Cohort F, 2nd line Hepatocellular Carcinoma` — n=30 — `COMPONENT_KEPT` **[kept]**
  - om28 `Part 2 - Cohort G, 1st line Hepatocellular Carcinoma` — n=31 — `COMPONENT_KEPT` **[kept]**
  - om28 `Part 2 - Cohort H, 2nd line HCC - atezolizumab in combination with bevacizumab failures` — n=1 — `COMPONENT_KEPT` **[kept]**
  - om28 `Part 2 - total` — n=238 — `POOLED_UNFLAGGED`
- **Non-overlapping set:** YES — sum **238** from om28 OG000-OG007
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04436107 — excess 160 (selected 14 cohorts summing 226 vs registered enrollment 66, ACTUAL)

- **Mechanism:** `POOLED_UNFLAGGED+CROSS_AXIS_DUPLICATE`
- **Source:** `ctg_results_bor_2018_2021` line 418 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** "Part 1+2 ... 25 mg" (description: all participants who received the RP2D) n=50 pools Part 1 25 mg (11) and Part 2 25 mg (39). om25/om27 (IHC subtype) and om26/om28 (gene-expression subtype) are two further partitions of the same patients. Dose groups + Part 2 = 66 = registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om1 `Part 1+2: Zanubrutinib + Lenalidomide 25 mg` — n=50 — `POOLED_UNFLAGGED`
  - om1 `Part 2: Zanubrutinib + Lenalidomide 25 mg` — n=39 — `COMPONENT_KEPT` **[kept]**
  - om2 `Part 1: Zanubrutinib + Lenalidomide 15 mg` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om2 `Part 1: Zanubrutinib + Lenalidomide 20 mg` — n=10 — `COMPONENT_KEPT` **[kept]**
  - om2 `Part 1: Zanubrutinib + Lenalidomide 25 mg` — n=11 — `COMPONENT_KEPT` **[kept]**
  - om25 `GCB Subtype: Zanubrutinib + Lenalidomide 15 mg` — n=3 — `CROSS_AXIS_DUPLICATE`
  - om25 `GCB Subtype: Zanubrutinib + Lenalidomide 20 mg` — n=4 — `CROSS_AXIS_DUPLICATE`
  - om25 `Non-GCB Subtype: Zanubrutinib + Lenalidomide 15 mg` — n=3 — `CROSS_AXIS_DUPLICATE`
  - om25 `Non-GCB Subtype: Zanubrutinib + Lenalidomide 20 mg` — n=6 — `CROSS_AXIS_DUPLICATE`
  - om26 `ABC Subtype: Zanubrutinib + Lenalidomide 15 mg` — n=1 — `CROSS_AXIS_DUPLICATE`
  - om26 `ABC Subtype: Zanubrutinib + Lenalidomide 20 mg` — n=8 — `CROSS_AXIS_DUPLICATE`
  - om27 `GCB Subtype: Zanubrutinib + Lenalidomide 25 mg` — n=16 — `CROSS_AXIS_DUPLICATE`
  - om27 `Non-GCB Subtype: Zanubrutinib + Lenalidomide 25 mg` — n=34 — `CROSS_AXIS_DUPLICATE`
  - om28 `ABC Subtype: Zanubrutinib + Lenalidomide 25 mg` — n=35 — `CROSS_AXIS_DUPLICATE`
- **Non-overlapping set:** YES — sum **66** from om2 OG000-OG002 (6+10+11) + om1 OG000 (39)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04280081 — excess 130 (selected 9 cohorts summing 207 vs registered enrollment 77, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT+NESTED_SUBSET`
- **Source:** `ctg_results_bor_2018_2021` line 308 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Three disease groups appear three times: om1 "Enrolled Population" (47/1/29 = 77 = registered enrollment), om5 the same enrolled population under short labels ("All NSCLC"/"All TC"/"All MTC", same 47/1/29), and om0 the "Primary Analysis Set" of centrally confirmed participants (26/1/26) nested inside them.
- **Selected cohorts (om index | denominator | role):**
  - om0 `RET Fusion Positive Non-small Cell Lung Cancer (NSCLC) Cohort 1` — n=26 — `NESTED_SUBSET`
  - om0 `RET Fusion Positive Thyroid Cancer (TC) Cohort 1` — n=1 — `NESTED_SUBSET`
  - om0 `RET Mutant Medullary Thyroid Cancer (MTC) Cohort 2` — n=26 — `NESTED_SUBSET`
  - om1 `Medullary Thyroid Cancer (All MTC)` — n=29 — `COMPONENT_KEPT` **[kept]**
  - om1 `Non-small Cell Lung Cancer (All NSCLC)` — n=47 — `COMPONENT_KEPT` **[kept]**
  - om1 `Thyroid Cancer (All TC)` — n=1 — `COMPONENT_KEPT` **[kept]**
  - om5 `All MTC` — n=29 — `DUPLICATE_TITLE_VARIANT`
  - om5 `All NSCLC` — n=47 — `DUPLICATE_TITLE_VARIANT`
  - om5 `All TC` — n=1 — `DUPLICATE_TITLE_VARIANT`
- **Non-overlapping set:** YES — sum **77** from om1 OG000-OG002 (47+1+29)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03773302 — excess 126 (selected 6 cohorts summing 174 vs registered enrollment 48, ACTUAL)

- **Mechanism:** `NONCOHORT_METHOD_LABEL`
- **Source:** `ctg_results_bor_2018_2021` line 546 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** The results-group titles name the ASSESSMENT METHOD, not a patient cohort: om3 OG000/OG001 both have description "Infigratinib" (n=29) and OG002/OG003 both "Gemcitabine + Cisplatin" (n=19). Casefold normalisation merges "By"/"by", leaving 2 keys per OM x 3 OMs = 6 keys, all at n=29. The arms are recoverable only from the group description field; 29+19=48=registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om3 `ORR By Central Assessment` — n=29 — `COMPONENT_KEPT` **[kept]**
  - om3 `ORR By Investigator Assessment` — n=29 — `NONCOHORT_METHOD_LABEL`
  - om4 `BOR By Central Assessment` — n=29 — `NONCOHORT_METHOD_LABEL`
  - om4 `BOR By Investigator Assessment` — n=29 — `NONCOHORT_METHOD_LABEL`
  - om6 `DCR By Central Assessment` — n=29 — `NONCOHORT_METHOD_LABEL`
  - om6 `DCR By Investigator Assessment` — n=29 — `NONCOHORT_METHOD_LABEL`
- **Non-overlapping set:** YES — sum **48** from om3 OG000 (Infigratinib, 29) + om3 OG002 (Gemcitabine + Cisplatin, 19)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03410693 — excess 125 (selected 4 cohorts summing 300 vs registered enrollment 175, ACTUAL)

- **Mechanism:** `NESTED_SUBSET`
- **Source:** `ctg_results_bor_2018_2021` line 135 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Same om0 carries the two randomised arms (87+88=175=registered enrollment) and their FGFR wild-type subsets (62, 63).
- **Selected cohorts (om index | denominator | role):**
  - om0 `Chemotherapy_Overall Population` — n=88 — `COMPONENT_KEPT` **[kept]**
  - om0 `Chemotherapy_WT Population` — n=63 — `NESTED_SUBSET`
  - om0 `Rogaratinib (BAY1163877)_Overall Population` — n=87 — `COMPONENT_KEPT` **[kept]**
  - om0 `Rogaratinib_WT Population` — n=62 — `NESTED_SUBSET`
- **Non-overlapping set:** YES — sum **175** from om0 OG000-OG001 (87+88)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04363801 — excess 121 (selected 9 cohorts summing 368 vs registered enrollment 247, ACTUAL)

- **Mechanism:** `NESTED_SUBSET`
- **Source:** `ctg_results_bor_2018_2021` line 335 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om22 re-reports Part C as an analysed subset (49/51) and a DKK1-high subset (14/16) of the same randomised groups reported at 85/85 in om18.
- **Selected cohorts (om index | denominator | role):**
  - om2 `Part A First Line Treatment` — n=22 — `COMPONENT_KEPT` **[kept]**
  - om3 `Part B1 Second Line Treatment` — n=22 — `COMPONENT_KEPT` **[kept]**
  - om3 `Part B2 Second Line Treatment` — n=24 — `COMPONENT_KEPT` **[kept]**
  - om18 `Part C Control First Line Treatment` — n=85 — `COMPONENT_KEPT` **[kept]**
  - om18 `Part C Experimental First Line Treatment` — n=85 — `COMPONENT_KEPT` **[kept]**
  - om22 `ORR All Patients, Part C Control` — n=49 — `NESTED_SUBSET`
  - om22 `ORR All Patients, Part C Experimental` — n=51 — `NESTED_SUBSET`
  - om22 `ORR DKK1-high Patient, Part C Control` — n=14 — `NESTED_SUBSET`
  - om22 `ORR DKK1-high Patients, Part C Experimental` — n=16 — `NESTED_SUBSET`
- **Non-overlapping set:** YES — sum **238** from om2 (22) + om3 (22+24) + om18 OG000-OG001 (85+85)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03006926 — excess 96 (selected 2 cohorts summing 200 vs registered enrollment 104, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT`
- **Source:** `ctg_results_bor_2014_2017` line 819 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Single cohort of 100; hyphen vs space in "HCC-1L"/"HCC 1L" makes two keys.
- **Selected cohorts (om index | denominator | role):**
  - om3 `HCC-1L: Lenvatinib 12 mg or 8 mg+ Pembrolizumab 200 mg` — n=100 — `COMPONENT_KEPT` **[kept]**
  - om6 `HCC 1L: Lenvatinib 12 mg or 8 mg+ Pembrolizumab 200 mg` — n=100 — `DUPLICATE_TITLE_VARIANT`
- **Non-overlapping set:** YES — sum **100** from om3 OG000
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03480646 — excess 93 (selected 12 cohorts summing 268 vs registered enrollment 175, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT+NESTED_SUBSET`
- **Source:** `ctg_results_bor_2014_2017` line 737 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om3 relabels three om0 Phase 2 groups ("Phase 2 Randomized Enza Contro" vs "Phase 2 Randomized Controlled: Enza" etc.). The crossover-period group is Arm-control patients recounted after crossover.
- **Selected cohorts (om index | denominator | role):**
  - om0 `Phase 1b Dose Escalation: CPI-1205 400 mg BID + Cobi + Abi/Pred` — n=7 — `COMPONENT_KEPT` **[kept]**
  - om0 `Phase 1b Dose Escalation: CPI-1205 400 mg BID + Cobi + Enza` — n=5 — `COMPONENT_KEPT` **[kept]**
  - om0 `Phase 1b Dose Escalation: CPI-1205 800 mg TID + Enza` — n=9 — `COMPONENT_KEPT` **[kept]**
  - om0 `Phase 1b Dose Escalation: CPI-1205 800 mg TID +Abi/Pred` — n=11 — `COMPONENT_KEPT` **[kept]**
  - om0 `Phase 1b HPEC: Heavily Pretreated Expansion Cohort CPI-1205 800 mg TID + Enza` — n=25 — `COMPONENT_KEPT` **[kept]**
  - om0 `Phase 2 Randomized Controlled: Enza` — n=35 — `COMPONENT_KEPT` **[kept]**
  - om0 `Phase 2 Randomized Crossover Period` — n=12 — `NESTED_SUBSET`
  - om0 `Phase 2 Randomized Experimental: CPI-1205 at RP2D (800 mg TID) + Enza` — n=38 — `COMPONENT_KEPT` **[kept]**
  - om0 `Phase 2 Single Arm CPI-1205 at RP2D (800 mg TID) + Abi/Pred` — n=28 — `COMPONENT_KEPT` **[kept]**
  - om3 `Phase 2 Randomized Combination With Enza` — n=35 — `DUPLICATE_TITLE_VARIANT`
  - om3 `Phase 2 Randomized Enza Contro` — n=35 — `DUPLICATE_TITLE_VARIANT`
  - om3 `Phase 2 Single Arm CPI-1205 +Abi/Pred` — n=28 — `DUPLICATE_TITLE_VARIANT`
- **Non-overlapping set:** YES — sum **158** from om0 OG000-OG006, OG008 (crossover group excluded)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03284957 — excess 89 (selected 18 cohorts summing 225 vs registered enrollment 136, ACTUAL)

- **Mechanism:** `POOLED_UNFLAGGED`
- **Source:** `ctg_results_bor_2014_2017` line 32 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om10 populationDescription states the analysis was run on a pooled population [Part A and B; Parts C and D]; those two pooled groups (59, 38) re-count om4 part/dose groups.
- **Selected cohorts (om index | denominator | role):**
  - om1 `Part B: Amcenestrant 400 mg` — n=46 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part A: Amcenestrant 150 mg` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part A: Amcenestrant 20 mg` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part A: Amcenestrant 200 mg` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part A: Amcenestrant 300 mg BID` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part A: Amcenestrant 400 mg` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part A: Amcenestrant 600 mg` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part C: Amcenestrant 200 mg + Palbociclib 125 mg` — n=9 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part C: Amcenestrant 400 mg + Palbociclib 125 mg` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part D: Amcenestrant 200 mg + Palbociclib 125 mg` — n=29 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part F: Amcenestrant 200 mg + Alpelisib 300 mg` — n=7 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part H: Amcenestrant 200 mg + Everolimus 10 mg` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part H: Amcenestrant 200 mg + Everolimus 5 mg` — n=2 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part I: Amcenestrant 200 mg + Everolimus 10 mg` — n=1 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part J: Amcenestrant 200 mg + Abemaciclib 100 mg BID` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om4 `Part J: Amcenestrant 200 mg + Abemaciclib 150 mg BID` — n=2 — `COMPONENT_KEPT` **[kept]**
  - om10 `Part A and B: Amcenestrant (Dose >20 mg)` — n=59 — `POOLED_UNFLAGGED`
  - om10 `Parts C and D: Amcenestrant 200 mg + Palbociclib 125 mg` — n=38 — `POOLED_UNFLAGGED`
- **Non-overlapping set:** YES — sum **128** from om1 OG000 (46) + om4 OG000-OG005,OG007-OG015 (82)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04194944 — excess 83 (selected 3 cohorts summing 344 vs registered enrollment 261, ACTUAL)

- **Mechanism:** `NESTED_SUBSET`
- **Source:** `ctg_results_bor_2018_2021` line 613 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om2 group is the ITT-Pembrolizumab stratum (n=83) of the same control arm whose full ITT is om7 OG001 (n=102). om7 sums to 261 = registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om2 `Pemetrexed and Platinum With Pembrolizumab (TRT B)` — n=83 — `NESTED_SUBSET`
  - om7 `Pemetrexed and Platinum With or Without Pembrolizumab (TRT B)` — n=102 — `COMPONENT_KEPT` **[kept]**
  - om7 `Selpercatinib (TRT A)` — n=159 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **261** from om7 OG000-OG001 (159+102)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03269136 — excess 73 (selected 21 cohorts summing 174 vs registered enrollment 101, ACTUAL)

- **Mechanism:** `POOLED_UNFLAGGED`
- **Source:** `ctg_results_bor_2014_2017` line 824 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Three route/part subtotals: Total IV 23 = 2+3+2+3+2+5+6; Total SC 30 = 6+4+4+4+6+6; Part 1.1 Total SC 20 = 7+13. Dose-level groups + Part 2A = 101 = registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om1 `Part 2A: PF-06863135 SC` — n=15 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1.1: PF-06863135 Priming Cohort Q1W SC` — n=7 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1.1: PF-06863135 Priming Cohort Q2W SC` — n=13 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1.1: PF-06863135 Total SC` — n=20 — `POOLED_UNFLAGGED`
  - om7 `Part 1: PF-06863135 0.1 mcg/kg IV` — n=2 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 0.3 mcg/kg IV` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 1 mcg/kg IV` — n=2 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 10 mcg/kg IV` — n=2 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 1000 mcg/kg SC` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 130 mcg/kg SC` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 215 mcg/kg SC` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 3 mcg/kg IV` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 30 mcg/kg IV` — n=5 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 360 mcg/kg SC` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 50 mcg/kg IV` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 600 mcg/kg SC` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 80 mcg/kg SC` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1: PF-06863135 Total IV` — n=23 — `POOLED_UNFLAGGED`
  - om7 `Part 1: PF-06863135 Total SC` — n=30 — `POOLED_UNFLAGGED`
  - om7 `Part 1C: PF-06863135 + Lenalidomide SC` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om7 `Part 1D: PF-06863135 + Pomalidomide SC` — n=9 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **101** from om7 dose-level groups (86) + om1 OG000 (15)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04287868 — excess 73 (selected 4 cohorts summing 124 vs registered enrollment 51, ACTUAL)

- **Mechanism:** `POOLED_EXPLICIT+NESTED_SUBSET`
- **Source:** `ctg_results_bor_2018_2021` line 155 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Strictly nested chain inside one outcome measure, stated in the group descriptions: All Participants N=50 (47 C1 + 3 C2) > HPV16+ N=37 > {ICB-naive 8, ICB-resistant 29}. The only complete non-overlapping cover in the record is the 50.
- **Selected cohorts (om index | denominator | role):**
  - om0 `All Participants` — n=50 — `COMPONENT_KEPT` **[kept]**
  - om0 `Human Papillomavirus 16 Tumors (HPV-16+), Immune Checkpoint Blockade (ICB) - Naive` — n=8 — `NESTED_SUBSET`
  - om0 `Human Papillomavirus 16 Tumors (HPV-16+), Immune Checkpoint Blockade (ICB) - Resistant` — n=29 — `NESTED_SUBSET`
  - om0 `Participants With Human Papillomavirus 16 (HPV16+) Tumors` — n=37 — `NESTED_SUBSET`
- **Non-overlapping set:** YES — sum **50** from om0 OG000
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03200717 — excess 62 (selected 3 cohorts summing 124 vs registered enrollment 62, ACTUAL)

- **Mechanism:** `POOLED_EXPLICIT`
- **Source:** `ctg_results_bor_2014_2017` line 728 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om1 OG002 "All Participants" n=62 = 47+15 = registered enrollment; flagged pooled by the rule but still summed.
- **Selected cohorts (om index | denominator | role):**
  - om1 `All Participants` — n=62 — `POOLED_EXPLICIT`
  - om1 `Pazopanib- 2nd Line` — n=47 — `COMPONENT_KEPT` **[kept]**
  - om1 `Pazopanib- 3rd Line` — n=15 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **62** from om1 OG000-OG001 (47+15)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03329690 — excess 60 (selected 6 cohorts summing 293 vs registered enrollment 233, ACTUAL)

- **Mechanism:** `POOLED_UNFLAGGED`
- **Source:** `ctg_results_bor_2014_2017` line 640 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om0 OG003 "Physician's Choice Overall" n=62 = irinotecan 55 + paclitaxel 7.
- **Selected cohorts (om index | denominator | role):**
  - om0 `DS-8201a` — n=126 — `COMPONENT_KEPT` **[kept]**
  - om0 `Physician's Choice Irinotecan` — n=55 — `COMPONENT_KEPT` **[kept]**
  - om0 `Physician's Choice Overall` — n=62 — `POOLED_UNFLAGGED`
  - om0 `Physician's Choice Paclitaxel` — n=7 — `COMPONENT_KEPT` **[kept]**
  - om6 `Exploratory: Naïve HER2 IHC 1+, DS-8201a` — n=22 — `COMPONENT_KEPT` **[kept]**
  - om6 `Exploratory: Naïve HER2 IHC 2+/ISH-, DS-8201a` — n=21 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **231** from om0 OG000-OG002 (126+55+7) + om6 OG000-OG001 (21+22)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04033991 — excess 59 (selected 2 cohorts summing 743 vs registered enrollment 684, ACTUAL)

- **Mechanism:** `MULTILINE_DOUBLE_COUNT`
- **Source:** `ctg_results_bor_2018_2021` line 488 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Retrospective chart review; om6 pop: participants "received sunitinib as first-line treatment and/or axitinib as second-line treatment". A patient who received both is counted in both groups. 622+121=743 vs 684 registered; the record never states how many received both, so the 59 cannot be assigned.
- **Selected cohorts (om index | denominator | role):**
  - om6 `Participants With mRCC and/or aRCC: First Line Sunitinib Treatment` — n=622 — `UNRESOLVED_DECLARED_OVERLAP`
  - om6 `Participants With mRCC and/or aRCC: Second Line Axitinib Treatment` — n=121 — `UNRESOLVED_DECLARED_OVERLAP`
- **Non-overlapping set:** `UNRESOLVED` — see mechanism note above
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03074318 — excess 56 (selected 9 cohorts summing 91 vs registered enrollment 35, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT+POOLED_UNFLAGGED`
- **Source:** `ctg_results_bor_2014_2017` line 386 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om6 repeats om5 with comma replaced by dash. om1 group is "Phase 2 plus subjects treated at the RP2D" - a pool over the om5 groups.
- **Selected cohorts (om index | denominator | role):**
  - om1 `Treatment (Avelumab, Trabectedin)` — n=23 — `POOLED_UNFLAGGED`
  - om5 `Phase 1, 1.0 mg/m^2 Trabectedin` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om5 `Phase 1, 1.2 mg/m^2 Trabectedin` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om5 `Phase 1, 1.5 mg/m^2 Trabectedin` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om5 `Phase 2, 1.0 mg/m^2 Trabectedin` — n=16 — `COMPONENT_KEPT` **[kept]**
  - om6 `Phase 1 - 1.0 mg/m^2 Trabectedin` — n=6 — `DUPLICATE_TITLE_VARIANT`
  - om6 `Phase 1 - 1.2 mg/m^2 Trabectedin` — n=6 — `DUPLICATE_TITLE_VARIANT`
  - om6 `Phase 1 - 1.5 mg/m^2 Trabectedin` — n=6 — `DUPLICATE_TITLE_VARIANT`
  - om6 `Phase 2 - 1.0 mg/m^2 Trabectedin` — n=16 — `DUPLICATE_TITLE_VARIANT`
- **Non-overlapping set:** YES — sum **34** from om5 OG000-OG003 (6+6+6+16)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03481556 — excess 56 (selected 8 cohorts summing 112 vs registered enrollment 56, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT`
- **Source:** `ctg_results_bor_2018_2021` line 57 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om1 and om9 are the same four cohorts (15/8/6/27) under two naming conventions; either OM alone sums to 56 = registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om1 `Regimen A - Melflufen 30mg + Bortezomib + Dexamethasone` — n=15 — `COMPONENT_KEPT` **[kept]**
  - om1 `Regimen A - Melflufen 40mg + Bortezomib + Dexamethasone` — n=8 — `COMPONENT_KEPT` **[kept]**
  - om1 `Regimen B - Melflufen 30mg + Daratumumab + Dexamethasone` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om1 `Regimen B - Melflufen 40mg + Daratumumab + Dexamethasone` — n=27 — `COMPONENT_KEPT` **[kept]**
  - om9 `A (Melflufen+Bortezomib+Dex) 30 mg` — n=15 — `DUPLICATE_TITLE_VARIANT`
  - om9 `A (Melflufen+Bortezomib+Dex) 40 mg` — n=8 — `DUPLICATE_TITLE_VARIANT`
  - om9 `B (Melflufen+Daratumumab+Dex) 30 mg` — n=6 — `DUPLICATE_TITLE_VARIANT`
  - om9 `B (Melflufen+Daratumumab+Dex) 40 mg` — n=27 — `DUPLICATE_TITLE_VARIANT`
- **Non-overlapping set:** YES — sum **56** from om1 OG000-OG003 (15+8+6+27)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04750824 — excess 52 (selected 4 cohorts summing 162 vs registered enrollment 110, ACTUAL)

- **Mechanism:** `NESTED_SUBSET`
- **Source:** `ctg_results_bor_2018_2021` line 354 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** One outcome measure holds both the full treatment groups (72+38=110=registered enrollment) and their first-line subsets (16, 36).
- **Selected cohorts (om index | denominator | role):**
  - om0 `All Afatinib Patients` — n=72 — `COMPONENT_KEPT` **[kept]**
  - om0 `All Non-afatinib (Other Systemic Therapies)` — n=38 — `COMPONENT_KEPT` **[kept]**
  - om0 `First Line Afatinib Patients` — n=16 — `NESTED_SUBSET`
  - om0 `First Line Non-afatinib Patients` — n=36 — `NESTED_SUBSET`
- **Non-overlapping set:** YES — sum **110** from om0 OG000-OG001 (72+38)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03410108 — excess 47 (selected 2 cohorts summing 151 vs registered enrollment 104, ACTUAL)

- **Mechanism:** `NESTED_SUBSET`
- **Source:** `ctg_results_bor_2018_2021` line 217 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om0 pop: "FAS-P ... is a subset of the FAS ... first 47 participants in the Main Cohort"; om2 FAS n=104 = registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om0 `Refractory Expansion Part: Main Cohort` — n=47 — `NESTED_SUBSET`
  - om2 `Brigatinib 90 mg/180 mg` — n=104 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **104** from om2 OG000
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03774082 — excess 44 (selected 4 cohorts summing 90 vs registered enrollment 46, ACTUAL)

- **Mechanism:** `POOLED_EXPLICIT`
- **Source:** `ctg_results_bor_2018_2021` line 266 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Age-band partition plus its own "All Participants" pool (45 = 22+16+7) inside one outcome measure.
- **Selected cohorts (om index | denominator | role):**
  - om0 `All Participants` — n=45 — `POOLED_EXPLICIT`
  - om0 `≥ 12y - < 18y RUX 10mg BID (Group 1)` — n=22 — `COMPONENT_KEPT` **[kept]**
  - om0 `≥ 2y - < 6y RUX 4mg/m2 BID (Group 3)` — n=7 — `COMPONENT_KEPT` **[kept]**
  - om0 `≥ 6y - < 12y RUX 5mg BID (Group 2)` — n=16 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **45** from om0 OG000-OG002 (22+16+7)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03729596 — excess 41 (selected 11 cohorts summing 184 vs registered enrollment 143, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT`
- **Source:** `ctg_results_bor_2018_2021` line 18 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om7 "mCRPC" (description: "Participants in cohort expansion with metastatic castration-resistant prostate cancer") n=41 is om3 "mCRPC Expansion" n=41. om3 sums to 143 = registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om3 `Cohort 1` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om3 `Cohort 2` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om3 `Cohort 3` — n=7 — `COMPONENT_KEPT` **[kept]**
  - om3 `Cohort 4` — n=7 — `COMPONENT_KEPT` **[kept]**
  - om3 `Cohort 5` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om3 `Melanoma Expansion` — n=21 — `COMPONENT_KEPT` **[kept]**
  - om3 `NSCLC Expansion` — n=21 — `COMPONENT_KEPT` **[kept]**
  - om3 `SCCHN Expansion` — n=13 — `COMPONENT_KEPT` **[kept]**
  - om3 `TNBC Expansion` — n=18 — `COMPONENT_KEPT` **[kept]**
  - om3 `mCRPC Expansion` — n=41 — `COMPONENT_KEPT` **[kept]**
  - om7 `mCRPC` — n=41 — `DUPLICATE_TITLE_VARIANT`
- **Non-overlapping set:** YES — sum **143** from om3 OG000-OG009
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03400176 — excess 39 (selected 9 cohorts summing 78 vs registered enrollment 39, ACTUAL)

- **Mechanism:** `POOLED_EXPLICIT`
- **Source:** `ctg_results_bor_2018_2021` line 334 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** "All Patients Expansion" 24 = 19+1+4; "All Patients Escalation" 15 = 4+3+4+4; components sum to 39 = registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om7 `All Patients Expansion` — n=24 — `POOLED_EXPLICIT`
  - om7 `VAY736 3mg/kg Q2W Arm A + Ibrutinib 420mg` — n=19 — `COMPONENT_KEPT` **[kept]**
  - om7 `VAY736 3mg/kg Q2W Arm B + Ibrutinib 280mg` — n=1 — `COMPONENT_KEPT` **[kept]**
  - om7 `VAY736 3mg/kg Q2W Arm B + Ibrutinib 420mg` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om9 `All Patients Escalation` — n=15 — `POOLED_EXPLICIT`
  - om9 `VAY736 0.3mg/kg Q2W + Ibrutinib 420mg` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om9 `VAY736 1mg/kg Q2W + Ibrutinib 420mg` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om9 `VAY736 3mg/kg Q2W + Ibrutinib 420mg` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om9 `VAY736 9mg/kg Q2W + Ibrutinib 420mg` — n=4 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **39** from om7 OG000-OG002 (19+1+4) + om9 OG000-OG003 (4+3+4+4)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03363893 — excess 37 (selected 22 cohorts summing 161 vs registered enrollment 124, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT+CROSSOVER_DOUBLE_COUNT`
- **Source:** `ctg_results_bor_2014_2017` line 436 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om5 pop: "Module 4-120mg OD Fed, ... 360mg OD Fasted are not reported ... The BOR for these patients are reported under the continuous dosing results" - Module 4 is a fed/fasted crossover, so om7 counts the same Module 4 patients in fed, fasted and continuous groups. om7 alone sums to 138 > 124 registered.
- **Selected cohorts (om index | denominator | role):**
  - om5 `Module 1 Part A-Cohort 3 480 mg OD` — n=2 — `COMPONENT_KEPT` **[kept]**
  - om5 `Module 2 Part ACT7001 240 mg OD +Fulvestrant (Cohort 1)` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om5 `Module 4 240 mg OD Continuous Dosing` — n=8 — `COMPONENT_KEPT` **[kept]**
  - om5 `Module 4 360 mg OD Continuous Dosing` — n=7 — `COMPONENT_KEPT` **[kept]**
  - om5 `Module 4-120mg OD Fed` — n=0 — `COMPONENT_KEPT` **[kept]**
  - om7 `Module 1 Part A Paired Biopsy Breast Cancer Expansion Cohort-240mg` — n=5 — `COMPONENT_KEPT` **[kept]**
  - om7 `Module 1 Part A Paired Biopsy Breast Cancer Expansion Cohort-360mg` — n=5 — `COMPONENT_KEPT` **[kept]**
  - om7 `Module 1 Part A-Cohort 1 120mg OD` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om7 `Module 1 Part A-Cohort 2 240mg OD` — n=5 — `COMPONENT_KEPT` **[kept]**
  - om7 `Module 1 Part A-Cohort 3 480mg OD` — n=2 — `DUPLICATE_TITLE_VARIANT`
  - om7 `Module 1 Part A-Cohort 4 360mg OD` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om7 `Module 1 Part A-Cohort 5 180mg BID` — n=7 — `COMPONENT_KEPT` **[kept]**
  - om7 `Module 1 Part B-1 Triple-negative Breast Cancer (TNBC) Expansion` — n=23 — `COMPONENT_KEPT` **[kept]**
  - om7 `Module 1 Part B-2 Castrate Resistant Prostate Cancer (CRPC) Expansion` — n=11 — `COMPONENT_KEPT` **[kept]**
  - om7 `Module 2 Part ACT7001 240 mg OD + Fulvestrant (Cohort 1)` — n=6 — `DUPLICATE_TITLE_VARIANT`
  - om7 `Module 2 Part ACT7001 360 mg OD + Fulvestrant (Cohort 2)` — n=19 — `COMPONENT_KEPT` **[kept]**
  - om7 `Module 4 120mg OD Fasted` — n=8 — `CROSSOVER_DOUBLE_COUNT`
  - om7 `Module 4 120mg OD Fed` — n=6 — `CROSSOVER_DOUBLE_COUNT`
  - om7 `Module 4 240mg OD Continuous Dosing` — n=8 — `DUPLICATE_TITLE_VARIANT`
  - om7 `Module 4 360mg OD Continous Dosing` — n=7 — `DUPLICATE_TITLE_VARIANT`
  - om7 `Module 4 360mg OD Fasted` — n=7 — `CROSSOVER_DOUBLE_COUNT`
  - om7 `Module 4 360mg OD Fed` — n=7 — `CROSSOVER_DOUBLE_COUNT`
- **Non-overlapping set:** PARTIAL — sum **110** from om5 OG000-OG016 (fed/fasted groups reported as 0 there)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT05228470 — excess 37 (selected 3 cohorts summing 76 vs registered enrollment 39, ACTUAL)

- **Mechanism:** `POOLED_UNFLAGGED`
- **Source:** `ctg_results_bor_2018_2021` line 145 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om1 OG002 "Phase 1b + Phase 2" n=38 = 8+30 in the same outcome measure; label outside the pooled vocabulary.
- **Selected cohorts (om index | denominator | role):**
  - om1 `Phase 1b` — n=8 — `COMPONENT_KEPT` **[kept]**
  - om1 `Phase 1b + Phase 2` — n=38 — `POOLED_UNFLAGGED`
  - om1 `Phase 2` — n=30 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **38** from om1 OG000-OG001 (8+30)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04677595 — excess 34 (selected 6 cohorts summing 70 vs registered enrollment 36, ACTUAL)

- **Mechanism:** `CROSS_AXIS_DUPLICATE`
- **Source:** `ctg_results_bor_2018_2021` line 149 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om12 re-partitions the same two cohorts by baseline ctDNA MET-mutation status (8+6 and 11+9 = 34 of the 36 with ctDNA available).
- **Selected cohorts (om index | denominator | role):**
  - om0 `Cohort 1` — n=15 — `COMPONENT_KEPT` **[kept]**
  - om0 `Cohort 2` — n=21 — `COMPONENT_KEPT` **[kept]**
  - om12 `Cohort 1 Mutant` — n=8 — `CROSS_AXIS_DUPLICATE`
  - om12 `Cohort 1 Non-Mutant` — n=6 — `CROSS_AXIS_DUPLICATE`
  - om12 `Cohort 2 Mutant` — n=11 — `CROSS_AXIS_DUPLICATE`
  - om12 `Cohort 2 Non-Mutant` — n=9 — `CROSS_AXIS_DUPLICATE`
- **Non-overlapping set:** YES — sum **36** from om0 OG000-OG001 (15+21)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03776812 — excess 21 (selected 4 cohorts summing 199 vs registered enrollment 178, ACTUAL)

- **Mechanism:** `NESTED_SUBSET`
- **Source:** `ctg_results_bor_2018_2021` line 215 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om7 "Crossover Patients" (description: patients initially in Arm C who cross over) n=21 are Arm C patients already counted in om11 OG002.
- **Selected cohorts (om index | denominator | role):**
  - om7 `Crossover Patients` — n=21 — `NESTED_SUBSET`
  - om11 `Arm A: Continuous Relacorilant Dosing` — n=58 — `COMPONENT_KEPT` **[kept]**
  - om11 `Arm B: Intermittent Relacorilant Dosing` — n=60 — `COMPONENT_KEPT` **[kept]**
  - om11 `Arm C: Nab-paclitaxel Comparator` — n=60 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **178** from om11 OG000-OG002 (58+60+60)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03176277 — excess 20 (selected 5 cohorts summing 62 vs registered enrollment 42, ACTUAL)

- **Mechanism:** `POOLED_EXPLICIT`
- **Source:** `ctg_results_bor_2014_2017` line 354 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om14 OG003 "Total" (n=20, described "Part A total") = 10+3+7.
- **Selected cohorts (om index | denominator | role):**
  - om14 `ONO-7475 10 mg` — n=7 — `COMPONENT_KEPT` **[kept]**
  - om14 `ONO-7475 3mg` — n=10 — `COMPONENT_KEPT` **[kept]**
  - om14 `ONO-7475 6mg` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om14 `Total` — n=20 — `POOLED_EXPLICIT`
  - om26 `ONO-7475 6mg + Venetoclax (Part D)` — n=22 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **42** from om14 OG000-OG002 (10+3+7) + om26 OG000 (22)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04895735 — excess 19 (selected 5 cohorts summing 64 vs registered enrollment 45, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT`
- **Source:** `ctg_results_bor_2018_2021` line 576 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om1 shortens two of om0 group titles ("Cohort A", "Cohort A1") with identical denominators 11 and 9, creating two extra keys.
- **Selected cohorts (om index | denominator | role):**
  - om0 `Cohort A (Adenoid Cystic Carcinoma)` — n=11 — `COMPONENT_KEPT` **[kept]**
  - om0 `Cohort A1 (ACC Patients Enrolled Starting With MCCC Amendment 3)` — n=9 — `COMPONENT_KEPT` **[kept]**
  - om0 `Cohort B (Non-adenoid Cystic Carcinoma)` — n=24 — `COMPONENT_KEPT` **[kept]**
  - om1 `Cohort A` — n=11 — `DUPLICATE_TITLE_VARIANT`
  - om1 `Cohort A1` — n=9 — `DUPLICATE_TITLE_VARIANT`
- **Non-overlapping set:** YES — sum **44** from om0 OG000-OG002 (11+9+24)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03274804 — excess 18 (selected 2 cohorts summing 38 vs registered enrollment 20, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT`
- **Source:** `ctg_results_bor_2018_2021` line 278 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Single-arm trial; the one arm is titled differently in om2 and om3, both n=19.
- **Selected cohorts (om index | denominator | role):**
  - om2 `Study Treatment Arm` — n=19 — `COMPONENT_KEPT` **[kept]**
  - om3 `Single Arm, Prospective, Open-label Trial` — n=19 — `DUPLICATE_TITLE_VARIANT`
- **Non-overlapping set:** YES — sum **19** from om2 OG000
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04216316 — excess 10 (selected 3 cohorts summing 22 vs registered enrollment 12, ACTUAL)

- **Mechanism:** `POOLED_UNFLAGGED`
- **Source:** `ctg_results_bor_2018_2021` line 258 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om8 is titled "Best Overall Response - Total Population" (n=11) and om9 "Best Overall Response - By Dose Level" splits the same 11 into 6+5.
- **Selected cohorts (om index | denominator | role):**
  - om8 `Berzosertib (M6620) + Carboplatin + Gemcitabine + Pembrolizumab` — n=11 — `POOLED_UNFLAGGED`
  - om9 `Dose Level -1 (Berzosertib (M6620) + Carboplatin + Gemcitabine + Pembrolizumab)` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om9 `Dose Level 1 (Berzosertib (M6620) + Carboplatin + Gemcitabine + Pembrolizumab)` — n=5 — `COMPONENT_KEPT` **[kept]**
- **Non-overlapping set:** YES — sum **11** from om9 OG000-OG001 (6+5)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03773107 — excess 8 (selected 5 cohorts summing 20 vs registered enrollment 12, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT`
- **Source:** `ctg_results_bor_2018_2021` line 195 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Three dose cohorts spelled two ways across om1/om2 ("Ruxolitibin" typo in om1, "5m" typo in om2). Either OM sums to 12 = registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om1 `Phase I 10 mg Ruxolitinib` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om1 `Phase I 15 mg Ruxolitibin` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om1 `Phase I 5mg Ruxolitinib` — n=5 — `COMPONENT_KEPT` **[kept]**
  - om2 `Phase I 15 mg Ruxolitinib` — n=3 — `DUPLICATE_TITLE_VARIANT`
  - om2 `Phase I 5m Ruxolitinib` — n=5 — `DUPLICATE_TITLE_VARIANT`
- **Non-overlapping set:** YES — sum **12** from om1 OG000-OG002 (5+4+3)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03126110 — excess 6 (selected 18 cohorts summing 151 vs registered enrollment 145, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT`
- **Source:** `ctg_results_bor_2014_2017` line 206 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Whole excess is one arm written out with doses in om9 and without doses in om2 (both n=6).
- **Selected cohorts (om index | denominator | role):**
  - om1 `Phase 2 Group C2 PD-1/PD-L1 RM: INCAGN01876 300 mg + Ipilimumab 1 mg/kg` — n=8 — `COMPONENT_KEPT` **[kept]**
  - om1 `Phase 2 Group F Biopsy: INCAGN01876 300 mg + Nivolumab 240 mg` — n=2 — `COMPONENT_KEPT` **[kept]**
  - om1 `Phase 2 Group F CC: INCAGN01876 300 mg + Nivolumab 240 mg` — n=18 — `COMPONENT_KEPT` **[kept]**
  - om1 `Phase 2 Group F GC: INCAGN01876 300 mg + Nivolumab 240 mg` — n=16 — `COMPONENT_KEPT` **[kept]**
  - om1 `Phase 2 Group F PD-1/PD-L1 RM: INCAGN01876 300 mg + Nivolumab 240 mg` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om1 `Phase 2 Group F SCCHN INCAGN01876 300 mg + Nivolumab 240 mg` — n=46 — `COMPONENT_KEPT` **[kept]**
  - om2 `Phase 1 Group A: INCAGN01876 1.0 mg/kg Q2W + Nivolumab 240 mg Q2W` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om2 `Phase 1 Group A: INCAGN01876 10.0 mg/kg Q2W + Nivolumab 240 mg Q2W` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om2 `Phase 1 Group A: INCAGN01876 3.0 mg/kg Q2W + Nivolumab 240 mg Q2W` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om2 `Phase 1 Group A: INCAGN01876 5.0 mg/kg Q2W + Nivolumab 240 mg Q2W` — n=5 — `COMPONENT_KEPT` **[kept]**
  - om2 `Phase 1 Group B: INCAGN01876 1.0 mg/kg Q2W, Then Nivolumab 240 mg Q2W` — n=5 — `COMPONENT_KEPT` **[kept]**
  - om2 `Phase 1 Group B: INCAGN01876 3.0 mg/kg Q2W, Then Nivolumab 240 mg Q2W` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om2 `Phase 1 Group B: INCAGN01876 5.0 mg/kg Q2W, Then Nivolumab 240 mg Q2W` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om2 `Phase 1 Group C: INCAGN01876 1.0 mg/kg Q2W + Ipilimumab 1 mg/kg Q6W` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om2 `Phase 1 Group C: INCAGN01876 3.0 mg/kg Q2W + Ipilimumab 1 mg/kg Q6W` — n=8 — `COMPONENT_KEPT` **[kept]**
  - om2 `Phase 1 Group C: INCAGN01876 5.0 mg/kg Q2W + Ipilimumab 1 mg/kg Q6W` — n=3 — `COMPONENT_KEPT` **[kept]**
  - om2 `Phase 1 Group D: INCAGN01876 + Nivolumab + Ipilimumab` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om9 `Phase 1 Group D: INCAGN01876 1.0 mg/kg + Nivolumab 3 mg/kg + Ipilimumab 1 mg/kg` — n=6 — `DUPLICATE_TITLE_VARIANT`
- **Non-overlapping set:** YES — sum **145** from om1 (94) + om2 (51)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04577963 — excess 6 (selected 5 cohorts summing 58 vs registered enrollment 52, ACTUAL)

- **Mechanism:** `NESTED_SUBSET`
- **Source:** `ctg_results_bor_2018_2021` line 139 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om2/om3/om5 pop states verbatim: "As pre-specified in SAP, all patients from Part 1 were also included in the relevant Cohorts in Part 2 based on their tumor type." The 6 Part 1 patients are inside the Part 2 cohorts, which sum to 52 = registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om2 `Part 2: Cohort A: TNBC (IO-Treated in the Metastatic Setting)` — n=1 — `COMPONENT_KEPT` **[kept]**
  - om2 `Part 2: Cohort B: TNBC (IO-Naïve in the Metastatic Setting)` — n=11 — `COMPONENT_KEPT` **[kept]**
  - om2 `Part 2: Cohort C: EC (IO-Naïve)` — n=1 — `COMPONENT_KEPT` **[kept]**
  - om2 `Part 2: Cohort D: MSS mCRC (IO-Naïve)` — n=39 — `COMPONENT_KEPT` **[kept]**
  - om3 `Part 1: Solid Tumor of Any Type (IO-Treated/IO-Naïve in the Metastatic Setting)` — n=6 — `NESTED_SUBSET`
- **Non-overlapping set:** YES — sum **52** from om2 OG000-OG003 (1+11+1+39)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03512353 — excess 5 (selected 3 cohorts summing 12 vs registered enrollment 7, ACTUAL)

- **Mechanism:** `CROSS_AXIS_DUPLICATE`
- **Source:** `ctg_results_bor_2018_2021` line 357 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om18 partitions the same single arm by prior lines (4+2=6). Registered enrollment 7; 6 treated/evaluable.
- **Selected cohorts (om index | denominator | role):**
  - om16 `Carfilzomib Plus Dexamethasone` — n=6 — `COMPONENT_KEPT` **[kept]**
  - om18 `1 Prior Line of Therapy` — n=4 — `CROSS_AXIS_DUPLICATE`
  - om18 `2+ Prior Lines of Therapy` — n=2 — `CROSS_AXIS_DUPLICATE`
- **Non-overlapping set:** YES — sum **6** from om16 OG000 (6) or om18 OG000-OG001 (4+2)
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03523572 — excess 4 (selected 6 cohorts summing 90 vs registered enrollment 86, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT`
- **Source:** `ctg_results_bor_2018_2021` line 437 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om7 OG000 is "Dose Escalation (3.2 kg/mg)" - units transposed - for the same 4 patients as om1 OG000 "Dose Escalation (3.2 mg/kg)". om1 sums to 86 = registered enrollment.
- **Selected cohorts (om index | denominator | role):**
  - om1 `Dose Escalation (3.2 mg/kg)` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om1 `Dose Escalation (5.4 mg/kg) + Dose Expansion Cohort 1 (5.4 mg/kg): HER2 Positive BC` — n=32 — `COMPONENT_KEPT` **[kept]**
  - om1 `Dose Expansion Cohort 2 (5.4 mg/kg): HER2 Low BC` — n=16 — `COMPONENT_KEPT` **[kept]**
  - om1 `Dose Expansion Cohort 3 (5.4 mg/kg): HER2 High Expressing (IHC 2+/3+) UC` — n=30 — `COMPONENT_KEPT` **[kept]**
  - om1 `Dose Expansion Cohort 4 (5.4 mg/kg): HER2 Low Expressing (IHC 1+) UC` — n=4 — `COMPONENT_KEPT` **[kept]**
  - om7 `Dose Escalation (3.2 kg/mg)` — n=4 — `DUPLICATE_TITLE_VARIANT`
- **Non-overlapping set:** YES — sum **86** from om1 OG000-OG004
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT03446040 — excess 3 (selected 3 cohorts summing 95 vs registered enrollment 92, ACTUAL)

- **Mechanism:** `CROSSOVER_DOUBLE_COUNT`
- **Source:** `ctg_results_bor_2018_2021` line 93 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** om3 pop states verbatim: "Participants who crossed over from part A1 to Part B are accounted for in both arms." The record declares the double count but never states how many participants crossed over, so no non-overlapping set can be named. 43+37+15=95 vs 92 registered.
- **Selected cohorts (om index | denominator | role):**
  - om3 `Part A1: BMS-986258 1200 mg + ENHANZE` — n=15 — `UNRESOLVED_DECLARED_OVERLAP`
  - om3 `Part A: All Doses` — n=43 — `UNRESOLVED_DECLARED_OVERLAP`
  - om3 `Part B: All Doses` — n=37 — `UNRESOLVED_DECLARED_OVERLAP`
- **Non-overlapping set:** `UNRESOLVED` — see mechanism note above
- **enrollment_type:** ACTUAL — ESTIMATED: NO

### NCT04033432 — excess 3 (selected 2 cohorts summing 17 vs registered enrollment 14, ACTUAL)

- **Mechanism:** `DUPLICATE_TITLE_VARIANT+NESTED_SUBSET`
- **Source:** `ctg_results_bor_2018_2021` line 381 (single cached copy; no other payload holds this NCT)
- **What drives the excess:** Single-arm trial: om0 group (n=14, PSA-evaluable) and om3 group "Treatment" (n=3, RECIST-evaluable) are the same arm at two evaluability denominators.
- **Selected cohorts (om index | denominator | role):**
  - om0 `Treatment (Recombinant EphB4-HSA Fusion Protein)` — n=14 — `COMPONENT_KEPT` **[kept]**
  - om3 `Treatment` — n=3 — `NESTED_SUBSET`
- **Non-overlapping set:** YES — sum **14** from om0 OG000
- **enrollment_type:** ACTUAL — ESTIMATED: NO

## What I did not establish

- I did not check whether any of these cohorts overlap cohorts in **another** trial. That is global
  and belongs to the parent.
- Where a trial's group descriptions do not state containment explicitly, my `NESTED_SUBSET` calls
  rest on arithmetic identity plus the population description (e.g. a subtotal that is exactly the
  sum of its named parts within the same outcome measure). Those are recorded as the evidence in the
  per-trial notes; a reader who rejects that inference should treat the affected trial as
  `UNRESOLVED` rather than as a different mechanism.
- I did not re-derive any response numerator, rate or effect, and no such value was read.
- I did not verify that Job 2's selection is the *right* selection; I took its selected cohort list
  as given and asked only why those denominators over-sum.
