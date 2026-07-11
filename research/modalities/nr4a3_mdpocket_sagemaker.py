#!/usr/bin/env python3
"""
Submit the NR4A3 MD-trajectory pocket analysis as an AWS SageMaker Processing job.

Pulls the MD outputs from s3://<default-bucket>/nr4a3-md via the "traj" input channel, runs the mdpocket/SASA
analysis (entry_mdpocket.py), and writes results to s3://<default-bucket>/nr4a3-mdpocket. This is CPU
work but defaults to ml.g5.xlarge so it reuses the GPU processing quota you already have (avoids a
separate CPU-instance quota request); override INSTANCE to a CPU type once that quota exists.

Driven from CI (gpu-mdpocket-aws.yml). Needs: AWS creds + SAGEMAKER_ROLE_ARN.
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
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(2 * 3600)))   # hard cap
    # Which trajectory to analyze. Defaults to the plain MD; point at the metad run by setting
    # INPUT_PREFIX=nr4a3-metad, DCD_NAME=nr4a3-lbd-metad.dcd, OUTPUT_PREFIX=nr4a3-metad-pocket.
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-md")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-mdpocket")
    dcd_name = os.environ.get("DCD_NAME", "nr4a3-lbd-md.dcd")
    # Optional separate source for nr4a3-lbd-solvated.pdb when the trajectory prefix lacks it (e.g. analyse
    # release_rep0.dcd from nr4a3-release with the topology from nr4a3-metad). Empty = co-located in in_prefix.
    struct_prefix = os.environ.get("STRUCTURE_PREFIX", "")
    git_ref = os.environ.get("GIT_REF", "main")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    # channel "traj" = the trajectory prefix; optional channel "structure" = a separate solvated-PDB prefix.
    # The --structure-dir argument now carries the CHANNEL NAME; entry_mdpocket resolves it via sm_io.channel.
    inputs = {"traj": f"s3://{bucket}/{in_prefix}"}
    extra_args = []
    if struct_prefix:
        inputs["structure"] = f"s3://{bucket}/{struct_prefix}"
        extra_args = ["--structure-dir", "structure"]
    print(f"submitting analysis: {instance}, trajectory={dcd_name} from {in_prefix}"
          f"{', structure from ' + struct_prefix if struct_prefix else ''} "
          f"-> s3://{bucket}/{out_prefix}", flush=True)
    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME out_prefix the reader
    # expects; entry writes to sm_io.out_dir() == /opt/ml/checkpoints, synced continuously.
    sagemaker_submit.submit_spot(
        entry_point="entry_mdpocket.py", source_dir=os.path.join(here, "sagemaker_src"),
        base_job_name="nr4a3-mdpocket", output_prefix=out_prefix,
        inputs=inputs,
        arguments=["--dcd-name", dcd_name, "--git-ref", git_ref] + extra_args,
        instance=instance, max_run=max_runtime, sess=sess, role=role,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
