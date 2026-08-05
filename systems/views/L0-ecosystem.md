---
id: DOC-VIEW-L0
title: L0 — the EMC research ecosystem
level: L0
kind: generated
status: generated
generator: systems/systems_check.py
purpose: "The complete landscape in one screen: every strategy family, its state, and what holds it down."
scope: Level 0. Detail appears on drill-down, never here.
audience: ["maintainers", "autonomous research agents", "external reviewers"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# L0 — the EMC research ecosystem

> Extraskeletal myxoid chondrosarcoma, driven by the EWSR1::NR4A3 fusion. One researcher, no wet
> lab, no funding for one — so every advance is either in-silico or publish-to-convince.
> **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness.**

**9 strategy families · 40 routes · 17 blockers · 25 technology dependencies.**

## The landscape

| family | thesis | routes | state | role |
|---|---|---:|---|---|
| **[ST-PROXIMITY](L1-st-proximity.md)**<br/>Induced-proximity therapeutics | The NR4A3 ligand-binding domain does not need to be inhibited, only ENGAGED, because the therapeutic effect comes from what the molecule recruits rath… | 7 | ◐ blocked · computed | lead |
| **[ST-OCCUPANCY](L1-st-occupancy.md)**<br/>Direct small-molecule engagement of the NR4A3 ligand-binding domain | If the ligand-binding domain is a functional handle in the chimera, then occupying it is enough, and the entire ternary-assembly problem disappears. T… | 3 | ○ blocked · scoped | hedge |
| **[ST-FUSION-DIRECT](L1-st-fusion-direct.md)**<br/>Targeting the fusion protein's other domains | The fusion has more than one surface. If a different domain is more tractable or more selective, the paralogue problem might be sidestepped rather tha… | 3 | ✕ closed · scoped | closed_but_informative |
| **[ST-NUCLEIC-ACID](L1-st-nucleic-acid.md)**<br/>Nucleic-acid and genetic therapeutics | The junction is the only truly tumour-exclusive feature of this disease. A molecule that reads sequence rather than shape can discriminate perfectly, … | 5 | ✓ blocked · computed | hedge |
| **[ST-IMMUNO](L1-st-immuno.md)**<br/>Immunotherapy and antigen-directed approaches | If a tumour-restricted antigen exists, the discrimination problem is solved by the immune system rather than by chemistry, and potency comes free. The… | 9 | ✓ blocked · computed | hedge |
| **[ST-REPURPOSING](L1-st-repurposing.md)**<br/>Repurposing approved and late-stage agents | An approved drug skips discovery, synthesis, toxicology and most of the cost of being right. For an ultra-rare disease with no targeted agent, a mecha… | 7 | ✓ blocked · computed | cheap_option |
| **[ST-RADIOLIGAND](L1-st-radioligand.md)**<br/>Radioligand and theranostic approaches | A radioligand does not need the target to be a driver, only to be present and accessible. That decouples the therapy entirely from the fusion biology … | 2 | ○ blocked · concept | cheap_option |
| **[ST-DEPENDENCY](L1-st-dependency.md)**<br/>Synthetic lethality and dependency | You do not have to drug the driver if the driver has made something else indispensable. A synthetic-lethal partner can be an ordinary, already-druggab… | 3 | ✓ blocked · computed | hedge |
| **[ST-DISSEMINATION](L1-st-dissemination.md)**<br/>Methods and publication as an outcome in itself | A computation-only program with no wet lab advances a disease in exactly two ways: by producing a result someone else tests, or by producing methodolo… | 1 | ○ ready · scoped | dissemination |

## What holds the portfolio down

A blocker on one route is a risk. A blocker on fifteen is the portfolio's shape.

| blocker | kind | routes held | retired by |
|---|---|---:|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | 15 | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |
| **BLK-NOT-FUSION-SELECTIVE** | `fundamental_biological_limit` | 9 | *permanent — nothing* |
| **BLK-PARALOGUE-DDG** | `requires_better_simulation_accuracy` | 7 | `TECH-FE-CRYPTIC-POCKET` |
| **BLK-R4-BINDS** | `requires_wet_lab` | 7 | `TECH-EMC-MODEL-ACCESS` |
| **BLK-NO-WET-LAB** | `requires_external_collaboration` | 6 | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-TERNARY-GEOMETRY** | `requires_better_structure_prediction` | 5 | `TECH-COFOLD-ASSEMBLY`, `TECH-E3-RECRUITER-STRUCTURE`, `TECH-OBSERVED-CRL` |
| **BLK-ANTIGEN-COLD** | `fundamental_biological_limit` | 5 | *permanent — nothing* |
| **BLK-VECTOR-DELIVERY** | `requires_future_technology` | 3 | `TECH-VECTOR-DELIVERY` |
| **BLK-REACH-CATEGORICAL** | `scientific_uncertainty` | 2 | `TECH-EXPOSURE-CRITERION` |
| **BLK-INDUCED-COMPLEX** | `requires_better_structure_prediction` | 2 | `TECH-COFOLD-ASSEMBLY` |
| **BLK-ENDPOINT-MD** | `no_known_assay` | 1 | `TECH-E1-POWERED` |
| **BLK-PARALOGUE-CONTROL** | `no_known_assay` | 1 | `TECH-NONCOVALENT-PARALOGUE-CONTROL` |
| **BLK-FUNCTIONAL-ACTIONABILITY** | `requires_wet_lab` | 1 | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-DELIVERY** | `requires_future_technology` | 1 | `TECH-OLIGO-DELIVERY` |
| **BLK-CLASS-INHERITANCE** | `insufficient_data` | 1 | `TECH-VIRTUAL-CELL` |
| **BLK-UNSIZED-REQUIREMENT** | `scientific_uncertainty` | 1 | *an action we can take* |
| **BLK-SELECTIVITY-CONTROL-UNAUTHORIZED** | `requires_authorization` | 1 | *an action we can take* |

## Highest-leverage things to wait for

Ordered by how much comes back if they land. Full register: [registers/technologies.md](registers/technologies.md).

| fan-out | technology | state | expected | basis |
|---:|---|---|---|---|
| 14 | **TECH-EMC-MODEL-ACCESS** | `absent` | 2029 | `speculative` |
| 11 | **TECH-FE-CRYPTIC-POCKET** | `absent` | 2028 | `extrapolated` |
| 10 | **TECH-EMC-EXPRESSION-DATA** | `early_signals` | 2029 | `speculative` |
| 9 | **TECH-COFOLD-ASSEMBLY** | `partially_landed` | 2027 | `evidence_based` |
| 7 | **TECH-CHEAP-ENSEMBLE** | `partially_landed` | 2027 | `evidence_based` |
| 7 | **TECH-POSE-CONVERGENCE** | `absent` | 2028 | `extrapolated` |
| 6 | **TECH-EXPOSURE-CRITERION** | `absent` | 2027H2 | `extrapolated` |
| 6 | **TECH-VIRTUAL-CELL** | `early_signals` | 2028 | `extrapolated` |
| 6 | **TECH-CLOUD-WET-LAB** | `early_signals` | 2029 | `extrapolated` |
| 5 | **TECH-CHARGE-CHANGE-FEP** | `absent` | 2027 | `extrapolated` |

## Drill down

- **L1** — a strategy family: `L1-<family>.md`
- **L2** — a single route: `L2-<route>.md`
- **Registers** — [blockers](registers/blockers.md) · [technologies](registers/technologies.md) · [instruments](registers/instruments.md)
- **Cross-cutting** — [methods index](methods-index.md) · [readiness](readiness.md) · [requirements](registers/requirements.md)
- **Multi-year** — [the roadmap](roadmap-5yr.md): scientific, technology, AI-capability and lab-capability milestones, and when blocked work becomes revisitable
- **Architecture** — [../ARCHITECTURE.md](../ARCHITECTURE.md) · [../CONVENTIONS.md](../CONVENTIONS.md) · [../MAINTENANCE.md](../MAINTENANCE.md) · [../MIGRATION.md](../MIGRATION.md)
