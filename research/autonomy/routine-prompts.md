---
id: DOC-AUTONOMY-ROUTINE-PROMPTS
title: The two Routine prompts trimcrae pastes into the claude.ai UI
level: L4
kind: runbook
status: live
canonical_for: [autonomy driver Routine prompt, autonomy escalation Routine prompt]
purpose: >
  The exact text of the two Routines that drive the autonomous research loop, kept here because a
  Routine's prompt is stored only inside the Routine and is lost when it is deleted.
scope: >
  The prompts and their creation parameters only. The loop's design is the autonomy architecture; the
  cycle contract is the `research-loop` skill. Neither is restated here.
audience: [maintainers, autonomous research agents]
date: 2026-08-26
last_verified: 2026-08-26
related: [DOC-EMC-AUTONOMY-ARCHITECTURE, DOC-METHOD-WATCH]
---

# The two Routines — and why this file exists

★★ **AND THE LOOP CANNOT EDIT THEM — measured 2026-08-26.** `update_trigger` refuses any Routine
`created_via: http_api`: *"Agents can only update routines they created."* The loop may DISABLE the
driver (that one exception is allowed, so a broken loop can stop itself) and may fire it, but every
retime or rewrite is **trimcrae pasting again**. ⭐ **So keep these prompts THIN.** The cycle contract
belongs in `.claude/skills/research-loop/SKILL.md`, which the loop can edit; a contract pasted into a
Routine prompt is frozen at whatever was last pasted by hand.

⛔ **A Routine's prompt lives ONLY inside the Routine.** Delete it and the text is gone. The
field-scan Routine's prompt was lost exactly that way and had to be recovered from git history. So
both prompts are archived here, and **this file is updated in the same commit as any change to
them.**

★★ **BOTH MUST BE CREATED FROM THE claude.ai ROUTINES UI, NOT BY AN AGENT.** Measured twice and
re-tested 2026-08-26: an agent-minted Routine carries no `sources` grant, so its fired sessions get
no repo and no GitHub tools. It fires, reports `SUCCEEDED`, and delivers nothing. See the
[architecture](../manuscripts/program/emc-autonomy-architecture.md) §2.2.

**When creating each one, three settings are load-bearing and none of them is a default:**

| setting | value | why |
|---|---|---|
| **Repository** | attach `trimcrae/Rare-cancers` | ⛔ **THE ONE THAT DECIDES WHETHER ANY OF THIS WORKS.** It defaults to unset, showing "Default" — and unset is the known failure: no repo, no `mcp__github__*`, dies at the prompt's first line, reports `SUCCEEDED`. |
| **Model** | pin it explicitly (Opus 5) | Measured 2026-08-26: a fired session ran on a *different model* than its parent. Unpinned, the research loop can change model with nothing in any artifact to show it. |
| **Connectors** | ⛔ remove every one, including `visualize` | The UI warns, correctly, that a connector's tools — writes included — are used without asking during a run. Neither Routine needs one. |
| **Notify when the routine finishes** | ⛔ **OFF for the driver, ON (push) for the sweep** | The driver fires ~6×/day and its whole contract is to stay silent unless one of the four escalations fired. A per-run summary would undo that, and six pings a day is the noise that makes the real message invisible. The sweep is the one whose job IS to notify. |
| **Auto-fix pull requests** | off | The loop commits to `main` directly and opens no PRs, so the setting is moot. |

⚠ **THERE IS NO "new session each fire" SETTING, AND LOOKING FOR ONE WASTES A MINUTE** (trimcrae found
this while creating them, 2026-08-26). A *scheduled* Routine always starts a fresh session; the
persistent-session mode exists only for a trigger an agent creates and binds to a named session
(`persistent_session_id`), which the UI has no way to express. So architecture §4.1's fresh context per
cycle is the platform's default here, not something to configure. ⛔ *Superseded, retained: this table
listed "New session each fire: yes" as a setting to choose.*

⚠ **The trigger picker takes friendly times, not cron.** The sweep's daily time maps directly. For the
driver, use an every-4-hours option if the picker offers one; if it only offers daily, use **"Add
another trigger"** six times at 12:13 AM / 4:13 AM / 8:13 AM / 12:13 PM / 4:13 PM / 8:13 PM ET, which is
the same schedule. The cron strings below are the canonical form for anything creating these by API.

---

## 1 · The driver — every 4 hours

**Name:** `EMC research loop — driver`
**Cron:** `13 */4 * * *` *(off the hour on purpose; every scheduled job in the world asks for :00)*
**Creates a new session on each fire:** yes

```
Run one cycle of the autonomous EMC research loop.

Before anything else, confirm you actually have the repository:

    git -C . rev-parse --abbrev-ref HEAD && git pull --rebase -q origin main

⛔ IF THAT FAILS, STOP AND SAY SO LOUDLY AS THE FIRST LINE OF YOUR FINAL MESSAGE. Do not improvise
around it, do not try to clone. A Routine without the repo source is the known failure that ran
every Friday for six weeks delivering nothing, and a silent failure here is indistinguishable from
a quiet week. The fix is a human recreating this Routine with the repo attached.

Now load the procedure. Try the `research-loop` skill first. ⚠ IF YOU HAVE NO `Skill` TOOL — a
scheduled Routine's tool surface is narrower than an interactive session's and may not include it —
then read the file, which is the same text:

    cat .claude/skills/research-loop/SKILL.md

Either way, READ it before acting. It is the ten-step cycle contract; this prompt is only the
trigger, and it is deliberately thin because you can improve that file and cannot improve this
prompt. ⛔ Do not run a cycle from the summary below alone.

  - refuse to start if the loop is unhealthy (`python3 research/autonomy/health.py --check`)
  - re-score the queue (`python3 research/autonomy/priority.py --write`)
  - take the top item that fits the current budget posture, and claim it before working
  - take every free observation first — CLAUDE.md §4
  - do the work, gating with preflight per `repo-gates`
  - if anything goes outward, `research/autonomy/publish_bar.py` decides, not you
  - run `research/autonomy/amendment_guard.py` before committing if you touched a governed path
  - commit and PUSH TO main
  - WRITE THE RECEIPT to research/autonomy/receipts/ — a cycle without one has failed however much
    it wrote, because the health checker reads receipts and never fire records

⚠ PUSH TO `main`, explicitly. This Routine carries an auto-generated outcome branch you did not
choose; ignore it. CLAUDE.md §7 makes branch drift a data-loss bug — a receipt on a branch nobody
reads is a cycle that looks delivered and is not.

⚠ You may also have no `Task` tool, so parallel subagents may be unavailable. That is fine: take ONE
item and do it properly. Do not reshape the work to fit a missing tool.

Escalate only the four things the skill names. Everything else is silent: no status report, no
"here is what I could do next", no asking which of several self-doable things to start with.

Your final message is short: what you took, what changed, and `route_advanced`. If the cycle did
nothing, say that plainly rather than describing what you looked at.
```

---

## 2 · The escalation sweep — daily

**Name:** `EMC research loop — escalation sweep`
**Cron:** `47 12 * * *` *(8:47 AM ET)*
**Creates a new session on each fire:** yes

```
Sweep the autonomous research loop for anything that needs trimcrae, and for nothing else.

Confirm the repo first — `git -C . rev-parse --abbrev-ref HEAD` — and if it fails, say so loudly as
your first line and stop.

    git pull --rebase -q origin main
    python3 research/autonomy/health.py --check
    python3 research/autonomy/amendment_guard.py --check-log

Read the receipts in research/autonomy/receipts/ since your last sweep. You are looking for exactly
four things, and you must not manufacture a fifth:

  1. A journal submission recommended — send it immediately with the top three venue fits and the
     evidence behind each (research/autonomy/venue_fit.py), not a recommendation alone.
  2. Spend crossing "expensive", or a DRIFT row we would otherwise buy.
  3. A goal-changing fact — the north-star route closed, or a capability landed that reorders the
     portfolio.
  4. The loop itself unhealthy — a health condition red past its deadline, an amendment log with
     problems, or three consecutive receipts reading `route_advanced: none`.

⛔ If none of the four holds, SEND NOTHING AND SAY NOTHING. A daily "all clear" is the noise that
makes the real message invisible, and the weekly newsletter already carries ambient state.

If one does hold: PushNotification (one line, under 200 characters, no markdown) AND AskUserQuestion
with the decision and enough context to answer without scrolling back. Write both in plain language
— lead with the point, one idea per sentence, jargon replaced rather than glossed.

Do not do research in this sweep. Do not fix things. If you find work, add it to the ledger and let
the driver take it.
```

---

## 3 · After creating them — verify by ARTIFACT, never by fire record

⛔ **A fired Routine is not a delivered one.** Both Routines' first runs are checked the same way:

```bash
ls research/autonomy/receipts/          # the driver must produce one per cycle
python3 research/autonomy/health.py     # cycle_delivering goes green only on a real receipt
```

**Two consecutive cycles with receipts** is the definition of done for this phase. A `SUCCEEDED` run
record proves only that a session started — the same status was returned by the probe that ran four
minutes and wrote nothing.
