#!/usr/bin/env python3
"""
Submit the NR4A3 metadynamics convergence + orthogonal-CV analysis as a SageMaker Processing job (CPU).

Pulls a metad replica's outputs (HILLS, COLVAR, nr4a3-lbd-solvated.pdb, nr4a3-lbd-metad.dcd) from its
S3 checkpoint prefix (default nr4a3-metad-r{seed}/ckpt), runs nr4a3_metad_analysis.py, and writes the
convergence + orthogonal-CV + recrossing + 2D-reweight results to s3://<bucket>/<output_prefix>.

This is the cheap CPU follow-up to the GPU metad replicas (no GPU quota used): defaults to a CPU
ml.c5.2xlarge (overridable). Run it once per replica (INPUT_PREFIX=nr4a3-metad-r1/ckpt, r2, r3) to get
per-realization convergence, then compare across replicas. Driven from metad-analysis-aws.yml.

Env: INPUT_PREFIX (metad replica checkpoint prefix), OUTPUT_PREFIX, DCD_NAME (nr4a3-lbd-metad.dcd),
STRUCTURE_PREFIX (empty = co-located), BLOCK_NS (10), INSTANCE (ml.c5.2xlarge), MAX_RUNTIME, GIT_REF.
Needs AWS creds + SAGEMAKER_ROLE_ARN.
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
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")   # CPU: no GPU quota contention
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(3 * 3600)))
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-metad-r1/ckpt")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-metad-analysis")
    dcd_name = os.environ.get("DCD_NAME", "nr4a3-lbd-metad.dcd")
    struct_prefix = os.environ.get("STRUCTURE_PREFIX", "")
    block_ns = os.environ.get("BLOCK_NS", "10")
    git_ref = os.environ.get("GIT_REF", "main")

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
        base_job_name="nr4a3-metad-analysis",
        sagemaker_session=sess,
    )
    inputs = [ProcessingInput(source=f"s3://{bucket}/{in_prefix}",
                              destination="/opt/ml/processing/input")]
    extra_args = []
    if struct_prefix:
        inputs.append(ProcessingInput(source=f"s3://{bucket}/{struct_prefix}",
                                      destination="/opt/ml/processing/structure"))
        extra_args = ["--structure-dir", "/opt/ml/processing/structure"]
    print(f"submitting metad analysis: {instance}, trajectory={dcd_name} from {in_prefix}, "
          f"block_ns={block_ns} -> s3://{bucket}/{out_prefix}", flush=True)
    proc.run(
        code="entry_metad_analysis.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=inputs,
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/{out_prefix}")],
        arguments=["--dcd-name", dcd_name, "--block-ns", block_ns, "--git-ref", git_ref] + extra_args,
        wait=True,
        logs=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
