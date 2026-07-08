#!/usr/bin/env python3
"""Stop a running SageMaker Training/Processing job (cleanly release an orphan).

Cancelling the wrapping GitHub Actions run kills the `est.fit`/`proc.run` WAIT but does NOT stop the
SageMaker job itself — it keeps running (or, for spot, keeps retrying for capacity) independently. When we
re-dispatch onto a different instance/pool with the same checkpoint prefix, that orphan is a write-race.
This read-then-stop utility issues StopTrainingJob/StopProcessingJob so only one writer owns the prefix.

Env:
  JOB_NAME    exact job name to stop (preferred; unambiguous), OR
  JOB_PREFIX  NameContains filter — stops the most recent *InProgress* match of the given TYPE.
  JOB_TYPE    training | processing (default training).
  AWS creds + AWS_DEFAULT_REGION.
Idempotent: a job already Stopping/terminal is reported, not an error.
"""
import os

import boto3


def main():
    name = os.environ.get("JOB_NAME", "").strip()
    prefix = os.environ.get("JOB_PREFIX", "").strip()
    job_type = os.environ.get("JOB_TYPE", "training").lower()
    sm = boto3.client("sagemaker")

    if job_type == "processing":
        stop, describe, keyname, statuskey = (sm.stop_processing_job, sm.describe_processing_job,
                                              "ProcessingJobName", "ProcessingJobStatus")
        if not name:
            jobs = sm.list_processing_jobs(NameContains=prefix, StatusEquals="InProgress",
                                           SortBy="CreationTime", SortOrder="Descending",
                                           MaxResults=10)["ProcessingJobSummaries"]
            names = [j["ProcessingJobName"] for j in jobs]
        else:
            names = [name]
    else:
        stop, describe, keyname, statuskey = (sm.stop_training_job, sm.describe_training_job,
                                              "TrainingJobName", "TrainingJobStatus")
        if not name:
            jobs = sm.list_training_jobs(NameContains=prefix, StatusEquals="InProgress",
                                         SortBy="CreationTime", SortOrder="Descending",
                                         MaxResults=10)["TrainingJobSummaries"]
            names = [j["TrainingJobName"] for j in jobs]
        else:
            names = [name]

    if not names:
        print(f"no in-progress {job_type} job matches "
              f"{('JOB_NAME=' + name) if name else ('JOB_PREFIX=' + prefix)!r}")
        return
    for nm in names:
        try:
            st = describe(**{keyname: nm})[statuskey]
        except Exception as e:  # noqa: BLE001
            print(f"  {nm}: describe failed ({e})"); continue
        if st != "InProgress":
            print(f"  {nm}: already {st} — nothing to stop"); continue
        try:
            stop(**{keyname: nm})
            print(f"  {nm}: StopJob requested (was InProgress)")
        except Exception as e:  # noqa: BLE001
            print(f"  {nm}: stop failed ({e})")


if __name__ == "__main__":
    main()
