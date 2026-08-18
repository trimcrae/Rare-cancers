---
id: DOC-FUSION-JUNCTION-ASO-SUBMISSION
title: "Nearly half of junction-spanning gapmer designs against the NR4A3 fusions of extraskeletal myxoid chondrosarcoma pair a wild-type parent gene, and a longer catalytic gap cannot separate them"
level: L3
kind: manuscript
status: live
canonical_for:
  - the submitted form of the fusion-junction ASO work
purpose: >
  The submission manuscript for PUB-ASO, deposited first to bioRxiv as a preprint. Its provenance
  archive, including every superseded value and the full correction history, is
  fusion-junction-aso-working-record.md; the numbers themselves live in the artifacts under
  research/modalities/ and are not duplicated here.
scope: >
  Computational design and specificity screening only. No wet-lab experiment was performed, and
  nothing here asserts efficacy, potency, safety, a therapeutic window, delivery to a tumour, or
  clinical readiness for any sequence. Every sequence named is a research reagent for laboratory
  investigation only and must not be administered to any person or animal. ⚠ THIS BLOCK IS STRIPPED
  FROM BOTH PDF BUILDS by build_submission_pdf.py and reaches no reader of the deposited article, so
  it is a routing copy: the operative statements live in the Abstract, in section 4.1 and in
  Declarations, and deleting them from there deletes them from the paper. Box 1 points at
  Declarations rather than restating it.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-15
last_verified: 2026-08-15
---

# Nearly half of junction-spanning gapmer designs against the *NR4A3* fusions of extraskeletal myxoid chondrosarcoma pair a wild-type parent gene, and a longer catalytic gap cannot separate them

**Author.** Tristan D. McRae

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [PLACEHOLDER — AUTHOR TO SUPPLY BEFORE DEPOSIT. This is not an identifier, and the deposit is
blocked until it is replaced.]

**Running title.** Junction gapmers across NR4A3 fusions

**Keywords.** antisense oligonucleotide; gapmer; RNase-H1; fusion transcript; NR4A3; extraskeletal
myxoid chondrosarcoma; oligonucleotide design pipeline; off-target screening

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma in which a variable partner gene
fuses to *NR4A3*, creating a junction present in no normal transcript. An antisense gapmer could in
principle cleave the fusion and spare both parent genes; none is reported. Of 190 junction-spanning
designs across the 38 in-frame junctions of five modelled partners, 87 pair their catalytic gap
against a mature parent transcript over a contiguous duplex of at least ten base pairs, 61 against
wild-type *NR4A3*. Arbitrary sequence pairs a parent far less often: scrambles reach 6.2% and
random-offset chimeras of the same two parents 23.8%, against 45.8% observed. Nor is that excess
resolved as specific to the disease's own breakpoints: an exon-terminus chimera no patient is
reported to carry reaches 40.6%. Lengthening the catalytic gap quiets the transcriptome but cannot
separate the fusion from its parents: the junction-unique bases a longer gap wins and the
wild-type-parent duplex it concedes are the same nucleotides. The work is computational: no wet-lab
experiment was performed, nothing has been synthesised or tested, and nothing here asserts efficacy,
safety, delivery to a tumour or clinical readiness. Every sequence named below is a research reagent
for laboratory investigation only and must not be administered to any person or animal. Two are
named for synthesis with their off-target loads, 5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 and
5′-GGGCATATCTTGTGTG-3′ at *TAF15* exon 6, and three as not to be used, each pairing its whole
catalytic gap against the patient's own un-rearranged *NR4A3* allele. The design and screening
pipeline is released, so a candidate can be designed for a breakpoint outside this panel by the same
procedure.

---

## 1 · Introduction

EMC is defined in the large majority of cases by an in-frame fusion of *EWSR1* to the orphan nuclear
receptor *NR4A3*,<sup>1</sup><!--PMID:8634690--> with *TAF15* a substantial minority and *TCF12* and
*TFG* rare.<sup>2</sup><!--PMID:32572850--> *FUS::NR4A3* is reported in a recent series that
identified it by sequencing in two of five variant EMCs.<sup>3</sup><!--PMID:41755350-->
Next-generation sequencing of six EMCs finds few recurrent secondary mutations beyond the
fusion,<sup>4</sup><!--PMID:28423517--> so it is to a first approximation the single clonal driver. In
every junction type described, the predicted product joins the partner's amino-terminal
transactivation domain to essentially the entire NR4A3 protein, including its nuclear-receptor
DNA-binding domain.<sup>1,5</sup><!--PMID:8634690,11156374-->

That driver is currently untargeted. Surgery with clear margins is the backbone of localised disease,
and for advanced disease no clinically validated agent directly targets
*NR4A3*.<sup>6</sup><!--PMID:41055792--> The largest EMC-specific prospective study, a single-arm
phase 2 of pazopanib in centrally confirmed *NR4A3*-translocated disease, returned four objective
responses in 22 evaluable patients;<sup>7</sup><!--PMID:31331701--> anthracycline-based chemotherapy
returned four in ten evaluable patients in a molecularly confirmed retrospective series of eleven, a
result that series presents as running counter to the prior record.<sup>8</sup><!--PMID:24345066-->
Two of those sources report a low objective response rate to that chemotherapy and low sensitivity to
cytotoxic chemotherapy generally,<sup>6,7</sup><!--PMID:41055792,31331701--> and none of the three
publishes a response rate by line of therapy. The population a fusion-directed agent would address is
close to the whole disease: across 58 molecularly confirmed cases, 79% carried *EWSR1::NR4A3*, 16%
*TAF15::NR4A3* and 3% *TCF12::NR4A3*.<sup>9</sup><!--PMID:36948401-->

The chimeric mRNA offers a discrimination handle its protein product does not. The *NR4A3*
ligand-binding domain is retained near-intact and identical in sequence to wild-type NR4A3, so a
ligand that engages it cannot distinguish fusion from wild type. The breakpoint junction can: it is a
contiguous stretch of sequence present in no normal transcript and absent from both parent
transcripts, so selectivity can in principle be enforced by base-pairing rather than by protein
conformation. It is the target of every design here.

Targeting a fusion breakpoint with an oligonucleotide is not new. The approach has a continuous
lineage from 1991,<sup>10</sup><!--PMID:1794439--> including RNase-H-dependent antisense at a sarcoma
fusion breakpoint in 1997,<sup>11</sup><!--PMID:9049825--> and the fusion-exclusivity rationale was
stated as a general principle in 2005.<sup>12</sup><!--PMID:16083345--> Parental sparing has been
reported at four fusions, two with a readout on the wild-type parent transcript and two asserting
junction specificity without one.<sup>13–16</sup><!--PMID:33241214,36265509,21846246,23052253--> A
bi-shRNA lipoplex against the *EWSR1::FLI1* junction reached preclinical
justification,<sup>17</sup><!--PMID:27166877--> and a GalNAc-conjugated junction siRNA in
fibrolamellar hepatocellular carcinoma passed the delivery gate in a rare fusion-driven cancer,
reaching durable growth inhibition in patient-derived
xenografts.<sup>18</sup><!--PMID:37980543--> That last precedent does not transfer to this disease
and is cited for the junction, not for the route: GalNAc conjugates enter cells through the
asialoglycoprotein receptor, which is a liver receptor, and the report's own basis for using it is
that fibrolamellar tumours retain that receptor at hepatocyte levels. An extraskeletal soft-tissue
sarcoma satisfies neither premise, and no delivery route is proposed anywhere in this paper. The
contribution here is the indication rather than the
modality: across 5,153 unique records retrieved from Europe PMC, four mention *EWSR1::NR4A3* at title
or abstract level, resolving to three papers, none an oligonucleotide study.

Two questions follow that the field has not asked of this disease. The first is whether specificity
sorts by partner at all. Prior design work has addressed only *EWSR1*, while the partner varies, and
partner identity may not be clinically inert: across the two series of antiangiogenic
tyrosine-kinase inhibition in advanced EMC that report a partner breakdown at all, no objective
response is reported in a *TAF15* patient, on a *TAF15* arm of three to five patients whose Wilson
upper bound remains compatible with equal
response.<sup>7,19</sup><!--PMID:31331701,24703573--> The two series are not shown to be independent cohorts, which is why the count is a range and why
they are not pooled: the smaller ran at an institution that was a site of the larger trial, under
the same senior investigator, so the same patients may appear in both and the distinct *TAF15* arm
may be as few as three.
Neither primary report states the per-arm
denominators; the sunitinib report states the partner split only qualitatively, and both denominators
are read from published reviews of the two series.<sup>20,21</sup><!--PMID:32967265,33799327--> The
second is whether a junction oligonucleotide must be bespoke per patient, or whether one sequence can
serve more than one fusion, which decides whether the deployable artefact for an ultra-rare disease
is a stock reagent or a panel.

This paper answers both from sequence, sets out where a computational screen stops being able to
answer them, and ends by naming the oligonucleotides to synthesise, the controls that make a
knockdown result interpretable, and the pre-registrable threshold that would falsify, at its top margin, the ranking
every candidate here is ordered by (§4). The design and screening procedure is released with the
artefacts, so a candidate can be designed by the same route for a breakpoint the panel does not
carry (§4.5). Box 1 collects the sequences, the cautions and the terms of art the sections below use
before the Methods (§6) define them.

## Box 1 · Sequences, cautions and the void condition

**Research use only.** Every sequence in this box is a research reagent for laboratory investigation
only, and the operative statement is in Declarations.

Every line below points at a fuller statement in the section cited, and none of it is argued here.

**The terms of art (§6).** Each design is one *register* of its junction, one way of sliding the
16-mer while the breakpoint still falls inside the six-nucleotide DNA *catalytic gap* RNase-H1
cleaves within; the 5-6-5 geometry admits five per junction. A design's *gap-level margin* is the
count of junction-unique bases inside that gap on the shorter side of the breakpoint, and every
ranking here is built on it. A *near-match* is a transcript window pairing a design at 14 or more of
its 16 positions, and is *gap-paired* where the six gap positions are themselves paired, which is the
class RNase-H1 could cleave. A design is *clean* where a complete hit list at a stated search depth
returns no sense-strand near-match, and a design's *load* is its predicted off-target burden counted
as near-matches. Counts from that hit list come at one of two search depths, a default alignment
ceiling and a tenfold deeper one, and each is reported with the depth it was taken at. Five screens
are applied, numbered here as in §6: (1) the
alignment screen, (2) the exhaustive transcript scan, (3) the pre-mRNA screen, (4) the mature-parent
screen and (5) the genome scan.

**The two reagents to synthesise (§4.1).** 5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 joined
to *NR4A3* exon 3, carrying 123 gap-paired sense-strand near-matches at six gene loci at the deeper
search ceiling together with a sense-strand near-match in wild-type *TAF15* precursor RNA (§4.3); and
5′-GGGCATATCTTGTGTG-3′ at *TAF15* exon 6, carrying 8 such near-matches at five loci and no
sense-strand pre-mRNA site. Both hold the top gap-level margin of 3, and neither has been synthesised
or tested. Between them they reach roughly two thirds of molecularly confirmed cases, on the
coverage ladder that prices every rung and bound above them (§4.1).

**Three designs not to be used (§2.6).** 5′-CAGTGGGCTCTCCACG-3′ and 5′-GCAGTGGGCTCTCCAC-3′ at *EWSR1*
exon 13 joined to *NR4A3* exon 2, and 5′-TGATGAGGGCCTTGTG-3′ at *TAF15* exon 6 joined to the *NR4A3*
intron-2 cryptic exon. Each cleared the spliced-cDNA parent screen, and each pairs its whole
catalytic gap against the patient's own un-rearranged *NR4A3* allele, which that screen cannot see.

**The cell line (§3).** No *NR4A3* fusion is detectable in H-EMC-SS on the public record, so no
reagent named here can be tested in it. That is not a statement that the line is misidentified.

**The replicate floor and the void condition (§4.4).** Selectivity is the wild-type *NR4A3*
half-maximal knockdown concentration divided by the fusion's, from a matched dose–response in the
same wells, and the cut is 5.0, taken as a convention rather than measured for this comparison (§4.4). Three biological replicates are a floor and not a target: above a
replicate standard deviation of about 0.65 on the log scale, no observed ratio at or above one can
place a 95% upper bound below that cut at three replicates, so the test can fail only where the
reagent is anti-selective and the design is otherwise void rather than negative. A *void* design is
one whose test cannot fail, which is a different outcome from one that fails to falsify. The
controls, the assay placement and the limit-of-quantification condition without which
the ratio is not reportable are in §4.4.

**A design procedure for a breakpoint outside this panel (§4.5).** The pipeline that produced the
190 designs is released with the artefacts, and §4.5 gives its input, the five screens a new design
must clear, and the limit on what it produces: a candidate, not a validated reagent.

## 2 · Results

The results are ordered for a laboratory deciding what to make. How far any of the counts below can
be trusted is stated in §5, which bounds all of them.

**How the counts are denominated.** Six numbers recur below and they are not interchangeable. 231 is
the donor-exon by acceptor-exon pairs graded for frame. 38 are the in-frame junctions among
them. Those 38 carry 190 design records, which are 176 distinct molecules, because nine of the
16-mers span more than one partner's junction and are recorded once per junction. Of the 190, 183 have a
returned specificity screen; the other seven failed at the remote service, which matters because a
free energy needs only a sequence where a screen needs a query that came back. 187 is the count
re-screened at the tenfold deeper ceiling. Each result below names the denominator it uses.

### 2.1 · The reading frame as the bound on junction space

Grading all 231 pairs of a donor exon with *NR4A3* exons 2-4 across the five partners returns 38
in-frame junctions (Table 1, Figure 1). The refusals are structural. *NR4A3* exon 2 carries
no coding sequence and is refused in every pair, and an exon-4 acceptor would delete the *NR4A3*
DNA-binding domain that every reported EMC chimera retains. All the variance therefore sits in the
exon-3 column. Within that column, being in frame reduces to a single arithmetic condition, a
donor coding phase of 1, which is necessary and sufficient across its 77 rows but only necessary
across all 231.

Among these, *EWSR1* exon 12 joined to *NR4A3* exon 3 is the junction reported most often: type 1 in
10 of the 15 *EWSR1*-rearranged tumours of an 18-case series.<sup>22</sup><!--PMID:12378528--> Designs
at this junction therefore correspond to the largest documented patient group.

No design at any of the 38 junctions is a perfect complement of any of the six parent transcripts.
That test excluded none of the 190, because a junction-spanning window cannot occur intact in a parent.
GC runs 25.0–75.0% across partners, with 132 of the 190 inside the conventional 40–60% band. Finding
candidate sequences is therefore not the constraint on this modality in this disease.

### 2.2 · Cross-partner coverage by a single oligonucleotide

Nine designs span more than one partner's junction exactly, and all nine draw from *EWSR1*, *TAF15*
and *FUS* (Figure 2). Five cover the same three-partner set, differing only in register across the
junction. The best by gap-level margin is 5′-GGGCATATCATCAAAC-3′ (43.8% GC, gap-level margin 3), which
divides eight donor and eight acceptor bases at the junction of *EWSR1* exon 12, *TAF15* exon 11 and
*FUS* exon 10 joined to *NR4A3* exon 3, and occurs in none of the six wild-type parent transcripts.
The basis is sequence identity: the three donors are identical over the ten bases immediately 5′ of
their breakpoints, diverging at the eleventh. No design draws more than ten donor bases, which is
what makes the coverage arithmetically possible.

In one respect the published data contradict the clinical reading of this result. The only
exon-resolved *TAF15::NR4A3* breakpoints reported in EMC are at exon 6, not exon 11. The primary
report of the variant fusion places the breakpoint there,<sup>23</sup><!--PMID:10537274--> and in a
series of 18 EMCs all three *TAF15*-rearranged tumours carried exon 6 joined to *NR4A3* exon
3.<sup>22</sup><!--PMID:12378528--> The exon-6 junction shares a single donor base with the exon-11 junction,
so this oligonucleotide cannot engage the *TAF15* junction that patients are reported to carry.

That junction is itself in-frame and yields five fusion-specific designs (43.8–50.0% GC), all
five screened and orientation-filtered. Every one of them retains a sense-strand near-match spanning
the catalytic gap. At the tenfold deeper ceiling, where every hit list is complete, those recount to
three gene loci at best, and five for the design its gap-level margin ranks first, three of those
five annotated only as predicted gene models (Table 2). Two of the five nonetheless return no exact
and no single-mismatch match on the exhaustive transcript scan.

So the one *TAF15* junction with a published breakpoint is designable and is not among the cleaner
junctions, while the junction the multi-partner result rests on has no reported patient. For *FUS* no
exon-resolved EMC breakpoint has been published at all. The three-partner result is therefore a
statement about FET-family (*FUS*, *EWSR1*, *TAF15*) sequence architecture and a hypothesis about junctions not yet observed.
It is not a claim that one reagent serves three patient groups. Testing it requires breakpoint
sequencing of archival *TAF15*- and *FUS*-positive cases.

### 2.3 · The non-FET partners: coverage and specificity

*TCF12* and *TFG* are the partners in this panel that are not FET-family proteins, and neither
appears in any of the nine multi-partner sets: all nine draw only on *EWSR1*, *TAF15* and *FUS*.
*TCF12* reaches multi-partner coverage only under a relaxed criterion that tolerates mismatches in
the oligonucleotide wings. That check had little power to fail, since any non-homologous donor would
be excluded, so it does not separate FET paralogy from incidental exon homology. The stronger
evidence for paralogy is that the remaining four of the nine, which span two partners rather than three, are also FET-only.

Specificity does not sort by partner. Taking at each junction the lowest count any of its
designs achieves after the orientation filter — a per-design minimum, which is in the released
per-junction screens and not in Table 3, whose row is that junction's highest-margin design and not
its cleanest — every one of the five partners has at least one
junction whose cleanest design carries no sense-strand near-match across the catalytic gap at the
default search ceiling: three of eight at both *TCF12* and *FUS*, two of eight at *EWSR1*, one of
eight at *TAF15* and one of six at *TFG*. At the tenfold deeper ceiling that becomes four partners:
each of *EWSR1*, *FUS*, *TAF15* and *TCF12* keeps one such junction and *TFG* keeps none, its single
default-depth zero returning 29 across the gap when searched deeper. The
minima therefore separate junctions rather than partners. Which exon a fusion breaks at matters more
for specificity than which gene it breaks into.

The same tension the *TAF15* result carries applies to *TCF12*, and in the same direction. The one
published *TCF12::NR4A3* breakpoint describes a chimera retaining the first 108 TCF12
residues,<sup>5</sup><!--PMID:11156374--> and names no exon; the same authors deposited the chimeric
cDNA, and that deposit resolves the junction to the nucleotide. GenBank AF289510.1 carries two
chromosome-tagged source features that meet at the junction. Mapped against the transcript models
used here, the donor side ends at *TCF12* exon 5 and at no other exon, the acceptor side begins at
*NR4A3* exon 3 and at no other exon, and the twelve bases either side of the seam are identical to
the seam the panel was designed on. The base-level assignment, its chromosome-tagged coordinates and
the translation check that reproduces the deposit's own recorded protein are in the released
artefact. That junction is in-frame and designable, and its best-margin design retains 17
gap-spanning near-matches at the deeper ceiling, every one of them a variant of a single curated
locus, *PIK3CG* (Table 2). None of the four *TCF12* designs with no sense-strand near-match is at
that exon. So for *TCF12* as for *TAF15*, the junction a patient is reported to carry is designable
and is not among the clean ones, while the clean junctions have no reported patient. What remains
unmeasured at *TCF12* is not the exon but the distribution: one *TCF12*-rearranged tumour has been
sequenced at this junction, and it is the tumour the junction was defined by. No search of the
nucleotide or read archives returns a second *TCF12::NR4A3* sequence, and what that leaves the
coverage estimate resting on is stated with the estimate (§4.1).

The same archive search resolves *TFG*, the other non-FET partner, in the same way and to the same
limit. No paper places a *TFG::NR4A3* breakpoint at an exon, but a deposited chimeric mRNA record
does — GenBank AY532911.1, annotated as a *TFG-NR4A3* fusion protein — and it lands on *TFG* exon 7
joined to *NR4A3* exon 3, a junction this panel already carries. Four patent sequence records agree
at the seam — GenBank DI433544.1, DI438966.1, LG067227.1 and LG067228.1 — corroborating a sequence
rather than four patients, being one family from one group. As
at *TCF12*, what the deposit supplies is the exon and not the distribution: no source states what
fraction of *TFG*-rearranged tumours break there, and *TFG* does not appear in the partner counts of
the 58-case cohort every coverage figure here is denominated on, so this changes which junctions are
reported and no percentage.

### 2.4 · Strand orientation, and designs with no sense-strand near-match

All 38 in-frame junctions were screened with orientation filtered, covering 183 designs, and Table 3
gives the per-junction result. Of the 1,677 apparent cleavage risks across the retained hit lists,
738 sit on the minus strand, or 44%. An antisense oligonucleotide cannot base-pair with those at all.

The proportion is not uniform. It runs from 0% at *TFG* exon 4, where no apparent risk is
minus-strand, to 100% at both *EWSR1* exon 1 and *TCF12* exon 7, where every one is. That
non-uniformity is what makes the filter worth applying rather than approximating. A uniform
inflation would rescale every junction and leave their ordering intact; this one reorders them.
*EWSR1* exons 7 and 13 return 55 and 57 apparent gap-spanning hits, and after filtering they stand
at 6 and 53.

Under the stricter criterion — no sense-strand near-match anywhere, not merely across the catalytic gap
as in §2.3 — nine designs at six junctions carry none among non-parent transcripts after filtering
(Table 4), spanning four of the five partners: three at *EWSR1* exon 1
(5′-GGGCATATCCGTGGAC-3′, 5′-GGCATATCCGTGGACG-3′, 5′-GCATATCCGTGGACGC-3′), one at *FUS* exon 8
(5′-AGGGCATATCGGAGTC-3′), one at *TAF15* exon 1 (5′-GGGCATATCCGACATG-3′), and four at *TCF12* —
5′-GGGCATATCTCTATAA-3′ at exon 17, 5′-CAGGGCATATCTTGCA-3′ at exon 9, and
5′-GGCATATCAAGCGCTG-3′ and 5′-GCATATCAAGCGCTGC-3′ at exon 7. The exhaustive transcript scan agrees
independently: each returns no exact and no single-mismatch match anywhere in 186,185 transcripts.
The two screens fail in different ways, so their agreement is not a restatement. One is a heuristic
alignment search over both strands; the other an exhaustive substitution scan over the sense
orientation only. The pre-mRNA screen, over a compartment neither of those reaches, does not
overturn them either: none of the nine has a sense-strand site in parent pre-mRNA (§2.5).

The graded re-score agrees, with one instructive exception. Scoring every retained hit by the
residual cleavage a gap-internal mismatch is predicted to permit, under both literature bounds,
returns a residual load of zero for all nine. It returns zero for one further design too, at *FUS*
exon 11, which is not counted as clean here. That design returns 21 near-matches, of which only 15
are retained, and all 15 are minus-strand. The graded score therefore sees nothing it can score,
while the cleanliness criterion refuses the design because the strand of the six unretained hits is
unknown. The graded model has no censoring guard, so it can award a zero the hit list does not
support, and the stricter count is the one reported. A zero for the nine is arithmetic rather than an
independent measurement: it follows from their having no sense-strand hit to score.

Every junction was then re-screened at a tenfold deeper alignment ceiling, with retention raised to
match so that no hit list is truncated: 38 junctions and 187 design records. The result withdraws
most of the set above. The 187 are the panel's 190 less three that failed at the remote service on
this pass, two at *FUS* exon 5 and one at *TFG* exon 2. They had returned 23, 41 and 31
near-matches at the default depth, so none was a candidate and no count below depends on them. Only
three of the nine still carry no sense-strand near-match: 5′-AGGGCATATCGGAGTC-3′ at *FUS* exon 8,
5′-GGGCATATCCGACATG-3′ at *TAF15* exon 1 and 5′-GGCATATCAAGCGCTG-3′ at *TCF12* exon 7, each of which
returned the same count at both depths. The other six did not. The three *EWSR1* exon-1 designs had
returned no near-match at all at the default ceiling and return 27, 29 and 84; 5′-GGGCATATCTCTATAA-3′
at *TCF12* exon 17 goes from 8 to 118 on either strand, and 5′-CAGGGCATATCTTGCA-3′ at *TCF12*
exon 9 from 7 to 67; and 5′-GCATATCAAGCGCTGC-3′ at *TCF12* exon 7, which had one near-match and none on the sense strand, returns 18 with two. Three of the six carry hits that span the catalytic gap and so are cleavage
risks rather than merely sense-strand matches: 64 for 5′-GCATATCCGTGGACGC-3′, 14 for
5′-GGGCATATCTCTATAA-3′ and 11 for 5′-CAGGGCATATCTTGCA-3′. A count of zero at the default ceiling
was not a count of zero, which is the sharpest form of the bound §5 sets out.

The deeper pass also decided what the default one could not. Seven of the 190 designs had failed at
the remote service and carried no count at all — a different seven from the seven §5 reports as
withheld by retention alone, which do carry default-depth counts; all seven returned at the deeper
ceiling, six of them dirty and one — 5′-GGGCATATCAAGCGCT-3′ at *TCF12* exon 7 — with three near-matches and none
on the sense strand. So the set of designs with a complete hit list and no sense-strand near-match is four
at this depth rather than three: a design the shallower pass never screened joins the three that
survived it. The deeper counts are reported as their own
measurement and no figure quoted above is restated from them.

The orientation call is corroborated independently of any of this. Ten designs return perfect
16/16 BLAST matches while the sense-only exhaustive scan reports no exact match. Both results can
only be correct if every one of those BLAST hits is on the minus strand, and every one is.

### 2.5 · The parents: liability in pre-mRNA and in mature transcript

RNase-H1 is active in the nucleus and gapmers engage pre-mRNA, so a screen over mature transcripts
cannot see intronic or intron–exon-spanning sites. That omission is not neutral in its direction. A
junction gapmer's two halves are both exonic, and in a parent pre-mRNA an exon is followed by an
intron rather than by the next exon. Parent pre-mRNA is therefore precisely where a design's donor
half sits beside sequence no mature screen has compared it against. A mature-only screen returns a
low count partly by construction.

Of the 190 designs, 53 have a near-match somewhere in parent pre-mRNA. Nineteen carry one that meets
all three conditions that would make it dangerous: it is on the sense strand, it pairs the catalytic gap in
full, and it touches intronic sequence. That third condition is what makes such a site invisible to
both transcript screens, rather than a re-count of something already reported.

The two liability classes are not disjoint designs, and the arithmetic has to be done as a union
rather than a sum. Thirteen of those 19 are already among the 87 that pair a mature parent through
the gap, so the pre-mRNA compartment adds six designs the mature screen misses entirely and the two
screens together condemn 93 of 190, not 106. What the compartment adds is therefore a liability class
invisible to every mature screen, not a second population of comparable size: the six are the number
that matters for a laboratory choosing among designs that already passed the mature-parent screen.

The step from 53 to 19 is a threshold rather than a measurement, and the class it removes is the one
the Methods (§6) decline to dismiss. Forty designs carry a sense-strand parent pre-mRNA site. The 19
counted here are those pairing the catalytic gap in full; the remaining 21 pair all of it but one or
two positions. Of their 28 sites, 26 are a single gap mismatch short, and five are in *NR4A3* itself.
Under the bounds this work adopts, a single mismatch inside the gap does not abolish cleavage, so
those 21 are not a null result. They are excluded because a graded count over this compartment would
need a discrimination model the literature does not supply for a parent duplex. The same condition
governs the mature-parent screen below, which considers only windows pairing the whole gap. Every
count in this section should be read as the fully-paired class, not as the whole parent liability.

Those 19 sites fall into two classes that do not mix, and only one is mechanistically interesting.
Nine are intron–exon-spanning, and every one is in *NR4A3* at the same place: six or seven
nucleotides into intron 2, spanning the boundary into exon 3. That follows from the design problem. A
junction gapmer's acceptor half is the 5′ end of *NR4A3* exon 3, and the wild-type *NR4A3* transcript
reaches that same exon across its own splice junction. So a design whose donor half also matches the
3′ end of intron 2, within the mismatch budget, pairs across the real splice site. That is a route to
wild-type *NR4A3* engagement which does not pass through the fusion at all, in the compartment where
RNase-H1 is active. It is the discrimination question this paper is about. The other ten are wholly
intronic and every one is in *TCF12*, which contributes 365,096 of the 517,157 intronic nucleotides
searched. That is 71% of the search space accounting for 100% of the class: volume alone predicts
about seven of the ten, so it accounts for most of the concentration and the remainder should not be
read as anything about *TCF12*.

The liability tracks the tiling register, of which the gap-level margin is a function. At margin 1,
12 of 76 designs carry a pre-mRNA site; at margin 2, 7 of 76; at margin 3, none of 38. Eight of the
nine *NR4A3* boundary sites are at the shortest donor-side register, which needs the fewest intronic
bases to match. None of the nine designs with no sense-strand near-match on either transcript screen
carries one.

The second class is in mature parent transcript, and it is larger. Each of the first three screens
misses it for its own reason. The alignment screen excludes parent records by design and filters at
≥14/16 identity. The exhaustive transcript scan admits only one mismatch. The pre-mRNA screen
searches unspliced sequence and so cannot reach a mature exon–exon junction. A parent duplex of 11
or 12 contiguous base pairs that pairs the whole catalytic gap is therefore invisible to all three,
while satisfying the duplex criterion adopted here — which §5 and §6 record as stated rather than
measured for this architecture.

Screen 4 compares every design's target window to every window of all six mature parents. 87 of 190
designs have a duplex of at least ten base pairs, and 61 of those 87 are against wild-type
*NR4A3*, the transcript this modality must spare. The count is a floor at the threshold chosen, and
seven base pairs is the shortest end of the same cited range (§6), and so the more inclusive reading of the liability: at seven the same screen returns
175 of 190 rather than 87. Those 61 are not 61 distinct sites: 59 of them are
the same one, the mature exon-2/exon-3 seam every design's acceptor half reaches, which is the
mature-transcript counterpart of the pre-mRNA concentration above. A sixty-second design pairs *NR4A3* at eleven base pairs but
another parent at twelve, so it is attributed elsewhere. The count falls steeply with the gap-level
margin: 50 of 76 designs at margin 1, 29 of 76 at margin 2, and 8 of 38 at margin 3. That is what the
margin's definition predicts, since at margin 1 a parent needs one lucky base to pair the whole gap
and at margin 3 it needs three. Five of the nine designs of §2.4 carry such a duplex at 11 or 12 base
pairs, including 5′-CAGGGCATATCTTGCA-3′ against wild-type *NR4A3* itself. The margin is therefore a
predictor of parent engagement rather than a guarantee against it, because it counts bases unique to
the fusion at the junction without asking whether a parent carries them elsewhere.

Eighty-seven of 190 is 45.8%, with a nominal binomial Wilson 95% interval of 38.9–52.9% — nominal
because it treats the 190 records as independent draws, which the close of this section states they
are not, so it is narrower than a junction-clustered interval on the same counts. A count of that
kind means little
without a null, so the same
screen was run over arbitrary 16-mers. Only the query changes: the same six mature parents, the same
forward orientation, the same ten-base-pair threshold. Scrambling each design's own target window,
which preserves its base composition and is the scrambled-gapmer control §4.4 asks a laboratory to
make, gives 6.2% (5.9–6.4%); a dinucleotide-preserving shuffle gives 10.0% (9.7–10.3%); 16-mers drawn
from uniform bases give 6.9% (6.7–7.2%), and from the panel's pooled base composition 7.2%
(6.9–7.4%). A calculation agrees with the sampled
figure rather than the sampled figure standing alone: the gap must pair, at 4⁻⁶, and the run must
then extend four further nucleotides across the two wings, at 1/64, which over the 19,921 parent
windows searched predicts 7.3%. The observed rate is about sixfold that, and the arm the modality
actually turns on separates further still: 32.1% of designs pair the gap against wild-type *NR4A3*
specifically, against 1.8% of scrambles. Scrambles are the weakest null run here; against the
random-offset chimera null of the next paragraph, that same arm separates 32.1% from 9.3%.

A second null asks whether that excess is a fact about reported breakpoints or merely about the
design rule. Joining a random window of a real donor parent to a random window of real *NR4A3*, split
at a junction offset the panel's registers use, reproduces everything the rule specifies, namely
donor sequence 5′, *NR4A3* sequence 3′ and the junction inside the catalytic gap, while destroying
only the fact that the two pieces meet where a tumour joins them. Those chimeras reach 23.8%
(23.3–24.2%).

That arm, however, destroys more than the breakpoint, and the excess over it should not be read as a
share attributable to where the disease joins the two genes. A real design's halves do not sit at
arbitrary interior positions: the donor half ends at an exon 3′ terminus and the *NR4A3* half begins
at an exon 5′ terminus, because that is what a splice junction is. Drawing both halves at real exon
termini of the same two transcripts — a syntactically valid exon–exon junction that no patient is
reported to carry — gives 40.6% (40.1–41.1%), against 45.8% observed, and 40.5% (40.0–41.0%) when the
*NR4A3* exon-3 acceptor that every junction tiled here uses is excluded from the draw altogether. The
observed rate's own interval contains both. The liability is therefore a property of joining two exon
termini of these two transcripts, and this panel does not resolve a residual specific to the reported
breakpoints.

The two termini do not contribute equally, and the asymmetry is the informative part. Requiring only
the donor half to end at a real exon terminus leaves the rate at 22.5% (22.1–23.0%), close to the
arbitrary-offset draw and far from the 40.6% both termini give; the whole of the difference appears when the *NR4A3* half is required
to begin at a real acceptor. What the screen is detecting tracks the acceptor boundary of wild-type
*NR4A3* — the transcript the modality exists to spare — rather than the donor consensus.
Two further arms locate it no more finely: holding the six
gap bases and scrambling the wings gives 9.1%, and the mirror gives 8.8%, because a run reaching ten
base pairs needs the real gap and the real flanks together. None of these rates is a significance
test and none is offered as one. The 190 records are 176 distinct molecules tiled at overlapping
registers across 38 junctions, so they are not independent draws, and a test treating them as 190
would be wrong about its own denominator.

### 2.6 · The *NR4A3* exon-2 acceptors, and the un-rearranged allele

Every junction above joins a donor exon to *NR4A3* exon 3, because the graded exon-pair atlas that
emits them (§2.1) drops
exon-2 acceptors as non-coding: *NR4A3* exon 2 lies upstream of the start codon, so a junction at
that acceptor cannot be built from the 38-junction panel at all. A frame-based exclusion is correct
for a fusion protein and does not transfer to an RNase-H mechanism, which cleaves a transcript
whether or not its reading frame survives, and the acceptors it excludes are not hypothetical: the
*EWSR1* type 2 transcript joins *EWSR1* exon 7 to *NR4A3* exon
2,<sup>24</sup><!--PMID:22567356--> sequenced as one of the five cases of a whole-transcriptome
cohort<sup>25</sup><!--PMID:29937513--> and again in an independent
patient,<sup>26</sup><!--PMID:35488288--> while functional work uses the *TAF15* exon 6 to *NR4A3*
intron 2 variant.<sup>27</sup><!--PMID:31020999-->

Those acceptors are now designed and screened to the panel's depth, at four seams with a published
exon-resolved breakpoint, each tiled by the same five registers and graded by the same five screens, and every count below is
at the tenfold deeper alignment ceiling — with one exception that is a limit of the instrument
rather than a property of the design. The pre-mRNA screen's parent set does not include *PGR*, whose
unspliced sequence the committed cache does not carry, so the *PGR* seam's zero in that compartment
is an absent reading of its own donor's introns rather than a clean one, and closing it needs a
networked re-fetch of the cache rather than a re-analysis.
Their best available designs are 5′-CAGTGGGCTTCTGCTG-3′ at *EWSR1* exon 7, the type 2 transcript, at
gap-level margin 2 and 51 gap-paired near-matches over 7 loci; 5′-AGTGGGCTCTCCACGG-3′ at *EWSR1*
exon 13, at margin 3 and 25 over 6; 5′-AGTGGGCTCTTGTGTG-3′ at *TAF15* exon 6, at margin 3 and 128
over 6; and 5′-AGTGGGCTCTTCCATT-3′ at *PGR* exon 2, a seam reported in a single
patient,<sup>28</sup><!--PMID:36103645--> at margin 3 and 51 over 14 (Table 5). None of the four is
clean. Each of these seams is tiled by five junction-spanning registers and no register at any of
them is clean either, so the least loaded of the four is the least dirty of its own seam's five
rather than a different kind of
result. They are reported beside the panel and never pooled into it, because the grade that excludes
their junctions from the 38 is unchanged. *PGR* carries a further caveat: it is a sixth partner,
outside the five modelled here, and §6 lists no transcript accession for it, so its design is
screened against the non-canonical-acceptor table rather than derived through the panel's own
transcript models.

**Some designs pair their whole catalytic gap against the patient's own un-rearranged *NR4A3* allele, and the parent screen passes
every one of them.** This is the result most consequential for anyone ordering these
oligonucleotides, and it applies wherever a design's acceptor half is *NR4A3* sequence that is not
exonic in the mature transcript: the 5′ untranslated exon 2, and the cryptic exon within intron 2. In
a fusion transcript that sequence follows the partner's donor exon; in the un-rearranged allele it
follows *NR4A3* intronic sequence, so the question is whether the design's donor half matches that
intron closely enough for the whole catalytic gap to pair. For three designs it does: at *EWSR1* exon
13 joined to *NR4A3* exon 2, 5′-CAGTGGGCTCTCCACG-3′ and 5′-GCAGTGGGCTCTCCAC-3′, each pairing across
the wild-type intron-1/exon-2 boundary at two mismatches with neither inside the gap; and at *TAF15*
exon 6 joined to the intron-2 cryptic exon, 5′-TGATGAGGGCCTTGTG-3′, likewise gap-paired at two
mismatches. All three are named here as not to be carried forward and are excluded from every
best-design field above. Both seams keep a reagent, 5′-AGTGGGCTCTCCACGG-3′ and
5′-ATGAGGGCCTTGTGTG-3′, the second's catalytic gap carrying three *TAF15*-derived bases the *NR4A3*
locus does not have and returning no wild-type site at all on the two screens that reach this seam.
That second reagent is not certifiable under the criterion §4.5 states, and §3 withdraws it on that
ground: its acceptor is a cryptic exon, which three of the five screens cannot address at all, so
what it holds is a quiet reading on two instruments rather than a clearance. What is lost is not a
seam but the assumption that designs tiled across one seam are interchangeable.

Two things about that finding matter more than the three sequences. The first is how they were
reached. Each had already cleared the mature-parent exclusion, and so had every other design at its
seam, that exclusion being a screen over spliced cDNA and structurally unable to see intronic
sequence: a clean parent screen at such a seam is the silence of an instrument that cannot look at
the compartment in question. The same three were returned independently by an exhaustive scan of the
*NR4A3* unspliced sequence, by the pre-mRNA screen and by the genome scan, on a fixed known-positive
control that fired on exactly the one design it was required to fire on. The second is what decides
it, because the obvious answer is wrong. It is not the gap-level margin this paper ranks by: the two
condemned *EWSR1* designs carry 2 and 1 donor bases inside the catalytic gap, while a design at the
same seam with a margin of 1 and five donor bases in its gap is clean. What decides is how much
donor sequence the gap holds, the rest being acceptor sequence the wild-type allele already carries
verbatim — a property of the donor rather than of the acceptor. The sequence bears it out: *EWSR1*
exon 13 ends
CACTCCGTGGAG against the last twelve nucleotides of *NR4A3* intron 1, CCTTGCCTGTAG, matching at 7 of
12 positions with a shared terminal AG, whereas *TAF15* exon 6 ends ACCACACACAAG and matches at 4,
mismatching in every register — which is why the *TAF15* exon-2 seam returns no such design and the
*EWSR1* exon-13 seam returns two. A design must therefore be checked against the acceptor gene's unspliced
sequence whenever its acceptor half is not exonic in the mature transcript, and no spliced-transcript
screen substitutes for it.

The *TAF15* intron-2 acceptor and a second cryptic-exon seam, *EWSR1* exon 10 to the same acceptor,
are designed but not comparably screened: three of the five instruments cannot address them at all,
resolving a junction by exon index where a cryptic exon 5′ of the *NR4A3* start codon has none, so
their counts are absent rather than low and must not be read beside the panel's. The pre-mRNA and
genome arms do reach them, and at the *TAF15* seam decide between its five designs rather than
ranking them.

### 2.7 · The surviving candidates, and a genome-wide check

Composing the mature-parent screen of §2.5 with the deeper re-screen of §2.4 leaves three of the four
designs that re-screen returns clean as candidates in the whole panel, and they are not equally
secure. The un-rearranged-allele exclusions of §2.6 remove none of them, because the seams they
condemn cannot be built from the 38-junction panel at all. 5′-AGGGCATATCGGAGTC-3′ at *FUS* exon
8 and 5′-GGGCATATCCGACATG-3′ at *TAF15* exon 1 carry no sense-strand near-match at ten times the
default search depth, no single-mismatch match on the exhaustive transcript scan, no pre-mRNA site
and no mature-parent duplex. Neither depends on the ten-base-pair threshold, because no window of
any parent pairs their catalytic gap at any length: their longest run is zero rather than merely
short. 5′-GGGCATATCAAGCGCT-3′ at *TCF12* exon 7 passes the same screens, but not in the same way.
Its longest parent run is eight base pairs against wild-type *NR4A3*, which is below the threshold
rather than absent, so it is a candidate at the stated cut and not at a stricter one. The fourth
design with a clean deep screen, 5′-GGCATATCAAGCGCTG-3′ at the same junction, is excluded by an
eleven-base-pair duplex with wild-type *TCF12* — its own donor parent, not the acceptor. That is the
honest size of the candidate set by screen, and it is not a set to make: no junction among them has
a published patient breakpoint, which is why §4.4 uses all three as mechanism controls rather than
candidates —
the exon-resolved *TAF15* breakpoints reported in EMC are exon 6, no *TCF12* breakpoint is reported
at exon 7, and for *FUS* none has been published at all. Selecting within each junction rather than
across the panel changes what is available, not what is clean: Table 2 applies the same criteria at
all 38, where 35 have a design that clears the parent screen and *TAF15* exon 14, *TCF12* exon 3
and *TFG* exon 2 have none.
All five junctions of the panel with a published exon-resolved breakpoint have one: four of them at
the top gap-level margin, with longest parent runs of eight, eight, nine and seven base pairs, and
*TFG* exon 7 at a margin of two with a longest parent run of nine.

Both classes were bounded the same way: exhaustive over six parent transcripts and silent about every
other gene. The genome scan, screen 5, removes that bound.

A raw genome-wide count is not a result at this threshold. Chance alone predicts of order 10³
near-matches per 16-mer over a genome for any 16-mer whatever, so the informative readings are
stratified. Exact 16/16 matches are the class where chance expectation is of order one: 1.37 expected
per design against 236 observed across 176 windows, which is at chance. Load relative to that
expectation separates designs where a total cannot — the median design sits at 0.98 of its
expectation and 14 of 176 exceed twice it. And the repeat split, free from a soft-masked reference,
shows 52.5% of hits fully repeat-masked against a genome that is 51.4% masked, so the load is not
repeat-driven.

The decisive reading is a lookup rather than a count: does any design have a gap-paired,
strand-agreeing site in *NR4A3*, in a parent gene, or in an *NR4A* paralogue anywhere in the genome?
Twenty of 176 do. No candidate above is among them, and the two secure at any parent-duplex
threshold carry a load well below chance — 0.33 and 0.24 of expectation at ≤2 mismatches,
ranking 26th and 13th of 176 on that axis, and 0.06 and 0.04 for gap-paired sites, ranking 5th and 1st. That is the strongest statement this work can
make about them, and it is a statement about predicted hybridisation and not about cleavage.

### 2.8 · Expression of the off-target loci

No screen above establishes that a design's off-target gene is transcribed in the organs a systemic dose reaches, and
that discount applies to every count in this paper. Read against reference expression data (Table
6), the gap-paired loci of the best design separate in the direction opposite to the sizes of their
loads at three of the four junctions covered. The fourth, *TCF12* exon 5, runs with its load rather
than against it: its reagent returns the second lightest load of the four, and its single locus,
*PIK3CG*, sits below the lower cut in all three exposure tissues. Table 6 lists every locus the
deeper screens return across the tiling registers read at a junction, so its rows are a union over
registers and can outnumber the per-reagent counts below, which are each best design's own. Its
record column counts gap-paired hits summed over every design read at that seam, one per hit, not
the number of transcript variants the locus is annotated with — a distinction the two extremes make
plain, since *NRP1*'s five records are one accession returned by five designs while *HNRNPA2B1*'s
hundred are fifty accessions returned by two. The *EWSR1* exon 12
reagent's six loci carry 123 of the 649 gap-paired hits returned across the four junctions of Table 6, and none of the four measurable
ones reaches the upper cut in liver or either kidney compartment; *ANKS1B* supplies 67 of them and
sits below the lower cut in all three, peaking instead in brain at 24.9 transcripts per million (TPM) in the Genotype-Tissue Expression
project's (GTEx) cervical spinal
cord, a whole-body reading carried in the released artefact rather than in either of Table 6's two
compartments, and *CHST5*, the smallest of the six by hit count, peaks in gut on the same
reading. The *EWSR1* exon 13 reagent's two loci are both transcribed at the upper cut in those same
compartments. The *TAF15* exon 6 reagent's five loci separate the other way: *NRP1* reaches 6.6 to
17.8 TPM across all three exposure tissues and is the only one all five of that junction's tiling
registers return, on five gap-paired hits to a single accession. It is at or above the upper cut in
two of those three, and robustness to register orders the loci differently again — though not
independently of the hit count, since a locus returned by more registers accrues more hits by
construction, and the two still do not order the loci together: *NRP1* leads on register robustness
and sits near the bottom on hits, its five records being one accession returned once per register;
the tumour-compartment proxy orders them a third way. What these readings can and cannot decide between two reagents is stated where
that choice is made (§4.1).

### 2.9 · Gap length trades junction specificity against parent-duplex competence

The panel above is one geometry. Tiling the same junctions at 5-8-5 and 5-10-5, wing fixed at five
nucleotides, resolves what a longer catalytic gap buys and what it costs (Table 7, Figure 3).

What a longer gap buys and what it costs are the same nucleotide. Inside the gap, the junction-unique
bases on the shorter side and the bases one wild-type parent pairs on the longer side are
complements: they sum to the gap. That holds for every design in all three panels rather than on
average, and it fixes the direction of both trades. Within one geometry the gap is fixed, so the two
move inversely: at 5-6-5 the 38 designs at margin 3 concede three nucleotides of contiguous
parent-paired gap DNA, the 76 at margin 2 concede four and the 76 at margin 1 concede five. What the
identity forbids is raising the margin past a geometry's ceiling, which is half its gap rounded down;
that takes a
longer gap, and a longer gap raises the parent-paired run at every register, the best-margin design
running from margin 3 conceding 3 nucleotides at 5-6-5 to margin 5 conceding 5 at 5-10-5. Lengthening
the gap therefore makes RNase-H1 more
competent against the fusion and against the parent together, and no register choice within a
geometry escapes that, though it does trade the two against each other.

Both directions are large. The best available gap-level margin rises from 3 to 4 to 5, and the
junction-spanning registers per junction from five to seven to nine. At the *EWSR1* exon 12, *TAF15* exon
11 and *FUS* exon 10 junction, the design carrying that margin sheds its transcriptome load completely:
123 sense-strand cleavage risks across the gap at six gene loci become 3 at one locus and then none.
Over the six junctions screened at every geometry, designs carrying no such risk rise from 8 of 30 to 28
of 42 to 54 of 54, and the most risk loci on any one design falls from seven to two to none.

Against that, the contiguous DNA a wild-type parent pairs at the same junction rises from 3 to 4 to 5
nucleotides, and the most stable parent duplex from −7.77 to −8.66 to −10.25 kcal/mol. The corpus
shows the same trade. Designs whose parent pairs at least five nucleotides of contiguous gap DNA, the
shorter of the two reported minima for RNase-H1, rise from 76 of 190 to 228 of 266 to 342 of 342, and
the median most stable parent duplex falls from −8.66 to −14.58 kcal/mol. At 5-10-5 that count is
every design, and necessarily so, since the larger half of a gap of ten cannot be under five. At
5-6-5, 114 of 190 designs keep the parent below it.

Part of the fall in near-matches is guaranteed by the instrument rather than measured. At a fixed
budget of two mismatches, every locus a longer design can reach is also reached by each of its own
shorter sub-windows, so the reachable set can only shrink as the design lengthens. Two mismatches is
also a fractionally stricter test at 20 nucleotides than at 16. Only the size of the fall, and which
designs reach zero, are measurements. The parent-side quantities carry no such qualification, being
computed from the junction rather than from a search.

Two liabilities the transcript screens do not reach appear to move the favourable way, and neither
reading survives one fixed criterion. A mature parent can pair
the whole gap for 181 of 190 designs at 5-6-5, 130 of 266 at 5-8-5 and 87 of 342 at 5-10-5, but the
whole gap is a six-nucleotide coincidence in the first and a ten-nucleotide one in the
last, so the three counts are not the same test. Held
to the ten-base-pair criterion applied everywhere else here, the
liability is flat: 87 of 190, 88 of 266 and 87 of 342, the two criteria coinciding at a gap of ten
because the gap alone is then already a ten-base-pair hybrid.
Designs pairing the gap in
parent pre-mRNA fall from 19 of 190 to 9 of 342, but that arm is a search at a fixed two-mismatch
budget and inherits the nesting bound above rather than the parent-side quantities' freedom from it.
Nor is the effect confined to the longest geometry:
5′-CAGGGCATATCAAGCGCT-3′ at *TCF12* exon 7 returns no near-match at all, where the 16-mer surviving
at that junction returns three.

### 2.10 · Duplex thermodynamics and conventional design rules

Scored as free energies, every one of the 190 designs favours the fusion duplex over the best duplex
either parent can form, by 4.8 to 13.1 kcal/mol with a median of 9.6. Every design favours the
fusion because a parent pairs roughly half the oligonucleotide, and half a duplex is much the weaker
one. That separates two things a base count conflates. Discrimination at the level of *binding* is
not marginal here, and is not what constrains the modality. What remains unresolved is
discrimination at the level of *catalysis*, where RNase-H1 requires a paired DNA gap and where the
literature bounds span one- to five-fold. The thermodynamic result therefore narrows the paper's
central uncertainty rather than relieving it.

The two rankings agree in direction. Grouping designs by the gap-level margin the Methods (§6) define,
the mean of that free-energy margin, written ΔΔG°37, rises monotonically with it, from 8.3
kcal/mol at margin 1 to 9.9 at margin 2 and 10.7 at margin 3. That agreement is arithmetic rather
than corroboration: the design's own seam hybrid — the run either
parent shares with it at the junction itself, which is not the screened parent duplex of §2.5 and is
not searched for anywhere else in the transcriptome — is exactly 11 minus the gap-level margin for all
190 designs, so the free energy is ordering that same length in kilocalories. What it adds is the
size of the difference; it is not purely a restatement of the margin, because composition reverses
the order in 19.9% of cross-margin design pairs and the margin-3 range sits inside the margin-1
range, and the same caution applies to the margin's agreement with the parent screens of §2.5.

Conventional design rules select differently, and against the paper's own candidates. Of the 190
designs, 106 satisfy all four rules; the rules bind at different rates, with every design free of a
G-quadruplex motif but 13 carrying a homopolymer run of four, 43 a CpG dinucleotide and 58 falling
outside the 40–60% GC window. The failures overlap, so they do not sum to the 84 designs that fail
at least one.

The disagreement is sharpest where it matters most. Of the nine designs with no sense-strand
near-match (Table 4), exactly one satisfies all four rules. Seven contain a CpG dinucleotide, the
canonical TLR9 immunostimulatory motif; four fall outside the 40–60% GC window — the three *EWSR1*
exon-1 designs above it at 62.5% and 5′-GGGCATATCTCTATAA-3′ below it at 37.5%. Only
5′-CAGGGCATATCTTGCA-3′ at *TCF12* exon 9 passes every rule, and the multi-partner candidate
5′-GGGCATATCATCAAAC-3′, which is not among the nine, also passes all four. The cleanest designs this
work found are, with one exception, molecules conventional triage would flag, in six of the seven
cases for a CpG that reaches into the catalytic gap, so the substitution that would remove it changes
one of the bases the gap-level margin is computed on. Both are reported rather than composed into a single
score.

## 3 · Discussion

Designability is not the constraint. Junction-spanning designs exist at every in-frame NR4A3
fusion junction, though at three of them every design pairs a wild-type parent through the catalytic
gap. Nor does specificity sort by partner. With all 38 junctions screened, four of the five partners
have a junction whose cleanest design carries no sense-strand near-match across the gap at the
deeper ceiling, and all five do at the default one. It is therefore the exon a fusion breaks at, not
the gene it breaks into, that predicts a clean design — and the count of clean junctions is itself a
function of search depth, as §5 sets out.

Clean designs are much scarcer than the default search depth implies, and two independent findings
converge on that. One is search depth, measured in §2.4 and bounded corpus-wide in §5. The other
is invisible to depth at any setting: five of the nine designs form an eleven- or twelve-base-pair
duplex with a mature wild-type parent that pairs the whole catalytic gap, one of them with *NR4A3*
itself, where no screen filtering on global identity can see it. Three designs survive every screen
applied here, two of them at any parent-duplex threshold (§2.7).

The limiting step is discrimination between the fusion and its parents, and it is not resolved here.
Both cited bounds are measured against a single substitution in an otherwise fully paired duplex.
Neither transfers to a parent that leaves half the oligonucleotide unpaired and the catalytic gap
only partly so: they bound the near-match case, and no retrieved measurement bounds the parent case.
The two parent compartments of §2.5 sharpen that rather than softening it. For nine designs the route
to wild-type *NR4A3* is not a gap-level discrimination problem at all. They pair the catalytic gap in
full across the wild-type intron-2/exon-3 boundary, at two mismatches that both fall in the locked-nucleic-acid (LNA) wing,
and the compartment in which that duplex would form is the nuclear one RNase-H1 occupies. For 87 the
same is true in mature parent sequence, over a contiguous duplex of at least ten base pairs. The general point is that a fusion-junction design's most
plausible wild-type liability is its own parent, reached either across a splice junction or in the
mature transcript, and both are invisible to a screen that ranks candidates by global identity. A
third compartment is invisible to all of them: at a seam whose acceptor half is not exonic in the
mature transcript, the patient's own un-rearranged *NR4A3* allele carries the same sequence behind an
intron, and three designs every parent screen passed pair their whole catalytic gap there (§2.6).
The four reports of parental sparing cited here were all made on molecules already
synthesised, and three of the four went further than cells: an shRNA to the *FGFR3* side of
*FGFR3::TACC3* improved survival in glioma-bearing
mice,<sup>13</sup><!--PMID:33241214--> a *PML::RARα*-specific siRNA prevented disease in NOD/SCID
mice,<sup>15</sup><!--PMID:21846246--> and liposomal siRNAs against *TMPRSS2::ERG* treated mice
bearing orthotopic and subcutaneous xenografts.<sup>16</sup><!--PMID:23052253--> Only the
fourth<sup>14</sup><!--PMID:36265509--> describes no in vivo model in its retrieved record. That
raises rather than lowers the bar the comparison above has to clear, and the point stands
unchanged: every one of those readouts required the molecule to exist first, and the comparison
above is available before anything is synthesised. Whether other groups apply an equivalent comparison before
synthesising is not established here: no survey of published design pipelines was performed, and the
argument above is about what particular instruments can see rather than about what the field
does. The null of §2.5 is what makes that a finding rather than a restatement of the design rule: arbitrary
sequence meets this screen at 6.2%, and a chimera keeping the whole rule while joining the two
parents at random offsets meets it at 23.8%, against 45.8% for designs at real breakpoints. That last
comparison overstates what is specific to the disease, and the stricter null says so: a chimera drawn
at real exon termini of the same two transcripts, at junctions no patient is reported to carry, meets
the screen at 40.6% — so most of the liability is what joining two exon termini of these genes gives,
and the excess at the reported breakpoints is not resolved at this panel's size (§2.5).

All of that presumes that sparing wild-type *NR4A3* is worth the specificity cost, and that premise
deserves examination rather than assumption. The published evidence cuts both ways and neither way
is decisive. On the permissive side, *NR4A3* has two close paralogues and the family is functionally
redundant where it has been tested: NR4A1 and NR4A3 are described as functionally redundant
suppressors of acute myeloid leukaemia, and the three receptors are highly
homologous.<sup>29,30</sup><!--PMID:29343483,25446259--> A conditional double knockout of *Nr4a1*
and *Nr4a3* disturbs haematopoietic stem-cell homeostasis, and even then the cells
retain regenerative and differentiation capacity;<sup>29</sup><!--PMID:29343483--> no single-knockout
arm is reported there, so the double deletion is shown to be sufficient and not to be necessary. On the
restrictive side, a separate study makes the loss of *NR4A3* consequential rather than silent when
paralogue reserve is reduced: mice hypoallelic across the two genes develop a myelodysplastic or
myeloproliferative neoplasm, and abrogation of both leads to rapid postnatal
leukaemia.<sup>31</sup><!--PMID:21205929--> The family is also not uniform in direction — within
atherosclerosis, NR4A1 and NR4A2 attenuate lesion formation while NR4A3 aggravates
it<sup>32</sup><!--PMID:24005216--> — so paralogue redundancy cannot be assumed to be
substitution.

Two limits on that reading matter more than the reading itself. Every source cited here is
haematopoietic or vascular, and none addresses the tissue an EMC arises in; two of the four are
reviews rather than primary reports; and the perturbation described throughout is germline or
conditional gene deletion, which is a different and more complete perturbation than
partial, reversible, dose-limited knockdown by an oligonucleotide. The honest position is therefore
that wild-type *NR4A3* knockdown has an unquantified cost that is probably not zero and probably not
catastrophic, and that the case for junction selectivity does not rest on it. It rests on the
*EWSR1* and *TAF15* side: the fusion's partner genes are essential RNA-binding proteins, and a
reagent cleaving a parent transcript is failing at the one thing that distinguishes this modality
from knocking down *NR4A3* directly, which requires no junction at all. A design that cannot spare
the parents has no advantage left to trade.

Free-energy calculation does not narrow the interval either. Every design discriminates amply at the
level of duplex formation, so what is unresolved is specifically the catalytic step, not the binding
one. Two things could narrow that interval, and no further sequence analysis is either of them: a
measurement, or a physics-based estimate of cleavage geometry on the RNase-H1·heteroduplex complex,
for which experimental structures exist. Neither is attempted here. Gap length is not a third, for
the arithmetic reason §2.9 gives: a longer gap buys a markedly quieter transcriptome by making
RNase-H1 more competent against the parent as well as against the fusion, which is the same limit
reached from the other side rather than a way around it. The field's own answer to poor single-base discrimination has been
positional chemical modification of the gap rather than
length,<sup>33</sup><!--PMID:23963702--> and that is the design direction this result points to, now
for a demonstrated reason rather than by analogy. A steric-block
mechanism, which does not require gap-level discrimination, is a second alternative this work does not
evaluate.

Delivery remains unsolved for a tumour, and separates into three routes with different
requirements. A characterised EMC-enriched surface antigen is a prerequisite of
the systemic receptor-targeted route only; local and inhaled administration require none. No such
antigen could be named when the question was put to the disease's own tissue: of the twelve candidate
surface antigens for which both a lineage reading against comparator sarcomas and a measured EMC
tumour-versus-normal-organ contrast exist — the latter from four EMC and 27 normal-organ libraries
across six organs in GEO deposit GSE28866 — none cleared both axes on every instrument that could
read it, and the three that cleared the two measured axes (*CD44*, *CSPG4*, *RET*) were refused by a
wider normal-tissue prior, or left ungraded by that prior's absence. That bounds what was examined
rather than establishing that no antigen exists: 86 of the 100 genes on the committed surface panel
carry no row in that deposit and are unmeasured rather than excluded, every reading is
transcript-level, and none of it speaks to protein, surface localisation, antigen density or
internalisation. Every reading in this paragraph is released as `aso-delivery-antigen.json`. For the
inhaled route, EMC's
distant spread is lung-dominant, at 35–45% of patients and a median of approximately 28 months to
metastasis.<sup>6</sup><!--PMID:41055792--> Inhaled oligonucleotides have reached human dosing in
non-oncology indications. An inhaled antisense oligonucleotide has been dosed in healthy volunteers
in phase 1,<sup>34</sup><!--PMID:39500647--> though that was a splice-switching oligonucleotide rather
than an RNase-H1-active gapmer, so it establishes the route and not the mechanism used here. An
inhaled siRNA has reached phase 2b–3 in patients.<sup>35</sup><!--PMID:40028836--> Both target airway
epithelium or parenchyma, which is the compartment inhalation naturally reaches. A hypocellular,
matrix-rich parenchymal sarcoma nodule is not. Inhaled delivery to lung tumours is an active
preclinical field, with 68 records in the retrieval corpus behind this section, but only two of those
carry clinical-stage language and neither is a trial. The route is therefore established in humans
and not for this target.

**The testable surface is narrower than the literature makes it look, and a reader planning an
experiment should know that before ordering anything.** A junction-spanning gapmer needs a junction to
span, so the test article has to carry one. The EMC line a reader
would reach for first, H-EMC-SS (RRID:CVCL_1238), is the only one this work could establish as available from a cell
repository, another reported line's distributor being unreadable and its availability therefore
unanswered rather than answered, and no *NR4A3* fusion is detectable in it on the public record: a
filtered fusion caller that ran against it — DepMap's filtered fusion
call set, release 24Q4, model ACH-001519 — returned two calls, `AL158209.1--NEBL` and
`VIM--RPS25`, neither naming *NR4A3* nor any FET gene; its *NR4A3* expression is 0.941 on a log2(TPM + 1) scale, near the floor in absolute terms while
sitting at the 83rd percentile of the 1,673-line panel, whose median is 0.214, so it is weak
corroboration and is graded as such, expression alone being able neither to establish nor to exclude
a fusion; the
reference registry that records a gene fusion for other EMC models
records none for this one; and no retrieved source reports a positive junction in it. The operative
consequence is narrow and is the only one this paper draws: no reagent named here can be tested in
that line. This is not a statement that the line is misidentified — it carries a short tandem repeat profile concordant across three independent sources at every locus
but one — D13S317, recorded as a single allele by one and as two by the other two — and no
problematic-line flag — nor a statement
about what the line is instead, and fusion-negative EMC tumours are
themselves a recognised minority category, so absence of the fusion is not by itself a
reclassification. The observation is also not new: it is in print in one figure legend and is carried
as a caution field in the reference registry. No retrieved source examines it as a subject, and it
is not discoverable by anyone searching on model validity. Both halves are released: the fusion-caller,
expression and registry readings in `emc-atr-vulnerability.json`, which owns them, and the reading of
that figure legend together with the reagent consequence in `emc-model-junction-evidence.json`.

What remains is five test articles, and each of the five now has a matching reagent. Three are the
engineered constructs of the functional study cited above,<sup>27</sup><!--PMID:31020999--> E-N,
T-N* and T-N, whose exon spans that paper states verbatim; two of the three, E-N and T-N*, carry the
same two junctions the reagents of §4.1 span — *EWSR1* exon 12 and *TAF15* exon 6, each joined to
*NR4A3* exon 3 — so both of those reagents have a stated test article; the third construct, T-N,
carries the intron-2 cryptic-exon seam of §2.6, whose reagent
cannot be certified under the criterion §4.5 states, three of the five screens being unable to
address a cryptic-exon acceptor at all. The other two
are the patient-derived, identity-clean models reported with two EMC
tumours,<sup>36</sup><!--PMID:36316541--> USZ20-EMC1 (RRID:CVCL_C6MX) and USZ22-EMC2
(RRID:CVCL_C6MY), whose fusions are reported as *EWSR1* exon 13 and *TAF15*
exon 6 joined to *NR4A3* exon 2 rather than exon 3; reagents exist at both acceptors, so each line
has one under either reading of that exon label.

The two routes are not interchangeable and their limits run in opposite directions. Rebuilding the
constructs is the faster route and the only one whose critical path contains no laboratory that has
to answer an email, since the junction is specified by construction. It is not unconditioned: the
published recipient background is a catalogue item supplied under a material transfer agreement, and
every plasmid carrying the published retroviral backbone that could be read here is distributed to
academic institutions and non-profits only, a restriction that binds before any price does. What it cannot buy is
biological relevance: a complementary DNA over-expressed in a heterologous background is not the
disease, so such an experiment could speak to junction-selective knockdown of the intended
transcript and not to activity at endogenous expression from an endogenous locus. The published
recipient background is in no cell-line registry either, so a rebuild would sit in a different
background from the original — an isogenic mismatch to declare rather than gloss. The
patient-derived models are the only route to a fusion-positive EMC cell, and are available on
request from the originating laboratory with no repository deposit; what a transfer requires is
stated nowhere that could be read, which is an absent statement rather than an absence of
conditions, and the cells are slow once received, at reported doubling times of five to six days as
sarco-spheres passaged every two to three weeks, which constrains any exposure window. A third
reported line cannot serve as a test article at all on current evidence, because its fusion partner
and exons are unstated anywhere readable and it would have to be sequenced first. One constraint
sits above all of them and no reagent choice moves it: every route ends at someone culturing cells,
and this work has no laboratory, so the rate-limiting step is a laboratory rather than a line, a
construct or an oligonucleotide.

One deliverable does not wait on that. No named reagent reaches every patient, and the released
design and screening pipeline is the paper's second output: §4.5 states what it takes as input, what
it does with it and what its result is worth, which is a candidate rather than a validated reagent.

## 4 · Reagents, controls and the falsification experiment

This section is the paper's output for a laboratory. It names six things: the oligonucleotides to
make, the arm that separates the two ways a weak result could arise, the predicted off-target load
each carries, the controls without which the readout does not mean what it appears to mean, the
number that would falsify, at its top margin, the ranking every candidate here is ordered by, and — for the patients no
named reagent reaches — the released procedure by which a candidate can be designed for a breakpoint
outside this panel. Nothing in it is a claim of efficacy. No sequence named below has been
synthesised or tested.

### 4.1 · The reagents to synthesise, and their population coverage

The experiment that would resolve the central uncertainty has been published in an
analogous disease. Fusion-specific antisense oligonucleotides against *NAB2::STAT6* in solitary
fibrous tumour, evaluated against CRISPR-engineered isogenic fusion-positive and fusion-negative
cells, reduced fusion expression by 58% and proliferation by 22% in
vitro.<sup>37</sup><!--PMID:37370737-->

**Research use only.** Both sequences named in the next paragraph, and every sequence in Tables 2
and 5, are research reagents for laboratory investigation only. Neither is a medicine or a candidate
drug, neither has been synthesised or tested, and neither may be administered to any human being or
animal or supplied to anyone for that purpose. Ordering either from a commercial synthesis service
is possible for anyone; doing so does not make it a treatment, and nothing in this section should be
read as licensing use in a patient.

Applied here, the reagents to synthesise are the best available at the two most frequently reported
junctions with a published exon-resolved breakpoint (Table 2): 5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 and
5′-GGGCATATCTTGTGTG-3′ at *TAF15* exon 6. Both hold the top gap-level margin of 3, and neither pairs
a parent through the catalytic gap at the ten-base-pair threshold, although the *TAF15* reagent's
longest parent run is nine. The first also tests the multi-partner prediction, against a synthetic
target only.

How much of the disease those two junctions represent is a junction figure, not a partner figure, and
the two differ: 46 *EWSR1* and 9 *TAF15* among 58 molecularly confirmed cases is 94.8% between the
partners,<sup>9</sup><!--PMID:36948401--> while each reagent spans one exon pair. Discounted by the
breakpoint distribution of an 18-case series<sup>22</sup><!--PMID:12378528--> the two are 68.4%,
roughly two thirds; Table 5 gives that figure, the rungs above it and the reagent at each.

What that figure is, and what it is not, has to be said in terms, because the arithmetic is easy to
read as a result. **It is not a coverage measurement.** No patient was screened with either
sequence, and a sequence that matches a reported junction is not thereby active against a tumour
carrying it, so the number prices which published junctions the two reagents address and nothing
about what they would do in a patient. It is also not a pooled proportion: the two cohorts are
combined multiplicatively, a partner prevalence times a conditional within-partner fraction, which
is a composition the repository's pooling policy does not reach. Four bounds sit on it, and they run
in different directions. The interval is wide for the denominators rather than the estimate: taking
each breakpoint fraction to its own Wilson bound spans 39.9% to 82.8%, the *EWSR1* arm resting on 15
tumours and the *TAF15* arm on three. **That interval propagates the breakpoint fractions only.** The
partner shares are held at their point estimates, and their own Wilson intervals are 67.2–87.7% for
*EWSR1* and 8.4–26.9% for *TAF15*, so an interval that varied all four quantities would be wider
than the one reported. The third decimal is not resolved by the data behind it: the *TAF15* arm is
three tumours out of three, so one tumour breaking elsewhere moves the total by about 5.2 percentage
points, which is why the plain-language reading is roughly two thirds and why nothing here should be
compared at one-tenth of a point. And the denominator has a denominator: every figure in this
paragraph is a fraction of *molecularly confirmed* EMC, while what fraction of EMC reaches molecular
confirmation at all is stated by no source retrieved here, so the population these percentages
describe is a tested population and not the disease. It assumes too that the breakpoint distribution
within *EWSR1*-rearranged tumours is the same in the 58-case cohort as in the 18-case one, 21 years
apart, which nothing here tests and which no published series is large enough to settle. Breakpoint
sequencing of archival material would sharpen it; no further analysis of sequence will.

Two things sit outside the table. Coverage rises only by adding reagents, because no oligonucleotide
can serve two breakpoints of the same partner: *EWSR1* exon 12 ending AATGGTTTGATG against exon 13's
CACTCCGTGGAG, which agree over a single terminal base. Taken across every pair of in-frame junctions
of one partner in this panel, the longest shared 3′ donor run is five nucleotides, at *TFG* exons 2
and 6, and three within *EWSR1*. The cross-partner coverage of §2.2 is the exception that shows the
rule, needing the ten identical donor bases the FET paralogues share. And the *NR4A3* exon-2
acceptor rows of §2.6 sit in Table 5 without entering the panel's own counts.

Two further reagents extend the set, both at the top gap-level margin of 3: 5′-GGGCATATCTCCACGG-3′ at
*EWSR1* exon 13 to *NR4A3* exon 3, and 5′-GGGCATATCCATCAGA-3′ at *TCF12* exon 5 to *NR4A3* exon 3,
whose junction is resolved to the nucleotide by the deposited chimeric cDNA of §2.3. The second comes
with no distribution: one *TCF12*-rearranged tumour has ever been sequenced at this junction, neither
breakpoint series contains a *TCF12* tumour at all, and the break-apart assay the later cohorts used
locates no seam within the *NR4A3* locus, so recurrence there is untested rather than refuted. The
98.3% above these reagents is an upper bound rather than a reachable target for two reasons and not
one: that *TCF12* arm is priced at its ceiling, worth 3.4 percentage points, and the figure also
assumes every remaining *EWSR1* breakpoint covered, which is the larger of the two steps at 15.9
points and needs three further reagents the retrieved record does not resolve to an exon (Table 5).
One fact about the screened set is invisible in the ladder, which prices rungs rather than counting
seams: every junction with a published exon-resolved breakpoint in the retrieved record now carries
a screened design, the five in this panel (§2.7) and the four *NR4A3* exon-2 acceptor seams reported
beside it (§2.6). Eight of those nine designs are taken through all five screens. The ninth, at the
*PGR* seam, is graded on four of them, because the pre-mRNA screen's parent set does not carry that
donor's unspliced sequence, so its pre-mRNA compartment is unmeasured rather than clean for the
reason §2.6 gives. That is a statement about how far the screening reached
and not a coverage figure, and it displaces nothing above it: how many patients a reagent set
reaches is the ladder's question, priced on the single series behind it. The Supplementary
Information (SI) §S6 carries the rest
of the ladder's bookkeeping — the count of those seams, a second basis that prices them on the whole
retrieved breakpoint record, and the two that move the figure by exactly zero.

The *EWSR1* exon-13 reagent should not be recommended on its transcriptome count, because the two
axes that separate it from the exon-12 reagent point in opposite directions and only one of them
bears on where an effect would land. On count it is the lighter of the two, 24 gap-paired
near-matches at 2 loci against 123 at 6. On exposure it is the heavier: both of its loci are
transcribed at the upper cut in the organs a systemic phosphorothioate gapmer distributes to, where
none of the exon-12 reagent's measurable loci is (§2.8, Table 6). For a laboratory choosing between
them, the exposure reading is the one that speaks to the question a count cannot: a locus matched
but not transcribed in the organs a systemic dose reaches has no route to an effect, whereas the count says only how
many gap-paired windows the screen returned there. Neither axis is a risk ranking, and this comparison
does not make the exon-12 reagent the safer molecule. Every hit behind both is a 14 of 16 match, no
cleavage is predicted at any of them, and an expressed gene is necessary and not sufficient for an
effect. The reason to make the exon-13 reagent is coverage, and it is unaffected by either axis.

Two risks attach, in this order. The first is architectural, and the Methods (§6) disclose it. A
six-nucleotide gap supports noteworthy but incomplete RNase-H1 activity where seven to ten are
reported as optimal,<sup>38</sup><!--PMID:24981949--> so weak knockdown is at least as likely to be
the gap as the sequence. That risk is now addressable by a named second reagent rather than by a
caveat.

### 4.2 · A second geometry as a gap-length control

5′-AGGGCATATCATCAAACC-3′ is the 5-8-5 design at the same *EWSR1* exon 12 junction. It spans the same
three partners' breakpoints and sits inside the reported activity optimum. It holds a gap-level
margin of 4 where the 16-mer holds 3, and carries 3 sense-strand near-matches across the gap at one
gene locus, against the 16-mer's 123 at six (§2.9, Table 7).

Synthesised alongside the 16-mer, at one extra oligonucleotide and one extra well per condition, it
separates the two explanations a weak result would otherwise confound. A 5-8-5 arm that knocks down
where the 5-6-5 arm does not attributes the failure to gap length rather than to sequence. What it
does not buy is parental sparing, since the same two nucleotides lengthen each parent's contiguous
duplex from 3 to 4 nucleotides of gap DNA, its whole contiguous hybrid at that seam from 8 to 9 base
pairs, and its free energy from −7.77 to −8.66 kcal/mol. Its longest mature-parent duplex through the
whole gap does fall from 8 base pairs to none, but 8 sits below the ten-base-pair threshold applied
throughout, so neither design counted as a mature-parent liability at this seam and that fall removes
nothing the screens had counted. Both arms therefore need
the fusion-negative comparator below.

### 4.3 · The predicted off-target load of each reagent

The second risk is transcriptome load, and it differs sharply between the two reagents. The *EWSR1*
reagent carries the heavier load of the two named here: 123 gap-paired
sense-strand near-matches at the deeper ceiling, recounting to six gene loci, all at the screen's
loosest admitted identity and none on a parent transcript (§5). It is not the heaviest in the
panel — fourteen of the 187 design records re-screened at that ceiling carry more, to a maximum of
240 at *TCF12* exon 3. Table 3 prints one row per junction rather than one per design record, so
those per-record counts are in the released screens rather than in a table. The *TAF15* reagent
carries 8 such near-matches at five loci.

The parent compartments qualify that, in a way the transcript screens cannot show. The *EWSR1*
reagent carries a sense-strand intron–exon-spanning near-match in wild-type *TAF15* pre-mRNA at two
mismatches, one of them inside the catalytic gap, returned independently by the pre-mRNA screen and
the genome scan. It falls outside every parent count reported here, because those require the gap to
be paired in full, and by the bounds adopted above a single gap mismatch does not abolish cleavage.
It is the multi-partner result's own cost rather than an incidental hit: the ten donor bases shared
across *EWSR1*, *TAF15* and *FUS* that let one oligonucleotide span three junctions are the bases that
place it against wild-type *TAF15*. The *TAF15* exon-6 reagent carries no sense-strand pre-mRNA site
at all, which is a second respect in which the two separate on something other than count.

That load should travel with the reagent. It is a liability to disclose and to control for rather
than a disqualification, because on the genome scan the same design falls below chance in both
directions that matter: 0.69 times the expected number of near-matches at two mismatches, and 0.62
times the expected number of gap-paired ones. Expression separates the two reagents the other way
(§2.8, Table 6): none of the *EWSR1* reagent's measurable loci is expressed at the upper cut in the
organs a systemic dose reaches, while the *TAF15* reagent's five include *NRP1*, which is. That does
not reverse the ranking, since no screen here establishes that a two-mismatch duplex engages any of
them, and it is not a statement about safety.

### 4.4 · Controls and the decision threshold

The three designs that survive every screen are mechanism controls rather than candidates:
5′-AGGGCATATCGGAGTC-3′ at *FUS* exon 8, 5′-GGGCATATCCGACATG-3′ at *TAF15* exon 1 and
5′-GGGCATATCAAGCGCT-3′ at *TCF12* exon 7, tiered as §2.7 describes. None sits at a junction a patient
is reported to carry (§2.7), which is what makes them controls rather than
candidates. 5′-GGGCATATCTCTATAA-3′ at *TCF12* exon 17, which the default-depth screen returns as
clean (Table 4), is not among them. At ten times the default search
depth it carries 101 sense-strand near-matches, 14 of them spanning the catalytic gap.

What a knockdown experiment with these reagents can transfer to depends on how it is set up, and the
first requirement is upstream of the assay. The breakpoint of the cell line or patient sample must
be established at nucleotide resolution by RNA sequencing before any oligonucleotide is ordered:
every design here is specific to one exon pair, and none is valid for an unverified junction.
Routine diagnosis does not supply it: break-apart *NR4A3* fluorescence in situ hybridisation is the
preferred single assay because it detects any rearrangement "irrespective of
partner",<sup>6</sup><!--PMID:41055792--> so on its own it does not locate the seam, and the 58-case
cohort every coverage figure here is denominated on was identified that way, with RNA exome
sequencing applied to three of its cases.<sup>9</sup><!--PMID:36948401--> That cohort reports a
partner for 57 of its 58 tumours, so partner assignment there rests on more than the break-apart
assay; what no part of that workflow supplies is the exon pair.

Three assay controls are required, and a knockdown assay alone distinguishes none of them:

- a positive control gapmer against an abundant housekeeping transcript in the same cells, to
  separate failed delivery from failed discrimination;
- a scrambled gapmer of matched chemistry, to separate sequence-specific cleavage from the
  non-specific toxicity of this chemistry — and the scramble actually ordered must itself be put
  through the mature-parent screen before it is made, because on this paper's own null 6.2% of
  scrambles pair a parent's whole catalytic gap at the ten-base-pair criterion and 1.8% do so
  against wild-type *NR4A3* (§2.5), which is the one transcript a control must not engage;
- a fusion-negative isogenic comparator, since wild-type *NR4A3* may be too weakly expressed in an
  EMC line for the selectivity readout to be defined at all.

Two limits of that set are invisible within it. The normalising reference transcript must be neither
the positive control's target nor either transcript measured, or the positive-control well becomes
uninterpretable and every other well is rescaled against a perturbed reference. And none of the
three assay controls separates RNase-H1-dependent cleavage from steric block, which §3 names as
unevaluated, so a knockdown seen with this set is consistent with both while the ranking under test
models cleavage alone.

Where the wild-type measurement sits decides the answer, because the fusion carries *NR4A3* exons 3
to 8 and a wild-type assay must not read sequence the fusion also carries. The two available
placements bias in opposite directions. An amplicon upstream of the acceptor cannot detect
the fusion, but it lies on the 5′ fragment that survives cleavage, so it under-reads wild-type
knockdown and inflates apparent selectivity; an amplicon spanning the wild-type exon-2/exon-3
boundary reads knockdown directly, but at the *NR4A3* exon-2 acceptors of §2.6 the fusion itself
carries that boundary. Both are defensible, no assay is prescribed here, and which placement was used
should be reported with the result.

The decision threshold should be fixed before
the experiment, in a form that can be registered. Selectivity is the wild-type *NR4A3* half-maximal
knockdown concentration divided by the fusion's, from a matched dose–response in the same wells, so
that a larger number is a more selective reagent. The cut is defined for that quantity and no other, and what that leaves out has to be said, because
it is the half of the argument §3 rests the modality on. Wild-type *NR4A3* is the acceptor parent;
no donor parent is read by this ratio, and neither is any other gene. So a reagent can clear the cut
while pairing a parent transcript through its whole catalytic gap — the case §2.7 excludes a fourth
*TCF12* design for, at eleven base pairs against its own donor — and each reagent of §4.1 carries
its longest mature-parent duplex against a gene this ratio does not read (§4.3, Table 5). The remedy
is not a second cut. No retrieved measurement bounds the parent case (§3), so a threshold on a donor
ratio would be a number with nothing behind it, where this one at least has a stated convention. It
is a reporting requirement instead: wild-type transcript for the reagent's own donor parent and for
the parent carrying its longest duplex,
measured in the same wells on the same dose–response, reported beside the ratio and against no cut —
the requirement the margin-contrast arm below already carries, stated for every arm rather than for
that one. A design whose donor knockdown tracks its fusion knockdown has lost what §3 says the
modality exists to buy, whatever the registered number reads.
A ratio of residual transcript at a single dose is not commensurate with it and must not be compared
against the same cut: that ratio is bounded above by one divided by the fusion knockdown's
complement, so at the 58% knockdown reported for the analogous published
experiment<sup>37</sup><!--PMID:37370737--> it cannot exceed about 2.4 however selective the reagent
is, and a cut of 5 would return falsification as arithmetic rather than as biology.

The replicate count follows from the variance rather than being asserted. Selectivity here compounds
four normalised measurements, so the replicate standard deviation of its logarithm is the quantity to
estimate in a pilot, and that standard deviation — taken across independent biological replicates of
the same matched dose–response, in the same wells, at the wild-type placement declared with it — is
the one thing the pilot has to return. Neither the pilot's replicate count nor its test article is
fixed here, for the same reason no assay is: both are properties of a platform this section leaves
open, and the replicate count is the quantity the pilot exists to decide rather than one it can be
given. What is fixed is the scale, because a standard deviation taken on the ratio rather than on
its logarithm is not the quantity the figures below are stated for.

At a standard deviation of 0.35 on that scale, six independent biological
replicates give about 80% power to falsify a true selectivity of 3, and three give about 30%; above a
standard deviation of about 0.65 no observed ratio at or above one can place a 95% upper bound below
5 at three replicates, so the test can fail only where the reagent is anti-selective and the design
is otherwise void — a design whose test cannot fail, which is a different outcome from one that
fails to falsify — rather than negative. The number of
replicates should therefore be set from the pilot estimate, with three as a floor and not a target.
That makes the pilot a gate as well as a sizing step, and its rule follows from the figures above
without needing a further one: a pilot returning a standard deviation at or above the void figure
has shown that the floor cannot falsify at this cut, so the decision at that point is a larger
replicate count or no falsification test at all, and never three.
The ranking is falsified only where the upper bound of the 95% confidence interval lies below the
cut, never where a point estimate does. The ratio is reportable only where the wild-type *NR4A3*
knockdown is itself resolved above a pre-stated limit of quantification — the quantity that can
approach zero, which is the change in wild-type transcript and not its vehicle-well abundance; a
wild-type change indistinguishable from none returns an unbounded selectivity that would otherwise
pass by default, and the honest output there is a one-sided lower bound, which cannot falsify. The cut is 5.0, taken as a convention from the approximately
five-fold near-match figure of §6 rather than measured for this comparison, on which §3 records that
no retrieved measurement bounds the parent case. It sits at the optimistic end of the one- to
five-fold span reported above, so a reading inside that span is consistent both with the ranking
failing and with the discrimination this chemistry is already reported to give; the margin contrast
below is what separates those two, and a single-arm result does not.

One property of that cut belongs to no single experiment. The rule is stated per reagent and the
claim it tests is not: the ranking is one claim, §4.5 releases a procedure that generates reagents
against it without limit, and any one reagent falsifying is read as falsifying the ranking. The
family over which an error rate would have to be controlled is therefore open-ended, which is why no
correction is imposed — a multiplicity adjustment needs a family size fixed in advance, and this
one is fixed by how many laboratories run the procedure. Two consequences follow and both belong
with any result. A falsification carries the full weight of its confidence statement for the first
reagent tested against this cut and less for each one after it, so how many reagents have been
tested against it, and in what order, is part of the result rather than context for it. And nothing
corrects in the other direction either: a reagent that clears the cut among many has not thereby
been shown to discriminate, only not to have falsified.

The reagents of §4.1 all hold gap-level margin 3, so as a set they measure the level of selectivity at
the top margin rather than whether selectivity orders by margin. One optional arm supplies that
contrast, and only at *EWSR1* exon 12: 5′-GCATATCATCAAACCA-3′ is the margin-1 register of the same
junction at the same geometry. Margin is not the only variable that moves with the register, and the
others are named here rather than left for a reader to find: GC falls from 43.8% to 37.5%, outside
the 40–60% window §2.10 audits, so this arm would fail a conventional rule the lead reagent passes;
gap-paired near-matches fall from 123 to 34 while single-mismatch off-targets rise from 1 to 22; and
its longest mature-parent duplex is eight base pairs against wild-type *FUS*, which is the same
length the lead reagent carries against wild-type *TFG*, so the two do not separate on that screen
at all. A difference between the arms is therefore not attributable to margin alone.

One asymmetry decides what the arm can show. Its five parent-paired gap nucleotides are *EWSR1*, the
donor, not *NR4A3* — so the liability its low margin creates is invisible to a readout defined on
wild-type *NR4A3*, and interpreting this arm requires the wild-type *EWSR1* measurement alongside it.
The mirror register at the same seam, 5′-CAGGGCATATCATCAA-3′, is the one whose five fall on *NR4A3*,
and it carries an eleven-base-pair duplex against wild-type *NR4A3* that would confound it differently.

*TAF15* exon 6 cannot supply the same arm: all four of its lower-margin registers pair a parent
through the whole gap at eleven or twelve base pairs, two of them against wild-type *NR4A3*. A
contrast at one junction tests the ordering at that seam and not the ranking across the panel, and
the comparison it supports is between two arms rather than of one ratio against the cut, for which
this section states no rule.

### 4.5 · A design procedure for a breakpoint outside this panel

The reagents named above do not reach every patient: the two leads cover roughly two thirds of
molecularly confirmed cases, and the panel is bounded by what has been sequenced rather than by what
can be designed. The deliverable is therefore the procedure as well as the reagents, and it is the
procedure that produced this paper's 190 designs, released unchanged with the artefacts.

Its input is the breakpoint at nucleotide resolution, by RNA sequencing of the tumour, which §4.4
requires in any case; an exon pair inferred from a break-apart assay is not sufficient. Given a
declared exon pair, `junction_aso.py` retrieves the parent transcripts, builds the modelled fusion,
grades the pair for frame and tiles the junction-spanning gapmers, emitting each with its GC, its
gap-level margin and a check that it complements neither parent perfectly. The five screens then run
on that panel: `junction_aso_offtarget.py` the alignment
screen against human RefSeq RNA, classifying each near-match by whether the catalytic gap is paired;
`aso_insilico.py` the exhaustive transcript scan, the target-site accessibility fold and the
sequence-liability filters; `aso_premrna_offtarget.py` the parents' unspliced sequence;
`aso_parent_gap_pairing.py` the mature-parent screen; and `aso_genome_offtarget.py` every position of
GRCh38. A new design must clear all five, and the parent screens matter most: pairing a parent
through the whole catalytic gap is this paper's central negative and surrenders the only advantage
the modality has. Where the acceptor half is not exonic in the mature transcript, the
un-rearranged-allele scan of §2.6 applies as well, and it lives in two further modules rather than in
a step within the five screens: `aso_taf15_intron2_designs.py` holds the single implementation of that scan,
which grades a design cleavage-competent on the un-rearranged allele when it pairs the unspliced
*NR4A3* sequence with no mismatch inside the catalytic gap, and `aso_noncoding_acceptor_designs.py`
calls that same implementation at the exon-2 acceptor, where the register runs across the
intron-1/exon-2 boundary instead of within intron 2.

What that yields is a candidate, not a validated reagent. Nothing designed this way has been
synthesised or tested, the procedure has been run at the junctions reported here and at no others,
and a design it returns is ordered by the ranking §4.4 states a falsification threshold for.

## 5 · Bounds on every claim, and the conditions for falsification

The conditions for falsification this heading names are stated with the experiment that would test
the ranking (§4.4); what this section adds are the bounds under which any such test would be read.
Seven of them sit under everything above, ordered by how much a decision would change if one of them
bit. None alters the ranking by gap-level margin; each alters what a count taken from it means. The
block that closes the section is not one of them: it records a released artefact that had no reading
to give.

**Counts are lower bounds, and a zero is not exempt.** The alignment screen is heuristic and stores
at most 50 hits per query, so 136 of the 183 filtered designs carry right-censored counts: 35 at the
cap, 101 more past the 15 hits retained. Re-screening at ten times the ceiling raised the count for
164 of the 180 designs screened at both depths, 129 of which had never approached the cap, so
reaching the cap is not what censors a count. Truncation is not the mechanism: of the 47 designs whose
default hit list the pipeline records as complete, 37 returned more at the deeper ceiling and none
returned fewer. One reporting 9 near-matches returned 34, one reporting 10 returned 110, and one
reporting exactly the 15 hits retained — a list the pipeline marks uncensored — returned 204, with a
second at that same boundary returning 374. Depth then moves the headline result: six of the nine
clean designs lose the property at the deeper ceiling, three having returned no near-match at all at
the default one (§2.4). Only those 47 of the 183 hit lists are short enough to assess for cleanliness, so
nine is a floor over that subset and an over-count of it at once, and their own raw counts, zero to
eight hits each, are not a measurement either. Retention alone withheld a verdict on seven further
records — a different seven from the seven whose default-depth query failed at the remote service
(§2.4) — and the deeper pass decided six of the seven; none of the six is clean, and the seventh
re-screen did not return, so that record remains undecided. The nine are untouched by that test.
BLAST's sensitivity at ≥14/16 is unquantified here, so "no sense-strand near-match" is a property of this search and not of the
transcriptome; the exhaustive transcript scan, complete for substitutions by construction, is the
screen the claim rests on.

**The parent threshold is stated, not measured.** Every parent count — 87 of 190, 61 of them against
wild-type *NR4A3* — is taken at a contiguous duplex of ten base pairs, a criterion adopted here
rather than measured for this architecture, so the count is a floor at that choice: at the
seven-base-pair end of the same cited range the screen returns 175 of 190. Nor does the criterion
transfer cleanly, ten being a whole-duplex length where the source counts RNA:DNA nucleotides, which
this architecture holds at six (§6). The threshold also sets how much of the liability the nulls
account for, and at ten they account for nearly all of it: the exon-terminus chimera reaches 40.6%
against 45.8% observed, so no share is attributed here to the reported breakpoints themselves (§2.5).

**The patient may not carry these junctions.** Which exon pair a patient carries is not decidable
from exon structure. The coverage figure of §4.1 is arithmetic over two published cohorts and not a
measurement of anything — no patient was screened with any sequence named here, and §4.1 sets out
the four bounds on it. It prices *TAF15* at 3 of 3 on a three-tumour series, while a functional
study reports a second isoform at a cryptic exon within *NR4A3* intron 2 and calls the two "the two
major *TAF15*-*NR4A3* isoforms detected in human tumors" without counting
either,<sup>27</sup><!--PMID:31020999--> so that arm's coverage is an upper bound and 68.4% is
optimistic on it by an unmeasured amount; no design in the 38-junction panel crosses that seam (0 of
190; the designs §2.6 reports at it sit outside the panel), and the
two isoforms share no sequence 3′ of the breakpoint, so it is a different target and not a near-miss.
The
multi-partner result is conditional on *TAF15* and *FUS* breaking at the homologous exons, which is
not established here, and the five partners are not the catalogue:
*ACTB*<sup>3</sup><!--PMID:41755350--> and others are reported, and 2% of one cohort carried no
identified partner.<sup>9</sup><!--PMID:36948401--> Three of the 15 *EWSR1*-rearranged tumours of the
primary breakpoint series carry transcript types the retrieved record does not name, so retrieval is
an upper bound on what would open that block. At least one named variant is reported to arise from a
genomic breakpoint interior to *EWSR1* exon 12 rather than between two exons, in a source that
carries a citation marker on that sentence and is therefore restating an earlier
report.<sup>39</sup><!--PMID:9060841--> Such a breakpoint is not undesignable: handing the same
builder a donor model cut inside its exon returns five candidates, all fusion-specific against both
parents, three gap-centred and a best gap-level margin of 3. What such a junction lacks is an exon
index, which is how every design here is specified, and a published nucleotide position, which no
retrieved source states, so it is out of reach for a stocked panel while remaining designable for a
named patient whose breakpoint has been sequenced. How many tumours this accounts for is not
established by any source.

**One geometry.** Every screened count outside §2.9 is for one architecture, a 16-mer at 5-6-5. The
genome scan is unavailable at 18 and 20 nucleotides by construction rather than merely unrun, so the
nesting bound on a longer design's genome liability is a next step and not a result, and no RNase-H1
assay distinguishes these geometries here.

**Hybridisation, not cleavage, and not exposure.** All five screens address hybridisation-dependent
liability only, and the free-energy calculation speaks to duplex formation rather than to cleavage.
Every parent count requires the catalytic gap paired in full, an inclusion criterion adopted because
no retrieved measurement grades a partly-paired parent duplex; the class it excludes is the 21
designs of §2.5. Nothing here establishes that a matched gene is transcribed in the organs a systemic dose reaches: 13
of the 46 loci returned no reading and carry 52 of those 649 hits, so there the exposure
question is unanswered rather than answered negatively, and reference bulk medians describe a population's normal tissue rather than a dosed
patient's organ (Table 6). The sequence-independent liabilities of this chemistry, protein binding
and target-independent hepatotoxicity, are not a function of any feature graded here.

**The chance null is crude.** It assumes independent uniform bases, where real transcript sequence is
composition-skewed and repetitive. An arbitrary position matches a given 16-mer at ≥14/16 with
probability 2.6 × 10⁻⁷, or 189 near-matches for any 16-mer whatever over the exhaustive scan's
measured span — a figure the alignment screen's 50-hit cap cannot test at all. The scan itself can,
and on the mean it comes in at chance: at ≤1 mismatch the same span predicts 8.2 per design against
an observed 9.2 over the 176 distinct oligonucleotides, a ratio of 1.12. The shape disagrees in both
tails, 40 of the 176 returning no match where a Poisson null of that mean predicts fewer than one,
and a right tail reaching 100 matches on one design (Supplementary Figure S1), so the null separates
"more than chance" from "at chance" and nothing finer and does not license reading the zeros as
cleanliness.

**Records are not genes, and one assembly is not a genome.** RefSeq carries one accession per
annotated variant, so a match to a constitutive exon is counted once per variant: over the 44 designs
of the 38 junction screens whose hit lists permit a locus recount the median inflation is 2.25
records per locus and the maximum 11.0, more than doubling the apparent number of distinct genes.
Where a load sits matters as much as its size: `NM_`/`NR_`
records are curated, `XM_`/`XR_` computationally predicted. Both compound on
5′-GGGCATATCATCAAAC-3′, whose 123 gap-paired near-matches at the deeper ceiling recount to six loci:
82 of the 123 are predicted models and the other 41 are curated records, and those 41 are themselves
inflated, 32 of them *ANKS1B* accessions and three *ZNF667*. The curated share moves with depth as
well. At the default ceiling that design carried a single curated sense-strand hit, *H2AP* (NM_012274),
mismatched inside the catalytic gap and so counted in full under the pessimistic bound; at the deeper
ceiling it carries 43 curated sense-strand hits, 41 of them gap-paired. The genome scan decides
sense-strand membership against an annotation, so unannotated transcription is uncounted; it is one
assembly, silent on a patient's private variation; and every exhaustive screen here is complete for
substitutions by construction and blind to insertions and deletions.

**An earlier genome-wide attempt is released, is uninterpretable, and is not screen 5.** Before the
exhaustive scan was built, one genome-wide query per design was run against a public mixed corpus of
assemblies, genomic clones, patent sequence and transcripts rather than against a genome reference.
Its output is released with the artefacts, as `aso-premrna-offtarget-genomic.json`, so that nobody
repeats it. It could not have yielded an interpretable number under any outcome, for two structural
reasons. That corpus has no defined nucleotide span, so no chance expectation can be formed against
it, and at this threshold an off-target count that cannot be referenced to chance is not a reading
at all. And its retrieval ceiling sat far below what chance alone predicts, so every query that
returned came back at the ceiling: of nine designs queried, one failed at the remote service, seven
returned exactly 50 records and the eighth 52.

The per-design rows in that file therefore look like off-target findings and are none. Of its 402
retained rows, six are exact 16-of-16 matches, four of them to genomic clone records and two to
annotation records on chromosome 6, and 55 are immunoglobulin variable-region records,
every one of them at 14 or fewer of 16. A corpus of this kind carries one stretch of sequence once
per record that contains it, so those rows are largely redundant copies of one another, and there is
no denominator against which to say whether any of them is more than arithmetic. No count, ratio,
load or cleanliness statement in this paper is taken from that file. Nor does it bear on screen 5,
which is a different object that shares the word
genome-wide: screen 5 is the exhaustive GRCh38 scan of §2.7 and §6, whose denominator is measured at
3.10 × 10⁹ nucleotides, whose expectations are computed from that denominator, and which caps
nothing at scan time. The earlier attempt is retained as the record of an instrument that had no
reading to give, and it should be read as nothing else.

## 6 · Methods

**Transcript models.** Canonical transcripts for the five partner genes and for *NR4A3* were obtained
from Ensembl.<sup>40</sup><!--PMID:39656687--> Each model was self-checked before use: exon lengths must sum to the spliced cDNA, the
coding sequence (CDS) must occur exactly once within it, and translation of the CDS must
reproduce the annotated protein. Per-exon coding content was additionally cross-checked against an independent exon audit for
*EWSR1* and *NR4A3*; for the other four partners that audit does not exist, and the weaker check is
recorded per gene in the released artefacts. Every exon number, coordinate and length in this paper
is relative to one specific model per gene, and the canonical transcript of a gene can change between
Ensembl releases, so the six accessions are given here rather than left to the artefacts:
ENST00000397938 (*EWSR1*), ENST00000605844 (*TAF15*), ENST00000333725 (*TCF12*), ENST00000254108
(*FUS*), ENST00000240851 (*TFG*) and ENST00000395097 (*NR4A3*).

**Chimera construction.** Chimeras were built from transcript sequence rather than by joining coding
sequences. A fusion keeps the whole *NR4A3* acceptor exon, so any bases of that exon lying ahead of
the *NR4A3* start codon are still present in the fusion transcript, and they are the first bases an
oligonucleotide meets on the *NR4A3* side of the junction. At the exon-3 acceptor, the only one that
yields designs here, there are two. Joining coding sequences alone would omit them, shifting every
design by two positions. A pair of exons is *in frame* when the partner's coding bases, plus those
retained bases, sum to a multiple of three. Every declared exon pair was graded by that rule before
any design was emitted, and only the in-frame pairs were carried forward, since only those describe a
fusion that could exist.

**Design.** Junction-spanning 16-mer gapmers were tiled in a 5-6-5 LNA/DNA/LNA architecture on a
phosphorothioate backbone, which is the chemistry the design rules below assume. Each way of sliding
that 16-mer along the transcript is a *register*, and only registers placing the junction inside the
six-nucleotide DNA gap were retained, since RNase-H1 cleaves within the DNA:RNA duplex of the gap and
needs a minimum run of contiguous DNA to do so.

The gap length is a compromise and is treated as one. Reported minima for that run are five to six
nucleotides — at least five for cleavage to occur,<sup>41</sup><!--PMID:39126066--> or a DNA segment
of "six or more bases" to activate the enzyme<sup>42</sup><!--PMID:41614678--> — and for LNA/DNA/LNA
gapmers specifically a six-nucleotide gap gives noteworthy but incomplete activity, with seven to ten
reported as optimal.<sup>38</sup><!--PMID:24981949--> None of the three figures is a titration in
this architecture, and SI §S3 gives the provenance of each. Six therefore sits at the short end of the
usable range and below the reported optimum. It was retained because it admits exactly five
junction-spanning registers per junction. No claim is made that a short gap improves
fusion-versus-parent discrimination: one series that shortened a 5-10-5 gapmer to 5-6-5 reported
lower off-target knockdown but also lower on-target activity and lower allele
selectivity.<sup>41</sup><!--PMID:39126066--> Within that same series 5-8-5 was the one shortened
design reported to give a small increase in activity or allele selectivity in some cases, and it also
increased off-target knockdown relative to 5-10-5 for several of the genes tested, so the exception
is not a free one. Those gapmers carry thiomorpholino rather than LNA wings and are directed at a
single-nucleotide polymorphism distinguishing two alleles rather than at a fusion junction, so
neither the rule nor its exception is evidence about gap length in this architecture. Because that
trade is the modality's central one,
5-8-5 and 5-10-5 were tiled over the same junctions by the same rule and carried through the same
screens, wings held at five nucleotides so that only the gap changed and LNA affinity enters every
parent duplex identically (§2.9).

**Ranking.** What separates the fusion from a parent is the junction-unique bases inside the gap, not
identity across the whole oligonucleotide, because the gap is where the enzyme cuts. Designs were
therefore ranked by their *gap-level margin*: the junction-unique bases inside the gap on the shorter
side of the junction. That is the panel-level statistic, which compares designs across junctions.
Selecting within one junction is a different question, and Table 2 — from which the reagents of §4.1
are taken — orders designs by parent liability first, then pre-mRNA sites, then distinct gene loci,
with the margin breaking ties. Each candidate was screened against all six parent transcripts rather
than the two of its own fusion, because the FET-family donors (FUS, EWSR1 and TAF15) are paralogues
with similar low-complexity amino-termini.

**Specificity screening.** Five screens were applied. Each is named below and referred to by that
name throughout, because each reaches a compartment the others cannot and each is blind to something
another catches. No single screen supports any claim here on its own.

1. **The alignment screen.** Each target window was queried against human RefSeq
   RNA<sup>43</sup><!--PMID:26553804--> with BLAST+<sup>44</sup><!--PMID:20003500--> (blastn-short,
   low-complexity filter off, ≥14/16 identity). A transcript window matching a design at 14 or more
   of its 16 positions is a *near-match*, classified by whether the six-nucleotide gap is itself
   base-paired: one that pairs the gap is *gap-paired*, or gap-spanning, and RNase-H1 could cleave
   there; one pairing only the wings could not. This is a heuristic search retaining only a limited
   number of hits per query, so every count it yields is a lower bound — an effect §5 measures. Records of the six parent genes are counted
   separately and excluded from every near-match count reported here, since each parent pairs one
   wing by construction and would otherwise dominate the list; the parents are assessed instead by
   the gap-level margin and by screen 4.

2. **The exhaustive transcript scan.** A seed-and-extend scan searched 186,185 transcripts
   (GRCh38.p14) for exact and ≤1-mismatch matches. It is complete for substitutions by construction,
   reads the sense orientation only, and does not detect insertions or deletions.

3. **The pre-mRNA screen.** Screens 1 and 2 search mature transcript, so a third covers the nuclear
   compartment they cannot reach. Unspliced sequence and exon coordinates for all six parents were
   retrieved from Ensembl, and every target window was scanned against them in both orientations at
   ≤2 mismatches. That is the threshold the alignment screen admits, which keeps the two comparable:
   a stricter one here would return a cleaner pre-mRNA result for that reason alone. This arm is
   exhaustive for substitutions, seeded on three blocks of the 16-mer so that a hit within the
   threshold must match one block exactly. Each hit is classified as wholly intronic, wholly exonic,
   or spanning an intron–exon boundary, since only the exonic class could have been visible to a
   transcript screen.

4. **The mature-parent screen.** This addresses the parent transcripts screen 1 excludes, in the
   compartment screen 3 cannot reach. Mature parent transcripts were spliced from the same Ensembl
   records, and every target window was compared to every 16-nucleotide window of all six, forward
   orientation only. A window counts only if all six gap positions are paired. Its size is the
   longest contiguous run of perfect pairing containing the whole gap, which is the duplex RNase-H1
   would see. Runs shorter than ten base pairs are not treated as plausible substrates. That is a
   stated threshold, not a measured one, so every design's longest run is released. Ten is the strict
   end of a figure its source gives as a possible explanation of its own observation — "this could be
   because RNase H1 requires a minimum length of 7 to 10 RNA:DNA hybridized nucleotides to bind with
   its hybrid binding domain" — rather than as a measured
   minimum.<sup>45</sup><!--PMID:35664704--> The qualifier does
   not transfer cleanly: the run counted here is the whole contiguous duplex, of which exactly six
   nucleotides are the RNA:DNA pairs of the gap and the rest are LNA:RNA wing pairs the source's
   wording would not count. Ten here is therefore a total-duplex length, while the source's 7 to 10
   is a count of RNA:DNA nucleotides that this architecture holds at six in every design, below the
   range the source states; what relation the one criterion bears to the other is not established
   here. The count it produces is a floor at that choice, and what the choice costs is stated beside
   the count in §2.5.

   **The null for this screen.** Bounded by six transcripts, this screen has no chance expectation of
   its own, and a count against six transcripts is not interpretable without one. Six ensembles of
   arbitrary 16-mers were therefore pushed through the identical screen, 200 draws per design in
   each: each design's target window shuffled to preserve base composition; shuffled to preserve
   dinucleotide composition by an Eulerian-path shuffle; drawn from uniform bases; drawn from the
   panel's pooled base composition; and two arms holding either the catalytic gap or the wings fixed
   while shuffling the other. A seventh is structural rather than a chance null: a random window of a
   real donor parent joined to a random window of real *NR4A3* at one of the junction offsets the
   panel's own registers use, which keeps the whole design rule and randomises only where in each
   transcript the two pieces come from. Three further structural arms, on the same 200 draws per design, hold the exon boundaries fixed
   as well, because a real design's halves do not sit at arbitrary interior positions: the donor
   half ends at an exon 3′ terminus and the acceptor half begins at an exon 5′ terminus. Exon
   boundaries were taken in mature coordinates by cumulative exon length from the same committed
   record the transcripts are spliced from, and the first and last boundaries of each transcript
   were excluded, being its ends rather than splice sites. The arms are: the donor half drawn to
   end at a real donor exon terminus with the acceptor half left at a uniform interior window; both
   halves drawn at real exon termini; and the same with the *NR4A3* exon-3 acceptor that every
   junction tiled here uses excluded from the draw altogether, so that arm cannot sample the
   disease's own acceptor even by chance. §2.5 reports all three. Proportions carry Wilson 95% intervals. The pseudo-random
   stream is written out in the released code rather than taken from the interpreter's own, so the
   artefact is reproducible bit for bit. §2.5 reports the result.

5. **The genome scan.** Screens 1 to 4 are bounded either by an annotation or by six transcripts.
   The fifth removes that bound. Every distinct target window and its reverse complement was tested
   against every position of GRCh38 in both orientations at ≤2 mismatches, exhaustively:
   2,948,609,696 windows over a measured 3.10 × 10⁹ nucleotides, with no seed, no word size and
   therefore no search sensitivity to quantify. §2.7 reports it.

**Strand orientation.** A match matters only if an antisense oligonucleotide could base-pair with it,
which means the sense strand; a window carrying the reverse complement is not a liability at all.
`blastn` searches both strands, so such a hit passes an identity filter unless orientation is parsed,
and screens produced before that parsing was added recorded them as cleavage risks. Orientation is
now parsed and filtered in all 38 junction
screens and the 183 designs they hold, and therefore in every cleanliness statement made here. Only
two released screens are unfiltered, and neither carries a junction from the 38-junction panel or supports a claim here (SI
§S5). The same rule governs pre-mRNA, which is transcribed in transcript orientation: a forward match can be
base-paired and a reverse-complement match cannot.

A design is called clean where it carries no sense-strand near-match, and that is always a
statement about a complete hit list at a stated search depth. Both qualifications matter. A hit list
the cap truncated is not complete, so no verdict is available for that design, and a design clean at
one depth need not be clean at another. §2.4 and §5 report both effects.

**Target-site accessibility.** Estimated as mean unpaired probability over a local fold of up to 180
nucleotides, computed with the ViennaRNA partition function,<sup>46</sup><!--PMID:22115189--> and
spanning 0.160 to 0.707 across all 190 designs at real exon junctions with a median of 0.477. It is
released with the artefacts and ranks nothing here. That omission is deliberate — accessibility bears
on potency, which is not claimed for any sequence, rather than on the discrimination this work is
about — and SI §S1 gives the three reasons in full.

**Expression of the off-target loci.** No screen above says whether a matched gene is transcribed
in the organs a systemic dose reaches. For four of the five junctions with a published exon-resolved breakpoint — those
Table 6 covers — the gene loci their deeper screens return in the gap-paired class were read against
GTEx v8 median TPM.<sup>47</sup><!--PMID:32913098--> No such reading was taken at *TFG* exon 7, so
that junction carries no expression reading rather than a negative one. The readings are in two
blocks, reported separately and never combined, against two cuts used for legibility rather than as
thresholds of concern: a lower cut of 1 TPM, below which a reading is taken as below detection, and
an upper cut of 10 TPM. The first block is liver and both kidney compartments, the organs a
systemically dosed phosphorothioate gapmer distributes to — a premise taken from the chemistry, for
which no measurement or citation was retrieved here; the second is six soft-tissue types,
standing in for the compartment EMC arises in, since no atlas contains the tumour itself. NCBI Gene
supplied locus identity, so a locus with no reading is attributed rather than left blank, and the
Human Protein Atlas<sup>48</sup><!--PMID:25613900--> was read as a transport check only, its
consensus incorporating GTEx rather than confirming it independently.

**Discrimination model.** The binary assumption that any mismatch inside the gap abolishes cleavage
is not supported by the primary literature and is not used for any claim of cleanliness. The field's
general figure for single-nucleotide discrimination by a gapmer carrying no positional modification
in its gap is approximately five-fold,<sup>33</sup><!--PMID:23963702--> and at 16-mer length one
study reports no efficient discrimination at all.<sup>49</sup><!--PMID:7567450--> Both are measured
against a single-nucleotide substitution rather than a fusion junction, and the pessimistic one used
unmodified antisense DNA, so they are used here as bounds for unmodified chemistry rather than as a
property of this architecture. Gapmer-specific work points the same way, which is why the bounds are
not narrowed: across more than 120 gapmers spanning five single-nucleotide changes, only two or three
achieved preferential cleavage of the mutant allele in cells,<sup>50</sup><!--PMID:28970564--> and
where allele selectivity is achieved it is engineered by modifying a gap position to block cleavage
of the near-match rather than obtained from the mismatch itself.<sup>51</sup><!--PMID:42327837-->

Every screen that resolves the gap was therefore re-scored under both bounds as a graded residual
cleavage load, holding the hit set fixed so that only the scoring changed: all 38 junction screens,
and 39 of the 93 screens released in total (SI §S4). Two distinct bounds follow, and they run in
opposite directions. Where a hit list is truncated, the strand of the remainder is unrecoverable, so
some designs keep a strand-blind count; that over-counts liability, because it includes matches no
antisense oligonucleotide can hybridise, and is an upper bound. The same truncation also means fewer
hits are recorded than the search returned, so the count of hits is itself right-censored: a lower
bound on how many exist. Each design records which bounds apply to it.

**Duplex thermodynamics.** A base count is a proxy for discrimination, and a free energy is the
field's standard instrument for it, so each design was also scored thermodynamically. A junction
gapmer is a perfect complement of the fusion across all 16 positions, while a parent transcript can
pair only the half of the oligonucleotide it contributes. The comparison is therefore the full 16-mer
duplex against the donor-side and acceptor-side runs alone. Nearest-neighbour enthalpies and
entropies for a DNA:RNA hybrid were taken from Sugimoto and colleagues,<sup>52</sup><!--PMID:7545436-->
and ΔG°37 computed as ΔH° − TΔS°. The arithmetic was checked against an independent implementation,
which agreed exactly; that check verifies the summation and not the choice of strand, and the strand
concentration it uses enters no reported free energy (SI §S2).

These designs carry LNA wings and the table is for an unmodified hybrid, so what is computed is the
duplex the DNA backbone would form. Because the junction lies inside the gap, each parent pairs one
of the two five-nucleotide LNA wings while the fusion pairs both, so LNA should widen this margin
rather than narrow it and every reported value is a conservative floor. That direction follows from
the architecture and was not computed: no LNA parameters were applied.

**Conventional design rules.** Every design was separately audited against four conventional
antisense design rules: GC within 40–60%, no G-quadruplex motif, no homopolymer run of four, and no
CpG dinucleotide. The audit is not there to grade the designs, but to ask whether conventional triage
and the gap-level margin would select the same molecules.

**Sequences.** **Do not order an oligonucleotide by copying it out of this PDF.** Every sequence
named here travels with the archive as `fusion-junction-aso-sequences.csv` and
`fusion-junction-aso-sequences.fasta`, which are the canonical record: they are generated from the
same artefacts as the tables, they carry each design's geometry, junction and gap-level margin, and
they flag the three designs §2.6 names as not to be carried forward. A typeset table cell is not a
machine-readable record — whether a sequence and the column beside it stay separate on extraction is
a property of the reader's software — and the sequences here are 16 to 20 bases in which a single
substitution changes what the molecule does. The bases alone are also not the reagent: the geometry
column denotes locked-nucleic-acid wings around a DNA gap on a phosphorothioate backbone (§6), and
unmodified DNA of the same sequence is a different molecule about which nothing reported here holds.

**Availability.** All code, graded artefacts and per-design tables are released under a single
archived version, deposited from the public repository at `github.com/trimcrae/Rare-cancers`
[ARCHIVE DOI — PLACEHOLDER, AUTHOR TO SUPPLY BEFORE DEPOSIT: the archive has not been deposited and
no digital object identifier has been reserved, so this citation does not yet resolve]. Every result
reported here is re-derived from the committed artefacts in that archive
without network access or credentials. That claim is meant to be checked rather than accepted:
`./scripts/regenerate_aso_chain.sh` re-derives every offline-derivable artefact in dependency order
and re-runs the consistency, citation and style gates in about half a minute on four cores with no
network, and the archive is current if it reports `ASO CHAIN OK` and leaves the working tree
unchanged. The guard suite behind it, `PREFLIGHT_FULL=1 ./scripts/preflight.sh`, contains the tests
that re-derive each reported number from its artefact and fail if the two diverge, and takes about
seven minutes on the same machine with `pytest-xdist` installed, or roughly four times that
single-threaded. Regenerating the specificity screens from scratch is not
offline, because the alignment screen queries NCBI BLAST and the exhaustive transcript scan downloads
the GRCh38.p14 RefSeq RNA set, but no reported number requires it: each screen's hit set is archived
and the re-scores hold it fixed. The pre-mRNA and mature-parent screens are fully offline against the
archive, since the retrieved unspliced sequence and exon coordinates travel with it.

## Tables

Tables 1 to 7 are in `fusion-junction-aso-submission-tables.md`, generated from the released
artefacts so that a cell and its source cannot diverge. Sections numbered SI §S1 to §S6 above are in
`fusion-junction-aso-supplementary-information.md`, which carries the method detail a reader does not
need in order to re-derive a design or re-run a screen, and the coverage ladder's second basis.

## Figure legends

Figures 1 to 3 are the main-text figures. Supplementary Figure S1 is printed here with them and
travels with the archive; the Supplementary Information carries no figure of its own. The two
S-numbered series are independent and both start at S1: Supplementary Figure S1 is the single
supplementary figure, and SI §S1 to §S6 are the numbered sections of the Supplementary Information.
Neither is a cross-reference to the other.

**Figure 1. Reading-frame compatibility across the NR4A3 fusion junction space.** All 231 donor-exon ×
acceptor-exon pairs across *EWSR1*, *TAF15*, *TCF12*, *FUS* and *TFG*, graded against the frame
condition.
Rows are donor exons grouped by partner; columns are *NR4A3* acceptor exons. Two acceptor columns
are refused in every pair for structural reasons, so the 38 in-frame junctions lie in a
single column.

**Figure 2. One 16-mer spans three partners' breakpoints.** The junction windows of *EWSR1* exon
12, *TAF15* exon 11 and *FUS* exon 10 joined to *NR4A3* exon 3, aligned at the breakpoint. Blue,
donor exon; green, acceptor exon; positions at which the three donors differ are boxed as well as
coloured, for greyscale and colour-blind readers. The shaded box is
the target window of 5′-GGGCATATCATCAAAC-3′, with the 5-6-5 locked-nucleic-acid (LNA)/DNA/LNA gapmer architecture below it and its
gap-level margin of three alongside. The three donors are the FET family — *FUS*, *EWSR1* and *TAF15* — and they are identical over
the ten nucleotides before the breakpoint, which is what makes one oligonucleotide
junction-spanning at all three junctions.
Coverage is predicted from sequence and has not been measured.

**Figure 3. The margin a longer catalytic gap wins is the parent duplex it concedes.** (A) The
best-margin design at *EWSR1* exon 12 joined to *NR4A3* exon 3, drawn at 5-6-5, 5-8-5 and 5-10-5
with the wings held at five nucleotides. Every base inside the catalytic gap comes from the donor
exon or from the acceptor exon, so the junction-unique bases on the shorter side and the bases one
wild-type parent pairs on the longer side tile the gap and sum to it. (B) Every fusion-specific
design in all three geometries, 798 over 38 junctions, plotted as gap-level margin against the
contiguous run of gap DNA a wild-type parent can pair. Marker area is the number of designs at that
point and the label is that count; the three lines are drawn from the identity, not fitted, and it
holds for each design individually rather than on average. Within one geometry the two move
inversely along a line of slope −1; a geometry's ceiling on margin is half its gap rounded down, and
clearing it means a longer gap and a higher parent-paired run at every register (§2.9, Table 7).

**Supplementary Figure S1. Transcriptome load per design against chance expectation.** Each bar is one distinct
oligonucleotide's count of exact plus ≤1-mismatch matches over 186,185 transcripts, ranked. The 190
design records at real exon junctions collapse to 176 molecules, because nine of the 16-mers are
junction-spanning at more than one partner's junction at once — five at three junctions and four at two — and
each of those is one physical oligonucleotide, plotted once rather than repeatedly (marked). The line
is the number of such matches expected for an arbitrary 16-mer under an independent-uniform-base
null, 8.2, computed against the scan's measured 718,571,139-nucleotide span;
118 of the 176 fall at or below it and 58 exceed it. Ten further designs from
modelled breakpoints not built from a spliced transcript model are excluded, and are released with
the artefacts. It is an expected count: the observed mean is 9.2, a ratio of 1.12, while the
median is 3, so real transcript sequence produces a long right tail the null cannot
rather than a uniform shift away from it. The line
separates "more than chance" from "at chance" and is not a significance test; the counts are
predictions from sequence search, not measured off-target activity.

## Declarations

**Research use only, and not for administration to any person or animal.** Every oligonucleotide
sequence in this manuscript, its Supplementary Information and its tables — the two reagents named for
synthesis, the three named as not to be used, the second-geometry and scrambled controls, and every
design in the released panel — is a research reagent intended solely for laboratory investigation.
None is a medicine, an investigational medicinal product or a candidate drug. None has been
synthesised, formulated, tested in any cell, tissue or animal, or evaluated for potency, purity,
stability, immunogenicity or toxicity by anyone. None may be administered to any human being or
animal, compounded or formulated for such use, or supplied to any person for such use, and nothing
in this manuscript should be read as recommending, authorising or enabling that. Custom
oligonucleotide synthesis is commercially available, so the sequences here are orderable by anyone;
that is a fact about the supply chain and not a statement about what they are fit for. A person with
extraskeletal myxoid chondrosarcoma seeking treatment should be directed to a clinical trial or a
sarcoma centre.

**Supplementary Information.** The sections cited above as SI §S1 to §S6 are in
`fusion-junction-aso-supplementary-information.md`, deposited as a separate file beside this
manuscript and included in the archive below.

**Data and code availability.** [ARCHIVE DOI — PLACEHOLDER, AUTHOR TO SUPPLY BEFORE DEPOSIT: no
digital object identifier has been reserved and this citation does not yet resolve], deposited from
`github.com/trimcrae/Rare-cancers`.
A manifest listing every archived file with its SHA-256 travels with the deposit. Artefacts include the graded junction
atlas, per-junction design panels, all five screens, the per-junction reagent table behind Table 2,
the graded re-scores under
both discrimination bounds, and the retrieval records for every literature claim.

**Provenance and corrections.** An earlier version of these analyses placed the acceptor junction
incorrectly through a coding-versus-transcript exon indexing error and was withdrawn in full; all
panels were rebuilt and verified against two independent transcript acquisitions. The complete
correction record, including every superseded value, is released with the archive.

Because that is the failure a reader will reasonably assume could recur, the two instruments the
paper's conclusions rest on were reimplemented a second time and the two implementations compared.
The reimplementation shares no code with the original and differs from it on four axes: it splices
each mature transcript out of the genomic record rather than reading the cDNA record; it locates each
gene's coding start by open-reading-frame search rather than by reading the annotated 5′ untranslated
length, which is the class of value the retracted error turned on; it grades the reading frame by
arithmetic on exon coding-length vectors rather than by translating the chimera; and it computes the
mature-parent screen by substring search over the design's gap-containing substrings rather than by
scanning every parent window and extending outward from the gap. The two agree on all 231 graded exon
pairs, field by field and not only on the grade, and on the longest parent duplex of all 190 designs,
giving the same 87 and the same 61 against *NR4A3*. The two transcript acquisitions agree base for
base for all six genes, and the annotation-free coding start reproduces the annotated one for all
six. Both implementations, the comparison and its deliberate-corruption tests are in the archive.

Two things that check should not be read as. It is not external review: the same author prepared
both implementations. And it bounds implementation error only — two implementations of a
specification that is itself wrong will agree with each other and both be wrong, so agreement here is
not evidence that the longest contiguous run containing the catalytic gap is the right quantity to
compute. Independent review of the code by another group remains wanted and is not claimed.

**Competing interests.** The author declares no financial competing interests: he holds no
position, equity, consultancy or patent relating to any gene, sequence or agent named here, and no
oligonucleotide described in this manuscript has been synthesised, licensed or offered for sale. One
non-financial interest is declared: the author is a survivor of extraskeletal myxoid chondrosarcoma,
the disease this work addresses.

**Funding.** This work received no external funding and was self-funded by the author. No grant,
institution, company or charity supported it, and no funder had any role in the design of the
analyses, the interpretation of the results, or the decision to publish.

**Ethics.** No human subjects, human material or animals were involved. All clinical figures are
taken from published reports and are cited.

**Use of AI tools.** A large language model (Claude, Anthropic) was used throughout this work: to
write the analysis code, to run the graded design and screening pipelines, to draft and revise this
manuscript, and to conduct internal critical review of earlier drafts. The work ran from 21 June
2026, the first commit of the design code, to 17 August 2026, and the repository's commit record
names two model versions over that span and no other: Claude Opus 4.8 for the design and screening
code committed between 21 June and 3 July 2026, and Claude Opus 5 for everything committed from
6 August 2026 onward, which includes every version of this manuscript. Every quantitative statement
derived from sequence or from a screen is produced by code in the released archive and is reproducible
from it, while the clinical figures are transcribed from the publications cited for them; no numerical
result was generated by a language model directly. Every literature identifier was checked against a
retrieved bibliographic record, and identifiers that could not be so anchored were removed rather
than retained. The three references dated 2026 were additionally checked for live resolution against
two independent registries, Europe PMC and Crossref, which return the same title and the same digital
object identifier for each; those records travel with the archive. The frame grading and the
mature-parent screen were additionally reimplemented and
cross-checked as described under Provenance, which bounds implementation error but is not
independent review. The author takes full responsibility for the content, including for the
correctness of the code and for the interpretation of the results.

## References

*The numbered entries are listed in `fusion-junction-aso-submission-references.md`, generated
from retrieved bibliographic records. Each superscript above carries its PubMed identifier in a
non-rendering comment, and the numbering is assigned from those identifiers by order of first
citation, so a superscript and its reference cannot drift apart. The external data records this work
uses — a Gene Expression Omnibus series, two GenBank deposits, four GenBank patent sequence records,
a DepMap release and three Cellosaurus cell-line records — are cited in the text by accession and
are listed in full, with their repositories, under `Data sources` in the same file. They carry no
PubMed identifier and so take no number.*
