#!/usr/bin/env python3
"""Which of the journals that publish THIS PAPER'S SHAPE have a $0 author route?

⭐ WHY THIS EXISTS. `nat_scope_census.py --term` established that a computation-only antisense
paper is ordinary — 323 original papers across 183 journals. trimcrae, 2026-08-25: "Yeah we need to
find out what journals are free… Don't look at all 183 though, just the good fits." So this screens
a SCOPE-FILTERED shortlist rather than the tail, and every exclusion is written down beside the
inclusions so the shortlist can be argued with instead of trusted.

⛔ THE ONE THING THIS SCREEN CANNOT SEE, AND OUR OWN RECORD IS THE COUNTEREXAMPLE. "No mandatory
APC" IS NOT "free". Nucleic Acid Therapeutics is a subscription journal, carries no APC on the
subscription route, and still charges $90 per typeset page plus colour — read at primary source on
2026-08-23. Page and colour charges are administered per journal, appear on author-guideline pages
that return 403 to the egress proxy AND to an Actions runner, and exist in no structured database.
So a SUBSCRIPTION_OR_HYBRID verdict below means "no APC is charged", never "this is free", and the
gap between those two is exactly the amount NAT costs.

SOURCES, all structured and all $0:
  NLM Catalog (E-utilities)  ISSN, full title, and the title history that tells us whether two rows
                             are two journals or one journal renamed.
  OpenAlex                   is_oa, is_in_doaj, apc_usd, publisher — a bibliographic database, not
                             a publisher page, and labelled as such in the output.
  DOAJ                       indexes only fully open-access journals; its APC record distinguishes
                             a diamond journal (free to read AND free to publish) from a gold one.

NETWORK. All three are 403'd or unreachable from the dev sandbox; this runs on an Actions runner.

Run:
    python3 research/manuscripts/venue_fee_screen.py          # fetch + write (CI)
    python3 research/manuscripts/venue_fee_screen.py --check   # offline: re-read the artifact
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "aso", "venue-fee-screen.json")
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

#: ⭐ THE SHORTLIST, AND WHY EACH ROW IS ON IT. Drawn from the journals with two or more non-review
#: computation-only antisense papers in `aso-design-only-census.json`, then filtered on whether the
#: journal could plausibly host a fusion-junction ASO DESIGN paper from an unaffiliated single
#: author with no wet-lab data. The count is evidence the journal publishes the SHAPE; the note is
#: the judgement that it would publish THIS shape. The judgement is mine and is arguable.
SHORTLIST = [
    ("Nucleic Acid Ther", "the modality journal, and the current plan of record"),
    ("Oligonucleotides", "apparent former title of Nucleic Acid Ther — verified below, not assumed"),
    ("Antisense Nucleic Acid Drug Dev", "apparent earlier title of the same journal"),
    ("Mol Ther Nucleic Acids", "second-highest count; nucleic-acid therapeutics, exact scope"),
    ("Nucleic Acids Res", "highest count of any journal in the census"),
    ("NAR Genom Bioinform", "nucleic-acid methods, plausible for a screening paper"),
    ("RNA", "RNA biology; a junction-pairing screen is an RNA result"),
    ("RNA Biol", "same reasoning as RNA"),
    ("Mol Ther", "gene and oligonucleotide therapy, parent journal of MTNA"),
    ("Bioinformatics", "the screen is a method; a methods framing has a home here"),
    ("BMC Bioinformatics", "same reasoning as Bioinformatics"),
    ("Biochem Biophys Res Commun", "broad, takes short computational reports"),
    ("Biochem J", "broad biochemistry, hybrid publisher"),
    ("Genes Cells", "broad molecular biology, hybrid publisher"),
    ("Int J Mol Sci", "publishes exactly this shape; fee model needs stating"),
    ("Biomedicines", "same as IJMS — appears in the census, fee model needs stating"),
    ("Genes (Basel)", "two ASO-design papers in the census design-language list"),
    ("Sci Rep", "generalist that takes computation-only work"),
    ("PLoS One", "generalist that takes computation-only work"),
    ("J Chem Inf Model", "the degrader paper's venue; $0 route already established here"),
]

#: ⛔ EXCLUDED, WITH THE REASON, because a shortlist that hides its exclusions is an assertion.
EXCLUDED = {
    "bioRxiv": "a preprint server, not a journal — and it declined this author as unaffiliated",
    "Res Sq": "a preprint server, not a journal",
    "Methods Mol Biol": "a protocols book series, not a journal taking primary research",
    "Nature": "no realistic path for a single-author, wet-lab-free rare-disease design paper",
    "Nat Commun": "same tier judgement as Nature",
    "Proc Natl Acad Sci U S A": "same tier judgement; also needs a member communicator route",
    "Cell Rep": "same tier judgement",
    "J Clin Invest": "same tier judgement, and it wants clinical or in-vivo data",
    "J Am Chem Soc": "same tier judgement, and the framing is not chemical",
    "Angew Chem Int Ed Engl": "same tier judgement, and the framing is not chemical",
    "Am J Hum Genet": "human genetics; this paper reports no new genetic observation",
    "PLoS Genet": "human genetics, same reason",
    "Genome Med": "human genomics, same reason",
    "Hum Mutat": "variant curation, wrong subject",
    "Mol Genet Genomic Med": "clinical genetics, wrong subject",
    "Dev Biol": "developmental biology; its ASO papers are morpholinos in embryos",
    "Endocrinology": "wrong organ scope",
    "J Neurochem": "the ASO literature here is neurological, wrong disease scope",
    "Curr Neuropharmacol": "wrong disease scope",
    "Brain Commun": "wrong disease scope",
    "Front Cardiovasc Med": "wrong disease scope",
    "J Cell Mol Med": "broad but its census hits are not design work",
    "CPT Pharmacometrics Syst Pharmacol": "pharmacokinetic modelling, a different kind of dry paper",
    "J Pharmacokinet Pharmacodyn": "same as CPT",
    "Pharm Res": "formulation and PK, wrong subject",
    "J Biol Chem": "moved to full open access with a mandatory APC; excluded on fee, not scope",
    "J Biomol Struct Dyn": "structure-simulation journal; the paper models no structure",
}


def _get(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode(errors="replace")
        except Exception as exc:  # noqa: BLE001
            last = exc
            print(f"  retry {i + 1}: {exc}", file=sys.stderr)
            time.sleep(2 ** i)
    print(f"  FAILED: {url}: {last}", file=sys.stderr)
    return None


def _nlm(abbrev):
    """ISSN-Linking, title and title history for the catalogue record whose MedlineTA is EXACTLY
    the abbreviation asked for.

    ⛔ TAKING THE FIRST ISSN IN THE RECORD IS THE BUG THIS REPLACES (found 2026-08-25). An NLM
    catalogue record lists the ISSNs of related and continuing titles too, so `issns[0]` for
    "Nucleic Acids Res" was 0261-3166 — a different journal — and OpenAlex duly answered about that
    one, returning "no mandatory APC" for a journal that is fully open access with a mandatory APC.
    A wrong identifier does not fail loudly; it returns a confident answer about something else.

    So: ISSNLinking is NLM's single canonical ISSN for the record, and MedlineTA is checked against
    the abbreviation before the record is accepted at all. A record that cannot be matched returns
    empty and the row says so, rather than inheriting a neighbour's fee model.
    """
    q = urllib.parse.quote(f'"{abbrev}"[ta]')
    js = _get(f"{EUTILS}/esearch.fcgi?db=nlmcatalog&retmode=json&retmax=10&term={q}"
              "&tool=rare-cancers&email=trimcrae@gmail.com")
    if not js:
        return {"lookup": "esearch failed"}
    try:
        ids = json.loads(js)["esearchresult"]["idlist"]
    except Exception:  # noqa: BLE001
        return {"lookup": "esearch returned no idlist"}
    if not ids:
        return {"lookup": "no catalogue record"}
    xml = _get(f"{EUTILS}/efetch.fcgi?db=nlmcatalog&retmode=xml&id={','.join(ids)}"
               "&tool=rare-cancers&email=trimcrae@gmail.com") or ""
    # ⛔ CAPTURE THE BYTES ON FAILURE. Two parses of NCBI XML have now been written from an
    # assumption about the element names and both were wrong, returning empty rather than raising.
    # The head of the real response is carried out in the artifact so the next fix is made against
    # the document instead of against another guess.
    for chunk in re.split(r"<NLMCatalogRecord>", xml)[1:]:
        ta = re.search(r"<MedlineTA>(.*?)</MedlineTA>", chunk, re.S)
        ta = re.sub(r"<[^>]+>", "", ta.group(1)).strip() if ta else ""
        if ta.lower() != abbrev.lower():
            continue
        linking = re.search(r"<ISSNLinking>([\dXx-]+)</ISSNLinking>", chunk)
        allissn = re.findall(r"<ISSN[^>]*>([\dXx-]+)</ISSN>", chunk)
        title = re.search(r"<TitleMain>.*?<Title>(.*?)</Title>", chunk, re.S)
        notes = re.findall(r"<GeneralNote[^>]*>(.*?)</GeneralNote>", chunk, re.S)
        hist = re.findall(r"<(?:PreviousTitle|IndexingHistory|TitleRelated)[^>]*>(.*?)"
                          r"</(?:PreviousTitle|IndexingHistory|TitleRelated)>", chunk, re.S)
        clean = lambda t: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t or "")).strip()  # noqa: E731
        return {"lookup": "matched on MedlineTA",
                "medline_ta": ta,
                "issn_linking": linking.group(1) if linking else "",
                "issns_in_record": sorted(set(allissn)),
                "full_title": clean(title.group(1)) if title else "",
                "title_history_notes": [clean(n) for n in notes + hist if clean(n)][:6]}
    return {"lookup": f"no record whose MedlineTA equals {abbrev!r}",
            "raw_efetch_head": xml[:2000],
            "raw_efetch_len": len(xml),
            "element_names_seen": sorted(set(re.findall(r"<([A-Za-z][\w:-]*)[ >]", xml)))[:60]}


def _openalex(issn):
    js = _get(f"https://api.openalex.org/sources/issn:{issn}?mailto=trimcrae@gmail.com")
    if not js:
        return {}
    try:
        d = json.loads(js)
    except Exception:  # noqa: BLE001
        return {}
    return {"openalex_display_name": d.get("display_name"),
            "publisher": (d.get("host_organization_name") or ""),
            "is_oa": d.get("is_oa"), "is_in_doaj": d.get("is_in_doaj"),
            "apc_usd": (d.get("apc_usd") if d.get("apc_usd") is not None
                        else ((d.get("apc_prices") or [{}])[0].get("price")
                              if d.get("apc_prices") else None))}


def _doaj(issn):
    js = _get(f"https://doaj.org/api/search/journals/issn%3A{issn}")
    if not js:
        return {}
    try:
        d = json.loads(js)
    except Exception:  # noqa: BLE001
        return {}
    if not d.get("results"):
        return {"in_doaj": False}
    bib = d["results"][0].get("bibjson", {})
    apc = bib.get("apc", {})
    return {"in_doaj": True, "doaj_has_apc": apc.get("has_apc"),
            "doaj_apc": [f"{m.get('price')} {m.get('currency')}" for m in (apc.get("max") or [])]}


def _classify(oa, dj):
    """Three verdicts and nothing softer. The wording is deliberate: the middle one says what is
    NOT charged, because saying 'free' there is the exact error NAT would have caused."""
    if dj.get("in_doaj") and dj.get("doaj_has_apc") is False:
        return ("OPEN_AND_NO_APC",
                "fully open access and charges no article-processing fee — free to publish and "
                "free to read, on DOAJ's record")
    if oa.get("is_oa") or dj.get("in_doaj"):
        return ("GOLD_OA_APC",
                "fully open access with an article-processing charge; there is no subscription "
                "route to decline, so this is not a $0 venue")
    return ("SUBSCRIPTION_OR_HYBRID",
            "no mandatory APC — open access is an option the author declines. ⛔ NOT the same as "
            "free: page and colour charges are set per journal, are in no database, and NAT charges "
            "them on exactly this footing")


def build():
    counts = {}
    census = os.path.join(HERE, "aso", "aso-design-only-census.json")
    if os.path.exists(census):
        c = json.load(open(census, encoding="utf-8"))
        for r in c.get("candidates", []):
            if not any("Review" in t for t in r.get("pub_types", [])):
                counts[r["journal"]] = counts.get(r["journal"], 0) + 1

    rows = []
    for abbrev, why in SHORTLIST:
        print(f"  {abbrev} …", file=sys.stderr)
        nlm = _nlm(abbrev)
        time.sleep(0.4)
        oa, dj = {}, {}
        issn = nlm.get("issn_linking") or ""
        if issn:
            oa = _openalex(issn)
            time.sleep(0.3)
            if oa:
                dj = _doaj(issn)
                time.sleep(0.3)
        oa["issn_used"] = issn or None
        if not oa.get("issn_used") or not oa.get("openalex_display_name"):
            # ⛔ No verdict without an identifier we can defend. An unresolved row must read as
            # unresolved, never as the permissive default.
            verdict, reading = ("UNRESOLVED",
                                "no canonical ISSN matched, or no OpenAlex record for it — this row "
                                "is not evidence of anything and must be read by hand")
        else:
            verdict, reading = _classify(oa, dj)
        rows.append({"journal_abbrev": abbrev, "why_shortlisted": why,
                     "computation_only_papers_in_census": counts.get(abbrev, 0),
                     **nlm, **oa, **dj, "verdict": verdict, "reading": reading})
    rows.sort(key=lambda r: (r["verdict"] != "OPEN_AND_NO_APC",
                             r["verdict"] != "SUBSCRIPTION_OR_HYBRID",
                             r["verdict"] == "UNRESOLVED",
                             -r["computation_only_papers_in_census"]))
    return {
        "_what": ("A fee screen of the journals that have actually published this paper's shape, "
                  "scope-filtered to plausible homes for a fusion-junction ASO design paper."),
        "_why": ("trimcrae, 2026-08-25: 'we need to find out what journals are free… just the good "
                 "fits'. The shortlist and its exclusions are both written down so the filter can "
                 "be argued with."),
        "⛔_no_mandatory_APC_is_not_free": (
            "SUBSCRIPTION_OR_HYBRID means no article-processing charge, NOT $0. Nucleic Acid "
            "Therapeutics is subscription, has no APC, and charges $90 per typeset page plus "
            "colour — read at primary source 2026-08-23. Page and colour charges are per-journal, "
            "live only on author-guideline pages that 403 to the proxy and to CI alike, and appear "
            "in no structured source. Every row below carries that unknown."),
        "⚠_these_are_databases_not_publisher_pages": (
            "OpenAlex and DOAJ are bibliographic databases. They are the best machine-readable "
            "evidence available and they are not the journal's own fee page. A row is a lead to "
            "confirm in a browser before submitting, not a fee quotation."),
        "⛔_a_wrong_identifier_answers_confidently": (
            "The first run of this screen took the first ISSN in each NLM record. Those records "
            "list related and continuing titles too, so Nucleic Acids Research resolved to "
            "0261-3166 — a different journal — and the screen reported 'no mandatory APC' for a "
            "fully open-access journal that charges one. Rows are now keyed on ISSNLinking and "
            "accepted only when MedlineTA matches the abbreviation exactly; anything unmatched is "
            "UNRESOLVED rather than defaulted."),
        "_sources": ["NLM Catalog via E-utilities", "api.openalex.org", "doaj.org/api"],
        "excluded_from_the_shortlist": EXCLUDED,
        "journals": rows,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--check" in argv:
        if not os.path.exists(OUT):
            print("venue-fee-screen.json is not built", file=sys.stderr)
            return 1
        d = json.load(open(OUT, encoding="utf-8"))
        for r in d["journals"]:
            print(f"{r['verdict']:24s} {r['journal_abbrev']}")
        return 0
    d = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}: {len(d['journals'])} journals screened", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
