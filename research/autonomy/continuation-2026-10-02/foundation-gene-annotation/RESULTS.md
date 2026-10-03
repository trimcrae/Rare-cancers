---
id: DOC-CHECKPOINT05-FOUNDATION-COMPLETED-RESULT
title: "Source-qualified gene-text differences"
kind: memo
status: live
date: "2026-10-02"
last_verified: "2026-10-02"
purpose: "Record the bounded checkpoint result and its evidence."
audience: [maintainers, autonomous research agents]
scope: "Named public sources and exact computations; no publication clearance."
---

This annotation companion leaves the verified sample-identity correction unchanged. Current HGNC previous-symbol fields support 12 of the 15 retained discrepant events, comprising nine unique textual symbol pairs and 13 changed gene slots. Two numeric source cells and the AKAP2 versus PALM2AKAP2 discrepancy remain unresolved. Current nomenclature support does not establish the source-era identifier or experimentally validate a gene assignment.

The [new two-cell cloud probe](https://github.com/trimcrae/Rare-cancers/actions/runs/37041943656) read the independently verified original workbook, SHA256 88c1a0bab7509ffe3bcff955b89f3d60ddb58a68311cd4c56ca4b0c78506b475. At Excel rows 8570 and 20794, both numeric partner values are stored as XLS date cells (xlrd ctype 3), format d-mmm, datemode 0. Values 44621.0 and 44812.0 encode 2022-03-01 and 2022-09-08. These observations do not prove intended MARCHF1 or SEPTIN8 identities or how the encoding arose. Retain the numeric-unresolved classifications; do not automatically repair gene names.

AKAP2 and PALM2AKAP2 have distinct current approved HGNC records. AKAP2 is a complex-locus constituent; PALM2AKAP2 lists PALM2-AKAP2 as a previous symbol, not AKAP2. Distinct records do not imply biologically unrelated genes. The primary event's intended mapping remains unadjudicated.

Exact 14 HGNC response records, retrieval receipts, the frozen policy, classification script and annotation.json are retained. [Independent source review](review/review.json) passed 96 saved-source checks; [result review](review/result-review.json) passed 13 code/returned-result checks without repeating the primary extraction. Root separately verified the artifact ZIP digest. The original cell-probe run failed because of a display-lookup API error; its executed code and failure logs remain under results/initial. Repaired run 37041943656 at 9918aa902d96128adcc86009174645d0300f59f4 passed in 0.50 seconds. This companion adds provenance, not a new biological result or authorization for outreach. Earlier findings.md is the pre-probe intake memo.
