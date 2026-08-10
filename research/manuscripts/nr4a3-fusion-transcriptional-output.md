---
id: DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT
title: "The published direct-target catalogue of the EWSR1::NR4A3 fusion is three genes wide, and none is separable from disease association in the available EMC expression record"
level: L3
kind: manuscript
status: live
canonical_for: ["the evidence-typed catalogue of published NR4A3 / NR4A3-fusion transcriptional targets", "the null-calibrated instrument for reading a gene set in the readable EMC expression series", "the cross-platform concordance reading of the class-A fusion target genes", "the confound audit of the EMC expression contrast — comparator composition, muscle admixture, reference pool and matrix content", "the size-matched empirical null used for a gene-set read on a small rare-tumour expression series, and its measured limits"]
purpose: >
  A submission-formatted report of what is actually known about the transcriptional output of the
  EMC fusion, and what the available expression record leaves of it. The published direct-target
  catalogue is enumerated with the evidence type recorded per gene; the three genes in it are read
  back in tumour tissue against a size-matched empirical null and an exact label-permutation test;
  the confounds that could manufacture the result are audited; and the paper states which single
  experiment would settle a question no correlative reading can. The null is treated as an applied
  instrument positioned against the existing competitive gene-set literature, not as a contribution.
scope: >
  Transcriptional output of the EMC fusion, at transcript level, in bulk tumour tissue. Asserts
  nothing about efficacy, selectivity, safety, a therapeutic window or clinical readiness for any
  agent, target or gene named, and no such quantity is computed. Says nothing about whether NR4A3
  is druggable, and nothing about the direction of any pharmacological intervention.
audience: [maintainers, external reviewers, autonomous research agents]
related: [DOC-GSE28866-READING, DOC-PPARG-DIRECTION-EMC]
date: 2026-08-10
last_verified: 2026-08-10
---

<!--
REPOSITORY NOTE (not part of the manuscript): the YAML block above is repository metadata read by
the systems checks; it is stripped at submission. So is Appendix A below, which is a supersession
register kept for the repository record rather than journal content. Everything from the title down
to the References is the manuscript proper, written so an external reader can reproduce it without
reading this repository. Purely operational notes live in
nr4a3-fusion-transcriptional-output-repo-notes.md. Supplementary material is in
nr4a3-fusion-transcriptional-output-SI.md.

SUBMISSION STATUS: submission-ready draft, not yet submitted. Revised 2026-08-10 in response to a
simulated internal peer review (nr4a3-fusion-transcriptional-output-peer-review-2026-08-10.md); the
point-by-point response is nr4a3-fusion-transcriptional-output-review-response-2026-08-10.md.
  Primary target : Genes, Chromosomes & Cancer (Wiley) — Original Research Article (subscription/$0 route)
  Alternatives   : The Journal of Pathology (Wiley); British Journal of Cancer (Springer Nature)
  Preprint       : bioRxiv (Cancer Biology / Genomics), free open copy
  Furniture      : nr4a3-fusion-transcriptional-output-cover-letter.md,
                   nr4a3-fusion-transcriptional-output-submission-checklist.md
-->

# The published direct-target catalogue of the EWSR1::NR4A3 fusion is three genes wide, and none is separable from disease association in the available EMC expression record

**Running title:** The EWSR1::NR4A3 direct-target catalogue, read back in EMC tissue

**Author:** Tristan D. McRae¹

¹ Independent Researcher. Correspondence: trimcrae@gmail.com
ORCID: [ORCID TO BE SUPPLIED BY THE AUTHOR BEFORE SUBMISSION]

**Article type:** Original Research Article
**Keywords:** extraskeletal myxoid chondrosarcoma; EWSR1::NR4A3; fusion transcription factor; transcriptional target; gene-set calibration; rare sarcoma; cistrome

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is defined by rearrangement of *NR4A3*, and its central
hypothesis is that the resulting chimera drives an aberrant transcriptional programme.
Across 2,276 retrieved full-text documents, the set of genes for which any NR4A3 chimera has been
shown to bind DNA is three: *SEMA3C*, *PPARG* and *ENO3*. All three were read back in the three
public EMC cohorts (6, 10 and 4 tumours) against a size-matched empirical null of random gene sets
from the same platform, an exact label-permutation test, every comparator stratum separately, a
matrix covariate and a muscle control. The 19-gene aggregate of fusion-bound
and native-NR4A3-bound targets reaches 39% and 88% of its null threshold on the two readable array
platforms and does not clear, while a published EMC expression signature clears the same threshold
11.9-fold and 4.2-fold in the same run. Calibrated, the three genes separate: *SEMA3C* survives
nothing and reverses sign with the comparator arm; *PPARG*'s strongest reading is circular, scored on
the cohort that first published it; *ENO3* survives every test but was the pre-designated positive
control and is not an independent finding. The binding constraint is not sample size. No experiment
has measured where an NR4A3 fusion binds, or what chromatin does, in EMC material; the one
genome-wide chromatin readout carrying these fusions reads accessibility in HEK293T, and the 110 NR4A
peak sets available are the wrong protein or the wrong disease. Until a fusion cistrome in EMC
chromatin exists, "elevated in EMC" and "driven by the fusion" are inseparable.

---

## 1 · Introduction

### 1.1 · The disease and the driver

EMC is a rare soft-tissue sarcoma defined by rearrangement of *NR4A3* (NOR-1/TEC). Subramanian
*et al.* describe it as "characterized by a balanced translocation most commonly involving t(9;22)
(q22;q12)" (PMID 15920699), which produces EWSR1::NR4A3; Brenca *et al.* express and assay both that
chimera and TAF15::NR4A3, "the commonest TAF15 (exons 1–6)–NR4A3 (exons 3–8) fusion" (PMID 31020999),
with a rarer *t(3;9)(q11-12;q22)* TFG::NR4A3 variant accounting for part of the remainder. NR4A3 is
an orphan nuclear receptor, and the chimera places its DNA-binding domain under a strong FET-family
transactivation domain. The disease's central molecular hypothesis is therefore straightforward: the
fusion is a transcription factor with an aberrant output, and that output is where the disease lives.

### 1.2 · Two different questions, and the frequency of each

The hypothesis dates from the fusion's cloning in 1995 (PMID 8634690). Two questions bear on it and
they are different: which genes has anyone shown an NR4A3 chimera to physically bind and drive, and
which genes are high in EMC tumours? The first is a mechanism claim; the second is an association. A
gene can satisfy the second for reasons unrelated to the fusion, including EMC's cell of origin, its
myxoid and hypocellular architecture, the anatomical site it arises in, or the gene being a generic
matrix or proliferation gene.

Neither question is much discussed. Measured against Europe PMC on 2026-08-08, of 1,305 records
naming the disease 261 are reviews, and the three genes with a published fusion DNA-binding assay are
named in 3, 1 and 0 of those 261 reviews respectively (*PPARG*, *SEMA3C*, *ENO3*). Their primary
sources are ordinary references of this literature, with EMC records supplying 42%, 54% and 33% of
the citations of Filion *et al.*, Subramanian *et al.* and Kim *et al.* and citing them in 4, 6 and 0
EMC reviews; the one source with a thin profile is Kim *et al.*, which is the source of the gene that
survives every test below (SI §S2). So the gap addressed here is not a contested claim in need of
correction: a disease defined by a transcription-factor fusion has no assembled account of what that
fusion transcribes.

This work separates the two questions by cataloguing the mechanism claims with their evidence type
recorded per gene, reading them back in tumour tissue with an explicit calibration for what an
arbitrary gene set of the same size does on the same platform, and putting each gene through the
confounds that could have manufactured it.

### 1.3 · The limits of an uncalibrated gene-set read

On a small rare-tumour series almost every gene set scored comes back higher in the index arm. In the
10-versus-6 series used here, PPARγ targets, hypoxia metagenes, adipogenesis, chondroitin-sulfate
biosynthesis and arginine metabolism all read "higher in EMC". The reason is not biology: a raw Welch
contrast on the sample means uses the samples as its unit of variability and ignores that a set's
per-sample score is one draw from a distribution whose width depends on the set's size and on the
platform. At n = 10 versus 6 that width is large. The 95% band for a random 17-gene set on GPL3290 is
[−0.297, +0.376] SD, and this paper's own aggregate target set, which has 17 readable members on that
platform, prints a raw delta of +0.330 with t = 3.16 and sits inside it.

Calibrating a set score against random sets of the same size drawn from the same platform is the
competitive gene-set null, and it is long established (§2.3.1). What follows is that null applied to
the gene set in this disease carrying the strongest mechanistic warrant, together with the
self-contained permutation test the competitive null cannot replace, and a measurement of how far the
calibration itself can be trusted at these arm sizes.

---

## 2 · Materials and Methods

Full method detail is in Supplementary Information §S1–§S11.

### 2.1 · The evidence-typed target catalogue

Every claim in the primary literature that EWSR1::NR4A3, another NR4A3 fusion, or native NR4A3
transcriptionally activates a named gene was recorded with the gene, the factor actually tested, the
assays, the cell system, the species of those cells, the expected direction in EMC, and the verbatim
sentence the classification rests on. Four evidence classes were assigned per row. Class A is a
DNA-binding or promoter assay performed with an NR4A3 fusion (3 genes); class B is the same assay
class with native NR4A3 (16 genes), where transfer to the fusion is an assumption tested in §3.2;
class C is a gene that moves when the fusion is expressed, with no binding assay (2 genes); class D
is measurement in EMC tissue with no mechanism (1 gene). The complete 22-row catalogue with verbatim
sentences is Supplementary Table S1.

Class B is not one evidence type and is split accordingly. B1 (6 genes) is a row whose primary assay
paper was retrieved and read; B2 (10 genes) rests on a review's assertion with no primary assay paper
retrieved, the partition rule being that the catalogue row's citation begins "Reviewed in". Class B
supplies 16 of the 19 genes in the aggregate that carries this paper's central negative, and §3.7
therefore reports A+B1 alongside A+B.

### 2.2 · Datasets

Three independent EMC cohorts on three platform families were used. They are never pooled (§5).

**Table 1. The three cohorts.**

| cohort | platform | EMC | comparators | value kind |
|---|---|---|---|---|
| **GSE24369** | GPL6244, Affymetrix Gene ST | 6 | 29 — 17 FET-rearranged LGFMS + 6 myxofibrosarcoma + 6 desmoid fibromatosis | single-channel intensity |
| **GSE4303** | GPL3290, two-colour cDNA, 43,008 probes | 10 | 6 (3 DFSP + 3 GIST) | two-colour log-ratio vs a reference pool |
| **GSE28866** | 3SEQ (GPL10999) | 4 | 32 non-EMC sarcoma libraries; 27 normal-organ libraries | 3′-end read density per peak |

Every class label above is the GEO sample title, not an internal grouping name. That distinction
decides §3.4: 23 of the 29 GPL6244 comparators are themselves myxoid tumours (17 low-grade
*fibromyxoid* sarcomas and 6 *myxo*fibrosarcomas) against 6 collagen-rich desmoid fibromatoses,
whereas none of the 6 GPL3290 comparators is myxoid. The two array cohorts therefore differ in the
one property the leading confound is built on, which makes the pair a control rather than only a
limitation. GSE24369's comparator arm is itself FET-rearranged (LGFMS is *FUS::CREB3L2*), so a
difference here is not merely "has a FET fusion"; of its 42 samples, 6 EMC and 29 comparators account
for 35, and the remaining 7 (five solitary fibrous tumours and two pooled skeletal-muscle RNA
samples) are excluded from both arms, the muscle pair making the *ENO3* admixture objection
measurable (§3.5). GSE4303 is Subramanian *et al.*, *J Pathol* 2005;206:433–444 (PMID 15920699), a
seven-platform series of which only GPL3290 carries a usable contrast; its verbatim sample
annotations record that all 10 EMC and all 3 DFSP samples are on the CRH reference pool while the 3
GIST samples are on Universal Human Reference (§3.4). GSE28866 is Brunner *et al.*, *Genome Biol*
2012;13(8):R75 (PMID 22929540); its 32 sarcoma columns come from 30 specimens.

Each cohort's EMC arm size was read from its series matrix and independently recovered from GEO
sample titles by a six-query GEO search (SI §S8), where the three cohorts serve as that search's
positive control. That search returned 56 records, 22 of them series or curated datasets, every one
read at sample level, and no fourth EMC expression cohort; four of its six queries first returned
zero through a shared field restriction and are reported in their repaired form, with both forms
recorded. GSE170983 is easy to miscount as a fourth cohort: it carries 99 samples, four of them EMC,
and is the same Brunner deposit as GSE28866.

### 2.3 · Scoring and the size-matched empirical null

Probes were mapped to symbols per platform (GPL6244: 20,230 of 28,459 probes to 18,694 distinct
symbols; GPL3290: 27,203 of 43,008 probes to 14,932, through an EST-accession bridge). Each sample's
values were z-scored against that array's own probe distribution; a gene or set score for a sample is
the mean z over its readable members; the contrast is a Welch *t* on the EMC versus comparator
per-sample scores (Welch, *Biometrika* 1947; PMID 20287819). A gene with no probe is treated as an
unread gene, never as an absent one. Floors were fixed at three samples per group for any contrast,
and four genes and 0.4 coverage for any set score.

Two quantities a raw Welch contrast does not supply are computed per platform. The exact global
offset is the per-sample mean z over every symbol the platform maps, contrasted EMC versus
comparator: the amount by which an arbitrary gene set is expected to differ for no set-specific
reason. The size-matched empirical null is 4,000 random gene sets of exactly the observed readable
size, drawn from a seeded random pool of the platform's own mapped symbols (seed 20260807; pool
4,000; universe 18,694 and 14,932), each scored exactly as the real set is; a random set carries the
offset too, so the null absorbs it by construction. The empirical p is the two-sided fraction of
draws at least as extreme, with +1/+1 smoothing (Phipson and Smyth, PMID 21044043), and a set is
reported as set-specific only if the observed delta falls outside the 95% band. Single genes are
calibrated the same way at set size 1. The smallest two-sided value the design can return is
2/4001 = 0.0005, and every value at that floor is written `p_emp ≤ 0.0005`. Three limits of the pool
are stated rather than implied: it is a seeded 4,000-symbol subsample of each platform's mapped
symbols (21% and 27%), the same pool is reused at every set size, and the gene under test is not
excluded from it.

#### 2.3.1 · Prior art, and the nature of this implementation

Calibrating a set score against random gene sets of the same size is a competitive gene-set null: the
null hypothesis is about the set relative to other genes, and the resampling unit is the gene. The
distinction between competitive nulls (gene sampling) and self-contained nulls (subject sampling),
and the argument that competitive nulls are anticonservative under inter-gene correlation, is the
standard framework in this area (Goeman and Bühlmann, PMID 17303618; Irizarry *et al.*, PMID
20048385; Rivals *et al.*, PMID 17182697). Pairing a gene-randomization null with a
sample-permutation null, which is what §2.3 and §2.6 build together, is restandardization (Efron and
Tibshirani, *Annals of Applied Statistics* 2007). A competitive test that additionally estimates and
corrects the inter-gene correlation is CAMERA (Wu and Smyth, PMID 22638577); the rotation-based
self-contained counterpart is ROAST (Wu *et al.*, PMID 20610611). Single-sample set scoring with an
explicit null of random gene sets of matched size is implemented in `singscore` (Foroutan *et al.*,
PMID 30400809), and control sets matched on expression bin rather than on size alone are standard in
single-cell module scoring (Tirosh *et al.*, PMID 27124452). GSVA (Hänzelmann *et al.*, PMID
23323831) and ssGSEA (Barbie *et al.*, PMID 19847166) are the comparators for the per-sample mean-z
score used here, and the original GSEA formulation is Subramanian *et al.*, PMID 16199517, a
different paper from the Subramanian *et al.* 2005 EMC expression cohort of §2.2 (PMID 15920699).

Nothing in the null used here is new. The only non-standard element is a reporting convention: the
observed effect is reported as a fraction of the detectability threshold rather than as a p-value, so
that a set which does not clear its null is described by how far it got. That convention makes a
negative interpretable; it is presentational, not a method. Presenting this implementation as a
method would require a simulation study benchmarking it against CAMERA on the established benchmarks
(Geistlinger *et al.*, PMID 32026945), which is not attempted.

#### 2.3.2 · The independence property of the null, and its correction

The null as implemented carries no inter-gene correlation term, which is measurable in the committed
artifact: across every scored set on both platforms, `null_sd × sqrt(n)` is constant to within 5.9%
(GPL6244 0.2528–0.2683 over set sizes 10 to 250; GPL3290 0.6623–0.6969 over sizes 10 to 230), the
signature of a mean of *n* independent gene-level contrasts, with the residual decline at the largest
sizes the finite-population correction for drawing without replacement from a 4,000-symbol pool. Two
consequences follow. The resampling is largely reproduced by a closed form, `offset ± 1.96
σ_platform / sqrt(n_readable)`, with σ = 0.261 on GPL6244 and σ = 0.678 on GPL3290: on GPL3290 that
expression reproduces the resampled band edges to within 3–13%, and on GPL6244 to within 14–36%,
because the null delta distribution there is left-skewed (at n = 19 the resampled band is [−0.142,
+0.105] against a closed-form [−0.126, +0.109]). The resampling is therefore worth running rather
than replacing, but the algebra sets the scale.

Second, an independence null is anticonservative for a coherent set, and the size of that effect is
computable. For each set the mean pairwise correlation ρ̄ between member genes' per-sample z was
computed after centring each gene within each arm, so that the arms differing cannot itself inflate
ρ̄; the variance inflation factor is 1 + (n−1)ρ̄ and the inflated threshold is the uninflated one
times its square root. Every set score in §3.7 and Supplementary Table S2 carries both. The direction
of the correction is not symmetric across this paper's claims: a set that fails an anticonservative
null fails a correct one a fortiori, so the negatives are strengthened, while every positive scored
against the competitive null alone sits on the unprotected side. Unqualified competitive-null
language is confined to the negatives throughout, and the six PPARγ arms in SI §S4 are re-reported
with their inflated thresholds, under which none clears. Two further sensitivities are in SI §S3:
redrawing the 4,000 random sets under 20 further seeds moves the 97.5th percentile by a relative
standard deviation of 1.6–3.1%, which bounds Monte-Carlo error but not pool composition, and two
composition-matched nulls were computed for the aggregate and the positive-control set, matching each
draw's decile composition on mean value and on detection rate (§3.7).

### 2.4 · Instrument controls, graded before the biology

Four known answers were graded before any biological read: *ENO3* (up on both platforms, the positive
control), *NR4A3* (up, tumour identity), *PLAGL1* (down, PMID 16112421, the directional falsifier,
the only prediction an arm-wide offset cannot manufacture) and *SGK1* (flat or down at transcript
level despite 10/10 protein positivity, PMID 16756948).

Grading is on where the delta sits relative to its size-1 null, never on the raw delta, and the rule
has three outcomes. A delta outside its null band is graded, and agrees or disagrees with the
published direction; a delta inside the band is not a reading at this power and is not graded either
way; a control with no computable contrast is likewise not graded. The denominator of any "n of n
agree" statement is therefore the number of gradeable readings rather than the number of controls,
and §3.3 gives every count and separates the agreements that could have refused their prediction from
those that could not. The size-1 null is drawn once per platform while genes differ in how many
samples carry a value, so Table S3 prints each gene's own arm sizes, and the size-1 null was also
redrawn under each gene's own observed sample set: those bands are 1.6–3.4% wider and change no grade
(SI §S3).

### 2.5 · The 3SEQ arm and its calibration

3SEQ measures 3′-end read density per peak. A gene's value in a library is the median across that
gene's peaks; an arm's value is the median across that arm's libraries. No z-score, no test and no
confidence interval are used, because n = 4, and nothing from this arm is pooled with the arrays. A
fold-change is not a reading until an arbitrary gene's fold-change is known, so the same two ratios
were computed for every gene in the deposit (14,120 genes; 13,708 with a computable EMC/normal ratio,
13,247 with an EMC/sarcoma ratio) and each target gene is reported as a percentile of that
distribution. A gene whose comparator median is zero has no ratio and is excluded rather than ranked
at the top. This axis contributes an ordering and never a test.

### 2.6 · Confound audit and sensitivity analyses

Four further readings were computed offline from the same cached inputs, using the same scoring
primitives, so the quantity tested is identical to the quantity reported; every delta re-derived was
asserted equal to the primary artifact before anything was written. Full detail is in SI §S5.

Exact sample-label permutation supplies a self-contained null: the EMC/comparator label is permuted
over samples and the real gene set rescored, so correlation structure is carried through untouched.
Every reported permutation p is exact for the design that gene or set actually has, the enumeration
being complete in every case and ranging from 286 to 1,623,160 assignments; genes with missing values
enumerate their own smaller design, so *PLAGL1* at 8 versus 6 and *PPARG* at 10 versus 5 each
enumerate 3,003. The contrast is also recomputed with the comparator arm restricted to one class at a
time, to the myxoid classes only, to the non-myxoid classes only, and on GPL3290 to the
reference-pool-matched comparators only, each with its own exact permutation p; nothing about the EMC
arm changes, so any movement is attributable to comparator composition. Each gene's per-sample z is
regressed on a matrix-content proxy and the contrast recomputed on the residuals, the proxy being
selected by provenance so that no gene drawn from an EMC-derived list enters it; this is a
sensitivity analysis, not a correction. A skeletal-muscle admixture control, a leave-one-out
jackknife over the EMC arm, a rank-based re-read on within-array percentile, and Benjamini–Hochberg
q-values across the per-gene permutation p-values complete the panel (Benjamini and Hochberg,
*Journal of the Royal Statistical Society Series B*, 1995).

For the occupancy axis (§3.8), 110 published NR4A ChIP-seq peak sets were intersected with the
class-A genes' regulatory windows, the same window as the motif scan, and every count placed against
a background panel of 198 genes assembled for an unrelated question. Four rules govern the reading. A
raw count is never reported as a finding, because the deepest catalogue puts a peak in 82.8% of the
panel; a peak set that recovers almost no panel gene is marked uninformative, and its silence is an
absent reading rather than evidence of non-occupancy; only NR4A antigens are scored, since a histone
peak at a promoter reports that the promoter is active; and multiplicity is over distinct
experiments, not genome builds. The Haller peak files carry no genome build, and a BED intersected on
an assumed build silently reports another locus, so the build was measured from H3K4me3 promoter
recovery: 90.6–93.9% on hg19 against 32.2–33.6% on hg38, all four samples independently (SI §S9).

### 2.7 · Reproduction

Every value in §3 derives from a committed artifact and is not re-typed from prose. All analyses are
CPU-only, use open-source tooling, and reproduce offline from cached inputs with no network access;
producers refuse to write if any row disagrees with the artifact that owns it.

---

## 3 · Results

### 3.1 · The whole of class A

**Table 2. The complete class-A catalogue: every gene for which an NR4A3 chimera has been shown to bind DNA.**

| gene | chimera assayed | assays | cells | citation |
|---|---|---|---|---|
| **SEMA3C** | EWSR1::NR4A3 (and TAF15::NR4A3, and native) | predicted NBRE-like site (GRCh38 chr7) + ChAP-qPCR, Strep-tagged | tBJ/ER transformed human fibroblasts | Brenca *et al.*, *J Pathol* 2019;249(1):90–101 (PMID 31020999) |
| **PPARG** | EWSR1::NR4A3 (and native, and NR4A3ΔC) | predicted perfect NBRE at −675 bp, band-shift, 2.8 kb human *PPARG* promoter luciferase, single-nucleotide NBRE mutant | CFK2 fetal rat chondrogenic cells; human promoter construct | Filion *et al.*, *J Pathol* 2009;217(1):83–93 (PMID 18855877) |
| **ENO3** (β-enolase) | TFG::NR4A3, not EWSR1 | EMSA + ChIP + luciferase, two NBRE motifs upstream of the TSS, plus ChIP for H3 acetylation at the endogenous promoter | cultured lines over-expressing TFG-TEC | Kim *et al.*, *Mol Carcinog* 2016 (PMID 26310886) |

Three genes are the whole of class A, and only one of them (*SEMA3C*) combines the EWSR1 chimera,
human cells and a chromatin assay. Three is the count in 2,276 retrieved full-text documents across
five corpora (§3.8), not a claim about all of the literature. Class B holds sixteen genes: *CCND1*,
*SKP2*, *VTN*, *SMPX*, *CDKN2AIP*, *GLS2*, *SDHA*, *COX5A*, *PDP1*, *VCAM1*, *ICAM1*, *BIRC3*,
*NOX1*, *TH*, *LOXL2*, *MYH7*. Six are B1, with the primary assay paper retrieved: *SMPX* (promoter
deletion, site-directed mutagenesis, EMSA and ChIP in human cells, PMID 27181368), *CDKN2AIP* (ChIP
plus mutation-reversed reporter in human cells, PMID 39664575), *GLS2*, *SDHA*, *COX5A* and *PDP1*.
The other ten are B2. Class C holds *SGK1* and *PLAGL1*; class D holds *NDRG2*. A published negative
control accompanies them: *CALD1*, whose promoter was searched for NOR-1 response elements in the
same experiment that found the *SMPX* site, and none were found (PMID 27181368).

### 3.2 · Failure of the native-to-fusion transfer assumption in both directions

Class B is only usable if a native-NR4A3 target is a fusion target, and two published measurements
say the transfer can fail in opposite directions. Filion *et al.* put native NR4A3 and NR4A3ΔC on the
same *PPARG* reporter the fusion activates: "the results show that both the native and truncated
receptors do not activate PPARG transcription under the same conditions in which it is readily
activated by the fusion protein." Brenca *et al.* report the converse: "the ability of NR4A3 to
recognize the SEMA3C target region was retained by the EWSR1-NR4A3 chimera but was impaired by
TAF15-NR4A3." So "NR4A3 binds X" does not license "EWSR1::NR4A3 drives X in EMC", and a native-NR4A3
cistrome is not a fusion cistrome. Both halves are demonstrated in the primary literature, not argued
here.

### 3.3 · The instrument controls

Four controls on two platforms give eight control × platform cells (Table S3). Seven carry a
computable contrast; the eighth, *NR4A3* on GPL3290, is not measurable, because four of six
comparator spots for that probe are missing and two values remain against a floor of three. Six of
the seven are gradeable against their size-1 null, and all six agree with the published direction;
none disagrees. *PLAGL1* on GPL6244 falls inside its band (Δ −0.4235, band [−0.606, +0.529]) and is
sign-concordant but not a reading at this power. Of the six agreements, four are outside-band
readings that could have refused their prediction: *ENO3* on both platforms (Δ +0.8075, p_emp 0.0195;
Δ +3.8113, p_emp 0.00054), *NR4A3* on GPL6244 (Δ +0.7415, p_emp 0.0240) and *PLAGL1* on GPL3290
(Δ −2.134, p_emp 0.013). The two *SGK1* cells could not have refused theirs, because an inside-band
reading satisfies "flat or down".

Arm sizes are not uniform per gene and are printed in Table S3: on GPL3290 *PLAGL1* is measured on 8
EMC samples against 6 comparators and *PPARG* on 10 against 5, and only 42 of the 78 readable genes
have the full 10 versus 6. Redrawing each gene's size-1 null under its own observed sample set widens
the band by 1.6–3.4% and moves no verdict. The positive control is independently reproduced, *ENO3*
matching a separately written module's committed value to three decimal places on both platforms
(+0.8075 here, +0.8074 there, on GPL6244). The directional falsifier fires in the right direction
where it is gradeable: *PLAGL1*, the one gene in the catalogue with a published down prediction, is
−2.13 SD in EMC on GPL3290 and outside its null band while every other class-A row points up, and no
arm-wide artefact produces that pattern. Its published EMC reading is n = 6 by RT-PCR against
chondrocyte controls rather than sarcomas, so it is an argument against the offset explanation rather
than a fully independent falsifier.

### 3.4 · Null-band width rather than the global offset

The measured global offset is small: −0.0084 SD on GPL6244 (t −1.592, over 18,694 mapped symbols) and
+0.0258 SD on GPL3290 (t +1.646, over 14,932), so the pattern of §1.3 is not an arm-wide shift. At
n = 6 versus 29 and n = 10 versus 6 the sampling variance of a set score is far larger than a Welch
*t* on the sample means implies. On GPL3290 the 95% null band for a 17-gene set is [−0.297, +0.376],
so this paper's own aggregate target set, at 17 readable members, prints +0.330 with t = 3.16 and
sits inside it (p_emp 0.083). The same holds on the *t* scale, computed rather than assumed:
recomputing *t* for each of the 4,000 draws gives a 95% null band for *t* of [−3.31, +4.35] at that
size, and 9.9% of random 17-gene sets print a larger absolute *t*. **Figure 1** shows the delta-scale
version. Two structural properties of the comparator arms qualify every contrast below: the GPL6244
comparator arm is 23/29 myxoid, so it largely matches EMC on the property confound (b) of §4.1 is
built on while the GPL3290 arm is 0/6 myxoid, and the GPL3290 arm spans two reference pools, which is
a per-gene offset that within-sample standardisation cannot remove.

### 3.5 · The three genes, per gene and per comparator stratum

**Figure 2** shows every tumour.

**Table 3. The three class-A genes on both array platforms, under an exact label-permutation test.**

| gene | class | GPL6244 Δ mean z (exact p, BH q) | GPL3290 Δ mean z (exact p, BH q) |
|---|---|---|---|
| **ENO3** | A · fusion | **+0.8075** (7.3 × 10⁻⁵, q 0.00044) | **+3.8113** (1.3 × 10⁻⁴, q 0.00063) |
| **PPARG** | A · fusion | +0.3071 (0.049, q 0.097) | +2.4809 (3.3 × 10⁻⁴, q 0.00083) — circular, §3.6 |
| **SEMA3C** | A · fusion | +0.7298 (0.194, q 0.233) | +0.6228 (0.165, q 0.165) |

All three genes are positive-signed on both platforms against the pooled comparator arm, and each
clears its size-matched single-gene null on at least one. That qualifier is load-bearing, since
taking the comparator arm apart reverses *SEMA3C*. Sign concordance across three genes is in any case
what a coordinated programme predicts and also what three individually EMC-associated genes predict.
Under exact sample-label permutation, *ENO3* is significant on both platforms after multiple-testing
correction, *PPARG* on GPL3290 only, which §3.6 shows is the circular platform, and *SEMA3C* on
neither. Clearing the size-matched null says a gene's delta is extreme relative to other genes on the
platform, which is not the same statement as the two arms differing for that gene. No row changed
sign in any leave-one-out fit or on the rank re-read.

Restricting the comparator arm one class at a time separates the three genes further (Table S5). On
GPL6244 there are five stratified contrasts over four distinct comparator sets, because the
"non-myxoid only" arm is the six desmoid fibromatoses; GPL3290's "pool-matched only" arm is likewise
its three DFSP comparators. *ENO3* is invariant, spanning +0.805 to +0.816 across the four
distinct GPL6244 sub-arms, which share almost nothing, and significant against every one of them
including the myxoid-matched arm that controls confound (b) by design; against the pool-matched
GPL3290 comparators it is +3.515 (p = 0.0035, the design floor). *SEMA3C* reverses sign: +1.657 against LGFMS (p = 1.2 × 10⁻⁴) and −0.645 against desmoid
fibromatosis (p = 0.015), and +0.113 (p = 0.84) against the pool-matched comparators, so its apparent
elevation is a property of which sarcomas are in the comparator arm. It is not significant against the
pooled arm (p = 0.194) yet is significant against two strata in opposite directions, because the
pooled arm averages a stratum where it is low with strata where it is high; a gene that looks flat
against a heterogeneous comparator arm has not been shown to be flat. Conversely, five uncorrected
contrasts per gene is where a gene can most easily be flattered, so the summary is the least
favourable stratum, defined as the largest permutation p: on that measure *ENO3* is significant at
its worst stratum (p = 0.022) and *SEMA3C* is not (p = 0.136). For *SEMA3C* that definition is the
wrong one, since its scientifically worst stratum is the significant reversal against desmoid
fibromatosis. Adjusting on an 11-gene matrix panel carries its own control, since a covariate that
does not differ between the arms cannot move a contrast: the panel separates the arms on GPL6244
(Δ −0.518) and not on GPL3290 (Δ +0.006), and on GPL6244 *ENO3* retains 75% of its delta, *PPARG* 32%
and *SEMA3C* 171% (Table S6).

*ENO3* is also this study's positive control (§2.4), so its elevation in EMC is not an independent
finding of this work; it was chosen because Kim *et al.* published it as fusion-driven and a
separately written module had already committed its value. The control role tested one proposition,
whether it is up on both platforms, and everything that separates *ENO3* from *PPARG* and *SEMA3C*
was not part of it; the finding reported is the ordering of the three genes, which selecting one
member in advance cannot manufacture. Limitation 17 records what remains.

The muscle-admixture objection is the obvious alternative explanation for *ENO3*, muscle-specific
β-enolase in a tumour arising in deep soft tissue of the limb. GSE24369 contains two pooled
skeletal-muscle RNA samples, in neither arm and used by no contrast, which fix the scale of what
muscle looks like on this platform. *ENO3* sits near the top of the muscle array (percentile 0.996),
and so do four markers that are more muscle-restricted: *ACTA1* 1.000, *MYH7* 1.000, *PYGM* 0.999 and
*MYL1* 0.998. Three of the four sit at or below zero between the tumour arms (−0.057, −0.043 and
−0.150 percentile points) and the fourth, *PYGM*, moves +0.142, about 45% of *ENO3*'s +0.315. Put
through the same size-1 null the class-A genes face, all four markers fall inside their band on
GPL6244 (p_emp 0.16, 0.29, 0.11 and 0.064) while *ENO3* falls outside it (p_emp 0.023, Table S7).
Two limits
apply: *MYH7* is also a class-B row of this paper's own catalogue, so its flatness cannot be read
purely as evidence about admixture, and this bounds admixture of differentiated skeletal muscle only,
not a myogenic differentiation programme within the tumour.

### 3.6 · Circularity in GSE4303

The fetched GEO record for GSE4303 reads "Gene expression profile of extraskeletal myxoid
chondrosarcoma", with linked PubMed identifier 15920699 and contributor "Matt van de Rijn", so
GSE4303 is the Subramanian *et al.* (2005) cohort. Two consequences follow. The Filion Table 2 gene
set (set E, Table S2) is a gene list scored on the data it was derived from, and is reported for
completeness only. And the *PPARG* gene row on GPL3290 is circular in the same sense: Subramanian
*et al.* reported, from these arrays, "High levels of expression of PPARG and the gene encoding its
interacting protein, PPARGC1A, in most EMCs." Measuring *PPARG* high in GSE4303 re-derives a
published finding from the data it was published from; a circularity grade applied to a gene set but
not to a gene is not a grade. With that cell set aside, *PPARG*'s remaining evidence is GPL6244
(q = 0.097, which does not survive correction) and the 3SEQ cohort.

### 3.7 · The aggregate against its own null

**Table 4. Gene-set scores against their size-matched nulls, with the threshold each had to clear and its correlation-inflated counterpart.**

| set (readable size, GPL6244 / GPL3290) | GPL6244 | GPL3290 |
|---|---|---|
| **A · fusion DNA-binding targets** (3, 3) | no score — floor is 4 genes | no score |
| **B · native NR4A3 DNA-binding targets** (16, 14) | d −0.0675, 43% of threshold; 25% inflated | d −0.1453, 43%; 39% inflated |
| **A+B pooled** (19, 17) | d +0.0403, 39%; 23% inflated | d +0.3301, 88%; 69% inflated |
| **A+B1, primary assay retrieved** (9, 9) | d +0.1699, 110% of its own re-drawn threshold, p_emp 0.039; 73% inflated | d +0.9189, 191%, p_emp 0.0015; 191% inflated |
| **D · published EMC expression signature** (21, 18) | d +1.1311, p_emp ≤ 0.0005, 11.9× threshold; 6.3× inflated | d +1.4783, p_emp ≤ 0.0005, 4.2×; 2.3× inflated |
| **D without the three genes shared with set E** (18, 15) | d +1.0756, p_emp ≤ 0.0005, 10.6× (against 11.5× for the full set in the same resampler) | d +1.0343, p_emp ≤ 0.0005, 2.7× (against 4.1×) |

The aggregate direct-target set does not clear its size-matched threshold on either platform,
reaching 39% and 88% of it, and 23% and 69% of the correlation-inflated threshold. Set D, a published
EMC expression signature derived on a platform used nowhere in this work (Affymetrix U133A) from a
cohort used nowhere in this work (MSKCC), clears at the null's resolution floor on both series.

Set D is a positive control selected on the same contrast, and is relabelled as one here. It was
chosen as the 25 probe sets most over-expressed in EMC versus other sarcomas, so scoring it on
another EMC-versus-sarcoma contrast is a winner's-curse replication: a list chosen for maximal
difference on this contrast will clear by a large margin on any platform that works. It shows that
the contrast detects a list selected for this difference at 11.9-fold and 4.2-fold threshold; it does
not calibrate what effect size a mechanistically selected set should reach. Set D also shares three
genes (*DKK1*, *MAN1A1*, *NMB*) with set E, which is the overlap between Filion's EMC profile and the
top 50 of the GPL3290 cohort itself, so 3 of its 18 GPL3290-readable members are documented members
of a list derived from that platform. Scored in one resampler with and without them, the clearance falls from 11.5-fold to 10.6-fold
on GPL6244 and from 4.1-fold to 2.7-fold on GPL3290, so it is not an artefact of those three genes,
though the GPL3290 margin falls by more than a third.

Three sensitivities qualify the aggregate negative (SI §S3). Under composition-matched nulls the
aggregate reaches 36% and 42% of a detection-rate-matched and an expression-decile-matched threshold
on GPL6244, and 87% and 106% of the same two on GPL3290, the last of these clearing at p_emp 0.047;
on a two-colour platform the matched mean value is a mean log-ratio against a reference pool rather
than an expression level, so detection rate is the closer analogue there, and both are reported
without preferring either. The negative therefore holds under three of the four composition-matched
nulls, is marginal in the fourth, and holds under all four once the correlation inflation is applied.
The A+B1 aggregate, restricted to the nine genes whose primary assay paper was retrieved, does clear
its uninflated threshold on both platforms (110% and 191%) and does not clear the inflated threshold
on GPL6244; B1 alone, without the three class-A genes, reaches 22% and 20% and clears nothing, so the
A+B1 clearance is carried by the three class-A genes whose individual readings are given above and
are separately confounded. A+B1 is reported as a sensitivity and not substituted for A+B as the
primary aggregate, since selecting the subset that clears is the manoeuvre this calibration exists to
prevent. Finally, the aggregate's raw delta on GPL3290 is +0.330 with an exact label-permutation 95%
confidence interval of [+0.092, +0.565], and on GPL6244 +0.040 with a sampled interval of [−0.082,
+0.163]. That interval replaces a power claim this design cannot support: the fraction-of-threshold
figure is descriptive and carries no information about the probability of detecting a true effect of
any given size, whereas a true shift of the set score larger than 0.15 SD on GPL6244 or 0.46 SD on
GPL3290 would fall outside the size-matched band four times in five, and smaller shifts are not
excluded.

Class B is flat-to-negative on both platforms with *VCAM1* significantly down on both, as Filion's
own measurement predicts (§3.2). One further reading belongs here: the A+B aggregate does not beat an
arbitrary set of the same size on either platform, and yet on GPL3290 it does differ between the arms
more than chance relabelling would give (exact p = 0.011). That is not a contradiction. The aggregate
target set really is higher in EMC, and so is almost any set of that size on that platform, which is
the distinction a competitive null is for. On the 3SEQ cohort (Table S8) all three class-A genes are
higher in EMC than in both comparator arms of a technology that shares no probe design with either
array: *ENO3* is in the top 2% of the 13,708 genes with a computable EMC/normal ratio (2.53×, 98.0th
percentile; 2.02× and 95.9th on the 13,247-gene sarcoma axis), *SEMA3C* is 94.2nd and 92.6th, and
*PPARG* is 84.0th against normals and 96.4th against sarcomas. "Top 2%" is not "highest", since
*RET*, *VCAN* and *CSPG4* all rank above *ENO3* here, and the normal arm is a six-organ tissue panel
with almost no soft tissue.

### 3.8 · The absent measurement in EMC chromatin

The obvious discriminator between driving and correlation is a cistrome. Five corpora totalling 2,276
full-text documents were searched; 153 name both a genome-wide chromatin method and NR4A3/NOR-1/TEC,
and none of the 153 applies one to an NR4A3 chimera. A wider search on 2026-08-08 across the primary
sequence archives retrieved GEO GSE243553 (Frenkel *et al.*, PMID 39048711), a pooled single-cell
ATAC screen of more than 100 oncofusions expressed in HEK293T whose library carries EWSR1-NR4A3,
TAF15-NR4A3, TCF12-NR4A3 and TFG-NR4A3 with wild-type NR4A3 and the reciprocal NR4A3-EWSR1 as
controls. It is accessibility and not occupancy, HEK293T and not EMC, ectopic and not endogenous, so
it is not a fusion cistrome and must not be cited as one. An earlier version of this manuscript read
the literature screen as establishing that no such experiment existed; that inference is withdrawn
and the corpus count it rested on is unchanged (Appendix A).

What is missing is therefore narrower than a blanket absence: no experiment has measured where an
NR4A3 fusion binds, or what chromatin does, in EMC material. Across GEO, SRA, BioProject, BioSample,
ArrayExpress/BioStudies, ENA and ChIP-Atlas, searched on 2026-08-08, an EMC disease term returns zero
deposits carrying any chromatin library strategy, and the 46 SRA runs an EMC term does return are
every one RNA-Seq, WXS, WGS, Targeted-Capture or CAGE (SI §S7). The negative is sharpest stated
comparatively, because the field runs this experiment routinely for the sibling fusions and has never
run it here: ChIP-seq for EWSR1::WT1 and EWSR1::ATF1, ATAC-seq for EWSR1::FLI1 and FUS::DDIT3, and
ChIP-seq twice for HEY1::NCOA2 mesenchymal chondrosarcoma. It remains a statement about what has been
deposited under a label an archive indexes, not about what exists.

The available surrogates were measured rather than dismissed: 110 NR4A peak sets from ChIP-Atlas,
ReMap2022 and the Haller *et al.* acinic cell carcinoma deposit were intersected with the class-A
genes' regulatory windows and placed against the 198-gene background panel (Table S9). Acinic cell
carcinoma activates native NR4A3 by enhancer hijacking, and Haller *et al.* mapped it at
8,501–18,666 peaks per sample across three carcinomas and one normal parotid gland, 55–121× the
deepest NR4A3 peak set otherwise available and the only NR4A3 cistrome in human tissue this analysis
could reach. It is not a fusion. The first number to read is the panel column: in the deepest
catalogue 82.8% of arbitrary genes carry a promoter-window peak, so "has an NR4A1 peak" is what
almost every gene does. Across the 12 informative experiments there are 36 gene-by-experiment tests
and 2 nominal hits at p < 0.05, both of them *ENO3*'s. No multiplicity statistic is computed on those
36; an earlier version reported a binomial tail against 1.8 expected, which requires each empirical p
to be uniform and the 36 tests to be independent, and neither holds, because the p-values are ranks
within a 198-gene panel of small integer peak counts and are heavily tied (*PPARG* returns exactly
1.00 in 11 of its 12 experiments) while the experiments share three genes, one panel and peak sets
that overlap by construction.

*PPARG* carries zero promoter-window peaks in all four deep NR4A3 experiments, which is a negative
rather than an absent reading, because those experiments recover 49–68% of the panel; it stands
against Filion *et al.*'s perfect NBRE at −675 bp, band shift and NBRE-mutant luciferase, and the two
are reconcilable, since a promoter can be bound by an over-expressed factor in a reporter assay and
unbound in a different lineage's chromatin. *SEMA3C* carries at most one peak in one experiment.
*ENO3* carries 2–4 peaks in every deep NR4A3 experiment and holds both nominal hits, p = 0.0348 in
the normal parotid gland and p = 0.0498 in an NR4A1 experiment; neither survives correction across
the 36 tests, and a signal present in normal tissue and absent from the tumours is the opposite shape
from a tumour-driven one. Two limits: NR4A1 supplies 8 of the 12 informative experiments and is a
paralogue sharing 0.347 of its peaks with NR4A3 in matched cells, and the twelve ChIP-Atlas NR4A3
peak sets at 53–154 peaks recover no panel gene, so their silence is an absent reading.

A sequence axis was also run (SI §S6): *ENO3* carries 4 exact NBREs in a −10 kb/+15 kb window, more
than its own composition predicts, *PPARG* carries 3, which is what composition predicts, and
*SEMA3C* carries none. Intersecting those four *ENO3* coordinates with GSE243553's per-fusion
accessibility calls places three inside TAF15-NR4A3's intervals and none inside EWSR1-NR4A3's, and
neither observation supports the motif argument: the EWSR1-NR4A3 set recovers only 2 of the 203
background promoters that resolve on hg38 (211 resolved, minus the 8 focus genes; the motif scan
itself resolves 198 windows, and the two counts are not interchangeable), so its zero is not a
reading, and the TAF15-NR4A3 co-location does not clear a null that slides the same four-site
configuration at its true spacing (p = 0.08).

### 3.9 · The instruments together

**Figure 3** puts the ordering on one screen. *ENO3* is supported by every instrument that returned a
test: both array platforms under an exact permutation test and after multiple-testing correction;
every comparator stratum separately, including the myxoid-matched and pool-matched arms; 75% of its
delta retained under matrix adjustment where that covariate differs and 100% where it does not; four
muscle markers more muscle-restricted than it is, all inside their size-1 null while it is outside;
and more exact NBREs than its own composition-matched null. It is additionally in the top 2% of the
13,708 genes with a computable ratio in an independent cohort on an unrelated technology, which is a
rank and not a test. The exception is the occupancy axis, and it is an exception for all three genes:
no class-A gene exceeds the background panel in any NR4A peak set after accounting for the 36 tests,
and *ENO3*'s two nominal hits are one in a normal parotid gland and one in an NR4A1 experiment.
*SEMA3C* is the mirror image, failing the permutation test on both platforms, reversing sign with
comparator choice, reading p = 0.84 against pool-matched comparators and carrying no exact NBRE.
*PPARG* sits between them, and lower than it first appeared, because its strongest cell is circular.
None of this converts association into causation for any of the three: every axis here is
correlative, the discriminating experiment (§4.3) remains unperformed, and ordering three genes by
independent support is not evidence that any is bound by the fusion in EMC.

![Figure 1](figures/fig1-size-matched-null.png)

> **Figure 1. Each set score beside random sets of the same size.** Grey histogram: 4,000 random gene
> sets of exactly the observed readable size, drawn from the platform's own mapped symbols under a
> fixed seed and scored identically to the real set. Shaded band: the central 95%. Vertical line: the
> observed delta, annotated with the value the set had to reach and how far it got. Top row: the A+B
> direct-target set reaches 39% and 88% of its threshold at 19 and 17 readable genes. Bottom row: set
> D, a published EMC expression signature selected on an EMC-versus-sarcoma contrast, overshoots by
> 11.9-fold and 4.2-fold. This null controls the platform offset and set size and not gene–gene
> correlation, so it is anticonservative for coherent sets; §2.3.2 gives the correlation-inflated
> threshold and §3.5 the complementary exact label-permutation test.

![Figure 2](figures/fig3-per-sample-class-a.png)

> **Figure 2. Every tumour, per gene and per comparator stratum.** Each point is one tumour; the
> horizontal bar is the arm mean. Values are within-array *z* against that sample's own probe
> distribution. n = 6 EMC vs 29 comparators (GPL6244) and 10 vs 6 (GPL3290). The two platforms
> measure different quantities and are never pooled, so no comparison across the two panels is
> licensed. The comparator strata are drawn separately because *SEMA3C*'s contrast changes sign
> between them (§3.5). No panel asserts that the fusion binds or drives any gene.

![Figure 3](figures/fig4-instrument-convergence.png)

> **Figure 3. Independent instruments applied to the three published direct targets.** The columns
> are not commensurable and no glyph is scaled by effect size: colour encodes only whether that
> instrument supported the gene, and each cell prints its own statistic in its own units. The amber
> cell marks the circular reading, *PPARG* on GPL3290, scored on the cohort from which high *PPARG*
> in EMC was first published (§3.6). The 3SEQ column is grey throughout and carries no test: at n = 4
> it is a percentile within that deposit's own distribution, printed so the three genes can be ranked
> on it. The stratum column is GPL6244 only and reports the least favourable exact p across five
> contrasts over four distinct comparator sub-arms. The occupancy column is grey for all three genes
> and is the only column on which no gene is supported: it reports the best empirical p any of twelve
> informative NR4A experiments gives against a 198-gene background panel, judged at a Bonferroni
> threshold for those twelve. Eight are NR4A1, a paralogue; four are wild-type NR4A3 in acinic cell
> carcinoma, a different disease. Neither is the fusion (§3.8). No cell asserts that the fusion binds
> or drives any gene.

---

## 4 · Discussion

### 4.1 · Alternative explanations, and their removal

A target gene that is up in EMC is consistent with the fusion driving it, and equally consistent
with: (a) EMC's cell of origin expressing it; (b) EMC's myxoid, hypocellular architecture; (c) a
platform-wide offset; (d) the gene being a generic proliferation or matrix gene; (e) the anatomical
site EMC arises in. The calibration removes (c) and part of (d). (b) is partly measured rather than
conceded, since the GPL6244 comparator arm is 23/29 myxoid and *ENO3* is unchanged against the
myxoid-only arm (+0.808, p = 8 × 10⁻⁵), while adjusting for an 11-gene matrix proxy containing no
EMC-selected gene leaves 75% of its delta where the covariate differs between arms and 100% where it
does not. (e) is bounded for *ENO3* by the muscle control of §3.5. What remains unremoved is (a):
nothing in these datasets separates a gene the fusion drives from a gene EMC's cell of origin
expresses, and the 3SEQ normal-organ arm does not help, because six visceral organs are not the soft
tissue EMC arises in.

### 4.2 · Contribution and its limits

Three things, in descending order of what survives. The map of what is missing, and the experiment
that closes it: class A is three genes wide, nothing has been deposited on EMC material under any
chromatin library strategy, and the 110 NR4A peak sets that do exist are measured, not assumed, to be
unable to substitute, while the same archives hold chromatin maps for five sibling fusions and one
accessibility screen carrying four NR4A3 fusions in HEK293T. The evidence-typed catalogue and the
confound audit: every claim carries the factor actually tested, the assay, the cell system and the
species; the native-to-fusion transfer assumption is shown to fail in both directions in the primary
literature; comparator composition is read from GEO sample titles rather than from a grouping label;
and the contrast is recomputed against every stratum, against the pool-matched comparators and
against a provenance-filtered matrix covariate. The ordering, which is the weakest part: *SEMA3C* is
supported by nothing that survives its own comparator being varied, *PPARG*'s strongest reading is
circular, and the surviving gene is the pre-designated positive control, so *ENO3*'s elevation is not
an independent finding and the ordering rests on cohorts of 4, 6 and 10.

Nothing here is a first-in-field methodological claim. The size-matched null is a competitive
gene-set null of a standard kind (§2.3.1), reported with its independence property measured and its
correlation correction applied; the only unusual element is a reporting convention, which is
presentational. No prior source states the class-A count of three, but the reason is measured rather
than asserted (§1.2), and it is not that the field says something different: the three genes are
named in 3, 1 and 0 of 261 EMC review records, so there is no competing account to correct. That is a
claim about a near-absence, the weaker of the two directions a citation index supports.

### 4.3 · The discriminating experiments

A cistrome in the right cell. An NR4A3 ChIP-seq peak set with the fusion expressed, intersected with
these expression reads: a gene that is up in EMC and carries a fusion-bound NBRE is driven; a gene
that is up with no peak is correlated. The nearest existing dataset is Haller *et al.* (2019, *Nat
Commun* 10:368, PMID 30664630), NR4A3 ChIP-seq in three human acinic cell carcinomas with a de-novo
NBRE motif recovered in all three, and the caveat is load-bearing: acinic cell carcinoma carries
native NR4A3 up-regulated by enhancer hijacking, not a fusion, and given §3.2's measurement that
native NR4A3 does not activate the *PPARG* promoter the fusion does, that dataset answers where the
NR4A3 DNA-binding domain goes in a human tumour and not where EWSR1::NR4A3 goes. GSE243553, the
nearest dataset in which an NR4A3 fusion is the perturbation, is subject to the same restriction from
the other direction, reading accessibility in HEK293T rather than occupancy in EMC chromatin. The
experiment named here is occupancy of an NR4A3 fusion in EMC material, and §3.8 shows the field
performs exactly that experiment routinely for neighbouring fusions.

Fusion knockdown or degradation in a genuinely fusion-positive EMC model, with RNA-seq, would also
discriminate; no such experiment was retrieved. So would fusion-type-stratified EMC expression data,
since Brenca *et al.* show class-3 versus class-4–6 semaphorins separating EWSR1- from
TAF15-translocated EMC while no readable series records which fusion each sample carries. A
within-EMC test against fusion level was attempted and does not discriminate at this n, giving
r = +0.37 (n = 6) and −0.35 (n = 10) for *ENO3*. An EWSR1::NR4A3 cistrome showing no peak near *ENO3*
would move it to "up in EMC, not fusion-bound"; one showing a peak near *SEMA3C* would restore
*SEMA3C* as a direct target despite its failure on every correlative axis here. A soft-tissue normal
comparator arm would remove confound (a), the one this paper cannot narrow. The fuller list is
Table S10.

---

## 5 · Limitations

These are ceilings, not caveats: each bounds what any sentence in §3 may be read to mean.

1. **Sample size.** n = 4, 6 and 10 EMC; nothing here survives being described as a distribution.
   This is a ceiling on the disease rather than on the search (SI §S8), whose bound is that a study
   registered in the Sequence Read Archive with no GEO series is invisible to a term search. One such
   study is public (`PRJNA1357027` / `SRP640302`, 12 FFPE EMC BioSamples) and is not a drop-in fourth
   arm, its experiment title saying targeted TempO-Seq while its `library_strategy` field says
   RNA-Seq and the panel is named nowhere in its metadata.
2. **No pooling.** 3SEQ read density, single-channel intensity and two-colour log-ratio are not the
   same quantity, so the concordance in §3.5–3.7 is sign agreement across three independent
   measurements rather than a combined estimate.
3. **Transcript, not protein**, with *SGK1* as the worked example: its published protein and
   transcript directions oppose.
4. **No occupancy, and therefore no causality from the fusion.** The class-A assays were performed in
   engineered human fibroblasts, in rat chondrogenic cells, and with a chimera (TFG::NR4A3) that is
   not the common one.
5. **The normal arm is a six-organ tissue panel**, not matched adjacent tissue, so it cannot separate
   EMC-specific from mesenchymal-lineage-specific.
6. **Comparator arms differ between platforms**, and the strata are small (6 desmoids, 3 DFSP, 3
   GIST), so a stratified contrast at n = 3 comparators can report no p below 0.0035 however large
   the effect.
7. **Fusion type is unrecorded in every series**, so each EMC arm mixes EWSR1::NR4A3 with whatever
   TAF15::NR4A3 and rarer variants it contains.
8. **Multiple testing is corrected for the per-gene permutation results only**, which is why §3.5
   reads the stratified panel on its least favourable stratum.
9. **The size-matched null is competitive and carries no inter-gene correlation term.** It is
   anticonservative for coherent sets by a factor computed in §2.3.2 and reported beside every set
   score; the permutation null is self-contained but cannot make three genes into more than three.
   The two disagree for *SEMA3C*, which is reported rather than reconciled.
10. **GPL3290 is relative**, spans two reference pools (§3.4), and maps probes to symbols through an
    EST accession bridge, so a gene unreadable there may be absent from the bridge rather than from
    the array.
11. **The 3SEQ rows are medians over very few peaks** (2, 3 and 5), and the percentile calibration is
    a rank within one deposit, not a test.
12. **The covariate adjustment is a sensitivity analysis, not a correction**: if a panel gene is
    itself driven by the fusion the adjustment removes real signal.
13. **The muscle control bounds differentiated-muscle admixture only**, and one of its four markers
    (*MYH7*) is also a class-B row of this paper's own catalogue.
14. **The motif scan speaks to sequence, never to occupancy**, is restricted to a fixed window, and
    does not reproduce the published site coordinates for either *ENO3* or *PPARG*.
15. **No efficacy, selectivity, safety, therapeutic-window or clinical-readiness claim** is made for
    any agent, target or gene, and expression data cannot become that evidence.
16. **The occupancy axis is measured on the wrong protein or the wrong disease in every experiment**,
    so §3.8 is not evidence that these genes are unbound by the fusion.
17. **The positive control and the surviving result are the same gene.** *ENO3* was designated the
    positive control before any biological read (§2.4) and survives every subsequent test, so its
    elevation in EMC is not an independent finding of this work. The observation that would remove
    the weakness is a gene other than *ENO3* clearing the same bar.
18. **The empirical null's own resolution is bounded**: its 97.5th percentile moves by a relative
    standard deviation of 1.6–3.1% across draw seeds, its pool is a 4,000-symbol subsample whose
    composition error is not bounded here, and the aggregate negative is marginal under one of the
    four composition-matched nulls (§3.7).

---

## 6 · Conclusion

The published direct-target catalogue of the EWSR1::NR4A3 fusion is three genes wide, and in the
available EMC expression record none of the three is separable from disease association. The 19-gene
aggregate reaches 39% and 88% of its size-matched threshold and does not clear it, while a published
EMC expression signature selected on an EMC-versus-sarcoma contrast clears the same threshold
11.9-fold and 4.2-fold on the same instrument in the same run. Applied per gene, the calibration
separates what is otherwise treated alike: *ENO3* is elevated on both readable array platforms under
an exact permutation test and after multiple-testing correction, against every comparator stratum
separately, with a skeletal-muscle admixture control that does not explain it; *PPARG*'s strongest
reading is circular and what remains does not survive correction; *SEMA3C* survives none of these
tests and changes sign with the choice of comparator. *ENO3* was also the pre-designated positive
control, so its elevation is not an independent finding of this work (Limitation 17).

The binding constraint on the biology is not sample size and not statistics. It is that class A is
three genes wide, and that no experiment has measured where an NR4A3 fusion binds, or what chromatin
does, in EMC material, which is a bounded statement about what has been deposited under a label an
archive indexes rather than a claim that no such data exists anywhere. The one genome-wide chromatin
readout that carries NR4A3 fusions at all reads accessibility in HEK293T; nor can the existing NR4A
chromatin data stand in for it, since across 110 peak sets no class-A gene carries occupancy beyond a
background panel. The field performs this experiment routinely for the sibling fusions and has never
performed it on EMC material. Until it is performed, "up in EMC" and "driven by the fusion" cannot be
told apart for any gene named here, *ENO3* included, and no further correlative re-analysis of these
deposits will substitute for it.

---

## Data and code availability

All primary data are public and no new data were generated. Every analysis is CPU-only and reproduces
without a login, a rental or a GPU.

**Public datasets.**

| accession | platform | source | primary publication |
|---|---|---|---|
| GSE24369 | GPL6244 | NCBI GEO | linked series PubMed identifier 21536545 |
| GSE4303 | GPL3290 | NCBI GEO | Subramanian *et al.*, *J Pathol* 2005;206:433–444 (PMID 15920699) |
| GSE28866 | 3SEQ / GPL10999 | NCBI GEO series supplementary peak tables | Brunner *et al.*, *Genome Biol* 2012;13(8):R75 (PMID 22929540) |

Gene-set libraries are served through Enrichr (Kuleshov *et al.*, 2016): `ChEA_2022`,
`TRRUST_Transcription_Factors_2019`, `TF_Perturbations_Followed_by_Expression` and
`MSigDB_Hallmark_2020`. Each term used is pinned verbatim in the code. Referenced but not used as
data: Haller *et al.* (2019) NR4A3 ChIP-seq, processed data Zenodo doi 10.5281/zenodo.1483691 (open),
raw data EGA EGAS00001002795 (controlled access); §4.3 states why it does not answer this question.
The NR4A ChIP-seq census of §3.8 reads public ChIP-Atlas and ReMap2022 records, including GSE186199.

**Code and derived artifacts.** All are openly available in the project repository
(https://github.com/trimcrae/rare-cancers), which will be archived to Zenodo with a citable DOI at
submission, and the DOI added to this section at that point.

| artifact | producer |
|---|---|
| `nr4a3-fusion-targets.json`: evidence table, global offsets, null calibrations, per-gene and per-set scores, controls, circularity grade | `nr4a3_fusion_targets.py` |
| `nr4a3-fusion-targets-review-sensitivity.json` — the closed-form check of the null, inter-gene correlation and variance-inflated thresholds, set D without the genes shared with set E, per-gene-missingness size-1 nulls, seed sensitivity, composition-matched nulls, the *t*-scale null, permutation confidence intervals and detectability, muscle-marker nulls, and the B1/B2 split | `nr4a3_fusion_targets_review_sensitivity.py` |
| `emc-expression-panels.json`, field `gene_reads`: the independent second implementation of the per-gene array reads | `emc_expression_panels.py` |
| `gse28866-tumour-vs-normal.json`, fields `per_gene.values` and `ratio_calibration`: the 3SEQ arm and its percentile calibration | `gse28866_tumour_vs_normal.py` |
| `nr4a3-fusion-targets-robustness.json` — exact label-permutation p-values, leave-one-out jackknife, rank-based re-read and BH q-values | `nr4a3_fusion_targets_robustness.py` |
| `nr4a3-fusion-targets-confounds.json` — comparator composition, the muscle-admixture control, every stratified and reference-pool-matched contrast with its own exact permutation p, the covariate-adjusted sensitivity analysis, minimum detectable effects, and the within-EMC axis | `nr4a3_fusion_targets_confounds.py` |
| `nr4a3-fusion-targets-occupancy.json` — NR4A ChIP-seq occupancy at the class-A genes across 110 peak sets, each count calibrated against a 198-gene background panel | `nr4a3_fusion_targets_occupancy.py` |
| `figures/fig1`–`fig5` (PNG + PDF) and `figures/figure-provenance.json` | `nr4a3_fusion_targets_figures.py` |
| `emc-ret-target-scan.json`, field `part_1_nbre_scan`: NBRE and NurRE counts, the dinucleotide-preserving shuffle null and the background-panel ranks | `emc_ret_target_scan.py` |
| `gene-set-null-prior-art.json` — the Europe PMC records for the gene-set-testing prior art cited in §2.3.1 | `.github/workflows/fetch-literature.yml`, query path |
| offline arithmetic guards | `tests/test_nr4a3_fusion_targets.py`, `tests/test_nr4a3_fusion_targets_confounds.py`, `tests/test_nr4a3_fusion_targets_figures.py` |

The null draw is seeded (20260807) and the pool size, seed and universe are recorded per platform, so
every empirical p is reproducible from the committed code and the public accessions alone. Each
producer re-derives its inputs and refuses to write if any row disagrees with the artifact that owns
it; the figure generator stamps the content hash of every artifact it read.

## Funding

None.

## Conflicts of interest

The author declares no competing interests.

## Ethics approval and consent

Ethics approval was not required. This study analysed only publicly available, de-identified gene-expression deposits and
generated no new human or animal data. No individual is identifiable from anything reported here.

## Author contributions

T.D.M. is the sole author and is responsible for the study design, analysis, interpretation and
manuscript.

## Use of generative AI

This work was carried out with the assistance of a large language model–based research agent (Claude,
Anthropic), used for literature extraction, analysis code, statistical computation and manuscript
drafting. All analyses are executed by committed, deterministic, independently re-implemented and
offline-reproducible code (see Data and code availability), and were reviewed by the author, who takes
full responsibility for the content. No AI tool is listed as an author, in accordance with journal
policy.

## Acknowledgements

None.

---

## References

1. Brenca M, Stacchiotti S, Fassetta K, et al. NR4A3 fusion proteins trigger an axon guidance switch
   that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas.
   *J Pathol* 2019;249(1):90–101. PMID 31020999; PMCID PMC6766969; doi 10.1002/path.5284.
2. Brunner AL, Beck AH, Edris B, et al. Transcriptional profiling of long non-coding RNAs and novel
   transcribed regions across a diverse panel of archived human cancers. *Genome Biol* 2012;13(8):R75.
   PMID 22929540; doi 10.1186/gb-2012-13-8-r75.
3. Ferran B, Marti-Pamies I, Alonso J, et al. The nuclear receptor NOR-1 regulates the small muscle
   protein, X-linked (SMPX) and myotube differentiation. *Sci Rep* 2016;6:25944. PMID 27181368;
   PMCID PMC4867575.
4. Filion C, et al. The PLAGL1 gene is down-regulated in human extraskeletal myxoid chondrosarcoma
   tumors. *Cancer Lett* 2005. PMID 16112421; doi 10.1016/j.canlet.2004.12.007.
5. Filion C, Motoi T, Olshen AB, et al. The EWSR1/NR4A3 fusion protein of extraskeletal myxoid
   chondrosarcoma activates the PPARG nuclear receptor gene. *J Pathol* 2009;217(1):83–93. PMID 18855877;
   PMCID PMC4429309; doi 10.1002/path.2445.
6. Frenkel M, Corban JE, Hujoel MLA, Morris Z, Raman S. Large-scale discovery of chromatin
   dysregulation induced by oncofusions and other protein-coding variants. *Nat Biotechnol*
   2025;43(6):996–1010. PMID 39048711; PMCID PMC13105821; doi 10.1038/s41587-024-02347-4.
7. Haller F, et al. Enhancer hijacking activates oncogenic transcription factor NR4A3 in acinic cell
   carcinomas of the salivary glands. *Nat Commun* 2019;10:368. PMID 30664630; PMCID PMC6341107.
8. Kim AY, Lim B, Choi J, Kim J. The TFG-TEC oncoprotein induces transcriptional activation of the human
   beta-enolase gene via chromatin modification of the promoter region. *Mol Carcinog* 2016.
   PMID 26310886; doi 10.1002/mc.22384.
9. Labelle Y, et al. Serum- and glucocorticoid-regulated kinase 1 (SGK1) induction by the EWS/NOR1(NR4A3)
   fusion protein. *Biochem Biophys Res Commun* 2006. PMID 16756948; doi 10.1016/j.bbrc.2006.05.134.
10. Labelle Y, Zucman J, Stenman G, et al. Oncogenic conversion of a novel orphan nuclear receptor by
    chromosome translocation. 1995. PMID 8634690. *(The cloning of the EMC fusion; the date under §1.2.)*
11. Subramanian S, West RB, Marinelli RJ, et al. The gene expression profile of extraskeletal myxoid
    chondrosarcoma. *J Pathol* 2005;206:433–444. PMID 15920699; doi 10.1002/path.1792. *(The EMC
    expression cohort. Distinct from reference 21, Subramanian et al. 2005 PNAS, which is GSEA.)*
12. Zhao X, Min X, Wang Z, et al. NR4A3 inhibits the tumor progression of hepatocellular carcinoma by
    inducing cell cycle G0/G1 phase arrest and upregulation of CDKN2AIP expression. *Int J Biol Sci*
    2024. PMID 39664575; PMCID PMC11628324; doi 10.7150/ijbs.95174.
13. Wilson TE, Fahrner TJ, Johnston M, Milbrandt J. Identification of the DNA binding site for NGFI-B
    by genetic selection in yeast. *Science* 1991;252:1296–1300. PMID 1902986. *(The NBRE.)*
14. Philips A, Lesage S, Gingras R, et al. Novel dimeric Nur77 signaling mechanism in endocrine and
    lymphoid cells. *Mol Cell Biol* 1997;17:5946–5951. PMID 9315667. *(The NurRE.)*
15. Welch BL. The generalisation of student's problems when several different population variances are
    involved. *Biometrika* 1947;34:28–35. PMID 20287819; doi 10.1093/biomet/34.1-2.28.
16. Goeman JJ, Bühlmann P. Analyzing gene expression data in terms of gene sets: methodological issues.
    *Bioinformatics* 2007;23(8):980–987. PMID 17303618; doi 10.1093/bioinformatics/btm051.
17. Irizarry RA, Wang C, Zhou Y, Speed TP. Gene set enrichment analysis made simple. *Stat Methods Med
    Res* 2009;18:565–575. PMID 20048385; doi 10.1177/0962280209351908.
18. Rivals I, Personnaz L, Taing L, Potier MC. Enrichment or depletion of a GO category within a class of
    genes: which test? *Bioinformatics* 2007;23:401–407. PMID 17182697; doi 10.1093/bioinformatics/btl633.
19. Wu D, Smyth GK. Camera: a competitive gene set test accounting for inter-gene correlation. *Nucleic
    Acids Res* 2012;40(17):e133. PMID 22638577; PMCID PMC3458527; doi 10.1093/nar/gks461.
20. Wu D, Lim E, Vaillant F, et al. ROAST: rotation gene set tests for complex microarray experiments.
    *Bioinformatics* 2010;26(17):2176–2182. PMID 20610611; PMCID PMC2922896;
    doi 10.1093/bioinformatics/btq401.
21. Subramanian A, Tamayo P, Mootha VK, et al. Gene set enrichment analysis: a knowledge-based approach
    for interpreting genome-wide expression profiles. *Proc Natl Acad Sci U S A* 2005;102(43):15545–15550.
    PMID 16199517; PMCID PMC1239896; doi 10.1073/pnas.0506580102. *(GSEA. Distinct from reference 11.)*
22. Foroutan M, Bhuva DD, Lyu R, Horan K, Cursons J, Davis MJ. Single sample scoring of molecular
    phenotypes. *BMC Bioinformatics* 2018;19(1):404. PMID 30400809; PMCID PMC6219008;
    doi 10.1186/s12859-018-2435-4.
23. Hänzelmann S, Castelo R, Guinney J. GSVA: gene set variation analysis for microarray and RNA-seq
    data. *BMC Bioinformatics* 2013;14:7. PMID 23323831; PMCID PMC3618321; doi 10.1186/1471-2105-14-7.
24. Barbie DA, Tamayo P, Boehm JS, et al. Systematic RNA interference reveals that oncogenic KRAS-driven
    cancers require TBK1. *Nature* 2009;462(7269):108–112. PMID 19847166; PMCID PMC2783335;
    doi 10.1038/nature08460. *(ssGSEA.)*
25. Tirosh I, Izar B, Prakadan SM, et al. Dissecting the multicellular ecosystem of metastatic melanoma
    by single-cell RNA-seq. *Science* 2016;352(6282):189–196. PMID 27124452; PMCID PMC4944528;
    doi 10.1126/science.aad0501. *(Expression-bin-matched control gene sets.)*
26. Phipson B, Smyth GK. Permutation P-values should never be zero: calculating exact P-values when
    permutations are randomly drawn. *Stat Appl Genet Mol Biol* 2010;9:Article39. PMID 21044043;
    doi 10.2202/1544-6115.1585.
27. Geistlinger L, Csaba G, Santarelli M, et al. Toward a gold standard for benchmarking gene set
    enrichment analysis. *Brief Bioinform* 2021;22:545–556. PMID 32026945; doi 10.1093/bib/bbz158.
28. Benjamini Y, Hochberg Y. Controlling the false discovery rate: a practical and powerful approach to
    multiple testing. *Journal of the Royal Statistical Society Series B*, 1995. *(Volume and pages to be
    completed from the primary source before submission; the journal is not indexed by Europe PMC and no
    identifier is asserted here.)*
29. Efron B, Tibshirani R. On testing the significance of sets of genes. *Annals of Applied Statistics*,
    2007. *(Restandardization. Volume and pages to be completed from the primary source before
    submission; the journal is not indexed by Europe PMC and no identifier is asserted here.)*

*Gene-set resources* are cited to the depth their source records supply (author, journal and year only;
full bibliographic identifiers to be completed against the primary sources before submission): Enrichr —
Kuleshov et al., *Nucleic Acids Research* 2016; ChEA — Lachmann et al., *Bioinformatics* 2010; TRRUST v2
— Han et al., *Nucleic Acids Research* 2018; MSigDB Hallmark collection — Liberzon et al., *Cell Systems*
2015. The GSE24369 GEO record links series PubMed identifier 21536545 and is cited throughout by
accession.

*Note on citation provenance.* Every identifier in this reference list is reproduced from a source held
in the project repository: the machine-readable target catalogue, the set-definition blocks, an existing
curated reference list, or (for references 15–27) `research/literature/gene-set-null-prior-art.json`, the
Europe PMC records retrieved on 2026-08-10 for exactly this purpose. References 28 and 29 carry no
identifier because none could be retrieved, and completing them from the primary source is a
pre-submission task. Author names and titles are given only to the depth the source supplies them.

---

## Appendix A · Superseded values and corrected claims

*Repository record, removed at submission along with the YAML frontmatter. Retained so that a
superseded number stays quotable as history and not as a current fact.*

| claim, as previously written | status | what replaced it |
|---|---|---|
| Title: "Almost every gene set reads higher in the index arm: a size-matched empirical null for small rare-tumour expression series, and what it leaves of the EWSR1::NR4A3 direct-target catalogue", with §1.1 leading on the calibration and the abstract's "We supply the calibration that refuses such a read". | **superseded 2026-08-10** | The size-matched empirical null is a competitive gene-set null of a standard kind, and the paper cited no prior art for it. Measured against the artifact, it is additionally an **independence** null: `null_sd × sqrt(n)` is constant to within 5.9% across set sizes 10–250 on both platforms, so the band is `offset ± 1.96 σ/√n` to within 3–13% on GPL3290 and 14–36% on GPL6244. Retitled around the disease result; §2.3.1 now positions the null against Goeman and Bühlmann, CAMERA, ROAST, restandardization, `singscore`, GSVA/ssGSEA and expression-binned control sets; the only claimed novelty is the fraction-of-threshold reporting convention. |
| "an arbitrary **19-gene** set on GPL3290" with band [−0.297, +0.376], in the abstract, §1.1 and §3.4; and `t = 3.16` described as that arbitrary set's. | **corrected 2026-08-10** | The artifact records `set_size: 17` for that band, because only 17 of the 19 A+B genes are readable on GPL3290 (*ICAM1* and *MYH7* are not); Figure 1 and Supplementary Table S2 already said 17. The `t = 3.16` is this paper's own A+B aggregate (`t = 3.159`), not an arbitrary set, and the null was computed over Δ rather than over *t*. The null distribution of *t* has since been computed at the same size: the 95% band is [−3.31, +4.35] and 9.9% of random 17-gene sets print a larger \|t\|. |
| "**Five of the six** control × platform cells carried a computable contrast, and all five agree." | **corrected 2026-08-10** | Four controls on two platforms are **eight** cells. Seven are computable, six gradeable, six agreeing, none disagreeing; four of the six agreements are outside-band readings that could have refused their prediction. ⚠ This sentence had already been corrected once, from "Four of four graded controls agree"; that correction replaced one wrong count with another. |
| "reached 39% and 88% of threshold" and "11.9× / 4.2×", quoted without a resolution. | **qualified 2026-08-10** | The figures are unchanged and remain the committed artifact's. What is added is their resolution: an independently implemented resampler under 20 further seeds gives a 97.5th-percentile relative standard deviation of 1.6–3.1%, and the committed percentile sits 2.9% above the mean of those 20 draws, so a fraction-of-threshold figure carries a few points of Monte-Carlo uncertainty (Limitation 18). Where the reduced set D is compared with the full one, both are scored in the same resampler so the comparison is like for like (11.5× against 10.6× on GPL6244; 4.1× against 2.7× on GPL3290). |
| "*ENO3*'s **one** nominally significant value" in the occupancy paragraph, in the same clause as "2 hits in 36 tests". | **corrected 2026-08-10** | The artifact gives *ENO3* **two** nominally significant values, p = 0.0348 (normal parotid gland, NR4A3) and p = 0.0498 (`SRX1653203`, NR4A1), and gives *PPARG* and *SEMA3C* none. Both of the two hits are *ENO3*'s. |
| "2 of 36 gene-by-experiment tests reach p < 0.05 against 1.8 expected by chance — a **binomial p of 0.54**." | **withdrawn 2026-08-10** | A binomial tail requires uniform, independent p-values and has neither: these are ranks within a 198-gene panel of small integer peak counts, heavily tied (*PPARG* returns exactly 1.00 in 11 of 12 experiments), and the 36 tests share three genes, one panel and overlapping peak sets. The raw counts against the panel column are reported instead. The permutation null that would replace it needs the panel's per-gene peak counts, which the deposited artifact does not carry. |
| "so do **three markers** that are more muscle-restricted than it is — *ACTA1*, *MYH7*, *PYGM*, *MYL1*" and "none of them separates the tumour arms". | **corrected 2026-08-10** | Four markers, and one of them moves: *PYGM* at +0.142, about 45% of *ENO3*'s +0.315. All four have since been put through the same size-1 null the class-A genes face and all four fall inside their band, while *ENO3* falls outside it. |
| Set D described as "an INDEPENDENT replication set: it comes from neither readable series", and its clearance as showing "the instrument reads this disease, not this set". | **corrected 2026-08-10** | Set D was selected as the 25 probe sets most over-expressed in EMC versus other sarcomas, so scoring it on another EMC-versus-sarcoma contrast is a winner's-curse replication; it is relabelled a positive control selected on the same contrast. It also shares *DKK1*, *MAN1A1* and *NMB* with set E, which is derived from the GPL3290 cohort itself, so 3 of its 18 GPL3290-readable genes are not independent of that platform. Without them the clearance is 10.6-fold and 2.7-fold. |
| "a **bounded negative, not an underpowered one**." | **withdrawn 2026-08-10** | The producing artifact's own guard says the fraction-of-threshold figure is a detectability threshold and not a power calculation. Replaced by an interval: the aggregate's delta with an exact label-permutation 95% confidence interval, and the smallest shift the design would place outside the band with 80% probability. |
| "the top 2% of **14,120** genes" (§3.7, §3.12, §6). | **corrected 2026-08-10** | 14,120 is the deposit's gene count; the percentile ranks within the **13,708** genes with a computable EMC/normal ratio (13,247 on the sarcoma axis). |
| "42–70% of their citations come from EMC records, and each is cited by four to six EMC reviews." | **corrected 2026-08-10** | The committed probe supports 42% (Filion), 54% (Subramanian) and 33% (Kim); Brenca's total-citation query executed and returned no count, so no share is available for it and the upper bound of 70% traces to nothing. The EMC-review counts are 4, 6 and 0, with Brenca at 5 — and Kim, the source of the surviving gene, at zero, which the earlier range concealed. |
| Table 2 "42,000-spot"; §3.9 heading "12-fold"; §3.3 "matches to **four** decimal places". | **corrected 2026-08-10** | 43,008 probes, as measured; 11.9-fold, matching the body; three decimal places, since the two implementations give +0.8075 and +0.8074 on GPL6244. |
| "That pattern is the shape of a platform-wide offset." | **superseded 2026-08-07** | The global offset is −0.0084 SD (GPL6244) and +0.0258 SD (GPL3290), an order of magnitude below the effects in question. The mechanism is null-band width at these arm sizes, not offset (§3.4). |
| GSE24369's comparator arm described as containing "6 fibrosarcoma", and the comparators as "dense". | **corrected 2026-08-08** | The GEO titles are `Myxofibrosarcoma 1–6`; 23 of 29 comparators are myxoid (§2.2). The producing artifact's `class_counts` still carries the internal label `fibrosarcoma: 6` and Supplementary Table S5's column heading is annotated accordingly. |
| "*PPARG* … significant on one platform" reported as independent support. | **corrected 2026-08-08** | *PPARG* on GPL3290 is circular: GSE4303 is the cohort from which high *PPARG* in EMC was published (§3.6). |
| Every `p_emp = 0.0005` written as an equality. | **corrected 2026-08-08** | 0.0005 is the resolution floor of a 4,000-draw two-sided null (2/4001) and is written `≤ 0.0005` (§2.3). |
| "Deep NR4A1 sets (ReMap2022) do recover both *SEMA3C* and *ENO3*", offered as a near-miss worth noting. | **corrected 2026-08-08** | True and uninformative: 82.8% of a 198-gene background panel is also recovered by that catalogue. |
| A background citation attributing the cloning of the EMC fusion to a 1995 paper. | **withdrawn, then re-anchored 2026-08-08** | The original PMID traced to no held source and was written from recollection. The cloning paper is now retrieved rather than recalled (PMID 8634690, reference 10). |
| "Two questions are routinely conflated" (§1.3) and "the field's prose does not usually say so" (§4.2). | **superseded 2026-08-08** | Both asserted what a literature does, and neither had been measured. Measured: the three class-A genes are named in 3, 1 and 0 of 261 EMC review records. The true state is a near-absence of any account, not a mistaken one. |
| "All twelve NR4A3-specific peak sets are too shallow to recover any gene at all", and the occupancy axis reported across **86** peak sets, **8** informative experiments and **24** tests. | **superseded 2026-08-08** | Still true of the twelve ChIP-Atlas sets and stated of them, but no longer of the axis: the Haller deposit adds four NR4A3 cistromes at 8,501–18,666 peaks. The axis is 110 peak sets, 12 informative experiments and 36 tests. |
| "No genome-wide chromatin experiment performed with an NR4A3 fusion was retrieved in 2,276 full-text documents across five corpora", read in §3.11, §4.2, §6, the abstract and the cover letter as an absence. | **retracted 2026-08-08** | The corpus count is unchanged and was never wrong. What is retracted is the inference from that screen to an absence: a wider search the same day retrieved GEO GSE243553 (PMID 39048711), a pooled single-cell ATAC screen in HEK293T carrying four NR4A3 fusions with wild-type and reciprocal controls. The replacement claim is narrower and is what the paper now carries: no experiment has measured where an NR4A3 fusion binds, or what chromatin does, in EMC material. |
| §3.10's caveat "only a chromatin experiment shows binding, and §3.11 records that none exists for any NR4A3 fusion." | **superseded 2026-08-08** | The second clause inherited the retracted absence. The four exact NBREs were intersected with GSE243553's per-fusion accessibility calls on the matching build: three of four sites fall inside TAF15-NR4A3's intervals and none inside EWSR1-NR4A3's, and neither observation supports the motif argument. Nulls treating the four sites as independent return p ≤ 0.002 and overstate the result about forty-fold; the geometry-preserving null gives p = 0.08. |
| §3.13: "Within that reach, no fourth EMC expression cohort exists", and "the three cohorts analysed here are the available public EMC transcriptional record". | **narrowed 2026-08-08** | The search was GEO-side. `PRJNA1357027` / `SRP640302` is public in the Sequence Read Archive with 12 FFPE EMC tumour BioSamples and no GEO mirror. Limitation 1 is unchanged for the analyses this paper runs, because the deposit is TempO-Seq targeted-panel data whose panel is named nowhere in its metadata. |
