---
id: DOC-RESEARCHER-FOLLOW-THROUGH-2026-09-05
title: Remaining researcher boundary fixes and reconciliation
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Close demonstrated repeat-work and failed-outcome gaps without reopening completed process or scientific work.
scope: Local cycle dispatch, outcome retention and review resumption; no publication authority.
audience: [maintainers, autonomous research agents]
---

# Reconciled scope

The base is `66c41277ec18cdbe1eb44450fd150292e21760d8`. The earlier structural fixes
are already integrated, as recorded in [the throughput report](../throughput-2026-09-05/README.md).
This follow-up did not restart their implementation or create a maintenance queue.

| Earlier concern | Evidence and disposition |
|---|---|
| Slow/redundant CI | Collector tests improved 126.94 to 9.20 seconds. Cold ablation used 27 rather than 36 subprocesses with identical results; timings were affected by contention. ORCID metadata exclusions, fewer duplicate push triggers, dependency caching and slow-test output are integrated. No additional change was justified. |
| Repeated whole-paper reviews | Bounded dispatch reaches the runner and legacy readers; eight stale candidates were withheld in the existing replay. This follow-up repairs two narrower seat lifecycle gaps below. |
| Writer/process collisions | Persistent coordinator/resource ownership, explicit recovery and separate worktrees are integrated. The original coordinator reserved `process:autonomous-researcher` for task `01a0702e-e20b-7cd3-a16f-508c006698c0` at 06:10:19Z. Only this task wrote process changes. |
| Claude migration/unattended execution | The Claude driver remains disabled. The existing 120-minute heartbeat still belongs to task `01a06e21-2d00-7070-be0b-208dc2bb6ccd`. Its preserved scheduled cycle produced verified science; no second scheduler or ownership transfer was needed. |
| Self-improvement without useful output | Bounded contracts, outcome measurements, science priority and maintenance limits already exist. The remaining fixes concern enforcement at dispatch and collection, not more planning machinery. |

The coordinator confirmed hosted CI run `33942914815` passed at the base. The latest
preserved detailed hosted profile predates that pass, so this task makes no new full-CI
speed claim. A stale scoped-selector stamp safely falls back to full modalities checks;
that does not block normal preflight and was not administratively restamped.

# Demonstrated remaining fixes

1. A no-work plan left its previous `task.txt` and `contract.json` available, and the
   runner accepted a copied completed-cycle contract after resource release. Empty
   plans now remove those generated files. Registered cycle contracts bind the base,
   input fingerprint and task text. The runner rechecks their current eligibility
   under its existing lock before authentication. Changed or unbound plans require
   replanning; generic manual and review contracts retain their existing interface.
2. Failed authentication before checkout creation, invalid partial worker output,
   and failed independent verification could prevent a durable attempted outcome.
   Collection now records these failures with explicit integrity issues and no
   verified artifacts. Successful verification still requires committed evidence,
   allowed worker changes, preserved check logs and matching integrated bytes.
3. Completed focused-review seats did not spend the review budget until the
   hardening summary selected their revision. The seats now enforce their own
   completed budget. The original partial batch can resume; changed deliverables
   and an evidenced material-review reason retain their existing treatment.
4. Reopening an open seat reconstructed it and could replace its frozen request,
   document identity and partial notes. Conflicting supplied values are refused;
   resumption preserves the original record and records the resumption time.

These are operational changes. No manuscript acceptance clause, scientific result,
preregistration, clinical registry, submission authority or historical review was edited.

# Actual validation and measured effect

The [corrected before reproduction](boundary-reproduced.json) failed all 14 new
boundary cases in 9.17 pytest seconds. The [matching after run](boundary-after.json)
passed all 14 in 9.55 seconds. The effect is correct refusal and preserved failure
evidence, not faster pytest. Five stale-dispatch variants previously reached the
authentication spy; afterward all stopped before it. Failed synthetic runs now
produce attempted history and suppress the next unchanged selection.

The [broader targeted run](targeted-final.json) passed **74 tests and 20 subtests in
47.07 seconds** (49.406 wall seconds). It includes an actual local synthetic worker
process through launch, collection, resource release and duplicate refusal, plus
existing timeout, ownership, evidence-tampering, review and seat checks. This fixture
is not an LLM run or a scientific result. Direct Python entry-point validation is
also preserved in `runner-standalone-after.json`: **15 tests and 14 subtests passed in
9.71 seconds** after the import repair; its scope overlaps the broader run.
The settled normal preflight is recorded separately in `normal-final.json` and its
complete log. It covers normal document/artifact gates, not full publication verification.

Original failures are retained. `boundary-before.log` exposed an incomplete test
fixture (missing protocol), corrected before the comparable reproduction.
`targeted-settled.log` exposed a synthetic fixture missing the repository's cache
ignore; the fixture was repaired. Independent focused review found the completed
worker/failed-independent-check case and its repair was included in `targeted-final`.
`runner-standalone-before.log` exposed one repair-induced sibling-import defect,
masked by combined test collection; the direct entry point now resolves its sibling
validator. No earlier failing log is described as passing. Counts overlap.

The [read-only replay](preservation-replay.json), generated by [replay.py](replay.py),
checked **70 preserved files** against the base, with zero mismatches. This covers
the frozen ASO release, Qeios receipt, completed cycle bundle and scientific outputs.
The cycle's own output hashes and independent-check log hashes also match. Planning
took 0.828 seconds; the copied completed-contract guard refused reuse in 0.641 seconds.
No model calls occurred. These local observations do not estimate subscription savings.

[Independent verification](independent-verification.json) is focused process-code and
temporary-fixture review, not manuscript review evidence. Saved ChatGPT authentication,
GPT-6 Astra, the finite 1,800-second/one-dispatch budget and no paid API/GPU fallback
were preserved. Official [non-interactive guidance](https://learn.chatgpt.com/docs/non-interactive-mode)
confirms that the CLI can reuse saved authentication; no new product capability is assumed.

# Remaining external constraints and next action

The actual unattended evidence remains cycle `20260905T032612Z-df96afc413`: 725.563
worker seconds and 818.012 seconds to independently verified output. This task did
not dispatch another scientific cycle. Machine/application availability and saved
subscription authentication remain prerequisites; remaining subscription capacity
is not established by this report.

The current science plan reuses the completed surface sensitivity output and holds
the FUS::DDIT3 comparator for missing preserved primary breakpoint evidence. Source
retrieval is scientific follow-up for the coordinator, not a process completion gate.
Qeios v3 was received and remains pending posting in its durable receipt. NAT remains
unsubmitted and separately authorized. No submission or outreach occurred here.

The original coordinator owns integration and shared state. Deliver the coherent
commits and verification receipts to that task, retain this resource until integrated,
and generate a fresh plan before any later science launch.
