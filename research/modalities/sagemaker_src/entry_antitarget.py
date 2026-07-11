#!/usr/bin/env python3
"""SageMaker managed-SPOT Training entry: anti-target / off-target panel dock (promiscuity control).

Docks the repurposing-survivor drug set into every prepared panel receptor with the same smina protocol as
the NR4A dock, ONE (drug,target) pair at a time, appending to a JSONL in /opt/ml/checkpoints (continuous S3
sync + resume on spot restart / re-dispatch). CPU job; defaults ml.c5.2xlarge spot.

Channels:
  panel/  (SM_CHANNEL_PANEL): nr4a3-antitarget-panel  (panel-manifest.json + <name>.pdb receptors)
The survivor candidate JSON is read from the cloned git_ref (committed in-repo).
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
    ap.add_argument("--candidates", required=True, help="survivor JSON filename under research/modalities")
    ap.add_argument("--tag", default="panel")
    ap.add_argument("--exhaustiveness", default="8")
    ap.add_argument("--per-ligand-timeout", default="300")
    args = ap.parse_args()

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating dock env via {conda}", flush=True)
    subprocess.run([conda, "install", "-n", "base", "-y", "-c", "conda-forge", "conda-libmamba-solver"],
                   check=False)
    _create = [conda, "create", "-y", "-n", "mx", "-c", "conda-forge",
               "python=3.11", "mdtraj", "fpocket=4.2.3", "rdkit", "biopython", "numpy", "matplotlib-base"]
    try:
        subprocess.run(_create + ["--solver=libmamba"], check=True)
    except subprocess.CalledProcessError:
        print("[sagemaker] libmamba unavailable; classic solver", flush=True)
        subprocess.run(_create, check=True)

    panel_dir = os.environ.get("SM_CHANNEL_PANEL", "/opt/ml/input/data/panel")
    import smina_env
    smina_env.setup_smina_env(conda)     # smina no longer co-solves with rdkit -> own env + wrapper

    env = os.environ.copy()
    env["PATH"] = smina_env.path_with_wrapper(env)          # make the smina wrapper discoverable
    env["OUTPUT_DIR"] = OUT
    env["RESUME_DIR"] = OUT
    env["PANEL_DIR"] = panel_dir
    env["CANDIDATE_JSON"] = os.path.join(work, args.candidates)
    env["EXHAUSTIVENESS"] = args.exhaustiveness
    env["PER_LIGAND_TIMEOUT"] = args.per_ligand_timeout
    os.makedirs(OUT, exist_ok=True)
    for name, p in (("panel-manifest", os.path.join(panel_dir, "panel-manifest.json")),
                    ("candidates", env["CANDIDATE_JSON"])):
        print(f"  {name}: {'present' if os.path.exists(p) else 'MISSING'} ({p})", flush=True)
    print(f"[sagemaker] running anti-target panel dock exh={args.exhaustiveness} ref={args.git_ref}", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "mx",
                        "python", "antitarget_dock.py"], cwd=work, env=env)
    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] anti-target dock exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
