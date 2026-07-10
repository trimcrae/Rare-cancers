#!/usr/bin/env python3
"""SageMaker entry — PHASE 0 of the metad convergence re-strengthening plan
(research/modalities/nr4a3-metad-convergence-plan.md).

**Per-replica** harmonized orthosteric-pocket scoring of the three independent WTMetaD replicas
(nr4a3-metad-r{1,2,3}). Runs the EXISTING `nr4a3_mdpocket.py` on each replica's trajectory with the
score-INDEPENDENT harmonized matcher (POCKET_MATCH=harmonized) and the PINNED fpocket build (4.2.3), so we can
ask, per replica and independently of the fixed-Rg proxy:
  (a) does a MATCHED, >= D* cavity-bearing sub-ensemble exist in THIS replica? (both denominators reported)
  (b) at what CV Rg values do the druggable frames sit? (druggability_timeseries carries cv_rg per frame)

This directly tests the round-6 reviewer's "are the replicas even comparing the same physical state?" doubt:
if a matched druggable cavity is found independently in each replica, the pocket claim survives the
non-convergence of F(Rg); if not, the pocket claim weakens on its own.

CPU work (fpocket); does NOT touch the GPU quota. Mounts (ProcessingInputs, wired by the submitter):
  /opt/ml/processing/r1  nr4a3-metad-r1/ckpt  (nr4a3-lbd-metad.dcd + nr4a3-lbd-solvated.pdb + HILLS/COLVAR/fes)
  /opt/ml/processing/r2  nr4a3-metad-r2/ckpt
  /opt/ml/processing/r3  nr4a3-metad-r3/ckpt
Output uploaded CONTINUOUSLY (per-replica JSON + a consolidated table reach S3 as written).
"""
import json
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"
REPS = {"r1": "/opt/ml/processing/r1", "r2": "/opt/ml/processing/r2", "r3": "/opt/ml/processing/r3"}
DCD_NAME = "nr4a3-lbd-metad.dcd"


def _run(conda, envname, work, script, env, label):
    print(f"[phase0] === {label}: {script} ===", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", envname, "python", script],
                       cwd=work, env=env)
    print(f"[phase0] {label} exit={r.returncode}", flush=True)
    return r.returncode


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main")
    ap.add_argument("--pocket-match", default="harmonized")  # harmonized | legacy (diagnostic)
    args = ap.parse_args()

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"], check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[phase0] creating analysis env (mdtraj + fpocket=4.2.3 + biopython) via {conda}", flush=True)
    subprocess.run([conda, "create", "-y", "-n", "an", "-c", "conda-forge",
                    "python=3.11", "mdtraj", "fpocket=4.2.3", "biopython", "matplotlib-base", "numpy"],
                   check=True)

    os.makedirs(OUT, exist_ok=True)
    base = os.environ.copy()
    base["POCKET_MATCH"] = args.pocket_match

    per_replica = {}
    for rep, mount in REPS.items():
        if not os.path.isdir(mount) or not os.path.exists(os.path.join(mount, DCD_NAME)):
            print(f"[phase0] SKIP {rep} — {mount}/{DCD_NAME} not mounted", flush=True)
            continue
        e = dict(base)
        e["INPUT_DIR"] = mount            # trajectory (nr4a3-lbd-metad.dcd) + topology + fes.dat live together
        e["STRUCTURE_DIR"] = mount
        e["DCD_NAME"] = DCD_NAME
        e["OUTPUT_DIR"] = os.path.join(OUT, rep)
        os.makedirs(e["OUTPUT_DIR"], exist_ok=True)
        _run(conda, "an", work, "nr4a3_mdpocket.py", e, rep)
        summ = os.path.join(e["OUTPUT_DIR"], "pocket_analysis_summary.json")
        per_replica[rep] = summ if os.path.exists(summ) else None

    # consolidate the harmonized both-denominator detection + druggable-frame CV per replica
    aggregate(conda, work, per_replica)


def aggregate(conda, work, per_replica):
    code = f'''
import json, os
OUT = "{OUT}"
paths = {json.dumps({k: v for k, v in per_replica.items()})}
rows = []
for rep, p in paths.items():
    if not p or not os.path.exists(p):
        rows.append({{"replica": rep, "status": "missing"}}); continue
    d = json.load(open(p))
    dts = d.get("druggability_timeseries") or {{}}
    h = dts.get("harmonized_detection") or {{}}
    rows.append({{
        "replica": rep,
        "n_frames": d.get("n_frames"),
        "frac_ge_0.53": dts.get("frac_frames_druggable_0.53"),
        "max_druggability": dts.get("max_druggability"),
        "mean_druggability": dts.get("mean_druggability"),
        "harmonized_detection": {{k: h.get(k) for k in ("d_star","n_propagated","n_detected","detection_fraction",
                                  "frac_ge_among_detected","frac_ge_among_propagated")}},
        "lowest_cost_druggable": d.get("lowest_cost_druggable"),
        "cv_rg_of_druggable": dts.get("cv_rg_of_druggable_frames") or dts.get("druggable_frame_cv_rg"),
    }})
tbl = {{"_title": "PHASE 0 — per-replica harmonized orthosteric-pocket detection across the 3 WTMetaD replicas",
        "_method": "nr4a3_mdpocket.py per replica, POCKET_MATCH=harmonized, pinned fpocket 4.2.3; both denominators.",
        "rows": rows}}
outp = os.path.join(OUT, "metad-replica-pocket-summary.json")
json.dump(tbl, open(outp,"w"), indent=2)
print("[phase0] wrote", outp)
for r in rows:
    print("   ", r.get("replica"), "detfrac=", (r.get("harmonized_detection") or {{}}).get("detection_fraction"),
          "frac>=D*(prop)=", (r.get("harmonized_detection") or {{}}).get("frac_ge_among_propagated"))
'''
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "an", "python", "-c", code],
                       cwd=work, env=os.environ.copy())
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
