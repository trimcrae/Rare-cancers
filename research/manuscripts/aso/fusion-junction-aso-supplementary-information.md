---
id: DOC-FUSION-JUNCTION-ASO-SUPPLEMENTARY-INFORMATION
title: "Supplementary Information — Nearly half of junction-spanning gapmer designs against the NR4A3 fusions of extraskeletal myxoid chondrosarcoma pair a wild-type parent gene"
level: L3
kind: manuscript
status: live
canonical_for:
  - the method detail split out of the fusion-junction ASO submission manuscript
purpose: >
  The Supporting Information for PUB-ASO. It holds the Methods material that a reader does not
  need in order to re-derive a design or re-run a screen: the target-site accessibility rationale,
  the melting-temperature cross-check of the duplex thermodynamics, the provenance of the three
  gap-length figures, the graded re-score's screen-by-screen bookkeeping, and the two unfiltered
  control screens. No claim, number or caveat was altered in the move; each block is the main
  text's own wording, and the main text keeps a pointer where the block used to sit.
scope: >
  Computational design and specificity screening only. No wet-lab experiment was performed, and
  nothing here asserts efficacy, potency, safety, a therapeutic window, delivery to a tumour, or
  clinical readiness for any sequence.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-16
last_verified: 2026-08-16
---

# Supplementary Information — Junction gapmers across the *NR4A3* fusions of extraskeletal myxoid chondrosarcoma

**Author.** Tristan D. McRae

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com

<!-- EDITORIAL, NOT FOR SUBMISSION: this Supporting Information was split out of
fusion-junction-aso-research-article.md in the 2026-08-16 editorial restructure. It holds the Methods
material demoted from the main-text spine: the target-site accessibility rationale, the melting-
temperature cross-check, the gap-length citation provenance, the graded re-score's screen bookkeeping,
and the two unfiltered control screens. No scientific claim, number or caveat was altered in the move.
Section numbers here are prefixed "S". -->

Section numbers here are prefixed **S**. Cross-references of the form "§n" point to the **main text**
(`fusion-junction-aso-research-article.md`); "SI §Sn" points within this document. All numbered
references are those of the main text's reference list, which is generated from the identifiers
carried in the main text.

## S1 · Target-site accessibility, and why nothing is ranked on it

Accessibility was estimated as mean unpaired probability over a local fold of up to 180 nucleotides,
computed with the ViennaRNA partition function.<sup>29</sup><!--PMID:22115189--> It spans 0.160 to
0.707 across all 190 designs at real exon junctions, with a median of 0.477. It is released with the
artefacts and is not used to rank anything in the main text, and the omission is deliberate rather
than an oversight. Three reasons, in decreasing order of force.

First, the quantity is not the one the paper is about: accessibility predicts whether an
oligonucleotide can reach its site on the fusion, and every question asked in the main text is
whether it can be told apart from a parent once it does. An inaccessible site is a potency problem,
and potency is not claimed for any sequence.

Second, the estimate is a fold of a naked transcript, whereas the compartment that matters is a
nascent, protein-coated pre-mRNA; measured antisense activity correlates with such predictions weakly
and inconsistently, which is why the field selects by screening rather than by folding.

Third, it would have no purchase on the result even if it were reliable: the surviving candidates are
separated by orders of magnitude of predicted off-target load, and reordering them on a quantity that
spans 0.160 to 0.707 across the panel would substitute a weak predictor for a strong one. The values
are released so that a laboratory ordering several oligonucleotides at one junction can break a tie
on them, which is the use they support.

## S2 · The melting-temperature cross-check on the duplex thermodynamics

The 250 nM strand concentration used in the main text's thermodynamic scoring enters only the melting
temperature, which was used to check the arithmetic against an independent implementation. The two
agreed exactly. That check verifies the summation, not the choice of strand, which is fixed by the
documented convention of the nearest-neighbour table<sup>36</sup><!--PMID:7545436--> that the
sequence supplied is the RNA one. No free energy reported in the main text depends on the strand
concentration.

## S3 · Provenance of the three gap-length figures

The main text records that a six-nucleotide gap sits at the short end of the usable range and below
the reported optimum, and cites three figures for that. None of the three is a titration in this
architecture, and the provenance of each is as follows.

- **A minimum of five.** One source states that RNase-H1 requires a gap of at least five for cleavage
  to occur.<sup>23</sup><!--PMID:39126066--> The figure is given in passing, citing prior work rather
  than measuring it.
- **A minimum of six.** The other is a design-protocol statement that the DNA segment must be "six or
  more bases" to activate the enzyme.<sup>24</sup><!--PMID:41614678--> It is likewise given in
  passing and cites prior work.
- **An optimum of seven to ten.** For LNA/DNA/LNA gapmers specifically, a six-nucleotide gap is
  reported to give noteworthy but incomplete activity, with seven to ten reported as optimal. Both
  figures are taken from a review that credits them to named earlier primary studies rather than
  measuring them itself.<sup>25</sup><!--PMID:24981949-->

## S4 · The graded re-score: which screens carry it

Every screen that resolves the catalytic gap was re-scored under both of the main text's
discrimination bounds as a graded residual cleavage load, holding the hit set fixed so that only the
scoring changed. That covers all 38 junction screens, and 39 of the 93 screens released in total.

Two classes of screen are released ungraded. One coverage-only control screen records no
gap-mismatch depth and so cannot be graded at all; the 53 deeper re-screens are released ungraded
because the graded model adds nothing where no hit list is truncated. The re-score counts only
sense-strand hits where it can, meaning where the retained hit list is complete and every hit's
strand is therefore known.

Which of the two bounds applies to a given design follows from its hit list, and each design records
that. Screens produced before the orientation fix carry a strand-blind count for every truncated
design, because the strand of an unretained hit is unrecoverable; screens produced afterwards carry
an already-filtered one.

## S5 · The two unfiltered control screens

Orientation is parsed and filtered in all 38 junction screens and the 183 designs they hold, and
therefore in every cleanliness statement the main text makes. The only two screens in the released
set that are not filtered are modelled control junctions built in amino-acid rather than transcript
coordinates. They carry no junction and support no claim in the main text, and no count reported
anywhere in it is taken from them.
