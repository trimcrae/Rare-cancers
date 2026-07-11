#!/usr/bin/env python3
"""
Parse a SageMaker CloudWatch / GitHub-Actions log tail into a STRUCTURED progress record, compute an ETA from
two consecutive samples, and flag a HANG when the newest progress marker is stale. Fulfils the standing ask
"have some way of monitoring the iteration progress so we can catch if it hangs and get ETAs as we go".

Two job families are recognised from their stdout markers (no external state needed — the log is the source):

  ABFE  (nr4a3_abfe.run_shard on a spot g5): each independent λ-window prints ONE line when it starts,
        `[abfe] nan-guard v2 active (window N, seed S)`. Windows are the progress unit; the reduce prints
        `[abfe] DG_BIND ...` / `SHARD_DONE` at the end. Per-iteration progress lives in the per-window jsonl
        (checkpointed to S3), not stdout, so window-granularity is the stdout-observable resolution.
        CAVEAT (verified 2026-07-11): one λ-window's MD can legitimately take 30-100 min on the OpenCL
        fallback (the g5 CUDA build hits CUDA_ERROR_UNSUPPORTED_PTX_VERSION), so a stale window-start marker
        is NOT a reliable hang signal — the AUTHORITATIVE ABFE progress/hang signal is the per-window jsonl
        checkpoint DEPTH via abfe-progress-aws.yml (iterations advancing = alive). Hence ABFE_HANG_MIN below is
        deliberately large; use abfe-progress for true intra-window ETA. Boltz per-seed markers (~3.5 min each)
        ARE reliable for marker-age hang detection.

  BOLTZ (nr4a3_ternary.py / nrv04_ternary.py co-fold): each ensemble member prints
        `running: boltz predict <stem>.yaml ... --seed K`, then `Predicting DataLoader 0: 100%|...| 1/1`
        when that member finishes. The (system, seed) pair is the progress unit.

Design: parsing is PURE and unit-tested against captured log lines; the fetch (dispatch tail-cloudwatch, pull
its GH-job log) happens upstream and the text is piped in. Given a prior sample (`--prev sample.json`) it
prints minutes/unit, an ETA to the expected total, and HANG=<bool> (last-marker age > --hang-min). Times are
reported in US-Eastern 12-hour AM/PM per the repo standing rule; timestamps in the log are UTC (SageMaker) and
converted on display only.

CLI:
  python job_progress_monitor.py --log tail.txt [--kind auto|abfe|boltz]
       [--total-units N] [--prev prev.json] [--hang-min 25] [--now-iso 2026-07-11T15:00:00Z] [--emit next.json]
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone

# Eastern is UTC-4 (EDT) for the summer months this project runs in; the repo standing rule is ET 12-hour AM/PM.
_ET = timezone(timedelta(hours=-4))

# Leading ISO-8601 timestamp(s), e.g. 2026-07-11T14:34:25.7301250Z. A line may carry TWO leading timestamps:
# when a tail is fetched back through the GitHub-Actions log API, GitHub prepends its own ingest time in FRONT
# of the real CloudWatch event time that tail_cloudwatch.py prepended. The authoritative event time is always
# the LAST of the run of leading timestamps (the one immediately before the message), so match that.
_TS = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.\d+)?Z")
_LEADING_TS = re.compile(r"^\s*((?:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z\s+)+)")
# ABFE per-window start marker (the one reliable per-window stdout line).
_ABFE_WIN = re.compile(r"nan-guard v2 active \(window\s+(\d+)")
_ABFE_DONE = re.compile(r"\bSHARD_DONE\b|\bDG_BIND\b")
_ABFE_ANY = re.compile(r"\[abfe\]")
# BOLTZ ensemble-member start: `running: boltz predict .../<stem>.yaml ... --seed K`
_BOLTZ_RUN = re.compile(r"boltz predict\s+\S*?/?([A-Za-z0-9_\-]+)\.yaml.*?--seed\s+(\d+)")
_BOLTZ_ANY = re.compile(r"boltz predict|Predicting DataLoader")

# Kind-aware default hang thresholds (min). ABFE windows can legitimately run ~100 min on the OpenCL fallback,
# so only flag a hang when a window-start marker is stale for far longer than any single window should take;
# for true ABFE progress use abfe-progress (checkpoint depth). Boltz members are ~3.5 min so 25 min is safe.
DEFAULT_HANG_MIN = {"abfe": 150.0, "boltz": 25.0}


def parse_ts(line):
    """The REAL event UTC timestamp of a log line as an aware datetime, or None. Uses the LAST of the leading
    run of timestamps (see _LEADING_TS) so a GitHub-API-fetched line's own ingest prefix doesn't mask the true
    CloudWatch event time; falls back to the first timestamp anywhere if there is no clean leading run."""
    lead = _LEADING_TS.match(line)
    if lead:
        stamps = _TS.findall(lead.group(1))
        if stamps:
            return datetime.strptime(stamps[-1], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    m = _TS.search(line)
    if not m:
        return None
    return datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


def detect_kind(text):
    if _ABFE_ANY.search(text):
        return "abfe"
    if _BOLTZ_ANY.search(text):
        return "boltz"
    return "unknown"


def parse_abfe(text):
    """Return the newest ABFE progress state: highest window index reached + its line timestamp, and whether the
    shard's reduce/DG_BIND has printed (i.e. the leg is essentially done)."""
    last_win, last_ts, done, done_ts = None, None, False, None
    for line in text.splitlines():
        m = _ABFE_WIN.search(line)
        if m:
            w = int(m.group(1))
            if last_win is None or w >= last_win:
                last_win, last_ts = w, parse_ts(line) or last_ts
        if _ABFE_DONE.search(line):
            done, done_ts = True, parse_ts(line) or done_ts
    return {"kind": "abfe", "unit": None if last_win is None else "window %d" % last_win,
            "index": last_win, "last_ts": _iso(last_ts), "done": done, "done_ts": _iso(done_ts)}


def parse_boltz(text):
    """Return the newest Boltz ensemble member: the last (system, seed) whose `boltz predict` line appeared, a
    running count of DISTINCT completed members (a `Predicting DataLoader 0: 100%` line = one member done), and
    the last activity timestamp. System is the yaml stem (e.g. 'nr4a1-nrv04-ternary', 'control-vhl-vh032')."""
    last_sys, last_seed, last_ts = None, None, None
    started = []          # ordered (system, seed) starts
    completed = 0
    for line in text.splitlines():
        m = _BOLTZ_RUN.search(line)
        if m:
            last_sys, last_seed = m.group(1), int(m.group(2))
            started.append((last_sys, last_seed))
            last_ts = parse_ts(line) or last_ts
        if "Predicting DataLoader 0: 100%" in line and "1/1" in line:
            completed += 1
            last_ts = parse_ts(line) or last_ts
    unit = None if last_sys is None else "%s seed %s" % (last_sys, last_seed)
    return {"kind": "boltz", "unit": unit, "index": completed, "last_ts": _iso(last_ts),
            "started": len(started), "completed": completed,
            "done": False, "done_ts": None}


def _iso(dt):
    return None if dt is None else dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _et(iso):
    """UTC iso string → 'H:MM AM/PM ET' (repo standing rule: always Eastern, 12-hour)."""
    if not iso:
        return "—"
    dt = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(_ET)
    return dt.strftime("%-I:%M %p ET")


def analyse(cur, prev=None, total_units=None, now_iso=None, hang_min=25.0):
    """Combine the current sample with a prior one → rate (min/unit), ETA, and a hang verdict. `now_iso` is the
    reference 'now' (defaults to the current sample's last_ts; pass the real wall clock to age a stalled job)."""
    out = dict(cur)
    now = datetime.strptime(now_iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) if now_iso else None
    last = datetime.strptime(cur["last_ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) \
        if cur.get("last_ts") else None
    # Age of the newest progress marker → hang flag.
    if now and last:
        age = (now - last).total_seconds() / 60.0
        out["marker_age_min"] = round(age, 1)
        out["hang"] = (not cur.get("done")) and age > hang_min
        out["now_et"] = _et(now_iso)
    else:
        out["marker_age_min"], out["hang"] = None, None
    out["last_et"] = _et(cur.get("last_ts"))
    # Rate + ETA from two samples of the same job (needs an advancing index + elapsed wall time).
    if prev and prev.get("index") is not None and cur.get("index") is not None \
            and cur.get("last_ts") and prev.get("last_ts"):
        d_units = cur["index"] - prev["index"]
        t0 = datetime.strptime(prev["last_ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        d_min = (last - t0).total_seconds() / 60.0
        out["sample_gap_min"] = round(d_min, 1)
        if d_units > 0 and d_min > 0:
            per = d_min / d_units
            out["min_per_unit"] = round(per, 1)
            if total_units is not None:
                remaining = max(total_units - cur["index"] - 1, 0)  # index is 0-based "current" unit
                out["units_remaining"] = remaining
                eta_min = remaining * per
                out["eta_min"] = round(eta_min, 1)
                if now:
                    out["eta_et"] = _et(_iso(now + timedelta(minutes=eta_min)))
        elif d_units == 0:
            out["min_per_unit"] = None   # no advance between samples — hang is caught by marker_age below
    return out


def render(a, total_units=None):
    k = a["kind"]
    tot = ("/%d" % total_units) if total_units else ""
    idx = a.get("index")
    idxs = "?" if idx is None else str(idx)
    line = "[%s] at %s%s  (%s, last activity %s" % (k, idxs, tot, a.get("unit") or "—", a.get("last_et") or "—")
    if a.get("marker_age_min") is not None:
        line += ", %.0f min ago" % a["marker_age_min"]
    line += ")"
    if a.get("min_per_unit"):
        line += "  |  %.1f min/unit" % a["min_per_unit"]
    if a.get("eta_min") is not None:
        line += "  |  ETA ~%.0f min → %s" % (a["eta_min"], a.get("eta_et") or "?")
    if a.get("done"):
        line += "  |  DONE"
    elif a.get("hang"):
        line += "  |  ⚠ HANG SUSPECTED (marker stale)"
    return line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", help="path to a captured log tail (default: stdin)")
    ap.add_argument("--kind", default="auto", choices=["auto", "abfe", "boltz"])
    ap.add_argument("--total-units", type=int, default=None, help="expected total units (16 windows / N members)")
    ap.add_argument("--prev", help="prior sample JSON (from a previous --emit) → rate + ETA")
    ap.add_argument("--hang-min", type=float, default=None,
                    help="mark a hang if the newest marker is older than this (min); default is kind-aware "
                         "(abfe=150, boltz=25) since ABFE windows run far longer than Boltz members")
    ap.add_argument("--now-iso", default=None, help="reference 'now' UTC iso (default = current sample's last activity)")
    ap.add_argument("--emit", help="write the current sample JSON here for the next cycle's --prev")
    args = ap.parse_args()

    text = open(args.log).read() if args.log else sys.stdin.read()
    kind = args.kind if args.kind != "auto" else detect_kind(text)
    if kind == "abfe":
        cur = parse_abfe(text)
    elif kind == "boltz":
        cur = parse_boltz(text)
    else:
        print("unknown job kind (no [abfe] or boltz markers in log)", file=sys.stderr)
        sys.exit(2)

    hang_min = args.hang_min if args.hang_min is not None else DEFAULT_HANG_MIN.get(kind, 25.0)
    prev = json.load(open(args.prev)) if args.prev else None
    a = analyse(cur, prev=prev, total_units=args.total_units, now_iso=args.now_iso, hang_min=hang_min)
    print(render(a, total_units=args.total_units))
    print(json.dumps(a))
    if args.emit:
        json.dump(cur, open(args.emit, "w"), indent=2)


if __name__ == "__main__":
    main()
