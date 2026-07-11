#!/usr/bin/env python3
"""
Submit the Pocket-5 fpocket residue-enumeration as an AWS SageMaker Processing job.

Pulls the AF2 model from s3://<default-bucket>/nr4a3-md (saved by the MD job) via the "md" input channel,
runs fpocket (entry_fpocket.py), and writes pocket5_lining_residues.json to
s3://<default-bucket>/nr4a3-fpocket. CPU work; defaults to ml.g5.xlarge to reuse the GPU quota.
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
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(3600)))

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    dest_prefix = "nr4a3-fpocket"
    print(f"submitting fpocket enumeration: {instance}, s3://{bucket}/nr4a3-md -> "
          f"s3://{bucket}/{dest_prefix}", flush=True)
    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME dest_prefix the
    # readers expect; entry writes to sm_io.out_dir() == /opt/ml/checkpoints, synced continuously.
    sagemaker_submit.submit_spot(
        entry_point="entry_fpocket.py", source_dir=os.path.join(here, "sagemaker_src"),
        base_job_name="nr4a3-fpocket", output_prefix=dest_prefix,
        inputs={"md": f"s3://{bucket}/nr4a3-md"},
        instance=instance, max_run=max_runtime, sess=sess, role=role,
    )
    print(f"done — results in s3://{bucket}/{dest_prefix}", flush=True)


if __name__ == "__main__":
    main()
