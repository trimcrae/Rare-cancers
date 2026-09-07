#!/usr/bin/env python3
"""THE ALARM BOARD AS A COMMITTED FILE — a PULL channel. Nothing is sent to anybody, ever.

★★ WHY THIS REPLACED THE ISSUE CHANNEL (trimcrae, 2026-07-31, verbatim: *"You're emailing me way too much.
You should not be emailing me."*).

Earlier the same day the escalation was a GitHub Issue, deduplicated and self-closing. It worked exactly as
designed, and that was the problem: **every issue open, comment and close emails the repo owner** through
their GitHub notification settings, so a channel built to be RELIABLE was by construction a channel that
mails him — and the self-test proving it worked mailed him four more times. The dedupe and the auto-close
were not the fault. Choosing a PUSH channel at all was.

⚠ RE-READ THE ACTUAL REQUIREMENT, WHICH WAS NEVER "NOTIFY TRIMCRAE": it is that **supervision survives with
no LLM in the loop**. That is a PULL requirement, and this repo already had the right pattern — the one thing
that works when everything else has stopped, because *a supervisor that has stopped cannot report that it
stopped*:

    A COMMITTED ARTIFACT THAT CARRIES ITS OWN EXPIRY, so a reader who OPENS THE FILE can tell it is dead
    without running anything, without an API, and without a clock but their own.

`work-ledger.json` does this with `_generated_utc` / `_stale_after_utc` / `_stale_after_means`. This module
does the same for the alarm verdicts. It sends nothing, opens nothing, comments on nothing, and — deliberately
— **cannot fail a run**: a red run is itself a push channel (GitHub emails the owner when a scheduled workflow
fails), so a recorder that exits non-zero would have quietly reintroduced the very thing being removed.

★ THE STALENESS WINDOW IS DERIVED, NEVER TYPED (CLAUDE.md §1). The cadence has ONE home already:
`work_ledger.EXPECTED_TICK_MIN`, itself derived from `step1-fanout-supervisor.yml`'s `tick_every_min` x
`watch_every_ticks`, and published in every `work-ledger.json` as `_expected_tick_min`. This module reads
that NUMBER OUT OF THE COMMITTED ARTIFACT rather than importing the module — a data dependency, not a code
one, so a broken `work_ledger` cannot take the board down with it. When it cannot be read, the window says
so in `_stale_window_basis` instead of inventing a number that looks derived and is not.

⚠ WHY THAT MATTERS, MEASURED: the issue that fired at 11:38 AM ET said *"the artifact is 8 min old, past the
1 min window"*. That 1-minute window was a deliberate `stale_min=1` test input, not the live setting (the
live default is 240 min, from measured 141-238 min GitHub delivery) — but it is exactly what a hand-set
window looks like when it is wrong, and the artifact it watches only refreshes on the ~16 min collect
cadence. A window that is not derived from the real refresh cadence trips on essentially every pass.

WHAT IT NEVER DOES: no issue, no email, no SES, no SMTP, no push of any kind; it rents, prices, reaps and
destroys nothing. Pure stdlib, and it imports nothing from the lanes it reports on — the failure it exists to
record is a shared-dependency failure.

Usage:
    python3 alarm_state.py --lane-report /tmp/lane-staleness-verdict.json \
                           --fleet-verdict /tmp/fleet-supervision-verdict.json \
                           --state research/modalities/alarm-state.json --write
Always exits 0 unless its own arguments are wrong.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys

ET = datetime.timezone(datetime.timedelta(hours=-4))  # EDT. CLAUDE.md §1: always US Eastern, 12-hour.

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STATE = os.path.join(HERE, "alarm-state.json")
DEFAULT_LEDGER = os.path.join(HERE, "work-ledger.json")

#: How many missed ticks before the BOARD declares itself stale. The tick LENGTH is not defined here — it is
#: read from `work-ledger.json` (see the module docstring). 3 is the same multiple the ledger uses, and it is
#: small on purpose: this deadline is read by a human opening a file, so it has to be tight enough to be
#: worth reading, and a false "stale" costs nothing but a second look.
STALE_AFTER_TICKS = 3.0

#: Used ONLY when the ledger's `_expected_tick_min` cannot be read, and the artifact SAYS SO when it is used.
#: It is a fallback, not a setting: a number that looks derived and is not is worse than an admitted guess.
FALLBACK_TICK_MIN = 16.0

#: Verdicts that name a FAILURE TO MEASURE rather than a measured failure. They are recorded in full — a
#: pull board has no reason to hide anything — but they are listed separately from `needs_attention`, because
#: "we could not read the lane" and "the lane is dead" are different problems with different fixes, and
#: merging them is what teaches a reader to skim past both.
UNMEASURED_VERDICTS = frozenset({
    "UNKNOWN",               # lane_staleness_watch: a CRITICAL field could not be read
    "FRESH-API-UNREADABLE",  # fleet_supervision_alarm: the artifact is fresh, the run history was not readable
    "TICKS-UNREADABLE",      # lane_staleness_watch supervision
})


def _et(ts):
    return ts.astimezone(ET).strftime("%I:%M %p ET %b %d, %Y").lstrip("0").replace(" 0", " ") if ts else None


def _z(ts):
    return ts.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if ts else None


def _parse_z(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return None


# ═══════════════════════════════════════════════════════════════════════════ the cadence, read not typed
def expected_tick_min(ledger_path=DEFAULT_LEDGER):
    """`(minutes, basis)` — the cadence this board is expected to be refreshed at.

    Read out of the committed `work-ledger.json`, which is the ONE home for it (CLAUDE.md §1). A DATA
    dependency deliberately, not an import: a broken `work_ledger` must not be able to take this board down,
    since a broken supervisor chain is one of the things the board exists to record.
    """
    try:
        with open(ledger_path) as fh:
            doc = json.load(fh)
        v = float(doc["_expected_tick_min"])
        if v <= 0:
            raise ValueError(f"non-positive {v}")
        return v, (f"read from work-ledger.json `_expected_tick_min` = {v:g} min, which is its one home "
                   f"(derived there from step1-fanout-supervisor.yml's tick_every_min x watch_every_ticks). "
                   f"Not typed here.")
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
        return FALLBACK_TICK_MIN, (
            f"⚠ NOT DERIVED — work-ledger.json `_expected_tick_min` could not be read "
            f"({type(e).__name__}: {e}), so this board fell back to {FALLBACK_TICK_MIN:g} min. Treat the "
            f"deadline below as approximate in BOTH directions until the ledger is readable again.")


# ═══════════════════════════════════════════════════════════════════════════ conditions
def _row(key, source, verdict, ok, detail, label="", payload=None):
    unmeasured = (not ok) and verdict in UNMEASURED_VERDICTS
    return {"key": key, "source": source, "label": label, "verdict": verdict, "ok": bool(ok),
            "unmeasured": unmeasured, "needs_attention": (not ok) and not unmeasured,
            "detail": detail, "payload": {k: v for k, v in (payload or {}).items() if v not in (None, "")}}


def conditions_from_fleet_verdict(v):
    """`fleet_supervision_alarm.py --json` -> one condition. One fleet, one supervision question."""
    unreadable = v.get("runs_readable") is False
    verdict = v.get("verdict", "?")
    row = _row("fleet-supervision", "fleet_supervision_alarm.py", verdict, v.get("ok", False),
               v.get("detail", ""), label="is anything measuring the step-1 fleet?",
               payload={"artifact_generated_et": v.get("artifact_generated_et"),
                        "artifact_age_min": v.get("artifact_age_min"),
                        "live_instances": v.get("live_instances"),
                        "realised_usd_so_far": v.get("realised_usd_so_far"),
                        "last_completed_run_et": v.get("last_completed_run_et"),
                        "last_completed_conclusion": v.get("last_completed_conclusion"),
                        "scheduled_delivery_gaps_min": v.get("scheduled_delivery_gaps_min"),
                        "fetch_error": v.get("fetch_error")})
    if unreadable and not row["ok"]:
        # The verdict rests on a question that was never answered, so it is recorded as unmeasured rather
        # than as an outage — the 2026-07-27 4:18 PM false alarm was exactly this case graded the other way.
        row["unmeasured"], row["needs_attention"] = True, False
    return [row]


def conditions_from_lane_report(r):
    """`lane_staleness_watch.py --json` -> one condition per lane, healthy lanes included.

    The healthy ones are not filler: on a pull board, a lane that is present and green is the only way a
    reader can tell "watched and fine" from "not watched at all", which is the distinction the whole
    supervision effort exists around.
    """
    out = []
    for lane in r.get("lanes", []):
        sup = lane.get("supervision") or {}
        out.append(_row(f"lane:{lane.get('lane')}", "lane_staleness_watch.py", lane.get("verdict", "?"),
                        lane.get("ok", False), lane.get("detail", ""), label=lane.get("label", ""),
                        payload={"provider": lane.get("provider"),
                                 "evidence_age_min": lane.get("evidence_age_min"),
                                 "census_flat_for_min": lane.get("census_flat_for_min"),
                                 "supervision": sup.get("verdict")}))
    return out


# ═══════════════════════════════════════════════════════════════════════════ merge with the previous board
def merge(previous, conditions, now):
    """Carry each condition's history forward. State lives IN the artifact — there is no side store.

    Three things survive a run and they are the reason this is worth committing at all: WHEN a condition was
    first seen bad, HOW MANY consecutive runs have seen it, and WHEN its verdict last changed. An
    instantaneous snapshot cannot answer "has this been red all night?", which is the first question anyone
    opening the file will have.
    """
    prev = {c["key"]: c for c in (previous or {}).get("conditions", []) if isinstance(c, dict)}
    for c in conditions:
        p = prev.get(c["key"], {})
        changed = p.get("verdict") != c["verdict"]
        c["last_seen_utc"] = _z(now)
        c["last_change_utc"] = _z(now) if changed or not p else p.get("last_change_utc")
        if c["ok"]:
            c["bad_since_utc"], c["consecutive_bad_runs"] = None, 0
        else:
            c["bad_since_utc"] = _z(now) if (p.get("ok", True) or not p.get("bad_since_utc")) \
                else p["bad_since_utc"]
            c["consecutive_bad_runs"] = 1 if p.get("ok", True) else int(p.get("consecutive_bad_runs", 0)) + 1
        since = _parse_z(c["bad_since_utc"] or "")
        c["bad_for_min"] = round((now - since).total_seconds() / 60.0, 1) if since else None
        c["bad_since_et"] = _et(since)
    # ⚠ A CONDITION THAT VANISHED IS NOT A CONDITION THAT CLEARED. A source that failed to run supplies no
    # rows at all, and silently dropping its keys would render "we stopped checking" identically to "it is
    # fine" — the measured-zero defect. Keys whose SOURCE is absent this run are carried over, marked.
    live_sources = {c["source"] for c in conditions}
    seen = {c["key"] for c in conditions}
    for key, p in prev.items():
        if key in seen or p.get("source") in live_sources:
            continue
        carried = dict(p)
        carried["stale_carried_over"] = True
        carried["detail"] = (f"⚠ NOT RE-MEASURED THIS RUN — {p.get('source')} supplied no verdict, so this "
                             f"row is the last one recorded ({_et(_parse_z(p.get('last_seen_utc') or ''))}). "
                             f"Carried over rather than dropped: a row that disappears reads as a row that "
                             f"cleared.")
        carried["needs_attention"], carried["unmeasured"] = False, True
        conditions.append(carried)
    return conditions


def build(previous, conditions, now, *, ledger_path=DEFAULT_LEDGER):
    tick, basis = expected_tick_min(ledger_path)
    stale_after = now + datetime.timedelta(minutes=tick * STALE_AFTER_TICKS)
    conditions = merge(previous, conditions, now)
    attention = [c["key"] for c in conditions if c.get("needs_attention")]
    unmeasured = [c["key"] for c in conditions if c.get("unmeasured")]
    return {
        "_what": "THE ALARM BOARD, AS A FILE. Every supervision verdict, when it was measured, how long it "
                 "has been that way, and when this file should be considered dead. Written by "
                 "alarm_state.py.",
        "_read_this_when": "you want to know whether anything is wrong and whether anything is still "
                           "watching — WITHOUT running anything, and without having been told.",
        "_this_channel_is_PULL_ONLY": "trimcrae, 2026-07-31: 'You should not be emailing me.' Nothing here "
                                      "sends, opens an issue, comments, or fails a run. A red run and a "
                                      "GitHub issue are both PUSH channels that email the repo owner; this "
                                      "file exists so neither is needed. If you are reading this, the "
                                      "channel worked.",
        "_generated_utc": _z(now), "_generated_et": _et(now),
        "_expected_tick_min": tick,
        "_stale_window_basis": basis,
        "_stale_after_utc": _z(stale_after), "_stale_after_et": _et(stale_after),
        "_stale_after_means": (
            f"IF THE CLOCK IS PAST THIS AND THIS FILE HAS NOT CHANGED, NOTHING IS WATCHING and every verdict "
            f"below is a memory, not a measurement. The deadline is written INTO the artifact because a "
            f"supervision chain that has stopped cannot report that it stopped — it needs no process, no API "
            f"and no clock but yours. {STALE_AFTER_TICKS:g} missed ticks at {tick:g} min. "
            f"Restart it: `gh workflow run step1-fanout-supervisor.yml --ref main`."),
        "ok": not attention,
        "n_conditions": len(conditions),
        "needs_attention": attention,
        "unmeasured": unmeasured,
        "_unmeasured_means": "a verdict that could not be reached, NOT a lane that is fine. Listed apart "
                             "from needs_attention because the fix is different: make it readable first.",
        "conditions": sorted(conditions, key=lambda c: (c.get("ok", True), c["key"])),
    }


# ═══════════════════════════════════════════════════════════════════════════ render
_GLYPH = {True: "✅", False: "⛔"}


def render(board, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    stale_after = _parse_z(board.get("_stale_after_utc") or "")
    dead = stale_after is not None and now > stale_after
    lines = [
        f"[alarm-board] generated {board.get('_generated_et')} · this file goes stale after "
        f"{board.get('_stale_after_et')}"
        + ("   ⛔ AND IT IS PAST THAT — NOTHING IS WATCHING" if dead else ""),
        f"[alarm-board] staleness window: {board.get('_stale_window_basis')}",
        "[alarm-board] PULL ONLY — nothing was sent, no issue opened, no run failed.",
    ]
    for c in board.get("conditions", []):
        glyph = "🔎" if c.get("unmeasured") else _GLYPH[bool(c.get("ok"))]
        age = f" · bad for {c['bad_for_min']:.0f} min ({c['consecutive_bad_runs']} run(s))" \
            if c.get("bad_for_min") else ""
        lines.append(f"[alarm-board] {glyph} {c['key']:<26} {c['verdict']:<22} {c.get('label', '')}{age}")
        if not c.get("ok"):
            lines.append(f"[alarm-board]      {c.get('detail', '')}")
    att, unm = board.get("needs_attention", []), board.get("unmeasured", [])
    lines.append(f"[alarm-board] {len(att)} need attention {att or ''} · {len(unm)} unmeasured {unm or ''} "
                 f"· {board.get('n_conditions')} condition(s) recorded")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════ cli
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fleet-verdict", default=None)
    ap.add_argument("--lane-report", default=None)
    ap.add_argument("--state", default=DEFAULT_STATE, help="the committed board; read for history, rewritten")
    ap.add_argument("--ledger", default=DEFAULT_LEDGER, help="where the tick cadence is READ from")
    ap.add_argument("--write", action="store_true", help="persist the board (otherwise print only)")
    a = ap.parse_args(argv)

    now = datetime.datetime.now(datetime.timezone.utc)
    conditions, missing = [], []
    for path, fn in ((a.fleet_verdict, conditions_from_fleet_verdict),
                     (a.lane_report, conditions_from_lane_report)):
        if not path:
            continue
        try:
            with open(path) as fh:
                conditions += fn(json.load(fh))
        except (OSError, json.JSONDecodeError) as e:
            # Recorded, not raised. ⚠ Exiting non-zero here would fail the run, and a failed run emails the
            # repo owner — reintroducing the push channel this module exists to remove.
            missing.append(f"{path}: {type(e).__name__}: {e}")

    try:
        with open(a.state) as fh:
            previous = json.load(fh)
    except (OSError, json.JSONDecodeError):
        previous = None

    board = build(previous, conditions, now, ledger_path=a.ledger)
    if missing:
        board["_sources_unreadable"] = missing
        board["_sources_unreadable_means"] = (
            "a producing step did not leave a verdict file, so those conditions were NOT re-measured this "
            "run. Their rows above are carried over and marked; do not read them as current.")
    print(render(board, now))
    for m in missing:
        print(f"[alarm-board] ⚠ source unreadable: {m}")
    if a.write:
        with open(a.state, "w") as fh:
            json.dump(board, fh, indent=2)
            fh.write("\n")
        print(f"[alarm-board] wrote {a.state}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
