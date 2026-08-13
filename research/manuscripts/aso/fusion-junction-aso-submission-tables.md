<!-- GENERATED — DO NOT EDIT. Regenerate: python3 research/manuscripts/submission_tables.py -->

# Tables — fusion-junction ASO submission

**Table 1. The frame-compatible junction space across five *NR4A3* fusion partners.** Every
donor-exon × *NR4A3*-acceptor-exon pair was graded against the frame condition before any design was
emitted. The gap-level margin is the number of junction-unique bases inside the six-nucleotide
catalytic gap on the shorter side of the seam. Frame compatibility is an arithmetic property of exon
structure and is not a claim about which junctions patients carry.

| 5′ partner | donor exons | exon pairs graded | frame-compatible | with ≥1 fusion-specific design | GC range of those designs (%) | best gap-level margin |
|---|---|---|---|---|---|---|
| *EWSR1* | 17 | 51 | 8 | 8 | 37.5–75.0 | 3 |
| *FUS* | 15 | 45 | 8 | 8 | 31.2–62.5 | 3 |
| *TAF15* | 16 | 48 | 8 | 8 | 31.2–68.8 | 3 |
| *TCF12* | 21 | 63 | 8 | 8 | 25.0–56.2 | 3 |
| *TFG* | 8 | 24 | 6 | 6 | 25.0–50.0 | 3 |
| **all 5 partners** | — | **231** | **38** | **38** | — | — |

**Table 2. Predicted specificity per screened junction.** One row per junction; figures are for the
design with the highest gap-level margin at that junction, which is the ranking the Methods define. Near-match counts are of RefSeq
transcript accessions and are also given collapsed to distinct gene loci, since RefSeq carries one
accession per annotated variant. A “≥” marks a right-censored count: the screens store the top 15
hits per design, so a design with more is a lower bound. **Counts in ‡-marked rows are upper
bounds**: those screens did not filter alignment orientation, so minus-strand matches — which an
antisense oligonucleotide cannot hybridise — are still included in them. Unmarked rows are
orientation-filtered. `XM_`/`XR_` records are computationally
predicted gene models rather than curated transcripts, and are counted separately for that reason.
None of these numbers is a measurement of off-target activity.

¹ Counted over the gap-spanning loci only, not over all of that design's near-match loci.

‡ This junction's counts were not filtered by alignment orientation, so they still include minus-strand hits — across the filtered corpus, 47% of all apparent gap-spanning hits. Two distinct causes are marked alike here because their consequence is identical: three screens never parsed the aligned strand, and four parsed it but were classified before the filter read it. Its numbers are upper bounds and are NOT comparable with the unmarked rows.

| junction | designs screened | best gap-level margin | that design | near-matches (transcripts → loci) | loci with a gap-spanning hit | of those, predicted models only¹ | ≤1-mismatch matches across that junction's designs, median (max) |
|---|---|---|---|---|---|---|---|
| EWSR1 e10::NR4A3 e3 | 0 of 5 — every BLAST submission failed at the remote service | — | — | — | — | — | — |
| EWSR1 e12::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATCAAAC-3′ | 9 → 4 | 1 | 1 | 2 (22) |
| EWSR1 e13::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCACGG-3′ | 31 → ≥3 | 2 | 0 | 2 (25) |
| EWSR1 e7::NR4A3 e3 | 5 | 3 | 5′-GGGCATATTCTGCTGC-3′ | 32 → ≥9 | 2 | 0 | 9 (21) |
| EWSR1 e9::NR4A3 e3 | 2 | 3 | 5′-GGGCATATCACCAGGC-3′ | 29 → ≥10 | 2 | 0 | 1 (22) |
| FUS e10::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATCAAAC-3′ | 9 → 4 | 1 | 1 | 2 (22) |
| FUS e1::NR4A3 e3 ‡ | 4 | 3 | 5′-GGGCATATCGTTTGAG-3′ | ≥50 → ≥7 | ≥0 | 0 | 10 (38) |
| FUS e3::NR4A3 e3 ‡ | 2 | 3 | 5′-GGGCATATTGTTCTGG-3′ | 18 → ≥4 | ≥3 | 2 | 3 (23) |
| FUS e5::NR4A3 e3 ‡ | 3 | 3 | 5′-GGGCATATCTCCACCT-3′ | 32 → ≥8 | ≥5 | 3 | 2 (3) |
| TAF15 e11::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATCAAAC-3′ | 9 → 4 | 1 | 1 | 2 (22) |
| TAF15 e6::NR4A3 e3 ‡ | 1 | 1 | 5′-GCATATCTTGTGTGTG-3′ | ≥50 → ≥4 | ≥4 | 1 | 2 (2) |
| TCF12 e11::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTAGAATG-3′ | 15 → 5 | 1 | 1 | 2 (6) |
| TCF12 e13::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGTGAGA-3′ | 17 → ≥8 | 1 | 1 | 1 (12) |
| TCF12 e17::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCTATAA-3′ | 8 → 3 | 0 | 0 | 1 (6) |
| TCF12 e19::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCTGACT-3′ | 12 → 4 | 1 | 1 | 1 (2) |
| TCF12 e3::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGATCCA-3′ | 15 → 4 | 2 | 2 | 2 (35) |
| TCF12 e5::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCATCAGA-3′ | 26 → ≥15 | 17 | 12 | 2 (32) |
| TCF12 e7::NR4A3 e3 | 4 | 2 | 5′-GGCATATCAAGCGCTG-3′ | 2 → 2 | 0 | 0 | 0 (1) |
| TCF12 e9::NR4A3 e3 | 4 | 3 | 5′-GGGCATATCTTGCATA-3′ | 14 → 2 | 1 | 0 | 8 (23) |
| TFG e2::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTTCATCT-3′ | ≥50 → ≥1 | 2 | 0 | 35 (87) |
| TFG e3::NR4A3 e3 ‡ | 5 | 3 | 5′-GGGCATATCAAATAAT-3′ | 14 → 6 | 5 | 2 | 9 (17) |
| TFG e4::NR4A3 e3 ‡ | 5 | 3 | 5′-GGGCATATCATTTTCA-3′ | ≥50 → ≥3 | 5 | 2 | 41 (100) |
| TFG e5::NR4A3 e3 ‡ | 5 | 3 | 5′-GGGCATATCTGAAACC-3′ | 41 → ≥6 | 7 | 1 | 3 (21) |
| TFG e6::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTTCAATC-3′ | 37 → ≥3 | 0 | 0 | 11 (21) |
| TFG e7::NR4A3 e3 ‡ | 5 | 3 | 5′-GGGCATATCTGAATAC-3′ | 27 → ≥3 | 7 | 2 | 4 (26) |
