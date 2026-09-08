---
id: DOC-OPUS-CAMPAIGN-CURATION-MORTALITY-ATTRIBUTION
title: "Source curation — underlying-cause attribution, named terminal event, source type and duplicate-source identity"
level: L4
kind: memo
status: live
purpose: >
  Code every retained mortality observation independently into four separately supported fields —
  underlying-cause attribution, named terminal event, source type, and possible overlap or secondary
  reporting — each carried by its own source pointer and quotation, with every unsupported field left
  as an explicit UNKNOWN.
scope: >
  L4. Source-curation evidence over already-retained material. It repairs no manuscript, runs no
  producer, retrieves nothing, adjudicates nothing, and authorises no publication act. It codes only
  the four questions named above; disease membership and death documentation are coded independently
  elsewhere and are not decided here.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Attribution, terminal event, source type and duplicate-source identity

⛔ **The mortality manuscript is parked and stays parked.** This document is curation evidence for
root and the parent. It changes no manuscript, substitutes no tally, and reinstates no claim held
under [`HOLD-mortality-causal-ceiling.md`](HOLD-mortality-causal-ceiling.md).

## What was read, and nothing else

All inputs were already retained. ⛔ No retrieval, no publisher route, no unretained full text and no
producer run.

| input | path | what it supplied |
|---|---|---|
| classified rows | `research/manuscripts/emc-terminal-events-classified.json` (21,732 B, sha256 `94c48d42b65ed031…`) | the 18 retained observation rows, their quotes and their sentence indices |
| retrieval artifact | `research/literature/emc-mortality-probe.json` (597,912 B, sha256 `386cd0c9376229d9…`) | every retained sentence of each cited paper, plus title, journal, year, DOI, PMCID |
| retained abstracts | `research/literature/rt-lung-mets-probe.json` | primary abstracts for 11 of the cited papers, used for source type and overlap only |
| review input package | `mortality-final-ultra-original-inputs.zip` → `review/input-manifest.json`, `review/title-eligible-retained-sentences.json` | the frozen revision `e21841ea…`, and the 34 title-eligible papers with retained death-cue sentences |
| accepted report and adjudication | `review/FINAL-SCIENTIFIC-REVIEW.md`, `root-adjudication.md`, [`HOLD-mortality-causal-ceiling.md`](HOLD-mortality-causal-ceiling.md) | the ten accepted findings, in particular F1 and F6 |

Every quotation below is copied from the retained artifact and is identified by PMID and by the
sentence index the classification names.

## The four fields, as coded here

⚠ These are **my** coding definitions, written before the rows were read and applied to every row.
They are not the package's legacy `label`, and they are not the package's `mechanism_tier`.

1. **Underlying-cause attribution** — what the record *itself* attributes the death to. An
   attribution requires the record to perform one: "died due to X", "died from X", "X resulting in
   death". ⛔ A metastasis, a comorbidity or a disease state merely **mentioned** in a death sentence
   is not an attribution and is coded UNKNOWN.
2. **Named terminal event** — the physiological event the patient died of, and only that. ⛔ A named
   **disease entity** is not a named event: "complications of unresectable colon cancer" names an
   entity whose complications are not themselves named. That distinction is root's accepted finding
   and is applied here without exception.
3. **Source type** — what kind of record the observation sits in: primary case report, primary case
   series, primary institutional or multi-institutional retrospective series, primary comparative
   diagnostic series, cases collected from earlier publications inside a review, or a registry.
4. **Possible overlap or secondary reporting** — whether the observation may be the same patient
   reported elsewhere. Three grades: **SECONDARY** (the record itself states the patient comes from
   an earlier publication), **SUSPECTED PAIR** (named evidence of a possible same-patient overlap
   with another record), **UNKNOWN** (nothing in retained material establishes uniqueness either way).

⛔ **UNKNOWN is not a defect and is not resolved by inference.** A missing event description does not
prove that no underlying cause was assigned, and does not invalidate a disease-specific survival
series. Non-EMC is not non-cancer. The corpus is a selected title-and-death-cue collection: ⛔ nothing
here may be extrapolated to the whole literature, and ⛔ no population-dominant death mechanism is
identified, named or implied.

## Coded records — individual observations

Units are **reported patient instances**, as the retained rows define them. The instance counts below
are recomputed from the rows for internal coherence only; ⛔ they are **not** an accepted
EMC-specific tally, because root's accepted finding **F1** holds that PMID 22569967's two instances
are attributed to the myoepithelial-carcinoma group, and disease membership is coded independently in
another lane and is **not decided here**.

### A · Records whose sentence names a terminal event

**A1 · PMID 35910216** — Front Genet, 2022. Sentences 0–1, n = 1.
> "Here, we present a case which initially demonstrated a typical indolent course of EMC, but rapidly
> progressed after the marginal resection and eventually died of pulmonary failure."

- **Attribution:** EMC progression, stated in the same clause chain ("rapidly progressed … and
  eventually died of"). ⚠ The record uses narrative sequence, not an attribution verb, for the
  underlying cause; the strength of this attribution is weaker than an explicit "due to".
- **Terminal event:** **pulmonary failure** — NAMED. Sentence 1 restates the same patient as dying
  "of respiratory failure".
- **Source type:** primary case report, single index patient with genomic characterisation.
- **Overlap:** internal only — two retained sentences describe one patient and the classification
  collapses them to one instance; I confirm that collapse from the retained sentences. Cross-report
  identity **UNKNOWN**.

**A2 · PMID 41799218** — NMC Case Rep J, 2026. Sentence 0, n = 1.
> "Despite slight neurological recovery, the patient died of respiratory failure on the 15th day
> after onset."

- **Attribution:** **UNKNOWN.** The retained sentence assigns no underlying cause. The title records
  that the ischaemic stroke was due to tumour emboli from cardiac metastasis, but a title establishes
  clinical context, not a cause-of-death attribution, and ⛔ the metastasis present at death does not
  assign it.
- **Terminal event:** **respiratory failure** — NAMED.
- **Source type:** primary case report.
- **Overlap:** index patient, no suspicion. ⚠ Curation note: this paper's sentence 2 — "Table 1 shows
  that 4 of the 11 patients with available postoperative prognoses died in the short term despite
  technically successful endovascular therapy" — reports deaths collected from **other** publications
  in a thrombectomy table. Those four are **not** coded as observations anywhere, which is correct;
  they are recorded here so the exclusion is visible rather than silent.

**A3 · PMID 35775709, third patient of the split row** — Pathologica, 2022. Sentence 0, n = 1 of 3.
> "… and 9.5 years (cerebral hemorrhage but no tumor recurrence) following the primary diagnosis"

- **Attribution:** the named haemorrhage itself, with tumour recurrence **explicitly absent** in the
  record's own parenthesis. This is the one instance in the corpus where a record both names an event
  and negates tumour involvement. ⛔ It remains one reported patient and supports nothing about any
  population.
- **Terminal event:** **cerebral hemorrhage** — NAMED.
- **Source type:** **SECONDARY** — see B3.
- **Overlap:** **SECONDARY**, see pair P2.

### B · Records collecting cases from earlier publications

**B1 · PMID 35665108, first row** — World J Clin Cases, 2022. Sentence 1, n = 1.
> "Only 1 out of the 11 patients who underwent PR died from local recurrence and spinal metastasis of
> primary intracranial EMC at 36 mo after surgery[ 9 ]."

- **Attribution:** EMC — local recurrence and spinal metastasis, attributed by the record ("died
  from").
- **Terminal event:** **UNKNOWN** — no physiological event named.
- **Source type:** **cases collected from the literature inside a case report + review**. The
  sentence cites reference **[9]**; that primary is **not retained** and is not identified anywhere
  in retained material.
- **Overlap:** **SECONDARY by construction.** The patient is someone else's published case. ⭐ One
  candidate can be excluded on retained evidence: PMID 23115670's own index patient had **total**
  surgical resection and was improving at six months, whereas this patient underwent **partial**
  resection and died at 36 months — not the same patient. Which primary it is remains UNKNOWN.

**B2 · PMID 35665108, second row** — sentence 0, n = 2.
> "In our research of the 16 primary intracranial EMC cases available in the literature, 3 did not
> have any information on the prognosis of patients, and in 2 cases, the patients died from
> non-EMC-related factors after surgery."

- **Attribution:** **UNKNOWN.** The record asserts only what the deaths were **not** related to. ⛔
  An exclusion names no cause, and ⛔ non-EMC is not non-cancer: these two deaths may have been from
  another malignancy, from treatment, or from an unrelated illness, and the record does not say.
- **Terminal event:** **UNKNOWN.**
- **Source type:** cases collected from the literature inside a case report + review; the reviewers'
  own patient was alive and recurrence-free at 12 months per the retained abstract, so these two are
  not the paper's own patients.
- **Overlap:** **SECONDARY**, and a **SUSPECTED PAIR** with B4 — see P1.

**B3 · PMID 35775709, first and second patients of the split row** — Pathologica, 2022. Sentence 0,
n = 2 of 3.
> "Three patients died 9 months (the patient with lung and skin metastasis later developed congestive
> heart disease), 10 months (the patient with hepatic metastasis), and 9.5 years (cerebral hemorrhage
> but no tumor recurrence) following the primary diagnosis ( Tab."

- **Attribution, patient at 9 months:** **UNKNOWN.** Lung and skin metastases and a later congestive
  heart disease are both **mentioned**; neither is attributed. ⛔ The metastases do not assign the
  cause and the cardiac condition is not stated as the cause.
- **Attribution, patient at 10 months:** **UNKNOWN.** ⛔ Hepatic metastasis stated at death does not
  assign the cause — this restates root's accepted F6 on the same instance.
- **Terminal event, both:** **UNKNOWN.** "Congestive heart disease" is a disease entity in a
  parenthesis, not a stated terminal event.
- **Source type:** **cases collected from the literature.** ⭐ Evidence, from the retained abstract of
  this very paper: its own index patient — a 45-year-old woman with primary breast EMC — "was in
  clinical and radiologic remission at the last follow-up (18 months post surgery)". The three deaths
  therefore come from the paper's literature table ("Tab."), not from its own case.
- **Overlap:** **SECONDARY** for all three patients of this row; see P2.

**B4 · PMID 23115670** — J Korean Neurosurg Soc, 2012. Sentence 0, n = 2.
> "Of the remaining five patients, two showed tumor recurrences and two died due to postoperative
> complications 2 , 14 , 15 , 17) ."

- **Attribution:** **postoperative complications** — treatment-related, attributed by the record
  ("died due to").
- **Terminal event:** **UNKNOWN** — the complications themselves are not named.
- **Source type:** cases collected from the literature inside a case report + review; the citation
  markers 2, 14, 15, 17 point at primaries that are **not retained**. The retained abstract records
  that only seven intracranial cases had been reported previously and that the paper's own patient
  survived surgery and radiotherapy.
- **Overlap:** **SECONDARY**, and a **SUSPECTED PAIR** with B2 — see P1.

### C · Primary records with an attribution but no named event

**C1 · PMID 29977924** — Biomed Res Int, 2018. Sentence 0, n = 1.
> "One patient died due to lung metastases."

- **Attribution:** **lung metastases**, attributed by the record's own "due to". ⚠ This is the
  boundary case for the metastasis rule: the rule forbids *me* from assigning a cause from a
  mentioned metastasis; it does not forbid recording that the **record** made that assignment. What
  the record assigns is a metastatic site, which is a cause class, not a mechanism.
- **Terminal event:** **UNKNOWN.**
- **Source type:** primary retrospective single-institution imaging-and-pathology series, 13 cases.
- **Overlap:** **UNKNOWN.** The retained abstract gives neither institution nor accrual dates, so no
  comparison with any other series in the corpus can be made from retained material.

**C2 · PMID 28638563** — J Clin Exp Dent, 2017. Sentences 0, 1, 2, 5, n = 1.
> "The patient received adjuvant radiotherapy but died after 1 year of follow-up due to complications
> of locoregional tumor dissemination to the skull base."

- **Attribution:** EMC — locoregional dissemination to the skull base, attributed by the record.
  Sentence 2 states independently that the local dissemination caused the death.
- **Terminal event:** **UNKNOWN.** ⚠ This is the same shape as the colon-cancer instance: the record
  names **complications of** a disease process and does not name the complications. It attributes a
  cause; it does not name an event.
- **Source type:** primary case report, paediatric masticator-space EMC.
- **Overlap:** four retained sentences, one patient, collapsed by the classification; I confirm the
  collapse. Cross-report identity **UNKNOWN**.

**C3 · PMID 36097623** — JAAD Case Rep, 2022. Sentence 0, n = 1.
> "The patient subsequently underwent radiation to the brain and failed systemic treatment with
> chemotherapy and immunotherapy, with the development of further metastases ultimately resulting in
> death."

- **Attribution:** EMC progression — "further metastases ultimately resulting in death" is the
  record's own causal construction.
- **Terminal event:** **UNKNOWN.**
- **Source type:** primary case report.
- **Overlap:** **UNKNOWN.**

**C4 · PMID 32963861** — Case Rep Orthop, 2020. Sentences 1–2, n = 1.
> "The patient was followed for 126 months, after which he died from complications of unresectable
> colon cancer."

- **Attribution:** **colon cancer**, a different disease from the one the paper follows, attributed
  by the record ("died from").
- **Terminal event:** **UNKNOWN** — a **named disease entity**, with its complications unnamed. This
  is the instance root's semantic correction was written for, and it is coded here the same way
  independently.
- **Source type:** primary report of **three** cases with pulmonary metastases managed by
  observation, per the retained abstract; one of the three is the coded death.
- **Overlap:** **UNKNOWN**, no suspicion.

**C5 · PMID 35251555, first row** — Rare Tumors, 2022. Sentences 3 and 7, n = 2.
> "Two patients with EMC died during follow-up from concurrent malignancies ( Table 2 )."

- **Attribution:** **concurrent malignancies** — attributed by the record to other cancers, which are
  **not named**. ⛔ These are not non-cancer deaths and must never be counted as such.
- **Terminal event:** **UNKNOWN.**
- **Source type:** primary single-institution retrospective case series, 15 patients, 1992–2019;
  these are the institution's own patients, recorded in its Table 2.
- **Overlap:** internal only — sentence 7 restates the same two patients ("two others died from
  concurrent malignancies within the first few months after diagnosis") and the classification counts
  them once; I confirm that from the retained sentences. Cross-report identity **UNKNOWN**.

**C6 · PMID 36326382** — Turk J Med Sci, 2022. Sentences 0 and 2, n = 7.
> "While recurrence developed in 5 (38.5%) of the patients during follow-up, lung metastasis (46.2%)
> was detected in 6 patients, and 7 patients (53.8%) died due to the disease and complications
> related to the disease."

- **Attribution:** the disease and its complications, attributed collectively at group level. ⛔ No
  per-patient attribution exists; this cannot be distributed across the seven.
- **Terminal event:** **UNKNOWN** — "complications related to the disease" names none.
- **Source type:** primary single-institution retrospective surgical series, 13 patients, 2006–2018,
  oncology reference centre.
- **Overlap:** internal only — sentence 0 states the same seven deaths without the attribution, and
  the classification counts them once. ⚠ Curation note: sentence 5 of this paper reports "only 4 out
  of 34 patients were reported to have died of the disease" in Enzinger and Shiraki's historical
  series. Those four are deaths from **another** publication and are **not** coded anywhere, which is
  correct; recorded here so the exclusion is visible.

**C7 · PMID 22569967** — Virchows Arch, 2012. Sentences 0–1, n = 2.
> "Two patients died of disease 8 months after the initial diagnosis."

- **Attribution:** "of disease" — the record attributes the deaths to the malignancy under follow-up
  and names no mechanism.
- **Terminal event:** **UNKNOWN.**
- **Source type:** primary **comparative diagnostic series** contrasting two entities — ten
  myoepithelial carcinomas against five cellular EMCs. ⚠ Its retained abstract places this sentence
  inside the description of the myoepithelial-carcinoma group ("Five patients were alive without
  evidence of disease, two were alive with disease and two died 8 months after the initial
  diagnosis"), immediately before the cEMC group is introduced. Which disease these two deaths belong
  to is **root's accepted finding F1** and is coded independently in another lane; ⛔ it is not
  decided here. What this lane records is that the **source type is a two-entity comparison**, which
  is exactly the source shape in which such an attribution error is possible.
- **Overlap:** **UNKNOWN.**

### D · Primary records with neither attribution nor event

**D1 · PMID 35251555, second row** — sentence 4, n = 2.
> "Both patients that presented with metastatic disease to the lungs died within 17 months ( Table 2 )."

- **Attribution:** **UNKNOWN.** Lung-metastatic **at presentation** is a baseline state, not a cause
  assignment. ⛔ Reading these as respiratory deaths would be exactly the inference the rules forbid.
- **Terminal event:** **UNKNOWN.**
- **Source type:** same primary single-institution series as C5.
- **Overlap:** ⭐ within-paper overlap with C5 is **improbable on the record's own arithmetic**: the
  retained abstract states fifteen patients were evaluated and "At last follow-up, 11 patients were
  alive", leaving four deaths, which is exactly C5's two plus this row's two. That is consistent with
  four distinct patients; it is not proof, since neither row identifies its patients. Cross-report
  identity **UNKNOWN**.

**D2 · PMID 25177237** — Radiol Oncol, 2014. Sentences 0, 2, 4–8, n = 3.
> "Three patients died during the time-frame of the study, 1 was lost to follow up, and 9 are still
> alive."

- **Attribution:** **UNKNOWN** in every one of the seven retained sentences. Two individual deaths are
  described by timing only ("died within 18 months of diagnosis"; "died 81 months after diagnosis").
- **Terminal event:** **UNKNOWN.**
- **Source type:** primary single-institution IRB-approved retrospective imaging series, 13 patients,
  August 1995 – December 2011.
- **Overlap:** internal only — seven retained sentences, three deaths, collapsed by the classification
  and concordant here with the abstract's "Among 13 patients, 3 died". Cross-report **UNKNOWN**.

**D3 · PMID 32612944** — Front Oncol, 2020. Sentence 1, n = 20.
> "With a median follow-up time of 72 months, 20 patients have died."

- **Attribution:** **UNKNOWN** — all-cause, and the paper does not split them. This is the largest
  single block of instances in the corpus and it carries no cause information at all.
- **Terminal event:** **UNKNOWN.**
- **Source type:** primary **two-institution** retrospective series — Istituto Oncologico Veneto and
  Institut Gustave Roussy — 59 patients diagnosed January 1980 – December 2018, from a prospectively
  maintained database.
- **Overlap:** **SUSPECTED secondary reporting downstream** — see P3. Patient-level uniqueness against
  other European series is **UNKNOWN**.

### E · Rows documenting no death

Both are retained for the harm or the care transition they document. ⛔ Neither documents survival
either, and nothing here asserts that these patients lived.

**E1 · PMID 23213584** — Case Rep Oncol Med, 2012, sentence 0, n = 1. "Due to persistent anemia and
gastrointestinal bleeding, the patient case was presented to the multidisciplinary tumor board, and
it was recommended to proceed with palliative small bowel tumor resection." Attribution **NOT
APPLICABLE — no death documented**; terminal event **NOT APPLICABLE**; source type primary case
report; overlap **UNKNOWN**, no suspicion.

**E2 · PMID 21941486** — Case Rep Oncol, 2011, sentence 1, n = 1. "The patient consequently
deteriorated clinically and was referred for palliative radiation and transitioned to supportive
care." Attribution **NOT APPLICABLE — no death documented**; terminal event **NOT APPLICABLE**;
source type primary case report; overlap **UNKNOWN**, no suspicion.

### F · Registry aggregate rows

**F1–F3 · PMID 40885991** — J Orthop Surg Res, 2025. Three strata of the Japanese National Bone and
Soft Tissue Tumor Registry Database, 171 patients pathologically diagnosed 2002–2022.

> "Of the 128 patients who did not receive (neo)adjuvant chemotherapy, 88 (68.8%) were tumor-free
> survivors, 28 (21.9%) survived with tumors, eight (6.3%) died from tumors, and four (3.1%) died from
> other causes."

- **Attribution:** a **two-class registry split** — "died from tumors" against "died from other
  causes". The tumour class is attributed by the registry; ⛔ the other-cause class names nothing, and
  "other causes" is not a non-cancer statement.
- **Terminal event:** **UNKNOWN** for every patient in all three strata; a registry cause field is not
  an event description.
- **Source type:** **national registry**, aggregate — the only registry source in this corpus and the
  only one with an explicit cause split.
- **Overlap:** ⛔ **known internal overlap.** The classification records that these strata overlap the
  localised stratum already used by `emc-mortality-decomposition-inputs.json` and excludes them from
  every pooled total; that exclusion is correct and is not disturbed here. Whether individual registry
  patients also appear in Japanese single-institution reports or case reports is **UNKNOWN** — a
  registry cannot be de-duplicated against the case literature from aggregate counts.

## Summary of the four codings

Recomputed from the rows above for internal coherence. ⛔ Not an accepted EMC-specific tally
(root F1); ⛔ not extrapolable to the literature (root F6).

**Underlying-cause attribution**, over the 50 documented-death instances:

| coded attribution | instances | records |
|---|---|---|
| EMC, its progression, recurrence or local extension | 11 | 28638563 (1), 36097623 (1), 36326382 (7), 35665108 B1 (1), 35910216 (1, narrative form) |
| a metastatic site, assigned by the record itself | 1 | 29977924 |
| a different, **named** disease | 1 | 32963861 (colon cancer) |
| other malignancy, **unnamed** | 2 | 35251555 C5 |
| treatment — postoperative complications | 2 | 23115670 |
| a non-EMC event with tumour recurrence explicitly absent | 1 | 35775709, 9.5-year patient |
| "of disease", no mechanism, two-entity source | 2 | 22569967 |
| **exclusion only — "non-EMC-related", no cause named** | 2 | 35665108 B2 |
| **UNKNOWN — the record assigns nothing** | 28 | 41799218 (1), 35251555 D1 (2), 35775709 (2), 25177237 (3), 32612944 (20) |

**Named terminal event:** **3** instances name one — pulmonary failure (35910216), respiratory
failure (41799218), cerebral hemorrhage (35775709). **1** instance names a **disease entity** and no
event (32963861). The remaining **46** are **UNKNOWN** at instance level. ⚠ Corrected 2026-09-08: **at record level the UNKNOWN total is 47**, because C4 codes 32963861's terminal event as UNKNOWN while this summary breaks it out as a named disease entity. The two counts are of different things and 50 closes under either; quoting them side by side without this sentence would look like an arithmetic error. ⚠ Two further instances name *complications
of* something — locoregional dissemination (28638563) and surgery (23115670) — and are coded UNKNOWN
for the event, because a complication that is not itself named is not an event.

**Source type**, over the 14 records carrying documented deaths:

| source type | records | instances |
|---|---|---|
| primary case report, single index patient | 35910216, 41799218, 28638563, 36097623 | 4 |
| primary small case series | 32963861 | 1 |
| primary single-institution retrospective series | 29977924, 25177237, 36326382, 35251555 | 15 |
| primary multi-institution retrospective series | 32612944 | 20 |
| primary comparative diagnostic series, two entities | 22569967 | 2 |
| **cases collected from earlier publications** | 35665108, 23115670, 35775709 | 8 |

Plus one **national registry** (40885991), whose strata sit outside the 50 and outside every pooled
total, and two primary case reports documenting no death (23213584, 21941486).

**Possible overlap or secondary reporting:** **8 of the 50** instances — every death instance
carried by 35665108, 23115670 and 35775709 — are **SECONDARY by the records' own words**: they are
patients from earlier publications, re-reported. Of those, 35775709's three are secondary on the
strength of its own abstract. For the remaining 42, uniqueness is **UNKNOWN**: nothing in retained
material establishes that any two primary series do not share a patient.

## Every UNKNOWN, and why retained material cannot resolve it

| # | UNKNOWN | why it cannot be resolved here |
|---|---|---|
| U1 | Underlying cause for 28 of 50 instances | The retained sentences assign none. Resolving them would require the papers' full text or their cause-of-death tables, which are not retained, and ⛔ inference from a mentioned metastasis is forbidden. |
| U2 | Terminal event for 46 of 50 instances | No physiological event appears in the retained sentence. ⛔ A missing event description does **not** prove no underlying cause was assigned elsewhere in the paper, and does not invalidate the source. |
| U3 | What "non-EMC-related factors" means (35665108, 2 instances) | The record states only an exclusion. Non-EMC is not non-cancer; the deaths could be another malignancy, treatment or unrelated illness. Only the primaries behind the review's 16 collected cases could say, and they are unretained. |
| U4 | Which patients the three 35775709 deaths are | The row is a literature table entry with no PMIDs, names or institutions in the retained sentence. |
| U5 | Which publication reference "[9]" of 35665108 is | Reference lists are not part of the retained artifact. |
| U6 | Which publications references "2, 14, 15, 17" of 23115670 are | Same reason. |
| U7 | Whether the two intracranial reviews' post-surgical deaths are the same patients (P1) | Both are literature collections in the same tiny published population, and neither retained sentence identifies a patient. |
| U8 | Patient-level uniqueness across the four primary institutional series and the two-institution series | No institution-plus-date-plus-patient identifiers are retained for 29977924; the others' accrual windows overlap in time but overlapping windows are not shared patients. |
| U9 | Whether registry patients (40885991) also appear in the case literature | Aggregate registry counts cannot be de-duplicated against individual reports. |
| U10 | Disease membership for 22569967's two instances | ⛔ Deliberately not coded in this lane. Root's F1 stands on its own record; membership is coded independently elsewhere. |
| U11 | Whether the 9-month 35775709 patient died of the cardiac condition or the metastases | The record juxtaposes both and attributes neither. |
| U12 | Cause split behind 32612944's 20 instances | The paper reports all-cause deaths only. This single record is 40% of the corpus's instances and carries no cause information. |
| U13 | Whether any coded death also appears inside a review not counted here | The corpus's reviews were read for the sentences they carry, not indexed by the patients they collect. |

## Suspected duplicate-source pairs, with their evidence

**P1 · PMID 23115670 (2012) ↔ PMID 35665108 (2022) — SUSPECTED, unresolved.**
Both are case reports of primary intracranial EMC that append a review of the previously published
cases of the same very rare presentation. The 2012 paper's abstract states intracranial EMC is
"extremely rare, with only seven patients previously reported"; the 2022 paper's row draws on "the 16
primary intracranial EMC cases available in the literature". A 2022 collection of 16 published
intracranial cases plausibly contains the cases the 2012 paper reviewed. Both rows report deaths
**after surgery**: two "due to postoperative complications" (2012) and two "from non-EMC-related
factors after surgery" (2022). ⚠ If these are the same two patients, four coded instances are two
patients, and one pair is attributed to treatment while the other is attributed to nothing at all —
the same deaths would then carry contradictory attributions in the coded set. ⛔ Retained material
cannot decide it: neither sentence names a patient, and the reference lists are not retained.

**P2 · PMID 35775709's three deaths ↔ unidentified earlier publications — SECONDARY, unresolved.**
Evidence that they are secondary is the paper's own abstract: its index patient was in remission at 18
months. The three deaths therefore come from its literature table. ⭐ A check of the retained sentences
of every other paper in the corpus finds no other record of a death at 9.5 years with cerebral
haemorrhage and no tumour recurrence, of a death at 10 months with hepatic metastasis, or of a death
at 9 months with lung and skin metastases plus congestive heart disease — so their primaries appear to
lie **outside** the retained corpus, and no double-count within the corpus is evidenced. That is an
absence of evidence for overlap, not evidence of independence.

**P3 · PMID 32612944 (2020) ↔ PMID 41055792 (2025) — CONFIRMED secondary reporting, correctly not
double-counted.** The 2025 comprehensive review is title-eligible and its retained sentences include:
"In the retrospective series by Chiusole et al. ( 2020 ) patients with metastatic EMC who received
palliative chemotherapy had a shorter median OS (72 months) than those who did not receive
chemotherapy (81 months)." That restates the two-institution cohort coded at D3. The review carries no
coded death instance, so nothing is double-counted — but it demonstrates that this corpus contains
secondary reporting chains, and that a mechanical count over retained sentences could have created one.

**P4 · PMID 35665108's partial-resection death ↔ PMID 23115670's index patient — EXCLUDED on
evidence.** The 2012 index patient underwent **total** surgical resection with no residual tumour on
postoperative MRI and was improving six months later; the 2022 row's patient underwent **partial**
resection and died at 36 months. Not the same patient. ⭐ Recorded because an excluded candidate is
as much a curation result as a suspected one.

**P5 · Within-record duplicate sentences — five, all already collapsed and independently re-read here.**
35910216 (sentences 0 and 1, one patient), 35251555 (sentences 3 and 7, two patients), 25177237 (seven
sentences, three patients, cross-checked against "Among 13 patients, 3 died"), 36326382 (sentences 0
and 2, seven patients), 41799218 (its own patient in sentence 0, distinct from the table deaths in
sentence 2). The classification collapses each correctly; sentence-level counting would have inflated
the corpus roughly threefold in these records alone.

## Coverage check on the retained title-eligible set

The review package's `title-eligible-retained-sentences.json` holds **34** papers whose title names the
disease and which carry a retained death-cue sentence. **17** carry the coded observations above
(of the five non-death examples the classification records, **only 40885991** is among these 17; the other four sit in the "other 17" listed below — corrected 2026-09-08, the earlier parenthetical placed all five here). I read the retained
sentences of the other **17** and found **no** uncoded patient death: they are background statements
about prognosis ("a high rate of death has been described to occur eventually due to these tumors" —
21938148), endpoint and methods definitions (24345066, 27418251), palliative-radiotherapy discussion
(35494187, 30534357, 26448808, 41323055, 41321774), other diseases' cohorts cited in discussion
(26125202), cell-line and molecular papers (36316541, 32967265, 31020999, 29937513, 27832806), and
review prose (41055792, 24944710, 22925697). ⭐ This independent re-read is concordant with the
classification's inclusion decisions: no death observation was dropped from the title-eligible set. ⛔
It says nothing about the 128 death-cue papers outside the title-eligible restriction, and nothing
about the literature beyond the probe.

## What this supports, and what it does not

**Supported, over the retained material only:**

- Each of the four questions is now coded **separately**, with its own quotation and pointer, so that
  an attribution is never read as an event and a source type is never read as independence.
- The corpus names a terminal event in **3** instances and a disease entity in **1**; everything else
  is silent on the event. Root's event-versus-entity distinction survives independent re-coding.
- **8** instances are, by the records' own words, patients from earlier publications; **42** have
  **UNKNOWN** uniqueness. ⛔ The summed instances are therefore **not** established as distinct people.
- The corpus's largest single block — 20 instances, 40% of the total — carries no cause information of
  any kind.
- Two suspected same-patient overlaps are named with their evidence, one candidate overlap is excluded
  on evidence, and one secondary reporting chain is documented.

**Does not establish:**

- ⛔ Nothing about the whole EMC literature. The corpus is selected by title and by death cue, and
  cannot support a statement about mechanism reporting in general.
- ⛔ No population-dominant mode of death, no cause fraction, no rate, no incidence and no denominator.
- ⛔ No validated EMC-specific tally: disease membership for 22569967 is root's accepted F1 and is
  coded in a separate lane, and the counts here are internal coherence only.
- ⛔ No conclusion that the silent records assigned no cause. A retained sentence that names no cause
  is a fact about the retained sentence.
- ⛔ Nothing about EMC efficacy, safety, selectivity or clinical readiness, and no claim that any
  treatment works or that any survival series is invalid.
- ⛔ No repair, no reinstatement and no publication act. The manuscript remains parked.
