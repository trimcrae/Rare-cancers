#!/usr/bin/env python3
"""
EMC Open Target & Drug Atlas — primary full-text verification (EuropePMC).

WHY. The v0.1 atlas verified load-bearing facts at ABSTRACT level only (the dev sandbox blocks
PubMed/PMC/Springer/EuropePMC). This script runs in GitHub Actions (unrestricted internet) and
pulls PRIMARY full text from the EuropePMC REST API for the open-access papers, then extracts the
sentences that bear on the specific items flagged for re-confirmation:
  - Bangerter 2023 (PMC9813045): IC50/EC50 numbers; HDM201/siremadlin present-or-absent;
    carfilzomib+doxorubicin / +venetoclax synergy-vs-additive per-model wording; screen panel size.
  - Iwata 2025 (PMID 40580361): NCC-EMC1-C1 fusion partner; IC50 numbers for brigatinib/panobinostat/romidepsin.
  - Stacchiotti pazopanib/sunitinib/anthracycline, Masunaga registry: confirm the headline numbers.

Pure stdlib. For non-OA papers EuropePMC returns no fullTextXML -> we record 'not_open_access' and
keep the abstract-level citation (honest). Output: research/atlas/_generated/fulltext-verify.json.
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "_generated")
os.makedirs(OUTDIR, exist_ok=True)

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"

# (key, source, id) — source PMC uses PMCID, MED uses PMID.
PAPERS = [
    {"key": "emcModels2023", "name": "Bangerter 2023 USZ", "source": "PMC", "id": "PMC9813045",
     "keywords": ["carfilzomib", "doxorubicin", "PU-H71", "PU H71", "HDM201", "siremadlin",
                  "venetoclax", "proteasome", "HSP90", "IC50", "EC50", "synerg", "additive", "17 "]},
    {"key": "emcCellLine2025", "name": "Iwata 2025 NCC-EMC1-C1", "source": "MED", "id": "40580361",
     "keywords": ["EWSR1", "TAF15", "NR4A3", "brigatinib", "panobinostat", "romidepsin",
                  "IC50", "221", "fusion"]},
    {"key": "pazopanibEMC", "name": "Stacchiotti 2019 pazopanib", "source": "MED", "id": "31331701",
     "keywords": ["EWSR1", "TAF15", "response", "progression-free", "18%", "19", "partial"]},
    {"key": "sunitinibEMC", "name": "Stacchiotti 2014 sunitinib", "source": "MED", "id": "24703573",
     "keywords": ["EWSR1", "TAF15", "partial response", "RECIST", "NR4A3"]},
    {"key": "anthracyclineEMC", "name": "Stacchiotti 2013 anthracycline", "source": "PMC", "id": "PMC3879193",
     "keywords": ["partial response", "progression-free", "8 months", "anthracycline", "PR"]},
    {"key": "japanRegistry2025", "name": "Masunaga 2025 registry", "source": "DOI", "id": "10.1186/s13018-025-06245-6",
     "keywords": ["margin", "local recurrence", "radiotherapy", "chemotherapy", "171", "R1", "R2"]},
]


def _get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-atlas/1.0"})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(), r.getcode()
        except urllib.error.HTTPError as e:
            if e.code in (404, 400):
                return b"", e.code
            print(f"  retry {i+1} {url[:80]}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
        except Exception as e:  # noqa
            print(f"  retry {i+1} {url[:80]}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    return b"", 0


def resolve_id(paper):
    """For DOI, resolve to a EuropePMC id (prefer PMCID for full text)."""
    if paper["source"] in ("PMC", "MED"):
        return paper["source"], paper["id"]
    raw, _ = _get(f"{EPMC}/search?query=DOI:%22{urllib.parse.quote(paper['id'])}%22&format=json&resultType=core")
    try:
        js = json.loads(raw)
        res = js.get("resultList", {}).get("result", [])
        if res:
            r0 = res[0]
            if r0.get("pmcid"):
                return "PMC", r0["pmcid"]
            if r0.get("pmid"):
                return "MED", r0["pmid"]
    except Exception:  # noqa
        pass
    return None, None


def sentences_with(text, keywords):
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    sents = re.split(r"(?<=[.!?])\s+", text)
    out, seen = [], set()
    kws = [k.lower() for k in keywords]
    for s in sents:
        sl = s.lower()
        if any(k in sl for k in kws) and len(s) < 400:
            key = s.strip()[:120]
            if key not in seen:
                seen.add(key)
                out.append(s.strip())
        if len(out) >= 25:
            break
    return out


def numbers_near(text, terms):
    """Find IC50/EC50-like numeric mentions."""
    text = re.sub(r"<[^>]+>", " ", text)
    hits = re.findall(r"(IC50|EC50|GI50)[^.]{0,80}?(\d+\.?\d*\s?(?:nM|uM|µM|mM|nmol|µmol))", text, re.I)
    return [f"{a}: {b}" for a, b in hits][:20]


def verify(paper):
    src, pid = resolve_id(paper)
    rec = {"key": paper["key"], "name": paper["name"], "resolved": f"{src}/{pid}" if pid else None}
    if not pid:
        rec["status"] = "id_unresolved"
        return rec
    # try OA full text (PMC only)
    ft_text = ""
    if src == "PMC":
        raw, code = _get(f"{EPMC}/PMC/{pid}/fullTextXML")
        if code == 200 and raw:
            ft_text = raw.decode("utf-8", "replace")
    if ft_text:
        rec["status"] = "full_text_open_access"
        rec["evidence_sentences"] = sentences_with(ft_text, paper["keywords"])
        rec["ic50_mentions"] = numbers_near(ft_text, paper["keywords"])
        low = re.sub(r"<[^>]+>", " ", ft_text).lower()
        # targeted resolutions
        rec["mentions_present"] = {k: (k.lower() in low) for k in
                                   ["HDM201", "siremadlin", "venetoclax", "carfilzomib", "brigatinib",
                                    "panobinostat", "romidepsin", "EWSR1", "TAF15"]}
    else:
        # fall back to abstract
        raw, _ = _get(f"{EPMC}/search?query=EXT_ID:{pid}%20AND%20SRC:{src}&format=json&resultType=core")
        abstract = ""
        try:
            js = json.loads(raw)
            res = js.get("resultList", {}).get("result", [])
            if res:
                abstract = res[0].get("abstractText", "") or ""
                rec["is_open_access"] = res[0].get("isOpenAccess")
        except Exception:  # noqa
            pass
        rec["status"] = "abstract_only" if abstract else "no_full_text_or_abstract"
        if abstract:
            rec["evidence_sentences"] = sentences_with(abstract, paper["keywords"])
            rec["ic50_mentions"] = numbers_near(abstract, paper["keywords"])
    return rec


def main():
    results = {"_note": "Primary full-text verification via EuropePMC REST (run in CI). OA papers get "
                        "fullTextXML sentence extraction; non-OA fall back to abstract (honest).",
               "papers": []}
    for p in PAPERS:
        print(f"verifying {p['name']} ...", file=sys.stderr)
        try:
            results["papers"].append(verify(p))
        except Exception as e:  # noqa
            results["papers"].append({"key": p["key"], "name": p["name"], "error": str(e)})
    with open(os.path.join(OUTDIR, "fulltext-verify.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("wrote fulltext-verify.json", file=sys.stderr)


if __name__ == "__main__":
    main()
