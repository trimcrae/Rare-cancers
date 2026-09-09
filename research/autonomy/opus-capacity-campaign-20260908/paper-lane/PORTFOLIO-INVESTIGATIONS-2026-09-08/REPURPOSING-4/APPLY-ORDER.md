---
id: DOC-OPUS-CAMPAIGN-REPURPOSING-4-APPLY-ORDER
title: "REPURPOSING rebased diff set — apply order"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Apply order — REPURPOSING rebased set

Target file, single file for the whole set:
`research/manuscripts/repurposing/repurposing-hypotheses.md`

Baseline the set was generated against: worktree HEAD `673d33044` (file byte-identical to the
committed copy; `git status` shows the manuscript unmodified).

## Preferred route — one patch, one check

| # | patch | `git apply --check` in tree | notes |
|---|---|---|---|
| 1 | `REBASED-COMBINED-single-patch.diff` | **0** (`checks/14`) | 10 hunks, +65 −20. Whole set in one apply. Real apply on a scratch copy outside the repo: exit **0** (`checks/17`). |

## Two-step route — same result, if the two authorships must stay separable

Apply **strictly in this order**:

| # | patch | check | notes |
|---|---|---|---|
| 1 | `REBASED-01-cited-reference-sweep.diff` | **0** (`checks/12`) | REPURPOSING-2's cited-reference sweep. 7 hunks. |
| 2 | `REBASED-02-five-unread-references-and-zaltoprofen.diff` | **1** against the bare tree (`checks/13`) — **expected** | 8 hunks. Its base is the post-step-1 file, not the tree. Real cumulative apply after step 1, on a scratch copy: exit **0** (`checks/16`). |

⚠ `checks/13`'s exit 1 is the documented `git apply --check`-is-not-cumulative artefact, not a
defect. Do not "fix" patch 02 to check clean against the bare tree — that would mean dropping
REPURPOSING-2's sweep.

Both routes produce a byte-identical file: `cmp` exit 0 against the same target in `checks/15-17`.

## Superseded — do not apply

* `REPURPOSING-2/PROPOSED-UNAPPLIED-cited-reference-sweep.diff`
* `REPURPOSING-3/PROPOSED-UNAPPLIED-five-unread-references.diff`
* `REPURPOSING-3/PROPOSED-UNAPPLIED-zaltoprofen-parent-histology-ADDS-REFERENCE.diff`
* `REPURPOSING-3/PROPOSED-UNAPPLIED-rebased-onto-REPURPOSING-2.diff`

All four carry a malformed `+++` header (see `FINDING.md` §2) and are superseded here.
