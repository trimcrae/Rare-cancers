#!/usr/bin/env python3
"""SageMaker entry for the fpocket calibration panel (CPU work, fetches structures from AFDB + RCSB).

Builds an isolated conda env with fpocket, runs nr4a3_calibration.py (which downloads the NR-LBD panel
and scores every structure), and copies nr4a3-calibration.json to /opt/ml/processing/output for S3.
No GPU/CUDA. No ProcessingInput — the panel is fetched from the public AFDB/RCSB at runtime.
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
    ap.add_argument("--git-ref", default="main", help="repo ref to run; default main")
    args = ap.parse_args()

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating fpocket env via {conda}", flush=True)
    subprocess.run([conda, "create", "-y", "-n", "cal", "-c", "conda-forge",
                    "python=3.11", "fpocket=4.2.3"], check=True)

    env = os.environ.copy()
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running fpocket calibration panel (ref {args.git_ref})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "cal",
                        "python", "nr4a3_calibration.py"], cwd=work, env=env)

    src = os.path.join(work, "nr4a3-calibration.json")
    if os.path.exists(src):
        shutil.copy(src, os.path.join(OUT, "nr4a3-calibration.json"))
        print(f"[sagemaker] saved nr4a3-calibration.json ({os.path.getsize(src)} bytes)", flush=True)
    print(f"[sagemaker] calibration exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
