#!/usr/bin/env python3
"""
Submit the MM-GBSA endpoint rescoring as an AWS SageMaker Processing job.

Mounts the matrix outputs (s3://<bucket>/nr4a3-matrix) as one ProcessingInput at
/opt/ml/processing/input, runs entry_mmgbsa.py -> nr4a3_mmgbsa.py, and writes s3://<bucket>/nr4a3-mmgbsa.
This is endpoint rescoring of existing docked poses (single-snapshot, no MD), so it runs fine on CPU and
defaults to a CHEAP CPU instance (ml.c5.2xlarge, ~$0.34/h, 8 vCPU for the multi-threaded OpenMM CPU
platform) — NOT a g5: it removes the GPU/OpenCL uncertainty entirely (run 7's 82-min silent hang was the
unpinned conda env dragging in an unused PyTorch-CUDA stack, not a compute-speed problem; see
entry_mmgbsa.py). Override with INSTANCE=ml.g5.xlarge to use the GPU. Needs AWS creds + SAGEMAKER_ROLE_ARN.

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
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")
    # Backstop only — entry_mmgbsa.py enforces tighter per-step timeouts (30 min env build, 90 min compute)
    # that end a hang fast and visibly. 2 h here just caps a pathological case from running away.
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(2 * 3600)))
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
