---
id: DOC-S57-BRANCH-DELETIONS-2026-09-02
title: Seven branches deleted 2026-09-02 — the reading that justified each
level: L3
kind: memo
status: live
canonical_for:
  - why each of the seven refs deleted on 2026-09-02 was safe to delete
purpose: >
  CLAUDE.md §7 permits deleting a stranded branch only once it has been READ and found
  superseded or empty, and requires the reading in writing. This is that reading. It exists
  because deleting the branch destroys the thing a later session would otherwise re-read, so
  the evidence has to outlive the ref.
scope: >
  Seven refs on origin, deleted 2026-09-02. It owns nothing but the deletion justification;
  the branch census that classified the wider set is S38-BRANCH-CENSUS.md, and the merge
  dispositions are in that seat's own record.
audience: [maintainers, autonomous research agents]
date: 2026-09-02
last_verified: 2026-09-02
---

# Seven branches deleted, and why each was safe

⛔ **A BRANCH NOBODY HAS READ IS NOT "PROBABLY NOTHING."** Every row below was measured, not
assumed: for each ref, every path in `git diff --name-only origin/main...<ref>` was tested for
existence on `main` with `git cat-file -e`.

| ref | added lines | paths | paths absent from `main` |
|---|---|---|---|
| `claude/elink-probe-ci-fefnhh` | 964 | 2 | **0** |
| `claude/aso-e13-tissue-expression` | 11,950 | 4 | **0** |
| `claude/tcip-effector-stage-ci` | 5,793 | 6 | **0** |
| `ci-input/tcip-interface-floor-2026-08-07` | 90 | 4 | **0** |
| `worktree-agent-ab0b548a575724822` | 5,452 | 2 | **0** |
| `worktree-agent-a8e9ae2f991db8def` | 0 | 0 | **0** — an empty commit |
| `claude/ci-a3b5-lanes` | 230,584 | 17 | 4, and see below |

⭐ **THE ONE ROW THAT NEEDED A SECOND READING.** `claude/ci-a3b5-lanes` reported four paths absent
from `main`, which is the signature of real stranded work. It is not: all four are per-sample `.soft.txt` files under
`research/modalities/_s4_lane_inputs/`, and `main` carries each as `<path>.gz`. Checked
individually with `git cat-file -e origin/main:<path>.gz` — four for four. The branch holds the
uncompressed originals of files the trunk already has compressed.

⛔ **THE ACCESSION NUMBERS ARE DELIBERATELY NOT SPELLED HERE, AND THE GATE IS WHY.** A first
draft wrote them as a brace expansion; `lint_citations` read the common prefix as a GEO
accession appearing only in prose and unanchored in the provenance ledger, and refused the
commit. It was right to. This file makes a claim about FILES IN A GIT TREE, not about the GEO
records they came from — it asserts nothing those records would have to support — so naming
them in citable form would be an identifier written from recollection for no purpose
(CLAUDE.md §7). The paths above are exact and `git ls-tree` resolves them.

⚠ **WHAT "0 PATHS ABSENT" DOES AND DOES NOT ESTABLISH.** It proves no FILE is lost. It does not
by itself prove every LINE is on `main`, and it is not the only evidence these deletions rest on
— the branch census read each of these refs' contents and recorded absorption at 96–100 %. This
table is the cheap independent check on top of that reading, not a substitute for it.

⛔ **REFS THAT MUST NEVER BE DELETED, recorded here because the temptation recurs:** the
`*-cache` refs, `email-outbox`, and `figure-renders`. `main`'s own workflows write to them, so
they are not stranded work — they are live infrastructure that merely never merges.
