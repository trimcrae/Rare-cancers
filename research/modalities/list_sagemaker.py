#!/usr/bin/env python3
"""Read-only: list in-progress SageMaker training jobs and how many spot INSTANCES they consume.

Answers "what is actually using the account 'instances across all spot training jobs' (=10) quota right
now?" — so we can reason about free slots instead of guessing. Prints each job's instance type/count,
spot flag, and SecondaryStatus (Starting/Downloading/Training), and totals the spot instances in use.

Env: AWS creds + AWS_DEFAULT_REGION. Starts nothing; describes only.
"""
import os

import boto3


def main():
    sm = boto3.client("sagemaker")
    jobs = sm.list_training_jobs(StatusEquals="InProgress", SortBy="CreationTime",
                                 SortOrder="Descending", MaxResults=50)["TrainingJobSummaries"]
    print(f"{len(jobs)} in-progress training jobs:")
    spot_instances = 0
    for j in jobs:
        name = j["TrainingJobName"]
        try:
            d = sm.describe_training_job(TrainingJobName=name)
        except Exception as e:  # noqa: BLE001
            print(f"  {name[:52]:52} describe failed: {e}"); continue
        rc = d.get("ResourceConfig", {})
        it, ic = rc.get("InstanceType", "?"), rc.get("InstanceCount", 1)
        spot = d.get("EnableManagedSpotTraining", False)
        sec = d.get("SecondaryStatus", "")
        if spot:
            spot_instances += ic
        print(f"  {name[:52]:52} {it:16} x{ic} spot={str(spot):5} {sec}")
    print(f"\nspot instances in use: {spot_instances} / 10 (account 'instances across all spot training jobs')")
    print(f"→ free spot slots (if quota=10): {max(0, 10 - spot_instances)}")


if __name__ == "__main__":
    main()
