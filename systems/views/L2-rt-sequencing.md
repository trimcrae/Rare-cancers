---
id: DOC-VIEW-RT-SEQUENCING
title: RT-SEQUENCING — Treatment sequencing and line ordering
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: In what order should the agents that already have activity in this disease be given?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-SEQUENCING — Treatment sequencing and line ordering

**Family:** [ST-STRATEGY](L1-st-strategy.md) · **state:** ✓ parked · computed · confidence moderate · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/emc-systemic-therapy-pooling.json`](../../research/manuscripts/emc-systemic-therapy-pooling.json)): ⛔ THE PUBLISHED RECORD CANNOT SUPPORT A SEQUENCING CLAIM, AND SAYING SO PRECISELY IS THE RESULT (2026-08-09). No randomised evidence exists for any systemic therapy in this disease: all prospective cohorts are single-arm or single-arm within a master protocol, and the one randomised dataset that touches the disease randomised translocation sarcomas as a class with no EMC patient in its control arm. Every pooled denominator is under sixty patients worldwide, ever, and two of the pools rest on single-digit EMC subsets whose intervals span almost the entire range. ⭐ The between-cohort response range runs from zero to a majority, which is why the artifact REFUSES the all-regimen pool rather than reporting it — and that refusal, not an ordering, is what this route can honestly contribute.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_SEQUENCING["✓ RT-SEQUENCING"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_SEQUENCING
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

The registry curates several agents with disease-specific activity and says nothing about the order to give them in. In a disease where decisions are years apart, ordering is one of the few variables a clinician actually controls, and no prior sweep treated it as a question at all.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-SYSTEMIC-THERAPY-POOLING` | no randomised evidence exists in this disease, every pooled denominator is under sixty patients worldwide, and the between-cohort response range is wide enough that the repository's own pooling refuses to produce a single all-regimen figure | `direct` |

## Remaining unknowns

- Whether prior-therapy exposure is recorded against outcome in any curated cohort at a resolution that would permit any sequencing statement — it is not, at cohort level.
- Whether individual-patient data behind these series would support one, which is not this programme's to obtain.
- Whether the absence of a sequencing evidence base has itself been stated anywhere in the field's literature, which would determine whether this is a finding or a restatement.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| The $0 analysis or registry sweep named in this route's next action | ⛔ none built | yes | — |
| Prospective confirmation, which no trial in this disease will supply | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`internal_note`**

A route whose deliverable is a negative about evidence quality is complete when that negative is precise, and it now is.

**Missing:**
- nothing at the analysis level — the question was asked and the record answered that it cannot support the claim

## Where this route ends — the paper

**[PUB-STRATEGY-ARCH](L3-publications.md)** — *Scheduling, sequencing and reachability as treatment variables in an ultra-rare cancer* (unwritten)

`contributing` · ◔ `outlined` · aimed at `preprint`

**This route contributes:** One of the variables a clinician actually controls in a cancer that will never have a randomised trial — when, in what order, and whether the patient can reach anything.

**The paper would claim:** For a cancer that will never have a randomised trial, the variables a clinician actually controls — when, in what order, and whether the patient can reach a trial at all — are treatable as research questions, and a portfolio whose every endpoint is a publication needs the step after publication registered as a route.

**It is not written because:** ⚠ ITS BLOCKER IS RETIRED AND ONE OF ITS ROUTES IS NOW THE MOST ACTIONABLE THING IN THE PORTFOLIO. All four routes are graded as of 2026-08-09, and two of the three '$0 analyses not run' had in fact run on 2026-08-07 and been committed without any route reading them. ⭐ THE REACHABILITY ROUTE IS READY AND ITS FINDING IS PUBLISHABLE WITHOUT ANY NEW SCIENCE: one confirmed fusion-family-defined recruiting trial and nine molecularly-defined trials admit this disease while never listing it as a condition — so a patient searching their own diagnosis would find none of them — and a registry-wide search for the driver gene returns five studies of which not one is oncology. ⛔ The other three are negatives, and they are clean ones: the scheduling model's named input does not exist and may not be built, because the evidence contract refuses to merge time-anchored endpoints — what exists is four separate medians, one printed by its source with no interval, no range and no number at risk, plus four PFS figures that circulate attributed to agents that did not produce them, one of which is a median FOLLOW-UP. Sequencing has no evidence base at all: no randomised evidence for any systemic therapy, every pooled denominator under sixty patients worldwide ever. ⛔ Superseded, retained: "three of its four routes have not had their $0 analyses run, and the fourth is a registry sweep that has not been performed." The sweep was performed two days before that sentence was written.

## Strategic timing — the wait equation

**Recommendation: `monitor`**

Only individual-patient data could change this, and it is not obtainable here.

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

Report the negative in the strategy paper: the sequencing question in this disease has no evidence base, stated with the denominators that make it so.

*Cost:* $0

[← ST-STRATEGY](L1-st-strategy.md) · [← L0](L0-ecosystem.md)
