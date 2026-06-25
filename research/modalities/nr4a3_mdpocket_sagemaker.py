#!/usr/bin/env python3
"""
Submit the NR4A3 MD-trajectory pocket analysis as an AWS SageMaker Processing job.

Pulls the MD outputs from s3://<default-bucket>/nr4a3-md via ProcessingInput, runs the mdpocket/SASA
analysis (entry_mdpocket.py), and writes results to s3://<default-bucket>/nr4a3-mdpocket. This is CPU
work but defaults to ml.g5.xlarge so it reuses the GPU processing quota you already have (avoids a
separate CPU-instance quota request); override INSTANCE to a CPU type once that quota exists.

Driven from CI (gpu-mdpocket-aws.yml). Needs: AWS creds + SAGEMAKER_ROLE_ARN.
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
        base_job_name="nr4a3-mdpocket",
        sagemaker_session=sess,
    )
    print(f"submitting analysis: {instance}, s3://{bucket}/nr4a3-md -> "
          f"s3://{bucket}/nr4a3-mdpocket", flush=True)
    proc.run(
        code="entry_mdpocket.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=[ProcessingInput(source=f"s3://{bucket}/nr4a3-md",
                                destination="/opt/ml/processing/input")],
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/nr4a3-mdpocket")],
        wait=True,
        logs=True,
    )
    print(f"done — results in s3://{bucket}/nr4a3-mdpocket", flush=True)


if __name__ == "__main__":
    main()
