---
id: DOC-ROUTINE-NEWS-MATCH-PROMPT
title: Prompt — weekly news-match Routine
level: L4
kind: memo
status: live
canonical_for: [news-match Routine prompt]
purpose: The verbatim prompt of the weekly news-match Routine, held in the repository so the rules it runs on are reviewable and so recreating the Routine does not depend on reading a config that recreation destroys.
scope: The prompt text and the reasoning for its shape. What the matcher IS lives in scripts/news_match.py and research/method-watch.md — not restated here.
audience: [maintainers, autonomous research agents]
date: 2026-08-28
last_verified: 2026-08-28
---
# Prompt — weekly news-match Routine

**What it does.** Once a week, after `method-watch.yml` publishes the digest, a Claude session reads
the week's headlines, matches them against what each of this program's 32 papers would claim, and
commits the result as an unvalidated queue.

★★ **THE PROMPT IS FOUR LINES, AND THAT IS DELIBERATE.** Every rule the session applies — what
counts as a match, that a negative readout counts as much as a positive one, that `none` is the
usual answer, that it may not invent a publication id — lives in `scripts/news_match.py --prompt`,
which is committed, reviewable and gated by preflight. The Routine's own stored config carries
none of it.

⛔ **That is a fix for a measured defect, not tidiness.** `research/modalities/mailer.py` records
that the newsletter's filter prompt lives in the claude.ai Routines UI, *"which no commit here can
reach"* — and that is precisely how the 2026-08-19 INTerpath-001 readout was lost from the
newsletter: the prompt asked only for methods, and no commit in this repository could correct it.
A Routine that carries the matching rules in its stored config repeats that failure. This one
cannot: edit the rules by editing `news_match.py`.

⚠ **The guards do not live in the prompt either.** `--ingest` re-checks every publication id
against `systems/graph/publications.json`, rejects out-of-range items and empty reasons, and counts
what it drops. A guard that exists only inside a prompt is a guard the next prompt edit deletes.

---

## The prompt

```
Weekly news-match for the EMC research program.

1. Get the digest this week's newsletter published:
   git fetch origin method-watch-cache --depth=1
   git show FETCH_HEAD:research/method-watch-digest.md > /tmp/digest.md

2. Read the brief and answer it:
   python3 scripts/news_match.py --prompt --digest /tmp/digest.md
   Follow its rules exactly. Save your JSON answer to /tmp/answer.json.

3. Ingest and validate:
   NEWS_MATCH_JUDGE="<the model you are>" \
     python3 scripts/news_match.py --ingest /tmp/answer.json --digest /tmp/digest.md
   python3 scripts/news_match.py --check

4. Commit research/literature/news-match-queue.json to main and push.
   Run ./scripts/preflight.sh first; it must pass.

Do not cite anything, do not edit a manuscript, and do not open a PR. The queue is a lead list.
If the digest has no news section, say so and commit nothing — that is an absent reading, not a
reading of absence.
```

---

## Creating it — ANSWERED 2026-08-28, AND THE ANSWER IS "IN THE UI"

⛔ **`create_trigger` DOES NOT PRODUCE A WORKING ROUTINE FOR THIS REPOSITORY. TESTED, NOT ASSUMED.**
An agent-minted Routine was created (`trig_018DLzTW1bGunfsWe25vd8hB`) and fired once. It ran for
**26 minutes** and ended `ROUTINE_RUN_STATUS_FAILED` (session `cse_01NxD3njB5r3UApS4FZFetGn`, fired
22:31:04Z, finished 22:57:02Z), having pushed nothing.

★ **The discriminating observation is one field, and it is visible before the run ends.** Compare
the two `session_context` blocks from `get_session`:

| | `session_context.sources` |
|---|---|
| trimcrae's UI-created Routine (`EMC research loop — driver`) | `[{git_repository: {url: .../Rare-cancers}}]` |
| this agent-created Routine | **absent** |

That is exactly the defect [`field-scan-routine-prompt.md`](./field-scan-routine-prompt.md)
records — *"it was agent-created, so it carries no repo source, and its own STEP 0 `git checkout
main` has nothing to check out"* — and its conclusion, **"recreate it in the UI, not with
`create_trigger`"**, now has a second measurement behind it rather than one.
⚠ **Superseded, retained:** this section previously said that conclusion *"was drawn about a
claude.ai Routine and may not transfer to a Claude Code Remote session"*. It transfers. A CCR
session fired from `create_trigger` gets a container and no repository, which is the same failure
wearing a different mechanism.

⛔ **AND THE FAILURE LOOKS LIKE HEALTH FROM OUTSIDE, WHICH IS THE WHOLE POINT.** For 25 of those 26
minutes the session reported `SESSION_STATUS_RUNNING` with `updated_at` advancing — a liveness
signal that reads as progress and is not one. That is how the field-scan Routine went six weeks
undetected. ★ **The test that works is cheap and is the only one that does: fire it once and read
whether the artifact landed.** `list_triggers` reports `last_run.status` per Routine; a repeatedly
non-SUCCEEDED row is the signal.

**So: create this Routine from the claude.ai Routines UI, with `trimcrae/Rare-cancers` attached as a
source.** That is the one step an agent cannot do for itself here.

⚠ **AND PIN THE MODEL WHILE CREATING IT, BECAUSE NOTHING IN THIS ACCOUNT PINS ONE.** Measured the
same day across all 13 Routines: **every one has an empty `model` field**, so each firing takes
whatever the runtime default is. That default served **`claude-sonnet-5`** to this test AND to
trimcrae's own `EMC research loop — driver` run at 20:15Z the same day. ⛔ **Do not read that as a
setting anybody chose** — it is the absence of a setting, everywhere, and it is worth a decision
here specifically: this Routine's whole purpose is to stop MISSING things, which is the failure mode
a weaker judge produces.

**Cadence:** weekly, after the Friday digest (`method-watch.yml`, 11:00 UTC Fridays). The digest is
the input, so firing before it publishes matches last week's news against this week's papers.
