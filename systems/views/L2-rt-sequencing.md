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

**Family:** [ST-STRATEGY](L1-st-strategy.md) · **state:** ○ blocked · concept · confidence low · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/cancer-modality-census.md`](../../research/manuscripts/cancer-modality-census.md#36--strategy-and-reachability)): ⭑ Registered 2026-08-09 from the modality census as a variable nobody here had treated as a question; its most likely honest output is that the published record cannot answer it.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_SEQUENCING["○ RT-SEQUENCING"]:::fam
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

## Remaining unknowns

- Whether reported prior-therapy exposure is recorded consistently enough across the published cohorts to support any ordering inference.
- Whether an observational ordering signal can be separated from the selection that produced it, which in a disease this rare it may not be.

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

**`preprint`**

Nothing has been run. This route was registered on 2026-08-09 from the modality census and is at concept maturity, so the only honest output today is the question and its cheapest next observation.

**Missing:**
- the prior-therapy-versus-outcome tabulation across the curated cohorts

## Where this route ends — the paper

**[PUB-STRATEGY-ARCH](L3-publications.md)** — *Scheduling, sequencing and reachability as treatment variables in an ultra-rare cancer* (unwritten)

`contributing` · ○ `unwritten` · aimed at `preprint`

**This route contributes:** One of the variables a clinician actually controls in a cancer that will never have a randomised trial — when, in what order, and whether the patient can reach anything.

**The paper would claim:** For a cancer that will never have a randomised trial, the variables a clinician actually controls — when, in what order, and whether the patient can reach a trial at all — are treatable as research questions, and a portfolio whose every endpoint is a publication needs the step after publication registered as a route.

**It is not written because:** Three of its four routes have not had their $0 analyses run, and the fourth is a registry sweep that has not been performed.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The next step costs nothing and needs nobody's cooperation, so there is no reason to defer it; what it returns decides whether this route is worth more than a row.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-STRATEGY](L1-st-strategy.md), which is where these are asserted — a family limitation binds every route inside it.*

- Nothing in this family produces a new agent, so the ceiling of every route here is bounded by what the existing agents can do.
- Scheduling and sequencing questions are normally settled by randomised trials, and this disease will not have one — so every route here ends in a modelled or observational argument whose limits must travel with it.
- The reachability routes act on institutions rather than on biology, which is a domain where this program has no track record and where a wrong answer is not falsifiable by computation.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Best next action

Tabulate reported prior-therapy exposure against outcome across the curated cohorts and state what the published record can and cannot support.

*Cost:* $0

[← ST-STRATEGY](L1-st-strategy.md) · [← L0](L0-ecosystem.md)
