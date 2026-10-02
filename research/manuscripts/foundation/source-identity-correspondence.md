---
id: DOC-FOUNDATION-SOURCE-IDENTITY-CORRESPONDENCE
title: A row-ordinal sample-ID transformation in a public sarcoma rearrangement export
level: L3
kind: manuscript
status: live
canonical_for: [Foundation sarcoma derivative export identity correspondence]
purpose: Report the complete primary-source mapping and disease-specific join consequence of one pinned derivative export identity defect.
scope: Source identity and literal annotation comparison only; no assay revalidation, clinical outcome inference, or confirmed upstream correction.
audience: [external reviewers, collaborators, maintainers]
date: 2026-10-02
last_verified: 2026-10-02
related: []
---

# A row-ordinal sample-ID transformation in a public sarcoma rearrangement export

**Author.** Tristan D. McRae

**Running title.** Sample identity in a sarcoma export

**Keywords.** sarcoma; sample identity; structural variation; data curation; extraskeletal myxoid chondrosarcoma

## Abstract

Public cancer datasets can retain the reported gene alteration while assigning it to the wrong sample. We compared all 3,771 rearrangement records in a published sarcoma workbook with a corresponding cBioPortal Datahub export. In every export row, the numeric sample-ID suffix equaled the rearrangement's position counted from one, plus three; 3,770 identifiers differed from their source identifiers. An independent extraction of the original workbook confirmed the complete mapping and an identity-only recovery. Selecting export records using the 75 original extraskeletal myxoid chondrosarcoma identifiers retrieved 28 events originating outside that source group and none of its 76 events. Separate gene-text discrepancies remain explicitly qualified. This is an export-linkage defect, not evidence that the original assays, diagnoses or study conclusions were wrong. The reproducible mapping provides a basis for curator correction, but no corrected deployment or effect on downstream studies has been established.

## Correspondence

A genomic alteration can retain its reported genes while losing its link to the sample in which it was measured. We identified this problem in the cBioPortal Datahub rearrangement export associated with a 7,494-profile sarcoma study.[1,2] We compared the export with the study's primary supplementary workbook and recovered the original sample identifiers.

We compared all rows marked `alteration_type=RE` in the workbook with all rows in the export, retaining their source order. For each event, we recorded the original sample ID, physical worksheet row, rearrangement ordinal, exported sample ID and ordered gene pair. File hashes fixed the identity of both sources. A separate extraction read the original workbook without using the first extractor or the recovery program. The two code paths used the same xlrd reader family, so they were not independent tests of the file-format parser.[7]

All 3,771 export suffixes equaled the one-based rearrangement ordinal plus three. Only one matched its original source sample ID; the remaining 3,770 were discordant. The events belonged to 3,182 source identifiers, rather than 3,771 independently verified patients. The second extraction confirmed every original ID, worksheet row and gene pair in the complete mapping. It also confirmed that every recovered ID matched the primary workbook.

Two source samples illustrate the consequence (Table 1). Sample 49's EWSR1/NR4A3 event was assigned to export suffix 28. Sample 245's two events were assigned to separate suffixes, making one source sample appear as two export samples. Subtracting three from an export suffix recovers the event ordinal, not the original sample ID.

**Table 1. Selected source events and their exported sample identifiers.**

| Rearrangement ordinal | Original sample ID | Export sample ID | Ordered gene pair |
|---:|---:|---|---|
| 25 | 49 | sarcoma_msk_2022-28 | EWSR1 / NR4A3 |
| 112 | 245 | sarcoma_msk_2022-115 | EWSR1 / NR4A3 |
| 113 | 245 | sarcoma_msk_2022-116 | NR4A3 / SASH1 |

These are illustrative records from the complete comparison. A reported gene pair does not establish an expressed functional fusion.

The discrepancy changes which events a disease-specific join retrieves. The primary workbook contained 75 profiles labelled extraskeletal myxoid chondrosarcoma (EMC), with 76 rearrangement events. All 76 had discordant export IDs. Prefixing the 75 original IDs with `sarcoma_msk_2022-` and selecting the matching export rows retrieved 28 events. None originated from those 75 source EMC IDs, and none of the 76 source EMC events was retrieved. Forty-seven original EMC IDs exceeded 3,774, the largest export suffix. These results describe a defined table join, not a live portal query or a clinical reassessment of the source labels.

Gene-text differences require a separate interpretation. Ordered gene pairs agreed in 3,756 events after treating exported `N/A` partner values as missing. Fifteen events retained differences. Current HGNC previous-symbol records support 12 of these events, involving nine distinct textual symbol pairs and 13 changed gene slots.[4,7] This supports present-day nomenclature correspondence, not the source-era annotation or the biological identity of a rearrangement.

The remaining three events are unresolved. Two primary gene cells contained 44621.0 and 44812.0; inspection confirmed that both are stored as dates with a day-month display format. They encode 1 March and 8 September 2022, respectively. These dates do not establish the intended genes, and we did not replace them with the export's MARCHF1 or SEPTIN8 labels. The third difference, AKAP2 versus PALM2AKAP2, involves distinct approved HGNC records without an exact previous-symbol or alias match. Their relationship at a complex locus does not resolve the intended annotation. These uncertainties do not change the independently verified sample-ID mapping.

The identity transformation was already present in an inspected February 2024 file revision, before the release pull request merged in June 2024.[3] It predates the December 2024 gene-symbol migration. The affected export remained in the repository snapshot checked on 2 October 2026.[2] These observations neither identify the operation that created the transformation nor establish when a portal deployed it.

The recovery program changes sample identifiers while preserving all events, their original sample multiplicities and every non-ID export field. That includes all 564 exported `N/A` tokens and the unresolved gene annotations. The recovered derivative is therefore a resource for curator reconciliation, not an approved replacement or validation of those annotations. Gene pairs, export `Somatic` labels and source diagnoses were not independently validated. The primary material lacked matched normals and did not distinguish germline from somatic origin.

Sample misannotation and gene-name corruption are established data-quality problems.[5,6] This report documents a specific deterministic transformation, its complete source mapping and its consequence for a defined EMC join. It does not challenge the original study's assays or scientific conclusions. We have not established an effect on downstream publications, clinical decisions or patient outcomes. The practical next step is reconciliation with the data maintainers and verification of any resulting export. Sample-level analyses should retain primary identifiers and check their linkage separately from alteration content.

## Data and code availability

The primary workbook is Supplementary Data 1 of Gounder et al.[1] Its SHA-256 is `88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475`. The analyzed export is pinned to the Datahub snapshot in reference 2; its SHA-256 is `d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701`. The complete mapping, recovery code, independent primary-source comparison, history and gene-annotation evidence are available in the versioned research repository.[7] The recovery preserves the export's non-ID fields and does not certify compatibility with an importer or a live portal. No upstream correction or corrected deployment is claimed.

## Source licenses

The original article is licensed under CC BY 4.0, subject to the publisher's stated exceptions for third-party material.[1] The [Datahub README](https://github.com/cBioPortal/datahub/blob/dca75cb3f32b82d54a6f78bf0a6323e5b975aca1/README.md#license) specifies ODbL 1.0 for its data. Any shared or adapted Datahub dataset must retain the applicable ODbL terms; the identity-corrected derivative is not relabeled CC BY or CC0.

## AI assistance

OpenAI Codex agents assisted with source retrieval, code development, data checks, drafting and revision. A separate agent reviewed the manuscript against the recorded evidence. These computational checks do not replace author responsibility for the final manuscript.

## Funding

This research received no funding.

## Competing interests

The author declares no competing interests.

## References

1. Gounder MM, et al. Clinical genomic profiling in the management of patients with soft tissue and bone sarcoma. *Nature Communications*. 2022;13:3406. [doi:10.1038/s41467-022-30496-0](https://doi.org/10.1038/s41467-022-30496-0).
2. cBioPortal Datahub. *sarcoma_msk_2022*. Repository snapshot `dca75cb3f32b82d54a6f78bf0a6323e5b975aca1`, checked 2 October 2026. [Pinned dataset](https://github.com/cBioPortal/datahub/tree/dca75cb3f32b82d54a6f78bf0a6323e5b975aca1/public/sarcoma_msk_2022).
3. cBioPortal Datahub. [February 2024 file revision](https://github.com/cBioPortal/datahub/blob/6ad0f9e0a93b2814a9e3514bfea17a63f4a7ca7e/public/sarcoma_msk_2022/data_sv.txt), [release pull request 2027](https://github.com/cBioPortal/datahub/pull/2027), and [December 2024 gene-symbol migration](https://github.com/cBioPortal/datahub/commit/45dcc57fb4007480207102cf48645c08c0c378ec).
4. HUGO Gene Nomenclature Committee. [HGNC REST web-service documentation](https://www.genenames.org/help/rest/). Exact responses retrieved 2 October 2026 are preserved in reference 7.
5. Yoo S, et al. A community effort to identify and correct mislabeled samples in proteogenomic studies. *Patterns*. 2021;2:100245. [doi:10.1016/j.patter.2021.100245](https://doi.org/10.1016/j.patter.2021.100245).
6. Abeysooriya M, et al. Gene name errors: Lessons not learned. *PLOS Computational Biology*. 2021;17:e1008984. [doi:10.1371/journal.pcbi.1008984](https://doi.org/10.1371/journal.pcbi.1008984).
7. EMC research repository. [Complete source mapping](https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/Foundation-complete-rearrangement-source-mapping.json) and [original proof](https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/Foundation-complete-ID-proof-and-current-source.json); [recovery and history](https://github.com/trimcrae/Rare-cancers/tree/2ef13e753e3a666015e6942bc644964ae31a6c94/research/autonomy/continuation-2026-10-02/foundation); [independent primary-workbook confirmation](https://github.com/trimcrae/Rare-cancers/tree/2ef13e753e3a666015e6942bc644964ae31a6c94/research/autonomy/continuation-2026-10-02/foundation-primary-aws); [gene-annotation evidence](https://github.com/trimcrae/Rare-cancers/tree/2ef13e753e3a666015e6942bc644964ae31a6c94/research/autonomy/continuation-2026-10-02/foundation-gene-annotation).

