---
id: DOC-CHECKPOINT05-REGISTRY-DATE-SAMPLING-AMENDMENT
title: Prospective amendment to the small registry sampling order
level: cross-cutting
kind: memo
status: live
purpose: Replace unsupported NCT identifier sorting with documented date sorting before acquiring independent evaluation contexts.
scope: One query, cancer condition, September 2026 first-results posting, at most ten studies, no classifier execution.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

This root-authorized amendment is frozen before acquisition. Checkpoint04's original plan and HTTP400 diagnostics remain immutable. The official OpenAPI specification at https://clinicaltrials.gov/api/oas/v2 returned HTTP200 and states that sort fields may be date or numeric types, with explicit ascending/descending directions. Official https://clinicaltrials.gov/api/v2/studies/metadata identifies ResultsFirstPostDate as sourceType DATE. These jointly support `sort=ResultsFirstPostDate:asc`; this changes the selection order rather than disguising a methodological change as a syntax repair.

Retain condition cancer and `AREA[ResultsFirstPostDate]RANGE[2026-09-01,2026-09-30]`, pageSize10, JSON, and the original requested IdentificationModule, StatusModule, ConditionsModule and OutcomeMeasuresModule fields. Make at most one amended studies query and read no more than1MiB. No pagination, condition/date broadening, replacement, response-label search or classifier-dependent selection is permitted. API failure, invalid date/order checks or oversize response terminates acquisition.

Tie policy: retain the server's returned order among studies sharing first-results date, freeze that exact response as the reproducible snapshot, and make no claim that tied order is stable across future API requests. If the ten-study cap cuts a date tie, the unobserved members remain unobserved. Even if all ten returned dates coincide, do not fetch additional records to break the tie. This is a date-defined first-page convenience slice, not an exhaustive first ten by NCT identifier or a probability sample. Record pagination token presence without following it.

Preserve all complete returned outcome objects and their zero-based source pointers before relevance screening. Compare trial IDs against the SHA256-verified accepted575-unit comparison; retain overlaps in the source record, exclude them from independent evaluation without replacement. Nonoverlap applies to the accepted575 units, not necessarily all historical raw retrieval pools. Save exact response bytes, URL, UTC retrieval time, HTTP status and SHA256, plus metadata last-update fields. Do not run the family companion or assign semantic family labels. A separate reviewer blind to companion outputs must lock response relevance, source-supported family/version/modification/ambiguity, literal role mappings, confirmation and denominator/pointer oracle before any evaluation. Empty, insufficient or non-response outcomes are retained as negative screening results, without fishing.

All scientific interpretation and limits in checkpoint04's plan remain: small post-development external-to-575 evaluation preparation only; no independent clinical adjudication or accuracy claim. Complete returned contexts means complete outcome objects and requested metadata, not unrequested study modules. This amendment changes only order/tie policy; the root will decide whether the acquired set supports a subsequent blinded evaluation.
