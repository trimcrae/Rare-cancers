# Pooled outcomes of extraskeletal myxoid chondrosarcoma: a reproducible systematic review and meta-analysis

**Status: DRAFT skeleton v0.1 — pre-clinician-review, not for submission.**
Authors: TBD (must include a sarcoma clinician/methodologist). Results below are
auto-generated from the project dataset and require the statistical upgrades in
`PROTOCOL.md` §6 before submission. Numbers current as of the last data build —
regenerate from `data/cancers/emc.json` before any version is circulated.

## Abstract (structured) — *to finalize*
- **Background:** EMC is an ultra-rare NR4A3-rearranged sarcoma; outcome data are
  scattered across small retrospective series.
- **Methods:** reproducible Europe PMC search; pooled crude proportions with Wilson
  95% CIs over non-overlapping, explicit-count cohorts; era and overlap handled
  pre-specified. *(Random-effects + I² upgrade pending.)*
- **Results (current):** pooled local recurrence **27% (95% CI 22–32%, n=330)**,
  distant metastasis **36% (30–42%, n=262)**, crude disease-specific survival
  **86% (82–90%, n=266)**, across **393 pooled patients** (5 cohorts + 4 individual
  cases). Time-anchored survival summarized per study, not merged.
- **Conclusions:** *to write* — EMC carries a high long-term recurrence/metastasis
  burden with relatively preserved disease-specific survival; estimates are
  era-sensitive and should be read as a conservative floor.

## 1. Introduction — *to write*
Rarity, NR4A3 biology, the indolent-but-metastasizing phenotype, why a reproducible
pooled synthesis is needed, and the unmet need this addresses.

## 2. Methods
Summarize `PROTOCOL.md`: eligibility; Europe PMC search (exact query) and triage;
extraction into the structured registry; **PRISMA flow diagram (TODO)**; risk-of-bias
(TODO); pooling = crude denominator-weighted proportions + Wilson 95% CI, with the
planned random-effects/I², forest plots, and sensitivity analyses (leave-one-out;
registry-only vs all-series; **era-stratified**; molecular-confirmed only).

## 3. Results (auto-generated — regenerate before circulating)
### 3.1 Included studies
Pooled cohorts: Masunaga 2025 (Japan national registry, localized n=134 + metastatic
n=29, dx 2002–2022); Meis-Kindblom 1999 (n=117); US Sarcoma Collaborative (n=60, dx
2000–2016); Chiusole 2020 (Europe, n=49 curative-intent, dx 1980–2018); plus 4 cited
individual case reports. Context (not pooled — overlap / percentage-only /
different-endpoint): SEER 2004–2015 (n=270), Drilon 2008 (n=87), U Michigan (n=44),
Japan 2003 (n=42), China 2016 (n=40), Bishop, SEER/Kemmerer, Giner, pazopanib phase 2.

### 3.2 Pooled estimates (crude, Wilson 95% CI)
| Outcome | Pooled estimate | 95% CI | n (events/at-risk) |
|---|---|---|---|
| Local recurrence | 27% | 22–32% | 330 |
| Distant metastasis | 36% | 30–42% | 262 |
| Disease-specific survival (crude) | 86% | 82–90% | 266 |

*Forest plots and I² to be added with the random-effects upgrade.*

### 3.3 Heterogeneity & era
Between-study local-recurrence rates ranged widely (registry ~12% vs consultation
series ~48%), reflecting selection and era. Underlying diagnoses span 1972–2026;
pre-specified era-stratified sensitivity analysis **TODO**.

### 3.4 Contested questions
Radiotherapy and adjuvant chemotherapy in localized EMC: opposing findings driven by
indication bias (see the project's `evidenceQuestions`). Presented as adjudicated
controversies, not pooled effect estimates.

## 4. Discussion — *to write*
Interpretation; comparison to prior single-series reports; the era/temporal-validity
argument; clinical implications (margins, surveillance length).

## 5. Limitations — *to write*
Small retrospective evidence base; crude (interim) pooling; residual population
overlap; publication bias; no IPD for most cohorts.

## 6. Reproducibility
Search, triage, extraction and pooling are scripted (`scripts/fetch-paper.mjs`,
`triage-literature.mjs`, `validate.mjs`; data in `data/cancers/emc.json`). Commit
hash to be cited in the final manuscript.
