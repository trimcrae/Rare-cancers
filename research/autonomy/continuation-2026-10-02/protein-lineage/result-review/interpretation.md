---
id: DOC-PROTEIN-LINEAGE-INDEPENDENT-RESULT-CHECK-20261002
title: Independent check of protein lineage covariance summaries
kind: memo
status: live
level: cross-cutting
purpose: Verify the new saved-measurement rank decompositions and delimit their descriptive interpretation.
scope: Independent standard-library arithmetic on 122 saved family-by-gene measurements; no primary extraction, model fitting or new cohort analysis.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

The independent script passed with process exit code 0. It uses pairwise midrank counting and exact rational within/between covariance numerators, followed by the global rank-variance denominator. All four decompositions, all 24 gene-by-histology-by-support cells, availability counts and archived support flags agree with the supplied result to numerical tolerance 10^-12. The covariance partition identity also holds exactly before floating-point normalization. This checks saved measurements and their summaries; it does not independently recover mass-spectrometry measurements or validate model/accession mappings against primary sources.

| Gene and subset | Pairs | Spearman rho | Within-histology global-rank component | Between-histology global-rank component |
| --- | ---: | ---: | ---: | ---: |
| CSPG4 original | 33 | 0.66577540 | 0.53302139 | 0.13275401 |
| CSPG4 added | 18 | -0.30443756 | -0.09270726 | -0.21173031 |
| L1CAM original | 29 | 0.66995074 | 0.50164204 | 0.16830870 |
| L1CAM added | 17 | -0.48284314 | -0.39583333 | -0.08700980 |

Twelve of 18 CSPG4 added pairs are Ewing's sarcoma. Only four gene-by-histology combinations permit a reported rho in both subsets under the minimum-three-pairs rule:

| Gene and histology | Original n; rho | Added n; rho | Observed sign reversal |
| --- | --- | --- | --- |
| CSPG4 Ewing's sarcoma | 3; -0.5 | 12; -0.18181818 | No |
| CSPG4 osteosarcoma | 8; 0.57142857 | 3; -1 | Yes |
| L1CAM Ewing's sarcoma | 12; 0.56643357 | 6; -0.6 | Yes |
| L1CAM other sarcomas | 6; 0.82857143 | 4; 0.2 | No |

The proposed statement that a between-histology term alone does not arithmetically account for both negative added-subset signs is supported as a descriptive statement. Both added subsets have negative within and between terms. This is not a causal decomposition of filtering or histology, a fixed-composition counterfactual, independent replication, or an EMC result. Only two of four supported within-cell comparisons show observed sign reversal. The remaining eight gene-by-histology combinations do not have both cell correlations supported; their omission from a paired comparison must not erase their available observations.

Global-rank components are not correlations recomputed within each histology. In particular, strata with two pairs can contribute to the global-rank covariance although the cell-rho reporting rule suppresses n<3. In the L1CAM added subset, the osteosarcoma n=2 and rhabdomyosarcoma n=2 within contributions are -0.14705882 and -0.14338235, respectively. Together they contribute -0.29044118 to the total within term of -0.39583333. This sparsity rules out describing the within term as evidence of a universal or robust within-lineage effect. No significance test, confidence interval or mechanistic conclusion is supplied by this arithmetic check.

The local result file is 73,198 bytes with SHA256 `ed98912488a29c97324d2503d65140604c2fd74ee45f3796d6539ff166a29f7e`. Removing exactly one appended terminal LF produces the provided original SHA256 `bfbd5bee8d88053565af54f7f0dea225cb55fed71f688cb4b6cab6f922bc0dbb`. No source bytes were modified. The verifier accepts only the exact expected bytes or this explicitly diagnosed one-byte transport difference.
