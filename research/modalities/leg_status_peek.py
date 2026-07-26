#!/usr/bin/env python3
"""Read a ternary leg's three status artifacts straight from S3 — no CI run, no queue, no spend.

WHY THIS EXISTS (2026-07-26). `rung5aks-cofold.yml mode=leg_diag` is the sanctioned $0 progress read, and it
is genuinely free — `aws s3 cp`/`ls` and `cat`, no `docker run`, no Vast call. But it is a workflow, and the
workflow declares

    concurrency:
      group: rung5aks-cofold-${{ github.ref }}
      cancel-in-progress: false

so a read QUEUES behind whatever else the lane is doing on that ref. That is correct behaviour — you do not
want two launches interleaved — but it means the cheap read is unavailable exactly when the lane is busy,
which is exactly when a monitoring session wants one. A 40-minute diagnostic makes an hourly status check a
40-minute wait.

This reads the same three objects directly. It is the monitoring path, not a replacement for `leg_diag`:
`leg_diag` also prints the failing attempt's LOG, which is what you want once something has actually gone
wrong. This answers only "where is it, and has it moved".

READ THE STATUS FIELD, NOT THE PRESENCE OF THE FILE. `leg.json` exists for failures too, carrying
`"status": "failed"` — inferring success from the object existing is the mistake this docstring is here to
stop.

Usage:
    python3 research/modalities/leg_status_peek.py                    # the live 5a-KS legs
    python3 research/modalities/leg_status_peek.py <unit> [<unit>...]
"""
import json
import os
import sys
import datetime

BUCKET = os.environ.get("TERNARY_BUCKET", "sagemaker-us-east-2-646605541856")
PREFIX = os.environ.get("TERNARY_LEG_PREFIX", "ternary-vast/legs")

DEFAULT_UNITS = [
    "5aks_d0_to_d__ternary_nr4a3_r0_dt4.0fs_wu1.0_5aks",
    "5aks_d0_to_d__ternary_nr4a1_r0_dt4.0fs_wu1.0_5aks",
]


def _et(ts):
    """UTC -> US Eastern, 12-hour. The repo reports ET; S3 and the legs speak UTC."""
    if not ts:
        return "?"
    if isinstance(ts, str):
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d %H:%M:%S"):
            try:
                ts = datetime.datetime.strptime(ts.strip(), fmt)
                break
            except ValueError:
                continue
        else:
            return str(ts)
    if isinstance(ts, datetime.datetime):
        if ts.tzinfo is not None:
            ts = ts.replace(tzinfo=None)
        return (ts - datetime.timedelta(hours=4)).strftime("%I:%M %p ET")
    return str(ts)


class Unreadable(RuntimeError):
    """The store could not be read. This is NOT the same as the object not existing."""


def _get(s3, key):
    """Return (body, mtime), or (None, None) ONLY when the object genuinely does not exist.

    THE BUG THIS SHAPE EXISTS TO PREVENT, caught on this file's first run (2026-07-26). The original
    swallowed every ClientError as "absent", so an `InvalidAccessKeyId` — the credentials in the dev
    sandbox are not valid for this bucket — printed a clean, calm report saying all four artifacts were
    missing on both legs. One of those legs had definitely written a status.json. A monitoring tool whose
    failure mode is "everything looks quiet" is worse than no tool: it manufactures the exact reassurance
    the tight-monitoring rule exists to forbid, and the same mistake (a null read reported as zero) had
    already been fixed once today in the fan-out monitor.

    So: NoSuchKey/404 is absence and returns None. Anything else — credentials, permissions, region,
    network — RAISES.
    """
    from botocore.exceptions import ClientError
    try:
        o = s3.get_object(Bucket=BUCKET, Key=key)
        return o["Body"].read().decode("utf-8", "replace"), o["LastModified"]
    except ClientError as e:
        code = (e.response.get("Error", {}) or {}).get("Code", "")
        status = (e.response.get("ResponseMetadata", {}) or {}).get("HTTPStatusCode")
        if code in ("NoSuchKey", "404") or status == 404:
            return None, None                               # genuinely not there — a real answer
        raise Unreadable(
            f"cannot READ s3://{BUCKET}/{key} — {code or type(e).__name__}. This is NOT 'the leg has "
            f"written nothing': the store did not answer. Do not read silence as progress.") from e


def peek(units):
    import boto3
    s3 = boto3.client("s3")
    out = []
    for u in units:
        base = f"{PREFIX}/{u}"
        phase, phase_mt = _get(s3, f"{base}/phase.txt")
        legs, _ = _get(s3, f"{base}/leg.json")
        stat, _ = _get(s3, f"{base}/status.json")

        rec = {"unit": u, "phase_txt": (phase or "").strip() or None,
               "phase_last_written": _et(phase_mt)}

        # leg.json exists on FAILURE too. Read the field.
        if legs:
            try:
                d = json.loads(legs)
                rec["leg_status"] = d.get("status")
                rec["dg_morph_kcal"] = d.get("dg_morph_kcal")
                rec["done"] = d.get("status") == "done"
            except json.JSONDecodeError:
                rec["leg_status"] = "UNPARSEABLE leg.json"
        else:
            rec["leg_status"] = None
            rec["done"] = False

        if stat:                                            # written only by fail()
            try:
                d = json.loads(stat)
                rec["failure"] = {"status": d.get("status"), "phase": d.get("phase"), "rc": d.get("rc")}
            except json.JSONDecodeError:
                rec["failure"] = {"raw": stat[:200]}
        else:
            rec["failure"] = None
        out.append(rec)
    return out


def main():
    units = sys.argv[1:] or DEFAULT_UNITS
    try:
        rows = peek(units)
    except Unreadable as e:
        print(f"UNREADABLE: {e}")
        print("Fall back to `rung5aks-cofold.yml mode=leg_diag` (runs in CI, where the credentials are "
              "real). NOTE it shares the lane's concurrency group, so it QUEUES behind a running job.")
        return 2
    for r in rows:
        short = r["unit"].split("__")[-1]
        print(f"== {short}")
        print(f"   phase.txt     : {r['phase_txt'] or 'ABSENT (not started, or pre-phase)'}")
        print(f"   last written  : {r['phase_last_written']}")
        if r["failure"]:
            print(f"   status.json   : FAILURE {r['failure']}   <- written only by fail()")
        else:
            print("   status.json   : absent (no recorded failure)")
        if r["leg_status"] is None:
            print("   leg.json      : absent (leg has not terminated)")
        elif r.get("done"):
            print(f"   leg.json      : DONE, dg_morph_kcal={r.get('dg_morph_kcal')}")
        else:
            print(f"   leg.json      : present but status={r['leg_status']!r} — NOT done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
