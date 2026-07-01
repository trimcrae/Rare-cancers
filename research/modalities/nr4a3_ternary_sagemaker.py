#!/usr/bin/env python3
"""
Submit the NR4A3–PROTAC–E3 ternary Boltz-2 prediction as an AWS SageMaker Processing job.

Same managed, auto-tears-down path as the MD pipeline (nr4a3_md_sagemaker.py): SageMaker provisions a
GPU container, installs boltz_src/requirements.txt, runs entry.py (which runs nr4a3_ternary.py --run),
enforces a HARD MaxRuntime cap, then terminates — nothing to shut off.

Driven from CI (gpu-ternary-aws.yml). Needs env: AWS creds + SAGEMAKER_ROLE_ARN. Optional
PROTAC_SMILES (forwarded to the job) once a warhead exists; absent, only the CRBN+ligand control runs.
"""
import os
import sys


def main():
    try:
        import sagemaker
        from sagemaker.processing import ProcessingOutput
        from sagemaker.processing import FrameworkProcessor
        from sagemaker.pytorch import PyTorch
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set (the SageMaker execution-role ARN)")
    instance = os.environ.get("INSTANCE", "ml.g5.2xlarge")            # A10G, more RAM for Boltz
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(6 * 3600)))   # hard cap
    protac = os.environ.get("PROTAC_SMILES", "")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    proc = FrameworkProcessor(
        estimator_cls=PyTorch,
        framework_version="2.3",
        py_version="py311",
        role=role,
        instance_count=1,
        instance_type=instance,
        max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-ternary",
        sagemaker_session=sess,
    )
    # SageMaker rejects an empty ContainerArguments list (min length 1), so in control mode (no PROTAC)
    # pass a benign --control sentinel rather than [].
    args = ["--protac-smiles", protac] if protac else ["--control"]
    print(f"submitting SageMaker ternary job: {instance}, protac={'set' if protac else 'control-only'}, "
          f"max_runtime={max_runtime}s, outputs -> s3://{bucket}/nr4a3-ternary", flush=True)
    proc.run(
        code="entry.py",
        source_dir=os.path.join(here, "boltz_src"),
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/nr4a3-ternary")],
        arguments=args,
        wait=True,
        logs=True,
    )
    print(f"done — results in s3://{bucket}/nr4a3-ternary", flush=True)


if __name__ == "__main__":
    main()
