#!/usr/bin/env python3
"""Submit the anti-target / off-target panel dock as a SageMaker managed-spot Training job (CPU smina).

Mounts the prepared panel receptors (PANEL_PREFIX) as the `panel` channel; the survivor candidate JSON is read
from the cloned git_ref (committed in-repo). Checkpoints per (drug,target) pair to checkpoint_s3_uri, so a spot
kill / re-dispatch resumes and skips done pairs. Needs AWS creds + SAGEMAKER_ROLE_ARN.

Re-dispatch with the SAME tag + output_prefix to resume/extend.
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
        sys.exit("SAGEMAKER_ROLE_ARN not set")
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")            # CPU; smina docking
    max_run = int(os.environ.get("MAX_RUNTIME", str(5 * 3600)))
    spot = os.environ.get("SPOT", "1") == "1"
    max_wait = int(os.environ.get("MAX_WAIT", str(int(max_run * 1.6)))) if spot else None
    git_ref = os.environ.get("GIT_REF", "main")
    candidates = os.environ.get("CANDIDATES")
    if not candidates:
        sys.exit("CANDIDATES not set (survivor JSON filename under research/modalities)")
    tag = os.environ.get("TAG", "panel")
    exhaustiveness = os.environ.get("EXHAUSTIVENESS", "8")
    per_ligand_timeout = os.environ.get("PER_LIGAND_TIMEOUT", "300")
    panel_prefix = os.environ.get("PANEL_PREFIX", "nr4a3-antitarget-panel")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-antitarget")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    ckpt = f"s3://{bucket}/{out_prefix}/{tag}-ckpt"

    est = PyTorch(
        entry_point="entry_antitarget.py", source_dir=os.path.join(here, "sagemaker_src"),
        role=role, framework_version="2.3", py_version="py311",
        instance_count=1, instance_type=instance, sagemaker_session=sess,
        base_job_name=f"nr4a3-antitarget-{tag}",
        use_spot_instances=spot, max_run=max_run, max_wait=max_wait,
        checkpoint_s3_uri=ckpt, checkpoint_local_path="/opt/ml/checkpoints",
        hyperparameters={"git-ref": git_ref, "candidates": candidates, "tag": tag,
                         "exhaustiveness": exhaustiveness, "per-ligand-timeout": per_ligand_timeout},
    )
    print(f"submitting anti-target dock [{tag}]: {instance} spot={spot}, candidates={candidates}, "
          f"exh={exhaustiveness}, panel s3://{bucket}/{panel_prefix} → checkpoints {ckpt}", flush=True)
    est.fit({"panel": TrainingInput(f"s3://{bucket}/{panel_prefix}")}, wait=True, logs=True)
    print(f"done — results in {ckpt}", flush=True)


if __name__ == "__main__":
    main()
