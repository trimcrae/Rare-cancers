# How an alarm reaches a human — the one home for channel status

**This file owns the answer to "if something goes wrong at 3 AM and no agent is running, who finds out?"**
Per CLAUDE.md §1, every other file points here rather than restating it. Workflows that carry a notification
step link this file from their header comment; do not re-type a channel's status into a workflow comment.

Measured **2026-07-31**. Every claim below has a run/job ID next to it.

---

## The channels, and which of them actually work

| channel | status | needs | dedupes? | evidence |
|---|---|---|---|---|
| **GitHub Issue** (`alarm_issue.py`) | ✅ **live — this is the escalation channel** | `GITHUB_TOKEN` only | ✅ one open issue per condition, auto-closed on recovery | proven end to end 2026-07-31, see "Proof" below |
| **Failed scheduled run** (GitHub's own email to the repo owner) | ⚠ live but **saturates** | nothing | ❌ none — one notification per run, forever | `vast-watchdog.yml` failed **38 consecutive** scheduled runs, 2026-07-28 13:42 UTC → 2026-07-31 08:44 UTC, before going green at 11:07 UTC |
| **Email via Gmail SMTP** (`mailer._send_smtp`) | ✅ works, but **opt-in and not standing coverage** | `MAIL_PASSWORD` secret passed into the step | ❌ none | `Sent via SMTP (smtp.gmail.com:465)` — run `30200038716`, job `89788285952`, 2026-07-26 |
| **Email via AWS SES** (`mailer._send_ses`) | ❌ **has never delivered, not once** | an IAM policy that does not exist | — | run `30602768073` job `91068780404`; probe run `30626375302` job `91142503053` |

---

## What was actually broken (root cause, not a story)

`lane-staleness-watch.yml`'s mail step passed `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
`AWS_DEFAULT_REGION` and `MAIL_TO` — **and not `MAIL_PASSWORD`**. `mailer.send_email` picks SMTP only when
`MAIL_PASSWORD` is set, so every call took the SES branch, and SES answered:

```
ClientError: An error occurred (AccessDenied) when calling the SendEmail operation: User
`arn:aws:iam::646605541856:user/nr4a3-ci-submitter' is not authorized to perform `ses:SendEmail'
on resource `arn:aws:ses:us-east-1:646605541856:identity/trimcrae@gmail.com'
```

`mode=probe` fails the same way one call earlier, on `ses:GetSendQuota` — so the IAM user has **no SES
permissions at all**.

Three things follow, all of them corrections to what the repo previously believed:

1. **It was never the SES sandbox.** The workflow comment said "SES may still be sandboxed on this account".
   A sandboxed account answers `MessageRejected: Email address is not verified` — a different error with a
   different fix. This is a **missing identity-based IAM policy**.
2. **`MAIL_PASSWORD` has never appeared in `lane-staleness-watch.yml` in any commit on any branch**
   (`git log -p --all -- .github/workflows/lane-staleness-watch.yml | grep -c MAIL_PASSWORD` → `0`). The
   transport that works was sitting one env line away the entire time.
3. **The exception was caught, so nothing was ever red about it.** It became
   `::warning title=LANE-WATCH MAIL NOT DELIVERED::`, on **159 failing runs**, and a warning annotation on a
   run nobody opens is indistinguishable from silence.

**Net effect:** for as long as that step has existed, the only escalation reaching trimcrae without an agent
in the loop was GitHub's failed-scheduled-run notification — and that channel was itself saturated for three
days by the watchdog's 38 straight failures. That is this repo's own documented cry-wolf failure, live.

---

## What replaced it

`research/modalities/alarm_issue.py`, wired into `fleet-supervision-alarm.yml` and
`lane-staleness-watch.yml`. Pure stdlib, imports nothing from the lanes it reports on, and its entire
additional permission is `issues: write`.

- **One open issue per distinct condition** (`fleet-supervision`, `lane:<key>`), matched on an HTML marker in
  the issue body. Dedupe reads the **issues list**, never the search API — GitHub's search index lags by
  seconds to minutes and a dedupe that misses opens a second issue.
- **A comment only when the verdict changes.** A body edit sends no notification; a comment does. So the
  phone buzzes on news, not on the hourly re-confirmation of news it already had.
- **Auto-closed on recovery**, with a `RECOVERED` comment and `state_reason: completed`. This is what makes an
  open issue mean something.
- **Silent on unmeasured verdicts** (`UNKNOWN`, `FRESH-API-UNREADABLE`, `TICKS-UNREADABLE`, and any verdict
  whose `runs_readable` is false): it neither opens **nor closes**. Not opening keeps the 2026-07-27 4:18 PM
  false alarm off a phone; not closing stops an unreadable API from silently retiring a live alarm.
- **Self-test built in and permanent:** `alarm_issue.py --self-test fire|fire-changed|recover`, also exposed
  as the `self_test` input on `fleet-supervision-alarm.yml`. It runs on its own key (`alarm-self-test`) so it
  can never mask or be mistaken for a real alarm. An unexercised notification path is exactly what turned out
  to be broken here — re-run it any time, $0.

Closing an alarm issue by hand does **not** silence anything: dedupe only looks at open issues, so the next
run that still sees the condition opens a fresh one.

---

## ⚠ If trimcrae wants email back — the part only he can do

Two independent things are wrong with SES and **both** must be fixed; either alone still fails.

**1 · Grant the CI user permission to send.** Attach an inline policy to IAM user
`nr4a3-ci-submitter` (account `646605541856`):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "CiAlarmMail",
    "Effect": "Allow",
    "Action": ["ses:SendEmail", "ses:SendRawEmail", "ses:GetSendQuota",
               "ses:GetAccountSendingEnabled", "ses:ListIdentities", "ses:VerifyEmailIdentity"],
    "Resource": "*"
  }]
}
```

```
aws iam put-user-policy --user-name nr4a3-ci-submitter \
  --policy-name CiAlarmMail --policy-document file://ses-send.json
```

**2 · Verify the identity in the right region, in SES itself.** The account is almost certainly still in the
SES **sandbox**, where both `Source` and every `To` must be a verified identity. The workflows disagree on
region — the daily email uses `us-east-2`, the lane watch's mail step uses `us-east-1` — and **SES identities
are per region**, so verify in whichever region the sender will use and make them agree:

```
aws ses verify-email-identity --email-address trimcrae@gmail.com --region us-east-1
```

then click the link AWS mails. (`daily-degrader-email.yml` `mode=verify` does exactly this call, and
`mode=probe` reports quota + verified identities — both currently die at step 1 above, which is how the whole
problem surfaced.)

**Verify the fix, don't assume it:** dispatch `daily-degrader-email.yml` with `mode=probe`. Success prints
the 24 h quota and the identity list. Then, and only then, is it honest to describe SES as coverage.

**Or skip SES entirely.** Gmail SMTP already works and the secret already exists; the only reason email is
default-off is the missing dedupe, not the transport. Set `email_on_fail=1` on a `lane-staleness-watch.yml`
dispatch when watching something specific.

---

## Rules this file exists to keep

- **A workflow must never advertise a notification it cannot send.** A comment or input description promising
  delivery is documentation, and stale documentation about a safety channel is worse than none — it buys
  false comfort (CLAUDE.md §1).
- **Any new escalation must be exercised before it is relied on.** The one that failed here was never fired
  on purpose even once.
- **A channel with no dedupe is not standing coverage.** It is a per-incident tool you switch on.
