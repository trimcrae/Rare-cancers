---
id: DOC-VIEW-ST-MORTALITY-MECHANISM
title: ST-MORTALITY-MECHANISM — Mortality-mechanism-directed and supportive care
level: L1
kind: generated
status: generated
generator: systems/systems_check.py
purpose: When an EMC patient dies, what is the proximate mechanism -- and is any of it treatable without treating the cancer?
scope: Level 1. 6 routes.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# ST-MORTALITY-MECHANISM — Mortality-mechanism-directed and supportive care

**Thesis.** Every other family here tries to stop the tumour from killing the patient. This one starts from the death certificate instead of the driver, and asks which mechanisms actually appear on it. For a disease measured in decades that reordering is not rhetorical: a therapy preventing every EMC death would raise ten-year overall survival by a bounded number of percentage points, and the deaths outside that bound are the ones nothing on this board is pointed at. The bet is that some of them are addressable by medicine that already exists and needs no discovery.

**Portfolio role:** `cheap_option` · **state:** ◐ active · computed · confidence low

> Registered 2026-08-09 on trimcrae's question. ⛔ ITS ABSENCE UNTIL NOW WAS STRUCTURAL, NOT A JUDGEMENT. The modality census grades every class on antitumour activity, so a supportive indication cannot score at all: MOD-ANTICOAGULANT is recorded `not_applicable` because it is "a supportive-care indication addressing thrombotic risk, with no antitumour claim to assess", and MOD-GLUCOCORTICOID is `excluded` as "supportive ... rather than as antitumour therapy". Both readings are correct on the census's own axis and neither is a finding about this disease. That is exactly the considered-and-dismissed versus never-pointed-at distinction the census exists to make, failing on the one question its grading criterion cannot express.

## What this family may NOT be used to claim

- The competing-mortality figure is arithmetic on published summary percentages from heterogeneous studies, not a competing-risks model, and most pairings cross populations.
- Every supportive-care effect size available to this family was measured in some other cancer; no EMC-specific supportive-care outcome data exists at all.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness, and a mechanism being common is not evidence that treating it changes survival.

## Is this family blocked as a unit, or route by route?

```mermaid
flowchart LR
  ST_MORTALITY_MECHANISM["ST-MORTALITY-MECHANISM"]:::fam
  RT_COMPETING_MORTALITY["○ RT-COMPETING-MORTALITY"]:::fam
  ST_MORTALITY_MECHANISM --> RT_COMPETING_MORTALITY
  RT_EARLY_PALLIATIVE["○ RT-EARLY-PALLIATIVE"]:::fam
  ST_MORTALITY_MECHANISM --> RT_EARLY_PALLIATIVE
  RT_HOST_FACTOR["○ RT-HOST-FACTOR"]:::fam
  ST_MORTALITY_MECHANISM --> RT_HOST_FACTOR
  RT_RESPIRATORY_FAILURE["○ RT-RESPIRATORY-FAILURE"]:::fam
  ST_MORTALITY_MECHANISM --> RT_RESPIRATORY_FAILURE
  RT_TREATMENT_HARM["○ RT-TREATMENT-HARM"]:::fam
  ST_MORTALITY_MECHANISM --> RT_TREATMENT_HARM
  RT_VTE_PROPHYLAXIS["○ RT-VTE-PROPHYLAXIS"]:::fam
  ST_MORTALITY_MECHANISM --> RT_VTE_PROPHYLAXIS

  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_COMPETING_MORTALITY
  BLK_NO_EMC_DATA --> RT_RESPIRATORY_FAILURE
  BLK_NO_EMC_DATA --> RT_TREATMENT_HARM
  BLK_NO_EMC_DATA --> RT_VTE_PROPHYLAXIS
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** ⭐ **No blocker points at the family node**, and that is the finding: the routes here are *not* held down by one shared thing. They are blocked individually, for different reasons — so retiring any one blocker frees some routes and not others, and there is no single unlock for the family.

*What this family RETIRES for the portfolio is listed below rather than drawn — it is a property of the family, not an edge between these nodes.*

## Routes

| route | state | maturity | readiness today | ends in | next action |
|---|---|---|---|---|---|
| **[RT-COMPETING-MORTALITY](L2-rt-competing-mortality.md)**<br/>Competing (non-EMC) mortality in a decade-scale cohort | ○ ready | computed | `internal_note` | [PUB-MORTALITY-MECHANISM](L3-publications.md) ◐ *contributing* | Close the background-mortality check with the fetched life table and state whether the decomposition survives  |
| **[RT-EARLY-PALLIATIVE](L2-rt-early-palliative.md)**<br/>Early specialist palliative care and structured symptom monitoring | ○ ready | concept | `internal_note` | [PUB-MORTALITY-MECHANISM](L3-publications.md) ◐ *contributing* | Read the retrieved trial set and record each effect size against the population it was measured in, marking ev |
| **[RT-HOST-FACTOR](L2-rt-host-factor.md)**<br/>Treating modifiable host conditions as de-facto EMC survival therapy | ○ ready | concept | `internal_note` | [PUB-MORTALITY-MECHANISM](L3-publications.md) ◐ *contributing* | Read the host-factor retrieval, enter each effect size against the population it was measured in, and run the  |
| **[RT-RESPIRATORY-FAILURE](L2-rt-respiratory-failure.md)**<br/>Progressive pulmonary metastatic burden and respiratory failure | ○ ready | concept | `internal_note` | [PUB-MORTALITY-MECHANISM](L3-publications.md) ◐ *contributing* | Classify the retrieved death-cue sentences by mechanism and report the unstated fraction honestly. |
| **[RT-TREATMENT-HARM](L2-rt-treatment-harm.md)**<br/>De-escalating cytotoxic therapy that has no measured EMC response | ○ ready | concept | `internal_note` | [PUB-MORTALITY-MECHANISM](L3-publications.md) ◐ *contributing* | Count treatment-attributed deaths in the terminal-event corpus and set them beside the curated response data f |
| **[RT-VTE-PROPHYLAXIS](L2-rt-vte-prophylaxis.md)**<br/>Venous thromboembolism in a lung-metastatic sarcoma population | ○ ready | concept | `internal_note` | [PUB-MORTALITY-MECHANISM](L3-publications.md) ◐ *contributing* | Count thromboembolic terminal events in the corpus and read the prophylaxis trials for a survival endpoint rat |
## Best next action

Read the retrieved terminal-event corpus and classify each quoted sentence, so the mechanism breakdown rests on sources a reader can check rather than on a plausible story about an indolent tumour.

*Cost:* $0

[← L0](L0-ecosystem.md)
