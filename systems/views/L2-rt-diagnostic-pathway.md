---
id: DOC-VIEW-RT-DIAGNOSTIC-PATHWAY
title: RT-DIAGNOSTIC-PATHWAY — The diagnosis itself — code contamination and a name that misleads
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Does EMC's classification — the ICD-O code it shares and the tumour class its name implies — change what patients are counted and what they are given?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-DIAGNOSTIC-PATHWAY — The diagnosis itself — code contamination and a name that misleads

**Family:** [ST-CARE-DELIVERY](L1-st-care-delivery.md) · **state:** ○ ready · computed · confidence moderate · verified 2026-08-09

**Grade** (owned by [`systems/graph/routes.json`](../graph/routes.json)): ⭐ ANSWERED, AT $0, AND THE ANSWER IS A CONTRADICTION BETWEEN TWO PUBLISHED METHODS SECTIONS. ICD-O-3 morphology code 9231/3 is queried as extraskeletal myxoid chondrosarcoma by one SEER study (PMID 32856598: 'We queried the SEER 1973-2016 database for patients with myxoid chondrosarcoma (ICD-O-3: 9231/3)') and enumerated as one histological subtype of chondrosarcoma of bone by another (PMID 31765367, beside 9220 chondrosarcoma NOS and 9221 juxtacortical). Neither misuses the code: a morphology code carries no skeletal-versus-extraskeletal information, which lives on the separate topography axis. ⭐⭐ AND THE CLINICAL HALF IS MEASURED TOO: 28% of musculoskeletal myxoid soft-tissue tumours have an INDETERMINATE preoperative diagnosis, and those patients' positive-margin rate is 37% versus 15% when malignancy is known beforehand (PMID 39899751) — a measured chain from diagnostic uncertainty to surgical failure.

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

This repository already noticed the edge of this and filed it as a one-line rejection — the IDH/ivosidenib row closed as a 'nominal name-match only ... worth one paragraph precisely because the name misleads clinicians into conventional-chondrosarcoma reasoning'. That observation is an instance of a general problem, not a curiosity: EMC is not cartilaginous, it shares a morphology code with a bone tumour, and both facts have consequences that reach a patient.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CARE-DELIVERY-EVIDENCE` | both sides of the ICD-O contradiction quoted from their own Methods sections, and the indeterminate-diagnosis margin penalty | `direct` |

## Remaining unknowns

- The SIZE of the contamination — what fraction of a 9231/3 cohort has a bone primary — which needs a topography-split registry query.
- Whether the indeterminate-diagnosis margin penalty holds in EMC specifically; the measured cohort is myxoid soft-tissue tumours broadly, of which EMC is a small part.
- Whether any treatment guidance actually imports conventional-chondrosarcoma reasoning for EMC, which has not been checked and would raise the finding's weight considerably.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Split a registry 9231/3 cohort by ICD-O topography and report the bone-versus-soft-tissue fraction | ⛔ none built | **no** | BLK-REGISTRY-DUA |
| Upgrade both quoted Methods passages from the abstract to the full text | ⛔ none built | yes | — |

## Readiness — what this could become today

**`internal_note`**

The argument is complete and citable; the contamination's SIZE is not measured, and a paper that can state the problem but not its magnitude is weaker than one that can.

**Missing:**
- nothing to start — the contradiction is measured and quoted

## Where this route ends — the paper

**[PUB-EMC-CLASSIFICATION](L3-publications.md)** — *One code, two diseases: what registry-based extraskeletal myxoid chondrosarcoma cohorts actually contain* (unwritten)

`contributing` · ◔ `outlined` · aimed at `preprint`

**This route contributes:** The whole argument: one code read as two diseases, and a measured cost of diagnostic uncertainty.

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

Upgrade the two quoted Methods passages to full text, then write the classification note — it needs nobody's cooperation and no data-use agreement.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 artifacts:** [ART-CARE-DELIVERY-EVIDENCE](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-CARE-DELIVERY](L1-st-care-delivery.md) · [← L0](L0-ecosystem.md)
