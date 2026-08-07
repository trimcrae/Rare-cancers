#!/usr/bin/env python3
"""Europe PMC probe for the metabolism / differentiation / dormancy / strategy sweep.

Pure stdlib. Runs a fixed list of queries against the Europe PMC REST search API and
writes structured hits (PMID, DOI, title, journal, year) plus the total hit count for
each query. The point is BOTH directions:

  * a hit count lets a real citation be quoted with a PMID rather than a remembered one;
  * a hit count of ZERO is the evidence behind an honest "nothing exists", which is
    otherwise indistinguishable from "I did not look".

The dev sandbox's egress proxy 403s www.ebi.ac.uk, pubmed.ncbi.nlm.nih.gov,
pmc.ncbi.nlm.nih.gov and api.openalex.org on CONNECT, so this runs on a GitHub runner
(CLAUDE.md section 6, escape hatch 1).

Output: research/literature/lane-probe-metabolism-strategy.json
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
OUT = pathlib.Path("research/literature/lane-probe-metabolism-strategy.json")

# (key, query). Keep queries quotable in the report verbatim.
QUERIES: list[tuple[str, str]] = [
    # --- (a) metabolism -------------------------------------------------
    ("emc_metabolism",
     '("extraskeletal myxoid chondrosarcoma") AND (metabolism OR metabolic OR glycolysis OR hypoxia)'),
    ("emc_hypoxia",
     '("extraskeletal myxoid chondrosarcoma") AND (hypoxia OR HIF1A OR "HIF-1" OR vascularity)'),
    ("nr4a3_metabolic_target",
     '(NR4A3 OR "NOR-1") AND (metabolism OR "metabolic reprogramming" OR glycolysis OR lipogenesis)'),
    ("gag_sulfation_cancer_target",
     '(PAPSS1 OR PAPSS2 OR UGDH OR UXS1 OR XYLT1 OR XYLT2 OR "PAPS synthase") AND (cancer OR tumour OR tumor) AND (target OR inhibitor OR dependency)'),
    ("gag_sulfation_sarcoma",
     '(PAPSS1 OR PAPSS2 OR UGDH OR UXS1 OR XYLT1 OR XYLT2 OR "chondroitin sulfate biosynthesis") AND (sarcoma OR chondrosarcoma OR "myxoid")'),
    ("proteoglycan_burden_myxoid",
     '("myxoid" OR "chondroid") AND ("proteoglycan synthesis" OR "glycosaminoglycan synthesis" OR "UDP-glucuronate" OR "UDP-sugar") AND (tumour OR tumor OR cancer OR sarcoma)'),
    ("ass1_sarcoma_arginine",
     '(ASS1 OR "argininosuccinate synthetase") AND (sarcoma OR chondrosarcoma) AND (arginine OR "ADI-PEG")'),
    ("ass1_chondrosarcoma",
     '("argininosuccinate synthetase" OR ASS1) AND chondrosarcoma'),
    ("mct_sarcoma",
     '(MCT1 OR MCT4 OR SLC16A1 OR SLC16A3 OR AZD3965) AND (sarcoma OR chondrosarcoma)'),
    ("chondrosarcoma_metabolism",
     'chondrosarcoma AND (glycolysis OR "metabolic vulnerability" OR "lactate" OR "IDH1" OR glutamine)'),
    ("hypoxia_prodrug_sarcoma",
     '(evofosfamide OR "TH-302" OR "hypoxia-activated prodrug") AND sarcoma'),

    # --- (b) differentiation -------------------------------------------
    ("differentiation_therapy_sarcoma_fusion",
     '("differentiation therapy" OR "terminal differentiation") AND sarcoma AND (fusion OR translocation)'),
    ("emc_differentiation",
     '("extraskeletal myxoid chondrosarcoma") AND (differentiation OR PPARG OR "PPAR gamma" OR chondrogenic)'),
    ("mlps_adipocytic_differentiation",
     '("myxoid liposarcoma") AND (adipocytic differentiation OR "differentiation therapy" OR pioglitazone OR rosiglitazone OR efatutazone)'),
    ("ne_lineage_switch_notch",
     '(NOTCH OR DLL3 OR ASCL1 OR INSM1) AND ("neuroendocrine" AND ("lineage plasticity" OR "lineage switch" OR "non-neuroendocrine"))'),
    ("emc_insm1_neuroendocrine",
     '("extraskeletal myxoid chondrosarcoma") AND (INSM1 OR neuroendocrine OR synaptophysin)'),

    # --- (c) dormancy / senescence / anti-metastatic --------------------
    ("nr2f1_dormancy",
     '(NR2F1 OR "COUP-TF1") AND (dormancy OR dormant) AND (metastasis OR "disseminated tumor cell")'),
    ("dormancy_sarcoma",
     '(dormancy OR "dormant tumor cell" OR "tumour dormancy") AND sarcoma'),
    ("antimetastatic_no_shrinkage_endpoint",
     '("anti-metastatic" OR "antimetastatic") AND ("clinical trial design" OR endpoint) AND NOT "tumor shrinkage"'),
    ("senescence_one_two_punch",
     '("one-two punch") AND (senescence OR senolytic) AND cancer'),
    ("senolytic_sarcoma",
     '(senolytic OR "therapy-induced senescence") AND sarcoma'),
    ("emc_lung_metastasis_history",
     '("extraskeletal myxoid chondrosarcoma") AND (metastasectomy OR "lung metastas*" OR "natural history" OR indolent)'),

    # --- (d) strategy ---------------------------------------------------
    ("adaptive_therapy_sarcoma",
     '("adaptive therapy" OR "evolutionary therapy") AND (sarcoma OR chondrosarcoma OR GIST)'),
    ("adaptive_therapy_general",
     '"adaptive therapy" AND (Gatenby OR "Lotka-Volterra" OR "dose modulation") AND cancer'),
    ("adaptive_therapy_tki",
     '"adaptive therapy" AND ("tyrosine kinase inhibitor" OR pazopanib OR sunitinib OR imatinib)'),
    ("math_onc_indolent",
     '("mathematical model" OR "digital twin") AND (indolent OR "slow-growing") AND (cancer OR tumour OR tumor) AND (schedule OR "drug holiday")'),
    ("ultrarare_trial_design",
     '("ultra-rare" OR "ultrarare") AND (cancer OR sarcoma) AND ("trial design" OR "n-of-1" OR Bayesian OR "single-arm")'),
    ("aspscar_atezolizumab",
     '("alveolar soft part sarcoma") AND atezolizumab'),
    ("emc_systemic_therapy",
     '("extraskeletal myxoid chondrosarcoma") AND (pazopanib OR sunitinib OR trabectedin OR anthracycline OR carfilzomib OR sorafenib)'),
    ("metronomic_sarcoma",
     '(metronomic OR "maintenance therapy") AND sarcoma AND (antiangiogenic OR "anti-angiogenic" OR cyclophosphamide)'),
    ("collateral_sensitivity_sarcoma",
     '("collateral sensitivity") AND (sarcoma OR "tyrosine kinase inhibitor")'),
]


def fetch(query: str, page_size: int = 25, retries: int = 4) -> dict:
    params = urllib.parse.urlencode({
        "query": query,
        "format": "json",
        "pageSize": str(page_size),
        "resultType": "core",
        "sort": "CITED desc",
    })
    url = f"{BASE}?{params}"
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-lane-probe/1.0"})
            with urllib.request.urlopen(req, timeout=90) as fh:
                return json.loads(fh.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - report, do not mask
            last = exc
            time.sleep(2 + 3 * attempt)
    return {"__error__": f"{type(last).__name__}: {last}"}


def slim(rec: dict) -> dict:
    return {
        "pmid": rec.get("pmid"),
        "pmcid": rec.get("pmcid"),
        "doi": rec.get("doi"),
        "title": (rec.get("title") or "").strip().rstrip("."),
        "journal": (rec.get("journalInfo") or {}).get("journal", {}).get("title")
        or rec.get("journalTitle"),
        "year": rec.get("pubYear"),
        "cited_by": rec.get("citedByCount"),
        "is_oa": rec.get("isOpenAccess"),
        "type": rec.get("pubType"),
    }


def main() -> int:
    only = os.environ.get("LANE_PROBE_ONLY", "").strip()
    queries = QUERIES
    if only:
        keys = {k.strip() for k in only.replace(",", " ").split() if k.strip()}
        queries = [(k, q) for k, q in QUERIES if k in keys]
        if not queries:
            print(f"no query matched LANE_PROBE_ONLY={only!r}", file=sys.stderr)
            return 2

    out: dict = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "Europe PMC REST search API",
        "note": (
            "Hit counts are Europe PMC's, on the query string recorded beside them. "
            "A zero is evidence of absence ONLY for that exact query - quote the query, "
            "never just the zero."
        ),
        "queries": {},
    }

    errors = 0
    for key, query in queries:
        data = fetch(query)
        if "__error__" in data:
            errors += 1
            out["queries"][key] = {"query": query, "error": data["__error__"]}
            print(f"[ERR ] {key}: {data['__error__']}", file=sys.stderr)
            continue
        results = (data.get("resultList") or {}).get("result", []) or []
        out["queries"][key] = {
            "query": query,
            "hit_count": data.get("hitCount"),
            "returned": len(results),
            "top": [slim(r) for r in results],
        }
        print(f"[ok  ] {key}: hitCount={data.get('hitCount')} returned={len(results)}")
        time.sleep(0.5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT} ({OUT.stat().st_size} bytes); {errors} query error(s)")

    # ⛔ THE FILE IS NOT THE DELIVERY CHANNEL, AND TWICE IT DELIVERED NOTHING (measured 2026-08-07).
    # Run 31134790934 lost the whole retrieval to a push race; run 31134956018 was refused
    # ("refusing to allow a GitHub App to create or update workflow ... without `workflows`
    # permission") because pushing a NEW ref carries the workflow file with it, and its artifact
    # then sat on blob.core.windows.net, which the dev sandbox's egress proxy 403s on CONNECT.
    # Three storage paths, three different failures, one cause: the reader could not reach any of
    # them. The JOB LOG is the one channel that is readable from here, so the digest goes there —
    # printed, not stored. Cheap, and it cannot be lost to a permission or a race.
    top_n = int(os.environ.get("LANE_PROBE_DIGEST_N", "4"))
    print("\n===BEGIN LANE-PROBE-DIGEST===")
    for key, q in queries:
        rec = out["queries"].get(key, {})
        if "error" in rec:
            print(f"## {key}\tERROR\t{rec['error']}")
            continue
        print(f"## {key}\thits={rec.get('hit_count')}\tq={q}")
        for r in (rec.get("top") or [])[:top_n]:
            print("   - PMID:{pmid} | {year} | {journal} | {title} | doi:{doi} | cited:{cited_by}".format(
                pmid=r.get("pmid") or "-", year=r.get("year") or "-",
                journal=(r.get("journal") or "-")[:38],
                title=(r.get("title") or "-")[:105],
                doi=r.get("doi") or "-", cited_by=r.get("cited_by")))
    print("===END LANE-PROBE-DIGEST===")
    return 1 if errors == len(queries) else 0


if __name__ == "__main__":
    raise SystemExit(main())
