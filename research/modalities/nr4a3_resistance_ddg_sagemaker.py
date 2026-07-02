#!/usr/bin/env python3
"""Submit the warhead-pocket alanine scan (entry_resistance.py -> nr4a3_resistance_ddg.py) as a SageMaker
Processing job. Mirrors nr4a3_mmgbsa_sagemaker.py: mounts s3://<bucket>/nr4a3-matrix (receptors + docked
poses), writes s3://<bucket>/nr4a3-resistance-ddg with Continuous upload (per-residue checkpoints survive a
timeout). One ml.g5.xlarge GPU job — serialize behind other g5 jobs (one-concurrent-g5 account limit)."""
import os
import sys


def main():
    try:
        import sagemaker
        from sagemaker.processing import FrameworkProcessor, ProcessingInput, ProcessingOutput
        from sagemaker.pytorch import PyTorch
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3 first")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set")
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(150 * 60)))
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-matrix")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-resistance-ddg")
    git_ref = os.environ.get("GIT_REF", "main")
    compute_timeout = os.environ.get("COMPUTE_TIMEOUT", "")
    multisnapshot = os.environ.get("MULTISNAPSHOT", "1")
    frames = os.environ.get("MS_FRAMES", "")
    pose_name = os.environ.get("POSE_NAME", "denovo_401")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    proc = FrameworkProcessor(
        estimator_cls=PyTorch, framework_version="2.3", py_version="py311", role=role,
        instance_count=1, instance_type=instance, max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-resistance", sagemaker_session=sess,
    )
    inputs = [ProcessingInput(source=f"s3://{bucket}/{in_prefix}",
                              destination="/opt/ml/processing/input", input_name="matrix")]
    args = ["--git-ref", git_ref, "--multisnapshot", str(multisnapshot), "--pose-name", pose_name]
    if compute_timeout:
        args += ["--compute-timeout", str(compute_timeout)]
    if frames:
        args += ["--frames", str(frames)]
    print(f"submitting resistance scan: {instance}; s3://{bucket}/{in_prefix} -> s3://{bucket}/{out_prefix}",
          flush=True)
    proc.run(
        code="entry_resistance.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=inputs,
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/{out_prefix}", s3_upload_mode="Continuous")],
        arguments=args, wait=True, logs=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
