#!/usr/bin/env python3
"""SageMaker entry: NR4A3 LBD well-tempered metadynamics (cryptic-pocket opening).

Same CUDA OpenMM conda recipe as the plain MD (entry.py) plus openmm-plumed for the metadynamics
bias. Runs nr4a3_metad.py and copies the CV/bias logs, trajectory, topology, and free-energy profile
to /opt/ml/processing/output (auto-uploaded to S3).
"""
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", default="30")
    ap.add_argument("--git-ref", default="main",
                    help="repo ref to run (branch/tag/sha); default main")
    args = ap.parse_args()
    ns = args.ns
    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    print(f"[sagemaker] running ref={args.git_ref}", flush=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating CUDA OpenMM + PLUMED env via {conda}", flush=True)
    create_env = os.environ.copy()
    create_env["CONDA_OVERRIDE_CUDA"] = "12.8"   # match the box driver; see deploy/aws-sagemaker-setup.md
    subprocess.run([conda, "create", "-y", "-n", "md", "-c", "conda-forge",
                    "python=3.11", "openmm", "pdbfixer", "openmm-plumed", "plumed",
                    "cuda-version=12.8"], check=True, env=create_env)

    env = os.environ.copy()
    env["NS"] = ns
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running metadynamics for {ns} ns", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "md",
                        "python", "nr4a3_metad.py"], cwd=work, env=env)

    for f in ("AF-Q92570.pdb", "nr4a3-lbd-solvated.pdb", "nr4a3-lbd-metad.dcd",
              "COLVAR", "HILLS", "fes.dat"):
        p = os.path.join(work, f)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(OUT, f))
            print(f"[sagemaker] saved {f} ({os.path.getsize(p)} bytes)", flush=True)
    print(f"[sagemaker] metad exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
