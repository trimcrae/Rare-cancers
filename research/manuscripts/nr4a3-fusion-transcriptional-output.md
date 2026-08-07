---
id: DOC-NR4A3-FUSION-TRANSCRIPTIONAL-OUTPUT
title: What EWSR1::NR4A3 actually transcribes — the evidence-typed target set, and how to test it in EMC tissue
level: L3
kind: memo
status: live
canonical_for: ["the evidence-typed catalogue of published NR4A3 / NR4A3-fusion transcriptional targets", "the null-calibrated instrument for reading a gene set in the two readable EMC series"]
purpose: >
  Enumerate, with the evidence type recorded per gene, every gene any primary paper claims an
  NR4A3 fusion or native NR4A3 transcriptionally activates; state what would discriminate the
  fusion DRIVING a gene from the gene merely being high in EMC; and specify the instrument that
  makes an EMC expression read interpretable — a size-matched empirical null on the same platform.
scope: >
  Transcriptional output of the EMC fusion only. Asserts nothing about efficacy, selectivity,
  safety, a therapeutic window or clinical readiness for any agent, target or gene named. Says
  nothing about whether NR4A3 is druggable.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-07
last_verified: 2026-08-07
---

# What EWSR1::NR4A3 actually transcribes

**One sentence.** The fusion's published direct-target set is **four genes wide with a DNA-binding assay
behind it and three of those four were assayed with a chimera** — `SEMA3C` (ChAP-qPCR, human cells,
the EWSR1 chimera), `PPARG` (EMSA + promoter-mutant luciferase, rat chondrogenic cells), `ENO3` (EMSA +
ChIP + luciferase, but with the **TFG** chimera, not the EWSR1 one) and, one class down, `CCND1`/`VTN`
from native NR4A3 — and the two published measurements that bear on whether native-NR4A3 targets
transfer to the fusion **both say the transfer can fail**, in opposite directions.

**Second sentence, and it is the one that changes how every EMC expression read in this repository must
be written.** On `GSE4303`/`GPL3290` almost every gene set anyone has scored comes back *"HIGHER in EMC"* —
PPARγ targets, hypoxia metagenes, adipogenesis, chondroitin-sulfate biosynthesis, arginine metabolism.
**No read on that platform is interpretable until it is calibrated against a size-matched random gene set
drawn from the same platform's own genes** — and once it is, a raw delta of **+0.33 with t = 3.16 lands
INSIDE the null band** (§2b (ii)). That calibration is the instrument this memo delivers.
*(⚠ Superseded, retained: "that pattern is the shape of a platform-wide offset". Measured — the offset is
+0.026 SD on GPL3290, an order of magnitude below the effects in question. The remedy is unchanged; the
mechanism is null-band **width** at n = 10 vs 6, not offset.)*

**Third sentence — what the measurement returned.** Run **31200817686** (2026-08-07, **$0**): all four
instrument controls pass, including the directional falsifier; **all three class-A genes are positive-signed
on both platforms with no reversal, each clearing its size-matched null on at least one**; the **aggregate**
direct-target set does **not** clear its null on either platform; the published EMC phenotype (Filion Table 1,
independent platform and cohort) **replicates at p_emp 0.0005 on both**; and the PPARγ activity question
resolves — the occupancy-derived arm is up and its falsifier is down on both platforms, with an adipogenic
differentiation confound that these data cannot separate. Numbers in **§2b**; PPARγ in **§3**.

---

## 1 · The evidence-typed target table

⭐ **Every row was read from a retrieved document** — the committed Europe PMC corpora on the
`literature-cache` branch (`literature/extraskeletal-myxoid-chondrosarcoma`, 694 files;
`literature/nr4a3-cistrome-tight`, 462; `literature/nr4a3-fusion-partners`;
`literature/pparg-direction-emc-2026-08-06`, 766) — never from memory. The machine-readable table, with the
**verbatim sentence** each classification rests on, is
[`nr4a3_fusion_targets.LITERATURE_TARGETS`](../modalities/nr4a3_fusion_targets.py) and is echoed into
`nr4a3-fusion-targets.json` → `evidence_table`. **Do not retype it** — the summary below is a pointer.

### Class A — a DNA-binding or promoter assay performed **with an NR4A3 fusion**

| gene | chimera assayed | assays | cells | citation |
|---|---|---|---|---|
| **SEMA3C** | **EWSR1::NR4A3** (and TAF15::NR4A3, and native) | in-silico NBRE-like site (GRCh38 chr7) + **ChAP-qPCR**, Strep-tagged | **tBJ/ER transformed human fibroblasts** | Brenca et al., *J Pathol* 2019;249(1):90–101. **PMID 31020999**, PMC6766969, doi 10.1002/path.5284 |
| **PPARG** | **EWSR1::NR4A3** (and native, and NR4A3ΔC) | predicted perfect NBRE at −675 bp, **band-shift**, 2.8 kb human *PPARG* promoter **luciferase**, **single-nucleotide NBRE mutant** | CFK2 fetal **rat** chondrogenic cells; human promoter construct | Filion et al., *J Pathol* 2009;217(1):83–93. **PMID 18855877**, PMC4429309, doi 10.1002/path.2445 |
| **ENO3** (β-enolase) | **TFG::NR4A3** — *not* EWSR1 | **EMSA + ChIP + luciferase**, two NBRE motifs upstream of the TSS, plus ChIP for H3 acetylation at the endogenous promoter | cultured lines over-expressing TFG-TEC | Kim et al., *Mol Carcinog* 2016. **PMID 26310886**, doi 10.1002/mc.22384 |

⛔ **Three genes. That is the whole of class A**, and it is the single most important number in this memo.
Thirty years after the fusion was cloned (Labelle et al., *Hum Mol Genet* 1995, **PMID 8634690**), the
number of genes anyone has shown an NR4A3 chimera physically binding and driving is three.

### Class B — the same assay class, **native NR4A3 (NOR-1)**

`CCND1` · `SKP2` · `VTN` · `SMPX` · `CDKN2AIP` · `GLS2` · `SDHA` · `COX5A` · `PDP1` · `VCAM1` · `ICAM1` ·
`BIRC3` · `NOX1` · `TH` · `LOXL2` · `MYH7` — sixteen genes, each with its assays, cell system, species and
verbatim sentence in the artifact. The strongest are `SMPX` (promoter deletion + site-directed mutagenesis
+ EMSA + ChIP, human cells, **PMID 27181368**), `SKP2` (EMSA + ChIP; used elsewhere as *the* positive-control
region for NR4A3 ChIP) and `CDKN2AIP` (ChIP + mutation-reversed reporter, human cells, **PMID 39664575**).

⚠ **Transfer to the fusion is an ASSUMPTION, and it is measured to fail in both directions.**

1. **A native target that the fusion does not share.** Filion et al. put native NR4A3 and NR4A3ΔC on the
   same *PPARG* reporter the fusion activates: *"the results show that **both the native and truncated
   receptors do not activate PPARG transcription** under the same conditions in which it is readily
   activated by the fusion protein."*
2. **A fusion target that the other fusion does not share.** Brenca et al.: *"the ability of NR4A3 to
   recognize the SEMA3C target region was **retained by the EWSR1-NR4A3 chimera but was impaired by
   TAF15-NR4A3**."*

⛔ So **"NR4A3 binds X" does not license "EWSR1::NR4A3 drives X in EMC"**, and a native-NR4A3 cistrome is
not a fusion cistrome. Both halves of that are demonstrated, not argued.

### Class C — the gene **moves** when the fusion is expressed; no binding assay

| gene | direction | why it is in the table |
|---|---|---|
| **SGK1** | ⚠ **UP as protein, DOWN as transcript** | Differential display in tetracycline-regulated EWS/NOR1 CFK2 cells; IHC positive in **10/10** fusion-positive EMC (**PMID 16756948**). But Filion 2009 report their EMC microarray shows *lower* SGK1 mRNA than other sarcomas, *"also consistent with the data of Subramanian and colleagues"*, and attribute the protein excess to an SGK1 isoform lacking the proteasomal degradation signal. **A transcript instrument should therefore read SGK1 flat or down** — which makes it a control on the reading direction, not a target prediction. |
| **PLAGL1** | ★★ **DOWN** | Down-regulated in CFK2(EWS/NOR1) by differential display and **strongly down in six EMC tumours by RT-PCR** (**PMID 16112421**). |

★★ **`PLAGL1` is the directional falsifier the whole panel needs.** Every other row predicts UP. A
platform-wide offset, or an "EMC differs from dense comparator sarcomas" artefact, pushes *everything* up
together — so a published **DOWN** prediction that reads DOWN is the one observation such an artefact
cannot manufacture.

### Class D — measured in EMC tissue, no mechanism

`NDRG2` — over-expressed in EMC in two independent cohorts, IHC-positive in 9/9 fusion-positive EMC
(Filion 2009). ⛔ **Not** a transcriptional target: Filion et al. examine it as a *phosphorylation substrate
of SGK1*, which is a different claim, and the repository has conflated the two before.

### A published negative control

`CALD1` — its promoter was searched for NOR-1 response elements in the same experiment that found the
`SMPX` site and **none were found** (**PMID 27181368**). ⚠ It controls the inference *"this gene moved,
therefore NR4A3 bound it"*, **not** EMC biology: CALD1 is a smooth-muscle/myofibroblast gene and EMC differs
from DFSP/GIST comparators on exactly that axis.

---

## 2 · Why a raw *"HIGHER in EMC"* is not a result — and the instrument that fixes it

**The observation that forced this.** On `GSE4303`/`GPL3290`, of the sixteen gene sets scored so far in
[`emc-expression-panels.json`](../modalities/emc-expression-panels.json), **twelve came back HIGHER in EMC**,
most of them at |t| > 3: PPARγ ChIP targets, PPARγ curated targets, the PPARγ KO_DOWN arm, adipogenesis,
four independent hypoxia metagenes, a hypoxia GO term, the hypoxia hallmark, chondroitin-sulfate
biosynthesis, GAG biosynthesis, arginine metabolism. **Sets with no biological relationship to one another
all moved the same way and by similar amounts.** The comparator means sit near −0.2 while the EMC means sit
near 0.0 to +0.2 for almost every set.

⚠ **The first hypothesis was that this is an arm-wide offset. IT IS NOT — measured, and the correction is
the more useful finding.** The global offset over every mapped symbol is **−0.0084 SD** on GPL6244 and
**+0.0258 SD** on GPL3290 (§2b (ii)): an order of magnitude below the effects in question. What actually
produces the pattern is that at **n = 10 vs 6** (and 6 vs 29) the **sampling variance of a set score** is far
larger than a Welch t on the sample means implies — the 95 % null band for a 19-gene set on GPL3290 is
**[−0.297, +0.376]**. So a set can print `t = 3.16` and still be indistinguishable from an arbitrary set of
the same size. *(⚠ Superseded, retained: "that is the signature of a global offset between the two arms".)*

**The fix, and it costs nothing.** `nr4a3_fusion_targets.py` measures two things no previous read here has:

1. **The exact global offset** — the per-sample mean z over **every** symbol the platform maps, contrasted
   EMC vs comparator. This is the amount by which an arbitrary gene set is expected to differ *for no
   set-specific reason*.
2. **A size-matched empirical null** — 4,000 random gene sets of exactly the observed size, drawn from a
   seeded random pool of the platform's own mapped symbols, each scored *exactly* as the real set is. A
   random set carries the offset too, so the null absorbs it by construction.

A set is reported **SET-SPECIFIC** only if it falls outside the 95 % band of that null. Otherwise the
verdict is, verbatim: *"⛔ NOT DISTINGUISHABLE FROM A RANDOM GENE SET of the same size on this platform.
The raw contrast above is what an arbitrary set of this size does here; it is NOT evidence about this set."*

⚠ **Stated honestly, the null has a limit and the artifact says so**: it controls for the platform offset
and for set *size*, but not for gene–gene correlation inside a real pathway, which makes a coherent set's
variance larger than a random set's. **The empirical p is therefore anti-conservative and is a screen, not
a test.**

### The instrument is graded before the biology is read

Four known answers, three of which can fail:

| control | expectation | why it discriminates |
|---|---|---|
| **ENO3** | UP on both platforms; prior **+0.8075 SD (t 3.607, df 5.5)** GPL6244, **+3.8113 SD (t 13.221, df 8.5)** GPL3290 — one home: [`emc-expression-panels.json`](../modalities/emc-expression-panels.json) → `gene_reads.ENO3` | ⛔ If it fails, **report the instrument, not the biology.** |
| **NR4A3** | UP — the chimera puts NR4A3 coding sequence under the partner's promoter, and NR4A3 IHC is the diagnostic marker of EMC | the tumour-identity check |
| **PLAGL1** | ★★ **DOWN** | the only prediction a global offset cannot manufacture |
| **SGK1** | flat or down **at transcript level** (threshold: delta < +0.3 SD), despite 10/10 IHC positivity | the only row whose published transcript and protein directions oppose |

⛔ **`pass` is computed only over platforms where a contrast was actually computed, and that rule is
load-bearing rather than pedantic.** `NR4A3` on GPL3290 is **readable and not measurable**: four of the six
comparator spots for that probe are missing, leaving 2 comparator values against a floor of 3. A naive rule
of the form *"every platform must show delta > 0"* marks that platform **FAILED** and prints *"⚠ at least
one known answer did not come back as published"* on a run where the instrument was fine and the array was
short four spots — **"an absent reading is not a reading of absence", inside the very block whose job is to
tell a working instrument from a broken one.** So `NOT_READABLE` and `NOT_MEASURABLE` are neither passes nor
failures, a control with no computable platform is `pass: null`, and
`test_a_control_that_is_READABLE_but_has_no_contrast_is_NOT_GRADED_not_FAILED` fails the build if that ever
collapses back into one state.

---

## 2b · The measured result

Run **31200817686** (`emc-expression-datasets.yml`, `mode=fusion-targets`), dispatched **1:07 PM ET
2026-08-07**, completed **1:34 PM ET**, **$0**. One home for every number below:
[`nr4a3-fusion-targets.json`](../modalities/nr4a3-fusion-targets.json).

### (i) Instrument controls — **all four pass**

| control | GPL6244 | GPL3290 |
|---|---|---|
| **ENO3** (positive) | **AGREES** — d **+0.8075**, t 3.607, p_emp **0.0195** | **AGREES** — d **+3.8113**, t 13.221, p_emp **0.00054** |
| **NR4A3** (tumour identity) | **AGREES** — d +0.7415, t 4.662 | **NOT MEASURABLE** — 2 comparator values against a floor of 3 |
| **PLAGL1** (directional falsifier) | INSIDE_NULL — d −0.4235, p_emp 0.088 (not graded) | **AGREES** — d **−2.134**, t −5.146, p_emp **0.013** |
| **SGK1** (transcript/protein discordance) | AGREES — d −0.1807, p_emp 0.269 | AGREES — d +0.6156, p_emp 0.293 (inside a band of [−1.31, +1.41]) |

⭐ **The instrument is independently validated twice over.** ENO3 reproduces the sibling lane's committed
value **to four decimal places on both platforms**, from a separately written module — and so do the PPARγ
arms (TRRUST GPL3290: +0.1647, t 3.193, df 8.3, 57/66 genes; adipogenesis GPL3290: +0.2183, t 5.081, df 13.9,
176/200 — identical to [`emc-expression-panels.json`](../modalities/emc-expression-panels.json)). Two
independent implementations, the same numbers.

★★ **And the directional falsifier fires in the right direction.** `PLAGL1` — the one gene in the whole
table with a published **DOWN** prediction — is **−2.13 SD in EMC on GPL3290, outside its null band**. No
arm-wide artefact can produce that while every other row points up.

### (ii) ⚠ The global offset was **not** the problem — the **null band width** is

**My §2 hypothesis was wrong and is corrected here.** The measured global offset is **tiny**: GPL6244
**−0.0084 SD** (t −1.592) and GPL3290 **+0.0258 SD** (t +1.646), across all 18,694 and 14,932 mapped symbols
respectively. So the "twelve of sixteen sets are up" pattern is *not* an arm-wide shift.

⭐ **What it is instead:** with n = 6 vs 29 and n = 10 vs 6, the **sampling variance of a set score is far
larger than a Welch t on the sample means implies.** On GPL3290 the 95 % null band for a 19-gene set is
**[−0.297, +0.376]** — so a raw delta of **+0.330 with t = 3.16** sits *inside* it (p_emp 0.083). The raw t
treats the samples as the unit and ignores that a set's per-sample mean is one draw from a distribution whose
width depends on set size and on the platform. **The empirical null measures that width directly.**

*(⚠ Superseded, retained: §2's original explanation, that GPL3290 carries "a platform-wide offset of the same
size as the effect being looked for". Measured 2026-08-07: the offset is +0.026 SD, roughly an order of
magnitude below the effects in question. The remedy is unchanged — the null absorbs both — but the
mechanism is null-band **width**, not offset.)*

### (iii) The gene sets, null-calibrated

| set | GPL6244 | GPL3290 |
|---|---|---|
| **A · fusion DNA-binding targets** (SEMA3C, PPARG, ENO3) | ⛔ **NO SCORE** — 3 genes, floor is 4 | ⛔ **NO SCORE** — 3 genes |
| **B · native NR4A3 DNA-binding targets** (16) | d −0.068, **p_emp 0.434** → not distinguishable | d −0.145, **p_emp 0.334** → not distinguishable |
| **A+B pooled** (19) | d +0.040, **p_emp 0.320** → not distinguishable | d +0.330, t 3.16, **p_emp 0.083** → not distinguishable |
| **C · fusion expression-only** (2) | ⛔ NO SCORE | ⛔ NO SCORE |
| ⭐ **D · Filion Table 1** — EMC vs 137 sarcomas, **independent platform and cohort** (21) | **d +1.131, t 5.93, p_emp 0.0005, z 19.8 → SET-SPECIFIC UP** | **d +1.478, t 5.55, p_emp 0.0005, z 8.9 → SET-SPECIFIC UP** |
| **E · Filion Table 2** — Subramanian overlap (20) | d +0.893, p_emp 0.0005 → SET-SPECIFIC UP | ⛔ **CIRCULAR** (see below) — d +1.985, p_emp 0.0005 |
| **F · Brenca EWSR1-high** (3) | ⛔ NO SCORE | ⛔ NO SCORE |
| **G · Brenca TAF15-high** (10) | d **−0.498**, p_emp 0.0005 → **SET-SPECIFIC DOWN** | d +0.121, p_emp 0.689 → not distinguishable |

**⛔ The circularity flag fired, and it was right.** The fetched GEO record for GSE4303 reads
*"Gene expression profile of extraskeletal myxoid chondrosarcoma"*, `!Series_pubmed_id = 15920699`,
contributor *"Matt van de Rijn"*. **GSE4303 is the Subramanian et al. 2005 cohort**, so set E's GPL3290 score
is a gene list scored on the data it came from and is not a test. **Set D and GPL6244 are unaffected.**

### (iv) Per gene — where the positive result actually is

| gene | class | GPL6244 | GPL3290 |
|---|---|---|---|
| **ENO3** | A · fusion | **+0.8075** (p 0.0195) | **+3.8113** (p 0.00054) |
| **PPARG** | A · fusion | +0.3071 (p 0.130) | **+2.4809** (p 0.0070) |
| **SEMA3C** | A · fusion | **+0.7298** (p 0.0245) | +0.6228 (p 0.288) |
| VCAM1 | B · native | **−0.818** (p 0.027) | **−1.751** (p 0.018) |
| LOXL2 | B · native | −0.006 (p 0.992) | **−1.886** (p 0.016) |
| NDRG2 | D · EMC tissue | +0.452 (p 0.068) | +1.383 (p 0.056) |
| PLAGL1 | C · fusion expr. | −0.424 (p 0.088) | **−2.134** (p 0.013) |

★★ **THIS IS THE POSITIVE RESULT, AND IT IS PER-GENE, NOT PER-SET.** All three genes with a DNA-binding
assay against an NR4A3 chimera are **positive-signed on both platforms — 6 of 6 readings, no reversal** —
and **each clears its size-matched single-gene null on at least one platform**. The aggregate could not be
scored because three genes is below the four-gene floor, and that refusal is reported rather than worked
around.

⛔ **The ceiling, in the same breath.** Three genes. Two platforms of n = 6 and n = 10. One of the three
(ENO3) was assayed with the **TFG** chimera and one (PPARG) in **rat** cells. Sign concordance across six
readings is what a coordinated programme predicts **and also what three individually-EMC-associated genes
predict**; with three genes the two are not separable. **No gene here is shown to be bound by the fusion
*in EMC*** — that needs the cistrome §4 says does not exist.

★ **And the native-NR4A3 set behaves as Filion's measurement predicts.** Class B is flat-to-negative on both
platforms (p 0.434, 0.334), with `VCAM1` significantly **DOWN** on both. The vascular/inflammatory
native-NOR-1 programme **does not transfer to EMC** — concordant with the same paper's finding that native
NR4A3 does not activate the promoter the fusion does.

### (v) ⭐ Outcome **F** of the pre-registered rule (§2c)

*"Filion Table 1 clears its null but class A does not."* Named in advance as **the most informative negative
available here**, because it separates *"this contrast cannot see anything"* from *"this contrast **can** see
EMC and does not see the aggregate target set."* The published EMC transcriptional phenotype **replicates
cross-platform and cross-cohort at p_emp 0.0005 on both platforms** — the instrument demonstrably reads EMC —
and the aggregate direct-target set does not clear its null on either. **The per-gene class-A result stands;
the aggregate claim does not.**

## 2c · ⭐ The decision rule, written **before** the numbers

⛔ **Pre-registered on 2026-08-07, while run 31200817686 was still executing**, precisely so the verdict
cannot be fitted to whatever came back. Each outcome below already has its sentence, its ceiling and its
next step.

| # | outcome | what it licenses — and its ceiling |
|---|---|---|
| **A** | ENO3 reproduces **and** class A (or A+B) clears its size-matched null on **both** platforms **and** PLAGL1 reads DOWN | ★ **A positive, EMC-specific result.** Sentence: *"the genes an NR4A3 chimera is published to bind are co-ordinately higher in EMC tumour tissue than in comparator sarcomas, beyond what a size-matched random gene set achieves on the same platform, in two independent series."* **Ceiling, attached in the same paragraph:** three genes with a fusion assay; two platforms of n = 6 and n = 10; **consistent with the fusion driving them and with EMC's cell of origin**; no cistrome, so no gene is shown to be bound *in EMC*. Next step: the NBRE promoter scan (§4.4), then a peak intersection when a peak set exists. |
| **B** | ENO3 reproduces, class A clears its null on **one** platform only | **A single-platform observation, reported as one.** Name the platform, its global offset and its comparator arm, and say which of the two is more likely to be the artefact. Not a result until it replicates. |
| **C** | ENO3 reproduces, **nothing** clears its null | ⭐ **Still a result, and a useful one:** *"the published NR4A3-target set is not distinguishable from a size-matched random gene set in either readable EMC series."* **It is NOT evidence that the fusion does not drive them** — n = 6/n = 10 on decade-old arrays, mixed fusion types, and three genes in class A. It is a **bound on what these two datasets can show**, and it re-files nine routes' `BLK-NO-EMC-DATA` from *"no data"* to *"data too thin at this effect size"*, which is a different and more actionable blocker. |
| **D** | ENO3 does **not** reproduce | ⛔ **Report the instrument and stop.** No biological sentence may be written from this run. |
| **E** | ENO3 reproduces but **PLAGL1 reads UP** | ⚠ Every UP row loses its strongest defence against the offset explanation, **and that must be stated in the same breath as any UP finding**, not in a limitations list. The PLAGL1 comparator differs from ours (chondrocytes, not sarcomas), so this weakens rather than refutes — and the weakening is the reportable part. |
| **F** | Filion Table 1 clears its null but class A does not | **The instrument reads EMC and the fusion-target set is the thing that is flat.** That is the most informative negative available here, because it separates *"this contrast cannot see anything"* from *"this contrast can see EMC and does not see the target set."* |

⚠ **In every branch, the raw delta may not be quoted without its empirical p.** That is the one rule this
memo adds to how EMC expression is written in this repository.

✅ **OUTCOME F CAME TRUE**, with a per-gene positive inside it that the rule did not anticipate: all three
class-A genes are positive-signed on both platforms and each clears its single-gene null on at least one,
while the **aggregate** is refused for being three genes wide. The rule's branches were written over set
scores; the measurement landed at the gene level. **That is a limit of the pre-registration, and it is
recorded rather than quietly rewritten** — a per-gene sign-concordance result is weaker than a set result
that clears its null, and §2b (iv) states it at that weight.

---

## 3 · The PPARγ activity question — what resolves it, and what bounds it

**The state of the question before this memo.** Abundance is settled and has one home:
[`pparg-direction-emc.md`](./pparg-direction-emc.md) §6 — *PPARG* is over-expressed in EMC in two
independent cohorts and the fusion can drive its promoter. What has never been measured by anyone is
receptor **activity**, i.e. transcriptional output. The first attempt at that measurement
([`emc-expression-panels.json`](../modalities/emc-expression-panels.json), read 3) produced an **ambiguous**
result:

| arm | construction | GPL6244 | GPL3290 |
|---|---|---|---|
| KO_DOWN | genes that fall when *PPARG* is removed — high in EMC = engaged receptor | t = +0.02 | **t = +3.18** |
| OE_UP | genes that rise on over-expression — **independent construction, same expected direction** | t = −1.03 | **t = −0.05** |
| KO_UP (falsifier) | must move the *other* way | t = −0.94 | t = −0.91 |
| ChEA ChIP targets | occupancy-derived | t = +3.72 | t = +5.24 |
| TRRUST, human-curated | the only human-derived arm | t = +1.06 | t = +3.19 |
| adipogenesis (process proxy, **not** a target set) | the composition confound | t = +2.11 | t = +5.08 |

⚠ **The falsifier behaves correctly and the corroborating arm does not.** KO_DOWN and OE_UP are built
from different experiments and must agree; they do not.

### ⭐ RESOLVED — and the "disagreement" was never biological

**Measured 2026-08-07, run 31200817686.** Every arm, null-calibrated on its own platform:

| arm | species | GPL6244 | GPL3290 |
|---|---|---|---|
| **ChEA ChIP-PET targets** (occupancy-derived, 191) | mouse | **+0.080, p_emp 0.0005, z 5.35 → SET-SPECIFIC UP** | **+0.294, p_emp 0.0005, z 5.08 → SET-SPECIFIC UP** |
| **KO_UP falsifier** (246) | mouse | **−0.054, p_emp 0.041 → SET-SPECIFIC DOWN** | **−0.112, p_emp 0.0035 → SET-SPECIFIC DOWN** |
| **KO_DOWN** (206) | mouse | +0.0003, p_emp 0.293 → not distinguishable | **+0.222, p_emp 0.0005 → SET-SPECIFIC UP** |
| **OE_UP** (269) | mouse | −0.024, p_emp 0.771 → not distinguishable | −0.002, p_emp 0.406 → not distinguishable |
| **TRRUST, human-curated** (66) | **human** | +0.045, p_emp 0.048 → SET-SPECIFIC UP | +0.165, p_emp 0.139 → not distinguishable |
| ⚠ **adipogenesis process proxy** (200) | unstated | **+0.047, p_emp 0.0005 → SET-SPECIFIC UP** | **+0.218, p_emp 0.0005 → SET-SPECIFIC UP** |

**⛔ WHY KO_DOWN AND OE_UP CANNOT AGREE — the discriminating observation, measured rather than argued.**
The two arms **share 16 genes out of 206 and 269** — Jaccard **0.035**, 7.8 % of the smaller set. They come
from different GEO experiments (`GSE23421` deficiency vs `GSE10192` over-expression), in different tissues.
**They are, for practical purposes, different gene sets.** Asking them to agree was asking two nearly
disjoint lists of mouse genes to score alike in human tumour tissue. *(Control on that arithmetic: KO_DOWN ∩
KO_UP = **0**, exactly as the two arms of one experiment must be.)*

★★ **What replicates, and it is the strongest PPARγ-activity evidence anyone has produced in EMC:**
the **occupancy-derived** target set is **set-specific UP on both platforms**, and the **falsifier is
set-specific DOWN on both**. A set of genes and the set of genes that move the *opposite* way in the same
knockout experiment separating in opposite directions, on two platforms, is the pattern an engaged receptor
predicts — and it is not something a size or offset artefact produces, because the null controls both.

⛔ **THE CEILING, AND IT IS NOT SMALL.** The **adipogenesis process proxy is also set-specific UP on both
platforms**, and it shares **44 genes (23 % of the smaller set) with the ChEA arm** — the largest overlap in
the whole table. **PPARγ target output therefore cannot be separated from an adipogenic differentiation
component in these data.** Abundance is measured, activity now has a positive null-calibrated reading, and
*which of the two is driving the signal is not resolvable here.* Five of the six arms are **mouse**-derived,
species taken from the matched term rather than assumed.

**So, stated at full honesty:** *PPARγ target genes are co-ordinately higher in EMC tumour tissue than in
comparator sarcomas, beyond a size-matched random set, on two platforms, with the knockout-opposite arm
moving the other way — and the same data cannot distinguish that from an adipogenic differentiation
programme, because the adipogenesis proxy behaves identically and overlaps the target set by 23 %.*
⚠ **This says nothing about the DIRECTION of pharmacological intervention** — that question has its one home
in [`pparg-direction-emc.md`](./pparg-direction-emc.md) §6 and is untouched by an activity reading.

---

**The framing that produced this measurement, retained because the prediction it made was specific:**

★ **The resolution this memo supplies is a method, and it makes a specific, falsifiable prediction.** Run
each arm through the size-matched null on its own platform:

- **If KO_DOWN, ChEA and adipogenesis all fail to clear their nulls on GPL3290**, then the KO_DOWN/OE_UP
  "disagreement" is **not a disagreement about biology at all** — it is two draws from the same null, one
  of which happened to land high. That would be a **BOUND**, not evidence of absence.
- **If KO_DOWN clears its null and OE_UP does not**, the disagreement is real and the likeliest cause is
  set construction rather than biology — five of the six resolved arms are **mouse**-derived (species
  derived from the matched term, never assumed; only TRRUST's `PPARG human` is human). ✅ **This is the
  branch that came true**, and the cause turned out to be measurable and blunter than orthology: the two
  arms **barely share genes** (Jaccard 0.035).
- **If both clear their nulls with opposite signs**, read 3 must be **withdrawn**, not reconciled.

⛔ **And one arm can never be made to agree, by construction, and it should not be asked to.** The
adipogenesis hallmark is a *process proxy*, not a PPARγ target set: PPARγ is the master adipogenic
regulator, so those gene lists overlap by definition. If adipogenesis and the PPARγ arms move together, the
reading is *"this tumour has an adipogenic-like expression component"* — which is a claim about EMC's
differentiation state, not about receptor occupancy. **Abundance is measured; activity is what is at
stake; and a differentiation programme is a third thing.** Conflating any two of them is how this route
produced a redundancy argument its own cited source contradicts (`pparg-direction-emc.md` §3).

---

## 4 · ⛔ The honest frame — what would discriminate driving from correlation

**A target gene that is up in EMC is consistent with the fusion driving it, and equally consistent with:**
(a) EMC's cell of origin expressing it; (b) EMC's myxoid, hypocellular architecture against dense
comparator sarcomas; (c) a platform-wide offset; (d) the gene being a generic proliferation or matrix gene.
**The null calibration removes (c) and part of (d). Nothing available at $0 removes (a) or (b).**

### ⛔ First, a measured negative: **no NR4A3-fusion cistrome has been retrieved**

The obvious discriminator is a cistrome. So the corpora were searched for one, and the search is
reported rather than assumed.

| corpus | full-text documents | catalogued Europe PMC records |
|---|---:|---:|
| `extraskeletal-myxoid-chondrosarcoma` | 693 | 1,369 |
| `pparg-direction-emc-2026-08-06` | 764 | 978 |
| `nr4a3-cistrome-tight` | 461 | 792 |
| `nr4a3-fusion-partners` | 345 | 530 |
| `nr4a3-lbd-vs-af1` | 13 | — |
| **total** | **2,276** | **3,669** |

**153 of those documents name both a genome-wide chromatin method** (ChIP-seq, CUT&RUN, CUT&Tag,
ChIP-exo, ChIP-PET, ATAC-seq, ChAP) **and NR4A3/NOR-1/TEC. Zero of them apply one to an NR4A3 chimera.**
The only chromatin experiment performed with a fusion anywhere in the corpus is Brenca et al.'s
**ChAP-qPCR — target-specific amplification at one locus**, not a genome-wide map.

⚠ **State it as what it is: a bounded negative about a SEARCH.** *"No EWSR1::NR4A3 cistrome has been
retrieved in 2,276 documents across five committed corpora."* It is **not** *"no such dataset exists"* —
this searched retrieved full text, not all of PubMed, and a dataset can be deposited without a paper.
**An absent reading is not a reading of absence.** What it does establish is that a fusion cistrome is an
**open, unclaimed experiment**, not a dataset someone forgot to fetch — and that any substitute must carry
Filion's *native-does-not-activate-PPARG* measurement beside it.

### What would discriminate, named rather than hand-waved

1. ★ **A cistrome, intersected with these expression reads.** A gene that is up in EMC **and** carries a
   fusion-bound NBRE in its regulatory region is driven; a gene that is up with no peak is correlated.
   The nearest existing dataset is **Haller et al. 2019** (*Nat Commun* 10:368, **PMID 30664630**,
   PMC6341107): NR4A3 ChIP-seq in **three human AciCC tumours** plus H3K27ac/H3K4me3/CTCF, with a de-novo
   NBRE motif recovered in all three.
   - **Processed data: Zenodo `doi 10.5281/zenodo.1483691` — OPEN.**
   - **Raw: EGA `EGAS00001002795` — controlled access.**
   - ⚠ **And the caveat is load-bearing, not decorative.** AciCC carries **native** NR4A3 up-regulated by
     enhancer hijacking, **not a fusion**. Given Filion's measurement that native NR4A3 does *not* activate
     the *PPARG* promoter the fusion does, that dataset answers *"where does the NR4A3 DBD go in a human
     tumour"* and **not** *"where does EWSR1::NR4A3 go"*. It must never be cited as the latter.
2. **Fusion knockdown or degradation in a genuinely fusion-positive EMC model, with RNA-seq.** No such
   experiment exists — see [`nr4a3-emc-biology-evidence.md`](./nr4a3-emc-biology-evidence.md), "the decisive
   gap", and the model-identity finding in [`pparg-direction-emc.md`](./pparg-direction-emc.md) §5.
3. **Fusion-type-stratified EMC expression data.** Brenca et al. show class-3 vs class-4–6 semaphorins
   separating EWSR1- from TAF15-translocated EMC. **Neither readable series records which fusion each EMC
   sample carries**, so every EMC arm in this repository is a *mixture* and any fusion-specific signal is
   attenuated by an unknown amount.
4. **⭐ Free, and not yet done: an NBRE motif scan** of the promoters of the genes that read high, against a
   matched background. Sequence work; needs no new data; needs no dispatch. It cannot prove binding, but a
   set of up-in-EMC genes with **no** NBRE enrichment would be a real negative.

### Coordination — what this lane needs rather than what it fetched

⚠ **A sibling lane is working the NR4A3 cistrome / ChIP-seq angle for `RET` specifically.** This module
**deliberately fetches no cistrome dataset.** What it needs, stated so it can be supplied rather than
duplicated: a peak set carrying **(i)** the factor and construct that was ChIPped, **(ii)** the genome
build, **(iii)** peak coordinates or nearest-gene assignments. Given those three fields, reads 1 and 2
become peak-intersected in one offline pass with no new fetch.

---

## 5 · ⚠ The circularity trap, and how it is graded rather than assumed

Filion et al. 2009 publish two gene lists, and **only one of them is safe to score here**:

- **Table 1** — the top 25 probe sets over-expressed in EMC vs **137** other translocation sarcomas on
  Affymetrix U133A at MSKCC. **Neither readable series shares that platform or that cohort**, so scoring it
  here is a genuine cross-cohort, cross-platform replication test of the EMC transcriptional phenotype.
  `DKK1`, `CDH10`, `NMB`, `LCN1`, `PDZRN4`, `CORIN`, `HTR4`, `MAN1A1`, `GULP1`, `PDE3B`, `GRIA3`, `CHAD`,
  `TYRP1`, `MMP16`, `HAPLN1`, `BCAT1`, `EDIL3`, `OXR1`, `P2RY14`, `KCNJ16`, `CCRL1`.
- **Table 2** — the 20 genes Filion's profile shares with the top 50 of **Subramanian et al. 2005**
  (*J Pathol* 206:433–444, **PMID 15920699**). ⛔ **If `GSE4303` is the Subramanian cohort — 10 EMC on a
  42,000-spot cDNA platform, which is what GPL3290 is — then scoring Table 2 on GPL3290 is scoring a gene
  list on the data it was derived from.**

**That is graded from a fetched GEO record, never from the sample counts.** The module reads the `GSE4303`
series record and stores its title, summary, contributors and linked PubMed id **verbatim**; if the record
names PMID 15920699 or Subramanian, the verdict is `CONFIRMED CIRCULAR` and Table 2's GPL3290 score is
reported for completeness only. If it does not, the verdict says **NOT CONFIRMED / suspect rather than
clean** — never "clean". If the record could not be read at all, the verdict is **UNANSWERED**, and Table 2
on GPL3290 must be read as possibly circular.

⛔ **Table 1 is a test of the EMC phenotype, not of the fusion.** A gene can be in it because of EMC's cell
of origin. Replication there says the instrument reads EMC; it does **not** say the fusion drives those genes.

---

## 6 · Limits

- n = **6** EMC (GPL6244) and n = **10** EMC (GPL3290). Small-sample, uncorrected for multiple testing;
  t statistics are reported and exact p-values are not, because this lane has no scipy.
- GPL3290 is a two-colour cDNA array read as log-ratios: only the **between-group** contrast is
  interpretable, never an absolute level.
- The comparator arms differ between platforms — 29 mixed sarcomas including FET-rearranged LGFMS on
  GPL6244, versus 3 DFSP + 3 GIST on GPL3290. A gene can move on one and not the other for that reason alone.
- Fusion type is unrecorded in both series; every EMC arm is a mixture (§4.3).
- GPL3290's probe→symbol mapping runs through an EST accession bridge; a gene unreadable there may be
  absent from the bridge rather than from the array. **An absent reading is not a reading of absence.**
- The empirical null is drawn from a **seeded** random pool of mapped symbols; the pool size, seed and
  universe are recorded per platform so the draw is reproducible and auditable.
- ⛔ **Nothing here is an efficacy, selectivity, safety, therapeutic-window or clinical-readiness claim**
  for any agent, target or gene, and expression data cannot become that evidence.

---

## 7 · Files this memo is the one home for

- **The evidence-typed catalogue** of published NR4A3 / NR4A3-fusion transcriptional targets, with the
  assay, cell system, species and verbatim sentence per gene — machine-readable in
  [`nr4a3_fusion_targets.py`](../modalities/nr4a3_fusion_targets.py) → `LITERATURE_TARGETS`.
- **The measurement that the native→fusion transfer assumption fails in both directions** (§1).
- **The size-matched empirical null** as the required calibration for any gene-set read on these two
  platforms (§2), and the four instrument controls (§2).
- **The named discriminators** between the fusion driving a gene and the gene being correlated with EMC (§4),
  and the **measured absence of any NR4A3-fusion cistrome** in 2,276 retrieved documents (§4).
- **The measured result** of run 31200817686 (§2b) and the **PPARγ activity resolution with its adipogenic
  ceiling** (§3) — including the measurement that the KO_DOWN and OE_UP arms share 16 genes of 206/269, which
  is why they could never have agreed.

Everything else points here rather than restating it. The PPARγ *direction* question and *abundance* both
have their one home in [`pparg-direction-emc.md`](./pparg-direction-emc.md); the ENO3 prior has its one home
in [`emc-expression-panels.json`](../modalities/emc-expression-panels.json).

## 8 · `map_edits_required` — DESCRIBED, NOT APPLIED

Routed as [`nr4a3-fusion-targets-map-edits.json`](./nr4a3-fusion-targets-map-edits.json) — **six edits,
every `current_text` grep-verified to appear exactly once on both `origin/main` and in the working tree
(0 failures)**. Verify with:

```
python3 research/manuscripts/verify_map_edit_anchors.py research/manuscripts/nr4a3-fusion-targets-map-edits.json
```

**Nothing in it has been applied** — `systems/graph/*`, `systems/views/*` and the roadmap are not editable
from this lane. In summary they: re-scope `RT-PPARG-DOWNSTREAM`'s activity readout from *blocked on data*
to *blocked on one free CI dispatch* (E1); withdraw a redundancy premise still standing in a second field
and correct *"an EMC expression read settles it either way"* (E2); give `RT-TRABECTEDIN-PPARG` its real,
narrower EMC-specific rationale with the caveat attached (E3); add Filion's never-cited negative result to
`EV-FILION-2009` (E4); register four new evidence items — Brenca 2019, Kim 2016, Haller 2019 and Filion
2005/PLAGL1 (E5); and narrow — **not** retire — `TECH-EMC-EXPRESSION-DATA`, through which nine routes
inherit `BLK-NO-EMC-DATA` (E6).

⚠ **The verifier itself was broken and is fixed in this change.** `verify_map_edit_anchors.py` documented a
path argument and **ignored it**, always checking `three-row-audit-map-edits.json`. Every session told to
"verify your map-edits JSON with it" was reading a green result for a *different file*. A checker that
silently checks something else is worse than no checker — it produces a pass indistinguishable from a real
one. The default is preserved so existing callers are unaffected.
