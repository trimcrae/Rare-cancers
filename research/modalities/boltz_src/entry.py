#!/usr/bin/env python3
"""SageMaker entry script — runs the Boltz-2 ternary prediction inside the AWS GPU container.

Clones the repo (latest main), installs Boltz, runs nr4a3_ternary.py --run (CRBN+ligand control, plus
the NR4A3-LBD+CRBN+PROTAC ternary if a SMILES is supplied), and copies the Boltz outputs + input
YAMLs + prep JSON to /opt/ml/processing/output, which SageMaker auto-uploads to S3. SageMaker
provisions the GPU, enforces the hard MaxRuntime cap, and tears the instance down on completion.
"""
import argparse
import os
import shutil
import subprocess

OUT = "/opt/ml/processing/output"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--protac-smiles", default="")
    protac = ap.parse_args().protac_smiles

    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["pip", "install", "--quiet", "boltz"], check=False)
    subprocess.run(["git", "clone", "--depth", "1",
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)

    work = "/tmp/repo/research/modalities"
    env = os.environ.copy()
    if protac:
        env["PROTAC_SMILES"] = protac
    print(f"[sagemaker] running Boltz ternary (protac={'set' if protac else 'control-only'})", flush=True)
    r = subprocess.run(["python", "nr4a3_ternary.py", "--run"], cwd=work, env=env)

    os.makedirs(OUT, exist_ok=True)
    for f in ("nr4a3-ternary-control.yaml", "nr4a3-ternary-protac.yaml", "nr4a3-ternary-prep.json"):
        p = os.path.join(work, f)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(OUT, f))
    boltz_out = os.path.join(work, "boltz_out")
    if os.path.isdir(boltz_out):
        shutil.copytree(boltz_out, os.path.join(OUT, "boltz_out"), dirs_exist_ok=True)
    print(f"[sagemaker] ternary exit={r.returncode}", flush=True)


if __name__ == "__main__":
    main()
