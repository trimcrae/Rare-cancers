---
id: "DOC-CSPG4-PRESUBMISSION-20260921-SUPPLEMENT"
title: "Supplementary information for CSPG4 RNA across sarcoma types"
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
# Supplementary information for CSPG4 RNA across sarcoma types

This supplement distinguishes the preserved original analysis, the expanded same-source comparison and the new public-source characterization. The original protocols and computations remain available in the Research Square version 1 archive. New calculations and metadata corrections are supplied with this revision; the old archive is not presented as containing them.

## Scope and chronology

The original fixed panel and comparator rule preceded inspection of target values in the Hofvander cohort. The primary types were MLPS, LGFMS and synovial sarcoma, with separate MFS, DFSP, SFT and desmoid contexts. The September 19 extension broadened the descriptive atlas and malignant-category reference after those results were known. A dated amendment made the unstratified defined-reference rank test the leading analysis after an earlier year-conditioned run. It is exploratory, not preregistered. Bonferroni correction applies to the 11 retained genes and does not remove all consequences of retrospective analysis choices.

External source plans were recorded before new expression analysis. Treehouse metadata review found 11 cross-project NCI donor aliases after the first gene slices were obtained but before expression summaries. The same expression-blind ranking rule was applied to the corrected identities. Boudin diagnosis mapping was frozen before reading its CSPG4 column. Modern GEO selection preceded extraction. GSE234092 required a header-based mapping amendment because its matrix column names differ from GEO titles. OpenPedCan specimen selection preceded remote extraction. One parental-tumor provenance exclusion was communicated from metadata review before the root read its expression values and recorded afterward. No specimen was selected or excluded because of a favorable CSPG4 value.

## Table S1 Source inventory and independent-patient limits

| Collection | Retained analytic scope | Measurement | Main qualification |
|---|---|---|---|
| Hofvander | 644 specimens; 9 EMC and 393 defined malignant references; 242 other contexts | Gene TPM | Fixed specimen exclusions; 60 original labels, not all sarcoma types |
| GSE24369 | 6 EMC, 17 LGFMS, 6 MFS, 6 desmoid, 5 SFT, 2 muscle pools | GPL6244 RMA log2 | Unknown lesion stage; muscle pools are not individual controls |
| Treehouse 25.01 | 1,334 histology-eligible profiles in 35 assay/source/accession strata | Gene-symbol log2(TPM+1) | 860 source donor keys and 474 unverified prefix groups; not universally verified patients |
| Boudin S8 | 986 mapped records in 9 historical cohorts | Published normalized log2 scale | Possible unresolved patient reuse and mixed platforms; not TPM |
| GSE213065 | 54 T1a profiles from 54 explicit patient IDs | Salmon protein-coding TPM | Advanced-disease context; T1 does not establish untreated primary disease |
| GSE234092 | 69 surgical records including 3 non-sarcoma contexts | FeatureCounts CPM | Source cohort exceeds linked paper subset; clinical state and some labels unresolved |
| OpenPedCan v15 | 28 clinical-context profiles in 2 library strata | RSEM collapsed gene TPM | CNS-enriched PBTA source family; aliases excluded; not general sarcoma sampling |

Resource counts are not summed as a unique global patient count. They represent different selection policies and measurement scales. In particular, TCGA is already represented in Treehouse; it is not also counted as 224 additional Boudin cases. Original GEO/SRA studies within Treehouse are not added again as separate datasets. OpenPedCan and Treehouse share CBTN/PBTA source families even after known patient aliases are excluded.

## Fixed Hofvander specimen policy and quantities

The retained EMC IDs are 11881-19, 3371-22, 3372-22, 4716-22, 4840-13, 5149-18, 5241-06, 7931-19 and 8102-22. The previously reported IDs 104-92, 168-97 and 536-00 map to historical MDB9736 cases 3, 4 and 7. The fourth excluded EMC specimen, 5081-14, is a local recurrence. No patient date is inferred from an identifier suffix. Original diagnoses, publication flags and specimen exceptions are retained in the supplied eligibility manifest.

The TPM source SHA256 is b0d665d1bd1d96ace1faf66cc5a4d7ab7e41cb487c8f0f61734f102a1f9a7af3. The original GSE24369 family gzip SHA256 is 98c83c8ca23b7052cf0d4d0099a7bf1af6c3c972276038c3a633e2a5349b3c37. Source precision is preserved. The expanded specimen file contains all 7,084 reported values for the 11 genes across 644 specimens; zeros remain zeros and are not interpreted as biological absence.

For EMC values x and reference values y, A is the average of I(x>y)+0.5I(x=y) over specimen pairs. The exact null distribution uses doubled midranks so ties retain their integer multiplicity. The observed doubled-rank sum is 6,078 and the null center is 3,627. The two-sided tail contains 90,052,879,544,272 label allocations out of 690,402,510,704,386,700. This is an exact combinatorial calculation, not a Monte Carlo estimate. The source pool is a chosen observational reference; these allocations do not describe randomized assignment of diagnoses.

The patient-weighted A for CSPG4 is 0.8464801. Giving each of the 28 reference labels equal weight gives 0.8655617. Single-EMC deletion gives 0.8276081–0.8940840. These deletion limits are not a confidence interval. The September21 amendment added an approximate 95% percentile bootstrap interval of 0.7090755–0.9575912 for this pooled A. The broader source Malignant-or-Intermediate reference contains 489 specimens in 37 labels, with median 13.20 TPM, specimen-weighted A=0.8243581 (interval 0.6778005–0.9427403) and equal-category A=0.8479346. Both references retain the exclusions of melanoma and unclassified spindle-cell tumors. No new P value was calculated for the broader reference. The nine observed CSPG4 values in increasing order are 10.14, 12.77, 41.41, 48.92, 54.18, 58.20, 63.98, 90.14 and 207.08 TPM.

The two-sample specimen bootstrap used 50,000 replicates, seed 20260921 and NumPy PCG64, restarting the generator for each reference. Independent multinomial multiplicities for nine EMC and n reference specimens were applied to the pairwise comparison matrix in 50 blocks of 1,000 draws. Each bootstrap A equals w-transpose C v divided by 9n. This exactly represents ordinary specimen resampling with replacement; dependent pairs are not independently resampled. Limits are NumPy linear-interpolation 2.5th and 97.5th percentiles. The nominal pointwise intervals are approximate and conditional on the observed specimen/reference design, not corrected for retrospective selection, unknown overlap, assay confounding or population sampling. The two overlapping-reference intervals do not test the difference between reference definitions. The dated plan, code and exact outputs accompany the archive.

## Table S6 Source-reported molecular support for retained EMC

EMC membership follows the unchanged original source diagnosis. Table S1 marks all nine retained specimens Fusion=Yes; its footnote permits evidence from current RNA sequencing or previous methods. Grade and ASCAT ploidy/purity are NA for all nine. Table S3 supplies filtered RNA-sequencing fusion records, summarized below with source qualifiers. Source Excel row numbers include the header.

| Specimen ID | S3 fusion | S3 row | Source qualification |
|---|---|---:|---|
| 11881-19 | TCF12::NR4A3 | 69 | High confidence; in-frame |
| 3371-22 | No filtered record | — | S1 Fusion=Yes; exact fusion not crosswalked |
| 3372-22 | HSPA8::NR4A3 | 71 | High confidence; in-frame; prior MDB15434 report |
| 4716-22 | TAF15::NR4A3 | 72 | Medium confidence; source frame label stop-codon |
| 4840-13 | EWSR1::NR4A3 | 73 | High confidence; in-frame |
| 5149-18 | FUS::NR4A2 | 75 | High confidence; in-frame; RT-PCR verified |
| 5241-06 | EWSR1::NR4A3 | 76 | High confidence; in-frame |
| 7931-19 | EWSR1::NR4A3 | 78 | High confidence; in-frame |
| 8102-22 | EWSR1::NR4A3 | 79 | High confidence; in-frame |

Source Table S4 row58 reports all 13 original EMC as fusion-positive, including one FUS::NR4A2 and an additional RT-PCR-confirmed TAF15::NR4A3 missed by both callers. That comment has no specimen-level crosswalk and is not assigned here to 3371-22. Seven retained cases have explicit NR4A3 fusions in filtered S3. The FUS::NR4A2 case is preserved under its source EMC diagnosis, not reclassified from a gene name alone. The source describes morphological/IHC rereview of selected cases, not documented rereview of every retained EMC. Molecular-support differences do not change the frozen specimen policy. The source workbooks, hashes and a machine-readable extraction accompany this revision.

## Original panel rule and retained adverse checks

The original operational rule required a marginal equal-histology score of at least 0.70; A>0.50 for each primary histology in both marginal and supported-year comparisons; and both composites above 0.50 after each single EMC and histology deletion. The threshold was an operational benchmark, not a clinical cutoff. Year removal, comparator-patient removal and revised-diagnosis checks qualified interpretation but were not additional pass conditions. All original results remain in the preserved tables; no gene is reclassified by the new pooled test.

The nine EMC specimens fall in sequencing years 2019 (two), 2020 (one), 2021 (one), 2022 (two) and 2023 (three). The original matched MLPS and LGFMS comparisons use 2019/2021; synovial sarcoma uses 2019/2020. Each uses three EMC specimens, with only four distinct EMC patients across the comparisons. The two 2019 specimens supply two-thirds of each matched histology's EMC weight. Year labels are incomplete proxies, not demonstrated assay changes or biological exposures.

For CSPG4, the original marginal/matched composites are 0.89454/0.81111. Single-EMC deletion ranges are 0.88136–0.94035/0.71667–0.94444; single-histology deletion ranges are 0.85891–0.94896/0.75000–0.88333. Removing the 2019 group removes two EMC and 19 original comparator specimens. Seven EMC remain in the all-year estimate, but only two matchable EMC remain in the conditional estimate, which becomes 0.43333; the marginal value is 0.83333. Revised diagnoses give 0.89475/0.81111, but those labels were partly informed by expression and are not independent confirmation.

The earlier conditional bootstrap used 2,000 draws with seed 20260906, resampling within histology/year groups and sharing each EMC resample across comparisons. Its intervals are pointwise and conditional on the observed support; singleton groups remain fixed. The matched MLPS interval for CSPG4 is [0.66667, 0.66667], a sparse-design artifact rather than absence of biological uncertainty. The original composite intervals were 0.86614–0.91806 marginal and 0.75278–0.86111 matched. They do not describe uncertainty in the new pooled 393-specimen reference.

The expanded-reference conditional sensitivity used 199,999 permutations, seed 20260919, and 319 references in supported years. Its statistic was 0.8212599, with P=0.02064 and Bonferroni-11 P=0.22704. In 2023, three EMC specimens had only one reference, giving that sparse comparison one-third of the EMC weight. This separate estimand and its limitations remain reported. Neither agreement nor disagreement with the all-year calculation establishes an effect of sequencing year.

## Array and normal-tissue measurements

The GPL6244 transcript clusters were CD276 7984743, SSTR2 8009526, PRAME 8074856, FAP 8056257, CD248 7949588, CSPG4 7990545, MSLN 7992071, L1CAM 8175871, GPC3 8175234, ALPP 8049123, CDH17 8151795 and the separate CHRNA6 control 8150550. Each was uniquely assigned under the retained annotation policy; no best-probe search or cross-gene standardization was performed. Finite negative log-array values are valid signals. TPM values must be finite and nonnegative. Missing or duplicate measurements are not imputed.

The original LGFMS-specific CSPG4 scores are 1.00000 in arrays and 0.96581 in Hofvander. The original separate matched RNA-sequencing value is 0.93333. Positive array scores against MFS, SFT and desmoid are retained with all other panel genes, including unfavorable or reversed contrasts. The separate CHRNA6 control had A=1.000 in the original marginal and matched three-histology composites and against LGFMS in both assays. CHRNA6 was discovered using GSE24369, so its reanalysis there is not independent discovery validation.

HPA records distinguish normal RNA, IHC and ICC/IF, with reliability warnings and missing records preserved. HPA normalized TPM is not directly divided into tumor TPM to estimate safety. GSE28866 contains four EMC library/STT records whose patient independence is not established; its selected 3SEQ peaks are a different quantity. A normal-colon value exceeds the lowest EMC library value. The PRAME workbook SHA256 is 20b4bd1243be22e4eee2da7470da986091f91cc4959fa416708748ba99187ca7. Sheet 1 rows 128–132 contain five EMC cases, all negative in both reader columns with antibody QR005. Four have recorded molecular support; the fifth lacks a recorded ancillary method. Blank percentage fields were not turned into measurements.

## External source selection and corrections

Treehouse candidates were selected from explicitly declared diagnosis labels, with other mesenchymal categories retained as context. Original donor identifiers were source-qualified. Exact NCI aliases were NCI0039, NCI0041, NCI0047, NCI0071, NCI0097, NCI0115, NCI0135, NCI0150, NCI0165, NCI0167 and NCI0198. ENA metadata connected SRP083915 with SRP069338, the SRA study behind phs000768.v2.p1. Ten pairs shared an experiment alias; NCI0097 represented different tumor specimens from the same donor. The same PolyA-first, lexicographic selection rule retained one profile per identity. NCI0165's Ewing/CIC diagnosis conflict was excluded from histology summaries rather than resolved using expression.

The 1,334 eligible Treehouse profiles comprise 1,098 PolyA and 236 ribosomal-depletion profiles; 1,280 are in the declared sarcoma/related scope and 54 in other mesenchymal context. The 35 analysis strata use library method, source name and original accession, with Treehouse project ID only as a fallback. THR52 contains two original accessions, SRP057793 and SRP113755, which remain separate. Source keys do not uniformly prove distinct patients, and clinical stage and treatment are not available in the clinical tables. The TCGA-derived label fibromyxosarcoma is not reclassified as LGFMS.

Boudin S8 contains 1,022 distinct GSM identifiers. Its actual Gobble and Guibault counts are 140 and 34, whereas Table S1 lists the corresponding inclusion counts in the opposite order. We used the actual S8 identifier joins. Of its 1,378 records, 986 remain, 166 lack an established diagnosis in inspected metadata, 224 TCGA records are represented through Treehouse, and two Nielsen records are alternative conservative STT-prefix identities. Forty-four Gobble and 183 Chibon old-accession aliases do not also occur as separate S8 records. The corrected Renner UPS label is supported by its primary paper, separately from pleomorphic liposarcoma. Historical MFH is not silently converted to modern UPS, nor malignant hemangiopericytoma to SFT. The unqualified Round cell label remains unspecified.

The Nielsen normalized cohort includes seven GPL versions and Beck two. Nielsen, Baird and Beck include historical two-color measurements with source-specific reference preparations. Their published-normalized distributions and numerical ranks are retained as qualified context; they are not new demonstrations of cross-assay RNA abundance. Four excluded West experiment identifiers match Stanford image IDs in retained Nielsen records; these would need resolution before any later recovery.

For GSE213065, T1a provides exactly one record per explicit patient ID. Supplement S14 describes selected T1 locations for 22 patients: 14 primary, seven metastatic and one local recurrence. Its SRC95 and SRC183 entries begin at T2, so those locations were not transferred to T1. Treatment between longitudinal specimens is not evidence that the first specimen was untreated. For GSE234092, all 69 MSB identifiers map uniquely to count columns using the MSB number and specimen identifier. MSB40 uses number 40 plus prefix agreement between GEO 13172022 and matrix 1317202224; this is not a complete TA-identifier match. Count denominators range from 9,350,062 to 68,678,731. Source labels AS and PLS remain unresolved abbreviations; PLS is not silently merged with PLPS.

OpenPedCan's 28 clinical-context records consist of 11 source-classified Ewing, 10 Sarcoma, three chordoma, three MPNST and one rhabdomyosarcoma; 17 use stranded libraries and 11 poly-A stranded libraries. Original free-text diagnoses and sampling events are preserved without retrospectively imposing a finer taxonomy. Six records enter only through primary-plus and represent recurrence, progression or second malignancy context. Known Treehouse donor aliases, myeloid and histiocytic sarcomas were excluded. BS_28GPVQAA, labeled Mug-CC1-T, is retained in the extraction ledger with 96.02 TPM but outside clinical summaries because the uncultured-parental-specimen crosswalk remains unverified. The source distinguishes it from derived cell-line records; we do not relabel it a proven cell line.

The OpenPedCan RDS was read on a remote runner after a storage check, not copied to the local workspace. Its actual dimensions were 60,325 genes by 4,124 profiles; exactly one row named CSPG4 and each of the 29 requested columns were present. The source MD5 was 5e17af159401140c5946dd0517d03015 and SHA256 57b803d2dbc8fc61ec324a3a2c37d06205ea21c07ba2d14e83f0b6e7e3f5933e. Only the selected gene row, schema and receipt were exported.

## Additional EMC source availability

| Source | Verified lead | Reason not counted as a new direct EMC replication |
|---|---|---|
| GSE4303 | 10 EMC arrays; some same-platform sarcoma comparators | Two-color reference compatibility and specimen provenance remain unresolved |
| Arbajian 2017 and GSE103677 | Published EMC discussion and new SEF arrays | EMC comparison reuses the six GSE24369 biopsies |
| Watson 2018, DOI 10.1002/path.5053 | Four EMC among study controls | Only controlled EGA raw data verified; no open processed matrix and EMC crosswalk recovered |
| Zullow 2022, DOI 10.1016/j.molcel.2022.03.019 | Article describes seven EMC | Retained deposited-data audit finds MLS/Ewing records, not the EMC measurements |
| Chaiboonchoe 2026, PRJNA1357027 | 12 molecularly confirmed EMC in targeted TempO-Seq source | No same-study non-EMC comparator set; not a direct broad comparison |
| Racanelli 2019, DOI 10.1093/annonc/mdz283.054 | Abstract describes 12 EMC and 7 myoepithelial tumors | No public measurement accession verified; independence unresolved |

GSE6481 contains 19 myxoid liposarcomas, not 19 EMC. We followed its original diagnosis metadata rather than an inconsistent secondary description. GSE71118 reuses 303 of 312 records from GSE21050 and was not counted as 312 additional independent tumors. The large ORIEN sarcoma collection is a specific request-only lead; no correspondence or controlled-access request was made. These are source-specific availability findings, not a claim that all remaining computational work or all public data are exhausted.

## Reproducibility and supplied tables

The source/data package includes the original expanded Hofvander selection, reported panel values, exact-test outputs and complete category summaries; external selection and alias ledgers; the preserved CSPG4 extracts; original-unit summary tables; and scripts. Every external pair is within its designated source stratum. Cross-source A ranges are descriptive, not a meta-analysis, and no transitive EMC contrasts are inferred through shared comparator types.

Table S2 below reports every original panel gene under the expanded reference test. Table S3 reports all 60 original Hofvander labels. The accompanying machine-readable Table S4 is external-type-summaries.csv (304 rows); Table S5 is external-within-source-pairs.csv (1,480 rows). External-pair-cross-source-ranges.csv and external-LMS-reference.csv retain the complete supported descriptive comparisons and figure inputs. Original panel effects and all deletion results remain in the historical-analysis subfolder and the original public archive.

The original reproducibility archive has SHA256 56e089a6b39b9d5d5140a4185987778803359ab1154d26beb882d6e6197f3ea6. Its original-source checks and offline replay are historical accepted evidence for those exact inputs; they were not repeated to validate the new data. Independent new checks verified the Treehouse query-to-specimen alignment, Boudin row joins, both modern GEO source matrices and count denominators, and all new summary/rank arithmetic. OpenPedCan's large-matrix extraction is verified by its committed guarded script, actual runner receipt, exact source checksum and exported schema; it was not independently downloaded and re-extracted a second time.

## Figure S2 External within-source CSPG4 ordering against LMS

The former external heatmap is retained as Figure S2. Each cell is A=P(row diagnosis>LMS)+0.5P(tie), within the labeled source, and requires at least five profiles of each type. Blank cells lack that support and are not negative results. Each source retains its measurement scale; historical Boudin cohorts retain the two-color or mixed-platform qualifications. There is no external EMC estimate or pooled expression scale. The 304 summaries and 1,480 pairwise comparisons remain in the accepted final tables.

## Figure S1 Other eligible tumors in the Hofvander source

The 242 eligible specimens outside the defined malignant comparison remain visible, including source-classified benign and intermediate tumors, melanoma and unclassified tumors. The display uses the same specimen values and graphical conventions as Figure 1; its Intermediate groups overlap the broader reference now shown there. This retained panel still gives all 242 specimens outside the primary comparison. No high-expression category was omitted because it weakens an EMC-specific interpretation. Original source diagnoses and classes, including any historical spelling, are retained in Table S3.


## Table S2 Expanded reference results for all 11 genes

| Gene | A | Exact two-sided P | Bonferroni-11 P |
|---|---:|---:|---:|
| CD276 | 0.1781 | 0.000473071 | 0.00520378 |
| SSTR2 | 0.6125 | 0.25305 | 1 |
| PRAME | 0.3565 | 0.134548 | 1 |
| FAP | 0.1090 | 6.87292e-06 | 7.56022e-05 |
| CD248 | 0.0905 | 1.43057e-06 | 1.57363e-05 |
| CSPG4 | 0.8465 | 0.000130435 | 0.00143479 |
| MSLN | 0.8107 | 0.000369283 | 0.00406212 |
| L1CAM | 0.5638 | 0.519536 | 1 |
| GPC3 | 0.1928 | 0.00093797 | 0.0103177 |
| ALPP | 0.5448 | 0.462165 | 1 |
| CDH17 | 0.4047 | 0.307226 | 1 |

## Table S3 All eligible original Hofvander diagnosis labels

Classes and labels follow the original source. A compares EMC with the row category and is descriptive; sparse groups do not establish population ordering. The EMC row has no self-comparison.

| Original diagnosis | Class | n | Median TPM | Q1 to Q3 | A |
|---|---|---:|---:|---:|---:|
| Angiofibroma of soft tissue | Benign | 2 | 10.66 | 7.59–13.72 | 0.889 |
| Angiolipoma | Benign | 3 | 24.56 | 20.05–25.20 | 0.778 |
| Angiosarcoma | Malignant | 8 | 22.48 | 15.21–38.86 | 0.736 |
| Atypical lipomatous tumor | Intermediate | 38 | 30.08 | 17.47–38.48 | 0.737 |
| Benign fibrous histiocytoma | Benign | 5 | 12.59 | 9.47–13.04 | 0.889 |
| CD34-postive superficial fibroblastic tumor | Intermediate | 7 | 6.03 | 3.17–7.76 | 1.000 |
| Clear cell sarcoma | Malignant | 3 | 18.54 | 9.43–21.22 | 0.852 |
| Cryptic liposarcoma | Malignant | 22 | 6.09 | 4.71–13.39 | 0.904 |
| Dedifferentiated liposarcoma | Malignant | 20 | 13.73 | 8.11–21.45 | 0.822 |
| Dermatofibrosarcoma protuberans | Intermediate | 10 | 59.10 | 40.12–76.16 | 0.467 |
| Desmoid | Benign | 11 | 7.11 | 5.10–7.84 | 1.000 |
| Desmoplastic fibroblastoma | Benign | 2 | 24.68 | 18.71–30.65 | 0.833 |
| Desmoplastic small round cell tumor | Malignant | 7 | 3.15 | 2.10–4.82 | 1.000 |
| Endometrial stromal sarcoma | Malignant | 2 | 4.82 | 4.38–5.25 | 1.000 |
| Epithelioid sarcoma | Malignant | 6 | 6.36 | 3.72–9.62 | 0.981 |
| Ewing sarcoma | Malignant | 3 | 5.34 | 4.67–6.76 | 1.000 |
| Extraskeletal myxoid chondrosarcoma | Malignant | 9 | 54.18 | 41.41–63.98 | — |
| GIST | Intermediate | 14 | 59.24 | 24.10–85.81 | 0.500 |
| Granular cell tumor | Intermediate | 2 | 2.82 | 2.68–2.95 | 1.000 |
| Hamartomatous fibroma | Benign | 2 | 28.58 | 22.98–34.19 | 0.778 |
| Hibernoma | Benign | 16 | 10.33 | 6.50–13.14 | 0.910 |
| Inflammatory rhabdomyoblastic tumor | Malignant | 5 | 1.94 | 1.62–2.18 | 0.956 |
| LMS | Malignant | 39 | 18.98 | 6.85–35.21 | 0.775 |
| Lipoblastoma | Benign | 7 | 23.42 | 15.57–55.52 | 0.635 |
| Lipoma | Benign | 20 | 43.97 | 25.14–67.62 | 0.539 |
| Lipoma, spindle cell/pleomorphic | Benign | 10 | 24.22 | 13.34–30.66 | 0.711 |
| Low-grade fibromyxoid sarcoma | Malignant | 13 | 6.11 | 5.26–8.50 | 0.966 |
| MPNST | Malignant | 18 | 27.80 | 10.87–50.12 | 0.722 |
| Melanoma | Malignant | 5 | 22.16 | 19.59–71.77 | 0.511 |
| Myoepithelial tumor | Malignant | 2 | 4.38 | 3.76–4.99 | 1.000 |
| Myxofibrosarcoma | Malignant | 60 | 12.36 | 5.70–21.97 | 0.854 |
| Myxoid liposarcoma | Malignant | 14 | 19.68 | 13.06–25.79 | 0.786 |
| Myxoid pleomorphic liposarcoma | Malignant | 3 | 14.68 | 13.85–56.09 | 0.556 |
| Myxoinflammatory fibroblastic sarcoma/hemosiderotic fibrolipomatous tumor | Malignant | 7 | 7.92 | 5.27–15.05 | 0.937 |
| Myxoma Class 1 | Benign | 5 | 12.01 | 10.29–12.17 | 0.867 |
| Myxoma Class 2 | Benign | 4 | 11.10 | 7.70–15.86 | 0.917 |
| Neurofibroma | Benign | 4 | 66.26 | 30.57–103.73 | 0.444 |
| Neurofibroma, atypical | Benign | 1 | 119.11 | 119.11–119.11 | 0.111 |
| Neurofibroma, diffuse | Benign | 1 | 281.63 | 281.63–281.63 | 0.000 |
| Neurofibroma, plexiform | Benign | 2 | 78.35 | 42.73–113.97 | 0.556 |
| Nodular fasciitis | Benign | 3 | 29.14 | 23.79–32.67 | 0.778 |
| Ossifying fibromyxoid tumor | Intermediate | 8 | 8.24 | 5.41–14.03 | 0.917 |
| Osteosarcoma | Malignant | 2 | 18.46 | 18.23–18.70 | 0.778 |
| Pleomorphic hyalinizing angiectatic tumor | Intermediate | 2 | 14.24 | 8.22–20.25 | 0.889 |
| Pleomorphic liposarcoma | Malignant | 8 | 22.02 | 8.31–66.57 | 0.681 |
| Pseudomyogenic hemangioendothelioma | Intermediate | 4 | 23.95 | 19.00–32.40 | 0.750 |
| Rhabdomyosarcoma, NOS | Malignant | 1 | 18.72 | 18.72–18.72 | 0.778 |
| Rhabdomyosarcoma, alveolar | Malignant | 7 | 8.47 | 4.40–9.88 | 0.968 |
| Rhabdomyosarcoma, embryonal | Malignant | 11 | 9.28 | 6.37–13.14 | 0.929 |
| Rhabdomyosarcoma, sclerosing | Malignant | 2 | 27.67 | 21.16–34.18 | 0.778 |
| Schwannoma | Benign | 13 | 31.75 | 26.34–45.62 | 0.709 |
| Sclerosing epithelioid fibrosarcoma | Malignant | 8 | 7.29 | 6.08–10.84 | 0.944 |
| Sclerosing epithelioid fibrosarcoma-like | Malignant | 4 | 3.04 | 2.71–4.03 | 1.000 |
| Solitary fibrous tumor | Intermediate | 11 | 4.02 | 2.37–21.75 | 0.879 |
| Spindle cell tumor NOS | Intermediate;Malignant | 12 | 15.06 | 11.75–26.43 | 0.741 |
| Synovial chondromatosis | Benign | 6 | 100.65 | 59.99–195.56 | 0.278 |
| Synovial sarcoma | Malignant | 18 | 8.85 | 5.75–13.31 | 0.932 |
| Tenosynovial giant cell tumor | Benign | 12 | 18.20 | 12.91–20.00 | 0.824 |
| UPS | Malignant | 98 | 14.44 | 8.16–25.49 | 0.824 |
| Undifferentiated round cell sarcoma | Malignant | 2 | 20.98 | 17.29–24.67 | 0.778 |
