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
    try:
        s = logs.describe_log_streams(logGroupName=TRAIN_GROUP, logStreamNamePrefix=name,
                                      orderBy="LastEventTime", descending=True,
                                      limit=1).get("logStreams", [])
    except logs.exceptions.ResourceNotFoundException:
        return None
    except Exception:  # noqa: BLE001
        return None
    return s[0] if s else None


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
    now = datetime.datetime.now(UTC)
    now_ms = now.timestamp() * 1000.0

    kw = dict(StatusEquals="InProgress", SortBy="CreationTime", SortOrder="Descending", MaxResults=40)
    if prefix:
        kw["NameContains"] = prefix
    jobs = sm.list_training_jobs(**kw)["TrainingJobSummaries"]

    print(f"=== fleet progress @ {now:%Y-%m-%d %H:%M}Z  (STALE_MIN={stale_min:.0f}m, {len(jobs)} in-progress) ===")
    print(f"{'JOB':<50} {'SECONDARY':<11} {'RUN':>5} {'LAST_EVT':>9}  STATE / MARKER")
    stalls = []
    for j in jobs:
        name = j["TrainingJobName"]
        d = sm.describe_training_job(TrainingJobName=name)
        sec = d.get("SecondaryStatus", "")
        start = d.get("TrainingStartTime")
        runmin = (now - start.replace(tzinfo=UTC)).total_seconds() / 60 if start else 0
        st = _stream(logs, name)
        last_ms = st.get("lastEventTimestamp") if st else None
        state, age = classify(sec, last_ms, now_ms, stale_min, has_stream=bool(st))
        marker = _marker(logs, st["logStreamName"], marker_re) if st else ""
        age_str = f"{age:.0f}m" if age is not None else "—"
        tag = state
        if state == "STALE":
            tag = f"⚠STALE {age:.0f}m HANG?"
            stalls.append((name, age, marker))
        print(f"{name[:50]:<50} {sec:<11} {runmin:5.0f} {age_str:>9}  {tag} | {marker[:70]}")
    print("=" * 104)
    # Free spot-Training slots: the account quota (8) minus the in-progress Training jobs. A positive number
    # means capacity is free RIGHT NOW — the hourly check can launch a queued, slot-fillable job (gpu-queue.json).
    quota = int(os.environ.get("SPOT_TRAIN_QUOTA", "8"))
    free = quota - len(jobs)
    print(f"spot Training slots: {len(jobs)}/{quota} in use  →  FREE SLOTS: {max(0, free)}")
    if stalls:
        print(f"⚠ {len(stalls)} job(s) look STUCK (Training but silent > {stale_min:.0f}m — investigate CloudWatch):")
        for name, age, marker in stalls:
            print(f"   {name}  idle {age:.0f}m  last: {marker[:80]}")
    else:
        print(f"✓ no stalls: every Training job logged within {stale_min:.0f}m (or is still provisioning/spot-waiting).")


if __name__ == "__main__":
    main()
