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
named at the two most frequently reported breakpoints: 5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 and
5′-GGGCATATCTTGTGTG-3′ at *TAF15* exon 6, both at the panel's top gap-level margin of three, with
longest wild-type parent duplexes through the whole gap of eight and nine base pairs. Five test
articles are named, and the design pipeline is released.

---

## 1 · Background

EMC is defined in the large majority of cases by an in-frame fusion of *EWSR1* to
*NR4A3*,<sup>1</sup><!--PMID:8634690--> with *TAF15* a substantial minority and *TCF12* and *TFG*
rare.<sup>2</sup><!--PMID:32572850--> The disease responds poorly to conventional cytotoxic
chemotherapy,<sup>3</sup><!--PMID:41055792--> though responses do
occur,<sup>4</sup><!--PMID:24345066--> and a tyrosine-kinase inhibitor trialled in it gave disease
control more often than response — a reading composed from the review's response
categories<sup>3</sup><!--PMID:41055792--> rather than from a figure stated in the trial
report.<sup>5</sup><!--PMID:31331701-->

The fusion junction is the one feature of an EMC tumour that exists at the RNA level and in no
normal cell. An antisense gapmer tiled across it recruits RNase-H1 to cleave the transcript it
pairs, at the six-nucleotide DNA gap at the centre of a 5-6-5 architecture.
Junction-directed nucleic-acid agents are a thirty-five-year lineage, reported against six fusion
oncogenes, two of them as antisense oligonucleotides and the rest as RNA-interference
agents.<sup>6,7,8,9,10,11</sup><!--PMID:1794439,9049825,33241214,21846246,23052253,37980543--> No
such design is reported for any *NR4A3* fusion in the literature retrieved here, and that absence is
why this work exists.

What a junction design must survive follows from its construction. Both halves are parent-gene
sequence, so each parent matches roughly half the oligonucleotide — far outside the mismatch budget
of a conventional off-target search, which therefore never returns a parent as a near-match. RNase-H1 does not require the whole duplex, only that the gap be paired — a premise
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
*TAF15* exon 6 joined to *NR4A3* exon 3 (Table 1). Exon numbers throughout are transcript exon indices counted
from the transcript 5′ end, including non-coding exons; an acceptor exon number read under the
coding-exon convention instead selects a different reagent. Both hold the panel's top gap-level margin of three: three
junction-unique bases inside the catalytic gap on the shorter side of the breakpoint, and
neither pairs a wild-type parent through the gap at the ten-base-pair criterion §3 adopts.

Both sit close to it. The *EWSR1* reagent's longest wild-type parent duplex through the whole gap is
eight base pairs and the *TAF15* reagent's is nine, both against wild-type *TFG*, so the cut decides
how they read: at eight both fall inside the class this work marks as not to be ordered, at nine the
*TAF15* reagent alone does, and only at ten does neither. Both also pair a wild-type parent through
part of the gap at the *NR4A3* exon-2/exon-3 seam their acceptor halves share, neither in full;
those partial duplexes are not counted here and have not been measured. Consecutive registers of one
seam differ by a single-base slide and can carry opposite verdicts (Table 2), so neither member of
such a pair may be substituted for the other.

Predicted transcriptome load separates the two: 123 gap-paired sense-strand near-matches for the
*EWSR1* reagent at a deeper search ceiling than the default, against eight for the *TAF15* one. Most
of the 123 are predicted transcript models rather than curated records, so the count is a search
result over a database that includes predictions, not a census of expressed transcripts. The *EWSR1* reagent also carries a sense-strand near-match in wild-type *TAF15*
precursor RNA at two mismatches, one inside the catalytic gap, spanning an intron-exon boundary: the
cost of the same ten shared donor bases that let one oligonucleotide span the *EWSR1*, *TAF15* and
*FUS* breakpoints at once (Figure 1). The *TAF15* reagent carries no sense-strand precursor site.
Both loads are predictions from sequence search rather than measured off-target activity.

Discounted by the breakpoint distribution of an 18-case series,<sup>12</sup><!--PMID:12378528--> the
two junctions account for 68.4% of molecularly confirmed cases in a 58-case
cohort,<sup>13</sup><!--PMID:36948401--> roughly two thirds. That prices which published junctions
the two reagents address; it is not a coverage measurement, no patient having been screened with
either sequence. The range 39.9% to 82.8% quoted with it is not a confidence interval and carries no
nominal level: two of its four inputs do not vary, and it assumes a breakpoint distribution reported
in one cohort transfers to a second collected twenty-one years later. The *TAF15* arm is priced at
three of three reported breakpoints, an upper bound rather than an estimate.

That figure is not a ceiling: a third design at *EWSR1* exon 13, already tiled and screened at the
same top margin, would take the figure above to 79.0%. It is not named for synthesis, on grounds the
extended report sets out.

## 3 · Selection from a panel of 190 designs

The two reagents above are what survived a screen applied uniformly to the whole panel. Across the
38 in-frame junctions of five modelled partners, 190 junction-spanning designs were tiled and put
through five specificity screens. Of those, 87 let one of six mature wild-type parent transcripts pair
their entire catalytic gap over a contiguous duplex of at least ten base pairs, and 61 of the 87 do
so against wild-type *NR4A3*; 85 are paired by one of the design's own two parent genes. A second class is invisible to any screen over mature transcripts: 19
designs carry a sense-strand near-match in parent precursor RNA pairing the gap in full. As a union
rather than a sum the two screens condemn 93 of the 190. A design whose gap carries a mismatch is
scored zero rather than short, so the 87 bound the fully-paired class, not the whole parent
liability.

Lengthening the catalytic gap does not remove this liability, for a reason that is arithmetic rather
than empirical: every base inside the gap comes from the donor or the acceptor exon, so a longer gap
buys margin only by conceding parent-paired gap DNA at the design's own seam. Screened across three
geometries the liable count does not fall, and at 5-10-5 the criterion is not independent of the
geometry at all; the extended report gives the series.

Three designs clear every screen applied here, none at a junction any patient is reported to carry,
which makes them mechanism controls rather than candidates. Selecting within each junction rather
than across the panel is what makes the two named reagents available: 35 of the 38 junctions have a design that
clears the parent screen, and all five junctions with a published exon-resolved breakpoint have one.
Both readings are properties of the cut. At nine base pairs 31 of the 38 still clear and three of the
five published ones do; at eight, 23 and two; at seven, 9 and none; at six, 6 and none. Those cuts
are whole-duplex run lengths, not the enzyme's own unit, so no cut on this ladder is the enzymology
restated, and the availability the two named reagents rest on fails at a run cut of nine, where the
*TAF15* junction's best design is itself liable. Read as design counts the loose cuts condemn almost
everything: 175 of 190 at seven and 181 at six.

Two bounds on the cleanliness claim are load-bearing. The alignment screen censors, leaving 47 of
the 183 filtered designs assessable at all, so a count of clean designs is a floor over that subset
and not a total over the panel; and most designs clean at the default search ceiling are not clean
at a deeper one.

The ten-base-pair criterion is adopted rather than measured, and the comparison against null models
does not resolve an excess specific to this disease. Mononucleotide scrambles — the weakest of the
ten nulls screened, and not the dinucleotide-preserving control §5 prescribes — meet the parent
screen at 6.2% against 45.8% for the panel, but chimeras built at real exon termini of the same two
transcripts, at junctions almost never reported in a patient, meet it at 40.6%. The adopted cut does not escape that comparison: at ten the
strongest null's 40.6% falls inside the panel's own 95% interval on 45.8%, as at every cut from
seven to thirteen but eleven, and the strongest null reaches 91.4% at seven against the panel's
92.1%. The comparison is narrower than it reads, the panel arm being itself mostly unreported
junctions — the property the chimeric null is discounted for. Most of the liability is therefore
what joining two exon termini of these genes gives, and across cuts of six to thirteen base pairs
the excess over the strongest null changes sign four times.

## 4 · Test articles

Five test articles bear on the junctions this panel designs against, and they divide into two
sources with opposite limits. Every design in the panel joins its donor to *NR4A3* exon 3; the two
cell models are reported at exon 2, so they carry a panel junction only under the exon-3 reading
their acceptor index leaves open.

Three are engineered constructs from a published functional study,<sup>14</sup><!--PMID:31020999-->
whose exon spans that paper states verbatim; two of them, E-N and T-N*, carry exactly the junctions
the reagents above span, so both named reagents have a stated test article. Rebuilding them is the
faster route, but a complementary DNA over-expressed in a heterologous background speaks to
junction-selective knockdown of the intended transcript, not to activity at endogenous expression
from an endogenous locus.

The other two are patient-derived, identity-clean models reported with two EMC
tumours,<sup>15</sup><!--PMID:36316541--> USZ20-EMC1 (RRID:CVCL_C6MX) and USZ22-EMC2
(RRID:CVCL_C6MY) — the only source of a fusion-positive EMC cell identified here. They are available
on request with no repository deposit, and are slow, at reported doubling times of five to six
days. Their fusions are reported as *EWSR1* exon 13 and *TAF15* exon 6
joined to *NR4A3* exon 2 rather than exon 3, but that acceptor index is not settled: the report
carries no sequenced exon-exon boundary, no transcript accession and no junction sequence, and this
work's own withdrawn version arose from an error of exactly this class. Reagents exist at both
acceptors, and in neither case is it the same molecule as the reagent named above:
5′-AGTGGGCTCTCCACGG-3′ at *EWSR1* exon 13 and 5′-AGTGGGCTCTTGTGTG-3′ at *TAF15* exon 6, both at the
panel's top margin. Neither reaches the ten-base-pair criterion, and their longest wild-type parent
duplexes through the whole gap are eight base pairs against wild-type *EWSR1* and nine against
wild-type *NR4A3* — the second against the acceptor parent on which §5's selectivity ratio is
defined, a closer call than either exon-3 reagent presents. A reagent selected for one acceptor is
not valid for the other.

One requirement is upstream of all of them: the breakpoint of the test article must be established
at nucleotide resolution by RNA sequencing before any oligonucleotide is ordered, every design here
being specific to the exon pair it was tiled at. Routine diagnosis does not supply the seam, since
break-apart *NR4A3* fluorescence in situ hybridisation detects a rearrangement irrespective of
partner.<sup>3</sup><!--PMID:41055792-->

## 5 · The falsification experiment

An isogenic fusion-positive against fusion-negative comparison has been run in an analogous fusion
sarcoma, against *NAB2::STAT6* in solitary fibrous
tumour.<sup>16</sup><!--PMID:37370737--> The extended report specifies it for these reagents, with
three controls a knockdown assay alone cannot distinguish. One belongs here because it constrains
what may be ordered: the dinucleotide-preserving scramble must itself pass the mature-parent screen
before synthesis, because 10.0% of dinucleotide-preserving scrambles pair a parent's whole catalytic
gap at the ten-base-pair criterion and 3.9% do so against wild-type *NR4A3*.

Selectivity is the wild-type *NR4A3* half-maximal knockdown concentration divided by the fusion's,
from a matched dose-response in the same wells, at a cut of 5.0 adopted as a convention. At a
replicate standard deviation of 0.35 on the natural-log scale, six independent biological replicates
give about 80% power to falsify a true selectivity of 3 and three give about 30%. Above a realised
standard deviation of about 0.65 at three replicates, no observed ratio at or above one can put the
upper limit of a two-sided 95% interval below 5, so the test can fail only on an anti-selective
reading. Such a test is void, and voidness is a property of the realised variance rather than of the
design, so a pilot-based gate on the population variance bounds it from one side only: where a
pilot's bound lies at or above the void figure for the count proposed, the decision is a larger
replicate count, or no falsification test at all, and never three. The threshold is defined on the
acceptor parent alone, so a reagent can clear it while pairing a donor transcript through its whole
gap.

## 6 · Beyond the panel

The panel is bounded by what has been sequenced rather than by what can be designed, and the
procedure that produced the 190 designs is released unchanged with the artefacts. It is not a turnkey service for an arbitrary breakpoint: the
builder's published-breakpoint list is a waiver list rather than a gate, admitting seams that would
otherwise be refused for a non-coding acceptor or an out-of-frame join. A seam needing such a waiver
requires the list to be extended first; a seam needing none is emitted without any check that a
patient has been reported to carry it.

A design is certifiable where all five screens could be run on it and it cleared all five; one that
a screen cannot address is uncertifiable whatever the others return. The reagent for the third
engineered construct of §4 is uncertifiable on that definition, its seam lying outside the
compartment three of the five screens reach. The two that reach it — the precursor-RNA and genome
arms — agree design by design, clearing the seam's top-margin design and condemning a lower-margin
one at a wild-type *NR4A3* site each records as pairing the whole catalytic gap; two screens
agreeing is not the clearance the other three would supply. What the procedure yields is a
candidate, not a validated reagent.

## 7 · Discussion

Designability is not the constraint. Junction-spanning designs exist at every in-frame *NR4A3*
fusion junction modelled here, and 35 of the 38 have one clearing the parent screen at the adopted
criterion — a property of the cut, as §3 sets out.

The constraint is discrimination between the fusion and its parents, and it is not resolved here. A junction design's most plausible wild-type liability is its own
parent, in the mature transcript or across a splice junction in precursor RNA. Both are searched
before any molecule exists, but not on comparable terms: the mature-transcript screen condemns on a
ten-base-pair duplex through the gap and the precursor arm on a hit at up to two mismatches with the
gap fully paired, so neither restates the other, and their counts may not be added because a design
condemned in both is one design. A third compartment is searched only in the extended report: the
patient's own un-rearranged *NR4A3* allele, at a two-mismatch ceiling that bounds its class from
below. No design this panel selects is condemned by it, but it excludes the two registers
neighbouring the *EWSR1* exon 13 reagent while clearing the reagent itself — the register hazard of
§2 arriving from a compartment the panel's selection never has to consider.

The four reports of parental sparing cited
here<sup>8,17,9,10</sup><!--PMID:33241214,36265509,21846246,23052253--> were all made on molecules
already synthesised; no survey of design pipelines was performed, so the screen-before-synthesis
claim is about this literature as retrieved and not a priority claim. Whether sparing wild-type *NR4A3* is worth a specificity cost is
itself unsettled. The family is functionally redundant where
tested,<sup>18,19</sup><!--PMID:29343483,25446259--> which cuts against the premise; against that,
reduced *NR4A1*/*NR4A3* dosage is consequential in
mice,<sup>20</sup><!--PMID:21205929--> and the family is not uniform in direction, *NR4A3*
aggravating murine atherosclerotic lesions where its paralogues attenuate
them.<sup>21</sup><!--PMID:24005216--> The evidence is not decisive either way.

Three limits bound what any test of these reagents could show. All five screens address
hybridisation rather than cleavage, and none establishes that a predicted duplex forms or is cut.
The method-level novelty is nil, junction-directed oligonucleotides being long established; what is
new is the indication and the screen applied before synthesis. And systemic delivery to a solid
tumour remains unsolved, the gate this modality faces after any result reported here. Above all of
them, every source of a test article named here ends at someone culturing cells.

## 8 · Methods

All analyses are computational and use public data; no laboratory work was performed. Full
parameters, the complete bounds on each claim and the per-design tables are in the extended report
named under Data availability.

Canonical transcripts for the five partner genes and for *NR4A3* were obtained from
Ensembl.<sup>22</sup><!--PMID:39656687--> Junction-spanning 16-mer gapmers were tiled in a 5-6-5
β-D-oxy-locked-nucleic-acid/DNA/β-D-oxy-locked-nucleic-acid
geometry,<sup>23</sup><!--PMID:24981949--> one design per register at which the breakpoint falls
inside the six-nucleotide DNA gap, which admits five per junction. That gap is the shortest length the cited source calls sufficient
rather than its preferred one — it reports six nucleotides as necessary for noteworthy RNase-H
activity and seven to ten as optimal — and six is used because the genome-wide arm is not available
above a 16-mer. A design's gap-level margin is the count of junction-unique bases inside the gap on
the shorter side of the breakpoint.

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
reporting status. Coverage here is a statement about sequence, predicted rather than measured, and
not a claim that one reagent serves three patient groups.

## Declarations

**Research use only, and not for administration to any person or animal.** Every sequence here is a
research reagent for laboratory investigation only, and none has been synthesised or tested. Order from the canonical record, `fusion-junction-aso-sequences.csv`, which specifies the sequence,
every locked residue and the backbone, rather than by copying from this article — and not until the
breakpoint has been established at nucleotide resolution by RNA sequencing.

**Ethics approval, consent to participate and consent for publication.** Not applicable. No human
subjects, human material or animals were involved.

**Data and code availability.** All code, graded artefacts and per-design tables are deposited under
[doi:10.5281/zenodo.22028916](https://doi.org/10.5281/zenodo.22028916). The extended report,
carrying every screen's parameters and the complete bounds on each claim, is
`fusion-junction-aso-research-article.md` inside that deposit; it is prepared for bioRxiv and not yet
posted, so the archived copy is the citable one. An earlier version
of these analyses placed the acceptor junction incorrectly through a coding-versus-transcript exon
indexing error and was withdrawn in full; the panels were rebuilt and verified, and the complete
correction record is released with the archive.

**Use of artificial intelligence.** A large language model (Claude, Anthropic) was used throughout
this work: to write and review the analysis code, to run the screens, to retrieve and check
literature, and to draft and revise this manuscript. Figures here are pinned to the artefact that
produces each and re-checked on every commit; the remaining counts are reproducible from the
released artefacts but not individually guarded, and §5's thresholds are stated conventions with no
producing artefact. The author directed all work reported here and is responsible for its
content.

**Funding.** No external funding; self-funded by the author.

**Competing interests.** The author declares no financial competing interests: he holds no patent,
patent application, equity or consultancy relating to any sequence or method described here. One
non-financial interest belongs on the record: this work reaches a journal because its screens
returned a nameable reagent, so the published record of this approach carries a survivorship this
paper cannot correct for.

## References
