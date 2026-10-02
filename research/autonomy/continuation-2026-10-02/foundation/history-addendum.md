---
id: "DOC-CONTINUATION-2026-10-02-FOUNDATION-HISTORY-ADDENDUM"
title: "Foundation source-identity history addendum"
level: "cross-cutting"
kind: "memo"
status: "live"
canonical_for: []
purpose: "Record the scoped evidence and reasoning for Foundation source-identity history addendum."
scope: "October 2 continuation; limited to the named sources, computations and review scope recorded in the body. No submission clearance."
audience: ["maintainers","autonomous research agents"]
date: "2026-10-02"
last_verified: "unverified"
_backfilled: "true"
---

# Foundation source-identity history addendum

Checked 2 October 2026 using quiet read-only HTTPS/API requests. No portal query,
contacts, issue posting, or submission was performed.

## Repository provenance

- The curation issue was opened 11 October 2023. Its 17 October 2023 comment
  identifies supplementary dataset 1, sheet 2 for clinical data and sheet 1 for
  mutation data, and reports requesting SV/RNA/CNA/clinical files. This records
  curation context; it does not identify the actual transformation script or
  establish that every exported SV came only from the public workbook.
  https://github.com/cBioPortal/datahub/issues/1937#issuecomment-1766599592
- Earliest discovered file commit: 6ad0f9e0a93b2814a9e3514bfea17a63f4a7ca7e,
  dated 2024-02-07T17:13:51Z. Its pointer matches the equivalent PR #2005 head
  bea7fb1a5fae55236173965a337e9bcd7e1424c3, whose payload was fetched in memory.
  Verified 184160 bytes and SHA256
  00d055161e509c37fe92878a33084d702012a18405a3a094dca8b13e54993f9a.
  All 3771 suffixes already equal rearrangement ordinal plus three. Historical
  prefix is Sarcoma_msk_2022- (capital S).
  https://github.com/cBioPortal/datahub/blob/6ad0f9e0a93b2814a9e3514bfea17a63f4a7ca7e/public/sarcoma_msk_2022/data_sv.txt
  https://github.com/cBioPortal/datahub/pull/2005
- Initial file commit in current mainline history:
  b04d967a8c6436e2c5208c4e1ab9a508302aae0f, 2024-05-02T21:23:47Z.
  Verified payload: 180387 bytes; SHA256
  c1226c70a50e45e8c7edad6ee95740843216cd1e6dd64e363a09fa7d67ffd14e.
  All 3771 IDs preserve the ordinal relationship.
  https://github.com/cBioPortal/datahub/blob/b04d967a8c6436e2c5208c4e1ab9a508302aae0f/public/sarcoma_msk_2022/data_sv.txt
- Release PR #2027 merged 2024-06-05T21:33:05Z. The May commit date is not an
  established public portal deployment date.
  https://github.com/cBioPortal/datahub/pull/2027
- Gene migration commit 45dcc57fb4007480207102cf48645c08c0c378ec, dated
  2024-12-26T20:05:54Z, PR #2117. May/current full-payload comparison found
  zero sample-ID changes and seven gene-symbol rows changed:
  412 C22orf46->C22orf46P; 908 LINC00476->ERCC6L2-AS1;
  1922 SLC26A10->SLC26A10P; 2160 ARNTL->BMAL1;
  2342 BTBD11->ABTB3; 3204 KIAA0100->BLTP2; 3317 AKAP2->PALM2AKAP2.
  These observed textual differences do not independently validate biological
  equivalence. The identity transformation predates this migration.
  https://github.com/cBioPortal/datahub/commit/45dcc57fb4007480207102cf48645c08c0c378ec
- Current HEAD remained dca75cb3f32b82d54a6f78bf0a6323e5b975aca1,
  dated 2026-09-28T16:00:37Z. Independently fetched current payload verifies
  180393 bytes and SHA256
  d9fc3fc8073104c3f364825972921f271b5e8793eefcf71331c3cff7d3882701.
  No source-repository correction detected in this snapshot. This does not
  establish which installations or cached analyses use that object.
  https://api.github.com/repos/cBioPortal/datahub/commits/master

## Small manuscript insertion

Repository history places the ordinal-ID relationship in a file revision dated
7 February 2024, before its public-release PR was merged in June 2024. The May
2024 release object and current object contain identical sample identifiers;
seven rows differ in gene symbols. Thus, the identity transformation predates
the December 2024 gene-symbol migration. The available records do not identify
the originating operation or establish a portal deployment date.

A defined join using the 75 original EMC IDs retrieves 28 export events, all
originating outside that EMC source set, and none of its 76 source events.
Forty-seven original EMC IDs exceed the maximum exported suffix. This is a
frozen-table join consequence, not a demonstrated effect on a downstream paper.

## Prior art and publication channel

Do not claim novelty of sample-misannotation detection. Relevant primary work:

- Lohr et al. (2015), Identification of sample annotation errors in gene
  expression datasets. https://doi.org/10.1007/s00204-015-1632-4
- Yoo et al. (2021), A community effort to identify and correct mislabeled
  samples in proteogenomic studies. https://pubmed.ncbi.nlm.nih.gov/34036290/
  DOI https://doi.org/10.1016/j.patter.2021.100245
- Abeysooriya et al. (2021), Gene name errors: Lessons not learned.
  https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008984
  This contextualizes five-digit gene entries, but does not establish the cause
  of this sample-ID defect.

A bounded web/official-repository issue-and-PR search found curation/release
records, not an existing report of this particular defect. That search is not
an exhaustive novelty assessment.

The immediate useful channel is a reproducible Datahub defect report.
The official FAQ directs suspected dataset errors to maintainers:
https://docs.cbioportal.org/user-guide/faq/

Nature Communications Matters Arising guidance allows concise post-publication
discussion and encourages prior contact with original authors. Cases that only
identify an error may instead lead to a clarification. This case currently
establishes a derivative-export defect, not a scientific error in the original
article, so journal fit remains uncertain. No manuscript should be described as
submission-ready from these checks.
https://www.nature.com/ncomms/submit/matters-arising

Finite next action: preserve and independently check the corrective prototype
and provenance, then resolve actual curation transformation or an upstream fix.
Do not repeat the completed original all-row proof merely for another review.
