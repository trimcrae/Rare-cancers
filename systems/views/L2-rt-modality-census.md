---
id: DOC-VIEW-RT-MODALITY-CENSUS
title: RT-MODALITY-CENSUS — The modality census as a publication
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is a complete modality enumeration, graded against one ultra-rare disease, a publishable result in its own right?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-MODALITY-CENSUS — The modality census as a publication

**Family:** [ST-DISSEMINATION](L1-st-dissemination.md) · **state:** ○ ready · concept · confidence low · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/modality-census/cancer-modality-census.md`](../../research/manuscripts/modality-census/cancer-modality-census.md#2--what-the-enumeration-returned)): ⭑ Complete as a deliverable on 2026-08-09: the register, the generated view and the manuscript all exist and every pointer in them resolves.

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

The census separates classes that were considered and dismissed from classes nobody had pointed at — a distinction a literature search cannot make about itself. It is complete, it needs nobody's cooperation, and its negative half is the larger one: eighty-four classes closed on first inspection is a result the field publishes almost none of.

## Remaining unknowns

- Whether a census of this kind is judged a contribution or a review. This is a question about JOURNAL fit and about how reviewers receive it; it does not gate the aiXiv preprint, which the standing grant already covers.
- Whether the taxonomy's nineteen groups are the right partition, which is a choice and would be the first thing a reviewer contests.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Independent review of the taxonomy and of a sample of the exclusion arguments | ⛔ none built | **no** | — |

## Readiness — what this could become today

**`preprint`**

Nothing has been run. This route was registered on 2026-08-09 from the modality census and is at concept maturity, so the only honest output today is the question and its cheapest next observation.

## Where this route ends — the paper

**[PUB-MODALITY-CENSUS](L3-publications.md)** — [What oncology can do, and what reaches extraskeletal myxoid chondrosarcoma — a modality census](../../research/manuscripts/modality-census/cancer-modality-census.md)

`primary` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The paper is the census: a complete enumeration graded line by line against one disease, and the census-versus-search distinction that makes its negative half meaningful.

**The paper would claim:** A complete enumeration of cancer-treatment modality classes, graded one line at a time against a single ultra-rare fusion sarcoma, separates the classes that were considered and dismissed from the classes nobody had pointed at — a distinction a literature search cannot make about itself, and one that changes which work is worth doing next.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The deliverable exists and needs nobody's cooperation, so there is nothing to wait for on the writing side. What remains is the loop's OWN work, not a decision: three open publish_bar clauses (hardening_converged, preflight_full_green, independent_adversarial_seat), measured 4/7 on 2026-09-02. ⛔ The previous text here read 'a framing and venue decision that is trimcrae's rather than this program's', and that was wrong on both halves. The aiXiv preprint venue is settled by the standing grant in publication-authority.json; a JOURNAL submission would be his, and is a separate, later act that no bar reaches.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-DISSEMINATION](L1-st-dissemination.md), which is where these are asserted — a family limitation binds every route inside it.*

- A methods paper documents what was done and what failed. It makes no claim about whether any route would work.
- The failure record's value depends on it being complete and honest, including the results that went against the program's own thesis.

## Best next action

Close the three open publish_bar clauses for PUB-MODALITY-CENSUS, in this order: a hardening round (hardening_converged), an independent blind adversarial seat on the pinned commit (independent_adversarial_seat), then PREFLIGHT_FULL=1 recorded on that same commit (preflight_full_green). The aiXiv preprint venue is NOT a decision and never was: publication-authority.json's standing grant covers this paper and publish_bar.authority_permits returns ok=True for aixiv/submit, with PUB-ASO the single named exception.

*Cost:* $0

[← ST-DISSEMINATION](L1-st-dissemination.md) · [← L0](L0-ecosystem.md)
