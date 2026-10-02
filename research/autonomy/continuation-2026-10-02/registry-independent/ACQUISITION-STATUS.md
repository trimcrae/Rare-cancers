---
id: DOC-CHECKPOINT04-REGISTRY-ACQUISITION-STATUS
title: Bounded registry acquisition stopped on an invalid-request response
level: cross-cutting
kind: memo
status: live
purpose: Record the actual acquisition failure without changing the prospectively frozen selection rule.
scope: One attempted date-defined ten-study query; no new source contexts or classifier execution.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

The single frozen query returned HTTP 400 Bad Request at 2026-10-02T16:27:03Z. No study JSON was acquired, no outcome or trial identifiers were selected, and no companion predictions or accuracy calculation were made. The client recorded the HTTP status through its exception but did not retain the response body; consequently the unsupported query parameter cannot be identified from the saved evidence. This is an unresolved API-query compatibility gap, not evidence that the date slice contains no trials and not a diagnosis of registry unavailability.

As specified before acquisition, no alternate query, pagination, date broadening or handpicked replacement was attempted. The official interactive API documentation was a JavaScript shell in available web-text retrieval. Accessible NLM documentation confirms the API and response conventions but does not validate this particular combination of sort, field filters and date query. A future checkpoint would need to validate syntax against accessible official API specification and freeze an amended query before source inspection; the current plan is preserved unchanged.

The baseline identity comparison was prepared from the exact SHA256-verified accepted unit-comparison artifact, covering all 575 units. Its unique study identifiers are recorded in acquisition-receipt.json. This provides study-level exclusion against the accepted corpus if acquisition is resumed, but does not establish absence from every historical raw retrieval pool. The source manifest was inspected and records both the compact 552-table source and the larger archived retrieval files; those bulk files were not downloaded.

Deliverables are the frozen prospective PLAN.md and acquisition-receipt.json. No raw-context file exists. There is therefore no new independently selected evaluation set to dispatch at this checkpoint.
