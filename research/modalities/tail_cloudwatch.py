#!/usr/bin/env python3
"""Read-only LIVE tail of a SageMaker job's CloudWatch logs — watch a RUNNING job without cancelling it.

Why this exists: GitHub Actions only renders a SageMaker job's streamed stdout when the wrapping step ENDS,
so during run 7 we could not see an 82-min hang without killing the job. But SageMaker streams that same
stdout to CloudWatch Logs in near-real-time. This script finds the most recent Processing job whose name
contains JOB_PREFIX and prints the last TAIL_LINES events from its /aws/sagemaker/ProcessingJobs streams —
so we can observe progress (the entry/compute heartbeats, the chosen OpenMM platform, per-ligand results)
live, on demand, via the tail-cloudwatch-aws.yml workflow.

Env: JOB_PREFIX (default nr4a3-mmgbsa), TAIL_LINES (default 200), AWS creds + AWS_DEFAULT_REGION.
Commits nothing; starts no instance.
"""
import os

import boto3

GROUP = "/aws/sagemaker/ProcessingJobs"


def main():
    prefix = os.environ.get("JOB_PREFIX", "nr4a3-mmgbsa")
    tail = int(os.environ.get("TAIL_LINES", "200"))
    sm = boto3.client("sagemaker")
    logs = boto3.client("logs")

    jobs = sm.list_processing_jobs(NameContains=prefix, SortBy="CreationTime",
                                   SortOrder="Descending", MaxResults=5)["ProcessingJobSummaries"]
    if not jobs:
        print(f"no SageMaker processing job matches NameContains={prefix!r}")
        return
    job = jobs[0]
    name = job["ProcessingJobName"]
    d = sm.describe_processing_job(ProcessingJobName=name)
    status = d["ProcessingJobStatus"]
    exitmsg = d.get("ExitMessage", "")
    print(f"job {name}")
    print(f"  status: {status}{(' / ' + exitmsg) if exitmsg else ''}")
    print(f"  created: {job['CreationTime']}   showing last {tail} CloudWatch events")
    print("=" * 88)

    events, token = [], None
    while True:
        kw = {"logGroupName": GROUP, "logStreamNamePrefix": name, "limit": 10000}
        if token:
            kw["nextToken"] = token
        try:
            resp = logs.filter_log_events(**kw)
        except logs.exceptions.ResourceNotFoundException:
            print("  (no CloudWatch stream yet — the job is probably still provisioning the instance)")
            return
        events.extend(resp.get("events", []))
        token = resp.get("nextToken")
        if not token or len(events) > 50000:
            break
    if not events:
        print("  (stream exists but no events yet)")
        return
    events.sort(key=lambda e: e["timestamp"])
    for e in events[-tail:]:
        print(e["message"].rstrip())


if __name__ == "__main__":
    main()
