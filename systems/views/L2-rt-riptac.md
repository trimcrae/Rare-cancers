---
id: DOC-VIEW-RT-RIPTAC
title: RT-RIPTAC — RIPTAC — bind the tumour protein, poison an essential one
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can a bifunctional molecule bind NR4A3 and hold an essential protein hostage, killing only cells that express the fusion?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-RIPTAC — RIPTAC — bind the tumour protein, poison an essential one

**Family:** [ST-PROXIMITY](L1-st-proximity.md) · **state:** ○ parked · concept · confidence low · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md)): Tier 3 — needs paralogue selectivity AND a med-chem campaign; strictly worse than TCIP on both

## What has to land for this route to move

```mermaid
flowchart LR
  RT_RIPTAC["○ RT-RIPTAC"]:::fam
  BLK_INDUCED_COMPLEX{{"BLK-INDUCED-COMPLEX — An induced ternary/bivalent complex…"}}:::blk
  BLK_INDUCED_COMPLEX --> RT_RIPTAC
  TECH_COFOLD_ASSEMBLY(["TECH-COFOLD-ASSEMBLY<br/>expected 2027"]):::tech
  TECH_COFOLD_ASSEMBLY -.-> BLK_INDUCED_COMPLEX
  BLK_PARALOGUE_DDG{{"BLK-PARALOGUE-DDG — The paralogue ΔΔG margin — selectivit…"}}:::blk
  BLK_PARALOGUE_DDG --> RT_RIPTAC
  TECH_FE_CRYPTIC_POCKET(["TECH-FE-CRYPTIC-POCKET<br/>expected 2028"]):::tech
  TECH_FE_CRYPTIC_POCKET -.-> BLK_PARALOGUE_DDG
  BLK_R4_BINDS{{"BLK-R4-BINDS — R4 — nothing is known to bind the cryptic…"}}:::blk
  BLK_R4_BINDS --> RT_RIPTAC
  TECH_EMC_MODEL_ACCESS(["TECH-EMC-MODEL-ACCESS<br/>expected 2029"]):::tech
  TECH_EMC_MODEL_ACCESS -.-> BLK_R4_BINDS
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

## Scientific rationale

A RIPTAC does not degrade anything: it forms a complex that poisons an essential protein, so the cell dies only where the tumour protein is present. It converts a selectivity problem into a lethality problem, which is attractive because partial selectivity still gives a therapeutic effect.

## Remaining unknowns

- Whether the paralogue selectivity this needs is achievable — it needs the same margin the program cannot measure.
- Whether a medicinal-chemistry campaign is even conceivable for one person with no bench.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A measurable paralogue selectivity margin | ⛔ none built | **no** | BLK-PARALOGUE-DDG |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-PARALOGUE-DDG** | `requires_better_simulation_accuracy` | `TECH-FE-CRYPTIC-POCKET` |
| **BLK-INDUCED-COMPLEX** | `requires_better_structure_prediction` | `TECH-COFOLD-ASSEMBLY` |
| **BLK-R4-BINDS** | `requires_wet_lab` | `TECH-EMC-MODEL-ACCESS` |

## Readiness — what this could become today

**`internal_note`**

It needs both the selectivity the program cannot measure and a chemistry campaign it cannot run. It is strictly harder than the proximity routes above it on both axes.

**Missing:**
- paralogue selectivity
- a chemistry programme

## Where this route ends — the paper

**[PUB-PARKED-MODALITIES](L3-publications.md)** — *Five modalities parked on a capability that does not exist yet: what would have to land, and how it is being watched for* (unwritten)

`contributing` · ○ `unwritten` · aimed at `preprint`

**This route contributes:** The row that is dominated on both axes at once — it needs the selectivity the program cannot measure and a chemistry campaign it cannot run.

**The paper would claim:** For each parked modality there is a single named capability — a glue design method with a prospective track record, a co-folder benchmarked on assembly, a solid-tumour vector — whose arrival would make the route computable, and stating that capability with its scan trigger converts an indefinite park into a monitored condition.

**It is not written because:** Every route it would cover is parked on a technology nobody has, so the paper has no result to report and would be a horizon scan. It is worth writing only once at least one of the watched capabilities lands; until then the scan triggers carry the work.

## Strategic timing — the wait equation

**Recommendation: `monitor`**

Strictly dominated by the induced-proximity routes: it needs everything they need plus a medicinal-chemistry campaign. There is no state of the world where this is the right next thing while they are still blocked.

| horizon | effect |
|---|---|
| Six months | None. |
| Two years | Only via the same free-energy advance that unblocks the whole family. |
| Cost trend | flat |
| Automation outlook | The chemistry half is not automatable at this program's scale. |

**Revisit when:**
- **TECH-FE-CRYPTIC-POCKET** — A binding free-energy method — alchemical or ML — with a published known-answer validation on cryptic or induced-fit pockets, repr *(expected 2028, basis `extrapolated`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-PROXIMITY](L1-st-proximity.md), which is where these are asserted — a family limitation binds every route inside it.*

- No molecule in this family has been shown to bind NR4A3 at all — the pocket every route here depends on has no known ligand of any kind.
- No NR4A3 ternary complex has been correctly assembled by anyone, so every geometry claim in this family is a prediction from an instrument that has never been pointed at this system.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Closure

`instrument_limit` — It needs the paralogue selectivity the program cannot measure, plus a med-chem campaign.

## Best next action

Keep registered. Do not build while the routes it is dominated by are still blocked.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-NR4A3-LBD-MODELLED](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

[← ST-PROXIMITY](L1-st-proximity.md) · [← L0](L0-ecosystem.md)
