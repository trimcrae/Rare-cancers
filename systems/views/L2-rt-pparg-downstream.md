---
id: DOC-VIEW-RT-PPARG-DOWNSTREAM
title: RT-PPARG-DOWNSTREAM — PPARG downstream-effector (repurpose TZDs)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could a PPARγ-directed agent act on a downstream effector of the fusion?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-PPARG-DOWNSTREAM — PPARG downstream-effector (repurpose TZDs)

**Family:** [ST-REPURPOSING](L1-st-repurposing.md) · **state:** ✓ blocked · computed · confidence low · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/target-route-options.md`](../../research/manuscripts/target-route-options.md#route-5--downstream-of-the-fusion-pparg-and-the-transactivated-nodes)): ★ keep; direction unresolved

## Scientific rationale

If the fusion drives its phenotype partly through PPARγ signalling, then an approved agent acting on that axis reaches the driver's output without touching the driver. Repurposing a well-characterised drug class is far cheaper than any new modality.

## Remaining unknowns

- The direction is unresolved rather than refuted: in EMC the fusion appears to turn PPARγ on, so an agonist may be redundant. Nobody has read the direction in EMC tissue.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| An EMC expression readout of the PPARγ axis | ⛔ none built | **no** | BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer
- **BLK-R4-BINDS** — R4 — nothing is known to bind the cryptic pocket at all

## Readiness — what this could become today

**`internal_note`**

Its central premise is directionally unresolved. Publishing a repurposing hypothesis whose sign is unknown would be exactly the over-claim the language rules exist to prevent.

**Missing:**
- a directional read of the PPARγ axis in EMC

## Strategic timing — the wait equation

**Recommendation: `wait`**

One cheap measurement settles it, and no amount of reasoning substitutes for the sign of an effect. Working further on a hypothesis whose direction is unknown is effort that a single dataset would render moot.

| horizon | effect |
|---|---|
| Six months | None unless data lands. |
| Two years | Settled either way by an EMC dataset. |
| Cost trend | flat |
| Automation outlook | Automatic re-grade on new data. |

**Revisit when:**
- **TECH-EMC-EXPRESSION-DATA** — A fetchable public EMC RNA-seq or proteomics deposit beyond the single existing model, enabling a target-regulon readout and per-a *(expected 2029, basis `speculative`)*

## Closure

`premise_false` — ⚠ Scoped: the DIRECTION is unresolved, not refuted — in EMC the fusion turns PPARG on, so an agonist may be redundant. An EMC expression read settles it either way.

## Best next action

Keep with the direction flagged as unresolved — the premise is scoped as unresolved, NOT refuted, and those must not be conflated.

*Cost:* $0

[← ST-REPURPOSING](L1-st-repurposing.md) · [← L0](L0-ecosystem.md)
