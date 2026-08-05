---
id: DOC-NOTIFICATION-CHANNELS
title: Push channels — what can reach trimcrae, and why almost nothing does
level: —
kind: runbook
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `runbook` from its location under research/compute/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# Push channels — what can reach trimcrae, and why almost nothing does

**This file owns the answer to "can this repo notify trimcrae, and how?"** Per CLAUDE.md §1, every other file
points here rather than restating it. Workflows carrying (or having carried) a notification step link this
file from their header; do not re-type a channel's status into a workflow comment.

> **trimcrae, 2026-07-31, verbatim: "You're emailing me way too much. You should not be emailing me."**

That is the governing instruction. Supervision must survive with no LLM in the loop — that was always the
requirement, and it is a **pull** requirement. Being *told* was never part of it.

Measured 2026-07-31. Every claim below has a run/job ID or a file:line next to it.

---

## 1 · The inventory — every push path this repo has

| # | path | can it reach his inbox? | status now |
|---|---|---|---|
| 1 | **GitHub Issue activity** — open/comment/close by anyone, including `github-actions` | **Yes**, via his GitHub notification settings | ⛔ **removed.** `issues:` permission revoked from both alarm workflows; `alarm_issue.py` deleted |
| 2 | **Failed SCHEDULED workflow run** — GitHub emails the repo owner | **Yes**, once per failing run, no memory, no dedupe | ⚠ **still live for 9 workflows** — see §4. Removed from the 2 alarm workflows |
| 3 | `lane-staleness-watch.yml` mail step | never delivered (SES `AccessDenied`) | ⛔ **step deleted** |
| 4 | `step1-fanout-autoscale.yml` → "Push the verdict to a human (SES)" (`if: failure()`, ~line 435) | never delivered — passes AWS keys, **not** `MAIL_PASSWORD`, so it takes the SES branch | ⛔ **neutralised at the mailer**, see §3. The file itself belongs to another lane and was not edited |
| 5 | `daily-degrader-email.yml` → `daily_status_email.py` | **Yes** — passes `MAIL_PASSWORD`, so Gmail SMTP, proven working | 🟡 **no cron** (removed 2026-07-26 at his request); manual dispatch only, and `mode` defaults to `dry_run` |
| 6 | `method-watch.yml` → `email_digest.py` | **Yes** — Gmail SMTP, `cron: 0 11 * * 5` (Fridays) | ✅ **left alone deliberately** — CLAUDE.md §5 calls the weekly newsletter "the surviving cadence". This is a *wanted* email |

Nothing else in the repo calls a mailer:
`grep -rn "import mailer\|send_email(" --include=*.py --include=*.yml` returns only the rows above.

---

## 2 · What went wrong, and it was not a bug

The escalation was rebuilt on 2026-07-31 as a GitHub Issue channel: one open issue per condition, a comment
only when the verdict changed, auto-closed on recovery, silent on unmeasured verdicts. **It worked.** That
was the problem — every issue write emails the repo owner, so a channel built to be *reliable* was by
construction a channel that mailed him, and the self-test proving it worked mailed him four more times.

Issues **#17** (self-test) and **#18** (a deliberately induced real condition) were the only two ever opened.
Both are closed; no alarm issue is open.

**The lesson, stated so it is not re-learned:** dedupe and auto-close were not the fault. *Choosing a push
channel at all* was. Before building any notification, check whether the requirement is "someone must be able
to find out" (pull) or "someone must be told" (push). It was the former.

### The prior defect this replaced, for the record

`lane-staleness-watch.yml`'s mail step passed `AWS_ACCESS_KEY_ID`/`SECRET`/`REGION` and `MAIL_TO` — and **not
`MAIL_PASSWORD`**. `mailer.send_email` picks SMTP only when `MAIL_PASSWORD` is set, so every call took SES:

```
ClientError: An error occurred (AccessDenied) when calling the SendEmail operation: User
`arn:aws:iam::646605541856:user/nr4a3-ci-submitter' is not authorized to perform `ses:SendEmail'
```

- Run `30602768073`, job `91068780404`. `mode=probe` fails one call earlier on `ses:GetSendQuota` (run
  `30626375302`, job `91142503053`) — the IAM user has **no SES permissions at all**.
- It was **never the SES sandbox**, which the old comment claimed: a sandboxed account answers
  `MessageRejected: Email address is not verified`, a different error with a different fix.
- `MAIL_PASSWORD` has never appeared in that workflow in any commit on any branch
  (`git log -p --all -- .github/workflows/lane-staleness-watch.yml | grep -c MAIL_PASSWORD` → `0`).
- The exception was caught into `::warning title=LANE-WATCH MAIL NOT DELIVERED::` on **159 failing runs**. A
  warning annotation on a run nobody opens is indistinguishable from silence.

So that step never delivered once, while looking like coverage — and it is now deleted rather than fixed.

---

## 3 · SES is dead on purpose (⚠ this is a decision, not a to-do)

`mailer._send_ses` **raises `SesDeliberatelyDisabled` instead of calling AWS.** Two independent reasons,
either sufficient: it has never had permission, and email to trimcrae is unwanted.

The refusal lives in `mailer.py` rather than in each caller, and that placement is the point. The dangerous
property of the old code was that `send_email` *silently* chose SES whenever a caller forgot `MAIL_PASSWORD`.
Refusing centrally means path **#4** above — in a file owned by another lane, which this work did not edit —
stays dead **even if somebody later grants the IAM policy**. `transport_name()` lets a caller say which
branch it is about to take instead of finding out in a swallowed traceback.

**Gmail SMTP is untouched**, because the Friday newsletter is wanted.

<details>
<summary><b>What restoring SES WOULD require — recorded so nobody re-derives it, NOT a task</b></summary>

Do not do this without trimcrae asking for it in his own words. The IAM policy alone would turn every
currently-silent caller into a live mailer, which is exactly what §3 prevents.

1. **Grant the CI user permission.** Inline policy on IAM user `nr4a3-ci-submitter` (account `646605541856`)
   allowing `ses:SendEmail`, `ses:SendRawEmail`, `ses:GetSendQuota`, `ses:GetAccountSendingEnabled`,
   `ses:ListIdentities`, `ses:VerifyEmailIdentity`.
2. **Verify the identity, per region.** The account is presumably still in the SES sandbox, where both
   `Source` and every `To` must be verified, and identities are **per region** — the workflows disagree
   (`us-east-2` for the daily email, `us-east-1` for the old lane-watch step), so pick one and make them
   agree: `aws ses verify-email-identity --email-address trimcrae@gmail.com --region us-east-1`, then click
   the link AWS mails.
3. **Then remove the refusal in `mailer._send_ses`** — it will not send while that raise is there.
4. Verify with `daily-degrader-email.yml` `mode=probe`, which prints quota + verified identities.

</details>

---

## 4 · ⚠ What can STILL email him, and what it would take to stop it

**A failed scheduled workflow run emails the repository owner.** This is GitHub's own behaviour, driven by
his account notification settings — no repo credential is involved and **no change in this repo can fully
disable it**. It is the channel that was firing every 1–2 h while `vast-watchdog.yml` was red on **38
consecutive scheduled runs** (2026-07-28 13:42 UTC → 2026-07-31 08:44 UTC).

Workflows carrying a `schedule:` today, i.e. every one that can produce that email:

| workflow | cron | notes |
|---|---|---|
| `vast-watchdog.yml` | `*/15 * * * *` | the 38-failure saturation; green since 11:07 UTC 07-31 |
| `ternary-vast-watchdog.yml` | `*/15 * * * *` | |
| `ternary-leg-watchdog.yml` | `*/15 * * * *` | |
| `fep-monitor-cron.yml` | `*/15 * * * *` | |
| `step1-fanout-autoscale.yml` | `*/20 * * * *` | also holds push path #4 |
| `gpu-ternary-fep-vast.yml` | `17 * * * *` | |
| `vast-price-sample.yml` | `17 * * * *` | |
| `credit-status.yml` | `0 12 * * *` | |
| `method-watch.yml` | `0 11 * * 5` | also sends the wanted newsletter |
| `fleet-supervision-alarm.yml` | `0 * * * *` | ✅ no longer fails deliberately |
| `lane-staleness-watch.yml` | `23 * * * *` | ✅ no longer fails deliberately |

The two alarm workflows are fixed at the source: they used to `exit 1` **because** it emails him, and they
now emit an `::error` annotation instead — equally visible on the run page and in the Actions list, and it
sends nothing. The other nine are owned by other lanes and were **not** touched; a red run there still mails
him.

**Two ways to close the remainder, both his to choose:**
- **His side, and it is the only complete fix:** GitHub → Settings → Notifications → Actions → uncheck email
  (or set to "Only notify for failed workflows I trigger"). This is the only lever that covers all nine.
- **Repo side, partial:** stop the nine failing on conditions that are merely *reported*. That is a per-lane
  judgement about which red runs are real CI failures and which are notifications wearing a CI costume, and
  it belongs to those lanes' owners.

---

## 5 · What replaced it — the pull channel

`research/modalities/alarm_state.py` writes **`research/modalities/alarm-state.json`**, committed by
`lane-staleness-watch.yml` on the supervisor's ~16 min cadence. It sends nothing, opens nothing, and cannot
fail a run (a non-zero exit would fail a scheduled run, which is itself a push channel).

The artifact carries its own expiry, the `work-ledger.json` pattern — **a reader who opens the file can tell
it is dead without running anything**, no API, no process, no clock but their own:

- `_generated_utc` / `_generated_et` — when it was last measured
- `_stale_after_utc` / `_stale_after_means` — *"IF THE CLOCK IS PAST THIS AND THIS FILE HAS NOT CHANGED,
  NOTHING IS WATCHING"*. A supervision chain that has stopped cannot report that it stopped.
- `_expected_tick_min` / `_stale_window_basis` — **the window is READ from `work-ledger.json`'s
  `_expected_tick_min`, never typed here** (CLAUDE.md §1). If it cannot be read, the basis field says
  `⚠ NOT DERIVED` rather than presenting a fallback as if it were derived.
- per condition: `verdict`, `ok`, `detail`, `bad_since_et`, `bad_for_min`, `consecutive_bad_runs` — the
  history an issue used to give for free.
- `needs_attention` vs `unmeasured` — kept apart, because "the lane is dead" and "we could not read the
  lane" have different fixes, and merging them teaches a reader to skim past both.
- a row whose **source** stopped reporting is **carried over and marked**, never dropped: a row that
  disappears reads as a row that cleared, which is this repo's most expensive defect class.

**To check on things:** open `research/modalities/alarm-state.json`. Nothing will tell you to.

---

## Rules this file exists to keep

- **Do not add a push channel.** Not an issue, not an email, not a deliberately-red run. If supervision needs
  to be visible, publish it to a committed artifact that carries its own expiry.
- **A workflow must never advertise a notification it cannot send.** Stale documentation about a safety
  channel is worse than none: it buys false comfort (CLAUDE.md §1).
- **Ask which requirement you are meeting** — "someone must be able to find out" (pull) or "someone must be
  told" (push) — *before* building. Getting that backwards is what happened here, and the resulting channel
  was well-built and still wrong.
- Pinned by `research/modalities/tests/test_no_push_notifications.py`: no `issues:` permission in any
  workflow, no mail call in the alarm workflows, no verdict-conditioned `exit 1`, and the SES branch raises.
