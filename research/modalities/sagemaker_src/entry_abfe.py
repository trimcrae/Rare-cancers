#!/usr/bin/env python3
"""SageMaker managed-SPOT Training entry for the MODERN independent-window ABFE (replaces entry_fep.py / Yank).

One spot Training job runs ONE (receptor, leg) shard = its λ-windows for that leg, via nr4a3_abfe.run_shard.
Each window checkpoints its OpenMM State + per-iteration reduced-potential jsonl into /opt/ml/checkpoints
(synced to checkpoint_s3_uri), so a spot interruption + retry RESUMES each window from its last iteration
(≤1 iter lost) — the whole point of the independent-window design vs Yank's monolithic HREX .nc.

Modes (hyperparameter --mode):
  smoke  : run `nr4a3_abfe.py --smoke` in the modern env — validates spot/checkpoint plumbing + the engine's
           core loop (build→MD→reduced-potentials→checkpoint→resume→MBAR) with NO receptor, NO heavy prep deps.
  run    : prepare the leg (receptor PDB + ligand SDF channels) and run its windows → /opt/ml/checkpoints.
  reduce : MBAR-combine the complex+solvent legs (mounted as channels) → ΔG_bind json in the model dir. CPU.

Channels (SM_CHANNEL_*): ligand (SDF) [, receptor (PDB) for complex run] [, complex+solvent dirs for reduce].
Hyperparameters: --git-ref --mode --receptor --leg --ligand-name --window-start --window-end --n-iter
                 --steps-per-iter --platform --prebaked.
"""
import argparse
import os
import shutil
import subprocess
import sys

CKPT = os.environ.get("ABFE_CHECKPOINT_DIR", "/opt/ml/checkpoints")
MODERN_PKGS = ["python=3.11", "openmm", "openmmtools", "pymbar>=4",
               "openmmforcefields", "openff-toolkit", "pdbfixer", "mdtraj"]


def ch(name):
    return os.environ.get(f"SM_CHANNEL_{name.upper()}", f"/opt/ml/input/data/{name}")


def _first(dirpath, suffix, prefer=None):
    """First file in dirpath ending in `suffix`. If `prefer` (e.g. the receptor token) is given, a filename
    containing it wins — the matrix prefix holds all receptors' <r>-opened.pdb / docked_<r>.sdf, so we must
    pick the one for THIS receptor rather than whichever sorts first."""
    if not os.path.isdir(dirpath):
        return None
    files = [f for f in sorted(os.listdir(dirpath)) if f.endswith(suffix)]
    if prefer:
        pref = [f for f in files if prefer in f]
        if pref:
            return os.path.join(dirpath, pref[0])
    return os.path.join(dirpath, files[0]) if files else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main")
    ap.add_argument("--mode", default="smoke")            # smoke | run | reduce
    ap.add_argument("--receptor", default="nr4a3")        # nr4a3 | nr4a1 | nr4a2
    ap.add_argument("--leg", default="complex")           # complex | solvent
    ap.add_argument("--ligand-name", default="denovo_401")
    ap.add_argument("--window-start", default="0")
    ap.add_argument("--window-end", default="")           # "" → all N_WINDOWS
    ap.add_argument("--n-iter", default="1000")
    ap.add_argument("--steps-per-iter", default="500")
    ap.add_argument("--platform", default="CUDA")
    ap.add_argument("--prebaked", default="0")            # 1 → skip conda create (image has env `abfe`)
    a = ap.parse_args()

    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"], check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", a.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"
    os.makedirs(CKPT, exist_ok=True)

    # SMOKE: modern env + engine core loop; no receptor, no prep deps needed — but the env still solves so we
    # also prove the modern solve. Run in the same env we'd use for real (so a solve break is caught here).
    if a.mode == "smoke":
        base = ["python", "nr4a3_abfe.py", "--smoke"]
        rc = _run_in_env(base, work, a.prebaked == "1")
        _copy_manifest()
        print(f"[abfe] smoke exit={rc}", flush=True)
        raise SystemExit(rc)

    if a.mode == "reduce":
        out_json = os.path.join(os.environ.get("SM_MODEL_DIR", "/opt/ml/model"), f"{a.receptor}_dg_bind.json")
        cmd = ["python", "nr4a3_abfe.py", "--reduce",
               "--complex-dir", ch("complex"), "--solvent-dir", ch("solvent"), "--out-json", out_json]
        rc = _run_in_env(cmd, work, a.prebaked == "1")
        print(f"[abfe] reduce exit={rc}", flush=True)
        raise SystemExit(rc)

    # RUN: prepare the leg + run its windows. out_dir = the synced checkpoint dir (per receptor/leg).
    out_dir = os.path.join(CKPT, a.receptor, a.leg)
    lig_sdf = _first(ch("ligand"), ".sdf", prefer=f"docked_{a.receptor}")
    if not lig_sdf:
        sys.exit(f"[abfe] no ligand SDF in channel {ch('ligand')}")
    cmd = ["python", "nr4a3_abfe.py", "--run-shard", "--leg", a.leg, "--ligand-sdf", lig_sdf,
           "--pose-name", a.ligand_name, "--out-dir", out_dir,
           "--window-start", a.window_start, "--n-iter", a.n_iter,
           "--steps-per-iter", a.steps_per_iter, "--platform", a.platform]
    if a.window_end:
        cmd += ["--window-end", a.window_end]
    if a.leg == "complex":
        rec_pdb = _first(ch("receptor"), ".pdb", prefer=f"{a.receptor}-opened")
        if not rec_pdb:
            sys.exit(f"[abfe] complex leg needs a receptor PDB in channel {ch('receptor')}")
        cmd += ["--receptor-pdb", rec_pdb]
    rc = _run_in_env(cmd, work, a.prebaked == "1")
    _copy_manifest()
    print(f"[abfe] run exit={rc} ({a.receptor}/{a.leg})", flush=True)
    raise SystemExit(rc)


def _run_in_env(cmd, work, prebaked):
    """Run `cmd` in the modern `abfe` conda env. Pre-baked image → skip the ~10-min solve. Clears PYTHONPATH so
    the env uses only its own site-packages (the SageMaker base container's PYTHONPATH leak — same numpy-1.x
    isolation bug fixed for the Yank env in entry_fep.py)."""
    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    have = prebaked or os.path.isdir("/opt/conda/envs/abfe")
    print(f"[abfe] {'PRE-BAKED abfe env' if have else 'building modern abfe env (no Yank pins)'}", flush=True)
    if not have:
        subprocess.run([conda, "create", "-y", "-n", "abfe", "--override-channels", "-c", "conda-forge",
                        *MODERN_PKGS], check=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = ""
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "abfe", *cmd], cwd=work, env=env)
    return r.returncode


def _copy_manifest():
    model_dir = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
    os.makedirs(model_dir, exist_ok=True)
    try:
        for root, _dirs, files in os.walk(CKPT):
            for f in files:
                if f in ("meta.json",) or f.endswith("_dg_bind.json"):
                    shutil.copy(os.path.join(root, f), os.path.join(model_dir, f))
    except Exception as e:  # noqa: BLE001
        print(f"[abfe] (manifest copy skipped: {e})", flush=True)


if __name__ == "__main__":
    main()
