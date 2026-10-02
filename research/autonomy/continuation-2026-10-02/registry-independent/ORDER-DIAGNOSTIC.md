---
id: DOC-CHECKPOINT04-REGISTRY-ORDER-DIAGNOSTIC
title: Official API rejects the frozen NCT identifier sort
level: cross-cutting
kind: memo
status: live
purpose: Diagnose the failed query without changing the prospective study selection rule.
scope: One repeated identical API request with a capped error body; no outcomes acquired or inspected.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

At 2026-10-02T16:32:54Z, the repeated identical query returned HTTP400 with the complete 32-byte plain-text body:

> Unsupported sort field type: nct

The original request explicitly used `sort=NCTId:asc`. The official server recognized the NCT field type and rejected sorting on it. The exact URL, timestamp, response content type, retained body and its SHA256 are saved in identical-query-diagnostic.json. No new study response was acquired or inspected. The initial failure receipt and PLAN.md remain unchanged.

This is not demonstrated to be a spelling or encoding error that can be repaired while retaining the original order. The original rule requires selecting the first ten studies in ascending NCT identifier order. Sorting a capped server response locally would only reorder those returned studies and would not establish that they are the first ten in the date-defined population. Retrieving the entire population to sort would exceed the frozen acquisition procedure.

Therefore no amendment or altered query was executed. Proceeding requires an explicit methodological change approved by root: choose a documented server-supported ordering and specify tie handling before acquisition, while retaining the condition, date window and ten-study cap. Alternatively a distinct bounded sampling design could be frozen. Either would be a changed selection rule, not a syntax-only correction. This checkpoint stops at the diagnosed ordering limitation; no classifier predictions, oracle labels or accuracy claims exist.
