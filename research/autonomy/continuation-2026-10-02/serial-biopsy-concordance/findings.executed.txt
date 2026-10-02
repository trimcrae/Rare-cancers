---
id: MEMO-CHECKPOINT04-CD8-PAIRED-FINDINGS
title: Shared-patient CD8 changes across RNA and IHC
kind: memo
status: live
level: cross-cutting
purpose: Report a newly executed descriptive paired cross-assay analysis of measured sarcoma biopsies.
scope: Thirteen complete patient pairs in published NCT03282344 source data; no efficacy inference.
audience: [maintainers, autonomous research agents]
date: 2026-10-02
last_verified: 2026-10-02
---

## Manuscript-ready addition

The published cross-sectional CD8 RNA–IHC correlation does not itself establish agreement in within-patient change. We therefore linked the published MCP-counter CD8 scores to recovered numerical CD8 IHC by exact patient and timepoint identity, preserving zero values and excluding incomplete pairs without imputation. Only 13 patients had both assays at baseline and on treatment. Changes were calculated as on-treatment minus baseline, using the published RNA score units and IHC percentage points. Six patients (46.2%) had concordant directions: four decreased on both assays and two increased on both. Seven had discordant directions: three had decreasing RNA scores with increasing IHC, and four had increasing RNA scores with decreasing IHC. Neither assay had an exactly zero change in this subset. The Spearman correlation between continuous changes was 0.0604. These sparse descriptive observations do not establish longitudinal interchangeability, identify a cause of disagreement, or contradict the published pooled cross-sectional correlation. Assay scale, biopsy sampling, measurement error and selective availability remain unresolved; no treatment-efficacy or EMC-specific inference follows.

## Support and boundaries

The 13 complete cases span eight published histology categories: osteosarcoma 4, chondrosarcoma 2, liposarcoma 2, and ASPS, leiomyosarcoma, other, small blue round cell and vascular 1 each. UPS/MFH/high-grade MFS contributes none. The ledger retains all 69 sample-registered patients with exact patient IDs, Subject IDs, baseline/on-treatment sample IDs, four measurements, missingness, histology, deltas and directions. These 69 are not the 84 enrolled patients. No histology-specific correlation is estimated. Source patient/timepoint correspondence is verified, but identical aliquots or spatially equivalent material cannot be established from these identifiers.

The bounded novelty check inspected the [primary article](https://doi.org/10.1038/s41467-022-30874-8), its Figure2/FigureS2 and other figure scripts, SetUpData.R and response-comparison code, and the accepted availability/numerical-IHC/composition reanalyses. FigureS2.R already computes pooled CD8 RNA–IHC correlations and separate IHC changes by response. The article reports CD8 Spearman rho 0.74. No paired RNA-change versus IHC-change comparison was found in those scoped sources; this is not an exhaustive literature novelty claim. [FigureS2.R](https://github.com/mskcc/ImmunoSarc/blob/b71c3373bc182f9c647a6f7bc1fbd641d24db917/Figures/FigureS2.R) defines the existing comparison. [SetUpData.R](https://github.com/mskcc/ImmunoSarc/blob/b71c3373bc182f9c647a6f7bc1fbd641d24db917/GeneralProcessing/SetUpData.R) merges MCP-counter output before heatmap Z scoring. Exported scores are analyzed directly, not interpreted as RNA cell percentages.

## Reproduction and actual verification

Plan SHA256: `481c1e8161e94f54074ab34e53a358a44ee2f8c037e21af627e01e60c0a81c6d`; written before the new cohort computation. Inputs are two small pinned files, not raw sequencing or new clinical data. Numerical IHC comes from the accepted source-workbook extraction at da49c4e836533253825587f83656675dac4c913b; its embedded attachment provenance remains intact. The script rejects identity inconsistencies, duplicate sample keys and conflicting IHC values, verifies exact input hashes and rejects pre-existing extraction errors/unmatched rows. Seven synthetic tests passed, covering finite zeros/missingness, rank ties, directional ties, duplicate samples, identity mismatch, conflicts and independent missingness. The final pinned-input analysis exited 0. This was quiet local standard-library computation; no cloud run, primary biological refit, survival analysis or independent scientific review was performed here.

Run `python -B test_pairs.py`, then `python -B analyze_pairs.py .` from this directory after obtaining the pinned inputs via `retrieve_inputs.py`. `results.json` and `patient-ledger.tsv` preserve all cohort results; `sources.json` binds source URLs and bytes. A later independent check should verify the transfer and interpretation; this memo is not a submission-readiness claim.
