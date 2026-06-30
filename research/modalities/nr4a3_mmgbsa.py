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
import signal
import sys
import threading
import time
import traceback

import mmgbsa_select as ms

PARALOGUES = ["nr4a3", "nr4a1", "nr4a2"]
KEY = {"nr4a3": "NR4A3", "nr4a1": "NR4A1", "nr4a2": "NR4A2"}

IN = os.environ.get("INPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUTPUT_DIR", IN)
MINIMIZE_ITERS = int(os.environ.get("MMGBSA_MIN_ITERS", "250"))
# Multi-snapshot (de-noising) tier: short GB MD + ensemble-averaged ΔG with an SD (red-team confirmation of
# denovo_393). MULTISNAPSHOT=1 switches endpoint_dG -> endpoint_dG_multisnapshot.
MULTISNAPSHOT = os.environ.get("MULTISNAPSHOT") == "1"
MS_FRAMES = int(os.environ.get("MMGBSA_FRAMES", "10"))
MS_INTERVAL_PS = float(os.environ.get("MMGBSA_FRAME_PS", "10"))
MS_EQUIL_PS = float(os.environ.get("MMGBSA_EQUIL_PS", "20"))
# Optional comma-separated label whitelist (e.g. "denovo_393,denovo_401") — only score these candidates.
# Multi-snapshot is expensive, so confirmation runs a small set, not all 60.
CANDIDATE_FILTER = [s.strip() for s in os.environ.get("CANDIDATE_FILTER", "").split(",") if s.strip()]
# Per-(ligand,target) wall-clock cap. One endpoint_dG that hangs (e.g. a pathological minimise) must not
# stall the whole run silently — SIGALRM turns it into a normal per-leg failure recorded in _errors.
TARGET_TIMEOUT = int(os.environ.get("MMGBSA_TARGET_TIMEOUT", "600"))


class _LegTimeout(Exception):
    """Raised by the SIGALRM handler when one endpoint_dG leg exceeds TARGET_TIMEOUT."""


def _on_alarm(_sig, _frame):
    raise _LegTimeout(f"endpoint_dG exceeded {TARGET_TIMEOUT}s")


# Shared progress state for the heartbeat thread (so even a long single leg shows liveness in CloudWatch).
_progress = {"done": 0, "n": 0, "current": "(starting)"}


def _heartbeat(stop, start, every=60):
    while not stop.wait(every):
        print(f"[hb] mmgbsa: {_progress['done']}/{_progress['n']} ligands done, "
              f"on {_progress['current']}, {int(time.time() - start)}s elapsed", flush=True)


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
                      "scheme": ("1-trajectory MULTI-snapshot; minimize + short GB Langevin MD, ΔG averaged "
                                 f"over {MS_FRAMES} frames @ {MS_INTERVAL_PS} ps (equil {MS_EQUIL_PS} ps)")
                                if MULTISNAPSHOT else
                                "1-trajectory single-snapshot; minimize complex then slice components",
                      "minimize_iters": MINIMIZE_ITERS, "entropy": "omitted",
                      "ensemble": (f"{MS_FRAMES}-frame MD average" if MULTISNAPSHOT else "single snapshot")},
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

    # 2) the candidate set = the labels docked into NR4A3 (rescoring follows the matrix library), optionally
    #    restricted to a whitelist (multi-snapshot confirmation scores a small set, not all candidates).
    labels = list(poses["nr4a3"].keys())
    if CANDIDATE_FILTER:
        labels = [lbl for lbl in labels if lbl in CANDIDATE_FILTER]
        missing = [lbl for lbl in CANDIDATE_FILTER if lbl not in poses["nr4a3"]]
        if missing:
            res.setdefault("_warnings", []).append(f"CANDIDATE_FILTER labels not in NR4A3 poses: {missing}")
        print(f"[mmgbsa] CANDIDATE_FILTER -> scoring {len(labels)} of "
              f"{len(poses['nr4a3'])}: {labels}", flush=True)
    cache = os.path.join(OUT, "sysgen_cache.json")
    rows = []

    # Select + print the OpenMM platform UP FRONT, and FAIL FAST if no GPU platform loads. There is no CPU
    # fallback (run 8: ~48 min/ligand on CPU), so this raises within seconds on a GPU-less/ICD-broken box —
    # the job dies immediately with a clear message instead of grinding to the timeout. (Outer __main__
    # handler writes the error JSON + exits 1.)
    omm, _app, ommunit, *_ = mme._mm()
    mme._platform(omm, ommunit)

    _progress["n"] = len(labels)
    res["_status"], res["_progress"] = "in_progress", f"0/{len(labels)}"
    _write(res)                                          # checkpoint before the first (slow) leg
    print(f"[mmgbsa] rescoring {len(labels)} candidates x {len(receptors)} targets "
          f"(min_iters={MINIMIZE_ITERS}, per-leg timeout={TARGET_TIMEOUT}s)", flush=True)
    signal.signal(signal.SIGALRM, _on_alarm)
    stop = threading.Event()
    threading.Thread(target=_heartbeat, args=(stop, time.time()), daemon=True).start()

    for i, label in enumerate(labels, 1):
        _progress["current"] = label[:32]
        t0 = time.time()
        dg = {}
        dg_sd = {}
        errs = {}
        for tag in PARALOGUES:
            if tag not in poses or label not in poses[tag]:
                dg[tag] = None
                continue
            signal.alarm(TARGET_TIMEOUT)
            try:
                rec_top, rec_pos = receptors[tag]
                if MULTISNAPSHOT:
                    r = mme.endpoint_dG_multisnapshot(
                        rec_top, rec_pos, poses[tag][label], n_frames=MS_FRAMES,
                        frame_interval_ps=MS_INTERVAL_PS, equil_ps=MS_EQUIL_PS,
                        minimize_iters=MINIMIZE_ITERS, cache=cache)
                    dg[tag] = r["dG"]
                    dg_sd[tag] = r.get("dG_sd")
                else:
                    r = mme.endpoint_dG(rec_top, rec_pos, poses[tag][label],
                                        minimize_iters=MINIMIZE_ITERS, cache=cache)
                    dg[tag] = r["dG"]
            except Exception as e:  # noqa: BLE001 — record + continue; one bad leg never voids the run
                dg[tag] = None
                errs[KEY[tag]] = str(e)[:160]
            finally:
                signal.alarm(0)
        mar = ms.margins(dg["nr4a3"], dg["nr4a1"], dg["nr4a2"])
        d = dock.get(label, {})
        v = ms.verdict(d.get("dock_min_margin"), mar["min_margin"])
        # SD of the min-margin = quadrature of the NR4A3 SD and the binding paralogue's SD (multi-snapshot).
        min_margin_sd = None
        if MULTISNAPSHOT and dg_sd.get("nr4a3") is not None:
            paras = [(mar["margin_vs_NR4A1"], dg_sd.get("nr4a1")), (mar["margin_vs_NR4A2"], dg_sd.get("nr4a2"))]
            binding = [p for p in paras if p[0] is not None and p[0] == mar["min_margin"]]
            psd = (binding[0][1] if binding and binding[0][1] is not None else 0.0)
            min_margin_sd = round((dg_sd["nr4a3"] ** 2 + psd ** 2) ** 0.5, 2)
        row = {"label": label, "chembl_id": d.get("chembl_id"),
               "dG_mmgbsa": {KEY[t]: dg[t] for t in PARALOGUES},
               "mm_margin_vs_NR4A1": mar["margin_vs_NR4A1"], "mm_margin_vs_NR4A2": mar["margin_vs_NR4A2"],
               "mm_min_margin": mar["min_margin"],
               "dock_min_margin": d.get("dock_min_margin"), "dock_cell": d.get("dock_cell"),
               "verdict": v}
        if MULTISNAPSHOT:
            row["dG_sd"] = {KEY[t]: dg_sd.get(t) for t in PARALOGUES}
            row["mm_min_margin_sd"] = min_margin_sd
        if errs:
            row["_errors"] = errs
        rows.append(row)
        _progress["done"] = i
        print(f"  [{i}/{len(labels)}] {label[:24]:<24} mmΔG3={dg['nr4a3']} mmMargin={mar['min_margin']} "
              f"dockMargin={d.get('dock_min_margin')} -> {v} ({int(time.time() - t0)}s)", flush=True)
        res["candidates"], res["_progress"] = rows, f"{i}/{len(labels)}"
        _write(res)                                      # checkpoint after every ligand (crash/stop-safe)

    stop.set()
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
