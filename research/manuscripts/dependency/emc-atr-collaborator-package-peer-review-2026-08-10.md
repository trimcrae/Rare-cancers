---
id: DOC-EMC-ATR-COLLABORATOR-PACKAGE-PEER-REVIEW
title: "Simulated peer review — emc-atr-collaborator-package.md (Genes, Chromosomes and Cancer)"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: A simulated journal peer review of the ATR collaborator package, and the revision list it generates.
scope: Review of one manuscript. Reports no new result and asserts nothing about any disease or agent.
audience: [maintainers, external reviewers]
date: 2026-08-10
last_verified: 2026-08-10
---

> **THIS IS A SIMULATED INTERNAL REVIEW, WRITTEN BY AN AI REVIEWER AT THE AUTHOR'S REQUEST. IT IS NOT
> A REAL JOURNAL REVIEW.** No editor, no journal and no external reviewer has seen this manuscript.
> Nothing in this file is correspondence from *Genes, Chromosomes and Cancer*, from Wiley, or from any
> person other than the author's own tooling. It is a rehearsal, produced to find the objections a real
> reviewer would raise before a real reviewer raises them. Do not quote it as an external assessment,
> do not attach it to a submission, and do not describe the manuscript anywhere as "reviewed" on the
> strength of it.

# Simulated peer review

**Manuscript:** "Transcript-level models of the NR4A3 fusions of extraskeletal myxoid chondrosarcoma,
and five pre-specified predictions for a DNA double-strand break recruitment assay"
(`research/manuscripts/emc-atr-collaborator-package.md`)

**Submitted as:** Research Article, *Genes, Chromosomes and Cancer*

**Also read:** `research/manuscripts/emc-atr-collaborator-package-cover-letter.md`;
`research/manuscripts/emc-atr-vulnerability-assessment.md` (companion, not under review)

**Reviewer's declared expertise:** fusion-gene analysis in sarcoma; FET-family fusion architecture;
breakpoint reporting conventions; transcript versus coding-sequence models; RGG and RG-repeat biology;
DNA damage recruitment imaging.

**Review method.** Unusually for a review, I had the underlying code and artifacts. I did not take the
manuscript's numbers on trust. I recomputed the RG dipeptide counts, the [S,Y,G,Q] fractions, the
alignment identities, every open reading frame length, every exon-boundary offset and the 59-residue
translation directly from the committed input cache, and I ran the reproduction command in section 2.5.
What verified and what did not is stated below in both directions.

---

## Recommendation

**MAJOR REVISION.**

The sequence work is sound, and I want to say that first and plainly, because most of what follows is
critical. I recomputed essentially every number in the Results from the committed input cache and they
matched: the retained RG counts (0, 7, 8, 8, 11 of 30 for EWSR1 cut at 264, 324, 348, 431 and 472; 0 of
31 for TAF15 cut at 161), the [S,Y,G,Q] fractions (0.540, 0.620, 0.804 for the FET proteins against
0.368 for TCF12), the six Needleman-Wunsch identities, all four open reading frame lengths (1058, 949,
1099, 788), and the 59-residue translation, which contains no stop codon and yields a 949-residue
protein identical to the committed artifact. The reproduction command runs offline in seconds and prints
`REPRODUCES`. Every reference identifier traces to a committed retrieval record. This is a more
auditable manuscript than most I am asked to review.

That is why the recommendation is revision rather than rejection. But the paper has one factual error in
its Abstract that its own held sources contradict, a status column in its central table that labels
comparators "measured" when they were not, and a headline arithmetic statement that is one nucleotide
short. It is also, as framed, a paper whose title announces a set of predictions for an experiment the
authors state they cannot perform, and I do not believe a *Genes, Chromosomes and Cancer* editor would
send that out. My honest position is that the content is real and the framing is wrong: the one genuinely
novel result here is the 59-residue N-terminal extension in the type-2 fusion, it is currently buried in
section 3.3 with no display item, and a paper built around it would be a straightforward accept-with-
revisions at this journal. I have set out that reframing in Major Point 1 and specified it concretely in
the Revision list.

---

## The editorial question, answered plainly

I was asked whether there is enough here for a Research Article or whether this is a resource plus a
wish-list. My answer: **as submitted, it is closer to a resource plus a wish-list, and I expect it to be
desk-rejected. Reframed around the sequence finding, it is a real Research Article, and a good fit for
this journal.**

Taking the content apart honestly:

| element | what it is | is it a Research Article result? |
|---|---|---|
| Table 1, the four sourced junctions | compilation from four prior reports, with verbatim quotations | No. This is careful curation. A review already contains it. It is valuable as Methods, not as Results. |
| Table 3, the four open reading frames | transcript-level translation with self-checks | Partly. That EMC fusions are in-frame chimeric transcription factors is established. The exact products, computed and checked, are a modest but real contribution. |
| Section 3.3, the 59-residue extension | a specific, checkable, consequential sequence result | **Yes.** This is the paper. |
| Table 4, the retained-RG placement | another group's axis with EMC points added by inference | No. This is an inference from someone else's calibration, and Major Point 3 shows the calibration is weaker than the table implies. It belongs in a Discussion. |
| Table 5, TCF12 as non-FET | a well-executed computation of something nobody disputes | No. TCF12 is a class I bHLH factor; that it is not a FET protein will surprise no reader. Its value is as a designed control, and it should be presented as one. |
| Tables 6 and 7, predictions and controls | a proposal | No. |

So the novel content is section 3.3, supported by section 3.2. That is thin for a Research Article as a
list, but it is not thin as a paper, because section 3.3 has a consequence: anyone who builds an
EWSR1 exon 7 to NR4A3 exon 2 construct from the protein-level model builds a protein 59 residues shorter
than the reported junction predicts. Groups do build EMC fusion constructs. A short, rigorous paper that
says "here is the reading frame of every reported EMC junction, here is the general rule that governs
them, and here is the one junction whose product is not what the field's protein model says" is exactly
the kind of paper this journal exists to publish.

What kills it in its present form is the title and the shape. The title's second clause is "five
pre-specified predictions for a DNA double-strand break recruitment assay". An editor reads the title and
the abstract. This title announces a proposal. The Discussion is then replaced by a prediction table, and
section 6 item 8 states that the author has no laboratory. The editorial block in the file records that
Registered Report, Study Protocol, Perspective and Resource were all considered and rejected; I agree
with each of those rejections, but the conclusion drawn from them was that a Research Article should
carry the prediction set, and the right conclusion was that the prediction set should be demoted to a
short application subsection of a Research Article about sequence.

**The reframing I would accept.** Retitle around the finding, for example: *"The reported EWSR1 exon 7 to
NR4A3 exon 2 fusion of extraskeletal myxoid chondrosarcoma encodes a 59-residue N-terminal extension
absent from the protein model in general use"*, with a subtitle or second clause covering the systematic
frame analysis. Then:

- **Results 1:** the frame rule across all EWSR1 donor exons and both NR4A3 acceptor exons (Major Point 6).
- **Results 2:** the 59-residue extension, at nucleotide resolution, with the independent RefSeq
  cross-check and the precedent in reference 3 (Major Points 4 and 5).
- **Results 3:** the four reported junctions as instances of the rule, with their products.
- **Results 4:** TCF12 as a computed control, presented as a control.
- **Discussion:** consequences for construct design, then a compressed subsection placing EMC on the
  published retained-RG axis and listing the predictions, reduced from five to the three that are
  independent.

That paper leads with a measurement-shaped statement about sequence, keeps every result currently in the
manuscript, loses nothing, and does not ask an editor to accept a proposal as a Research Article.

---

## MAJOR POINTS

### Major Point 1. Article type and framing

**Applies to:** title; Abstract; section 4; section 5; the editorial comment block.

Set out above. The specific resolution: retitle to lead with the 59-residue extension; move sections 4
and 5 into a Discussion subsection; reduce the five predictions to the three independent ones (see Major
Point 8); and remove from the running text every construction that presents the paper as an offer to a
laboratory rather than as a report. Section 1's closing sentence ("This report supplies those three
things") and section 5's "Adding EMC to that panel requires plasmids and nothing else" both read as a
pitch. The Results should not be introduced as a service to a reader who might run an experiment.

### Major Point 2. "The two commonest EMC fusions" is unsupported, and the authors hold sources that contradict it

**Applies to:** Abstract, sentence 6; Table 1, "reported rank" column; section 3.4, paragraph 2; P4.

This is the most serious factual problem in the manuscript, and it is in the Abstract.

The Abstract states: "Retained EWSR1 RG dipeptide counts place the two commonest EMC fusions at 0 of 30
and 8 of 30". The two fusions meant are type 2 (EWSR1 exon 7 to NR4A3 exon 2) and type 1 (EWSR1 exon 12 to
NR4A3 exon 3). Table 1 assigns type 2 a reported rank of "second", citing references 4 and 6.

Neither cited source makes a frequency claim about type 2. I checked the quotations the producing artifact
actually holds. Reference 4's quotation is a definition: "The most common fusion transcript contains exon
12 of EWSR1 fused to exon 3 of NR4A3 (type 1), whereas exon 7 of EWSR1 is fused to exon 2 of NR4A3 in the
type 2 fusion transcript." That sentence names type 2; it does not rank it. Reference 6's quotation in the
artifact is an RT-PCR primer design, which establishes that the junction is assayed, not how often it is
found. The rank "second" appears to have been inferred from the type *number*.

The counted evidence points the other way, and both series are already in this repository:

- Reference 7's own series, quoted in section 3.1 and in the manuscript's reference annotation: 15
  EWS/NR4A3 cases, of which type 1 in 10 and type 5 in 2. Type 2 is not among the counted types at all.
  The same abstract, committed in `research/manuscripts/lit-targets-aso-verify.json`, adds the genomic
  mapping: of 14 cases mapped, 12 broke in NR4A3 intron 2 and only 2 in intron 1, and in EWSR1 the breaks
  fell in intron 7 (one), intron 12 (eight) and intron 13 (one). A single EWSR1 intron 7 break in 14
  mapped cases.
- Okamoto et al. 2001, whose abstract is committed verbatim in the same file and is quoted in two other
  manuscripts in this repository: of 18 cases, 15 fusion-positive, "EWS-CHN type 1 in 11 cases, EWS-CHN
  type 2 in 1, and TAF2N-CHN in 3."

On both series type 2 is a rare variant, and on Okamoto's series TAF15::NR4A3 is three times more common
than type 2. So the sentence "the two commonest EMC fusions" is wrong, and the more interesting true
statement is being missed: **the zero-RG end of the axis in EMC is occupied principally by
TAF15::NR4A3, not by EWSR1::NR4A3 type 2.** That makes P3, not P1, the clinically dominant zero-RG arm,
which is a better paper.

**Resolution.** Delete "the two commonest" from the Abstract. Replace Table 1's "reported rank" column
with counted frequencies and their sources, one row per series, and mark type 2 as a minority variant.
Rewrite section 3.4 paragraph 2 so the "bracket" claim does not rest on type 2 being common. Adjust P4,
which currently leans on the type-1 and type-2 pair being "two naturally occurring points"; they are, but
one of them is rare and the sentence should say so. Add one sentence noting that TAF15::NR4A3 is the more
frequent zero-RG EMC fusion. All of this is re-analysis of sources already held; none of it requires new
data.

### Major Point 3. Table 4 marks comparators "measured" that were not measured, and omits two rows the artifact contains

**Applies to:** Table 4, "status" column; section 3.4, paragraphs 2 and 3; P2.

Table 4 assigns the status "measured" to three rows: EWSR1-FLI1, EWSR1::ATF1 exon 8 ("measured,
phenotype present") and EWSR1::ATF1 exon 10 ("measured"). Reference 1 built one EWSR1-ATF1 construct.
At most one of those two ATF1 rows can describe it.

The repository's own census module states the position explicitly, in a field a reader can check:
the control rule is written as "any type", not "all types", *"because a fusion's breakpoint varies
between patients and this repo has no exon audit fixing which type the source's constructs used"*. So the
manuscript's Table 4 asserts as measured precisely what the underlying artifact declines to assert.

Two rows the artifact contains are absent from Table 4, and both absences flatter the argument:

1. **EWSR1::ATF1 at EWSR1 exon 7**, retaining 0 of 30 RG, fraction 0.000, carried in the artifact under
   the same "the mechanism was MEASURED on this fusion" label as the two rows that were included. With
   it, the ATF1 comparator is not a point at 0.233 but a **range from 0.000 to 0.267 depending on which
   breakpoint the measured construct used**. The "bracketing" framing does not survive that, and P2's
   stated basis, "8 of 30 against 7 of 30", becomes a comparison against an assumed breakpoint.
2. **EWSR1-RGG(1)-FLI1**, the middle point of reference 1's own three-point dose series, whose retained
   RG count is recorded in the artifact as null. It is unplaceable on this paper's axis because the paper
   does not know which RGG domain was reintroduced. Its omission is what allows section 3.4 to say
   "Neither EMC type extrapolates beyond the published series; both interpolate between points already
   measured". With the middle anchor missing, the only firm measured points are 0.000 and 1.000, and
   "interpolate between points already measured" is true only in the trivial sense that everything
   between zero and one does.

I should note that restoring row 1 is not purely damaging to the paper: an ATF1 construct at 0 of 30 in a
disease where the phenotype was observed is a second measured point at zero, which strengthens P1. The
argument is better for being complete.

**Resolution.** Split the status column into two: "measured in reference 1" (EWSR1-FLI1, the RGG add-back
series, native EWSR1) and "a reported breakpoint of a disease in which the mechanism was measured"
(the ATF1 rows). Restore both omitted rows, with the RGG(1) row carrying an explicit "not placeable, RGG
domain identity not specified in the source". Add one sentence to section 3.4 stating that the EWSR1
breakpoint of reference 1's EWSR1-ATF1 construct is not specified in the source as retrieved, so the ATF1
comparator spans 0.000 to 0.267. Replace "bracketing" and "interpolate between points already measured"
with language the restored table supports. Restate P2's basis accordingly, or make P2 conditional on the
ATF1 breakpoint.

### Major Point 4. The headline arithmetic is one nucleotide short, and the finding it describes is buried

**Applies to:** Abstract, sentence 5; section 3.3, sentences 1 and 2; Table 3, "extra residues" column;
Appendix A row 2; the cover letter, paragraph 3.

The claim, in four places, is that the type-2 junction "carries 176 nucleotides of NR4A3 5' untranslated
sequence in the EWSR1 reading frame, encoding 59 residues". 176 is not a multiple of three. 176 nucleotides
read in frame are 58 codons and two spare bases.

The computation is right; the sentence describing it is not. I reproduced it from the input cache. EWSR1
coding sequence through exon 7 is 793 nucleotides, which is 264 complete codons plus one base. That single
donated base, plus the first two bases of NR4A3's retained non-coding sequence, forms the hybrid codon
encoding lysine at position 265. Only then do 58 complete codons follow. So **59 residues require 177
nucleotides: one from EWSR1 and 176 from NR4A3.**

A second, smaller imprecision sits in the same sentence. Section 3.3 says "The named 3' exon of the
type-2 junction, NR4A3 exon 2, is entirely non-coding, so the fusion mRNA carries 176 nucleotides of NR4A3
5' untranslated sequence". The 176 is not all exon 2: it is 174 nucleotides of exon 2 plus the 2
nucleotides of 5' untranslated sequence that exon 3 carries ahead of the initiator codon. That second
component matters more than it looks, because it is the same 2 nucleotides that make the other three
constructs in-frame (Major Point 6).

I confirmed the substance: the 59-residue segment translates as
`KPTAEEGSPASPGPEPGPLAVPGSTAGASPRRTSAPPTLSASAGETPSPTIQRARYPPD`, contains no stop codon, and the resulting
949-residue open reading frame matches the committed artifact exactly. The finding is real. Only the
sentence is wrong.

**On burial.** This is the one result in the manuscript that a specialist reader will not already know. It
occupies six sentences of section 3.3, one cell of Table 3, one clause of the Abstract, and no display item
at all. The title does not mention it. Meanwhile the TCF12 classification, which nobody will dispute, gets
a full table and a full Results subsection. The proportions are inverted. See Major Point 10 for the figure
this result needs, and Major Point 1 for the retitle.

**Resolution.** Restate the arithmetic precisely in all four locations: the split codon at the seam plus
176 nucleotides of NR4A3 5' untranslated sequence (174 from exon 2, 2 from exon 3) are read in the EWSR1
frame as 59 residues with no intervening stop. Note that the first of the 59 is a hybrid codon and the
remaining 58 are encoded entirely by NR4A3 sequence in a frame NR4A3 itself does not use. Add the
translated sequence to the manuscript, not only to the artifact.

### Major Point 5. The exon-numbering correspondence is the paper's largest unstated risk, and the evidence closing it is already in the paper's own sources

**Applies to:** section 2.1; section 3.1; section 6, limitation 3.

Everything in this manuscript depends on one unstated assumption: that "NR4A3 exon 2" and "NR4A3 exon 3"
as used in the EMC breakpoint literature are the same exons as transcript exon ranks 2 and 3 of
ENST00000395097. If they are not, the 176-nucleotide segment, the 59 residues, the in-frame verdicts and
every construct in Table 3 are wrong together.

This is not a theoretical worry. Limitation 2 discloses that this programme has already been bitten by an
exon-indexing error of exactly this family, in which a coding-exon offset table indexed with transcript
exon numbers deleted NR4A3's AF-1 domain and the first zinc finger from seven junctions. The manuscript
fixed the coding-versus-transcript axis and did not address the literature-versus-Ensembl axis, which is
the one that remains open. Limitation 3 mentions only that "a tumour may use a different transcript", which
is a different risk.

The evidence that closes it is already in hand, in three independent forms, at no cost:

1. **Reference 7's genomic mapping.** Its abstract, committed in `lit-targets-aso-verify.json`, reports
   that in NR4A3 "12 breakpoints were found in intron 2 and only two in intron 1". A genomic break in
   intron 2 produces a transcript joining to exon 3; a break in intron 1 produces one joining to exon 2.
   That fixes the field's numbering onto the same exons the manuscript uses, from the primary breakpoint
   paper, and it simultaneously supplies the frequency data Major Point 2 asks for.
2. **Reference 3's cryptic exon.** The quotation the manuscript already uses in section 3.1, that a rarer
   TAF15::NR4A3 isoform splices into a cryptic exon in NR4A3 intron 2 "thus encoding 25 additional amino
   acids prior to the NR4A3 ATG", places intron 2 immediately upstream of the initiator codon in the
   field's numbering. It also, incidentally, means the field has already described an N-terminal extension
   arising by exactly the mechanism section 3.3 reports, which bears on how the novelty is worded (see
   below).
3. **An independent transcript model already in the repository.** `junction-aso-designs-e7n3.json`, built
   from the RefSeq mRNAs rather than from Ensembl, independently reports
   `nr4a3_acceptor_exon_5utr_nt_retained: 2` for NR4A3 exon 3 and the identical seam context. Two
   independent annotation sources agreeing on the 2-nucleotide figure is a real cross-check and the
   manuscript does not mention it.

**A related point on how the novelty is worded.** Section 3.3 says the 59 residues are absent from "the
protein-level model in general use". No source is cited for what the field's model is; the only model the
manuscript can actually document is this programme's own, recorded in Appendix A. And reference 3 already
describes a 25-residue N-terminal extension in a TAF15::NR4A3 variant by the same mechanism, so the
*concept* is in the literature even though its application to the type-2 junction is not. Both facts should
be stated. They make the claim more defensible, not less: the precedent shows the mechanism is real in this
gene, and the honest scope of the novelty is the specific junction.

**Resolution.** Add a short paragraph to section 2.1 or 3.2 establishing the numbering correspondence from
sources 1 and 2, cite the RefSeq cross-check in section 2.1 and section 7, replace "the protein-level model
in general use" with a statement of what is actually documented, and cite reference 3's cryptic-exon
extension as precedent in section 3.3.

### Major Point 6. Section 3.2 reports four instances where a single rule applies, and the rule is already computed

**Applies to:** section 3.2, closing paragraph; Table 3.

Section 3.2 says only: "All four are in frame. Each splits a codon across the junction, which is why the
frame was computed at the nucleotide level rather than inferred from residue arithmetic." That is four
anecdotes where there is one law, and the law is more interesting than any of the four.

From the committed exon models: EWSR1 exons 7, 12 and 13 and TAF15 exon 6 all end at coding phase 1, that
is with one base of a codon unused (793, 1294, 1417 and 484 nucleotides of coding sequence respectively,
each congruent to 1 modulo 3). NR4A3 exon 3 contributes exactly 2 nucleotides of 5' untranslated sequence.
One plus two is three. That single fact makes all four reported junctions in frame, for the same reason.

Better still, NR4A3 exon 2 is 174 nucleotides, a multiple of three, so **joining at exon 2 and joining at
exon 3 give the same frame register**. The rule reduces to: an EWSR1::NR4A3 fusion is in frame if and only
if the EWSR1 donor exon ends at coding phase 1, irrespective of which of the two acceptors is used.

The repository has already computed this across all pairs. `junction-mrna-frame-audit.json` carries 27
rows with a `frame_sum_mod3` field and an `ewsr1_coding_phase` field; over the nine EWSR1 donor exons and
the two NR4A3 acceptors it grades ten junctions in frame, and the in-frame set is exactly the phase-1
donors (exons 7, 9, 10, 12, 13). The manuscript does not cite this artifact anywhere.

This is the single largest free upgrade available to the Results. It converts a list of four checked
examples into a general statement with a small table, it predicts which unreported junctions would be in
frame if found, and it explains the 59-residue extension as a property of the *acceptor* rather than of
type 2 specifically, since any fusion using NR4A3 exon 2 carries it.

**Resolution.** Add the frame rule to section 3.2 as a stated result. Add a compact table of EWSR1 donor
exon, coding phase, and in-frame status against both NR4A3 acceptors. Cite `junction-mrna-frame-audit.json`
in section 7. State that the 59-residue extension attaches to the exon 2 acceptor, so any fusion using it
carries the extension.

### Major Point 7. Reference transcript provenance is incomplete for a paper made entirely of exon coordinates

**Applies to:** Table 2; section 2.1; section 7.

Table 2 gives an accession for EWSR1 and NR4A3 and the word "canonical" for TAF15, FUS and TCF12. This is
not adequate for a manuscript whose entire content is exon arithmetic on specific transcripts.
"Canonical" is a moving designation that changes between Ensembl releases, and TAF15 in particular is
load-bearing: P3's whole argument is that TAF15 exon 6 retains 161 residues and TAF15's first RG dipeptide
sits at 175, and a different canonical assignment moves both numbers.

Nothing in the manuscript states the Ensembl release, the genome assembly, or the retrieval date. I
checked the input cache: it records the fetch timestamp and the REST endpoint, and no release number or
assembly. The transcript identifiers carry no version suffix. A reader in two years cannot reproduce this
table, and the "re-derives every figure offline" guarantee in section 2.5 covers reproduction from the
cache, not reproduction of the cache.

**Resolution.** Give the full versioned accession for every transcript and translation in Table 2, state
the Ensembl release and genome assembly, and report the retrieval date in section 2.1 or 2.5. If the
release cannot be recovered for the existing cache, say so and give the fetch date, which is recorded.

### Major Point 8. The prediction set is less than five predictions, two falsifiers are incomplete, and there is no analysis plan

**Applies to:** section 4; Table 6; section 5, closing paragraph.

A pre-specified prediction set is only worth the discipline it imposes, so it has to survive being read
adversarially. This one does not, in five specific ways.

1. **P4 is not independent of P2.** P4 predicts that "the type-1 and type-2 pair reproduces the RGG
   dose-dependence"; its falsifier is "the pair showing no kinetic difference". P2 predicts that type 1 is
   "recruited earlier than type 2"; half its falsifier is "type 1 recruiting no earlier than type 2".
   These are the same experiment and the same falsifier. Counting them as two predictions inflates the set.
2. **P1 is an equivalence claim with no margin.** "Kinetics indistinguishable from EWSR1-FLI1" cannot be
   falsified by a null result, and an underpowered experiment satisfies it automatically. The manuscript
   says elsewhere that the axis is ordinal with no slope available, so no equivalence margin can be quoted;
   the honest fix is to restate P1 as a rank prediction (type 2 sits with EWSR1-FLI1 and both are later
   than native EWSR1) rather than as an equivalence.
3. **P3's falsifier omits its most likely failure.** P3 predicts TAF15::NR4A3 "is recruited, at the zero end
   of the axis", falsified by "kinetics indistinguishable from native TAF15". No accumulation at all would
   not falsify P3 as written, yet that is exactly the outcome P1's falsifier explicitly includes and exactly
   the outcome section 4 treats as informative for P5. Add it.
4. **P2 bundles a falsifiable claim with an unfalsifiable one.** "Recruited earlier than type 2" is
   testable. "Closest to the commonest clear-cell EWSR1::ATF1 type" has no falsifier in the table, and its
   basis, "8 of 30 against 7 of 30", is a difference of one RG dipeptide on an axis the manuscript itself
   describes as ordinal with no slope. I would add that the two retained segments are not merely close: at a
   cut of 348 residues and a cut of 431 residues the retained set of RG dipeptides is the *same eight*
   (positions 300 to 330), differing only by 83 residues of RG-free sequence. The axis cannot distinguish
   them even in principle. Either drop the proximity clause or restate it as an explicit non-prediction.
5. **P5 has no construct.** Section 4 calls P5 "the arm capable of falsifying the class argument" and
   section 5 then states that no TCF12::NR4A3 construct is emitted. The substitute offered, full-length
   GFP-TCF12, is a wild-type protein rather than a chimera, so it tests whether a non-FET N-terminus reaches
   a break, not whether the EMC minority fusion does. The single most informative prediction is the one this
   paper cannot equip, and that should be stated in section 4 where the prediction is made, not only in
   section 5.

**And there is no analysis plan.** A pre-specification without an endpoint definition, a comparison and a
sample size is not much of a pre-specification. Reference 1's methods, quoted in section 5, give the imaging
cadence (one-minute intervals for fifteen minutes), which is enough to define an endpoint on paper: a
normalised stripe-to-nucleoplasm intensity ratio, a time to half-maximal enrichment, the number of nuclei
per construct, the number of independent experiments, and the comparison to be made. None of this requires
performing an experiment; it is specification, which is what the format is for. Section 5 notes that "a
delayed curve cannot be told from a poorly expressed construct" and then supplies no expression-normalisation
step, which is a design element and can also be specified.

**Resolution.** Reduce to three independent predictions (axis placement, TAF15, TCF12), fold P4 into P2 as a
corollary, restate P1 as a rank prediction, complete P3's falsifier, split or drop P2's proximity clause,
move P5's construct limitation into section 4, and add a short analysis-plan paragraph specifying endpoint,
normalisation, replication and comparison.

### Major Point 9. The novelty claim's support is understated, and the authors' own negative findings are not disclosed

**Applies to:** section 1, paragraph 4; section 6.

Two separate issues, both about completeness rather than correctness.

**The prior-art screen.** I checked the cited artifact. The counts verify: 322 records, 238 retrieved as
full text, zero hits for ATR or replication stress. The manuscript correctly writes "no indexed report"
rather than "no report", and correctly gives the title-and-abstract matching caveat. Two further limits are
not stated and should be:

- **The screen has no positive control.** The artifact records this deliberately: "expect_pmids was left
  EMPTY deliberately ... No confident control existed for a prior-art query, so the corpus was screened by
  hand instead." A zero from a screen with no positive control cannot be distinguished from a zero from a
  screen that does not work. The manuscript should say so.
- **The corpus is anchored on the disease name, which is a different limit from abstract-only matching.**
  A FET-fusion paper that included an NR4A3 fusion construct but never used the disease name would not be
  in the 322 records at all, so it could not be missed by the matching step; it would be missed by the
  retrieval step. The companion assessment records a measured instance of exactly this failure mode in this
  programme, where a relevant series was not disease-titled and was found only by widening the query. That
  is directly relevant and should be cited as the reason the caveat is stated at the strength it is.
- **The search strategy is not reported.** Neither the manuscript nor the cited artifact records the query
  strings, the date limits or the inclusion criteria. For a novelty claim in a journal article, that is
  reportable and should be reported.

**The undisclosed companion findings.** Section 1 motivates the work with "a candidate vulnerability that
does not require the driver to be drugged is worth the cost of establishing". The companion assessment,
which this manuscript ships with and cites in section 7, reports that EMC tumours show no
proliferation-independent DDR signature on two independent series, and that ATR-inhibitor sensitivity does
not track the mechanism, one of four pre-registered tests passing, with the mechanism's load-bearing
predictor returning the wrong sign. None of this appears in the manuscript. I accept that those findings
concern transcriptional and pharmacogenomic surrogates while these predictions concern recruitment kinetics,
and that they do not refute the hypothesis. But they bear directly on whether the proposed experiment is
worth a laboratory's time, which is the manuscript's own stated motivation, and a reader who follows the
citation in section 7 will find them. Withholding them from the paper that asks for the experiment is not
defensible. Two or three sentences in section 1 or section 6 would settle it, and the paper is stronger for
volunteering them.

### Major Point 10. Presentation: one figure is worth more than all seven tables, and Appendix A must not reach an editor

**Applies to:** whole file; Appendix A; the editorial comment block; Tables 2 to 7.

**A figure is the single biggest improvement available to this manuscript.** Seven tables and no figure is
the wrong display-item mix for a paper about protein architecture, and it is a large part of why the novel
result reads as buried. I would ask for one figure with three panels, all buildable from data already in the
committed artifacts, at no cost:

- **Panel A, architecture and the RG dose.** EWSR1 (656 aa) drawn to scale, with the N-terminal [S,Y,G,Q]-rich
  low-complexity region shaded, all 30 RG dipeptides drawn as ticks at their measured positions (300, 302,
  304, 309, 314, 317, 321, 330, then 455 onwards), and the two operational RGG boxes (300 to 332 and 455 to
  638) bracketed. TAF15 (592 aa, first RG at 175, box 326 to 572) beneath it. NR4A3 (626 aa) with AF-1, the
  C4 zinc finger from residue 292, the ligand-binding domain from 373, and C166 marked. Then the four
  constructs on the same scale, with cut points at EWSR1 431, 264 and 472 and TAF15 161, so the reader *sees*
  which RG ticks fall inside each retained segment. This makes 0 of 30, 8 of 30 and 11 of 30 legible at a
  glance in a way Table 4 never will, and it shows immediately that the type-1 cut and the ATF1 exon 10 cut
  capture the same eight ticks.
- **Panel B, the axis, drawn honestly.** A one-dimensional plot of retained RG fraction, with reference 1's
  measured constructs at 0.000 and 1.000, the RGG(1) construct drawn as a hatched band because its position
  is unknown, the EWSR1::ATF1 comparator drawn as a range from 0.000 to 0.267 because the measured
  breakpoint is not specified, and the four EMC constructs plotted as predictions in a distinct style. Drawn
  this way, the panel displays the paper's central caveat instead of burying it in prose, which is exactly
  what Major Point 3 asks for.
- **Panel C, the type-2 seam at nucleotide resolution.** EWSR1 exon 7 ending at coding nucleotide 793 in
  phase 1; the single donated base; NR4A3 exon 2 (174 nt) and the 2 nt of exon 3 5' untranslated sequence;
  the 59 codons; and NR4A3's own initiator. Print the 59-residue sequence beneath. **This is the paper's
  novel result and it currently has no display item at all.** Panel C should be the panel the abstract
  points at.

**Appendix A must be deleted from the submission version.** It is 1,145 words, roughly forty per cent of the
main text length, and it is entirely internal bookkeeping: it names the project's own house-rules file four
times, cites the project's own style linter as a result, records superseded internal presentations including
bold-run and em-dash densities, and carries glyph markers and em-dashes that the rest of the manuscript has
correctly eliminated. It would go to the editor as part of the file. I note that the style gate the
manuscript passes exempts appendices, so the green result certifies everything except the one section that
most needs checking. Move this content to a repository-side changelog and remove it from the manuscript.

**The editorial comment block must be verified stripped.** It is an HTML comment, so a Markdown renderer will
drop it, but a copy-paste or a naive conversion will not. It contains a stale word count, a self-contradictory
claim (it states the manuscript is "built to the tighter" Short Communication limits of 2,500 words and six
display items while reporting 2,722 words and seven display items), and an internal instruction to "cut
section 5 first". None of that should ever be visible to an editor. Confirm removal in the produced file, not
in the source.

**Table count.** Seven tables for 2,800 words of text is too many. With the figure added, Table 2 (gene
models) and Table 7 (wild-type controls) belong in supplementary material, and Table 6 compresses to three
rows under Major Point 8.

---

## MINOR POINTS

1. **Abstract length and the stated word counts have drifted.** By a plain whitespace count the abstract is
   238 words, not the 227 the editorial block records; it is a single paragraph and within a 250-word limit,
   so this is a bookkeeping issue rather than a compliance one. The main text measures 2,812 words excluding
   table rows against the 2,722 recorded, and 3,846 including them against 3,467. Recount before submission
   and state the counting convention. (Editorial block; Abstract.)

2. **"14 residues of margin" conflicts with the census's own convention.** Section 3.4 and P3 state that the
   TAF15 exon 6 junction lies "inside the strict zero-RG window with 14 residues of margin" to the first RG
   at residue 175. The census computes margin as the RG-free ceiling minus the retained length, which here is
   174 minus 161, or 13. Fourteen is the distance to the RG position; thirteen is the number of residues that
   could be added before touching it. Either is defensible; state which is meant, and use the same convention
   as the artifact.

3. **The EWSR1::ATF1 residue numbers differ by one from the clear-cell literature convention.** Table 4 gives
   EWSR1(1-324) for the exon 8 breakpoint and EWSR1(1-348) for exon 10. These are the fully encoded residues;
   the clear-cell literature conventionally reports the exon 8 breakpoint as EWSR1 residues 1 to 325,
   counting the hybrid seam residue. The manuscript's convention is the more precise one, but it is not the
   reader's, and section 2.1 should state it explicitly so the offset is not read as an error.

4. **"Byte-identical" is repository register, not journal register** (section 3.4). Use "identical in
   sequence". This is the only such term I found in the running text; the register conversion is otherwise
   clean, and I confirmed zero glyph markers, zero em-dashes and only 22 bold runs across the Abstract to
   section 8.

5. **"The source" is used ten times as a noun for reference 1.** In journal register this should be
   "Gracilla and colleagues" or "reference 1". The construction reads as internal shorthand. Similar:
   "this programme" (twice), which most journals would render as "we" or "the present analysis".

6. **The artifacts cited in section 7 disagree with the manuscript's own reference list.** Section 7 states
   that "any figure above that disagrees with the artifact is an error in this document", which invites a
   reader to check. Three mismatches await them: the construct artifact and the census both cite reference 1
   as the preprint rather than the published version corrected in Appendix A; the type 5 and TAF15
   breakpoint sources in the construct artifact still cite the conference abstract that reference 7 replaced;
   and the census carries a field literally named `emc_canonical_EWSR1_NR4A3` describing an exon 7 to exon 3
   junction that this manuscript's own Appendix A states is not a reported type. Either regenerate the
   artifacts or add a dated note to section 7 recording that the committed artifacts predate the reference
   correction.

7. **The verbatim quotation from reference 1's methods in section 5 runs to about 85 words.** Extended
   verbatim quotation from a copyrighted methods section may require permission. Consider paraphrasing to
   the operative parameters (cell line, dye, wavelength, power, stripe width, imaging cadence and duration),
   which loses nothing a replicating laboratory needs.

8. **Report NR4A3's own RG content.** The artifact records `rg_dipeptides_total: 2` for full-length NR4A3.
   The GFP-NR4A3 control in Table 7 exists to test whether the partner alone reaches a break, and its
   interpretation depends on the partner not carrying FET-like RG content. Two dipeptides against EWSR1's
   thirty is a strong quantitative statement in the control's favour and it is free to include.

9. **Table 5's sweep row is graded "decisive" on an asymmetric comparison.** The sweep gives TCF12 every
   prefix from 50 residues to full length and compares its best value, 0.400, against the FET proteins at a
   single fixed 250-residue window. I ran the symmetric version: sweeping all three FET proteins over the
   same prefix grid gives a lowest FET value of 0.439 (EWSR1 at 1 to 560). The conclusion survives, and I
   want to be clear that it does, but the separation is 0.039 rather than the 0.140 the table implies.
   Report the symmetric comparison and soften "decisive" for that row. The 250-residue row (0.368 against a
   FET minimum of 0.540) is genuinely decisive and can keep the grade.

10. **The [S,Y,G,Q] metric has no background.** A reader cannot tell whether TCF12's 0.368 is
    characteristically non-FET or moderately FET-like, because those four residues have a substantial
    background frequency in any protein. A distribution over a panel of other non-FET 5' fusion partners, or
    over a proteome background, would place 0.368 on a scale. This is computable from sequence at no cost and
    would materially strengthen section 3.5, which is currently the least surprising result presented at the
    greatest length.

11. **Section 2.3 says "three independent tests, plus one sweep" and Table 5 shows five rows.** The RG row
    and the RGG-box row are both part of test two, which a reader counting rows will not infer. Appendix A
    records that a three-versus-four mismatch of exactly this shape was corrected once already. Label the
    Table 5 rows with their test numbers.

12. **The pazopanib figures are cited to a review rather than to the trial report.** Section 1 attributes an
    18 per cent objective response rate and 19-month median progression-free survival to reference 2, a 2025
    comprehensive review. I verified that reference 2 does report both figures, so the citation is accurate;
    but the primary trial report is the conventional citation and is available. Cite both, or the primary
    alone.

13. **Table 3's "extra residues" column needs a clarifying note for the type-2 row.** The definition given,
    "encoded across the seam by neither partner's own reading frame", is correct but suggests a short hybrid
    seam. For type 2 the value is 59, of which one residue is the hybrid codon and 58 are encoded entirely by
    NR4A3 sequence read in a frame NR4A3 does not itself use. A footnote prevents the reader from assuming a
    59-residue hybrid junction.

14. **Submission metadata is incomplete.** The ORCID line is a bracketed placeholder in the manuscript body;
    there is no keyword list; and the cover letter carries a bracketed date. None of these should survive to
    submission.

15. **The "Scope of the claims" blockquote at the head of the paper.** Its content is correct and important,
    and I would not lose any of it, but most journals would ask for it as the opening paragraph of the
    Limitations section rather than as a standing disclaimer above the Abstract. Prose that pre-emptively
    declares its own restraint reads as advocacy in the position it currently occupies; the same sentences
    read as rigour in section 6.

---

## What I checked and could not fault

Recorded because a review that lists only defects misrepresents the manuscript.

- **The reproduction claim in section 2.5 is true.** `python3 research/modalities/emc_fet_construct_designs.py --check`
  runs offline and prints `REPRODUCES`.
- **Every sequence figure I recomputed from the committed input cache matched the manuscript**, including
  all four open reading frame lengths, all retained-residue counts, all RG counts and fractions, all four
  [S,Y,G,Q] fractions, all six alignment identities, the 66-prefix sweep and its maximum of 0.400 at
  residues 1 to 160, and the 59-residue translation with no internal stop.
- **The internal arithmetic of Table 3 is exactly self-consistent**: 431 + 1 + 626 = 1058, 264 + 59 + 626 =
  949, 472 + 1 + 626 = 1099, 161 + 1 + 626 = 788, and each open reading frame nucleotide length is three
  times its residue count.
- **The domain-retention claims verify against the sequence**: NR4A3 residue 166 is a cysteine, residue 292
  is the first cysteine of the C4 zinc finger, and all four constructs retain NR4A3 from residue 1.
- **Every reference identifier traces to a committed retrieval record**, and reference 1's published-version
  bibliographic details match that record field for field, including the change of first author between
  preprint and published version.
- **The TCF12 database mismatch flagged in Table 2 does not affect the conclusion**, as the manuscript
  claims. I recomputed the RG count and the 250-residue composition on both the 706-residue and the
  682-residue sequences and they are identical.
- **Limitation 2 is unusually honest.** Disclosing an exon-indexing error in one's own prior work, in the
  Limitations of the paper that corrects it, is rarer than it should be and is to the author's credit.
- **The manuscript stands alone.** I read the companion assessment and the manuscript does not depend on it
  for intelligibility. Major Point 9 asks for two or three sentences from it, but as a matter of disclosure,
  not of comprehension.

---

## Revision list

Work through top to bottom. Every item is achievable by re-analysis of public sequence, restructuring,
better display items, or honest weakening of language. No item requires new laboratory data.

**A. Factual corrections, highest priority**

1. `emc-atr-collaborator-package.md`, Abstract, sentence 6 — delete "the two commonest EMC fusions".
   Replace with wording that names type 1 as the commonest and type 2 as a reported minority variant.
2. Same file, Table 1 — replace the "reported rank" column with counted frequencies and their sources.
   Use reference 7's series (type 1 in 10 of 15, type 5 in 2 of 15) and the Okamoto 2001 series committed
   in `research/manuscripts/lit-targets-aso-verify.json` (type 1 in 11, type 2 in 1, TAF15 in 3, of 15
   fusion-positive cases). Remove the unsourced "second" for type 2.
3. Same file, section 3.4, paragraph 2 — rewrite so the argument does not rest on type 2 being common. Add
   one sentence stating that TAF15::NR4A3, not type 2, is the more frequent zero-RG EMC fusion.
4. Same file, Abstract sentence 5, section 3.3 sentences 1 and 2, Table 3 note, Appendix A row 2, and
   `emc-atr-collaborator-package-cover-letter.md` paragraph 3 — correct the arithmetic in all five places
   to: the split codon at the seam plus 176 nucleotides of NR4A3 5' untranslated sequence (174 from exon 2
   and 2 from exon 3) are read in the EWSR1 frame as 59 residues with no intervening stop.
5. Same file, section 3.3 — add the translated 59-residue sequence to the manuscript text, and state that
   the first residue is a hybrid codon and the remaining 58 are NR4A3 sequence in a non-native frame.
6. Same file, Table 4 — split the "status" column into "measured in reference 1" and "reported breakpoint of
   a disease in which the mechanism was measured".
7. Same file, Table 4 — restore the EWSR1::ATF1 exon 7 row (EWSR1(1-264), 0 of 30, 0.000) from
   `research/modalities/emc-fet-construct-designs.json`.
8. Same file, Table 4 — restore the EWSR1-RGG(1)-FLI1 anchor with an explicit "position on this axis not
   determinable; the reintroduced RGG domain is not identified in the source".
9. Same file, section 3.4, paragraph 3 — add a sentence stating that the EWSR1 breakpoint of reference 1's
   EWSR1-ATF1 construct is not specified in the source as retrieved, so the ATF1 comparator spans 0.000 to
   0.267. Delete or requalify "bracketing" and "interpolate between points already measured".
10. Same file, P2 — restate the basis, which currently assumes the exon 8 ATF1 breakpoint.

**B. Results that should be added because they are already computed**

11. Same file, section 3.2 — state the frame rule: an EWSR1::NR4A3 fusion is in frame if and only if the
    EWSR1 donor exon ends at coding phase 1, and both NR4A3 acceptors give the same register because exon 2
    is 174 nucleotides.
12. Same file, section 3.2 — add a table of EWSR1 donor exon, coding phase, and in-frame status against both
    NR4A3 acceptors, derived from `research/modalities/junction-mrna-frame-audit.json`.
13. Same file, section 3.2 or 3.3 — state that the 59-residue extension is a property of the exon 2 acceptor,
    so any fusion using it carries the extension.
14. Same file, section 2.1 or 3.2 — establish the literature-to-Ensembl exon numbering correspondence for
    NR4A3, using reference 7's genomic mapping (12 breakpoints in intron 2, 2 in intron 1) and reference 3's
    cryptic-exon quotation.
15. Same file, section 2.1 and section 7 — cite the RefSeq-derived cross-check in
    `research/modalities/junction-aso-designs-e7n3.json`, which independently reproduces the 2-nucleotide
    exon 3 5' untranslated segment and the identical seam.
16. Same file, section 3.3 — replace "the protein-level model in general use" with a statement of what is
    actually documented, and cite reference 3's 25-residue TAF15 cryptic-exon extension as precedent for the
    mechanism.
17. Same file, section 3.5 and Table 5 — add the symmetric FET prefix sweep. Report that the lowest FET
    prefix value is 0.439 against TCF12's best of 0.400, and soften "decisive" on that row only.
18. Same file, section 3.5 — add a background or comparator panel for the [S,Y,G,Q] metric so 0.368 sits on
    a scale.
19. Same file, Table 7 — add NR4A3's own RG dipeptide count (2) to the GFP-NR4A3 control row.

**C. Provenance and reproducibility**

20. Same file, Table 2 — give the full versioned transcript and translation accession for TAF15, FUS and
    TCF12 in place of "canonical".
21. Same file, section 2.1 or 2.5 — state the Ensembl release, the genome assembly and the retrieval date.
22. Same file, section 7 — add a dated note recording that the committed artifacts predate the reference 1
    correction and still cite the preprint, that the type 5 and TAF15 breakpoint sources still cite the
    conference abstract, and that the census carries a field named for a junction that is not a reported
    type. Alternatively regenerate the artifacts.
23. Same file, section 1, paragraph 4 — add the prior-art screen's search strategy, the absence of a positive
    control, and the fact that the corpus is anchored on the disease name so a FET-fusion paper not naming
    EMC would not be in it.

**D. Predictions**

24. Same file, section 4 and Table 6 — reduce to three independent predictions; fold P4 into P2 as a
    corollary.
25. Same file, P1 — restate as a rank prediction rather than an equivalence claim.
26. Same file, P3 — add "no accumulation at the stripe" to the falsifier.
27. Same file, P2 — drop the "closest to the commonest clear-cell type" clause or move it to the explicit
    non-predictions, noting that the type 1 and ATF1 exon 10 cuts retain the same eight RG dipeptides.
28. Same file, section 4 — state where P5 is made that no TCF12::NR4A3 construct is supplied and that the
    substitute tests a wild-type protein rather than a chimera.
29. Same file, new short subsection in section 4 or 5 — add an analysis plan: endpoint quantity,
    expression normalisation, nuclei per construct, independent experiments, and the comparison to be made.

**E. Disclosure**

30. Same file, section 1 or section 6 — disclose the companion assessment's negative findings: no
    proliferation-independent DDR signature in EMC tumours on two independent series, and ATR-inhibitor
    sensitivity not tracking the mechanism, with one of four pre-registered tests passing.

**F. Framing and presentation**

31. Same file, title and frontmatter `title` — retitle to lead with the 59-residue extension. Update
    `emc-atr-collaborator-package-cover-letter.md` line 35 to match, and regenerate
    `systems/views/L3-publications.md`.
32. Same file — build and insert one three-panel figure: (A) scaled architecture of EWSR1, TAF15 and NR4A3
    with RG tick positions, RGG boxes and domain boundaries, and the four constructs on the same scale;
    (B) the retained-RG axis with the ATF1 comparator drawn as a range and the RGG(1) anchor drawn as
    unplaced; (C) the type-2 seam at nucleotide resolution with the 59 codons and the translated sequence.
33. Same file — move Table 2 and Table 7 to supplementary material.
34. Same file — restructure sections 4 and 5 into a Discussion subsection, so the Results end with sequence
    and the proposal follows from them.
35. Same file — delete Appendix A from the submission version and move its content to a repository-side
    changelog.
36. Same file — confirm the editorial HTML comment block is stripped by whatever conversion produces the
    submitted file, and correct its internal contradiction (it claims the manuscript is built to a 2,500-word,
    six-display-item limit while reporting 2,722 words and seven display items).
37. Same file — recount the abstract and main text and state the counting convention; the abstract measures
    238 words by a plain whitespace count against the 227 recorded.
38. Same file, section 3.4 — replace "byte-identical" with "identical in sequence".
39. Same file, throughout — replace "the source" with "Gracilla and colleagues" or "reference 1", and
    "this programme" with "the present analysis".
40. Same file, section 2.1 — state the residue-numbering convention (fully encoded residues only) and note
    that it differs by one from the clear-cell literature's EWSR1 1 to 325 for the exon 8 breakpoint.
41. Same file, section 3.4 and P3 — state the margin convention and use the artifact's (13 residues to the
    RG-free ceiling), or say explicitly that 14 is the distance to the first RG position.
42. Same file, Table 5 — label rows with their test numbers so the count in section 2.3 matches the rows.
43. Same file, Table 3 — footnote the type-2 "extra residues" value to prevent it being read as a 59-residue
    hybrid junction.
44. Same file, section 5 — paraphrase the extended methods quotation from reference 1 to its operative
    parameters.
45. Same file, section 1 — cite the primary pazopanib trial report alongside or instead of the 2025 review.
46. Same file — supply an ORCID or remove the placeholder line; add a keyword list;
    `emc-atr-collaborator-package-cover-letter.md` — fill the bracketed date.
47. Same file — move the "Scope of the claims" blockquote into section 6 as its opening paragraph.
