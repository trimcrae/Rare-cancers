---
id: DOC-OPUS-CAMPAIGN-R4-ROBUSTNESS-STOPPED-DUPLICATE
title: "R4 zero-handling robustness — STOPPED as a duplicate of completed work"
level: L4
kind: selection-record
status: stopped
date: 2026-09-08
last_verified: 2026-09-08
---

# R4 zero-handling robustness — STOPPED, duplicate

**Selection error by the parent, caught by the launcher's reconciliation and corrected here.**
Same cause as the R1 case: I dispatched from the retained backlog's ready list
(`PROPOSAL-next-work-backlog.md` lines 302–355) without first checking the lane directory for a
completed sibling.

## The completed work this duplicates

| | |
|---|---|
| lane | `R4-zero-handling-sensitivity/` |
| commit | `78f268caf`, *"R4: the zero-handling invariance is a tautology of the panel's construction, not robustness"* |
| artifacts | `R4-per-gene-convention-table.tsv` (2,587 lines), `R4-sign-rank-sensitivity.tsv` (863 lines = 862 genes + header), `R4-summary.json`, `R4-zero-handling-sensitivity.md` (304 lines), `r4_zero_handling_sensitivity.py` (381 lines), `R4-run-log.txt` |
| closure | root's dated interpretation correction at `1dd53f562`, "R4 bracketing" |

That lane already computed the per-gene δ under the three conventions across all 862 panel genes and
the sign/rank sensitivity — precisely the measurement my contract asked for. Its conclusion is
already recorded and is **stronger and less flattering** than "robust": the invariance is a
**tautology of the panel's construction**, not evidence of robustness.

## Actual execution record produced before the stop

**None.** The agent was stopped while reading its specification, before any command ran and before
any file was written. No tracked file was modified and no artifact directory content was produced.
There is no execution stream to preserve, and none is reconstructed.

## Disposition

**Stopped, not paused.** Nothing outstanding sits behind this label. The completed lane's finding
stands as written and is not to be re-run, re-graded, or extended under a reused label.
