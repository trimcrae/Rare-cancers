---
id: DOC-DAILY-EMAIL-SYSTEM
title: Status email + weekly newsletter — how it works
level: L4
kind: memo
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `memo` from its location under research/modalities/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# Status email + weekly newsletter — how it works

Automated emails to trimcrae (trimcrae@gmail.com). All times **US Eastern, 12-hour AM/PM**.
**As of 2026-07-26 the only email on a schedule is the weekly Friday newsletter**; the degrader status
email is dispatch-only.

## What's live (merged to `main`)
- **Daily status email — ⛔ RETIRED 2026-07-26, no longer sends on a schedule.** Its `schedule:` cron was
  removed from `.github/workflows/daily-degrader-email.yml` at trimcrae's request. The workflow itself is
  intact and **still dispatchable** (`mode=dry_run` / `mode=send`) — see "Manual controls" — and the file
  carries the exact two lines to re-add on `main` if the daily cadence is ever wanted back. Everything below
  about how it composes (summary priority order, `daily_status_email.py`) still describes the dispatch path.
  Its Claude summary-writer Routine has nothing left to feed, so it is dead weight — see the appendix.
- **Weekly newsletter — the surviving cadence** — `.github/workflows/method-watch.yml`, cron `0 11 * * 5` (Fridays 7:00 AM ET);
  emails the method-watch digest via `research/modalities/email_digest.py`. Now picks up a Claude-written
  summary the same way the daily email does (`email-outbox:newsletter-summary.md`, accepted if ≤2 days
  old) — see "Weekly newsletter Option B" below.
- **Delivery**: Gmail SMTP (repo secret `MAIL_PASSWORD`, a Gmail app password). Shared code in
  `research/modalities/mailer.py` (`send_email` + `llm_summarize`).

## Summary source — priority order (in `daily_status_email.py::build_bodies`)
1. **Claude-written override** — `email-outbox:daily-summary.md` if dated **today**. The workflow step that
   fetches it is deliberately KEPT, so a session that writes a fresh one before a manual `mode=send` still
   gets used. **The file itself was deleted 2026-07-26** (it had been stale since 2026-07-18); with nothing
   writing it, this tier is dormant and the step degrades cleanly to (2)/(3).
2. **Anthropic API** — if secret `ANTHROPIC_API_KEY` is set (`llm_summarize`, model `claude-haiku-4-5`).
3. **Deterministic fallback** — always works; concise headline + bullets.

So a dispatched send always produces an email; it just gets nicer prose when (1) or (2) is available.

## Daily summary-writer Routine — ⛔ RETIRED 2026-07-26
Ran 2026-07-15 → ~2026-07-18: a Routine woke a fresh Claude session each morning, wrote the summary and
committed it to `email-outbox:daily-summary.md`, which the send cron picked up. It is **gone** — trimcrae
confirmed 2026-07-26 that the only Routines still scheduled are the weekly newsletter's, and the daily send
cron it fed has itself been removed (see the appendix). Its setup parameters and prompt were deleted with
it rather than left looking live; recover them from this file's history (`git log -- <this file>`) if the
daily cadence is ever revived. The one lesson worth keeping is immediately below, because it governs the
weekly Routine and any future one.

## ⚠️ Routines MUST be created from the claude.ai Routines UI, not `create_trigger`
**(verified 2026-07-15.)** A session CAN create the Routine via `create_trigger`, and it fires — BUT the fired
fresh sessions run **without any `mcp__github__*` connector tools**: `create_trigger` only passes
through connectors the *calling* session holds *and* that are marked passable, and the GitHub grant is
not passable. So a Routine created that way spins up a session every morning that has no way to dispatch
the workflow, read its logs, or commit the summary — it silently does nothing (empirically confirmed:
test fire dispatched no run and left `daily-summary.md` untouched). **Fix: create the Routine from the
claude.ai Routines UI and ATTACH the repo `trimcrae/Rare-cancers` as a source** — that repo source (NOT
anything in the "Connectors" dropdown, which shows "No more connectors available") is what grants the
fired sessions the `mcp__github__*` tools. Verified: a UI Routine with the repo attached dispatched the
workflow and committed the summary successfully.

## Weekly newsletter Option B — ✅ LIVE (code wired 2026-07-17; Routine confirmed running 2026-07-24)
The newsletter now uses the **same LLM-filter mechanism as the daily email** — a scheduled Claude session
reads the raw method-watch digest, drops the keyword-collision noise (e.g. "ASO Author Reflections" where
ASO = Annals of Surgical Oncology, not antisense; unrelated NR4A3 case reports), and commits a readable
summary that the newsletter send picks up. Without it, the newsletter falls back to the deterministic
"list the section headings" summary — which is why it read as unfiltered noise.

**Code side (done, this branch):**
- `email_digest.py` now prefers `SUMMARY_OVERRIDE_FILE` / `SUMMARY_OVERRIDE` (the Claude-written summary)
  over the Anthropic API over the deterministic fallback — mirroring `daily_status_email.py`.
- `method-watch.yml` gained (a) a `mode` dispatch input — `send` (default; generate digest + email) vs
  `dry_run` (generate + publish the digest to `method-watch-cache`, **no email** — what the Routine
  dispatches to get a fresh digest to summarize); and (b) a "Pick up Claude-written newsletter summary"
  step that fetches `email-outbox:newsletter-summary.md` and uses it if ≤2 days old.

**Routine side — DONE, and verified firing.** It was created in the claude.ai Routines UI with repo
`trimcrae/Rare-cancers` attached as a source (that repo source is what grants the fired session the
`mcp__github__*` tools — an agent-created `create_trigger` Routine does NOT get them, see the ⚠️ above).
Evidence it works: `email-outbox:newsletter-summary.md` was committed at **6:10 AM ET on Friday
2026-07-24**, 50 minutes before that morning's 7:00 AM send, and the send (run `30092329992`) succeeded.
**This is now the only Claude Routine in the system — keep it.** Parameters kept for re-creation:
- **name**: `Weekly method-watch newsletter summary writer`
- **cron_expression**: `0 10 * * 5`  (10:00 UTC = **6:00 AM ET Friday**, one hour before the 7:00 AM send)
- **create_new_session_on_fire**: `true`
- **prompt**:

```
You are a scheduled Claude session. Your ONE job: write this week's short, readable summary of the NR4A3
method-watch digest for Tristan (trimcrae) and save it so the Friday 7:00 AM ET newsletter cron picks it up.
Work fully autonomously — do not ask questions, do not stop to report progress.

Repo: trimcrae/rare-cancers (use the GitHub MCP tools, prefixed mcp__github__). All times US Eastern, 12-hour AM/PM.

Steps:
1. Dispatch workflow `method-watch.yml` on ref `main` with input mode=dry_run
   (mcp__github__actions_run_trigger, method run_workflow). This regenerates the digest and publishes it to
   the method-watch-cache branch; it SENDS NO EMAIL.
2. Poll the public Actions API until that run completes:
   curl "https://api.github.com/repos/trimcrae/rare-cancers/actions/workflows/method-watch.yml/runs?per_page=1"
   ; wait ~15s between polls (background bash sleep — foreground short sleeps are blocked); up to ~5 minutes.
3. Read the fresh digest: mcp__github__get_file_contents for research/method-watch-digest.md on branch
   method-watch-cache. It is a long Markdown digest of literature hits + tool releases, grouped by capability
   topic, each with an "*Unlocks:*" trigger line. MANY HITS ARE FALSE POSITIVES from keyword collisions —
   e.g. "ASO Author Reflections" (ASO = Annals of Surgical Oncology, NOT antisense oligonucleotide), "protein
   dynamics" in a forensics paper, unrelated NR4A3 case reports. IGNORE those.
4. WRITE a short brief Tristan can read at a glance on his phone, keeping ONLY what genuinely matters (a new
   method/tool/model he could run or that changes the plan; a watched tool that shipped a release; a real
   NR4A / EWSR1::NR4A3 / EMC advance). Shape:
   - One headline line: did anything material land this week, or is it all quiet?
   - A few short bullets, each naming the item in bold and one clause on why it matters / what it unlocks.
   - If nothing material changed, say so plainly in one or two lines — do NOT pad.
   Under ~180 words. Plain prose + short bullets. NO tables. Do not invent anything not in the digest.
5. Save it: write file `newsletter-summary.md` on branch `email-outbox` using mcp__github__create_or_update_file
   (first mcp__github__get_file_contents for newsletter-summary.md on branch email-outbox to get its sha, if it
   exists, and pass that sha to update). Content = your summary. Commit message: "newsletter summary <today's date>".
6. Stop. Do NOT send any email — the Friday 7:00 AM ET cron reads newsletter-summary.md and sends it. Do NOT
   modify any other file or branch. If you cannot get the digest after retries, do NOT write newsletter-summary.md
   (the cron falls back). End with a one-line result.
```

### After it's created
- Fire it once (`fire_trigger`) post-merge, then check `email-outbox:newsletter-summary.md` updated, and
  dispatch `method-watch.yml` with `mode=send` (or wait for Friday) to confirm the email leads with it.

## Manual controls
- Preview without sending: dispatch `daily-degrader-email.yml` with mode=`dry_run` (downloads a preview artifact).
- Send now: dispatch with mode=`send`. **This is now the ONLY way the degrader status email goes out** — the
  daily cron is gone.
- Disable newsletter email: set repo variable `NEWSLETTER_EMAIL=off`.
- Override model: repo variable `ANTHROPIC_MODEL`.

## Appendix — superseded cadences
- **Daily status email, cron `0 10 * * *` (6:00 AM ET), live 2026-07-15 → 2026-07-26.** Sent daily; earlier
  it ran at `0 11 * * *` (7:00 AM ET) until moved one hour earlier on 2026-07-17. Removed 2026-07-26 because
  trimcrae did not want a daily email; the weekly newsletter is the intended cadence. Last scheduled send:
  run `30200038716`, 7:23 AM ET on 2026-07-26 (GitHub delayed it ~83 min past the 6:00 AM ET target — the
  usual cron throttling on this repo).
- **Daily summary-writer Routine (5:00 AM ET, `0 9 * * *`), which committed `email-outbox:daily-summary.md`.**
  Already gone — trimcrae confirmed 2026-07-26 that the only Claude Routines still scheduled are the weekly
  newsletter's. That is *why* the daily email kept arriving on generated prose rather than a Claude summary,
  and it is also why deleting a Routine could never have stopped it: **the send was a GitHub `schedule:` cron,
  not a Routine.** `email-outbox:daily-summary.md` was left orphaned by this and was **deleted from the
  `email-outbox` branch on 2026-07-26** (last written 2026-07-18; recoverable from that branch's history).
  The weekly newsletter's own summary-writer Routine and `email-outbox:newsletter-summary.md` are separate,
  still live, and must be KEPT.
