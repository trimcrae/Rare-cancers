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

## Creating it — PROGRAMMATIC, IN TWO CALLS

⭐ **THIS SECTION SAID "CREATE IT IN THE UI, AN AGENT CANNOT DO THIS" AND THAT WAS WRONG**
(trimcrae, 2026-08-28: *"Are you sure there's no programmatic way to make a routine? … Seems like a
big oversight to make it need to be manual"*). It was, and the error was **generalising from one
tool's schema to the toolset**: `create_trigger` has no `source_url` parameter, that much is true,
and the conclusion "so it cannot be done" was drawn without looking at the neighbouring call.
**`create_session` HAS one.** Superseded, retained, because the wrong conclusion is the instructive
part: a tested negative about one route is not a negative about the goal.

**The working path is two calls, and the first one is where the repository comes from:**

```
create_session(
    source_url      = "https://github.com/trimcrae/Rare-cancers",
    source_revision = "<branch>",
    outcome_branch  = "<branch to push to>",
    model           = "claude-opus-5",        # pinnable HERE — see below
    prompt          = "<a setup check; make it prove it has the repo before you trust it>")

create_trigger(
    persistent_session_id = "<that session id>",   # mode 2: fire INTO it, do not spawn a bare one
    cron_expression       = "0 14 * * 5",
    prompt                = "<the weekly prompt, written for a session that CONTINUES>")
```

★ **THE DISCRIMINATING FIELD IS `session_context.sources`, AND IT IS READABLE THE MOMENT THE
SESSION IS CREATED** — long before anything runs. Three records, same environment
(`env_01AFwLH33U3ZprSgZf2nbV7S`), same day:

| how it was made | `session_context.sources` | outcome |
|---|---|---|
| trimcrae's UI-created Routine (`EMC research loop — driver`) | `[{git_repository: …}]` | works |
| `create_trigger` alone, `create_new_session_on_fire` | **absent** | ran 26 min, `FAILED`, pushed nothing |
| `create_session` with `source_url`, then `create_trigger` bound to it | `[{git_repository: …, revision: …}]` | setup check passed in 76 s |

⛔ **CHECK THAT FIELD BEFORE BINDING A SCHEDULE TO ANYTHING.** It is the cheapest possible test and
it distinguishes the two failures that look identical from outside — a Routine that fires into a
container with no repository reports `RUNNING` with an advancing timestamp for as long as it flails,
which reads as progress and is not. That is how the field-scan Routine went six weeks undetected,
and it is what a 26-minute run cost here before anyone read `last_run.status`.
⚠ **And a populated field is still only a declaration.** Verify with a setup check the session must
answer — does it have the checkout, on which branch, does the module run — before trusting it with
work. `list_triggers` then reports `last_run.status` per Routine; a repeatedly non-SUCCEEDED row is
the standing signal.

⭐ **THE MODEL IS PINNABLE, AND ON THIS PATH IT IS PINNED AT `create_session`.** ⚠ Measured
2026-08-28 across all 13 Routines in this account: **every one has an empty `model` field**, so each
firing takes whatever the runtime default is — and that default served `claude-sonnet-5` both to the
failed test AND to trimcrae's own `EMC research loop — driver` run at 20:15Z the same evening.
⛔ **That is the absence of a setting, not a choice anybody made**, and it matters here specifically:
this Routine exists to stop things being MISSED, which is the failure a weaker judge produces. The
runner is pinned to `claude-opus-5` and `last_served_model` confirms Opus actually served it.

**Cadence:** weekly, after the Friday digest (`method-watch.yml`, 11:00 UTC Fridays). The digest is
the input, so firing before it publishes matches last week's news against this week's papers.

⚠ **One property of mode 2 to watch.** A persistent session accumulates context across firings, so
this Routine reuses one conversation rather than starting clean each week. That is fine for a small
weekly task and is the reason it can skip re-establishing its checkout — but if the runner ever gets
slow, confused, or starts referring to a previous week's headlines, the fix is to create a fresh
runner with `create_session` and re-bind, not to debug the conversation.
