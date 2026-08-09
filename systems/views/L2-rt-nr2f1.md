---
id: DOC-VIEW-RT-NR2F1
title: RT-NR2F1 — Orphan nuclear-receptor agonism against dormancy escape
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can a nuclear receptor other than the driver's be engaged to hold disseminated cells dormant?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-NR2F1 — Orphan nuclear-receptor agonism against dormancy escape

**Family:** [ST-OCCUPANCY](L1-st-occupancy.md) · **state:** ○ blocked · concept · confidence low · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/cancer-modality-census.md`](../../research/manuscripts/cancer-modality-census.md#37--nuclear-receptors-outside-nr4a3)): ⭑ Registered 2026-08-09 from the modality census, porting a 2026-08-07 lane; its value to the program is partly that it supplies a positive control the NR4A3 work lacks.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_NR2F1["○ RT-NR2F1"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_NR2F1
  TECH_EMC_EXPRESSION_DATA(["TECH-EMC-EXPRESSION-DATA<br/>expected 2029"]):::tech
  TECH_EMC_EXPRESSION_DATA -.-> BLK_NO_EMC_DATA
  TECH_VIRTUAL_CELL(["TECH-VIRTUAL-CELL<br/>expected 2028"]):::tech
  TECH_VIRTUAL_CELL -.-> BLK_NO_EMC_DATA
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

## Scientific rationale

A registered lane with no route. It targets this disease's actual clinical problem rather than its driver, and it repoints the orphan-nuclear-receptor modelling stack built for NR4A3 onto a receptor that has a published tool compound — which is the known-answer control the program's own receptor never had, and is worth as much methodologically as the biology is clinically.

## Remaining unknowns

- Whether the receptor is expressed in this disease at all, which is unmeasured.
- Whether a dormancy-maintenance strategy has any measurable endpoint in a disease whose response endpoint is itself contested here.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A read of the receptor in the targeted expression panel already committed here | ⛔ none built | yes | — |
| A demonstration that the existing pocket-modelling pipeline runs on its ligand-binding domain | ⛔ none built | yes | — |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`internal_note`**

Nothing has been run. This route was registered on 2026-08-09 from the modality census and is at concept maturity, so the only honest output today is the question and its cheapest next observation.

**Missing:**
- a read of the receptor in the expression panel already committed here

## Where this route ends — the paper

**[PUB-NR-OUTSIDE-NR4A3](L3-publications.md)** — *Nuclear-receptor pharmacology outside NR4A3 in a NR4A3-driven sarcoma* (unwritten)

`primary` · ○ `unwritten` · aimed at `preprint`

**This route contributes:** The half of the paper that targets the disease's clinical problem — late metastasis — through a receptor that has the tool compound this program's own receptor never had.

**The paper would claim:** Two nuclear-receptor routes exist in this disease that do not act on its own receptor — one where a 5′ fusion partner imports a druggable transcriptional input, and one targeting dormancy through a receptor that has the published tool compound this program's own receptor never had.

**It is not written because:** Both routes it would cover were surfaced as lanes on 2026-08-07 and neither has had its expression lookup run.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The next step costs nothing and needs nobody's cooperation, so there is no reason to defer it; what it returns decides whether this route is worth more than a row.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-OCCUPANCY](L1-st-occupancy.md), which is where these are asserted — a family limitation binds every route inside it.*

- Whether the ligand-binding domain is a functional handle in the fusion — whose other end is a strong independent activator — has never been tested by anyone.
- Nobody has stated how much paralogue selectivity this family would need, so 'the requirement is smaller here' is not a claim this repository can make.
- The covalent sub-form's negative result rests on an exposure criterion that fails its own positive control, so it is a rank and not a verdict.

## Best next action

Read the receptor in the targeted expression panel already committed here, then state whether the existing pocket-modelling pipeline runs unmodified on its ligand-binding domain.

*Cost:* $0

[← ST-OCCUPANCY](L1-st-occupancy.md) · [← L0](L0-ecosystem.md)
