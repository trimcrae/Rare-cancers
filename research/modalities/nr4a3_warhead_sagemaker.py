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
        import sagemaker_submit
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

    print(f"submitting warhead screen: {instance}, ref={git_ref}, "
          f"s3://{bucket}/{in_prefix} -> s3://{bucket}/{out_prefix}", flush=True)
    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME out_prefix the readers
    # expect; entry_warhead.py writes to sm_io.out_dir() == /opt/ml/checkpoints (synced continuously) and reads
    # the metad outputs from sm_io.channel("input"). The bare /opt/ml/processing/input mount (no subdir) becomes
    # the single "input" channel.
    sagemaker_submit.submit_spot(
        entry_point="entry_warhead.py", source_dir=os.path.join(here, "sagemaker_src"),
        base_job_name="nr4a3-warhead", output_prefix=out_prefix,
        inputs={"input": f"s3://{bucket}/{in_prefix}"},
        arguments=["--git-ref", git_ref],
        instance=instance, max_run=max_runtime, sess=sess, role=role, wait=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
