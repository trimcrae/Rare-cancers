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

**Grade** (owned by [`research/manuscripts/emc-mtap-prmt5-hypothesis.md`](../../research/manuscripts/emc-mtap-prmt5-hypothesis.md#3--the-reading)): ⭐ SUPPORTED at the level public expression data can reach (2026-08-09). The MTAP/CDKN2A/CDKN2B locus reads LOWER in EMC on the platform where the read is powered (t=-4.06, 3/3 genes readable, 6 vs 29); the PRMT5 methylosome reads HIGHER on BOTH platforms; MAT2A sits at the 99th and 84th array percentile. ⛔ A transcript is not a copy number and this is not a copy-number call.

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
| `ART-CENSUS-ROUTE-GRADING` | the MTAP locus group reads lower in EMC than in comparator sarcomas on the platform where all three genes are readable, and the PRMT5 methylosome reads higher on both | `direct` |

## Remaining unknowns

- Whether the MTAP locus is actually deleted, which is a copy-number question that a transcript read can triage and cannot answer.
- Whether the low locus read is driven by CDKN2A alone — the neighbouring genes are silenced by mechanisms that leave MTAP intact, and only a gene-level call separates those.
- Whether an elevated methylosome implies any dependency on it, which abundance never establishes.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| MTAP immunohistochemistry on archival EMC tissue — the decisive test, routine, and it needs no fresh tissue or cell line | ⛔ none built | **no** | BLK-NO-WET-LAB |
| A gene-level copy-number or methylation read of the locus in any EMC cohort | ⛔ none built | **no** | BLK-NO-EMC-DATA |

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

**[PUB-MTAP-PRMT5](L3-publications.md)** — [MTAP-locus loss and methylosome elevation in extraskeletal myxoid chondrosarcoma — a biomarker-selected hypothesis, and the one cheap test that would settle it](../../research/manuscripts/emc-mtap-prmt5-hypothesis.md)

`primary` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The route IS the paper: the locus reading, the methylosome reading, the confound that could produce the first without the second, and the single inexpensive stain that separates them.

**The paper would claim:** Public archival expression data places the MTAP/CDKN2A/CDKN2B locus lower in extraskeletal myxoid chondrosarcoma than in comparator sarcomas and the PRMT5 methylosome higher on both readable platforms — the shape an MTAP-deleted, methylosome-loaded state makes — which raises the first genetically selected treatment hypothesis this disease has had, and which one routine immunohistochemical stain on archival tissue would confirm or kill.

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
