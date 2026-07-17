#!/usr/bin/env python3
"""Fetch published COOPERATIVITY (alpha) evidence for congeneric-pair members that lack a curated alpha.

The congeneric search (ternary_calib_search.py) found exactly ONE clean congeneric different-ligand RBFE edge in
the entire PDB VHL-PROTAC set: 7Z76(IFJ) <-> 9HYB(A1IYB) (7 perturbed heavy atoms, 91% shared scaffold). 9HYB is
smarca2_p3 (alpha=5.0, verified); 7Z76/IFJ has NO curated cooperativity. If 7Z76's degrader has a published
alpha (TR-FRET or ITC) that spans a real class gap vs 5.0, 7Z76->9HYB becomes the valB_mini calibration edge.

This resolves each target PDB's PRIMARY CITATION from RCSB, then pulls the abstract + (if open-access) full text
from EuropePMC and surfaces every sentence mentioning cooperativity / alpha / ITC / K_d ternary — as EVIDENCE FOR
A HUMAN TO CURATE, not an auto-parsed number. No alpha is fabricated or asserted: the script reports what the
primary source says (or that it says nothing about cooperativity), and freezing an alpha remains a manual,
provenance-checked step. Runs on a CI runner (unrestricted internet; the dev sandbox egress-proxy 403s these).
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ternary-calib-alpha-evidence.json")

RCSB_ENTRY = "https://data.rcsb.org/rest/v1/core/entry/{pdb}"
EPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json&resultType=core"
EPMC_FULLTEXT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{src}/{pid}/fullTextXML"

TARGETS = os.environ.get("ALPHA_FETCH_PDBS", "7Z76").split(",")
COOP_RE = re.compile(r"cooperativ|alpha|α|\bITC\b|ternary\s+K[_ ]?d|positive\s+cooperativity|negative\s+cooperativity",
                     re.IGNORECASE)


def _get(url: str, as_json=True):
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-ci",
                                               "Accept": "application/json" if as_json else "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read().decode("utf-8", "replace")
        return json.loads(data) if as_json else data
    except Exception as e:  # noqa: BLE001
        print(f"[alpha] fetch failed {url}: {e}", flush=True)
        return None


def _citation(pdb: str) -> dict:
    e = _get(RCSB_ENTRY.format(pdb=pdb))
    if not e:
        return {}
    cit = (e.get("rcsb_primary_citation") or {})
    # RCSB REST field names vary by case; try the known variants for DOI + PubMed.
    doi = (cit.get("pdbx_database_id_doi") or cit.get("pdbx_database_id_DOI")
           or cit.get("pdbx_database_id_doi".upper()))
    pmid = (cit.get("pdbx_database_id_pub_med") or cit.get("pdbx_database_id_PubMed"))
    return {"title": cit.get("title"), "doi": doi, "pubmed": pmid,
            "journal": cit.get("rcsb_journal_abbrev"), "year": cit.get("year")}


def _epmc_record(doi: str | None, pmid, title: str | None = None) -> dict:
    """Resolve the EuropePMC core record. Prefer DOI/PMID; FALL BACK to an exact-title search (RCSB often omits
    the DOI/PMID, as for 7Z76 — a missing id must not be misread as 'no cooperativity data')."""
    queries = []
    if doi:
        queries.append(f"DOI:{doi}")
    if pmid:
        queries.append(f"EXT_ID:{pmid}")
    if title:
        t = title.strip().rstrip(".").replace('"', "")
        queries.append(f'TITLE:"{t}"')
    for q in queries:
        d = _get(EPMC_SEARCH.format(q=urllib.parse.quote(q)))
        hits = ((d or {}).get("resultList") or {}).get("result") or []
        if hits:
            return hits[0]
    return {}


def _coop_sentences(text: str, limit=40) -> list:
    # strip XML tags → sentences → keep those mentioning cooperativity/alpha/ITC
    plain = re.sub(r"<[^>]+>", " ", text)
    plain = re.sub(r"\s+", " ", plain)
    out = []
    for sent in re.split(r"(?<=[.!?])\s+", plain):
        if COOP_RE.search(sent) and 20 < len(sent) < 400:
            out.append(sent.strip())
            if len(out) >= limit:
                break
    return out


def fetch_one(pdb: str) -> dict:
    cit = _citation(pdb)
    rec = _epmc_record(cit.get("doi"), cit.get("pubmed"), cit.get("title"))
    abstract = rec.get("abstractText") or ""
    src, pid = rec.get("source"), rec.get("id")
    is_oa = str(rec.get("isOpenAccess", "")).upper() in ("Y", "TRUE")
    fulltext_sents, ft_status = [], "not_open_access_or_unavailable"
    if is_oa and src and pid:
        ft = _get(EPMC_FULLTEXT.format(src=src, pid=pid), as_json=False)
        if ft:
            fulltext_sents = _coop_sentences(ft)
            ft_status = f"open_access_fulltext ({len(fulltext_sents)} coop sentences)"
    abstract_hit = bool(COOP_RE.search(abstract))
    return {
        "pdb": pdb, "citation": cit,
        "epmc": {"pmcid": rec.get("pmcid"), "pmid": rec.get("pmid"), "is_open_access": is_oa,
                 "title": rec.get("title")},
        "abstract_mentions_cooperativity": abstract_hit,
        "abstract": abstract if abstract_hit else (abstract[:400] + "…" if abstract else ""),
        "fulltext_status": ft_status,
        "cooperativity_sentences": fulltext_sents,
        "verdict": ("HUMAN-CURATE: cooperativity evidence present — read the sentences/abstract to extract a "
                    "provenance-checked alpha for this ligand" if (abstract_hit or fulltext_sents) else
                    "NO cooperativity/alpha language in the reachable text — this ligand likely has no published "
                    "cooperativity; the congeneric-with-alpha edge is not available from it"),
    }


def main() -> int:
    r = {"_note": "RCSB primary citation + EuropePMC. Evidence for human curation; no alpha fabricated.",
         "targets": [fetch_one(p.strip()) for p in TARGETS if p.strip()]}
    with open(OUT, "w") as f:
        json.dump(r, f, indent=2)
    print(json.dumps(r, indent=2), flush=True)
    print(f"[alpha] wrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
