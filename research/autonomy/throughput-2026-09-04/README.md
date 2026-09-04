---
id: DOC-RESEARCH-THROUGHPUT-2026-09-04
title: Research throughput redesign and first ASO result
kind: memo
status: live
date: 2026-09-04
last_verified: 2026-09-04
purpose: Record measured workflow improvements, delivered science and remaining cutover work.
scope: This implementation and its actual checks; no publication-readiness or unattended-writing claim.
audience: [maintainers, autonomous research agents]
---

# Research throughput redesign, 4 September 2026

The first concrete scientific output is a [six-page ASO NAT candidate](../../release-candidates/PUB-ASO/2026-09-04/README.md).
It reduces main text from 3,803 to 2,241 words using the existing typography and margins,
preserves 24 references and three display items, clarifies three claims, and has been checked
in all six rendered pages. The current Qeios text and external deposits were not changed.
Author review, final archive reconciliation, upload variants and release verification remain.

The [operating protocol](../OPERATING_PROTOCOL.md) now prioritizes PUB-ASO, limits work in
progress, assigns one writer per paper and a coordinator for shared state, and gives reviews
a finite endpoint. One independent review batch, one repair batch and one focused verification
replace repeated whole-paper rounds without a material reason. A real unresolved defect still
blocks submission. A missing regression guard for correct content is maintenance.

## Changes with evidence

| Change | Observed basis and result |
|---|---|
| Remove contradictory stopping rules | ASO round 34 had no blockers, but the recorder still required zero P1s even though the publish bar had stopped doing so. The informational summary now agrees with that existing rule. Publication clauses and grants were not weakened. |
| Reduce mandatory context | AGENTS, CLAUDE and three active skills fell from 34,532 to 3,019 words, a 91.3% reduction. The new protocol is additional context. Historical skill details remain in optional references and Git history. This is a size measurement, not a measured 91.3% latency saving. |
| Stop unrelated task expansion | Two Claude Stop registrations requiring more backlog work or unrelated branch merging were removed. Promised-work, escalation and detached-process protections remain. |
| Avoid duplicate full CI runs | Full tests remain on main pushes, pull requests and manual dispatches. Branch pushes no longer duplicate the same full suite immediately before integration. An observed pair ran the same revision twice; the main pytest step took 1,079 seconds. Cache keys now include the dependency-bearing workflow. |
| Fix a measured hot path | Real ligand identification on the existing 7,032-particle fixture fell from 4.429 to 0.022 seconds with equal result dictionaries. Missing OpenMM imports now resolve once per identification. This single local measurement does not predict total CI time. |
| Repair Windows checks | Native path separators caused false parser, map, archive and residue failures. Consistency scans also descended into worktrees and dependency caches. Excluding those directories and normalizing repository paths removed those false findings; `.gitattributes` preserves source line endings. |
| Preserve honest gate scope | FULL plus skipped tests is refused; a paper-scoped run cannot print the unscoped FULL banner. A stale selector record still chooses the full suite, but no longer makes the full run required to refresh that record impossible. |

Raw observations, commands and limits are in [measurements.json](measurements.json).
The CI timing and duplicate runs came from [the main run](https://github.com/trimcrae/Rare-cancers/actions/runs/33903448963)
and [the branch run](https://github.com/trimcrae/Rare-cancers/actions/runs/33903446351).
No hosted run of the final patch has yet been measured.

## Actual Codex execution

The [subscription runner](../CODEX_RUNNER.md) enforces a local coordinator lock, separate worktree,
finite timeout/dispatch limits, process-tree cleanup and durable outcomes. It uses saved ChatGPT
authentication and refuses alternate API authentication; there is no paid fallback.

The [first audit](codex-audit-blocked.json) authenticated but could not read files. Explicitly
selecting the documented Windows sandbox implementation corrected the configuration omission;
the [second audit](codex-audit-completed.json) completed the ASO submission-material inventory in
97.141 seconds with six read/search commands, one dispatch and no edits. Its outcome distinguishes
files merely listed from files actually inspected. Token usage was 241,109 input, including
195,200 cached input, and 1,242 output. These totals include repeated context across tool calls;
they do not establish remaining subscription capacity or API charges. The smoke checkout still
contained the old committed entry instructions; the shortened instructions were not benchmarked.

This verifies the read-only path. It does not establish that a recurring writing scheduler is
running. The legacy Claude driver status remains unconfirmed, so autonomous writing has not been
activated. After handover, the next bounded writing task should finish the accepted ASO upload
package rather than open another review round or another paper.

## Verification and integration status

Checks performed, with overlap between groups:

- CI and selector behavior: 72 passed in 23.10 seconds.
- Windows portability: 91 passed, 1 skipped in 20.75 seconds; [log](portability-tests.log).
- Final archive/preflight behavior: 27 passed in 2.82 seconds; [log](archive-portability-tests.log).
- Runner behavior after the Windows setting: 14 passed in 11.463 seconds.
- Review recorder plus existing receipt contract: 29 passed in 1.29 seconds.
- Candidate PDF: six pages, all input hashes match, six printed manuscript sequences present,
  all pages visually inspected; detailed checks are in the candidate bundle.

The final normal preflight **passed in 71.844 seconds**; see the [complete log](normal-preflight.log)
and [checked snapshot and artifact hashes](normal-preflight-result.json). It checked document and
artifact gates against source commit `1a2d667d77405070d794b1383961bacf3ad2951f` plus the two regenerated
ASO records. The manifest truthfully names that clean source commit; its 516-file inventory, DOI
and scientific gaps are unchanged. Comparison with the actual published revision reports
27 changed files, one added and none removed. The initial native run failed in 217.641 seconds;
these runs establish the portability repair, not a controlled speed benchmark.

This result is a normal document/artifact check, not a FULL or publication receipt. Focused tests
are listed above; no full scientific test suite has been run for this patch. Changes are saved on
`codex/research-throughput-2026-09-04`; active `main` is unchanged. Writing cutover remains pending
confirmation that the legacy Claude driver has stopped. No preprint or journal submission occurred.

OpenAI's current [Astra guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra)
supports testing smaller instruction sets, explicit delegation and bounded verification; its
capability claims do not validate the science here. The implementation follows official
[subscription authentication](https://learn.chatgpt.com/docs/auth) and
[non-interactive execution](https://learn.chatgpt.com/docs/non-interactive-mode) documentation.
