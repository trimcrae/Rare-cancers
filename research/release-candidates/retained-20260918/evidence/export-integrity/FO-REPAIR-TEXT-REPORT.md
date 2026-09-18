# Fusion-output supplement repair textual acceptance

**PASS — all 362 source paragraphs are preserved in the repaired 12-page SI2, including all S14 rows.** The repaired 67-page combined PDF exactly preserves the unchanged main, unchanged SI1, and repaired SI2 text in order.

Checked 2026-09-18T17:19:42.033194+00:00. Remote Word export run `35373013434`, source commit `d2b23ef5ecab60cf0e31c15dac36232ec9acfe8d`.

- Corrected Word SHA-256: `920d00215d0029e6c3b74837eb4ce4a80941fd5c922c5a724d13e51fa1c8b7d9`.
- Corrected SI2 PDF SHA-256: `d02219acb01e22edc69af2a4038627877c415171b5a87a92cccb4bb52a8d9f3c`.
- Recombined FO aiXiv PDF SHA-256: `a3ed10f9036e9cd9977216a0041d9994ff02dc0751eb9663cda68a2c87256787`.
- Detailed acceptance: `FO-REPAIR-TEXT-ACCEPTANCE.json`, SHA-256 `6b474d03bdb72e6d8c9b262424e9b037b9cf70b481a0e59ca8ea08dd21d6ea9f`.

The entire nonempty Word paragraph sequence is byte-for-byte equal to the pre-repair accepted source sequence. Of 362 paragraphs, 355 match exactly in both retained PDF text and independent pypdf extraction in source order. The remaining seven are the already identified fallback-glyph reading-order cases; independent character-coordinate extraction restores every full paragraph including its signs/symbols. No character was discarded to resolve them. There are zero unresolved mismatches and zero unexpected ordering failures.

S14 now has its header plus all nine data rows: 70 cell paragraphs match exactly in the required source order. This includes the eight previously missing data rows and every one of their 56 cells, not only the anchor strings SRX1653204 and Normal parotid. All paragraphs, tables, numbers, citations, declarations and historical-record text outside S14 are also covered.

The unchanged main and SI1 PDF hashes were checked against the original audit. Every page of the 67-page combined PDF has extracted text identical to the three component PDFs in order. Prior original failure/mismatch evidence remains intact; the old defective PDF bytes are not accepted by this report.

This is textual export acceptance only. Root's separately pending actual visual QA of these repaired PDF bytes remains necessary. No repository edits, rendering, browser/UI work, downloads or new scientific/prose review were performed.
