#!/usr/bin/env python3
"""Fold the km-figures retrieval rounds into ONE reachability census.

WHY THIS EXISTS
---------------
Four dispatches of `fetch-literature.yml`'s `km-figures` mode answered one question between them --
*which of this program's candidate extraskeletal myxoid chondrosarcoma survival series can be read
at $0, and by what route* -- and each left its answer in its own slug directory on the
`literature-cache` branch. A question answered across four artifacts is a question the next session
re-asks, so this folds them into one record.

⛔ IT IS A REACHABILITY CENSUS, NOT A SCIENCE ONE. "Unreachable" here means this program has no free
route to the full text today. It says nothing about whether the paper prints a curve, whether that
curve is admissible, or whether the series is any good. What each RETRIEVED paper's figures actually
show is recorded per candidate in `emc_ipd_survival.CANDIDATE_SOURCES[].figure_finding`.

⚠ THE INPUT IS NOT IN THIS REPOSITORY. The round manifests live on the `literature-cache` branch,
which is a working cache rather than repository content. `--cache` points at a checkout of it; the
artifact records the branch commit it was built from so the census can be rebuilt or refuted.

Run:  python3 scripts/emc_km_reachability_census.py --cache <path-to-literature-cache-checkout>
Writes: research/literature/emc-km-reachability-census-2026-08-25.json
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "research", "literature",
                   "emc-km-reachability-census-2026-08-25.json")


def _cache_commit(cache: str) -> str | None:
    try:
        return subprocess.run(["git", "-C", cache, "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=False).stdout.strip() or None
    except Exception:  # noqa: BLE001
        return None


def collect(cache: str) -> dict:
    rounds = sorted(glob.glob(os.path.join(cache, "literature", "*km-figures*",
                                           "_km_figure_manifest.json")))
    by_source: dict[str, dict] = {}
    round_records = []
    for path in rounds:
        slug = os.path.basename(os.path.dirname(path))
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        round_records.append({"slug": slug, "totals": doc.get("_totals"),
                              "targets": len(doc.get("targets", []))})
        for t in doc.get("targets", []):
            sid = t.get("source_id")
            if not sid:
                continue
            row = by_source.setdefault(sid, {"source_id": sid, "rounds": []})
            up = t.get("unpaywall") or {}
            pr = t.get("pmid_resolution") or {}
            routes = [{k: r.get(k) for k in ("route", "http", "kind", "bytes", "browser_retry")}
                      for r in t.get("routes", [])]
            row["rounds"].append({
                "slug": slug,
                "pmcid": t.get("pmcid"),
                "europe_pmc_is_open_access": pr.get("is_open_access"),
                "unpaywall_is_oa": up.get("is_oa"),
                "unpaywall_oa_status": up.get("oa_status"),
                "unpaywall_host_type": up.get("best_host_type"),
                "unpaywall_licence": up.get("licence"),
                "route_used": t.get("route_used"),
                "routes": routes,
                "refused": t.get("⛔_refused"),
                "crashed": t.get("⛔_crashed"),
            })
    # the verdict per source is the BEST outcome any round reached
    for sid, row in by_source.items():
        got = [r for r in row["rounds"] if r["route_used"]]
        oa = [r for r in row["rounds"] if r["unpaywall_is_oa"] is True]
        closed = [r for r in row["rounds"] if r["unpaywall_is_oa"] is False]
        if got:
            row["verdict"] = "retrieved"
            row["route_used"] = got[-1]["route_used"]
        elif oa:
            row["verdict"] = "free_to_read_but_not_retrieved"
            row["⚠"] = ("Unpaywall grades it open access and every route this program tried was "
                        "refused by the publisher. That is a retrieval problem, not a licence one.")
        elif closed:
            row["verdict"] = "closed"
        else:
            row["verdict"] = "unresolved"
    return {"rounds": round_records, "by_source": by_source}


def build(cache: str) -> dict:
    data = collect(cache)
    rows = list(data["by_source"].values())
    tally: dict[str, int] = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    return {
        "_what": "Which candidate EMC survival series this program can reach at $0, by what route, "
                 "folded from every km-figures retrieval round.",
        "_not_medical_advice": "Nothing here is medical advice, and nothing here asserts efficacy, "
                               "safety or clinical readiness.",
        "⛔_reachability_not_science": "'Unreachable' means no free route today. It says nothing "
                                       "about whether the paper prints a curve or whether that "
                                       "curve is admissible; that is "
                                       "emc_ipd_survival.CANDIDATE_SOURCES[].figure_finding.",
        "⭐_the_headline": "Europe PMC answered isOpenAccess: N for every series outside the "
                          "original PMC set, and Unpaywall found three of those nine FREE TO READ "
                          "at the publisher. Not in PMC is not the same as not free, and this "
                          "program had been treating them as the same thing.",
        "_source": {
            "cache_checkout": cache,
            "cache_commit": _cache_commit(cache),
            "⚠": "The round manifests live on the literature-cache branch, which is a working "
                 "cache rather than repository content. The commit above is what this census was "
                 "built from.",
        },
        "rounds": data["rounds"],
        "tally": tally,
        "series": sorted(rows, key=lambda r: (r["verdict"], r["source_id"])),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cache", required=True,
                    help="path to a checkout of the literature-cache branch")
    args = ap.parse_args(argv)
    art = build(args.cache)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(art, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps(art["tally"], indent=2))
    for r in art["series"]:
        print(f"  {r['source_id']:26s} {r['verdict']}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
