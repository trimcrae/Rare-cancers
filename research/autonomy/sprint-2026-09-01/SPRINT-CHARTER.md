---
id: DOC-SPRINT-2026-09-01
title: "The 14-hour sprint — charter, seat contract and file-ownership map"
level: L3
kind: process
status: live
date: 2026-09-01
audience: [autonomous research agents, maintainers]
---

# The 14-hour sprint — charter and seat contract

**Authorisation.** trimcrae, 2026-09-01T18:32:47Z, verbatim: *"our usage limit reset and we have 14
hours to use a weeks worth of usage credits. Fan out massively parallel subagents to make sure we
are absolutely maxing out our ability to use tokens here before they reset tomorrow morning anyway.
This means we can advance projects outside of just the ASO paper again"*.

Recorded, with its calibration against the instrument, in
[`autonomy-state.json`](../autonomy-state.json) → `last_utilisation_report_2`,
`budget_hold._SUSPENDED_FOR_THE_SPRINT_2026_09_01` and `_ASO_ONLY_RESTRICTION_LIFTED_2026_09_01`.
**The window closes 2026-09-02T09:00:00Z (5:00 AM ET) and the pre-sprint posture returns then.**

---

## THE SEAT CONTRACT — read this before you do anything

You are one seat of a wave of up to twelve running **concurrently in one working tree**. Everything
below exists because concurrent seats in one tree have already cost this repository real damage
(CLAUDE.md §6: `git add -A` inside a mutation window pushed 13 inverted claims to `origin/main`).

### 1 · ⛔ NEVER RUN GIT WRITE COMMANDS. NOT ONE.

No `git add`, `git commit`, `git push`, `git stash`, `git checkout`, `git rebase`, `git merge`,
`git restore`. The driver commits, staging **by path**, after the wave lands. Reading is fine:
`git log`, `git show`, `git diff`, `git blame` are all yours.

**Why:** twelve seats sharing one index means one seat's `git add` captures eleven seats' work
mid-flight. That is not a hypothetical — it is the measured 2026-08-27 incident.

### 2 · ⛔ EDIT ONLY THE PATHS YOUR PROMPT NAMES AS YOURS.

Your prompt carries an **OWNED PATHS** list. Editing anything outside it collides with another seat
and the collision is silent. If the work genuinely needs a file you do not own, **do not take it** —
write the requirement into your findings file and say which path you needed. The driver sequences it.

Two paths nobody owns and no seat may touch this sprint:

- `research/autonomy/research-ledger.json` — the id allocator collides across concurrent writers
  (AUT-PD-171, open). **Propose ledger rows in your findings file; the driver writes them.**
- `research/autonomy/autonomy-state.json` — the driver's.

### 3 · ⭐⭐ WRITE YOUR FINDINGS FILE BEFORE YOU RETURN. IT IS THE DELIVERABLE.

`research/autonomy/sprint-2026-09-01/<YOUR-SEAT-ID>.md` — a path only you write.

**Why this is rule 3 and not rule 9:** the 107-agent fan-out that this sprint's width is calibrated
against lost its synthesis, and the loss was not the 67 errors — it was that the 40 successes had
nowhere to land and had to be recovered by hand out of `journal.jsonl`. A seat that dies on the way
home must cost its own work and nothing else. **The file on disk is the result. Your returned
summary is a convenience.** Write the file as you go, not at the end.

Required sections:

```markdown
# <SEAT-ID> — <one-line title>
**Item(s):** <ledger ids>   **Owned paths:** <list>   **Started/Finished (UTC):**

## Verdict
FIXED | PARTIAL | REFUTED | BLOCKED | NO-CHANGE-NEEDED — one sentence.

## What I measured
The commands you ran and what they returned. ⛔ Not "probably" — CLAUDE.md §4 wants the
observation that discriminates between the competing hypotheses, cited.

## What I changed
Path-by-path. Empty if nothing changed, and say why.

## What I could not do, and what it is actually waiting on
⛔ "Blocked" is a claim that needs evidence and is usually wrong (CLAUDE.md §0).

## Ledger rows the driver should write
Proposed `what` / `kind` / `state` for each. You may not write them yourself.
```

### 4 · ⛔ REFUTE BY DEFAULT.

Your ledger row is a **claim somebody else made**, often days ago, and this repository's most
expensive recurring defect is a row that was already false. **First establish the defect still
exists, with a command and its output.** A seat that returns "REFUTED — the row describes a state
that no longer holds, here is the reading" has done excellent work, not zero work.

### 5 · Evidence discipline is not relaxed by the sprint.

- A $0 observation is never "watching" — run it before you write the sentence about it.
- Never write an identifier, a PMID, a price or an AI capability figure from recollection. An honest
  **UNKNOWN** costs nothing; a remembered number costs the route.
- A hedge, a null, an UNKNOWN and a negative keep exactly the strength they had.
- Never fabricate medical facts, statistics, citations or patient data.

### 6 · Gates: run what is scoped to your change, never the whole thing.

`./scripts/preflight.sh` is the **driver's** job, once, on a settled tree. Running it from a seat
while eleven others mutate the tree measures nothing. Run the specific linter or test file that
covers your change — `python3 research/manuscripts/lint_consistency.py`, one pytest file — and
report what it said.

### 7 · If you write or widen a guard, mutation-test it.

Break the thing the guard protects **in a scratch copy**, confirm the guard goes red, restore.
⛔ **In a scratch copy or a worktree — never in the live tree.** That is the same 2026-08-27
incident from the other end.

### 8 · Manuscript language discipline applies to every word you write into a paper.

Never imply proteome-wide selectivity, EMC efficacy, safety, a therapeutic window, or clinical
readiness. A correction **replaces** text; it never appends. If a paper is under a word budget,
adding a sentence means removing one.

---

## Wave log

| wave | seats | theme |
|---|---|---|
| 1 | see `WAVE-1.md` | loop machinery, lint tooling, and the concurrency defects the sprint itself depends on |
