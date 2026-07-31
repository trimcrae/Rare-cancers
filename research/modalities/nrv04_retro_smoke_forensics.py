#!/usr/bin/env python3
"""ONE-SHOT FORENSIC: are the NR-V04 retrospective "landed" legs real 5 ns production legs, or smoke legs?

Written 2026-07-31 after `retro_collect` reported 1 -> 17 -> 18 of 18 R1 legs "landed" inside ~2 h, against a
measured ~2.5 h per 6 ns Arm E leg. It answers, from the ARTIFACTS rather than from a story:

  * per leg: mode / n_frames / timed_ns / prod_wall_s / blew_up / E1, and the S3 LastModified of the record;
  * the panel verdict actually persisted by the last collect (`collect/nrv04-retro-collect-latest.json`);
  * the live Vast fleet, whole account, so a retro box and a ternary box are told apart by label;
  * the lane's own price ledger -> what the `nrv04retro-` namespace has actually been billed.

Read-only. Rents nothing, destroys nothing, writes nothing to S3.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BUCKET = os.environ.get("VAST_CKPT_BUCKET", "sagemaker-us-east-2-646605541856")
PREFIX = os.environ.get("NRV04_RETRO_RESULT_PREFIX") or "nrv04-retro-results"

# The genuine leg on record (run 30621389167, retro_noncov_nr4a2__m1 s0). A leg is REAL only if it matches
# this shape; anything shorter is a plumbing smoke, whatever `panel_complete` says.
GENUINE = {"mode": "run", "n_frames": 500, "timed_ns": 5.0, "prod_ns": 5.0}


def _et(dt):
    import datetime
    return (dt - datetime.timedelta(hours=4)).strftime("%-I:%M %p ET %b %-d")


def main():
    import boto3
    s3 = boto3.client("s3")

    # ── 1 · every leg record under the lane's prefix ───────────────────────────────────────────────────
    keys, tok = [], None
    while True:
        kw = {"Bucket": BUCKET, "Prefix": f"{PREFIX}/"}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            if o["Key"].rsplit("/", 1)[-1].startswith("leg_") and o["Key"].endswith(".json"):
                keys.append((o["Key"], o["LastModified"], o["Size"]))
        tok = r.get("NextContinuationToken")
        if not r.get("IsTruncated"):
            break

    print(f"=== {len(keys)} leg record(s) under s3://{BUCKET}/{PREFIX}/ ===", flush=True)
    hdr = (f"{'UNIT':<40} {'MODE':<6} {'FRAMES':>6} {'timed_ns':>9} {'prod_ns':>7} {'wall_s':>8} "
           f"{'ns/day':>7} {'blew':>5} {'E1_A':>7}  RECORD WRITTEN (ET)")
    print(hdr, flush=True)
    print("-" * len(hdr), flush=True)
    rows, real, smoke, other = [], [], [], []
    for k, mtime, size in sorted(keys, key=lambda x: x[1]):
        d = json.loads(s3.get_object(Bucket=BUCKET, Key=k)["Body"].read().decode())
        unit = k.split("/")[-2]
        r1 = d.get("R1_interface") or d.get("R1") or {}
        row = {
            "unit": unit, "key": k, "size": size, "written_utc": mtime.isoformat(),
            "written_et": _et(mtime.replace(tzinfo=None)),
            "panel": d.get("panel"), "leg_id": d.get("leg_id"), "seed": d.get("seed"),
            "mode": d.get("mode"), "n_frames": d.get("n_frames"), "timed_ns": d.get("timed_ns"),
            "prod_ns": d.get("prod_ns"), "equil_ns": d.get("equil_ns"),
            "prod_wall_s": d.get("prod_wall_s"), "ns_per_day": d.get("ns_per_day"),
            "blew_up": d.get("blew_up"), "n_atoms": (d.get("meta") or {}).get("n_atoms"),
            "e1_plateau_A": r1.get("plateau_A"), "e2_stable": r1.get("stable"),
            "analysis_traj": d.get("analysis_traj"),
        }
        rows.append(row)
        verdict = ("REAL" if all(row.get(f) == v for f, v in GENUINE.items())
                   else "SMOKE" if row["mode"] == "smoke" else "OTHER")
        (real if verdict == "REAL" else smoke if verdict == "SMOKE" else other).append(row)
        print(f"{unit:<40} {str(row['mode']):<6} {str(row['n_frames']):>6} {str(row['timed_ns']):>9} "
              f"{str(row['prod_ns']):>7} {str(row['prod_wall_s']):>8} {str(row['ns_per_day']):>7} "
              f"{str(row['blew_up']):>5} {str(row['e1_plateau_A']):>7}  {row['written_et']}", flush=True)

    print(f"\n=== CLASSIFICATION vs the genuine leg {GENUINE} ===", flush=True)
    print(f"  REAL  (mode=run, 500 frames, 5.0 ns) : {len(real)}  {[r['unit'] for r in real]}", flush=True)
    print(f"  SMOKE (mode=smoke)                   : {len(smoke)}", flush=True)
    print(f"  OTHER (neither)                      : {len(other)}  {[r['unit'] for r in other]}", flush=True)

    # ── 2 · the verdict the last collect actually persisted ────────────────────────────────────────────
    print("\n=== LAST PERSISTED COLLECT READOUT ===", flush=True)
    try:
        c = json.loads(s3.get_object(Bucket=BUCKET,
                                     Key=f"{PREFIX}/collect/nrv04-retro-collect-latest.json"
                                     )["Body"].read().decode())
        print(json.dumps({k: v for k, v in c.items() if k not in ("legs", "raw_keys", "phases")},
                         indent=2)[:6000], flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  (unreadable: {e})", flush=True)

    # ── 3 · the live fleet, WHOLE ACCOUNT, labelled ────────────────────────────────────────────────────
    print("\n=== LIVE VAST INSTANCES (whole account) ===", flush=True)
    try:
        import time as _t
        from nrv04_vast_launch import _vast_request
        insts = _vast_request("GET", "/instances/", os.environ.get("VAST_API_KEY"),
                              params={"owner": "me"}).get("instances", [])
        now = _t.time()
        print(f"  n_instances = {len(insts)}", flush=True)
        for i in sorted(insts, key=lambda x: (x.get("label") or "")):
            try:
                age = (now - float(i.get("start_date"))) / 60.0
            except (TypeError, ValueError):
                age = None
            print(f"  id={i.get('id')} label={i.get('label')!r} actual={i.get('actual_status')} "
                  f"cur={i.get('cur_state')} gpu_util={i.get('gpu_util')} "
                  f"age_min={None if age is None else round(age, 1)} "
                  f"dph_total=${i.get('dph_total')} msg={str(i.get('status_msg'))[:60]!r}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  (fleet UNREADABLE: {type(e).__name__}: {e})", flush=True)

    # ── 4 · what the namespace has been billed ─────────────────────────────────────────────────────────
    print("\n=== LANE PRICE LEDGER (nrv04retro- namespace) ===", flush=True)
    try:
        led = json.loads(s3.get_object(Bucket=BUCKET,
                                       Key=f"{PREFIX}/nrv04-price-ledger.json")["Body"].read().decode())
        L = led.get("ledger", led)
        tot = 0.0
        for lbl, v in sorted(L.items()):
            c = v.get("cost_usd")
            tot += (c or 0.0)
            print(f"  {lbl:<44} uptime_s={v.get('uptime_s'):>7} dph=${v.get('dph_total')} "
                  f"cost=${c} final={v.get('final')}", flush=True)
        print(f"  LEDGER SUM = ${round(tot, 4)}   summary={json.dumps(led.get('summary'))}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  (unreadable: {e})", flush=True)

    json.dump({"legs": rows, "n_real": len(real), "n_smoke": len(smoke), "n_other": len(other)},
              open("nrv04-retro-smoke-forensics.json", "w"), indent=2, default=str)
    print("\n[forensics] wrote nrv04-retro-smoke-forensics.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
