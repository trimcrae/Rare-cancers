---
id: DOC-VIEW-RT-TCRT-CTA
title: RT-TCRT-CTA — TCR-T / engineered T cells vs a cancer-testis antigen (synovial-sarcoma port)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could engineered T cells against a cancer-testis antigen be ported to EMC, as was done in synovial sarcoma?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-TCRT-CTA — TCR-T / engineered T cells vs a cancer-testis antigen (synovial-sarcoma port)

**Family:** [ST-IMMUNO](L1-st-immuno.md) · **state:** ✓ parked · computed · confidence moderate · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/immunotherapy-options-emc.md`](../../research/manuscripts/immunotherapy-options-emc.md)): DOWNGRADED to weak — gating fact resolved, mostly negative

## What has to land for this route to move

```mermaid
flowchart LR
  RT_TCRT_CTA["✓ RT-TCRT-CTA"]:::fam
  BLK_ANTIGEN_COLD[["BLK-ANTIGEN-COLD — EMC is antigen-cold, and the fusion ju…"]]:::perm
  BLK_ANTIGEN_COLD --> RT_TCRT_CTA
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_TCRT_CTA
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

⛔ **1 of these is permanent** (`BLK-ANTIGEN-COLD`) — a fact about the biology, drawn double-walled, with no way out by definition. No technology arrives to fix it.

✓ Already cleared by this route: `BLK-PARALOGUE-DDG`, `BLK-TERNARY-GEOMETRY`.

## Scientific rationale

The synovial-sarcoma precedent shows the approach works in a translocation sarcoma, and porting an approved approach is far cheaper than inventing one.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-SURFACE-EXPRESSION` | EMC is cancer-testis-antigen-low on the available measured data | `surrogate` |

## Remaining unknowns

- Whether a real EMC series would agree with the surrogate measurement that downgraded this.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A real EMC expression series | ⛔ none built | **no** | BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-ANTIGEN-COLD** | `fundamental_biological_limit` | *permanent* |
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Readiness — what this could become today

**`internal_note`**

Downgraded on a measurement rather than on reasoning, which is the useful kind of downgrade — but it means the route needs a better measurement, not a better argument.

**Missing:**
- a real EMC expression series

## Strategic timing — the wait equation

**Recommendation: `monitor`**

The gating fact was resolved and came back mostly negative. Only better data reopens it, and that data is watched.

| horizon | effect |
|---|---|
| Six months | None. |
| Two years | Only via an EMC dataset. |
| Cost trend | flat |
| Automation outlook | Re-grading would be automatic once data lands. |

**Revisit when:**
- **TECH-EMC-EXPRESSION-DATA** — A fetchable public EMC RNA-seq or proteomics deposit beyond the single existing model, enabling a target-regulon readout and per-a *(expected 2029, basis `speculative`)*

## Closure

`premise_false` — EMC is CTA-low on measured data; a real EMC series is what could change it.

## Best next action

Keep registered for automatic re-grade when EMC expression data lands.

*Cost:* $0

[← ST-IMMUNO](L1-st-immuno.md) · [← L0](L0-ecosystem.md)
