---
id: DOC-VIEW-RT-RIPTAC
title: RT-RIPTAC — RIPTAC — bind the tumour protein, poison an essential one
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can a bifunctional molecule bind NR4A3 and hold an essential protein hostage, killing only cells that express the fusion?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-RIPTAC — RIPTAC — bind the tumour protein, poison an essential one

**Family:** [ST-PROXIMITY](L1-st-proximity.md) · **state:** ○ parked · concept · confidence low · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md#routes-813--why-each-sits-in-tier-3|route8)): Tier 3 — needs paralogue selectivity AND a med-chem campaign; strictly worse than TCIP on both

## Scientific rationale

A RIPTAC does not degrade anything: it forms a complex that poisons an essential protein, so the cell dies only where the tumour protein is present. It converts a selectivity problem into a lethality problem, which is attractive because partial selectivity still gives a therapeutic effect.

## Remaining unknowns

- Whether the paralogue selectivity this needs is achievable — it needs the same margin the program cannot measure.
- Whether a medicinal-chemistry campaign is even conceivable for one person with no bench.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A measurable paralogue selectivity margin | ⛔ none built | **no** | BLK-PARALOGUE-DDG |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-PARALOGUE-DDG** | `requires_better_simulation_accuracy` | `TECH-FE-CRYPTIC-POCKET` |
| **BLK-INDUCED-COMPLEX** | `requires_better_structure_prediction` | `TECH-COFOLD-ASSEMBLY` |
| **BLK-R4-BINDS** | `requires_wet_lab` | `TECH-EMC-MODEL-ACCESS` |

## Readiness — what this could become today

**`internal_note`**

It needs both the selectivity the program cannot measure and a chemistry campaign it cannot run. It is strictly harder than the proximity routes above it on both axes.

**Missing:**
- paralogue selectivity
- a chemistry programme

## Strategic timing — the wait equation

**Recommendation: `monitor`**

Strictly dominated by the induced-proximity routes: it needs everything they need plus a medicinal-chemistry campaign. There is no state of the world where this is the right next thing while they are still blocked.

| horizon | effect |
|---|---|
| Six months | None. |
| Two years | Only via the same free-energy advance that unblocks the whole family. |
| Cost trend | flat |
| Automation outlook | The chemistry half is not automatable at this program's scale. |

**Revisit when:**
- **TECH-FE-CRYPTIC-POCKET** — A binding free-energy method — alchemical or ML — with a published known-answer validation on cryptic or induced-fit pockets, repr *(expected 2028, basis `extrapolated`)*

## Closure

`instrument_limit` — It needs the paralogue selectivity the program cannot measure, plus a med-chem campaign.

## Best next action

Keep registered. Do not build while the routes it is dominated by are still blocked.

*Cost:* $0

[← ST-PROXIMITY](L1-st-proximity.md) · [← L0](L0-ecosystem.md)
