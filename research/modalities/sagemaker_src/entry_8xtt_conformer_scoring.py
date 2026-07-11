#!/usr/bin/env python3
"""SageMaker entry for the 8XTT conformer-ensemble endpoint scoring (nr4a3_8xtt_conformer_scoring.py). GPU.

Docks denovo_401 + a decoy subset into EACH of the ~20 deposited 8XTT NMR conformers, MM-GBSA endpoint-scores
each pose, and per conformer ranks denovo_401 against the decoy endpoint-score null. NO extra input channels:
8XTT (RCSB) + AF-Q92570 (AFDB, reference sequence only) are fetched at runtime; there are no paralogue
receptors and no re-dock margins to mount (this scores the endpoint ΔG, not a selectivity margin).

Env = the SLIM MM-GBSA env (openmm/openmmforcefields/openff-toolkit-base/ambertools/pdbfixer/rdkit + the
OpenCL ICD fix) PLUS `smina` (docking into the 8XTT receptors) and `biopython` (the UniProt<->8XTT numbering
map) — IDENTICAL to entry_8xtt_redock.py / entry_8xtt_decoy_null.py so the endpoint scoring is matched.
Spot Training: /opt/ml/checkpoints is the output AND resume dir (continuous S3 sync); the per-(conformer,
ligand) JSON survives a spot kill/timeout and a re-dispatch resumes from the last scored leg.
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
    ap.add_argument("--models", default="", help="8XTT conformers to score ('all' default = every model)")
    ap.add_argument("--decoy-count", default="", help="decoys per conformer (default 15)")
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
                "pdbfixer", "rdkit", "biopython", "numpy", "ocl-icd-system"],
               "conda-create-rd", timeout=env_build_timeout)

    # OpenCL vendor ICD (same g5 fix as entry_mmgbsa.py) so OpenMM's OpenCL platform registers on the A10G.
    subprocess.run(["bash", "-c", "mkdir -p /etc/OpenCL/vendors && "
                    "echo libnvidia-opencl.so.1 > /etc/OpenCL/vendors/nvidia.icd && "
                    "ls -l /etc/OpenCL/vendors/"], check=False)

    import smina_env
    smina_env.setup_smina_env(conda)     # smina no longer co-solves with rdkit -> own env + wrapper

    env = os.environ.copy()
    env["PATH"] = smina_env.path_with_wrapper(env)          # make the smina wrapper discoverable
    env["OUTPUT_DIR"] = OUT                            # spot checkpoint dir == output (continuous sync)
    if args.models:
        env["MODELS"] = args.models
    if args.decoy_count:
        env["DECOY_COUNT"] = args.decoy_count
    print(f"[sagemaker] running 8XTT conformer scoring (ref {args.git_ref}, models {args.models or 'all'}, "
          f"decoys {args.decoy_count or '15'})", flush=True)
    compute_timeout = int(args.compute_timeout or os.environ.get("COMPUTE_TIMEOUT", str(11 * 60 * 60)))
    rc = 0
    try:
        proc = subprocess.run([conda, "run", "--no-capture-output", "-n", "rd",
                               "python", "-u", "nr4a3_8xtt_conformer_scoring.py"], cwd=work, env=env,
                              timeout=compute_timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        print(f"[sagemaker] conformer-scoring compute TIMED OUT after {compute_timeout}s "
              "(checkpoint holds the partial; re-dispatch to resume)", flush=True)
        rc = 124

    for f in sorted(os.listdir(OUT)):
        try:
            print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
        except OSError:
            pass
    print(f"[sagemaker] conformer-scoring exit={rc}", flush=True)
    if rc != 0:
        sys.exit(rc)


if __name__ == "__main__":
    main()
