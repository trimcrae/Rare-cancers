#!/usr/bin/env python3
"""
Consolidate the HARMONIZED, score-independent orthosteric-pocket detection across EVERY load-bearing
NR4A3 ensemble into ONE table (reviewer P0 deliverable).

The heavy per-ensemble re-scoring is done by the EXISTING scorers run with POCKET_MATCH=harmonized and
fpocket pinned (sagemaker_src/entry_pocket_reharmonize.py orchestrates them as subprocesses). This module
holds only the PURE aggregation: pull each ensemble's `harmonized_detection` (both-denominator) block out
of its result JSON — whatever shape that scorer uses — and fold them into a single consolidated table via
pocket_tracking.consolidated_table. Pure + unit-tested (tests/test_pocket_reharmonize.py).

Consolidated columns (per ensemble): total frames propagated, matched detected, detection fraction,
fraction >= D* among DETECTED, fraction >= D* among ALL propagated.
"""
import json
import os

import pocket_tracking as pt


def detection_from_result(kind, result):
    """Extract the both-denominator detection dict from one scorer's result JSON, keyed by `kind`.
    Returns a detection_report()-shaped dict, or None if absent. Pure (takes the parsed JSON)."""
    if result is None:
        return None
    if kind == "af2_static":
        return (result.get("harmonized_orthosteric_match") or {}).get("detection")
    if kind == "8xtt":
        h = result.get("harmonized_detection") or {}
        # strip the non-numeric annotation keys, keep the detection fields
        return {k: h.get(k) for k in ("d_star", "n_propagated", "n_detected", "n_ge_dstar",
                                      "detection_fraction", "frac_ge_among_detected",
                                      "frac_ge_among_propagated")} if h else None
    if kind in ("metad", "release_rep"):
        dts = result.get("druggability_timeseries") or {}
        h = dts.get("harmonized_detection") or {}
        return {k: h.get(k) for k in ("d_star", "n_propagated", "n_detected", "n_ge_dstar",
                                      "detection_fraction", "frac_ge_among_detected",
                                      "frac_ge_among_propagated")} if h else None
    if kind == "release_druggable":
        return result.get("harmonized_detection")
    if kind == "calibration_nr4a3":
        # calibration reports a single-structure match (no distribution); synthesize a 1-frame detection.
        for r in result.get("results", []):
            if r.get("id") == "NR4A3_AF2_Q92570":
                m = r.get("harmonized_pocket5_match") or {}
                drug = m.get("matched_druggability")
                scores = [drug] if drug is not None else []
                return pt.detection_report(scores, d_star=pt.D_STAR, n_propagated=1)
        return None
    return None


def pool_detection(detections, d_star=pt.D_STAR):
    """Pool several detection dicts (e.g. the 3 release replicas) into one by summing counts. The
    fractions are recomputed from the pooled counts, NOT averaged. Pure."""
    ds = [d for d in detections if d]
    if not ds:
        return None
    n_prop = sum(d.get("n_propagated") or 0 for d in ds)
    n_det = sum(d.get("n_detected") or 0 for d in ds)
    n_ge = sum(d.get("n_ge_dstar") or 0 for d in ds)
    return {
        "d_star": d_star,
        "n_propagated": n_prop,
        "n_detected": n_det,
        "n_ge_dstar": n_ge,
        "detection_fraction": (n_det / n_prop) if n_prop else None,
        "frac_ge_among_detected": (n_ge / n_det) if n_det else None,
        "frac_ge_among_propagated": (n_ge / n_prop) if n_prop else None,
    }


def build_consolidated(entries, fpocket_version=None):
    """`entries`: ordered list of {"ensemble": name, "kind": kind, "result": parsed_json | None}.
    Returns the consolidated table dict (columns + rows) plus metadata. Pure."""
    ensembles = []
    for e in entries:
        det = detection_from_result(e["kind"], e.get("result"))
        ensembles.append({"ensemble": e["ensemble"], "detection": det or {}})
    table = pt.consolidated_table(ensembles)
    return {
        "_title": "NR4A3 harmonized orthosteric-pocket detection — consolidated across all ensembles",
        "_method": ("Orthosteric Pocket-5 defined by the FIXED lining residue set (score-independent), "
                    "matched per frame by the composite Jaccard/recovery + centroid gate; BOTH "
                    "denominators reported. One homogeneous, pinned fpocket build."),
        "fpocket_version": fpocket_version,
        "match_params": pt.match_params(),
        "d_star": pt.D_STAR,
        **table,
    }


# ---- thin I/O wrapper used by the entry point (not unit-tested) -----------------------------------

def load_and_build(spec, out_path):
    """`spec`: list of (ensemble_name, kind, json_path). Loads each JSON (missing -> None) and writes
    the consolidated table to `out_path`. Returns the table dict."""
    entries = []
    for name, kind, path in spec:
        result = None
        if path and os.path.exists(path):
            try:
                with open(path) as fh:
                    result = json.load(fh)
            except Exception as ex:  # noqa: BLE001
                print(f"  [reharmonize] could not read {path}: {ex}", flush=True)
        else:
            print(f"  [reharmonize] missing {kind} result {path}", flush=True)
        entries.append({"ensemble": name, "kind": kind, "result": result})
    table = build_consolidated(entries, fpocket_version=pt.resolved_fpocket_version())
    with open(out_path, "w") as fh:
        json.dump(table, fh, indent=2)
    print(f"  [reharmonize] wrote {out_path}", flush=True)
    for row in table["rows"]:
        print(f"    {row['ensemble']:>22}: n={row['n_propagated']} det={row['n_detected']} "
              f"detfrac={row['detection_fraction']} ge_det={row['frac_ge_among_detected']} "
              f"ge_all={row['frac_ge_among_propagated']}", flush=True)
    return table
