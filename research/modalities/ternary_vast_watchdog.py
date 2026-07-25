#!/usr/bin/env python3
"""Session-independent watchdog for the VAST ternary lane.

WHY IT HAD TO BE WRITTEN RATHER THAN REUSED
-------------------------------------------
`.github/workflows/ternary-leg-watchdog.yml` already watches ternary legs — but only GCP ones. Every one of
its three questions is GCP-specific: it authenticates by WIF, reads state from GCS, asks "is a
`gcp-ternary-*` VM up?", and its only recovery is to re-dispatch `gpu-ternary-fep-gcp.yml`. Pointing a Vast
leg at it would produce a watchdog that silently watches nothing — the exact failure class this program has
been bitten by repeatedly (a check that reports success while measuring nothing). Under the 2026-07-25
all-runs-on-Vast directive that gap applies to every GPU run the program makes from here, so it is closed
here rather than worked around.

THE THREE QUESTIONS, mirrored from the GCP watchdog:
    result artifact in S3                -> DONE     (disable the entry)
    an instance for this unit alive AND ADVANCING -> RUNNING  (emit progress)
    neither                              -> DIED     (relaunch; resumes from the last committed checkpoint)

TWO THINGS THE GCP VERSION HAS NO ANALOGUE FOR
----------------------------------------------
1. **"Alive" is not "advancing" on Vast.** A rented instance can sit up with a dead container or an idle
   GPU and look perfectly healthy. So RUNNING requires the COMMITTED ITERATION COUNT to have gone up since
   the previous tick, not merely that an instance exists. The commit store is the only durable evidence
   that the science advanced, and unlike the instance it survives a preemption.
2. **A capacity refusal is not a preemption.** If a start comes back
   `{"success": false, "error": "resources_unavailable"}` the machine has no free GPU and no bid fixes it
   (verified 2026-07-25: +26% to the value ceiling changed nothing). The answer is to destroy, add the
   machine to the exclusion set, and pick a different host — never to wait, never to raise the bid. A host
   that never starts has infinite realised $/ns, which the ranking cannot see, so without the exclusion it
   keeps winning selection and keeps failing. That policy already exists in
   `ternary_vast_launch.collect` + `ResourceSpec.exclude_machine_ids`; this module DELEGATES to it rather
   than writing a second policy that can disagree.

SAFETY PROPERTIES CARRIED OVER FROM THE GCP WATCHDOG
  - a per-UTC-day relaunch counter per entry, capping runaway re-dispatch;
  - a no-op on an empty or all-disabled watch list;
  - all state in the repo (the watch list) and S3 (progress + counters), so it survives container restarts
    with no agent awake;
  - outcomes emitted as ::notice::/::error:: annotations, readable from the check-runs API without opening
    a log, and any alert also fails the job so GitHub's own workflow-failure notification fires.

STATE LAYOUT (S3, under the lane prefix)
    watchdog/progress-<unit_id>.json     {"scalar": int, "stall": int, "utc": str}
    watchdog/relaunch-<YYYYMMDD>-<unit_id>.txt
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ternary_vast_launch as tv  # noqa: E402
from gpu_backend import _vast_request  # noqa: E402

WATCH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ternary-vast-watch.json")

# Grace before "zero committed iterations" is called a stall rather than a slow start. A cold unit does
# stage (~15 min) -> pre-equilibrate (~10 min) -> solvate+parameterise the ~146k-atom hybrid (~8-40 min)
# -> minimise 12 replicas, all before its first commit. 90 min is comfortably past a healthy cold start and
# far short of an hour wasted on a hang.
SETUP_GRACE_MIN = float(os.environ.get("TVAST_SETUP_GRACE_MIN") or "90")
# Consecutive no-advance ticks before a frozen counter is a stall. At a 15-min cron and a 40-iteration
# production commit interval (~10 min of MD at 4 fs), 2 ticks is one missed interval, not noise.
STALL_TICKS = int(os.environ.get("TVAST_STALL_TICKS") or "2")


# =============================================================================================================
# decision logic — PURE. This is the part that must be right, so it is separated from every I/O call and
# unit-tested. Each function answers one question and takes the evidence as arguments.
# =============================================================================================================
def classify(*, has_result, instance_alive, instance_age_min, progress_scalar, prev_scalar, prev_stall,
             setup_grace_min=SETUP_GRACE_MIN, stall_ticks=STALL_TICKS):
    """The watchdog's verdict for one entry, and the new stall counter. PURE.

    Returns (verdict, new_stall) where verdict is one of:
        DONE          the result artifact exists — nothing to do
        RUNNING       an instance is up and the committed iteration ADVANCED this tick
        SETUP_STALL   an instance is up, has committed NOTHING, and is past the cold-start grace
        STALLED       an instance is up, has committed something, and has not advanced for `stall_ticks`
        DIED          no result and no instance — relaunch

    Note what is NOT here: "an instance exists" never on its own yields RUNNING. That is the whole
    correction over a liveness ping.
    """
    if has_result:
        return "DONE", 0
    if not instance_alive:
        return "DIED", 0
    advanced = progress_scalar > prev_scalar
    new_stall = 0 if advanced else int(prev_stall) + 1
    if progress_scalar <= 0:
        if instance_age_min >= setup_grace_min:
            return "SETUP_STALL", new_stall
        return "RUNNING", new_stall
    if new_stall >= stall_ticks:
        return "STALLED", new_stall
    return "RUNNING", new_stall


def should_relaunch(verdict, count_today, cap):
    """Is a relaunch authorised? PURE.

    Only DIED relaunches. A STALL does NOT — a relaunch would hang the same way and pay for it again;
    a stall is a diagnosis job, not a retry job. That distinction is inherited from the GCP watchdog and it
    is the reason a stall annotation is an ::error:: rather than a silent re-dispatch.
    """
    if verdict != "DIED":
        return False, ("only a DIED entry relaunches; %s needs diagnosis, not a retry" % verdict)
    try:
        n, c = int(count_today), int(cap)
    except (TypeError, ValueError):
        return False, "unparseable relaunch counter or cap — refusing to relaunch blind"
    if n >= c:
        return False, f"relaunch cap reached ({n}/{c} today) — something is failing repeatedly"
    return True, f"attempt {n + 1}/{c} today"


def enabled_entries(doc):
    """The entries this pass should act on. PURE. An absent/!dict/empty list is a legitimate no-op."""
    if not isinstance(doc, dict):
        return []
    return [w for w in (doc.get("watch") or []) if isinstance(w, dict) and w.get("enabled")]


def watch_entry(leg_id, seed, direction, mode, timestep_fs, warmup_timestep_fs,
                max_relaunches_per_day=8, enabled=True):
    """One watch-list entry. PURE. Carries every parameter a relaunch needs, so the watchdog INVENTS
    NOTHING — it re-dispatches exactly what was launched."""
    return {
        "unit_id": tv.unit_id(leg_id, seed, direction, timestep_fs, warmup_timestep_fs, mode),
        "leg_id": leg_id, "seed": int(seed), "direction": direction, "mode": mode,
        "timestep_fs": str(timestep_fs), "warmup_timestep_fs": str(warmup_timestep_fs),
        "max_relaunches_per_day": int(max_relaunches_per_day),
        "enabled": bool(enabled),
    }


# =============================================================================================================
# I/O
# =============================================================================================================
def load_watch(path=None):
    p = path or WATCH_FILE
    try:
        with open(p) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"watch": []}


def save_watch(doc, path=None):
    with open(path or WATCH_FILE, "w") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")


def arm(mode, path=None, timestep_fs=None, warmup_timestep_fs=None):
    """Register (or re-enable) every unit of `mode` in the watch list. Idempotent.

    Called by the launch job immediately after renting, because the watch list is the ONLY input the cron
    watchdog reads — a launch that does not register its units is a launch nobody is watching.
    """
    dt = str(timestep_fs or os.environ.get("TVAST_TIMESTEP_FS") or tv.DEFAULT_TIMESTEP_FS)
    wdt = str(warmup_timestep_fs or os.environ.get("TVAST_WARMUP_TIMESTEP_FS")
              or tv.DEFAULT_WARMUP_TIMESTEP_FS)
    doc = load_watch(path)
    doc.setdefault("watch", [])
    by_id = {w.get("unit_id"): w for w in doc["watch"] if isinstance(w, dict)}
    added = 0
    for (leg, seed, direction) in tv.units_for(mode):
        e = watch_entry(leg, seed, direction, mode, dt, wdt)
        if e["unit_id"] in by_id:
            by_id[e["unit_id"]]["enabled"] = True
        else:
            doc["watch"].append(e)
            added += 1
    doc["_note"] = ("Watch list for the Vast ternary lane. The cron watchdog "
                    "(.github/workflows/ternary-vast-watchdog.yml) reads ONLY this file; an entry with "
                    "enabled=false is invisible to it. Entries are added by the lane's launch job.")
    save_watch(doc, path)
    print(f"[arm] mode={mode} dt={dt} warmup_dt={wdt}: {added} new entr(ies), "
          f"{len(enabled_entries(doc))} enabled in total")
    return doc


def _s3():
    import boto3
    return boto3.client("s3")


def _read_json_key(bucket, key, default=None):
    try:
        return json.loads(_s3().get_object(Bucket=bucket, Key=key)["Body"].read().decode())
    except Exception:  # noqa: BLE001 — absent state is a legitimate first pass
        return default


def _write_json_key(bucket, key, doc):
    try:
        _s3().put_object(Bucket=bucket, Key=key, Body=json.dumps(doc, indent=2).encode())
        return True
    except Exception as e:  # noqa: BLE001
        print(f"::warning::watchdog state write failed for {key}: {type(e).__name__}: {e}")
        return False


def _annotate(level, title, msg):
    print(f"::{level} title={title}::{msg}")


def tick(path=None, dry_run=False, bucket=None, prefix=None, ref=None):
    """One watchdog pass over the enabled entries. Returns the number of alerts raised."""
    b = bucket or tv.DEFAULT_BUCKET
    p = (prefix or tv.RESULT_PREFIX).rstrip("/")
    doc = load_watch(path)
    entries = enabled_entries(doc)
    print(f"enabled watch entries: {len(entries)} (dry_run={dry_run})")
    if not entries:
        _annotate("notice", "TVAST WATCHDOG idle",
                  "No enabled entries in ternary-vast-watch.json — nothing to watch.")
        return 0

    recs = tv.leg_records(b, p)
    key = os.environ.get("VAST_API_KEY")
    insts = []
    if key:
        try:
            insts = [i for i in _vast_request("GET", "/instances/", key).get("instances", [])
                     if (i.get("label") or "").startswith(tv.LABEL_PREFIX)]
        except Exception as e:  # noqa: BLE001
            # Without the instance list we cannot tell DIED from RUNNING, and guessing DIED would relaunch
            # on top of a live leg — two hosts on one commit prefix. Refuse the pass instead.
            _annotate("error", "TVAST WATCHDOG BLIND",
                      f"could not list Vast instances ({type(e).__name__}: {e}) — refusing to act this "
                      f"pass rather than risk relaunching on top of a live leg.")
            return 1
    else:
        _annotate("error", "TVAST WATCHDOG BLIND",
                  "VAST_API_KEY absent — cannot tell a live leg from a dead one; taking no action.")
        return 1

    alerts = 0
    day = time.strftime("%Y%m%d", time.gmtime())
    for e in entries:
        uid = e["unit_id"]
        print(f"=============== {uid} ===============")
        rec = recs.get(uid) or {}
        has_result = rec.get("status") == "done"

        inst = next((i for i in insts if tv.label_matches_unit(i.get("label"), uid)), None)
        age_min = 0.0
        if inst:
            try:
                age_min = (time.time() - float(inst.get("start_date") or time.time())) / 60.0
            except (TypeError, ValueError):
                age_min = 0.0

        phase, it, scalar = tv.committed_progress(uid, b, p)
        if scalar < 0:
            # A listing failure is NOT zero progress; treating it as zero would manufacture a SETUP_STALL.
            _annotate("warning", "TVAST WATCHDOG progress unreadable",
                      f"{uid} — could not list the commit store this pass; leaving the counters alone.")
            continue

        pkey = f"{p}/watchdog/progress-{uid}.json"
        prev = _read_json_key(b, pkey, {}) or {}
        verdict, stall = classify(
            has_result=has_result, instance_alive=inst is not None, instance_age_min=age_min,
            progress_scalar=scalar, prev_scalar=int(prev.get("scalar") or 0),
            prev_stall=int(prev.get("stall") or 0))
        pstr = f"{phase}/{it}" if phase else "none (stage/pre-equil/setup/minimise)"
        print(f"verdict={verdict} progress={pstr} scalar={scalar} prev={prev.get('scalar')} "
              f"stall={stall} instance={inst.get('id') if inst else None} age={age_min:.0f}min")
        if not dry_run:
            _write_json_key(b, pkey, {"scalar": scalar, "stall": stall,
                                      "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                      "phase": pstr, "verdict": verdict})

        if verdict == "DONE":
            _annotate("notice", "TVAST WATCHDOG DONE",
                      f"{uid} — leg.json is in S3 (dG_morph={rec.get('dg_morph_kcal')}, "
                      f"NaN={rec.get('nan_seen')}). Set enabled=false for this entry.")
            continue
        if verdict == "RUNNING":
            _annotate("notice", "TVAST WATCHDOG RUNNING",
                      f"{uid} — advancing at {pstr} on instance {inst.get('id')} "
                      f"({inst.get('gpu_name')}, up {age_min:.0f} min). Leaving it alone.")
            continue
        if verdict == "SETUP_STALL":
            alerts += 1
            _annotate("error", "TVAST WATCHDOG SETUP STALL",
                      f"{uid} — instance {inst.get('id')} up {age_min:.0f} min with ZERO committed "
                      f"iterations (grace {SETUP_GRACE_MIN:.0f} min). Setup is hung, not slow: check the "
                      f"CUDA probe, the charge cache, minimise steps and GPU utilisation. NOT relaunching "
                      f"— a relaunch would hang the same way.")
            continue
        if verdict == "STALLED":
            alerts += 1
            _annotate("error", "TVAST WATCHDOG STALLED",
                      f"{uid} — instance {inst.get('id')} is up but the committed iteration has been "
                      f"frozen at {pstr} for {stall} consecutive passes. The MD is not advancing. NOT "
                      f"relaunching — diagnose (GPU util, NaN, run log) before spending more.")
            continue

        # DIED: no result, no instance. Relaunch, capped.
        ckey = f"{p}/watchdog/relaunch-{day}-{uid}.json"
        cnt = int((_read_json_key(b, ckey, {}) or {}).get("count") or 0)
        ok, why = should_relaunch(verdict, cnt, e.get("max_relaunches_per_day", 8))
        if not ok:
            alerts += 1
            _annotate("error", "TVAST WATCHDOG CAPPED",
                      f"{uid} — died again but {why}. NOT relaunching; needs a human.")
            continue
        if dry_run:
            _annotate("notice", "TVAST WATCHDOG would-relaunch",
                      f"{uid} — died (no result, no instance), {why}. dry_run=1 so taking no action.")
            continue
        print(f"relaunching {uid} ({why}) — resumes from the last committed checkpoint")
        try:
            # DELEGATE to the launcher. It already skips finished/in-flight units, excludes blocked
            # machines, spreads one unit per machine, and keys the commit prefix by dt — so a relaunch
            # resumes rather than restarts, and cannot double-book a live unit.
            handles = tv.submit(mode=e["mode"], timestep_fs=e["timestep_fs"],
                                warmup_timestep_fs=e["warmup_timestep_fs"],
                                legs=[(e["leg_id"], e["seed"], e["direction"])])
            if handles:
                _write_json_key(b, ckey, {"count": cnt + 1, "unit_id": uid,
                                          "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
                _annotate("notice", "TVAST WATCHDOG RELAUNCHED",
                          f"{uid} — was dead (no result, no instance); rented instance "
                          f"{handles[0].get('instance')} on machine {handles[0].get('machine_id')}, "
                          f"{why}. Resumes from the last committed checkpoint.")
            else:
                alerts += 1
                _annotate("error", "TVAST WATCHDOG RELAUNCH PRODUCED NOTHING",
                          f"{uid} — died and the relaunch rented no host (no rentable offer, or every "
                          f"candidate machine is on the blocked list). Needs a human.")
        except Exception as ex:  # noqa: BLE001 — one entry must not abandon the others
            alerts += 1
            _annotate("error", "TVAST WATCHDOG RELAUNCH FAILED",
                      f"{uid} — died AND the relaunch raised {type(ex).__name__}: {ex}. Needs a human.")
    print(f"watchdog pass complete; {alerts} alert(s)")
    return alerts


def main(argv=None):
    ap = argparse.ArgumentParser(description="Session-independent watchdog for the Vast ternary lane")
    ap.add_argument("--arm", metavar="MODE", help="register every unit of MODE in the watch list")
    ap.add_argument("--tick", action="store_true", help="run one watchdog pass")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--disable", metavar="UNIT_ID", help="set enabled=false for one entry")
    a = ap.parse_args(argv)
    if a.arm:
        arm(a.arm)
        return 0
    if a.disable:
        doc = load_watch()
        for w in doc.get("watch", []):
            if w.get("unit_id") == a.disable:
                w["enabled"] = False
        save_watch(doc)
        print(f"[disable] {a.disable}")
        return 0
    alerts = tick(dry_run=a.dry_run)
    # A non-zero exit makes GitHub send its own workflow-failure notification — the alert path that does
    # not depend on an agent, a session, or anyone thinking to open a log. RUNNING/DONE stay green.
    return 1 if alerts else 0


if __name__ == "__main__":
    raise SystemExit(main())
