---
id: DOC-VIEW-RT-CARFILZOMIB
title: RT-CARFILZOMIB — Carfilzomib ± anthracycline (± venetoclax)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Does the best ex-vivo EMC drug-sensitivity evidence point at a proteasome inhibitor combination?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-CARFILZOMIB — Carfilzomib ± anthracycline (± venetoclax)

**Family:** [ST-REPURPOSING](L1-st-repurposing.md) · **state:** ○ ready · concept · confidence moderate · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/repurposing-hypotheses.md`](../../research/manuscripts/repurposing-hypotheses.md)): NEAR-TERM LEAD — best ex-vivo EMC evidence

## Scientific rationale

This carries the best ex-vivo EMC drug-sensitivity evidence in the repository — an actual measurement on actual EMC material, which is rarer than anything else in this family. An approved agent with an ex-vivo signal is a strong near-term lead by the standards available for this disease.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `EV-EMC-EXVIVO` | ex-vivo drug sensitivity measured on EMC material | `direct` |

## Remaining unknowns

- Whether ex-vivo sensitivity transfers to clinical benefit, which it frequently does not.
- The provenance of the underlying evidence needs firming — it is the repository's only ex-vivo EMC result and its citation has been flagged as incomplete.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Confirmation of the ex-vivo result and a firm primary citation | ⛔ none built | yes | — |
| A clinical series | ⛔ none built | **no** | BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Readiness — what this could become today

**`internal_note`**

Its single supporting result currently lacks a resolvable primary identifier, and an uncitable result cannot carry a published claim however good it looks.

**Missing:**
- a resolvable primary citation for the ex-vivo evidence

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The blocking item is a citation lookup, not a capability — and it gates the only ex-vivo EMC evidence the repository holds. Leaving the program's best measured EMC result uncitable is a defect worth fixing before anything else in this family.

| horizon | effect |
|---|---|
| Six months | None. |
| Two years | None on the citation; a clinical series would change the route. |
| Cost trend | flat |
| Automation outlook | The literature lookup is automatable and is already wired. |

## Best next action

Resolve the primary citation for the ex-vivo EMC drug-sensitivity evidence. It is the only ex-vivo EMC result here and it currently carries no resolvable identifier.

*Cost:* $0

[← ST-REPURPOSING](L1-st-repurposing.md) · [← L0](L0-ecosystem.md)
