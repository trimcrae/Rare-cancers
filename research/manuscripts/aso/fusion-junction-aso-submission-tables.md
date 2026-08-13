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

² A near-match count is what the search returned on EITHER strand; a match on the strand opposite the target window cannot be hybridised by an antisense oligonucleotide and is not a liability. Across this corpus 44% of apparent gap-spanning hits (738 of 1,677) are of that kind, which is why the two columns differ and why the raw count alone should not be read as load. This column counts only the 15 RETAINED hits. The gap-spanning locus column is recounted from those hits wherever they are the complete list, and is exact there; a “≤” marks a truncated design, where the column instead carries the screen's own count over every ranked hit, computed under a locus assignment since corrected that split some genes across accessions and therefore over-counts. The two columns are not in conflict where a truncated design shows “≥0” hybridisable and a non-zero gap-spanning locus count: the hybridisable hits are real and simply fall outside the stored window, which is precisely why such a design cannot be called clean.

| junction | designs screened | best gap-level margin | that design | near-matches, either strand (transcripts → loci) | of the retained hits, hybridisable² | loci with a gap-spanning hit | of those, predicted models only¹ | ≤1-mismatch matches across that junction's designs, median (max) |
|---|---|---|---|---|---|---|---|---|
| EWSR1 e10::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTAGATCA-3′ | 35 → ≥2 | ≥15 | ≤4 | 0 | 4 (32) |
| EWSR1 e12::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATCAAAC-3′ | 9 → 4 | 6 | 1 | 1 | 2 (22) |
| EWSR1 e13::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCACGG-3′ | 31 → ≥3 | ≥12 | ≤2 | 0 | 2 (25) |
| EWSR1 e15::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCGGGGGC-3′ | 36 → ≥2 | ≥12 | ≤1 | 0 | 1 (10) |
| EWSR1 e1::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCGTGGAC-3′ | 0 → 0 | 0 | 0 | 0 | 0 (0) |
| EWSR1 e4::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCAGTGGGA-3′ | 11 → 4 | 11 | 3 | 2 | 4 (10) |
| EWSR1 e7::NR4A3 e3 | 5 | 3 | 5′-GGGCATATTCTGCTGC-3′ | 32 → ≥9 | ≥6 | ≤2 | 0 | 9 (21) |
| EWSR1 e9::NR4A3 e3 | 2 | 3 | 5′-GGGCATATCACCAGGC-3′ | 29 → ≥2 | ≥6 | ≤2 | 0 | 1 (22) |
| FUS e10::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATCAAAC-3′ | 9 → 4 | 6 | 1 | 1 | 2 (22) |
| FUS e11::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCTCGC-3′ | 30 → ≥1 | ≥15 | ≤1 | 0 | 0 (3) |
| FUS e13::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCATGTGA-3′ | 6 → 5 | 2 | 2 | 1 | 1 (9) |
| FUS e1::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCGTTTGAG-3′ | ≥50 → ≥7 | ≥13 | ≤1 | 0 | 10 (38) |
| FUS e3::NR4A3 e3 | 4 | 3 | 5′-GGGCATATTGTTCTGG-3′ | 18 → ≥4 | ≥1 | ≤2 | 0 | 3 (23) |
| FUS e5::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCACCT-3′ | 32 → ≥8 | ≥8 | ≤2 | 1 | 2 (3) |
| FUS e7::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCACCAAAT-3′ | 34 → ≥5 | ≥8 | ≤0 | 0 | 12 (39) |
| FUS e8::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCGGAGTCA-3′ | 4 → 3 | 3 | 1 | 0 | 0 (1) |
| TAF15 e11::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATCAAAC-3′ | 9 → 4 | 6 | 1 | 1 | 2 (22) |
| TAF15 e12::NR4A3 e3 | 4 | 2 | 5′-AGGGCATATCTCGCCG-3′ | 42 → ≥4 | ≥11 | ≤3 | 0 | 3 (4) |
| TAF15 e14::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCTCCT-3′ | ≥50 → ≥2 | ≥11 | ≤2 | 0 | 19 (40) |
| TAF15 e1::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCGACATG-3′ | 5 → 2 | 0 | 0 | 0 | 0 (0) |
| TAF15 e4::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGACTGA-3′ | 34 → ≥3 | ≥15 | ≤4 | 1 | 10 (53) |
| TAF15 e6::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTTGTGTG-3′ | 11 → 7 | 7 | 4 | 2 | 2 (2) |
| TAF15 e8::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCACCAAAA-3′ | 41 → ≥4 | ≥13 | ≤2 | 0 | 10 (17) |
| TAF15 e9::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCAGCATCT-3′ | 23 → ≥7 | ≥0 | ≤2 | 0 | 1 (4) |
| TCF12 e11::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTAGAATG-3′ | 15 → 5 | 2 | 1 | 1 | 2 (6) |
| TCF12 e13::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGTGAGA-3′ | 17 → ≥8 | ≥6 | ≤1 | 1 | 1 (12) |
| TCF12 e17::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCTATAA-3′ | 8 → 3 | 0 | 0 | 0 | 1 (6) |
| TCF12 e19::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCTGACT-3′ | 12 → 4 | 8 | 1 | 1 | 1 (2) |
| TCF12 e3::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGATCCA-3′ | 15 → 4 | 10 | 2 | 2 | 2 (35) |
| TCF12 e5::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCATCAGA-3′ | 26 → ≥1 | ≥15 | ≤17 | 0 | 2 (32) |
| TCF12 e7::NR4A3 e3 | 4 | 2 | 5′-GGCATATCAAGCGCTG-3′ | 2 → 2 | 0 | 0 | 0 | 0 (1) |
| TCF12 e9::NR4A3 e3 | 4 | 3 | 5′-GGGCATATCTTGCATA-3′ | 14 → 2 | 8 | 1 | 0 | 8 (23) |
| TFG e2::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTTCATCT-3′ | ≥50 → ≥1 | ≥15 | ≤2 | 0 | 35 (87) |
| TFG e3::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCAAATAAT-3′ | 14 → 6 | 9 | 3 | 0 | 9 (17) |
| TFG e4::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATTTTCA-3′ | ≥50 → ≥3 | ≥15 | ≤5 | 2 | 41 (100) |
| TFG e5::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGAAACC-3′ | 41 → ≥6 | ≥11 | ≤7 | 1 | 3 (21) |
| TFG e6::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTTCAATC-3′ | 37 → ≥3 | ≥2 | ≤0 | 0 | 11 (21) |
| TFG e7::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGAATAC-3′ | 27 → ≥3 | ≥3 | ≤3 | 1 | 4 (26) |

**Table 3. The 9 designs with no hybridisable near-match at the default search depth.** Six of
these lose the property when the same junctions are re-screened at a tenfold deeper alignment
ceiling, three of them having returned no near-match at all here; §3.5 reports that
measurement and names the three that survive it. This table is the default-depth result, retained
because it is the depth at which the corpus-wide counts elsewhere in the paper were computed. Every design at the 6 junctions
where one exists. A design qualifies only
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

**Table 4. The best available design at each of the 38 frame-compatible junctions.** Tables 2 and 3
select across the panel; this table selects within each junction, which is the question a patient's
fusion poses. Designs are ranked by parent liability first, since sparing the wild-type parents is
what the modality exists for, then by pre-mRNA sites, then by distinct gene loci, with ties broken
on gap-level margin rather than on raw hit counts. Nothing was re-screened: every field is joined
from a screen already reported above. Whether a junction has a published exon-resolved breakpoint is
reported separately from specificity and never folded into the ranking — “published” means an
exon-resolved EMC breakpoint is reported for that exon pair, “exon not reported” that the partner
has a resolved breakpoint at a different exon, and “none published” that no exon-resolved breakpoint
has been reported for that partner at all. The last of those is absence of evidence: EMC case
reports usually name the partner gene without sequencing to nucleotide resolution. Gap-paired
near-matches are at the tenfold deeper alignment ceiling, where every hit list is complete. The
genome column is the observed number of gap-paired sites at ≤2 mismatches over the number expected
for an arbitrary 16-mer, so 1.00 is chance. A junction with no design clearing the parent screen is
reported as such rather than given a best row.

| junction | exon-resolved breakpoint | designs clearing the parent screen | best available design | gap-level margin | longest parent duplex through the gap (bp) | gap-paired near-matches at the deeper ceiling (transcripts → loci) | genome-wide gap-paired load, observed/expected |
|---|---|---|---|---|---|---|---|
| EWSR1 e10::NR4A3 e3 | exon not reported | 3 of 5 | 5′-GGCATATCTAGATCAA-3′ | 2 | 7 | 70 → 4 | 0.61 |
| EWSR1 e12::NR4A3 e3 | published | 4 of 5 | 5′-GGGCATATCATCAAAC-3′ | 3 | 8 | 123 → 6 | 0.62 |
| EWSR1 e13::NR4A3 e3 | exon not reported | 3 of 5 | 5′-GGGCATATCTCCACGG-3′ | 3 | 8 | 24 → 2 | 0.29 |
| EWSR1 e15::NR4A3 e3 | exon not reported | 4 of 5 | 5′-GGGCATATCCGGGGGC-3′ | 3 | 0 | 33 → 1 | 0.06 |
| EWSR1 e1::NR4A3 e3 | exon not reported | 2 of 5 | 5′-GGGCATATCCGTGGAC-3′ | 3 | 0 | 0 → 0 | 0.07 |
| EWSR1 e4::NR4A3 e3 | exon not reported | 4 of 5 | 5′-AGGGCATATCAGTGGG-3′ | 2 | 6 | 9 → 3 | 0.71 |
| EWSR1 e7::NR4A3 e3 | exon not reported | 5 of 5 | 5′-CAGGGCATATTCTGCT-3′ | 1 | 8 | 14 → 5 | 1.08 |
| EWSR1 e9::NR4A3 e3 | exon not reported | 4 of 5 | 5′-GGCATATCACCAGGCT-3′ | 2 | 7 | 15 → 4 | 0.73 |
| FUS e10::NR4A3 e3 | none published | 4 of 5 | 5′-GGGCATATCATCAAAC-3′ | 3 | 8 | 123 → 6 | 0.62 |
| FUS e11::NR4A3 e3 | none published | 3 of 5 | 5′-GGGCATATCTCCTCGC-3′ | 3 | 9 | 30 → 1 | 0.22 |
| FUS e13::NR4A3 e3 | none published | 4 of 5 | 5′-GGGCATATCCATGTGA-3′ | 3 | 7 | 2 → 2 | 0.75 |
| FUS e1::NR4A3 e3 | none published | 2 of 5 | 5′-GGGCATATCGTTTGAG-3′ | 3 | 8 | 5 → 2 | 0.12 |
| FUS e3::NR4A3 e3 | none published | 5 of 5 | 5′-GGCATATTGTTCTGGC-3′ | 2 | 7 | 18 → 3 | 0.76 |
| FUS e5::NR4A3 e3 | none published | 2 of 3 | 5′-GGGCATATCTCCACCT-3′ | 3 | 8 | 33 → 4 | 0.65 |
| FUS e7::NR4A3 e3 | none published | 4 of 5 | 5′-GGCATATCACCAAATT-3′ | 2 | 7 | 10 → 3 | 0.92 |
| FUS e8::NR4A3 e3 | none published | 3 of 5 | 5′-AGGGCATATCGGAGTC-3′ | 2 | 0 | 0 → 0 | 0.06 |
| TAF15 e11::NR4A3 e3 | exon not reported | 4 of 5 | 5′-GGGCATATCATCAAAC-3′ | 3 | 8 | 123 → 6 | 0.62 |
| TAF15 e12::NR4A3 e3 | exon not reported | 3 of 5 | 5′-GGGCATATCTCGCCGC-3′ | 3 | 6 | 4 → 2 | 0.04 |
| TAF15 e14::NR4A3 e3 | exon not reported | 0 of 5 | — | — | — | — | — |
| TAF15 e1::NR4A3 e3 | exon not reported | 2 of 5 | 5′-GGGCATATCCGACATG-3′ | 3 | 0 | 0 → 0 | 0.04 |
| TAF15 e4::NR4A3 e3 | exon not reported | 2 of 5 | 5′-GGCATATCTGACTGAC-3′ | 2 | 8 | 12 → 2 | 0.69 |
| TAF15 e6::NR4A3 e3 | published | 1 of 5 | 5′-GGGCATATCTTGTGTG-3′ | 3 | 9 | 8 → 5 | 0.60 |
| TAF15 e8::NR4A3 e3 | exon not reported | 4 of 5 | 5′-GGGCATATCACCAAAA-3′ | 3 | 7 | 36 → 3 | 0.86 |
| TAF15 e9::NR4A3 e3 | exon not reported | 2 of 5 | 5′-AGGGCATATCAGCATC-3′ | 2 | 6 | 6 → 2 | 1.13 |
| TCF12 e11::NR4A3 e3 | none published | 3 of 5 | 5′-GGCATATCTAGAATGC-3′ | 2 | 8 | 4 → 3 | 0.69 |
| TCF12 e13::NR4A3 e3 | none published | 2 of 5 | 5′-GGCATATCTGTGAGAG-3′ | 2 | 7 | 6 → 5 | 1.08 |
| TCF12 e17::NR4A3 e3 | none published | 3 of 5 | 5′-GGGCATATCTCTATAA-3′ | 3 | 7 | 14 → 5 | 0.83 |
| TCF12 e19::NR4A3 e3 | none published | 2 of 5 | 5′-GGGCATATCTCTGACT-3′ | 3 | 8 | 75 → 3 | 0.82 |
| TCF12 e3::NR4A3 e3 | none published | 0 of 5 | — | — | — | — | — |
| TCF12 e5::NR4A3 e3 | none published | 4 of 5 | 5′-GGGCATATCCATCAGA-3′ | 3 | 7 | 17 → 1 | 0.56 |
| TCF12 e7::NR4A3 e3 | none published | 2 of 5 | 5′-GGGCATATCAAGCGCT-3′ | 3 | 8 | 0 → 0 | 0.26 |
| TCF12 e9::NR4A3 e3 | none published | 1 of 5 | 5′-GGGCATATCTTGCATA-3′ | 3 | 8 | 39 → 6 | 0.71 |
| TFG e2::NR4A3 e3 | none published | 0 of 4 | — | — | — | — | — |
| TFG e3::NR4A3 e3 | none published | 4 of 5 | 5′-GGGCATATCAAATAAT-3′ | 3 | 8 | 18 → 6 | 1.35 |
| TFG e4::NR4A3 e3 | none published | 1 of 5 | 5′-AGGGCATATCATTTTC-3′ | 2 | 7 | 82 → 12 | 1.77 |
| TFG e5::NR4A3 e3 | none published | 2 of 5 | 5′-GGCATATCTGAAACCT-3′ | 2 | 8 | 34 → 7 | 1.38 |
| TFG e6::NR4A3 e3 | none published | 3 of 5 | 5′-GGGCATATCTTCAATC-3′ | 3 | 9 | 29 → 3 | 0.73 |
| TFG e7::NR4A3 e3 | none published | 2 of 5 | 5′-GGCATATCTGAATACT-3′ | 2 | 9 | 24 → 6 | 1.24 |

**Table 5. Gap length against junction specificity, at one seam and across the design space.** The
same seams tiled and screened at three gapmer geometries, wing held at five nucleotides so that only
the catalytic gap changes. Inside the gap the junction-unique bases on the shorter side and the
bases one wild-type parent pairs on the longer side are complements: they sum to the gap, which the
generating module asserts for every design rather than assuming. Each nucleotide of gap-level margin
therefore costs one nucleotide of contiguous wild-type-parent duplex, and the two directions are
reported separately and never combined into a score. Near-match counts fall partly for a reason the
instrument guarantees rather than measures: at a fixed budget of two mismatches every locus a longer
design can reach is also reached by each of its own shorter sub-windows, so the set can only shrink,
and two mismatches is a fractionally stricter test at 20 nucleotides than at 16. Only the size of
the fall and which designs reach zero are measurements. The three blocks carry different
denominators and are not comparable across blocks: the seam block is one molecule, the matched-seam
block is the six junctions every geometry was screened at, and the corpus block is each geometry's
whole design space, which is not screened at the same junctions. The exhaustive GRCh38 genome scan
is unavailable at 18 and 20 nucleotides by construction, so no row reports it. Because the wing is
five throughout, a parent's seam hybrid is five base pairs plus its share of the gap, so pairing
five nucleotides of contiguous gap DNA and reaching a ten-base-pair hybrid are the same condition
and are reported as one row. ΔG°37 values are for
an unmodified DNA:RNA hybrid; the wing is five at every geometry, so LNA affinity enters each parent
duplex identically and cannot explain a difference between the columns. None of these numbers is a
measurement of cleavage.

| | 5-6-5 (16-mer) | 5-8-5 (18-mer) | 5-10-5 (20-mer) |
|---|---|---|---|
| **At the *EWSR1* e12 / *TAF15* e11 / *FUS* e10 seam** | | | |
| design (5′→3′) | GGGCATATCATCAAAC | AGGGCATATCATCAAACC | CAGGGCATATCATCAAACCA |
| gap-level margin | 3 | 4 | 5 |
| hybridisable gap-spanning cleavage risks | 123 | 3 | 0 |
| gene loci carrying one | 6 | 1 | 0 |
| near-matches (≤2 mismatches, deeper ceiling) | 189 | 50 | 20 |
| ≤1-mismatch matches over 186,185 transcripts | 1 | 0 | 0 |
| mature-parent duplex through the whole gap (bp) | 8 (*TFG*) | 0 | 0 |
| contiguous DNA a wild-type parent pairs (nt) | 3 | 4 | 5 |
| most stable parent ΔG°37 (kcal/mol) | −7.77 | −8.66 | −10.25 |
| **Over the six seams screened at every geometry** | | | |
| designs screened | 30 | 42 | 54 |
| median near-matches | 86.5 | 15 | 0 |
| median gap-spanning cleavage risks | 21 | 0 | 0 |
| designs carrying none | 8 of 30 | 28 of 42 | 54 of 54 |
| most risk loci on any one design | 7 | 2 | 0 |
| designs with no near-match at all | 0 of 30 | 7 of 42 | 39 of 54 |
| **Over each geometry's whole design space** | | | |
| junction-spanning registers per seam | 5 | 7 | 9 |
| fusion-specific designs | 190 | 266 | 342 |
| best gap-level margin available | 3 | 4 | 5 |
| a mature parent can pair the whole gap | 181 of 190 | 130 of 266 | 87 of 342 |
| parent pairs ≥5 nt of contiguous gap DNA, a ten-base-pair hybrid | 76 of 190 | 228 of 266 | 342 of 342 |
| designs pairing the gap in parent pre-mRNA | 19 of 190 | 11 of 266 | 9 of 342 |
| median most stable parent ΔG°37 (kcal/mol) | −8.66 | −11.60 | −14.58 |
