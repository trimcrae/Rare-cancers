---
id: DOC-EMC-MORTALITY-MECHANISMS
title: What actually kills EMC patients — mechanism of death, and the share of it no antitumour route addresses
level: L3
kind: memo
status: live
canonical_for: [ST-MORTALITY-MECHANISM, RT-COMPETING-MORTALITY, RT-RESPIRATORY-FAILURE, RT-TREATMENT-HARM, RT-EARLY-PALLIATIVE, RT-VTE-PROPHYLAXIS]
purpose: >-
  Answer three questions the route portfolio has never asked: when EMC kills someone, what is the
  proximate mechanism; which of those mechanisms are treatable without treating the cancer; and what
  such treatment would actually be worth in survival terms.
scope: >-
  Mortality mechanisms and non-antitumour interventions. Owns the grade of every route in
  ST-MORTALITY-MECHANISM. Owns no clinical figure — every number points at the clinical registry.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-09
last_verified: 2026-09-04
---

# What actually kills EMC patients

> **⛔ NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS**, for any
> intervention named, including the ones with randomised evidence behind them in other diseases.
> Nothing here is a prognosis and nothing here is advice. A mechanism being common is **not**
> evidence that treating it changes survival, and the distance between those two statements is most
> of what this memo is about.

**The question (trimcrae, 2026-08-09).** Every route in this portfolio fights the tumour. EMC is
indolent. So: when it does kill people, what is the actual mechanism — and of those mechanisms, do
any have symptomatic treatments that would prolong EMC survival *without* treating the cancer?

---

## 0 · Why this was missing, and why that is not the same as it having been rejected

The [modality census](../../systems/views/modality-census.md) enumerates **217 modality classes** and
grades each against this disease. Supportive care appears in it, and is graded out — but read *why*:

- `MOD-ANTICOAGULANT` → `not_applicable`, because it is *"a supportive-care indication addressing
  thrombotic risk, **with no antitumour claim to assess**."*
- `MOD-GLUCOCORTICOID` → `excluded`, because it is *"used across oncology for **supportive** and
  anti-oedema indications **rather than as antitumour therapy**."*

**Both readings are correct on the census's own axis, and neither is a finding about EMC.** The census
grades antitumour activity, so an intervention with no antitumour claim cannot score at all — it is
filtered by the grading criterion before any evidence about it is consulted. ⛔ **That is precisely
the *considered-and-dismissed* versus *never-pointed-at* distinction the census exists to make,
failing on the one question its criterion cannot express.** The absence was structural, not
evidential, which is why this is registered as a new family rather than argued into an existing one.

---

## 1 · The ceiling — what a perfect antitumour therapy could buy

Before asking what kills people, ask how much of the dying is even in scope. Computed by
[`emc_mortality_decomposition.py`](./emc_mortality_decomposition.py) →
[`emc-mortality-decomposition.json`](./emc-mortality-decomposition.json), entirely from figures whose
one home is [the clinical registry](../data/emc-clinical-registry.json).

⭐ **THE DIRECT CAUSE SPLIT — the strongest reading, and it needs no survival curve at all.** When one
study reports, for one cohort, how many patients died **of** the disease and how many died of
**something else**, the competing share is a ratio of two counts from the same patients under the
same ascertainment: no estimator mismatch, no cross-population pairing, no subtracting percentages.
Masunaga 2025 (the Japanese national registry, PMID 40885991) reports exactly that, and **the
other-cause counts were in the paper's full text and not in the curated record** — a registry that
tracks disease-specific death has no field for the deaths that were not. The mortality probe pulled
them out; they are now in [the registry](../data/emc-clinical-registry.json) with the source
sentence attached.

| stratum | n | EMC deaths | other-cause deaths | **share not EMC** | **antitumour ceiling** | median f/u |
|---|---:|---:|---:|---:|---:|---:|
| localised, surgical | 134 | 9 | 4 | **30.8 %** | **6.7 pts** | 38 mo |
| metastatic at diagnosis | 29 | 9 | 1 | **10.0 %** | **31.0 pts** | 41 mo |
| **both** | 163 | 18 | 5 | **21.7 %** | — | ~39 mo |

⭐ **THE STRATUM SPLIT IS THE RESULT, NOT A SUBGROUP DETAIL.** For **localised** EMC — the majority of
patients — curing the cancer outright would add **6.7 points** of survival at three years, because at
that horizon most of these patients are not dying of it. For **metastatic** disease the same cure is
worth **31 points**. ⇒ **The antitumour portfolio's value is concentrated almost entirely in the
metastatic stratum**, and for localised patients the deaths available to prevent are mostly not the
cancer's.

**The two weaker readings, kept because they show the horizon effect.** Meis-Kindblom 1999 (n = 117,
PMID 10366145) pairs a 10-year all-cause curve against a crude disease-death proportion — different
estimators — and gives **39.4 %** with an **18.2**-point ceiling. The cross-series band at 10 years
gives **50–57 %** (4 of 6 pairings coherent; 2 arithmetically impossible, which is the pairing
disclosing that it joins studies that cannot describe one population). At **5 years the cross-series
pairing collapses** — 6 of 12 coherent — so no 5-year figure is quoted.

> ⚠ **THESE ARE NOT IN CONFLICT, AND THE PATTERN IS ITSELF A FINDING: the competing share RISES with
> follow-up.** 21.7 % at ~3 years, 39.4 % at 10. That is what an indolent disease should do — EMC
> deaths accrue late, over decades, while ordinary deaths accrue from day one at a rate that only
> climbs with age. So a short-follow-up study understates how much of a patient's *lifetime*
> mortality is not their sarcoma.

> **⇒ Read as a ceiling: a therapy preventing EVERY EMC death buys roughly 7 points of survival for a
> localised patient at three years and roughly 31 for a metastatic one, and by ten years somewhere
> between a third and a half of all deaths are already outside its reach.** That bounds this
> repository's **entire 68-route antitumour portfolio taken together**.

**⚠ The one directional bias, stated because it favours this memo's own conclusion.** Disease-specific
survival estimated by censoring other-cause deaths *overstates* the cumulative incidence of disease
death under competing risks. So `1 − DSS` is an over-estimate of EMC's share, and the competing share
above is an **under-estimate**. The bias runs against the argument being made, which is the only
reason subtracting summary percentages across heterogeneous studies is publishable at all.

### ✅ The background check — is any of this real, or just incomparable studies?

The decomposition is worthless if the "other-cause" deaths are an artifact of pairing studies that
never described one population. So: are the observed non-EMC deaths the **size** an ordinary cohort of
this age and sex produces anyway? Compared at **each study's own follow-up**, against a US life table
(WHO GHO, `nMx`, 2021) blended to this cohort's 2:1 male ratio at age 55:

| stratum | follow-up | observed other-cause | expected background | **ratio** | 95 % CI |
|---|---:|---:|---:|---:|---:|
| localised | 3.2 y | 3.0 % (4/134) | 3.1 % | **0.97** | 0.38–2.41 |
| metastatic | 3.4 y | 3.4 % (1/29) | 3.3 % | **1.04** | 0.18–5.18 |

> ⭐ **EMC patients die of other causes at almost exactly the rate their age and sex predict.** The
> competing mortality is real, and it is *ordinary*. That is what the check was for, and it passes.

⚠ **It rests on 4 events and 1 event.** The intervals are wide, so what this establishes is
**consistency** with background, never equality to it. And the check is **one-sided by construction**:
a general-population table over-states background for a cohort fit enough to reach and survive a
sarcoma diagnosis, so it can *refute* "this gap is background" and cannot *prove* it. It did not
refute it.

**⛔ What this does NOT say:** that competing deaths are preventable. It says only that they exist, in
quantity, and that nothing on the board is aimed at them. Establishing preventability needs a named
cause and a measured intervention — §2 and §3.

---

## 2 · The mechanisms — ⏳ RETRIEVAL RUNNING, NOT YET READ

**⛔ THIS SECTION IS DELIBERATELY EMPTY OF CONCLUSIONS.** The honest answer to "what is the most
common mechanism of death in EMC" is that **this repository does not yet know**, and the reason is
worth stating: every pooled EMC outcome table reduces a death to a *vital status*, while the
mechanism — when it is recorded at all — sits in the prose of case reports and small series. Nobody
has tabulated it.

So the prose is being made into the dataset.
[`scripts/lit_mortality_probe.py`](../../scripts/lit_mortality_probe.py), dispatched on CI
(`fetch-literature.yml`, `slug=mortality-probe`, run `31334481362`), retrieves **every open-access
EMC paper Europe PMC returns** as full text and keeps **every sentence containing a death cue,
verbatim, with its PMCID** — alongside a 24-query citation index so that an absence can carry a real
`hitCount: 0` rather than a remembered impression.

**⛔ The probe classifies nothing, and that is a design decision rather than a limitation.**
Retrieval is mechanical; the reading is done afterwards against the quoted sentences, so every row of
the eventual breakdown resolves to a source a reader can check. A regex deciding *"cause of death =
respiratory failure"* would be a fabricated clinical fact wearing an artifact's costume — the exact
shape of failure CLAUDE.md §4 records, where a populated field was mistaken for a measured one.

The filter is **recall-first** on purpose: it keeps negatives (*"no deaths occurred"*) and bare vital
statuses (*"died of disease at 62 months"*). A visible false positive costs a reader a moment; a
silently dropped unusual terminal event costs the finding.

**What the record's shape lets us anticipate — as hypotheses to be checked against the corpus, not
as findings:**

| candidate mechanism | why it is a candidate | how the corpus settles it |
|---|---|---|
| progressive pulmonary metastatic burden → respiratory failure | the registry records distant spread as *mostly lung*, with survival measured in years after it | count of sentences naming a respiratory terminal event |
| competing non-cancer causes | §1 says these are ~40 % of deaths; EMC series record only that they were *not* EMC | sentences naming an unrelated or intercurrent cause |
| treatment-related death | anthracycline exposure across a decade-scale survivorship; neutropenic sepsis acutely | sentences naming toxicity, postoperative or treatment-attributed death |
| local / regional complication | pelvic and proximal primaries carry a worse prognosis in the registry | sentences naming cord compression, obstruction, haemorrhage, airway |
| thromboembolism | years of carrying pulmonary metastases; one of the few *abrupt* mechanisms available to an indolent disease | sentences naming embolism or thrombosis |

⚠ **The count that will matter most is the one for "unstated".** In a case-report literature it will
be large, and it bounds every proportion the corpus can support. It gets reported as prominently as
the mechanisms do.

⚠ **And the corpus is a convenience sample.** Case reports over-represent dramatic and unusual
terminal events and under-report ordinary decline, which biases *against* the slow respiratory course
that §1's natural history predicts. That is the opposite direction from the bias in §1, and both are
stated rather than netted.

---

## 3 · What symptom-directed treatment would be worth — ⏳ 1 OF 8 SUB-QUESTIONS ANSWERED

**⛔ NO EFFECT SIZE IS WRITTEN HERE FROM RECOLLECTION.** This memo names no trial, no percentage and
no PMID for any intervention until the retrieval returns it. That restraint is not fastidiousness: it
is the documented failure mode in CLAUDE.md §7, where an agent drafting a manuscript wrote a citation
from memory, the PMID existed in no committed source, and it **passed `lint_claims` twice** — because
claim *strength* and citation *provenance* are orthogonal, and a hedged sentence on an invented PMID
is a perfect sentence to a linter that reads only hedging.

The probe's third query block asks the questions this section needs answered, and each has a real
`hitCount` waiting: ✅ **early specialist palliative care and overall survival — RETRIEVED AND READ
2026-09-04 (AUT-219)**, see below; structured patient-reported symptom monitoring and overall
survival; thromboprophylaxis in ambulatory cancer; sepsis-bundle mortality in neutropenic and
immunocompromised patients; malignant pleural effusion management; cachexia intervention; exercise
oncology; palliative care in **sarcoma specifically** (searched as a byproduct of the query above —
title-level, not a dedicated search — and found nothing; see below).

**✅ Early specialist palliative care — the class-level finding, and what it does not show.** The
class replicates across three independent randomised trials in three distinct populations: Temel et
al. 2010 (US, metastatic NSCLC, n=151, PMID 20818875, median OS 11.6 vs 8.9 months, p=0.02), Allende
et al. 2024/PACO (Mexico/LMIC, advanced NSCLC, n=146, PMID 38558247, median OS 18.1 vs 10.5 months,
HR 1.5 [1.04-2.3], p=.030), and Chen et al. 2023 (China, NSCLC, n=140, PMID 37781179, HR 0.19
[0.04-0.85], p=0.029). Kochovska et al. 2020 (PMID 32953543) shows the survival evidence base was
thin (2 studies, one of them a timing-within-palliative-care comparison rather than early-vs-none) as
of that date -- the two subsequent trials materially strengthen the class-level finding. ⚠ **All
three are NSCLC, all three are months-scale survival populations. EMC's natural history runs to
decades, and no trial has tested whether the effect transfers to a disease this indolent** -- that is
the route's actual open question, and it is answered by none of the four papers above. A title-level
search of the same 388-paper retrieved corpus for "sarcoma" found one hit, unrelated (visceral
angiosarcoma epidemiology), consistent with -- not proof of -- no sarcoma-specific trial existing.
Full detail, including the mechanism candidates the original trials proposed (earlier symptom
detection, less aggressive end-of-life chemotherapy) and why neither is confirmed here: `RT-EARLY-
PALLIATIVE` in `systems/graph/routes.json`, `EV-TEMEL-2010` / `EV-PACO-2024` / `EV-CHEN-2023-CEPC` /
`EV-KOCHOVSKA-2020` in `systems/graph/evidence.json`. Written into the paper at
`emc-mortality-mechanisms-paper.md` §4.3.

**The arithmetic each retrieved effect size will feed**, once it exists:

> gain in survival ≈ *attributable fraction of deaths* (§2) × *relative effect of the intervention*
> (retrieved) × *transferability* (graded, never assumed)

**⚠ Transferability is the dominant uncertainty and must not be buried in it.** Every candidate
effect size in this class was measured in some other cancer, in populations with far shorter survival
than EMC's. That cuts both ways and the memo will say so in both directions: a decade-scale
survivorship is a *longer window* for a supportive intervention to act in, and it is also a
population no such trial has ever enrolled. **A transferred effect is labelled `transferred`, and a
number carried across from another disease never gets stated as a result in this one.**

**⛔ And the specific answer to the question as posed — "if it kills through acute sepsis and we are
better at treating that, what is the real impact?" — is expected to be SMALL, for a reason worth
stating in advance so the analysis cannot be read as having gone looking for a big number.** §1's
natural history is a disease that kills slowly. The mechanisms most amenable to acute rescue — sepsis,
embolism — are the ones an indolent tumour reaches *least* often, while the mechanism it reaches most
often, slow respiratory failure from accumulating lung metastases, is the one acute-care improvement
does least for. **If that is what the corpus shows, the honest headline is that the largest
non-antitumour lever in EMC is not acute rescue at all — it is §1's competing mortality and the
treatment-related deaths in §2, neither of which requires any new science.** That is a prediction
recorded before the data lands, so it can be wrong on the record.

---

## 4 · The route that is subtraction

One route in this family is worth surfacing here because it inverts the portfolio's usual shape:
**`RT-TREATMENT-HARM`, whose intervention is to stop doing something.**

The registry records that in the Drilon 2008 two-referral-centre series (n = 87, PMID 18951519)
**chemotherapy produced no objective responses**, with median progression-free survival of 5.2
months. The registry separately records that no objective response to trabectedin has been reported
in an EMC patient at all. Set against that: anthracycline cardiotoxicity acting over a
decade-scale survivorship, and neutropenic sepsis acting immediately.

⚠ **This is stated as a question, not a recommendation, and the distinction is load-bearing.** "No
objective response in a small, heavily selected series" is not "no benefit" — response rate is not
survival, and every EMC cohort is small enough that absence of response is weak evidence. What makes
it worth registering as a route is that it is the one place in this portfolio where the intervention
needs no discovery, no synthesis, no delivery vehicle and no collaborator, and where the mortality it
would act on may be **iatrogenic rather than oncologic**. The corpus in §2 can count
treatment-attributed deaths; that count is the cheapest next observation in the family.

---

## 4a · Treating the patient's other conditions as EMC therapy — ✅ MODELLED 2026-09-04, four factors, compartment B only

**The idea (trimcrae, 2026-08-09).** If a common, independently treatable condition raises the chance
of dying after an EMC diagnosis, then the drug for that condition is a **de-facto EMC survival drug
for the patients who have it** — a GLP-1 receptor agonist for the obese, and the same shape for
smoking, hypertension, diabetes and deconditioning. No EMC biology, no molecule to discover, and the
drug is already in a pharmacy.

**⛔ FIRST, THE STRUCTURAL FACT THAT DETERMINES HOW THIS CAN BE ANSWERED AT ALL: EMC's evidence base
contains no host factor whatsoever.** Every prognostic factor in the registry is a property of the
**tumour** (size, grade, fusion partner, stage, site) or of its **treatment** (resection
completeness); the per-patient schema carries age and sex and nothing else about the person.

⚠ **AND THE HIT COUNT THAT LOOKED LIKE IT CONTRADICTED THAT DOES NOT — WHICH IS THE SAME DISCIPLINE
RUNNING IN REVERSE.** The query `EMC AND (obesity OR BMI OR diabetes OR smoking OR comorbidity OR
"performance status" OR sarcopenia OR frailty)` returns **195**, and the first reading of that number
was that more host-factor material existed than the registry's curation suggested. Inspecting the
hits refutes it: they are EMC **case reports** that mention "ECOG performance status" in their
methods, a spontaneous-regression report, an intracranial case report, a genomic-panel paper, and
general sarcoma series matching on the `OR` arm alone. **Not one is an analysis of a host factor
against EMC outcome.** ⛔ *A populated hit count is not a reading of presence*, exactly as an absent
reading is not a reading of absence — a loose `OR` query measures term co-occurrence, and only
reading tells you whether the terms were doing any work. The registry's own curation, which found
zero host factors among the prognostic variables, remains the better evidence. Superseded, retained:
the reading of **195** as evidence that EMC host-factor analyses exist.

**The model is two compartments, and keeping them apart is the whole discipline**
([`emc_host_factor_model.py`](./emc_host_factor_model.py)):

| | what it is | share of deaths | how well does outside evidence transfer? |
|---|---|---:|---|
| **A** | death **caused by EMC** | ~60 % | ⛔ **badly.** No EMC evidence exists; sarcoma evidence is thin and confounded. Default is that **nothing is claimed** |
| **B** | death from **everything else** | ~40 % | ✅ **well.** These are ordinary deaths in ordinary people — general-population evidence applies with the weakest assumption in this repository |

> ⭐ **THE ASYMMETRY IS THE FINDING, AND IT INVERTS THIS PROGRAMME'S USUAL PROBLEM.** Every antitumour
> route here is blocked on EMC-specific evidence that cannot be obtained without a wet lab or a
> clinic. **Compartment B needs no EMC-specific evidence at all.** Its transfer assumption is *"EMC
> patients die of heart disease at roughly the rate their age and sex predict"* — far weaker than
> *"a ligand designed into a cryptic pocket will be paralogue-selective"*, which the flagship route
> has spent most of this repository's effort failing to establish.

> ✅ **AND THAT ASSUMPTION IS NO LONGER AN ASSUMPTION — §1's background check MEASURED IT.** Observed
> non-EMC deaths run at **0.97×** and **1.04×** the general-population rate for this cohort's age and
> sex. The transfer compartment B depends on is the one thing in this whole analysis that has been
> checked against data rather than argued. ⚠ On 4 events and 1 event, so it is *consistency*, not
> equality — but it is the right direction and it is more than any antitumour route here can say
> about its own central assumption.

**⚠ And the honest consequence cuts the claim down, which is why it is stated here rather than in a
footnote.** Acting on compartment B alone, a host-factor intervention can only ever touch the ~40 %
of deaths that are not EMC deaths. **It is not a cancer treatment and must never be presented as
one.** The headline is never *"this cures EMC"* — it is *"this is worth a defined and modest number
of percentage points, to a defined subgroup, at a cost of zero new science"*. That is a real thing to
be able to say about an ultra-rare disease with no approved targeted agent, and it is a smaller thing
than it first sounds.

**⛔ THE CAUSAL HAZARDS ARE RETRIEVED ON PURPOSE, NOT ADDED AS A CAVEAT.** A naive reading of "body
mass versus survival in cancer" reproduces the **obesity paradox**, in which low weight looks lethal
because *the disease causes the weight loss* rather than the reverse. **An analysis blind to that
would recommend weight gain to cancer patients** — a confident, harmful, and entirely plausible-looking
output. So the probe retrieves the reverse-causation, collider-bias, immortal-time, healthy-user and
Mendelian-randomisation literature *alongside* the association literature, and the model carries a
**bias registry** that every factor must declare against. ⚠ **A row declaring no biases is flagged as
unanalysed rather than clean** — silence about bias must not read as absence of bias, and that is the
row most likely to be quoted and least likely to be right.

**⛔ No effect size, PMID or prevalence appears in this section until the retrieval returns it**, for
the reason in §3. The model refuses to run on any identifier absent from the committed artifact.

**✅ THE RETRIEVAL WAS READ AND THE MODEL HAS RUN (2026-09-04, AUT-220).** Every effect size lives in
[`emc-host-factor-inputs.json`](./emc-host-factor-inputs.json), transcribed from the abstract of a
paper the probe returned, with the population it was measured in and the verbatim sentence beside it;
[`emc-host-factor-model.json`](./emc-host-factor-model.json) is the run. **Four factors were entered
and none of the numbers below should be quoted without the row's caveat** — the table is a reading of
that file, regenerated by the model script, never edited here.

| factor | intervention | compartment B (ordinary death) | compartment A (EMC death) | share of ALL cohort deaths averted, band |
|---|---|---|---|---:|
| obesity | GLP-1 receptor agonist | modelled — all-cause mortality in heart-failure RCTs, low certainty, the dedicated HF trials ran the other way | nothing retrieved | 0.5 – 3.3 % |
| current smoking | cessation | modelled — quitting at a *lung-cancer* diagnosis, observational; transfers as direction and order of magnitude only | nothing retrieved | 0.5 – 1.4 % |
| statin-eligible cardiovascular risk | statin | modelled — **cardiovascular** death only, so this band is an upper-bound shape, not an estimate | a sarcoma PFS association, **recorded at zero** | 0.6 – 5.4 % |
| sarcopenia | exercise and nutrition | an association only, **recorded at zero** | the one sarcoma-specific host-factor estimate in the retrieval — an OS association in patients whose tumour and chemotherapy cause the muscle loss — **recorded at zero** | 0 |

**What the run says, at its true weight.** Acting on compartment B alone, the three modellable factors
each touch **under a twentieth of the cohort's deaths over a decade**, and only for the patients who
carry the factor. That is the "defined and modest number of percentage points" the framing above
predicted, now with a retrieved number behind it. ⚠ **Three things keep it from being more than a
band.** *(1)* Every prevalence is imported from a US general-population survey and is an assumption,
because no EMC series records one. *(2)* The retrieval's hits are relevance-ranked 2025–2026 syntheses
and cohorts, **not the landmark trials** — those were not returned and could not be entered without
a fetch. *(3)* **The sarcoma-specific evidence is all association.** A CT-defined sarcopenia hazard
ratio near two in sarcoma patients is exactly the estimate the bias registry exists to refuse: the
cancer and its chemotherapy cause the muscle loss, so the sign survives even if the intervention does
nothing. The model carries every such row as `ASSOCIATION_ONLY` at zero, which is the honest reading.

**Not entered, and why:** diabetes and hypertension — the probe's top hits held no usable estimate for
either, and the probe has no blood-pressure query at all. That is a re-query, queued, not an
assumption.

---

## 5 · What is registered, and where each piece lives

| id | question |
|---|---|
| `ST-MORTALITY-MECHANISM` | the family — start from the death, not the driver |
| `RT-COMPETING-MORTALITY` | the ~40 % of deaths that are not EMC deaths |
| `RT-RESPIRATORY-FAILURE` | the dominant *disease* mechanism, and whether its course is symptom-treatable |
| `RT-TREATMENT-HARM` | mortality caused by treatment rather than tumour |
| `RT-EARLY-PALLIATIVE` | the only non-antitumour class with randomised survival evidence in oncology |
| `RT-VTE-PROPHYLAXIS` | plausible, acute, and probably small — carried because a portfolio that registers only what it expects to find is not a census |
| `RT-HOST-FACTOR` | ⭑ treating the patient's *other* conditions as EMC survival therapy — the only route whose drug already exists and needs no EMC evidence to act |
| `PUB-MORTALITY-MECHANISM` | the endpoint all six feed |

**One home for each fact.** Clinical figures: [the registry](../data/emc-clinical-registry.json).
The decomposition: [`emc-mortality-decomposition.json`](./emc-mortality-decomposition.json), from
[declared inputs](./emc-mortality-decomposition-inputs.json) that carry the verbatim registry string
behind every value — so a registry correction cannot silently leave a stale figure here. The
retrieval: ⏳ `research/literature/emc-mortality-probe.json` — **not yet on disk**, and deliberately
left as a path rather than a link until the run that writes it lands, because a link to a file that
does not exist reads as an artifact that does. Route state:
[`systems/graph/routes.json`](../../systems/graph/routes.json).

---

## Appendix A — superseded and corrected

- ⛔ **The headline competing share was 39.4 % and is now 21.7 % at ~3 years / 30.8 % in the localised
  stratum.** The first figure came from the *weakest* available estimator — Meis-Kindblom 1999's
  10-year all-cause curve paired against a crude disease-death proportion over a different horizon —
  because it was the only within-series pairing the curated registry could support. The mortality
  probe then retrieved Masunaga 2025's full text, which reports both cause counts on the same
  patients, and that supersedes it. Superseded, retained: **39.4 %**, and the description of
  Meis-Kindblom as *"the only series measuring both on the same patients"*, which was true of the
  registry and never true of the literature. Live figures: §1.
- ⛔ **The antitumour ceiling was stated as a single 15–18 points and is now stratum-dependent: 6.7
  points localised, 31.0 metastatic.** The single figure averaged across strata that differ by a
  factor of five, which hid the finding. Superseded, retained: **"~15–18 points"** as a whole-cohort
  10-year figure.
- ⛔ **The background-mortality check reported `OK` with a figure roughly four times too low.**
  Measured 2026-08-09 (run `31335519304`): 2.4 % ten-year all-cause mortality from age 55, against a
  real US figure near 11 %. The WHO indicator serves an annual **rate** and the code used it as a
  five-year **probability**. The artifact was populated, internally consistent and plausible — the
  precise shape of failure this repository has recorded before. Fixed twice over: the indicator's
  name is now read from the API and the rate-versus-probability decision made from it, and a
  known-answer sanity band rejects any result outside what basic demography guarantees. Superseded,
  retained: **2.4 %**.

- **The cross-series competing share was first computed from the two EXTREME pairings and read
  −25 % to 57 %.** A negative share is arithmetically impossible and was appearing as a lower bound.
  Every pairing is now enumerated; impossible and undefined ones are counted and excluded from the
  band rather than trimmed from it, because each is a cross-population pairing demonstrating its own
  limit. Superseded, retained: **−25 % to 57 %**. Live figures: §1.
- **A no-death cohort paired against real disease deaths was first classified `undefined`.** It is a
  *contradiction* — there cannot be deaths from a cause in a population with no deaths — and belongs
  with the impossible pairings, which is the louder signal. Only a genuine 0/0 is undefined.
