#!/usr/bin/env python3
"""SageMaker entry for the NR4A3 metadynamics convergence + orthogonal-CV analysis (CPU work).

Mounts a metad replica's outputs (HILLS, COLVAR, nr4a3-lbd-solvated.pdb, nr4a3-lbd-metad.dcd) at
/opt/ml/processing/input, conda-installs the analysis stack (mdtraj + numpy + matplotlib; fpocket for
the best-effort mdpocket volume), and runs nr4a3_metad_analysis.py. SageMaker uploads
/opt/ml/processing/output to S3 on completion. No GPU/CUDA here — cheap CPU follow-up.

The heavy convergence math (per-block F(Rg) reconstruction, recrossings, 2D reweight) is pure Python;
mdtraj/numpy are only needed for the per-frame gate distance + CV Rg from the trajectory.
"""
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dcd-name", default="nr4a3-lbd-metad.dcd",
                    help="metad trajectory filename in the mounted input dir")
    ap.add_argument("--structure-dir", default="",
                    help="dir holding nr4a3-lbd-solvated.pdb when it is NOT in the input dir; "
                         "empty = same as INPUT_DIR")
    ap.add_argument("--block-ns", default="10", help="convergence block size (ns): F at 10/20/30/...")
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
    env["BLOCK_NS"] = args.block_ns
    if args.structure_dir:
        env["STRUCTURE_DIR"] = args.structure_dir
    env.pop("PYTHONPATH", None)   # don't let the base container's site-packages shadow the conda env
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running metad analysis on {args.dcd_name}, block_ns={args.block_ns} "
          f"(ref {args.git_ref})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "an",
                        "python", "nr4a3_metad_analysis.py"], cwd=work, env=env)
    print(f"[sagemaker] analysis exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
