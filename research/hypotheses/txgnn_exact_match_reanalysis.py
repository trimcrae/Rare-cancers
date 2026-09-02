#!/usr/bin/env python3
"""Re-derive the TxGNN comparison by EXACT drug-name matching. ($0, stdlib, no model)

WHY THIS EXISTS. `txgnn_predict.relevant_ranks` matched a queried agent to the model's ranked
output by SUBSTRING: `next((i, d) for i, d in enumerate(ranked, 1) if q in d["drug"].lower())`.
The list is sorted by descending score, so that returns the HIGHEST-SCORING compound whose name
CONTAINS the query, which is a different molecule whenever one exists. The committed artifacts
record the damage in their own `matched` fields: `doxorubicin` resolved to `13-deoxydoxorubicin`
and to `Zoptarelin doxorubicin`, `apatinib` to `Lapatinib`, `ifosfamide` to `Palifosfamide`.
The repository's other enumeration script guards against exactly this — `enumerate-drugs.mjs`'s
self-test asserts that "Lapatinib must NOT match apatinib" — so the fix was known in one place and
absent in the other.

WHAT THIS CAN AND CANNOT RECOVER. Only the top 100 ranked drugs (EMC) and the top 15 (each
comparison node) were ever committed, and no full 7,957-drug ranking exists on any branch. So the
TRUE rank of the three mis-resolved agents is NOT recoverable from what is committed: it needs a
re-run of the model, which needs the pretrained weights and the knowledge graph. This script
therefore reports the exactly-matched subset and leaves the three unresolved rather than
substituting a plausible number for a measured one.

WHY THE PUBLISHED MEDIANS WERE UPPER BOUNDS. If a queried agent is in the vocabulary at all, its
own name contains its own query string, so the substring match returns a compound scoring at least
as high as the agent itself. Every substring percentile is therefore an upper bound on the agent's
true percentile, and a median over them is an upper bound on the median over exact matches.

Usage:
  python3 research/hypotheses/txgnn_exact_match_reanalysis.py
  python3 research/hypotheses/txgnn_exact_match_reanalysis.py --check   # fail if the output drifts
"""
from __future__ import annotations

import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMPARISON = os.path.join(HERE, "txgnn-relatives-comparison.json")
PREDICTIONS = os.path.join(HERE, "txgnn-emc-predictions.json")
OUT = os.path.join(HERE, "txgnn-exact-match-reanalysis.json")


def _quartiles(values):
    q = statistics.quantiles(sorted(values), n=4, method="inclusive")
    return round(q[0], 1), round(q[2], 1)


def classify(rows):
    """Split the recorded query rows into exact matches, mis-resolved queries and absences."""
    exact, misresolved, absent = [], [], []
    for r in rows:
        matched = r.get("matched")
        if matched is None:
            absent.append({"query": r["query"]})
        elif str(matched).lower() == r["query"]:
            exact.append(r)
        else:
            misresolved.append({
                "query": r["query"], "returned_instead": matched,
                "rank_of_the_returned_compound": r.get("rank"),
                "percentile_of_the_returned_compound": r.get("percentile"),
                "true_rank_of_the_query": None,
            })
    return exact, misresolved, absent


def build():
    comp = json.load(open(COMPARISON, encoding="utf-8"))
    pred = json.load(open(PREDICTIONS, encoding="utf-8"))

    tops = {d["label"]: [x["drug"] for x in d["topDrugs"]] for d in comp["diseases"]}
    shared = sorted(set.intersection(*(set(v) for v in tops.values())))

    diseases = []
    for d in comp["diseases"]:
        exact, misresolved, absent = classify(d["relevantDrugRanks"])
        pct = [r["percentile"] for r in exact]
        lo, hi = _quartiles(pct)
        best = max(exact, key=lambda r: r["percentile"])
        diseases.append({
            "label": d["label"],
            "disease_node": d["disease"],
            "totalRanked": d["totalRanked"],
            "n_queried": len(d["relevantDrugRanks"]),
            "n_exact": len(exact),
            "median_percentile_exact": round(statistics.median(pct), 1),
            "iqr_percentile_exact": [lo, hi],
            "min_percentile_exact": round(min(pct), 1),
            "max_percentile_exact": round(max(pct), 1),
            "best_exactly_matched_agent": {
                "drug": best["matched"], "rank": best["rank"],
                "percentile": best["percentile"],
            },
            "named_agents": {
                r["query"]: {"rank": r["rank"], "percentile": r["percentile"]}
                for r in exact
                if r["query"] in ("pazopanib", "sunitinib", "imatinib", "trabectedin")
            },
            "misresolved_by_the_substring_matcher": misresolved,
            "absent_from_the_graph": [a["query"] for a in absent],
            "median_percentile_as_published_by_substring_matching":
                d["relevantMedianPercentile"],
            "top_ranked_compound": tops[d["label"]][0],
        })

    return {
        "_what": "Exact-name re-derivation of the TxGNN indication-ranking comparison, from the "
                 "two committed model artifacts. No model was re-run.",
        "_generated_by": "research/hypotheses/txgnn_exact_match_reanalysis.py",
        "_inputs": ["research/hypotheses/txgnn-relatives-comparison.json",
                    "research/hypotheses/txgnn-emc-predictions.json"],
        "_the_defect_this_corrects": "txgnn_predict.relevant_ranks matched by substring against a "
                                     "descending-sorted list, so it returned the highest-scoring "
                                     "compound whose name contained the query. Fixed in that file "
                                     "on 2026-08-10; the committed artifacts predate the fix and "
                                     "are re-read here rather than regenerated.",
        "⛔_what_cannot_be_recovered_here": "The true rank of doxorubicin, apatinib and ifosfamide "
                                           "at any of the three nodes. Only the top 100 (EMC) and "
                                           "top 15 (each node) of the 7,957-drug ranking were ever "
                                           "committed, so those three ranks require a re-run of "
                                           "the model. They are reported as unknown, never "
                                           "estimated.",
        "⚠_the_published_medians_were_upper_bounds": "A queried agent's own name contains its own "
                                                     "query string, so the substring match returns "
                                                     "a compound scoring at least as high as the "
                                                     "agent. Each substring percentile is an upper "
                                                     "bound on the true one.",
        "_no_clinical_claim": "A model's indication rank is not evidence of efficacy, safety or "
                              "clinical readiness for any agent in any disease.",
        "model": pred.get("model"),
        "relation": comp.get("relation"),
        "diseases": diseases,
        "top15_shared_by_all_three_nodes": shared,
        "n_top15_shared_by_all_three_nodes": len(shared),
    }


def main(argv):
    built = build()
    if "--check" in argv:
        if not os.path.exists(OUT):
            print(f"MISSING {OUT}")
            return 1
        on_disk = json.load(open(OUT, encoding="utf-8"))
        if on_disk != built:
            print(f"DRIFT: {OUT} does not match a fresh derivation")
            return 1
        print(f"OK {os.path.basename(OUT)} matches a fresh derivation")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(built, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    for d in built["diseases"]:
        print("%-22s n_exact=%d median=%.1f (IQR %.1f-%.1f) best=%s %.1f" % (
            d["label"], d["n_exact"], d["median_percentile_exact"],
            d["iqr_percentile_exact"][0], d["iqr_percentile_exact"][1],
            d["best_exactly_matched_agent"]["drug"],
            d["best_exactly_matched_agent"]["percentile"]))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
