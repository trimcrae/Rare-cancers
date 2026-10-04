#!/usr/bin/env python3
"""Finite public API retrieval; raw responses retained with hashes, no browsers."""
import concurrent.futures
import hashlib
import json
import pathlib
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
CACHE = ROOT / "sources"
CACHE.mkdir(exist_ok=True)
QUERIES = {
    "chrna6_emc": "CHRNA6 AND (extraskeletal OR chondrosarcoma)",
    "insm1_chondrosarcoma": "INSM1 AND chondrosarcoma",
    "insm1_mesenchymal": "INSM1 AND (sarcoma OR mesenchymal)",
    "emc_ish": '("extraskeletal myxoid chondrosarcoma") AND ("RNA in situ" OR chromogenic OR CHRNA6)',
    "emc_diagnostic": '("extraskeletal myxoid chondrosarcoma" OR "NR4A3-rearranged sarcoma") AND (diagnostic OR immunohistochemical) AND FIRST_PDATE:[2023-01-01 TO 2026-10-04]',
    "historical_neuroendocrine": '("myxoid chondrosarcoma") AND (neuroendocrine OR synaptophysin OR INSM1)',
}

def get(key, url):
    dest = CACHE / f"{key}.json"
    if dest.exists():
        raise RuntimeError(f"Refusing unchanged reacquisition: {key}")
    started = datetime.now(timezone.utc).isoformat()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "EMC-public-source-research/1.0"})
        with urllib.request.urlopen(req, timeout=40) as r:
            body = r.read(4 * 1024 * 1024 + 1)
            if len(body) > 4 * 1024 * 1024:
                raise RuntimeError("Source exceeds 4 MiB per-response budget")
            status, final, ctype = r.status, r.url, r.headers.get("Content-Type")
        json.loads(body)
        dest.write_bytes(body)
        return {"key": key, "url": url, "final_url": final, "status": status,
                "content_type": ctype, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                "started_utc": started, "completed_utc": datetime.now(timezone.utc).isoformat(),
                "path": str(dest.relative_to(ROOT))}
    except Exception as e:
        return {"key": key, "url": url, "started_utc": started, "error": repr(e)}

if __name__ == "__main__":
    requests = []
    for key, q in QUERIES.items():
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": q, "format": "json", "resultType": "core", "pageSize": 1000})
        requests.append((key, url))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        receipts = list(pool.map(lambda args: get(*args), requests))
    (ROOT / "SEARCH-RECEIPTS.json").write_text(json.dumps(receipts, indent=2) + "\n")
    for receipt in receipts:
        print(receipt["key"], receipt.get("bytes"), receipt.get("error"))
    records = {}
    for key in QUERIES:
        p = CACHE / f"{key}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_bytes())
        print("query", key, "hits", d["hitCount"])
        if d["hitCount"] > 1000:
            raise RuntimeError("Search pagination needed, record incomplete")
        for row in d["resultList"]["result"]:
            ident = row.get("pmid") or row["id"]
            records.setdefault(ident, {"record": row, "queries": []})["queries"].append(key)
    (ROOT / "SEARCH-INDEX.json").write_text(json.dumps(records, indent=2) + "\n")
    for ident, item in records.items():
        row = item["record"]
        print(ident, row.get("pubYear"), row.get("pmcid"), row.get("title", "[no title in source]"), ";".join(item["queries"]))
