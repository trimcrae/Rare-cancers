#!/usr/bin/env python3
"""Bounded follow-up for primary papers and broader diagnostic sources."""
import concurrent.futures
import hashlib
import json
import pathlib
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
CACHE = ROOT / "sources"

def fetch(item):
    key, url, suffix = item
    path = CACHE / (key + suffix)
    if path.exists():
        return {"key": key, "error": "unchanged acquisition refused"}
    rec = {"key": key, "url": url, "started_utc": datetime.now(timezone.utc).isoformat()}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "EMC-public-source-research/1.0"})
        with urllib.request.urlopen(req, timeout=35) as r:
            body = r.read(4 * 1024 * 1024 + 1)
            if len(body) > 4 * 1024 * 1024:
                raise RuntimeError("4 MiB response cap exceeded; source remains pending")
            rec.update(status=r.status, final_url=r.url, content_type=r.headers.get("Content-Type"))
        path.write_bytes(body)
        rec.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                   path=str(path.relative_to(ROOT)), completed_utc=datetime.now(timezone.utc).isoformat())
    except Exception as e:
        rec["error"] = repr(e)
    return rec

if __name__ == "__main__":
    tasks = [
        ("insm1_2018_primary", "https://www.nature.com/articles/modpathol2017189.pdf", ".pdf"),
        ("insm1_mesenchymal_titleabs", "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": "TITLE_ABS:INSM1 AND (sarcoma OR mesenchymal)", "format": "json", "resultType": "core", "pageSize": 1000}), ".json"),
    ]
    for ident in ["PMC9750778", "PMC12376927", "PMC9052449", "PMC12285907", "PMC10756670", "PMC13136674", "PMC12504171"]:
        tasks.append((ident, f"https://www.ebi.ac.uk/europepmc/webservices/rest/{ident}/fullTextXML", ".xml"))
    for pmid in ["29327709", "38447752", "36563884", "36376703", "36948401"]:
        tasks.append(("citations_" + pmid, f"https://www.ebi.ac.uk/europepmc/webservices/rest/MED/{pmid}/citations?format=json&pageSize=1000", ".json"))
    for doi in ["10.1016/j.humpath.2022.12.005", "10.1038/modpathol.2017.189", "10.1007/s00428-022-03453-x", "10.1016/j.modpat.2023.100161"]:
        key = "openalex_" + doi.rsplit("/", 1)[1]
        tasks.append((key, "https://api.openalex.org/works/https://doi.org/" + doi, ".json"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        receipts = list(pool.map(fetch, tasks))
    (ROOT / "FOLLOWUP-RECEIPTS.json").write_text(json.dumps(receipts, indent=2) + "\n")
    for r in receipts:
        print(r["key"], r.get("status"), r.get("bytes"), r.get("error"))
