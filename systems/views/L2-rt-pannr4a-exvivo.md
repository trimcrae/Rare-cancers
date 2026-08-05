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

## Readiness — what this could become today

**`preprint`**

It is already a pole of the lead manuscript. Its constraint is that no cellular validation exists, so it is a design argument rather than a result.

**Missing:**
- a cellular persistence readout

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

## Best next action

Use it more prominently as the argument that the family's chemistry has a use that does not depend on solving paralogue selectivity.

*Cost:* $0

[← ST-IMMUNO](L1-st-immuno.md) · [← L0](L0-ecosystem.md)
