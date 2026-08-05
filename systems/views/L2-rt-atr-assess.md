---
id: DOC-VIEW-RT-ATR-ASSESS
title: RT-ATR-ASSESS — The in-silico ATR vulnerability assessment (the computed half)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Does EMC inherit a replication-stress vulnerability from its FET-fusion class, and can that be assessed computationally?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-ATR-ASSESS — The in-silico ATR vulnerability assessment (the computed half)

**Family:** [ST-DEPENDENCY](L1-st-dependency.md) · **state:** ✓ ready · computed · confidence moderate · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md)): Tier 1, rank 3 — DELIVERABLE

## Scientific rationale

FET-fusion sarcomas as a class show replication-stress phenotypes that make them sensitive to inhibitors of the associated checkpoint kinase. If EMC inherits that, an existing clinical-stage drug class becomes relevant without any new chemistry. The computational half — assembling the class argument and the supporting molecular features — is complete.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `INS-IDR-CENSUS` | the low-complexity-region features the class argument rests on | `class_inherited` |
| `INS-DDR-AXIS-SCAN` | the replication-stress axis assembled for EMC from class-level evidence | `class_inherited` |

## Remaining unknowns

- Whether the class vulnerability transfers: no NR4A3 fusion has ever been tested for the phenotype.
- Whether the computed features predict drug sensitivity, which is a step nobody has validated for this class.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A cell panel in EMC lines | ⛔ none built | **no** | BLK-NO-WET-LAB, BLK-CLASS-INHERITANCE |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-CLASS-INHERITANCE** | `insufficient_data` | `TECH-VIRTUAL-CELL` |
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer
- **BLK-R4-BINDS** — R4 — nothing is known to bind the cryptic pocket at all

## Readiness — what this could become today

**`preprint`**

It is computationally complete on its own axis, and its limit — that this is class inheritance rather than an EMC measurement — is stated inside the deliverable rather than hidden. That is publishable as an assessment; it is not publishable as a finding about EMC.

**Missing:**
- an EMC-specific measurement

**Experiment required:**
- a checkpoint-kinase inhibitor sensitivity panel in EMC lines

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

Complete, honest, and does not need the cell panel to be worth publishing. Its value is precisely that it states a testable class hypothesis clearly enough for someone with cells to act on — which is how a no-wet-lab program converts computation into experiments.

| horizon | effect |
|---|---|
| Six months | None on the computation. |
| Two years | An EMC dataset would convert the class argument into a measurement. |
| Cost trend | flat |
| Automation outlook | The assessment is automated; the panel is not. |

## Best next action

Publish the assessment with the class-inheritance limit stated inside it, and pair it with the cell-panel ask.

*Cost:* $0

[← ST-DEPENDENCY](L1-st-dependency.md) · [← L0](L0-ecosystem.md)
