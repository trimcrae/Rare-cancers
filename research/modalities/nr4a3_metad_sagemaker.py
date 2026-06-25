#!/usr/bin/env python3
"""
Submit the NR4A3 LBD metadynamics as an AWS SageMaker Processing job (managed, auto-tears-down).

Same managed-GPU path as nr4a3_md_sagemaker.py (entry_metad.py builds the CUDA OpenMM + PLUMED env).
Outputs (COLVAR, HILLS, trajectory, fes.dat) go to s3://<default-bucket>/nr4a3-metad. Default
MaxRuntime is 8 h to fit a ~30 ns biased run; raise MAX_RUNTIME for longer NS.
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
    ns = os.environ.get("NS", "30")
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(8 * 3600)))   # hard cap, AWS kills the job

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
        base_job_name="nr4a3-metad",
        sagemaker_session=sess,
    )
    print(f"submitting metadynamics: {instance}, ns={ns}, max_runtime={max_runtime}s -> "
          f"s3://{bucket}/nr4a3-metad", flush=True)
    proc.run(
        code="entry_metad.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/nr4a3-metad")],
        arguments=["--ns", str(ns)],
        wait=True,
        logs=True,
    )
    print(f"done — results in s3://{bucket}/nr4a3-metad", flush=True)


if __name__ == "__main__":
    main()
