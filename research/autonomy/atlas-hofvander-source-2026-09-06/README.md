---
id: DOC-ATLAS-HOFVANDER-SOURCE-20260906
title: Newly recovered tissue RNA source for EMC target validation
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Preserve the exact public matrix and source metadata before target outcomes are read.
scope: Hofvander version 1.0.1 tissue expression and source provenance.
audience: [maintainers, autonomous research agents]
---

[Hofvander et al.](https://doi.org/10.1158/1078-0432.CCR-25-3740) provide a public tissue TPM matrix through the article's Data Availability section and [versioned author archive](https://doi.org/10.5281/zenodo.17866629). The recovered version 1.0.1 matrix has 19,116 unique gene-symbol rows and 704 samples, with exact metadata joins for every column. The archive record declares open access and CC BY 4.0; the original author README, retrieval records and metadata are retained unchanged inside source-provenance.zip.

The matrix is preserved as tpm_matrix.tsv.gz. Decompression must produce SHA256 b0d665d1bd1d96ace1faf66cc5a4d7ab7e41cb487c8f0f61734f102a1f9a7af3 and 65,407,718 bytes. The original 38-file source manifest is retained; its matrix entry applies to decompressed bytes. All other original source files, including article XML, supplements, inspection scripts and raw source notes, are in source-provenance.zip. Selected original metadata, S1 and XML are additionally exposed here for convenient audit. preservation-manifest.json verifies every source hash and archive member; independent-metadata-assessment.zip preserves the separate metadata assessment before outcome selection.

Thirteen samples are labelled EMC. Three have explicit historical case mappings (104-92, 168-97 and 536-00), and 5081-14 is a local recurrence. Excluding those leaves nine primary EMC samples for the overlap-reduced candidate analysis. Swedish recruitment and documented old-case exclusions support probable additional tissue evidence; collaborative recruitment exceptions prevent a universal patient-independence claim. Primary-lesion exclusions must be applied symmetrically to comparators. Sequencing year is a partial technical proxy, and sparse common-year comparisons address a different estimand from the all-nine marginal comparison.

This checkpoint contains no selected numeric target-expression results. Freeze the fixed eleven-address panel, separate prior-supported CHRNA6 context control, sample and comparator rules, weighting, uncertainty and deletion sensitivity before analysis. Analyze per-gene within-cohort rank probabilities; do not pool TPM with arrays or substitute samplewise cross-gene z scores. Bulk tissue RNA can support experimental tissue-validation priorities but cannot establish tumor-cell localization, normal-tissue sparing, therapeutic window or clinical efficacy.

The writer's reserved analysis packet is ../atlas-hofvander-validation-2026-09-06/. The descriptive NCC-Zurich drug comparison is deferred because this new source directly repairs the highest-ranked atlas's tissue-data gap. This is a source acquisition checkpoint, not a completed paper or publication clearance.
