---
id: DOC-VIEW-RT-SYNPROMOTER
title: RT-SYNPROMOTER — Fusion-driven synthetic promoter → suicide gene
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could a synthetic promoter driven by the fusion switch on a suicide gene only in tumour cells?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-SYNPROMOTER — Fusion-driven synthetic promoter → suicide gene

**Family:** [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) · **state:** ○ closed · scoped · confidence moderate · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md#route-14---the-fusion-driven-synthetic-promoter-and-the-precise-reason-emc-is-a-harder-case-than-ewing)): Tier 3 — vector delivery, AND EMC lacks the neomorphic DNA-binding element the technique depends on

## What has to land for this route to move

```mermaid
flowchart LR
  RT_SYNPROMOTER["○ RT-SYNPROMOTER"]:::fam
  BLK_VECTOR_DELIVERY{{"BLK-VECTOR-DELIVERY — Vector delivery gene-therapy payloa…"}}:::blk
  BLK_VECTOR_DELIVERY --> RT_SYNPROMOTER
  TECH_VECTOR_DELIVERY(["TECH-VECTOR-DELIVERY<br/>expected 2030"]):::tech
  TECH_VECTOR_DELIVERY -.-> BLK_VECTOR_DELIVERY
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

✓ Already cleared by this route: `BLK-PARALOGUE-DDG`, `BLK-TERNARY-GEOMETRY`.

## Scientific rationale

Registered with its refutation attached. The technique depends on the fusion creating a neomorphic DNA-binding element that a synthetic promoter can be built against — and this fusion does not appear to create one, which is a measured statement about this disease rather than about the technique.

## Remaining unknowns

- Whether the absence of a neomorphic binding element is firmly established, or merely unmeasured in EMC — this is what distinguishes a closed route from a data-blocked one.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A direct read of the fusion's DNA-binding specificity in EMC | ⛔ none built | **no** | BLK-NO-EMC-DATA, BLK-VECTOR-DELIVERY |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-VECTOR-DELIVERY** | `requires_future_technology` | `TECH-VECTOR-DELIVERY` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Readiness — what this could become today

**`internal_note`**

Closed on a premise about this fusion's biology; the useful output is the reasoning, not a result.

**Missing:**
- a direct binding-specificity read in EMC

## Strategic timing — the wait equation

**Recommendation: `monitor`**

Closed on a premise rather than definitionally, so an EMC dataset that measured the fusion's binding specificity could in principle reopen it — which is exactly why it is `premise_false` and not `definitional`.

| horizon | effect |
|---|---|
| Six months | None. |
| Two years | Only via an EMC dataset. |
| Cost trend | flat |
| Automation outlook | Not applicable. |

**Revisit when:**
- **TECH-EMC-EXPRESSION-DATA** — A fetchable public EMC RNA-seq or proteomics deposit beyond the single existing model, enabling a target-regulon readout and per-a *(expected 2029, basis `speculative`)*

## Closure

`premise_false` — ⭐ EMC lacks the neomorphic DNA-binding element the technique depends on — a measured premise about EMC's fusion, and the reason it fails is itself a computed EMC result worth publishing.

## Best next action

Keep registered with the premise stated. If an EMC dataset lands, re-read the binding specificity before re-closing.

*Cost:* $0

[← ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) · [← L0](L0-ecosystem.md)
