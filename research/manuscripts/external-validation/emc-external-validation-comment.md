---
id: DOC-EMC-EXTERNAL-VALIDATION-COMMENT
title: "External evidence for an EMC prognostic gene panel: cohort identity and baseline comparability"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: Assess whether the published external analyses substantiate their stated validation claims.
scope: Scientific comment based on original public source records and the reported statistical transformation; no new expression or survival analysis.
audience: [external reviewers, collaborators]
date: "2026-09-07"
last_verified: "2026-09-07"
---

# External evidence for an EMC prognostic gene panel: cohort identity and baseline comparability

**Author.** Tristan D. McRae

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [0000-0002-1823-1451](https://orcid.org/0000-0002-1823-1451)

**Article type.** Scientific comment

**Running title.** External evidence for an EMC gene panel

## Abstract

A recent extraskeletal myxoid chondrosarcoma (EMC) study proposed a three-gene prognostic panel and used external expression cohorts to support lineage specificity and cross-platform baseline comparability. We examined the original article, supplementary Figure S6 and the cited public cohort records. GSE6481 contains 105 soft-tissue tumor arrays with no deposited EMC diagnosis, whereas the article describes 19 EMC and 128 cartilaginous comparators. The figure separately labels 19 and 59 samples beneath a total of 147. These discrepancies leave the underlying lineage comparison unidentified; an accession or labeling error remains possible. Separately, within-cohort gene standardization removes location and scale differences before the cross-platform comparison. Non-significant tests of those standardized distributions cannot establish the original baseline comparability. Exact analysis inputs and a narrower interpretation are needed to make the external evidence reproducible and informative.

**Keywords.** extraskeletal myxoid chondrosarcoma; external validation; reproducibility; cohort identity; gene expression; standardization

## The claim requiring clarification

Chaiboonchoe and colleagues proposed a PXN, H1FX and TYMS expression panel from a retrospective EMC cohort of 12 patients.[1] Their report explicitly acknowledges severe overfitting, including an optimism-corrected concordance index of 0.10. It also explains why the external datasets do not provide meaningful prognostic validation. Those limitations are already part of the published account.

The external analyses make two additional claims: that H1FX expression distinguishes EMC from cartilaginous tumors, and that normalized expression confirms baseline comparability across sequencing platforms. These concern different properties from prediction of survival. We examined whether the public sources and stated methods support those particular interpretations. This comment does not evaluate a new prognostic model or infer treatment effects.

## The cited cohort does not identify the reported lineage comparison

The article describes GSE6481 as 19 EMC tumors compared with 128 other cartilaginous tumors or chondrosarcomas. It reports higher H1FX expression in EMC, with log2 fold change 0.64 and P = 0.001, and uses this result to support lineage specificity.[1] However, the original GEO series is a study of soft-tissue tumor classification with 105 arrays.[2]

We parsed every sample record in the official GSE6481 family SOFT release and independently checked agreement with its series roster. The 105 unique GEO sample identifiers comprise 16 synovial sarcomas, 19 myxoid liposarcomas, three lipomas, three well-differentiated liposarcomas, 15 dedifferentiated liposarcomas, 15 myxofibrosarcomas, six leiomyosarcomas, three malignant peripheral nerve sheath tumors, four fibrosarcomas and 21 malignant fibrous histiocytomas. No deposited sample is annotated as EMC or another chondrosarcoma. The original dataset publication describes the same 105-tumor cohort.[3]

There is also an internal inconsistency in the reported sample counts. Figure S6B is headed GSE6481 with n = 147, but each of its three comparisons labels EMC with n = 19 and the comparator group with n = 59. Those group labels sum to 78. The article text instead gives 128 comparators. We inspected the original supplementary image; we did not digitize plotted values or treat visible points as a patient roster.

These observations establish a problem with identifying and reproducing the reported comparison. They do not establish which data were actually analyzed. In particular, the occurrence of 19 myxoid liposarcomas in the cited deposit is not evidence that these were analyzed as EMC. A mistaken accession, an incorrect figure label or a different undocumented selection could explain part of the discrepancy. The underlying expression estimates cannot be adjudicated without the actual accession, sample identifiers, group assignments and analysis inputs.

The other GEO cohort also needs a precise description. GSE24369 contains six EMC arrays, 34 arrays from other lesions and two pooled skeletal-muscle RNA references.[4] The article describes the complement of the six EMC arrays as 36 other soft-tissue sarcomas. That description does not match the full deposited complement. This observation alone does not demonstrate a material change in any expression contrast; it identifies another reason to provide the exact sample selection.

## Separate standardization cannot validate the baseline it removes

For the sequencing comparison, the article describes 12 internal TempO-Seq profiles and six external MI-ONCOSEQ profiles, the latter from Davis and colleagues.[1,5] The gene values were transformed to z-scores within each dataset before a two-sided Mann-Whitney comparison. Figure S6C reports P-values of 0.963 for PXN, 0.888 for H1FX and 1 for TYMS. The article interprets these results as confirmation that normalization bridges the platforms and validates baseline comparability.

If, as the wording and Figure S6C suggest, each nonconstant gene was centered and scaled across samples separately within each cohort, the transformation is:

`z_C(x_i) = (x_i - mean_C(x)) / s_C(x)`.

If every value in that cohort is replaced by `a*x_i + b`, with `a > 0`, its mean becomes `a*mean_C(x) + b` and its standard deviation becomes `a*s_C(x)`. Consequently:

`z_C(a*x_i + b) = z_C(x_i)`.

Separate standardization therefore gives identical analyzed values after arbitrary cohort-specific location shifts or positive rescaling. A comparison of those values cannot identify the baseline differences that were removed. The invariance holds with either population or sample standard deviations, provided the same convention is used before and after transformation. Under this interpretation, the limitation follows algebraically without the external expression matrix.

Standardization does not force the distribution shapes to agree or force a Mann-Whitney P-value of 1. A rank comparison can still detect differences in the standardized distributions. However, failure to reject such a difference is not an equivalence assessment, and no equivalence margin is specified for the claimed baseline agreement. Moreover, the two datasets contain different patients, so their contrast combines biological and technical differences. Neither agreement nor disagreement can be attributed to platform alone.

The reported result can be described as an absence of detected differences between separately standardized distributions in these small cohorts. It cannot establish agreement of the original expression baselines, analytical interchangeability of the assays or transportability of a prognostic score. This limitation does not demonstrate that the platforms are discordant; it limits what this particular comparison can show.

## A reproducible and proportionate interpretation

Expression detection, association with histology, analytical comparability and prognostic performance each require evidence suited to that claim. The original authors appropriately limit their survival-model interpretation. Similar care is needed for the external expression evidence: the cited public accession does not currently identify the reported EMC lineage comparison, while the stated standardization cannot validate removed baseline differences.

The smallest useful clarification is the accession and version actually used for Figure S6B, the sample identifiers and diagnosis assignments for both GEO comparisons, and the gene or probe mapping and expression table underlying S6A-C. The analysis script should identify the normalization steps and the reference distribution used for each z-score. Those inputs would permit a direct reproduction and show whether correcting the cohort description changes the lineage-specificity result.

If baseline comparability is an intended claim, its definition and acceptable difference should be specified before testing it. Shared reference materials or specimens measured on both platforms could address technical agreement more directly; a study comparing different patient cohorts addresses a different question. Prognostic transportability would additionally require independent outcomes and evaluation of the fixed model. None of these measurements is supplied by the present audit.

This is an article-specific comment based on the public record as inspected on 7 September 2026. It is not a systematic audit of EMC biomarker studies. The original supplementary packet contains internal-cohort expression data but no external sample-by-gene table or analysis script for S6A-C. Their absence from that packet does not establish that the inputs are unavailable elsewhere. An author clarification could resolve the accession and count discrepancies; separate within-cohort standardization would still require the narrower interpretation described above.

## Data and code availability

The accompanying verification supplement provides source URLs and SHA256 hashes, scripts to retrieve and check the original public records, and deposited sample identifiers and diagnosis counts. Third-party source files are retrieved separately under their existing terms. The original datasets remain available through GEO.[2,4] No new patient data, gene-expression estimates or survival outcomes were generated. The algebraic argument is stated in full above.

## Declarations

**Funding.** No external funding was received for this work.

**Competing interests.** The author declares no competing interests.

**Ethics.** This work examines published material and public repository metadata; no new participants were recruited.

**Author contributions.** Tristan D. McRae directed the research and takes responsibility for the manuscript.

**AI assistance.** OpenAI Codex assisted with source retrieval, metadata parsing, drafting and computational checks. AI-generated assessments do not constitute experimental validation or independent human peer review.

## References

1. Chaiboonchoe A, Chanthercrob J, Sakamula R, et al. Prognostic biomarkers for enhanced risk stratification in extraskeletal myxoid chondrosarcoma: a retrospective cohort study. *PeerJ*. 2026;14:e21497. [doi:10.7717/peerj.21497](https://doi.org/10.7717/peerj.21497).
2. NCBI Gene Expression Omnibus. GSE6481: Gene Expression Analysis of Soft Tissue Sarcomas: Characterization & Reclassification of Malignant Fibrous Histiocytoma. [Series record](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE6481). Original family SOFT release inspected 7 September 2026.
3. Nakayama R, Nemoto T, Takahashi H, et al. Gene expression analysis of soft tissue sarcomas: characterization and reclassification of malignant fibrous histiocytoma. *Modern Pathology*. 2007;20:749-759. [PubMed record](https://pubmed.ncbi.nlm.nih.gov/17464315/).
4. NCBI Gene Expression Omnibus. GSE24369: Gene expression profiling of low-grade fibromyxoid sarcoma (LGFMS). [Series record](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE24369). Original family SOFT release inspected 7 September 2026.
5. Davis EJ, Wu YM, Robinson D, et al. Next generation sequencing of extraskeletal myxoid chondrosarcoma. *Oncotarget*. 2017;8:21770-21777. [doi:10.18632/oncotarget.15568](https://doi.org/10.18632/oncotarget.15568).
