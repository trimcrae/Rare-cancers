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
    # ⭐ THE PAGE-CHARGE QUESTION IS NOT THE APC QUESTION, AND IT IS ASKED HERE (2026-08-20).
    # NAT was eliminated on a mandatory $90/page Publishing Services Fee. Condensing the paper to a
    # short journal article changes what that fee COSTS, so the live question is no longer "does
    # SAGE charge per page" but "how many pages are charged" — specifically whether a free page
    # allowance precedes the per-page rate, and what colour figures cost. Neither is answerable
    # from the APC pages already targeted above: those speak to open access only and are silent on
    # page and colour charges, which is the same error that sent the first venue decision to a
    # publisher which no longer publishes the journal. This path is on the `us.sagepub.com` host
    # rather than the `journals.sagepub.com` one that returns 403 to a real headless browser.
    "sage_page_and_publication_charges":
        "https://us.sagepub.com/en-us/nam/page-and-publication-charges",
    # ⭐ A FALLBACK VENUE IS ONLY A FALLBACK IF ITS POLICY CAN BE READ (2026-08-12). Every previous
    # candidate for this paper sits behind a publisher that refuses this fetcher — Wiley 403,
    # Elsevier 403, journals.sagepub.com 403 — so "we will go to X instead" would be an assumption
    # of exactly the kind that sent the first venue decision at a publisher which no longer
    # publishes the journal. nature.com answered 200 on the first run, so the Springer Nature
    # portfolio is the one whose fee model this repository can actually confirm. Cancer Gene
    # Therapy is the closest Springer Nature title in scope: fusion-directed and nucleic-acid
    # therapeutics, hybrid subscription model.
    "cgt_journal_home": "https://www.nature.com/cgt/",
    "cgt_author_instructions": "https://www.nature.com/cgt/for-authors",
    "cgt_open_access": "https://www.nature.com/cgt/open-access",
    # ⛔⛔ ASK EVERY VENUE ABOUT PAGE CHARGES, NOT ONLY ABOUT APCs (2026-08-12, and this reversed a
    # venue decision). The whole comparison above — mine and the plan's — asked one question: "is
    # there a subscription route without an article processing charge?" Nucleic Acid Therapeutics
    # PASSES that test (`Access: Subscription`) and still bills the author: its guidelines state
    # "All manuscripts ... will be assessed the following MANDATORY Publishing Services Fees: Page
    # Charges (assessed upon acceptance): $90/page", which for this manuscript is roughly $700-1,100.
    # ⛔ "HYBRID" NEVER MEANT "FREE". It means OA is the paid upgrade; it says nothing about page,
    # colour, submission or over-length charges levied on the subscription route as well. A $0
    # constraint has to be tested against the FULL fee schedule, and until today it was not.
    # These targets are the fee schedule for the venue currently chosen, so the same question gets
    # asked of it before anything is submitted.
    # ⛔ ALL THREE OF THE ORIGINAL AUTHOR-FACING CGT PATHS RETURNED 404 ON EVERY ATTEMPT, SO THE
    # FEE SCHEDULE FOR THE CHOSEN VENUE HAS NEVER BEEN READ (measured 2026-08-12). That is the
    # open half of the paragraph above: the open-access page answered 200 and established that OA
    # is the paid upgrade, which settles the APC question and says nothing whatever about page,
    # colour or over-length charges. Nucleic Acid Therapeutics passed the APC test and was then
    # disqualified by $90/page, so an unread fee schedule is not a formality here — it is the same
    # trap one venue later.
    # ⚠ GUESSING THE NEXT PATH IS WHAT PRODUCED THE 404s. `/cgt/for-authors`,
    # `/cgt/submission-guidelines` and `/cgt/about` were all plausible and all wrong;
    # `/cgt/about` merely redirected to `/cgt/journal-information`. The journal home answers 200,
    # so the reliable move is to READ ITS LINKS rather than to invent more paths — see
    # `harvest_links()`, which records every author-facing href the home page actually carries.
    # The two below are kept because they are patterns confirmed to work elsewhere in this file:
    # `authors-and-referees/gta` is the exact shape that answered 200 for BJC.
    "cgt_gta": "https://www.nature.com/cgt/authors-and-referees/gta",
    "cgt_article_types": "https://www.nature.com/cgt/article-types",
    "cgt_about": "https://www.nature.com/cgt/about",
    # ── WAIVERS AND DISCOUNTS FOR AN UNAFFILIATED, UNFUNDED AUTHOR ──────────────────────
    # ⛔ ASKED 2026-08-13 BY trimcrae AND ANSWERABLE ONLY BY READING, NOT BY RECALL: "Nobody
    # waives fees for non-institutional authors?" Every fee page this repository has read so far
    # offers exactly two routes off a charge — an institutional prepaid account, and country-based
    # eligibility — and this author has neither an institution nor a qualifying country. That is a
    # reading of the JOURNAL pages, though, and waiver policy at both these publishers lives at the
    # PUBLISHER level, one link up from where anyone has looked. So these are the pages that decide
    # it, and until they answer, "there is no waiver" is an assumption and not a finding.
    # ⚠ The question is worth its own targets rather than a note, because a waiver would reopen
    # both venues eliminated on fees so far — Cancer Gene Therapy at $238/page and Nucleic Acid
    # Therapeutics at $90/page — and neither was rejected on scientific fit.
    "sn_apc_waivers": "https://www.springernature.com/gp/open-research/policies/journal-policies",
    "sn_oa_funding_support": "https://www.springernature.com/gp/open-research/funding/policy-compliance-faqs",
    "sn_waiver_country_list": "https://www.springernature.com/gp/open-research/policies/journal-policies/apc-waivers-discounts",
    "sage_author_discounts": "https://us.sagepub.com/en-us/nam/author-gateway-open-access-fees",
    # ⚠ TWO NAT PATHS NEVER TRIED, AND THE REASON THEY ARE WORTH ONE MORE ATTEMPT (2026-08-13).
    # Seven `journals.sagepub.com` paths returned 403 to a real browser, which is why this venue was
    # abandoned as unreadable. But every one of those seven was guessed, and the CGT lesson was that
    # guessed paths 404 while the journal's own link works: a web search surfaced
    # `/author-instructions/nat`, which is a DIFFERENT path shape from any tried, and
    # `uk.sagepub.com` is a HOST never attempted at all — notable because plain `sagepub.com`
    # answered 200 while `journals.sagepub.com` did not, so the block is host-specific rather than
    # publisher-wide. Search reports $90/page persisting under SAGE plus $800 for the first colour
    # figure in print, and a search snippet is not a retrieved fact; these targets are what would
    # make it one.
    "sage_nat_author_instructions": "https://journals.sagepub.com/author-instructions/nat",
    "sage_nat_uk_journal_page": "https://uk.sagepub.com/en-gb/eur/nucleic-acid-therapeutics/journal204141",

    # ── THE ONLY PUBLISHER FAMILY NOT YET PRICED, AND THE PATTERN THAT MAKES IT WORTH ASKING ──
    # ⛔ EVERY SPECIALIST VENUE PRICED SO FAR CHARGES BY THE PAGE ON THE SUBSCRIPTION ROUTE, and
    # they are the venues that fit this paper best: Cancer Gene Therapy $238/page (read at primary
    # source), Nucleic Acid Therapeutics $90/page, Molecular Therapy $116/page for a non-ASGCT
    # member up to eight pages and $180 thereafter (both search-derived, being confirmed). The
    # common cause is structural rather than editorial — these are society-run journals funded from
    # subscription revenue, so the author is billed for typeset pages. A general journal without a
    # society behind it need not work that way, and the British Journal of Cancer does not: no page
    # charge at all, colour optional. Oxford University Press is the remaining family nobody has
    # priced, and it is worth one fetch because OUP hybrid titles commonly levy no page charge on
    # the subscription route.
    # ⚠ FIT IS THE REASON THESE TWO AND NOT ANY OUP TITLE. `Briefings in Bioinformatics` was named
    # as a fallback in the submission plan and set aside because "the emphasis is wrong: this is a
    # therapeutic-design paper, not a method paper". That judgement predates this session's finding
    # that an off-target screen ignoring alignment orientation overstates gap-spanning risk by 47%
    # AND reorders the candidates, which is a methods result generalising past this manuscript.
    "oup_bib_instructions": "https://academic.oup.com/bib/pages/General_Instructions",
    "oup_hmg_instructions": "https://academic.oup.com/hmg/pages/General_Instructions",
    "oup_author_charges": "https://academic.oup.com/pages/authoring/journals/preparing_your_manuscript",
    "research4life_eligibility": "https://www.research4life.org/access/eligibility/",

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
    r"colou?r charge", r"page charge", r"per page", r"publishing services fee",
    r"mandatory", r"assessed upon acceptance", r"over-?length", r"excess page", r"word limit", r"maximum of [\d,]+ words",
    r"[\d,]+ words", r"abstract .{0,30}\b\d{3}\b .{0,10}words", r"subscription",
    r"open access option", r"hybrid",
]

OUT = os.path.join("research", "literature", "venue-policy-browser-fetch.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")


# ---------------------------------------------------------------------------
# Caller-supplied targets — the same instrument pointed at a different corpus
# ---------------------------------------------------------------------------
# ⭐ WHY THIS SEAM EXISTS (2026-08-23). The venue corpus above is one QUESTION answered with this
# METHOD. The method -- a real browser against hosts whose bot protection is keyed on TLS
# fingerprint rather than on IP -- is the only route this repository has to several classes of
# publicly readable page, and rebuilding it per question would be the tail wagging the dog. The
# ESMO clinical practice guidelines are the case that forced it: they are free to read on
# annalsofoncology.org and return HTTP 403 to plain urllib from both the sandbox and a CI runner.
#
# ⛔ AND THE SCOPE RULE IS UNCHANGED BY THE SEAM, WHICH IS THE POINT OF STATING IT HERE. This
# fetcher takes PUBLICLY READABLE pages only. It is not a paywall route and must never be pointed
# at one: a subscription article that a browser cannot read without a login is UNREACHABLE, and
# "unreachable" is the honest finding to record. Measured the day this seam was added: PMID
# 32856598 (Cancer Epidemiol Biomarkers Prev) is not in PMC, is not open access, and its publisher
# PDF URL serves a JavaScript shim. That paper was recorded as unreachable rather than pursued
# here, and this comment is the record of that decision.
def _targets_from_env():
    """(targets, out_path, override_note) — TARGETS/OUT unless the caller replaced them."""
    raw = os.environ.get("BROWSER_TARGETS_JSON", "").strip()
    if not raw:
        return TARGETS, OUT, None
    try:
        supplied = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"BROWSER_TARGETS_JSON is not valid JSON: {exc}") from exc
    if not isinstance(supplied, dict) or not supplied:
        raise SystemExit("BROWSER_TARGETS_JSON: expected a non-empty JSON object of name -> url")
    for name, url in supplied.items():
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise SystemExit(f"BROWSER_TARGETS_JSON: {name!r} is not an http(s) URL")
    out = os.environ.get("BROWSER_OUT", "").strip() or os.path.join(
        "research", "literature", "browser-fetch.json")
    return supplied, out, (
        f"TARGETS were REPLACED by the caller via BROWSER_TARGETS_JSON ({len(supplied)} URLs); "
        "the built-in venue corpus did not run. Public pages only -- this is not a paywall route."
    )


#: Home pages whose author-facing links are worth harvesting, because guessing their paths failed.
HARVEST_LINKS_FROM = ["cgt_journal_home"]

#: A link is author-facing if its text or href says so. Deliberately broad: the cost of recording
#: an irrelevant link is one line of JSON, and the cost of missing the fee schedule is a venue
#: chosen on an unread policy — which this file already did once.
LINK_WORDS = re.compile(
    r"author|submi|guideline|instruction|for-authors|article.?type|charge|fee|"
    r"policies|publish|editorial", re.I)


def harvest_links(page):
    """Every author-facing link on a page, as (text, absolute href).

    ⛔ THIS EXISTS BECAUSE THREE INVENTED URLS 404ed AND THE FEE SCHEDULE WENT UNREAD. A journal's
    own navigation is the one authority on where its guidelines live; a plausible path is a guess
    no matter how conventional it looks.
    """
    try:
        raw = page.eval_on_selector_all(
            "a[href]", "els => els.map(e => [e.innerText.trim(), e.href])")
    except Exception:  # noqa: BLE001 — a page that will not enumerate links is not a failure
        return []
    seen, out = set(), []
    for text, href in raw:
        if not href or href in seen:
            continue
        if LINK_WORDS.search(text or "") or LINK_WORDS.search(href):
            seen.add(href)
            out.append({"text": re.sub(r"\s+", " ", text or "")[:80], "href": href})
    return out


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

    targets, out_path, override_note = _targets_from_env()
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

        for name, url in targets.items():
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
                        if name in HARVEST_LINKS_FROM:
                            rec["author_facing_links"] = harvest_links(page)
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

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    payload = {
            "_what": "Publisher policy and author-guidance pages fetched with a headless Chromium "
                     "from a GitHub Actions runner, 2026-08-10.",
            "_why": "These pages return 403 (publisher bot protection) or 429 (shared runner IPs) to "
                    "plain HTTP from both the dev sandbox and CI. The $0 route and the format limits "
                    "had to rest on the pages themselves rather than on search summaries of them.",
            "_scope": "Public policy and author-guidance pages only. No login, no paywalled content, "
                      "no article full text.",
            "_generator": "scripts/venue_policy_browser_fetch.py",
            "targets": records,
    }
    if override_note:
        payload["_targets_overridden"] = override_note
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    got = sum(1 for r in records.values() if (r.get("status") or 999) < 400)
    print(f"\nwrote {out_path}: {got}/{len(records)} pages retrieved")
    return 0 if got else 1


if __name__ == "__main__":
    sys.exit(main())
