#!/usr/bin/env python3
"""SageMaker entry for the DE-NOVO selectivity funnel — docking tier (nr4a3_matrix.py in candidate mode).

Docks the top-N de-novo candidates into the Step-0 druggable-release NR4A3 receptor + the NR4A1/NR4A2
metad-opened conformers, and classifies each candidate's selectivity fingerprint. Reuses nr4a3_matrix.py
(env-guarded de-novo mode) so the OUTPUT IS THE SAME nr4a3-matrix.json + <tag>-opened.pdb + docked_<tag>.sdf
format the MM-GBSA step consumes — the next tier needs no new wiring (just INPUT_PREFIX=nr4a3-denovo-matrix).
CPU work (smina docking); no GPU.

ProcessingInputs (mounted under /opt/ml/processing/input):
  denovo/   : nr4a3-denovo            (nr4a3-denovo.json — the ranked generated candidates)
  receptor/ : nr4a3-release-druggable (nr4a3-release-druggable.pdb + manifest with box_residues)
  nr4a1/    : nr4a1-metad             (paralogue opened ensemble)
  nr4a2/    : nr4a2-metad             (paralogue opened ensemble)
"""
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"
IN = "/opt/ml/processing/input"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main")
    ap.add_argument("--top-n", default="20")
    ap.add_argument("--developable-only", default="1",
                    help="1 = dock only structural-alert-clean generations (red-team Tier-1 #1); 0 = all")
    ap.add_argument("--receptor-mode", default="release", choices=["release", "metad"],
                    help="release = Step-0 unbiased druggable-release NR4A3 frame (default); "
                         "metad = NR4A3 metad-opened conformer, STATE-MATCHED to the paralogue metad frames "
                         "(red-team Tier-1 #3). 'metad' needs the nr4a3-metad ensemble mounted at input/nr4a3.")
    ap.add_argument("--decoy", default="0",
                    help="1 = dock the fixed non-NR4A decoy set (specificity NULL, red-team Tier-1 #2) "
                         "through the identical funnel instead of the generations.")
    args = ap.parse_args()

    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating funnel env via {conda}", flush=True)
    subprocess.run([conda, "create", "-y", "-n", "mx", "-c", "conda-forge",
                    "python=3.11", "mdtraj", "fpocket", "smina", "rdkit", "biopython", "numpy",
                    "matplotlib-base"], check=True)

    env = os.environ.copy()
    env["INPUT_DIR"] = IN                                            # holds nr4a1/ nr4a2/ (and nr4a3/ in metad mode)
    env["OUTPUT_DIR"] = OUT
    env["CANDIDATE_JSON"] = os.path.join(IN, "denovo", "nr4a3-denovo.json")
    env["TOP_N"] = args.top_n
    env["DEVELOPABLE_ONLY"] = args.developable_only
    env["DECOY_MODE"] = args.decoy
    # NR4A3 receptor: release frame (set NR4A3_RECEPTOR -> driver docks the Step-0 unbiased druggable frame)
    # vs metad frame (unset -> driver extracts NR4A3's metad-opened conformer from input/nr4a3, STATE-MATCHED
    # to the paralogue metad frames). See nr4a3_matrix.py candidate-mode receptor logic.
    if args.receptor_mode == "release":
        env["NR4A3_RECEPTOR"] = os.path.join(IN, "receptor", "nr4a3-release-druggable.pdb")
    else:
        env.pop("NR4A3_RECEPTOR", None)
    print(f"[sagemaker] receptor_mode={args.receptor_mode} developable_only={args.developable_only}",
          flush=True)
    os.makedirs(OUT, exist_ok=True)
    # In metad mode NR4A3_RECEPTOR is unset (NR4A3 comes from the input/nr4a3 metad ensemble), so use .get.
    nr4a3_rec = env.get("NR4A3_RECEPTOR", os.path.join(IN, "nr4a3"))
    for name, p in (("candidates", env["CANDIDATE_JSON"]), ("NR4A3 receptor", nr4a3_rec),
                    ("nr4a1", os.path.join(IN, "nr4a1")), ("nr4a2", os.path.join(IN, "nr4a2"))):
        print(f"  {name}: {'present' if os.path.exists(p) else 'MISSING'} ({p})", flush=True)
    print(f"[sagemaker] running de-novo dock funnel (top {args.top_n}, ref {args.git_ref})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "mx",
                        "python", "nr4a3_matrix.py"], cwd=work, env=env)
    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] de-novo dock exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
