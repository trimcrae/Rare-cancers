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
  are in fusion-junction-aso-research-article.md, the bioRxiv preprint, which this manuscript cites
  as its extended report; the numbers themselves live in the artifacts under research/modalities/
  and are not duplicated here.
scope: >
  Computational design and specificity screening only. No wet-lab experiment was performed, and
  nothing here asserts efficacy, potency, safety, a therapeutic window, delivery to a tumour, or
  clinical readiness for any sequence. Every sequence named is a research reagent for laboratory
  investigation only and must not be administered to any person or animal. This block is stripped
  from the PDF builds and reaches no reader of the submitted article, so it is a routing copy: the
  operative statements live in the Abstract, in the reagents section and in Declarations.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-20
last_verified: 2026-08-20
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
ten or more contiguous base pairs, 61 of those against wild-type *NR4A3* itself. Two reagents are
named at the two most frequently reported breakpoints: 5′-GGGCATATCATCAAAC-3′ at
*EWSR1* exon 12 and 5′-GGGCATATCTTGTGTG-3′ at *TAF15* exon 6, both at the panel's top gap-level
margin of three, with longest wild-type parent runs of eight and nine base pairs. Five test
articles are named: two engineered constructs at these junctions, and two fusion-positive EMC cell
models whose *NR4A3* exon-2 acceptors are matched to different designs. The design pipeline is
released for breakpoints outside the panel.

---

## 1 · Background

EMC is defined in the large majority of cases by an in-frame fusion of *EWSR1* to
*NR4A3*,<sup>1</sup><!--PMID:8634690--> with *TAF15* a substantial minority and *TCF12* and *TFG*
rare.<sup>2</sup><!--PMID:32572850--> The disease responds poorly to conventional cytotoxic
chemotherapy,<sup>3</sup><!--PMID:41055792--> though responses do occur: the one molecularly
confirmed series to record any recorded four partial responses in ten evaluable
patients.<sup>4</sup><!--PMID:24345066--> The tyrosine-kinase inhibitors trialled in it give disease
control more often than response.<sup>5</sup><!--PMID:31331701-->

The fusion junction is the one feature of an EMC tumour that exists at the RNA level and in no normal
cell. An antisense gapmer tiled across it recruits RNase-H1 to cleave the transcript it pairs, and
the six-nucleotide DNA gap at the centre of a 5-6-5 architecture is where that cleavage occurs.
Junction-directed oligonucleotides are a thirty-five-year lineage, reported against six fusion
oncogenes.<sup>6,7,8,9,10,11</sup><!--PMID:1794439,9049825,33241214,21846246,23052253,37980543-->
No such design is reported for any *NR4A3* fusion in the literature retrieved here, and that absence
is why this work exists: EMC is rare enough that the design step has not been done, and rare enough
that no group is likely to do it as a by-product of something else.

What a junction design must survive follows from its construction. Both halves are parent-gene
sequence, so each parent matches roughly half the oligonucleotide, and half-identity falls far
outside the mismatch budget of a conventional off-target search: a parent is not returned as a
near-match. RNase-H1 does not require the whole duplex, only that the gap be paired. Whether a
wild-type parent pairs the catalytic gap contiguously is therefore a separate question from overall
similarity, and it is the one this work puts to all 190 designs before recommending any.

## 2 · The reagents

The two reagents named for synthesis are the best available designs at the two junctions with a
published exon-resolved breakpoint and the highest reported prevalence:
5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 joined to *NR4A3* exon 3, and 5′-GGGCATATCTTGTGTG-3′ at
*TAF15* exon 6 joined to *NR4A3* exon 3 (Table 1). Exon numbers throughout are transcript exon indices,
counted from the transcript 5′ end and including non-coding exons; that convention differs from
coding-exon indexing for *TCF12*, *TFG* and *NR4A3*, and an acceptor exon number read under the
wrong convention selects a different reagent. Both hold the panel's top gap-level margin of three, meaning
three junction-unique bases inside the catalytic gap on the shorter side of the breakpoint. Neither
pairs a wild-type parent through the gap at the ten-base-pair criterion adopted here. That criterion
counts only windows pairing the catalytic gap in full, and a single mismatch inside the gap reduces
rather than abolishes cleavage, so the 87 are a subclass rather than the whole parent liability: at
a cut of seven base pairs the count is 175 of 190 and at six it is 181. Both reagents pair a
wild-type parent through part of the gap at the *NR4A3* exon-2/exon-3 seam their acceptor halves
share, neither in full; those partial duplexes are not counted here and have not been measured
reagent by reagent.

Both sit close to that criterion. The *EWSR1* reagent's longest wild-type parent run is eight base pairs and the
*TAF15* reagent's is nine, both against wild-type *TFG*. Where the criterion is set therefore decides
how the two read: at a cut of eight both fall inside the class this work marks as not to be ordered,
at nine the *TAF15* reagent alone does, and only at ten does neither. Ten is adopted as a
convention and is not measured for this architecture; the extended report gives the panel's count at
every cut.

One hazard of this design space belongs beside the sequences. Consecutive registers of one seam differ by a single-base slide and can carry opposite verdicts, so a design that
pairs a wild-type parent through its whole catalytic gap sits one nucleotide from one that does not
(Table 2). Neither member of such a pair may be substituted for the other.

Predicted transcriptome load separates the two, and Table 1 carries it beside the sequences: 123
gap-paired sense-strand near-matches for the *EWSR1* reagent at ten times the default search depth
against eight for the *TAF15* one. The *EWSR1* reagent also carries a sense-strand near-match in wild-type *TAF15* precursor RNA at two
mismatches, one of them inside the catalytic gap, spanning an intron-exon boundary. That site is the
cost of the same ten shared donor bases that let one oligonucleotide span the *EWSR1*, *TAF15* and
*FUS* breakpoints at once (Figure 1). The *TAF15* reagent carries no sense-strand precursor site at all. Neither
load is a disqualification, and neither is a statement about safety: these are predictions from
sequence search, not measured off-target activity.

Discounted by the breakpoint distribution of an 18-case series,<sup>12</sup><!--PMID:12378528--> the
two junctions account for 68.4% of molecularly confirmed cases in a 58-case
cohort,<sup>13</sup><!--PMID:36948401--> roughly two thirds. That figure prices which published
junctions the two reagents address. It is not a coverage measurement, no patient having been screened
with either sequence, and its interval is wide for the denominators rather than for the estimate,
spanning 39.9% to 82.8% when each breakpoint fraction is taken to its own Wilson bound.

## 3 · Selection from a panel of 190 designs

The two reagents above are what survived a screen applied uniformly to the whole panel. Across the 38
in-frame junctions of five modelled partners, 190 junction-spanning designs were tiled and put
through five specificity screens. Of those, 87 let one of six mature wild-type parent transcripts
pair their entire catalytic gap over a contiguous duplex of at least ten base pairs, and 61 of the 87
do so against wild-type *NR4A3*. That is the single largest liability class in the panel, and 85 of
the 87 are paired by one of the design's own two parent genes rather than by an unrelated transcript.
A second class is invisible to any screen over mature transcripts: 19 designs carry a sense-strand
near-match in parent precursor RNA that pairs the gap in full and touches intronic sequence. Taken as
a union rather than a sum, the two screens condemn 93 of the 190.

Lengthening the catalytic gap does not remove this liability, and the reason is arithmetic rather
than empirical. Every base inside the gap comes from the donor exon or from the acceptor exon, so
the junction-unique bases on the shorter side and the bases a wild-type parent can pair on the
longer side tile the gap and sum to it. A longer gap therefore raises the margin available only by
conceding parent-paired gap DNA at the design's own seam, and that concession is not flat: designs
whose seam duplex reaches ten base pairs run from 76 of 190 to 228 of 266 to 342 of 342. The
searched liability behaves differently. Across the three geometries screened — 5-6-5, 5-8-5 and
5-10-5 over the same 38 junctions — the count of designs pairing a parent at the ten-base-pair
criterion is 87 of 190, 88 of 266 and 87 of 342, so the count does not fall while the share does,
from 45.8% to 33.1% to 25.4%, because a longer oligonucleotide admits more junction-spanning
registers per seam. At 5-10-5 the criterion is no longer independent of the geometry: a
ten-nucleotide gap is itself a ten-base-pair hybrid, so every window pairing the whole gap clears
the criterion by construction, and the three counts are not a reading at a constant substrate.

Three designs clear every screen applied here. None of the three sits at a junction any patient is
reported to carry, which is what makes them mechanism controls rather than candidates.
Selecting within each junction rather than across the panel is what makes the two named reagents
available: 35 of the 38 junctions have a design that clears the parent screen, and all five junctions
with a published exon-resolved breakpoint have one.

Two bounds on the cleanliness claim are load-bearing and are stated with it. The alignment screen is
heuristic and stores at most 50 hits per query, so only 47 of the 183 filtered designs have hit lists
short enough to assess for cleanliness at all; a count of clean designs is therefore a floor over
that subset rather than a total over the panel. And search depth moves the result: most of the
designs clean at the default ceiling are not clean at ten times it, as the extended report shows
design by design.

The ten-base-pair criterion is adopted rather than measured, and the comparison against null models
does not resolve an excess specific to this disease. Scrambled sequences meet the parent screen at
6.2% against 45.8% for designs at real breakpoints, but chimeras built at real exon termini of the
same two transcripts, at junctions almost never reported in a patient, meet it at 40.6%. Most of the
liability is therefore what joining two exon termini of these genes gives, and across cuts of six to
thirteen base pairs the excess of the observed rate over the strongest null changes sign four times.
No cut in that range is a boundary the data picks out.

## 4 · Test articles

Five test articles carry a junction this panel designs against, and they divide into two sources with
opposite limits.

Three are engineered constructs from a published functional study,<sup>14</sup><!--PMID:31020999-->
whose exon spans that paper states verbatim. Two of them, E-N and T-N*, carry exactly the two
junctions the reagents above span, so both named reagents have a stated test article. Rebuilding the
constructs is the faster route and its critical path contains no laboratory that has to answer an
email. What it cannot buy is biological relevance: a complementary DNA over-expressed in a
heterologous background is not the disease, so such an experiment speaks to junction-selective
knockdown of the intended transcript and not to activity at endogenous expression from an endogenous
locus.

The other two are patient-derived, identity-clean models reported with two EMC
tumours,<sup>15</sup><!--PMID:36316541--> USZ20-EMC1 (RRID:CVCL_C6MX) and USZ22-EMC2
(RRID:CVCL_C6MY). These are the only source of a fusion-positive EMC cell identified here. They are
available on request from the originating laboratory with no repository deposit, and they are slow,
at reported doubling times of five to six days as sarco-spheres passaged every two to three weeks,
which constrains any exposure window. Their fusions are reported as *EWSR1* exon 13 and *TAF15* exon
6 joined to *NR4A3* exon 2 rather than exon 3. Reagents exist at both acceptors, so each line has
one, and it is not in either case the same molecule as the reagent named above for the exon-3
acceptor. A reagent selected for one acceptor is not valid for the other.

One requirement is upstream of all of them. The breakpoint of the cell line or tumour sample used as
the test article must be established at nucleotide resolution by RNA sequencing before any
oligonucleotide is ordered. Every design here is specific to the exon pair it was tiled at, and none
is valid for an unverified junction. Routine diagnosis does not supply the seam: break-apart *NR4A3*
fluorescence in situ hybridisation detects a rearrangement irrespective of
partner,<sup>3</sup><!--PMID:41055792--> so on its own it locates neither the partner nor the exon
pair.

## 5 · The falsification experiment

The experimental design that would resolve the central uncertainty, an isogenic
fusion-positive against fusion-negative comparison, has been published in an analogous fusion
sarcoma. Fusion-specific antisense oligonucleotides against *NAB2::STAT6* in solitary fibrous tumour,
evaluated against CRISPR-engineered isogenic fusion-positive and fusion-negative cells, reduced
fusion expression by 58% and proliferation by 22% in vitro.<sup>16</sup><!--PMID:37370737-->

Three assay controls are required, and a knockdown assay alone distinguishes none of them. A positive
control gapmer against an abundant housekeeping transcript in the same cells separates failed
delivery from a reagent that reached its target and did not cleave it, and it must carry the same
5-6-5 β-D-oxy-locked-nucleic-acid phosphorothioate geometry as the test article, since uptake and
endosomal release track chemistry class; that is the chemistry of the two named reagents themselves,
which the canonical sequence file carries in full. A scrambled gapmer of the same chemistry and geometry,
dinucleotide-preserving so that nearest-neighbour stacking composition and the terminal bases are
held as well as base composition, separates the backbone-class component of toxicity; that shuffle
does not hold a 5′ guanine run, which has to be imposed by hand where the test article carries one.
The scramble actually ordered must itself be put through the mature-parent screen before it is made,
because 10.0% of dinucleotide-preserving scrambles pair a parent's whole catalytic gap at the
ten-base-pair criterion and 3.9% do so against wild-type *NR4A3*. That screen is
`aso_parent_gap_pairing.py`, and it takes the target window rather than the antisense strand:
screening the sequence as it would be ordered searches the complement and returns a false pass, so
the scramble must be reverse-complemented before it is submitted. A scramble reaching the criterion
against a wild-type parent is redrawn rather than adjusted, because a single-base edit moves a
design to a neighbouring register whose verdict may differ (Table 2). A
fusion-negative isogenic comparator supplies the discrimination readout that neither of the other two
gives, and no supplier of one is named here: such a pair has to be engineered. A fourth arm is free: the three all-screen-clear designs of §3, named in the extended report.

The decision threshold should be fixed before the experiment. Selectivity is the wild-type *NR4A3*
half-maximal knockdown concentration divided by the fusion's, from a matched dose-response in the
same wells, and the cut is 5.0, taken as a convention rather than measured for this comparison. A
ratio of residual transcript at a single dose is not commensurate with it and must not be compared
against the same cut: that ratio is bounded above by one divided by the fusion knockdown's
complement, so at the 58% knockdown reported for the published experiment above it cannot exceed
approximately 2.4 however selective the reagent is, and a cut of 5 would return falsification as
arithmetic rather than as biology.

The replicate count follows from the variance rather than being asserted. At a replicate standard
deviation of 0.35 on the natural-log scale, six independent biological replicates give about 80%
power to falsify a true selectivity of 3 and three give about 30%, computed from a noncentral t.
Above a standard deviation of about 0.65, no observed ratio at or above one can place the upper limit
of a two-sided 95% interval below 5 at three replicates, so the test can fail only where the reagent
is anti-selective, and such a test is void. The replicate count should be set from a pilot estimate with three as a floor and
not a target, and the void gate applied to the upper confidence bound on the pilot's standard
deviation rather than to its point estimate. The ranking is falsified only where the upper bound of
the interval lies below the cut, never where a point estimate does.

Two limits of that threshold belong with any result. It is defined on wild-type *NR4A3*, which is the
acceptor parent; no donor parent is read by the ratio, so a reagent can clear the cut while pairing a
donor transcript through its whole catalytic gap. Wild-type transcript for the reagent's own donor
parent, and for the parent carrying its longest duplex, should be measured in the same wells and
reported beside the ratio against no cut. No cut is stated for a donor ratio because no retrieved
measurement bounds the parent case, so a threshold on it would be a number with nothing behind it;
the donor measurement is required to be reported and is not required to clear anything. A result on
the stated cut can therefore falsify the ranking and cannot falsify the rationale. No multiplicity correction is imposed, for the reason the extended
report gives: the family over which an error rate would be controlled is open-ended.

## 6 · Beyond the panel

The panel is bounded by what has been sequenced rather than by what can be designed, and the
procedure that produced the 190 designs is released unchanged with the artefacts. A design is
certifiable where all five screens could be run on it and it cleared all five; a design one screen
cannot address is uncertifiable whatever the other four return. What the procedure yields is a
candidate, not a validated reagent.

## 7 · Discussion

Designability is not the constraint in this disease. Junction-spanning designs exist at every
in-frame *NR4A3* fusion junction modelled here, and 35 of the 38 have one clearing the parent screen.
The constraint is discrimination between the fusion and its parents, and it is not resolved here. A
junction design's most plausible wild-type liability is its own parent, in the mature transcript or
across a splice junction in precursor RNA; both compartments are searched here before any molecule
exists. The four reports of parental sparing cited
here<sup>8,17,9,10</sup><!--PMID:33241214,36265509,21846246,23052253--> were all made on molecules
already synthesised. What other groups do at the design stage is not established here; no survey of
published design pipelines was performed. The premise that sparing wild-type *NR4A3* is worth a
specificity cost also deserves examination: *NR4A3* has two close paralogues and the family is
functionally redundant where tested,<sup>18,19</sup><!--PMID:29343483,25446259--> which cuts against
it, and the evidence is not decisive either way.

Three limits bound what any test of these reagents could show. All five screens address
hybridisation rather than cleavage, and none establishes that a predicted duplex forms or is cut.
The method-level novelty of this work is nil, junction-directed oligonucleotides being long
established; what is new is the indication and the screen applied before synthesis. And systemic,
antigen-dependent delivery of an oligonucleotide to a solid tumour remains unsolved, which is the
gate this modality faces after any result reported here. Nothing in this work addresses it.

One constraint sits above all of the others and no reagent choice moves it. Every source of a test
article named here ends at someone culturing cells, so the rate-limiting step is a laboratory rather
than a line, a construct or an oligonucleotide.

## 8 · Methods

All analyses are computational and use public data. No laboratory work was performed. Full
parameters, every screen's settings, the complete bounds on each claim and the per-design tables are
in the extended report named under Data availability.

Canonical transcripts for the five partner genes and for *NR4A3* were obtained from
Ensembl.<sup>20</sup><!--PMID:39656687--> Junction-spanning 16-mer gapmers were tiled in a 5-6-5
β-D-oxy-locked-nucleic-acid/DNA/β-D-oxy-locked-nucleic-acid geometry,<sup>21</sup><!--PMID:24981949-->
one design per register at which the breakpoint falls inside the six-nucleotide DNA gap, which admits
five per junction. A design's gap-level margin is the count of junction-unique bases inside the gap
on the shorter side of the breakpoint.

Five specificity screens were applied: an alignment screen against human RefSeq RNA, classifying each
near-match by whether the catalytic gap is paired; an exhaustive transcript scan complete for
substitutions within a one-mismatch budget; a screen of the parents' unspliced sequence; a
mature-parent screen recording the longest contiguous duplex any of six wild-type parent transcripts
forms through the catalytic gap; and a genome-wide screen over every position of GRCh38. A near-match
is a transcript window pairing a design at 14 or more of its 16 positions. A design is liable where a
wild-type parent pairs its whole catalytic gap over a contiguous run of ten base pairs or more, ten
being adopted rather than measured. Null ensembles were built as scrambles of each design and as
chimeras joining the same two parent transcripts at real exon termini, screened identically.

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
copying from this article, and not at all until the breakpoint of the cell line or patient sample
has been established at nucleotide resolution by RNA sequencing.

**Ethics approval, consent to participate and consent for publication.** Not applicable. No human
subjects, human material or animals were involved.

**Data and code availability.** All code, graded artefacts and per-design tables are public and are
deposited under [doi:10.5281/zenodo.22028916](https://doi.org/10.5281/zenodo.22028916). The extended
report of this work, carrying every screen's full parameters and the complete bounds on each claim,
is deposited as a preprint on bioRxiv. An earlier version of these analyses placed the acceptor
junction incorrectly through a coding-versus-transcript exon indexing error and was withdrawn in
full; the panels were rebuilt and verified against two independent transcript acquisitions, and the
complete correction record, including every superseded value, is released with the archive.

**Use of artificial intelligence.** A large language model (Claude, Anthropic) was used throughout
this work: to write and review the analysis code, to run the screens, to retrieve and check
literature, and to draft and revise this manuscript. Every quantitative claim is tied by automated
guard to the committed artefact that produces it. The author directed all work reported here and is
responsible for its content.


**Funding.** This work received no external funding and was self-funded by the author.

**Competing interests.** The author declares no financial competing interests: he holds no patent,
patent application, equity or consultancy relating to any sequence or method described here.


## References
