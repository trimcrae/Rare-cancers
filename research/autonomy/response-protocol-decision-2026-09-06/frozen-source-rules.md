---
id: DOC-RESPONSE-PROTOCOL-RULES-20260906
title: Frozen NCT00601003 protocol rules before saved-result inspection
kind: prereg
status: immutable
purpose: Preserve source-defined decision rules before attempting comparison with saved aggregate results.
scope: Protocol version 9 dated December 4 2015; a retrospective source extraction, not a trial preregistration.
audience: [maintainers, external reviewers]
date: 2026-09-06
last_verified: 2026-09-06
---

This extraction was frozen after retrieval and original-page visual inspection, before this
worker opened the saved NCT00601003 registry record. The allocation contract had already
disclosed pooled counts (112 started, 76 outcome observations, 18 CR/PR); this is therefore
not outcome-blinded preregistration. Thresholds below come from the source, not those counts.
The source is the official 55-page Prot_SAP_000.pdf, SHA256
51939d1801b5a351145797a9bf3cf8d8fb11ac58d16a2a4e36190c5522b344d5.
Printed and PDF page numbers coincide. Embedded statistical analysis is section 6, pages
17-19; this is a protocol containing a statistical plan, not a separately titled SAP.

## Source-defined population and decisions

Section 6.2 (page 19) requires separate analysis for each of three strata and summarizes
CR, PR, SD and PD against the total number of evaluable subjects. This is not an
all-enrolled denominator. Page 18 inflates accrual for anticipated non-evaluability:
41, 36 and 23 accrued for 39, 33 and 21 evaluable patients in strata I, II and III.
An assumption that every treatment noncompleter is a nonresponder is not specified.
No general operational definition of response evaluability or explicit primary-endpoint
imputation for every unevaluable patient was found in the extracted complete protocol.
The missing-data sensitivity analysis on page 19 concerns longitudinal models and is
conditional on MAR/MCAR; it does not prescribe universal failure assignment.

Page 15 section 4.2 labels I first-relapsed and refractory neuroblastoma, II multiply
relapsed neuroblastoma, and III relapsed/refractory medulloblastoma. Page 17 section 6.1
instead calls I first relapse and II multiply relapsed or refractory neuroblastoma.
Preserve that refractory-stratum ambiguity; do not silently repair or assign patients.
This is not an EMC population.

| Stratum | Null / alternative CR+PR | Interim rule | Final rule |
|---|---|---|---|
| I | 0.30 / 0.50 | At first 19 evaluable, stop for futility when CR+PR <= 6; otherwise continue | At 39 evaluable, reject null if CR+PR >= 17 |
| II | 0.20 / 0.40 | At first 18 evaluable, stop for futility when CR+PR <= 4; otherwise continue | At 33 evaluable, reject null if CR+PR >= 11 |
| III | 0.05 / 0.20 | None; single stage | At full n=21, one-sided exact binomial test at 0.05 |

I and II thresholds are explicit on page 18; final decisions require the prior interim
path as well as the final count. III has no explicit integer threshold in that page;
any integer cutoff must be identified as a calculation from its specified exact test,
not a quoted protocol threshold. Section 6.2 says III analysis only after full accrual.
There is no source-defined pooled efficacy decision. Patient strata, evaluability,
stage order/counts and central overall response must be recoverable before an actual
decision can be reproduced. Do not substitute enrollment totals for those inputs.

## Endpoint and timing

Page 17 section 6.1 defines best CR or PR during six treatment cycles. Page 29 section
13.1 specifies best response from the sequence of objective statuses; section 13.3.1
assesses measurable disease at the ends of cycles 2 and 4 and protocol therapy.
Page 30 specifies central CT/MRI review, measurable disease CR/PR, and bone marrow
response. Bone marrow CR requires two subsequent bilateral aspirates/biopsies at least
three weeks apart. No universal four-week confirmation requirement was found in these
response sections; do not import one from generic RECIST familiarity.

Pages 31-32 sections 13.6-13.7 require central MIBG Curie assessment for the efficacy
endpoint and integrated overall response across CT/MRI, MIBG and bone marrow. Page 33
overall CR requires absence of tumor at all sites and normal HVA/VMA; overall PR has
CT/MRI reduction plus bone marrow CR and specified MIBG requirements. A pooled
radiological category alone must not automatically be treated as this overall endpoint.
The page 32 overall-response paragraph says both strata despite section 6 requiring
three; this inconsistency is preserved rather than resolved by assumption.

## Prospective computation and stop

After freezing this file, inspect only the already saved NCT00601003 result record.
Locate exact primary outcome groups/categories, denominators, population description,
stage/stratum information and statistical analyses. Derive the III cutoff and validate
I/II threshold boundaries. If the saved results lack required strata or stage inputs,
return non-identifiability and stop this source check. Any illustrative counterexample
must be labeled synthetic and cannot be attributed to real patients or investigators.
No pooled threshold testing, guessed nonresponder imputation, inferred trial success,
new-trial search, or manuscript preparation is authorized by this extraction.
