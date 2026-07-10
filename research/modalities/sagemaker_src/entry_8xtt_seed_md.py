#!/usr/bin/env python3
"""SageMaker managed-SPOT Training entry: unbiased release-style MD seeded from an EXPERIMENTAL 8XTT
conformer (nr4a3_8xtt_seed_md.py).

Unlike entry_release.py (which resumes a metad `metad_system.xml`), this job BUILDS a fresh solvated system
from a bare 8XTT NMR conformer, so the env adds pdbfixer (system prep) + biopython (the UniProt<->8XTT map
for the CV). 8XTT + AF-Q92570 are fetched from RCSB/AFDB at runtime — NO input channel. All outputs (Rg
traces, per-replica state.xml checkpoints, progress, summary, DCDs) go to /opt/ml/checkpoints, synced to
checkpoint_s3_uri CONTINUOUSLY and re-populated on a spot restart / re-dispatch (RESUME). GPU job.

Per-frame fpocket druggability is produced downstream by nr4a3_mdpocket on the emitted DCD
(DCD_NAME=8xtt_release_rep0.dcd) — the same two-step split the metad release run uses.
"""
import os
import shutil
import subprocess
import sys

OUT = os.environ.get("SM_CHECKPOINT_DIR", "/opt/ml/checkpoints")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", default="5")
    ap.add_argument("--n-rep", default="3")
    ap.add_argument("--seed-model", default="8")
    ap.add_argument("--run-tag", default="8xtt_release")
    ap.add_argument("--checkpoint-every", default="10")
    ap.add_argument("--git-ref", default="main")
    args = ap.parse_args()
    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    create_env = os.environ.copy()
    create_env["CONDA_OVERRIDE_CUDA"] = "12.8"
    print(f"[sagemaker] creating CUDA OpenMM + mdtraj + pdbfixer + biopython env via {conda}", flush=True)
    subprocess.run([conda, "create", "-y", "-n", "md", "-c", "conda-forge",
                    "python=3.11", "openmm", "mdtraj", "pdbfixer", "biopython", "cuda-version=12.8"],
                   check=True, env=create_env)

    env = os.environ.copy()
    env["OUTPUT_DIR"] = OUT
    env["RESUME_DIR"] = OUT           # SageMaker pre-populates /opt/ml/checkpoints → resume own trajectories
    env["NS"] = args.ns
    env["N_REP"] = args.n_rep
    env["SEED_MODEL"] = args.seed_model
    env["RUN_TAG"] = args.run_tag
    env["CHECKPOINT_EVERY"] = args.checkpoint_every
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running 8XTT-seeded unbiased MD ({args.n_rep} x {args.ns} ns, "
          f"seed model {args.seed_model})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "md",
                        "python", "nr4a3_8xtt_seed_md.py"], cwd=work, env=env)
    for f in sorted(os.listdir(OUT)):
        try:
            print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
        except OSError:
            pass
    print(f"[sagemaker] 8xtt-seed-md exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
