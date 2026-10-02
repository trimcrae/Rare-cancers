# Proposed manuscript additions and integration notes

These edits concern the draft at
research/autonomy/data-opportunities-2026-09-30/drafts/registry-response-unit-short-report.md,
reviewed at da49c4e836533253825587f83656675dac4c913b.
They do not change the frozen 552 parent-table / 575 class-group-row audit counts.

## Prior-art context for Introduction

Automated extraction and structured reuse of ClinicalTrials.gov results are established
approaches. EXACT extracted quantitative data for meta-analysis, while subsequent work
linked arm-level efficacy and safety results. Our narrower contribution is a
source-reconciled correction of one oncology response corpus, with explicit cases
demonstrating how category qualification, class boundaries and denominator scope affect
extracted quantities.

Primary references:
- Pradhan R, Hoaglin DC, Cornell M, Liu W, Wang V, Yu H. Automatic extraction of quantitative
  data from ClinicalTrials.gov to conduct meta-analyses. Journal of Clinical Epidemiology.
  2019;105:92-100. https://doi.org/10.1016/j.jclinepi.2018.08.023
  Institutional abstract: https://research.monash.edu/en/publications/automatic-extraction-of-quantitative-data-from-clinicaltrialsgov-/
- Shi X, Du J. Constructing a finer-grained representation of clinical trial results from
  ClinicalTrials.gov. Scientific Data. 2024;11:41.
  https://www.nature.com/articles/s41597-023-02869-7
  Their efficacy extraction concerns statistical analyses and comparison-group
  relationships; it is not the same as this literal category-count audit.

This focused search does not establish exhaustive novelty. Do not claim the first
structured registry extraction or that other extraction systems share our parser defects.

## Small Methods wording repair

Replace the sentence beginning "Recovery retained outcome descriptions..." with:

The pinned source payloads retain complete outcome descriptions and measurement metadata.
The recovered tables retain time frames, population descriptions, results-group
identifiers, literal categories, class boundaries and posted denominators.

Reason: registry_response_complete_reconciliation.py retains unitOfMeasure but its
literalTables omit description, paramType and full measurement metadata. The original
normalization also omits unitOfMeasure. These remain in the pinned raw source payloads.
This is a metadata/export wording issue, not a challenge to the recovered integer counts.
The new conformance utility retains complete outcome and measurement objects but should
not be described as having retroactively changed the existing 575-row artifact.

## Denominator-consequence example for Results

For the differentiated class, CR plus PR was 16, whereas the four selected categories
summed to 39 and the posted class denominator was 44, including five participants reported
as not evaluable. The corresponding arithmetic fractions were 41.0% and 36.4%. This
illustrates the consequence of denominator substitution; it does not establish which
response estimand should be used for clinical comparison.

Exact arithmetic: 16/39 = 0.41025641025641024; 16/44 = 0.36363636363636365;
difference = 4.66200466200466 percentage points.

Source: NCT00654238, outcome 0, group OG000, class 0 ("Differentiated").
Archived source: ctg_results_bor_1999_2009.txt, study index 127, at source revision
216bd1b5fb25a56b90ef3cc2373e1fe68322708f; exact original-byte SHA256 in sources.json.
The source population description specifies total enrolled by histological subtype.
Current corroborating source: https://clinicaltrials.gov/api/v2/studies/NCT00654238
lastUpdatePostDate 2019-11-18. Retain archived provenance for frozen numerical claims.

## New outcome-local identity example for Discussion or supplement

A results-group identifier alone does not identify a trial-wide treatment arm. In
NCT00942162, OG000 identifies the GS-positive group in Best Overall Response (BOR) by GS,
but identifies the overall study group in Duration of Response (CR or PR).
Preserving outcome scope prevents an otherwise plausible group-ID join from mixing
different analysis populations.

Actual source selectors:
- outcome index 7, OG000: GSK2132231A GS+ Group; posted participants 71.
- outcome index 8, OG000: Overall Study Group; posted participants 4.

Source: https://clinicaltrials.gov/api/v2/studies/NCT00942162;
lastUpdatePostDate 2020-12-08. Both are expected in archived
ctg_results_bor_1999_2009.txt, study index 4. Final archived conformance is pending CI.

## Validation statement

Seven explicitly synthetic behavior checks passed using the bundled standard-library
Python runtime, without file writes. Four real case groups passed against three live
API responses at 2026-10-02T12:30:32Z, covering class scope, SD/PR qualification,
unconfirmed-remission qualification and outcome-local group identity. These are known
development cases, not an independent held-out validation sample.

Seven synthetic checks passed after adding an NCT output filter that preserves original
study indices. The live cases ran before that small filter addition. Frozen-source CI
has not yet run; do not report it as passed.

No existing full-corpus aggregate calculations were rerun. No clinical outcomes, registry
error rates, diagnostic performance estimates or therapeutic claims were established.
