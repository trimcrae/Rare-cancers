---
id: DOC-VIEW-RT-LUNG-DIRECTED
title: RT-LUNG-DIRECTED — Lung-directed local therapy (regional perfusion, inhaled delivery, ablation)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Does a lung-predominant, indolent metastatic pattern make local therapy of the metastases a better-matched strategy than systemic treatment?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-LUNG-DIRECTED — Lung-directed local therapy (regional perfusion, inhaled delivery, ablation)

**Family:** [ST-LOCOREGIONAL](L1-st-locoregional.md) · **state:** ✓ blocked · computed · confidence low · verified 2026-08-25

**Grade** (owned by [`research/modalities/emc-locoregional-eligibility.json`](../../research/modalities/emc-locoregional-eligibility.json)): ◐ THE POPULATION EXISTS; THE ELIGIBILITY CRITERION IS NOT CURATED (2026-08-09). ⭐ The route's premise half holds and is now sized: across three non-overlapping series, roughly a third of localised patients develop distant disease, so the population a lung-directed strategy exists for is real and is a substantial minority rather than a rarity. ⛔ But the criterion that decides OFFERABILITY is not computable here. Metastatic SITE is recorded in one series' free-text note and nowhere as a field; lesion BURDEN and time-to-metastasis are absent from every cohort. So the fraction meeting any conventional oligometastatic threshold cannot be stated, and the route must stop describing that as an extraction — the data was never curated, not merely un-extracted.  ⚠ 2026-08-25 — A SECOND SERIES WAS CURATED AND IT DOES NOT MAKE THE METASTATIC-SITE DISTRIBUTION POOLABLE. The primary reports were retrieved and their site tables transcribed (`emc-site-curation.json`). Masunaga's metastatic-at-diagnosis stratum reports 27 lung and 2 peritoneal on n=29 — those rows exhaust the cohort, so 27/29 IS a lung-only fraction for that presenting stratum. ⛔ Chiusole's cannot be added: its rows are NON-EXCLUSIVE (23 lung + 4 bone + 14 other = 41 over a denominator of 26), so no lung-CONFINED fraction is readable from it at all, and its own table and running text disagree by one and by two patients. ⇒ The honest state is unchanged in kind — ONE presenting cohort, not a pooled distribution — and the reason has moved from 'nobody curated it' to 'the second series does not report it in a form that can be pooled'. ⛔ Lesion BURDEN remains absent from every reachable series, so no oligometastatic threshold fraction can be stated, and the other nine candidate series are not open access.  ⭐ 2026-08-27 — THE LUNG-CONFINED READING NOW EXISTS IN BOTH PRESENTATION STRATA, AND IT IS AN UPPER BOUND RATHER THAN A MEASUREMENT. bishop2019 was reached at $0 through its PMC full-text record and partitions the 13 patients who developed distant metastases during follow-up as 12 lung and 1 bone — rows that exhaust that cohort. So the quantity is readable for patients who metastasise LATER (12/13) as well as for patients metastatic AT DIAGNOSIS (27/29), which is what a lung-directed strategy needs, because the two groups are offered it at different points. ⛔ THE TWO MAY NOT BE SUMMED — different estimands over different populations — so there is still no pooled distribution. ⛔⛔ AND BOTH ARE UPPER BOUNDS, WHICH CUTS AGAINST THIS ROUTE. drilon2008 is the only reachable series that separates lung-CONFINED from lung-INVOLVED in its own words, and when it does, 63% of metastatic patients are confined to the lungs against 80% with lung as a first site. A two-row partition records which site a patient was filed under, not the absence of another one — so 27/29 and 12/13 bound the lung-confined fraction from above, and the only explicit confined reading in the literature is markedly lower and is percentage-only, entering no pool. ⚠ Stated because it runs against this route's own argument. ⛔ Lesion BURDEN is unchanged: still absent from every reachable series. ⚠ *Superseded, retained: "the other nine candidate series are not open access"* — two of the nine have a PMC full-text record and were read; seven return no PMCID and stay unreachable. ⛔ AND THE 2026-08-25 WORDING IS RETRACTED: ⚠ *Superseded, retained: "those rows exhaust the cohort, so 27/29 IS a lung-only fraction for that presenting stratum"*. The primary text was re-read on 2026-08-27 and says '27 patients HAD LUNG METASTASES, and two had peritoneal dissemination' — an involvement statement. The rows exhausting the cohort shows one category was assigned per patient; it does not show that category means lung-ONLY.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_LUNG_DIRECTED["✓ RT-LUNG-DIRECTED"]:::fam
  BLK_NO_CURATED_CLINICAL_DATA{{"BLK-NO-CURATED-CLINICAL-DATA — Three of these six clinica…"}}:::blk
  BLK_NO_CURATED_CLINICAL_DATA --> RT_LUNG_DIRECTED
  TECH_RECONSTRUCTED_IPD(["TECH-RECONSTRUCTED-IPD<br/>expected 2026H2"]):::tech
  TECH_RECONSTRUCTED_IPD -.-> BLK_NO_CURATED_CLINICAL_DATA
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

## Scientific rationale

The curated record for this disease states both that distant spread is mostly to lung and that removing isolated metastases can give long disease-free intervals — which is already the surgical form of this argument. Regional perfusion, inhaled delivery and percutaneous ablation extend it to patients and lesions surgery cannot reach, and none had ever been considered here.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-LOCOREGIONAL-ELIGIBILITY` | roughly a third of localised EMC patients develop distant disease across three non-overlapping series, while metastatic site, lesion burden and time-to-metastasis are absent from the curated cohorts entirely | `direct` |

## Remaining unknowns

- What fraction of metastatic patients are lung-CONFINED, which is the actual eligibility criterion. ⚠ One series' presenting cohort is strikingly lung-dominant in a free-text note, and one series' presenting cohort is not a pooled distribution.
- What fraction would meet any conventional oligometastatic threshold, which needs lesion counts that none of these series publishes.
- Whether crude during-follow-up proportions understate the lifetime rate in a disease whose metastases appear over many years — they do, and the direction of that bias runs in this route's favour, which is why it is stated rather than omitted.

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

The denominator is now real and the eligibility numerator is not, so the route can size the problem and cannot yet size its own addressable population.

**Missing:**
- metastatic-site and lesion-burden curation from the pooled series' primary reports, which is $0 for the open-access ones and is this route's single highest-value step

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

State the lung-confined fraction as the UPPER BOUND it is — two exclusive partitions over different strata (27/29 and 12/13) bounded above, and one explicit confined reading (63%, percentage-only) below — and write that framing into PUB-LOCOREGIONAL rather than curating further. ⚠ Superseded, retained: "Re-curate metastatic site from the open-access primary reports of the pooled series — the one $0 step that converts this route's denominator into an eligible fraction." — DONE 2026-08-27, and it did NOT convert the denominator into an eligible fraction: it showed the readings available are upper bounds and are not poolable.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 artifacts:** [ART-SITE-CURATION](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-LOCOREGIONAL](L1-st-locoregional.md) · [← L0](L0-ecosystem.md)
