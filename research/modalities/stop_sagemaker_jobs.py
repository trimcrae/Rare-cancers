#!/usr/bin/env python3
"""
Kill-switch: stop in-progress SageMaker Processing jobs (frees the single g5 quota slot / cost control).

Cancelling a GitHub workflow does NOT stop the SageMaker job it launched — the job keeps running on the
instance until it finishes or hits MaxRuntime. This calls StopProcessingJob on every InProgress job
(optionally filtered by NAME_PREFIX) so the slot frees immediately. Uses boto3 directly on the GitHub
runner (no GPU instance needed). The CI user has sagemaker:ListProcessingJobs/StopProcessingJob.
"""
import os
import sys

import boto3

PREFIX = os.environ.get("NAME_PREFIX", "")   # e.g. "nr4a3-metad"; empty = all in-progress jobs


def main():
    sm = boto3.client("sagemaker")
    jobs = sm.list_processing_jobs(StatusEquals="InProgress", MaxResults=100).get(
        "ProcessingJobSummaries", [])
    targets = [j["ProcessingJobName"] for j in jobs
               if not PREFIX or j["ProcessingJobName"].startswith(PREFIX)]
    if not targets:
        print(f"no in-progress processing jobs{f' matching {PREFIX!r}' if PREFIX else ''}")
        return
    for name in targets:
        print(f"stopping {name}", flush=True)
        sm.stop_processing_job(ProcessingJobName=name)
    print(f"requested stop on {len(targets)} job(s)")


if __name__ == "__main__":
    main()
