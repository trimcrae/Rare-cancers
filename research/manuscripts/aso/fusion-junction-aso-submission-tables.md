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
design with the highest gap-level margin at that junction, which is the ranking the Methods define,
and NOT for that junction's cleanest design — the two are often different molecules, and the
cleanest ones are in Table 3. Near-match counts are of RefSeq
transcript accessions and are also given collapsed to distinct gene loci, since RefSeq carries one
accession per annotated variant. A “≥” marks a right-censored count: the screens store the top
15 hits per design, so a design with more is a lower bound. All 38 junction screens
are filtered by alignment orientation. `XM_`/`XR_` records are computationally
predicted gene models rather than curated transcripts, and are counted separately for that reason.
None of these numbers is a measurement of off-target activity.

¹ Counted over the gap-spanning loci only, not over all of that design's near-match loci.

² A near-match count is what the search returned on EITHER strand; a match on the strand opposite the target window cannot be hybridised by an antisense oligonucleotide and is not a liability. Across this corpus 44% of apparent gap-spanning hits (738 of 1,677) are of that kind, which is why the two columns differ and why the raw count alone should not be read as load. This column counts only the 15 RETAINED hits, whereas the gap-spanning locus column is computed over every ranked hit before truncation and is therefore exact. The two are not in conflict where a truncated design shows “≥0” hybridisable and a non-zero gap-spanning locus count: the hybridisable hits are real and simply fall outside the stored window, which is precisely why such a design cannot be called clean.

| junction | designs screened | best gap-level margin | that design | near-matches, either strand (transcripts → loci) | of the retained hits, hybridisable² | loci with a gap-spanning hit | of those, predicted models only¹ | ≤1-mismatch matches across that junction's designs, median (max) |
|---|---|---|---|---|---|---|---|---|
| EWSR1 e10::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTAGATCA-3′ | 35 → ≥2 | ≥15 | 4 | 0 | 4 (32) |
| EWSR1 e12::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATCAAAC-3′ | 9 → 4 | 6 | 1 | 1 | 2 (22) |
| EWSR1 e13::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCACGG-3′ | 31 → ≥3 | ≥12 | 2 | 0 | 2 (25) |
| EWSR1 e15::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCGGGGGC-3′ | 36 → ≥2 | ≥12 | 1 | 0 | 1 (10) |
| EWSR1 e1::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCGTGGAC-3′ | 0 → 0 | 0 | 0 | 0 | 0 (0) |
| EWSR1 e4::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCAGTGGGA-3′ | 11 → 4 | 11 | 3 | 2 | 4 (10) |
| EWSR1 e7::NR4A3 e3 | 5 | 3 | 5′-GGGCATATTCTGCTGC-3′ | 32 → ≥9 | ≥6 | 2 | 0 | 9 (21) |
| EWSR1 e9::NR4A3 e3 | 2 | 3 | 5′-GGGCATATCACCAGGC-3′ | 29 → ≥10 | ≥6 | 2 | 0 | 1 (22) |
| FUS e10::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATCAAAC-3′ | 9 → 4 | 6 | 1 | 1 | 2 (22) |
| FUS e11::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCTCGC-3′ | 30 → ≥1 | ≥15 | 1 | 0 | 0 (3) |
| FUS e13::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCATGTGA-3′ | 6 → 5 | 2 | 2 | 1 | 1 (9) |
| FUS e1::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCGTTTGAG-3′ | ≥50 → ≥7 | ≥13 | 1 | 0 | 10 (38) |
| FUS e3::NR4A3 e3 | 4 | 3 | 5′-GGGCATATTGTTCTGG-3′ | 18 → ≥4 | ≥1 | 2 | 0 | 3 (23) |
| FUS e5::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCACCT-3′ | 32 → ≥8 | ≥8 | 2 | 1 | 2 (3) |
| FUS e7::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCACCAAAT-3′ | 34 → ≥5 | ≥8 | 0 | 0 | 12 (39) |
| FUS e8::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCGGAGTCA-3′ | 4 → 3 | 3 | 1 | 0 | 0 (1) |
| TAF15 e11::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATCAAAC-3′ | 9 → 4 | 6 | 1 | 1 | 2 (22) |
| TAF15 e12::NR4A3 e3 | 4 | 2 | 5′-AGGGCATATCTCGCCG-3′ | 42 → ≥4 | ≥11 | 3 | 0 | 3 (4) |
| TAF15 e14::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCTCCT-3′ | ≥50 → ≥2 | ≥11 | 2 | 0 | 19 (40) |
| TAF15 e1::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCGACATG-3′ | 5 → 2 | 0 | 0 | 0 | 0 (0) |
| TAF15 e4::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGACTGA-3′ | 34 → ≥3 | ≥15 | 4 | 1 | 10 (53) |
| TAF15 e6::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTTGTGTG-3′ | 11 → 10 | 7 | 7 | 5 | 2 (2) |
| TAF15 e8::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCACCAAAA-3′ | 41 → ≥4 | ≥13 | 2 | 0 | 10 (17) |
| TAF15 e9::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCAGCATCT-3′ | 23 → ≥7 | ≥0 | 2 | 0 | 1 (4) |
| TCF12 e11::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTAGAATG-3′ | 15 → 5 | 2 | 1 | 1 | 2 (6) |
| TCF12 e13::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGTGAGA-3′ | 17 → ≥8 | ≥6 | 1 | 1 | 1 (12) |
| TCF12 e17::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCTATAA-3′ | 8 → 3 | 0 | 0 | 0 | 1 (6) |
| TCF12 e19::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCTGACT-3′ | 12 → 4 | 8 | 1 | 1 | 1 (2) |
| TCF12 e3::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGATCCA-3′ | 15 → 4 | 10 | 2 | 2 | 2 (35) |
| TCF12 e5::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCATCAGA-3′ | 26 → ≥15 | ≥15 | 17 | 12 | 2 (32) |
| TCF12 e7::NR4A3 e3 | 4 | 2 | 5′-GGCATATCAAGCGCTG-3′ | 2 → 2 | 0 | 0 | 0 | 0 (1) |
| TCF12 e9::NR4A3 e3 | 4 | 3 | 5′-GGGCATATCTTGCATA-3′ | 14 → 2 | 8 | 1 | 0 | 8 (23) |
| TFG e2::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTTCATCT-3′ | ≥50 → ≥1 | ≥15 | 2 | 0 | 35 (87) |
| TFG e3::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCAAATAAT-3′ | 14 → 6 | 9 | 3 | 0 | 9 (17) |
| TFG e4::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATTTTCA-3′ | ≥50 → ≥3 | ≥15 | 5 | 2 | 41 (100) |
| TFG e5::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGAAACC-3′ | 41 → ≥6 | ≥11 | 7 | 1 | 3 (21) |
| TFG e6::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTTCAATC-3′ | 37 → ≥3 | ≥2 | 0 | 0 | 11 (21) |
| TFG e7::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGAATAC-3′ | 27 → ≥3 | ≥3 | 3 | 1 | 4 (26) |

**Table 3. The 9 designs with no hybridisable near-match.** Every design at the 6 junctions
where one exists, which is the set the Results' cleanliness claim is about. A design qualifies only
if its retained hit list is not truncated — no more near-matches than the 15 the screens store — because the
strand of an unstored hit cannot be recovered, so a truncated list cannot establish that nothing
hybridisable remains. The underlying search is itself capped, so these are the designs whose
near-match lists are shortest, not the designs whose lists are known to be exhaustive. ΔΔG°37 is the margin by which the fusion duplex is favoured over the best
duplex either parent can form, for an unmodified DNA:RNA hybrid; because the fusion duplex pairs
both LNA wings and each parent duplex only one, it is a lower bound on the modified
oligonucleotide's discrimination rather than an upper one. None of these numbers is a measurement of off-target
activity, and none speaks to cleavage.

³ Under the optimistic five-fold and the pessimistic
no-discrimination bound on RNase-H1 single-mismatch discrimination. A single value means the two
bounds agree.

⁴ Of four conventional antisense design rules: GC within 40–60%, no G-quadruplex
motif, no homopolymer run of four, no CpG dinucleotide.

| design | junction | GC (%) | gap-level margin | ΔΔG°37 (kcal/mol) | near-matches, either strand | of those, hybridisable | exact / ≤1-mismatch matches | residual cleavage load, both bounds³ | conventional rules failed⁴ |
|---|---|---|---|---|---|---|---|---|---|
| 5′-GCATATCCGTGGACGC-3′ | EWSR1 e1::NR4A3 e3 | 62.5 | 1 | 7.981 | 0 | 0 | 0 / 0 | 0 | GC outside 40–60%, contains a CpG |
| 5′-GGCATATCCGTGGACG-3′ | EWSR1 e1::NR4A3 e3 | 62.5 | 2 | 10.085 | 0 | 0 | 0 / 0 | 0 | GC outside 40–60%, contains a CpG |
| 5′-GGGCATATCCGTGGAC-3′ | EWSR1 e1::NR4A3 e3 | 62.5 | 3 | 12.189 | 0 | 0 | 0 / 0 | 0 | GC outside 40–60%, contains a CpG |
| 5′-AGGGCATATCGGAGTC-3′ | FUS e8::NR4A3 e3 | 56.2 | 2 | 10.895 | 3 | 0 | 0 / 0 | 0 | contains a CpG |
| 5′-GGGCATATCCGACATG-3′ | TAF15 e1::NR4A3 e3 | 56.2 | 3 | 11.894 | 5 | 0 | 0 / 0 | 0 | contains a CpG |
| 5′-GGGCATATCTCTATAA-3′ | TCF12 e17::NR4A3 e3 | 37.5 | 3 | 8.556 | 8 | 0 | 0 / 0 | 0 | GC outside 40–60% |
| 5′-GCATATCAAGCGCTGC-3′ | TCF12 e7::NR4A3 e3 | 56.2 | 1 | 7.98 | 1 | 0 | 0 / 0 | 0 | contains a CpG |
| 5′-GGCATATCAAGCGCTG-3′ | TCF12 e7::NR4A3 e3 | 56.2 | 2 | 10.085 | 2 | 0 | 0 / 0 | 0 | contains a CpG |
| 5′-CAGGGCATATCTTGCA-3′ | TCF12 e9::NR4A3 e3 | 50.0 | 1 | 9.325 | 7 | 0 | 0 / 0 | 0 | none |
