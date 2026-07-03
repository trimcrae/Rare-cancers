#!/usr/bin/env python3
"""
EMC cell-line data probe — does real EMC surface / expression data exist publicly?

WHY. The surfaceome scan (emc_surfaceome_scan.py) uses DepMap SARCOMA lines as an EMC surrogate
because the real patient-derived EMC lines are not in DepMap. But those lines now EXIST — USZ-EMC
(Bangerter 2022/2023) and NCC-EMC1-C1 (Iwata 2025) — and their establishment papers may (a) report
an immunophenotype (real EMC surface markers) and (b) have deposited RNA-seq (GEO/SRA/DDBJ), which
would let us re-run the surfaceome scan on REAL EMC transcriptomes. This probe answers both, from a
GitHub-hosted runner (open internet; the dev sandbox / agent proxy 403s NCBI+EBI).

WHAT.
  1. Europe PMC: fetch the two establishment papers' abstract + open-access full text (where OA),
     and regex-scan the full text for data-availability ACCESSIONS (GEO GSE/GSM, SRA/BioProject,
     DDBJ DRA, ArrayExpress/BioStudies) and for reported IHC/surface markers.
  2. NCBI eutils (esearch): query GEO DataSets (db=gds) and SRA (db=sra) for EMC / EWSR1-NR4A3
     datasets, returning any accessions + titles — an independent check for deposited EMC data.

Output: emc-line-data-probe.json  (surface markers found + accessions found). Internet required.
This is a LITERATURE/DATABASE PROBE, not a claim; every hit must be human-verified before use.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "emc-line-data-probe.json")

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# The two EMC cell-line establishment papers (+ the older 2-model EMC paper is the same Bangerter PMC).
PAPERS = [
    {"tag": "NCC-EMC1-C1 (Iwata 2025)", "ext_id": "40580361", "src": "MED"},
    {"tag": "USZ EMC models (Bangerter 2022/2023)", "pmcid": "PMC9813045"},
]

# Accession patterns for deposited expression/sequence data.
ACC_PATTERNS = {
    "GEO_series": r"GSE\d{3,7}",
    "GEO_sample": r"GSM\d{4,8}",
    "SRA": r"SR[APRXZ]\d{5,9}",
    "BioProject": r"PRJ(?:NA|EB|DB)\d{4,8}",
    "DDBJ_DRA": r"DRA\d{5,7}",
    "DDBJ_run": r"DR[RXP]\d{5,7}",
    "ArrayExpress": r"E-[A-Z]{4}-\d{3,6}",
    "BioStudies": r"S-BSST\d{3,7}",
}
# Surface / immunophenotype markers worth catching in full text (CD/surface first).
MARKER_TERMS = ["CD56", "NCAM", "CD99", "CD34", "CD117", "KIT", "EMA", "MUC4", "S100", "S-100",
                "NKX2-2", "NKX2.2", "synaptophysin", "chromogranin", "INI1", "SMARCB1", "vimentin",
                "SOX", "GFAP", "cytokeratin", "desmin", "SMA", "ERG", "B7-H3", "CD276", "MCAM",
                "CD146", "EGFR", "HER2", "CDH11", "cadherin-11", "FGFR", "GPC2", "PTK7"]


def _get(url, timeout=60, accept="application/json"):
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0", "Accept": accept})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa
            print(f"  retry {i+1} {url[:70]}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    return ""


def scan_text(text):
    accs = {k: sorted(set(re.findall(p, text))) for k, p in ACC_PATTERNS.items()}
    accs = {k: v for k, v in accs.items() if v}
    markers = sorted({m for m in MARKER_TERMS if re.search(r"\b" + re.escape(m) + r"\b", text, re.I)})
    # pull the data-availability sentence(s) if present
    da = re.findall(r"(data availability[^\n]{0,400}|accession[^\n]{0,300}|deposited[^\n]{0,300})",
                    text, re.I)
    return accs, markers, da[:6]


def probe_epmc(paper):
    out = {"paper": paper["tag"], "abstract": None, "fulltext_available": False,
           "accessions": {}, "markers_found": [], "data_availability_snippets": []}
    # resolve to a core record for the abstract
    if paper.get("ext_id"):
        q = f"EXT_ID:{paper['ext_id']} AND SRC:{paper['src']}"
    else:
        q = f"PMCID:{paper['pmcid']}"
    core = _get(f"{EPMC}/search?query={urllib.parse.quote(q)}&resultType=core&format=json")
    pmcid = paper.get("pmcid")
    try:
        j = json.loads(core)
        res = (j.get("resultList", {}).get("result") or [{}])[0]
        out["abstract"] = (res.get("abstractText") or "")[:4000] or None
        pmcid = pmcid or res.get("pmcid")
        out["title"] = res.get("title")
    except Exception as e:  # noqa
        out["epmc_core_error"] = str(e)
    # scan abstract
    if out["abstract"]:
        a_acc, a_mark, a_da = scan_text(out["abstract"])
        out["accessions"] = a_acc
        out["markers_found"] = a_mark
        out["data_availability_snippets"] = a_da
    # try open-access full text (richer for markers + accessions)
    if pmcid:
        ft = _get(f"{EPMC}/{pmcid}/fullTextXML", accept="application/xml")
        if ft and len(ft) > 2000:
            out["fulltext_available"] = True
            f_acc, f_mark, f_da = scan_text(ft)
            # merge (full text supersedes/extends abstract)
            for k, v in f_acc.items():
                out["accessions"].setdefault(k, [])
                out["accessions"][k] = sorted(set(out["accessions"][k]) | set(v))
            out["markers_found"] = sorted(set(out["markers_found"]) | set(f_mark))
            out["data_availability_snippets"] = (out["data_availability_snippets"] + f_da)[:8]
    return out


def probe_geo_sra():
    """esearch GEO DataSets + SRA for EMC / EWSR1-NR4A3 datasets."""
    result = {}
    terms = ['"extraskeletal myxoid chondrosarcoma"', '"EWSR1-NR4A3" OR "EWSR1::NR4A3"']
    for db in ("gds", "sra"):
        hits = []
        for term in terms:
            url = (f"{EUTILS}/esearch.fcgi?db={db}&term={urllib.parse.quote(term)}"
                   f"&retmax=20&retmode=json")
            txt = _get(url)
            try:
                ids = json.loads(txt).get("esearchresult", {}).get("idlist", [])
            except Exception:  # noqa
                ids = []
            if ids:
                # summarise to accessions/titles
                summ = _get(f"{EUTILS}/esummary.fcgi?db={db}&id={','.join(ids[:20])}&retmode=json")
                try:
                    js = json.loads(summ).get("result", {})
                    for i in js.get("uids", []):
                        rec = js.get(i, {})
                        hits.append({"accession": rec.get("accession") or rec.get("gse")
                                     or rec.get("expxml", "")[:0] or i,
                                     "title": (rec.get("title") or rec.get("summary") or "")[:200],
                                     "gpl_taxon": rec.get("taxon"),
                                     "n_samples": rec.get("n_samples")})
                except Exception as e:  # noqa
                    hits.append({"esummary_error": str(e)})
            time.sleep(0.5)
        # dedup by accession
        seen, uniq = set(), []
        for h in hits:
            k = h.get("accession")
            if k and k not in seen:
                seen.add(k); uniq.append(h)
        result[db] = uniq
    return result


def main():
    papers = [probe_epmc(p) for p in PAPERS]
    try:
        geo_sra = probe_geo_sra()
    except Exception as e:  # noqa
        geo_sra = {"error": str(e)}

    any_acc = any(p["accessions"] for p in papers) or bool(
        geo_sra.get("gds") or geo_sra.get("sra"))
    result = {
        "_note": ("Probe for PUBLIC real-EMC surface/expression data (EMC cell lines USZ-EMC, "
                  "NCC-EMC1-C1). Europe PMC abstract/full-text scan for IHC markers + deposited "
                  "accessions, plus NCBI GEO/SRA search. A DATABASE PROBE — every hit must be "
                  "human-verified before it is cited or used to re-point the surfaceome scan."),
        "papers": papers,
        "geo_sra_search": geo_sra,
        "verdict": {
            "any_deposited_accession_found": any_acc,
            "reads": ("if TRUE: fetch that dataset and re-run emc_surfaceome_scan.py on real EMC "
                      "expression; if FALSE: no public EMC transcriptome — the DepMap surrogate "
                      "stands, and the reported IHC markers (if any) are the only real EMC surface "
                      "evidence."),
        },
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({"any_accession": any_acc,
                      "markers": {p["paper"]: p["markers_found"] for p in papers},
                      "paper_accessions": {p["paper"]: p["accessions"] for p in papers},
                      "geo": [h.get("accession") for h in geo_sra.get("gds", [])],
                      "sra": [h.get("accession") for h in geo_sra.get("sra", [])]}, indent=2))


if __name__ == "__main__":
    main()
