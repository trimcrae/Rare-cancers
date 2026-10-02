---
id: DOC-METH-PACKAGE-SUPPLEMENT-20261002
title: Methylation methods and reproducibility supplement
level: L3
kind: report
status: live
purpose: Prepare the completed methylation empirical methods study for author and journal review.
scope: Dataset-specific secondary analysis; no publication authorization or readiness claim.
audience: [maintainers, external reviewers]
date: 2026-10-02
last_verified: 2026-10-02
related: []
---

# Online Resource 1

Training support and score weighting alter conclusions in a public sarcoma methylation reanalysis

Tristan D. McRae

## Scope and data lineage

This supplement explains the completed empirical analysis and the compact reproducibility archive. It adds no model fit, statistical test, or external-cohort prediction. The analysis source revision is da49c4e836533253825587f83656675dac4c913b in trimcrae/Rare-cancers. The final reviewed working manuscript is preserved at continuation revision 5d2f2e2116f43c0bb56a46120902a1332f27720b, SHA256 7e249932cb12aa4eaa85cd130c76099c2cfb1a0edb7cd31065d31ac4c19cd028. The accompanying journal manuscript is an editorial and format adaptation of that version.

Four frozen result objects are included under results/ in Online Resource 2: methylation-corrected-full-support-actual.json (grouped analysis), methylation-processed-external-validation-final.json (428-profile comparison), methylation-hallmark-fusion-score-transport-final.json (fusion subset and sensitivities), and methylation-hallmark-fusion-selected-cases-final.json (discordant cases). Each table records its source file and JSON pointer. The original source workbooks and accession metadata are preserved under source-audits/.

## Definitions and implementation

Let p(i,k) be the random-forest vote for profile i and class k, and y(i) its comparison label. Multiclass Brier loss is sum over k of (p(i,k) minus the indicator of k=y(i)) squared. The reported Brier score is the arithmetic mean of these class-sum losses across profiles; it is not divided by the number of classes. Raw Brier values use the original votes.

For negative log likelihood, input votes are floored at epsilon and normalized. Write q(i,k) = max(p(i,k),epsilon) / sum over j of max(p(i,j),epsilon). The transformed score is q(i,k) raised to (1/T), divided by the sum of these values over classes. Negative log likelihood is minus the natural logarithm of the comparison-label score. Computation uses log-sum-exp and does not clip transformed outputs. Epsilon is 0.000001 for the principal result, with 0.0001 and 0.00000001 sensitivities. The reference out-of-fold objective is optimized over log(T), bounded by log(0.05) and log(10), using scipy.optimize.minimize_scalar with method bounded and xatol=0.0000001. The temperature is refitted separately for each input epsilon. No validation label enters that optimization.

Profile weighting averages all 120 losses. Equal-class weighting averages each of the 12 class-specific mean losses once. This post hoc reaggregation changes the target class distribution. Four classes supply 91 profiles and three classes contain one profile each. Neither weighting creates population representativeness or precise rare-class inference. Online table 1 contains the class losses; Online table 2 contains the input-floor sensitivity. The three discordant cases remain in every applicable summary.

## Grouped validation and matched support

The processed matrices share 408,768 CpGs. Missingness rules, training-only imputation and 500-feature selection are specified in the main text and original-code/methylation_full_geo.py. Sample splits use StratifiedKFold; supplier and chip splits use StratifiedGroupKFold, with five folds, shuffle enabled and seed 2601001. Each common-panel class has at least ten profiles and at least five training profiles in every split. The common panel contains 658 profiles and 23 classes, excluding EMCS. The matched quota for each class is the minimum training count across every scheme and fold. One deterministic subsample per class, scheme and fold is drawn with default_rng(seed plus fold index). Quotas sum to 315 training profiles per fold. There are no repeated subsampling realizations in this report.

The forest uses 200 trees, class_weight=balanced_subsample and fixed random seeds. Full settings and saved folds are in original-code/, original-code/outputs/methylation-full-geo/frozen-folds.tsv, equal-budget-quotas.json and equal-budget-training.tsv. Matching changes feature selection and training composition in addition to class counts. It cannot isolate a sample-number-only effect or a technical batch effect.

The saved paired contrasts use within-profile differences on the same evaluation panel. For each contrast, 1,000 bootstrap draws resample supplier or chip blocks with replacement using seed 2601001; each draw divides its sum of paired loss differences by its total sampled profile count. The 2.5th and 97.5th percentiles are descriptive conditional intervals. There are 26 suppliers or 286 chips. Models are not refitted in this bootstrap; overlapping training sets, alternative splits and unmeasured patient clustering are not resolved by these intervals. Online table 3 exports the already-computed contrasts and intervals unchanged.

## Fusion-compatible annotation subset

The fixed mapping rules are listed in Online table 4. Matching is case insensitive with bounded gene names, optional whitespace around the source colon delimiter, and an explicit fusion annotation. The case-insensitive exclusion patterns are `\bno\s+RNA\b`, `reported`, `unclear`, and `\bno\s+fusion\b`; these are literal text heuristics, not semantic adjudication. Notes matching a pattern are excluded; absent mappings and conflicting class mappings are excluded. The exact original implementation and all 428 inclusion/exclusion rows are preserved. The resulting 120-profile, 12-class subset is fixed for this report, but the inspected history does not establish freezing before prediction inspection. The annotations were author reported and not independently blinded diagnostic adjudication.

The prediction ledger retains source IDs, original annotations and original versus transformed scores. VALIDATION_SAMPLE 262 has a COL1A1::PDGFB-compatible label but an ASPS maximum class with a zero target vote; sharpening raises its maximum score above 0.9. VALIDATION_SAMPLE 405 is the sole EWSR1::NR4A3 annotation and does not permit an EMC sensitivity estimate. Identical numerical cutoffs on different score scales are not interchangeable calibrated probabilities.

## Source reconciliation

The original study reports distinct reference and validation patients. Its 1,077 and 428 unique array IDs have no exact overlap, but no shared public patient key independently verifies patient-level separation. The external metadata contain 986 arrays and no exact match to either original list. Different arrays may still represent the same patient.

The external publication's Supplementary Table S1 flags failed cases 847, 848 and 982; 983 cases remain. Column J has 820 represented and 163 unrepresented diagnoses among retained rows. Column M flags revisions for cases 166, 254, 287, 884, 964 and 965. Original-diagnosis column I is incomplete and is not imputed from final diagnosis. The external Supplementary Table S3 cells D4 and E4 contain literal 821 denominators, conflicting with the 820 supported by S1/main text. This remains unresolved. No extra case, QC threshold, patient independence, or prediction analysis is inferred from this audit. The source-native represented/unrepresented flag is not a mapping to the 12-class fusion subset.

## Reproduction tiers

Online Resource 2 is a self-contained ZIP. Extract it into a task directory, then run `python reproduce.py --out reproduced`. This standard-library command validates input sizes and SHA256 hashes, exports both main tables and four online tables, checks annotation/profile counts, and runs the unchanged fixed-loss reaggregation. It performs no network access, fitting or new bootstrap. Compare reproduced files with the included expected-tables/ outputs. File hashes bind exact saved artifacts; this layer does not reconstruct the original forests.

An optional deeper replay uses original-code/methylation_final_replay.py and methylation_external_metrics.py with the preserved original-code/outputs/ hierarchy. Run this in a scratch copy because the historical scripts overwrite outputs. The four needed files are the parsed primary-workbooks.json, external-reference-and-validation-votes.npz, full-geo/results.json, and per-profile-predictions.tsv for confusion counts. This replay recalculates temperatures and sensitivities from saved votes without training forests. It includes an ancillary live article-XML request after numerical work; README.txt describes an offline wrapper. The original scripts contain historical freeze wording that is not independent timing evidence; the manuscript's explicit timing limitation governs interpretation.

Full forest refitting is a separate tier requiring the original processed GEO matrices and the original feature-selection environment. It was not repeated for this publication-preparation package. Original-code/ contains the code, while the archived run and input_receipt bind the executed inputs. The original workflow installed unpinned dependencies. Its logs show Python 3.12 (patch unknown), NumPy 2.5.3, pandas 3.0.6, SciPy 1.18.1, scikit-learn 1.9.1 and openpyxl 3.1.5. requirements-observed.txt records these observed versions; it is not a complete locked environment or proof of bitwise cross-platform refit reproducibility.

## Artifact preservation and verification limits

Compact prediction and training artifacts were recovered from GitHub Actions artifact 11175775440 of run 36888322221 before its expiry. Its archive SHA256 is 7cd796af836a11010e108c6e0a8003c6e998772c3f0e62c5b03941ed393ab8cd. Recovered files retain their original subdirectories to distinguish the three different results.json files. The grouped inputs were inherited unchanged from run 36881792527. Final external predictions take precedence over that earlier run's superseded external outputs.

The saved external result object's artifacts_sha256 entry for results.json refers to a preexisting file before that script rewrote itself. That historical entry is preserved and is not treated as a checksum for the final result file. The new archive input-manifest.json directly hashes the retained final bytes. The bulky CpG cache index and external feature/refit matrix are omitted; primary measurement repositories remain the source for a full refit. The package does not claim a new external-cohort experiment, independent diagnosis adjudication, or clinical validation.
