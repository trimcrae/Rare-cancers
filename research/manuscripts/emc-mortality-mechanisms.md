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
last_verified: 2026-08-09
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

**The within-series reading — the only one that does not cross populations.** Meis-Kindblom 1999
(n = 117, median follow-up 9 years, PMID 10366145) is the single curated series reporting both a
long-horizon all-cause survival curve and a disease-specific death count *on the same patients*:

| at 10 years | value |
|---|---:|
| all-cause mortality | **30.0 %** |
| of which, EMC deaths | **18.2 %** |
| of which, **not** EMC deaths | **11.8 %** |
| **share of deaths that were not EMC deaths** | **39.4 %** |
| **antitumour ceiling** (points of 10-yr OS a perfect cure would add) | **18.2** |

**The cross-series band.** Pairing every all-cause figure against every disease-specific figure at 10
years: competing share **50–57 %**, ceiling **15.0** points. ⚠ **4 of 6 pairings are coherent and 2
are arithmetically impossible** (disease-specific mortality exceeding all-cause), which is the
pairing telling you it joins studies that cannot describe one population. At **5 years the pairing
breaks down** — only 6 of 12 are coherent — so no 5-year figure is quoted here.

> **⇒ A therapy that prevented EVERY EMC death would raise 10-year overall survival from roughly
> 67 % to roughly 85 %.** Not to 100 %. That ~15–18 points is the ceiling on this repository's
> **entire 68-route portfolio taken together**, and roughly **two of every five deaths in the first
> decade are already outside it**.

**⚠ The one directional bias, stated because it favours this memo's own conclusion.** Disease-specific
survival estimated by censoring other-cause deaths *overstates* the cumulative incidence of disease
death under competing risks. So `1 − DSS` is an over-estimate of EMC's share, and the competing share
above is an **under-estimate**. The bias runs against the argument being made, which is the only
reason subtracting summary percentages across heterogeneous studies is publishable at all.

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

## 3 · What symptom-directed treatment would be worth — ⏳ AWAITING CITED EFFECT SIZES

**⛔ NO EFFECT SIZE IS WRITTEN HERE FROM RECOLLECTION.** This memo names no trial, no percentage and
no PMID for any intervention until the retrieval returns it. That restraint is not fastidiousness: it
is the documented failure mode in CLAUDE.md §7, where an agent drafting a manuscript wrote a citation
from memory, the PMID existed in no committed source, and it **passed `lint_claims` twice** — because
claim *strength* and citation *provenance* are orthogonal, and a hedged sentence on an invented PMID
is a perfect sentence to a linter that reads only hedging.

The probe's third query block asks the questions this section needs answered, and each has a real
`hitCount` waiting: early specialist palliative care and overall survival; structured
patient-reported symptom monitoring and overall survival; thromboprophylaxis in ambulatory cancer;
sepsis-bundle mortality in neutropenic and immunocompromised patients; malignant pleural effusion
management; cachexia intervention; exercise oncology; palliative care in **sarcoma specifically**.

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

## 4a · Treating the patient's other conditions as EMC therapy — ⏳ RETRIEVING

**The idea (trimcrae, 2026-08-09).** If a common, independently treatable condition raises the chance
of dying after an EMC diagnosis, then the drug for that condition is a **de-facto EMC survival drug
for the patients who have it** — a GLP-1 receptor agonist for the obese, and the same shape for
smoking, hypertension, diabetes and deconditioning. No EMC biology, no molecule to discover, and the
drug is already in a pharmacy.

**⛔ FIRST, THE STRUCTURAL FACT THAT DETERMINES HOW THIS CAN BE ANSWERED AT ALL: EMC's evidence base
contains no host factor whatsoever.** Every prognostic factor in the registry is a property of the
**tumour** (size, grade, fusion partner, stage, site) or of its **treatment** (resection
completeness); the per-patient schema carries age and sex and nothing else about the person. So this
question cannot be answered from this disease's own literature, and the retrieval's first query is
aimed squarely at establishing that absence with a real `hitCount` rather than an impression.

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

- **The cross-series competing share was first computed from the two EXTREME pairings and read
  −25 % to 57 %.** A negative share is arithmetically impossible and was appearing as a lower bound.
  Every pairing is now enumerated; impossible and undefined ones are counted and excluded from the
  band rather than trimmed from it, because each is a cross-population pairing demonstrating its own
  limit. Superseded, retained: **−25 % to 57 %**. Live figures: §1.
- **A no-death cohort paired against real disease deaths was first classified `undefined`.** It is a
  *contradiction* — there cannot be deaths from a cause in a population with no deaths — and belongs
  with the impossible pairings, which is the louder signal. Only a genuine 0/0 is undefined.
