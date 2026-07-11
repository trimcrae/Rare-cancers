#!/usr/bin/env python3
"""
Submit the NR4A3 cryptic-pocket MD as an AWS SageMaker Processing job (managed, auto-tears-down).

Standard, mainstream AWS path. SageMaker provisions a GPU container from AWS's own PyTorch image
(no container registry to manage), installs sagemaker_src/requirements.txt, runs entry.py, enforces
a HARD MaxRuntime cap, then terminates the instance — there is nothing to shut off manually and it
cannot run away.

Driven from CI (gpu-md-aws.yml). Needs env: AWS creds + SAGEMAKER_ROLE_ARN (the execution role).
First run will likely need a GPU service-quota increase on a new account (see deploy/aws-sagemaker-setup.md).
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
    ns = os.environ.get("NS", "10")
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")          # A10G GPU
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(6 * 3600)))  # hard cap, AWS kills the job

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    print(f"submitting SageMaker job: {instance}, ns={ns}, max_runtime={max_runtime}s, "
          f"outputs -> s3://{bucket}/nr4a3-md", flush=True)
    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME nr4a3-md prefix the readers
    # expect; entry.py writes to sm_io.out_dir() == /opt/ml/checkpoints, synced continuously.
    sagemaker_submit.submit_spot(
        entry_point="entry.py", source_dir=os.path.join(here, "sagemaker_src"),
        base_job_name="nr4a3-md", output_prefix="nr4a3-md",
        arguments=["--ns", str(ns)],
        instance=instance, max_run=max_runtime, sess=sess, role=role, wait=True,
    )
    print(f"done — results in s3://{bucket}/nr4a3-md", flush=True)


if __name__ == "__main__":
    main()
