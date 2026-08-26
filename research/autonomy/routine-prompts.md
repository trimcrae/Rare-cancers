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
| **Source** | attach `trimcrae/Rare-cancers` | This, and only this, is what grants the fired session the repo and the `mcp__github__*` tools. |
| **Model** | pin it explicitly | Measured 2026-08-26: a fired session ran on a *different model* than its parent. Unpinned, the research loop can change model with nothing in any artifact to show it. |
| **New session each fire** | yes | Fresh context per cycle is deliberate — architecture §4.1. |

---

## 1 · The driver — every 4 hours

**Name:** `EMC research loop — driver`
**Cron:** `13 */4 * * *` *(off the hour on purpose; every scheduled job in the world asks for :00)*
**Creates a new session on each fire:** yes

```
Run one cycle of the autonomous EMC research loop.

Load the `research-loop` skill first and follow its ten-step cycle contract exactly. It is the
procedure; this prompt is only the trigger.

Before anything else, confirm you actually have the repository:

    git -C . rev-parse --abbrev-ref HEAD && git pull --rebase -q origin main

⛔ IF THAT FAILS, STOP AND SAY SO LOUDLY AS THE FIRST LINE OF YOUR FINAL MESSAGE. Do not improvise
around it, do not try to clone. A Routine without the repo source is the known failure that ran
every Friday for six weeks delivering nothing, and a silent failure here is indistinguishable from
a quiet week. The fix is a human recreating this Routine with the repo attached.

Then run the cycle. In short, and the skill has the detail:
  - refuse to start if the loop is unhealthy (`python3 research/autonomy/health.py --check`)
  - re-score the queue (`python3 research/autonomy/priority.py --write`)
  - take the top item that fits the current budget posture, and claim it before working
  - take every free observation first — CLAUDE.md §4
  - do the work, gating with preflight per `repo-gates`
  - if anything goes outward, `research/autonomy/publish_bar.py` decides, not you
  - run `research/autonomy/amendment_guard.py` before committing if you touched a governed path
  - commit and push to main
  - WRITE THE RECEIPT — a cycle without one has failed however much it wrote

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
