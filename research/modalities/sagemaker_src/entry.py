#!/usr/bin/env python3
"""SageMaker entry script — runs inside the AWS-managed GPU container.

Clones the repo (latest main), runs the OpenMM MD (nr4a3_md.py), and copies outputs to
/opt/ml/processing/output, which SageMaker auto-uploads to S3 when the job finishes. SageMaker
provisions the GPU, enforces the hard MaxRuntime cap, and tears the instance down on completion —
nothing to shut off manually.
"""
import argparse
import os
import shutil
import subprocess
import sys

import sm_io
OUT = sm_io.out_dir()   # spot Training → /opt/ml/checkpoints (continuous S3 sync); Processing → legacy path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", default="10")
    ns = ap.parse_args().ns

    subprocess.run(["nvidia-smi"], check=False)  # confirm GPU attached
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1",
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)

    work = "/tmp/repo/research/modalities"

    # The pip OpenMM wheel ships without a working CUDA platform on this DLC, so the
    # MD aborts (OpenMM falls back to CPU). Install a CUDA-enabled OpenMM from
    # conda-forge into an isolated env — conda's __cuda virtual package pulls the
    # build matching the GPU driver — and run the MD with that env's python.
    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating conda env with CUDA OpenMM via {conda}", flush=True)
    create_env = os.environ.copy()
    # The Processing container doesn't expose the GPU driver to conda's solver, so
    # __cuda isn't auto-detected and conda would pick the CPU openmm build. Force the
    # CUDA virtual package so it resolves the driver-matched GPU build.
    create_env["CONDA_OVERRIDE_CUDA"] = "12.8"
    # Pin the CUDA runtime to the driver's version (the box driver is CUDA 12.8); without
    # this conda pulls cuda-nvrtc 12.9, which fails to init on a 12.8 driver -> CPU fallback.
    subprocess.run([conda, "create", "-y", "-n", "md", "-c", "conda-forge",
                    "python=3.11", "openmm", "pdbfixer", "cuda-version=12.8"],
                   check=True, env=create_env)
    subprocess.run([conda, "list", "-n", "md", "openmm"], check=False)  # log build str (cuda vs cpu)

    env = os.environ.copy()
    env["NS"] = ns
    print(f"[sagemaker] running MD for {ns} ns", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "md",
                        "python", "nr4a3_md.py"], cwd=work, env=env)

    os.makedirs(OUT, exist_ok=True)
    for f in ("AF-Q92570.pdb", "nr4a3-lbd-solvated.pdb", "nr4a3-lbd-md.dcd"):
        p = os.path.join(work, f)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(OUT, f))
            print(f"[sagemaker] saved {f} ({os.path.getsize(p)} bytes)", flush=True)
    print(f"[sagemaker] MD exit={r.returncode}", flush=True)
    if r.returncode != 0:
        # Fail the processing job so a broken MD can't masquerade as a green run.
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
