---
id: DOC-ATU027-SYSTEMIC-SIRNA-SOLID-TUMOUR
title: "Tolerated is not engaged — what the two completed Atu027 systemic-siRNA solid-tumour trials actually produced, graded against the delivery gate"
level: L3
kind: memo
status: live
canonical_for:
  - the outcome evidence of NCT00938574 and NCT01808638, and its grade
  - whether the completed Atu027 trials move BLK-DELIVERY
  - the registry-level inventory of systemically administered oligonucleotide trials in solid tumours held by this repository
purpose: >
  research/manuscripts/aso/aso-delivery-evidence-2026-08.md §6 recorded, as the one UNKNOWN on the
  gate itself, that two completed Silence Therapeutics trials of a systemically administered siRNA in
  solid tumours had been read at registry-status level only and never for outcomes. This memo reads
  them: the registry records, the peer-reviewed publications, and — separately and deliberately — the
  question of whether anything in them shows the siRNA reaching a tumour. It grades every claim and
  states what remains UNKNOWN.
scope: >
  Retrieval and grading only. Nothing here unparks a route, re-grades a blocker, or edits
  research/method-watch.md or anything under research/manuscripts/neoantigen/. Nothing here asserts or
  implies efficacy, safety, a therapeutic window, selectivity or clinical readiness for any agent
  named, in EMC or in any other disease; where a source reports a safety or survival figure it is
  reported as that source's finding about that trial and nothing is inferred from it.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
---

# Tolerated is not engaged

## 0 · The answer, in one line

**No. `BLK-DELIVERY` does not move on Atu027.** Both trials measured **administration tolerability and
plasma pharmacokinetics**. Neither prespecified — and neither publication reports — a tumour biopsy, a
biodistribution measurement, or any tissue-level PKN3 readout. What is established is that a lipoplex
siRNA can be infused into people with advanced solid tumours and that its components appear in plasma
with a measurable half-life. What is **not** established, anywhere in this programme, is that any of it
reached a tumour.

**`BLK-DELIVERY` stands. `RT-ASO` stays parked.** The re-grade is not this agent's to make; this memo is
evidence plus a recommendation (§8).

⚠ **A second reason, specific to this agent, and it is the one most likely to be lost.** Atu027's
*intended* target cell is the **vascular endothelium** — the sponsor's description, the authors'
description, and the design of the molecule. Endothelium lines the lumen; it is on the **blood side** of
the vessel wall. So even a fully successful Atu027 would not have shown that an oligonucleotide crosses
the vasculature into tumour parenchyma, which is exactly what a fusion-junction ASO would have to do in
an EMC nodule. **Reading "systemic siRNA worked in a solid-tumour trial" off this programme would import
a claim the programme never even set out to make.**

### ⭐ The genuinely on-gate thing the same $0 queries surfaced

Nobody asked for it and it is stronger than what was asked for. The registry searches run for Atu027
returned two other trials, and one of them has a published result that **is** the shape `BLK-DELIVERY`
waits for:

> **Davis ME, Zuckerman JE, Choi CH, Seligson D, Tolcher A, Alabi CA, Yen Y, Heidel JD, Ribas A.**
> *Evidence of RNAi in humans from systemically administered siRNA via targeted nanoparticles.*
> **Nature** 2010;464(7291):1067–1070. **PMID 20305636**, **PMC2855406**, **doi:10.1038/nature08956**.
> Open access; full text retrieved and read (§6).

An intravenously infused, **non-GalNAc, non-hepatocyte-targeted** siRNA nanoparticle (CALAA-01,
`NCT00689065`) was found **intracellularly in melanoma tumour biopsies**, in amounts tracking the dose,
absent from adjacent epidermis and absent from every pre-dosing sample; target mRNA and protein were
reduced against pre-dosing tissue; and an RNAi-specific mRNA cleavage fragment was detected in one
patient. **Three patients. One accessible tumour type. Voluntary biopsies. Two of three baselines were
archive tissue taken months earlier — the authors say so themselves. The trial is `TERMINATED` with no
registry results record.** It is a proof of principle at n=3 from 2010, not a validated delivery route,
and it says nothing whatever about EMC or a myxoid matrix. §6 states its limits in the authors' own
words, because the temptation to round it up is the whole risk here.

Every identifier in this memo is anchored in
[`atu027-systemic-sirna-solid-tumour-evidence.json`](./atu027-systemic-sirna-solid-tumour-evidence.json),
which records the runner job that returned it. Nothing here was typed from recollection.

---

## 1 · Grades at a glance

| Claim | Grade |
|---|---|
| The two Atu027 trials' design, status, enrolment, outcome measures | **registry record retrieved verbatim** (ClinicalTrials.gov API v2, HTTP 200) |
| The Phase I (`NCT00938574`) result | **traced to primary source, abstract level** — J Clin Oncol 2014 is paywalled, body not retrieved |
| The Phase Ib/IIa (`NCT01808638`) result | **traced to primary source, FULL TEXT** — Cancers 2020 is open access, body retrieved and searched |
| The 2012 Int J Clin Pharmacol Ther record | **bibliographic record only** — Europe PMC carries no abstract for it |
| "No tumour target engagement was measured in either trial" | **full text for the later trial; registry + abstract for the earlier** (§3, §7 UNKNOWN 1) |
| Programme continuation | **registry-verified absence** + **press retrieved verbatim** from the sponsor's own site |
| CALAA-01 tumour target engagement | **traced to primary source, FULL TEXT**, open access |
| EPHARNA (`NCT01591356`) status and prespecified endpoints | **registry record retrieved verbatim**; its 2025 result is **conference-abstract grade** |
| The other-trials list in §7 | **registry existence and status only** — no outcome read or implied for any row |

---

## 2 · The two trials, from the registry

Both records were pulled from `https://clinicaltrials.gov/api/v2/studies/<NCT>`, HTTP 200, and are
reproduced in the JSON sidecar. **`hasResults` is `false` for both and neither record carries a results
section** — so ClinicalTrials.gov itself holds no outcome data for either trial.

| | **`NCT00938574`** | **`NCT01808638`** |
|---|---|---|
| Sponsor ID | Atu027-I-01 | Atu027-I-02 |
| Official title | *A Prospective, Open-label, Single Center, Dose Finding Phase I-study With Atu027 (an siRNA Formulation) in Subjects With Advanced Solid Cancer* | *A PHASE Ib/IIa STUDY OF COMBINATION THERAPY WITH GEMCITABINE AND ATU027 IN SUBJECTS WITH LOCALLY ADVANCED OR METASTATIC PANCREATIC ADENOCARCINOMA* |
| Sponsor | Silence Therapeutics GmbH | Silence Therapeutics GmbH |
| Phase | Phase 1 | Phase 1/2 |
| Design | single group, open label, single centre | randomised, parallel, open label |
| Enrolment (ACTUAL) | 34 | 29 ⚠ |
| Condition | Advanced Solid Tumors | Carcinoma, Pancreatic Ductal |
| Status | `COMPLETED`, 2012-09 | `COMPLETED`, 2016-01 |
| `whyStopped` | none recorded | none recorded |
| `hasResults` | **false** | **false** |

**`NCT00938574`'s outcome list is complete as returned and contains no tissue endpoint of any kind:**
primary is *"Determination of dose-limiting toxicities (DLT) and maximum tolerated dose (MTD) of single
and repeated intravenous infusion"*; the three secondaries are pharmacokinetics of Atu027 and its
components, clinical safety and tolerability, and RECIST response.

**`NCT01808638` prespecifies more, and every measurement it prespecifies is in blood or on a scan:**
adverse events, physical examination, vital signs, ECG, laboratory parameters, and **plasma**
pharmacokinetics (Cmax, AUC, tmax, t½ of the siRNA A-strand, the cationic lipid AtuFect01 and the helper
lipid DPyPE) as primaries; ORR by RECIST 1.1 on MRI/CT, PFS and OS, ECOG, quality of life, tumour markers,
and one **"Biomarker response"** endpoint whose own description reads *"Serum protein markers and
circulating microRNA"* — **serum and circulating**, i.e. the blood compartment.

⚠ **The registry enrolment (29) does not match the publication** (3 lead-in safety subjects plus 24
randomised, of whom 1 was a screening failure, giving 23 treated in the treatment period). Nothing
retrieved reconciles them; the discrepancy is recorded rather than resolved.

---

## 3 · The published results — verified citations

Three publications, all verified against Europe PMC core records (HTTP 200, one hit each on an
`EXT_ID:<pmid> AND SRC:MED` query).

### 3a · The Phase I · `NCT00938574`

> Schultheis B, Strumberg D, Santel A, Vank C, Gebhardt F, Keil O, Lange C, Giese K, Kaufmann J,
> Khan M, Drevs J. *First-in-human phase I study of the liposomal RNA interference therapeutic Atu027
> in patients with advanced solid tumors.* **J Clin Oncol** 2014;32(36):4141–4148.
> **PMID 25403217**, **doi:10.1200/jco.2013.55.0376**. Europe PMC reports it **not** open access
> (no PMCID); cited 193 times at retrieval.

A second, three-page record exists for the same programme and carries **no abstract in Europe PMC**:

> Strumberg D, Schultheis B, Traugott U, Vank C, Santel A, Keil O, Giese K, Kaufmann J, Drevs J.
> *Phase I clinical development of Atu027, a siRNA formulation targeting PKN3 in patients with advanced
> solid tumors.* **Int J Clin Pharmacol Ther** 2012;50(1):76–78. **PMID 22192654**,
> **doi:10.5414/cpp50076**. Not open access. Nothing is claimed from it beyond its existence.

### 3b · The Phase Ib/IIa · `NCT01808638`

> Schultheis B, Strumberg D, Kuhlmann J, Wolf M, Link K, Seufferlein T, Kaufmann J, Feist M,
> Gebhardt F, Khan M, Stintzing S, Pelzer U. *Safety, Efficacy and Pharcacokinetics of Targeted Therapy
> with The Liposomal RNA Interference Therapeutic Atu027 Combined with Gemcitabine in Patients with
> Pancreatic Adenocarcinoma. A Randomized Phase Ib/IIa Study.* **Cancers (Basel)** 2020;12(11):E3130.
> **PMID 33114652**, **PMC7693593**, **doi:10.3390/cancers12113130**. Open access; **full text
> retrieved** (Europe PMC `fullTextXML`, HTTP 200, 86,630 characters). Cited 56 times at retrieval.

*("Pharcacokinetics" is the publisher's spelling in the record as returned, reproduced unaltered.)*

---

## 4 · The question the gate turns on — and the two things that must not be conflated

**Was there any evidence the siRNA REACHED a non-hepatic solid tumour?**

**No.** For the Phase Ib/IIa this is a **measurement on the retrieved full text**, not an impression.
Tags stripped, whitespace collapsed, case-insensitive counts over the whole body including references:

| term | occurrences in PMC7693593 |
|---|---|
| `biops` (biopsy, biopsies, biopsied) | **0** |
| `biodistribution` | **0** |
| `knockdown` / `knock-down` | **0** |
| `tumor tissue` / `tumour tissue` | **0** |
| `target engagement` | **0** |
| `pharmacodynam` | **0** |
| `immunohisto` | **0** |
| `microRNA` | **0** ⚠ *(a prespecified endpoint — see §7)* |
| `sFLT` / `VEGF` | **0** |
| `PKN3` | 6 |
| `endotheli` | 8 |

**All six PKN3 mentions are statements of design intent or citations to preclinical work.** The strongest
of them — *"a targeted agent that induces RNAi as well as the down-regulation of the PKN3 mRNA transcript
and protein directly in the vascular endothelium"* — is a description of what the agent **is**, carried
over from mouse and primate work; it is not a report of a measurement made in a trial subject. The
authors' own closing sentence settles the reading: *"Our clinical results support the significant
involvement of the vascular endothelium in the spread of cancer, and thus **the further investigation of
its target role**."* A target role still to be investigated is not a target role demonstrated.

**What the trial did measure, in full:**

- **Plasma pharmacokinetics**, n = 11 (3 lead-in, 4 per arm). Tmax at or just after the end of the 4-hour
  infusion; mean t½ ~10 h for the siRNA, ~20 h for AtuFect01, ~17 h for DPyPE; siRNA Cmax ~150 ng/mL and
  AUC ~1000 h·ng/mL, stable across administrations. Twice-weekly dosing produced ~40–50% plasma
  accumulation of the two lipids by day 18 of cycle 1; once-weekly produced none.
- **A 301-analyte plasma biomarker panel.** 46 and 59 analytes moved from baseline in arms 1 and 2, and 13
  associated with response status — but **after Benjamini–Hochberg correction, one analyte (Factor VII,
  arm 1) changed from baseline and one (Angiopoietin-2) associated with response.** The paper reports the
  correction itself, which is why the uncorrected counts are quoted here only alongside it.
- **Tumour markers** (CA 19-9, CEA), **RECIST 1.1 imaging**, ECOG, EORTC quality of life.

Every one of those is **blood or radiology**. None of them can distinguish "the drug reached the tumour"
from "the drug was in the circulation while the tumour was imaged".

For the **Phase I**, the same conclusion rests on two independent supports and one honest gap. The
registry outcome list contains **no tissue endpoint at all**, and the abstract's only pharmacodynamic
readout is the **plasma protein sFLT1** — *"sFLT1 ... decreased from pretreatment levels in most patients
after dose levels 04 to 10"*, offered explicitly as a candidate biomarker for future study, not as tumour
target engagement. ⛔ **The gap: the JCO body was not retrieved and is not open access, so "the paper
contains no tissue measurement" is an inference from its registry record and abstract, not a reading of
its body.** That inference is exactly the kind CALAA-01 falsifies elsewhere in this memo — its biopsies
were voluntary and appear in no registry outcome list — so it is carried as **UNKNOWN 1** in §7 rather
than stated as fact.

---

## 5 · Safety, dose, and whether the programme continued

⚠ **Reported as each source's finding about its own trial. Nothing here is an assessment of safety, a
therapeutic window, or clinical readiness for any agent, and none is implied.**

**Phase I (`NCT00938574`), as its abstract reports it:** 34 patients, 10 escalating dose levels, one
single infusion followed by eight intravenous infusions twice weekly over a 28-day cycle, no
premedication. *"Atu027 was well tolerated up to dose levels of 0.336 mg/kg; most adverse events were
low-grade toxicities (grade 1 or 2). **No maximum tolerated dose was reached.**"* Disease stabilisation in
14 of 34 at end of treatment; 8 with stable disease at end of study.

**Phase Ib/IIa (`NCT01808638`), as its full text reports it:** the paper describes grade 3 events in 9/11
(arm 1) and 11/12 (arm 2), *"mainly laboratory abnormalities without clinical significance"*; four
subjects (17%) with a grade 4 event (one lipase increase, one hyperglycaemia, two neutrophil-count
decreases); 23 serious adverse events across 16 subjects, of which **two** were judged treatment-related.
Twice as many events were attributed to gemcitabine (n = 110) as to Atu027 (n = 49); the most frequent
Atu027-attributed event was fatigue, *"never dose-limiting"*.

⚠ **The dose figure for this trial is internally inconsistent in its own publication.** The abstract says
**0.235 mg/kg**; the Subjects and Methods section says **0.253 mg/kg**, for both arms. They are digit
transpositions of one another and the paper does not reconcile them. **Which is correct is UNKNOWN** and
no dose from this trial is quoted elsewhere without this caveat.

**Did the programme continue or stop?** Two readings, both retrieved, neither a discontinuation notice.

1. **Registry-verified absence.** `query.spons=Silence Therapeutics` returns 8 studies (control passed —
   §7). The two Atu027 trials are the only oncology solid-tumour entries, both under *Silence Therapeutics
   GmbH*. **No Atu027 trial is registered after `NCT01808638`**, and every later trial under *Silence
   Therapeutics plc* — `NCT05499013`, `NCT04718844`, `NCT04176653` (withdrawn), `NCT04559971`,
   `NCT04606602`, `NCT05537571` — is a hepatocyte-directed GalNAc-siRNA programme, i.e. the canonical
   liver paradigm this route already discounts. ⛔ That is an absence from one registry under one query,
   not proof of formal termination.

2. **⭐ The sponsor's own last word, and it names delivery.** Press release *"Atu027 Update"*,
   **05 April 2016**, RNS 1376U, retrieved HTTP 200 from the company's own site:

   > *"We will now actively pursue partnering and collaboration opportunities both with Atu027 and PKN3
   > as a target."*
   >
   > *"We plan to do further pre-clinical work in order to ensure that PKN3 is targeted as effectively as
   > possible. These R&D activities will include optimisation of in house technology (AtuPLEX) as well as
   > **evaluation of external delivery systems with the potential of complementing proprietary assets to
   > strengthen our drug candidate**."*

   The sponsor announced no stop. It announced partnering plus a return to **pre-clinical** work, and the
   thing it named as needing strengthening was **the delivery system**. That is a company statement, not
   a measurement — but it is the sponsor placing the open problem in the same place `BLK-DELIVERY` puts
   it, which is worth recording precisely because it is not this repository's own framing.

**No document stating that the programme was discontinued, and no stated reason, was located.** The
company site's current navigation lists only Divesiran and Zerlasiran as products (read from the
retrieved page's own navigation, 2026-08-24); the pipeline URL tried returned HTTP 404. **Absence from a
navigation menu is not a discontinuation statement.** Carried as UNKNOWN.

---

## 6 · The precedent that does bear on the gate — and its limits, in the authors' words

`NCT00689065`, *A Phase I, Dose-Escalating Study of the Safety of Intravenous CALAA-01 in Adults With
Solid Tumors Refractory to Standard-of-Care Therapies*, Calando Pharmaceuticals, Phase 1, 24 enrolled,
**`TERMINATED`**, `hasResults` false, no reason recorded.

⚠ **Its registry record prespecifies no tissue endpoint either** — safety and MTD primary; PK, tumour
response, dose recommendation and immune/complement effects secondary. **The biopsies are nowhere in it,
and the biopsies are the entire result.** That is the load-bearing methodological lesson of this memo: a
registry outcome list is a **floor** on what a trial measured, never a ceiling.

**What was found**, from the retrieved open-access full text:

- Nanoparticles **intracellular in post-dosing tumour tissue and absent from adjacent epidermis**;
  staining intensity ordered by dose across the three patients (30 > 24 > 18 mg-siRNA/m²), and **every
  pre-dosing sample completely negative**. The authors call it *"the first example of a dose-dependent
  accumulation of targeted nanoparticles in tumors of humans from systemic injections for nanoparticles
  of any type."*
- **RRM2 protein reduced 5-fold** by blinded IHC scoring across 10 random regions in patient C's
  pre/post pair, while the transferrin receptor rose 1.2-fold in the same sections.
- **Direct mRNA evidence in the one pair collected 10 days apart during the trial**: *"the PCR data from
  the C2 pre vs. C2 post samples ... provide direct evidence for RRM2 mRNA reduction via the treatment of
  the patient with the nanoparticles."*
- An mRNA cleavage fragment at the site predicted for an RNAi mechanism, in the patient at the highest
  dose.

⛔ **The limits, quoted rather than paraphrased, because they are what keep this from being over-read:**

> *"Given the highly experimental nature of this protocol, the regulatory process at both the local and
> federal levels explicitly precluded a provision for mandatory biopsies in all patients. Therefore,
> biopsies were obtained on a voluntary basis."*
>
> *"Since samples A pre and B pre are from tissues collected many months before the initiation of siRNA
> treatment, the fraction of the overall reduction in mRNA observed in A post and B post attributable to
> the nanoparticle treatment cannot be directly ascertained."*
>
> *"Unfortunately, we were not able to perform PCR on the C1 samples."*
>
> *"The IHC data from patient A do not reveal changes in RRM2 expression after dosing..."*

**Three patients. One tumour type. Cutaneous and subcutaneous melanoma deposits — lesions chosen partly
because they are reachable by a voluntary biopsy needle. The trial terminated.** ⚠ **And the distance to
EMC is not small:** an accessible melanoma nodule is not a deep, hypocellular, matrix-rich EMC nodule,
and RRM2 in a proliferating melanoma cell is not a fusion transcript in a myxoid stroma. **This does not
clear `BLK-DELIVERY`.** What it does is change what "no human precedent exists" may honestly be taken to
mean — the honest statement is *"one n=3 mechanistic demonstration exists, from 2010, in an accessible
tumour type, from a programme that terminated"*.

### ⭐ And there is a live trial with the right endpoint already prespecified

`NCT01591356`, *EphA2 Gene Targeting Using Neutral Liposomal Small Interfering RNA Delivery: A Phase I
Clinical Trial* (EPHARNA), M.D. Anderson Cancer Center, Phase 1, **49 enrolled (ACTUAL)**,
`ACTIVE_NOT_RECRUITING`, estimated completion 2027-04-30, record last updated **2026-07-17**,
`hasResults` false. Its secondary outcomes, verbatim from the registry, include:

> *"Changes in ephrin type-A receptor 2 expression — **Tissue effects will be assessed in core biopsy
> samples collected pre-treatment and course 1 day 2 or day 3**"*, *"Percent of patients with ephrin
> type-A receptor 2 expression modulation, defined as a 50% decrease from baseline expression"*, and
> *"Changes in endothelial and tumor cell apoptosis conducted by terminal deoxynucleotidyl transferase
> dUTP nick end labeling assay"*.

A 2025 ASCO abstract (**doi:10.1200/jco.2025.43.16_suppl.3086**, conference-abstract grade, retrieved via
a bibliographic API) reports 48 patients treated, the adverse-event profile, five dose-limiting
toxicities, no partial or complete responses among 25 evaluable, and that *"the study was closed to
enrollment prior to confirmation of the MTD due to unavailability of the drug"*. **It reports none of the
tissue endpoints.** ⛔ **So the single most gate-relevant readout located anywhere in this exercise — a
prespecified pre/post tumour biopsy of target modulation in a systemic-siRNA solid-tumour trial — exists,
is registered, is at an academic centre, and is UNREPORTED.** That is a watch, not a spend.

---

## 7 · What remains UNKNOWN — and the controls behind every zero

**All five controls passed.** No zero in this memo rests on an unvalidated query.

| control | purpose | result | verdict |
|---|---|---|---|
| ClinicalTrials.gov `query.term=Atu027` | known-positive for the endpoint used to enumerate the programme | totalCount **2** — exactly `NCT00938574` and `NCT01808638` | ✅ |
| ClinicalTrials.gov `query.intr=patisiran` | known-positive for the endpoint used in the §7 survey searches | totalCount **17** | ✅ |
| ClinicalTrials.gov `query.term=zzqqxxnotadrugname` | does the endpoint return an honest zero, not a default page | totalCount **0**, empty array | ✅ |
| Europe PMC `EXT_ID:20305636 AND SRC:MED` | known-positive for the Europe PMC search endpoint | hitCount **1** | ✅ |
| Europe PMC literal `"qqzzxx-not-a-real-term-9f3b"` | negative control | hitCount **0** | ✅ |

⚠ **Carried forward from the prior memo, and it does not bite here:**
[`aso-delivery-evidence-2026-08.json`](./aso-delivery-evidence-2026-08.json) records that
`query.term=divesiran` returned zero for a drug whose trial **is** in the registry under a code name —
a real failure mode of `query.term` for brand/code-name synonyms. **No conclusion in this memo rests on a
`query.term` zero**: the Atu027 term control passed and returned the sought records.

**Open questions:**

1. **Whether the JCO 2014 body reports any tissue-level measurement.** Not open access, no PMCID, body not
   retrieved. Its registry record has no tissue endpoint and its abstract names only plasma sFLT1 — but
   **CALAA-01 in §6 is the counter-example that forbids treating that as settled.** UNKNOWN.
2. **What the 2012 Int J Clin Pharmacol Ther record contains.** No abstract in Europe PMC, not open access.
3. **Whether the Atu027 dose in `NCT01808638` was 0.235 or 0.253 mg/kg.** The paper states both.
4. **Why the registry's actual enrolment (29) differs from the publication's 3 + 23.**
5. **What the prespecified "circulating microRNA" biomarker endpoint showed.** The publication reports a
   301-analyte plasma panel and never uses the word. A registered endpoint absent from the primary
   publication is an unreported measurement, not a null one.
6. **Whether the Atu027 programme was formally discontinued and on what reason.** No such statement
   retrieved (§5).
7. **⭐ What the EPHARNA tumour-biopsy target-modulation and apoptosis endpoints showed.** The one open
   question here that sits directly on the gate.
8. **Whether any systemic-ASO trial in §7's table reported tumour-tissue target engagement.** Registry
   existence and status only were read for every row.

---

## 8 · Other systemically administered oligonucleotide trials in solid tumours

⛔ **Registry existence and status only. No outcome, efficacy or safety is read or implied for any row.**
Method: three ClinicalTrials.gov API v2 searches — `query.intr=siRNA` + `query.cond=solid tumor` (11),
`query.intr=antisense oligonucleotide` + `query.cond=solid tumor` (13), `query.intr=small interfering RNA`
+ `query.cond=neoplasms` (23). ⚠ **These totals are what one registry matched under three spellings — a
convenience sample, not a census**, and rows whose route is not stated in the registry title were not
individually verified as systemic. Rows that are *not* systemically delivered oligonucleotides are kept
with that label so the next reader does not re-derive the filter. Full table in the JSON sidecar.

**Systemic siRNA, non-hepatic solid tumour — the class that bears on the gate:**

| NCT | agent | phase | status |
|---|---|---|---|
| `NCT01591356` | EphA2 siRNA in DOPC neutral liposomes (EPHARNA) | 1 | `ACTIVE_NOT_RECRUITING` ⭐ *biopsy endpoint prespecified* |
| `NCT00689065` | CALAA-01 (transferrin-targeted cyclodextrin nanoparticle, anti-RRM2) | 1 | `TERMINATED` ⭐ *tumour target engagement published* |
| `NCT00938574` | Atu027 | 1 | `COMPLETED` |
| `NCT01808638` | Atu027 + gemcitabine | 1/2 | `COMPLETED` |
| `NCT02110563` | DCR-MYC (lipid-nanoparticle DsiRNA) | 1 | `TERMINATED` |
| `NCT03608631` | MSC-derived exosomes carrying KRAS G12D siRNA | 1/2 | `RECRUITING` |
| `NCT06424301` | NUDT21-targeting siRNA, refractory retinoblastoma | early 1 | `RECRUITING` *(route not verified)* |

**Systemic ASO in solid tumours:** `NCT00543231`, `NCT00054548`, `NCT00636545` (oblimersen);
`NCT00471432` (custirsen); `NCT00385775` (AEG35156, `TERMINATED`); `NCT00466583` and `NCT01120288`
(EZN-2968); `NCT02144051` (AZD5312); `NCT03101839` (AZD4785); `NCT04504669` (AZD8701);
`NCT04196257` (BP1001-A, `RECRUITING`); `NCT04862767` (TASO-001); `NCT05267899` (WGI-0301, `UNKNOWN`).

**Excluded, with the reason kept:** `NCT01188785` and `NCT01676259` (siG12D LODER — a **local implanted**
drug-eluting device); `NCT07583914` (NCP-CD47 — **intratumoural** injection); `NCT02166255`, `NCT03087591`,
`NCT06172894` (APN401 — **ex vivo** siRNA-transfected PBMC); `NCT00672542` (ex vivo dendritic cells);
`NCT02314052` and `NCT01437007` (DCR-MYC and TKM-080301 in **liver** indications); `NCT04995536`
(`WITHDRAWN`, never conducted).

⚠ **Intratumoural and implanted-device rows are not failures of this search — they are route R1 in
[`lit-targets-aso-delivery-routes.json`](./lit-targets-aso-delivery-routes.json)**, which the 2026-08-12
rescope pulled out from under `BLK-DELIVERY` because it needs no surface antigen. They are labelled, not
discarded.

---

## 9 · Recommendation

1. **Do not unpark `RT-ASO` and do not re-grade `BLK-DELIVERY` on Atu027.** Neither trial produced a
   tumour target-engagement result, and the agent's own intended target cell sits on the blood side of
   the vessel wall. This memo is evidence plus a recommendation; the re-grade is not this agent's to make.
2. **Raise with whoever owns [`blockers.json`](../../../systems/graph/blockers.json) that the blocker's
   evidence base has changed shape, without the blocker clearing.** It now has a **named human precedent**
   (`PMC2855406`, n = 3, 2010, terminated programme) and a **named ongoing trial with the right endpoint
   prespecified** (`NCT01591356`). Neither clears it. Both make *"no clinical precedent for delivering an
   oligonucleotide to a non-hepatic solid tumour exists"* a sentence this repository should no longer
   write unqualified.
3. **Watch the EPHARNA tissue endpoint** (UNKNOWN 7). Registered, academic, pre/post core biopsies
   prespecified, record updated within the last two months, estimated completion 2027-04. A $0 re-check,
   not a spend.
4. **Close UNKNOWN 1 through a different door or leave it open.** The JCO body needs an institutional or
   interlibrary copy, or an author request; retrying a paywall buys nothing.
5. **Nothing here goes into the fusion-junction ASO manuscript as a delivery claim.** An n=3 melanoma
   result from 2010 and an unreported endpoint in an ongoing trial are not a delivery route for an EMC
   nodule, and §3c of that manuscript must not acquire one.

---

## Appendix · Gate scoreboard for this memo

| Item | Grade | Moves `BLK-DELIVERY`? |
|---|---|---|
| `NCT00938574` → J Clin Oncol 2014;32(36):4141–4148 | traced to primary source, abstract level | **No.** Tolerability and plasma PK; no tissue endpoint prespecified or reported. |
| `NCT01808638` → Cancers 2020;12(11):E3130 | traced to primary source, **full text** | **No.** Zero occurrences of biopsy, biodistribution, knockdown, tumour tissue or pharmacodynamics in the body. |
| Int J Clin Pharmacol Ther 2012;50(1):76–78 | bibliographic record only (no abstract in Europe PMC) | **No** — nothing readable. |
| Atu027 programme continuation | registry-verified absence + sponsor press retrieved verbatim | **No** — and the sponsor's own last statement named delivery as the thing needing work. |
| *(unsought)* `NCT00689065` → Nature 2010;464(7291):1067–1070 | traced to primary source, **full text** | **No — but it is the closest thing to the gate's shape that exists.** n = 3, voluntary biopsies, 2010, programme terminated. |
| *(unsought)* `NCT01591356` EPHARNA | registry record verbatim; 2025 result conference-abstract grade | **Not yet readable** — the prespecified tissue endpoint is unreported. The live follow-up. |
