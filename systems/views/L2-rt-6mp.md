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

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md)): ✕ CLOSED 2026-08-03 — 6-MP acts through the AF-1, the domain the fusion replaces

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

Registered with its refutation. The reported mechanism acts through the AF-1 domain — and the fusion REPLACES the AF-1 with EWSR1's low-complexity region. A ligand whose entire mechanism lives in a domain the disease deletes cannot act on the disease protein.

## Remaining unknowns

- Nothing is open. The mechanism's domain is absent from the fusion by construction, so no capability reopens it.

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-MONOVALENT](L2-rt-monovalent.md) | which domain the mechanism lives in | `BLK-NOT-FUSION-SELECTIVE` | ⚠ SCOPED SO IT IS NOT OVER-READ: this closes 6-MP, NOT LBD-directed modulation generally. The published LBD-borne functional result was read out on a Gal4-NOR-1-LBD construct that is itself AF-1-less |

## Readiness — what this could become today

**`internal_note`**

Closed definitionally; the output is the reasoning, which is a useful worked example of why wild-type pharmacology does not transfer to a fusion.

## Strategic timing — the wait equation

**Recommendation: `closed`**

Permanently closed. The domain the mechanism needs is the domain the fusion replaces.

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-REPURPOSING](L1-st-repurposing.md), which is where these are asserted — a family limitation binds every route inside it.*

- EMC is nearly absent from public functional-genomics data, so mechanism fit is argued from class membership rather than measured in this disease.
- Several routes here rest on a direction of effect that has never been read in EMC tissue; an expression readout would settle them cheaply and does not exist.
- A repurposing hypothesis is a hypothesis. Nothing here asserts efficacy in EMC.

## Closure

`definitional` — 6-MP acts through the AF-1, and the fusion REPLACES the AF-1 with EWSR1's low-complexity region. A ligand whose whole mechanism lives in a domain the disease deletes cannot act on the chimera at any dose. ⚠ Scoped: this closes 6-MP, NOT LBD-directed modulation.

## Best next action

Nothing. Cite the closure — it is the clearest example in the register of wild-type pharmacology failing to transfer.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-EWSR1-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-NR4A3-AF1](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

**L5 evidence:** [EV-WANSA-2003](L5-evidence-base.md#evidence--the-literature-this-program-cites)

**L5 artifacts:** [ART-TARGET-ROUTE-CENSUS](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-REPURPOSING](L1-st-repurposing.md) · [← L0](L0-ecosystem.md)
