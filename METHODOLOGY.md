# METHODOLOGY.md — citing sources & combining studies

This file is **policy**, not decoration. The patient registry and its pooled
"what happened to people like me?" figures are the most dangerous part of the
site: a number that *looks* authoritative can mislead a frightened person. Two
mechanisms keep it honest — a **structured citation system** (every datum is
traceable) and a **conservative statistical method** (numbers are combined in a
defensible, clearly-bounded way). Both are enforced by `scripts/validate.mjs`
and rendered by `assets/js/cancer.js`. Read this before touching `registry`.

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

The pooled headline answers "of patients like me, how many had X?" by combining
**patient-level event counts** across studies. It is deliberately simple,
conservative, and labelled as crude. It is **hypothesis-generating, not
prognostic** — there is no survival model and no individual prediction.

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
- [ ] `node scripts/validate.mjs` and `node scripts/smoke-render.mjs` pass.
