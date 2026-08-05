---
id: DOC-VIEW-ST-REPURPOSING
title: ST-REPURPOSING — Repurposing approved and late-stage agents
level: L1
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is there an already-approved drug whose mechanism plausibly fits EMC's biology and that has not been tried in EMC?
scope: Level 1. 7 routes.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# ST-REPURPOSING — Repurposing approved and late-stage agents

**Thesis.** An approved drug skips discovery, synthesis, toxicology and most of the cost of being right. For an ultra-rare disease with no targeted agent, a mechanism-fit repurposing candidate is the shortest path from a computational finding to a patient.

**Portfolio role:** `cheap_option` · **state:** ✓ blocked · computed · confidence low

> The shortest-latency family in the portfolio and the one whose blockers are almost entirely about DATA rather than chemistry. It carries the repository's earlier computational layer — a target-driven enumeration and a knowledge-graph model's zero-shot ranking — whose divergence from mechanism-based reasoning is itself a reportable limitation result.

## What this family may NOT be used to claim

- EMC is nearly absent from public functional-genomics data, so mechanism fit is argued from class membership rather than measured in this disease.
- Several routes here rest on a direction of effect that has never been read in EMC tissue; an expression readout would settle them cheaply and does not exist.
- A repurposing hypothesis is a hypothesis. Nothing here asserts efficacy in EMC.

## Is this family blocked as a unit, or route by route?

```mermaid
flowchart LR
  ST_REPURPOSING["ST-REPURPOSING"]:::fam
  RT_6MP["✓ RT-6MP"]:::fam
  ST_REPURPOSING --> RT_6MP
  RT_CARFILZOMIB["○ RT-CARFILZOMIB"]:::fam
  ST_REPURPOSING --> RT_CARFILZOMIB
  RT_HDAC_BET["○ RT-HDAC-BET"]:::fam
  ST_REPURPOSING --> RT_HDAC_BET
  RT_PPARG_DOWNSTREAM["✓ RT-PPARG-DOWNSTREAM"]:::fam
  ST_REPURPOSING --> RT_PPARG_DOWNSTREAM
  RT_RXR["✓ RT-RXR"]:::fam
  ST_REPURPOSING --> RT_RXR
  RT_TRABECTEDIN["○ RT-TRABECTEDIN"]:::fam
  ST_REPURPOSING --> RT_TRABECTEDIN
  RT_TRABECTEDIN_PPARG["○ RT-TRABECTEDIN-PPARG"]:::fam
  ST_REPURPOSING --> RT_TRABECTEDIN_PPARG

  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_CARFILZOMIB
  BLK_NO_EMC_DATA --> RT_PPARG_DOWNSTREAM
  BLK_NO_EMC_DATA --> RT_TRABECTEDIN
  BLK_NO_EMC_DATA --> RT_TRABECTEDIN_PPARG
  BLK_NO_WET_LAB{{"BLK-NO-WET-LAB — No wet lab and no collaborator — an ask…"}}:::blk
  BLK_NO_WET_LAB --> RT_TRABECTEDIN_PPARG
  BLK_NOT_FUSION_SELECTIVE[["BLK-NOT-FUSION-SELECTIVE — The route also engages the wil…"]]:::perm
  BLK_NOT_FUSION_SELECTIVE --> RT_HDAC_BET
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** ⭐ **No blocker points at the family node**, and that is the finding: the routes here are *not* held down by one shared thing. They are blocked individually, for different reasons — so retiring any one blocker frees some routes and not others, and there is no single unlock for the family.

*What this family RETIRES for the portfolio is listed below rather than drawn — it is a property of the family, not an edge between these nodes.*

## Routes

| route | state | maturity | readiness today | next action |
|---|---|---|---|---|
| **[RT-6MP](L2-rt-6mp.md)**<br/>6-mercaptopurine / AF-1 agonism of the fusion | ✓ closed | scoped | `internal_note` | Nothing. Cite the closure — it is the clearest example in the register of wild-type pharmacology failing to tr |
| **[RT-CARFILZOMIB](L2-rt-carfilzomib.md)**<br/>Carfilzomib ± anthracycline (± venetoclax) | ○ ready | concept | `internal_note` | Resolve the primary citation for the ex-vivo EMC drug-sensitivity evidence. It is the only ex-vivo EMC result  |
| **[RT-HDAC-BET](L2-rt-hdac-bet.md)**<br/>HDAC / BET to lower fusion expression | ○ closed | concept | `internal_note` | Nothing. Cite the closure when the idea resurfaces. |
| **[RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md)**<br/>PPARG downstream-effector (repurpose TZDs) | ✓ blocked | computed | `internal_note` | Keep with the direction flagged as unresolved — the premise is scoped as unresolved, NOT refuted, and those mu |
| **[RT-RXR](L2-rt-rxr.md)**<br/>RXR-heterodimer modulation of the fusion | ✓ closed | computed | `internal_note` | Nothing. The scan carries the one observation that would reopen it. |
| **[RT-TRABECTEDIN](L2-rt-trabectedin.md)**<br/>Trabectedin (± RT or combination) | ○ ready | concept | `internal_note` | Keep as cited landscape context. Do not overstate a single response. |
| **[RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md)**<br/>Trabectedin + a PPARγ agonist (all approved drugs) | ○ blocked | concept | `experimental_proposal` | Hold the ask until the PPARγ direction can be stated. Re-grade automatically when EMC expression data lands. |
## What this family buys the portfolio — blockers it RETIRES

- **BLK-PARALOGUE-DDG** (`requires_better_simulation_accuracy`) — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-R4-BINDS** (`requires_wet_lab`) — R4 — nothing is known to bind the cryptic pocket at all
- **BLK-TERNARY-GEOMETRY** (`requires_better_structure_prediction`) — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Best next action

Watch for a fetchable public EMC expression dataset — it is the single input that would convert most of this family from class-inherited argument to measurement.

*Cost:* $0

[← L0](L0-ecosystem.md)
