---
id: DOC-VIEW-RT-EWSR1-PROTEIN
title: RT-EWSR1-PROTEIN — Target the EWSR1 half at the protein level
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could the EWSR1 half of the fusion be targeted at the protein level?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-EWSR1-PROTEIN — Target the EWSR1 half at the protein level

**Family:** [ST-FUSION-DIRECT](L1-st-fusion-direct.md) · **state:** ✕ closed · scoped · confidence high · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/target-route-options.md`](../../research/manuscripts/target-route-options.md#route-11--target-the-ewsr1-half-at-the-protein-level)): ✕ down — relocates onto an essential gene

## What has to land for this route to move

```mermaid
flowchart LR
  RT_EWSR1_PROTEIN["✕ RT-EWSR1-PROTEIN"]:::fam
  BLK_NOT_FUSION_SELECTIVE[["BLK-NOT-FUSION-SELECTIVE — The route also engages the wil…"]]:::perm
  BLK_NOT_FUSION_SELECTIVE --> RT_EWSR1_PROTEIN
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

⛔ **1 of these is permanent** (`BLK-NOT-FUSION-SELECTIVE`) — a fact about the biology, drawn double-walled, with no way out by definition. No technology arrives to fix it.

✓ Already cleared by this route: `BLK-PARALOGUE-DDG`.

## Scientific rationale

Registered so the idea, which recurs, has a permanent answer rather than being re-argued. The EWSR1 half of the fusion IS wild-type EWSR1 sequence, so a ligand for it engages an essential housekeeping protein by construction. This is a fact about what the objects are, not a limit of any method.

## Remaining unknowns

- Nothing is open. The EWSR1 half of the fusion IS wild-type EWSR1 sequence, so this closure is a fact about what the objects are — no method advance, dataset or capability reopens it.

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
| [RT-FET-LC-LIGAND](L2-rt-fet-lc-ligand.md) | the same liability, arrived at from a different direction | `BLK-NOT-FUSION-SELECTIVE` | one targets EWSR1 as EWSR1; the other targets the FET low-complexity half as a shared class feature. Both land on wild-type EWSR1, so they share a blocker and are still separately registered because their entry points differ |
| [RT-DBD](L2-rt-dbd.md) | which protein the collateral damage lands on | `BLK-NOT-FUSION-SELECTIVE` | this route relocates onto wild-type EWSR1, an essential housekeeping protein, and closes definitionally with nothing computed; RT-DBD stays on NR4A3 and closes on a computed paralogue-identity ordering |

## Readiness — what this could become today

**`internal_note`**

It is a closed route. Its only output is the reasoning that closes it, which belongs in the closed-route register.

## Where this route ends — the paper

**[PUB-CLOSED-ROUTES](L3-publications.md)** — *Seven routes closed on argument rather than on experiment: the negative record of an EWSR1::NR4A3 route search* (unwritten)

`contributing` · ○ `unwritten` · aimed at `preprint`

**This route contributes:** A definitional closure: the half of the fusion that is shared with normal cells cannot discriminate for the tumour.

**The paper would claim:** A route can be closed rigorously without an experiment when the closure is definitional or is arithmetic over a fixed measured fact, and separating those permanent closures from the merely instrument-limited ones is what keeps a portfolio from re-litigating settled questions — with wild-type NR4A3 pharmacology failing to transfer to the chimera as the worked example.

**It is not written because:** The closures themselves are complete and each is already recorded with its grounds in the route register; what has not been done is the writing that turns seven register entries into one argument a reader outside this repository can use.

## Strategic timing — the wait equation

**Recommendation: `closed`**

Permanently closed on a fact about the sequence. No future capability reopens it, and it must appear on no watch list.

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-FUSION-DIRECT](L1-st-fusion-direct.md), which is where these are asserted — a family limitation binds every route inside it.*

- The closures here are definitional or arithmetic over a fixed fact. They may carry no revival trigger and must never appear on a watch list.
- That a route is closed says nothing about whether the disease can be treated — only that this surface is not the way.

## Closure

`definitional` — Definitional: the EWSR1 half of the fusion IS wild-type EWSR1 sequence, so a ligand for it engages wild-type EWSR1 BY CONSTRUCTION. Wild-type EWSR1 is additionally pan-essential (DepMap gene effect ~-1.2, depmap-insilico-findings.md) — but that is a SURROGATE cell-line read and is NOT the definitional leg; the closure stands without it. ⚠ Scoped: this closes targeting the EWSR1 half ON ITS OWN. It does NOT close RT-ANDGATE, whose logic requires both arms in cis, nor the junction routes RT-ASO / RT-JUNCTION-NEOANTIGEN, which act on a sequence wild-type EWSR1 does not have.

## Best next action

Nothing. Cite the closure when the idea resurfaces.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-EWSR1-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-MODEL-E7E3](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

**L5 artifacts:** [ART-FUSION-OBJECT-INVENTORY](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-FUSION-DIRECT](L1-st-fusion-direct.md) · [← L0](L0-ecosystem.md)
