#!/usr/bin/env python3
"""
Submit the 8XTT-anchored ABFE RECEPTOR-PREFIX build as an AWS SageMaker Processing job.

Mounts the 8XTT-seeded release outputs and produces the ABFE receptor prefix consumed by nr4a3_abfe_sagemaker.py:
  release : s3://<bucket>/nr4a3-8xtt-release (8xtt_release_rep*_from*.dcd + 8xtt-lbd-solvated.pdb +
            8xtt_release_summary.json)  -> /opt/ml/processing/input/release
Runs entry_8xtt_abfe_receptor.py -> nr4a3_8xtt_abfe_receptor.py, writing nr4a3-opened.pdb + docked_nr4a3.sdf +
the manifest to s3://<bucket>/nr4a3-abfe-8xtt-receptor.

CPU work (fpocket per frame + smina dock + RDKit; no GPU, no MM-GBSA) — defaults ml.c5.2xlarge (separate quota
from the g5 used by MD/MM-GBSA/FEP). Output is uploaded CONTINUOUSLY so the per-frame manifest checkpoints reach
S3 as written (a timeout keeps the last partial as the deliverable — CLAUDE.md checkpoint rule). Driven from
gpu-8xtt-abfe-receptor-aws.yml. Needs AWS creds + SAGEMAKER_ROLE_ARN.

Prereq: nr4a3_8xtt_seed_md.py populated s3://<bucket>/nr4a3-8xtt-release. AFTER this job, run the ABFE complex
leg for NR4A3 with RECEPTOR_PREFIX=nr4a3-abfe-8xtt-receptor and ABFE_RECEPTORS=nr4a3.
"""
import os
import sys


def main():
    try:
        import sagemaker
        from sagemaker.processing import FrameworkProcessor, ProcessingInput, ProcessingOutput
        from sagemaker.pytorch import PyTorch
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set (the SageMaker execution-role ARN)")
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")     # CPU; this step never needs a GPU
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(3 * 3600)))
    release_prefix = os.environ.get("RELEASE_PREFIX", "nr4a3-8xtt-release/8xtt_release-ckpt")  # seed-MD (Training job) writes under the checkpoint subprefix
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-abfe-8xtt-receptor")
    git_ref = os.environ.get("GIT_REF", "main")
    d_star = os.environ.get("D_STAR", "0.53")
    rg_tol = os.environ.get("RG_TOL", "0.1")
    seed_rg = os.environ.get("SEED_RG", "")
    max_frames = os.environ.get("MAX_FRAMES_PER_DCD", "0")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    proc = FrameworkProcessor(
        estimator_cls=PyTorch, framework_version="2.3", py_version="py311", role=role,
        instance_count=1, instance_type=instance, max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-8xtt-abfe-receptor", sagemaker_session=sess,
    )
    inputs = [ProcessingInput(source=f"s3://{bucket}/{release_prefix}",
                              destination="/opt/ml/processing/input/release", input_name="release")]
    args = ["--git-ref", git_ref, "--d-star", d_star, "--rg-tol", rg_tol,
            "--max-frames-per-dcd", max_frames]
    if seed_rg:
        args += ["--seed-rg", seed_rg]
    print(f"submitting 8XTT ABFE-receptor build: {instance}; release=s3://{bucket}/{release_prefix} "
          f"-> s3://{bucket}/{out_prefix}", flush=True)
    proc.run(
        code="entry_8xtt_abfe_receptor.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=inputs,
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/{out_prefix}", s3_upload_mode="Continuous")],
        arguments=args,
        wait=True, logs=True,
    )
    print(f"done — receptor prefix in s3://{bucket}/{out_prefix} "
          f"(nr4a3-opened.pdb + docked_nr4a3.sdf). Run the ABFE NR4A3 complex leg with "
          f"RECEPTOR_PREFIX={out_prefix} ABFE_RECEPTORS=nr4a3.", flush=True)


if __name__ == "__main__":
    main()
