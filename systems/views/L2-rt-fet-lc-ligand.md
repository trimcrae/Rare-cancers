---
id: DOC-VIEW-RT-FET-LC-LIGAND
title: RT-FET-LC-LIGAND — A ligand for the shared FET low-complexity half
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could a ligand for the shared FET low-complexity region work?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-FET-LC-LIGAND — A ligand for the shared FET low-complexity half

**Family:** [ST-FUSION-DIRECT](L1-st-fusion-direct.md) · **state:** ✕ closed · scoped · confidence high · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md#route-15---a-ligand-for-the-shared-fet-low-complexity-half)): Tier 3 — relocates selectivity somewhere worse

## What has to land for this route to move

```mermaid
flowchart LR
  RT_FET_LC_LIGAND["✕ RT-FET-LC-LIGAND"]:::fam
  BLK_NOT_FUSION_SELECTIVE[["BLK-NOT-FUSION-SELECTIVE — The route also engages the wil…"]]:::perm
  BLK_NOT_FUSION_SELECTIVE --> RT_FET_LC_LIGAND
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

⛔ **1 of these is permanent** (`BLK-NOT-FUSION-SELECTIVE`) — a fact about the biology, drawn double-walled, with no way out by definition. No technology arrives to fix it.

✓ Already cleared by this route: `BLK-PARALOGUE-DDG`.

## Scientific rationale

Registered for the same reason as the row above. A ligand for the SHARED low-complexity half binds wild-type EWSR1 by the definition of 'shared'. It relocates the selectivity problem onto a protein that is more essential, not less.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-FUSION-OBJECT-INVENTORY` | the fusion's EWSR1 portion is wild-type EWSR1 sequence and the low-complexity region is present breakpoint-independently (K144 INVARIANT 9/9) | `direct` |

## Remaining unknowns

- Nothing is open. A ligand for a SHARED region cannot discriminate between the things that share it; that is what 'shared' means, so no capability reopens it.

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NOT-FUSION-SELECTIVE** | `fundamental_biological_limit` | *permanent* |

## Blockers this route never FACES

*This route is closed. It does not answer these blockers — its architecture never encounters them, so nothing here is a hedge the portfolio can spend.*

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-EWSR1-PROTEIN](L2-rt-ewsr1-protein.md) | the same liability, arrived at from a different direction | `BLK-NOT-FUSION-SELECTIVE` | a NEW route to this repo, proposed as a class-wide FET handle rather than as an EWSR1-specific one |

## Readiness — what this could become today

**`internal_note`**

Closed on the same definitional grounds as the EWSR1 protein route.

## Strategic timing — the wait equation

**Recommendation: `closed`**

Permanently closed. A shared region cannot discriminate between the things that share it — that is what 'shared' means.

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-FUSION-DIRECT](L1-st-fusion-direct.md), which is where these are asserted — a family limitation binds every route inside it.*

- The closures here are definitional or arithmetic over a fixed fact. They may carry no revival trigger and must never appear on a watch list.
- That a route is closed says nothing about whether the disease can be treated — only that this surface is not the way.

## Closure

`definitional` — Definitional on the shared-region leg: a ligand DEFINED by the shared FET low-complexity feature cannot discriminate among the things that share it, and the fusion's EWSR1 portion is wild-type EWSR1 sequence in all nine surviving breakpoint windows (ART-FUSION-OBJECT-INVENTORY). ⚠ THE COMPARATIVE IS NOT DEFINITIONAL: 'relocates somewhere WORSE' rests on a DepMap essentiality trade (EWSR1 gene effect ~-1.2 against NR4A1 0.5% / NR4A2 0.3% dependent) — a surrogate cell-line read, not a fact about the objects. The registry does not otherwise treat 'engages an essential protein' as fatal by construction: RT-CARFILZOMIB is `ready` on a pan-essential proteasome and RT-RIPTAC is parked rather than closed on a deliberately essential-protein mechanism. So the permanence rests on the first leg alone. ⚠ OPEN for trimcrae: whether 'worse' should be dropped from the grade, or the closure re-filed as non-permanent — see systems/AUDIT-2026-08-06-routes.md.

## Best next action

Nothing. Cite the closure.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-EWSR1-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

**L5 artifacts:** [ART-FUSION-OBJECT-INVENTORY](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-FUSION-DIRECT](L1-st-fusion-direct.md) · [← L0](L0-ecosystem.md)
