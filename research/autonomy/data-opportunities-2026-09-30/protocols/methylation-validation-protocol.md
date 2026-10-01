# Validation across suppliers and array chips in public sarcoma methylation data

**Completed metadata feasibility audit and prospective classifier protocol. Classifier results pending.**

## Abstract

Public sarcoma methylation profiles permit analysis without new tissue experiments, but small classes may have insufficient representation across suppliers or physical array chips for some validation designs. We audited metadata for 1,077 reference profiles assigned to 65 methylation classes. Thirty-one classes contained at most ten profiles. Eleven of these classes came from one supplier label; thirteen had more than half their profiles on one chip. Extraskeletal myxoid chondrosarcoma (EMC) contained ten primary formalin-fixed paraffin-embedded specimens, eight from Jena Pathology and six on one chip.

An exploratory requirement of at least three held-out and five retained profiles per class allowed a supplier holdout for three small classes and a chip holdout for eleven. EMC supported neither. These are feasibility findings, not evidence of technical confounding or poor classifier performance. We propose discrimination, calibration and abstention comparisons wherever class support permits, with training-contained preprocessing and independent validation.

## Background and completed analysis

Koelsche et al. developed a random forest using 1,077 reference profiles: 62 tumour methylation classes and three non-neoplastic control classes.[1] The study used threefold cross-validation and nested threefold calibration, and separately evaluated 428 additional tumours. Of these, 322 reached a calibrated score of at least 0.9. That is not322 independently verified correct diagnoses: the original report distinguishes concordant, discrepant, revised and unresolved diagnoses. This protocol does not allege absence of external validation.

The proposed question is whether performance and calibration transfer across supplier or physical-chip groups where the class distribution supports that comparison. Supplier and chip associations could reflect technical differences, specimen selection or biological case mix. They do not identify a causal mechanism.

The primary Supplementary Data 1 workbook was downloaded on1 October 2026, SHA256 85a148285ef1812d6ca8d68c839a2d64f73cebb6f8ebfa95844e3d85b5c03bb9. It contains 1,077 nonempty reference records. We compared it with the public qtran1/MeQTrack_app CSV at revision 578bb615e0e89858ffb02cbe1da87680c74a01ba, Git blob 3dd8b13a4c30d7ef06e5a933633a3e0da670efc1.[3] All1,077 IDs and IDAT, supplier, material, manifestation and site fields match. Thirty-seven class-name formatting differences are confined to “Ewings sarcoma” versus “Ewing´s sarcoma”; EMC fields agree and class counts are unchanged. Formatted batch dates and rounded purity values were not compared for exact equivalence. The [audit](../analysis/methylation_feasibility.mjs) and [results](../results/methylation-feasibility.json) retain the reconciliation scope.

A small class means at most ten reference profiles, not low population incidence. Supplier labels include named pathology services and research projects; they do not uniformly denote independent hospitals. Chip identity is inferred from the IDAT basename prefix. A physical chip is not asserted to be a biological batch. The separate Batch field remains under its source name.

| Quantity | Completed finding |
|---|---:|
| Reference profiles / classes | 1,077 /65 |
| Classes with at most ten profiles |31 |
| Small classes supplied by one label |11 |
| Small classes with more than half on one chip |13 |
| Small classes with any eligible supplier holdout |3/31 |
| Small classes with any eligible chip holdout |11/31 |
| Small classes with every represented supplier/chip holdout eligible |0/31 |
| Missing Batch / Manifestation / Site values |64 /56 /88 |

Holdout eligibility requires at least three test and five training profiles of the class. These are exploratory planning thresholds, not guarantees of statistical power or calibration precision. EMC has supplier counts8/1/1 and chip counts6/2/1/1. Holding out its dominant supplier leaves two training profiles; holding out its largest chip leaves four. Smaller held-out groups contain fewer than three test profiles. All ten EMC specimens are primary FFPE. No supplier or chip holdout meets the illustrative rule.

## Prospective analysis

### Access and identity

Reconcile GEO sample records, primary identifiers and the mirror through an explicit mapping table.[2] Preserve histological diagnosis and methylation class as distinct fields. Verify paired red/green IDAT availability, accession mapping, size and checksums for every included profile. Missing files and unresolved mappings remain in an exclusion ledger. This audit did not import IDATs, perform array QC or fit a classifier.

Check the original 428-case validation cohort separately for raw data, provenance and adequate diagnostic reference metadata. Public metadata alone do not establish access to every raw profile or adjudicated diagnosis. Retain the original report's statement that its reference and validation specimens came from different patients, while checking the downloaded mapping for consistency.

### QC and preprocessing

Apply prespecified detection-failure, signal-intensity and control-probe criteria without selecting exclusions from prediction results. Document array type, sample-identity consistency and each exclusion. Verify the common450K/EPIC probe set and exclusions for sex chromosomes, ambiguous mapping and relevant polymorphisms. The published 428,230 retained probes are a reproduction target, not an assumed current-manifest count.

Distinguish sample-wise operations from parameters estimated across samples. Learn across-sample normalization, scaling, imputation and probe selection within training partitions and apply them to held-out profiles. Keep feature ranking, model tuning and calibration inside the applicable training folds. Do not estimate corrections from combined training/test profiles. A correction that uses held-out profiles is a separately labelled transductive analysis.

### Validation support and comparisons

Freeze specimen/group assignments, class panels and eligible evaluations from metadata before fitting. Compare sample-stratified validation with supplier-separated and chip-separated validation as separate questions. Keep any patient-linked specimens together. Match evaluation label panels and, where possible, out-of-fold test-profile sets. Report training size and class composition, and use a training-size sensitivity analysis where feasible.

Unavailable estimates are distinct from errors. A class absent from training cannot receive an ordinary closed-set performance estimate. A class lacking test support cannot receive the planned class-level estimate. Neither should be turned into a misclassification or silently removed from coverage denominators.

Do not select folds because they yield a large performance difference. Use deterministic, metadata-defined selection and record amendments before examining results. Pooling folds with changing label panels requires an explicit estimand and weighting rule. The present metadata rule does not support an EMC supplier/chip comparison; additional independent EMC profiles would be required.

Nested group validation must also support calibration. If an outer training partition cannot support its inner calibration, mark that panel's calibrated analysis infeasible. Report any prespecified uncalibrated discrimination separately rather than silently substituting another design.

### Model and outcomes

Follow the published random-forest approach and class-balancing rationale, with multinomial ridge calibration.[1] The original model used10,000 trees and10,000 CpGs selected by variable importance. Estimate importance within training partitions. Fit calibration from predictions produced by classifiers that did not train on the scored profiles; select its penalty within training data. Declare any reduced-tree approximation before evaluation.

The primary prospective calibration endpoint is multiclass Brier score within each fixed supported panel. Report macro-averaged recall, class-level sensitivity and confusion matrices for discrimination. Give each metric's profile, class and group counts. At the published 0.9 threshold, report assignment coverage, errors among assigned profiles and abstention by class. A score reaching0.9 is not automatically a correct diagnosis.

Define published class families before fitting and report them separately from individual classes. Do not introduce family aggregation after observing errors.

### Controls, uncertainty and external evaluation

Use a provenance-only predictor of class as a diagnostic control. Its variables may include supplier, chip and material; use Batch only after establishing its meaning. Anatomical site is not purely technical. Good provenance-only prediction demonstrates association between class and metadata; it does not prove that methylation predictions depend on an artefact.

For paired validation comparisons, resample held-out groups jointly with both prediction sets. Use cluster bootstrap intervals where group support permits; otherwise disclose support and sensitivity directly. Declare any class-level exploratory test family and apply false-discovery-rate correction. Do not search across fold definitions or thresholds for significance.

Keep the original 428-case cohort outside training, feature selection, tuning and calibration. If accessible, its evaluation reproduces a previously published validation and should be labelled accordingly. Institutional diagnosis, methylation class and molecularly adjudicated diagnosis are different reference standards. A diagnostic revision informed by the tested classifier may involve incorporation bias; unresolved discrepancies remain unresolved.

A stronger extension would use a non-overlapping cohort whose diagnoses were established independently of the tested classifier. The public reference set alone cannot establish prospective clinical performance.

### Execution and stopping

Begin with a small CPU pilot spanning array types and supplier labels. Measure runtime, memory and storage before projecting a full run. Budget limits are prospective planning constraints, not measured requirements or an authorization to spend on external services. Stop and document measured requirements if a faithful analysis cannot fit the available allocation; declare any reduced scope before using outcomes.

Also stop when raw mappings remain ambiguous, QC leaves no useful supported panel, nested calibration is infeasible, or the intended independent evaluation cannot be assembled. Insufficient support is a legitimate feasibility outcome, not a reason to force all 65 classes through one model.

## Interpretation and readiness

The completed audit documents support constraints, especially for EMC. It supplies no new accuracy, calibration, batch-effect or degradation result. Metadata concentration alone is an internal feasibility finding. A future methods manuscript requires an executed analysis and a consequential result beyond existing sarcoma classifiers and Mepylome's classification/copy-number functions.[4] Novelty and venue suitability remain unverified.

## References

1. Koelsche C, et al. Sarcoma classification by DNA methylation profiling. Nature Communications.2021;12:498. [DOI 10.1038/s41467-020-20603-4](https://doi.org/10.1038/s41467-020-20603-4). [PMC7819999](https://pmc.ncbi.nlm.nih.gov/articles/PMC7819999/).
2. NCBI GEO. [GSE140686](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE140686).
3. [Pinned metadata mirror](https://github.com/qtran1/MeQTrack_app/blob/578bb615e0e89858ffb02cbe1da87680c74a01ba/reference/GSE140686_sarcoma_methylation_labels.csv).
4. Mepylome publication.2025. [DOI 10.1002/aisy.202500778](https://doi.org/10.1002/aisy.202500778).
5. [Primary retrieval run 36797786226](https://github.com/trimcrae/Rare-cancers/actions/runs/36797786226), job 110165087206; hashes in the [source receipt](../results/source-retrieval-receipt.json).
