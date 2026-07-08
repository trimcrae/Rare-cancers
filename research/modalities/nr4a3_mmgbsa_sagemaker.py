#!/usr/bin/env python3
"""
Submit the MM-GBSA endpoint rescoring as an AWS SageMaker managed-**spot Training** job (trimcrae standing
rule 2026-07-03: default every GPU run to spot). Spot is ~60-70% cheaper and draws on the spot-Training
quota (parallel) instead of the on-demand g5 Processing quota of 1.

Spot is safe because the driver now RESUMES: `checkpoint_s3_uri` ↔ /opt/ml/checkpoints is re-populated with
the prior partial `nr4a3-mmgbsa.json` on a spot restart / re-dispatch, and nr4a3_mmgbsa.py skips ligands
already scored there — so a spot interruption costs ≤1 ligand. The matrix outputs (receptors + docked_*.sdf
+ nr4a3-matrix.json) are the `matrix` Training channel. GPU job; defaults ml.g5.xlarge. Needs AWS creds +
SAGEMAKER_ROLE_ARN. Re-dispatch with the SAME output_prefix to resume/extend.

Prereq: the matrix job populated s3://<bucket>/<INPUT_PREFIX> (receptors + docked_*.sdf + nr4a3-matrix.json).
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
    max_run = int(os.environ.get("MAX_RUNTIME", str(12 * 3600)))      # generous; timeout → resume on re-dispatch
    spot = os.environ.get("SPOT", "1") == "1"
    max_wait = int(os.environ.get("MAX_WAIT", str(int(max_run * 1.6)))) if spot else None
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-matrix")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-mmgbsa")
    git_ref = os.environ.get("GIT_REF", "main")
    compute_timeout = os.environ.get("COMPUTE_TIMEOUT", "")
    multisnapshot = os.environ.get("MULTISNAPSHOT", "")
    candidate_filter = os.environ.get("CANDIDATE_FILTER", "")
    ms_frames = os.environ.get("MMGBSA_FRAMES", "")
    target_timeout = os.environ.get("MMGBSA_TARGET_TIMEOUT", "")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    # checkpoint_s3_uri == the output prefix: /opt/ml/checkpoints ↔ s3://<bucket>/<out_prefix>, synced
    # continuously and re-downloaded on restart (the RESUME mechanism). Results land at
    # s3://<bucket>/<out_prefix>/nr4a3-mmgbsa.json, where report-mmgbsa-aws.yml reads them.
    ckpt = f"s3://{bucket}/{out_prefix}"

    hp = {"git-ref": git_ref}
    if compute_timeout:
        hp["compute-timeout"] = compute_timeout
    if multisnapshot:
        hp["multisnapshot"] = multisnapshot
    if candidate_filter:
        hp["candidate-filter"] = candidate_filter
    if ms_frames:
        hp["frames"] = ms_frames
    if target_timeout:
        hp["target-timeout"] = target_timeout

    est = PyTorch(
        entry_point="entry_mmgbsa.py", source_dir=os.path.join(here, "sagemaker_src"),
        role=role, framework_version="2.3", py_version="py311",
        instance_count=1, instance_type=instance, sagemaker_session=sess,
        base_job_name="nr4a3-mmgbsa",
        use_spot_instances=spot, max_run=max_run, max_wait=max_wait,
        checkpoint_s3_uri=ckpt, checkpoint_local_path="/opt/ml/checkpoints",
        hyperparameters=hp,
    )
    print(f"submitting mmgbsa: {instance} spot={spot}; matrix s3://{bucket}/{in_prefix} "
          f"→ checkpoints/results {ckpt}", flush=True)
    est.fit({"matrix": TrainingInput(f"s3://{bucket}/{in_prefix}")}, wait=True, logs=True)
    print(f"done — results in {ckpt}", flush=True)


if __name__ == "__main__":
    main()
