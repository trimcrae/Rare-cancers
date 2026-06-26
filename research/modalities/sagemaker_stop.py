#!/usr/bin/env python3
"""
Stop in-progress SageMaker Processing jobs by name prefix — to free GPU when a run is no longer needed.

Necessary because cancelling the GitHub Actions wrapper does NOT stop the SageMaker job (it is an
independent AWS resource; we observed the 30 ns job run to completion after its wrapper was cancelled).
This calls StopProcessingJob on every InProgress job whose name contains JOB_PREFIX. Needs AWS creds.

JOB_PREFIX (env): base-job-name fragment to match (e.g. 'nr4a3-release'). Driven by sagemaker-stop-aws.yml.
"""
import os
import sys


def main():
    try:
        import boto3
    except ImportError:
        sys.exit("pip install boto3")
    prefix = os.environ.get("JOB_PREFIX", "").strip()
    if not prefix:
        sys.exit("JOB_PREFIX not set (the base-job-name fragment to stop, e.g. nr4a3-release)")

    sm = boto3.client("sagemaker")
    stopped, seen = [], []
    paginator = sm.get_paginator("list_processing_jobs")
    for page in paginator.paginate(StatusEquals="InProgress", NameContains=prefix):
        for job in page.get("ProcessingJobSummaries", []):
            name = job["ProcessingJobName"]
            seen.append(name)
            try:
                sm.stop_processing_job(ProcessingJobName=name)
                stopped.append(name)
                print(f"  stopped {name}", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"  could not stop {name}: {e}", file=sys.stderr)

    print(f"[stop] prefix='{prefix}': {len(seen)} in-progress job(s) matched, "
          f"{len(stopped)} stop requests sent", flush=True)
    if not seen:
        print("[stop] nothing to stop (no matching in-progress jobs).", flush=True)


if __name__ == "__main__":
    main()
