#!/usr/bin/env python3
"""
Submit de-novo warhead GENERATION as an AWS SageMaker Processing job (the only GPU spend in the de-novo
step; the screen runs free on a GitHub CPU runner).

Mounts s3://<bucket>/nr4a3-matrix at /opt/ml/processing/input (for the opened NR4A3 conformer DiffSBDD
conditions on), runs entry_denovo.py -> nr4a3_denovo.py MODE=generate on a GPU instance, and writes the
SMILES pool + generated SDFs to s3://<bucket>/nr4a3-denovo. Needs AWS creds + SAGEMAKER_ROLE_ARN.

GPU-cost rule (standing): this spins up a GPU instance — only dispatch after the AskUserQuestion
cost/payoff pop-up and after the release-run pocket gate has cleared. DiffSBDD provisioning is operator-
provided via DIFFSBDD_REPO / DIFFSBDD_CKPT_URL (passed through as job env); absent -> generation skips.
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
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-matrix")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-denovo")
    git_ref = os.environ.get("GIT_REF", "main")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    # Pass the (operator-provided) DiffSBDD provisioning + sampling knobs through to the job env.
    passthrough = {k: os.environ[k] for k in
                   ("DIFFSBDD_REPO", "DIFFSBDD_CKPT_URL", "N_PER_CAMPAIGN",
                    "ENV_BUILD_TIMEOUT", "COMPUTE_TIMEOUT") if os.environ.get(k)}

    proc = FrameworkProcessor(
        estimator_cls=PyTorch, framework_version="2.3", py_version="py311", role=role,
        instance_count=1, instance_type=instance, max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-denovo", sagemaker_session=sess, env=passthrough or None,
    )
    print(f"submitting denovo-generate: {instance}; input s3://{bucket}/{in_prefix} "
          f"-> s3://{bucket}/{out_prefix}; passthrough={list(passthrough)}", flush=True)
    proc.run(
        code="entry_denovo.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=[ProcessingInput(source=f"s3://{bucket}/{in_prefix}",
                                destination="/opt/ml/processing/input", input_name="matrix")],
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/{out_prefix}")],
        arguments=["--git-ref", git_ref],
        wait=True, logs=True,
    )
    print(f"done — pool in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
