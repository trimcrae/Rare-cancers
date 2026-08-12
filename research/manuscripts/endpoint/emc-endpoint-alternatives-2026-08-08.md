---
id: DOC-EMC-ENDPOINT-ALTERNATIVES
title: "What should be measured in advanced EMC — and what the 6-month progression-free benchmark is actually benchmarked against"
level: L3
kind: memo
status: live
canonical_for:
  - the provenance and appropriateness of the 6-month progression-free null used in advanced-EMC trials
  - the EMC-specific 6-month progression-free ladder
  - the candidate-endpoint evaluation for advanced EMC and what each costs in patients
purpose: >
  Answer the two questions PUB-ENDPOINT deliberately left open — what outcome variable should be
  tracked in advanced extraskeletal myxoid chondrosarcoma, and how the published trial record would
  read under it — and settle, one way or the other, whether the 6-month progression-free rate the
  field migrated to is benchmarked against anything appropriate for an indolent tumour.
scope: >
  Endpoints, nulls, trial designs and reporting completeness in advanced EMC. It is a note about a
  MEASURING INSTRUMENT. It contains no efficacy, potency, safety, selectivity, therapeutic-window or
  clinical-readiness statement about any agent, no re-analysis of any patient, and no treatment
  recommendation of any kind, including a negative one.
audience: [external reviewers, collaborators, maintainers, autonomous research agents]
date: 2026-08-08
last_verified: 2026-08-08
related: [DOC-RESPONSE-ENDPOINT-REGIME, DOC-POLICY-EVIDENCE]
---

# What should be measured in advanced EMC — and what the 6-month progression-free benchmark is actually benchmarked against

**Feeds:** `PUB-ENDPOINT` (route `RT-ENDPOINT-CHOICE`) — this note is the second half of that paper's
argument, the half its own §6.6 says it cannot supply: *"This paper does not propose a specific
replacement endpoint, because the data that would let anyone compare candidate endpoints on these
patients has not been published."*

**Producer:** [`emc_endpoint_alternatives.py`](../emc_endpoint_alternatives.py) →
[`emc-endpoint-alternatives.json`](./emc-endpoint-alternatives.json), reproducible offline with
`--check`.
**Retrieval corpus:** [`lit-targets-endpoint-benchmarks.json`](./lit-targets-endpoint-benchmarks.json),
fetched to the `literature-cache` branch under `literature/emc-endpoint-benchmarks{,-r2}/`.
**Counts and citations:** [`emc-systemic-therapy-pooling.json`](./emc-systemic-therapy-pooling.json)
and [`emc-endpoint-discordance.json`](./emc-endpoint-discordance.json) own them; nothing is re-typed.

⛔ **Nothing in this note says any treatment works, does not work, is safe, or should be given to
anybody.** Where a trial's published conclusion is shown to depend on the null it chose, that is a
finding about the null.

---

## The short version

1. **The prior hypothesis was that the 6-month progression-free null was an aggressive-histology
   import from the Van Glabbeke / EORTC reference values. It is not, and the corrected finding is
   worse.** The null of 50% is not any Van Glabbeke value; it coincides *exactly* with a published
   EMC-specific figure. The benchmark appears to be EMC-derived — and every EMC-derived benchmark is
   measured on patients receiving chemotherapy, so the endpoint still cannot separate a drug from an
   indolent natural history. **It answers "better than the last regimen", not "better than nothing".**
2. **An EMC-specific 6-month progression-free benchmark has existed since 2008 and a second since
   2013, and this repository did not have either.** Drilon 2008 published 40% and said in its own
   conclusion that the figure was offered as a benchmark for future trials; Stacchiotti 2013
   published 50%.
3. **The 2025 cohort's positive conclusion clears its null by 0.3 percentage points *of null*.**
   16 of 23 clears a 50% null at one-sided exact `p = 0.0466`. The largest null it still clears at
   α = 0.05 is **50.3%**. Against the rate implied by the largest published EMC chemotherapy series,
   `p = 0.3374`.
4. **Recommended: keep the 6-month progression-free rate as primary, require its null to be sourced
   in print, and add the growth modulation index as a co-primary.** The index is the only candidate
   that carries its own control inside each patient, and it costs **zero additional patients**.
5. **The index is currently computable for 0 of 47 patients**, because none of the nine curated EMC
   systemic-therapy reports publishes any patient's time to progression on their previous line. The
   minimal ask is **four dates per patient** from two completed trials.
6. **The confound is not hypothetical — it has been measured once, in a different disease.** In the
   only randomised placebo-controlled trial in an indolent soft-tissue tumour (desmoid, PMID
   30575484), **36% of placebo patients were progression-free at 2 years and 20% had an objective
   response**. ⛔ Not transferable to EMC; quoted as an existence proof about endpoints (§6).

---

## 1 · What each trial actually tested, and against what

`emc-endpoint-discordance.json` → `D5` established that the two modern EMC trials chose **different**
primary endpoints six years apart and that nobody wrote the argument down. That is a fact about *which*
endpoint. It says nothing about the **threshold**, and the threshold is what decides whether a trial
reports a positive result. Neither threshold was recorded anywhere in this repository before this note.

Both were retrievable at zero cost, and both are now in
[`emc-endpoint-alternatives.json`](./emc-endpoint-alternatives.json) → `E1_design_ledger`.

| | pazopanib EMC stratum (NCT02066285, 2019) | IMMUNOSARC II EMC cohort (NCT03277924, 2025) |
|---|---|---|
| primary endpoint | objective response, RECIST 1.1 | 6-month progression-free rate, RECIST 1.1 |
| design | Simon optimal two-stage | threshold only; the master trial's stage 1 used a one-arm one-stage Brookmeyer–Crowley-like survival design |
| H0 / H1 | 0.05 / 0.25 | 0.50 / 0.80 |
| α / β | 0.10 / 0.10 | 0.05 / 0.10 |
| decision rule | ≥ 3 responses of 24 | ≥ 15 progression-free of 22 |
| observed | 4 of 22 | 16 of 23 |
| **stated justification for the null** | **"having considered the very scarce published information on response rate"** — in the registry record | **none, anywhere** |

⭐ **The asymmetry is the point.** A null justified by the *absence* of data is auditable: you can
read the sentence and disagree with it. A null stated as a number and attributed to nothing cannot be
argued with, and it is the one carrying a field's conclusion forward. The 2025 cohort has no full
paper, ClinicalTrials.gov posts no results for it, and the registry's outcome-measure text defines
the endpoint without stating a threshold.

⚠ **One protocol, one drug, two strata, two different response criteria.** The same 2019 trial
designed its solitary-fibrous-tumour stratum on **Choi** criteria with a 40% null — *"having
considered the published response rate based on Choi criteria in SFT patients which correspond to 40%
in monotherapy"* — and its EMC stratum on **RECIST** with a 5% null. Both strata received the same
antiangiogenic agent, which is the setting Choi was developed for. No rationale for reading EMC by
RECIST rather than by Choi appears in the registry record or in the published EMC paper.

⚠ **The registry is ambiguous about whether Choi was registered for EMC at all, so this note does not
claim it was.** The primary-outcome text names both criteria without assigning either — *"measured
using Choi and RECIST 1.1 criteria"* — while the brief summary assigns them with the word
*"respectively"* (SFT → Choi, EMC → RECIST) and the detailed statistical design powers the EMC
stratum on RECIST. The defensible statement is narrower and is enough: **the same protocol judged its
other stratum, on the same drug, by Choi**, and the EMC scans a Choi read would use were taken.

---

## 2 · The EMC 6-month progression-free ladder

`E2_emc_six_month_progression_free_ladder`. Five cohorts, ordered:

| cohort | year | regimen | 6-month progression-free | basis |
|---|---|---|---|---|
| Drilon | 2008 | cytotoxic chemotherapy | **40.0%** | published Kaplan–Meier rate |
| Stacchiotti (Italian RCN) | 2013 | anthracycline-based | **50.0%** | published rate |
| Chiusole | 2020 | first-line chemotherapy | 63.0% | converted from a 9-month median |
| IMMUNOSARC II | 2025 | sunitinib + nivolumab | **77.0%** | published Kaplan–Meier rate |
| pazopanib | 2019 | pazopanib | 80.3% | converted from a 19-month median |

⭐ **Two of these are published rates and neither was in this repository.** Drilon 2008's own
conclusion reads: *"Although there are biases inherent in retrospective analyses, these data provide
a benchmark for time to disease progression for the study of new agents for the treatment of patients
with this diagnosis."* Stacchiotti 2013 states: *"The median PFS for the entire group was 8 months
(range 2–10), with 50% patients progression-free at 6 months."*

⚠ **This does not contradict `emc-systemic-therapy-pooling.json` → `A6`, and the distinction matters.**
A6 records that 6-month progression-free status is extractable as an **integer count** for exactly one
of nine cohorts. That is true and remains true — neither of these two figures is a count, and
POLICY-evidence §2.1 forbids reconstructing one from a percentage. **A figure can be unpoolable and
still be the best benchmark a disease has.** A6 measured poolability and answered correctly; nobody
had asked the different question of whether a *comparator* existed.

**The one modelling assumption, and its measured error.** Two rows publish a median and no 6-month
rate, so a constant-hazard conversion is unavoidable. Three rows publish *both*, so the assumption is
measured rather than asserted:

| cohort | published median | published 6-month | conversion gives | error |
|---|---|---|---|---|
| Drilon 2008 | 5.2 mo | 40.0% | 44.9% | +4.9 pts |
| Stacchiotti 2013 | 8.0 mo | 50.0% | 59.5% | +9.5 pts |
| IMMUNOSARC II 2025 | 13.2 mo | 77.0% | 73.0% | −4.0 pts |

Accurate to within **9.5 percentage points**, with no consistent direction. Every converted value
here should be read with a ±10-point band. **§3's verdict rests only on published rates.** §4's
conclusion-flipping row is a converted value, so the whole band was tested rather than the point
estimate — see §4.

⛔ **Every row is a treated row.** None is an untreated or observation cohort. This ladder can
calibrate one treatment against another; it cannot calibrate any of them against natural history.

---

## 3 · Where the 50% null came from — settled

`E3_benchmark_provenance`.

**The Van Glabbeke chain is real, and it leads somewhere else.** IMMUNOSARC I — the stage-1 paper of
the *same master protocol*, by the same investigators — states its own threshold and its source
outright: *"In this population, a 5% PFSR was considered not promising, whereas a 15% PFSR was
considered promising"*, and *"This threshold was based on the European Organisation for Research and
Treatment of Cancer (EORTC) recommendation cut-off for activity, in terms of 6-month PFSR, in second
line drugs of advanced STS"*, citing as reference 22 **Van Glabbeke *et al.*, *Eur J Cancer* 2002;
38:543–9; PMID 11872347**. So the framework is demonstrably in use in this trial family.

**But 50% is not a Van Glabbeke value.** Retrieved verbatim from that paper's abstract: in 146
pretreated patients on an active agent the 6-month progression-free rate was **14%**; with inactive
regimens, **8%**; in 1154 non-pretreated patients it ranged from **56% (synovial sarcoma) to 38%
(malignant fibrous histiocytoma)**; in 61 gastrointestinal leiomyosarcomas, **30%**. The paper's own
conclusion: *"for first-line therapy, a 6-month PFR of ≥ 30–56% (depending on histology) can be
considered as a reference value to suggest drug activity."*

- The master trial's cited value is the **second-line cut-off — 14% in Van Glabbeke, used by
  IMMUNOSARC I as 15%** — not 50%. That one-point difference is the trial's own rounding, not an
  inference here: the attribution is the trial's.
- 50% sits inside the *first-line* band of 38–56% but near its top, and the top is synovial sarcoma.
- **H1 = 80% exceeds every 6-month figure in that paper by 24 percentage points**, so it cannot have
  been read off it.
- The abstract names **synovial sarcoma, malignant fibrous histiocytoma and gastrointestinal
  leiomyosarcoma**. It names no indolent histology and it does not name EMC. Whether the 1154
  non-pretreated patients included any EMC **cannot be settled** — the full text is paywalled and was
  not retrieved. The paper itself says the reference is histology-dependent, and the spread across
  the four histologies it does name is 18 points at 6 months.

⭐ **What 50% does match, exactly, is EMC's own chemotherapy figure.** Stacchiotti 2013 published
*50% progression-free at 6 months*, and S. Stacchiotti is first author of that 2013 series and a
co-author of the 2025 abstract. **This is a numerical coincidence plus an author overlap, and it is
recorded as that and not as an attribution** — the abstract states no source, and a full paper or a
protocol would settle it in one sentence. The same pattern completes at the other end: the pazopanib
trial's 19-month median implies a 6-month rate of 80.3%, within a point of H1 = 80%, though that one
rests on the conversion and its ±10-point band.

**Restated as a progression speed**, which is checkable: H0 = 50% at 6 months is a **median
progression-free survival of 6.0 months**; H1 = 80% is **18.6 months**. Four of the five published EMC
medians are longer than 6.0 (8, 9, 13.2, 19) and one is shorter (5.2). H1 is within half a month of
the pazopanib trial's observed 19. **The two hypotheses bracket the EMC literature almost exactly —
H0 at the chemotherapy end, H1 at the tyrosine-kinase-inhibitor end.**

**And the EMC-specific benchmark that existed was not used.** Drilon 2008's 40% is cited in neither
trial's *stated design justification*. ⚠ That is narrower than "neither trial cites Drilon": the 2019
full paper is paywalled and was not retrieved, and may well cite it in its introduction. What is
established is that neither trial's stated null was sourced to it. **And it would have made the null
lower, not higher** — 40% against the 50% used — so on this axis the 2025 design was *conservative*.
That is the opposite of the prior hypothesis, and it is reported as such.

### ⭐ The verdict

- **Is the 50% null an aggressive-histology import?** **No**, on the evidence retrieved.
- **Is it therefore appropriate for EMC?** **No — for a more fundamental reason.** Van Glabbeke's
  values are measured on EORTC trial patients receiving regimens; Drilon's on chemotherapy courses;
  Stacchiotti 2013's on anthracyclines. **No untreated EMC progression rate appears anywhere in the
  retrieved record** (§6 records exactly what was searched, and how far that absence does and does not
  reach). A 6-month progression-free rate benchmarked this way answers *"does this regimen
  keep disease still for longer than the last regimen did"* — a real and useful question — and cannot
  answer *"for longer than nothing does"*, which is the question an indolent tumour forces. The
  endpoint inherits exactly the confound PUB-ENDPOINT §6.1 says it cannot remove, and **changing the
  number does not remove it.**

---

## 4 · How the published record reads under a sourced benchmark

`E4_operating_characteristics`, `E5_conclusion_sensitivity`.

**The 2025 cohort.** Observed 16 of 23 (crude 69.6%, Wilson 95% CI 49.1–84.4%). Published conclusion,
verbatim: *"The combination of sunitinib and nivolumab has shown to be active in advanced
extraskeletal myxoid chondrosarcoma."* One-sided exact binomial *p* for 16/23 against each candidate
null:

| candidate null | source of the null | *p* | significant at 0.05 |
|---|---|---|---|
| 40.0% | Drilon 2008, published EMC rate | 0.0040 | yes |
| 50.0% | Stacchiotti 2013, published EMC rate — **and the null used** | 0.0466 | yes |
| 63.0% | Chiusole 2020, largest EMC chemotherapy series, converted | 0.3374 | **no** |
| 80.3% | pazopanib 2019, converted | 0.9344 | **no** |

⭐ **The margin.** The result clears its null by `0.05 − 0.0466 = 0.0034`. **The largest null it still
clears at α = 0.05 is 50.3%.** Any EMC-specific null above that — including the one implied by the
largest published EMC chemotherapy series — and the same data are not significant.

⚠ **And the flipping row is a converted value, so the whole conversion band was tested, not the point
estimate.** Chiusole's 63% carries a ±10-point band (§2): at its most favourable end, 53%, the
one-sided exact *p* is **0.0821** — still not significant. The band floor already sits above the
50.3% ceiling, so the finding does not depend on the conversion landing on 63%; it depends only on
Chiusole's median being **9 months rather than 6**, which is published.

**What would change:** the word *active*. A single-arm result clearing a null derived from EMC
patients on chemotherapy supports a **comparative** statement — longer disease stability than a
historical chemotherapy comparator — not an activity statement, because the comparator is itself a
treatment. The honest sentence names the comparator.

**What would not change:** the counts. 16 of 23 free of progression at 6 months is what was observed;
so is the 13.2-month median. Nothing here re-analyses a patient.

⛔ **And this is not a claim that the regimen is inactive.** Failing to clear a higher null is not
evidence of absence. The 23-patient Wilson interval spans 49.1–84.4%, which contains most of the
ladder. What the sensitivity shows is that **the evidence base cannot separate the candidate nulls** —
not that one of them is true.

**The 2019 cohort — no change, and it is the cleaner result.** Four RECIST responses in 22 against a
5% null is significant by a wide margin, and an objective response is the one observation in this
disease that natural history struggles to explain (PUB-ENDPOINT §7.2 makes exactly that point). Its
difficulty was never its threshold; it is that its endpoint could only ever describe 4 of the 22
patients enrolled. **What would change is what else it reported:** no Choi read of the EMC stratum
has ever been published, in a protocol that judged its sibling stratum on the same drug by Choi at a
40% null (§1); and no 6-month progression-free rate was printed, although the 12- and 24-month rates
were. Both are readable off scans the trial has already taken.

**A field-level re-reading is not possible.** `D3_reporting_completeness` records a 6-month
progression-free status extractable as an integer count for 1 of 9 cohorts. Adding the two published
rates found here raises the cohorts with *any* 6-month figure from 1 to 3 of 9 — and leaves **6 of 9
with none**. The endpoint the field migrated to is still the one it reports least.

⚠ **A design footnote, not an error.** An exact single-stage binomial design at H0 = 0.50, H1 = 0.80,
α = 0.05, β = 0.10 requires **n = 23 with a threshold of 16**. The trial published "15 out of 22",
whose exact one-sided type I error is **0.0669** — above the stated 0.05. That is not a
miscalculation: the master trial's stage 1 states its sample size came from a Brookmeyer–Crowley-like
**survival** design with non-parametric estimation, and a survival-based design need not land on the
same (n, r) as a binomial one. It is recorded because a reader re-deriving the design from the
abstract's parameters will land on 23/16 and should know why. **The observed result clears both.**

---

## 5 · Which endpoint should be tracked

`E6_endpoint_matrix`. Ten candidates, graded on three criteria fixed before grading: **power at
n ≈ 20–25**, **immunity to the natural-history confound**, and **computability from what is already
published**. Condensed:

| endpoint | power at n≈20 | natural-history immunity | computable from published | patient cost |
|---|---|---|---|---|
| objective response rate | poor (12.8% pooled) | **high** | best: 7 of 9 cohorts | none |
| disease control rate | poor, other direction (89.4%) | **none** | 5 of 9 | none |
| median progression-free survival | moderate, very wide CI | none alone | 3 of 9 (+ Chiusole, §8) | follow-up years |
| **progression-free rate at a fixed timepoint** | **good** | none — only as good as its null | worst: 1 of 9 as a count | none |
| **growth modulation index** | moderate | **highest, and uniquely so** | **0 of 47 patients** | **zero additional patients** |
| tumour growth rate / volumetric | potentially high | high *if* a pre-treatment rate exists | no | zero patients; prospective imaging |
| time to next treatment | moderate | low — measures clinician discretion | no; **18 of 25 retrieved records are indolent lymphoid malignancies, 0 sarcoma** | zero patients |
| duration of response | useless as primary (6 events in 47) | high, on six patients | no | zero patients |
| Choi rather than RECIST | better than RECIST for antiangiogenics | same as RECIST | **no — and most recoverable** | **zero** |
| randomized discontinuation design | not achievable at this accrual | **complete** | n/a | **highest by far** |

### ⭐ The recommendation

**No single endpoint satisfies all three criteria, and saying otherwise would be the error
PUB-ENDPOINT criticises.** The recommendation is a pair, because the two halves fix different
failures and neither costs a patient.

1. **Primary: keep the 6-month progression-free rate — and require its null to be sourced in print.**
   It is the only endpoint whose event rate sits where a 20-patient binomial design has information.
   Two EMC-specific published figures exist to source it to: 40% (Drilon 2008) and 50% (Stacchiotti
   2013). A trial that states which it used, and why, can be argued with. **Cost: zero patients. It is
   a sentence.**
2. **Co-primary or mandatory secondary: the growth modulation index** (TTP on study ÷ TTP on the
   immediately preceding line; conventionally a benefit at ≥ 1.33). It is the **only** candidate that
   carries its own control inside each patient — a patient whose disease is intrinsically slow
   contributes a long TTP1 as well as a long TTP2, and the ratio is unmoved. It is the only option on
   the list that **attacks** PUB-ENDPOINT §6.1 rather than inheriting it. **Cost: zero additional
   patients**, and one extra date per patient. The design it operationalises is published (Mick *et
   al.*, PMID 10913809) and so is sample-size methodology for it as a primary endpoint (PMID
   30458583), so "nobody knows how to power this" is not available as an objection.
3. **Free, immediate, unilateral: publish a Choi read and the 6-month progression-free count for the
   2019 EMC stratum.** Both are readable off scans a completed trial has already taken, and its own
   protocol judged the sibling stratum by Choi.

**Explicitly not recommended.** The **randomized discontinuation design** is the only complete answer
— it was invented for precisely this problem, in Rosner *et al.*'s words: *"An appropriate design has
to distinguish antiproliferative activity attributable to the novel agent from indolent disease"*
(PMID 12431972) — and it is **unaffordable at this disease's accrual**, and is additionally known to
be less efficient than upfront randomisation under some growth models (PMID 15983399). **Naming a
design is not proposing it**; PUB-ENDPOINT §7.3 already said so. **Time to next treatment** is not
recommended as a primary in EMC specifically, because in an indolent tumour clinician discretion
about when to start the next line is exactly the noise it cannot separate — and its published home is
elsewhere: a Europe PMC title search returned 26 records, of the 25 returned **18 are titled in an
indolent lymphoid malignancy and none in any sarcoma**. Those are diseases with published
treatment-initiation criteria, which is what turns that discretion into a rule. ⚠ *That last clause
is a judgement, not a retrieval — no search here established the absence of EMC treatment-initiation
criteria.*

⛔ **None of this is a treatment recommendation.** The choice of endpoint has no bearing on which
treatment a person with EMC should receive, which belongs with a specialist sarcoma centre.

---

## 6 · What is missing — the recommendation's own blocker

`E7_growth_modulation_index_data_availability`.

The index needs two dated intervals per patient, neither of which may be a cohort median.

| | count |
|---|---|
| prospective-trial EMC patients ever evaluated for response | 47 |
| with a published **per-patient** time to progression on study | **2** |
| with a published per-patient time to progression on the **prior line** | **0** |
| cohorts publishing any per-patient time to progression | 1 of 9 |
| cohorts publishing prior-line time to progression | **0 of 9** |

⭐ **The growth modulation index is computable for zero EMC patients.** Exactly one of the nine
curated cohorts prints a per-patient time to progression — the trabectedin sub-analysis's Table 2,
giving 13.0 and 7.4 months for its two EMC subjects. **None of the nine gives any patient's time to
progression on their previous line**, and that is derived rather than asserted: the producer scans
every field of every committed cohort row for one and returns nothing, so the count moves on its own
if such a field is ever added.

⚠ **Scope: the curated corpus** — every systemic-therapy report this repository has found for EMC.
It is a reading of nine reports, not a proof about a literature nobody has fully enumerated. That
does not soften the conclusion: one unfound report would move the count from 0 to a handful, and a
handful of paired intervals is still not an analysis.

**The near misses make it sharper.** The 2025 abstract reports that 6 of 23 patients had a prior
antiangiogenic and compares that subgroup's median progression-free survival on study (7 months
versus 13) — so the trial holds the prior-line information *at patient level*, stratified on it, and
published a group median instead of the paired intervals. The 2019 trial required RECIST progression
in the previous 6 months as an entry criterion, so the date of the previous progression was recorded
by protocol for every enrolled patient. **The data exists and has been collected. It has not been
printed.** That is a reporting failure, not a measurement one — the same shape PUB-ENDPOINT §4.2 found
for the endpoint counts.

### ⭐ The minimal ask

**Four dates per patient**, anonymised: start of the immediately preceding systemic line, progression
on it, start of study treatment, progression on study or censoring. No new patient, no new scan.
Suppliers: the Spanish, Italian, French and UK sarcoma networks that appear on both papers.

- **Upper bound: 45 patients** (22 evaluable in 2019 + 23 in 2025).
- **Realistic bound: fewer** — the index is undefined for a treatment-naive patient, and 13 of 24 in
  the 2025 cohort were treatment-naive, so at most 11 of that cohort could contribute.
- ⚠ **The two cohorts are not independent** (PUB-ENDPOINT §6.5). For a growth modulation index that
  is not a contamination — it is the ideal case, a patient whose TTP1 is another trial's *measured*
  endpoint — but it must be declared.
- ⭐ **And the overlap can only run one way, which makes it cleaner still.** The 2019 trial's
  Exclusion Criteria, read from the ClinicalTrials.gov v2 record fetched for this note, contain
  verbatim: *"Patients who have received previous antiangiogenic agents."* A patient who had already
  had an antiangiogenic could not enter the 2019 trial, while nothing stops a 2019 patient from later
  entering the 2025 cohort — where they would be one of the 6 of 23 recorded as previously
  antiangiogenic-treated. So **TTP1 for those patients would be a protocol-measured endpoint of a
  published trial**, not a date recovered from notes. ⚠ **This is the protocol's rule, not a
  patient-level audit** — registries publish eligibility criteria, not enrolment decisions. The honest
  form is *"the trial's own criterion excludes it"*, never *"no patient appeared in both"*. Same
  criterion, independently corroborated on the EU Clinical Trials Register for EudraCT 2013-005456-15
  by a sibling retrieval the same day (`partner-event-counts-2026-08-08.md` §3).

**What it would be powered against.** The only sarcoma-wide reference proportions retrieved: 69 of 227
(French Sarcoma Group, PMID 23904460) and 118 of 357 (GEISTRA, PMID 33672857) exceeded an index of
1.33. Pooled under POLICY-evidence §2.2: **187 of 584 = 32.0% (Wilson 95% CI 28.4–35.9%)**. ⚠ Neither
series states an EMC patient, so **this is not an EMC figure** — it is the reference a first-ever EMC
index design would have to use in the absence of anything closer, and **it is a treated reference
too**. What the index fixes is the *within-patient* confound; it does not by itself supply an
untreated comparator.

⛔ **This section does not predict what such an analysis would show, in either direction.** It claims
only that the quantity is uncomputable today and that four dates per patient would make it
computable.

### What no amount of reporting supplies

`E9_the_natural_history_gap`. **No fixed-timepoint progression rate for advanced EMC patients
receiving no systemic therapy was retrieved.** ⚠ That is a measured absence across three Europe PMC
searches (`epmc_emc_untreated_metastases`, `epmc_emc_indolent_naturalhistory`,
`epmc_emc_time_to_metastasis`, top 25 relevance-ranked hits each) plus the nine curated EMC
systemic-therapy cohort rows — **not a proof that no such figure exists anywhere**, and the
distinction is the one CLAUDE.md §4 insists on. The nearest retrieved item is a single 2025 case
report of spontaneous regression of lung metastases
after palliative surgery in a heavily pre-treated patient (PMID 41321774) — **n = 1, after surgery, so
not even a clean observation of untreated behaviour.** It is recorded because it is the whole of the
direct evidence that metastatic EMC can regress without systemic therapy, and because "the field's
single documented instance is a case report" is itself the measurement of how empty this space is. It
supports no rate, no null and no design.

For context, the disease's indolence, verbatim from the 2025 review (PMID 41055792): *"The median time
to metastasis is approximately 28 months. Overall survival (OS) reflects the typically indolent yet
metastatic course: 5-year OS 66–88%, and 10-year disease-specific survival approximately 85%."*

### The confound has been measured once — in a different disease

`E10_indolent_tumour_placebo_calibration`.

⛔ **Desmoid fibromatosis is not EMC and no number in this subsection may be used as an EMC rate.**
Desmoid is locally aggressive and does not metastasise; EMC metastasises in 35–45% of patients. Their
untreated behaviours are not interchangeable. This is here to settle a different question: **is the
natural-history confound hypothetical, or has anyone ever measured it in an indolent soft-tissue
tumour?**

**Randomised, double-blind, placebo-controlled** — Gounder 2018 (PMID 30575484), 87 patients with
progressive, symptomatic or recurrent desmoid, verbatim: *"the 2-year progression-free survival rate
was 81% (95% CI, 69 to 96) in the sorafenib group and **36% (95% CI, 22 to 57) in the placebo
group**… Before crossover, the objective response rate was 33% (95% CI, 20 to 48) in the sorafenib
group and **20% (95% CI, 8 to 38) in the placebo group**."*

- **A fixed-timepoint progression-free rate has a large placebo component.** 36% at 2 years on
  nothing — in a population enrolled *for progressive disease*, the very design feature PUB-ENDPOINT
  §6.1 names as what bounds the confound. It bounds it; it does not remove it. Benchmarked against a
  historical treated cohort, 36% and 81% would have been indistinguishable.
- ⚠ **And so does objective response, which qualifies a claim this repository makes.**
  **One patient in five responded to placebo.** PUB-ENDPOINT §7.2 argues a response is *"hard to
  explain by natural history"*. This measurement shows that is **disease-specific, not general**.
  ⛔ **It does not refute §7.2 for EMC** — spontaneous regression is well-documented desmoid biology,
  whereas the whole retrieved EMC evidence for it is one 2025 case report. What it does is turn
  "responses are hard to explain by natural history" from a principle into a claim that must be
  argued per disease — and in EMC it has not been.

**Untreated observation cohort** — the only one retrieved for any indolent soft-tissue tumour
(PMID 42052362, Singapore, 1999–2023): *"At one-year, progressive disease was observed in 5 out of 19
patients (26.3%) on active surveillance"* → **14 of 19 = 73.7% progression-free at 12 months, Wilson
95% CI 51.2–88.2%.** ⚠ n = 19, retrospective, single centre, different disease, and an
active-surveillance population is *selected* for expected indolence. It is quoted because **EMC has
no equivalent, not even a biased one.**

⭐ **What this licenses:** the natural-history confound is not a theoretical worry. The one time
anyone measured the placebo component of these endpoints in an indolent soft-tissue tumour, it was
large enough to account for a substantial part of a single-arm result. **That is the strongest
argument for the growth modulation index** — the only recommended change that measures that component
per patient instead of assuming it away.

---

## 7 · What each change costs, in patients

`E8_patient_cost`. Exact single-stage single-arm binomial designs, one-sided α = 0.05.

| scenario | H0 / H1 | n at 90% power | n at 80% power |
|---|---|---|---|
| the 2025 design as published | 0.50 / 0.80 | 23 (≥16) | 18 (≥13) |
| null sourced to Drilon 2008 | 0.40 / 0.80 | 13 (≥9) | 11 (≥8) |
| null sourced to Chiusole 2020, converted | 0.63 / 0.85 | 36 (≥28) | 26 (≥21) |
| null at the pazopanib-implied rate | 0.803 / 0.92 | 77 (≥68) | 58 (≥52) |
| growth-modulation-index proportion vs the sarcoma reference | 0.32 / 0.60 | 29 (≥14) | 19 (≥10) |

The two modern EMC cohorts accrued 26 and 24 patients over 2014–2017 and 2020–2024 respectively across
9–11 European centres, so **an n above roughly 30 is a decade of international accrual**.

⭐ **Raising the null from 50% to 63% takes the trial from 23 to 36 patients at 90% power — a factor
of 1.57.** Asking whether a new regimen beats the pazopanib result costs **77**, three times what the
disease has ever accrued into one cohort. **That is why the recommendation is not "raise the null":
at this accrual, that factor means not running the trial.** The benchmark has to be fixed by making it
*auditable* and by adding a *within-patient control*, not by making the bar higher. The three changes
recommended in §5 all cost zero patients.

---

## 8 · A correction owed to a source artifact

`corrections_owed_to_the_source_file`. Recorded here, dated, with its evidence; **fixed in the file
that owns the sentence**, per CLAUDE.md rule 1.2 and the pattern set by `D5`.

**C1 — Chiusole 2020 does report a median progression-free survival.**
`emc-systemic-therapy-pooling.json` → `analyses.A5_time_to_event_never_pooled` states *"Chiusole 2020
reports no median PFS for its chemotherapy patients."* That paper's Results say: *"Median
progression-free survival for patients receiving first-line chemotherapy was 9 months"*, and its
Discussion repeats it while comparing itself to Drilon (5.2), Stacchiotti (8) and pazopanib (19).
Evidence: `literature/emc-endpoint-benchmarks-r2/epmc_ft_chiusole_PMC7308468.txt`, HTTP 200.

⚠ **The correction that row actually carries — that 5.2 months belongs to Drilon 2008 and not to
Chiusole — is CORRECT and stands.** What is falsified is the extra sentence appended to it. A **fourth**
EMC-specific median progression-free survival exists and this repository recorded that it did not.
This matters here because Chiusole's 9-month median is the candidate null under which the 2025
cohort's result stops being significant (§4) — a finding resting on a number the source file says
does not exist would be worthless, which is why it was checked against the full text before use.
**Correction owed to:** `emc-systemic-therapy-pooling.json`.

**C2 — not a defect, an addition.** `A6` correctly answers the *poolability* question. What no
artifact recorded is that two EMC cohorts publish a 6-month progression-free **rate** without a count.
Its home is this note's §2.

---

## 9 · Limitations

1. **The provenance of H0 = 50% is circumstantial.** An exact numerical match with the only published
   EMC figure equal to 50%, by an author common to both papers, is strong circumstantial evidence and
   is not proof. The abstract states no source. A full paper or a protocol settles it in one sentence.
2. **Van Glabbeke's full text was not retrieved.** Whether its 1154 non-pretreated patients contained
   any EMC is unsettled and is stated as unsettled everywhere it matters.
3. **Two rungs of the ladder are conversions** under a constant hazard, carrying a measured ±10-point
   band. The pazopanib cohort's own published points argue the hazard is *not* constant. Neither §3's
   verdict nor §4's headline turns on a converted value.
4. **Every EMC benchmark discussed is measured on treated patients**, including the
   growth-modulation-index reference proportion. The natural-history question is bounded here, not
   closed.
4b. **The §6 desmoid calibration is a different disease** and is used only as an existence proof
   about endpoints. None of its numbers is transferable to EMC, in either direction, and none is used
   as a null anywhere in this work.
5. **The 2025 cohort is a conference abstract** with no full paper, no posted results, and two
   internal inconsistencies already documented in `emc-systemic-therapy-pooling.json`. Every statement
   about its design rests on four sentences.
6. **"Neither trial cites Drilon 2008" is not what is established** — only that neither trial's
   *stated design justification* uses it. The 2019 full paper is paywalled and was not retrieved.
7. **The endpoint matrix's grades are judgements**, not measurements, on two of three criteria. Only
   *computability from published data* is computed, from the committed census.

---

## 10 · What this note does not claim

- ⛔ No efficacy, potency, dose, schedule, safety, selectivity, therapeutic-window or clinical-readiness
  claim for any agent in EMC. None is supported by anything here.
- ⛔ No treatment recommendation, including a negative one.
- ⛔ No claim that any trial was wrongly conducted, that any published conclusion is false, or that any
  investigator erred. A null with no stated source is a **reporting** gap, and single-arm trials with
  investigator-chosen thresholds are the normal and accepted way to study an ultra-rare disease.
- ⛔ No re-analysis of any patient. Every count used is the count its trial published.
- ⛔ No prediction about what a growth modulation index computed on these patients would show.
- ⛔ No claim that the 6-month progression-free rate is the *right* endpoint in an absolute sense —
  only that it is the best-powered available one and that its null has never been sourced in print.
