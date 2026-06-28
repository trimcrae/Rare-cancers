#!/usr/bin/env python3
"""
MM-GBSA endpoint RESCORING of the NR4A selectivity matrix (the cheap quantitative tier before FEP).

Reuses the matrix job's own outputs (mounted at INPUT_DIR = s3://<bucket>/nr4a3-matrix) — the three
opened-conformer receptors `<tag>-opened.pdb` and the docked pose sets `docked_<tag>.sdf` — and re-scores
every candidate's pose in each paralogue with a single-snapshot, 1-trajectory MM-GBSA endpoint energy
(`mmgbsa_energy.endpoint_dG`: enthalpy + GBn2 implicit solvent, NO entropy, NO ensemble average). NO
re-docking and NO MD, so it is CPU work on ~13 candidates × 3 targets — minutes, not a multi-hour GPU run.

Deliverable (`nr4a3-mmgbsa.json`): per candidate, the MM-GBSA ΔG into NR4A3/NR4A1/NR4A2, the recomputed
NR4A3-selectivity margins, and a `verdict` (`mmgbsa_select.verdict`) comparing the MM-GBSA selectivity to
the docking selectivity — i.e. did the docking-level NR4A3 preference SURVIVE a physics-based energy model?
This directly tests the matrix's central caveat (every selectivity call was within docking noise, and the
top hit cytosporone B is a known NR4A1 agonist). It is STILL triage, not affinity — that is the FEP tier.
"""
import json
import os
import sys
import traceback

import mmgbsa_select as ms

PARALOGUES = ["nr4a3", "nr4a1", "nr4a2"]
KEY = {"nr4a3": "NR4A3", "nr4a1": "NR4A1", "nr4a2": "NR4A2"}

IN = os.environ.get("INPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUTPUT_DIR", IN)
MINIMIZE_ITERS = int(os.environ.get("MMGBSA_MIN_ITERS", "250"))


def _docking_margins(matrix_json):
    """Pull each candidate's docking min-margin (min of margin_vs_NR4A1/2) + cell from the matrix JSON,
    so the MM-GBSA verdict can be compared to what docking said. Returns {label: {dock_min_margin, cell}}."""
    out = {}
    if not os.path.exists(matrix_json):
        return out
    with open(matrix_json) as fh:
        mtx = json.load(fh)
    for r in mtx.get("candidates", []):
        m1, m2 = r.get("margin_vs_NR4A1"), r.get("margin_vs_NR4A2")
        present = [m for m in (m1, m2) if m is not None]
        out[r["label"]] = {"dock_min_margin": (min(present) if present else None),
                           "dock_cell": r.get("cell"), "chembl_id": r.get("chembl_id")}
    return out


def main():
    import mmgbsa_energy as mme
    res = {"_note": "MM-GBSA endpoint RESCORING of the matrix docked poses (single-snapshot, "
                    "1-trajectory, enthalpy + GBn2; NO entropy, NO ensemble average). Tests whether the "
                    "docking-level NR4A3-selectivity survives a physics-based energy model. STILL triage, "
                    "NOT an affinity — that is the FEP tier.",
           "method": {"model": "amber14/ff14SB + GBn2 implicit; ligand gaff-2.11/AM1-BCC",
                      "scheme": "1-trajectory single-snapshot; minimize complex then slice components",
                      "minimize_iters": MINIMIZE_ITERS, "entropy": "omitted", "ensemble": "single snapshot"},
           "paralogues": {}, "candidates": []}
    os.makedirs(OUT, exist_ok=True)

    dock = _docking_margins(os.path.join(IN, "nr4a3-matrix.json"))

    # 1) prepare each receptor once; load each target's pose set once.
    receptors, poses = {}, {}
    for tag in PARALOGUES:
        rec_pdb = os.path.join(IN, f"{tag}-opened.pdb")
        pose_sdf = os.path.join(IN, f"docked_{tag}.sdf")
        if not (os.path.exists(rec_pdb) and os.path.exists(pose_sdf)):
            res.setdefault("_warnings", []).append(f"{KEY[tag]} skipped: missing {rec_pdb} or {pose_sdf}")
            continue
        try:
            receptors[tag] = mme.prepare_receptor(rec_pdb)
            poses[tag] = mme.load_poses(pose_sdf)
            res["paralogues"][KEY[tag]] = {"n_poses": len(poses[tag])}
        except Exception as e:  # noqa: BLE001
            res.setdefault("_warnings", []).append(f"{KEY[tag]} receptor/pose load failed: {e}")

    if "nr4a3" not in poses:
        res["_status"] = "NR4A3 receptor/poses unavailable — cannot rescore"
        _write(res); print(json.dumps({k: res[k] for k in ('_status', '_warnings') if k in res})); return

    # 2) the candidate set = the labels docked into NR4A3 (rescoring follows the matrix library).
    labels = list(poses["nr4a3"].keys())
    cache = os.path.join(OUT, "sysgen_cache.json")
    rows = []
    for label in labels:
        dg = {}
        errs = {}
        for tag in PARALOGUES:
            if tag not in poses or label not in poses[tag]:
                dg[tag] = None
                continue
            try:
                rec_top, rec_pos = receptors[tag]
                r = mme.endpoint_dG(rec_top, rec_pos, poses[tag][label],
                                    minimize_iters=MINIMIZE_ITERS, cache=cache)
                dg[tag] = r["dG"]
            except Exception as e:  # noqa: BLE001 — record + continue; one bad ligand never voids the run
                dg[tag] = None
                errs[KEY[tag]] = str(e)[:160]
        mar = ms.margins(dg["nr4a3"], dg["nr4a1"], dg["nr4a2"])
        d = dock.get(label, {})
        v = ms.verdict(d.get("dock_min_margin"), mar["min_margin"])
        row = {"label": label, "chembl_id": d.get("chembl_id"),
               "dG_mmgbsa": {KEY[t]: dg[t] for t in PARALOGUES},
               "mm_margin_vs_NR4A1": mar["margin_vs_NR4A1"], "mm_margin_vs_NR4A2": mar["margin_vs_NR4A2"],
               "mm_min_margin": mar["min_margin"],
               "dock_min_margin": d.get("dock_min_margin"), "dock_cell": d.get("dock_cell"),
               "verdict": v}
        if errs:
            row["_errors"] = errs
        rows.append(row)
        print(f"  {label[:24]:<24} mmΔG3={dg['nr4a3']} mmMargin={mar['min_margin']} "
              f"dockMargin={d.get('dock_min_margin')} -> {v}", flush=True)

    rows = ms.rank_rows(rows)
    res["candidates"] = rows
    res["verdict_census"] = ms.census(rows)
    res["leads_confirmed_selective"] = [r["label"] for r in rows if r["verdict"] == "confirmed_selective"]
    res["leads_reversed"] = [r["label"] for r in rows if r["verdict"] == "reversed"]
    res["_status"] = "ok"
    _write(res)
    print(json.dumps({"verdict_census": res["verdict_census"],
                      "confirmed_selective": res["leads_confirmed_selective"],
                      "reversed": res["leads_reversed"]}, indent=2), flush=True)


def _write(res):
    with open(os.path.join(OUT, "nr4a3-mmgbsa.json"), "w") as fh:
        json.dump(res, fh, indent=2)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — always leave a diagnostic
        json.dump({"_status": "error", "error": str(exc), "trace": traceback.format_exc()[-1800:]},
                  open(os.path.join(OUT, "nr4a3-mmgbsa.json"), "w"), indent=2)
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
