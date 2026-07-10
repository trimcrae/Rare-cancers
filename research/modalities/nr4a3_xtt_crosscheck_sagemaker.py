#!/usr/bin/env python3
"""
Submit the AF2-model-vs-8XTT experimental cross-check as an AWS SageMaker Processing job (managed,
auto-tears-down).

CPU work (fpocket + Biopython on the AF2 NR4A3 LBD model and the 8XTT NMR ensemble, fetched from
AFDB + RCSB at runtime). Defaults to ml.c5.2xlarge (no GPU -> no ABFE/GPU-quota contention). No
ProcessingInput. Output (nr4a3-xtt-crosscheck.json) -> s3://<default-bucket>/nr4a3-xtt-crosscheck.
Needs AWS creds + SAGEMAKER_ROLE_ARN. Driven from gpu-xtt-crosscheck-aws.yml.

Cost note: c5.2xlarge on-demand ~ $0.41/hr (us-east-2); runtime is dominated by the one-off conda env
build (~10-20 min) + fpocket on ~20 NMR models (seconds each) -> well under $0.25 per run. No GPU spend.
"""
import os
import sys


def main():
    try:
        import sagemaker
        from sagemaker.processing import FrameworkProcessor, ProcessingOutput
        from sagemaker.pytorch import PyTorch
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set (the SageMaker execution-role ARN)")
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(2 * 3600)))
    git_ref = os.environ.get("GIT_REF", "main")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    out_prefix = f"s3://{bucket}/nr4a3-xtt-crosscheck"

    proc = FrameworkProcessor(
        estimator_cls=PyTorch,
        framework_version="2.3",
        py_version="py311",
        role=role,
        instance_count=1,
        instance_type=instance,
        max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-xtt-crosscheck",
        sagemaker_session=sess,
    )
    print(f"submitting 8XTT cross-check: {instance}, ref={git_ref} -> {out_prefix}", flush=True)
    proc.run(
        code="entry_xtt_crosscheck.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination=out_prefix,
                                  s3_upload_mode="Continuous")],
        arguments=["--git-ref", git_ref],
        wait=True,
        logs=True,
    )
    print(f"done — results in {out_prefix}/nr4a3-xtt-crosscheck.json", flush=True)


if __name__ == "__main__":
    main()
