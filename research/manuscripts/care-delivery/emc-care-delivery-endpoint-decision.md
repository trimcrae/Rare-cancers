---
id: DOC-EMC-CARE-DELIVERY-ENDPOINT-DECISION
title: "What the EMC care-delivery evidence actually supports — five route decisions, two refuted absences, and the denominators that decide them"
level: L3
kind: memo
status: live
canonical_for: ["the 2026-09-01 decision on ledger rows AUT-042, AUT-057, AUT-058, AUT-064 and AUT-065"]
purpose: >
  Answer the five parked care-delivery and locoregional judgement calls with a recommendation each,
  by reading the artifact that holds the data every row says is in hand and reporting where the row
  and the artifact disagree. It decides nothing about publishing that a bar decides; it says what
  each route can claim in one falsifiable sentence and what the honest denominator is.
scope: >
  L3. Five ledger rows serving PUB-CARE-DELIVERY and PUB-LOCOREGIONAL. It curates nothing new, runs
  no search, and re-litigates nothing the rows mark closed. It reports one $0 read of two files
  already committed to the literature-cache branch. It contains no new patient data, involved no
  wet-laboratory work, and is not clinical advice.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-09-01
last_verified: 2026-09-01
---

# What the EMC care-delivery evidence actually supports

> ⛔ **NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS.** Every
> number below is an observational association or a count of what was done, from retrospective
> series in which every treatment was allocated by indication. No randomised trial of any of these
> interventions exists in this disease.

**One home for every number.** Margin counts and rates:
[`emc-surgical-quality.json`](../../modalities/emc-surgical-quality.json). Cox coefficients:
[`emc-prognostic-coefficients.json`](../../modalities/emc-prognostic-coefficients.json). Site,
metastatic-site and local-therapy counts: [`emc-site-curation.json`](../../modalities/emc-site-curation.json).
Recurrence timing: [`emc-recurrence-timing.json`](../../modalities/emc-recurrence-timing.json).
Radiotherapy estimates and modality case reports:
[`emc-radiotherapy-contradiction.json`](../../modalities/emc-radiotherapy-contradiction.json).
Reconstructed survival: [`emc-ipd-survival.json`](../../modalities/emc-ipd-survival.json). The two
refutations in §2 and the blob identity they rest on:
[`emc-absence-claims-refuted.json`](./emc-absence-claims-refuted.json). **This file quotes those
artifacts and computes nothing.**

⚠ **No synthetic data enters this document.** Measured 2026-09-01:
`grep -c SAMPLE_SYNTHETIC research/data/emc-clinical-registry.json` returns **0**, and none of the
six modality artifacts above carries the flag. Nothing here is sourced from the clinical registry.

---

## 0 · The five decisions, in one table

| row | route | recommendation | the honest denominator |
|---|---|---|---|
| **AUT-064** | RT-SURGICAL-QUALITY | **WRITE IT — strongest of the five.** Not as a rate, as a *denominator* result. | Four named denominators, each explicit: 156 / 134 / 22 / 40. **No pooled rate exists and none should be quoted.** |
| **AUT-057** | RT-RISK-MODEL | **WRITE IT, MERGED INTO AUT-064.** Alone it is a null with one survivor; beside the margin rate it is the same finding measured a second way. | 45 printed coefficients, 12 cross-cohort comparisons, **0 in which both intervals exclude 1**. |
| **AUT-065** | RT-SURVEILLANCE | **WRITE IT, ONE PARAGRAPH.** The within-cohort censoring observation is confound-free and needs no model. | One cohort, one clock: upper quartile 63.5 months against its own median follow-up of 38. |
| **AUT-042** | RT-METASTASECTOMY | **DO NOT WRITE THE NOTE THE ROW PROPOSES.** Its sentence has no denominator, and its premise is refuted (§2). | Three different strata — 29, 26, 13 — that may not be summed. **"Roughly a quarter" is not computable.** |
| **AUT-058** | RT-RT-INTENSIFY | **REFUTED — already written, and the one new half is wrong.** | n/a; see §2 and §3.5. |

---

## 1 · The measurement that reframes all five, and what it actually says

Another seat read `publish_bar --paper PUB-CARE-DELIVERY` and `--paper PUB-LOCOREGIONAL` at **0/7**
with `endpoint_declared` open, and read that as the bar saying the manuscript does not meaningfully
exist. Re-run on `d5f8f3c67584` on 2026-09-01, the verdict holds and **the diagnosis is sharper than
that**. Clause 5 requires two things: a `what_it_would_claim` of at least 40 characters, and a
`document.file` that exists. Both papers pass the first. The failure line for both is one string:

```
[FAIL] the endpoint is a declared falsifiable claim
       endpoint names no existing document (None)
```

Three further clauses fail for the same reason and say so in their own words — *"has no
document.file in publications.json"*, *"has no readable document"*, *"names no document"*. So **four
of the seven clauses are one missing field**, and across all 32 entries in
`systems/graph/publications.json` the correlation is exact: every entry with `state: drafted` or
better has a `document.file` and every `unwritten`/`outlined` entry has none.

⭐ **The consequence for these five rows is that the bar is not the thing deciding.** The claim
sentences already exist and are already falsifiable. What the bar is reporting is that nobody has
written the paper, which is a statement about this program's output rather than about the evidence.
**So the question in front of each row is the §5 test — can the route name its paper in one
falsifiable sentence, and what is honestly missing — and §4 below answers it.**

⛔ **And PUB-CARE-DELIVERY's recorded reason for being unwritten is now false.** It reads: *"The
paper needs the reconstructed survival dataset (RT-IPD-SURVIVAL) to say anything quantitative;
without it, it is an argument with citations rather than a result."* Four quantitative artifacts
have landed since, none of which consumes the reconstruction: 196 operated patients with a margin
recorded, 45 printed Cox coefficients, 271 patients' site distribution, and four printed
time-to-event statistics with three interquartile ranges. The reconstruction is not what the paper
was waiting on, and AUT-065 already says so in its own words.

⚠ **Its blocker is mis-stated in the same direction.** `BLK-NO-CURATED-CLINICAL-DATA` reads *"the
clinical facts these routes need are IN the published record and have never been extracted into the
registry."* They have been extracted — into `research/modalities/`, not into the registry, and that
is the correct home rather than a shortfall: `emc-site-curation.json` records that
`research/data/emc-clinical-registry.json` is inside the inventory of a DOI-deposited archive, so
any byte change to it forces a re-stamp of a published deposit. The blocker describes a destination
the repository has deliberately stopped using.

---

## 2 · Two recorded absences, refuted at $0, from one file

Both rows AUT-042 and AUT-058 rest on an absence. **Both absences are false against the very corpus
each names**, and the discriminating observation is one article that sits inside both corpora.

Masunaga 2025 (`PMC12398172`, PMID 40885991) was read on 2026-09-01 through the GitHub contents API
at `refs/heads/literature-cache`, branch commit `0eac3e3aaa5b3e`. The API returns **the same blob
SHA, `79a8c197243f`, at both** `literature/emc-care-delivery-and-classification/PMC12398172.txt`
**and** `literature/emc-radiotherapy-2026-08-26/PMC12398172.txt` — so this is not two corpora each
missing a paper. It is one identical file inside both.

**REF-01 — metastasectomy.** `emc-care-delivery-evidence.json` records the query *"metastasectom*
within the EMC-matching subset of a 554-record open-access corpus retrieved 2026-08-09"* with the
result **"ZERO records."**, and RT-METASTASECTOMY's grade turns that into *"nobody has asked the
question in this histology."* The file in that corpus reads, verbatim: *"Eight patients (27.6%)
underwent metastasectomy, including six, one, and one who underwent lung, bone, and lymph node
resections, respectively."*

**REF-02 — carbon ion.** `emc-radiotherapy-contradiction.json` records
`carbon_ion.found_in_this_histology: false` over a 354-text corpus, and RT-RT-INTENSIFY's grade
turns that into *"carbon ion appears nowhere in it."* The file in that corpus reads, verbatim: *"Of
the eight patients who did not undergo surgery, two received carbon ion therapy, one received proton
beam therapy, and one received conventional radiotherapy."*

⛔⛔ **REF-02 is the worse of the two, because the artifact considered that exact sentence and
rejected it.** Its own field records a web-search synthesis reporting *"two received carbon ion
therapy, one received proton beam therapy"* and dismisses it: *"Read against the sources, that
belongs to EXTRACRANIAL CHONDROSARCOMA generally, not to this histology … An AI search summary is a
lead, never a citation."* The sentence is verbatim Masunaga, whose entire cohort is 171
pathologically diagnosed EMC patients. **The lead was right and the verification reached the wrong
source** — CLAUDE.md §4's warning that a stale or dismissed reading errs in the direction that kills
a route, arriving exactly where it was predicted to.

⭐ **The mechanism is the same for both and no gate could have caught either.** Neither value is
computed. `"result": "ZERO records."` and `"found_in_this_histology": False` are string and boolean
constants in their generators, so the build reads the constant and never the corpus. Worse,
`emc_radiotherapy_contradiction.py` carries a self-check that fails *"the carbon-ion finding has
flipped without its search being redone"* — written to stop an unexamined flip, it now also stops a
corrected one, so the value and its guard must move in one commit.

⚠ **What survives of each absence, narrowed rather than withdrawn.** No reachable series studies
metastasectomy *with a comparator*: Masunaga prints the count and no outcome by it, and Bishop's 5
of 13 distant recurrers are followed by that paper's own statement that salvage surgery was not
associated with improved disease-specific survival (p = 0.15) at thirteen patients. And no series
prints an outcome for the two carbon-ion or one proton-beam patient — all eight non-operated
patients are excluded from that paper's prognostic analysis. **Arms exist; comparisons do not.**
That is a weaker and true statement in place of a stronger and false one.

---

## 3 · Row by row

### 3.1 AUT-064 — the margin note. **WRITE IT, AND THE RESULT IS THE DENOMINATOR**

The row proposes *"a positive-margin rate with an honest denominator range across two independent
cohorts."* ⚠ **The artifact says something stronger and slightly different, and the artifact is
right:** *"THERE IS NO SINGLE POSITIVE-MARGIN RATE and the artifact refuses to elect one"*, with a
test that fails if the denominator stops moving the answer by more than any interval's width. The
row's phrasing — one rate carrying a range — is the reading the data refuses.

The four rates are 25.0 % over all 156 operated patients, 22.4 % over the 134 operated who were
localized at diagnosis, 40.9 % over the 22 operated who were already metastatic, and 35.0 % over the
40 in the second cohort where the field was recorded. **Every denominator is explicit and named**,
which is why this is a result and not the failure mode of an unclear denominator: nothing is
computed over a population nobody defined. The 9 curative-intent patients whose margin is unrecorded
in the second cohort are 18 % of that group, missingness is not plausibly random in a series
reaching back to 1980, and no rate over 49 is computed.

**What it would claim:** *quoting a positive-margin rate for this disease without its denominator
moves the answer by nearly twenty points inside a single paper, and the direction of that movement —
patients already metastatic are operated to a positive margin far more often — means the rate is not
a surgical quality metric unless the intent of each operation is known, which no reachable series
prints.*

Chiusole's outcome-by-margin contrast is real and secondary: local recurrence 2 of 26 after R0
against 5 of 12 after R1, metastases 4 of 26 against 7 of 12, both intervals wide and overlapping.
**It is a direction from 38 patients and confounded in the obvious way** — whatever made a tumour
impossible to clear is also a reason it recurs — so the margin is a marker of the tumour as much as
of the operation. The two R2 patients are printed as NA and no rate is computed over them.

⛔ **What the row marks closed stays closed and both closures were checked, not assumed.** Treatment
setting and unplanned excision are absent by reading: one source prints no centre at all, the other
is entirely referral-centre care and so holds the exposure constant by construction, and the two
candidate proxies carry `is_the_thing: false`. Re-curating either paper cannot produce them.

### 3.2 AUT-057 — the ordering-only prognostic statement. **WRITE IT, MERGED INTO 3.1**

The row asks what an ordering-only statement is worth publishing as. **Alone, less than it looks.**
Of 12 cross-cohort comparisons 11 agree in direction and all 12 pairs of intervals overlap, and the
artifact says plainly why both numbers are close to uninformative: overlap is near-guaranteed at
intervals this wide, 9 of the 12 are between two intervals that *both* include 1, and **in not one
comparison do both cohorts' intervals exclude 1**. The two cohorts are *consistent*, not
corroborating. The single directional disagreement is between two null results on different
endpoints and must not be reported as a contradiction.

**One covariate survives that filter, and it is surgical margin** — on the harmful side of 1 in all
three endpoints of the larger cohort and in the second cohort, the only covariate significant in
more than one model (local recurrence 4.76, 1.72–13.15; distant metastasis 2.37, 1.21–4.64; 3.40,
1.57–7.38 adjusted), and the only one whose direction holds across four endpoints and two
continents. The second cohort's own margin interval still includes 1 (0.540–7.570), so it is
consistent with the first without independently establishing it.

⭐ **That is the same answer as 3.1, reached by a different instrument, and it is why these two rows
should be one section rather than two notes.** A rate says how often the first operation is
incomplete; an ordering says it is the one thing that reliably matters afterwards. Neither is a
model. **No absolute risk is derivable** — no baseline hazard, no reference-group curve with a risk
row, therefore no survival probability, no nomogram, no n-year risk and no validation — and the
artifact holds `absolute_risk_computable: false` with a test failing the build if it is ever
flipped. A publication from these coefficients is an **ordering and must say so in its title**.

⚠ **The row's other half is confirmed rather than merely accepted:** neither cohort prints a
numbers-at-risk row under any of its seven stratified curves, so the reconstruction path is closed
for these covariates for a reporting reason. Do not re-attempt it.

### 3.3 AUT-065 — surveillance. **WRITE IT, ONE PARAGRAPH, AND IT IS ABOUT FOLLOW-UP NOT SCHEDULES**

The row's premise checks out: RT-IPD-SURVIVAL has produced data and the data is the wrong shape.
`emc-ipd-survival.json` holds exactly one admitted curve — 11 patients, 9 events, **progression-free
survival in an anthracycline-treated advanced cohort** — plus two patient rows printed in a
trabectedin table. None of that is time-to-recurrence after resection of localized disease, which is
the only curve a surveillance model could consume. **Do not wait on it.**

**What is publishable is a within-cohort observation that needs no model.** In the larger series the
upper quartile of time from surgery to local recurrence, 63.5 months, lies 25.5 months beyond that
same cohort's own median follow-up of 38 months; a quarter of the local recurrences it observed
happened later than half its patients were watched. Death from tumour behaves the same way, 69
against 38. **One paper, one set of patients, one clock**, so era, country, setting and imaging
generation cannot explain it. The anchors differ by the diagnosis-to-surgery interval, which the
paper does not print and which moves the comparison in the conservative direction.

⛔ **Three limits travel with it or it should not be written.** An interquartile range that fits
inside the observation window is what censoring *produces*, so the inference runs one way only and
the distant-metastasis row must not be read as reassurance. A median and an interquartile range are
three points on a cumulative distribution and cannot be differentiated into a hazard, so **no
surveillance interval, duration or schedule follows from this and a test forbids one appearing**.
And lead-time bias is untouched: finding a recurrence sooner moves the date of detection and need not
move the date of death.

⚠ The cross-cohort divergence — median time to distant metastasis 16 months against about 71, a
factor of 4.4 — is consistent with censoring and cannot be established by it, because the two
cohorts also differ in era, country and setting. It is context, not the finding.

### 3.4 AUT-042 — metastasectomy. **DO NOT WRITE THE SENTENCE THE ROW PROPOSES**

The row proposes a note saying *"local therapy of metastases is already standard for roughly a
quarter of these patients, with no comparator anywhere in the literature."* **Both halves fail.**

**The denominator does not exist.** The three counts sit in three different and non-summable strata:
8 of 29 among patients *presenting* with distant metastases; 8 lung metastasectomies and 2 ablations
in a second series whose own table prints its percentages against an undefined denominator of 47;
and 5 of 13 among patients who *developed* distant metastases during follow-up in a cohort localized
at diagnosis. Those are a presenting stratum, an unstated denominator and an incidence cohort.
**"Roughly a quarter" is the lowest of the three, taken from one stratum and dressed as a pooled
rate.** POLICY-evidence §2.1 forbids pooling across these and §2.3 forbids inventing a shared
denominator; a rate that cannot name its population is not a result, and this one cannot.

**And "no comparator anywhere in the literature" is refuted** — narrowly, but in the way that
matters. Bishop reports that neither salvage surgery (p = 0.15) nor salvage chemotherapy (p = 0.24)
was associated with improved disease-specific survival. That is a comparison, at 13 patients, and at
that size it establishes nothing in either direction. **The honest statement is that the only
comparison in the reachable literature is uninformative, not that none exists** — and the difference
is the whole value of the sentence, because a route justified by "nobody has asked" is a different
route from one justified by "one series asked at n = 13 and could not answer."

⭐ **What is worth writing sits one level up, in §2 rather than here:** an absence recorded as a
finding, load-bearing on a route grade, refuted by a file inside its own corpus. That is a statement
about how this program searches, and it is a better paragraph than the one the row asked for.

⛔ Lesion burden stays closed. No series prints per-patient lesion counts, so no oligometastatic
threshold fraction is computable and the eligibility criterion RT-METASTASECTOMY needs cannot be
stated. **Do not re-curate for it.**

### 3.5 AUT-058 — the radiotherapy contradiction. **REFUTED: ALREADY WRITTEN, AND THE NEW HALF IS WRONG**

The row says the finding worth something is that two series the field reads as conflicting are
statistically consistent, and asks whether it is worth writing up. **It was written up on
2026-08-07** in [`emc-radioresistance-reappraisal.md`](./emc-radioresistance-reappraisal.md), a live
L3 memo, **and written better than the row proposes**: over *three* series rather than two, with
Cochran's Q = 2.015 on 2 df (p = 0.365, I² ≈ 0.007), a pairwise z = 1.36 (p = 0.175), a quantified
correction for the measured indication bias that moves the registry's own estimate from 0.50 toward
0.33, and a demonstration that α/β is not identifiable from the record at all because fraction size
is perfectly separated from treatment setting. The row's proposed note is a subset of a document
that already exists.

⚠ *A coincidence worth recording so nobody reports it as a defect:* the heterogeneity p-value 0.365
equals the registry's printed p-value for its radiotherapy coefficient. For 2 degrees of freedom
p = exp(−Q/2), and exp(−1.0075) = 0.3651. The arithmetic is right and the collision is arithmetic.

**The genuinely new half of AUT-058 is the particle census, and §2 refutes it.** Carbon ion has been
delivered in this histology — two patients, in the largest reachable series, inside the corpus the
census searched — alongside one proton-beam patient in the same paragraph. No outcome is printed for
any of them, because all eight non-operated patients are excluded from that paper's prognostic
analysis. **This does not make particle therapy promising in this disease and nothing here says it
does.** It removes a false negative and leaves an existence proof with no denominator and no
outcome, which is a weaker claim than the route was carrying and a true one.

---

## 4 · Can `endpoint_declared` be closed? One sentence each

**PUB-CARE-DELIVERY — the claim sentence needs one amendment before any document is written.** Its
declared claim names three determinants. Two are supported by artifacts in hand and **the third
cannot be studied at all**: *"whether the diagnosis was known before it"* is the unplanned-excision
question, and `emc-surgical-quality.json` records `unplanned_excision.recorded_in_any_reachable_series:
false` with both candidate proxies marked `is_the_thing: false`, alongside the same verdict for
treatment setting. **A declared claim one third of which no reachable source can address is not
falsifiable in that third.** The honest sentence the evidence in hand does support:

> In extraskeletal myxoid chondrosarcoma the completeness of the first operation is the only
> determinant that holds its direction across four endpoints and two independent cohorts, and the
> published record cannot price it, cannot say whether the diagnosis was known before that operation,
> and stops watching patients before a quarter of the local recurrences it reports have happened.

That sentence is falsifiable in three separate places — a series printing a covariate that holds
across the same four endpoints refutes the first clause, a baseline hazard or a reference-group curve
with a risk row refutes the second, and a series recording referral status or unplanned excision
refutes the third — and every clause is already carried by a committed artifact.

⛔ **Even so, `endpoint_declared` cannot close tonight, and the reason is mechanical rather than
evidentiary.** Clause 5 requires an existing `document.file`, that field lives in
`systems/graph/publications.json`, and **this document is not that paper and must not be pointed at
by it** — it is a decision memo about five ledger rows, not the manuscript its claim describes.
What is missing is a manuscript covering §3.1, §3.2 and §3.3 as one argument, plus the one-line graph
edit. Both are free and neither is this seat's to make.

**PUB-LOCOREGIONAL — no, and more is missing.** Its claim survives on three of four clauses.
*Extremity-primary* holds at 71.6 % strict and 84.5 % inclusive over 271 patients, but the artifact's
own reading is that the binding uncertainty is a **category boundary rather than a sample size** —
the gap between the two definitions is wider than the interval on either, and the inclusive pool is
biased downward because only one of three series contributes junctional patients to it. Any sentence
quoting a single extremity fraction is quoting a boundary it did not state. *Slow enough for local
control to matter* holds, from §3.3. *Lung-metastasis-dominant* holds only as **involvement**: the
27/29 and 12/13 readings are upper bounds on a lung-confined fraction, not measurements of one, and
the single series that separates confined from involved in its own words reports the confined figure
markedly lower — which runs against the eligibility criterion a lung-directed strategy needs. And
*"had never assessed any of it"* is the clause §2 breaks: metastasis-directed local therapy is being
delivered and reported in every reachable series, and carbon ion and proton beam have each reached
patients with this histology. **The correct clause is that these things are done and not studied,
which is a different and more defensible paper than the one currently declared.**

⇒ **PUB-LOCOREGIONAL needs its claim sentence rewritten first, then a document.** Two of its four
routes already have live memos — this one's §3.5 subject and the metastasis-directed radiotherapy
concept note — and **neither is the portfolio paper**, so neither may be wired to `document.file` as
a shortcut.

---

## 5 · What this document does not claim

- **No efficacy, for anything.** Margin, radiotherapy, carbon ion, proton beam, metastasectomy and
  surveillance are each discussed as an association or a count of what was done. Every treatment in
  every series was allocated by indication, and the one indication bias that has been measured runs
  against radiotherapy rather than for it.
- **No pooled estimate crosses a population POLICY-evidence would refuse to pool.** No positive-margin
  rate is combined across the two cohorts, no metastasectomy rate is combined across the three strata,
  no hazard ratio is pooled, and no time-anchored figure is merged.
- **No absolute risk and no schedule.** The coefficients order patients and cannot price them; the
  timing statistics establish a long right tail and cannot give its shape.
- **No claim that either corpus is complete.** §2 shows two absences are false against corpora that
  contain the refuting file. It bounds nothing upward, and "not found in an open-access corpus" was
  never the same as "does not exist."
- **No correction was applied.** The two artifacts refuted in §2, the two publication records
  discussed in §1 and §4, and the two route grades that inherit the absences all sit outside this
  seat's owned paths and are left for the driver to sequence.
