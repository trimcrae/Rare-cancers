---
id: DOC-ATLAS-OFFLINE-REPLAY-RESULT-20260906
title: Successful exact scientific replay in a clean local directory
level: cross-cutting
kind: memo
status: live
canonical_for: []
purpose: Record the actual offline replay and exact scientific-output comparison.
scope: One clean directory on this Windows host, unchanged frozen scientific kernels.
audience: [external reviewers, autonomous research agents]
date: "2026-09-06"
last_verified: "2026-09-06"
related: [DOC-ATLAS-OFFLINE-REPLAY-20260906]
---

The one authorized mechanical replay completed successfully, with **829,482 exact scalar comparisons and zero mismatches**. The29 scientific JSON files and all five CSV exports match under the declared policy; both execution records separately have complete status and the expected final stage. No floating tolerance was used. Original source values, patient/probe membership, all effects, bootstrap intervals, gates and deletion sensitivities are unchanged. This reproduces the historical CSPG4 result and its2019-deletion reversal; it adds no biological cohort or validation experiment.

Actual start2026-09-06T15:54:10.655070+00:00; completion15:54:57.112112+00:00 (46.46 seconds overall). All five subprocesses exited0: original Hofvander fixtures0.75s, original replication fixtures0.63s, Hofvander kernel31.17s, array kernel7.33s, reporting adapter0.42s. There were no failed empirical attempts, code repairs after freezing or repeat runs. No process remains running.

The test used a newly created directory at `replay/.cache/clean-run-20260906/`, within the owned worktree. It used the existing configured Windows host and explicit pinned runtime: CPython3.12.14, NumPy2.3.5, openpyxl3.1.5 and et-xmlfile2.0.0. It is **not** a claim that another machine or operating system was tested. Dependency installation instructions and requirements are supplied; bundling a Python distribution or wheel set is not asserted or required for this result.

Seven outer archive/provenance/gzip/normal-roster inputs were pinned before execution. Eleven exact source files were staged and verified from source packets under the supplied bundle root. The large original-array annotation was extracted from its pinned archive; the existing byte-identical GSE24369 gzip was reused. No original cache path was used to locate scientific inputs, and no network/download operation occurred.

All eight historical scientific-file bytes were preserved. Only `/source_location` in each of two staging manifests changed; equality after removal of that key was asserted. The separately named compatibility record preserves historical coordinator fields with an explicit historical-schema notice. The actual present replay authority is the coordinator's standing instruction recorded in standing-authorization.json; no newly issued original-science approval was fabricated. Original authorization and both scientific/draft packet manifests remain unchanged.

Exact comparison excludes only the named top-level authorization objects and replication.original_result_sha256, all separately checked against actual replay provenance. Source-value digests remain exact. Timestamps are retained rather than required to equal historical execution times. Five CSV tables match as parsed strings, named columns and row order. report.py takes explicit run and normal-context paths, removes the reporting dependency on the original hardcoded root/HPA cache, and leaves original summarize.py unchanged. It exports data and context rather than asserting byte-identical narrative text.

Durable evidence is in verification/receipt.json, verification/comparison.json, all ten subprocess logs, verification/replay-compatibility.json and verification/manifest.json. The full local staged source/results remain in the single clean-run directory; these large duplicate files need not be republished. `code-freeze.json` SHA256 is `cdfc8330fc0cdfd7a0ca18468cc00492311c96c3ef456cc5ba0311c2e3316bd7`; comparison SHA256 is `1855cb2c73d71f5fd00339557fc5292119f26687732c45f98e21e8e7c7c0dad9`. These are mechanical reproducibility receipts, not proof of patient independence, protein accessibility, normal sparing or manuscript readiness.
