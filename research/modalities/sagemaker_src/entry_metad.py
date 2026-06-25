#!/usr/bin/env python3
"""SageMaker entry: NR4A3 LBD well-tempered metadynamics (cryptic-pocket opening).

Same CUDA OpenMM conda recipe as the plain MD (entry.py) plus openmm-plumed for the metadynamics
bias. Runs nr4a3_metad.py and copies the CV/bias logs, trajectory, topology, free-energy profile, and
the checkpoint/restart set to /opt/ml/processing/output (auto-uploaded to S3).

--resume-from <dir>: a directory (a prior run's outputs, mounted by SageMaker as a ProcessingInput)
holding the restart set (metad_system.xml, nr4a3-lbd-solvated.pdb, metad_checkpoint.chk /
metad_state.xml, HILLS, COLVAR, metad_manifest.json, and the trajectory). These are staged into the
work dir before the run so nr4a3_metad.py continues the accumulated bias instead of starting fresh.
"""
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"

# The restart / reproducibility set written by nr4a3_metad.py. Staged IN on resume, copied OUT always.
ARTIFACTS = ("AF-Q92570.pdb", "nr4a3-lbd-solvated.pdb", "nr4a3-lbd-metad.dcd", "COLVAR", "HILLS",
             "fes.dat", "metad_system.xml", "metad_checkpoint.chk", "metad_state.xml",
             "metad_manifest.json")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", default="30")
    ap.add_argument("--git-ref", default="main",
                    help="repo ref to run (branch/tag/sha); default main")
    ap.add_argument("--resume-from", default="",
                    help="dir with a prior run's restart set to continue from (empty = fresh run)")
    args = ap.parse_args()
    ns = args.ns
    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    print(f"[sagemaker] running ref={args.git_ref}", flush=True)
    work = "/tmp/repo/research/modalities"
    git_sha = subprocess.run(["git", "-C", "/tmp/repo", "rev-parse", "HEAD"],
                             capture_output=True, text=True).stdout.strip()

    # Stage a prior run's restart set into the work dir, if provided.
    staged = []
    if args.resume_from and os.path.isdir(args.resume_from):
        for f in ARTIFACTS:
            src = os.path.join(args.resume_from, f)
            if os.path.exists(src):
                shutil.copy(src, os.path.join(work, f))
                staged.append(f)
        print(f"[sagemaker] resume: staged {len(staged)} artifact(s) from {args.resume_from}: "
              f"{staged}", flush=True)
        if "metad_system.xml" not in staged or "HILLS" not in staged:
            print("[sagemaker] WARNING: incomplete restart set — nr4a3_metad.py will start fresh.",
                  flush=True)
    elif args.resume_from:
        print(f"[sagemaker] WARNING: --resume-from {args.resume_from} is not a directory; fresh run.",
              flush=True)

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating CUDA OpenMM + PLUMED env via {conda}", flush=True)
    create_env = os.environ.copy()
    create_env["CONDA_OVERRIDE_CUDA"] = "12.8"   # match the box driver; see deploy/aws-sagemaker-setup.md
    subprocess.run([conda, "create", "-y", "-n", "md", "-c", "conda-forge",
                    "python=3.11", "openmm", "pdbfixer", "openmm-plumed", "plumed",
                    "cuda-version=12.8"], check=True, env=create_env)

    env = os.environ.copy()
    env["NS"] = ns
    env["GIT_REF"] = args.git_ref
    env["GIT_SHA"] = git_sha
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running metadynamics for {ns} ns (sha {git_sha[:10]})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "md",
                        "python", "nr4a3_metad.py"], cwd=work, env=env)

    for f in ARTIFACTS:
        p = os.path.join(work, f)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(OUT, f))
            print(f"[sagemaker] saved {f} ({os.path.getsize(p)} bytes)", flush=True)
    print(f"[sagemaker] metad exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
