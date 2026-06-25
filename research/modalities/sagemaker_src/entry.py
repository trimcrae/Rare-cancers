#!/usr/bin/env python3
"""SageMaker entry script — runs inside the AWS-managed GPU container.

Clones the repo (latest main), runs the OpenMM MD (nr4a3_md.py), and copies outputs to
/opt/ml/processing/output, which SageMaker auto-uploads to S3 when the job finishes. SageMaker
provisions the GPU, enforces the hard MaxRuntime cap, and tears the instance down on completion —
nothing to shut off manually.
"""
import argparse
import os
import shutil
import subprocess
import sys

OUT = "/opt/ml/processing/output"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", default="10")
    ns = ap.parse_args().ns

    subprocess.run(["nvidia-smi"], check=False)  # confirm GPU attached
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    subprocess.run(["git", "clone", "--depth", "1",
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)

    work = "/tmp/repo/research/modalities"
    env = os.environ.copy()
    env["NS"] = ns
    print(f"[sagemaker] running MD for {ns} ns", flush=True)
    r = subprocess.run(["python", "nr4a3_md.py"], cwd=work, env=env)

    os.makedirs(OUT, exist_ok=True)
    for f in ("AF-Q92570.pdb", "nr4a3-lbd-solvated.pdb", "nr4a3-lbd-md.dcd"):
        p = os.path.join(work, f)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(OUT, f))
            print(f"[sagemaker] saved {f} ({os.path.getsize(p)} bytes)", flush=True)
    print(f"[sagemaker] MD exit={r.returncode}", flush=True)
    if r.returncode != 0:
        # Fail the processing job so a broken MD can't masquerade as a green run.
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
