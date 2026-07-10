#!/usr/bin/env python3
"""SageMaker entry for the NR4A3 Gate-2 handle-facing confirmation (nr4a3_handle_facing.py). CPU work.

The metad outputs are mounted by ProcessingInput at /opt/ml/processing/input. We conda-install the
analysis stack (mdtraj + fpocket + matplotlib + numpy) and run nr4a3_handle_facing.py; SageMaker uploads
/opt/ml/processing/output (handle_facing_summary.json + plot) to S3 on completion. No GPU/CUDA here.
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
                    help="trajectory filename in the mounted input dir (the metad run by default)")
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
    env["INPUT_DIR"] = "/opt/ml/processing/input"
    env["OUTPUT_DIR"] = OUT
    env["DCD_NAME"] = args.dcd_name
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running handle-facing analysis on {args.dcd_name} (ref {args.git_ref})",
          flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "an",
                        "python", "nr4a3_handle_facing.py"], cwd=work, env=env)
    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] handle-facing exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
