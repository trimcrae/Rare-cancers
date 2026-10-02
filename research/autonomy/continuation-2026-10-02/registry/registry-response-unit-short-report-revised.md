---
id: "DOC-CONTINUATION-2026-10-02-REGISTRY-REGISTRY-RESPONSE-UNIT-SHORT-REPORT-REVISED"
title: "Preserving categories, classes and denominators in automated oncology response extraction"
level: "L3"
kind: "manuscript"
status: "live"
canonical_for: []
purpose: "Working research draft: Preserving categories, classes and denominators in automated oncology response extraction."
scope: "October 2 continuation; limited to the named sources, computations and review scope recorded in the body. No submission clearance."
audience: ["maintainers","external reviewers"]
date: "2026-10-02"
last_verified: "unverified"
_backfilled: "true"
---

# Preserving categories, classes and denominators in automated oncology response extraction

## Abstract

We reconciled every record in a frozen 552-record oncology extraction corpus with archived ClinicalTrials.gov source data and replayed its producer. All records had exact source-table matches. The source material comprised 552 distinct outcome–results-group tables, 564 physical query occurrences and 169 distinct outcomes from 138 trials. Preserving population classes yielded 575 class–group rows: 537 contained one integer exact alias for each of four response categories, and 38 required literal adjudication. Twenty-seven normalized rows differed from their inherited count vector, encompassing 14 parent tables in eight trials. Prefix matching let qualified categories overwrite unqualified counts; class traversal let later subgroups overwrite earlier ones. The audit supplies an executable correction for this extraction corpus. It does not estimate a registry error rate or compare treatment efficacy.

## Introduction

A registry response table identifies an assessment, population and observation period as well as a treatment. ClinicalTrials.gov can report outcome-specific populations and several classes within an outcome. An extracted vector of complete response (CR), partial response (PR), stable disease (SD) and progressive disease (PD) can lose these distinctions while retaining numbers that each appeared in the source.

Automated extraction and structured reuse of registry results are established approaches. EXACT extracted quantitative data for meta-analysis, and subsequent work linked arm-level efficacy and safety results.[4,5] Our narrower contribution is a source-reconciled correction of one oncology response corpus, with explicit examples of category, class and denominator handling. We audited its frozen producer to recover the source unit and test preservation of literal counts.[1,2] This exploratory audit covers the realized corpus, including hematological malignancies, rather than an adjudicated set of independent treatment arms.

## Methods

The corpus and producer were pinned to revision af7211708205b5189d8c537c1ce2a23aa4bea076. The inherited retrieval used best-overall-response and oncology-placebo queries across five date windows. We read all ten archived payloads at revision 216bd1b5fb25a56b90ef3cc2373e1fe68322708f.[3] Source identity comprised trial identifier, complete outcome object and results-group identifier. Identical objects repeated across queries retained their physical occurrences without becoming independent tables.

We reproduced the producer's prefix recognition and integer assignment. Its compact key comprised trial identifier, outcome title, results-group title and four-category sum. Every record was mapped to all exact count-vector matches; same-key candidates with different vectors remained separate. The pinned source payloads retain complete outcome descriptions and measurement metadata. The recovered tables retain time frames, population descriptions, results-group identifiers, literal categories, class boundaries and posted denominators.

We then normalized categories separately within each class–group row using explicit exact aliases. A row qualified for four-count normalization only when each retained category had exactly one integer exact alias. Qualified and unrecognized labels outside those aliases remained literal. We did not infer absent categories as zero, merge ambiguous labels or sum potentially overlapping classes. Posted class denominators were retained; an overall denominator was eligible only for a single-class table. A four-category sum remained a separate field, not a validated population denominator.

A supplementary conformance utility preserves complete outcome and measurement objects, scopes group identifiers within outcomes and separates exact label recognition from measurement type and denominator selection. Its known-source cases illustrate the identified behaviors; they are development cases, not held-out validation. This utility does not replace the frozen corpus analysis or harmonize clinical response estimands.

## Results

All 552 compact records had exact archived count-vector matches. They mapped to 552 distinct outcome–results-group tables and 564 physical query occurrences, representing 169 distinct outcomes from 138 trials. Recovery distinguished repeated query copies from separately reported populations and assessments.

Ten parent tables contained multiple classes, producing 33 class–group rows. Across all parents, class preservation yielded 575 rows. Of these, 537 had four unambiguous exact-alias integer cells; 38 retained literal categories for adjudication. Twenty-seven normalized rows differed from inherited vectors, covering 14 parent tables in eight trials. Four changed rows came from single-class tables. These are different units; 27/552 would not be an extraction-error rate.

In NCT00942162, "SD/ PR" followed "SD" in the source. Prefix recognition assigned both to SD, and the later assignment overwrote the earlier count. The inherited SD counts of 3 and 0 became the literal SD counts of 11 and 4. The combined category, with counts of 3 and 0, remained separate. This correction preserves source labels without deciding whether the combined category belongs in a clinical response estimate.

In NCT00654238, one outcome contained four histological classes. The producer retained the final class's vector, 0/0/0/1. Class preservation recovered the preceding vectors and their denominators (Table 1). Applying the overall denominator of 55 to any one class would describe a different quantity.

**Table 1. Class-specific counts in the archived NCT00654238 outcome.**

| Literal class title | CR | PR | SD | PD | Posted participants | Not evaluable |
|---|---:|---:|---:|---:|---:|---:|
| Differentiated | 0 | 16 | 22 | 1 | 44 | 5 |
| Poorly Differenitated | 0 | 2 | 1 | 1 | 6 | 2 |
| Medullary | 0 | 1 | 2 | 0 | 3 | 0 |
| Anaplastic | 0 | 0 | 0 | 1 | 2 | 1 |

The spelling of the second class is preserved from the source. The parent outcome concerns best response to BAY 43-9006 in metastatic thyroid carcinoma.

For the differentiated class, CR plus PR was 16, whereas the four selected categories summed to 39 and the posted class denominator was 44, including five participants reported as not evaluable. The corresponding arithmetic fractions were 41.0% and 36.4%. This illustrates the consequence of denominator substitution; it does not establish which response estimand should be used for clinical comparison.

In two NCT01403948 tables, "Complete remission" with count one was followed by "Complete remission unconfirmed" with count zero. Prefix assignment replaced the unqualified category with the qualified category. Exact normalization restored the literal complete-remission count while keeping the qualification separate.

Within the 33 multi-class rows, class-level denominators were available in 31 rows; two rows had missing or ambiguous eligible denominators. Across the corpus, four retained categories summed to a posted denominator in 250 rows. Arithmetic equality does not validate a clinical response partition, disjoint populations or outcome comparability.

A separate live-source check on October 2, 2026 illustrates why results-group identifiers must remain outcome-scoped. In NCT00942162, OG000 identifies the GS-positive group in "Best Overall Response (BOR) by GS," with 71 participants analyzed, but the overall study group in "Duration of Response (CR or PR)," with four participants analyzed.[7] Joining on trial and group identifiers alone would mix these populations. This corroborating example does not change the frozen corpus counts.

A companion archived search comparison found 23 versus 24 records when both the search field and query expression changed. The additional EMC R1507 record concerns an already published result. This is a source-findability example; it cannot isolate a search-field effect or estimate retrieval sensitivity.

## Discussion

Complete source recovery exposed two reproducible producer behaviors: qualified-label overwriting and subgroup overwriting. Recovering class-specific counts changes both the values and their analysis unit. The contribution is an executable correction grounded in every archived source match, supplemented by reusable conformance cases. We have not established that other extraction systems share these defects.

The registry schema already distinguishes outcome metadata, classes, categories, measurements and denominator units.[6] Reusable response data should preserve those distinctions, literal labels and source-occurrence receipts. Normalized counts should be additional fields with explicit recognition rules. Outcome-local group identifiers cannot by themselves establish trial-wide arm identity. Ambiguous rows should remain available for adjudication, and selected-category totals should remain separate from posted denominators.

The audit is limited to tables selected by the inherited corpus. It does not measure recall across all response outcomes, adjudicate every clinical response definition or establish independent patient populations. The changes arise from the frozen extraction program, not errors by registry contributors. The supplementary utility's case checks establish particular extraction behaviors, not clinical endpoint equivalence or generalization across the registry.

## Data and code availability

The original corpus, producer and archived inputs are pinned publicly.[1–3] The [complete source map](https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/registry-complete-matches-actual.json) and [575-row normalization](https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/registry-complete575-class-preserving-normalization-final.json) preserve literal tables, recognized counts, ambiguous cells and denominators. Executable recovery and normalization are [registry_response_complete_reconciliation.py](https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/registry_response_complete_reconciliation.py) and [registry_class_preserving_normalization.py](https://github.com/trimcrae/Rare-cancers/blob/da49c4e836533253825587f83656675dac4c913b/research/autonomy/data-opportunities-2026-09-30/deep-analysis/registry_class_preserving_normalization.py). The historical normalization completed in [workflow run 36880897541](https://github.com/trimcrae/Rare-cancers/actions/runs/36880897541), job 110432170241.

The supplementary [conformance utility](registry_literal_extractor.py), [case definitions](cases.json), [behavior checks](conformance_checks.py) and [source receipts](sources.json) are separate from that historical analysis. At revision b066a7e7bcffe4892c78f2d9462cc70b4d14945b, seven synthetic checks and all four known-source case groups passed against the two hash-verified archived inputs in [workflow run 37009409052](https://github.com/trimcrae/Rare-cancers/actions/runs/37009409052), job 110845272744. This replay validates the specified conformance cases; it does not rerun the full 552-table reconciliation or 575-row normalization. Earlier live-source checks provide corroboration; their response bodies were not persisted. Frozen corpus numerical claims concern archived payloads.

## References

1. [Frozen oncology endpoint corpus](https://github.com/trimcrae/Rare-cancers/blob/af7211708205b5189d8c537c1ce2a23aa4bea076/research/manuscripts/endpoint/endpoint-corpus.json).
2. [Frozen corpus producer, endpoint_corpus.py](https://github.com/trimcrae/Rare-cancers/blob/af7211708205b5189d8c537c1ce2a23aa4bea076/research/manuscripts/endpoint_corpus.py).
3. [Archived ClinicalTrials.gov payloads](https://github.com/trimcrae/Rare-cancers/tree/216bd1b5fb25a56b90ef3cc2373e1fe68322708f/literature/xdisease-ctg-results).
4. Pradhan R, Hoaglin DC, Cornell M, Liu W, Wang V, Yu H. Automatic extraction of quantitative data from ClinicalTrials.gov to conduct meta-analyses. *Journal of Clinical Epidemiology*. 2019;105:92–100. [doi:10.1016/j.jclinepi.2018.08.023](https://doi.org/10.1016/j.jclinepi.2018.08.023).
5. Shi X, Du J. Constructing a finer-grained representation of clinical trial results from ClinicalTrials.gov. *Scientific Data*. 2024;11:41. [doi:10.1038/s41597-023-02869-7](https://www.nature.com/articles/s41597-023-02869-7).
6. ClinicalTrials.gov. [API study metadata](https://clinicaltrials.gov/api/v2/studies/metadata) and [outcome measure reporting template](https://cdn.clinicaltrials.gov/documents/results_table_layout/DataEntryTable_OMForm.pdf). Accessed October 2, 2026.
7. ClinicalTrials.gov. [NCT00942162 API record](https://clinicaltrials.gov/api/v2/studies/NCT00942162), outcomes 7 and 8 (zero-based indices). Accessed October 2, 2026; source last-update-posted date December 8, 2020.
