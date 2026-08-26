#!/usr/bin/env python3
"""LOOP HEALTH AS A COMMITTED FILE — the ten conditions of
`research/manuscripts/program/emc-autonomy-architecture.md` §5.2, in the `alarm-state.json` idiom.

★★ WHY THIS EXISTS. §5.1 already covers ARTIFACT correctness — every gate in `./scripts/preflight.sh`
checks whether what the loop wrote is true. Nothing checks whether the LOOP IS WORKING. Those are
different failures and conflating them is how a loop passes its own tests while producing nothing:
a cycle that fires, writes a tidy negative, commits green and advances no live route is *indexed as
success* by every gate this repository owns. The architecture's own summary of the risk (§0): the
largest failure mode is "a loop that runs forever, commits daily, and advances nothing".

★ THE IDIOM IS DELIBERATELY `alarm_state.py`'s, NOT A NEW ONE. Same three properties, for the same
reason — a supervisor that has stopped cannot report that it stopped:
  `_generated_utc` / `_stale_after_utc` / `_stale_after_means`  — the file carries its OWN expiry, so a
  reader who opens it can tell it is dead without running anything, without an API and without a clock
  but their own;
  per-condition `bad_since_utc` / `consecutive_bad_runs`  — "has this been red all night?" is the first
  question anyone opening the board will have, and a snapshot cannot answer it;
  `unmeasured` kept APART from `needs_attention`  — different problem, different fix.

⛔⛔ THE ONE RULE THIS FILE IS BUILT AROUND: **A CONDITION THAT COULD NOT BE MEASURED IS `unmeasured`,
NEVER `ok`.** CLAUDE.md §4: *an absent reading is not a reading of absence, and a populated field is not
a measured one.* Zero receipts does not mean the loop is delivering — it means nothing has reported.
An absent `publication-authority.json` does not mean authority was respected — it means there is
nothing to check acts against. A missing `route_advanced` field does not mean a route advanced.
Every one of those, graded the other way, produces a GREEN BOARD BUILT FROM MISSING DATA, which is
precisely the failure this repository has already paid for: env-echoed defaults once carried a
fabricated verdict all the way out, and a "FRESH-API-UNREADABLE" row graded as an outage produced the
2026-07-27 false alarm graded the other way. So `ok`, `unmeasured` and `needs_attention` are three
states here, constructed by three DIFFERENT functions (`_green` / `_unmeasured` / `_red`) rather than
by one function with a boolean, because a single constructor is one typo away from collapsing the
distinction — and `systems/tests/test_autonomy_health.py` mutation-tests exactly that collapse.

⭐ NO WORK, NO COMMIT — `fleet_armed.py`'s discipline, ported (measured cost of ignoring it: 1,476
commits in 24 h, 703 of which said in their own subject line that they did nothing). `commit_worthy()`
answers whether this board SAYS anything the committed one did not. ⛔ And it keeps the other half of
that lesson too: a board that stops refreshing must not read as a board that keeps saying "fine", so
the answer is also yes whenever the committed copy is about to age past its own staleness window.

WHAT IT NEVER DOES: no network, no model, no subprocess, no push channel of any kind. Pure stdlib and
deterministic — the same inputs give the same board, so a diff in `health.json` is a change in the LOOP,
never in the checker. It cannot fail a run either: `--write` and the default render always exit 0,
because a red run emails the repo owner and that is the push channel `alarm_state.py` exists to remove.
`--check` is the opt-in non-zero exit, for a caller that wants the gate.

Usage:
    python3 research/autonomy/health.py                 # the board, as a table
    python3 research/autonomy/health.py --write         # (re)write research/autonomy/health.json
    python3 research/autonomy/health.py --check         # exit 1 if any condition needs attention
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import sys

ET = datetime.timezone(datetime.timedelta(hours=-4))  # EDT. CLAUDE.md §1: US Eastern, 12-hour, always.

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LEDGER = os.path.join(HERE, "research-ledger.json")
DEFAULT_STATE = os.path.join(HERE, "autonomy-state.json")
DEFAULT_RECEIPTS = os.path.join(HERE, "receipts")
DEFAULT_HEALTH = os.path.join(HERE, "health.json")
DEFAULT_AUTHORITY = os.path.join(HERE, "publication-authority.json")

#: The TEN §5.2 conditions, in the order the architecture table lists them. Renaming or dropping one
#: is a "free, but DECLARED" edit under §10.4 — it changes what "doing well" MEANS — so it goes in the
#: amendment log, never silently.
CONDITION_ORDER = (
    "cycle_delivering",
    "advancing_live_work",
    "evidence_moving",
    "blocks_are_real",
    "queue_is_takeable",
    "cycles_are_sized",
    "fanout_is_governed",
    "budget_recovering",
    "gates_green",
    "authority_respected",
)

#: §5.2 thresholds. Each is the doc's number, in one place, named after the row it governs.
CYCLE_MISS_PERIODS = 2.0        # "no receipt within 2 expected cycle periods"
EVIDENCE_FROZEN_PERIODS = 2.0   # "running with last_evidence_utc unchanged over 2 cycles"
NO_ADVANCE_RUN = 3              # "3 consecutive receipts with route_advanced: none"
BACKOFF_GRACE_H = 24.0          # "backoff level > 0 for > 24 h"
GATES_RED_GRACE_H = 24.0        # "preflight red on main for > 24 h"

#: How many expected cycle periods before the BOARD declares itself dead. Same multiple, and same
#: reasoning, as `alarm_state.STALE_AFTER_TICKS`: a human reads this deadline, so it has to be tight
#: enough to be worth reading, and a false "stale" costs one second look.
STALE_AFTER_CYCLES = 3.0

#: ⚠ USED ONLY WHEN `autonomy-state.json` CANNOT BE READ, AND THE BOARD SAYS SO WHEN IT IS USED. It is
#: a fallback, not a setting — the cycle interval's one home is the state file (§9.2's start point).
#: A number that looks derived and is not is worse than an admitted guess (`alarm_state` idiom).
FALLBACK_CYCLE_INTERVAL_H = 4.0


# ═════════════════════════════════════════════════════════════════════════════════ time, read not typed
def _z(ts):
    return ts.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if ts else None


def _et(ts):
    return ts.astimezone(ET).strftime("%-I:%M %p ET %b %-d, %Y") if ts else None


def _parse_ts(s):
    """UTC datetime, or None. ⚠ None means UNREADABLE and every caller must treat it as unmeasured.

    Three shapes are accepted because three already exist in the tree: the `%Y-%m-%dT%H:%M:%SZ` stamp
    `alarm_state`/`work_ledger` write, an ISO-8601 stamp with an explicit offset, and the DATE-ONLY
    `last_evidence_utc` the seeded `research-ledger.json` actually carries ("2026-08-08"). A date-only
    value is read as midnight UTC, which is the earliest instant it can mean — the conservative
    direction for a staleness test, since it can only make an entry look older, never fresher.
    """
    if not isinstance(s, str) or not s.strip():
        return None
    raw = s.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(raw, fmt).replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            pass
    try:
        dt = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)


def _hours(later, earlier):
    return (later - earlier).total_seconds() / 3600.0


def _is_empty(v):
    """Empty in the sense `blocked_evidence` means it: nothing was OBSERVED and recorded."""
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    if isinstance(v, (list, tuple, dict, set)):
        return not v
    return False


# ═════════════════════════════════════════════════════════════════ the three verdict states, kept apart
def _row(key, label, source, verdict, *, ok, unmeasured, detail, payload=None):
    # ⛔ The invariant, asserted rather than commented: ok and unmeasured are mutually exclusive, and
    # `needs_attention` is the third state — a MEASURED failure. A row that is both is the collapse
    # this module exists to prevent, and it must die here rather than reach a reader as a green board.
    assert not (ok and unmeasured), f"{key}: a row cannot be both ok and unmeasured"
    return {
        "key": key,
        "label": label,
        "source": source,
        "verdict": verdict,
        "ok": bool(ok),
        "unmeasured": bool(unmeasured),
        "needs_attention": (not ok) and (not unmeasured),
        "detail": detail,
        "payload": {k: v for k, v in (payload or {}).items() if v not in (None, "")},
    }


def _green(key, label, source, verdict, detail, payload=None):
    """MEASURED, and fine. Reachable only when the reading was actually taken."""
    return _row(key, label, source, verdict, ok=True, unmeasured=False, detail=detail, payload=payload)


def _red(key, label, source, verdict, detail, payload=None):
    """MEASURED, and failing. This is the state that escalates (§7 trigger 4)."""
    return _row(key, label, source, verdict, ok=False, unmeasured=False, detail=detail, payload=payload)


def _unmeasured(key, label, source, verdict, detail, payload=None):
    """⛔ NOT MEASURABLE — the reading could not be taken. NOT `ok`, and NOT `needs_attention` either.

    Separate from both on purpose, because the FIX is different: a red condition needs the loop fixed,
    an unmeasured one needs the reading made possible first. Collapsing it into `ok` is the failure
    mode named in the module docstring; collapsing it into `needs_attention` is the 2026-07-27 false
    alarm. `detail` must always name WHAT WOULD SETTLE IT — an unmeasured row that does not say how to
    become measurable is an unanswered question wearing the costume of a status (CLAUDE.md §4).
    """
    return _row(key, label, source, verdict, ok=False, unmeasured=True, detail=detail, payload=payload)


# ═════════════════════════════════════════════════════════════════════════════════════════════ inputs
def _read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), None
    except FileNotFoundError:
        return None, f"{os.path.basename(path)} is absent"
    except (OSError, json.JSONDecodeError) as e:
        return None, f"{os.path.basename(path)} is unreadable: {type(e).__name__}: {e}"


def load_receipts(receipts_dir=DEFAULT_RECEIPTS):
    """Every `<cycle-id>.json` in §4.2 step 10's directory, oldest first, plus the unreadable ones.

    ⚠ ORDER IS PART OF THE MEASUREMENT — `advancing_live_work` asks about the LAST THREE — so it is
    made deterministic rather than left to the filesystem: sort on the receipt's own end stamp, ties
    and missing stamps broken by filename. Cycle ids are timestamped, so filename order is the same
    order in practice; it is the tiebreak, not the source of truth.

    ⛔ A receipt that will not parse is returned in `unreadable`, never dropped. A cycle whose receipt
    is corrupt is not a cycle that did not run, and silently skipping it would let a broken writer
    read as a quiet loop.
    """
    receipts, unreadable = [], []
    for path in sorted(glob.glob(os.path.join(receipts_dir, "*.json"))):
        doc, err = _read_json(path)
        if err or not isinstance(doc, dict):
            unreadable.append(err or f"{os.path.basename(path)} is not a JSON object")
            continue
        doc = dict(doc)
        doc["_path"] = path
        doc["_file"] = os.path.basename(path)
        receipts.append(doc)
    receipts.sort(key=lambda r: (_receipt_ts_raw(r) or "", r["_file"]))
    return receipts, unreadable


#: Receipt timestamp keys, in precedence order. ⚠ §4.2 step 10 names the receipt's CONTENT ("what was
#: taken, what changed, what it cost, what is now queued, and route_advanced") but not its field names,
#: so these are this module's choice and the writer must match one of them. File mtime is deliberately
#: NOT a fallback: a fresh `git clone` rewrites every mtime, which would make an ancient receipt look
#: like this minute's — a populated field that is not a measured one (CLAUDE.md §4).
RECEIPT_TIME_KEYS = ("ended_utc", "finished_utc", "generated_utc", "cycle_ended_utc", "utc")


def _receipt_ts_raw(receipt):
    for key in RECEIPT_TIME_KEYS:
        v = receipt.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _receipt_ts(receipt):
    return _parse_ts(_receipt_ts_raw(receipt))


def cycle_interval_hours(state):
    """`(hours, basis)` — the expected cycle period, READ from `autonomy-state.json`, never typed.

    Returns `(None, basis)` when it cannot be read, and every condition that needs a cycle period then
    goes unmeasured rather than borrowing the fallback: the fallback exists ONLY to date the board's
    own expiry (a board with no expiry is worse than one with an approximate one), not to manufacture a
    threshold a verdict would then rest on.
    """
    if not isinstance(state, dict):
        return None, ("⚠ NOT READ — autonomy-state.json was not readable, so the expected cycle period "
                      f"is UNKNOWN and this board's own expiry falls back to "
                      f"{FALLBACK_CYCLE_INTERVAL_H:g} h. Treat the deadline as approximate in BOTH "
                      f"directions until the state file is readable again.")
    v = state.get("cycle_interval_hours")
    if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0:
        return None, ("⚠ NOT READ — autonomy-state.json carries no positive `cycle_interval_hours` "
                      f"(saw {v!r}), so the expected cycle period is UNKNOWN and this board's own "
                      f"expiry falls back to {FALLBACK_CYCLE_INTERVAL_H:g} h.")
    return float(v), (f"read from autonomy-state.json `cycle_interval_hours` = {float(v):g} h, which is "
                      f"its one home (the governor writes it — architecture §9.2). Not typed here.")


# ══════════════════════════════════════════════════════════════════════════════ the seven §5.2 conditions
def c_cycle_delivering(receipts, unreadable, interval_h, now):
    """Red when no receipt within 2 expected cycle periods (§2.2 — a fired Routine is not a delivered one).

    ⛔ ZERO RECEIPTS IS `unmeasured`, NOT `ok`, AND IT IS THE HEADLINE CASE OF THIS WHOLE FILE. An empty
    receipts directory is consistent with "the loop has never run", "the loop runs and cannot write",
    and "the clock never fired" — three different failures, none of them health. Grading it green is
    how a loop that has never delivered anything reports that it is delivering.
    """
    key, label = "cycle_delivering", "is a fired cycle actually DELIVERING a receipt?"
    source = "research/autonomy/receipts/*.json + autonomy-state.json"
    if interval_h is None:
        return _unmeasured(key, label, source, "PERIOD-UNKNOWN",
                           "the expected cycle period is unreadable, so 'late' has no definition. "
                           "Settle it: give autonomy-state.json a positive `cycle_interval_hours`.",
                           {"receipts_seen": len(receipts)})
    if not receipts:
        return _unmeasured(key, label, source, "NO-RECEIPTS",
                           "NO receipt exists yet, so delivery has never been observed — this is NOT a "
                           "reading that the loop is fine, it is the absence of a reading (CLAUDE.md "
                           "§4). Settle it: let one cycle complete §4.2 step 10, or check whether the "
                           "clock is firing at all.",
                           {"receipts_seen": 0, "unreadable_receipts": len(unreadable) or None})
    latest = receipts[-1]
    ts = _receipt_ts(latest)
    if ts is None:
        return _unmeasured(key, label, source, "RECEIPT-TIME-UNREADABLE",
                           f"the most recent receipt ({latest['_file']}) carries none of "
                           f"{list(RECEIPT_TIME_KEYS)}, so its age cannot be taken. A receipt with no "
                           f"clock cannot testify to delivery.",
                           {"receipts_seen": len(receipts), "latest_receipt": latest["_file"]})
    age_h = _hours(now, ts)
    deadline_h = CYCLE_MISS_PERIODS * interval_h
    payload = {"receipts_seen": len(receipts), "latest_receipt": latest["_file"],
               "latest_receipt_et": _et(ts), "age_h": round(age_h, 2),
               "deadline_h": round(deadline_h, 2), "unreadable_receipts": len(unreadable) or None}
    if age_h > deadline_h:
        return _red(key, label, source, "LATE",
                    f"the last receipt is {age_h:.1f} h old against a {deadline_h:.1f} h deadline "
                    f"({CYCLE_MISS_PERIODS:g} cycle periods of {interval_h:g} h). A Routine that fires "
                    f"and delivers nothing is indistinguishable from one that never fired — check the "
                    f"clock before assuming the cycle is slow.", payload)
    return _green(key, label, source, "DELIVERING",
                  f"the last receipt ({latest['_file']}) landed {age_h:.1f} h ago, inside the "
                  f"{deadline_h:.1f} h deadline.", payload)


def c_advancing_live_work(receipts, now):
    """Red on 3 consecutive receipts with `route_advanced: none` — CLAUDE.md §0's documentation drift.

    ⭐ This is the design's own honesty instrument (§4.2). Writing up a closed route always looks like
    progress and is always easier than the live one, so the loop is capable of running for months,
    committing daily, and advancing nothing — while every artifact gate stays green.

    ⛔ A MISSING `route_advanced` IS `unmeasured`, NOT `none` AND NOT `ok`. It is the field the whole
    condition rests on, and a writer that omits it is a broken writer, not a cycle that advanced
    nothing — nor one that did. Fewer than three receipts is likewise unmeasured: the condition is
    defined on a run of three and there is no shorter reading of it.
    """
    key, label = "advancing_live_work", "are cycles moving LIVE routes, or just documenting?"
    source = "research/autonomy/receipts/*.json `route_advanced`"
    if len(receipts) < NO_ADVANCE_RUN:
        return _unmeasured(key, label, source, "TOO-FEW-RECEIPTS",
                           f"{len(receipts)} receipt(s) exist and the condition is defined on a run of "
                           f"{NO_ADVANCE_RUN}. Not a verdict that the loop is advancing work — there is "
                           f"no verdict yet. Settle it: {NO_ADVANCE_RUN - len(receipts)} more cycle(s).",
                           {"receipts_seen": len(receipts)})
    window = receipts[-NO_ADVANCE_RUN:]
    raw = [(r["_file"], r.get("route_advanced")) for r in window]
    absent = [f for f, v in raw if not (isinstance(v, str) and v.strip())]
    if absent:
        return _unmeasured(key, label, source, "ROUTE-ADVANCED-ABSENT",
                           f"receipt(s) {absent} record no `route_advanced`, so what those cycles moved "
                           f"is unknown. §4.2 step 10 requires the route id or the literal 'none' — an "
                           f"omitted field is neither, and reading it as 'none' would invent a failure "
                           f"exactly as readily as reading it as ok would hide one.",
                           {"window": [f for f, _ in raw]})
    values = [v.strip() for _, v in raw]
    payload = {"window": [f for f, _ in raw], "route_advanced": values, "receipts_seen": len(receipts)}
    if all(v.lower() == "none" for v in values):
        return _red(key, label, source, "NOT-ADVANCING",
                    f"the last {NO_ADVANCE_RUN} receipts all record `route_advanced: none` — the loop is "
                    f"doing documentation, not research (CLAUDE.md §0). The fix is a live item off the "
                    f"top of the ledger, not a tidier negative.", payload)
    advanced = [v for v in values if v.lower() != "none"]
    return _green(key, label, source, "ADVANCING",
                  f"{len(advanced)} of the last {NO_ADVANCE_RUN} cycles moved a live route "
                  f"({', '.join(advanced)}).", payload)


def c_evidence_moving(entries, ledger_err, interval_h, now):
    """Red when a `running` entry's `last_evidence_utc` has not moved over 2 cycles.

    §4's unproven-pipeline rule as a board row: an item in flight must show MOVEMENT, and "no error
    yet" is not movement. ⛔ A running entry whose `last_evidence_utc` is unreadable is unmeasured, not
    fine — that is the field the reading is taken from.

    ⚠ Zero running entries IS a measurement, not an absence: the ledger was read and it says nothing is
    in flight, so nothing can be frozen. It is recorded as green with the vacuity stated in `detail`,
    because a reader must be able to tell "checked, nothing running" from "nothing checked".
    """
    key, label = "evidence_moving", "is work in flight producing new EVIDENCE, not just heartbeats?"
    source = "research/autonomy/research-ledger.json `state`/`last_evidence_utc`"
    if entries is None:
        return _unmeasured(key, label, source, "LEDGER-UNREADABLE", f"{ledger_err}.")
    if interval_h is None:
        return _unmeasured(key, label, source, "PERIOD-UNKNOWN",
                           "the expected cycle period is unreadable, so 'unchanged over 2 cycles' has "
                           "no definition. Settle it in autonomy-state.json.")
    running = [e for e in entries if str(e.get("state") or "").strip() == "running"]
    if not running:
        return _green(key, label, source, "NOTHING-RUNNING",
                      "the ledger was read and no entry is in state `running`, so no entry can be "
                      "frozen. Vacuously true, and stated as such: this row says the check ran, not "
                      "that the loop is busy — `cycle_delivering` is the row that says that.",
                      {"entries": len(entries), "running": 0})
    deadline_h = EVIDENCE_FROZEN_PERIODS * interval_h
    frozen, unreadable = [], []
    for e in running:
        ts = _parse_ts(e.get("last_evidence_utc"))
        if ts is None:
            unreadable.append(e.get("id"))
            continue
        age_h = _hours(now, ts)
        if age_h > deadline_h:
            frozen.append({"id": e.get("id"), "age_h": round(age_h, 2),
                           "last_evidence_utc": e.get("last_evidence_utc")})
    payload = {"entries": len(entries), "running": len(running), "deadline_h": round(deadline_h, 2),
               "frozen": frozen or None, "evidence_time_unreadable": unreadable or None}
    if frozen:
        return _red(key, label, source, "FROZEN",
                    f"{len(frozen)} running entr(ies) have not changed on evidence in over "
                    f"{deadline_h:.1f} h ({EVIDENCE_FROZEN_PERIODS:g} cycles): "
                    f"{[f['id'] for f in frozen]}. Twice frozen is a stall — diagnose it against the "
                    f"real log, never against the estimate (CLAUDE.md §4).", payload)
    if unreadable:
        return _unmeasured(key, label, source, "EVIDENCE-TIME-UNREADABLE",
                           f"running entr(ies) {unreadable} carry no readable `last_evidence_utc`, so "
                           f"whether they are moving cannot be read. Settle it: §4.2 step 9 requires "
                           f"the cycle to write back what it OBSERVED, with its stamp.", payload)
    return _green(key, label, source, "MOVING",
                  f"all {len(running)} running entr(ies) changed on evidence within {deadline_h:.1f} h.",
                  payload)


def c_blocks_are_real(entries, ledger_err):
    """Red on any `blocked` entry with empty `blocked_evidence` — CLAUDE.md §0.

    "Blocked" is a claim that needs evidence and it is usually wrong: most blocked rows in this repo
    were waiting on a $0 fetch, a regeneration or a staging step. `priority.py` re-emits a
    blocked-without-evidence ROUTE as a free `kind: fetch` check, so a row that is still sitting in
    state `blocked` with nothing recorded is either hand-added or written back by a cycle that skipped
    the observation — both are the same defect and both belong on the board.
    """
    key, label = "blocks_are_real", "does every BLOCKED row carry the observation that blocked it?"
    source = "research/autonomy/research-ledger.json `state`/`blocked_evidence`"
    if entries is None:
        return _unmeasured(key, label, source, "LEDGER-UNREADABLE", f"{ledger_err}.")
    blocked = [e for e in entries if str(e.get("state") or "").strip() == "blocked"]
    naked = [e.get("id") for e in blocked if _is_empty(e.get("blocked_evidence"))]
    payload = {"entries": len(entries), "blocked": len(blocked), "without_evidence": naked or None}
    if naked:
        return _red(key, label, source, "UNEVIDENCED-BLOCK",
                    f"{len(naked)} entr(ies) claim `blocked` with no recorded evidence: {naked}. "
                    f"Each is a $0 re-test away from being either a real block with a date on it or a "
                    f"live route nobody checked — CLAUDE.md §0.", payload)
    if not blocked:
        return _green(key, label, source, "NO-BLOCKS",
                      "the ledger was read and no entry is in state `blocked`.", payload)
    return _green(key, label, source, "EVIDENCED",
                  f"all {len(blocked)} blocked entr(ies) record what was observed to establish the block.",
                  payload)


def c_queue_is_takeable(entries, ledger_err):
    """⛔ THE STALL CONDITION. Is there ANY item a cycle could actually pick up right now?

    Every other condition here asks whether the loop is doing its work well. This one asks whether
    there is any work it CAN do — and a loop with nothing takeable does not crash, does not error and
    does not go quiet. It fires on schedule, re-scores, finds nothing, writes a receipt saying it did
    nothing, and repeats. From outside it is indistinguishable from a healthy loop on a slow week.

    A queue goes untakeable four ways, and all four have happened or nearly happened here:
      - every item CLAIMED by a cycle that died (fixed by the lease in priority.py, guarded here);
      - every item BLOCKED with evidence, so the penalty demotes them all and none is workable;
      - every item's retry budget spent;
      - the ledger emptied or unreadable.

    ⚠ It counts what a cycle would take, not what exists. An 81-entry ledger where all 81 are owned or
    blocked is an EMPTY queue, and reporting 81 would be the reassuring lie.
    """
    key = "queue_is_takeable"
    label = "is there any work a cycle could actually pick up?"
    source = "research/autonomy/research-ledger.json — unowned, unblocked, retry budget remaining"
    if entries is None:
        return _unmeasured(key, label, source, "LEDGER-UNREADABLE", f"{ledger_err}.")
    if not entries:
        return _red(key, label, source, "EMPTY-LEDGER",
                    "the ledger holds no entries at all, so every cycle from here does nothing. "
                    "Re-seed it: python3 research/autonomy/priority.py --write.")
    takeable = [
        e for e in entries
        if not e.get("owner")
        and str(e.get("state") or "queued") in {"queued", "blocked"}
        and int(e.get("retry_budget") or 0) > 0
        and e.get("score") is not None
    ]
    owned = [e.get("id") for e in entries if e.get("owner")]
    spent = [e.get("id") for e in entries if int(e.get("retry_budget") or 0) <= 0]
    payload = {"entries": len(entries), "takeable": len(takeable),
               "owned": owned or None, "retry_budget_spent": spent or None}
    if not takeable:
        return _red(key, label, source, "NOTHING-TAKEABLE",
                    f"{len(entries)} entr(ies) and NONE is takeable — "
                    f"{len(owned)} owned, {len(spent)} out of retry budget. Every cycle from here "
                    "will fire, find nothing, and write a receipt saying so. That is a stall wearing "
                    "the costume of a quiet week.", payload)
    return _green(key, label, source, "TAKEABLE",
                  f"{len(takeable)} of {len(entries)} entr(ies) are takeable now.", payload)


def c_cycles_are_sized(receipts, state, state_err):
    """Red when one session ran more cycles than the cap — the session-shape rule, MEASURED at last.

    ⛔⛔ THIS CONDITION EXISTS BECAUSE THE RULE IT ENFORCES FAILED IN THE WILD ON 2026-08-26, AND IT
    FAILED IN THE ONE WAY A WRITTEN RULE CAN FAIL COMPLETELY: it was never reached.
    `.claude/skills/research-loop/SKILL.md` §3 has always said a full hardening cycle is a SPAWNED
    session rather than more work in the current one. That rule lives in a SKILL, and a skill's rules
    bind only when the skill is loaded. Measured in the offending session's own transcript:
    `"name":"Skill"` appears ZERO times. The skill's description lists four load triggers and every
    one of them is a Routine firing a cycle — so on the INTERACTIVE path, where a human asks for
    research work directly, the rule was not weak, it was UNREACHABLE. That session ran CYC-0005 and
    CYC-0006 end to end, compacted 23 times, and reached a 7.6 MB transcript.

    ⭐ THE REPAIR IS TWO-SIDED AND THIS IS ONLY THE SECOND HALF. Reachability was fixed in CLAUDE.md,
    which loads every session including interactive ones, with a §6 tripwire pointing at the skill.
    But a rule nothing measures decays back into a suggestion — the lease and the stall alarm each
    have a suite and a workflow behind them, and §3 had nothing at all. This is that gate.

    ⚠ IT BOUNDS CYCLES, WHICH IS A PROXY FOR CONTEXT AND NOT CONTEXT ITSELF, and the limit is stated
    rather than hidden: one enormous single cycle passes this check. Nothing in this repository can
    read a context window, and receipts already carry `session_id`, so this is the measurement that
    exists rather than the one that would be ideal. An imperfect gate that fires beats a perfect one
    that does not.

    ⚠ A receipt with no readable `session_id` is UNMEASURED for that receipt, never counted as a
    fresh session — otherwise the absence of a field would read as evidence of good behaviour, which
    is CLAUDE.md §4's rule exactly.
    """
    key = "cycles_are_sized"
    label = "is each cycle getting a fresh context, or is one session doing all of them?"
    source = ("research/autonomy/receipts/*.json `session_id`, against "
              "autonomy-state.json `max_cycles_per_session`")
    if not isinstance(state, dict):
        return _unmeasured(key, label, source, "STATE-UNREADABLE",
                           f"{state_err or 'autonomy-state.json is unreadable'}, so the cap is "
                           "unknown and no verdict is possible.")
    cap = state.get("max_cycles_per_session")
    if not isinstance(cap, int) or cap < 1:
        return _unmeasured(key, label, source, "NO-CAP",
                           f"autonomy-state.json carries `max_cycles_per_session`={cap!r}, not a "
                           "positive integer, so there is nothing to check against.")
    if not receipts:
        return _unmeasured(key, label, source, "NO-RECEIPTS",
                           "no readable receipt carries a session_id yet.")

    counts, unstamped = {}, []
    for r in receipts:
        sid = r.get("session_id")
        cid = r.get("cycle_id") or "?"
        # A placeholder sentence is not an id. Anything without a plausible id token is unstamped.
        if not isinstance(sid, str) or not sid.strip() or sid.strip().lower().startswith("unknown"):
            unstamped.append(cid)
            continue
        counts.setdefault(sid.strip().split()[0], []).append(cid)

    over = {sid: cids for sid, cids in counts.items() if len(cids) > cap}
    payload = {"cap": cap, "sessions": {k: len(v) for k, v in counts.items()},
               "unstamped_receipts": unstamped or None,
               "worst": max((len(v) for v in counts.values()), default=0)}
    if over:
        worst = max(over.items(), key=lambda kv: len(kv[1]))
        return _red(key, label, source, "SESSION-OVERLOADED",
                    f"session {worst[0][:24]} ran {len(worst[1])} cycles ({', '.join(worst[1])}) "
                    f"against a cap of {cap}. §3 of the cycle contract: a full hardening cycle is a "
                    "SPAWNED session, not more work in the current one. Context is the resource that "
                    "runs out silently — nothing announces it, and the cycle that overruns it is the "
                    "one that cannot tell.", payload)
    if not counts:
        return _unmeasured(key, label, source, "NONE-STAMPED",
                           f"{len(unstamped)} receipt(s) carry no usable session_id "
                           f"({', '.join(unstamped[:5])}), so nothing can be counted. An absent "
                           "stamp is not evidence of a fresh session.", payload)
    return _green(key, label, source, "SIZED",
                  f"{len(counts)} session(s), worst carries {payload['worst']} cycle(s) against a "
                  f"cap of {cap}.", payload)


def c_fanout_is_governed(receipts, state, state_err):
    """Red when a cycle dispatched more concurrent subagents than `subagent_width` allows.

    ⛔⛔ THIS DIAL WAS WIRED TO NOTHING, AND IT IS THE ONE THE ARCHITECTURE CALLS THE MOST IMPORTANT.
    Measured 2026-08-26: `grep -rn subagent_width` over the whole repository returned TWO hits — the
    JSON that defines it, and one test asserting its value is 5. No code read it, no cycle consulted
    it, and no receipt recorded what was actually dispatched. §9 records why that matters: a
    **107-agent fan-out hit the account weekly usage limit — 40 completed, 67 errored, and the
    synthesis step failed**, so the tool's returned result was a truncation artifact and the findings
    had to be recovered by hand from journal.jsonl. The architecture's own words: *width is the more
    important dial — the incident above was a WIDTH failure, not a depth one.*

    ⭐ AND IT WAS WORSE THAN THE SESSION-SHAPE RULE THIS REPOSITORY FIXED AN HOUR EARLIER. That rule
    at least existed as prose in a skill; this was a NUMBER IN A STATE FILE CONNECTED TO NO CODE PATH
    AT ALL — the purest form of a governed value that governs nothing.

    ⛔ THE UNIT HAD NEVER BEEN WRITTEN DOWN EITHER, WHICH IS WHY THIS WAS UNENFORCEABLE RATHER THAN
    MERELY UNENFORCED. A cap of "5" says nothing until you say five of what. It is CONCURRENT
    subagents — see autonomy-state.json's `_subagent_width_means`, which now carries the reasoning and
    the limit of what this dial does NOT govern (serial total).

    ⚠ THIS IS A RETROSPECTIVE GATE AND SAYS SO. Nothing here can intercept a dispatch; a health
    condition reads committed files after the fact. Its job is to make an overrun VISIBLE and
    attributable, exactly as `cycles_are_sized` does. The prevention half lives in CLAUDE.md, at the
    line that grants standing authorisation to spawn — which is where the number has to be readable,
    because that is the moment the decision is made.

    ⚠ A receipt with no `subagents` block is UNMEASURED, never green. Otherwise the cheapest way to a
    clean board is to stop recording dispatches, and a gate whose easiest defeat is omitting data is
    a gate that measures compliance with itself (CLAUDE.md §4).
    """
    key = "fanout_is_governed"
    label = "did any cycle fan out wider than the governed cap?"
    source = "receipts' `subagents.max_concurrent`, against autonomy-state.json `subagent_width`"
    if not isinstance(state, dict):
        return _unmeasured(key, label, source, "STATE-UNREADABLE",
                           f"{state_err or 'autonomy-state.json is unreadable'}, so the cap is "
                           "unknown and no verdict is possible.")
    cap = state.get("subagent_width")
    if not isinstance(cap, int) or cap < 1:
        return _unmeasured(key, label, source, "NO-CAP",
                           f"`subagent_width`={cap!r} is not a positive integer, so there is nothing "
                           "to check against.")

    measured, unrecorded = [], []
    for r in receipts or []:
        cid = r.get("cycle_id") or "?"
        block = r.get("subagents")
        width = block.get("max_concurrent") if isinstance(block, dict) else None
        if not isinstance(width, int) or width < 0:
            unrecorded.append(cid)
        else:
            measured.append((cid, width))

    payload = {"cap": cap, "measured": dict(measured) or None,
               "receipts_not_recording_dispatch": unrecorded or None,
               "worst": max((w for _, w in measured), default=None)}
    over = [(c, w) for c, w in measured if w > cap]
    if over:
        c, w = max(over, key=lambda cw: cw[1])
        return _red(key, label, source, "FANOUT-OVER-CAP",
                    f"{c} dispatched {w} concurrent subagents against a cap of {cap}. Width is the "
                    "dial §9 records as having failed catastrophically: a 107-agent fan-out lost 67 "
                    "agents and its synthesis to the weekly limit. Lower it, or move `backoff_level` "
                    "— never widen the cap to fit what was already spent.", payload)
    if not measured:
        return _unmeasured(key, label, source, "DISPATCH-NOT-RECORDED",
                           f"{len(unrecorded)} receipt(s) record no `subagents` block "
                           f"({', '.join(unrecorded[:5])}), so what was dispatched is unknown. An "
                           "absent record is not a record of restraint.", payload)
    return _green(key, label, source, "WITHIN-CAP",
                  f"{len(measured)} cycle(s) recorded a fan-out; the widest was "
                  f"{payload['worst']} against a cap of {cap}.", payload)


def c_budget_recovering(state, state_err, now):
    """Red when `backoff_level` has been > 0 for more than 24 h — §9's stuck-loop row.

    ⛔ A raised backoff with no `backoff_since_utc` is unmeasured: the level is readable, the DURATION
    is not, and the whole condition is a duration. The governor writes that stamp when it raises the
    level (§9.1 — it backs off on an OBSERVED signal, so it knows when it observed it).

    ⚠ Level 0 is a MEASURED green, not a vacuous one: the file exists and says the loop is not in
    backoff. That is a reading, and it is the difference between this row and an absent state file.
    """
    key, label = "budget_recovering", "is the budget governor RECOVERING, or stuck in backoff?"
    source = "research/autonomy/autonomy-state.json `backoff_level`/`backoff_since_utc`"
    if not isinstance(state, dict):
        return _unmeasured(key, label, source, "STATE-UNREADABLE", f"{state_err}.")
    level = state.get("backoff_level")
    if not isinstance(level, int) or isinstance(level, bool) or level < 0:
        return _unmeasured(key, label, source, "LEVEL-UNREADABLE",
                           f"`backoff_level` is {level!r}, not a non-negative integer, so the budget "
                           f"posture cannot be read.")
    if level == 0:
        return _green(key, label, source, "NO-BACKOFF",
                      "the governor records backoff level 0 — the loop is running at full cadence and "
                      "width.", {"backoff_level": 0})
    since = _parse_ts(state.get("backoff_since_utc"))
    if since is None:
        return _unmeasured(key, label, source, "BACKOFF-AGE-UNKNOWN",
                           f"backoff level is {level} but `backoff_since_utc` is absent or unreadable, "
                           f"so HOW LONG it has been raised is unknown — and the condition is entirely "
                           f"a duration. Settle it: the governor stamps `backoff_since_utc` in the same "
                           f"write that raises the level.", {"backoff_level": level})
    held_h = _hours(now, since)
    payload = {"backoff_level": level, "backoff_since_et": _et(since), "held_h": round(held_h, 2),
               "grace_h": BACKOFF_GRACE_H, "last_limit_flip": state.get("last_limit_flip")}
    if held_h > BACKOFF_GRACE_H:
        return _red(key, label, source, "STUCK",
                    f"backoff has been at level {level} for {held_h:.1f} h (> {BACKOFF_GRACE_H:g} h). A "
                    f"limit that never clears is a stuck loop, not a busy one — §9.1 makes the reset a "
                    f"timestamp (`rate_limit_info.resetsAt`), so read it rather than waiting blind.",
                    payload)
    return _green(key, label, source, "BACKING-OFF",
                  f"backoff is at level {level}, raised {held_h:.1f} h ago and inside the "
                  f"{BACKOFF_GRACE_H:g} h grace — degrading, which is the design working (§9 property 4).",
                  payload)


def c_gates_green(gates, gates_err, now):
    """Red when preflight has been red on `main` for > 24 h — a red trunk stops every cycle at step 8.

    ⛔ THIS MODULE CANNOT MEASURE IT ITSELF and does not pretend to: the gate verdict lives in GitHub
    Actions, and this file is stdlib-only with no network by design (it must keep working when
    everything else has stopped). So the verdict is supplied as a FILE by the caller that does have the
    network — `autonomy-tick.yml`, the same shape `alarm_state.py` takes `--fleet-verdict` in. Absent
    file, absent reading: `unmeasured`, never green.

    ⚠ ONE ASYMMETRY, DELIBERATE. If the verdict says main is red RIGHT NOW but carries no
    `red_since_utc`, this reports RED rather than unmeasured. The failure itself was measured; only its
    age was not, and reporting a measured failure early is the fail-loud direction. That is the
    opposite call from `budget_recovering` above, where the LEVEL alone is not a failure at all.
    """
    key, label = "gates_green", "is `main` green, so a cycle can even commit?"
    source = "--gates-verdict (written by the workflow that can read Actions)"
    if not isinstance(gates, dict):
        return _unmeasured(key, label, source, "NO-GATE-VERDICT",
                           f"{gates_err or 'no gate verdict was supplied'}. This checker has no network "
                           f"by design, so it cannot read Actions itself. Settle it: have the tick "
                           f"workflow write {{\"ok\": bool, \"red_since_utc\": str|null, \"detail\": "
                           f"str}} and pass it with --gates-verdict.")
    ok = gates.get("ok")
    if not isinstance(ok, bool):
        return _unmeasured(key, label, source, "GATE-VERDICT-UNREADABLE",
                           f"the gate verdict carries `ok`={ok!r}, not a boolean, so it says nothing "
                           f"about the trunk.", {"raw": gates.get("detail")})
    if ok:
        return _green(key, label, source, "GREEN", gates.get("detail") or "the trunk is green.",
                      {"checked_et": gates.get("checked_et"), "ref": gates.get("ref")})
    since = _parse_ts(gates.get("red_since_utc"))
    detail = gates.get("detail") or "the trunk is red."
    if since is None:
        return _red(key, label, source, "RED",
                    f"{detail} How long it has been red is not recorded, so it is reported now rather "
                    f"than waiting out a {GATES_RED_GRACE_H:g} h deadline that cannot be measured — a "
                    f"red trunk stops every cycle at §4.2 step 8.", {"ref": gates.get("ref")})
    held_h = _hours(now, since)
    payload = {"red_since_et": _et(since), "held_h": round(held_h, 2), "grace_h": GATES_RED_GRACE_H,
               "ref": gates.get("ref")}
    if held_h > GATES_RED_GRACE_H:
        return _red(key, label, source, "RED-STUCK",
                    f"{detail} Red for {held_h:.1f} h (> {GATES_RED_GRACE_H:g} h) — every cycle since "
                    f"has been unable to commit.", payload)
    return _green(key, label, source, "RED-BUT-FRESH",
                  f"{detail} Red for {held_h:.1f} h, inside the {GATES_RED_GRACE_H:g} h grace — the "
                  f"next cycle is expected to fix it, and this row goes red if it does not.", payload)


def c_authority_respected(receipts, authority, authority_err):
    """Red on any outward act with no matching grant — §6.3, the one permission the loop cannot self-grant.

    An outward act is anything a receipt records under `outward_acts[]`: `{"venue": ..., "act": ...}`.
    A grant matches when `publication-authority.json` gives that venue `standing_grant: true` AND lists
    the act in `scope.acts`. `journal.standing_grant` is a constant false — not a parameter, not
    reachable by any bar — so a journal submission never matches and always shows here.

    ⛔ THE ABSENT-FILE CASE IS SPLIT, AND THE SPLIT IS THE POINT:
      no authority file AND no acts recorded  → `unmeasured`. There is nothing to check against, and no
        evidence the loop even logs acts. Green here would mean "we found no violations" when what
        happened is that nobody looked.
      no authority file BUT acts recorded     → RED, immediately. An outward act taken when no authority
        record exists at all is the exact failure CLAUDE.md §3 is written against, and its absence of a
        grant is not an absence of a reading — it is the reading.
    """
    key, label = "authority_respected", "did every OUTWARD act have a grant behind it?"
    source = "receipts `outward_acts[]` × research/autonomy/publication-authority.json"
    acts = []
    for r in receipts:
        for a in (r.get("outward_acts") or []):
            acts.append((r["_file"], a))
    have_authority = isinstance(authority, dict)
    if not have_authority and not acts:
        return _unmeasured(key, label, source, "NO-AUTHORITY-RECORD",
                           f"{authority_err or 'publication-authority.json is absent'}, and no receipt "
                           f"records an outward act. Nothing was checked, which is NOT the same as "
                           f"nothing being wrong: it is equally consistent with receipts that never log "
                           f"acts. Settle it: land §6.3's authority file (a rule change trimcrae makes, "
                           f"in the same commit as AGENTS.md and CLAUDE.md §3), and have receipts write "
                           f"`outward_acts[]` even when empty.",
                           {"receipts_seen": len(receipts)})
    ungranted = []
    for fname, act in acts:
        if not isinstance(act, dict):
            ungranted.append({"receipt": fname, "act": repr(act), "why": "act is not an object"})
            continue
        venue = str(act.get("venue") or act.get("target") or "").strip().lower()
        kind = str(act.get("act") or act.get("kind") or "").strip().lower()
        if not have_authority:
            ungranted.append({"receipt": fname, "venue": venue, "act": kind,
                              "why": "no authority file exists at all"})
            continue
        grant = authority.get(venue)
        if not isinstance(grant, dict) or grant.get("standing_grant") is not True:
            ungranted.append({"receipt": fname, "venue": venue, "act": kind,
                              "why": f"no standing grant for venue {venue!r}"})
            continue
        allowed = [str(x).strip().lower() for x in ((grant.get("scope") or {}).get("acts") or [])]
        if kind not in allowed:
            ungranted.append({"receipt": fname, "venue": venue, "act": kind,
                              "why": f"act {kind!r} is not in scope.acts {allowed}"})
    payload = {"acts_seen": len(acts), "ungranted": ungranted or None,
               "authority_file": "present" if have_authority else "absent"}
    if ungranted:
        return _red(key, label, source, "UNGRANTED-ACT",
                    f"{len(ungranted)} outward act(s) have no matching grant: {ungranted}. This is the "
                    f"one thing the loop may never grant itself (§6.3) — being blocked is not "
                    f"authorisation (CLAUDE.md §3).", payload)
    if not acts:
        return _green(key, label, source, "NO-OUTWARD-ACTS",
                      "the authority file is present and no receipt records an outward act, so nothing "
                      "went out unauthorised.", payload)
    return _green(key, label, source, "GRANTED",
                  f"all {len(acts)} outward act(s) match a standing grant in "
                  f"publication-authority.json.", payload)


# ═════════════════════════════════════════════════════════════════════ merge with the committed board
def merge(previous, conditions, now):
    """Carry each condition's history forward. State lives IN the artifact — there is no side store.

    Lifted from `alarm_state.merge` and kept deliberately identical in shape, because the two boards
    are read by the same person in the same way. Three things survive a run: WHEN a condition first
    went bad, HOW MANY consecutive runs have seen it, and WHEN its verdict last changed.

    ⚠ `unmeasured` rows count as bad here — that is what makes "unmeasured for six runs" visible, which
    is a different and often worse story than "unmeasured once".

    ⛔ Unlike `alarm_state`, a condition CANNOT vanish: the seven keys are fixed by §5.2 and every run
    emits all seven, so there is no carry-over-a-missing-source case. A key going missing would be a
    code defect, and `test_autonomy_health.py` asserts all seven are present.
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
            c["bad_since_utc"] = (_z(now) if (p.get("ok", True) or not p.get("bad_since_utc"))
                                  else p["bad_since_utc"])
            c["consecutive_bad_runs"] = 1 if p.get("ok", True) else int(p.get("consecutive_bad_runs", 0)) + 1
        since = _parse_ts(c["bad_since_utc"] or "")
        c["bad_for_h"] = round(_hours(now, since), 2) if since else None
        c["bad_since_et"] = _et(since)
    return conditions


def commit_worthy(previous, board, interval_h, now):
    """`(bool, why)` — does this board SAY anything the committed one did not? `fleet_armed.py`'s rule.

    ⛔ NO WORK, NO COMMIT. Measured cost of ignoring it: 1,476 commits to `main` in 24 h, 703 of which
    said in their own subject line that they did nothing. A board whose seven verdicts are unchanged
    carries no information, and committing it re-times the file for nothing.

    ⭐ AND THE OTHER HALF OF THAT LESSON, WHICH IS THE HALF THAT GETS DROPPED: a checker that goes quiet
    must not read as a checker that keeps saying "fine". The committed board carries its own expiry, so
    it is refreshed whenever it is within one cycle period of that expiry — the keep-alive, exactly as
    `fleet_armed._census_lane_state` refreshes a published census before it ages out. It can therefore
    never be the reason the board looks dead.
    """
    if not isinstance(previous, dict) or not previous.get("conditions"):
        return True, "no committed board exists yet"
    def surface(b):
        return sorted((c.get("key"), c.get("verdict"), bool(c.get("ok")), bool(c.get("unmeasured")))
                      for c in b.get("conditions", []))
    if surface(previous) != surface(board):
        return True, "a verdict changed"
    expiry = _parse_ts(previous.get("_stale_after_utc") or "")
    if expiry is None:
        return True, "the committed board has no readable expiry, so it cannot be trusted to stay alive"
    period = interval_h if interval_h is not None else FALLBACK_CYCLE_INTERVAL_H
    if now + datetime.timedelta(hours=period) >= expiry:
        return True, (f"keep-alive — the committed board expires {_et(expiry)}, inside one cycle period "
                      f"({period:g} h), and a frozen board must not read as a board that keeps saying fine")
    return False, ("every verdict is unchanged and the committed board is not near its expiry — this run "
                   "carries no information the last one did not")


def build(*, ledger_path=DEFAULT_LEDGER, state_path=DEFAULT_STATE, receipts_dir=DEFAULT_RECEIPTS,
          authority_path=DEFAULT_AUTHORITY, gates_path=None, health_path=DEFAULT_HEALTH, now=None,
          previous=None):
    """The whole board. Pure function of the files it is pointed at plus `now` — no hidden inputs."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    ledger, ledger_err = _read_json(ledger_path)
    state, state_err = _read_json(state_path)
    authority, authority_err = _read_json(authority_path)
    gates, gates_err = (_read_json(gates_path) if gates_path else (None, None))
    receipts, unreadable = load_receipts(receipts_dir)
    entries = ledger.get("entries") if isinstance(ledger, dict) else None
    if entries is not None and not isinstance(entries, list):
        entries, ledger_err = None, f"{os.path.basename(ledger_path)} carries a non-list `entries`"
    if isinstance(ledger, dict) and entries is None and not ledger_err:
        ledger_err = f"{os.path.basename(ledger_path)} carries no `entries`"
    interval_h, interval_basis = cycle_interval_hours(state)

    conditions = [
        c_cycle_delivering(receipts, unreadable, interval_h, now),
        c_advancing_live_work(receipts, now),
        c_evidence_moving(entries, ledger_err, interval_h, now),
        c_blocks_are_real(entries, ledger_err),
        c_queue_is_takeable(entries, ledger_err),
        c_cycles_are_sized(receipts, state, state_err),
        c_fanout_is_governed(receipts, state, state_err),
        c_budget_recovering(state, state_err, now),
        c_gates_green(gates, gates_err, now),
        c_authority_respected(receipts, authority, authority_err),
    ]
    if previous is None:
        previous, _ = _read_json(health_path)
    conditions = merge(previous, conditions, now)

    period = interval_h if interval_h is not None else FALLBACK_CYCLE_INTERVAL_H
    stale_after = now + datetime.timedelta(hours=STALE_AFTER_CYCLES * period)
    attention = [c["key"] for c in conditions if c["needs_attention"]]
    unmeasured_keys = [c["key"] for c in conditions if c["unmeasured"]]
    board = {
        "_what": "THE AUTONOMY LOOP'S HEALTH BOARD, AS A FILE. The ten §5.2 conditions, when each was "
                 "measured, how long it has been that way, and when this file should be considered "
                 "dead. Written by research/autonomy/health.py.",
        "_read_this_when": "you want to know whether the unattended research loop is WORKING — not "
                           "whether what it wrote is correct, which every preflight gate already covers "
                           "(§5.1). A loop can be perfectly correct and advance nothing.",
        "_owner": "research/manuscripts/program/emc-autonomy-architecture.md#52--loop-health--new-and-it-"
                  "is-what-never-check-in-actually-requires",
        "_this_channel_is_PULL_ONLY": "nothing here sends, opens an issue, comments, or fails a run. §7 "
                                      "trigger 4 is the ONE push, and it is the caller's act, not this "
                                      "file's: a condition red past its deadline earns a "
                                      "PushNotification and a line in the Friday digest, nothing else.",
        "_generated_utc": _z(now), "_generated_et": _et(now),
        "_cycle_interval_h": interval_h,
        "_stale_window_basis": interval_basis,
        "_stale_after_utc": _z(stale_after), "_stale_after_et": _et(stale_after),
        "_stale_after_means": (
            f"IF THE CLOCK IS PAST THIS AND THIS FILE HAS NOT CHANGED, NOTHING IS CHECKING THE LOOP and "
            f"every verdict below is a memory, not a measurement. The deadline is written INTO the "
            f"artifact because a checker that has stopped cannot report that it stopped — it needs no "
            f"process, no API and no clock but yours. {STALE_AFTER_CYCLES:g} missed cycles at "
            f"{period:g} h. Restart it: `gh workflow run autonomy-tick.yml --ref main`."),
        "ok": not attention,
        "_ok_means": (
            "no condition is FAILING. ⛔ IT DOES NOT MEAN EVERY CONDITION WAS MEASURED — read "
            "`fully_measured` and `unmeasured` beside it. `ok: true, fully_measured: false` is the "
            "honest shape of a loop nobody can yet grade, and it is NOT a healthy loop."),
        "fully_measured": not unmeasured_keys,
        "n_conditions": len(conditions),
        "needs_attention": attention,
        "unmeasured": unmeasured_keys,
        "_unmeasured_means": (
            "⛔ A VERDICT THAT COULD NOT BE REACHED — NOT a condition that is fine. It is listed apart "
            "from needs_attention because the fix is different: make the reading possible first. "
            "CLAUDE.md §4: an absent reading is not a reading of absence. Anything that grades an "
            "unmeasured condition as green has manufactured a green board out of missing data."),
        "conditions": sorted(conditions, key=lambda c: (c["ok"], CONDITION_ORDER.index(c["key"]))),
    }
    if unreadable:
        board["_receipts_unreadable"] = unreadable
        board["_receipts_unreadable_means"] = (
            "a receipt file exists and would not parse. It is NOT counted as a delivered cycle and NOT "
            "silently skipped — a corrupt receipt is a broken writer, not a quiet loop.")
    worth, why = commit_worthy(previous, board, interval_h, now)
    board["_commit_worthy"] = worth
    board["_commit_worthy_why"] = why
    board["_commit_worthy_means"] = (
        "fleet_armed.py's discipline: the caller COMMITS this file only when this is true. A board "
        "whose verdicts are unchanged carries no information (measured cost of ignoring that: 1,476 "
        "commits in 24 h, 703 of them non-events), and the keep-alive clause makes sure a live checker "
        "can never be the reason the board looks dead.")
    return board


# ═════════════════════════════════════════════════════════════════════════════════════════════ render
_GLYPH = {True: "✅", False: "⛔"}


def render(board, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    stale_after = _parse_ts(board.get("_stale_after_utc") or "")
    dead = stale_after is not None and now > stale_after
    lines = [
        f"[loop-health] generated {board.get('_generated_et')} · this file goes stale after "
        f"{board.get('_stale_after_et')}"
        + ("   ⛔ AND IT IS PAST THAT — NOTHING IS CHECKING THE LOOP" if dead else ""),
        f"[loop-health] cycle period: {board.get('_stale_window_basis')}",
        "[loop-health] PULL ONLY — nothing was sent, no issue opened, no run failed.",
    ]
    for c in board.get("conditions", []):
        glyph = "🔎" if c["unmeasured"] else _GLYPH[c["ok"]]
        age = (f" · bad for {c['bad_for_h']:.1f} h ({c['consecutive_bad_runs']} run(s))"
               if c.get("bad_for_h") else "")
        lines.append(f"[loop-health] {glyph} {c['key']:<21} {c['verdict']:<24} {c['label']}{age}")
        if not c["ok"]:
            lines.append(f"[loop-health]      {c['detail']}")
    att, unm = board.get("needs_attention", []), board.get("unmeasured", [])
    lines.append(f"[loop-health] {len(att)} need attention {att or ''} · {len(unm)} UNMEASURED "
                 f"{unm or ''} — unmeasured is not ok · {board.get('n_conditions')} condition(s)")
    lines.append(f"[loop-health] commit-worthy: {board.get('_commit_worthy')} — "
                 f"{board.get('_commit_worthy_why')}")
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════════════════════════════ cli
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    ap.add_argument("--state", default=DEFAULT_STATE)
    ap.add_argument("--receipts", default=DEFAULT_RECEIPTS)
    ap.add_argument("--authority", default=DEFAULT_AUTHORITY)
    ap.add_argument("--gates-verdict", default=None,
                    help="JSON written by the caller that CAN read Actions; absent = gates_green is "
                         "unmeasured, never green")
    ap.add_argument("--health", default=DEFAULT_HEALTH, help="the committed board; read for history")
    ap.add_argument("--write", action="store_true", help="persist the board (otherwise print only)")
    ap.add_argument("--commit-worthy", action="store_true",
                    help="exit 0 if this board says something the committed one did not, 10 if not. "
                         "For autonomy-tick.yml's no-work-no-commit step — 10 rather than 1 because "
                         "'nothing to say' is the rule working, not a failure")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any condition needs attention (unmeasured does NOT exit 1 — it is "
                         "not a failing loop, it is an unreadable one, and the fix is different)")
    a = ap.parse_args(argv)

    now = datetime.datetime.now(datetime.timezone.utc)
    board = build(ledger_path=a.ledger, state_path=a.state, receipts_dir=a.receipts,
                  authority_path=a.authority, gates_path=a.gates_verdict, health_path=a.health, now=now)
    print(render(board, now))
    if a.write:
        with open(a.health, "w", encoding="utf-8") as fh:
            json.dump(board, fh, indent=2)
            fh.write("\n")
        print(f"[loop-health] wrote {a.health}")
    if a.commit_worthy:
        # ⭐ Exposes `commit_worthy()` to a shell caller so `autonomy-tick.yml` obeys the no-work-no-commit
        # rule by ASKING this module rather than reimplementing its four-argument plumbing in YAML — a
        # second copy of that logic is exactly the drift `fleet_armed.py` was consolidated to end.
        # Exit 10, not 1: "nothing to say" is the rule working, and must not render like a failure.
        previous, _ = _read_json(a.health)
        state, _ = _read_json(a.state)
        interval_h, _ = cycle_interval_hours(state)
        worth, why = commit_worthy(previous or {}, board, interval_h, now)
        print(f"[loop-health] commit-worthy: {worth} — {why}")
        return 0 if worth else 10
    if a.check:
        # ⚠ The ONLY non-zero path in this module. Everything else exits 0 on purpose: a red run is a
        # push channel (GitHub mails the repo owner), and reintroducing that is what alarm_state.py's
        # whole design removed. A caller that wants the gate asks for it.
        return 1 if board["needs_attention"] else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
