---
id: "DOC-DATA-OPPORTUNITIES-2026-09-30-DRAFTS-SARCOMA-ANTIGEN-PROTEIN-TRANSFER-SHORT-REPORT"
title: "Quantification support and sarcoma transfer of RNA-based antigen protein estimates"
level: "L3"
kind: "manuscript"
status: "live"
canonical_for: []
purpose: "Working research draft: Quantification support and sarcoma transfer of RNA-based antigen protein estimates."
scope: "September 30 measured-data campaign; retain the source qualifications, execution boundaries and historical status stated in the body."
audience: ["maintainers","external reviewers"]
date: "2026-09-30"
last_verified: "unverified"
_backfilled: "true"
---

# Quantification support and sarcoma transfer of RNA-based antigen protein estimates

## Abstract

Public proteomic atlases can test whether RNA measurements provide useful estimates of antigen protein abundance in sarcoma. We evaluated a fixed 11-gene panel using published ProCan–DepMapSanger measurements, with 717 non-sarcoma development models and 61 sarcoma models representing 61 biological families. Development-only selection compared cognate-RNA linear regression with a ridge model using the panel's available RNA features. In 11 eligible gene–histology strata, the selected models reduced normalized mean absolute error by 26.49% relative to a development-median baseline, but had higher error than cognate-RNA regression alone: 0.4919 versus 0.4741. Only CD276, CSPG4 and L1CAM met primary evaluation criteria. Their quantified coverage depended strongly on the protein matrix: 35, 33 and 29 of 61 families in the 6,692-protein matrix, increasing to 53, 52 and 47 in the 8,498-protein matrix. Identical-model comparisons showed close agreement between these matrices, while newly quantified subsets had weaker or negative RNA–protein rank associations. Cross-assay common subsets were too small to establish assay disagreement. This analysis qualifies antigen-specific transfer and measurement support; it provides no direct evidence of cell-surface accessibility, efficacy or EMC-specific biology.

## Introduction

A pan-cancer proteomic atlas provides an opportunity to examine hypotheses using experiments that have already been performed. However, a useful RNA–protein association across many cancers does not establish that an antigen can be estimated reliably in a particular sarcoma lineage. Measurement support, calibration and the composition of the evaluated models may each affect that translation.

The original ProCan study already examined RNA–protein relationships, integrated drug response and CRISPR measurements, and developed predictive models of cancer vulnerabilities [1]. Our contribution is consequently narrower: a fixed sarcoma antigen-panel analysis with development restricted to non-sarcoma models, explicit quantification denominators, and comparisons on identical biological models. We also evaluated whether broader target–outcome benchmarks supported a consistent advantage for protein abundance. These analyses concern published whole-cell measurements, rather than the accessibility or function of an antigen at the cell surface.

## Methods

We used the released 6,692-protein ProCan matrix, its model mapping, and author-processed RNA measurements in the corresponding multi-omics archive [2]. The released RNA centering intercept was restored; archival processing remained part of the source data. This was not a reprocessing of raw RNA counts or raw mass-spectrometry signals. Model identity was reconciled using patient identifiers, parent models, Broad identifiers and normalized names. Related models formed transitive families. Families containing sarcoma models were withheld from development, and unresolved EMC-labelled or conflicting-lineage identities were excluded from the primary analysis.

The primary evaluation comprised 717 development models and 61 sarcoma models representing 61 biological families. The latter represented 23 Ewing sarcoma, 11 osteosarcoma, 11 other sarcomas, seven rhabdomyosarcoma, five chondrosarcoma and four leiomyosarcoma families. No independently verified EMC model was available in this matched proteomic evaluation. H-EMC-SS was retained in the identity audit, rather than treated as molecularly confirmed EMC.

The panel was CD276, SSTR2, PRAME, FAP, CD248, CSPG4, MSLN, L1CAM, GPC3, ALPP and CDH17. CHRNA6 was a specified RNA-marker control, but lacked the measurements required for evaluation. Protein non-quantification remained missing; it was never converted to zero. A primary gene evaluation required at least 50 development observations and five matched test families. Primary aggregation additionally required five measured families in each gene–histology stratum.

For each supported gene, development-only nested cross-validation grouped models by cancer type. It selected between cognate-RNA linear regression and ridge regression using the available panel RNA features. Ridge penalties were 0.01, 0.1, 1, 10 and 100. Newly fitted imputation and scaling were contained within development folds. Test errors were divided by the development protein interquartile range. The primary statistic weighted eligible gene–histology strata equally, rather than allowing the largest lineage to dominate. We used 1,000 histology-stratified family bootstrap draws and 1,000 within-lineage protein permutations. These quantify uncertainty conditional on the fitted models and observed measurement support; they do not include training or between-laboratory uncertainty.

We separately examined the less filtered 8,498-protein matrix and the Broad protein measurements in the released archive. Source accessions, matrix orientation, model identities and file hashes were checked. Comparisons used matched families and preserved quantification missingness. The three-antigen overlap analysis was descriptive and did not refit or select the primary prediction models.

A bounded secondary analysis evaluated 305 specified target–outcome pairs using released drug-response and CRISPR measurements. Drug identifiers retained the GDSC version, and higher log IC50 indicated greater resistance. Associations were examined before and after within-histology centering and adjustment for the released measured-growth covariate. Its primary source defines growth using day-one untreated and day-four DMSO control signals, but the mapping from that ratio to the exported numerical scale remains unverified. We therefore used the released values without an inferred transformation. Growth was observed for 708 of 717 development models and all 61 primary models. Association analyses used complete cases; predictive imputation remained confined to development. Adjusted residual-rank associations and their nominal P values are descriptive; the P values do not incorporate nuisance-fitting uncertainty.

## Results

Only CD276, CSPG4 and L1CAM met primary gene criteria. In the frozen 6,692-protein matrix, their quantified coverage was 57.38%, 54.10% and 47.54%, respectively. FAP had six matched test observations but only 20 development observations and remained descriptive. Other panel genes either lacked a quantified protein feature or had insufficient development or test support. These restrictions describe the available measurements, rather than biological absence of the corresponding antigens.

The primary analysis contained 11 eligible strata, spanning the three genes and five histologies. Selected-model normalized mean absolute error was 0.491887, compared with 0.669106 for the development-median baseline. Relative improvement was 26.486%, with a conditional bootstrap interval of 16.970%–35.235%; all 1,000 bootstrap draws retained the fixed strata. The within-lineage permutation P value was 0.000999. Cognate-RNA regression nevertheless had lower aggregate error, 0.474078. Thus, development selection did not improve on the simpler predictor in held-out sarcoma.

Individual selected-model improvements over the median baseline were 23.27% for CD276, 12.48% for CSPG4 and 33.23% for L1CAM. Observed RNA–protein Spearman correlations were 0.651, 0.605 and 0.667. Calibration slopes were 1.205, 0.551 and 1.267. CSPG4 illustrates why error, ordering and calibration should be reported separately: the selected ridge predictor had a protein rank correlation of 0.241, despite a 0.605 correlation between observed cognate RNA and protein. Its positive baseline-relative error improvement therefore did not imply superior ranking or calibrated abundance.

Coverage increased substantially in the 8,498-protein matrix: CD276 was quantified in 53/61 families, CSPG4 in 52/61 and L1CAM in 47/61. All three exceeded a 70% coverage benchmark under this alternative support definition. RNA-paired counts were 53, 51 and 46. Descriptive single-RNA transfers on this matrix improved on their development-median baselines by 24.50%, 1.93% and 9.04%, respectively. These are a separate support sensitivity, rather than a replacement of the frozen primary analysis.

An identical-model comparison separated quantification support from changing model composition. The two ProCan matrices agreed closely on common quantified families: CD276 n=35, rho=0.907; CSPG4 n=33, rho=0.956; L1CAM n=29, rho=0.999. RNA–8,498-protein associations were positive among families quantified in the original matrix: rho=0.716, 0.666 and 0.670. In additionally quantified RNA-paired families, the corresponding correlations were 0.216, −0.304 and −0.483, with n=18, 18 and 17. These are quantification-selected subsets; the contrasts do not identify a causal effect of filtering or an individual processing step.

Only five, six and four families, respectively, had RNA, both ProCan protein measurements and Broad protein measurements. On these common subsets, 6,692-protein ProCan–Broad correlations were 0.000, −0.257 and 0.200; corresponding 8,498-protein correlations were 0.300, −0.257 and 0.200. The small overlaps and wide conditional intervals preclude a conclusion that either assay failed. The two ProCan matrices are also measurements from the same project, rather than independent replication.

Of 305 secondary target–outcome pairs, 218 could be evaluated: 154 met primary support criteria and 64 were descriptive; 87 remained unsupported. Across 195 unadjusted association tests, four RNA and four protein associations had Benjamini–Hochberg q<0.05. After histology and measured-growth adjustment, one RNA association and no protein association met that threshold across 154 available tests. The surviving EGFR–AST-1306 RNA association was positive (rho=0.617, q=0.0337), indicating higher released log IC50, rather than increased sensitivity. Median predictive improvement of protein over RNA across the 154 primary pairs was −0.0257%. This bounded benchmark did not demonstrate a consistent protein advantage; it cannot establish equivalence across the full proteome.

## Discussion

The practical finding is that antigen estimates depend on both the prediction task and the measurements admitted to evaluation. A simpler RNA predictor transferred at least as well as development-selected multivariable models in the primary aggregate. Wider quantification support increased coverage, but did not preserve the RNA–protein relationship uniformly among the added observations. Reporting a single correlation or the fraction of antigens represented in a matrix would conceal these distinctions.

This result extends an established public resource through a specific sarcoma transfer analysis. It does not rediscover the original atlas's broader ability to connect RNA, proteins and cancer vulnerabilities. Whole-cell abundance also cannot establish membrane localization, epitope accessibility, normal-tissue safety, target dependence or response to an antigen-directed intervention. Cell lines omit stromal and immune compartments, and the matched proteomic cohort contains no verified EMC model. The CSPG4 results therefore qualify this computational estimation task without testing an EMC-specific biological claim.

The source matrices contain global archival preprocessing, and the analysis conditions on proteins that were quantified. These limitations constrain prospective performance claims. Within that scope, the reusable contribution is an explicit set of family identities, coverage denominators, fixed test strata and calibration results that allows antigen evidence to be assessed gene by gene.

## Data availability

Source files are publicly released through Figshare article 19345397 and its associated publication. Essential numerical results are preserved in the repository: [matched RNA/protein measurements](../deep-analysis/results/protein-RNA-final-matched-measurements.json), [drug/CRISPR benchmark](../deep-analysis/results/protein-drug-CRISPR-final-actual.json), [less-filtered and Broad assay sensitivity](../deep-analysis/results/protein-less-filtered-and-Broad-assays-actual.json), and [three-antigen same-model assay overlaps](../deep-analysis/results/protein-three-antigens-assay-overlap-final.json). Workflow artifacts are temporary supplements. Source hashes and model reconciliation accompany the results.

## References

1. Gonçalves, Poulos, Cai, et al. Pan-cancer proteomic map of 949 human cell lines. 2022. [PMCID: PMC9387775](https://pmc.ncbi.nlm.nih.gov/articles/PMC9387775/).
2. ProCan–DepMapSanger public data release. Figshare article 19345397, version 1. https://api.figshare.com/v2/articles/19345397
