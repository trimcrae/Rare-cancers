---
id: DOC-EMC-VACCINE-DEVELOPMENT-PATH
title: "A fusion-junction vaccine in extraskeletal myxoid chondrosarcoma: what can be established today, and the capabilities that would change it"
level: L3
kind: manuscript
status: live
canonical_for: [emc-vaccine-development-path]
purpose: >
  State the best characterisation of a EWSR1::NR4A3 junction vaccine obtainable with today's
  instruments and today's access, separate the limits that are properties of the disease from
  those that are properties of current method, and record for each movable limit what active
  research would move it and by when.
scope: >
  Computational and evidence-synthetic. No wet-laboratory work was performed. No efficacy,
  safety or clinical-readiness claim is made for any agent or combination.
audience: [external reviewers, collaborators, maintainers, autonomous research agents]
date: 2026-08-19
last_verified: 2026-08-19
---

# A fusion-junction vaccine in extraskeletal myxoid chondrosarcoma: what can be established today, and the capabilities that would change it

**Author.** Tristan D. McRae

*Independent researcher, unaffiliated.* Correspondence: trimcrae@gmail.com
ORCID: [0000-0002-1823-1451](https://orcid.org/0000-0002-1823-1451)

**Preprint status.** This manuscript is a preprint. It has not been peer reviewed and has not been
submitted to a journal. It has not been read by a sarcoma medical oncologist or by a tumour
immunologist, and a reader should weigh it accordingly. Independent, personal-capacity work,
unconnected to the author's employer; Section 9 states the role of AI tools.

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is a rare soft-tissue sarcoma defined by
rearrangement of *NR4A3*, most often to *EWSR1*. The fusion junction encodes a peptide sequence absent
from either parent protein, and because the fusion is the truncal oncogenic driver it is present in every
tumour cell and cannot be lost without loss of the driver. Individualised neoantigen therapy has now
reported a positive phase 3 result in resected melanoma, which makes the platform question timely for
other tumours.

**Purpose.** This paper does not predict whether an EMC vaccine will work, and it does not argue that it
will not. It reports the most complete characterisation of the target that current instruments and current
access permit, states plainly where each conclusion is bounded by the tumour's biology rather than by
method, and records for every limit that is a property of method or access what specific advance would move
it, on what evidence, and on what timescale. It is intended to be re-read against a changing field rather
than to settle a question.

**Methods.** Junctions were derived at the transcript level from Ensembl exon structure, so the acceptor
exon is retained whole including its 5' untranslated region. Class I binding was predicted with MHCflurry
2.1.4 (models release 2.2.0) [2], on a ten-allele panel for the junction screen and a 34-allele panel for
the coverage scan, calling a peptide strong at a presentation percentile of 0.5 or below. Class II binding
was predicted with MHCnuggets [12] on three DRB1 alleles, calling a peptide strong below 100 nM and a
binder below 1000 nM. Population coverage is the union carrier frequency of the presenting alleles over
Allele Frequency Net Database records [1]; the sampling model such pooling would require does not hold
here, so no confidence interval is placed on it, and the threshold sensitivity is reported instead.
Peptide novelty was assessed by exact-match search against the UniProt reviewed human proteome including
isoform sequences. Clinical evidence was drawn from a curated EMC registry with structured citation
provenance. No new wet-laboratory data were generated.

**What can be established today.** Of 27 declared exon pairs, 5 are in frame and yield 11 distinct
predicted binders, of which 4 are strong; there is no pan-EMC epitope. Predicted class I coverage is a
property of the allele panel screened as much as of the junction, and the paper reports both panels rather
than one. On the ten-allele screen the commonly reported *EWSR1* exon 7 to *NR4A3* exon 3 junction is
presented on HLA-B\*15:01 alone and covers 8.5% of the pooled reference populations; on 34 alleles the same
lead peptide is also strong on HLA-A\*30:02 and the junction covers 12.3%. Pooling every in-frame junction
gives 27.4% on ten alleles and 30.4% on 34, which is one quantity at two panel widths rather than two
quantities. None of these is a ceiling: each of the four presenting alleles rests on a single
peptide-allele call, all five such calls lie within 0.13 percentile units of the acceptance threshold, and
moving that threshold from 0.50 to 0.37 removes every one of them. 170 of 174 junction peptides
are absent from the reviewed human proteome including isoforms, and all 4 strong binders survive that
search. The 4 that do not all occur in an *NR4A3* isoform and all belong to the four junctions whose seam
codon is aspartate; one is a predicted binder and is withdrawn. The class II arm returns 2 predicted
binders and no strong binder on three DRB1 alleles, of which only one produced anything within an order of
magnitude of a threshold, so combined CD8 and CD4 coverage is not computed rather than null: zero of three
alleles bounds the per-allele strong-binder rate only at 63% from above, and the candidate construct is 11
residues carrying class I epitopes only. In a phase 2 histology-specific EMC cohort of sunitinib plus
nivolumab, 16 of 23 evaluable patients were progression-free at 6 months and median progression-free
survival was 13.2 months; that report is a single-arm conference abstract, is not peer reviewed, and is
cited here only to establish that a trial vehicle exists in this disease.

**What bounds each conclusion.** Of ten limits enumerated, three are properties of this tumour and this
junction and will not move: antigen depth, the physical myxoid barrier, and disease incidence. Four are
limits of current instruments: sequence-based binding prediction standing in for measured presentation,
class II prediction on a narrow allele panel, a novelty filter that reads canonical proteins only, and the
absence of any fusion-junction-validated presentation model. Three are limits of access rather than of
knowledge: no EMC immune profiling, no reachable patient-derived material, and no manufacturing route at
this incidence. Each instrument and access limit is paired with the specific advance that would move it and
with the observation that would show it had arrived.

**Interpretation.** The most defensible present statement is neither that the route is viable nor that it
is closed, but that it is instrument-limited in identifiable ways, and that several of the numbers a reader
would take as bounding it are bounding the screen instead. Two findings are offered as results rather than
as framing: that seam-proximal peptides of four of the five in-frame junctions reproduce a sequence in a
normal *NR4A3* isoform, which withdraws one predicted binder and is a defect in the novelty filter that
will recur at any breakpoint whose seam reconstructs an isoform boundary; and that the coverage figures
this route has been graded on move with the allele panel and the acceptance threshold by more than the
spread between them. The paper also observes that this programme's own route ledger excluded several
priming-directed classes for this disease on the ground that antigen supply is what EMC lacks, and that a
vaccine is an antigen supply, so the combination was never graded as a unit here. That is an observation
about how this programme graded its own routes, not a correction offered to the field, and the standing
objection to the vaccine is not the one it answers. Predicted binding is a screen and not evidence of
presentation, immunogenicity or benefit, and nothing here supports use of any agent outside a clinical
trial.

## 1. A standing-state report rather than a verdict

A therapeutic hypothesis in a rare disease is usually written up once, as an argument for or against. That
format serves neither the reader nor the hypothesis when the binding constraint is not the biology but the
instrument. A verdict of "unpromising" delivered against a target whose presentation has never been
measured records the state of the measuring apparatus, and it records it in a form that looks like a
statement about the tumour and that nobody revisits when the apparatus improves.

This paper is written in the opposite format. It separates three kinds of limit that a single verdict
conflates. Some limits are properties of this disease and this junction: a quiet genome offers few
antigens, a myxoid matrix physically excludes lymphocytes, and an incidence below one per million per year
constrains every study design. Those will not move, and the paper marks them as fixed. Other limits are
properties of today's instruments: a sequence-based binder predictor is standing in for a measurement
nobody has taken, a class II panel of three alleles is standing in for the class II locus, and a novelty
filter that reads canonical proteins was standing in for the proteome until this work replaced it. Those
move when methods move. A third group are limits of access rather than of knowledge: no EMC immune
profiling has been published, no patient-derived material is reachable without an affiliation, and no
manufacturing route exists at this incidence without a partner. Those move when circumstances change, and
on quite different timescales from the methods.

For every limit in the second and third groups, Section 3 records the specific advance that would move it
and the evidence that would count as that advance arriving. No date is attached to any of them. Section 6
states, for each, what would look like that advance arriving without being it: a result on a different
fusion, a cloud laboratory that supplies robots but not the cell line, and a general improvement in
neoantigen prediction have each been mistaken for the specific capability this route waits on.

The immediate occasion is external. The sponsors of an individualised neoantigen therapy given with
pembrolizumab have announced that a randomised phase 3 trial met its primary endpoint of recurrence-free
survival in resected stage IIB to IV melanoma [9]; that announcement is a company press release, no effect
size was disclosed in it, and the peer-reviewed evidence in this setting remains the phase 2b trial [3].
The result does not transfer to EMC, and Section 4 sets out the axis on which the transfer fails. What it
shows is that the manufacturing, regulatory and delivery apparatus for an individualised RNA vaccine
exists as a clinical reality rather than as a proposal.

## 2. The target and its current evidence base

### 2.1 Disease and fusion

EMC accounts for roughly 1 to 3% of soft-tissue sarcomas, with an estimated incidence well under one per
million per year [7]. It is defined by rearrangement of *NR4A3* on chromosome 9q22. *EWSR1*::*NR4A3* is
the commonest fusion, reported in approximately 62 to 75% of cases [7] and in 79% of a molecularly
confirmed series of 58 cases [10]; variant partners include *TAF15*, *TCF12*, *TFG* and *FUS* [7]. The
genome is otherwise quiet, and the fusion is the truncal driver.

Two consequences follow, and they point in opposite directions. Because the fusion is truncal and clonal,
it is present in every tumour cell and cannot be subclonally lost, so a T-cell response directed at the
junction cannot be escaped by antigen loss in the way that a response against a passenger mutation can.
Because the genome is quiet, the junction is close to the only tumour-exclusive antigen the disease
offers, so if the junction fails there is no second candidate to fall back on. The same feature that
makes the target durable makes the portfolio of targets shallow.

### 2.2 Junction structure and predicted binding

Junctions were derived from the spliced transcripts rather than from an assumed breakpoint, so the
acceptor exon is retained whole with its 5' untranslated region, as a fusion transcript retains it. This
matters: a superseded model that concatenated coding sequences discarded that retained region and
selected a junction disjoint from the one the transcript model produces. All figures below are from the
transcript model.

Of 27 declared exon pairs, 5 are in frame: *EWSR1* exons 7, 9, 10, 12 and 13 joined to *NR4A3* exon 3. The
remaining 22 are graded out as non-coding acceptor (9), out of frame (4) or not producing the seam (9).
The in-frame set yields 174 distinct junction-spanning peptides, screened with MHCflurry 2.1.4 (models
release 2.2.0) [2] over the ten alleles HLA-A\*01:01, A\*02:01, A\*03:01, A\*11:01, A\*24:02, B\*07:02,
B\*08:01, B\*15:01, B\*35:01 and B\*44:02, calling a peptide strong at a presentation percentile of 0.5 or
below and weak at 2.0 or below. That screen returns 11 distinct predicted binders, 4 of them strong. The
lead candidate at the commonly reported *EWSR1* exon 7 junction is NMPCVQAQY on HLA-B\*15:01, at a
presentation percentile of 0.37 and a predicted affinity of 73.4 nM; the class call is made on the
percentile and not on the affinity, and the two do not agree in rank order across the set, so affinities
are quoted below only alongside the percentile that classified them.

The ten-allele panel is the instrument behind every binder figure in this paper, and a wider one changes
them. A 34-allele screen of the same 174 peptides at the same threshold returns five strong peptide-allele
calls rather than four, because the same lead peptide NMPCVQAQY is also strong on HLA-A\*30:02. Section 2.3
reports both panels for that reason.

There is no pan-EMC epitope: the most widely shared candidate appears in 4 of the 5 junctions and is a weak
binder, three of the five junctions return no strong binder at all, and every strong binder is specific to
its breakpoint. One of the 11 predicted binders, DMPCVQAQY on HLA-B\*35:01, is withdrawn on the proteome
search reported under B5 below, leaving 10; all 4 strong binders survive that search.

### 2.3 Population coverage

Coverage here means the union carrier frequency of the presenting alleles, computed as one minus the
product of squared non-carrier frequencies over Allele Frequency Net Database records [1]. Two properties
of that quantity govern how the figures below should be read, and both are properties of the screen rather
than of the tumour.

**It moves with the panel.** On the ten-allele screen the *EWSR1* exon 7 junction is presented on
HLA-B\*15:01 alone and covers 8.5%; on 34 alleles the same lead peptide is also strong on HLA-A\*30:02 and
the junction covers 12.3%. Pooling every in-frame junction gives 27.4% on ten alleles and 30.4% on 34.
The four figures are one computation at two panel widths and two junction scopes, not four findings, and
the 27.4% and 30.4% pair differs by exactly one allele. Extending the panel further can only raise them,
so none of them is a ceiling and this paper does not call any of them one.

**It moves with the threshold, further than it moves with anything else.** All five strong peptide-allele
calls on the 34-allele screen lie between presentation percentiles 0.3736 and 0.4986, against an
acceptance threshold of 0.5, and each of the four presenting alleles rests on exactly one of them. Moving
the threshold to 0.45 leaves three alleles and 23.2%, to 0.40 leaves one and 8.5%, and to 0.37 leaves
none and 0.0%. A 0.13-unit move in an undefended cut takes the headline figure to zero.

**What is not reported, and why.** Pooling the underlying records yields a binomial count large enough to
produce a Wilson interval about half a percentage point wide, and earlier versions of this analysis
printed those intervals. They are withdrawn here. The same records show the frequency of HLA-B\*15:01
ranging from 0 to 0.40 between the populations pooled, so the single-urn model such an interval requires
is refuted by its own input, and the interval it produces is an order of magnitude narrower than the
threshold sensitivity above. Regional figures are reported as point values for the same reason, and the
spread between them is large: 1.4% in Melanesia and 60% in Northern Europe, on 579 and 923 individuals
respectively. In Northern Europe two alleles reach 52.8%, so statements of the form "no panel reaches
half of patients" hold for the pooled global frame and not everywhere.

Because an individualised platform selects against the patient's own genotype rather than against a public
epitope, the relevant question is what fraction of patients carry any presenting allele, which is the
pooled-junction figure rather than the single-junction one. Selecting per patient therefore moves the
figure from 8.5% to 30.4% on the panels screened here, and does not remove the dependence on either the
panel or the threshold.

### 2.4 Limits of the current evidence

Predicted binding is a screen. It is not evidence that any peptide is presented on an EMC tumour cell, not
a measure of the density at which it would be presented, and not evidence of T-cell recognition. No EMC
immunopeptidomic dataset is known to the author, so nothing here bears on whether any of these peptides
reaches the cell surface. Sequence-level novelty against the proteome has now been tested and is reported
under B5; it excludes one failure mode and leaves presentation, immunogenicity and cross-reactivity
untouched. These gaps are enumerated as limits B2 and B3 below rather than treated as resolved.

## 3. The standing state, limit by limit

Ten limits are enumerated. The second column is the one that matters for how each should be read. A limit
bounded by disease is a property of this tumour or this junction and is not expected to move. A limit
bounded by instrument is a property of the methods currently available, and moves when those methods move.
A limit bounded by access is a property of this programme's circumstances rather than of anyone's
knowledge, and moves when material, collaboration or a partner arrives.

| ID | Limit | Bounded by | Best available answer today | What would move it |
|---|---|---|---|---|
| B1 | Predicted class I coverage is low and panel-dependent | instrument, partly disease | 8.5% and 12.3% for the public junction on 10 and 34 alleles; 27.4% and 30.4% pooled on the same two panels; 0.0% if the acceptance cut moves to 0.37 | Wider allele panels; a defended threshold; measured presentation reweighting the screen |
| B2 | Presentation predicted, never measured | instrument and access | MHCflurry 2.0 percentiles on 174 peptides | Immunopeptidomics on EMC tissue or a patient-derived line |
| B3 | Self-adjacency and central tolerance | instrument | Seam structure characterised; no tolerance model applied | Distance-to-self and anchor-versus-contact filters; T-cell reactivity assay |
| B4 | No strong CD4 epitope found on the panel tested | instrument | 2 binders, 0 strong, on 3 DRB1 alleles of which 1 was informative; bounds the per-allele rate only at 63% from above | Wider DR, DP and DQ panel; a class II threshold convention; measured class II presentation |
| B5 | Seam-proximal peptides of four junctions occur in an *NR4A3* isoform | instrument, one failure mode resolved | 170 of 174 novel proteome-wide; one binder withdrawn | Sequence novelty answered; cross-reactivity and unreviewed sequences are not, and the upstream filter should become isoform-aware |
| B6 | Immunologically cold microenvironment | disease, addressable in combination | Inferred, not measured in EMC | A vaccine supplies antigen; a checkpoint inhibitor supplies release |
| B7 | Physical exclusion by the myxoid matrix | disease | Inferred from histology and pathway expression | Vascular normalisation; matrix-directed agents |
| B8 | No EMC immune profiling published | access | None; the cold and excluded readings are inferences | A deposited EMC series, or a pan-sarcoma atlas reaching this histology |
| B9 | Manufacturing economics at this incidence | access | Five enumerable in-frame junctions, not per-patient discovery | A platform holder; a master-protocol vehicle |
| B10 | Trial design below the randomisation threshold | disease | A 24-patient histology cohort has been run across nine centres | Adaptive or histology-cohort design with a defensible endpoint |

### 3.1 Which limit is worth watching

The single most consequential of the movable limits is B2. Direct mass-spectrometry evidence that a
fusion-junction peptide is presented at measurable abundance on a common allele, in any fusion-driven
tumour, would convert the central question of this route from a prediction into an empirical one. The
coverage instrument used here is disclosed as failing for exactly that reason: it computes an eligibility
fraction for an epitope whose presentation is unestablished. No date is offered for that arrival, or for
any other in this section. An earlier version of this paper carried a table of optimistic, expected and
conservative years for four such capabilities; it is withdrawn, because a forecast a reader cannot check
does not become checkable by being tabulated, and Section 6 does the work it was there for by saying what
each arrival would and would not look like.

### B1. Predicted class I coverage is low, and it is a property of the screen

**Proposition.** On the panels and thresholds screened here, fewer than a third of patients carry an
allele predicted to present any junction peptide — and that fraction is set by the screen at least as
much as by the tumour.

**Evidence.** The 34-allele screen finds 4 presenting alleles and a union coverage of 30.4%; the
ten-allele screen finds 3 and 27.4%. Both figures rest on five strong peptide-allele calls clustered
between presentation percentiles 0.3736 and 0.4986 against a cut at 0.5, one call per presenting allele.
Section 2.3 gives the sensitivity: 0.45 leaves 23.2%, 0.40 leaves 8.5%, 0.37 leaves nothing.

**What would clear or move it.** Three things, in ascending cost. First, the panels are 10 and 34 alleles
and class I only; extending to the full set for which validated predictors exist would raise the
denominator and is a computational task. Second, the acceptance threshold is a convention rather than a
result, and no analysis in this repository defends 0.5 against 0.4 or 0.6; establishing what the cut
should be for junction peptides would do more to this figure than any panel extension. Third, measured
immunopeptidomics (B2) could either promote peptides the predictor ranks weakly or remove ones it ranks
strongly, and the direction is not knowable in advance. The class II arm (B4) bounds nothing above and so
cannot move this figure in either direction on present evidence.

**What would not move it.** Manufacturing improvements, delivery formulation and adjuvant selection
change nothing here. This limit is about which patients have a target at all.

**Residual.** Some fraction of patients will have no presented junction peptide and no second antigen to
substitute. That fraction is a real and permanent exclusion from this approach, and it should be stated
in any protocol rather than discovered at screening.

### B2. Predicted rather than measured presentation

**Proposition.** No junction peptide has been shown to be presented on the surface of an EMC cell.

**Evidence.** All binding figures in Section 2 come from MHCflurry 2.0, a sequence-based predictor [2].
No EMC immunopeptidomic dataset is known to the author, and the repository contains none.

**What would clear it.** Mass-spectrometry immunopeptidomics on EMC tumour tissue or on one of the
patient-derived EMC cell lines that have been established and characterised [6]. A single positive
identification of a junction-spanning peptide in an EMC eluate would convert the central premise of this
route from predicted to observed. A negative result across adequate material would be close to decisive
against the route, which is what makes this the highest-value single experiment in the ledger.

**Cost and owner.** Requires tissue and a proteomics facility. It is not computational and cannot be
performed by this programme.

### B3. Self-adjacency and central tolerance

**Proposition.** The junction peptide is mostly self sequence with one or two novel residues at the seam,
so the T-cell repertoire capable of recognising it may have been deleted or anergised.

**Evidence.** At the *EWSR1* exon 7 junction the seam carries a single novel codon formed from one leftover
*EWSR1* nucleotide and two retained acceptor 5' untranslated nucleotides, after which *NR4A3* methionine 1
follows as an internal residue. The remainder of each peptide is parental sequence. Whether one altered
residue is sufficient to break tolerance is not answerable by binding prediction.

**What would clear or narrow it.** Two computational filters were specified for this route and never
built: a distance-to-self and tolerance filter, and an analysis of whether the novel residues fall at
anchor positions, which affect binding, or at positions contacting the T-cell receptor, which affect
recognition. A peptide whose only novelty is at an anchor may bind differently from self without looking
different to a T cell, which is the failure mode that matters here. Both filters are computational and
neither has been run. Beyond that, only a T-cell reactivity assay against the specific peptide-HLA
complex answers the question.

**Comparator.** This limit is where EMC differs most sharply from the melanoma setting, in which
selected neoantigens frequently arise from point mutations in a repertoire that has not been tolerised
against them and in a tumour already under immune pressure.

### B4. No strong CD4 epitope on the three alleles tested, which bounds very little

**Proposition.** An effective vaccine generally requires CD4 helper epitopes, and the corrected junction
supplies no strong class II binder on the three alleles screened. That is a statement about the screen,
and it is reported here as one.

**History.** The committed class II demonstration was previously built on the superseded coordinate system
and sat on a seam disjoint from the class I set, so the arm and every combined CD8 and CD4 figure were
withheld. The cause was that the per-patient junction builder shared by the class I and class II scripts
concatenated coding sequences rather than working on the transcript, so regenerating its inputs could not
repair it. The builder has been moved to the transcript model and the arm has been regenerated.

**Result.** With the class II and class I arms now certified to sit on the same seam, the arm can be
reported. At the corrected *EWSR1* exon 7 junction, 15 candidate 15-mers were screened with MHCnuggets
[12] against DRB1\*15:01, DRB1\*03:01 and DRB1\*07:01, calling a peptide a binder below 1000 nM and strong
below 100 nM. Two peptides bind and none is strong: YSQQSSSYGQQNMPC at 262 nM and QYSQQSSSYGQQNMP at 439
nM, both on DRB1\*07:01. The superseded version on the retracted seam reported 9 binders of which 4 were
strong. The correction weakened this arm as it weakened the class I arm.

**What that result does and does not bound.** Four things limit it, and together they leave it bounding
almost nothing above. The 15 candidates are single-residue-offset windows over one seam, so they share 14
of 15 residues with their neighbours and the number of independent peptides tested is close to one rather
than fifteen. Two of the three alleles produced nothing within an order of magnitude of a threshold — the
best call on DRB1\*15:01 is 3,061 nM and on DRB1\*03:01 is 13,585 nM — so the panel is effectively one
allele wide. Zero strong binders on three alleles bounds the per-allele probability of a strong binder at
63% from above, and no lower, by the exact one-sided 95% interval. And the 100 nM cut used for "strong" is
a class I convention; the conventional class II binder band is 500 to 1000 nM, inside which 262 nM sits
comfortably. The negative is real as a description of what this screen returned, and it is not evidence
that the junction supplies no helper epitope.

**What would clear or move it.** The panel is three alleles, which is narrow, and class II presentation is
substantially harder to predict than class I; a wider DR, DP and DQ panel is a computational task and may
change the picture. Beyond that, only measured class II presentation settles it. A construct can also
supply help from a heterologous source rather than from the junction itself, which is standard practice in
peptide vaccine design and would make this limit a design constraint rather than a blocking one.

**Consequence for the construct, and for the combined figure.** Two things follow directly. The candidate
construct regenerated at the corrected junction carries two strong class I epitopes, NMPCVQAQY and
QQNMPCVQAQY, both on HLA-B\*15:01, and no class II epitope at all; its minimal synthetic long peptide is
11 residues where the retracted-seam version was 27 residues carrying both arms. And the combined CD8 and
CD4 coverage figure is **not computed**, which is different from being zero. The coverage instrument
defines class II coverage over the alleles presenting a strong class II binder; with none, its class II
branch never evaluates and the field it writes is empty. That empty field records that the quantity was
not computed, and the instrument's own note describes the class II coverage it would compute as a floor
over a tested panel that untested alleles could only raise. Reporting it as a null result would be
reading an absent value as a measured zero.

**Status.** Reported rather than withheld, negative on the three alleles tested, and bounding the general
availability of helper epitopes at this junction hardly at all.

### B5. Four peptides occur in an *NR4A3* isoform

**Proposition, as originally stated.** The junction peptides had been tested for novelty against two
proteins rather than against the proteome, so their absence from normal human proteins was not established.

**Result.** All 174 distinct junction peptides were searched by exact substring against the UniProt
reviewed human proteome, isoform sequences included. 170 are absent from every reviewed human protein. All
4 strong binders survive, including the *EWSR1* exon 7 lead NMPCVQAQY. The limit is largely cleared, and
the sequence-level novelty premise of this route holds for the great majority of the peptide set.

**The four that do not, and which junctions they belong to.** DMPCVQAQ, DMPCVQAQY, DMPCVQAQYS and
DMPCVQAQYSP all occur in Q92570-3, an isoform of *NR4A3* itself. One of them, DMPCVQAQY, is a predicted
binder on HLA-B\*35:01 at 369.1 nM. Those four peptides are not tumour-exclusive, and DMPCVQAQY is
withdrawn as a candidate.

The pattern is not random across the junction set. All four belong to the same four junctions, *EWSR1*
exons 9, 10, 12 and 13, which are the four whose seam codon is aspartate; the *EWSR1* exon 7 junction has
an asparagine seam codon and none of its peptides collides. So four of the five in-frame junctions share a
seam whose most seam-proximal peptides reproduce a normal *NR4A3* isoform sequence, and the one junction
that is clean is the commonly reported public one that carries the lead binder. Within the affected
junctions the collision is confined to peptides that begin at the seam residue, which are the peptides
with the least donor content; those extending further into *EWSR1*, including the strong binder
RGDMPCVQAQY, remain novel. The consequence for design is specific rather than general: for the
aspartate-seam junctions, a construct should not rely on the seam-proximal window.

**The methodological finding.** The upstream novelty filter compares each candidate against the canonical
parent proteins only, so an isoform that carries the seam sequence passes it unseen. That is a defect in
the filter rather than in these particular junctions, and it will recur for any breakpoint whose seam
residue reconstructs an isoform boundary. The proteome search reports this condition explicitly rather
than silently discarding the hits. The filter should be made isoform-aware.

**What a clean result does not license.** A peptide absent from every reviewed human protein is not thereby
safe. A T-cell receptor engages a peptide-MHC surface rather than a sequence, so a peptide differing from a
self peptide at a position that does not contact the receptor can still be cross-recognised. Unreviewed
sequences were not searched: a hit among predicted-and-unreviewed entries is not evidence that a normal
protein carries the peptide, and a miss there is not evidence of absence. This test
excludes one specific failure mode and leaves the others standing.

### B6. Immunologically cold microenvironment

**Proposition.** EMC has a low mutational burden and a sparse infiltrate, so there is little pre-existing
antigen-specific response for an intervention to amplify.

**Evidence, and an observation about this programme's own grading.** This proposition is the basis on
which this programme set most immune-modulating classes aside for this disease in its route ledger, a
committed record of forty candidate modalities with a stated verdict and reason for each. The reasons are
quoted here from that ledger, and they are this author's own prior notes rather than positions taken in
the literature. Innate agonists of the STING, TLR and RIG-I classes were excluded there on the ground that
such agonism "supplies the danger signal and the priming context; it does not supply antigens, and a
genome as quiet as EMC's is short of antigens rather than short of priming". In-situ vaccination was
excluded on the ground that it "releases and adjuvants the antigens the tumour already has", so that
"releasing more of nothing does not help". Checkpoint inhibitors beyond PD-1, costimulatory agonists,
adenosine-axis inhibitors and regulatory T-cell depletion were each excluded for acting on a response
presumed absent.

Each of those exclusions is an argument about antigen supply, and a vaccine is an antigen supply, so none
of them is an argument against the classes in a configuration where the antigen is supplied exogenously.
That much is a straightforward observation about the ledger's own reasoning, and it is the reason the
combination in Section 4 was never graded here as a unit.

The symmetry is not exact, and an earlier version of this paper asserted that it was. The vaccine was not
parked in that ledger for want of priming: its entry is on the board rather than excluded, and its stated
reason for being parked is immunogenicity, "which its own record states is not a computational question".
The standing blocker recorded against it names two things — that EMC is antigen-cold, and that the fusion
junction is a weak peptide-HLA — and the second is an objection on the antigen side that no
priming-directed partner answers. So the correct statement is the weaker one: a partner supplies what
several exclusions said was missing, and it does not supply what the vaccine's own blocker says is
missing.

**What would clear it.** Clinical evaluation of a vaccine together with an agent that supplies priming or
releases inhibition. Section 4 sets out the specific backbone for which EMC evidence already exists.

### B7. Physical exclusion by the myxoid matrix

**Proposition.** EMC is immune-excluded by a dense chondroitin-sulfate gel, which is a physical barrier
rather than a signalling programme.

**Evidence.** The myxoid matrix is the disease's defining histological compartment. The oncofetal
chondroitin sulfate pathway is the mechanism proposed for it here by analogy: the glycosaminoglycan
biosynthesis genes of that pathway are differentially expressed and correlated with immune response in
placenta and colorectal cancer [8], which is the tissue setting that study examined. No EMC-specific
expression evidence for the pathway is cited, because none is known to the author, and the inference from
those tissues to this one is the author's. Transforming growth factor beta inhibition, which is the standard proposal for
immune-excluded tumours, was set aside for EMC precisely on the ground that the exclusion here is
physical rather than driven by a fibroblast programme.

**Why this limit is distinct from B6.** A cold tumour lacks a response. An excluded tumour may have a
response that cannot reach the target. These require different interventions, and an intervention aimed at
one does not address the other. A vaccine can raise the circulating frequency of junction-specific T cells
without changing whether those cells can enter the tumour.

**What would clear or mitigate it.** Vascular normalisation is the mechanism with the most direct EMC
evidence, discussed in Section 4. Matrix-directed approaches, including addressing the oncofetal
chondroitin sulfate modification itself, are registered in this programme as candidates and are not
resolved.

### B8. Absent EMC immune-profiling data

**Proposition.** The characterisations of EMC as cold and as excluded are inferred from the disease's
mutational burden, its histology and sarcoma-wide immunotherapy experience, rather than from published
EMC-specific immune profiling.

**Consequence.** Several exclusions above rest on an assumption that has not been measured in this
disease. The absence of a reading is not a reading of absence, and it is possible that EMC is less cold
than assumed, or excluded in a manner that suggests a specific intervention.

**What would clear it.** Infiltrate quantification, HLA class I expression status and antigen-presentation
machinery assessment on a series of EMC specimens. HLA class I loss would independently disable every
antigen-directed route including this one, and is not known for this disease.

**Cost and owner.** Requires tissue. This is the cheapest tissue-based item in the ledger and the one that
most efficiently informs the others.

### B9. Manufacturing economics at this incidence

**Proposition.** An individualised vaccine requires per-patient sequencing, design and manufacture, and
EMC's incidence is well under one per million per year.

**Consequence.** No independent programme can supply the manufacturing, and the economics that support an
individualised product in melanoma do not obviously extend to a disease with this incidence.

**What would mitigate it.** Two features of this target reduce the requirement relative to a general
individualised product. First, the antigen is not discovered per patient by tumour sequencing but is
determined by which exon pair the patient carries, of which five are in frame; the design space is
therefore small, enumerable in advance, and shared across patients with the same breakpoint. Second,
because the fusion is truncal, the antigen does not need re-selection over the disease course. A small
fixed panel of breakpoint-specific constructs, allocated by a diagnostic assay, is closer to a stratified
product than to a bespoke one. Whether that is commercially tractable is a question for a platform holder
and not one this analysis can answer.

### B10. Trial design below the randomisation threshold

**Proposition.** At this incidence a conventional randomised trial of a vaccine addition is not feasible.

**Evidence and mitigation.** A histology-specific EMC cohort within a sarcoma master protocol has already
been executed and reported for a different regimen, enrolling 24 patients across nine centres in three
countries over four years [5]. That shows the vehicle exists, and it gives an accrual rate of about six
unselected patients a year across nine centres.

**And that rate does not survive this paper's own eligibility filter.** A junction-vaccine cohort cannot
enrol unselected EMC. It needs a patient carrying *EWSR1*::*NR4A3*, which is 62 to 75% of cases [7], and
then an HLA type that presents a junction peptide, which on the panels screened here is 8.5 to 30.4% of
those (B1). Multiplying the same trial's own accrual by those two fractions gives roughly 0.3 to 1.4
eligible patients a year, so a 24-patient cohort of the size already run would take on the order of two
decades and a cohort powered to detect a difference in six-month progression-free survival would take
substantially longer than that. This is the arithmetic that makes B10 a limit of the disease rather than
of study design, and no adaptive or master-protocol vehicle changes it: the vehicle exists, and the
patients to put in it do not arrive fast enough. The endpoint question is separate: response-based
endpoints behave poorly in indolent tumours, and progression-free survival at a fixed time point is the
measure the existing EMC cohort reported.

## 4. An ungraded combination

The limits above do not resolve independently. B6 and B7 are properties of the tumour that a vaccine
cannot address, and B1 and B3 are properties of the antigen that a checkpoint inhibitor cannot address.
The relevant question is therefore not whether a junction vaccine works in EMC, which is the question that
was asked and answered negatively, but whether a junction vaccine adds anything to a backbone that
already has EMC-specific activity.

Such a backbone exists. A phase 2 histology-specific EMC cohort within the IMMUNOSARC II master protocol
evaluated sunitinib with nivolumab in adults with advanced, progressing, centrally confirmed EMC across
nine centres in Spain, Italy and the United Kingdom. Of 23 evaluable patients, 16 were progression-free at
6 months, median progression-free survival was 13.2 months (95% CI 5.7 to 20.7), and there were 2 partial
responses [5]. This is a conference abstract and has not been peer-reviewed; the full publication is not
available, and no results are posted for the registration. It is reported here as the most direct
EMC-specific evidence available for an immunotherapy-containing regimen, and not as evidence of efficacy.
The preceding mixed-histology phase Ib/II study of the same combination is published [4].

Three features make this backbone the natural context for the vaccine question rather than an unrelated
route. The antiangiogenic component addresses B7 by a mechanism, in that vascular normalisation reduces
the physical and vascular barriers to lymphocyte entry, and antiangiogenic tyrosine kinase inhibitors
carry the most consistent prospective signal reported in this disease: pazopanib gave an objective
response in 4 of 22 evaluable patients with a median progression-free survival of about 19 months in a
single-arm phase 2 trial [11], and a sunitinib series reported activity in translocated EMC [13]. The
checkpoint component addresses the release arm of B6. Neither addresses antigen supply, which is what the
vaccine would contribute. The three components are complementary rather than redundant, and each covers a
limit the others do not.

This is also the architecture used in the melanoma programme behind the recent phase 3 announcement: the
individualised vaccine is given with pembrolizumab, never alone [3,9]. The transfer from melanoma to EMC
fails on antigen depth, because melanoma supplies a pool of private neoantigens from which a construct is
assembled per patient, while EMC supplies one junction. It does not fail on architecture.

**What this section is claiming, and what it is not.** The proposition is that the addition of a
breakpoint-matched junction construct to a checkpoint and antiangiogenic backbone is a combination in
which each component covers a limit the others do not, and that it has not been evaluated or graded as a
unit — including in this programme's own ledger, which is where the observation in B6 comes from. It is
not a trial proposal, and this paper does not offer one: no population, comparator, endpoint, effect size
or sample size is specified anywhere here, a single-arm addition to a backbone whose own six-month
progression-free rate is 16 of 23 could not attribute an effect to the vaccine, and B10's arithmetic says
the eligible patients to run such a study do not arrive at a workable rate. Whether the combination merits
evaluation at all turns on B2, and so on whether measured presentation ever arrives; Section 5 gives what
that arrival would change. Nothing in this section is a recommendation that any patient receive any of
these agents, alone or together, outside a clinical trial.

## 5. What could be improved now, and what is waiting

Four items on this list need nothing but public data and would sharpen numbers this paper reports as
provisional: the distance-to-self and anchor-versus-contact-position filters specified for this route and
never implemented, which bear directly on B3; extension of the 10- and 34-allele class I panels and the
three-allele DR panel to the full set for which validated predictors exist; a defended acceptance
threshold for junction peptides, without which B1's figures remain as sensitive to the cut as Section 2.3
shows them to be; and the isoform-aware novelty filter identified in B5. None requires permission,
material or funding.

Everything else waits. Measured presentation (B2) would change the character of this route rather than its
score, because the screen in Section 2 would stop being a stand-in and become a hypothesis with a
calibrating dataset. A deposited EMC expression or proteomics series would settle B8, which is the
cheapest item that informs the most others, since infiltrate density and HLA class I expression status
bear on every antigen-directed route in this disease. Access to a patient-derived line would additionally
make B2 executable rather than merely specified; these are separate arrivals and neither implies the
other. B6 and B7 are properties of the tumour that no computational advance addresses at all.

## 6. Distinguishing a real advance from an apparent one

A paper that names the capabilities it waits on incurs an obligation to say what would look like those
capabilities arriving without being them. Each of the following has a plausible near-miss, and in each case
the near-miss would be reported in the literature in language that resembles a hit.

**A result on a different fusion is not a result on this one.** A presentation or immunogenicity study on
another fusion-driven tumour raises the prior that fusion junctions in general can be seen by T cells. It
does not establish that this junction, on these alleles, is presented at usable abundance. General advances
in neoantigen prediction have repeatedly not transferred to this target, which is why the coverage
instrument here is disclosed as failing rather than quietly retired. The discriminating question to ask of
any such report is whether its evidence concerns presentation, abundance, or only a different fusion.

**Robotic execution is not material access.** A cloud laboratory offering per-experiment pricing for
cell-based assays supplies robots and generic reagents. It does not supply an EMC line or organoid, and
without that, none of the tissue-gated items in Section 3 become runnable.

**A better predictor is not a measurement.** An improved class I or class II model would change the numbers
in Section 2, and it would leave B2 exactly where it is. The limit there is that nobody has looked, not
that the looking-glass is imprecise.

**A larger allele panel raises a ceiling without changing a floor.** Extending the panels, as Section 5
proposes, can only move the coverage figures upward, and a higher ceiling on predicted presentation is not
evidence that any patient's tumour presents anything.

### 6.1 Conditions for revision

Four statements in this paper are falsifiable by an observation a reader could go and make, and they are
listed so a future reader can check them rather than re-derive them. Sequence-level novelty for 170 of 174
peptides would be overturned by a proteome release adding a protein that contains one of the four strong
binders. Every coverage figure would move upward if a wider panel added a presenting allele and downward
if measured presentation removed one of the strong calls, and all of them go to zero if the acceptance
threshold is set below 0.37. The class II statement would be changed by a wider DR, DP and DQ panel, which
is the single most likely source of a change to it. And the argument in Section 4 would be closed
altogether by an EMC immune-profiling series showing HLA class I loss, which would end every
antigen-directed route in this disease including this one.

## 7. Limitations

All binding figures are predictions from sequence-based models and no EMC-specific validation of either
model exists. Population coverage is computed from reference allele frequencies by multiplying
non-carrier frequencies across alleles, which assumes independence not only between loci but between
alleles at the same locus; two of the alleles pooled here are both HLA-B, and handling that correctly
moves the pooled figure by about 0.3 percentage points. The population-to-region mapping is an
approximation, the regional figures are point values on samples as small as 579 individuals, and the
frequencies themselves are pooled across populations whose allele frequencies differ by more than the
figures being reported. The IMMUNOSARC II EMC
cohort result is a conference abstract, single-arm, and not peer-reviewed, and it evaluates a combination
in which the component with the larger independent EMC evidence base is the tyrosine kinase inhibitor
rather than the checkpoint inhibitor; it is cited here to establish that a vehicle and a backbone exist,
not to attribute activity to the immune arm. The characterisations of EMC as cold and as immune-excluded
rest on inference rather than on published EMC-specific immune profiling, which is itself recorded as
limit B8. The class II panel comprises three DR alleles and no DP or DQ alleles, so its negative result
bounds a narrow question rather than the general availability of helper epitopes. No claim is made
that any peptide is presented, that any construct would be immunogenic, that any combination would be safe
or effective, or that any of this is ready for clinical use. No wet-laboratory work was performed for this
paper, and the measurements this characterisation most needs require work this programme cannot carry out.

Two further limits are properties of this paper rather than of its subject. The binder counts and every
coverage figure derived from them depend on an acceptance threshold that no analysis here defends, and
Section 2.3 shows that a 0.13-unit move in it takes the headline figure to zero; nothing in this paper
should be read as though those figures were threshold-independent. And no multiplicity correction is
applied anywhere: 174 peptides were screened against 10 and then 34 alleles at two thresholds, with no
decoy control and no null expectation computed, so the small number of calls that pass is reported as
what the screen returned rather than as an enrichment over chance.

## 8. Reproducibility

Every figure in Sections 2 and 3 is generated by a script in `research/modalities/` and is committed as a
JSON artifact beside it: `fusion_breakpoints.py` for the junction set and predicted binders,
`hla_coverage.py` for population coverage, `coverage_scan.py` for the broad-panel screen and curve,
`junction_proteome_novelty.py` for the proteome search of Section B5, `patient_neoepitopes.py` and
`patient_cd4_epitopes.py` for the per-patient shortlisters, and `vaccine_construct.py` for the candidate
construct and its minimal synthetic long peptide. The corresponding artifacts are
`fusion-breakpoint-neoantigens.json`, `hla-coverage.json`, `coverage-curve.json`,
`epitope-allele-matrix.json`, `junction-proteome-novelty.json`, `patient-cd4-demo.json` and
`vaccine-construct.json`. The predictor versions those artifacts record are MHCflurry 2.1.4 with models
release 2.2.0 for class I and MHCnuggets for class II.

⚠ **These are not regenerated on every commit, and this paper does not claim they are.** The workflow that
runs them is dispatched by hand, its steps do not fail the run when a generator fails, and it writes its
outputs to a separate cache branch from which they are copied in. So the artifacts in the repository are
the record of a run that happened, verifiable by their embedded timestamps and input hashes, rather than
the output of continuous re-execution. An earlier version of this section said they were regenerated in
continuous integration; that was not true of any branch a reader would fetch.

Clinical figures are quoted from the curated EMC registry at `research/data/emc-clinical-registry.json`,
which carries a structured citation entry for every source and a retrieval note for those whose
identification required one.

## 9. Declarations

**Use of AI tools.** A large language model (Claude, Anthropic) was used throughout this work: to write
the analysis code, to run the screening pipelines, to draft and revise this manuscript, and to conduct
the internal adversarial review of earlier drafts whose findings this version incorporates. The model
versions used over the span of the work are the ones the repository's commit record names, and are not
restated here. No quantitative result was generated by a language model directly: every figure in
Sections 2 and 3 is produced by the code named in Section 8 and is reproducible from the committed
artifacts, and the clinical figures are transcribed from the publications cited for them. Every literature
identifier in Section 10 was checked against a retrieved bibliographic record held in this repository, and
any identifier that could not be so anchored was removed rather than retained. The author takes full
responsibility for all content, including for the correctness of the code and for the interpretation of
the results.

**Data and code availability.** All code and all artifacts underlying every figure are in the public
repository that accompanies this manuscript, under the paths given in Section 8. No restricted data were
used.

**Competing interests.** The author declares no financial competing interests: he holds no position,
equity, consultancy or patent relating to any gene, sequence, peptide or agent named here. One
non-financial interest is declared: the author is a survivor of extraskeletal myxoid chondrosarcoma, the
disease this work addresses.

**Funding.** This work received no external funding and was self-funded by the author. No funder had any
role in the analyses, the interpretation of the results, or the decision to publish.

**Ethics.** No human subjects, human material or animals were involved. No patient data were used; the
clinical figures quoted are published or publicly presented aggregate results.

**Not clinical guidance.** Nothing in this manuscript is medical advice, and nothing in it is evidence
that any agent or combination is safe or effective in extraskeletal myxoid chondrosarcoma. No peptide
reported here has been synthesised, formulated, or tested in any cell, tissue or animal by anyone, and
none may be administered to any person. The agents named in Section 4 are discussed as a research
hypothesis and their use outside a clinical trial is not supported by anything in this paper.

## 10. References

Verified pool, anchored in this repository's citation records:

1. Gonzalez-Galarza FF, et al. Allele Frequency Net Database (AFND) 2020 update. *Nucleic Acids Research*
   2020. Accessed via the MIT-licensed `slowkow/allelefrequencies` mirror.
2. O'Donnell TJ, Rubinsteyn A, Laserson U. MHCflurry 2.0: improved pan-allele prediction of MHC class
   I-presented peptides. *Cell Systems* 2020. doi:10.1016/j.cels.2020.09.001.
3. Weber JS, Carlino MS, Khattak A, Meniawy T, Ansstas G, Taylor MH, et al. Individualised neoantigen
   therapy mRNA-4157 (V940) plus pembrolizumab versus pembrolizumab monotherapy in resected melanoma
   (KEYNOTE-942): a randomised, phase 2b study. *Lancet* 2024;403(10427):632-644.
   doi:10.1016/S0140-6736(23)02268-7. PMID 38246194.
4. Martin-Broto J, Hindi N, Grignani G, Martinez-Trufero J, Redondo A, Valverde C, et al. Nivolumab and
   sunitinib combination in advanced soft tissue sarcomas: a multicenter, single-arm, phase Ib/II trial.
   *Journal for ImmunoTherapy of Cancer* 2020. doi:10.1136/jitc-2020-001561. PMID 33203665.
5. Hindi N, Palmerini E, Carrasco-Garcia I, Gonzalez-Billalabeitia E, Valverde C, Strauss SJ, et al.
   Phase II of sunitinib plus nivolumab in extraskeletal myxoid chondrosarcoma: results from the GEIS,
   ISG and UCL IMMUNOSARC II study. *Journal of Clinical Oncology* 2025;43(16_suppl):11513.
   doi:10.1200/JCO.2025.43.16_suppl.11513. Conference abstract; registration NCT03277924.
6. Establishment and characterization of patient-derived EMC cell lines. *Human Cell* 2025.
   PMID 40580361; and *Human Cell* 2023, PMID 36316541.
7. From pathogenesis to the patient's bedside: a comprehensive review of extraskeletal myxoid
   chondrosarcoma. *Journal of Cancer Research and Clinical Oncology* 2025. PMID 41055792.
8. Glycogenes in oncofetal chondroitin sulfate biosynthesis are differently expressed and correlated with
   disease outcome. *Frontiers in Cell and Developmental Biology* 2021. PMID 34966741.

Cited as a company announcement rather than as peer-reviewed literature:

9. Merck and Moderna announce phase 3 INTerpath-001 trial of intismeran autogene plus KEYTRUDA met
   endpoints of recurrence-free survival and distant metastasis-free survival in patients with completely
   resected stage IIB-IV melanoma. Press release, 2026. Effect sizes for the phase 3 result were not
   disclosed in the announcement and none are quoted here.

Requiring verification before submission:

10. The population-coverage formula (Bui et al., 2006) and the Wilson interval (Wilson, 1927) as applied
    in the coverage analysis. [citation to verify]
11. EMC sensitivity to antiangiogenic tyrosine kinase inhibitors as a general clinical characterisation.
    [citation to verify] against the clinical registry's antiangiogenic records.

## Appendix A. Superseded figures

The following values were reported before the 2026-08-07 coordinate-system correction and must not be
quoted. They are retained so that earlier drafts and derived documents can be identified.

| Quantity | Superseded value | Current value |
|---|---|---|
| In-frame junctions | 7 | 5 |
| Distinct predicted binders | 26 | 11 |
| *EWSR1* exon 7 junction, presenting alleles | A\*11:01 and B\*08:01 | B\*15:01 alone |
| *EWSR1* exon 7 junction coverage | 29.7% | 8.51% |
| Any-strong-binder coverage | 58.0% | 27.4% |
| Regional range | 36% to 79% | 1.4% to 60% |
| Broad-panel presenting alleles | 20 of 34 | 4 of 34 |
| Broad-panel coverage ceiling | 84.5% | 30.4% |
| Combined CD8 and CD4 coverage | 16.5% | null, no strong class II binder |
| Candidate minimal synthetic long peptide | 27 residues, both arms | 11 residues, class I only |
| Class II predicted binders at the *EWSR1* exon 7 junction | 9, of which 4 strong | 2, of which 0 strong |

The superseded values arose from a model that concatenated coding sequences and thereby discarded the
acceptor exon's retained 5' untranslated region. The corrected junction set is disjoint from the
superseded one, so the earlier peptide identifiers do not appear in the current artifacts.
