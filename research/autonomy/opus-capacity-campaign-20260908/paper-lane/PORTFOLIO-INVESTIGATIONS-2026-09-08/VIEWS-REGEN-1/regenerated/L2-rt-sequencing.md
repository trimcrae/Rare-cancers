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

**Family:** [ST-STRATEGY](L1-st-strategy.md) · **state:** ✓ parked · computed · confidence moderate · verified 2026-08-28

**Grade** (owned by [`research/manuscripts/endpoint/emc-systemic-therapy-pooling.json`](../../research/manuscripts/endpoint/emc-systemic-therapy-pooling.json)): ⛔ THE PUBLISHED RECORD CANNOT SUPPORT A SEQUENCING CLAIM, AND SAYING SO PRECISELY IS THE RESULT (2026-08-09). No randomised evidence exists for any systemic therapy in this disease: all prospective cohorts are single-arm or single-arm within a master protocol, and the one randomised dataset that touches the disease randomised translocation sarcomas as a class with no EMC patient in its control arm. Every pooled denominator is under sixty patients worldwide, ever, and two of the pools rest on single-digit EMC subsets whose intervals span almost the entire range. ⭐ The between-cohort response range runs from zero to a majority, which is why the artifact REFUSES the all-regimen pool rather than reporting it — and that refusal, not an ordering, is what this route can honestly contribute.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_SEQUENCING["✓ RT-SEQUENCING"]:::fam
  BLK_NO_CURATED_CLINICAL_DATA{{"BLK-NO-CURATED-CLINICAL-DATA — Three of these six clinica…"}}:::blk
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
- ⭐ ANSWERED 2026-08-26, AND MORE NARROWLY THAN THE QUESTION ASSUMED. Superseded, retained: "Whether the absence of a sequencing evidence base has itself been stated anywhere in the field's literature, which would determine whether this is a finding or a restatement." Checked against the field's most recent comprehensive EMC review (Remiszewski et al. 2025, PMC12504171, in literature-cache slug emc-radiotherapy-2026-08-26). ⛔ THE SIMPLE VERSION OF THIS FINDING WOULD HAVE BEEN FALSE: that review states evidence limitations repeatedly and carefully — 'the available data to support improved outcomes with perioperative chemotherapy is very limited', 'the current evidence does not support the routine use of neoadjuvant/adjuvant chemotherapy in EMC', 'Without randomised trials, it remains unclear whether immunotherapy can provide a meaningful survival benefit', 'definitive evidence on metastasectomy for EMC is limited', and 'most clinical trials include EMC within broader sarcoma trials, making it difficult to gather disease-specific data'. The field is not unaware of its evidence problem. ⭐ WHAT IS NOT STATED IS THE ORDERING SPECIFICALLY: the string 'sequenc' does not occur in that review at all, and where it does order agents — 'to reduce practice variability, we suggest: observe indolent, asymptomatic metastatic disease; use doxorubicin ± ifosfamide first-line for symptomatic or rapidly progressive disease per STS guidance; favour pazopanib after anthracycline failure' — it attaches no evidence-limitation statement to the ORDER, and derives it by extrapolation from soft-tissue-sarcoma guidance rather than from EMC data. ⇒ This route's negative is a FINDING rather than a restatement, but a narrower one than 'nobody has said the evidence is thin': the gap is that the limitation has never been scoped to SEQUENCING. ⚠ That is not a charge against the review, which is explicit that it is extrapolating and which cites EMC-specific activity where it has it.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| ⛔ TAKEN 2026-08-09 and sharpened 2026-08-26 — the $0 analysis and registry sweep this route named. It produced the pooling artifact's refusal to report an all-regimen figure, and the check against the field's most recent comprehensive EMC review. Recorded as taken so the row stops reading as an open feasible-today step (AUT-PD-086). | ⛔ none built | yes | — |
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

Unchanged in substance and sharpened in content: report the negative, now with the specific gap it fills — the field states its evidence limitations for adjuvant chemotherapy, immunotherapy and metastasectomy, and states none for the ORDER in which agents are given, while recommending one. ⛔ Whether and where to publish that is a judgement call about what we publish, not a technical one, and it is not settled here.

*Cost:* $0

[← ST-STRATEGY](L1-st-strategy.md) · [← L0](L0-ecosystem.md)
