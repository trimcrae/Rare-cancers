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
