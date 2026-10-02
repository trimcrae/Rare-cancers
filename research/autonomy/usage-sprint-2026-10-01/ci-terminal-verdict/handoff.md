---
id: DOC-USAGE-SPRINT-CI-TERMINAL-VERDICT-20261001
title: Bounded CI terminal verdict repair
kind: memo
status: live
date: 2026-10-02
last_verified: 2026-10-02
purpose: Preserve a verified operational CI reporter repair and its bounded validation.
scope: Offline CI reporter behavior only; no scientific or publication verdict.
audience: [maintainers, autonomous research agents]
---

# Completed result

Terminal cancelled/skipped or unrecognized CI conclusions now return exit 2
with UNKNOWN. Previously the reporter printed “not evidence of green”, then
fell through to GREEN and exit 0. Existing success/neutral classification,
RED precedence, minimum inventory and finite waiting behavior are unchanged.

The exact pinned original at base
`184e6aff659180492f4df94ed46a222849ab1b7c`, native Git blob
`121bb8798debff50e207a14e50aa5aae162f3d0e`, actually reproduced the
cancelled-to-GREEN/exit-0 defect in the offline Python test. API responses and
time were mocked; this was not a live GitHub-health measurement.

This is AI-authored work by Codex. A separate AI reviewer and root checked
source/methods; the separate reviewer also inspected actual settled CI and
byte-matched the original logs. No human review or new primary biomedical
source verification is claimed.

# Actual exact-source validation

Tested revision: `a8dc6075be2dc782954d10982b43cea554a4c3a0`.
Tested tree: `f2b0e3c1aaafa157f28334080e1a49ba52389565`.

[CI 37001860371](https://github.com/trimcrae/Rare-cancers/actions/runs/37001860371),
job `110821137756`, completed SUCCESS on that exact checkout with
CPython 3.11.16:

- Eight offline unittest methods passed (0.007 s), retaining all fourteen
  original scenario/assertion bodies in natural behavioral families.
- Fifteen inherited offline HTTP pytest tests passed (0.08 s); syntax passed.
- The unchanged systems checker passed with 0 errors and 90 retained warnings.
- Normal default FAST passed its document/artifact gates, with the existing
  commit-loop tier at 1500/1500 test functions; tracked diff remained clean.

The full scientific and pure-logic pytest suites were explicitly skipped by
default FAST. No `PREFLIGHT_FULL` publication verification was performed.
See [validation-receipt.json](validation-receipt.json) and the
[original settled transcript](final-ci.log), 122695 UTF-8 bytes, SHA256
`01101a0a7db73a96aefd1e131135bdbc1d8b6f7a26c2314e526ca2d920ea9572`.

# Initial failure and narrow repair

Initial exact-source CI `37000543323`, job `110816998065`, at
`f957a685941d23c28b07fa974502c2fc9c939f6e` passed its fourteen unittest
methods, syntax, fifteen inherited HTTP tests and clean diff. Overall it
FAILED normal FAST at both systems-model and test-function-budget gates.

Our test packaging raised the tier to 1506/1500. We grouped the same assertion
bodies into eight natural families without changing any ceiling or guard.
Our new handoff used `status: draft`, outside the native schema, and now uses
`live` with truthful validation state. The original systems diagnostic was
suppressed, so this schema mismatch supports an inference about that failure;
no original D2/D11 trace is claimed. Direct unchanged systems diagnostics and
normal FAST passed after correction. These were our repair/metadata failures,
not baseline environment failures.

The [original failed transcript](initial-ci.log) is 103252 UTF-8 bytes, SHA256
`92fa06435416ef2ede5b0ad8561b76346da453ba5c2e1956ce5f00d82df5573d`.
It remains FAILED; the passing settled run does not relabel it.

# Preservation and endpoint

The frozen EMC ASO NAT submission package remains first priority and awaits
author action. Scientific inputs/results, deposited assets, review seats,
preregistrations, shared queues, paid fleet, categorical no-GPU posture and
publication enforcers are unchanged. No PR, main merge, publication, outreach,
new source acquisition, scientific rescreen/kernel, inference/API or paid
compute job occurred.

Runtime/test/workflow bytes remain exactly those reviewed and tested; the
final handoff/JSON/original-log commit adds documentation evidence only.
Mocks establish reporter behavior, not completeness of live GitHub inventory
or a new CI acceptance policy.

Stop this completed route unless distinct changed input or an independently
demonstrated useful defect appears. Do not repeat an unchanged audit/check
cycle to consume usage. No new task, worker, source cycle, job or monitor is
queued by this handoff; ownership returns to the coordinator.
