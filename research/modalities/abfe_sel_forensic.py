#!/usr/bin/env python3
"""WHAT WROTE `s3://<bucket>/sel-cbp30-v1/ckpt/`? — a real diagnostic, not a story (CLAUDE.md §4).

THE UNRECONCILED PAIR THIS EXISTS TO SETTLE
-------------------------------------------
Two observations were on the table at once and they cannot both mean what they appear to:

  (a) the checkpoint prefix `sel-cbp30-v1/ckpt/` is OCCUPIED — objects exist under a leg name;
  (b) NO SageMaker training job whose name contains `sel-cbp30` has ever been seen in the account.

`selectivity-benchmark.json` -> `abfe_plan.readiness` asserts the opposite of (a): *"tag sel-cbp30-v1 unused
(a fresh run, not a resume)"*. So either the readiness check was wrong, or something other than an ABFE
training job put those bytes there. A prior agent reported "a run today at 3:16 PM ET" — an UNVERIFIED LEAD,
recorded here as a hypothesis, never as a fact.

THE COMPETING HYPOTHESES, and the one observation that discriminates each
------------------------------------------------------------------------
  H1  A real ABFE leg ran under this tag and produced sampling.
      DISCRIMINATOR: the contents. Only a real `run_window` loop writes `window_XX.jsonl` lines carrying
      monotonically increasing `iter` and a 12- (or 16-) entry `u` vector. That is a thing no default,
      no staging job and no manual copy can fabricate — CLAUDE.md §4b's test exactly ("check the thing only
      a real run can produce").
  H2  A leg STARTED, built + cached its reference system, and died before sampling.
      DISCRIMINATOR: `reference_system.xml` / `reference_positions.json` / `reference_aux.json` present with
      NO `window_*.jsonl` — `_prepare_or_load_reference` writes those three BEFORE the first window runs.
  H3  Something other than the ABFE engine wrote here (a staging job, a manual `aws s3 cp`, a different tag
      family colliding).
      DISCRIMINATOR: object names that belong to no ABFE artifact, or a `meta.json` naming a different leg /
      ligand / receptor than this benchmark.
  H4  The objects are older than the benchmark and the prefix was reused.
      DISCRIMINATOR: LastModified against the benchmark's own staging date.

WHAT THIS PRINTS, and why each field is there
---------------------------------------------
  * every key under the tag, with SIZE, LastModified in **US Eastern 12-hour** (CLAUDE.md §1), ETag and
    StorageClass — the raw evidence, unsummarised, so the reader can check the conclusion;
  * the DECODED contents of every small text artifact (`meta.json`, the first/last line of each
    `window_*.jsonl`, recovery logs) — provenance, not just presence;
  * the full SageMaker job history filtered by name, across EVERY status and the whole paginated history,
    not the last page. "I looked at the last 40 jobs" is how (b) was established, and it is not the same
    statement as "no such job has ever existed";
  * a VERDICT naming which hypothesis the evidence supports, or `UNDETERMINED` with the reason. An
    unreadable prefix is recorded as a REFUSAL, never as an absence (CLAUDE.md §4: an absent reading is not
    a reading of absence).

$0. Read-only: `ListObjectsV2`, `GetObject`, `ListTrainingJobs`, `DescribeTrainingJob`. Starts nothing.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_HERE = os.path.dirname(os.path.abspath(__file__))

DEFAULT_BUCKET = os.environ.get("VAST_CKPT_BUCKET") or "sagemaker-us-east-2-646605541856"
DEFAULT_TAG = os.environ.get("ABFE_TAG") or "sel-cbp30-v1"
OUT_PATH = os.path.join(_HERE, "abfe-sel-ckpt-forensic.json")

# Artifacts the ABFE engine writes, and WHICH function writes each. The map is the diagnostic: a key that
# matches nothing here was not written by this engine, and a key that matches tells us how far the leg got.
_ENGINE_ARTIFACTS = {
    "reference_system.xml": "nr4a3_abfe._prepare_or_load_reference — written BEFORE the first window runs",
    "reference_positions.json": "nr4a3_abfe._prepare_or_load_reference — written BEFORE the first window runs",
    "reference_aux.json": "nr4a3_abfe._prepare_or_load_reference — written BEFORE the first window runs",
    "meta.json": "nr4a3_abfe.run_shard — written after the reference is built, before window 0",
    "hydration_validation.json": "nr4a3_abfe.run_hydration_validation",
}
_ENGINE_PREFIXES = {
    "window_": "nr4a3_abfe.append_reduced_potentials / run_window — ONLY a real sampling loop writes these",
    "recovery_": "nr4a3_abfe._log_recovery — a NaN-recovery event during real sampling",
}

# ★ TIME IS ALWAYS US EASTERN, 12-HOUR (CLAUDE.md §1). EDT = UTC-4 on 2026-08-02. Done with a fixed offset
# rather than a tz database because a CI runner is UTC and `zoneinfo`'s tzdata may be absent; the offset is
# stated in the output so a reader can check it rather than trust it.
ET_OFFSET_H = -4
ET_LABEL = "EDT (UTC-4)"


def et(dt):
    """A UTC datetime -> 'Aug 02 2026 3:16 PM ET'. Pure."""
    import datetime as _dt
    if dt is None:
        return None
    if isinstance(dt, (int, float)):
        dt = _dt.datetime.utcfromtimestamp(float(dt))
    if dt.tzinfo is not None:
        dt = dt.astimezone(_dt.timezone.utc).replace(tzinfo=None)
    local = dt + _dt.timedelta(hours=ET_OFFSET_H)
    return local.strftime("%b %d %Y %-I:%M:%S %p ET")


def classify_key(key):
    """(writer, note) for one S3 key under the tag. PURE — this is the whole H1/H2/H3 discriminator."""
    base = os.path.basename(key)
    if base in _ENGINE_ARTIFACTS:
        return "abfe-engine", _ENGINE_ARTIFACTS[base]
    for pfx, why in _ENGINE_PREFIXES.items():
        if base.startswith(pfx):
            return "abfe-engine", why
    if not base:
        return "s3-directory-marker", "a zero-byte key ending in '/' — a console-created folder, not a write"
    return "unknown", ("no ABFE engine function writes this name — evidence for H3 (something other than "
                       "the engine wrote here)")


def leg_of(key, tag):
    """The leg segment of `<tag>/ckpt/<leg>/...`, or None. PURE."""
    parts = [p for p in str(key).split("/") if p]
    if len(parts) >= 3 and parts[0] == tag and parts[1] == "ckpt":
        return parts[2]
    return None


def verdict_from(rows, jobs_found, tag):
    """(verdict, reason) from the classified rows + the job history. PURE, so it is unit-testable.

    The ordering is the argument: sampling proves the most, a cached reference proves less, an unknown
    writer proves something different, and an empty prefix proves the readiness claim was right after all.
    """
    if rows is None:
        return "UNDETERMINED", ("the prefix could not be LISTED — this is a REFUSAL, not an absence. "
                                "Nothing may be concluded about what is or is not there.")
    if not rows:
        return "EMPTY", (f"nothing under {tag}/ — the 'tag unused' readiness claim in "
                         f"selectivity-benchmark.json holds, and the 4-object report was of a different "
                         f"prefix or a stale listing")
    sampling = [r for r in rows if os.path.basename(r["key"]).startswith("window_")]
    reference = [r for r in rows if os.path.basename(r["key"]).startswith("reference_")]
    unknown = [r for r in rows if r["writer"] == "unknown"]
    if sampling:
        n_lines = sum(int(r.get("n_lines") or 0) for r in sampling)
        return "H1_REAL_SAMPLING", (
            f"{len(sampling)} window log(s) carrying {n_lines} reduced-potential line(s). Only "
            f"`run_window`'s iteration loop writes these, so a real ABFE leg sampled under this tag. "
            f"⚠ THE TAG IS THEREFORE NOT FRESH: `run_window` resumes at `_last_logged_iter + 1`, so a "
            f"re-dispatch on this tag would CONTINUE rather than start, and a re-labelled seed would "
            f"re-emit these samples under the new label (the replicate-tag defect).")
    if reference:
        return "H2_STARTED_NEVER_SAMPLED", (
            f"{len(reference)} cached-reference artifact(s) and ZERO window logs. "
            f"`_prepare_or_load_reference` writes these BEFORE window 0 runs, so something started this "
            f"leg, built + cached its solvated system, and died before a single iteration was logged. The "
            f"cached system is REUSABLE — a resume would reload it rather than rebuild — but it contains "
            f"no sampling, so no ΔG is recoverable from it and nothing here can contaminate a fresh run's "
            f"numbers.")
    if unknown and not any(r["writer"] == "abfe-engine" for r in rows):
        return "H3_FOREIGN_WRITER", (
            f"{len(unknown)} object(s) under this tag match NO artifact the ABFE engine writes "
            f"({[os.path.basename(r['key']) for r in unknown][:8]}). The prefix is occupied by something "
            f"else; the ABFE lane never ran here.")
    return "H2_OR_H3_MIXED", (
        f"{len(rows)} object(s), no window logs, and a mix of engine and non-engine names. See the rows.")


# =============================================================================================================
# the live reads
# =============================================================================================================
def list_prefix(s3, bucket, prefix, max_bytes_to_decode=64_000):
    """Every object under `prefix`, classified, with small text artifacts DECODED. None on a read refusal."""
    rows = []
    try:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for o in page.get("Contents", []):
                writer, note = classify_key(o["Key"])
                row = {"key": o["Key"], "size_bytes": int(o["Size"]),
                       "last_modified_et": et(o["LastModified"]),
                       "last_modified_utc": o["LastModified"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                       "etag": str(o.get("ETag") or "").strip('"'),
                       "storage_class": o.get("StorageClass") or "STANDARD",
                       "writer": writer, "writer_note": note}
                # ★ MULTIPART IS PROVENANCE, NOT TRIVIA. An ETag with a `-N` suffix was uploaded in N parts,
                # which is what the CLI/SDK does for a large object; a bare 32-hex ETag is a single PUT. It
                # does not name the uploader, but it separates "streamed by a job" from "copied by hand" for
                # anything big enough to have had the choice.
                row["multipart_parts"] = (int(row["etag"].split("-")[1])
                                          if "-" in row["etag"] and row["etag"].split("-")[1].isdigit()
                                          else 1)
                row["leg"] = leg_of(o["Key"], prefix.split("/")[0])
                if 0 < o["Size"] <= max_bytes_to_decode and not o["Key"].endswith(".xml"):
                    _decode_into(s3, bucket, o["Key"], row)
                rows.append(row)
    except Exception as e:  # noqa: BLE001 — a refusal is EVIDENCE OF NOTHING and must say so
        print(f"[forensic] LIST REFUSED for s3://{bucket}/{prefix}: {type(e).__name__}: {e}", flush=True)
        return None
    return rows


def _decode_into(s3, bucket, key, row):
    """Read a small artifact and attach what it PROVES. Best-effort; a failure is recorded, never guessed."""
    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    except Exception as e:  # noqa: BLE001
        row["content_error"] = f"{type(e).__name__}: {e}"
        return
    text = body.decode("utf-8", errors="replace")
    base = os.path.basename(key)
    if base.startswith("window_") and base.endswith(".jsonl"):
        lines = [ln for ln in text.splitlines() if ln.strip()]
        row["n_lines"] = len(lines)
        # THE PROVENANCE CHECK. A real sampling loop produces increasing `iter` and a `u` vector whose length
        # equals the λ-window count. A hand-made or truncated file will not.
        try:
            first, last = json.loads(lines[0]), json.loads(lines[-1])
            row["first_iter"], row["last_iter"] = first.get("iter"), last.get("iter")
            row["u_length"] = len(first.get("u") or [])
            row["window_index"] = first.get("w")
            row["looks_like_real_sampling"] = bool(
                row["u_length"] in (12, 16) and last.get("iter", -1) >= first.get("iter", 0))
        except Exception as e:  # noqa: BLE001
            row["content_error"] = f"unparseable jsonl: {type(e).__name__}: {e}"
        return
    if base.endswith(".json"):
        try:
            row["content"] = json.loads(text)
        except Exception:  # noqa: BLE001
            row["content_head"] = text[:1500]
        return
    row["content_head"] = text[:1500]


def describe_job(sm, name):
    """The FULL terminal record of one training job. None on a refusal (never an invented absence).

    ★ WHY THIS FUNCTION EXISTS, in the words of the mistake it repairs. On 2026-08-02 a leg was dispatched at
    3:16 PM ET and, forty minutes later, four independent reads said `0 in-progress training jobs`, `0/8 spot
    instances`, and "absent from the last ~40 completed/stopped jobs". That triple was read as *the job does
    not exist*. It is not: `list_sagemaker.MODE=savings` walks `StatusEquals` in ("Completed", "Stopped") ONLY,
    so a **Failed** job is invisible to every one of those reads — CLAUDE.md §4's "an absent reading is not a
    reading of absence", with the collector's own filter as the thing that could not read.
    `DescribeTrainingJob` has no such filter: it answers for a job in ANY state, and it is the only call that
    returns `FailureReason`, `SecondaryStatusTransitions` and `BillableTimeInSeconds` at all.
    """
    try:
        d = sm.describe_training_job(TrainingJobName=name)
    except Exception as e:  # noqa: BLE001
        print(f"[forensic] DESCRIBE REFUSED for {name}: {type(e).__name__}: {e}", flush=True)
        return None
    rc = d.get("ResourceConfig", {}) or {}
    out = {
        "name": d.get("TrainingJobName"),
        "arn": d.get("TrainingJobArn"),
        "status": d.get("TrainingJobStatus"),
        "secondary_status": d.get("SecondaryStatus"),
        # ⚠ THE FIELD THE WHOLE INVESTIGATION TURNS ON. Absent => AWS recorded no reason, which is itself a
        # finding (it points at the control plane rather than the container); it is NEVER filled with a guess.
        "failure_reason": d.get("FailureReason"),
        "created_et": et(d.get("CreationTime")),
        "training_start_et": et(d.get("TrainingStartTime")),
        "training_end_et": et(d.get("TrainingEndTime")),
        "last_modified_et": et(d.get("LastModifiedTime")),
        "billable_seconds": d.get("BillableTimeInSeconds"),
        "training_seconds": d.get("TrainingTimeInSeconds"),
        "instance_type": rc.get("InstanceType"),
        "instance_count": rc.get("InstanceCount"),
        "volume_size_gb": rc.get("VolumeSizeInGB"),
        "managed_spot": d.get("EnableManagedSpotTraining"),
        "max_run_s": (d.get("StoppingCondition") or {}).get("MaxRuntimeInSeconds"),
        "max_wait_s": (d.get("StoppingCondition") or {}).get("MaxWaitTimeInSeconds"),
        "training_image": (d.get("AlgorithmSpecification") or {}).get("TrainingImage"),
        "checkpoint_s3_uri": (d.get("CheckpointConfig") or {}).get("S3Uri"),
        "output_s3": (d.get("OutputDataConfig") or {}).get("S3OutputPath"),
        "role_arn": d.get("RoleArn"),
        "hyperparameters": d.get("HyperParameters") or {},
        "input_channels": [{"name": c.get("ChannelName"),
                            "s3_uri": ((c.get("DataSource") or {}).get("S3DataSource") or {}).get("S3Uri")}
                           for c in (d.get("InputDataConfig") or [])],
    }
    # The transition list is the timeline the FailureReason alone cannot give: it says which PHASE the job
    # died in, and "never left Starting" vs "died in Training" are opposite diagnoses.
    tr = []
    for t in d.get("SecondaryStatusTransitions", []) or []:
        start, end = t.get("StartTime"), t.get("EndTime")
        tr.append({"status": t.get("Status"),
                   "start_et": et(start), "end_et": et(end),
                   "seconds": (int((end - start).total_seconds()) if (start and end) else None),
                   "message": t.get("StatusMessage")})
    out["transitions"] = tr
    out["phases_reached"] = [t["status"] for t in tr]
    return out


def money(billable_seconds, usd_per_billable_h=None):
    """Realized dollars for a job's billable time. DERIVED, never typed (CLAUDE.md §1).

    The rate has ONE home — `abfe_selectivity_cost.USD_PER_BILLABLE_H_G5_XLARGE`, itself cross-checked against
    a real Ohio bill — and the semantics matter: managed spot's discount arrives as FEWER BILLED SECONDS, not a
    lower rate, so `billable_seconds` is ALREADY the discounted quantity and must be multiplied by the meter
    rate. Multiplying it by a "spot rate" applies the discount twice; that error is registered in that module's
    `SUPERSEDED_CALIBRATION_COSTS`.
    """
    if usd_per_billable_h is None:
        try:
            import abfe_selectivity_cost
            usd_per_billable_h = abfe_selectivity_cost.USD_PER_BILLABLE_H_G5_XLARGE
        except Exception as e:  # noqa: BLE001
            return {"usd": None, "rate_source": f"UNAVAILABLE: {type(e).__name__}: {e}"}
    if billable_seconds is None:
        return {"usd": None, "billable_seconds": None,
                "rate_usd_per_billable_h": usd_per_billable_h,
                "rate_source": "abfe_selectivity_cost.USD_PER_BILLABLE_H_G5_XLARGE",
                "note": "AWS returned NO BillableTimeInSeconds — the field is absent, which is not the same "
                        "as zero. Recorded as unknown."}
    return {"usd": round(billable_seconds / 3600.0 * usd_per_billable_h, 4),
            "billable_seconds": int(billable_seconds),
            "billable_hours": round(billable_seconds / 3600.0, 4),
            "rate_usd_per_billable_h": usd_per_billable_h,
            "rate_source": "abfe_selectivity_cost.USD_PER_BILLABLE_H_G5_XLARGE (cross-checked against the "
                           "2026-07 Ohio SpotTraining bill line)"}


# The failure taxonomy, and — the part that actually matters now — whether each class FOLLOWS THE WORK TO VAST.
# trimcrae has ruled Vast the flagship and SageMaker out, so this ABFE is being ported. A cause in the science
# code or the staged inputs travels with the port and must be fixed FIRST; a cause in SageMaker's own plumbing
# is sidestepped by leaving SageMaker. Each entry: (substring probes, class, recurs_on_vast, what it means).
_FAILURE_SIGNATURES = [
    (("MaxWaitTimeExceeded",), "spot_capacity_never_satisfied", False,
     "managed spot never found capacity inside max_wait. A SageMaker POOL property — Vast picks a named host "
     "instead, so this class does not port (CLAUDE.md §6: a capacity refusal on Vast means pick another host)."),
    (("InsufficientCapacity", "CapacityError", "not enough capacity"), "capacity", False,
     "the instance pool had no capacity. SageMaker-specific; Vast's board is a different market."),
    (("interrupt", "Spot instance was interrupted", "reclaim"), "spot_interruption", False,
     "routine preemption (CLAUDE.md §6 — mention lightly). Does not port as a defect; Vast preempts too but "
     "the checkpointed resume is the same answer."),
    (("CannotPullContainerError", "Failed to pull", "toomanyrequests", "manifest unknown",
      "no basic auth credentials"), "image_pull", False,
     "the ECR image could not be pulled. The IMAGE is SageMaker/ECR-side; on Vast the equivalent is a Docker "
     "Hub pull of a baked image, so the specific failure does not port — but it confirms the leg never ran."),
    (("ResourceLimitExceeded", "limit is",), "quota", False,
     "an account quota refused the instance. SageMaker-specific."),
    (("AccessDenied", "not authorized to perform", "assume role", "AmazonSageMakerFullAccess"), "iam", False,
     "the execution role lacked a permission. SageMaker-specific plumbing."),
    (("Data download failed", "failed to download", "S3DownloadFailed", "NoSuchKey", "NoSuchBucket",
      "does not exist or the object"), "s3_input_missing_or_malformed", True,
     "★ PORTS TO VAST. The job could not fetch its staged inputs. The receptor/ligand staging is the SAME "
     "artifact set the Vast lane must read, so a missing or malformed input fails there too. Fix before porting."),
    (("MaxRuntimeExceeded",), "timeout", True,
     "the job hit max_run. Whether this ports depends on the per-unit rate, which is a property of the work, "
     "not the provider — re-scope the unit before porting."),
    (("AlgorithmError", "ExecuteUserScriptError", "Traceback", "ModuleNotFoundError", "ImportError",
      "KeyError", "ValueError", "RuntimeError", "AssertionError", "exit code"), "in_container_error", True,
     "★ PORTS TO VAST. The container started and the SCIENCE CODE or its environment raised. The same "
     "`nr4a3_abfe.py` and the same inputs run on Vast, so this recurs there. Fix before porting."),
    (("InternalServerError",), "aws_internal", False,
     "AWS reported an internal error. SageMaker-specific; retry is the standard answer."),
]


def classify_failure(status, failure_reason, transitions=None):
    """(class, recurs_on_vast, meaning, matched_on) from the terminal record. PURE, so it is unit-testable.

    An unmatched reason is `unclassified` with `recurs_on_vast=None` — an HONEST UNKNOWN. It is never bucketed
    into the nearest-looking class, because the whole point of the field is to decide what the Vast port must
    fix, and a wrong bucket there is worse than no bucket.
    """
    if status is None:
        return "undetermined", None, "the job record could not be read — a REFUSAL, not a finding.", None
    if status in ("Completed",):
        return "none", False, "the job completed; there is no failure to classify.", None
    if status in ("InProgress", "Stopping"):
        return "still_running", None, f"the job is {status}; no terminal cause exists yet.", None
    if status == "Stopped" and not failure_reason:
        return "stopped_by_request", False, ("the job was STOPPED, not failed — somebody or something called "
                                             "StopTrainingJob. Not a defect that ports."), None
    hay = str(failure_reason or "")
    for probes, cls, ports, meaning in _FAILURE_SIGNATURES:
        for p in probes:
            if p.lower() in hay.lower():
                return cls, ports, meaning, p
    phases = [t.get("status") for t in (transitions or [])]
    if failure_reason is None:
        return ("failed_no_reason_recorded", None,
                ("the job is Failed and AWS recorded NO FailureReason. That is itself evidence: a container "
                 "that raised normally gets an AlgorithmError string, so an empty reason points AWAY from the "
                 f"science code and toward the control plane. Phases reached: {phases or 'none recorded'}."),
                None)
    return ("unclassified", None,
            f"the FailureReason matched no known signature. Verbatim, unparaphrased: {hay[:400]!r}", None)


def cloudwatch_tail(logs, job_name, max_events=200, log_group="/aws/sagemaker/TrainingJobs"):
    """The container's own stdout for one training job, or a recorded REFUSAL.

    SageMaker writes each job's container output to `<log_group>/<job_name>/algo-1-<epoch>`. If the job never
    reached the container, THERE IS NO STREAM — and that absence is a real discriminator (it separates "the
    code crashed" from "the code never ran"), so it is reported as `no_stream`, distinctly from `refused`.
    """
    try:
        streams = logs.describe_log_streams(logGroupName=log_group, logStreamNamePrefix=f"{job_name}/"
                                            )["logStreams"]
    except Exception as e:  # noqa: BLE001
        return {"state": "refused", "error": f"{type(e).__name__}: {e}",
                "note": "the log group could not be read. This is a REFUSAL — it says nothing about whether "
                        "the container produced output (CLAUDE.md §4)."}
    if not streams:
        return {"state": "no_stream", "log_group": log_group,
                "note": "no log stream exists for this job. SageMaker creates one when the CONTAINER STARTS, "
                        "so its absence is positive evidence the job died BEFORE the container ran — which "
                        "rules out the science code as the cause."}
    out = {"state": "read", "log_group": log_group, "streams": [], "events": []}
    for s in streams[:4]:
        out["streams"].append({"name": s.get("logStreamName"),
                               "first_event_et": et((s.get("firstEventTimestamp") or 0) / 1000.0)
                               if s.get("firstEventTimestamp") else None,
                               "last_event_et": et((s.get("lastEventTimestamp") or 0) / 1000.0)
                               if s.get("lastEventTimestamp") else None})
        try:
            ev = logs.get_log_events(logGroupName=log_group, logStreamName=s["logStreamName"],
                                     limit=max_events, startFromHead=False)["events"]
        except Exception as e:  # noqa: BLE001
            out["events"].append({"stream": s.get("logStreamName"), "error": f"{type(e).__name__}: {e}"})
            continue
        for e in ev:
            out["events"].append({"stream": s.get("logStreamName"),
                                  "t_et": et(e["timestamp"] / 1000.0),
                                  "message": (e.get("message") or "").rstrip()})
    return out


def sagemaker_jobs(sm, name_contains, statuses=("InProgress", "Completed", "Failed", "Stopping", "Stopped")):
    """EVERY training job whose name contains `name_contains`, across every status and the WHOLE history.

    ⚠ THIS IS THE FIX FOR HOW (b) WAS ESTABLISHED. "the last ~40 completed/stopped jobs show nothing newer
    than nr4a3-ternary-2026-07-24" is a statement about one page of a sorted listing. It is NOT the statement
    "no such job has ever existed", and only the second one reconciles with an occupied prefix. `NameContains`
    + full pagination + every status is the read that can actually answer it. None on a refusal.
    """
    out = []
    try:
        for status in statuses:
            token = None
            while True:
                kw = {"StatusEquals": status, "NameContains": name_contains,
                      "SortBy": "CreationTime", "SortOrder": "Descending", "MaxResults": 100}
                if token:
                    kw["NextToken"] = token
                page = sm.list_training_jobs(**kw)
                for s in page.get("TrainingJobSummaries", []):
                    out.append({"name": s["TrainingJobName"], "status": s.get("TrainingJobStatus"),
                                "created_et": et(s.get("CreationTime")),
                                "ended_et": et(s.get("TrainingEndTime"))})
                token = page.get("NextToken")
                if not token:
                    break
    except Exception as e:  # noqa: BLE001
        print(f"[forensic] SageMaker LIST REFUSED: {type(e).__name__}: {e}", flush=True)
        return None
    return out


def run(bucket=None, tag=None, out_path=None):
    import boto3
    b = bucket or DEFAULT_BUCKET
    t = tag or DEFAULT_TAG
    s3 = boto3.client("s3")
    doc = {
        "_what": f"Forensic on s3://{b}/{t}/ — what wrote the checkpoint objects under the selectivity "
                 f"benchmark's tag, and can they be reused. THE ONE HOME for this finding.",
        "_generated_by": "research/modalities/abfe_sel_forensic.py",
        "_timezone": f"all times US Eastern 12-hour, {ET_LABEL}",
        "bucket": b, "tag": t,
    }
    print(f"[forensic] listing s3://{b}/{t}/ …", flush=True)
    rows = list_prefix(s3, b, f"{t}/")
    doc["objects"] = rows
    doc["n_objects"] = (len(rows) if rows is not None else None)
    if rows is None:
        doc["list_refused"] = True

    # The sibling reads that turn one prefix listing into a reconciliation.
    print(f"[forensic] listing the benchmark's STAGED INPUTS (the prefix that is supposed to be full) …",
          flush=True)
    staged = list_prefix(s3, b, "selectivity-benchmark/")
    doc["staged_inputs"] = staged
    doc["staged_inputs_present"] = (sorted(os.path.basename(r["key"]) for r in staged) if staged else staged)

    print(f"[forensic] querying the FULL SageMaker job history for names containing {t.split('-v')[0]!r} …",
          flush=True)
    try:
        sm = boto3.client("sagemaker")
        jobs = sagemaker_jobs(sm, t.split("-v")[0])
    except Exception as e:  # noqa: BLE001
        print(f"[forensic] SageMaker client unavailable: {type(e).__name__}: {e}", flush=True)
        jobs = None
    doc["sagemaker_jobs_matching"] = jobs
    doc["sagemaker_jobs_matching_n"] = (len(jobs) if jobs is not None else None)

    # ---- the JOB-LEVEL forensic: terminal state, cause, money, container log ---------------------------------
    # Every matched job is described in full, not just the one we came looking for, because "which job wrote
    # the prefix" is answered by comparing job clocks to object clocks and that needs all of them.
    described, cw = [], {}
    try:
        sm = boto3.client("sagemaker")
    except Exception as e:  # noqa: BLE001
        print(f"[forensic] SageMaker client unavailable: {type(e).__name__}: {e}", flush=True)
        sm = None
    try:
        logs_client = boto3.client("logs")
    except Exception as e:  # noqa: BLE001
        print(f"[forensic] CloudWatch Logs client unavailable: {type(e).__name__}: {e}", flush=True)
        logs_client = None
    for j in (jobs or []):
        if sm is None:
            break
        print(f"[forensic] describing {j['name']} …", flush=True)
        rec = describe_job(sm, j["name"])
        if rec is None:
            described.append({"name": j["name"], "describe_refused": True})
            continue
        cls, ports, meaning, matched = classify_failure(rec["status"], rec["failure_reason"],
                                                        rec["transitions"])
        rec["failure_class"] = cls
        rec["recurs_on_vast"] = ports
        rec["failure_meaning"] = meaning
        rec["matched_signature"] = matched
        rec["cost"] = money(rec.get("billable_seconds"))
        described.append(rec)
        if logs_client is not None:
            print(f"[forensic] pulling CloudWatch for {j['name']} …", flush=True)
            cw[j["name"]] = cloudwatch_tail(logs_client, j["name"])
    doc["jobs_described"] = described
    doc["container_logs"] = cw
    doc["realized_spend_usd"] = _realized(described)
    doc["ckpt_provenance"] = attribute_objects(rows, described)

    v, why = verdict_from(rows, jobs, t)
    doc["verdict"], doc["verdict_reason"] = v, why
    # THE ACTIONABLE HALF. A forensic that stops at "here is what happened" leaves the next agent to re-derive
    # the consequence, which is the failure mode the program map exists to stop.
    doc["consequence_for_the_vast_run"] = _consequence(v, rows)

    p = out_path or OUT_PATH
    with open(p, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    _print(doc)
    return doc


def _realized(described):
    """Total realized dollars across the described jobs, plus the honest shape of what could NOT be priced.

    Rule 1: a total is DERIVED. It is also SEPARATE from the Vast ladder — this is AWS SageMaker money, a
    different provider and therefore a different ledger, and it must never be summed into a ladder figure.
    """
    priced = [d for d in described if (d.get("cost") or {}).get("usd") is not None]
    unpriced = [d["name"] for d in described if d.get("name") and (d.get("cost") or {}).get("usd") is None]
    total = round(sum(d["cost"]["usd"] for d in priced), 4)
    return {
        "usd_total": total,
        "jobs_priced": len(priced),
        "jobs_unpriceable": unpriced,
        "ledger": "AWS SageMaker managed spot (us-east-2). A SEPARATE LEDGER from the Vast ladder and from "
                  "GCP trial credit — never summed into either (CLAUDE.md §1, §6).",
        "recorded_anywhere_else": "NO. As of this artifact there is no other home for this figure; the "
                                  "in-flight board in STRATEGY.md is Vast-shaped and never carried it.",
    }


def attribute_objects(rows, described):
    """Did one of these jobs write the checkpoint objects? Decided on CLOCKS, not on plausibility.

    ★ THE QUESTION THIS SETTLES, and why it is not answerable from the object list alone. An occupied
    checkpoint prefix reads the same whether a job wrote it minutes ago or something unexplained wrote it
    weeks ago — and the two have opposite consequences, because `nr4a3_abfe.run_window` RESUMES from
    `_last_logged_iter + 1`. A future run onto unattributed state is a run onto unknown provenance.

    The test is an interval containment: an object whose `LastModified` lies between a job's
    `TrainingStartTime` and its `TrainingEndTime` was written while that job held the instance. An object
    OUTSIDE every job's window is `unattributed` — reported as such, never assigned to the nearest job.
    """
    import datetime as _dt
    if rows is None:
        return {"state": "undetermined", "why": "the prefix listing was refused."}
    if not rows:
        return {"state": "empty", "why": "no objects under the tag; nothing to attribute."}

    windows = [{"job": d.get("name"), "status": d.get("status"),
                "start_utc": _utc_of(d.get("training_start_et")),
                "end_utc": _utc_of(d.get("training_end_et")),
                "start_et": d.get("training_start_et"), "end_et": d.get("training_end_et")}
               for d in described if d.get("training_start_et")]
    # A job that never reached Training has no window at all; that is a finding, not a gap to paper over.
    no_window = [d.get("name") for d in described if not d.get("training_start_et")]

    out = {"state": "attributed", "job_windows": windows, "jobs_with_no_training_window": no_window,
           "objects": []}
    for r in rows:
        lm = _utc_of_iso(r.get("last_modified_utc"))
        wrote_by, verdict = None, "unattributed"
        if lm is not None:
            for w in windows:
                s, e = w["start_utc"], w["end_utc"]
                if s and lm >= s and (e is None or lm <= e + _dt.timedelta(minutes=5)):
                    wrote_by, verdict = w["job"], "written_during_this_job"
                    break
            else:
                if windows and all(w["start_utc"] and lm < w["start_utc"] for w in windows):
                    verdict = "predates_every_described_job"
                elif not windows:
                    verdict = ("no_described_job_ever_reached_Training — so NO job in this tag family can "
                               "have written it; the writer is unexplained")
        out["objects"].append({
            "key": r["key"], "size_bytes": r["size_bytes"],
            "last_modified_et": r["last_modified_et"],
            "last_modified_utc": r.get("last_modified_utc"),
            "writer_class": r["writer"], "attributed_to": wrote_by, "attribution": verdict,
        })
    kinds = {o["attribution"] for o in out["objects"]}
    out["summary"] = (
        "every object falls inside a described job's Training window — the provenance is settled"
        if kinds == {"written_during_this_job"} else
        f"MIXED/UNATTRIBUTED provenance: {sorted(kinds)}. An object no job window contains was written by "
        f"something this forensic did not see. ⚠ A future run that RESUMES on this tag would resume onto "
        f"state of unknown origin (`nr4a3_abfe.run_window` continues from `_last_logged_iter + 1`).")
    return out


def _utc_of(et_str):
    """'Aug 02 2026 3:16:52 PM ET' -> naive UTC datetime, using the module's stated fixed offset."""
    import datetime as _dt
    if not et_str:
        return None
    try:
        naive = _dt.datetime.strptime(str(et_str).replace(" ET", ""), "%b %d %Y %I:%M:%S %p")
        return naive - _dt.timedelta(hours=ET_OFFSET_H)
    except Exception:  # noqa: BLE001
        return None


def _utc_of_iso(iso):
    import datetime as _dt
    try:
        return _dt.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")
    except Exception:  # noqa: BLE001
        return None


def _consequence(v, rows):
    if v == "H1_REAL_SAMPLING":
        return ("DO NOT reuse this prefix for the Vast run. A resume would extend somebody else's samples "
                "and the provenance of the combined leg would be unrecoverable. The Vast lane writes to its "
                "OWN prefix (`abfe_sel_vast_launch.RESULT_PREFIX`), so this is already the default; the "
                "finding is that the AWS tag must not be re-dispatched either.")
    if v == "H2_STARTED_NEVER_SAMPLED":
        return ("SAFE TO IGNORE, and safe to leave in place. The objects are a cached solvated system with "
                "no sampling in them, so they cannot contaminate a ΔG. The Vast lane builds its own "
                "reference under its own prefix and never reads this one. Nothing needs deleting.")
    if v == "EMPTY":
        return "Nothing to reconcile — the prefix is empty and the readiness claim stands."
    if v == "UNDETERMINED":
        return ("UNRESOLVED — the listing was refused, so no claim is made either way. The Vast lane writes "
                "to a different prefix regardless, so this does not block it, but the readiness line in "
                "selectivity-benchmark.json remains unverified.")
    return ("The Vast lane writes to its own prefix and never reads this one, so the run is unaffected "
            "whatever wrote these bytes.")


def _print(doc):
    print("\n" + "=" * 100)
    print(f"FORENSIC  s3://{doc['bucket']}/{doc['tag']}/     (all times {ET_LABEL}, 12-hour)")
    print("=" * 100)
    rows = doc.get("objects")
    if rows is None:
        print("  LIST REFUSED — no claim may be made about what is or is not under this prefix.")
    elif not rows:
        print("  (empty)")
    else:
        print(f"  {'size':>10}  {'last modified (ET)':26} {'writer':13} key")
        for r in rows:
            print(f"  {r['size_bytes']:>10}  {r['last_modified_et']:26} {r['writer']:13} {r['key']}")
        for r in rows:
            extra = {k: r[k] for k in ("n_lines", "first_iter", "last_iter", "u_length",
                                       "looks_like_real_sampling", "multipart_parts", "content",
                                       "content_head", "content_error") if k in r}
            if extra:
                print(f"\n  -- {r['key']}")
                print(f"     {r['writer_note']}")
                for k, val in extra.items():
                    print(f"     {k} = {str(val)[:600]}")
    jobs = doc.get("sagemaker_jobs_matching")
    print(f"\n  SageMaker jobs matching the tag family: "
          + ("REFUSED" if jobs is None else (str(len(jobs)) if jobs else "NONE, across every status and the "
                                             "whole paginated history")))
    for j in (jobs or [])[:20]:
        print(f"    {j['status']:10} {j['created_et']:26} {j['name']}")

    for d in doc.get("jobs_described") or []:
        print("\n  " + "-" * 96)
        if d.get("describe_refused"):
            print(f"  {d['name']}: DESCRIBE REFUSED — no claim made.")
            continue
        print(f"  JOB {d['name']}")
        print(f"    status              {d['status']}   (secondary: {d.get('secondary_status')})")
        print(f"    FailureReason       {d.get('failure_reason')!r}")
        print(f"    failure_class       {d.get('failure_class')}   recurs_on_vast={d.get('recurs_on_vast')}")
        print(f"    -> {d.get('failure_meaning')}")
        print(f"    created / start / end (ET)  {d.get('created_et')}  |  "
              f"{d.get('training_start_et')}  |  {d.get('training_end_et')}")
        print(f"    instance            {d.get('instance_type')} x{d.get('instance_count')}  "
              f"spot={d.get('managed_spot')}")
        print(f"    image               {d.get('training_image')}")
        print(f"    checkpoint_s3_uri   {d.get('checkpoint_s3_uri')}")
        c = d.get("cost") or {}
        print(f"    BILLABLE            {d.get('billable_seconds')} s  "
              f"(training {d.get('training_seconds')} s)  =>  ${c.get('usd')}  @ "
              f"${c.get('rate_usd_per_billable_h')}/billable-h")
        print(f"    phases reached      {d.get('phases_reached')}")
        for t in d.get("transitions") or []:
            print(f"      {t['status']:14} {str(t['start_et']):26} {str(t['seconds']):>6}s  "
                  f"{(t.get('message') or '')[:110]}")

    cw = doc.get("container_logs") or {}
    for name, blk in cw.items():
        print(f"\n  CONTAINER LOG  {name}: state={blk.get('state')}")
        if blk.get("state") == "refused":
            print(f"    REFUSED: {blk.get('error')}")
            print(f"    {blk.get('note')}")
        elif blk.get("state") == "no_stream":
            print(f"    {blk.get('note')}")
        else:
            for e in (blk.get("events") or [])[-60:]:
                if e.get("error"):
                    print(f"    ERR {e['error']}")
                else:
                    print(f"    {e['t_et']}  {e['message'][:160]}")

    r = doc.get("realized_spend_usd") or {}
    print(f"\n  REALIZED SPEND (AWS SageMaker ledger, NOT the Vast ladder): ${r.get('usd_total')} "
          f"across {r.get('jobs_priced')} priced job(s); unpriceable: {r.get('jobs_unpriceable')}")
    prov = doc.get("ckpt_provenance") or {}
    print(f"\n  CKPT PROVENANCE: {prov.get('state')} — {prov.get('summary', prov.get('why'))}")
    for o in (prov.get("objects") or []):
        print(f"    {o['size_bytes']:>10}  {o['last_modified_et']:26} {o['attribution']:34} {o['key']}")

    print(f"\n  VERDICT: {doc['verdict']}")
    print(f"  {doc['verdict_reason']}")
    print(f"\n  CONSEQUENCE: {doc['consequence_for_the_vast_run']}")
    print("=" * 100 + "\n")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    bucket = tag = None
    for i, a in enumerate(argv):
        if a == "--bucket" and i + 1 < len(argv):
            bucket = argv[i + 1]
        if a == "--tag" and i + 1 < len(argv):
            tag = argv[i + 1]
    run(bucket=bucket, tag=tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
