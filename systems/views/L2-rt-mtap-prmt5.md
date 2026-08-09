---
id: DOC-VIEW-RT-MTAP-PRMT5
title: RT-MTAP-PRMT5 — PRMT5 / MAT2A synthetic lethality (MTAP co-deletion)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Does this tumour carry the copy-number state that selects the PRMT5 axis?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-MTAP-PRMT5 — PRMT5 / MAT2A synthetic lethality (MTAP co-deletion)

**Family:** [ST-DEPENDENCY](L1-st-dependency.md) · **state:** ✓ ready · computed · confidence moderate · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/emc-mtap-prmt5-hypothesis.md`](../../research/manuscripts/emc-mtap-prmt5-hypothesis.md#3--the-reading)): ⭐ TWO INDEPENDENT LINES, neither established (2026-08-09). Route 1: a published preclinical result that PRMT5 supports EWSR1-fusion-driven transcription in a sibling sarcoma with the same 5' gene — the stronger line, and its source is an uncertified preprint. Route 2: the MTAP/CDKN2A/CDKN2B locus reads LOWER in EMC where powered (t=-4.06) and the PRMT5 methylosome HIGHER on both platforms. ⛔ Neither is a copy-number call or a dependency measurement.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_MTAP_PRMT5["✓ RT-MTAP-PRMT5"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_MTAP_PRMT5
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

One of the few genuinely biomarker-selected synthetic-lethal classes in oncology, and its selecting feature is a copy state nobody here has ever read in this disease. The question is cheap and close to binary, and it has simply never been asked.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CENSUS-ROUTE-GRADING` | the PRMT5 methylosome reads higher in EMC than in comparator sarcomas on both readable platforms, and the MTAP locus group reads lower on the platform where all three genes are readable | `direct` |

## Remaining unknowns

- Whether PRMT5's contribution in the sibling sarcoma runs through the shared EWSR1 moiety or is specific to that fusion's own DNA-binding partner — the transfer is an assumption and nothing here bridges it.
- Whether the MTAP locus is actually deleted, which a transcript read can triage and cannot answer.
- Whether the low locus read is driven by CDKN2A alone, which is near-universally co-lost with MTAP but is also lost by mechanisms that leave MTAP intact.
- Whether an elevated methylosome implies any dependency on it.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A clinical-stage PRMT5 inhibitor added to the functional screen already running on the two published patient-derived EMC models — the decisive test for the stronger route | ⛔ none built | **no** | BLK-NO-WET-LAB |
| MTAP immunohistochemistry on archival EMC tissue — routine, no fresh tissue, no cell line | ⛔ none built | **no** | BLK-NO-WET-LAB |
| A gene-level copy-number read of the locus in any EMC cohort | ⛔ none built | **no** | BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`preprint`**

The decisive observation is a stain on tissue this programme cannot obtain, so the deliverable is the hypothesis and its falsifier rather than the answer.

**Missing:**
- nothing for the preprint — it is written and every figure resolves to a committed artifact

## Where this route ends — the paper

**[PUB-MTAP-PRMT5](L3-publications.md)** — [PRMT5 in extraskeletal myxoid chondrosarcoma — a hypothesis with two independent routes in, and the cheap test that would settle the second](../../research/manuscripts/emc-mtap-prmt5-hypothesis.md)

`primary` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The route IS the paper: two independent routes into the same class, the confounds that could produce each reading without the underlying biology, and the two different cheap experiments that separate them.

**The paper would claim:** Two independent lines point at the PRMT5 methylosome in extraskeletal myxoid chondrosarcoma and neither has ever been examined in it: a published preclinical result that PRMT5 supports EWSR1-fusion-driven transcription in a sibling translocation sarcoma sharing the same 5' gene, and public expression data placing the methylosome higher and the MTAP locus lower in this disease than in comparator sarcomas. Each ends at a different inexpensive experiment, and the negative branch of each is worth publishing.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The preprint is complete and needs nobody's cooperation, and the experiment it specifies is the cheapest decisive one anywhere in this portfolio — a routine stain on archival blocks that already exist.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-DEPENDENCY](L1-st-dependency.md), which is where these are asserted — a family limitation binds every route inside it.*

- The dependency transfer prior came back negative on the available data — a measured premise, revivable only by EMC-specific data.
- One route rests on class inheritance: no NR4A3 fusion has been tested for the phenotype it assumes.
- There is one EMC model in public dependency data, with no CRISPR data, so this family's in-silico half is bounded by a sample size of one.

## Best next action

Post the preprint and put the MTAP stain in front of a group holding EMC archival material.

*Cost:* $0

[← ST-DEPENDENCY](L1-st-dependency.md) · [← L0](L0-ecosystem.md)
