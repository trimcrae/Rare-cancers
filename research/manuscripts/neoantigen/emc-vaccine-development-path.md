---
id: DOC-EMC-VACCINE-DEVELOPMENT-PATH
title: "Toward a fusion-junction vaccine in extraskeletal myxoid chondrosarcoma: a blocker-by-blocker development path"
level: L3
kind: manuscript
status: live
canonical_for: [emc-vaccine-development-path]
purpose: >
  Enumerate every obstacle standing between the EWSR1::NR4A3 fusion junction and a viable
  therapeutic vaccine in extraskeletal myxoid chondrosarcoma, state what evidence would clear
  each, and order them into a staged development path with explicit falsifiers.
scope: >
  Computational and evidence-synthetic. No wet-laboratory work was performed. No efficacy,
  safety or clinical-readiness claim is made for any agent or combination.
audience: [external reviewers, collaborators, maintainers, autonomous research agents]
date: 2026-08-19
last_verified: 2026-08-19
---

# Toward a fusion-junction vaccine in extraskeletal myxoid chondrosarcoma: a blocker-by-blocker development path

*Preprint draft, 2026-08. Author: [Name], independent researcher, [City, Country]. Independent,
personal-capacity work, unconnected to the author's employer; prepared with AI assistance (Section 9).
Review by a sarcoma medical oncologist and a tumour immunologist is recommended before circulation.*

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is a rare soft-tissue sarcoma defined by
rearrangement of *NR4A3*, most often to *EWSR1*. The fusion junction encodes a peptide sequence that is
absent from either parent protein, and because the fusion is the truncal oncogenic driver it is present
in every tumour cell and cannot be lost without loss of the driver. Individualised neoantigen therapy has
now reported a positive phase 3 result in resected melanoma, which makes the platform question timely for
other tumours. EMC, however, is a low-mutation, immunologically cold tumour, and the junction-directed
vaccine has previously been set aside on those grounds.

**Purpose.** This paper does not argue that an EMC vaccine will work. It asks a narrower and more
tractable question: what specifically stands in the way, what evidence would clear each obstacle, in what
order can those obstacles be attacked, and what result at each stage would end the programme. The intent
is to convert a route that has been dismissed in aggregate into a set of individually addressable and
individually falsifiable propositions.

**Methods.** Junctions were derived at the transcript level from Ensembl exon structure, so the acceptor
exon is retained whole including its 5' untranslated region, and class I binding was predicted with
MHCflurry 2.0. Population coverage was computed from Allele Frequency Net Database frequencies using the
standard population-coverage formula with Wilson intervals. Clinical evidence was drawn from a curated
EMC registry with structured citation provenance. No new wet-laboratory data were generated.

**Findings.** Of 27 declared exon pairs, 5 are in frame and yield 11 distinct predicted binders, of which
4 are strong; there is no pan-EMC epitope. Class I population coverage is 8.51% (95% CI 8.26 to 8.76) for
the commonly reported *EWSR1* exon 7 to *NR4A3* exon 3 junction, presented on HLA-B\*15:01 alone, and
27.4% (95% CI 26.6 to 28.1) pooling all strong-binder alleles. Screening the junction against a broad
34-allele panel raises the ceiling only to 30.4%, with 4 alleles presenting anything at all, and the
coverage curve never reaches 50%. A proteome-wide exact-match search finds 170 of the 174 junction
peptides absent from the reviewed human proteome including isoforms; the 4 that are present all occur in
an *NR4A3* isoform, and one of them is a predicted binder and is withdrawn. The class II arm, regenerated
at the corrected junction, yields 2 predicted binders and no strong binder on a three-allele DR panel.
Against this, a histology-specific EMC cohort of sunitinib plus
nivolumab reported 16 of 23 evaluable patients progression-free at 6 months with median progression-free
survival of 13.2 months, which indicates that an immunotherapy-containing regimen is not inert in this
disease. Ten obstacles are enumerated: one is resolved, one is answered and negative on the panel tested,
two are computational and outstanding, two require EMC tissue, two require clinical evaluation in
combination, and two are structural features of studying a disease with an incidence well under one per
million per year. Because no strong class II binder survives at the corrected junction, the combined CD8
and CD4 coverage figure is null rather than merely unreported.

**Interpretation.** The central observation is a gap in prior reasoning rather than a new measurement.
Innate agonists and in-situ vaccination were set aside for this disease on the grounds that a quiet genome
supplies too few antigens, while the junction vaccine was set aside on the grounds that a cold tumour
supplies too little priming. Each was excluded for lacking precisely what the other provides. The unit
that should be evaluated is therefore a junction vaccine combined with checkpoint blockade on a backbone
that also addresses physical exclusion, not a vaccine alone. That combination has never been graded as a
unit. Predicted binding is a screen and not evidence of presentation, immunogenicity or benefit, and
nothing here supports use of any agent outside a clinical trial.

## 1. Why enumerate blockers rather than argue for a route

Two framings are available for a therapeutic hypothesis in a rare disease. The first asks whether the
hypothesis is promising, and answers with a judgement. The second asks what would have to be true for it
to work, and answers with a list. The first framing has already been applied to the EMC junction vaccine
and returned a negative: a self-adjacent junction in a cold tumour is a weak immunogen, and the route was
set aside. That judgement is defensible on the evidence available at the time.

It is also unfalsifiable in its aggregate form, and it conceals the fact that the obstacles it bundles
together have very different characters. Some are arithmetic and already answered. Some are measurements
nobody has taken and which cost little to take. Some are properties of the tumour that no amount of
engineering will change. Grouping them under a single verdict makes the cheap ones invisible and gives
the expensive ones no price.

This paper takes the second framing. Each obstacle is stated as a proposition, paired with the evidence
that currently bears on it, the specific observation that would clear it, and an estimate of what
obtaining that observation costs and who is capable of obtaining it. Where an obstacle is a fixed
property of the disease it is labelled as such rather than assigned a mitigation. Where the existing
reasoning about an obstacle appears to be in error, that is stated with the reasoning shown.

The immediate occasion is external. A randomised phase 3 trial of an individualised neoantigen therapy
combined with pembrolizumab has reported meeting its primary endpoint of recurrence-free survival in
resected stage IIB to IV melanoma, following the phase 2b result in the same setting [3]. That does not
transfer to EMC, and Section 4 sets out why the transfer fails on the axis that matters. It does
establish that the manufacturing, regulatory and delivery apparatus for an individualised RNA vaccine now
exists as a clinical reality rather than as a proposal, which changes the cost of several of the
obstacles below.

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
untouched. These gaps are enumerated as obstacles B2 and B3 below rather than treated as resolved.

## 3. The blocker ledger

Ten obstacles are enumerated. The kind column distinguishes an obstacle that is an unperformed
computation, one that requires biological material, one that requires an industrial partner, and one that
is a fixed property of the disease.

| ID | Obstacle | Kind | Clearing observation | Cost tier |
|---|---|---|---|---|
| B1 | Class I coverage plateaus near 30% | fixed property, partially mitigable | Extended allele panels; class II contribution; per-patient selection | Computational |
| B2 | Presentation is predicted, never measured | measurement | Immunopeptidomics on EMC tissue or a patient-derived line | Tissue |
| B3 | Self-adjacency and central tolerance | measurement | Distance-to-self and anchor-position filtering; T-cell reactivity assay | Computational, then tissue |
| B4 | No strong CD4 epitope at the corrected junction | measurement, performed | Wider class II allele panel; measured class II presentation | Computational, then tissue |
| B5 | Four peptides occur in an *NR4A3* isoform | resolved, with a withdrawal | Completed; the upstream filter needs to become isoform-aware | Done |
| B6 | Immunologically cold microenvironment | property, addressable in combination | Vaccine supplies antigen; checkpoint supplies release | Clinical |
| B7 | Physical exclusion by myxoid matrix | property, addressable in combination | Vascular normalisation or matrix-directed agent | Clinical |
| B8 | No EMC immune-profiling data | measurement | Infiltrate and HLA-expression characterisation on EMC specimens | Tissue |
| B9 | Manufacturing economics at this incidence | structural | Platform partner; basket or master-protocol vehicle | Partner |
| B10 | Trial design below the randomisation threshold | structural | Adaptive or histology-cohort design with a defensible endpoint | Partner |

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
change nothing here. This obstacle is about which patients have a target at all.

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

**Comparator.** This obstacle is where EMC differs most sharply from the melanoma setting, in which
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
peptide vaccine design and would make this obstacle a design constraint rather than a blocking one.

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
4 strong binders survive, including the *EWSR1* exon 7 lead NMPCVQAQY. The obstacle is largely cleared, and
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

**Why this obstacle is distinct from B6.** A cold tumour lacks a response. An excluded tumour may have a
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

The obstacles above do not resolve independently. B6 and B7 are properties of the tumour that a vaccine
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
components are complementary rather than redundant, and each covers an obstacle the others do not.

This is also the architecture used in the melanoma programme that generated the recent phase 3 result:
the individualised vaccine is given with pembrolizumab, never alone [3]. The transfer from melanoma to EMC
fails on antigen depth, because melanoma supplies a large pool of private neoantigens from which roughly
thirty can be selected against the patient's genotype while EMC supplies one. It does not fail on
architecture. The architectural lesson transfers even though the disease biology does not.

The proposition this paper puts forward is therefore narrow and testable: the addition of a
breakpoint-matched junction construct to a checkpoint and antiangiogenic backbone is a coherent
combination in which each component covers a distinct and enumerated obstacle, and it has not been
evaluated or graded as a unit. Whether it should be evaluated depends on results from Stage 1 below, and
in particular on B2.

## 5. Staged development path

The stages are ordered so that the cheapest observations that could end the programme come first. Each
stage names the gate that must pass before the next is worth beginning.

**Stage 0, computational, no cost.** Two items are complete. The proteome-wide novelty search has been run
and did not close the route: 170 of 174 peptides are novel and all 4 strong binders survive, with one
predicted binder withdrawn (B5). The class II arm has been regenerated and is reported, negative on the
panel tested (B4). Two items remain: build the distance-to-self and
anchor-versus-contact-position filters that were specified and never implemented (B3); and extend the
class I allele panel beyond 34 and the class II panel beyond three DR alleles, then report the revised
ceilings (B1, B4). *Gate:* if anchor analysis shows that novelty falls
exclusively at anchor positions across all in-frame junctions, the route closes here at no cost.

**Stage 1, requires EMC tissue.** Immune profiling of EMC specimens, comprising infiltrate quantification
and HLA class I expression (B8), followed by immunopeptidomics for junction-spanning peptides on tissue or
a patient-derived line (B2). *Gate:* HLA class I loss, or failure to detect any junction peptide across
adequate material, closes the route and also closes the T-cell receptor and soluble T-cell receptor routes
that share this antigen. A positive identification is the single result that would justify Stage 2.

**Stage 2, requires a partner.** T-cell reactivity assessment against the identified peptide-HLA complexes
using healthy-donor and, if available, patient-derived material, to address the tolerance question in B3
directly. In parallel, an assessment by a platform holder of whether a small fixed panel of
breakpoint-matched constructs is manufacturable within the constraints of B9. *Gate:* no detectable
reactivity in an appropriately powered assay closes the route.

**Stage 3, clinical.** Addition of a breakpoint-matched construct to an established checkpoint and
antiangiogenic backbone within a histology-specific cohort of a sarcoma master protocol, with a fixed-time-point
progression-free survival endpoint and with HLA and breakpoint eligibility stated in advance (B10). The
eligible fraction is bounded by B1 and should be planned against approximately 30% rather than against the
whole population.

## 6. Falsifiers

Explicit falsifiers, stated so that a negative result is recognisable as one rather than absorbed:

1. Every strong-binding junction peptide also occurs in a normal human protein. *Evaluated and not met:*
   all 4 strong binders are absent from the reviewed human proteome including isoforms, although 4 peptides
   of 174 and one weak binder are not.
2. Across all five in-frame junctions, the novel residues fall exclusively at anchor positions, so no
   junction presents an altered surface to a T-cell receptor.
3. EMC specimens show loss or substantial downregulation of HLA class I.
4. Immunopeptidomics on adequate EMC material detects no junction-spanning peptide.
5. No T-cell reactivity is detectable against any identified junction peptide-HLA complex in an
   appropriately powered assay.
6. The combined class I and class II eligible fraction, after the Stage 0 refinements, remains low enough
   that a histology-specific cohort cannot accrue at the observed rate.

Item 1 has been evaluated. Items 2 and 6 are computational and can be evaluated now. Items 3 and 4 require
tissue. Item 5 requires tissue and an assay platform.

## 7. Limitations

All binding figures are predictions from a sequence-based model and no EMC-specific validation of that
model exists. Population coverage is computed from reference allele frequencies with an independence
assumption across loci, and the population-to-region mapping is an approximation. The IMMUNOSARC II EMC
cohort result is a conference abstract, single-arm, and not peer-reviewed, and it evaluates a combination
in which the component with the larger independent EMC evidence base is the tyrosine kinase inhibitor
rather than the checkpoint inhibitor; it is cited here to establish that a vehicle and a backbone exist,
not to attribute activity to the immune arm. The characterisations of EMC as cold and as immune-excluded
rest on inference rather than on published EMC-specific immune profiling, which is itself recorded as
obstacle B8. The class II panel comprises three DR alleles and no DP or DQ alleles, so its negative result
bounds a narrow question rather than the general availability of helper epitopes. No claim is made
that any peptide is presented, that any construct would be immunogenic, that any combination would be safe
or effective, or that any of this is ready for clinical use. No wet-laboratory work was performed for this
paper, and its central recommendations require work this programme cannot carry out.

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
