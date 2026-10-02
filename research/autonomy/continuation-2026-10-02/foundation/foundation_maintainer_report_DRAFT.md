---
id: "DOC-CONTINUATION-2026-10-02-FOUNDATION-FOUNDATION-MAINTAINER-REPORT-DRAFT"
title: "DRAFT — not sent"
level: "cross-cutting"
kind: "memo"
status: "live"
canonical_for: []
purpose: "Record the scoped evidence and reasoning for DRAFT — not sent."
scope: "October 2 continuation; limited to the named sources, computations and review scope recorded in the body. No submission clearance."
audience: ["maintainers","autonomous research agents"]
date: "2026-10-02"
last_verified: "unverified"
_backfilled: "true"
---

# DRAFT — not sent

Subject: Reproducible sample-ID mismatch in sarcoma_msk_2022/data_sv.txt

We found a deterministic sample-ID discrepancy between the primary supplementary
workbook of Gounder et al. (Nature Communications 2022, doi:10.1038/s41467-022-30496-0)
and the Datahub sarcoma_msk_2022 rearrangement export.

The affected current export is the 180,393-byte LFS object
d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701,
still referenced by Datahub commit
dca75cb3f32b82d54a6f78bf0a6323e5b975aca1 when checked on 2 October 2026.

Across 3,771 rearrangement rows, each exported sample-ID suffix equals the
one-based rearrangement-row ordinal plus three. Only one matches the original
source sample ID. Source sample 49's EWSR1/NR4A3 event appears under suffix 28.
Two source-245 events appear separately under suffixes 115 and 116.

The relationship is already present in the earliest file revision we found,
6ad0f9e0a93b2814a9e3514bfea17a63f4a7ca7e (7 February 2024). Comparing the
May 2024 release object with the current object found no changed sample IDs;
the seven changed rows involve gene symbols. This bounds the discrepancy
before the December 2024 symbol migration. We have not identified its
originating script or established a portal deployment date.

An explicit join using the 75 original EMC sample IDs retrieves 28 export
events, all originating outside that EMC source set, and none of its 76 source
events. Forty-seven original EMC IDs exceed the export's maximum suffix.
This is a frozen-table calculation, not evidence of a particular affected
downstream publication.

We prepared an offline identity-only recovery prototype. It requires exact
SHA-256 matches for the export and complete source mapping, preserves all
3,771 events and their original sample multiplicities, and changes only
Sample_Id. The output is an investigational derivative, not an upstream-approved
replacement. It retains export gene symbols and SOMATIC labels without claiming
to validate them. The primary study lacked matched-normal validation.

The mapping has 564 absent-gene values represented as empty strings where the
TSV uses N/A; the prototype explicitly handles that comparison convention and
retains the original TSV values.

Could you help identify the original transformation and reconcile the mapping?
The historical curation record is:
https://github.com/cBioPortal/datahub/issues/1937

Primary paper:
https://doi.org/10.1038/s41467-022-30496-0

Pinned Datahub source:
https://github.com/cBioPortal/datahub/tree/dca75cb3f32b82d54a6f78bf0a6323e5b975aca1/public/sarcoma_msk_2022

Complete mapping:
https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/Foundation-complete-rearrangement-source-mapping.json

This report concerns source-to-export identity linkage. It does not establish
an error in the primary assay, a changed diagnosis, or clinical consequences.
