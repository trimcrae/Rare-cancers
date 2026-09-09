---
id: DOC-NEOANTIGEN-3-CHARACTERISATION
title: "NEOANTIGEN-3 — validated fusion-junction epitopes vs. this repository's predicted EWSR1::NR4A3 junction peptides"
level: L4
kind: investigation-artifact
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Characterisation — rendered from `neoantigen3-correspondence.json`, do not hand-edit

⛔ **Prediction is not presentation.** The 15 validated epitopes come from nine *other* fusion
oncoproteins. Nothing here is evidence that any EWSR1::NR4A3 peptide is or is not presented.
Nine fusions are not a sample of fusions; every comparison below is a statement about the
**prediction set and its allele panel**, not about EMC.

## 1 · Correspondence (each arm separate)

| query set | reference set | exact | substring | isobaric exact (I=L) | isobaric substring |
|---|---|---|---|---|---|
| junction_peptides_174 | validated_junction_epitopes_15 | **0** | **0** | **0** | **0** |
| junction_peptides_174 | non_junction_negative_controls | **0** | **0** | **0** | **0** |
| junction_peptides_174 | other_sequenced_records | **0** | **1** | **0** | **0** |
| predicted_binders_11 | validated_junction_epitopes_15 | **0** | **0** | **0** | **0** |
| predicted_binders_11 | non_junction_negative_controls | **0** | **0** | **0** | **0** |
| predicted_binders_11 | other_sequenced_records | **0** | **0** | **0** | **0** |

Context-level arm (each reference sequence against the full 21-residue junction context of
each of the 5 in-frame junctions, so an epitope lying wholly in a flank would be caught): **1 hit(s)** of 32 reference sequences.

* `SQQSSSYGQQ` — EWSR1::FLI1 / EWSR1::ERG / EWSR1::FEV / EWSR1::WT1 (E38, set `other_sequenced`)
* substring: repo `SQQSSSYGQQN` contains reference `SQQSSSYGQQ` (E38, EWSR1::FLI1 / EWSR1::ERG / EWSR1::FEV / EWSR1::WT1)

**Matcher self-test.** Exact arm recovers 15/15 running the reference set against itself; the
isobaric arm recovers 13 hits on 13 I/L-swapped copies of the reference sequences. The one
substring hit above is a live positive on the real query set. The zeros are therefore not a
dead matcher.

## 2 · What the 15 real ones look like

| property | validated (n=15) |
|---|---|
| length | 9-mer ×11, 10-mer ×2, 11-mer ×2 |
| allotype (epitope-allele pairs) | HLA-A*02:01 ×5, HLA-B*07:02 ×3, HLA-C*04:01 ×2, HLA-A*24:02 ×2, HLA-B*40:01 ×1, HLA-C*12:03 ×1, HLA-A*68:02 ×1 |
| locus | HLA-A ×8, HLA-B ×4, HLA-C ×3 |
| distinct fusion oncoproteins | 9 |
| C-terminal residue | V×3, L×3, T×2, K×2, M×1, C×1, A×1, S×1, F×1 |

### Breakpoint position inside the validated peptides

Stated in the source record, or fixed by another record in the same fusion protein, for
**4 of 15**. The remaining **11 are UNKNOWN**: a peptide sequence alone does not say where the
junction falls inside it, and this lane is offline. They are reported as unknown, not as zero.

| id | fusion | peptide | len | donor residues | acceptor residues | C-terminal anchor from | basis |
|---|---|---|---|---|---|---|---|
| E01 | BCR::ABL1 (b3a2) | `SSKALQRPV` | 9 | 3 | 6 | acceptor | stated |
| E19 | DNAJB1::PRKACA | `EIFDRYGEEV` | 10 | 9 | 1 | acceptor | derived |
| E20 | DNAJB1::PRKACA | `IFDRYGEEV` | 9 | 8 | 1 | acceptor | derived |
| E21 | DNAJB1::PRKACA | `RYGEEVKEF` | 9 | 5 | 4 | acceptor | stated |

UNKNOWN: E09, E10, E11, E12, E13, E14, E15, E16, E18, E25, E26.

## 3 · What this repository predicted

The 174 distinct junction peptides are a **uniform sliding-window tiling** of each junction —
every 8–11mer window that crosses the seam — so their donor/acceptor split is a property of the
enumeration, not of the predictor. Only the ranked binders carry predictive content.

| property | 174 junction peptides (190 instances over 5 junctions) | 11 ranked binders |
|---|---|---|
| length | 8×40, 9×45, 10×50, 11×55 | 9×3, 10×3, 11×5 |
| allotype | n/a (all 10 panel alleles screened) | HLA-A*01:01×4, HLA-B*07:02×3, HLA-B*15:01×2, HLA-B*35:01×1, HLA-B*44:02×1 |
| contains the hybrid seam residue | 190/190 | 11/11 |
| C-terminal residue from | acceptor×170, seam×20 | acceptor×11 |

### The 11 ranked binders, with their partner split

| peptide | allele | len | EWSR1 residues | seam (hybrid) | NR4A3 residues | presentation percentile | class |
|---|---|---|---|---|---|---|---|
| `DMPCVQAQY` | HLA-B*35:01 | 9 | 0 | 1 | 8 | 1.2493 | weak |
| `GDMPCVQAQY` | HLA-B*44:02 | 10 | 1 | 1 | 8 | 0.9687 | weak |
| `NMPCVQAQY` | HLA-B*15:01 | 9 | 0 | 1 | 8 | 0.3736 | strong |
| `RGDMPCVQAQY` | HLA-A*01:01 | 11 | 2 | 1 | 8 | 0.4061 | strong |
| `MPPPLRGDM` | HLA-B*07:02 | 9 | 7 | 1 | 1 | 0.458 | strong |
| `QQNMPCVQAQY` | HLA-B*15:01 | 11 | 2 | 1 | 8 | 0.4986 | strong |
| `DLDMPCVQAQY` | HLA-A*01:01 | 11 | 2 | 1 | 8 | 0.5601 | weak |
| `FDDMPCVQAQY` | HLA-A*01:01 | 11 | 2 | 1 | 8 | 0.6837 | weak |
| `KPGDMPCVQA` | HLA-B*07:02 | 10 | 3 | 1 | 6 | 0.9381 | weak |
| `MPPPLRGDMPC` | HLA-B*07:02 | 11 | 7 | 1 | 3 | 1.2367 | weak |
| `LDMPCVQAQY` | HLA-A*01:01 | 10 | 1 | 1 | 8 | 1.8202 | weak |

**8 of 11** ranked binders take **8 or more of their residues from NR4A3** and at most two from
EWSR1. ⛔ This says nothing about presentation; it is a property of where the predictor's scores
landed on a tiling this repository generated.

## 4 · Allele panel — the one comparison that is directly actionable

| | |
|---|---|
| predictor panel (MHCflurry, 10 alleles) | HLA-A*01:01, HLA-A*02:01, HLA-A*03:01, HLA-A*11:01, HLA-A*24:02, HLA-B*07:02, HLA-B*08:01, HLA-B*15:01, HLA-B*35:01, HLA-B*44:02 |
| allotypes carrying a validated junction epitope | HLA-A*02:01, HLA-A*24:02, HLA-A*68:02, HLA-B*07:02, HLA-B*40:01, HLA-C*04:01, HLA-C*12:03 |
| **in the panel** | HLA-A*02:01, HLA-A*24:02, HLA-B*07:02 |
| **NOT in the panel** | HLA-A*68:02, HLA-B*40:01, HLA-C*04:01, HLA-C*12:03 |
| validated epitope-allele pairs on-panel / off-panel | 10 / 5 |
| HLA-C in the panel | **none** |
| HLA-C among validated allotypes | HLA-C*04:01, HLA-C*12:03 |
| panel allotypes that returned **zero** ranked binders | HLA-A*02:01, HLA-A*03:01, HLA-A*11:01, HLA-A*24:02, HLA-B*08:01 |

