---
id: DOC-CHECKPOINT05-REGISTRY-BLIND-ORACLE-METHOD
title: Frozen blind source-context oracle review method
kind: memo
status: frozen
date: "2026-10-02"
last_verified: "2026-10-02"
purpose: Document independent-of-predictions screening and source-label extraction before classifier evaluation.
scope: All 68 returned outcomes in the ten-study registry date slice.
audience: [maintainers, reviewers]
---

The separate LLM reviewer read only the amendment, acquisition receipt, and exact acquired API response. Classifier code, predictions, and historical 575 outcome texts were not inspected. The receipt exposes baseline study identifiers but not their labels. No web, UI, browser automation, new checkout, runtime, or large artifact was used.

Every zero-based outcome was screened in returned order. Eligibility means a direct tumor/disease response proportion or categorical response distribution. DCR qualifies; symptom, safety, drug exposure, immunogenicity, dose selection, continuous Ki67, mortality, and temporal DOR/TTR/PFS endpoints do not. Temporal outcomes remain explicitly excluded even if they mention named response criteria; this boundary is fixed before evaluation. There were nine eligible outcomes in six studies and 59 exclusions. No uncertain eligibility was required, which does not imply uncertainty-free clinical data.

For eligible outcomes, family/version requires explicit source naming. CR/PR alone does not establish RECIST. No named modifier is inferred from confirmation language, disease type, or local assessment. The cystoscopy/cytology tumor-response record remains unknown family. Eight outcomes explicitly name iwCLL 2018 (one), Lugano 2014 (one), or RECIST 1.1 (six). No eligible paired named-family conflict was found. The RECIST distribution's malformed stable-disease prose is retained as a source inconsistency; explicit family and literal category labels are not silently repaired.

The oracle copies exact title, description, timeframe, population, source groups, denominators, and classes. JSON pointers identify fields. Supporting literal spans use zero-based Python Unicode character offsets in decoded field strings, not byte offsets in serialized JSON. Category roles distinguish actual class/category labels from definition components; unnamed aggregate categories are not relabeled as if a literal title existed. No Response is not mapped to progressive disease. Missing and zero-denominator Phase II groups remain explicit. Reader/confirmation labels are taken from the same outcome only; sibling statements are not silently inherited.

No pooling, per-patient classification, clinical response reconstruction, ORR recalculation, or efficacy/safety assertion was performed. This is a small LLM source-context evaluation, not independent clinical adjudication or a stable accuracy estimate. The initial oracle and method are frozen by SHA256 before root classifier execution. Any later correction must be a separately named dated amendment, preserving these bytes.
