#!/usr/bin/env python3
"""Shared Europe PMC search plumbing for the citation-index probes.

WHY THIS EXISTS. Four probes in scripts/ (lane, consensus, mortality, host-factor) each
carry their own copy of the same forty lines: a retrying GET, a search wrapper, a hit-row
projection and a summary block. The copies have already drifted -- two retry three times
and one does not, and the mortality probe's `get` gained a life-table caller the others
never got. A fifth and sixth copy would be worse, so the NEW probes import this instead.

⛔ IT DELIBERATELY DOES NOT TOUCH THE EXISTING FOUR. Rewriting a working retrieval script
to use a new helper risks changing what a committed artifact would contain, for no gain
in what any of them retrieves. They stay as they are; this is for what comes next.

WHAT IT DOES NOT DO: classify, conclude, or decide anything. Every probe built on it
records what was asked, how many hits came back and which papers they were. The reading
happens downstream against the retrieved text.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request

SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
FULLTEXT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
UA = "rare-cancers-research/1.0 (github.com/trimcrae/Rare-cancers; mailto:trimcrae@gmail.com)"
SLEEP = 0.34  # Europe PMC asks for <= 3 req/s


def get(url: str, tries: int = 3, timeout: int = 90) -> str:
    """GET with a small backoff. Returns '' rather than raising, so one dead URL cannot
    discard a whole corpus -- a probe that dies on hit 200 of 400 has retrieved nothing
    a reader can use."""
    last = ""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as fh:
                return fh.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001 - a probe must survive one bad URL
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(1.5 * (attempt + 1))
    print(f"  ! give up on {url}: {last}", file=sys.stderr)
    return ""


def search(query: str, page_size: int = 25, cursor: str = "*") -> dict:
    params = urllib.parse.urlencode({
        "query": query,
        "format": "json",
        "pageSize": str(page_size),
        "cursorMark": cursor,
        "resultType": "core" if page_size <= 25 else "lite",
    })
    raw = get(f"{SEARCH}?{params}")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def hit_row(r: dict) -> dict:
    return {
        "pmid": r.get("pmid"),
        "pmcid": r.get("pmcid"),
        "doi": r.get("doi"),
        "title": r.get("title"),
        "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title")
                   or r.get("journalTitle"),
        "year": r.get("pubYear"),
        "citedBy": r.get("citedByCount"),
        "isOpenAccess": r.get("isOpenAccess"),
    }


def run_index(queries, page_size: int = 25) -> dict:
    """Run a list of (key, query, what_a_hit_would_mean) and return the index.

    ⚠ `hitCount is None` means the API call FAILED and is kept distinct from a hitCount of
    0, which means the search ran and matched nothing. Collapsing those two is how a
    broken probe comes to read as evidence of absence.
    """
    out = {}
    for item in queries:
        key, query = item[0], item[1]
        means = item[2] if len(item) > 2 else None
        print(f"[query] {key}", file=sys.stderr)
        data = search(query, page_size=page_size)
        res = (data.get("resultList") or {}).get("result", []) if data else []
        out[key] = {
            "query": query,
            "a_hit_would_mean": means,
            "hitCount": data.get("hitCount") if data else None,
            "retrieved": len(res),
            "hits": [hit_row(r) for r in res],
        }
        if not data:
            print(f"  ! {key}: API call failed (hitCount null, not zero)", file=sys.stderr)
        time.sleep(SLEEP)
    return out


def summarise(index: dict) -> dict:
    return {
        "n_queries": len(index),
        "n_with_hits": sum(1 for v in index.values() if (v["hitCount"] or 0) > 0),
        "n_zero": sum(1 for v in index.values() if v["hitCount"] == 0),
        "n_failed": sum(1 for v in index.values() if v["hitCount"] is None),
    }
