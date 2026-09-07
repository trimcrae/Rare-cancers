---
id: DOC-VIEW-RT-EMC-EXTERNAL-VALIDATION-AUDIT
title: RT-EMC-EXTERNAL-VALIDATION-AUDIT — External expression validation evidence in EMC
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Do the published external cohorts and normalization support the specific lineage and baseline-comparability claims assigned to them?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-EMC-EXTERNAL-VALIDATION-AUDIT — External expression validation evidence in EMC

**Family:** [ST-DISSEMINATION](L1-st-dissemination.md) · **state:** ◐ active · concept · confidence unknown · verified 2026-09-07

**Grade** (owned by [`research/autonomy/peerj-validation-audit-2026-09-07/README.md`](../../research/autonomy/peerj-validation-audit-2026-09-07/README.md)): Original source audit independently checked; baseline independent ultra review and final focused medium verification support the frozen comment. Linux full candidate verification pending.

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

Correctly distinguishing deposited cohort identity and transformed-distribution comparisons prevents the reported external evidence from being assigned support it does not establish.

## Remaining unknowns

- The accession, selected samples and source expression values actually used for Figure S6B remain unidentified.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Independent ultra review of original-source fidelity, normalization inference, claim strength and submission merit, followed by focused repairs and full publication checks. | ⛔ none built | yes | — |

## Readiness — what this could become today

**`reproducible_workflow`**

Actual baseline ultra review and focused verification support the unchanged frozen deliverables; exact release full preflight and publication-bar evidence remain pending.

**Missing:**
- Full candidate preflight and actual publication-bar evaluation

## Where this route ends — the paper

**[PUB-EMC-EXTERNAL-VALIDATION-COMMENT](L3-publications.md)** — [External evidence for an EMC prognostic gene panel: cohort identity and baseline comparability](../../research/manuscripts/external-validation/emc-external-validation-comment.md)

`primary` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** An article-specific source and inference comment with complete accession metadata checks and a stated standardization invariance argument.

**The paper would claim:** The cited public GSE6481 accession does not identify the reported EMC-versus-chondrosarcoma comparison, and separate within-cohort gene standardization cannot establish the original baseline comparability claimed from the external sequencing comparison; the actual analyzed cohort remains unresolved.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The original source discrepancy and stated normalization limitation can be evaluated now; a precise author clarification is separately coordinated.

| horizon | effect |
|---|---|
| Cost trend | unknown |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-DISSEMINATION](L1-st-dissemination.md), which is where these are asserted — a family limitation binds every route inside it.*

- A methods paper documents what was done and what failed. It makes no claim about whether any route would work.
- The failure record's value depends on it being complete and honest, including the results that went against the program's own thesis.

## Best next action

Verify the isolated release candidate on the existing Linux CI workflow, then evaluate the actual publication bar using the shared local historical objects and the exact fetched CI revision.

*Cost:* $0

[← ST-DISSEMINATION](L1-st-dissemination.md) · [← L0](L0-ecosystem.md)
