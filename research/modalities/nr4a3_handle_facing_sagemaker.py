#!/usr/bin/env python3
"""
Submit the NR4A3 Gate-2 handle-facing confirmation as an AWS SageMaker Processing job.

Pulls the 30 ns metad outputs from s3://<default-bucket>/nr4a3-metad via ProcessingInput, runs the
handle-facing analysis (entry_handle_facing.py -> nr4a3_handle_facing.py), and writes results to
s3://<default-bucket>/nr4a3-handle-facing. CPU work (fpocket + geometry over ~25 frames, well under an
hour), but defaults to ml.g5.xlarge to reuse the GPU processing quota (override INSTANCE for a CPU type).

Driven from CI (handle-facing-aws.yml). Needs: AWS creds + SAGEMAKER_ROLE_ARN.
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
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(2 * 3600)))   # hard cap
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-metad")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-handle-facing")
    dcd_name = os.environ.get("DCD_NAME", "nr4a3-lbd-metad.dcd")
    git_ref = os.environ.get("GIT_REF", "main")

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
        base_job_name="nr4a3-handle-facing",
        sagemaker_session=sess,
    )
    print(f"submitting handle-facing analysis: {instance}, trajectory={dcd_name}, "
          f"s3://{bucket}/{in_prefix} -> s3://{bucket}/{out_prefix}", flush=True)
    proc.run(
        code="entry_handle_facing.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=[ProcessingInput(source=f"s3://{bucket}/{in_prefix}",
                                destination="/opt/ml/processing/input")],
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/{out_prefix}")],
        arguments=["--dcd-name", dcd_name, "--git-ref", git_ref],
        wait=True,
        logs=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
