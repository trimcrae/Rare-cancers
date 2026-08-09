---
id: DOC-VIEW-RT-SCHEDULING
title: RT-SCHEDULING — Adaptive and metronomic scheduling of existing agents
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can the schedule of the agents this disease already receives be changed to hold it in check longer?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-SCHEDULING — Adaptive and metronomic scheduling of existing agents

**Family:** [ST-STRATEGY](L1-st-strategy.md) · **state:** ✓ blocked · computed · confidence moderate · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/emc-systemic-therapy-pooling.json`](../../research/manuscripts/emc-systemic-therapy-pooling.json)): ⚠ THE INPUT THE ROUTE NAMED DOES NOT EXIST AND MUST NOT BE BUILT (2026-08-09). The route's next step was 'build the scheduling model on the pooled progression-free-survival data already curated here'. ⛔ There is no pooled PFS and there cannot be one: the repository's evidence contract refuses to merge time-anchored endpoints, and the systemic pooling artifact refuses that pool explicitly rather than by omission. ⭐ What DOES exist is four EMC-specific medians that must be carried separately — two with confidence intervals, one with an observed range only, and one printed by its source with NO interval, NO range and NO number at risk. That is exactly a parameters-as-intervals model with one parameter that has no interval at all, which is a stronger specification than the pooled figure would have been. ⭐⭐ AND THE ROUTE ACQUIRES A SECOND, SHARPER CLAIM: four PFS figures circulate in this disease's literature attributed to agents that did not produce them — including one that is a median FOLLOW-UP quoted as a median PFS, from a paper whose own text says PFS was not reached.

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

A registered lane with no route, plus the comparator it never had. Adaptive scheduling asks nothing new of chemistry and everything of timing, it costs nothing to model, and the 2026-08-07 sweep found this disease close to an ideal indication on several independent grounds. Metronomic dosing is the obvious alternative hypothesis and had never been named here at all, so the two are registered together and evaluated against each other.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-SYSTEMIC-THERAPY-POOLING` | no pooled PFS exists or may be constructed under the evidence contract; four EMC-specific medians exist with heterogeneous dispersion reporting, one with none at all, and four widely-circulated EMC PFS figures are misattributions | `direct` |

## Remaining unknowns

- Whether a scheduling model is identifiable at all from four medians with mismatched dispersion, which is the sensitivity analysis the model exists to perform rather than a question to answer before it.
- What the growth and resistance parameters are, which no published EMC series reports and which the model must therefore carry as intervals rather than estimate.
- Whether the misattributed figures have propagated into any treatment guidance, which has not been checked and would raise the finding's weight considerably.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| The $0 analysis or registry sweep named in this route's next action | ⛔ none built | yes | — |
| Prospective confirmation, which no trial in this disease will supply | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Readiness — what this could become today

**`internal_note`**

The model has not been built. What changed is that its specification is now correct, where before it named an input the contract forbids.

**Missing:**
- nothing to start — the inputs are committed, and their shape is now known to be four separate medians rather than one pooled value

## Where this route ends — the paper

**[PUB-STRATEGY-ARCH](L3-publications.md)** — [Eligible but unfindable — trials that admit an ultra-rare sarcoma while listing conditions that never name it](../../research/manuscripts/emc-trial-reachability.md)

`contributing` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** One of the variables a clinician actually controls in a cancer that will never have a randomised trial — when, in what order, and whether the patient can reach anything.

**The paper would claim:** For a cancer that will never have a randomised trial, the variables a clinician actually controls — when, in what order, and whether the patient can reach a trial at all — are treatable as research questions, and a portfolio whose every endpoint is a publication needs the step after publication registered as a route.  ⚠ THE DRAFTED PAPER COVERS THE REACHABILITY VARIABLE ONLY. The endpoint's claim spans three variables — scheduling, sequencing and reachability — and the other two are now graded as closed (RT-SCHEDULING definitional, RT-SEQUENCING instrument_limit). Their findings are real and publishable (four medians that cannot be pooled by contract, four PFS figures circulating attributed to agents that did not produce them, and a refusal to pool that is itself the result) but they are NOT in the drafted manuscript yet. ⛔ Recorded here rather than left for a reader to discover, because `drafted` on an endpoint whose paper covers one of its three routes would otherwise read as more finished than it is.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

Every input is committed and the work is $0 model-building.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-STRATEGY](L1-st-strategy.md), which is where these are asserted — a family limitation binds every route inside it.*

- Nothing in this family produces a new agent, so the ceiling of every route here is bounded by what the existing agents can do.
- Scheduling and sequencing questions are normally settled by randomised trials, and this disease will not have one — so every route here ends in a modelled or observational argument whose limits must travel with it.
- The reachability routes act on institutions rather than on biology, which is a domain where this program has no track record and where a wrong answer is not falsifiable by computation.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Closure

`definitional` — Set 2026-08-09. The route's named input — a pooled progression-free-survival figure — cannot be built, and not for want of data: this repository's evidence contract REFUSES to merge time-anchored endpoints, so the pool is excluded by definition rather than by measurement. That is why `definitional` and not `instrument_limit`. ⭐ A result survives the closure: four EMC-specific medians carried separately, one of them printed by its source with no interval, no range and no number at risk — and four PFS figures that circulate attributed to agents that did not produce them, one of which is a median FOLLOW-UP. The closure is what makes those findable.

## Best next action

Build the two-population model with each median carried separately as its own parameter interval, and the one median that has no dispersion carried as a point with that stated — then report the four misattributed figures, which stand on their own.

*Cost:* $0

[← ST-STRATEGY](L1-st-strategy.md) · [← L0](L0-ecosystem.md)
