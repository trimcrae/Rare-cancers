---
id: "DOC-CSPG4-PRESUBMISSION-20260921-MANUSCRIPT"
title: "CSPG4 RNA across sarcoma types with an expanded comparison of extraskeletal myxoid chondrosarcoma"
level: "L3"
kind: "manuscript"
status: "live"
canonical_for: []
purpose: "Document the independently reviewed CSPG4 author-review paper and its supporting preparation."
scope: "Exploratory descriptive RNA analysis and current author-review materials; source qualifications and all adverse findings retained. No journal submission or author certification."
audience: ["external reviewers", "collaborators", "maintainers"]
date: "2026-09-21"
last_verified: "2026-09-21"
---
# CSPG4 RNA across sarcoma types with an expanded comparison of extraskeletal myxoid chondrosarcoma

**Author.** Tristan D. McRae

Independent researcher, unaffiliated. Correspondence: trimcrae@gmail.com. ORCID: 0000-0002-1823-1451.

**Running title.** Comparative CSPG4 RNA in EMC

## Abstract

**Background:** Extraskeletal myxoid chondrosarcoma (EMC) is a rare soft-tissue sarcoma. Chondroitin sulfate proteoglycan 4 (CSPG4) is a cell-surface protein studied across sarcoma types. We examined where EMC lies within a broader tissue RNA landscape and whether named contrasts recur across datasets.

**Methods:** An exploratory extension of a fixed 11-gene analysis compared nine EMC specimens with 393 specimens from 28 source-defined malignant categories. All 644 eligible specimens remained in the descriptive atlas. We used an exact rank-sum test with 11-gene Bonferroni correction, specimen bootstrap intervals, and a sensitivity including source-classified intermediate tumors. Array comparisons and additional public collections were analyzed separately by source and scale.

**Results:** Median CSPG4 was 54.18 TPM in EMC and 11.87 TPM in the defined reference. The probability of higher EMC expression, allowing half credit for ties, was 0.846 (approximate 95% interval 0.709–0.958); adjusted P=0.00143. Including intermediate tumors gave 489 references and a score of 0.824 (0.678–0.943). Scores against low-grade fibromyxoid sarcoma were 0.966 in RNA sequencing and 1.000 in arrays. Gastrointestinal stromal tumors (GIST) and dermatofibrosarcoma protuberans had slightly higher medians than EMC. External collections supplied no additional explicitly labeled EMC group.

**Conclusions:** EMC lies toward the higher end of CSPG4 RNA expression within the defined references, with substantial uncertainty, overlap and comparator dependence. These findings support a broader comparative RNA account, without establishing diagnostic specificity, malignant-cell protein expression or therapeutic suitability.

**Keywords.** extraskeletal myxoid chondrosarcoma; CSPG4; sarcoma; RNA sequencing; public data; comparative expression

## Introduction

Extraskeletal myxoid chondrosarcoma (EMC) is a rare soft-tissue sarcoma characteristically associated with NR4A3 rearrangements.[1] Individual public expression studies contain few EMC specimens. Comparing those specimens with a small set of other sarcomas can reveal a reproducible difference, but leaves a broader question unanswered: is the observed RNA expression unusual across the available sarcoma landscape, or mainly unusual relative to the chosen comparison types?

CSPG4 encodes a cell-surface proteoglycan already studied in sarcoma. Boudin and colleagues described its expression and clinical and immune associations in a large collection of soft-tissue sarcomas.[2] The remaining question is how the uncommon EMC specimens compare with the wider range of available tumor types. We address this through a same-source reference, named contrasts shared across assays, and external histologic context.

RNA abundance also needs to be distinguished from other kinds of evidence. Bulk tissue includes malignant cells and nonmalignant components; a tissue RNA measurement does not identify the cells producing the signal or establish cell-surface protein density. CHRNA6 illustrates that distinction. Dulken et al. identified CHRNA6 using GSE24369 and subsequently demonstrated strong, diffuse RNA staining in 25 EMC cases by chromogenic in situ hybridization.[1] That work established an RNA tissue assay, not a protein-targeting result. Here, CHRNA6 remains a separate, previously supported RNA-marker control.

An earlier fixed-panel analysis compared nine EMC specimens with myxoid liposarcoma (MLPS), low-grade fibromyxoid sarcoma (LGFMS) and synovial sarcoma in a public RNA-sequencing cohort, and retained same-histology comparisons in an array cohort.[3,4,5] The present exploratory extension expands the same-source reference to all eligible source-defined malignant categories and describes additional public sarcoma collections. The unstratified defined-reference comparison is the leading analysis. Sequencing year is not treated as an established biological exposure or technical effect.

## Methods

### Study design and direct EMC comparisons

We retained the original 11-gene panel, specimen exclusions and array-probe mappings.[4,6] The panel comprised CD276, SSTR2, PRAME, FAP, CD248, CSPG4, MSLN, L1CAM, GPC3, ALPP and CDH17. CHRNA6 was analyzed separately. The earlier panel and operational selection rule were frozen before inspecting the new cohort's target values; this was not public preregistration. The broader reference and external characterization reported here were documented on 19 September 2026 after earlier results were known. They are exploratory extensions, not prospectively independent discovery analyses. A dated 21 September amendment specified bootstrap intervals and one broader reference sensitivity before their computation, in response to a pre-submission review; these additions are also exploratory.

The Hofvander release contains gene-level transcripts per million (TPM) for 704 source patients, original diagnoses and clinical specimen metadata.[3] Its reported processing used STAR 2.7.10b with GRCh38 and RSEM 1.3.3 with Ensembl 104. We used the original Table S1 diagnoses rather than replacing them with expression-informed revisions. The existing policy excluded specimens with a nonblank recurrence or metastasis flag and preserved specified exclusions for previously reported EMC cases. Nine of 13 EMC specimens remained: three explicitly overlapping historical cases and one local recurrence were excluded. A blank prior-publication field does not establish complete independence from every historical series. All nine retained EMC diagnoses were fusion-positive in source Table S1. Filtered Table S3 specified an NR4A3 fusion for seven, an RT-PCR-verified FUS::NR4A2 fusion for one, and no filtered transcript for the remaining specimen. We retained the source diagnoses rather than asserting uniform NR4A3 confirmation (Table S6).

Applying the retained specimen policy across the source yielded 644 eligible specimens spanning 60 original diagnosis labels. This is a count of retained labels, not a claim to enumerate 60 distinct diseases or every sarcoma type. The source article reports 56 tumor types under its own classification. The inferential reference contained 393 non-EMC specimens across 28 categories classified as Malignant in the original source, excluding melanoma and the unclassified spindle-cell category. All other eligible specimens remained visible in the atlas. This reference follows the source taxonomy; in particular, its Intermediate category includes GIST and dermatofibrosarcoma protuberans (DFSP). These tumors were not omitted from the descriptive results because of their expression values. The broader sensitivity adds all eligible Intermediate-category specimens, retaining the exclusions of EMC, melanoma and unclassified spindle-cell tumors. It contains 489 references across 37 labels; it is not a comprehensive clinical sarcoma taxonomy.

GSE24369 supplied 42 original GPL6244 array records: six EMC biopsies, 17 LGFMS, six myxofibrosarcomas (MFS), six desmoids, five solitary fibrous tumors (SFT) and two pooled skeletal-muscle RNAs.[5] Lesion stage was not established, so these biopsies were not assumed to be primary tumors. The two muscle pools were not counted as two individual healthy controls. We retained released robust multi-array average (RMA) log2 signals and the original, uniquely assigned transcript cluster for each gene; CSPG4 used probe 7990545. The same-histology contrasts were calculated within each dataset, without pooling TPM and array signals.

### Broader public-source characterization

We examined large public sarcoma compendia, their original accessions and identifiable EMC-containing studies. The search was a bounded source-recovery exercise completed on 19 September 2026, not a systematic review or evidence that every possible public dataset had been exhausted. Eligibility required a usable CSPG4 measurement and a traceable specimen-to-diagnosis mapping. Identified inaccessible or unresolved sources remain in the availability table. The external data contributed expression context; none of the selected external records had an explicit EMC diagnosis.

Treehouse Tumor Compendium 25.01 provided consistently processed gene-symbol log2(TPM+1) values and source metadata.[7] We used the human tumor PolyA and ribosomal-depletion collections, excluding cell-line and xenograft compendia. An explicit diagnosis map included sarcoma and related mesenchymal categories, with benign or intermediate context separated. Gliosarcoma and uterine carcinosarcoma were excluded. We selected one profile per source-supplied donor identifier where available, otherwise conservatively grouped repeated Treehouse specimen prefixes. PolyA was preferred, followed by lexicographic specimen identifier, without consulting CSPG4 values.

The initial 1,446 Treehouse candidate profiles reduced to 1,335 selected identity groups after metadata review. Eleven NCI donors occurred in two projects; original ENA experiment aliases confirmed the reuse. One donor had conflicting Ewing and CIC-associated diagnoses and was excluded from histology summaries, leaving 1,334 profiles. Of these, 860 had source-supplied donor keys and 474 relied on unverified specimen-prefix grouping. Source-supplied identifiers themselves were not universally independently established patient identities. Analyses were stratified by library method, source and study accession; a single Treehouse project label could contain more than one original study.

We also recovered Boudin et al.'s published 1,378-record CSPG4 table and joined its specimen identifiers to original GEO metadata.[2] We retained 986 mapped records across nine cohorts after two conservative repeated-specimen exclusions; 166 records lacked a resolved diagnosis, and 224 TCGA records were omitted because TCGA was represented through Treehouse. Explicit old GSM aliases did not recur elsewhere in the selected published table and were not subtracted twice. A GEO UPS label was corrected from the primary Renner paper while preserving its original text.[8] These values remain on their published normalized scale, labeled CSPG4 mRNA (log2), not TPM. Historical two-color and mixed-platform collections supply qualified published-signal context, not newly established abundance replication.

Two additional clinical cohorts were analyzed separately. GSE213065 contains 87 profiles from 54 identified patients; we selected the first region of the earliest sampled timepoint, T1a, for each patient.[9] The deposited values are Salmon/Gencode 27 protein-coding gene TPM. These specimens include advanced disease and treatment histories. The supplement establishes 14 primary anatomical sites, seven metastases and one local recurrence among the selected specimens; 32 lack a T1 location classification in that table. GSE234092 contains 69 distinct surgical records with diagnosis labels, beyond the 34 retroperitoneal RNA cases described in the linked article.[10] We retained all repository records as a separately defined collection, separating two desmoids and one paraganglioma as context and retaining unresolved abbreviations. For each sample we divided CSPG4 featureCounts by the sum across all 64,253 supplied gene rows and multiplied by one million. These values are counts per million (CPM), not TPM.

OpenPedCan v15 supplied additional CNS-enriched context.[11] We used its independent-specimen lists, preferring primary-list representatives and adding only previously unrepresented donors from primary-plus. We excluded TCGA, TARGET, xenografts, hematologic entities and identified Treehouse donor aliases. Twenty-nine profiles were extracted; one source-labeled parental tumor associated with a chordoma cell-line family remained provenance-uncertain and was retained outside the clinical summaries. The other 28 had distinct source participant IDs. Library methods were analyzed separately, and source collection-event descriptors were preserved. Neither an Initial CNS Tumor descriptor nor primary-list membership was interpreted as proof of untreated primary systemic sarcoma.

### Statistical summaries and inference

The probability-of-superiority score was A=P(EMC>reference)+0.5P(tie), calculated across all available specimen pairs. A=0.5 denotes neutral ordering. For the pooled Hofvander reference, each of its 393 specimens had equal weight. We also report the mean of the 28 type-specific scores, which gives each source-defined reference category equal weight. These answer different questions; neither represents the population incidence of sarcoma types. A is not a fold change or externally validated diagnostic accuracy.

The expanded unstratified test used the exact rank-sum distribution under a common expression-distribution null for every allocation of nine EMC labels among the 402 included observations, preserving ties. The two-sided tail included rank sums at least as far from their null expectation as the observed sum. Bonferroni adjustment retained the original family of 11 genes. This adjustment addresses that gene family but does not erase retrospective choices of question, comparator set or analysis. The exchangeable-label null is a modeling assumption for observational specimens, not randomized assignment of tumor diagnoses. 

For each of the primary and broader references, we computed a nominal 95% percentile bootstrap interval from 50,000 independent two-sample specimen resamples, seed 20260921, using linear-interpolation quantiles.[12] Each draw resampled nine EMC specimens and the reference specimens independently at their original sample sizes; specimen multiplicities preserved dependence among pairs. These approximate, pointwise intervals describe sampling variability conditional on the observed design. They do not account for retrospective selection, unidentified patient overlap, assay confounding or nonrepresentative sampling. No new hypothesis test was added for the broader sensitivity.

We retained all original comparator-specific results, the original operational rule and its adverse sensitivity checks in Supplementary Information. Removing one EMC at a time describes dependence on individual specimens; those ranges are not confidence intervals. Earlier sequencing-year-conditioned analyses remain secondary. No demonstrated CSPG4 year effect motivated adjustment, and sparse matching does not establish control of technical confounding. Those analyses change the supporting patients and comparison sets and therefore do not replace the unstratified defined-reference question.

For external collections, we report the number of profiles, median, linear-interpolation quartiles and range on the original measurement scale for each source and diagnosis. The complete table of within-source pairwise A values is provided on each source’s designated measurement scale, retaining the qualifications for historical mixed-platform cohorts. Cross-source descriptive ranges include only pairs with at least five profiles of each diagnosis in each contributing stratum. The external figure uses LMS as a frequently represented reference; all other pairs remain available. No external P values, pooled cross-platform expression test or synthetic nine-EMC-versus-all-databases comparison was calculated. Uniform computational processing does not remove differences in specimen composition, library construction, disease stage or collection practice.

### Verification and contextual evidence

Source files, selection ledgers, code and result tables have cryptographic digests. Independent implementations checked original values, specimen mapping, quartiles and rank probabilities. The expanded CSPG4 exact tail was reproduced using a different integer-count algorithm. Additional small exhaustive controls checked the exact-test implementation. These checks establish computational consistency, not external expert endorsement or biological validity.

Human Protein Atlas normal-tissue RNA and protein records remained separate context, with assay reliability and missingness retained.[13,14] Historical GSE28866 3SEQ peaks and independent PRAME immunohistochemistry were not pooled with tumor RNA.[15,16] We did not calculate a safety ratio between HPA normalized TPM and tumor TPM.

**Use of artificial intelligence.** OpenAI Codex assisted with source recovery and organization, analysis-code implementation, computation, verification and drafting. The author is responsible for the final interpretation and manuscript. AI assistance and independent code checks do not establish biological validity.

## Results

### EMC was toward the higher end of the defined malignant reference

The nine EMC specimens had median CSPG4 expression of 54.18 TPM, an interquartile range of 41.41–63.98 TPM and a range of 10.14–207.08 TPM. The 393 reference specimens had a median of 11.87 TPM. The specimen-weighted score was A=0.84648 (approximate 95% bootstrap interval 0.70908–0.95759), and the equal-type score was 0.86556. The exact two-sided P value was 0.000130435; the Bonferroni-11 adjusted value was 0.00143479.

EMC had the highest observed median among the 29 labels in this defined malignant comparison, including EMC itself. Figure 1 also shows the nine additional Intermediate labels. Several groups were very small; this sample ordering is not an established population ranking. Individual distributions overlapped. Removing any one EMC specimen left the pooled A between 0.82761 and 0.89408, so the ordering was not dependent on the largest value alone. The analysis still contained only nine EMC specimens.

CSPG4 was not the only panel gene departing from the pooled reference. MSLN also had higher ordering, A=0.811, with adjusted P=0.00406, whereas several genes had lower ordering. The full 11-gene table is retained in the supplement. These pooled results do not replace the original comparator-specific rule, which CSPG4 alone satisfied, or promote another gene as a treatment target.

### High expression was not unique to EMC

The full 644-specimen atlas changes the interpretation of the malignant-only summary. GIST (n=14) had a median of 59.24 TPM and DFSP (n=10) a median of 59.10 TPM, both slightly above the EMC median. They were classified as Intermediate in the source and are visible in Figure 1; all 60 labels remain in Table S3, with the other source contexts in Figure S1. Adding the 96 eligible Intermediate specimens gave a broader-reference median of 13.20 TPM and A=0.82436 (approximate 95% interval 0.67780–0.94274); the equal-category score was 0.84793. This sensitivity preserved higher EMC ordering while showing its dependence on the reference definition. Several benign categories also had high values. Thus, the data do not support an EMC-specific expression threshold or uniquely high CSPG4 RNA across all soft-tissue tumors.

The original same-histology comparisons remained informative (Figure 2). Against LGFMS, CSPG4 A was 1.000 in the six-EMC versus 17-LGFMS arrays and 0.96581 in the nine-EMC versus 13-LGFMS RNA-sequencing comparison. Removing any one EMC or LGFMS array biopsy retained A=1. The array scores against MFS, SFT and desmoid were also 1.000; the corresponding Hofvander scores were 0.85370, 0.87879 and 1.000. DFSP supplied a contrary Hofvander comparison, A=0.46667. These results establish recurrence of particular observed contrasts, rather than universal specificity or complete patient independence between historical collections.

### Broader collections showed histology-dependent and source-dependent patterns

The external characterization retained 1,334 Treehouse profiles, 986 mapped published-array records, 54 GSE213065 profiles, 69 GSE234092 records and 28 OpenPedCan clinical-context profiles. These resource counts must not be added as independently verified patients. Treehouse already includes TCGA, TARGET and several original GEO/SRA cohorts, and it shares a pediatric source family with OpenPedCan. Known donor aliases were handled explicitly, but undisclosed overlap remains possible. The final external tables contain 304 source-by-diagnosis summaries and 1,480 within-source pairwise comparisons.

Some relative patterns recurred (Figure S2). MFS was lower than LMS in all six source strata supporting at least five profiles per group, with A=P(MFS>LMS)+0.5P(tie) ranging from 0.182 to 0.246. UPS was lower than LMS in all five supported strata, A=0.077–0.414. Other patterns were less uniform. Dedifferentiated liposarcoma had A=0.173–0.343 in four strata but 0.517 in Nakayama's 15-versus-six comparison. GIST had A=0.836 in GSE234092 (19 versus nine) and 0.502 in the Treehouse-processed SRP057793 collection (12 versus 40). These descriptive differences are not cross-study treatment effects or proof of the mechanism producing the RNA signal.

The added collections broadened representation of adult, pediatric and bone sarcomas, but did not provide a further identified EMC group. For example, the retained Treehouse records included 279 osteosarcoma and 115 Ewing profiles across qualified source strata. Those larger comparator collections cannot independently replicate an EMC contrast when EMC is not measured in them. They also cannot be attached numerically to the nine Hofvander EMC values as if all measurements came from a single assay.

### Retained sensitivity and tissue-context findings

The original three-histology CSPG4 composite remained 0.89454 using all years and 0.81111 under the earlier year-conditioned calculation. Only four distinct EMC patients supported the latter. Removing the 2019 sample group left two matchable EMC patients and a conditioned score of 0.43333, while the all-year score remained positive at 0.83333. The expanded-reference year-conditioned sensitivity likewise gave a larger P value, 0.02064, with adjusted P=0.22704. It used a different statistic and only 319 supported-year reference specimens. These adverse results are preserved, but neither establishes a year effect or isolates technical variation from specimen composition and chance.

The separate CHRNA6 control had A=1.000 against LGFMS in both assays and in the original marginal and year-conditioned three-histology composites. GSE24369 contributed to its discovery, so this is historical concordance rather than independent discovery validation.

The separate tissue evidence remained limiting. HPA records do not establish EMC cell-surface density or normal-tissue sparing; normal-tissue IHC and cell-localization assays examine different compartments.[13,14] A normal-colon record exceeded the lowest EMC library value in the separate GSE28866 3SEQ context.[15] In the PRAME protein study, all five EMC cases were negative in both readers' columns with antibody QR005, despite favorable PRAME RNA ordering against LGFMS in the retained RNA analyses.[16] These are different specimens and assays, not paired RNA–protein measurements.

## Discussion

This public-data reanalysis locates EMC toward the higher end of CSPG4 RNA expression within two declared sarcoma references. Higher ordering persisted when the source's Intermediate categories were included, and four named contrasts recurred across RNA sequencing and arrays. At the same time, GIST and DFSP had slightly higher observed medians, and several benign groups also expressed CSPG4 strongly. The combined result is an EMC-centered comparative account, not an EMC-specific marker claim.

Boudin et al. previously established broad CSPG4 heterogeneity and prognostic and immune associations across soft-tissue sarcomas.[2] Here, the contribution is the explicit placement of a rare histology, paired display of the available direct EMC contrasts, and source-qualified maps of additional tumor types. The external collections show recurring and divergent relative patterns but cannot replicate an EMC contrast in the absence of identified EMC specimens.

The nine EMC observations remain the principal limit on precision. The wide bootstrap intervals make that limitation visible despite the much larger reference samples. Both pools reflect the source collection's proportions, not sarcoma incidence, and the source classifications are not comprehensive clinical taxonomies. Equal-category estimates and the full category table expose this reference dependence; neither removes it. The exact P value addresses a common-distribution null within the selected primary comparison.

Cross-study scale differences are a separate issue from calendar year. Treehouse's consistently processed data, Hofvander TPM, protein-coding Salmon TPM, transcriptome-capture CPM and historical array signals differ in quantification and specimen context. Some historical collections also combine platforms or reference preparations. A shared gene symbol or the word TPM is not sufficient calibration for pooling these measurements. We therefore retained within-source descriptions and rank contrasts without pooling them into a cross-database EMC test.

The study has further limits. It is an exploratory public-data reanalysis after CSPG4 had already been identified as a gene of interest. Multiplicity correction for 11 genes does not account for every possible retrospective choice. Small and uneven groups limit precision; the approximate bootstrap intervals do not correct post-selection bias or unmeasured confounding, and deletion ranges are not confidence intervals. Some specimen identities, clinical states and historical overlaps cannot be fully resolved. The broader search identified additional EMC-containing articles, but not another open, qualified EMC-versus-sarcoma expression matrix: controlled-access data, missing deposited EMC records and reuse of earlier specimens are concrete boundaries, documented in the supplement. This is not evidence that no further usable cohort exists.

Finally, bulk RNA does not localize CSPG4 to malignant cells or measure accessible protein. Source Table S1 recorded ASCAT purity and grade as unavailable for all nine retained EMC specimens, and normal tissues were not matched to tumors. Neither statistical separation nor relative rank among sarcomas establishes a therapeutic window, safety, diagnostic performance or treatment benefit. The analysis provides a more complete RNA comparison and a reproducible reference resource for subsequent tissue studies and independently sampled EMC cohorts.

## Data code and declarations

**Data availability.** The original Hofvander data are available through https://doi.org/10.5281/zenodo.17866629. Original array data and annotations are available as GEO GSE24369 and GPL6244. Additional inputs are Treehouse Tumor Compendium 25.01, Boudin et al. Supplementary Table S8, GEO GSE213065 and GSE234092, and OpenPedCan v15. The revision’s data and code package, including exact source URLs, selection ledgers, digests and specimen values, is available at https://github.com/trimcrae/Rare-cancers/blob/1f9f087e2dd666f721bed6c20b8b64d72203c12e/research/release-candidates/cspg4-presubmission-20260921/CSPG4-data-code.zip. The original reproducibility archive remains at https://assets-eu.researchsquare.com/files/rs-10959636/v1/b95606f3a3799c60c8ac4434.zip. That historical archive does not contain the new expanded analyses. Source-specific attribution and reuse terms continue to apply.

**Author and correspondence.** Tristan D. McRae, independent researcher, unaffiliated, is the corresponding author at trimcrae@gmail.com; ORCID 0000-0002-1823-1451. The author has no institutional affiliation.

**Research scope.** This work reanalyzes public data and reports no newly collected participant specimens, intervention, protein experiment or clinical treatment. No new ethics approval, exemption or waiver is asserted.

**CRediT authorship contribution statement.** Tristan D. McRae: Project administration, Supervision. AI-assisted implementation, execution, verification and drafting are disclosed in Methods. The author is responsible for the final interpretation and manuscript.

**Funding.** This research received no funding.

**Competing interests.** No competing financial interests exist. One non-financial interest is declared: the author is a survivor of extraskeletal myxoid chondrosarcoma, the disease this work addresses.

**Declaration of generative AI and AI-assisted technologies in the manuscript preparation process.** OpenAI Codex assisted with source organization, code implementation, computation, verification and drafting, as described in Methods. The author takes responsibility for the article. Data visualizations were generated programmatically from the supplied measurements and estimates with AI-assisted code; no primary experimental image was generated or altered.

## References

[1] Dulken BW, Kingsley L, Zdravkovic S, Cespedes O, Qian X, Suster DI, et al. CHRNA6 RNA In Situ Hybridization Is a Useful Tool for the Diagnosis of Extraskeletal Myxoid Chondrosarcoma. Mod Pathol. 2024;37:100464. https://doi.org/10.1016/j.modpat.2024.100464.

[2] Boudin L, de Nonneville A, Finetti P, Mescam L, Le Cesne A, Italiano A, et al. CSPG4 expression in soft tissue sarcomas is associated with poor prognosis and low cytotoxic immune response. J Transl Med. 2022;20:464. https://doi.org/10.1186/s12967-022-03679-y.

[3] Hofvander J, Köster J, Sydow S, Piccinelli P, Vult von Steyern F, Tsagkozis P, et al. Transcriptomic Subgroups in Soft Tissue Tumors Correlate with Morphologic Subtype, Genomic Features, and Outcome. Clin Cancer Res. 2026;32:1825–1834. https://doi.org/10.1158/1078-0432.CCR-25-3740.

[4] McRae TD. Fixed-panel tissue RNA prioritization in extraskeletal myxoid chondrosarcoma: CSPG4 evidence across cohorts with comparator and sequencing-year limits. Research Square. 2026. Version 1 and accompanying code/data supplement. https://doi.org/10.21203/rs.3.rs-10959636/v1.

[5] National Center for Biotechnology Information. GEO series GSE24369 and platform GPL6244. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE24369; https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL6244.

[6] McRae TD. EMC research program expression-panel definitions. Pinned revision 81d2931733aae640220c042039d0c53efed1690a. https://github.com/trimcrae/Rare-cancers/blob/81d2931733aae640220c042039d0c53efed1690a/research/modalities/emc_expression_panels.py.

[7] Beale HC, Learned K, Kephart ET, et al. Consistently processed RNA sequencing data from 50 sources enriched for pediatric data. Sci Data. 2025;12:1134. https://doi.org/10.1038/s41597-025-05376-z.

[8] Renner M, et al. Integrative DNA methylation and gene expression analysis in high-grade soft tissue sarcomas. Genome Biol. 2013;14:R137. https://doi.org/10.1186/gb-2013-14-12-r137.

[9] Subramanian A, Nemat-Gorgani N, Ellis-Caleo TJ, et al. Sarcoma microenvironment cell states and ecosystems are associated with prognosis and predict response to immunotherapy. Nat Cancer. 2024;5:642–658. https://doi.org/10.1038/s43018-024-00743-y.

[10] Seligson ND, Asmann YW, Almerey T, et al. Molecular markers of proliferation, DNA repair, and immune infiltration defines high-risk subset of resectable retroperitoneal sarcomas. Surg Oncol. 2024;56:102125. https://doi.org/10.1016/j.suronc.2024.102125.

[11] Geng Z, Wafula E, Corbett RJ, et al. The Open Pediatric Cancer Project. GigaScience. 2025;14:giaf093. https://doi.org/10.1093/gigascience/giaf093.

[12] Efron B. Bootstrap methods: another look at the jackknife. Ann Statist. 1979;7:1–26. https://doi.org/10.1214/aos/1176344552.

[13] Uhlén M, Fagerberg L, Hallström BM, Lindskog C, Oksvold P, Mardinoglu A, et al. Tissue-based map of the human proteome. Science. 2015;347:1260419. https://doi.org/10.1126/science.1260419.

[14] Thul PJ, Åkesson L, Wiking M, Mahdessian D, Geladaki A, Ait Blal H, et al. A subcellular map of the human proteome. Science. 2017;356:eaal3321. https://doi.org/10.1126/science.aal3321.

[15] Brunner AL, Beck AH, Edris B, Sweeney RT, Zhu SX, Li R, et al. Transcriptional profiling of long non-coding RNAs and novel transcribed regions across a diverse panel of archived human cancers. Genome Biol. 2012;13:R75. https://doi.org/10.1186/gb-2012-13-8-r75.

[16] Cammareri C, Beltzung F, Michal M, Vanhersecke L, Coindre JM, Velasco V, et al. PRAME immunohistochemistry in soft tissue tumors and mimics: a study of 350 cases highlighting its imperfect specificity but potentially useful diagnostic applications. Virchows Arch. 2023;483:145–156. https://doi.org/10.1007/s00428-023-03606-6.

## Figure legends

**Figure 1. CSPG4 RNA in EMC and the primary and broader source references.** The 498 specimens span 38 original diagnosis labels: nine EMC (burgundy), 393 primary Malignant-category references (blue), and 96 additional Intermediate-category references (ochre). GIST and DFSP are therefore visible beside EMC. Dots show specimens, segments the interquartile range and vertical marks the median. The axis uses log2(1+TPM) spacing with TPM labels. Categories are ordered by observed median; small groups do not establish population rankings. The original 393-reference exact test is unchanged. Melanoma, unclassified spindle-cell tumors and benign contexts remain outside both reference pools; all 60 labels appear in Table S3. MIFS/HFLT denotes the source's combined myxoinflammatory fibroblastic sarcoma/hemosiderotic fibrolipomatous tumor label; NOS, not otherwise specified. Plot generated from supplied data using AI-assisted reproducible code.

**Figure 2. Direct EMC comparisons shared across two assays.** Points show A=P(EMC>comparator)+0.5P(tie) for the four diagnosis groups available in both Hofvander RNA sequencing and GSE24369 arrays. The table supplies EMC/reference specimen counts and A for each assay. Differences are calculated within each source; expression units are not pooled. The apparent complete array separation describes six EMC biopsies and is not a validated diagnostic cutoff. Patient independence across the historical collections and array lesion stage are incompletely established. LGFMS, low-grade fibromyxoid sarcoma; MFS, myxofibrosarcoma; SFT, solitary fibrous tumor. Plot generated from supplied data using AI-assisted reproducible code.
