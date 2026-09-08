#!/usr/bin/env python3
"""X1 step 2 - figure, new methods subsection, D5 move, preregistration explanation,
supplementary section, editorial counts. Every replacement asserted."""
import pathlib, re
L = pathlib.Path("/tmp/claude-0/x1-lane")
F = L / "PROPOSED-X1-emc-atr-collaborator-package.md"
t = F.read_text()
src = (L / "INPUTS/R1/PROPOSED-emc-atr-collaborator-package.md").read_text()
edits = []
def rep(tag, old, new, count=1):
    global t
    n = t.count(old); assert n == count, f"{tag}: found {n}"
    t = t.replace(old, new); edits.append(tag)

# --- fix: retain Appendix A verbatim from the UNEDITED input (step 1 retained a post-edit copy)
apx = src[src.index("## Appendix A. Superseded and corrected values"):]
(L / "RETAINED-APPENDIX-A-history.md").write_text(
    "# RETAINED VERBATIM: Appendix A of the input candidate\n\n"
    "Removed from the proposed submission copy ONLY because it is retained here, unaltered and\n"
    "byte-for-byte as it stands in the input. Nothing in it has been edited, shortened or reworded.\n"
    "Original history is never erased. Source:\n"
    "`INPUTS/R1/PROPOSED-emc-atr-collaborator-package.md` (its own Appendix A section).\n"
    "The same content is also carried in the committed changelog\n"
    "`research/manuscripts/dependency/emc-atr-collaborator-package-changelog.md`, which the input's\n"
    "own Appendix A header states it is the former Appendix A of.\n\n---\n\n" + apx)
edits.append("FIX-appendixA-verbatim-from-input")

# --- §3.2 prefix wording
rep("S2a-3.2-prefix",
    "whose decisive\ntests are compositional and are computed over every prefix.",
    "whose decisive\ntests are compositional and are computed over every prefix on the evaluated grid (section 3.5).")

# --- new Methods subsection 2.6
rep("S2b-methods-2.6",
    "\n## 3. Results\n",
    """
### 2.6 Exon numbering and its provenance

Every exon rank in this report is a transcript exon rank: exon *n* is the *n*-th exon of the named
transcript, counted from the transcript's first exon whether or not that exon is translated. The
primary sources quoted in section 3.1 state their breakpoints as exon numbers without stating which
numbering they use, so the correspondence is asserted here and not taken from the sources. Two
consequences follow and are stated rather than hidden. First, NR4A3 exons 1 and 2 are non-coding on
ENST00000395097, so a coding-exon rank and a transcript exon rank differ by two for this gene: the
label "NR4A3 exon 3" means the third exon of the transcript, which is NR4A3's first coding exon.
Second, the arithmetic is carried at the nucleotide level throughout, so an exon label never enters
a computation directly; it selects a boundary whose cumulative nucleotide count the artifact holds,
and the four gene-model assertions and three per-construct self-checks are what a reader should
audit.

The provenance of those boundaries is a single offline input cache, itself derived from UniProt and
Ensembl records (section 7). **This correspondence has not been verified against a second,
independent annotation source in this work.** No such verification was attempted here and none is
claimed: the exon-to-nucleotide map, the transcript choices and the coding-exon offsets all rest on
one retrieval into one cache. That is the same class of dependency that produced this programme's
documented off-by-two error (section 6, item 2), which an independent re-derivation caught. A
reader who needs the numbering to be right for their own case should re-derive it from their own
annotation source rather than rely on the correspondence asserted here.

## 3. Results
""")

# --- Figure 1
FIG = """**Figure 1.** Reported EMC junctions on the retained-RG axis, and the type-2 seam. Three panels,
drawn by [`emc_fusion_frame_figure.py`](../figures/emc_fusion_frame_figure.py) and committed as
[`emc-fusion-frame-fig1.png`](../figures/emc-fusion-frame-fig1.png) and
[`emc-fusion-frame-fig1.pdf`](../figures/emc-fusion-frame-fig1.pdf).

**Panel A.** Bars are drawn to residue scale on the shared axis. Each thin vertical tick marks one
RG dipeptide, at the 1-based position of its arginine
(`emc-fet-frame-and-composition.json`, `composition.rg_content.<protein>.rg_positions`); the count
printed at the right of each wild-type bar is that protein's total. Dashed rectangles mark
operationally defined RGG boxes — maximal merged runs of 60-residue windows each containing at least
six RG dipeptides, trimmed to start at the first RG the box contains and to end two residues past
its last RG-start (`emc_fet_idr_census.py`, `RGG_WINDOW = 60`, `RGG_MIN_RG_IN_WINDOW = 6`); the
spans drawn are `rgg_boxes_operational` in `emc-fet-construct-designs.json`. This finder returns two
boxes on EWSR1 and one on TAF15; the source paper names three RGG-rich domains in EWSR1, and the box
definition was deliberately not tuned to reproduce that count. NR4A3 has no box because the finder
returns none for it. `C166` is a printed text label placed above the NR4A3 bar with a single
vertical marker drawn on that bar at residue 166; it identifies that residue position and nothing
more, and no functional property is asserted for it here. Below the dotted rule, each fusion row
shows the retained 5' segment ending at a heavy end-cap at its breakpoint, carrying only the RG
ticks at or before that breakpoint; the right-hand text gives the retained residue range and the
retained-of-total RG count. Panel A carries four weights of vertical black line — RG tick, dashed
box outline, breakpoint end-cap and the `C166` marker — and the figure prints no key of its own, so
the reader is directed to this caption for all four.

**Panel B.** The retained-RG fraction axis, carrying the fusion positions of Table 3, the hatched
band labelled "position on this axis not determinable" for the construct whose reintroduced
RGG-rich domain the source does not identify, and the 0.000 to 0.267 interval spanned by the three
reported EWSR1::ATF1 breakpoints. That interval describes reported breakpoints; it is not a measured
recruitment range.

**Panel C.** The type-2 seam, drawn as NR4A3 exon 2 (174 nt, untranslated in NR4A3), one nucleotide
donated by EWSR1, and the resulting extension of 59 codons over 177 nt with no internal stop codon.
The panel does not print the words "type 2": it draws the EWSR1 exon 7 to NR4A3 exon 2 junction,
which is the only reported EMC junction using the exon 2 acceptor, and it should be read as that
junction and not as a general statement about the acceptor.

*What the figure does not show.* The frame rule as a rule over all donor and acceptor pairs, the
complete phase-1 donor set, the symmetric prefix sweep and its 0.039 margin, and the TAF15 zero-RG
margin are results of sections 3.2, 3.4 and 3.5 and appear in no panel; none of them may be cited to
this figure. The generator draws NR4A3 RG ticks at residues 371 and 508; an independent reading of
the rendered image reported one of them, and whether the 371 tick is occluded by the adjacent
domain-block edge at 373 or is not resolved at print size was not settled and is not asserted here.

*A provenance limitation of the drawing.* The Panel A box spans are hard-coded literals in the
generator and currently match `rgg_boxes_operational` exactly, which was checked. The generator
stamps a hash of each of its listed source files, so a change to that data field would change the
recorded stamp; what the code does not carry is any binding or asserted equality between that field
and the literals, so a later redraw with the literals unchanged could preserve a semantic mismatch
while still producing a fresh source stamp.

"""
rep("S2c-figure1", "### 3.4 Placement on the retained-RG axis\n\n",
    "### 3.4 Placement on the retained-RG axis\n\n" + FIG)
rep("S2d-fig1ab-xref",
    "Type 2 sits where EWSR1-FLI1 sits, at zero,",
    "Figure 1A shows the retained segments and their RG content, and Figure 1B the axis itself.\nType 2 sits where EWSR1-FLI1 sits, at zero,")

# --- preregistration: separate explanation, registration itself untouched
rep("S2e-prereg-note",
    "\nP5 is the arm capable of falsifying the class argument.",
    """
**The registered text above is reproduced unchanged, including two figures this report corrects.**
P1 to P5 are a preregistration. Their wording, their bases and their falsifiers are reproduced here
exactly as they were registered, and nothing below rewrites them; the corrections and the limitations
are stated separately, as corrections, so that a reader can see both the registered claim and what is
now known about it.

*The margin convention in P3.* P3's registered basis states 14 residues of margin to TAF15's first RG
at residue 175. Two conventions are in use and they differ by one. The census convention, used in
section 3.4, is the RG-free ceiling (174, the largest retained length carrying no RG dipeptide) minus
the retained length (161), which gives 13. The distance from the retained length to the first RG
position (175 minus 161) is 14. Both describe the same junction and the same sequence; section 3.4
states the census convention explicitly and P3 is left as registered.

*Redundancy and equivalence within the registered set.* Two limitations of the set as registered are
identified here and neither is repaired by editing it. P4's falsifier, "the pair showing no kinetic
difference", is the same observation as P2's first falsifier, "type 1 recruiting no earlier than
type 2"; one experiment therefore falsifies two entries, and the set counts fewer independent tests
than its five ids suggest. P1 as registered predicts kinetics *indistinguishable* from a comparator,
which is an equivalence: a null result satisfies it and an underpowered experiment satisfies it too,
so P1 is confirmable but not straightforwardly falsifiable in the direction it is written. Whether
to re-register a narrowed set is a scientific decision about a preregistration and is not taken here.

*Two records, and what each holds.* The machine-readable record
`rgg_dose_calibration_and_predictions.registered_predictions` holds four entries, P1 to P4. This
manuscript carries five hypotheses, P1 to P5, with P5 held separately under
`tcf12_negative_control.registered_prediction`. Both records are preserved as they stand. They are
not the same record, their entries are not word-for-word identical, and neither is edited here to
agree with the other; a reader auditing a prediction should read the entry in the record they cite.

P5 is the arm capable of falsifying the class argument.""")

# --- D5: move the Scope of the claims blockquote into Limitations, wording unchanged
scope = t[t.index("> **Scope of the claims.**"):t.index("\n\n## Abstract")]
t = t.replace(scope + "\n\n", "", 1); edits.append("S2f-scope-removed-from-front")
rep("S2g-scope-into-limitations",
    "\n8. **No laboratory work is proposed by the author.** This programme has no laboratory. The\n   deliverable is the design, the prediction and the criteria.\n",
    "\n8. **No laboratory work is proposed by the author.** This programme has no laboratory. The\n   deliverable is the design, the prediction and the criteria.\n\n"
    + scope.rstrip() + "\n")
rep("S2h-limitation3-widened",
    "3. **Canonical Ensembl transcripts only.** A tumour may use a different transcript or a different\n   breakpoint, in which case the exon-to-residue map changes and so does the protein.",
    "3. **Canonical Ensembl transcripts only, from a single annotation source.** A tumour may use a\n   different transcript or a different breakpoint, in which case the exon-to-residue map changes and\n   so does the protein. The exon numbering, the transcript choices and the coding-exon offsets all\n   rest on one offline input cache and have not been verified against a second, independent\n   annotation source in this work (section 2.6).")

F.write_text(t)
print("STEP2 EDITS:", len(edits))
for e in edits: print("  ", e)
