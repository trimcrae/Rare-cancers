#!/usr/bin/env python3
"""SageMaker entry for the 8XTT-anchored ABFE RECEPTOR-PREFIX build (nr4a3_8xtt_abfe_receptor.py).

CPU work (fpocket per frame + smina dock + RDKit embed; no GPU, no MM-GBSA). One ProcessingInput mounts the
8XTT-seeded release outputs:
  /opt/ml/processing/input/release : nr4a3-8xtt-release  (8xtt_release_rep*_from*.dcd + 8xtt-lbd-solvated.pdb
                                     + 8xtt_release_summary.json)
We conda-install the docking/analysis stack (mdtraj + fpocket + smina + rdkit + biopython + numpy +
matplotlib) and run the driver; SageMaker uploads /opt/ml/processing/output CONTINUOUSLY (the submitter sets
s3_upload_mode="Continuous") so the per-frame manifest checkpoints reach S3 as written and a timeout keeps the
last partial as the deliverable. Output → s3://<bucket>/nr4a3-abfe-8xtt-receptor
(nr4a3-opened.pdb + docked_nr4a3.sdf + manifest + plot). The AFDB reference structure is fetched at runtime.
"""
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main", help="repo ref to run; default main")
    ap.add_argument("--d-star", default="0.53", help="druggable threshold (calibrated drug-bound band)")
    ap.add_argument("--rg-tol", default="0.1", help="nm persistence band around the seed Rg")
    ap.add_argument("--seed-rg", default="", help="override the seed Rg (else read from the release summary)")
    ap.add_argument("--max-frames-per-dcd", default="0", help="0 = every frame; >0 = evenly subsample")
    args = ap.parse_args()

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating docking/analysis env via {conda}", flush=True)
    subprocess.run([conda, "install", "-n", "base", "-y", "-c", "conda-forge", "conda-libmamba-solver"],
                   check=False)
    _create = [conda, "create", "-y", "-n", "ar", "-c", "conda-forge",
               "python=3.11", "mdtraj", "fpocket", "smina", "rdkit", "biopython", "numpy", "matplotlib-base"]
    try:
        subprocess.run(_create + ["--solver=libmamba"], check=True)
    except subprocess.CalledProcessError:
        print("[sagemaker] libmamba unavailable; classic solver", flush=True)
        subprocess.run(_create, check=True)

    env = os.environ.copy()
    env["RELEASE_DIR"] = "/opt/ml/processing/input/release"
    env["OUTPUT_DIR"] = OUT
    env["D_STAR"] = args.d_star
    env["RG_TOL"] = args.rg_tol
    env["MAX_FRAMES_PER_DCD"] = args.max_frames_per_dcd
    if args.seed_rg:
        env["SEED_RG"] = args.seed_rg
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running 8XTT ABFE-receptor build (ref {args.git_ref}, d_star={args.d_star}, "
          f"rg_tol={args.rg_tol})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "ar",
                        "python", "nr4a3_8xtt_abfe_receptor.py"], cwd=work, env=env)
    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] 8XTT ABFE-receptor build exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
