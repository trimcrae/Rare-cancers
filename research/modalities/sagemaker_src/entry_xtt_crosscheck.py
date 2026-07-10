#!/usr/bin/env python3
"""SageMaker entry for the AF2-model-vs-8XTT cross-check (CPU; fetches AFDB + RCSB at runtime).

Builds an isolated conda env with fpocket + Biopython + numpy, runs nr4a3_xtt_crosscheck.py (which
downloads the AF2 NR4A3 LBD model and the 8XTT solution-NMR ensemble, aligns numbering, computes
per-model backbone RMSD + per-model fpocket at Pocket-5 + maps the selectivity handles), and copies
nr4a3-xtt-crosscheck.json to /opt/ml/processing/output for S3. No GPU/CUDA. No ProcessingInput — both
structures are fetched from the public AFDB/RCSB at runtime (this container has open internet, unlike the
authoring session where RCSB is egress-blocked).
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
    print(f"[sagemaker] creating fpocket+biopython env via {conda}", flush=True)
    # fpocket from conda-forge; biopython for parsing/alignment/superposition; numpy for RMSD math.
    subprocess.run([conda, "create", "-y", "-n", "xtt", "-c", "conda-forge",
                    "python=3.11", "fpocket", "biopython", "numpy"], check=True)

    env = os.environ.copy()
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running 8XTT cross-check (ref {args.git_ref})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "xtt",
                        "python", "nr4a3_xtt_crosscheck.py"], cwd=work, env=env)

    src = os.path.join(work, "nr4a3-xtt-crosscheck.json")
    if os.path.exists(src):
        shutil.copy(src, os.path.join(OUT, "nr4a3-xtt-crosscheck.json"))
        print(f"[sagemaker] saved nr4a3-xtt-crosscheck.json ({os.path.getsize(src)} bytes)", flush=True)
    print(f"[sagemaker] cross-check exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
