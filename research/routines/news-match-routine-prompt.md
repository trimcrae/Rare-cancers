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

## Creating it

⛔ **A prior Routine in this repository was agent-created, carried no repo source, and delivered
nothing for six weeks** — its own first step, `git checkout main`, had nothing to check out. See
[`field-scan-routine-prompt.md`](./field-scan-routine-prompt.md), which concludes: *"Recreate it in
the UI, not with `create_trigger`."*

⚠ **That conclusion was drawn about a claude.ai Routine and may not transfer to a Claude Code
Remote session, which is a different mechanism** — a CCR session fires into an environment that
already has this repository cloned, which is exactly the thing the field-scan Routine lacked. The
two are not the same failure until somebody checks. **Whichever way it is created, the test is the
same and it is cheap: fire it once and read whether the queue landed.** A Routine that fires and
delivers nothing looks identical to one that was never created, which is how six weeks went by.

**Cadence:** weekly, after the Friday digest (`method-watch.yml`, 11:00 UTC Fridays). The digest is
the input, so firing before it publishes matches last week's news against this week's papers.
