---
id: DOC-CHECKPOINT05-FOUNDATION-INDEPENDENT-SOURCE-REVIEW
title: Independent saved-response review of Foundation gene nomenclature companion
kind: memo
status: immutable
date: "2026-10-02"
last_verified: "2026-10-02"
purpose: Validate exact current HGNC evidence and event/slot bookkeeping.
scope: Frozen fifteen-event annotation and saved HGNC responses only.
audience: [maintainers, external reviewers]
---

The companion passes the bounded saved-source checks. All nine supported source-to-export pairs occur verbatim in the respective approved target record's prev_symbol array. They support 12 events and 13 changed gene slots; event 871 changes both slots. Fifteen events contain 30 slots: 13 previous-symbol supported, 9 unchanged, 5 missing-token convention, 2 unresolved numeric, and 1 unresolved exact-symbol conflict. Exact event order, worksheet rows, source IDs, ordered pairs, classifications, and selected HGNC fields match the supplied primary-check receipt and raw responses. No alias or fuzzy match is needed.

AKAP2 (HGNC:372) and PALM2AKAP2 (HGNC:33529) are distinct Approved current records, and AKAP2 is not an exact symbol/prev_symbol/alias_symbol match in the target record. Preserve the distinction without claiming unrelated biology: the raw AKAP2 locus_type is complex locus constituent, while the target is gene with protein product named PALM2 and AKAP2 fusion. Their shared accession/name context is not exact synonym evidence and does not identify the intended alteration. The existing cautious unresolved classification is appropriate.

The numeric strings 44621.0 and 44812.0 remain unresolved. MARCH1 and SEPT8 in target prev_symbol fields do not establish the numeric cells' intended genes. The new cell-format probe result was not available to this review; no date or source-encoding interpretation is made here.

Current support does not establish source-era nomenclature or validate any rearrangement. Raw symbol-change dates for C22orf46P and BMAL1 agree with the annotation. The findings' June 2022 article date was not independently verified within these permitted inputs; treat its comparison as conditional on the existing primary citation. No inference about intended genes, diagnosis, biological function, or experimental validation follows.

This review checked all saved raw/annotation hashes against the companion and retrieval receipts, excluding executable scripts being updated separately by root. It independently recomputed exact membership and event/slot classifications without calling the companion classifier. It did not reread the XLS or exports, so their preservation and primary extraction results remain receipt-based limits rather than fresh independent workbook/export validation. No input files were modified and no network, UI, runtime, checkout, or publication action occurred.
