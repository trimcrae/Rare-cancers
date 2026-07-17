#!/usr/bin/env python3
"""Email a Markdown digest (e.g. the method-watch newsletter) as a bite-sized brief.

Reads a Markdown file, writes a short human-readable TL;DR at the top, and sends it through the shared
mailer (Gmail SMTP / SES). Reused for any digest.

The TL;DR is chosen in priority order: (1) a Claude-written summary passed via SUMMARY_OVERRIDE_FILE /
SUMMARY_OVERRIDE (a scheduled Claude session filters the digest and commits it to email-outbox — the
newsletter's real "LLM filter", same pattern as the daily status email); else (2) the Anthropic API
(ANTHROPIC_API_KEY); else (3) a deterministic fallback. An email always sends.

Usage:  DIGEST_FILE=research/method-watch-digest.md DIGEST_TITLE="Method-watch" \
        python research/modalities/email_digest.py
Env:    SUMMARY_OVERRIDE_FILE (path) | SUMMARY_OVERRIDE (inline text) — optional Claude-written TL;DR.
Modes:  MODE=send (default) | MODE=dry_run (print + write digest_email.html, send nothing).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mailer import llm_summarize, md_to_html, send_email  # noqa: E402


SYSTEM = (
    "You write a SHORT newsletter-style email brief for Tristan (trimcrae), a solo researcher, from a longer "
    "Markdown digest about the in-silico methods and NR4A3/degrader advances he is tracking. Turn it into "
    "something he can read at a glance on his phone. Rules: under ~180 words; NO tables; a one-line headline, "
    "then a few short bullets grouping only what MATTERS (new capability that changes what he can do, a "
    "watched method that shipped, a relevant NR4A3 advance). Bold the item names sparingly. If nothing "
    "materially changed, say that plainly instead of padding. Do not invent anything not in the digest. End "
    "with one line pointing to the full digest below."
)


def _summary_override():
    """A summary written elsewhere (e.g. by a scheduled Claude session that reads the digest and
    filters it down, committed to email-outbox/newsletter-summary.md). This is the newsletter's
    equivalent of the daily email's Claude-written summary — the primary "LLM filter".

    SUMMARY_OVERRIDE_FILE (a path) takes precedence over SUMMARY_OVERRIDE (inline text). Empty => None.
    """
    ov_file = (os.environ.get("SUMMARY_OVERRIDE_FILE") or "").strip()
    if ov_file and Path(ov_file).exists():
        txt = Path(ov_file).read_text().strip()
        if txt:
            return txt
    return (os.environ.get("SUMMARY_OVERRIDE") or "").strip() or None


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fallback_summary(md, title):
    """Headline + the first few section headings/bullets when no LLM key is present."""
    heads = [ln.strip() for ln in md.splitlines() if ln.lstrip().startswith("#")][1:7]
    S = [f"**{title}** — latest digest.", ""]
    if heads:
        S.append("In this issue:")
        for h in heads:
            S.append(f"- {h.lstrip('# ').strip()}")
    else:
        S.append("See the full digest below.")
    S.append("")
    S.append("Full digest below.")
    return "\n".join(S)


def main():
    path = os.environ.get("DIGEST_FILE", "research/method-watch-digest.md")
    title = os.environ.get("DIGEST_TITLE", "Method-watch newsletter")
    mode = os.environ.get("MODE", "send").strip().lower()
    try:
        md = Path(path).read_text()
    except Exception as e:  # noqa: BLE001
        print(f"digest not found ({path}): {e}; nothing to send.")
        return 0
    if not md.strip():
        print("digest empty; nothing to send.")
        return 0

    # Priority (mirrors the daily status email): a Claude-written summary (override) > Anthropic API
    # > deterministic fallback. The override is the newsletter's real "LLM filter": a scheduled Claude
    # session reads this digest, drops the keyword-collision noise, and commits the readable summary.
    summary_md = _summary_override() or llm_summarize(md, SYSTEM, max_tokens=900) or fallback_summary(md, title)

    text = f"{title}\n{'='*len(title)}\n\n{summary_md}\n\n{'-'*60}\nFULL DIGEST:\n\n{md}"
    html = (
        '<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;font-size:15px;'
        'color:#1a1a1a;max-width:640px;line-height:1.55;margin:0 auto">'
        f'<h2 style="margin:0 0 8px">{esc(title)}</h2>'
        '<div style="padding:14px 16px;background:#f7f9fc;border:1px solid #e3e8ef;border-radius:10px">'
        f'{md_to_html(summary_md)}</div>'
        '<details style="margin-top:8px"><summary style="cursor:pointer;color:#2b6cb0;font-size:13px">'
        'Full digest</summary>'
        f'<pre style="white-space:pre-wrap;font-size:12px;color:#444;background:#fafafa;border:1px solid #eee;'
        f'border-radius:8px;padding:10px;margin-top:6px">{esc(md)}</pre></details>'
        "</div>"
    )
    subject = f"{title} — {md.splitlines()[0].lstrip('# ').strip()[:70]}" if md.strip() else title

    if mode == "dry_run":
        Path("digest_email.html").write_text(html)
        print(f"Subject: {subject}\n\n{text[:1500]}\n\n[dry_run] wrote digest_email.html; nothing sent.")
        return 0
    send_email(subject, text, html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
