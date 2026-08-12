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

**Grade** (owned by [`research/manuscripts/endpoint/emc-systemic-therapy-pooling.json`](../../research/manuscripts/endpoint/emc-systemic-therapy-pooling.json)): ⛔ THE PUBLISHED RECORD CANNOT SUPPORT A SEQUENCING CLAIM, AND SAYING SO PRECISELY IS THE RESULT (2026-08-09). No randomised evidence exists for any systemic therapy in this disease: all prospective cohorts are single-arm or single-arm within a master protocol, and the one randomised dataset that touches the disease randomised translocation sarcomas as a class with no EMC patient in its control arm. Every pooled denominator is under sixty patients worldwide, ever, and two of the pools rest on single-digit EMC subsets whose intervals span almost the entire range. ⭐ The between-cohort response range runs from zero to a majority, which is why the artifact REFUSES the all-regimen pool rather than reporting it — and that refusal, not an ordering, is what this route can honestly contribute.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_SEQUENCING["✓ RT-SEQUENCING"]:::fam
  BLK_NO_CURATED_CLINICAL_DATA{{"BLK-NO-CURATED-CLINICAL-DATA — The clinical facts these r…"}}:::blk
  BLK_NO_CURATED_CLINICAL_DATA --> RT_SEQUENCING
  TECH_RECONSTRUCTED_IPD(["TECH-RECONSTRUCTED-IPD<br/>expected 2026H2"]):::tech
  TECH_RECONSTRUCTED_IPD -.-> BLK_NO_CURATED_CLINICAL_DATA
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
| **BLK-NO-CURATED-CLINICAL-DATA** | `insufficient_data` | `TECH-RECONSTRUCTED-IPD` |

## Readiness — what this could become today

**`internal_note`**

A route whose deliverable is a negative about evidence quality is complete when that negative is precise, and it now is.

**Missing:**
- nothing at the analysis level — the question was asked and the record answered that it cannot support the claim

## Where this route ends — the paper

**[PUB-STRATEGY-ARCH](L3-publications.md)** — [Eligible but unfindable — trials that admit an ultra-rare sarcoma while listing conditions that never name it](../../research/manuscripts/care-delivery/emc-trial-reachability.md)

`contributing` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** One of the variables a clinician actually controls in a cancer that will never have a randomised trial — when, in what order, and whether the patient can reach anything.

**The paper would claim:** For a cancer that will never have a randomised trial, the variables a clinician actually controls — when, in what order, and whether the patient can reach a trial at all — are treatable as research questions, and a portfolio whose every endpoint is a publication needs the step after publication registered as a route.  ⚠ THE DRAFTED PAPER COVERS THE REACHABILITY VARIABLE ONLY. The endpoint's claim spans three variables — scheduling, sequencing and reachability — and the other two are now graded as closed (RT-SCHEDULING definitional, RT-SEQUENCING instrument_limit). Their findings are real and publishable (four medians that cannot be pooled by contract, four PFS figures circulating attributed to agents that did not produce them, and a refusal to pool that is itself the result) but they are NOT in the drafted manuscript yet. ⛔ Recorded here rather than left for a reader to discover, because `drafted` on an endpoint whose paper covers one of its three routes would otherwise read as more finished than it is.

## Strategic timing — the wait equation

**Recommendation: `monitor`**

Only individual-patient data could change this, and it is not obtainable here.

| horizon | effect |
|---|---|
| Cost trend | flat |

**Revisit when:**
- **TECH-RECONSTRUCTED-IPD** — Patient-level survival data recovered from published Kaplan-Meier curves, at a quality this disease's series can actually support *(expected 2026H2, basis `evidence_based`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-STRATEGY](L1-st-strategy.md), which is where these are asserted — a family limitation binds every route inside it.*

- Nothing in this family produces a new agent, so the ceiling of every route here is bounded by what the existing agents can do.
- Scheduling and sequencing questions are normally settled by randomised trials, and this disease will not have one — so every route here ends in a modelled or observational argument whose limits must travel with it.
- The reachability routes act on institutions rather than on biology, which is a domain where this program has no track record and where a wrong answer is not falsifiable by computation.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Closure

`instrument_limit` — Set 2026-08-09. No randomised evidence exists for any systemic therapy in this disease, every pooled denominator is under sixty patients worldwide ever, and two pools rest on single-digit EMC subsets whose intervals span almost the whole range. The instrument here is the published record and it cannot support an ordering — `instrument_limit` rather than `premise_false`, because the premise is not refuted, it is unanswerable with what exists. ⭐ The refusal to pool is itself the contribution.

## Best next action

Report the negative in the strategy paper: the sequencing question in this disease has no evidence base, stated with the denominators that make it so.

*Cost:* $0

[← ST-STRATEGY](L1-st-strategy.md) · [← L0](L0-ecosystem.md)
