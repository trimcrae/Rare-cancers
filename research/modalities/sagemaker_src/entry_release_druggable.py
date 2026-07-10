#!/usr/bin/env python3
"""SageMaker entry for STEP 0 — the NR4A3 druggable-release receptor re-anchor (nr4a3_release_druggable.py).

CPU work. ProcessingInputs mount three S3 prefixes:
  /opt/ml/processing/input/release : nr4a3-release      (release_rep*.dcd)
  /opt/ml/processing/input/struct  : nr4a3-metad        (nr4a3-lbd-solvated.pdb topology)
  /opt/ml/processing/input/pocket  : nr4a3-release-pocket (existing per-frame druggability summary; reused)
We conda-install the analysis stack (mdtraj + fpocket + matplotlib + numpy) and run the driver; SageMaker
uploads /opt/ml/processing/output (the manifest + receptor PDBs + plot) to S3 on completion. No GPU/CUDA.
"""
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main", help="repo ref to run; default main")
    ap.add_argument("--target-rg", default="0.737", help="CV Rg (nm) of the druggable state to anchor on")
    ap.add_argument("--n-alt", default="3", help="alternate receptor frames to keep (breathing ensemble)")
    ap.add_argument("--d-star", default="0.53", help="druggable threshold (calibrated drug-bound band)")
    ap.add_argument("--force-scan", default="", help="set to 1 to ignore the reusable summary and re-scan")
    args = ap.parse_args()

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating analysis env via {conda}", flush=True)
    subprocess.run([conda, "create", "-y", "-n", "an", "-c", "conda-forge",
                    "python=3.11", "mdtraj", "fpocket=4.2.3", "matplotlib-base", "numpy"], check=True)

    env = os.environ.copy()
    env["RELEASE_DIR"] = "/opt/ml/processing/input/release"
    env["STRUCTURE_DIR"] = "/opt/ml/processing/input/struct"
    env["POCKET_DIR"] = "/opt/ml/processing/input/pocket"
    env["OUTPUT_DIR"] = OUT
    env["TARGET_RG"] = args.target_rg
    env["N_ALT"] = args.n_alt
    env["D_STAR"] = args.d_star
    if args.force_scan:
        env["FORCE_SCAN"] = args.force_scan
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running receptor re-anchor (ref {args.git_ref}, target_rg={args.target_rg}, "
          f"n_alt={args.n_alt})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "an",
                        "python", "nr4a3_release_druggable.py"], cwd=work, env=env)
    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] receptor re-anchor exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
