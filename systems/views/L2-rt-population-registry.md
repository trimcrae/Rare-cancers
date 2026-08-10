---
id: DOC-VIEW-RT-POPULATION-REGISTRY
title: RT-POPULATION-REGISTRY — Population cancer-registry microdata (SEER, NCDB)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: What do population-level treatment patterns and outcomes say about EMC that the published series cannot?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-POPULATION-REGISTRY — Population cancer-registry microdata (SEER, NCDB)

**Family:** [ST-CARE-DELIVERY](L1-st-care-delivery.md) · **state:** ○ blocked · concept · confidence low · verified 2026-08-09

**Grade** (owned by [`systems/graph/routes.json`](../graph/routes.json)): ⛔ GATED, AND DELIBERATELY BEHIND RT-DIAGNOSTIC-PATHWAY RATHER THAN BEHIND THE DATA-USE AGREEMENT. Registry microdata would supply the denominators, treatment patterns and facility-level variation that no case series can — but a cohort keyed on ICD-O-3 9231/3 is of unknown composition, because two published SEER studies read that one code as two mutually incompatible diseases. Access bought before the split is quantified buys a contaminated denominator. NCDB returns zero files repo-wide; SEER appears eighteen times and always as somebody else's published analysis.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_POPULATION_REGISTRY["○ RT-POPULATION-REGISTRY"]:::fam
  BLK_REGISTRY_DUA{{"BLK-REGISTRY-DUA — Population cancer-registry microdata S…"}}:::blk
  BLK_REGISTRY_DUA --> RT_POPULATION_REGISTRY
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

⚠ **1 blocker here has no technology named at all** (`BLK-REGISTRY-DUA`) — not *waiting*, **unaddressed**. A blocker with no named way out is the most expensive kind, because nothing is being watched for it.

## Scientific rationale

This is the only route in the family that this programme cannot execute alone, and the reason is administrative rather than scientific — which is exactly the kind of blocker CLAUDE.md s0 warns is usually mis-stated. It is registered so that the dependency is visible and so nobody re-proposes it as free.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CARE-DELIVERY-EVIDENCE` | that two published SEER analyses use 9231/3 for incompatible populations, which is why access is gated on the split rather than the reverse | `direct` |

## Remaining unknowns

- What fraction of a 9231/3 registry cohort has a bone primary — the whole question.
- Whether SEER records enough treatment detail to say anything about surgical completeness, which it generally does not.
- Whether facility volume is recoverable at all in the public files, which affects whether the referral question is answerable from this source.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Obtain SEER research data under a signed data-use agreement and run the topography split | ⛔ none built | **no** | BLK-REGISTRY-DUA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-REGISTRY-DUA** | `requires_authorization` | An action only trimcrae can take: register for SEER research data and sign the agreement. ⚠ DO NOT DO THIS FIRST. The prior question is whether a SEER cohort keyed on ICD-O-3 9231/3 is an EMC cohort at all, and it is measured in emc-care-delivery-evidence.json -> icd_o_9231_3: two published SEER studies read that one morphology code as two mutually incompatible diseases. Access bought before that split is quantified buys a contaminated denominator. |

## Readiness — what this could become today

**`internal_note`**

The analysis is fully specified and cannot be run. ⚠ Registering it as ready would misrepresent an administrative dependency as a scientific one.

**Missing:**
- a signed data-use agreement, which only trimcrae can obtain

## Where this route ends — the paper

**[PUB-EMC-CLASSIFICATION](L3-publications.md)** — *One code, two diseases: what registry-based extraskeletal myxoid chondrosarcoma cohorts actually contain* (unwritten)

`contributing` · ◔ `outlined` · aimed at `preprint`

**This route contributes:** The measurement that would size the contamination the classification paper can currently only demonstrate.

**The paper would claim:** ICD-O-3 morphology code 9231/3 is read by the published literature as two mutually incompatible diseases — extraskeletal myxoid chondrosarcoma in one SEER study and a histological subtype of chondrosarcoma of bone in another — so every registry-based EMC statistic carries an unquantified contamination, and the disease's name imports a tumour class it does not belong to.

**It is not written because:** ⭐ The contradiction is MEASURED and quoted from both papers' own Methods sections (emc-care-delivery-evidence.json -> icd_o_9231_3), which is enough for the argument. What is missing is the SIZE of the contamination — a SEER query split by ICD-O topography — and that needs a data-use agreement rather than a fetch.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

Every input is either committed or free to curate, and the work is $0.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-CARE-DELIVERY](L1-st-care-delivery.md), which is where these are asserted — a family limitation binds every route inside it.*

- Nothing in this family produces a new agent, so its ceiling is bounded by what the existing arsenal can do — and its floor is that the arsenal is already being used, so the gain is variance-reduction rather than a new option.
- Every route here ends in an observational or modelled argument. No randomised trial will ever settle a surgical-margin or surveillance-interval question in a disease this rare, so the limits of the design must travel with every claim.
- Reconstructed and registry data are re-expressions of published records, never new patients — they inherit every selection and publication bias of the series they came from and can correct none of it.
- Treatment associations in observational sarcoma data are dominated by confounding by indication, which runs in the direction that makes therapy look harmful; a route here that reports an unadjusted hazard has produced an artefact, not a result.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Best next action

Do NOT seek access yet. Finish RT-DIAGNOSTIC-PATHWAY first, then decide — a contaminated denominator is worse than no denominator.

*Cost:* $0

[← ST-CARE-DELIVERY](L1-st-care-delivery.md) · [← L0](L0-ecosystem.md)
