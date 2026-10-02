---
id: DOC-FOUNDATION-PREP-HG-MANUSCRIPT
title: Foundation sarcoma correspondence for Human Genetics
kind: manuscript
status: draft
audience: [maintainers, external reviewers]
date: 2026-10-02
last_verified: 2026-10-02
---

# A row-ordinal sample-ID transformation in a public sarcoma rearrangement export

**Author.** Tristan D. McRae

Independent researcher, unaffiliated. Correspondence: trimcrae@gmail.com. ORCID: 0000-0002-1823-1451.

**Running title.** Sample identity in a sarcoma export

**Keywords.** sarcoma; sample identity; structural variation; data curation; extraskeletal myxoid chondrosarcoma

## Abstract

Public cancer datasets can retain the reported gene alteration while assigning it to the wrong sample. We compared all 3,771 rearrangement records in a published sarcoma workbook with a corresponding cBioPortal Datahub export. In every export row, the numeric sample-ID suffix equaled the rearrangement's position counted from one, plus three; 3,770 identifiers differed from their source identifiers. An independent extraction of the original workbook confirmed the complete mapping and an identity-only recovery. Selecting export records using the 75 original extraskeletal myxoid chondrosarcoma identifiers retrieved 28 events originating outside that source group and none of its 76 events. The reconstruction assumes that the export retained source event order. Repeated gene pairs do not independently establish unique event identity. Fifteen literal gene-pair discrepancies were considered separately from the sample identifiers; three remain unresolved. This is an export-linkage defect, not evidence that the original assays, diagnoses or study conclusions were wrong. The reproducible mapping provides a basis for curator correction, but no corrected deployment or effect on downstream studies has been established.

## Introduction

A genomic alteration can retain its reported genes while losing its link to the sample in which it was measured. We identified this problem in the cBioPortal Datahub rearrangement export associated with a 7,494-profile sarcoma study (Gounder et al. 2022; cBioPortal Datahub 2026). We compared the export with the study's primary supplementary workbook and recovered the original sample identifiers.

## Correspondence

We compared all rows marked `alteration_type=RE` in the workbook with all rows in the export, retaining their source order. For each event, we recorded the original sample ID, physical worksheet row, rearrangement ordinal, exported sample ID and ordered gene pair. File hashes fixed the identity of both sources. This reconstruction assumes that the export retained the workbook's event order; repeated gene pairs do not establish unique event identity. A separate extraction read the original workbook without using the first extractor or the recovery program. The two code paths used the same xlrd reader family, so they were not independent tests of the file-format parser (McRae 2026).

All 3,771 export suffixes equaled the one-based rearrangement ordinal plus three. Only one matched its original source sample ID; the remaining 3,770 were discordant. The events belonged to 3,182 source identifiers, rather than 3,771 independently verified patients. The second extraction confirmed every original ID, worksheet row and gene pair in the complete mapping. It also confirmed that every recovered ID matched the primary workbook.

Two source samples illustrate the consequence (Table 1). Sample 49's EWSR1/NR4A3 event was assigned to export suffix 28. Sample 245's two events were assigned to separate suffixes, making one source sample appear as two export samples. Subtracting three from an export suffix recovers the event ordinal, not the original sample ID.

**Table 1. Selected source events and their exported sample identifiers.** Source: Gounder et al. (2022), Supplementary Data 1, and cBioPortal Datahub (2026), aligned by retained event order.

| Rearrangement ordinal | Original sample ID | Export sample ID | Ordered gene pair |
|---:|---:|---|---|
| 25 | 49 | sarcoma_msk_2022-28 | EWSR1 / NR4A3 |
| 112 | 245 | sarcoma_msk_2022-115 | EWSR1 / NR4A3 |
| 113 | 245 | sarcoma_msk_2022-116 | NR4A3 / SASH1 |

These are illustrative records from the complete comparison. A reported gene pair does not establish an expressed functional fusion.

The discrepancy changes which events a disease-specific join retrieves. The primary workbook contained 75 profiles labelled extraskeletal myxoid chondrosarcoma (EMC), with 76 rearrangement events. All 76 had discordant export IDs. Prefixing the 75 original IDs with `sarcoma_msk_2022-` and selecting the matching export rows retrieved 28 events. None originated from those 75 source EMC IDs, and none of the 76 source EMC events was retrieved. Forty-seven original EMC IDs exceeded 3,774, the largest export suffix. These results describe a defined table join, not a live portal query or a clinical reassessment of the source labels.

Gene-text differences require a separate interpretation. Ordered gene pairs agreed in 3,756 events after treating exported `N/A` partner values as missing. Fifteen events retained differences. Current HUGO Gene Nomenclature Committee (HGNC) previous-symbol records support 12 of these events, involving nine distinct textual symbol pairs and 13 changed gene slots (HGNC 2026; McRae 2026). This supports present-day nomenclature correspondence, not the source-era annotation or the biological identity of a rearrangement.

The remaining three events are unresolved. Two primary gene cells contained 44621.0 and 44812.0; inspection confirmed that both are stored as dates with a day-month display format. They encode 1 March and 8 September 2022, respectively. These dates do not establish the intended genes, and we did not replace them with the export's MARCHF1 or SEPTIN8 labels. The third difference, AKAP2 versus PALM2AKAP2, involves distinct approved HGNC records without an exact previous-symbol or alias match. Their relationship at a complex locus does not resolve the intended annotation. These uncertainties do not change the independently verified sample-ID mapping.

The identity transformation was already present in an inspected February 2024 file revision, before the release pull request merged in June 2024 (cBioPortal Datahub 2024). It predates the December 2024 gene-symbol migration. The affected export remained in the repository snapshot checked on 2 October 2026 (cBioPortal Datahub 2026). These observations neither identify the operation that created the transformation nor establish when a portal deployed it.

The recovery program changes sample identifiers while preserving all events, their original sample multiplicities and every non-ID export field. That includes all 564 exported `N/A` tokens and the unresolved gene annotations. The recovered derivative is therefore a resource for curator reconciliation, not an approved replacement or validation of those annotations. Gene pairs, export `Somatic` labels and source diagnoses were not independently validated. The primary material lacked matched normals and did not distinguish germline from somatic origin.

Sample misannotation and gene-name corruption are established data-quality problems (Yoo et al. 2021; Abeysooriya et al. 2021). This report documents a specific deterministic transformation, its complete source mapping and its consequence for a defined EMC join. It does not challenge the original study's assays or scientific conclusions. We have not established an effect on downstream publications, clinical decisions or patient outcomes. The practical next step is reconciliation with the data maintainers and verification of any resulting export. Sample-level analyses should retain primary identifiers and check their linkage separately from alteration content.

## References

Abeysooriya M, et al. (2021) Gene name errors: Lessons not learned. PLOS Computational Biology 17:e1008984. https://doi.org/10.1371/journal.pcbi.1008984

cBioPortal Datahub (2024) Sarcoma export history: [February file revision](https://github.com/cBioPortal/datahub/blob/6ad0f9e0a93b2814a9e3514bfea17a63f4a7ca7e/public/sarcoma_msk_2022/data_sv.txt), [release pull request 2027](https://github.com/cBioPortal/datahub/pull/2027), and [December gene-symbol migration](https://github.com/cBioPortal/datahub/commit/45dcc57fb4007480207102cf48645c08c0c378ec). Accessed 2 October 2026.

cBioPortal Datahub (2026) sarcoma_msk_2022. [Repository snapshot dca75cb3f32b82d54a6f78bf0a6323e5b975aca1](https://github.com/cBioPortal/datahub/tree/dca75cb3f32b82d54a6f78bf0a6323e5b975aca1/public/sarcoma_msk_2022). Accessed 2 October 2026.

Gounder MM, et al. (2022) Clinical genomic profiling in the management of patients with soft tissue and bone sarcoma. Nature Communications 13:3406. https://doi.org/10.1038/s41467-022-30496-0

HGNC (2026) HUGO Gene Nomenclature Committee [REST web-service documentation](https://www.genenames.org/help/rest/). Exact responses retrieved 2 October 2026 are preserved in McRae (2026).

McRae TD (2026) Foundation sarcoma source-identity reconstruction and reproducibility records. [Versioned research repository, revision 5d2f2e2116f43c0bb56a46120902a1332f27720b](https://github.com/trimcrae/Rare-cancers/tree/5d2f2e2116f43c0bb56a46120902a1332f27720b/research/autonomy/continuation-2026-10-02/foundation-publication). Companion directories contain the [identity recovery](https://github.com/trimcrae/Rare-cancers/tree/5d2f2e2116f43c0bb56a46120902a1332f27720b/research/autonomy/continuation-2026-10-02/foundation), [independent source confirmation](https://github.com/trimcrae/Rare-cancers/tree/5d2f2e2116f43c0bb56a46120902a1332f27720b/research/autonomy/continuation-2026-10-02/foundation-primary-aws) and [gene annotation evidence](https://github.com/trimcrae/Rare-cancers/tree/5d2f2e2116f43c0bb56a46120902a1332f27720b/research/autonomy/continuation-2026-10-02/foundation-gene-annotation). Accessed 2 October 2026.

Yoo S, et al. (2021) A community effort to identify and correct mislabeled samples in proteogenomic studies. Patterns 2:100245. https://doi.org/10.1016/j.patter.2021.100245

## Statements and Declarations

### Data and code availability

The primary workbook is Supplementary Data 1 of Gounder et al. (2022). The analyzed Datahub export is fixed at the snapshot in cBioPortal Datahub (2026). Exact input bytes, the complete mapping and identity-corrected export are preserved in [primary-inputs.zip](https://github.com/trimcrae/Rare-cancers/blob/5d2f2e2116f43c0bb56a46120902a1332f27720b/research/autonomy/continuation-2026-10-02/foundation-publication/primary-inputs.zip), with member hashes and attribution in [source-archive.json](https://github.com/trimcrae/Rare-cancers/blob/5d2f2e2116f43c0bb56a46120902a1332f27720b/research/autonomy/continuation-2026-10-02/foundation-publication/source-archive.json). Recovery code, independent confirmation and gene-text evidence are versioned in McRae (2026). Online Resource 1 describes the files, offline reproduction and limitations. The [reproducibility package](https://github.com/trimcrae/Rare-cancers/blob/c29f301be3c90c9355b04501ff4ae43ab2199c67/research/autonomy/continuation-2026-10-02/foundation-publication/preparation-2026-10-02/reproducibility.zip) and [offline instructions](https://github.com/trimcrae/Rare-cancers/blob/c29f301be3c90c9355b04501ff4ae43ab2199c67/research/autonomy/continuation-2026-10-02/foundation-publication/preparation-2026-10-02/README-reproduction.txt) preserve these inputs and scripts with separate source licences. The proposed derivative preserves non-ID fields; no importer compatibility, maintainer approval or corrected live deployment is claimed.

### Source licences

Primary-source content retains the article's CC BY 4.0 terms and any stated third-party exceptions. Datahub data and the adapted database retain ODbL 1.0, including applicable attribution and share-alike obligations; they are not offered under a publisher-exclusive article licence or relabeled CC BY or CC0. Original repository code retains its Apache 2.0 licence. Third-party content is not relicensed by the archive wrapper. Source notices are available from [the primary article](https://www.nature.com/articles/s41467-022-30496-0), [Datahub](https://github.com/cBioPortal/datahub/blob/dca75cb3f32b82d54a6f78bf0a6323e5b975aca1/README.md#license) and [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).

### AI assistance

OpenAI Codex agents assisted with source retrieval, code development, data checks, drafting and revision. A separate agent reviewed the manuscript against the recorded evidence. These computational checks do not replace author responsibility for the final manuscript.

### Funding

This research received no funding.

### Competing interests

The author declares no competing interests.

### Author contribution

Tristan D. McRae directed the research and is the sole named author. The AI assistance is disclosed above.

### Ethics and consent

This work compares public, previously released source tables and repository exports. No participants were recruited and no new specimens or measurements were collected. No new ethics approval, exemption or consent determination is claimed.

### Supplementary information

Online Resource 1. Reproducibility guide for the pinned sarcoma source-identity comparison, including source attribution, archive inventory, offline commands and the retained event-order assumption. The database files remain in the separately licensed repository package.
