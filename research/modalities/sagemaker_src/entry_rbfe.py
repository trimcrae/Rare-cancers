#!/usr/bin/env python3
"""SageMaker Training entry for the RBFE morph legs (OpenFE). Mirrors entry_abfe.py: clone git_ref, build the
openfe conda env (unless a pre-baked image is used), then run nr4a3_rbfe.py for this (receptor, leg). Per-leg
OpenFE results + checkpoints land in /opt/ml/checkpoints (continuously synced to checkpoint_s3_uri → spot-safe;
a re-dispatch with the same tag resumes). Inputs mounted: ligand/ (docked_<r>.sdf), receptor/ (<r>-opened.pdb).
"""
import argparse
import os
import subprocess
import sys

CKPT = "/opt/ml/checkpoints"
IN = "/opt/ml/input/data"
# openfe brings openmm + perses hybrid-topology + lomap + gufe; pinned loosely so the solve resolves a CUDA
# openmm. SHAKEOUT-PENDING: mode=smoke validates this solve before any MD spend.
# PIN a MODERN openfe (>=1.1, pydantic-v2 native, uses openfe.protocols.openmm_rfe). Without this, libmamba
# resolved an OLD openfe (0.x, legacy setup.methods.openmm + pydantic-v1 Settings) against pydantic 2.11 → an
# import-time PydanticUserError. The classic solver happened to pick a modern openfe; the pin makes EITHER
# solver deterministic. pydantic>=2 is explicit for the same reason.
# openff-nagl + models: a GNN AM1-BCC surrogate for partial charges. OpenFE defaults to am1bcc, which needs
# OpenEye (unlicensed here) or a working AmberTools antechamber (fails in this env) — NAGL avoids both.
# cuda-version=12.6: the g5 driver (570.x) supports up to CUDA 12.8, but the default solve pulled an OpenMM CUDA
# runtime whose PTX is NEWER than 12.8 → CUDA_ERROR_UNSUPPORTED_PTX_VERSION (222) at Context load, forcing the
# pathologically-slow OpenCL hybrid-kernel JIT that wedged the complex legs (confirmed by mode=cudaprobe on
# 2026-07-08: driver 12.8, openmm 8.1.2, CUDA 222 → OpenCL). Pinning cuda-version ≤ driver makes NVRTC emit PTX
# the driver accepts, so the CUDA platform loads and the hybrid Context builds fast (no giant runtime compile).

# openfe>=1.12: the 3-unit split (HybridTopologySetupUnit / ...SimulationUnit / ...AnalysisUnit) that lets us run
# the CPU hybrid-system BUILD on cheap CPU and only the MD on GPU (2026-07-14). Older openfe was the MONOLITHIC
# RelativeHybridTopologyProtocolUnit (single unit, build+MD welded) — the version our earlier env resolved.
OPENFE_PKGS = ["python=3.11", "openfe>=1.12", "pydantic>=2", "importlib_resources", "openff-toolkit",
               "openmmforcefields", "openff-nagl", "openff-nagl-models", "ocl-icd-system", "cuda-version=12.6",
               "rdkit", "lomap2", "kartograf", "numpy", "scipy"]


def _sh(cmd, **kw):
    print(f"[entry_rbfe] $ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, check=True, **kw)


def main():
    ap = argparse.ArgumentParser()
    for a in ("git-ref", "ligand-a", "ligand-b", "receptor", "leg", "mode"):
        ap.add_argument(f"--{a}", default="")
    ap.add_argument("--n-windows", default="12")
    ap.add_argument("--n-iter", default="1000")
    ap.add_argument("--seed", default="0")
    ap.add_argument("--prebaked", default="0")
    args, _ = ap.parse_known_args()

    # nvidia-smi is absent on CPU instances (the split's setup/analyze jobs) — check=False suppresses non-zero
    # EXIT codes, NOT a missing binary (that raises FileNotFoundError). Guard it so CPU jobs don't crash at line 1.
    try:
        subprocess.run(["nvidia-smi"], check=False)
    except FileNotFoundError:
        print("[entry_rbfe] no nvidia-smi (CPU instance) — expected for setup/analyze", flush=True)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"], check=False)
    _sh(["git", "clone", "--depth", "1", "--branch", args.git_ref or "main",
         "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"])
    work = "/tmp/repo/research/modalities"

    env = os.environ.copy()
    env.update({"CKPT_DIR": CKPT, "OUTPUT_DIR": CKPT, "INPUT_DIR": IN,
                "LIGAND_A": args.ligand_a, "LIGAND_B": args.ligand_b, "RECEPTOR": args.receptor or "nr4a3",
                "LEG": args.leg or "complex", "MODE": args.mode or "smoke",
                "N_WINDOWS": args.n_windows, "N_ITER": args.n_iter, "SEED": args.seed})
    os.makedirs(CKPT, exist_ok=True)

    # === CKPT-RESTORE PROBE (2026-07-14 root-cause diagnostic) ===============================================
    # DEFINITIVE test of "did SageMaker restore the spot checkpoint to local disk?". Runs at container boot,
    # BEFORE the slow conda solve, so it prints within ~1 min. SageMaker downloads checkpoint_s3_uri ->
    # checkpoint_local_path (=/opt/ml/checkpoints=CKPT) during bootstrap, so whatever is here now is exactly
    # what OpenFE's _check_restart will see. It checks shared_path/output_filename + shared_path/
    # checkpoint_storage_filename (defaults simulation.nc / checkpoint.chk) under ctx.shared (= CKPT/sim_shared).
    # If those two files are ABSENT here but present in S3 -> restore/config bug; if PRESENT -> the bug is
    # downstream (filename/path/clearing). No dependency on the conda env — pure stdlib.
    try:
        print("[ckpt-restore-probe] ===== restored contents of %s (before conda) =====" % CKPT, flush=True)
        _n = 0
        for root, _dirs, files in os.walk(CKPT):
            for f in sorted(files):
                p = os.path.join(root, f)
                try:
                    st = os.stat(p)
                    print("[ckpt-restore-probe]   %10d B  %s" % (st.st_size, os.path.relpath(p, CKPT)), flush=True)
                except OSError:
                    pass
                _n += 1
        print("[ckpt-restore-probe] total files restored: %d" % _n, flush=True)
        for rel in ("sim_shared/simulation.nc", "sim_shared/checkpoint.chk"):
            fp = os.path.join(CKPT, rel)
            ok = os.path.isfile(fp)
            print("[ckpt-restore-probe]   _check_restart needs %-30s present=%s%s" % (
                rel, ok, (" size=%dB" % os.path.getsize(fp)) if ok else ""), flush=True)
    except Exception as e:  # noqa: BLE001
        print("[ckpt-restore-probe] probe error: %r" % e, flush=True)
    # =========================================================================================================

    # === CHECKPOINT-UPLOADER SIDECAR (2026-07-15 root-cause fix) ==============================================
    # DIAGNOSED: SageMaker does NOT push the checkpoint to S3 during a run — the complex leg's S3 checkpoint
    # stayed frozen at job-start (mtime 10:42Z) for ~3h while it ran through equilibration + production. So a spot
    # kill loses everything since job start (restore then brings iteration-0 -> re-equilibrate). FIX: upload the
    # sim_shared checkpoint files to S3 OURSELVES every few minutes (base env has boto3; runs as a daemon thread
    # alongside the MD), so a recent RESUMABLE checkpoint always exists in S3 -> a spot kill resumes losing at
    # most one upload interval. Gated on simulate (the only GPU/MD leg) + CKPT_S3_URI (passed by the submitter).
    if (args.mode or "") == "simulate" and os.environ.get("CKPT_S3_URI"):
        _start_ckpt_uploader(os.path.join(CKPT, "sim_shared"), os.environ["CKPT_S3_URI"],
                             int(os.environ.get("CKPT_UPLOAD_SECONDS", "300")))
    else:
        print("[ckpt-uploader] not started (mode=%s CKPT_S3_URI=%s)" % (
            args.mode, bool(os.environ.get("CKPT_S3_URI"))), flush=True)
    # =========================================================================================================

    conda = shutil_which("conda") or "/opt/conda/bin/conda"
    # OpenCL vendor ICD so OpenMM's OpenCL platform registers the A10G — the conda OpenMM CUDA build targets a
    # newer CUDA than the g5 driver supports (CUDA_ERROR_UNSUPPORTED_PTX_VERSION), so we run on OpenCL instead
    # (nr4a3_rbfe.py sets compute_platform=OpenCL). Same fix as entry_abfe.py / entry_fep.py.
    subprocess.run(["bash", "-c", "mkdir -p /etc/OpenCL/vendors && "
                    "echo libnvidia-opencl.so.1 > /etc/OpenCL/vendors/nvidia.icd"], check=False)
    if args.prebaked == "1":
        # pre-baked image already has the 'rbfe' env; skip the solve, run in it.
        env["PYTHONPATH"] = ""
        r = subprocess.run([conda, "run", "--no-capture-output", "-n", "rbfe", "python", "nr4a3_rbfe.py"],
                           cwd=work, env=env)
        sys.exit(r.returncode)

    # The classic conda solver takes ~50 min on the openfe dependency graph; libmamba solves the SAME packages
    # in ~5 min. Install the solver plugin (no-op if present) and try it, falling back to classic if unavailable.
    subprocess.run([conda, "install", "-n", "base", "-y", "-c", "conda-forge", "conda-libmamba-solver"],
                   check=False)
    create = [conda, "create", "-y", "-n", "rbfe", "-c", "conda-forge"] + OPENFE_PKGS
    try:
        _sh(create + ["--solver=libmamba"])
    except subprocess.CalledProcessError:
        print("[entry_rbfe] libmamba solver unavailable; falling back to classic solver", flush=True)
        _sh(create)
    # clear PYTHONPATH so the base container's numpy doesn't shadow the env's (the abfe/fep leak lesson).
    env["PYTHONPATH"] = ""
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "rbfe", "python", "nr4a3_rbfe.py"],
                       cwd=work, env=env)
    if r.returncode != 0:
        sys.exit(r.returncode)


def _start_ckpt_uploader(local_dir, s3_uri, interval_s=300):
    """Daemon thread: every interval_s, upload the sim_shared checkpoint files to S3 ourselves (SageMaker's own
    checkpoint sync does NOT push mid-run — verified by forensic). Guarantees a recent resumable checkpoint in
    S3 so a spot interruption resumes losing <= interval_s of MD instead of the whole leg. Best-effort; a failed
    upload just logs and retries next cycle. Uploads to the SAME prefix SageMaker restores from on start."""
    import threading
    import time as _t
    from urllib.parse import urlparse
    try:
        import boto3
    except Exception as e:  # noqa: BLE001
        print("[ckpt-uploader] boto3 unavailable (%r) — sidecar disabled; relying on SageMaker end-of-job sync"
              % e, flush=True)
        return
    u = urlparse(s3_uri)
    bucket, prefix = u.netloc, u.path.lstrip("/")            # prefix e.g. "<tag>/ckpt/<leg>/"
    dest = prefix + "sim_shared/"
    files = ("simulation.nc", "checkpoint.chk", "simulation_real_time_analysis.yaml")
    s3 = boto3.client("s3")

    def _loop():
        while True:
            _t.sleep(interval_s)
            up = []
            for fn in files:
                fp = os.path.join(local_dir, fn)
                if os.path.isfile(fp):
                    try:
                        s3.upload_file(fp, bucket, dest + fn)
                        up.append("%s(%dB)" % (fn, os.path.getsize(fp)))
                    except Exception as e:  # noqa: BLE001
                        print("[ckpt-uploader] upload %s failed: %r" % (fn, e), flush=True)
            stamp = _t.strftime("%H:%M:%SZ", _t.gmtime())
            print("[ckpt-uploader] %s -> s3://%s/%s  uploaded=[%s]" % (stamp, bucket, dest, ", ".join(up)),
                  flush=True)

    threading.Thread(target=_loop, daemon=True).start()
    print("[ckpt-uploader] STARTED: every %ds  %s -> s3://%s/%s" % (interval_s, local_dir, bucket, dest),
          flush=True)


def shutil_which(x):
    import shutil
    return shutil.which(x)


if __name__ == "__main__":
    main()
