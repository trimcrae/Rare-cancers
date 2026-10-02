---
id: DOC-USAGE-SPRINT-2026-10-01-LEARNING-WINDOW-CLOCK
title: Learning-window observation clock repair
kind: memo
status: live
date: 2026-10-02
last_verified: 2026-10-02
audience: [maintainers, autonomous research agents]
purpose: Record one bounded operational reporter repair and its exact validation scope.
scope: UTC observation time for the learning-rate CLI; no scientific or publication change.
---

# Learning-window observation clock

AI-authored by Codex. Base: `b9b420ec4073a2b28489521c7a7d6f827f90d90a`. Ownership is limited to
this isolated branch and returns to the coordinator at closure. No PR, main integration or
publication is authorized.

The reporter used the latest ledger edit as observation time. With unchanged history, an old
closure stayed in the displayed current window indefinitely. The repair samples UTC observation
time once, supports an explicit deterministic observation time, and reports observation/window
start/latest-ledger times separately. An explicit observation clock is caller-supplied input, not an
authenticated time receipt: aware offsets normalize to UTC, and naive or undefined-offset inputs
refuse. Closure transitions, route classifications, thresholds,
shallow-history rules, cadence readers and CLI exit mapping are unchanged.

The original module's historical scientific/prior-art assertions are preserved bytes, not newly
verified or endorsed. Fixtures are synthetic; no current ledger outcome, scientific learning,
patient evidence, detection or live system health is established.

The source-bound V8 scout is preliminary adapter evidence, not executed Python. Actual CPU
validation is PENDING: all 12 original learning-rate test bodies plus four new behavior families,
the pinned-original mocked-history witness, syntax, the unchanged amendment guard, direct systems
diagnostic, normal default FAST preflight and clean tracked diff. Full scientific/pure-logic
suites are not requested. No source acquisition, inference/API job, GPU/paid compute, scheduler,
fleet, queue, review seat, frozen asset or enforcer change is part of this task.

One answered declaration is appended to `amendments.jsonl` for the governed existing test file.
Existing log bytes and all original tests are retained. Root and independent review are required
before the branch head advances for actual CI. No success claim or final receipt exists yet.

Initial actual run `37009014212` / job `110843998646` at `cee8d4d2e48fe8ba3ee7a4ad967edbb42b17af50`
completed FAILURE. CPython 3.11.16 ran all 16 targeted tests (0.09 s), the pinned-original witness,
syntax, one declared governed path, the 349-record amendment log and clean diff successfully.
The unchanged systems checker reported five errors in this handoff's missing audience/last_verified
and unsupported report kind. This was our packaging failure, not baseline or environment.
Normal FAST was SKIPPED. The metadata now uses the native memo schema; settled validation remains
PENDING. The exact original initial-ci.log is retained (64,839 UTF-8 bytes; SHA256
`eef49e0138ca914b14590f47d4dab34462aff964216ef8357d3fa43908c0cb80`).
