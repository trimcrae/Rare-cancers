#!/usr/bin/env python3
"""
Primary-source check: did Zaienne 2022 (the anchor-warhead paper) counter-screen compound 19 (or its series)
against the paralogues NR4A1/Nur77 and NR4A2/Nurr1 — i.e. is there ANY literature paralogue-selectivity datum
for our anchor, or is the compound only characterized on NR4A3/NOR-1?

Zaienne D et al., "Druggability Evaluation of the Neuron Derived Orphan Receptor (NOR-1) Reveals Inverse
NOR-1 Agonists," ChemMedChem 2022; PMID 35704774; PMC9542104; doi 10.1002/cmdc.202200259 (open access).

Pulls the article full text (Europe PMC) and dumps verbatim ±350-char windows around every paralogue /
selectivity term, so the "paralogue selectivity is unmeasured" claim rests on the paper's actual text.
Pure stdlib (urllib). Runs on a GitHub Actions CPU runner (dev-sandbox egress-proxy 403s PMC). Never
fabricates: records exactly what is fetched, with source URL + HTTP status; flags anything not retrieved.
"""
import json
import re
import sys
import urllib.request
import urllib.error

PMCID = "PMC9542104"
PMID = "35704774"
DOI = "10.1002/cmdc.202200259"
UA = "rare-cancers-research/1.0 (NR4A3 anchor selectivity verification; mailto:trimcrae@gmail.com)"
NEEDLES = ["NR4A1", "Nur77", "NR4A2", "Nurr1", "paralog", "selectiv", "specific", "off-target",
           "counter-screen", "counterscreen", "cross-react", "isoform"]


def _get(url, accept=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **({"Accept": accept} if accept else {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace"), r.status


def fetch_fulltext_xml():
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{PMCID}/fullTextXML"
    try:
        body, status = _get(url, accept="application/xml")
        return {"url": url, "http_status": status, "ok": status == 200, "body": body}
    except urllib.error.HTTPError as e:
        return {"url": url, "http_status": e.code, "ok": False, "body": ""}
    except Exception as e:  # noqa: BLE001
        return {"url": url, "http_status": None, "ok": False, "error": str(e), "body": ""}


def strip_tags(xml):
    xml = re.sub(r"<xref[^>]*>.*?</xref>", " ", xml, flags=re.S)
    xml = re.sub(r"<[^>]+>", " ", xml)
    xml = re.sub(r"\s+", " ", xml)
    return xml


def windows(text, needles):
    wins = []
    low = text.lower()
    for nd in needles:
        start = 0
        while True:
            i = low.find(nd.lower(), start)
            if i < 0:
                break
            wins.append({"needle": nd, "context": text[max(0, i - 350):i + 350]})
            start = i + len(nd)
            if len(wins) >= 60:
                return wins
    return wins


def main():
    out = {
        "purpose": "Verify whether Zaienne 2022 reports any NR4A1/NR4A2 paralogue counter-screen for the "
                   "anchor warhead (compound 19 / NOR-1 series).",
        "citation": {"pmid": PMID, "pmcid": PMCID, "doi": DOI},
        "disclaimer": "Records only verbatim fetched text. Absence of a paralogue window here means the term "
                      "does not appear in the fetched full text (or the fetch failed) — NOT proof no data "
                      "exists in figures/SI. Interpret conservatively.",
    }
    ft = fetch_fulltext_xml()
    out["fulltext_fetch"] = {k: ft[k] for k in ("url", "http_status", "ok") if k in ft}
    if ft.get("ok") and ft.get("body"):
        text = strip_tags(ft["body"])
        w = windows(text, NEEDLES)
        out["paralogue_windows"] = w
        out["n_windows"] = len(w)
        out["needles_found"] = sorted({x["needle"] for x in w})
        out["needles_absent"] = [n for n in NEEDLES if n not in out["needles_found"]]
    else:
        out["error"] = "Could not fetch full text; retry or use an alternate OA source."
    with open("zaienne-selectivity-verify.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"zaienne_selectivity_verify: fetch_ok={ft.get('ok')} windows={out.get('n_windows', 0)} "
          f"found={out.get('needles_found')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
