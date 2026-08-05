---
id: DOC-VIEW-RT-FET-LC-LIGAND
title: RT-FET-LC-LIGAND — A ligand for the shared FET low-complexity half
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could a ligand for the shared FET low-complexity region work?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-FET-LC-LIGAND — A ligand for the shared FET low-complexity half

**Family:** [ST-FUSION-DIRECT](L1-st-fusion-direct.md) · **state:** ✕ closed · scoped · confidence high · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md#route-15---a-ligand-for-the-shared-fet-low-complexity-half)): Tier 3 — relocates selectivity somewhere worse

## Scientific rationale

Registered for the same reason as the row above. A ligand for the SHARED low-complexity half binds wild-type EWSR1 by the definition of 'shared'. It relocates the selectivity problem onto a protein that is more essential, not less.

## Remaining unknowns

- Nothing is open. A ligand for a SHARED region cannot discriminate between the things that share it; that is what 'shared' means, so no capability reopens it.

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NOT-FUSION-SELECTIVE** | `fundamental_biological_limit` | *permanent* |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)

## Readiness — what this could become today

**`internal_note`**

Closed on the same definitional grounds as the EWSR1 protein route.

## Strategic timing — the wait equation

**Recommendation: `closed`**

Permanently closed. A shared region cannot discriminate between the things that share it — that is what 'shared' means.

## Closure

`definitional` — A ligand for the SHARED FET low-complexity half binds wild-type EWSR1 by definition of 'shared'. Permanent for the same reason as the row above, reached from the other direction.

## Best next action

Nothing. Cite the closure.

*Cost:* $0

[← ST-FUSION-DIRECT](L1-st-fusion-direct.md) · [← L0](L0-ecosystem.md)
