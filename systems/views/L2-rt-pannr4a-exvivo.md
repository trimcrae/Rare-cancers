---
id: DOC-VIEW-RT-PANNR4A-EXVIVO
title: RT-PANNR4A-EXVIVO — Ex-vivo pan-NR4A pole (CAR-T manufacturing additive)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could pan-NR4A engagement be useful EX VIVO — during T-cell manufacturing — where selectivity does not matter?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-PANNR4A-EXVIVO — Ex-vivo pan-NR4A pole (CAR-T manufacturing additive)

**Family:** [ST-IMMUNO](L1-st-immuno.md) · **state:** ✓ ready · computed · confidence moderate · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/target-route-options.md`](../../research/manuscripts/target-route-options.md#route-4--the-ex-vivo-pan-nr4a-pole-car-t-manufacturing-additive)): ★ already in the paper as pole 2; under-used as an ARGUMENT

## What has to land for this route to move

```mermaid
flowchart LR
  RT_PANNR4A_EXVIVO["✓ RT-PANNR4A-EXVIVO"]:::fam
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

✓ Already cleared by this route: `BLK-NOT-FUSION-SELECTIVE`, `BLK-PARALOGUE-DDG`.

## Scientific rationale

NR4A factors drive T-cell exhaustion, and a manufacturing additive acts on cells outside the patient for a bounded time. That changes the exposure regime entirely: pan-family engagement becomes acceptable, so the paralogue selectivity requirement — the blocker that dominates the whole portfolio — simply does not apply.

## Remaining unknowns

- Whether pan-NR4A engagement improves T-cell persistence in a manufacturing context, which is a cell-biology question nobody here can run.
- Whether the same chemistry serves both poles or they diverge.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| An ex-vivo T-cell persistence readout | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-NOT-FUSION-SELECTIVE** — The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-CART-SURFACE](L2-rt-cart-surface.md) | where the NR4A molecule acts | `BLK-NO-EMC-DATA` | it is not an EMC treatment route at all in the direct sense — it removes the selectivity requirement by changing the exposure regime, not by being cleverer about the pocket |

## Readiness — what this could become today

**`preprint`**

It is already a pole of the lead manuscript. Its constraint is that no cellular validation exists, so it is a design argument rather than a result.

**Missing:**
- a cellular persistence readout

## Where this route ends — the paper

**[PUB-DEGRADER](L3-publications.md)** — [In silico design of a paralogue-favoured ligand for a cryptic NR4A3 pocket](../../research/manuscripts/nr4a3-degrader-paper.md)

`contributing` · ◐ `drafted` · aimed at `journal_submission`

**This route contributes:** The ex-vivo pole — the argument that this family's chemistry has a use that does not depend on solving paralogue selectivity. Without it the paper carries only the blocked application.

**The paper would claim:** A cryptic pocket on the NR4A3 ligand-binding domain can be found and a paralogue-favoured ligand designed into it by computation alone — and the selectivity margin that design would need is larger than the instruments used to predict it can currently resolve, which is reported as the result rather than worked around.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

It is free, already written, and it is the argument that makes the family's chemistry valuable even if paralogue selectivity is never achieved. It is under-used as an argument rather than under-developed as work.

| horizon | effect |
|---|---|
| Six months | None. |
| Two years | A cloud lab with T-cell assay scope would make this directly testable. |
| Cost trend | flat |
| Automation outlook | The design half is done; the assay is not computational. |

**Revisit when:**
- **TECH-CLOUD-WET-LAB** — A remote robotic or cloud wet lab, rentable per experiment by an unaffiliated researcher, at a price and assay scope that covers E *(expected 2029, basis `extrapolated`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-IMMUNO](L1-st-immuno.md), which is where these are asserted — a family limitation binds every route inside it.*

- EMC is antigen-cold and the fusion junction is a weak peptide-HLA — a property of this tumour and this junction, not of any modality here.
- Surface-antigen selectivity was measured on cell-line surrogates rather than on EMC tissue, so the negatives are as provisional as the positives would have been.
- One route's predicted binders span junction seams that a corrected exon index says do not exist; that result is void and the question is open.

## Best next action

Use it more prominently as the argument that the family's chemistry has a use that does not depend on solving paralogue selectivity.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-NR4A1-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-NR4A2-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-NR4A3-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

[← ST-IMMUNO](L1-st-immuno.md) · [← L0](L0-ecosystem.md)
