---
id: DOC-METH-PACKAGE-MANUSCRIPT-20261002
title: Training support and score weighting alter conclusions in a public sarcoma methylation reanalysis
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

# Training support and score weighting alter conclusions in a public sarcoma methylation reanalysis


Tristan D. McRae

Article type: Original Article

Main text: 2021 words (conservative count including table text and declarations); abstract: 172 words.

Keywords: sarcoma; DNA methylation; validation design; training support; temperature scaling; scoring rules

## Abstract

Methylation classifiers can retain their predicted classes while changing the scores used to accept those predictions. We reanalyzed released sarcoma methylation measurements to examine how training support and score weighting affect apparent robustness. A fixed random forest used 1,077 reference profiles and 428 validation profiles from GSE140686. In a common 658-profile, 23-class panel, the supplier-minus-sample difference in multiclass Brier score fell from 0.0803 to 0.0211 when class-specific training budgets were equalized. A reference-fitted temperature transformation left maximum-score classes unchanged. In 120 validation profiles with explicit hallmark-fusion annotations, it increased assignments at a numerical 0.9 threshold from 44 to 115, including one discordant assignment. Profile-weighted negative log likelihood changed from 0.4389 to 0.4359, whereas equal-class weighting changed it from 1.0743 to 1.8438. The direction of profile-weighted log-loss change also depended on the input floor for a zero-vote case. These results show how training support, score scale and case weighting affect conclusions from this completed dataset. They do not establish clinical calibration, an extraskeletal myxoid chondrosarcoma (EMC) diagnostic sensitivity, or a new biological subtype.

## Introduction

Public sarcoma methylation measurements permit empirical study of validation design without collecting new tissue. The original classifier defined a reference taxonomy and evaluated diagnostic use in a validation series [1]. Separate studies subsequently examined its clinical performance [2,3]. Those studies already establish that external validation is necessary; repeating that observation is not the contribution of this reanalysis.

We asked whether two apparent improvements withstand changes in what is held constant. First, does a supplier-versus-sample validation difference persist when training support is matched? Second, does reference-fitted score sharpening improve validation summaries consistently across loss functions, case weighting and rare discordant profiles? We used a separate fixed model in the original taxonomy. This is a diagnostic-methods reanalysis of measured data, not an evaluation of the current clinical classifier or a discovery study of sarcoma biology.

## Methods

We used both author-processed GSE140686 matrices and primary reference and validation workbooks [1]. The matrices shared 408,768 CpGs across the released 450K and EPIC files. We treated beta values as missing when detection measurements were absent or detection P exceeded 0.01. All 1,077 reference and 428 validation profiles passed the rule excluding profiles with more than 5% missing common CpGs. Median imputation and analysis-of-variance selection of 500 CpGs used training data only. The model was a fixed 200-tree random forest with balanced subsample weights, implemented in scikit-learn [4,5]. We did not reproduce the original raw-intensity normalization, probe-exclusion manifest, feature selection or calibration algorithm.

We used deterministic fivefold sample, supplier and physical-chip partitions constructed from metadata with seed 2601001 and reused unchanged for the full analysis. Their common evaluation panel contained 658 reference profiles in 23 classes. Each class had at least ten profiles and at least five training profiles in every partition. The EMC class was absent from this panel. We repeated the comparison with class-specific training quotas shared across partitions, totaling 315 training profiles per fold. Each class quota was its minimum available training count across all partitions and folds; one deterministic within-class subsample was drawn for each partition and fold. Evaluation profiles remained fixed.

We report class-label agreement and multiclass Brier score, defined as the mean across profiles of the sum of squared probability errors across classes [6]. Paired differences use saved per-profile losses. Descriptive 95% percentile intervals used 1,000 cluster-bootstrap draws over 26 suppliers or 286 chips. These intervals condition on the fitted models; they exclude model-refitting variability and do not address unmeasured patient clustering.

A separate all-reference model predicted 65 classes in the 428 validation profiles. We used temperature scaling [7], fitting a temperature by minimizing reference fivefold out-of-fold negative log likelihood over temperatures from 0.05 to 10, refitting it separately for each epsilon. For log losses, we floored input votes at epsilon, normalized them, and applied the temperature in log space without clipping output probabilities. The principal epsilon was 10^-6, with sensitivities at 10^-4 and 10^-8. Raw Brier scores and threshold assignments used original votes. Temperature fitting was reference-only; its fitting targets were not presented as an independent validation set.

The validation analysis used two distinct comparators. The published classifier's maximum-score class provided an algorithm comparator for all 428 profiles. A frozen mapping of explicit hallmark-fusion annotations supplied compatible labels for 120 profiles in 12 classes. The annotation-based rules excluded absent, unclear, historical and taxonomically ambiguous annotations. The inspected records do not establish that the mapping was frozen before predictions were inspected. These author-reported annotations were not blinded independent adjudication. The equal-class sensitivity was post hoc: it averaged the 12 saved class-specific mean losses without refitting or excluding cases.

AI assistance was used for analysis-code preparation, evidence organization, manuscript drafting, and technical checking. Computational results were produced by the archived scripts on the identified public measurements. AI-generated text and technical checks do not substitute for author accountability or independent clinical validation. Detailed implementation, software records, and reproducibility instructions are provided in Online Resource 1; frozen inputs, predictions, code, and machine-readable tables are provided in Online Resource 2.

## Results

### Matched training support reduced the supplier validation difference

Class agreement remained high across partitions, but Brier scores were more sensitive to partition design (Table 1). With the original training sizes, the supplier-minus-sample Brier difference was 0.0803 (descriptive interval 0.0454–0.1162). After matching class-specific training budgets, it was 0.0211 (0.0084–0.0367). The matched chip-minus-sample difference was 0.0102 (0.0011–0.0193). Thus the supplier comparison depended substantially on training support in this fixed subsampling realization. Matching changed training composition and feature selection as well as class counts; it does not isolate an effect of sample number alone. The remaining difference cannot isolate a technical batch effect from biological or referral differences.

Table 1. Fixed evaluation panel: 658 profiles in 23 classes. Agreement is with source class labels; Brier score uses the class-sum convention. Values are descriptive point estimates. Source: Online Resource 2, expected-tables/table-1.csv and its linked frozen grouped result.

| Training support | Partition | Agreement (%) | Brier score |
|---|---|---:|---:|
| Original | Sample | 97.9 | 0.0973 |
| Original | Supplier | 95.6 | 0.1776 |
| Original | Chip | 97.6 | 0.1031 |
| Matched, 315 per fold | Sample | 97.4 | 0.1223 |
| Matched, 315 per fold | Supplier | 96.8 | 0.1433 |
| Matched, 315 per fold | Chip | 97.7 | 0.1325 |

Source annotations themselves predicted case mix. A model using supplier, chip and DNA preparation achieved 61.4% agreement under sample partitioning, compared with 9.0% for training-class prevalence. Its agreement fell to 9.4% when suppliers were held out. Supplier, preparation, histology, referral and biological selection remain entangled; these results do not establish that technical artifacts caused methylation predictions.

### Score sharpening increased threshold coverage without changing predicted classes

The fitted temperature was 0.3115. Across all 428 validation profiles, our maximum-vote class agreed with the published classifier's maximum-score class in 358 profiles (83.6%). At a numerical threshold of 0.9, raw votes assigned 57 profiles, all concordant with that algorithm comparator. Transformed scores assigned 311 profiles, of which 297 were concordant (95.5%). No maximum-score class changed. The same numerical threshold does not make raw votes, transformed scores and the published calibrated scores interchangeable.

In the fusion-compatible subset, both algorithms agreed with the compatible label in 117 of 120 profiles (97.5%). Their threshold behavior differed (Table 2). The transformation increased assignments from 44 to 115 and included one discordant prediction. These are concordance and assignment counts, not independent diagnostic-accuracy estimates.

Table 2. Threshold assignments among 120 profiles with explicit fusion-compatible labels. Each method uses a numerical threshold of 0.9 on its own score scale. Source: Online Resource 2, expected-tables/table-2.csv and its linked frozen fusion result.

| Scores | Assigned profiles | Assigned concordant | Assigned discordant |
|---|---:|---:|---:|
| Published classifier | 113 | 113 | 0 |
| Separate model, raw votes | 44 | 44 | 0 |
| Separate model, transformed | 115 | 114 | 1 |

### Aggregate loss improvement depended on weighting and the zero-vote convention

Profile-weighted Brier score fell from 0.1123 to 0.0375 after transformation. Profile-weighted negative log likelihood changed little, from 0.4389 to 0.4359. Equal-class weighting instead increased negative log likelihood from 1.0743 to 1.8438, while reducing Brier score from 0.2365 to 0.1933. Four classes supplied 91 of the 120 profiles, and three classes had one profile each. Equal-class weighting changes the target distribution and gives sparse classes substantial influence; it does not correct the profile-weighted estimate.

One profile had zero raw votes for its fusion-compatible class. At epsilon = 10^-4, profile-weighted negative log likelihood fell from 0.4053 to 0.3127. At 10^-8, it rose from 0.4772 to 0.5591. Assignment coverage and discordance were unchanged. The direction of the log-loss comparison therefore depended on how a zero-vote failure was represented.

The underlying exception was VALIDATION_SAMPLE 262, annotated with COL1A1::PDGFB and a compatible dermatofibrosarcoma protuberans label. Both algorithms predicted alveolar soft part sarcoma (ASPS). Our raw maximum vote was 0.37; its transformed maximum score was 0.9758. The transformation sharpened a discordant prediction into an above-threshold assignment. VALIDATION_SAMPLE 405, the only profile with an EWSR1::NR4A3 annotation, was outside the EMC-compatible class for both algorithms and remained below 0.9 after transformation. One annotated profile cannot estimate EMC sensitivity. Molecular workup may have followed morphology or methylation findings, further limiting the interpretation of fusion concordance.

### Source identity is partly resolved; separate-cohort transport remains unmeasured

The original authors report that reference and validation samples came from different patients [1]. The primary workbooks contain 1,077 unique reference and 428 unique validation array identifiers with no exact overlap. They lack a shared patient key for independent patient-level verification. Removing the one shared physical-chip prefix retained 118 fusion-compatible profiles and the same three discordances in the completed sensitivity analysis.

A separate metadata audit found no exact array matches between either original list and the 986 arrays deposited as E-MTAB-9875 [2]. The external study's Supplementary Table S1 identifies three failed cases, 847, 848 and 982, leaving 983 retained cases. Its source-native flags identify 820 represented diagnoses and 163 unrepresented diagnoses. Six cases carry explicit diagnostic-revision flags: 166, 254, 287, 884, 964 and 965. The source describes review of discrepant results, so final diagnoses cannot be assumed independent of classifier output.

This audit resolves exclusion identities without establishing separate-cohort performance. The external study's Supplementary Table S3 cells D4 and E4 contain literal core denominators of 821, whereas its Supplementary Table S1 and main text support 820. That discrepancy remains unexplained. The inspected sources do not identify the case-specific failed QC metric or threshold. Distinct array identifiers also cannot exclude different-array specimens from a shared patient. We have not fit or evaluated predictions in E-MTAB-9875 for this report, and its source-native membership flags are not a mapping into our 12-class subset.

## Discussion

This completed reanalysis identifies two ways a favorable aggregate result can become narrower when its comparison is made explicit. Matching training support reduced the supplier-validation loss difference. Reference-only score sharpening greatly increased threshold assignments, but its log-loss benefit was not stable across case weighting or zero-vote conventions. The measured contribution is the joint demonstration of these effects in a fixed public dataset, including the case that crossed the threshold while remaining discordant.

The findings support reporting training support, score definitions, class support and individual high-confidence exceptions alongside aggregate losses. They do not establish a new sarcoma subtype, a methylation mechanism, technical causation, clinical calibration, or superiority to a current classifier. Brier score and log loss summarize more than calibration alone. Temperature preserves within-profile class ordering; we do not infer that every measure of discrimination across profiles is unchanged.

The main limitation is the reference standard, not an unresolved array match. The original study reports distinct patients, and the available identifiers support array-level separation. Nonetheless, the validation series remains a secondary reanalysis of the original study, its molecular annotations are selected and potentially affected by diagnostic workup, and some classes have only one annotated profile. A separately specified transport study would require a frozen taxonomy mapping, a policy for diagnoses revised after classifier review, and appropriate patient/specimen linkage. Recovering an eligibility ledger does not satisfy those requirements.

## Data availability

The author-processed methylation matrices are available from GEO accession GSE140686 (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE140686), with the primary reference and validation workbooks in the original article [1]. External source metadata are available under E-MTAB-9875 (https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-9875) and its publication [2]. No external-cohort predictions were generated here. Online Resource 2 preserves the compact predictions, fold and training ledgers, source audits, and hash-verified result inputs used in this report. It includes a standard-library table and loss-reaggregation entry point, with separate instructions for replaying score calculations from the saved votes. Original forest computations remain anchored to their executed code and source-data hashes; their bulk processed matrices are not redistributed in the supplement. Code and provenance are maintained at https://github.com/trimcrae/Rare-cancers. Online Resource 1 identifies the exact analysis revisions and reproducibility scope.

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

