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

## Remaining unknowns

- Nothing is open. A ligand for a SHARED region cannot discriminate between the things that share it; that is what 'shared' means, so no capability reopens it.

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NOT-FUSION-SELECTIVE** | `fundamental_biological_limit` | *permanent* |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)

## Readiness — what this could become today

**`internal_note`**

Closed on the same definitional grounds as the EWSR1 protein route.

## Where this route ends — the paper

**[PUB-CLOSED-ROUTES](L3-publications.md)** — *Seven routes closed on argument rather than on experiment: the negative record of an EWSR1::NR4A3 route search* (unwritten)

`contributing` · ○ `unwritten` · aimed at `preprint`

**This route contributes:** The same definitional closure applied to the shared low-complexity region, which is what makes the pattern a class of argument rather than a one-off.

**The paper would claim:** A route can be closed rigorously without an experiment when the closure is definitional or is arithmetic over a fixed measured fact, and separating those permanent closures from the merely instrument-limited ones is what keeps a portfolio from re-litigating settled questions — with wild-type NR4A3 pharmacology failing to transfer to the chimera as the worked example.

**It is not written because:** The closures themselves are complete and each is already recorded with its grounds in the route register; what has not been done is the writing that turns seven register entries into one argument a reader outside this repository can use.

## Strategic timing — the wait equation

**Recommendation: `closed`**

Permanently closed. A shared region cannot discriminate between the things that share it — that is what 'shared' means.

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-FUSION-DIRECT](L1-st-fusion-direct.md), which is where these are asserted — a family limitation binds every route inside it.*

- The closures here are definitional or arithmetic over a fixed fact. They may carry no revival trigger and must never appear on a watch list.
- That a route is closed says nothing about whether the disease can be treated — only that this surface is not the way.

## Closure

`definitional` — A ligand for the SHARED FET low-complexity half binds wild-type EWSR1 by definition of 'shared'. Permanent for the same reason as the row above, reached from the other direction.

## Best next action

Nothing. Cite the closure.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-EWSR1-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

[← ST-FUSION-DIRECT](L1-st-fusion-direct.md) · [← L0](L0-ecosystem.md)
