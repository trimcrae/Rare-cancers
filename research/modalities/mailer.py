#!/usr/bin/env python3
"""Shared email delivery + optional LLM summarization for the repo's status/newsletter emails.

Two things live here so the daily status email and the weekly/monthly newsletter share one path:

  send_email(subject, text_body, html_body, ...)  - deliver via Gmail SMTP (if MAIL_PASSWORD is set)
                                                    else AWS SES. Empty env vars fall back to defaults.
  llm_summarize(facts, system, ...)               - turn a block of raw facts into a short, human-readable
                                                    TL;DR using the Anthropic API. Returns None if no
                                                    ANTHROPIC_API_KEY is set or the call fails, so callers
                                                    can fall back to a deterministic summary and never break.

Pure stdlib except boto3 (only imported on the SES path). All network egress happens from a CI runner.

★★ THE SES BRANCH IS DEAD ON PURPOSE — IT REFUSES INSTEAD OF SENDING (2026-07-31).

    SMTP  WORKS, and is the ONLY transport. `Sent via SMTP (smtp.gmail.com:465)`, the daily email's last
          scheduled send (GH run 30200038716, job 89788285952, 2026-07-26). It is reached whenever
          MAIL_PASSWORD is in the environment, and it still serves the WANTED weekly newsletter
          (`method-watch.yml`, Fridays). Nothing about that changed.
    SES   NEVER DELIVERED ONCE, AND IS NOW ALSO UNWANTED. The CI IAM user has no SES permission at all:
          `AccessDenied ... arn:aws:iam::646605541856:user/nr4a3-ci-submitter is not authorized to perform
          ses:SendEmail` (run 30602768073) and the same on `ses:GetSendQuota` (run 30626375302) — a MISSING
          IAM POLICY, not the SES sandbox (a sandboxed account answers `MessageRejected: Email address is
          not verified`, a different error with a different fix). Then trimcrae said, verbatim: *"You're
          emailing me way too much. You should not be emailing me."*

⚠ SO `_send_ses` RAISES `SesDeliberatelyDisabled` RATHER THAN CALLING AWS, and that placement is the point.
The dangerous property of the old code was that `send_email` SILENTLY chose SES whenever a caller forgot to
pass MAIL_PASSWORD — which is how a step could believe it had email coverage for 159 runs while sending
nothing. Refusing here rather than in each caller means:

  * a caller that reaches this branch is TOLD, loudly, instead of getting a swallowed AccessDenied; and
  * `step1-fanout-autoscale.yml`'s "Push the verdict to a human (SES)" step — which passes the AWS keys and
    NOT MAIL_PASSWORD, so it lands here — stays dead even if somebody later grants the IAM policy. That
    file belongs to another lane and is not edited from here; this is how the push path is closed anyway.

`transport_name()` lets a caller SAY which branch it is about to take instead of finding out in a traceback.
One home for the whole channel picture, and for the IAM/SES steps we are deliberately NOT taking:
`research/compute/notification-channels.md`.
"""
import json
import os
import urllib.request


# ----------------------------------------------------------------------------- delivery
def _first(*vals, default=""):
    for v in vals:
        if v:
            return v
    return default


def transport_name():
    """Which branch `send_email` would take, from the environment alone — 'smtp' or 'ses'.

    Report it BEFORE sending. The measured failure (see the module docstring) was a step that passed the AWS
    keys but not MAIL_PASSWORD, took the SES branch, and had its AccessDenied swallowed into a `::warning`
    nobody read — for 159 consecutive runs. A caller that prints this cannot make that mistake silently.
    ⚠ 'ses' now means "this call will RAISE": that branch is deliberately disabled, so it is the answer to
    "am I about to discover I have no transport", not a delivery method.
    """
    return "smtp" if os.environ.get("MAIL_PASSWORD") else "ses"


def send_email(subject, text_body, html_body, mail_to=None, mail_from=None):
    """SMTP when MAIL_PASSWORD is set, else SES. Returns a short human string describing what happened."""
    mail_to = _first(mail_to, os.environ.get("MAIL_TO"), "trimcrae@gmail.com").strip()
    mail_from = _first(mail_from, os.environ.get("MAIL_FROM"), mail_to).strip()
    if os.environ.get("MAIL_PASSWORD"):
        return _send_smtp(mail_from, mail_to, subject, text_body, html_body)
    return _send_ses(mail_from, mail_to, subject, text_body, html_body)


def _send_smtp(mail_from, mail_to, subject, text, html):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    host = _first(os.environ.get("SMTP_HOST"), "smtp.gmail.com")
    port = int(_first(os.environ.get("SMTP_PORT"), "465"))
    user = _first(os.environ.get("MAIL_USERNAME"), mail_from)
    pw = os.environ["MAIL_PASSWORD"]
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, mail_from, mail_to
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL(host, port) as s:
        s.login(user, pw)
        s.sendmail(mail_from, [mail_to], msg.as_string())
    out = f"Sent via SMTP ({host}:{port}): {mail_from} -> {mail_to}"
    print(out)
    return out


class SesDeliberatelyDisabled(RuntimeError):
    """Raised instead of sending. See the module docstring — this is a decision, not a defect."""


def _send_ses(mail_from, mail_to, subject, text, html):
    """⛔ DISABLED 2026-07-31. Raises rather than calling AWS. Do not "fix" this by restoring the call.

    Two independent reasons, either sufficient: (1) the CI IAM user has never had `ses:SendEmail`, so this
    branch has delivered exactly zero emails in its lifetime while looking like coverage; (2) trimcrae asked
    not to be emailed. Restoring it needs his word AND an IAM policy, in that order — the policy alone would
    turn every currently-silent caller into a live mailer, which is the outcome this prevents.
    """
    raise SesDeliberatelyDisabled(
        f"SES delivery is disabled in this repo (would have sent {subject!r} to {mail_to}). It never had "
        f"permission — `AccessDenied` on ses:SendEmail for nr4a3-ci-submitter — and email to trimcrae is "
        f"unwanted as of 2026-07-31. Supervision verdicts are PUBLISHED to "
        f"research/modalities/alarm-state.json instead; see research/compute/notification-channels.md. "
        f"If you meant to send the weekly newsletter, pass MAIL_PASSWORD so the SMTP branch is taken.")


# ----------------------------------------------------------------------------- LLM summary (optional)
def llm_summarize(facts, system, max_tokens=700, model=None):
    """Summarize `facts` into a short human-readable brief using the Anthropic API.

    Returns the model's text, or None if ANTHROPIC_API_KEY is unset or the call fails (caller falls back).
    """
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    model = model or os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")
    body = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": facts}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"content-type": "application/json", "x-api-key": key,
                 "anthropic-version": "2023-06-01"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
        text = "".join(parts).strip()
        return text or None
    except Exception as e:  # noqa: BLE001
        print(f"[llm_summarize] skipped: {e}")
        return None


def md_to_html(md: str) -> str:
    """Very small Markdown-ish -> HTML for the LLM summary (headings, bold, bullets, paragraphs)."""
    import html as _html
    import re

    out, in_ul = [], False
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            if in_ul:
                out.append("</ul>"); in_ul = False
            continue
        esc = _html.escape(line)
        esc = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc)
        esc = re.sub(r"(?<!\*)\*(?!\s)(.+?)\*", r"<i>\1</i>", esc)
        m = re.match(r"^\s*[-*]\s+(.*)", line)
        if m:
            if not in_ul:
                out.append('<ul style="margin:4px 0 8px;padding-left:20px">'); in_ul = True
            item = _html.escape(m.group(1))
            item = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", item)
            out.append(f"<li>{item}</li>")
            continue
        if in_ul:
            out.append("</ul>"); in_ul = False
        if line.startswith("### "):
            out.append(f'<div style="font-weight:700;margin:8px 0 2px">{_html.escape(line[4:])}</div>')
        else:
            out.append(f'<p style="margin:4px 0">{esc}</p>')
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)
