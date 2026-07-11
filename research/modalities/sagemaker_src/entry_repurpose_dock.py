#!/usr/bin/env python3
"""SageMaker managed-SPOT Training entry: interruption-robust NR4A3-only drug-repurposing dock.

Docks one shard of the Broad Repurposing Hub library into the unbiased druggable-release NR4A3 pocket, ONE
drug at a time, appending to a JSONL in /opt/ml/checkpoints — which SageMaker syncs to checkpoint_s3_uri
continuously AND re-downloads on a spot restart / re-dispatch, so the driver RESUMES and a kill loses ≤1
drug. CPU job (smina docking); defaults ml.c5.2xlarge spot.

Channels:
  receptor/  (SM_CHANNEL_RECEPTOR): nr4a3-release-druggable  (nr4a3-release-druggable.pdb + manifest)
The candidate shard JSON is read from the cloned git_ref (it is committed in the repo), so no S3 mount and
no CI-user PutObject is needed — the SageMaker role writes only the checkpoint output.
"""
import os
import shutil
import subprocess
import sys

OUT = os.environ.get("SM_CHECKPOINT_DIR", "/opt/ml/checkpoints")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main")
    ap.add_argument("--shard", required=True, help="shard JSON filename under research/modalities")
    ap.add_argument("--tag", default="", help="output namespace (default: derived from --shard)")
    ap.add_argument("--exhaustiveness", default="4")
    ap.add_argument("--per-ligand-timeout", default="300")
    args = ap.parse_args()
    tag = args.tag or args.shard.replace("nr4a3-repurpose-", "").replace(".json", "")

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating dock env via {conda}", flush=True)
    subprocess.run([conda, "install", "-n", "base", "-y", "-c", "conda-forge", "conda-libmamba-solver"],
                   check=False)
    # same proven env spec as the de-novo dock funnel (avoids a fresh env shakeout).
    _create = [conda, "create", "-y", "-n", "mx", "-c", "conda-forge",
               "python=3.11", "mdtraj", "fpocket=4.2.3", "rdkit", "biopython", "numpy", "matplotlib-base"]
    try:
        subprocess.run(_create + ["--solver=libmamba"], check=True)
    except subprocess.CalledProcessError:
        print("[sagemaker] libmamba unavailable; classic solver", flush=True)
        subprocess.run(_create, check=True)

    receptor_dir = os.environ.get("SM_CHANNEL_RECEPTOR", "/opt/ml/input/data/receptor")
    import smina_env
    smina_env.setup_smina_env(conda)     # smina no longer co-solves with rdkit -> own env + wrapper

    env = os.environ.copy()
    env["PATH"] = smina_env.path_with_wrapper(env)          # make the smina wrapper discoverable
    env["OUTPUT_DIR"] = OUT
    env["RESUME_DIR"] = OUT               # SageMaker pre-populated OUT with prior checkpoints on start
    env["TAG"] = tag
    env["NR4A3_RECEPTOR"] = os.path.join(receptor_dir, "nr4a3-release-druggable.pdb")
    env["CANDIDATE_JSON"] = os.path.join(work, args.shard)
    env["EXHAUSTIVENESS"] = args.exhaustiveness
    env["PER_LIGAND_TIMEOUT"] = args.per_ligand_timeout
    os.makedirs(OUT, exist_ok=True)
    for name, p in (("receptor", env["NR4A3_RECEPTOR"]), ("candidates", env["CANDIDATE_JSON"])):
        print(f"  {name}: {'present' if os.path.exists(p) else 'MISSING'} ({p})", flush=True)
    print(f"[sagemaker] running NR4A3-only repurpose dock tag={tag} exh={args.exhaustiveness} "
          f"ref={args.git_ref}", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "mx",
                        "python", "nr4a3_repurpose_dock.py"], cwd=work, env=env)
    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] repurpose dock exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
