---
id: DOC-VIEW-RT-GLUE
title: RT-GLUE — Molecular glue instead of a PROTAC
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could a molecular glue — no linker, no designed exit vector — degrade NR4A3 instead of a PROTAC?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-GLUE — Molecular glue instead of a PROTAC

**Family:** [ST-PROXIMITY](L1-st-proximity.md) · **state:** ○ parked · concept · confidence low · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/target-route-options.md`](../../research/manuscripts/target-route-options.md#route-10--a-molecular-glue-instead-of-a-protac)): ⏸ watch, do not build — removes handles and keeps the same ~1 kcal/mol claim

## Scientific rationale

A glue stabilises a protein–protein interface rather than tethering two ligands. That removes the linker, the exit vector and the covalent axis in one step — three of this program's hardest sub-problems. The cost is that a glue interface cannot be designed from the target alone, and glues are typically found by screening rather than designed.

## Remaining unknowns

- Whether a glue interface exists for this target at all.
- Whether prospective glue design works on an interface outside a method's training set — nobody has shown it.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A prospective glue design method demonstrated out of training distribution | ⛔ none built | **no** | BLK-PARALOGUE-DDG |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-PARALOGUE-DDG** | `requires_better_simulation_accuracy` | `TECH-FE-CRYPTIC-POCKET` |
| **BLK-TERNARY-GEOMETRY** | `requires_better_structure_prediction` | `TECH-COFOLD-ASSEMBLY`, `TECH-E3-RECRUITER-STRUCTURE`, `TECH-OBSERVED-CRL` |
| **BLK-R4-BINDS** | `requires_wet_lab` | `TECH-EMC-MODEL-ACCESS` |

## Readiness — what this could become today

**`internal_note`**

There is no design method to apply and no screen to run, so there is no computation whose result would mean anything.

**Missing:**
- a prospective glue design method

## Strategic timing — the wait equation

**Recommendation: `monitor`**

This is the modality most likely to arrive from someone else's screen rather than from this program's design. Watching costs nothing; building a glue programme without a design method is not a real option for one person with no bench.

| horizon | effect |
|---|---|
| Six months | None here; possibly a lot in the field. |
| Two years | Generative interface design is moving fast enough that this could become buildable. |
| Cost trend | flat |
| Automation outlook | A prospective design method would make this largely automatable, which is exactly why it is worth watching. |

**Revisit when:**
- **TECH-GLUE-DESIGN** — A validated prospective molecular-glue design method or glue-interface selectivity predictor, demonstrated on a neosubstrate inter *(expected 2027H2, basis `extrapolated`)*

## Closure

`instrument_limit` — ⚠ Graded ⏸ rather than ✕ because the block is a MISSING CAPABILITY — the modality most likely to arrive from someone else's screen.

## Best next action

Watch for a prospectively validated glue design method. Nothing to build until one exists.

*Cost:* $0

[← ST-PROXIMITY](L1-st-proximity.md) · [← L0](L0-ecosystem.md)
