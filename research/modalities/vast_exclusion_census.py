#!/usr/bin/env python3
"""WHAT THE EXCLUSION SET IS ACTUALLY MADE OF, AND WHAT RE-ADMITTING PART OF IT WOULD BUY.

★ THE MEASUREMENT `vast_machine_blacklist.__doc__` ASKED FOR, AND THE TRIGGER THAT CAME DUE.

That module parks a re-test policy explicitly — *"Revisit with a measured re-test policy when the set is
large enough to matter against the ~23-host board"* — and names the symptom that would say the time has
come: 38 machines excluded against a 152-offer board, **4 of 5 authorised placements failing with
`no rentable verified offer`**. At 9:05 PM ET on 2026-07-27 the set stood at 48 and **2 of 2** authorised
placements failed the same way, on a 189-offer board, with the gate having cleared both units on price
(1.67x and 1.80x basis, comfortably under the buy line). Zero hosts were rented and price was not the
reason: the lane was strangling its own supply.

The trigger is a symptom, not a policy. A policy needs three numbers this module produces and nothing else
in the repo does:

  1. **COMPOSITION** — how many entries are `resources_unavailable` (a claim about a MOMENT: "this
     machine's GPU was taken at 8:12 PM") versus never-starts / container failures (a claim about the
     HOST) versus lane-scoped throughput verdicts. These are different claims and must not share a
     policy; conflating them is how the set came to grow without bound.
  2. **LIVE OVERLAP** — how many excluded machines are RIGHT NOW advertising a rentable verified offer
     that meets the lane's own `ResourceSpec`. An entry whose machine is not on the board costs us
     nothing; an entry whose machine is on the board, priced under the buy line, and excluded anyway is
     the capacity we are refusing ourselves.
  3. **THE COUNTERFACTUAL** — how many more units this tick's board could have placed if capacity-class
     entries older than X hours had been re-admitted, for several X. That number is the entire case for
     (or against) doing anything, and it is the one thing an argument cannot supply.

★★ WHY AGE IS A LEGITIMATE AXIS **HERE** AND A GUESSED TTL IS STILL FORBIDDEN. `vast_machine_blacklist`
refuses a TTL because *"a guessed TTL would silently re-admit the hosts this exists to refuse"* — and it
is right, for the claim it is mostly about. "This container never executes" does not become false with
time. But `resources_unavailable` is a statement about an INSTANT of a rental market, and treating an
instant as a durable property of a host is a category error that can only ever accumulate. So age is used
here as a **screen on one reason class**, never as a withdrawal, and its cut-off is chosen from the
counterfactual below rather than picked — which is exactly the difference between a measurement and a
guess.

⚠ THIS MODULE RENTS NOTHING AND WRITES NOTHING TO THE EXCLUSION SETS. It is a read: S3 for the sets, one
Vast board read for the offers. $0. The policy it feeds lives in `vast_machine_blacklist.retest_*`.

USAGE
    python3 vast_exclusion_census.py [--bucket B] [--units N] [--out PATH]
    python3 vast_exclusion_census.py --offers-json FILE --sets-json FILE      # offline, for tests
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import congeneric_fanout as _cf              # noqa: E402
import vast_machine_blacklist as _vmb        # noqa: E402
from gpu_backend import rank_offers_by_usd_per_ns  # noqa: E402

#: The ages, in hours, the counterfactual is evaluated at. Deliberately spanning "minutes ago" to "a day
#: ago" so the answer is a CURVE and not a single number somebody has to trust. `0` re-admits every
#: capacity-class entry regardless of age and is the UPPER BOUND on what any age policy could buy — if
#: that column is zero, no cut-off is worth having and the whole change is refuted.
DEFAULT_AGE_CUTOFFS_H = (0.0, 1.0, 3.0, 6.0, 12.0, 24.0, 48.0)

OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vast-exclusion-census.json")


# =============================================================================================================
# reason classification — PURE
# =============================================================================================================
#: A refusal that names Vast's capacity error. This is the ONLY class the re-test policy may touch, because
#: it is the only recorded claim that is about a moment rather than about the host. `resources_unavailable`
#: is the provider's own response string; `no free gpu` / `has no free GPU` is how `ternary_vast_launch`
#: phrases the same observation in its log line.
CAPACITY_MARKERS = ("resources_unavailable", "no free gpu", "no free_gpu", "capacity refusal",
                    "no rentable", "gpu is already taken", "gpu was taken")

#: A claim about the HOST that starting-again does not weaken with time: the container never executed, the
#: box crash-loops, the machine cannot be reached. Left strictly alone by the re-test policy.
HOST_FAULT_MARKERS = ("never started", "never executed", "never reached running", "crash-loop", "crashloop",
                      "create/start race", "unreachable", "cannot be reached", "container never")

#: A verdict about the machine PAIRED WITH A WORKLOAD — the sustained-`gpu_util` shortfall. `pricing.md` A.1
#: withdrew the broad version of this rule once already; it is lane-scoped, never shared, and never re-tested
#: from here.
THROUGHPUT_MARKERS = ("starv", "gpu_util", "utilisation", "utilization", "shortfall", "slower than its card")

CAPACITY = "capacity"
HOST_FAULT = "host_fault"
THROUGHPUT = "throughput"
UNKNOWN = "unknown"


def classify_reason(why):
    """Which CLAIM does this recorded reason make? PURE.

    ⚠ ORDER IS LOAD-BEARING AND THE STRICT DIRECTION IS FIRST-WINS ON THE **DURABLE** CLASSES. A reason
    that names a host fault is a host fault even if it also happens to quote the capacity error, because
    the re-test policy may only act on entries whose ENTIRE claim is about a moment. Getting this backwards
    would re-admit exactly the hosts the set exists to refuse — the failure mode
    `vast_machine_blacklist.__doc__` refuses a TTL to avoid.

    ⚠ AND A BACKFILLED ENTRY IS **NOT** CAPACITY. `vast_machine_blacklist.backfill` writes
    "backfilled from <lane>'s refuse-to-start list" for ids promoted out of a lane's bare id list — there is
    no per-id reason behind them at all, only the list's construction. `refuse` lands them in HOST_FAULT
    here, which is the conservative direction: an entry we cannot read the claim of is not one we may
    re-admit on an age screen.
    """
    w = str(why or "").lower()
    if any(m in w for m in THROUGHPUT_MARKERS):
        return THROUGHPUT
    if any(m in w for m in HOST_FAULT_MARKERS) or "refuse" in w:
        return HOST_FAULT
    if any(m in w for m in CAPACITY_MARKERS):
        return CAPACITY
    return UNKNOWN


def _parse_utc(s):
    """Seconds since epoch for a '%Y-%m-%dT%H:%M:%SZ' stamp, or None. PURE-ish (no clock read)."""
    try:
        return time.mktime(time.strptime(str(s), "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    except (TypeError, ValueError):
        return None


def fold_history(doc, machine_ids=None, source=""):
    """{machine_id: record} folded from an exclusion document's history. PURE.

    A record carries every LIVE reason for the machine (withdrawals drop the reasons they retract), the
    lanes that recorded them, the most recent recording time, and the machine's overall class.

    ★ THE CLASS OF A MACHINE IS THE STRICTEST CLASS AMONG ITS LIVE REASONS, not the latest one. A machine
    excluded once for a capacity refusal and once as a never-start is a never-start: the durable claim
    survives the momentary one, and only a machine whose ENTIRE live record is momentary may be re-tested.

    An id present in `machine_ids` with NO history at all (the shape `ternary_vast_launch._blocked_machines`
    has by construction, and the shape a hand-seeded id has) is recorded as `UNKNOWN` with no timestamp —
    it is not re-testable, and the census counts it so the unreadable fraction is visible rather than
    quietly folded into whatever class happens to be biggest.
    """
    ids = {str(m) for m in (machine_ids if machine_ids is not None else (doc or {}).get("machine_ids") or [])}
    recs = {mid: {"machine_id": mid, "source": source, "reasons": [], "lanes": [], "classes": [],
                  "last_utc": None, "first_utc": None, "withdrawals": 0} for mid in ids}
    for h in ((doc or {}).get("history") or []):
        mid = str(h.get("machine_id"))
        if mid not in recs:
            continue
        r = recs[mid]
        why = str(h.get("why") or "")
        if h.get("action") == "withdraw" or why.upper().startswith("WITHDRAWN"):
            # A withdrawal retracts what came before it; the entry is only back on the list because
            # something was recorded AFTER it. Dropping the prior reasons is what keeps a stale, already-
            # refuted verdict from pinning a machine into HOST_FAULT for ever.
            r.update({"reasons": [], "lanes": [], "classes": [], "first_utc": None})
            r["withdrawals"] += 1
            continue
        r["reasons"].append(why[:200])
        r["classes"].append(classify_reason(why))
        if h.get("lane"):
            r["lanes"].append(str(h.get("lane")))
        t = _parse_utc(h.get("utc"))
        if t is not None:
            r["last_utc"] = h.get("utc") if r["last_utc"] is None else max(
                [r["last_utc"], h.get("utc")], key=lambda s: _parse_utc(s) or 0)
            r["first_utc"] = h.get("utc") if r["first_utc"] is None else min(
                [r["first_utc"], h.get("utc")], key=lambda s: _parse_utc(s) or 0)
    for r in recs.values():
        cls = set(r["classes"])
        if not cls:
            r["class"] = UNKNOWN
        elif cls == {CAPACITY}:
            r["class"] = CAPACITY
        elif THROUGHPUT in cls and not (cls - {THROUGHPUT, CAPACITY}):
            r["class"] = THROUGHPUT
        elif HOST_FAULT in cls:
            r["class"] = HOST_FAULT
        else:
            r["class"] = UNKNOWN
        r["lanes"] = sorted(set(r["lanes"]))
    return recs


#: Strictness order for merging one machine's class across several sets. HOST_FAULT beats THROUGHPUT beats
#: CAPACITY, because a durable claim survives a momentary one and only a machine whose ENTIRE live record is
#: momentary may be re-tested.
#:
#: ⚠⚠ `UNKNOWN` RANKS **BELOW** EVERY REAL CLASS, AND THE FIRST DRAFT HAD IT ABOVE — WHICH SILENTLY ATE THE
#: ENTIRE SIGNAL (measured, 2026-07-28 1:17 AM ET run). `ternary_vast_launch` keeps its blocked ids as a BARE
#: LIST with no history at all, so folding that set produces 32 machines classified `UNKNOWN` — not because
#: anything unknown was observed, but because that file has no room to record a reason. Ranking UNKNOWN as
#: "stricter" then overwrote the shared set's perfectly explicit `resources_unavailable on start` for every id
#: the two sets share: the first census reported **0 capacity-class entries out of 48** while nineteen of them
#: carried that exact string and nothing else. UNKNOWN is the ABSENCE OF A CLAIM, not a stronger one. A
#: machine known only as UNKNOWN still stays excluded — `readmissible` takes CAPACITY only — so nothing is
#: loosened by this; what is fixed is that a set which cannot record reasons can no longer erase the reasons
#: a set that can record them did record.
_CLASS_RANK = {UNKNOWN: -1, CAPACITY: 0, THROUGHPUT: 1, HOST_FAULT: 2}


def merge_records(*record_maps):
    """Union of several folded sets, keeping the STRICTEST class per machine. PURE.

    The lane sets and the shared set overlap heavily (the shared one is seeded from them), and a machine
    that is a never-start on one lane's evidence must not become re-testable because another set happens to
    record only its capacity refusal."""
    rank = _CLASS_RANK
    out = {}
    for m in record_maps:
        for mid, r in (m or {}).items():
            cur = out.get(mid)
            if cur is None:
                out[mid] = dict(r, sources=[r.get("source", "")])
                continue
            cur["sources"] = sorted(set(cur["sources"]) | {r.get("source", "")})
            cur["reasons"] = (cur["reasons"] + r["reasons"])[:12]
            cur["lanes"] = sorted(set(cur["lanes"]) | set(r["lanes"]))
            if rank.get(r["class"], -1) > rank.get(cur["class"], -1):
                cur["class"] = r["class"]
            for k, pick in (("last_utc", max), ("first_utc", min)):
                a, b = cur.get(k), r.get(k)
                if a and b:
                    cur[k] = pick([a, b], key=lambda s: _parse_utc(s) or 0)
                else:
                    cur[k] = a or b
    return out


def age_hours(rec, now_utc=None):
    """Hours since the machine's MOST RECENT live exclusion reason, or None if it carries no timestamp. PURE.

    Measured from the LAST recording, not the first: the claim whose age matters is the newest one, and a
    machine re-condemned an hour ago is an hour-old claim however long it has been on the list."""
    t = _parse_utc(rec.get("last_utc"))
    if t is None:
        return None
    now = _parse_utc(now_utc) if now_utc else time.time()
    return max(0.0, (now - t) / 3600.0)


# =============================================================================================================
# live overlap + the counterfactual — PURE given a board
# =============================================================================================================
def board_machine_ids(offers, res):
    """(qualifying_ids, priceable_ids) among `offers`, with the spec's own exclusions IGNORED. PURE.

    "Currently advertising a rentable verified offer that meets the lane's ResourceSpec" is exactly what
    `rank_offers_by_usd_per_ns` decides, so it is asked rather than re-implemented — a second copy of that
    filter would be free to disagree with the one that actually rents, which is the defect
    `rank_offers_by_usd_per_ns` was extracted to prevent in the first place."""
    bare = dataclasses.replace(res, exclude_machine_ids=(), max_usd_per_ns=None)
    measured, capable = rank_offers_by_usd_per_ns(offers, bare)
    return ({str(o.get("machine_id")) for _p, o in capable},
            {str(o.get("machine_id")) for _u, _p, o in measured})


def placeable(offers, res, excluded, n_units, ceiling=None):
    """What this board would place for `n_units` given `excluded`. PURE.

    Delegates the ceiling to `congeneric_fanout.place_units`, which derives it from the approved absolute
    rate — no multiple is typed here or anywhere downstream of here (CLAUDE.md §1)."""
    res2 = dataclasses.replace(res, exclude_machine_ids=tuple(sorted(str(m) for m in excluded)),
                               max_usd_per_ns=None)
    measured, capable = rank_offers_by_usd_per_ns(offers, res2)
    ranked = [u for u, _p, _o in measured]
    cap = _cf.unit_usd_per_ns_ceiling() if ceiling is None else float(ceiling)
    n, placed, why = _cf.place_units(ranked, n_units, cap)
    return {"qualifying": len(capable), "priceable": len(measured),
            "clearing_the_buy_line": sum(1 for u in ranked if u <= cap),
            "placed": n, "cheapest_usd_per_ns": (round(ranked[0], 6) if ranked else None),
            "held_reason": why}


def readmissible(records, cutoff_h, now_utc=None):
    """The machine ids an age screen at `cutoff_h` would re-admit. PURE.

    CAPACITY class only, and an entry with NO timestamp is never re-admitted — an unreadable age cannot be
    shown to have passed, and this is the direction in which being wrong is free."""
    out = set()
    for mid, r in (records or {}).items():
        if r.get("class") != CAPACITY:
            continue
        a = age_hours(r, now_utc)
        if a is not None and a >= float(cutoff_h):
            out.add(str(mid))
    return out


def counterfactual(offers, res, excluded, records, n_units, cutoffs=DEFAULT_AGE_CUTOFFS_H, now_utc=None):
    """The table that decides the policy: placements at each age cut-off, against the do-nothing baseline.

    `gain` is the whole argument. If every row is 0, re-admission buys nothing on this board and the change
    is refuted by its own measurement rather than by an opinion."""
    excluded = {str(m) for m in (excluded or ())}
    base = placeable(offers, res, excluded, n_units)
    rows = []
    for x in cutoffs:
        re_ids = readmissible(records, x, now_utc)
        got = placeable(offers, res, excluded - re_ids, n_units)
        rows.append({"cutoff_h": x, "readmitted": len(re_ids),
                     "readmitted_ids": sorted(re_ids)[:40],
                     "placed": got["placed"], "gain_vs_baseline": got["placed"] - base["placed"],
                     "clearing_the_buy_line": got["clearing_the_buy_line"],
                     "cheapest_usd_per_ns": got["cheapest_usd_per_ns"]})
    # ★ THE UPPER BOUND, AND IT IS THE ROW THAT CAN KILL THE WHOLE CHANGE. Every excluded machine re-admitted,
    # reason class ignored — an exclusion policy cannot possibly buy more than this. If `gain_vs_baseline` is
    # 0 here then the exclusion set is NOT what is binding on this board, and any re-test policy tuned to
    # raise placements would be tuning against a constraint that is not the one holding.
    everything = placeable(offers, res, set(), n_units)
    return {"baseline": base,
            "upper_bound_readmit_everything": {
                "_what": "every excluded machine back on the board, class ignored — the ceiling on what ANY "
                         "exclusion policy could buy this tick",
                "readmitted": len(excluded),
                "placed": everything["placed"],
                "gain_vs_baseline": everything["placed"] - base["placed"],
                "clearing_the_buy_line": everything["clearing_the_buy_line"],
                "cheapest_usd_per_ns": everything["cheapest_usd_per_ns"]},
            "by_cutoff": rows}


def gate_vs_submit(offers, res, excluded, held_machine_ids, n_units):
    """The gap between what the market gate AUTHORISES and what `submit` can actually BUY. PURE.

    ★★ THE DISCRIMINATING OBSERVATION FOR THE 9:05 PM ET FAILURE, and it is not the one the log line
    suggested. `congeneric_fanout_vast.market_gate` prices the board against `_load_excluded()` ALONE, and
    then the wave loop hands `submit` a spec excluding `excluded ∪ the machines this lane is already renting
    ∪ the machines it rented earlier in this very wave`. Two different filters, one decision: the gate can
    therefore authorise N placements against offers that the renting path is structurally forbidden to take,
    and the readout will say `N unit(s) LAUNCHING NOW` while N submits fail.

    That is exactly the shape of the incident: `2 unit(s) LAUNCHING NOW` and `SUBMIT FAILED` twice, with the
    handler correctly reporting `53 machine(s) (48 excluded + 5 we already hold or just rented this wave)`.
    The 5 were invisible to the gate. So the census measures BOTH filters against the same board and reports
    the difference, because "the exclusion set has outgrown the market" and "the gate is pricing hosts the
    launcher may not buy" are different diagnoses with different fixes, and the log line conflated them.
    """
    excluded = {str(m) for m in (excluded or ())}
    held = {str(m) for m in (held_machine_ids or ())}
    gate = placeable(offers, res, excluded, n_units)
    submit = placeable(offers, res, excluded | held, n_units)
    return {"_what": "what market_gate prices (exclusions only) vs what submit may actually rent "
                     "(exclusions + hosts this lane already holds)",
            "n_excluded": len(excluded), "n_already_held": len(held),
            "held_machine_ids": sorted(held),
            "gate_authorises": gate["placed"], "submit_can_buy": submit["placed"],
            "phantom_placements": max(0, gate["placed"] - submit["placed"]),
            "gate_clearing_the_buy_line": gate["clearing_the_buy_line"],
            "submit_clearing_the_buy_line": submit["clearing_the_buy_line"]}


# =============================================================================================================
# the census
# =============================================================================================================
def compose(records, advertising_qualifying, advertising_priceable, now_utc=None):
    """Composition + age distribution + live overlap. PURE."""
    by_class, ages = {}, []
    for mid, r in records.items():
        c = r.get("class", UNKNOWN)
        b = by_class.setdefault(c, {"n": 0, "on_board_now": 0, "priceable_now": 0, "no_timestamp": 0,
                                    "ids": []})
        b["n"] += 1
        b["ids"].append(mid)
        if mid in advertising_qualifying:
            b["on_board_now"] += 1
        if mid in advertising_priceable:
            b["priceable_now"] += 1
        a = age_hours(r, now_utc)
        if a is None:
            b["no_timestamp"] += 1
        else:
            ages.append(a)
    for b in by_class.values():
        b["ids"] = sorted(b["ids"])[:60]
    ages.sort()

    def _pct(p):
        return round(ages[min(len(ages) - 1, int(p * len(ages)))], 2) if ages else None

    return {"n_excluded": len(records),
            "by_class": by_class,
            "age_hours": {"n_with_timestamp": len(ages), "min": (round(ages[0], 2) if ages else None),
                          "p25": _pct(0.25), "median": _pct(0.5), "p75": _pct(0.75),
                          "max": (round(ages[-1], 2) if ages else None)},
            "on_board_now": len(set(records) & set(advertising_qualifying)),
            "priceable_now": len(set(records) & set(advertising_priceable))}


def _sets_from_s3(bucket, s3=None):
    """[(source, doc, ids)] for the shared set and every lane set we can read. Never raises on a missing key."""
    import boto3
    s3 = s3 or boto3.client("s3")
    out = []
    shared_ids, shared_doc = _vmb.load(s3, bucket)
    out.append(("shared", shared_doc, shared_ids))
    for source, key in (("step1_fanout", "nr4a3-step1-fanout/results/_excluded_machines.json"),
                        ("rung5a_ks", "ternary-vast/_lane_state.json")):
        try:
            doc = json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
        except Exception:  # noqa: BLE001 — a lane that has never excluded anything has no key
            continue
        ids = doc.get("machine_ids") or doc.get("_blocked_machines") or []
        out.append((source, doc, [str(m) for m in ids]))
    return out


def census(bucket=None, units=None, offers=None, sets=None, res=None, key=None, now_utc=None,
           cutoffs=DEFAULT_AGE_CUTOFFS_H, held_machine_ids=None):
    """The whole measurement. `offers`/`sets` may be injected for an offline run; otherwise both are read."""
    import congeneric_fanout_vast as _cfv
    res = res or _cfv.FANOUT_RES
    units = int(units or _cf.fanout_width())
    if sets is None:
        sets = _sets_from_s3(bucket or os.environ.get("VAST_CKPT_BUCKET")
                             or "sagemaker-us-east-2-646605541856")
    folded = [fold_history(doc, ids, source) for source, doc, ids in sets]
    records = merge_records(*folded)
    api = key or os.environ.get("VAST_API_KEY")
    if offers is None:
        from gpu_backend import _vast_offer_query, _vast_request
        if not api:
            raise RuntimeError("no VAST_API_KEY — the board cannot be read, and a census without the live "
                               "board cannot answer the only question that decides the policy")
        offers = (_vast_request("GET", "/search/asks/", api,
                                params={"q": json.dumps(_vast_offer_query(res))}) or {}).get("offers", [])
    if held_machine_ids is None and api:
        # Best-effort: the machines this lane is ALREADY renting are the other half of the filter that
        # `submit` applies and the gate does not. A failure to read them degrades `gate_vs_submit` to
        # "exclusions only", never the whole census.
        try:
            held_machine_ids = [str(i.get("machine_id")) for i in _cfv._live_instances(api)
                                if i.get("machine_id") is not None]
        except Exception:  # noqa: BLE001
            held_machine_ids = []
    qual, priced = board_machine_ids(offers, res)
    basis = _cf.basis_usd_per_ns()
    ceiling = _cf.unit_usd_per_ns_ceiling()
    return {
        "_what": "Composition of the Vast exclusion sets, their live overlap with the board, and how many "
                 "more units an age screen on the CAPACITY class would have placed. Read-only, $0.",
        "_why": "vast_machine_blacklist.__doc__ parks a re-test policy 'when the set is large enough to "
                "matter against the ~23-host board' and asks for a measurement first. This is it.",
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) if now_utc is None else now_utc,
        "sets_read": [{"source": s, "n_ids": len(i)} for s, _d, i in sets],
        "board": {"offers_returned": len(offers), "qualifying": len(qual), "priceable": len(priced),
                  "units_wanted": units},
        "buy_line": {"usd_per_ns": round(ceiling, 6), "basis_usd_per_ns": round(basis, 6),
                     "x_basis": round(ceiling / basis, 3) if basis else None,
                     "_derived": "congeneric_fanout.unit_usd_per_ns_ceiling() — never typed (CLAUDE.md §1)"},
        "composition": compose(records, qual, priced, now_utc),
        "counterfactual": counterfactual(offers, res, set(records), records, units, cutoffs, now_utc),
        "gate_vs_submit": gate_vs_submit(offers, res, set(records), held_machine_ids or (), units),
        "per_machine": sorted(({"machine_id": mid, "class": r["class"], "lanes": r["lanes"],
                                "last_utc": r["last_utc"], "age_h": (round(age_hours(r, now_utc), 2)
                                                                     if age_hours(r, now_utc) is not None
                                                                     else None),
                                "on_board_now": mid in qual, "priceable_now": mid in priced,
                                "reasons": r["reasons"][:3]}
                               for mid, r in records.items()), key=lambda d: d["machine_id"]),
    }


def summarise(doc):
    """The three sentences a reader needs. Returns a list of lines."""
    c, b, cf = doc["composition"], doc["board"], doc["counterfactual"]
    lines = [f"[census] {c['n_excluded']} machine(s) excluded; board {b['offers_returned']} offers -> "
             f"{b['qualifying']} qualifying -> {b['priceable']} priceable; {c['on_board_now']} excluded "
             f"machine(s) are advertising a qualifying offer RIGHT NOW ({c['priceable_now']} priceable)."]
    for cls, v in sorted(c["by_class"].items()):
        lines.append(f"[census]   {cls:<11} n={v['n']:<4} on_board_now={v['on_board_now']:<4} "
                     f"priceable_now={v['priceable_now']:<4} no_timestamp={v['no_timestamp']}")
    lines.append(f"[census] baseline placements for {b['units_wanted']} unit(s): "
                 f"{cf['baseline']['placed']} ({cf['baseline']['clearing_the_buy_line']} of "
                 f"{cf['baseline']['priceable']} priceable offers clear the buy line; "
                 f"{cf['baseline']['held_reason'] or 'placed'})")
    ub = cf["upper_bound_readmit_everything"]
    lines.append(f"[census]   UPPER BOUND — re-admit ALL {ub['readmitted']} excluded machine(s), class "
                 f"ignored -> {ub['placed']} placed (gain {ub['gain_vs_baseline']:+d}). No exclusion policy "
                 f"can beat this row.")
    for r in cf["by_cutoff"]:
        lines.append(f"[census]   re-admit CAPACITY older than {r['cutoff_h']:>5.1f} h -> "
                     f"+{r['readmitted']} machine(s) back on the board -> {r['placed']} placed "
                     f"(gain {r['gain_vs_baseline']:+d})")
    g = doc.get("gate_vs_submit") or {}
    if g:
        lines.append(f"[census] GATE vs SUBMIT: the gate prices against {g['n_excluded']} exclusion(s) and "
                     f"authorises {g['gate_authorises']}; submit also excludes {g['n_already_held']} host(s) "
                     f"this lane already holds and can buy {g['submit_can_buy']} -> "
                     f"{g['phantom_placements']} PHANTOM placement(s) (authorised, unbuyable).")
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bucket", default=os.environ.get("VAST_CKPT_BUCKET"))
    ap.add_argument("--units", type=int, default=None)
    ap.add_argument("--out", default=OUT_JSON)
    ap.add_argument("--offers-json", default=None, help="offline: a saved /search/asks/ response")
    ap.add_argument("--sets-json", default=None, help="offline: [[source, doc, ids], ...]")
    a = ap.parse_args(argv)
    offers = sets = None
    if a.offers_json:
        raw = json.load(open(a.offers_json))
        offers = raw.get("offers", raw) if isinstance(raw, dict) else raw
    if a.sets_json:
        sets = [tuple(x) for x in json.load(open(a.sets_json))]
    doc = census(bucket=a.bucket, units=a.units, offers=offers, sets=sets)
    with open(a.out, "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=False)
    for line in summarise(doc):
        print(line, flush=True)
    print(f"[census] written to {a.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
