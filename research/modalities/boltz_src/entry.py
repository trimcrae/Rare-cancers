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
    ap.add_argument("--binary-smiles", default="",
                    help="warhead SMILES → BINARY co-fold (NR4A-LBD + warhead), the AF3-class pose cross-check")
    ap.add_argument("--control", action="store_true",
                    help="control-only (no PROTAC); no-op flag so the SageMaker arg list is non-empty")
    _a = ap.parse_args()
    protac = _a.protac_smiles
    binary = _a.binary_smiles

    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"],
                   check=False)
    # boltz + its cuEquivariance accel kernel (boltz>=2 imports cuequivariance_torch in the triangular-mult
    # kernel and HARD-CRASHES if absent — the 2026-07-01 control failure). Install the accel stack too.
    subprocess.run(["pip", "install", "--quiet", "boltz",
                    "cuequivariance-torch", "cuequivariance-ops-torch-cu12"], check=False)
    subprocess.run(["git", "clone", "--depth", "1",
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)

    work = "/tmp/repo/research/modalities"
    env = os.environ.copy()
    if protac:
        env["PROTAC_SMILES"] = protac
    if binary:
        env["BINARY_SMILES"] = binary
    # Write Boltz outputs + prep JSON DIRECTLY into the SageMaker output dir so the Continuous S3 upload
    # (set in the submitter) captures each target as it finishes — a timeout after target N still uploads
    # targets 1..N (the checkpoint/continuous-upload standing rule). nr4a3_ternary.py honours $OUTPUT_DIR.
    os.makedirs(OUT, exist_ok=True)
    env["OUTPUT_DIR"] = OUT
    print(f"[sagemaker] running Boltz ternary (protac={'set' if protac else 'control-only'})", flush=True)
    r = subprocess.run(["python", "nr4a3_ternary.py", "--run"], cwd=work, env=env)

    # belt-and-braces: also copy any YAML/prep left next to the code (back-compat)
    import glob
    for p in glob.glob(os.path.join(work, "*-ternary-*.yaml")) + \
            glob.glob(os.path.join(work, "nr4a3-ternary-prep.json")):
        dst = os.path.join(OUT, os.path.basename(p))
        if not os.path.exists(dst):
            shutil.copy(p, dst)
    print(f"[sagemaker] ternary exit={r.returncode}", flush=True)
    # Propagate the real exit code: a Boltz crash (e.g. the missing-accel-module failure) must FAIL the
    # job, not report false-green. Prep JSON + YAMLs are already copied above, so partials still upload.
    if r.returncode != 0:
        raise SystemExit(r.returncode)


if __name__ == "__main__":
    main()
