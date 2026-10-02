---
id: "DOC-DATA-OPPORTUNITIES-2026-09-30-PROTOCOLS-EXPERIMENTAL-DATA-PROTOCOLS"
title: "Three protocols for new analyses of measured public data"
level: "cross-cutting"
kind: "memo"
status: "live"
canonical_for: []
purpose: "Record the scoped evidence and reasoning for Three protocols for new analyses of measured public data."
scope: "September 30 measured-data campaign; retain the source qualifications, execution boundaries and historical status stated in the body."
audience: ["maintainers","autonomous research agents"]
date: "2026-09-30"
last_verified: "unverified"
_backfilled: "true"
---

# Three protocols for new analyses of measured public data

These protocols address biological or measurement questions that existing experiments could answer. None of the three analyses has been executed in this campaign. The [candidate catalogue](../candidate-catalogue.json) and [ranking](../RANKING.md) distinguish completed drafts from these future opportunities. All 33 registered backlog endpoints are assessed in [backlog-assessment.md](../backlog-assessment.md); this is a metadata assessment, not a full source reread of every manuscript.

## Spatial organization beyond cell abundance in UPS and MFS

**Question:** Do CD8-positive cells occupy tumour neighbourhoods differently in UPS and higher-grade myxofibrosarcoma after accounting for cell abundance, ROI geometry and tissue structure?

Source: van Oost et al., [DOI 10.1007/s00262-025-04123-y](https://doi.org/10.1007/s00262-025-04123-y), [author code](https://github.com/svanoost/immunogenic-features-of-ups-and-mfs) at tree bd1417ecee3c0d7ea7724c05c11c6c02ab3e9465, RNA accession GSE285944, imaging accession [S-BIAD1555](https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD1555).

Inspected annotations contain 29 baseline patients (15 MFS/14 UPS), including five low-grade MFS, and 42 paired specimens from 21 patients (eight MFS/thirteen UPS pairs), with 32 phenotype labels. Counts describe annotations, not verified imaging availability. The code already analyzes density, abundance and survival; repeating those is not the proposed contribution. Its paired script notes no FDR-significant MFS density changes.

The GitHub tree lacks cell coordinates and the referenced phenotype-count table. Raw imaging retrieval, masks and segmentation availability remain unverified; survival data are requestable. Proceed only after retrieving and hashing coordinate/mask exports, cell labels, ROI areas and specimen mappings. Reproduce enough source counts to catch mapping/segmentation errors. Patient 4620 has untreated L7306 in baseline annotation but L7307 in paired annotation: reconcile or exclude that pair. “Treated” is not sufficient to infer regimen, timing or radiotherapy/checkpoint blockade.

Freeze phenotype definitions before examining associations: CD8_Tcells plus CD8_KI67_Tcells; tumour cells from supplied cell_type=Tumor mapping. Prefer shared mask boundaries for actual adjacency. With coordinates alone, use a distance-capped graph whose radius is fixed from resolution/cell-size information; call this a neighbourhood, not physical contact.

The primary ROI endpoint is the fraction of CD8 cells with at least one tumour neighbour. Compare observed fraction with 10,000 within-ROI phenotype-label permutations preserving coordinates, graph and phenotype counts. Report observed-minus-expected fraction and standardized enrichment where null variance permits. This preserves geometry and abundance but does not distinguish compartment segregation from biological interaction. Add independently annotated compartment-restricted permutations, or prespecified spatial-block sensitivity with its limitations.

Aggregate to specimens and patients with equal ROI weights as primary and cell-count weights as sensitivity. Patients, not ROIs or cells, are inferential units. Compare baseline UPS with higher-grade MFS, stratifying by supported grade and retaining low-grade MFS as descriptive. Use patient-level effects, diagnosis permutation within supported strata and patient bootstrap uncertainty.

Secondary paired changes use within-patient status swaps and retain histology. They describe specimen-state associations; an uncontrolled pre/post comparison does not identify a treatment effect. Separate the primary contrast from secondary families; correct the entire exploratory phenotype-pair family for FDR.

Patient deletion is stability analysis, not independent validation. Any tuned graph, radius, selected combination or predictor requires patient-separated training and evaluation. Stop if coordinates/masks, ROI identity or mappings are unavailable. A density-only substitute cannot answer the spatial question. Publication requires a stable contribution beyond abundance or a precise failure of a prespecified meaningful spatial effect. Wide intervals mean inconclusive, not absence of organization. No result transfers automatically to EMC or proves immune function.

## RNA-based protein prioritization in held-out sarcoma models

**Question:** How well does a previously fixed transcript panel predict measured whole-cell protein in sarcoma cell lines excluded from development?

Sources: pan-cancer map of 949 human lines, PMID 35839778/[PMC9387775](https://pmc.ncbi.nlm.nih.gov/articles/PMC9387775/), raw PXD030304, [processed Figshare 19345397](https://figshare.com/articles/dataset/19345397), [author code](https://github.com/EmanuelGoncalves/cancer_proteomics). The original study already substantially compares RNA and protein and benchmarks prediction. Inspect its figures/models/supplements first: a generic correlation analysis duplicates prior work.

Processed matrices, actual sarcoma counts, panel coverage, batches and drug/CRISPR overlap have not been retrieved. Audit stable identifiers, aliases, lineages, related derivatives, matched RNA/protein, replicates and quantification. Keep related models in one split. H-EMC-SS has unresolved disease identity and cannot validate EMC. No confirmed EMC model is established here. Whole-cell protein does not measure accessible tumour surface or peptide-HLA presentation; nondetection is missing/censored measurement, not zero.

Freeze the existing 11-gene panel: CD276, SSTR2, PRAME, FAP, CD248, CSPG4, MSLN, L1CAM, GPC3, ALPP, CDH17. Keep CHRNA6 as a separately identified prior RNA-marker control. Do not reduce the panel because some proteins perform well or disappear. Report all coverage failures.

Hold all sarcoma models out of fitting, normalization parameter estimation, feature selection, tuning and calibration. Develop simple gene-specific RNA-to-protein models and a selected predictor in non-sarcoma lines using nested lineage-grouped folds, compare with reproducible author baselines, then freeze before sarcoma evaluation.

The primary endpoint is macro-averaged normalized mean absolute prediction error across supported panel genes and sarcoma lineages, with training-derived scales. Report relative error improvement over the fixed baseline and line-grouped uncertainty. Give quantification coverage, calibration slope/intercept, error and rank agreement per gene. A secondary prioritization endpoint is concordance between RNA upper-quartile and measured protein upper-quartile lines; freeze tie handling and minimum lineage size before test inspection.

Observed-protein performance is conditional on quantification. Investigate abundance-dependent missingness and supported sensitivity bounds. As explicit planning conventions, at least two sarcoma lineages, 20 independent matched lines and six panel proteins quantified in 70% of test lines could screen feasibility. These thresholds do not guarantee precision; evaluate precision using development data.

Drug/CRISPR measurements may provide secondary outcome validation after target–outcome mappings are frozen from external evidence. They cannot select the panel, predictor or favorable threshold. Use within-lineage associations, grouping derivatives, and compare protein-informed versus RNA-only predictions on identical models/outcomes. Pleiotropic drugs need mapping uncertainty. Reusing the same outcome to define and validate target reliability is circular.

Stop if original work already answers the exact transfer question, coverage is inadequate or leakage cannot be prevented. Publication requires a meaningful, reproducible improvement or consequential calibration failure; a planning 10% relative error reduction is a computational convention, not a clinical threshold. Wide intervals are inconclusive. No result establishes EMC drug sensitivity or clinical response.

## External transfer of a pre-existing fusion-output candidate gene set

**Question:** Does the existing NR4A3/fusion-output gene set transfer to an overlap-reduced EMC tissue cohort and distinguish it from relevant sarcoma classes?

Source: [Zenodo 17866629](https://doi.org/10.5281/zenodo.17866629), 19,116 genes/704 patients; TPM SHA256 b0d665d1bd1d96ace1faf66cc5a4d7ab7e41cb487c8f0f61734f102a1f9a7af3. The [existing manifest](../../atlas-hofvander-validation-2026-09-06/metadata-manifest.json) retains nine of thirteen source EMC specimens after three known-overlap exclusions (104-92, 168-97, 536-00) and one recurrence (5081-14). A two-overlap shorthand in discovery notes was insufficient: preserve the manifest's three until a source-case reconciliation justifies change.

Map every retained patient against every prior candidate gene set discovery/validation cohort. Nine eligible specimens do not guarantee nine independent specimens relative to every source. Year matching currently supports only four unique EMC patients; pairwise comparisons cannot inflate that count.

The existing fusion-output manuscript identifies SEMA3C, PPARG, ENO3 with a chimera DNA-binding assay and combines them with 16 native-NR4A3 targets for scoring. These evidence classes remain separate; the 19-gene set is not nineteen validated fusion targets. The existing manuscript's Table 8 reports that the pooled 19-gene A+B candidate set was not distinguishable from its size-matched null on either source platform, reaching 39% and 88% of the respective thresholds. This external test must preserve that prior negative. Export and hash the exact existing membership, directions and scoring before opening atlas values. Do not remove genes that fail.

If the score cannot transfer across platforms, date and freeze a replacement using prior cohorts/platform information only. Within-specimen ranks are one candidate, not a retroactively attributed original method. The primary endpoint is score probability of superiority for EMC versus an equal-histology mixture of myxoid liposarcoma, LGFMS and synovial sarcoma, with separate comparator estimates. MFS and DFSP are prespecified specificity contexts. Do not optimize a classifier or diagnostic cutoff using nine EMCs.

Resample patients with fixed histology weights for uncertainty. Secondary endpoints are the three core genes, prior-cohort direction transfer and wider-atlas specificity, with FDR for the declared family. Use 10,000 matched gene sets for size, detectable expression and variability, matched using diagnosis-blinded background summaries; consider correlation matching where feasible. This null tests unusual behavior versus comparable sets, not disease specificity.

Keep all choices outside atlas validation. Patient deletion is sensitivity, not another cohort. Delete each sequencing year and preserve year-matched comparator reversals using four unique EMCs. Evaluate purity/tissue-composition measures if available. Bulk expression cannot distinguish fusion regulation from lineage, matrix, muscle admixture or other components. Partner-specific analysis needs verified partner labels and adequate counts.

Stop the external-validation claim if overlap remains unresolved, membership cannot be reproduced or a scoring change follows outcome inspection. A useful extension must establish transfer, limited class specificity or a precise failure of a prospectively fixed specificity target. A superiority target 0.70 is a planning convention, not diagnostic validation; nonsignificance at nine patients does not establish absence.

This should extend the existing fusion-output paper unless the new question warrants a separate contribution. It should not become another CSPG4 paper using the same atlas. RNA does not establish protein, chromatin occupancy, dependency or efficacy.

## Deliverables and boundary

Each activated project needs source hashes and identity mappings, a dated frozen endpoint/split manifest, complete outputs including nulls/coverage failures, sensitivity results and replay code, followed by one finite independent review. Access failure, duplication or inadequate precision ends the corresponding claim with a durable explanation. These protocols supply executable designs; they contain no invented Results, executed-model claim or journal-acceptance probability.
