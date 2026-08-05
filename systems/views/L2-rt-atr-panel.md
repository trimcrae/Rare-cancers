---
id: DOC-VIEW-RT-ATR-PANEL
title: RT-ATR-PANEL — The ATR-inhibitor cell panel in EMC lines (the ask)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Will someone run a checkpoint-inhibitor sensitivity panel in EMC lines?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-ATR-PANEL — The ATR-inhibitor cell panel in EMC lines (the ask)

**Family:** [ST-DEPENDENCY](L1-st-dependency.md) · **state:** ○ blocked · scoped · confidence moderate · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md#2--the-ranked-list|tier2-rank4)): Tier 2, rank 4 — ASK, best W1 in the portfolio

## Scientific rationale

This is the experiment that converts the computed class argument into an EMC result. It is small, uses commercially available compounds, and is the best-matched ask in the portfolio: the taker gets a publishable result from a short experiment.

## Remaining unknowns

- Whether a taker exists — the material gate is an EMC line, which repositories do not supply to unaffiliated individuals.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| The panel itself | ⛔ none built | **no** | BLK-NO-WET-LAB, BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-WET-LAB** | `requires_external_collaboration` | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`experimental_proposal`**

It is already a complete experimental proposal with a costed design. What it lacks is a person with cells.

**Missing:**
- a collaborator with an EMC line

**Experiment required:**
- a checkpoint-kinase inhibitor dose-response panel in EMC lines

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The best-matched ask on the board: small, cheap for the taker, publishable for both sides. Asking costs nothing and the proposal is already written.

| horizon | effect |
|---|---|
| Six months | Only through whoever reads the assessment. |
| Two years | A solo-affordable cloud lab would remove the need for a taker — though not for the cell line. |
| Cost trend | falling |
| Automation outlook | Not automatable today; this is exactly what lab automation would change. |

**Revisit when:**
- **TECH-EMC-MODEL-ACCESS** — Access to a patient-derived EMC model through a collaborator, or through a solo-affordable cloud or robotic wet-lab service with E *(expected 2029, basis `speculative`)*
- **TECH-CLOUD-WET-LAB** — A remote robotic or cloud wet lab, rentable per experiment by an unaffiliated researcher, at a price and assay scope that covers E *(expected 2029, basis `extrapolated`)*

## Closure

`authorization` — Best taker in the portfolio and still not something this programme executes.

## Best next action

Send the ask with the assessment. It is the strongest taker-fit in the portfolio.

*Cost:* $0

[← ST-DEPENDENCY](L1-st-dependency.md) · [← L0](L0-ecosystem.md)
