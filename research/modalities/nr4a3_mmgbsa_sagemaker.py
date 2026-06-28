#!/usr/bin/env python3
"""
Submit the MM-GBSA endpoint rescoring as an AWS SageMaker Processing job.

Mounts the matrix outputs (s3://<bucket>/nr4a3-matrix) as one ProcessingInput at
/opt/ml/processing/input, runs entry_mmgbsa.py -> nr4a3_mmgbsa.py, and writes s3://<bucket>/nr4a3-mmgbsa.
This is endpoint rescoring of existing docked poses (single-snapshot, no MD). Defaults to ml.g5.xlarge
(A10G GPU): run 8 proved the ~4000-atom GB minimisation is ~48 min/ligand on CPU, so the compute genuinely
needs the GPU — and there is now NO CPU fallback (mmgbsa_energy.py fails fast if no GPU platform loads).
The earlier env hang (run 7) was the unpinned conda env, not the instance, and is fixed independently (slim
env in entry_mmgbsa.py). Override INSTANCE=ml.c5.* only with MMGBSA_ALLOW_CPU=1. Needs AWS creds +
SAGEMAKER_ROLE_ARN.

Prereq: the matrix job must have populated s3://<bucket>/nr4a3-matrix (receptors + docked_*.sdf).
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
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    # Backstop only — entry_mmgbsa.py enforces tighter per-step timeouts (30 min env build, 30 min compute)
    # that end a hang fast and visibly. 90 min here just caps a pathological case from running away.
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(90 * 60)))
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-matrix")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-mmgbsa")
    git_ref = os.environ.get("GIT_REF", "main")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    proc = FrameworkProcessor(
        estimator_cls=PyTorch, framework_version="2.3", py_version="py311", role=role,
        instance_count=1, instance_type=instance, max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-mmgbsa", sagemaker_session=sess,
    )
    inputs = [ProcessingInput(source=f"s3://{bucket}/{in_prefix}",
                              destination="/opt/ml/processing/input", input_name="matrix")]
    print(f"submitting mmgbsa: {instance}; input s3://{bucket}/{in_prefix} -> s3://{bucket}/{out_prefix}",
          flush=True)
    proc.run(
        code="entry_mmgbsa.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=inputs,
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/{out_prefix}")],
        arguments=["--git-ref", git_ref],
        wait=True, logs=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
