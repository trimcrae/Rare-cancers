#!/usr/bin/env python3
"""SageMaker entry — runs the EWSR1::NR4A3 fusion-junction apo co-fold inside the AWS GPU container.

Clones the repo (latest main), installs Boltz + its cuEquivariance accel stack, runs
fusion_cofold.py --run (two chimeric apo constructs: `seam` and `composite`), and copies the Boltz
outputs + input YAMLs + prep JSON to /opt/ml/processing/output, which SageMaker auto-uploads to S3
(Continuous mode → each finished construct survives a later timeout). SageMaker provisions the GPU,
enforces the hard MaxRuntime cap, and tears the instance down on completion.
"""
import argparse
import glob
import os
import shutil
import subprocess

import sm_io
OUT = sm_io.out_dir()   # spot Training → /opt/ml/checkpoints (continuous S3 sync); Processing → legacy path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", nargs="?", const=True, default=False,
                    help="no-op sentinel; keeps the SageMaker arg list non-empty")
    # parse_known_args + nargs="?": spot-Training hyperparameters turn a bare `--control` into `--control true`,
    # which a store_true flag rejects (the 2026-07-11 ternary smoke failure). Tolerate it here too.
    ap.parse_known_args()

    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    # boltz>=2 imports cuequivariance_torch in its triangular-mult kernel and hard-crashes if absent;
    # fusion_cofold.py runs with --no_kernels (pure-PyTorch path) but install the accel stack anyway.
    subprocess.run(["pip", "install", "--quiet", "boltz",
                    "cuequivariance-torch", "cuequivariance-ops-torch-cu12"], check=False)
    subprocess.run(["git", "clone", "--depth", "1",
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)

    work = "/tmp/repo/research/modalities"
    env = os.environ.copy()
    os.makedirs(OUT, exist_ok=True)
    env["OUTPUT_DIR"] = OUT     # Boltz outputs + prep JSON land in the Continuous-upload dir
    print("[sagemaker] running Boltz fusion-junction apo co-fold (seam + composite)", flush=True)
    r = subprocess.run(["python", "fusion_cofold.py", "--run"], cwd=work, env=env)

    # belt-and-braces: copy any YAML/prep left next to the code (back-compat)
    for p in glob.glob(os.path.join(work, "*.yaml")) + \
            glob.glob(os.path.join(work, "fusion-cofold-prep.json")):
        dst = os.path.join(OUT, os.path.basename(p))
        if not os.path.exists(dst):
            shutil.copy(p, dst)
    print(f"[sagemaker] cofold exit={r.returncode}", flush=True)
    if r.returncode != 0:
        raise SystemExit(r.returncode)


if __name__ == "__main__":
    main()
