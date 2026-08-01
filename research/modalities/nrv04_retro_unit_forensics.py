#!/usr/bin/env python3
"""Read-only forensics for ONE NR-V04 retrospective unit: WHAT KILLED EACH ATTEMPT, from the artifacts.

★★ WHY THIS EXISTS (2026-07-31). `nrv04_vast_launch.retro_attempt_hosts` answers *how many real rentals*
a streak is; `leg_failure_breaker` answers *should we buy another*. Neither answers **what went wrong**, and
until 2026-07-31 nothing could: the lane overwrote `$RESULT_S3/run.log` every 45 s, so each attempt destroyed
the only record of how the last one died. `_RETRO_ATTEMPT_MARKER` now archives the previous attempt's log to
`legs/<unit>/attempt-logs/` — a namespace `count_attempts` deliberately does not count — and this module is
what reads that archive.

It rents nothing, destroys nothing, and writes nothing to S3. Every field it emits is a MEASUREMENT off a
real object (key, size, mtime, body) — never a default, never an inference (CLAUDE.md §4b).

THE THREE FAULTS IT SEPARATES, which is the whole point (a breaker verdict cannot tell them apart):

  * **never-starts**      — a marker exists, no `phase.txt` beyond `env-ready`, no staged input. Host/env.
  * **dies-in-staging**   — phase stops at `staged`/`md-running` with no production frame. Input or build.
  * **resume-and-die**    — production frames were reached and the attempt died before the NEXT checkpoint,
                            so `done_frames` does not advance across attempts. Nothing is banked, the streak
                            anchor cannot move, and the breaker counts it out while the unit is *working*.
                            This is the fault `RETRO_CKPT_EVERY_OVERRIDES` was opened for.

The discriminator between the last two is `frame_progress`: the per-attempt maximum frame index parsed out of
each archived log, and the `done_frames` of every checkpoint object. A unit whose frame ceiling RISES across
attempts is making progress no counter can see; one whose ceiling is pinned at the same number is wedged.

⚠ AN ABSENT LOG IS NOT AN ABSENT FAILURE. The archive only began on 2026-07-31 (commit e060cbfa), so an
attempt that predates it leaves a marker and no log. Those are reported as `log: null` with the reason, and
they are NEVER scored as "died silently" — that would be reading absence as evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

BUCKET = os.environ.get("VAST_CKPT_BUCKET") or "sagemaker-us-east-2-646605541856"
PREFIX = os.environ.get("NRV04_RETRO_RESULT_PREFIX") or "nrv04-retro-results"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nrv04-retro-unit-forensics.json")

#: Default subjects: the unit AMENDMENT 4 §4.5 names as the live dependency, and the sibling replica on the
#: SAME co-fold that landed. The pair is the comparison — §4.2's replicate-asymmetry argument in reverse.
DEFAULT_UNITS = (
    "nrv04retro-retro_noncov_nr4a2-m2-r0",
    "nrv04retro-retro_noncov_nr4a2-m2-r1",
)

#: Lines worth surfacing verbatim from a run.log. Ordered widest-first so a traceback is never hidden by a
#: routine line matching earlier.
_SIGNAL_RE = re.compile(
    r"(Traceback|Error|error|ERROR|Exception|exception|NaN|nan\b|"
    r"CUDA|cuda|out of memory|OOM|Killed|killed|SIGKILL|SIGTERM|"
    r"resume|Resume|RESUME|checkpoint|ckpt|frame|Frame|"
    r"blew_up|minimi|equil|production|prod@|no space|Disk|disk|"
    r"Unable|unable|refus|denied|AccessDenied|NoSuchKey|Timeout|timeout)")

#: `frame <i>/<n>` and `frames <i>/<n>` and `frame=<i>` — the driver's progress prints. Kept permissive on
#: purpose: a ceiling parsed from a slightly different spelling is still a measurement, and a missed one
#: reports as `None` rather than as zero progress.
_FRAME_RE = re.compile(r"frames?[ =_]*(\d+)\s*/\s*(\d+)")


def _client():
    import boto3
    return boto3.client("s3")


def _list(s3, prefix):
    """[(key, size, mtime_iso, mtime_epoch)] under `prefix`, oldest first. Read failure RAISES — a partial
    listing silently read as complete is how an absent reading becomes a reading of absence."""
    out = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=prefix):
        for o in page.get("Contents", []) or []:
            lm = o.get("LastModified")
            out.append((o["Key"], int(o.get("Size") or 0),
                        lm.strftime("%Y-%m-%dT%H:%M:%SZ") if lm else None,
                        lm.timestamp() if lm else None))
    out.sort(key=lambda r: (r[3] or 0.0, r[0]))
    return out


def _get(s3, key, max_bytes=400_000):
    try:
        body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read(max_bytes)
    except Exception as e:  # noqa: BLE001 — unreadable is UNKNOWN and says so
        return None, "%s: %s" % (type(e).__name__, e)
    try:
        return body.decode("utf-8", "replace"), None
    except Exception as e:  # noqa: BLE001
        return None, "decode: %s" % e


def _frame_ceiling(text):
    """(max_i, n) — the highest production frame index this log reached, or (None, None). PURE."""
    best, tot = None, None
    for m in _FRAME_RE.finditer(text or ""):
        i, n = int(m.group(1)), int(m.group(2))
        if best is None or i > best:
            best, tot = i, n
    return best, tot


def _signals(text, keep=40):
    """The lines a human would grep for, de-duplicated, newest-last. PURE."""
    seen, out = set(), []
    for ln in (text or "").splitlines():
        ln = ln.rstrip()
        if not ln or not _SIGNAL_RE.search(ln):
            continue
        k = re.sub(r"\d+", "#", ln)[:200]
        if k in seen:
            continue
        seen.add(k)
        out.append(ln[:400])
    return out[-keep:]


def _classify(phase, frame_max, has_leg, ckpt_frames):
    """PURE: which of the three faults this attempt looks like, or 'unknown' when the evidence is absent.

    ⚠ 'unknown' IS A REAL ANSWER HERE and must never be rendered as one of the three. An attempt whose log
    was never archived cannot be classified, and saying so is the honest output (CLAUDE.md §4b)."""
    if has_leg:
        return "landed", "a conforming leg record exists for this attempt's unit"
    if phase is None and frame_max is None:
        return "unknown", "no archived log and no phase marker — this attempt predates the log archive"
    if frame_max is not None and frame_max > 0:
        banked = "banked %s" % ckpt_frames if ckpt_frames else "banked NOTHING"
        return "resume-and-die", (
            "reached production frame %d and produced no leg record; checkpoints %s. The fault is host "
            "lifetime vs checkpoint interval, not the input." % (frame_max, banked))
    if phase in (None, "", "env-ready"):
        return "never-starts", "the attempt marker is the last thing it wrote — env came up, nothing else did"
    return "dies-in-staging", "phase stopped at %r with no production frame" % phase


def unit_report(s3, unit):
    """Everything measurable about one unit. Every key is an observation; nothing is inferred."""
    rep = {"unit": unit, "bucket": BUCKET, "prefix": PREFIX}

    result_objs = _list(s3, f"{PREFIX}/{unit}/")
    rep["result_objects"] = [{"key": k, "size": s, "mtime": t} for k, s, t, _e in result_objs]

    # ---- leg records: what landed, and is it a PRODUCTION leg or a smoke? -------------------------------
    legs = []
    for k, s, t, _e in result_objs:
        base = k.rsplit("/", 1)[-1]
        if not (base.startswith("leg_") and base.endswith(".json")):
            continue
        body, err = _get(s3, k)
        rec = None
        if body is not None:
            try:
                rec = json.loads(body)
            except Exception as e:  # noqa: BLE001
                err = "json: %s" % e
        entry = {"key": k, "size": s, "mtime": t, "error": err}
        if isinstance(rec, dict):
            entry.update({f: rec.get(f) for f in (
                "panel", "leg_id", "seed", "mode", "prod_ns", "equil_ns", "n_frames", "timed_ns",
                "ns_per_day", "prod_wall_s", "blew_up", "blow_phase", "pe_pre_min_kj", "pe_post_min_kj")})
            # ★ PROVENANCE, NOT PRESENCE (CLAUDE.md §4b): `production_leg_check` is the predicate that
            # refuses a field an ENV could have filled in. Never re-implemented here.
            try:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                import nrv04_retro_panel as _panel
                ok, why = _panel.production_leg_check(rec)
                entry["production_leg_check"] = {"pass": bool(ok), "why": why}
            except Exception as e:  # noqa: BLE001
                entry["production_leg_check"] = {"pass": None, "why": "predicate unavailable: %s" % e}
        legs.append(entry)
    rep["leg_records"] = legs
    rep["has_production_leg"] = any((l.get("production_leg_check") or {}).get("pass") for l in legs)

    # ---- checkpoints: the ONLY object that proves banked production frames ------------------------------
    ckpts = []
    for k, s, t, _e in result_objs:
        base = k.rsplit("/", 1)[-1]
        if not (base.startswith("ckpt_") and base.endswith(".ckpt.json")):
            continue
        body, err = _get(s3, k)
        d = {}
        if body is not None:
            try:
                d = json.loads(body) or {}
            except Exception as e:  # noqa: BLE001
                err = "json: %s" % e
        ckpts.append({"key": k, "size": s, "mtime": t, "error": err,
                      "phase": d.get("phase"), "done_frames": d.get("done_frames"),
                      "frames": d.get("frames"), "seed": d.get("seed")})
    rep["checkpoints"] = ckpts
    rep["banked_frames"] = max([c.get("done_frames") or 0 for c in ckpts] or [0])

    # ---- phase marker + the CURRENT run.log -------------------------------------------------------------
    phase_body, phase_err = _get(s3, f"{PREFIX}/{unit}/phase.txt")
    rep["phase_txt"] = (phase_body or "").strip() or None
    rep["phase_txt_error"] = phase_err
    live_log, live_err = _get(s3, f"{PREFIX}/{unit}/run.log")
    rep["run_log"] = None if live_log is None else {
        "bytes": len(live_log.encode()), "sha256": hashlib.sha256(live_log.encode()).hexdigest()[:16],
        "frame_ceiling": _frame_ceiling(live_log)[0], "frames_total": _frame_ceiling(live_log)[1],
        "tail": live_log.splitlines()[-60:], "signals": _signals(live_log)}
    rep["run_log_error"] = live_err

    # ---- attempt markers: the breaker's own evidence, read for ids not counted for objects --------------
    markers = []
    for k, s, t, _e in _list(s3, f"{PREFIX}/legs/{unit}/attempts/"):
        body, err = _get(s3, k, 4096)
        m = re.search(r"instance=(\S+)", body or "")
        markers.append({"key": k, "size": s, "mtime": t, "error": err,
                        "body": (body or "").strip()[:200],
                        "instance": (m.group(1) if m and m.group(1) not in ("", "unknown") else None)})
    rep["attempt_markers"] = markers
    rep["n_markers"] = len(markers)
    rep["distinct_hosts"] = sorted({m["instance"] for m in markers if m["instance"]})
    rep["n_distinct_hosts"] = len(rep["distinct_hosts"])
    rep["unreadable_markers"] = sum(1 for m in markers if m["instance"] is None)

    # ---- archived per-attempt logs: WHAT KILLED EACH ONE ------------------------------------------------
    # ★ THE BYTE-IDENTICAL TEST. Two logs from DIFFERENT hosts with the same sha256 and the same last line
    #   place the fault between two specific prints — that is how the ternary lane localised its wedge, and
    #   it needs >=2 preserved logs, which is why the archive exists.
    alogs = []
    for k, s, t, _e in _list(s3, f"{PREFIX}/legs/{unit}/attempt-logs/"):
        body, err = _get(s3, k)
        fmax, ftot = _frame_ceiling(body or "")
        alogs.append({
            "key": k, "size": s, "mtime": t, "error": err,
            "sha256": hashlib.sha256((body or "").encode()).hexdigest()[:16] if body is not None else None,
            "n_lines": len((body or "").splitlines()) if body is not None else None,
            "last_line": ((body or "").splitlines() or [None])[-1],
            "frame_ceiling": fmax, "frames_total": ftot,
            "phase_words": sorted({w for w in re.findall(
                r"\b(env-ready|staged|md-running|md-done|uploaded|minimi\w*|equil\w*|production|resume\w*)\b",
                body or "")}),
            "signals": _signals(body or ""),
            "tail": (body or "").splitlines()[-45:],
        })
    rep["attempt_logs"] = alogs
    by_sha = {}
    for a in alogs:
        if a["sha256"]:
            by_sha.setdefault(a["sha256"], []).append(a["key"])
    rep["identical_log_groups"] = {k: v for k, v in by_sha.items() if len(v) > 1}

    # ---- the classification, per attempt where a log exists ---------------------------------------------
    ceilings = [a["frame_ceiling"] for a in alogs if a["frame_ceiling"] is not None]
    rep["frame_ceilings"] = ceilings
    rep["frame_ceiling_rising"] = (len(ceilings) >= 2 and ceilings[-1] > ceilings[0])
    live_ceiling = (rep["run_log"] or {}).get("frame_ceiling")
    rep["fault"], rep["fault_why"] = _classify(
        rep["phase_txt"], max(ceilings + ([live_ceiling] if live_ceiling else []) or [0]) or None,
        rep["has_production_leg"], rep["banked_frames"] or None)
    return rep


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    sel = os.environ.get("RETRO_FORENSIC_UNITS") or (" ".join(argv) if argv else "")
    units = [u.strip() for u in sel.replace(",", " ").split() if u.strip().startswith("nrv04retro-")]
    if not units:
        units = list(DEFAULT_UNITS)
    s3 = _client()
    out = {"_what": "NR-V04 retrospective — per-attempt forensics for one unit and its comparison sibling.",
           "_rule": "CLAUDE.md §4 — the mechanism, from the artifact, before any decision.",
           "bucket": BUCKET, "prefix": PREFIX, "units": {}}
    for u in units:
        try:
            out["units"][u] = unit_report(s3, u)
        except Exception as e:  # noqa: BLE001 — one unreadable unit must not hide the other's evidence
            out["units"][u] = {"unit": u, "error": "%s: %s" % (type(e).__name__, e)}
    print(json.dumps(out, indent=1, default=str), flush=True)
    try:
        with open(OUT_JSON, "w") as fh:
            json.dump(out, fh, indent=1, default=str)
        print(f"[retro-forensics] wrote {OUT_JSON}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[retro-forensics] could not write artifact: {e}", flush=True)
    return out


if __name__ == "__main__":
    main()
