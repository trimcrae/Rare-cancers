#!/usr/bin/env python3
"""
Submit the unbiased MD (Gate-3 disambiguation / open-from-closed test) as an AWS SageMaker managed-**spot
Training** job — same cheap, resumable pattern as the FEP fleet (spot ~60-70% off; spot Training quota is 8,
vs the on-demand Processing quota of 1).

Spot is safe here because the harness checkpoints per interval: `checkpoint_s3_uri` bidirectionally syncs
/opt/ml/checkpoints ↔ S3 — on start it DOWNLOADS any prior checkpoints (so a spot interruption OR a re-dispatch
RESUMES + extends), and it UPLOADS continuously during the run. The metad outputs (system/topology/trajectory)
are mounted as the `metad` channel to seed from. GPU job; defaults ml.g5.xlarge. Needs AWS creds +
SAGEMAKER_ROLE_ARN. Driven from gpu-release-aws.yml.

RUN_TAG namespaces outputs so one harness runs both the persistence-from-open 'release' run and the
opening-from-closed run (TARGET_RG~0.48). Re-dispatch with the SAME run_tag + output_prefix to resume/extend.
"""
import os
import sys


def main():
    try:
        import sagemaker
        from sagemaker.pytorch import PyTorch
        from sagemaker.inputs import TrainingInput
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set (the SageMaker execution-role ARN)")
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    max_run = int(os.environ.get("MAX_RUNTIME", str(5 * 3600)))        # per-attempt wall cap; timeout → resume
    spot = os.environ.get("SPOT", "1") == "1"
    max_wait = int(os.environ.get("MAX_WAIT", str(int(max_run * 1.6)))) if spot else None  # ≥ max_run for spot
    git_ref = os.environ.get("GIT_REF", "main")
    ns = os.environ.get("NS", "5")
    n_rep = os.environ.get("N_REP", "3")
    target_rg = os.environ.get("TARGET_RG", "0.717")   # seed-frame CV Rg; ~0.48 = CLOSED; <=0 = max-Rg frontier
    run_tag = os.environ.get("RUN_TAG", "release")
    checkpoint_every = os.environ.get("CHECKPOINT_EVERY", "10")
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-metad")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-release")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    # checkpoint_s3_uri IS the resume mechanism: SageMaker downloads its prior contents to /opt/ml/checkpoints
    # on start (spot restart OR a fresh re-dispatch with the same prefix), then uploads continuously.
    ckpt = f"s3://{bucket}/{out_prefix}/{run_tag}-ckpt"

    est = PyTorch(
        entry_point="entry_release.py", source_dir=os.path.join(here, "sagemaker_src"),
        role=role, framework_version="2.3", py_version="py311",
        instance_count=1, instance_type=instance, sagemaker_session=sess,
        base_job_name=f"nr4a3-md-{run_tag}",
        use_spot_instances=spot, max_run=max_run, max_wait=max_wait,
        checkpoint_s3_uri=ckpt, checkpoint_local_path="/opt/ml/checkpoints",
        hyperparameters={"ns": ns, "n-rep": n_rep, "target-rg": target_rg,
                         "run-tag": run_tag, "checkpoint-every": checkpoint_every, "git-ref": git_ref},
    )
    print(f"submitting unbiased MD [{run_tag}]: {instance} spot={spot}, {n_rep}×{ns} ns, seed Rg {target_rg}, "
          f"metad s3://{bucket}/{in_prefix} → checkpoints {ckpt}", flush=True)
    est.fit({"metad": TrainingInput(f"s3://{bucket}/{in_prefix}")}, wait=True, logs=True)  # wait → quota errors surface
    print(f"done — checkpoints/results in {ckpt}", flush=True)


if __name__ == "__main__":
    main()
