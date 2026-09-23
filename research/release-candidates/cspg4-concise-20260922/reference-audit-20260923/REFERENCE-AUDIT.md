# CSPG4 reference audit — 23 September 2026

All 19 original reference entries identify real sources. The audit checked bibliographic details, identifiers, claim support, dataset attribution, citation placement and indexed correction/retraction notices. Eight additional source leads in the supplement were also checked.

The audit found one material overstatement: the Wang antibody-study sentence generalized tumor-growth evidence from a cell line with disputed identity. The revised sentence uses the clearly supported culture-growth and experimental-lung-metastasis experiments. No numerical result or abstract wording changed.

## Corrections made

- Credited Möller 2011, the original GSE24369 publication, in place of a generic NCBI reference; retained accession/platform links in data availability.
- Narrowed the Wang 2010 claim to the relevant experiments.
- Replaced Efron 1979 with Efron 1987, whose percentile-interval discussion directly supports the stated method; reference count remains unchanged.
- Placed the HPA, 3SEQ and five-case PRAME citations beside the detailed claims.
- Added primary article DOIs to the Chaiboonchoe and ORIEN source leads and made author-list formatting consistent.

## Reference-by-reference findings

| Ref. | Source | Finding | Evidence |
|---|---|---|---|
| 1 | Dulken 2024 | Characteristic NR4A3 association is supported; the wording does not imply universal confirmation. | [Source](https://pubmed.ncbi.nlm.nih.gov/38447752/) |
| 2 | Yang 2004 | Melanoma-cell spreading and FAK/ERK signaling claims match the experimental study. | [Source](https://pmc.ncbi.nlm.nih.gov/articles/PMC2172406/) |
| 3 | Boudin 2022 | Sarcoma expression heterogeneity, prognosis and immune-feature associations are supported; normalized values remain distinct from TPM. | [Source](https://pmc.ncbi.nlm.nih.gov/articles/PMC9552405/) |
| 4 | Hofvander 2026 | 704 source patients and processing pipeline match. Zenodo record 17866629 identifies v1.0.1; selected 644/9/393 counts are this study's reanalysis. | [Source](https://pubmed.ncbi.nlm.nih.gov/41661217/) |
| 5 | Möller 2011 / GSE24369 | Replaced NCBI-only attribution with the original article explicitly linked by GEO. Six EMC and the listed comparator groups, GPL6244 and retained RMA/transcript-cluster mapping agree. GEO links retained in data availability. | [Source](https://pubmed.ncbi.nlm.nih.gov/21536545/) |
| 6 | Beale 2025 | Resource and log2(TPM+1) description match. Exact 25.01 release provenance resides in provider files/retained receipts, not an assumption about every release in the article. | [Source](https://www.nature.com/articles/s41597-025-05376-z) |
| 7 | Subramanian 2024 | GSE213065 links the study:87 profiles from 54 patients. Retained 54 T1a selection and Salmon TPM agree; T1 remains a timepoint, not proof of untreated primary disease. | [Source](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE213065) |
| 8 | Seligson 2024 | Exact published title uses "defines". The 34-case article subset and 69-record GEO source differ as already explained. FeatureCounts is the input; CPM is this reanalysis's transformation. | [Source](https://pubmed.ncbi.nlm.nih.gov/39213836/) |
| 9 | Geng 2025 | Published resource identity and RSEM gene TPM agree. Fresh v15 checksum manifest matches retained RDS MD5; the linked preprint is an earlier version, not a correction. | [Source](https://pmc.ncbi.nlm.nih.gov/articles/PMC12402770/) |
| 10 | Efron 1987 | Replaced valid general-bootstrap attribution Efron 1979 with a direct percentile-interval reference. Section 3, p. 173 defines the approximate percentile construction; this does not validate coverage in this small sample. | [Source](https://doi.org/10.1080/01621459.1987.10478410) |
| 11 | Wang 2010 | Corrected model-specific overstatement. MDA-MB-435 orthotopic growth experiments have disputed lineage; retained sentence describes breast-cancer cell growth in culture and experimental lung metastases from MDA-MB-231. | [Source](https://pmc.ncbi.nlm.nih.gov/articles/PMC2950168/) |
| 12 | Leuci 2020 | Culture and xenograft claims are supported. Named xenografts are S172 leiomyosarcoma, S1 UPS and HT1080fibrosarcoma; no EMC model is implied. | [Source](https://pmc.ncbi.nlm.nih.gov/articles/PMC7710537/) |
| 13 | NCI / NCT06096038 | Official registry confirms Phase I, recruiting, actual start 2024-04-05, latest update 2026-09-16 and no posted results. The existing phaseI/safety claim is supported. Access date updated. | [Source](https://clinicaltrials.gov/study/NCT06096038) |
| S1 | Renner 2013 | Primary taxonomy distinguishes UPS from pleomorphic liposarcoma. It supports the specific label correction, not blanket reassignment of every MFH record. | [Source](https://doi.org/10.1186/gb-2013-14-12-r137) |
| S2 | Uhlén 2015 | Tissue transcriptomics and IHC resource citation supports separation of assay types, not tumor surface density or therapeutic safety. Citation moved adjacent to the assay statement. | [Source](https://pubmed.ncbi.nlm.nih.gov/25613900/) |
| S3 | Thul 2017 | Subcellular immunofluorescence/resource citation is appropriate; cell-localization evidence remains distinct from tissue IHC/RNA. | [Source](https://pubmed.ncbi.nlm.nih.gov/28495876/) |
| S4 | Brunner 2012 | GSE28866 linkage and 3SEQ measurement type agree. Four library/STT records do not prove four unique patients. Citation now sits beside the measurement description. | [Source](https://doi.org/10.1186/gb-2012-13-8-r75) |
| S5 | Cammareri 2023 | Fresh supplementary workbook is byte-identical to retained source; rows 128–132 show five EMC negative in both readers with QR005. Four have molecular support; blanks remain blank. Citation moved beside the count. | [Source](https://doi.org/10.1007/s00428-023-03606-6) |
| S6 | Arbajian 2017 | Primary article states reuse of six EMC arrays; clinical-table case links support known historical overlap. Exact aliquot/EMC1–6 mappings remain unresolved, as stated. | [Source](https://doi.org/10.1158/1078-0432.CCR-17-1856) |

## Additional cited source leads

| Source | Finding | Evidence |
|---|---|---|
| GSE4303 | Ten EMC and 26 other sarcomas confirmed; two-color reference compatibility remains unresolved. | [Source](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE4303) |
| Watson2018 | Four EMC controls confirmed from author manuscript; EGA controlled raw reads remain the verified access route. No open processed matrix was recovered; this is not a universal absence claim. | [Source](https://doi.org/10.1002/path.5053) |
| Zullow2022 | Primary methods report seven EMC. Retained deposit audit identifies MLS/Ewing records, not recovered EMC measurements; no new dataset was obtained. | [Source](https://pmc.ncbi.nlm.nih.gov/articles/PMC9465545/) |
| Chaiboonchoe2026 | Twelve molecularly confirmed EMC in targeted TempO-Seq analysis; article DOI added alongside PRJNA1357027. No same-study non-EMC reference. | [Source](https://doi.org/10.7717/peerj.21497) |
| Racanelli2019 | Conference abstract reports 12 EMC and 7 myoepithelial tumors. No accession in the abstract; independence unresolved. | [Source](https://doi.org/10.1093/annonc/mdz283.054) |
| GSE6481 | Original diagnosis metadata says 19 myxoid liposarcomas, not EMC. | [Source](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE6481) |
| GSE71118 | 312 records include 303 explicit reanalysis aliases from GSE21050; new GSM identifiers do not imply new patients. | [Source](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE71118) |
| ORIEN | Publisher data-availability section requires a data request. Added the original study DOI; no request/contact made. | [Source](https://doi.org/10.1038/s41467-025-58678-6) |

## Notices, completeness and verification limits

Crossref metadata was retrieved for all 17 original journal DOIs, the two replacement articles and the newly specified Chaiboonchoe DOI. Fresh PubMed XML covered all 16 original biomedical articles, the Möller replacement and linked comments. No relevant retraction, expression of concern or linked correction was found in inspected records. This is an indexed-notice check, not a guarantee that no unindexed criticism exists.

The linked Uhlén/Thul comments are contextual commentary; Arbajian's linked letter reports a separate SEF/LGFMS case. Watson's commentary concerns classification. Geng's UpdateOf link points to its preprint. None is a correction invalidating the cited claim.

The bibliography has 13 main and 6 supplement entries, with no missing callouts, uncited entries, duplicate DOI entries or citations to the author's earlier preprints. Original source papers and version-specific repository evidence serve different roles: source-specific selected counts are this reanalysis's results, not necessarily the source article's whole-cohort totals.

Full-text verification used primary articles, deposited supplements and accessions, with indexed author text where publisher access was unavailable. Watson publisher access was limited; its author manuscript and EGA record were inspected. The original Efron 1979 scans had no machine-readable body text during the restricted device window; the replacement Efron 1987 percentile-method passage was inspected through indexed original-article text (p. 173, §3). No claim of complete visual inspection of those scanned articles is made. Existing unresolved donor/aliquot identities and controlled data access remain unresolved.

The corrected Markdown and prepared Word files require the already pending PDF render, all-page visual/text checks and exact-candidate normal preflight. Prior PDF acceptance does not apply to these edits. The existing daily 10:30 America/New_York watch retains that follow-through; no journal submission or provider preprint update occurred.
