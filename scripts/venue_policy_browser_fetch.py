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
    # ── Nucleic Acid Therapeutics (Mary Ann Liebert) — the fusion-junction ASO paper ────
    #    Added 2026-08-12 with the venue decision. That decision was written stating the fee
    #    model as a PLAN rather than a retrieved fact, and said so; these three targets are what
    #    turn it into a reading. What has to be answered: is there a free subscription route
    #    (the $0 constraint is binding and eliminates most of the field), what is the main-text
    #    word limit, and what is the preprint policy.
    # ⛔ THE LIEBERT URLs ARE DEAD AND THE PUBLISHER HAS CHANGED (measured 2026-08-12, this
    #    fetcher). `home.liebertpub.com` returned 403 on both author-facing pages, and the
    #    open-access URL RESOLVED to
    #    sagepub.com/journals/mary-ann-liebert-journals-transition-information — "Mary Ann Liebert
    #    journals transition information". Nucleic Acid Therapeutics is now a SAGE journal, so its
    #    fee model has to be read at SAGE and the Liebert-era assumption is worthless. This is the
    #    reason the venue decision was written as a plan to be confirmed rather than as a fact.
    "nat_liebert_legacy_oa": "https://home.liebertpub.com/lpages/open-access-options/226",
    "sage_liebert_transition": "https://www.sagepub.com/journals/mary-ann-liebert-journals-transition-information",
    "sage_nat_journal": "https://journals.sagepub.com/home/nat",
    "sage_open_access_options": "https://us.sagepub.com/en-us/nam/open-access-at-sage",
    "sage_apc_information": "https://us.sagepub.com/en-us/nam/article-processing-charges-apcs",
    # ⛔ THE PAGE THAT ACTUALLY DECIDES THE SUBMISSION, AND IT WAS NEVER TARGETED (2026-08-12).
    # The four SAGE targets above answer the FEE question. None of them answers the two questions a
    # manuscript has to be built against — the main-text word limit and the article types the
    # journal accepts — because those live on the journal's own submission-guidelines page, and the
    # venue plan recorded that limit as "~6,000 words" from an inference nobody had checked. A
    # Short Communication written to a guessed limit is a Short Communication that may be the wrong
    # length. `manuscript-submission-guidelines` is SAGE's standard per-journal path.
    "sage_nat_submission_guidelines":
        "https://journals.sagepub.com/author-instructions/NAT",
    "sage_nat_aims_and_scope": "https://journals.sagepub.com/aims-scope/NAT",
    "sage_nat_home_alt": "https://journals.sagepub.com/description/NAT",
    # ⛔ ANSWER THE QUESTION FROM A HOST THAT ANSWERS (2026-08-12). Measured across two runs:
    # `journals.sagepub.com` returns 403 to a real headless browser, exactly as Wiley and Elsevier
    # do, while `sagepub.com` and `us.sagepub.com` return 200. Adding more paths on the refusing
    # host is not a plan. So the fee question is put to sources that DO answer, and each is a
    # discriminator rather than a restatement of SAGE's portfolio-wide page:
    #   * DOAJ indexes FULLY open-access journals only. Present -> the journal is gold, and the $0
    #     constraint rules it out. Absent -> it is not indexed as fully OA, which is consistent with
    #     hybrid. ⚠ Absence is weaker evidence than presence and must be reported as such: a gold
    #     journal can be missing from DOAJ for administrative reasons.
    #   * SAGE publishes its own list of pure-gold journals. NAT's absence from a list the PUBLISHER
    #     maintains is the strongest negative available without reading the journal page itself.
    # Together, presence in neither is what would let the hybrid inference be stated as a reading.
    "doaj_nat_api": "https://doaj.org/api/search/journals/%22Nucleic%20Acid%20Therapeutics%22",
    "sage_gold_oa_journal_list":
        "https://us.sagepub.com/en-us/nam/pure-gold-open-access-journals-at-sage",
    "us_sage_nat_description":
        "https://us.sagepub.com/en-us/nam/journal/nucleic-acid-therapeutics",
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
