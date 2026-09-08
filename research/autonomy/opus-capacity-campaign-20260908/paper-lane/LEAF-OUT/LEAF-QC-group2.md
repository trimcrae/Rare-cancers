---
id: LEAF-QC-GROUP2
title: "QUESTION C, group 2 — do the step-f registration-order ties have a recoverable metadata basis?"
level: L4
kind: leaf-source-validation
status: live
date: 2026-09-08
---

# LEAF QC-group2 — registration-order ties, record-level test

⛔ Source-validation evidence only. No efficacy, safety, selectivity or capacity claim is made,
restated or reinstated. No response rate, numerator or effect size is reported anywhere in this
leaf. The endpoint manuscript is PARKED and was not read or edited. The pre-registered rule was
**not** rewritten and the global selection was **not** re-run.

## 1 · What was tested

Job 2's `RULE-PREREGISTERED.md` resolves a cohort at step **f** ("smallest outcome-measure index")
when steps a–e leave more than one candidate. Job 2 recorded 1,590 such ties globally and asserted
that **"no metadata basis exists for those."** This leaf tests that assertion at the record level,
for its assigned 121 NCTs only.

**Verdict for this group: the assertion does not hold.** In **524 of 525** assigned step-f ties the
competing outcome measures differ in at least one recorded field that the ladder never consults.
In the single remaining tie the two measures report the same quantity for the cohort.

## 2 · Inputs and integrity

| item | value |
|---|---|
| cache | `…/scratchpad/ctg-cache-216bd1b5/` (12 payloads + `_manifest.json` + `SHA256-MANIFEST.txt`) |
| `sha256sum -c SHA256-MANIFEST.txt` | all 13 lines `OK`, **exit code 0** |
| network activity in this leaf | **none** — no request, no re-download, no second cache copy |
| assignment | `LEAF-ASSIGNMENTS/QC-group2.txt`, 121 NCTs |
| tie source | `CURATION-endpoint-identity-and-overlap-artifacts/TIES.tsv` |
| assigned step-f tie rows | **525** (all rows whose `nct` ∈ my list and `resolved_at_step` = `f (smallest outcome index)`) |
| **ties reached / assigned** | **525 / 525 (100 %)**; **121 / 121 NCTs** reached; 0 unreached, 0 skipped |
| ties outside my group | not read, not counted, not reasoned about |

## 3 · Method, and how the reconstruction was validated

To see *which* measures were still competing at step f, the candidate set had to be rebuilt from the
cache. R0 (canonical record per `nctId`), R1 (title regex, `POSTED`, group present, `Participants`
denominator) and ladder steps **a–e** were re-applied **exactly as pre-registered**, with the
pre-registered regexes verbatim, and the survivors taken as the step-f competitor set. Nothing in
the rule was altered, and no selection outside these 525 rows was recomputed.

**Validation of the reconstruction:** for all **525 / 525** rows the number of survivors reproduces
Job 2's own `candidates_still_competing` value **exactly** (0 mismatches). Survivor counts:
441 ties with 2 candidates, 73 with 3, 11 with 4.

One normalisation note: the group-title match is `norm(record group title) == norm(TIES.group_norm)`,
i.e. the same function applied to both sides, because Job 2's stored `group_norm` retains a trailing
`)` (e.g. `nivolumab + brentuximab vedotin (bv)`). Applying a strip only to the record side loses 36
of the 525 rows; applying it to both sides recovers all 525 and reproduces every tie count.

Fields examined per tie, none of which the ladder uses as a discriminator: `title` (endpoint
construct and response-depth wording), `description`, `populationDescription`, `timeFrame`,
`paramType`, `unitOfMeasure`, named assessment criteria (RECIST 1.0/1.1, irRECIST, iRECIST, mRECIST,
irRC, Cheson, Lugano, IWG, IMWG, IWCLL, RANO, PCWG, Choi, WHO, Deauville, RECIL, PERCIST, EORTC,
INRC), imaging modality (PET-CT vs CT alone), and the `classes[].title` / `categories[].title`
structure of the reported cells. Outcome `type` is equal across survivors **by construction** (step a
already ordered on it): 470 ties SECONDARY, 49 PRIMARY, 4 OTHER_PRE_SPECIFIED, 2 POST_HOC. The
`Participants` denominator is likewise equal across survivors by construction (step e).

## 4 · Result

| classification | ties | share |
|---|---|---|
| `BASIS_EXISTS` | **524** | 99.8 % |
| `NO_BASIS` (Job 2's claim confirmed) | **1** | 0.2 % |
| `UNRESOLVED` | **0** | — |

### Primary distinguishing field (strongest basis per tie)

| primary basis | ties | what actually differs |
|---|---|---|
| `ENDPOINT_CONSTRUCT` | **372** | the competitors are **different endpoints**: ORR vs DCR vs CBR vs a best-overall-response category distribution |
| `ASSESSMENT_CRITERIA` | 65 | different named criteria set or version |
| `RESPONSE_DEPTH` | 34 | different response threshold (CR-only, composite CR, VGPR-or-better, major/minor response) at the same construct |
| `POPULATION` | 18 | `populationDescription` names a different analysed subgroup |
| `MODALITY` | 14 | PET-CT-based vs CT-alone assessment of the same response |
| `PARAM_UNIT` | 10 | different `paramType`/`unitOfMeasure` — not the same reported quantity |
| `TIME_FRAME` | 8 | different assessment window |
| `STRUCTURE` | 3 | different `classes`/`categories` layout of the reported cells |
| none found | 1 | — |

Counting every basis present, not only the strongest: `ENDPOINT_CONSTRUCT` 372, `STRUCTURE` 205,
`ASSESSMENT_CRITERIA` 186, `TIME_FRAME` 163, `PARAM_UNIT` 117, `POPULATION` 111,
`RESPONSE_DEPTH` 35, `MODALITY` 15.

Of the 186 criteria-differing ties, **157** have both competitors naming a criteria set and the sets
differ; **29** are asymmetric (one names a criteria set, the other names none). The commonest
differing pairs: RECIST 1.1 vs irRC (53), RECIST 1.1 vs unversioned RECIST (47),
Cheson+Lugano vs Lugano (19), RECIST 1.1 vs RECIST 1.1+mRECIST (11), RECIST 1.1 vs iRECIST (7),
RECIST 1.0 vs unversioned RECIST (4), Cheson vs Lugano (2).

In **420 of 525** ties the reported measurement cells for the cohort are not identical across the
competing measures, so the tie-break is materially selecting between different reported numbers.
(Reported as a materiality flag only; no value is quoted, compared or interpreted here.)

## 5 · Worked examples, with exact pointers

Every pointer is `payload → NCT → outcome index → results group id`.

- **`ENDPOINT_CONSTRUCT`** — `ctg_results_bor_2014_2017.txt` → NCT02519348 → cohort
  `China Cohort: Durvalumab 20 mg/kg` (`OG006`), indices **5** and **6**:
  [5] "Overall Objective Response Rate (ORR) Based on Investigator Assessments and Blinded
  Independent Central Review" vs [6] "Disease Control Rate (DCR) …". ORR and DCR are different
  endpoints; the ladder treated them as interchangeable because R1's title regex admits both.
- **`ASSESSMENT_CRITERIA`** — `ctg_results_bor_2014_2017.txt` → NCT02596971 → indices **5** and **7**:
  Cheson criteria vs Lugano criteria for the same cohort.
- **`RESPONSE_DEPTH`** — `ctg_results_bor_2014_2017.txt` → NCT02604511 → cohort `ibrutinib`,
  indices **0** and **1**: "Major Response Rate" (PR or better, ≥50 % IgM reduction) vs
  "Best Overall Response Rate" (minor response or better, ≥25 % IgM reduction). Registration order
  selects the narrower index-0 measure.
- **`MODALITY`** — `ctg_results_bor_2014_2017.txt` → NCT02624986 → indices **6** and **8**: objective
  response by IRC on **PET-CT** vs by IRC on **CT alone**, both Lugano 2014.
- **`PARAM_UNIT`** — `ctg_results_bor_2014_2017.txt` → NCT02678780 → indices **0** and **1**:
  `COUNT_OF_PARTICIPANTS` / "Participants" vs `NUMBER` / "percentage of participants with response".
- **`TIME_FRAME`** — `ctg_placebo_onc_1999_2009.txt` → NCT02799069 → indices **14, 15, 18, 19**:
  complete lesion response at 3–4 weeks after first PDT, 12 weeks after first PDT, 3–4 weeks after
  last PDT, 12 weeks after last PDT. Four distinct assessment windows; registration order takes the
  earliest-indexed one.
- **`POPULATION`** — `ctg_results_bor_2014_2017.txt` → NCT02712905 → indices **3** and **4**: the
  same Full Analysis Set label restricted to **AML** participants vs to **MDS** participants.
- **`STRUCTURE`** — `ctg_results_bor_2018_2021.txt` → NCT03384940 → indices **0** and **1**: a
  per-category best-response distribution (Confirmed CR / PR / SD / PD / …) vs a
  confirmed-CR+PR-rate layout with 3- and 12-month variants.

### The single `NO_BASIS` tie — Job 2's claim confirmed here

`ctg_results_bor_2014_2017.txt` → **NCT02928224** → cohort `Phase 3: Doublet Arm` → indices **24**
and **26**. Both are "(Phase 3) Comparison of Objective Response Rate (ORR) … Per BICR", RECIST
v1.1, identical `populationDescription` (Phase 3 Response Efficacy Set), identical `timeFrame`,
identical `paramType`/`unitOfMeasure`, identical criteria, identical class/category structure; the
titles differ only in which pairwise comparison the measure belongs to (Doublet vs Control;
Triplet vs Doublet), and the reported cells for this cohort are identical. The two measures report
the same quantity for this cohort, so nothing distinguishes them and nothing turns on the choice.

## 6 · Would the basis change the selection?

Stating this requires a preference the pre-registered rule does not contain, so it is reported
**conditionally and factually**; proposing or adopting such a preference is the parent's decision,
not this leaf's.

- **92 ties (17 NCTs)** are marked `would_change_selection = YES`: registration order selected a
  measure that is **not** the ORR construct at full response depth, while a candidate that **is**
  ORR-at-full-depth was competing at a higher index. If the parent preferred the ORR construct — the
  endpoint R1's own regex nominally targets — the selected measure would change to the named index.
- **433 ties** are `NOT_DETERMINED`: the fields distinguish the candidates, but the pre-registered
  rule states no ordering over them (e.g. RECIST 1.1 vs irRC, PET-CT vs CT alone, AML vs MDS
  subgroup, 3-week vs 12-week window), so the selection is unchanged unless the parent adds one.

| NCT | conseq. ties | payload | indices | selected → would become | selected title // alternative title |
|---|---|---|---|---|---|
| NCT02525536 | 3 | ctg_results_bor_1999_2009 | 9,10 | 9 → 10 | Number of Participants With Best Overall Response // Percentage of Participants With Objective Response |
| NCT02545075 | 2 | ctg_results_bor_2014_2017 | 4,5 | 4 → 5 | Disease Control Rate (DCR) // Best Overall Response Rate (BORR) |
| NCT02598960 | 13 | ctg_results_bor_2014_2017 | 3,4 | 3 → 4 | Best Overall Response // Overall Response Rate |
| NCT02604511 | 1 | ctg_results_bor_2014_2017 | 0,1 | 0 → 1 | Major Response Rate // Best Overall Response Rate |
| NCT02608268 | 28 | ctg_results_bor_2014_2017 | 7,10 | 7 → 10 | Best Overall Response (BOR) Per RECIST v1.1 // Overall Response Rate (ORR) Per irRC |
| NCT02625610 | 2 | ctg_results_bor_2014_2017 | 2,3 | 2 → 3 | Best Overall Response (BOR) by Investigator Assessment // Objective Response Rate (ORR) by Investigator Assessment |
| NCT02658084 | 1 | ctg_results_bor_2014_2017 | 3,5 | 3 → 5 | Phase 2 – Clinical Benefit Rate (CBR) // Phase 2 – Objective Response Rate (ORR) |
| NCT02755597 | 2 | ctg_placebo_onc_2014_2017 | 1,10 | 1 → 10 | Very Good Partial Response (VGPR) or Better Response Rate // Overall Response Rate (ORR) |
| NCT02795429 | 3 | ctg_results_bor_2014_2017 | 6,7,8,9 | 6 → 8 | Phase Ib and Phase II: Best Overall Response (BOR) Per RECIST v1.1 // Phase Ib: Overall Response Rate (ORR) Per RECIST v1.1 |
| NCT02795988 | 4 | ctg_results_bor_2014_2017 | 5,6 | 5 → 6 | Phase 2 and Phase 2 Extension: Disease Control Rate (DCR) // … Objective Response Rate (ORR) |
| NCT02875223 | 13 | ctg_results_bor_2014_2017 | 1,2 | 1 → 2 | Part A – Clinical Benefit Rate (CBR) … // Part A – Objective Response Rate … |
| NCT02939183 | 8 | ctg_results_bor_2014_2017 | 7,8 | 7 → 8 | Best Overall Response (BOR) According to Revised International Myeloma Working Group Uniform Response Criteria // Overall Response Rate (ORR) According to IMWG-URC |
| NCT02975700 | 1 | ctg_results_bor_2014_2017 | 0,1 | 0 → 1 | Summary of Best Overall Response … // Objective Response Rate (ORR) … |
| NCT03085225 | 2 | ctg_results_bor_2014_2017 | 2,3 | 2 → 3 | Dose Escalation Part: Preliminary Signs of Antitumor Activity // Dose Escalation Part: Objective Response Rate (ORR) |
| NCT03138499 | 2 | ctg_results_bor_2014_2017 | 1,2 | 1 → 2 | Complete Response Rate (CRR) // Objective Response Rate (ORR) |
| NCT03138538 | 6 | ctg_results_bor_2014_2017 | 15,22 | 15 → 22 | Number of Participants With Best Overall Response Assessment // Percentage of Participants With Objective Response |
| NCT03368196 | 1 | ctg_results_bor_2018_2021 | 5,6,7 | 5 → 6 | Best Overall Response By The Investigator's Assessment (Unconfirmed) // Objective Response Rate (Unconfirmed) |

Per-tie rows, including the cohort each applies to, are in `LEAF-QC-group2.tsv`.

## 7 · What this does and does not establish

- It establishes, for **these 525 ties only**, that the source records carry distinguishing metadata
  in all but one case, so the global phrase "no metadata basis exists" is **not** supported at the
  record level in this group.
- It does **not** extrapolate to the other 1,065 step-f ties; those NCTs are outside my group and
  were not read.
- The dominant finding — 372 ties between **different endpoints** (ORR / DCR / CBR / BOR
  distribution) — is a property of R1's candidate regex, which admits several endpoint constructs
  into one candidate pool, not only of step f. Whether to narrow R1, add a construct preference, or
  leave the rule as pre-registered and carry this as a recorded limitation is the parent's decision.
- No amendment to `RULE-PREREGISTERED.md` is proposed here, and no selection outside these 525 rows
  was recomputed.
- Nothing here bears on efficacy, safety, selectivity, therapeutic window or clinical readiness.

## 8 · Output files

- `LEAF-OUT/LEAF-QC-group2.md` (this file)
- `LEAF-OUT/LEAF-QC-group2.tsv` — 525 rows, one per assigned step-f tie, columns:
  `nct`, `group_norm`, `group_title_source`, `results_group_id` (per competing index),
  `payload`, `n_candidates`, `outcome_indices`, `selected_index`, `outcome_type`,
  `participants_denominator`, `classification`, `primary_basis`, `all_bases`,
  `distinguishing_field`, `values_by_index`, `titles_by_index`, `reported_cells_differ`,
  `would_change_selection`, `would_change_to_index`.

Both files are untracked. No tracked file, manuscript, producer, graph file or frozen packet was
edited; no gate, preflight, test or producer was run; no commit, push, branch or worktree was made.
