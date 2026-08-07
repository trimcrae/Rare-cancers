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
**That pattern is the shape of a platform-wide offset, not of biology**, and no read taken on that platform
is interpretable until it is calibrated against a **size-matched random gene set drawn from the same
platform's own genes**. That calibration is the instrument this memo delivers.

**⏳ Status of the measurement.** The literature table (§1), the instrument (§2), the PPARγ framing (§3),
the discriminators (§4) and the circularity grading (§5) are complete and are what this memo is the one home
for. **The numbers themselves are produced by a CI dispatch** of
[`emc-expression-datasets.yml`](../../.github/workflows/emc-expression-datasets.yml) `mode=fusion-targets`
($0, GitHub-hosted CPU runner), which writes
[`nr4a3-fusion-targets.json`](../modalities/nr4a3-fusion-targets.json). **Until §2b below carries a table
of measured values, no number in this document is a reading of EMC** — read §1–§5 as the specification of a
test, not as its result.

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

⛔ **That is the signature of a global offset between the two arms, not of twelve independent biological
findings.** EMC is a myxoid, hypocellular tumour; the GPL3290 comparators are three DFSP and three GIST,
both cellular; and the platform is a two-colour cDNA array read as log-ratios against a reference pool.
Any of those alone would produce an arm-wide shift.

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

> **⏳ NOT YET LANDED — this section is deliberately empty rather than absent.** The dispatch
> (`emc-expression-datasets.yml`, `mode=fusion-targets`, run **31200817686**, dispatched **1:07 PM ET
> 2026-08-07** against branch `worktree-agent-a7b8d3b23b5c7b311`, **$0**) writes
> [`nr4a3-fusion-targets.json`](../modalities/nr4a3-fusion-targets.json) and publishes it to that branch.
>
> ⛔ **An empty section here means the measurement was not taken. It does NOT mean the sets were flat.**
> When it lands, this section must carry, in this order: the four instrument controls with their per-platform
> state; the measured **global offset** on each platform; each set's raw delta *and* its empirical p against
> the size-matched null; and the per-gene, evidence-typed rows. A verdict written from the raw deltas alone
> would be the exact error §2 exists to prevent.

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

★ **The resolution this memo supplies is a method, and it makes a specific, falsifiable prediction.** Run
each arm through the size-matched null on its own platform:

- **If KO_DOWN, ChEA and adipogenesis all fail to clear their nulls on GPL3290**, then the KO_DOWN/OE_UP
  "disagreement" is **not a disagreement about biology at all** — it is two draws from the same null, one
  of which happened to land high. That is a **BOUND**, stated precisely: *PPARγ transcriptional activity in
  EMC is not measurable on GPL3290 with these sets, because the platform's arm-wide offset is of the same
  size as the effect being looked for.* It is not evidence of absence and must never be written as such.
- **If KO_DOWN clears its null and OE_UP does not**, the disagreement is real and the likeliest cause is
  set construction rather than biology — four of the five resolved arms are **mouse**-derived (species
  derived from the matched term, never assumed; only TRRUST's `PPARG human` is human). An orthology
  mismatch would degrade the arms unequally.
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
- **The named discriminators** between the fusion driving a gene and the gene being correlated with EMC (§4).

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
