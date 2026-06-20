# Protocol: systematic review & meta-analysis of EMC outcomes

Status: **DRAFT v0.1** — pre-registration / pre-clinician-review. This protocol
documents how the pooled EMC outcome estimates on this project are produced, so the
analysis is reproducible and reviewable. It extends the site's `METHODOLOGY.md`.

## 1. Objectives

1. Estimate pooled rates of local recurrence, distant metastasis, and
   disease-specific survival in EMC, with uncertainty intervals.
2. Characterise prognostic factors (stage at diagnosis, surgical margin, tumour
   size, site, fusion partner) qualitatively across studies.
3. Map and adjudicate areas of genuine disagreement (e.g. radiotherapy benefit).
4. Quantify how outcome estimates depend on study era (temporal validity).

## 2. Eligibility criteria

- **Population:** patients with EMC, diagnosed molecularly (NR4A3 rearrangement)
  and/or by accepted histology. Studies of "extraskeletal/extraosseous
  chondrosarcoma" are included only if the entity is EMC (not conventional-type).
- **Designs:** cohorts, registries, and case series reporting outcomes; individual
  case reports pooled separately (n=1 strata).
- **Outcomes:** ≥1 of local recurrence, distant metastasis, disease-specific or
  overall survival, with extractable counts or rates.
- **Exclusions for pooling** (kept as *context*): series reporting only percentages
  without denominators; populations that overlap a larger included dataset
  (e.g. single institutions inside a national/SEER registry); outcomes that are the
  study's inclusion criterion (e.g. metastasis rate in a metastatic-only cohort).

## 3. Information sources & search

- **Source:** Europe PMC REST API (PubMed/PMC), via `scripts/fetch-paper.mjs sync`,
  paginated over the entire result set; every record's metadata + abstract stored,
  open-access full text additionally retrieved. Reproducible and re-runnable in CI.
- **Query (EMC):** `"extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid
  chondrosarcoma" OR "chordoid sarcoma" OR (NR4A3 AND chondrosarcoma)`.
- **Triage:** `scripts/triage-literature.mjs` ranks records by likely
  cohort/outcome content for screening.
- A **PRISMA flow diagram** (records identified → screened → included) is to be
  generated from the corpus index for the manuscript. *(TODO before submission.)*

## 4. Data extraction

Into `data/cancers/emc.json → registry`: `citations` (structured, ≥1 resolvable
id + license + study period), `cohorts` (grouped, with `{events, denom}` counts,
`studyPeriod`, `provenance`, overlap keys), `patients` (IPD). Each datum is
traceable to a source per the citation rules in `METHODOLOGY.md`.

## 5. Risk of bias

*Planned (not yet implemented):* a per-study risk-of-bias appraisal (e.g. adapted
Newcastle–Ottawa for cohorts) covering selection, ascertainment, follow-up
completeness, and confounding (notably indication bias in treatment comparisons).
Consultation/referral series flagged for selection bias.

## 6. Statistical methods

- **Current (implemented):** crude denominator-weighted pooled proportions
  (Σevents/Σdenom) with **Wilson 95% confidence intervals**, over non-overlapping
  explicit-count cohorts; between-study spread reported as a range.
- **Planned upgrade for publication:** random-effects (DerSimonian–Laird or GLMM)
  pooling of proportions with **I² / τ² heterogeneity**, forest plots, and
  sensitivity analyses: (a) leave-one-out, (b) registry-only vs all-series,
  (c) **era-stratified** (diagnosis period), (d) molecular-confirmed only.
- Time-anchored survival (5/10/15-yr) is summarised per study, **not** pooled as a
  single crude proportion (differing follow-up/censoring).

## 7. Temporal validity

Every cohort carries `studyPeriod` (diagnosis years). Outcomes are interpreted as a
**conservative floor**: older data predates current therapy and may understate a
contemporary patient's outlook. Era is a pre-specified sensitivity analysis, never
a silent adjustment.

## 8. Deviations & limitations

Rare-disease evidence is dominated by small retrospective series with heterogeneous
follow-up; pooled crude figures are descriptive, not causal. Overlap between
multi-institution databases and population registries is handled by exclusion to
context, but residual overlap cannot be fully excluded. This protocol and all
deviations are version-controlled in git.
