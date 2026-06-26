#!/usr/bin/env python3
"""
Submit the NR4A family-wide selectivity matrix as an AWS SageMaker Processing job.

Mounts the three opened-ensemble prefixes (s3://<bucket>/{nr4a3-metad,nr4a1-metad,nr4a2-metad}) as
ProcessingInputs at /opt/ml/processing/input/{nr4a3,nr4a1,nr4a2}, runs entry_matrix.py ->
nr4a3_matrix.py, and writes s3://<bucket>/nr4a3-matrix. CPU work (docking into 3 opened pockets);
defaults to ml.g5.xlarge to reuse the GPU quota. Needs AWS creds + SAGEMAKER_ROLE_ARN.

Prereq: all three `*-metad` runs must have completed (verify the opened ensembles are in S3).
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
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-matrix")
    git_ref = os.environ.get("GIT_REF", "main")
    # S3 prefixes for the three opened ensembles (override if named differently).
    prefixes = {"nr4a3": os.environ.get("NR4A3_PREFIX", "nr4a3-metad"),
                "nr4a1": os.environ.get("NR4A1_PREFIX", "nr4a1-metad"),
                "nr4a2": os.environ.get("NR4A2_PREFIX", "nr4a2-metad")}

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    proc = FrameworkProcessor(
        estimator_cls=PyTorch, framework_version="2.3", py_version="py311", role=role,
        instance_count=1, instance_type=instance, max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-matrix", sagemaker_session=sess,
    )
    inputs = [ProcessingInput(source=f"s3://{bucket}/{prefixes[t]}",
                              destination=f"/opt/ml/processing/input/{t}", input_name=t)
              for t in ("nr4a3", "nr4a1", "nr4a2")]
    print(f"submitting matrix: {instance}; inputs " +
          ", ".join(f"{t}=s3://{bucket}/{prefixes[t]}" for t in prefixes) +
          f" -> s3://{bucket}/{out_prefix}", flush=True)
    proc.run(
        code="entry_matrix.py",
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
