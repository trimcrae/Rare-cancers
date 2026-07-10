#!/usr/bin/env python3
"""Submit PHASE 1 (metad convergence plan) — TICA slow-CV discovery — as an AWS SageMaker Processing job (CPU).

Mounts the 3 metad replica checkpoint prefixes (nr4a3-metad-r{1,2,3}/ckpt) and, optionally, the release prefix,
and runs entry_slow_cv.py: featurize (pocket distances / gate χ1 / SASA / Rg) -> TICA -> corr(IC1, Rg) +
implied timescales + redundancy verdict (slow-cv-summary.json). No GPU quota. Output uploaded continuously.

Driven from slow-cv-aws.yml. Needs: AWS creds + SAGEMAKER_ROLE_ARN.
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
        sys.exit("SAGEMAKER_ROLE_ARN not set")
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(6 * 3600)))
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-slow-cv")
    git_ref = os.environ.get("GIT_REF", "main")
    lag_frames = os.environ.get("LAG_FRAMES", "10")
    n_components = os.environ.get("N_COMPONENTS", "5")
    # Release DCDs use a different solvated box (atom count) than the metad topology, so they cannot be loaded
    # with the metad PDB; default OFF. The 3 metad replicas are the biased-opening data the slow-CV wants.
    include_release = os.environ.get("INCLUDE_RELEASE", "0") == "1"
    r1p = os.environ.get("R1_PREFIX", "nr4a3-metad-r1/ckpt")
    r2p = os.environ.get("R2_PREFIX", "nr4a3-metad-r2/ckpt")
    r3p = os.environ.get("R3_PREFIX", "nr4a3-metad-r3/ckpt")
    release_prefix = os.environ.get("RELEASE_PREFIX", "nr4a3-release")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    dest = f"s3://{bucket}/{out_prefix}"

    proc = FrameworkProcessor(
        estimator_cls=PyTorch, framework_version="2.3", py_version="py311", role=role,
        instance_count=1, instance_type=instance, max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-slow-cv", sagemaker_session=sess,
    )
    inputs = [
        ProcessingInput(source=f"s3://{bucket}/{r1p}", destination="/opt/ml/processing/r1"),
        ProcessingInput(source=f"s3://{bucket}/{r2p}", destination="/opt/ml/processing/r2"),
        ProcessingInput(source=f"s3://{bucket}/{r3p}", destination="/opt/ml/processing/r3"),
    ]
    if include_release:
        inputs.append(ProcessingInput(source=f"s3://{bucket}/{release_prefix}",
                                      destination="/opt/ml/processing/release"))
    print(f"submitting PHASE 1 slow-CV: {instance}, lag={lag_frames} frames, release={include_release}, "
          f"ref={git_ref} -> {dest}", flush=True)
    proc.run(
        code="entry_slow_cv.py", source_dir=os.path.join(here, "sagemaker_src"),
        inputs=inputs,
        outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination=dest,
                                  s3_upload_mode="Continuous")],
        arguments=["--git-ref", git_ref, "--lag-frames", str(lag_frames), "--n-components", str(n_components)],
        wait=True, logs=True,
    )
    print(f"done — results in {dest} (see slow-cv-summary.json)", flush=True)


if __name__ == "__main__":
    main()
