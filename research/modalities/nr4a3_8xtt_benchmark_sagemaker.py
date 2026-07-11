#!/usr/bin/env python3
"""
Submit the 8XTT benchmark as an AWS SageMaker Processing job (managed, auto-tears-down).

CPU work: fpocket on the ~20 8XTT NMR conformers + a Biopython alignment + pure-Python superposition.
Structures are fetched from RCSB/AFDB at runtime (no ProcessingInput). Defaults to a CPU instance
(ml.c5.2xlarge; fpocket is CPU — does NOT touch the GPU quota). Output (nr4a3-8xtt-benchmark.json +
per-conformer fpocket runs) -> s3://<default-bucket>/nr4a3-8xtt-benchmark, uploaded CONTINUOUSLY so the
per-conformer JSON checkpoints reach S3 as they're written (a timeout/crash keeps the last partial as the
deliverable — CLAUDE.md checkpoint rule). Needs AWS creds + SAGEMAKER_ROLE_ARN. Driven from
gpu-8xtt-benchmark-aws.yml.
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
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(2 * 3600)))
    git_ref = os.environ.get("GIT_REF", "main")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    out_prefix = "nr4a3-8xtt-benchmark"

    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME out_prefix the readers
    # expect; entry_8xtt.py writes to sm_io.out_dir() (== /opt/ml/checkpoints, synced to S3 CONTINUOUSLY).
    # No ProcessingInput — structures are fetched from public RCSB/AFDB at runtime.
    print(f"submitting 8XTT benchmark: {instance}, ref={git_ref} -> s3://{bucket}/{out_prefix}", flush=True)
    sagemaker_submit.submit_spot(
        entry_point="entry_8xtt.py", source_dir=os.path.join(here, "sagemaker_src"),
        base_job_name="nr4a3-8xtt-benchmark", output_prefix=out_prefix,
        arguments=["--git-ref", git_ref],
        instance=instance, max_run=max_runtime, sess=sess, role=role, wait=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
