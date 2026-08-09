---
id: DOC-VIEW-RT-HYPOXIA-PRODRUG
title: RT-HYPOXIA-PRODRUG — Hypoxia-activated prodrugs
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is the hypoxic fraction of this hypovascular, matrix-dominated tumour large enough to activate a prodrug selectively?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-HYPOXIA-PRODRUG — Hypoxia-activated prodrugs

**Family:** [ST-MICROENV](L1-st-microenv.md) · **state:** ✓ ready · computed · confidence moderate · verified 2026-08-09

**Grade** (owned by [`research/modalities/census-route-expression-grading.json`](../../research/modalities/census-route-expression-grading.json)): ⭐ Premise SUPPORTED at the level this data reaches (2026-08-09): a canonical HIF-target metagene scores higher in EMC than in comparator sarcomas on BOTH platforms, 15/15 and 14/15 genes readable. The only route of six graded this day to be concordantly supported.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_HYPOXIA_PRODRUG["✓ RT-HYPOXIA-PRODRUG"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_HYPOXIA_PRODRUG
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

This repository has already accepted that a hypovascular matrix-dominated tumour is a good niche fit for hypoxia-directed treatment — it said so when grading engineered bacteria, where the fit was real and the decisive objection was that no in-silico instrument could be brought to bear. That objection does not hold here, because a hypoxia signature is readable in expression data already on disk. The class has a negative randomised soft-tissue-sarcoma record that any assessment must lead with.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CENSUS-ROUTE-GRADING` | EMC tumour tissue scores higher on a curated canonical HIF-target metagene than comparator sarcomas, concordantly on two independent array platforms | `direct` |

## Remaining unknowns

- Whether a transcriptional hypoxia signature corresponds to a hypoxic FRACTION large enough to reduce a prodrug, which no expression dataset can answer.
- Whether the class's negative randomised soft-tissue-sarcoma record was a mechanism failure or a patient-selection failure — which decides whether a biomarker-selected retry is coherent at all.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| The expression lookup that grades this route's premise | ⛔ none built | yes | — |
| A measurement of the matrix compartment in EMC tissue | ⛔ none built | **no** | BLK-NO-WET-LAB, BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`preprint`**

A supported premise is not a result about a drug. What is publishable is the observation plus the selection argument, and the class's own negative trial has to lead it.

**Missing:**
- a read of the randomised sarcoma record for whether selection or mechanism failed — a literature question, not a compute one

## Where this route ends — the paper

**[PUB-MATRIX-ADDRESS](L3-publications.md)** — *The myxoid matrix as an address rather than an obstacle* (unwritten)

`contributing` · ○ `unwritten` · aimed at `preprint`

**This route contributes:** One of the handles the matrix offers — an epitope, a biosynthetic pathway or a hypoxic niche — none of which requires the fusion protein to be druggable.

**The paper would claim:** The matrix that defines this tumour histologically has been treated in the therapeutic literature almost entirely as a barrier to drug delivery, and it admits at least three distinct handles — an epitope, a biosynthetic pathway and a hypoxic niche — none of which requires the fusion protein to be druggable.

**It is not written because:** The expression read that would ground it is committed but ungraded, and the paper's whole argument depends on what that read says.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The premise is supported and the follow-up is a literature read that costs nothing, so the route can reach its stated ceiling without any external input.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-MICROENV](L1-st-microenv.md), which is where these are asserted — a family limitation binds every route inside it.*

- The screen this repository uses to nominate surface addresses ranks tumour-cell monoculture transcripts, so it has no stromal compartment in it and cannot see glycans — its silence about a matrix target is an absent reading rather than a reading of absence.
- Nothing in this family discriminates the tumour from normal tissue by the fusion, so every route here depends entirely on the matrix itself being tumour-restricted enough, and no route here has shown that.
- The matrix has never been measured in this disease as a therapeutic compartment — only described histologically — so every route in this family rests on inference from phenotype rather than on a measurement.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Best next action

Read the randomised soft-tissue-sarcoma record for the class and establish whether its failure was mechanism or patient selection.

*Cost:* $0

[← ST-MICROENV](L1-st-microenv.md) · [← L0](L0-ecosystem.md)
