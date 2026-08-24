---
id: DOC-FUSION-JUNCTION-ASO-JOURNAL
title: "NR4A3 fusion-junction antisense gapmers for extraskeletal myxoid chondrosarcoma: reagents, test articles and a pre-registrable knockdown experiment"
level: L3
kind: manuscript
status: live
canonical_for:
  - the journal-submission form of the fusion-junction ASO work
purpose: >
  The journal submission for PUB-ASO. It names the reagents to synthesise, the material to test them
  in and the experiment that would falsify the ranking. The full screen, its bounds and its methods
  are in fusion-junction-aso-research-article.md, archived and not posted as a preprint,
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

# *NR4A3* fusion-junction antisense gapmers for extraskeletal myxoid chondrosarcoma: reagents, test articles and a pre-registrable knockdown experiment

**Author.** Tristan D. McRae

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [0000-0002-1823-1451](https://orcid.org/0000-0002-1823-1451)

**Running title.** NR4A3 junction gapmers for EMC

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma usually defined by an
in-frame *NR4A3* fusion. That junction is in no normal transcript, so an antisense
gapmer could in principle cleave the fusion, sparing its parents; none is reported for any
*NR4A3* fusion. This work is computational, executing an industry off-target framework's in-silico
step; every sequence named is a research reagent not for administration. It sets out what a laboratory needs: two reagents at the most reported
breakpoints, 5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 and 5′-GGGCATATCTTGTGTG-3′ at
*TAF15* exon 6, both to *NR4A3* exon 3, longest wild-type parent gap duplexes eight and nine base
pairs; two screened controls; and a pre-registrable selectivity threshold. Both come from a panel of
190 junction-spanning 16-mers tiled at 5-6-5 across 38 in-frame junctions: 87 let a mature wild-type
parent pair their whole catalytic gap over ten or more contiguous base pairs, 61 against wild-type
*NR4A3* itself. Ten is a convention, not a measurement: exon-terminus chimeras meet the same screen
at 40.6% against the panel's 45.8%. Five test articles are named; the two fusion-positive EMC cell
models are reported at an *NR4A3* exon-2 acceptor, not this panel's. Also
released is the procedure that produced the 190 designs.

## Keywords

**Keywords.** antisense oligonucleotide; gapmer; RNase-H1; fusion transcript; NR4A3; extraskeletal
myxoid chondrosarcoma; off-target screening

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
Junction-directed nucleic-acid agents are a thirty-five-year lineage, reported against at least six
fusion oncogenes: two as antisense oligonucleotides, the rest as RNA-interference agents, one of those from
a lentiviral vector rather than an administered oligonucleotide.<sup>6,7,8,9,10,11</sup><!--PMID:1794439,9049825,33241214,21846246,23052253,37980543--> No
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
recommending any. That direction is the one an industry working group's 2025 off-target
recommendations report: off-target effects are seen more often where an oligonucleotide's mismatches
fall in its wings than where they fall in its central gap, on which reading a flanking mismatch is
suggested as the more important one to avoid.<sup>22</sup><!--PMID:39912803--> Those recommendations
set five steps: in-silico identification with transcriptomics, a focus on cell types showing
activity, in-vitro verification and margin assessment, risk assessment of what is confirmed, and
management of what remains. This work performs the in-silico half of the first step and stops there;
the margin measurement of the third is what §5 specifies, against the wild-type parent §3 identifies
as the liability.

## 2 · The reagents

The two reagents named for synthesis are the best available designs at the two junctions with a
published exon-resolved breakpoint and the highest reported prevalence:
5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 joined to *NR4A3* exon 3, and 5′-GGGCATATCTTGTGTG-3′ at
*TAF15* exon 6 joined to *NR4A3* exon 3 (Table 1). Exon numbers throughout are transcript exon indices counted
from the transcript 5′ end, including non-coding exons; an acceptor exon number read under the
coding-exon convention instead selects a different reagent. Both hold the panel's top gap-level margin of three: three
junction-unique bases inside the catalytic gap on the shorter side of the breakpoint, and
neither pairs a wild-type parent through the gap at §3's ten-base-pair criterion.

Both sit close to it. The *EWSR1* reagent's longest wild-type parent duplex through the whole gap is
eight base pairs and the *TAF15* reagent's is nine, both against wild-type *TFG*, so the cut decides
how they read: at eight both fall inside the class this work marks as not to be ordered, at nine the
*TAF15* reagent alone does, and only at ten does neither. Both also pair a wild-type parent through
part of the gap at the *NR4A3* exon-2/exon-3 seam their acceptor halves share, neither in full;
those partial duplexes are not counted here and have not been measured. Consecutive registers of one seam differ by a single-base
slide and can carry opposite verdicts, and the condemned class reaches these reagents:
5′-AGGGCATATCTTGTGT-3′ is one slide from the *TAF15* reagent and pairs 11 base pairs of wild-type
*NR4A3* through its whole catalytic gap. Neither may be substituted for the other.

Predicted transcriptome load separates the two: 123 gap-paired sense-strand near-matches for the
*EWSR1* reagent at a deeper search ceiling than the default, against eight for the *TAF15* one. Most
of the 123 are predicted transcript models rather than curated records, so the count is a search
result over a database that includes predictions, not a census of expressed transcripts. The *EWSR1* reagent also carries a sense-strand near-match in wild-type *TAF15*
precursor RNA at two mismatches, one inside the catalytic gap, spanning an intron-exon boundary: the
cost of the same ten shared donor bases that let one oligonucleotide span the *EWSR1*, *TAF15* and
*FUS* breakpoints at once (Figure 1). The *TAF15* reagent carries no sense-strand precursor site.
Both loads are predictions from sequence search rather than measured activity.

Both reagents are phosphorothioate throughout, with wings of five contiguous β-D-oxy-locked
residues — a high locked content against the two to four per wing taken here as usual, so these are
not conventional locked-nucleic-acid reagents and their matched-duplex melting temperatures are
correspondingly high. That cuts against the screens: a high-affinity chemistry is reported to
retain knockdown at more extensively mismatched sites than a conventional design
does,<sup>22</sup><!--PMID:39912803--> so the two-mismatch ceiling the near-match screens run at may
under-call for reagents of this locked content. Both begin 5′-GGG, a contiguous locked G-tract. High affinity is taken to
carry a risk of sequence-dependent hepatotoxicity; that is a premise adopted here rather than a
retrieved finding, and nothing here measures it.

Discounted by the breakpoint distribution of an 18-case series,<sup>12</sup><!--PMID:12378528--> the
two junctions account for 68.4% of molecularly confirmed cases in a 58-case
cohort.<sup>13</sup><!--PMID:36948401--> That prices which published junctions the two reagents
address; it is not a coverage measurement, no patient having been screened with
either sequence. The range 39.9% to 82.8% quoted with it is not a confidence interval and carries no
nominal level: two of its four inputs do not vary, and it assumes a breakpoint distribution reported
in one cohort transfers to a second collected twenty-one years later. The *TAF15* arm is priced at
three of three reported breakpoints, an upper bound rather than an estimate.

That figure is not a ceiling: a third design at *EWSR1* exon 13 joined to *NR4A3* exon 3, already
tiled and screened at the same top margin, would take the figure above to 79.0%. It is not named for synthesis, on grounds the
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
liability. Re-scored on duplex stability rather than on mismatch count, 8 designs carry a fully
paired sixteen-base-pair off-target duplex and 45 one inside 2 kcal/mol of their own; neither named
reagent is in either class, the closest to each being 3.2 and 3.0 kcal/mol weaker.

Lengthening the catalytic gap does not remove this liability, for an arithmetic reason: every base
inside the gap comes from the donor or the acceptor exon, so a longer gap buys margin only by
conceding parent-paired gap DNA at the design's own seam. Across three geometries the liable count
does not fall; the extended report gives the series.

Three designs clear every screen applied here, none at a junction any patient is reported to carry,
which makes them mechanism controls rather than candidates. Selecting within each junction rather
than across the panel is what makes the two named reagents available: 35 of the 38 junctions have a design that
clears the parent screen, and all five junctions with a published exon-resolved breakpoint have one.
Both readings are properties of the cut. At nine base pairs 31 of the 38 still clear and three of the
five published ones do; at eight, 23 and two; at seven, 9 and none; at six, 6 and none. These are
whole-duplex run lengths rather than the enzyme's own unit, and the availability the named reagents
rest on fails at nine, where the *TAF15* junction's best design is itself liable. As design counts
the loose cuts condemn almost everything: 175 of 190 at seven and 181 at six.

Two bounds on the cleanliness claim: seven of the 190 screens never
returned, and the alignment screen censors the rest, leaving 47 of 183 assessable at all, so a count
of clean designs is a floor over that subset and not a total over the panel; and most designs clean at the default search ceiling are not clean
at a deeper one.

The ten-base-pair criterion is adopted rather than measured, and the comparison against null models
does not resolve an excess specific to this disease. What the screen does establish is structural
rather than statistical, and it does not depend on the cut: each parent supplies about half of any
junction design, which is far outside the mismatch budget of a conventional off-target search, so
that search cannot return a parent as a near-match at any threshold it is normally run at. The
liability is therefore invisible to the instrument a designer would ordinarily use, which is the
case for screening it directly whatever cut is adopted. Mononucleotide scrambles — the weakest of the
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
sources with opposite limits. Every design in the panel joins its donor to *NR4A3* exon 3, its first
coding exon; the two cell models are reported at exon 2, and annotation does not reconcile the two.
On all four annotated *NR4A3* transcripts, the three with a RefSeq accession included, exon 3 is the
first coding exon and exon 2 is non-coding, so a reported exon-2 acceptor is not this panel's
acceptor renumbered.

Three are engineered constructs from a published functional study,<sup>14</sup><!--PMID:31020999-->
whose exon spans that paper states verbatim; two of them, E-N and T-N*, carry exactly the junctions
the reagents above span, so both named reagents have a stated test article. Rebuilding them is the faster route, but a complementary DNA
over-expressed in a heterologous background speaks to junction-selective knockdown of the intended
transcript, not to activity at an endogenous locus.

The other two are patient-derived, identity-clean models reported with two EMC
tumours,<sup>15</sup><!--PMID:36316541--> USZ20-EMC1 (RRID:CVCL_C6MX) and USZ22-EMC2
(RRID:CVCL_C6MY) — the only source of a fusion-positive EMC cell identified here. They are available
on request with no repository deposit, and are slow, at reported doubling times of five to six
days. Their fusions are reported as *EWSR1* exon 13 and *TAF15* exon 6
joined to *NR4A3* exon 2 rather than exon 3, and the report carries no sequenced exon-exon
boundary, no transcript accession and no junction sequence, so whether that names a non-coding
acceptor or an unsupported numbering is not decidable from what is published. This work's own
withdrawn version arose from an error of exactly this class.

One reading is nonetheless more parsimonious, and it favours the reagents named here. EMC's defining
lesion produces a chimeric transcription factor.<sup>1,14</sup><!--PMID:8634690,31020999--> A donor
joined to *NR4A3*'s non-coding exon 2 would sit upstream of that gene's own initiation codon and so
would not yield one; a donor joined to its first coding exon does, and that exon is transcript exon
3, the acceptor this panel is tiled at. On the coding-exon reading, therefore, the two cell models
carry the junctions the reagents above span. This is an inference and not a determination: a
5′-untranslated acceptor is reported in this disease at least once, in a *PGR*::*NR4A3*
case,<sup>16</sup><!--PMID:36103645--> and the requirement below is unchanged. The released builder will not emit an
exon-2 acceptor unaided: a non-coding acceptor needs its published-breakpoint list extended first. Reagents exist at both acceptors, neither of them a
molecule named above: 5′-AGTGGGCTCTCCACGG-3′ at *EWSR1* exon 13 to exon 2 and 5′-AGTGGGCTCTTGTGTG-3′ at *TAF15* exon 6
to exon 2, both at the panel's top margin. Neither reaches the ten-base-pair criterion, and their longest wild-type parent
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
tumour.<sup>17</sup><!--PMID:37370737--> The extended report specifies it for these reagents, with
three controls a knockdown assay alone cannot distinguish. Two are named as sequences (Table 2): a
dinucleotide-preserving scramble of each reagent, drawn and then put through the same mature-parent
screen the reagent passed. That screening is what makes a scramble a control — 10.0% of such
scrambles pair a parent's whole catalytic gap at the ten-base-pair criterion and 3.9% do so against
wild-type *NR4A3*, so an unscreened one carries a one-in-ten chance of being a second active
molecule offered as a negative control. Clearing the screen is not a claim of inertness; it is the
property a negative control has to have.

Selectivity is the wild-type *NR4A3* half-maximal knockdown concentration divided by the fusion's,
from a matched dose-response in the same wells, at a cut of 5.0 adopted as a convention — a
comparison of the two half-maximal concentrations is the margin assessment the recommendations
specify at this step, and they decline to set a default value for it.<sup>22</sup><!--PMID:39912803-->
At a
replicate standard deviation of 0.35 on the natural-log scale, six independent biological replicates
give about 80% power to falsify a true selectivity of 3 and three give about 30%. Above a realised
standard deviation of about 0.65 at three replicates — 1.53 at six, 2.25 at ten —
no observed ratio at or above one can put the upper limit of a two-sided 95% interval below 5,
so the test can fail
only on an anti-selective reading. Those figures are computed on that interval; a
normal-approximation interval would move them. Such a test is void, and voidness is a property of
the realised variance rather than of the design, so a pilot-based gate on the population variance
bounds it from one side only: where a one-sided 95% chi-square bound on the pilot's standard
deviation lies at or above the void figure for the count proposed, the decision is a larger
replicate count, or no falsification test at all, and never three. The threshold is defined on the
acceptor parent alone, so a reagent can clear it while pairing a donor transcript through its whole
gap.


## 6 · Discussion

Designability is not the constraint: junction-spanning designs exist at every in-frame *NR4A3*
fusion junction modelled here, and 35 of the 38 have one clearing the parent screen.

The constraint is discrimination between the fusion and its parents, and it is not resolved here. A junction design's most plausible wild-type liability is its own
parent, in the mature transcript or across a splice junction in precursor RNA. Both are searched
before any molecule exists, but not on comparable terms: the mature-transcript screen condemns on a
ten-base-pair duplex through the gap and the precursor arm on a hit at up to two mismatches with the
gap fully paired, so neither restates the other, and their counts may not be added because a design
condemned in both is one design. A third compartment is searched only in the extended report: the
patient's own un-rearranged *NR4A3* allele, at a two-mismatch ceiling that bounds its class from
below. No design this panel selects is condemned by it, but it excludes two registers
of §4's *EWSR1* exon 13 to *NR4A3* exon-2 seam while clearing that reagent — the register hazard of
§2 arriving from a compartment the panel's selection never has to consider.

The four junction-specificity reports cited
here<sup>8,9,10,18</sup><!--PMID:33241214,21846246,23052253,36265509--> were all made on molecules
already synthesised; no survey of design pipelines was performed, so the screen-before-synthesis
claim is about this literature as retrieved and not a priority claim. Whether sparing wild-type *NR4A3* is worth a specificity cost is
itself unsettled, the reported paralogue redundancy and dosage effects pointing in opposite
directions; the extended report gives that literature and does not resolve it either.

Three limits bound what any test of these reagents could show. All five screens address
hybridisation rather than cleavage, and none establishes that a predicted duplex forms or is cut.
The method-level novelty is nil, junction-directed oligonucleotides being long established; what is
new is the indication and the screen applied before synthesis. And systemic delivery to a solid
tumour remains unsolved, the gate this modality faces after any result reported here. Every source of a test article named here ends at someone culturing cells.

## 7 · Methods

All analyses are computational and use public data; no laboratory work was performed. Full
parameters, the complete bounds on each claim and the per-design tables are in the extended report
named under Data availability.

Canonical transcripts for the five partner genes and for *NR4A3* were obtained from
Ensembl.<sup>19</sup><!--PMID:39656687--> Junction-spanning 16-mer gapmers were tiled in a 5-6-5
β-D-oxy-locked-nucleic-acid/DNA/β-D-oxy-locked-nucleic-acid
geometry,<sup>20</sup><!--PMID:24981949--> one design per register at which the breakpoint falls
inside the six-nucleotide DNA gap, which admits five per junction. That gap is the shortest length the cited source credits
rather than its preferred one, and six is used because the genome-wide arm is not available above a
16-mer. A design's gap-level margin is the count of junction-unique bases inside the gap on
the shorter side of the breakpoint.

Five specificity screens were applied: an alignment screen against human RefSeq RNA, classifying
each near-match by whether the catalytic gap is paired; an exhaustive transcript scan complete for
substitutions within a one-mismatch budget; a screen of the parents' unspliced sequence; a
mature-parent screen recording the longest contiguous duplex any of six wild-type parent transcripts
forms through the catalytic gap; and a genome-wide screen over every position of GRCh38, mitochondrial sequence
included. Between them they cover mature transcript, unspliced precursor, exon-exon junction,
non-coding and mitochondrial sequence, which is the search scope the 2025 recommendations
ask for.<sup>22</sup><!--PMID:39912803--> A
near-match is a transcript window pairing a design at 14 or more of its 16 positions. Each alignment
was then re-scored on the nearest-neighbour stability of its longest contiguous paired run, the
energy-based second stage those recommendations prescribe; only separations are reported. A design is
liable where a wild-type parent pairs its whole catalytic gap over a contiguous run of ten base
pairs or more, ten being adopted rather than measured. Null ensembles were built as scrambles of
each design and as chimeras joining the same two parent transcripts at real exon termini, screened
identically. Melting temperatures are nearest-neighbour values for an unmodified DNA:RNA hybrid at
250 nM strand.<sup>21</sup><!--PMID:7545436--> Those parameters do not describe a locked,
phosphorothioate oligonucleotide, so no absolute melting point is reported for these reagents; only
the fusion-versus-parent separation is, and as a floor, because the fusion duplex pairs all ten
locked residues where each parent half-duplex pairs five, by construction for every design here.

## Tables

Tables 1 and 2 are in `fusion-junction-aso-journal-tables.md`, generated from the canonical sequence
file so that a cell and its source cannot diverge.

## Figure legends

**Figure 1. One 16-mer spans three partners' breakpoints, and only one of the three is a junction
any patient is reported to carry.** The junction windows of *EWSR1* exon 12, *TAF15* exon 11 and
*FUS* exon 10 joined to *NR4A3* exon 3, aligned at the breakpoint, each row carrying its own
reporting status.

## Author Contributions

T.D.M. is the sole author, and is responsible for the conception and design of the study, the
analysis code, the screens and their interpretation, and the drafting and revision of this
manuscript.

## Statements and Declarations

**Research use only, and not for administration to any person or animal.** Every sequence here is a
research reagent for laboratory investigation only, and none has been synthesised or tested. Order from the canonical record, `fusion-junction-aso-sequences.csv`, which specifies the sequence,
every locked residue and the backbone, and not until the breakpoint has been established at
nucleotide resolution by RNA sequencing.

**Ethical considerations.** Not applicable. No human
subjects, human material or animals were involved, and no ethics approval was required.

**Consent to participate.** Not applicable. No participants were enrolled.

**Consent for publication.** Not applicable. The manuscript contains no data from any individual
person.

**Declaration of conflicting interest.** The author declares no financial competing interests: he holds no patent,
patent application, equity or consultancy relating to any sequence or method described here.

**Funding statement.** No external funding; self-funded by the author.

**Use of artificial intelligence.** A large language model (Claude, Anthropic) was used throughout
this work: to write and review the analysis code, to run the screens, to retrieve and check
literature, and to draft and revise this manuscript. Every reference's bibliographic record was
retrieved from PubMed rather than written from model output, and each citation was checked against
the retrieved record. The author directed all work reported here and is responsible for its content.

**Data availability.** All code, graded artefacts and per-design tables are deposited under
[doi:10.5281/zenodo.22061075](https://doi.org/10.5281/zenodo.22061075). The extended report,
carrying every screen's parameters and the complete bounds on each claim, is
`fusion-junction-aso-research-article.md` inside that deposit; it is not posted as a preprint, so
the archived copy is the citable one. An earlier version
of these analyses placed the acceptor junction incorrectly through a coding-versus-transcript exon
indexing error and was withdrawn in full; the panels were rebuilt and verified, and the complete
correction record is released with the archive.

## References
