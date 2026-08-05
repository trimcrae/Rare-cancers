---
id: DOC-VIEW-INSTRUMENTS
title: Instrument register
level: cross-cutting
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Every method that produces evidence here, and whether it has recovered a known answer.
scope: All instruments. An instrument that has not recovered a known answer cannot support a claim.
audience: ["maintainers", "autonomous research agents", "external reviewers"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# Instrument register

> **An instrument that has never recovered a known answer cannot support a claim, however good
> its output looks.** An instrument whose control FAILED and one that has NO control are different
> facts — and neither is support.

| id | instrument | known-answer control | state | serves |
|---|---|---|---|---|
| **V1** | Structural selectivity descriptor (selcal_interface_signature) | recover the published SMARCA2 Gln1469↔VCB hydrogen bond, unaided, from two crystals | `passes` | R11 |
| **V2** | Ternary generator given both sites (assembly route) | rebuild 6HAX (in-set) and 9DTY (post-horizon) | `passes` | R9, R10 |
| **V3** | Ligand pose prediction (dock + MM-GBSA) | recover a known holo pose in a nuclear receptor from apo | `inconclusive` | R5, R8 |
| **V4** | Selectivity free energy (ABFE) — the selectivity known-answer test | CREBBP vs BRD4(1) / SGC-CBP30 | `none` | R7 |
| **V5** | Alchemical ternary cooperativity (valB_mini ΔΔG_coop) | reproduce a known cooperativity | `fails` | R11 |
| **V6** | Relative FEP (OpenFE, the congeneric lane) | TYK2 ejm_31→ejm_42 benchmark | `passes` | R7 |
| **V7** | ABFE engine, absolute | T4-lysozyme L99A + benzene | `fails` | R7 |
| **V8** | ABFE engine, hydration | methane hydration free energy (FreeSolv) | `passes` | R7 |
| **V9** | λ-overlap diagnostic on the standing ABFE block | a self-check, not a known answer | `none` | R7 |
| **V10** | Interface-mutation physics (pmx/GROMACS) | barnase–barstar Y29A vs published ΔΔG | `passes` | R7 |
| **V11** | Interface-stability endpoint (E1) | two attempts: NR-V04 retrospective, SMARCA2/4 sensitivity control | `fails` | R11 |
| **V12** | Sequence-only co-folding (Boltz-2 ternary) | reproduce 9DTY/9DTX from sequence + ligand | `fails` | R10 |
| **V13** | Cryptic-opening free-energy profile (metadynamics F(Rg)) | Gate 1: a genuine two-state cryptic opening | `fails` | R1, R2 |
| **V14** | BioEmu unbiased ensemble cross-check | ⛔ no in-repo known-answer test on this system | `none` | R1 |
| **V15** | PocketMiner + four permutation nulls | the nulls are the control | `mixed` | R1 |
| **V16** | The causal matched-pair test S (RUNG 5a-KS) | ⛔ none — it has no known-answer calibrator | `none` | R11 |
| **V17** | The exposure criterion EXPOSED_RSA = 0.25 | NR4A1 C551 — the one NR4A-family covalent site with literature support | `fails` | R8, R15 |
| **V18** | The transfer-zone lysine-identity term | ⛔ none exists | `none` | R12 |
| **V19** | The generation-matched null (winner's-curse / generative confound) | the scrambled-objective arm | `mixed` | R7, R15 |
| **V20** | Single-snapshot MM-GBSA margin > 0 as a selectivity verdict | 38 unrelated marketed drugs through the identical funnel | `fails` | — |
| **V21** | The anti-target docking panel (antitarget_dock) | each target's own cognate crystallographic ligand re-docked through the identical protocol | `fails` | R14 |
| **V22** | The scoring-independent second pose method (rDock) | ⛔ none of its own on this system — it is run BESIDE V3 and the comparison IS the test | `none` | R5 |
| **INS-IDR-CENSUS** | FET N-terminal IDR / RGG retention census | the fusions in which ATM suppression was MEASURED (EWSR1::FLI1 type 1, EWSR1::ATF1 clear-cell types) are pushed through the identical pipeline as positive controls | `passes` | the ATR route's structural precondition |
| **INS-CONSTRUCT-DESIGNS** | Transcript-level fusion construct designer (frame computed at the nucleotide level) | each gene model must pass its own translate-and-sum self-check, and Ensembl translations are cross-checked against the UniProt cache | `passes` | the exon-level and residue-level definition of every fusion OBJECT |
| **INS-FUSION-OBJECT-INVENTORY** | Fusion object sequence inventory + breakpoint enumeration | a REPRODUCED gate: five checks on exon coding status, boundaries and protein length, plus both exon maps' translate-and-sum self-checks | `passes` | R13 |
| **INS-MONOVALENT-REACH** | Paired monovalent-vs-bivalent covalent reach enumeration (E3 arm removed) | its BIVALENT half must replicate the already-committed bivalent artifact cell-for-cell | `passes` | R8, the categorical axis at C397 |
| **INS-DDR-AXIS-SCAN** | ATRi/PARPi sensitivity re-cut by FET status (GDSC2) | a general-chemosensitivity correction — the ATRi effect must survive it, and the same lines' PARPi response is computed as the contrast arm | `passes` | the ATR route's pharmacological premise |
| **INS-DEPMAP-KO** | DepMap CRISPR-knockout dependency scan of the ATR axis | the FET-vs-non-FET sarcoma contrast must exceed the panel's own spread | `fails` | the ATR route — as a disclosed failure, never as support |
| **INS-FUSION-COFOLD** | Fusion protein-level co-folding model | ⛔ none of its own | `none` | R13 |
| **INS-HLA-COVERAGE** | HLA population-coverage calculator | ⛔ no known-answer test recorded | `none` | the junction-neoantigen family of routes |

## Which routes cite each instrument

| id | cited as SUPPORT by | disclosed failing on |
|---|---|---|
| **V1** | RT-DEGRADER | — |
| **V2** | RT-DEGRADER | RT-AF3-INTERFACE |
| **V3** | — | RT-COVALENT-PROBE, RT-MONOVALENT |
| **V4** | — | RT-DEGRADER, RT-METHODS-PAPER |
| **V5** | — | RT-DEGRADER, RT-METHODS-PAPER |
| **V6** | RT-DEGRADER | — |
| **V7** | — | RT-DEGRADER, RT-METHODS-PAPER |
| **V8** | RT-DEGRADER | — |
| **V9** | — | — |
| **V10** | — | — |
| **V11** | — | RT-DEGRADER, RT-METHODS-PAPER |
| **V12** | — | RT-DEGRADER, RT-METHODS-PAPER, RT-AF3-INTERFACE |
| **V13** | — | RT-DEGRADER, RT-METHODS-PAPER |
| **V14** | — | — |
| **V15** | — | — |
| **V16** | — | — |
| **V17** | — | RT-DEGRADER, RT-METHODS-PAPER, RT-COVALENT-PROBE, RT-MONOVALENT |
| **V18** | — | RT-UBIQ-SELECTIVE |
| **V19** | — | — |
| **V20** | — | RT-DEGRADER, RT-METHODS-PAPER |
| **V21** | — | RT-DEGRADER, RT-METHODS-PAPER |
| **V22** | — | — |
| **INS-IDR-CENSUS** | RT-ATR-ASSESS | — |
| **INS-CONSTRUCT-DESIGNS** | RT-ATR-ASSESS | — |
| **INS-FUSION-OBJECT-INVENTORY** | — | — |
| **INS-MONOVALENT-REACH** | RT-MONOVALENT | — |
| **INS-DDR-AXIS-SCAN** | RT-ATR-ASSESS | — |
| **INS-DEPMAP-KO** | — | RT-ATR-ASSESS |
| **INS-FUSION-COFOLD** | — | — |
| **INS-HLA-COVERAGE** | — | RT-JUNCTION-NEOANTIGEN, RT-VACCINE, RT-TCR-IMMTAC, RT-TCRT-CTA |

[← L0](../L0-ecosystem.md)
