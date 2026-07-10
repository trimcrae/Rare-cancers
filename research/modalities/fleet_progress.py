#!/usr/bin/env python3
"""Fleet progress + HANG detector for the in-flight SageMaker spot Training jobs (read-only).

Why this exists: a SageMaker Training job that is STUCK on a single λ-window (or a wedged MD step) still
reports TrainingJobStatus=InProgress / SecondaryStatus=Training — so comparing *status* hour-over-hour
CANNOT catch a hang (it reads "Training" the whole time). What DOES catch it: the job stops emitting
CloudWatch log events, so the AGE of its last log event grows without bound. This tool reads each job's
last-event timestamp straight from CloudWatch (describe_log_streams → lastEventTimestamp, one cheap call,
no event scan), reports it alongside status + runtime + the last progress marker (the ABFE per-iteration
'[abfe] window k iter i' line, or an MD ns/step line), and FLAGS any job that is 'Training' but has gone
quiet for more than STALE_MIN minutes. That flag is the stuck-at-the-same-iteration signal.

Read-only; starts no instance; commits nothing. Env: JOB_PREFIX (NameContains filter; '' = all in-progress
Training jobs), STALE_MIN (default 25), MARKER_RE (progress-line regex), AWS creds + AWS_DEFAULT_REGION.
Driven from fleet-progress-aws.yml.
"""
import datetime
import os
import re

TRAIN_GROUP = "/aws/sagemaker/TrainingJobs"
UTC = datetime.timezone.utc
DEFAULT_MARKER_RE = r"\[abfe\]|window\s*\d+|iter(ation)?\b|\bns\b|step\s*=|%\)|lambda|mbar"


def classify(secondary, last_event_ms, now_ms, stale_min, has_stream):
    """PURE decision: is a job stalled? Returns (state, age_min|None). Unit-tested.
      - secondary 'Starting'/'Downloading'/'Stopping' with no stream yet -> 'provisioning' (benign).
      - 'Training' but last event older than stale_min -> 'STALE' (possible hang).
      - 'Training' with a fresh event -> 'alive'.
      - anything else -> 'other'."""
    if not has_stream or last_event_ms is None:
        return ("provisioning" if secondary in ("Starting", "Downloading", "Stopping", "Pending") else "no_stream"), None
    age_min = (now_ms - last_event_ms) / 60000.0
    if secondary == "Training":
        return ("STALE" if age_min > stale_min else "alive"), age_min
    return "other", age_min


def _stream(logs, name):
    """Newest log stream for a training job. NOTE: CloudWatch forbids orderBy=LastEventTime together with
    logStreamNamePrefix, so we filter by prefix and pick the max lastEventTimestamp ourselves (a training
    job normally has a single algo-1-* stream). A real API error is PRINTED, not swallowed into 'no stream'
    — silently treating an error as 'no events' would make the hang detector falsely report 'no stalls'."""
    try:
        streams = logs.describe_log_streams(logGroupName=TRAIN_GROUP, logStreamNamePrefix=name,
                                             limit=50).get("logStreams", [])
    except logs.exceptions.ResourceNotFoundException:
        return None                                    # stream genuinely not created yet (provisioning)
    except Exception as e:  # noqa: BLE001
        print(f"   (describe_log_streams error for {name[:40]}: {e})", flush=True)
        return None
    streams = [s for s in streams if s.get("lastEventTimestamp")]
    return max(streams, key=lambda s: s["lastEventTimestamp"]) if streams else None


def _checkpoint_latest(s3, s3_uri, cap_pages=20):
    """Freshest object under a training job's checkpoint S3 prefix -> (last_ms, key, n_objects).
    This is the CORRECT per-iteration heartbeat: a healthy ABFE λ-window prints only ONE stdout line per
    window (the nan-guard header) and then appends to window_NN.jsonl every iteration — SageMaker syncs that
    file to S3 continuously, so the prefix's newest LastModified advances each iteration even while stdout is
    silent. (CloudWatch stdout staleness would false-positive on every healthy window.) Returns (None,...) if
    there is no checkpoint prefix or it is empty."""
    if not s3_uri or not s3_uri.startswith("s3://"):
        return None, None, 0
    bkt, _, pref = s3_uri[5:].partition("/")
    latest_ms, latest_key, n = None, None, 0
    try:
        pages = s3.get_paginator("list_objects_v2").paginate(Bucket=bkt, Prefix=pref)
        for i, page in enumerate(pages):
            for o in page.get("Contents", []):
                n += 1
                lm = o["LastModified"].timestamp() * 1000.0
                if latest_ms is None or lm > latest_ms:
                    latest_ms, latest_key = lm, o["Key"]
            if i + 1 >= cap_pages:
                break
    except Exception as e:  # noqa: BLE001 — surface, don't swallow into a false 'no heartbeat'
        print(f"   (s3 list error for {pref[:60]}: {e})", flush=True)
        return None, None, 0
    return latest_ms, latest_key, n


def _marker(logs, stream_name, marker_re):
    try:
        evs = logs.get_log_events(logGroupName=TRAIN_GROUP, logStreamName=stream_name,
                                  startFromHead=False, limit=30).get("events", [])
    except Exception:  # noqa: BLE001
        return ""
    rx = re.compile(marker_re, re.I)
    for e in reversed(evs):
        if rx.search(e["message"]):
            return e["message"].strip()[:110]
    return (evs[-1]["message"].strip()[:110] if evs else "")


def main():
    prefix = os.environ.get("JOB_PREFIX", "").strip()
    stale_min = float(os.environ.get("STALE_MIN", "25"))
    marker_re = os.environ.get("MARKER_RE", DEFAULT_MARKER_RE)
    import boto3
    sm = boto3.client("sagemaker")
    logs = boto3.client("logs")
    s3 = boto3.client("s3")
    now = datetime.datetime.now(UTC)
    now_ms = now.timestamp() * 1000.0

    kw = dict(StatusEquals="InProgress", SortBy="CreationTime", SortOrder="Descending", MaxResults=40)
    if prefix:
        kw["NameContains"] = prefix
    jobs = sm.list_training_jobs(**kw)["TrainingJobSummaries"]

    print(f"=== fleet progress @ {now:%Y-%m-%d %H:%M}Z  (STALE_MIN={stale_min:.0f}m, {len(jobs)} in-progress) ===")
    print("heartbeat = freshest S3 checkpoint object (per-iteration; healthy ABFE windows are stdout-silent)")
    print(f"{'JOB':<50} {'SECONDARY':<11} {'RUN':>5} {'CKPT_AGE':>9} {'SRC':>4}  STATE | last-marker")
    stalls = []
    for j in jobs:
        name = j["TrainingJobName"]
        d = sm.describe_training_job(TrainingJobName=name)
        sec = d.get("SecondaryStatus", "")
        start = d.get("TrainingStartTime")
        runmin = (now - start.replace(tzinfo=UTC)).total_seconds() / 60 if start else 0
        # PRIMARY heartbeat: freshest S3 checkpoint object (advances every iteration via continuous sync).
        ck_uri = (d.get("CheckpointConfig") or {}).get("S3Uri", "")
        ck_ms, ck_key, ck_n = _checkpoint_latest(s3, ck_uri)
        # CloudWatch stream only for the descriptive marker (what window/iter), NOT for the stall decision.
        stm = _stream(logs, name)
        marker = _marker(logs, stm["logStreamName"], marker_re) if stm else ""
        if ck_ms is not None:
            state, age = classify(sec, ck_ms, now_ms, stale_min, has_stream=True)
            src = "s3"
        else:                                          # no checkpoint prefix yet: fall back to CloudWatch age
            last_ms = stm.get("lastEventTimestamp") if stm else None
            state, age = classify(sec, last_ms, now_ms, stale_min, has_stream=bool(stm))
            src = "cw"
        age_str = f"{max(0.0, age):.0f}m" if age is not None else "—"   # clamp tiny clock-skew negatives
        tag = state
        if state == "STALE":
            tag = f"⚠STALE {age:.0f}m HANG?"
            stalls.append((name, age, marker, src))
        print(f"{name[:50]:<50} {sec:<11} {runmin:5.0f} {age_str:>9} {src:>4}  {tag} | {marker[:60]}")
    print("=" * 108)
    # Free spot-Training slots: the account quota (8) minus the in-progress Training jobs. A positive number
    # means capacity is free RIGHT NOW — the hourly check can launch a queued, slot-fillable job (gpu-queue.json).
    quota = int(os.environ.get("SPOT_TRAIN_QUOTA", "8"))
    free = quota - len(jobs)
    print(f"spot Training slots: {len(jobs)}/{quota} in use  →  FREE SLOTS: {max(0, free)}")
    if stalls:
        print(f"⚠ {len(stalls)} job(s) look STUCK (no fresh checkpoint > {stale_min:.0f}m — investigate):")
        for name, age, marker, src in stalls:
            print(f"   {name}  no-{src}-heartbeat {age:.0f}m  last-marker: {marker[:70]}")
    else:
        print(f"✓ no stalls: every Training job wrote a checkpoint within {stale_min:.0f}m (or is provisioning/spot-waiting).")


if __name__ == "__main__":
    main()
