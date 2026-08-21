#!/usr/bin/env python3
"""Can the EMC fusion-junction ASO paper go to arXiv q-bio, and what would it take?

WHY THIS EXISTS. bioRxiv declined this project's submission because the author is unaffiliated
(`research/literature/preprint-host-eligibility.json`, target `biorxiv_submission_guide`).
trimcrae, 2026-08-21: *"This is for the EMC ASO paper. I'd like you to revisit arXiv again since it
seems dedicated to exactly the research I'm doing here."* That reading is defensible on the merits
rather than only on eligibility -- the paper is a computed, no-wet-lab result, which is q-bio's
remit and is precisely what bioRxiv's experimental-biology audience is NOT selected for.

⛔ SO THE QUESTION IS NOT "DOES ARXIV ALLOW UNAFFILIATED AUTHORS". It does; its gate is
ENDORSEMENT, which is a different obstacle with a different remedy -- a person, not an institution.
This file answers the four things that actually decide whether the ASO paper can be posted:

  1. WHAT ENDORSEMENT NOW REQUIRES. arXiv's help page says a new submitter without an institutional
     e-mail must seek personal endorsement -- but it also links a blog post about CHANGES to that
     process, and a December 2025 change made institutional e-mail insufficient on its own for
     Mathematics, with a January 2026 post extending it. If institutional e-mail no longer qualifies
     anyone automatically, an unaffiliated author is in the SAME position as every other new
     author, which is a materially different finding from "you are locked out".
  2. WHETHER THE PAPER'S EXISTING BUILD IS SUBMITTABLE. arXiv refuses "PDF created from TeX/LaTeX
     source" because it wants the source instead. This repository's PDF is printed from HTML by
     Chromium (`build_submission_pdf.py`, Page.printToPDF), so the prohibition does not reach it --
     but the format, figure, file-name and ancillary-file rules do, and they are read here.
  3. WHICH CATEGORY, and whether a therapeutic-design paper is topical for it.
  4. WHO COULD ENDORSE. arXiv's own instructions are to find an endorser among authors of related
     arXiv papers, via the "Which authors of this paper are endorsers?" link on an abstract page.
     That is a search this repository can run, so it runs it rather than telling a human to.

⚠ WHAT THIS DELIBERATELY DOES NOT DO. It records candidate papers and the public endorser listing
arXiv itself publishes for them. It does NOT harvest e-mail addresses, and it does not contact
anyone: arXiv states that mailing large numbers of potential endorsers at once is inappropriate, and
outreach is an outward-facing act that belongs to the named human author under CLAUDE.md §3. The
output is a shortlist for a person to choose from, not a mailing list.

Emits research/literature/arxiv-aso-route.json.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

POLICY_TARGETS = {
    # ── what endorsement requires NOW, not when the help page was last rewritten ────────
    "endorsement_help": "https://info.arxiv.org/help/endorsement.html",
    "endorsement_blog_2026": "https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/",
    "endorsement_blog_2025_math":
        "https://blog.arxiv.org/2025/12/10/updated-endorsement-policy-for-arxiv-mathematics/",
    "register_help": "https://info.arxiv.org/help/registerhelp.html",
    # ── is this paper's existing build submittable as it stands ────────────────────────
    "submit_guidelines": "https://info.arxiv.org/help/submit/index.html",
    "submit_pdf": "https://info.arxiv.org/help/submit_pdf.html",
    "ancillary_files": "https://info.arxiv.org/help/ancillary_files.html",
    "size_limits": "https://info.arxiv.org/help/submit/index.html#oversized",
    # ── which category, and is a therapeutic-design paper topical there ────────────────
    "category_taxonomy": "https://arxiv.org/category_taxonomy",
    "moderation": "https://info.arxiv.org/help/moderation/index.html",
    "policies_index": "https://info.arxiv.org/help/policies/index.html",
    # ── the things a living preprint and a later journal submission depend on ──────────
    "licenses": "https://info.arxiv.org/help/license/index.html",
    "versions": "https://info.arxiv.org/help/versions.html",
    "doi_help": "https://info.arxiv.org/help/doi.html",
    "withdraw": "https://info.arxiv.org/help/withdraw.html",
    "submit_journal_ref": "https://info.arxiv.org/help/jref.html",
}

#: ⛔ THESE QUERIES ARE THE PAPER'S OWN SUBJECT, NOT "BIOLOGY". An endorser must be able to see that
#: the work belongs in the category, so a candidate pool drawn from unrelated q-bio work would be
#: useless to a person and rude to the recipients. The ASO paper computes fusion-junction-selective
#: antisense oligonucleotides and their off-target risk, so these are the four things it is about.
ENDORSER_QUERIES = {
    "antisense_oligo_qbio": 'cat:q-bio* AND (abs:"antisense oligonucleotide" OR abs:gapmer)',
    "oligo_offtarget": 'cat:q-bio* AND (abs:"off-target" AND (abs:oligonucleotide OR abs:siRNA OR abs:ASO))',
    "fusion_oncogene_qbio": 'cat:q-bio* AND (abs:"fusion oncogene" OR abs:"fusion transcript" OR abs:"gene fusion")',
    "rna_target_design": 'cat:q-bio.BM AND (abs:"RNA target" OR abs:"secondary structure" AND abs:therapeutic)',
    "sarcoma_qbio": 'cat:q-bio* AND (abs:sarcoma OR abs:"rare cancer")',
}

API = "http://export.arxiv.org/api/query"
OUT = os.path.join("research", "literature", "arxiv-aso-route.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")

PROBES = [
    r"endorse", r"institutional e-?mail", r"academic", r"affiliat", r"automatic",
    r"unaffiliated", r"independent",
    r"PDF", r"LaTeX", r"TeX", r"format", r"figure", r"ancillary", r"size", r"MB",
    r"licen[cs]e", r"CC ?BY", r"version", r"\bDOI\b", r"withdraw", r"journal reference",
    r"moderat", r"topical", r"refereeable", r"remove", r"reclassif",
    r"q-bio", r"quantitative biology", r"Genomics", r"Biomolecules", r"Molecules",
]

ATOM = "{http://www.w3.org/2005/Atom}"


def probe_hits(text):
    out = {}
    for pat in PROBES:
        for m in re.finditer(pat, text, re.I):
            a, b = max(0, m.start() - 200), min(len(text), m.end() + 200)
            out.setdefault(pat, []).append(re.sub(r"\s+", " ", text[a:b]).strip())
            if len(out[pat]) >= 4:
                break
    return out


def api_query(query, limit=25):
    """arXiv's Atom API. Stdlib only; the runner reaches it, the dev sandbox 403s at the proxy."""
    url = f"{API}?{urllib.parse.urlencode({'search_query': query, 'start': 0, 'max_results': limit, 'sortBy': 'submittedDate', 'sortOrder': 'descending'})}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as fh:
        raw = fh.read().decode("utf-8", "replace")
    root = ET.fromstring(raw)
    total = root.findtext("{http://a9.com/-/spec/opensearch/1.1/}totalResults")
    out = []
    for e in root.findall(ATOM + "entry"):
        eid = (e.findtext(ATOM + "id") or "").rsplit("/", 1)[-1]
        cats = [c.get("term") for c in e.findall(ATOM + "category")]
        out.append({
            "arxiv_id": eid,
            "title": re.sub(r"\s+", " ", (e.findtext(ATOM + "title") or "")).strip(),
            "published": e.findtext(ATOM + "published"),
            "primary_category": (e.find("{http://arxiv.org/schemas/atom}primary_category") or {}).get("term")
                if e.find("{http://arxiv.org/schemas/atom}primary_category") is not None else None,
            "categories": cats,
            "authors": [a.findtext(ATOM + "name") for a in e.findall(ATOM + "author")],
        })
    return {"query": query, "total_results": total, "n_returned": len(out), "entries": out}


def fetch_pages(page, targets, records, harvest=()):
    for name, url in targets.items():
        rec = {"url": url, "attempts": []}
        for attempt, wait in enumerate([0, 8, 25], start=1):
            if wait:
                time.sleep(wait)
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                status = resp.status if resp else None
                page.wait_for_timeout(2500)
                text = page.inner_text("body")
                rec["attempts"].append({"n": attempt, "status": status, "chars": len(text)})
                if status and status < 400 and len(text) > 300:
                    rec.update({"final_url": page.url, "status": status, "title": page.title(),
                                "chars": len(text), "probe_hits": probe_hits(text),
                                "text": text[:150000]})
                    break
                if status == 403:
                    rec.update({"status": 403, "chars": len(text), "text": text[:3000],
                                "note": "403 under a real browser; not fixable by retrying"})
                    break
            except Exception as exc:                          # noqa: BLE001 - recorded, not raised
                rec["attempts"].append({"n": attempt, "error": f"{type(exc).__name__}: {exc}"})
        rec.setdefault("status", None)
        records[name] = rec
        print(f"{str(rec.get('status')):>5}  {rec.get('chars', 0):>7}  {name}", flush=True)
        time.sleep(2)


def main():
    from playwright.sync_api import sync_playwright

    policy, searches, endorser_pages = {}, {}, {}

    # ── 1. the API search runs first: it is stdlib, cheap, and it decides which abstract
    #       pages are worth opening with a browser at all.
    for name, q in ENDORSER_QUERIES.items():
        try:
            searches[name] = api_query(q)
            print(f"  api  {searches[name]['n_returned']:>3} of {searches[name]['total_results']:>6}  {name}",
                  flush=True)
        except Exception as exc:                              # noqa: BLE001
            searches[name] = {"query": q, "error": f"{type(exc).__name__}: {exc}"}
            print(f"  api  ERROR  {name}: {exc}", flush=True)
        time.sleep(3)                                          # arXiv asks for a 3s courtesy delay

    # ⛔ ONE ABSTRACT PAGE PER CANDIDATE PAPER, CAPPED. arXiv publishes an endorser listing per
    # paper and tells authors to use it; opening a handful is using the service as documented.
    # Opening hundreds would not be, and would not help a human choose either.
    top = []
    for name, res in searches.items():
        for e in res.get("entries", [])[:3]:
            top.append((f"{name}::{e['arxiv_id']}", f"https://arxiv.org/auth/show-endorsers/{e['arxiv_id'].split('v')[0]}"))
    endorser_targets = dict(top[:12])

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900},
                                  locale="en-GB", java_script_enabled=True)
        ctx.set_extra_http_headers({
            "Accept-Language": "en-GB,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
        })
        page = ctx.new_page()
        fetch_pages(page, POLICY_TARGETS, policy)
        fetch_pages(page, endorser_targets, endorser_pages)
        ctx.close()
        browser.close()

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({
            "_what": "arXiv's endorsement, format, category, licence and versioning rules, plus a "
                     "candidate-endorser search in q-bio, fetched from a GitHub Actions runner.",
            "_why": "bioRxiv declined this project's ASO paper because the author is unaffiliated. "
                    "arXiv's gate is endorsement rather than affiliation, so what decides the route "
                    "is what endorsement currently requires and who could give it.",
            "_scope": "Public help, policy and blog pages, and arXiv's own public API and endorser "
                      "listings. No login, no e-mail harvesting, no contact with any person.",
            "_generator": "scripts/arxiv_route_fetch.py",
            "_absence_note": "A probe that does not fire means the phrase is absent from the page, "
                             "not that the rule is absent. Read the stored text.",
            "policy": policy,
            "endorser_search": searches,
            "endorser_listings": endorser_pages,
        }, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    got = sum(1 for r in policy.values() if (r.get("status") or 999) < 400)
    print(f"\nwrote {OUT}: {got}/{len(policy)} policy pages, "
          f"{sum(r.get('n_returned', 0) for r in searches.values())} candidate papers")
    return 0 if got else 1


if __name__ == "__main__":
    sys.exit(main())
