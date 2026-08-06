---
id: DOC-VIEW-RT-HDAC-BET
title: RT-HDAC-BET — HDAC / BET to lower fusion expression
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could an epigenetic agent lower fusion expression?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-HDAC-BET — HDAC / BET to lower fusion expression

**Family:** [ST-REPURPOSING](L1-st-repurposing.md) · **state:** ✓ parked · concept · confidence high · verified 2026-08-06

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md)): Tier 3 — not fusion-selective; a class effect, not a fusion-SELECTIVITY result

## What has to land for this route to move

```mermaid
flowchart LR
  RT_HDAC_BET["✓ RT-HDAC-BET"]:::fam
  BLK_CLASS_INHERITANCE{{"BLK-CLASS-INHERITANCE — Class inheritance, not an EMC mea…"}}:::blk
  BLK_CLASS_INHERITANCE --> RT_HDAC_BET
  TECH_VIRTUAL_CELL(["TECH-VIRTUAL-CELL<br/>expected 2028"]):::tech
  TECH_VIRTUAL_CELL -.-> BLK_CLASS_INHERITANCE
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

✓ Already cleared by this route: `BLK-PARALOGUE-DDG`, `BLK-TERNARY-GEOMETRY`.

## Scientific rationale

Registered with its refutation attached, because the idea recurs. Lowering expression of a fusion via a broad epigenetic mechanism is not fusion-selective by construction: the mechanism does not distinguish the chimera from anything else the drug class affects.

## Remaining unknowns

- Whether the class has non-selective activity in EMC. NOT closed by this route: Iwata 2025's 221-drug screen in a patient-derived EMC line returned panobinostat and romidepsin among its top hits, and candidates.json carries the open question of PDX/in-vivo activity. This closure covers fusion selectivity only.
- No NR4A3 fusion has been tested for the phenotype — the transfer argument rests on sarcoma-wide DepMap.

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-CLASS-INHERITANCE** | `insufficient_data` | `TECH-VIRTUAL-CELL` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-TRABECTEDIN](L2-rt-trabectedin.md) | whether the closure is about molecular selectivity or about clinical activity | `BLK-CLASS-INHERITANCE` | trabectedin is also a chromatin-acting drug that is not molecularly fusion-selective, and it stays live because its claim is clinical activity; this route is closed only on the SELECTIVITY claim |

## Readiness — what this could become today

**`internal_note`**

Closed on a definitional argument; the output is the reasoning.

## Where this route ends — the paper

**[PUB-CLOSED-ROUTES](L3-publications.md)** — [Seven routes closed on argument rather than on experiment — the negative record of an EWSR1::NR4A3 route search](../../research/manuscripts/closed-routes-negative-record.md)

`contributing` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** A definitional closure on lowering expression of a driver whose expression is not the discriminating feature.

**The paper would claim:** A route can be closed rigorously without an experiment when the closure is definitional or is arithmetic over a fixed measured fact, and separating those permanent closures from the merely instrument-limited ones is what keeps a portfolio from re-litigating settled questions — with wild-type NR4A3 pharmacology failing to transfer to the chimera as the worked example.

## Strategic timing — the wait equation

**Recommendation: `monitor`**

Any non-selective cytotoxic use of these classes is a different claim and is outside this program's scope; nothing here asserts activity in EMC. No HDAC or BET inhibitor is approved in sarcoma, and no BET inhibitor is approved at all.

**Revisit when:**
- **TECH-VIRTUAL-CELL** — A virtual-cell or perturbation model that predicts held-out knockdown phenotype in a cell type it was not trained on *(expected 2028, basis `extrapolated`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-REPURPOSING](L1-st-repurposing.md), which is where these are asserted — a family limitation binds every route inside it.*

- EMC is nearly absent from public functional-genomics data, so mechanism fit is argued from class membership rather than measured in this disease.
- Several routes here rest on a direction of effect that has never been read in EMC tissue; an expression readout would settle them cheaply and does not exist.
- A repurposing hypothesis is a hypothesis. Nothing here asserts efficacy in EMC.

## Closure

`premise_false` — A class effect on fusion EXPRESSION is not fusion-SELECTIVE. ⛔ RE-FILED 2026-08-06 (route framing audit): this was `definitional`, but it names no fact about an object — it rests on a MEASUREMENT, `depmap-sarcoma-dependency.json` (BET/CDK pan-essential, no selectivity window), which is a sarcoma-wide TRANSFER PRIOR and not EMC data. The identical artifact and the identical sentence are filed `premise_false` and revivable on RT-SYNLETH-DEP. One artifact cannot be a permanent definitional fact on one route and a revivable measured premise on another. ⚠ Scoped: this closes the FUSION-SELECTIVITY claim, not non-selective activity — the repo holds a fact-checked EMC ex-vivo result for the class (Iwata 2025, 221-drug screen in a patient-derived EMC line: panobinostat, romidepsin, brigatinib).

## Best next action

Nothing. Cite the closure when the idea resurfaces.

*Cost:* $0

[← ST-REPURPOSING](L1-st-repurposing.md) · [← L0](L0-ecosystem.md)
