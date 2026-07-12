#!/usr/bin/env python3
"""Fan-out submitter for the ternary-COOPERATIVITY pilot (Track B; prereg budget.ternary_pilot, $200 cap).

Launches the frozen pilot's alchemical morph legs — the 4 frozen environment legs (ternary_coop.PILOT_LEG_MAP:
calib binary/ternary + NR-V04 active→epimer binary/ternary-NR4A1) + the 2 derived shared-solvent references —
each as ≥3 independent replicas (SEED=0..N-1), as managed-spot Training jobs, per-window checkpointed to S3
(spot-safe). Mirrors nr4a3_rbfe_sagemaker.py's spot + checkpoint + sharding + diagnostics plumbing; the only
differences are the ternary system assembly and the ≥3-replica fan-out (prereg uncertainty_estimator).

MODE (env MODE):
  plan   : dry-run — the tcoop.plan() $200-cap forecast + the leg×replica launch list. No spend, no GPU.
  smoke  : ONE tiny spot job — validates the openfe env solve + ternary assembly + mapping + hybrid-topology
           build (NO MD). Mounts the staged inputs (needs data/<leg>/complex.pdb + ligands.sdf).
  run    : launch the pilot legs × replicas as spot jobs. GATED (ternary pilot is authorized under the $200
           cap; still: pilot-one-leg-first — ONLY_LEGS to a single leg, wait out spot capacity).
  reduce : CPU job → ternary_fep_reduce (binary-vs-ternary cycle, replicate-SD errors, NR-V04 margins).
  jobs | tracelog | stop : the same liveness / failure-trace / kill diagnostics as the RBFE submitter.

VALIDATE-FIRST + PILOT-ONE-LEG-FIRST (CLAUDE.md): smoke → ONLY_LEGS=<one binary leg>, one replica → the pair
that gives NR-V04's affinity knockout → the full bundle. Abort the fleet if the co-fold can't seat the complex
or the first leg can't converge.
"""
import os
import sys

import ternary_coop as tcoop
import nr4a3_ternary_fep as eng

TAG = os.environ.get("TERNARY_TAG", "nr4a3-ternary-coop-pilot")
MODE = os.environ.get("MODE", "plan")
INSTANCE = os.environ.get("INSTANCE", "ml.g5.xlarge")
MAX_RUN_H = float(os.environ.get("MAX_RUN_HOURS", "36"))     # ternary systems are larger than binary RBFE morphs
MAX_WAIT_H = float(os.environ.get("MAX_WAIT_HOURS", "48"))   # run + generous spot capacity wait
GIT_REF = os.environ.get("GIT_REF", "main")
SPOT = os.environ.get("SPOT", "1") == "1"
N_ITER = os.environ.get("N_ITER", "1000")
N_WINDOWS = int(os.environ.get("N_WINDOWS", "16"))
N_REPLICAS = int(os.environ.get("N_REPLICAS", "3"))          # prereg min_replicas_per_leg = 3 (replicate-SD)
DIRECTIONS = [d.strip() for d in os.environ.get("DIRECTIONS", "fwd").split(",") if d.strip()]
TERNARY_PREFIX = os.environ.get("TERNARY_PREFIX", "nr4a3-ternary-coop-inputs")
SPOT_HOURLY = float(os.environ.get("SPOT_HOURLY", "0.50"))
IMAGE_URI = os.environ.get("TERNARY_IMAGE_URI", "").strip()
UNIT_GPU_H = float(os.environ.get("UNIT_GPU_H", "3.0"))      # PLANNING STUB (ternary > binary-RBFE); calibrate leg 1


def _legs():
    """Every (leg_id, direction, seed) unit the pilot launches."""
    units = []
    for leg_id in eng.expand_pilot_legs():
        for d in DIRECTIONS:
            for s in range(N_REPLICAS):
                units.append((leg_id, d, s))
    return units


def _cost_note():
    n_legs = len(eng.expand_pilot_legs())
    total_windows = n_legs * len(DIRECTIONS) * N_REPLICAS * N_WINDOWS
    gpu_h = total_windows * UNIT_GPU_H
    return ("%d legs × %d dir × %d replicas × %d windows = %d alchemical windows ≈ %.0f GPU-h; legs parallel on "
            "spot (8-wide) → wall ~%.0f h; spot ≈ $%.0f. UNIT_GPU_H=%g is a PLANNING STUB — calibrate on leg 1."
            % (n_legs, len(DIRECTIONS), N_REPLICAS, N_WINDOWS, total_windows, gpu_h,
               N_WINDOWS * N_REPLICAS * UNIT_GPU_H, gpu_h * SPOT_HOURLY, UNIT_GPU_H))


def _job_suffix(leg_id, direction, seed):
    # SageMaker job names: keep short + DNS-safe. leg ids have '__' → collapse to '-'.
    short = leg_id.replace("_", "-").replace("--", "-")[:40]
    return "%s-%s-r%d" % (short, direction, seed)


def main():
    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if MODE not in ("plan", "jobs", "tracelog", "stop") and not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set")

    if MODE == "jobs":
        import boto3
        from collections import defaultdict
        sm = boto3.client("sagemaker")
        try:
            resp = sm.list_training_jobs(MaxResults=100, SortBy="CreationTime", SortOrder="Descending")
            jobs = [(j["TrainingJobName"], j["TrainingJobStatus"]) for j in resp.get("TrainingJobSummaries", [])
                    if TAG in j["TrainingJobName"]]
        except Exception as e:  # noqa: BLE001
            print("[tfep] job-list error: %s" % e); jobs = []
        print("[tfep] JOBS for tag=%s:" % TAG)
        for name, status in jobs[:24]:
            reason = ""
            if status in ("Failed", "InProgress"):
                try:
                    d = sm.describe_training_job(TrainingJobName=name)
                    if status == "Failed":
                        reason = (d.get("FailureReason", "") or "").replace("\n", " ")[-160:]
                    else:
                        tr = d.get("SecondaryStatusTransitions", [])
                        msg = (tr[-1].get("StatusMessage", "") if tr else "").replace("\n", " ")[:120]
                        reason = "[%s] %s" % (d.get("SecondaryStatus", ""), msg)
                except Exception:  # noqa: BLE001
                    pass
            print("  %-58s %-12s %s" % (name, status, reason))
        try:
            import sagemaker
            s3 = boto3.client("s3")
            bucket = sagemaker.Session().default_bucket()
            cnt, last = defaultdict(int), {}
            for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix="%s/ckpt/" % TAG):
                for o in page.get("Contents", []):
                    leg = o["Key"].split("%s/ckpt/" % TAG, 1)[1].split("/", 1)[0]
                    cnt[leg] += 1
                    if leg not in last or o["LastModified"] > last[leg]:
                        last[leg] = o["LastModified"]
            print("[tfep] CKPT census (liveness = recent last-write):")
            for leg in sorted(cnt):
                print("  %-44s %4d objs   last-write %s" % (leg, cnt[leg], last[leg].strftime("%m-%d %H:%M:%SZ")))
            if not cnt:
                print("  (no checkpoint objects yet)")
        except Exception as e:  # noqa: BLE001
            print("[tfep] ckpt-census error: %s" % e)
        return

    if MODE == "tracelog":
        import boto3
        sm = boto3.client("sagemaker")
        logs = boto3.client("logs")
        jobname = os.environ.get("TERNARY_JOB", "").strip()
        if not jobname:
            r = sm.list_training_jobs(NameContains=TAG, MaxResults=12, SortBy="CreationTime",
                                      SortOrder="Descending")
            jobname = next((j["TrainingJobName"] for j in r.get("TrainingJobSummaries", [])
                            if j["TrainingJobStatus"] == "Failed"), "")
        print("[tfep] TRACELOG for %s" % (jobname or "(none found)"))
        if jobname:
            grp = "/aws/sagemaker/TrainingJobs"
            for st in logs.describe_log_streams(logGroupName=grp, logStreamNamePrefix=jobname,
                                                orderBy="LogStreamName").get("logStreams", []):
                ev = logs.get_log_events(logGroupName=grp, logStreamName=st["logStreamName"], limit=250,
                                         startFromHead=False)
                for e in ev.get("events", [])[-150:]:
                    print(e["message"].rstrip())
        return

    if MODE == "stop":
        import boto3
        sm = boto3.client("sagemaker")
        only = {x.strip() for x in os.environ.get("ONLY_LEGS", "").split(",") if x.strip()} or None
        resp = sm.list_training_jobs(MaxResults=100, SortBy="CreationTime", SortOrder="Descending")
        killed = 0
        for j in resp.get("TrainingJobSummaries", []):
            name, status = j["TrainingJobName"], j["TrainingJobStatus"]
            if TAG not in name or status != "InProgress":
                continue
            if only and not any(o.replace("_", "-") in name for o in only):
                continue
            try:
                sm.stop_training_job(TrainingJobName=name); killed += 1
                print("[tfep] STOP requested: %s" % name)
            except Exception as e:  # noqa: BLE001
                print("[tfep] stop failed for %s: %s" % (name, e))
        print("[tfep] %d InProgress job(s) sent Stop." % killed)
        return

    print("[tfep] TAG=%s mode=%s windows=%d replicas=%d dirs=%s spot=%s" %
          (TAG, MODE, N_WINDOWS, N_REPLICAS, DIRECTIONS, SPOT))
    print("[tfep] legs: %s" % eng.expand_pilot_legs())
    print("[tfep] COST %s" % _cost_note())

    if MODE == "plan":
        import json
        forecast = tcoop.plan(n_windows=N_WINDOWS, n_replicas=N_REPLICAS, unit_gpu_h=UNIT_GPU_H,
                              spot_hourly=SPOT_HOURLY)
        print("[tfep] $200-CAP FORECAST (frozen 4-leg bundle):", json.dumps(forecast, indent=1))
        if not forecast["fits_cap"]:
            print("[tfep] STOP — the frozen bundle exceeds the $%g cap. Return a revised costed scope; do NOT "
                  "drop replicas/convergence to fit." % forecast["hard_cap_usd"])
        units = _legs()
        for leg_id, d, s in units:
            print("  WOULD launch %s-%s: leg=%s dir=%s seed=%d, %d windows → ckpt s3://<bucket>/%s/ckpt/%s/"
                  % (TAG, _job_suffix(leg_id, d, s), leg_id, d, s, N_WINDOWS, TAG, _job_suffix(leg_id, d, s)))
        print("[tfep] plan only (%d launch units). smoke → ONLY_LEGS=<one binary leg> N_REPLICAS=1 → full bundle."
              % len(units))
        return

    import sagemaker
    from sagemaker.pytorch import PyTorch
    from sagemaker.inputs import TrainingInput
    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))
    inputs_uri = "s3://%s/%s/" % (bucket, TERNARY_PREFIX)

    def make_estimator(name, hp):
        kw = dict(entry_point="entry_ternary_fep.py", source_dir=os.path.join(here, "sagemaker_src"),
                  role=role, instance_count=1, instance_type=INSTANCE, sagemaker_session=sess,
                  base_job_name="%s-%s" % (TAG, name), use_spot_instances=SPOT,
                  max_run=int(MAX_RUN_H * 3600), max_wait=int(MAX_WAIT_H * 3600) if SPOT else None,
                  checkpoint_s3_uri="s3://%s/%s/ckpt/%s/" % (bucket, TAG, name),
                  checkpoint_local_path="/opt/ml/checkpoints", hyperparameters=hp)
        if IMAGE_URI:
            kw["image_uri"] = IMAGE_URI
        else:
            kw["framework_version"] = "2.3"; kw["py_version"] = "py311"
        return PyTorch(**kw)

    common = {"git-ref": GIT_REF, "n-iter": N_ITER, "n-windows": N_WINDOWS, "prebaked": "1" if IMAGE_URI else "0"}

    if MODE == "smoke":
        leg_id = (os.environ.get("ONLY_LEGS", "").split(",")[0].strip()
                  or "nrv04_active_to_epimer__binary_vhl")
        est = make_estimator("smoke", {**common, "leg-id": leg_id, "direction": "fwd", "seed": "0",
                                       "mode": "smoke"})
        print("[tfep] launching SMOKE (openfe env + %s assembly + mapping + hybrid topology, no MD)…" % leg_id)
        est.fit({"data": TrainingInput(inputs_uri)}, wait=True, logs=True)
        print("[tfep] SMOKE complete — env solves; ternary assembly + mapping + spot + checkpoint path work.")
        return

    if MODE == "reduce":
        est = make_estimator("reduce", {**common, "mode": "reduce", "leg-id": "reduce", "direction": "fwd",
                                        "seed": "0"})
        est.fit({"data": TrainingInput("s3://%s/%s/ckpt/" % (bucket, TAG))}, wait=False)
        print("[tfep] launched reduce: %s → binary-vs-ternary cycle + NR-V04 margins." %
              est.latest_training_job.name)
        return

    # MODE == run
    only = {x.strip() for x in os.environ.get("ONLY_LEGS", "").split(",") if x.strip()} or None
    launched = []
    for leg_id, d, s in _legs():
        if only and not any(o in leg_id for o in only):
            continue
        name = _job_suffix(leg_id, d, s)
        est = make_estimator(name, {**common, "leg-id": leg_id, "direction": d, "seed": str(s), "mode": "run"})
        try:
            est.fit({"data": TrainingInput(inputs_uri)}, wait=False)
        except Exception as e:  # noqa: BLE001
            if "ResourceLimitExceeded" in str(e) or "quota" in str(e).lower():
                print("[tfep] spot quota reached after %d jobs. Re-dispatch mode=run — resume picks up the rest."
                      % len(launched)); break
            raise
        launched.append(est.latest_training_job.name)
        print("[tfep] launched %s (%s/%s/r%d): %s" % (name, leg_id, d, s, launched[-1]))
    print("[tfep] %d spot morph-leg jobs launched. When complete: MODE=reduce. Jobs: %s" % (len(launched),
          launched))


if __name__ == "__main__":
    main()
