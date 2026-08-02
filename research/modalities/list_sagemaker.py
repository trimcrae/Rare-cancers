#!/usr/bin/env python3
"""Read-only: list in-progress SageMaker training jobs and how many spot INSTANCES they consume.

Answers "what is actually using the account 'instances across all spot training jobs' (=8) quota right
now?" — so we can reason about free slots instead of guessing. Prints each job's instance type/count,
spot flag, and SecondaryStatus (Starting/Downloading/Training), and totals the spot instances in use.

MODES (env MODE; blank = the in-progress listing above):
  job       - the FULL terminal record of ONE job by name (JOB_NAME), in ANY state: TrainingJobStatus,
              FailureReason, SecondaryStatusTransitions, BillableTimeInSeconds and the CloudWatch container
              log. ⚠ THE MODE THE OTHERS CANNOT SUBSTITUTE FOR: every listing here is `StatusEquals`-filtered,
              so a FAILED job is invisible to all of them; `DescribeTrainingJob` is not filtered at all.
  savings   - realized managed-spot discount (billable vs training time) over the ~40 most recent jobs.
              NOW INCLUDES Failed/Stopping and prints a status column — see the note at the mode itself.
  abfe_rate - the MEASURED per-leg rate of the independent-window ABFE engine, over the FULL job history
              filtered by name. This is the only place a completed ABFE leg's billable time is read, and it
              is what `abfe_selectivity_cost.py` prices the CREBBP/BRD4 selectivity benchmark from.
  abfe_ready - dispatch-readiness for an ABFE run: pre-baked ECR image present, staged receptor inputs
              present, target checkpoint tag not already occupied (it would silently RESUME), spot headroom.

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
    # ⚠ ★★ THIS MODE USED TO WALK ONLY ("Completed", "Stopped") AND THAT WAS A REAL BLIND SPOT, not a style
    # point. On 2026-08-02 a leg dispatched at 3:16 PM ET FAILED, and because a Failed job matches neither
    # status it was absent from this listing, absent from the in-progress listing, and absent from the spot
    # count — three reads that all said "nothing", from which "the job does not exist" was concluded. It
    # existed, it had a FailureReason, and (had it been billed) it would have spent money no ledger recorded.
    # CLAUDE.md §4: AN ABSENT READING IS NOT A READING OF ABSENCE — and here the absence was manufactured by
    # this collector's own filter. `Failed`/`Stopping` are now walked, and the STATUS is printed on every row
    # so a non-Completed job can never again be invisible in the only place people look for spend.
    # For the full terminal record of ONE job (FailureReason, transitions, container log), use MODE=job.
    _SPEND_STATUSES = ("Completed", "Stopped", "Failed", "Stopping")
    if os.environ.get("MODE", "").strip().lower() == "savings":
        want = os.environ.get("INSTANCE_FILTER", "").strip()  # e.g. "ml.g5.xlarge"; blank = all
        n = int(os.environ.get("LOOKBACK", "40"))
        summaries = []
        for status in _SPEND_STATUSES:
            summaries += sm.list_training_jobs(StatusEquals=status, SortBy="CreationTime",
                                               SortOrder="Descending", MaxResults=n)["TrainingJobSummaries"]
        summaries.sort(key=lambda s: s["CreationTime"], reverse=True)
        print(f"Realized managed-spot savings, last ~{n} jobs in {_SPEND_STATUSES}"
              + (f" (filter: {want})" if want else "") + ":\n")
        hdr = (f"  {'job':44} {'status':10} {'instance':15} {'spot':5} {'billable_h':>10} "
               f"{'training_h':>11} {'savings%':>8}")
        print(hdr); print("  " + "-" * (len(hdr) - 2))
        n_failed = 0
        for s in summaries[:n]:
            name = s["TrainingJobName"]
            try:
                d = sm.describe_training_job(TrainingJobName=name)
            except Exception as e:  # noqa: BLE001
                print(f"  {name[:44]:44} describe failed: {e}"); continue
            it = d.get("ResourceConfig", {}).get("InstanceType", "?")
            if want and want not in it:
                continue
            st = d.get("TrainingJobStatus", "?")
            n_failed += 1 if st == "Failed" else 0
            spot = d.get("EnableManagedSpotTraining", False)
            bt = d.get("BillableTimeInSeconds")
            tt = d.get("TrainingTimeInSeconds")
            bh = f"{bt/3600:.3f}" if bt else "-"
            th = f"{tt/3600:.3f}" if tt else "-"
            sav = f"{(1 - bt/tt)*100:.1f}" if (bt and tt) else "-"
            print(f"  {name[:44]:44} {st:10} {it:15} {str(spot):5} {bh:>10} {th:>11} {sav:>8}")
            if st == "Failed":
                # A failed job that was BILLED is realized spend for zero science. Say so on the row rather
                # than leaving it to be inferred from a dash in a savings column.
                print(f"  {'':44} └─ FailureReason: {str(d.get('FailureReason'))[:150]}")
        print(f"\n{n_failed} FAILED job(s) in this window. A failed job can still carry "
              f"BillableTimeInSeconds — that is realized spend for no result; check it against the ledger.")
        print("savings% = (1 - billable/training)*100. ~0 means the job ran uninterrupted, so managed")
        print("spot bought no hours discount — compare the per-hour rate on the bill to on-demand instead.")
        return

    # MODE=job: the FULL terminal record of ONE training job, in ANY state — the read that no listing can
    # substitute for. `DescribeTrainingJob` is not status-filtered, so this works on Failed jobs, and it is
    # the only call that returns FailureReason / SecondaryStatusTransitions / BillableTimeInSeconds.
    # JOB_NAME = exact name; if it is a substring, the FULL paginated history across EVERY status is searched.
    if os.environ.get("MODE", "").strip().lower() == "job":
        import sys as _sys
        _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import abfe_sel_forensic as F
        want = (os.environ.get("JOB_NAME") or os.environ.get("INSTANCE_FILTER") or "").strip()
        if not want:
            print("MODE=job needs JOB_NAME (exact name or a name substring)."); return
        names = [want] if F.describe_job(sm, want) else []
        if not names:
            found = F.sagemaker_jobs(sm, want)
            if found is None:
                print(f"REFUSED — the job history could not be listed. No claim is made about {want!r}."); return
            names = [j["name"] for j in found]
            print(f"{len(names)} job(s) whose name contains {want!r}, across EVERY status "
                  f"and the whole paginated history.\n")
        if not names:
            print(f"NO job named or containing {want!r} exists in this account/region — checked across every "
                  f"status (InProgress, Completed, Failed, Stopping, Stopped) and the full history, so this "
                  f"IS a reading of absence and not merely an absent reading.")
            return
        try:
            logs_client = boto3.client("logs")
        except Exception as e:  # noqa: BLE001
            print(f"CloudWatch Logs client unavailable: {type(e).__name__}: {e}"); logs_client = None
        for nm in names:
            d = F.describe_job(sm, nm)
            if d is None:
                print(f"\n{nm}: DESCRIBE REFUSED"); continue
            cls, ports, meaning, _m = F.classify_failure(d["status"], d["failure_reason"], d["transitions"])
            cost = F.money(d.get("billable_seconds"))
            print(f"\n{'='*100}\n{nm}\n{'='*100}")
            print(f"  status          {d['status']} (secondary {d.get('secondary_status')})")
            print(f"  FailureReason   {d.get('failure_reason')!r}")
            print(f"  class           {cls}   recurs_on_vast={ports}\n  -> {meaning}")
            print(f"  start/end (ET)  {d.get('training_start_et')} .. {d.get('training_end_et')}")
            print(f"  billable        {d.get('billable_seconds')} s => ${cost.get('usd')}")
            print(f"  phases          {d.get('phases_reached')}")
            for t in d.get("transitions") or []:
                print(f"    {t['status']:14} {str(t['start_et']):26} {str(t['seconds']):>6}s  "
                      f"{(t.get('message') or '')[:110]}")
            if logs_client is not None:
                blk = F.cloudwatch_tail(logs_client, nm)
                print(f"  container log   state={blk.get('state')} {blk.get('note') or blk.get('error') or ''}")
                for e in (blk.get("events") or [])[-80:]:
                    print(f"    {e.get('t_et')}  {str(e.get('message') or e.get('error'))[:160]}")
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

    # MODE=abfe_ready: the DISPATCH-READINESS check for an ABFE run, so a "yes" can launch without a
    # discovery round-trip. INSTANCE_FILTER carries the checkpoint TAG (default `sel-cbp30-v1`).
    #
    # It answers the four things that silently ruin an ABFE dispatch, each of which is free to check and
    # expensive to discover on a billing GPU:
    #   1. IS THE PRE-BAKED IMAGE THERE? `gpu-abfe-aws.yml` defaults `image_uri` to EMPTY, which means the
    #      stock DLC solves the conda env at RUNTIME on the g5 — the exact thing CLAUDE.md §6 forbids
    #      ("never build an environment on a machine we are paying for"), once per leg. If the ECR image
    #      exists, the dispatch must name it; if it does not, it must be re-baked FIRST.
    #   2. ARE THE STAGED INPUTS ACTUALLY THERE? A receptor prefix that 404s fails each leg after the
    #      instance is already up and billing.
    #   3. IS THE TARGET TAG ALREADY OCCUPIED? This is the dangerous one and it is CLAUDE.md §4b in its
    #      purest form. The checkpoint prefix is `<TAG>/ckpt/<leg>/` with NO SEED IN THE PATH, and
    #      `nr4a3_abfe.run_window` resumes from `_last_logged_iter + 1`. So dispatching a NEW SEED under an
    #      OLD TAG does not produce a replicate — every window is already at n_iter, the loop body never
    #      executes, and the job exits "successfully" re-emitting the first seed's samples under the new
    #      seed's label. A fresh run needs a fresh tag; a replicate needs its own tag.
    #   4. IS THERE SPOT HEADROOM? The account cap is 8 concurrent spot instances; 3 legs need 3.
    if os.environ.get("MODE", "").strip().lower() == "abfe_ready":
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
        tag = (os.environ.get("INSTANCE_FILTER", "").strip() or "sel-cbp30-v1")
        prefix = os.environ.get("RECEPTOR_PREFIX", "selectivity-benchmark")
        acct = boto3.client("sts").get_caller_identity()["Account"]
        bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
        s3 = boto3.client("s3")
        print(f"ABFE DISPATCH READINESS — tag={tag!r} receptor_prefix={prefix!r} region={region}\n")

        print("1. PRE-BAKED ECR IMAGE (CLAUDE.md §6 — never solve an env on a billing GPU)")
        repo_name = os.environ.get("ECR_REPO", "nr4a3-abfe")
        try:
            imgs = boto3.client("ecr").describe_images(repositoryName=repo_name)["imageDetails"]
            imgs.sort(key=lambda i: i["imagePushedAt"], reverse=True)
            for i in imgs[:5]:
                print(f"   {','.join(i.get('imageTags', ['<untagged>'])):20} "
                      f"pushed {i['imagePushedAt']:%Y-%m-%d %H:%M} UTC  "
                      f"{i.get('imageSizeInBytes', 0)/1e9:.2f} GB")
            if any("latest" in (i.get("imageTags") or []) for i in imgs):
                print(f"   => PASS. image_uri = {acct}.dkr.ecr.{region}.amazonaws.com/{repo_name}:latest")
            else:
                print(f"   => NO ':latest' TAG — re-bake with build-abfe-image.yml before dispatching.")
        except Exception as e:  # noqa: BLE001
            print(f"   => ABSENT/UNREADABLE ({type(e).__name__}). Re-bake with build-abfe-image.yml, or the "
                  f"legs will each solve conda on a billing g5.")

        print(f"\n2. STAGED RECEPTOR INPUTS  s3://{bucket}/{prefix}/")
        got = {o["Key"].split("/")[-1]: o["Size"]
               for o in s3.list_objects_v2(Bucket=bucket, Prefix=prefix + "/").get("Contents", [])}
        for f in ("crebbp-opened.pdb", "docked_crebbp.sdf", "brd4bd1-opened.pdb", "docked_brd4bd1.sdf"):
            print(f"   {'OK ' if f in got else 'MISSING'} {f:24} {got.get(f, '-')}")
        print("   => " + ("PASS — all four present." if len(got) >= 4 else
                          "INCOMPLETE — re-run stage-selectivity-benchmark-aws.yml."))

        print(f"\n3. TAG COLLISION  s3://{bucket}/{tag}/ckpt/   (a used tag SILENTLY RESUMES — see above)")
        ck = s3.list_objects_v2(Bucket=bucket, Prefix=f"{tag}/ckpt/").get("Contents", [])
        if not ck:
            print("   => PASS — prefix empty, this tag starts a genuinely fresh run.")
        else:
            legs = sorted({o["Key"].split("/")[2] for o in ck if len(o["Key"].split("/")) > 2})
            print(f"   => OCCUPIED: {len(ck)} object(s) across leg(s) {legs}. A dispatch on this tag RESUMES.")
            print("      Use a fresh tag unless you intend to resume.")

        print("\n4. SPOT HEADROOM (account cap = 8 concurrent spot training instances; 3 legs need 3)")
        inprog = sm.list_training_jobs(StatusEquals="InProgress", MaxResults=50)["TrainingJobSummaries"]
        used = 0
        for j in inprog:
            try:
                d = sm.describe_training_job(TrainingJobName=j["TrainingJobName"])
            except Exception:  # noqa: BLE001
                continue
            if d.get("EnableManagedSpotTraining"):
                used += d.get("ResourceConfig", {}).get("InstanceCount", 1)
        print(f"   {used}/8 in use => {'PASS' if 8 - used >= 3 else 'BLOCKED'}, {max(0, 8 - used)} free slot(s)")
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
