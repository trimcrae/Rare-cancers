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
OPENFE_PKGS = ["python=3.11", "openfe>=1.1", "pydantic>=2", "importlib_resources", "openff-toolkit",
               "openmmforcefields", "openff-nagl", "openff-nagl-models", "rdkit", "lomap2", "kartograf",
               "numpy", "scipy"]


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

    subprocess.run(["nvidia-smi"], check=False)
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

    conda = shutil_which("conda") or "/opt/conda/bin/conda"
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


def shutil_which(x):
    import shutil
    return shutil.which(x)


if __name__ == "__main__":
    main()
