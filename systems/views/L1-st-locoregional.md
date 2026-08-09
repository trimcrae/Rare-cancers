---
id: DOC-VIEW-ST-LOCOREGIONAL
title: ST-LOCOREGIONAL — Locoregional, physical and radiation-based treatment
level: L1
kind: generated
status: generated
generator: systems/systems_check.py
purpose: If a systemic agent cannot discriminate this tumour from normal tissue, can the discrimination be made anatomically instead — by where the treatment is delivered rather than by what it binds?
scope: Level 1. 3 routes.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# ST-LOCOREGIONAL — Locoregional, physical and radiation-based treatment

**Thesis.** Every other family here tries to buy selectivity with chemistry. A beam, a perfusion circuit or a needle buys it with geometry, which is a discrimination this disease's own natural history makes unusually available: it is extremity-primary, lung-metastasis-dominant, and slow enough that local control has time to matter.

**Portfolio role:** `hedge` · **state:** ○ ready · concept · confidence low

> Minted 2026-08-09 from the modality census. The 2026-08-07 sweep named this as one of four categories structurally invisible to every prior search here -- not rejected, never queried -- and a category nothing could be filed under is a category that stays invisible.

## What this family may NOT be used to claim

- Anatomical selectivity works only for anatomically confined disease, so every route here is limited to a subset of patients whose size has not been established in this disease.
- The portfolio contains no physical intervention of any kind, so it holds no instrument, no prior result and no reviewer competence in this family — the in-silico half of every route here is literature synthesis rather than computation.
- A modality dosed per unit volume but delivered per cell is penalised in a matrix-dominated tumour with few cells per unit volume, and that correction has already closed one route in this area.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Is this family blocked as a unit, or route by route?

```mermaid
flowchart LR
  ST_LOCOREGIONAL["ST-LOCOREGIONAL"]:::fam
  RT_LIMB_PERFUSION["✓ RT-LIMB-PERFUSION"]:::fam
  ST_LOCOREGIONAL --> RT_LIMB_PERFUSION
  RT_LUNG_DIRECTED["✓ RT-LUNG-DIRECTED"]:::fam
  ST_LOCOREGIONAL --> RT_LUNG_DIRECTED
  RT_RT_INTENSIFY["✓ RT-RT-INTENSIFY"]:::fam
  ST_LOCOREGIONAL --> RT_RT_INTENSIFY

  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> ST_LOCOREGIONAL
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** 1 blocker point at the FAMILY node: every route here inherits it, so the family stands or falls as a unit on that. The rest point at individual routes.

*What this family RETIRES for the portfolio is listed below rather than drawn — it is a property of the family, not an edge between these nodes.*

## Routes

| route | state | maturity | readiness today | ends in | next action |
|---|---|---|---|---|---|
| **[RT-LIMB-PERFUSION](L2-rt-limb-perfusion.md)**<br/>Isolated limb perfusion for extremity disease | ✓ blocked | computed | `internal_note` | [PUB-LOCOREGIONAL](L3-publications.md) ◔ *contributing* | Curate primary anatomical site from the open-access pooled series, then search the perfusion literature for my |
| **[RT-LUNG-DIRECTED](L2-rt-lung-directed.md)**<br/>Lung-directed local therapy (regional perfusion, inhaled delivery, ablation) | ✓ blocked | computed | `internal_note` | [PUB-LOCOREGIONAL](L3-publications.md) ◔ *contributing* | Re-curate metastatic site from the open-access primary reports of the pooled series — the one $0 step that con |
| **[RT-RT-INTENSIFY](L2-rt-rt-intensify.md)**<br/>Radiotherapy intensification (particle therapy, brachytherapy, radiosensitisation, hyperthermia) | ✓ blocked | computed | `internal_note` | [PUB-LOCOREGIONAL](L3-publications.md) ◔ *contributing* | Search the particle registries by histology, which is $0 and is the only input to the reappraisal that does no |

## Family-level bets — blockers EVERY route here inherits

If one of these is never retired, the whole family is dead. That is a different risk from any
single route failing, and it is only visible at this level.

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)

## Best next action

Extract primary site, metastatic site and metastatic burden from the cohorts already curated in the clinical registry, and size the eligible fraction for each route here.

*Cost:* $0

[← L0](L0-ecosystem.md)
