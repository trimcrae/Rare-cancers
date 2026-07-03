#!/usr/bin/env python3
"""SageMaker entry: unbiased "release" MD from the metad-opened NR4A3 pocket (Gate-3 disambiguation).

Mounts the metad outputs (ProcessingInput at /opt/ml/processing/input: metad_system.xml,
nr4a3-lbd-solvated.pdb, nr4a3-lbd-metad.dcd), builds the CUDA OpenMM env (+ mdtraj), runs
nr4a3_md_release.py (no PLUMED — the base system is unbiased), and copies the Rg traces + summary to
/opt/ml/processing/output for S3. GPU job.
"""
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", default="5")
    ap.add_argument("--n-rep", default="3")
    ap.add_argument("--target-rg", default="0.717")
    ap.add_argument("--run-tag", default="release")
    ap.add_argument("--checkpoint-every", default="10")
    ap.add_argument("--git-ref", default="main")
    args = ap.parse_args()
    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    create_env = os.environ.copy()
    create_env["CONDA_OVERRIDE_CUDA"] = "12.8"
    print(f"[sagemaker] creating CUDA OpenMM + mdtraj env via {conda}", flush=True)
    subprocess.run([conda, "create", "-y", "-n", "md", "-c", "conda-forge",
                    "python=3.11", "openmm", "mdtraj", "cuda-version=12.8"], check=True, env=create_env)

    env = os.environ.copy()
    env["INPUT_DIR"] = "/opt/ml/processing/input"
    env["OUTPUT_DIR"] = OUT
    env["NS"] = args.ns
    env["N_REP"] = args.n_rep
    env["TARGET_RG"] = args.target_rg
    env["RUN_TAG"] = args.run_tag
    env["CHECKPOINT_EVERY"] = args.checkpoint_every
    # If a prior checkpoint was mounted for RESUME, point the harness at it (continue trajectories); else the
    # harness treats OUTPUT_DIR as the (empty) resume dir and seeds fresh.
    resume = "/opt/ml/processing/resume"
    env["RESUME_DIR"] = resume if os.path.isdir(resume) else OUT
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running unbiased release MD ({args.n_rep} x {args.ns} ns)", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "md",
                        "python", "nr4a3_md_release.py"], cwd=work, env=env)
    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] release exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
