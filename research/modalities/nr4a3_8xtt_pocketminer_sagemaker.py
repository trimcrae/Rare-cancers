#!/usr/bin/env python3
"""
Submit the PocketMiner-on-8XTT cross-check as an AWS SageMaker Processing job (managed, auto-tears-down).

Re-runs the orthogonal cryptic-pocket GNN (PocketMiner) on the EXPERIMENTAL apo NR4A3 LBD (PDB 8XTT NMR
ensemble) instead of the AF2 model — the review's explicit ask. CPU work (small GNN inference + a Biopython
alignment; the runtime is dominated by the one-off TF conda-env build ~10-20 min). Defaults to
ml.c5.2xlarge, so it does NOT touch the GPU quota. Structures are fetched from RCSB/AFDB at runtime (no S3
input). Output (nr4a3-8xtt-pocketminer.json) -> s3://<default-bucket>/nr4a3-8xtt-pocketminer, uploaded
CONTINUOUSLY. Needs AWS creds + SAGEMAKER_ROLE_ARN. Driven from gpu-8xtt-pocketminer-aws.yml.

The PocketMiner env is TF-based and version-fragile (see research/modalities/pocketminer-run-notes.md) —
VALIDATE with one run before relying on the numbers.
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
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(3600)))
    git_ref = os.environ.get("GIT_REF", "main")
    models = os.environ.get("PM8_MODELS", "2,8,20,6")            # '2,8,20,6' or 'all'
    tf_version = os.environ.get("PM_TF_VERSION", "")             # optional PocketMiner TF pin

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    dest_prefix = "nr4a3-8xtt-pocketminer"
    out_prefix = f"s3://{bucket}/{dest_prefix}"

    print(f"submitting 8XTT PocketMiner cross-check: {instance}, ref={git_ref} -> {out_prefix}", flush=True)
    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME dest_prefix the
    # reader expects; entry writes to sm_io.out_dir() == /opt/ml/checkpoints, synced continuously.
    sagemaker_submit.submit_spot(
        entry_point="entry_8xtt_pm.py", source_dir=os.path.join(here, "pocketminer_src"),
        base_job_name="nr4a3-8xtt-pocketminer", output_prefix=dest_prefix,
        arguments=["--git-ref", git_ref, "--models", models] + (
            ["--tf-version", tf_version] if tf_version else []),
        instance=instance, max_run=max_runtime, sess=sess, role=role,
    )
    print(f"done — results in {out_prefix}/nr4a3-8xtt-pocketminer.json", flush=True)
    # Cost: ml.c5.2xlarge on-demand ~$0.41/hr (us-east-2); runtime dominated by the one-off TF env build
    # (~10-20 min) + a few conformers of seconds-long inference -> well under $0.50. No GPU spend.


if __name__ == "__main__":
    main()
