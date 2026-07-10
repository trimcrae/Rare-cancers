#!/usr/bin/env python3
"""
Submit the 8XTT conformer-ensemble endpoint scoring (nr4a3_8xtt_conformer_scoring.py) as an AWS SageMaker
managed-**spot Training** job (trimcrae standing rule: default every GPU run to spot; ~60-70% cheaper in
billed hours, larger/parallel spot Training quota).

Docks denovo_401 + a decoy subset into EACH of the ~20 deposited 8XTT NMR conformers and MM-GBSA
endpoint-scores each pose, then per conformer ranks denovo_401 against the decoy endpoint-score null and
aggregates (#{conformers clearing the null}, denovo_401 rank distribution). NO extra input channels — 8XTT
(RCSB) and AF-Q92570 (AFDB, reference sequence only) are fetched at runtime.

Spot is safe: nr4a3_8xtt_conformer_scoring.py checkpoints the JSON after EACH (conformer, ligand) MM-GBSA
leg and checkpoint_s3_uri <-> /opt/ml/checkpoints is re-downloaded on a spot restart / re-dispatch, so an
interruption costs <=1 leg. GPU job (MM-GBSA has no CPU fallback); defaults ml.g5.xlarge. Needs AWS creds +
SAGEMAKER_ROLE_ARN. Driven from gpu-8xtt-conformer-scoring-aws.yml.
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
    # 20 conformers x (1 denovo_401 + DECOY_COUNT decoys) single-snapshot MM-GBSA legs -> generous cap; a
    # timeout just checkpoints and you re-dispatch (same prefix) to resume from the last (conformer,ligand).
    max_run = int(os.environ.get("MAX_RUNTIME", str(16 * 3600)))
    spot = os.environ.get("SPOT", "1") == "1"
    max_wait = int(os.environ.get("MAX_WAIT", str(int(max_run * 1.6)))) if spot else None
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-8xtt-conformer-scoring")
    git_ref = os.environ.get("GIT_REF", "main")
    models = os.environ.get("MODELS", "")
    decoy_count = os.environ.get("DECOY_COUNT", "")
    compute_timeout = os.environ.get("COMPUTE_TIMEOUT", "")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    ckpt = f"s3://{bucket}/{out_prefix}"                # /opt/ml/checkpoints <-> this (output + resume dir)

    hp = {"git-ref": git_ref}
    if models:
        hp["models"] = models
    if decoy_count:
        hp["decoy-count"] = decoy_count
    if compute_timeout:
        hp["compute-timeout"] = compute_timeout

    est = PyTorch(
        entry_point="entry_8xtt_conformer_scoring.py", source_dir=os.path.join(here, "sagemaker_src"),
        role=role, framework_version="2.3", py_version="py311",
        instance_count=1, instance_type=instance, sagemaker_session=sess,
        base_job_name="nr4a3-8xtt-conformer-scoring",
        use_spot_instances=spot, max_run=max_run, max_wait=max_wait,
        checkpoint_s3_uri=ckpt, checkpoint_local_path="/opt/ml/checkpoints",
        hyperparameters=hp,
    )
    print(f"submitting 8XTT conformer scoring: {instance} spot={spot}; "
          f"models={models or 'all'} decoys={decoy_count or '15'} -> checkpoints/results {ckpt}", flush=True)
    est.fit(wait=True, logs=True)
    print(f"done — results in {ckpt}/nr4a3-8xtt-conformer-scoring.json", flush=True)
    # Cost: g5.xlarge on-demand ~$1.01/hr (us-east-2); spot ~60-70% off in BILLED HOURS. Env build ~25 min +
    # 20 smina fan-out docks (all ligands/conformer, CPU) + 20 x (1+DECOY_COUNT) single-snapshot MM-GBSA
    # endpoint legs (~1-2 min each on the A10G). Default 15 decoys -> 20x16 = 320 legs -> ~9-14 h wall ->
    # ~$4-7 real spot cost (~$10-15 on-demand). Drop DECOY_COUNT to 12 (-> 20x13 = 260 legs) to save.
    # No FEP, NO multi-snapshot MD (single-snapshot MATCHES the denovo_401 endpoint tier).


if __name__ == "__main__":
    main()
