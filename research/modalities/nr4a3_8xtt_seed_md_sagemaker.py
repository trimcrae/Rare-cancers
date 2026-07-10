#!/usr/bin/env python3
"""
Submit the 8XTT-seeded unbiased release MD as an AWS SageMaker managed-**spot Training** job (same cheap,
resumable pattern as nr4a3_md_release_sagemaker.py).

BUILD-STATUS FLAG: this seeds unbiased MD from an EXPERIMENTAL 8XTT conformer by BUILDING a fresh solvated
system (the one new piece vs the metad release run, which resumes an existing system.xml). Everything else
(replica loop + per-interval checkpoint/resume, per-frame fpocket via nr4a3_mdpocket downstream) reuses the
release machinery. Validated only on the first cloud run (repo "launch-ready" convention).

Spot is safe: nr4a3_8xtt_seed_md.py checkpoints per interval and checkpoint_s3_uri ↔ /opt/ml/checkpoints is
re-downloaded on a spot restart / re-dispatch → RESUME + extend. NO input channel (8XTT + AF-Q92570 fetched
at runtime). GPU job; defaults ml.g5.xlarge. Needs AWS creds + SAGEMAKER_ROLE_ARN. Driven from
gpu-8xtt-seed-md-aws.yml. Re-dispatch with the SAME run_tag + output_prefix to resume/extend.

Follow-up (per-frame druggability): run gpu-mdpocket-aws.yml with DCD_NAME=8xtt_release_rep0.dcd on the
output prefix, exactly as the metad release run does.
"""
import os
import sys


def main():
    try:
        import sagemaker
        from sagemaker.pytorch import PyTorch
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set (the SageMaker execution-role ARN)")
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    max_run = int(os.environ.get("MAX_RUNTIME", str(5 * 3600)))
    spot = os.environ.get("SPOT", "1") == "1"
    max_wait = int(os.environ.get("MAX_WAIT", str(int(max_run * 1.6)))) if spot else None
    git_ref = os.environ.get("GIT_REF", "main")
    ns = os.environ.get("NS", "5")
    n_rep = os.environ.get("N_REP", "3")
    seed_model = os.environ.get("SEED_MODEL", "8")
    run_tag = os.environ.get("RUN_TAG", "8xtt_release")
    job_tag = run_tag.replace("_", "-")   # SageMaker training-job names forbid underscores
    checkpoint_every = os.environ.get("CHECKPOINT_EVERY", "10")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-8xtt-release")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    ckpt = f"s3://{bucket}/{out_prefix}/{run_tag}-ckpt"

    est = PyTorch(
        entry_point="entry_8xtt_seed_md.py", source_dir=os.path.join(here, "sagemaker_src"),
        role=role, framework_version="2.3", py_version="py311",
        instance_count=1, instance_type=instance, sagemaker_session=sess,
        base_job_name=f"nr4a3-8xtt-md-{job_tag}",
        use_spot_instances=spot, max_run=max_run, max_wait=max_wait,
        checkpoint_s3_uri=ckpt, checkpoint_local_path="/opt/ml/checkpoints",
        hyperparameters={"ns": ns, "n-rep": n_rep, "seed-model": seed_model,
                         "run-tag": run_tag, "checkpoint-every": checkpoint_every, "git-ref": git_ref},
    )
    print(f"submitting 8XTT-seeded MD [{run_tag}]: {instance} spot={spot}, {n_rep}×{ns} ns, seed model "
          f"{seed_model} → checkpoints {ckpt}", flush=True)
    est.fit(wait=True, logs=True)      # no input channel; wait → quota/capacity errors surface
    print(f"done — checkpoints/results in {ckpt}", flush=True)
    # Cost: g5.xlarge on-demand ~$1.01/hr; spot ~60-70% off in billed hours. Env build ~10-15 min + system
    # build/minimize + 3×5 ns unbiased MD (~1-2 h on an A10G) → ~$0.6-1.5 real spot cost for 3×5 ns.


if __name__ == "__main__":
    main()
