#!/usr/bin/env python3
"""SageMaker managed-SPOT Training entry — PHASE 2 SHAKEOUT (metad convergence plan): well-tempered
metadynamics on the DATA-DERIVED slow coordinate, one NR4A3 seed.

Phase 1 (TICA) showed corr(IC1, Rg)=0.68 -> Rg is an incomplete reaction coordinate (a hidden slow mode
exists). Phase 2 biases that data-derived coordinate instead of Rg. This SHAKEOUT proves, on a single
NR4A3 seed, that the coordinate (i) can be fit from the existing metad trajectories, (ii) wires into the
openmm-plumed metad stack as a PLUMED COMBINE of pocket-lining Cα distances, and (iii) actually drives
opening / recrossing — before the full 3-seed x 3-paralogue fleet is launched.

Two steps in ONE conda env (openmm + plumed + mdtraj + scipy):
  1) FIT: featurize the mounted metad trajectories (r1/r2/r3: pocket-lining pairwise Cα distances + Rg),
     fit the pure-numpy TICA (nr4a3_slow_cv.tica_covariances/tica_solve), orient IC1 so it grows on
     opening, build the PLUMED COMBINE spec (nr4a3_slow_cv.build_combine_cv), set SIGMA/grid from the
     observed range, write phase2_cv.json to the checkpoint dir (continuous S3 upload), and GATE:
     abort if |corr(s, Rg)| is ~1 (the distances-only slow mode collapsed to Rg -> no gain, add features)
     or if the CV is degenerate.
  2) RUN: nr4a3_metad.py with CV_MODE=tica_combine reads phase2_cv.json, maps the residue-labelled pairs
     to CA atoms in the freshly-built topology, and runs the biased MD (Rg kept only as an unfolding wall).

Resume is automatic + spot-safe (OUTPUT_DIR == /opt/ml/checkpoints, pre-populated + continuously synced);
the FIT step is idempotent (re-writes the same phase2_cv.json from the same trajectories + lag + seed).

Mounts (Training input channels, wired by nr4a3_metad_tica_sagemaker.py): /opt/ml/input/data/r{1,2,3}
each with nr4a3-lbd-metad.dcd + nr4a3-lbd-solvated.pdb (the existing metad replicas, for the CV fit).
"""
import glob
import json
import os
import shutil
import subprocess
import sys

OUT = os.environ.get("SM_CHECKPOINT_DIR", "/opt/ml/checkpoints")
LBD_FIRST = 373
CV_RESSEQS = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]
GATE_ABORT_ABS_CORR = 0.90     # |corr(s,Rg)| above this -> distances-only slow mode ~ Rg; abort (add features)


def _channel_dirs():
    """Locate the mounted metad replica channels (SageMaker Training puts channel X at
    /opt/ml/input/data/X). Each must have the trajectory + topology."""
    out = []
    base = "/opt/ml/input/data"
    for rep in ("r1", "r2", "r3"):
        d = os.path.join(base, rep)
        dcd = os.path.join(d, "nr4a3-lbd-metad.dcd")
        pdb = os.path.join(d, "nr4a3-lbd-solvated.pdb")
        if os.path.exists(dcd) and os.path.exists(pdb):
            out.append((rep, dcd, pdb))
        else:
            print(f"[phase2] channel {rep} missing dcd/pdb ({d}) — skipping", flush=True)
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", default="8")            # short shakeout
    ap.add_argument("--seed", default="1")
    ap.add_argument("--lag-frames", type=int, default=10)
    ap.add_argument("--n-components", type=int, default=5)
    ap.add_argument("--git-ref", default="main")
    args = ap.parse_args()

    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"], check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"
    git_sha = subprocess.run(["git", "-C", "/tmp/repo", "rev-parse", "HEAD"],
                             capture_output=True, text=True).stdout.strip()
    os.makedirs(OUT, exist_ok=True)

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[phase2] creating CUDA OpenMM + PLUMED + mdtraj + scipy env via {conda}", flush=True)
    create_env = os.environ.copy()
    create_env["CONDA_OVERRIDE_CUDA"] = "12.8"
    subprocess.run([conda, "create", "-y", "-n", "md", "-c", "conda-forge",
                    "python=3.11", "openmm", "pdbfixer", "openmm-plumed", "plumed", "biopython",
                    "mdtraj", "scipy", "numpy", "cuda-version=12.8"], check=True, env=create_env)

    spec_path = os.path.join(OUT, "phase2_cv.json")
    channels = _channel_dirs()
    # ---- STEP 1: fit the TICA CV from the mounted trajectories (skip if already written = resume) ----
    if os.path.exists(spec_path):
        print(f"[phase2] phase2_cv.json already present ({spec_path}) — reusing (resume).", flush=True)
    else:
        if not channels:
            sys.exit("[phase2] no metad replica channels mounted — cannot fit the CV.")
        fit_spec = {"channels": [{"label": c[0], "dcd": c[1], "pdb": c[2]} for c in channels],
                    "cv_resseqs": CV_RESSEQS, "lbd_first": LBD_FIRST, "lag_frames": args.lag_frames,
                    "n_components": args.n_components, "out": spec_path,
                    "gate_abs_corr": GATE_ABORT_ABS_CORR}
        with open("/tmp/fit_spec.json", "w") as fh:
            json.dump(fit_spec, fh)
        fit_code = r'''
import json, sys
import numpy as np
import mdtraj as md
sys.path.insert(0, "/tmp/repo/research/modalities")
import nr4a3_slow_cv as sc
fs = json.load(open("/tmp/fit_spec.json"))
def _resolve(top, resseqs, lbd_first):
    present = {top.residue(i).resSeq for i in range(top.n_residues)}
    if any(rs in present for rs in resseqs):
        return list(resseqs)
    return [rs - lbd_first + 1 for rs in resseqs]
dists_list, rg_list, pair_ref = [], [], None
for ch in fs["channels"]:
    t = md.load(ch["dcd"], top=ch["pdb"])
    prot = t.atom_slice(t.topology.select("protein"))
    lining = sorted(_resolve(prot.topology, fs["cv_resseqs"], fs["lbd_first"]))
    dists, rg, pairs = sc.featurize_distances(prot, lining)
    # pairs are in the trajectory's own numbering; map back to reference (373-based) numbering for labels
    off = fs["lbd_first"] - 1 if lining and lining[0] != fs["cv_resseqs"][0] else 0
    pairs_ref = [(a + off, b + off) for a, b in pairs]
    if pair_ref is None:
        pair_ref = pairs_ref
    elif pairs_ref != pair_ref:
        sys.exit("[phase2] pair ordering differs across replicas: %s vs %s" % (pairs_ref, pair_ref))
    dists_list.append(np.asarray(dists, float)); rg_list.append(np.asarray(rg, float))
    print("[phase2] featurized", ch["label"], dists.shape, flush=True)
C0, Ctau, mean, std, npairs = sc.tica_covariances(dists_list, fs["lag_frames"])
w, v = sc.tica_solve(C0, Ctau, n_components=fs["n_components"])
lead = v[:, 0]
# orient IC1 so it GROWS on opening: correlate the raw projection with pooled Rg, flip sign if negative
d_all = np.concatenate(dists_list, axis=0); rg_all = np.concatenate(rg_list)
proj = ((d_all - mean) / std) @ lead
if sc.pearson(proj, rg_all) < 0:
    lead = -lead; proj = -proj
spec = sc.build_combine_cv(lead, mean, std)
s_all = ((d_all - spec["parameters"]) * np.asarray(spec["coefficients"])).sum(axis=1)  # == proj (raw form)
corr = sc.pearson(s_all, rg_all)
ts = sc.implied_timescales([float(x) for x in w], fs["lag_frames"], 0.05)
s_min, s_max = float(s_all.min()), float(s_all.max()); s_rng = s_max - s_min or 1.0
sigma_s = max(0.05, 0.3 * float(s_all.std()))
out = {"pair_residues": [[int(a), int(b)] for a, b in pair_ref],
       "coefficients": spec["coefficients"], "parameters": spec["parameters"], "powers": spec["powers"],
       "sigma_s": sigma_s,
       # generous grid: biasing PUSHES s beyond the Rg-metad range (s oriented to grow on opening), so pad
       # the opening (high) side hard to avoid a PLUMED grid overflow mid-run.
       "grid_min": s_min - 1.0 * s_rng - 10 * sigma_s, "grid_max": s_max + 3.0 * s_rng + 10 * sigma_s,
       "grid_bin": 400, "corr_s_rg": corr, "abs_corr_s_rg": abs(corr),
       "tica_eigenvalues": [float(x) for x in w], "implied_timescales_ns": ts,
       "n_pairs": len(pair_ref), "n_input_frames": int(rg_all.size), "lag_frames": fs["lag_frames"],
       "s_observed_min": s_min, "s_observed_max": s_max, "s_std": float(s_all.std())}
json.dump(out, open(fs["out"], "w"), indent=2)
print("[phase2] CV fit: corr(s,Rg)=%.3f n_pairs=%d slowest_ts_ns=%.2f -> %s" %
      (corr, len(pair_ref), ts[0] if ts and ts[0] else float("nan"), fs["out"]))
if abs(corr) >= fs["gate_abs_corr"]:
    sys.exit("[phase2] GATE FAIL: |corr(s,Rg)|=%.3f >= %.2f — distances-only slow mode ~ Rg; "
             "add gate-chi1/SASA features before biasing (no gain from this CV)." % (abs(corr), fs["gate_abs_corr"]))
print("[phase2] GATE PASS: data-derived CV is distinct from Rg (|corr|=%.3f) — proceeding to biased MD." % abs(corr))
'''
        with open("/tmp/fit_cv.py", "w") as fh:
            fh.write(fit_code)
        fenv = os.environ.copy(); fenv.pop("PYTHONPATH", None)
        r = subprocess.run([conda, "run", "--no-capture-output", "-n", "md", "python", "/tmp/fit_cv.py"],
                           cwd=work, env=fenv)
        if r.returncode != 0:
            print(f"[phase2] CV fit/gate exited {r.returncode} (see above)", flush=True)
            sys.exit(r.returncode)

    # ---- STEP 2: biased MD on the data-derived CV (nr4a3_metad.py, CV_MODE=tica_combine) ----
    env = os.environ.copy()
    env["NS"] = args.ns
    env["TARGET"] = "NR4A3"
    env["SEED"] = args.seed
    env["GIT_REF"] = args.git_ref
    env["GIT_SHA"] = git_sha
    env["OUTPUT_DIR"] = OUT
    env["CV_MODE"] = "tica_combine"
    env["PHASE2_CV_JSON"] = spec_path
    env.pop("PYTHONPATH", None)
    print(f"[phase2] running tica_combine metad {args.ns} ns, seed={args.seed} (sha {git_sha[:10]})",
          flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "md", "python", "nr4a3_metad.py"],
                       cwd=work, env=env)
    for p in glob.glob(os.path.join(work, "AF-*.pdb")):
        shutil.copy(p, os.path.join(OUT, os.path.basename(p)))
    print(f"[phase2] metad exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
