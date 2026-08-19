---
id: DOC-FUSION-JUNCTION-ASO-SUPPLEMENTARY-INFORMATION
title: "Supplementary Information — Nearly half of junction-spanning gapmer designs against the NR4A3 fusions of extraskeletal myxoid chondrosarcoma pair a wild-type parent gene"
level: L3
kind: manuscript
status: live
canonical_for:
  - the method detail split out of the fusion-junction ASO submission manuscript
purpose: >
  The Supplementary Information for PUB-ASO. It holds the Methods material that a reader does not
  need in order to re-derive a design or re-run a screen: the target-site accessibility rationale,
  the melting-temperature cross-check of the duplex thermodynamics, the provenance of the three
  gap-length figures, the graded re-score's screen-by-screen bookkeeping, the two unfiltered
  control screens, and the coverage ladder's second basis. Each block carries only what the main
  text's Methods does not, and points back at it for the method it elaborates.
scope: >
  Computational design and specificity screening only. No wet-lab experiment was performed, and
  nothing here asserts efficacy, potency, safety, a therapeutic window, delivery to a tumour, or
  clinical readiness for any sequence. Every sequence named is a research reagent for laboratory
  investigation only and must not be administered to any person or animal. ⚠ THIS BLOCK IS REPOSITORY
  FRONT MATTER AND IS STRIPPED FROM THE DEPOSITED PDF, which
  `build_submission_pdf.py` renders beside the manuscript; the operative research-use statement is
  the one in the body below, not this block.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-16
last_verified: 2026-08-16
---

# Supplementary Information — Junction gapmers across the *NR4A3* fusions of extraskeletal myxoid chondrosarcoma

**Running title.** Junction gapmers across NR4A3 fusions — SI

**Author.** Tristan D. McRae

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com

**Research use only, and not for administration to any person or animal.** Every oligonucleotide
sequence named in this Supplementary Information, in the main text and in their tables is a research
reagent intended solely for laboratory investigation. None is a medicine or a candidate drug, none
has been synthesised or tested by anyone, and none may be administered to any human being or animal,
compounded for such use, or supplied to any person for such use. Custom oligonucleotide synthesis is
commercially available, so the restriction is on use rather than on access. The full statement is in
the main text's Declarations.

Section numbers here are prefixed S. Cross-references of the form "§n" point to the main text
(`fusion-junction-aso-research-article.md`); "SI §Sn" points within this document. All numbered
references are those of the main text's reference list, which is generated from the identifiers
carried in the main text; the seven entries this document cites are repeated at its end so that an
SI read on its own resolves them, and the full list is in the main text. This document carries no
figure of its own: Supplementary Figure S1 is printed in the main text beside Figures 1 to 3 and
carries its legend there, and it travels with the archive as well.

## S1 · Target-site accessibility, and its exclusion from every ranking

§6 gives the estimator, the range across the panel and the fact that nothing in the main text is
ranked on it. Here are the three reasons for that omission, in decreasing order of force.

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

The 250 nM strand concentration used in the main text's thermodynamic scoring enters only the
melting temperature, which is the quantity the independent implementation of §6 was compared
against. The strand choice that check does not verify is fixed instead by the documented convention
of the software interface the parameters are read through — Biopython's `R_DNA_NN1` table in
`Bio.SeqUtils.MeltingTemp`, whose calling convention is that the sequence supplied is the RNA one,
which is the sequence the scoring code supplies. The nearest-neighbour parameters themselves are
Sugimoto and colleagues',<sup>52</sup><!--PMID:7545436--> read from that table rather than entered
by hand, and the package version they were read at is recorded beside every released free energy.
The parameter set and the strand convention have different sources and are stated separately here
for that reason.

## S3 · Provenance of the three gap-length figures

§6 states the three figures that place a six-nucleotide gap below the reported optimum, and records
that none of them is a titration in this architecture. Their provenance is as follows.

- **A minimum of five.**<sup>41</sup><!--PMID:39126066--> Given in passing, citing prior work rather
  than measuring it.
- **A minimum of six.**<sup>42</sup><!--PMID:41614678--> A design-protocol statement, likewise given
  in passing and citing prior work.
- **An optimum of seven to ten.**<sup>38</sup><!--PMID:24981949--> Both this and the six-nucleotide
  activity figure beside it are taken from a review that credits them to named earlier primary
  studies rather than measuring them itself.

## S4 · The graded re-score: which screens carry it

The re-score of §6 covers all 38 junction screens, and 39 of the 93 screens released in total. Two
classes of screen are released ungraded. One coverage-only control screen records no gap-mismatch
depth and so cannot be graded at all; the 53 deeper re-screens are released ungraded because the
graded model adds nothing where no hit list is truncated. The re-score counts only sense-strand hits
where it can, meaning where the retained hit list is complete and every hit's strand is therefore
known.

Which of the two bounds applies to a given design follows from its hit list, and each design records
that. Screens produced before the orientation fix carry a strand-blind count for every truncated
design, because the strand of an unretained hit is unrecoverable; screens produced afterwards carry
an already-filtered one.

## S5 · The two unfiltered control screens

The two screens §6 records as unfiltered are modelled control junctions built in amino-acid rather
than transcript coordinates. They carry no junction from the 38-junction panel, and no count
reported anywhere in the main text is taken from them.

## S6 · The coverage ladder's second basis, and four zero-contribution junctions

Table 5 prices every rung on the breakpoint distribution of a single 18-case
series,<sup>22</sup><!--PMID:12378528--> which is the basis 68.4% is computed on. Every figure in
this section is arithmetic over published cohorts rather than a coverage measurement — no patient
was screened with any sequence named here — and §4.1 states in full what that figure is, what it is
not, and the four bounds on it. Two things sit around that ladder: where its arithmetic runs out,
and a second basis that answers a different question and supersedes nothing.

The arithmetic runs out before the target does. A set covering every *EWSR1* and every *TAF15*
breakpoint reaches 94.8% of molecularly confirmed cases and stops, so no panel restricted to those
two partners reaches 95%, and the remaining reachable cases are the two *TCF12* tumours that the
fourth reagent of §4.1 addresses.

Nine junctions now carry a published exon-resolved breakpoint and a screened design, eight of them
through all five screens and the ninth, the *PGR* seam, through three of the five: its pre-mRNA
compartment is unmeasured for the reason main text §2.6 gives, and so is its mature-parent
compartment, because that screen reads the same committed six-gene sequence cache the pre-mRNA
screen reads and that cache carries no *PGR*. One absent donor therefore costs two screens rather
than one. Four of the nine sit outside the 38-junction panel, at the *NR4A3* exon-2 acceptors of §2.6. Four
of the nine move the estimate; one moves only the bound, its arm having no measured
within-partner distribution; and four move it by nothing at all — two because their partner is
absent from this cohort, and two because their partner is present while their exon pair carries no
count in it. That last pair is the easier of the two kinds of zero to miss, and a membership test that
asked only about the partner did miss it. Priced on a pooled breakpoint basis rather than on the
single series the ladder uses, the nine together are 82.9% of molecularly confirmed cases, widening
to 57.5–90.7%. That range is built the way §4.1 builds its own and carries the same caveat: each
breakpoint fraction is taken to its own Wilson bound while the partner shares are held at their
point estimates, so it is a composed-endpoint range carrying no nominal coverage level, and it is
not a confidence interval. The two reagents of §4.1 are 67.1% rather than the ladder's 68.4%. The
denominators are not the ladder's, and neither are the numerators: the *EWSR1* arm is 17 of 20 here
against the ladder's 10 of 15, and two changes make that move rather than one. The denominator widens
by pooling the 18-case series with the five-case whole-transcriptome
cohort,<sup>25</sup><!--PMID:29937513--> and the numerator rises because this panel carries four
*EWSR1* junctions where the ladder carries one, reaching 12 of the same 15 tumours before any
pooling. The *TAF15* arm stays at 3 of 3. Three things follow. Fifteen of those 20 tumours come from one
series, so the pool stays close to it; the two series agree at *EWSR1* exons 12 and 13 and disagree
completely at exon 7 to *NR4A3* exon 2, 0 of 15 against 1 of 5; and a third series was refused
because every case in its *EWSR1* arm carries a covered junction by construction, 12 of 12, since a
case with any other junction could not have entered that arm at all; the series that is pooled is 12
of 15 on the same test and so is not fixed by its own assay. That third series is Okamoto and
colleagues' 18 cases, PMID 11679947, cited only here and so taking no number in the main text's
list. Pooling it would give 87.4% rather than 82.9%, which is to say the rule costs coverage rather
than buying it, and it is applied for that reason and not for the figure. Two of seven retrieved series resolve
every case to an exon pair, so this is a pooled record and not the whole one; the seven are the
papers that report an exon-resolved junction at all in the breakpoint census behind this section,
which read 295 papers and is the one home for both counts. The figure supersedes
nothing: it answers a different question from the ladder, whose rungs are incremental and priced on
the single series 68.4% is computed on, and 68.4% remains the coverage of the two reagents named in
§4.1. Its own membership rule is an evidence test rather than a list — a junction qualifies where a
published report places a patient's breakpoint at it and a reagent has been through all five screens,
three of the five for the *PGR* seam, whose pre-mRNA and mature-parent compartments are both
unmeasured rather than clean, on the one shared cache main text §2.6 describes — and one qualifying junction, *PGR* exon 2 to *NR4A3* exon 2, reported in a single
patient,<sup>28</sup><!--PMID:36103645--> moves the figure by exactly zero, because the 58-case
cohort behind the denominator contains no *PGR* case for such a reagent to engage. The further
caveat on that reagent — a sixth partner, outside the five the panel models, whose seam is screened
against the non-canonical-acceptor table rather than through the panel's transcript models — is in
§2.6, which also points at the accession §6 lists for it.
*TFG* exon 7 to *NR4A3* exon 3 is the second of that pair, on the same ground and from a deposited
cDNA rather than a report. Those two are the partner-absent half of the four that add nothing; the
other two have their partner present in the cohort and their exon pair carrying no count in it.
What such a reagent changes is which patients are reachable at all, which is a
different statement and is not added to a coverage percentage.

## References cited in this Supplement

These are the seven entries of the main text's reference list that this document cites, repeated here
verbatim from it so that a reader holding only the Supplementary Information can resolve them. The
numbers are the main text's and are assigned there; each entry carries its PubMed identifier in the
same non-rendering comment the superscripts use, so the renumbering that keeps a superscript and its
reference together reaches this block too. This is a copy, not a second list: the reference list of
record is the main text's, generated from the identifiers carried in it.

<sup>22</sup><!--PMID:12378528--> Panagopoulos I, Mertens F, Isaksson M, Domanski HA, Brosjö O, Heim S, Bjerkehagen B, Sciot R, Dal Cin P, Fletcher JA, Fletcher CD, Mandahl N. Molecular genetic characterization of the EWS/CHN and RBP56/CHN fusion genes in extraskeletal myxoid chondrosarcoma. Genes, chromosomes & cancer. 2002;35(4):340-352. PMID: 12378528. doi:10.1002/gcc.10127

<sup>25</sup><!--PMID:29937513--> Urbini M, Indio V, Astolfi A, Tarantino G, Renne SL, Pilotti S, Dei Tos AP, Maestro R, Collini P, Nannini M, Saponara M, Murrone L, Dagrada GP, Colombo C, Gronchi A, Pession A, Casali PG, Stacchiotti S, Pantaleo MA. Identification of an Actionable Mutation of KIT in a Case of Extraskeletal Myxoid Chondrosarcoma. International journal of molecular sciences. 2018;19(7):E1855. PMID: 29937513. doi:10.3390/ijms19071855

<sup>28</sup><!--PMID:36103645--> Wilbur HC, Robinson DR, Wu YM, Kumar-Sinha C, Chinnaiyan AM, Chugh R. Identification of Novel PGR-NR4A3 Fusion in Extraskeletal Myxoid Chondrosarcoma and Resultant Patient Benefit From Tamoxifen Therapy. JCO precision oncology. 2022;6:e2200039. PMID: 36103645. doi:10.1200/po.22.00039

<sup>38</sup><!--PMID:24981949--> Kauppinen S, Vester B, Wengel J. Locked nucleic acid (LNA): High affinity targeting of RNA for diagnostics and therapeutics. Drug discovery today. Technologies. 2005;2(3):287-290. PMID: 24981949. doi:10.1016/j.ddtec.2005.08.012

<sup>41</sup><!--PMID:39126066--> Mejzini R, Caruthers MH, Schafer B, Kostov O, Sudheendran K, Ciba M, Danielsen M, Wilton S, Akkari PA, Flynn LL. Allele-Selective Thiomorpholino Antisense Oligonucleotides as a Therapeutic Approach for Fused-in-Sarcoma Amyotrophic Lateral Sclerosis. International journal of molecular sciences. 2024;25(15):8495. PMID: 39126066. doi:10.3390/ijms25158495

<sup>42</sup><!--PMID:41614678--> Agrawal S. Transient Cyclic Structured Oligonucleotide Designs for Therapeutic Applications. Current protocols. 2026;6(2):e70319. PMID: 41614678. doi:10.1002/cpz1.70319

<sup>52</sup><!--PMID:7545436--> Sugimoto N, Nakano S, Katoh M, Matsumura A, Nakamuta H, Ohmichi T, Yoneyama M, Sasaki M. Thermodynamic parameters to predict stability of RNA/DNA hybrid duplexes. Biochemistry. 1995;34(35):11211-11216. PMID: 7545436. doi:10.1021/bi00035a029

One further source is cited only here and therefore takes no number in that list, exactly as the
external data records do: Okamoto S, Hisaoka M, Ishida T, Imamura T, Kanda H, Shimajiri S, Hashimoto
H. Extraskeletal myxoid chondrosarcoma: a clinicopathologic, immunohistochemical, and molecular
analysis of 18 cases. Human pathology. 2001;32(10):1116-1124. PMID: 11679947.
doi:10.1053/hupa.2001.28226 — the third breakpoint series SI §S6 records as refused.