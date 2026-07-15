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


def _send_ses(mail_from, mail_to, subject, text, html):
    import boto3

    region = _first(os.environ.get("AWS_DEFAULT_REGION"), "us-east-2")
    ses = boto3.client("ses", region_name=region)
    ses.send_email(
        Source=mail_from,
        Destination={"ToAddresses": [mail_to]},
        Message={"Subject": {"Data": subject},
                 "Body": {"Text": {"Data": text}, "Html": {"Data": html}}},
    )
    out = f"Sent via SES: {mail_from} -> {mail_to}"
    print(out)
    return out


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
