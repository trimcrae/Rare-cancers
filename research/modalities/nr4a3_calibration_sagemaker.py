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
        import sagemaker_submit
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
    out_prefix = "nr4a3-calibration"

    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME out_prefix the readers
    # expect; entry_calibration.py writes to sm_io.out_dir() == /opt/ml/checkpoints, synced continuously.
    print(f"submitting calibration: {instance}, ref={git_ref} -> s3://{bucket}/{out_prefix}", flush=True)
    sagemaker_submit.submit_spot(
        entry_point="entry_calibration.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        base_job_name="nr4a3-calibration",
        output_prefix=out_prefix,
        arguments=["--git-ref", git_ref],
        instance=instance, max_run=max_runtime, sess=sess, role=role, wait=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
