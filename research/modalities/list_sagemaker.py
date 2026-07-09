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
    # Optional: list an S3 prefix (e.g. to confirm cached opened-conformer PDBs exist) then return.
    s3_prefix = os.environ.get("S3_PREFIX", "").strip()
    if s3_prefix:
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
        s3, sts = boto3.client("s3"), boto3.client("sts")
        acct = sts.get_caller_identity()["Account"]
        bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
        print(f"s3://{bucket}/{s3_prefix} :")
        r = s3.list_objects_v2(Bucket=bucket, Prefix=s3_prefix)
        for o in r.get("Contents", []):
            print(f"  {o['Size']:>10}  {o['Key']}")
        if "Contents" not in r:
            print("  (empty / not found)")
        return

    sm = boto3.client("sagemaker")

    # MODE=savings: for recent COMPLETED/STOPPED jobs, print BillableTimeInSeconds vs
    # TrainingTimeInSeconds so we can read the REALIZED managed-spot discount off real jobs
    # instead of trusting a quoted "60-70%" average. Savings = (1 - Billable/Training) * 100
    # (AWS's own formula). If Billable ≈ Training the job was barely interrupted, so there is
    # NO hours-based saving and the on-demand-vs-spot comparison is purely the per-hour rate.
    if os.environ.get("MODE", "").strip().lower() == "savings":
        want = os.environ.get("INSTANCE_FILTER", "").strip()  # e.g. "ml.g5.xlarge"; blank = all
        n = int(os.environ.get("LOOKBACK", "40"))
        summaries = []
        for status in ("Completed", "Stopped"):
            summaries += sm.list_training_jobs(StatusEquals=status, SortBy="CreationTime",
                                               SortOrder="Descending", MaxResults=n)["TrainingJobSummaries"]
        summaries.sort(key=lambda s: s["CreationTime"], reverse=True)
        print(f"Realized managed-spot savings, last ~{n} completed/stopped jobs"
              + (f" (filter: {want})" if want else "") + ":\n")
        hdr = f"  {'job':44} {'instance':15} {'spot':5} {'billable_h':>10} {'training_h':>11} {'savings%':>8}"
        print(hdr); print("  " + "-" * (len(hdr) - 2))
        for s in summaries[:n]:
            name = s["TrainingJobName"]
            try:
                d = sm.describe_training_job(TrainingJobName=name)
            except Exception as e:  # noqa: BLE001
                print(f"  {name[:44]:44} describe failed: {e}"); continue
            it = d.get("ResourceConfig", {}).get("InstanceType", "?")
            if want and want not in it:
                continue
            spot = d.get("EnableManagedSpotTraining", False)
            bt = d.get("BillableTimeInSeconds")
            tt = d.get("TrainingTimeInSeconds")
            bh = f"{bt/3600:.3f}" if bt else "-"
            th = f"{tt/3600:.3f}" if tt else "-"
            sav = f"{(1 - bt/tt)*100:.1f}" if (bt and tt) else "-"
            print(f"  {name[:44]:44} {it:15} {str(spot):5} {bh:>10} {th:>11} {sav:>8}")
        print("\nsavings% = (1 - billable/training)*100. ~0 means the job ran uninterrupted, so managed")
        print("spot bought no hours discount — compare the per-hour rate on the bill to on-demand instead.")
        return

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
