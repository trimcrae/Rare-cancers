---
id: DOC-TRIAL-FROZEN-BASELINE-PACKAGE-20260906
title: Portable frozen EMC retrieval experiment
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Preserve and reproduce the bounded retrieval allocation experiment.
scope: Exact frozen inputs, methods and outputs; no new science or label reading.
audience: [maintainers, autonomous research agents]
---

# Portable frozen experiment

The ZIP preserves the complete original experiment and every frozen input, with paths relative to `research/autonomy`. Original Markdown and all other bytes are unchanged. `archive-manifest.json` records each entry's size/SHA-256 and the archive digest; the original freeze, output manifest and first-run result hashes remain inside. The archived selected reference is present solely because it was a frozen input; reproduction never opens its label values.

In 6,182 records, EMC augmentation replaced 17 of hierarchy retrieval's top 100, below the prespecified 20, while 13 records moved robustly from beyond rank 200 into the top 100, exceeding the required 10. This pragmatic allocation threshold supports prioritizing atlas/fusion work over bulk additional trial labels. It is not scientific futility: ordering changed, but relevance, real review time and clinical usefulness remain unmeasured. The selected pilot stayed unopened and the 124 new labels were excluded. Descriptive DSRCT and synovial sarcoma counts do not replace the EMC decision.

From this package directory, run with an explicitly supplied **new, nonexistent** output directory whose parent exists:

```powershell
& C:/Users/mcrae/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -B -X utf8 ./reproduce.py --output C:/path/to/new-reproduction
```

Any Python 3.9+ standard-library environment can instead use `python -B -X utf8 reproduce.py --output <new-directory>`. The wrapper validates paths and entry hashes, refuses existing output, checks the original freeze/artifact hashes, then runs the original verification, mechanics checks, ranking and result verifier using its own Python executable. It compares all five original result hashes and checks that the failed-screen pilot rejects before reading reference values. The archive is never edited. Results and a log/receipt remain in the supplied output directory; the extracted original verification output is regenerated there.

`portability-reproduction.log` and `portability-receipt.json` preserve the packaging end-to-end test. Convenient `rank-results.json` and `execution.json` copies are byte-identical to the original. No network, installs, preflight, commits, method variants or additional adjudication were performed for packaging.

The local disposable `portability-test/` extraction is ignored and excluded from the deliverable manifest. Automatic tool policy blocked its cleanup; it is not part of this package's integration payload. All raw Markdown deliverables remain inside the ZIP.
