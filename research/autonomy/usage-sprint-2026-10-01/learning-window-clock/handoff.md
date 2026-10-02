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

AI-authored by Codex. Base: `b9b420ec4073a2b28489521c7a7d6f827f90d90a`. Completed on
`codex/usage-sprint-2026-10-01-learning-window-clock`; ownership returns to the coordinator.
No PR, main integration or publication occurred.

The reporter used the latest ledger edit as observation time. With unchanged history, an old
closure stayed in the displayed current window indefinitely. It now samples UTC observation time
once and reports observation, window start and latest-ledger timestamps separately. An optional
observation clock is caller-supplied input, not authenticated time: aware offsets normalize to UTC;
naive or undefined-offset inputs refuse. Closure transitions, classifications, thresholds,
shallow-history rules, cadence readers and CLI exit mapping are unchanged.

The actual pinned-original Python witness reproduces the stale report: the original source gives
one closure / LEARNING for old unchanged synthetic history; the repaired reporter gives zero /
NOT-LEARNING at the observation clock. All 12 original test bodies remain byte-for-byte, plus four
new behavior families for aging, boundaries, current/empty/shallow history, UTC normalization,
single sampling and CLI mapping. One answered test declaration is appended to the existing
amendment log; its prior bytes and guard are unchanged.

Settled source `f5f39ba46555f8afbaa741862667623b39677a52` (tree
`9b8b0772c2ec88886ae80e089e756cff93028ed3`) passed actual
[run 37009554894 / job 110845744408](https://github.com/trimcrae/Rare-cancers/actions/runs/37009554894/job/110845744408).
CPython 3.11.16 ran 16 pytest items (0.07 s), the pinned-original witness and syntax checks.
The unchanged amendment guard admitted one declared governed path and checked 349 log records.
The direct systems checker reported 0 ERROR / 90 WARN / 7 INFO. Normal default FAST passed on the
exact source, including the unchanged 1496/1500 commit-loop budget, and the tracked diff stayed
clean. Pure-logic/full scientific suites were explicitly SKIPPED; this is not publication evidence.

Initial run `37009014212` / job `110843998646` at
`cee8d4d2e48fe8ba3ee7a4ad967edbb42b17af50` completed FAILURE after all 16 tests (0.09 s),
syntax, declaration/log checks and clean diff passed. The systems checker found five errors in
our new handoff's missing audience/last_verified and unsupported report kind; FAST was SKIPPED.
This was our packaging failure. The reviewed metadata repair corrected only the native frontmatter
and added the exact handoff path to the existing branch workflow before one automatic changed-metadata
validation. The initial log is preserved as [initial-ci.log](initial-ci.log)
(64,839 UTF-8 bytes; SHA256 `eef49e0138ca914b14590f47d4dab34462aff964216ef8357d3fa43908c0cb80`).
The settled original [settled-ci.log](settled-ci.log) is 121,470 UTF-8 bytes, SHA256
`5134e80962b8db6b1b069d5445295fc30371ff154e9f9411cace0d40ae62cae1`.

Root and separate AI review cleared source, methods, the append-only declaration and actual CI.
The final closure changes only this handoff, [validation-receipt.json](validation-receipt.json)
and the original settled log. All tested source/test/declaration/workflow blobs remain unchanged.
Its documentation-only commit uses `[skip ci]`; exact final-head Actions inventory is separate
from completed source proof and will not be presented as a green run.

Fixtures are synthetic. No current ledger outcome, scientific learning, patient evidence, detection
or live system health is established. The original module's historical scientific/prior-art header
assertions remain preserved bytes, not newly verified or endorsed. Preliminary V8 adapter evidence
is distinct from the actual Python checks. Frozen EMC ASO priority/assets, review seats,
preregistrations, paid fleet, shared queues and all publication/GPU enforcers are preserved.
No new acquisition, inference/API/GPU/paid job, scientific rescreen, outreach or notification occurred.

Next bounded action is coordinator review of the branch/compare; no integration is authorized.
Reopen work only for a distinct demonstrated useful defect or changed qualifying input. Stop this
completed clock route without repeated unchanged checks, acquisition or an extended monitoring loop.
