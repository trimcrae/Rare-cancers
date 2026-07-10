#!/usr/bin/env python3
"""SageMaker entry — PHASE 1 (metad convergence plan): find the true slow CV of pocket opening via TICA.

Loads the EXISTING trajectories (metad r1/r2/r3 + the unbiased release replicas), featurizes each with
nr4a3_slow_cv.featurize_trajectory (pocket-lining Cα distances, gate-residue χ1 sin/cos, lining SASA, and Rg),
fits TICA (deeptime) on the pooled features, and reports the slowest modes + the decisive number:
corr(IC1, Rg). |corr|~1 => Rg already captures the slow mode; |corr| well below 1 => a hidden slow coordinate
exists and biasing Rg alone is the convergence problem (bias a better CV in Phase 2).

Mounts (ProcessingInputs, wired by the submitter): /opt/ml/processing/r{1,2,3} (metad replica ckpt prefixes,
each with nr4a3-lbd-metad.dcd + nr4a3-lbd-solvated.pdb) and optionally /opt/ml/processing/release
(release_rep*.dcd + topology from the metad prefix). CPU. Output uploaded continuously.
"""
import glob
import json
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"
LBD_FIRST = 373                       # NR4A3 LBD construct first residue (manifest); topology may renumber from 1
CV_RESSEQS = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]   # pocket-lining set (metad CV residues)
GATE_RESSEQS = [407, 410, 412, 484, 531]                          # rotameric gate subset for χ1


def _resolve_resseqs(top, resseqs):
    """Return resseqs in the trajectory's own numbering: use them as-is if present, else map assuming the
    topology was renumbered from 1 (construct residue 1 == LBD_FIRST)."""
    present = {top.residue(i).resSeq for i in range(top.n_residues)}
    if any(rs in present for rs in resseqs):
        return list(resseqs)
    return [rs - LBD_FIRST + 1 for rs in resseqs]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main")
    ap.add_argument("--lag-frames", type=int, default=10)   # 10 frames * 0.05 ns = 0.5 ns lag
    ap.add_argument("--n-components", type=int, default=5)
    args = ap.parse_args()

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"], check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[phase1] creating env (mdtraj + deeptime + numpy + scipy) via {conda}", flush=True)
    subprocess.run([conda, "create", "-y", "-n", "sc", "-c", "conda-forge",
                    "python=3.11", "mdtraj", "numpy", "scipy"], check=True)
    subprocess.run([conda, "run", "-n", "sc", "pip", "install", "deeptime"], check=True)

    os.makedirs(OUT, exist_ok=True)
    # discover trajectory (dcd) + topology (pdb) per mounted replica
    channels = []
    for rep in ("r1", "r2", "r3"):
        d = f"/opt/ml/processing/{rep}"
        dcd = os.path.join(d, "nr4a3-lbd-metad.dcd")
        pdb = os.path.join(d, "nr4a3-lbd-solvated.pdb")
        if os.path.exists(dcd) and os.path.exists(pdb):
            channels.append((rep, dcd, pdb))
        else:
            print(f"[phase1] SKIP {rep} — missing {dcd} or {pdb}", flush=True)
    rel = "/opt/ml/processing/release"
    reltop = None
    for rep in ("r1", "r2", "r3"):
        cand = os.path.join(f"/opt/ml/processing/{rep}", "nr4a3-lbd-solvated.pdb")
        if os.path.exists(cand):
            reltop = cand; break
    if os.path.isdir(rel) and reltop:
        for dcd in sorted(glob.glob(os.path.join(rel, "release_rep*.dcd"))):
            channels.append((os.path.basename(dcd).replace(".dcd", ""), dcd, reltop))

    spec = {"channels": [{"label": c[0], "dcd": c[1], "pdb": c[2]} for c in channels],
            "cv_resseqs": CV_RESSEQS, "gate_resseqs": GATE_RESSEQS,
            "lbd_first": LBD_FIRST, "lag_frames": args.lag_frames, "n_components": args.n_components}
    with open("/tmp/spec.json", "w") as fh:
        json.dump(spec, fh)

    code = r'''
import json, os, sys
import numpy as np
import mdtraj as md
sys.path.insert(0, "/tmp/repo/research/modalities")
import nr4a3_slow_cv as sc
spec = json.load(open("/tmp/spec.json"))
def _resolve_resseqs(top, resseqs, lbd_first):
    present = {top.residue(i).resSeq for i in range(top.n_residues)}
    if any(rs in present for rs in resseqs):
        return list(resseqs)
    return [rs - lbd_first + 1 for rs in resseqs]
OUT = "''' + OUT + r'''"
NS_PER_FRAME = 0.05
all_feats, all_rg, per_chan = [], [], []
for ch in spec["channels"]:
    try:
        t = md.load(ch["dcd"], top=ch["pdb"])
        prot = t.atom_slice(t.topology.select("protein"))
        lining = _resolve_resseqs(prot.topology, spec["cv_resseqs"], spec["lbd_first"])
        gate = _resolve_resseqs(prot.topology, spec["gate_resseqs"], spec["lbd_first"])
        feats, rg = sc.featurize_trajectory(prot, lining, gate)
        all_feats.append(feats); all_rg.append(rg)
        per_chan.append({"label": ch["label"], "n_frames": int(feats.shape[0]),
                         "n_features": int(feats.shape[1]),
                         "corr_rg_ic_will_be": None})
        print("[phase1] featurized", ch["label"], feats.shape, flush=True)
    except Exception as e:
        print("[phase1] FAILED", ch["label"], repr(e), flush=True)
if not all_feats:
    sys.exit("[phase1] no trajectories featurized")
# TICA on the pooled features (deeptime accepts a list of trajectories)
res = sc.run_tica(all_feats, lag_frames=spec["lag_frames"], n_components=spec["n_components"])
proj = res["projection"]
proj = np.concatenate(proj, axis=0) if isinstance(proj, list) else np.asarray(proj)
rg_all = np.concatenate(all_rg)
ic1 = proj[:, 0]
corr = sc.pearson(ic1, rg_all)
ts = sc.implied_timescales(res["eigenvalues"], spec["lag_frames"], NS_PER_FRAME)
verdict = sc.redundancy_verdict(corr)
out = {"_title": "PHASE 1 — TICA slow-CV of NR4A3 pocket opening (metad + release trajectories)",
       "_decisive": "corr(IC1, Rg): ~1 => Rg captures the slow mode; << 1 => a hidden slow CV exists.",
       "lag_frames": spec["lag_frames"], "lag_ns": spec["lag_frames"]*NS_PER_FRAME,
       "n_channels": len(all_feats), "total_frames": int(rg_all.size),
       "tica_eigenvalues": res["eigenvalues"], "implied_timescales_ns": ts,
       "corr_ic1_rg": corr, "abs_corr_ic1_rg": abs(corr), "redundancy_verdict": verdict,
       "channels": per_chan}
json.dump(out, open(os.path.join(OUT, "slow-cv-summary.json"), "w"), indent=2)
print("[phase1] corr(IC1,Rg)=%.3f verdict=%s timescales_ns=%s" % (corr, verdict, ts))
'''
    with open("/tmp/run_tica.py", "w") as fh:
        fh.write(code)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "sc", "python", "/tmp/run_tica.py"],
                       cwd=work, env=os.environ.copy())
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
