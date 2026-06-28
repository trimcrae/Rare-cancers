#!/usr/bin/env python3
"""SageMaker entry for the MM-GBSA endpoint rescoring (nr4a3_mmgbsa.py). CPU work, no MD.

One ProcessingInput (s3://<bucket>/nr4a3-matrix) is mounted at /opt/ml/processing/input — it holds the
matrix job's receptors (<tag>-opened.pdb), docked poses (docked_<tag>.sdf) and nr4a3-matrix.json. Builds a
SLIM, CONTINUOUSLY-LOGGED MM env, runs nr4a3_mmgbsa.py, and copies nr4a3-mmgbsa.json (+ the sysgen cache
+ a captured conda lock) to S3.

Two hard lessons from run 7 (which hung 82 min in the env build, silently, and had to be KILLED to diagnose)
are baked in here:
  * SLIM ENV. We install `openff-toolkit-base`, NOT the `openff-toolkit` metapackage. The metapackage pulls
    `openff-nagl`, which depends on the full multi-GB PyTorch-CUDA stack (pytorch + triton + nccl + cuda
    libs) — none of which MM-GBSA uses. That bloat is what stalled the unpinned build. AM1-BCC charges for
    the gaff-2.11 ligand FF come from AmberTools `sqm`, which needs no nagl, so nothing is lost.
  * NEVER GO BLIND. Every long step (`run_logged`) streams its child stdout live to CloudWatch, prints an
    elapsed-time heartbeat, and is wrapped in a hard wall-clock timeout, so a hang ends FAST and VISIBLY
    instead of burning to the 4 h cap in silence. Tail a *running* job any time with tail-cloudwatch-aws.yml.
"""
import os
import shutil
import subprocess
import sys
import threading
import time

OUT = "/opt/ml/processing/output"


def _heartbeat(label, start, stop, every):
    while not stop.wait(every):
        print(f"[hb] {label}: still running, {int(time.time() - start)}s elapsed", flush=True)


def run_logged(cmd, label, timeout, heartbeat=30, check=True):
    """Run `cmd` inheriting stdout/stderr (so the child streams live to CloudWatch), print an elapsed-time
    heartbeat every `heartbeat`s, and enforce a hard `timeout`. On timeout: kill + raise TimeoutExpired so
    the job ends fast and visibly. Returns the CompletedProcess on success."""
    print(f"[run] {label}: {' '.join(cmd)} (timeout {timeout}s)", flush=True)
    start = time.time()
    stop = threading.Event()
    hb = threading.Thread(target=_heartbeat, args=(label, start, stop, heartbeat), daemon=True)
    hb.start()
    try:
        return subprocess.run(cmd, check=check, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"[run] {label}: TIMED OUT after {timeout}s — aborting so the job fails fast, not silent.",
              flush=True)
        raise
    finally:
        stop.set()
        print(f"[run] {label}: returned after {int(time.time() - start)}s", flush=True)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main", help="repo ref to run; default main")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    run_logged(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], "git-clone", timeout=300)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    env_build_timeout = int(os.environ.get("ENV_BUILD_TIMEOUT", str(30 * 60)))
    print(f"[sagemaker] creating SLIM mmgbsa env via {conda} "
          f"(openff-toolkit-base, no nagl/pytorch)", flush=True)
    # --override-channels keeps the solve on conda-forge only (no defaults mixing). libmamba is conda's
    # default solver (fast, reliable). Heartbeat + timeout so a stalled build is seen and bounded.
    # ocl-icd-system: the OpenCL ICD loader, bridged to the instance's NVIDIA OpenCL driver. Run 9 proved
    # CUDA is dead on the g5 (PTX mismatch) AND OpenCL was "not registered" — because slimming the env
    # dropped the ICD that run 7's bloated env happened to carry. OpenMM's OpenCL platform needs libOpenCL
    # at runtime to register; with it present, OpenCL runs on the A10G and sidesteps the CUDA PTX problem.
    run_logged([conda, "create", "-y", "-n", "mmg", "--override-channels", "-c", "conda-forge",
                "python=3.11", "openmm", "openmmforcefields", "openff-toolkit-base", "ambertools",
                "pdbfixer", "rdkit", "numpy", "ocl-icd-system"], "conda-create-mmg", timeout=env_build_timeout)

    # Capture an EXACT lockfile of what just solved, for free — a future run can pin to it for full
    # reproducibility (`conda create --file mmg-lock.txt`) instead of re-rolling the conda-forge dice.
    try:
        lock = subprocess.run([conda, "list", "-n", "mmg", "--explicit", "--md5"],
                              capture_output=True, text=True, check=True).stdout
        with open(os.path.join(OUT, "mmg-lock.txt"), "w") as fh:
            fh.write(lock)
        print(f"[sagemaker] captured conda lock ({lock.count(chr(10))} lines) -> mmg-lock.txt", flush=True)
    except Exception as e:  # noqa: BLE001 — lock capture is best-effort, never fail the run on it
        print(f"[sagemaker] could not capture conda lock: {e}", flush=True)

    # Run 10: ocl-icd-system (the ICD *loader*) still left OpenCL "not registered". The g5 container mounts
    # NVIDIA's OpenCL driver (libnvidia-opencl.so.1) but NOT its ICD *vendor file*, so the loader finds no
    # device and OpenMM's OpenCL platform never registers. Write the vendor file so the loader sees the A10G.
    subprocess.run(["bash", "-c", "mkdir -p /etc/OpenCL/vendors && "
                    "echo libnvidia-opencl.so.1 > /etc/OpenCL/vendors/nvidia.icd && "
                    "echo '[sagemaker] wrote /etc/OpenCL/vendors/nvidia.icd' && "
                    "ls -l /etc/OpenCL/vendors/"], check=False)

    env = os.environ.copy()
    env["INPUT_DIR"] = "/opt/ml/processing/input"     # nr4a3-matrix outputs mounted here
    env["OUTPUT_DIR"] = OUT
    present = sorted(f for f in os.listdir(env["INPUT_DIR"])) if os.path.isdir(env["INPUT_DIR"]) else []
    print(f"[sagemaker] mounted matrix inputs: {present}", flush=True)
    print(f"[sagemaker] running MM-GBSA rescoring (ref {args.git_ref})", flush=True)
    # 30 min: a GPU run of 13x3 endpoint MM-GBSA is minutes. There is no CPU fallback (nr4a3_mmgbsa.py
    # fails fast if no GPU platform loads), so a run that drags past this is a real problem, not slow CPU.
    compute_timeout = int(os.environ.get("COMPUTE_TIMEOUT", str(30 * 60)))
    rc = 0
    try:
        # `python -u` => unbuffered child stdout (per-ligand progress streams live, not at process exit).
        proc = subprocess.run([conda, "run", "--no-capture-output", "-n", "mmg",
                               "python", "-u", "nr4a3_mmgbsa.py"], cwd=work, env=env,
                              timeout=compute_timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        print(f"[sagemaker] mmgbsa compute TIMED OUT after {compute_timeout}s", flush=True)
        rc = 124

    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] mmgbsa exit={rc}", flush=True)
    if rc != 0:
        sys.exit(rc)


if __name__ == "__main__":
    main()
