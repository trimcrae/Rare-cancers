#!/usr/bin/env python3
"""
Submit the fpocket calibration panel as an AWS SageMaker Processing job (managed, auto-tears-down).

CPU work (fpocket on a small NR-LBD panel fetched from AFDB + RCSB at runtime); defaults to
ml.g5.xlarge to reuse the GPU processing quota (override INSTANCE for a CPU type). No ProcessingInput.
Output (nr4a3-calibration.json) -> s3://<default-bucket>/nr4a3-calibration. Needs AWS creds +
SAGEMAKER_ROLE_ARN. Driven from gpu-calibration-aws.yml.
"""
import os
import sys


def main():
    try:
        import sagemaker
        from sagemaker.processing import FrameworkProcessor, ProcessingOutput
        from sagemaker.pytorch import PyTorch
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set (the SageMaker execution-role ARN)")
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(2 * 3600)))
    git_ref = os.environ.get("GIT_REF", "main")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    out_prefix = f"s3://{bucket}/nr4a3-calibration"

    proc = FrameworkProcessor(
        estimator_cls=PyTorch,
        framework_version="2.3",
        py_version="py311",
        role=role,
        instance_count=1,
        instance_type=instance,
        max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-calibration",
        sagemaker_session=sess,
    )
    print(f"submitting calibration: {instance}, ref={git_ref} -> {out_prefix}", flush=True)
    proc.run(
        code="entry_calibration.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination=out_prefix)],
        arguments=["--git-ref", git_ref],
        wait=True,
        logs=True,
    )
    print(f"done — results in {out_prefix}", flush=True)


if __name__ == "__main__":
    main()
