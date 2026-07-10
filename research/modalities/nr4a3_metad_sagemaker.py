#!/usr/bin/env python3
"""
Submit the NR4A3 LBD metadynamics as an AWS SageMaker managed-**spot Training** job (one job per
independent-seed replica).

Converted from an on-demand Processing job (which serialized on the single on-demand g5 quota) to a
managed-spot Training job (same pattern as nr4a3_md_release_sagemaker.py / nr4a3_fep_sagemaker.py):
  * spot is ~60-70% cheaper AND draws on the larger spot Training quota (8), so >=3 seed replicas run
    CONCURRENTLY instead of serially;
  * checkpoint_s3_uri <-> /opt/ml/checkpoints gives native, spot-safe resume — SageMaker downloads the
    prior restart set on start (spot interruption OR fresh re-dispatch with the same prefix) and uploads
    continuously, so a kill loses <=1 checkpoint (~100 ps). This IS the resume mechanism; no
    --resume-from staging is needed.

Per replica: SEED picks the initial velocities + Langevin noise (independent realization) and keys the
S3 prefix, default nr4a3-metad-r{seed}, so replicas never share a HILLS file. Dispatch one job per seed
(gpu-metad-aws.yml with different `seed` inputs) to get the >=3 independent metad realizations the
reviewer asked for. Re-dispatch the SAME seed to resume/extend that replica (resumes from its checkpoint).

Env: SEED (default 1), NS (default 30), TARGET (NR4A3), INSTANCE (ml.g5.xlarge), SPOT (1), MAX_RUNTIME
(per-attempt wall cap, s), MAX_WAIT (spot; >= MAX_RUNTIME), OUTPUT_PREFIX (override the per-seed default),
GIT_REF (main). Needs AWS creds + SAGEMAKER_ROLE_ARN. Driven from gpu-metad-aws.yml.
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
    ns = os.environ.get("NS", "30")
    target = os.environ.get("TARGET", "NR4A3").upper()
    seed = os.environ.get("SEED", "1").strip() or "1"
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    # Per-ATTEMPT wall cap (spot interruption/timeout -> resume from checkpoint, not a loss). 30 ns needs
    # ~9-10 h of MD at NR4A LBD speeds (~80 ns/day); default 12 h gives headroom. max_wait must be >=
    # max_run for spot (run time + capacity wait); a capacity-wait burns $0 and auto-resumes (do NOT
    # switch to on-demand — standing rule).
    max_run = int(os.environ.get("MAX_RUNTIME", str(12 * 3600)))
    spot = os.environ.get("SPOT", "1") == "1"
    max_wait = int(os.environ.get("MAX_WAIT", str(int(max_run * 1.7)))) if spot else None
    git_ref = os.environ.get("GIT_REF", "main")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    # Per-seed S3 prefix so replicas are isolated (never share HILLS). OUTPUT_PREFIX overrides.
    out_prefix = os.environ.get("OUTPUT_PREFIX") or f"{target.lower()}-metad-r{seed}"
    # checkpoint_s3_uri IS the resume mechanism: SageMaker downloads its prior contents to
    # /opt/ml/checkpoints on start (spot restart OR a re-dispatch with the same prefix), then uploads
    # continuously. The metad restart set + HILLS/COLVAR/trajectory/fes.dat all live here.
    ckpt = f"s3://{bucket}/{out_prefix}/ckpt"

    est = PyTorch(
        entry_point="entry_metad.py", source_dir=os.path.join(here, "sagemaker_src"),
        role=role, framework_version="2.3", py_version="py311",
        instance_count=1, instance_type=instance, sagemaker_session=sess,
        base_job_name=out_prefix,
        use_spot_instances=spot, max_run=max_run, max_wait=max_wait,
        checkpoint_s3_uri=ckpt, checkpoint_local_path="/opt/ml/checkpoints",
        hyperparameters={"ns": ns, "target": target, "seed": seed, "git-ref": git_ref},
    )
    print(f"submitting metadynamics replica: target={target}, seed={seed}, {instance} spot={spot}, "
          f"ns={ns}, ref={git_ref}, max_run={max_run}s max_wait={max_wait}s -> checkpoints {ckpt}",
          flush=True)
    est.fit(wait=True, logs=True)   # wait -> quota/capacity errors surface in the log
    print(f"done — restart set + HILLS/COLVAR/trajectory/fes.dat in {ckpt}", flush=True)


if __name__ == "__main__":
    main()
