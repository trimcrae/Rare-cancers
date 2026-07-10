#!/usr/bin/env python3
"""
Submit the 8XTT re-dock + MM-GBSA of denovo_401 as an AWS SageMaker managed-**spot Training** job
(trimcrae standing rule: default every GPU run to spot; ~60-70% cheaper, parallel spot-Training quota).

Docks denovo_401 into the druggable experimental 8XTT conformers and MM-GBSA-rescores, reusing the matrix
NR4A1/NR4A2 receptors+poses (the `matrix` Training channel = s3://<bucket>/nr4a3-matrix) as the paralogue
baseline. Spot is safe: nr4a3_8xtt_redock.py checkpoints the per-conformer JSON after EACH conformer and
checkpoint_s3_uri ↔ /opt/ml/checkpoints is re-downloaded on a spot restart / re-dispatch, so an interruption
costs ≤1 conformer. GPU job (MM-GBSA has no CPU fallback); defaults ml.g5.xlarge. Needs AWS creds +
SAGEMAKER_ROLE_ARN. Driven from gpu-8xtt-redock-aws.yml.

Prereq: the matrix job populated s3://<bucket>/<INPUT_PREFIX> (nr4a1-opened.pdb / nr4a2-opened.pdb +
docked_nr4a1.sdf / docked_nr4a2.sdf + nr4a3-matrix.json).
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
    max_run = int(os.environ.get("MAX_RUNTIME", str(6 * 3600)))        # timeout → resume on re-dispatch
    spot = os.environ.get("SPOT", "1") == "1"
    max_wait = int(os.environ.get("MAX_WAIT", str(int(max_run * 1.6)))) if spot else None
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-matrix")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-8xtt-redock")
    git_ref = os.environ.get("GIT_REF", "main")
    models = os.environ.get("MODELS", "")
    compute_timeout = os.environ.get("COMPUTE_TIMEOUT", "")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    ckpt = f"s3://{bucket}/{out_prefix}"                # /opt/ml/checkpoints ↔ this (output + resume dir)

    hp = {"git-ref": git_ref}
    if models:
        hp["models"] = models
    if compute_timeout:
        hp["compute-timeout"] = compute_timeout

    est = PyTorch(
        entry_point="entry_8xtt_redock.py", source_dir=os.path.join(here, "sagemaker_src"),
        role=role, framework_version="2.3", py_version="py311",
        instance_count=1, instance_type=instance, sagemaker_session=sess,
        base_job_name="nr4a3-8xtt-redock",
        use_spot_instances=spot, max_run=max_run, max_wait=max_wait,
        checkpoint_s3_uri=ckpt, checkpoint_local_path="/opt/ml/checkpoints",
        hyperparameters=hp,
    )
    print(f"submitting 8XTT re-dock: {instance} spot={spot}; matrix s3://{bucket}/{in_prefix} "
          f"→ checkpoints/results {ckpt}", flush=True)
    est.fit({"matrix": TrainingInput(f"s3://{bucket}/{in_prefix}")}, wait=True, logs=True)
    print(f"done — results in {ckpt}/nr4a3-8xtt-redock-denovo401.json", flush=True)
    # Cost: g5.xlarge on-demand ~$1.01/hr (us-east-2); spot ~60-70% off in billed hours. Env build ~20-30
    # min + 8XTT/AF2 fetch + smina docks + ~6 MM-GBSA endpoint legs (minutes on GPU) → ~30-45 min wall →
    # ~$0.30-0.60 real spot cost. No FEP.


if __name__ == "__main__":
    main()
