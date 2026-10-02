---
id: DOC-CHECKPOINT05-REGISTRY-PRESENCE-VALIDATION-REPAIR
title: Distinguish absent optional source fields from present null values
level: cross-cutting
kind: memo
status: live
purpose: Repair the observed pre-prediction evidence validation failure without altering semantic oracle labels or classifier code.
scope: Mechanical source-presence amendment and generic evidence validation; no case-label inspection or prediction execution.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

Cloud run37042765466 atd27ceef passed the initial three wrapper tests, then failed on an absent optional populationDescription source pointer before the prediction loop. Initial wrapper bytes are preserved as initial-executed.txt (SHA256827a45d49bec3a7a767022336f949bfa5348b3616fe5cd050551a19543b2ffe7) with initial-freeze-manifest.json. No prior success or prediction is asserted.

The separate oracle author audited source presence and froze source-presence-amendment-02.json, SHA256086d974d984f56ebb1690aa05f245b5db39ecac4e96b038b40ab3a2737e010a1. This worker received only schema and hash, not case contents. The wrapper applies that pinned amendment after the pinned offset amendment in memory. Each operation must add sourceFieldPresent:false to an existing evidence object with a null placeholder. Its source parent must exist as an object and the exact source leaf must be absent. Removing all added presence flags must restore the prior oracle exactly; original labels and both amendments are preserved in outputs.

The validator distinguishes explicitly absent leaves from present null values. Unmarked missing leaves, missing parents, asserted absence of an existing leaf (even null), non-null absence placeholders and absence assertions with literals fail. No missing field is silently replaced with null. Two synthetic tests cover these distinctions in addition to the three previously passed wrapper tests. Local validation remains AST parsing only; root runs the updated five tests and evaluation in cloud.

Add `--presence-amendment /tmp/source-presence-amendment-02.json` to the README CLI. All original source/code/oracle/offset pins remain unchanged. New outputs preserve the presence amendment and the oracle with both mechanical amendments applied. This is an observed execution-defect repair before predictions, not classifier retuning or semantic adjudication.
