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

The curated cohorts report ten-year all-cause survival of 65-70% against a ten-year disease-specific survival near 85%. Within the one series that measures both on the same patients, a registry cause-of-death split gives a competing share of 21.7% of deaths at ten years (relative survival independently gives 23.0%; an earlier retrieval read this as 39.4% and is superseded, per the paper's own Appendix A.1). A cohort diagnosed in its fifties and sixties and surviving five to seven years even after metastasis accrues an ordinary person's cardiovascular and second-cancer risk for a very long time, and no route on this board is aimed at any of it.

## Remaining unknowns

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

**`preprint`**

The background check is folded in and consistent with background mortality (per-stratum ratios 0.97 and 1.04, both including 1 in a wide CI on 4 and 1 events respectively), and the result is written into the paper's own S3.6 -- 'It did not refute it.' What keeps this below journal_submission is not this route's own validation but that PUB-MORTALITY-MECHANISM as a whole has not been through this repository's hardening rounds yet; the second required_validation item (a cause-of-death breakdown) stays genuinely blocked on BLK-NO-EMC-DATA.

## Where this route ends — the paper

**[PUB-MORTALITY-MECHANISM](L3-publications.md)** — [What kills patients with extraskeletal myxoid chondrosarcoma, and the survival available to tumour-directed therapy: a cause-of-death and relative-survival analysis of the published record](../../research/manuscripts/emc-mortality-mechanisms-paper.md)

`contributing` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The arithmetic that bounds every other route in the portfolio: what a perfect antitumour therapy could add, and what it could not touch.

**The paper would claim:** In extraskeletal myxoid chondrosarcoma the published record does not state a mechanism for most recorded deaths; where it does, competing causes and second malignancies are the largest identifiable category and respiratory failure is not dominant. Between a fifth and a third of deaths after diagnosis are not attributed to the tumour -- a figure relative survival and registry cause attribution agree on despite sharing no input -- so the survival available to all antitumour therapy taken together is bounded at 6.7 percentage points in localised disease against 31.0 in metastatic disease.

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

CORRECTED 2026-09-03: this field was stale, carried over from before the branch that registered this route closed the check it describes. The background-mortality check is CLOSED, not open -- both the whole-cohort 10-year check (ratio 1.77) and the per-stratum horizon-matched check (ratios 0.97, 1.04) are run and folded into research/manuscripts/emc-mortality-decomposition.json, and the paper quotes the per-stratum result in S3.6 ('It did not refute it'). Nothing route-specific remains actionable today; the second required_validation item (cause-of-death breakdown) is blocked on BLK-NO-EMC-DATA, and the paper's remaining path is PUB-MORTALITY-MECHANISM's own hardening/publish_bar route, not a per-route action.

*Cost:* $0

[← ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) · [← L0](L0-ecosystem.md)
