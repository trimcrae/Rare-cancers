---
id: DOC-EMC-OLIGOMET-RT-CONCEPT
title: Metastasis-directed radiotherapy in extraskeletal myxoid chondrosarcoma — concept paper proposal
kind: memo
status: live
purpose: Establish whether ablative radiotherapy has ever been delivered to EMC lung metastases, and whether there is a concept paper in it worth writing.
scope: One route (RT-MDT-LUNG). Proposal only — this is not the manuscript.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-10
last_verified: 2026-08-10
---

# Metastasis-directed radiotherapy in EMC — is there a concept paper here?

**Yes, and it is a stronger one than the route board currently implies.** This file is the proposal, not
the manuscript. Every identifier it uses is anchored in
[`emc-rt-lung-mets-findings.json`](../literature/emc-rt-lung-mets-findings.json), which in turn points at
the Europe PMC index that produced it.

⚠ **Read the "what would sink it" section before writing a word of the paper.** Two of the four
objections there are serious, and one of them is the reason this is filed as a proposal rather than an
outline.

---

## 1 · The empirical answer to the question that started this

**Has anyone tried radiation on lung mets for EMC?** Yes — four times in the searchable record, in four
different modalities, and never as a studied question.

| what | modality | n | what happened |
|---|---|---|---|
| PMID 41323055 (2025) | SABR, alternating with surgery | 1 | All metastatic sites treated by excision or SABR alone on three occasions; complete or major response each time |
| PMID 36944557 (2023) | bilateral whole-lung EBRT | 2 | Reported sustained symptomatic benefit ⚠ **full text unread — Cloudflare-blocked, no indexed abstract** |
| PMID 35494187 (2022) | HDR interstitial brachytherapy, 30 Gy/2 fx | 1 | Durable local control at three separate metastatic sites, no severe toxicity |
| PMID 40885991 (2025) | palliative RT to metastases | 2 | Exposure recorded in a 171-patient cohort; **no outcome reported** |

Against a denominator of five papers that mention EMC and stereotactic radiotherapy in title or abstract
at all — four of which are intracranial or cardiac primaries and a review.

**So the honest summary is: it has been done, it has never been studied, and every time someone has
written it up it worked.** That last clause is also the single biggest threat to the paper, and §5 treats
it as such.

## 2 · The claim the paper would make

> Extraskeletal myxoid chondrosarcoma is the closest thing in solid-tumour oncology to a natural
> experiment for metastasis-directed therapy, and the field has never run it.

Not "SABR works in EMC" — that is not establishable from this evidence and the paper must not imply it.
The claim is about **study design**: that this disease isolates the variable the oligometastatic field
cannot otherwise isolate.

## 3 · Why the claim is defensible

The oligometastatic literature's central unresolved problem is **selection**. A patient with few
metastases may do well because local therapy helped, or because their disease was always going to behave
indolently. Every trial in the field carries that confound, and it is the standard objection to every
positive result.

EMC decouples the two, for four reasons that hold simultaneously and hold in no common tumour:

1. **The indolence is a property of the histology, not of the patient's disease burden.** It travels with
   a single defining genetic event — NR4A3 rearrangement — that is diagnostic, testable, and present
   before any treatment decision. In every other disease, indolent behaviour is inferred retrospectively
   from the outcome the trial is trying to measure.
2. **The metastatic compartment is anatomically stereotyped.** 63% of metastatic patients have disease
   *confined to the lungs*, and lung is the first site in 80%; an independent cohort found 27 of 29
   metastatic-at-presentation patients had lung metastases. A single-organ target with a fixed
   distribution is what makes a local-therapy strategy definable at all.
3. **Systemic therapy is weak enough not to confound the readout.** The 171-patient cohort found no
   association between chemotherapy and disease-specific survival, and the best-performing agent in this
   disease is a targeted therapy with a modest response rate. Elsewhere, effective systemic therapy makes
   the local-therapy contribution unidentifiable.
4. **The radioresistance premise that excluded the disease from consideration is itself unsettled** — see
   §4, which is the part of this paper with genuinely new content.

## 4 · The reappraisal that gives the paper a spine

The disease is labelled radioresistant. The evidence for and against that label is recent, serious, and
**entirely about the primary tumour**:

- **Against radiotherapy:** the 2025 cohort (n = 171) finds no association with local recurrence,
  HR 0.50 (95% CI 0.11–2.25), p = 0.365 — but 41.7% of its irradiated patients had R1/R2 margins against
  18.2% of the unirradiated, so the null is confounded toward the null.
- **For radiotherapy:** a 41-patient institutional series in which surgery alone was the only factor
  significantly associated with worse local control; a propensity-weighted SEER analysis of 172 localised
  patients reporting a cancer-specific survival benefit; a **pathological** complete response at 50 Gy;
  and a complete response sustained beyond seven years with protons.

**The observation the paper is built on:** every one of those concerns conventionally fractionated dose to
a primary or a resection bed. None concerns ablative dose to a metastasis. A null result for 50–66 Gy in
2 Gy fractions to a surgical bed is not evidence about 3–5 fraction ablative SABR to a lung nodule — the
biological effect is different in kind, not degree. **The field has been reading one as though it were the
other, and that inference is what has kept an entire modality off the table for this disease.**

That is a real, checkable, previously unstated point. It is the paper's actual contribution.

## 5 · ⛔ What would sink this paper

Written first, because a proposal that lists its objections last has usually not taken them seriously.

1. **⛔ PUBLICATION BIAS IS NEARLY TOTAL, AND IT POINTS THE SAME WAY AS THE THESIS.** Four case reports,
   four successes. Nobody publishes the EMC metastasis that was irradiated and progressed. The paper
   therefore **cannot argue from the outcomes** — the moment it says "radiotherapy controlled these
   lesions", it is quoting a filtered sample and a reviewer will say so correctly. The argument has to
   rest on the **design asymmetry** in §3 and the **inferential error** in §4, using the case reports only
   as existence proofs that the treatment is deliverable. This constraint is severe and it is what makes
   the paper hard to write well.
2. **⛔ THE INDOLENCE ARGUMENT CUTS BOTH WAYS AND THE PAPER MUST SAY SO.** If EMC metastases grow slowly,
   a treated lesion that stays stable for two years may have done so untreated. Three cases in the
   brachytherapy report and three occasions in the SABR report make coincidence less comfortable, but they
   do not exclude it. **A concept paper that uses indolence as the reason the strategy is attractive
   cannot then ignore indolence as the reason the evidence is uninterpretable.** Both must appear, in the
   same section.
3. **⚠ THE SURVIVAL FIGURE THAT DOES NOT FIT.** Median survival after detection of metastases in the
   largest series with the figure is **17.8 months** — which is not an indolent number, and sits badly
   beside the 58% 15-year overall survival used in the same argument. Reconciling these (a 2008 cohort,
   3.6 years median follow-up, likely dominated by patients who presented with burden) is a task the paper
   owes its reader, not a detail to omit.
4. **⚠ THE AUTHORSHIP PROBLEM.** This repository holds no radiation-oncology competence, no clinical
   series, and no patient of its own. A concept paper in this space written without a radiation oncologist
   as an author will read as an outsider's proposal — which is survivable for a hypothesis piece and is
   not survivable if the paper drifts toward implying clinical recommendations.

## 6 · What the paper is, and what it would need

**Format:** a hypothesis / perspective piece, roughly 2,500–3,500 words. Not a systematic review — the
retrievable evidence is four case reports and would not survive the framing.

**Sections:** the natural-history case for anatomical selectivity · the radioresistance reappraisal (§4,
the spine) · what has actually been tried, with its publication bias stated plainly · why this histology
isolates the selection confound · **the study that should be done and the registry that could answer it
without one.**

**What it needs that this repository does not have today:**

| need | cost | who |
|---|---|---|
| Full text of PMID 36944557 | $0 but currently blocked at both sandbox and runner | a library copy, or a co-author with access |
| Dose, fractionation and control duration from PMID 41323055 | $0 | full-text fetch — open access, retrievable |
| Whether any sarcoma-wide SABR series reports an EMC subgroup | $0 | full-text sweep of the series in the findings artifact |
| A radiation oncologist co-author | — | outside this repository |

**What it does NOT need:** a wet lab, a GPU, or any compute. This is the cheapest live paper on the board.

## 7 · How this sits against the existing route board

⚠ **It is not covered by the three routes already in ST-LOCOREGIONAL, and the gap is structural rather
than an oversight.** `RT-LUNG-DIRECTED` covers regional perfusion, inhaled delivery and percutaneous
ablation; `RT-RT-INTENSIFY` covers particle therapy, brachytherapy, radiosensitisation and hyperthermia.
**Ordinary ablative external-beam radiotherapy to a lung metastasis — the actual standard-of-care
oligometastatic intervention, and the one thing that has actually been done to EMC lung metastases — falls
between them and is named by neither.**

⭐ **And one finding retires a blocker on a neighbouring route.** `RT-LUNG-DIRECTED`'s view states that the
lung-confined fraction, "the actual eligibility criterion", is not curated, and that metastatic site
"appears once in free text rather than as data". That is true of the registry and false of the primary
literature: **63% lung-confined** is stated outright in the retrieved full text of one series and
corroborated at 27 of 29 in another. The route's missing numerator cost one fetch.

---

*Every claim above is anchored in [`emc-rt-lung-mets-findings.json`](../literature/emc-rt-lung-mets-findings.json).
Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness, and the case-report
outcomes are not evidence of benefit.*
