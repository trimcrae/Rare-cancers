# Response tables and analysis populations in ClinicalTrials.gov: an audit of an oncology extraction corpus

## Abstract

**Background:** Automated extraction can turn a registry response table into an apparently simple treatment-arm record. The table may instead describe a particular assessment, analysis population or time window.

**Methods:** We audited a frozen corpus of 552 extracted response records from 138 ClinicalTrials.gov trials. We grouped records by trial identifier and results-group title, compared their four retained response categories, and checked purposively selected examples against archived registry payloads. This exploratory audit was not preregistered.

**Results:** The corpus contained 465 trial–group-title combinations. Of these, 65 appeared more than once, contributing 152 records. Repeated records differed in their response counts in 43 combinations. Repetition included distinct assessment methods and analysis populations; it did not establish duplicate patients. In one archived trial, the parser reconstructed 26 participants from four response categories, while the posted analysis population contained 27 and an additional “Not Evaluable” category accounted for the difference.

**Conclusions:** Extracted response records should retain the source assessment and analysis population. Repeated group titles require contextual interpretation, and a sum of selected categories should be labeled as a reconstructed total until reconciled with the posted denominator.

## Introduction

An oncology response table describes more than a treatment. Its counts depend on the population analyzed, the assessment method, the response definition and the observation period. A registry can legitimately report several such tables for the same named treatment group. An extraction pipeline that retains response counts but drops this context can make these tables appear interchangeable.

We examined these distinctions in an existing ClinicalTrials.gov extraction corpus [1,2]. The question was whether its records could be read as independent treatment arms with validated population denominators. Our contribution is a reproducible audit of the extraction unit, supported by examples that readers can reconstruct from archived source data. We did not compare treatment efficacy.

## Methods

We pinned the corpus and its producer to repository revision af7211708205b5189d8c537c1ce2a23aa4bea076 [1,2]. The inherited retrieval used two oncology query families: records mentioning best overall response and records with a registered placebo comparator, across five date windows. This audit used the resulting corpus rather than performing a new registry search. Although the inherited protocol described solid tumors, the realized corpus includes hematological malignancies. We therefore treat the present work as an exploratory audit of oncology extraction, not a solid-tumor benchmark.

The parser scans posted outcome measures for category titles beginning with labels for complete response (CR), partial response (PR), stable disease (SD) and progressive disease (PD). It accepts integer measurements, requires all four categories and retains records with a positive category sum. All 552 stored records carry the unit “Participants.” The stored field evaluable_n is calculated as CR + PR + SD + PD; it is not read from a posted population denominator.

The parser suppresses repeated keys comprising trial identifier, outcome title, results-group title and reconstructed total. Its output retains outcome titles but omits source outcome identifiers or indices, results-group identifiers, time frames, outcome descriptions, posted denominators and categories outside the four retained labels. We call its outputs extracted records because these fields do not establish independent treatment arms or fully defined analysis populations.

We grouped records by exact trial identifier and results-group title. Within each combination, we counted multiplicity and compared reconstructed totals and four-category vectors. These combinations are an audit device, not adjudicated populations. We also described record size and the occurrence of zero CR + PR counts. Thresholds of 10 and 20 participants were descriptive checks, not efficacy cutoffs. Source examples were selected purposively to clarify interpretation. They do not estimate the prevalence of extraction errors. The audit code and machine-readable results accompany this report [3].

## Results

The 552 records came from 138 trials and formed 465 trial–group-title combinations. Most combinations appeared once. The 65 repeated combinations occurred in 14 trials and contributed 152 records, or 87 records beyond one per combination (Table 1). Thirty-eight repeated combinations had the same reconstructed total across their records; 43 had differing four-category vectors. These properties can coexist.

**Table 1. Multiplicity of trial–group-title combinations**

| Records per combination | Combinations | Extracted records |
|---|---:|---:|
| 1 | 400 | 400 |
| 2 | 50 | 100 |
| 3 | 8 | 24 |
| 4 | 7 | 28 |
| Total | 465 | 552 |

Repeated titles preserved distinctions within the compact corpus. NCT00600340 reports best overall response and explicitly unconfirmed best overall response for intention-to-treat and per-protocol populations. For its bevacizumab-plus-paclitaxel group, the corresponding reconstructed totals are 270, 255, 270 and 255. These are different response definitions and population labels, not four independently established arms. This illustration has not been independently checked against its oversized archived payload in this audit.

A second corpus illustration, NCT00858117, reports physical-examination and CT-based assessments for “Alemtuzumab and Rituximab.” Both retained tables total 30 participants, but their CR/PR/SD/PD vectors are 18/12/0/0 and 7/14/9/0. This illustration comes from the extracted corpus; it has not been independently checked against its archived payload in this audit. Matching titles and totals alone cannot establish patient overlap or justify choosing one assessment.

An archived source check identified a separate denominator issue in NCT05323656 [4]. Its posted “Overall Response Rate (ORR)” table identifies a full analysis set of 27 participants for setanaxib plus pembrolizumab and 28 for placebo plus pembrolizumab. The four retained categories sum to 26 and 28, respectively. The source also reports “Not Evaluable” counts of one and zero (Table 2). The parser excludes that category and stores the four-category sums as evaluable_n. This reconstructs a selected-category total rather than the posted full analysis set. The example demonstrates why a denominator must retain its population definition; it does not establish how often this occurs.

**Table 2. Posted population and retained categories in archived NCT05323656 results**

| Results group | Posted full analysis set | CR + PR + SD + PD | Not Evaluable |
|---|---:|---:|---:|
| Setanaxib plus pembrolizumab | 27 | 26 | 1 |
| Placebo plus pembrolizumab | 28 | 28 | 0 |

Small reconstructed totals also shaped the corpus description. The median was seven participants; 321 records had totals below 10 and 414 below 20. Zero CR + PR counts occurred in 251/552 records (45.5%), compared with 32/231 (13.9%) among records totaling at least 10 and 4/138 (2.9%) among those totaling at least 20. These are overlapping descriptive subsets of heterogeneous records. They do not show that zero responses are uninformative or identify a treatment effect.

## Discussion

The audit supports an explicit population unit for registry response extraction. Neither a treatment title nor a four-category total supplies that unit by itself. Repeated tables may legitimately reflect intention-to-treat versus per-protocol populations, response-confirmation requirements, different measurement methods or different time windows. Collapsing them by title can discard distinctions; counting every record as an independent arm can overstate the number of independent observations.

A useful extraction should preserve the source outcome key or index, title, description and time frame; the results-group identifier and title; the analysis-population description and posted denominator; the measurement method; and every reported category, including non-evaluable participants. It should store a reconstructed category sum separately and flag discrepancies for interpretation. This preserves the evidence needed to select an analysis unit before pooling results.

The audit has limited scope. We have not adjudicated every response definition, population overlap or source table. Exact title matching may split equivalent groups or combine differently defined populations. The representative source checks were purposive, and an identified denominator discrepancy cannot be generalized into an error rate. Likewise, failure to extract a four-category table would not demonstrate that a trial omitted response reporting. The corpus can support audits of extraction behavior; additional source-level adjudication is needed for efficacy synthesis or comparisons between diseases.

## Data and code availability

The pinned corpus and original parser are public [1,2]. The audit is provided in [registry_units.mjs](../analysis/registry_units.mjs), with results in [registry-units.json](../results/registry-units.json) [3]. Exact numerical source claims refer to archived payloads rather than the current live registry page.

## References

1. Cross-disease endpoint corpus. Revision af7211708205b5189d8c537c1ce2a23aa4bea076, corpus blob343922742f88f63a1803dba26904c45369c73d07. [Pinned data](https://github.com/trimcrae/Rare-cancers/blob/af7211708205b5189d8c537c1ce2a23aa4bea076/research/manuscripts/endpoint/endpoint-corpus.json).
2. Original corpus extraction program, endpoint_corpus.py. [Pinned source](https://github.com/trimcrae/Rare-cancers/blob/af7211708205b5189d8c537c1ce2a23aa4bea076/research/manuscripts/endpoint_corpus.py).
3. Registry analysis-unit audit. Code and results supplied with this report.
4. Archived ClinicalTrials.gov best-overall-response retrieval, 2022–2026 window. Blobf125b25e71104dc7db4f3134c3632406e88a9033; NCT05323656. [Pinned payload](https://github.com/trimcrae/Rare-cancers/blob/216bd1b5fb25a56b90ef3cc2373e1fe68322708f/literature/xdisease-ctg-results/ctg_results_bor_2022_2026.txt).
