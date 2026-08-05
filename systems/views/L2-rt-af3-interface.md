---
id: DOC-VIEW-RT-AF3-INTERFACE
title: RT-AF3-INTERFACE — AF3 on a druggable interface
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can a modern co-folding model predict a druggable interface on the fusion directly?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-AF3-INTERFACE — AF3 on a druggable interface

**Family:** [ST-PROXIMITY](L1-st-proximity.md) · **state:** ○ parked · concept · confidence low · verified 2026-08-05

**Grade** (owned by [`research/IDEAS.md`](../../research/IDEAS.md)): Deferred; method not strategy

## Scientific rationale

Rather than designing an induced complex, ask a structure predictor to find one. If a co-folder could propose a druggable interface on the fusion, it would replace several manual design steps at once.

## Remaining unknowns

- Whether any co-folder can assemble an induced complex from sequence and ligand alone — the one tested here failed badly.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A co-folder benchmarked on assembly rather than per-chain accuracy | V12 | **no** | BLK-TERNARY-GEOMETRY |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-TERNARY-GEOMETRY** | `requires_better_structure_prediction` | `TECH-COFOLD-ASSEMBLY`, `TECH-E3-RECRUITER-STRUCTURE`, `TECH-OBSERVED-CRL` |

## Readiness — what this could become today

**`internal_note`**

This is a method waiting on a method. There is nothing to report until a co-folder that assembles is available.

**Missing:**
- a co-folder validated on assembly

## Strategic timing — the wait equation

**Recommendation: `monitor`**

This is a method rather than a strategy, and it is registered so that a co-folder landing has somewhere to attach. Structure prediction is the fastest-moving dependency in the register, so the wait is likely short.

| horizon | effect |
|---|---|
| Six months | Plausibly material — this field iterates in months, not years. |
| Two years | Likely decisive one way or the other. |
| Cost trend | falling_fast |
| Automation outlook | Entirely automatable once the model exists. |

**Revisit when:**
- **TECH-COFOLD-ASSEMBLY** — A sequence-only co-folder evaluated on ternary ASSEMBLY — inter-chain accuracy on post-training-horizon induced complexes — rather *(expected 2027, basis `evidence_based`)*

## Closure

`instrument_limit` — A method, not a route — it is waiting on a co-folder that assembles ternaries.

## Best next action

Watch for an induced-complex benchmark reporting inter-chain accuracy on post-training-horizon structures. In-horizon results are memorisation-permitting and move nothing.

*Cost:* $0

[← ST-PROXIMITY](L1-st-proximity.md) · [← L0](L0-ecosystem.md)
