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

import sm_io
OUT = sm_io.out_dir()   # spot Training → /opt/ml/checkpoints (continuous S3 sync); Processing → legacy path


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
    # kernel and HARD-CRASHES if absent — the 2026-07-01 control failure). REPRODUCIBILITY (review fix #9): PIN
    # the Boltz version (BOLTZ_SPEC, default the last-used 2.2.1) so a rerun is not silently a different model;
    # record the resolved version + git ref into the output for provenance. Override BOLTZ_SPEC to bump.
    boltz_spec = os.environ.get("BOLTZ_SPEC", "boltz==2.2.1")
    subprocess.run(["pip", "install", "--quiet", boltz_spec,
                    "cuequivariance-torch", "cuequivariance-ops-torch-cu12"], check=False)
    # PIN the code to an exact commit (GIT_REF, default main) rather than always cloning live main, so the
    # analysis code + spec used are reproducible and recorded.
    git_ref = os.environ.get("GIT_REF", "main")
    subprocess.run(["git", "clone", "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    subprocess.run(["git", "-C", "/tmp/repo", "checkout", git_ref], check=False)
    resolved = subprocess.run(["git", "-C", "/tmp/repo", "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    # Provenance stamp (review fix #9): the exact code commit + Boltz spec + args land in the output prefix so a
    # rerun is auditable and old/new predictions are never confused (use an immutable OUTPUT_PREFIX per run).
    try:
        import json as _json
        _json.dump({"git_ref": git_ref, "resolved_commit": resolved, "boltz_spec": boltz_spec,
                    "output_prefix": os.environ.get("OUTPUT_PREFIX"), "ternary_script": os.environ.get("TERNARY_SCRIPT"),
                    "extra_args": os.environ.get("TERNARY_EXTRA_ARGS"), "seeds": os.environ.get("SEEDS")},
                   open(os.path.join(OUT, "run_provenance.json"), "w"), indent=2)
    except Exception as _e:  # noqa: BLE001
        print("[sagemaker] provenance stamp skipped: %s" % _e, flush=True)

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
    # Configurable ternary script + extra args (default = the CRBN nr4a3_ternary.py). Set TERNARY_SCRIPT=
    # nrv04_ternary.py + TERNARY_EXTRA_ARGS="--pilot" for the retrospective NR-V04/VHL benchmark; those and
    # SEEDS/WITH_VBC/NRV04_SMILES pass through via the container env (set on the processor by the submitter).
    script = os.environ.get("TERNARY_SCRIPT", "nr4a3_ternary.py")
    extra = os.environ.get("TERNARY_EXTRA_ARGS", "").split()
    print(f"[sagemaker] running Boltz ternary: {script} --run {' '.join(extra)} "
          f"(protac={'set' if protac else 'control-only'})", flush=True)
    r = subprocess.run(["python", script, "--run"] + extra, cwd=work, env=env)

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
