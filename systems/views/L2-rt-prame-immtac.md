---
id: DOC-VIEW-RT-PRAME-IMMTAC
title: RT-PRAME-IMMTAC — PRAME-directed brenetafusp (ImmTAC) / PRAME CAR-TCR
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is a PRAME-directed T-cell engager or receptor therapy applicable to EMC?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-PRAME-IMMTAC — PRAME-directed brenetafusp (ImmTAC) / PRAME CAR-TCR

**Family:** [ST-IMMUNO](L1-st-immuno.md) · **state:** ○ blocked · computed · confidence moderate · verified 2026-08-05

**Grade** (owned by [`research/IDEAS.md`](../../research/IDEAS.md)): NEW antigen-directed lead — best of the CTAs

## What has to land for this route to move

```mermaid
flowchart LR
  RT_PRAME_IMMTAC["○ RT-PRAME-IMMTAC"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_PRAME_IMMTAC
  TECH_EMC_EXPRESSION_DATA(["TECH-EMC-EXPRESSION-DATA<br/>expected 2029"]):::tech
  TECH_EMC_EXPRESSION_DATA -.-> BLK_NO_EMC_DATA
  TECH_VIRTUAL_CELL(["TECH-VIRTUAL-CELL<br/>expected 2028"]):::tech
  TECH_VIRTUAL_CELL -.-> BLK_NO_EMC_DATA
  BLK_NOT_FUSION_SELECTIVE[["BLK-NOT-FUSION-SELECTIVE — The route also engages the wil…"]]:::perm
  BLK_NOT_FUSION_SELECTIVE --> RT_PRAME_IMMTAC
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

⛔ **1 of these is permanent** (`BLK-NOT-FUSION-SELECTIVE`) — a fact about the biology, drawn double-walled, with no way out by definition. No technology arrives to fix it.

✓ Already cleared by this route: `BLK-PARALOGUE-DDG`, `BLK-TERNARY-GEOMETRY`.

## Scientific rationale

Unlike the junction neoantigen, this uses an antigen with an existing clinical-stage agent — so the reagent problem is already solved by someone else, and the only question is whether EMC expresses the antigen. That makes it the cheapest antigen-directed route to test.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-SURFACE-EXPRESSION` | surrogate expression came back favourable, unlike every other cancer-testis antigen examined | `surrogate` |

## Remaining unknowns

- Whether the surrogate expression holds on real EMC tissue — the measurement was on cell-line surrogates.
- HLA restriction limits which patients are eligible.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Expression confirmation on EMC tissue | ⛔ none built | **no** | BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |
| **BLK-NOT-FUSION-SELECTIVE** | `fundamental_biological_limit` | *permanent* |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Readiness — what this could become today

**`experimental_proposal`**

The reagent exists clinically and the computational case is made, so what remains is a confirmation, not a discovery. That makes it a proposal rather than a paper.

**Missing:**
- expression confirmation on EMC tissue

**Experiment required:**
- immunohistochemistry or expression readout on EMC tissue

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The best-supported antigen-directed row on the board and the one where someone else has already solved the hard part. The confirm is small and the agent already exists, so the value of asking now is high.

| horizon | effect |
|---|---|
| Six months | None on our side. |
| Two years | An EMC expression dataset would settle it without anyone running anything. |
| Cost trend | flat |
| Automation outlook | The confirm is a bench readout, not computation. |

**Revisit when:**
- **TECH-EMC-EXPRESSION-DATA** — A fetchable public EMC RNA-seq or proteomics deposit beyond the single existing model, enabling a target-regulon readout and per-a *(expected 2029, basis `speculative`)*

## Best next action

Include in the collaborator ask: an expression confirm on EMC tissue is small, and the therapeutic already exists.

*Cost:* $0

[← ST-IMMUNO](L1-st-immuno.md) · [← L0](L0-ecosystem.md)
