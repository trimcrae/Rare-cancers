---
id: "DOC-DATA-OPPORTUNITIES-2026-09-30-DRAFTS-IMMUNOSARC1-COMPLETE-PUBLISHED-SUMMARY-SOURCE-APPENDIX"
title: "Qualification of the published IMMUNOSARC1 gene summary"
level: "L3"
kind: "manuscript"
status: "live"
canonical_for: []
purpose: "Working research draft: Qualification of the published IMMUNOSARC1 gene summary."
scope: "September 30 measured-data campaign; retain the source qualifications, execution boundaries and historical status stated in the body."
audience: ["maintainers","external reviewers"]
date: "2026-09-30"
last_verified: "unverified"
_backfilled: "true"
---

# Qualification of the published IMMUNOSARC1 gene summary

The identified IMMUNOSARC1 source provides a published gene-level summary rather than an independently reusable patient-by-gene matrix for this analysis. We parsed the complete table, preserving every printed row, source region, direction and stated adjusted value. The source contains 84 unique genes: 70 rows labelled DOWN and 14 labelled UP in the printed contrast. An earlier campaign filename referring to 184 is superseded and must not be treated as a data count.

Fifty-nine of the 84 rows had reported Bonferroni values below 0.05. We checked the arithmetic relationship between printed nominal and adjusted values and retained the complete table without selecting favorable genes. Sensitivity calculations applying alternative fixed correction-family sizes of 102, 732 and 2,549 to the printed nominal values yielded 59, 39 and 27 values below 0.05, respectively. Those alternative family calculations do not identify the authors' actual search universe or replace their reported analysis. Printed rounding and the availability of only a selected summary limit reconstruction.

The analysis unit remains a reported gene summary, not a patient, independent tumor or experimental replicate. The source-selected genes cannot be reinterpreted as an externally validated EMC treatment signature. No differential-expression model, patient-level resampling, cell-type deconvolution or clinical predictor was fit from these rows. IMMUNOSARC1 is distinct from the NCT03282344 serial-biopsy source studied in the [availability correspondence](immunosarc-availability-correspondence.md).

The contribution is a complete source and arithmetic qualification for existing immunotherapy discussion, with modest standalone novelty. The [84-row audit](../deep-analysis/results/ImmunoSarc-complete84-printed-gene-summary-audit.json) preserves the literal table, complete parsed rows, source identity, all correction sensitivities and precise limitations. The older misnamed 184-row artifact remains historical; this complete 84-row object is authoritative.
