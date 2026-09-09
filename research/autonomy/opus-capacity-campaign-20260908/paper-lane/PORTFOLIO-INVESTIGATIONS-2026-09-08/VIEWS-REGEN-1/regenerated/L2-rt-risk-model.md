---
id: DOC-VIEW-RT-RISK-MODEL
title: RT-RISK-MODEL — A prognostic risk model for EMC
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can the prognostic factors reported piecemeal across EMC's series be combined into a stratification that would let treatment intensity be matched to risk?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-RISK-MODEL — A prognostic risk model for EMC

**Family:** [ST-CARE-DELIVERY](L1-st-care-delivery.md) · **state:** ○ ready · computed · confidence low · verified 2026-09-02

**Grade** (owned by [`systems/graph/routes.json`](../graph/routes.json)): ⭐ RE-GRADED 2026-08-26 — THE COEFFICIENTS DO NOT HAVE TO BE ESTIMATED, THEY ARE ALREADY PRINTED. This route was written as though a model had to be FITTED, which made it wait on reconstructed patient-level data. The two largest reachable open-access EMC series each print FITTED COX MODELS with hazard ratios, 95 % intervals and per-level patient counts — 7 models and 45 estimable coefficients across four endpoints, in emc-prognostic-coefficients.json. So the prognostic ORDERING is reachable today at $0.  ⛔ WHAT IS STRUCTURALLY UNREACHABLE FROM PRINT IS THE HALF A RISK MODEL IS FOR: neither paper prints a baseline hazard, or a reference-group curve with a numbers-at-risk row that one could be recovered from. Coefficients alone rank patients by risk and can never price any patient's risk — no survival probability, no nomogram, no n-year risk, and no validation, since discrimination and calibration both need patient-level outcomes. A model published from this is an ordering and must say so.  ⚠ AND THE TWO COHORTS ARE CONSISTENT RATHER THAN CORROBORATING. 11 of 12 cross-cohort comparisons agree in direction and all 12 pairs of intervals overlap, but 9 of the 12 are between intervals that BOTH include 1, and in NOT ONE does both cohorts' interval exclude 1. Only surgical margin holds its direction across four endpoints and two cohorts while reaching significance in the larger one. The single directional disagreement — sex on local recurrence — is between two null results and is not a contradiction.  No validated EMC risk model exists — `nomogram` returns zero files repo-wide and no published EMC series presents one. ⚠ Any model FITTED on a few hundred reconstructed patients would be badly overfit unless held to a handful of predictors with an honest optimism correction; a well-calibrated three-variable model is the realistic ceiling for that path.  ⚠ Superseded, retained: "INHERITS THE 2026-08-09 FEASIBILITY DOWNGRADE ON RT-IPD-SURVIVAL: only 19 of 340 EMC full texts print a Kaplan-Meier curve at all, so the reconstructed hazard this route consumes will rest on single-digit poolable curves and a few hundred patients. Whether that supports a decision-relevant model is now the route's first question rather than its last." The downgrade is still true OF THE RECONSTRUCTION PATH and is confirmed harder — neither of the two cohorts here prints a numbers-at-risk row under ANY of its 7 stratified curves, so none of them is reconstructable at all. What is superseded is the inference that the route therefore waits: it does not consume the reconstruction for its coefficients.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_RISK_MODEL["○ RT-RISK-MODEL"]:::fam
  BLK_NO_CURATED_CLINICAL_DATA{{"BLK-NO-CURATED-CLINICAL-DATA — Three of these six clinica…"}}:::blk
  BLK_NO_CURATED_CLINICAL_DATA --> RT_RISK_MODEL
  TECH_RECONSTRUCTED_IPD(["TECH-RECONSTRUCTED-IPD<br/>expected 2026H2"]):::tech
  TECH_RECONSTRUCTED_IPD -.-> BLK_NO_CURATED_CLINICAL_DATA
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

## Scientific rationale

Risk stratification is the mechanism by which every other route in this family becomes actionable — surveillance intensity, margin ambition and metastasectomy selection are all decisions about which patients, not whether. It falls out of the reconstructed dataset rather than needing an input of its own.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CARE-DELIVERY-EVIDENCE` | tumour size as a prognostic factor in the molecularly-confirmed cohort, and the absence of any published EMC risk model | `direct` |

## Remaining unknowns

- Whether any reachable EMC publication prints a baseline hazard or a reference-group curve with a numbers-at-risk row — without one, no absolute risk is computable from any number this route holds, and that is now the route's binding constraint rather than sample size.
- Whether the three free-to-read series that no automated route can fetch (emc-km-reachability-census-2026-08-25.json) print further Cox tables; the reachable coefficient set is bounded by retrieval, not by the literature.
- Whether fusion partner adds prognostic information over size and stage, which RT-PARTNER-STRAT bears on and which no series has tested jointly.
- ⚠ Superseded, retained: "Whether the covariates are even recoverable — a reconstruction returns times and event indicators, not the covariates that would stratify them, so a stratified model needs per-arm curves rather than one pooled curve." ANSWERED, and by a different instrument than the question assumed: the covariates arrive as printed Cox tables, so they never had to survive a reconstruction. The concern was correct about reconstruction and wrong that reconstruction was the only route to them.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Fit and internally validate a small model on the reconstructed dataset with an explicit optimism correction | ⛔ none built | **no** | BLK-NO-CURATED-CLINICAL-DATA |
| External validation in an independent cohort | ⛔ none built | **no** | BLK-REGISTRY-DUA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-CURATED-CLINICAL-DATA** | `insufficient_data` | `TECH-RECONSTRUCTED-IPD` |

## Readiness — what this could become today

**`internal_note`**

The coefficients are transcribed, guarded and reproducible, but a prognostic ORDERING with no baseline hazard and no validation is an internal note until it is either validated or published explicitly as an ordering. ⚠ Superseded, retained: "A reconstruction recovers times and events, NOT covariates. Stratification requires the source to have published a curve PER STRATUM, and most have not — which bounds this route more tightly than the others in the family." The first sentence stands. The second was the wrong bound: both reachable cohorts DO publish stratified curves — 7 of them — and not one carries a numbers-at-risk row, so what bounds the reconstruction path is journal reporting practice rather than stratified publishing. The route's actual bound is the missing baseline hazard.

**Missing:**
- a baseline hazard, without which the ordering cannot become a risk
- patient-level outcomes for any validation at all — discrimination and calibration both need them, and no reachable publication contains them
- ⚠ Superseded, retained: "the reconstructed dataset, and per-arm curves rather than pooled ones." Neither is what the route is missing: the printed Cox tables supply the covariates the reconstruction was wanted for.

## Where this route ends — the paper

**[PUB-CARE-DELIVERY](L3-publications.md)** — *What decides survival in extraskeletal myxoid chondrosarcoma, and what the literature has been looking at instead* (unwritten)

`contributing` · ○ `unwritten` · aimed at `preprint`

**This route contributes:** The stratification that turns the family's other three routes from observations into decisions.

**The paper would claim:** In extraskeletal myxoid chondrosarcoma the determinants of survival that have been studied least are the ones that decide it most: the completeness of the first operation, whether the diagnosis was known before it, and whether follow-up outlasts a disease that recurs for decades.

**It is not written because:** ⚠ Superseded, retained (rule 1.2): "Its four contributing routes are registered and their evidence is cited but not yet extracted. The paper needs the reconstructed survival dataset (RT-IPD-SURVIVAL) to say anything quantitative; without it, it is an argument with citations rather than a result." ⛔ BOTH HALVES ARE FALSE AS OF 2026-09-01. Six extraction artifacts exist and none of them consumes a reconstruction: 196 operated patients with a margin (research/modalities/emc-surgical-quality.json), 271 patients' primary site (emc-site-curation.json), 45 printed Cox coefficients (emc-prognostic-coefficients.json) and four printed time-to-event statistics (emc-recurrence-timing.json). RT-IPD-SURVIVAL has produced exactly one admissible curve — 11 patients, progression-free survival in advanced disease — which is the wrong shape for this paper and always was.

⭐ THE REAL REASON IT IS UNWRITTEN IS A JUDGEMENT, NOT A GAP. The paper's strongest quantitative claim — that margin decides local recurrence — is the printed conclusion of the abstract of its own largest source (PMID 40885991: "Wide resection is mandatory to reduce the risk of local recurrence of localized EMCs"). The third clause of what_it_would_claim, whether the diagnosis was known before the operation, is unstudiable in EMC from the reachable record: treatment setting is reported by no reachable series. And the working title's second half — "what the literature has been looking at instead" — is an argument with no measurement behind it. ⭐ The one free step that would change this is a term census over the 554-record corpus already committed at literature/emc-care-delivery-and-classification/ on the literature-cache branch, which is now filed as BLK-NO-FIELD-ATTENTION-MEASUREMENT.

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

⛔ ANSWERED — publish nothing standalone. Of 12 cross-cohort comparisons, 0 have both intervals excluding 1 (`emc-prognostic-coefficients.json → cross_cohort_summary`); the cohorts are consistent, not corroborating, and `absolute_risk_computable` is false and guarded. The ordering's one survivor is surgical margin, which is RT-SURGICAL-QUALITY's finding measured a second way — so it is a paragraph of that record, not its own note. ⛔ Do NOT re-attempt the reconstruction path for these covariates: neither cohort prints a numbers-at-risk row under any of its 7 stratified survival curves (masunaga 3, chiusole 4, every one refused in `emc-km-admissibility-2026-08-27.json`). ⚠ Superseded, retained: "Decide what an ordering-only prognostic statement is worth publishing as."

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 artifacts:** [ART-PROGNOSTIC-COEFFICIENTS](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-CARE-DELIVERY](L1-st-care-delivery.md) · [← L0](L0-ecosystem.md)
