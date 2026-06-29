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
        from sagemaker.processing import FrameworkProcessor, ProcessingInput, ProcessingOutput
        from sagemaker.pytorch import PyTorch
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

    proc = FrameworkProcessor(
        estimator_cls=PyTorch, framework_version="2.3", py_version="py311", role=role,
        instance_count=1, instance_type=instance, max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-denovo", sagemaker_session=sess,
    )
    print(f"submitting de-novo generation: {instance}, campaign={campaign}, n={n_samples}, "
          f"receptor=s3://{bucket}/{in_prefix} -> s3://{bucket}/{out_prefix}", flush=True)
    arguments = ["--git-ref", git_ref, "--n-samples", str(n_samples), "--campaign", campaign,
                 "--num-nodes-list", num_nodes_list]
    if ckpt_url:
        arguments += ["--ckpt-url", ckpt_url]
    proc.run(
        code="entry_denovo.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=[ProcessingInput(source=f"s3://{bucket}/{in_prefix}",
                                destination="/opt/ml/processing/input/receptor", input_name="receptor")],
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/{out_prefix}")],
        arguments=arguments,
        wait=True, logs=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
