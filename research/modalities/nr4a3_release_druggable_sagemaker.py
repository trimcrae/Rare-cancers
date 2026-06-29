#!/usr/bin/env python3
"""
Submit STEP 0 — the NR4A3 druggable-release receptor re-anchor — as an AWS SageMaker Processing job.

Mounts three S3 prefixes as ProcessingInputs:
  release : s3://<bucket>/nr4a3-release        (release_rep*.dcd)          -> /opt/ml/processing/input/release
  struct  : s3://<bucket>/nr4a3-metad          (nr4a3-lbd-solvated.pdb)    -> /opt/ml/processing/input/struct
  pocket  : s3://<bucket>/nr4a3-release-pocket (per-frame druggability)    -> /opt/ml/processing/input/pocket
Runs entry_release_druggable.py -> nr4a3_release_druggable.py, writes the receptor sub-ensemble +
manifest to s3://<bucket>/nr4a3-release-druggable.

CPU work (a handful of fpocket calls + Rg over the release trajectory) — defaults to ml.c5.2xlarge (no GPU
needed, separate quota from the g5 used by the MD/MM-GBSA steps). Driven from release-druggable-aws.yml.
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
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")     # CPU; this step never needs a GPU
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(2 * 3600)))
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-release-druggable")
    git_ref = os.environ.get("GIT_REF", "main")
    target_rg = os.environ.get("TARGET_RG", "0.737")
    n_alt = os.environ.get("N_ALT", "3")
    d_star = os.environ.get("D_STAR", "0.53")
    force_scan = os.environ.get("FORCE_SCAN", "")
    prefixes = {"release": os.environ.get("RELEASE_PREFIX", "nr4a3-release"),
                "struct": os.environ.get("STRUCT_PREFIX", "nr4a3-metad"),
                "pocket": os.environ.get("POCKET_PREFIX", "nr4a3-release-pocket")}

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    proc = FrameworkProcessor(
        estimator_cls=PyTorch, framework_version="2.3", py_version="py311", role=role,
        instance_count=1, instance_type=instance, max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-release-druggable", sagemaker_session=sess,
    )
    inputs = [ProcessingInput(source=f"s3://{bucket}/{prefixes[t]}",
                              destination=f"/opt/ml/processing/input/{t}", input_name=t)
              for t in ("release", "struct", "pocket")]
    print(f"submitting receptor re-anchor: {instance}; inputs " +
          ", ".join(f"{t}=s3://{bucket}/{prefixes[t]}" for t in prefixes) +
          f" -> s3://{bucket}/{out_prefix}", flush=True)
    args = ["--git-ref", git_ref, "--target-rg", target_rg, "--n-alt", n_alt, "--d-star", d_star]
    if force_scan:
        args += ["--force-scan", force_scan]
    proc.run(
        code="entry_release_druggable.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=inputs,
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/{out_prefix}")],
        arguments=args,
        wait=True, logs=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
