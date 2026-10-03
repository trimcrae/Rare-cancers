---
id: DOC-CHECKPOINT05-FOUNDATION-CELL-ENCODING-INTERPRETATION-PROPOSAL
title: Proposed companion update after bounded cell-encoding result
kind: memo
status: proposed
date: "2026-10-02"
last_verified: "2026-10-02"
purpose: Replace the pending-probe wording with observed encoding evidence without gene inference.
scope: Two source partner-gene cells only.
audience: [maintainers, reviewers]
---

The repaired cloud probe succeeded in run 37041943656 at revision 9918aa902d96128adcc86009174645d0300f59f4. Reviewed source bytes match the code SHA256 in execution.json. The prior failed run 37041128464 should remain part of the record.

At worksheet row 8570, partner column 2 (zero-based), raw value 44621.0 is reported as xlrd date type 3, XF 64, format key 16, d-mmm, datemode 0, encoding 2022-03-01. At row 20794, the same type/format metadata accompanies raw value 44812.0, encoding 2022-09-08. Exact workbook hash, header, source ID, adjacent gene, raw value, and RE alteration sentinels are checked by the reviewed code. This is observed XLS date encoding, not recovery of original intended gene strings.

Retain both unresolved_numeric_source_cell classifications and the two numeric source literals. Add an encoding-evidence status such as observed_date_encoding_intended_gene_unresolved; do not classify either event as nomenclature-supported, infer MARCHF1 or SEPTIN8 from calendar text, alter original/corrected exports, or change the 12 supported / 2 numeric unresolved / 1 distinct-record discrepancy event counts. Current target previous symbols MARCH1 and SEPT8 do not bridge the primary-evidence gap.

Replace pending-probe statements with completed bounded encoding evidence, preserving original failure and success receipts separately. The initial HGNC review is unchanged. The saved JSON wrapper provides embedded output and reports the underlying artifact hash; its underlying 1026 artifact bytes were not independently available for rehashing in this review.
