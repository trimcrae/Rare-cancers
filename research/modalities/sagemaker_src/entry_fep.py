#!/usr/bin/env python3
"""SageMaker managed-SPOT Training entry for one selectivity-FEP shard.

Runs inside a spot Training job launched by nr4a3_fep_sagemaker.py. Clones the repo, (for real mode) builds
the OpenMM/openmmtools env, points nr4a3_fep.py at the mounted shard + receptor/pose channels + the
continuously-synced checkpoint dir, and runs the shard. Because per-unit results are written into
/opt/ml/checkpoints (synced to checkpoint_s3_uri), a spot interruption + automatic retry RESUMES from the last
completed window rather than restarting the shard.

Channels (SM_CHANNEL_*): shard (the units JSON) [, receptor, poses for real mode].
Hyperparameters: --git-ref, --smoke (0/1), --ligand, --prod-ps, --equil-ps.
"""
import argparse
import os
import shutil
import subprocess
import sys

CKPT = os.environ.get("FEP_CHECKPOINT_DIR", "/opt/ml/checkpoints")


def ch(name):
    return os.environ.get(f"SM_CHANNEL_{name.upper()}", f"/opt/ml/input/data/{name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main")
    ap.add_argument("--smoke", default="0")
    ap.add_argument("--ligand", default="denovo_401")
    ap.add_argument("--prod-ps", default="1000")
    ap.add_argument("--equil-ps", default="200")
    ap.add_argument("--phase", default="full")          # bootstrap (on-demand) | sample (spot) | full (legacy)
    ap.add_argument("--bootstrap-iter", default="60")
    a = ap.parse_args()
    smoke = a.smoke == "1"

    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"], check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", a.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    os.makedirs(CKPT, exist_ok=True)
    env = os.environ.copy()
    env["FEP_CHECKPOINT_DIR"] = CKPT
    env["FEP_LIGAND"] = a.ligand
    env["FEP_PROD_PS"] = a.prod_ps
    env["FEP_EQUIL_PS"] = a.equil_ps
    env["FEP_PHASE"] = a.phase                           # bootstrap on-demand → sample on spot (trailblaze-safe)
    env["FEP_BOOTSTRAP_ITER"] = a.bootstrap_iter
    # the shard channel holds exactly one <shard>.json
    shard_dir = ch("shard")
    shard_files = [f for f in os.listdir(shard_dir) if f.endswith(".json")] if os.path.isdir(shard_dir) else []
    if not shard_files:
        sys.exit(f"[fep] no shard json in channel {shard_dir}")
    env["FEP_SHARD_FILE"] = os.path.join(shard_dir, shard_files[0])

    runner = ["python", "nr4a3_fep.py"] + (["--smoke"] if smoke else [])
    if smoke:
        print("[fep] SMOKE mode — validating spot/checkpoint/resume plumbing (no MD, no heavy env)", flush=True)
        r = subprocess.run(runner, cwd=work, env=env)
    else:
        env["FEP_RECEPTOR_DIR"] = ch("receptor")
        env["FEP_POSE_DIR"] = ch("poses")
        conda = shutil.which("conda") or "/opt/conda/bin/conda"
        print(f"[fep] real mode — building Yank FEP env via {conda}", flush=True)
        # The physics is Yank (absolute-binding FEP: explicit solvent, Boresch restraints + standard-state
        # correction, HREX, MBAR). PIN openmmtools=0.21.2: yank 0.25.2 calls the private
        # openmmtools.alchemy._ALCHEMICAL_REGION_ARGS, REMOVED in openmmtools 0.25 (which conda-forge's loose
        # yank pin otherwise co-installs → runtime AttributeError at alchemy setup, invisible to an import
        # check). yank-env-check.yml confirmed 0.21.2 has the attr and solves with openmm 8.3.1 / numpy 1.26 /
        # python 3.9. ocl-icd-system + the nvidia.icd vendor file below let OpenMM's OpenCL platform register
        # the A10G (CUDA PTX is dead on this g5 image).
        # PINS for the unmaintained yank 0.25.2 (2020) on a modern solve — each verified by a failed shard:
        #   python=3.9      : yank uses legacy `collections.MutableMapping`, REMOVED in py3.10 (openbabel/
        #                     setuptools otherwise pulled py3.10+). 3.9 is also what yank-env-check resolved.
        #   openmmtools=0.21.2: yank needs alchemy._ALCHEMICAL_REGION_ARGS, gone in 0.25.
        #   setuptools<81   : yank imports pkg_resources, removed in setuptools>=81 (openbabel bumped it past).
        #   openbabel       : adds explicit H to the heavy-atom docked pose before antechamber.
        #   netcdf4<1.6 / libnetcdf<4.9 : openmmtools 0.21.2's MultiStateReporter writes its .nc with the old
        #     compression-filter API; libnetcdf 4.9.x (which the loose solve pulled, via netcdf4 1.7.2) rejects
        #     it with "NetCDF: Filter error: bad id or parameters or duplicate filter" at _store_options —
        #     the FIRST thing the sampler does, so it fails before any MD (masked earlier only because
        #     auto-trailblaze never finished). Pinning to the 4.8.x/1.5.x era yank was built against fixes it.
        subprocess.run([conda, "create", "-y", "-n", "fep", "--override-channels", "-c", "conda-forge",
                        "python=3.9", "yank", "openmmtools=0.21.2", "ocl-icd-system", "openbabel",
                        "setuptools<81", "netcdf4=1.5.8", "libnetcdf=4.8.1"], check=True)
        subprocess.run(["bash", "-c", "mkdir -p /etc/OpenCL/vendors && "
                        "echo libnvidia-opencl.so.1 > /etc/OpenCL/vendors/nvidia.icd"], check=False)
        # CRITICAL isolation fix (2026-07-03): the SageMaker PyTorch base container sets PYTHONPATH to its own
        # site-packages; `conda run -n fep` inherits it, so `import numpy` resolved the BASE numpy 1.x instead
        # of the fep env's numpy — the "numpy.dtypes has no attribute StringDType" failure. Clear PYTHONPATH so
        # the fep env uses only its own packages; nr4a3_fep.py still imports local modules via cwd (sys.path[0]).
        fep_env = dict(env)
        fep_env["PYTHONPATH"] = ""
        r = subprocess.run([conda, "run", "--no-capture-output", "-n", "fep"] + runner,
                           cwd=work, env=fep_env)

    # per-unit results already live in CKPT (synced continuously). Copy a manifest to the model dir too.
    model_dir = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
    os.makedirs(model_dir, exist_ok=True)
    try:
        for f in os.listdir(CKPT):
            if f.endswith(".json"):
                shutil.copy(os.path.join(CKPT, f), os.path.join(model_dir, f))
    except Exception as e:  # noqa: BLE001
        print(f"[fep] (manifest copy skipped: {e})", flush=True)
    print(f"[fep] shard exit={r.returncode}", flush=True)
    if r.returncode != 0:
        raise SystemExit(r.returncode)


if __name__ == "__main__":
    main()
