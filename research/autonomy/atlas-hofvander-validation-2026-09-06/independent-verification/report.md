---
id: DOC-HOFVANDER-INDEPENDENT-RESULTS-20260906
title: Independent source and arithmetic verification of Hofvander results
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Verify authorized terminal empirical results directly from primary source records.
scope: Fixed eleven addresses and separate CHRNA6 control in Hofvander and GSE24369.
audience: [maintainers, autonomous research agents]
---

The terminal empirical results are verified with no material source or arithmetic discrepancies. CSPG4 is the sole address passing the original frozen allocation rule. This is a qualified bulk-RNA rationale for tissue validation, not clinical efficacy, surface localization or normal-tissue sparing.

Independent parsing recovered all8,448 fixed12 Hofvander values directly from the original704-column TPM matrix and all504 fixed12 GSE24369 values directly from the42 original SOFT sample tables. All values match the worker's selected outputs. The original99MB GPL6244 annotation independently supplies one uniquely gene-assigned probe for each fixed gene, with no alternative-gene mappings. All42 sample titles independently classify as6 EMC,17 LGFMS,6 MFS,6 desmoid,5 SFT and2 pooled muscle RNAs. Tumor-biopsy metadata agrees; pooled normal RNA is not treated as two healthy patients.

Source Table S1 and sequencing metadata independently reconstruct704 unique IDs, the three explicit MDB9736 exclusions, symmetric nonprimary-lesion exclusions and9 retained EMCs. All joins agree. Eleven source-file hashes and16 authorized-file hash entries match. Both worker executions are terminal complete; original and replication results remain separate.

`verify.py` imports no worker code. It uses Decimal source values and Fraction pair counts, with sorted-rank lookup, to check2,436 published estimate/deletion blocks and266,772 scalar comparisons. It checks per-histology marginal and exact-year probabilities, cells, weights, denominators, EMC placements, original allocation decisions, EMC/comparator/year/histology deletions, revised-diagnosis sensitivity and all48 shared-histology gene contrasts with both cohorts' deletions. Comparison tolerance1e-12 accommodates serialized binary64 output; no discrepancies occurred. All eleven false/true allocation labels agree, including ten failures.

CSPG4's original equal-histology estimates are0.8945416723 marginal and0.8111111111 year-matched. The primary LGFMS replication anchor is arrayA1.0 (6×17 biopsies), Hofvander marginal0.9658119658 (9×13 primary lesions), and matched0.9333333333 (3 supported EMC). Secondary CSPG4 arrayA is1.0 for MFS, SFT and desmoid; Hofvander marginal/matched values are0.8537037037/0.8571428571,0.8787878788/0.625, and1.0/1.0 respectively. These are per-histology effects, not a pooled cross-platform composite. Patient/lesion equivalence and universal independence remain unproven.

The decisive qualification is sequencing-year sensitivity: deleting2019 makes the CSPG4 year-matched equal-histology summary0.4333333333, reversing its direction. Other required EMC/histology deletion checks remain positive, so the frozen allocation rule still passes exactly as specified; sequencing-year deletion was a reporting qualifier, not an acceptance condition. This must be described as year-sensitive evidence, not generally batch-robust validation. That deletion also changes the sparse supported target population; it is not a precision-adjusted estimate for the original population.

Contrary evidence is retained. LGFMS directions are negative in both cohorts for CD276, CD248 and CDH17; opposite for SSTR2, FAP, MSLN and GPC3. PRAME and L1CAM show positive LGFMS directions in both cohorts but fail the original broader allocation rule. ALPP's Hofvander matched LGFMS effect is neutral0.5. CHRNA6 is1.0 in the anchor's array, marginal and matched estimates but remains a separate context control, never an address success. Full twelve-gene, four-histology effects and directions are in `verification.json`.

`bootstrap_check.py` independently uses5,000 multinomial histology/year-stratum draws, seed931704, with shared EMC weights across comparisons. CSPG4 marginal interval endpoints differ from the writer's2,000-draw result by0.0016563 and0.0001102; matched endpoints agree at0.7527778 and0.8611111. This checks the sampling approach without requiring identical random-number ordering. The intervals remain conditional on sparse/singleton strata and do not cover unknown batch/purity confounding or simultaneous eleven-gene inference.

Commands use `C:/Users/mcrae/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -B -X utf8` followed by this cache directory's `verify.py` or `bootstrap_check.py`. Both exited0. Machine logs are `verification.json` and `bootstrap-check.json`; execution receipt and durable manifest pin commands, scripts, outputs and hashes. Active scientific seconds were not instrumented; no claim of a measured review-duration budget is made.

The fixed outcomes are verified, not upgraded to protein, therapeutic-window or clinical validation. No source survey, normal-context analysis, tracked edits, mail, spending, commits or full preflight occurred. Nothing remains running.
