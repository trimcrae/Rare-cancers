---
id: DOC-FUSION-JUNCTION-ASO-SUBMISSION
title: "In silico, nearly half of junction-spanning 5-6-5 gapmer designs across 38 modelled NR4A3 fusion junctions of five extraskeletal myxoid chondrosarcoma partner genes pair a wild-type parent gene over a ten-base-pair duplex through the catalytic gap, and, as an identity between base counts, a longer gap trades gap-level margin against parent-paired gap DNA"
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

# *In silico*, nearly half of junction-spanning 5-6-5 gapmer designs across 38 modelled *NR4A3* fusion junctions of five extraskeletal myxoid chondrosarcoma partner genes pair a wild-type parent gene over a ten-base-pair duplex through the catalytic gap, and, as an identity between base counts, a longer gap trades gap-level margin against parent-paired gap DNA

**Author.** Tristan D. McRae

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [PLACEHOLDER: AUTHOR TO SUPPLY BEFORE DEPOSIT. This is not an identifier, and the deposit is
blocked until it is replaced.]

**Preprint status.** This manuscript is a preprint. It has not been peer reviewed and has not been
submitted to a journal.

**Running title.** Junction gapmers across NR4A3 fusions

**Keywords.** antisense oligonucleotide; gapmer; RNase-H1; fusion transcript; NR4A3; extraskeletal
myxoid chondrosarcoma; oligonucleotide design pipeline; off-target screening

---

## Abstract

In extraskeletal myxoid chondrosarcoma (EMC), an ultra-rare sarcoma, a variable partner gene fuses to
*NR4A3*, creating a junction present in no normal transcript. An antisense gapmer could in principle
cleave it and spare both parents; none is reported in the literature retrieved here. Of 190
junction-spanning designs (16-mers, 5-6-5, a six-nucleotide DNA gap) across the 38 in-frame
junctions of five modelled partners, 87 pair their catalytic gap against one of six mature parents
searched over ten or more contiguous base pairs, 61 of those 87 against wild-type *NR4A3* (59 at
one site) and 85 against their own parents. That is a rate over designs: 35 of 38 junctions have one
clearing that screen. Scrambles, the weakest null here, reach 6.2% against 45.8% observed; chimeras at real exon
termini of the same two transcripts, almost never reported, reach 40.6%, so no excess
specific to this disease's breakpoints is resolved. Ten base pairs is adopted, not
measured and not separated: at seven, 175 of 190 pair a parent and 9 of 38 junctions clear, but so
does that null, to 91.4% against the 92.1% observed there; at six, the gap's own length, 181 of
190; and across cuts of six to thirteen the excess over the strongest null changes sign four times
(§2.5). A longer gap quiets the transcript screens, partly by
construction at a fixed mismatch budget: parent-clean designs per junction rise from 2.7 to 6.7
while the liable count stays flat, and gap-level margin is won only by conceding
parent-paired gap DNA. Search depth moves it too: six of nine designs clean at the default
ceiling are not at ten times it. Three designs survive every screen, two at any parent-duplex
threshold; none at a junction any patient is reported to carry, so every named reagent carries
loads. The work is computational: nothing was synthesised or tested; nothing asserts
efficacy, safety, delivery or clinical readiness. Every sequence named is a
research reagent, not for administration to any person or animal.
Two leads carry off-target loads and longest parent runs of eight and nine base
pairs, so a cut of eight condemns both: 5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 and
5′-GGGCATATCTTGTGTG-3′ at *TAF15* exon 6, with two more for coverage; and three not to be used: designs the mature-parent screen clears or cannot read, pairing their whole gap against unspliced wild-type *NR4A3*.
The pipeline is released for breakpoints outside this panel.

---

## 1 · Introduction

EMC is defined in the large majority of cases by an in-frame fusion of *EWSR1* to the orphan nuclear
receptor *NR4A3*,<sup>1</sup><!--PMID:8634690--> with *TAF15* a substantial minority and *TCF12* and
*TFG* rare.<sup>2</sup><!--PMID:32572850--> *FUS::NR4A3* is reported in a recent series that
identified it by sequencing in two of five variant EMCs.<sup>3</sup><!--PMID:41755350-->
Next-generation sequencing of six EMCs finds few recurrent secondary mutations beyond the
fusion,<sup>4</sup><!--PMID:28423517--> so it is to a first approximation the single clonal
driver. That is an absence of co-mutations in six tumours rather than a dependency: no study cited
here tests whether an EMC cell requires the fusion for growth or survival, and no knockdown,
dependency screen or xenograft in this disease is cited anywhere in this paper, so the target's
necessity to the tumour is assumed throughout and is not shown. In
the *EWSR1* and *TCF12* junction types described, the predicted product joins the partner's amino-terminal
transactivation domain to essentially the entire NR4A3 protein, including its nuclear-receptor
DNA-binding domain.<sup>1,5</sup><!--PMID:8634690,11156374--> Those two sources are the extent of the
claim: a junction at *NR4A3* exon 2 lies upstream of the start codon and does not describe the same
product at all (§2.6). The disease is ultra-rare: it accounts for approximately 1–3% of
soft-tissue sarcomas, in a course a review of it describes as typically indolent yet
metastatic.<sup>6</sup><!--PMID:41055792--> No incidence, prevalence, annual case count or survival
figure for this disease is read from any source here, so nothing in this paper sizes the population
a reagent would serve in absolute terms.

That driver is currently untargeted. Surgery with clear margins is the backbone of localised disease,
and for advanced disease no clinically validated agent directly targets
*NR4A3*.<sup>6</sup><!--PMID:41055792--> The largest EMC-specific prospective study, a single-arm
phase 2 of pazopanib in centrally confirmed *NR4A3*-translocated disease, returned four objective
responses in 22 evaluable patients;<sup>7</sup><!--PMID:31331701--> anthracycline-based chemotherapy
returned four in ten evaluable patients in a molecularly confirmed retrospective series of eleven, a
result that series presents as running counter to the prior record.<sup>8</sup><!--PMID:24345066-->
The review describes a low objective response rate to anthracycline-based
chemotherapy,<sup>6</sup><!--PMID:41055792--> which the retrospective series just cited runs counter
to, and the pazopanib report opens on low sensitivity to cytotoxic chemotherapy
generally;<sup>7</sup><!--PMID:31331701--> none of the three publishes a response
rate by line of therapy. Every figure in this paragraph is an objective response rate, and no
progression-free survival, disease-control rate, duration of response or overall survival figure is
read from any of these reports here, so the paragraph bounds what has been reported to shrink
tumours and is not a characterisation of how these agents are used or of how long patients live. The population a fusion-directed agent would address is
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
justification,<sup>17</sup><!--PMID:27166877--> and an *N*-acetylgalactosamine (GalNAc)-conjugated junction siRNA in
fibrolamellar hepatocellular carcinoma passed the delivery gate in a rare fusion-driven cancer,
reaching durable growth inhibition in patient-derived
xenografts.<sup>18</sup><!--PMID:37980543--> That last precedent does not transfer to this disease
and is cited for the junction, not for the route: GalNAc conjugates enter cells through the
asialoglycoprotein receptor, which is a liver receptor, and the report's own basis for using it is
that fibrolamellar tumours retain that receptor at hepatocyte levels. An extraskeletal soft-tissue
sarcoma satisfies neither premise, and no delivery route is proposed anywhere in this paper. The
contribution here is the indication rather than the
modality: across 5,153 unique records retrieved from Europe PMC, four mention *EWSR1::NR4A3* at title
or abstract level, and none is an oligonucleotide study. Those four resolve to three papers, one of
them indexed twice; that de-duplication is recorded in the working record travelling with the
archive rather than in the retrieval artefact, which holds the record identifiers and the counts.

Two questions follow that the field has not asked of this disease. The first is whether specificity
sorts by partner at all. No junction-directed oligonucleotide study has compared specificity across fusion partners: each
precedent addresses one fusion (a bi-shRNA lipoplex against the *EWSR1::FLI1* junction in Ewing
sarcoma, antisense oligonucleotides against *NAB2::STAT6* in solitary fibrous tumour; §4.1), and
none asks whether the partner changes what is achievable. In this disease the partner varies, and
partner identity may not be clinically inert: across the two series of antiangiogenic
tyrosine-kinase inhibition in advanced EMC that report a partner breakdown at all, no objective
response is reported in a *TAF15* patient, on a *TAF15* arm of three to five patients whose Wilson
upper bound remains compatible with equal
response.<sup>7,19</sup><!--PMID:31331701,24703573--> The two series are not shown to be independent cohorts, which is why the count is a range and why
they are not pooled: the smaller ran at an institution that was a site of the larger trial, under
the same senior investigator, so the same patients may appear in both and the distinct *TAF15* arm
may be as few as three.
Neither primary report's retrieved record states the per-arm
denominators, and the sunitinib record states the partner split only qualitatively. Both full texts
are paywalled here, so both may state more than their records show. Both denominators
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
only and must not be administered to any person or animal; the operative statement is in Declarations
and governs this manuscript throughout, not any one section.
Do not order an oligonucleotide by copying it out of this PDF: the canonical record is
`fusion-junction-aso-sequences.csv` and `fusion-junction-aso-sequences.fasta` (§6). Before any
oligonucleotide is ordered, the breakpoint of the cell line or tumour sample used as the test
article must be established at nucleotide resolution by RNA sequencing (§4.4): every design here is
specific to the exon pair or pairs it was tiled at, and none is valid for an unverified junction.
That is a laboratory precondition for an experiment and not a clinical indication to sequence a
patient: no sequence named here may be administered to anyone, so no sequencing result about a
person changes what is available to them.

Every line below points at a fuller statement in the section cited, and none of it is argued here.

**The terms of art (§6).** A *seam* is a donor exon joined to an acceptor exon, and each seam is
tiled by several designs. Each design is one *register* of its junction, one way of sliding the
16-mer while the breakpoint still falls inside the six-nucleotide DNA *catalytic gap* RNase-H1
cleaves within; the 5-6-5 geometry admits five per junction. A design's *gap-level margin* is the
count of junction-unique bases inside that geometry's gap on the shorter side of the breakpoint: the number of
bases a wild-type parent would have to match by coincidence in order to pair the whole gap. The
gap-level margin is the
axis this paper's central negative is stated on; where a table instead ranks by predicted
liability, or by the conventional design rules of §2.10, that table's caption says so.

**Exon numbers here are transcript exon indices, not coding-exon indices**, counted from the
transcript 5′ end of the model §6 names, including non-coding exons. The two conventions differ for
*TCF12*, *TFG* and *NR4A3*; the numbers used here are what a breakpoint is matched to a design by,
and §6 gives the accession for every gene so a report numbered the other way can be reconciled.
The consequence is not cosmetic: at one *EWSR1* exon-13 donor this paper's *NR4A3* exon-3 and
exon-2 acceptors carry five registers each with no molecule in common, and two registers at each
carry `do_not_order`, for different reasons (§2.5, §2.6). An acceptor exon number read under the
wrong convention therefore selects a different reagent.

A *near-match* is a transcript window pairing a design at 14 or more of
its 16 positions, and is *gap-paired* where the six gap positions are themselves paired, which is the
class RNase-H1 could cleave; a gap-paired near-match on the sense strand is what this paper calls a *gap-paired sense-strand match*. That name replaced *cleavage risk* on 2026-08-19, because the earlier term named a catalytic outcome for what is a sequence observation. No screen here predicts cleavage (§5); each grades hybridisation only. A design is *clean* where a complete hit list at a stated search depth
returns no sense-strand near-match, and a design's *load* is its predicted off-target burden counted
as near-matches. A design is *liable* where a wild-type parent pairs its whole catalytic gap over a
contiguous run reaching a stated length, ten base pairs unless another is named, and the count of
liable designs is what §2.5 reports at each length it reads the same screen at. That length is a
whole-duplex count and not the enzyme's unit: the figure ten is taken from is a range of 7 to 10
RNA:DNA hybridised nucleotides, and a 5-6-5 design holds six of those against every target, below
that range in every design, so four or more pairs of any ten-base-pair run counted here are
locked-wing pairs. The count is a stratification of the panel at a stated cut and not a prediction
of cleavage (§5, §6). Counts from that hit list come at one of two search depths, a default alignment
ceiling and a tenfold deeper one (a hitlist of 50 alignments per query, of which 15 are retained,
against 500 with retention raised to match so that no list is truncated; §6), and each is reported
with the depth it was taken at. Five screens
are applied, numbered here as in §6: (1) the
alignment screen, (2) the exhaustive transcript scan, (3) the pre-mRNA screen, (4) the mature-parent
screen and (5) the genome scan.

**The two lead reagents to synthesise (§4.1, which names two more for coverage).** 5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 joined
to *NR4A3* exon 3, carrying 123 gap-paired sense-strand near-matches at six gene loci at the deeper
search ceiling, of which 82 hits fall on computationally predicted gene models rather than curated
ones (§5), together with a sense-strand near-match in wild-type *TAF15* precursor RNA (§4.3); and
5′-GGGCATATCTTGTGTG-3′ at *TAF15* exon 6, carrying 8 such near-matches at five loci and no
sense-strand pre-mRNA site. Both hold the top gap-level margin of 3, and neither has been synthesised
or tested. Neither clears the parent screen with room to spare: their longest parent runs through the
gap are eight and nine base pairs against a criterion of ten, so at any cut of eight or below,
which is inside the range §5 bounds that criterion by, both fall inside the liability class this
paper's central negative is about, and at nine the *TAF15* reagent alone does (§4.1). Between them they address the published breakpoints of roughly two thirds of molecularly confirmed cases
(39.9% to 82.8% on the breakpoint denominators alone, and optimistic by an unmeasured
amount because one arm is priced 3 of 3 on a three-tumour series, the four bounds §4.1 sets on it
running in different directions rather than all one way; §4.1, §5) on the
coverage ladder: the reagent set ordered so that each added reagent, each *rung*, carries
the cumulative share of published breakpoints the set through that rung addresses, with a *bound* row
giving what that share would be if every remaining breakpoint of a partner were covered (§4.1).

**Three designs not to be used (§2.6).** 5′-CAGTGGGCTCTCCACG-3′ and 5′-GCAGTGGGCTCTCCAC-3′ at *EWSR1*
exon 13 joined to *NR4A3* exon 2, and 5′-TGATGAGGGCCTTGTG-3′ at *TAF15* exon 6 joined to the *NR4A3*
intron-2 cryptic exon. Two of the three cleared the spliced-cDNA parent screen and the third's seam that screen cannot address, so its record reads `not_screened` rather than clear; and each pairs its whole
catalytic gap against the patient's own un-rearranged *NR4A3* allele, which that screen cannot see.

**A second class not to be ordered, and it is much larger (§2.5).** Any design a wild-type parent
pairs through the whole catalytic gap at ten base pairs or more surrenders the advantage the
modality has, and that is this paper's central negative rather than a side finding: 87 of the 190
panel designs, and 249 of the 780 records the canonical file holds, the records whose
`mature_parent_duplex_through_gap_bp` column reaches ten, which is the column the count is
reproducible from. They are marked ⚑ in Tables 3 and 4 and carry `do_not_order` in the canonical
file. The three designs of the paragraph above carry `do_not_order` for the other reason, so 252
records carry the flag in all. **⚑ IS THAT VERDICT, WHEREVER IT APPEARS.** A sequence printed with
⚑ beside it, in a table, in a figure, or inline in the body text, is one this paper says must not
be ordered or used; the marker means the same thing in prose as it does in a table, and it is never
decorative. Tables 3 and 4 mark ⚑ every design of this class that they print,
but between them they print only a small minority of it, because they are per-junction and
per-screen selections rather than a census, so an absence from those tables is not a clearance and
the canonical file is the only complete record. Five of the nine designs §2.4 names as
carrying no sense-strand near-match are in this class. An unmarked row is not a clearance: the
marker is set at ten base pairs, and at seven, 175 of the 190 pair a parent through the whole gap.
Neither verdict can be read off a sequence by eye. Two of the three designs §2.6 forbids, and one of
the two lead reagents above, each sit a single base from a design at the same junction carrying the
opposite verdict: 5′-CAGTGGGCTCTCCACG-3′ ⚑ beside 5′-AGTGGGCTCTCCACGG-3′, 5′-TGATGAGGGCCTTGTG-3′ ⚑
beside 5′-GATGAGGGCCTTGTGT-3′, and the orderable 5′-GGGCATATCTTGTGTG-3′ beside
5′-AGGGCATATCTTGTGT-3′ ⚑. The canonical file carries that pairing for every design that has one, in
its `near_identical_design_with_a_different_verdict` column.

**The cell line (§3).** No *NR4A3* fusion is detectable in H-EMC-SS on the public record, which
is a filtered caller's silence and bounds detection at a sensitivity nothing here quantifies rather
than establishing absence, so no reagent named here can be assumed testable in it without sequencing
its junction first. That is not a statement that the line is misidentified.

**The replicate floor and the void condition (§4.4).** Selectivity is the wild-type *NR4A3*
half-maximal knockdown concentration divided by the fusion's, from a matched dose–response in the
same wells, and the cut is 5.0, taken as a convention rather than measured for this comparison (§4.4). Three biological replicates are a floor and not a target: above a
replicate standard deviation of about 0.65 on the natural-log scale, no observed ratio at or above
one can place the upper limit of a two-sided 95% interval below that cut at three replicates, so the
test can fail only where the reagent is anti-selective and the test is otherwise void rather than
negative. A *void* test is one that cannot fail, which is a different outcome from one that fails to
falsify, and voidness is a property of the assay's variance rather than of the design. The
controls, the assay placement and the limit-of-quantification condition without which
the ratio is not reportable are in §4.4.

**A design procedure for a breakpoint outside this panel (§4.5).** The pipeline that produced the
190 designs is released with the artefacts, and §4.5 gives its input, the five screens a new design
must clear, and the limit on what it produces: a candidate, not a validated reagent.

## 2 · Results

The results are ordered for a laboratory deciding what to make. How far any of the counts below can
be trusted is stated in §5, which bounds all of them.

**How the counts are denominated.** Six numbers recur below and they are not interchangeable. 231 is
the number of donor-exon by acceptor-exon pairs graded for frame. 38 are the in-frame junctions among them. Those 38 carry 190 design records, which are 176 distinct molecules, because nine of the
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
donor coding phase of 1, which is necessary and sufficient across those 77 exon-3
rows but only necessary across all 231.

Among these, *EWSR1* exon 12 joined to *NR4A3* exon 3 is the junction reported most often: type 1 in
10 of the 15 *EWSR1*-rearranged tumours of an 18-case series.<sup>22</sup><!--PMID:12378528--> Designs
at this junction therefore correspond to the largest documented patient group. The type numbers are
each source's own shorthand for a donor–acceptor exon pair and are used here only where a source uses
them; every junction in this paper is named by its exon pair, so no type number needs to be resolved
in order to read a design.

No design at any of the 38 junctions is a perfect complement of any of the six parent transcripts.
That check excluded none of the 190 and could not have: a junction-spanning window cannot occur
intact in a parent. It is a guard against an error in the screen, not a specificity result.
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
three gene loci at best, and five for the design its gap-level margin ranks first (Table 2);
three of those five are annotated only as predicted gene models, which is a property of the
deep hit list rather than a column of any table here. Two of the five nonetheless return no exact
and no single-mismatch match on the exhaustive transcript scan.

So the one *TAF15* junction with a published breakpoint is designable and is not among the cleaner
junctions, while the junction the multi-partner result rests on has no reported patient. For *FUS* no
exon-resolved EMC breakpoint has been published at all. The three-partner result is therefore a
statement about FET-family (*FUS*, *EWSR1*, *TAF15*) sequence architecture and a hypothesis about junctions not yet observed.
It is not a claim that one reagent serves three patient groups. Testing it requires breakpoint
sequencing of archival *TAF15*- and *FUS*-positive cases.

### 2.3 · The non-FET partners: coverage and specificity

*TCF12* and *TFG* are the partners in this panel that are not FET-family proteins, and neither
appears in any of the nine multi-partner designs: all nine draw only on *EWSR1*, *TAF15* and *FUS*.
*TCF12* reaches multi-partner coverage only under a relaxed criterion that tolerates mismatches in
the oligonucleotide wings. That check had little power to fail, because a donor sharing the last bases before the
breakpoint by coincidence passes it as readily as a paralogue does, so it does not separate FET
paralogy from incidental exon homology. The stronger
evidence for paralogy is that the remaining four of the nine, which span two partners rather than three, are also FET-only.

Specificity does not sort by partner on the one existence statistic tested, and does on the one
other axis this section prints. Taking at each junction the lowest count any of its
designs achieves after the orientation filter (a per-design minimum, which is in the released
per-junction screens and not in Table 3, whose row is that junction's highest-margin design and not
its cleanest) every one of the five partners has at least one
junction whose cleanest design carries no sense-strand near-match across the catalytic gap at the
default search ceiling: three of eight at both *TCF12* and *FUS*, two of eight at *EWSR1*, one of
eight at *TAF15* and one of six at *TFG*. At the tenfold deeper ceiling that becomes four partners:
each of *EWSR1*, *FUS*, *TAF15* and *TCF12* keeps one such junction and *TFG* keeps none, its single
default-depth zero returning 29 across the gap when searched deeper. On this one existence
statistic, then, no partner is uniformly clean or uniformly dirty, and which exon a fusion breaks
at bears on specificity as well as which gene it breaks into. That is the limit of what was
tested: no comparison between partners was performed, and one axis printed here does sort by
partner. Table 2's genome-wide gap-paired load runs at a mean of 1.30 of chance across *TFG*'s
five scored junctions — Table 2 gives a best row only at the 35 junctions where some design clears
the parent screen (§2.7) — four of them above chance, against partner means of 0.51 to 0.71 taken
over seven or eight junctions each, and three rows above chance among the other thirty junctions;
over the whole corpus the same axis reads 2.23 across *TFG*'s thirty designs against 0.74 across
the other 146 of the 176 distinct molecules. Those two means are not comparable summaries: the
*TFG* distribution has a standard deviation of 3.41, larger than its own mean, and one design at 20
times chance, so its median is 1.53 while the other 146 sit at a median of 0.74 with a standard
deviation of 0.44. On medians the contrast is 2.1-fold rather than 3.0-fold. That axis is reported and it is confounded rather
than explained: the null behind it assumes uniform bases, so it tracks base composition, and *TFG*'s
designs average 39.0% GC against 50.6% elsewhere. Non-*TFG* designs at matched composition (the 46
of the other 146 carrying no more than seven G or C bases of 16, the band 29 of *TFG*'s 30 designs
fall in) run at 1.04. That restriction is one-sided — the 1.04 is over matched non-*TFG* designs
while the 2.23 is over all thirty *TFG* designs — and restricting both sides gives 2.28 against
1.04. Matching on composition therefore removes 20% of the difference in means one-sided, 0.74 to
1.04 against 2.23, and 17% with both sides restricted, so part of the excess is GC and not partner;
how large a part depends on the scale chosen, and both figures are on the plain difference in
means. On medians, the scale this paragraph moved to above, matching removes a third rather than a
fifth:
the matched non-*TFG* median is 1.00 against *TFG*'s 1.53, so the median contrast falls
from 2.1-fold to 1.5-fold and does not close. The matching rule is stated
because the answer moves with it too: taken instead over the whole span of GC that *TFG*'s designs
cover, the same figure is 0.89. Neither reading leaves the partner effect intact, and neither is a
composition-matched null: the one built for the mature-parent screen was not run for the genome
scan.

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
gap-paired near-matches at the deeper ceiling, every one of them a variant of a single
locus (Table 2). That locus is the curated *PIK3CG*, which is read from the deep hit
list; Table 2 carries no gene column. None of the four *TCF12* designs with no sense-strand near-match is at
that exon. So for *TCF12* as for *TAF15*, the junction a patient is reported to carry is designable
and is not among the clean ones, while the clean junctions have no reported patient. What remains
unmeasured at *TCF12* is not the exon but the distribution: one *TCF12*-rearranged tumour has been
sequenced at this junction, and it is the tumour the junction was defined by. No search of the
nucleotide or read archives returns a second *TCF12::NR4A3* sequence, and what that leaves the
coverage estimate resting on is stated with the estimate (§4.1).

The same archive search resolves *TFG*, the other non-FET partner, in the same way and to the same
limit. No paper places a *TFG::NR4A3* breakpoint at an exon, but a deposited chimeric mRNA record
does (GenBank AY532911.1, annotated as a *TFG-NR4A3* fusion protein), and it lands on *TFG* exon 7
joined to *NR4A3* exon 3, a junction this panel already carries. Four patent sequence records agree
at the seam (GenBank DI433544.1, DI438966.1, LG067227.1 and LG067228.1), corroborating a sequence
rather than four patients, being one family from one group. As
at *TCF12*, what the deposit supplies is the exon and not the distribution: no source states what
fraction of *TFG*-rearranged tumours break there, and *TFG* does not appear in the partner counts of
the 58-case cohort every coverage figure here is denominated on, so this changes which junctions are
reported and no percentage.

### 2.4 · Strand orientation, and designs with no sense-strand near-match

All 38 in-frame junctions were screened with orientation filtered, covering 183 designs, and Table 3
gives the per-junction result. Of the 1,677 apparent gap-paired hits across the retained hit lists,
738 sit on the minus strand, or 44%. An antisense oligonucleotide cannot base-pair with those at all.

The proportion is not uniform. It runs from 0% at *TFG* exon 4, where no apparent risk is
minus-strand, to 100% at both *EWSR1* exon 1 and *TCF12* exon 7, where every one is. That
non-uniformity is what makes the filter worth applying rather than approximating. A uniform
inflation would rescale every junction and leave the distances between them intact; this one does
not, so an apparent count is not a proxy for the filtered one even between neighbours. *EWSR1*
exons 7 and 13 return 55 and 57 apparent gap-paired hits (all but indistinguishable) and
after filtering they stand at 6 and 53.

Under the stricter criterion — no sense-strand near-match anywhere, not merely across the catalytic gap
as in §2.3 — nine designs at six junctions, a different nine from the nine multi-partner designs of
§2.2, carry none among non-parent transcripts after filtering
(Table 4), spanning four of the five partners — five of them do-not-order designs for a reason no
near-match screen sees, marked ⚑ in the list and explained after it. Three are at *EWSR1* exon 1
(5′-GGGCATATCCGTGGAC-3′, 5′-GGCATATCCGTGGACG-3′ ⚑, 5′-GCATATCCGTGGACGC-3′ ⚑), one at *FUS* exon 8
(5′-AGGGCATATCGGAGTC-3′), one at *TAF15* exon 1 (5′-GGGCATATCCGACATG-3′), and four at *TCF12* —
5′-GGGCATATCTCTATAA-3′ at exon 17, 5′-CAGGGCATATCTTGCA-3′ ⚑ at exon 9, and
5′-GGCATATCAAGCGCTG-3′ ⚑ and 5′-GCATATCAAGCGCTGC-3′ ⚑ at exon 7. Five of those nine carry ⚑ here
and `do_not_order` in the canonical file, because the mature-parent screen of §2.5 condemns them at
eleven or twelve base pairs: this is a list of designs clean on the near-match screens, and it is not
a list of designs to order. The exhaustive transcript scan agrees
independently: each returns no exact and no single-mismatch match anywhere in 186,185 transcripts.
The two screens fail in different ways, so their agreement is not a restatement. One is a heuristic
alignment search over both strands; the other an exhaustive substitution scan over the sense
orientation only. The pre-mRNA screen, over a compartment neither of those reaches, does not
overturn them either: none of the nine carries a pre-mRNA site of the strict class §2.5 defines
(gap-paired, sense-strand), though §2.5 is silent on the wider sense-strand forty, of which 21 pair
all of the gap but one or two positions.

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
near-matches at the default depth, but a raw either-strand count decides nothing about sense-strand
cleanliness (§5); what disqualifies them is that none carries a deep hit list at all, which §2.7
requires of a candidate, and no count below depends on them. Only
three of the nine still carry no sense-strand near-match: 5′-AGGGCATATCGGAGTC-3′ at *FUS* exon 8,
5′-GGGCATATCCGACATG-3′ at *TAF15* exon 1 and 5′-GGCATATCAAGCGCTG-3′ ⚑ at *TCF12* exon 7 — the last
of which the mature-parent screen condemns at eleven base pairs against wild-type *TCF12* and §2.7
excludes, so it is not to be ordered. Each returned the same count at both depths. The other six did not. The three *EWSR1* exon-1 designs had
returned no near-match at all at the default ceiling and return 27, 29 and 84; 5′-GGGCATATCTCTATAA-3′
at *TCF12* exon 17 goes from 8 to 118 on either strand, and 5′-CAGGGCATATCTTGCA-3′ ⚑ at *TCF12*
exon 9 from 7 to 67; and 5′-GCATATCAAGCGCTGC-3′ ⚑ at *TCF12* exon 7, which had one near-match and none on the sense strand, returns 18 with two. Three of the six carry hits that span the catalytic gap and so are gap-paired rather than merely sense-strand matches: 64 for 5′-GCATATCCGTGGACGC-3′ ⚑, 14 for
5′-GGGCATATCTCTATAA-3′ and 11 for 5′-CAGGGCATATCTTGCA-3′ ⚑. Three of the designs named in this
paragraph carry ⚑ because the mature-parent screen condemns them at a twelve-base-pair duplex —
5′-CAGGGCATATCTTGCA-3′ against wild-type *NR4A3*, 5′-GCATATCAAGCGCTGC-3′ against wild-type *TCF12*
and 5′-GCATATCCGTGGACGC-3′ against wild-type *EWSR1* — so none of them is to be ordered, and they
are named here only for what the depth change does to their hit counts. A count of zero at the default ceiling
was not a count of zero, which is the sharpest form of the bound §5 sets out. The three named above
are clean on the near-match screens alone; composing them with the mature-parent screen changes
which design stands at *TCF12* exon 7, as §2.7 sets out, so this list is not the candidate set and
must not be ordered as one.

The deeper pass also decided what the default one could not. Seven of the 190 designs had failed at
the remote service and carried no count at all — a different seven from the seven §5 reports as
withheld by retention alone, which do carry default-depth counts; all seven returned at the deeper
ceiling, six of them dirty and one (5′-GGGCATATCAAGCGCT-3′ at *TCF12* exon 7) with three near-matches and none
on the sense strand. So the set of designs with a complete hit list and no sense-strand near-match is four
at this depth rather than three: a design the shallower pass never screened joins the three that
survived it. The deeper counts are reported as their own
measurement and no figure quoted above is restated from them.

The orientation call is corroborated independently of any of this. Ten designs return perfect
16/16 BLAST matches while the sense-only exhaustive scan reports no exact match, and every one of
those BLAST hits is on the minus strand. That last is read off the alignments rather than deduced
from the disagreement, and the deduction would not have been available: the two screens do not
search one corpus (§6, screens 1 and 2), so a hit to a record outside the pinned GRCh38.p14 set
would reconcile the two results without any statement about orientation at all.

### 2.5 · The parents: liability in pre-mRNA and in mature transcript

RNase-H1 is active in the nucleus and gapmers engage pre-mRNA, so a screen over mature transcripts
cannot see intronic or intron–exon-spanning sites. That omission is not neutral in its direction. A
junction gapmer's two halves are both exonic, and in a parent pre-mRNA an exon is followed by an
intron rather than by the next exon. Parent pre-mRNA is therefore precisely where a design's donor
half sits beside sequence no mature screen has compared it against. A mature-only screen returns a
low count partly by construction.

That argument cuts one way and the paper does not pretend otherwise. The fusion junction is itself
made by splicing: in an unspliced fusion transcript the donor exon is followed by intron, exactly as
in a parent, so the target these designs are built for exists only in spliced transcript, while the
parent pre-mRNA sites counted here are additionally available on nascent transcript. The screens do
not resolve that asymmetry between target and liability, and nothing here measures how much of
either species a gapmer meets.

Of the 190 designs, 53 have a near-match somewhere in parent pre-mRNA. Nineteen carry one that meets
all three conditions that would make it dangerous: it is on the sense strand, it pairs the catalytic gap in
full, and it touches intronic sequence. That third condition is what makes such a site invisible to
both transcript screens, rather than a re-count of something already reported.

The two liability classes are not disjoint designs, and the arithmetic has to be done as a union
rather than a sum. Thirteen of those 19 are already among the 87 designs the mature-parent screen below returns (screen
4, which finds a parent duplex of at least ten base pairs through the whole gap), so the pre-mRNA
compartment adds six designs that screen misses entirely, and the two screens together condemn 93 of
190 rather than the 87 + 19 = 106 a sum would give. That union is arithmetic and not a claim that
the two liabilities are equivalent: an intron–exon-spanning site exists only between transcription
of that region and its splicing, while a mature-transcript site is present for as long as the
transcript is, and nothing here measures either abundance. The 93 is a count of designs condemned by
at least one screen, not a graded liability. What the compartment adds is therefore a liability class
invisible to every mature screen, not a second population of comparable size: the six are the number
that matters for a laboratory choosing among designs that already passed the mature-parent screen.

The step from 53 to 19 runs through two filters and only the second is a threshold. Thirteen of the
53 carry their pre-mRNA sites on the minus strand alone, which an antisense oligonucleotide cannot
pair at all, leaving forty with a sense-strand parent pre-mRNA site. The step from forty to 19 is
then a threshold rather than a measurement, and the class it removes is the one the Methods (§6)
decline to dismiss: the 19 are those pairing the catalytic gap in full, and the remaining 21 pair
all of it but one or two positions. Of their 28 sites, 26 are a single gap mismatch short; five of the 28 are in *NR4A3* itself.
Under the bounds this work adopts, a single mismatch inside the gap does not abolish cleavage, so
those 21 are not a null result. They are excluded because a graded count over this compartment would
need a discrimination model the literature does not supply for a parent duplex. The same condition
governs the mature-parent screen below, which considers only windows pairing the whole gap. The
headline counts of this section should be read as the fully-paired class, not as the whole parent
liability: the 19 is drawn from the forty and the forty from the 53, while the 21 the 19 leaves out
is counted separately rather than being a tally it comes from. The mature-parent counts below carry
the same exclusion, and their own wider tally is the 181 designs a parent can pair the whole gap for
at any length (§2.9).

Those 19 designs fall into two classes that do not mix, and only one is mechanistically interesting.
Nine are intron–exon-spanning, and all nine read the same two sites in *NR4A3*: each begins in the
last six or seven nucleotides of intron 2 (an intron 2,208 nucleotides long, so the site sits at
its 3′ end and not near its start) and spans the boundary into exon 3. That follows from the design problem. A
junction gapmer's acceptor half is the 5′ end of *NR4A3* exon 3, and the wild-type *NR4A3* transcript
reaches that same exon across its own splice junction. So a design whose donor half also matches the
3′ end of intron 2, within the mismatch budget, pairs across the real splice site. That is a route to
wild-type *NR4A3* engagement which does not pass through the fusion at all, in the compartment where
RNase-H1 is active. It is the discrimination question this paper is about.

**And that site carries a second liability no screen here grades.** The sequence those nine designs cover
is not incidental: the last twelve nucleotides of *NR4A3* intron 2 are `CTGTCCCTGCAG`, a
pyrimidine-rich tract closing on the AG that terminates the intron, so the site is the wild-type
3′ splice acceptor itself. An oligonucleotide occupying a splice acceptor can alter the splicing of
the transcript it sits on by occupancy alone, which is the steric mechanism §3 names as unevaluated
here, and that route requires no catalytic gap, no ten-base-pair duplex and no RNase-H1. Every screen in
this paper grades hybridisation-dependent cleavage liability (§5), so none of them sees it, and the
one- to five-fold single-mismatch discrimination bounds this work imports do not bound it. What
that would do to wild-type *NR4A3* is not predicted here; it is named because the screens are
silent on it rather than reassuring about it. The other ten are wholly
intronic and every one is in *TCF12*, which contributes 365,096 of the 517,157 intronic nucleotides
searched. That is 71% of the search space accounting for 100% of the class: volume alone predicts
about seven of the ten, so it accounts for most of the concentration and the remainder should not be
read as anything about *TCF12*.

The liability tracks the tiling register, of which the gap-level margin is a function. At margin 1,
12 of 76 designs carry a gap-paired sense-strand pre-mRNA site of the strict class just
defined — the 19, not the 53 or the 40; at margin 2, 7 of 76; at margin 3, none of 38. Eight of the
nine designs reading those two *NR4A3* boundary sites are at the shortest donor-side register, which
needs the fewest intronic bases to match. None of the nine designs with no sense-strand near-match on either transcript screen
carries one.

The second of the two liability compartments (mature parent transcript rather than pre-mRNA) is
the larger. Each of the first three screens
misses it for its own reason. The alignment screen excludes parent records by design and filters at
≥14/16 identity. The exhaustive transcript scan admits only one mismatch. The pre-mRNA screen
searches unspliced sequence and so cannot reach a mature exon–exon junction. A parent duplex of 11
or 12 contiguous base pairs that pairs the whole catalytic gap is therefore invisible to all three,
while satisfying the duplex criterion adopted here — which §5 and §6 record as stated rather than
measured for this architecture.

Screen 4 compares every design's target window to every window of all six mature parents. 87 of 190
designs have a duplex of at least ten base pairs, and 61 of those 87 are against wild-type
*NR4A3*, the transcript this modality must spare. Six transcripts are searched, so a duplex could in
principle fall on a gene with no relation to the design's own fusion, and that reading has to be
separated from the one the title makes: 85 of the 87 pair one of the design's own two parent genes —
*NR4A3* or its own donor — and two do not, one *FUS* design paired by *TAF15* and one *TAF15* design
paired by *EWSR1*, both inside the FET paralogue family. The liability is therefore self-targeting
almost throughout, which is what makes it a property of the modality rather than an ordinary
off-target count. Sub-threshold readings do not follow that pattern: the two lead reagents of §4.1
run to eight and nine base pairs against *TFG*, a gene neither fusion involves. The count is a floor at the threshold chosen, and
seven base pairs is the shortest end of the same cited range (§6): at seven the same screen returns
175 of 190 rather than 87, and 9 of the 38 junctions retain a design clearing it rather than 35.
Loosening the cut enlarges the negative on both of those readings and does not strengthen it, because
the nulls below move with it. Re-run at seven, the exon-terminus chimera ensemble reaches 91.4%
against the 92.1% that 175 of 190 is, and the comparison attributed to *NR4A3* reverses outright, 73 of 190 or 38.4%
observed against 46.6% for the null. At seven this screen is measuring what any chimera of two real
transcripts does.

**Ten is adopted, and reporting two cuts is still a choice of two cuts.** Whether 87 of 190 is a
property of these designs or a property of where the criterion was put is a question about the whole
range, so the whole range is measured — the observed arm, every null ensemble, and the junction-level
reading, at every cut the instrument can reach. The shortest counted run is the catalytic gap itself,
six base pairs, which is the only cut with an enzymological referent, since a counted run of any
length presents exactly those six as RNA:DNA hybrid and the rest as locked-wing pairs; thirteen is
the longest run any arm returns.

**The cut ladder.** Every cut the instrument can reach, from the catalytic gap's own six base pairs to the thirteen that is the longest run any arm returns: the observed arm, its Wilson interval, the strongest null ensemble at that cut and the scramble null beside it, the signed excess of observed over strongest null, the junction-level reading, and how many designs pair wild-type *NR4A3* specifically. This is the paper's central negative and is set here, in the argument that reads it, rather than with the numbered tables: the excess over the strongest null changes sign four times down the column, so no cut in the range is a boundary the data picks out. Derived, like every table here, from the released artefacts; the adopted cut of ten is one row of it and is adopted, not measured.

| cut (bp) | liable designs | % | Wilson 95% | strongest null % | scramble null % | observed − strongest | strongest null vs the observed interval | junctions with a clearing design | designs still liable at the five published-breakpoint junctions | designs *NR4A3* pairs specifically |
|---|---|---|---|---|---|---|---|---|---|---|
| 6 | 181 | 95.3 | 91.2–97.5 | 98.2 (exon-terminus, novel acceptor) | 91.4 | −2.9 | outside, above | 6 of 38 | 25 of 25 | 158 |
| 7 | 175 | 92.1 | 87.4–95.2 | 91.4 (exon-terminus) | 74.3 | +0.7 | inside | 9 of 38 | 25 of 25 | 111 |
| 8 | 143 | 75.3 | 68.7–80.9 | 76.2 (exon-terminus) | 43.8 | −1.0 | inside | 23 of 38 | 21 of 25 | 84 |
| 9 | 98 | 51.6 | 44.5–58.6 | 56.8 (exon-terminus, novel acceptor) | 18.4 | −5.2 | inside | 31 of 38 | 14 of 25 | 63 |
| **10** | **87** | **45.8** | **38.9–52.9** | **40.6 (exon-terminus)** | **6.2** | **+5.2** | **inside** | **35 of 38** | **11 of 25** | **62** |
| 11 | 84 | 44.2 | 37.3–51.3 | 34.7 (exon-terminus) | 1.8 | +9.5 | outside, below | 37 of 38 | 11 of 25 | 62 |
| 12 | 35 | 18.4 | 13.6–24.5 | 14.5 (exon-terminus) | 0.4 | +3.9 | inside | 38 of 38 | 5 of 25 | 24 |
| 13 | 6 | 3.2 | 1.5–6.7 | 4.7 (exon-terminus) | 0.1 | −1.6 | inside | 38 of 38 | 1 of 25 | 5 |

The strongest null at every cut is one of the two exon-terminus chimera arms (the column names
which, because they change places at six and nine) and the comparison
against it does not behave as a real effect behaves. **The excess is not monotone in the cut and
changes sign four times**: the observed rate is below the strongest null at six, eight, nine and
thirteen, and above it at seven, ten, eleven and twelve. The strongest null lies inside the observed
rate's own nominal interval at every cut but two — at six it lies above it, and at eleven, which is
not the cut reported here, below it. **An earlier version of this section said that ten is the cut at
which the observed rate stands clear of every null. The ladder was written to check that sentence
and it does not survive: at ten the exon-terminus null is inside the interval, as the closing
paragraphs of this section already said in another form.** Ten is the cut this work adopts and states
every count at, on the criterion's stated provenance (§6) rather than on separation, and no cut in
the reachable range resolves an excess over a chimera of two real exon termini. The central negative
is therefore not weakened by the ladder; it is the same negative, holding across the criterion's
whole range instead of at one point in it.

Three further readings come off the same table and none of them is available from a single cut. The
junction-level and design-level counts move in opposite directions, so a looser criterion enlarges
the class and empties the panel at once: at six, 181 of 190 designs are liable and only 6 of 38
junctions retain a design that clears. At the five junctions any patient is reported to carry, every
design is liable at six and at seven, and the count falls gradually rather than stepping — 21 of
those 25 at eight, 14 at nine, 11 at ten — so the deliverable is more cut-dependent than the corpus
is. And the count of designs wild-type
*NR4A3* pairs specifically (asked of *NR4A3* alone rather than attributed to whichever parent
returned the longest run) is 62 at ten against the 61 attributed there, and 158 at six against 77:
the attributed figure this paper reports is a floor on the *NR4A3*-specific one, and the two separate
as the cut loosens. Those 61 are not 61 distinct sites: 59 of them are
the same one, the mature exon-2/exon-3 seam every design's acceptor half reaches, which is the
mature-transcript counterpart of the pre-mRNA concentration above. One further design pairs *NR4A3* at eleven base pairs but
another parent at twelve, so it is attributed elsewhere. The count falls steeply with the gap-level
margin: 50 of 76 designs at margin 1, 29 of 76 at margin 2, and 8 of 38 at margin 3. That is what the
margin's definition predicts, since at margin 1 a parent needs one lucky base to pair the whole gap
and at margin 3 it needs three. Five of the nine designs of §2.4 carry such a duplex at 11 or 12 base
pairs, including 5′-CAGGGCATATCTTGCA-3′ against wild-type *NR4A3* itself — a do-not-order design, ⚑
in Table 4. The margin is therefore a
predictor of parent engagement rather than a guarantee against it, because it counts bases unique to
the fusion at the junction without asking whether a parent carries them elsewhere.

Eighty-seven of 190 is 45.8%, with a nominal binomial Wilson 95% interval of 38.9–52.9% — nominal
because it treats the 190 records as independent draws, which the close of this section states they
are not. Clustering on the 38 junctions the five registers of each are tiled from, with the
within-junction correlation estimated by one-way analysis of variance, gives a design effect of
1.42, an effective sample of 134 and an interval of 37.6–54.2%, which is the one to read. That
interval is a Wilson interval evaluated at the effective sample, 133.57 before rounding, and the
correction it carries is for register clustering only: it does not reach the other non-independence
the close of this section names, because the nine molecules recorded at more than one junction fall
in different clusters rather than in one. Collapsing the 190 records onto the 176 distinct
molecules instead gives 82 of 176, 46.6%, nominal Wilson 39.4–54.0%. Both intervals sit on a
complete enumeration rather than on a sample (the 190 are every 5-6-5 register whose seam falls
strictly inside the catalytic gap, at all 38 junctions) so what they describe is a differently
tiled panel of the same junctions, not sampling error about a larger population of designs. A count of that
kind means little
without a null, so the same
screen was run over arbitrary 16-mers. Only the query changes: the same six mature parents, the same
forward orientation, the same ten-base-pair threshold. Scrambling each design's own target window,
which preserves its base composition and is the scrambled-gapmer control §4.4 asks a laboratory to
make, gives 6.2% (5.9–6.4%); a dinucleotide-preserving shuffle gives 10.0% (9.7–10.3%); 16-mers drawn
from uniform bases give 6.9% (6.7–7.2%), and from the panel's pooled base composition 7.2%
(6.9–7.4%). Every parenthesis on a null rate in this section is a Monte-Carlo interval on that
ensemble's mean, narrowing with the number of draws rather than with evidence, and it is not the
spread against which the observed rate should be read; the exon-terminus paragraph below sets
the two against each other. The uniform-base figure does not stand alone; a calculation on the same uniform bases
agrees with it: the gap must pair,
at 4⁻⁶, and the run must
then extend four further nucleotides across the two wings, at 1/64, which over the 19,921 parent
windows searched predicts 7.3%. That last step is a Poisson conversion and treats those windows as
independent trials, which they are not: they tile 20,011 nucleotides, so consecutive windows share
15 of their 16 bases and a site that lands in one lands in its neighbours too. Clumping of that kind
makes a Poisson figure sit high, and the sampled uniform arm 0.4 points below it at 6.9% is what
bounds the assumption here. The observed rate is 6.6 times the sampled uniform-base arm, and the *NR4A3*
sub-analysis the modality actually turns on appears to separate further still: 32.1% of designs
carry their qualifying duplex against wild-type *NR4A3*, against 1.8% of scrambles — the count
attributed to *NR4A3*, not the *NR4A3*-specific count of the ladder's last column. That sub-analysis's own nominal interval is 25.9–39.0%, and the
clustering correction applied above does not widen it: its design effect is 0.82 rather than
1.42. That is not a reading about the registers. Permuting the liability labels across the 38
junctions gives a design effect of 1.00 on average, a standard deviation of 0.21 and a 95% range of
0.62 to 1.45, so 0.82 is not distinguishable from no clustering at all, while the aggregate 1.42 sits at the top of that same range rather than outside it, so the clustering the aggregate carries is marginal rather than established. A design effect below one would narrow the interval, and the nominal one
is reported instead. Scrambles are the weakest null run here; against the
random-offset chimera null of the next paragraph, the same sub-analysis gives 32.1% against 9.3%. Neither
comparison survives the exon-terminus null two paragraphs below, which returns 28.8% (28.3–29.2%) on
it: the liability attributed to *NR4A3* is no better resolved as specific to the reported
breakpoints than the aggregate is.

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
termini of the same two transcripts — a syntactically valid exon–exon junction, almost always at an
exon pair no patient is reported to carry — gives 40.6% (40.1–41.1%), against 45.8% observed, and
40.5% (40.0–41.0%) when the *NR4A3* exon-3 acceptor that every junction tiled here uses is excluded
from the draw altogether. Almost always, not never: the arm draws both termini freely, so 7.7% of
its 38,000 draws reproduce a panel design's target window exactly and 1.4% land on one of the five
junctions a patient is reported to carry. Excluding those draws moves the arm to 40.0% and widens
the excess from 5.2 to 5.8 points — still inside the observed rate's interval, and in the direction
that runs against this section's conclusion rather than for it.
The parenthetical ranges on every null rate here are Monte-Carlo intervals on the ensemble mean
over 38,000 draws, not confidence intervals comparable to the observed Wilson interval: they
narrow with more drawing rather than with more evidence, and the spread of what 190 designs drawn
from this arm would give is about 3.6 percentage points rather than the one printed — and that 3.6
is itself nominal, since at the design effect of 1.42 above the comparable spread on the observed
side is 4.3 points, against which the 5.2-point excess at ten is about 1.2 standard deviations. The
observed rate's own interval contains both. The liability is therefore a property of joining two exon
termini of these two transcripts, and this panel does not resolve a residual specific to the reported
breakpoints.

Two tighter readings agree with that, and one of them needs no null model at all. Holding the gene
pair, the *NR4A3* exon-3 acceptor and the tiling register fixed, and varying only which donor exon
3′ terminus the donor half ends at (the reported one excluded, so every draw is this paper's own
design rule at an exon pair the disease is not reported to use) returns 44.5% against the 45.8%
observed. That is an excess of 1.3 percentage points — 0.4 of the standard deviation of the count
the null predicts, before any clustering correction, and a junction-cluster bootstrap interval of
−7.3 to +10.0 points. Within the panel itself
the same answer comes off the counts directly: the five junctions a patient is reported to carry
are liable at 44.0%, 11 of 25, against 46.1%, 76 of 165, at the 33 in-frame junctions nobody is
reported to carry — a difference of −2.1 points at a junction-label permutation p of 1.00, and
p ≥ 0.42 at every cut of the ladder above. Both readings cluster on the junction rather than on the
record. What the screen resolves is the gene pair and the splice geometry; it resolves nothing
about where the disease joins them.

The two termini do not contribute equally, and the asymmetry is the informative part. Requiring only
the donor half to end at a real exon terminus leaves the rate at 22.5% (22.1–23.0%), close to the
arbitrary-offset draw and far from the 40.6% both termini give; the whole of the difference appears when the *NR4A3* half is required
to begin at a real acceptor. What the screen is detecting tracks the acceptor boundary of wild-type
*NR4A3* — the transcript the modality exists to spare — rather than the donor consensus.
Two further arms locate it no more finely: holding the six
gap bases and scrambling the wings gives 9.1%, and the mirror gives 8.8%, because a run reaching ten
base pairs needs the real gap and the real flanks together. None of these rates is a significance
test and none is offered as one, and the two tests that are reported above relabel or resample the
38 junctions rather than the 190 records. The 190 records are 176 distinct molecules tiled at overlapping
registers across 38 junctions, so they are not independent draws, and a test treating them as 190
would be wrong about its own denominator.

Nor is any of it a transcriptome-wide rate. Every figure in this section, observed and null alike,
is a rate over 19,921 windows of the 20,011 nucleotides these six mature parents hold — 0.0028% of
the 718,571,139-nucleotide, 186,185-transcript span the exhaustive scan measured (§6, screen 2) —
and the criterion does not survive the enlargement: over that span the same uniform-base arithmetic
predicts about 2.7 × 10³ qualifying sites for any 16-mer whatever, real design, scramble and
chimera alike, so every sequence would meet it. What screen 4 counts is therefore a self-liability
and not an off-target rate (the 85 of 87 above) and for that quantity a six-transcript search is
already exhaustive rather than merely narrow.

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
patient.<sup>26</sup><!--PMID:35488288--> At the *TAF15* seam, functional work has engineered both
the intron-2 cryptic-exon acceptor and the exon-3 one, calling the *TAF15* exon 6 to *NR4A3* intron
2 form the less common of those two.<sup>27</sup><!--PMID:31020999-->

Those acceptors are now designed and screened to the panel's depth, at four seams with a published
exon-resolved breakpoint, each tiled by the same five registers and graded by the same five screens, and every count below is
at the tenfold deeper alignment ceiling — with two exceptions at one seam, both limits of the
instrument rather than properties of the design. Neither the pre-mRNA screen nor the mature-parent
screen carries *PGR* in its parent set: both read the same six genes, and the committed cache holds
no *PGR* unspliced sequence, so that seam's zero in either compartment is an absent reading of its
own donor rather than a clean one. A scan outside the screens closes the mature half, returning no
window of wild-type *PGR* mature transcript within two mismatches of any of that seam's five designs
(`pgr-parent-engagement-noncoding-acceptor.json`); the unspliced half stays unread, and closing it
needs a networked re-fetch of the cache rather than a re-analysis.
Their best available designs are 5′-CAGTGGGCTTCTGCTG-3′ at *EWSR1* exon 7, the type 2 transcript, at
gap-level margin 2 and 51 gap-paired near-matches over 7 loci; 5′-AGTGGGCTCTCCACGG-3′ at *EWSR1*
exon 13, at margin 3 and 25 over 6; 5′-AGTGGGCTCTTGTGTG-3′ at *TAF15* exon 6, at margin 3 and 128
over 6; and 5′-AGTGGGCTCTTCCATT-3′ at *PGR* exon 2, a sixth fusion partner outside the five
modelled here, at a seam reported in a single
patient,<sup>28</sup><!--PMID:36103645--> at margin 3 and 51 over 14 (Table 5). None of the four is
clean. Each of these seams is tiled by five junction-spanning registers and no register at any of
them is clean either, so the least loaded of the four is the least dirty of its own seam's five
rather than a different kind of
result. They are reported beside the panel and never pooled into it, because the grade that excludes
their junctions from the 38 is unchanged. *PGR* carries a further caveat: its design is screened against the non-canonical-acceptor table
rather than derived through the panel's own transcript models. Its transcript accession is given
with the other six in §6, so the design is reproducible even though the panel does not model it.

**Where a design's acceptor half is *NR4A3* sequence that is not exonic in the mature transcript (the
5′ untranslated exon 2, or the cryptic exon within intron 2) the patient's own un-rearranged *NR4A3*
allele carries that same sequence too, sitting behind an intron instead of behind a partner's donor
exon. Some designs therefore pair their whole catalytic gap against that un-rearranged allele, and the mature-parent screen, which reads spliced transcript only, passes the two it can read and never runs on the third, whose cryptic-exon acceptor it cannot address.** This is
the result most consequential for anyone ordering these oligonucleotides. In a fusion transcript that
acceptor sequence follows the partner's donor exon; in the un-rearranged allele it follows *NR4A3*
intronic sequence, so the question is whether the design's donor half matches that intron closely
enough for the whole catalytic gap to pair. For three designs it does: at *EWSR1* exon
13 joined to *NR4A3* exon 2, 5′-CAGTGGGCTCTCCACG-3′ and 5′-GCAGTGGGCTCTCCAC-3′, each pairing across
the wild-type intron-1/exon-2 boundary at two mismatches with neither inside the gap; and at *TAF15*
exon 6 joined to the intron-2 cryptic exon, 5′-TGATGAGGGCCTTGTG-3′, likewise gap-paired at two
mismatches. All three must not be ordered or used, for that reason, and are excluded from every
best-design field above. Both seams keep a reagent, 5′-AGTGGGCTCTCCACGG-3′ and
5′-ATGAGGGCCTTGTGTG-3′, the second's catalytic gap carrying three *TAF15*-derived bases the *NR4A3*
locus does not have and returning no wild-type site at all on the two screens that reach this seam.
Two of the three condemned designs, and the kept one, sit at the *EWSR1* exon-13 seam as
consecutive registers differing only by a single-base slide: the kept reagent,
5′-AGTGGGCTCTCCACGG-3′, is shifted one base 3′ of 5′-CAGTGGGCTCTCCACG-3′ ⚑ and two of
5′-GCAGTGGGCTCTCCAC-3′ ⚑. The third condemned design, 5′-TGATGAGGGCCTTGTG-3′ ⚑, is at the *TAF15*
exon-6 seam and is not a register of that *EWSR1* set — **but it stands in exactly the same relation
to the reagent kept beside it**: it is shifted two bases 5′ of 5′-ATGAGGGCCTTGTGTG-3′, and the
fourteen bases the slide leaves overlapping are identical. Neither condemned *EWSR1* exon-13
register may be ordered in place of the kept *EWSR1* reagent, the condemned *TAF15* exon-6 design
may not be ordered in place of the kept *TAF15* one, and in both cases a slide of one or two bases
is all that separates a reagent from a design this paper condemns. Every seam in this section joins its donor to *NR4A3* exon 2 or to the intron-2
cryptic exon, and none of them to *NR4A3* exon 3: the *EWSR1* exon-13 to *NR4A3* exon-3 reagent of §4.1 is a
different molecule at a different seam.
Of the two kept reagents, 5′-ATGAGGGCCTTGTGTG-3′ is the one not certifiable under the criterion §4.5 states, and §3 carries it only
under that qualification rather than as a cleared reagent: its acceptor is a cryptic exon, which
three of the five screens cannot address at all, so what it holds is a quiet reading on two
instruments rather than a clearance. What is lost is not a
seam but the assumption that designs tiled across one seam are interchangeable.

Two things about that finding matter more than the three sequences. The first is how they were
reached. The mature-parent exclusion had passed two of them, and every other design at their seam;
at the third's seam it never ran at all, on that design or on any other there. That exclusion is a
screen over spliced cDNA and structurally unable to see intronic sequence: a parent screen that
returns nothing at such a seam is the silence of an instrument that cannot look at
the compartment in question. The same three were returned independently by an exhaustive scan of the
*NR4A3* unspliced sequence, by the pre-mRNA screen and by the genome scan, on a fixed known-positive
control that fired on exactly the one design it was required to fire on. The second is what decides
it, because the obvious answer is wrong. It is not the gap-level margin this paper ranks by: the two
condemned *EWSR1* designs carry 2 and 1 donor bases inside the catalytic gap, while a design at the
same seam with a margin of 1 and five donor bases in its gap does not cleave the un-rearranged
allele at all. What decides is how much
donor sequence the gap holds, the rest being acceptor sequence the wild-type allele already carries
verbatim — a property of the donor rather than of the acceptor. The sequence bears it out: *EWSR1*
exon 13 ends
CACTCCGTGGAG against the last twelve nucleotides of *NR4A3* intron 1, CCTTGCCTGTAG, matching at 7 of
12 positions with a shared terminal AG, whereas *TAF15* exon 6 ends ACCACACACAAG and matches at 4,
mismatching in every register — which is why *TAF15* exon 6 joined to *NR4A3* exon 2
returns no such design while *EWSR1* exon 13 joined to *NR4A3* exon 2 returns two. Both are
named here by donor and acceptor together, because *TAF15* exon 6 is also the donor of the
intron-2 cryptic-exon seam above, which is a different seam and does return one. A design must therefore be checked against the acceptor gene's unspliced
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
rather than absent, so it is a candidate at ten and at no cut of eight or below — including the
seven-base-pair end of the range §5 bounds the criterion by, where it joins the liability class. The fourth
design with a clean deep screen, 5′-GGCATATCAAGCGCTG-3′ at the same junction, is excluded by an
eleven-base-pair duplex with wild-type *TCF12* — its own donor parent, not the acceptor.
The *TCF12* exon-7 member therefore differs between the near-match set of §2.4 and the candidate set
here, and the two sequences are consecutive registers of one seam differing by a single-base slide:
5′-GGCATATCAAGCGCTG-3′ is the design §2.4 lists and this screen excludes, and
5′-GGGCATATCAAGCGCT-3′ is the candidate, first screened only at the deeper ceiling. Neither may be
ordered for the other. That is the
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
*TFG* exon 7 at a margin of two with a longest parent run of nine. Those are readings at ten base
pairs, and they are the readings that move most: at the seven-base-pair end of the range §5 bounds
this criterion by, no design at any of the five clears the screen, and at eight, two of the five do.

Both parent-liability classes of §2.5 (the pre-mRNA sites and the mature-transcript duplexes)
were bounded the same way: exhaustive over six parent transcripts and silent about every
other gene. The genome scan, screen 5, removes that bound for the pre-mRNA class alone. It runs at two
mismatches, and a contiguous run of eleven or twelve base pairs inside a 16-mer leaves five or four
positions unpaired respectively, so the
mature-transcript duplexes stay bounded by the six transcripts searched — the same reason §2.5 gives for
their being invisible to the alignment screens.

A raw genome-wide count is not a result at this threshold. Chance alone predicts of order 10³
near-matches per 16-mer over a genome for any 16-mer whatever, so the informative readings are
stratified. Exact 16/16 matches are the class where chance expectation is of order one: 1.37 expected
per design against 236 observed over the 176 designs, or 1.34 each, which is at chance on the mean
and on no individual design: 79 of the 176 return none where that expectation predicts about 45, and
twelve return five or more where it predicts about two, to a maximum of 20. The corpus sits at chance;
the designs are dispersed around it, and a reagent should be read from its own row rather than from
the mean. Load relative to that
expectation separates designs where a total cannot — the median design sits at 0.97 of its
expectation and 14 of 176 exceed twice it. And the repeat split, which a soft-masked reference supplies at no extra cost,
shows 52.5% of hits fully repeat-masked. The baseline that figure needs is not the whole assembly's
51.4%, because a hit can only arise in a window free of ambiguous bases and 151,138,112 windows were
dropped for carrying one; a masked base is never an N, so every masked base survives into the
scanned sequence and the masked share of what was scanned lies between 51.4% and 54.1%. The upper
end of that band is a bound and not a value: a maximal run of *k* ambiguous bases costs *k* + 15
windows, so the dropped-window count over-states the bases removed, and dividing by it over-states
the share. The two figures are also not in the same units — 52.5% is a share of hit *windows* fully
masked, and the band a share of *bases* — and a window is fully masked only when all sixteen of its
bases are, which is rarer than a base being masked. The same-units baseline, the share of scanned
16-mer windows that are fully masked, is not computed here. So the comparison supports no direction
at all: 52.5% falls inside the band, and the two quantities it would be read against are counted in
different units. What can be said is that the hits are not repeat-enriched.

The decisive reading is a lookup rather than a count: does any design have a gap-paired,
strand-agreeing site in *NR4A3*, in a parent gene, or in an *NR4A* paralogue anywhere in the genome?
Twenty of 176 do. No candidate above is among them, and the two secure at any parent-duplex
threshold — 5′-AGGGCATATCGGAGTC-3′ at *FUS* exon 8 and 5′-GGGCATATCCGACATG-3′ at *TAF15* exon 1,
neither of them a reagent of §4.1 — carry a low load: 0.33 and 0.24 of expectation at ≤2 mismatches
against a corpus median of 0.97, and 0.06 and 0.04 for gap-paired sites, each pair given in that
order, the *FUS* design first. These ratios are taken either-orientation against
an either-orientation null, unlike the sense-filtered transcript columns beside them: strand
agreement is applied to the named-target lookup above but not to the load ratio, and for the
*EWSR1* exon-12 reagent 58% of the sites the *gap-paired* ratio counts lie on a strand an antisense
oligonucleotide cannot pair — 156 of its 371 gap-paired sites at two mismatches or fewer are
hybridisable. The stratum has to be named, because the other axis the loads above are given on
returns a different figure: over the ≤2-mismatch set, 437 of 1,062 sites are hybridisable and the
non-hybridisable share is 59%. The two candidates' ranks on those axes, in that same order, 26th and 13th of 176
and 5th and 1st, are reported because the ordering is what the scan supports; the null assumes
independent uniform bases and resolves more-than-chance from at-chance and nothing finer (§5), so
the ratios should not be read as calibrated distances below chance. The third candidate is not quiet
on this axis and its reading is given for the same reason: 5′-GGGCATATCAAGCGCT-3′ sits at 1.46 of
expectation at ≤2 mismatches, 144th of 176 rather than near the clean end, and at 7.0 times
expectation at ≤1 mismatch. That is the strongest statement this work can
make about them, and it is a statement about predicted hybridisation and not about cleavage.

### 2.8 · Expression of the off-target loci

No screen above establishes that a design's off-target gene is transcribed in the organs a systemic dose reaches, and
that discount applies to every count in this paper. Read against reference expression data (Table 6), off-target count and off-target exposure run
against each other at three of the four junctions covered: the design with the heavier gap-paired
load has the less-expressed loci. Exposure is graded at two cuts, 1 and 10 transcripts per million
(TPM), against the three tissues a systemically dosed phosphorothioate gapmer is taken to reach —
liver, kidney cortex and kidney medulla (§6). The fourth, *TCF12* exon 5, runs with its load rather
than against it: its reagent returns the second lightest load of the four, 17 hits resolving to one
locus, and that locus, *PIK3CG*, sits below the lower cut in all three exposure tissues. The single
locus is the reagent's, not the junction's: Table 6 lists twelve at that seam, because its rows are
a union over every tiling register read at a junction and can outnumber the per-reagent counts
below, which are each best design's own. Its
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
reading. The *EWSR1* exon 13 to *NR4A3* exon 3 reagent's two loci are both transcribed at the upper cut in those same
compartments. The *TAF15* exon 6 to *NR4A3* exon 3 reagent's five loci separate the other way: *NRP1* reaches 6.6 to
17.8 TPM across all three exposure tissues and is the only one all five of that junction's tiling
registers return, on five gap-paired hits to a single accession. It is at or above the upper cut in
two of those three, and robustness to register orders the loci differently again — though not
independently of the hit count, since a locus returned by more registers accrues more hits by
construction, and the two still do not order the loci together: *NRP1* leads on register robustness
and sits mid-range on hits, its five records being one accession returned once per register;
the tumour-compartment proxy orders them a third way. What these readings can and cannot decide between two reagents is stated where
that choice is made (§4.1).

### 2.9 · Gap length trades junction specificity against parent-duplex competence

The panel above is one geometry. Tiling the same junctions at 5-8-5 and 5-10-5, wing fixed at five
nucleotides, resolves what a longer catalytic gap buys and what it costs (Table 7, Figure 3).

What a longer gap buys and what it costs are the two halves of one gap, so the trade is exact
rather than approximate — exact as an identity between base counts, which is the whole of what it
is. It fixes how many nucleotides fall on each side of the seam, and settles nothing about the
chemistry those nucleotides carry or about what the enzyme does with them. Inside the gap, the junction-unique
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
11 and *FUS* exon 10 junction, the design carrying that margin sheds its gap-paired
sense-strand matches completely: 123 across the gap at six gene loci become 3 at one locus and
then none, though 20 near-matches remain (Table 7), so it is that risk class and not the load of Box 1
that goes to zero.
Over the six junctions screened at every geometry, designs carrying no such risk rise from 8 of 30 to 28
of 42 to 54 of 54, and the most risk loci on any one design falls from seven to two to none. Part of
that fall is guaranteed by the instrument rather than measured: at a fixed budget of two mismatches,
every locus a longer design can reach is also reached by each of its own shorter sub-windows, so the
reachable set can only shrink as the design lengthens, and two mismatches is a fractionally stricter
test at 20 nucleotides than at 16. Only the size of the fall, and which designs reach zero, are
measurements. The parent-side quantities below carry no such qualification, being computed from the
junction rather than from a search.

Against that, the contiguous DNA a wild-type parent pairs at the same junction rises from 3 to 4 to 5
nucleotides, and the most stable parent duplex becomes more stable, −7.77 to −8.66 to −10.25 kcal/mol. The corpus
shows the same trade. Designs whose parent pairs at least five nucleotides of contiguous gap DNA, the
shorter of the two reported minima for RNase-H1, rise from 76 of 190 to 228 of 266 to 342 of 342 —
those minima being stated for a DNA gap internal to a fully paired duplex, where a parent-paired run
of the same length terminates the duplex at the seam, so meeting the count is necessary and not
sufficient — and
the median most stable parent duplex becomes more stable, −8.66 to −11.60 to −14.58 kcal/mol. At 5-10-5 that count is
every design, and necessarily so, since the larger half of a gap of ten cannot be under five: every
design at that geometry concedes a parent-paired run reaching the shorter of the two minima. At
5-6-5, 114 of 190 designs keep the parent below it. Which minimum is read decides the contrast, and
that is why both are carried: at the six-nucleotide minimum the same series reads 0 of 190, 152 of
266 and 304 of 342, no 5-6-5 design reaching it at all, since a margin of at least one leaves the
parent at most five of that geometry's six gap nucleotides.

A third consequence of a longer gap is counted nowhere in this paper, and it runs against the longer
geometries. Every screen here counts a site only where all gap positions pair, so a single mismatch
inside the gap deletes that site from every count — but a mismatch does not delete the DNA:RNA
hybrid, and how much competent hybrid survives one depends on the gap's length. In a six-nucleotide
gap a mismatch at the third position leaves contiguous runs of two and three, below both of the
minima §6 cites; in a ten-nucleotide gap a mismatch at the fifth leaves runs of five and four, the
longer of which reaches the shorter minimum. Lengthening the DNA gap therefore widens the
RNase-H1-competent window, and the population of imperfectly matched sites the enzyme could still
cleave grows entirely outside what these screens count. That a gap mismatch reduces rather than
abolishes cleavage is the premise this work adopts (§6); how that tolerance scales with gap length is
bounded by no source retrieved for this paper, and the direction of the omission is against 5-8-5
and 5-10-5. It bears on a liability §5 and §6 raise and tie only to affinity and wing content —
sequence-dependent hepatotoxicity — which §5 rightly says this work cannot attribute to a mechanism.
That the mechanism the phrase points at is RNase-H1-dependent cleavage of unintended transcripts is
adopted here as a premise, no source having been retrieved for it; on that premise the axis this
work comes nearest to grading is the one its screens cannot read. The liability is in any case
geometry-dependent in a way the panel does not hold fixed: the wings stay at five locked residues
while the oligonucleotide lengthens, so the locked share of the molecule falls from ten bases in
sixteen at 5-6-5 to ten in eighteen and ten in twenty — 62.5%, 55.6% and 50%. The longer geometries
trade affinity down while trading the catalytic window up, and this paper grades neither axis.

Two liabilities the transcript screens do not reach appear to move the favourable way, and neither
reading survives one fixed criterion. A mature parent can pair
the whole gap for 181 of 190 designs at 5-6-5, 130 of 266 at 5-8-5 and 87 of 342 at 5-10-5, but the
whole gap is a six-nucleotide coincidence in the first and a ten-nucleotide one in the
last, so the three counts are not the same test. Held
to the ten-base-pair criterion applied everywhere else here, the count of liable designs does
not fall: 87 of 190, 88 of 266 and 87 of 342, the two criteria coinciding at a gap of ten
because the gap alone is then already a ten-base-pair hybrid. As a share those are 45.8%, 33.1%
and 25.4%, and the share falls because a longer oligonucleotide has more junction-spanning
registers per seam — five, seven and nine.

Neither framing is the whole reading, and the credit side is a reading at one cut. The liable count
is flat at 87, 88 and 87, and what the extra registers add is choices at a junction rather than a
lower liability per design: at the ten-base-pair criterion the parent-clean designs available at
each junction rise with them, from 2.7 to 4.7 to 6.7 on average — five, seven and nine registers
per junction less 2.29, 2.32 and 2.29 liable ones, so the rise of about two per step is the rise in
registers rather than a fall in liability. That series is not cut-independent, and the cut it is read at
flatters the shortest geometry. Re-derived at the seven-base-pair end of the range §5 bounds this
criterion by, it reads 0.4, 3.6 and 6.7 — and at 5-6-5, 29 of the 38 junctions then have no
parent-clean design at all, against none at 5-8-5 and none at 5-10-5. What a longer gap cannot do is
raise the margin without conceding parent-paired gap DNA, and that is the identity above rather than
a matter of which denominator is chosen.
Designs pairing the gap in
parent pre-mRNA fall from 19 of 190 to 9 of 342, but that arm is a search at a fixed two-mismatch
budget and inherits the nesting bound above rather than the parent-side quantities' freedom from it.
Nor is the effect confined to the longest geometry:
5′-CAGGGCATATCAAGCGCT-3′ at *TCF12* exon 7 returns no near-match at all, where the two 16-mers
surviving at that junction return three and two.

### 2.10 · Duplex thermodynamics and conventional design rules

Scored as free energies (nearest-neighbour values for an unmodified DNA:RNA hybrid, with no locked
or phosphorothioate parameters applied anywhere in this work, §6) — every one of the 190 designs
favours the fusion duplex over the better of the two runs a parent can pair at the junction itself,
by 4.8 to 13.1 kcal/mol with a median of 9.6. The
comparison is to the seam and not to the transcriptome: the mature-parent duplexes of §2.5, which for
87 of the 190 reach ten base pairs or more against a parent (and for 59 of them that duplex is not
elsewhere at all, but runs past the seam into the wild-type *NR4A3* exon-2/exon-3 junction the
acceptor half already meets) are not scored here. Every
design favours the fusion because a parent pairs roughly half the oligonucleotide, and half a duplex is
much the weaker one. That separates two things a base count conflates. The *difference* in binding free energy is not
marginal here. That is not the same as saying binding discriminates: what would decide that is
whether a parent seam is occupied at the exposure concentration, which depends on the modified
duplex's absolute stability and is not computed anywhere in this paper (§6). Two things therefore
remain unresolved rather than one — occupancy at the binding step, and discrimination at the level of
*catalysis*, where RNase-H1 requires a DNA:RNA segment within the gap and where a mismatch in it
reduces rather than abolishes cleavage by a factor the literature bounds at one- to five-fold. The thermodynamic result narrows neither; it orders them.

The two rankings agree in direction. Grouping designs by the gap-level margin the Methods (§6) define,
the mean of that free-energy margin (written ΔΔG°37 and computed as ΔG°37 of the better parent run
minus ΔG°37 of the full fusion duplex, so that it is positive where the fusion duplex is the more
stable of the two and larger is better) rises monotonically with it, from 8.3
kcal/mol at margin 1 to 9.9 at margin 2 and 10.7 at margin 3. That agreement is arithmetic rather
than corroboration: the design's own seam hybrid (the run either
parent shares with it at the junction itself, which is not the screened parent duplex of §2.5 and is
not searched for anywhere else in the transcriptome) is exactly 11 minus the gap-level margin for all
190 designs (11 being one wing's five bases plus the gap's six, so the longer of a design's two seam
runs is a whole wing plus whatever of the gap the margin leaves) so the free energy is largely
ordering that same length in kilocalories. Largely, because the identity is on the longer run while
the free energy is taken against the more stable one, and for 6 of the 190 that is the shorter side:
all six sit at margin 2, where the two runs are nine and seven bases and the seven-base run is the
more stable of the pair. That run is taken by
construction and never extended outward, so it is a minimum: where a parent's next base beyond the
seam happens to match, the real hybrid is longer and more stable than the one scored, and the margin
reported for that design is correspondingly generous. The §2.5 screens do not recover those cases,
since they retain only sites pairing the whole gap. What it adds is the
size of the difference; it is not purely a restatement of the margin, because composition reverses
the order in 19.9% of cross-margin design pairs and the margin-3 range sits inside the margin-1
range, and the same caution applies to the margin's agreement with the parent screens of §2.5.

Conventional design rules select differently, and against three of the designs this paper calls
candidates — though not against the two lead reagents of §4.1, which fail no rule (a narrower clearance than it
reads, for the reason two paragraphs below); the *EWSR1* exon-13
reagent §4.1 adds for coverage fails two. Of the 190
designs, 106 satisfy all four rules; the rules bind at different rates, with every design free of a
G-quadruplex motif but 13 carrying a homopolymer run of four or more, 43 a CpG dinucleotide and 58
falling outside the 40–60% GC window. The failures overlap, so they do not sum to the 84 designs
that fail at least one. The 13 with a homopolymer run are neither base-neutral nor spread across the
molecule: five carry a guanine run, five a thymine run and three an adenine run, none a cytosine
run, and all 13 come from three junctions — *EWSR1* exon 15, *TFG* exon 4 and *TAF15* exon 8. Every
one of those runs sits at the 3′ end, six of them wholly inside the 3′ locked wing and seven
straddling the gap and that wing; none lies in the 5′ wing and none is confined to the gap. The quadruplex column passes everything because of what it asks: four separate runs of
two or more guanines, which a 16-mer of this composition has little room to carry. The guanine
feature that is present is a different one. A run of three or more guanines is carried by 118 of the
190, at the 5′ end in 38 of them — one register per junction, including both lead reagents of §4.1 —
and four registers of the *EWSR1* exon-15 junction carry a run of five, which the homopolymer rule
catches and the quadruplex rule does not. A clean quadruplex column is therefore not a statement
about this panel's guanine content, and the two should not be read as one.

Where that 5′ run sits is a fact about the chemistry and not only about the sequence. Both lead
reagents of §4.1 begin 5′-GGG, and at 5-6-5 with a five-nucleotide wing those three guanines are
positions 1 to 3 of the 5′ locked wing: a contiguous locked G-tract, not a DNA one. This work adopts
as a premise that a contiguous guanine run inside a locked wing carries synthesis, aggregation and
melting-temperature consequences distinct from the ones a homopolymer rule written for unmodified
DNA is aimed at; no source retrieved for this paper bounds them, and nothing here measures them.
What the audit can be held to is what the audit reads: each of the four rules is computed from the
base string alone and none of them takes the sugar or the backbone as an input, and the 5-6-5,
5-8-5 and 5-10-5 geometries are the 2′-O-methoxyethyl convention rather than a locked one (§6).
Passing all four is therefore a DNA/MOE rule set returning clean on a locked molecule, and it is not
a chemistry clearance.

The disagreement is sharpest where it matters most. Of the nine designs with no sense-strand
near-match (Table 4), exactly one satisfies all four rules. Seven contain a CpG dinucleotide; four fall outside the 40–60% GC window — the three *EWSR1*
exon-1 designs above it at 62.5% and 5′-GGGCATATCTCTATAA-3′ below it at 37.5%.
The CpG rule is applied position-blind, and this architecture argues in two directions at once. The
canonical immunostimulatory motif is a CpG in sequence context rather than a bare dinucleotide, and
only the six-nucleotide gap of a 5-6-5 gapmer carries an unmodified sugar, the wings carrying a 2′
modification at every position — but that gap is phosphorothioate DNA rather than unmodified DNA,
and a phosphorothioate backbone is the feature that makes an oligodeoxynucleotide a competent ligand
for this receptor at all. One consideration lowers the prior and the other raises it; neither is
measured here. Whether a CpG inside a locked wing is recognised at
all is not established here and no source is cited for it, so the audit is left position-blind and
the reading below is stated as the direction the architecture argues for rather than as a result. Only
5′-CAGGGCATATCTTGCA-3′ at *TCF12* exon 9 passes every rule — and it is a do-not-order design, ⚑ in
Table 4, pairing wild-type *NR4A3* itself through the whole catalytic gap at twelve base pairs, which
is this section's disagreement at its sharpest: the one molecule conventional triage clears outright
is the one this paper's central screen condemns. The multi-partner lead reagent
5′-GGGCATATCATCAAAC-3′, which is not among the nine, also passes all four. The cleanest designs this
work found are, with one exception, molecules conventional triage would flag, in six of the seven
cases for a CpG that reaches into the catalytic gap, which is the stretch the argument above says
the rule would bite on if it bites anywhere. Removing such a motif by base substitution would change
one of the bases the gap-level margin is computed on; 5-methylation of the gap cytosine would remove
it at no cost to the margin at all, and §6 specifies the gap cytosines as unmethylated precisely so
that this audit reads as written rather than as a question about a vendor's default. Both are
reported rather than composed into a single score.

## 3 · Discussion

Designability is not the constraint. Junction-spanning designs exist at every in-frame NR4A3
fusion junction, though at three of them every design pairs a wild-type parent through the catalytic
gap — three at ten base pairs, 29 at seven, and 32 at any length, which is the same cut dependence
§2.5 states and the reason none of these counts is quoted without it.
On the one existence statistic tested, no partner is uniformly clean or uniformly dirty: with
all 38 junctions screened, four of the five partners
have a junction whose cleanest design carries no sense-strand near-match across the gap at the
deeper ceiling, and all five do at the default one. The exon a fusion breaks at therefore bears on
whether a design is clean across the gap in that sense, and not the gene alone — though no test of
a partner effect was run, and *TFG* sits higher on the genome-wide load on an axis confounded with
base composition (§2.3),
and the count
of such junctions is itself a
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
The two parent compartments of §2.5 sharpen that rather than softening it. For nine designs of the
panel (a different nine from the nine of Table 4 discussed above), the route
to wild-type *NR4A3* is not a gap-level discrimination problem at all. Those nine pair the catalytic gap in
full across the wild-type intron-2/exon-3 boundary, at two mismatches that both fall in the locked-nucleic-acid (LNA) wing,
and the compartment such a duplex would form in is the nuclear one RNase-H1 occupies. That the site
exists is not that the duplex forms: pairing the whole gap forces both mismatches opposite locked
residues, where destabilisation is largest and where no penalty is modelled anywhere in this work
(§6), so these counts are an upper bound on hybridisation. None of
Table 4's nine carries such a site of the strict class §2.5 defines, and that section is silent on
whether any sits in the wider sense-strand forty. In
mature parent sequence 87 designs pair a wild-type parent (any of the six, not *NR4A3* alone,
which 61 of them pair) over a contiguous duplex of at least ten base pairs. The general point is that a fusion-junction design's most
plausible wild-type liability is its own parent, reached either across a splice junction or in the
mature transcript, and both are invisible to a screen that ranks candidates by global identity. A
third compartment is invisible to all of them: at a seam whose acceptor half is not exonic in the
mature transcript, the patient's own un-rearranged *NR4A3* allele carries the same sequence behind an
intron, and three designs the mature-parent screen clears or cannot read — the pre-mRNA screen
returned all three, as §2.6 reports — pair their whole catalytic gap there.
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
at real exon termini of the same two transcripts, almost always at junctions no patient is
reported to carry, meets
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
arm is reported there, so the double deletion is shown to be sufficient and is not shown either
way on necessity. On the
restrictive side, a separate study makes the loss of *NR4A3* consequential rather than silent when
paralogue reserve is reduced: mice hypoallelic across the two genes develop a myelodysplastic or
myeloproliferative neoplasm.<sup>31</sup><!--PMID:21205929--> That same source restates, from an
earlier report of its own authors rather than as a finding of its own, that abrogation of both genes
leads to rapid postnatal leukaemia; it is cited here as a restatement and the earlier report was not
retrieved. The family is also not uniform in direction — within
atherosclerosis, NR4A1 and NR4A2 attenuate lesion formation while NR4A3 aggravates
it<sup>32</sup><!--PMID:24005216--> — so paralogue redundancy cannot be assumed to be
substitution.

Three limits on that reading matter more than the reading itself. Every source cited here is
haematopoietic or vascular, and none addresses the tissue an EMC arises in; two of the four are
reviews rather than primary reports; and the perturbation described throughout is germline or
conditional gene deletion, which is a different and more complete perturbation than
partial, reversible, dose-limited knockdown by an oligonucleotide. The honest position is therefore
that wild-type *NR4A3* knockdown has an unquantified cost that is probably not zero and probably not
catastrophic, and that the case for junction selectivity does not rest on it. It rests on the donor
side instead, on the premise that knocking down the FET donors *EWSR1* and *TAF15* costs more than
knocking down the two non-FET partners of §2.3, *TCF12* and *TFG*. That premise is adopted here and
is not established here: this paper cites no essentiality measurement for any of the four donor
genes, and nothing below rests on the contrast holding. What does not depend on it is the failure
mode, which is the same whichever donor a design sits at: a
reagent cleaving a parent transcript is failing at the one thing that distinguishes this modality
from knocking down *NR4A3* directly, which requires no junction at all. A design that cannot spare
the parents has no advantage left to trade.

Free-energy calculation does not narrow the interval either. Every design shows a large free-energy
*difference* against the parent runs it meets at the seam, but that difference is not occupancy: no
modified-duplex stability was computed for any parent seam, so the binding step is unresolved
alongside the catalytic one rather than settled ahead of it (§6). Two things could narrow that interval, and no further sequence analysis is either of them: a
measurement, or a physics-based estimate of cleavage geometry on the RNase-H1·heteroduplex complex,
for which experimental structures exist. Neither is attempted here. Gap length is not a third, for
the arithmetic reason §2.9 gives: a longer gap buys a markedly quieter transcriptome while at the
same time pairing more of one wild-type parent through the gap. The two are not one effect: the
transcriptome quiets because at a fixed two-mismatch budget a longer design can reach no locus its
own shorter sub-windows do not, so the reachable set only shrinks, while the parent duplex grows
out of the gap identity itself. It is the same limit reached from the other side rather than a way
around it. The field's own answer to poor single-base discrimination has been
positional chemical modification of the gap rather than
length,<sup>33</sup><!--PMID:23963702--> and that is the design direction this result points to, now
for a demonstrated reason rather than by analogy. A steric-block
mechanism, which does not require gap-level discrimination, is a second alternative this work does not
evaluate. It is also an ungraded liability and not only an opportunity: the wild-type *NR4A3* 3′
splice acceptor that §2.5's pre-mRNA class concentrates at can be occupied with no catalytic gap
paired, and what that would do to wild-type *NR4A3* is outside every screen reported here (§5).

Delivery remains unsolved for a tumour, and separates into three routes with different
requirements. A characterised EMC-enriched surface antigen is a prerequisite of
the systemic receptor-targeted route only; local and inhaled administration require none. No such
antigen could be named when the question was put to the disease's own tissue: of the twelve candidate
surface antigens for which both a lineage reading against comparator sarcomas and a measured EMC
tumour-versus-normal-organ contrast exist (the latter from four EMC and 27 normal-organ libraries
across six organs in Gene Expression Omnibus (GEO) deposit GSE28866) three cleared both measured axes, and none
cleared those two axes and a wider prior on normal-tissue distribution together. *CD44* and
*CSPG4* cleared the two measured axes and were then refused by that prior; *RET* cleared the same
two and carries no reading against the prior, so it is ungraded rather than excluded; the other
nine did not clear both measured axes. That bounds what was examined
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
epithelium or alveolar parenchyma, which is the compartment inhalation naturally reaches. A
hypocellular, matrix-rich sarcoma nodule sitting within that parenchyma is not. Inhaled delivery to lung tumours is an active
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
consequence is narrow and is the only one this paper draws: no reagent named here can be assumed
testable in that line on current evidence, and its junction would have to be established by RNA
sequencing first, as §4.4 requires of any test article. A filtered caller's silence bounds detection
at a sensitivity nothing here quantifies, and an absent reading is not a reading of absence. This is not a statement that the line is misidentified, nor a statement about what the line is
instead. It carries a short tandem repeat profile concordant across three independent sources at
every locus but one (D13S317, recorded as a single allele by one source and as two by the other
two), and no problematic-line flag. Fusion-negative EMC tumours are
themselves a recognised minority category: of eight extraskeletal myxoid chondrosarcomas in one
series the fusion transcript was found in six, and two carried neither a fusion transcript nor a
genomic rearrangement of either partner,<sup>36</sup><!--PMID:9060841--> against a later report
stating that more than 90% of these tumours carry an *NR4A3*
rearrangement.<sup>37</sup><!--PMID:36316541--> Absence of the fusion is therefore not by itself a
reclassification. The observation is also not new: it is in print in one figure legend and is carried
as a caution field in the reference registry. No retrieved source examines it as a subject, and it
is not discoverable by anyone searching on model validity. Both halves are released: the fusion-caller,
expression and registry readings in `emc-atr-vulnerability.json`, which owns them, and the reading of
that figure legend together with the reagent consequence in `emc-model-junction-evidence.json`.

What remains is five test articles. Each of the five has a reagent at its junction, but one of
those reagents — the cryptic-exon one below — is not certifiable under the criterion §4.5
states, so the reagents matched to a test article are four that all five screens can be run on and a fifth carried under that qualification — a different set from the four of the coverage ladder in §4.1, overlapping it in two members. Addressable by all five is not cleared by all five: within the 38-junction panel the designs that clear every screen are the three of §2.7, and the two of those four that §4.1 names carry the off-target loads §4.3 reports. Three are the
engineered constructs of the functional study cited above,<sup>27</sup><!--PMID:31020999--> E-N,
T-N* and T-N, whose exon spans that paper states verbatim; two of the three, E-N and T-N*, carry the
same two junctions the reagents of §4.1 span — *EWSR1* exon 12 and *TAF15* exon 6, each joined to
*NR4A3* exon 3 — so both of those reagents have a stated test article; the third construct, T-N,
carries the intron-2 cryptic-exon seam of §2.6, whose reagent
cannot be certified under the criterion §4.5 states, three of the five screens being unable to
address a cryptic-exon acceptor at all. The other two
are the patient-derived, identity-clean models reported with two EMC
tumours,<sup>37</sup><!--PMID:36316541--> USZ20-EMC1 (RRID:CVCL_C6MX) and USZ22-EMC2
(RRID:CVCL_C6MY), whose fusions are reported as *EWSR1* exon 13 and *TAF15*
exon 6 joined to *NR4A3* exon 2 rather than exon 3; reagents exist at both acceptors, so each line
has one under either reading of that exon label.

The two sources of a test article are not interchangeable and their limits run in opposite
directions. Rebuilding the constructs is the faster of the two and the only one whose critical path
contains no laboratory that has to answer an email, since the junction is specified by construction. It is not unconditioned: the
published recipient background is a catalogue item supplied under a material transfer agreement, and
every plasmid carrying the published retroviral backbone that could be read here is distributed to
academic institutions and non-profits only, a restriction that binds before any price does. What it cannot buy is
biological relevance: a complementary DNA over-expressed in a heterologous background is not the
disease, so such an experiment could speak to junction-selective knockdown of the intended
transcript and not to activity at endogenous expression from an endogenous locus. The published
recipient background is in no cell-line registry either, so a rebuild would sit in a different
background from the original — an isogenic mismatch to declare rather than gloss. The
patient-derived models are the only source of a fusion-positive EMC cell, and are available on
request from the originating laboratory with no repository deposit; what a transfer requires is
stated nowhere that could be read, which is an absent statement rather than an absence of
conditions, and the cells are slow once received, at reported doubling times of five to six days as
sarco-spheres passaged every two to three weeks, which constrains any exposure window. One further
reported line — the one whose distributor could not be read, above — cannot serve as a test article
at all on current evidence, because its fusion partner and exons are unstated anywhere readable and
it would have to be sequenced first. One constraint
sits above all of them and no reagent choice moves it: every one of these sources ends at someone
culturing cells, so the rate-limiting step is a laboratory rather than a line, a construct or an
oligonucleotide. §4 opens on what that means for this work.

One deliverable does not wait on that. No named reagent reaches every patient, and the released
design and screening pipeline is the paper's second output: §4.5 states what it takes as input, what
it does with it and what its result is worth, which is a candidate rather than a validated reagent.

## 4 · Reagents, controls and the falsification experiment

**This work has no laboratory.** Nothing specified below has been performed, and the rate-limiting
step for all of it is a laboratory rather than a line, a construct or an oligonucleotide (§3). What
follows is a specification for someone else to run, not a report of a result.

This section is the paper's output for a laboratory. It names six things: the oligonucleotides to
make, the arm that separates the two ways a weak result could arise, the predicted off-target load
each carries, the controls without which the readout does not mean what it appears to mean, the
number that would falsify, at its top margin, the ranking every candidate here is ordered by, and — for the patients no
named reagent reaches — the released procedure by which a candidate can be designed for a breakpoint
outside this panel. Nothing in it is a claim of efficacy. No sequence named below has been
synthesised or tested.

### 4.1 · The reagents to synthesise, and their population coverage

The experimental design that would resolve the central uncertainty — an isogenic
fusion-positive/fusion-negative comparison — has been published in an
analogous disease, though with a single-dose knockdown readout rather than the matched dose-response
and wild-type-parent measurement §4.4 requires. Fusion-specific antisense oligonucleotides against *NAB2::STAT6* in solitary
fibrous tumour, evaluated against CRISPR-engineered isogenic fusion-positive and fusion-negative
cells, reduced fusion expression by 58% and proliferation by 22% in
vitro.<sup>38</sup><!--PMID:37370737-->

**Research use only.** Both sequences named in the next paragraph, and every sequence in Tables 2
and 5, are research reagents for laboratory investigation only. None is a medicine or a candidate
drug, none has been synthesised or tested, and none may be administered to any human being or
animal or supplied to anyone for that purpose. Ordering any of them from a commercial synthesis
service is possible for anyone; doing so does not make it a treatment, and nothing in this manuscript
should be read as licensing use in a patient. Do not order an oligonucleotide by copying it out of this
PDF — use the canonical `fusion-junction-aso-sequences.csv` or `.fasta` (§6) — and do not order at all
until the breakpoint of the cell line or patient sample has been established at nucleotide resolution
by RNA sequencing (§4.4).

Applied here, the reagents to synthesise are the best available at the two most frequently reported
junctions with a published exon-resolved breakpoint (Table 2): 5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 and
5′-GGGCATATCTTGTGTG-3′ at *TAF15* exon 6. Both hold the top gap-level margin of 3, and neither pairs
a parent through the catalytic gap at the ten-base-pair threshold, though both sit close to it: the
*EWSR1* reagent's longest parent run is eight base pairs and the *TAF15* reagent's nine, both
against wild-type *TFG*. Where the criterion is set therefore decides how these two reagents read,
and the reading is not favourable across the range §5 bounds it by: at a cut of eight both would
fall inside the class Box 1 marks do-not-order, at nine the *TAF15* reagent alone would, and only at
ten does neither. The panel moves with them — 143 of the 190 designs pair a wild-type parent through
the whole gap at a cut of eight, 98 at nine and 87 at ten. One of the two carries a second liability
no transcript screen shows, and it belongs beside the sequence rather than two subsections later:
the *EWSR1* reagent has a sense-strand near-match in wild-type *TAF15* precursor RNA at two
mismatches, one of them inside the catalytic gap, spanning an intron–exon boundary (§4.3); the
*TAF15* reagent has no sense-strand pre-mRNA site at all. The first also tests the multi-partner prediction, against a synthetic
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
is a composition no pooling rule for proportions applies to. Four bounds sit on it, and they run
in different directions. The interval is wide for the denominators rather than the estimate: taking
each breakpoint fraction to its own Wilson bound spans 39.9% to 82.8%, the *EWSR1* arm resting on 15
tumours and the *TAF15* arm on three. **That interval propagates the breakpoint fractions only.** The
partner shares are held at their point estimates, and their own Wilson intervals are 67.2–87.7% for
*EWSR1* and 8.4–26.9% for *TAF15*, so an interval that varied all four quantities would be wider
than the one reported. Wider, but not reachable by composing them: taking all four quantities to
their upper bounds at once returns 101.4% of cases covered. The reason the composition cannot be
repaired rather than widened is that the two partner shares are cells of one multinomial, whose
Wilson upper bounds sum to 114.7% on their own — a note on how the interval is built, not a second
attempt at the coverage figure. What is reported is therefore a
composed-endpoint range carrying no nominal coverage level, and not a confidence interval. The third decimal is not resolved by the data behind it: the *TAF15* arm is
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
with no distribution: one *TCF12*-rearranged tumour has ever been sequenced at this junction, no
breakpoint series retrieved here contains a *TCF12* tumour at all, and the break-apart assay the
later cohorts used
locates no seam within the *NR4A3* locus, so recurrence there is untested rather than refuted.
Table 5's top figure, 98.3%, is an upper bound rather than a reachable target for two reasons and not
one: that *TCF12* arm is priced at its ceiling, worth 3.4 percentage points, and the figure also
assumes every remaining *EWSR1* breakpoint covered, which is the larger of the two steps at 15.9
points and needs three further reagents the retrieved record does not resolve to an exon (Table 5).
One fact about the screened set is invisible in the ladder, which prices rungs rather than counting
seams: every junction with a published exon-resolved breakpoint in the retrieved record now carries
a screened design, the five in this panel (§2.7) and the four *NR4A3* exon-2 acceptor seams of §2.6,
of which Table 5 carries three under its own “beside the panel” label and the fourth as a coverage
rung, reported
beside it (§2.6). Eight of those nine designs are taken through all five screens. The ninth, at the
*PGR* seam, is graded on three of them, and two screens miss it rather than one: the mature-parent
screen and the pre-mRNA screen read the same six-gene set of parent sequence, which does not carry
that donor, so neither of that junction's parent compartments is read by the screens, for the
reason §2.6 gives. The mature half is closed outside them by the scan §2.6 names, which returns no
wild-type *PGR* window within two mismatches of any of that seam's designs; the unspliced half is
unmeasured rather than clean. That is a statement about how far the screening reached
and not a coverage figure, and it displaces nothing above it: how many patients a reagent set
reaches is the ladder's question, priced on the single series behind it. The Supplementary
Information (SI) §S6 carries the rest
of the ladder's bookkeeping — the count of those seams, a second basis that prices them on the
pooled breakpoint record, which SI §S6 states is two of seven retrieved series and not the whole
one, and the four that move the figure by nothing at all.

The *EWSR1* exon-13 to *NR4A3* exon-3 reagent should not be recommended on its transcriptome count, because the two
axes that separate it from the exon-12 reagent point in opposite directions and only one of them
bears on where an effect would land. On count it is the lighter of the two, 24 gap-paired
near-matches at 2 loci against 123 at 6. On exposure it is the heavier: both of its loci are
transcribed at the upper cut in the organs a systemic phosphorothioate gapmer distributes to, where
none of the exon-12 reagent's measurable loci is (§2.8, Table 6). For a laboratory choosing between
them, the exposure reading is the one that speaks to the question a count cannot: a locus matched
but not transcribed in the organs a systemic dose reaches has no route to an effect, whereas the count says only how
many gap-paired windows the screen returned there. Neither axis is a risk ranking, and this comparison
does not make the exon-12 reagent the safer molecule. Every hit behind both is a 14 of 16 match, no screen
here predicts cleavage at any of them because all five grade hybridisation only (§5), and an
expressed gene is necessary and not sufficient for an effect. The reason to make the *EWSR1* exon-13 to *NR4A3* exon-3 reagent is coverage, and it is unaffected by either axis.

Two risks attach, in this order. The first is architectural, and the Methods (§6) disclose it. A
six-nucleotide gap supports noteworthy but incomplete RNase-H1 activity where seven to ten are
reported as optimal,<sup>39</sup><!--PMID:24981949--> so weak knockdown is at least as likely to be
the gap as the sequence. That risk is now addressable by a named second reagent rather than by a
caveat.

### 4.2 · A second geometry as a gap-length control

5′-AGGGCATATCATCAAACC-3′ is the 5-8-5 design at the same *EWSR1* exon 12 junction. It spans the same
three partners' breakpoints and sits inside the reported activity optimum. It holds a gap-level
margin of 4 where the 16-mer holds 3, and carries 3 sense-strand near-matches across the gap at one
gene locus, against the 16-mer's 123 at six (§2.9, Table 7).

Synthesised alongside the 16-mer, at one extra oligonucleotide and one extra well per condition, it
separates the two explanations a weak result would otherwise confound. A 5-8-5 arm that knocks down
where the 5-6-5 arm does not attributes the failure to gap length rather than to sequence, though
only if occupancy is held equal: the longer arm is also a longer perfect duplex against the fusion,
so a positive result is consistent with better cleavage competence or simply with the fusion duplex
being occupied where the 16-mer's was not, and this pair does not separate those. What it
does not buy is parental sparing, since the same two nucleotides lengthen each parent's contiguous
duplex from 3 to 4 nucleotides of gap DNA and its whole contiguous hybrid at that seam from 8 to 9
base pairs, and drive its free energy from −7.77 to −8.66 kcal/mol. Its longest mature-parent duplex through the
whole gap does fall from 8 base pairs to none, but 8 sits below the ten-base-pair threshold applied
throughout, so neither design counted as a mature-parent liability at this seam and that fall removes
nothing the screens had counted at ten. That reading has to be stated with its other half, because
the cut is used in both directions in this paper and must not be used in whichever direction
enlarges the negative: at the seven-base-pair end of the range §5 bounds the criterion by, the same
fall removes a duplex that does count, and it is the same dual reading Box 1 and §4.1 apply to the
two lead reagents' own runs of eight and nine. Both arms therefore need
the fusion-negative comparator below.

### 4.3 · The predicted off-target load of the two lead reagents

The second of the two risks §4.1 names is transcriptome load, and it differs sharply between the two
leads. The *EWSR1*
exon-12 reagent carries the heavier load of the two: 123 gap-paired
sense-strand near-matches at the deeper ceiling, recounting to six gene loci, all at the screen's
loosest admitted identity and none on a parent transcript (§5). It is not the heaviest in the
panel — fourteen of the 187 design records re-screened at that ceiling carry more, to a maximum of
240 at *TCF12* exon 3. Table 3 prints one row per junction rather than one per design record, so
those per-record counts are in the released screens rather than in a table. The *TAF15* reagent
carries 8 such near-matches at five loci.

The parent compartments qualify that, in a way the transcript screens cannot show. The *EWSR1*
reagent carries a sense-strand intron–exon-spanning near-match in wild-type *TAF15* pre-mRNA at two
mismatches, one of them inside the catalytic gap, returned independently by the pre-mRNA screen and
the genome scan. It falls outside the headline parent counts, because those require the gap to
be paired in full; it sits inside §2.5's wider tallies, among the 53 with a pre-mRNA near-match, the
forty on the sense strand and the 21 that pair all of the gap but one or two positions. By the bounds
adopted above a single gap mismatch does not abolish cleavage.
It is the multi-partner result's own cost rather than an incidental hit: the ten donor bases shared
across *EWSR1*, *TAF15* and *FUS* that let one oligonucleotide span three junctions are the bases that
place it against wild-type *TAF15*. The *TAF15* exon-6 to *NR4A3* exon-3 reagent carries no sense-strand pre-mRNA site
at all, which is a second respect in which the two separate on something other than count.

That load should travel with the reagent. It is a liability to disclose and to control for rather
than a disqualification, because on the genome scan the same design sits at chance in both
directions that matter: 0.69 times the expected number of near-matches at two mismatches, against a
corpus median of 0.97 on that axis, and 0.62 times the expected number of gap-paired ones, against a
corpus median of 0.82 on that one. The two medians are different quantities and only the first is
0.97, so each ratio is read against its own (§2.7). The null
behind those ratios assumes independent uniform bases and separates more-than-chance from
at-chance and nothing finer (§5), so the scan neither aggravates the load nor exonerates it. Expression separates the two reagents the other way
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
every design here is specific to the exon pair or pairs it was tiled at — nine span more than one
(§2.2) — and none is valid for an unverified junction.
Routine diagnosis does not supply it: break-apart *NR4A3* fluorescence in situ hybridisation is the
preferred single assay because it detects any rearrangement "irrespective of
partner",<sup>6</sup><!--PMID:41055792--> so on its own it does not locate the seam, and the 58-case
cohort every coverage figure here is denominated on was identified that way, with RNA exome
sequencing applied to three of its cases.<sup>9</sup><!--PMID:36948401--> That cohort reports a
partner for 57 of its 58 tumours, so partner assignment there rests on more than the break-apart
assay; what no part of that workflow supplies is the exon pair.

Three assay controls are required, and a knockdown assay alone distinguishes none of them:

- a positive control gapmer against an abundant housekeeping transcript in the same cells, to
  separate failed delivery from a test reagent that reached its target and did not cleave it. It must
  be of the same 5-6-5 β-D-oxy-LNA phosphorothioate geometry as the test articles, so that only the
  target sequence differs: a catalogue control of another chemistry or another gap length — a 5-10-5
  2′-O-methoxyethyl gapmer, say — establishes neither that a 5-6-5 was delivered on comparable terms,
  since uptake and endosomal release track chemistry class and phosphorothioate content, nor that a
  six-nucleotide gap can direct cleavage in these cells, which §4.1 names as this panel's first risk.
  It says nothing about discrimination, which is fusion-versus-parent selectivity and is what the
  fusion-negative isogenic comparator below is for. §4.2's gap-length arm is not that control: it
  separates gap length from sequence as explanations of weak knockdown, and §4.2 states that it buys
  no parental sparing, both arms needing the comparator too;
- a scrambled gapmer of the same 5-6-5 β-D-oxy-LNA phosphorothioate chemistry and geometry as the
  test article, and composition-matched to it — dinucleotide-preserving, so that GC fraction, total
  guanine content and the 5′ run are held as well as base composition, since a scramble differing in
  those differs from the test article in melting temperature, protein binding and aggregation as well
  as in sequence. What it separates is the backbone-class component of toxicity and not the whole of
  it: §6 records that the relevant liability of high-affinity gapmers is sequence-dependent, and a
  scramble cannot by construction control for a sequence-dependent effect. The scramble actually
  ordered must itself be put
  through the mature-parent screen before it is made, because on this paper's own null 6.2% of
  scrambles pair a parent's whole catalytic gap at the ten-base-pair criterion and 1.8% do so
  against wild-type *NR4A3* (§2.5), which is the one transcript a control must not engage. That
  6.2% is a mean over 190 windows, and the per-window rates should not be read as window properties:
  each rests on 200 draws, so its standard error is 1.7 percentage points, and the observed spread of
  2.0% to 15.0% is close to what 190 windows of 200 draws from a single common rate would produce.
  Nine molecules are tiled at two or three junctions with an identical target window, and their
  repeated estimates disagree by up to 8.5 percentage points, which is the size of that noise. There
  is real between-window variation underneath it — the dispersion ratio is 1.61 on 189 degrees of
  freedom and the between-window standard deviation is about 1.3 percentage points — but it is
  smaller than the range suggests, so the screen is required for every scramble rather than for the
  windows that happen to have drawn high. Two things decide whether that screen
  answers the question. The sequence to screen is the *target window*, the reverse complement of the
  oligonucleotide ordered, because screen 4 searches the sense strand only (§6): screening the
  antisense sequence directly searches the wrong strand and returns a false pass. And the rejection
  rule is the paper's own criterion — redraw the scramble where a wild-type parent pairs its whole
  catalytic gap over ten base pairs or more, wild-type *NR4A3* above all, since a control that
  engages the transcript the modality exists to spare is not a control. What a passed scramble is
  then clean at has to be said with it: it is clean at ten and not below it. Read at seven, the same
  null returns 74.3% of scrambles pairing a wild-type parent's whole catalytic gap and 23.9% doing
  so against wild-type *NR4A3*, so passing this rule certifies the criterion applied throughout this
  paper and does not certify that the control spares the parents;
- a fusion-negative isogenic comparator, since wild-type *NR4A3* may be too weakly expressed in an
  EMC line for the selectivity readout to be defined at all.

The test articles can be ordered from this paper. The experiment cannot, and the gap should be read
before it is budgeted rather than discovered at the bench. Two of the three controls are named as classes rather
than as molecules. No target transcript and no catalogue item is named for the positive control,
which must carry the test articles' own 5-6-5 β-D-oxy-LNA phosphorothioate geometry and is therefore
a custom synthesis rather than a shelf reagent; and the scramble is a sequence a laboratory has to
draw against its own test article's dinucleotide composition and then put through the mature-parent
screen before ordering, so it does not exist until that is done. The third is not a molecule at all,
and this paper names no supplier of one: a fusion-negative isogenic pair has to be engineered, and
only the construct route of §3 supplies one, in the recipient background those constructs are
expressed in. Neither patient-derived model of §3 has a fusion-negative counterpart reported or
sourced anywhere here, so that route runs without this control unless one is built by excising the
fusion from lines whose reported growth rate §3 gives — a project rather than a control. No
assay is prescribed either — not the quantification platform, not the wild-type amplicon placement,
whose two options are set out below and bias in opposite directions, and not the normalising
reference, which the next paragraph constrains without naming. What this
section fixes is the reagents, the arms, the reporting requirements and the threshold; what it
leaves to the laboratory is the assay and the two control molecules.

Two limits of that set are invisible within it. The normalising reference transcript must be neither
the positive control's target nor either transcript measured, or the positive-control well becomes
uninterpretable and every other well is rescaled against a perturbed reference. And none of the
three assay controls separates RNase-H1-dependent cleavage from steric block, which §3 names as
unevaluated, so a knockdown seen with this set is consistent with both while the ranking under test
models cleavage alone.

Where the wild-type measurement sits decides the answer, because the fusion carries *NR4A3* exons 3
to 8 and a wild-type assay must not read sequence the fusion also carries. The two available
placements bias in opposite directions. An amplicon upstream of the acceptor cannot detect
the fusion, but it lies on the 5′ cleavage fragment rather than the 3′ one, and the two fragments
are cleared by different routes at rates nothing here measures, so it reads wild-type knockdown
through the 5′ fragment's own persistence and biases apparent selectivity by an amount and in a
direction that are not fixed in advance; an amplicon spanning the wild-type exon-2/exon-3
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
its longest mature-parent duplex against a gene this ratio does not read (Table 5). The remedy
is not a second cut. No retrieved measurement bounds the parent case (§3), so a threshold on a donor
ratio would be a number with nothing behind it, where this one at least has a stated convention. It
is a reporting requirement instead: wild-type transcript for the reagent's own donor parent and for
the parent carrying its longest duplex,
measured in the same wells on the same dose–response, reported beside the ratio and against no cut —
the requirement the margin-contrast arm below already carries, stated for every arm rather than for
that one. A design whose donor knockdown tracks its fusion knockdown has lost what §3 says the
modality exists to buy, whatever the registered number reads.

What that leaves the registrable test able to settle should be stated without hedging, because it is
narrower than the existence of a pre-registrable threshold makes it look. The quantity above is
defined on wild-type *NR4A3*, and wild-type *NR4A3* is the one parent §3 states the case for
junction selectivity does *not* rest on. A result on this cut can therefore falsify the ranking and
cannot falsify the rationale. What would falsify the rationale is the corresponding ratio on a donor
parent — wild-type *EWSR1* or wild-type *TAF15* half-maximal knockdown concentration over the
fusion's, on the same matched dose–response — and this section states no cut for it, because no
retrieved measurement bounds the parent case (§3). The donor measurement is required to be reported
and is not required to clear anything. That asymmetry is a limit of the test rather than a property
of the reagents, and it is why the reporting requirement above is not optional. Nor does any arm
of this experiment read a phenotype: every quantity fixed here is a transcript measurement, so a
reagent that clears the cut has been shown to discriminate and has been shown nothing about the
growth or survival of an EMC cell. Whether such a cell requires the fusion at all is the assumption
§1 records as unshown, and no experiment in this paper tests it.

A ratio of residual transcript at a single dose is not commensurate with it and must not be compared
against the same cut: that ratio is bounded above by one divided by the fusion knockdown's
complement, so at the 58% knockdown reported for the analogous published
experiment<sup>38</sup><!--PMID:37370737--> it cannot exceed 1/(1 − 0.58) ≈ 2.4 however selective
the reagent is, and a cut of 5 would return falsification as arithmetic rather than as biology.

The replicate count follows from the variance rather than being asserted. Selectivity here compounds
four normalised measurements, so the replicate standard deviation of its natural logarithm is the quantity to
estimate in a pilot, and that standard deviation — taken across independent biological replicates of
the same matched dose–response, in the same wells, at the wild-type placement declared with it — is
the one thing the pilot has to return. Neither the pilot's replicate count nor its test article is
fixed here, for the same reason no assay is: both are properties of a platform this section leaves
open, and the replicate count is the quantity the pilot exists to decide rather than one it can be
given. What is fixed is the scale, because a standard deviation taken on the ratio rather than on
its logarithm is not the quantity the figures below are stated for.

At a standard deviation of 0.35 on that scale — natural log throughout, a 1.42-fold replicate
spread — six independent biological replicates give about 80% power to falsify a true selectivity of
3, and three give about 30%, computed from a noncentral t. The bound that decides falsification is
the upper limit of a two-sided 95% interval, equivalently a one-sided 97.5% bound, so the test's
one-sided type-I rate is 2.5% rather than 5%; the figures above are for that bound and change if a
one-sided 95% bound is used instead.

Above a
standard deviation of about 0.65 no observed ratio at or above one can place that upper bound below
5 at three replicates, so the test can fail only where the reagent is anti-selective. Such a test is
*void*: it cannot fail, which is a different outcome from one that fails to falsify, and voidness is
a property of the assay's replicate variance and not of the design. The number of
replicates should therefore be set from the pilot estimate, with three as a floor and not a target.
A pilot standard deviation is itself an estimate with large sampling error at small replicate counts,
so the void gate is applied to the upper confidence bound on the pilot's standard deviation rather
than to its point estimate, and the pilot reports that bound with its degrees of freedom.
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
contrast, at *EWSR1* exon 12: 5′-GCATATCATCAAACCA-3′ is the margin-1 register of the same
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
and it carries an eleven-base-pair duplex against wild-type *NR4A3*. That is not a reason to prefer
one mirror over the other: it puts that register in the do-not-order class of Box 1. No table here
prints that 16-mer — the tables select per junction and per screen — so the canonical file carries
its verdict and is where it must be read. This arm is available in one direction only.

*TAF15* exon 6 cannot supply the same arm: all four of its lower-margin registers pair a parent
through the whole gap at eleven or twelve base pairs, two of them against wild-type *NR4A3*.
Lower-margin registers do clear the parent screen at *EWSR1* exon 13 and *TCF12* exon 5 (Table 2), so
the arm is placed at *EWSR1* exon 12 because that is where the lead reagent sits, not because it is the
only junction that could carry one. A
contrast at one junction tests the ordering at that seam and not the ranking across the panel, and
the comparison it supports is between two arms rather than of one ratio against the cut, for which
this section states no rule.

### 4.5 · A design procedure for a breakpoint outside this panel

The reagents named above do not reach every patient: the two leads address the published breakpoints of roughly two thirds of
molecularly confirmed cases, and the panel is bounded by what has been sequenced rather than by what
can be designed. The deliverable is therefore the procedure as well as the reagents, and it is the
procedure that produced this paper's 190 designs, released unchanged with the artefacts.

Its input is the breakpoint at nucleotide resolution, by RNA sequencing of the tumour, which §4.4
requires in any case; an exon pair inferred from a break-apart assay is not sufficient. The builder
itself consumes the exon pair, and the nucleotide resolution is what establishes that the pair is
the right one and that the seam falls where the model puts it. Three things about running it are not
guessable from the module names given below, so the invocation is given rather than described. The
breakpoint is declared in the environment and the audit gate is a flag:

```
python3 junction_aso.py --audit
FUSION_JUNCTION_MODE=real DONOR_GENE=TCF12 DONOR_EXON_END=5 NR4A3_EXON_START=3 \
    python3 junction_aso.py
```

The audit run grades every declared breakpoint and designs nothing; a panel may only be emitted for
a pair it grades emittable. All three breakpoint variables are required and the builder refuses to
run without them, because a default would emit one junction's panel under the name of whichever
junction the caller believed they were designing for. And a non-coding acceptor is refused by
default: the *NR4A3* exon-2 and cryptic-exon
seams of §2.6 are reachable only with `PUBLISHED_BREAKPOINT_JUNCTION=1` set and the seam present in
the builder's whitelist of already-published non-coding acceptors, so a
new patient's exon-2 acceptor needs an entry added before the builder will emit for it — which
is the one acceptor class §2.6 calls most consequential, and the one place the released procedure
does not simply run. Given a
declared exon pair, `junction_aso.py` retrieves the parent transcripts, builds the modelled fusion,
grades the pair for frame and tiles the junction-spanning gapmers, emitting each with its GC, its
gap-level margin and a check that it complements neither parent perfectly. The five screens then run
on that panel: `junction_aso_offtarget.py` the alignment
screen against human RefSeq RNA, classifying each near-match by whether the catalytic gap is paired;
`aso_insilico.py` the exhaustive transcript scan, the target-site accessibility fold and the
sequence-liability filters; `aso_premrna_offtarget.py` the parents' unspliced sequence;
`aso_parent_gap_pairing.py` the mature-parent screen; and `aso_genome_offtarget.py` every position of
GRCh38. A design is *certifiable* here where all five could be run on it and it cleared all five; a design one screen cannot address is uncertifiable whatever the other four return. The parent screens matter most: pairing a parent
through the whole catalytic gap is this paper's central negative and surrenders the only advantage
the modality has. Where the acceptor half is not exonic in the mature transcript, the
un-rearranged-allele scan of §2.6 applies as well, and it lives in two further modules rather than in
a step within the five screens: `aso_taf15_intron2_designs.py` holds the single implementation of that scan,
which grades a design gap-paired on the un-rearranged allele's unspliced transcript — a
hybridisation test, not an establishment of cleavage — when it pairs the unspliced
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
BLAST's sensitivity at ≥14/16 is bounded rather than unquantified, and the bound is not one: at a
word size of seven, two mismatches split a 16-mer into at most three segments whose longest is at
least five, and 15 of the 120 two-mismatch configurations leave no exact seven-mer and cannot be
seeded at all — about an eighth of the class, unreachable at any depth. So "no sense-strand
near-match" is a property of this search and not of the
transcriptome; the exhaustive transcript scan is complete for substitutions only within its
one-mismatch budget, so it corroborates the exact and single-mismatch part of the claim, and no
screen here establishes the absence of two-mismatch sense-strand near-matches.

**The parent threshold is stated, not measured.** The mature-parent counts — 87 of 190, 61 of them against
wild-type *NR4A3* — are taken at a contiguous duplex of ten base pairs, a criterion adopted here
rather than measured for this architecture, so each is a floor at that choice: at the
seven-base-pair end of the same cited range the screen returns 175 of 190. Nor does the criterion
transfer cleanly, ten being a whole-duplex length where the source counts RNA:DNA nucleotides, which
this architecture holds at six (§6). Nor does the rate transfer to a wider search space. Every count
at this criterion, and every null rate beside it, is a rate over the 19,921 sixteen-nucleotide
windows of six parent transcripts (20,011 nucleotides, 0.0028% of the windows of the transcript
corpus screen 2 measured), and the criterion is saturating over that corpus: independent uniform
bases predict about 2.7 × 10³ qualifying sites per 16-mer there, so an arbitrary 16-mer would meet
it transcriptome-wide with probability one, as would a scramble and as would a chimera. What the
screen measures is therefore self-liability rather than an off-target rate. Of the 87 liable
designs, 85 are paired by one of their own two parent genes and the other two by a FET paralogue of
their donor, and this work claims no transcriptome-wide rate, nor could one be taken from it. The
threshold also sets how much of the liability the nulls account for, and ten is not where they
account for least: the exon-terminus chimera reaches 40.6% against 45.8% observed, which is 88.6% of
the observed rate and the third-lowest such share on the eight-cut ladder of §2.5. At four of those
eight cuts, six, eight, nine and thirteen, the strongest null stands above the observed rate rather
than below it, so the share the nulls account for is not monotone in the criterion and changes sign
with it. One cut does leave a share to attribute to the reported breakpoints themselves, and it is
not the cut reported here: at eleven the strongest null falls below the observed rate's interval
rather than inside it, the only cut on the ladder at which the observed rate nominally stands
clear of every null (§2.5).

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
*ACTB*,<sup>3</sup><!--PMID:41755350--> and others are reported, and 2% of one cohort carried no
identified partner.<sup>9</sup><!--PMID:36948401--> Three of the 15 *EWSR1*-rearranged tumours of the
primary breakpoint series carry transcript types the retrieved record does not name, so retrieval is
an upper bound on what would open that block. At least one named variant is reported to arise from a
genomic breakpoint interior to *EWSR1* exon 12 rather than between two exons, in a source that
carries a citation marker on that sentence and is therefore restating an earlier
report.<sup>36</sup><!--PMID:9060841--> That marker, and the 1995 report of this fusion it resolves
to — reference 1 here — were read from the paper's scanned page images through an optical-character
layer, the only form of its full text obtained here, and are recorded with the retrieval in
`lit-targets-aso-type3-designability.json`; two later attempts to re-fetch the full text returned no
open-access copy, so the reading stands on that layer and is marked unverified beyond it. Such a breakpoint is not undesignable: handing the same
builder a donor model cut inside its exon returns five builder outputs, all fusion-specific against both
parents, three gap-centred and a best gap-level margin of 3. What such a junction lacks is an exon
index, which is how every design here is specified, and a published nucleotide position, which no
retrieved source states, so it is out of reach for a stocked panel while remaining designable for a
named patient whose breakpoint has been sequenced. How many tumours this accounts for is not
established by any source.

**One geometry.** Every screened count here is for one architecture, a 16-mer at 5-6-5, except those
§2.9 reports and the ones §4.2 and Table 5 carry over from it for the 5-8-5 control. Across those
three panels the ten-base-pair criterion is not one criterion. It is an absolute hybrid length that
does not scale with the gap, so a run counted at it is six RNA:DNA pairs plus four locked-wing
pairs at 5-6-5, eight plus two at 5-8-5, and ten RNA:DNA pairs at 5-10-5, where every window
pairing the whole gap clears it by construction. §2.9's liable count is flat at 87, 88 and 87
across a criterion whose RNA:DNA content rises from six to eight to ten, so that flatness is not a
reading at a constant substrate. The
genome scan is unavailable at 18 and 20 nucleotides by construction rather than merely unrun, so the
nesting bound on a longer design's genome liability is a next step and not a result, and no RNase-H1
assay distinguishes these geometries here.

**Hybridisation, not cleavage, and not exposure.** All five screens address hybridisation-dependent
liability only, and the free-energy calculation speaks to duplex formation rather than to cleavage.
Within that they grade cleavage-competent hybridisation, so a liability that needs binding alone
falls outside every one of them: an oligonucleotide occupying the wild-type *NR4A3* 3′ splice
acceptor — the intron-2/exon-3 boundary §2.5's pre-mRNA class concentrates at — can alter that
transcript's splicing with no catalytic gap paired, and no screen here reads occupancy. It is
unmeasured rather than absent.
The headline parent counts require the catalytic gap paired in full, an inclusion criterion adopted because
no retrieved measurement grades a partly-paired parent duplex; the class it excludes is counted separately,
as the 21 designs of §2.5. Nothing here establishes that a matched gene is transcribed in the organs a systemic dose reaches: 13
of the 46 loci returned no reading and carry 52 of those 649 hits, so there the exposure
question is unanswered rather than answered negatively, and reference bulk medians describe a population's normal tissue rather than a dosed
patient's organ (Table 6). Two liabilities of this chemistry are separated here because they are usually conflated. The
phosphorothioate-class effects — protein binding, and toxicity that tracks backbone content rather
than sequence — are not a function of any feature graded here. Hepatotoxicity is the second, and this paper grades neither. Nothing in this work
establishes which mechanism drives it, and no screen here is a readout on it: the only pre-mRNA arm,
screen 3, is bounded to six parent genes rather than to the transcriptome, while the genome-wide
arm, screen 5, grades hybridisation and not cleavage. The affinity-linked component that the
architecture (§6) would raise is not graded either.

**The chance null is crude.** It assumes independent uniform bases, where real transcript sequence is
composition-skewed and repetitive. An arbitrary position matches a given 16-mer at ≥14/16 with
probability 2.6 × 10⁻⁷, or 189 near-matches for any 16-mer whatever over the exhaustive transcript
scan's measured span of 718,571,139 nucleotides across 186,185 transcripts — a figure the alignment
screen's 50-hit cap cannot test at all. That span is screen 2's transcript corpus and is under a
quarter of the 3.10 × 10⁹ nucleotides of assembly the genome scan covers, so the two chance figures
this section quotes stand over different denominators and are not comparable to one another. The
scan itself can,
and on the mean it comes in at chance: at ≤1 mismatch the same span predicts 8.2 per design against
an observed 9.2 over the 176 distinct oligonucleotides, a ratio of 1.12. The shape disagrees in both
tails, 40 of the 176 returning no match where a Poisson null of that mean predicts fewer than one,
and a right tail reaching 100 matches on one design (Supplementary Figure S1), so the null separates
"more than chance" from "at chance" and nothing finer and does not license reading the zeros as
cleanliness.

**Records are not genes, and one assembly is not a genome.** RefSeq carries one accession per
annotated variant, so a match to a constitutive exon is counted once per variant: over the 44 designs
of the 38 junction screens whose hit lists permit a locus recount the median inflation is 2.25
records per locus and the maximum 11.0 at the default search depth, more than doubling the apparent
number of distinct genes. Tables 2 to 4 are built at the deeper ceiling, where the same recount gives
a median of 5.52 and a maximum of 28.0, so the tables' locus counts are inflated by more than this
paragraph's figures and not less.
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
returned came back at or above the ceiling: of nine designs queried, one failed at the remote service, seven
returned exactly 50 records and the eighth 52.

The per-design rows in that file therefore look like off-target findings and are none. Of its 402
retained rows, six are exact 16-of-16 matches, four of them to genomic clone records and two to
annotation records on chromosome 6, and 55 are immunoglobulin variable-region records,
every one of them at 14 or fewer of 16. A corpus of this kind carries one stretch of sequence once
per record that contains it, so those rows are largely redundant copies of one another, and there is
no denominator against which to say whether any of them is more than arithmetic. No count, ratio,
load or cleanliness statement in this paper is taken from that file. Nor does it bear on screen 5,
which is a different object that shares the word
genome-wide: screen 5 is the exhaustive GRCh38 scan of §2.7 and §6, whose expectations are computed from the
2,948,609,696 windows it actually searched over a measured 3.10 × 10⁹ nucleotides of assembly, and
which caps nothing at scan time. The earlier attempt is retained as the record of an instrument that had no
reading to give, and it should be read as nothing else.

## 6 · Methods

**Transcript models.** Canonical transcripts for the five partner genes and for *NR4A3* were obtained
from Ensembl.<sup>40</sup><!--PMID:39656687--> Each model was self-checked before use: exon lengths must sum to the spliced cDNA, the
coding sequence (CDS) must occur exactly once within it, and translation of the CDS must
reproduce the annotated protein. Per-exon coding content was additionally cross-checked against an independent exon audit for
*EWSR1* and *NR4A3*; for the other four partners that audit does not exist, and the weaker check is
recorded per gene in the released artefacts. Every exon number, coordinate and length in this paper
is relative to one specific model per gene, and the canonical transcript of a gene can change between
Ensembl releases, so the accessions are given here rather than left to the artefacts:
ENST00000397938 (*EWSR1*), ENST00000605844 (*TAF15*), ENST00000333725 (*TCF12*), ENST00000254108
(*FUS*), ENST00000240851 (*TFG*), ENST00000395097 (*NR4A3*) and ENST00000325455 (*PGR*), the last
for the single seam of §2.6 that lies outside the five modelled partners. Each is the Ensembl
canonical transcript for its gene at the release read, which is what the pipeline selects; no MANE
status was checked for any of them here. Two things this argument needs were not captured and cannot
be recovered from the artefacts: the Ensembl release, and the version suffix of each accession. The
transcript-model record carries the instant of its fetch, 2026-08-12T13:41:57Z, and the REST
endpoint it used; the unspliced-sequence cache carries neither a release nor a date. An unversioned
accession under an unstated release does not by itself pin sequence, so what pins it here is the
committed sequence caches, which travel with the archive and are what a reproducer should compare a
refetch against rather than assume agreement with. The release stated for the genome scan below
governs that scan's annotation and is not evidence about these models.

Exon numbers are transcript exon indices, counted from the transcript 5′ end of the model named
and including non-coding exons; they are not coding-exon indices. The distinction is not cosmetic,
and it is the axis on which an earlier version of this work was withdrawn: *TCF12* carries 21
transcript exons and 19 coding, *TFG* eight and seven, *NR4A3* eight and six. The count difference
is not the index shift, and for *TCF12* the two differ: its two non-coding exons are the first and
the last, so only one of them precedes the coding sequence and the index shifts by one rather than
by two. *TCF12* transcript exon 5 is coding exon 4 under the other convention, with a different 3′
terminus; *TFG* shifts by one and *NR4A3* by two, their non-coding exons all preceding the coding
sequence. *EWSR1*, *TAF15*, *FUS*
and *PGR* have a coding first exon and the two conventions coincide for them.

**Chimera construction.** Chimeras were built from transcript sequence rather than by joining coding
sequences. A fusion keeps the whole *NR4A3* acceptor exon, so any bases of that exon lying ahead of
the *NR4A3* start codon are still present in the fusion transcript, and they are the first bases an
oligonucleotide meets on the *NR4A3* side of the junction. At the exon-3 acceptor, the only one the
38-junction panel yields designs at — §2.6 designs and screens at *NR4A3* exon 2 and at the
intron-2 cryptic exon besides — there are two. Joining coding sequences alone would omit them, shifting every
design by two positions. A pair of exons is *in frame* when the partner's coding bases, plus those
retained bases, sum to a multiple of three. Every declared exon pair was graded by that rule before
any design was emitted, and only the in-frame pairs were carried forward, since only those describe a
fusion that could exist.

**Design.** Junction-spanning 16-mer gapmers were tiled in a 5-6-5 β-D-oxy-LNA/DNA/β-D-oxy-LNA
architecture, which is the chemistry the design rules below assume. Every one of the 15
internucleoside linkages is a phosphorothioate — wings and gap alike, not the wing-only variant — and
that backbone is specified as stereorandom, the ordinary case: a 16-mer carries 15 chiral phosphorus
centres and is made as a mixture. The bicycle is named because α-L-LNA, 2′-amino-LNA, ENA and cEt are
also sold as locked analogues and behave differently in a gapmer wing.
Nucleobase modification is specified here rather than left to a vendor default, because two suppliers
filling the same base string with different conventions would ship two molecules: locked cytosines
are 5-methylcytosine, and the cytosines of the DNA gap are unmethylated 2′-deoxycytidine. The second
half of that is what makes §2.10's CpG audit read as written — 5-methylation of a gap cytosine
removes the motif while leaving the base pair, the target window and the gap-level margin untouched,
so a paper that left the state open would be auditing a liability the reader could already have
removed at no cost. Neither choice is modelled by the free energies below, which are computed for an
unmodified DNA:RNA hybrid. Termini are free 5′-hydroxyl and 3′-hydroxyl, with no cap and no 5′
phosphate, and the sodium salt is intended. Backbone stereochemistry is not modelled anywhere in this work, and nothing here
distinguishes one diastereomer from another — which bears on §4.2's gap-length arm, since a
six-nucleotide gap offers few cleavage positions to redistribute among. Each way of sliding
that 16-mer along the transcript is a *register*, and only registers placing the junction inside the
six-nucleotide DNA gap were retained, since RNase-H1 cleaves within the DNA:RNA duplex of the gap and
needs a minimum run of contiguous DNA to do so.

The gap length is a compromise and is treated as one. Reported minima for that run are five to six
nucleotides — at least five for cleavage to occur,<sup>41</sup><!--PMID:39126066--> or a DNA segment
of "six or more bases" to activate the enzyme<sup>42</sup><!--PMID:41614678--> — and for LNA/DNA/LNA
gapmers specifically a six-nucleotide gap gives noteworthy but incomplete activity, with seven to ten
reported as optimal.<sup>39</sup><!--PMID:24981949--> None of the three figures is a titration in
this architecture, and SI §S3 gives the provenance of each. Six therefore sits at the short end of the
usable range and below the reported optimum. Each wing is five contiguous locked residues. That is a
high locked-residue content for a 16-mer, against the two to four locked residues per wing this work
takes to be usual; and the 5-6-5, 5-8-5 and 5-10-5 ladder tiled here is adopted from the geometries
commonly reported for 2′-O-methoxyethyl gapmers rather than for locked ones. No source was retrieved
into this work for either statement. Both are premises adopted to justify a specification, neither
is evidence for any result here, and the three citations in this paragraph are attached to the
gap-length figures above and not to either of them. The geometries were held fixed so that gap
length is the only variable across the three panels, which is what §2.9 measures; the consequence
is that these are not conventional locked-nucleic-acid reagents, that their matched-duplex melting
temperatures are correspondingly high, and that this work takes high affinity to carry a risk of
sequence-dependent hepatotoxicity. That last is a premise adopted here and not a retrieved finding:
no source for it was retrieved into this work. It is stated because it bears on any decision to
synthesise, and none of it is graded here. It was retained as the panel's fixed baseline rather than
as an optimum, and the two longer
geometries were tiled and screened beside it precisely so the trade it makes is measured rather
than assumed (§2.9, Table 7). The five junction-spanning registers per junction it admits are a
consequence of that gap length, not a reason for it: 5-8-5 and 5-10-5 admit seven and nine. No claim is made that a short gap improves
fusion-versus-parent discrimination: one series that shortened a 5-10-5 gapmer to 5-6-5 reported
lower off-target knockdown but also lower on-target activity and lower allele
selectivity.<sup>41</sup><!--PMID:39126066--> Within that same series 5-8-5 was the one shortened
design reported to give a small increase in activity or allele selectivity in some cases, and it also
increased off-target knockdown relative to 5-10-5 for several of the genes tested, so the exception
is not a free one. Those gapmers carry thiomorpholino rather than LNA wings and are directed at a
single-nucleotide polymorphism distinguishing two alleles rather than at a fusion junction, so
neither the rule nor its exception is evidence about gap length in this architecture. Because that
trade is the modality's central one,
5-8-5 and 5-10-5 were tiled over the same junctions by the same rule and carried through four of
the five screens below — the exhaustive genome scan is unavailable at 18 and 20 nucleotides by
construction, as §5 and Table 7 both state — wings held at five nucleotides so that only the gap changed and LNA affinity enters every
parent duplex identically (§2.9).

**Ranking.** What separates the fusion from a parent is the junction-unique bases inside the gap, not
identity across the whole oligonucleotide, because the gap is where the enzyme cuts. Designs were
therefore ranked by their *gap-level margin*: the junction-unique bases inside the gap on the shorter
side of the junction. That is the panel-level statistic, which compares designs across junctions.
Selecting within one junction is a different question, and Table 2 — from which the reagents of §4.1
are taken — orders designs by parent liability first, then pre-mRNA sites, then distinct gene loci,
with the margin breaking ties. Each candidate was screened against all six parent transcripts rather
than the two of its own fusion, because a design's liability need not fall on its own two parents:
§5 records the designs a FET paralogue of their donor pairs instead.

**Specificity screening.** Five screens were applied. Each is named below and referred to by that
name throughout, because each reaches a compartment the others cannot and each is blind to something
another catches. No single screen supports any claim here on its own.

1. **The alignment screen.** Each target window was queried against human RefSeq
   RNA<sup>43</sup><!--PMID:26553804--> through the NCBI BLAST URL
   interface<sup>44</sup><!--PMID:20003500--> rather than a local installation, so the database is a
   live service rather than a pinned snapshot. When it was queried is not recorded either: no screen
   artefact released here carries a run date, a date range or a database build identifier, so the
   divergence between the counts reported here and what the same query returns today cannot be
   bounded from the record. Each screen stores the request identifier the service returned, which is
   not a date. The parameters decide what a ≥14/16 screen can
   return and are therefore given in full: `PROGRAM=blastn`, `DATABASE=refseq_rna`, `WORD_SIZE=7`,
   `EXPECT=1000`, `MEGABLAST=off`, `FILTER=F`, `ENTREZ_QUERY=txid9606[ORGN]`, and a hitlist of 50
   per query raised to 500 on the deeper pass, with ≥14/16 identity applied on the returned
   alignments. That 500 is not on the same footing as the rest of the list: it is stored in a
   parameters block for the longer-geometry screens, while for the 38 panel screens it is inferred
   from retention exceeding what a default run can produce rather than read back from the request.
   What does not depend on the inference is that no deep hit list was truncated — the largest holds
   374 records against a ceiling of 500, and no design's list is recorded as incomplete. A transcript window matching a design at 14 or more
   of its 16 positions is a *near-match*, classified by whether the six-nucleotide gap is itself
   base-paired: one that pairs the gap is *gap-paired* — the paper uses that one term throughout,
   and a sense-strand gap-paired near-match is what it calls a gap-paired sense-strand match — and RNase-H1 could
   cleave
   there; one pairing only the wings could not. That definition is written in substitutions, but
   `blastn` returns gapped alignments and an identity filter does not reject them, so this screen
   alone — unlike screens 2 to 5, which are substitution-only by construction — admits a near-match
   carrying an insertion or a deletion. Across every 5-6-5 alignment screen released here 110
   retained alignments carry an indel and 28 of those are counted as gap-paired sense-strand matches.
   Admitting them
   can only raise a design's count, so no cleanliness statement rests on their exclusion; the point
   is that this screen's counts are not substitution-only and should not be read as though they
   were. This is a heuristic search retaining only a limited
   number of hits per query, so every count it yields is a lower bound — an effect §5 measures.
   Records of a design's own two parent genes, its donor and *NR4A3*, matched by the symbol and the
   aliases each screen records in its parameters, are counted separately and excluded from this
   screen's near-match counts, since each of those two pairs one wing by construction and would
   otherwise dominate the list; the parents are assessed instead by the gap-level margin, by screen
   4 and — for their unspliced sequence — by screen 3, whose own near-match counts are counts of
   parent sites and are reported as such (§2.5). The exclusion is not taken over the six parent
   genes of the panel: a record of a partner gene that is not the design's own donor is retained,
   because engagement of a gene the fusion does not involve is a specificity finding at that
   junction rather than a parent pairing. The distinction is measured and not hypothetical.
   5′-GCATATCTGAATACTG-3′ at *TFG* exon 7 retains nine near-matches to wild-type *FUS* in its deeper
   re-screen, every one of them gap-paired on the sense strand.
   A substitution-only gap-paired near-match at 14 of 16 carries both its mismatches in the locked
   wings, since the six gap positions are paired by definition; the gapped alignments named above
   are the exception, their two non-identical positions not being substitutions in a wing at all. A mismatch opposite a locked
   residue is more destabilising than one opposite DNA, and no locked-nucleotide mismatch
   penalty is applied anywhere in this work. These counts are therefore an upper bound on
   hybridisation as well as a lower bound on search depth, and the architecture is invoked
   for the free-energy margin (§6, duplex thermodynamics) while being left out of the
   off-target counts. Both directions are stated rather than composed.

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
   records, and every target window was compared to every 16-nucleotide window of all six — *EWSR1*,
   *FUS*, *NR4A3*, *TAF15*, *TCF12* and *TFG*; *PGR* lies outside this set — forward
   orientation only. The query is the target window, which is the reverse complement of the
   antisense oligonucleotide the tables print. A window counts only if all six gap positions are paired. Its size is the
   longest contiguous run of perfect pairing containing the whole gap. It is not the duplex the
   enzyme acts on: exactly six of its ten to thirteen base pairs are the RNA:DNA gap, and the rest
   are LNA:RNA wing pairs. That RNase-H1 does not cleave those pairs is why a gapmer has a gap at
   all: no RNase-H-mediated cleavage was observed for a fully modified 11-mer locked
   oligonucleotide or an 11-mer locked/DNA mixmer, where an LNA/DNA/LNA gapmer with a
   six-nucleotide DNA gap elicited substantial activity.<sup>39</sup><!--PMID:24981949--> That the
   catalytic footprint reaches past the DNA stretch is retrieved too: a footprint model places
   sugar-modified, non-DNA residues at footprint positions flanking a five-base DNA gap and reports
   cleavage retained there.<sup>45</sup><!--PMID:28624195--> Whether the hybrid-binding domain
   reads a locked pair as hybrid is a third statement and is not one of these: no measurement
   retrieved into this work bounds that domain's affinity for a locked duplex, so that it does not
   is a premise adopted here, and the ten-base-pair threshold below is stated on it. The caveat
   below states the consequence.
   Runs shorter than ten base pairs are not treated as plausible substrates. That is a
   stated threshold, not a measured one, so every design's longest run is released. Ten is the strict
   end of a figure its source gives as a possible explanation of its own observation — "this could be
   because RNase H1 requires a minimum length of 7 to 10 RNA:DNA hybridized nucleotides to bind with
   its hybrid binding domain" — rather than as a measured
   minimum.<sup>46</sup><!--PMID:35664704--> The qualifier does
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
   disease's own acceptor even by chance. §2.5 reports all three. Proportions carry Wilson 95%
   intervals. The pseudo-random stream is a splitmix64 written out in the released module rather
   than taken from the interpreter's own, and it is seeded at 20260815, each ensemble drawing its
   own stream from that seed and its own name so that adding or removing an ensemble cannot shift
   the draws of the ones either side of it. Those two facts are what make the artefact reproducible
   bit for bit, and the artefact records both. The module is `aso_parent_null.py` and its output
   `aso-parent-null.json`; the screen it re-runs is `aso_parent_gap_pairing.py` unchanged, so
   between the observed arm and every null only the query differs. §2.5 reports the result.

5. **The genome scan.** Screens 1 to 4 are bounded either by an annotation or by six transcripts.
   The fifth removes that SEARCH-SPACE bound, and only for the pre-mRNA class: it runs at two
   mismatches, and a contiguous run of eleven or twelve base pairs inside a 16-mer leaves five or
   four positions unpaired respectively, so the mature-parent duplex class of §2.5 stays bounded by
   the same six transcripts it
   was bounded by before. A reader who takes this bullet alone gets a wider clearance than the
   screen supplies (§2.7). Each distinct target window and its reverse complement were placed
   in one membership set and every plus-strand position probed once, which covers both
   orientations without a second pass, at ≤2 mismatches, exhaustively: windows containing an N
   were excluded, leaving 2,948,609,696 of 3,099,747,808 over a measured 3.10 × 10⁹ nucleotides,
   with no seed, no word size and therefore no search sensitivity to quantify. The assembly is
   `Homo_sapiens.GRCh38.dna_sm.primary_assembly.fa.gz` and the annotation that decides every
   strand-agreement and gene call is Ensembl release 116; the primary assembly matters, because the
   full GRCh38 with alternate contigs would not reproduce this denominator. §2.7 reports it.

   **The un-rearranged-allele scan.** A sixth instrument sits outside those five and is scoped to
   the seams where it can bite. Screens 1 to 5 ask what else a design can pair; this one asks
   whether a design pairs the patient's own un-rearranged *NR4A3* allele, which can only arise where
   a design's acceptor half is *NR4A3* sequence the wild-type allele presents in the same register:
   the exon-2 and intron-2 cryptic-exon seams of §2.6, not the exon-3 acceptor the 38-junction panel
   uses. Each target window was compared to every window of the committed *NR4A3* unspliced
   sequence, the same cache screen 3 reads, in the forward orientation only, which is screen 4's
   convention rather than screen 3's. A site is retained at two or fewer mismatches over the whole
   16-mer and is called cleavage-competent only where none of those mismatches falls within the six
   gap positions, which are positions 6 to 11 of the target window. Where the cache is absent, or
   where the cryptic exon is not a substring of it, the scan refuses and records an absent reading
   rather than a clean one. This is one locus and not a genome-wide result; §2.6 reports it, and
   three designs are condemned by it and by nothing else, which is why they carry a flag no
   parent-screen column accounts for.

**Strand orientation.** A match matters only if an antisense oligonucleotide could base-pair with it,
which means the sense strand; a window carrying the reverse complement is not a liability at all.
`blastn` searches both strands, so such a hit passes an identity filter unless orientation is parsed,
and screens produced before that parsing was added recorded them as gap-paired sense-strand matches. Orientation is
now parsed and filtered in all 38 junction
screens and the 183 designs they hold, and therefore in every cleanliness statement made here. Only
two released screens are unfiltered, and neither carries a junction from the 38-junction panel or supports a claim here (SI
§S5). The same rule governs pre-mRNA, which is transcribed in transcript orientation: a forward match can be
base-paired and a reverse-complement match cannot.

A design is called clean where it carries no sense-strand near-match, and that is always a
statement about a complete hit list at a stated search depth. Both qualifications matter. A hit list
the cap truncated is not complete, so no verdict is available for that design, and a design clean at
one depth need not be clean at another. §2.4 and §5 report both effects.

**Target-site accessibility.** Accessibility was estimated as the mean unpaired probability over a
local fold of up to 180 nucleotides, computed with the ViennaRNA partition
function,<sup>47</sup><!--PMID:22115189--> and it spans 0.160 to 0.707 across all 190 designs at
real exon junctions, with a median of 0.477. The window is not a fixed 180: it spans the union of a
junction's candidate target windows plus 80 nucleotides either side, on the modelled fusion
transcript, clipped at the transcript ends. The partition function was called at the package's own
defaults, and no version, temperature or energy-parameter set was captured for it, so the released
values are reproducible only against the same installation. It is released with the artefacts and
ranks nothing here. That omission is deliberate — accessibility bears
on potency, which is not claimed for any sequence, rather than on the discrimination this work is
about — and SI §S1 gives the three reasons in full.

**Expression of the off-target loci.** No screen above says whether a matched gene is transcribed
in the organs a systemic dose reaches. For four of the five junctions of the 38-junction panel with a published exon-resolved breakpoint — those
Table 6 covers — the gene loci their deeper screens return in the gap-paired class were read against
GTEx v8 median TPM.<sup>48</sup><!--PMID:32913098--> No such reading was taken at *TFG* exon 7, so
that junction carries no expression reading rather than a negative one. The readings are in two
blocks, reported separately and never combined, against two cuts used for legibility rather than as
thresholds of concern: a lower cut of 1 TPM, below which a reading is taken as below detection, and
an upper cut of 10 TPM. The first block is liver and both kidney compartments, the organs a
systemically dosed phosphorothioate gapmer distributes to — a premise taken from the chemistry, for
which no measurement or citation was retrieved here; the second is six soft-tissue types: skeletal
muscle, subcutaneous adipose, tibial nerve, cultured fibroblasts, tibial artery and sun-exposed skin
of the lower leg, standing in for the compartment EMC arises in, since no atlas contains the tumour
itself. Both blocks are read from the same v8 gene-level release,
`GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm`, whose cells are medians across a
tissue's donors and are gene-level rather than transcript-level. NCBI Gene
supplied locus identity, so a locus with no reading is attributed rather than left blank, and the
Human Protein Atlas<sup>49</sup><!--PMID:25613900--> was read as a transport check only, its
consensus incorporating GTEx rather than confirming it independently.

**Discrimination model.** The binary assumption that any mismatch inside the gap abolishes cleavage
is not supported by the primary literature and is not used for any claim of cleanliness. The field's
general figure for single-nucleotide discrimination by a gapmer carrying no positional modification
in its gap is approximately five-fold, given in its source as prior work restated rather than
measured there,<sup>33</sup><!--PMID:23963702--> and at 16-mer length one study reports no efficient
discrimination at all.<sup>50</sup><!--PMID:7567450--> Both underlying measurements are against a
single-nucleotide substitution rather than a fusion junction, and the pessimistic one used
unmodified antisense DNA, so they are used here as bounds for unmodified chemistry rather than as a
property of this architecture. Neither is resolved at a gap of six. The five-fold figure carries no
geometry at all, being prior work restated rather than measured where it is stated, and the
pessimistic one has no gap, an unmodified antisense 16-mer presenting a sixteen-nucleotide DNA:RNA
hybrid. Both are applied as a scalar per gap mismatch, so the re-score treats a mismatch at the
gap's edge and one at its centre alike, where the surviving contiguous run does not — five
nucleotides for a mismatch at the first of six gap positions against three for one at the third
(§2.9). The classification records how many gap positions mismatch and not which, so no count
reported here is positional; the alignment strings are released, so such a re-score is possible and
has not been done. Gapmer-specific work points the same way, which is why the bounds are
not narrowed: across more than 120 gapmers spanning five single-nucleotide changes, three achieved
preferential cleavage of the mutant allele both in vitro and in cells, two at one substitution and
one at another, while several more did so in vitro only,<sup>51</sup><!--PMID:28970564--> and in the
one retrieved campaign that achieves allele selectivity on purpose it is engineered by a chemical
modification at a gap position that restricts cleavage of the near-match, rather than obtained from
the mismatch itself: a single 2′-O-methyl at gap position 2, in locked and 2′-O-methoxyethyl gapmers
directed at one substitution in one gene, and reported by its own authors as preliminary proof of
concept.<sup>52</sup><!--PMID:42327837--> That is one gene, one substitution and one modified
position, and it is not evidence about a fusion junction.

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
entropies for a DNA:RNA hybrid were taken from Sugimoto and
colleagues,<sup>53</sup><!--PMID:7545436--> as packaged in `Bio.SeqUtils.MeltingTemp.R_DNA_NN1`
(Biopython 1.88) and read from the installed package rather than entered by hand, and ΔG°37 computed
as ΔH° − TΔS° at T = 310.15 K, with that table's own initiation term included in the sum and ΔS°
converted from cal to kcal. Those four specifications decide the absolute free energies below; the
parameter values alone do not. The arithmetic was checked against an independent implementation,
which agreed exactly; that check verifies the summation and not the choice of strand, and the strand
concentration it uses enters no reported free energy (SI §S2). No salt correction was applied. A
nearest-neighbour set is determined at the ionic strength of the measurements behind it rather than
at a physiological one, and the correction is length-dependent, so it does not cancel in a ΔΔG°37
taken between a 16-base-pair duplex and the seven- to ten-base-pair parent run it is measured
against. That term is unstated in the
artefact and uncorrected here, and it is one of at least three omissions running against the floor
direction stated below rather than with it. The other two are chemistry this work specifies and
does not model. The backbone is a phosphorothioate throughout, wings and gap alike, and no
phosphorothioate parameters were applied, so a substitution carried by every linkage of both duplexes is absent from
a comparison that sets 16 base pairs against seven to ten and therefore does not cancel between
them. And a parent seam is not the isolated short duplex the calculation treats it as: the rest of
the same molecule, five locked residues among them, stays covalently attached and stacks on that
seam, where the fusion duplex has no unpaired remainder to stack. Both are taken here to narrow
ΔΔG°37 rather than widen it, and both directions are premises adopted for this work rather than
measurements: no source retrieved into it bounds either term.

These designs carry LNA wings and the table is for an unmodified hybrid, so what is computed is the
duplex the DNA backbone would form. Because the junction lies inside the gap, each parent pairs one
of the two five-nucleotide LNA wings while the fusion pairs both, so LNA should widen the
free-energy difference rather than narrow it, and every reported ΔΔG°37 is a floor in that sense.
That direction follows from the architecture and was not computed: no LNA parameters were applied.

That floor is a statement about the difference and not about selectivity, and it must not be read
as one. What decides whether a parent duplex forms in a cell is its absolute stability at the
exposure concentration, not its distance from the fusion duplex. Five contiguous locked residues
per wing raise duplex melting temperature substantially, and the same modification that widens the
difference therefore also stabilises the parent seam it is measured against. Every one of the 38
top-margin designs divides its 16-mer eight and eight, and every one of them carries the same
acceptor-side seam — the shared *NR4A3* exon-3 octamer — at −7.77 kcal/mol as an unmodified hybrid.
That figure is therefore a structural floor of the class rather than one weak outlier in it, and it
is the more stable of the design's two seams, the one the free-energy margin is measured against, for
25 of the 38. Within the top-margin class the best parent seam runs from −7.77 to −12.60; the
190-design panel across all three margins runs to −17.51 with a median of −8.66, which is a wider
distribution but a different denominator. That median coincides numerically with a different
quantity §2.9 and §4.2 print, the lead reagent's own best parent seam at 5-8-5; the two are
unrelated and the repetition of −8.66 is arithmetic coincidence rather than one cell copied twice. A
seam that weak melts far below 37 °C at the strand concentrations
these parameters are defined at, which is not the same as saying it is unoccupied at the
concentration a cell sees, and it is exactly this class that LNA wings would push toward occupancy. No modified-duplex
melting temperature or dissociation constant was computed for any parent seam, so discrimination at
the binding step is not resolved here — it is uncomputed, and an occupied but catalytically
incompetent parent duplex is the steric-block liability §3 names as unevaluated.

**The four design rules.** Every design was separately audited against four rules commonly applied
in antisense design and adopted here without a retrieved source: GC within 40–60%, no G-quadruplex
motif, no homopolymer run of four, and no CpG dinucleotide. The set is this work's own, declared in
the released module that computes it, and no design-guidance source was retrieved for any of the
four; §2.10's disagreement is therefore between this rule set and the gap-level margin, and not
between the field's convention and either. The quadruplex rule tests for four separate runs of two
or more guanines, which is
what makes it silent on this panel (§2.10). The audit is not there to grade the designs, but to ask
whether conventional triage and the gap-level margin would select the same molecules.

**Sequences.** **Do not order an oligonucleotide by copying it out of this PDF.** Every sequence
named here travels with the archive as `fusion-junction-aso-sequences.csv` and
`fusion-junction-aso-sequences.fasta`, both under `research/manuscripts/aso/` in the repository
named above. They are the canonical record: generated from the
same artefacts as the tables, carrying each design's geometry, junction and gap-level margin, and
flagging every design this paper names as one not to be carried forward. A design's `junction` is
one of its junctions and not all of them — nine of the 16-mers span two or three, which is why 190
design records are 176 distinct molecules — so `also_tiled_at_junctions` carries the rest and both
columns must be searched before concluding that a junction has no reagent.

**Which column to select on, because the obvious one is wrong.** The record's `role` column carries
the paper's own answer: `best available at this junction` marks the design §4 would name there.
Ranking by gap-level margin instead — the only ranking this paper states, and the one a reader
naturally reaches for — is not the selection rule and does not reproduce it. The file keys a row to
43 distinct junctions, 42 of which carry a 5-6-5 register; over those 42 the top-margin register is
a design the file condemns at eight. At three of those every register
is condemned and no rule could do better, so what the margin rule actually costs a reader is a
clean design at the other five, where one was available and it picked a design pairing a
wild-type parent through the whole catalytic gap — four of those against wild-type *NR4A3*. Those rows carry
`do_not_order`, as does every one of the 249 records whose `mature_parent_duplex_through_gap_bp`
reaches the criterion applied throughout; three further records carry the flag for the separate
un-rearranged-allele reason of §2.6, so 252 of the 780 carry it in all. An empty `do_not_order` is not a clearance: the
flag is set at ten base pairs, while 175 of the 190 panel designs pair a parent through the whole
gap at seven and 181 do so at any length (§2.9). A typeset table cell is not a
machine-readable record — whether a sequence and the column beside it stay separate on extraction is
a property of the reader's software — and the sequences here are 16 to 20 bases in which a single
substitution changes what the molecule does. The bases alone are also not the reagent: the geometry
column denotes locked-nucleic-acid wings around a DNA gap on a phosphorothioate backbone (§6), and
unmodified DNA of the same sequence is a different molecule about which nothing reported here holds.

**Availability.** All code, graded artefacts and per-design tables are public at the repository
`github.com/trimcrae/Rare-cancers`, and are to be released as a single archived version deposited
from it
[ARCHIVE DOI — PLACEHOLDER, AUTHOR TO SUPPLY BEFORE DEPOSIT: the archive has not been deposited and
no digital object identifier has been reserved, so this citation does not yet resolve]. Every result
reported here is re-derived, without network access or credentials, from the committed artefacts in
that repository, which is what a reader can check today. That claim is meant to be checked rather
than accepted: `./scripts/regenerate_aso_chain.sh` re-derives, in dependency order, the artefacts
its own step list names: the duplex thermodynamics and the chance baseline, the locus collapse, the
per-junction and non-canonical-acceptor tables, the four figures and their provenance record, the
submission tables, references and metrics, the canonical sequence file, the prior-art evidence and
the archive manifest. It re-runs the consistency, citation and style gates in about two and a half
minutes on four cores with no network. Four producers are not in that list and have to be run
separately to re-derive the central negative and its null: the design panel (`junction_aso.py`), the
mature-parent screen (`aso_parent_gap_pairing.py`), the pre-mRNA screen (`aso_premrna_offtarget.py`)
and the null ensembles (`aso_parent_null.py`). Two of the four read committed caches with no switch;
the design panel takes its transcript models from the committed cache under
`TRANSCRIPT_SOURCE=cache`, and the pre-mRNA screen scans the committed fetch under `--offline`. `ASO
CHAIN OK` is a statement about the artefacts the script regenerates and not about those four. The
artefacts are current where it reports `ASO CHAIN OK` and rewrites no artefact
but one: the archive manifest records the commit it is committed in, which a committed file cannot
hold, so that single row moves on every run and is not evidence of staleness. The chain additionally
needs the repository's `literature-cache` branch, which carries the prior-art retrieval indices and
which a clone fetches but a file archive does not; `git fetch origin literature-cache` supplies it.
A fuller guard suite in the same repository re-derives each reported number from its artefact and
fails if the two diverge; its invocation is documented there rather than here, since it is
repository tooling and not a step in reproducing a result. Which file holds which number is given
here rather than left to a search. Under `research/modalities/`: the design panel is
`nr4a3-fusion-junction-atlas.json`; the transcript models `emc-construct-inputs.json` and the
unspliced sequence and exon coordinates `aso-premrna-sequences.json`; screen 3
`aso-premrna-offtarget.json`, screen 4 `aso-parent-gap-pairing.json` and its nulls
`aso-parent-null.json`, screen 5 `aso-genome-offtarget.json`; the alignment screens one file per
junction under `junction-aso-offtarget-*.json`; the free energies and the four design rules
`junction-aso-thermo.json`; the chance baseline `offtarget-chance-baseline.json`; the expression
readings `aso-offtarget-tissue-expression.json`; and the gap-length comparison
`aso-gap-length-tradeoff.json`. The *TCF12* base-level breakpoint assignment of §2.3 is
`research/manuscripts/aso/tcf12-breakpoint-assignment.json`. Regenerating the specificity screens
from scratch is not
offline, because the alignment screen queries NCBI BLAST and the exhaustive transcript scan downloads
the GRCh38.p14 RefSeq RNA set, but no reported number requires it: each screen's hit set is archived
and the re-scores hold it fixed. The pre-mRNA and mature-parent screens are fully offline against the
repository, since the retrieved unspliced sequence and exon coordinates are committed to it and will
travel into the archive unchanged.

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
acceptor-exon pairs across *EWSR1*, *FUS*, *TAF15*, *TCF12* and *TFG* — named here in the order the
panels draw them — graded against the frame condition. The grid is one grid, drawn as two
side-by-side continuations to fit the page, so the three acceptor columns appear twice; a pair is
not duplicated by appearing in the second block.
Green marks the 38 frame-compatible pairs the panel is emitted at; the three refusal classes are
greys, lightest to darkest: out of frame (39), acceptor exon carries no coding sequence (77), and
acceptor outside the plausible resumption range (77). The panel repeats this key and these counts
beside the grid, so it can be read without this caption. Rows are donor exons grouped by partner; columns are *NR4A3* acceptor exons 2 to 4, the declared
acceptor window, and not all eight exons of the transcript — the 231 pairs are every donor exon
against that window rather than against the whole gene. Two acceptor columns
are refused in every pair for structural reasons, so the 38 in-frame junctions lie in a
single column. The five partners are those for which transcript models are held here; *PGR*, the
sixth partner §2.6 reports a single seam at, is not modelled and has no row.

**Figure 2. One 16-mer spans three partners' breakpoints.** The junction windows of *EWSR1* exon
12, *TAF15* exon 11 and *FUS* exon 10 joined to *NR4A3* exon 3, aligned at the breakpoint. Blue,
donor exon; green, acceptor exon; positions at which the three donors differ are boxed as well as
coloured, for greyscale and colour-blind readers. The shaded box is
the target window of 5′-GGGCATATCATCAAAC-3′, with the 5-6-5 locked-nucleic-acid (LNA)/DNA/LNA gapmer architecture below it; the
note beneath the panel gives its gap-level margin of three. The three donors are the FET family — *FUS*, *EWSR1* and *TAF15* — and they are identical over
the ten nucleotides before the breakpoint, which is what makes one oligonucleotide
junction-spanning at all three junctions. Two of the three drawn junctions are not reported in
any patient: the exon-resolved *TAF15* breakpoints in this disease are at exon 6 rather than exon 11,
and no exon-resolved *FUS* breakpoint has been published at all (§2.2). This is a statement about
sequence, not a claim that one reagent serves three patient groups.
Coverage is predicted from sequence and has not been measured.

**Figure 3. The margin a longer catalytic gap wins is the gap DNA a parent pairs at the design's own seam.** (A) The
best-margin design at *EWSR1* exon 12 joined to *NR4A3* exon 3, drawn at 5-6-5, 5-8-5 and 5-10-5
with the wings held at five nucleotides. Every base inside the catalytic gap comes from the donor
exon or from the acceptor exon, so the junction-unique bases on the shorter side and the bases one
wild-type parent pairs on the longer side tile the gap and sum to it. (B) Every fusion-specific
design in all three geometries, 798 over 38 junctions, plotted as gap-level margin (abscissa) against
the contiguous run of gap DNA one of the design's OWN two parents pairs at its seam (ordinate).
That is not the quantity the ⚑ markers and the do-not-order verdicts are set on. Those come
from a SEARCH over all six mature parent transcripts, and the two separate: for the molecule drawn
in (A) this figure draws 3 nucleotides where Tables 2, 3, 5 and 7 print an 8 bp duplex against
wild-type *TFG*. The two also move in opposite directions across the geometries — the searched
duplex FALLS (181 of 190, then 130 of 266, then 87 of 342 pair a parent at any length) and is flat
at the ten-base-pair criterion (87, 88, 87), while the quantity drawn here RISES (76 of 190, 228 of
266, 342 of 342). A longer gap concedes seam-level parent DNA; it does not concede more of the
liability this paper condemns. In (A) red marks the gap bases contributed by the donor exon,
green those contributed by *NR4A3*, and pale grey the LNA wings, which are not cleaved; the shorter
of the two coloured runs is the margin and the longer is what a wild-type parent can pair, so which
colour is which depends on the register — the junction drawn here divides its gap evenly in all three
geometries, and 76 of the 190 designs at 5-6-5 have the longer run on the donor side; in (B) the three geometries are blue (5-6-5), orange (5-8-5) and purple
(5-10-5). Both panels repeat these keys beside the drawing. Marker area is the number of designs at that
point and the label is that count; the three lines are drawn from the identity, not fitted, and it
holds for each design individually rather than on average. Within one geometry the two move
inversely along a line of slope −1, and both axes are drawn at the same scale (32 px per nucleotide) so that slope is true as plotted rather than only in the units;
a geometry's ceiling on margin is half its gap rounded down, and
clearing it means a longer gap and a higher parent-paired run at every register (§2.9, Table 7).

**Supplementary Figure S1. Transcriptome load per molecule against chance expectation.** Per
molecule, not per design record: the 190 records are 176 distinct oligonucleotides and each is
plotted once, so this series is 176 bars and not 190. Bars are
green at or below the chance line and red above it, which is redundant with each bar's height
against that line and carries no information of its own. Each bar is one distinct
oligonucleotide's count of exact plus ≤1-mismatch matches over 186,185 transcripts, ranked. The 190
design records at real exon junctions collapse to 176 molecules, because nine of the 16-mers are
junction-spanning at more than one partner's junction at once — five at three junctions and four at two — and
each of those is one physical oligonucleotide, plotted once rather than repeatedly (marked). The line
is the number of such matches expected for an arbitrary 16-mer under an independent-uniform-base
null, 8.2, computed against the scan's measured 718,571,139-nucleotide span;
118 of the 176 fall at or below it and 58 exceed it. Ten further designs from
modelled breakpoints not built from a spliced transcript model are excluded, and are released with
the artefacts; four of those ten carry loads ABOVE the chance line, at 16 to 95 matches, so the
excluded set is not a set of quiet designs and the panel understates the corpus rather than
flattering it. Forty of the 176 return no match at all; their bars have zero height and so draw
nothing, which is why the left of the panel reads as empty rather than as the start of the series.
It is an expected count: the observed mean is 9.2, a ratio of 1.12, while the
median is 3, so real transcript sequence produces a long right tail the null cannot
rather than a uniform shift away from it. The line
separates "more than chance" from "at chance" and is not a significance test; the counts are
predictions from sequence search, not measured off-target activity.

## Declarations

**Research use only, and not for administration to any person or animal.** Every oligonucleotide
sequence in this manuscript, its Supplementary Information and its tables — the two lead reagents and the two
named for coverage, the three named as not to be used, the second-geometry control and any scrambled
control drawn by the procedure of §4.4,
every design in the released panel, and the non-canonical-acceptor designs reported beside that panel
rather than pooled into it — is a research reagent intended solely for laboratory investigation.
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
`fusion-junction-aso-supplementary-information.md`, rendered to PDF from the same builder as this
manuscript and deposited as a separate file beside it, and included in the archive below.

**Data and code availability.** [ARCHIVE DOI — PLACEHOLDER, AUTHOR TO SUPPLY BEFORE DEPOSIT: no
digital object identifier has been reserved and this citation does not yet resolve], to be deposited
from `github.com/trimcrae/Rare-cancers`.
`fusion-junction-aso-archive-manifest.json` lists every archived file with its SHA-256; it is
generated with the archive and travels with the deposit.
Two renderings of this manuscript travel with it and their text is the same:
`fusion-junction-aso-research-article.md` in submission format is the version of record, the one to
cite and to deposit onward, and the typeset preview beside it is the same text set as a printed
article. `fusion-junction-aso-submission-tables.md` is the machine-readable copy of Tables 1 to 7,
whose content is printed in both renderings.
Artefacts include the graded junction
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

That check should not be read as either of two things. It is not external review: the same author prepared
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
2026, the first commit of the design code, to the commit this version was built from, whose date the
repository's commit record carries; an end date typed here would exclude the deposited version from
its own declared span, since preparing that version is itself part of the work. That record
names two model versions over the span and no other: Claude Opus 4.8 for the design and screening
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

**Author contributions.** T.D.M. is the sole author and directed all work reported here:
conception, design, analysis, code and manuscript. The use of a language model in producing the
code and the manuscript text is declared above and is not restated here as authorship.

## References

*The numbered entries are listed in `fusion-junction-aso-submission-references.md`, generated
from retrieved bibliographic records. Each superscript above carries its PubMed identifier in a
non-rendering comment, and the numbering is assigned from those identifiers by order of first
citation, so a superscript and its reference cannot drift apart. The external data records this work
uses — a Gene Expression Omnibus series, two GenBank deposits, four GenBank patent sequence records,
a DepMap release and three Cellosaurus cell-line records — are cited in the text by accession and
are listed in full, with their repositories, under `Data sources` in the same file. They carry no
PubMed identifier and so take no number.*
