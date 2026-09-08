---
id: DOC-OPUS-CAMPAIGN-CURATION-MORTALITY-MEMBERSHIP
title: "Source curation — disease membership and death documentation, row by row"
level: L4
kind: memo
status: live
purpose: >
  Audit every currently contributing classified terminal-event row against the retained study-group
  and case context, and record, per row, what the retained sources actually support about disease
  membership and documented death.
scope: >
  L4. Source-curation evidence only. It repairs no manuscript, produces no headline tally, reinstates
  no claim, retrieves no new source, and runs no producer.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Source curation — disease membership and death documentation

⛔ **The mortality manuscript stays parked.** `research/manuscripts/emc-mortality-mechanisms-paper.md`
is frozen at `e21841ea103560d801f4e21f64ee31a68028e232` under the accepted adverse review recorded in
[`HOLD-mortality-causal-ceiling.md`](HOLD-mortality-causal-ceiling.md). Nothing here reopens it,
edits it, or supplies a replacement number for it. This document is curation evidence about sources.

⛔ **No causal ceiling, no cause fraction, no patient-capacity figure and no treatment-efficacy
statement is made, implied, or restored anywhere below.**

⛔ **This document produces no headline tally.** The review's illustrative 48 / 13 / 25 is explicitly
**not** an accepted replacement and is **not** used here. Where the rows below imply an arithmetic,
it is stated as what the sources support **with its unknowns named**, never as a corrected headline.

## What was audited, and against what

**Unit of audit:** the 18 rows in `individual_events` of
`research/manuscripts/emc-terminal-events-classified.json` — the currently contributing classified
rows. **All 18 are preserved below with their original dispositions.** No row is dropped, merged, or
renumbered; row numbers are the artifact's own array indices.

**Retained material used, and nothing else:**

| purpose | retained input |
|---|---|
| the classified rows | `research/manuscripts/emc-terminal-events-classified.json` → `individual_events[0..17]` |
| the quoted sentences and their in-paper neighbours | `research/literature/emc-mortality-probe.json` → `terminal_events[i].sentences[j]` |
| retained primary abstracts | `research/literature/rt-lung-mets-probe.json` → `queries.<query>.top[k].abstract` |
| the accepted review and its findings | `…/collected/mortality-final-ultra-original-inputs.zip` → `review/FINAL-SCIENTIFIC-REVIEW.md`, `root-adjudication.md` |
| intake and hold context | [`RECEIPT-mortality-final-review-originals-intake.md`](RECEIPT-mortality-final-review-originals-intake.md), [`HOLD-mortality-death-counts.md`](HOLD-mortality-death-counts.md), [`HOLD-mortality-causal-ceiling.md`](HOLD-mortality-causal-ceiling.md) |

⛔ **No new retrieval was performed.** No publisher route, no full text, no producer run. Where the
retained material does not settle a field, the field is **UNKNOWN** and says so.

## The three distinctions this audit applies

1. **Group membership beats the title.** A publication whose title names EMC may report its deaths in
   a different disease group (PMID 22569967) or in a literature-review set rather than in its own
   index patient (PMIDs 23115670, 35665108, 35775709). Membership is read from the group the retained
   context places the deaths in, never from the title.
2. **A documented death is not a clinical complication.** Two rows record a complication or a
   transition of care and **document no death**. ⛔ Neither asserts that the patient survived either.
3. **Unknown membership or unknown death status cannot enter a validated EMC denominator.** Such rows
   are marked UNKNOWN here and are not resolved by inference.

## Row-by-row disposition (all 18 rows, artifact order)

| # | PMID | source group the deaths sit in | supported diagnosis | documented death | denominator scope | disposition |
|---|---|---|---|---|---|---|
| 0 | 35910216 | index case, n=1 | **EMC** — the quoted sentence itself says "typical indolent course of EMC" | yes, n=1 | single case report | EMC membership supported by the quote; retain |
| 1 | 29977924 | one patient inside a 13-case EMC imaging/pathology series | **EMC** — abstract: 13 EMC cases confirmed by surgery biopsy, no second disease group | yes, n=1 | 1 of 13; the series' total death count is **UNKNOWN** from retained material | retain; cause is a broad category, not a named terminal event |
| 2 | 41799218 | index case, n=1 | **EMC** — title names EMC with cardiac metastasis | yes, n=1 | single case report | retain; ⚠ the same paper's Table 1 (4 of 11 thrombectomy patients died) is a **different, non-EMC group** and is correctly not counted |
| 3 | 28638563 | index case, n=1 | **EMC** — title: EMC of the masticator space | yes, n=1 | single case report | retain |
| 4 | 35665108 | **not the index patient** — one patient inside the 16 primary-intracranial-EMC cases collected from the literature, cited to ref [9] | **EMC** (primary intracranial) — named in the quoted sentence | yes, n=1 | 11-patient partial-resection subgroup of a 16-case literature set; **secondary report** | retain, but as a previously published case, **overlap UNKNOWN** (see row 8) |
| 5 | 35665108 | same 16-case literature set, 2 patients | **EMC** (primary intracranial) — the 2 are among the 16 EMC cases | yes, n=2 | same 16-case literature set, of which 3 have no prognosis information at all | retain as documented deaths; ⛔ **cause UNKNOWN** — "non-EMC-related factors" names no cause and does not establish a non-cancer death |
| 6 | 36097623 | index case, n=1 | **EMC** — title: metastatic EMC | yes, n=1 | single case report | retain; ⚠ the retained record's abstract field is **null** — membership rests on title plus the single retained sentence |
| 7 | 23213584 | index case, n=1 | **EMC** — title: EMC with small-bowel metastasis | ⛔ **NO** — a complication (anaemia, GI bleeding) and its management | excluded from every death numerator **and** denominator | preserved as a documented harm, **not a death**; ⛔ it does not document survival either |
| 8 | 23115670 | **not the index patient** — "the remaining five" previously reported intracranial EMC patients, cited to refs 2, 14, 15, 17 | **EMC** (intracranial) at the level of the review's subject; ⚠ the identity of the five is **UNKNOWN** | yes, n=2 | previously published cases; abstract states only seven prior patients existed; **secondary report** | retain as documented deaths; ⛔ **overlap with row 4/5's 16-case set UNKNOWN and plausibly substantial** |
| 9 | 32963861 | one of three index EMC patients | **EMC** — abstract: three EMC cases with pulmonary metastases | yes, n=1 | 1 of 3 cases in the report | retain; names a **disease entity** (colon cancer), not the terminal event |
| 10 | 35251555 | institutional 15-patient EMC series | **EMC** — the sentence says "Two patients with EMC" | yes, n=2 | 2 of 15 | retain; cause is a broad category ("concurrent malignancies") |
| 11 | 35251555 | same 15-patient EMC series | **EMC** | yes, n=2 | 2 of 15 | retain; no mechanism stated. ⚠ distinctness from row 10 is **consistent with** the abstract's "11 patients were alive at last follow-up" (15 − 11 = 4 = 2 + 2) but is **not stated** in either quote |
| 12 | 35775709 | **not the index patient** (index alive, in remission at 18 months) — three patients in the paper's literature-review table | ⛔ **UNRESOLVED** — the quoted sentence names no diagnosis and the referenced table is not retained; the publication's scope is primary EMC of the breast | yes, n=3 | previously published cases in a review table whose population is **not retained** | ⛔ **membership UNKNOWN → cannot enter a validated EMC denominator.** Sub-splits retained unchanged: 1 ambiguous (congestive heart disease with lung/skin metastases), 1 hepatic metastasis (**states metastasis at death, assigns no cause**), 1 cerebral haemorrhage at 9.5 years explicitly without tumour recurrence (a named terminal event) |
| 13 | 22569967 | ⛔ **the myoepithelial-carcinoma (MEC) group** — 9 of 10 MEC patients had follow-up: 5 alive NED, 2 alive with disease, **2 died**. The **cellular-EMC group's** 4 followed patients were **all alive** | ⛔ **myoepithelial carcinoma of soft tissue — NOT EMC** | yes, n=2 — **but in the wrong disease** | ⛔ **must be excluded from any EMC-specific denominator** | ⛔ **THE DEFECT CLASS (accepted finding F1).** The paper's own retained sentence for the cEMC group is "No patient died of the disease so far." The extracted death sentence had lost its disease-group attribution |
| 14 | 25177237 | 13-patient EMC imaging series | **EMC** — abstract: 13 patients with pathologically proven EMC | yes, n=3 | 3 of 13 (1 lost to follow-up, 9 alive) | retain; no mechanism stated |
| 15 | 36326382 | 13-patient surgical EMC series | **EMC** — abstract: 13 patients diagnosed with EMC | yes, n=7 | 7 of 13 | retain; collective attribution "due to the disease and complications related to the disease", **no per-patient mechanism**. ⚠ the same paper's Enzinger–Shiraki 34-patient historical group is a **different group** and is correctly not counted |
| 16 | 32612944 | two-institution 59-patient EMC cohort | **EMC** — abstract: 59 patients with confirmed EMC | yes, n=20 | 20 of 59, median follow-up 72 months | retain; **all-cause**, the paper splits no causes at all |
| 17 | 21941486 | index case, n=1 | **EMC** — title and abstract: a case of highly aggressive EMC | ⛔ **NO** — clinical deterioration and a transition to supportive care | excluded from the death tally | ⛔ **death status UNKNOWN from the retained sentence** — it proves neither death nor survival |

## Per-row source binding

Each entry gives the quotation the row is judged on and the exact pointer to it. Classified-row
pointers are `research/manuscripts/emc-terminal-events-classified.json → individual_events[#]`.
Sentence pointers are `research/literature/emc-mortality-probe.json → terminal_events[i].sentences[j]`
(`i` is the array index for that PMID). Abstract pointers are
`research/literature/rt-lung-mets-probe.json → queries.<query>.top[k].abstract`.

**Row 0 — PMID 35910216**, *Front Genet* 2022, "Case Report: Gene Heterogeneity in the Recurrent and
Metastatic Lesions of a Myxoid Chondrosarcoma Patient With Aggressive Transformation."
> "Here, we present a case which initially demonstrated a typical indolent course of EMC, but rapidly progressed after the marginal resection and eventually died of pulmonary failure."

Pointer: `terminal_events[57].sentences[0]` (the discussion restatement is `sentences[1]`; one patient,
counted once). ⚠ **No abstract is retained anywhere in this repository for this PMID** — the retained
records in `fusion-consensus-probe.json` and `emc-mortality-probe.json` carry title and metadata only.
⚠ The title says "Myxoid Chondrosarcoma" without "extraskeletal", so the **title alone** would not
establish EMC; the quoted sentence does.

**Row 1 — PMID 29977924**, *Biomed Res Int* 2018, "Extraskeletal Myxoid Chondrosarcoma: A Comparative
Study of Imaging and Pathology."
> "One patient died due to lung metastases."

Pointer: `terminal_events[16].sentences[0]`. Abstract:
`queries.emc_topic_lung_mets.top[18].abstract` — "13 cases of EMC confirmed by surgery biopsy were
retrospectively studied", a single-disease series with no comparison group. The abstract does **not**
state how many patients died, so the series' death total is UNKNOWN here.

**Row 2 — PMID 41799218**, *NMC Case Rep J* 2026, "Endovascular Thrombectomy in a Patient with Acute
Ischemic Stroke due to Tumor Emboli Associated with Cardiac Metastasis of Extraskeletal Myxoid
Chondrosarcoma: A Case Report."
> "Despite slight neurological recovery, the patient died of respiratory failure on the 15th day after onset."

Pointer: `terminal_events[2].sentences[0]`. ⚠ No abstract retained. ⚠ `sentences[2]` of the same
paper — "4 of the 11 patients with available postoperative prognoses died in the short term despite
technically successful endovascular therapy" — is a **literature table of thrombectomy patients, not
an EMC group**; it is correctly absent from the classified rows.

**Row 3 — PMID 28638563**, *J Clin Exp Dent* 2017, "Extraskeletal myxoid chondrosarcoma of the
masticator space in a pediatric patient."
> "The patient received adjuvant radiotherapy but died after 1 year of follow-up due to complications of locoregional tumor dissemination to the skull base."

Pointer: `terminal_events[18].sentences[1]` (row also cites `sentences[0,2,5]`; four sentences, one
patient). ⚠ No abstract retained; all six retained sentences concern this one patient.

**Row 4 — PMID 35665108**, *World J Clin Cases* 2022, "Primary intracranial extraskeletal myxoid
chondrosarcoma: A case report and review of literature."
> "Only 1 out of the 11 patients who underwent PR died from local recurrence and spinal metastasis of primary intracranial EMC at 36 mo after surgery[ 9 ]."

Pointer: `terminal_events[9].sentences[1]`. Abstract:
`queries.emc_topic_stereotactic.top[3].abstract` — the **index** 52-year-old patient was alive at 12
months with no recurrence, so this death is **not** the paper's own case; it is a previously published
case reached through the review, cited to reference [9].

**Row 5 — PMID 35665108**, same publication.
> "In our research of the 16 primary intracranial EMC cases available in the literature, 3 did not have any information on the prognosis of patients, and in 2 cases, the patients died from non-EMC-related factors after surgery."

Pointer: `terminal_events[9].sentences[0]`. The deaths are documented; ⛔ the **causes are not named**.
"Non-EMC-related factors" is a negative disease attribution, not a cause and not a non-cancer death.

**Row 6 — PMID 36097623**, *JAAD Case Rep* 2022, "Metastatic extraskeletal myxoid chondrosarcoma
presenting as a forehead mass."
> "The patient subsequently underwent radiation to the brain and failed systemic treatment with chemotherapy and immunotherapy, with the development of further metastases ultimately resulting in death."

Pointer: `terminal_events[6].sentences[0]`. ⚠ The retained record
`queries.emc_topic_metastatic_pattern.top[12]` exists but its `abstract` is **null**.

**Row 7 — PMID 23213584**, *Case Rep Oncol Med* 2012, "Extraskeletal myxoid chondrosarcoma with small
bowel metastasis causing bowel obstruction."
> "Due to persistent anemia and gastrointestinal bleeding, the patient case was presented to the multidisciplinary tumor board, and it was recommended to proceed with palliative small bowel tumor resection."

Pointer: `terminal_events[26].sentences[0]`. ⚠ No abstract retained. ⛔ **This is a complication, not a
death.** It is retained for the harm it documents and is excluded from every death numerator and
denominator, including the stored-mechanism-label count. It documents no survival.

**Row 8 — PMID 23115670**, *J Korean Neurosurg Soc* 2012, "Intracranial extraskeletal myxoid
chondrosarcoma: case report and literature review."
> "Of the remaining five patients, two showed tumor recurrences and two died due to postoperative complications 2 , 14 , 15 , 17) ."

Pointer: `terminal_events[24].sentences[0]`. Abstract:
`queries.emc_topic_radiotherapy.top[22].abstract` — the **index** 21-year-old patient improved after
total resection and radiotherapy, and the abstract states "only seven patients previously reported".
So these two deaths are **previously published intracranial EMC patients**, not the paper's own case.
⚠ Which five patients "the remaining five" are is not retained.

**Row 9 — PMID 32963861**, *Case Rep Orthop* 2020, "Extraskeletal Myxoid Chondrosarcoma: Long-Term
Survival in the Setting of Metastatic Disease."
> "The patient was followed for 126 months, after which he died from complications of unresectable colon cancer."

Pointer: `terminal_events[12].sentences[1]`. Abstract:
`queries.emc_topic_lung_mets_local_therapy.top[16].abstract` — three EMC patients with pulmonary
metastases managed by observation. The sentence names a **disease entity**; the complications
themselves are not named.

**Row 10 — PMID 35251555**, *Rare Tumors* 2022, "Extraskeletal myxoid chondrosarcoma: A case series
and review of the literature."
> "Two patients with EMC died during follow-up from concurrent malignancies ( Table 2 )."

Pointer: `terminal_events[7].sentences[3]` (restated at `sentences[7]`; one event, counted once).
Abstract: `queries.emc_topic_metastasectomy.top[1].abstract` — 15 patients, 11 alive at last follow-up.

**Row 11 — PMID 35251555**, same series.
> "Both patients that presented with metastatic disease to the lungs died within 17 months ( Table 2 )."

Pointer: `terminal_events[7].sentences[4]`. ⚠ It is tempting to read these as respiratory deaths; the
paper does not say so. ⚠ Distinctness from row 10 is arithmetically consistent with the abstract
(15 − 11 alive = 4 deaths = 2 + 2) but **neither quotation states it**.

**Row 12 — PMID 35775709**, *Pathologica* 2022, "Primary extraskeletal myxoid chondrosarcoma of the
breast: report of a case and literature review."
> "Three patients died 9 months (the patient with lung and skin metastasis later developed congestive heart disease), 10 months (the patient with hepatic metastasis), and 9.5 years (cerebral hemorrhage but no tumor recurrence) following the primary diagnosis ( Tab."

Pointer: `terminal_events[8].sentences[0]`. Abstract:
`queries.emc_topic_lung_mets_local_therapy.top[22].abstract` — the **index** 45-year-old patient was
in clinical and radiologic remission 18 months after surgery, so these three deaths are **not** the
paper's own case; they come from the review table the sentence points at, which is **truncated in the
retained sentence and not retained anywhere**. ⛔ Row-level disease membership is therefore
**UNRESOLVED**. The hepatic-metastasis member **states metastasis at death and assigns no cause**.

**Row 13 — PMID 22569967**, *Virchows Arch* 2012, "NR4A3 rearrangement reliably distinguishes between
the clinicopathologically overlapping entities myoepithelial carcinoma of soft tissue and cellular
extraskeletal myxoid chondrosarcoma."
> "Two patients died of disease 8 months after the initial diagnosis."

Pointer: `terminal_events[34].sentences[1]`. **The disposing evidence** is the retained primary
abstract at `queries.emc_topic_lung_mets.top[4].abstract` (identical copy at
`queries.emc_topic_series_outcomes.top[17].abstract`):

> "…we compare ten MECs with five cEMCs. MEC patients had an equal gender distribution. … Follow-up,
> available for nine patients, ranged from 4 to 85 months… **Five patients were alive without
> evidence of disease, two were alive with disease and two died 8 months after the initial
> diagnosis.** cEMCs were from three males and two females… Follow-up, available for four patients,
> ranged from 6 to 220 months… **All patients were alive**, two with recurrences and/or metastases
> and two without evidence of disease."

The probe preserves the same group transition at `terminal_events[34].sentences[0]`, and the paper's
statement about the cellular-EMC group at `terminal_events[34].sentences[2]`: **"No patient died of
the disease so far."**

⛔ **The two deaths are myoepithelial-carcinoma deaths. They are not EMC deaths and must not appear in
an EMC-specific denominator.** This is accepted finding **F1** and root's independent confirmation.

**Row 14 — PMID 25177237**, *Radiol Oncol* 2014, "Clinical and radiologic features of extraskeletal
myxoid chondrosarcoma including initial presentation, local recurrence, and metastases."
> "Three patients died during the time-frame of the study, 1 was lost to follow up, and 9 are still alive."

Pointer: `terminal_events[28].sentences[2]` (row also cites `sentences[0,4,5,6,7,8]`; seven sentences,
the same three deaths). Abstract: `queries.emc_topic_radiotherapy.top[17].abstract` — 13 patients with
pathologically proven EMC.

**Row 15 — PMID 36326382**, *Turk J Med Sci* 2022, "Surgical outcomes of extraskeletal myxoid
chondrosarcoma."
> "While recurrence developed in 5 (38.5%) of the patients during follow-up, lung metastasis (46.2%) was detected in 6 patients, and 7 patients (53.8%) died due to the disease and complications related to the disease."

Pointer: `terminal_events[5].sentences[2]` (also `sentences[0]`). Abstract:
`queries.emc_topic_lung_mets_local_therapy.top[14].abstract` — 13 EMC patients, 2006–2018.
⚠ `sentences[5]` of the same paper describes Enzinger and Shiraki's historical 34 patients with 4
deaths — a **different group**, correctly not counted.

**Row 16 — PMID 32612944**, *Front Oncol* 2020, "Extraskeletal Myxoid Chondrosarcoma: Clinical and
Molecular Characteristics and Outcomes of Patients Treated at Two Institutions."
> "With a median follow-up time of 72 months, 20 patients have died."

Pointer: `terminal_events[15].sentences[1]`. Abstract:
`queries.emc_topic_radiotherapy.top[19].abstract` — 59 patients with confirmed EMC, 1980–2018.
⛔ These are **all-cause** deaths; the paper splits no causes.

**Row 17 — PMID 21941486**, *Case Rep Oncol* 2011, "A case of highly aggressive extraskeletal myxoid
chondrosarcoma."
> "The patient consequently deteriorated clinically and was referred for palliative radiation and transitioned to supportive care."

Pointer: `terminal_events[27].sentences[1]`. Abstract:
`queries.emc_topic_lung_mets_local_therapy.top[17].abstract`. ⛔ **The death itself is not described.**
The retained sentence proves neither death nor survival.

## Rows carried in the artifact but not contributing to the death rows

Preserved here so the audit is complete; none of them is a classified death row and none is changed.

- `aggregate_cause_splits` — three overlapping strata of PMID 40885991 (a national registry), already
  marked in the artifact as **excluded from any pooling** because pooling overlapping strata from one
  registry double-counts patients.
- `prognostic_findings` — one multivariate association from PMID 40885991. Not a death record.
- `not_a_patient_death_examples` — five sentences carrying a death cue that document **no patient
  death here**: a methods definition (40885991), an explicit negative (27418251), an endpoint
  definition (24345066), another disease's cohort cited in discussion (26125202), and a general
  sarcoma radiotherapy series (35494187). ⭐ Two of these are exactly the title-versus-membership trap:
  the paper matched, the patients were someone else's.

## Summary of dispositions

Counted over the 18 preserved rows, and stated as row dispositions rather than as a tally of anything:

- **13 rows** are documented deaths in a group the retained context places **within EMC**:
  rows 0, 1, 2, 3, 4, 5, 6, 9, 10, 11, 14, 15 and 16. Of these, rows 4 and 5 sit in a
  literature-collected set rather than in the reporting institution's own cohort.
- **1 row** (row 8) is a documented death in previously published **intracranial EMC** patients whose
  individual identity is not retained and whose overlap with rows 4 and 5 is undetermined.
- **1 row** (row 12) is documented deaths whose **disease membership is unresolved** from the retained
  material.
- **1 row** (row 13) is documented deaths in the **wrong disease** — myoepithelial carcinoma.
- **2 rows** (rows 7, 17) **document no death at all**; one documents a complication, one a transition
  of care. Neither documents survival.
The five categories above partition all 18 rows: 13 + 1 + 1 + 1 + 2 = 18, with no row dropped.

Cutting across that partition, and not a sixth category: row 5 (n = 2) is a documented death whose
**cause is not named**, and rows 15 and 16 carry **collective or all-cause** attributions with no
per-patient mechanism.

⛔ **No headline count is produced from this.** Rows 8, 12 and 13 each change what any EMC-specific
denominator may contain, and rows 4, 5 and 8 carry an undetermined overlap, so the retained material
does **not** support a single validated EMC death count. Stating one would substitute a new unexamined
number for the old one — the exact failure recorded in
[`HOLD-mortality-death-counts.md`](HOLD-mortality-death-counts.md).

## What the sources DO support

- **Row 13 is a wrong-disease row, on the paper's own words.** The retained primary abstract assigns
  the two deaths to the myoepithelial-carcinoma group and states that every followed cellular-EMC
  patient was alive. This is a documented exclusion, not an inference from absence.
- **Row 13 is the only instance of that exact defect** among the 18 rows: no other contributing
  publication in this set contains a second, non-EMC disease group that the counted deaths belong to.
  ⚠ This is a statement about the **retained context of these 18 rows**, not about the literature.
- **A related but distinct defect is present in four rows** (4, 5, 8 and 12 — three source records,
  eight patient instances; corrected 2026-09-08, the earlier "three rows" miscounted the rows against
  the records): the deaths belong
  to **previously published cases reached through a literature review**, not to the reporting paper's
  own patients. The disease is right in rows 4, 5 and 8; the **source type and the overlap** are not
  what a primary-cohort count assumes.
- **Two rows document no death** (7, 17), and the artifact already records them as such.
- **Where an abstract is retained, membership is checkable**; for rows 0, 2, 3 and 7 no abstract is
  retained anywhere in this repository, and membership rests on the title plus the quoted sentence.
- **Several rows carry attributions weaker than their stored labels** — row 1 (broad cause), row 5
  (no cause named), row 12's hepatic member (metastasis at death, no cause assigned), rows 15 and 16
  (collective and all-cause). This matches accepted finding F6 and the artifact's own
  `mechanism_tier` disclosure.

## What the sources DO NOT support

- ⛔ **They do not support any EMC-specific death total, mechanism share, cause fraction, causal
  ceiling, or competing-mortality partition.** Unknown membership (row 12), unretained case identity
  (row 8), undetermined overlap (rows 4, 5, 8) and unnamed causes (row 5) each prevent it.
- ⛔ **They do not establish that the counted reports describe distinct patients.** Two contributing
  reports collect previously published intracranial cases; whether they share patients with each other
  or with the case reports **cannot be determined from what was retrieved**.
- ⛔ **They do not establish a dominant mode of death, or the absence of mechanism reporting in the
  literature.** This is a selected death-cue and title-eligible collection.
- ⛔ **They do not establish any clinical, therapeutic, prognostic or capacity conclusion**, and
  nothing here bears on EMC efficacy, safety, selectivity or clinical readiness.
- ⛔ **The review's illustrative 48 / 13 / 25 is not supported as a replacement tally**, and is not
  adopted here.

## Effect on the parked paper's reopening condition — plainly

This curation is **membership and death-documentation evidence for the retained sources**. Measured
against the reopening conditions in [`HOLD-mortality-causal-ceiling.md`](HOLD-mortality-causal-ceiling.md):

- ⛔ **It does not meet the condition for reinstating the quantitative central claims.** That requires
  a defensible common-horizon competing-risk or excess-hazard estimand, time and censoring
  information, verified cohort demographics with suitable life-table matching, and a justified
  synthesis. **None of those is produced or approached here**, and F2, F3, F4, F5 and F7 are untouched
  by anything in this document.
- ⛔ **It does not meet the condition for reinstating comprehensive-absence or supportive-care efficacy
  claims.** That requires a separately authorized source and synthesis scope (F9). No new source was
  retrieved and no such authority is claimed.
- ⭐ **It supplies one input the hold names as a prerequisite for a possible future, narrowly scoped
  reporting audit or data note: coherent disease-membership and context coding of the retained
  rows** — F1's minimum repair ("verify disease-group identity in the context of each already retained
  contributing source… If the retained context cannot establish a row's EMC membership, classify its
  membership as unresolved") and part of F6's evidence-table requirement.
- ⛔ **That is one input among several, and it is not authorization.** The hold is explicit that such a
  revision is a possible author choice **only after explicit root or author merit adjudication**, and
  that "this is not authorization to produce that revision now." The remaining prerequisites —
  withdrawal of the causal ceilings and relative-derived cause fractions, scoped literature assertions
  with primary citations and dependencies, corrected declarations and provenance descriptions — are
  **not** addressed here.
- ⛔ **The paper stays parked.** Clean lint and a well-sourced table are not the evidence the reopening
  condition asks for, and this document asserts none of the claims the hold withdrew.

## Verification

Run on 2026-09-08, exit codes preserved as measured:

- `python3 research/manuscripts/lint_claims.py <this file>` → **exit 0**, `0 ERROR, 4 WARN`.
  ⚠ All four WARNs are `R4` substring hits inside **verbatim retained source wording** —
  "13 patients with pathologically proven EMC" (PMID 25177237's abstract) and "59 patients with
  confirmed EMC" (PMID 32612944's abstract). They are the sources' words about their own histology,
  not a claim made by this document, and they are left unaltered because rewording a quotation would
  misquote it.
- `python3 research/manuscripts/lint_consistency.py` → **exit 0**, `0 ERROR across 29 target file(s)`.
  ⚠ That linter takes no file argument: it runs over a fixed registry of targets. **This file is not
  in that registry**, and it was not added — the registry is shared state outside this lane. So the
  clean result is the repository's, and is **not** a check of this document.

⛔ No wider test suite was run, nothing was committed or pushed, and no other lane's files, the
manifest, the claim-coverage record and `systems/graph/` were touched.
