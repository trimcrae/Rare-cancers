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

**Family:** [ST-LOCOREGIONAL](L1-st-locoregional.md) · **state:** ○ blocked · concept · confidence low · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/cancer-modality-census.md`](../../research/manuscripts/cancer-modality-census.md#35--locoregional-and-radiation)): ⭑ Registered 2026-08-09 from the modality census; it attaches to a contradiction already live in this repository's record rather than opening a new question.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_RT_INTENSIFY["○ RT-RT-INTENSIFY"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_RT_INTENSIFY
  TECH_EMC_EXPRESSION_DATA(["TECH-EMC-EXPRESSION-DATA<br/>expected 2029"]):::tech
  TECH_EMC_EXPRESSION_DATA -.-> BLK_NO_EMC_DATA
  TECH_VIRTUAL_CELL(["TECH-VIRTUAL-CELL<br/>expected 2028"]):::tech
  TECH_VIRTUAL_CELL -.-> BLK_NO_EMC_DATA
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

## Scientific rationale

This repository's own record contains a live contradiction about whether radiotherapy does anything in this disease — two registries and the largest series disagree. Every prior treatment of that question has been about whether to give radiotherapy. No prior sweep considered that the answer might be dose quality, dose geometry or radiosensitisation, and the one striking combination response in the literature is itself a radiotherapy combination that was previously recorded only as a confound.

## Remaining unknowns

- Whether the existing radioresistance contradiction resolves to a dose-response relationship or to selection bias, which the reappraisal already scoped here would settle.
- Whether particle-therapy or brachytherapy series contain any myxoid or chondroid histology in reportable numbers.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| The eligibility arithmetic from the curated cohorts | ⛔ none built | yes | — |
| A clinical series in this histology, which only a collaborating centre could assemble | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`internal_note`**

Nothing has been run. This route was registered on 2026-08-09 from the modality census and is at concept maturity, so the only honest output today is the question and its cheapest next observation.

**Missing:**
- the radioresistance reappraisal's dose-response regression, extended beyond external-beam series

## Where this route ends — the paper

**[PUB-LOCOREGIONAL](L3-publications.md)** — *Anatomical selectivity in an indolent, extremity-primary, lung-metastasising sarcoma* (unwritten)

`contributing` · ○ `unwritten` · aimed at `preprint`

**This route contributes:** One of the anatomical-selectivity strategies a disease that is extremity-primary, lung-metastasis-dominant and indolent is unusually well matched to.

**The paper would claim:** A disease that is extremity-primary, lung-metastasis-dominant and slow enough for local control to matter is unusually well matched to locoregional and radiation-based treatment, and a portfolio containing no physical intervention at all had never assessed any of it.

**It is not written because:** The eligibility arithmetic it rests on has not been extracted from the curated cohorts yet, and without it the paper would be an argument with no denominator.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The next step costs nothing and needs nobody's cooperation, so there is no reason to defer it; what it returns decides whether this route is worth more than a row.

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

Build the dose-response regression for the radioresistance reappraisal including brachytherapy and particle-therapy arms, and search the particle registries by histology.

*Cost:* $0

[← ST-LOCOREGIONAL](L1-st-locoregional.md) · [← L0](L0-ecosystem.md)
