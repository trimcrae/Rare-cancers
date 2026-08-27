---
id: DOC-POLICY-EVIDENCE
title: The evidence contract — citing sources and combining studies
level: L0
kind: policy
status: live
canonical_for: [citation structure, study pooling, double-counting, contested evidence, data vintage, study-level descriptive series]
purpose: >
  Define how a clinical fact enters this repository, what may be combined with what, and how
  disagreement and age are represented — so that every clinical number is traceable to a resolvable
  source and combined by one stated method rather than by whichever method the author reached for.
scope: >
  Clinical and epidemiological evidence only — the EMC registry, the manuscript's meta-analysis, and
  any pooled proportion or interval derived from published cohorts. It does NOT govern computational
  results (free energies, poses, ensembles), whose evidence rules live in the roadmap's validation
  architecture.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-05
last_verified: 2026-08-05
aliases: [METHODOLOGY.md]
related: [DOC-ARCHITECTURE, DOC-CONVENTIONS, DOC-RESEARCH-HYPOTHESES-METHODOLOGY]
---
# The evidence contract — citing sources and combining studies

This file is **policy**, not decoration. It is the repository's **evidence
contract**: how a clinical fact enters this project, what may be combined with
what, and how disagreement and age are represented. Two mechanisms keep it
honest — a **structured citation system** (every datum traceable to a resolvable
source) and a **conservative statistical method** (numbers combined in a
defensible, clearly-bounded way). Enforced by
[`scripts/validate-registry.mjs`](../scripts/validate-registry.mjs), which is
gate 10 of `scripts/preflight.sh` — checked against the script's real gate order
by `[P1]`, because this ordinal had four homes and three of them said 2.

> ⚠ **This was written for the patient-facing site and it is not site policy.**
> That framing was misleading and cost a near-miss: this file looked like
> interface tooling while §1, §2.1, §2.3, §3 and §4 are the extraction contract
> the manuscript's meta-analysis ASSUMES and does not re-check. The site is
> retired; the contract is not. Owner of the data:
> [`research/data/emc-clinical-registry.json`](../research/data/emc-clinical-registry.json).
>
> ⚠ **DO NOT CONFUSE THIS WITH
> [`research/hypotheses/METHODOLOGY.md`](../research/hypotheses/METHODOLOGY.md).** Until this file
> moved here on 2026-08-05 it was `METHODOLOGY.md` at the repository root, and the two shared a
> basename — so bare prose references to "METHODOLOGY.md" resolved to whichever one the reader
> guessed, and they are **different contracts**: this one governs clinical evidence (citation
> structure, pooling, Wilson intervals, vintage); that one governs drug-repurposing hypotheses
> (candidate generation, the triage score, the treatment-advice firewall, TxGNN). The move is what
> makes a bare reference unambiguous.

---

## 1. Citing mechanism

### 1.1 Every clinical datum points to a citation by id

Each cancer file carries a `registry.citations` map keyed by a short id
(`masunaga2025`, `remiszewski2025`, …). Every patient row and every cohort
references a citation with `sourceId` (and, where relevant, `primaryRef`)
instead of an inline free-text string. This means:

- citation metadata lives **once** and can't drift between rows,
- the validator can prove every `sourceId` resolves,
- the UI renders a consistent, linked reference list,
- swapping a paywalled secondary source for the primary later is a one-line edit.

### 1.2 What a citation entry must contain

```jsonc
"masunaga2025": {
  "short":   "Masunaga 2025",                 // display label
  "type":    "journal-article",
  "title":   "The role of radiotherapy and chemotherapy in ...",
  "authors": "Masunaga T, Tsukamoto S, Nagano A, et al.",
  "journal": "J Orthop Surg Res",
  "year":    2025,
  "pmcid":   "PMC12398172",                    // >=1 resolvable id REQUIRED
  "doi":     "10.1186/s13018-025-06245-6",     // (pmid | pmcid | doi)
  "url":     "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12398172/",
  "license": "CC-BY-NC-ND-4.0",                // record it; respect it
  "openAccess": true,
  "design":  "retrospective national registry cohort",
  "n":       171,
  "population": "EMC diagnosed 2002–2022, Japanese National ... Registry",
  "accessed": "2026-06-20",
  "verified": true                             // a human/agent confirmed the
}                                              //   link resolves AND supports
                                               //   the specific claim
```

**Hard requirements** (validator-enforced): at least one **resolvable
identifier** (`pmid`, `pmcid`, or `doi`), a `title`, a `year`, and a `url`.
Record the `license`; never reproduce more than it permits (the raw-text
`literature-cache` branch is never served by Pages for this reason).

### 1.3 Primary vs. secondary provenance — never launder a citation

A number read out of a **review** is not the same as a number read from the
**study that produced it**. Conflating them is how false precision spreads.

- `sourceId` is **the document you actually read the number in**.
- If that document is a review/secondary source, set `provenance: "secondary"`
  and record `primaryRef` — a plain-text description of the original study
  (author, year, n). The UI shows it as *"Bishop et al. (n=41) — via Remiszewski
  2025 review."*
- **Do not invent an identifier** (PMID/DOI) for a primary you have not actually
  fetched and verified. Leave it as `primaryRef` text until you pull it; then add
  a real citation entry and repoint `sourceId`.
- `verified: true` is set **only** when the link was opened and confirmed to
  support the exact claim. Auto-fetched but unread → `verified: false`.

---

## 2. Statistical method for combining studies

The pooled headline combines **patient-level event counts** across studies. It is
deliberately simple, conservative, and labelled as crude. It is
**hypothesis-generating, not prognostic** — there is no survival model and no
individual prediction.

> ⚠ **TWO POOLING METHODS EXIST AND THEY ARE NOT INTERCHANGEABLE.** The crude
> denominator-weighted proportions with Wilson intervals described in this
> section were built for the retired interactive filter, and they remain the
> repository's standard interval for simple proportions — a dozen research
> modules cite them by name. The **manuscript** uses a random-effects
> (DerSimonian–Laird) model implemented in
> [`research/meta/meta-analysis.mjs`](../research/meta/meta-analysis.mjs). Quoting
> one where the other is meant is a real error: they answer the same question
> with different assumptions about between-study heterogeneity. §2.1 and §2.3 —
> what may be pooled at all — bind BOTH.

### 2.1 What gets pooled (the `pool: true` set)

A cohort is summed into the headline only if **all** hold:

1. **Confirmed EMC** (molecular/histological), matching the page.
2. **Explicit integer counts** are reported: `{events, denom}`. We never derive
   counts from a published percentage for pooling (rounding invents data).
3. The outcome is a **true outcome, not the inclusion criterion** — e.g. a
   "metastatic at diagnosis" cohort does **not** contribute to the *metastasis*
   rate (its metastasis count is structurally 100%).
4. **Non-overlapping population** (see 2.3).

Everything else — percentage-only series, overlapping populations, different
endpoints — is shown as **context** (`pool: false`): visible in the breakdown
with its own numbers and citation, but **not** added to the headline.

### 2.2 The pooled estimate and its uncertainty

For an event across the included cohorts:

- **Pooled proportion** p̂ = (Σ eventsᵢ) / (Σ denomᵢ). This is a
  denominator-weighted ("fixed-effect"-style) crude pool — larger studies carry
  more weight. Disclose when one study dominates (currently a single national
  registry does).
- **95% confidence interval**: the **Wilson score interval** on (Σevents,
  Σdenom). Wilson is used because it behaves well at small n and near 0%/100%,
  unlike the normal approximation. The UI shows `p̂% (95% CI lo–hi%)`.
- **Heterogeneity**: the per-cohort rates are shown side-by-side and the
  breakdown reports their **range**. A wide range means the pooled point estimate
  hides real between-study variation — treat it with extra caution. (We do not
  compute I²; the honest signal is "look how much the studies disagree.")

### 2.3 Avoiding double-counting

The cardinal sin of pooling is counting the same patient twice.

- **Within a study:** use **mutually exclusive strata** only. Never pool a
  whole-cohort row *and* its sub-strata. Strata of one study share a
  `populationKey` and declare a distinct `stratum`; the validator flags two
  pooled cohorts that share both.
- **Across studies:** single-institution series are often subsets of national or
  SEER registries. Where populations may overlap, the **smaller/overlapping**
  cohort is marked `pool: false` with `contextReason: "population-overlap"`.
  Distinct populations (e.g. a Japanese registry and a US single institution) may
  be pooled.

### 2.4 Endpoints: counts vs. time-to-event

- **Event-rate metrics** (local recurrence, distant metastasis, disease-specific
  death) are pooled as **crude during-follow-up proportions** — labelled "crude,
  mixed follow-up" because cohorts differ in follow-up length and censoring is
  ignored.
- **Time-anchored survival** (5-yr, 10-yr DSS/OS) is **never merged** into one
  number — denominators represent different follow-up. Each cohort's
  time-anchored figure is shown **per row** in the breakdown instead.

### 2.5 Stated limitations (shown to the user)

Publication bias (case reports over-represent unusual/severe disease);
heterogeneous and often short follow-up; no censoring/Kaplan–Meier; no
risk-adjustment or multivariable control; small total N for a rare cancer. The
banner and methodology note say all of this. The figure is a **rough signal,
never a personal prognosis.**

### 2.6 Study-level descriptive series — the second estimand class

Everything above governs one estimand: a **patient-level pooled proportion**, whose unit is a
patient and whose question is *how do patients fare*. A second class exists and was not previously
covered, which meant cross-disease work had no legal form and would have had to borrow §2.1–2.2's
machinery, producing a pooled cross-disease proportion — a weighted average of unlike things,
carrying an interval that misstates its own precision.

A **study-level descriptive series** has as its unit **one arm of one trial**, and its question is
*how does a trial read*. It is the correct form for any analysis that compares reporting or
measurement practice across populations that §2.1 would refuse to pool.

- **(a) No pooled estimate across populations.** Rows are never summed across populations §2.1
  would not allow to be pooled. There is no cross-population point estimate and no confidence
  interval on any cross-population summary.
- **(b) Rows carry explicit integers and their own interval.** §2.1's ban on back-deriving a count
  from a published percentage applies unchanged, and each row gets its own Wilson interval.
- **(c) Permitted summaries: count, median, IQR, range, and counts crossing a pre-stated
  threshold.** Order statistics only. **Prohibited: pooled proportion, inverse-variance or
  random-effects weighting, I², meta-regression, and any significance test across rows.**
- **(d) Rows are unweighted by denominator by default**, because the estimand is how a trial reads
  rather than how patients fare. A denominator-weighted view answers a different question and must
  be labelled as answering it.
- **(e) Deduplication is at arm level** on (registry id, publication id, population key). Companion
  papers, updates and pooled re-reports of one arm collapse to the earliest complete report; the
  rest become dispositions.
- **(f) Time-to-event obeys §2.4** — per row, never merged. A modelling conversion validated in one
  disease (for instance a constant-hazard median↔rate conversion) does not transfer to another and
  may appear only as a labelled display quantity, never as an input to a summary.
- **(g) The corpus must be pre-specified.** Queries, date window, screening rules and the
  extraction rule are committed **before** retrieval runs, with the run ids recorded in the
  artifact. Every screened record carries a disposition, not only the included ones. A descriptive
  label — "indolent", "low-grade", "rare" — may be recorded verbatim from a source as an attribute
  and **may never be used as an inclusion criterion**, because selecting on the description is how
  a corpus comes to confirm the description.
- **(h) Selection bias is bounded by a census taken from the same denominator.** Arms that report
  the quantity being studied may differ systematically from those that do not, and the only honest
  bound on that difference is the size of the non-reporting set. The census is therefore not a
  separate finding; it is the sensitivity analysis, and it must share its denominator structurally
  rather than by assertion.

⚠ **This section widens what may be computed, not what may be claimed.** A descriptive series
supports statements about measurement and reporting. It supports no statement about efficacy,
comparative effectiveness, or any patient's prognosis, and the §2.5 limitations continue to apply
to every row inside it.

### 2.7 Reconstructed patient-level survival — the third estimand class

§2.4 forbids merging time-anchored survival and §2.5 records the consequence in its own words:
*"no censoring/Kaplan–Meier; no risk-adjustment or multivariable control."* Both are correct about
the method §2.2 mandates — a median cannot be averaged and a percentage carries no censoring — and
neither is a statement about the published record, which prints Kaplan–Meier curves this contract
had no legal way to read.

A **reconstructed patient-level survival dataset** has as its unit **one patient-time record**
(a time and an event indicator) recovered from a published curve by the Guyot algorithm
(*BMC Med Res Methodol* 2012;12:9). Its question is *how does risk evolve over time*, which is the
question this disease's indolence makes central and which neither of the first two classes can
express. It is admitted under the conditions below and under no others.

- **(a) A numbers-at-risk table is mandatory.** Without one the per-interval censored count is
  unidentifiable and the reconstruction is assumption rather than inversion. A curve without a
  risk table is **refused, not admitted with a caveat** — a caveat travels badly and a refusal is
  checkable.
- **(b) The reconstruction must reproduce its own input.** The product-limit estimate recomputed
  from the reconstructed records is compared against the digitized survival probabilities, and a
  curve exceeding the stated deviation floor is refused. A reconstruction that cannot reproduce
  the curve it came from has not converged.
- **(c) Digitization provenance is required per curve** — who read the figure and with what tool.
  This is the one hand step in the chain, and an unattributed coordinate is indistinguishable from
  an invented one.
- **(d) §2.1 and §2.3 bind unchanged.** Only non-overlapping populations may be combined, and the
  smaller of any overlapping pair stays `pool: false` with its reason recorded. The SEER analyses
  of this disease overlap each other and overlap institutional series.
- **(e) Permitted: Kaplan–Meier estimates, medians with "not reached" preserved as a NON-NUMBER,
  competing-risks decomposition, and proportional-hazards models with an explicit optimism
  correction.** Prohibited: any covariate-stratified claim where the source published only a
  pooled curve, because a reconstruction recovers times and events and **never covariates**.
- **(f) The reconstruction is labelled as one wherever it appears.** It is a re-expression of a
  published figure, not new patients and not new follow-up, and it inherits every selection and
  publication bias of the source series while correcting none of them.

⚠ **What this class adds is censoring structure, and that is all.** It makes a time-to-event
analysis legal where §2.4 made it a category error; it does not make the underlying series larger,
newer, less selected or better conducted. The §2.5 limitations apply in full to every row.

⛔ **A passing known-answer control on the reconstruction algorithm is not evidence about any
particular curve.** The control in `research/modalities/tests/test_emc_ipd_survival.py` feeds
exact coordinates and therefore bounds algorithmic error alone; it is structurally incapable of
failing on a mis-read figure. Digitization error is bounded per curve by (b), never by the control.

---

## 3. Representing disagreement (contested evidence)

Rare-cancer evidence frequently **conflicts** — small retrospective series reach
opposite conclusions. The wrong response is to pick a winner, or to silently pool
conflicting findings into one confident-looking number. The right response is to
**show the disagreement and explain why it exists.**

Contested clinical questions live in `evidenceQuestions[]`:

```jsonc
{
  "id": "rt-localized-emc",
  "question": "Does radiotherapy improve outcomes in localized EMC?",
  "consensus": "contested",            // consensus-for | consensus-against |
                                       // contested | limited-evidence | emerging
  "summary": "...plain-language synthesis that states the uncertainty...",
  "positions": [
    { "stance": "supports",            // supports | against | mixed | null
      "claim": "10-yr local control 100% vs 63% (surgery+RT vs surgery alone)",
      "design": "single-institution, n=41",
      "sourceId": "remiszewski2025", "provenance": "secondary",
      "primaryRef": "Bishop et al.", "studyPeriod": [1989, 2014],
      "caveat": "Combined-modality patients differ systematically from surgery-alone." },
    { "stance": "against",
      "claim": "No association between RT and local recurrence (HR 0.50, p=0.37)",
      "design": "national registry, n=134", "sourceId": "masunaga2025",
      "provenance": "primary", "studyPeriod": [2002, 2022],
      "caveat": "Indication bias: RT given to higher-risk margins/sites." }
  ],
  "bottomLine": "Guideline-pragmatic stance + an explicit statement of what the data cannot prove."
}
```

**Rules.** Every position carries a real `sourceId` (primary/secondary as in §1).
A question marked `contested` must show **≥2 positions taking opposing stances**
(validator-enforced) — you may not label something contested and then list one
side. Always name the **mechanism of conflict** (indication bias, era effects,
selection, tiny n). The `bottomLine` may give a guideline-based pragmatic stance
but must state what remains unproven. **Never** resolve a genuine controversy
with a fabricated consensus.

**Link to the pool.** When a pooled metric shows wide between-study spread
(§2.2 heterogeneity) and that spread maps onto a known controversy, point the
user to the relevant `evidenceQuestions` entry rather than implying the pooled
point estimate settles it.

## 4. Temporal validity (data ages; prognoses move)

Most rare-cancer outcome data is **retrospective**, often describing patients
diagnosed years to **decades** ago. Cancer care improves (surgery, imaging,
systemic agents — for EMC, anti-angiogenic TKIs are a post-2019 development —
supportive care, stage migration). **Presenting a 5-year survival from patients
treated in the 1990s as a today-patient's outlook is misleading and usually
pessimistic.** This is handled at every step, and generalizes to every cancer.

### 4.1 Anchor on study period, not publication year

Every cohort/citation records `studyPeriod: [firstDxYear, lastDxYear]` — the
years patients were **diagnosed/treated**, which is what determines how current
the evidence is (a 2025 paper can describe 1990s patients). **Record it only
from what the source states; never infer or fabricate it** — mark it absent and
the UI shows "diagnosis period not reported", which is itself useful information.

### 4.2 Surface vintage everywhere

Each breakdown row shows its diagnosis period; the pooled result shows the
**span of diagnosis years** feeding it and flags when it is dominated by old
data. A user-facing **"diagnosed since (year)"** control lets people exclude
cohorts whose data ends before a chosen year, so they can see the most current
slice. (Cohorts spanning an era cannot be split without individual data; that
limitation is stated, not hidden.)

### 4.3 Direction of bias — conservative floor, not ceiling

State explicitly that **older outcome data most likely *understate* the outlook
for someone diagnosed today**, and should be read as a *conservative floor*
rather than a prediction. Point users to current options (`emergingTreatments`,
`clinicalTrials`). But **never silently adjust a number upward** to "correct" for
age — improvement is not guaranteed for a given subtype, and inventing optimism
is as dishonest as inventing pessimism. The correction is **transparency +
stratification + qualitative direction**, never a black-box multiplier. Symmetric
caution: do not over-claim that modern results are better without evidence.

### 4.3 Generalization

`studyPeriod`, vintage display, the "diagnosed since" lever, and the
floor-not-ceiling caveat are generic and apply to every cancer page. Any pooled
survival/recurrence figure on the site must travel with its data vintage.

## 5. Checklist when adding registry data

- [ ] Each new source added to `registry.citations` with ≥1 resolvable id + url + license.
- [ ] Each patient/cohort uses `sourceId` (and `primaryRef` + `provenance:"secondary"` if read from a review).
- [ ] Pooled cohorts have explicit `{events, denom}`, confirmed EMC, non-overlapping population, outcome ≠ inclusion criterion.
- [ ] Overlapping / percentage-only / different-endpoint series set `pool:false` + `contextReason`.
- [ ] Each cohort/citation has `studyPeriod` (diagnosis years) where the source states it; absent if not.
- [ ] Genuinely conflicting findings are an `evidenceQuestions` entry with ≥2 opposing, cited positions and the mechanism of conflict — not pooled into one number.
- [ ] `node scripts/validate-registry.mjs` passes (or `./scripts/preflight.sh`, which runs it).
