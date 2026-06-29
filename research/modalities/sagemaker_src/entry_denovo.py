#!/usr/bin/env python3
"""SageMaker entry for de-novo warhead GENERATION (nr4a3_denovo.py MODE=generate). GPU work.

One ProcessingInput (s3://<bucket>/nr4a3-matrix) is mounted at /opt/ml/processing/input — it holds the
opened NR4A3 conformer (nr4a3-opened.pdb) DiffSBDD conditions on. This builds the DiffSBDD env (the one
genuinely heavy stack: PyTorch + torch-geometric), clones the DiffSBDD repo + fetches its pretrained
checkpoint (both operator-provided via DIFFSBDD_REPO / DIFFSBDD_CKPT_URL — we do NOT hard-code a model
URL), runs the generation, and copies the SMILES pool (nr4a3-denovo-pool.json) + generated SDFs to S3.

GENERATION ONLY. The cheap screen (docking + developability + novelty) runs free on a GitHub CPU runner
(denovo-screen.yml), so the only GPU spend in the whole de-novo step is this one short sampling job.

Hardening carried over from the MM-GBSA run-7 incident (entry_mmgbsa.py): every long step streams live to
CloudWatch, prints an elapsed heartbeat, and has a hard wall-clock timeout, so a stalled env build / hung
sampler ends FAST and VISIBLY instead of burning to the cap in silence. A captured conda lock
(denovo-lock.txt) lets a future run pin the exact solve. If the DiffSBDD repo/checkpoint env vars are not
provided, generation is SKIPPED gracefully (the 'primed but skipped' pattern) rather than failing.
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


def run_logged(cmd, label, timeout, check=True, heartbeat=30):
    """Run `cmd` inheriting stdout/stderr (live CloudWatch), heartbeat every `heartbeat`s, hard `timeout`."""
    print(f"[run] {label}: {' '.join(cmd)} (timeout {timeout}s)", flush=True)
    start, stop = time.time(), threading.Event()
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
    ap.add_argument("--git-ref", default="main", help="repo ref to run; default main")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    run_logged(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], "git-clone", timeout=300)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    env_build_timeout = int(os.environ.get("ENV_BUILD_TIMEOUT", str(40 * 60)))
    # DiffSBDD needs PyTorch (GPU) + torch-geometric + the usual cheminformatics. Pin python; let the
    # CUDA-matched pytorch come from conda-forge/pytorch channels. Heartbeat + timeout bound a stalled solve.
    print(f"[sagemaker] creating DiffSBDD env via {conda}", flush=True)
    run_logged([conda, "create", "-y", "-n", "dn", "-c", "pytorch", "-c", "nvidia", "-c", "conda-forge",
                "python=3.10", "pytorch", "pytorch-cuda=12.1", "pytorch-scatter",
                "pyg", "rdkit", "openbabel", "biopython", "numpy", "scipy"],
               "conda-create-dn", timeout=env_build_timeout)

    try:
        lock = subprocess.run([conda, "list", "-n", "dn", "--explicit", "--md5"],
                              capture_output=True, text=True, check=True).stdout
        with open(os.path.join(OUT, "denovo-lock.txt"), "w") as fh:
            fh.write(lock)
        print(f"[sagemaker] captured conda lock ({lock.count(chr(10))} lines) -> denovo-lock.txt", flush=True)
    except Exception as e:  # noqa: BLE001 — best-effort
        print(f"[sagemaker] could not capture conda lock: {e}", flush=True)

    env = os.environ.copy()
    env["INPUT_DIR"] = "/opt/ml/processing/input"      # nr4a3-matrix outputs (nr4a3-opened.pdb)
    env["OUTPUT_DIR"] = OUT
    env["MODE"] = "generate"

    # Provision DiffSBDD (operator-provided; no hard-coded model URL). Absent -> generation skips gracefully.
    repo = os.environ.get("DIFFSBDD_REPO")
    ckpt_url = os.environ.get("DIFFSBDD_CKPT_URL")
    if repo:
        try:
            run_logged(["git", "clone", "--depth", "1", repo, "/tmp/diffsbdd"], "clone-diffsbdd", timeout=300)
            run_logged([conda, "run", "-n", "dn", "pip", "install", "-r",
                        "/tmp/diffsbdd/requirements.txt"], "pip-diffsbdd", timeout=20 * 60, check=False)
            env["DIFFSBDD_DIR"] = "/tmp/diffsbdd"
            if ckpt_url:
                ckpt = "/tmp/diffsbdd/checkpoint.ckpt"
                run_logged(["bash", "-c", f"curl -fsSL '{ckpt_url}' -o '{ckpt}'"], "fetch-ckpt", timeout=600)
                env["DIFFSBDD_CKPT"] = ckpt
        except Exception as e:  # noqa: BLE001 — provisioning failure -> graceful skip in the driver
            print(f"[sagemaker] DiffSBDD provisioning failed ({e}); generation will skip", flush=True)
    else:
        print("[sagemaker] DIFFSBDD_REPO not set — generation will SKIP (primed-but-idle).", flush=True)

    compute_timeout = int(os.environ.get("COMPUTE_TIMEOUT", str(90 * 60)))
    rc = 0
    try:
        proc = subprocess.run([conda, "run", "--no-capture-output", "-n", "dn",
                               "python", "-u", "nr4a3_denovo.py"], cwd=work, env=env,
                              timeout=compute_timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        print(f"[sagemaker] generation TIMED OUT after {compute_timeout}s", flush=True)
        rc = 124

    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] denovo-generate exit={rc}", flush=True)
    if rc != 0:
        sys.exit(rc)


if __name__ == "__main__":
    main()
