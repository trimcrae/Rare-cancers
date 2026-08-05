---
id: DOC-VIEW-ST-DEPENDENCY
title: ST-DEPENDENCY — Synthetic lethality and dependency
level: L1
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Does the fusion create a vulnerability elsewhere in the cell — a dependency that is not the driver itself but is only essential because the driver is present?
scope: Level 1. 3 routes.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# ST-DEPENDENCY — Synthetic lethality and dependency

**Thesis.** You do not have to drug the driver if the driver has made something else indispensable. A synthetic-lethal partner can be an ordinary, already-druggable protein, which removes both the selectivity problem and the undruggability problem at once.

**Portfolio role:** `hedge` · **state:** ✓ blocked · computed · confidence low

> The family that would most cleanly bypass everything blocking the lead family, and the one most starved by the data blocker: it is the family that most needs functional-genomics data EMC does not have.

## What this family may NOT be used to claim

- The dependency transfer prior came back negative on the available data — a measured premise, revivable only by EMC-specific data.
- One route rests on class inheritance: no NR4A3 fusion has been tested for the phenotype it assumes.
- There is one EMC model in public dependency data, with no CRISPR data, so this family's in-silico half is bounded by a sample size of one.

## Routes

| route | state | maturity | readiness today | next action |
|---|---|---|---|---|
| **[RT-ATR-ASSESS](L2-rt-atr-assess.md)**<br/>The in-silico ATR vulnerability assessment (the computed half) | ✓ ready | computed | `preprint` | Publish the assessment with the class-inheritance limit stated inside it, and pair it with the cell-panel ask. |
| **[RT-ATR-PANEL](L2-rt-atr-panel.md)**<br/>The ATR-inhibitor cell panel in EMC lines (the ask) | ○ blocked | scoped | `experimental_proposal` | Send the ask with the assessment. It is the strongest taker-fit in the portfolio. |
| **[RT-SYNLETH-DEP](L2-rt-synleth-dep.md)**<br/>Synthetic-lethal / dependency partner (BRD9 / ncBAF via EWSR1-prion→BAF) | ✓ parked | computed | `internal_note` | Keep parked on data with the transfer-prior negative stated as data-bounded, not as a biological finding. |

## Family-level bets — blockers EVERY route here inherits

If one of these is never retired, the whole family is dead. That is a different risk from any
single route failing, and it is only visible at this level.

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)

## What this family buys the portfolio — blockers it RETIRES

- **BLK-PARALOGUE-DDG** (`requires_better_simulation_accuracy`) — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-R4-BINDS** (`requires_wet_lab`) — R4 — nothing is known to bind the cryptic pocket at all
- **BLK-TERNARY-GEOMETRY** (`requires_better_structure_prediction`) — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Best next action

Keep the computed vulnerability assessment as a standalone deliverable with its limit stated inside it; it does not need the cell panel to be publishable.

*Cost:* $0

[← L0](L0-ecosystem.md)
