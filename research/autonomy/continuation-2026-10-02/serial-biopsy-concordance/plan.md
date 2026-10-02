---
id: MEMO-CHECKPOINT04-CD8-PAIRED-PLAN
title: Paired CD8 cross-assay change analysis plan
kind: memo
status: live
level: cross-cutting
purpose: Freeze a narrowly new descriptive question before computing shared-patient results.
scope: Published numerical CD8 IHC and RNA-derived CD8 scores in NCT03282344.
audience: [maintainers, autonomous research agents]
date: 2026-10-02
last_verified: 2026-10-02
---

This plan precedes computation of the shared paired cohort and its change results. The author code at mskcc/ImmunoSarc b71c3373bc182f9c647a6f7bc1fbd641d24db917 FigureS2.R already computes pooled cross-sectional RNA–IHC correlations, and separate IHC changes versus response. The primary paper reports CD8 Spearman rho 0.74. This analysis is restricted to whether within-patient changes agree across the two assays; it does not claim a new discovery of cross-sectional concordance.

Use SampleSourceData.txt at that author revision and the frozen numerical-IHC extraction JSON in trimcrae/Rare-cancers da49c4e836533253825587f83656675dac4c913b, deep-analysis/results/ImmunoSarc-measured-numeric-IHC-actual.json. Join exact SampleID to numericCells.sampleKey, requiring Subject, timepoint and Cohort equality; require SampleID = PatientID + semicolon + SampleTimepoint. Reject duplicate patient/timepoint, inconsistent patient–Subject mapping, conflicting IHC values, or missing join targets. Retain all sample-registered patients in an availability ledger, with histology and four independent missingness flags. Include in the change analysis only patients with finite RNA T-cell (CD8) and finite numerical CD8 IHC at both exact labels Baseline and On-Treatment. Progression is excluded. Preserve zero as observed, never as missing; no imputation or cutoff selection.

Changes are on-treatment minus baseline: RNA in the published MCP-counter score units, not cell percentages, and IHC in percentage points of positive cells. SetUpData.R merges raw MCP-counter outputs into clin2 before constructing separate heatmap Z scores; use the published numeric score column directly, without timepoint standardization. Display continuous changes for every included patient. Compute Spearman correlation using average ranks and Pearson covariance of ranks; no inferential P value or survival/efficacy model. Count the full 3 by 3 sign table (negative, exactly zero, positive), report same nonzero direction among nonzero pairs and among all shared pairs, and report ties separately. Exact decimal input differences determine ties; no tolerance or data-driven threshold. Report histology counts for inclusion and exclusion, without sparse within-histology correlations.

Tests must cover rank ties, finite zero versus missing, exact delta ties, duplicate IDs, inconsistent identity, conflicting numerical IHC, and a known synthetic directional example. Record input SHA256 and frozen plan SHA256. Stop after the bounded descriptive result and limitations; no clinical, causal, mechanistic, independent-replication or EMC-specific conclusion. Same patient/timepoint does not prove identical biopsy aliquots or spatial sampling; assay scales and sampling differences may contribute to disagreement.

Primary sources: https://doi.org/10.1038/s41467-022-30874-8 and https://github.com/mskcc/ImmunoSarc/blob/b71c3373bc182f9c647a6f7bc1fbd641d24db917/Figures/FigureS2.R and https://github.com/mskcc/ImmunoSarc/blob/b71c3373bc182f9c647a6f7bc1fbd641d24db917/GeneralProcessing/SetUpData.R . Literature/code inspection is scoped to the primary article and its repository plus accepted local reanalyses, not an exhaustive novelty search.
