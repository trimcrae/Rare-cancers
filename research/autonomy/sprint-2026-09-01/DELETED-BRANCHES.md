---
id: DOC-SPRINT-DELETED-BRANCHES
title: "Stranded branches cleared for deletion, and the deletion this session could not perform"
level: L3
kind: register
status: live
purpose: "The tip sha and written verdict for every stranded branch this sprint established is safe to delete — and the record that the deletion itself was REFUSED by this session's GitHub token."
scope: "Deletions only. The branches that were MERGED are in the commit that merged them; the ones still stranded are in S31-ORPHANS.md and S34-STRANDED.md."
audience: [autonomous research agents, maintainers]
date: 2026-09-01
last_verified: 2026-09-01
---

# Stranded branches cleared for deletion — and the deletion this session could not perform

⛔⛔ **NOTHING BELOW HAS BEEN DELETED. THE ATTEMPT WAS MADE AND REFUSED.** All nine
`git push origin --delete` calls returned `RPC failed; HTTP 403`. The agent proxy is not the
cause — this session pushes branches and merges to `main` through the same proxy all night, and
`__agentproxy/status` shows no relay failure for github.com. **The session's GitHub credential
permits creating and updating refs and does not permit deleting them.**
★ SO THIS FILE IS A CLEARED-FOR-DELETION REGISTER, NOT A DELETION RECORD, and its title says so.
Writing it the other way — after an attempt that failed — would have been a false record of the
same class as a fabricated receipt.
⚠ AND THE HOOK'S COUNT DOES NOT MOVE: 37 branches / 152 commits before the attempt and after it.
`merge-debt-at-turn-end.sh` is explicit that only merging or deleting discharges a branch, and
neither happened here. The verdicts below are real work and the debt is untouched by them.
★ WHAT WOULD ACTUALLY CLEAR THESE NINE: someone with delete permission running the nine commands
in the table, or the nine branches being merged (they are superseded, so each merge is a no-op
against `main`'s content — which is a legitimate way to discharge them without any new access).

⛔ **A DELETED BRANCH'S COMMITS BECOME UNREACHABLE AND CAN BE GARBAGE-COLLECTED, so this file is
written BEFORE the deletion and not after.** Every row carries the tip sha, and every tip was
re-read from `origin` immediately before deleting rather than copied from the report that
recommended it — that re-read is what proves the verdict was made against the branch that actually
exists.

★ **Why deleting is the right move rather than carrying them.** `merge-debt-at-turn-end.sh` was
fixed tonight and now names **37 branches carrying 152 unmerged commits**. Its own instruction is
explicit that recording a branch does not discharge it: *"⛔ It does NOT silence this hook. Only
merging or deleting the branch does."* A branch nobody can delete is carried forever, and a hook
that fires on 37 rows every stop is one that gets tuned out — which CLAUDE.md records as how this
repository has already lost the value of several guards.

★ **The verdict method, and it is content rather than ancestry.** S34-STRANDED classified each
branch by applying its own diff in reverse, per file: if the branch's POST state is already in the
tree, the change is present by content even though `--is-ancestor` says false, because it reached
`main` by a different route. That distinction matters — S31 found one branch byte-identical on HEAD
while ancestry called it stranded.

⚠ **What is NOT in this table, and why.** The branches carrying LIVE work are excluded from the
cleared-for-deletion list entirely: their content was applied as patches in this sprint, and they
must stay until that landing is confirmed on `main` by CI. Clearing a branch whose work exists only
on an unpushed local commit would be the data-loss bug this whole exercise is about.

## Cleared for deletion — attempted 2026-09-01, refused 403

Tip shas re-read from `origin` at deletion time. Per-branch evidence:
[`S34-STRANDED.md`](./S34-STRANDED.md) §2.

| branch | tip | verdict |
|---|---|---|
| `claude/s76-sgk1` | `d40898eb7` | SUPERSEDED — landed on `main` as `61231a22c`. The first hypothesis about this branch (a false `done` row) was **refuted** by that commit. |
| `claude/aut-pd-148-s5-CYC-0074` | `08f02f002` | OBSOLETE — the defect it fixed was closed by a different, better route. |
| `claude/aut-pd-145-s2-CYC-0074` | `76a8f7f2d` | OBSOLETE — same. |
| `s3/aut-pd-031-line-citations-enumerate-carriers` | `429241264` | SUPERSEDED — and superseded again tonight: S3-CITATIONS rebuilt carrier reporting from 32% to 48% citation coverage. |
| `s1-aut-pd-050-unscored-rows` | `d082c01a7` | SUPERSEDED, **and it is the success story** — the ratchet and its vacuity guard landed from it, and the population it was written against reached **0** tonight. |
| `aut-pd-058-deepen-ledger-history` | `4a56de2fa` | SUPERSEDED. ⛔ S34 marks it **do not apply**: it would undo a deliberate later decision. |
| `aut-pd-052-ci-autonomy-tests` | `ff828c1ce` | SUPERSEDED — the wiring it asked for was re-verified as already present rather than re-added. |
| `aut-pd-037-ledger-serialization` | `b29ffc4f1` | SUPERSEDED. |
| `aut-pd-036-ls-files-scope` | `8aeeea201` | SUPERSEDED, cleanly. |

## What this does not claim

⛔ **It does not claim the remaining branches are fine.** All 37 remain — nothing was deleted — and
the hook's own warning
stands: the count is a **lower bound twice over** — refs are only as fresh as the last fetch, and
**this clone is shallow (grafted 2026-08-04)**, so a branch forked below the graft cannot be
classified at all and is counted as neither merged nor stranded. UNMEASURED, not clean.

⛔ **It does not claim a deletion is free.** If any verdict above is wrong, the cost is the work on
that branch, recoverable only while its tip object survives. That is why the tips are here and why
the verdicts cite a reading rather than an impression.
