---
id: DOC-VIEW-RT-RESPIRATORY-FAILURE
title: RT-RESPIRATORY-FAILURE — Progressive pulmonary metastatic burden and respiratory failure
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is the dominant mechanism of EMC death progressive respiratory failure from lung metastases, and is any part of that course symptom-treatable?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-RESPIRATORY-FAILURE — Progressive pulmonary metastatic burden and respiratory failure

**Family:** [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) · **state:** ○ ready · concept · confidence low · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/emc-mortality-mechanisms.md`](../../research/manuscripts/emc-mortality-mechanisms.md)): ⭑ Registered 2026-08-09 from trimcrae's mechanism-of-death question; the family this route sits in did not exist before that day.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_RESPIRATORY_FAILURE["○ RT-RESPIRATORY-FAILURE"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_RESPIRATORY_FAILURE
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

Distant spread in this disease is mostly to lung, and patients survive years with it, so the terminal event is reached slowly rather than suddenly. That matters for what could help: a mechanism approached over years is the one least amenable to acute rescue and most exposed to cumulative symptom-directed management -- oxygen, effusion control, airway and breathlessness management. The mechanism is asserted everywhere in the clinical prose and tabulated nowhere.

## Remaining unknowns

- Whether respiratory failure is in fact the most common terminal event, which requires reading the published case record rather than assuming it from the metastatic pattern.
- Whether any symptom-directed management of that course changes survival as opposed to changing symptoms, which has never been measured in this disease.
- How much of the terminal course is respiratory at all, given that case reports over-represent dramatic events and under-report ordinary decline.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A classified terminal-event corpus drawn from the open-access EMC literature, with each mechanism resolving to a quoted sentence | ⛔ none built | yes | — |
| A prospective symptom-directed intervention in EMC patients, which needs a clinic | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`internal_note`**

Registered 2026-08-09 at concept maturity; the honest output today is the question and its cheapest next observation.

## Where this route ends — the paper

**[PUB-MORTALITY-MECHANISM](L3-publications.md)** — *What actually kills people with extraskeletal myxoid chondrosarcoma, and the share of it no targeted therapy addresses* (unwritten)

`contributing` · ◔ `outlined` · aimed at `preprint`

**This route contributes:** The mechanism half of the paper: what the terminal event actually is, quoted from the record rather than inferred from the metastatic pattern.

**The paper would claim:** In extraskeletal myxoid chondrosarcoma a large share of the deaths that follow diagnosis are not caused by the tumour, so the ceiling on the entire antitumour portfolio is a bounded number of percentage points of overall survival rather than an open-ended one -- and the remaining deaths, which no targeted route addresses, fall to mechanisms ordinary medicine already treats.

**It is not written because:** The mechanism half rests on a terminal-event corpus that is being retrieved but has not yet been read, and until each mechanism resolves to a quoted sentence the paper would be asserting a cause-of-death breakdown from a plausible story about an indolent tumour. The decomposition half is computed and holds; the two are not publishable separately, because a ceiling without a mechanism is a statistic and a mechanism without a ceiling is an anecdote.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The retrieval is already running and the classification after it costs only reading, so this is the cheapest unanswered question in the family.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md), which is where these are asserted — a family limitation binds every route inside it.*

- The competing-mortality figure is arithmetic on published summary percentages from heterogeneous studies, not a competing-risks model, and most pairings cross populations.
- Every supportive-care effect size available to this family was measured in some other cancer; no EMC-specific supportive-care outcome data exists at all.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness, and a mechanism being common is not evidence that treating it changes survival.

## Best next action

Classify the retrieved death-cue sentences by mechanism and report the unstated fraction honestly.

*Cost:* $0

[← ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) · [← L0](L0-ecosystem.md)
