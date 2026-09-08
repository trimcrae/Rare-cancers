---
id: DOC-OPUS-CAMPAIGN-STOPPED-CLOSED-ROUTES
title: "Stopped lane — closed-routes negative record, a held paper"
level: L4
kind: memo
status: live
purpose: >
  Record that a paper lane was dispatched against a held paper in error, was stopped, and what was
  preserved and reverted.
scope: >
  L4. A termination record. It adjudicates nothing and completes no work.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# ⛔ STOPPED — the closed-routes lane targeted a held paper

**My dispatch error, not the worker's.** I assigned a preprint-readiness batch on
`research/manuscripts/methods-record/closed-routes-negative-record.md` (`PUB-CLOSED-ROUTES`). That
exact science and preprint route is under the **CR1 route-permission / merit HOLD**. The lane should
never have been opened, and it was stopped as soon as root's scope correction identified it.

## Termination, exactly

- **Stopped by an explicit task stop**, not by a signal or a timeout. Its last observed state was
  "Now running the permitted checks."
- ⛔ **No adjudication was completed and none is recorded.** Nothing this lane produced is a finding,
  a disposition, or a merit judgement about the held paper.

## What was preserved

The worker had already modified the held manuscript in the working tree (105 insertions, 38
deletions). Both are retained here rather than discarded:

| file | bytes | what it is |
|---|---:|---|
| `partial-edits-INTERRUPTED.diff` | 20,496 | the exact uncommitted diff at termination |
| `WORKING-COPY-AT-TERMINATION.md` | 50,554 | the working copy as it stood, sha256 `1f063903…4aef` |

⛔ **The held manuscript itself was reverted to `HEAD`** so that no edit made under a mistaken
dispatch lands on a held paper. The preserved copies are evidence of what the lane had done when it
was stopped; they are **not** a candidate, not an approved revision, and not to be applied.

## What this does not do

⛔ It does not bypass the hold by a title change, a model change, a rewording or a fresh merit pass.
⛔ It does not reopen `PUB-CLOSED-ROUTES`, and the CR1 route-permission / merit hold stands unchanged.
⭐ The separate **mechanical, immutable-CR1 evidence-representation proposal** remains allowed in the
maintenance lane, and is unaffected by this stop.

The slot was refilled with eligible work from the admitted pool.
