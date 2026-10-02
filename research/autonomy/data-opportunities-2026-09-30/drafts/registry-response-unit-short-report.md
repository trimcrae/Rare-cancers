---
id: "DOC-DATA-OPPORTUNITIES-2026-09-30-DRAFTS-REGISTRY-RESPONSE-UNIT-SHORT-REPORT"
title: "Preserving categories, classes and denominators in automated oncology response extraction"
level: "L3"
kind: "manuscript"
status: "live"
canonical_for: []
purpose: "Working research draft: Preserving categories, classes and denominators in automated oncology response extraction."
scope: "September 30 measured-data campaign; retain the source qualifications, execution boundaries and historical status stated in the body."
audience: ["maintainers","external reviewers"]
date: "2026-09-30"
last_verified: "unverified"
_backfilled: "true"
---

# Preserving categories, classes and denominators in automated oncology response extraction

## Abstract

We reconciled every record in a frozen 552-record oncology extraction corpus with archived ClinicalTrials.gov source data and replayed its producer. All records had exact source-table matches. The source material comprised 552 distinct outcome–results-group tables, 564 physical query occurrences and 169 distinct outcomes from 138 trials. Preserving population classes yielded 575 class–group rows: 537 contained one integer exact alias for each of four response categories, and 38 required literal adjudication. Twenty-seven normalized rows differed from their inherited count vector, encompassing 14 parent tables in eight trials. Prefix matching let qualified categories overwrite unqualified counts; class traversal let later subgroups overwrite earlier ones. The audit supplies an executable correction for this extraction corpus. It does not estimate a registry error rate or compare treatment efficacy.

## Introduction

A registry response table identifies an assessment, population and observation period as well as a treatment. ClinicalTrials.gov can legitimately report several outcomes for one results group or several population classes within one outcome. An extracted vector of complete response (CR), partial response (PR), stable disease (SD) and progressive disease (PD) can lose these distinctions while retaining numbers that each appeared in the source.

We audited an existing public corpus and its producer.[1,2] Our aim was to recover the source unit and test whether category assignment preserved literal counts. This exploratory audit covers the realized oncology corpus, including hematological malignancies, rather than an adjudicated set of independent treatment arms.

## Methods

The corpus and producer were pinned to revision af7211708205b5189d8c537c1ce2a23aa4bea076. The inherited retrieval used best-overall-response and oncology-placebo queries across five date windows. We read all ten archived payloads at revision 216bd1b5fb25a56b90ef3cc2373e1fe68322708f.[3] Source identity comprised trial identifier, complete outcome object and results-group identifier. Identical objects repeated across queries retained their physical occurrences without becoming independent tables.

We reproduced the producer's prefix recognition and integer assignment. Its compact key comprised trial identifier, outcome title, results-group title and four-category sum. Every record was mapped to all exact count-vector matches; same-key candidates with different vectors remained separate. Recovery retained outcome descriptions, time frames, population descriptions, group identifiers, all categories, class boundaries and posted denominators.

We then normalized categories separately within each class–group row using explicit exact aliases. A row qualified for four-count normalization only when each retained category had exactly one integer exact alias. Qualified and unrecognized labels remained literal. We did not infer absent categories as zero, merge ambiguous labels or sum potentially overlapping classes. Posted class denominators were retained; an overall denominator was eligible only for a single-class table. A four-category sum remained a separate field, not a validated population denominator.

## Results

All 552 compact records had exact archived count-vector matches. They mapped to 552 distinct outcome–results-group tables and 564 physical query occurrences, representing 169 distinct outcomes from 138 trials. Recovery distinguished repeated query copies from separately reported populations and assessments.

Ten parent tables contained multiple classes, producing 33 class–group rows. Across all parents, class preservation yielded 575 rows. Of these, 537 had four unambiguous exact-alias integer cells; 38 retained literal categories for adjudication. Twenty-seven normalized rows differed from inherited vectors, covering 14 parent tables in eight trials. Four changed rows came from single-class tables. These are different units; 27/552 would not be an extraction-error rate.

In NCT00942162, "SD/ PR" followed "SD" in the source. Prefix recognition assigned both to SD, and the later assignment overwrote the earlier count. The inherited SD counts of 3 and 0 became the literal SD counts of 11 and 4. The combined category, with counts of 3 and 0, remained separate. This correction preserves source labels without deciding whether the combined category belongs in a clinical response estimate.

In NCT00654238, one outcome contained four histological classes. The producer retained the final class's vector, 0/0/0/1. Class preservation recovered the preceding vectors and their denominators (Table 1). The source also retained not-evaluable participants. Applying the overall denominator of 55 to any one class would describe a different quantity.

**Table 1. Class-specific counts in the archived NCT00654238 outcome.**

| Literal class title | CR | PR | SD | PD | Posted participants | Not evaluable |
|---|---:|---:|---:|---:|---:|---:|
| Differentiated | 0 | 16 | 22 | 1 | 44 | 5 |
| Poorly Differenitated | 0 | 2 | 1 | 1 | 6 | 2 |
| Medullary | 0 | 1 | 2 | 0 | 3 | 0 |
| Anaplastic | 0 | 0 | 0 | 1 | 2 | 1 |

The spelling of the second class is preserved from the source. The parent outcome concerns best response to BAY 43-9006 in metastatic thyroid carcinoma.

In two NCT01403948 tables, "Complete remission" with count one was followed by "Complete remission unconfirmed" with count zero. Prefix assignment replaced the unqualified category with the qualified category. Exact normalization restored the literal complete-remission count while keeping the qualification separate.

Within the 33 multi-class rows, class-level denominators were available in 31 rows; two rows had missing or ambiguous eligible denominators. Across the corpus, four retained categories summed to a posted denominator in 250 rows. Arithmetic equality does not validate a clinical response partition, disjoint populations or outcome comparability.

A companion archived search comparison found 23 versus 24 records when both the search field and query expression changed. The additional EMC R1507 record concerns an already published result. This is a source-findability example; it cannot isolate a search-field effect or estimate retrieval sensitivity. It is retained as a companion to the unit audit.

## Discussion

Complete source recovery exposed two reproducible producer behaviors: qualified-label overwriting and subgroup overwriting. Recovering class-specific counts changes both the values and their analysis unit. The contribution is an executable correction grounded in every archived source match.

Reusable response data should preserve trial, outcome, results-group and class identifiers; literal categories; assessment and population descriptions; time frames; every posted denominator; and source-occurrence receipts. Normalized counts should be additional fields with explicit recognition rules. Ambiguous rows should remain available for adjudication, and selected-category totals should remain separate from posted denominators.

The audit is limited to tables selected by the inherited corpus. It does not measure recall across all response outcomes, adjudicate every clinical response definition or establish independent patient populations. The changes arise from the frozen extraction program, not errors by registry contributors. Within that scope, a complete source map and class-preserving alternative make the result independently reviewable.

## Data and code availability

The original corpus, producer and archived inputs are pinned publicly.[1–3] The [complete source map](../deep-analysis/results/registry-complete-matches-actual.json) and [complete 575-row normalization](../deep-analysis/results/registry-complete575-class-preserving-normalization-final.json) preserve literal tables, recognized counts, ambiguous cells and denominators. Executable recovery and normalization are [registry_response_complete_reconciliation.py](../deep-analysis/registry_response_complete_reconciliation.py) and [registry_class_preserving_normalization.py](../deep-analysis/registry_class_preserving_normalization.py). The normalization completed in [workflow run 36880897541](https://github.com/trimcrae/Rare-cancers/actions/runs/36880897541), job 110432170241. Numerical source claims concern archived payloads, not mutable live registry pages.

## References

1. Frozen oncology endpoint corpus. https://github.com/trimcrae/Rare-cancers/blob/af7211708205b5189d8c537c1ce2a23aa4bea076/research/manuscripts/endpoint/endpoint-corpus.json
2. Frozen corpus producer, endpoint_corpus.py. https://github.com/trimcrae/Rare-cancers/blob/af7211708205b5189d8c537c1ce2a23aa4bea076/research/manuscripts/endpoint_corpus.py
3. Archived ClinicalTrials.gov payloads. https://github.com/trimcrae/Rare-cancers/tree/216bd1b5fb25a56b90ef3cc2373e1fe68322708f/literature/xdisease-ctg-results
