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
OPENFE_PKGS = ["python=3.11", "openfe", "openff-toolkit", "openmmforcefields", "rdkit", "lomap2",
               "kartograf", "numpy", "scipy"]


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

    if args.prebaked == "1":
        # pre-baked image already has the openfe env active.
        r = subprocess.run([sys.executable, "nr4a3_rbfe.py"], cwd=work, env=env)
        sys.exit(r.returncode)

    conda = shutil_which("conda") or "/opt/conda/bin/conda"
    _sh([conda, "create", "-y", "-n", "rbfe", "-c", "conda-forge"] + OPENFE_PKGS)
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
