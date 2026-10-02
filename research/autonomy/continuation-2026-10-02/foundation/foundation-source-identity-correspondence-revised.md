# A row-ordinal sample-ID transformation in a public sarcoma rearrangement export

Public genomic datasets can preserve an alteration's genes while changing the sample to which it is assigned. We found such a transformation between the primary supplementary workbook of a 7,494-profile sarcoma study and the corresponding cBioPortal Datahub structural-variant export.[1,2] It affects rearrangement linkage to clinical samples, including extraskeletal myxoid chondrosarcoma (EMC), without demonstrating an error in the primary assay or a changed diagnosis.

We compared every primary alteration_type=RE row, in source order, with every data_sv.txt row from public/sarcoma_msk_2022. The workbook SHA-256 was 88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475; the export was the 180,393-byte Git LFS object d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701. The comparison retained original deidentified sample IDs, source worksheet rows, rearrangement ordinals, exported IDs and ordered gene pairs.

Both sources contained 3,771 rearrangement rows. Every exported sample-ID suffix equaled the one-based rearrangement ordinal plus three. Only one matched the original sample ID. Thus, 3,770 rows had discordant IDs, involving 3,181 distinct original source IDs and 3,770 distinct exported IDs. The complete ordinal relationship establishes the identity transformation independently of gene interpretation.

Ordered gene pairs agreed in 3,756 rows after explicitly treating export N/A values as absent partners, represented as empty strings in the mapping. The prototype comparison encountered 564 such export tokens and retained them unchanged in its output. The other 15 rows included numeric source entries 44621 and 44812 and other symbol differences; biological equivalence was not assumed. Preserved alteration content therefore does not establish preserved sample linkage.

Source sample 49's EWSR1/NR4A3 event was exported under suffix 28. Two events from sample 245 were exported under separate suffixes 115 and 116 (Table 1). One original sample can therefore become multiple apparent samples in the rearrangement table.

**Table 1. Selected EMC source events and exported identifiers.**

| Rearrangement ordinal | Source sample ID | Export sample ID | Source and export ordered gene pair |
|---:|---:|---|---|
| 25 | 49 | sarcoma_msk_2022-28 | EWSR1 / NR4A3 |
| 112 | 245 | sarcoma_msk_2022-115 | EWSR1 / NR4A3 |
| 113 | 245 | sarcoma_msk_2022-116 | NR4A3 / SASH1 |

These examples illustrate the measured transformation; reported gene pairs alone do not establish expressed functional fusions.

The primary workbook contained 75 distinct EMC profiles and 76 rearrangement events, all with discordant export IDs. Direct primary linkage supported 63 EWSR1-partner and 12 TAF15-partner profiles, describing this selected series rather than population prevalence. A defined join using the 75 original EMC IDs with the export's study prefix retrieved 28 events, all originating outside the EMC source set, and none of its 76 events. Forty-seven original EMC IDs exceeded 3,774, the largest export suffix. This is a reproducible table-join consequence, not a live portal query or evidence of an affected downstream publication.

As a limited identity control, all 43 primary EMC short-variant rows matched export source-ID/gene multiplicities after explicitly recognizing MRE11/MRE11A. This did not validate complete alleles, coordinates or annotation changes. The primary material lacked matched normals and was agnostic to germline versus somatic origin; export Somatic labels do not establish that distinction.

Repository history places the ordinal relationship in a file revision dated 7 February 2024, before the public-release pull request was merged in June 2024.[3] The May 2024 release object and current object had identical sample IDs; seven rows differed in gene symbols. The identity transformation therefore predates the December 2024 symbol migration. The available records do not identify the originating operation or establish a portal deployment date. On 2 October 2026, Datahub HEAD, dated 28 September 2026, still referenced the affected object.[2] This establishes persistence in that repository snapshot, not its use by particular installations or analyses.

We prepared an offline recovery prototype bound to the exact export and complete mapping hashes. It restores original sample IDs while retaining separate event IDs and worksheet provenance. A [CLI replay](https://github.com/trimcrae/Rare-cancers/actions/runs/37009409052) preserved all 3,771 events, original sample multiplicities, and every non-ID export field, including the two events from source 245; four negative controls passed. This replay used the pinned derived mapping. A separate attempt to re-extract the primary workbook timed out during retrieval and remains unverified. This identity-only derivative retains gene symbols and Somatic labels without validating them; it is not an upstream-approved replacement. Subtracting three from an affected suffix recovers an event ordinal, not a sample ID.

Sample misannotation and gene-name corruption are established data-quality problems.[4,5] Our bounded prior-art search does not support a claim to first detection of such errors. The contribution here is the documented deterministic transformation, its explicit join consequence, and a reproducible recovery resource. The practical next step is maintainer reconciliation of the curation mapping, followed by verification of any corrected export. Sample-level rearrangement analyses should retain primary identifiers and check linkage separately from alteration content.

## Data and code availability

The frozen [complete proof](https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/Foundation-complete-ID-proof-and-current-source.json) and [complete mapping](https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/Foundation-complete-rearrangement-source-mapping.json) document source hashes, EMC rows and the limited short-variant control. The accompanying recovery prototype, replay receipt, history addendum and primary-source availability record distinguish completed mapping-based checks from the unverified fresh primary extraction and unperformed importer or live-portal validation. A maintainer-report draft has been prepared but not sent. No upstream correction or submission is claimed.

## References

1. Gounder MM et al. Clinical genomic profiling in the management of patients with soft tissue and bone sarcoma. Nature Communications. 2022;13:3406. [doi:10.1038/s41467-022-30496-0](https://doi.org/10.1038/s41467-022-30496-0).
2. cBioPortal Datahub. [Pinned sarcoma_msk_2022 directory](https://github.com/cBioPortal/datahub/tree/dca75cb3f32b82d54a6f78bf0a6323e5b975aca1/public/sarcoma_msk_2022). Repository snapshot checked 2 October 2026.
3. cBioPortal Datahub. [February file revision](https://github.com/cBioPortal/datahub/blob/6ad0f9e0a93b2814a9e3514bfea17a63f4a7ca7e/public/sarcoma_msk_2022/data_sv.txt), [public-release PR #2027](https://github.com/cBioPortal/datahub/pull/2027), and [December symbol-migration commit](https://github.com/cBioPortal/datahub/commit/45dcc57fb4007480207102cf48645c08c0c378ec).
4. Yoo S et al. A community effort to identify and correct mislabeled samples in proteogenomic studies. Patterns. 2021;2:100245. [doi:10.1016/j.patter.2021.100245](https://doi.org/10.1016/j.patter.2021.100245).
5. Abeysooriya M et al. Gene name errors: Lessons not learned. PLOS Computational Biology. 2021;17:e1008984. [doi:10.1371/journal.pcbi.1008984](https://doi.org/10.1371/journal.pcbi.1008984).
