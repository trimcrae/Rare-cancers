---
id: DOC-VIEW-RT-6MP
title: RT-6MP — 6-mercaptopurine / AF-1 agonism of the fusion
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could 6-mercaptopurine act on the fusion through the mechanism reported for wild-type NR4A3?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-6MP — 6-mercaptopurine / AF-1 agonism of the fusion

**Family:** [ST-REPURPOSING](L1-st-repurposing.md) · **state:** ✓ closed · scoped · confidence high · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md#2--the-ranked-list|tier4-6mp)): ✕ CLOSED 2026-08-03 — 6-MP acts through the AF-1, the domain the fusion replaces

## Scientific rationale

Registered with its refutation. The reported mechanism acts through the AF-1 domain — and the fusion REPLACES the AF-1 with EWSR1's low-complexity region. A ligand whose entire mechanism lives in a domain the disease deletes cannot act on the disease protein.

## Remaining unknowns

- Nothing is open. The mechanism's domain is absent from the fusion by construction, so no capability reopens it.

## Readiness — what this could become today

**`internal_note`**

Closed definitionally; the output is the reasoning, which is a useful worked example of why wild-type pharmacology does not transfer to a fusion.

## Strategic timing — the wait equation

**Recommendation: `closed`**

Permanently closed. The domain the mechanism needs is the domain the fusion replaces.

## Closure

`definitional` — 6-MP acts through the AF-1, and the fusion REPLACES the AF-1 with EWSR1's low-complexity region. A ligand whose whole mechanism lives in a domain the disease deletes cannot act on the chimera at any dose. ⚠ Scoped: this closes 6-MP, NOT LBD-directed modulation.

## Best next action

Nothing. Cite the closure — it is the clearest example in the register of wild-type pharmacology failing to transfer.

*Cost:* $0

[← ST-REPURPOSING](L1-st-repurposing.md) · [← L0](L0-ecosystem.md)
