---
id: DOC-CTA-RETAINED-TPM-20260919
title: Three cancer-testis antigen transcripts in retained primary EMC specimens
kind: memo
status: live
date: 2026-09-19
last_verified: 2026-09-19
audience: [maintainers, autonomous research agents]
purpose: Resolve the previously unread CTAG1B, MAGEA3 and SSX2 transcript lookup.
scope: Three fixed released gene-level TPM rows in nine already-selected primary EMC specimens.
---

# Three cancer-testis antigen transcripts in retained primary EMC specimens

The retained Hofvander matrix contains the three gene-labeled rows that the older arrays and assigned-gene panel could not read. This resolves an instrument-coverage gap. The table reports the released values for the same nine primary EMC specimens used by the existing manifest.

| Specimen | CTAG1B TPM | MAGEA3 TPM | SSX2 TPM |
| --- | ---: | ---: | ---: |
| 11881-19 | 11.45 | 0 | 0 |
| 3371-22 | 1.93 | 0 | 0 |
| 3372-22 | 0.06 | 0 | 0 |
| 4716-22 | 0.08 | 0 | 0 |
| 4840-13 | 0 | 0 | 0 |
| 5149-18 | 2.3 | 0 | 0 |
| 5241-06 | 0 | 0 | 0 |
| 7931-19 | 0 | 0 | 0.09 |
| 8102-22 | 0 | 0 | 0 |

CTAG1B: median 0.06 TPM, range 0–11.45; 5 of nine values are reported above zero.

MAGEA3: median 0 TPM, range 0–0; 0 of nine values are reported above zero.

SSX2: median 0 TPM, range 0–0.09; 1 of nine values are reported above zero.

These counts use only the reported values, not an assay positivity threshold. Zero does not establish biological absence. The three known discovery-overlap records and one nonprimary/unspecified specimen remain excluded under the existing manifest; none was excluded by these expression values. Exact reasons, matrix locations and hashes are in RESULT.json.

The retained source methods describe gene-level RSEM estimates after STAR alignment. This lookup does not independently establish unique read assignment among homologous genes or isoforms. It does not identify malignant-cell expression, antigen protein, a presented peptide, an eligible HLA type or treatment coverage. MAGEA3 is also not an observation of the separate MAGEA4 target. No comparator test, target ranking, new clinical inference or standalone paper follows.

The route remains an internal unresolved therapeutic question. Preserve prior antigen-specific evidence at its original scope, but do not use nonmeasurement on the older platforms as a tumor-negative result. Further work needs a defined antigen and a useful question supported by a relevant source or measurement; another summary of these same TPM values would add little.
