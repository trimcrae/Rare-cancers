#!/usr/bin/env python3
# =============================================================================================================
# WHY THE TERNARY REPLICATE LEGS COMMIT NOTHING — read from the CONTAINER'S OWN OUTPUT, not from exit status
# =============================================================================================================
# THE OBSERVATION THIS EXISTS TO EXPLAIN (measured 2026-07-27, three consecutive cohorts of RUNG 2b's
# valB_mini replicates). Every cohort rents four hosts for four units. Every cohort, the two BINARY legs
# advance normally and the two TERNARY legs commit ABSOLUTELY NOTHING — not a slow first checkpoint, zero:
#
#   cohort 3, `task=collect` 6:17 PM ET
#     ternary_vhl_r1  46040507  exited   committed=none/0        phase md-running, log froze 3 min in
#     binary_vhl_r1   46040514  running  committed=warmup/832    6.0 s/iter, committing every 64 iterations
#     ternary_vhl_r2  46040577  exited   committed=none/0        phase md-running, log froze 2 min in
#     binary_vhl_r2   46040659  exited   committed=warmup/256    committed, then lost its host
#
# Three cohorts of the same asymmetry is a PATTERN, not spot churn — preemption does not preferentially kill
# one leg type six times out of six. And it is not cosmetic: `ternary_fep_reduce.per_replicate_ddg_coop`
# forms ΔΔG_coop over `set(ternary) & set(binary)`, so while the ternary side never commits, n_paired stays 1
# and `calibration_gate` returns INDETERMINATE no matter how well the binary legs run. Every dollar spent on
# binary-only replicates buys nothing.
#
# ⛔ WHY NOT THE EXIT STATUS, AND WHY NOT S3 (CLAUDE.md §4 — a plausible story is a HYPOTHESIS, not a
# diagnosis). The on-host log reaches S3 through a `while true; sleep 120` copy loop in the onstart script.
# So the last TWO MINUTES of output — which for a leg that dies is the entire interesting part, including
# whatever the kernel or the runtime said on the way out — is exactly the part S3 never receives. The
# instance's `actual_status` says `exited`; it cannot say why, and the three candidate mechanisms
# (an out-of-memory kill on the ~142k-particle system where the binary's ~94k fits; a missing or mis-keyed
# stage-cache entry; a host reclaim that the ternary leg loses because it takes longer to reach its first
# checkpoint) all produce the same `exited`.
#
# So this reads the two sources that CAN discriminate:
#
#   1. `request_logs` — the container's console, straight from the provider, including the part S3 never got.
#      Vast's flow is PUT-then-poll-a-URL; that path is already implemented and reviewed in
#      `nrv04_vast_launch._vast_instance_logs`, so it is IMPORTED here rather than re-typed (CLAUDE.md §1).
#   2. The `attempts/` archive in S3. The onstart script copies the previous attempt's `run.log` aside before
#      truncating it, so every cohort's failure is still on disk under `legs/<uid>/attempts/`. Reading the
#      LAST LINE of every attempt for every unit turns "it failed three times" into "it failed three times AT
#      THE SAME LINE", which is the difference between a deterministic defect and bad luck — and it costs $0.
#
# Plus the host spec each unit actually landed on (RAM/disk/GPU), because if the ternary legs are being
# refused by hosts the binary legs clear, that is a SPEC problem — `resource_spec` asking for too little —
# and no number of retries fixes it.
#
# $0: reads only. It never rents, never destroys, never nudges.
# =============================================================================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ternary_vast_launch as tv  # noqa: E402

# The tail of an attempt log that is worth printing. Long enough to carry a Python traceback with its frames,
# short enough that four units x several attempts still fits inside a job log GitHub truncates from the tail.
ATTEMPT_TAIL_LINES = int(os.environ.get("TVAST_DIAG_TAIL") or "25")

# Fields of the instance record this may print. ALLOW-LIST, for the same reason
# `ternary_vast_launch.rented_rate_row`'s is: the record carries `jupyter_token`, `ssh_host` and
# `public_ipaddr`, and a diagnostic's output gets pasted into issues and commit messages. The four capacity
# fields are the point of the exercise — they are what answers "did the ternary leg land somewhere smaller".
SAFE_INSTANCE_FIELDS = ("id", "machine_id", "label", "actual_status", "cur_state", "intended_status",
                        "status_msg", "gpu_name", "num_gpus", "gpu_ram", "cpu_ram", "cpu_cores_effective",
                        "disk_space", "disk_util", "mem_usage", "mem_limit", "gpu_util", "dph_total",
                        "start_date", "image_uuid")


def safe_instance(inst):
    """The printable projection of an instance record. PURE."""
    return {k: inst.get(k) for k in SAFE_INSTANCE_FIELDS if k in inst}


def arm_of(unit_id):
    """`ternary` / `binary` / `solvent` / None. PURE. The whole diagnosis is a comparison BETWEEN ARMS, so
    the grouping key has to come from the unit id rather than from a hand-maintained list that can go stale
    the next time a mode is added."""
    for arm in ("ternary", "binary", "solvent"):
        if f"__{arm}_" in unit_id or unit_id.endswith(f"__{arm}"):
            return arm
    return None


def last_meaningful_line(text):
    """The last line that is not blank. PURE. This is the whole comparison in one value: if every ternary
    attempt across every cohort ends on the SAME line and the binary attempts do not, the failure is
    deterministic and lives at that line."""
    for ln in reversed((text or "").splitlines()):
        if ln.strip():
            return ln.strip()
    return ""


def attempt_logs(uid, bucket=None, prefix=None):
    """[{key, utc, bytes, last_line, tail}] for every archived attempt of this unit, oldest first, plus the
    CURRENT run.log last. One entry per cohort this unit has been through."""
    b = bucket or tv.DEFAULT_BUCKET
    p = (prefix or tv.RESULT_PREFIX).rstrip("/")
    s3 = tv._s3()
    out = []
    for key in (f"{p}/legs/{uid}/attempts/", None):
        if key is None:
            keys = [f"{p}/legs/{uid}/run.log"]
        else:
            keys = []
            try:
                for page in s3.get_paginator("list_objects_v2").paginate(Bucket=b, Prefix=key):
                    keys += [o["Key"] for o in page.get("Contents", []) if o["Key"].endswith(".log")]
            except Exception as e:  # noqa: BLE001 — a unit with no archive is a legitimate first attempt
                print(f"    (attempts unreadable for {uid}: {type(e).__name__}: {e})")
            keys.sort()
        for k in keys:
            try:
                o = s3.get_object(Bucket=b, Key=k)
                txt = o["Body"].read().decode(errors="replace")
            except Exception:  # noqa: BLE001 — run.log may not exist yet
                continue
            lines = [ln for ln in txt.splitlines() if ln.strip()]
            out.append({"key": k, "utc": o["LastModified"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "bytes": o["ContentLength"], "n_lines": len(lines),
                        "last_line": last_meaningful_line(txt),
                        "tail": lines[-ATTEMPT_TAIL_LINES:]})
    return out


def console(iid, key=None, tail=600):
    """The container's own console for a still-listed instance, via the reviewed `request_logs` path.

    IMPORTED, NOT RE-IMPLEMENTED (CLAUDE.md §1). `nrv04_vast_launch._vast_instance_logs` already encodes the
    two things that are easy to get wrong here — that the PUT only TRIGGERS collection and returns a URL, and
    that the URL is empty for several seconds afterwards so it must be polled rather than read once.
    """
    from nrv04_vast_launch import _vast_instance_logs
    return _vast_instance_logs(key or os.environ["VAST_API_KEY"], iid, tail=tail)


def diagnose(mode="edge_reps", bucket=None, prefix=None, key=None, want_console=True):
    """The full picture for one mode's units: host spec, S3 phase/commit state, every archived attempt's last
    line, and — for anything still listed — the container's own console.

    Returns the structured record so a caller can commit it; prints the human-readable version, because the
    thing a person actually needs at 3 AM is the two arms' last lines side by side.
    """
    b = bucket or tv.DEFAULT_BUCKET
    p = (prefix or tv.RESULT_PREFIX).rstrip("/")
    key = key or os.environ.get("VAST_API_KEY")
    uids = [tv.build_jobspec(l, s, d, mode=mode).env["UNIT_ID"] for (l, s, d) in tv.units_for(mode)]

    hosts = {"live": {}, "dead": {}}
    try:
        hosts = tv.unit_hosts(uids, key=key)
    except Exception as e:  # noqa: BLE001 — the S3 half of this diagnostic stands on its own
        print(f"[diag] instance list unreadable ({type(e).__name__}: {e}) — S3 evidence only")
    listed = dict(hosts["dead"])
    listed.update(hosts["live"])

    recs = tv.leg_records(b, p)
    doc = {"_what": "why the ternary replicate legs commit nothing, measured from the container's own "
                    "output rather than inferred from exit status (CLAUDE.md §4)",
           "mode": mode, "utc": tv.time.strftime("%Y-%m-%dT%H:%M:%SZ", tv.time.gmtime()), "units": {}}

    for uid in uids:
        arm = arm_of(uid)
        inst = listed.get(uid)
        phase, it, scalar = tv.committed_progress(uid, b, p)
        marker, marker_age, _tail, log_age = tv.phase_and_log(uid, b, p)
        atts = attempt_logs(uid, b, p)
        rec = recs.get(uid) or {}
        u = {"arm": arm, "leg_record_status": rec.get("status"),
             "committed": {"phase": phase, "iteration": it, "scalar": scalar},
             "phase_marker": marker, "phase_marker_age_min": marker_age, "log_age_min": log_age,
             "n_attempts_archived": len(atts),
             "attempts": [{k: a[k] for k in ("key", "utc", "bytes", "n_lines", "last_line")} for a in atts],
             "instance": safe_instance(inst) if inst else None,
             "instance_is_working": bool(inst) and uid in hosts["live"]}

        print("=" * 108)
        print(f"{uid}   arm={arm}")
        if inst:
            print(f"  host {inst.get('id')} machine={inst.get('machine_id')} {inst.get('gpu_name')} "
                  f"actual={inst.get('actual_status')!r} cur={inst.get('cur_state')!r}")
            # ★ THE CAPACITY LINE. If the ternary legs are landing on hosts that cannot hold their system,
            # that is a SPEC problem (`resource_spec` asking for too little RAM/disk) and retries cannot fix
            # it — which is the one candidate mechanism whose remedy is different from all the others.
            print(f"  capacity: cpu_ram={inst.get('cpu_ram')} mem_usage={inst.get('mem_usage')} "
                  f"mem_limit={inst.get('mem_limit')} disk_space={inst.get('disk_space')} "
                  f"disk_util={inst.get('disk_util')} gpu_ram={inst.get('gpu_ram')} "
                  f"cores={inst.get('cpu_cores_effective')}")
            print(f"  status_msg: {str(inst.get('status_msg') or '')[:160]!r}")
        else:
            print("  host: none listed (destroyed, or never rented)")
        print(f"  committed: {phase or 'NOTHING'}/{it}  scalar={scalar}  "
              f"phase_marker={marker!r} ({'%.0f min old' % marker_age if marker_age is not None else 'n/a'})"
              f"  log {'%.1f min old' % log_age if log_age is not None else 'n/a'}")
        print(f"  attempts archived: {len(atts)}")
        for a in atts:
            print(f"    {a['utc']}  {a['bytes']:>8} B  {a['n_lines']:>5} lines  {a['key'].split('/')[-1]}")
            print(f"      LAST: {a['last_line'][:160]}")
        if atts:
            print(f"  --- tail of the newest attempt ({atts[-1]['key'].split('/')[-1]}) ---")
            for ln in atts[-1]["tail"]:
                print(f"    | {ln[:180]}")

        # THE CONSOLE — the only source that carries the last two minutes before the container died, because
        # the S3 sync loop runs on a 120 s timer. Attempted for every LISTED instance, live or exited: Vast
        # keeps serving logs for an instance that has exited but not been destroyed, and that window is
        # exactly the one worth catching.
        if want_console and inst and key:
            try:
                txt = console(inst.get("id"), key=key)
                lines = [ln for ln in txt.splitlines() if ln.strip()]
                u["console_last_line"] = last_meaningful_line(txt)
                u["console_tail"] = lines[-40:]
                print(f"  --- CONTAINER CONSOLE (request_logs, instance {inst.get('id')}) ---")
                for ln in lines[-40:]:
                    print(f"    > {ln[:180]}")
            except Exception as e:  # noqa: BLE001 — a destroyed instance serves no logs; say so, don't crash
                u["console_error"] = f"{type(e).__name__}: {e}"
                print(f"  console unavailable: {type(e).__name__}: {e}")
        doc["units"][uid] = u

    # ---- THE COMPARISON, LAST AND COMPACT. GitHub truncates a job log from the tail, and this is the line
    # anyone reading the run is actually after: what each arm's last words were.
    print("=" * 108)
    print("---- ARM COMPARISON (the diagnosis is the difference between these two blocks) ----")
    for arm in ("ternary", "binary", "solvent"):
        rows = [(u, d) for u, d in doc["units"].items() if d["arm"] == arm]
        if not rows:
            continue
        print(f"  {arm}:")
        for u, d in rows:
            last = (d["attempts"][-1]["last_line"] if d["attempts"] else "(no log at all)")
            print(f"    {u}")
            print(f"      committed={d['committed']['phase']}/{d['committed']['iteration']} "
                  f"attempts={d['n_attempts_archived']} working={d['instance_is_working']}")
            print(f"      last S3 line : {last[:150]}")
            if d.get("console_last_line"):
                print(f"      last CONSOLE : {d['console_last_line'][:150]}")
    print("---- END ARM COMPARISON ----")
    return doc


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", default="edge_reps")
    ap.add_argument("--out", default=None, help="write the structured record here (committed by CI)")
    ap.add_argument("--no-console", action="store_true",
                    help="S3 evidence only — skip the provider round trip")
    a = ap.parse_args(argv)
    doc = diagnose(mode=a.mode, want_console=not a.no_console)
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(doc, fh, indent=2, default=str)
            fh.write("\n")
        print(f"[diag] wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
