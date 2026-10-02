---
id: "DOC-DATA-OPPORTUNITIES-2026-09-30-DRAFTS-FOUNDATION-SOURCE-IDENTITY-CORRESPONDENCE"
title: "A row-ordinal sample-ID transformation in a public sarcoma rearrangement export"
level: "L3"
kind: "manuscript"
status: "live"
canonical_for: []
purpose: "Working research draft: A row-ordinal sample-ID transformation in a public sarcoma rearrangement export."
scope: "September 30 measured-data campaign; retain the source qualifications, execution boundaries and historical status stated in the body."
audience: ["maintainers","external reviewers"]
date: "2026-09-30"
last_verified: "unverified"
_backfilled: "true"
---

# A row-ordinal sample-ID transformation in a public sarcoma rearrangement export

Public genomic datasets can preserve an alteration's genes while changing the identity of the sample to which it is assigned. We found such a transformation when comparing the primary supplementary workbook of a 7,494-profile sarcoma study with the corresponding cBioPortal Datahub structural-variant export.[1,2] The mismatch affects the linkage of rearrangement records to clinical samples, including extraskeletal myxoid chondrosarcoma (EMC). It does not demonstrate an error in the primary assay or a change in any diagnosis.

We compared every primary alteration_type=RE row, in source order, with every data_sv.txt row from public/sarcoma_msk_2022. The source workbook SHA-256 was 88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475. The export was the 180,393-byte Git LFS object d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701. We retained the original deidentified sample identifier, source worksheet row, one-based rearrangement-row ordinal, exported identifier and ordered gene pair. Gene differences were recorded literally; they were not silently normalized to make records match.

Both sources contained 3,771 rearrangement rows. For all 3,771 export rows, the numeric suffix of the exported sample identifier equaled the one-based rearrangement-row ordinal plus three (equivalently, the zero-based row index plus four). Only one suffix matched the original source sample identifier. Thus, 3,770 rows had discordant identifiers, involving 3,181 distinct original source identifiers and 3,770 distinct exported identifiers. This complete ordinal relationship explains the transformation independently of any interpretation of the altered genes.

The ordered gene pairs matched literally in 3,756 rows. The remaining 15 rows included the literal numeric source entries 44621 and 44812 and other literal symbol differences. Their biological equivalence was not assumed. The preservation of most gene pairs should therefore not be taken as evidence that sample linkage is preserved.

Two examples show why the difference matters (Table 1). A source EWSR1–NR4A3 rearrangement from sample 49 was exported under sample suffix 28. Two rearrangements belonging to source sample 245 were exported under suffixes 115 and 116. Consequently, one original sample can become multiple apparent samples in the rearrangement table. Selecting export rows by a clinical sample list can then attach events to different records or miss the original sample's events.

**Table 1. Literal sample identifiers in selected EMC source rearrangement rows.**

| One-based rearrangement ordinal | Source sample ID | Export sample ID | Source and export ordered gene pair |
|---:|---:|---|---|
| 25 | 49 | sarcoma_msk_2022-28 | EWSR1 / NR4A3 |
| 112 | 245 | sarcoma_msk_2022-115 | EWSR1 / NR4A3 |
| 113 | 245 | sarcoma_msk_2022-116 | NR4A3 / SASH1 |

These rows illustrate the measured transformation. They are not independent estimates of its frequency, and a reported gene pair alone does not establish an expressed functional fusion.

The primary workbook contained 75 distinct EMC source profiles and 76 rearrangement rows assigned to them. All 76 rearrangement rows had discordant export identifiers. Directly linked primary calls, rather than export identifiers, supported 63 EWSR1-partner and 12 TAF15-partner profiles. These counts describe this selected profiling series; they are not a population estimate of fusion-partner prevalence. The rare-disease example makes the linkage consequence visible without restricting the defect to EMC.

We used short variants as a limited identity control. All 43 primary EMC short-variant rows matched the corresponding export's source-ID/gene multiplicities after explicitly recognizing MRE11/MRE11A. This control did not validate complete alleles, coordinates or annotation changes. The primary material did not include matched normals and was agnostic to germline versus somatic origin; the export's Somatic labels do not supply that missing evidence. The control shows that the deterministic rearrangement identifier transformation was not shared by this separate record type.

A bounded current-source check performed on 1 October 2026 also found that the Datahub HEAD commit dated 28 September 2026 (dca75cb3f32b82d54a6f78bf0a6323e5b975aca1) still pointed to the identical rearrangement LFS object.[2] This verifies persistence in that source snapshot. It does not show which downstream studies, portal installations or cached analyses used the object, and we have not estimated their consequences.

The reproducible correction is to retain the primary sample identifier while assigning a separate event identifier to each rearrangement. Source worksheet rows and original identifiers should accompany any gene-symbol or coordinate transformation. Clinical linkage should then be checked independently from event-content concordance. For this dataset, the primary workbook permits that comparison directly; recovering identifiers from the affected export alone would instead assume information the export no longer preserves.

The finding is a source-to-export identity defect, not a reassessment of sarcoma biology. Its immediate implication is that analyses requiring sample-level rearrangement linkage should return to the primary identifiers until the derivative mapping is reconciled. Similar checks of original ID, event ordinal and independently retained alteration content can detect this kind of transformation in other public exports without requiring new laboratory work.

## Data and code availability

The complete comparisons, current-source pointer receipt, EMC rows and limited short-variant control are documented in [Foundation-complete-ID-proof-and-current-source.json](../deep-analysis/results/Foundation-complete-ID-proof-and-current-source.json) and [Foundation-complete-rearrangement-source-mapping.json](../deep-analysis/results/Foundation-complete-rearrangement-source-mapping.json). These artifacts preserve source hashes and literal differences. The source and export can be retrieved independently from the cited public records.

## References

1. Gounder MM et al. Clinical genomic profiling in the management of patients with soft tissue and bone sarcoma. Nature Communications. 2022;13:3406. [doi:10.1038/s41467-022-30496-0](https://doi.org/10.1038/s41467-022-30496-0). [PMID 35705558](https://pubmed.ncbi.nlm.nih.gov/35705558/). Numerical claims in this report refer to the hashed primary workbook, not to reconstructed export sample assignments.
2. cBioPortal Datahub. [Pinned sarcoma_msk_2022 source directory](https://github.com/cBioPortal/datahub/tree/dca75cb3f32b82d54a6f78bf0a6323e5b975aca1/public/sarcoma_msk_2022). The data_sv.txt Git LFS object identifier is stated above.
