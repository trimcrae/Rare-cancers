#!/usr/bin/env python3
"""SageMaker entry for the warhead-pocket alanine scan (nr4a3_resistance_ddg.py). Same slim MM env as
entry_mmgbsa.py (openmm + pdbfixer + openff-toolkit-base, no nagl/pytorch), same nr4a3-matrix input mount
(receptors + docked poses). Mutates NR4A3 pocket residues -> Ala and re-scores denovo_401 by MM-GBSA. Per-
residue checkpoints stream to S3 (Continuous upload) so a timeout keeps completed mutants."""
import os
import shutil
import subprocess
import sys
import threading
import time

import sm_io
OUT = sm_io.out_dir()   # spot Training → /opt/ml/checkpoints (continuous S3 sync); Processing → legacy path


def _hb(label, start, stop, every):
    while not stop.wait(every):
        print(f"[hb] {label}: {int(time.time() - start)}s", flush=True)


def run_logged(cmd, label, timeout, heartbeat=30, check=True):
    print(f"[run] {label}: {' '.join(cmd)} (timeout {timeout}s)", flush=True)
    start = time.time(); stop = threading.Event()
    threading.Thread(target=_hb, args=(label, start, stop, heartbeat), daemon=True).start()
    try:
        return subprocess.run(cmd, check=check, timeout=timeout)
    finally:
        stop.set(); print(f"[run] {label}: {int(time.time() - start)}s", flush=True)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main")
    ap.add_argument("--compute-timeout", default="")
    ap.add_argument("--multisnapshot", default="1")
    ap.add_argument("--frames", default="")
    ap.add_argument("--pose-name", default="denovo_401")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"], check=False)
    run_logged(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], "git-clone", timeout=300)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    env_build_timeout = int(os.environ.get("ENV_BUILD_TIMEOUT", str(30 * 60)))
    run_logged([conda, "create", "-y", "-n", "mmg", "--override-channels", "-c", "conda-forge",
                "python=3.11", "openmm", "openmmforcefields", "openff-toolkit-base", "ambertools",
                "pdbfixer", "rdkit", "numpy", "ocl-icd-system"], "conda-create-mmg", timeout=env_build_timeout)
    # OpenCL vendor file so OpenMM's OpenCL platform registers the A10G (CUDA PTX is dead on this g5 image).
    subprocess.run(["bash", "-c", "mkdir -p /etc/OpenCL/vendors && "
                    "echo libnvidia-opencl.so.1 > /etc/OpenCL/vendors/nvidia.icd"], check=False)

    env = os.environ.copy()
    env["INPUT_DIR"] = sm_io.channel("matrix")   # the matrix set (was mounted at the Processing input root)
    env["OUTPUT_DIR"] = OUT
    env["MS"] = args.multisnapshot
    env["POSE_NAME"] = args.pose_name
    if args.frames:
        env["MS_FRAMES"] = args.frames
    present = sorted(os.listdir(env["INPUT_DIR"])) if os.path.isdir(env["INPUT_DIR"]) else []
    print(f"[sagemaker] mounted inputs: {present}; pose={args.pose_name} ms={args.multisnapshot}", flush=True)
    compute_timeout = int(args.compute_timeout or os.environ.get("COMPUTE_TIMEOUT", str(110 * 60)))
    rc = 0
    try:
        proc = subprocess.run([conda, "run", "--no-capture-output", "-n", "mmg",
                               "python", "-u", "nr4a3_resistance_ddg.py"], cwd=work, env=env,
                              timeout=compute_timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        print(f"[sagemaker] resistance compute TIMED OUT after {compute_timeout}s", flush=True); rc = 124
    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] resistance exit={rc}", flush=True)
    if rc != 0:
        sys.exit(rc)


if __name__ == "__main__":
    main()
