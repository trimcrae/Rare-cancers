---
id: DOC-VIEW-RT-COMPETING-MORTALITY
title: RT-COMPETING-MORTALITY — Competing (non-EMC) mortality in a decade-scale cohort
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: What fraction of deaths after an EMC diagnosis is not caused by EMC, and is any of that fraction modifiable?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-COMPETING-MORTALITY — Competing (non-EMC) mortality in a decade-scale cohort

**Family:** [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) · **state:** ○ ready · computed · confidence low · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/emc-mortality-mechanisms.md`](../../research/manuscripts/emc-mortality-mechanisms.md)): ⭑ Registered 2026-08-09 from trimcrae's mechanism-of-death question; the family this route sits in did not exist before that day.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_COMPETING_MORTALITY["○ RT-COMPETING-MORTALITY"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_COMPETING_MORTALITY
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

The curated cohorts report ten-year all-cause survival of 65-70% against a ten-year disease-specific survival near 85%. Within the one series that measures both on the same patients, 39.4% of deaths at ten years were not EMC deaths. A cohort diagnosed in its fifties and sixties and surviving five to seven years even after metastasis accrues an ordinary person's cardiovascular and second-cancer risk for a very long time, and no route on this board is aimed at any of it.

## Remaining unknowns

- Whether the observed all-cause minus disease-specific gap is the size this cohort's age and sex explain, or is instead an artifact of pairing figures from studies that were never comparable.
- What the competing deaths actually are, which no EMC series reports -- the disease-specific classification tells you only that they were not EMC.
- Whether an EMC cohort's non-cancer mortality resembles the general population's at all, given it is selected for being fit enough to reach and survive a sarcoma diagnosis.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A background-mortality comparison against a published life table, which decides whether the gap is ordinary or is a study-comparability artifact | ⛔ none built | yes | — |
| A cause-of-death breakdown for the non-EMC deaths, which requires registry death-certificate linkage nobody here can perform | ⛔ none built | **no** | BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`internal_note`**

The competing share is computed and reproducible, but until the background check runs it cannot be distinguished from a study-comparability artifact, and an internal note is the strongest honest output.

**Missing:**
- the background-mortality comparison, which is fetched but not yet folded in

## Where this route ends — the paper

**[PUB-MORTALITY-MECHANISM](L3-publications.md)** — *What actually kills people with extraskeletal myxoid chondrosarcoma, and the share of it no targeted therapy addresses* (unwritten)

`contributing` · ◔ `outlined` · aimed at `preprint`

**This route contributes:** The arithmetic that bounds every other route in the portfolio: what a perfect antitumour therapy could add, and what it could not touch.

**The paper would claim:** In extraskeletal myxoid chondrosarcoma a large share of the deaths that follow diagnosis are not caused by the tumour, so the ceiling on the entire antitumour portfolio is a bounded number of percentage points of overall survival rather than an open-ended one -- and the remaining deaths, which no targeted route addresses, fall to mechanisms ordinary medicine already treats.

**It is not written because:** The mechanism half rests on a terminal-event corpus that is being retrieved but has not yet been read, and until each mechanism resolves to a quoted sentence the paper would be asserting a cause-of-death breakdown from a plausible story about an indolent tumour. The decomposition half is computed and holds; the two are not publishable separately, because a ceiling without a mechanism is a statistic and a mechanism without a ceiling is an anecdote.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The decomposition already runs and the check that validates it costs nothing, so there is no version of this that is worth deferring.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md), which is where these are asserted — a family limitation binds every route inside it.*

- The competing-mortality figure is arithmetic on published summary percentages from heterogeneous studies, not a competing-risks model, and most pairings cross populations.
- Every supportive-care effect size available to this family was measured in some other cancer; no EMC-specific supportive-care outcome data exists at all.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness, and a mechanism being common is not evidence that treating it changes survival.

## Best next action

Close the background-mortality check with the fetched life table and state whether the decomposition survives it.

*Cost:* $0

[← ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) · [← L0](L0-ecosystem.md)
