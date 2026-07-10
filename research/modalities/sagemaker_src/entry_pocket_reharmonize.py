#!/usr/bin/env python3
"""SageMaker entry: RE-HARMONIZE every load-bearing NR4A3 ensemble with the score-INDEPENDENT
orthosteric-pocket matcher + the PINNED fpocket build, and emit ONE consolidated detection-fraction
table (reviewer P0).

It runs the EXISTING scorers as subprocesses with POCKET_MATCH=harmonized and fpocket pinned to 4.2.3
(single homogeneous build), each into its own OUTPUT subdir, then aggregates their both-denominator
`harmonized_detection` blocks with nr4a3_pocket_reharmonize.

Ensembles re-scored:
  af2_static           AF2 model AF-Q92570 (fetched from AFDB)             -> nr4a3_fpocket_enumerate.py
  calibration          NR-panel calibration structures (AFDB + RCSB)       -> nr4a3_calibration.py
  8xtt                 all 20 8XTT NMR conformers (fetched from RCSB)       -> nr4a3_8xtt_benchmark.py
  metad                metadynamics trajectory frames                      -> nr4a3_mdpocket.py
  release_rep0..2      the 3 unbiased release replicas (+ a pooled row)    -> nr4a3_mdpocket.py x3

Mounts (ProcessingInputs; the submitter wires the S3 prefixes):
  /opt/ml/processing/metad    nr4a3-metad prefix  (nr4a3-lbd-metad.dcd + nr4a3-lbd-solvated.pdb + fes.dat)
  /opt/ml/processing/release  nr4a3-release prefix (release_rep*.dcd)
AF2 + 8XTT + calibration panel are fetched from AFDB/RCSB at runtime (no S3 input). CPU work (fpocket).
Output uploaded CONTINUOUSLY so per-ensemble JSONs + the consolidated table reach S3 as written.
"""
import json
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"
METAD = "/opt/ml/processing/metad"
RELEASE = "/opt/ml/processing/release"


def _run(conda, envname, work, script, env, label):
    print(f"[reharmonize] === {label}: {script} ===", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", envname, "python", script],
                       cwd=work, env=env)
    print(f"[reharmonize] {label} exit={r.returncode}", flush=True)
    return r.returncode


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main")
    ap.add_argument("--n-release-reps", type=int, default=3)
    ap.add_argument("--pocket-match", default="harmonized")  # harmonized | legacy (diagnostic comparison)
    args = ap.parse_args()

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[reharmonize] creating analysis env (mdtraj + fpocket=4.2.3 + biopython) via {conda}",
          flush=True)
    subprocess.run([conda, "create", "-y", "-n", "an", "-c", "conda-forge",
                    "python=3.11", "mdtraj", "fpocket=4.2.3", "biopython", "matplotlib-base", "numpy"],
                   check=True)

    os.makedirs(OUT, exist_ok=True)
    base = os.environ.copy()
    base["POCKET_MATCH"] = args.pocket_match             # harmonized (default) | legacy (diagnostic)

    # --- af2_static: fetch AF-Q92570 then enumerate --------------------------------------------------
    af2_dir = "/tmp/af2"
    os.makedirs(af2_dir, exist_ok=True)
    subprocess.run([conda, "run", "--no-capture-output", "-n", "an", "python", "-c",
                    "import nr4a3_structure as ns; ns.fetch_pdb('Q92570', '/tmp/af2/AF-Q92570.pdb')"],
                   cwd=work, check=False)
    e = dict(base); e["INPUT_DIR"] = af2_dir; e["OUTPUT_DIR"] = os.path.join(OUT, "af2_static")
    os.makedirs(e["OUTPUT_DIR"], exist_ok=True)
    _run(conda, "an", work, "nr4a3_fpocket_enumerate.py", e, "af2_static")

    # --- calibration panel (writes nr4a3-calibration.json into the script dir; copy it out) ----------
    e = dict(base)
    _run(conda, "an", work, "nr4a3_calibration.py", e, "calibration")
    cal_out = os.path.join(OUT, "calibration"); os.makedirs(cal_out, exist_ok=True)
    src_cal = os.path.join(work, "nr4a3-calibration.json")
    if os.path.exists(src_cal):
        shutil.copy(src_cal, os.path.join(cal_out, "nr4a3-calibration.json"))

    # --- 8XTT: all 20 NMR conformers (fetches 8XTT + AF2 itself) -------------------------------------
    e = dict(base); e["OUTPUT_DIR"] = os.path.join(OUT, "8xtt")
    os.makedirs(e["OUTPUT_DIR"], exist_ok=True)
    _run(conda, "an", work, "nr4a3_8xtt_benchmark.py", e, "8xtt")

    # --- metad trajectory frames --------------------------------------------------------------------
    if os.path.isdir(METAD):
        e = dict(base); e["INPUT_DIR"] = METAD; e["STRUCTURE_DIR"] = METAD
        e["DCD_NAME"] = "nr4a3-lbd-metad.dcd"; e["OUTPUT_DIR"] = os.path.join(OUT, "metad")
        os.makedirs(e["OUTPUT_DIR"], exist_ok=True)
        _run(conda, "an", work, "nr4a3_mdpocket.py", e, "metad")
    else:
        print(f"[reharmonize] SKIP metad — {METAD} not mounted", flush=True)

    # --- release replicas (topology from the metad prefix) ------------------------------------------
    release_rep_dirs = []
    if os.path.isdir(RELEASE) and os.path.isdir(METAD):
        for k in range(args.n_release_reps):
            dcd = f"release_rep{k}.dcd"
            if not os.path.exists(os.path.join(RELEASE, dcd)):
                print(f"[reharmonize] SKIP {dcd} — not present", flush=True)
                continue
            e = dict(base); e["INPUT_DIR"] = RELEASE; e["STRUCTURE_DIR"] = METAD
            e["DCD_NAME"] = dcd; e["OUTPUT_DIR"] = os.path.join(OUT, f"release_rep{k}")
            os.makedirs(e["OUTPUT_DIR"], exist_ok=True)
            _run(conda, "an", work, "nr4a3_mdpocket.py", e, f"release_rep{k}")
            release_rep_dirs.append((f"release_rep{k}", e["OUTPUT_DIR"]))
    else:
        print(f"[reharmonize] SKIP release — {RELEASE} or {METAD} not mounted", flush=True)

    # --- aggregate into ONE consolidated table ------------------------------------------------------
    aggregate(conda, work)


def aggregate(conda, work):
    """Run the pure aggregator inside the env (it imports pocket_tracking). Builds the spec, pools the
    release reps, writes pocket-reharmonize-summary.json."""
    n_reps = 3
    agg_code = f'''
import json, os
import nr4a3_pocket_reharmonize as rh
import pocket_tracking as pt
OUT = "{OUT}"
def load(p):
    try:
        return json.load(open(p))
    except Exception:
        return None
entries = []
entries.append({{"ensemble":"af2_static","kind":"af2_static",
                 "result":load(os.path.join(OUT,"af2_static","pocket5_lining_residues.json"))}})
entries.append({{"ensemble":"calibration_nr4a3","kind":"calibration_nr4a3",
                 "result":load(os.path.join(OUT,"calibration","nr4a3-calibration.json"))}})
entries.append({{"ensemble":"8xtt_20conformers","kind":"8xtt",
                 "result":load(os.path.join(OUT,"8xtt","nr4a3-8xtt-benchmark.json"))}})
entries.append({{"ensemble":"metad_frames","kind":"metad",
                 "result":load(os.path.join(OUT,"metad","pocket_analysis_summary.json"))}})
rep_dets = []
for k in range({n_reps}):
    r = load(os.path.join(OUT, f"release_rep{{k}}", "pocket_analysis_summary.json"))
    d = rh.detection_from_result("release_rep", r)
    if d:
        rep_dets.append(d)
        entries.append({{"ensemble": f"release_rep{{k}}", "kind":"prebuilt", "result": d}})
pooled = rh.pool_detection(rep_dets)
if pooled:
    entries.append({{"ensemble":"release_unbiased_pooled","kind":"prebuilt","result":pooled}})
tbl = rh.build_consolidated(entries, fpocket_version=pt.resolved_fpocket_version())
outp = os.path.join(OUT, "pocket-reharmonize-summary.json")
json.dump(tbl, open(outp,"w"), indent=2)
print("[reharmonize] wrote", outp)
for row in tbl["rows"]:
    print("   ", row["ensemble"], "n=", row["n_propagated"], "det=", row["n_detected"],
          "detfrac=", row["detection_fraction"], "ge_all=", row["frac_ge_among_propagated"])
'''
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "an", "python", "-c", agg_code],
                       cwd=work, env=os.environ.copy())
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
