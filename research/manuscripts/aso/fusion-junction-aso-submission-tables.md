<!-- GENERATED — DO NOT EDIT. Regenerate: python3 research/manuscripts/submission_tables.py -->

# Tables — fusion-junction ASO submission

**Research use only, and not for administration to any person or animal.** Every oligonucleotide
sequence named in these tables is a research reagent intended solely for laboratory investigation.
None is a medicine or a candidate drug, none has been synthesised or tested by anyone, and none may
be administered to any human being or animal, compounded for such use, or supplied to any person for
such use. Custom oligonucleotide synthesis is commercially available, so the restriction is on use
rather than on access. The three designs the main text names as NOT to be carried forward — each
pairs its whole catalytic gap against the patient's own un-rearranged *NR4A3* allele — are **not** in
these tables; a table row is nevertheless not a recommendation, and the full statement is in the main
text's Declarations.

**Table 1. The in-frame junction space across five *NR4A3* fusion partners.** Every
donor-exon × *NR4A3*-acceptor-exon pair was graded against the frame condition before any design was
emitted. The gap-level margin is the number of junction-unique bases inside the six-nucleotide
catalytic gap on the shorter side of the junction. Frame compatibility is an arithmetic property of exon
structure and is not a claim about which junctions patients carry.

| 5′ partner | donor exons | exon pairs graded | in-frame | with ≥1 fusion-specific design | GC range of those designs (%) | best gap-level margin |
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
cleanest ones are in Table 3. The margin column is therefore the best among the designs that
RETURNED a screen at this depth: 7 of the panel's 190 default-depth submissions
failed at the remote service, which is why a junction can show fewer than five designs screened
here, and why Table 4 — which selects from the deeper re-screens — can name a design of higher
margin at the same junction. Near-match counts are of RefSeq
transcript accessions and are also given collapsed to distinct gene loci, since RefSeq carries one
accession per annotated variant. A “≥” marks a right-censored count: the screens store the top
15 hits per design, so a design with more is a lower bound. All 38 junction screens
are filtered by alignment orientation. `XM_`/`XR_` records are computationally
predicted gene models rather than curated transcripts, and are counted separately for that reason.
None of these numbers is a measurement of off-target activity.

¹ A near-match count is what the search returned on EITHER strand; a match on the strand opposite the target window cannot be hybridised by an antisense oligonucleotide and is not a liability. Across this corpus 44% of apparent gap-spanning hits (738 of 1,677) are of that kind, which is why the two columns differ and why the raw count alone should not be read as load. This column counts only the 15 RETAINED hits. The gap-spanning locus column is recounted from those hits wherever they are the complete list, and is exact there; a “≤” marks a truncated design, where the column instead carries the screen's own count over every ranked hit, computed under a locus assignment since corrected that split some genes across accessions and therefore over-counts. The two columns are not in conflict where a truncated design shows “≥0” sense-strand hits and a non-zero gap-spanning locus count: the sense-strand hits are real and simply fall outside the stored window, which is precisely why such a design cannot be called clean.

² Counted over the gap-spanning loci only, not over all of that design's near-match loci.

³ The same design re-screened at a tenfold deeper alignment ceiling, with retention raised to match it so that no hit list is truncated. Because no list is truncated, the gap-spanning locus column at this depth is recounted from the complete stored hits under the current locus assignment and is exact; it is not the screen's own stored figure, which was computed before that assignment was corrected and splits any gene whose description carries a comma across one accession per transcript variant. It is therefore the same quantity, counted the same way, as the locus figures in Table 4 and in the Results. The three columns are the counterparts of the default-depth columns to their left, given beside them rather than in place of them because the default depth is where the corpus-wide counts elsewhere in the paper were computed and the two must stay comparable. Read together they are the paper's censoring result at the level of a single row: a default-depth count is a lower bound whether or not it reached the 50-hit cap, and three junctions whose default cell reads zero in the gap-spanning column carry gap-spanning hits at ten times the depth. Three of the panel's 190 records failed at this ceiling; they are absent from the deep set rather than counted as zero in it.

| junction | designs screened | best gap-level margin | that design | near-matches, either strand (transcripts → loci) | of the retained hits, on the sense strand¹ | loci with a gap-spanning hit | of those, predicted models only² | at the deeper ceiling: near-matches³ | of those, on the sense strand³ | loci with a gap-spanning hit³ | ≤1-mismatch matches across that junction's designs, median (max) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EWSR1 e10::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTAGATCA-3′ | 35 → ≥2 | ≥15 | ≤4 | 0 | 138 | 137 | 5 | 4 (32) |
| EWSR1 e12::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATCAAAC-3′ | 9 → 4 | 6 | 1 | 1 | 189 | 141 | 6 | 2 (22) |
| EWSR1 e13::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCACGG-3′ | 31 → ≥3 | ≥12 | ≤2 | 0 | 63 | 47 | 2 | 2 (25) |
| EWSR1 e15::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCGGGGGC-3′ | 36 → ≥2 | ≥12 | ≤1 | 0 | 93 | 62 | 1 | 1 (10) |
| EWSR1 e1::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCGTGGAC-3′ | 0 → 0 | 0 | 0 | 0 | 27 | 18 | 0 | 0 (0) |
| EWSR1 e4::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCAGTGGGA-3′ | 11 → 4 | 11 | 3 | 2 | 90 | 67 | 8 | 4 (10) |
| EWSR1 e7::NR4A3 e3 | 5 | 3 | 5′-GGGCATATTCTGCTGC-3′ | 32 → ≥9 | ≥6 | ≤2 | 0 | 300 | 65 | 6 | 9 (21) |
| EWSR1 e9::NR4A3 e3 | 2 | 3 | 5′-GGGCATATCACCAGGC-3′ | 29 → ≥2 | ≥6 | ≤2 | 0 | 165 | 81 | 7 | 1 (22) |
| FUS e10::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATCAAAC-3′ | 9 → 4 | 6 | 1 | 1 | 189 | 141 | 6 | 2 (22) |
| FUS e11::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCTCGC-3′ | 30 → ≥1 | ≥15 | ≤1 | 0 | 60 | 30 | 1 | 0 (3) |
| FUS e13::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCATGTGA-3′ | 6 → 5 | 2 | 2 | 1 | 20 | 8 | 2 | 1 (9) |
| FUS e1::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCGTTTGAG-3′ | ≥50 → ≥7 | ≥13 | ≤1 | 0 | 129 | 116 | 2 | 10 (38) |
| FUS e3::NR4A3 e3 | 4 | 3 | 5′-GGGCATATTGTTCTGG-3′ | 18 → ≥4 | ≥1 | ≤2 | 0 | 148 | 34 | 4 | 3 (23) |
| FUS e5::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCACCT-3′ | 32 → ≥8 | ≥8 | ≤2 | 1 | 127 | 47 | 4 | 2 (3) |
| FUS e7::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCACCAAAT-3′ | 34 → ≥5 | ≥8 | ≤0 | 0 | 141 | 107 | 4 | 12 (39) |
| FUS e8::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCGGAGTCA-3′ | 4 → 3 | 3 | 1 | 0 | 4 | 3 | 1 | 0 (1) |
| TAF15 e11::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATCAAAC-3′ | 9 → 4 | 6 | 1 | 1 | 189 | 141 | 6 | 2 (22) |
| TAF15 e12::NR4A3 e3 | 4 | 2 | 5′-AGGGCATATCTCGCCG-3′ | 42 → ≥4 | ≥11 | ≤3 | 0 | 42 | 33 | 3 | 3 (4) |
| TAF15 e14::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCCTCCT-3′ | ≥50 → ≥2 | ≥11 | ≤2 | 0 | 174 | 95 | 6 | 19 (40) |
| TAF15 e1::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCGACATG-3′ | 5 → 2 | 0 | 0 | 0 | 5 | 0 | 0 | 0 (0) |
| TAF15 e4::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGACTGA-3′ | 34 → ≥3 | ≥15 | ≤4 | 1 | 78 | 57 | 7 | 10 (53) |
| TAF15 e6::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTTGTGTG-3′ | 11 → 7 | 7 | 4 | 2 | 62 | 10 | 5 | 2 (2) |
| TAF15 e8::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCACCAAAA-3′ | 41 → ≥4 | ≥13 | ≤2 | 0 | 133 | 93 | 3 | 10 (17) |
| TAF15 e9::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCAGCATCT-3′ | 23 → ≥7 | ≥0 | ≤2 | 0 | 68 | 48 | 5 | 1 (4) |
| TCF12 e11::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTAGAATG-3′ | 15 → 5 | 2 | 1 | 1 | 46 | 17 | 4 | 2 (6) |
| TCF12 e13::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGTGAGA-3′ | 17 → ≥8 | ≥6 | ≤1 | 1 | 170 | 80 | 4 | 1 (12) |
| TCF12 e17::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCTATAA-3′ | 8 → 3 | 0 | 0 | 0 | 118 | 101 | 5 | 1 (6) |
| TCF12 e19::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTCTGACT-3′ | 12 → 4 | 8 | 1 | 1 | 102 | 79 | 3 | 1 (2) |
| TCF12 e3::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGATCCA-3′ | 15 → 4 | 10 | 2 | 2 | 374 | 246 | 6 | 2 (35) |
| TCF12 e5::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCCATCAGA-3′ | 26 → ≥1 | ≥15 | ≤17 | 0 | 83 | 70 | 1 | 2 (32) |
| TCF12 e7::NR4A3 e3 | 4 | 2 | 5′-GGCATATCAAGCGCTG-3′ | 2 → 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 (1) |
| TCF12 e9::NR4A3 e3 | 4 | 3 | 5′-GGGCATATCTTGCATA-3′ | 14 → 2 | 8 | 1 | 0 | 86 | 64 | 6 | 8 (23) |
| TFG e2::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTTCATCT-3′ | ≥50 → ≥1 | ≥15 | ≤2 | 0 | 207 | 117 | 5 | 35 (87) |
| TFG e3::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCAAATAAT-3′ | 14 → 6 | 9 | 3 | 0 | 217 | 161 | 6 | 9 (17) |
| TFG e4::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCATTTTCA-3′ | ≥50 → ≥3 | ≥15 | ≤5 | 2 | 318 | 238 | 15 | 41 (100) |
| TFG e5::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGAAACC-3′ | 41 → ≥6 | ≥11 | ≤7 | 1 | 112 | 72 | 10 | 3 (21) |
| TFG e6::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTTCAATC-3′ | 37 → ≥3 | ≥2 | ≤0 | 0 | 238 | 193 | 3 | 11 (21) |
| TFG e7::NR4A3 e3 | 5 | 3 | 5′-GGGCATATCTGAATAC-3′ | 27 → ≥3 | ≥3 | ≤3 | 1 | 43 | 12 | 4 | 4 (26) |

**Table 3. The 9 designs with no sense-strand near-match at the default search depth.** Six of
these lose the property when the same junctions are re-screened at a tenfold deeper alignment
ceiling, three of them having returned no near-match at all here; §2.4 reports that
measurement and names the three that survive it. This table is the default-depth result, retained
because it is the depth at which the corpus-wide counts elsewhere in the paper were computed. Every design at the 6 junctions
where one exists. A design qualifies only
if its retained hit list is not truncated — no more near-matches than the 15 the screens store — because the
strand of an unstored hit cannot be recovered, so a truncated list cannot establish that nothing
on the sense strand remains. The underlying search is itself capped, so these are the designs whose
near-match lists are shortest, not the designs whose lists are known to be exhaustive. ΔΔG°37 is the margin by which the fusion duplex is favoured over the best
duplex either parent can form, for an unmodified DNA:RNA hybrid; because the fusion duplex pairs
both LNA wings and each parent duplex only one, it is a lower bound on the modified
oligonucleotide's discrimination rather than an upper one. None of these numbers is a measurement of off-target
activity, and none speaks to cleavage.

⁴ Under the optimistic five-fold and the pessimistic
no-discrimination bound on RNase-H1 single-mismatch discrimination. A single value means the two
bounds agree.

⁵ Of four conventional antisense design rules: GC within 40–60%, no G-quadruplex
motif, no homopolymer run of four, no CpG dinucleotide.

⁶ Whether the design still carries no
sense-strand near-match once its junction is re-screened at the tenfold deeper ceiling. The verdict
is computed from the three deep columns beside it, not asserted, so this table cannot come to
disagree with §2.4 about which designs survive. The six that do not are the reason this table's
default-depth zeros must not be read on their own.

| design | junction | GC (%) | gap-level margin | ΔΔG°37 (kcal/mol) | near-matches, either strand | of those, on the sense strand | exact / ≤1-mismatch matches | residual cleavage load, both bounds⁴ | conventional rules failed⁵ | at the deeper ceiling: near-matches | of those, on the sense strand | loci with a gap-spanning hit | survives⁶ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5′-GCATATCCGTGGACGC-3′ | EWSR1 e1::NR4A3 e3 | 62.5 | 1 | 7.981 | 0 | 0 | 0 / 0 | 0 | GC outside 40–60%, contains a CpG | 84 | 83 | 1 | **no** |
| 5′-GGCATATCCGTGGACG-3′ | EWSR1 e1::NR4A3 e3 | 62.5 | 2 | 10.085 | 0 | 0 | 0 / 0 | 0 | GC outside 40–60%, contains a CpG | 29 | 22 | 0 | **no** |
| 5′-GGGCATATCCGTGGAC-3′ | EWSR1 e1::NR4A3 e3 | 62.5 | 3 | 12.189 | 0 | 0 | 0 / 0 | 0 | GC outside 40–60%, contains a CpG | 27 | 18 | 0 | **no** |
| 5′-AGGGCATATCGGAGTC-3′ | FUS e8::NR4A3 e3 | 56.2 | 2 | 10.895 | 3 | 0 | 0 / 0 | 0 | contains a CpG | 3 | 0 | 0 | yes |
| 5′-GGGCATATCCGACATG-3′ | TAF15 e1::NR4A3 e3 | 56.2 | 3 | 11.894 | 5 | 0 | 0 / 0 | 0 | contains a CpG | 5 | 0 | 0 | yes |
| 5′-GGGCATATCTCTATAA-3′ | TCF12 e17::NR4A3 e3 | 37.5 | 3 | 8.556 | 8 | 0 | 0 / 0 | 0 | GC outside 40–60% | 118 | 101 | 5 | **no** |
| 5′-GCATATCAAGCGCTGC-3′ | TCF12 e7::NR4A3 e3 | 56.2 | 1 | 7.98 | 1 | 0 | 0 / 0 | 0 | contains a CpG | 18 | 2 | 0 | **no** |
| 5′-GGCATATCAAGCGCTG-3′ | TCF12 e7::NR4A3 e3 | 56.2 | 2 | 10.085 | 2 | 0 | 0 / 0 | 0 | contains a CpG | 2 | 0 | 0 | yes |
| 5′-CAGGGCATATCTTGCA-3′ | TCF12 e9::NR4A3 e3 | 50.0 | 1 | 9.325 | 7 | 0 | 0 / 0 | 0 | none | 67 | 18 | 4 | **no** |

**Table 4. The best available design at each of the 38 in-frame junctions.** Tables 2 and 3
select across the panel; this table selects within each junction, which is the question a patient's
fusion poses. Designs are ranked by parent liability first, since sparing the wild-type parents is
what the modality exists for, then by pre-mRNA sites, then by distinct gene loci, with ties broken
on gap-level margin rather than on raw hit counts. Nothing was re-screened: every field is joined
from a screen already reported above. Whether a junction has a published exon-resolved breakpoint is
reported separately from specificity and never folded into the ranking — “published” means an
exon-resolved EMC breakpoint is reported for that exon pair; “published (deposit)” that the exon is
resolved by a deposited chimeric mRNA record with no peer-reviewed report behind it, which §2.3
describes; “exon not reported” that a published report resolves a breakpoint of that partner at a
different exon; and “none published” that no published report resolves any breakpoint of that
partner to an exon. The last two are drawn on the published record alone, so one partner can carry
a “published (deposit)” row and “none published” rows at once — *TFG* is that case here, and the
deposit is why its exon-7 row is not one of them. “None published” is absence of evidence: EMC case
reports usually name the partner gene without sequencing to nucleotide resolution. Gap-paired
near-matches are at the tenfold deeper alignment ceiling, where every hit list is complete. The
genome column is the observed number of gap-paired sites at ≤2 mismatches over the number expected
for an arbitrary 16-mer, so 1.00 is chance. A junction with no design clearing the parent screen is
reported as such rather than given a best row.

| junction | exon-resolved breakpoint | designs clearing the parent screen | best available design | gap-level margin | longest parent duplex through the gap (bp) | gap-paired near-matches at the deeper ceiling (transcripts → loci) | genome-wide gap-paired load, observed/expected |
|---|---|---|---|---|---|---|---|
| EWSR1 e10::NR4A3 e3 | exon not reported | 3 of 5 | 5′-GGCATATCTAGATCAA-3′ | 2 | 7 | 70 → 4 | 0.61 |
| EWSR1 e12::NR4A3 e3 | published | 4 of 5 | 5′-GGGCATATCATCAAAC-3′ | 3 | 8 | 123 → 6 | 0.62 |
| EWSR1 e13::NR4A3 e3 | published | 3 of 5 | 5′-GGGCATATCTCCACGG-3′ | 3 | 8 | 24 → 2 | 0.29 |
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
| TCF12 e11::NR4A3 e3 | exon not reported | 3 of 5 | 5′-GGCATATCTAGAATGC-3′ | 2 | 8 | 4 → 3 | 0.69 |
| TCF12 e13::NR4A3 e3 | exon not reported | 2 of 5 | 5′-GGCATATCTGTGAGAG-3′ | 2 | 7 | 6 → 5 | 1.08 |
| TCF12 e17::NR4A3 e3 | exon not reported | 3 of 5 | 5′-GGGCATATCTCTATAA-3′ | 3 | 7 | 14 → 5 | 0.83 |
| TCF12 e19::NR4A3 e3 | exon not reported | 2 of 5 | 5′-GGGCATATCTCTGACT-3′ | 3 | 8 | 75 → 3 | 0.82 |
| TCF12 e3::NR4A3 e3 | exon not reported | 0 of 5 | — | — | — | — | — |
| TCF12 e5::NR4A3 e3 | published | 4 of 5 | 5′-GGGCATATCCATCAGA-3′ | 3 | 7 | 17 → 1 | 0.56 |
| TCF12 e7::NR4A3 e3 | exon not reported | 2 of 5 | 5′-GGGCATATCAAGCGCT-3′ | 3 | 8 | 0 → 0 | 0.26 |
| TCF12 e9::NR4A3 e3 | exon not reported | 1 of 5 | 5′-GGGCATATCTTGCATA-3′ | 3 | 8 | 39 → 6 | 0.71 |
| TFG e2::NR4A3 e3 | none published | 0 of 4 | — | — | — | — | — |
| TFG e3::NR4A3 e3 | none published | 4 of 5 | 5′-GGGCATATCAAATAAT-3′ | 3 | 8 | 18 → 6 | 1.35 |
| TFG e4::NR4A3 e3 | none published | 1 of 5 | 5′-AGGGCATATCATTTTC-3′ | 2 | 7 | 82 → 12 | 1.77 |
| TFG e5::NR4A3 e3 | none published | 2 of 5 | 5′-GGCATATCTGAAACCT-3′ | 2 | 8 | 34 → 7 | 1.38 |
| TFG e6::NR4A3 e3 | none published | 3 of 5 | 5′-GGGCATATCTTCAATC-3′ | 3 | 9 | 29 → 3 | 0.73 |
| TFG e7::NR4A3 e3 | published (deposit) | 2 of 5 | 5′-GGCATATCTGAATACT-3′ | 2 | 9 | 24 → 6 | 1.24 |

**Table 5. Gap length against junction specificity, at one junction and across the design space.** The
same junctions tiled and screened at three gapmer geometries, wing held at five nucleotides so that only
the catalytic gap changes. Inside the gap the junction-unique bases on the shorter side and the
bases one wild-type parent pairs on the longer side are complements: they sum to the gap, which the
generating module asserts for every design rather than assuming. Within one geometry the gap is
fixed, so each nucleotide of gap-level margin is one FEWER nucleotide of contiguous
wild-type-parent duplex; what raises the parent-paired run at every register is a longer gap, which
is the only way past a geometry's ceiling of half its gap rounded down. The two directions are
reported separately and never combined into a score. Near-match counts fall partly for a reason the
instrument guarantees rather than measures: at a fixed budget of two mismatches every locus a longer
design can reach is also reached by each of its own shorter sub-windows, so the set can only shrink,
and two mismatches is a fractionally stricter test at 20 nucleotides than at 16. Only the size of
the fall and which designs reach zero are measurements. The three blocks carry different
denominators and are not comparable across blocks: the junction block is one molecule, the matched-junction
block is the six junctions every geometry was screened at, and the corpus block is each geometry's
whole design space, which is not screened at the same junctions. The exhaustive GRCh38 genome scan
is unavailable at 18 and 20 nucleotides by construction, so no row reports it. Two of the corpus rows
carry a ten-base-pair criterion and they are not the same measurement. “…and that duplex reaches ten
base pairs” is the mature-parent screen, a search over every window of all six parent transcripts,
and it is the row §2.5's 87 of 190 and §2.9's 87 / 88 / 87 are read from. “At the design's own seam”
is arithmetic on the junction itself: because the wing is five throughout, a parent's hybrid at that
seam is five base pairs plus its share of the gap, so pairing five nucleotides of contiguous gap DNA
and reaching a ten-base-pair seam hybrid are the same condition and are reported as one row. ΔG°37 values are for
an unmodified DNA:RNA hybrid; the wing is five at every geometry, so LNA affinity enters each parent
duplex identically and cannot explain a difference between the columns. None of these numbers is a
measurement of cleavage.

| | 5-6-5 (16-mer) | 5-8-5 (18-mer) | 5-10-5 (20-mer) |
|---|---|---|---|
| **At the *EWSR1* e12 / *TAF15* e11 / *FUS* e10 junction** | | | |
| design (5′→3′) | GGGCATATCATCAAAC | AGGGCATATCATCAAACC | CAGGGCATATCATCAAACCA |
| gap-level margin | 3 | 4 | 5 |
| sense-strand gap-spanning cleavage risks | 123 | 3 | 0 |
| gene loci carrying one | 6 | 1 | 0 |
| near-matches (≤2 mismatches, deeper ceiling) | 189 | 50 | 20 |
| ≤1-mismatch matches over 186,185 transcripts | 1 | 0 | 0 |
| mature-parent duplex through the whole gap (bp) | 8 (*TFG*) | 0 | 0 |
| contiguous DNA a wild-type parent pairs (nt) | 3 | 4 | 5 |
| most stable parent ΔG°37 (kcal/mol) | −7.77 | −8.66 | −10.25 |
| **Over the six junctions screened at every geometry** | | | |
| designs screened | 30 | 42 | 54 |
| median near-matches | 86.5 | 15 | 0 |
| median gap-spanning cleavage risks | 21 | 0 | 0 |
| designs carrying none | 8 of 30 | 28 of 42 | 54 of 54 |
| most risk loci on any one design | 7 | 2 | 0 |
| designs with no near-match at all | 0 of 30 | 7 of 42 | 39 of 54 |
| **Over each geometry's whole design space** | | | |
| junction-spanning registers per junction | 5 | 7 | 9 |
| fusion-specific designs | 190 | 266 | 342 |
| best gap-level margin available | 3 | 4 | 5 |
| a mature parent can pair the whole gap | 181 of 190 | 130 of 266 | 87 of 342 |
| …and that duplex reaches ten base pairs, the criterion applied throughout | 87 of 190 | 88 of 266 | 87 of 342 |
| at the design's own seam, the parent pairs ≥5 nt of contiguous gap DNA | 76 of 190 | 228 of 266 | 342 of 342 |
| designs pairing the gap in parent pre-mRNA | 19 of 190 | 11 of 266 | 9 of 342 |
| median most stable parent ΔG°37 (kcal/mol) | −8.66 | −11.60 | −14.58 |

**Table 6. Where the clinically-relevant reagents' off-target loci are expressed.** Every gene
locus returned by the deeper screens at four of the five junctions with a published exon-resolved EMC breakpoint,
read against reference expression data. The two compartments answer different questions and are
never combined: a systemically dosed phosphorothioate gapmer distributes predominantly to liver and
kidney, so liver, kidney - cortex and kidney - medulla address exposure, while the soft-tissue column is the normal
tissue of the compartment EMC arises in and stands in for a tumour no reference atlas contains.
Values are GTEx v8 median TPM across each tissue's donors. The two cuts behind the last column are
stated for legibility and are not thresholds of concern: below 1 TPM in all three exposure
tissues reads as below detection, at or above 10 TPM in any of them as the level at which an
off-target hypothesis would have to be tested. Every raw median is released so another cut can be
applied without re-running. Gap-paired hit records are the gap-paired near-matches the deeper
screens returned at that locus, one per accession per design, added up over every design tiled
across the junction; the column totals 649, which is the gap-paired hit count over the
four junctions of this table and not over the whole 38-junction panel. It is a count of what the search returned and not of how many accessions RefSeq lists for
the gene, so it is not annotation depth and not a property of the locus on its own: a locus that
every register returns is counted once per register. Tiling registers is how many of the designs
tiled across that junction return the locus, which is robustness to where the window is placed; the
two columns therefore move together rather than being independent axes, and neither is ranked on,
neither is expression and neither is affinity. A locus with no reading carries the reason rather
than a zero, because an absent reading is not a reading of absence. Every hit behind this table sits at 14 of 16 identity, the loosest the screen admits, so
nothing here distinguishes these loci from one another on affinity. None of these numbers is a
measurement of cleavage, and no expression figure is a predicted cleavage event.

⁷ The denominator is how many designs at that seam THIS TABLE READS, and not how many junction-spanning registers the seam admits — 5 at every junction of this panel (Table 5). At the lead seam the multi-partner reagent's own screen is the only one read, so those rows carry a denominator of one; at the other seams no design is selected and every screened register is read, because a ranking is not a reagent and the union across registers is what the panel has to cover.

◆ A locus returned by the design Table 4 names as the best available at that seam, which is the molecule Table 7 prices and §4 names. The unmarked rows are returned by other registers tiled across the same junction and not by that reagent. The marker identifies and does not rank: every locus keeps its row, the union is still what this table reports, and a reagent's own loci are neither cleaner nor dirtier for being its own.

| junction | gene locus | gap-paired hit records | tiling registers returning it⁷ | Liver | Kidney - Cortex | Kidney - Medulla | soft-tissue proxy maximum | exposure-organ reading |
|---|---|---|---|---|---|---|---|---|
| EWSR1 e12::NR4A3 e3 | *ANKS1B* ◆ | 67 | 1 of 1 | 0.03 | 0.46 | 0.28 | 3.6 (Artery - Tibial) | below the lower cut in all three |
|  | *ZNF667* ◆ | 37 | 1 of 1 | 0.31 | 1.63 | 2.58 | 6.2 (Nerve - Tibial) | detectable, below the upper cut |
|  | *GMCL1* ◆ | 9 | 1 of 1 | 4.52 | 4.98 | 6.72 | 18.3 (Artery - Tibial) | detectable, below the upper cut |
|  | *LOC105374140* ◆ | 5 | 1 of 1 | — | — | — | — | no gene model — not measurable |
|  | *LOC105370997* ◆ | 4 | 1 of 1 | — | — | — | — | no gene model — not measurable |
|  | *CHST5* ◆ | 1 | 1 of 1 | 0.07 | 0.35 | 0.78 | 0.8 (Nerve - Tibial) | below the lower cut in all three |
| TAF15 e6::NR4A3 e3 | *G3BP2* | 56 | 2 of 5 | 11.92 | 17.03 | 23.12 | 77.0 (Cells - Cultured fibroblasts) | at or above the upper cut |
|  | *LINC02030* | 22 | 2 of 5 | 0.00 | 0.00 | 0.02 | 0.3 (Skin - Sun Exposed (Lower leg)) | below the lower cut in all three |
|  | *MIR9-2HG* | 18 | 2 of 5 | — | — | — | — | no reading taken |
|  | *LAMA4* | 13 | 1 of 5 | 1.28 | 3.13 | 6.06 | 268.6 (Cells - Cultured fibroblasts) | detectable, below the upper cut |
|  | *ZFPM2* ◆ | 12 | 3 of 5 | 0.64 | 0.55 | 0.40 | 9.6 (Artery - Tibial) | below the lower cut in all three |
|  | *GNAL* | 10 | 2 of 5 | 0.66 | 1.74 | 1.81 | 8.6 (Artery - Tibial) | detectable, below the upper cut |
|  | *NRP1* ◆ | 5 | 5 of 5 | 6.62 | 16.87 | 17.81 | 104.7 (Cells - Cultured fibroblasts) | at or above the upper cut |
|  | *SLC17A3* | 4 | 2 of 5 | 9.14 | 33.61 | 8.09 | 0.0 (Adipose - Subcutaneous) | at or above the upper cut |
|  | *CA5B* ◆ | 3 | 3 of 5 | 0.66 | 1.57 | 1.96 | 11.7 (Artery - Tibial) | detectable, below the upper cut |
|  | *CA5BP1-CA5B* ◆ | 3 | 3 of 5 | — | — | — | — | no reading taken |
|  | *EEFSEC* | 3 | 1 of 5 | 16.15 | 14.37 | 15.57 | 39.1 (Nerve - Tibial) | at or above the upper cut |
|  | *ANKRD26P3* | 1 | 1 of 5 | 0.00 | 0.00 | 0.00 | 0.0 (Muscle - Skeletal) | below the lower cut in all three |
|  | *GBP4* | 1 | 1 of 5 | 3.12 | 5.59 | 10.08 | 18.2 (Adipose - Subcutaneous) | at or above the upper cut |
|  | *LOC105376349* | 1 | 1 of 5 | — | — | — | — | no gene model — not measurable |
|  | *LOC124907518* ◆ | 1 | 1 of 5 | — | — | — | — | no gene model — not measurable |
|  | *NRXN3-AS1* | 1 | 1 of 5 | — | — | — | — | no reading taken |
|  | *ST3GAL1* | 1 | 1 of 5 | 28.58 | 16.36 | 8.06 | 27.2 (Muscle - Skeletal) | at or above the upper cut |
| EWSR1 e13::NR4A3 e3 | *FNBP1* ◆ | 42 | 2 of 5 | 7.08 | 12.12 | 14.06 | 56.5 (Nerve - Tibial) | at or above the upper cut |
|  | *EHMT2* | 34 | 2 of 5 | 6.89 | 13.23 | 16.70 | 53.0 (Nerve - Tibial) | at or above the upper cut |
|  | *ZNF215* | 27 | 1 of 5 | 0.13 | 0.67 | 1.27 | 5.2 (Cells - Cultured fibroblasts) | detectable, below the upper cut |
|  | *ESYT2* | 26 | 2 of 5 | 10.42 | 14.26 | 28.28 | 139.9 (Artery - Tibial) | at or above the upper cut |
|  | *LRP5L* | 8 | 2 of 5 | 7.83 | 6.32 | 11.16 | 8.0 (Nerve - Tibial) | at or above the upper cut |
|  | *CDC42SE1* ◆ | 6 | 2 of 5 | 22.74 | 44.73 | 78.97 | 187.6 (Nerve - Tibial) | at or above the upper cut |
|  | *THEMIS* | 6 | 1 of 5 | 0.13 | 0.08 | 0.18 | 0.3 (Adipose - Subcutaneous) | below the lower cut in all three |
|  | *LOC105374651* | 4 | 1 of 5 | — | — | — | — | no gene model — not measurable |
|  | *ZC3H4* | 4 | 1 of 5 | 6.41 | 5.89 | 9.71 | 26.2 (Nerve - Tibial) | detectable, below the upper cut |
|  | *ERBIN* | 2 | 1 of 5 | 9.80 | 9.38 | 14.68 | 43.8 (Cells - Cultured fibroblasts) | at or above the upper cut |
|  | *ZNF236* | 2 | 1 of 5 | 1.68 | 2.29 | 2.90 | 8.7 (Nerve - Tibial) | detectable, below the upper cut |
| TCF12 e5::NR4A3 e3 | *HNRNPA2B1* | 100 | 2 of 5 | 184.12 | 247.24 | 457.30 | 656.6 (Nerve - Tibial) | at or above the upper cut |
|  | *PIK3CG* ◆ | 51 | 3 of 5 | 0.14 | 0.17 | 0.37 | 1.2 (Adipose - Subcutaneous) | below the lower cut in all three |
|  | *MROH2A* | 28 | 1 of 5 | 1.04 | 0.42 | 0.07 | 0.3 (Skin - Sun Exposed (Lower leg)) | detectable, below the upper cut |
|  | *LINC02940* | 9 | 1 of 5 | — | — | — | — | no reading taken |
|  | *EXOC2* | 6 | 1 of 5 | 5.27 | 6.54 | 8.87 | 22.5 (Nerve - Tibial) | detectable, below the upper cut |
|  | *KCNG3* | 4 | 2 of 5 | 0.00 | 0.09 | 0.06 | 1.3 (Nerve - Tibial) | below the lower cut in all three |
|  | *PLAC8* | 4 | 2 of 5 | 1.43 | 0.32 | 0.30 | 0.7 (Adipose - Subcutaneous) | detectable, below the upper cut |
|  | *EFCAB11* | 2 | 1 of 5 | 0.37 | 0.92 | 1.20 | 2.1 (Cells - Cultured fibroblasts) | detectable, below the upper cut |
|  | *LOC107984281* | 2 | 2 of 5 | — | — | — | — | no gene model — not measurable |
|  | *LOC107985219* | 2 | 2 of 5 | — | — | — | — | no gene model — not measurable |
|  | *LOC107987169* | 1 | 1 of 5 | — | — | — | — | no gene model — not measurable |
|  | *LOC124905457* | 1 | 1 of 5 | — | — | — | — | no gene model — not measurable |

**Table 7. Every seam the coverage ladder qualifies, with the ladder's bounds and §4's two contrast
arms beside them, what each costs on each screen and what each buys in coverage.** The rows are in the order §4 decides them:
the two lead reagents, the rungs of the coverage ladder above them, the bounds above those, the
remaining junction with a published exon-resolved breakpoint and a reagent through all five deep
screens, the four *NR4A3* exon-2 acceptor seams reported beside the panel, and the two contrast
arms. Membership is the coverage ladder's and not this table's: every junction its best-supported
buildable panel qualifies — a published exon-resolved breakpoint and five completed deep screens,
each read from the table that owns it — has a row here whether or not §4 names its reagent, and the
generator refuses to build if one is missing. A row can therefore qualify and still buy no coverage,
which is a statement about the denominator and not about the reagent. Cumulative coverage is the
coverage of the reagent set through that row, so the two leads are
one rung and carry one figure between them; it is discounted by the breakpoint distribution of a
single series and is not a partner figure, and its interval is composed from each breakpoint
fraction's own Wilson bound rather than from the point estimate. Every rung and every bound prints
the increment it adds over the row above it, so no figure reads as bought by the row it sits on.
Each coverage figure and each increment is rounded to one decimal independently, from the unrounded
fraction rather than from each other, so a row's figure plus the increment printed on the row below
it need not reproduce that row's figure in the last place. A
bound row is what coverage would be if every remaining breakpoint of that partner were covered,
which nothing measures. A bound that names no reagent still has a row, and the *EWSR1* one is the
larger of the two steps between the last buildable rung and the table's top figure: the three
breakpoints it prices are ones the retrieved record does not resolve to an exon, so no sequence,
geometry or screen result exists for them and every such cell is empty. If those breakpoints are
private rather than recurrent, no stocked panel reaches them at any size. A row that
adds nothing prints why, because the two reasons differ: the partner is absent from the 58-case
cohort behind the denominator, or the partner is present and that exon pair carries no count in the
measured within-partner distribution. The exon-2 acceptor rows are from the non-canonical-acceptor
table and are never pooled into the panel, since the grade that excludes their junctions from the 38
is unchanged. A contrast arm carries no coverage figure and must not borrow its junction's, which is
already counted a row above. The three controls §4 requires have no row and can have none: the
fusion-negative isogenic comparator is a cell line rather than a reagent; the positive control is
specified as a class rather than a sequence, a gapmer against an abundant housekeeping transcript;
and the scrambled control is a draw from a stated shuffling procedure rather than one oligonucleotide.
None of the three therefore has a sequence, a geometry or a screen result for these columns. Gap-paired near-matches are at the tenfold deeper alignment ceiling
where every hit list is complete, and the parent duplex is the longest contiguous run containing the
whole catalytic gap, at the ten-base-pair criterion applied throughout. None of these numbers is a
measurement of off-target activity, and no row is a claim of efficacy.

| reagent | junction | sequence | geometry | gap-level margin | gap-paired near-matches → loci at the deeper ceiling | longest mature-parent duplex through the gap | cumulative coverage | basis |
|---|---|---|---|---|---|---|---|---|
| lead reagent | EWSR1 e12::NR4A3 e3 | 5′-GGGCATATCATCAAAC-3′ | 5-6-5 | 3 | 123 → 6 | 8 bp (*TFG*) | 68.4% (39.9–82.8) | single series, cumulative |
| lead reagent | TAF15 e6::NR4A3 e3 | 5′-GGGCATATCTTGTGTG-3′ | 5-6-5 | 3 | 8 → 5 | 9 bp (*TFG*) | 68.4% (39.9–82.8) | single series, cumulative |
| coverage rung | EWSR1 e13::NR4A3 e3 | 5′-GGGCATATCTCCACGG-3′ | 5-6-5 | 3 | 24 → 2 | 8 bp (*TCF12*) | 79.0% (50.3–89.2) (+10.6) | single series, cumulative |
| coverage rung | EWSR1 e7::NR4A3 e2 | 5′-CAGTGGGCTTCTGCTG-3′ | 5-6-5 | 2 | 51 → 7 | 8 bp (*TAF15*) | 79.0% (50.3–89.2) (+0.0) | single series, cumulative |
| coverage bound | BOUND — every remaining EWSR1 breakpoint covered | — (3 further reagents, none named) | — | — | — | — | 94.8% (+15.9) | arithmetic bound |
| coverage bound | TCF12 e5::NR4A3 e3 | 5′-GGGCATATCCATCAGA-3′ | 5-6-5 | 3 | 17 → 1 | 7 bp (*EWSR1*) | 98.3% (+3.4) | arithmetic bound |
| published seam in the panel | TFG e7::NR4A3 e3 | 5′-GGCATATCTGAATACT-3′ | 5-6-5 | 2 | 24 → 6 | 9 bp (*TAF15*) | adds nothing | partner absent from the cohort behind the denominator |
| beside the panel | EWSR1 e13::NR4A3 e2 | 5′-AGTGGGCTCTCCACGG-3′ | 5-6-5 | 3 | 25 → 6 | 8 bp (*EWSR1*) | adds nothing | partner in the cohort, this exon pair uncounted in it |
| beside the panel | TAF15 e6::NR4A3 e2 | 5′-AGTGGGCTCTTGTGTG-3′ | 5-6-5 | 3 | 128 → 6 | 9 bp (*NR4A3*) | adds nothing | partner in the cohort, this exon pair uncounted in it |
| beside the panel | PGR e2::NR4A3 e2 | 5′-AGTGGGCTCTTCCATT-3′ | 5-6-5 | 3 | 51 → 14 | 9 bp (*NR4A3*) | adds nothing | partner absent from the cohort behind the denominator |
| gap-length control | EWSR1 e12::NR4A3 e3 | 5′-AGGGCATATCATCAAACC-3′ | 5-8-5 | 4 | 3 → 1 | none | — | not a coverage row |
| margin contrast arm | EWSR1 e12::NR4A3 e3 | 5′-GCATATCATCAAACCA-3′ | 5-6-5 | 1 | 34 → 6 | 8 bp (*FUS*) | — | not a coverage row |
