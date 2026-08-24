#!/usr/bin/env python3
"""Email a Markdown digest (e.g. the method-watch newsletter) as a bite-sized brief.

Reads a Markdown file, writes a short human-readable TL;DR at the top, and sends it through the shared
mailer (Gmail SMTP / SES). Reused for any digest.

The TL;DR is chosen in priority order: (1) a Claude-written summary passed via SUMMARY_OVERRIDE_FILE /
SUMMARY_OVERRIDE (a scheduled Claude session filters the digest and commits it to email-outbox — the
newsletter's real "LLM filter", same pattern as the daily status email); else (2) the Anthropic API
(ANTHROPIC_API_KEY); else (3) a deterministic fallback. An email always sends.

The email is a real newsletter: a masthead, the filtered summary as the body, and a small footer. The
raw firehose digest is NOT inlined by default (it stays published on the method-watch-cache branch);
set NEWSLETTER_FULL_DIGEST=1 to append it, rendered as clean HTML rather than a monospace dump.

Usage:  DIGEST_FILE=research/method-watch-digest.md DIGEST_TITLE="Method-watch" \
        python research/modalities/email_digest.py
Env:    SUMMARY_OVERRIDE_FILE (path) | SUMMARY_OVERRIDE (inline text) — optional Claude-written TL;DR.
        NEWSLETTER_FULL_DIGEST=1 — append the full digest (off by default for a condensed read).
Modes:  MODE=send (default) | MODE=dry_run (print + write digest_email.html, send nothing).
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mailer import llm_summarize, md_to_html, send_email  # noqa: E402


# ⚠ SCOPE. This prompt, the scheduled Claude session's prompt (research/modalities/
# daily-email-system.md) and scripts/method-watch.mjs's watch list must agree about what counts as
# news, because they are three filters in series and the NARROWEST one decides what Tristan reads.
# On 2026-08-19 the Merck/Moderna Phase 3 INTerpath-001 readout — the first positive Phase 3 for an
# individualized neoantigen therapy — did not reach the 2026-08-21 newsletter. The generator had no
# source that could carry it, AND this prompt asked only for methods/tools/NR4A3, so it would have
# been dropped even if a source had. Both halves are fixed; keep them in step.
SYSTEM = (
    "You write a SHORT newsletter-style email brief for Tristan (trimcrae), a solo researcher, from a longer "
    "Markdown digest. He runs an entirely in-silico program against extraskeletal myxoid chondrosarcoma "
    "(EMC / EWSR1::NR4A3), across a PORTFOLIO of routes — a selective degrader, a fusion-junction ASO, and a "
    "fusion-junction NEOANTIGEN VACCINE among them. Turn the digest into something he can read at a glance "
    "on his phone. Rules: under ~220 words; NO tables; a one-line headline, then short bullets, most "
    "consequential first.\n"
    "LEAD WITH CLINICAL / TREATMENT NEWS when there is any. A pivotal trial readout, an approval, or a "
    "program halt is the highest-consequence thing this digest carries — ESPECIALLY in a modality one of his "
    "routes uses (individualized neoantigen therapy or cancer vaccines; antisense/siRNA in solid tumours; "
    "targeted protein degraders) or anything touching sarcoma. A first-in-class or practice-changing cancer "
    "result belongs in this brief EVEN IF it is in another tumour type and touches none of his routes — say "
    "in one clause what it would mean for the route it bears on, or that it bears on none. Never drop a "
    "large treatment result for being off-topic.\n"
    "Then the rest: a new capability that changes what he can do, a watched method or tool that shipped, a "
    "relevant NR4A3/EMC advance, and a newly-opened funding opportunity he could apply to — especially "
    "AI/compute grants open to individuals/unrestricted, which fund his GPU time.\n"
    "Bold item names sparingly. A news-feed item is a LEAD, NOT EVIDENCE: write it as reported, name the "
    "source, and never restate a press claim as an established medical fact. If nothing materially changed, "
    "say that plainly instead of padding. Do not invent anything not in the digest. End with one line "
    "pointing to the full digest below."
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
    """Graceful placeholder when neither a Claude-written summary nor the API is available.

    We deliberately do NOT dump section headings here (that read as noise). Just say the filtered
    brief is unavailable and point to the full digest, so a bad week degrades to one honest line.
    """
    return (
        "**This week's filtered brief wasn't generated.** No summary was written for this issue, so "
        "there's nothing condensed to show. See the full digest (link below) for the raw watch, or "
        "re-run the summary writer."
    )


def digest_date(md):
    """The date/label from the digest's first heading, e.g. 'Method-watch digest — 2026-07-17'."""
    first = next((ln for ln in md.splitlines() if ln.strip()), "")
    return first.lstrip("# ").strip()


def subject_line(summary_md, date_line):
    """Lead the subject with the summary's headline so the newsletter is scannable in the inbox."""
    first = next((ln for ln in summary_md.splitlines() if ln.strip()), "")
    first = re.sub(r"[*_`#>-]", "", first).strip()
    tail = first or date_line
    return f"Method-watch · {tail[:72]}"


FOOTER = (
    "Auto-filtered brief — triage, not decisions. The full digest with every source lives on the "
    "<code>method-watch-cache</code> branch (<code>research/method-watch-digest.md</code>)."
)


def build_html(summary_md, date_line, md, include_full):
    """A clean, mobile-first newsletter: masthead, filtered summary body, small footer."""
    summary_html = md_to_html(summary_md)
    P = []
    P.append('<div style="background:#eef2f7;padding:20px 12px;margin:0">')
    P.append('<div style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,'
             'sans-serif;max-width:600px;margin:0 auto;background:#ffffff;border-radius:14px;'
             'overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.08)">')
    # masthead
    P.append('<div style="padding:22px 24px 14px">'
             '<div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#2b6cb0;'
             'font-weight:700">Method-Watch Newsletter</div>'
             f'<div style="font-size:20px;font-weight:700;color:#1a202c;margin-top:4px">{esc(date_line)}</div>'
             '<div style="font-size:13px;color:#718096;margin-top:4px">Cancer treatment news, and the '
             'in-silico capabilities and NR4A3 advances worth knowing about this week.</div></div>')
    P.append('<div style="height:1px;background:#e2e8f0;margin:0 24px"></div>')
    # body (the filtered summary IS the newsletter)
    P.append(f'<div style="padding:16px 24px 8px;font-size:15px;line-height:1.6;color:#2d3748">'
             f'{summary_html}</div>')
    # optional full digest, rendered as clean HTML (never a monospace dump)
    if include_full:
        P.append('<div style="padding:0 24px 8px"><details><summary style="cursor:pointer;color:#2b6cb0;'
                 'font-size:13px;font-weight:600">Full digest — every source</summary>'
                 f'<div style="font-size:13px;line-height:1.5;color:#4a5568;margin-top:8px">'
                 f'{md_to_html(md)}</div></details></div>')
    # footer
    P.append('<div style="padding:14px 24px 22px;border-top:1px solid #edf2f7;margin-top:8px">'
             f'<div style="font-size:12px;color:#a0aec0;line-height:1.5">{FOOTER}</div></div>')
    P.append("</div></div>")
    return "\n".join(P)


def build_text(summary_md, date_line, md, include_full):
    L = ["METHOD-WATCH NEWSLETTER", date_line, "=" * 40, "", summary_md, ""]
    if include_full:
        L += ["-" * 40, "FULL DIGEST (every source):", "", md]
    else:
        L += ["-" * 40,
              "Full digest with every source: method-watch-cache branch "
              "(research/method-watch-digest.md)."]
    return "\n".join(L)


def main():
    path = os.environ.get("DIGEST_FILE", "research/method-watch-digest.md")
    title = os.environ.get("DIGEST_TITLE", "Method-watch newsletter")
    mode = os.environ.get("MODE", "send").strip().lower()
    include_full = (os.environ.get("NEWSLETTER_FULL_DIGEST") or "").strip().lower() in ("1", "true", "yes", "on")
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

    date_line = digest_date(md)
    subject = subject_line(summary_md, date_line)
    text = build_text(summary_md, date_line, md, include_full)
    html = build_html(summary_md, date_line, md, include_full)

    if mode == "dry_run":
        Path("digest_email.html").write_text(html)
        print(f"Subject: {subject}\n\n{text[:1500]}\n\n[dry_run] wrote digest_email.html; nothing sent.")
        return 0
    send_email(subject, text, html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
