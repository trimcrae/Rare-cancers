---
id: DOC-USAGE-SPRINT-CI-TERMINAL-VERDICT-20261001
title: Bounded CI terminal verdict repair
kind: memo
status: live
date: 2026-10-02
last_verified: 2026-10-02
purpose: Preserve one operational CI reporting repair and its bounded validation.
scope: Offline CI reporter behavior only; no scientific or publication verdict.
audience: [maintainers, autonomous research agents]
---

# Question and stop

At base `184e6aff659180492f4df94ed46a222849ab1b7c`,
`research/autonomy/await_ci.py` reports terminal cancelled/skipped
or unrecognized conclusions as neither pass nor fail, then falls through to
GREEN and exit 0. Can that reporting path preserve UNKNOWN while keeping
existing success/neutral, red precedence, minimum inventory and finite waiting
behavior?

The independently inspected original Git blob is
`121bb8798debff50e207a14e50aa5aae162f3d0e`.
The repair returns exit 2 with UNKNOWN for terminal nonverdict conclusions.
It does not change workflow conclusions, GitHub Actions policy, publication
acceptance, the shared HTTP describer, scientific checks or any scheduler.

# Validation status

This is an AI-authored source/method checkpoint by Codex. Source inspection is
distinct from executed Python. Initial exact-source CI 37000543323 at
f957a685941d23c28b07fa974502c2fc9c939f6e passed its 14 offline unittest
methods, syntax and 15 inherited HTTP pytest tests, with clean tracked diff.
Normal FAST failed both systems-model and test-function-budget gates, so the
run is FAILED. Our handoff used a status outside the native schema; our test
packaging put the commit-loop tier at 1506/1500. These are our repair/metadata
failures, not baseline environment failures. The original 103252-byte log is
retained for the final receipt. Its SHA256 is
92fa06435416ef2ede5b0ad8561b76346da453ba5c2e1956ce5f00d82df5573d.

The updated checkpoint corrects the handoff status and groups all original
scenario/assertion bodies into eight natural behavioral families. It changes
no budget ceiling or guard. A direct unchanged systems-checker diagnostic is
included before normal FAST to expose any additional failure. Settled checks
have not yet run at this checkpoint; exact-source CI success remains PENDING.

The planned settled checks are eight offline unittest methods (including an
exact pinned-original cancelled false-green witness), existing offline HTTP
diagnosis pytest cases, syntax compilation, normal default FAST and clean
tracked diff. API responses and time are mocked for poll behavior; no live
provider/source request or scientific rescreen is required. Normal FAST is
not full publication verification.

# Preservation and endpoint

The frozen EMC ASO NAT submission package remains first priority and awaits
author action. All scientific inputs/results, deposited assets, review seats,
preregistrations, shared queues, paid fleet, categorical no-GPU posture and
publication enforcers remain unchanged. This task creates no PR, main merge,
publication, outreach, model inference/API or paid compute job.

Stop after one independent review/repair batch and exact settled CI receipt.
Record actual failures as repair/configuration failures when appropriate;
never substitute a cancelled or skipped run for green evidence. No new
scientific or scheduler task is queued by this handoff.
