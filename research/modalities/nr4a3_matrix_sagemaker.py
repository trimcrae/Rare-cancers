#!/usr/bin/env python3
"""
Submit the NR4A family-wide selectivity matrix as an AWS SageMaker Processing job.

Mounts the three opened-ensemble prefixes (s3://<bucket>/{nr4a3-metad,nr4a1-metad,nr4a2-metad}) as
ProcessingInputs at /opt/ml/processing/input/{nr4a3,nr4a1,nr4a2}, runs entry_matrix.py ->
nr4a3_matrix.py, and writes s3://<bucket>/nr4a3-matrix. CPU work (docking into 3 opened pockets);
defaults to ml.g5.xlarge to reuse the GPU quota. Needs AWS creds + SAGEMAKER_ROLE_ARN.

Prereq: all three `*-metad` runs must have completed (verify the opened ensembles are in S3).
"""
import os
import sys


def main():
    try:
        import sagemaker
        import sagemaker_submit
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set (the SageMaker execution-role ARN)")
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(4 * 3600)))
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-matrix")
    git_ref = os.environ.get("GIT_REF", "main")
    # S3 prefixes for the three opened ensembles (override if named differently).
    prefixes = {"nr4a3": os.environ.get("NR4A3_PREFIX", "nr4a3-metad"),
                "nr4a1": os.environ.get("NR4A1_PREFIX", "nr4a1-metad"),
                "nr4a2": os.environ.get("NR4A2_PREFIX", "nr4a2-metad")}

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    # Gate-2 published-chemistry benchmark: activate the verified-SMILES panel (nr4a3_matrix.py reads
    # BENCHMARK_PANEL) when the output prefix marks a benchmark run, OR when BENCHMARK_PANEL is set explicitly.
    proc_env = {}
    if os.environ.get("BENCHMARK_PANEL") == "1" or "benchmark" in out_prefix.lower():
        proc_env["BENCHMARK_PANEL"] = "1"
        print("[submit] BENCHMARK_PANEL=1 -> appending the registry verified-SMILES Gate-2 panel", flush=True)

    inputs = {t: f"s3://{bucket}/{prefixes[t]}" for t in ("nr4a3", "nr4a1", "nr4a2")}
    print(f"submitting matrix: {instance}; inputs " +
          ", ".join(f"{t}=s3://{bucket}/{prefixes[t]}" for t in prefixes) +
          f" -> s3://{bucket}/{out_prefix}", flush=True)
    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME out_prefix the readers
    # expect; entry_matrix.py reads the three paralogue channels via sm_io.channel(name) and writes to
    # sm_io.out_dir(). env=(proc_env or None) is passed through unchanged as `environment`.
    sagemaker_submit.submit_spot(
        entry_point="entry_matrix.py", source_dir=os.path.join(here, "sagemaker_src"),
        base_job_name="nr4a3-matrix", output_prefix=out_prefix,
        inputs=inputs, arguments=["--git-ref", git_ref], environment=(proc_env or None),
        instance=instance, max_run=max_runtime, sess=sess, role=role, wait=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
