---
id: DOC-CHECKPOINT05-FOUNDATION-GENE-NOMENCLATURE
title: Source-qualified classification of fifteen retained gene-text differences
kind: memo
status: live
level: cross-cutting
purpose: Distinguish current nomenclature support from unresolved source encodings and gene conflicts.
scope: Fifteen events fixed from the successful primary workbook check; annotation only, without rewriting gene identities.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

Twelve of the fifteen retained event-level text differences have direct current HGNC previous-symbol evidence. These involve nine distinct symbol pairs and thirteen changed gene slots, because event871 changes both genes. Two events retain numeric source-cell uncertainty; one has distinct current approved gene records without exact synonym support. The original and identity-corrected exports remain unchanged.

The event list and exact-match policy were saved before lookup in frozen-policy.json. Each export symbol was queried once through the [official HGNC REST fetch service](https://www.genenames.org/help/rest/). Current records must have exact approved-symbol equality and Approved status; source spelling must appear verbatim in prev_symbol or alias_symbol. No fuzzy matching was used. All nine supported pairs matched prev_symbol; none depended on alias matching. A separately recorded follow-up policy allowed one exact AKAP2 query after its absence from the target record.

| Source literal | Export literal | Current HGNC evidence | Event ordinals |
|---|---|---|---|
| C22orf46 | C22orf46P | [HGNC:26294](https://rest.genenames.org/fetch/symbol/C22orf46P), previous symbol | 412 |
| ICK | CILK1 | [HGNC:21219](https://rest.genenames.org/fetch/symbol/CILK1), previous symbol | 871,1891,3213,3491 |
| MLF1IP | CENPU | [HGNC:21348](https://rest.genenames.org/fetch/symbol/CENPU), previous symbol | 871 |
| LINC00476 | ERCC6L2-AS1 | [HGNC:27858](https://rest.genenames.org/fetch/symbol/ERCC6L2-AS1), previous symbol | 908 |
| HIST1H1D | H1-3 | [HGNC:4717](https://rest.genenames.org/fetch/symbol/H1-3), previous symbol | 1211,1814 |
| SLC26A10 | SLC26A10P | [HGNC:14470](https://rest.genenames.org/fetch/symbol/SLC26A10P), previous symbol | 1922 |
| ARNTL | BMAL1 | [HGNC:701](https://rest.genenames.org/fetch/symbol/BMAL1), previous symbol | 2160 |
| BTBD11 | ABTB3 | [HGNC:23844](https://rest.genenames.org/fetch/symbol/ABTB3), previous symbol | 2342 |
| KIAA0100 | BLTP2 | [HGNC:28960](https://rest.genenames.org/fetch/symbol/BLTP2), previous symbol | 3204 |
| 44621.0 | MARCHF1 | Unresolved numeric cell; target [HGNC:26077](https://rest.genenames.org/fetch/symbol/MARCHF1) does not identify its source meaning | 1145 |
| 44812.0 | SEPTIN8 | Unresolved numeric cell; target [HGNC:16511](https://rest.genenames.org/fetch/symbol/SEPTIN8) does not identify its source meaning | 2760 |
| AKAP2 | PALM2AKAP2 | Distinct approved [HGNC:372](https://rest.genenames.org/fetch/symbol/AKAP2) and [HGNC:33529](https://rest.genenames.org/fetch/symbol/PALM2AKAP2); no exact previous/alias match | 3317 |

For event3317, the target record is named PALM2 and AKAP2 fusion and has previous symbol PALM2-AKAP2. Shared name text does not make the separate AKAP2 record equivalent. The evidence does not decide the original alteration's correct molecular annotation; retain the discrepancy for curator review. For the two numeric cells, MARCH1 and SEPT8 appear as previous symbols of the export targets, but neither proves what the numeric workbook cell originally intended. No date-to-gene inference is made.

HGNC info reports lastModified2026-10-02T12:18:06.445Z and46987 documents. Raw responses, actual request times, hashes and per-record date_modified/date_symbol_changed are preserved. This is a current-record receipt, not a historical nomenclature release. For example, C22orf46P's symbol-change date is2022-09-12 and BMAL1's is2022-07-21, both after the source article's June2022 publication; present-day previous-symbol support cannot establish what an earlier source used. No HGNC lookup validates rearrangement biology, pathogenicity, transcript identity or source diagnosis.

## Source-cell evidence and bounded next step

The already successful primary check records exact worksheet rows8570 and20794, partner-gene slot2, raw values44621.0 and44812.0, source IDs2290 and5458. That receipt does not record BIFF cell type or format. The new cloud-only probe reads just those coordinates with xlrd formatting_info, verifies workbook SHA, headers and adjacent ID/gene/alteration sentinels, and reports cell type, XF, format and datemode. If date-typed, it may display the encoded date solely as source-encoding evidence. No local XLS download or extraction occurred.

Run `python probe_source_cells.py --workbook primary.xls` against the retained workbook in artifact11239081000, with an outer60-second limit. A full hash mismatch or coordinate mismatch fails. Probe source was syntax-checked only; execution is pending. Its result cannot resolve intended genes without additional primary evidence. The existing whole-workbook extraction and identity correction must not be repeated for this question.

The complete companion is annotation.json with exact source IDs, worksheet rows, ordered gene pairs and per-slot classes. Empty versus N/A remains the prior explicit missing-token convention. Stop after adding the two-cell encoding receipt or its exact failure. No submission, upstream correction or new biological experiment is claimed.
