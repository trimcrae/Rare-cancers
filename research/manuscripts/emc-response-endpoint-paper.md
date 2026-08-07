---
id: DOC-EMC-RESPONSE-ENDPOINT-PAPER
title: "Objective response is the wrong endpoint for extraskeletal myxoid chondrosarcoma: the same 47 patients, read two ways"
level: L3
kind: manuscript
status: live
canonical_for:
  - the endpoint discordance between objective response and disease control in advanced EMC
  - the endpoint-reporting completeness census of the published EMC systemic-therapy literature
purpose: >-
  Show, on the identical patients, how far apart the objective-response and disease-control readings
  of advanced-EMC systemic therapy sit; state exactly what that gap can and cannot mean; and set out
  what each endpoint costs a single-arm trial of the size this disease can actually accrue.
scope: >-
  Published systemic-therapy outcomes in advanced extraskeletal myxoid chondrosarcoma, as already
  extracted and cited in this repository's clinical registry and its systemic-therapy pooling
  artifact. It is a paper about MEASUREMENT. It contains no new patient, no new study, no
  laboratory or computational result about any drug, and no statement that any agent works.
audience: [external reviewers, collaborators, maintainers, autonomous research agents]
date: 2026-08-07
last_verified: 2026-08-07
related: [DOC-POLICY-EVIDENCE, DOC-EMC-TREATMENT-STRATEGY, DOC-EMC-FUSION-PARTNER-STRATIFICATION]
---

# Objective response is the wrong endpoint for extraskeletal myxoid chondrosarcoma: the same 47 patients, read two ways

> ## ⛔ WHAT THIS PAPER IS, AND WHAT IT IS NOT
>
> **It is an argument about an ENDPOINT.** It compares two ways of reading outcomes that have
> already been published, over patients who have already been counted, using the pooling method this
> repository's evidence contract fixes in advance
> ([`systems/POLICY-evidence.md`](../../systems/POLICY-evidence.md) §2.1–2.4).
>
> ⛔ **It is NOT a claim that any drug works in this disease.** It asserts no efficacy, no potency,
> no dose, no safety, no therapeutic window and no clinical readiness for pazopanib, sunitinib,
> nivolumab, trabectedin, apatinib, anthracyclines or anything else. A difference between two
> endpoints is a fact about measurement; it is never evidence that a treatment did something.
> ⛔ **It makes no treatment recommendation, including a negative one**, and it does not rank agents.
>
> ⚠ **Its own central finding has a confound the paper cannot remove, and that confound is stated in
> the abstract rather than in the limitations.** The endpoint that looks larger here — disease
> control — counts stable disease as an event, and in a tumour this indolent an unknown share of
> those stable diseases would have been stable without treatment. No randomised comparison in this
> disease exists that could size it. §6 is where that argument is made against this paper, at its
> full strength, rather than deflected.
>
> **Producers.** Every figure below is derived, not typed:
> [`emc_endpoint_discordance.py`](./emc_endpoint_discordance.py) →
> [`emc-endpoint-discordance.json`](./emc-endpoint-discordance.json), which reads the integer counts
> owned by [`emc-systemic-therapy-pooling.json`](./emc-systemic-therapy-pooling.json) and re-derives
> them offline. `--check` reproduces the artifact byte for byte. **$0 — CPU only, no GPU, no rental.**

---

## Abstract

**Background.** Extraskeletal myxoid chondrosarcoma (EMC) is an ultra-rare translocation sarcoma
driven by an *NR4A3* rearrangement and characterised throughout its own literature as indolent. Its
systemic-therapy record is habitually summarised by the objective-response rate. That endpoint keeps
only tumour shrinkage, which is the category an indolent tumour is least likely to enter — and what
it costs in this disease has not been quantified, because no publication combines the trials that
would be needed to do so.

**Methods.** We took every advanced-EMC patient ever evaluated for response inside a prospective
trial with protocol-defined assessment — three cohorts, one per trial — and read the same patients
twice: once as objective response (complete or partial response) and once as disease control
(complete response, partial response or stable disease as best response). Pooling is crude
denominator-weighted proportions with Wilson score 95% intervals over explicit integer counts, per
[`systems/POLICY-evidence.md`](../../systems/POLICY-evidence.md) §2.1–2.4. No count is reconstructed
from a published percentage; no time-to-event figure is merged. We then audited how completely each
endpoint is reported across the whole published EMC systemic-therapy literature, and computed what
each endpoint's event rate does to a single-arm trial of the size this disease can accrue.

**Results.** Over the identical 47 patients, objective response was **12.8 %** (6/47, Wilson 95 % CI
6.0–25.2) and disease control **89.4 %** (42/47, 95 % CI 77.4–95.4) — a gap of **76.6 percentage
points**, a ratio of **7.0**. The whole of that gap is **36 of 47 patients (76.6 %, 95 % CI
62.8–86.4)** whose best response was stable disease: counted as non-responders by one endpoint and
as events by the other. An objective-response readout sees 6 of the 42 recorded disease-control
events and cannot represent the other **36 (85.7 %)**. Reporting is the mirror image of what the
argument needs: across the **9** published EMC systemic-therapy cohorts, objective-response counts
are extractable for **7**, disease-control counts for **5**, an EMC-specific median progression-free
survival for **3**, and a 6-month progression-free count for **1**. At the pooled response rate, a
single-arm trial of 20 patients would expect **2.6** responses and has a **6.5 %** chance of
observing none at all; at the interval's lower bound that chance is **29 %**. **17** patients are
needed for a 90 % chance of one response at the point estimate, **38** at the lower bound — against
the 22 and 23 that the two modern prospective EMC cohorts actually accrued, over three and four
years respectively.

**Conclusions.** In EMC the objective-response rate discards the majority of what its own trials
recorded, and at achievable sample sizes it returns a result that is uninterpretable rather than
negative a substantial fraction of the time. **This does not make disease control the right endpoint
instead**: at 89.4 % it is close to its ceiling, it has no comparator in this disease, and stable
disease in an indolent tumour may be natural history. What the record supports is narrower and
firmer — that a small EMC trial reported only as an objective-response rate is being asked a
question its sample size cannot answer, and that the per-category counts which would let any reader
compute either endpoint are absent from most of this literature. The second half costs nothing to
fix.

---

## 1 · Introduction

### 1.1 The disease

Extraskeletal myxoid chondrosarcoma is a translocation sarcoma defined by rearrangement of *NR4A3*,
most often as *EWSR1::NR4A3*. It is ultra-rare, and it is slow. This repository's own pooled reading
of its outcome literature — a random-effects (DerSimonian–Laird) meta-analysis over the pooled
cohorts of the cited EMC clinical registry, whose one home is
[`research/meta/results.json`](../meta/results.json), produced by
[`research/meta/meta-analysis.mjs`](../meta/meta-analysis.mjs) — reads:

| outcome | pooled | 95 % CI | I² | k | contributing cohorts |
|---|---|---|---|---|---|
| local recurrence | 27.8 % | 14.2–47.3 | 90 % | 4 | Masunaga 2025, Meis-Kindblom 1999, US Sarcoma Collaborative 2022, Chiusole 2020 |
| distant metastasis | 37.9 % | 27.5–49.6 | 69 % | 3 | Masunaga 2025, Meis-Kindblom 1999, Chiusole 2020 |
| disease-specific death | 14.2 % | 8.5–22.6 | 62 % | 2 | Masunaga 2025, Meis-Kindblom 1999 |

⚠ **Those three figures use a different pooling method from everything else in this paper, and the
distinction is not cosmetic.** [`POLICY-evidence`](../../systems/POLICY-evidence.md) §2 records that
two methods coexist here — random-effects (DerSimonian–Laird) for the registry meta-analysis, and
crude denominator-weighted proportions with Wilson intervals for simple proportions — and that
quoting one where the other is meant is a real error. The table above is the first; §2 onward is the
second. They are never combined.

Read as an indolence statement rather than as a prognosis, the shape is what matters: **the
distant-metastasis rate sits far above the disease-specific death rate, and the two intervals do not
overlap.** ⚠ **The three rows rest on partly different study sets and different follow-up, so this is
a description of the literature's shape and not a within-cohort comparison** — the death row is two
cohorts, the metastasis row three, and within a shared source the two metrics are computed over
different strata. It is stated as a qualitative direction for that reason, and it is not a survival
model, not risk-adjusted, and not a prognosis for any individual. A tumour with that profile is one
in which the interesting quantity is how long the disease stays where it is.

### 1.2 The endpoint

The objective-response rate — the proportion of patients whose tumour shrinks by a criterion amount —
is the reflex summary of a systemic-therapy record. It carries real advantages: it is early, it is
per-patient, it needs no control arm, and it is comparable across diseases. Those advantages are why
it became the default, and none of them is in dispute here.

⭐ **Nor is this an argument against RECIST, which never asked to be used this way.** The RECIST 1.1
guideline opens by naming *two* endpoints, not one: *"both tumour shrinkage (objective response) and
disease progression are useful endpoints in clinical trials"* (Eisenhauer *et al.*, *Eur J Cancer*
2009; PMID 19097774; doi 10.1016/j.ejca.2008.10.026). The criteria supply both categories. What this
paper is about is a **field-level habit of summarising by the first and discarding the second** — and
§3 measures what that habit costs in this particular disease.

Its cost is that it is a *categorical* reading of a *continuous* observation, and the category it
keeps is the one an indolent tumour is least likely to enter. Every patient whose disease neither
shrank nor grew is scored identically to a patient whose disease grew through treatment. In a rapidly
progressive tumour that collapse loses little, because untreated stability is rare. In EMC it is not
rare, and the question of how much is lost has never been asked with the numbers in front of it.

### 1.3 What this paper adds

Two things, both small and both checkable.

1. **The size of the gap, on one patient set.** The pooled objective-response and disease-control
   rates in advanced EMC each exist in this repository already
   ([`emc-systemic-therapy-pooling.json`](./emc-systemic-therapy-pooling.json) → `analyses.A1_*` and
   `analyses.A4_*`, which own them). What did not exist is the two placed on the *same denominator*,
   with the discordant patients named and counted, and with the arithmetic consequence for a trial of
   achievable size worked through. No publication states the gap, because no publication combines
   these three trials.
2. **A completeness census of the literature, not of the disease.** Choosing a better endpoint is
   worth nothing if the reports do not carry the counts to compute it. §5 measures that, and it is
   the finding with the cheapest remedy.

⭐ **Neither is a landmark result and this paper does not claim novelty beyond arithmetic.** The
underlying observations are all published; what is new is putting them on one denominator and saying
what follows.

---

## 2 · Methods

### 2.1 Data source

Every count in this paper comes from
[`research/manuscripts/emc-systemic-therapy-pooling.json`](./emc-systemic-therapy-pooling.json),
this repository's pooled synthesis of published systemic-therapy outcomes in advanced EMC. That file
owns the extraction: each cohort row carries the verbatim quote the counts were read from, its
citation with at least one resolvable identifier, its design tier, and — where one exists — the
correction it carries against a figure in circulation. It in turn sits beside the cited EMC clinical
registry, [`research/data/emc-clinical-registry.json`](../data/emc-clinical-registry.json), whose
evidence contract is enforced by [`scripts/validate-registry.mjs`](../../scripts/validate-registry.mjs)
as gate 5 of [`scripts/preflight.sh`](../../scripts/preflight.sh).

No new literature search was performed for this paper and no count was re-extracted from a source
document. That is deliberate: the extraction and this analysis are separate acts with separate
failure modes, and re-typing a count is how a transcription error enters a second file.

### 2.2 Endpoint definitions

- **Objective response** — complete or partial response as best response, by the response criterion
  the reporting trial used (RECIST 1.1 in the two modern prospective cohorts, with central review;
  Eisenhauer *et al.*, *Eur J Cancer* 2009; PMID 19097774; doi 10.1016/j.ejca.2008.10.026 —
  retrieved and its identifiers cross-checked from a GitHub Actions runner via Europe PMC on
  2026-08-07 at 4:06 PM ET, with the PMID carried as a known-positive control on the query, because
  the development sandbox's egress proxy refuses these hosts and a citation written from memory is
  the failure this repository's evidence rules exist to prevent).
- **Disease control** — complete response, partial response *or stable disease* as best response.
- **Discordant patients** — best response stable disease. These are the entire difference between the
  two endpoints: scored as failures by the first and as events by the second.

### 2.3 The patient set

Three cohorts, comprising every advanced-EMC patient ever evaluated for response inside a prospective
trial with protocol-defined assessment. The membership is the source file's judgement, recorded there
with its reasons (`analyses.A1_*.why_these_three_may_be_pooled`); this paper's producer script asserts
that its list still equals the source's, so the two cannot drift apart silently.

| cohort | regimen | design | n evaluable | ref |
|---|---|---|---|---|
| `pazopanib_phase2` | pazopanib 800 mg/day | single-arm phase 2, central molecular confirmation, 11 sites of the Spanish/Italian/French sarcoma groups, accrued 2014–2017 | 22 | Stacchiotti *et al.*, *Lancet Oncol* 2019;20:1252–62; PMID 31331701; doi 10.1016/S1470-2045(19)30319-5; NCT02066285 |
| `sunitinib_nivolumab_immunosarc2` | sunitinib + nivolumab | phase 2 histology-specific cohort inside the IMMUNOSARC II master trial, central pathology, 9 centres in Spain/Italy/UK, accrued 2020–2024. **Conference abstract only** | 23 | Hindi *et al.*, *J Clin Oncol* 2025;43(16_suppl):11513; doi 10.1200/JCO.2025.43.16_suppl.11513; NCT03277924 |
| `trabectedin_emc_subset` | trabectedin 1.5 mg/m² q3w | EMC subset of the trabectedin arm of a randomised phase 2 trial in translocation-related sarcoma, central radiology review | 2 | Morioka *et al.*, *BMC Cancer* 2016; PMID 27418251; PMC4946242; doi 10.1186/s12885-016-2511-y; JapicCTI-121850 |

Retrospective and named-patient series are used only in §5's completeness census, never in the
pooled comparison: Stacchiotti *et al.*, *Eur J Cancer* 2014;50:1657–64 (doi
10.1016/j.ejca.2014.03.013); Stacchiotti *et al.*, *Clin Sarcoma Res* 2013;3:16 (PMID 24345066;
PMC3879193; doi 10.1186/2045-3329-3-16); Drilon *et al.*, *Cancer* 2008 (PMID 18951519; PMC2779719;
doi 10.1002/cncr.23978); Xie *et al.*, *Cancer Manag Res* 2020 (PMID 32547189; PMC7237692; doi
10.2147/CMAR.S253201); Chiusole *et al.*, *Front Oncol* 2020 (PMID 32612944; PMC7308468; doi
10.3389/fonc.2020.00828); Martin-Broto *et al.*, *J Immunother Cancer* 2020 (PMID 33203665;
PMC7674086; doi 10.1136/jitc-2020-001561).

### 2.4 Pooling method

Fixed in advance by [`systems/POLICY-evidence.md`](../../systems/POLICY-evidence.md) §2.1–2.4 and not
varied for this analysis:

- **crude denominator-weighted proportions** — p̂ = Σevents / Σdenominators;
- **Wilson score 95 % intervals**, chosen because they behave at small *n* and near 0 %/100 %, which
  is the entire regime this paper works in;
- **explicit integer {events, denominator} pairs only** — never a count back-derived from a published
  percentage, because rounding invents data;
- **non-overlapping populations only**, each exclusion recorded with its reason;
- **time-to-event endpoints are never merged**; they are carried per row (§4.3);
- **heterogeneity is reported as the per-cohort spread**, not as I², so the signal is how much the
  studies disagree rather than a single index.

The two endpoints are computed over the identical denominator, and the producer script asserts that
identity rather than assuming it — if the two ever ceased to be the same patients, the comparison
would be between populations and the paper's argument would be void.

### 2.5 Reproduction

```
python3 research/manuscripts/emc_endpoint_discordance.py           # regenerate
python3 research/manuscripts/emc_endpoint_discordance.py --check   # verify committed artifact
```

The script re-derives the source file's own pooled objective-response and disease-control figures
from the same cohort rows and **refuses to write if they disagree** — a parity check, so that the
discordance figures are provably about the same object as the numbers they are compared with. It
does not become a second home for those two pooled proportions; the source file owns them.

---

## 3 · Results — the same patients, read twice

**One home: [`emc-endpoint-discordance.json`](./emc-endpoint-discordance.json) →
`D1_same_patients_two_endpoints`.**

| reading | events / n | proportion | Wilson 95 % CI |
|---|---|---|---|
| **objective response** | 6 / 47 | **12.8 %** | 6.0 – 25.2 |
| **disease control** | 42 / 47 | **89.4 %** | 77.4 – 95.4 |
| **discordant — stable disease as best response** | 36 / 47 | **76.6 %** | 62.8 – 86.4 |

**Gap: 76.6 percentage points. Ratio: 7.0.**

Per cohort, with the same patients in both columns:

| cohort | n | objective response | stable disease | progressive disease | disease control | gap (pp) |
|---|---|---|---|---|---|---|
| pazopanib | 22 | 4 (18.2 %) | 16 | 2 | 20 (90.9 %) | 72.7 |
| sunitinib + nivolumab | 23 | 2 (8.7 %) | 18 | 2 | 20 (87.0 %) | 78.3 |
| trabectedin (EMC subset) | 2 | 0 (0 %) | 2 | 0 | 2 (100 %) | 100.0 |

The gap is not an artefact of one cohort. It is present in every cohort, in the same direction, and
its smallest value is 72.7 percentage points.

**The discordant count is derived two independent ways and required to agree**: as the sum of the
reported stable-disease counts (16 + 18 + 2 = 36) and as disease control minus objective response
(42 − 6 = 36). A transcription error in either extraction would break the identity and fail the
build.

### 3.1 What an objective-response reading cannot see

**One home: `D2_share_invisible_to_objective_response`.**

Of the 42 recorded disease-control events, an objective-response readout sees **6**. The other
**36 — 85.7 %** — are discarded by construction, not by judgement: the endpoint has no category for
them.

⚠ **This is a statement about representation, not about drug effect.** It measures how much of the
recorded observation one endpoint cannot express. Whether that observation means anything is the
separate and unresolved question of §6.

### 3.2 The one sensitivity that moves anything

**One home: `D1_…sensitivity_immunosarc2_denominator_22`.**

The IMMUNOSARC II EMC cohort reports 23 response-evaluable patients, and its own best-response
categories sum to 22 (2 partial responses + 18 stable + 2 progressive). One patient is unaccounted
for; the abstract does not reconcile it and no full paper exists to check against. Recomputing with
that cohort's denominator set to 22:

| | as reported (n = 47) | sensitivity (n = 46) |
|---|---|---|
| objective response | 12.8 % (6.0–25.2) | 13.0 % (6.1–25.7) |
| disease control | 89.4 % (77.4–95.4) | 91.3 % (79.7–96.6) |
| discordant | 76.6 % (62.8–86.4) | 78.3 % (64.4–87.7) |
| **gap** | **76.6 pp** | **78.3 pp** |

The gap moves by 1.7 percentage points, and it moves **against** the smaller reading — so the
headline figure is the conservative one. The inconsistency is real, it sits in the newest datapoint
this disease has, and it is reported rather than smoothed over.

---

## 4 · Results — what the field has already done, and what it wrote down

### 4.1 The endpoint migrated between 2019 and 2025, and nobody wrote the argument

**One home: `D5_primary_endpoint_correction`.**

The 2019 pazopanib trial's **primary endpoint was the objective-response rate** — its own report
reads *"22 patients (one patient died before the primary analysis) were evaluable for the primary
endpoint: four (18 % [95 % CI 1–36]) had a RECIST objective response"* (PMID 31331701). The 2025
IMMUNOSARC II EMC cohort's primary endpoint was the **6-month progression-free rate**, as its
registration record states (NCT03277924).

So the field did not settle on a progression-free endpoint; it **changed** endpoints, six years
apart, without an argument in the literature for why. That is the situation in which the older
endpoint keeps being quoted as though it were the disease's verdict — which is what this paper is
about.

> ⚠ **Correction carried, not inherited.** This repository's own systemic-therapy pooling artifact
> summarises the record as *"both modern trials chose 6-month PFS rather than response rate as their
> primary endpoint"* — and its own verbatim quote of the 2019 trial, reproduced above, contradicts
> it. The superseded wording is retained here so it stays quotable; the correction is owed to
> [`emc-systemic-therapy-pooling.json`](./emc-systemic-therapy-pooling.json) →
> `findings_no_source_states`, which owns the sentence, and is detected rather than re-typed by
> `emc_endpoint_discordance.D5_primary_endpoint_correction`, so it cannot rot.

### 4.2 The endpoint completeness census

**One home: `D3_reporting_completeness`.** The denominator is every row of the source's
systemic-therapy table — **9**: 8 cohort rows plus 1 context-only row that reports rates without
counts. One of the 8 (IMMUNOSARC I) is a mixed soft-tissue-sarcoma cohort with no EMC subgroup
reported, so it contributes to no endpoint below; it stays in the denominator because *"reports
nothing extractable for EMC"* is exactly what this census measures, and dropping it would flatter
every row. For how many rows is each endpoint extractable as an integer count under the evidence
contract?

| endpoint | extractable for | of 9 | |
|---|---|---|---|
| objective-response counts | **7** | 9 | 77.8 % |
| disease-control counts | **5** | 9 | 55.6 % |
| an EMC-specific median progression-free survival | **3** | 9 | 33.3 % |
| 6-month progression-free status as a count | **1** | 9 | 11.1 % |

**The endpoint the field's own trials have migrated to is the one it reports least completely**, and
the gap bites hardest in the direction that matters: **4 of the 9 rows cannot enter a disease-control
pool at all, against 2 that cannot enter a response pool** (`rows_that_cannot_enter_a_pool`).
What the missing rows are missing is specific and mostly trivial to have avoided:

- Drilon 2008 — best-response categories given only as percentages;
- the apatinib EMC subgroup — per-subtype breakdown gives responses but not stable disease;
- Chiusole 2020 — disease-control *rates* only, several of which do not convert to integers on their
  own stated denominators (60 % of 11 = 6.6; 46.1 % of 14 = 6.5). This is the largest published EMC
  chemotherapy experience and the only one reporting outcome by regimen and line, and the evidence
  contract correctly refuses to reconstruct its counts;
- IMMUNOSARC I — mixed-histology cohort with no EMC subgroup reported separately.

⭐ **This is the finding with the cheapest remedy in the paper.** A four-cell table — complete
response, partial response, stable disease, progression, with the denominator — costs a sentence, is
compatible with every endpoint anyone might later want, and would have let every one of these
cohorts enter a pooled analysis of either kind.

### 4.3 Time-to-event figures are not merged — and five in circulation are not EMC figures

The evidence contract forbids merging time-anchored endpoints, so the three EMC-specific median
progression-free survivals are carried per row and not compared: **19 months** on pazopanib (95 % CI
11–27), **13.2 months** on sunitinib plus nivolumab (95 % CI 5.7–20.7), and **8 months** on
anthracycline-based chemotherapy (observed range 2–10, not a confidence interval). Different lines of
therapy, different eras, different assessment standards.

⚠ **Five further time-to-event figures circulate in this literature as EMC results and describe a
different population or a different quantity.** They are listed and evidenced in
[`emc-systemic-therapy-pooling.json`](./emc-systemic-therapy-pooling.json) →
`analyses.A5_time_to_event_never_pooled`, which owns them; the shortest statement of why they matter
here is that a field which mis-attributes five of its own headline numbers is a field whose reporting
conventions, not just whose endpoint choice, need saying out loud.

---

## 5 · Results — what each endpoint costs a trial this disease can accrue

**One home: `D4_small_trial_arithmetic`.** The only inputs are the two pooled proportions from §3 and
the binomial distribution. It assumes the pooled proportion is the true event rate — which is the
assumption a trial designer makes when powering on a historical rate — and the Wilson bounds are
carried through every row for exactly that reason. **It is not a power calculation for any specific
design and it names no alternative hypothesis.**

| n | expected objective responses | expected disease-control events | P(no objective response at all) at point estimate | at CI lower bound | at CI upper bound |
|---|---|---|---|---|---|
| 10 | 1.3 | 8.9 | 0.255 | 0.539 | 0.055 |
| 15 | 1.9 | 13.4 | 0.129 | 0.395 | 0.013 |
| 20 | 2.6 | 17.9 | 0.065 | 0.290 | 0.003 |
| 22 | 2.8 | 19.7 | 0.050 | 0.256 | 0.002 |
| 23 | 2.9 | 20.6 | 0.043 | 0.241 | 0.001 |
| 25 | 3.2 | 22.3 | 0.033 | 0.213 | 0.001 |
| 30 | 3.8 | 26.8 | 0.017 | 0.156 | 0.000 |

**Patients required per single event: 7.8 for an objective response, 1.1 for a disease-control
event.**

**Patients required for a 90 % chance of seeing at least one objective response: 17** at the point
estimate, **38** at the interval's lower bound, 8 at its upper bound. For scale, the two modern
prospective EMC cohorts accrued **22** and **23** response-evaluable patients — the first across
2014–2017 at eleven European sites, the second across 2020–2024 at nine.

### 5.1 The asymmetry, stated in both directions

**Both endpoints fail at this sample size, in opposite directions, and both failures are real.**

- **Objective response is too rare.** A 10-patient cohort of an agent whose true response rate equals
  the pooled estimate returns zero responses about a quarter of the time, and at the interval's lower
  bound more than half the time. A zero in that regime is **uninterpretable, not negative** — yet it
  is read as negative, and a futility rule keyed to it would stop such an agent at that rate.
- **Disease control is too common.** At 89.4 % it is near its ceiling, so almost every patient is an
  event and the endpoint has very little room left in which to distinguish anything. Worse, in this
  disease the null it would need to beat is not zero and nobody knows what it is (§6).

Neither observation recommends an agent or a design. Together they say the endpoint question in EMC
is not *which is better* but *what does each one buy at n ≈ 20* — and that the answer for the
response rate is: less than the trial costs.

---

## 6 · Limitations

**The first of these is the strongest argument against this paper's own thesis, and it is stated
first for that reason.**

### 6.1 ⛔ Disease control in an indolent tumour is an uncalibrated endpoint — this is the objection that would sink the paper if it were pushed harder than the paper pushes it

Stable disease is only evidence of activity if the disease would otherwise have progressed. EMC is
described throughout its own literature as indolent, and this repository's pooled reading of its
outcome cohorts (§1.1) puts disease-specific death well below distant metastasis — across partly
different study sets, so read as a direction rather than as a within-cohort comparison. So **an
unknown share of the 36 stable diseases in §3 would have been stable without any treatment**, and
nothing in the published record can size that share:

- **None of the three cohorts was randomised against no treatment.** No randomised evidence exists
  for any systemic therapy in EMC. The one randomised dataset that touches the disease randomised
  translocation-related sarcomas as a class, and its best-supportive-care arm contained three
  mesenchymal chondrosarcoma patients and **no EMC at all** — so it is not a comparator for anything
  here (Morioka 2016; PMID 27418251).
- **All three trials required documented progression before entry**, which is the design feature that
  bounds the objection. A patient enrolled with radiologically progressing disease who is then stable
  is a different observation from a patient who was stable all along. *Bounds* is the honest verb: it
  does not settle it, because the rate of spontaneous stabilisation after documented progression in
  EMC is not published, and the progression window in the pazopanib trial was the previous 6 months
  rather than at the moment of enrolment.
- **Therefore the 89.4 % figure must never be read as a treatment effect.** It is the proportion of
  enrolled patients whose disease was not progressing at best-response assessment. That is a
  description of a cohort, not an attribution to a drug.

⭐ **What survives this objection is narrower than the paper's title and is what the paper actually
argues.** The confound attacks the *interpretation* of disease control. It does **not** touch:
(a) the arithmetic of §5, which shows an objective-response endpoint returns an uninterpretable zero
at achievable *n* regardless of what stable disease means; (b) the reporting census of §4.2, which is
about what was written down; or (c) the observation that the field changed its primary endpoint
without writing the argument (§4.1). A reader who rejects §3's interpretation entirely should still
accept §4 and §5.

### 6.2 Every denominator here is tiny, and no larger series is coming

The pooled response denominator is 47 patients — worldwide, ever, inside a prospective trial. One
contributing cohort is **two patients**. Its Wilson interval alone spans 0–65.8 % and says nothing on
its own; it is included because excluding a real EMC observation for being small is its own bias, and
flagged because a reader scanning a table weighs rows rather than denominators. The pooled response
interval (6.0–25.2 %) contains both *"this essentially does not happen"* and *"this happens in a
quarter of patients"*. **That width is a finding, not a provisional estimate awaiting a larger
series**: EMC's incidence is well under one per million.

### 6.3 The evidence is retrospective, single-arm and heterogeneous

Two of the three pooled cohorts are single-arm; the third is a two-patient subset of one arm of a
randomised trial whose control arm contained no EMC. Three different regimens, three accrual eras,
three networks. **Nothing here supports a statement that any drug is better than any other, or than
none.** The §4.2 census additionally draws on retrospective and named-patient series in which
response was physician-assessed rather than centrally reviewed.

### 6.4 The newest datapoint is a conference abstract with two unreconciled inconsistencies

The IMMUNOSARC II EMC cohort has no full paper. Europe PMC indexes none; ClinicalTrials.gov posts no
results for NCT03277924. Its primary endpoint is reported both as 77 % and as 16/23 (69.6 %) with no
reconciliation, and its best-response categories sum to 22 rather than 23 (§3.2). Its sibling cohorts
in the same master trial have full papers; this one does not. It contributes 23 of 47 patients to
every pooled figure in §3.

### 6.5 Residual non-independence between the two European cohorts

Both recruited through the Spanish and Italian sarcoma groups, and the IMMUNOSARC II abstract records
that 6 of 23 patients had received a prior antiangiogenic — a group that may include patients from
the pazopanib trial. Such a patient contributes two evaluations of two different drugs, which does
not double-count an observation but does violate independence, so the intervals in §3 are very
slightly narrower than they should be. No patient-level data is published with which to size it.

### 6.6 Best response is not duration, and this paper measures neither

Disease control as a *best-response category* says nothing about how long control lasted. A
6-month progression-free rate or a median progression-free survival does, which is precisely why
those endpoints are the interesting ones — and §4.2 shows they are the ones this literature reports
least completely. **This paper does not propose a specific replacement endpoint**, because the data
that would let anyone compare candidate endpoints on these patients has not been published.

### 6.7 What this paper does not claim, restated as a list

- ⛔ No efficacy claim for any agent in EMC, and no potency, dose, schedule, safety or
  therapeutic-window claim. None is supported by anything here.
- ⛔ No treatment recommendation, including a negative one. Sequencing, patient selection, and
  whether to treat asymptomatic indolent metastatic EMC at all are decisions this evidence base
  cannot inform.
- ⛔ No claim that disease control is the correct endpoint for EMC. §6.1 is the reason.
- ⛔ No claim about fusion-partner stratification. The observation that responders in one series
  carried *EWSR1::NR4A3* is exploratory in cohorts of 10 and 22 and supports no selection of any
  patient for any treatment; it is owned by
  [`emc-fusion-partner-stratification.md`](./emc-fusion-partner-stratification.md).
- ⛔ No regulatory claim. Nothing here speaks to what any agency would accept as an endpoint.

---

## 7 · Discussion

### 7.1 What a trialist could do with this

The concrete, low-cost consequences are all about **reporting**, and none requires a decision about
which endpoint is right:

1. **Publish the four-cell table.** Complete response, partial response, stable disease, progression,
   with the denominator that produced them. **Four of the nine rows cannot enter a disease-control
   pool** (Drilon 2008, the apatinib EMC subgroup, IMMUNOSARC I, Chiusole 2020) and **two of those
   cannot enter a response pool either** — in every case because the categories were printed as
   percentages, or not printed. It costs a sentence.
2. **State the response-evaluable denominator explicitly, and only once.** The pazopanib trial has
   three different patient counts — 26 started, 23 in the modified intention-to-treat set, 22
   evaluable for the primary endpoint — and this repository's own registry had previously attached
   the 18 % figure to the largest of them, which simultaneously understates the rate and overstates
   the evidence base.
3. **Report a progression-free endpoint as a count, not only as a Kaplan–Meier percentage.** One EMC
   cohort in nine does this. The percentage cannot be pooled with anything; the count can.
4. **Name the population every headline number belongs to.** Five circulating "EMC" time-to-event
   figures belong to a different population or a different quantity (§4.3).

### 7.2 What this does not license

It does not license reading a high disease-control rate as evidence that a drug worked (§6.1), and it
does not license abandoning response assessment — a response is an unambiguous observation and the
few that occur are informative precisely because they are hard to explain by natural history. The
argument is against using response *as the summary*, in a disease where it can only ever describe a
small minority of what was seen, at sample sizes where its absence is uninterpretable.

It is also not a criticism of the response criteria themselves. RECIST 1.1 names shrinkage **and**
progression as endpoints in its opening sentence (§1.2) and defines the categories for both; the four
counts §7.1 asks for are already produced by any trial that applies it. What §4.2 measures is that
those counts are usually not printed.

### 7.3 The honest open question

The quantity that would settle §6.1 is the rate of spontaneous stabilisation after documented
progression in untreated advanced EMC. It is not published, and a randomised no-treatment arm in an
ultra-rare indolent sarcoma is not a realistic ask. The nearest achievable substitutes are
observational: a growth-rate or time-to-next-treatment analysis across a registry with pre-treatment
imaging, or the growth-modulation-index design in which each patient is their own control. Both are
outside what this paper's data can support, and naming them is not proposing them.

---

## 8 · Data and code availability

Everything below is committed in this repository. Nothing is behind a login, a rental or a GPU.

| what | where |
|---|---|
| **Derived figures for every number in this paper** | [`research/manuscripts/emc-endpoint-discordance.json`](./emc-endpoint-discordance.json) |
| **Producer, with `--check` reproduction mode** | [`research/manuscripts/emc_endpoint_discordance.py`](./emc_endpoint_discordance.py) |
| **The integer counts, each with its verbatim quote, citation and exclusion reason** | [`research/manuscripts/emc-systemic-therapy-pooling.json`](./emc-systemic-therapy-pooling.json) |
| **Its producer** | [`research/manuscripts/emc_systemic_therapy_pooling.py`](./emc_systemic_therapy_pooling.py) |
| **The cited EMC clinical registry** | [`research/data/emc-clinical-registry.json`](../data/emc-clinical-registry.json) |
| **Registry evidence-contract validator (preflight gate 5)** | [`scripts/validate-registry.mjs`](../../scripts/validate-registry.mjs) |
| **Outcome meta-analysis quoted in §1.1 (different method — see §1.1)** | [`research/meta/meta-analysis.mjs`](../meta/meta-analysis.mjs) → [`research/meta/results.json`](../meta/results.json) |
| **The pooling contract this paper obeys** | [`systems/POLICY-evidence.md`](../../systems/POLICY-evidence.md) §2.1–2.4 |
| **RECIST 1.1 retrieval record (§2.2)** | branch `literature-cache`, `literature/recist11-citation-check/_index.json`, written by [`.github/workflows/fetch-literature.yml`](../../.github/workflows/fetch-literature.yml) with PMID 19097774 as the query's known-positive control |

**Cost of this analysis: $0.** CPU only; no GPU, no rental, no external service.

**Conflicts of interest:** none. **Funding:** none. **Patient data:** none — this paper uses only
aggregate counts already published in the cited reports. No individual patient is identifiable from
anything here, and no non-real or synthetic datum appears in this paper.

---

## 9 · References

1. Stacchiotti S, Ferrari S, Redondo A, *et al.* Pazopanib for treatment of advanced extraskeletal
   myxoid chondrosarcoma: a multicentre, single-arm, phase 2 trial. *Lancet Oncol* 2019;20:1252–62.
   PMID 31331701. doi 10.1016/S1470-2045(19)30319-5. NCT02066285.
2. Hindi N, *et al.* Phase II of sunitinib plus nivolumab in extraskeletal myxoid chondrosarcoma:
   results from the GEIS, ISG and UCL IMMUNOSARC II study. *J Clin Oncol* 2025;43(16_suppl):11513.
   doi 10.1200/JCO.2025.43.16_suppl.11513. NCT03277924. *(Conference abstract; no full paper.)*
3. Morioka H, Takahashi S, Araki N, *et al.* Results of sub-analysis of a phase 2 study on
   trabectedin treatment for extraskeletal myxoid chondrosarcoma and mesenchymal chondrosarcoma.
   *BMC Cancer* 2016. PMID 27418251. PMC4946242. doi 10.1186/s12885-016-2511-y.
   JapicCTI-121850.
4. Stacchiotti S, Dagrada GP, Morosi C, *et al.* Activity of sunitinib in extraskeletal myxoid
   chondrosarcoma. *Eur J Cancer* 2014;50:1657–64. doi 10.1016/j.ejca.2014.03.013.
5. Stacchiotti S, Ferrari S, Morosi C, *et al.* Anthracycline-based chemotherapy in extraskeletal
   myxoid chondrosarcoma: a retrospective study. *Clin Sarcoma Res* 2013;3:16. PMID 24345066.
   PMC3879193. doi 10.1186/2045-3329-3-16.
6. Drilon AD, Popat S, Bhuchar G, *et al.* Extraskeletal myxoid chondrosarcoma: a retrospective
   review from 2 referral centers emphasizing long-term outcomes with surgery and chemotherapy.
   *Cancer* 2008. PMID 18951519. PMC2779719. doi 10.1002/cncr.23978.
7. Xie L, Xu J, Sun X, *et al.* Apatinib for treatment of inoperable metastatic or locally advanced
   chondrosarcoma. *Cancer Manag Res* 2020. PMID 32547189. PMC7237692. doi 10.2147/CMAR.S253201.
8. Chiusole B, Le Cesne A, Rastrelli M, *et al.* Extraskeletal myxoid chondrosarcoma: clinical and
   molecular characteristics and outcomes of patients treated at two institutions. *Front Oncol*
   2020. PMID 32612944. PMC7308468. doi 10.3389/fonc.2020.00828.
9. Martin-Broto J, Hindi N, Grignani G, *et al.* Nivolumab and sunitinib combination in advanced soft
   tissue sarcomas: a multicenter, single-arm, phase Ib/II trial. *J Immunother Cancer* 2020. PMID
   33203665. PMC7674086. doi 10.1136/jitc-2020-001561.
10. Remiszewski P, *et al.* From pathogenesis to the patient's bedside: a comprehensive review of
    extraskeletal myxoid chondrosarcoma. *J Cancer Res Clin Oncol* 2025. PMID 41055792. PMC12504171.
    doi 10.1007/s00432-025-06316-5.
11. Masunaga T, Tsukamoto S, Nagano A, *et al.* The role of radiotherapy and chemotherapy in
    extraskeletal myxoid chondrosarcoma. *J Orthop Surg Res* 2025. PMC12398172.
    doi 10.1186/s13018-025-06245-6.
12. Meis-Kindblom JM, Bergh P, Gunterberg B, Kindblom LG. Extraskeletal myxoid chondrosarcoma: a
    reappraisal of its morphologic spectrum and prognostic factors based on 117 cases.
    *Am J Surg Pathol* 1999. PMID 10366145. doi 10.1097/00000478-199906000-00002.
13. Eisenhauer EA, Therasse P, Bogaerts J, *et al.* New response evaluation criteria in solid
    tumours: revised RECIST guideline (version 1.1). *Eur J Cancer* 2009. PMID 19097774.
    doi 10.1016/j.ejca.2008.10.026.

---

## Appendix A · Superseded and corrected values

Per [CLAUDE.md](../../CLAUDE.md) rule 1.2, a corrected value is registered rather than silently
dropped, and the live text above carries only the current value.

| superseded | current | where it lived | why it changed |
|---|---|---|---|
| *"both modern trials chose 6-month PFS rather than response rate as their primary endpoint"* | the 2019 pazopanib trial's primary endpoint was the **objective-response rate**; the 2025 IMMUNOSARC II EMC cohort's was the **6-month progression-free rate** | [`emc-systemic-therapy-pooling.json`](./emc-systemic-therapy-pooling.json) → `findings_no_source_states` | contradicted by that file's own verbatim quote of the 2019 trial (§4.1). The correction is owed to the file that owns the sentence; this paper does not edit it |
| "18 % of 26" for the pazopanib response rate | **4 of 22** — 26 started, 23 met modified-intention-to-treat criteria, 22 were evaluable for the primary endpoint | the EMC clinical registry, corrected before this paper was written | quoting the largest of a trial's three patient counts understates the rate and overstates the evidence base at once. Owned by [`emc-systemic-therapy-pooling.json`](./emc-systemic-therapy-pooling.json) → `corrections_to_the_repository_registry` |
| "Liu 2020 (apatinib)" as the short citation label | **Xie 2020 (apatinib)** — the registry's author list reads *"Xie L, Xu J, Sun X, Liu K, … Liu X, …"*; Liu X is the seventh author | [`emc-systemic-therapy-pooling.json`](./emc-systemic-therapy-pooling.json) → `citations.apatinib2020.short` | found by cross-checking every author string in this paper against the registry's own `authors` fields instead of writing any from memory. This paper had inherited the wrong first author from that label before the check. It changes no count and no conclusion; a wrong first author is how a citation stops resolving for a reader searching by name |

## Appendix B · What would change this paper's conclusions

Stated in advance so the paper can be falsified rather than merely disagreed with.

| finding | effect |
|---|---|
| A published rate of spontaneous stabilisation after documented progression in untreated advanced EMC | Would calibrate §6.1 directly. If it were high, §3's gap would remain a true statement about measurement while losing most of its clinical interest |
| The IMMUNOSARC II full paper, resolving its 23-vs-22 denominator and its 77 %-vs-69.6 % primary endpoint | Would replace 23 of 47 pooled patients with peer-reviewed counts. §3.2 already brackets the numerical effect as 1.7 percentage points |
| Any new prospective EMC cohort reporting a four-cell best-response table | Would enter §3's pool directly and could move it in either direction; a cohort with many progressive diseases would narrow the gap |
| Evidence that the two European cohorts share patients | Would widen §3's intervals. The point estimates would not move, because no patient contributes two evaluations of the same drug |
| An EMC trial reporting a growth-modulation index or time-to-next-treatment | Would supply the within-patient comparator this literature lacks, and is the single most informative thing that could be added to it |
