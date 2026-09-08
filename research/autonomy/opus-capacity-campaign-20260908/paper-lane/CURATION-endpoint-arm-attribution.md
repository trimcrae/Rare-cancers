---
id: DOC-OPUS-CAMPAIGN-CURATION-ARM-ATTRIBUTION
title: "Source validation — arm-level disease, phase and control attribution for the 552 included groups"
level: L4
kind: memo
status: live
purpose: >
  Establish, from the delivered immutable ClinicalTrials.gov cache copy, what each included group's
  own record actually supports for disease, phase and control status, keeping the whole-trial
  condition list, the phase label, the arm description and the group-specific evidence separate;
  and state the limits this places on any disease-specific subgroup analysis.
scope: >
  L4. Source-validation evidence for finding F3 of the endpoint hold. It computes no rate, no
  response fraction, no cause fraction and no capacity figure, repairs nothing, reopens nothing and
  authorises no publication act.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
related: [DOC-OPUS-CAMPAIGN-HOLD-ENDPOINT]
---

# Arm-level disease, phase and control attribution — what the raw record supports

⛔ **The endpoint manuscript stays parked.** This memo is source-validation evidence only. It
produces **no clinical effect estimate**: no efficacy, no response rate, no cause fraction, no
capacity claim, and it reinstates none. It does not touch
`research/manuscripts/endpoint/response-endpoint-indolent-tumours.md`, its producers or its
artifacts.

## What was read, and nothing else

The delivered immutable cache copy at cache revision
`216bd1b5fb25a56b90ef3cc2373e1fe68322708f` — 12 payloads, `_manifest.json`, `SHA256-MANIFEST.txt`,
157,268,733 payload bytes. **No ClinicalTrials.gov request was made, no retry, no uncached lookup,
no synthetic record and no second copy of the cache.**

## The unit, and the proof that it is the right one

The unit is the **included group**: one `(NCT, outcome-measure title, results-group title,
four-cell sum)` key carrying all four best-response categories as integers. Re-deriving the key set
from the cache with the frozen producer's own category patterns yields **552 keys, matching the
552 rows of `C2_arms` in `endpoint-corpus.json` exactly** — 552 matched, 0 only-here, 0 only-there —
and the trial-level condition and phase strings reproduce the frozen corpus for all 552 rows with
**0 mismatches**. The attribution below therefore applies to exactly the included groups, and the
disagreements that follow are disagreements about *attribution*, not about which records were read.

## Four things, kept apart

Every row of the mapping carries these four separately and never merges them.

| # | Field group | What it is | Where it comes from |
|---|---|---|---|
| 1 | `trial_conditions`, `n_trial_conditions` | the **whole-trial condition list**, verbatim | `protocolSection.conditionsModule.conditions` — a **trial** attribute |
| 2 | `trial_phases` | the **phase label** | `protocolSection.designModule.phases` — a **trial** attribute |
| 3 | `registry_arm_label`, `registry_arm_type`, `registry_arm_description`, `arm_match_quality` | the **arm description** as registered | `protocolSection.armsInterventionsModule.armGroups` — an **arm** attribute, and only usable once the results group is actually resolved to an arm |
| 4 | `group_title`, `group_description`, `om_title` | the **group-specific evidence** | `resultsSection.outcomeMeasuresModule…groups` — the only text that belongs to **this group** |

A trial-level value is never promoted to a group-level finding. Where the group's own record cannot
carry the attribute, the row says **MIXED** or **UNKNOWN**, and that is recorded as the result.

## Deliverable

- **Mapping table** — `CURATION-endpoint-arm-attribution-map.tsv`, **553 lines (552 group rows +
  header), 30 columns, 407,150 bytes**, sha256 `1d7e8e18b7ad4c437b5a9776b76cfa8e7dd83ca1897f954dfada9c040497bbec`.
  One row per included group; every attribution carries its own `*_basis` string.
- **Derivation** — `CURATION-endpoint-arm-attribution-derive.py` (stdlib only, reads the cache copy,
  writes no clinical estimate).

### Why no concurrent shards

The payloads divide by era and the judgement is per record, so an era split would have been safe.
It was **not used**: 552 records over 12 files parse in **3.5 s** in one process, so sharding would
have added coordination cost and a second cache read for nothing. The era split is delivered as the
**shard table** below, computed in that single pass. No unit was judged twice.

## Shard table — attribution by era

| era (shard) | groups | trials | names a tumour type | umbrella label | broad only | unassignable | phase single | phase mixed | phase unknown | control supported | not a control | control unknown |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1999_2009 | 49 | 15 | 17 | 18 | 8 | 6 | 42 | 7 | 0 | 0 | 13 | 36 |
| 2010_2013 | 85 | 26 | 68 | 0 | 2 | 15 | 60 | 25 | 0 | 5 | 61 | 19 |
| 2014_2017 | 285 | 57 | 102 | 133 | 0 | 50 | 111 | 169 | 5 | 17 | 122 | 146 |
| 2018_2021 | 130 | 38 | 38 | 41 | 8 | 43 | 88 | 40 | 2 | 5 | 49 | 76 |
| 2022_2026 | 3 | 2 | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 1 | 2 | 0 |
| **TOTAL** | 552 | 138 | 228 | 192 | 18 | 114 | 304 | 241 | 7 | 28 | 247 | 277 |
## 1 · Disease attribution

**Headline: 228 of 552 groups (41.3%) have a record that names a tumour type. 324 do not.**

| Attribution | Groups | Meaning |
|---|---|---|
| `NAMES_A_TUMOUR_TYPE` | **228** | the group is attributable to a named tumour type |
| `NOT_A_DISEASE_UMBRELLA` | **192** | the trial lists exactly one condition and that condition **names no tumour type** — `Solid Tumor`, `Advanced Solid Tumor`, `Advanced Malignancies`, `Cancer`, `Neoplasms` |
| `BROAD_CATEGORY_ONLY` | **18** | one condition, but an organ system, a lineage or a biomarker rather than a tumour type — `Central Nervous System Tumors`, `Leukemia`, `Lung Cancer`, `Isocitrate Dehydrogenase Gene Mutation` |
| `UNASSIGNABLE` (MIXED) | **114** | the trial lists **several distinct diseases** and the group's own record names none of them |

The mechanism behind those 228 is recorded per row, because they are not equally strong:

| Route | Groups | of which name a tumour type | What actually supports it |
|---|---|---|---|
| `TRIAL_SINGLE` | 381 | **201** | the trial lists exactly one condition, so trial-level inheritance is not a merge. The other 180 are umbrella (162) or broad-category (18) labels |
| `GROUP_SPECIFIC` | 47 | **20** | in a multi-disease trial, the **group's own title or description names exactly one** of the trial's conditions. For 27 of the 47 the term the group names is itself an umbrella (`Solid Tumors`), so group-level evidence resolves the *ambiguity* without naming a disease |
| `TRIAL_SINGLE_AFTER_COLLAPSE` | 10 | **7** | several strings that are stage or status variants of one disease (e.g. `Recurrent / Stage IIIA / IIIB / IVA / IVB Cervical Cancer`) |
| `MIXED` | 114 | 0 | several distinct diseases at trial level, nothing group-specific |

⚠ The 114 MIXED groups are a **result, not a gap**. Nothing in the cache assigns them a disease, and
filling them in from the trial's condition list is precisely the defect this memo documents.

### F3, confirmed and corrected in both directions

Root's F3 example holds, and the raw record makes it sharper than stated.

- The 23 records are **one trial, `NCT03829501`**, whose condition list carries **12 diseases**
  (`Squamous Cell Carcinoma of Head and Neck ; Non-small Cell Lung Cancer ; Hepatocellular Carcinoma ;
  Esophageal Cancer ; Gastric Cancer ; Melanoma ; Renal Cell Carcinoma ; Pancreatic Cancer ;
  Cervical Cancer ; Triple Negative Breast Cancer ; Advanced Cancer ; Metastatic Cancer`)
  at a single trial-level phase label of **`PHASE1/PHASE2`**.
- **None of those 23 groups is supported as cervical.** Four are group-supported as **pancreatic**
  (their own titles read `Alomfilimab … in Anti-PD-(L)1 Naïve/Pre-treated Pancreatic Cancer`); the
  remaining **19 stay MIXED**.
- Across all 552 groups, **exactly one** is attributable to cervical cancer — a single group from
  `NCT01676818`, a `PHASE2` trial whose five condition strings are stage variants of cervical cancer.

So "23 cervical records" was wrong in both directions: it over-counted cervical by 23 and it hid
four pancreatic-specific groups inside a basket label.

### The largest single "disease" in the corpus is not a disease

`Solid Tumor` / `Advanced Solid Tumor` / `Solid Tumors` and their kin account for **192 groups
(34.8%)** — more than any real tumour type. These pass a naive "the trial lists one condition" test
and are diagnostically empty. Any procedure that treats "one condition string" as "one disease"
inherits this.

### What is actually available for a disease-specific subgroup analysis

| derived disease key | groups | distinct trials | of which also single-phase |
|---|---|---|---|
| melanoma | 30 | 11 | 27 |
| breast | 20 | 7 | 14 |
| lymphoma non hodgkin | 20 | 1 | 20 |
| non small cell lung | 16 | 6 | 11 |
| hepatocellular | 14 | 4 | 1 |
| ovarian | 13 | 3 | 10 |
| small cell lung | 12 | 3 | 4 |
| castration resistant prostate mcrpc | 9 | 1 | 0 |
| leukemia lymphocytic chronic b cell | 9 | 1 | 9 |
| colorectal | 7 | 4 | 7 |
| multiple myeloma | 7 | 3 | 6 |
| glioblastoma | 6 | 2 | 6 |
| follicular lymphoma | 4 | 2 | 2 |
| pancreatic | 4 | 1 | 0 |
| renal cell | 4 | 1 | 0 |
| *(29 further keys, each <4 groups)* | 53 | — | — |
Across the 228 tumour-typed groups there are **47 distinct disease keys**. Of those:

- **15** keys have ≥4 groups; **11** are backed by ≥2 distinct trials; only **9** have both ≥5 groups
  and ≥2 trials.
- **17** keys are a **single group**.
- **96 of the 228 groups** sit in keys backed by **one trial only** — within such a key, group count
  is arm multiplicity, not independent evidence.
- **161** groups have **both** a named tumour type **and** an unambiguous single phase.

## 2 · Phase attribution

| Attribution | Groups | Trial phase field |
|---|---|---|
| `TRIAL_SINGLE` | **304** | one phase — `PHASE1` 133, `PHASE2` 114, `PHASE3` 54, `EARLY_PHASE1` 2, `PHASE4` 1 |
| `MIXED` | **241** | `PHASE1/PHASE2` 237, `PHASE2/PHASE3` 4 |
| `UNKNOWN` | **7** | no phase in the record (`NCT02679170`, `NCT02825420`, `NCT04539327`, `NCT04753658`) |

**241 groups (43.7%) have no single phase.** `PHASE1/PHASE2` alone covers **237 groups from 37
trials**. The phase label is a property of the **whole protocol**, and a phase I/II trial's dose-
escalation groups and its expansion groups are not at the same phase — but the record carries one
label for both. Where a group's own text hints at a phase or part (`phase_group_hint`: `Phase 3`,
`Part 2`, `dose escalation`, …), that hint is **recorded verbatim and not acted on**: a fragment of
a group title is not a phase assignment, and promoting it would repeat F3 in the phase dimension.

⚠ Mixed phase stays MIXED. It is not resolved to its lower or higher component.

## 3 · Control-status attribution

⛔ Control status here is supported by the **arm or group record**, never inferred from the trial's
design label. A trial being randomised, placebo-controlled or three-armed says nothing about which
*group* a given four-cell table belongs to.

The prerequisite is resolving the results group to a registered arm, and that mostly fails:

| Results-group → registered arm | Groups |
|---|---|
| `EXACT` label match | 137 |
| `NORMALIZED` match (punctuation/case only) | 48 |
| `CONTAINMENT` only (substring) — **treated as weak, not a resolution** | 36 |
| `AMBIGUOUS_MULTI` (several arms match) | 3 |
| `NONE` | 328 — of which **245 in trials that do register ≥2 arms**, and 6 where the trial registers no arm groups at all |

Posted results name outcome-measure groups independently of protocol arm labels, so for **367 of 552
groups the registry arm type is simply not reachable by a defensible match.**

| Control status | Groups | Supporting record |
|---|---|---|
| `CONTROL_PLACEBO` | **7** | exact/normalized match to a registered arm typed `PLACEBO_COMPARATOR` — `NCT02263508` ×2, `NCT02440464` ×2, `NCT01744249` ×2, `NCT02204982` ×1 |
| `CONTROL_NO_INTERVENTION` | **1** | `NCT02046733`, group `Observation` → registered arm `Observation`, type `NO_INTERVENTION` (exact) |
| `CONTROL_PLACEBO_BY_GROUP_TEXT` | **2** | the results group's own **title** states placebo, but no registered placebo arm resolves — `NCT01859741` `P2: Placebo + CIS or CARB`, `NCT03409614` `Part 2: Placebo + Chemotherapy`. **Both carry the flag `PLACEBO_CLAIM_WITHOUT_PLACEBO_ARM_IN_REGISTRY`: neither trial registers any placebo-typed arm.** Weaker than the 7 above and marked as such |
| `CONTROL_ACTIVE_COMPARATOR` | **13** | strong match to an arm typed `ACTIVE_COMPARATOR`. A comparator, **not** an untreated or placebo control |
| `CONTROL_UNSPECIFIED_BY_GROUP_TEXT` | **5** | the group record says control/comparator without naming placebo — `NCT02421588` ×3 (`Control (PLD or Topotecan)`), `NCT02566993` (description: "randomized to the Control Arm"), `NCT03480646` (`Enzalutamide Control Drug`) |
| `NOT_CONTROL` | **164** | strong match to an arm typed `EXPERIMENTAL` or `OTHER` |
| `NOT_CONTROL_SINGLE_ARM_TRIAL` | **83** | the trial registers ≤1 arm group, so no control exists to be |
| `UNKNOWN` | **239** | no strong arm match and no control language in the group's own record |
| `UNKNOWN_WEAK_MATCH_ONLY` | **36** | resolvable only by substring; not group-supported |
| `UNKNOWN_AMBIGUOUS_SEQUENCE_LABEL` | **2** | `NCT02259582` `Demcizumab/Placebo Arm (Arm 2)` — a treatment **sequence**, not a placebo arm |

**Totals: 28 groups from 22 trials have record-supported control status. Only 10 groups from 7
trials are placebo or no-intervention. 277 groups are UNKNOWN.**

### Where this disagrees with the frozen corpus

`endpoint-corpus.json` records **19 `control_arm_candidates`**, set by a regular expression over the
group **title**. That rule and the record disagree in both directions:

- **Producer says control, the record says otherwise (5 groups).** `NCT01256359` `Docetaxel and
  Placebo` ×3 — the registered arm of that exact label is typed **`EXPERIMENTAL`**, and the group
  description reads "Docetaxel without AZD6244 … docetaxel and placebo": the placebo is the blinding
  partner inside an active-treatment arm. Likewise `NCT02625610` `Chemotherapy + Best Supportive Care
  (BSC)` and `NCT02625623` `Physician Choice Chemotherapy + BSC`, both registered `EXPERIMENTAL` —
  BSC is background care, not the comparator. **A title containing the word "placebo" or "BSC" is not
  evidence that the group is a control arm.**
- **The record supports control status the producer misses (16 groups)**, chiefly the 13
  `ACTIVE_COMPARATOR` arms, which a placebo-word rule cannot see.
- Only **12** of the producer's 19 survive as record-supported.

Two further title traps are recorded because they are the general failure mode, not one-offs:
`Demcizumab/Placebo Arm (Arm 2)` (a sequence label — the placebo control of that trial is
`Placebo/Placebo Arm (Arm 1)`), and `NCT03854227` Parts 2B/2C, where "standard of care" appears in
the description of **prior therapy in the eligibility narrative** while both arms are `EXPERIMENTAL`.
Both are excluded from control status here.

## 4 · The resulting limits on any disease-specific subgroup analysis

These are limits, not estimates.

1. **A disease-specific subgroup can be formed for at most 228 of 552 groups (41.3%).** The other
   324 have no record-supported tumour type. **324 cannot be assigned to a disease at all**, and
   192 of them are under labels that name no disease in the first place.
2. **No disease subgroup may be formed by reading the trial's condition list onto a group.** For the
   114 MIXED groups that is the F3 defect exactly; the honest value is MIXED.
3. **A disease subgroup and a phase subgroup cannot generally be taken together.** Only **161 of 552
   groups (29.2%)** carry both a named tumour type and an unambiguous single phase. Any analysis
   stratified on disease *and* phase runs on under a third of the corpus.
4. **Most disease keys are too thin, and thin in a way that group counts hide.** 47 keys; 17 are a
   single group; **96 of 228 tumour-typed groups sit in keys supported by exactly one trial**, where
   the group count measures arm multiplicity, not independent trials. Only **9** keys reach ≥5 groups
   from ≥2 trials. This compounds F2: within one trial the groups are not independent units.
5. **No phase-stratified statement can be made for 241 groups (43.7%)**, and `PHASE1/PHASE2` cannot
   be split into its components from this cache. Rare-disease strata are worst hit, because basket
   and first-in-human trials are exactly where the mixed label sits.
6. **No control-referenced comparison is available at corpus scale.** 28 record-supported control
   groups across 22 trials, of which **10 across 7 trials** are placebo or no-intervention. After
   disease attribution these do not populate disease strata: they are scattered across trials, and a
   per-disease control comparison is not constructible for any disease key here.
7. **The 36 weak-match and 239 unknown control rows must not be read as "not a control."** Absent
   evidence is not evidence of absence; treating UNKNOWN as NOT_CONTROL would manufacture a
   denominator.
8. **Cervical cancer specifically supports n = 1 group.** Any cervical-specific statement built on
   the 23 records of `NCT03829501` is unsupported.

## 5 · What the sources cannot support

- **They cannot say which disease a group treated in a multi-disease trial**, unless the group's own
  title or description says so. That holds for 114 groups.
- **They cannot assign a phase to a group in a phase I/II trial.** One label covers escalation and
  expansion alike; 241 groups.
- **They cannot tell whether a group is a control arm in 277 of 552 cases**, mainly because posted
  results groups and registered arm labels are different naming systems that do not join.
- **They cannot distinguish "no placebo arm" from "a placebo arm the registry did not type."** Two
  groups state placebo in their own title in trials that register no placebo-typed arm.
- **They cannot support any effect estimate, cause fraction or capacity claim**, and none is computed
  here. Attribution is a precondition for such an analysis, and on this corpus it fails for most
  groups. This memo does not revive F1 (the circular denominator) or F2 (arm multiplicity and
  repeated assessments), and neither is repaired by anything above.
- **They cannot be extended by fetching more.** The single authorised cache lookup is done; this memo
  is bounded by those 12 payloads and says so.

## What this memo is not

⛔ Not a reopening of the endpoint manuscript, not a repair, not a replacement extraction, not a
recomputation of any manuscript number, and not a claim that any gate is green. It asserts no EMC
efficacy, safety, selectivity or clinical readiness. It does not analyse duplicate-NCT co-location or
record overlap, which belong to a different job on the same inputs.
