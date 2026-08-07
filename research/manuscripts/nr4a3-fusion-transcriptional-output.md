---
id: DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT
title: "What EWSR1::NR4A3 is published to transcribe, read in EMC tumour tissue against a size-matched empirical null: three cohorts, three platform families"
level: L3
kind: manuscript
status: live
canonical_for: ["the evidence-typed catalogue of published NR4A3 / NR4A3-fusion transcriptional targets", "the null-calibrated instrument for reading a gene set in the readable EMC expression series", "the cross-platform concordance reading of the class-A fusion target genes"]
purpose: >
  A preprint-shaped report of one question: do the genes an NR4A3 chimera is published to bind
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

# What EWSR1::NR4A3 is published to transcribe, read in EMC tumour tissue against a size-matched empirical null

**Three cohorts, three platform families, and the ceiling stated in the same breath as the result.**

> **STATUS — PREPRINT DRAFT, NOT POSTED.** Target venue: preprint (bioRxiv/ChemRxiv class). No DOI has
> been minted and nothing here has been sent anywhere. Every figure below is read from a committed
> artifact named in §8; none is re-typed from prose. ⛔ **Nothing in this document is an efficacy,
> selectivity, safety, therapeutic-window or clinical-readiness claim** for any agent, target or gene,
> and expression data cannot become that evidence.

---

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is a soft-tissue tumour "characterized by a
balanced translocation most commonly involving t(9;22) (q22;q12)" (Subramanian et al. 2005, PMID 15920699),
rearranging *NR4A3*; the commonest chimeras are EWSR1::NR4A3 and TAF15::NR4A3 (Brenca et al. 2019,
PMID 31020999). The set of
genes any NR4A3 chimera has been shown to physically bind and drive is very small. Whether those genes
are co-ordinately elevated in EMC tumour tissue is a separate and checkable question — and answering it
needs a calibration for what an arbitrary gene set of the same size does on the same platform, because
without one almost every gene set scored in these series comes back "higher in EMC".

**Question.** Do the genes an NR4A3 chimera is published to bind read higher in EMC tumour tissue than
in comparator tumours — beyond what an arbitrary gene set of the same size achieves on the same
platform?

**Approach.** Every primary-literature claim that an NR4A3 fusion or native NR4A3 transcriptionally
activates a named gene was catalogued with its evidence type, assay, cell system, species and the
verbatim sentence it rests on (22 rows). Those genes were then scored in three independent EMC cohorts
on three platform families: GSE24369/GPL6244 (6 EMC vs 29 comparator sarcomas, single-channel array),
GSE4303/GPL3290 (10 EMC vs 6, two-colour cDNA array), and GSE28866 (4 EMC, 32 non-EMC sarcoma
libraries and 27 normal-organ libraries, 3SEQ). On the two array series every contrast is calibrated
against a **size-matched empirical null** — 4,000 random gene sets of exactly the observed size drawn
from the platform's own mapped symbols and scored identically — and four instrument controls,
including a directional falsifier with a published DOWN prediction, are graded before any biology is
read. The decision rule was written and committed before the numbers returned.

**Findings.** The published direct-target set with a DNA-binding or promoter assay behind it is **three
genes wide** — *SEMA3C*, *PPARG*, *ENO3* — and two of the three were assayed with a chimera other than
EWSR1::NR4A3 or in non-human cells. All four instrument controls agree with the published direction on
every platform where a contrast could be computed. The measured global offset between the arms is
**−0.0084 SD** (GPL6244) and **+0.0258 SD** (GPL3290), an order of magnitude below the effects in
question, so the pervasive "higher in EMC" pattern on these platforms is a null-band **width** effect
at n = 6/10, not an arm-wide shift. All three class-A genes are **positive-signed on both array
platforms — six of six readings, no reversal — and each clears its size-matched single-gene null on at
least one**; all three are also higher in EMC than in both the non-EMC sarcoma and the normal-organ arm
of the independent 3SEQ cohort. The **aggregate** direct-target set does not clear its null on either
array platform, while the published EMC transcriptional phenotype (Filion et al. 2009 Table 1, an
independent platform and cohort) replicates at p_emp 0.0005 on both. The native-NR4A3 target set does
**not** transfer: it is flat-to-negative on both platforms, concordant with the published measurement
that native NR4A3 does not activate the promoter the fusion does. A PPARγ activity reading resolves in
the same direction on both platforms — occupancy-derived targets up, the knockout-opposite arm down —
and cannot be separated from an adipogenic differentiation component in these data.

**Interpretation.** These data are consistent with the fusion's published direct targets being
co-ordinately elevated in EMC tissue, and equally consistent with three genes being individually
associated with EMC for reasons that have nothing to do with the fusion. With three genes the two are
not separable. No gene here is shown to be bound by the fusion *in EMC*: a search of 2,276 retrieved
full-text documents across five committed corpora found **no genome-wide chromatin experiment
performed with any NR4A3 chimera**, which makes a fusion cistrome an open, unclaimed experiment rather
than an unfetched dataset.

**Keywords:** extraskeletal myxoid chondrosarcoma · EWSR1::NR4A3 · NR4A3 · transcriptional target ·
empirical null · gene-set calibration · rare sarcoma

---

## 1 · Introduction

### 1.1 · The disease and the driver

EMC is a rare soft-tissue sarcoma defined by rearrangement of *NR4A3* (NOR-1/TEC). Subramanian et al.
describe it as "characterized by a balanced translocation most commonly involving t(9;22) (q22;q12)"
(**PMID 15920699**), which produces EWSR1::NR4A3; Brenca et al. express and assay both that chimera and
TAF15::NR4A3, "the commonest TAF15 (exons 1–6)–NR4A3 (exons 3–8) fusion" (**PMID 31020999**), and the
rarer `t(3;9)(q11-12;q22)` TFG::NR4A3 variant accounts for part of the remainder. NR4A3 is an
orphan nuclear receptor and the chimera places its DNA-binding domain under a strong FET-family
transactivation domain, so the disease's central molecular hypothesis is straightforward: the fusion is
a transcription factor with an aberrant output, and the output is where the disease lives.

### 1.2 · The gap this addresses

The hypothesis is thirty years old and the *evidence* under it is thin in a specific, checkable way.
Two questions are routinely conflated:

1. **Which genes has anyone shown an NR4A3 chimera to physically bind and drive?**
2. **Which genes are high in EMC tumours?**

The first is a mechanism claim and the second is an association. A gene can satisfy the second for
reasons that have nothing to do with the fusion — EMC's cell of origin, its myxoid and hypocellular
architecture against dense comparator sarcomas, or the gene being a generic matrix or proliferation
gene. This work separates the two by (a) cataloguing the mechanism claims with their evidence type
recorded per gene, and (b) reading them back in tumour tissue with an explicit calibration for what an
arbitrary gene set does on the same platform.

### 1.3 · Why the calibration is the load-bearing part

On `GSE4303`/`GPL3290`, almost every gene set anyone scores comes back *"higher in EMC"* — PPARγ
targets, hypoxia metagenes, adipogenesis, chondroitin-sulfate biosynthesis, arginine metabolism. Sets
with no biological relationship to one another move the same way and by similar amounts. A raw Welch
contrast on the sample means uses the samples as its unit of variability and ignores that a set's
per-sample score is one draw from a distribution whose width depends on the set's **size** and on the
platform. At n = 10 vs 6 that width is large: the 95 % band for an arbitrary 19-gene set on GPL3290 is
**[−0.297, +0.376]** SD, so a set can print `t = 3.16` and remain indistinguishable from a random set of
the same size. **No read on these platforms is interpretable until it is calibrated against a
size-matched random gene set drawn from the same platform's own genes.** That calibration is the
instrument this work supplies, and it is applied to its own headline result.

---

## 2 · Methods

Every number in §3 has one home in a committed artifact; this section names the artifact and the module
that produced it, and no figure is re-typed from prose into this document.

### 2.1 · The evidence-typed target catalogue

Every claim in the primary literature that EWSR1::NR4A3, another NR4A3 fusion, or native NR4A3
transcriptionally activates a named gene was recorded with: the gene, the **factor actually tested**,
the assays, the cell system, the **species of those cells**, the expected direction in EMC, and the
**verbatim sentence** the classification rests on. Rows were read from retrieved full text — the
committed Europe PMC corpora on the `literature-cache` branch
(`literature/extraskeletal-myxoid-chondrosarcoma`, `literature/nr4a3-cistrome-tight`,
`literature/nr4a3-fusion-partners`, `literature/pparg-direction-emc-2026-08-06`,
`literature/nr4a3-lbd-vs-af1`) — never from memory.

Four evidence classes, recorded per row in `evidence_table._evidence_classes`:

| class | definition |
|---|---|
| **A** `fusion_dna_binding` | a DNA-binding or promoter assay performed **with an NR4A3 fusion**. The strongest class. |
| **B** `native_dna_binding` | the same assay class with **native NR4A3**. Transfer to the fusion is an assumption. |
| **C** `fusion_expression_only` | the gene moves when the fusion is expressed; no binding assay. |
| **D** `emc_tumour_expression_only` | measured in EMC tissue; no mechanism. |

Machine-readable table with the verbatim sentences:
[`nr4a3_fusion_targets.py`](../modalities/nr4a3_fusion_targets.py) → `LITERATURE_TARGETS`, echoed into
[`nr4a3-fusion-targets.json`](../modalities/nr4a3-fusion-targets.json) → `evidence_table` (22 rows).

### 2.2 · Datasets

Three independent EMC cohorts on three platform families. **They are never pooled** (§6).

| cohort | platform | EMC | comparators | value kind |
|---|---|---|---|---|
| **GSE24369** | GPL6244, Affymetrix Gene ST | **6** | **29** — 17 FET-rearranged LGFMS + 6 desmoid fibromatosis + 6 fibrosarcoma | single-channel intensity |
| **GSE4303** | GPL3290, 42,000-spot two-colour cDNA | **10** | **6** (3 DFSP + 3 GIST) | two-colour log-ratio vs a reference pool |
| **GSE28866** | 3SEQ (GPL10999) | **4** | **32** non-EMC sarcoma libraries; **27** normal-organ libraries | 3′-end read density per peak |

- **GSE24369** — series record read verbatim into `series_records.GSE24369`; linked `!Series_pubmed_id`
  **21536545**. Its comparator arm is itself FET-rearranged (LGFMS is FUS::CREB3L2), so a difference
  here is not merely *"has a FET fusion"*. ⚠ The array carries **42** samples; 6 EMC + 29 comparators
  accounts for 35, and the remaining **7 are unclassified in `platforms.…class_counts` and are excluded
  from the comparator arm** rather than silently absorbed into it — so the arithmetic closes.
- **GSE4303** — Subramanian et al., *J Pathol* 2005;206:433–444, **PMID 15920699**, doi 10.1002/path.1792.
  See §3.8 on circularity.
- **GSE28866** — Brunner AL et al., *Genome Biol* 2012;13(8):R75, **PMID 22929540**,
  doi 10.1186/gb-2012-13-8-r75. The EMC libraries are `EMC_STT5525/5526/5527/5592`; the normal arm is
  27 libraries across six organs (bowel, breast, colon, kidney, lung, uterus). ⚠ The 32 non-EMC sarcoma
  columns include two pairs of **technical replicates** of one specimen each (`ESS_STT5520`,
  `LMS_STT516`), so 32 libraries come from 30 specimens; the pairs are named in
  `per_gene._ties_to_technical_replicates`.

### 2.3 · Per-gene and per-set scoring on the two array series

Probes are mapped to symbols per platform (GPL6244: 20,230 of 28,459 probes → 18,694 distinct symbols;
GPL3290: 27,203 of 43,008 probes → 14,932, through an EST-accession bridge). Each sample's values are
z-scored **against that array's own probe distribution**, so a per-sample score is a within-array
quantity; a gene or set score for a sample is the mean z over its readable members; the contrast is a
Welch t on the EMC vs comparator per-sample scores. A gene with no probe is `readable: false` and its
verdict says the **read** failed, never that the gene is absent. Floors: **3 samples per group** for any
contrast, and **4 genes / 0.4 coverage** for any set score. A set below the floor emits **no score** and
says so.

### 2.4 · The size-matched empirical null

Two quantities a raw Welch contrast does not supply, and which this work computes per platform:

1. **The exact global offset.** The per-sample mean z over **every** symbol the platform maps, contrasted
   EMC vs comparator. This is the amount by which an arbitrary gene set is expected to differ *for no
   set-specific reason*.
2. **A size-matched empirical null.** 4,000 random gene sets of exactly the observed size, drawn from a
   **seeded** random pool of the platform's own mapped symbols (`random.Random(20260807).sample` over the
   sorted symbol list; pool 4,000; universe 18,694 / 14,932), each scored *exactly* as the real set is.
   A random set carries the offset too, so the null absorbs it by construction. The empirical p is the
   fraction of draws at least as extreme, +1/+1 smoothed.

A set is reported **SET-SPECIFIC** only if the observed delta falls outside the 95 % band of that null.
Otherwise the verdict is, verbatim: *"⛔ NOT DISTINGUISHABLE FROM A RANDOM GENE SET of the same size on
this platform. The raw contrast above is what an arbitrary set of this size does here; it is NOT
evidence about this set."* Single genes are calibrated the same way at **set size 1**.

⚠ **The null's own limit, stated rather than assumed.** It controls for the platform-wide offset and for
set *size*. It does **not** control for gene–gene correlation inside a real pathway, which makes a
coherent set's variance larger than a random set's. **The empirical p is therefore anti-conservative for
coherent sets and is a screen, not a test.**

### 2.5 · Instrument controls, graded before the biology

Four known answers, three of which can fail:

| control | published expectation | what it discriminates |
|---|---|---|
| **ENO3** | UP on both platforms | the positive control. ⛔ If it fails, **report the instrument, not the biology.** |
| **NR4A3** | UP — the chimera places *NR4A3* coding sequence under the partner's promoter, and NR4A3 immunostaining is the diagnostic marker of EMC | tumour identity |
| **PLAGL1** | ★ **DOWN** (PMID 16112421) | the **directional falsifier** — the only prediction an arm-wide offset cannot manufacture |
| **SGK1** | flat or down **at transcript level**, despite 10/10 protein positivity (PMID 16756948) | the only row whose published transcript and protein directions oppose |

⛔ **Grading is on where the delta sits relative to its size-1 null, never on the raw delta**, and `pass`
is computed **only over platforms where a contrast was actually computed**. `NOT_READABLE` and
`NOT_MEASURABLE` are absent readings: neither a pass nor a failure. This is load-bearing rather than
pedantic — *NR4A3* on GPL3290 is **readable and not measurable** (four of six comparator spots for that
probe are missing, leaving 2 values against a floor of 3), and a naive rule of the form *"every platform
must show delta > 0"* would mark that platform FAILED and print *"a known answer did not come back as
published"* on a run where the instrument was fine and the array was short four spots. An absent reading
is not a reading of absence, and the block whose job is to tell a working instrument from a broken one is
the last place that distinction may collapse.
`test_a_control_that_is_READABLE_but_has_no_contrast_is_NOT_GRADED_not_FAILED` fails the build if it
ever does.

### 2.6 · The 3SEQ arm

3SEQ measures 3′-end read density per peak. The supplementary peak table carries a `gene_symbol` column,
so gene assignment is a parse rather than a coordinate-mapping project. A gene's value in a library is
the **median across that gene's peaks**; an arm's value is the **median across that arm's libraries**.
No z-score, no test, no confidence interval: n = 4. ⛔ **3SEQ read density is not array intensity and
nothing from this arm may be pooled with GPL6244/GPL3290**, whose z-scores and percentiles measure a
different thing. The canonical interpretation of this arm — including exactly what its 27 visceral-organ
normals can and cannot settle — is [`gse28866-tumour-vs-normal-reading.md`](./gse28866-tumour-vs-normal-reading.md).

### 2.7 · The circularity grade

Filion et al. 2009 publish two gene lists and **only one of them can be scored here without
circularity** (§3.8). Whether GSE4303 is the Subramanian 2005 cohort is graded **from the fetched GEO
series record, never from the sample counts**: the module reads the record and stores its title, summary,
contributors and linked PubMed id verbatim. If the record names PMID 15920699 or Subramanian, the verdict
is `CONFIRMED CIRCULAR` and that set's score on that platform is not a test; if the record does not name
them, the verdict is `NOT CONFIRMED / suspect rather than clean` — never "clean"; if the record could not
be read at all, the verdict is `UNANSWERED`.

### 2.8 · Pre-registration of the decision rule

⛔ The six-branch decision rule in §7 was **written and committed on 2026-08-07 while the measurement run
was still executing**, so that the verdict could not be fitted to whatever came back. Each branch carries
its sentence, its ceiling and its next step in advance. §7 records which branch came true **and where the
pre-registration itself fell short**, rather than quietly rewriting it.

### 2.9 · Reproduction

| what | where |
|---|---|
| target catalogue + null calibration + all array scores | [`nr4a3_fusion_targets.py`](../modalities/nr4a3_fusion_targets.py) → [`nr4a3-fusion-targets.json`](../modalities/nr4a3-fusion-targets.json) |
| independent second implementation of the per-gene array reads | [`emc_expression_panels.py`](../modalities/emc_expression_panels.py) → [`emc-expression-panels.json`](../modalities/emc-expression-panels.json) → `gene_reads` |
| the 3SEQ tumour-vs-normal arm | [`gse28866_tumour_vs_normal.py`](../modalities/gse28866_tumour_vs_normal.py) → [`gse28866-tumour-vs-normal.json`](../modalities/gse28866-tumour-vs-normal.json) → `per_gene.values` |
| offline arithmetic guard, run **before** any fetch | `research/modalities/tests/test_nr4a3_fusion_targets.py` — constructs a known pure global offset and asserts the module declines it, and a known set-specific signal on the same offset and asserts it does not |
| execution | `.github/workflows/emc-expression-datasets.yml`, `mode=fusion-targets` (array arms) and `mode=gse28866` (3SEQ arm) |

The array measurement is **run 31200817686**, dispatched **1:07 PM ET** and completed **1:34 PM ET** on
2026-08-07, at **$0** (GitHub Actions, CPU only, no GPU). The 3SEQ arm ran the same afternoon on the same
free lane.

---

## 3 · Results

### 3.1 · Three genes is the whole of class A

| gene | chimera assayed | assays | cells | citation |
|---|---|---|---|---|
| **SEMA3C** | **EWSR1::NR4A3** (and TAF15::NR4A3, and native) | predicted NBRE-like site (GRCh38 chr7) + **ChAP-qPCR**, Strep-tagged | **tBJ/ER transformed human fibroblasts** | Brenca M et al., *J Pathol* 2019;249(1):90–101. **PMID 31020999**, PMC6766969, doi 10.1002/path.5284 |
| **PPARG** | **EWSR1::NR4A3** (and native, and NR4A3ΔC) | predicted perfect NBRE at −675 bp, **band-shift**, 2.8 kb human *PPARG* promoter **luciferase**, **single-nucleotide NBRE mutant** | CFK2 fetal **rat** chondrogenic cells; human promoter construct | Filion C et al., *J Pathol* 2009;217(1):83–93. **PMID 18855877**, PMC4429309, doi 10.1002/path.2445 |
| **ENO3** (β-enolase) | **TFG::NR4A3** — *not* EWSR1 | **EMSA + ChIP + luciferase**, two NBRE motifs upstream of the TSS, plus ChIP for H3 acetylation at the endogenous promoter | cultured lines over-expressing TFG-TEC | Kim AY et al., *Mol Carcinog* 2016. **PMID 26310886**, doi 10.1002/mc.22384 |

⛔ **Three genes. That is the whole of class A**, and it is the most important number in this report.
Across the whole retrieved corpus, the number of genes anyone has shown an NR4A3 chimera physically
binding and driving is three — and only one of the three (*SEMA3C*) combines the EWSR1 chimera, human
cells and a chromatin assay. ⚠ Three is the count in **2,276 retrieved full-text documents across five
committed corpora** (§3.10), not a claim about all of the literature.

**Class B** — the same assay class with **native NR4A3** — holds sixteen genes: `CCND1` · `SKP2` · `VTN` ·
`SMPX` · `CDKN2AIP` · `GLS2` · `SDHA` · `COX5A` · `PDP1` · `VCAM1` · `ICAM1` · `BIRC3` · `NOX1` · `TH` ·
`LOXL2` · `MYH7`. The strongest are `SMPX` (promoter deletion + site-directed mutagenesis + EMSA + ChIP,
human cells, **PMID 27181368**), `SKP2` (EMSA + ChIP) and `CDKN2AIP` (ChIP + mutation-reversed reporter,
human cells, **PMID 39664575**). **Class C** holds `SGK1` and `PLAGL1`; **class D** holds `NDRG2`, which
Filion et al. examine as a *phosphorylation substrate of SGK1* and which is therefore **not** a
transcriptional-target claim.

A **published negative control** is carried with them: `CALD1`, whose promoter was searched for NOR-1
response elements in the same experiment that found the `SMPX` site and **none were found**
(**PMID 27181368**). ⚠ It controls the inference *"this gene moved, therefore NR4A3 bound it"*, **not**
EMC biology.

### 3.2 · The native→fusion transfer assumption is measured to fail in both directions

Class B is only usable if a native-NR4A3 target is a fusion target. Two published measurements say the
transfer can fail, in opposite directions:

1. **A native target the fusion does not share.** Filion et al. put native NR4A3 and NR4A3ΔC on the same
   *PPARG* reporter the fusion activates: *"the results show that **both the native and truncated
   receptors do not activate PPARG transcription** under the same conditions in which it is readily
   activated by the fusion protein."*
2. **A fusion target the other fusion does not share.** Brenca et al.: *"the ability of NR4A3 to recognize
   the SEMA3C target region was **retained by the EWSR1-NR4A3 chimera but was impaired by
   TAF15-NR4A3**."*

⛔ So *"NR4A3 binds X"* does not license *"EWSR1::NR4A3 drives X in EMC"*, and a native-NR4A3 cistrome is
not a fusion cistrome. Both halves of that are demonstrated in the primary literature, not argued here.

### 3.3 · All four instrument controls agree

One home for every figure below:
[`nr4a3-fusion-targets.json`](../modalities/nr4a3-fusion-targets.json) → `controls.checks`.

| control | GPL6244 | GPL3290 |
|---|---|---|
| **ENO3** (positive) | **AGREES** — d **+0.8075**, t 3.607, df 5.5, p_emp **0.0195** | **AGREES** — d **+3.8113**, t 13.221, df 8.5, p_emp **0.00054** |
| **NR4A3** (tumour identity) | **AGREES** — d +0.7415, t 4.662, df 7.2, p_emp 0.0240 | **NOT MEASURABLE** — 2 comparator values against a floor of 3 |
| **PLAGL1** (directional falsifier) | INSIDE_NULL — d −0.4235, p_emp 0.0885 (not graded) | **AGREES** — d **−2.134**, t −5.146, df 11.3, p_emp **0.013** |
| **SGK1** (transcript/protein discordance) | AGREES — d −0.1807, p_emp 0.269 | AGREES — d +0.6156, p_emp 0.293, inside a band of [−1.314, +1.410] |

`all_checks_pass: true`, 4 of 4 graded, 0 disagreeing.

⭐ **The positive control is independently reproduced.** *ENO3* reproduces a separately written module's
committed value **to four decimal places on both platforms**
([`emc-expression-panels.json`](../modalities/emc-expression-panels.json) → `gene_reads.ENO3`), and so do
the PPARγ arms (TRRUST on GPL3290: +0.1647, t 3.193, 57/66 genes; adipogenesis on GPL3290: +0.2183,
t 5.081, 176/200). Two independent implementations, the same numbers.

★ **And the directional falsifier fires in the right direction.** `PLAGL1` — the one gene in the whole
catalogue with a published **DOWN** prediction — is **−2.13 SD in EMC on GPL3290, outside its null band**,
while every other class-A row points up. No arm-wide artefact produces that pattern.

⚠ **What the PLAGL1 control cannot do.** Its published EMC reading is n = 6 by RT-PCR against
**chondrocyte** controls, not against sarcomas, so the comparator differs from ours. It is a strong
argument against the offset explanation and it is not a proof of one.

### 3.4 · The global offset is not the problem — null-band width is

The measured global offset is **tiny**: GPL6244 **−0.0084 SD** (t −1.592) across 18,694 mapped symbols,
GPL3290 **+0.0258 SD** (t +1.646) across 14,932. So the "most sets come back higher in EMC" pattern is
**not** an arm-wide shift.

⭐ **What it is instead:** at n = 6 vs 29 and n = 10 vs 6 the **sampling variance of a set score is far
larger than a Welch t on the sample means implies.** On GPL3290 the 95 % null band for a 19-gene set is
**[−0.297, +0.376]** — so a raw delta of **+0.330 with t = 3.16** sits *inside* it (p_emp 0.083). The
empirical null measures that width directly; the raw t cannot see it.

### 3.5 · Per gene — where the positive result is

One home: `gene_reads.<SYMBOL>.<series>.null_calibration`.

| gene | class | GPL6244 Δ mean z (p_emp) | GPL3290 Δ mean z (p_emp) |
|---|---|---|---|
| **ENO3** | A · fusion | **+0.8075** (0.0195) | **+3.8113** (0.00054) |
| **PPARG** | A · fusion | +0.3071 (0.130) | **+2.4809** (0.0070) |
| **SEMA3C** | A · fusion | **+0.7298** (0.0245) | +0.6228 (0.288) |
| VCAM1 | B · native | **−0.8183** (0.0275) | **−1.7511** (0.0178) |
| LOXL2 | B · native | −0.0062 (0.992) | **−1.8859** (0.0157) |
| NDRG2 | D · EMC tissue | +0.4518 (0.0685) | +1.3828 (0.0557) |
| PLAGL1 | C · fusion expr. | −0.4235 (0.0885) | **−2.1340** (0.0130) |

★★ **This is the positive result, and it is per-gene, not per-set.** All three genes with a DNA-binding
assay against an NR4A3 chimera are **positive-signed on both platforms — six of six readings, no
reversal — and each clears its size-matched single-gene null on at least one platform.** The aggregate
could not be scored because three genes is below the four-gene floor, and that refusal is reported rather
than worked around.

⛔ **The ceiling, in the same breath.** Three genes. Two array platforms of n = 6 and n = 10. One of the
three (*ENO3*) was assayed with the **TFG** chimera and one (*PPARG*) in **rat** cells. Sign concordance
across six readings is what a coordinated programme predicts **and also what three individually
EMC-associated genes predict**; with three genes the two are not separable.

### 3.6 · A third cohort on a third platform family

The 3SEQ arm carries **both** contrasts in one experiment: 32 non-EMC sarcoma libraries (the same
lineage axis as the two arrays, on an unrelated technology) and 27 normal-organ libraries (a
normal-tissue axis neither array cohort can supply, because neither contains normal tissue). One home:
[`gse28866-tumour-vs-normal.json`](../modalities/gse28866-tumour-vs-normal.json) → `per_gene.values`.

| gene | peaks | EMC median | normal median | other-sarcoma median | EMC/normal | EMC/sarcoma |
|---|---:|---:|---:|---:|---:|---:|
| **ENO3** | 2 | 1.7725 | 0.7002 | 0.8795 | **2.53×** | **2.02×** |
| **SEMA3C** | 3 | 0.5347 | 0.2942 | 0.3217 | 1.82× | 1.66× |
| **PPARG** | 5 | 0.3938 | 0.2783 | 0.1859 | 1.42× | 2.12× |
| *NR4A3 (control)* | 3 | 0.2164 | 0.1102 | **0.000** | 1.96× | — |

*(Medians are the artifact's; the two ratio columns are derived from them in this table and are not a
second home for a measurement.)*

All three class-A genes are higher in EMC than in **both** comparator arms of a cohort and a technology
that share no probe design with either array. *PPARG*'s array evidence was the weakest of the three —
significant on one platform, not the other — and it is the row this arm helps most, because a weak effect
that reproduces on an unrelated assay is a different object from a weak effect that does not.

⛔ **NR4A3 is the internal control, and it is NOT a result.** Its median across the 32 non-EMC sarcoma
libraries is **0.000** and it is detected in the EMC arm — the fusion's own 3′ partner behaving exactly
as the disease definition requires, in a cohort this work did not choose and on an assay it did not
design, with the gene list fixed before the table was parsed. **It licenses reading the other rows at
all; it does not validate any of them.** Read as a finding it would be circular: EMC is *defined* by an
*NR4A3* rearrangement, so a raised *NR4A3* in EMC libraries restates the inclusion criterion.

⚠ **And the normal arm is a tissue panel, not matched adjacent tissue.** The 27 normals are visceral
organs (bowel, breast, colon, kidney, lung, uterus) with almost no soft tissue in them, so a gene high in
EMC against *that* panel is not thereby EMC-specific rather than mesenchymal-lineage-specific. The two
axes are complementary and neither substitutes for the other. Full reading:
[`gse28866-tumour-vs-normal-reading.md`](./gse28866-tumour-vs-normal-reading.md).

### 3.7 · The aggregate set does not clear its null; the published EMC phenotype does

One home: `set_scores.<set>.<series>.null_calibration`.

| set | GPL6244 | GPL3290 |
|---|---|---|
| **A · fusion DNA-binding targets** (SEMA3C, PPARG, ENO3) | ⛔ **NO SCORE** — 3 genes, floor is 4 | ⛔ **NO SCORE** — 3 genes |
| **B · native NR4A3 DNA-binding targets** (16) | d −0.0675, **p_emp 0.434** → not distinguishable | d −0.1453, **p_emp 0.334** → not distinguishable |
| **A+B pooled** (19) | d +0.0403, t 0.756, **p_emp 0.320** → not distinguishable | d +0.3301, t 3.159, **p_emp 0.083** → not distinguishable |
| **C · fusion expression-only** (2) | ⛔ NO SCORE | ⛔ NO SCORE |
| ⭐ **D · Filion Table 1** — EMC vs 137 other translocation sarcomas, **independent platform and cohort** (21) | **d +1.1311, t 5.934, p_emp 0.0005, z 19.8 → SET-SPECIFIC UP** | **d +1.4783, t 5.552, p_emp 0.0005, z 8.9 → SET-SPECIFIC UP** |
| **E · Filion Table 2** — Subramanian overlap (20) | d +0.8932, p_emp 0.0005 → SET-SPECIFIC UP | ⛔ **CIRCULAR** (§3.8) — d +1.985, p_emp 0.0005 |
| **F · Brenca EWSR1-high axon guidance** (3) | ⛔ NO SCORE | ⛔ NO SCORE |
| **G · Brenca TAF15-high axon guidance** (10) | d **−0.4975**, p_emp 0.0005 → **SET-SPECIFIC DOWN** | d +0.1214, p_emp 0.689 → not distinguishable |

⭐ **This is the informative shape.** The published EMC transcriptional phenotype — a gene list derived on
a platform used nowhere in this work (Affymetrix U133A) from a cohort used nowhere in this work (MSKCC,
EMC vs 137 other translocation sarcomas) —
**replicates cross-platform and cross-cohort at p_emp 0.0005 on both readable series.** So the contrast
demonstrably *can* see EMC. On the same instrument, in the same run, the **aggregate direct-target set
does not clear its null on either platform.** That separates *"this contrast cannot see anything"* from
*"this contrast can see EMC and does not see the aggregate target set"* — and only the second is
consistent with what was found.

★ **And the native-NR4A3 set behaves as Filion's own measurement predicts.** Class B is flat-to-negative
on both platforms (p_emp 0.434 and 0.334), with `VCAM1` significantly **down** on both. The
vascular/inflammatory native-NOR-1 programme does **not** transfer to EMC tissue — concordant with the
same paper's finding that native NR4A3 does not activate the promoter the fusion does (§3.2).

⛔ **Set D is a test of the EMC phenotype, not of the fusion.** A gene can be in it because of EMC's cell
of origin. Its replication says the instrument reads EMC; it does **not** say the fusion drives those
genes.

### 3.8 · The circularity flag fired, and it was right

The fetched GEO record for GSE4303 reads *"Gene expression profile of extraskeletal myxoid
chondrosarcoma"*, `!Series_pubmed_id = 15920699`, contributor *"Matt van de Rijn"*. **GSE4303 is the
Subramanian et al. 2005 cohort**, so set E's GPL3290 score is a gene list scored on the data it was
derived from and is not a test; it is reported for completeness only. **Set D and the whole of GPL6244
are unaffected**, which is why the replication in §3.7 stands.

### 3.9 · PPARγ activity — a positive null-calibrated reading with an adipogenic ceiling

*PPARG* **abundance** in EMC is settled elsewhere and is not this work's subject; its one home is
[`pparg-direction-emc.md`](./pparg-direction-emc.md) §6. What no study retrieved in the corpora searched
here reports is receptor **activity** — transcriptional output, as distinct from receptor abundance.
⚠ That is a bounded statement about a search, not a claim that no such measurement exists anywhere.
Six gene sets, each pinned to a verbatim Enrichr term
with its species read off the term rather than assumed, each null-calibrated on its own platform:

| arm | library / term | species | GPL6244 | GPL3290 |
|---|---|---|---|---|
| **ChEA ChIP-PET targets** (191) | `ChEA_2022` · `PPARG 19300518 ChIP-PET 3T3-L1 Mouse` | mouse | **+0.080, p_emp 0.0005, z 5.35 → SET-SPECIFIC UP** | **+0.294, p_emp 0.0005, z 5.08 → SET-SPECIFIC UP** |
| **KO_UP falsifier** (246) | `TF_Perturbations…` · `PPARG DEFICIENCY MOUSE GSE23421 … UP` | mouse | **−0.054, p_emp 0.041 → SET-SPECIFIC DOWN** | **−0.112, p_emp 0.0035 → SET-SPECIFIC DOWN** |
| **KO_DOWN** (206) | `…PPARG DEFICIENCY MOUSE GSE23421 … DOWN` | mouse | +0.0003, p_emp 0.293 → not distinguishable | **+0.222, p_emp 0.0005 → SET-SPECIFIC UP** |
| **OE_UP** (269) | `…PPARG OE MOUSE GSE10192 … UP` | mouse | −0.024, p_emp 0.771 → not distinguishable | −0.002, p_emp 0.406 → not distinguishable |
| **TRRUST, human-curated** (66) | `TRRUST…2019` · `PPARG human` | **human** | +0.0454, p_emp 0.048 → SET-SPECIFIC UP | +0.1647, p_emp 0.139 → not distinguishable |
| ⚠ **adipogenesis process proxy** (200) | `MSigDB_Hallmark_2020` · `Adipogenesis` | unstated in the term | **+0.047, p_emp 0.0005 → SET-SPECIFIC UP** | **+0.218, p_emp 0.0005 → SET-SPECIFIC UP** |

**⛔ Why KO_DOWN and OE_UP cannot agree — the discriminating observation, measured rather than argued.**
The two arms are constructed to have the same expected direction, and they were previously read as
disagreeing about biology. Derived from the artifact's own `set_definitions` gene lists, they **share 16
genes out of 206 and 269** — Jaccard **0.035**, 7.8 % of the smaller set — and they come from different
GEO experiments (`GSE23421` deficiency vs `GSE10192` over-expression) in different tissues. **They are,
for practical purposes, different gene sets**, and asking them to agree was asking two nearly disjoint
lists of mouse genes to score alike in human tumour tissue. *(Arithmetic control: KO_DOWN ∩ KO_UP = **0**,
exactly as the two arms of one knockout experiment must be.)*

★★ **What replicates:** the **occupancy-derived** target set is set-specific UP on both platforms, and the
**falsifier is set-specific DOWN on both**. A set of genes and the set of genes that move the *opposite*
way in the same knockout experiment separating in opposite directions, on two platforms, is the pattern
an engaged receptor predicts — and it is not something a size or offset artefact produces, because the
null controls both.

⛔ **The ceiling, and it is not small.** The **adipogenesis process proxy is also set-specific UP on both
platforms**, and it shares **44 genes with the ChEA arm — 23 % of the smaller set**, the largest overlap
in the table. **PPARγ target output therefore cannot be separated from an adipogenic differentiation
component in these data.** Five of the six arms are **mouse**-derived. Stated at full honesty: *PPARγ
target genes are co-ordinately higher in EMC tumour tissue than in comparator sarcomas, beyond a
size-matched random set, on two platforms, with the knockout-opposite arm moving the other way — and the
same data cannot distinguish that from an adipogenic differentiation programme, because the adipogenesis
proxy behaves identically and overlaps the target set by 23 %.* ⚠ This says **nothing** about the
direction of any pharmacological intervention on this axis; that question has its one home in
[`pparg-direction-emc.md`](./pparg-direction-emc.md) §6 and is untouched by an activity reading.

### 3.10 · No NR4A3-fusion cistrome was retrieved — a bounded negative about a search

The obvious discriminator between *driving* and *correlation* is a cistrome, so the corpora were searched
for one and the search is reported rather than assumed.

| corpus | full-text documents | catalogued Europe PMC records |
|---|---:|---:|
| `extraskeletal-myxoid-chondrosarcoma` | 693 | 1,369 |
| `pparg-direction-emc-2026-08-06` | 764 | 978 |
| `nr4a3-cistrome-tight` | 461 | 792 |
| `nr4a3-fusion-partners` | 345 | 530 |
| `nr4a3-lbd-vs-af1` | 13 | — |
| **total** | **2,276** | **3,669** |

**153 of those documents name both a genome-wide chromatin method** (ChIP-seq, CUT&RUN, CUT&Tag,
ChIP-exo, ChIP-PET, ATAC-seq, ChAP) **and NR4A3/NOR-1/TEC. None of them applies one to an NR4A3
chimera.** The only chromatin experiment performed with a fusion anywhere in the corpus is Brenca et
al.'s **ChAP-qPCR — target-specific amplification at one locus**, not a genome-wide map.

⚠ **State it as what it is.** *"No EWSR1::NR4A3 cistrome has been retrieved in 2,276 documents across
five committed corpora."* That is **not** *"no such dataset exists"*: this searched retrieved full text,
not all of PubMed, and a dataset can be deposited without a paper. **An absent reading is not a reading
of absence.** What it does establish is that a fusion cistrome is an **open, unclaimed experiment**
rather than a dataset someone forgot to fetch.

---

## 4 · Discussion

### 4.1 · What these data are consistent with, and what they are equally consistent with

A target gene that is up in EMC is consistent with the fusion driving it, and **equally** consistent
with: (a) EMC's cell of origin expressing it; (b) EMC's myxoid, hypocellular architecture against dense
comparator sarcomas; (c) a platform-wide offset; (d) the gene being a generic proliferation or matrix
gene. **The null calibration removes (c) and part of (d). Nothing available at $0 removes (a) or (b).**
The 3SEQ normal-organ arm narrows nothing on this axis either, because six visceral organs are not the
soft tissue EMC arises in.

### 4.2 · What would discriminate, named rather than hand-waved

1. ★ **A cistrome in the right cell.** An NR4A3 ChIP-seq peak set with the **fusion** expressed,
   intersected with these expression reads: a gene that is up in EMC **and** carries a fusion-bound NBRE
   in its regulatory region is driven; a gene that is up with no peak is correlated. The nearest existing
   dataset is **Haller F et al. 2019** (*Nat Commun* 10:368, **PMID 30664630**, PMC6341107): NR4A3
   ChIP-seq in **three human acinic cell carcinoma tumours** plus H3K27ac/H3K4me3/CTCF, with a de-novo
   NBRE motif recovered in all three. Processed data: **Zenodo doi 10.5281/zenodo.1483691 — open.** Raw:
   **EGA `EGAS00001002795` — controlled access.**
   ⚠ **The caveat is load-bearing, not decorative.** Acinic cell carcinoma carries **native** NR4A3
   up-regulated by enhancer hijacking, **not a fusion**. Given the measurement in §3.2 that native NR4A3
   does *not* activate the *PPARG* promoter the fusion does, that dataset answers *"where does the NR4A3
   DNA-binding domain go in a human tumour"* and **not** *"where does EWSR1::NR4A3 go"*. It must never be
   cited as the latter.
2. **Fusion knockdown or degradation in a genuinely fusion-positive EMC model, with RNA-seq.** No such
   experiment was retrieved — see [`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md),
   "the decisive gap", and the model-identity finding in
   [`pparg-direction-emc.md`](./pparg-direction-emc.md) §5.
3. **Fusion-type-stratified EMC expression data.** Brenca et al. show class-3 vs class-4–6 semaphorins
   separating EWSR1- from TAF15-translocated EMC. **No readable series records which fusion each EMC
   sample carries**, so every EMC arm here is a *mixture* and any fusion-specific signal is attenuated by
   an unknown amount. Set G — the TAF15-high axon-guidance list — reading **set-specific DOWN** on
   GPL6244 and flat on GPL3290 is the closest these data come to touching that axis, and it is not close
   enough to stratify anything.
4. **⭐ Free, and not yet done: an NBRE motif scan** of the promoters of the genes that read high, against
   a matched background. Sequence work; needs no new data and no dispatch. It cannot demonstrate binding,
   but a set of up-in-EMC genes with **no** NBRE enrichment would be a real negative.

### 4.3 · What is new here

Three things, each of them incremental. Nothing here is landmark and none of it is a
first-in-field claim:

- **The catalogue is evidence-typed and the class-A count is stated.** The number of genes with a
  DNA-binding assay against an NR4A3 chimera is three, and the field's prose does not usually say so.
- **The calibration.** A size-matched empirical null on the platform's own genes converts a pervasive and
  uninformative *"higher in EMC"* into a statement that can be refused — and it refuses this work's own
  aggregate.
- **Cross-platform concordance for the class-A genes**, including a third cohort on a technology sharing
  no probe design with the arrays, together with an internal control (*NR4A3* at 0.000 across 32 non-EMC
  sarcoma libraries) that makes the panel readable.

---

## 5 · Limitations

These are ceilings, not caveats: each one bounds what any sentence in §3 may be read to mean.

1. **n = 4, 6 and 10 EMC.** The EMC arms are four, six and ten tumours. Nothing here survives being
   described as a distribution, and no result should be read as a population estimate.
2. **⛔ The three cohorts are never pooled, and must never be.** 3SEQ 3′-end read density is **not** array
   intensity; GPL6244 single-channel intensity and GPL3290 two-colour log-ratio are not the same quantity
   either. The concordance in §3.5–3.6 is *sign agreement across three independent measurements*, which is
   weaker than a combined estimate and is deliberately reported as the weaker thing.
3. **Transcript, not protein.** No protein abundance, no post-translational state, no subcellular
   localisation. `SGK1` is the worked example of why this matters: its published protein direction and its
   published transcript direction oppose, and this instrument can only see the second.
4. **No occupancy, and therefore no causality from the fusion.** Nothing here shows any gene being bound
   by EWSR1::NR4A3 **in EMC**. The class-A assays were performed in engineered human fibroblasts, in rat
   chondrogenic cells, and with a chimera (TFG::NR4A3) that is not the common one. A cistrome in a
   fusion-expressing cell is what would close this, and §3.10 records that none was retrieved.
5. **The normal arm is a six-organ tissue panel, not matched adjacent tissue.** Bowel, breast, colon,
   kidney, lung, uterus. Six organs are not a body, and none of them is soft tissue, so the normal-tissue
   contrast cannot separate EMC-specific from mesenchymal-lineage-specific.
6. **Comparator arms differ between platforms** — 29 mixed sarcomas including FET-rearranged LGFMS on
   GPL6244, versus 3 DFSP + 3 GIST on GPL3290, versus 32 libraries from 30 sarcoma specimens on 3SEQ. A
   gene can move on one and not another for that reason alone.
7. **Fusion type is unrecorded in every series.** Each EMC arm mixes EWSR1::NR4A3 with whatever
   TAF15::NR4A3 and rarer variants it contains, and Brenca et al. show those variants differ
   transcriptionally, so the mixture attenuates any fusion-specific signal by an unknown amount.
8. **Uncorrected for multiple testing.** t statistics are reported; exact parametric p-values are not,
   because this lane has no scipy. The empirical p is the calibrated quantity and it is not corrected
   across genes or sets.
9. **The empirical null is anti-conservative for coherent sets.** It controls the platform offset and set
   size, not gene–gene correlation within a real pathway. It is a screen, not a test.
10. **GPL3290 is relative.** A two-colour log-ratio against a reference pool: only the between-group
    contrast is interpretable, never an absolute level. Its probe→symbol mapping also runs through an EST
    accession bridge, so a gene unreadable there may be absent from the bridge rather than from the array.
11. **The 3SEQ rows are medians over very few peaks.** The four genes reported here rest on 2 (*ENO3*),
    3 (*SEMA3C*), 5 (*PPARG*) and 3 (*NR4A3*) peaks, so none is a single-peak row — but a median over two
    peaks carries almost no internal replication, and `n_peaks` is recorded per gene in the artifact so a
    reader can weight each row rather than take them as equivalent. *(Five other genes in that 19-gene
    panel do rest on one peak each; none of them is reported in this work.)*
12. **The PPARγ activity reading cannot be separated from adipogenic differentiation** (§3.9), and five of
    its six arms are mouse-derived.
13. **Set E is circular on GPL3290** and is reported for completeness only (§3.8).
14. **⛔ Nothing here is an efficacy, selectivity, safety, therapeutic-window or clinical-readiness claim**
    for any agent, target or gene, and expression data cannot become that evidence. No drug, dose,
    schedule or patient population is named or implied.

---

## 6 · Conclusion

The genes an NR4A3 chimera is published to bind read higher in EMC tumour tissue than in comparator
tumours in every one of six array readings and in all three genes on an independent third cohort, and
each clears a size-matched single-gene null on at least one array platform. The **aggregate** target set
does not clear its null in either readable series, while the published EMC transcriptional phenotype does
so at p_emp 0.0005 on both — so the instrument demonstrably reads EMC and does not read the aggregate.
The native-NR4A3 target set does not transfer, exactly as the primary literature's own reporter
experiment predicts.

The binding constraint is not sample size and not statistics. **It is that class A is three genes wide,
and that no genome-wide chromatin experiment performed with an NR4A3 fusion was retrieved in 2,276
full-text documents across five corpora** (§3.10 — a bounded statement about a search, not a claim that
none exists anywhere). Until such a dataset is in hand, "up in EMC" and "driven by the fusion" cannot be
told apart for any gene named here.

---

## 7 · The pre-registered decision rule, and how it landed

⛔ **Written on 2026-08-07 while the measurement run was still executing**, precisely so the verdict could
not be fitted to what came back.

| # | outcome | what it licenses — and its ceiling |
|---|---|---|
| **A** | ENO3 reproduces **and** class A (or A+B) clears its null on **both** platforms **and** PLAGL1 reads DOWN | A positive, EMC-specific result. Ceiling attached in the same paragraph: three genes with a fusion assay; n = 6 and 10; consistent with the fusion driving them **and** with EMC's cell of origin; no cistrome, so no gene shown to be bound *in EMC*. |
| **B** | ENO3 reproduces, class A clears its null on **one** platform only | A single-platform observation, reported as one. Name the platform, its offset and its comparator arm. Not a result until it replicates. |
| **C** | ENO3 reproduces, **nothing** clears its null | Still a result: *"the published NR4A3-target set is not distinguishable from a size-matched random gene set in either readable EMC series."* **Not** evidence that the fusion does not drive them — a bound on what these datasets can show. |
| **D** | ENO3 does **not** reproduce | ⛔ Report the instrument and stop. No biological sentence may be written from the run. |
| **E** | ENO3 reproduces but **PLAGL1 reads UP** | Every UP row loses its strongest defence against the offset explanation, and that must be stated in the same breath as any UP finding. |
| **F** | Filion Table 1 clears its null but class A does not | The instrument reads EMC and the fusion-target set is the thing that is flat — the most informative negative available here. |

⚠ **In every branch, a raw delta may not be quoted without its empirical p.**

✅ **Outcome F came true**, with a per-gene positive inside it that the rule did not anticipate: all three
class-A genes are positive-signed on both platforms and each clears its single-gene null on at least one,
while the **aggregate** is refused for being three genes wide.

⛔ **That is a limit of the pre-registration and it is recorded rather than quietly rewritten.** The
branches were written over **set** scores; the measurement landed at the **gene** level. A per-gene
sign-concordance result is weaker than a set result that clears its null, and §3.5 states it at that
weight. A future version of this rule should carry an explicit gene-level branch, and should say in
advance what six same-signed readings across three non-poolable platforms are worth — which is the
question this run had to answer after the fact.

---

## 8 · Data and code availability

**All primary data are public and no new data were generated.** Every analysis in this report is CPU-only
and cost **$0**.

### Public datasets

| accession | platform | source | primary publication |
|---|---|---|---|
| **GSE24369** | GPL6244 | NCBI GEO | linked `!Series_pubmed_id` **21536545** |
| **GSE4303** | GPL3290 | NCBI GEO | Subramanian S et al., *J Pathol* 2005;206:433–444, **PMID 15920699**, doi 10.1002/path.1792 |
| **GSE28866** | 3SEQ / GPL10999 | NCBI GEO series supplementary peak tables | Brunner AL et al., *Genome Biol* 2012;13(8):R75, **PMID 22929540**, doi 10.1186/gb-2012-13-8-r75 |

Gene-set libraries are served through Enrichr (Kuleshov et al., *Nucleic Acids Research* 2016):
`ChEA_2022` (Lachmann et al., *Bioinformatics* 2010), `TRRUST_Transcription_Factors_2019` (Han et al.,
*Nucleic Acids Research* 2018), `TF_Perturbations_Followed_by_Expression`, `MSigDB_Hallmark_2020`
(Liberzon et al., *Cell Systems* 2015). Each is cited to the depth its Enrichr term records — author,
journal and year, with no title claimed because none was retrieved — and each term used is pinned
**verbatim** in `pparg_arms.slots`.

Referenced but **not** used as data here: Haller F et al. 2019 NR4A3 ChIP-seq — processed data Zenodo
**doi 10.5281/zenodo.1483691** (open), raw EGA **`EGAS00001002795`** (controlled access). §4.2 states why
it does not answer this question.

### Code and derived artifacts

All in this repository, all committed:

| artifact | producer |
|---|---|
| [`nr4a3-fusion-targets.json`](../modalities/nr4a3-fusion-targets.json) — evidence table, global offsets, null calibrations, per-gene and per-set scores, controls, circularity grade | [`nr4a3_fusion_targets.py`](../modalities/nr4a3_fusion_targets.py) |
| [`emc-expression-panels.json`](../modalities/emc-expression-panels.json) → `gene_reads` — the independent second implementation of the per-gene array reads | [`emc_expression_panels.py`](../modalities/emc_expression_panels.py) |
| [`gse28866-tumour-vs-normal.json`](../modalities/gse28866-tumour-vs-normal.json) → `per_gene.values` — the 3SEQ arm | [`gse28866_tumour_vs_normal.py`](../modalities/gse28866_tumour_vs_normal.py) |
| offline arithmetic guard | `research/modalities/tests/test_nr4a3_fusion_targets.py` |
| execution | `.github/workflows/emc-expression-datasets.yml` (`mode=fusion-targets`, `mode=gse28866`) |

**Determinism.** The null draw is seeded (`20260807`) and the pool size, seed and universe are recorded
per platform, so every empirical p in §3 is reproducible from the committed code and the public
accessions alone.

**Competing interests.** None. **Funding.** None. **Ethics.** No new human data; all analyses are of
public, de-identified deposits.

---

## 9 · What this document is the one home for

- The **evidence-typed catalogue** of published NR4A3 / NR4A3-fusion transcriptional targets, with assay,
  cell system, species and verbatim sentence per gene — machine-readable in
  [`nr4a3_fusion_targets.py`](../modalities/nr4a3_fusion_targets.py) → `LITERATURE_TARGETS`.
- The **measurement that the native→fusion transfer assumption fails in both directions** (§3.2).
- The **size-matched empirical null** as the required calibration for any gene-set read on these
  platforms (§2.4), and the four instrument controls (§2.5).
- The **named discriminators** between the fusion driving a gene and the gene being correlated with EMC
  (§4.2), and the **measured absence of any retrieved NR4A3-fusion cistrome** in 2,276 documents (§3.10).
- The **result** of run 31200817686 (§3.3–3.7) and the **PPARγ activity reading with its adipogenic
  ceiling** (§3.9).

Everything else points here rather than restating it. The PPARγ *direction* and *abundance* questions both
have their one home in [`pparg-direction-emc.md`](./pparg-direction-emc.md); the interpretation of the
3SEQ arm has its one home in
[`gse28866-tumour-vs-normal-reading.md`](./gse28866-tumour-vs-normal-reading.md).

---

## Appendix A · Corrections register

Per the repository's correction rule, superseded statements are retained here and removed from the live
text, so that the body carries only current values.

**A1 — "That pattern is the shape of a platform-wide offset."** Superseded 2026-08-07. Measured: the
global offset is **−0.0084 SD** on GPL6244 and **+0.0258 SD** on GPL3290, an order of magnitude below the
effects in question. The remedy is unchanged — the null absorbs both — but the mechanism is null-band
**width** at n = 10 vs 6, not offset (§3.4). Also superseded: *"GPL3290 carries a platform-wide offset of
the same size as the effect being looked for."*

**A2 — "`emc-expression-panels.json` is not on `main`, and it is named here rather than linked for that
reason."** Superseded 2026-08-07. Checked directly against the remote: the artifact **is** on `main`
(commit `d99f51e29`, 1:39 PM ET 2026-08-07), together with `emc_expression_panels.py`,
`gse28866-tumour-vs-normal.json`, `nr4a3-fusion-targets.json` and their producing modules. This branch
carries a later generation of `emc-expression-panels.json` that adds a surface-antigen read, and **every
class-A figure quoted in §3.3 is byte-identical between the two refs** (ENO3 +0.8075 / +3.8113,
SEMA3C +0.7298 / +0.6228, PPARG +0.3071 / +2.4809). The file is therefore linked normally throughout, and
the corroboration in §3.3 remains corroboration rather than a dependency: every number in §3 is derived
from `nr4a3-fusion-targets.json`.

**A3 — "A frozen gate was one leg short of emitting a fabricated verdict."** Not this document's claim,
retained here only because §2.5's grading rule was written in response to it: a control that is READABLE
but has no computable contrast is **not graded**, never **failed**.

**A4 — Document kind.** This file was `kind: memo` until 2026-08-07 and is now `kind: manuscript`. Its
canonical content is unchanged; what changed is the shape — abstract, methods, results, limitations and a
data/code availability statement, so an external reader can reproduce it without reading the repository.

**A5 — An unsourced citation was removed.** A draft of this manuscript attributed the cloning of the EMC
fusion to a 1995 paper with a PMID that appears in **no committed source in this repository**. It was
written from recollection and is withdrawn; the background sentence is now anchored on the verbatim GEO
series record and on Brenca et al. One home for the account, because it is a lesson rather than a
footnote: **[§References](#references)**, final paragraph.

---

## Appendix B · Repository-internal notes

**B1 · `map_edits_required` — DESCRIBED, NOT APPLIED.** Routed as
[`nr4a3-fusion-targets-map-edits.json`](./nr4a3-fusion-targets-map-edits.json) — six edits, every
`current_text` grep-verified to appear exactly once on both `origin/main` and in the working tree
(0 failures). Verify with:

```
python3 research/manuscripts/verify_map_edit_anchors.py research/manuscripts/nr4a3-fusion-targets-map-edits.json
```

Nothing in it has been applied; `systems/graph/*`, `systems/views/*` and the roadmap are not editable from
this lane. In summary the six edits: re-scope `RT-PPARG-DOWNSTREAM`'s activity readout from *blocked on
data* to *blocked on one free CI dispatch* (E1); withdraw a redundancy premise still standing in a second
field, and correct *"an EMC expression read settles it either way"* (E2); give `RT-TRABECTEDIN-PPARG` its
real, narrower EMC-specific rationale with the caveat attached (E3); add Filion's never-cited negative
result to `EV-FILION-2009` (E4); register four new evidence items — Brenca 2019, Kim 2016, Haller 2019 and
Filion 2005/PLAGL1 (E5); and narrow — **not** retire — `TECH-EMC-EXPRESSION-DATA`, through which nine
routes inherit `BLK-NO-EMC-DATA` (E6).

⚠ **The verifier itself was broken and is fixed.** `verify_map_edit_anchors.py` documented a path argument
and **ignored it**, always checking `three-row-audit-map-edits.json`. Every session told to "verify your
map-edits JSON with it" was reading a green result for a *different file*. A checker that silently checks
something else is worse than no checker, because it produces a pass indistinguishable from a real one. The
default is preserved so existing callers are unaffected.

**B2 · Proposed systems-graph records — DESCRIBED, NOT APPLIED.** No route in `systems/graph/routes.json`
models this work, so it has no publication endpoint. A proposed route record (`RT-FUSION-OUTPUT`) and
publication record (`PUB-FUSION-OUTPUT`) are staged in
[`fusion-output-graph-records.json`](./fusion-output-graph-records.json), matching the live schema, with
the one edit each collection needs spelled out. They are **not** applied here: four agents were working
this branch concurrently and a direct edit to `systems/graph/*.json` would collide.

**B3 · Coordination.** A sibling lane works the NR4A3 cistrome / ChIP-seq angle for `RET` specifically.
This module deliberately fetches **no** cistrome dataset. What it needs, stated so it can be supplied
rather than duplicated: a peak set carrying **(i)** the factor and construct that was ChIPped, **(ii)** the
genome build, **(iii)** peak coordinates or nearest-gene assignments. Given those three fields, §3.5 and
§3.7 become peak-intersected in one offline pass with no new fetch.

---

## References

⛔ **Every entry below is reproduced from a committed source in this repository — the `citation` field of
[`nr4a3_fusion_targets.py`](../modalities/nr4a3_fusion_targets.py) → `LITERATURE_TARGETS`, the
`set_definitions` and `pparg_arms.slots` blocks of
[`nr4a3-fusion-targets.json`](../modalities/nr4a3-fusion-targets.json), or an existing manuscript's
reference list. Author lists and titles are given only to the depth the source supplies them.** An author
name or title this repository has not retrieved is not written in, and `et al.` after the sourced initial
authors is the honest form rather than a shortening.

1. Brenca M, Stacchiotti S, Fassetta K, et al. NR4A3 fusion proteins trigger an axon guidance switch that
   marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas.
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
    inducing cell cycle G0/G1 phase arrest and upregulation of CDKN2AIP expression. *Int J Biol Sci* 2024.
    PMID 39664575; PMCID PMC11628324; doi 10.7150/ijbs.95174.

⚠ **One citation was removed rather than kept, and the removal is the point.** An earlier draft of this
manuscript opened by attributing the cloning of the EMC fusion to a 1995 *Hum Mol Genet* paper with a
PMID. **That citation appears in no committed source in this repository** — it was written from an agent's
recollection, which is exactly the failure mode the golden rule exists to stop, and it survived two
language-lint passes because a linter checks claim STRENGTH and not citation PROVENANCE. The background
sentence is now anchored on the verbatim GEO series record and on Brenca et al., both of which this
repository holds. **A plausible-looking citation is more dangerous than a missing one**, for the same
reason a populated field is more dangerous than an empty one: it reads as checked.

**Gene-set resources**, cited as their Enrichr terms record them (author, journal and year only — no title
is claimed, because none was retrieved): Enrichr — Kuleshov et al., *Nucleic Acids Research* 2016; ChEA —
Lachmann et al., *Bioinformatics* 2010; TRRUST v2 — Han et al., *Nucleic Acids Research* 2018; MSigDB
Hallmark collection — Liberzon et al., *Cell Systems* 2015. Each term used is pinned verbatim in
`pparg_arms.slots`, and the ChEA term carries its own source PMID in the term string
(`PPARG 19300518 ChIP-PET 3T3-L1 Mouse`).

**Series record without a retrieved bibliographic entry.** The GSE24369 GEO record links
`!Series_pubmed_id = 21536545`. That record is stored verbatim in
[`nr4a3-fusion-targets.json`](../modalities/nr4a3-fusion-targets.json) → `series_records.GSE24369`, and the
series is cited throughout by accession and linked identifier rather than by a bibliographic entry this
work did not retrieve.
