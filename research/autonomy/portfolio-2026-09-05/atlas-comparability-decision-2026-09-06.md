---
id: DOC-ATLAS-COMPARABILITY-DECISION-20260906
title: Require an identifiable RNA contrast rather than universal absolute calibration
kind: memo
status: live
purpose: Independently challenge the normal-reference gate before further allocation.
scope: Completed source packets, RNA-only contribution and the minimum missing validation input.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

Independent read-only assessment by /root/atlas_comparability_decision, requested medium,
completed without expression-outcome analysis, downloads, files or running processes.
This is a coordinator synthesis of its returned reasoning, not an ultra release review.

The universal absolute-calibration gate is too strong for RNA-only replication. The actual
indispensable requirement is an identifiable, decision-relevant RNA contrast. PeerJ provides
EMC-only processed columns; GSE119630 contains within-study colon cancer/normal comparisons;
E-MTAB-12593 contains within-study prostate regions. Neither normal dataset supplies an EMC
comparison. Separate-study gene differences mix biology and gene-specific study response.
Same-platform assumptions, z-scoring or harmonization do not independently estimate that
response. A common physical reference is one solution, but justified measurement invariance
or externally supported response bounds could also suffice. No such evidence is identified.

An independent EMC-bearing dataset with fixed relevant comparators measured in the same
design could support useful replication without absolute units. For each frozen target g,
the estimand is P(X_EMC,g > X_comparator,g) + 0.5 P(tie), estimated within each cohort.
Comparator histologies and their weights must be fixed before validation outcomes. A common
monotone gene-specific measurement transformation preserves that estimand. Do not rank genes
against one another by unlike assay response or pool patients across platforms. Patient units,
target mapping, credible independent recruitment and within-study technical comparability
remain necessary. A documented processed matrix may suffice; raw counts, exhaustive donor
crosswalks, protein localization and absolute transcript calibration are not universal gates.

Such replication could strengthen or remove a target's EMC-enrichment rationale for tissue
validation. It would establish neither normal-organ sparing nor malignant-cell localization.
The result must have enough precision to inform a prespecified experimental decision; mere
transcript representation or an arbitrary favorable threshold cannot replace that requirement.

Coordinator disposition: accept the narrower gate; retain the original normal-source memo
bytes and read its common-reference requirement as specific to that proposed cross-study
calibrated contrast. No normal-only precision or prostate raw-read computation is allocated.
Existing GSE28866 contrasts and provenance were already checked and are not a new experiment.
The named Zullow2022 seven-case EMC source is the next specific dependency check; its metadata
and availability must be resolved before any target outcomes or analysis allocation.
