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
        print(f"[fep] real mode — building FEP env via {conda}", flush=True)
        # numpy>=2 REQUIRED: the MD stack (a pymbar/openmmtools dep) accesses numpy.dtypes.StringDType,
        # which only exists in numpy >= 2.0. An unpinned solve picked numpy 1.x and the real-MD path died
        # with "module 'numpy.dtypes' has no attribute 'StringDType'" (the smoke path skips this env, so it
        # did not catch it). Pin >=2 so conda-forge solves a consistent, importable stack.
        subprocess.run([conda, "create", "-y", "-n", "fep", "--override-channels", "-c", "conda-forge",
                        "python=3.11", "openmm", "openmmtools", "openmmforcefields",
                        "openff-toolkit-base", "pymbar", "mdtraj", "rdkit", "pdbfixer", "ambertools",
                        "ocl-icd-system", "numpy>=2"], check=True)
        # CRITICAL isolation fix: the SageMaker PyTorch base container sets PYTHONPATH to its OWN
        # site-packages (numpy 1.x). `conda run -n fep` inherits that PYTHONPATH, so `import numpy` inside
        # the fep env resolved the BASE numpy 1.x (which lacks numpy.dtypes.StringDType) instead of the
        # fep env's numpy 2.x — the real cause of the "StringDType" failure (the env itself has numpy 2,
        # forced by scipy 1.17 / pandas 2.3). Clear PYTHONPATH so the fep env uses only its own packages;
        # nr4a3_fep.py still imports its local modules via cwd (sys.path[0]).
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
