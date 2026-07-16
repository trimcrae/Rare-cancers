#!/usr/bin/env python3
"""SageMaker Training entry for the ternary-cooperativity morph legs (OpenFE). Mirrors entry_rbfe.py exactly:
clone git_ref, build the SAME openfe conda env (openfe>=1.1 + NAGL charges + cuda-version pin), then run
nr4a3_ternary_fep.py for this (leg_id, direction, seed). Per-leg OpenFE results + checkpoints land in
/opt/ml/checkpoints (continuously synced → spot-safe; a re-dispatch with the same tag resumes). Inputs mounted:
data/<leg_id>/complex.pdb (assembled E3[+target]) + data/<leg_id>/ligands.sdf (posed PROTAC morph endpoints).
"""
import argparse
import os
import shutil
import subprocess
import sys

CKPT = "/opt/ml/checkpoints"
IN = "/opt/ml/input/data"
# Identical package set to entry_rbfe.OPENFE_PKGS (single source of truth for the openfe/openmm stack — the
# ternary morph uses the SAME RelativeHybridTopologyProtocol, so the env must not diverge).
OPENFE_PKGS = ["python=3.11", "openfe>=1.1", "pydantic>=2", "importlib_resources", "openff-toolkit",
               "ambertools>=23", "openmmforcefields", "openff-nagl", "openff-nagl-models", "ocl-icd-system",
               "cuda-version=12.6", "rdkit", "lomap2", "kartograf", "numpy", "scipy"]
# ambertools>=23 provides am1bcc (via antechamber/sqm) so binary + ternary legs share the SAME charge method
# (nr4a3_ternary_fep.py sets am1bcc; the coop cycle subtracts binary/ternary morphs so charges MUST match).


def _sh(cmd, **kw):
    print("[entry_tfep] $ %s" % " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=True, **kw)


def main():
    ap = argparse.ArgumentParser()
    for a in ("git-ref", "leg-id", "direction", "mode"):
        ap.add_argument("--%s" % a, default="")
    ap.add_argument("--n-windows", default="16")
    ap.add_argument("--n-iter", default="1000")
    ap.add_argument("--seed", default="0")
    ap.add_argument("--prebaked", default="0")
    args, _ = ap.parse_known_args()

    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"], check=False)
    _sh(["git", "clone", "--depth", "1", "--branch", args.git_ref or "main",
         "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"])
    work = "/tmp/repo/research/modalities"

    env = os.environ.copy()
    env.update({"CKPT_DIR": CKPT, "OUTPUT_DIR": CKPT, "INPUT_DIR": IN,
                "LEG_ID": args.leg_id or "nrv04_active_to_epimer__binary_vhl",
                "DIRECTION": args.direction or "fwd", "MODE": args.mode or "smoke",
                "N_WINDOWS": args.n_windows, "N_ITER": args.n_iter, "SEED": args.seed})
    os.makedirs(CKPT, exist_ok=True)

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    # OpenCL vendor ICD (same as entry_rbfe/entry_abfe) so OpenMM's OpenCL platform registers if CUDA can't load.
    subprocess.run(["bash", "-c", "mkdir -p /etc/OpenCL/vendors && "
                    "echo libnvidia-opencl.so.1 > /etc/OpenCL/vendors/nvidia.icd"], check=False)
    if args.prebaked == "1":
        env["PYTHONPATH"] = ""
        r = subprocess.run([conda, "run", "--no-capture-output", "-n", "rbfe", "python", "nr4a3_ternary_fep.py"],
                           cwd=work, env=env)
        sys.exit(r.returncode)

    subprocess.run([conda, "install", "-n", "base", "-y", "-c", "conda-forge", "conda-libmamba-solver"],
                   check=False)
    # Reuse the SAME env name 'rbfe' so a pre-baked RBFE image (build-fep-image.yml) serves both engines.
    create = [conda, "create", "-y", "-n", "rbfe", "-c", "conda-forge"] + OPENFE_PKGS
    try:
        _sh(create + ["--solver=libmamba"])
    except subprocess.CalledProcessError:
        print("[entry_tfep] libmamba unavailable; classic solver", flush=True)
        _sh(create)
    env["PYTHONPATH"] = ""      # clear so the base container numpy doesn't shadow the env's (abfe/fep lesson)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "rbfe", "python", "nr4a3_ternary_fep.py"],
                       cwd=work, env=env)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
