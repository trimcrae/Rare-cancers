---
id: DOC-VIEW-RT-UBIQ-SELECTIVE
title: RT-UBIQ-SELECTIVE — Fusion-selective ubiquitination — discriminate at the transfer step
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could selectivity be achieved at the ubiquitin-transfer step rather than at binding?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-UBIQ-SELECTIVE — Fusion-selective ubiquitination — discriminate at the transfer step

**Family:** [ST-PROXIMITY](L1-st-proximity.md) · **state:** ✓ parked · computed · confidence moderate · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/target-route-options.md`](../../research/manuscripts/target-route-options.md#route-13--fusion-selective-ubiquitination-closed-by-a-number-the-repo-already-owns)): ✕ closed by a measurement already committed

## Scientific rationale

Even a non-selective binder could give a selective outcome if only the fusion presents a lysine in a geometry that permits ubiquitin transfer. That would move discrimination from thermodynamics, where the margin is tiny, to geometry, where it might be categorical.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `V18` | a categorical lysine inventory, as set membership rather than energy | `direct` |

## Remaining unknowns

- Whether the transfer geometry is real: the ligase assembly it rests on was COMPOSED rather than observed, and carries tens of angstroms of positional uncertainty.
- Whether lysine identity predicts outcome at all — real degraders often ubiquitinate several lysines, and lysine-less substrates can still be degraded.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| An OBSERVED ligase assembly rather than a composed one | ⛔ none built | **no** | BLK-TERNARY-GEOMETRY |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-TERNARY-GEOMETRY** | `requires_better_structure_prediction` | `TECH-COFOLD-ASSEMBLY`, `TECH-E3-RECRUITER-STRUCTURE`, `TECH-OBSERVED-CRL` |

## Readiness — what this could become today

**`internal_note`**

No degradation-geometry claim may rest on a composed assembly, so the computed result cannot currently be reported as evidence for anything.

**Missing:**
- an observed transfer geometry

## Strategic timing — the wait equation

**Recommendation: `monitor`**

The blocking fact is about the geometry's PROVENANCE, not about sampling or effort, so no amount of work here changes it. Only a deposited structure does.

| horizon | effect |
|---|---|
| Six months | None unless a structure is deposited. |
| Two years | Plausible — cryo-EM of large flexible assemblies keeps improving. |
| Cost trend | flat |
| Automation outlook | The analysis is automated already; the input is what is missing. |

**Revisit when:**
- **TECH-OBSERVED-CRL** — An OBSERVED rather than COMPOSED ubiquitin-ligase RING and E2-ubiquitin geometry — a deposited full-assembly structure replacing a *(expected 2028, basis `speculative`)*

## Closure

`instrument_limit` — ⚠ GRADED ⏸ NOT ✕, on the register's own caveat that this is a route closed by measurements that already exist rather than a proof of impossibility. The geometry does not reach FROM AN E3 ANCHORED AT THE CRYPTIC POCKET; a different anchor re-opens the measurement.

## Best next action

Keep the categorical inventory as a disclosed-limitation supplement. Do not restate it as a degradation-geometry claim.

*Cost:* $0

[← ST-PROXIMITY](L1-st-proximity.md) · [← L0](L0-ecosystem.md)
