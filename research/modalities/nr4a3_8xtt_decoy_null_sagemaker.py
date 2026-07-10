#!/usr/bin/env python3
"""
Submit the MATCHED 8XTT-frame decoy null (nr4a3_8xtt_decoy_null.py) as an AWS SageMaker managed-**spot
Training** job (trimcrae standing rule: default every GPU run to spot; ~60-70% cheaper, parallel quota).

Runs the SAME 38 non-NR4A decoys through the SAME 4 druggable 8XTT conformers + SAME matrix paralogue
receptors + SAME single-snapshot MM-GBSA endpoint denovo_401's 8XTT re-dock used, and ranks denovo_401's
per-conformer NR4A3-selectivity margin against that frame-matched null. Reuses the matrix NR4A1/NR4A2
receptors (the `matrix` channel = s3://<bucket>/nr4a3-matrix) and mounts the denovo_401 re-dock result (the
`redock` channel = s3://<bucket>/nr4a3-8xtt-redock) so the null is ranked against the REAL denovo_401 margins.

Spot is safe: nr4a3_8xtt_decoy_null.py checkpoints the per-decoy JSON after EACH decoy and checkpoint_s3_uri
↔ /opt/ml/checkpoints is re-downloaded on a spot restart / re-dispatch, so an interruption costs ≤1 decoy.
GPU job (MM-GBSA has no CPU fallback); defaults ml.g5.xlarge. Needs AWS creds + SAGEMAKER_ROLE_ARN.
Driven from gpu-8xtt-decoy-null-aws.yml.

Prereq: the matrix job populated s3://<bucket>/<INPUT_PREFIX> (nr4a1-opened.pdb / nr4a2-opened.pdb) and the
8XTT re-dock populated s3://<bucket>/<REDOCK_PREFIX>/nr4a3-8xtt-redock-denovo401.json.
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
    # 38 decoys × (4 conformers + 2 paralogues) = 228 single-snapshot MM-GBSA legs → default a generous cap;
    # a timeout just checkpoints and you re-dispatch (same prefix) to resume from the last decoy.
    max_run = int(os.environ.get("MAX_RUNTIME", str(12 * 3600)))
    spot = os.environ.get("SPOT", "1") == "1"
    max_wait = int(os.environ.get("MAX_WAIT", str(int(max_run * 1.6)))) if spot else None
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-matrix")
    redock_prefix = os.environ.get("REDOCK_PREFIX", "nr4a3-8xtt-redock")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-8xtt-decoy-null")
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
        entry_point="entry_8xtt_decoy_null.py", source_dir=os.path.join(here, "sagemaker_src"),
        role=role, framework_version="2.3", py_version="py311",
        instance_count=1, instance_type=instance, sagemaker_session=sess,
        base_job_name="nr4a3-8xtt-decoy-null",
        use_spot_instances=spot, max_run=max_run, max_wait=max_wait,
        checkpoint_s3_uri=ckpt, checkpoint_local_path="/opt/ml/checkpoints",
        hyperparameters=hp,
    )
    print(f"submitting 8XTT decoy null: {instance} spot={spot}; matrix s3://{bucket}/{in_prefix} + "
          f"redock s3://{bucket}/{redock_prefix} → checkpoints/results {ckpt}", flush=True)
    est.fit({"matrix": TrainingInput(f"s3://{bucket}/{in_prefix}"),
             "redock": TrainingInput(f"s3://{bucket}/{redock_prefix}")}, wait=True, logs=True)
    print(f"done — results in {ckpt}/nr4a3-8xtt-decoy-null.json", flush=True)
    # Cost: g5.xlarge on-demand ~$1.01/hr (us-east-2); spot ~60-70% off in BILLED HOURS. Env build ~25 min +
    # 6 smina fan-out docks (all 38 decoys/receptor, CPU) + 228 single-snapshot MM-GBSA endpoint legs
    # (~1-2 min each on the A10G) → ~7-11 h wall → ~$3-5 real spot cost (~$8-11 on-demand). No FEP,
    # NO multi-snapshot MD (single-snapshot MATCHES the denovo_401 8XTT re-dock; multi-snapshot would be
    # ~10× the MD and UNMATCHED).


if __name__ == "__main__":
    main()
