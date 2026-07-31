#!/usr/bin/env python3
"""
NR-V04 retrospective — PRICE LEDGER FORENSICS (strictly read-only).

THE QUESTION. `s3://<bucket>/nrv04-retro-results/_price_ledger.json` carries an entry for
`nrv04retro-retro_noncov_nr4a2-m1-r0` reading `uptime_s: 561615` = 156.0 h = 6.50 days, costed at $25.83 —
while that leg's own record says `prod_wall_s: 3730.5` (1.04 h). The ledger attributes ~151x more uptime than
the leg it is named after computed. Two hypotheses, and a plausible story is not a diagnosis (CLAUDE.md §4):

  H1  a real leak — a host was rented for that unit and left running ~6.5 days after the leg finished.
  H2  the field means something else — a record age, a create-time delta, a whole-machine lifetime, or a
      wall-clock difference taken at read time rather than at teardown.

WHAT THE WRITER ACTUALLY DOES (`nrv04_vast_launch._update_price_ledger`, the `now = time.time()` loop):

    now = time.time()
    for i in insts:                       # insts = /instances/?owner=me FILTERED to this lane's label prefix
        up_s = now - float(i.get("start_date") or now)
        ...
        if prev.get("final"): continue    # a finalized entry is never rewritten
        ledger[label] = {"uptime_s": round(up_s), ..., "final": label in done_units}

so `uptime_s` is **the age of a LIVE rental at the instant some collect polled**, not the leg's compute time
and not the rental's total lifetime. Three consequences this script exists to test, because they decide
between H1 and H2 and they point in OPPOSITE directions:

  (a) The loop iterates only over instances the Vast API is returning RIGHT NOW. A destroyed instance is not
      in `insts`, so no entry can ever be written for a host that is already gone. **Any `uptime_s` at all is
      therefore a live observation of a rental that had existed that long.**
  (b) `uptime_s` <= the rental's true billed wall clock, always — the poll happens at or before teardown. So
      each entry is a LOWER bound on that host's lifetime, never an upper one.
  (c) It is *not* a lower bound on the leg's cost in the other direction: `final` latches at the FIRST poll
      where the label appears in `done_units`, and if the result predates the rental (a re-run over an
      existing leg_*.json) that is the first poll after launch — freezing a minutes-old age on a host that
      then ran for hours. The same field therefore over-reports (a) and under-reports (c).

The discriminating observation, and why it is available: `start_date`'s meaning is checked IN THIS LANE
against a host whose rental age we know independently. `congeneric_fanout_vast._age_min` already documents
that on a Vast instance object `duration` is the HOST MACHINE's uptime (it read 145 days on a box just
rented) while `start_date` is ours — but that was measured on another lane, so this script re-measures it
here: for every live instance it prints `start_date` as a wall time AND the age it implies, so a box rented
minutes ago must read minutes. If it does, a 561615 s reading is 6.5 days of rental and H1 is settled.

It is strictly READ-ONLY: S3 `list_objects_v2`/`get_object` and Vast `GET /instances/`. It never destroys,
launches, stops, or writes to S3. The only thing it writes is a local JSON report.

Usage (CI, with AWS creds and VAST_API_KEY):
    python nrv04_retro_price_forensics.py --bucket $VAST_CKPT_BUCKET --out nrv04-retro-price-forensics.json
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RESULT_PREFIX = "nrv04-retro-results"
LEDGER_KEY = f"{RESULT_PREFIX}/_price_ledger.json"
LABEL_PREFIX = "nrv04retro-"


def _et(epoch):
    """US Eastern, 12-hour — CLAUDE.md §1. EDT = UTC-4 across this program's whole calendar."""
    if epoch is None:
        return None
    d = datetime.datetime.fromtimestamp(float(epoch), datetime.timezone.utc) - datetime.timedelta(hours=4)
    return d.strftime("%-I:%M %p ET %a %b %-d, %Y")


def _hms(seconds):
    if seconds is None:
        return None
    s = int(seconds)
    return f"{s // 86400}d {s % 86400 // 3600}h {s % 3600 // 60}m"


def classify_entry(uptime_s, dph_total, final, leg_prod_wall_s=None):
    """PURE (unit-tested). What one ledger row can and cannot support, in words a reader cannot misread.

    Returns a dict with `means`, `is_bound` and `leak_ratio`. The point of the `means` string is that
    `uptime_s` is NOT "how long the leg ran" — the single mistake this whole module exists to prevent."""
    out = {
        "uptime_s": uptime_s,
        "uptime_human": _hms(uptime_s),
        "dph_total": dph_total,
        "final": bool(final),
        "means": "age of a LIVE rental at the instant a collect polled it — NOT the leg's compute time, "
                 "and NOT the rental's total lifetime",
        "is_bound": "LOWER bound on that host's billed wall clock (the poll is at or before teardown)",
        "leak_ratio": None,
        "verdict": None,
    }
    if uptime_s is None:
        return out
    if leg_prod_wall_s:
        out["leak_ratio"] = round(float(uptime_s) / float(leg_prod_wall_s), 1)
    # A rental whose observed age exceeds a generous whole-leg budget cannot be explained by the leg.
    # 6 h: the lane's own MAX_LEG_MIN backstop is 240 min, plus provisioning.
    if uptime_s > 6 * 3600:
        out["verdict"] = ("UNEXPLAINED BY THE LEG — a host of this lane was alive this long. The leg's own "
                          "backstop is MAX_LEG_MIN=240 min, so this is idle rental time, not compute.")
    else:
        out["verdict"] = "within a plausible single-leg rental (provision + run + poll lag)"
    return out


def survey(bucket, key=None, s3c=None):
    """Read the ledger, the lane's S3 objects and the live Vast census. Returns the report dict."""
    import boto3
    s3c = s3c or boto3.client("s3")
    report = {
        "_what": "read-only forensics on nrv04-retro-results/_price_ledger.json — what uptime_s measures, "
                 "and whether the 6.5-day entry is a rental leak",
        "bucket": bucket,
        "ledger_key": LEDGER_KEY,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_et": _et(datetime.datetime.now(datetime.timezone.utc).timestamp()),
    }

    # ---- 1. the ledger itself, and WHEN it was last written -------------------------------------------
    try:
        obj = s3c.get_object(Bucket=bucket, Key=LEDGER_KEY)
        doc = json.loads(obj["Body"].read().decode())
        ledger_mtime = obj["LastModified"].timestamp()
    except Exception as e:  # noqa: BLE001
        report["ledger_error"] = f"{type(e).__name__}: {e}"
        return report
    ledger = doc.get("ledger", {})
    report["ledger_last_modified_utc"] = obj["LastModified"].strftime("%Y-%m-%dT%H:%M:%SZ")
    report["ledger_last_modified_et"] = _et(ledger_mtime)
    report["ledger_summary"] = doc.get("summary")
    report["ledger_raw"] = ledger

    # ---- 2. the lane's S3 objects: when did each unit actually WRITE anything? ------------------------
    objects, token = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": f"{RESULT_PREFIX}/"}
        if token:
            kw["ContinuationToken"] = token
        page = s3c.list_objects_v2(**kw)
        for o in page.get("Contents", []):
            objects.append({"key": o["Key"], "bytes": o["Size"],
                            "mtime": o["LastModified"].timestamp()})
        if not page.get("IsTruncated"):
            break
        token = page.get("NextContinuationToken")
    by_unit = {}
    for o in objects:
        parts = o["key"].split("/")
        unit = parts[-2] if len(parts) > 2 else "(root)"
        b = by_unit.setdefault(unit, {"first_write": o["mtime"], "last_write": o["mtime"], "keys": []})
        b["first_write"] = min(b["first_write"], o["mtime"])
        b["last_write"] = max(b["last_write"], o["mtime"])
        b["keys"].append({"key": parts[-1], "bytes": o["bytes"],
                          "mtime_et": _et(o["mtime"])})
    report["s3_units"] = {u: {"first_write_et": _et(v["first_write"]),
                              "last_write_et": _et(v["last_write"]),
                              "keys": v["keys"]} for u, v in sorted(by_unit.items())}

    # ---- 3. the leg records, for prod_wall_s / mode -----------------------------------------------------
    legs = {}
    for o in objects:
        name = o["key"].rsplit("/", 1)[-1]
        if not (name.startswith("leg_") and name.endswith(".json")):
            continue
        unit = o["key"].split("/")[-2]
        try:
            d = json.loads(s3c.get_object(Bucket=bucket, Key=o["key"])["Body"].read().decode())
        except Exception:  # noqa: BLE001
            continue
        legs[unit] = {k: d.get(k) for k in ("panel", "leg_id", "mode", "prod_ns", "equil_ns", "n_frames",
                                            "timed_ns", "prod_wall_s", "ns_per_day", "blew_up")}
        legs[unit]["record_written_et"] = _et(o["mtime"])
        legs[unit]["record_written_epoch"] = o["mtime"]
    report["legs"] = legs

    # ---- 4. per-entry reading, with the implied rental start ------------------------------------------
    # `uptime_s` was taken at SOME poll at or before `ledger_mtime`, so `ledger_mtime - uptime_s` is the
    # LATEST the rental can have started. An earlier poll only pushes the true start earlier still.
    rows = {}
    for label, e in sorted(ledger.items()):
        unit = label[len(LABEL_PREFIX):] if label.startswith(LABEL_PREFIX) else label
        leg = legs.get(label) or legs.get(unit) or {}
        row = classify_entry(e.get("uptime_s"), e.get("dph_total"), e.get("final"),
                             leg.get("prod_wall_s"))
        row["cost_usd_recorded"] = e.get("cost_usd")
        if e.get("uptime_s") is not None:
            row["latest_possible_rental_start_et"] = _et(ledger_mtime - float(e["uptime_s"]))
        row["leg_mode"] = leg.get("mode")
        row["leg_prod_wall_s"] = leg.get("prod_wall_s")
        row["leg_record_written_et"] = leg.get("record_written_et")
        rows[label] = row
    report["entries"] = rows

    # ---- 5. the LIVE Vast census — and the control that pins what start_date means -------------------
    key = key or os.environ.get("VAST_API_KEY")
    if not key:
        report["vast"] = {"error": "no VAST_API_KEY — census not taken"}
        return report
    from gpu_backend import _vast_request
    import time
    try:
        insts = _vast_request("GET", "/instances/", key, params={"owner": "me"}).get("instances", [])
    except Exception as e:  # noqa: BLE001
        report["vast"] = {"error": f"{type(e).__name__}: {e}"}
        return report
    now = time.time()
    census = []
    for i in insts:
        sd = i.get("start_date")
        census.append({
            "id": i.get("id"), "label": i.get("label"),
            "actual_status": i.get("actual_status"), "cur_state": i.get("cur_state"),
            "dph_total": i.get("dph_total"), "gpu_util": i.get("gpu_util"),
            "machine_id": i.get("machine_id"),
            "start_date_epoch": sd, "start_date_et": _et(sd),
            # THE CONTROL. This is `now - start_date`, i.e. exactly the arithmetic the ledger writer uses.
            # A box rented minutes ago must read minutes. `duration` is printed beside it because that is
            # the field that reads in the hundreds of thousands (the host machine's uptime) and confusing
            # the two is the specific mistake `congeneric_fanout_vast._age_min` was written to stop.
            "start_date_age_s": round(now - float(sd)) if sd else None,
            "start_date_age_human": _hms(now - float(sd)) if sd else None,
            "duration_field": i.get("duration"),
            "duration_human": _hms(i.get("duration")) if i.get("duration") else None,
        })
    census.sort(key=lambda r: (r["label"] or ""))
    report["vast"] = {
        "n_instances_on_account": len(insts),
        "n_this_lane": sum(1 for c in census if str(c["label"] or "").startswith(LABEL_PREFIX)),
        "census": census,
        "still_billing_this_lane": [c for c in census
                                    if str(c["label"] or "").startswith(LABEL_PREFIX)],
    }
    return report


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", default=os.environ.get("VAST_CKPT_BUCKET"))
    ap.add_argument("--out", default="nrv04-retro-price-forensics.json")
    a = ap.parse_args(argv)
    if not a.bucket:
        raise SystemExit("--bucket (or $VAST_CKPT_BUCKET) is required")
    rep = survey(a.bucket)
    json.dump(rep, open(a.out, "w"), indent=2)
    print(json.dumps(rep, indent=2), flush=True)

    # A readable verdict block, so the finding is not buried in a JSON dump.
    print("\n" + "=" * 108, flush=True)
    print("VERDICT INPUTS — what uptime_s measures, read against the live census", flush=True)
    print("=" * 108, flush=True)
    print(f"ledger last written : {rep.get('ledger_last_modified_et')}", flush=True)
    v = rep.get("vast") or {}
    print(f"vast census         : {v.get('n_instances_on_account')} instance(s) on the account; "
          f"{v.get('n_this_lane')} carry {LABEL_PREFIX!r}", flush=True)
    for c in (v.get("census") or []):
        print(f"  id={c['id']} label={c['label']} status={c['actual_status']} "
              f"start_date={c['start_date_et']} age={c['start_date_age_human']} "
              f"duration_field={c['duration_human']} dph=${c['dph_total']}", flush=True)
    print("-" * 108, flush=True)
    for label, r in sorted((rep.get("entries") or {}).items(),
                           key=lambda kv: -(kv[1].get("uptime_s") or 0)):
        print(f"  {label:48s} uptime={r['uptime_human']:>14s} ${r['cost_usd_recorded']:>8} "
              f"final={r['final']} leg_mode={r['leg_mode']} "
              f"latest_start={r.get('latest_possible_rental_start_et')}", flush=True)
        if r.get("leak_ratio"):
            print(f"      leg prod_wall_s={r['leg_prod_wall_s']} -> uptime is {r['leak_ratio']}x the "
                  f"computed leg. {r['verdict']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
