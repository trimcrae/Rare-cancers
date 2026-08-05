---
id: DOC-VIEW-RT-RIBOZYME
title: RT-RIBOZYME — Trans-splicing ribozyme → suicide gene, triggered by the fusion transcript
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could a trans-splicing ribozyme convert the fusion transcript into a suicide gene?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-RIBOZYME — Trans-splicing ribozyme → suicide gene, triggered by the fusion transcript

**Family:** [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) · **state:** ○ parked · concept · confidence low · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md)): Tier 3 — vector delivery; a 2000s-era technique with no modern solid-tumour clinical footing

## Scientific rationale

A ribozyme triggered by the fusion transcript would turn the driver into the thing that kills the cell — the cleanest possible coupling of tumour identity to tumour death.

## Remaining unknowns

- Vector delivery, as above.
- Whether the technique has any modern solid-tumour footing at all — it is largely a 2000s-era approach.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Vector delivery, and a modern demonstration of the technique | ⛔ none built | **no** | BLK-VECTOR-DELIVERY |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-VECTOR-DELIVERY** | `requires_future_technology` | `TECH-VECTOR-DELIVERY` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer
- **BLK-NOT-FUSION-SELECTIVE** — The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)

## Readiness — what this could become today

**`internal_note`**

Two independent gates — delivery and a technique with no modern clinical footing — and no computation addresses either.

**Missing:**
- a solid-tumour vector
- a modern demonstration of trans-splicing ribozymes

## Strategic timing — the wait equation

**Recommendation: `monitor`**

The weaker of the two suicide-gene routes: it carries the same delivery gate plus a technique the field has largely moved on from.

| horizon | effect |
|---|---|
| Six months | None. |
| Two years | Unlikely to change. |
| Cost trend | flat |
| Automation outlook | Not automatable — the gap is delivery and a technique base. |

**Revisit when:**
- **TECH-VECTOR-DELIVERY** — A gene-therapy vector that reaches a solid tumour at therapeutic coverage *(expected 2030, basis `speculative`)*

## Closure

`instrument_limit` — Vector delivery, and a technique with no modern solid-tumour clinical footing.

## Best next action

Keep registered at low priority.

*Cost:* $0

[← ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) · [← L0](L0-ecosystem.md)
