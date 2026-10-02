---
id: DOC-REGISTRY-FULL-REPLAY-RESULT-20261002
title: Known-corpus registry replay separates literal recovery from normalization policy
level: cross-cutting
kind: memo
status: live
purpose: Record independently aggregated qualification changes in the executed full-corpus literal-extraction replay.
scope: Saved comparison rows for the existing 552-parent and 575-class-group corpus; no held-out validation or clinical response-rate estimation.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

# Literal recovery agrees; conservative label qualification differs

The [cloud replay](https://github.com/trimcrae/Rare-cancers/actions/runs/37017553101/job/110872050056), executed at `e4e41e8cc93e66c2a576ec8a6f6f4acba5c5d496`, completed on the existing archived corpus. Independent aggregation of its saved unit-comparison rows confirmed 575 distinct matched class–group units and 564 physical source occurrences. All rows report literal fidelity; denominator values and selected scopes agree in every comparison. The coordinator separately verified that the saved unmatched-unit and occurrence lists are empty. This review did not rerun the raw-corpus extraction.

Four-cell qualification decreased from 537 to 510. The transitions are 510 qualified under both policies, 38 unqualified under both, and 27 qualified only under the older policy. None became newly qualified. All 510 retained count vectors are unchanged. Consequently, 65 rows require literal adjudication under the conservative utility, compared with 38 under the historical normalizer.

## Actual reasons

All 27 reductions arise from excluding qualified `i`/`ir` abbreviations from unqualified four-category normalization. They are 27 single-class parent tables from three trials:

| Trial | Rows losing qualification | Literal category suffixes |
|---|---:|---|
| NCT02263508 | 2 | `(iCR)`, `(iPR)`, `(iSD)`, `(iPD)` |
| NCT02626000 | 1 | `(iCR)`, `(iPR)`, `(iSD)`, `(iPD)` |
| NCT02829723 | 24 | `(irCR)`, `(irPR)`, `(irSD)`, `(irPD)` |

The older normalizer recognized these aliases while retaining their label family. The conservative utility leaves them literal and declines to produce an unqualified four-count vector. This is a normalization-policy difference, not evidence that the posted measurements are wrong or that their response definitions are interchangeable. The rows and measurements remain available for appropriately qualified analysis.

There are 29 rows with changed alias assignments, rather than 27: two NCT01876446 groups additionally lose recognition of `SD Stable Disease` and `PD Progressive Disease`. Both were already unqualified and remain so. These two rows account for four label-assignment changes; the 27 qualification reductions account for 108, totaling 112 changed measurement-level assignments. No denominator change accounts for any reduction.

Physical source coordinates are retained in the comparison artifact. For example, NCT02263508 maps to archived `ctg_results_bor_2014_2017.txt`, study 219, outcome 19, class 0, groups OG000/OG001; NCT02626000 maps to study 466, outcome 3, class 0, OG000. Group IDs are outcome-local and were joined with trial, complete outcome hash and class index. NCT02829723's 24 rows must not be read as 24 independent trials or patients.

## The two sets of 27 are different

The historical audit found 27 corrected count vectors relative to the inherited prefix/class-overwriting extractor, across 14 parent tables and eight trials. The present replay found 27 qualification reductions relative to the later class-preserving normalizer. Joining these sets by trial ID, full outcome hash, class index and group ID gives **zero overlapping units**. All 27 historically corrected rows remain qualified in the conservative utility and retain exactly their corrected count vectors.

Thus the manuscript's historical 552 parent tables, 575 class–group rows, 537 qualified rows and 27 corrected rows remain the description of that frozen analysis. The new utility separately yields 510 qualified rows and 65 adjudication rows on the same known corpus. Neither count is a clinical error rate. This is not a held-out test, a registry-wide estimate, a test of clinical estimand harmonization or a measurement of retrieval recall. The lack of denominator changes in this corpus does not establish equivalence of the two denominator policies on ambiguous inputs.

## Provenance

Reviewed input: `unit-comparison.json` from artifact `11231565922`, 725677 bytes, SHA256 `f32fc2197608547889312264155dcc8ed77a4587feeb5a2d06413a297b6cc3a1`. The coordinator retrieved and extracted the small ZIP and verified its GitHub digest: `57d104bd9f9e101c82c0ecf90e50837b084eafd165a0d12bb8faaecf3fed0deb`. Independent aggregation used that exact extracted entry. The supporting `independent-result-audit.json` records the label differences and unit-level overlap assessment.

Historical corrected-unit membership comes from the previously inspected pinned normalization at `6514d5c0399453d5cbd38c3989ba632dfd336d88`, SHA256 `da3485b76c984db714fc20f3bc0e82b1c07b06cb792b980f82927d3917891851`, using its `correctedCellsDifferFromLegacy` fields. No historical counts were silently revised and no new registry corpus was retrieved for this review.
