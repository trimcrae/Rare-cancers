---
id: DOC-VIEW-RT-RT-INTENSIFY
title: RT-RT-INTENSIFY — Radiotherapy intensification (particle therapy, brachytherapy, radiosensitisation, hyperthermia)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is this disease's contested radiosensitivity a question about dose, or about the quality and delivery of dose?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-RT-INTENSIFY — Radiotherapy intensification (particle therapy, brachytherapy, radiosensitisation, hyperthermia)

**Family:** [ST-LOCOREGIONAL](L1-st-locoregional.md) · **state:** ✓ blocked · computed · confidence low · verified 2026-09-02

**Grade** (owned by [`research/modalities/emc-locoregional-eligibility.json`](../../research/modalities/emc-locoregional-eligibility.json)): ⭐ RE-GRADED 2026-08-26 — THE CONTRADICTION THIS ROUTE IS BUILT ON DOES NOT SURVIVE BEING PUT ON ONE SCALE. Bishop 2019 and Masunaga 2025 were read as disagreeing about whether radiotherapy does anything in EMC. Bishop reports the ADVERSE exposure (surgery alone) at HR 12.7 (1.4-115.3), p = 0.02 for local control; inverted, that is a radiotherapy effect of 0.079 (0.0087-0.71). Masunaga reports the PROTECTIVE exposure at 0.50 (0.11-2.25), p = 0.365. Both protective, intervals overlapping across 0.11-0.71. What separates them is which side of p = 0.05 each landed on, across 5 and 16 local events respectively. ⛔ THAT IS NOT EVIDENCE RADIOTHERAPY WORKS — it is evidence the reachable literature is underpowered and CONSISTENT, and that the route's motivating conflict was an artifact of dichotomising p-values.  ⚠ AND MASUNAGA'S CONFOUNDING RUNS AGAINST RADIOTHERAPY, WHICH MAKES ITS NULL WEAKER STILL: the paper states radiotherapy is given to patients with close margins, and its irradiated arm carried R1/R2 margins at 41.7 % against 18.2 %. Its treated group was at higher baseline risk of the very event measured, so 0.50 understates any protection.  ⭐ THE PARTICLE QUESTION IS ANSWERED AND ITS ANSWER WAS CORRECTED ON 2026-09-01 — CARBON ION HAS BEEN DELIVERED IN THIS HISTOLOGY AND REPORTED. Brachytherapy (Takagawa, HDR interstitial, read directly) and proton beam (Honda, via a review) have each been reported ONCE. Carbon ion is reported too: among the 8 of 171 registry patients who were localized at diagnosis and did not undergo surgery, 2 received carbon ion therapy, 1 proton beam and 1 conventional radiotherapy (Masunaga 2025, PMID 40885991, PMC12398172, quoted verbatim and pinned by blob sha 79a8c197243ff4202a713d437def379c5f499a68 in `research/modalities/emc-radiotherapy-contradiction.json` → `carbon_ion`). ⛔ NO OUTCOME ATTACHES TO ANY OF THEM — the series excludes all eight non-operated patients from its prognostic analysis, so this is an existence proof that an arm was delivered and nothing more. It states and implies nothing about efficacy, safety, tolerability or appropriateness, and it is not a utilisation rate: 2 of 8 and 2 of 171 answer different questions and no rate is derived from either. ⭐ THE ROUTE'S CONCLUSION IS UNCHANGED AND SLIGHTLY STRENGTHENED — arms exist for all three modalities; registries of them do not. How often carbon ion is used in this histology is UNKNOWN: neither corpus has been recounted since the correction and the particle registries themselves are not open.  ⚠ Superseded, retained (rule 1.2): "carbon ion appears nowhere in it across a 354-paper open-access corpus including a 2025 comprehensive EMC review." ⛔ THAT WAS A FALSE ABSENCE, AND ITS OWN CORPUS REFUTES IT. `literature/emc-radiotherapy-2026-08-26/PMC12398172.txt` sits inside the named corpus and carries the sentence; the identical blob also sits at `literature/emc-care-delivery-and-classification/PMC12398172.txt`, so this is one file in two corpora rather than two corpora each missing a paper. The verdict was a term count over ONE document — the 2025 review — scoped to all 354 texts. ⛔ The mechanism mattered more than the value: `found_in_this_histology` was a typed boolean literal and the generator's guard bound to the ANSWER (`is not False`), so it failed the build on the correction rather than on the error. Both were replaced on 2026-09-01 — the value is now derived from pinned corpus quotes and the guard (`emc_radiotherapy_contradiction.py::_check_corpus_derivation`) binds to the evidence, with a ratchet that goes red if a recorded correction loses its quotes.  ⚠ Superseded, retained: "◐ THE PROBLEM IS SIZED AND THE DOSE-RESPONSE IS NOT (2026-08-09). … No dose, modality or margin data is curated anywhere, so the radioresistance reappraisal this route proposes cannot be built from the registry." The endpoint-mixture caution stands. The rest is corrected: dose and modality ARE published — Bishop a median 50 Gy over 50-65 with arms of 23 preoperative / 10 postoperative / 8 surgery alone, Masunaga 40-50 Gy neoadjuvant and 50-66 Gy adjuvant in 2 Gy fractions — and margin data is curated in ART-SURGICAL-QUALITY. The regression is still unbuildable, but because nobody publishes dose PER PATIENT, which is a much narrower gap than 'no dose data anywhere'.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_RT_INTENSIFY["✓ RT-RT-INTENSIFY"]:::fam
  BLK_NO_CURATED_CLINICAL_DATA{{"BLK-NO-CURATED-CLINICAL-DATA — Three of these six clinica…"}}:::blk
  BLK_NO_CURATED_CLINICAL_DATA --> RT_RT_INTENSIFY
  TECH_RECONSTRUCTED_IPD(["TECH-RECONSTRUCTED-IPD<br/>expected 2026H2"]):::tech
  TECH_RECONSTRUCTED_IPD -.-> BLK_NO_CURATED_CLINICAL_DATA
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

## Scientific rationale

This repository's own record contains a live contradiction about whether radiotherapy does anything in this disease — two registries and the largest series disagree. Every prior treatment of that question has been about whether to give radiotherapy. No prior sweep considered that the answer might be dose quality, dose geometry or radiosensitisation, and the one striking combination response in the literature is itself a radiotherapy combination that was previously recorded only as a confound.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-LOCOREGIONAL-ELIGIBILITY` | local recurrence is a substantial minority across four non-overlapping series, but the pooled figure mixes locoregional-specific and unqualified recurrence endpoints and no dose, modality or margin data is curated | `direct` |

## Remaining unknowns

- Whether the recurrence heterogeneity is dose-related at all, which needs PER-PATIENT dose against PER-PATIENT outcome. Both series publish dose at the arm level and neither publishes it per patient, so the dose-response regression remains unbuildable — for a narrower reason than the route previously recorded.
- Whether a properly powered test of radiotherapy in EMC is possible at all from published data. The two reachable estimates carry 5 and 16 local events; a difference the size of either point estimate would need far more events than the whole reachable literature contains.
- ⚠ Superseded TWICE, both retained. (1) "Whether brachytherapy and particle-therapy arms exist in this histology, which has not been searched in the particle registries." SEARCHED AND ANSWERED at $0. (2) The answer that search recorded — "brachytherapy and proton beam each appear once, as case reports; carbon ion appears not at all in this histology across a 354-paper open-access corpus" — ⛔ WAS HALF FALSE AND WAS CORRECTED 2026-09-01. All three arms are reported: brachytherapy and proton beam as single case reports, and carbon ion in 2 of the 8 non-operated localized patients of a 171-patient national-registry series (Masunaga 2025, PMID 40885991), a file that sits inside the very corpus the absence was scoped to. No outcome is printed for any of them. ⛔ What still stands unchanged is the LIMIT on the reading: this is the open-access literature, not the particle registries themselves, which are not open — so how often carbon ion is used in EMC remains UNKNOWN and further use may exist unpublished or paywalled.
- ⚠ Superseded, retained: "How much of the pooled recurrence figure is margin status rather than radioresistance — one series names margins as its main risk factor and this pooling cannot separate them." SEPARATED: Masunaga's local-recurrence model contains both, and margin is significant (4.76, 1.72-13.15) where radiotherapy is not (0.50, 0.11-2.25); stepwise selection retained margin alone.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| The eligibility arithmetic from the curated cohorts | ⛔ none built | yes | — |
| A clinical series in this histology, which only a collaborating centre could assemble | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-CURATED-CLINICAL-DATA** | `insufficient_data` | `TECH-RECONSTRUCTED-IPD` |

## Readiness — what this could become today

**`internal_note`**

The route now holds a real finding — that its own motivating contradiction is a p-value artifact between two underpowered series whose intervals overlap — and that is an internal note's worth. What it cannot become is a reappraisal of radioresistance, because the dose-response regression has no per-patient inputs and the reachable event counts cannot power the comparison anyway. ⚠ Superseded, retained: "The endpoint mixture and the absent dose data mean the reappraisal's regression has no inputs, even though the problem it addresses is now sized." The dose data is not absent; the per-patient dose data is.

**Missing:**
- per-patient dose against per-patient outcome, which no reachable series publishes
- enough local events anywhere in the reachable literature to power the comparison — 5 and 16 in the two series that have made it
- ⚠ Superseded, retained: "per-patient dose and modality data, which none of the curated series publishes" and "a particle-registry search by histology". The first is half wrong — dose and modality are published, just not per patient. The second is done.

## Where this route ends — the paper

**[PUB-LOCOREGIONAL](L3-publications.md)** — *Anatomical selectivity in an indolent, extremity-primary, lung-metastasising sarcoma* (unwritten)

`contributing` · ◔ `outlined` · aimed at `preprint`

**This route contributes:** One of the anatomical-selectivity strategies a disease that is extremity-primary, lung-metastasis-dominant and indolent is unusually well matched to.

**The paper would claim:** A disease that is extremity-primary, lung-metastasis-dominant and slow enough for local control to matter is unusually well matched to locoregional and radiation-based treatment, and a portfolio containing no physical intervention at all had never assessed any of it.

**It is not written because:** ⚠ ITS BLOCKER WAS HALF RIGHT, AND THE HALF IT GOT WRONG IS THE INTERESTING ONE. The arithmetic ran on 2026-08-09 under the repository's binding pooling contract, and it splits cleanly: the SIZE OF THE PROBLEM is computable and now computed — roughly a third of localised patients develop distant disease and a substantial minority recur locally, each pooled over three or four non-overlapping series with its heterogeneity range shown. ⛔ But the ELIGIBILITY criteria are not extractable, because they were never curated: no cohort carries a primary anatomical site field, metastatic site appears once in free text rather than as data, and no cohort records lesion burden or time-to-metastasis. So the paper has its denominator and not its numerator. ⭐ That is still writable and is arguably a better paper: the argument, the sized problem, and an explicit statement of which single curation step would convert it into an eligible fraction — which is $0 for the open-access series. ⛔ Superseded, retained: "the eligibility arithmetic has not been extracted from the curated cohorts yet", which reads as though extraction were the missing step. For two of the three quantities no extraction could have produced them.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The remaining steps are $0 curation and literature search, both self-doable.

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

⛔ ANSWERED — already written. The consistency finding is in `research/manuscripts/care-delivery/emc-radioresistance-reappraisal.md` (live, 2026-08-07) over three series with Cochran's Q, which is strictly more than this row proposes. The genuinely new half — the particle census — was REFUTED on 2026-09-01: `carbon_ion.found_in_this_histology` is now `true`, 2 patients in Masunaga 2025, with no outcome printed for any of the eight non-operated patients. **That refutation is now propagated into this route's `grade.value` and `remaining_unknowns`, which is what this action asked for; nothing further is outstanding on it.** ⚠ Superseded, retained: "⛔ Do NOT re-run the particle search or re-litigate the contradiction … Whether that is worth writing up is a judgement call about what we publish."

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 artifacts:** [ART-RT-CONTRADICTION](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-LOCOREGIONAL](L1-st-locoregional.md) · [← L0](L0-ecosystem.md)
