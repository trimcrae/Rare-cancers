---
id: DOC-AUTONOMY-OPERATING-PROTOCOL
title: Research operating protocol
kind: runbook
status: live
date: 2026-09-04
last_verified: 2026-09-04
purpose: Deliver useful computational EMC research with bounded review and explicit ownership.
audience: [maintainers, autonomous research agents]
scope: Work selection, review, coordination, and the Claude-to-Codex transition.
---

# Research operating protocol

This is the active procedure for both Codex and Claude. The user's 2026-09-04 instruction
authorizes structural changes to improve scientific throughput, cost, and coordination.
Historical runbooks explain old decisions; they do not override this procedure or current user
instructions. Publication permissions remain in `publication-authority.json` and its enforcers.

## Objective and work selection

Optimize for useful evidence that could improve EMC patient outcomes, not paper count, review
rounds, test count, or subscription consumption. Computational work must distinguish prediction,
association, and experimental validation. No wet-lab claim can be established by an LLM review.

1. **PUB-ASO is the first manuscript to finish.** Read its current manuscript, outgoing package,
   existing review evidence, and the dated readiness assessment. Do not start with the degrader
   program's entire roadmap. Its Qeios history remains under the human author's control; its
   intended journal is Nucleic Acid Therapeutics.
2. Until its package is ready or externally blocked, keep one manuscript owner and one separately
   owned process improvement. Parallel evidence retrieval, computation, and independent review
   are useful when they return distinct outputs. Multiple agents must not rewrite the same paper.
3. Choose subsequent projects by clinical relevance, a question public data can answer, credible
   validation, expected information gained, and effort. Record the concrete question and stop
   condition before starting. Reproducible reanalyses, benchmark datasets, and decisive negative
   results can be valuable; do not manufacture papers from work with no useful result.
4. An unrelated red health row or maintenance backlog is not a scientific task. Triage only the
   conditions that affect the proposed action. Enforce real budget, access, ownership, and evidence
   constraints. A process fix must remove observed friction and report its measured effect.

## Review with an endpoint

Freeze the outgoing files and identify their evidence before commissioning a review. Reuse
existing completed reviews when their deliverable digest still matches. Read
`publish_bar.py` for actual acceptance, not the convenience `converged` field alone.

For new work, budget one independent review batch covering claims/citations and methods/results,
one batched repair, and one independent verification of the changed claims and their dependencies.
This is an iteration budget, not a declaration that a paper must pass. Choose additional expert
lenses only for a named uncertainty. Maintain any evidence required by the existing publish bar;
a shorter workflow is not permission to fabricate a review record or override a failed clause.

Each finding names the exact outgoing artifact, evidence, consequence, and smallest correction:

| Class | Meaning | Action |
|---|---|---|
| Submission blocker | A current unsupported/misleading claim, invalid analysis, missing reproducibility evidence, or a real venue requirement | Resolve or narrow the claim before submission |
| Maintenance | Correct current content lacks a regression guard or tooling could be improved | Separate backlog; does not trigger another whole-paper review |
| Editorial suggestion | Optional wording, presentation, or speculative future work | Accept only if it improves clarity without starting a rewrite cycle |

Independently verify findings; reviewer labels are not evidence. Do not require a nonzero finding
count. Record disputed and dismissed findings with reasons. A repair replaces the defective text
and receives a focused evidence check; it does not append defensive paragraphs or reopen every
section. A material methods change may justify broader review; record that reason explicitly.

After the budget is used, return either a verified package or a precise unresolved issue. A new
whole-paper review needs changed scientific evidence, an independently demonstrated material
error, or an external review request. "Another fresh look" and unguarded correct sentences are
insufficient. Never change a real acceptance criterion merely to relabel unresolved work as ready.

## Ownership and integration

Use a separate Git worktree for each writing task. The coordinator alone integrates changes and
writes shared queue/status records. Assign ownership by paper or shared subsystem, not merely by
task name. A process worker must not change its own scientific task's acceptance rules mid-run.

Workers report a needed execution approval to the coordinator before entering a blocking tool
call. The coordinator owns the approval request and keeps its purpose visible to the user.
Do not leave several delegated workers silently waiting on separate permission prompts.

The legacy remote `claim.py` protocol uses a successful compare-and-push to `main` as its lock.
A local file, worktree, or branch is not a remote claim. The new local Codex runner serializes its
own runs using an OS-held lock shared by worktrees; it cannot lock a Claude worker on another
machine. **Do not run both schedulers over the same work.** Before autonomous local execution,
pause/drain the legacy driver and identify outstanding owners. A user-invoked read-only audit
can run while that handover is pending; a local implementation branch is not a live cutover.

Start from a known base. Integrate coherent changes at a settled checkpoint, after checking current
main for conflicts. Do not merge main after every edit or push each status observation separately.
Preserve working branches and evidence until integration. On a collision, leave both versions
intact and reconcile; never choose a winner by last write.

A draft commit on an isolated work branch may anchor generated-artifact provenance before its
manifest is regenerated. Record the pending checks explicitly, generate the manifest from that
committed source, and validate before integration. A draft checkpoint is not a green gate or a
publication candidate. This avoids requiring a clean-source manifest before its source can exist
in a commit.

## Verification and cost

Run the smallest checks that cover the changed behavior during development. Batch all known fixes
and regenerations, then validate the settled tree once. Re-run only for a change, a failure, or an
unresolved concern. Use `scripts/preflight.sh` for the normal commit gate; its reported scope is
part of the result. Full publication verification still uses `PREFLIGHT_FULL=1` on the release
candidate, with its original log and exact revision. A skipped suite has not passed.

Do not add tests that merely pin a sentence, a file length, or a narrative incident. Add behavioral
checks for meaningful failure modes. Retain scientific provenance, arithmetic, reproducibility,
claim-strength, and artifact-integrity checks. An administrative hash mismatch with a safe full
fallback must not force a circular "full must pass before full can pass" repair loop.

Use saved ChatGPT authentication for local Codex work. API use is separately billed and is not an
automatic fallback. Preserve the active no-GPU-spend posture. Set a finite task duration and record
model, effort, base revision, output files, test scope, elapsed time, usage when available, unresolved
issues, and the next concrete action. Unknown remaining subscription capacity stays unknown.

Evaluate improvements by time to a verified artifact, substantive defects found, repair-induced
defects, duplicate work, and observed usage. Do not create work to reach a utilization target.

## Distribution and continuity

Prepare reviewer-readable preprints, reusable data/code, accurate limitations, and venue metadata
together. aiXiv remains an authorized distribution option within the existing grant, not evidence
of scientific credibility. PUB-ASO remains excluded from automatic aiXiv posting. Recheck venue
rules at release time; do not wait indefinitely for a hypothetical higher-visibility AI venue.
Journal submission and outreach follow the user's specific authorization and existing authority.

A cycle ends with a durable outcome and a clear next action. A process launch is not a delivered
result. Do not report a scheduler as active until an actual run produced and preserved its output.
Local runner receipts are not legacy `CYC-*` receipts or publication evidence. A remote cycle must
continue using the existing claim and receipt schemas until its readers are deliberately migrated.

## Basis for this change

The baseline is repository commit `c309b6f6e42ab6adb684c995dc9af2b6caa08fe5`.
`hardening-state/PUB-ASO.json` records round 34 with no blockers and maintenance findings, but its
recorder still used the retired zero-P1 rule. Historical instructions also required repeated blind
review, immediate synchronization, and continuing through an open-ended maintenance backlog.
These mechanisms rewarded activity and made acceptance move while the paper was being repaired.

OpenAI's current [Astra guide](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra)
describes strong multistep research/coding and flags sensitivity to accumulated instructions and
excessive verification. That supports testing concise instructions and bounded review here; it
does not independently validate this project's science. [Codex authentication](https://learn.chatgpt.com/docs/auth)
distinguishes subscription sign-in from separately billed API use.
