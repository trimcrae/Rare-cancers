---
id: DOC-OPUS-CAPACITY-CAMPAIGN-20260908
title: OPUS-CAPACITY-CAMPAIGN-20260908 campaign manifest
kind: runbook
status: live
date: 2026-09-08
purpose: Durable record of the admitted Opus capacity campaign — environment, model evidence, worker roster, and honest deviations.
scope: >
  The OPUS-CAPACITY-CAMPAIGN-20260908 run only: its measured environment, its worker roster and
  wave structure, its evidence-retention obligations, and the deviations recorded against it. It is
  NOT the campaign's scientific findings (those are the per-worker reports under `reports/` and the
  paper-lane packets) and NOT a standing repository procedure (that is CLAUDE.md and the operating
  protocol).
audience: [maintainers, autonomous research agents]
last_verified: unverified
---

# OPUS-CAPACITY-CAMPAIGN-20260908

Resource process: `OPUS-CAPACITY-CAMPAIGN-20260908`.
Delegated by Codex thread `01a07c26-9379-7d32-b024-61acb86de93f`.
Final scientific integration belongs to thread `01a07c22-89ff-7132-bfd4-7ae6740e516a`.
External submissions/correspondence belong to thread `01a07c5e-3499-78f3-b3f3-af246bd9347a`.
This campaign is the sole launcher/coordinator of these workers.

## Measured environment (recorded 2026-09-08T01:46:00Z)

| Item | Actual observed value |
|---|---|
| Campaign start (UTC) | `2026-09-08T01:46:00Z` (`date -u`) |
| Campaign deadline (UTC) | `2026-09-09T02:37:19Z` (given; ~24.85 h from start) |
| Cloud session ID | `session_01Eui7FVgatEXAwt2N35yHH6` |
| Environment ID / kind | `env_01AFwLH33U3ZprSgZf2nbV7S` / `anthropic_cloud` |
| Origin | `web_claude_ai` |
| Coordinator configured model | `claude-opus-5` |
| Coordinator last served model | `claude-opus-5` |
| Coordinator effort level | `medium` |
| Container CLI version | `2.1.263` |
| Rate limit state at start | `five_hour`, status `allowed`, `isUsingOverage: false` |
| Working branch | `claude/confident-bardeen-ji76cd` |
| Git HEAD at start | `92abbcb905cacf07f14b238db50d1b98f6590374` |
| Disk (`/`) | 252G size, 8.9G used, **29G available** |
| Memory | 15 GiB total, 14 GiB free |
| CPU | 4 cores |
| Tracked files | 7600 |
| Working-copy size | 921 MiB |

## Deviations recorded honestly

1. **Frozen read commit `93b75888e31976195145e2404373b2d7a512f6d1` was not reachable at
   campaign start, and the coordinator has since confirmed why: it had not yet been pushed.**
   Initialization evidence, preserved: `git cat-file -t 93b7588…` -> `bad object`;
   `git fetch origin 93b7588…` -> `fatal: remote error: upload-pack: not our ref`; clone shallow
   at 321 commits; `git fetch --deepen=3000` and `--unshallow` both ->
   `fatal: error in object: unshallow 3e8ba80be192b488a7cd03d1dc87466760a3df7f`.
   Per the 2026-09-08 coordinator correction this is an **infrastructure handoff in progress,
   not missing evidence and not a scientific blocker**. Arbitrary-SHA and unshallow retries are
   stopped. The scientific owner is publishing a scoped supporting-input branch at
   `4878b9b9d1c082cea46e636dad47be419f1fe021` carrying `93b7588` ancestry and the exact
   source-index code / execution / review archives; the remote ref is pending.
   **Interim freeze point actually used: `92abbcb905cacf07f14b238db50d1b98f6590374`**, the remote
   main at handoff and this checkout's HEAD. Wave-1 reads are frozen there; the supporting-input
   branch is fetched and adopted as an additional read input the moment its ref arrives.
2. Two artifacts named in the campaign brief are not present at the interim freeze point (they
   are expected to arrive with the supporting-input branch, so they are pending input, not
   absent evidence):
   `research/autonomy/clinical-methods-checkpoints-2026-09-07` and
   `research/autonomy/cycle-outcomes/20260905T133448Z-6bd43b913c/atlas-primary-matrix-availability.json`.
   No file matching `*source*index*` is tracked either. This is consistent with the confirmed fact that `93b7588`
   was not yet pushed. Absence at this checkout is **pending input, not proof of absence**.
3. **Custom subagent definition files were not used.** No `.claude/agents/` directory exists in
   this repository, and the subagent registry for this session is fixed at session start, so a
   file written mid-session would not register. The documented supported control actually
   exercised is the Agent tool's per-call `model` override (`opus` → `claude-opus-5`) plus the
   catch-all `claude` agent type. Role, tool discipline, bounded turn budget and stop condition
   are carried in each worker's dispatch prompt instead, and the intended definitions are
   recorded in `AGENT-ROLES.md` in this directory. Per-agent `effort` is not an Agent-tool
   parameter in this CLI version; children inherit the session effort (`medium`).
4. Continuous wall-clock occupancy to the deadline is not something a single cloud session can
   assert in advance: the container is reclaimed after inactivity and each wave runs inside a
   turn. Waves are therefore run to completion and refilled, and actual concurrent counts are
   measured per wave in `WAVE-LOG.md` rather than asserted.

## Isolation model (no 20 full copies)

Disk budget requires retaining ≥10 GiB free; 29 GiB is available and a full worktree copy is
~921 MiB, so 20 copies (~18 GiB) is refused as unnecessary. Instead:

- **Shared read-only frozen corpus:** the checkout at `92abbcb9…`, which every worker reads.
- **Write isolation by exclusive path:** each worker owns exactly one report path
  `reports/W##-<slug>.md` and, if it writes code, exactly one directory `code/W##/`.
  No two workers may write the same file. Workers must not edit `main`, other workers' files,
  frozen deliverables, preregistrations, or shared coordination state.
- The coordinator (this session) is the only integrator.

## Standing constraints carried into every worker prompt

No invented facts, sources, patient data, measurements, or test results. No clinical
efficacy/safety/therapeutic-window claims from computation. No wet-lab or reagent design.
No paid API, no GPU spend, no alternative model, no external human contact, no publication,
no PR, no merge, no push. Actual test evidence requires command + environment + exit code;
anything not run is labelled `PROPOSED (NOT RUN)`. A content-policy refusal stops that branch
and is retained, never routed around. Negative results and scope limitations stay intact.
No worker may author or relax its own acceptance criteria.
