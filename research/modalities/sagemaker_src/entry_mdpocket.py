#!/usr/bin/env python3
"""SageMaker entry for the NR4A3 MD-trajectory pocket analysis (CPU work).

The MD outputs are mounted on the "traj" input channel (read via sm_io.channel("traj")). We conda-install
the analysis stack (mdtraj + fpocket/mdpocket + matplotlib) from conda-forge into an isolated env and run
nr4a3_mdpocket.py; SageMaker syncs sm_io.out_dir() (spot Training checkpoint dir) to S3 continuously. No
GPU/CUDA here.
"""
import os
import shutil
import subprocess
import sys

import sm_io
OUT = sm_io.out_dir()   # spot Training → /opt/ml/checkpoints (continuous S3 sync); Processing → legacy path


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dcd-name", default="nr4a3-lbd-md.dcd",
                    help="trajectory filename in the mounted input dir (use nr4a3-lbd-metad.dcd "
                         "for the metadynamics run, or release_rep0.dcd for the release run)")
    ap.add_argument("--structure-dir", default="",
                    help="dir holding nr4a3-lbd-solvated.pdb when it is NOT in the trajectory input dir "
                         "(a separately-mounted structure prefix); empty = same as INPUT_DIR")
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
                    "python=3.11", "mdtraj", "fpocket=4.2.3", "matplotlib-base", "numpy"], check=True)

    env = os.environ.copy()
    env["INPUT_DIR"] = sm_io.channel("traj")
    env["OUTPUT_DIR"] = OUT
    env["DCD_NAME"] = args.dcd_name
    if args.structure_dir:
        # --structure-dir now carries the CHANNEL NAME (e.g. "structure"); resolve to its local mount.
        env["STRUCTURE_DIR"] = sm_io.channel(args.structure_dir)   # solvated PDB from a separate channel
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
