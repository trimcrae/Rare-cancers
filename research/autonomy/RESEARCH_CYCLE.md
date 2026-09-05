---
id: DOC-BOUNDED-RESEARCH-CYCLE
title: Bounded research cycle and measured improvement
kind: runbook
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Turn the existing research ledger into finite computational questions and preserve independently verified outcomes.
scope: Local Codex cycles, project selection and process measurement; no publication authority.
audience: [maintainers, autonomous research agents]
---

# One question, one durable outcome

The coordinator reads the operating protocol, current handover, ownership status and latest
cycle outcome. `scripts/research_cycle.py --plan` evaluates the bounded contracts in
`cycle-tasks.json`, linked to existing research-ledger entries. It writes a plan, a task and a
contract under `.cache/research-cycle/`. Planning makes no model call and changes no ledger.
An empty plan removes its generated dispatch files. Generated contracts bind the base revision,
input fingerprint and task text; the runner rechecks current eligibility under the existing lock
before authentication. Regenerate a plan after the base, contract or inputs change. Old copied
contracts cannot redispatch matching completed or attempted work.

Contracts name the question, evidence inputs, allowed outputs, validation and stop condition
before dispatch. Ratings for clinical relevance, answerability, validation and information gained
are explicit coordinator judgements; their sum divided by estimated effort is a planning aid,
not scientific evidence. Negative results receive the same consideration as positive results.
Select only questions public data and available local computation can answer. The initial surface
address sensitivity question was selected because per-sample values already exist and exact
deletion arithmetic can be independently checked. Primary FUS::DDIT3 exon evidence is now
preserved, and a conditional native-prefix comparison is verified in cycle
`20260905T084620Z-b7637a0999`. Its transcript mapping and the exact FUS::CHOP construct used
in the mechanism study remain unresolved; this is not a validated mechanism positive control.

Use the configured Python executable and saved ChatGPT authentication. Claim the existing runner's
coordinator identity, then launch the selected committed checkout:

```text
python scripts/research_cycle.py --plan
python scripts/research_run.py --ack-local-cutover --coordinator-id THREAD-ID --resource paper:PUB-SURFACE-TARGETS --task-file .cache/research-cycle/task.txt --task-contract .cache/research-cycle/contract.json --config research/autonomy/codex-runner.json
```

Retain the 30-minute, one-dispatch budget. Do not change process acceptance while executing a
scientific task. Review requests also pass through `bounded_review.py`; matching frozen evidence
is reusable. A new whole-paper review needs a demonstrated material reason. Publication still
uses the existing publish bar and separate authority.

After the worker stops, inspect its diff and the named outputs. Independently recompute affected
quantities or run appropriate behavioral checks. Record commands, exit codes, full log paths and
SHA256s, output SHA256s, the run ID, next action and measured time to verified output in a
coordinator verification JSON. Counts of substantive and repair-induced defects may be null when
not assessed; do not convert unknown values to zero. Later publication requirements are follow-up,
not blockers of a finished computational task.
For a failed run, record a reconciliation note with the run ID, any actual checks, and the next
action. Collection can preserve it as `attempted` even if authentication failed before the worker
checkout existed or partial output violated its contract. The durable record names those integrity
issues and claims no verified output. Keep the original receipt and partial worktree; resolve the
resource explicitly only after this evidence is preserved. Successful-result integrity checks
still apply in full before any result is recorded as verified. A worker's completion label with
a failed independent check is an attempted outcome, never verified success.

While holding the existing coordinator lock, integrate only the allowed outputs into the
coordinator worktree. `research_cycle.py --collect RECEIPT --plan-file PLAN --verification-file
VERIFICATION --coordinator-id THREAD-ID` preserves the plan, worker receipt, outcomes and check
logs under `cycle-outcomes/RUN-ID/`. It checks the selected input fingerprint, base commit, task
hash, allowed changed paths, integrated output hashes and independent check logs. A worker's
`completed` label alone is insufficient. Collection records operational evidence, never a
publication verdict. Release the resource through the existing runner with the durable cycle
record as integration evidence, then run the settled-tree normal preflight and commit coherently.

# Improvement without an expanding maintenance queue

Compare measured worker elapsed time, time to independently verified output, substantive defects,
repair-induced defects, actual usage and duplicate candidates suppressed. A task with the same
contract and input fingerprint as an earlier outcome is withheld: reuse verified output, or
reconcile the retained failure. Missing or changed completed output requires reconciliation, not
automatic redispatch. Unrelated HEAD changes elsewhere in the repository do not invalidate reuse.

Maintenance needs a recorded observation, measurement and evidence file. When useful science and
maintenance are both eligible, science goes first. At most one maintenance cycle is selected in
four outcomes. An urgent failure preventing safe execution is handled explicitly by the
coordinator, with its reason recorded, rather than disguised as a scientific cycle. No count of
papers, tokens, reviews or subscriptions consumed is a target.

If no contract is eligible, examine one promising existing ledger route and either preserve the
missing primary evidence or define one new bounded question. Do not repeatedly rescore, create
regression guards for correct prose, or dispatch the same failed inputs. A precise evidence gap
and a stopped cycle are valid outcomes. Keep notifications quiet while the state is unchanged.

Runtime dependencies and machine availability are operational prerequisites. A heartbeat entry
is not proof of unattended execution: record the actual scheduled trigger, runner receipt,
coordinator verification and integrated output before claiming that result.
