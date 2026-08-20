---
id: DOC-FUSION-JUNCTION-ASO-JOURNAL
title: "Two junction-spanning gapmer reagents for NR4A3 fusion transcripts in extraskeletal myxoid chondrosarcoma, selected from 190 designs against a wild-type parent screen that condemns 87"
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

# Two junction-spanning gapmer reagents for *NR4A3* fusion transcripts in extraskeletal myxoid chondrosarcoma, selected from 190 designs against a wild-type parent screen that condemns 87

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
normal transcript, so an antisense gapmer could in principle cleave the fusion and spare both parents. This work is computational: nothing was synthesised or tested, and nothing here asserts
efficacy, safety, delivery or clinical readiness. Every sequence named is a research
reagent for laboratory investigation only and must not be administered to any person or animal. Of
190 junction-spanning 16-mers tiled at 5-6-5 across the 38 in-frame junctions of five
modelled partners, 87 let a mature wild-type parent transcript pair their whole catalytic gap over
ten or more contiguous base pairs, 61 of those against wild-type *NR4A3* itself. Two reagents are
named at the two most frequently reported breakpoints: 5′-GGGCATATCATCAAAC-3′ at
*EWSR1* exon 12 and 5′-GGGCATATCTTGTGTG-3′ at *TAF15* exon 6, both at the panel's top gap-level
margin of three, with longest wild-type parent runs of eight and nine base pairs. Two fusion-positive
EMC cell models and two engineered constructs at these junctions are named as test articles,
and the design pipeline is released for breakpoints outside the panel.

---

## Background

EMC is defined in the large majority of cases by an in-frame fusion of *EWSR1* to
*NR4A3*,<sup>1</sup><!--PMID:8634690--> with *TAF15* a substantial minority and *TCF12* and *TFG*
rare.<sup>2</sup><!--PMID:32572850--> The disease responds poorly to conventional cytotoxic
chemotherapy,<sup>8</sup><!--PMID:24345066--> and the tyrosine-kinase inhibitors trialled in it give
disease control more often than response.<sup>7</sup><!--PMID:31331701-->

The fusion junction is the one feature of an EMC tumour that exists at the RNA level and in no normal
cell. An antisense gapmer tiled across it recruits RNase-H1 to cleave the transcript it pairs, and
the six-nucleotide DNA gap at the centre of a 5-6-5 architecture is where that cleavage occurs.
Junction-directed oligonucleotides are a thirty-five-year lineage, reported against *BCR::ABL1*,<sup>10</sup><!--PMID:1794439-->
*EWSR1::FLI1*,<sup>11</sup><!--PMID:9049825--> *FGFR3::TACC3*,<sup>13</sup><!--PMID:33241214-->
*PML::RARα*,<sup>15</sup><!--PMID:21846246--> *TMPRSS2::ERG*<sup>16</sup><!--PMID:23052253--> and
*DNAJB1::PRKACA*.<sup>18</sup><!--PMID:37980543--> No such design is reported for any *NR4A3* fusion
in the literature retrieved here, and that absence is the reason this work exists: EMC is rare enough
that the design step has not been done, and rare enough that no group is likely to do it as a
by-product of something else.

What a junction design has to survive is specific to its construction. Both halves of the
oligonucleotide are parent-gene sequence, so each of the fusion's two parents matches roughly half
of it. Half-identity falls far outside the mismatch budget of a conventional off-target search, so a
parent transcript is not returned as a near-match. RNase-H1, however, does not require the whole
duplex. It requires the gap to be paired. Whether a wild-type parent pairs the catalytic gap
contiguously is therefore a separate question from overall similarity, and it is the question this
work puts to all 190 designs before any of them is recommended.

## The reagents

The two reagents named for synthesis are the best available designs at the two junctions with a
published exon-resolved breakpoint and the highest reported prevalence:
5′-GGGCATATCATCAAAC-3′ at *EWSR1* exon 12 joined to *NR4A3* exon 3, and 5′-GGGCATATCTTGTGTG-3′ at
*TAF15* exon 6 joined to *NR4A3* exon 3. Both hold the panel's top gap-level margin of three, meaning
three junction-unique bases inside the catalytic gap on the shorter side of the breakpoint. Neither
pairs a wild-type parent through the gap at the ten-base-pair criterion adopted here.

Both sit close to that criterion, and the number belongs beside the sequence rather than in a
limitations paragraph. The *EWSR1* reagent's longest wild-type parent run is eight base pairs and the
*TAF15* reagent's is nine, both against wild-type *TFG*. Where the criterion is set therefore decides
how the two read: at a cut of eight both fall inside the class this work marks as not to be ordered,
at nine the *TAF15* reagent alone does, and only at ten does neither. The panel moves with them, 143
of the 190 designs pairing a wild-type parent through the whole gap at a cut of eight, 98 at nine and
87 at ten. Ten is adopted as a convention and is not measured for this architecture.

Predicted transcriptome load separates the two. The *EWSR1* reagent carries 123 gap-paired
sense-strand near-matches at ten times the default search depth, recounting to six gene loci, none of
them on a parent transcript; the *TAF15* reagent carries eight such near-matches at five loci. The
*EWSR1* reagent also carries a sense-strand near-match in wild-type *TAF15* precursor RNA at two
mismatches, one of them inside the catalytic gap, spanning an intron-exon boundary. That site is the
cost of the same ten shared donor bases that let one oligonucleotide span the *EWSR1*, *TAF15* and
*FUS* breakpoints at once. The *TAF15* reagent carries no sense-strand precursor site at all. Neither
load is a disqualification, and neither is a statement about safety: these are predictions from
sequence search, not measured off-target activity.

Discounted by the breakpoint distribution of an 18-case series,<sup>22</sup><!--PMID:12378528--> the
two junctions account for 68.4% of molecularly confirmed cases in a 58-case
cohort,<sup>9</sup><!--PMID:36948401--> roughly two thirds. That figure prices which published
junctions the two reagents address. It is not a coverage measurement, no patient having been screened
with either sequence, and its interval is wide for the denominators rather than for the estimate,
spanning 39.9% to 82.8% when each breakpoint fraction is taken to its own Wilson bound.

## Selection from a panel of 190 designs

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
conceding parent-paired gap DNA at the design's own seam, and across the three geometries screened
the count of designs pairing a parent at the ten-base-pair criterion is flat at 87, 88 and 87.

Three designs clear every screen applied here. None of the three sits at a junction any patient is
reported to carry, which is what makes them mechanism controls rather than candidates.
Selecting within each junction rather than across the panel is what makes the two named reagents
available: 35 of the 38 junctions have a design that clears the parent screen, and all five junctions
with a published exon-resolved breakpoint have one.

Two bounds on the cleanliness claim are load-bearing and are stated with it. The alignment screen is
heuristic and stores at most 50 hits per query, so only 47 of the 183 filtered designs have hit lists
short enough to assess for cleanliness at all; a count of clean designs is therefore a floor over
that subset rather than a total over the panel. And search depth moves the result: of the nine designs
that carry no sense-strand near-match at the default search ceiling, six are not clean at ten times
it, three of the six having returned no near-match whatever at the shallower setting.

The ten-base-pair criterion is adopted rather than measured, and the comparison against null models
does not resolve an excess specific to this disease. Scrambled sequences meet the parent screen at
6.2% against 45.8% for designs at real breakpoints, but chimeras built at real exon termini of the
same two transcripts, at junctions almost never reported in a patient, meet it at 40.6%. Most of the
liability is therefore what joining two exon termini of these genes gives, and across cuts of six to
thirteen base pairs the excess of the observed rate over the strongest null changes sign four times.
No cut in that range is a boundary the data picks out.

## Test articles

Five test articles carry a junction this panel designs against, and they divide into two sources with
opposite limits.

Three are engineered constructs from a published functional study,<sup>27</sup><!--PMID:31020999-->
whose exon spans that paper states verbatim. Two of them, E-N and T-N*, carry exactly the two
junctions the reagents above span, so both named reagents have a stated test article. Rebuilding the
constructs is the faster route and its critical path contains no laboratory that has to answer an
email. What it cannot buy is biological relevance: a complementary DNA over-expressed in a
heterologous background is not the disease, so such an experiment speaks to junction-selective
knockdown of the intended transcript and not to activity at endogenous expression from an endogenous
locus.

The other two are patient-derived, identity-clean models reported with two EMC
tumours,<sup>37</sup><!--PMID:36316541--> USZ20-EMC1 (RRID:CVCL_C6MX) and USZ22-EMC2
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
partner,<sup>6</sup><!--PMID:41055792--> so on its own it locates neither the partner nor the exon
pair.

## The falsification experiment

The experimental design that would resolve the central uncertainty, an isogenic
fusion-positive against fusion-negative comparison, has been published in an analogous fusion
sarcoma. Fusion-specific antisense oligonucleotides against *NAB2::STAT6* in solitary fibrous tumour,
evaluated against CRISPR-engineered isogenic fusion-positive and fusion-negative cells, reduced
fusion expression by 58% and proliferation by 22% in vitro.<sup>38</sup><!--PMID:37370737-->

Three assay controls are required, and a knockdown assay alone distinguishes none of them. A positive
control gapmer against an abundant housekeeping transcript in the same cells separates failed
delivery from a reagent that reached its target and did not cleave it, and it must carry the same
5-6-5 β-D-oxy-locked-nucleic-acid phosphorothioate geometry as the test article, since uptake and
endosomal release track chemistry class. A scrambled gapmer of the same chemistry and geometry,
dinucleotide-preserving so that guanine content and the 5′ run are held as well as base composition,
separates the backbone-class component of toxicity; the scramble actually ordered must itself be put
through the mature-parent screen before it is made, because 6.2% of scrambles pair a parent's whole
catalytic gap at the ten-base-pair criterion and 1.8% do so against wild-type *NR4A3*. A
fusion-negative isogenic comparator supplies the discrimination readout that neither of the other two
gives, and no supplier of one is named here: such a pair has to be engineered. A fourth arm is
available at no design cost: the three designs that clear every screen sit at junctions no patient is
reported to carry, which makes them mechanism controls for gap-directed cleavage rather than
candidates, and the extended report names them.

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
is anti-selective. Such a test is void: it cannot fail, which is a different outcome from one that
fails to falsify. The replicate count should be set from a pilot estimate with three as a floor and
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
the stated cut can therefore falsify the ranking and cannot falsify the rationale. And no multiplicity correction is imposed, because the
family over which an error rate would be controlled is open-ended: the released procedure generates
reagents against the same ranking without limit, so how many reagents have been tested against this
cut, and in what order, is part of a result rather than context for it.

## Beyond the panel

The named reagents do not reach every patient, and the panel is bounded by what has been sequenced
rather than by what can be designed. The procedure that produced the 190 designs is released
unchanged with the artefacts, and it is the second deliverable of this work. Its input is the
breakpoint at nucleotide resolution; an exon pair inferred from a break-apart assay is not
sufficient. Given a declared exon pair it retrieves the parent transcripts, builds the modelled
fusion, grades the pair for frame, tiles the junction-spanning gapmers, and runs the five screens,
of which the two parent screens matter most, since pairing a parent through the whole catalytic gap
surrenders the only advantage the modality has. A design is certifiable where all five screens could
be run on it and it cleared all five; a design one screen cannot address is uncertifiable whatever
the other four return. What the procedure yields is a candidate, not a validated reagent.

## Discussion

Designability is not the constraint in this disease. Junction-spanning designs exist at every
in-frame *NR4A3* fusion junction modelled here, and 35 of the 38 have one that clears the parent
screen. The constraint is discrimination between the fusion and its parents, and it is not resolved
here. A fusion-junction design's most plausible wild-type liability is its own parent, reached either
in the mature transcript or across a splice junction in precursor RNA, and both compartments are
searched in this work before any molecule exists. The four reports of parental sparing cited
here<sup>13,14,15,16</sup><!--PMID:33241214,36265509,21846246,23052253-->
were all made on molecules already synthesised, and three of the four went further than cells. Every
one of those readouts required the molecule to exist first. What other groups do at the design stage
is not established here; no survey of published design pipelines was performed.

The premise that sparing wild-type *NR4A3* is worth a specificity cost deserves examination rather
than assumption. *NR4A3* has two close paralogues and the family is functionally redundant where it
has been tested,<sup>29,30</sup><!--PMID:29343483,25446259--> which cuts against the premise; the
evidence is not decisive in either direction.

Several limits bound what any test of these reagents could show. Every screened count here is for one
architecture, a 16-mer at 5-6-5. All five screens address hybridisation rather than cleavage, and
none establishes that a predicted duplex forms or is cut. Counts are lower bounds, the alignment
screen being heuristic and depth-dependent. Which exon pair a patient carries is not decidable from a
break-apart assay, so no reagent named here is valid for a tumour whose seam has not been sequenced.
The method-level novelty of this work is nil, junction-directed oligonucleotides being long
established; what is new is the indication and the screen applied before synthesis. And systemic,
antigen-dependent delivery of an oligonucleotide to a solid tumour remains unsolved, which is the
gate this modality faces after any result reported here. Nothing in this work addresses it.

One constraint sits above all of the others and no reagent choice moves it. Every source of a test
article named here ends at someone culturing cells, so the rate-limiting step is a laboratory rather
than a line, a construct or an oligonucleotide.

## Methods

All analyses are computational, use public data, run in continuous integration at no compute cost,
and commit their outputs. No laboratory work was performed. Full parameters, every screen's settings,
the complete bounds on each claim and the per-design tables are in the extended report, which is the
bioRxiv preprint of this work; the released artefacts are in the archive named under Data
availability.

Canonical transcripts for the five partner genes and for *NR4A3* were obtained from
Ensembl.<sup>40</sup><!--PMID:39656687--> Junction-spanning 16-mer gapmers were tiled in a 5-6-5
β-D-oxy-locked-nucleic-acid/DNA/β-D-oxy-locked-nucleic-acid geometry,<sup>39</sup><!--PMID:24981949-->
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

## Display items

Tables 1 and 2 are in `fusion-junction-aso-journal-tables.md`, generated from the canonical sequence
file by `research/manuscripts/aso_journal_tables.py` so that a cell and its source cannot diverge.

**Figure 1. One 16-mer spans three partners' breakpoints.** The junction windows of *EWSR1* exon 12,
*TAF15* exon 11 and *FUS* exon 10 joined to *NR4A3* exon 3, aligned at the breakpoint. Blue, donor
exon; green, acceptor exon; positions at which the three donors differ are boxed as well as coloured,
for greyscale and colour-blind readers. The shaded box is the target window of
5′-GGGCATATCATCAAAC-3′ with the 5-6-5 architecture below it. The three donors are identical over the
ten nucleotides before the breakpoint, which is what makes one oligonucleotide junction-spanning at
all three. Two of the three drawn junctions are reported in no patient: the exon-resolved *TAF15*
breakpoints in this disease are at exon 6, and no exon-resolved *FUS* breakpoint has been published.
This is a statement about sequence, not a claim that one reagent serves three patient groups.
Coverage is predicted from sequence and has not been measured.

## Declarations

**Research use only, and not for administration to any person or animal.** Every oligonucleotide
sequence in this manuscript and its tables is a research reagent for laboratory investigation only.
None is a medicine or a candidate drug, none has been synthesised or tested, and none may be
administered to any human being or animal or supplied to anyone for that purpose. Ordering any of
them from a commercial synthesis service is possible for anyone; doing so does not make it a
treatment, and nothing in this manuscript should be read as licensing use in a patient. An
oligonucleotide should not be ordered by copying it out of this article: the canonical record is
`fusion-junction-aso-sequences.csv`. No sequence should be ordered at all until the breakpoint of the
cell line or patient sample has been established at nucleotide resolution by RNA sequencing.

**Ethics approval and consent to participate.** Not applicable. No human subjects, human material or
animals were involved.

**Consent for publication.** Not applicable.

**Data and code availability.** All code, graded artefacts and per-design tables are public and are
deposited under [doi:10.5281/zenodo.22028916](https://doi.org/10.5281/zenodo.22028916). The extended
report of this work, carrying every screen's full parameters and the complete bounds on each claim,
is deposited as a preprint on bioRxiv.

**Use of artificial intelligence.** A large language model (Claude, Anthropic) was used throughout
this work: to write and review the analysis code, to run the screens, to retrieve and check
literature, and to draft and revise this manuscript. Every quantitative claim is tied by automated
guard to the committed artefact that produces it. The author directed all work reported here and is
responsible for its content.

**Author contributions.** T.D.M. is the sole author and directed all work reported here.

**Funding.** This work received no external funding and was self-funded by the author.

**Competing interests.** The author declares no financial competing interests: he holds no patent,
patent application, equity or consultancy relating to any sequence or method described here.

**Acknowledgements.** None.

## References

*Numbering follows the extended report, so that a reference cited in both documents carries the same
number in each. Metadata is read from retrieved bibliographic records.*

1. Labelle Y, Zucman J, Stenman G, Kindblom LG, Knight J, Turc-Carel C, Dockhorn-Dworniczak B, Mandahl N, Desmaze C, Peter M. Oncogenic conversion of a novel orphan nuclear receptor by chromosome translocation. Human molecular genetics. 1995;4(12):2219-2226. PMID: 8634690. doi:10.1093/hmg/4.12.2219
2. Paioli A, Stacchiotti S, Campanacci D, Palmerini E, Frezza AM, Longhi A, Radaelli S, Donati DM, Beltrami G, Bianchi G, et al. Extraskeletal Myxoid Chondrosarcoma with Molecularly Confirmed Diagnosis: A Multicenter Retrospective Study Within the Italian Sarcoma Group. Ann Surg Oncol. 2021;28(2):1142-1150. PMID: 32572850. doi:10.1245/s10434-020-08737-7
6. Remiszewski P, Falkowski S, Szumera-Ciećkiewicz A, Spałek MJ, Rutkowski P, Czarnecka AM. From pathogenesis to the patient's bedside: a comprehensive review of extraskeletal myxoid chondrosarcoma. Journal of cancer research and clinical oncology. 2025;151(11):283. PMID: 41055792. doi:10.1007/s00432-025-06316-5
7. Stacchiotti S, Ferrari S, Redondo A, Hindi N, Palmerini E, Vaz Salgado MA, Frezza AM, Casali PG, Gutierrez A, Lopez-Pousa A, Grignani G, Italiano A, LeCesne A, Dumont S, Blay JY, Penel N, Bernabeu D, et al. Pazopanib for treatment of advanced extraskeletal myxoid chondrosarcoma: a multicentre, single-arm, phase 2 trial. The Lancet Oncology. 2019;20(9):1252-1262. PMID: 31331701. doi:10.1016/S1470-2045(19)30319-5
8. Stacchiotti S, Dagrada GP, Sanfilippo R, Negri T, Vittimberga I, Ferrari S, et al. Anthracycline-based chemotherapy in extraskeletal myxoid chondrosarcoma: a retrospective study. Clinical Sarcoma Research. 2013;3(1):16. PMID: 24345066. doi:10.1186/2045-3329-3-16
9. Huang SC, Lee JC, Hsu YC, Tsai JW, Kao YC, Hsieh TH, Chang YM, Chang KC, Wu PS, Chen PC, Chen CH, Chang CD, Lee PH, Tai HC, Liu TT, Wen MC, Li WS, Yu SC, Wang JC, Huang HY. Extraskeletal Myxoid Chondrosarcomas: The Uncommon Clinicopathologic Manifestations and Significance of TAF15::NR4A3 Fusion. Modern pathology. 2023;36(7):100161. PMID: 36948401. doi:10.1016/j.modpat.2023.100161
10. Skórski T, Szczylik C, Malaguarnera L, Calabretta B. Gene-targeted specific inhibition of chronic myeloid leukemia cell growth by BCR-ABL antisense oligodeoxynucleotides. Folia histochemica et cytobiologica. 1991;29(3):85-89. PMID: 1794439.
11. Toretsky JA, Connell Y, Neckers L, Bhat NK. Inhibition of EWS-FLI-1 fusion protein with antisense oligodeoxynucleotides. Journal of neuro-oncology. 1997;31(1-2):9-16. PMID: 9049825. doi:10.1023/a:1005716926800
13. Parker Kerrigan BC, Ledbetter D, Kronowitz M, Phillips L, Gumin J, Hossain A, Yang J, Mendt M, Singh S, Cogdell D, Ene C, Shpall E, Lang FF. RNAi technology targeting the FGFR3-TACC3 fusion breakpoint: an opportunity for precision medicine. Neuro-oncology advances. 2020;2(1):vdaa132. PMID: 33241214. doi:10.1093/noajnl/vdaa132
14. Lee MS, An S, Song JY, Sung M, Jung K, Chang ES, Choi J, Oh DY, Jeon YK, Yang H, Lakshmi C, Park S, Han J, Lee SH, Choi YL. Cancer-Specific Sequences in the Diagnosis and Treatment of NUT Carcinoma. Cancer research and treatment. 2023;55(2):452-467. PMID: 36265509. doi:10.4143/crt.2022.910
15. Ward SV, Sternsdorf T, Woods NB. Targeting expression of the leukemogenic PML-RARα fusion protein by lentiviral vector-mediated small interfering RNA results in leukemic cell differentiation and apoptosis. Human gene therapy. 2011;22(12):1593-1598. PMID: 21846246. doi:10.1089/hum.2011.079
16. Shao L, Tekedereli I, Wang J, Yuca E, Tsang S, Sood A, Lopez-Berestein G, Ozpolat B, Ittmann M. Highly specific targeting of the TMPRSS2/ERG fusion gene using liposomal nanovectors. Clinical cancer research. 2012;18(24):6648-6657. PMID: 23052253. doi:10.1158/1078-0432.ccr-12-2715
18. Neumayer C, Ng D, Requena D, Jiang CS, Qureshi A, Vaughan R, Prakash TP, Revenko A, Simon SM. GalNAc-conjugated siRNA targeting the DNAJB1-PRKACA fusion junction in fibrolamellar hepatocellular carcinoma. Molecular therapy. 2024;32(1):140-151. PMID: 37980543. doi:10.1016/j.ymthe.2023.11.012
22. Panagopoulos I, Mertens F, Isaksson M, Domanski HA, Brosjö O, Heim S, Bjerkehagen B, Sciot R, Dal Cin P, Fletcher JA, Fletcher CD, Mandahl N. Molecular genetic characterization of the EWS/CHN and RBP56/CHN fusion genes in extraskeletal myxoid chondrosarcoma. Genes, chromosomes & cancer. 2002;35(4):340-352. PMID: 12378528. doi:10.1002/gcc.10127
27. Brenca M, Stacchiotti S, Fassetta K, Sbaraglia M, Janjusevic M, Racanelli D, et al. NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas. J Pathol. 2019;249(1):90-101. PMID: 31020999. doi:10.1002/path.5284
29. Freire PR, Conneely OM. NR4A1 and NR4A3 restrict HSC proliferation via reciprocal regulation of C/EBPα and inflammatory signaling. Blood. 2018;131(10):1081-1093. PMID: 29343483. doi:10.1182/blood-2017-07-795757
30. Beard JA, Tenga A, Chen T. The interplay of NR4A receptors and the oncogene-tumor suppressor networks in cancer. Cellular signalling. 2015;27(2):257-266. PMID: 25446259. doi:10.1016/j.cellsig.2014.11.009
37. Bangerter JL, Harnisch KJ, Chen Y, Hagedorn C, Planas-Paz L, Pauli C. Establishment, characterization and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma (EMC) cell models. Human cell. 2023;36(1):446-455. PMID: 36316541. doi:10.1007/s13577-022-00818-x
38. Li Y, Nguyen JT, Ammanamanchi M, Zhou Z, Harbut EF, Mondaza-Hernandez JL, Meyer CA, Moura DS, Martin-Broto J, Hayenga HN, Bleris L. Reduction of Tumor Growth with RNA-Targeting Treatment of the NAB2-STAT6 Fusion Transcript in Solitary Fibrous Tumor Models. Cancers. 2023;15(12):3127. PMID: 37370737. doi:10.3390/cancers15123127
39. Kauppinen S, Vester B, Wengel J. Locked nucleic acid (LNA): High affinity targeting of RNA for diagnostics and therapeutics. Drug discovery today. Technologies. 2005;2(3):287-290. PMID: 24981949. doi:10.1016/j.ddtec.2005.08.012
40. Dyer SC, Austine-Orimoloye O, Azov AG, et al. Ensembl 2025. Nucleic acids research. 2025;53(D1):D948-D957. PMID: 39656687. doi:10.1093/nar/gkae1071

## Appendix A. Correction and supersession register

This appendix records corrections that reached the analyses behind this manuscript, so that a reader
comparing it against earlier versions of the work can see what changed and why. The full chronology
is in the working record deposited with the archive.

### Appendix A1 — Withdrawn reagents

An earlier draft of this work recommended two reagents that a deeper re-screen subsequently withdrew.
They are named here as withdrawn rather than dropped silently. Six of the nine designs that carried
no sense-strand near-match at the default search ceiling lost that property at ten times the ceiling,
three of them having returned no near-match at all at the shallower setting. The reagents named in
the present manuscript are those that survive the deeper screen.

### Appendix A2 — Exon-numbering correction

An earlier version of these analyses placed the acceptor junction using coding-exon indices and
concatenated coding sequence to coding sequence, which discarded the 5′ untranslated region that
*NR4A3* transcript exon 3 carries and which a fusion transcript retains. The corrected model is
mRNA-level. Exon numbers in this manuscript are transcript exon indices counted from the transcript
5′ end, including non-coding exons; the two conventions differ for *TCF12*, *TFG* and *NR4A3*. An
acceptor exon number read under the wrong convention selects a different reagent.

### Appendix A3 — Terminology

The term *cleavage risk* was replaced by *gap-paired sense-strand match* on 2026-08-19, because the
earlier term named a catalytic outcome for what is a sequence observation. No screen in this work
predicts cleavage; each grades hybridisation only.
