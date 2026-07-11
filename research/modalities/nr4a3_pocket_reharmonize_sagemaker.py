#!/usr/bin/env python3
"""
Submit the NR4A3 pocket RE-HARMONIZATION as an AWS SageMaker Processing job (CPU).

Re-scores EVERY load-bearing ensemble (AF2 static, the NR-panel calibration structures, all 20 8XTT
conformers, the metad trajectory frames, and the 3 unbiased release replicas) with the score-INDEPENDENT
orthosteric-pocket matcher (POCKET_MATCH=harmonized) and the PINNED fpocket build (4.2.3), and emits one
consolidated both-denominator detection table (pocket-reharmonize-summary.json).

Mounts the metad + release S3 prefixes (topology + trajectories); AF2/8XTT/calibration structures are
fetched from AFDB/RCSB at runtime. CPU work (fpocket) -> defaults to a CPU instance (does NOT touch the
GPU quota). Output uploaded CONTINUOUSLY (per-ensemble JSONs + the consolidated table reach S3 as written;
a timeout keeps the last partial as the deliverable — CLAUDE.md checkpoint rule).

Driven from gpu-pocket-reharmonize-aws.yml. Needs: AWS creds + SAGEMAKER_ROLE_ARN.
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
    instance = os.environ.get("INSTANCE", "ml.c5.4xlarge")   # CPU; fpocket over many frames wants cores
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(8 * 3600)))
    metad_prefix = os.environ.get("METAD_PREFIX", "nr4a3-metad")
    release_prefix = os.environ.get("RELEASE_PREFIX", "nr4a3-release")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-pocket-reharmonize")
    git_ref = os.environ.get("GIT_REF", "main")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    dest = f"s3://{bucket}/{out_prefix}"

    # Managed-SPOT Training (was on-demand Processing): the metad + release prefixes mount as the "metad"
    # and "release" channels (entry reads sm_io.channel("metad")/("release")); checkpoint_s3_uri = the SAME
    # out_prefix, synced continuously (per-ensemble JSONs + the consolidated table reach S3 as written).
    inputs = {
        "metad": f"s3://{bucket}/{metad_prefix}",
        "release": f"s3://{bucket}/{release_prefix}",
    }
    print(f"submitting pocket re-harmonize: {instance}, metad={metad_prefix}, release={release_prefix}, "
          f"ref={git_ref} -> {dest}", flush=True)
    sagemaker_submit.submit_spot(
        entry_point="entry_pocket_reharmonize.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        base_job_name="nr4a3-pocket-reharmonize",
        output_prefix=out_prefix,
        inputs=inputs,
        arguments=["--git-ref", git_ref,
                   "--pocket-match", os.environ.get("POCKET_MATCH", "harmonized")],
        instance=instance, max_run=max_runtime, sess=sess, role=role, wait=True,
    )
    print(f"done — results in {dest} (see pocket-reharmonize-summary.json)", flush=True)


if __name__ == "__main__":
    main()
