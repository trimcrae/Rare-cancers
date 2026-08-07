---
id: DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT
title: "Published transcriptional targets of EWSR1::NR4A3 are elevated in extraskeletal myxoid chondrosarcoma tissue across three cohorts and three platforms: an evidence-typed, null-calibrated re-analysis"
level: L3
kind: manuscript
status: live
canonical_for: ["the evidence-typed catalogue of published NR4A3 / NR4A3-fusion transcriptional targets", "the null-calibrated instrument for reading a gene set in the readable EMC expression series", "the cross-platform concordance reading of the class-A fusion target genes"]
purpose: >
  A submission-formatted report of one question: do the genes an NR4A3 chimera is published to bind
  read higher in EMC tumour tissue than in comparator tumours, once the reading is calibrated
  against a size-matched random gene set on the same platform? It enumerates, with the evidence
  type recorded per gene, every gene any primary paper claims an NR4A3 fusion or native NR4A3
  transcriptionally activates; states what would discriminate the fusion DRIVING a gene from the
  gene merely being high in EMC; and reports the measurement in three independent cohorts on
  three platform families.
scope: >
  Transcriptional output of the EMC fusion, at transcript level, in bulk tumour tissue. Asserts
  nothing about efficacy, selectivity, safety, a therapeutic window or clinical readiness for any
  agent, target or gene named, and no such quantity is computed. Says nothing about whether NR4A3
  is druggable, and nothing about the direction of any pharmacological intervention.
audience: [maintainers, external reviewers, autonomous research agents]
related: [DOC-GSE28866-READING, DOC-PPARG-DIRECTION-EMC]
date: 2026-08-07
last_verified: 2026-08-07
---

<!--
REPOSITORY NOTE (not part of the manuscript): the YAML block above is repository metadata read by
the systems checks; it is stripped at submission. Everything from the title below is the manuscript
proper, written so an external reader can reproduce it without reading this repository. Every figure
is derived from a committed artifact (see Data and code availability) and reproduces with
`python3 research/modalities/nr4a3_fusion_targets.py --check`. Purely operational notes (staged
graph records, proposed map-edits, cross-lane coordination) have been moved to
nr4a3-fusion-transcriptional-output-repo-notes.md so they are preserved without appearing in the paper.

SUBMISSION STATUS: submission-ready draft, not yet submitted.
  Primary target : Genes, Chromosomes & Cancer (Wiley) — Original Research Article (subscription/$0 route)
  Alternatives   : The Journal of Pathology (Wiley); British Journal of Cancer (Springer Nature)
  Preprint       : bioRxiv (Cancer Biology / Genomics), free open copy
  Furniture      : nr4a3-fusion-transcriptional-output-cover-letter.md,
                   nr4a3-fusion-transcriptional-output-submission-checklist.md
-->

# Published transcriptional targets of EWSR1::NR4A3 are elevated in extraskeletal myxoid chondrosarcoma tissue across three cohorts and three platforms: an evidence-typed, null-calibrated re-analysis

**Running title:** EWSR1::NR4A3 targets in EMC tissue, null-calibrated

**Author:** Tristan D. McRae¹

¹ Independent Researcher. Correspondence: trimcrae@gmail.com

**Article type:** Original Research Article
**Keywords:** extraskeletal myxoid chondrosarcoma; EWSR1::NR4A3; NR4A3; transcriptional target; empirical null; gene-set calibration; rare sarcoma

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is a rare translocation sarcoma usually driven by the
EWSR1::NR4A3 fusion. The fusion is presumed to act as an aberrant transcription factor, yet the set of
genes any NR4A3 chimera is shown to bind and drive is small, and whether they are elevated in EMC
tissue has not been tested against a calibration for what an arbitrary set of the same size does on the
same platform — without which almost every set scores "higher in EMC". We
catalogued every primary-literature claim that an NR4A3 fusion or native NR4A3 transcriptionally
activates a named gene, recording evidence type, assay, cell system and species, and scored the
resulting genes in three independent EMC cohorts on three platform families (GSE24369/GPL6244;
GSE4303/GPL3290; GSE28866/3SEQ). Each array contrast was calibrated against a size-matched empirical
null, and four instrument controls, including a directional falsifier with a published *down*
prediction, were graded before any biology was read under a decision rule fixed in advance. The
direct-target set with a fusion DNA-binding assay behind it is three genes wide (*SEMA3C*,
*PPARG*, *ENO3*). All three are positive-signed on both array platforms (six of six readings) and higher
in EMC than in both comparator arms of the independent 3SEQ cohort, each clearing its single-gene null
on at least one platform; the aggregate set does not clear its null, while the published EMC
transcriptional phenotype replicates at p = 0.0005 on both. Under an exact sample-label permutation
test, *ENO3* survives multiple-testing correction on both platforms and *PPARG* on one, whereas
*SEMA3C* does not reach significance on either; no row changes sign when any single EMC tumour is
dropped. No genome-wide chromatin experiment with an NR4A3 fusion was found in 2,276 full-text
documents, so "elevated in EMC" and "driven by the fusion" cannot yet be separated.

---

## 1 · Introduction

### 1.1 · The disease and the driver

EMC is a rare soft-tissue sarcoma defined by rearrangement of *NR4A3* (NOR-1/TEC). Subramanian *et al.*
describe it as "characterized by a balanced translocation most commonly involving t(9;22) (q22;q12)"
(PMID 15920699), which produces EWSR1::NR4A3; Brenca *et al.* express and assay both that chimera and
TAF15::NR4A3, "the commonest TAF15 (exons 1–6)–NR4A3 (exons 3–8) fusion" (PMID 31020999), with a
rarer *t(3;9)(q11-12;q22)* TFG::NR4A3 variant accounting for part of the remainder. NR4A3 is an orphan
nuclear receptor, and the chimera places its DNA-binding domain under a strong FET-family
transactivation domain. The disease's central molecular hypothesis is therefore straightforward: the
fusion is a transcription factor with an aberrant output, and that output is where the disease lives.

### 1.2 · The gap this addresses

The hypothesis is thirty years old, and the evidence under it is thin in a specific, checkable way.
Two questions are routinely conflated:

1. Which genes has anyone shown an NR4A3 chimera to physically bind and drive?
2. Which genes are high in EMC tumours?

The first is a mechanism claim; the second is an association. A gene can satisfy the second for reasons
that have nothing to do with the fusion — EMC's cell of origin, its myxoid and hypocellular
architecture against dense comparator sarcomas, or the gene being a generic matrix or proliferation
gene. This work separates the two by (a) cataloguing the mechanism claims with their evidence type
recorded per gene, and (b) reading them back in tumour tissue with an explicit calibration for what an
arbitrary gene set does on the same platform.

### 1.3 · Why the calibration is the load-bearing part

On GSE4303/GPL3290, almost every gene set anyone scores comes back "higher in EMC" — PPARγ targets,
hypoxia metagenes, adipogenesis, chondroitin-sulfate biosynthesis, arginine metabolism. Sets with no
biological relationship to one another move the same way and by similar amounts. A raw Welch contrast
on the sample means uses the samples as its unit of variability and ignores that a set's per-sample
score is one draw from a distribution whose width depends on the set's *size* and on the platform. At
n = 10 versus 6, that width is large: the 95% band for an arbitrary 19-gene set on GPL3290 is
[−0.297, +0.376] SD, so a set can print t = 3.16 and remain indistinguishable from a random set of the
same size. No read on these platforms is interpretable until it is calibrated against a size-matched
random gene set drawn from the same platform's own genes. That calibration is the instrument this work
supplies, and it is applied to the work's own headline result.

---

## 2 · Materials and Methods

### 2.1 · The evidence-typed target catalogue

Every claim in the primary literature that EWSR1::NR4A3, another NR4A3 fusion, or native NR4A3
transcriptionally activates a named gene was recorded with: the gene, the factor actually tested, the
assays, the cell system, the species of those cells, the expected direction in EMC, and the verbatim
sentence the classification rests on. Rows were read from retrieved full text, not from memory. Four
evidence classes were assigned per row:

| class | definition |
|---|---|
| **A** — fusion DNA-binding | a DNA-binding or promoter assay performed **with an NR4A3 fusion**. The strongest class. |
| **B** — native DNA-binding | the same assay class with **native NR4A3**. Transfer to the fusion is an assumption. |
| **C** — fusion expression only | the gene moves when the fusion is expressed; no binding assay. |
| **D** — EMC tumour expression only | measured in EMC tissue; no mechanism. |

### 2.2 · Datasets

Three independent EMC cohorts on three platform families were used. They are never pooled (§5).

| cohort | platform | EMC | comparators | value kind |
|---|---|---|---|---|
| **GSE24369** | GPL6244, Affymetrix Gene ST | 6 | 29 — 17 FET-rearranged LGFMS + 6 desmoid fibromatosis + 6 fibrosarcoma | single-channel intensity |
| **GSE4303** | GPL3290, 42,000-spot two-colour cDNA | 10 | 6 (3 DFSP + 3 GIST) | two-colour log-ratio vs a reference pool |
| **GSE28866** | 3SEQ (GPL10999) | 4 | 32 non-EMC sarcoma libraries; 27 normal-organ libraries | 3′-end read density per peak |

- **GSE24369** — its comparator arm is itself FET-rearranged (LGFMS is *FUS::CREB3L2*), so a difference
  here is not merely "has a FET fusion". The array carries 42 samples; 6 EMC + 29 comparators accounts
  for 35, and the remaining 7 are unclassified and are excluded from the comparator arm rather than
  silently absorbed into it, so the arithmetic closes. Linked series PubMed identifier 21536545.
- **GSE4303** — Subramanian *et al.*, *J Pathol* 2005;206:433–444 (PMID 15920699). See §3.8 on
  circularity.
- **GSE28866** — Brunner *et al.*, *Genome Biol* 2012;13(8):R75 (PMID 22929540). The EMC libraries are
  EMC_STT5525/5526/5527/5592; the normal arm is 27 libraries across six organs (bowel, breast, colon,
  kidney, lung, uterus). The 32 non-EMC sarcoma columns include two pairs of technical replicates of
  one specimen each (ESS_STT5520, LMS_STT516), so 32 libraries come from 30 specimens.

### 2.3 · Per-gene and per-set scoring on the two array series

Probes were mapped to symbols per platform (GPL6244: 20,230 of 28,459 probes → 18,694 distinct
symbols; GPL3290: 27,203 of 43,008 probes → 14,932, through an EST-accession bridge). Each sample's
values were z-scored against that array's own probe distribution, so a per-sample score is a
within-array quantity; a gene or set score for a sample is the mean z over its readable members; the
contrast is a Welch *t* on the EMC versus comparator per-sample scores. A gene with no probe is treated
as an unread gene, never as an absent one. Floors were fixed at three samples per group for any
contrast, and four genes / 0.4 coverage for any set score; a set below the floor emits no score and
says so.

### 2.4 · The size-matched empirical null

A raw Welch contrast does not supply two quantities this work computes per platform:

1. **The exact global offset.** The per-sample mean z over every symbol the platform maps, contrasted
   EMC versus comparator. This is the amount by which an arbitrary gene set is expected to differ for
   no set-specific reason.
2. **A size-matched empirical null.** 4,000 random gene sets of exactly the observed size, drawn from a
   seeded random pool of the platform's own mapped symbols (seed 20260807; pool 4,000; universe 18,694
   for GPL6244, 14,932 for GPL3290), each scored exactly as the real set is. A random set carries the
   offset too, so the null absorbs it by construction. The empirical p is the fraction of draws at
   least as extreme, with +1/+1 smoothing.

A set is reported as SET-SPECIFIC only if the observed delta falls outside the 95% band of that null;
otherwise it is reported as not distinguishable from a random gene set of the same size on that
platform. Single genes are calibrated the same way at set size 1. The null's own limit is stated
rather than assumed: it controls for the platform-wide offset and for set *size*, but not for
gene–gene correlation inside a real pathway, which makes a coherent set's variance larger than a random
set's. The empirical p is therefore anti-conservative for coherent sets and is a screen, not a test.

### 2.5 · Instrument controls, graded before the biology

Four known answers were graded before any biological read, three of which can fail:

| control | published expectation | what it discriminates |
|---|---|---|
| ***ENO3*** | UP on both platforms | the positive control. If it fails, report the instrument, not the biology. |
| ***NR4A3*** | UP — the chimera places *NR4A3* coding sequence under the partner's promoter, and NR4A3 immunostaining is the diagnostic marker of EMC | tumour identity |
| ***PLAGL1*** | DOWN (PMID 16112421) | the directional falsifier — the only prediction an arm-wide offset cannot manufacture |
| ***SGK1*** | flat or down at transcript level, despite 10/10 protein positivity (PMID 16756948) | the only row whose published transcript and protein directions oppose |

Grading is on where the delta sits relative to its size-1 null, never on the raw delta, and *pass* is
computed only over platforms where a contrast was actually computed. A readable control with no
computable contrast (for example, *NR4A3* on GPL3290, where four of six comparator spots for that probe
are missing, leaving two values against a floor of three) is not graded — it is neither a pass nor a
failure. An absent reading is not a reading of absence, and the block whose job is to tell a working
instrument from a broken one is the last place that distinction may collapse.

### 2.6 · The 3SEQ arm

3SEQ measures 3′-end read density per peak. The supplementary peak table carries a gene-symbol column,
so gene assignment is a parse rather than a coordinate-mapping project. A gene's value in a library is
the median across that gene's peaks; an arm's value is the median across that arm's libraries. No
z-score, no test and no confidence interval are used, because n = 4. 3SEQ read density is not array
intensity, and nothing from this arm is pooled with GPL6244/GPL3290, whose z-scores and percentiles
measure a different thing.

### 2.7 · The circularity grade

Filion *et al.* (2009) publish two gene lists, and only one of them can be scored here without
circularity (§3.8). Whether GSE4303 is the Subramanian (2005) cohort was graded from the fetched GEO
series record, never from the sample counts: the record's title, summary, contributors and linked
PubMed identifier were read verbatim. If the record names PMID 15920699 or Subramanian, the verdict is
confirmed-circular and that set's score on that platform is not a test; if it does not, the verdict is
not-confirmed rather than clean; if the record could not be read, the verdict is unanswered.

### 2.8 · Pre-registration of the decision rule

The six-branch decision rule reported in §3.11 was written and committed while the measurement run was
still executing, so that the verdict could not be fitted to whatever came back. Each branch carried its
sentence, its ceiling and its next step in advance. §3.11 records which branch came true and where the
pre-registration itself fell short, rather than quietly rewriting it.

### 2.9 · Reproduction

Every value in §3 derives from a single committed artifact and is not re-typed from prose. The target
catalogue, null calibration and all array scores are produced by `nr4a3_fusion_targets.py` →
`nr4a3-fusion-targets.json`; the per-gene array reads are independently re-implemented in
`emc_expression_panels.py` → `emc-expression-panels.json`; the 3SEQ arm is produced by
`gse28866_tumour_vs_normal.py` → `gse28866-tumour-vs-normal.json`. An offline arithmetic guard, run
before any data fetch, constructs a known pure global offset and asserts the pipeline declines it, and a
known set-specific signal on the same offset and asserts it does not. All analyses are CPU-only and use
open-source tooling; the committed artifact reproduces offline via `nr4a3_fusion_targets.py --check`
(see Data and code availability).

### 2.10 · Robustness tests

The size-matched null of §2.4 is a **competitive** null: it asks whether a set is more extreme than an
arbitrary set of the same size on the same platform, which is the right question for the pervasive
"higher in EMC" pattern of §1.3, but it permutes *genes* and so cannot see gene–gene correlation. Four
further tests were therefore run, all offline from the same cached inputs, all using the same scoring
primitives so that the quantity tested is identical to the quantity reported.

1. **Exact sample-label permutation** (a **self-contained** null). The EMC/comparator label is
   permuted over samples and the *real* gene set is rescored each time, so the correlation structure is
   carried through untouched. The classified arms are 6 versus 29 on GPL6244 and 10 versus 6 on
   GPL3290, giving 1,623,160 and 8,008 distinct label assignments respectively — few enough to
   **enumerate completely**, so the reported p is an exact permutation p rather than a sampled
   estimate. Two-sided throughout.
2. **Leave-one-out jackknife** over the EMC arm: each EMC tumour is dropped in turn and the contrast
   recomputed, testing whether any single tumour carries a row.
3. **Rank-based re-read**: the same contrast recomputed on the within-array percentile instead of the
   z, which no background model and no small number of extreme probes can move.
4. **Benjamini–Hochberg** q-values across the per-gene permutation p-values within each platform.

Every row's observed delta is re-derived here and asserted equal to the committed primary artifact; the
producer refuses to write if any row disagrees. Set-level permutation p-values are reported uncorrected.

---

## 3 · Results

### 3.1 · Three genes are the whole of class A

| gene | chimera assayed | assays | cells | citation |
|---|---|---|---|---|
| **SEMA3C** | EWSR1::NR4A3 (and TAF15::NR4A3, and native) | predicted NBRE-like site (GRCh38 chr7) + ChAP-qPCR, Strep-tagged | tBJ/ER transformed human fibroblasts | Brenca *et al.*, *J Pathol* 2019;249(1):90–101 (PMID 31020999) |
| **PPARG** | EWSR1::NR4A3 (and native, and NR4A3ΔC) | predicted perfect NBRE at −675 bp, band-shift, 2.8 kb human *PPARG* promoter luciferase, single-nucleotide NBRE mutant | CFK2 fetal **rat** chondrogenic cells; human promoter construct | Filion *et al.*, *J Pathol* 2009;217(1):83–93 (PMID 18855877) |
| **ENO3** (β-enolase) | TFG::NR4A3 — *not* EWSR1 | EMSA + ChIP + luciferase, two NBRE motifs upstream of the TSS, plus ChIP for H3 acetylation at the endogenous promoter | cultured lines over-expressing TFG-TEC | Kim *et al.*, *Mol Carcinog* 2016 (PMID 26310886) |

Three genes are the whole of class A, and this is the most important number in the report. Across the
retrieved corpus, the number of genes anyone has shown an NR4A3 chimera physically binding and driving
is three — and only one of the three (*SEMA3C*) combines the EWSR1 chimera, human cells and a chromatin
assay. Three is the count in 2,276 retrieved full-text documents across five corpora (§3.10), not a
claim about all of the literature.

**Class B** — the same assay class with native NR4A3 — holds sixteen genes: *CCND1*, *SKP2*, *VTN*,
*SMPX*, *CDKN2AIP*, *GLS2*, *SDHA*, *COX5A*, *PDP1*, *VCAM1*, *ICAM1*, *BIRC3*, *NOX1*, *TH*, *LOXL2*,
*MYH7*. The strongest are *SMPX* (promoter deletion + site-directed mutagenesis + EMSA + ChIP, human
cells, PMID 27181368), *SKP2* (EMSA + ChIP) and *CDKN2AIP* (ChIP + mutation-reversed reporter, human
cells, PMID 39664575). **Class C** holds *SGK1* and *PLAGL1*; **class D** holds *NDRG2*, which Filion
*et al.* examine as a phosphorylation substrate of *SGK1* and which is therefore not a
transcriptional-target claim. A published negative control is carried alongside them: *CALD1*, whose
promoter was searched for NOR-1 response elements in the same experiment that found the *SMPX* site,
and none were found (PMID 27181368). It controls the inference "this gene moved, therefore NR4A3 bound
it", not EMC biology.

### 3.2 · The native→fusion transfer assumption is measured to fail in both directions

Class B is only usable if a native-NR4A3 target is a fusion target. Two published measurements say the
transfer can fail, in opposite directions:

1. **A native target the fusion does not share.** Filion *et al.* put native NR4A3 and NR4A3ΔC on the
   same *PPARG* reporter the fusion activates: "the results show that both the native and truncated
   receptors do not activate PPARG transcription under the same conditions in which it is readily
   activated by the fusion protein."
2. **A fusion target the other fusion does not share.** Brenca *et al.*: "the ability of NR4A3 to
   recognize the SEMA3C target region was retained by the EWSR1-NR4A3 chimera but was impaired by
   TAF15-NR4A3."

So "NR4A3 binds X" does not license "EWSR1::NR4A3 drives X in EMC", and a native-NR4A3 cistrome is not a
fusion cistrome. Both halves of that are demonstrated in the primary literature, not argued here.

### 3.3 · All four instrument controls agree

| control | GPL6244 | GPL3290 |
|---|---|---|
| ***ENO3*** (positive) | AGREES — d +0.8075, t 3.607, df 5.5, p_emp 0.0195 | AGREES — d +3.8113, t 13.221, df 8.5, p_emp 0.00054 |
| ***NR4A3*** (tumour identity) | AGREES — d +0.7415, t 4.662, df 7.2, p_emp 0.0240 | not measurable — 2 comparator values against a floor of 3 |
| ***PLAGL1*** (directional falsifier) | inside null — d −0.4235, p_emp 0.0885 (not graded) | AGREES — d −2.134, t −5.146, df 11.3, p_emp 0.013 |
| ***SGK1*** (transcript/protein discordance) | AGREES — d −0.1807, p_emp 0.269 | AGREES — d +0.6156, p_emp 0.293, band [−1.314, +1.410] |

Four of four graded controls agree with the published direction, with none disagreeing. The positive
control is independently reproduced: *ENO3* matches a separately written module's committed value to
four decimal places on both platforms (`emc-expression-panels.json` → `gene_reads.ENO3`), as do the
PPARγ arms (TRRUST on GPL3290: +0.1647, t 3.193, 57/66 genes; adipogenesis on GPL3290: +0.2183,
t 5.081, 176/200) — two independent implementations, the same numbers. The directional falsifier fires
in the right direction: *PLAGL1*, the one gene in the catalogue with a published *down* prediction, is
−2.13 SD in EMC on GPL3290 and outside its null band, while every other class-A row points up; no
arm-wide artefact produces that pattern. Its published EMC reading is n = 6 by RT-PCR against
chondrocyte controls rather than sarcomas, so it is a strong argument against the offset explanation
and not a proof of one.

### 3.4 · The global offset is not the problem — null-band width is

The measured global offset is tiny: −0.0084 SD on GPL6244 (t −1.592, over 18,694 mapped symbols) and
+0.0258 SD on GPL3290 (t +1.646, over 14,932). So the "most sets come back higher in EMC" pattern is
not an arm-wide shift. What it is instead: at n = 6 versus 29 and n = 10 versus 6, the sampling
variance of a set score is far larger than a Welch *t* on the sample means implies. On GPL3290 the 95%
null band for a 19-gene set is [−0.297, +0.376], so a raw delta of +0.330 with t = 3.16 sits inside it
(p_emp 0.083). The empirical null measures that width directly; the raw *t* cannot see it.

### 3.5 · Per gene — where the positive result is

| gene | class | GPL6244 Δ mean z (p_emp) | GPL3290 Δ mean z (p_emp) |
|---|---|---|---|
| **ENO3** | A · fusion | +0.8075 (0.0195) | +3.8113 (0.00054) |
| **PPARG** | A · fusion | +0.3071 (0.130) | +2.4809 (0.0070) |
| **SEMA3C** | A · fusion | +0.7298 (0.0245) | +0.6228 (0.288) |
| VCAM1 | B · native | −0.8183 (0.0275) | −1.7511 (0.0178) |
| LOXL2 | B · native | −0.0062 (0.992) | −1.8859 (0.0157) |
| NDRG2 | D · EMC tissue | +0.4518 (0.0685) | +1.3828 (0.0557) |
| PLAGL1 | C · fusion expr. | −0.4235 (0.0885) | −2.1340 (0.0130) |

This is the positive result, and it is per-gene, not per-set. All three genes with a DNA-binding assay
against an NR4A3 chimera are positive-signed on both platforms — six of six readings, no reversal — and
each clears its size-matched single-gene null on at least one platform. The aggregate could not be
scored because three genes is below the four-gene floor, and that refusal is reported rather than worked
around.

The ceiling is stated in the same breath. Three genes. Two array platforms of n = 6 and n = 10. One of
the three (*ENO3*) was assayed with the TFG chimera and one (*PPARG*) in rat cells. Sign concordance
across six readings is what a coordinated programme predicts, and also what three individually
EMC-associated genes predict; with three genes the two are not separable.

⚠ **And the three genes are not equally supported — §3.12 separates them.** Under an exact
sample-label permutation test, *ENO3* is significant on both platforms after multiple-testing
correction and *PPARG* on one, while ***SEMA3C* does not reach significance on either** (p = 0.194 and
0.165). Clearing the size-matched null is a statement that a gene's delta is extreme relative to other
genes on the platform; it is not the same statement as the two arms differing for that gene. The
sentence above is true as written of the size-matched null, and it must be read with §3.12 attached.

### 3.6 · A third cohort on a third platform family

The 3SEQ arm carries both contrasts in one experiment: 32 non-EMC sarcoma libraries (the same lineage
axis as the two arrays, on an unrelated technology) and 27 normal-organ libraries (a normal-tissue axis
neither array cohort can supply, because neither contains normal tissue).

| gene | peaks | EMC median | normal median | other-sarcoma median | EMC/normal | EMC/sarcoma |
|---|---:|---:|---:|---:|---:|---:|
| **ENO3** | 2 | 1.7725 | 0.7002 | 0.8795 | 2.53× | 2.02× |
| **SEMA3C** | 3 | 0.5347 | 0.2942 | 0.3217 | 1.82× | 1.66× |
| **PPARG** | 5 | 0.3938 | 0.2783 | 0.1859 | 1.42× | 2.12× |
| *NR4A3 (control)* | 3 | 0.2164 | 0.1102 | 0.000 | 1.96× | — |

*(Medians are the artifact's; the two ratio columns are derived from them in this table.)*

All three class-A genes are higher in EMC than in both comparator arms of a cohort and a technology that
share no probe design with either array. *PPARG*'s array evidence was the weakest of the three —
significant on one platform, not the other — and it is the row this arm helps most, because a weak
effect that reproduces on an unrelated assay is a different object from a weak effect that does not.

*NR4A3* is the internal control here, and it is not a result: its median across the 32 non-EMC sarcoma
libraries is 0.000 and it is detected in the EMC arm — the fusion's own 3′ partner behaving exactly as
the disease definition requires, in a cohort this work did not choose and on an assay it did not design.
It licenses reading the other rows at all; it does not validate any of them, and read as a finding it
would be circular, because EMC is *defined* by an *NR4A3* rearrangement. The normal arm is a tissue
panel, not matched adjacent tissue: the 27 normals are visceral organs with almost no soft tissue, so a
gene high in EMC against that panel is not thereby EMC-specific rather than mesenchymal-lineage-specific.
The two axes are complementary and neither substitutes for the other.

### 3.7 · The aggregate set does not clear its null; the published EMC phenotype does

| set | GPL6244 | GPL3290 |
|---|---|---|
| **A · fusion DNA-binding targets** (SEMA3C, PPARG, ENO3) | no score — 3 genes, floor is 4 | no score — 3 genes |
| **B · native NR4A3 DNA-binding targets** (16) | d −0.0675, p_emp 0.434 → not distinguishable | d −0.1453, p_emp 0.334 → not distinguishable |
| **A+B pooled** (19) | d +0.0403, t 0.756, p_emp 0.320 → not distinguishable | d +0.3301, t 3.159, p_emp 0.083 → not distinguishable |
| **C · fusion expression-only** (2) | no score | no score |
| **D · Filion Table 1** — EMC vs 137 other translocation sarcomas, independent platform and cohort (21) | d +1.1311, t 5.934, p_emp 0.0005, z 19.8 → SET-SPECIFIC UP | d +1.4783, t 5.552, p_emp 0.0005, z 8.9 → SET-SPECIFIC UP |
| **E · Filion Table 2** — Subramanian overlap (20) | d +0.8932, p_emp 0.0005 → SET-SPECIFIC UP | circular (§3.8) — d +1.985, p_emp 0.0005 |
| **F · Brenca EWSR1-high axon guidance** (3) | no score | no score |
| **G · Brenca TAF15-high axon guidance** (10) | d −0.4975, p_emp 0.0005 → SET-SPECIFIC DOWN | d +0.1214, p_emp 0.689 → not distinguishable |

This is the informative shape. The published EMC transcriptional phenotype — a gene list derived on a
platform used nowhere in this work (Affymetrix U133A) from a cohort used nowhere in this work (MSKCC,
EMC vs 137 other translocation sarcomas) — replicates cross-platform and cross-cohort at p_emp 0.0005
on both readable series. So the contrast demonstrably *can* see EMC. On the same instrument, in the same
run, the aggregate direct-target set does not clear its null on either platform. That separates "this
contrast cannot see anything" from "this contrast can see EMC and does not see the aggregate target
set", and only the second is consistent with what was found.

The native-NR4A3 set behaves as Filion's own measurement predicts: class B is flat-to-negative on both
platforms (p_emp 0.434 and 0.334), with *VCAM1* significantly down on both. The vascular/inflammatory
native-NOR-1 programme does not transfer to EMC tissue — concordant with the same paper's finding that
native NR4A3 does not activate the promoter the fusion does (§3.2). Set D is a test of the EMC
phenotype, not of the fusion: a gene can be in it because of EMC's cell of origin, so its replication
says the instrument reads EMC, not that the fusion drives those genes.

### 3.8 · The circularity flag fired, and it was right

The fetched GEO record for GSE4303 reads "Gene expression profile of extraskeletal myxoid
chondrosarcoma", with linked PubMed identifier 15920699 and contributor "Matt van de Rijn". GSE4303 is
the Subramanian *et al.* (2005) cohort, so set E's GPL3290 score is a gene list scored on the data it
was derived from and is not a test; it is reported for completeness only. Set D and the whole of GPL6244
are unaffected, which is why the replication in §3.7 stands.

### 3.9 · PPARγ activity — a positive null-calibrated reading with an adipogenic ceiling

*PPARG* abundance in EMC is settled elsewhere and is not this work's subject. What no study retrieved in
the corpora searched here reports is receptor *activity* — transcriptional output, as distinct from
receptor abundance (a bounded statement about a search, not a claim that no such measurement exists
anywhere). Six gene sets, each pinned to a verbatim Enrichr term with its species read off the term
rather than assumed, each null-calibrated on its own platform:

| arm | library / term | species | GPL6244 | GPL3290 |
|---|---|---|---|---|
| **ChEA ChIP-PET targets** (191) | `ChEA_2022` · PPARG 19300518 ChIP-PET 3T3-L1 Mouse | mouse | +0.080, p_emp 0.0005, z 5.35 → SET-SPECIFIC UP | +0.294, p_emp 0.0005, z 5.08 → SET-SPECIFIC UP |
| **KO_UP falsifier** (246) | `TF_Perturbations…` · PPARG DEFICIENCY MOUSE GSE23421 … UP | mouse | −0.054, p_emp 0.041 → SET-SPECIFIC DOWN | −0.112, p_emp 0.0035 → SET-SPECIFIC DOWN |
| **KO_DOWN** (206) | …PPARG DEFICIENCY MOUSE GSE23421 … DOWN | mouse | +0.0003, p_emp 0.293 → not distinguishable | +0.222, p_emp 0.0005 → SET-SPECIFIC UP |
| **OE_UP** (269) | …PPARG OE MOUSE GSE10192 … UP | mouse | −0.024, p_emp 0.771 → not distinguishable | −0.002, p_emp 0.406 → not distinguishable |
| **TRRUST, human-curated** (66) | `TRRUST…2019` · PPARG human | human | +0.0454, p_emp 0.048 → SET-SPECIFIC UP | +0.1647, p_emp 0.139 → not distinguishable |
| **adipogenesis process proxy** (200) | `MSigDB_Hallmark_2020` · Adipogenesis | unstated in the term | +0.047, p_emp 0.0005 → SET-SPECIFIC UP | +0.218, p_emp 0.0005 → SET-SPECIFIC UP |

Why KO_DOWN and OE_UP cannot be expected to agree, measured rather than argued: the two arms were
previously read as disagreeing about biology, but they share 16 genes out of 206 and 269 (Jaccard
0.035, 7.8% of the smaller set) and come from different experiments (GSE23421 deficiency versus GSE10192
over-expression) in different tissues. They are, for practical purposes, different gene sets, and asking
them to agree was asking two nearly disjoint lists of mouse genes to score alike in human tumour tissue.
(Arithmetic control: KO_DOWN ∩ KO_UP = 0, exactly as the two arms of one knockout experiment must be.)

What replicates: the occupancy-derived target set is set-specific up on both platforms, and the
falsifier is set-specific down on both. A set of genes and the set of genes that move the opposite way
in the same knockout experiment separating in opposite directions, on two platforms, is the pattern an
engaged receptor predicts, and it is not something a size or offset artefact produces, because the null
controls both.

⚠ **The two halves of that pattern are not equally robust (§3.12).** Under an exact sample-label
permutation test the occupancy-derived arm remains strongly significant on both platforms
(p = 0.00033 and 0.00075), but **the KO_UP falsifier does not reach significance on either**
(p = 0.362 and 0.296). The falsifier half of the pattern therefore rests on the competitive null alone,
and the sentence above should be read as such.

The ceiling is not small. The adipogenesis process proxy is also set-specific up on both platforms, and
it shares 44 genes with the ChEA arm (23% of the smaller set), the largest overlap in the table. PPARγ
target output therefore cannot be separated from an adipogenic differentiation component in these data,
and five of the six arms are mouse-derived. Stated at full honesty: PPARγ target genes are coordinately
higher in EMC tumour tissue than in comparator sarcomas, beyond a size-matched random set, on two
platforms, with the knockout-opposite arm moving the other way — and the same data cannot distinguish
that from an adipogenic differentiation programme. This says nothing about the direction of any
pharmacological intervention on this axis.

### 3.10 · No NR4A3-fusion cistrome was retrieved — a bounded negative about a search

The obvious discriminator between *driving* and *correlation* is a cistrome, so the corpora were
searched for one, and the search is reported rather than assumed.

| corpus | full-text documents | catalogued Europe PMC records |
|---|---:|---:|
| extraskeletal-myxoid-chondrosarcoma | 693 | 1,369 |
| pparg-direction-emc | 764 | 978 |
| nr4a3-cistrome-tight | 461 | 792 |
| nr4a3-fusion-partners | 345 | 530 |
| nr4a3-lbd-vs-af1 | 13 | — |
| **total** | **2,276** | **3,669** |

153 of those documents name both a genome-wide chromatin method (ChIP-seq, CUT&RUN, CUT&Tag, ChIP-exo,
ChIP-PET, ATAC-seq, ChAP) and NR4A3/NOR-1/TEC. None of them applies one to an NR4A3 chimera. The only
chromatin experiment performed with a fusion anywhere in the corpus is Brenca *et al.*'s ChAP-qPCR —
target-specific amplification at one locus, not a genome-wide map. Stated as what it is: no EWSR1::NR4A3
cistrome has been retrieved in 2,276 documents across five corpora. That is not "no such dataset
exists" — this searched retrieved full text, not all of PubMed, and a dataset can be deposited without a
paper. What it does show is that a fusion cistrome is an open, unclaimed experiment rather than a
dataset someone forgot to fetch.

### 3.11 · The pre-registered decision rule, and how it landed

The decision rule below was committed while the measurement run was still executing, so the verdict
could not be fitted to what came back.

| # | outcome | what it licenses — and its ceiling |
|---|---|---|
| **A** | *ENO3* reproduces **and** class A (or A+B) clears its null on **both** platforms **and** *PLAGL1* reads down | A positive, EMC-specific result. Ceiling attached in the same paragraph: three genes with a fusion assay; n = 6 and 10; consistent with the fusion driving them **and** with EMC's cell of origin; no cistrome, so no gene shown to be bound *in EMC*. |
| **B** | *ENO3* reproduces, class A clears its null on **one** platform only | A single-platform observation, reported as one. Not a result until it replicates. |
| **C** | *ENO3* reproduces, **nothing** clears its null | Still a result: the published target set is not distinguishable from a size-matched random gene set in either readable EMC series. Not evidence that the fusion does not drive them — a bound on what these datasets can show. |
| **D** | *ENO3* does **not** reproduce | Report the instrument and stop. No biological sentence may be written from the run. |
| **E** | *ENO3* reproduces but *PLAGL1* reads up | Every up row loses its strongest defence against the offset explanation, and that must be stated in the same breath as any up finding. |
| **F** | Filion Table 1 clears its null but class A does not | The instrument reads EMC and the fusion-target set is the thing that is flat — the most informative negative available here. |

Outcome F came true, with a per-gene positive inside it that the rule did not anticipate: all three
class-A genes are positive-signed on both platforms and each clears its single-gene null on at least
one, while the aggregate is refused for being three genes wide. That is a limit of the pre-registration,
recorded rather than quietly rewritten: the branches were written over *set* scores, and the
measurement landed at the *gene* level. A per-gene sign-concordance result is weaker than a set result
that clears its null, and §3.5 states it at that weight. A future version of this rule should carry an
explicit gene-level branch.

### 3.12 · Robustness: an exact permutation test separates what survives from what does not

The four tests of §2.10 were run over the class-A genes, the instrument controls and the sets whose
interpretation depends most on correlation. Every one of the 23 computable rows re-derived the primary
artifact's delta exactly, so the tests below are about the same object the rest of this paper reports.
Both platforms enumerated completely, so every p is exact.

| row | platform | delta | exact permutation p | BH q | jackknife sign | rank re-read |
|---|---|---:|---:|---:|---|---|
| **ENO3** | GPL6244 | +0.807 | **0.000073** | **0.00044** | holds | same sign |
| **ENO3** | GPL3290 | +3.811 | **0.000125** | **0.00063** | holds | same sign |
| **PPARG** | GPL6244 | +0.307 | 0.049 | 0.097 | holds | same sign |
| **PPARG** | GPL3290 | +2.481 | **0.00033** | **0.00083** | holds | same sign |
| **SEMA3C** | GPL6244 | +0.730 | 0.194 | 0.233 | holds | same sign |
| **SEMA3C** | GPL3290 | +0.623 | 0.165 | 0.165 | holds | same sign |
| *NR4A3* (identity control) | GPL6244 | +0.742 | **0.00018** | **0.00055** | holds | same sign |
| *PLAGL1* (directional falsifier) | GPL6244 | −0.423 | 0.083 | 0.124 | holds | same sign |
| *PLAGL1* (directional falsifier) | GPL3290 | −2.134 | **0.0023** | **0.0039** | holds | same sign |
| *SGK1* | GPL6244 | −0.181 | 0.369 | 0.369 | holds | same sign |
| *SGK1* | GPL3290 | +0.616 | 0.156 | 0.165 | holds | same sign |
| A+B pooled (19) | GPL6244 | +0.040 | 0.518 | — | holds | same sign |
| A+B pooled (19) | GPL3290 | +0.330 | 0.011 | — | holds | same sign |
| B native (16) | GPL6244 | −0.068 | 0.226 | — | holds | same sign |
| B native (16) | GPL3290 | −0.145 | 0.257 | — | holds | same sign |
| **D · Filion Table 1 (21)** | GPL6244 | +1.131 | **0.000001** | — | holds | same sign |
| **D · Filion Table 1 (21)** | GPL3290 | +1.478 | **0.0005** | — | holds | same sign |
| PPARγ ChEA occupancy (191) | GPL6244 | +0.080 | **0.00033** | — | holds | same sign |
| PPARγ ChEA occupancy (191) | GPL3290 | +0.294 | **0.00075** | — | holds | same sign |
| PPARγ KO_UP falsifier (246) | GPL6244 | −0.054 | 0.362 | — | holds | same sign |
| PPARγ KO_UP falsifier (246) | GPL3290 | −0.112 | 0.296 | — | holds | same sign |
| Adipogenesis proxy (200) | GPL6244 | +0.047 | 0.035 | — | holds | same sign |
| Adipogenesis proxy (200) | GPL3290 | +0.218 | **0.0015** | — | holds | same sign |

**What survives everything.** *ENO3* is significant on both platforms after multiple-testing correction
(q = 0.0004 and 0.0006), its sign survives dropping any single EMC tumour, and it reads the same way on
a rank statistic. *PPARG* survives on GPL3290 (q = 0.0008). The identity control (*NR4A3*), the
directional falsifier (*PLAGL1*, on GPL3290) and the instrument-reads-EMC control (Filion Table 1, at
p = 1 × 10⁻⁶ and 5 × 10⁻⁴) all behave as §3.3 and §3.7 report, now under an exact test. **No row in the
whole panel changed sign in any leave-one-out fit, and none changed sign on the rank re-read** — so
nothing here rests on one tumour or on the z-scoring convention.

**⚠ What does not survive, stated plainly.** Two claims elsewhere in this paper are weaker under a
self-contained null than under the competitive one, and the difference is not cosmetic:

- ***SEMA3C* does not reach significance under the label-permutation test on either platform**
  (p = 0.194 and 0.165). Its clearance of the size-matched null on GPL6244 (§3.5, p_emp 0.0245) is a
  statement that its delta is extreme *relative to other genes on that platform*; it is not a
  demonstration that the EMC and comparator arms differ for that gene. Both readings are reported, and
  §3.5's per-gene claim must be read with this one attached. *PPARG* on GPL6244 is likewise nominally
  significant but does not survive correction (q = 0.097).
- **The PPARγ KO_UP falsifier is not significant under the permutation test on either platform**
  (p = 0.362 and 0.296), although the occupancy-derived arm is strongly significant on both. So the
  "two arms separating in opposite directions" pattern of §3.9 rests on the competitive null for its
  falsifier half, and §3.9's reading is bounded accordingly. The adipogenic ceiling in that section is
  unchanged and, if anything, firmer: the adipogenesis proxy is itself significant on both platforms.

**And one claim becomes more interesting rather than weaker.** The A+B aggregate does *not* beat an
arbitrary set of the same size on either platform (§3.7) — yet on GPL3290 it *does* differ between the
arms more than chance relabelling would give (p = 0.011). That is not a contradiction; it is the
cleanest available demonstration of this paper's own thesis. The aggregate target set really is higher
in EMC, **and so is almost any set of that size on that platform**, which is precisely why a competitive
null is the one that decides whether a gene set has told you anything. A reader who takes only the
self-contained test away from this literature will over-read every set they score.

---

## 4 · Discussion

### 4.1 · What these data are consistent with, and what they are equally consistent with

A target gene that is up in EMC is consistent with the fusion driving it, and equally consistent with:
(a) EMC's cell of origin expressing it; (b) EMC's myxoid, hypocellular architecture against dense
comparator sarcomas; (c) a platform-wide offset; (d) the gene being a generic proliferation or matrix
gene. The null calibration removes (c) and part of (d). Nothing available in these datasets removes (a)
or (b), and the 3SEQ normal-organ arm narrows nothing on this axis either, because six visceral organs
are not the soft tissue EMC arises in.

### 4.2 · What would discriminate, named rather than hand-waved

1. **A cistrome in the right cell.** An NR4A3 ChIP-seq peak set with the *fusion* expressed, intersected
   with these expression reads: a gene that is up in EMC *and* carries a fusion-bound NBRE in its
   regulatory region is driven; a gene that is up with no peak is correlated. The nearest existing
   dataset is Haller *et al.* (2019, *Nat Commun* 10:368, PMID 30664630): NR4A3 ChIP-seq in three human
   acinic cell carcinoma tumours plus H3K27ac/H3K4me3/CTCF, with a de-novo NBRE motif recovered in all
   three (processed data on Zenodo, doi 10.5281/zenodo.1483691; raw data on EGA, EGAS00001002795,
   controlled access). The caveat is load-bearing: acinic cell carcinoma carries *native* NR4A3
   up-regulated by enhancer hijacking, not a fusion. Given the measurement in §3.2 that native NR4A3
   does not activate the *PPARG* promoter the fusion does, that dataset answers "where does the NR4A3
   DNA-binding domain go in a human tumour" and not "where does EWSR1::NR4A3 go". It must never be cited
   as the latter.
2. **Fusion knockdown or degradation in a genuinely fusion-positive EMC model, with RNA-seq.** No such
   experiment was retrieved.
3. **Fusion-type-stratified EMC expression data.** Brenca *et al.* show class-3 versus class-4–6
   semaphorins separating EWSR1- from TAF15-translocated EMC, but no readable series records which fusion
   each EMC sample carries, so every EMC arm here is a mixture and any fusion-specific signal is
   attenuated by an unknown amount. Set G — the TAF15-high axon-guidance list — reading set-specific
   down on GPL6244 and flat on GPL3290 is the closest these data come to touching that axis, and it is
   not close enough to stratify anything.
4. **An NBRE motif scan** of the promoters of the genes that read high, against a matched background.
   Sequence work; needs no new data. It cannot demonstrate binding, but a set of up-in-EMC genes with no
   NBRE enrichment would be a real negative.

### 4.3 · What is new here

Three things, each of them incremental; nothing here is a first-in-field claim:

- **The catalogue is evidence-typed and the class-A count is stated.** The number of genes with a
  DNA-binding assay against an NR4A3 chimera is three, and the field's prose does not usually say so.
- **The calibration.** A size-matched empirical null on the platform's own genes converts a pervasive
  and uninformative "higher in EMC" into a statement that can be refused — and it refuses this work's
  own aggregate.
- **Cross-platform concordance for the class-A genes**, including a third cohort on a technology sharing
  no probe design with the arrays, together with an internal control (*NR4A3* at 0.000 across 32 non-EMC
  sarcoma libraries) that makes the panel readable.

---

## 5 · Limitations

These are ceilings, not caveats: each one bounds what any sentence in §3 may be read to mean.

1. **n = 4, 6 and 10 EMC.** The EMC arms are four, six and ten tumours. Nothing here survives being
   described as a distribution, and no result should be read as a population estimate.
2. **The three cohorts are never pooled, and must never be.** 3SEQ 3′-end read density is not array
   intensity; GPL6244 single-channel intensity and GPL3290 two-colour log-ratio are not the same
   quantity either. The concordance in §3.5–3.6 is sign agreement across three independent measurements,
   which is weaker than a combined estimate and is deliberately reported as the weaker thing.
3. **Transcript, not protein.** No protein abundance, no post-translational state, no subcellular
   localisation. *SGK1* is the worked example: its published protein direction and its published
   transcript direction oppose, and this instrument can only see the second.
4. **No occupancy, and therefore no causality from the fusion.** Nothing here shows any gene being bound
   by EWSR1::NR4A3 *in EMC*. The class-A assays were performed in engineered human fibroblasts, in rat
   chondrogenic cells, and with a chimera (TFG::NR4A3) that is not the common one. A cistrome in a
   fusion-expressing cell is what would close this, and §3.10 records that none was retrieved.
5. **The normal arm is a six-organ tissue panel, not matched adjacent tissue.** None of the six organs
   is soft tissue, so the normal-tissue contrast cannot separate EMC-specific from
   mesenchymal-lineage-specific.
6. **Comparator arms differ between platforms** — 29 mixed sarcomas including FET-rearranged LGFMS on
   GPL6244, versus 3 DFSP + 3 GIST on GPL3290, versus 32 libraries from 30 sarcoma specimens on 3SEQ. A
   gene can move on one and not another for that reason alone.
7. **Fusion type is unrecorded in every series.** Each EMC arm mixes EWSR1::NR4A3 with whatever
   TAF15::NR4A3 and rarer variants it contains, and those variants differ transcriptionally, so the
   mixture attenuates any fusion-specific signal by an unknown amount.
8. **Multiple testing is corrected for the per-gene permutation results only.** §3.12 reports
   Benjamini–Hochberg q-values across the per-gene exact permutation p-values within each platform;
   the size-matched empirical p-values of §3.5 and §3.7, and the set-level permutation p-values, remain
   uncorrected.
9. **The size-matched null is a competitive null and is anti-conservative for coherent sets.** It
   controls the platform offset and set size, not gene–gene correlation within a real pathway, so on
   its own it is a screen rather than a test. §2.10 and §3.12 supply the complementary self-contained
   null — an exact sample-label permutation that preserves the correlation structure — and the two
   disagree for *SEMA3C* and for the PPARγ falsifier, which is reported rather than reconciled. The
   residual limit is that neither null can make three genes into more than three genes.
10. **GPL3290 is relative.** A two-colour log-ratio against a reference pool: only the between-group
    contrast is interpretable, never an absolute level. Its probe→symbol mapping runs through an EST
    accession bridge, so a gene unreadable there may be absent from the bridge rather than from the
    array.
11. **The 3SEQ rows are medians over very few peaks** — 2 (*ENO3*), 3 (*SEMA3C*), 5 (*PPARG*) and 3
    (*NR4A3*). None is a single-peak row, but a median over two peaks carries almost no internal
    replication, and the peak count is recorded per gene so a reader can weight each row.
12. **The PPARγ activity reading cannot be separated from adipogenic differentiation** (§3.9), and five
    of its six arms are mouse-derived.
13. **Set E is circular on GPL3290** and is reported for completeness only (§3.8).
14. **Nothing here is an efficacy, selectivity, safety, therapeutic-window or clinical-readiness claim**
    for any agent, target or gene, and expression data cannot become that evidence. No drug, dose,
    schedule or patient population is named or implied.

---

## 6 · Conclusion

The genes an NR4A3 chimera is published to bind read higher in EMC tumour tissue than in comparator
tumours in every one of six array readings and in all three genes on an independent third cohort, and
each clears a size-matched single-gene null on at least one array platform. The aggregate target set
does not clear its null in either readable series, while the published EMC transcriptional phenotype
does so at p_emp 0.0005 on both — so the instrument demonstrably reads EMC and does not read the
aggregate. The native-NR4A3 target set does not transfer, exactly as the primary literature's own
reporter experiment predicts.

The binding constraint is not sample size and not statistics. It is that class A is three genes wide,
and that no genome-wide chromatin experiment performed with an NR4A3 fusion was retrieved in 2,276
full-text documents across five corpora (§3.10 — a bounded statement about a search, not a claim that
none exists anywhere). Until such a dataset is in hand, "up in EMC" and "driven by the fusion" cannot
be told apart for any gene named here.

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
`MSigDB_Hallmark_2020`. Each term used is pinned verbatim in the code. Referenced but not used as data:
Haller *et al.* (2019) NR4A3 ChIP-seq — processed data Zenodo doi 10.5281/zenodo.1483691 (open), raw
data EGA EGAS00001002795 (controlled access); §4.2 states why it does not answer this question.

**Code and derived artifacts.** All are openly available in the project repository
(https://github.com/trimcrae/rare-cancers), which will be archived to Zenodo with a citable DOI at
submission:

| artifact | producer |
|---|---|
| `nr4a3-fusion-targets.json` — evidence table, global offsets, null calibrations, per-gene and per-set scores, controls, circularity grade | `nr4a3_fusion_targets.py` |
| `emc-expression-panels.json` → `gene_reads` — the independent second implementation of the per-gene array reads | `emc_expression_panels.py` |
| `gse28866-tumour-vs-normal.json` → `per_gene.values` — the 3SEQ arm | `gse28866_tumour_vs_normal.py` |
| `nr4a3-fusion-targets-robustness.json` — exact label-permutation p-values, leave-one-out jackknife, rank-based re-read and BH q-values (§2.10, §3.12) | `nr4a3_fusion_targets_robustness.py` |
| offline arithmetic guard | `tests/test_nr4a3_fusion_targets.py` |

The null draw is seeded (20260807) and the pool size, seed and universe are recorded per platform, so
every empirical p in §3 is reproducible from the committed code and the public accessions alone. The
committed artifact reproduces offline via `nr4a3_fusion_targets.py --check`.

## Funding

None.

## Conflicts of interest

The author declares no competing interests.

## Ethics approval and consent

Not required. This study analysed only publicly available, de-identified gene-expression deposits and
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
6. Haller F, et al. Enhancer hijacking activates oncogenic transcription factor NR4A3 in acinic cell
   carcinomas of the salivary glands. *Nat Commun* 2019;10:368. PMID 30664630; PMCID PMC6341107.
7. Kim AY, Lim B, Choi J, Kim J. The TFG-TEC oncoprotein induces transcriptional activation of the human
   beta-enolase gene via chromatin modification of the promoter region. *Mol Carcinog* 2016.
   PMID 26310886; doi 10.1002/mc.22384.
8. Labelle Y, et al. Serum- and glucocorticoid-regulated kinase 1 (SGK1) induction by the EWS/NOR1(NR4A3)
   fusion protein. *Biochem Biophys Res Commun* 2006. PMID 16756948; doi 10.1016/j.bbrc.2006.05.134.
9. Subramanian S, West RB, Marinelli RJ, et al. The gene expression profile of extraskeletal myxoid
   chondrosarcoma. *J Pathol* 2005;206:433–444. PMID 15920699; doi 10.1002/path.1792.
10. Zhao X, Min X, Wang Z, et al. NR4A3 inhibits the tumor progression of hepatocellular carcinoma by
    inducing cell cycle G0/G1 phase arrest and upregulation of CDKN2AIP expression. *Int J Biol Sci*
    2024. PMID 39664575; PMCID PMC11628324; doi 10.7150/ijbs.95174.

*Gene-set resources* are cited to the depth their source records supply (author, journal and year only;
full bibliographic identifiers to be completed against the primary sources before submission): Enrichr —
Kuleshov et al., *Nucleic Acids Research* 2016; ChEA — Lachmann et al., *Bioinformatics* 2010; TRRUST v2
— Han et al., *Nucleic Acids Research* 2018; MSigDB Hallmark collection — Liberzon et al., *Cell Systems*
2015. The ChEA term carries its own source PMID in the term string (PPARG 19300518 ChIP-PET 3T3-L1
Mouse). The GSE24369 GEO record links series PubMed identifier 21536545 and is cited throughout by
accession.

*Note on citation provenance.* Every identifier in this reference list is reproduced from a source held
in the project repository (the machine-readable target catalogue, the set-definition blocks, or an
existing curated reference list); author names and titles are given only to the depth the source
supplies them. During preparation, one background citation attributing the cloning of the EMC fusion to
a 1995 paper was found to trace to no held source and was removed; the corresponding statement is now
anchored on the verbatim GEO series record and on Brenca *et al.*
