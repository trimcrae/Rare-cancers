---
id: DOC-EMC-HYPOXIA-READING
title: The EMC hypoxia reading — what survives its confounds, and what it licenses
level: L3
kind: memo
status: live
canonical_for: [emc_hypoxia_expression_reading, emc_hypoxia_confound_audit]
purpose: >-
  Grade the one measured, EMC-specific expression signal this repository holds — six published
  hypoxia signatures positive in EMC tumour tissue on two array platforms — against the confounds
  that could produce it without any oxygen being low, and state at their true weight the three
  therapeutic classes it points at.
scope: >-
  Two GEO series (GSE24369/GPL6244, GSE4303/GPL3290), 16 EMC tumours total. Transcript level only.
  Not a claim about any agent, any patient, or any oxygen measurement.
audience: [maintainers, autonomous research agents]
date: 2026-08-07
last_verified: 2026-08-07
---

# The EMC hypoxia reading — what survives its confounds, and what it licenses

**Artifacts:** [`emc-hypoxia-confounds.json`](../modalities/emc-hypoxia-confounds.json) (this
memo's numbers; every one is derived, none typed) ·
[`emc-expression-panels.json`](../modalities/emc-expression-panels.json) (the reading being
audited — the six headline t-statistics live there and are **not** restated here) ·
[`emc_hypoxia_confounds.py`](../modalities/emc_hypoxia_confounds.py)

⚠ **Two artifacts this memo depends on do NOT yet exist, and are deliberately named rather than
linked so that stays visible:** `research/modalities/emc-hypoxia-null-background.json` (the
genome-wide null, §2.7 / F11) and `research/modalities/emc-hypoxia-therapeutic-status.json` (the
retrieved clinical record, §5). Both are produced by one $0 CI dispatch —
`emc-expression-datasets.yml` `mode=hypoxia-confounds`. Until they land the audit reports those two
readings as **NOT TAKEN** and **NOT RETRIEVED**, which is not the same as a pass and is not the same
as a negative. **A link to a file that does not exist would make an absent reading look like an
available one**; the link goes in when the file does.

⛔ **THE CEILING ON EVERYTHING BELOW.** These are transcript levels in 16 archival tumours on two
decade-old array platforms, uncorrected for multiple testing. A hypoxia metagene is a
transcriptional shadow of hypoxia; **no oxygen was measured**, no pimonidazole was stained, and no
hypoxia signature has ever been calibrated in EMC or in any myxoid sarcoma. Nothing here is
evidence of efficacy, selectivity, safety, a therapeutic window or clinical readiness for any agent,
and it cannot become that evidence from public expression data.

---

## 1 · Why this reading is worth auditing rather than announcing

It is the first time this repository has **measured EMC's own biology** rather than reasoned about
its fusion, and the direction is positive on both series. That combination is exactly the shape of
result that is most often a confound, and there is a specific reason to be careful here: the
strongest *preclinical* support for hypoxia-directed therapy in EMC — the dose-dependent
radiosensitivity plus hypoxia-prodrug potentiation result (**PMID 32948981**) — was run in
**H-EMC-SS**, whose identity this repository has determined is disputed and which it grades
`NOT_FUSION_POSITIVE_PER_CURATED_RECORD`. That use is classified `invalidated`; the canonical
correction is [`emc-surface-target-landscape.md` → Amendment 1](./emc-surface-target-landscape.md)
and this memo does not restate it.

So the hypoxia premise in EMC currently rests on **nothing that is both EMC and fusion-positive**.
This reading is the first candidate replacement, which is precisely why it has to be graded hard
before it is used.

---

## 2 · The confounds, and which ones the data can actually address

### 2.1 · Comparator composition — TESTED, and it does not explain the signal

The pooled contrast hides that the two series' comparator arms are **opposite** in the property that
matters:

| series | EMC | comparator arm | myxoid comparators |
|---|---|---|---|
| GSE24369 / GPL6244 | 6 | 17 low-grade fibromyxoid sarcoma + 6 myxofibrosarcoma + 6 desmoid fibromatosis | **23 of 29** |
| GSE4303 / GPL3290 | 10 | 3 DFSP + 3 GIST | **0 of 6** |

If a myxoid, hypocellular, poorly vascularised matrix produced a hypoxia signature for **physical**
rather than oncogenic reasons, the contrast should collapse against myxoid comparators. **It does
not.** Re-scoring GPL6244 with the comparator arm restricted to the 23 myxoid tumours versus the 6
non-myxoid ones gives effect sizes that are the same to within noise across all six signatures
(four marginally larger against non-myxoid, two marginally larger against myxoid). The
myxoid-matrix explanation gets **no support** from the one within-platform test that can address it.

Two things this does not settle. Desmoid fibromatosis is collagen-rich rather than myxoid but is
**also** hypocellular and paucivascular, so it controls the matrix-abundance half of the physical
hypothesis and not the cellularity half — it is the closest thing to a non-myxoid comparator in
either series and it is not a clean one. And GPL3290 has **no** myxoid comparator at all, so on that
series the test cannot be run.

⚠ **The two platforms' effect sizes may not be compared with each other**, and an earlier reading of
this data that did so was wrong. GPL6244 carries single-channel intensities; GPL3290 carries
two-colour log-ratios against a reference pool. A within-sample *z* has a different scale on each.
Only the **direction** and the **per-platform** resampling result travel between them.

Also checked: GPL6244 carries five solitary fibrous tumours and **two pooled skeletal-muscle RNA
samples**, which would be a severe confound in a comparator arm. They are classified `unclassified`
and are excluded from **both** arms.

### 2.2 · The two-colour reference pool — TESTED, and it is not the explanation

GPL3290 is a two-colour print run, so every value is a ratio against a reference pool, and a sample
ratioed against a *different* pool carries a gene-specific offset that within-sample
standardisation cannot remove. Reading the pool token from the verbatim GEO annotations rather than
from the class labels: EMC and DFSP are annotated `CRH`/`CRH-mRNA`; **the three GIST samples are
`UHR`** — a different pool. Restricting the comparator arm to the three pool-matched DFSP samples,
all six signatures stay positive (*t* = +2.36 to +4.27). The signal is not a reference-pool artefact.

⭐ **§§2.3–2.5 are read on the MERGED gene cache.** The panels want list never asked for PECAM1,
VWF, CDH5, PTPRC, CD68 or most of the proliferation set, so those proxies were three- and
four-gene stubs and were reported as instrument limits. The CI background fetch requested them by
name; the audit now merges the two caches after checking that the **411 and 434 genes present in
both are value-identical**, so a disagreement between two independent parses of the same matrices
would raise rather than average. Every proxy below is 8–11 genes, and **all three moved in the same
direction they already pointed** — which is what a better-powered version of the same measurement
should do, and is worth noting precisely because it is not guaranteed.

### 2.3 · Proliferation — the platform split is sharper than it first looked

Eight proliferation genes readable on both. The module contrast is *t* = **+0.39** on GPL6244
(flat) and *t* = **+2.85** on GPL3290, and it correlates with the hypoxia score across samples on
both (*r* = +0.61, +0.66). So on GPL6244 — where proliferation is flat — it **cannot** be driving
the contrast; on GPL3290 it is a live partial explanation and the correlation is the strongest of
any confound tested there. MKI67's own array percentile in EMC is **0.516** (GPL6244) and **0.153**
(GPL3290): EMC is not proliferative in absolute terms on either platform, and the GPL3290 "up" is
relative to two comparators that are lower still.

### 2.4 · Vascularity — CONSISTENT WITH THE READING, on both platforms

Eleven endothelium-restricted transcripts (KDR, FLT1, TEK, TIE1, CLDN5, ESAM, ROBO4, EMCN, PECAM1,
VWF, CDH5 — deliberately **excluding** VEGFA and ANGPT2, which are HIF-driven and would make this a
copy of the hypoxia read) are **lower** in EMC on both platforms (*t* = −3.73, −1.73) and
**negatively** correlated with the hypoxia score across samples on both (*r* = −0.53, −0.65). That
is the direction a hypovascular tissue predicts, and it is now the most consistent cross-platform
confound reading in the audit.

⚠ It is still a **transcript proxy for vessel content in bulk tissue**, not a vessel count. It
cannot distinguish fewer vessels from the same vessels diluted by more matrix — and for the hypoxia
question those are not the same thing, because only the first lengthens a diffusion path.

### 2.5 · Necrosis — NOT DIRECTLY TESTABLE; the available proxy points away from it

**There is no transcript marker of necrosis.** The nearest available proxy is myeloid infiltrate
(eleven genes), and only one direction of it is informative: necrotic tumour recruits myeloid
cells, so a **low** myeloid read is evidence against a necrosis-driven signature, while a high one
would not have been proof of one. Measured: myeloid score **lower** in EMC on both platforms
(*t* = −4.40, −1.60). This argues against necrosis and does not exclude it.

### 2.6 · The signature multiplicity — THE LARGEST CORRECTION IN THIS AUDIT

"All six independent hypoxia signatures are positive on both platforms" is the claim that makes the
reading feel strong, and it is the claim that most needs deflating. Two measurements answer
"are they independent", and they disagree:

- **Gene membership is genuinely distinct.** Pairwise Jaccard between the six sets is **0.04–0.28**;
  546 genes in the union, 377 of them in exactly one set. They are not six copies of one list.
- **Their per-sample scores are not.** Across samples the six scores correlate **r = 0.66–0.95**
  (GPL6244) and **r = 0.73–0.96** (GPL3290).

Different gene lists whose scores move together are **near-parallel measurements of one axis**. So
`all six positive` is **one observation per platform, not six**, and the effective multiplicity is
closer to the number of platforms than to the number of signatures. The naive sign test over the
twelve cells (12/12 positive, 2⁻¹² if independent) is the single easiest over-sell available here;
the audit names it and refuses to compute it, rather than reporting it with a caveat.

### 2.7 · Resampling — and this is where the two platforms genuinely part company

Two different nulls, asking two different questions:

**Label permutation** (given this gene set, is the arm separation more than chance?) — one-sided,
uncorrected:

| signature | GPL6244 *p* | GPL3290 *p* (exact) |
|---|---|---|
| Buffa | 0.015 | 0.0011 |
| Winter | 0.19 | 0.0014 |
| Harris | 0.24 | 0.0015 |
| Elvidge | 0.092 | 0.0029 |
| HALLMARK | 0.074 | 0.00012 |
| GO cellular response | 0.0041 | 0.00037 |

**Leave-one-EMC-tumour-out** — every signature keeps its sign on both platforms, but on GPL6244
**none** stays at |*t*| ≥ 2 across all six drops (Buffa ranges 1.44–3.18), while on GPL3290 **all
six** do.

So: on the platform with 10 EMC tumours and an unmatched comparator arm the reading is strong and
robust; on the platform with 6 EMC tumours and a matrix-matched arm, **two of six** signatures clear
an uncorrected 0.05 and none survives leave-one-out at |*t*| ≥ 2. Both statements are true and the
second one is the one the original framing omitted.

**Random-gene-set null** (given this arm split, is a set of this size unusual?) — this is the test
the signatures do worst on, and its own bias runs the *other* way. Against random sets of matched
size drawn from the cached want list, **6.3–34.0 % of random sets reach or beat the observed *t*** on
GPL6244 and **4.3–20.5 %** on GPL3290; only HALLMARK on GPL3290 falls below 5 %. ⚠ That universe is
**33–34 % hypoxia-signature membership by construction** — it is the want list assembled for these
reads — so a "random" draw from it contains hypoxia genes and the null is inflated toward the
observed value. **Read those fractions as an upper bound on the p-value, not the p-value.**

⭐ **THE GENOME-WIDE NULL HAS NOW BEEN TAKEN, and it is the sharpest result in this memo.** A seeded
random sample of ~3,970 symbols from each platform's own mapped-symbol universe — **2.3 % and 3.1 %
signature membership**, against 33–34 % for the want list, so the bias really did run the way the
paragraph above said. Fraction of random same-size sets reaching or beating the observed *t*:

| | GPL6244 | GPL3290 |
|---|---|---|
| Buffa | 0.1055 | **0.0315** |
| Winter | 0.0575 | 0.061 |
| Harris | 0.1875 | **0.0415** |
| Elvidge | 0.077 | 0.069 |
| HALLMARK | 0.053 | **0.0165** |
| GO cellular response | 0.0655 | **0.022** |

**On GPL6244 not one signature falls below 0.05. On GPL3290 four of six do.** Removing the bias
moved every fraction *down*, as predicted — and it did not move GPL6244's below the line.

⚠ **The two nulls disagree, and the disagreement is informative rather than a defect.** Label
permutation asks whether *these arms* separate on *this* score; the random-gene-set null asks
whether *this set* is special among sets of its size. A signature can pass the first and fail the
second when the arms differ on a broad axis that many gene sets partly report — which, given §3's
finding that the signal is concentrated in the glycolytic members, is the most likely reading here.
Neither null is the "right" one. A reading quoting only the permutation result would be
over-stated; one quoting only the random-set result would be under-stated.

---

## 3 · Is the hypoxia reading downstream of the fusion, or a property of the tissue?

The question is sharp because EWSR1::NR4A3 is a transcriptional driver and its one published direct
transactivation target here is **ENO3, a glycolytic enzyme** (PMID 26310886) — and every published
hypoxia signature is substantially glycolytic. A fusion that drives glycolytic genes and a tumour
that is genuinely hypoxic produce the **same metagene score**.

**Finding 1 — the signal is concentrated in the glycolytic members, on both platforms.** Splitting
each published set into its glycolytic members and the remainder, the glycolytic part carries
**2.9–11.6×** the remainder's effect on GPL6244 and **2.2–5.4×** on GPL3290, in every set that can
be scored both ways (*d* = +0.28 to +0.50 vs +0.02 to +0.15, and +0.87 to +1.10 vs +0.17 to +0.41).
The GO cellular-response set has only two glycolytic members, below the gene floor, so its
glycolytic arm emits UNDERPOWERED rather than a number.

**Finding 2 — but the non-glycolytic remainder is still positive in every set on both platforms**,
and on GPL3290 substantially so (*t* = +2.62 to +4.04; on GPL6244 *t* = +0.28 to +2.35). The reading
is therefore **broader than glycolysis** and a purely metabolic explanation does not cover it.

**Finding 3 — it is not an ENO3 artefact.** The curated glycolytic programme is up on both
platforms and stays up with ENO3 removed and with **every** enolase removed (GPL6244 *t* = +3.66 →
+3.21; GPL3290 *t* = +7.13 → +5.72).

**Finding 4 — the discriminating test. Within the EMC arm, the score does NOT track fusion output.**
Holding the disease constant and letting only the degree of fusion output vary:

| within-EMC correlation with the hypoxia score | GPL6244 | GPL3290 |
|---|---|---|
| **NR4A3** | −0.28 (n=6) | −0.40 (n=9) |
| **ENO3** | −0.91 (n=6) | +0.84 (n=10) |
| **CA9** (score recomputed with CA9 removed) | **+0.53** (n=6) | **+0.89** (n=10) |

NR4A3 is negative on both. ENO3 **flips sign** between platforms, so it reproduces nothing. CA9 — the
most oxygen-restricted HIF1 target available, with no recognised fusion-independent driver here — is
positive on both, and the circularity is handled by removing CA9 from the score it is correlated
against. CA9 is also up between arms on both platforms.

**Finding 5 — the sharper version of the same test, and it points the same way.** Because the
hypoxia score is mostly glycolysis, correlating it with ENO3 partly asks whether glycolysis tracks
glycolysis. The narrower question is whether the **rest of the glycolytic programme, with ENO3
excluded from the score**, rises with ENO3 within EMC tumours. It does not reproduce: *r* = **−0.88**
(n = 6, GPL6244) and **+0.65** (n = 10, GPL3290). So the largest single glycolytic effect on both
platforms — ENO3, the published fusion target, at *t* = +3.61 and +13.22 between arms — sits **on top
of** a glycolytic programme it does not co-vary with. That is the pattern a fusion-driven outlier
over a differently-driven programme makes, and it is not the pattern a fusion-driven programme
makes.

**Reading.** On the evidence available, the axis behaves like **tissue state, not fusion output**:
it tracks the oxygen-specific readout within EMC tumours on both platforms and does not track the
fusion or its published target. ⚠ This is *n* = 6 and *n* = 9–10 with a stated probe caveat (on a
3′-biased or EST-annotated array the NR4A3 probe may sit in the region the fusion replaces; on
GPL3290 five of sixteen samples carry no NR4A3 value at all). It leans; it does not decide.

**Consistent with tissue state, and worth stating:** HIF machinery transcript is flat on both
(*t* = +1.45, +0.90) — which is the **expected** reading under real hypoxia, since HIF1α is regulated
by oxygen-dependent degradation rather than transcription, and therefore carries almost no
information either way. It is reported so that its absence from the argument is visible.

---

## 4 · The matrix reading — an abundant, comparatively UNDER-sulfated matrix

VCAN at the top of the array beside a **down** sulfate-donor module is the tension, and it resolves.

**Up on both platforms:** VCAN (*t* = +3.94, +4.76; EMC array percentile **0.997**, **0.975**),
BGN (+4.14, +3.87; percentile 0.994, 0.992), CD44 (+7.86, +3.04), UST — the 2-*O*-sulfotransferase —
(+3.29, +2.08), CSGALNACT2 (+2.28, +2.31).

**Down on both platforms:** the **PAPS module** (*t* = −2.23, −2.11), driven by **PAPSS2**
(−3.94, −3.12) and the Golgi PAPS transporter **SLC35B3** (−1.99, −6.37); **CHST15** (−6.90, −2.82),
the GalNAc4S-6ST that makes the 4,6-disulfated CS-E unit; **CHST7** (C6ST-2; −3.45, −2.56).

**Flat on both:** **CHST11** (C4ST-1, the principal 4-*O*-sulfotransferase; *t* = +0.07, −0.50).

**Not reproducible — do not build on these:** CHST14 (−5.07 / +2.10), CHST3 (+2.02 / −1.47),
CHSY1 (−2.39 / +3.15), PAPSS1 (−0.75 / +2.25), and **CSPG4 (+7.42 / −0.40)**, which matters because
CSPG4 is a therapeutic-address candidate elsewhere in this repository — on these two series it
does not replicate.

**What it means.** The core proteoglycan is at the array ceiling while the cell's capacity to donate
sulfate is, if anything, lower than in the comparator sarcomas. That is coherent rather than
contradictory: a myxoid matrix is dominated by **water, hyaluronan and versican**, and hyaluronan is
**not sulfated at all** — an abundant versican/hyaluronan matrix needs no extra sulfate donor. CD44,
the hyaluronan receptor, being among the strongest up-calls on both platforms fits the same picture.

**What it rules out.** "EMC makes more highly sulfated chondroitin sulfate" is **not supported**: the
donor module is down, the principal 4-*O*-sulfotransferase is flat, and the enzyme that builds the
CS-E (4,6-disulfated) unit — the epitope most often invoked in oncofetal-CS narratives — is **down on
both platforms**. A substrate-reduction or sulfation-pattern-targeting hypothesis for EMC gets no
support from this data; what the data support is an **abundant, comparatively under-sulfated** CS
matrix.

⛔ **A sulfation pattern has no gene.** Sulfotransferase and PAPS-module transcript is a proxy for
the *capacity* to sulfate, never a measurement of the sulfation state of anything. Nothing here says
which CS epitopes are on EMC tissue; only a stain, a binding assay or glycomics can. Intracellular
PAPS is set by flux and sulfate availability as much as by synthase transcript, so a low PAPSS2 read
is not a measurement of low PAPS.

**And it connects to §2.4.** An abundant, water-swollen, versican/hyaluronan matrix with reduced
endothelial content is the physically obvious way to get long diffusion distances. That is a
*mechanism* consistent with the hypoxia reading — not a second piece of evidence for it, since the
two readings come from the same 16 tumours.

---

## 5 · The therapeutic hooks, at their true weight

⛔ **What this reading licenses:** a hypothesis about tissue state that is worth putting into the
literature **because it is EMC-specific and measured**, and that names three drug classes as things
somebody could ask about. That is the entire licence.

⛔ **What it does not license:** anything about activity, selectivity, safety, a therapeutic window
or clinical readiness for any agent in any of these classes in EMC. A transcriptional shadow of
hypoxia in 16 archival tumours is not a patient-selection biomarker, is not a companion diagnostic,
and does not support giving anyone anything.

**The clinical record below was RETRIEVED, not recalled**, from ClinicalTrials.gov API v2 and
PubMed on 2026-08-07. Every query and every returned row is in
`research/modalities/emc-hypoxia-therapeutic-status.json`, which is its one home; the summary in
`emc-hypoxia-confounds.json` → `therapeutic_hooks` adds no fact that file does not carry.

⚠ **Read the registry for STATUS, never for OUTCOME.** ClinicalTrials.gov records that a trial
completed, not what it showed. Where a trial's own `whyStopped` field is quoted below it is verbatim
from the registry; nowhere does this memo state a trial's *result*, because the registry cannot
supply one and this session did not read the publications.

| class | registered studies (ph 3) | sarcoma-indexed | what the record actually says |
|---|---|---|---|
| **Hypoxia-activated prodrugs** (evofosfamide/TH-302, tirapazamine, PR-104, tarloxotinib, CP-506, apaziquone, banoxantrone) | **109** (17) | **9** | ⚠ **This class has already been taken into soft-tissue sarcoma at phase 3 and the follow-on is gone.** `NCT01440088` — TH-302 + doxorubicin vs doxorubicin alone, **PHASE 3, COMPLETED**; its continuation `NCT02712567` (SARC021C) is **NO_LONGER_AVAILABLE**; the Japanese phase 2 `NCT02255110` is **TERMINATED**. Two further TH-302 trials carry registry `whyStopped` text of *"the futility boundary was not met and the study was stopped"* (`NCT02093962`) and *"company decision to discontinue"* (`NCT02047500`), and three PR-104 trials are terminated, one for *"low probability of clinically significant result"* (`NCT00862134`), one *"poorly tolerated"* (`NCT00862082`). |
| **HIF-pathway agents** (belzutifan/MK-6482/PT2977, PT2385, ARO-HIF2, EZN-2968) | **109** (24) | **0** | ⚠ **A large, active class that has never been indexed to sarcoma at all** — and **isoform** decides whether that matters. The approved agent is HIF-2α-selective, i.e. **EPAS1**, and EPAS1 here is *t* = **+2.55** (GPL6244) and **+0.26** (GPL3290): not reproducibly elevated, with HIF machinery overall flat (§2, §3). A class hook that ignores which isoform moves is not a hook. |
| **CA-IX-directed agents** (girentuximab and the ⁸⁹Zr line, SLC-0111, DTP348, CA9 CAR-T) | **30** (6) | **1** | ⚠ **The single sarcoma-indexed trial is IMAGING, not therapy** — `NCT06447103`, an ⁸⁹Zr-DFO-GmAb PET/CT scan study, RECRUITING. `SLC-0111`'s pancreatic trial `NCT03450018` is TERMINATED (*"changing treatment landscape"*), `DTP348`'s `NCT02216669` WITHDRAWN (*"no financial agreement"*). This is a small class, mostly early phase, with its sarcoma exposure so far confined to imaging. |

**And the question a reader will ask, asked directly rather than inferred:** ClinicalTrials.gov
returns **23 registered trials whose condition list names extraskeletal myxoid chondrosarcoma**
(query in the artifact). Scanning their titles, none is a trial of any agent in the three classes
above — they are sarcoma-basket, radiotherapy, and targeted/immunotherapy studies (e.g.
`NCT02066285`, pazopanib in solitary fibrous tumour **and EMC**). ⚠ That is a reading of trial
TITLES and condition lists, not of their intervention lists, so it is a strong indication and not a
proof of absence.

**The honest ranking among the three**, on this data alone: CA-IX has the best measured basis here —
CA9 is up between arms on both platforms and is the one readout that tracks the rest of the
signature within EMC tumours on both (§3). It also has the **least** clinical baggage of the three
in sarcoma, and by far the least clinical development overall. Those two facts pull in opposite
directions and neither is evidence of anything about EMC. ⛔ It does **not** make a CA-IX-directed
agent a candidate: the address is a **surface protein nobody has measured in EMC**, and a CA9
transcript reading cannot become that measurement.

⛔ **What the prodrug row means for this memo's own framing.** The class whose mechanism this
reading points at most directly is the class that has already had its phase 3 in soft-tissue
sarcoma, and the strongest EMC-specific preclinical support for it is `invalidated` here (§1). A
hypoxia signature in EMC is therefore a reason to ask a **question**, not a reason to revisit that
class — and any sentence that reads the other way is over-reading this memo.

---

## 6 · Falsifiers

Each claim this memo makes, and the single observation that would kill it.

| # | claim | falsifier |
|---|---|---|
| F1 | EMC tumours carry a higher hypoxia-signature score than comparator sarcomas | a third EMC series, with a comparator arm of either composition, in which the six scores are null or negative. Two series is not a replication set. |
| F2 | The signal is not produced by myxoid matrix content | a series in which EMC is contrasted against **myxoid** comparators and the contrast disappears — GPL6244 is that test and it did not disappear, so the falsifier is a second run of the same design that does. Equivalently: a per-sample matrix score that, when regressed out, removes the contrast. |
| F3 | The signal is not produced by proliferation | a series where EMC and comparators are matched on MKI67/TOP2A and the contrast disappears. Partly open already: proliferation is flat on GPL6244 and up on GPL3290. |
| F4 | The signal is not produced by necrosis | a matched histopathological review scoring necrosis on these blocks and finding it higher in EMC. **Not answerable from transcript data** — the myeloid proxy points away from necrosis, and that is the most this instrument can say. |
| F5 | The signal is not a reference-pool artefact | it is already falsifiable and did not falsify: the pool-matched DFSP-only contrast stays positive. A failure of that restricted contrast would kill it. |
| F6 | "Six signatures" is one observation per platform, not six | a per-sample score correlation near zero between the six sets on a new dataset. The measured correlations are §2.6's and this row does not restate them. |
| F7 | The axis is tissue-intrinsic rather than fusion-driven | EMC tumours (or an isogenic fusion-inducible model) in which hypoxia score rises with fusion output. The within-EMC NR4A3 correlation is negative on both platforms; a positive, reproducible one would overturn this. |
| F8 | The glycolytic elevation is not an ENO3 artefact | already falsifiable and did not falsify: removing every enolase leaves *t* = +3.30 / +5.74. |
| F9 | EMC's CS matrix is abundant but comparatively under-sulfated | a glycomics or antibody measurement on EMC tissue showing normal or elevated 4-*O*/CS-E sulfation. **This is a capacity proxy, not a sulfation measurement**, so a wet-lab result outranks it outright. |
| F10 | CSPG4 is not a reproducible up-call in EMC tumour tissue | a third series in which CSPG4 is up. It is +7.42 on one platform and −0.40 on the other. |
| F11 | The signature is not simply a set of the right size | ⭐ **TAKEN, and it FIRED on one platform.** Against the genome-wide null (§2.7) not one of the six clears 0.05 on **GPL6244**; four of six do on GPL3290. So on the 6-tumour, matrix-matched series the signature is not distinguishable from a gene set of its size, and the memo's claim is restricted to GPL3290 accordingly. The falsifier that remains is the same test on a third series. |

---

## 7 · What this route is for

**The paper it belongs to:** an EMC tissue-biology short report — *"Extraskeletal myxoid
chondrosarcoma tumours carry a hypoxia-associated, glycolysis-weighted transcriptional programme and
an abundant but comparatively under-sulfated chondroitin-sulfate matrix, in the only two publicly
readable EMC expression series"* — reporting the confound audit **as the result**, including the
platform disagreement and the multiplicity deflation, rather than the headline.

**What is missing before it is worth posting:** a **third EMC series** (§7.1) — that is the only
open item. The genome-wide null landed and fired on GPL6244; the clinical record was retrieved and
§5 states it. Nothing here needs a wet lab to be *publishable* — it needs one to be *actionable*,
which is a different sentence and this memo does not blur them.

**And the headline the abstract may carry, after all of the above:** *on the only two publicly
readable EMC series, EMC tumours score higher than comparator sarcomas on six published hypoxia
signatures; the effect is robust on the 10-tumour series by permutation, leave-one-out and a
genome-wide gene-set null, and is not distinguishable from a random gene set of the same size on
the 6-tumour series; it is not explained by comparator myxoid composition, reference pool,
proliferation or a necrosis proxy; it is concentrated in the glycolytic members but not confined to
them; and within EMC tumours it tracks CA9 and not fusion output.* Every clause there is measured,
and the two that a reader would most want to be stronger are stated as the limits they are.

### 7.1 · The third series is not missing — it is unread, and for an instrument reason

⭐ **`GSE28866` is the replication candidate, and what stops it is a probe→symbol bridge, not data.**
The five EMC expression series this repository has found are characterised in
[`emc-atr-vulnerability.json`](../modalities/emc-atr-vulnerability.json) →
`part_b_emc_tumour_signature.series_readability`, which is their one home. Three of the five are
unreadable and the reasons are not the same:

| series | why it is not used |
|---|---|
| `GSE43632`, `GSE80126` | **n_EMC = 1** each. No contrast is computable at any effort. Genuinely closed. |
| `GSE28866` | **4 EMC vs 27 comparators, and ZERO concepts scored on GPL10999** — that platform's probe mapping rate is recorded as `None`, i.e. the bridge from its probes to gene symbols did not resolve. ⛔ **That is an instrument limit, not a biological null**, and it is the same class of problem the GPL3290 EST-accession bridge already solved for `GSE4303`. |

Why it is worth the attempt rather than merely possible: `GSE28866`'s comparator arm carries **six
myxoid liposarcomas** — a myxoid *and* fusion-driven comparator that neither readable series
contains. That is a sharper version of §2.1's test than either platform here can run, and it
addresses F1 and F2 at the same time. ⚠ **Nothing here says the bridge will resolve** — GPL10999 was
not attempted in this session and the honest state is "unattempted", not "solvable". The
falsifiable form is: *a run that attempts the GPL10999 bridge either resolves enough probes to score
a contrast, or records why it cannot* — and either outcome is worth more than the current silence.
