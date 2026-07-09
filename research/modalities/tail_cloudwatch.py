#!/usr/bin/env python3
"""Read-only LIVE tail of a SageMaker job's CloudWatch logs — watch a RUNNING job without cancelling it.

Why this exists: GitHub Actions only renders a SageMaker job's streamed stdout when the wrapping step ENDS,
so during run 7 we could not see an 82-min hang without killing the job. But SageMaker streams that same
stdout to CloudWatch Logs in near-real-time. This script finds the most recent Processing job whose name
contains JOB_PREFIX and prints the last TAIL_LINES events from its /aws/sagemaker/ProcessingJobs streams —
so we can observe progress (the entry/compute heartbeats, the chosen OpenMM platform, per-ligand results)
live, on demand, via the tail-cloudwatch-aws.yml workflow.

Env: JOB_PREFIX (default nr4a3-mmgbsa), TAIL_LINES (default 200), JOB_TYPE (processing|training|auto,
default auto — spot fleets are Training jobs, docks/MM-GBSA are Processing), AWS creds + AWS_DEFAULT_REGION.
Commits nothing; starts no instance.
"""
import os

import boto3

PROC_GROUP = "/aws/sagemaker/ProcessingJobs"
TRAIN_GROUP = "/aws/sagemaker/TrainingJobs"


def _find_processing(sm, prefix):
    jobs = sm.list_processing_jobs(NameContains=prefix, SortBy="CreationTime",
                                   SortOrder="Descending", MaxResults=5)["ProcessingJobSummaries"]
    if not jobs:
        return None
    j = jobs[0]
    name = j["ProcessingJobName"]
    d = sm.describe_processing_job(ProcessingJobName=name)
    return {"name": name, "status": d["ProcessingJobStatus"], "exit": d.get("ExitMessage", ""),
            "created": j["CreationTime"], "group": PROC_GROUP}


def _find_training(sm, prefix):
    jobs = sm.list_training_jobs(NameContains=prefix, SortBy="CreationTime",
                                 SortOrder="Descending", MaxResults=5)["TrainingJobSummaries"]
    if not jobs:
        return None
    j = jobs[0]
    name = j["TrainingJobName"]
    d = sm.describe_training_job(TrainingJobName=name)
    # spot resume info is useful context when watching a Training job.
    sec = d.get("SecondaryStatus", "")
    # the latest SecondaryStatusTransition StatusMessage explains WHY a job is still Starting
    # (spot capacity wait vs image pull vs preparing instances) — the key signal for a parked spot job.
    trans = d.get("SecondaryStatusTransitions") or []
    msg = trans[-1].get("StatusMessage", "") if trans else ""
    return {"name": name, "status": d["TrainingJobStatus"] + (f" / {sec}" if sec else ""),
            "exit": d.get("FailureReason", "") or msg, "created": j["CreationTime"], "group": TRAIN_GROUP}


def _list_all(sm, prefix):
    """Diagnostic: print status/secondary/created/message for ALL recent matching jobs (both types).
    Answers 'is this job running, parked on spot capacity, or failed?' across a whole fleet at once."""
    print(f"=== recent SageMaker jobs matching NameContains={prefix!r} ===")
    try:
        tj = sm.list_training_jobs(NameContains=prefix, SortBy="CreationTime",
                                   SortOrder="Descending", MaxResults=12)["TrainingJobSummaries"]
    except Exception:  # noqa: BLE001
        tj = []
    for j in tj:
        d = sm.describe_training_job(TrainingJobName=j["TrainingJobName"])
        trans = d.get("SecondaryStatusTransitions") or []
        msg = (trans[-1].get("StatusMessage", "") if trans else "") or d.get("FailureReason", "") or ""
        print(f"[T] {j['TrainingJobName']:<44} {d['TrainingJobStatus']:>10}/{d.get('SecondaryStatus',''):<12} "
              f"{j['CreationTime']:%m-%d %H:%M}  {msg[:70]}")
    try:
        pj = sm.list_processing_jobs(NameContains=prefix, SortBy="CreationTime",
                                     SortOrder="Descending", MaxResults=8)["ProcessingJobSummaries"]
    except Exception:  # noqa: BLE001
        pj = []
    for j in pj:
        print(f"[P] {j['ProcessingJobName']:<44} {j['ProcessingJobStatus']:>10}  {j['CreationTime']:%m-%d %H:%M}")


def main():
    prefix = os.environ.get("JOB_PREFIX", "nr4a3-mmgbsa")
    tail = int(os.environ.get("TAIL_LINES", "200"))
    job_type = os.environ.get("JOB_TYPE", "auto").lower()
    sm = boto3.client("sagemaker")
    logs = boto3.client("logs")

    if os.environ.get("LIST_ALL") == "1":
        _list_all(sm, prefix)
        return

    # auto: pick whichever job-type has the more recent match (Training fleets vs Processing docks).
    finders = {"processing": _find_processing, "training": _find_training}
    if job_type in finders:
        job = finders[job_type](sm, prefix)
    else:
        cands = [j for j in (_find_processing(sm, prefix), _find_training(sm, prefix)) if j]
        job = max(cands, key=lambda j: j["created"]) if cands else None
    if not job:
        print(f"no SageMaker processing/training job matches NameContains={prefix!r}")
        return
    name, GROUP = job["name"], job["group"]
    status, exitmsg = job["status"], job["exit"]
    print(f"job {name}  [{'Training' if GROUP == TRAIN_GROUP else 'Processing'}]")
    print(f"  status: {status}{(' / ' + exitmsg) if exitmsg else ''}")
    print(f"  created: {job['created']}   showing last {tail} CloudWatch events")
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
