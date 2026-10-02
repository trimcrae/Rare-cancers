---
id: DOC-CHECKPOINT05-REGISTRY-ACQUIRED-CONTEXTS
title: Date-selected registry contexts acquired for separate blinded review
level: cross-cutting
kind: memo
status: live
purpose: Record the bounded acquisition result and handoff for blinded source interpretation.
scope: Ten new-to-575 trial identifiers and 68 unscreened outcome objects; no companion prediction or accuracy evaluation.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

The single amended query returned HTTP200 at 2026-10-02T17:27:10Z, with 235396 bytes of JSON, SHA256 `d20367d3d14f99716b20309ee8bed1cebe4b6a1270077fc0ac234a4cc5b91fa6`. The amendment was already saved and hash-bound before this request. All returned first-results dates satisfy the September2026 window and are nondecreasing. Seven studies are dated September1 and three September2. Pagination is present but was not followed. The cap may truncate a date tie; no completeness or probability-sampling claim is made.

The frozen returned order is NCT04008706, NCT01520701, NCT05508867, NCT05327530, NCT04209686, NCT04557956, NCT04570956, NCT04276493, NCT02657486, NCT05700903. None occurs in the SHA256-verified accepted575-unit comparison. Their complete returned outcome objects number4,2,6,24,3,5,1,15,1,7 respectively, totaling68. These are outcome objects, not established response outcomes or class/group units. Study-level separation is demonstrated only against the accepted575 units, not every historical retrieval pool.

The exact raw response is api-response.json. It preserves requested study metadata and all returned outcome fields without rewriting literals. acquisition-receipt.json records source URL, status, timestamp, hashes, last-update dates, every outcome pointer, baseline exclusion IDs and documentation receipts. The official machine-readable OpenAPI and metadata documents are preserved. No classifier output has been generated, and this acquisition worker did not inspect outcome semantics or assign family/relevance labels.

Next, a different reviewer should receive the response plus amendment and original screening instructions, without companion predictions. The reviewer must screen all68 objects, retain exclusions/ambiguities, and freeze source-supported family/version/role/denominator judgments before root authorizes any companion evaluation. A possible absence of response-eligible outcomes remains a legitimate negative result; the acquisition is closed with no substitutions.
