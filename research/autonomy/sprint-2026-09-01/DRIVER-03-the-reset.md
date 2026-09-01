---
id: DOC-SPRINT-DRIVER-03-THE-RESET
title: "The driver's `git reset --hard`, and the third thing it did"
level: L3
kind: incident
status: live
purpose: "The full accounting of one destructive command the sprint driver ran in a shared working tree — what it destroyed, what recovered it, and the consequence neither the driver nor the first seat to report it had noticed."
scope: "One incident. The rule it produced is in SPRINT-CHARTER.md §1a; the seats' own accounts are in their findings files and are the primary record."
audience: [autonomous research agents, maintainers]
date: 2026-09-01
last_verified: 2026-09-01
---

# DRIVER-03 — the driver's `git reset --hard`, and the third thing it did

**2026-09-01, ~20:55Z.** The sprint driver ran `git reset --hard HEAD` in the shared working tree,
inside a loop testing whether stranded branches merged cleanly, tidying up after `git merge --abort`.
Three seats were working in that tree.

## What it destroyed, and what brought each back

| lost | recovered by |
|---|---|
| six manuscript edits a seat had finished and gated | the seat rebuilt them from an atomic script, then **re-derived every figure against the post-reset tree** rather than assuming its inputs survived |
| six re-applied patches from stranded branches | the patch files were in the scratchpad, which a reset does not touch |
| a ledger closure recording a decision trimcrae had made minutes earlier | the script that wrote it was in the scratchpad |
| frontmatter repairs across ~30 files | ditto |
| another seat's `ORDER_BY` fix, a whole findings section, and a repo-wide measurement | the seat re-pushed the code (it had gone to GitHub through the API, so the branch and all four CI runs were unaffected) |

## ⭐ The third consequence, which neither the driver nor the first seat noticed

Two seats reported the incident independently. The first framed it as work destroyed. The second
found something worse:

> ⛔ **A destructive reset does not merely lose work — it can restore a *superseded* claim to
> apparent currency, which is worse, because the next reader gets no signal it was ever corrected.**

Concretely: that seat had written a diagnosis, **refuted it with a later measurement**, and recorded
the correction. The reset removed the correction and left **the refuted diagnosis standing as
current**. Nothing was missing; a section simply ran from (c) to (e), and the wrong claim read as
live.

★ **That is the same shape as everything else this sprint has been finding, arriving through a new
door.** A check that cannot see the history it checks; an error whose body is discarded, so the
reader invents a cause; a hold never consulted at level 0. Here: a correction removed, so the thing
it corrected reads as true. **In every case the artifact looks fine and says something false.**

## The two recovery lessons, both from the seats rather than the driver

1. **Compare each owned file against the copy you pushed, not against your memory of it.** That is
   what surfaced the loss; a reflog alone did not.
2. ⛔ **Re-MEASURE rather than restore.** One seat's destroyed finding was a repo-wide count. It had
   moved (46 → 47 sites, with line numbers shifted, because concurrent seats kept editing those
   files). **Restoring the remembered number would have committed a stale one** — the exact defect
   CLAUDE.md §4 names, reintroduced by an act of recovery.

## Why the rule did not stop it

`SPRINT-CHARTER.md` rule 1 forbids **seats** the git write commands. The driver is the one process in
a wave that legitimately runs git all night, so the rule that would have stopped it read, to its
author, as a rule about somebody else. **New §1a binds the driver**: `git reset --hard`,
`git checkout -- <path>`, `git stash` and `git merge --abort` are forbidden in a shared tree while
any seat runs. A merge that needs aborting belongs in a separate worktree — which is where every
merge in this sprint was already being done, making the lapse gratuitous as well as costly.

⚠ **A shared tree loses work in BOTH directions and neither raises an error.** `git add -A` commits
what a seat is midway through writing (the measured 2026-08-27 incident, which pushed 13 inverted
claims to `origin/main`); `git reset --hard` discards what a seat has finished writing. The charter
had a rule for the first and not the second.

## ⭐ What actually made recovery possible

The two things a hard reset does not touch: **untracked files and the scratchpad.** Charter rule 3
requires each seat to write its findings file *as it goes* rather than as a closing report, and that
file is untracked — so every number needed to rebuild the destroyed manuscript edit was already on
disk. The seat that lost the most work put it best:

> *Had I written the findings file at the end as a report of finished work, one command would have
> destroyed the work and the record of it together.*

⛔ That is the 107-agent fan-out's failure mode — forty successes with nowhere to land — reached by a
completely different route. The rule written to survive a subagent dying also survived the driver
attacking the tree.

## One thing this does not claim

The driver has no way to know whether anything else was lost. Two seats detected their own losses and
reported them; a third may not have noticed, and a seat that had already returned could not report at
all. **The accounting above is a lower bound.**
