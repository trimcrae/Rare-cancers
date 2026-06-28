#!/usr/bin/env python3
"""SageMaker entry for the MM-GBSA endpoint rescoring (nr4a3_mmgbsa.py). CPU work, no MD.

One ProcessingInput (s3://<bucket>/nr4a3-matrix) is mounted at /opt/ml/processing/input — it holds the
matrix job's receptors (<tag>-opened.pdb), docked poses (docked_<tag>.sdf) and nr4a3-matrix.json. Builds
the MM env (openmm + openmmforcefields + openff-toolkit + ambertools + pdbfixer + rdkit), runs
nr4a3_mmgbsa.py, and copies nr4a3-mmgbsa.json (+ the sysgen cache) to S3.
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
    args = ap.parse_args()

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating mmgbsa env via {conda}", flush=True)
    subprocess.run([conda, "create", "-y", "-n", "mmg", "-c", "conda-forge",
                    "python=3.11", "openmm", "openmmforcefields", "openff-toolkit", "ambertools",
                    "pdbfixer", "rdkit", "numpy"], check=True)

    env = os.environ.copy()
    env["INPUT_DIR"] = "/opt/ml/processing/input"     # nr4a3-matrix outputs mounted here
    env["OUTPUT_DIR"] = OUT
    os.makedirs(OUT, exist_ok=True)
    present = sorted(f for f in os.listdir(env["INPUT_DIR"])) if os.path.isdir(env["INPUT_DIR"]) else []
    print(f"[sagemaker] mounted matrix inputs: {present}", flush=True)
    print(f"[sagemaker] running MM-GBSA rescoring (ref {args.git_ref})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "mmg",
                        "python", "nr4a3_mmgbsa.py"], cwd=work, env=env)
    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] mmgbsa exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
