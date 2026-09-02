---
id: DOC-EMC-BIOMARKER-SELECTED
title: Biomarker-selected therapeutic classes in an ultra-rare sarcoma — what the available expression data excludes
level: L3
kind: manuscript
status: live
canonical_for: ["the 2026-08-09 EMC biomarker-selected class exclusions"]
purpose: >
  Ask, of five therapeutic classes that are given on a molecular state rather than on a histology,
  whether that state is present in extraskeletal myxoid chondrosarcoma — and report that for four of
  them the answer is no, with the strength of each negative stated separately.
scope: >
  L3. Two public archival expression series, 16 EMC tumours, transcript level only, plus a public
  sarcoma-line CRISPR dependency panel containing no EMC line. Reports no experiment in EMC cells, no
  drug exposure and no patient.
audience: [maintainers, external reviewers, autonomous research agents, collaborators]
date: 2026-08-09
last_verified: 2026-08-09
related: [DOC-MODALITY-CENSUS, DOC-EMC-MTAP-PRMT5]
---

# Biomarker-selected therapeutic classes in an ultra-rare sarcoma

> ⛔ **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness for any agent
> in any disease.** This paper reads public transcript data from 16 archival tumours and a public
> dependency panel that contains no cell line from this disease. Every conclusion is a statement about
> whether a *selection criterion* appears to be met, never about whether a drug works.

---

## Summary

Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare sarcoma driven by an *NR4A3* gene fusion,
most often **EWSR1::NR4A3**. It has no targeted agent, and its systemic options are few.

A growing share of oncology's therapeutic classes are given not on a histology but on a **molecular
state** — a lost enzyme, an intact pathway, a repair deficiency. That is structurally good news for an
ultra-rare disease, because it offers entry to a drug developed for someone else. It is only good news
if the state is actually there.

**We asked that question for five such classes, and for four of them the state is absent.** Each
selecting feature is readable in expression data that has been public for years, and for none of the
five had the lookup been reported.

⭐ **The useful output of this paper is which classes the data rules OUT.** In a disease with perhaps a
few hundred patients diagnosed per year worldwide, a route that is quietly kept alive on an untested
assumption consumes attention that has nowhere else to come from. **The field publishes almost none of
these exclusions**, so each one gets re-proposed.

⚠ **The four negatives are not equally strong, and the paper's central methodological claim is that
saying so is the whole job.** One is a clean refutation of the selecting feature. Two are refutations
of a *proxy* for a feature this instrument cannot see. One is a partial reading whose absent half is
precisely the half a transcript cannot measure. They are reported separately for that reason and never
summed.

---

## 1 · What was measured, and against what

**Two public series — the only EMC expression data this array-based reader can score as a group of
tumours.**

⚠ **That is a statement about the instrument, not about what exists.** The repository's own readability
record names five GEO series carrying EMC-titled samples; three are unread here, and none is read as
absent. GSE28866 (4 EMC) is a 3SEQ deposit whose processed matrix sits in GEO *supplementary* files this
reader never opens and is indexed by peaks rather than genes, so whether a given gene can be read out of
it is UNKNOWN. GSE43632 and GSE80126 hold one EMC sample each, and on neither platform did any probe map
to a gene symbol. One further datapoint sits outside these array series: GSE299349 / GSM9037837, a
patient-derived EMC-*labelled* model whose identity check returned
`LABEL_WEAKLY_CORROBORATED_AND_THE_COMPARISON_IS_CONFOUNDED`. **An absent reading is not a reading of
absence, and sixteen tumours is a defensible choice rather than a ceiling nobody could have exceeded.**

| series | platform | EMC | comparator arm |
|---|---|---:|---|
| GSE24369 | GPL6244 | 6 | 29 comparator sarcomas, itself including a FET-rearranged histology |
| GSE4303 | GPL3290 | 10 | 6 |

⚠ **Sample accounting, GSE24369.** The series holds **42** samples: six entered the EMC arm, 29 the
comparator arm, and **seven entered neither.** Two are pooled skeletal-muscle RNA references, correctly
out of a tumour comparator. **Five are solitary fibrous tumours — soft-tissue sarcoma biopsies on the
same array, annotated `sample type: tumor biopsy` like every included comparator — and they are out
because the sample classifier matches substrings and holds no pattern for that histology, not because of
any stated rule about which sarcomas belong in the arm.** Every GPL6244 statistic below is computed
against the reduced arm of 29, and **what the five would do to it is UNKNOWN**: the panel artifact holds
per-sample values for 35 of the 42 and the series matrix is not in this repository, so answering it needs
a re-fetch and a regeneration.

Genes were read as a *z*-score against each array's own probe distribution; groups scored as the mean
EMC-minus-comparator difference in standard-deviation units, with Welch *t* and no multiplicity
correction. Every figure quoted here is owned by
[`emc-expression-panels.json`](../../modalities/emc-expression-panels.json), and the grading of each class
against its own selection criterion by
[`census-route-expression-grading.json`](../../modalities/census-route-expression-grading.json). Class
definitions are anchored in
[`biomarker-class-definitions-2026-08-09.json`](../../literature/biomarker-class-definitions-2026-08-09.json).

**A second, independent axis where a class needed one.** Where the question was not "is the feature
present" but "would hitting this target be selective", the sarcoma-line CRISPR dependency panel
([`depmap-sarcoma-dependency.json`](../../modalities/depmap-sarcoma-dependency.json)) was read instead.
⛔ **That panel contains no EMC line** — the one line carrying the disease's label is recorded as not
harbouring the fusion — so every dependency figure here is a **transfer from other sarcomas**, and the
honest bound is not a small sample but no observation in this disease at all.

⚠ **The proliferation control does not pass on both platforms.** MKI67 was read as an instrument
control, on the expectation that EMC is slow-cycling and that a large proliferation delta would mean the
contrast is being driven by cellularity. It is flat on GPL6244 (+0.13 SD, *t* = 0.53) and **higher in EMC
on GPL3290 by 1.24 SD (*t* = 2.30)**. Three other proliferation-associated transcripts are flat on
GPL3290 (PCNA *t* = 0.13, TOP2A *t* = 0.76, MCM2 *t* = 1.45), so the control fails on one gene on one
platform rather than uniformly — **but it fails, and every GPL3290 reading below must be read with that
open.**

⚠ **Two standing rules govern every row below.** A gene with no probe mapping is recorded as
*unreadable*, never as unexpressed — an absent reading is not a reading of absence. And a near-universal
dependency is evidence **against** selectivity, not for it.

## 2 · The five classes

### 2.1 · Arginine deprivation — the selecting feature reads the wrong way

Agents in this class are given on **loss of ASS1**, the enzyme that lets a cell make its own arginine;
the argument and its sarcoma-specific evidence are in PMID 27735949 and PMID 28122247, the latter being
the closest published setting to this disease.

**ASS1 is HIGHER in EMC than in comparator sarcomas on both platforms**, and on GPL6244 it sits at the
92nd percentile of that array's own distribution. The class requires it to be low.

⚠ **Strength: this is the strongest of the four negatives, and it is still not a proof.** ASS1 loss in
the source literature is an immunohistochemistry call, and a transcript is not a protein. The reading
de-prioritises the class; it does not establish that the class could not act.

### 2.2 · MDM2 inhibition — the axis reads quiet rather than intact

This class needs a p53 axis that is both intact **and transcriptionally live**. Reading output rather
than the gene is the point: MDM2 expression is itself *induced by* wild-type p53 activity (PMID
8440237), so the axis's own output is the available proxy for whether it is running.

**The p53 transcriptional output group is LOWER in EMC on both platforms** (*t* = −2.20 and −1.13),
while the axis genes themselves are flat. Quiet, not live.

⚠ **Strength: weak, and in a direction worth stating.** A quiet p53 output is not a defective axis — an
unstressed tumour has little p53 output by construction, and these are archival resections. **This
cannot establish that *TP53* is wild-type or mutant, and it does not.** ⭐ It is reported because the
quiet-genome argument that raised this class *predicted the opposite*, and a prediction that fails its
own test should be recorded.

### 2.3 · EZH2 inhibition — neither selecting shape is present

The approved agent's registrational indication is selected by **loss of INI1/SMARCB1** (PMID 33035459)
— a SWI/SNF tumour-suppressor subunit — and the neighbouring argument for the class is PRC2 elevation.

**Neither is there.** EZH2 is mildly higher on both platforms and the rest of PRC2 is flat (*t* = −0.22
and 1.71); **no SWI/SNF tumour-suppressor subunit reads anywhere near a floor** (*t* = −1.02 and −0.08).

⚠ **Strength: weak, and this is the clearest case of the instrument missing the target.** The approved
indication is selected by protein **loss**, which is frequently post-transcriptional. A normal
transcript does not exclude it. This is reported as a weak negative and should be read as one.

### 2.4 · Polymerase-θ inhibition — one half present, the other absent

This class selects on a **combination**: alternative end-joining active while homologous recombination
is deficient. Both halves are established — HR-deficient tumours depend on Polθ-mediated repair (PMID
25642963), Polθ promotes alternative end-joining and suppresses recombination (PMID 25642960) — and the
first-in-class inhibitor selects on the HR-deficient half (PMID 34179826).

⭐ **The alt-EJ half is present on both platforms.** The alt-EJ module is higher in EMC on both
(*t* = 2.42 and 2.23), every readable member is higher on both, and the non-homologous end-joining
contrast is flat on both (*t* = −0.19 and 0.16) — **so the elevation is specific against NHEJ.**
⚠ **It is not shown to be specific more broadly, and on GPL3290 it is not shown to be specific at all:**
the homologous-recombination module rises *more* than the alt-EJ module there (+0.266 against +0.258 SD),
so the two move together on that platform and only GPL6244 separates them (+0.087 against −0.044).
⚠ **Three of the module's four members are single-strand-break and base-excision-repair factors**
(LIG3, PARP1, XRCC1), and no contrast against that pathway was read. ⚠ **The route's own primary gene is
the weakest reading in the module.** POLQ has no probe on GPL3290, so the module score there is computed
over three of four genes and the drug target contributes nothing; on GPL6244 it is higher by 0.04 SD
(*t* = 0.31) and sits at the **21st percentile** of that array. **The module carries this observation and
the target gene does not.** Nothing in the literature explains the elevation in this disease.

⛔ **The half that selects the class is not present.** The homologous-recombination arm is flat to mildly
*higher* (*t* = −0.57 and 1.04), not down. The combination is absent, so the class is not indicated.

⚠ **Strength: the weakest negative in the paper, and its own reason for being weak is decisive.** An HR
**defect** is usually a mutation, and can sit behind entirely normal HR transcript. So the half that came
back negative is precisely the half this instrument is least able to measure. ⭐ **We report the alt-EJ
elevation alongside the negative rather than burying it**, with the limits above attached, because a
reader deciding whether to spend a sequencing run on this disease should have it.

### 2.5 · BH3-mimetics — the one that survives, and it survives by failing differently

This class is selected by which anti-apoptotic protein holds the cell's death effectors. That is a
**dependency**, and the method that measures it is BH3 profiling, which reads integrated pathway
function rather than protein level (PMID 17692808, PMID 22230093).

**On abundance the reading is negative and clean.** All five druggable guardians together are LOWER in
EMC than in comparator sarcomas on both platforms (*t* = −4.57 and −2.54), MCL1 and BCL2L1 individually
included.

⭐ **But NOXA — the BH3-only protein that specifically neutralises MCL-1 — is higher in EMC by 1.74
standard deviations of that array on GPL3290** (*t* = 7.59; 66 of that array's 14,403 symbols move at
least as hard). ⚠ **On GPL6244 it is directionally higher and flat by this paper's own convention**
(0.23 SD, *t* = 0.63, with 76% of that array's symbols at least as extreme), and there the BH3-only
sensitiser group as a whole is flat-to-lower (*t* = −0.17). **This is a one-platform observation.**

⛔ **Low guardians with a high sensitiser on GPL3290 would be the transcriptional shadow of a *primed*
cell, and priming is what this class exploits.** So the abundance reading does not refute the class — it
de-prioritises one specific claim about which guardian dominates, while leaving the underlying
hypothesis *more* interesting, not less. **This is the one class of the five that stays open**, and it
stays open because the instrument cannot reach the question rather than because the data was favourable.

⚠ On the dependency axis, MCL1 and BCL2L1 are dependencies in the large majority of sarcoma lines. That
is a statement about the tissue class, not about EMC, and a near-universal dependency argues against
selectivity rather than for it.

## 3 · What this paper is not

- ⛔ **Not a claim that any of these agents would fail in this disease.** Four selection criteria are
  unmet on the evidence available; a class can act through a mechanism its biomarker does not capture.
- ⛔ **Not a substitute for the assays named above.** For all five of them the deciding measurement is
  a protein, a mutation or a functional assay, and each is named in its own section.
- ⛔ **Not generalisable beyond these 16 tumours** on two array platforms of different generations, with
  differing comparator arms, uncorrected for multiple testing.

## 4 · Falsifiers

| # | claim | the observation that would kill it |
|---|---|---|
| F1 | ASS1 is not lost in EMC | ASS1 immunohistochemistry showing protein loss in an EMC series, which would override the transcript reading entirely |
| F2 | the p53 axis is not transcriptionally live | a *TP53* sequence call plus a stress-response readout in the same tumours |
| F3 | no SWI/SNF subunit is lost | INI1/SMARCB1 immunohistochemistry in an EMC series — the assay the approved indication actually uses |
| F4 | the HR-down half is absent | a mutational or genomic-scar readout showing homologous-recombination deficiency behind normal transcript — **the single most likely way this paper is wrong** |
| F5 | the alt-EJ elevation is real | a third EMC series in which the alt-EJ module is null or lower |
| F6 | guardian abundance is low with NOXA high | a third series reversing either direction |
| F7 | the apoptotic question is unresolved | BH3 profiling on EMC tissue or a model — **the decisive test, and the one this paper argues is worth running** |
| F8 | none of these readings is a proliferation or cellularity artefact | ⚠ **partly tested and not clean.** The MKI67 control passes on GPL6244 (*t* = 0.53) and fails on GPL3290 (+1.24 SD, *t* = 2.30), with three other proliferation transcripts flat there. A series matched on proliferation, in which the contrasts disappear, would still kill it |

## 5 · Limits

- **Sixteen tumours, two decade-old array platforms, uncorrected for multiple testing — and a *t* near 2
  is not remarkable on either array.** The producing artifact scores a Welch *t* for every symbol on each
  platform; against that distribution, transcripts at |*t*| ≈ 2.2 sit where roughly a quarter to a third
  of all symbols sit (0.29–0.32 on GPL6244, 0.26–0.29 on GPL3290), while ASS1 sits at 0.069 and 0.046.
  **That placement controls no error rate and is not a significance claim** — the distribution is
  observed rather than permuted and contains real biology — but it cuts both ways: it makes the four
  negatives harder to overturn and removes any claim of remarkableness from the alt-EJ elevation. Two
  series is not a replication set.
- **A transcript is not a protein, a mutation or a dependency**, and for all five classes the
  selecting feature is one of those three rather than a transcript level.
- **The comparator arm is other sarcoma**, so every statement is relative. A feature could be present in
  EMC and in its comparators alike and would read as absent here.
- **No EMC cell line carrying the fusion appears in any public dependency dataset**, so the dependency
  axis is a transfer from other sarcomas throughout and inherits that limit wherever it is used.
- **Nothing here has been tested in an EMC cell**, and no agent in any of these five classes has been
  given to a patient with this disease.
