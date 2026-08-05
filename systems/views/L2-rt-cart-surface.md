---
id: DOC-VIEW-RT-CART-SURFACE
title: RT-CART-SURFACE — CAR-T for EMC (surface-directed)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is there a surface antigen on EMC that a CAR-T cell could target?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-CART-SURFACE — CAR-T for EMC (surface-directed)

**Family:** [ST-IMMUNO](L1-st-immuno.md) · **state:** ✓ blocked · computed · confidence low · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/car-t-strategies-emc.md`](../../research/manuscripts/car-t-strategies-emc.mdNone)): Hard but not closed — among surface modalities, ADC/FAPI-RLT likely beat CAR-T to a patient

## Scientific rationale

A surface target avoids the intracellular-antigen problem entirely and CAR-T is a mature modality. The whole route reduces to whether EMC presents a surface antigen that healthy tissue does not.

## Remaining unknowns

- Whether any sufficiently selective surface antigen exists on EMC.
- Whether the myxoid stroma admits T cells at all.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A selective surface antigen confirmed on EMC tissue | ⛔ none built | **no** | BLK-NO-EMC-DATA, BLK-ANTIGEN-COLD |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-ANTIGEN-COLD** | `fundamental_biological_limit` | *permanent* |
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |
| **BLK-NOT-FUSION-SELECTIVE** | `fundamental_biological_limit` | *permanent* |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Readiness — what this could become today

**`internal_note`**

Blocked by the antigen search and the cold stroma rather than by the cell product. Among surface modalities, conjugates and radioligands would likely reach a patient first.

**Missing:**
- a selective surface antigen

## Strategic timing — the wait equation

**Recommendation: `monitor`**

Two independent blockers, both about the tumour rather than the modality, and other surface modalities are ahead of it on the same antigen question.

| horizon | effect |
|---|---|
| Six months | None. |
| Two years | Only via an EMC dataset that surfaces a candidate antigen. |
| Cost trend | flat |
| Automation outlook | The antigen search is automatable and has been run; the data is what is missing. |

**Revisit when:**
- **TECH-EMC-EXPRESSION-DATA** — A fetchable public EMC RNA-seq or proteomics deposit beyond the single existing model, enabling a target-regulon readout and per-a *(expected 2029, basis `speculative`)*

## Closure

`instrument_limit` — Blocked by the antigen search and the cold myxoid stroma, not by the cell product.

## Best next action

Keep registered. The antigen search re-runs automatically when EMC expression data lands.

*Cost:* $0

[← ST-IMMUNO](L1-st-immuno.md) · [← L0](L0-ecosystem.md)
