---
id: DOC-VIEW-RT-JUNCTION-NEOANTIGEN
title: RT-JUNCTION-NEOANTIGEN — Fusion-junction neoantigen (the antigen, shared by three delivery routes)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Does the fusion junction produce a peptide the immune system could see — and is it presented?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-JUNCTION-NEOANTIGEN — Fusion-junction neoantigen (the antigen, shared by three delivery routes)

**Family:** [ST-IMMUNO](L1-st-immuno.md) · **state:** ✓ blocked · computed · confidence low · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/target-route-options.md`](../../research/manuscripts/target-route-options.md#route-7--junction-neoantigen-vaccine--tcr-t--soluble-tcr)): ○ drafted — and now carrying a correction owed

## Scientific rationale

The junction is tumour-exclusive at the sequence level, so a peptide spanning it is a true neoantigen shared by every patient with this fusion. That would make one reagent serve the whole disease, which is the only economically plausible shape for an ultra-rare cancer.

## Remaining unknowns

- The predicted binders are VOID: they span seams that a corrected exon index says no reported junction produces. The result is unusable; the question is open.
- Whether a junction peptide is presented at all, and at what level — EMC is antigen-cold.
- Whether the peptide-HLA is strong enough to be a target rather than merely present.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Regeneration of the predictions against the corrected exon index | ⛔ none built | yes | — |
| Measured presentation on EMC tissue | ⛔ none built | **no** | BLK-ANTIGEN-COLD, BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-ANTIGEN-COLD** | `fundamental_biological_limit` | *permanent* |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer
- **BLK-NOT-FUSION-SELECTIVE** — The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)

## Readiness — what this could become today

**`internal_note`**

The current predictions cannot be published because they span junctions that do not exist. That is a defect of the input index, not of the method — which is why the fix is free and is the route's next action.

**Missing:**
- regenerated predictions against the corrected exon index

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The blocking defect is an input error this program made and can fix for nothing. Waiting on any external capability while a free self-inflicted defect stands unrepaired is the wrong order.

| horizon | effect |
|---|---|
| Six months | None — the fix is available now. |
| Two years | Presentation prediction is improving, but the void result must be repaired first regardless. |
| Cost trend | flat |
| Automation outlook | Fully automatable; it is a regeneration. |

## Closure

`unregenerable_artifact` — ⚠ THE TWO HALVES, KEPT APART: the 26 predicted binders are unusable because they span seams that do not exist — that RESULT is void. The QUESTION is open and one free regeneration answers it.

## Best next action

Regenerate the junction-neoantigen predictions against the corrected exon index, then re-grade. Every predicted binder currently spans a seam no reported junction produces.

*Cost:* $0

[← ST-IMMUNO](L1-st-immuno.md) · [← L0](L0-ecosystem.md)
