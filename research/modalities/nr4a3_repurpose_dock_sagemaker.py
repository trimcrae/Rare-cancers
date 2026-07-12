#!/usr/bin/env python3
"""
Submit the interruption-robust NR4A3-only drug-repurposing dock as an AWS SageMaker managed-**spot Training**
job (spot ~60-70% off; spot Training quota is separate from the on-demand Processing quota, so shards can run
more concurrently). Spot is safe here because the driver checkpoints per drug: `checkpoint_s3_uri`
bidirectionally syncs /opt/ml/checkpoints ↔ S3 — on start it DOWNLOADS any prior checkpoint (so a spot
interruption OR a re-dispatch with the same tag RESUMES + skips already-docked drugs), and UPLOADS
continuously during the run. A kill loses at most the one drug in flight.

Mounts the release-frame NR4A3 receptor as the `receptor` channel; the candidate shard JSON is read from the
cloned git_ref (committed in-repo), so no candidate S3 mount is needed. CPU job; defaults ml.c5.2xlarge.
Needs AWS creds + SAGEMAKER_ROLE_ARN. Driven from gpu-repurpose-dock-aws.yml.

Re-dispatch with the SAME shard + output_prefix to resume/extend.
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
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")            # CPU; smina docking
    max_run = int(os.environ.get("MAX_RUNTIME", str(5 * 3600)))       # per-attempt wall cap; timeout → resume
    spot = os.environ.get("SPOT", "1") == "1"
    max_wait = int(os.environ.get("MAX_WAIT", str(int(max_run * 1.6)))) if spot else None  # ≥ max_run for spot
    git_ref = os.environ.get("GIT_REF", "main")
    shard = os.environ.get("SHARD")
    if not shard:
        sys.exit("SHARD not set (e.g. nr4a3-repurpose-shard-02.json)")
    tag = os.environ.get("TAG", "") or shard.replace("nr4a3-repurpose-", "").replace(".json", "")
    exhaustiveness = os.environ.get("EXHAUSTIVENESS", "4")
    per_ligand_timeout = os.environ.get("PER_LIGAND_TIMEOUT", "300")
    receptor_prefix = os.environ.get("RECEPTOR_PREFIX", "nr4a3-release-druggable")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-repurpose-nr4a3only")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    # checkpoint_s3_uri IS the resume mechanism: SageMaker downloads its prior contents to /opt/ml/checkpoints
    # on start (spot restart OR fresh re-dispatch with the same tag), then uploads continuously.
    ckpt = f"s3://{bucket}/{out_prefix}/{tag}-ckpt"

    est = PyTorch(
        entry_point="entry_repurpose_dock.py", source_dir=os.path.join(here, "sagemaker_src"),
        role=role, framework_version="2.3", py_version="py311",
        instance_count=1, instance_type=instance, sagemaker_session=sess,
        base_job_name=f"nr4a3-repurpose-{tag}",
        use_spot_instances=spot, max_run=max_run, max_wait=max_wait,
        checkpoint_s3_uri=ckpt, checkpoint_local_path="/opt/ml/checkpoints",
        hyperparameters={"git-ref": git_ref, "shard": shard, "tag": tag,
                         "exhaustiveness": exhaustiveness, "per-ligand-timeout": per_ligand_timeout},
        # KEEP_POSES=1 retains docked poses + writes a combined docked_<r>.sdf into the checkpoint (RBFE
        # staging); default off (disk hygiene). Propagates to the dock subprocess via entry's os.environ.copy().
        environment={"KEEP_POSES": os.environ.get("KEEP_POSES", "0"),
                     "DOCKED_RECEPTOR": os.environ.get("DOCKED_RECEPTOR", "nr4a3")},
    )
    print(f"submitting repurpose dock [{tag}]: {instance} spot={spot}, shard={shard}, exh={exhaustiveness}, "
          f"receptor s3://{bucket}/{receptor_prefix} → checkpoints {ckpt}", flush=True)
    est.fit({"receptor": TrainingInput(f"s3://{bucket}/{receptor_prefix}")}, wait=True, logs=True)
    print(f"done — checkpoints/results in {ckpt}", flush=True)


if __name__ == "__main__":
    main()
