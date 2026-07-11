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
        import sagemaker_submit
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

    # Managed-SPOT Training (was on-demand Processing): the metad prefix mounts as the "metad" channel
    # (entry reads sm_io.channel("metad")); checkpoint_s3_uri = the SAME out_prefix, synced continuously.
    inputs = {"metad": f"s3://{bucket}/{in_prefix}"}
    print(f"submitting handle-facing analysis: {instance}, trajectory={dcd_name}, "
          f"s3://{bucket}/{in_prefix} -> s3://{bucket}/{out_prefix}", flush=True)
    sagemaker_submit.submit_spot(
        entry_point="entry_handle_facing.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        base_job_name="nr4a3-handle-facing",
        output_prefix=out_prefix,
        inputs=inputs,
        arguments=["--dcd-name", dcd_name, "--git-ref", git_ref],
        instance=instance, max_run=max_runtime, sess=sess, role=role, wait=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
