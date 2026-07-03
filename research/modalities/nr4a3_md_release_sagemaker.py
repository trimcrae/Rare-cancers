#!/usr/bin/env python3
"""
Submit the unbiased "release" MD (Gate-3 disambiguation) as an AWS SageMaker Processing job.

Mounts the metad outputs (s3://<bucket>/nr4a3-metad) so the job can seed from the opened conformer, runs
N_REP unbiased replicas of NS ns each (default 3 x 5 ns ~ 4 h, under GitHub's 6 h wrapper cap), and
writes the Rg traces + release_summary.json to s3://<bucket>/nr4a3-release. GPU job; defaults to
ml.g5.xlarge. Needs AWS creds + SAGEMAKER_ROLE_ARN. Driven from gpu-release-aws.yml.
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
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(5 * 3600)))   # under the 6 h GitHub job cap
    git_ref = os.environ.get("GIT_REF", "main")
    ns = os.environ.get("NS", "5")
    n_rep = os.environ.get("N_REP", "3")
    target_rg = os.environ.get("TARGET_RG", "0.717")   # seed-frame CV Rg; <=0 = legacy max-Rg frontier
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-metad")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-release")
    run_tag = os.environ.get("RUN_TAG", "release")     # namespaces outputs; "openfromclosed" for the from-closed run
    checkpoint_every = os.environ.get("CHECKPOINT_EVERY", "10")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    # RESUME: if the output prefix already holds a checkpoint (a prior run of THIS tag), mount it so the job
    # continues its trajectories instead of re-seeding — "pick up where we left off, don't repeat compute".
    # Guarded so the FIRST run (empty prefix) doesn't try to mount a nonexistent channel.
    import boto3
    have_prior = bool(boto3.client("s3").list_objects_v2(
        Bucket=bucket, Prefix=f"{out_prefix}/{run_tag}_rep", MaxKeys=1).get("KeyCount", 0))
    resume_inputs = []
    if have_prior:
        print(f"[release] prior checkpoint found under s3://{bucket}/{out_prefix} — mounting for RESUME", flush=True)
        resume_inputs = [ProcessingInput(source=f"s3://{bucket}/{out_prefix}",
                                         destination="/opt/ml/processing/resume")]

    proc = FrameworkProcessor(
        estimator_cls=PyTorch, framework_version="2.3", py_version="py311", role=role,
        instance_count=1, instance_type=instance, max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-release", sagemaker_session=sess,
    )
    print(f"submitting release MD: {instance}, {n_rep}x{ns} ns, ref={git_ref}, "
          f"s3://{bucket}/{in_prefix} -> s3://{bucket}/{out_prefix}", flush=True)
    proc.run(
        code="entry_release.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=[ProcessingInput(source=f"s3://{bucket}/{in_prefix}",
                                destination="/opt/ml/processing/input")] + resume_inputs,
        # Continuous upload: per-block state checkpoints reach S3 as written, so a timeout/spot-kill loses only
        # the last checkpoint interval and the run can be extended later (default EndOfJob would lose it all).
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/{out_prefix}", s3_upload_mode="Continuous")],
        arguments=["--ns", str(ns), "--n-rep", str(n_rep), "--target-rg", str(target_rg),
                   "--run-tag", run_tag, "--checkpoint-every", checkpoint_every, "--git-ref", git_ref],
        wait=True, logs=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
