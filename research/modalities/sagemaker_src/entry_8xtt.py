#!/usr/bin/env python3
"""SageMaker entry for the 8XTT benchmark (CPU work; fetches 8XTT from RCSB + AF-Q92570 from AFDB).

Builds an isolated conda env with fpocket + biopython, runs nr4a3_8xtt_benchmark.py (which downloads
8XTT's NMR ensemble + the AF2 model, maps numbering, runs fpocket per conformer, superposes, and writes
nr4a3-8xtt-benchmark.json), and copies the output to /opt/ml/processing/output for CONTINUOUS S3 upload.
No GPU/CUDA. No ProcessingInput — structures are fetched from public RCSB/AFDB at runtime.
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
    subprocess.run([conda, "create", "-y", "-n", "xtt", "-c", "conda-forge",
                    "python=3.11", "fpocket=4.2.3", "biopython"], check=True)

    env = os.environ.copy()
    env["OUTPUT_DIR"] = OUT                     # benchmark writes checkpoints straight to the S3-synced dir
    env["INPUT_DIR"] = "/opt/ml/processing/input"
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running 8XTT benchmark (ref {args.git_ref})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "xtt",
                        "python", "nr4a3_8xtt_benchmark.py"], cwd=work, env=env)

    src = os.path.join(OUT, "nr4a3-8xtt-benchmark.json")
    if os.path.exists(src):
        print(f"[sagemaker] nr4a3-8xtt-benchmark.json present ({os.path.getsize(src)} bytes)", flush=True)
    else:
        print("[sagemaker] WARNING: no benchmark JSON produced", flush=True)
    print(f"[sagemaker] 8XTT benchmark exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
