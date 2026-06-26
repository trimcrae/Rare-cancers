#!/usr/bin/env python3
"""
Submit the selective NR4A3 warhead screen as an AWS SageMaker Processing job (managed, auto-tears-down).

Mounts the 30 ns metad outputs (s3://<bucket>/nr4a3-metad) as ProcessingInput so the job can extract the
opened conformer, then docks candidates into NR4A3-opened + NR4A1/NR4A2 and scores selectivity. CPU work
(< 6 h, so wait=True is safe); defaults to ml.g5.xlarge to reuse the GPU quota. Output ->
s3://<bucket>/nr4a3-warhead. Needs AWS creds + SAGEMAKER_ROLE_ARN. Driven from gpu-warhead-aws.yml.
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
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(4 * 3600)))
    git_ref = os.environ.get("GIT_REF", "main")
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-metad")     # has the opened-conformer trajectory
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-warhead")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    proc = FrameworkProcessor(
        estimator_cls=PyTorch,
        framework_version="2.3",
        py_version="py311",
        role=role,
        instance_count=1,
        instance_type=instance,
        max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-warhead",
        sagemaker_session=sess,
    )
    print(f"submitting warhead screen: {instance}, ref={git_ref}, "
          f"s3://{bucket}/{in_prefix} -> s3://{bucket}/{out_prefix}", flush=True)
    proc.run(
        code="entry_warhead.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=[ProcessingInput(source=f"s3://{bucket}/{in_prefix}",
                                destination="/opt/ml/processing/input")],
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/{out_prefix}")],
        arguments=["--git-ref", git_ref],
        wait=True,
        logs=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
