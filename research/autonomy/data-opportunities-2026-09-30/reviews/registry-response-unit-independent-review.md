# Retained independent review: PUB-ENDPOINT-2026-09-30

This is a coordinator transcription of the completed independent review messages, preserving their judgment and execution scope. It is not a verbatim copy of the reviewer's longer original report. Draft review does not establish publication eligibility or repository-gate approval.

Reviewer: /root/review_registry_units. Writers: /root/write_registry_units, /root. Exact served model was not observable. Review timestamp: 2026-10-01T01:25:10.162Z. Checkpoint: 9a7337b3277657a03ad75d37bde2ef8111eafe73.

## Artifact bindings

- research/autonomy/data-opportunities-2026-09-30/drafts/registry-response-unit-short-report.md: Git blob 425c0b5d731e01975f394f8eedbef80ce5a29810; SHA256 2cc1630739fc7a575199efcac6e254866968b2d6d627bb3edb8bcaec282ab7d3.
- research/autonomy/data-opportunities-2026-09-30/analysis/registry_units.mjs: Git blob f07fb3e23d1c74cffb6b036580bbb2d94251fcbc; SHA256 f970ba4fed25a1147ad887b0f260556c3b977e7da94a9715a351a6d98edbf73a.
- research/autonomy/data-opportunities-2026-09-30/results/registry-units.json: Git blob a58af61cbfbd5852dce2fc4859e920b8814ae81b; SHA256 2844967d356f26d09756c1a33727c1ec459b77c0d8d0b03f22cb4fa8aa1083ed.

## Reader explanation and checked evidence

Question: Do extracted response records establish independent treatment arms and validated population denominators?

Approach and execution: Group a frozen 552-record oncology corpus by exact trial identifier and results-group title, compare retained category counts, and examine selected archived primary tables. The reviewer executed auditRegistryUnits in V8 using all four pinned inputs; the complete serialized result matched.

Main finding: There are 465 trial-title combinations, 65 repeated. NCT05323656 has one group with posted population 27, four-category sum 26 and one Not Evaluable participant. NCT04268277 supports the reported distinct time windows/counts; its table without a PD label is not imputed as zero.

Main limitations: This posthoc realized corpus includes hematological malignancies. Repeated titles do not identify duplicate patients or independent arms. Purposive examples do not estimate an error rate, and two compact-corpus examples remain explicitly not independently raw-source checked.

Next step: Retain outcome/group identifiers, definitions, time windows, posted populations and every reported category. Adjudicate tables before efficacy pooling.

## Actual prose review

All prose was read: title, abstract, introduction, methods, results and both tables, discussion, availability and references. The reviewer found the abstract understandable, the narrative followable and the scientific limits intact. No material corrections; three optional citation/wording suggestions.

Decision: pass for continued draft/author review. No unresolved material draft blockers. No full preflight, registered outgoing-prose inventory, rendered-packet inspection, exhaustive novelty determination, venue approval or submission is claimed.
