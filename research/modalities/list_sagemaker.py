#!/usr/bin/env python3
"""Read-only: list in-progress SageMaker training jobs and how many spot INSTANCES they consume.

Answers "what is actually using the account 'instances across all spot training jobs' (=8) quota right
now?" — so we can reason about free slots instead of guessing. Prints each job's instance type/count,
spot flag, and SecondaryStatus (Starting/Downloading/Training), and totals the spot instances in use.

MODES (env MODE; blank = the in-progress listing above):
  savings   - realized managed-spot discount (billable vs training time) over the ~40 most recent jobs.
  abfe_rate - the MEASURED per-leg rate of the independent-window ABFE engine, over the FULL job history
              filtered by name. This is the only place a completed ABFE leg's billable time is read, and it
              is what `abfe_selectivity_cost.py` prices the CREBBP/BRD4 selectivity benchmark from.

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

    # MODE=abfe_rate: the MEASURED per-leg rate for the independent-window ABFE engine (nr4a3_abfe.py).
    #
    # WHY THIS EXISTS. Pricing the CREBBP/BRD4 selectivity benchmark needs GPU-hours per leg, and the repo had
    # no home for one: `vast_cost_model.LADDER_REFERENCE_GPU_H` covers the OpenFE RBFE/ternary lanes only, and
    # the ABFE engine is a different protocol on a different instance type. The `savings` mode above cannot
    # reach these jobs — it walks the ~40 most recent completed jobs, and the ABFE legs ran 2026-07-06..07-12
    # with hundreds of jobs since. So this mode pages the FULL job list filtered by name.
    #
    # WHAT IT REPORTS, AND WHY THE HYPERPARAMETERS ARE PART OF IT (CLAUDE.md §4b — a populated field is not a
    # measured one): billable seconds alone cannot be converted into a rate, because a leg's work is
    # `n_windows x n_iter x steps_per_iter` and every one of those is a per-job dispatch input. A job's own
    # recorded `n-iter` is what it RAN, so the rate is derived per job from its own settings rather than from
    # an assumed protocol. A job whose hyperparameters do not say is reported as UNPRICEABLE, not defaulted.
    if os.environ.get("MODE", "").strip().lower() == "abfe_rate":
        needle = (os.environ.get("INSTANCE_FILTER", "").strip() or "abfe")
        print(f"ABFE leg rate — every completed training job whose NAME contains {needle!r}\n")
        summaries, token = [], None
        while True:
            kw = {"StatusEquals": "Completed", "SortBy": "CreationTime", "SortOrder": "Descending",
                  "MaxResults": 100, "NameContains": needle}
            if token:
                kw["NextToken"] = token
            page = sm.list_training_jobs(**kw)
            summaries += page["TrainingJobSummaries"]
            token = page.get("NextToken")
            if not token:
                break
        print(f"  {len(summaries)} completed job(s) matched\n")
        hdr = (f"  {'job':52} {'instance':14} {'spot':5} {'billable_h':>10} {'train_h':>8} "
               f"{'mode':9} {'n_iter':>7} {'spi':>5} {'s/iter':>7}")
        print(hdr); print("  " + "-" * (len(hdr) - 2))
        for s in summaries:
            name = s["TrainingJobName"]
            try:
                d = sm.describe_training_job(TrainingJobName=name)
            except Exception as e:  # noqa: BLE001
                print(f"  {name[:52]:52} describe failed: {e}"); continue
            hp = d.get("HyperParameters", {}) or {}
            it = d.get("ResourceConfig", {}).get("InstanceType", "?")
            spot = d.get("EnableManagedSpotTraining", False)
            bt, tt = d.get("BillableTimeInSeconds"), d.get("TrainingTimeInSeconds")
            jmode = str(hp.get("mode", "?")).strip('"')
            ni, spi = str(hp.get("n-iter", "")).strip('"'), str(hp.get("steps-per-iter", "")).strip('"')
            sched = str(hp.get("lambda-schedule", "standard")).strip('"')
            nwin = 16 if sched == "dense" else 12
            # s/iter is per WINDOW-ITERATION: a leg job runs its n_windows windows SERIALLY inside one job
            # (nr4a3_abfe.run_shard loops over them), so total iterations = n_windows x n_iter.
            try:
                sper = f"{bt / (nwin * int(ni)):.2f}" if (bt and ni) else "-"
            except (TypeError, ValueError, ZeroDivisionError):
                sper = "-"
            print(f"  {name[:52]:52} {it:14} {str(spot):5} "
                  f"{(f'{bt/3600:.3f}' if bt else '-'):>10} {(f'{tt/3600:.3f}' if tt else '-'):>8} "
                  f"{jmode[:9]:9} {(ni or '-'):>7} {(spi or '-'):>5} {sper:>7}")
        print("\ns/iter = billable_s / (n_windows x n_iter) — INCLUDES each job's one-off setup (env solve when")
        print("not pre-baked, S3 download, PDBFixer + solvation + parameterisation), so it is an UPPER bound on")
        print("the steady-state MD rate and a FAIR basis for pricing a whole leg. n_windows is read from each")
        print("job's own lambda-schedule hyperparameter (dense=16, else 12), never assumed.")
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
    # Account 'ml.g5.xlarge for spot training job usage' quota = 8 (confirmed by a live ResourceLimitExceeded:
    # "limit is 8 Instances, current utilization 8"). NOT 10 — an earlier note that said 10 was wrong.
    SPOT_QUOTA = 8
    print(f"\nspot instances in use: {spot_instances} / {SPOT_QUOTA} (account 'instances across all spot "
          f"training jobs')")
    print(f"→ free spot slots (quota={SPOT_QUOTA}): {max(0, SPOT_QUOTA - spot_instances)}")


if __name__ == "__main__":
    main()
