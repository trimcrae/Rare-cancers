#!/usr/bin/env python3
"""SageMaker entry for the NR4A family-wide selectivity matrix (nr4a3_matrix.py). CPU work.

Three ProcessingInputs are mounted under /opt/ml/processing/input as nr4a3/ nr4a1/ nr4a2/ (each a
`*-metad` opened-ensemble set). Builds the docking/cheminformatics conda env (same as the warhead),
runs nr4a3_matrix.py, and copies nr4a3-matrix.json (+ opened-conformer PDBs / pose SDFs) to S3.
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
    print(f"[sagemaker] creating matrix env via {conda}", flush=True)
    subprocess.run([conda, "create", "-y", "-n", "mx", "-c", "conda-forge",
                    "python=3.11", "mdtraj", "fpocket", "smina", "rdkit", "biopython", "numpy"],
                   check=True)

    env = os.environ.copy()
    env["INPUT_DIR"] = "/opt/ml/processing/input"     # holds nr4a3/ nr4a1/ nr4a2/ subdirs
    env["OUTPUT_DIR"] = OUT
    os.makedirs(OUT, exist_ok=True)
    print("[sagemaker] mounted inputs:", flush=True)
    for sub in ("nr4a3", "nr4a1", "nr4a2"):
        p = os.path.join(env["INPUT_DIR"], sub)
        print(f"  {sub}: {'present' if os.path.isdir(p) else 'MISSING'}", flush=True)
    print(f"[sagemaker] running selectivity matrix (ref {args.git_ref})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "mx",
                        "python", "nr4a3_matrix.py"], cwd=work, env=env)
    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] matrix exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
