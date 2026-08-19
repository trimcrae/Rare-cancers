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

*Preprint draft, 2026-08. Author: [Name], independent researcher, [City, Country]. Independent,
personal-capacity work, unconnected to the author's employer; prepared with AI assistance (Section 9).
Review by a sarcoma medical oncologist and a tumour immunologist is recommended before circulation.*

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
exon is retained whole including its 5' untranslated region, and class I binding was predicted with
MHCflurry 2.0. Population coverage was computed from Allele Frequency Net Database frequencies using the
standard population-coverage formula with Wilson intervals. Peptide novelty was assessed by exact-match
search against the reviewed human proteome including isoform sequences. Clinical evidence was drawn from a
curated EMC registry with structured citation provenance. No new wet-laboratory data were generated.

**What can be established today.** Of 27 declared exon pairs, 5 are in frame and yield 11 distinct
predicted binders, of which 4 are strong; there is no pan-EMC epitope. Class I population coverage is 8.51%
(95% CI 8.26 to 8.76) for the commonly reported *EWSR1* exon 7 to *NR4A3* exon 3 junction, presented on
HLA-B\*15:01 alone, and 27.4% (95% CI 26.6 to 28.1) pooling all strong-binder alleles; against a broad
34-allele panel the ceiling is 30.4% and the coverage curve never reaches 50%. 170 of 174 junction peptides
are absent from the reviewed human proteome including isoforms, and all 4 strong binders survive that
search. The 4 that do not all occur in an *NR4A3* isoform and all belong to the four junctions whose seam
codon is aspartate; one is a predicted binder and is withdrawn. The class II arm yields 2 predicted binders
and no strong binder on a three-allele DR panel, so the combined CD8 and CD4 figure is null rather than
unreported, and the candidate construct is 11 residues carrying class I epitopes only. A
histology-specific EMC cohort of sunitinib plus nivolumab reported 16 of 23 evaluable patients
progression-free at 6 months with median progression-free survival of 13.2 months.

**What bounds each conclusion.** Of ten limits enumerated, three are properties of this tumour and this
junction and will not move: antigen depth, the physical myxoid barrier, and disease incidence. Four are
limits of current instruments: sequence-based binding prediction standing in for measured presentation,
class II prediction on a narrow allele panel, a novelty filter that reads canonical proteins only, and the
absence of any fusion-junction-validated presentation model. Three are limits of access rather than of
knowledge: no EMC immune profiling, no reachable patient-derived material, and no manufacturing route at
this incidence. Each instrument and access limit is paired with the specific advance that would move it and
a dated expectation band drawn from a maintained capability watch.

**Interpretation.** The most defensible present statement is neither that the route is viable nor that it
is closed, but that it is instrument-limited in identifiable ways. The one substantive reasoning correction
this work offers is that priming-directed classes were excluded for this disease on the grounds that a
quiet genome supplies too few antigens, while the junction vaccine was set aside on the grounds that a cold
tumour supplies too little priming. Each was excluded for lacking what the other provides, and the
combination has never been evaluated as a unit. Predicted binding is a screen and not evidence of
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

For every limit in the second and third groups, Section 3 records the specific advance that would move it,
what evidence would count as that advance actually arriving, and a dated expectation band. The bands come
from a maintained capability watch that this programme keeps for its whole route portfolio and reviews on a
schedule, so they are the same bands used to sequence unrelated work rather than estimates produced to
support this paper. They are explicitly uncertain, and each carries its own confidence.

Section 6 does the part that most capability-watching gets wrong: it states, for each watched advance, what
would look like that advance arriving without being it. A result on a different fusion, a cloud laboratory
that supplies robots but not the cell line, and a general improvement in neoantigen prediction have each
been mistaken for the specific capability this route waits on.

The immediate occasion is external. A randomised phase 3 trial of an individualised neoantigen therapy
combined with pembrolizumab has reported meeting its primary endpoint of recurrence-free survival in
resected stage IIB to IV melanoma, following the phase 2b result in the same setting [3]. That result does
not transfer to EMC, and Section 4 sets out the axis on which the transfer fails. It does show that the
manufacturing, regulatory and delivery apparatus for an individualised RNA vaccine exists as a clinical
reality rather than as a proposal, which lowers the cost of several limits below.

## 2. The target and its current evidence base

### 2.1 Disease and fusion

EMC accounts for roughly 1 to 3% of soft-tissue sarcomas, with an estimated incidence well under one per
million per year [7]. It is defined by rearrangement of *NR4A3* on chromosome 9q22. *EWSR1*::*NR4A3* is
the commonest fusion, reported in approximately 62 to 75% of cases and in 79% of one molecularly
confirmed series of 58 cases; variant partners include *TAF15*, *TCF12*, *TFG* and *FUS* [7]. The genome
is otherwise quiet, and the fusion is the truncal driver.

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

Of 27 declared exon pairs, 5 are in frame: *EWSR1* exons 7, 9, 10, 12 and 13 joined to *NR4A3* exon 3.
These yield 11 distinct predicted binders, 4 of them strong, and 174 distinct junction-spanning peptides
in total. The lead candidate at the commonly reported *EWSR1* exon 7 junction is NMPCVQAQY on HLA-B\*15:01,
at 73.4 nM with a presentation percentile of 0.37. There is no pan-EMC epitope: the most widely shared
candidate appears in 4 of the 5 junctions and is a weak binder, three of the five junctions return no
strong binder at all, and every strong binder is specific to its breakpoint. One of the 11 predicted
binders, DMPCVQAQY on HLA-B\*35:01, is withdrawn on the proteome search reported under B5 below, leaving
10; all 4 strong binders survive that search.

### 2.3 Population coverage

Class I coverage for the *EWSR1* exon 7 junction is 8.51% (95% CI 8.26 to 8.76), because that junction is
predicted to be presented on HLA-B\*15:01 alone. Pooling every allele that presents a strong binder from
any in-frame junction gives 27.4% (95% CI 26.6 to 28.1). Regional variation is large, from 1.4% in
Melanesia to 60% in Northern Europe.

Because an individualised platform selects against the patient's own genotype rather than against a
public epitope, the more relevant computation screens the junction peptides across a broad allele panel
and asks what fraction of patients carry at least one presenting allele. Against a 34-allele panel, 4
alleles present at least one strong binder, and the greedy coverage curve reaches 30.4% and then stops.
It does not attain 50% at any panel size. The personalised framing therefore raises the ceiling from 8.51%
to 30.4% and does not remove it.

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
| B1 | Class I coverage plateaus near 30% | disease, partly instrument | 8.51% public junction, 27.4% pooled, 30.4% broad-panel ceiling | Wider allele panels; measured presentation reweighting the screen |
| B2 | Presentation predicted, never measured | instrument and access | MHCflurry 2.0 percentiles on 174 peptides | Immunopeptidomics on EMC tissue or a patient-derived line |
| B3 | Self-adjacency and central tolerance | instrument | Seam structure characterised; no tolerance model applied | Distance-to-self and anchor-versus-contact filters; T-cell reactivity assay |
| B4 | No strong CD4 epitope at the corrected junction | instrument | 2 binders, 0 strong, on a three-allele DR panel | Wider DR, DP and DQ panel; measured class II presentation |
| B5 | Seam-proximal peptides of four junctions occur in an *NR4A3* isoform | resolved | 170 of 174 novel proteome-wide; one binder withdrawn | Answered; the upstream filter should become isoform-aware |
| B6 | Immunologically cold microenvironment | disease, addressable in combination | Inferred, not measured in EMC | A vaccine supplies antigen; a checkpoint inhibitor supplies release |
| B7 | Physical exclusion by the myxoid matrix | disease | Inferred from histology and pathway expression | Vascular normalisation; matrix-directed agents |
| B8 | No EMC immune profiling published | access | None; the cold and excluded readings are inferences | A deposited EMC series, or a pan-sarcoma atlas reaching this histology |
| B9 | Manufacturing economics at this incidence | access | Five enumerable in-frame junctions, not per-patient discovery | A platform holder; a master-protocol vehicle |
| B10 | Trial design below the randomisation threshold | disease | A 24-patient histology cohort has been run across nine centres | Adaptive or histology-cohort design with a defensible endpoint |

### 3.1 Dated expectation for the movable limits

The bands below are taken from a maintained capability watch that this programme keeps across its whole
route portfolio and reviews on a schedule. They are drawn from a scenario record rather than composed for
this paper, they carry their own stated confidence, and their basis is marked as extrapolated or
speculative rather than measured. They are offered as an ordering aid and a re-read schedule, not as
predictions to be scored.

| Capability the route waits on | Bears on | Optimistic | Expected | Conservative | Basis |
|---|---|---|---|---|---|
| Presentation or immunogenicity prediction validated on fusion junctions, or a discovery platform reaching low-abundance peptide-HLA | B1, B2, B3 | 2027H2 | 2029 | 2032 | extrapolated |
| A fetchable public EMC expression or proteomics deposit | B8, B2 | 2027 | 2029 | beyond 2031 | speculative |
| Access to patient-derived EMC material, by collaboration or service | B2, B3, B8 | 2027H2 | 2029 | beyond 2031 | speculative |
| A solo-rentable robotic laboratory with cell-based assay scope | execution half of B2 and B3 | 2027H2 | 2029 | beyond 2031 | extrapolated |

The single most consequential of these is the first. Direct mass-spectrometry evidence that a
fusion-junction peptide is presented at measurable abundance on a common allele, in any fusion-driven
tumour, would convert the central question of this route from a prediction into an empirical one. The
programme's own coverage instrument is disclosed as failing for exactly this reason: it computes an
eligibility ceiling for an epitope whose presentation is unestablished.

### B1. Class I coverage plateaus near 30%

**Proposition.** Even under per-patient selection, fewer than a third of patients carry an allele
predicted to present any junction peptide.

**Evidence.** The broad-panel screen finds 4 presenting alleles of 34, a ceiling of 30.4%, and no panel
size that reaches 50%.

**What would clear or move it.** Three things, in ascending cost. First, the panel is 34 alleles and
class I only; extending it to the full set of alleles for which validated predictors exist would raise
the denominator and is a computational task. Second, the class II arm is currently withheld (B4), and CD4
epitopes are presented on a different and more permissive set of molecules, so the combined figure may
differ substantially from the class I figure alone. Third, the screen scores peptides by predicted
presentation percentile; measured immunopeptidomics (B2) could either promote peptides the predictor
ranks weakly or remove ones it ranks strongly, and the direction is not knowable in advance.

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

### B4. No strong CD4 epitope at the corrected junction

**Proposition.** An effective vaccine generally requires CD4 helper epitopes, and the corrected junction
supplies no strong class II binder on the panel tested.

**History.** The committed class II demonstration was previously built on the superseded coordinate system
and sat on a seam disjoint from the class I set, so the arm and every combined CD8 and CD4 figure were
withheld. The cause was that the per-patient junction builder shared by the class I and class II scripts
concatenated coding sequences rather than working on the transcript, so regenerating its inputs could not
repair it. The builder has been moved to the transcript model and the arm has been regenerated.

**Result.** With the class II and class I arms now certified to sit on the same seam, the combined figure
is computable and is null. At the corrected *EWSR1* exon 7 junction, 15 candidate 15-mers yield 2 predicted class II
binders and no strong binder, both on DRB1\*07:01 at 262 nM and 439 nM, against a three-allele DR panel of
DRB1\*15:01, DRB1\*03:01 and DRB1\*07:01. The superseded version on the retracted seam reported 9 binders
of which 4 were strong. The correction weakened this arm as it weakened the class I arm.

**What would clear or move it.** The panel is three alleles, which is narrow, and class II presentation is
substantially harder to predict than class I; a wider DR, DP and DQ panel is a computational task and may
change the picture. Beyond that, only measured class II presentation settles it. A construct can also
supply help from a heterologous source rather than from the junction itself, which is standard practice in
peptide vaccine design and would make this limit a design constraint rather than a blocking one.

**Consequence for the construct, and for the combined figure.** Two things follow directly. The candidate
construct regenerated at the corrected junction now carries two strong class I epitopes, NMPCVQAQY and
QQNMPCVQAQY, both on HLA-B\*15:01, and no class II epitope at all; its minimal synthetic long peptide is
11 residues where the retracted-seam version was 27 residues carrying both arms. And the combined CD8 and
CD4 coverage figure is not a pending computation but a null: class II coverage is defined over the alleles
presenting a strong class II binder, there are none, so the combined figure has no value rather than an
unreported one. That is a result, and the paper reports it as one.

**Status.** No longer withheld. Reported, and negative on the panel tested.

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

**Evidence and the reasoning error.** This proposition is the basis on which most immune-modulating
classes were set aside for this disease, and the specific reasons given are worth quoting because they
turn out to be conditional rather than absolute. Innate agonists of the STING, TLR and RIG-I classes were
excluded on the grounds that such agonism "supplies the danger signal and the priming context; it does not
supply antigens, and a genome as quiet as EMC's is short of antigens rather than short of priming."
In-situ vaccination was excluded on the grounds that it "releases and adjuvants the antigens the tumour
already has," and that "releasing more of nothing does not help." Checkpoint inhibitors beyond PD-1,
costimulatory agonists, adenosine-axis inhibitors and regulatory T-cell depletion were each excluded for
acting on a response that is presumed absent.

Every one of those exclusions is an argument about antigen supply. A vaccine is an antigen supply. The
reasoning that excludes priming-directed classes for this disease is therefore not applicable to a
configuration in which the antigen is supplied exogenously, and the reasoning that parked the vaccine, which
was that priming is absent, is not applicable to a configuration in which a priming-directed agent is
present. The two verdicts were each derived on the assumption that the other component was absent, and no
evaluation of the combination exists.

**What would clear it.** Clinical evaluation of a vaccine together with an agent that supplies priming or
releases inhibition. Section 4 sets out the specific backbone for which EMC evidence already exists.

### B7. Physical exclusion by the myxoid matrix

**Proposition.** EMC is immune-excluded by a dense chondroitin-sulfate gel, which is a physical barrier
rather than a signalling programme.

**Evidence.** The myxoid matrix is the disease's defining histological compartment, and glycosaminoglycan
biosynthesis genes in the oncofetal chondroitin sulfate pathway are differentially expressed in this
tumour class [8]. Transforming growth factor beta inhibition, which is the standard proposal for
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
countries over four years [5]. That shows the vehicle exists and gives a realistic accrual rate. The
endpoint question is separate and is treated at length in a companion analysis in this programme:
response-based endpoints behave poorly in indolent tumours, and progression-free survival at a fixed
time point is the measure the existing EMC cohort reported.

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
the physical and vascular barriers to lymphocyte entry, and EMC is unusually sensitive to antiangiogenic
tyrosine kinase inhibitors, which is its most consistent clinical signal. The checkpoint component
addresses the release arm of B6. Neither addresses antigen supply, which is what the vaccine would
contribute and what B6's own stated exclusion reasoning identifies as the missing element. The three
components are complementary rather than redundant, and each covers a limit the others do not.

This is also the architecture used in the melanoma programme that generated the recent phase 3 result:
the individualised vaccine is given with pembrolizumab, never alone [3]. The transfer from melanoma to EMC
fails on antigen depth, because melanoma supplies a large pool of private neoantigens from which roughly
thirty can be selected against the patient's genotype while EMC supplies one. It does not fail on
architecture. The architectural lesson transfers even though the disease biology does not.

The proposition this paper puts forward is therefore narrow and testable: the addition of a
breakpoint-matched junction construct to a checkpoint and antiangiogenic backbone is a coherent
combination in which each component covers a distinct and enumerated limit, and it has not been
evaluated or graded as a unit. Whether it merits evaluation turns on B2, and so on whether measured
presentation ever arrives; Section 5 gives what that arrival would change and Section 3.1 gives when it
might be expected.

## 5. Present work, and the unlocks each capability arrival brings

The work below is ordered by what it depends on rather than by expected payoff, so that a reader can see
which parts of this characterisation could be improved by anyone today and which are waiting on the field.

**Improvable now, by computation alone.** Two of the limits above yield to work that needs nothing but
public data. The distance-to-self and anchor-versus-contact-position filters specified for this route have
never been implemented, and they bear directly on B3, which is otherwise the least characterised limit in
the ledger. The class I allele panel is 34 and the class II panel is 3, and both can be extended to the
full set for which validated predictors exist, which would replace the present ceilings with better ones in
either direction. The isoform-aware novelty filter identified in B5 is a small change to an existing
instrument. None of this requires permission, material or funding, and all of it sharpens numbers this
paper reports as provisional.

**Improvable on the arrival of measured presentation.** If direct mass-spectrometry evidence appears that a
fusion-junction peptide is presented at measurable abundance on a common allele, in any fusion-driven
tumour, the character of this route changes rather than its score. The screen in Section 2 stops being a
stand-in and becomes a hypothesis with a calibrating dataset; the ceiling in B1 can be recomputed against
measured rather than predicted presentation; and B3 acquires a comparison class. This is the capability
whose band is given first in Section 3.1, and the one this paper would most want a reader to watch.

**Improvable on the arrival of EMC material or EMC data.** A deposited EMC expression or proteomics series
would settle B8 directly, and B8 is the cheapest item that informs the most others: infiltrate density and
HLA class I expression status bear on every antigen-directed route in this disease, not only on this one.
Access to a patient-derived line would additionally make B2 executable rather than merely specified. These
are separate arrivals with separate bands, and neither implies the other.

**Improvable only in combination, and only clinically.** B6 and B7 are properties of the tumour that no
computational advance addresses. What can be said today is the argument in Section 4: the components that
address them exist, have been given together in this disease, and have never been given together with an
antigen supply.

**A distinction worth keeping.** A remote robotic laboratory rentable by the experiment would flip the
execution half of B2 and B3, and this programme watches it for that reason. It would not supply the EMC
cell line. Execution and material are separate gates, and reporting the first as though it cleared the
second is the specific error Section 6 is written to prevent.

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

Stated so that a future reader can check them rather than re-derive them. Sequence-level novelty is
established for 170 of 174 peptides and would be overturned by a proteome release that adds a protein
containing one of the strong binders. The coverage ceiling would move if a wider panel added presenting
alleles, and would move downward if measured presentation removed any of the four strong binders. The
combined CD8 and CD4 figure is null because no strong class II binder survives on three DR alleles, and a
wider class II panel is the single most likely source of a change to that statement. The argument in
Section 4 would be weakened by an EMC immune-profiling series showing HLA class I loss, which would close
every antigen-directed route in this disease including this one, and would be strengthened by any report of
antigen-specific response in an EMC patient on a checkpoint-containing regimen.

## 7. Limitations

All binding figures are predictions from a sequence-based model and no EMC-specific validation of that
model exists. Population coverage is computed from reference allele frequencies with an independence
assumption across loci, and the population-to-region mapping is an approximation. The IMMUNOSARC II EMC
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

The dated bands in Section 3.1 are the weakest material in the paper and should be read as such. Their
basis is marked extrapolated or speculative rather than measured, each carries low or moderate confidence,
and they describe when a capability might become available rather than when this route might succeed. They
are included because a limit with no timescale attached tends to be read as permanent, which for the
instrument-bounded and access-bounded limits here would be wrong.

## 8. Reproducibility

Every figure in Sections 2 and 3 is generated by scripts in `research/modalities/` and regenerated in
continuous integration: `fusion_breakpoints.py` for the junction set and predicted binders,
`hla_coverage.py` for population coverage, `coverage_scan.py` for the broad-panel curve,
`junction_proteome_novelty.py` for the proteome search of Section B5, and `patient_neoepitopes.py` and
`patient_cd4_epitopes.py` for the per-patient shortlisters. The corresponding artifacts are
`fusion-breakpoint-neoantigens.json`, `hla-coverage.json`, `coverage-curve.json`,
`junction-proteome-novelty.json` and `patient-cd4-demo.json`. Clinical figures are
quoted from the curated EMC registry at `research/data/emc-clinical-registry.json`, which carries
structured citation provenance and retrieval notes for each record.

## 9. Declarations

Prepared with AI assistance. The author is responsible for all content. No funding was received. The author declares no
competing interests. No patient data were used and no human material was handled; the clinical figures
quoted are from published or publicly presented aggregate results.

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
