---
id: "DOC-CONTINUATION-2026-10-02-FOUNDATION-ASO-INDEPENDENT-REVIEW"
title: "ASO transcriptome extension: independent focused review"
level: "cross-cutting"
kind: "memo"
status: "live"
canonical_for: []
purpose: "Record the scoped evidence and reasoning for ASO transcriptome extension: independent focused review."
scope: "October 2 continuation; limited to the named sources, computations and review scope recorded in the body. No submission clearance."
audience: ["maintainers","autonomous research agents"]
date: "2026-10-02"
last_verified: "unverified"
_backfilled: "true"
---

# ASO transcriptome extension: independent focused review

Date: 2026-10-02. Seat: foundation_contribution. Routine independent code review;
not the required ultra pre-submission review and not biological validation.

## Inspected

Private proposed scan_transcriptome.cpp, test_scan.py and run_transcriptome.py.
Frozen accepted catalogue:
https://github.com/trimcrae/Rare-cancers/blob/a916dab2979e27f930b417243f021b6c2b2ca371/research/release-candidates/PUB-ASO/2026-09-30-full-catalogue/results/all-designs.tsv

Independently recomputed catalogue ranks from 220 designs in 44 groups:
minimum expanded-seven-gene gap, then maximum exact Hamming distance.
Zero disagreements with primary_co_winner or final_co_winner flags.
Archived Hamming distribution: distance1=1, distance2=20, distance3=82,
distance4=109, distance5=8.

Inspected seed/core indices, bidirectional contiguous-match extension, bounded
Hamming-neighbor enumeration, complete-window boundaries, ambiguity resets,
record partitioning and witness caps. No concrete engine defect found.
Compiler/scanner execution was not performed by this seat.

## Findings and disposition

1. Union construction discarded exact archived distances outside scanner radius.
   With no <=3 hit and archived exact4, retained-corpus union is exactly4.
   With archived exact5, union is [4,5]. Original result code returned null for
   both and failed to retain the upper bound. Root accepted the repair.
   Proposed union_distance validates distances, resolves exact observations,
   and returns explicit lower/upper bounds.

2. Ranking uncertainty was conflated with numerical-distance uncertainty.
   A sole primary winner is final regardless of its censored distance.
   A primary candidate whose lower bound exceeds every rival upper bound is
   uniquely final. Root accepted the repair. Proposed rank_primary_intervals
   also returns all argmax co-winners when all intervals are exact; otherwise
   it conservatively returns unresolved without guessing.

Implementation intake: ../interval_ranking.py and ../test_interval_ranking.py.
These are new independent files; existing root-owned sources were not edited.
Synthetic tests cover exact4 recovery, [4,5], exact observed minima, censored
singleton, guaranteed winner, overlapping intervals, exact ties, unresolved
ties, ordering independence, invalid distances, inconsistent bounds and IDs.

## Validation status and limits

Tests were written but NOT executed locally, per root instruction.
Root must execute them in the permitted cloud validation environment and
integrate the module into the driver before describing the findings as fixed.
The root's analysis-plan censoring language also requires corresponding update.
No UI, builds, checkout creation, external messages, repository writes or
downloads to disk were performed. This is a focused mathematical/code review,
not evidence of off-target safety, cleavage, expression or therapeutic efficacy.
