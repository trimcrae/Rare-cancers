---
id: DOC-CODEX-RESEARCH-RUNNER
title: Local subscription research runner
kind: runbook
status: live
date: 2026-09-04
last_verified: 2026-09-05
purpose: Run one bounded research task using saved ChatGPT authentication and preserve its actual outcome.
audience: [maintainers, autonomous research agents]
scope: Setup and operation of scripts/research_run.py; not publication authority.
---

# Local subscription research runner

Run `scripts/research_run.py` with the Python interpreter that has this project's dependencies.
The runner itself uses only the standard library. Install Codex and sign in using ChatGPT. Do not
put subscription credentials in GitHub Actions. Model access and usage remain account-dependent.

```text
python scripts/research_run.py --plan
python scripts/research_run.py --doctor
python scripts/research_run.py --read-only --resource paper:PUB-ASO --task-file task.txt --config research/autonomy/codex-runner.json
```

`--plan` performs no model call or authentication probe. `--doctor` verifies saved ChatGPT
authentication. A read-only run audits a frozen checkout; its returned structured outcome is
saved by the runner. For editing, pause/drain the legacy and remote writers first, then use:

```text
python scripts/research_run.py --claim-coordinator --coordinator-id TASK-ID --ack-local-cutover --note "Previous scheduler paused, writers drained, ownership reviewed"
python scripts/research_run.py --ack-local-cutover --coordinator-id TASK-ID --resource paper:PAPER-ID --task-file task.txt --task-contract contract.json --config research/autonomy/codex-runner.json
```

The acknowledgment describes a real handover. Registration and every writing dispatch verify
that `codex-handover.json` records a disabled legacy driver and that the research ledger has no
outstanding owner. The coordinator's stable task ID persists between heartbeat firings in
`.cache/research-runs/coordinator.json`. All state changes use the runner's existing
`coordinator.lock`, shared by this clone's worktrees. Updated local `claim.py` uses that same lock
and refuses while a Codex coordinator owns the clone. Other updated legacy clones read the fetched
disabled-driver handover before claiming; already running or outdated remote code still requires
the explicit drain. A local record cannot fence another machine.

`--task-contract` contains the selected task's metadata: `kind` must be `science`, `maintenance`
or `review`, and `resource` must match the command. Review tasks require a `review_request` object;
the shared bounded-review reader checks it before authentication or dispatch.
The task description must match this contract. The runner cannot independently infer every review
from arbitrary prose. A manuscript's matching frozen review is reused; a further review needs the
evidence described by `bounded_review.py`.

Inspect ownership with `--coordinator-status`. Transfer it with `--coordinator-id CURRENT
--handoff-coordinator SUCCESSOR --note "..."`; the explicit transfer retains all resource claims.
There is no automatic lease expiry. `--release-coordinator` requires all resources to be resolved.
The OS lock remains free between cycles, so an idle schedule does not keep a process running.

Before dispatching a manual writer, use `--reserve-resource --coordinator-id TASK-ID --resource
paper:PAPER-ID --worker-id WORKER-ID --worktree ABSOLUTE-LINKED-WORKTREE`. Each resource and worktree
can have only one writer. Process workers reserve `process:SUBSYSTEM` the same way. Direct manual
edits must follow these reservations; Git does not prevent a person from bypassing the protocol.
For integration/shared queue writes, hold `local_ownership.Coordinator(root)` and call
`require(TASK-ID)` inside that context. This uses the same OS lock as a worker launch, so integration
and dispatch cannot overlap. Workers do not commit, push, or publish.

Each launch reads the current operating protocol, records its hash, and checks out the committed
HEAD into a separate worktree. **Uncommitted scientific edits are not included.** Commit an
intended candidate before asking the runner to inspect it. Worktrees, exact task/protocol snapshots,
logs, outcomes, and receipts are retained under `.cache/research-runs/` beside the primary clone.
Preserve useful output in the repository before treating it as durable research progress.

The enforced maxima are 1,800 seconds and one dispatch, including direct Python callers. Missing output, incomplete work,
timeouts, authentication failure, and blocked tools produce distinct non-success outcomes.
`completed` means the assigned task completed; it is never a publication verdict. The outcome's
`blockers` list concerns that assigned deliverable only; later publication requirements belong
in `follow_up`. Completion with a real task blocker is still refused. The worker receives the
actual model, effort, time and dispatch limits rather than guessing execution metadata. Usage is
recorded when Codex emits it; token counts do not imply a known remaining subscription allowance.

Completion retains resource ownership until integration. Each returned outcome has a SHA256 and
an inventory of all changed files, including untracked additions and deletions. Missing claimed
artifacts, paths outside the worktree, and worker commits fail the run. After inspecting and
preserving useful output, resolve the resource with `--release-resource --coordinator-id TASK-ID
--resource paper:PAPER-ID --resolution integrated --evidence VERIFICATION-FILE`. The evidence path
and hash remain in ownership history. Use `abandoned` with an explicit reason file for discarded
work; neither resolution deletes the original output. A completed task is never automatically
treated as integrated or publication-ready.

`--recover --coordinator-id TASK-ID` acquires the existing OS lock and marks interrupted run
receipts for reconciliation. It retains partial files, logs, worktrees and resource reservations.
An interrupted or completed unintegrated writer cannot be silently redispatched. Authentication
failure after an authorized launch also produces a retained failed receipt. Ownership-state
corruption fails closed; timestamps never transfer ownership. If the coordinator task itself is
lost, inspect its receipts and the actual schedule, then explicitly hand off using the recorded
identity and a note explaining recovery.

Environment variables for API-key/custom-provider access are refused, and the command pins
ChatGPT authentication and the OpenAI provider. There is no automatic paid fallback. The sandbox
and task contract prohibit network commands, paid compute, external writes, and extra model
dispatches. Time and dispatch limits are enforced by the runner; the prohibition on arbitrary
tool spending is also a task constraint, not a universal billing firewall.

Schedule writing only after one real end-to-end task succeeds and the old scheduler is drained.
A local scheduled task requires the machine and application to be available. A launch or an
authentication success alone does not establish that unattended research works.

On Windows, the runner explicitly selects the documented `windows.sandbox="elevated"`
implementation while retaining its chosen filesystem sandbox and approval policy. The first
audit was blocked before reading files when that setting was omitted. With it set, the
2026-09-04 ASO inventory completed in 97.141 seconds using saved ChatGPT authentication, six
local read/search commands and one model dispatch. The user subsequently confirmed disabling
the Claude driver. A read-only ownership audit found no assigned manuscript owners. The first
writing run produced three ASO submission support files and passed their integrity checks, but
its final receipt was refused because it placed downstream journal requirements in task blockers.
That failed receipt is preserved. The follow-up distinction above addresses the observed contract
ambiguity; it does not change publication acceptance. Current handover and scheduling status are
in `codex-handover.json`; detailed results are in `throughput-2026-09-04/README.md`.

References: [authentication](https://learn.chatgpt.com/docs/auth),
[non-interactive execution](https://learn.chatgpt.com/docs/non-interactive-mode),
[worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees).
