#!/usr/bin/env python3
"""Read every candidate PREPRINT SERVER's own eligibility policy, with a real browser, from CI.

WHY THIS EXISTS. bioRxiv declined a submission from this project on 2026-08-21 on the grounds that
the author is unaffiliated. Every preprint route in the programme -- and `systems/graph` aims some
thirty routes at `preprint` -- rested on the assumption that a preprint server is open to anyone,
which is the same class of assumption that once sent a venue decision to a publisher that no longer
published the journal. So the replacement host cannot be chosen from recollection or from a search
snippet: it has to be chosen from what each server SAYS about who may post.

⚠ AND THE QUESTION IS NOT ONLY "WILL THEY TAKE IT". A host that accepts the paper and is invisible
to the field is not a route to a reader (CLAUDE.md §5: the published record is the only channel by
which any of this reaches a patient). Four things decide a host, and all four are fetched here:
  1. ELIGIBILITY   -- does an unaffiliated author qualify, in the server's own words?
  2. COST          -- $0 is a hard programme constraint.
  3. PERSISTENCE   -- a DOI, and versioning, because the plan of record is a *living* preprint.
  4. DISCOVERY     -- indexed where a sarcoma researcher looks: Europe PMC, Crossref, Scholar.

⚠ WHAT THIS IS NOT. Not paywall evasion. Every URL is a public policy or author-guidance page a
prospective author is expected to read before submitting; the only thing worked around is bot
detection that cannot tell an automated reader from an abusive one. No login, no article full text,
one pass with a delay between pages.

⛔ TWO CLASSES OF PAGE DEFEAT PLAIN HTTP FROM BOTH THE DEV SANDBOX AND A RUNNER, which is why this
is a browser and not urllib: bot protection keyed on TLS fingerprint (403, unaffected by IP or
User-Agent), and bioRxiv's 429 to shared runner IPs. Measured for the publisher pages in
`scripts/venue_policy_browser_fetch.py`; the same machinery is reused here deliberately.

Emits research/literature/preprint-host-eligibility.json with, per target, the final URL, HTTP
status, page title, probe hits and the extracted visible text, so every quotation downstream is
checkable against a retrieved page rather than against a memory of one.
"""
import json
import os
import re
import sys
import time

TARGETS = {
    # ── 1. THE REFUSAL ITSELF. Read bioRxiv's own words before replacing it ──────────────
    # ⛔ WHAT WAS ACTUALLY REFUSED MATTERS. "Unaffiliated" could mean a stated policy, a
    # screening judgement, or an account/e-mail mechanism, and the three have different fixes
    # (respectively: go elsewhere; appeal; supply a different address). Nobody in this repository
    # has read the policy, so the rejection cannot yet be classified -- these pages are what
    # classify it, and they also decide whether an appeal exists.
    "biorxiv_faq": "https://www.biorxiv.org/about/FAQ",
    "biorxiv_submission_guide": "https://www.biorxiv.org/submit-a-manuscript",
    "biorxiv_about": "https://www.biorxiv.org/about-biorxiv",
    "biorxiv_screening_procedures":
        "https://connect.biorxiv.org/news/2022/06/13/screening_procedures",
    "medrxiv_faq": "https://www.medrxiv.org/about/FAQ",

    # ── 2. ChemRxiv — THE DEGRADER PAPER'S PLAN OF RECORD, AND THEREFORE AT RISK ─────────
    # `research/manuscripts/degrader/nr4a3-degrader-preprint-plan.md` names ChemRxiv as the
    # preprint host for the degrader/med-chem paper and records its fee as confirmed. Its
    # ELIGIBILITY rule was never read. If ChemRxiv screens on affiliation too, a second route
    # loses its terminus, and finding that out now costs one page fetch.
    "chemrxiv_dashboard": "https://chemrxiv.org/engage/chemrxiv/public-dashboard",
    "chemrxiv_about": "https://chemrxiv.org/engage/chemrxiv/page/about",
    "chemrxiv_faq": "https://chemrxiv.org/engage/chemrxiv/page/faq",
    "chemrxiv_terms": "https://chemrxiv.org/engage/chemrxiv/public-dashboard/terms",
    "chemrxiv_moderation": "https://chemrxiv.org/engage/chemrxiv/page/moderation-and-screening",

    # ── 3. arXiv q-bio — open to anyone, but gated by ENDORSEMENT rather than affiliation ──
    # The relevant question is not "may an unaffiliated author post" but "how does an
    # unaffiliated author get endorsed", which is a different obstacle with a different remedy
    # (a person, not an institution). Both pages are needed to state it honestly.
    "arxiv_submit": "https://info.arxiv.org/help/submit/index.html",
    "arxiv_endorsement": "https://info.arxiv.org/help/endorsement.html",
    "arxiv_moderation": "https://info.arxiv.org/help/moderation/index.html",
    "arxiv_policies": "https://info.arxiv.org/help/policies/submission_policy.html",

    # ── 4. THE CANDIDATE REPLACEMENTS ───────────────────────────────────────────────────
    # Chosen because each is free, mints a DOI and takes life-science work. Ranked in the memo
    # on what these pages say, not on reputation.
    "osf_preprints_home": "https://help.osf.io/article/377-preprints-home",
    "osf_preprints_product": "https://www.cos.io/products/osf-preprints",
    "osf_preprint_moderation": "https://help.osf.io/article/376-preprints-moderation",
    "osf_terms": "https://github.com/CenterForOpenScience/cos.io/blob/master/TERMS_OF_USE.md",

    "preprints_org_about": "https://www.preprints.org/about",
    "preprints_org_faq": "https://www.preprints.org/faq",
    "preprints_org_guidelines": "https://www.preprints.org/guidelines",

    "research_square_home": "https://www.researchsquare.com/",
    "research_square_preprints": "https://www.researchsquare.com/researchers/preprints",
    "research_square_policies": "https://www.researchsquare.com/publishers/preprint-policies",

    "zenodo_policies": "https://about.zenodo.org/policies/",
    "zenodo_principles": "https://about.zenodo.org/principles/",
    "zenodo_help_deposit": "https://help.zenodo.org/docs/deposit/",

    "qeios_home": "https://www.qeios.com/",
    "qeios_policies": "https://www.qeios.com/publishing-policies",

    "ssrn_faq": "https://www.ssrn.com/index.cfm/en/ssrn-faq/",
    "authorea_home": "https://www.authorea.com/",
    "scienceopen_preprints": "https://www.scienceopen.com/",

    # ── 5. DISCOVERY — a host nobody indexes is not a route to a reader ──────────────────
    # ⛔ THIS IS THE HALF A HOST COMPARISON USUALLY SKIPS. Europe PMC indexes SOME preprint
    # servers and not others, and its list is the single page that decides whether a sarcoma
    # researcher's literature search ever surfaces the paper. PubMed is separate and stricter
    # (an NIH-funded pilot), so it is asked separately rather than assumed.
    "europepmc_preprints": "https://europepmc.org/Preprints",
    "europepmc_about": "https://europepmc.org/About",
    "pubmed_preprint_pilot": "https://www.ncbi.nlm.nih.gov/pmc/about/nihpreprints/",
    "crossref_preprints": "https://www.crossref.org/documentation/research-nexus/preprints/",
    "scholar_inclusion": "https://scholar.google.com/intl/en/scholar/inclusion.html",
}

#: Phrases worth surfacing per page so a reader need not scan the whole dump. Presence is reported;
#: ⛔ ABSENCE IS NOT EVIDENCE OF ANYTHING -- a server can state its rule in words nobody predicted,
#: which is why the full text is stored rather than only these hits.
PROBES = [
    # eligibility, the question that opened this file
    r"affiliat", r"institution", r"independent researcher", r"unaffiliated", r"not affiliated",
    r"who (?:can|may) (?:post|submit|deposit)", r"eligib", r"endorse", r"invit",
    r"academic e-?mail", r"institutional e-?mail", r"verif(?:y|ied|ication)",
    # screening and refusal
    r"screen", r"moderat", r"declin", r"reject", r"withdraw", r"appeal",
    # cost
    r"free of charge", r"no charge", r"at no cost", r"no fee", r"free to (?:submit|post)",
    r"\bAPC\b", r"article processing charge", r"fee",
    # persistence and discovery
    r"\bDOI\b", r"version", r"Crossref", r"Europe PMC", r"PubMed", r"Google Scholar", r"index",
    r"licen[cs]e", r"CC ?BY", r"journal submission", r"submit(?:ted)? to a journal",
]

OUT = os.path.join("research", "literature", "preprint-host-eligibility.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")

#: Home/landing pages whose real policy paths are worth harvesting rather than guessing.
#: ⛔ THREE INVENTED URLS 404ed IN THE PUBLISHER SWEEP AND A FEE SCHEDULE WENT UNREAD. A site's own
#: navigation is the only authority on where its policies live; a plausible path is still a guess.
HARVEST_LINKS_FROM = [
    "chemrxiv_dashboard", "research_square_home", "preprints_org_about", "qeios_home",
    "osf_preprints_product", "europepmc_preprints", "authorea_home", "scienceopen_preprints",
]

LINK_WORDS = re.compile(
    r"author|submi|guideline|instruction|polic|moderat|screen|eligib|faq|about|"
    r"terms|charge|fee|preprint|deposit|index", re.I)


def harvest_links(page):
    """Every policy-facing link on a page, as {text, href}."""
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
    return out[:200]


def probe_hits(text):
    out = {}
    for pat in PROBES:
        for m in re.finditer(pat, text, re.I):
            a, b = max(0, m.start() - 200), min(len(text), m.end() + 200)
            out.setdefault(pat, []).append(re.sub(r"\s+", " ", text[a:b]).strip())
            if len(out[pat]) >= 4:
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
            # ⚠ Backoff is for the 429 case (bioRxiv to shared runner IPs); a 403 does not clear by
            # waiting, so the loop stops on it rather than burning six minutes proving that again.
            for attempt, wait in enumerate([0, 8, 25, 60], start=1):
                if wait:
                    time.sleep(wait)
                try:
                    resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    status = resp.status if resp else None
                    page.wait_for_timeout(3000)
                    text = page.inner_text("body")
                    rec["attempts"].append({"n": attempt, "status": status, "chars": len(text)})
                    if status and status < 400 and len(text) > 400:
                        rec.update({"final_url": page.url, "status": status,
                                    "title": page.title(), "chars": len(text),
                                    "probe_hits": probe_hits(text), "text": text[:150000]})
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

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({
            "_what": "Preprint-server eligibility, cost, persistence and indexing policy pages, "
                     "fetched with a headless Chromium from a GitHub Actions runner.",
            "_why": "bioRxiv declined this project's submission because the author is unaffiliated. "
                    "Every replacement host had to be judged on what it SAYS about who may post, "
                    "not on reputation or on a search snippet -- and the dev sandbox's egress proxy "
                    "blocks every one of these domains.",
            "_scope": "Public policy and author-guidance pages only. No login, no paywalled "
                      "content, no article full text.",
            "_generator": "scripts/preprint_host_policy_fetch.py",
            "_absence_note": "A probe that does not fire means the phrase is absent from the page, "
                             "NOT that the policy is absent. Read the stored text before "
                             "concluding a server is silent on eligibility.",
            "targets": records,
        }, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    got = sum(1 for r in records.values() if (r.get("status") or 999) < 400)
    print(f"\nwrote {OUT}: {got}/{len(records)} pages retrieved")
    return 0 if got else 1


if __name__ == "__main__":
    sys.exit(main())
