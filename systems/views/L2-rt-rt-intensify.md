---
id: DOC-VIEW-RT-RT-INTENSIFY
title: RT-RT-INTENSIFY — Radiotherapy intensification (particle therapy, brachytherapy, radiosensitisation, hyperthermia)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is this disease's contested radiosensitivity a question about dose, or about the quality and delivery of dose?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-RT-INTENSIFY — Radiotherapy intensification (particle therapy, brachytherapy, radiosensitisation, hyperthermia)

**Family:** [ST-LOCOREGIONAL](L1-st-locoregional.md) · **state:** ✓ blocked · computed · confidence low · verified 2026-08-09

**Grade** (owned by [`research/modalities/emc-locoregional-eligibility.json`](../../research/modalities/emc-locoregional-eligibility.json)): ◐ THE PROBLEM IS SIZED AND THE DOSE-RESPONSE IS NOT (2026-08-09). Local recurrence across four non-overlapping series is a substantial minority — so the problem this route addresses is real — but the per-cohort rates span a wide range, and one of the pooled series reports LOCOREGIONAL recurrence specifically while the others report recurrence unqualified. ⛔ The pooled recurrence figure is therefore a MIXTURE of endpoints and is the weaker of the two quantities this arithmetic produced. No dose, modality or margin data is curated anywhere, so the radioresistance reappraisal this route proposes cannot be built from the registry.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_RT_INTENSIFY["✓ RT-RT-INTENSIFY"]:::fam
  BLK_NO_CURATED_CLINICAL_DATA{{"BLK-NO-CURATED-CLINICAL-DATA — The clinical facts these r…"}}:::blk
  BLK_NO_CURATED_CLINICAL_DATA --> RT_RT_INTENSIFY
  TECH_RECONSTRUCTED_IPD(["TECH-RECONSTRUCTED-IPD<br/>expected 2026H2"]):::tech
  TECH_RECONSTRUCTED_IPD -.-> BLK_NO_CURATED_CLINICAL_DATA
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

## Scientific rationale

This repository's own record contains a live contradiction about whether radiotherapy does anything in this disease — two registries and the largest series disagree. Every prior treatment of that question has been about whether to give radiotherapy. No prior sweep considered that the answer might be dose quality, dose geometry or radiosensitisation, and the one striking combination response in the literature is itself a radiotherapy combination that was previously recorded only as a confound.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-LOCOREGIONAL-ELIGIBILITY` | local recurrence is a substantial minority across four non-overlapping series, but the pooled figure mixes locoregional-specific and unqualified recurrence endpoints and no dose, modality or margin data is curated | `direct` |

## Remaining unknowns

- Whether the recurrence heterogeneity is dose-related at all, which needs per-patient radiotherapy detail that no cohort carries.
- Whether brachytherapy and particle-therapy arms exist in this histology, which has not been searched in the particle registries.
- How much of the pooled recurrence figure is margin status rather than radioresistance — one series names margins as its main risk factor and this pooling cannot separate them.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| The eligibility arithmetic from the curated cohorts | ⛔ none built | yes | — |
| A clinical series in this histology, which only a collaborating centre could assemble | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-CURATED-CLINICAL-DATA** | `insufficient_data` | `TECH-RECONSTRUCTED-IPD` |

## Readiness — what this could become today

**`internal_note`**

The endpoint mixture and the absent dose data mean the reappraisal's regression has no inputs, even though the problem it addresses is now sized.

**Missing:**
- per-patient dose and modality data, which none of the curated series publishes
- a particle-registry search by histology

## Where this route ends — the paper

**[PUB-LOCOREGIONAL](L3-publications.md)** — *Anatomical selectivity in an indolent, extremity-primary, lung-metastasising sarcoma* (unwritten)

`contributing` · ◔ `outlined` · aimed at `preprint`

**This route contributes:** One of the anatomical-selectivity strategies a disease that is extremity-primary, lung-metastasis-dominant and indolent is unusually well matched to.

**The paper would claim:** A disease that is extremity-primary, lung-metastasis-dominant and slow enough for local control to matter is unusually well matched to locoregional and radiation-based treatment, and a portfolio containing no physical intervention at all had never assessed any of it.

**It is not written because:** ⚠ ITS BLOCKER WAS HALF RIGHT, AND THE HALF IT GOT WRONG IS THE INTERESTING ONE. The arithmetic ran on 2026-08-09 under the repository's binding pooling contract, and it splits cleanly: the SIZE OF THE PROBLEM is computable and now computed — roughly a third of localised patients develop distant disease and a substantial minority recur locally, each pooled over three or four non-overlapping series with its heterogeneity range shown. ⛔ But the ELIGIBILITY criteria are not extractable, because they were never curated: no cohort carries a primary anatomical site field, metastatic site appears once in free text rather than as data, and no cohort records lesion burden or time-to-metastasis. So the paper has its denominator and not its numerator. ⭐ That is still writable and is arguably a better paper: the argument, the sized problem, and an explicit statement of which single curation step would convert it into an eligible fraction — which is $0 for the open-access series. ⛔ Superseded, retained: "the eligibility arithmetic has not been extracted from the curated cohorts yet", which reads as though extraction were the missing step. For two of the three quantities no extraction could have produced them.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The remaining steps are $0 curation and literature search, both self-doable.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-LOCOREGIONAL](L1-st-locoregional.md), which is where these are asserted — a family limitation binds every route inside it.*

- Anatomical selectivity works only for anatomically confined disease, so every route here is limited to a subset of patients whose size has not been established in this disease.
- The portfolio contains no physical intervention of any kind, so it holds no instrument, no prior result and no reviewer competence in this family — the in-silico half of every route here is literature synthesis rather than computation.
- A modality dosed per unit volume but delivered per cell is penalised in a matrix-dominated tumour with few cells per unit volume, and that correction has already closed one route in this area.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Best next action

Search the particle registries by histology, which is $0 and is the only input to the reappraisal that does not need per-patient data.

*Cost:* $0

[← ST-LOCOREGIONAL](L1-st-locoregional.md) · [← L0](L0-ecosystem.md)
