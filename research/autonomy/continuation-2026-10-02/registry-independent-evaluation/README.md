---
id: DOC-CHECKPOINT05-REGISTRY-EVALUATION-WRAPPER
title: Frozen wrapper for blinded registry outcome evaluation
level: cross-cutting
kind: memo
status: live
purpose: Compare frozen companion output with a separately authored source oracle while auditing literal preservation.
scope: All68 acquired outcomes for screening and literal preservation; family comparison restricted to oracle eligible or uncertain outcomes, reported separately.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

This wrapper was authored from extractor/companion code and oracle schema only, without reading oracle case labels, raw outcome semantics or predictions. Root executes after reviewing the frozen code and oracle. No scientific evaluation or wrapper tests were executed locally; Python AST parsing is the only local code check. The three tests use synthetic structures, not the source corpus or classifier suite.

From this directory, using standard-library Python and exact repository bytes:

```sh
python -m unittest -v test_wrapper.py
timeout 150s python evaluate.py --source /tmp/api-response.json --oracle /tmp/oracle.json --offset-amendment /tmp/offset-amendment-01.json --oracle-sha256 302ba913bdebe23f312f7cdb674b34af79ed4b7a4b8c0b57f3695c8794e6af6e --extractor ../registry/registry_literal_extractor.py --companion ../registry-family-companion/family_companion.py --out /tmp/registry-evaluation
```

Source bytes/SHA256 and both code Git blob SHA1 identities are constants. The code bytes must match head52a9fd8b8bf119d30912dca308baa0cc5541df69, not line-ending-converted copies. Importing the verified modules does not execute their guarded CLI entry points. The source is the frozen235396-byte capture. The original oracle and offset-only amendment are independently SHA256-pinned. The amendment is applied to an in-memory copy after old-scalar checks; only two named offset scalars may change. Original oracle and amendment are retained alongside the applied copy. No semantic labels are inferred, rewritten or accepted from another hash.

Every outcome object is compared in full to its original source coordinate. Every class/group extraction row, category/measurement literal, and group-specific denominator entry is checked for exact preservation and complete coordinate coverage. Empty categories and denominators without matched groups are also inventoried against the preserved full outcome. No denominator normalization or clinical response imputation is performed by the wrapper. The accepted literal extraction row is passed unchanged to accompany with [nctId,outcomeHash,classIndex,groupId], then checked against the returned copy and digest.

All68 oracle records must join one-to-one by source pointer and study/outcome indices. Exact evidence text/spans and structured source values are verified before any family classification. Excluded outcomes are not classified. Eligible and uncertain outcomes are classified separately, including those with no class/group rows; the outcome-level family result therefore does not depend on populated response categories. Counts of exact status/family/version/modifier agreements and joint agreements use each stratum's outcome denominator, not the number of repeated class/group rows. Unknown and ambiguous states are retained. Empty strings and null both denote absent version/modifier; no gene/criteria synonym rewriting is applied.

Complete outcome comparisons preserve all oracle fields and all companion mentions. Category-title role annotations can be compared to returned measurement-level family roles. Class-title or description-span roles and aggregate roles remain visible but are not automatically scored as if the extractor had equivalent scope. Reader, confirmation and clinical-threshold judgments are retained for review and are not semantically adjudicated by code. A classification disagreement is a result, not execution failure; identity, coverage or evidence-binding failures stop execution.

Outputs are summary.json, literal-extraction.json, literal-fidelity.json, outcome-comparisons.json, family-companions.json and preserved oracle/amendment files. Each has an8MiB cap; source/oracle are at most1MiB each, no network requests occur, output directory must be new. A120-second loop deadline plus root's150-second process timeout bounds execution. The reported agreement counts are a small capped date-snapshot method check, not a population error rate or independent clinical validation. No fixes or retuning belong to this evaluation.
