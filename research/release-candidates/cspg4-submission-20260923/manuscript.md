---
id: "DOC-CSPG4-CONCISE-20260922-MANUSCRIPT"
title: "CSPG4 RNA across sarcoma types with an expanded comparison of extraskeletal myxoid chondrosarcoma"
level: "L3"
kind: "manuscript"
status: "live"
canonical_for: []
purpose: "Provide the author-requested concise editorial revision of the accepted CSPG4 study."
scope: "Concise study with source-backed discovery rationale and CSPG4 biology and targeting context; accepted scientific results retained."
audience: ["external reviewers", "collaborators", "maintainers"]
date: "2026-09-22"
last_verified: "2026-09-22"
---
# CSPG4 RNA across sarcoma types with an expanded comparison of extraskeletal myxoid chondrosarcoma

**Author.** Tristan D. McRae

Independent researcher, unaffiliated. Correspondence: trimcrae@gmail.com. ORCID: 0000-0002-1823-1451.

**Running title.** Comparative CSPG4 RNA in EMC

## Abstract

**Background:** Extraskeletal myxoid chondrosarcoma (EMC) is a rare soft-tissue sarcoma. Chondroitin sulfate proteoglycan 4 (CSPG4) is a cell-surface protein whose expression has been studied across sarcoma types. This study examined where EMC lies within a broader tissue RNA landscape and whether its differences from named sarcomas recur across datasets.

**Methods:** An exploratory analysis of a curated 11-gene panel compared nine EMC specimens with 393 other specimens from 28 source-defined malignant tumor categories in one RNA-sequencing cohort. All 644 eligible specimens, including other tumor categories, remained in the descriptive atlas. Analysis used an exact rank-sum permutation test with Bonferroni correction for 11 genes, evaluated the array comparisons, and characterized additional public collections separately by source and measurement scale.

**Results:** Median CSPG4 was 54.18 TPM in EMC and 11.87 TPM in the defined malignant reference. The probability of higher EMC expression, allowing half credit for ties, was 0.846; exact two-sided P=0.000130 and adjusted P=0.00143. CSPG4 was higher than low-grade fibromyxoid sarcoma in both RNA sequencing and arrays, with comparison scores of 0.966 and 1.000. Gastrointestinal stromal tumors and dermatofibrosarcoma protuberans had slightly higher medians than EMC in the same RNA-sequencing source. External collections expanded histologic context but supplied no additional explicitly labeled EMC comparison.

**Conclusions:** These data place EMC toward the higher end of CSPG4 RNA expression within a defined sarcoma reference, with substantial overlap and comparator dependence. They support a broader comparative RNA account, without establishing diagnostic specificity, malignant-cell protein expression or therapeutic suitability.

**Keywords.** extraskeletal myxoid chondrosarcoma; CSPG4; sarcoma; RNA sequencing; public data; comparative expression

## Introduction

Extraskeletal myxoid chondrosarcoma (EMC) is a rare soft-tissue sarcoma characteristically associated with NR4A3 rearrangements.[1] Public expression studies contain few EMC specimens, making it difficult to place candidate antigens in the context of other sarcomas.

CSPG4 emerged from an exploratory assessment of 11 candidate therapeutic targets in EMC. Its RNA expression was higher than in three selected sarcoma comparators—myxoid liposarcoma, low-grade fibromyxoid sarcoma (LGFMS) and synovial sarcoma—and the contrast with low-grade fibromyxoid sarcoma recurred in an array collection. These observations motivated a broader question: where does EMC lie within the range of CSPG4 expression across sarcoma types?

CSPG4 encodes a cell-surface proteoglycan, also known as NG2, with an established role in experimental cancer biology. In melanoma cells, CSPG4 enhances integrin-dependent cell spreading and activation of focal adhesion kinase (FAK) and ERK1/2 signaling.[2] Boudin and colleagues described heterogeneous CSPG4 expression and associations with prognosis and immune features across soft-tissue sarcomas.[3] This provides a biological context for examining the small EMC groups available in public RNA-sequencing and array collections.[4,5]

The present study places EMC within a source atlas of 60 diagnosis labels, spanning malignant, intermediate and benign soft-tissue tumors and related contexts. Broad sarcoma references and contrasts shared across assays establish the comparative framework; additional public collections describe the wider CSPG4 landscape.

## Methods

The 11 genes—CD276, SSTR2, PRAME, FAP, CD248, CSPG4, MSLN, L1CAM, GPC3, ALPP and CDH17—were a manually curated working list of candidate therapeutic targets. The list combined cell-surface antigens, stromal targets and the intracellular peptide–HLA candidate PRAME. It was a hypothesis-driven subset, rather than the top 11 genes from a genome-wide screen. All 11 were measured and retained. The initial myxoid liposarcoma, LGFMS and synovial sarcoma comparisons were investigator-selected for morphological and diagnostic relevance; the broader analysis included every category meeting the criteria below. Supplementary Information gives panel provenance and the original prioritization rule.

The Hofvander collection provides gene-level transcripts per million (TPM), original diagnoses and specimen metadata.[4] A consistent primary-lesion definition excluded specimens flagged as recurrent or metastatic across all histologies. This removed one local recurrence from the 13 source EMC specimens. Three further EMC patients were identified in the historical array cohort through published case identifiers and excluded to reduce overlap between assays, leaving nine. Sensitivity analyses included all 12 source-primary EMCs and then all 13 source EMCs, including the local recurrence, against the same references. The supplement identifies each exclusion and its evidence. Among the retained nine, source records specify seven NR4A3 fusions, one FUS::NR4A2 fusion and one fusion-positive case without a crosswalked fusion identity (Table S6); membership follows the source diagnosis.

The retained atlas contains 644 specimens across 60 original diagnosis labels. The primary reference uses all 393 non-EMC specimens from 28 categories classified as Malignant by the source, excluding melanoma, a non-sarcoma context, and unclassified spindle-cell tumors, which lack a specific histologic identity. A broader reference includes all 96 eligible specimens from nine source-classified Intermediate categories, giving 489 references across 37 labels. These are source behavior labels: gastrointestinal stromal tumor (GIST), dermatofibrosarcoma protuberans (DFSP) and solitary fibrous tumor (SFT) fall in the Intermediate category in this dataset. The broader analysis tests how this classification boundary affects the EMC comparison. All other eligible categories remain in the descriptive atlas.
GSE24369 provides six EMC biopsies, 17 LGFMS, six myxofibrosarcomas (MFS), six desmoids, five SFT and two pooled muscle RNAs.[5] Array analysis retained the released GPL6244 robust multi-array average log2 signals and CSPG4 transcript cluster 7990545. Lesion stage was not established. LGFMS, MFS, desmoid and SFT were compared because they are the tumor groups shared with the RNA-sequencing collection. Comparisons used each dataset’s own measurement scale.

The source search examined public sarcoma compendia, their original accessions and identifiable EMC-containing studies. Records required a usable CSPG4 measurement and traceable diagnosis. Each collection retained its source-specific measurement scale: Treehouse Tumor Compendium 25.01 log2(TPM+1), Boudin et al. published normalized log2 values, GSE213065 Salmon TPM, GSE234092 featureCounts-derived counts per million (CPM), and OpenPedCan v15 gene TPM.[3,6,7,8,9] The supplement lists unresolved or inaccessible EMC sources.

Selection used diagnosis and identity metadata. Within each resource, donor identifiers, specimen aliases and explicit patient IDs guided retention of one eligible profile per supported identity. Known reuse across Treehouse, Boudin and OpenPedCan was removed; unresolved identities remain qualified in the supplied ledgers. Library-method and original-study strata were retained. Counts describe profiles within resources, not a globally unique patient cohort.

Expression summaries included medians, quartiles and ranges. The comparison score A averages every EMC–reference specimen pair, assigning 1 when EMC expression is higher, 0.5 when equal and 0 when lower; A=0.5 denotes neutral ordering. The primary estimate weights reference specimens equally. Sensitivity analyses averaged the category-specific scores to give each reference category equal weight and examined deletion of individual EMC specimens.

The primary test used the exact rank-sum distribution for every allocation of nine EMC labels among 402 observations. Equal expression values received their average rank and remained separate observations in the permutation distribution. Its two-sided tail includes sums at least as far from the null expectation as the observed sum. This tests an exchangeable-label, common-distribution null for the observational groups. Bonferroni correction covers the retained 11 genes. Approximate 95% percentile bootstrap intervals for both references used 50,000 independent resamples of specimens within each group at its original size, seed 20260921, with linear-interpolation quantiles.[10]

The broader reference and the 12- and 13-specimen EMC sensitivities were summarized descriptively. External summaries and pairwise A values were calculated within designated source strata. Cross-source descriptive ranges included only within-source contrasts with at least five profiles per diagnosis in each contributing stratum. Code, source digests, selection ledgers and complete results accompany the data archive.

OpenAI Codex (OpenAI; GPT-6-family models identified in retained execution records) assisted with source organization, analysis-code implementation, computation and verification. Exact model versions were not retained for every session. Data visualizations were generated programmatically from the reported measurements and estimates using reproducible Python code supplied with the data archive.

## Results

Median CSPG4 was 54.18 TPM in the nine EMC specimens, with an interquartile range of 41.41–63.98 and a range of 10.14–207.08 TPM. The primary reference median was 11.87 TPM. The specimen-weighted A was 0.846 (approximate 95% bootstrap interval 0.709–0.958), with exact two-sided P=0.000130435 and Bonferroni-11 P=0.00143479. Equal weighting of reference categories gave A=0.866. Deleting any one EMC specimen left A between 0.828 and 0.894. Including all 12 primary EMCs gave a median of 51.21 TPM and A=0.808 and 0.785 against the primary and broader references, respectively. Including the local recurrence (all 13 EMCs) gave a median of 48.92 TPM and corresponding scores of 0.809 and 0.784.

EMC had the highest observed median among the 29 labels in the primary comparison, although distributions overlapped and several groups were small (Figure 1). GIST (n=14) and DFSP (n=10), both source-classified Intermediate, had slightly higher medians of 59.24 and 59.10 TPM. Adding all eligible Intermediate categories gave a reference median of 13.20 TPM and A=0.824 (approximate 95% interval 0.678–0.943); equal-category A was 0.848. Several benign categories also had high values (Figure S1). Table S3 supplies every eligible diagnosis label.

MSLN also had higher ordering against the primary reference (A=0.811; adjusted P=0.00406), while several panel genes had lower ordering. Table S2 reports all 11 genes. The original three-comparator panel results and historical sensitivity analyses are supplied in the supplement.

CSPG4 was higher in EMC than LGFMS in both the six-EMC versus 17-LGFMS array comparison (A=1.000) and the nine-EMC versus 13-LGFMS RNA-sequencing comparison (A=0.966; Figure 2). Deleting any one EMC or LGFMS array biopsy retained A=1.000. Array scores against MFS, SFT and desmoid were also 1.000; corresponding RNA-sequencing scores were 0.854, 0.879 and 1.000. DFSP supplied a contrary RNA-sequencing comparison (A=0.467).

The external characterization retained 1,334 Treehouse profiles, 986 Boudin records, 54 GSE213065 profiles, 69 GSE234092 records and 28 OpenPedCan clinical-context profiles. These supplied 304 source-by-diagnosis summaries and 1,480 within-source comparisons, but no additional explicitly labeled EMC group.

Some relative patterns recurred across sources (Figure S2). MFS was lower than leiomyosarcoma (LMS) in all six strata with at least five profiles per group, with A=P(MFS>LMS)+0.5P(tie) ranging from 0.182 to 0.246. Undifferentiated pleomorphic sarcoma was lower than LMS in all five supported strata (A=0.077–0.414). Other comparisons varied: dedifferentiated liposarcoma had A=0.173–0.343 against LMS in four strata but 0.517 in the Nakayama cohort. GIST had A=0.836 against LMS in GSE234092 and 0.502 in Treehouse-processed SRP057793. The complete tables retain each comparison's source, scale and specimen counts.

## Discussion

EMC lay toward the higher end of CSPG4 RNA expression in both the primary malignant reference and the broader reference including intermediate tumors. Four named contrasts recurred across RNA sequencing and arrays. The slightly higher medians in GIST and DFSP show that elevated CSPG4 RNA extends across distinct mesenchymal tumor types. These groups provide useful comparators for subsequent EMC tissue studies, while the high values in some benign categories make cellular localization particularly important. Similar bulk expression does not establish a shared biological driver.

CSPG4 is already being investigated as a therapeutic target. A CSPG4-directed antibody inhibited breast-cancer cell growth in culture and reduced experimental lung metastases in mice.[11] In sarcoma models, cytokine-induced killer cells carrying a CSPG4-directed chimeric antigen receptor (CAR) showed activity in culture and in xenografts of leiomyosarcoma, undifferentiated pleomorphic sarcoma and fibrosarcoma.[12] A CSPG4-directed CAR-T approach has also entered phase I testing in recurrent or refractory head-and-neck squamous-cell carcinoma (NCT06096038), with safety and tolerability as the primary objective.[13] These studies place the EMC expression finding within an existing experimental targeting field, without establishing a treatment for EMC.

The contribution here is the explicit placement of EMC within the wider CSPG4 RNA distribution. The additional collections show both recurring and divergent relationships among other sarcomas, consistent with the heterogeneity reported by Boudin et al.[3] They supplied no further explicitly labeled EMC group, leaving independent replication of the EMC comparison unresolved.

The small EMC group remains the main limit on precision, reflected in the wide bootstrap intervals. Including the three overlapping primary cases attenuated the comparison; adding the local recurrence had little further effect on the comparison scores. Small comparison groups also make median rankings uncertain. The references reflect source classifications and sampling rather than population incidence or a comprehensive clinical taxonomy. Equal-category estimates change the weights but retain this dependence. This is an exploratory analysis of a curated gene panel. Gene selection and unmeasured confounding remain outside the 11-test correction and approximate bootstrap intervals.

Incomplete specimen identities, clinical histories and historical overlap further limit interpretation. Applicability across sex and gender groups was not evaluated. Assays and collections differ in quantification, library construction, disease stage and tissue composition, so cross-source measurements were kept separate. Uniform computational processing alone does not make them directly comparable. The known shared patients were excluded from the nine-case comparison, but incomplete array identifiers leave further historical overlap unresolved. The bounded source search and unresolved collections are documented in the supplement.

Finally, bulk RNA measures contributions from malignant and nonmalignant cells. Purity estimates were unavailable for all nine EMC specimens, and normal tissues were not matched to tumors. These data leave malignant-cell localization, accessible CSPG4 protein and normal-tissue sparing unresolved. Expression ordering alone cannot establish a diagnostic threshold, therapeutic window or treatment benefit. The next step is to establish CSPG4 protein abundance and cellular localization in EMC, including its accessibility on malignant cells. That would connect the RNA finding to the biological and targeting questions already being studied in other cancers.


## Data code and declarations


**Data availability.** The original Hofvander data are available through https://doi.org/10.5281/zenodo.17866629. Original array data and annotations are available as GEO GSE24369 (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE24369) and GPL6244 (https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL6244). Additional inputs are Treehouse Tumor Compendium 25.01, Boudin et al. Supplementary Table S8, GEO GSE213065 and GSE234092, and OpenPedCan v15. The data and code package, including exact source URLs, selection ledgers, digests and specimen values, is available at https://github.com/trimcrae/Rare-cancers/blob/30fa69b2f0c4fce74bc39b9e13edc6fcffaf25c2/research/release-candidates/cspg4-concise-20260922/journal-package/CSPG4-data-code.zip. Source-specific attribution and reuse terms continue to apply.

**Research scope.** This study reanalyzes public data and includes no newly collected participant specimens or intervention.

**CRediT authorship contribution statement.** Tristan D. McRae: Project administration, Supervision. The author is responsible for the final interpretation and manuscript.

**Funding.** This research received no funding.

**Competing interests.** No competing financial interests exist. One non-financial interest is declared: the author is a survivor of extraskeletal myxoid chondrosarcoma, the disease this work addresses.

**Declaration of generative AI and AI-assisted technologies in the manuscript preparation process.** OpenAI Codex assisted with source organization, code implementation, computation, verification and drafting. The author takes responsibility for the article. Data visualizations were generated programmatically from the supplied measurements and estimates with AI-assisted code; no primary experimental image was generated or altered.

## References

[1] Dulken BW, Kingsley L, Zdravkovic S, Cespedes O, Qian X, Suster DI, et al. CHRNA6 RNA In Situ Hybridization Is a Useful Tool for the Diagnosis of Extraskeletal Myxoid Chondrosarcoma. Mod Pathol. 2024;37:100464. https://doi.org/10.1016/j.modpat.2024.100464.

[2] Yang J, Price MA, Neudauer CL, Wilson C, Ferrone S, Xia H, et al. Melanoma chondroitin sulfate proteoglycan enhances FAK and ERK activation by distinct mechanisms. J Cell Biol. 2004;165:881–91. https://doi.org/10.1083/jcb.200403174.

[3] Boudin L, de Nonneville A, Finetti P, Mescam L, Le Cesne A, Italiano A, et al. CSPG4 expression in soft tissue sarcomas is associated with poor prognosis and low cytotoxic immune response. J Transl Med. 2022;20:464. https://doi.org/10.1186/s12967-022-03679-y.

[4] Hofvander J, Köster J, Sydow S, Piccinelli P, Vult von Steyern F, Tsagkozis P, et al. Transcriptomic Subgroups in Soft Tissue Tumors Correlate with Morphologic Subtype, Genomic Features, and Outcome. Clin Cancer Res. 2026;32:1825–34. https://doi.org/10.1158/1078-0432.CCR-25-3740.

[5] Möller E, Hornick JL, Magnusson L, Veerla S, Domanski HA, Mertens F. FUS-CREB3L2/L1-positive sarcomas show a specific gene expression profile with upregulation of CD24 and FOXL1. Clin Cancer Res. 2011;17:2646–56. https://doi.org/10.1158/1078-0432.CCR-11-0145.

[6] Beale HC, Learned K, Kephart ET, Lyle AG, van den Bout A, McCabe M, et al. Consistently processed RNA sequencing data from 50 sources enriched for pediatric data. Sci Data. 2025;12:1134. https://doi.org/10.1038/s41597-025-05376-z.

[7] Subramanian A, Nemat-Gorgani N, Ellis-Caleo TJ, van IJzendoorn DGP, Sears TJ, Somani A, et al. Sarcoma microenvironment cell states and ecosystems are associated with prognosis and predict response to immunotherapy. Nat Cancer. 2024;5:642–58. https://doi.org/10.1038/s43018-024-00743-y.

[8] Seligson ND, Asmann YW, Almerey T, Zayas YC, Edgar MA, Attia S, et al. Molecular markers of proliferation, DNA repair, and immune infiltration defines high-risk subset of resectable retroperitoneal sarcomas. Surg Oncol. 2024;56:102125. https://doi.org/10.1016/j.suronc.2024.102125.

[9] Geng Z, Wafula E, Corbett RJ, Zhang Y, Jin R, Gaonkar KS, et al. The Open Pediatric Cancer Project. GigaScience. 2025;14:giaf093. https://doi.org/10.1093/gigascience/giaf093.

[10] Efron B. Better bootstrap confidence intervals. J Am Stat Assoc. 1987;82:171–85. https://doi.org/10.1080/01621459.1987.10478410.

[11] Wang X, Osada T, Wang Y, Yu L, Sakakura K, Katayama A, et al. CSPG4 protein as a new target for the antibody-based immunotherapy of triple-negative breast cancer. J Natl Cancer Inst. 2010;102:1496–512. https://doi.org/10.1093/jnci/djq343.

[12] Leuci V, Donini C, Grignani G, Rotolo R, Mesiano G, Fiorino E, et al. CSPG4-Specific CAR.CIK Lymphocytes as a Novel Therapy for the Treatment of Multiple Soft-Tissue Sarcoma Histotypes. Clin Cancer Res. 2020;26:6321–34. https://doi.org/10.1158/1078-0432.CCR-20-0357.

[13] National Cancer Institute. iC9-CAR.CSPG4 T-Cells for the Treatment of Patients with Recurrent or Refractory Head and Neck Squamous Cell Carcinoma. NCT06096038; NCI-2024-01228. https://www.cancer.gov/research/participate/clinical-trials-search/v?id=NCI-2024-01228. Accessed 23 September 2026.

## Figure legends

**Figure 1. CSPG4 RNA across sarcoma and related tumor categories.** The 498 specimens span 38 source diagnosis labels: nine EMC, 393 primary-reference specimens and 96 additional specimens marked by asterisks. Asterisks identify categories classified as Intermediate in the source; all other non-EMC rows form the Malignant-category reference. The broader reference includes both sets. Dots show specimens, horizontal segments interquartile ranges and vertical marks medians. The axis uses log2(1+TPM) spacing with TPM labels; categories are ordered by observed median. Other eligible contexts appear in Figure S1. MIFS/HFLT, myxoinflammatory fibroblastic sarcoma/hemosiderotic fibrolipomatous tumor; NOS, not otherwise specified.

**Figure 2. Direct EMC comparisons shared across two assays.** Points show A=P(EMC>comparator)+0.5P(tie) for the four diagnosis groups measured in both Hofvander RNA sequencing and GSE24369 arrays. The table supplies specimen counts and scores. Each score is calculated within its source. LGFMS, low-grade fibromyxoid sarcoma; MFS, myxofibrosarcoma; SFT, solitary fibrous tumor.
