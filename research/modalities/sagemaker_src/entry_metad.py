#!/usr/bin/env python3
"""SageMaker managed-SPOT Training entry: NR4A3 LBD well-tempered metadynamics (cryptic-pocket opening).

Converted from an on-demand Processing job to a managed-spot Training job (same pattern as
entry_release.py / nr4a3_md_release_sagemaker.py), so >=3 independent-seed replicas run CONCURRENTLY on
the spot Training quota (8) instead of serializing on the single on-demand g5 Processing quota (1).

Resume is automatic and spot-safe: OUTPUT_DIR == the SageMaker-managed checkpoint dir
(SM_CHECKPOINT_DIR / /opt/ml/checkpoints), which SageMaker (a) PRE-POPULATES on start by downloading
checkpoint_s3_uri (a spot interruption OR a fresh re-dispatch with the same prefix) and (b) UPLOADS
CONTINUOUSLY during the run. nr4a3_metad.py writes its whole restart set (metad_system.xml,
nr4a3-lbd-solvated.pdb, metad_checkpoint.chk / metad_state.xml, HILLS, COLVAR, trajectory, fes.dat,
metad_manifest.json) there, so on restart it finds them and continues the accumulated bias with
PLUMED RESTART — losing at most the work since the last checkpoint (~100 ps). No --resume-from staging
is needed: the checkpoint dir replaces the ProcessingInput resume mount.

Each replica uses a DISTINCT --seed (independent initial velocities + Langevin noise) and its own S3
checkpoint prefix (nr4a3-metad-r{seed}), so the replicas never share a HILLS file. A seed mismatch on
resume is refused inside nr4a3_metad.py (the manifest guard).
"""
import glob
import os
import shutil
import subprocess
import sys

# SageMaker-managed checkpoint dir: continuously synced to checkpoint_s3_uri AND pre-populated with any
# prior checkpoints on start -> it is simultaneously the OUTPUT dir and the RESUME dir.
OUT = os.environ.get("SM_CHECKPOINT_DIR", "/opt/ml/checkpoints")

# The AF model is fetched by nr4a3_metad.py into the work dir; copy it out too for a complete audit set.
EXTRA_OUT_GLOBS = ("AF-*.pdb",)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", default="30")
    ap.add_argument("--target", default="NR4A3",
                    help="NR4A3 (default), NR4A1, or NR4A2 — paralogue CV/LBD mapped by alignment")
    ap.add_argument("--seed", default="0",
                    help="per-replica random seed (velocities + Langevin noise); 0 = legacy random")
    ap.add_argument("--git-ref", default="main",
                    help="repo ref to run (branch/tag/sha); default main")
    args = ap.parse_args()

    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    print(f"[sagemaker] running ref={args.git_ref} seed={args.seed}", flush=True)
    work = "/tmp/repo/research/modalities"
    git_sha = subprocess.run(["git", "-C", "/tmp/repo", "rev-parse", "HEAD"],
                             capture_output=True, text=True).stdout.strip()

    os.makedirs(OUT, exist_ok=True)
    # Resume audit: report what SageMaker pre-populated into the checkpoint dir (a re-dispatch / spot
    # restart lands the prior restart set here; a first run finds it empty -> fresh build).
    staged = [f for f in ("metad_system.xml", "HILLS", "metad_checkpoint.chk", "metad_manifest.json")
              if os.path.exists(os.path.join(OUT, f))]
    print(f"[sagemaker] checkpoint dir {OUT} contains {len(os.listdir(OUT))} file(s); "
          f"resume artifacts present: {staged or 'none (fresh run)'}", flush=True)

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating CUDA OpenMM + PLUMED env via {conda}", flush=True)
    create_env = os.environ.copy()
    create_env["CONDA_OVERRIDE_CUDA"] = "12.8"   # match the box driver; see deploy/aws-sagemaker-setup.md
    subprocess.run([conda, "create", "-y", "-n", "md", "-c", "conda-forge",
                    "python=3.11", "openmm", "pdbfixer", "openmm-plumed", "plumed", "biopython",
                    "cuda-version=12.8"], check=True, env=create_env)

    env = os.environ.copy()
    env["NS"] = args.ns
    env["TARGET"] = args.target
    env["SEED"] = args.seed
    env["GIT_REF"] = args.git_ref
    env["GIT_SHA"] = git_sha
    env["OUTPUT_DIR"] = OUT       # restart set written here -> continuous S3 sync + spot-restart resume
    # Clear any leaked PYTHONPATH so the SageMaker base container's site-packages can't shadow the conda
    # md env (the FEP numpy-1-vs-2 incident; see TESTING/next-steps "Infra gotchas").
    env.pop("PYTHONPATH", None)
    print(f"[sagemaker] running metadynamics {args.ns} ns, target={args.target}, seed={args.seed} "
          f"(sha {git_sha[:10]})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "md",
                        "python", "nr4a3_metad.py"], cwd=work, env=env)

    # nr4a3_metad.py already writes the restart set to OUT (= OUTPUT_DIR). Copy the AF model out too.
    for pat in EXTRA_OUT_GLOBS:
        for p in glob.glob(os.path.join(work, pat)):
            shutil.copy(p, os.path.join(OUT, os.path.basename(p)))
            print(f"[sagemaker] saved {os.path.basename(p)} ({os.path.getsize(p)} bytes)", flush=True)
    print(f"[sagemaker] metad exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
