---
id: DOC-VIEW-RT-COVALENT-PROBE
title: RT-COVALENT-PROBE — Covalent probe at C397 — as a REAGENT, not a drug
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can a covalent probe at an NR4A3-unique cysteine serve as a REAGENT — a tool to test the biology, not a drug?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-COVALENT-PROBE — Covalent probe at C397 — as a REAGENT, not a drug

**Family:** [ST-OCCUPANCY](L1-st-occupancy.md) · **state:** ✓ blocked · computed · confidence low · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md#route-5--the-covalent-probe-at-c397-proposed-as-a-reagent---the-largest-single-demotion)): Tier 3 — the largest single demotion; D ≈ 0 and P is negative rather than merely absent

## Scientific rationale

A cysteine present in NR4A3 and absent from both paralogues would give categorical rather than thermodynamic discrimination: the bond either forms or it does not. As a chemical probe rather than a therapeutic, it would let someone test whether engaging this domain does anything at all — which is the question the whole occupancy family rests on.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `V17` | a threshold-free RANK of cysteine accessibility across the family — and nothing stronger, because the criterion fails its own positive control | `direct` |

## Remaining unknowns

- Whether the target cysteine is actually engageable: the exposure criterion that says it is fails on the one family member with literature support.
- Whether the reach geometry survives a criterion that passes its control — the current negative may be an artifact of the failing one.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| An exposure or reactivity criterion that recovers the known covalent site | V17 | **no** | BLK-REACH-CATEGORICAL |
| Chemical synthesis and a binding assay | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-WET-LAB** | `requires_external_collaboration` | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-R4-BINDS** | `requires_wet_lab` | `TECH-EMC-MODEL-ACCESS` |
| **BLK-REACH-CATEGORICAL** | `scientific_uncertainty` | `TECH-EXPOSURE-CRITERION` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer
- **BLK-FUNCTIONAL-ACTIONABILITY** — Is the LBD a FUNCTIONAL handle in the chimera, whose other end is a strong independent activator?

## Readiness — what this could become today

**`internal_note`**

Its in-silico half is not publishable BECAUSE its exposure instrument fails its own positive control. That is a statement about the instrument, not about the cysteine.

**Missing:**
- a criterion that passes its positive control

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The blocking criterion is small enough to BUILD rather than wait for — a reactivity-weighted accessibility criterion calibrated against the existing positive control is bounded work. Waiting for the field to publish one defers a repair this program could make itself.

| horizon | effect |
|---|---|
| Six months | None if we wait; potentially decisive if we build. |
| Two years | Chemoproteomics datasets keep growing, so a calibrated criterion becomes easier over time either way. |
| Cost trend | flat |
| Automation outlook | Fully automatable — it is a $0 recalculation once the criterion is defined. |

**Revisit when:**
- **TECH-EXPOSURE-CRITERION** — A solvent-exposure or thiol-reactivity criterion that recovers the one NR4A-family covalent site with literature support as engage *(expected 2027H2, basis `extrapolated`)*

## Closure

`instrument_limit` — Its in-silico half is not publishable BECAUSE its exposure instrument fails its own positive control — an instrument limit, not a statement about C397.

## Best next action

Build a reactivity-weighted accessibility criterion and calibrate it against the known covalent site, then re-run the reach enumeration under it. Report the result as a rank until the criterion passes.

*Cost:* $0

[← ST-OCCUPANCY](L1-st-occupancy.md) · [← L0](L0-ecosystem.md)
