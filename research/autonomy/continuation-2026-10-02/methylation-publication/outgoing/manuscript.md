---
id: DOC-METH-PACKAGE-MANUSCRIPT-20261002
title: Interpreting confidence scores in a public sarcoma methylation dataset
level: L3
kind: manuscript
status: live
purpose: Prepare the completed methylation empirical methods study for author and journal review.
scope: Dataset-specific secondary analysis; no publication authorization or readiness claim.
audience: [maintainers, external reviewers]
date: 2026-10-02
last_verified: 2026-10-02
related: []
---

# Interpreting confidence scores in a public sarcoma methylation dataset

Tristan D. McRae

Article type: Original Article

Main text: 2623 words (conservative count including headings, table text and declarations); abstract: 221 words.

Keywords: sarcoma; DNA methylation; validation design; training support; temperature scaling; scoring rules

## Abstract

A sarcoma methylation classifier reports both a predicted tumour class and a score expressing confidence in that prediction. We asked how the training data and the treatment of these scores affect conclusions about performance. Using a separate random-forest model, we reanalyzed 1,077 reference profiles and 428 validation profiles from a public dataset. First, we compared testing on randomly held-out profiles with testing on profiles from suppliers excluded during training. In a common set of 658 profiles, the supplier-related gap in squared probability error fell from 0.0803 to 0.0211 when the number of training profiles per class was matched. Second, we rescaled confidence scores using temperature scaling fitted on reference data. Among 120 validation profiles with reported gene fusions compatible with specific tumour classes, rescaling increased assignments meeting a 0.9 cutoff from 44 to 115 without changing any predicted class. One discordant prediction crossed the cutoff. Average squared probability error improved. However, log loss, which penalizes confident errors, was nearly unchanged overall and worsened when each class received equal weight. Whether log loss improved or worsened also depended on how a zero model score for a fusion-compatible class was handled. These results show how training differences and score summaries can change the apparent performance of a classifier. In this dataset, assigning more cases with high confidence did not establish greater diagnostic reliability.

## Introduction

A methylation classifier gives a pathologist two different pieces of information: a predicted tumour class and a score attached to that prediction. The class identifies the proposed diagnosis. The score can help determine whether the prediction is accepted or requires further investigation. For that reason, a method that assigns more cases with high confidence may appear to offer better diagnostic performance. That interpretation depends on what the scores mean and how they have been evaluated.

Sarcoma methylation classification provides a useful setting in which to examine this problem. The original study released reference data, a tumour taxonomy and a validation series [1]. Later studies examined the classifier's clinical performance [2,3]. We used the released measurements to study a narrower question: how do the training comparison and the way scores are transformed and averaged affect conclusions about performance? Our model was a separate random forest, not the current clinical classifier.

We examined two parts of that question. First, holding out all samples from a supplier changes both the source of the test samples and the training data available to the model. We therefore asked how much of the apparent supplier-related performance gap remained after matching training profiles per class. Second, rescaling scores can move predictions above a confidence cutoff while leaving every predicted class unchanged. We asked whether this increase in confident assignments was accompanied by consistent reductions in prediction error. Together, these comparisons test how much a favorable or unfavorable score summary depends on the choices used to produce it.

## Methods

### Data and model

We used the author-processed methylation matrices and primary reference and validation workbooks for GSE140686 [1]. A profile denotes one array-level methylation measurement. The dataset contained 1,077 reference profiles and 428 validation profiles; the released 450K and EPIC matrices shared 408,768 CpGs.

We treated beta values as missing when detection measurements were absent or detection P exceeded 0.01. All profiles passed the rule excluding those with more than 5% missing common CpGs. Within each training set, we used median imputation and analysis-of-variance selection of 500 CpGs. The model was a 200-tree random forest with balanced subsample weights, implemented in scikit-learn [4,5]. We used this fixed specification throughout. We did not reproduce the original classifier's raw-intensity normalization, probe-exclusion manifest, feature selection or calibration algorithm.

### Comparing test schemes with matched training data

We tested the effect of separating training and test data in three ways: by individual profile, by supplier and by physical chip. Supplier and chip groups came from the deposited metadata. We constructed deterministic fivefold partitions with seed 2601001 and reused them throughout the analysis.

The three schemes were compared on the same 658 reference profiles in 23 classes. Each class had at least ten profiles overall and at least five training profiles in every partition. Extraskeletal myxoid chondrosarcoma (EMC) was absent from this common evaluation set. We first used the original training sets, then repeated the comparison after matching the number of training profiles per class across all schemes and folds. Each class received its smallest available training count, giving 315 training profiles per fold. We drew one deterministic subsample per class for each scheme and fold. The evaluation profiles stayed the same.

### Rescaling confidence scores

For the second analysis, we trained a model on all reference profiles and predicted 65 classes for the 428 validation profiles. Raw scores averaged the class probabilities returned by the individual trees. We then applied temperature scaling, a transformation that changes the concentration of scores while preserving the highest-scoring class within each profile [7]. We counted a profile as assigned when its highest score was at least 0.9. This was a numerical reporting cutoff, not a validated clinical decision rule for our model.

We fitted the temperature using reference predictions from fivefold cross-validation, with each reference profile predicted by a model that had not trained on it. We chose the temperature between 0.05 and 10 that minimized negative log likelihood. No validation labels entered this fitting step. The reference predictions used to fit the temperature were not treated as independent evidence of its benefit.

Zero scores require a convention because the logarithm of zero is undefined. Before calculating log loss, we replaced scores below a small positive floor, epsilon, with that floor and normalized them. We applied temperature scaling in log space without clipping its output probabilities. The principal floor was 10^-6; we also used 10^-4 and 10^-8, fitting the temperature separately at each value. Raw Brier scores and raw threshold assignments used the original scores.

### Comparison labels and measures of error

We compared predictions against two sources of labels. For all 428 validation profiles, we measured agreement with the published classifier's highest-scoring class. This was agreement between algorithms. For 120 profiles in 12 classes, explicit hallmark-fusion annotations supplied a second set of compatible labels. The mapping excluded absent, unclear, historical and taxonomically ambiguous annotations. These were author-reported annotations, not blinded independent diagnostic adjudications. The mapping was fixed for this report, but the inspected records do not establish that it was fixed before predictions were inspected.

We assessed scores using two standard measures of probability error [6]. The multiclass Brier score sums squared errors across classes and then averages them across profiles. Negative log likelihood, or log loss, focuses on the score given to the comparison label and strongly penalizes very small values. Lower values are better for both measures. Neither measure isolates calibration from other aspects of predictive performance.

In the fusion-compatible subset, we calculated each loss in two ways. The profile-weighted mean gives every profile equal weight, so common classes contribute more to the average. The equal-class mean first calculates the mean loss within each class, then gives all 12 classes equal weight. This second calculation was a post hoc sensitivity analysis of saved losses. It did not refit the model or exclude cases.

For the partition comparisons, we used saved paired losses and 1,000 cluster-bootstrap draws over 26 suppliers or 286 chips. We report descriptive 95% percentile intervals. These intervals condition on the fitted models; they exclude model-refitting variability and do not account for unmeasured patient clustering. Full definitions, implementation details and the audit of a separate published cohort are in Online Resource 1. Online Resource 2 contains the frozen results, predictions, code and source-linked tables.

AI assistance was used for analysis-code preparation, evidence organization, manuscript drafting and technical checking. The archived scripts produced the computational results from the identified public measurements. AI assistance does not replace author accountability or independent clinical validation.

## Results

### Matching training data reduced the apparent supplier effect

With the original training sets, testing on profiles from held-out suppliers produced a larger Brier score than testing on individually held-out profiles (Table 1). The supplier-minus-sample difference was 0.0803, with a descriptive interval of 0.0454–0.1162. After matching training profiles per class, this difference fell to 0.0211 (0.0084–0.0367). The corresponding chip-minus-sample difference after matching was 0.0102 (0.0011–0.0193). Agreement with source class labels remained high under all three schemes.

Table 1. Comparison on the same 658 profiles in 23 classes. Agreement is with source class labels. Lower Brier scores indicate smaller squared probability errors, using the class-sum convention. Values are descriptive point estimates. Source: Online Resource 2, expected-tables/table-1.csv and its linked frozen grouped result.

| Training support | Partition | Agreement (%) | Brier score |
|---|---|---:|---:|
| Original | Sample | 97.9 | 0.0973 |
| Original | Supplier | 95.6 | 0.1776 |
| Original | Chip | 97.6 | 0.1031 |
| Matched, 315 per fold | Sample | 97.4 | 0.1223 |
| Matched, 315 per fold | Supplier | 96.8 | 0.1433 |
| Matched, 315 per fold | Chip | 97.7 | 0.1325 |

Thus, much of the supplier-related difference depended on the training comparison. This result applies to the single fixed subsample used here. Matching changed the composition of the training data and the selected features as well as the class counts. It therefore cannot isolate the effect of training sample size alone, and the remaining gap cannot distinguish technical batch effects from biological or referral differences.

Metadata also reflected differences in case mix. A model using supplier, chip and DNA preparation achieved 61.4% agreement under sample partitioning, compared with 9.0% for a model using training-class prevalence. Its agreement fell to 9.4% when suppliers were held out. Supplier, preparation, histology, referral and biological selection remain entangled, so this finding does not establish that technical artifacts caused the methylation predictions.

### Rescaling increased confident assignments without changing predicted classes

The fitted temperature was 0.3115. The transformation left all predicted classes unchanged. Across all 428 validation profiles, our model's predicted class agreed with the published classifier in 358 profiles (83.6%). Before rescaling, 57 profiles met the 0.9 cutoff, all concordant with that algorithm comparator. After rescaling, 311 profiles met it, of which 297 were concordant (95.5%).

The same pattern appeared in the 120 profiles with fusion-compatible annotations. Both our model and the published classifier agreed with the compatible label in 117 profiles (97.5%). Rescaling our scores increased assignments meeting the cutoff from 44 to 115 (Table 2). The additional assignments included one discordant prediction. These counts measure agreement with the available annotations, not independent diagnostic accuracy. Also, a cutoff of 0.9 does not make raw scores, rescaled scores and the published calibrated scores interchangeable.

Table 2. Assignments among 120 profiles with explicit fusion-compatible labels. Each method uses a numerical cutoff of 0.9 on its own score scale. Source: Online Resource 2, expected-tables/table-2.csv and its linked frozen fusion result.

| Scores | Assigned profiles | Assigned concordant | Assigned discordant |
|---|---:|---:|---:|
| Published classifier | 113 | 113 | 0 |
| Separate model, raw scores | 44 | 44 | 0 |
| Separate model, rescaled scores | 115 | 114 | 1 |

The discordant assignment shows what this change means for an individual profile. VALIDATION_SAMPLE 262 carried a COL1A1::PDGFB annotation compatible with dermatofibrosarcoma protuberans. Both algorithms instead predicted alveolar soft part sarcoma (ASPS). Our model's maximum raw score was 0.37; after rescaling, its maximum score was 0.9758. Rescaling made this discordant prediction appear highly confident without changing its class.

### The apparent benefit depended on how errors were averaged

The higher scores improved some summaries but not others. In the fusion-compatible subset, the profile-weighted Brier score fell from 0.1123 to 0.0375. Profile-weighted log loss changed little, from 0.4389 to 0.4359. When every class received equal weight, log loss worsened from 1.0743 to 1.8438, although Brier score still improved, from 0.2365 to 0.1933.

The two averages answer different questions. Four classes contributed 91 of the 120 profiles and therefore dominated the profile-weighted result. Three classes contained only one profile each; equal-class weighting gives these sparse classes much more influence. It changes the class distribution being evaluated rather than correcting the profile-weighted estimate. Neither average establishes performance in a representative clinical population.

The log-loss result also depended on how zero scores were handled. Our model gave a raw score of zero to the fusion-compatible class for VALIDATION_SAMPLE 262. With a floor of 10^-4, profile-weighted log loss improved from 0.4053 to 0.3127 after rescaling. With a floor of 10^-8, it worsened from 0.4772 to 0.5591. The assignment counts and discordances were unchanged. Thus, the direction of the average log-loss change depended on the numerical convention used for this failure.

## Discussion

This reanalysis shows how a classifier can look different when its training comparison or score summary changes. Matching training profiles per class substantially reduced the apparent supplier-related performance gap. Rescaling scores then produced many more high-confidence assignments, but the evidence of lower prediction error depended on the loss measure, class weighting and treatment of zero scores. The class predictions themselves did not change, and one discordant prediction crossed the confidence cutoff.

These findings support two practical reporting choices. Comparisons across data sources should show how much training data each class receives. Without that information, a performance gap can combine changes in the test population with changes in the training data. Reports of confidence scores should also state the score scale and show what happens to individual discordant cases when a cutoff is applied. In our data, the increase from 44 to 115 assignments looked favorable until considered alongside the discordant assignment and the sensitivity of log loss.

The choice of average is part of the scientific question. An average over profiles describes the case mix in the evaluated dataset. An average over classes gives rare and common classes the same weight, even when a rare class has only one observation. Reporting both exposed a limitation that either average alone would have hidden. The result does not determine which weighting will be appropriate for a particular clinical population.

The main limit on interpretation is the quality and independence of the comparison labels. The fusion annotations were selected, author-reported and potentially influenced by diagnostic workup. Molecular testing may have followed morphology or methylation findings. Agreement with these annotations therefore cannot establish diagnostic reliability. The only profile annotated with EWSR1::NR4A3, VALIDATION_SAMPLE 405, was outside the EMC-compatible class for both algorithms and remained below 0.9 after rescaling. One annotated profile cannot estimate EMC sensitivity.

Array identifiers help document the datasets but do not prove patient independence. The original study reports that reference and validation samples came from different patients [1]. Their 1,077 and 428 unique array identifiers do not overlap, but there is no shared public patient key with which to verify that report independently. Removing the one shared physical-chip prefix left 118 fusion-compatible profiles and the same three discordances. A separate audit of E-MTAB-9875 [2] recovered 986 arrays, three QC exclusions and 983 retained arrays, with no exact overlap with either original list. Its source records still disagree between denominators of 820 and 821 for represented diagnoses. Different arrays can come from the same patient, and some external diagnoses were revised after classifier review. That audit therefore does not supply an independent transport test. No predictions were generated for the external cohort; the full reconciliation and its unresolved details are in Online Resource 1.

The contribution is a dataset-specific demonstration of how evaluation choices change conclusions about scores. It does not establish a new sarcoma subtype, technical causation or clinical calibration, and it does not test the current clinical classifier. Temperature scaling preserves class ordering within a profile; it need not preserve every measure of discrimination across profiles. Any subsequent transport study would need a prespecified taxonomy mapping, a policy for diagnoses revised after classifier review, and patient or specimen linkage appropriate to its question.

In this dataset, higher confidence was easier to achieve than consistent evidence of better prediction. Interpreting that confidence required keeping the training comparison explicit and examining how the conclusion changed across error summaries.

## Data availability

The processed methylation matrices are available from GEO accession GSE140686 (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE140686); the primary reference and validation workbooks accompany the original article [1]. External metadata are available under E-MTAB-9875 (https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-9875) and its publication [2]. Online Resource 2 contains the compact predictions, fold and training ledgers, source audits and hash-verified inputs used here. Its standard-library entry point reproduces the tables and loss reaggregation without fitting models. Separate instructions explain how to replay score calculations from saved votes. The original forest computations remain linked to their executed code and source-data hashes; the bulk processed matrices are not redistributed. Code and provenance are maintained at https://github.com/trimcrae/Rare-cancers. Online Resource 1 identifies the exact revisions and limits of reproduction.

## Statements and Declarations

Funding: This research received no funding.

Competing interests: The author declares no competing interests.

Human data and consent: This study reanalyzed publicly released measurements and published annotations. No new patient material was collected and no participants were contacted. This description does not assert an institutional ethics approval, exemption, waiver, or consent determination.

## References

1. Koelsche C, et al (2021) Sarcoma classification by DNA methylation profiling. Nature Communications 12:498. https://doi.org/10.1038/s41467-020-20603-4
2. Lyskjær I, et al (2021) DNA methylation-based profiling of bone and soft tissue tumours: a validation study of the ‘DKFZ Sarcoma Classifier’. Journal of Pathology: Clinical Research 7:350–360. https://doi.org/10.1002/cjp2.215
3. Miettinen M, et al (2024) Assessment of the utility of the sarcoma DNA methylation classifier in surgical pathology. American Journal of Surgical Pathology 48:112–122. https://doi.org/10.1097/PAS.0000000000002138
4. Breiman L (2001) Random Forests. Machine Learning 45:5–32. https://doi.org/10.1023/A:1010933404324
5. Pedregosa F, et al (2011) Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research 12:2825–2830. https://www.jmlr.org/papers/v12/pedregosa11a.html
6. Gneiting T, Raftery AE (2007) Strictly Proper Scoring Rules, Prediction, and Estimation. Journal of the American Statistical Association 102:359–378. https://doi.org/10.1198/016214506000001437
7. Guo C, Pleiss G, Sun Y, Weinberger KQ (2017) On Calibration of Modern Neural Networks. Proceedings of Machine Learning Research 70:1321–1330. https://proceedings.mlr.press/v70/guo17a.html
