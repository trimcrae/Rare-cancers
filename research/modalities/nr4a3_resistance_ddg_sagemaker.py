#!/usr/bin/env python3
"""Submit the warhead-pocket alanine scan (entry_resistance.py -> nr4a3_resistance_ddg.py) as a SageMaker
Processing job. Mirrors nr4a3_mmgbsa_sagemaker.py: mounts s3://<bucket>/nr4a3-matrix (receptors + docked
poses), writes s3://<bucket>/nr4a3-resistance-ddg with Continuous upload (per-residue checkpoints survive a
timeout). One ml.g5.xlarge GPU job — serialize behind other g5 jobs (one-concurrent-g5 account limit)."""
import os
import sys


def main():
    try:
        import sagemaker
        import sagemaker_submit
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3 first")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set")
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(150 * 60)))
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-matrix")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-resistance-ddg")
    git_ref = os.environ.get("GIT_REF", "main")
    compute_timeout = os.environ.get("COMPUTE_TIMEOUT", "")
    multisnapshot = os.environ.get("MULTISNAPSHOT", "1")
    frames = os.environ.get("MS_FRAMES", "")
    pose_name = os.environ.get("POSE_NAME", "denovo_401")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    inputs = {"matrix": f"s3://{bucket}/{in_prefix}"}
    args = ["--git-ref", git_ref, "--multisnapshot", str(multisnapshot), "--pose-name", pose_name]
    if compute_timeout:
        args += ["--compute-timeout", str(compute_timeout)]
    if frames:
        args += ["--frames", str(frames)]
    print(f"submitting resistance scan: {instance}; s3://{bucket}/{in_prefix} -> s3://{bucket}/{out_prefix}",
          flush=True)
    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME out_prefix the readers
    # expect; entry mounts the matrix channel via sm_io.channel("matrix") and writes to sm_io.out_dir()
    # (== /opt/ml/checkpoints, synced to S3 CONTINUOUSLY so per-residue checkpoints survive a timeout).
    sagemaker_submit.submit_spot(
        entry_point="entry_resistance.py", source_dir=os.path.join(here, "sagemaker_src"),
        base_job_name="nr4a3-resistance", output_prefix=out_prefix,
        inputs=inputs, arguments=args,
        instance=instance, max_run=max_runtime, sess=sess, role=role, wait=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
