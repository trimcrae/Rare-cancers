---
id: DOC-VIEW-RT-TXN-CDK
title: RT-TXN-CDK — Transcriptional CDK dependency (CDK7, CDK9, CDK12/13)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is a fusion whose entire mechanism is transactivation more dependent on the transcriptional CDKs than the normal cells around it?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-TXN-CDK — Transcriptional CDK dependency (CDK7, CDK9, CDK12/13)

**Family:** [ST-DEPENDENCY](L1-st-dependency.md) · **state:** ○ parked · computed · confidence moderate · verified 2026-08-09

**Grade** (owned by [`research/modalities/census-route-expression-grading.json`](../../research/modalities/census-route-expression-grading.json)): ⛔ CLOSED ON THE AXIS THAT MATTERS (2026-08-09). Supported on abundance — CDK7 module and transcriptional output higher in EMC on both platforms — and then the dependency screen this row asked for ran the same day: across the 91 screened sarcoma lines CDK7 and CDK9 are dependencies in 100% ⛔ DENOMINATOR CORRECTED 2026-08-27: this grade said 176 sarcoma lines. 176 is the number of sarcoma MODELS in DepMap 24Q4; only 91 of them carry CRISPR gene-effect data, and every fraction here is computed over those 91. The repository caught this identical error in the MTAP/PRMT5 manuscript on 2026-08-09/10 -- the day after this grade was written -- and the correction never reached the graph., mean gene effect -1.85 and -1.46. Pan-essential. The elevation buys no window.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_TXN_CDK["○ RT-TXN-CDK"]:::fam
  BLK_CLASS_INHERITANCE{{"BLK-CLASS-INHERITANCE — Class inheritance, not an EMC mea…"}}:::blk
  BLK_CLASS_INHERITANCE --> RT_TXN_CDK
  TECH_VIRTUAL_CELL(["TECH-VIRTUAL-CELL<br/>expected 2028"]):::tech
  TECH_VIRTUAL_CELL -.-> BLK_CLASS_INHERITANCE
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_TXN_CDK
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

The driver acts by transactivating target promoters, and transcriptional CDK dependency is the best-established vulnerability of fusion-driven sarcomas as a class. The census found no route, no prior sweep and no technique-class table here had ever named it, which makes this the largest single gap in the class the portfolio should most obviously have covered.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CENSUS-ROUTE-GRADING` | the transcriptional CDK modules are elevated in EMC on both platforms AND are dependencies in 100% of 176 sarcoma lines — the second reading is what closes the route | `class_inherited` |

## Remaining unknowns

- Whether any therapeutic index exists for a pan-essential transcriptional kinase, which is a question about the class in every disease and not about this one.
- Whether the EMC elevation is a cellularity or proliferation artefact, which this data cannot exclude.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A class-inheritance argument over the transcriptional CDKs using the sarcoma dependency prior already committed here | ⛔ none built | yes | — |
| A measurement in a fusion-positive EMC model | ⛔ none built | **no** | BLK-NO-WET-LAB, BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-CLASS-INHERITANCE** | `insufficient_data` | `TECH-VIRTUAL-CELL` |
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`internal_note`**

A pan-essential target with no window is a closed line, and its value is as a paragraph in the census paper's negative half.

**Missing:**
- nothing — the question was asked and answered

## Where this route ends — the paper

**[PUB-TXN-DEPENDENCY](L3-publications.md)** — [Transcriptional and proteostatic dependency of a fusion transcription factor — what a no-wet-lab program can and cannot establish](../../research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md)

`primary` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The half of the paper that argues from what the driver IS: a transcriptional oncoprotein should be more dependent on the transcriptional machinery than the cell it sits in.

**The paper would claim:** A fusion oncoprotein whose entire mechanism is transactivation, and whose structure is a chimera of two domains that never evolved together, predicts dependencies on the transcriptional machinery and on the chaperone system — and for both, ABUNDANCE AND DEPENDENCY DISAGREE IN OPPOSITE DIRECTIONS. The transcriptional half is the most concordant elevation in the census and closes completely on dependency, being pan-essential with no selectivity. The chaperone half is an internally contradictory elevation that survives weakly for a reason abundance alone could not show. Reading only the first axis would have given a confident and wrong answer in both cases, which is the transferable result.

## Strategic timing — the wait equation

**Recommendation: `monitor`**

The decisive observation has been taken and it went against the route: the target is pan-essential across sarcoma lines, so the EMC elevation buys no window. ⚠ What would reopen it is not a better inhibitor but a way to tell an EMC-SPECIFIC consequence apart from the consequence every line shares — which is what a perturbation model that predicts held-out phenotype would supply, and it is the technology that retires this route's own class-inheritance blocker.

| horizon | effect |
|---|---|
| Cost trend | flat |

**Revisit when:**
- **TECH-VIRTUAL-CELL** — A virtual-cell or perturbation model that predicts held-out knockdown phenotype in a cell type it was not trained on *(expected 2028, basis `extrapolated`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-DEPENDENCY](L1-st-dependency.md), which is where these are asserted — a family limitation binds every route inside it.*

- The dependency transfer prior came back negative on the available data — a measured premise, revivable only by EMC-specific data.
- One route rests on class inheritance: no NR4A3 fusion has been tested for the phenotype it assumes.
- There is one EMC model in public dependency data, with no CRISPR data, so this family's in-silico half is bounded by a sample size of one.

## Best next action

Report it as a closed line: elevated and pan-essential is not an opportunity.

*Cost:* $0

[← ST-DEPENDENCY](L1-st-dependency.md) · [← L0](L0-ecosystem.md)
