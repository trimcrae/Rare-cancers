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

**Family:** [ST-CARE-DELIVERY](L1-st-care-delivery.md) · **state:** ○ blocked · concept · confidence low · verified 2026-08-23

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

This is the only route in the family that this programme cannot execute alone, and the reason is administrative rather than scientific — which is exactly the kind of blocker CLAUDE.md s0 warns is usually mis-stated. It is registered so that the dependency is visible and so nobody re-proposes it as free. ★★ AND THE SEQUENCING THAT LOOKS CIRCULAR IS NOT — SAY SO RATHER THAN TRIPPING OVER IT. This route sits BEHIND RT-DIAGNOSTIC-PATHWAY, and that route's open question needs a registry query, which reads as a cycle. It is not one. The rule is: do not use registry data for population ESTIMATES until the denominator is understood. Measuring the contamination is the DIAGNOSTIC query that establishes the denominator — it is what earns the right to the estimates, not an instance of them. A diagnostic query asks what the cohort CONTAINS; an estimate asks what the cohort IMPLIES about a population. Running the first before the second is the correct order, not a violation of it. ⚠ So the single SEER access request, when it is made, serves BOTH: the first query run under it is RT-DIAGNOSTIC-PATHWAY's frequency session (SEER 18, 2000-2018, morphology 9231, no site restriction, divided by the 459 non-bone records PMC9303001 already publishes), and only its answer decides whether this route's estimates are worth computing.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CARE-DELIVERY-EVIDENCE` | that two published SEER analyses use 9231/3 for incompatible populations, which is why access is gated on the split rather than the reverse | `direct` |

## Remaining unknowns

- What fraction of a 9231/3 registry cohort has a bone primary — the whole question, and it is RT-DIAGNOSTIC-PATHWAY's to answer first. ⭐ It is now ONE frequency session rather than a research problem: SEER 18, diagnosis years 2000-2018, ICD-O-3 morphology 9231, no site restriction, divided by 459 (PMC9303001 Supplementary Table 1, same registries and window, bone primaries already excluded).
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

**The paper would claim:** ICD-O-3 morphology code 9231/3 is read by published work as THREE mutually incompatible populations — extraskeletal myxoid chondrosarcoma of soft tissue (PMID 32856598), a histological subtype of chondrosarcoma of bone (PMID 31765367), and an intracranial mesenchymal/meningeal tumour (CBTRUS, PMC9290890) — because a morphology code carries no topography; SEER's own site/histology validation list takes the skeletal reading; and morphology-selected SEER sarcoma cohorts demonstrably contain bone primaries (PMC9303001 excluded 1,668 of 115,800, 1.44%). So registry-based EMC statistics carry a contamination whose size is unmeasured and is now reducible to one specified query.

**It is not written because:** ⭐ The CODING half is ready to write and needs nobody's cooperation: three published readings, a registry edit rule, a bone-framed cohort that states it includes EMC and has no soft-tissue location category, and a measured base rate. What is missing is the SIZE. ⚠ AND THE BLOCKER IS MIS-STATED IN THIS REPOSITORY'S HISTORY: the cheapest close is Table 1 of PMID 32856598, a SUBSCRIPTION PDF, not a data-use agreement. The DUA route is the second one, and under it the question is a single frequency session (SEER 18, 2000-2018, morphology 9231, no site restriction, divided by 459) rather than a study. ⛔ SEPARATELY, THE NAMING HALF IS WEAKER THAN THIS ENDPOINT ASSUMED: PMC7771031 already published it, and two EMC reviews place EMC under ESMO and NCCN SOFT TISSUE SARCOMA guidance, so the paper must position against prior art rather than restate it. ⚠ THE WORKING TITLE NOW UNDERSTATES THE FINDING — the code is read three ways, not two. The title is deliberately left unchanged: renaming a named paper is trimcrae's call, not an agent's (CLAUDE.md s3).

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

Do NOT seek access for THIS route yet — a contaminated denominator is worse than no denominator. ⚠ But note what the sequencing does and does not forbid: it forbids ESTIMATES, not the diagnostic query. If SEER access is obtained for RT-DIAGNOSTIC-PATHWAY's frequency session, that is the correct first use of it, and this route resumes on the answer.

*Cost:* $0

[← ST-CARE-DELIVERY](L1-st-care-delivery.md) · [← L0](L0-ecosystem.md)
