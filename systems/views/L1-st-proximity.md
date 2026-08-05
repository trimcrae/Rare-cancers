---
id: DOC-VIEW-ST-PROXIMITY
title: ST-PROXIMITY — Induced-proximity therapeutics
level: L1
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can a bifunctional molecule force NR4A3 into a productive complex with a second protein — an E3 ligase, a transcriptional effector, or an essential protein — and thereby remove or neutralise the driver?
scope: Level 1. 7 routes.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# ST-PROXIMITY — Induced-proximity therapeutics

**Thesis.** The NR4A3 ligand-binding domain does not need to be inhibited, only ENGAGED, because the therapeutic effect comes from what the molecule recruits rather than from what it blocks. This converts an undruggable transcription factor into a tractable target, at the price of needing a second binding site, a linker geometry and a productive assembly.

**Portfolio role:** `lead` · **state:** ◐ blocked · computed · confidence low

> This is the program's north star and the family that has absorbed most of its effort. It is also the family whose failures reorganise every other row in the portfolio.

## What this family may NOT be used to claim

- No molecule in this family has been shown to bind NR4A3 at all — the pocket every route here depends on has no known ligand of any kind.
- No NR4A3 ternary complex has been correctly assembled by anyone, so every geometry claim in this family is a prediction from an instrument that has never been pointed at this system.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Is this family blocked as a unit, or route by route?

```mermaid
flowchart LR
  ST_PROXIMITY["ST-PROXIMITY"]:::fam
  RT_AF3_INTERFACE["○ RT-AF3-INTERFACE"]:::fam
  ST_PROXIMITY --> RT_AF3_INTERFACE
  RT_ANDGATE["○ RT-ANDGATE"]:::fam
  ST_PROXIMITY --> RT_ANDGATE
  RT_DEGRADER["◐ RT-DEGRADER"]:::fam
  ST_PROXIMITY --> RT_DEGRADER
  RT_GLUE["○ RT-GLUE"]:::fam
  ST_PROXIMITY --> RT_GLUE
  RT_RIPTAC["○ RT-RIPTAC"]:::fam
  ST_PROXIMITY --> RT_RIPTAC
  RT_TCIP["○ RT-TCIP"]:::fam
  ST_PROXIMITY --> RT_TCIP
  RT_UBIQ_SELECTIVE["✓ RT-UBIQ-SELECTIVE"]:::fam
  ST_PROXIMITY --> RT_UBIQ_SELECTIVE

  BLK_ENDPOINT_MD{{"BLK-ENDPOINT-MD — Endpoint-MD selectivity readout E1 retu…"}}:::blk
  BLK_ENDPOINT_MD --> RT_DEGRADER
  BLK_INDUCED_COMPLEX{{"BLK-INDUCED-COMPLEX — An induced ternary/bivalent complex…"}}:::blk
  BLK_INDUCED_COMPLEX --> RT_RIPTAC
  BLK_INDUCED_COMPLEX --> RT_TCIP
  BLK_NO_WET_LAB{{"BLK-NO-WET-LAB — No wet lab and no collaborator — an ask…"}}:::blk
  BLK_NO_WET_LAB --> RT_TCIP
  BLK_NOT_FUSION_SELECTIVE[["BLK-NOT-FUSION-SELECTIVE — The route also engages the wil…"]]:::perm
  BLK_NOT_FUSION_SELECTIVE --> RT_DEGRADER
  BLK_PARALOGUE_CONTROL{{"BLK-PARALOGUE-CONTROL — The paralogue-discrimination posi…"}}:::blk
  BLK_PARALOGUE_CONTROL --> RT_DEGRADER
  BLK_PARALOGUE_DDG{{"BLK-PARALOGUE-DDG — The paralogue ΔΔG margin — selectivit…"}}:::blk
  BLK_PARALOGUE_DDG --> RT_ANDGATE
  BLK_PARALOGUE_DDG --> RT_DEGRADER
  BLK_PARALOGUE_DDG --> RT_GLUE
  BLK_PARALOGUE_DDG --> RT_RIPTAC
  BLK_PARALOGUE_DDG --> RT_TCIP
  BLK_R4_BINDS{{"BLK-R4-BINDS — R4 — nothing is known to bind the cryptic…"}}:::blk
  BLK_R4_BINDS --> RT_ANDGATE
  BLK_R4_BINDS --> RT_DEGRADER
  BLK_R4_BINDS --> RT_GLUE
  BLK_R4_BINDS --> RT_RIPTAC
  BLK_R4_BINDS --> RT_TCIP
  BLK_SELECTIVITY_CONTROL_UNAUTHORIZED{{"BLK-SELECTIVITY-CONTROL-UNAUTHORIZED — The program's only…"}}:::blk
  BLK_SELECTIVITY_CONTROL_UNAUTHORIZED --> RT_DEGRADER
  BLK_TERNARY_GEOMETRY{{"BLK-TERNARY-GEOMETRY — Ternary geometry — assembly, E3, e…"}}:::blk
  BLK_TERNARY_GEOMETRY --> RT_AF3_INTERFACE
  BLK_TERNARY_GEOMETRY --> RT_ANDGATE
  BLK_TERNARY_GEOMETRY --> RT_DEGRADER
  BLK_TERNARY_GEOMETRY --> RT_GLUE
  BLK_TERNARY_GEOMETRY --> RT_UBIQ_SELECTIVE
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
| **[RT-AF3-INTERFACE](L2-rt-af3-interface.md)**<br/>AF3 on a druggable interface | ○ parked | concept | `internal_note` | Watch for an induced-complex benchmark reporting inter-chain accuracy on post-training-horizon structures. In- |
| **[RT-ANDGATE](L2-rt-andgate.md)**<br/>AND-gate bivalent degrader (avidity coincidence detection) | ○ parked | concept | `internal_note` | Keep as a registered design option; do not build. Its value is that it names what a second arm would buy, so t |
| **[RT-DEGRADER](L2-rt-degrader.md)**<br/>NR4A3-LBD PROTAC degrader | ◐ blocked | computed | `preprint` | Ask for the decision on the binary selectivity control. It is the highest-leverage unrun item in the portfolio |
| **[RT-GLUE](L2-rt-glue.md)**<br/>Molecular glue instead of a PROTAC | ○ parked | concept | `internal_note` | Watch for a prospectively validated glue design method. Nothing to build until one exists. |
| **[RT-RIPTAC](L2-rt-riptac.md)**<br/>RIPTAC — bind the tumour protein, poison an essential one | ○ parked | concept | `internal_note` | Keep registered. Do not build while the routes it is dominated by are still blocked. |
| **[RT-TCIP](L2-rt-tcip.md)**<br/>TCIP — transcriptional chemically-induced proximity on EWSR1::NR4A3 | ○ blocked | scoped | `reproducible_workflow` | Run the paired anchor-plus-effector reach enumeration with a transcriptional-effector second terminus, reusing |
| **[RT-UBIQ-SELECTIVE](L2-rt-ubiq-selective.md)**<br/>Fusion-selective ubiquitination — discriminate at the transfer step | ✓ parked | computed | `internal_note` | Keep the categorical inventory as a disclosed-limitation supplement. Do not restate it as a degradation-geomet |
## What this family buys the portfolio — blockers it RETIRES

- **BLK-TERNARY-GEOMETRY** (`requires_better_structure_prediction`) — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Best next action

Resolve the paralogue selectivity question at its cheapest decisive point — the binary selectivity control that is built, staged and unrun.

*Cost:* $0 to decide; the run itself points at the pricing home

[← L0](L0-ecosystem.md)
