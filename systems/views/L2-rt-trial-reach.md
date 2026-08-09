---
id: DOC-VIEW-RT-TRIAL-REACH
title: RT-TRIAL-REACH — Trial reachability and access pathways
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can a patient with this disease actually reach the trials and the agents that a computational result would point them toward?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-TRIAL-REACH — Trial reachability and access pathways

**Family:** [ST-STRATEGY](L1-st-strategy.md) · **state:** ✓ ready · computed · confidence moderate · verified 2026-08-09

**Grade** (owned by [`research/literature/fet-fusion-trial-eligibility-2026-08-07.json`](../../research/literature/fet-fusion-trial-eligibility-2026-08-07.json)): ⭐ THE MECHANISM IS REAL AND MEASURED, AND ITS SHARPEST FINDING IS AN ABSENCE (graded 2026-08-09 from a sweep that ran 2026-08-07). The route's premise is that a patient can be eligible for a trial that no histology search would ever surface, because eligibility is written on the fusion rather than the diagnosis — and that is now measured rather than argued: one recruiting trial is confirmed FET-fusion-family-defined with this disease absent from its listed conditions, and nine more are molecularly rather than histologically defined. ⛔ AND THE DRIVER GENE IS ABSENT FROM THE REGISTRY INDEX ENTIRELY: a registry-wide term search for it returns five studies of which NOT ONE is an oncology study — they are exercise physiology, spinal-cord injury, neck pain and a surgical series that mention the gene incidentally. No trial anywhere is indexed to this disease's driver. ⚠ Four further candidates could not be confirmed because the large screens carry no eligibility text, and non-US registries are not covered at all — the EU endpoint returns an authentication error.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_TRIAL_REACH["✓ RT-TRIAL-REACH"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_TRIAL_REACH
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

Two findings meet here. A trial exists whose eligibility is defined by the fusion family this disease belongs to while its listed conditions do not name the disease, so no histology-based search reaches it — a reachability problem, and reachability is something a paper can fix. And the portfolio names publication as its endpoint everywhere while never registering the mechanism by which a published hypothesis becomes a treated patient, which leaves the chain from result to patient with a missing link nobody owns.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-FET-TRIAL-ELIGIBILITY` | one confirmed fusion-family-defined recruiting trial and nine molecularly-defined trials admit this disease while never listing it as a condition, and a registry-wide search for the driver gene returns no oncology study at all | `direct` |

## Remaining unknowns

- Whether the four unconfirmed candidates are genuinely fusion-eligible, which needs one per-trial eligibility-text read — $0, and dispatched 2026-08-09.
- What the non-US registries hold, which this screen does not cover: the EU endpoint returns an authentication error and was not reachable.
- Whether any of these trials would in practice accept a patient with this histology, which is each trial team's decision and not a registry fact.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| ⛔ TAKEN 2026-08-07 — the registry sweep for eligibility criteria naming fusion families rather than histologies | ⛔ none built | yes | — |
| Per-trial eligibility-text reads for the four unconfirmed candidates | ⛔ none built | yes | — |
| Coverage of non-US registries, which need an authenticated endpoint | ⛔ none built | **no** | — |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`internal_note`**

The finding is solid and the screen's own limits are stated. What is missing is coverage rather than validity.

**Missing:**
- confirmation of four candidates, dispatched and $0
- non-US registry coverage, which needs an authenticated endpoint this programme does not have

## Where this route ends — the paper

**[PUB-STRATEGY-ARCH](L3-publications.md)** — *Scheduling, sequencing and reachability as treatment variables in an ultra-rare cancer* (unwritten)

`contributing` · ◔ `outlined` · aimed at `preprint`

**This route contributes:** One of the variables a clinician actually controls in a cancer that will never have a randomised trial — when, in what order, and whether the patient can reach anything.

**The paper would claim:** For a cancer that will never have a randomised trial, the variables a clinician actually controls — when, in what order, and whether the patient can reach a trial at all — are treatable as research questions, and a portfolio whose every endpoint is a publication needs the step after publication registered as a route.

**It is not written because:** ⚠ ITS BLOCKER IS RETIRED AND ONE OF ITS ROUTES IS NOW THE MOST ACTIONABLE THING IN THE PORTFOLIO. All four routes are graded as of 2026-08-09, and two of the three '$0 analyses not run' had in fact run on 2026-08-07 and been committed without any route reading them. ⭐ THE REACHABILITY ROUTE IS READY AND ITS FINDING IS PUBLISHABLE WITHOUT ANY NEW SCIENCE: one confirmed fusion-family-defined recruiting trial and nine molecularly-defined trials admit this disease while never listing it as a condition — so a patient searching their own diagnosis would find none of them — and a registry-wide search for the driver gene returns five studies of which not one is oncology. ⛔ The other three are negatives, and they are clean ones: the scheduling model's named input does not exist and may not be built, because the evidence contract refuses to merge time-anchored endpoints — what exists is four separate medians, one printed by its source with no interval, no range and no number at risk, plus four PFS figures that circulate attributed to agents that did not produce them, one of which is a median FOLLOW-UP. Sequencing has no evidence base at all: no randomised evidence for any systemic therapy, every pooled denominator under sixty patients worldwide ever. ⛔ Superseded, retained: "three of its four routes have not had their $0 analyses run, and the fourth is a registry sweep that has not been performed." The sweep was performed two days before that sentence was written.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

This is the route with a live, actionable and entirely $0 output — a list of open trials a patient with this disease could be eligible for and would never find by searching their diagnosis.

| horizon | effect |
|---|---|
| Cost trend | flat |

**Revisit when:**
- **TECH-EMC-EXPRESSION-DATA** — A fetchable public EMC RNA-seq or proteomics deposit beyond the single existing model, enabling a target-regulon readout and per-a *(expected 2029, basis `speculative`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-STRATEGY](L1-st-strategy.md), which is where these are asserted — a family limitation binds every route inside it.*

- Nothing in this family produces a new agent, so the ceiling of every route here is bounded by what the existing agents can do.
- Scheduling and sequencing questions are normally settled by randomised trials, and this disease will not have one — so every route here ends in a modelled or observational argument whose limits must travel with it.
- The reachability routes act on institutions rather than on biology, which is a domain where this program has no track record and where a wrong answer is not falsifiable by computation.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Best next action

Publish the eligibility map — this is the one route in the portfolio whose output could reach a patient without any new science, and its absence finding about the driver gene is a reportable fact about how the registry indexes rare disease.

*Cost:* $0

[← ST-STRATEGY](L1-st-strategy.md) · [← L0](L0-ecosystem.md)
