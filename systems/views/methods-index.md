---
id: DOC-VIEW-METHODS
title: Methods index — instrument to routes served
level: cross-cutting
kind: generated
status: generated
generator: systems/systems_check.py
purpose: The method axis, which is deliberately an index rather than a level of the hierarchy.
scope: Every instrument and the routes it serves, plus the technologies that would improve it.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# Methods index

**Why this is an index and not a level.** A method serves many routes at once — the same pose
instrument is cited by three routes in two different families. If method were a level of the
hierarchy, every shared instrument would be duplicated into each family and its status would
have several homes, which is the one-fact-many-places bug in a new costume. Modality partitions
the routes cleanly; method cuts across them, so it gets this view.

| instrument | control state | routes served | technology that would improve it |
|---|---|---|---|
| **V1** Structural selectivity descriptor (selcal_interface_signature) | `passes` | RT-DEGRADER | — |
| **V2** Ternary generator given both sites (assembly route) | `passes` | RT-AF3-INTERFACE, RT-DEGRADER | — |
| **V3** Ligand pose prediction (dock + MM-GBSA) | `inconclusive` | RT-COVALENT-PROBE, RT-MONOVALENT | `TECH-POSE-CONVERGENCE` |
| **V4** Selectivity free energy (ABFE) — the selectivity known-answer test | `none` | RT-DEGRADER, RT-METHODS-PAPER | `TECH-FE-CRYPTIC-POCKET` |
| **V5** Alchemical ternary cooperativity (valB_mini ΔΔG_coop) | `fails` | RT-DEGRADER, RT-METHODS-PAPER | `TECH-CHARGE-CHANGE-FEP`, `TECH-TERNARY-ALCHEMY` |
| **V6** Relative FEP (OpenFE, the congeneric lane) | `passes` | RT-DEGRADER | `TECH-CHARGE-CHANGE-FEP`, `TECH-ATOM-MAPPER` |
| **V7** ABFE engine, absolute | `fails` | RT-DEGRADER, RT-METHODS-PAPER | `TECH-FE-CRYPTIC-POCKET` |
| **V8** ABFE engine, hydration | `passes` | RT-DEGRADER | — |
| **V9** λ-overlap diagnostic on the standing ABFE block | `none` | — | `TECH-FE-CRYPTIC-POCKET` |
| **V10** Interface-mutation physics (pmx/GROMACS) | `passes` | — | — |
| **V11** Interface-stability endpoint (E1) | `fails` | RT-DEGRADER, RT-METHODS-PAPER | `TECH-E1-POWERED` |
| **V12** Sequence-only co-folding (Boltz-2 ternary) | `fails` | RT-AF3-INTERFACE, RT-DEGRADER, RT-METHODS-PAPER | `TECH-COFOLD-ASSEMBLY` |
| **V13** Cryptic-opening free-energy profile (metadynamics F(Rg)) | `fails` | RT-DEGRADER, RT-METHODS-PAPER | `TECH-CHEAP-ENSEMBLE` |
| **V14** BioEmu unbiased ensemble cross-check | `none` | — | `TECH-CHEAP-ENSEMBLE` |
| **V15** PocketMiner + four permutation nulls | `mixed` | — | — |
| **V16** The causal matched-pair test S (RUNG 5a-KS) | `none` | — | — |
| **V17** The exposure criterion EXPOSED_RSA = 0.25 | `fails` | RT-COVALENT-PROBE, RT-DEGRADER, RT-METHODS-PAPER, RT-MONOVALENT | `TECH-EXPOSURE-CRITERION` |
| **V18** The transfer-zone lysine-identity term | `none` | RT-UBIQ-SELECTIVE | `TECH-OBSERVED-CRL` |
| **V19** The generation-matched null (winner's-curse / generative confound) | `mixed` | — | — |
| **V20** Single-snapshot MM-GBSA margin > 0 as a selectivity verdict | `fails` | RT-DEGRADER, RT-METHODS-PAPER | — |
| **V21** The anti-target docking panel (antitarget_dock) | `fails` | RT-DEGRADER, RT-METHODS-PAPER | `TECH-ANTITARGET-PROTOCOL` |
| **V22** The scoring-independent second pose method (rDock) | `none` | — | `TECH-POSE-CONVERGENCE` |
| **INS-IDR-CENSUS** FET N-terminal IDR / RGG retention census | `passes` | RT-ATR-ASSESS | — |
| **INS-CONSTRUCT-DESIGNS** Transcript-level fusion construct designer (frame computed at the nucl | `passes` | RT-ATR-ASSESS | — |
| **INS-FUSION-OBJECT-INVENTORY** Fusion object sequence inventory + breakpoint enumeration | `passes` | — | — |
| **INS-MONOVALENT-REACH** Paired monovalent-vs-bivalent covalent reach enumeration (E3 arm remov | `passes` | RT-MONOVALENT | — |
| **INS-DDR-AXIS-SCAN** ATRi/PARPi sensitivity re-cut by FET status (GDSC2) | `passes` | RT-ATR-ASSESS | — |
| **INS-DEPMAP-KO** DepMap CRISPR-knockout dependency scan of the ATR axis | `fails` | RT-ATR-ASSESS | — |
| **INS-FUSION-COFOLD** Fusion protein-level co-folding model | `none` | — | — |
| **INS-HLA-COVERAGE** HLA population-coverage calculator | `none` | RT-JUNCTION-NEOANTIGEN, RT-TCR-IMMTAC, RT-TCRT-CTA, RT-VACCINE | `TECH-JUNCTION-PMHC` |
| **INS-GEO-SERIES-CHARACTERISE** Sample-level GEO series characterisation + disease-label corroboration | `passes` | — | — |

[← L0](L0-ecosystem.md)
