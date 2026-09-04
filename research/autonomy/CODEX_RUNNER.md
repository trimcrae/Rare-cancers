---
id: DOC-CODEX-RESEARCH-RUNNER
title: Local subscription research runner
kind: runbook
status: live
date: 2026-09-04
last_verified: 2026-09-04
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
python scripts/research_run.py --ack-local-cutover --resource paper:PUB-ASO --task-file task.txt --config research/autonomy/codex-runner.json
```

The acknowledgment describes a real handover; it is not a shortcut around it. The lock serializes
only these runner processes in this local clone. Other clones, manual sessions, and Claude
routines are outside that lock. One coordinator integrates completed work after reviewing the
diff and its checks. Workers do not commit, push, or publish.

Each launch reads the current operating protocol, records its hash, and checks out the committed
HEAD into a separate worktree. **Uncommitted scientific edits are not included.** Commit an
intended candidate before asking the runner to inspect it. Worktrees, exact task/protocol snapshots,
logs, outcomes, and receipts are retained under `.cache/research-runs/` beside the primary clone.
Preserve useful output in the repository before treating it as durable research progress.

The configuration limits elapsed time, rounds, and dispatches. A second round, when enabled,
repairs only existing blockers through an explicit session ID. Missing output, incomplete work,
timeouts, authentication failure, and blocked tools produce distinct non-success outcomes.
`completed` means the assigned task completed; it is never a publication verdict. The outcome's
`blockers` list concerns that assigned deliverable only; later publication requirements belong
in `follow_up`. Completion with a real task blocker is still refused. The worker receives the
actual model, effort, time and dispatch limits rather than guessing execution metadata. Usage is
recorded when Codex emits it; token counts do not imply a known remaining subscription allowance.

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
