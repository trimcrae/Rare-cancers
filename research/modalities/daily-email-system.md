# Daily status email + weekly newsletter — how it works, and the one remaining step

Automated emails to trimcrae (trimcrae@gmail.com). All times **US Eastern, 12-hour AM/PM**.

## What's live (merged to `main`)
- **Daily status email** — `.github/workflows/daily-degrader-email.yml`, cron `0 10 * * *` (**6:00 AM ET**;
  moved one hour earlier 2026-07-17). Sends: (1) what SageMaker jobs finished in the last ~30h, (2) what's
  running now (+ spot slots), (3) an optimistic day-by-day schedule to PROTAC-degrader-paper completion.
  Leads with a **bite-sized summary**; raw tables are tucked into a collapsed "Full detail" block.
  ⚠️ Its Claude summary-writer Routine must run **before** this send — see the 5:00 AM ET target below.
- **Weekly newsletter** — `.github/workflows/method-watch.yml`, cron `0 11 * * 5` (Fridays 7:00 AM ET);
  emails the method-watch digest via `research/modalities/email_digest.py`. Now picks up a Claude-written
  summary the same way the daily email does (`email-outbox:newsletter-summary.md`, accepted if ≤2 days
  old) — see "Weekly newsletter Option B" below.
- **Delivery**: Gmail SMTP (repo secret `MAIL_PASSWORD`, a Gmail app password). Shared code in
  `research/modalities/mailer.py` (`send_email` + `llm_summarize`).

## Summary source — priority order (in `daily_status_email.py::build_bodies`)
1. **Claude-written override** — `email-outbox:daily-summary.md` if dated **today** (the cron fetches it).
2. **Anthropic API** — if secret `ANTHROPIC_API_KEY` is set (`llm_summarize`, model `claude-haiku-4-5`).
3. **Deterministic fallback** — always works; concise headline + bullets.

So an email always sends; it just gets nicer prose when (1) or (2) is available.

## Option B — a scheduled Claude session writes the summary (no API key) — ✅ LIVE (2026-07-15)
trimcrae chose Option B ("you're Claude, write it yourself"). A **Routine** (scheduled trigger) wakes a
fresh Claude session each morning, writes the summary, and commits it to `email-outbox/daily-summary.md`;
the send cron then picks it up.

> **⚠️ 2026-07-17 — send moved to 6:00 AM ET, so the writer Routine must move to 5:00 AM ET (`0 9 * * *`).**
> The send cron is now `0 10 * * *` (6:00 AM ET). The live writer Routine (`Daily degrader paper status`,
> `trig_01PxGLz3puh6Rh9Lsew16Fvk`) currently fires at `0 10 * * *` (6:00 AM ET) — that now **collides with
> the send**, so the 6:00 AM email would go out before today's summary is written and fall back to stale
> prose. **Action (trimcrae, claude.ai Routines UI):** change that Routine's schedule to `0 9 * * *`
> (5:00 AM ET). It was created via `http_api`, so an agent's `update_trigger` cannot edit it — only the UI
> can. (Its prompt still says "7:00 AM ET cron"; that text is cosmetic — the file-handoff mechanism is
> time-agnostic — but update it too if editing anyway.)

**STATUS: created + verified working end-to-end 2026-07-15.** The Routine (`Daily degrader ...`, connector
`Claude_Code_Remote`, source repo `trimcrae/Rare-cancers` attached, daily 6:00 AM EDT) ran via "Run now":
it dispatched the `daily-degrader-email.yml` dry-run, read the FACTS log, and committed a correctly-shaped
summary to `email-outbox:daily-summary.md` (commit "Daily status summary for 2026-07-15"). No further
setup needed.

**⚠️ MUST be created from the claude.ai Routines UI, NOT via the `create_trigger` MCP tool (verified
2026-07-15).** A session CAN create the Routine via `create_trigger`, and it fires — BUT the fired
fresh sessions run **without any `mcp__github__*` connector tools**: `create_trigger` only passes
through connectors the *calling* session holds *and* that are marked passable, and the GitHub grant is
not passable. So a Routine created that way spins up a session every morning that has no way to dispatch
the workflow, read its logs, or commit the summary — it silently does nothing (empirically confirmed:
test fire dispatched no run and left `daily-summary.md` untouched). **Fix: create the Routine from the
claude.ai Routines UI and ATTACH the repo `trimcrae/Rare-cancers` as a source** — that repo source (NOT
anything in the "Connectors" dropdown, which shows "No more connectors available") is what grants the
fired sessions the `mcp__github__*` tools. Verified: a UI Routine with the repo attached dispatched the
workflow and committed the summary successfully. Use the exact name / cron / prompt below.

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

## Weekly newsletter Option B — ✅ CODE WIRED (2026-07-17); needs the Friday Routine created
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

**Action (trimcrae) — create the Friday Routine in the claude.ai Routines UI**, attaching repo
`trimcrae/Rare-cancers` as a source (that repo source is what grants the fired session the `mcp__github__*`
tools — an agent-created `create_trigger` Routine does NOT get them, see the ⚠️ above). Do this **after this
branch merges to `main`** (the `mode=dry_run` input must exist on `main` to be dispatchable).
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
- Send now: dispatch with mode=`send`.
- Disable newsletter email: set repo variable `NEWSLETTER_EMAIL=off`.
- Override model: repo variable `ANTHROPIC_MODEL`.
