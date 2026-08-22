---
id: DOC-FUSION-JUNCTION-ASO-JOURNAL
title: "Two NR4A3 fusion-junction gapmers for extraskeletal myxoid chondrosarcoma, screened against wild-type parents"
level: L3
kind: manuscript
status: live
canonical_for:
  - the journal-submission form of the fusion-junction ASO work
purpose: >
  The journal submission for PUB-ASO. It names the reagents to synthesise, the material to test them
  in and the experiment that would falsify the ranking. The full screen, its bounds and its methods
  are in fusion-junction-aso-research-article.md, prepared for bioRxiv deposit and not yet posted,
  which this manuscript cites as its extended report; the numbers live in the artifacts under
  research/modalities/ and are restated here where the argument needs them, each pinned or
  reproducible from those artifacts.
scope: >
  Computational design and specificity screening only. No wet-lab experiment was performed, and
  nothing here asserts efficacy, potency, safety, a therapeutic window, delivery to a tumour, or
  clinical readiness for any sequence. Every sequence named is a research reagent for laboratory
  investigation only and must not be administered to any person or animal. This block is stripped
  from the PDF builds and reaches no reader of the submitted article, so it is a routing copy: the
  operative statements live in the Abstract, in the reagents section and in Declarations.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-20
last_verified: 2026-08-22
related: [DOC-FUSION-JUNCTION-ASO-SUBMISSION]
---

# Two *NR4A3* fusion-junction gapmers for extraskeletal myxoid chondrosarcoma, screened against wild-type parents

**Author.** Tristan D. McRae

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [0000-0002-1823-1451](https://orcid.org/0000-0002-1823-1451)

**Running title.** Junction gapmer reagents for EMC

**Keywords.** antisense oligonucleotide; gapmer; RNase-H1; fusion transcript; NR4A3; extraskeletal
myxoid chondrosarcoma; off-target screening

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma defined in most cases
by an in-frame fusion of a variable partner gene to *NR4A3*. That junction is present in no
normal transcript, so an antisense gapmer could in principle cleave the fusion and spare both parents. This work is
computational: nothing was synthesised or tested, and every sequence named is a research reagent
not for administration. Of
190 junction-spanning 16-mers tiled at 5-6-5 across the 38 in-frame junctions of five
modelled partners, 87 let a mature wild-type parent transcript pair their whole catalytic gap over
ten or more contiguous base pairs, 61 of those against wild-type *NR4A3* itself. Ten is a
convention rather than a measurement, and chimeras built at real exon termini of the same
transcripts meet the same screen at 40.6% against the panel's 45.8%, so most of that liability is
what joining two exon termini of these genes gives rather than anything specific to this disease. Two reagents are
named at the two most frequently reported breakpoints: 5′-GGGCATATCATCAAAC-3′ at
*EWSR1* exon 12 and 5′-GGGCATATCTTGTGTG-3′ at *TAF15* exon 6, both at the panel's top gap-level
margin of three, and their longest wild-type parent duplexes through the whole gap run to eight and nine base pairs respectively. Five test
articles are named: three engineered constructs, two of them at these junctions, and two
fusion-positive EMC cell models whose reported *NR4A3* exon-2 acceptors are matched to different
designs. The design pipeline is released; its published-breakpoint list waives
seams that would otherwise be refused rather than gating which junctions it will design for.

---

## 1 · Background

EMC is defined in the large majority of cases by an in-frame fusion of *EWSR1* to
*NR4A3*,<sup>1</sup><!--PMID:8634690--> with *TAF15* a substantial minority and *TCF12* and *TFG*
rare.<sup>2</sup><!--PMID:32572850--> The disease responds poorly to conventional cytotoxic
chemotherapy,<sup>3</sup><!--PMID:41055792--> though responses do occur: one molecularly confirmed
series recorded four partial responses in ten evaluable
patients.<sup>4</sup><!--PMID:24345066--> A tyrosine-kinase inhibitor trialled in it gave disease
control more often than response — a reading composed from the response categories as the review
above reports them,<sup>3</sup><!--PMID:41055792--> rather than from a disease-control figure stated
in the trial report.<sup>5</sup><!--PMID:31331701-->

The fusion junction is the one feature of an EMC tumour that exists at the RNA level and in no normal
cell. An antisense gapmer tiled across it recruits RNase-H1 to cleave the transcript it pairs, and
the six-nucleotide DNA gap at the centre of a 5-6-5 architecture is where that cleavage occurs.
Junction-directed nucleic-acid agents are a thirty-five-year lineage, reported against six fusion
oncogenes; two of the six were antisense oligonucleotides and the rest RNA-interference agents, one
delivered from a lentiviral vector rather than administered as an
oligonucleotide.<sup>6,7,8,9,10,11</sup><!--PMID:1794439,9049825,33241214,21846246,23052253,37980543-->
No such design is reported for any *NR4A3* fusion in the literature retrieved here, and that absence
is why this work exists.

What a junction design must survive follows from its construction. Both halves are parent-gene
sequence, so each parent matches roughly half the oligonucleotide, and half-identity falls far
outside the mismatch budget of a conventional off-target search: a parent is not returned as a
near-match. RNase-H1 does not require the whole duplex, only that the gap be paired — a premise
adopted here rather than established, and one whose length requirement is stated in a different unit
from the criterion this paper screens on. The requirement is reported as a DNA gap of at least six
nucleotides, with seven to ten the working range; the screen below counts a liability only at ten
contiguous base pairs of duplex through that gap, a length of hybrid rather than a count of gap
nucleotides. Whether a wild-type parent pairs the catalytic gap contiguously is therefore a separate
question from overall similarity, and it is the one this work puts to all 190 designs before
recommending any.

## 2 · The reagents

The two reagents named for synthesis are the best available designs at the two junctions with a
published exon-resolved breakpoint and the highest reported prevalence:
5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 joined to *NR4A3* exon 3, and 5′-GGGCATATCTTGTGTG-3′ at
*TAF15* exon 6 joined to *NR4A3* exon 3 (Table 1). Exon numbers throughout are transcript exon
indices counted from the transcript 5′ end, including non-coding exons; that differs from
coding-exon indexing for *TCF12*, *TFG* and *NR4A3*, and an acceptor exon number read under the
wrong convention selects a different reagent. Both hold the panel's top gap-level margin of three —
three junction-unique bases inside the catalytic gap on the shorter side of the breakpoint — and
neither pairs a wild-type parent through the gap at the ten-base-pair criterion §3 adopts.

Both sit close to that criterion. The *EWSR1* reagent's longest wild-type parent duplex through the
whole gap is eight base pairs and the *TAF15* reagent's is nine, both against wild-type *TFG*, so
where the cut is set decides how they read: at eight both fall inside the class this work marks as
not to be ordered, at nine the *TAF15* reagent alone does, and only at ten does neither. Both also
pair a wild-type parent through part of the gap at the *NR4A3* exon-2/exon-3 seam their acceptor
halves share, neither in full; those partial duplexes are not counted here and have not been
measured reagent by reagent. One hazard of the design space belongs beside the sequences:
consecutive registers of one seam differ by a single-base slide and can carry opposite verdicts, so
a design that pairs a parent through its whole gap sits one nucleotide from one that does not
(Table 2), and neither member of such a pair may be substituted for the other.

Predicted transcriptome load separates the two: 123 gap-paired sense-strand near-matches for the
*EWSR1* reagent at a deeper search ceiling than the default, against eight for the *TAF15* one, both
read from the alignment screen rather than from Table 1. What the count is made of bounds it — 82 of
the 123 are predicted transcript models rather than curated records and 32 of the remaining 41 are
one gene — so it is a search result over a database that includes predictions, not a census of
expressed transcripts. The *EWSR1* reagent also carries a sense-strand near-match in wild-type
*TAF15* precursor RNA at two mismatches, one inside the catalytic gap, spanning an intron-exon
boundary: the cost of the same ten shared donor bases that let one oligonucleotide span the *EWSR1*,
*TAF15* and *FUS* breakpoints at once (Figure 1). The *TAF15* reagent carries no sense-strand
precursor site. Both loads are predictions from sequence search rather than measured off-target
activity, and neither is a disqualification.

Discounted by the breakpoint distribution of an 18-case series,<sup>12</sup><!--PMID:12378528--> the
two junctions account for 68.4% of molecularly confirmed cases in a 58-case
cohort,<sup>13</sup><!--PMID:36948401--> roughly two thirds. That prices which published junctions
the two reagents address; it is not a coverage measurement, no patient having been screened with
either sequence. The range 39.9% to 82.8% quoted with it is not a confidence interval and carries no
nominal level — it is what the figure becomes when each breakpoint fraction is taken to its own
Wilson bound while the partner shares are held at their point estimates — and it assumes a
breakpoint distribution reported in one cohort transfers to a second collected twenty-one years
later. The *TAF15* arm is priced at three of three reported breakpoints, an upper bound rather than
an estimate, and reference 14 reports two major *TAF15*::*NR4A3* isoforms.

That figure is not a ceiling. A third design, 5′-GGGCATATCTCCACGG-3′ at *EWSR1* exon 13 joined to
*NR4A3* exon 3, is already tiled and screened at the same top margin; its junction is the type-5
transcript named in the same sentence of the 18-case series that supplies the exon-12 count, and
adding it would take the figure above to 79.0% — about ten percentage points for one further
oligonucleotide with no new screen. It is not named for synthesis on two grounds. Its off-target
axes point in opposite directions, the lighter transcriptome count against the heavier tissue
exposure, so it is not preferable on either; the extended report sets both out design by design. And
no test article in §4 is established as carrying its junction: under the reported exon-2 reading of
the two cell models none does, and under the exon-3 reading §4 says also survives, USZ20-EMC1 would
carry it exactly. That is a reason to settle the acceptor index before ordering rather than a
property of the design.

## 3 · Selection from a panel of 190 designs

The two reagents above are what survived a screen applied uniformly to the whole panel. Across the
38 in-frame junctions of five modelled partners, 190 junction-spanning designs were tiled and put
through five specificity screens. Of those, 87 let one of six mature wild-type parent transcripts
pair their entire catalytic gap over a contiguous duplex of at least ten base pairs, and 61 of the
87 do so against wild-type *NR4A3*; 85 of the 87 are paired by one of the design's own two parent
genes rather than by an unrelated transcript. A second class is invisible to any screen over mature
transcripts: 19 designs carry a sense-strand near-match in parent precursor RNA that pairs the gap in
full and touches intronic sequence. Taken as a union rather than a sum, the two screens condemn 93 of
the 190. A design whose gap carries a mismatch is scored zero rather than short, so the 87 bound the
fully-paired class and not the whole parent liability; the mismatched class is not measured here.

Lengthening the catalytic gap does not remove this liability, for a reason that is arithmetic rather
than empirical: every base inside the gap comes from the donor or the acceptor exon, so the
junction-unique bases on the shorter side and the bases a parent can pair on the longer side tile the
gap and sum to it. A longer gap buys margin only by conceding parent-paired gap DNA at the design's
own seam. Screened across 5-6-5, 5-8-5 and 5-10-5 over the same 38 junctions, the count pairing a
parent at the ten-base-pair criterion does not fall while the share does — 45.8% to 33.1% to 25.4% —
because a longer oligonucleotide admits more junction-spanning registers per seam; and at 5-10-5 a
ten-nucleotide gap is itself a ten-base-pair hybrid, so the three are not a reading at a constant
substrate. The extended report gives the counts.

Three designs clear every screen applied here, two at any parent-duplex threshold and the third only
at the ten-base-pair criterion, pairing eight base pairs of wild-type *NR4A3* and failing at any cut
of eight or less. None sits at a junction any patient is reported to carry, which makes them
mechanism controls rather than candidates. Selecting within each junction rather than across the
panel is what makes the two named reagents available: 35 of the 38 junctions have a design that
clears the parent screen, and all five junctions with a published exon-resolved breakpoint have one.
Both readings are properties of the cut. At nine base pairs 31 of the 38 still clear and three of the
five published ones do; at eight, 23 and two; at seven, 9 of the 38 and none of the five; at six, 6
of the 38 and again none. Those cuts are whole-duplex run lengths, not the enzyme's own unit, which
is the DNA gap: the geometry holds six gap nucleotides against every target, so no cut on this ladder
is the enzymology restated. The availability the two named reagents rest on holds at the adopted
criterion and fails at a run cut of nine, where the *TAF15* junction's best design is itself liable
— the sense in which the criterion is a convention rather than a measurement.

Read as design counts rather than junction counts, the loose cuts condemn almost everything: the same
screen returns 175 of 190 at seven base pairs and 181 at six. Neither is a larger finding, because
the null moves with the cut — the strongest of the ten null ensembles reaches 91.4% at seven against
the panel's 92.1%, and at six it exceeds the panel outright.

Two bounds on the cleanliness claim are load-bearing. The alignment screen is heuristic and censors
on a requested hit list and a retained window, leaving 47 of the 183 filtered designs with lists
short enough to assess at all, so a count of clean designs is a floor over that subset rather than a
total over the panel. And search depth moves the result: most of the designs clean at the default
ceiling are not clean at a deeper one, as the extended report shows design by design.

The ten-base-pair criterion is adopted rather than measured, and the comparison against null models
does not resolve an excess specific to this disease. Mononucleotide scrambles — the weakest of the
ten nulls screened, and not the dinucleotide-preserving control §5 prescribes — meet the parent
screen at 6.2% against 45.8% for the panel, but chimeras built at real exon termini of the same two
transcripts, at junctions almost never reported in a patient, meet it at 40.6%. The adopted cut does
not escape that comparison: at ten the strongest null's 40.6% falls inside the panel's own 95%
interval on 45.8%, as it does at every cut from seven to thirteen but eleven, and which ensemble is
strongest changes along the ladder. The comparison is also narrower than it reads, because the panel
arm is itself mostly unreported junctions: 25 of the 190 designs sit at the five junctions with a
published exon-resolved breakpoint and the other 165 do not, which is the property the chimeric null
is discounted for. Most of the liability is therefore what joining two exon termini of these genes
gives, and across cuts of six to thirteen base pairs the excess of the observed rate over the
strongest null changes sign four times. No cut in that range is a boundary the data picks out.

## 4 · Test articles

Five test articles bear on the junctions this panel designs against, and they divide into two
sources with opposite limits. Every design in the panel joins its donor to *NR4A3* exon 3; the two
cell models are reported at exon 2, so they carry a panel junction only under the exon-3 reading
their acceptor index leaves open.

Three are engineered constructs from a published functional study,<sup>14</sup><!--PMID:31020999-->
whose exon spans that paper states verbatim. Two of them, E-N and T-N*, carry exactly the two
junctions the reagents above span, so both named reagents have a stated test article. Rebuilding the
constructs is the faster route, and its critical path contains no laboratory that has to answer an
email. What it cannot buy is biological relevance: a complementary DNA over-expressed in a
heterologous background is not the disease, so such an experiment speaks to junction-selective
knockdown of the intended transcript and not to activity at endogenous expression from an endogenous
locus.

The other two are patient-derived, identity-clean models reported with two EMC
tumours,<sup>15</sup><!--PMID:36316541--> USZ20-EMC1 (RRID:CVCL_C6MX) and USZ22-EMC2
(RRID:CVCL_C6MY) — the only source of a fusion-positive EMC cell identified here. They are available
on request from the originating laboratory with no repository deposit, and they are slow, at
reported doubling times of five to six days as sarco-spheres passaged every two to three weeks,
which constrains any exposure window. Their fusions are reported as *EWSR1* exon 13 and *TAF15* exon
6 joined to *NR4A3* exon 2 rather than exon 3, but that acceptor index is not settled: the report
carries no sequenced exon-exon boundary, no transcript accession and no junction sequence, so two
readings of the exon label survive — and this work's own withdrawn version arose from an error of
exactly this class. Reagents exist at both acceptors, so each line has one, and in neither case is it
the same molecule as the reagent named above for the exon-3 acceptor: 5′-AGTGGGCTCTCCACGG-3′ at
*EWSR1* exon 13 and 5′-AGTGGGCTCTTGTGTG-3′ at *TAF15* exon 6, both at the panel's top margin.
Neither reaches the ten-base-pair criterion, and their longest wild-type parent duplexes through the
whole gap are eight base pairs against wild-type *EWSR1* and nine against wild-type *NR4A3* — the
second against the acceptor parent on which §5's selectivity ratio is defined, a closer call than
either exon-3 reagent presents. A reagent selected for one acceptor is not valid for the other.

One requirement is upstream of all of them. The breakpoint of the cell line or tumour used as the
test article must be established at nucleotide resolution by RNA sequencing before any
oligonucleotide is ordered: every design here is specific to the exon pair it was tiled at, and none
is valid for an unverified junction. Routine diagnosis does not supply the seam — break-apart
*NR4A3* fluorescence in situ hybridisation detects a rearrangement irrespective of
partner,<sup>3</sup><!--PMID:41055792--> so on its own it locates neither the partner nor the exon
pair.

## 5 · The falsification experiment

The design that would resolve the central uncertainty — an isogenic fusion-positive against
fusion-negative comparison — has been run in an analogous fusion sarcoma: antisense oligonucleotides
against *NAB2::STAT6* in solitary fibrous tumour, evaluated against CRISPR-engineered isogenic
pairs, reduced fusion expression by 58% and proliferation by 22% in
vitro.<sup>16</sup><!--PMID:37370737-->

Three controls are required, and a knockdown assay alone distinguishes none of them. A
positive-control gapmer against an abundant housekeeping transcript separates failed delivery from a
reagent that reached its target and did not cleave it; it must carry the same 5-6-5
β-D-oxy-locked-nucleic-acid phosphorothioate geometry, since uptake and endosomal release track
chemistry class. A dinucleotide-preserving scramble of that chemistry separates the backbone-class
component of toxicity; it does not hold a 5′ guanine run, which has to be imposed by hand where the
test article carries one. That scramble must itself pass the mature-parent screen before synthesis,
because 10.0% of dinucleotide-preserving scrambles pair a parent's whole catalytic gap at the
ten-base-pair criterion and 3.9% do so against wild-type *NR4A3*; it must be reverse-complemented
first, since the screen takes the target window and screening the ordered strand returns a false
pass. A scramble
reaching the criterion is redrawn rather than adjusted: a single-base edit moves the design to a
neighbouring register whose verdict may differ (Table 2). The third control, a fusion-negative
isogenic comparator, supplies the discrimination readout the other two do not and has to be
engineered; no supplier is named here. A fourth arm exists but is not free: the three
all-screen-clear designs of §3 sit at *FUS* exon 8, *TAF15* exon 1 and *TCF12* exon 7, none of them
carried by the five test articles of §4, so running it means three further constructs.

The decision threshold should be fixed before the experiment. Selectivity is the wild-type *NR4A3*
half-maximal knockdown concentration divided by the fusion's, from a matched dose-response in the
same wells, at a cut of 5.0 adopted as a convention rather than measured. A ratio of residual
transcript at a single dose is not commensurate with it and must not be read against the same cut:
that ratio is bounded above by one divided by the fusion knockdown's complement, so at the 58% above
it cannot exceed approximately 2.4 however selective the reagent is. The same anchor bounds the dose
range. On a unit Hill slope a reagent whose ratio is exactly 5 puts the wild-type midpoint at a dose
where the fusion is already 83.3% knocked down, and at 58% the wild-type is only 21.6% knocked down
— short of the half-maximal reading its own concentration is defined by. The range must reach far
enough to resolve that midpoint, and the ratio is reportable only where the wild-type knockdown is
resolved above a pre-stated limit of quantification.

The replicate count follows from the variance rather than being asserted. At a replicate standard
deviation of 0.35 on the natural-log scale, six independent biological replicates give about 80%
power to falsify a true selectivity of 3 and three give about 30%. Above a realised standard
deviation of about 0.65 at three replicates no observed ratio at or above one can put the upper
limit of a two-sided 95% interval below 5, so the test can fail only on a reading that is itself
anti-selective. Such a test is void, and voidness is a property of the assay's realised variance
rather than of the design — so a pilot-based gate on the population variance bounds it from one side
only and does not guarantee a run that can fail. Where a pilot's bound lies at or above the void
figure for the count proposed, the decision is a larger replicate count, or
no falsification test at all, and never three: the gate is always satisfiable by adding replicates, so "more replicates" on
its own is not an answer. The extended report gives the void figures by replicate count, the gate's
construction and the residual void probability under it. Falsification is
read from the interval's upper bound and never from a point estimate; a run that is void, or one
whose dose range never resolves the wild-type midpoint, is uninformative and must not be recorded as
a reagent clearing the cut by default.

Two limits of that threshold belong with any result. It is defined on wild-type *NR4A3*, the
acceptor parent; no donor parent is read by the ratio, so a reagent can clear the cut while pairing
a donor transcript through its whole catalytic gap. Donor wild-type transcript should be measured in
the same wells and reported beside the ratio against no cut, because no retrieved measurement bounds
the parent case. A result on the stated cut can therefore falsify the ranking and cannot falsify the
rationale. Multiplicity is bounded here rather than dismissed: the design is closed and holds two
ranking tests, one per named reagent at its own junction, the three all-screen-clear designs being a
mechanism control that is not read against the cut. Two tests at a nominal one-sided 2.5% carry a
familywise error rate of 4.94%, and that is the rate this design runs at; reading the two exon-2
reagents of §4 against the same cut makes four tests at 9.63%, and adding the three control designs
seven at 16.24%. The replicate counts above hold per test at the nominal level whatever the family
size, so long as no correction is applied — and which level a correction targets is the whole of it,
since holding the family to the 2.5% a single test runs at drops six replicates below two thirds
power and calls for eight. Whether to correct, and to what, belongs in the pre-registration.

## 6 · Beyond the panel

The panel is bounded by what has been sequenced rather than by what can be designed, and the
procedure that produced the 190 designs is released unchanged with the artefacts. It is not a
turnkey service for an arbitrary breakpoint: the builder's published-breakpoint list is a waiver
list rather than a gate, admitting seams that would otherwise be refused for a non-coding acceptor
or an out-of-frame join, every entry sitting at a *NR4A3* exon-2 acceptor. A new seam that needs
such a waiver requires the list to be extended before the procedure will emit for it, and a seam
that needs none is emitted without any check that a patient has been reported to carry it.

A design is certifiable where all five screens could be run on it and it cleared all five; a design
one screen cannot address is uncertifiable whatever the other four return. By that definition the
reagent for the third engineered construct of §4 is uncertifiable, its seam lying outside the
compartment three of the five screens can address at all. The two that can — the precursor-RNA and
genome arms — did run there and agree design by design, both clearing the seam's top-margin design
and both condemning a lower-margin one at a wild-type *NR4A3* site each records as pairing the whole
catalytic gap. Two screens agreeing is not the clearance the other three would have to supply. What
the procedure yields is a candidate, not a validated reagent.

## 7 · Discussion

Designability is not the constraint in this disease. Junction-spanning designs exist at every
in-frame *NR4A3* fusion junction modelled here, and 35 of the 38 have one clearing the parent screen
at the adopted criterion — a reading that is a property of the cut, as §3 sets out.

The constraint is discrimination between the fusion and its parents, and it is not resolved here. A
junction design's most plausible wild-type liability is its own parent, in the mature transcript or
across a splice junction in precursor RNA. Both compartments are searched before any molecule
exists, but not on comparable terms: the mature-transcript screen condemns on a ten-base-pair duplex
through the gap, the precursor arm on a hit at up to two mismatches with the gap fully paired, so
neither restates the other. Nor may their counts be added, because a design condemned in both is one
design — which is why §3 reports their union rather than their sum. A third compartment is searched only in the extended
report: the patient's own un-rearranged *NR4A3* allele, at the two-mismatch ceiling §8 states, which
bounds its class from below. No design this panel selects is condemned by it, but two of the
reagents §4 names sit outside the panel, and it is what excludes the two registers neighbouring the
*EWSR1* exon 13 reagent while clearing the reagent itself — the register hazard of §2 arriving from
a compartment the panel's own selection never has to consider.

The four reports of parental sparing cited
here<sup>8,17,9,10</sup><!--PMID:33241214,36265509,21846246,23052253--> were all made on molecules
already synthesised. No survey of published design pipelines was performed, so the claim that the
screen-before-synthesis step is what is new is a statement about this literature as retrieved and
not a priority claim. The premise that sparing wild-type *NR4A3* is worth a specificity cost also
deserves examination. *NR4A3* has two close paralogues and the family is functionally redundant
where tested,<sup>18,19</sup><!--PMID:29343483,25446259--> which cuts against the premise. Against
that, mice carrying reduced gene dosage across *NR4A1* and *NR4A3* develop mixed
myelodysplastic/myeloproliferative neoplasms,<sup>20</sup><!--PMID:21205929--> so loss of *NR4A3* is
consequential once paralogue reserve is reduced, and the family is not uniform in direction: in
murine atherosclerosis *NR4A1* and *NR4A2* attenuate lesion formation while *NR4A3* aggravates
it.<sup>21</sup><!--PMID:24005216--> The evidence is not decisive either way, and both sides are
cited here.

Three limits bound what any test of these reagents could show. All five screens address
hybridisation rather than cleavage, and none establishes that a predicted duplex forms or is cut.
The method-level novelty is nil, junction-directed oligonucleotides being long established; what is
new is the indication and the screen applied before synthesis. And systemic, antigen-dependent
delivery of an oligonucleotide to a solid tumour remains unsolved, which is the gate this modality
faces after any result reported here. Nothing in this work addresses it. One constraint sits above
the others and no reagent choice moves it: every source of a test article named here ends at someone
culturing cells, so the rate-limiting step is a laboratory rather than a line, a construct or an
oligonucleotide.

## 8 · Methods

All analyses are computational and use public data. No laboratory work was performed. Full
parameters, every screen's settings, the complete bounds on each claim and the per-design tables are
in the extended report named under Data availability.

Canonical transcripts for the five partner genes and for *NR4A3* were obtained from
Ensembl.<sup>22</sup><!--PMID:39656687--> Junction-spanning 16-mer gapmers were tiled in a 5-6-5
β-D-oxy-locked-nucleic-acid/DNA/β-D-oxy-locked-nucleic-acid
geometry,<sup>23</sup><!--PMID:24981949--> one design per register at which the breakpoint falls
inside the six-nucleotide DNA gap, which admits five per junction. That gap is the shortest length
the cited source calls sufficient rather than its preferred one: it reports six nucleotides as
necessary for noteworthy RNase-H activity, seven as allowing complete activity and seven to ten as
optimal. Six is used because the panel is built to be screened and the genome-wide arm is not
available above a 16-mer; a longer gap is a design choice this work does not test. A design's
gap-level margin is the count of junction-unique bases inside the gap on the shorter side of the
breakpoint.

Five specificity screens were applied: an alignment screen against human RefSeq RNA, classifying
each near-match by whether the catalytic gap is paired; an exhaustive transcript scan complete for
substitutions within a one-mismatch budget; a screen of the parents' unspliced sequence; a
mature-parent screen recording the longest contiguous duplex any of six wild-type parent transcripts
forms through the catalytic gap; and a genome-wide screen over every position of GRCh38. A
near-match is a transcript window pairing a design at 14 or more of its 16 positions. A design is
liable where a wild-type parent pairs its whole catalytic gap over a contiguous run of ten base
pairs or more, ten being adopted rather than measured. Null ensembles were built as scrambles of
each design and as chimeras joining the same two parent transcripts at real exon termini, screened
identically.

## Tables

Tables 1 and 2 are in `fusion-junction-aso-journal-tables.md`, generated from the canonical sequence
file by `research/manuscripts/aso_journal_tables.py` so that a cell and its source cannot diverge.

## Figure legends

**Figure 1. One 16-mer spans three partners' breakpoints, and only one of the three is a junction
any patient is reported to carry.** The junction windows of *EWSR1* exon 12, *TAF15* exon 11 and
*FUS* exon 10 joined to *NR4A3* exon 3, aligned at the breakpoint, each row carrying its own
reporting status. The same paralogy that lets one reagent cover three fusions is why these designs
are hard to discriminate from the parent transcripts: this reagent's gap-level margin is three
junction-unique bases inside the six-nucleotide catalytic gap. Coverage is a statement about
sequence, predicted rather than measured, and not a claim that one reagent serves three patient
groups.

## Declarations

**Research use only, and not for administration to any person or animal.** Every oligonucleotide
sequence here is a research reagent for laboratory investigation only, and none has been synthesised
or tested. Order from the canonical record, `fusion-junction-aso-sequences.csv`, rather than by
copying from this article, and not until the breakpoint of the cell line or patient sample has been
established at nucleotide resolution by RNA sequencing. That file specifies the sequence, the
position of every locked residue and the backbone; it does not specify purification grade or
synthesis scale, which are the orderer's to choose.

**Ethics approval, consent to participate and consent for publication.** Not applicable. No human
subjects, human material or animals were involved.

**Data and code availability.** All code, graded artefacts and per-design tables are public and are
deposited under [doi:10.5281/zenodo.22028916](https://doi.org/10.5281/zenodo.22028916). The extended
report, carrying every screen's full parameters and the complete bounds on each claim, is
`fusion-junction-aso-research-article.md` inside that deposit; it is prepared for posting as a
bioRxiv preprint and is not yet posted, so the archived copy is the citable one. An earlier version
of these analyses placed the acceptor junction incorrectly through a coding-versus-transcript exon
indexing error and was withdrawn in full; the panels were rebuilt and verified against two
independent transcript acquisitions, and the complete correction record is released with the
archive.

**Use of artificial intelligence.** A large language model (Claude, Anthropic) was used throughout
this work: to write and review the analysis code, to run the screens, to retrieve and check
literature, and to draft and revise this manuscript. Eleven figures in this article are pinned to
the artefact that produces each and re-checked on every commit; the remaining counts are reproducible
from the released artefacts but are not individually guarded, and §5's decision thresholds and power
figures are stated conventions and arithmetic with no producing artefact. The author directed all
work reported here and is responsible for its content.

**Funding.** This work received no external funding and was self-funded by the author.

**Competing interests.** The author declares no financial competing interests: he holds no patent,
patent application, equity or consultancy relating to any sequence or method described here. One
non-financial interest belongs on the record: this work reaches a journal because its screens
returned a nameable reagent, and the same procedure applied to a panel that returned nothing would
be far less likely to have been written up at all, so the published record of this approach is
subject to a survivorship this paper cannot correct for.

## References
