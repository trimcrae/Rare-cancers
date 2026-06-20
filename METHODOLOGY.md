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

## 3. Checklist when adding registry data

- [ ] Each new source added to `registry.citations` with ≥1 resolvable id + url + license.
- [ ] Each patient/cohort uses `sourceId` (and `primaryRef` + `provenance:"secondary"` if read from a review).
- [ ] Pooled cohorts have explicit `{events, denom}`, confirmed EMC, non-overlapping population, outcome ≠ inclusion criterion.
- [ ] Overlapping / percentage-only / different-endpoint series set `pool:false` + `contextReason`.
- [ ] `node scripts/validate.mjs` and `node scripts/smoke-render.mjs` pass.
