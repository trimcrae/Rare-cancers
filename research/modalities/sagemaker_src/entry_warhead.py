#!/usr/bin/env python3
"""SageMaker entry for the selective NR4A3 warhead screen (nr4a3_warhead.py).

Mounts the 30 ns metad outputs (ProcessingInput at /opt/ml/processing/input), builds a conda env with
the docking/cheminformatics stack (mdtraj + fpocket + smina + rdkit + biopython + numpy), extracts the
opened conformer, docks candidates into NR4A3-opened + NR4A1/NR4A2, and copies nr4a3-warhead.json (and
the conformer/pose SDFs) to /opt/ml/processing/output for S3. CPU work; defaults to g5 to reuse the
GPU quota. No GPU needed unless a de-novo generative model is wired (DENOVO_MODEL).
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
    print(f"[sagemaker] creating warhead env via {conda}", flush=True)
    subprocess.run([conda, "create", "-y", "-n", "wh", "-c", "conda-forge",
                    "python=3.11", "mdtraj", "fpocket=4.2.3", "smina", "rdkit", "biopython", "numpy"],
                   check=True)

    env = os.environ.copy()
    env["INPUT_DIR"] = "/opt/ml/processing/input"
    env["OUTPUT_DIR"] = OUT
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running warhead screen (ref {args.git_ref})", flush=True)
    # nr4a3_warhead.py writes all outputs (nr4a3-warhead.json + conformer/pose SDFs) straight to
    # OUTPUT_DIR=OUT, which SageMaker uploads to S3.
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "wh",
                        "python", "nr4a3_warhead.py"], cwd=work, env=env)
    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] warhead exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
