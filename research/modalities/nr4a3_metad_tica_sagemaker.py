#!/usr/bin/env python3
"""Submit the PHASE 2 SHAKEOUT (metad convergence plan) — well-tempered metadynamics on the DATA-DERIVED
slow coordinate, ONE NR4A3 seed — as an AWS SageMaker managed-**spot Training** job.

Phase 1 (TICA) found corr(IC1, Rg)=0.68 -> Rg is an incomplete reaction coordinate. This shakeout biases
the data-derived coordinate instead of Rg on a single NR4A3 seed, to prove the CV (i) fits from the
existing metad trajectories, (ii) wires into openmm-plumed as a COMBINE of pocket-lining Cα distances, and
(iii) drives opening/recrossing — the mandatory single-shard validation before the full 3-seed x
3-paralogue fleet (see nr4a3-metad-convergence-plan.md, Phase 2).

Mounts the 3 metad replica checkpoint prefixes (nr4a3-metad-r{1,2,3}/ckpt) as READ-ONLY Training input
channels (r1/r2/r3) so entry_metad_tica.py can fit the TICA CV. Spot Training (draws on the spot quota,
~60-70% cheaper) with native checkpoint/resume: checkpoint_s3_uri <-> /opt/ml/checkpoints holds phase2_cv.json
+ the metad restart set + HILLS/COLVAR/trajectory/fes.dat, uploaded continuously and pre-populated on a
spot restart or re-dispatch (same prefix -> resume).

Env: NS (default 8 = short shakeout), SEED (default 1), LAG_FRAMES (10), INSTANCE (ml.g5.xlarge), SPOT (1),
MAX_RUNTIME (per-attempt wall cap s), MAX_WAIT (spot; >= MAX_RUNTIME), OUTPUT_PREFIX, GIT_REF (main).
Needs AWS creds + SAGEMAKER_ROLE_ARN. Driven from metad-tica-shakeout-aws.yml.
"""
import os
import sys


def main():
    try:
        import sagemaker
        from sagemaker.inputs import TrainingInput
        from sagemaker.pytorch import PyTorch
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set (the SageMaker execution-role ARN)")
    ns = os.environ.get("NS", "8")
    seed = os.environ.get("SEED", "1").strip() or "1"
    lag_frames = os.environ.get("LAG_FRAMES", "10")
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    # 8 ns needs ~2.5-3 h of MD at NR4A LBD speeds (~80 ns/day) + env build + CV fit; default 8 h gives
    # ample headroom. A capacity-wait burns $0 and auto-resumes (do NOT switch to on-demand — standing rule).
    max_run = int(os.environ.get("MAX_RUNTIME", "").strip() or str(8 * 3600))
    spot = os.environ.get("SPOT", "1") == "1"
    _mw = os.environ.get("MAX_WAIT", "").strip()
    max_wait = (int(_mw) if _mw else int(max_run * 1.7)) if spot else None
    git_ref = os.environ.get("GIT_REF", "main")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    out_prefix = os.environ.get("OUTPUT_PREFIX") or "nr4a3-metad-tica-shakeout"
    ckpt = f"s3://{bucket}/{out_prefix}/ckpt"

    # The 3 existing metad replicas provide the trajectories the TICA CV is fit on (read-only).
    channels = {rep: TrainingInput(f"s3://{bucket}/nr4a3-metad-{rep}/ckpt", input_mode="File")
                for rep in ("r1", "r2", "r3")}

    est = PyTorch(
        entry_point="entry_metad_tica.py", source_dir=os.path.join(here, "sagemaker_src"),
        role=role, framework_version="2.3", py_version="py311",
        instance_count=1, instance_type=instance, sagemaker_session=sess,
        base_job_name=out_prefix,
        use_spot_instances=spot, max_run=max_run, max_wait=max_wait,
        checkpoint_s3_uri=ckpt, checkpoint_local_path="/opt/ml/checkpoints",
        hyperparameters={"ns": ns, "seed": seed, "lag-frames": lag_frames, "git-ref": git_ref},
    )
    print(f"submitting PHASE 2 shakeout: NR4A3 seed={seed}, {instance} spot={spot}, ns={ns}, "
          f"lag={lag_frames}, ref={git_ref}, max_run={max_run}s max_wait={max_wait}s -> {ckpt}",
          flush=True)
    est.fit(inputs=channels, wait=True, logs=True)
    print(f"done — phase2_cv.json + restart set + HILLS/COLVAR/trajectory/fes.dat in {ckpt}", flush=True)


if __name__ == "__main__":
    main()
