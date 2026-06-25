#!/usr/bin/env python3
"""SageMaker entry: enumerate Pocket-5 lining residues with fpocket on the AF2 model.

ProcessingInput mounts the MD outputs (incl. AF-Q92570.pdb) at /opt/ml/processing/input. We
conda-install fpocket, run nr4a3_fpocket_enumerate.py, and SageMaker uploads /opt/ml/processing/output
to S3. CPU work.
"""
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"


def main():
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1",
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    print(f"[sagemaker] creating fpocket env via {conda}", flush=True)
    subprocess.run([conda, "create", "-y", "-n", "fp", "-c", "conda-forge",
                    "python=3.11", "fpocket"], check=True)

    env = os.environ.copy()
    env["INPUT_DIR"] = "/opt/ml/processing/input"
    env["OUTPUT_DIR"] = OUT
    os.makedirs(OUT, exist_ok=True)
    print("[sagemaker] enumerating Pocket-5 lining residues", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "fp",
                        "python", "nr4a3_fpocket_enumerate.py"], cwd=work, env=env)
    print(f"[sagemaker] fpocket exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
