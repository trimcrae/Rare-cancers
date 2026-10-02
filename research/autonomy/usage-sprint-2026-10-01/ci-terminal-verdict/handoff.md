---
id: DOC-USAGE-SPRINT-CI-TERMINAL-VERDICT-20261001
title: Bounded CI terminal verdict repair
kind: memo
status: draft
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
distinct from executed Python. No Python suite, FAST check or CI success has
been claimed at this checkpoint. The branch-only CPU workflow will run only
after independent source/method review.

The proposed actual checks are 14 offline unittest methods (including an
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
