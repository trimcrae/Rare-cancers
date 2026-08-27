#!/usr/bin/env python3
"""Fold retrieval and figure-reading into ONE admit-or-refuse record per EMC survival series.

WHAT THIS ANSWERS
-----------------
Ledger item AUT-034: *digitize the Kaplan-Meier curve and numbers-at-risk table of the largest
open-access EMC series, and admit or refuse the result against the quality floor.* Answering it
needs three facts about each series that live in three different places, and the failure this file
exists to prevent is reading one of them as another:

  * how big it is, and what identifiers it has -- `research/data/emc-clinical-registry.json`;
  * whether this program can GET it at $0 -- the km-figures retrieval rounds;
  * whether its figures PRINT a numbers-at-risk row -- `research/modalities/km-risk-row-detection.json`.

⛔ REACHABILITY IS NOT ADMISSIBILITY AND NEITHER IS A STATEMENT ABOUT THE SCIENCE. A series this
program cannot fetch may print a perfect risk table; a series it can fetch may print none. The
verdict per row is therefore one of:

    admitted            the figures were read and at least one prints a numbers-at-risk row
    refused_no_risk_row the figures were read and none prints one -- POLICY-evidence.md §2.7(a)
    unreadable          retrieved, but no figure could be read (an encoding, not a finding)
    unreachable         no free route today; the figure question is UNASKED, not answered

⛔ AND `admitted` IS NOT `pooled`. §2.1 and §2.3 still decide what may be combined with what, and
this file records the overlap risk beside each row rather than resolving it.

Every count in the output is computed here. Nothing in it is typed.
"""

from __future__ import annotations

import argparse
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(REPO, "research", "data", "emc-clinical-registry.json")
DETECTION = os.path.join(REPO, "research", "modalities", "km-risk-row-detection.json")

# Series this program treats as candidate survival sources. The set, and WHY each row is a
# candidate, is owned by research/modalities/emc_ipd_survival.py:CANDIDATE_SOURCES; only the
# identifiers are read from the registry, never typed.
CANDIDATES = [
    "seer270_2022", "masunaga2025", "meisKindblom1999", "drilon2008", "ussc2022", "chiusole2020",
    "uMich2023", "japan2003", "china2016", "huang2023", "bishop2019", "stacchiotti2019pazopanib",
    "martinbroto2020immunosarc1", "stacchiotti2013anthracycline", "stacchiotti2014sunitinib",
    "morioka2016trabectedin",
]

KM_CAPTION_HINT = ("kaplan", "survival", "progression", "recurrence")


def registry() -> dict:
    with open(REGISTRY, encoding="utf-8") as fh:
        return json.load(fh)["registry"]["citations"]


def retrieval_state(manifests: list[dict]) -> dict:
    """The LATEST outcome per source across the rounds given, with every route it tried."""
    out: dict[str, dict] = {}
    for man in manifests:
        for tgt in man.get("targets", []):
            sid = tgt.get("source_id")
            if not sid:
                continue
            out[sid] = {
                "round": man.get("_round"),
                "route_used": tgt.get("route_used"),
                "routes": [{k: r.get(k) for k in ("route", "http", "bytes", "content_type")}
                           | ({"interstitial": r["interstitial"]} if r.get("interstitial") else {})
                           | ({"browser_http": (r.get("browser_retry") or {}).get("http")}
                              if r.get("browser_retry") else {})
                           for r in tgt.get("routes", [])],
                "unpaywall": {k: (tgt.get("unpaywall") or {}).get(k)
                              for k in ("is_oa", "oa_status", "n_oa_locations")},
                "oa_locations": [loc for loc in
                                 ((tgt.get("unpaywall") or {}).get("oa_locations") or [])],
                "openalex_locations": (tgt.get("openalex") or {}).get("locations") or [],
            }
    return out


def figure_state(detection: dict) -> dict:
    """Per source: the verdicts of the figures whose captions name a survival endpoint."""
    out: dict[str, dict] = {}
    for src in detection.get("sources", []):
        km = [f for f in src.get("figures", [])
              if any(h in (f.get("caption_head") or "").lower() for h in KM_CAPTION_HINT)]
        out[src["source_id"]] = {
            "pdf_sha256": src["pdf_sha256"],
            "km_figures_read": len(km),
            "present": sum(1 for f in km if f["verdict"] == "present"),
            "absent": sum(1 for f in km if f["verdict"] == "absent"),
            "undetermined": sum(1 for f in km if f["verdict"] == "undetermined"),
            "figures": [{"page": f["page"], "caption": f["caption_head"], "arm": f["arm"],
                         "source": f.get("source", "embedded"), "verdict": f["verdict"]}
                        for f in km],
        }
    return out


def verdict_for(fig: dict | None, ret: dict | None) -> tuple[str, str]:
    if fig and fig["km_figures_read"]:
        if fig["present"]:
            return "admitted", ("at least one survival figure prints a numbers-at-risk row; "
                                "admissible under POLICY-evidence.md §2.7(a), which is a statement "
                                "about REPORTING and not about the cohort")
        if fig["absent"]:
            return "refused_no_risk_row", ("every survival figure read prints NO numbers-at-risk "
                                           "row, so the per-interval censored count is "
                                           "unidentifiable: §2.7(a) refuses it rather than "
                                           "admitting it with a caveat")
        return "unreadable", "figures were found but none could be read"
    if ret and ret.get("route_used"):
        return "unreadable", ("the article was retrieved and no survival figure could be read from "
                              "it; an encoding or layout limit, never a finding about the paper")
    return "unreachable", ("no free route returned the article today, so its figures have not been "
                           "LOOKED at: the risk-row question is unasked, not answered no")


def build(manifests: list[dict], detection: dict) -> dict:
    cits = registry()
    ret = retrieval_state(manifests)
    figs = figure_state(detection)
    rows = []
    for sid in CANDIDATES:
        cit = cits.get(sid, {})
        v, why = verdict_for(figs.get(sid), ret.get(sid))
        rows.append({
            "source_id": sid,
            "n": cit.get("n"),
            "identifiers": {k: cit.get(k) for k in ("pmid", "pmcid", "doi") if cit.get(k)},
            "study_period": cit.get("studyPeriod"),
            "verdict": v,
            "why": why,
            "figures": (figs.get(sid) or {}).get("figures"),
            "pdf_sha256": (figs.get(sid) or {}).get("pdf_sha256"),
            "retrieval": ret.get(sid),
        })
    rows.sort(key=lambda r: -(r["n"] or 0))
    by_verdict: dict[str, list[str]] = {}
    for r in rows:
        by_verdict.setdefault(r["verdict"], []).append(r["source_id"])
    read = [r for r in rows if r["verdict"] in ("admitted", "refused_no_risk_row")]
    return {
        "_what": "Admit or refuse, per candidate EMC survival series, against the numbers-at-risk "
                 "condition POLICY-evidence.md §2.7(a) makes mandatory.",
        "_generated_by": "scripts/emc_km_admissibility.py",
        "_not_medical_advice": "Nothing here is medical advice, and nothing here asserts efficacy, "
                               "safety or clinical readiness.",
        "⛔_a_refusal_is_about_reporting": "Every `refused_no_risk_row` row is a statement about "
            "what a journal printed beneath an axis. It is not a criticism of the study, it does "
            "not bear on the study's conclusions, and it says nothing about the patients in it.",
        "⛔_a_figure_that_is_not_a_kaplan_meier_curve_is_refused_here_by_construction": "The rule "
            "reads figures whose caption names a survival endpoint. martinbroto2020's Figure 3 is a "
            "SWIMMER PLOT captioned 'Progression-free survival ...': it prints no numbers-at-risk "
            "row because it needs none, and it is read by a different instrument entirely "
            "(research/modalities/km-swimmer-readings.json). A refusal here is a refusal to invert "
            "that figure with Guyot's algorithm, never a claim that it carries nothing.",
        "⛔_the_patient_totals_are_series_denominators_not_emc_patients": "A denominator is the "
            "whole arm the figure describes. morioka2016's admitted curve covers a five-patient "
            "trabectedin arm of which the paper's Table 2 identifies two as EMC, so summing "
            "denominators overstates the EMC patients available. Composition is recorded per row in "
            "research/modalities/emc_ipd_survival.py:CANDIDATE_SOURCES.",
        "⛔_admitted_is_not_pooled": "§2.1 and §2.3 decide what may be combined; an admitted curve "
            "still has to clear non-overlap, and the overlap risks are recorded in "
            "research/modalities/emc_ipd_survival.py:CANDIDATE_SOURCES.",
        "reads_from": {
            "registry": "research/data/emc-clinical-registry.json",
            "figure_readings": "research/modalities/km-risk-row-detection.json",
            "retrieval_rounds": [{"slug": m.get("_round"),
                                  "path_in_literature_cache": m.get("_cache_path"),
                                  "cache_commit": m.get("_cache_commit"),
                                  "actions_run_id": m.get("_run_id")} for m in manifests],
        },
        "totals": {
            "candidates": len(rows),
            "figures_read_whose_caption_names_a_survival_endpoint":
                sum((figs.get(r["source_id"]) or {}).get("km_figures_read", 0) for r in rows),
            "patients_in_series_whose_figures_were_read": sum(r["n"] or 0 for r in read),
            "patients_in_admitted_series": sum(r["n"] or 0 for r in rows
                                               if r["verdict"] == "admitted"),
            "by_verdict": {k: len(v) for k, v in sorted(by_verdict.items())},
        },
        "by_verdict": by_verdict,
        "series": rows,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--round", action="append", default=[], metavar="SLUG=PATH",
                    help="a km-figures round manifest, as slug=path")
    ap.add_argument("--cache-commit", default=None,
                    help="commit of origin/literature-cache the round manifests were read from")
    ap.add_argument("--run-id", action="append", default=[], metavar="SLUG=RUNID",
                    help="the Actions run that produced a round, as slug=run_id")
    ap.add_argument("--detection", default=DETECTION)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    run_ids = dict(spec.partition("=")[::2] for spec in args.run_id)
    manifests = []
    for spec in args.round:
        slug, _, path = spec.partition("=")
        with open(path, encoding="utf-8") as fh:
            man = json.load(fh)
        man["_round"] = slug
        man["_cache_path"] = f"literature/{slug}/_km_figure_manifest.json"
        man["_cache_commit"] = args.cache_commit
        man["_run_id"] = run_ids.get(slug)
        manifests.append(man)
    with open(args.detection, encoding="utf-8") as fh:
        detection = json.load(fh)
    doc = build(manifests, detection)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps(doc["totals"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
