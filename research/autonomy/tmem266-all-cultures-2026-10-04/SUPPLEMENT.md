---
id: DOC-TMEM266-CULTURE-SUPPLEMENT-20261004
title: Culture census supplement to the TMEM266 tissue RNA analysis
level: L3
kind: manuscript
status: live
purpose: Add complete recovered culture coverage and new measurements to the preserved tissue methods.
scope: Exploratory public-data analysis and explicit source gaps.
audience: [maintainers, collaborators, external reviewers]
date: 2026-10-04
last_verified: 2026-10-04
---

# Supplementary methods and culture coverage

The [previous supplementary methods](../tmem266-questions-2026-10-04/SUPPLEMENT.md) remain the methods for the tissue cohorts, arrays, detector products, normal-muscle analyses and USZ23 transcript work. Their source files and results are preserved unchanged. The current [draft](DRAFT.md) adds the culture census and qualifies the breadth of model expression; it introduces no new tissue cohort or patient count.

The full [culture table and methods](COVERAGE.md) accounts for all six named candidates recovered in this bounded search, historical short-term preparations, and engineered models. [PLAN.txt](PLAN.txt) records target and resource decisions before the relevant new expression values. [REVIEW.txt](REVIEW.txt) records the independent scientific checks.

The new exact numerical results and executable analyses are:

- [ARCHS4 subset extraction](extract_archs4.py), [results](archs4-results.json), [retained source archive](archs4-subset.zip) and [live request replay](retrieve_archs4.py). Source: [ARCHS4](https://archs4.org/download), [GSM6883080](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM6883080) and [GSM2113301](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM2113301).
- [USZ22 fixed-anchor pilot](usz22_prefix.py) and [lead replay](usz22-prefix-replay.json). All four predefined anchors had zero hits in the limited prefixes; no expression-absence conclusion follows.
- [Disputed-model expression extraction](disputed_model_expression.py) and [results](disputed-model-expression.json). Dataset: public DepMap Expression (Short-read) 26Q1; [identity qualification](https://pmc.ncbi.nlm.nih.gov/articles/PMC8571037/).
- [Davila full series census](davila_census.py), [source metadata/results](davila-census.json), [additional source receipts](source-search-receipts.json) and [bounded search replay](replay_source_searches.py).

Raw-expression uncertainty is not captured by a gene count alone. USZ22 has one library, no biological replicates, a rounded pseudocount estimate and no target-specific validation; no biological or Poisson confidence interval is reported. The full matrix includes duplicate symbols, and CPM is explicitly relative to the sum of every returned row. We do not compare its magnitude with USZ23 TPM, V1-34 regional coverage or transformed DepMap expression. Missing deposits and absent rows in selected tables are not zero-expression measurements.

The strongest next culture experiment is transcript-resolved validation in USZ23, with upstream/downstream assays and controls, followed by direct protein measurement. For extending coverage, obtaining authenticated USZ20 and NCC1 expression data and a USZ23 donor crosswalk would be valuable; no outreach is authorized or underway. The trace USZ22 assignment should not motivate a claim of common high expression across EMC cultures.
