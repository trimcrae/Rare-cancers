---
id: DOC-VIEW-ST-OCCUPANCY
title: ST-OCCUPANCY — Direct small-molecule engagement of the NR4A3 ligand-binding domain
level: L1
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can a molecule that merely OCCUPIES the NR4A3 pocket — reversibly or covalently — change the fusion's behaviour, without recruiting anything?
scope: Level 1. 4 routes.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# ST-OCCUPANCY — Direct small-molecule engagement of the NR4A3 ligand-binding domain

**Thesis.** If the ligand-binding domain is a functional handle in the chimera, then occupying it is enough, and the entire ternary-assembly problem disappears. The bet is on the pocket being actionable rather than merely bindable.

**Portfolio role:** `hedge` · **state:** ○ blocked · scoped · confidence low

> The hedge against the proximity family: it retires the ternary-geometry blocker outright. What it cannot retire is the requirement that something binds the pocket, and it adds one the proximity family does not have — that occupancy alone does something.

## What this family may NOT be used to claim

- Whether the ligand-binding domain is a functional handle in the fusion — whose other end is a strong independent activator — has never been tested by anyone.
- Nobody has stated how much paralogue selectivity this family would need, so 'the requirement is smaller here' is not a claim this repository can make.
- The covalent sub-form's negative result rests on an exposure criterion that fails its own positive control, so it is a rank and not a verdict.

## Is this family blocked as a unit, or route by route?

```mermaid
flowchart LR
  ST_OCCUPANCY["ST-OCCUPANCY"]:::fam
  RT_ASYMMETRIC["✓ RT-ASYMMETRIC"]:::fam
  ST_OCCUPANCY --> RT_ASYMMETRIC
  RT_COVALENT_PROBE["✓ RT-COVALENT-PROBE"]:::fam
  ST_OCCUPANCY --> RT_COVALENT_PROBE
  RT_MONOVALENT["○ RT-MONOVALENT"]:::fam
  ST_OCCUPANCY --> RT_MONOVALENT
  RT_NR2F1["○ RT-NR2F1"]:::fam
  ST_OCCUPANCY --> RT_NR2F1

  BLK_FUNCTIONAL_ACTIONABILITY{{"BLK-FUNCTIONAL-ACTIONABILITY — Is the LBD a FUNCTIONAL ha…"}}:::blk
  BLK_FUNCTIONAL_ACTIONABILITY --> RT_MONOVALENT
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_NR2F1
  BLK_NO_WET_LAB{{"BLK-NO-WET-LAB — No wet lab and no collaborator — an ask…"}}:::blk
  BLK_NO_WET_LAB --> RT_COVALENT_PROBE
  BLK_NOT_FUSION_SELECTIVE[["BLK-NOT-FUSION-SELECTIVE — The route also engages the wil…"]]:::perm
  BLK_NOT_FUSION_SELECTIVE --> RT_COVALENT_PROBE
  BLK_NOT_FUSION_SELECTIVE --> RT_MONOVALENT
  BLK_PARALOGUE_DDG{{"BLK-PARALOGUE-DDG — The paralogue ΔΔG margin — selectivit…"}}:::blk
  BLK_PARALOGUE_DDG --> RT_ASYMMETRIC
  BLK_PARALOGUE_DDG --> RT_COVALENT_PROBE
  BLK_PARALOGUE_DDG --> RT_MONOVALENT
  BLK_R4_BINDS{{"BLK-R4-BINDS — R4 — nothing is known to bind the cryptic…"}}:::blk
  BLK_R4_BINDS --> RT_COVALENT_PROBE
  BLK_R4_BINDS --> RT_MONOVALENT
  BLK_REACH_CATEGORICAL{{"BLK-REACH-CATEGORICAL — The categorical covalent window a…"}}:::blk
  BLK_REACH_CATEGORICAL --> RT_COVALENT_PROBE
  BLK_REACH_CATEGORICAL --> RT_MONOVALENT
  BLK_UNSIZED_REQUIREMENT{{"BLK-UNSIZED-REQUIREMENT — The selectivity requirement is…"}}:::blk
  BLK_UNSIZED_REQUIREMENT --> RT_ASYMMETRIC
  BLK_UNSIZED_REQUIREMENT --> RT_MONOVALENT
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** ⭐ **No blocker points at the family node**, and that is the finding: the routes here are *not* held down by one shared thing. They are blocked individually, for different reasons — so retiring any one blocker frees some routes and not others, and there is no single unlock for the family.

*What this family RETIRES for the portfolio is listed below rather than drawn — it is a property of the family, not an edge between these nodes.*

## Routes

| route | state | maturity | readiness today | ends in | next action |
|---|---|---|---|---|---|
| **[RT-ASYMMETRIC](L2-rt-asymmetric.md)**<br/>Asymmetric selectivity — NR4A1-sparing mandatory, NR4A2-sparing best-effort | ✓ ready | computed | `reproducible_workflow` | [PUB-DEGRADER](L3-publications.md) ◐ *contributing* | BUILD THE DETECTOR. The corpus-wide sweep was done by hand on 2026-08-07: 1,354 paralogue-pair mentions triage |
| **[RT-COVALENT-PROBE](L2-rt-covalent-probe.md)**<br/>Covalent probe at C397 — as a REAGENT, not a drug | ✓ blocked | computed | `internal_note` | [PUB-DEGRADER](L3-publications.md) ◐ *contributing* | DONE 2026-09-02 (S56) and it did not clear the axis. The criterion is built (`nr4a3_monovalent_reach.reactivit |
| **[RT-MONOVALENT](L2-rt-monovalent.md)**<br/>Monovalent LBD pocket modulation — a molecule that only OCCUPIES the NR4A3 LBD | ○ blocked | computed | `internal_note` | [PUB-MONOVALENT](L3-publications.md) ◐ *primary* | Trace whether the covalent sub-form's negative actually inherits the defective exposure criterion C7. ⚠ RE-TES |
| **[RT-NR2F1](L2-rt-nr2f1.md)**<br/>Orphan nuclear-receptor agonism against dormancy escape | ○ blocked | scoped | `internal_note` | [PUB-NR-OUTSIDE-NR4A3](L3-publications.md) ◔ *primary* | Check whether the fourth public cohort carries the receptor at all. |
## What this family buys the portfolio — blockers it RETIRES

- **BLK-FUNCTIONAL-ACTIONABILITY** (`requires_wet_lab`) — Is the LBD a FUNCTIONAL handle in the chimera, whose other end is a strong independent activator?
- **BLK-INDUCED-COMPLEX** (`requires_better_structure_prediction`) — An induced ternary/bivalent complex is still required (a second protein must be placed)
- **BLK-TERNARY-GEOMETRY** (`requires_better_structure_prediction`) — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Best next action

State the selectivity requirement this family would actually have to meet — it is currently unsized, and an unsized requirement cannot be shown to be met or missed.

*Cost:* $0

[← L0](L0-ecosystem.md)
