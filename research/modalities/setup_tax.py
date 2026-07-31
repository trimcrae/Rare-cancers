#!/usr/bin/env python3
"""THE SETUP TAX — how much of each rental is bought and NOT spent on science, split by line item. $0.

★★ THE COLD START IS NOT THE PROBLEM, AND I SAID IT WAS — MEASURED AND RETRACTED (2026-07-31, 6:47 PM ET).

I reported that "legs are not failing because MD is slow; they die during the ~28 min cold start, before MD
begins." **The mechanism in that sentence is wrong.** Reading `phase.txt`'s own timestamp against the log's
`[tvast] <utc> start` on all four live legs:

    container start -> md-running:  0.3, 0.4, 0.5, 0.6 min   (median 0.4 min)

MD begins within ~30 SECONDS of the container starting, because all three caches are hitting (23 of 27
attempts). The `ternary-4fs-vast-findings.md` budget predicted exactly this — "~15 min of that is cached and
will not repeat" — and the cached line items (staging ~8 min, pre-equilibration 456 s, and the ~460 s
solvate+parameterise, which is RESTORED not rebuilt) really have gone to nearly zero.

WHAT THE "~28 min" ACTUALLY IS: **time to the first COMMIT**, which is dominated by one checkpoint interval
of MD, not by setup. 64 warmup iterations x the measured rate:

    leg          staging   s/iter   64 x s/iter   = first commit
    nr4a3_r0       0.6 m     33.5      35.7 m         36.4 m
    nr4a3_r1       0.5 m     31.1      33.1 m         33.6 m
    nr4a1_r0       0.3 m     18.3      19.5 m         19.8 m
    nr4a1_r1       0.4 m     17.8      19.0 m         19.4 m

(plus the ~2.8 min image pull, which happens BEFORE the log's first line and is not in these figures.)

⚠ WHY THE CORRECTION CHANGES THE RECOMMENDATION. A staging problem would be fixed by faster staging or a
bigger host; this is not one. The lever is the CHECKPOINT INTERVAL — halving it halves time-to-first-commit
directly — and that is a change for NEW legs only, because the interval is fixed when the .nc is created
(`rbfe_spot_checkpoint.effective_interval`; `tests/test_ckpt_cadence_is_new_legs_only.py`). It also explains
why measure-on-arrival would have condemned nobody: the MD rate is fine, the INTERVAL is long.

⚠ NOT MEASURED, AND NOT CLAIMED: minimisation and the setup RESTORE both sit inside `md-running`, before the
first `[timing]` line, so the figures above bound them together rather than separating them. The `[spot-driver]
restore: <label> took Ns` instrumentation and the timestamped phase marks will separate them on the next
re-placement; until one lands, "0.4 min of staging" is a statement about the SHELL phases only.


★★ THE QUESTION (trimcrae, 2026-07-31): *"What do we have to do to get back to the good throughput we had in
prior sessions?"* The comparison that framed it kills the obvious answer. The step 1 fan-out churned HARDER
than 5a-KS — 208 rentals for 19 units, median 7 per unit, max 37 — and still landed 18 of 19. So churn is not
the problem. What differs is how much of each rental is PRODUCTIVE:

  * fan-out `realised_rentals`: median 1.62 h per rental, 9 % under 0.5 h.
  * 5a-KS today: median session <= 1.00 h (an UPPER bound — it is measured rental-to-rental, so it includes
    the hostless gap), 25 % under 0.5 h against a ~28 min time-to-first-commit.

A rental shorter than time-to-first-commit buys NOTHING: it bills and commits nothing. So the tax is not a
tidiness complaint, it is the difference between a session that banks progress and one that does not.

★ WHAT THIS MEASURES, AND WHY IT CAN BE MEASURED AT ALL WITHOUT TIMESTAMPS IN THE LOG. `run.log` lines are
bare `print`s with no clock. But two other things DO carry wall-clock:
  1. the S3 **phase markers** the onstart writes (`mark preequil`, `mark md-running`, `mark md-done`) — their
     `LastModified` is a real boundary, and they survive the host;
  2. the **self-timed** lines the code already prints: `SETUP done in %.0fs`, and (since 2026-07-31)
     `[spot-driver] restore: <label> took %.1fs`.
Together those split a rental into: container start -> stage -> pre-equil -> MD start -> setup restore/build
-> first commit.

★ AND THE CACHE VERDICT, WHICH WAS PREVIOUSLY UNOBSERVABLE FROM ANY COMMITTED ARTIFACT. Three caches sit in
this path and each prints its own HIT/MISS, but only into a log nobody parses:
  * the STAGE cache      `[tvast] stage cache HIT|MISS`
  * the PRE-EQUIL cache  `[tvast] pre-equil cache HIT|MISS`
  * the SETUP cache      `[spot-safe] SETUP RESTORED from cache …` | `SETUP begin …` | `SETUP CACHE MISSING`
A cache whose effectiveness is unobservable is one we cannot tell from an absent one — and the fan-out has NO
setup cache at all and still beat us, so "we have a cache" was never evidence that we were paying less.

⛔ $0 and READ-ONLY: S3 LIST + GET of logs and markers. Rents nothing, changes nothing, decides nothing.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ternary_vast_launch as tv  # noqa: E402

# One entry per thing a run.log says about a cache. `hit` is tri-state on purpose: True / False / None, where
# None means THE LINE WAS NEVER PRINTED — which is a different finding from a miss and must not be folded
# into one (CLAUDE.md §4: an absent reading is not a reading of absence).
CACHE_MARKERS = [
    ("stage", re.compile(r"\[tvast\] stage cache (HIT|MISS)")),
    ("preequil", re.compile(r"\[tvast\] pre-equil cache (HIT|MISS)")),
]
SETUP_RESTORED = re.compile(r"\[spot-safe\] SETUP RESTORED from cache (\S+)")
SETUP_BEGIN = re.compile(r"\[spot-safe\] SETUP begin")
SETUP_DONE = re.compile(r"\[spot-safe\] SETUP done in (\d+(?:\.\d+)?)s")
SETUP_MISSING = re.compile(r"\[spot-safe\] SETUP CACHE MISSING at (\S+)")
SETUP_RESTORE_FAILED = re.compile(r"\[spot-safe\] setup-cache restore failed")
COMMIT_COST = re.compile(r"\[barrier\] commit (\S+)@(\d+) persisted ([\d.]+) MiB in ([\d.]+)s")
RESTORE_TOOK = re.compile(r"\[spot-driver\] restore: (\S+) took (\d+(?:\.\d+)?)s")
RESTORE_LIST = re.compile(r"\[restore\] (\S+): list_committed returned (\d+) generation\(s\) in "
                          r"(\d+(?:\.\d+)?)s")
RESTORE_FETCH = re.compile(r"\[restore\] \S+ iter \d+ gen \S+ fetched (\d+) B in (\d+(?:\.\d+)?)s")
FIRST_COMMIT = re.compile(r"\[(?:barrier|spot-safe)\].*committed checkpoint at iteration (\d+)")
ITER_RATE = re.compile(r"\[timing\].*?(\d+(?:\.\d+)?)\s*s/iter")
# ★★ THE COLD-START SPLIT (2026-07-31). `mark()` used to write its timestamp ONLY to `phase.txt`, which it
# OVERWRITES — so S3 held the current phase and the history was destroyed at every transition, and the run.log
# carried exactly two clocks (`start`, `EXIT`). The ~28 min cold start could be measured as a TOTAL and never
# split. It now echoes `[tvast] <utc> phase=<name>` into the log, so these line items record themselves:
#     start -> staging     container boot + onstart preamble
#     staging -> preequil  STAGE download (or rebuild on a miss)
#     preequil -> md-running   PRE-EQUILIBRATION
#     md-running -> first [timing]   run_ternary_leg + setup restore/build + minimise + warmup to first rate
# Why it is the most expensive unknown on this lane: median session ~1.00 h, so a cold start of tens of
# minutes is a large fraction of every rental, and any session shorter than it banks NOTHING (25 % of
# today's). Measure-on-arrival showed MD itself is fine, so this is the constraint.
#
# ⚠ THE "~28 min" IS INHERITED, NOT MEASURED HERE. Its one home is `ternary-4fs-vast-findings.md`'s cold-start
# budget: a MEASURED ~25 min total (2.8 min image pull, ~8 min staging, 456 s pre-equil, ~6 min setup) of
# which **~15 min is cached and will not repeat** — and the cache tally below says the caches ARE hitting on
# 23 of 27 attempts. So the expected warm-cache cold start is nearer ~10 min. Nobody has measured which the
# lane actually pays; that is what `timeline` exists to settle.
PHASE_MARK = re.compile(r"\[tvast\] (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) phase=(\S+)")
START_TS = re.compile(r"\[tvast\] (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) start ")
EXIT_TS = re.compile(r"\[tvast\] (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) EXIT ")


def parse_log(text):
    """Every anchor a single attempt's run.log carries. PURE."""
    out = {"caches": {}, "setup_seconds": None, "setup_built": False, "setup_restored_from": None,
           "setup_cache_missing": None, "restore_seconds": {}, "restore_list": [], "restore_fetch": [],
           "first_commit_iteration": None, "s_per_iter": None, "n_lines": len(text.splitlines())}
    for name, rx in CACHE_MARKERS:
        m = rx.search(text)
        out["caches"][name] = (m.group(1) == "HIT") if m else None
    m = SETUP_RESTORED.search(text)
    if m:
        out["caches"]["setup"] = True
        out["setup_restored_from"] = m.group(1)
    elif SETUP_MISSING.search(text):
        out["caches"]["setup"] = False
        out["setup_cache_missing"] = SETUP_MISSING.search(text).group(1)
    elif SETUP_BEGIN.search(text):
        out["caches"]["setup"] = False
        out["setup_built"] = True
    else:
        out["caches"]["setup"] = None
    if SETUP_RESTORE_FAILED.search(text):
        out["setup_restore_failed"] = True
    m = SETUP_DONE.search(text)
    if m:
        out["setup_seconds"] = float(m.group(1))
    for m in RESTORE_TOOK.finditer(text):
        out["restore_seconds"][m.group(1)] = float(m.group(2))
    for m in RESTORE_LIST.finditer(text):
        out["restore_list"].append({"phase": m.group(1), "n_gen": int(m.group(2)), "seconds": float(m.group(3))})
    for m in RESTORE_FETCH.finditer(text):
        out["restore_fetch"].append({"bytes": int(m.group(1)), "seconds": float(m.group(2))})
    m = FIRST_COMMIT.search(text)
    if m:
        out["first_commit_iteration"] = int(m.group(1))
    rates = [float(x) for x in ITER_RATE.findall(text)]
    if rates:
        out["s_per_iter"] = round(st.median(rates), 2)
    out["timeline"] = timeline(text)
    out["commits"] = [{"phase": m.group(1), "iteration": int(m.group(2)),
                       "mib": float(m.group(3)), "seconds": float(m.group(4))}
                      for m in COMMIT_COST.finditer(text or "")]
    return out


def timeline(text):
    """[(phase, utc)] plus the derived per-phase seconds, from the log's OWN stamps. PURE.

    Returns `{"marks": [...], "spans": {from->to: seconds}, "complete": bool}`. `complete` is False for any
    attempt logged before the phase marks were timestamped (everything up to 2026-07-31) — those legs cannot
    be split retroactively and must not be silently reported as having a zero-length phase."""
    import datetime as _dt

    def _p(t):
        return _dt.datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")

    marks = []
    m = START_TS.search(text or "")
    if m:
        marks.append(("container-start", m.group(1)))
    marks += [(g2, g1) for g1, g2 in PHASE_MARK.findall(text or "")]
    m = EXIT_TS.search(text or "")
    if m:
        marks.append(("exit", m.group(1)))
    # de-duplicate consecutive repeats (a phase re-marked on a container restart) while keeping order
    seen, ordered = set(), []
    for name, ts in marks:
        if (name, ts) in seen:
            continue
        seen.add((name, ts))
        ordered.append((name, ts))
    spans = {}
    for (n1, t1), (n2, t2) in zip(ordered, ordered[1:]):
        try:
            spans["%s->%s" % (n1, n2)] = (_p(t2) - _p(t1)).total_seconds()
        except ValueError:
            continue
    return {"marks": ordered, "spans": spans,
            "complete": len([n for n, _ in ordered if n not in ("container-start", "exit")]) >= 2}


def verdict(parsed):
    """One sentence a person can act on. PURE.

    The THREE-way split is the point. `MISS` says the cache is configured and cold — pre-bake it. `ABSENT`
    says the line was never printed, i.e. we cannot tell, and that is a reporting defect rather than a cost.
    Treating those alike is how a cache nobody could observe went un-examined for weeks."""
    c = parsed["caches"]
    bits = []
    for k in ("stage", "preequil", "setup"):
        v = c.get(k)
        bits.append("%s=%s" % (k, "HIT" if v else ("MISS" if v is False else "ABSENT(unobservable)")))
    if parsed.get("setup_cache_missing"):
        bits.append("SETUP CACHE MISSING -> the leg FAILS FAST rather than rebuilding on the GPU")
    if parsed.get("setup_built"):
        bits.append("rebuilt the hybrid system ON THE RENTED GPU (%ss)" % parsed.get("setup_seconds"))
    return " · ".join(bits)


# =============================================================================================================
# S3 side — logs and the phase markers that carry the only wall-clock in the system
# =============================================================================================================
def attempt_texts(uid, bucket, prefix, s3, limit=6):
    """[(key, last_modified, text)] for the newest `limit` attempts of this unit, oldest first."""
    keys = []
    pfx = f"{prefix}/legs/{uid}/attempts/"
    try:
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=pfx):
            for o in page.get("Contents") or []:
                if o["Key"].endswith(".log"):
                    keys.append((o["Key"], o["LastModified"]))
    except Exception:  # noqa: BLE001
        pass
    keys.sort(key=lambda t: t[1])
    keys = keys[-limit:]
    keys.append((f"{prefix}/legs/{uid}/run.log", None))
    out = []
    for k, lm in keys:
        try:
            body = s3.get_object(Bucket=bucket, Key=k)
            out.append((k, lm or body["LastModified"], body["Body"].read().decode("utf-8", "replace")))
        except Exception:  # noqa: BLE001
            continue
    return out


def marker_times(uid, bucket, prefix, s3):
    """{marker: LastModified} for the onstart's phase markers. These are the ONLY wall-clock boundaries that
    survive the host, which is why the split is built on them rather than on log line order."""
    out = {}
    try:
        for page in s3.get_paginator("list_objects_v2").paginate(
                Bucket=bucket, Prefix=f"{prefix}/legs/{uid}/"):
            for o in page.get("Contents") or []:
                base = o["Key"].rsplit("/", 1)[-1]
                if base.startswith("mark.") or base.startswith("phase"):
                    out[base] = o["LastModified"]
    except Exception:  # noqa: BLE001
        pass
    return out


def live_cold_start(uid, bucket, prefix, s3):
    """(seconds, detail) from container start to the CURRENT phase, for the attempt running RIGHT NOW.

    ★ WHY THIS EXISTS WHEN `timeline` ALREADY DOES THE SPLIT (2026-07-31). `timeline` reads the phase marks
    the log now carries — but only attempts started AFTER those marks were timestamped have them, so the
    headline question ("is this lane's cold start ~10 min or ~28?") would have to wait for a re-placement.
    It does not: `mark()` has ALWAYS written `<phase> <utc>` into `phase.txt`, and the log has ALWAYS carried
    `[tvast] <utc> start`. The history was destroyed at each transition, but the CURRENT phase's start time
    survives — so for a leg that has reached `md-running`, the difference is its whole cold start, measured,
    on the attempt that is billing now.

    Returns (None, why) when either clock is missing — never a zero."""
    import datetime as _dt
    base = f"{prefix}/legs/{uid}"
    try:
        ph = s3.get_object(Bucket=bucket, Key=f"{base}/phase.txt")["Body"].read().decode(errors="replace")
        phase, _, pts = ph.strip().partition(" ")
    except Exception as e:  # noqa: BLE001
        return None, f"no phase.txt ({type(e).__name__})"
    try:
        log = s3.get_object(Bucket=bucket, Key=f"{base}/run.log")["Body"].read().decode(errors="replace")
    except Exception as e:  # noqa: BLE001
        return None, f"no run.log ({type(e).__name__})"
    m = START_TS.search(log)
    if not m or not pts.strip():
        return None, "start or phase timestamp absent"
    try:
        t0 = _dt.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ")
        t1 = _dt.datetime.strptime(pts.strip(), "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None, "unparseable timestamp"
    return (t1 - t0).total_seconds(), f"container-start -> {phase}"


def commit_object_census(uid, bucket, prefix, s3, max_keys=4000):
    """(bytes_per_commit_median, n_generations, detail) from the REAL committed objects. $0, LIST only.

    ★ WHY MEASURED RATHER THAN THE INLINE ESTIMATE. `MODES`'s comment prices a checkpoint at "an ~25 MB
    .nc/.chk pair" and nothing has ever checked it against S3. Halving the warmup interval 64 -> 32 doubles
    how often that pair is written, so the trade turns on the real figure — and on the WALL TIME, which the
    bytes alone do not give (see `commit_cost`, which the driver now self-times).
    """
    import collections
    base = tv.commit_prefix(bucket, uid, prefix)
    key = base.split("://", 1)[-1].split("/", 1)[-1].rstrip("/") if "://" in base else base.rstrip("/")
    per_gen = collections.defaultdict(int)
    try:
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=key + "/"):
            for o in page.get("Contents") or []:
                k = o["Key"]
                if k.endswith("COMMITTED.json"):
                    continue
                per_gen["/".join(k.split("/")[:-1])] += int(o.get("Size") or 0)
    except Exception as e:  # noqa: BLE001
        return None, 0, f"commit store unreadable ({type(e).__name__}: {e})"
    if not per_gen:
        return None, 0, f"no committed generations under {key}"
    vals = sorted(per_gen.values())
    # ⚠ IS THE PAYLOAD FLAT OR GROWING? An openmmtools .nc accumulates the trajectory, so a later commit may
    # re-upload far more than an early one — and that decides whether "MiB per commit" is a constant or a
    # curve. Reported as (first, last) by ITERATION, not by size, so the growth is visible.
    by_iter = sorted(((int(k.split("/iter-")[1].split("/")[0]), v)
                      for k in per_gen for v in [per_gen[k]] if "/iter-" in k))
    growth = None
    if len(by_iter) >= 2:
        growth = {"first_iter": by_iter[0][0], "first_mib": round(by_iter[0][1] / 1048576.0, 1),
                  "last_iter": by_iter[-1][0], "last_mib": round(by_iter[-1][1] / 1048576.0, 1)}
    return st.median(vals), len(vals), {"n": len(vals), "prefix": key, "growth": growth,
                                        "min_mib": round(vals[0] / 1048576.0, 1),
                                        "max_mib": round(vals[-1] / 1048576.0, 1)}


def measure(mode="5aks", bucket=None, prefix=None, limit=6):
    b = bucket or tv.DEFAULT_BUCKET
    p = (prefix or tv.RESULT_PREFIX).rstrip("/")
    s3 = tv._s3()
    uids = [tv.build_jobspec(l, s, d, mode=mode).env["UNIT_ID"] for (l, s, d) in tv.units_for(mode)]
    doc = {"_what": __doc__.split("\n")[0], "mode": mode,
           "utc": tv.time.strftime("%Y-%m-%dT%H:%M:%SZ", tv.time.gmtime()), "units": {}}
    setup_s, restore_s = [], []
    for uid in uids:
        rows = []
        for key, lm, text in attempt_texts(uid, b, p, s3, limit=limit):
            pr = parse_log(text)
            pr.update({"attempt": key.rsplit("/", 1)[-1], "utc": str(lm), "bytes": len(text),
                       "verdict": verdict(pr)})
            if pr["setup_seconds"]:
                setup_s.append(pr["setup_seconds"])
            for v in pr["restore_seconds"].values():
                restore_s.append(v)
            rows.append(pr)
        _cs, _cswhy = live_cold_start(uid, b, p, s3)
        _cb, _cn, _cwhy = commit_object_census(uid, b, p, s3)
        doc["units"][uid] = {"attempts": rows,
                             "live_cold_start_s": _cs, "live_cold_start_span": _cswhy,
                             "commit_bytes_median": _cb, "n_generations": _cn,
                             "commit_store": _cwhy,
                             "markers": {k: str(v) for k, v in marker_times(uid, b, p, s3).items()}}
    # THE LINE-ITEM SPLIT, medianed across every attempt that recorded one. Attempts predating the
    # timestamped marks contribute NOTHING rather than a zero — an unmeasured phase is not a fast one.
    spans = {}
    for u in doc["units"].values():
        for a in u["attempts"]:
            tl = a.get("timeline") or {}
            if not tl.get("complete"):
                continue
            for k, v in (tl.get("spans") or {}).items():
                spans.setdefault(k, []).append(v)
    doc["cold_start_split"] = {
        "n_attempts_with_a_split": len(set(
            id(a) for u in doc["units"].values() for a in u["attempts"]
            if (a.get("timeline") or {}).get("complete"))),
        "median_seconds": {k: round(st.median(v), 1) for k, v in sorted(spans.items())},
        "n_observations": {k: len(v) for k, v in sorted(spans.items())},
    }
    _cm = [c for u in doc["units"].values() for a in u["attempts"] for c in (a.get("commits") or [])]
    doc["commit_cost"] = {
        "n_observed": len(_cm),
        "median_mib": (round(st.median([c["mib"] for c in _cm]), 1) if _cm else None),
        "median_seconds": (round(st.median([c["seconds"] for c in _cm]), 1) if _cm else None),
        "_reading": ("the PAUSE a checkpoint costs. Halving the warmup interval 64 -> 32 doubles how often "
                     "this is paid, so the interval change is only worth taking while this is small against "
                     "interval x s/iter (the MD between commits)."),
    }
    doc["totals"] = {
        "n_attempts": sum(len(u["attempts"]) for u in doc["units"].values()),
        "setup_build_seconds_median": (round(st.median(setup_s), 1) if setup_s else None),
        "n_setup_builds": len(setup_s),
        "restore_seconds_median": (round(st.median(restore_s), 1) if restore_s else None),
    }
    # The cache tally is the headline: how many attempts actually skipped work, versus how many we simply
    # cannot say anything about.
    tally = {}
    for u in doc["units"].values():
        for a in u["attempts"]:
            for k, v in a["caches"].items():
                d = tally.setdefault(k, {"HIT": 0, "MISS": 0, "ABSENT": 0})
                d["HIT" if v else ("MISS" if v is False else "ABSENT")] += 1
    doc["cache_tally"] = tally
    return doc


def render(doc):
    L = ["=" * 104,
         "SETUP TAX — %s  (read-only, $0)   %s" % (doc["mode"], doc["utc"]),
         "=" * 104,
         "CACHE TALLY across %d attempt(s) — ABSENT means the line was never printed, which is NOT a miss:"
         % doc["totals"]["n_attempts"]]
    for k, d in sorted((doc.get("cache_tally") or {}).items()):
        L.append("   %-10s HIT %-4d MISS %-4d ABSENT %-4d" % (k, d["HIT"], d["MISS"], d["ABSENT"]))
    live = [(u, d["live_cold_start_s"], d.get("live_cold_start_span"))
            for u, d in doc["units"].items() if d.get("live_cold_start_s")]
    if live:
        L.append("")
        L.append("LIVE COLD START (container start -> current phase, on the attempt billing NOW):")
        for u, v, span in sorted(live, key=lambda t: -(t[1] or 0)):
            L.append("   %-52s %6.1f min   %s" % (u.split("__")[-1][:52], v / 60.0, span))
        L.append("   median %.1f min over %d leg(s)" % (st.median([v for _, v, _ in live]) / 60.0, len(live)))
    sizes = [(u, d["commit_bytes_median"], d.get("n_generations"))
             for u, d in doc["units"].items() if d.get("commit_bytes_median")]
    if sizes:
        L.append("")
        L.append("COMMITTED CHECKPOINT SIZE (measured from the real S3 objects):")
        for u, v, n in sorted(sizes, key=lambda t: -(t[1] or 0)):
            L.append("   %-52s %7.1f MiB/commit  (%d generations)"
                     % (u.split("__")[-1][:52], v / 1048576.0, n))
        L.append("   median %.1f MiB per commit"
                 % (st.median([v for _, v, _ in sizes]) / 1048576.0))
        for u, d in doc["units"].items():
            g = (d.get("commit_store") or {})
            g = g.get("growth") if isinstance(g, dict) else None
            if g:
                L.append("     %-26s iter %d = %.1f MiB  ->  iter %d = %.1f MiB"
                         % (u.split("__")[-1][:26], g["first_iter"], g["first_mib"],
                            g["last_iter"], g["last_mib"]))
    cc = doc.get("commit_cost") or {}
    if cc.get("n_observed"):
        L.append("")
        L.append("COMMIT COST (the pause, measured): median %.1f MiB in %.1fs over %d commit(s)"
                 % (cc["median_mib"], cc["median_seconds"], cc["n_observed"]))
    cs = doc.get("cold_start_split") or {}
    L.append("")
    if cs.get("median_seconds"):
        L.append("COLD-START SPLIT (median over %d attempt(s) that recorded one):"
                 % cs.get("n_attempts_with_a_split", 0))
        for k, v in cs["median_seconds"].items():
            L.append("   %-34s %6.1f min   (n=%d)" % (k, v / 60.0, cs["n_observations"][k]))
    else:
        L.append("COLD-START SPLIT: no attempt has recorded one yet — phase marks became timestamped on "
                 "2026-07-31, so only attempts started after that can be split.")
    L.append("")
    L.append("SELF-TIMED LINE ITEMS: setup build median %ss over %d build(s); checkpoint restore median %ss"
             % (doc["totals"]["setup_build_seconds_median"], doc["totals"]["n_setup_builds"],
                doc["totals"]["restore_seconds_median"]))
    for uid, u in doc["units"].items():
        L.append("")
        L.append("-- %s" % uid)
        for a in u["attempts"]:
            L.append("   %-28s %-22s %s" % (a["attempt"], a["utc"][:19], a["verdict"]))
            if a["restore_list"]:
                L.append("      restore LIST: %s" % a["restore_list"])
            if a["restore_fetch"]:
                L.append("      restore FETCH: %s" % a["restore_fetch"][:3])
            if a["s_per_iter"]:
                L.append("      median %s s/iter" % a["s_per_iter"])
    return "\n".join(L)


def _main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mode", default="5aks")
    ap.add_argument("--limit", type=int, default=6, help="newest N archived attempts per unit")
    ap.add_argument("--out", default=None)
    ap.add_argument("--head", type=int, default=0,
                    help="also print the first N lines of one real run.log — the anchors this parser does "
                         "not know about are only discoverable by looking")
    a = ap.parse_args(argv)
    doc = measure(mode=a.mode, limit=a.limit)
    print(render(doc))
    if a.head:
        b, p, s3 = tv.DEFAULT_BUCKET, tv.RESULT_PREFIX.rstrip("/"), tv._s3()
        for uid in doc["units"]:
            try:
                txt = s3.get_object(Bucket=b, Key=f"{p}/legs/{uid}/run.log")["Body"].read().decode(
                    "utf-8", "replace")
            except Exception:  # noqa: BLE001
                continue
            print("\n==== first %d lines of %s run.log ====" % (a.head, uid))
            print("\n".join(txt.splitlines()[:a.head]))
            break
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(doc, fh, indent=1)
        print("\nwrote %s" % a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
