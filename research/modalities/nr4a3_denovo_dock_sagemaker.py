#!/usr/bin/env python3
"""
Submit the DE-NOVO selectivity funnel (docking tier) as an AWS SageMaker Processing job.

Mounts four prefixes — nr4a3-denovo (candidates), nr4a3-release-druggable (Step-0 NR4A3 receptor),
nr4a1-metad, nr4a2-metad — runs entry_denovo_dock.py -> nr4a3_matrix.py (candidate mode), and writes
s3://<bucket>/nr4a3-denovo-matrix in the SAME format MM-GBSA consumes (nr4a3-matrix.json +
<tag>-opened.pdb + docked_<tag>.sdf). CPU work (smina docking) — defaults to ml.c5.2xlarge (~$0.3-0.7),
separate quota from the g5. Needs AWS creds + SAGEMAKER_ROLE_ARN. Driven from gpu-denovo-dock-aws.yml.
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
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")     # CPU; smina docking
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(4 * 3600)))
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-denovo-matrix")
    git_ref = os.environ.get("GIT_REF", "main")
    top_n = os.environ.get("TOP_N", "20")
    prefixes = {"denovo": os.environ.get("DENOVO_PREFIX", "nr4a3-denovo"),
                "receptor": os.environ.get("RECEPTOR_PREFIX", "nr4a3-release-druggable"),
                "nr4a1": os.environ.get("NR4A1_PREFIX", "nr4a1-metad"),
                "nr4a2": os.environ.get("NR4A2_PREFIX", "nr4a2-metad")}

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    proc = FrameworkProcessor(
        estimator_cls=PyTorch, framework_version="2.3", py_version="py311", role=role,
        instance_count=1, instance_type=instance, max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-denovo-dock", sagemaker_session=sess,
    )
    inputs = [ProcessingInput(source=f"s3://{bucket}/{prefixes[t]}",
                              destination=f"/opt/ml/processing/input/{t}", input_name=t)
              for t in ("denovo", "receptor", "nr4a1", "nr4a2")]
    print(f"submitting de-novo dock: {instance}, top {top_n}; inputs " +
          ", ".join(f"{t}=s3://{bucket}/{prefixes[t]}" for t in prefixes) +
          f" -> s3://{bucket}/{out_prefix}", flush=True)
    proc.run(
        code="entry_denovo_dock.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=inputs,
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/{out_prefix}")],
        arguments=["--git-ref", git_ref, "--top-n", str(top_n)],
        wait=True, logs=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
