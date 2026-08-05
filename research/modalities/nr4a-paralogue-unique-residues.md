---
id: DOC-NR4A-PARALOGUE-UNIQUE-RESIDUES
title: NR4A3 paralogue-unique reactive residues — the categorical selectivity axes
level: L4
kind: memo
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `memo` from its location under research/modalities/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# NR4A3 paralogue-unique reactive residues — the categorical selectivity axes

A residue type present in NR4A3 and absent at the aligned position in BOTH paralogues is a selectivity mechanism that does not depend on winning a ~1 kcal/mol free-energy contest: cysteines gate covalent capture, lysines gate ubiquitin transfer.

*Method:* UniProt FASTA + Needleman-Wunsch global alignment (NR4A3 as reference) for uniqueness; Shrake-Rupley RSA + reactive-atom distances on the matched opened LBD model for reachability. Pure stdlib.

## Summary

- NR4A3 cysteines: **20**, of which **4** are absent in BOTH paralogues (2 solvent-exposed).
- NR4A3 lysines: **31**, of which **4** are absent in BOTH paralogues (3 solvent-exposed).

## Axis 1 — NR4A3-unique cysteines (covalent-capture handles)

| NR4A3 | NR4A1 | NR4A2 | RSA | d(pocket) Å | d(nearest docked lig) Å | reach |
|---|---|---|---|---|---|---|
| C166 | H160 | N151 | — | — | — | — |
| C397 | N363 | S363 | 0.395 | 10.86 | 12.3 | exit_vector |
| C420 | Q388 | A389 | 0.311 | 18.34 | 16.04 | linker_borne |
| C559 | Q528 | Q528 | 0.095 | 12.8 | 13.45 | linker_borne |

## Axis 2 — NR4A3-unique lysines (ubiquitination-site handles)

| NR4A3 | NR4A1 | NR4A2 | RSA | d(pocket) Å | d(nearest docked lig) Å | reach |
|---|---|---|---|---|---|---|
| K178 | R171 | I163 | — | — | — | — |
| K518 | L487 | V487 | 0.413 | 13.44 | 14.06 | linker_borne |
| K572 | A540 | N543 | 0.879 | 11.45 | 15.14 | exit_vector |
| K592 | T564 | T564 | 0.506 | 16.23 | 17.15 | linker_borne |

## Reciprocal — reactive residues a paralogue has and NR4A3 lacks

(These are the anti-handles: sites where a paralogue is addressable and NR4A3 is not. NR4A1 Cys551 — the celastrol/NR-V04 site — is the precedent this whole map mirrors.)

- **NR4A1**: 5 unique cysteines (C78, C111, C136, C534, C551)
- **NR4A2**: 2 unique cysteines (C190, C534)

## Fusion context — lysines the EWSR1 moiety contributes

Present on EWSR1::NR4A3, absent from NR4A1/NR4A2 entirely and from the NR4A3 LBD construct. Breakpoint scenarios, not an asserted breakpoint.

| scenario | EWSR1 residues kept | lysines |
|---|---|---|
| exon7_like_1_264 | 1–264 | **1** |
| modelled_keep_200 | 1–200 | **1** |
| exon12_like_1_349 | 1–349 | **2** |

## Gate

**GO on BOTH categorical axes — at least one exposed NR4A3-unique cysteine is within tether range of the warhead pocket (covalent-capture axis) AND at least one exposed NR4A3-unique lysine exists (ubiquitination-site axis). Search these BEFORE, not after, the ~1 kcal/mol interface-thermodynamics axis.**

## Honest limits

- Sequence uniqueness is exact; everything downstream (reachability, adduct formation, transfer competence) is a HYPOTHESIS generated for testing, not a result.
- Reachability uses ONE static opened conformer and a heavy-atom distance to the cryptic pocket — not a docked electrophile or a linker conformer search.
- Intrinsic cysteine reactivity (pKa, local electrostatics, hard/soft preference) is NOT computed.
- Lysine uniqueness does not by itself establish ubiquitination competence — that is a geometry question for the ternary/CRL stage.
- No efficacy, safety, therapeutic-window or clinical claim is made or implied.
