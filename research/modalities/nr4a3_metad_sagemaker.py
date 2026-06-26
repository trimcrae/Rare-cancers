#!/usr/bin/env python3
"""
Submit the NR4A3 LBD metadynamics as an AWS SageMaker Processing job (managed, auto-tears-down).

Same managed-GPU path as nr4a3_md_sagemaker.py (entry_metad.py builds the CUDA OpenMM + PLUMED env).
Outputs (COLVAR, HILLS, trajectory, fes.dat, and the checkpoint/restart set) go to
s3://<default-bucket>/nr4a3-metad. Default MaxRuntime is 8 h to fit a ~30 ns biased run; raise
MAX_RUNTIME for longer NS.

RESUME_FROM env: continue a prior run's accumulated bias instead of starting fresh.
  - unset / ""     -> fresh run.
  - "auto"         -> resume from the default output prefix s3://<bucket>/nr4a3-metad (the latest run;
                      a completed run overwrites that prefix with its cumulative checkpoint + HILLS).
  - "s3://..."     -> resume from that explicit prefix.
A resume is refused inside nr4a3_metad.py if the CV or metad parameters changed.
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
    ns = os.environ.get("NS", "30")
    target = os.environ.get("TARGET", "NR4A3").upper()
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(8 * 3600)))   # hard cap, AWS kills the job
    git_ref = os.environ.get("GIT_REF", "main")   # repo ref the job clones + runs (default main)
    resume_from = os.environ.get("RESUME_FROM", "").strip()

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    # Output S3 prefix. Default keyed to the target (nr4a3-metad / nr4a1-metad / nr4a2-metad) so the
    # family runs don't overwrite each other; OUTPUT_PREFIX overrides.
    out_name = os.environ.get("OUTPUT_PREFIX") or f"{target.lower()}-metad"   # empty -> target default
    out_prefix = f"s3://{bucket}/{out_name}"

    # Resolve the resume source. "auto" -> the default output prefix (the latest cumulative run).
    resume_s3 = ""
    if resume_from.lower() == "auto":
        resume_s3 = out_prefix
    elif resume_from:
        resume_s3 = resume_from

    proc = FrameworkProcessor(
        estimator_cls=PyTorch,
        framework_version="2.3",
        py_version="py311",
        role=role,
        instance_count=1,
        instance_type=instance,
        max_runtime_in_seconds=max_runtime,
        base_job_name=out_name,
        sagemaker_session=sess,
    )

    arguments = ["--ns", str(ns), "--target", target, "--git-ref", git_ref]
    inputs = []
    if resume_s3:
        inputs.append(ProcessingInput(source=resume_s3, destination="/opt/ml/processing/resume",
                                      input_name="resume"))
        arguments += ["--resume-from", "/opt/ml/processing/resume"]

    print(f"submitting metadynamics: target={target}, {instance}, ns={ns}, ref={git_ref}, "
          f"resume_from={resume_s3 or '(fresh)'}, max_runtime={max_runtime}s -> {out_prefix}",
          flush=True)
    proc.run(
        code="entry_metad.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=inputs,
        outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination=out_prefix)],
        arguments=arguments,
        wait=True,
        logs=True,
    )
    print(f"done — results in {out_prefix}", flush=True)


if __name__ == "__main__":
    main()
