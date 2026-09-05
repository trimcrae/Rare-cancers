---
id: DOC-RESEARCHER-COMPLETION-2026-09-05
title: Measured researcher improvements and operational cutover
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Record implemented process changes, measured benefits and the evidence required for unattended research.
scope: Computational researcher implementation; frozen ASO release and publication authority preserved.
audience: [maintainers, autonomous research agents]
---

# Implemented changes

The [performance record](performance/README.md) profiles actual repeated work. The five collector
contract tests took 126.94 seconds before and 9.20 seconds after isolating a leaked control-plane
network request; all five assertions still pass. Four cold claim ablations took 340.81 seconds
before and 296.21 seconds after mutation-only early stopping, with 36 versus 27 subprocesses,
identical full result dictionaries and unchanged manuscript hashes. Concurrent local tests affected
those timings. This is a measured workload comparison, not an estimate of the new full CI duration.

Eight checksum-valid ORCID digit sites were being perturbed as scientific quantities. They are
now excluded while adjacent gene identifiers and scientific values remain tested. The affected
cache entries are invalidated. The metadata-heavy span completed in 69.23 seconds after the fix;
the original probe was interrupted after more than six minutes, so there is no exact before/after
ratio. Preflight retains slow-test durations for subsequent full runs. The historical full ASO
release remains 2,961 seconds, including 2,239.13 seconds for manuscripts, 538.22 for modalities and
104.04 for pure logic. Its complete release evidence is unchanged.

[Bounded review](../BOUNDED_REVIEW.md) now reaches the runner, legacy claims, continuity, handoff,
seat creation, readiness notifications and goal readers. The [replay](bounded-review-replay.json)
withheld eight stale whole-paper review candidates among 172 legacy candidates in 0.561 seconds.
Five of nine historical ASO rounds incorrectly counted a rollup as an extra reviewer; counting is
corrected without altering old evidence. Notifications follow deliverable bytes and author action,
so unrelated commits do not restart readiness. Scientific acceptance and publication authority
remain separate from dispatch permission.

The [existing runner](../CODEX_RUNNER.md) now retains coordinator identity and paper/subsystem
reservations through integration. It shares its original OS lock with local legacy claims, rechecks
the disabled-driver handover, refuses duplicate dispatch, preserves interrupted output and requires
explicit recovery/disposition. Tests exercise real competing Git claims and process death. An
existing canonical-byte test also exposed Windows newline conversion in the ledger writer; the
writer and claim withdrawal now preserve the required bytes.

The [cycle adapter](../RESEARCH_CYCLE.md) attaches finite computational questions to existing ledger
routes, requires committed input hashes and independently verified output/log hashes, preserves
atomic outcome bundles, and withholds identical completed or failed work. Selection assessments
are explicit judgements. Useful science precedes independent maintenance; maintenance requires
observed friction and normally occupies at most one of four cycles. The first selected question
tests single-sample and comparator-histology sensitivity of eleven existing therapeutic-address
expression reads. It does not create an efficacy, safety or surface-protein claim.

# Verification and scope

The integrated behavioral run passed **67 tests and 20 subtests in 36.10 seconds**; see
[the complete log](targeted-settled.log) and [execution receipt](targeted-settled.json). Independent
review reproduced one material input-provenance bug in the new cycle collector; the
[focused repair verification](cycle-independent-review.json) confirmed that dirty coordinator
inputs and changed worker inputs are refused, while matching committed evidence succeeds.

Additional worker checks overlap this integrated scope: 109 performance checks, 215 review/legacy
reader checks plus eight final revision checks, and 139 ownership/legacy checks before the newline
defect followed by 28 affected checks after its repair. The original failing ownership log is
preserved with the passing repair log. Counts are not additive. The settled normal preflight
passed in **136.875 seconds**; its [log](normal-settled.log) and [receipt](normal-settled.json)
record the document/artifact scope. The source revision had no tracked diff; the running log was
an untracked verification output, so the preflight truthfully printed `+dirty`. No scientific
pytest suite is claimed by this normal check, and it is not full publication verification.

# Ownership, schedule and preservation

The existing `emc-research-coordinator` heartbeat was preserved in
[its original configuration](automation-before.toml) and paused before implementation. No second
scheduler was created. The same durable ownership record supports explicit transfer back to
the original task for scheduled execution. Current owner, actual schedule state and observed
scheduled outcomes are recorded in [the handover](../codex-handover.json) and the cycle outcome
directory created by collection. A configured heartbeat alone does not establish unattended
operation. Each actual cycle must preserve its runner outcome, independent verification and
integrated result. Machine/application availability remains required.

Saved ChatGPT authentication passed the [live prerequisite probe](subscription-doctor.json).
The model remains GPT-6 Astra at high effort, with a 30-minute/one-dispatch limit and no paid API
fallback or GPU spending. Current official [Astra guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra)
supports explicit delegation and bounded verification, while [authentication documentation](https://learn.chatgpt.com/docs/auth)
distinguishes subscription sign-in from API billing. Those product capabilities do not validate
scientific findings.

The exact Qeios v3 receipt from the source checkout is preserved; the three upload-file hashes
[still match](aso-preservation.json). Qeios received the submission and posting remains external.
There was no resubmission. NAT remains unsubmitted and separately authorized. No ASO manuscript,
frozen release artifact, clinical registry or preregistration was rewritten.
