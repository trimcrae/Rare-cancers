---
id: DOC-VIEW-RT-MDT-LUNG
title: RT-MDT-LUNG — Metastasis-directed ablative radiotherapy to lung metastases (SABR/SBRT)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Has the standard-of-care oligometastatic intervention ever been tried on EMC lung metastases, and does the evidence said to rule radiotherapy out in this disease actually bear on it?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-MDT-LUNG — Metastasis-directed ablative radiotherapy to lung metastases (SABR/SBRT)

**Family:** [ST-LOCOREGIONAL](L1-st-locoregional.md) · **state:** ✓ ready · computed · confidence low · verified 2026-08-10

**Grade** (owned by [`research/literature/emc-rt-lung-mets-findings.json`](../../research/literature/emc-rt-lung-mets-findings.json)): ◔ THE PRACTICE IS REAL; THE ARGUMENT FOR IT IS ALREADY PUBLISHED (2026-08-10, corrected the same day it was written). ⛔ THIS ROUTE'S ORIGINAL GRADE CLAIMED A CATEGORY ERROR NOBODY HAD NAMED — that the field reads conventionally fractionated primary-site nulls as evidence about ablative dose to a metastasis. The 2025 comprehensive review (PMID 41055792) names it, in BED terms: conventional EBRT 'typically deliver[s] BED levels insufficient for long-term control' against 142 Gy at α/β = 4, hypofractionation 'may have contributed to overcoming the intrinsic radioresistance of EMC', 'SBRT may also be an option instead of surgery', and 'metastasis-directed local therapy should follow uniform MDT criteria'. ⛔ THE REFUTING FULL TEXT WAS ALREADY RETRIEVED IN literature-cache WHEN THE CLAIM WAS WRITTEN, cited as a search hit and never opened. ⭐ WHAT SURVIVES IS SMALLER AND QUANTITATIVE: at least seven reported deliveries exist scattered across case reports and one review that garbles two of their attributions, and nobody has tabulated them by dose, BED and duration of local control, nor tested whether the α/β = 4 borrowed from generic sarcoma fits the EMC observations. ⛔ That is a synthesis, not a reappraisal, and it may not carry a paper by itself — publication bias across ~7 uniformly positive anecdotes will not support a dose-response claim. Superseded, retained: the category-error framing.

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

This disease is extremity-primary, lung-metastasis-dominant and slow, and 63% of its metastatic patients have disease confined to the lungs — the exact anatomical situation metastasis-directed radiotherapy exists for. It was never considered here because the disease is labelled radioresistant, and that label rests entirely on conventionally fractionated dose to primary tumours. Meanwhile four separate groups have quietly given ablative radiotherapy to metastatic EMC and published what happened, and nobody has assembled those reports or noticed that the exclusion rests on a category error.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-EMC-RT-LUNG-METS` | four published deliveries of radiotherapy to metastatic EMC across four modalities, two to lung; five papers total naming EMC and stereotactic radiotherapy in title or abstract; and the primary-vs-metastasis split running through every study on both sides of the radioresistance question | `direct` |
| `ART-EMC-RT-LUNG-METS` | 63% of metastatic patients have disease confined to the lungs and lung is the first site in 80%, from retrieved full text — the eligibility numerator RT-LUNG-DIRECTED records as uncurated | `direct` |

## Remaining unknowns

- ⛔ Whether ANY contribution survives that the 2025 review has not already made in prose. This is now the route's gating question and it was not asked before the route was minted.
- Dose, fractionation, lesion size and duration of local control in the one SABR report — none is in its abstract and the full text is open access and unfetched.
- What the whole-lung radiotherapy report actually found. It is the single most on-point paper in the record, it carries no indexed abstract, and it returns HTTP 403 to the sandbox and to a runner alike.
- Whether any sarcoma-wide SABR series reports an EMC subgroup, which would convert borrowed evidence into histology-specific evidence.
- ⚠ How many EMC metastases have been irradiated and progressed. This is unknowable from the published record and it is the number that would decide the route — four case reports with four good outcomes is what a literature looks like when nobody publishes the failures.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Full-text extraction of dose, fractionation and control duration from the reported cases | ⛔ none built | yes | — |
| A histology-specific outcome series, which only a collaborating centre or a sarcoma registry could assemble | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-LUNG-DIRECTED](L2-rt-lung-directed.md) | how the lung lesion is reached | `BLK-NO-CURATED-CLINICAL-DATA` | that route is regional perfusion, inhaled delivery and percutaneous ablation — ways of reaching lesions surgery cannot. This one is external-beam ablative radiotherapy, which is the standard-of-care oligometastatic intervention and the only modality actually delivered to EMC lung metastases in the published record |
| [RT-RT-INTENSIFY](L2-rt-rt-intensify.md) | whether the question is dose quality at the primary or dose geometry at the metastasis | — | that route asks whether particles, brachytherapy or radiosensitisation rescue a contested PRIMARY-site result. This one argues those primary-site results were never evidence about ablative dose to a METASTASIS, so the exclusion it inherits rests on a category error rather than on a measurement |

## Readiness — what this could become today

**`internal_note`**

The novelty claim that justified a standalone paper is refuted by a 2025 review that makes the same argument more precisely. What remains is a dose-and-outcome table over roughly seven uniformly positive anecdotes, which is a useful addendum to another paper and is not a preprint on its own.

**Missing:**
- a quantitative contribution that a 2025 review has not already made in prose — currently the only candidate is the BED-versus-local-control tabulation, and roughly seven positively-selected cases will not support it
- the full text of the whole-lung radiotherapy report, blocked at both the sandbox and the runner
- primary reports for the three cases the 2025 review names with garbled or duplicated attributions

## Where this route ends — the paper

**[PUB-LOCOREGIONAL](L3-publications.md)** — *Anatomical selectivity in an indolent, extremity-primary, lung-metastasising sarcoma* (unwritten)

`contributing` · ◔ `outlined` · aimed at `preprint`

**This route contributes:** The one anatomical-selectivity strategy in this family that has actually been delivered to patients with this disease, and the reappraisal showing why the evidence said to rule it out was never about it.

**The paper would claim:** A disease that is extremity-primary, lung-metastasis-dominant and slow enough for local control to matter is unusually well matched to locoregional and radiation-based treatment, and a portfolio containing no physical intervention at all had never assessed any of it.

**It is not written because:** ⚠ ITS BLOCKER WAS HALF RIGHT, AND THE HALF IT GOT WRONG IS THE INTERESTING ONE. The arithmetic ran on 2026-08-09 under the repository's binding pooling contract, and it splits cleanly: the SIZE OF THE PROBLEM is computable and now computed — roughly a third of localised patients develop distant disease and a substantial minority recur locally, each pooled over three or four non-overlapping series with its heterogeneity range shown. ⛔ But the ELIGIBILITY criteria are not extractable, because they were never curated: no cohort carries a primary anatomical site field, metastatic site appears once in free text rather than as data, and no cohort records lesion burden or time-to-metastasis. So the paper has its denominator and not its numerator. ⭐ That is still writable and is arguably a better paper: the argument, the sized problem, and an explicit statement of which single curation step would convert it into an eligible fraction — which is $0 for the open-access series. ⛔ Superseded, retained: "the eligibility arithmetic has not been extracted from the curated cohorts yet", which reads as though extraction were the missing step. For two of the three quantities no extraction could have produced them.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

Every remaining step is a $0 literature fetch, and the concept paper needs no compute, no wet lab and no data this repository lacks.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-LOCOREGIONAL](L1-st-locoregional.md), which is where these are asserted — a family limitation binds every route inside it.*

- Anatomical selectivity works only for anatomically confined disease, so every route here is limited to a subset of patients whose size has not been established in this disease.
- The portfolio contains no physical intervention of any kind, so it holds no instrument, no prior result and no reviewer competence in this family — the in-silico half of every route here is literature synthesis rather than computation.
- A modality dosed per unit volume but delivered per cell is penalised in a matrix-dominated tumour with few cells per unit volume, and that correction has already closed one route in this area.
- Nothing in this family asserts efficacy, safety, a therapeutic window or clinical readiness.

## Best next action

Do NOT write the concept paper as framed. Extract dose, fractionation, BED and local-control duration for every reported irradiated EMC metastasis into the findings artifact, and decide from the assembled table whether anything survives that the 2025 review has not already said.

*Cost:* $0

[← ST-LOCOREGIONAL](L1-st-locoregional.md) · [← L0](L0-ecosystem.md)
