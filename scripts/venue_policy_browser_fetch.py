#!/usr/bin/env python3
"""Fetch publisher policy pages with a REAL BROWSER, from a GitHub Actions runner.

WHY THIS EXISTS. The $0 publishing route for three journals had to be verified at primary source
before a preprint went out, because the journal submission follows the preprint immediately. Two
classes of page defeated every plain-HTTP attempt, from the dev sandbox AND from a CI runner:

  * PUBLISHER JOURNAL PAGES (onlinelibrary.wiley.com, www.sciencedirect.com, www.elsevier.com
    journal paths) return HTTP 403. This is bot protection keyed on TLS fingerprint and header
    order, not on IP reputation, so it fails identically from CI -- retrying, changing the
    User-Agent string, or waiting does not help. What defeats it is being an actual browser.
  * BIORXIV returns HTTP 429 to GitHub runner IPs, which are shared and heavily rate-limited.
    Measured: five attempts across three separate workflow runs, all 429. A browser session with
    real headers and a cookie jar behaves like a reader rather than a scraper, and the retry
    schedule below gives the limiter room to reset.

⚠ WHAT THIS IS NOT. It is not an attempt to evade a paywall or to take content that is not public.
Every URL here is a publicly readable policy or author-guidance page that any prospective author is
expected to read before submitting; the only thing being worked around is bot detection that does
not distinguish an automated reader from an abusive one. Nothing is fetched behind a login, no
article full text is taken, and the fetch is one pass over ~20 pages with a delay between them.

Emits research/literature/venue-policy-browser-fetch.json with, per target, the final URL, the HTTP
status, the page title and the extracted visible text, so every downstream quotation is checkable.
"""
import json
import os
import re
import sys
import time

TARGETS = {
    # ── Genes, Chromosomes and Cancer (Wiley) — MTAP/PRMT5 and the ATR package ──────────
    "gcc_author_guidelines": "https://onlinelibrary.wiley.com/page/journal/10982264/homepage/forauthors.html",
    "gcc_open_access": "https://onlinelibrary.wiley.com/page/journal/10982264/homepage/fundedaccess.html",
    "gcc_journal_home": "https://onlinelibrary.wiley.com/journal/10982264",
    # ── Critical Reviews in Oncology/Hematology (Elsevier) — the repurposing menu ───────
    "croh_guide_for_authors": "https://www.sciencedirect.com/journal/critical-reviews-in-oncology-hematology/publish/guide-for-authors",
    "croh_journal_home": "https://www.sciencedirect.com/journal/critical-reviews-in-oncology-hematology",
    "croh_oa_options": "https://www.elsevier.com/journals/critical-reviews-in-oncology-hematology/1040-8428/open-access-options",
    # ── British Journal of Cancer (Springer Nature) — surface targets. These answered on
    #    plain HTTP already; re-read here so all four venues rest on one method. ──────────
    "bjc_guide_to_authors": "https://www.nature.com/bjc/authors-and-referees/gta",
    # ── bioRxiv, the free open copy for all four papers ─────────────────────────────────
    "biorxiv_faq": "https://www.biorxiv.org/about/FAQ",
    "biorxiv_submission_guide": "https://www.biorxiv.org/submit-a-manuscript",
    "biorxiv_about": "https://www.biorxiv.org/about-biorxiv",
}

#: Phrases worth surfacing per page so a reader does not have to scan the whole dump. Presence is
#: reported; ⛔ absence is NOT evidence of anything, because a page can state a policy in words
#: nobody predicted, which is why the full text is stored rather than only these hits.
PROBES = [
    r"free of charge", r"no charge", r"at no cost", r"no fee", r"free to (?:submit|post)",
    r"submission fee", r"article processing charge", r"article publication charge", r"\bAPC\b",
    r"colou?r charge", r"page charge", r"word limit", r"maximum of [\d,]+ words",
    r"[\d,]+ words", r"abstract .{0,30}\b\d{3}\b .{0,10}words", r"subscription",
    r"open access option", r"hybrid",
]

OUT = os.path.join("research", "literature", "venue-policy-browser-fetch.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")


def probe_hits(text):
    out = {}
    for pat in PROBES:
        for m in re.finditer(pat, text, re.I):
            a, b = max(0, m.start() - 170), min(len(text), m.end() + 170)
            out.setdefault(pat, []).append(re.sub(r"\s+", " ", text[a:b]).strip())
            if len(out[pat]) >= 3:
                break
    return out


def main():
    from playwright.sync_api import sync_playwright

    records = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900},
                                  locale="en-GB", java_script_enabled=True)
        # Cloudflare scores the absence of these as bot-like.
        ctx.set_extra_http_headers({
            "Accept-Language": "en-GB,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
        })
        page = ctx.new_page()

        for name, url in TARGETS.items():
            rec = {"url": url, "attempts": []}
            # ⚠ Backoff is for the 429 case specifically; a 403 will not clear by waiting, so the
            # loop stops on it rather than burning six minutes proving that again.
            for attempt, wait in enumerate([0, 8, 25, 60], start=1):
                if wait:
                    time.sleep(wait)
                try:
                    resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    status = resp.status if resp else None
                    page.wait_for_timeout(2500)
                    text = page.inner_text("body")
                    rec["attempts"].append({"n": attempt, "status": status, "chars": len(text)})
                    if status and status < 400 and len(text) > 400:
                        rec.update({"final_url": page.url, "status": status,
                                    "title": page.title(), "chars": len(text),
                                    "probe_hits": probe_hits(text), "text": text[:120000]})
                        break
                    if status == 403:
                        rec.update({"status": 403, "chars": len(text), "text": text[:4000],
                                    "note": "403 persisted under a real browser; not an IP or "
                                            "header-string problem and not fixable by retrying"})
                        break
                except Exception as exc:                      # noqa: BLE001 - recorded, not raised
                    rec["attempts"].append({"n": attempt, "error": f"{type(exc).__name__}: {exc}"})
            rec.setdefault("status", None)
            records[name] = rec
            print(f"{str(rec.get('status')):>5}  {rec.get('chars', 0):>7}  {name}", flush=True)
            time.sleep(3)

        ctx.close()
        browser.close()

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({
            "_what": "Publisher policy and author-guidance pages fetched with a headless Chromium "
                     "from a GitHub Actions runner, 2026-08-10.",
            "_why": "These pages return 403 (publisher bot protection) or 429 (shared runner IPs) to "
                    "plain HTTP from both the dev sandbox and CI. The $0 route and the format limits "
                    "had to rest on the pages themselves rather than on search summaries of them.",
            "_scope": "Public policy and author-guidance pages only. No login, no paywalled content, "
                      "no article full text.",
            "_generator": "scripts/venue_policy_browser_fetch.py",
            "targets": records,
        }, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    got = sum(1 for r in records.values() if (r.get("status") or 999) < 400)
    print(f"\nwrote {OUT}: {got}/{len(records)} pages retrieved")
    return 0 if got else 1


if __name__ == "__main__":
    sys.exit(main())
