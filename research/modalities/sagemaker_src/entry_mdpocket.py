#!/usr/bin/env python3
"""SageMaker entry for the NR4A3 MD-trajectory pocket analysis (CPU work).

The MD outputs are mounted by ProcessingInput at /opt/ml/processing/input. We conda-install the
analysis stack (mdtraj + fpocket/mdpocket + matplotlib) from conda-forge into an isolated env and run
nr4a3_mdpocket.py; SageMaker uploads /opt/ml/processing/output to S3 on completion. No GPU/CUDA here.
"""
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dcd-name", default="nr4a3-lbd-md.dcd",
                    help="trajectory filename in the mounted input dir (use nr4a3-lbd-metad.dcd "
                         "for the metadynamics run)")
    ap.add_argument("--git-ref", default="main", help="repo ref to run; default main")
    args = ap.parse_args()

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating analysis env via {conda}", flush=True)
    subprocess.run([conda, "create", "-y", "-n", "an", "-c", "conda-forge",
                    "python=3.11", "mdtraj", "fpocket", "matplotlib-base", "numpy"], check=True)

    env = os.environ.copy()
    env["INPUT_DIR"] = "/opt/ml/processing/input"
    env["OUTPUT_DIR"] = OUT
    env["DCD_NAME"] = args.dcd_name
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] analyzing trajectory {args.dcd_name} (ref {args.git_ref})", flush=True)
    print("[sagemaker] running pocket analysis", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "an",
                        "python", "nr4a3_mdpocket.py"], cwd=work, env=env)
    print(f"[sagemaker] analysis exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
