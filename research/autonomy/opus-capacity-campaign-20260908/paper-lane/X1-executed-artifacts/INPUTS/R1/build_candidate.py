# R1 lane. Builds a PROPOSED candidate revision from the committed baseline.
# Writes ONLY inside /tmp/claude-0/r1-lane/. Reads the baseline copy exported via git show.
import io, sys
SRC="/tmp/claude-0/r1-lane/BASELINE-emc-atr-collaborator-package.md"
DST="/tmp/claude-0/r1-lane/PROPOSED-emc-atr-collaborator-package.md"
t=open(SRC).read()
edits=[]
def rep(tag, old, new):
    global t
    assert old in t, "MISS: "+tag+" :: "+old[:60]
    n=t.count(old)
    t=t.replace(old,new)
    edits.append((tag,n))

# ---- M1 Abstract: seam arithmetic (artifact type2_seam; test line 32) ----
rep("M1 abstract 177nt",
"""carries 176 nucleotides of NR4A3 5' untranslated sequence in the EWSR1 reading frame, encoding 59
residues that the protein-level model in general use does not contain.""",
"""places 177 nucleotides in the EWSR1 reading frame between the two moieties: one donated by EWSR1
across the seam and 176 supplied by NR4A3, of which 174 come from exon 2 and 2 from exon 3. They
encode 59 residues that this programme's own earlier protein-level model did not contain.""")

# ---- M2 Abstract: rank / bracketing (artifact counted_fusion_type_frequencies, recruitment_axis_rows) ----
rep("M2 abstract rank+bracket",
"""Retained EWSR1 RG dipeptide
counts place the two commonest EMC fusions at 0 of 30 and 8 of 30, bracketing the two fusions in
which the mechanism has been measured.""",
"""Type 1 is the commonest reported type in every
series that types its cases; type 2 is a minority variant, counted once across three counted series.
Retained EWSR1 RG dipeptide counts place type 1 at 8 of 30 and type 2 at 0 of 30, against a measured
comparator span of 0.000 to 0.267 for EWSR1::ATF1 and firmly measured positions at 0.000 and 1.000.""")

# ---- M3 3.3 seam arithmetic ----
rep("M3 s3.3 177nt",
"""The named 3' exon of the type-2 junction, NR4A3 exon 2, is entirely non-coding, so the fusion mRNA
carries 176 nucleotides of NR4A3 5' untranslated sequence downstream of the EWSR1 cut. Read in the
EWSR1 frame that segment contains no stop codon and encodes 59 residues lying between EWSR1(1-264)
and NR4A3's own methionine.""",
"""The named 3' exon of the type-2 junction, NR4A3 exon 2, is entirely non-coding, so the fusion mRNA
carries 176 nucleotides of NR4A3 5' untranslated sequence downstream of the EWSR1 cut. EWSR1 coding
sequence runs through exon 7 to nucleotide 793, which is 264 complete codons and one base over, and
that base completes the first codon of the extension. The 59 residues therefore span 177 nucleotides,
one donated by EWSR1 across the seam and 176 supplied by NR4A3, of which 174 come from exon 2 and 2
from exon 3. Read in the EWSR1 frame the segment contains no stop codon; the first residue is the
hybrid codon AAG, encoding lysine at position 265 of the chimera, and the remaining 58 are NR4A3
sequence read in a non-native frame. The insertion lies between EWSR1(1-264) and NR4A3's own
methionine, and the chimeric open reading frame is 949 aa.""")

rep("M4 s3.3 general-use model",
"""therefore not EWSR1(1-264)::NR4A3(1-626), the protein-level model in general use and the one this
programme itself used until this analysis.""",
"""therefore not EWSR1(1-264)::NR4A3(1-626), the protein-level model this programme itself used until
this analysis. No source retrieved states what protein-level model the field uses. An N-terminal
addition ahead of NR4A3's initiator is not itself novel: reference 3 describes a cryptic exon in
NR4A3 intron 2 "thus encoding 25 additional amino acids prior to the NR4A3 ATG" in a rarer
TAF15::NR4A3 isoform. What is specific here is the junction and the sequence of its insertion.""")

# ---- M5 Table 1 reported rank (artifact counted_fusion_type_frequencies) ----
rep("M5 table1 rank col",
"| fusion | junction | reported rank | sources |",
"| fusion | junction | counted frequency | sources |")
rep("M5 table1 type1",
"| EWSR1::NR4A3 type 1 | EWSR1 e12 to NR4A3 e3 | commonest |",
"| EWSR1::NR4A3 type 1 | EWSR1 e12 to NR4A3 e3 | commonest in every series that types its cases: 10 of 15 [7], 11 of 15 [9] |")
rep("M5 table1 type2",
"| EWSR1::NR4A3 type 2 | EWSR1 e7 to NR4A3 e2 | second |",
"| EWSR1::NR4A3 type 2 | EWSR1 e7 to NR4A3 e2 | minority variant, counted once across three counted series: 1 of 15 [9], absent from the counted types of [7] |")
rep("M5 table1 type5",
"| EWSR1::NR4A3 type 5 | EWSR1 e13 to NR4A3 e3 | minority |",
"| EWSR1::NR4A3 type 5 | EWSR1 e13 to NR4A3 e3 | named second commonest in [7], 2 of 15 |")
rep("M5 table1 taf15",
"| TAF15::NR4A3 | TAF15 e6 to NR4A3 e3 | the only reported coding junction |",
"| TAF15::NR4A3 | TAF15 e6 to NR4A3 e3 | the only reported coding junction; 3 of 15 [9], 4 of 10 [10] |")

# ---- M6 Table 4 -> status column, restored rows, no "bracket"/"interpolate" ----
rep("M6 table4",
"""| construct | 5' partner retained | RG kept | fraction | status |
|---|---|---|---|---|
| EWSR1-FLI1, the study's reference fusion | EWSR1(1-264) | 0 / 30 | 0.000 | measured |
| EWSR1::NR4A3 type 2 | EWSR1(1-264) | 0 / 30 | 0.000 | predicted (P1) |
| TAF15::NR4A3 | TAF15(1-161) | 0 / 31 | 0.000 | predicted (P3) |
| EWSR1::ATF1 e8, commonest clear-cell type | EWSR1(1-324) | 7 / 30 | 0.233 | measured, phenotype present |
| EWSR1::ATF1 e10 | EWSR1(1-348) | 8 / 30 | 0.267 | measured |
| EWSR1::NR4A3 type 1, commonest EMC | EWSR1(1-431) | 8 / 30 | 0.267 | predicted (P2) |
| EWSR1::NR4A3 type 5 | EWSR1(1-472) | 11 / 30 | 0.367 | predicted |
| EWSR1-RGG(3)-FLI1 and native EWSR1 | full length | 30 / 30 | 1.000 | measured |""",
"""| construct | 5' partner retained | RG kept | fraction | status |
|---|---|---|---|---|
| EWSR1-FLI1 (0 RGG domains), reference 1's reference fusion | EWSR1(1-264) | 0 / 30 | 0.000 | measured in reference 1 |
| EWSR1-RGG(1)-FLI1 | not identified | not placeable | not placeable | measured in reference 1; reference 1 does not identify which RGG-rich domain was reintroduced, so its retained RG count is unknown |
| EWSR1-RGG(3)-FLI1 and native EWSR1 | full length | 30 / 30 | 1.000 | measured in reference 1 |
| EWSR1::FLI1 (Ewing, type 1), EWSR1 e7 | EWSR1(1-264) | 0 / 30 | 0.000 | a reported breakpoint of a disease in which the mechanism was measured |
| EWSR1::ATF1 (clear cell, reported type), EWSR1 e7 | EWSR1(1-264) | 0 / 30 | 0.000 | a reported breakpoint of a disease in which the mechanism was measured |
| EWSR1::ATF1 (clear cell, commonest type), EWSR1 e8 | EWSR1(1-324) | 7 / 30 | 0.233 | a reported breakpoint of a disease in which the mechanism was measured |
| EWSR1::ATF1, EWSR1 e10 | EWSR1(1-348) | 8 / 30 | 0.267 | a reported breakpoint of a disease in which the mechanism was measured |
| EWSR1::NR4A3 type 2 | EWSR1(1-264) | 0 / 30 | 0.000 | computed here; predicted |
| TAF15::NR4A3 | TAF15(1-161) | 0 / 31 | 0.000 | computed here; predicted |
| EWSR1::NR4A3 type 1 | EWSR1(1-431) | 8 / 30 | 0.267 | computed here; predicted |
| EWSR1::NR4A3 type 5 | EWSR1(1-472) | 11 / 30 | 0.367 | computed here; predicted |

Reference 1 built one EWSR1-ATF1 construct and the retrieved text does not state its EWSR1
breakpoint. Three EWSR1::ATF1 breakpoints are reported, retaining 0, 7 and 8 of 30 RG dipeptides, so
the EWSR1::ATF1 comparator is a span from 0.000 to 0.267 rather than a point. The firmly measured
positions on this axis are 0.000 and 1.000.""")

rep("M7 s3.4 p2 bracket/interpolate/byte-identical",
"""EMC's two main fusion types bracket the two fusions in which the mechanism was measured. Type 2
sits where EWSR1-FLI1 sits, at zero, on a retained segment reported as byte-identical over the
shared prefix. Type 1 sits at 0.267 against 0.233 for the commonest reported clear-cell type and
0.267 for the exon 10 type. Neither EMC type extrapolates beyond the published series; both
interpolate between points already measured.""",
"""Type 2 sits where EWSR1-FLI1 sits, at zero, on a retained EWSR1 segment identical in sequence over
the shared prefix. Type 1 sits at 0.267, inside the reported EWSR1::ATF1 span of 0.000 to 0.267.
Neither EMC type falls outside the range of retained-RG fractions the reported breakpoints of the
measured diseases already cover; neither is placed between two positions measured in reference 1,
because only 0.000 and 1.000 were measured there.""")

rep("M8 s3.4 margin 13",
"""and TAF15's first RG dipeptide falls at residue 175, so the junction lies inside the strict zero-RG
window with 14 residues of margin, where the earlier sweep could report only a range of 100 to 170.""",
"""and TAF15's first RG dipeptide falls at residue 175, so the junction lies inside the strict zero-RG
window with 13 residues of margin, where the earlier sweep could report only a range of 100 to 170.
Margin is stated here as the RG-free ceiling (174, the largest retained length carrying no RG
dipeptide) minus the retained length (161), the convention the census uses; the distance to the
first RG position is one greater.""")

# ---- M9 Table 5 symmetric sweep ----
rep("M9 table5 sweep row",
"| best [S,Y,G,Q] over every prefix, 50 aa to full length, 66 prefixes | as above | 0.400, at residues 1-160 | decisive; no TCF12 prefix reaches the lowest FET value |",
"| symmetric [S,Y,G,Q] sweep, every prefix from 50 aa to full length in 10-aa steps, all four proteins on the same grid | lowest FET prefix value 0.439 (EWSR1, residues 1-560) | best TCF12 prefix 0.400, at residues 1-160 | separates, by 0.039; no TCF12 prefix of any length reaches the lowest value any FET prefix takes |")

# ---- M10 3.5 restate margin honestly ----
rep("M10 s3.5 robustness",
"""TCF12 has no RGG box, roughly a quarter of the RG content, and no
N-terminal prefix of any length reaching the FET compositional range, which makes the
classification robust to the unpinned TCF12 breakpoint.""",
"""TCF12 has no RGG box, roughly a quarter of the RG content, and no
N-terminal prefix of any length reaching the lowest value any FET prefix takes, which makes the
classification robust to the unpinned TCF12 breakpoint. The margin on that sweep is 0.039 and the
published version of the comparison, which gave TCF12 every prefix and the FET proteins one fixed
250-residue window, overstated it.""")

# ---- M11 P1 basis, P3 margin ----
rep("M11 p1 byte-identical",
"Basis: 0 of 30 RG retained, on a segment byte-identical to the reference construct's",
"Basis: 0 of 30 RG retained, on a segment identical in sequence to the reference construct's")
rep("M12 p3 margin",
"Basis: TAF15(1-161) retains 0 of 31, with 14 residues of margin to TAF15's first RG at 175",
"Basis: TAF15(1-161) retains 0 of 31, with 13 residues of headroom below the RG-free ceiling of 174 and TAF15's first RG at 175")

# ---- M13 register: "the source" -> reference 1 ; "this programme" -> the present analysis ----
for old,new in [
 ("which no experiment in the source performs","which no experiment in reference 1 performs"),
 ("the source's own data show a second variable","reference 1's own data show a second variable"),
 ("because the source reports it that way","because reference 1 reports it that way"),
 ("the source showed that a DNA-binding-domain mutation","Gracilla and colleagues showed that a DNA-binding-domain mutation"),
 ("the EMC analogue of the source's GFP-FLI1 control","the EMC analogue of reference 1's GFP-FLI1 control"),
 ("behaving like the source's full-length FLI1 control","behaving like reference 1's full-length FLI1 control"),
 ("EWSR1, which the source shows contributes","EWSR1, which reference 1 shows contributes"),
]:
    rep("M13 register", old, new)

# ---- M14 3.2: the frame rule as one rule (artifact frame_rule) ----
rep("M14 frame rule",
"""All four are in frame. Each splits a codon across the junction, which is why the frame was computed
at the nucleotide level rather than inferred from residue arithmetic.""",
"""All four are in frame. Each splits a codon across the junction, which is why the frame was computed
at the nucleotide level rather than inferred from residue arithmetic.

The four junctions are four instances of one rule rather than four checked examples. A 5' partner
exon joined to NR4A3 exon 2 or exon 3 is in frame if and only if the donor exon ends one nucleotide
into a codon, that is if its cumulative coding nucleotide count is congruent to 1 modulo 3. Both
acceptors give the same register, because NR4A3 exon 2 is 174 nucleotides, a multiple of three. The
rule was evaluated over every donor and acceptor pair rather than over the reported junctions alone,
and across EWSR1's seventeen coding exons the complete phase-1 donor set is exons 1, 4, 7, 9, 10, 12,
13 and 15.""")

open(DST,"w").write(t)
for e in edits: print(e)
print("WROTE", DST)
