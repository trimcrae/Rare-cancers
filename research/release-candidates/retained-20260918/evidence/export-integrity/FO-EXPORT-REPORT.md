# Fusion-output DOCX-to-PDF export integrity

**FAIL — Supplementary Table S14 loses eight complete data rows in Supplementary File 2 and the combined aiXiv PDF.** No additional textual export loss was found across all five documents after explicit glyph-order adjudication.

Checked 2026-09-18T17:17:33.144113+00:00; render source commit `2cf33f03a1aa6cc21143d618ee51cfa7fd532ab1`. This is a read-only comparison, not scientific or prose review.

## Bound evidence

- Initial mismatch audit (preserved): `FO-INITIAL-EXPORT-AUDIT.json`, SHA-256 `1f6a46588a5d0b5a5d9a9ada86940f62d0c63c5c065deb27468166ce73ff83c9`.
- Character-position adjudication: `FO-GEOMETRY-ADJUDICATION.json`, SHA-256 `59b5f190c3f5a5470e6f897377991aa8fb4a15fc58a473fc479ce8e41b89bc2b`.
- Final adjudication: `FO-EXPORT-ADJUDICATION.json`, SHA-256 `4b61778bde97bc58725190f35614990a400465422fe532eb5493393ee75784d2`.
- Render receipt: `C:\Users\mcrae\.codex\worktrees\emc-fo-figure4-20260909\EMC-Research\research\release-candidates\retained-20260918\rendered\RENDER-RECEIPT.json`, SHA-256 `fbb5a13710200ed569039b8aa9740118180a956dedadbd5d38bfca5c9f6c6ec7`.
- Main source authority: `C:\Users\mcrae\.codex\worktrees\emc-fo-figure4-20260909\EMC-Research\research\release-candidates\retained-20260918\rendered\FO\figures\LABEL-CORRECTION-RECEIPT.json`, SHA-256 `3f8a49c4f0bbb7c197b0666f1898181672476ec379fd0c8ec5fcb7153feb230f`.

The main was compared to `rendered/FO/main-with-corrected-labels.docx` (SHA-256 `567d3f02aec8e7e4c0181538dd03f22cb55e53c9e15429a2bd95bbf541d8df34`). The render receipt intentionally retains the original input hash; the corrected Word hash was verified against the label-correction receipt. Other documents use the original inputs and render receipt hashes. All current input/PDF hashes matched these authorities.

## Comprehensive coverage

| Role | Source paragraphs including cells | Exact initial matches | Glyph-order artifacts resolved geometrically | Actual omitted cell paragraphs | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| main | 413 | 407 | 6 | 0 | PASS_TEXTUAL_COMPLETENESS |
| supplement-1 | 1086 | 1086 | 0 | 0 | PASS_TEXTUAL_COMPLETENESS |
| supplement-2 | 362 | 313 | 7 | 56 | FAIL_S14_EIGHT_ROWS_OMITTED |
| cover | 10 | 10 | 0 | 0 | PASS_TEXTUAL_COMPLETENESS |
| highlights | 6 | 6 | 0 | 0 | PASS_TEXTUAL_COMPLETENESS |

Source matching includes every nonempty paragraph/table-cell paragraph, all numbers, citations, references and declarations. Normalization is NFKC plus whitespace/line breaks, soft hyphens and zero-width/BOM removal. Only terminal printed page numbers equal to the PDF page ordinal are removed. No scientific digit, sign or citation is discarded. After excluding the specifically documented lost S14 cells and geometrically resolved glyph cases, every other source paragraph matches the actual PDF in source order without reusing occurrences.

## True loss: eight S14 rows

In source XML, S14 is table 6 and has a header plus nine data rows. The PDF retains only the header and first data row, ReMap2022 (merged), on page 2. Page 3 proceeds to S15. The omitted source rows are:

| XML row including header | Experiment |
| ---: | --- |
| 3 | SRX1653204 (hg38) |
| 4 | SRX1653203 (hg38) |
| 5 | AciCC-1 (Haller) |
| 6 | AciCC-2 (Haller) |
| 7 | AciCC-3 (Haller) |
| 8 | Normal parotid gland (Haller) |
| 9 | 5 further NR4A1 experiments |
| 10 | 12 ChIP-Atlas NR4A3 peak sets |

These eight rows contain 56 source cell paragraphs. The initial substring comparison detected 42 missing cell strings; 14 generic/repeated strings also occur elsewhere and therefore initially matched. The complete row/position check establishes that all 56 cells are absent from their required S14 positions. Full exact cell contents and paragraph ordinals are preserved in the initial audit; full omitted rows are reproduced in the final JSON. No other table/paragraph omission remains after adjudication.

## Non-loss mismatches

The other 13 initial mismatches are reading-order artifacts from separately emitted fallback glyphs. PDF character-coordinate extraction restores each entire source block exactly, including all signs/symbols. No glyph is waived or dropped to obtain a match.

- Main XML paragraphs 150, 151, 155 and 335: scientific-notation superscript minus signs; paragraphs 263 and 283: CD1c superscript plus.
- SI2 XML paragraphs 64, 65 and 74: scientific-notation superscript minus; paragraph 270: warning symbol; paragraph 294: set-membership symbol; paragraph 322: CD1c superscript plus; paragraph 326: no-entry symbol.

`FO-GEOMETRY-ADJUDICATION.json` records character bounding boxes and reconstructed lines. This is text-coordinate inspection without rendering. Raw mismatch records remain intact.

## Consequence and limits

Combined FO PDF: `C:\Users\mcrae\.codex\worktrees\emc-fo-figure4-20260909\EMC-Research\research\release-candidates\retained-20260918\rendered\FO\aixiv-review.pdf`; SHA-256 `6c0a9f2d8b634bdee4948ede0c0729578873bf8a67a703658bb24bdb0b7d810e`, 66 pages. Its extracted page text exactly equals the component pages in order, so the S14 omission is also present in the combined upload bytes. **Do not post this PDF.** Repair export pagination, rerender the affected supplement and regenerate the combined PDF, then verify all ten S14 rows (header plus nine data rows) and repeat the affected completeness/visual checks.

Author, correspondence, ORCID, declaration and preprint lines preserve source text. FO acknowledges existing aiXiv version 1.1; journal-not-submitted wording remains about the journal derivative. No independent external identity/current-page review performed.

No source/scientific inputs, repository files or receipts were modified. No UI, browser, rendering, downloads, publication or scientific reevaluation was performed. This report covers textual completeness; visual layout is covered by the separate visual advisor.
