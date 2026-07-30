#!/usr/bin/env python3
"""How often is the market refusing to start our containers? A PERISHABLE trend, and never a gate.

★★ THE GAP THIS FILLS (2026-07-29). Between 9:25 AM and 10:01 AM ET the ternary lane rented four hosts —
machines 29711, 28164, 12227, 41950 — and every one answered `resources_unavailable` on start and was
correctly torn down. Every board read was cheap (1.04x, 1.09x, 1.34x basis, all far under the buy line), so
this was never a price problem: the offers were there, priced fine, and would not run.

Then I went to bring trimcrae the TREND, which CLAUDE.md §6 explicitly asks for in the "ceiling nobody can
clear" case — *"bring trimcrae the trend, not just the latest number"* — and could not, because **nothing
records a capacity refusal anywhere.** `vast_machine_blacklist.publish()` REFUSES `CLASS_CAPACITY` outright,
by trimcrae's ruling that a capacity refusal is *"a claim about a moment, not about the host"*. That ruling is
right and is not touched here. Its unintended consequence is that a sustained availability failure leaves no
durable trace at all: the four refusals above exist only in four CI job logs that nobody will read again, and
the shared blacklist for that whole morning shows a single row — a `retire`.

So the system was built so that the one pattern §6 wants trended is the one pattern it cannot see.

WHAT THIS IS, PRECISELY. A rolling window of refusal EVENTS, aged out by time. It answers "how many hosts have
refused us, across how many distinct machines, in the last N hours" — the question a human needs to decide
whether to wait, switch provider, or stop. It is written by the same teardown branch that already handles the
refusal, so it costs one put per refusal and nothing otherwise.

⛔ IT MUST NEVER GATE ANYTHING, AND THAT IS NOT A STYLE PREFERENCE. The moment a refusal count can withhold a
rental it has become the durable, accumulating machine-exclusion trimcrae struck down — just wearing a
different name, and worse for being derived rather than declared. `summarize()` returns numbers for a READOUT.
Nothing in this module returns a verdict, a block, a hold or an exclusion, and `tests/test_capacity_refusal_
trend.py` asserts that against the parsed source so a later "just one small check" cannot slip in.

PERISHABLE BY CONSTRUCTION, three ways:
  1. Every event carries its own `utc` and is dropped once older than `WINDOW_H`.
  2. The window is pruned on WRITE, so the object cannot grow without bound even if nobody reads it.
  3. There is no per-machine aggregate stored — only events. A machine that refused once at 9 AM has no
     standing record by lunchtime, which is exactly what "a moment, not a property" means.
"""
from __future__ import annotations

import calendar
import json
import time

# 24 h. Long enough to show an overnight pattern (the 4.6-hour blackout on 2026-07-26/27 would be one glance),
# short enough that a refusal genuinely stops mattering. NOT tunable per lane — a per-lane window is how a
# trend gets quietly shortened until it never shows anything.
WINDOW_H = 24.0

DEFAULT_KEY = "ternary-vast/_capacity_refusals.json"

_WHAT = ("PERISHABLE capacity-refusal events, for a READOUT only — never a gate, never an exclusion. "
         "A capacity refusal is a claim about a MOMENT, not about the host (trimcrae, 2026-07-27), so "
         "nothing here may ever withhold a rental. Events age out after WINDOW_H hours.")


def _utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _epoch(utc):
    """Seconds since epoch for an ISO-Z stamp, or None if it cannot be parsed. Never raises — an undateable
    event is dropped rather than allowed to poison the window with a wrong age."""
    if not utc:
        return None
    try:
        return calendar.timegm(time.strptime(str(utc), "%Y-%m-%dT%H:%M:%SZ"))
    except Exception:  # noqa: BLE001
        return None


def prune(events, now_epoch=None, window_h=WINDOW_H):
    """Drop events older than the window, and any that cannot be dated. PURE."""
    now = now_epoch if now_epoch is not None else time.time()
    cutoff = now - window_h * 3600.0
    out = []
    for e in events or []:
        ts = _epoch((e or {}).get("utc"))
        if ts is None or ts < cutoff:
            continue
        out.append(e)
    return out


def summarize(events, now_epoch=None, window_h=WINDOW_H):
    """The numbers a human needs. PURE, and returns ONLY counts — no verdict, by design."""
    live = prune(events, now_epoch=now_epoch, window_h=window_h)
    machines = sorted({str((e or {}).get("machine_id")) for e in live if (e or {}).get("machine_id") is not None})
    units = sorted({str((e or {}).get("unit_id")) for e in live if (e or {}).get("unit_id")})
    stamps = sorted(_epoch(e.get("utc")) for e in live)
    span_h = round((stamps[-1] - stamps[0]) / 3600.0, 2) if len(stamps) >= 2 else 0.0
    return {"window_h": window_h, "n_refusals": len(live), "n_distinct_machines": len(machines),
            "machines": machines, "n_units_affected": len(units), "units": units,
            "span_h": span_h,
            "per_h": round(len(live) / span_h, 2) if span_h > 0 else None}


def render(s):
    """One operator line. Deliberately carries NO recommendation — this module reports, it does not decide."""
    if not s["n_refusals"]:
        return "    capacity refusals: none in the last %.0f h" % s["window_h"]
    return ("    ⓘ CAPACITY-REFUSAL TREND: %d refusal(s) across %d distinct machine(s) in the last %.0f h "
            "(span %.2f h%s), affecting %d unit(s). Every board read may still be CHEAP — a refusal is the "
            "host declining to start, not a price. This is a READOUT, not a gate: nothing here withheld a "
            "rental."
            % (s["n_refusals"], s["n_distinct_machines"], s["window_h"], s["span_h"],
               "" if s["per_h"] is None else ", %.2f/h" % s["per_h"], s["n_units_affected"]))


def load(s3, bucket, key=None):
    try:
        raw = s3.get_object(Bucket=bucket, Key=key or DEFAULT_KEY)["Body"].read().decode()
        doc = json.loads(raw)
        return list(doc.get("events") or [])
    except Exception:  # noqa: BLE001 — an absent or unreadable ledger is "no events", never an error
        return []


def record(s3, bucket, machine_id, unit_id, lane, why=None, key=None, now_epoch=None):
    """Append one refusal event and prune. Returns the post-write summary, or None if it could not be written.

    Failure here must NEVER disturb the caller: this is instrumentation attached to a teardown that is doing
    real work, and a monitoring aid that can break a teardown is worse than no monitoring aid.
    """
    if s3 is None or not bucket:
        return None
    try:
        events = prune(load(s3, bucket, key), now_epoch=now_epoch)
        events.append({"utc": _utcnow(), "machine_id": None if machine_id is None else str(machine_id),
                       "unit_id": unit_id, "lane": lane, "why": (str(why)[:300] if why else None)})
        s3.put_object(Bucket=bucket, Key=key or DEFAULT_KEY,
                      Body=json.dumps({"_what": _WHAT, "window_h": WINDOW_H,
                                       "events": events}, indent=2).encode())
        return summarize(events, now_epoch=now_epoch)
    except Exception as e:  # noqa: BLE001
        print(f"    (capacity-refusal trend not recorded: {type(e).__name__}: {e})")
        return None
