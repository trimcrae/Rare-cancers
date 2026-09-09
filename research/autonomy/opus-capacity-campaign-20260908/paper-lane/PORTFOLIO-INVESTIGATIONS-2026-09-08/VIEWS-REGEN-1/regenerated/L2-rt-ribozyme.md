---
id: DOC-VIEW-RT-RIBOZYME
title: RT-RIBOZYME — Trans-splicing ribozyme → suicide gene, triggered by the fusion transcript
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could a trans-splicing ribozyme convert the fusion transcript into a suicide gene?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-RIBOZYME — Trans-splicing ribozyme → suicide gene, triggered by the fusion transcript

**Family:** [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) · **state:** ○ parked · concept · confidence low · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/program/emc-post-degrader-options.md`](../../research/manuscripts/program/emc-post-degrader-options.md)): Tier 3 — vector delivery; a 2000s-era technique with no modern solid-tumour clinical footing

## What has to land for this route to move

```mermaid
flowchart LR
  RT_RIBOZYME["○ RT-RIBOZYME"]:::fam
  BLK_VECTOR_DELIVERY{{"BLK-VECTOR-DELIVERY — Vector delivery gene-therapy payloa…"}}:::blk
  BLK_VECTOR_DELIVERY --> RT_RIBOZYME
  TECH_VECTOR_DELIVERY(["TECH-VECTOR-DELIVERY<br/>expected 2030"]):::tech
  TECH_VECTOR_DELIVERY -.-> BLK_VECTOR_DELIVERY
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

✓ Already cleared by this route: `BLK-NOT-FUSION-SELECTIVE`, `BLK-PARALOGUE-DDG`, `BLK-TERNARY-GEOMETRY`.

## Scientific rationale

A trans-splicing ribozyme would sense the fusion transcript by base-pairing across the breakpoint junction — a sequence present in no healthy cell — and convert that sensing into expression of a suicide gene. ⚠ The coupling is to the junction SEQUENCE, not to tumour identity: the vector delivers indiscriminately, so any cell it reaches in which the ribozyme trans-splices off-target is killed by the same mechanism, and no trans-splicing specificity has been computed anywhere in this repo. No efficacy, safety or therapeutic window is asserted.

## Remaining unknowns

- Vector delivery, as above.
- Whether the technique has any modern solid-tumour footing at all — it is largely a 2000s-era approach.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Vector delivery, and a modern demonstration of the technique | ⛔ none built | **no** | BLK-VECTOR-DELIVERY |
| Trans-splicing specificity: that the ribozyme's binding arm engages the breakpoint junction and not other transcripts | ⛔ none built | **no** | BLK-VECTOR-DELIVERY |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-VECTOR-DELIVERY** | `requires_future_technology` | `TECH-VECTOR-DELIVERY` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer
- **BLK-NOT-FUSION-SELECTIVE** — The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-SYNPROMOTER](L2-rt-synpromoter.md) | what the fusion is sensed BY | `BLK-NOT-FUSION-SELECTIVE` | the ribozyme senses the fusion TRANSCRIPT by base-pairing; the synthetic promoter senses the fusion PROTEIN by DNA binding — and the second fails for an EMC-specific reason the first does not (EMC lacks a neomorphic DNA-binding element) |

## Readiness — what this could become today

**`internal_note`**

Two independent gates — delivery and a technique with no modern clinical footing — and no computation addresses either.

**Missing:**
- a solid-tumour vector
- a modern demonstration of trans-splicing ribozymes

## Where this route ends — the paper

**[PUB-PARKED-MODALITIES](L3-publications.md)** — *Five modalities parked on a capability that does not exist yet: what would have to land, and how it is being watched for* (unwritten)

`contributing` · ○ `unwritten` · aimed at `preprint`

**This route contributes:** The one row gated twice over — delivery, and a technique with no modern clinical footing — and the reason two gates is a different situation from one.

**The paper would claim:** For each parked modality there is a single named capability — a glue design method with a prospective track record, a co-folder benchmarked on assembly, a solid-tumour vector — whose arrival would make the route computable, and stating that capability with its scan trigger converts an indefinite park into a monitored condition.

**It is not written because:** Every route it would cover is parked on a technology nobody has, so the paper has no result to report and would be a horizon scan. It is worth writing only once at least one of the watched capabilities lands; until then the scan triggers carry the work.

## Strategic timing — the wait equation

**Recommendation: `monitor`**

The weaker of the two suicide-gene routes: it carries the same delivery gate plus a technique the field has largely moved on from.

| horizon | effect |
|---|---|
| Six months | None. |
| Two years | Unlikely to change. |
| Cost trend | flat |
| Automation outlook | Not automatable — the gap is delivery and a technique base. |

**Revisit when:**
- **TECH-VECTOR-DELIVERY** — A gene-therapy vector that reaches a solid tumour at therapeutic coverage *(expected 2030, basis `speculative`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md), which is where these are asserted — a family limitation binds every route inside it.*

- Delivery of an oligonucleotide to a non-hepatic solid tumour has no validated solution, and this is not solvable in silico today.
- Predicted specificity rests in part on a conservative heuristic rather than a calibrated cleavage-activity model.
- The vector-delivered sub-routes carry a second, distinct delivery problem that must not be conflated with the oligonucleotide one.

## Closure

`instrument_limit` — Vector delivery, and a technique with no modern solid-tumour clinical footing.

## Best next action

Keep registered at low priority.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-FUS-T1](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

[← ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) · [← L0](L0-ecosystem.md)
