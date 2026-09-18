---
id: "DOC-RETAINED-20260918-DOCX-PDF-TEXT-REPORT"
title: "CSPG4 and ASO first-render textual integrity"
level: "L5"
kind: "memo"
status: "live"
canonical_for: []
purpose: "Preserve the dated textual export audit and its explicit source and output bindings."
scope: "Release artifact integrity only; no new scientific analysis, prose review, or provider-publication claim."
audience: ["maintainers", "external reviewers"]
date: "2026-09-18"
last_verified: "2026-09-18"
---

# CSPG4 and ASO first-render textual integrity

**PASS — no textual export omission or changed number, citation, declaration, author, or preprint statement found.** Checked 2026-09-18 at 17:08:36 UTC (13:08:36 America/New_York).

This read-only audit binds the accepted Word inputs to the actual first-render PDFs from source commit `aebeb47fec2142c72e2f9effa1ef1c1977eb1c19`, GitHub run `35369786182`. It does not reopen scientific or prose review. The accepted source-to-Word comparison and existing visual reviews remain separate evidence.

## Evidence and scope

- Repository: `C:/Users/mcrae/.codex/worktrees/emc-fo-figure4-20260909/EMC-Research`.
- Package: `research/release-candidates/retained-20260918`.
- Render receipt: `rendered/CSPG4-ASO-RENDER-RECEIPT.json`, SHA-256 `4e6b6ecc598da6b38aee76098a96f43c4fe26ae23ba1d3c80d54c5737710c37c`.
- Machine-readable audit: `DOCX-PDF-TEXT-AUDIT.json`, SHA-256 `cdb6d337301373a5373941280a586a08510a9e451bba8f98a63952e70ca85437`.
- Reproducible checker: `check_docx_pdf.py`, SHA-256 `db77ac3fd669cbc0e76f109835a24f2e7648e93542e90595ad850c31c6445f9f`.

Every input Word hash, individual PDF hash, page count, and combined PDF hash matched the first-render receipt. The JSON records full absolute paths, all input/PDF/text SHA-256 hashes, every source paragraph's hash and match result, and combined-PDF/CSV checks.

## Comparison result

| Paper / role | Pages | Source nonempty paragraphs | Table-cell paragraphs included | Matched in source order in retained text and direct PDF extraction |
| --- | ---: | ---: | ---: | ---: |
| CSPG4 main | 14 | 82 | 0 | 82/82 |
| CSPG4 supplement | 5 | 172 | 141 | 172/172 |
| CSPG4 cover | 1 | 14 | 0 | 14/14 |
| ASO main | 24 | 138 | 27 | 138/138 |
| ASO supplement | 2 | 15 | 0 | 15/15 |
| ASO cover | 1 | 10 | 0 | 10/10 |
| ASO highlights | 1 | 6 | 0 | 6/6 |
| Total | 48 | 437 | 168 | 437/437 |

The checker reads `word/document.xml` and any headers, footers, footnotes and endnotes; includes all nonempty Word paragraphs and table-cell paragraphs; and compares against both retained `pdf-text.txt` and independent `pypdf` extraction from the actual PDF. Sequential matching consumes each occurrence once, so repeated cells/paragraphs cannot reuse an earlier occurrence. There are no textboxes, math text, alternate chunks, symbol elements, deleted runs or note references requiring a different extractor in these files. Footer page numbers are generated fields.

Normalization applies Unicode NFKC, removal of soft hyphens/zero-width/BOM characters, and whitespace/linebreak removal. It does not discard punctuation, change scientific digits, strip citations, or substitute wording. Only a standalone terminal page number equal to its actual page ordinal is removed at a PDF page boundary. All paragraph contents then match exactly, including numbers, table contents, citations, reference URLs/DOIs and declarations.

## Explicit mismatch adjudication

Before printed-page-number normalization, independent PDF extraction interrupted 17 source paragraphs with pagination:

- CSPG4 main: XML paragraph ordinals 50, 55, 61, 81.
- CSPG4 supplement: XML paragraph ordinals 32, 88.
- ASO main: XML paragraph ordinals 6, 15, 18, 24, 27, 32, 46, 51, 61, 82, 88.

Every mismatch disappears solely by removing the validated printed page number at the page boundary. All remaining characters match. These are extraction artifacts, not missing or changed material. The audit records the affected source text and adjudication individually. No unresolved mismatch remains.

## Combined preprint exports

- CSPG4 `aixiv-review.pdf`: 19 pages, SHA-256 `11d904a0a0793bce908ad323090eae0c8a79b432f00a29c265abac50f99298e0`. Every page's extracted text is identical to the main-then-supplement component pages in order.
- ASO `aixiv-review.pdf`: 26 pages, SHA-256 `f1c29a6e06e1709e4cb385c5ebab3268a115a547f04931948ea20498a46fc339`. Every page's extracted text is identical to the main-then-supplement component pages in order.
- ASO contains exactly one `fusion-junction-aso-sequences.csv` attachment, 143,782 bytes, SHA-256 `9b82929a3433dddb9fbd3369ed4cf4b45f65c4ab23446616a26eb327ea856fa3`. Its bytes equal the retained input CSV and receipt value.

## Author and preprint metadata

No export-induced or currently critical author/preprint error was found within this bounded check. Author name, unaffiliated status, email, ORCID, responsibility, funding, financial and non-financial interests, and AI-assistance declarations are preserved exactly. This is preservation/internal-consistency verification, not independent external identity verification.

CSPG4's cover discloses its existing Research Square and aiXiv preprints. Its reference to the prior Research Square title is explicitly historical. ASO's cover discloses Qeios version 4 and qualifies the historical Zenodo archive correctly relative to the accepted text. It makes no claim that ASO has already appeared on aiXiv; the retained inventory before today's posting had no ASO aiXiv ID. **After a successful new ASO aiXiv posting, add that posting to the journal cover's preprint disclosure before a later journal submission.** This contingent update is not an existing export omission and does not require editing the current preprint scientific text.

Raster figure labels are outside the Word text comparison and remain covered by existing figure/layout review. No UI, browser, rendering, downloads, source changes, publication or new scientific analysis was performed. Only this small scoped audit and its checker were written outside the repository.
