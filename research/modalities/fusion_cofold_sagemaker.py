#!/usr/bin/env python3
"""
Submit the EWSR1::NR4A3 fusion-junction apo co-fold as an AWS SageMaker Processing job.

Same managed, auto-tears-down path as the ternary Boltz job (nr4a3_ternary_sagemaker.py): SageMaker
provisions a GPU container, installs boltz_src/requirements.txt, runs entry_cofold.py (which runs
fusion_cofold.py --run — two chimeric apo constructs), enforces a hard MaxRuntime cap, then terminates.

Driven from CI (gpu-cofold-aws.yml). Needs env: AWS creds + SAGEMAKER_ROLE_ARN. Both constructs are a
single ~380-490 aa chain, so the ml.g5.xlarge (A10G, 16 GB) the account has quota for is ample.
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
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(6 * 3600)))   # hard cap
    dest_prefix = os.environ.get("OUTPUT_PREFIX", "fusion-cofold")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    print(f"submitting SageMaker fusion co-fold job: {instance}, max_runtime={max_runtime}s, "
          f"outputs -> s3://{bucket}/{dest_prefix}", flush=True)
    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME dest_prefix the readers
    # expect; entry_cofold.py writes to sm_io.out_dir() == /opt/ml/checkpoints, synced continuously (each
    # finished construct survives a later interruption). No input channels. The --control sentinel keeps the
    # argparse happy (store_true); it is a no-op.
    sagemaker_submit.submit_spot(
        entry_point="entry_cofold.py", source_dir=os.path.join(here, "boltz_src"),
        base_job_name="fusion-cofold", output_prefix=dest_prefix,
        arguments=["--control"],
        instance=instance, max_run=max_runtime, sess=sess, role=role, wait=True,
    )
    print(f"done — results in s3://{bucket}/{dest_prefix}", flush=True)


if __name__ == "__main__":
    main()
