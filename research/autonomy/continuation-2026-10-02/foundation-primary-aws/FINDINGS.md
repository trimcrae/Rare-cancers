---
id: DOC-CONTINUATION-20261002-FOUNDATION-PRIMARY-FINDINGS
title: Independent primary workbook confirmation of the Foundation identity correction
level: cross-cutting
kind: memo
status: live
purpose: Record executed primary-source confirmation and its limits.
scope: One frozen published workbook, mapping and historical/corrected export; source identity only.
audience: [maintainers, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

The previous independent Foundation job in run37011070408 timed out on a Europe PMC supplementary-files request. That failure remains unchanged. A newly evidenced [official PMC AWS object](https://pmc-oa-opendata.s3.amazonaws.com/PMC9200814.1/41467_2022_30496_MOESM2_ESM.xls) enabled a separate bounded retrieval and extraction in [run37035103326](https://github.com/trimcrae/Rare-cancers/actions/runs/37035103326/job/110931230146), revision83e0fb5348fe41b1747970d6346c6f3b19a3b5ea. Both subprocesses exited0. The 4,812,800byte workbook matched the historical SHA25688c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475 and metadata MD5.

The checker independently read both primary XLS sheets without importing the prior extractor or correction prototype. All3,771 rearrangement records matched the frozen mapping's ordinal, physical source row, source ID and source gene pair. All3,771 corrected IDs matched the directly extracted source IDs;3,770 original IDs differed. The records represent3,182 source IDs, not3,771 independent patients. All non-ID export fields and the complete event-multiplicity counter were preserved.

After the explicit missing-token convention,3,756 gene pairs agreed and15 differed. The full differences, including two numeric source gene cells, remain in the result. Passing the identity check does not establish gene-alias equivalence or repair these values. Source-label joins identify75 EMC profiles and76 events; the28 events selected by the original export suffix join originate from none of those source EMC IDs. These are source-label joins, not re-adjudicated clinical diagnoses. They apply to the pinned export and do not establish the state of a live portal or another release.

The primary extraction gap is closed for this frozen correction artifact. This is a data-quality/resource validation result, not a new biological assay result. An independent reviewer inspected the code and checked the returned hashes, exits, counters and differences; [review receipts](review/result-review.json) preserve the scope. The independent code path shares the xlrd2.0.1 file reader family with historical extraction.

Exact returned stdout/stderr and execution metadata are retained in results/. The summary ZIP digest was verified against GitHub. The raw workbook, original export, corrected export and mapping are retained in cloud artifact11239081000, SHA256e37eecc77a001f3265db074bb9f5a86ec3736752c855664d992bf00fc200db3b, through2026-11-01; no bulk workbook was downloaded locally. This retention is temporary, not permanent archival. The exact public source and hashes remain recorded; preserve the source bundle in the normal evidence archive before artifact expiry if longer retention is required.
