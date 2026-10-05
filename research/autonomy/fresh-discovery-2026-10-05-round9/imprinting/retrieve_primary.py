#!/usr/bin/env python3
"""Bounded ordinary public-API retrieval with explicit source receipts."""
from pathlib import Path
import concurrent.futures
import datetime
import hashlib
import json
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
QUERIES = {
    "emc_locus": '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma") AND (DLK1 OR DIO3 OR MEG3 OR "14q32" OR imprint* OR methylat*)',
    "sarcoma_locus": '(sarcoma OR chondrosarcoma) AND ("DLK1-DIO3" OR "DLK1 DIO3" OR "MEG3-DMR" OR "IG-DMR")',
    "human_dmr": '("IG-DMR" OR "MEG3-DMR") AND (human OR chromosome) AND ("450K" OR Infinium OR coordinate* OR "14q32")',
    "sarcoma_imprinting": 'sarcoma AND (MEG3 OR "14q32") AND (methylat* OR imprint*)',
}


def fetch(name, url, cap=4*1024*1024, method="GET"):
    row = {"name": name, "url": url, "method": method,
           "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "cap": cap}
    try:
        req = urllib.request.Request(url, method=method, headers={"User-Agent": "EMC-public-research/1"})
        with urllib.request.urlopen(req, timeout=35) as response:
            row.update(status=response.status, final_url=response.url,
                       headers={k: v for k, v in response.headers.items()
                                if k.lower() in ["content-length", "content-type", "last-modified", "etag"]})
            if method == "HEAD":
                row["bytes"] = 0
            else:
                data = response.read(cap+1)
                if len(data) > cap:
                    row.update(status="oversize_pending", bytes_observed_at_least=len(data))
                else:
                    target = ROOT / "sources" / name
                    assert not target.exists()
                    target.write_bytes(data)
                    row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                               path=str(target.relative_to(ROOT)))
    except Exception as exc:
        row.update(status="access_failed", error=repr(exc))
    return row


if __name__ == "__main__":
    jobs = []
    for name, query in QUERIES.items():
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": query, "format": "json", "resultType": "core", "pageSize": 1000})
        jobs.append((name+".json", url))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda job: fetch(*job), jobs))
    (ROOT / "PRIMARY-QUERY-RECEIPTS.json").write_text(json.dumps(rows, indent=2)+"\n")
