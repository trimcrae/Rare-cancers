# Daily status email + weekly newsletter — how it works, and the one remaining step

Automated emails to trimcrae (trimcrae@gmail.com). All times **US Eastern, 12-hour AM/PM**.

## What's live (merged to `main`)
- **Daily status email** — `.github/workflows/daily-degrader-email.yml`, cron `0 11 * * *` (7:00 AM ET).
  Sends: (1) what SageMaker jobs finished in the last ~30h, (2) what's running now (+ spot slots),
  (3) an optimistic day-by-day schedule to PROTAC-degrader-paper completion. Leads with a **bite-sized
  summary**; raw tables are tucked into a collapsed "Full detail" block.
- **Weekly newsletter** — `.github/workflows/method-watch.yml`, cron `0 11 * * 5` (Fridays 7:00 AM ET);
  emails the method-watch digest via `research/modalities/email_digest.py`.
- **Delivery**: Gmail SMTP (repo secret `MAIL_PASSWORD`, a Gmail app password). Shared code in
  `research/modalities/mailer.py` (`send_email` + `llm_summarize`).

## Summary source — priority order (in `daily_status_email.py::build_bodies`)
1. **Claude-written override** — `email-outbox:daily-summary.md` if dated **today** (the cron fetches it).
2. **Anthropic API** — if secret `ANTHROPIC_API_KEY` is set (`llm_summarize`, model `claude-haiku-4-5`).
3. **Deterministic fallback** — always works; concise headline + bullets.

So an email always sends; it just gets nicer prose when (1) or (2) is available.

## The one remaining step — Option B: a scheduled Claude session writes the summary (no API key)
trimcrae chose Option B ("you're Claude, write it yourself"). It needs a **Routine** (scheduled trigger)
that wakes a fresh Claude session at **6:30 AM ET**, writes the summary, and commits it to
`email-outbox/daily-summary.md`; the 7:00 AM cron then sends it. Creating that Routine requires the
**scheduled-triggers / claude-code-remote connector to be authorized** — it was NOT authorized in the
session that built this (every `create_trigger`/`list_triggers` call returned "requires approval").
**Retry from a session where that connector is enabled.**

### Create it with these exact parameters (`create_trigger`)
- **name**: `Daily degrader-paper summary writer`
- **cron_expression**: `30 10 * * *`  (10:30 UTC = 6:30 AM ET; before the 7:00 AM send cron)
- **create_new_session_on_fire**: `true`
- **prompt**:

```
You are a scheduled Claude session. Your ONE job: write today's bite-sized status summary for Tristan
(trimcrae)'s NR4A3 PROTAC-degrader paper and save it so the 7:00 AM ET email cron picks it up. Work fully
autonomously — do not ask questions, do not stop to report progress.

Repo: trimcrae/rare-cancers (use the GitHub MCP tools, prefixed mcp__github__). All times US Eastern, 12-hour AM/PM.

Steps:
1. Dispatch workflow `daily-degrader-email.yml` on ref `main` with input mode=dry_run
   (mcp__github__actions_run_trigger, method run_workflow). This computes the current status facts and SENDS NOTHING.
2. Poll the public Actions API until that run completes:
   curl "https://api.github.com/repos/trimcrae/rare-cancers/actions/workflows/daily-degrader-email.yml/runs?per_page=1"
   ; wait ~15s between polls (background bash sleep — foreground short sleeps are blocked); up to ~5 minutes.
   When status=completed, read that run's job log with mcp__github__get_job_logs (return_content=true, large
   tail_lines). The log contains a "Full detail"/"FACTS" block: what SageMaker jobs finished in ~30h, what is
   running now (with spot slots), and the optimistic schedule with dates + a projected paper-completion date.
3. From ONLY those facts, WRITE a bite-sized summary Tristan can read at a glance on his phone. Use EXACTLY this shape:
   - One headline line: whether things are on track + the optimistic completion date.
   - A line "**Since yesterday**" then 1-4 short bullets on what finished; if a job FAILED or looks stalled, say so FIRST.
   - A line "**Running now**" then short bullets, or "Nothing running."
   - A line "**Path to done**" then one or two sentences of prose timeline naming the next few milestones with
     their optimistic dates, ending at the projected completion date.
   Under ~170 words. Plain prose + short bullets. Bold sparingly. NO tables. Do not invent numbers.
4. Save it: write file `daily-summary.md` on branch `email-outbox` using mcp__github__create_or_update_file
   (first mcp__github__get_file_contents for daily-summary.md on branch email-outbox to get its sha, pass that
   sha to update). Content = your summary. Commit message: "daily summary <today's date>".
5. Stop. Do NOT send any email — the 7:00 AM ET cron reads daily-summary.md and sends it. Do NOT modify any
   other file or branch. If you cannot get the facts after retries, do NOT write daily-summary.md (the cron
   falls back). End with a one-line result.
```

### After it's created
- Fire it once to test (`fire_trigger`), then check `email-outbox:daily-summary.md` updated + the next
  daily email uses it.
- **Weekly newsletter Option B** (optional next): same pattern — a Friday Routine (`30 10 * * 5`) that reads
  the latest method-watch digest (`method-watch-cache:research/method-watch-digest.md`), writes a summary, and
  commits `email-outbox/newsletter-summary.md`; then wire `email_digest.py`/`method-watch.yml` to pick that up
  the same way the daily cron does (fetch email-outbox, use if dated within ~1 day, else fallback).

## Manual controls
- Preview without sending: dispatch `daily-degrader-email.yml` with mode=`dry_run` (downloads a preview artifact).
- Send now: dispatch with mode=`send`.
- Disable newsletter email: set repo variable `NEWSLETTER_EMAIL=off`.
- Override model: repo variable `ANTHROPIC_MODEL`.
