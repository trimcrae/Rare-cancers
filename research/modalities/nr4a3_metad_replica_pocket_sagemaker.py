#!/usr/bin/env python3
"""Submit PHASE 0 (metad convergence plan) — per-replica harmonized orthosteric-pocket scoring of the three
independent WTMetaD replicas — as an AWS SageMaker Processing job (CPU; no GPU quota).

Mounts each replica's checkpoint prefix (nr4a3-metad-r{1,2,3}/ckpt, containing nr4a3-lbd-metad.dcd +
nr4a3-lbd-solvated.pdb + HILLS/COLVAR/fes.dat) and runs entry_metad_replica_pocket.py, which scores each with
`nr4a3_mdpocket.py` under POCKET_MATCH=harmonized + pinned fpocket 4.2.3 and writes a consolidated
both-denominator per-replica table (metad-replica-pocket-summary.json). Output uploaded continuously.

Driven from metad-replica-pocket-aws.yml. Needs: AWS creds + SAGEMAKER_ROLE_ARN.
"""
import os
import sys


def main():
    try:
        import sagemaker
        import sagemaker_submit
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set (the SageMaker execution-role ARN)")
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")   # CPU; fpocket over metad frames
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(6 * 3600)))
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-metad-replica-pocket")
    git_ref = os.environ.get("GIT_REF", "main")
    pocket_match = os.environ.get("POCKET_MATCH", "harmonized")
    # per-replica metad checkpoint prefixes (each holds nr4a3-lbd-metad.dcd + topology + fes.dat)
    r1p = os.environ.get("R1_PREFIX", "nr4a3-metad-r1/ckpt")
    r2p = os.environ.get("R2_PREFIX", "nr4a3-metad-r2/ckpt")
    r3p = os.environ.get("R3_PREFIX", "nr4a3-metad-r3/ckpt")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    dest = f"s3://{bucket}/{out_prefix}"

    inputs = {
        "r1": f"s3://{bucket}/{r1p}",
        "r2": f"s3://{bucket}/{r2p}",
        "r3": f"s3://{bucket}/{r3p}",
    }
    print(f"submitting PHASE 0 metad-replica pocket scoring: {instance}, r1={r1p} r2={r2p} r3={r3p}, "
          f"match={pocket_match}, ref={git_ref} -> {dest}", flush=True)
    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME out_prefix the readers
    # expect; entry writes to sm_io.out_dir() == /opt/ml/checkpoints, synced continuously.
    sagemaker_submit.submit_spot(
        entry_point="entry_metad_replica_pocket.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        base_job_name="nr4a3-metad-replica-pocket", output_prefix=out_prefix,
        inputs=inputs,
        arguments=["--git-ref", git_ref, "--pocket-match", pocket_match],
        instance=instance, max_run=max_runtime, sess=sess, role=role, wait=True,
    )
    print(f"done — results in {dest} (see metad-replica-pocket-summary.json)", flush=True)


if __name__ == "__main__":
    main()
