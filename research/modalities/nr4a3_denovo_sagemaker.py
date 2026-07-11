#!/usr/bin/env python3
"""
Submit STEP 2 — DiffSBDD pocket-conditioned NR4A3 warhead generation — as an AWS SageMaker Processing job.

Mounts the Step-0 receptor outputs (s3://<bucket>/nr4a3-release-druggable) at
/opt/ml/processing/input/receptor, runs entry_denovo.py -> nr4a3_denovo.py (DiffSBDD generation +
cheminformatics + pose handle-contact), and writes s3://<bucket>/nr4a3-denovo. GPU job (ml.g5.xlarge;
DiffSBDD diffusion on the A10G). Needs AWS creds + SAGEMAKER_ROLE_ARN. Driven from gpu-denovo-aws.yml.

PILOT default N_SAMPLES=200 (~$2-5). Watch live with tail-cloudwatch-aws.yml (job_prefix=nr4a3-denovo).
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
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(4 * 3600)))
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-release-druggable")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-denovo")
    git_ref = os.environ.get("GIT_REF", "main")
    n_samples = os.environ.get("N_SAMPLES", "200")
    campaign = os.environ.get("CAMPAIGN", "selective")
    num_nodes_list = os.environ.get("NUM_NODES_LIST", "24,28,32,36")
    ckpt_url = os.environ.get("CKPT_URL", "")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    print(f"submitting de-novo generation: {instance}, campaign={campaign}, n={n_samples}, "
          f"receptor=s3://{bucket}/{in_prefix} -> s3://{bucket}/{out_prefix}", flush=True)
    arguments = ["--git-ref", git_ref, "--n-samples", str(n_samples), "--campaign", campaign,
                 "--num-nodes-list", num_nodes_list]
    if ckpt_url:
        arguments += ["--ckpt-url", ckpt_url]
    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME out_prefix the readers
    # expect; entry_denovo.py writes to sm_io.out_dir() == /opt/ml/checkpoints (synced continuously) and reads
    # the receptor from sm_io.channel("receptor").
    sagemaker_submit.submit_spot(
        entry_point="entry_denovo.py", source_dir=os.path.join(here, "sagemaker_src"),
        base_job_name="nr4a3-denovo", output_prefix=out_prefix,
        inputs={"receptor": f"s3://{bucket}/{in_prefix}"},
        arguments=arguments,
        instance=instance, max_run=max_runtime, sess=sess, role=role, wait=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
