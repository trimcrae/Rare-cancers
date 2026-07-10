#!/usr/bin/env python3
"""SageMaker entry for the 8XTT re-dock + MM-GBSA of denovo_401 (nr4a3_8xtt_redock.py). GPU work.

Docks the carried lead denovo_401 into the druggable EXPERIMENTAL 8XTT conformers and MM-GBSA-rescores,
reusing the matrix NR4A1/NR4A2 receptors+poses (mounted as the `matrix` Training channel) as the paralogue
baseline, to test whether the NR4A3-vs-paralogue selectivity survives on experimental geometry.

Env = the SLIM MM-GBSA env (entry_mmgbsa.py: openmm/openmmforcefields/openff-toolkit-base/ambertools/
pdbfixer/rdkit + the OpenCL ICD fix) PLUS `smina` (docking into the 8XTT conformers) and `biopython` (the
UniProt<->8XTT numbering map + the paralogue-mapping fallback). Spot Training: /opt/ml/checkpoints is the
output AND resume dir (continuous S3 sync); the per-conformer JSON checkpoint survives a spot kill/timeout.
8XTT + AF-Q92570 are fetched from RCSB/AFDB at runtime.
"""
import os
import shutil
import subprocess
import sys
import threading
import time

OUT = os.environ.get("SM_CHECKPOINT_DIR",
                     "/opt/ml/checkpoints" if os.path.isdir("/opt/ml/checkpoints")
                     else "/opt/ml/processing/output")


def _heartbeat(label, start, stop, every):
    while not stop.wait(every):
        print(f"[hb] {label}: still running, {int(time.time() - start)}s elapsed", flush=True)


def run_logged(cmd, label, timeout, heartbeat=30, check=True):
    print(f"[run] {label}: {' '.join(cmd)} (timeout {timeout}s)", flush=True)
    start = time.time()
    stop = threading.Event()
    threading.Thread(target=_heartbeat, args=(label, start, stop, heartbeat), daemon=True).start()
    try:
        return subprocess.run(cmd, check=check, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"[run] {label}: TIMED OUT after {timeout}s — aborting fast, not silent.", flush=True)
        raise
    finally:
        stop.set()
        print(f"[run] {label}: returned after {int(time.time() - start)}s", flush=True)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main")
    ap.add_argument("--models", default="", help="8XTT conformers to dock into (default '2,8,20,6')")
    ap.add_argument("--compute-timeout", default="", help="overall compute wall-clock seconds")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    run_logged(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], "git-clone", timeout=300)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    env_build_timeout = int(os.environ.get("ENV_BUILD_TIMEOUT", str(35 * 60)))
    print(f"[sagemaker] creating SLIM mm+dock env via {conda} (mmgbsa stack + smina + biopython)",
          flush=True)
    run_logged([conda, "create", "-y", "-n", "rd", "--override-channels", "-c", "conda-forge",
                "python=3.11", "openmm", "openmmforcefields", "openff-toolkit-base", "ambertools",
                "pdbfixer", "rdkit", "smina", "biopython", "numpy", "ocl-icd-system"],
               "conda-create-rd", timeout=env_build_timeout)

    # OpenCL vendor ICD (same g5 fix as entry_mmgbsa.py) so OpenMM's OpenCL platform registers on the A10G.
    subprocess.run(["bash", "-c", "mkdir -p /etc/OpenCL/vendors && "
                    "echo libnvidia-opencl.so.1 > /etc/OpenCL/vendors/nvidia.icd && "
                    "ls -l /etc/OpenCL/vendors/"], check=False)

    env = os.environ.copy()
    env["MATRIX_DIR"] = os.environ.get("SM_CHANNEL_MATRIX", "/opt/ml/processing/input/matrix")
    env["OUTPUT_DIR"] = OUT                            # spot checkpoint dir == output (continuous sync)
    if args.models:
        env["MODELS"] = args.models
    present = sorted(os.listdir(env["MATRIX_DIR"])) if os.path.isdir(env["MATRIX_DIR"]) else []
    print(f"[sagemaker] mounted matrix inputs: {present}", flush=True)
    print(f"[sagemaker] running 8XTT re-dock (ref {args.git_ref}, models {args.models or '2,8,20,6'})",
          flush=True)
    compute_timeout = int(args.compute_timeout or os.environ.get("COMPUTE_TIMEOUT", str(60 * 60)))
    rc = 0
    try:
        proc = subprocess.run([conda, "run", "--no-capture-output", "-n", "rd",
                               "python", "-u", "nr4a3_8xtt_redock.py"], cwd=work, env=env,
                              timeout=compute_timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        print(f"[sagemaker] redock compute TIMED OUT after {compute_timeout}s", flush=True)
        rc = 124

    for f in sorted(os.listdir(OUT)):
        try:
            print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
        except OSError:
            pass
    print(f"[sagemaker] redock exit={rc}", flush=True)
    if rc != 0:
        sys.exit(rc)


if __name__ == "__main__":
    main()
