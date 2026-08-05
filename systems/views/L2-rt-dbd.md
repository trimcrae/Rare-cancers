---
id: DOC-VIEW-RT-DBD
title: RT-DBD — Target the DBD / DNA binding
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could the DNA-binding domain be targeted instead of the ligand-binding domain?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-DBD — Target the DBD / DNA binding

**Family:** [ST-FUSION-DIRECT](L1-st-fusion-direct.md) · **state:** ✕ closed · computed · confidence high · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/target-route-options.md`](../../research/manuscripts/target-route-options.md#route-12--target-the-dbd--dna-binding)): ✕ down, on arithmetic — 92.8 % / 98.6 % paralogue identity

## What has to land for this route to move

```mermaid
flowchart LR
  RT_DBD["✕ RT-DBD"]:::fam
  BLK_PARALOGUE_DDG{{"BLK-PARALOGUE-DDG — The paralogue ΔΔG margin — selectivit…"}}:::blk
  BLK_PARALOGUE_DDG --> RT_DBD
  TECH_FE_CRYPTIC_POCKET(["TECH-FE-CRYPTIC-POCKET<br/>expected 2028"]):::tech
  TECH_FE_CRYPTIC_POCKET -.-> BLK_PARALOGUE_DDG
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

## Scientific rationale

The zinc-finger DNA-binding domain is far more conserved between the paralogues than the ligand-binding domain the program already targets. Moving there makes the discrimination problem strictly harder, and that follows arithmetically from a measured sequence identity.

## Remaining unknowns

- Nothing is open. The closure is arithmetic over a measured paralogue sequence identity, and that identity does not change — so no capability reopens it.

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-PARALOGUE-DDG** | `requires_better_simulation_accuracy` | `TECH-FE-CRYPTIC-POCKET` |

## Readiness — what this could become today

**`internal_note`**

Closed by arithmetic over a fixed measured fact.

## Strategic timing — the wait equation

**Recommendation: `closed`**

Permanently closed. The closure is arithmetic over a sequence identity that does not change.

## Closure

`arithmetic_over_fixed_fact` — The zinc-finger DBD is far more conserved between the paralogues than the LBD the program already targets. An arithmetic consequence of a fixed sequence fact — never revivable.

## Best next action

Nothing. Cite the closure.

*Cost:* $0

[← ST-FUSION-DIRECT](L1-st-fusion-direct.md) · [← L0](L0-ecosystem.md)
