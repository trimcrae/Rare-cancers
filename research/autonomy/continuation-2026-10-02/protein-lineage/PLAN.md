---
id: DOC-CHECKPOINT03-PROTEIN-LINEAGE-PLANNING
title: Feasibility of a within-histology protein quantification-support follow-up
level: cross-cutting
kind: memo
status: live
purpose: Determine whether lineage composition explains the reported original-versus-added protein quantification contrast using existing experimental measurements.
scope: CSPG4 and L1CAM in the frozen 61-family sarcoma panel; source inspection and a conditional descriptive analysis plan, with no new correlations or model refits.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

# Feasibility finding

The specific original-versus-additionally-quantified **within-histology** comparison is not reported or implemented in the inspected pinned producers. Public inputs are sufficient for a bounded follow-up, but the compact committed result artifacts alone are insufficient: they do not preserve the 8,498-matrix protein values for every family. The next work should therefore begin with a small, durable two-antigen measurement extract in cloud, not with predictor refitting or another full multi-omics run.

All repository paths below are beneath `research/autonomy/data-opportunities-2026-09-30/` at `da49c4e836533253825587f83656675dac4c913b`; exact Git blob identities are in `feasibility-receipt.json`.

## What was already done

`drafts/sarcoma-antigen-protein-transfer-short-report.md` reports positive RNA–8,498-protein correlations in original support and negative correlations in added support: CSPG4 original n=33/rho=0.666, added n=18/rho=-0.304; L1CAM original n=29/rho=0.670, added n=17/rho=-0.483. These are established aggregate results, not new calculations here.

`deep-analysis/protein_overlap_actual.py`, function `protein_overlap_diagnostics`, constructs original and added subsets after family aggregation, then calls `correlation` on each entire subset. Inside `correlation`, histology controls which families are resampled for confidence intervals, but the point estimate remains a pooled Spearman correlation. Histology-stratified resampling does not remove between-histology covariance. The script does not calculate original-versus-added within-histology correlations or a within/between covariance decomposition.

`deep-analysis/finite_protein_cross_assay.py` does have `perLineageRNAtoBroadProtein`, preserved in `deep-analysis/results/protein-less-filtered-and-Broad-assays-actual.json`. That is a different comparison involving Broad measurements; it does not answer this support-subset question. Similarly, the manuscript's histology/growth-adjusted drug and CRISPR associations do not answer it. The definitive pooled subset results live in `deep-analysis/results/protein-three-antigens-assay-overlap-final.json`, run36905457130/job110514841009.

## Available measurements and exact gap

`deep-analysis/results/protein-RNA-final-matched-measurements.json` preserves 786 model metadata rows, RNA records and original 6,692-matrix protein records. The 61 primary models correspond to 61 distinct `relatedGroup` families. Their fixed reported histologies are 23 Ewing sarcoma, 11 osteosarcoma, 11 other sarcomas, seven rhabdomyosarcoma, five chondrosarcoma and four leiomyosarcoma. Necessary join fields are `model_id`/measurement `index`, `relatedGroup`, `Cancer_type` and `primarySarcomaTest`.

The 8,498 values were created transiently as `less` in the overlap script. The result JSON stores correlations and assay-common-family identifiers, not the full original/added family tables. Consequently, the histology composition and within-histology support of the added subsets cannot be recovered honestly from the printed n/rho values.

The missing values are in the public [94,222,540-byte 8,498-matrix file](https://ndownloader.figshare.com/files/34411172), SHA256 `5e7adf7e8217e5a02389c299dce1266e74c7a3b786b8c177e56d12402fe783ac`. The producer maps CSPG4 to accession Q6UVK1 and L1CAM to P32004, averages matching accession columns and normalizes model identifiers before joining the frozen metadata. Reuse exactly that mapping and arithmetic.

Cloud artifact11184670046 remains listed as unexpired, size44,166,685 bytes, expiration October31. Its producing workflow includes text caches in uploaded paths, so it is a candidate source-cache recovery route. Its ZIP members were not inspected; cache availability is not established. If absent, one bounded cloud fetch of the pinned 8,498 file suffices. The 246 MB HDF5/Broad input is unnecessary because this question uses already-preserved RNA and original protein values. No full matrix was downloaded locally.

## Finite descriptive plan, frozen before examining new strata

1. Recover only CSPG4/L1CAM values for the existing primary61 models from the pinned 8,498 matrix. Preserve model/family/lineage, original RNA, original protein, added-matrix protein, explicit missingness and source hashes in a compact permanent table. Apply the existing family mean aggregation; assert the61-family membership rather than rebuilding or expanding the cohort. Hash-bind all inputs. Do not rerun development fitting, predictor selection, permutations or drug/CRISPR analyses.
2. Reconstruct the existing original support definition (RNA plus both protein measurements available) and added support definition (original protein missing, RNA plus 8,498 protein available). Confirm the published n and pooled correlations as a source/processing check. A mismatch stops the new analysis; it is not repaired by selecting different rows.
3. Publish a complete two-gene by six-histology by two-support table: family counts, RNA/protein availability and distinct-value counts. Do not select histologies based on their correlation signs or significance. Retain the pre-existing correlation function's rule: rho undefined with fewer than three paired families or constant measurements. Mark unsupported cells explicitly.
4. For every supported cell, report descriptive within-histology Spearman rho for RNA versus the same 8,498 measurement. Compare original and added support only where both cells are defined. Do not pool undefined cells, change thresholds or label a sparse stratum as evidence of absence. This resolves whether observed reversals recur within any adequately supported shared histology.
5. For each gene/support subset, decompose its already-defined pooled Spearman coefficient exactly. Let X and Y be average-tie ranks within that complete support subset. With family weights and observed histology weights, Cov(X,Y) equals the weighted within-histology covariances plus the covariance of histology-specific rank means. Divide both components by the same global rank standard deviations; their sum must reproduce the pooled rho. Emit both signed components, including singleton strata whose within contribution is zero. This is an arithmetic diagnostic, not a new significance test or causal adjustment.

No new P values, data-driven cutoffs or fitted clinical models are proposed. The plan is a post hoc follow-up motivated by the known pooled signs, not a preregistration. If shared within-histology cells are too sparse, that is the result: the data do not resolve persistence, even if a pooled decomposition is computable. A between-lineage component dominating the sign can explain the observed pooled arithmetic, but cannot establish that lineage is causally sufficient or that quantification selection has no within-lineage effect. Persisting within-lineage differences likewise cannot identify filtering as their cause.

## Deliverable and stopping condition

One compact source-bound two-antigen table, one complete support/lineage diagnostic table, and four pooled-rank decompositions. Stop after this fixed descriptive analysis and preserve all unsupported cells. A defensible manuscript addition would distinguish a compositional explanation of the pooled correlation from evidence that the relationship persists within a lineage. No surface-accessibility, treatment-response, independent-patient or EMC-specific inference follows.

This checkpoint performed source/code inspection and feasibility assessment only. No new RNA–protein association, uncertainty interval or biological result has been computed.
