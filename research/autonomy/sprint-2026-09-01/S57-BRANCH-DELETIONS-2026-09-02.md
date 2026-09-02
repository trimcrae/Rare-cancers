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

---

## ⛔ THE DELETIONS COULD NOT BE MADE — AND THE BLOCK IS THE ENVIRONMENT, NOT THE READING

The seven refs above are read, verified and safe to delete. **They were not deleted**, because
this session cannot delete a remote ref at all. Measured 2026-09-02, two independent paths:

1. **`git push origin --delete <ref>` → `RPC failed; HTTP 403`**, `send-pack: unexpected
   disconnect`, on every one of the seven. ⭐ **The discriminating observation: an ordinary
   `git push origin main` to the SAME remote succeeded seconds earlier**, and the pre-push ledger
   guard ran and passed on the delete attempt too — so this is not credentials, not the network,
   and not a broken remote. It is the delete RPC specifically.
2. **The GitHub MCP server exposes no branch-delete tool.** It carries `create_branch`,
   `list_branches`, `update_pull_request_branch` and `delete_file`; there is no ref deletion.

The agent proxy's own README settles the class: *"organization policy denials (403/407) — report
them instead."* This is a policy denial, so it is reported rather than routed around.

★ **WHAT THIS MEANS FOR THE MERGE-DEBT HOOK, said plainly so the next session does not re-litigate
it.** The hook is explicit that recording a branch does NOT silence it — *"Only merging or
deleting the branch does."* These seven can be neither: merging them adds nothing (that is the
finding above), and deleting them is refused by the environment. **So the hook will keep listing
them, correctly, forever, and that is not a defect in the hook.** It is the one case its remedy
list does not cover: read, superseded, and undeletable.

⛔ **DO NOT retry the deletion, and do NOT "fix" this by weakening the hook** — a guard narrowed to
stop reporting work it cannot clear is worse than one that cries wolf, because the next genuinely
stranded branch would land in the same silence. The remedy belongs to trimcrae, who can delete
these refs from the GitHub UI in under a minute; until then the honest state is
read-and-undeletable, which is what this file records.
