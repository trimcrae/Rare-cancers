---
id: DOC-EMC-MTAP-PRMT5
title: MTAP-locus loss and methylosome elevation in extraskeletal myxoid chondrosarcoma — a biomarker-selected hypothesis, and the one cheap test that would settle it
level: L3
kind: manuscript
status: live
canonical_for: ["the 2026-08-09 EMC MTAP/PRMT5 reading and its hypothesis"]
purpose: >
  State a therapeutic hypothesis nobody has asked about this disease — that it may carry the MTAP
  locus deletion that selects the PRMT5/MAT2A axis — give the public-data reading that raises it,
  bound that reading honestly, and specify the single inexpensive assay that would confirm or kill it.
scope: >
  L3. Two public archival expression series, 16 EMC tumours in total, transcript level only. This
  document raises a hypothesis and names its falsifier. It reports no experiment in EMC cells, no
  drug exposure, and no patient.
audience: [maintainers, external reviewers, autonomous research agents, collaborators]
date: 2026-08-09
last_verified: 2026-08-09
related: [DOC-MODALITY-CENSUS, DOC-EMC-UNEXPLORED-LANES]
---

# MTAP-locus loss and methylosome elevation in EMC

> ⛔ **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness for any agent
> in any disease.** This is a hypothesis raised from public transcript data in 16 archival tumours.
> It has never been tested in an EMC cell, and the assay that would test it has never been run on an
> EMC block.

---

## Summary

Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare translocation sarcoma driven by an
NR4A3 gene fusion. It has no targeted agent. The systemic options that carry any disease-specific
evidence are a small set of multi-kinase antiangiogenic inhibitors, an anthracycline backbone and a
minor-groove binder — an arsenal of about eight drug classes, only one of which has a meaningful
response record.

**One class of therapeutic that is selected by a genetic state rather than by a growth rate has never
been considered for this disease at all**: inhibition of the PRMT5 methylosome, and of the MAT2A
enzyme upstream of it, in tumours that have lost the *MTAP* locus. That class is unusual in oncology
because its window is genetic — cells retaining *MTAP* are comparatively spared — and because its
selecting feature is a homozygous deletion that a routine immunohistochemical assay can call.

Reading two public archival expression series, we find that:

- the three-gene ***MTAP* / *CDKN2A* / *CDKN2B* locus reads LOWER in EMC than in comparator
  sarcomas** on the platform where the read is adequately powered;
- the **PRMT5 methylosome reads HIGHER in EMC on both platforms**, and *MAT2A* sits in the top
  percentiles of its own array in both series.

That combination is the shape an *MTAP*-deleted, methylosome-loaded state makes on an expression
platform. ⛔ **It is not a copy-number call, and this document does not make one.** A transcript is
not a copy number; the locus read is underpowered on the second platform; and the whole observation
rests on six tumours on one array and ten on another.

**The hypothesis is therefore stated as a question with a named, cheap answer:** *MTAP*
immunohistochemistry on archival EMC blocks — a stain already used routinely as a surrogate for
locus deletion in other tumour types — would confirm or kill it outright, in a single afternoon, on
material that already exists in pathology archives.

---

## 1 · Why this class, and why nobody has asked

Two properties make this class worth a question in an ultra-rare disease.

**It is selected by a genetic state, not by proliferation.** Most systemic options that reach a
sarcoma are proliferation-coupled, and EMC is a slow-cycling tumour with an indolent natural history
— the profile in which division-rate-dependent mechanisms are weakest. A class selected by a
deletion is indifferent to how fast the tumour divides.

**Its window is genetic rather than pharmacological.** Loss of *MTAP* changes the metabolic state of
the cell in a way that makes the PRMT5 methylosome comparatively more sensitive to inhibition;
normal cells, which retain *MTAP*, are comparatively less so. ⚠ *Comparatively* is doing real work
in that sentence and this document does not strengthen it: a differential sensitivity established in
engineered and pan-cancer settings is not a therapeutic window in a patient, and nothing here claims
one.

**Why it was never asked here.** Not oversight — instrument shape. A modality census of this disease
completed on 2026-08-09 enumerated 217 categories of cancer treatment and found that the classes
selected by a molecular state had been dismissed as a group, largely because the relevant biomarker
had never been read. The *MTAP* locus in particular appears in **no prose document in this
repository**, and no published EMC series reports it. The class was not rejected; nobody had looked.

## 2 · What was measured

**Two public series, and they are the only readable EMC expression data that exists.**

| series | platform | EMC | comparator arm |
|---|---|---:|---|
| GSE24369 | GPL6244 | 6 | 29 comparator sarcomas, itself including a FET-rearranged histology |
| GSE4303 | GPL3290 | 10 | 6 |

Genes were read as a *z*-score against each array's own probe distribution, and groups scored as the
mean difference between the EMC and comparator arms in standard-deviation units. The reading, the
per-sample values and the probe mappings live in
[`emc-expression-panels.json`](../modalities/emc-expression-panels.json), which owns every figure
quoted here; the grading against this hypothesis lives in
[`census-route-expression-grading.json`](../modalities/census-route-expression-grading.json).

⚠ **A gene with no probe mapping is recorded as unreadable and never as unexpressed.** That rule is
the source artifact's, it is enforced there, and it matters below: one of the three locus genes has
no probe on the second platform, which is why the locus read is powered on one platform only.

## 3 · The reading

**The locus.** Scored as the three-gene group *MTAP* + *CDKN2A* + *CDKN2B*, the locus is **lower in
EMC than in comparator sarcomas on GPL6244**, with all three genes readable and a *t* statistic of
−4.06. On GPL3290 only two of the three genes are readable, which falls below the panel's own floor
for emitting a score, so **no score is emitted there** — an instrument limit, not a reading of the
biology.

**The methylosome.** The PRMT5 methylosome group is **higher in EMC on both platforms**
(*t* = 3.11 and 3.89), as is the methionine-salvage context group (*t* = 4.26 and 2.07). At the
single-gene level *MAT2A* sits at the 99th percentile of its array on GPL6244 and the 84th on
GPL3290, and *PRMT5* at the 91st and 59th.

**What that combination is, and is not.** Loss of the *MTAP* locus and a loaded methylosome are the
two halves of the state this class is given for, and both are present in the direction the
hypothesis requires. ⛔ **Neither half is established by this reading.** The locus read is a
transcript-level shadow of a copy-number event, powered on one platform, in six tumours. An elevated
methylosome is an abundance, and abundance is not dependency.

⚠ **A confound this reading cannot exclude, stated because it is the most likely alternative.**
*CDKN2A* and *CDKN2B* sit beside *MTAP* and are lost with it in most tumours that lose it — but they
are also silenced by mechanisms that leave *MTAP* intact. A three-gene locus group can therefore
read low because of a *CDKN2A* event that has nothing to do with *MTAP*. Only a gene-level
copy-number or protein call separates those, and this data does not.

## 4 · The one test that would settle it

**MTAP immunohistochemistry on archival EMC tissue.**

The assay is routine, is already used as a surrogate for locus deletion in other tumour types, runs
on formalin-fixed archival material, and needs neither fresh tissue nor a cell line. EMC blocks exist
in sarcoma pathology archives and in the two-institution cohorts already reported in the literature.
For a disease with no targeted agent, this is close to the cheapest decisive experiment available
anywhere in its portfolio.

**What each outcome means, stated in advance:**

| result | what follows |
|---|---|
| MTAP protein **retained** across EMC cases | the hypothesis is dead, the locus reading is a *CDKN2A* shadow, and this document becomes a published negative that stops the next person repeating it |
| MTAP protein **lost** in a subset | the subset is the first genetically selected treatment group ever defined in this disease, and the class becomes askable |
| MTAP protein lost in **most** cases | the same, at a frequency that would make the class worth a formal request |

⚠ **In every branch the result is publishable and the negative branch is the more likely one.** That
is stated deliberately: a hypothesis whose refutation is worth as much as its survival is the
kind an ultra-rare disease can afford to test.

## 5 · Falsifiers

| # | claim | the observation that would kill it |
|---|---|---|
| F1 | the MTAP locus reads low in EMC relative to comparator sarcomas | a third EMC series in which the locus group is null or higher |
| F2 | the low locus read is not driven by *CDKN2A* alone | gene-level copy-number showing *CDKN2A* loss with *MTAP* intact |
| F3 | the methylosome reads high in EMC | a third series in which the PRMT5 group is null or lower |
| F4 | the reading is not a comparator artefact | the same contrast against a different comparator arm, disappearing |
| F5 | the locus signal is not a proliferation or cellularity effect | a series matched on proliferation in which the contrast disappears |
| F6 | MTAP protein is lost in some EMC | MTAP immunohistochemistry retained across an EMC series — **the decisive one, and the cheapest** |

## 6 · Limits

- **Sixteen tumours, two decade-old array platforms, uncorrected for multiple testing.** Two series
  is not a replication set, and the locus result rests on six tumours on one of them.
- **A transcript is not a copy number.** The class is selected by homozygous deletion. Expression can
  triage that question and cannot answer it, which is why §4 rather than §3 is the point of this
  document.
- **No EMC cell line carries the fusion in any public dependency dataset**, so no dependency evidence
  for this axis in this disease exists or can be generated computationally. Anything transferred from
  other sarcomas is a class prior and is labelled as one.
- **Abundance is not dependency.** An elevated methylosome does not establish reliance on it.
- **Nothing here has been tested in an EMC cell.** No agent in this class has been given to a patient
  with this disease, and this document does not propose that one should be.
