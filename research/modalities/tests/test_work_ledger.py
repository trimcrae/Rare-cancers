"""BOTH DIRECTIONS, ON THE DAY'S REAL FAILURES, OR IT IS NOT A GUARD.

★★ THE TWO WAYS THIS SYSTEM CAN FAIL ARE BOTH FATAL AND THEY PULL IN OPPOSITE DIRECTIONS.

    A GUARD THAT CANNOT CONDEMN ANYTHING reports success while measuring nothing. A work ledger is unusually
    exposed to it: give every item a green state and the suite passes, the workflow passes, and the fleet
    burns exactly as before.

    A GUARD THAT CONDEMNS CORRECT BEHAVIOUR gets switched off within a day. §6 makes a price hold a SUCCESS
    — *"I'd rather pause until availability opens than pay double per ns"* — so an alarm that fires on one is
    an alarm nobody reads by tomorrow. That is not hypothetical here: the FIRST version of `scan_rung_gates`
    cross-checked ladder rungs against plan titles by name and raised three false positives on the real
    files, one of them the lane that was billing six hosts at that moment. It was replaced, not tuned.

So every failure mode below is tested TWICE — once with something that MUST be caught and auto-dispatched,
once with the legitimate resting state that wears the same shape and MUST stay quiet.

THE PAIRS, and the real 2026-07-27 incident each replays:
    idle-vs-parked          the closure triangle idle ~3 h   vs  the 5a-KS pair parked with a stated reason
    dead-unit-vs-slow-unit  two units, 6 h, 0 iterations     vs  a unit mid-warmup inside its window
    placer-vs-advancing     green for 2 h placing nothing    vs  a fleet whose census is moving
    handoff-vs-answered     a gate that dispatched nothing   vs  a gate answered by a rental 22 min later
    hold-vs-stall           a §6 price hold with a snapshot  vs  a lane that simply stopped
    blocked-vs-looping      an item whose budget is spent    vs  an item whose dispatch worked

⚠ AND THE RISK trimcrae NAMED WHEN HE CHOSE AUTO-ASSIGN — *"a genuinely broken item could loop indefinitely
and burn rentals while looking busy"* — has its own block of tests, because it is the one failure mode the
design is specifically engineered against rather than merely careful about.
"""
from __future__ import annotations

import ast
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import work_ledger as wl  # noqa: E402

NOW = datetime.datetime(2026, 7, 27, 23, 0, 0, tzinfo=datetime.timezone.utc)   # 7:00 PM ET
MOD = os.path.join(os.path.dirname(__file__), "..", "work_ledger.py")


def _ago(minutes):
    return (NOW - datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# builders for the REAL artifact shapes (keys verified against the live files on 2026-07-27)
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _progress(minutes_old=5, live=6, n_units=4, scalars=None, phases=None, instances=None):
    scalars = scalars if scalars is not None else [1000600 + i for i in range(n_units)]
    units = [{"unit_id": f"e_anchor__lig{i}__neutral__neutral",
              "phase": (phases[i] if phases else "leg-complex-running " + _ago(1)),
              "committed": f"complex/production@{i}",
              "committed_scalar": scalars[i], "committed_prev_scalar": scalars[i], "ddg_bind_kcal": None}
             for i in range(n_units)]
    return {"_generated_utc": _ago(minutes_old), "_vast_unreadable": None, "live_instances": live,
            "n_units": n_units, "n_complete": 0, "instance_states": {"running": live},
            "gpu_util": [0.0] * live, "units": units,
            "instances": instances if instances is not None else
            [{"id": 46041403 + i, "label": f"s1f-0{i}-lig{i}", "machine_id": 1000 + i, "status": "running",
              "cur_state": "running", "gpu": "RTX 4090", "gpu_util": 0.0, "dph": 0.2049, "age_min": 100}
             for i in range(live)],
            "realised_usd_so_far": 21.63, "plan_usd_whole_tranche": 29.72}


def _fanout_hold(held=False, n_held=0):
    return {"utc": _ago(2), "held": held, "n_withheld": n_held, "n_held": n_held, "n_launching_now": 1,
            "basis_usd_per_ns": 0.003412, "held_reason": None,
            "board_depth": {"offers_returned": 167, "qualifying": 159, "priceable": 89},
            "offers_priced": [{"gpu": "RTX 5090", "machine_id": 26403, "min_bid": 0.1733,
                               "usd_per_ns": 0.004741}]}


def _ternary_hold(minutes_old=10, hold=False, mode="edge_reps", live=(), reason="within both ceilings",
                  depth=None, offers=None):
    return {"utc": _ago(minutes_old), "mode": mode, "hold": hold, "reason": reason,
            "nothing_to_launch": False, "units_live": list(live), "units_done": [],
            "depth": depth or {"offers_returned": 162, "priceable": 85},
            "offers": offers or [{"gpu": "RTX 5090", "machine_id": 51045, "min_bid_usd_h": 0.2,
                                  "usd_per_ns": 0.005255}],
            "live_host_rates": [{"cur_state": "running"} for _ in live]}


def _watch(entries):
    return {"watch": list(entries)}


def _entry(mode, enabled, parked=None, disabled=None, uid=None):
    e = {"unit_id": uid or f"u_{mode}", "leg_id": "calib", "seed": 1, "direction": "fwd", "mode": mode,
         "timestep_fs": "4.0", "warmup_timestep_fs": "1.0", "git_branch": "main",
         "max_relaunches_per_day": 8, "enabled": enabled}
    if parked:
        e["_parked_why"] = parked
    if disabled:
        e["_disabled_why"] = disabled
    return e


def _ledger(*rows):
    """`(minutes_ago, stage, outcome, reason)` -> the launch-attempt ledger's real shape."""
    return {"attempts": [{"utc": _ago(m), "et": "", "stage": st, "outcome": oc, "reason": rs,
                          "what_that_means": "", "run_url": "", "gate_hold": False}
                         for m, st, oc, rs in rows]}


def _schedule(*ms):
    """`(id, status, [deps])` -> the schedule JSON's real milestone shape."""
    return {"milestones": [{"id": i, "title": i, "status": s, "depends_on": list(d), "track": "gpu",
                            "cost_est_usd": "0", "optimistic_days": 1, "remaining_days": 0,
                            "parallel_ok": True, "note": ""} for i, s, d in ms]}


def _tree(tmp_path, *, progress=None, watch=None, thold=None, fhold=None, ledger=None, gcp=None,
          schedule=None, strategy=None):
    root = tmp_path / "root"
    root.mkdir(parents=True, exist_ok=True)
    (root / "step1-fanout-progress.json").write_text(json.dumps(progress if progress is not None
                                                                else _progress()))
    (root / "step1-fanout-market-hold.json").write_text(json.dumps(fhold if fhold is not None
                                                                   else _fanout_hold()))
    (root / "ternary-vast-watch.json").write_text(json.dumps(watch if watch is not None else _watch([])))
    if thold is not None:
        (root / "ternary-vast-market-hold.json").write_text(json.dumps(thold))
    (root / "ternary-vast-launch-attempts.json").write_text(json.dumps(ledger if ledger is not None
                                                                       else _ledger()))
    (root / "ternary-watch.json").write_text(json.dumps(gcp if gcp is not None else _watch([])))
    sched = root / "schedule.json"
    sched.write_text(json.dumps(schedule if schedule is not None else _schedule()))
    strat = root / "nr4a3-program-map.md"
    strat.write_text(strategy if strategy is not None else
                     "## THE ORDERED PLAN (spend-gated)\n\n### RUNG 9 — x\n\n")
    return str(root), str(strat), str(sched)


def _build(tmp_path, prev=None, now=NOW, **kw):
    """★ THE PROGRESS ARTIFACT IS RE-STAMPED TO THIS BUILD'S CLOCK, and that is not fixture housekeeping —
    it is what makes the replay REAL. A live tick writes `_generated_utc` a few minutes before it is read,
    ALWAYS, whatever hour it is. So a six-hour stall never shows up as an old artifact; it shows up as a
    FRESH artifact carrying an unchanged census, which is exactly why artifact age cannot detect this class
    and the reconciled fingerprint clock can. Pinning the stamp to the module constant instead let a stale
    unit read as in-window and hid four real detections behind a green suite."""
    root, strat, sched = _tree(tmp_path, **kw)
    pj = os.path.join(root, "step1-fanout-progress.json")
    doc = json.load(open(pj))
    doc["_generated_utc"] = (now - datetime.timedelta(minutes=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    open(pj, "w").write(json.dumps(doc))
    return wl.build(root, strat, sched, now, prev=prev, use_api=False), root


def _by_id(doc):
    return {e["id"]: e for e in doc["entries"]}


def _dispatched_workflows(doc):
    return {r["workflow"] for r in doc["_dispatch_plan"] if not r.get("capped")}


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PAIR 1 — the closure triangle idle ~3 h  vs  the 5a-KS pair parked with a stated reason
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_FIRES_the_idle_closure_triangle_is_caught_and_auto_dispatched(tmp_path):
    """THE INCIDENT: `triangle-prime` succeeded at ~3:40 PM ET and the lane that would dispatch the next
    step ended its turn. There was NO LIVE INSTANCE, so every liveness check read it as 'nothing to watch'.
    It sat ~3 h. This is the failure `lane_staleness_watch`'s docstring calls 'THE ONE NOTHING DETECTS'."""
    doc, _root = _build(tmp_path, ledger=_ledger((180, "triangle-prime", "success", "task=triangle-prime")))
    e = _by_id(doc)["lane:closure-triangle"]
    assert e["state"] == wl.OPEN, e
    assert e["owner"] == "gpu-ternary-fep-vast.yml"
    assert e["auto_action"], "an idle lane with unfinished work must be auto-dispatched, not merely noticed"
    # ★ THE $0 GATE, NOT THE PURCHASE. `triangle` rents four legs (~$6.83 plan); `triangle-gate` prices them
    # for $0 and self-dispatches the launch only if the board clears. The ledger asks for the second, so it
    # never asks for the spend at all.
    assert e["auto_action"]["inputs"] == {"task": "triangle-gate"}
    assert "gpu-ternary-fep-vast.yml" in _dispatched_workflows(doc)


def test_QUIET_the_5aks_pair_parked_with_a_stated_reason_is_a_resting_state(tmp_path):
    """The opposite shape wearing the same silence: two 5a-KS legs, checkpoints intact, deliberately parked
    behind the buy line. §6 makes this a SUCCESS. It must not be dispatched and must never accrue an
    attempt — retrying it would be the ledger spending money to defeat the guard that was saving it."""
    doc, _root = _build(tmp_path, watch=_watch([
        _entry("5aks", False, parked="checkpointed at production/800; blocked on the $/ns gate", uid="a"),
        _entry("5aks", False, parked="the paralogue half of the pair", uid="b")]))
    e = _by_id(doc)["lane:rung-5aks"]
    assert e["state"] == wl.HELD, e
    assert e["auto_action"] is None
    assert e["attempts"] == [], "a resting lane must never accrue an attempt against its retry budget"
    assert "gpu-ternary-fep-vast.yml" not in _dispatched_workflows(doc)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PAIR 2 — two fan-out units, ~6 h, ZERO committed iterations  vs  a unit legitimately inside its window
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_FIRES_a_fanout_unit_with_no_committed_iteration_for_six_hours(tmp_path):
    """THE INCIDENT: two units drew rentals for ~6 h with zero committed iterations across 48 snapshots,
    on a board yielding 1-3 placeable hosts per tick — so they were also displacing units that would have
    advanced. The signal is the committed-iteration census and nothing else."""
    flat = _progress(scalars=[0, 0, 1000600, 1000700])
    prev, _root = _build(tmp_path, progress=flat, now=NOW - datetime.timedelta(minutes=360))
    doc, _root = _build(tmp_path, prev=prev, progress=flat)      # same scalars, six hours later
    dead = _by_id(doc)["fanout-unit:e_anchor__lig0__neutral__neutral"]
    assert dead["evidence_fingerprint"] == "0"
    assert dead["auto_action"], "a unit that has committed nothing for 6 h must be acted on"
    assert "step1-fanout-autoscale.yml" in _dispatched_workflows(doc)
    # The clock is anchored to when the value last CHANGED, not to when it was last observed.
    assert dead["last_evidence_utc"] == prev["entries"][0]["last_evidence_utc"] or \
        wl._parse_z(dead["last_evidence_utc"]) < NOW - datetime.timedelta(minutes=300)


def test_QUIET_a_unit_inside_its_evidence_window_is_advancing_not_stalled(tmp_path):
    """Same artifact shape, same code path, ten minutes instead of six hours. A healthy fleet must produce
    NO dispatch at all — an alarm that fires on ordinary progress is the one that gets switched off."""
    flat = _progress(scalars=[0, 0, 1000600, 1000700])
    prev, _root = _build(tmp_path, progress=flat, now=NOW - datetime.timedelta(minutes=10))
    doc, _root = _build(tmp_path, prev=prev, progress=flat)
    unit = _by_id(doc)["fanout-unit:e_anchor__lig0__neutral__neutral"]
    assert unit["state"] == wl.ADVANCING, unit
    assert unit["auto_action"] is None
    assert "step1-fanout-autoscale.yml" not in _dispatched_workflows(doc)


def test_a_null_committed_scalar_is_not_the_same_as_zero(tmp_path):
    """`null` = never started; `0` = started and produced nothing. Only the second is a stall, and coercing
    either to the other is the absent-as-a-legal-value defect this repo keeps paying for."""
    doc, _root = _build(tmp_path, progress=_progress(scalars=[None, 0, 1, 2]))
    ids = _by_id(doc)
    assert ids["fanout-unit:e_anchor__lig0__neutral__neutral"]["evidence_fingerprint"] is None
    assert ids["fanout-unit:e_anchor__lig1__neutral__neutral"]["evidence_fingerprint"] == "0"


def test_the_phase_string_is_never_part_of_the_fingerprint(tmp_path):
    """`phase` carries a timestamp that moves EVERY TICK — including on a unit dead for hours. A
    fingerprint containing it would mask exactly the failure above. Same scalars, moved phases: the
    fingerprints must be identical, so the staleness clock does not reset."""
    a, _ = _build(tmp_path, progress=_progress(scalars=[5, 5, 5, 5],
                                               phases=["leg-complex-running " + _ago(300)] * 4))
    b, _ = _build(tmp_path, progress=_progress(scalars=[5, 5, 5, 5],
                                               phases=["leg-complex-running " + _ago(1)] * 4))
    assert [e["evidence_fingerprint"] for e in a["entries"] if e["scanner"] == "fanout_units"] == \
           [e["evidence_fingerprint"] for e in b["entries"] if e["scanner"] == "fanout_units"]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PAIR 3 — the placer green for ~2 h placing nothing  vs  a fleet that is genuinely advancing
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_FIRES_the_placer_running_green_while_the_whole_census_is_flat(tmp_path):
    """THE INCIDENT: a placement guard inverted on a null input, the placer reported success for ~2 h, and
    the fleet decayed 18 -> 5 across SEVEN GREEN TICKS. Every tick was green; the census never moved.
    Nothing here reads a tick's own report of itself — only the census."""
    flat = _progress(minutes_old=2, live=5, scalars=[7, 7, 7, 7])
    prev, _root = _build(tmp_path, progress=flat, now=NOW - datetime.timedelta(minutes=125))
    doc, _root = _build(tmp_path, prev=prev, progress=flat)
    stalled = [e for e in doc["entries"] if e["scanner"] == "fanout_units" and e["auto_action"]]
    assert stalled, "a fleet whose entire census is flat for 2 h must be acted on despite green ticks"
    assert "step1-fanout-autoscale.yml" in _dispatched_workflows(doc)


def test_QUIET_the_same_fleet_when_a_single_unit_advanced(tmp_path):
    """One unit moving is evidence the fleet is alive. The clock resets per unit, so the ones that moved
    go quiet — and the ones that did not keep their own ageing clock. Both facts survive."""
    prev, _root = _build(tmp_path, progress=_progress(scalars=[7, 7, 7, 7]),
                         now=NOW - datetime.timedelta(minutes=125))
    doc, _root = _build(tmp_path, prev=prev, progress=_progress(scalars=[8, 7, 7, 7]))
    moved = _by_id(doc)["fanout-unit:e_anchor__lig0__neutral__neutral"]
    assert moved["state"] == wl.ADVANCING and moved["auto_action"] is None, moved


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PAIR 4 — a hand-off that evaporated  vs  one answered by a rental
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_FIRES_a_gate_that_dispatched_and_produced_nothing(tmp_path):
    doc, _root = _build(tmp_path, ledger=_ledger(
        (90, "market-gate", "dispatched", "board cleared both ceilings; dispatching task=edge-reps")))
    hand = [e for e in doc["entries"] if e["scanner"] == "handoff"]
    assert len(hand) == 1, hand
    assert "never answered" in hand[0]["what"]


def test_QUIET_a_hand_off_answered_by_a_rental_22_minutes_later(tmp_path):
    """The slowest real gate->rental hand-off measured on 2026-07-27 was ~22 min (19:38:47Z dispatched ->
    20:00:29Z launched). The acknowledgement window is set past it, so a slow-but-working hand-off is never
    graded a failure — and an ANSWERED one is never raised however old it is."""
    doc, _root = _build(tmp_path, ledger=_ledger(
        (90, "market-gate", "dispatched", "dispatching task=edge-reps"),
        (68, "rent (steps.rent.outcome=success)", "launched", "task=edge-reps; job status success")))
    assert [e for e in doc["entries"] if e["scanner"] == "handoff"] == []


def test_QUIET_a_dispatch_still_inside_the_acknowledgement_window(tmp_path):
    doc, _root = _build(tmp_path, ledger=_ledger((5, "market-gate", "dispatched", "task=edge-reps")))
    assert [e for e in doc["entries"] if e["scanner"] == "handoff"] == []


def test_a_second_gate_pass_is_not_an_answer_to_the_first(tmp_path):
    """A repeated gate evaluation is the same question asked again — which is what a stuck lane looks like.
    Only a non-gate record answers a dispatch."""
    doc, _root = _build(tmp_path, ledger=_ledger(
        (90, "market-gate", "dispatched", "task=triangle"),
        (60, "market-gate", "nothing-to-launch", "task=triangle")))
    assert len([e for e in doc["entries"] if e["scanner"] == "handoff"]) == 1


def test_a_triangle_record_never_answers_for_the_replicate_lane(tmp_path):
    """`gpu-ternary-fep-vast.yml` serves the replicates, the triangle and 5a-KS. Attribution is by `task=`,
    so one lane's activity can never vouch for a sibling's silence."""
    doc, _root = _build(tmp_path, ledger=_ledger(
        (90, "market-gate", "dispatched", "task=edge-reps"),
        (60, "rent (steps.rent.outcome=success)", "launched", "task=triangle")))
    hand = [e for e in doc["entries"] if e["scanner"] == "handoff"]
    assert len(hand) == 1 and "edge-reps" in hand[0]["id"]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PAIR 5 — a §6 price hold with its snapshot  vs  a lane that simply stopped
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_QUIET_a_price_hold_with_its_market_snapshot_is_a_resting_state(tmp_path):
    """§6: *'I'd rather pause until availability opens than pay double per ns.'* A hold is the gate WORKING.
    It must be `held`, never dispatched, and — the property that matters most — it must be structurally
    incapable of decaying into `blocked`, because it accrues no attempts."""
    doc, _root = _build(
        tmp_path,
        watch=_watch([_entry("edge_reps", True)]),
        thold=_ternary_hold(hold=True, reason="2.4x basis — pausing rather than paying double per ns"))
    e = _by_id(doc)["lane:ternary-valb-reps"]
    assert e["state"] == wl.HELD, e
    assert e["auto_action"] is None and e["attempts"] == []
    assert e["n_fruitless_attempts"] == 0


def test_a_price_hold_can_NEVER_become_blocked_however_long_it_lasts(tmp_path):
    """Twenty consecutive ticks of a legitimate hold. The retry budget is 3. If a hold could drain it, a
    correct §6 pause would be recorded as a broken item — condemning the exact behaviour the rule
    requires."""
    prev = None
    for i in range(20):
        prev, _root = _build(
            tmp_path, prev=prev, now=NOW + datetime.timedelta(minutes=15 * i),
            watch=_watch([_entry("edge_reps", True)]),
            thold=_ternary_hold(hold=True, reason="2.4x basis — pausing rather than paying double"))
    e = _by_id(prev)["lane:ternary-valb-reps"]
    assert e["state"] == wl.HELD, f"a 5-hour price hold must still be `held`, not `blocked`: {e['state']}"
    assert e["attempts"] == []


def test_FIRES_a_lane_that_simply_stopped_is_not_a_hold(tmp_path):
    """Same 'nothing is happening', no gate snapshot to explain it. This is a stall and must be acted on."""
    doc, _root = _build(tmp_path, watch=_watch([_entry("edge_reps", True)]),
                        ledger=_ledger((200, "market-gate", "nothing-to-launch", "task=edge-reps")))
    e = _by_id(doc)["lane:ternary-valb-reps"]
    assert e["state"] != wl.HELD, e


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PAIR 6 — THE RISK trimcrae NAMED: "a genuinely broken item could loop indefinitely and burn rentals
# while looking busy". Bounded retries, both directions.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_a_genuinely_broken_item_STOPS_being_retried_after_the_budget(tmp_path):
    """The whole engineered answer to the auto-assign risk. Tick it repeatedly with an item that never
    moves: after MAX_FRUITLESS_ATTEMPTS it must become `blocked` and NEVER be dispatched again."""
    flat = _progress(scalars=[0, 1000600, 1000700, 1000800])
    prev, _root = _build(tmp_path, progress=flat, now=NOW - datetime.timedelta(minutes=400))
    fired = []
    for i in range(10):
        prev, _root = _build(tmp_path, prev=prev, progress=flat,
                             now=NOW + datetime.timedelta(minutes=100 * i))
        fired.append("step1-fanout-autoscale.yml" in _dispatched_workflows(prev))
    e = _by_id(prev)["fanout-unit:e_anchor__lig0__neutral__neutral"]
    assert e["state"] == wl.BLOCKED, e
    assert e["blocked_cause"] == "retry-budget-spent"
    assert e["n_fruitless_attempts"] >= wl.MAX_FRUITLESS_ATTEMPTS
    assert sum(fired) == wl.MAX_FRUITLESS_ATTEMPTS, \
        f"exactly {wl.MAX_FRUITLESS_ATTEMPTS} attempts, then silence — got {sum(fired)}"
    assert not fired[-1], "the last tick must not have dispatched: that is the bound"


def test_a_blocked_item_is_RECORDED_not_dropped_and_carries_every_failure(tmp_path):
    """'Never escalate' means do not interrupt him — NOT do not record. A blocked item that vanished from
    the board would be a worse defect than the one this replaces."""
    flat = _progress(scalars=[0, 1, 2, 3])
    prev, _root = _build(tmp_path, progress=flat, now=NOW - datetime.timedelta(minutes=400))
    for i in range(8):
        prev, _root = _build(tmp_path, prev=prev, progress=flat,
                             now=NOW + datetime.timedelta(minutes=100 * i))
    e = _by_id(prev)["fanout-unit:e_anchor__lig0__neutral__neutral"]
    assert e["id"] in prev["blocked"], "a blocked item must be indexed at the top of the ledger"
    assert len(e["attempts"]) == wl.MAX_FRUITLESS_ATTEMPTS
    assert all(a.get("fingerprint_at_dispatch") is not None for a in e["attempts"]), \
        "each attempt must record the fingerprint it was made against, or 'did it help' is unanswerable"
    assert e["blocked_by"], "a blocked item must say why"
    board = wl.render_board(prev, _root, NOW)
    assert "RETRY BUDGET SPENT" in board, "a blocked item must appear on the generated board"


def test_a_dispatch_that_WORKED_resets_the_budget(tmp_path):
    """The property that stops a slow-but-live item being parked as broken: an attempt counts as fruitless
    only while the fingerprint it was made against is still current. Real progress wipes the count."""
    flat = _progress(scalars=[0, 1, 2, 3])
    prev, _root = _build(tmp_path, progress=flat, now=NOW - datetime.timedelta(minutes=400))
    for i in range(2):
        prev, _root = _build(tmp_path, prev=prev, progress=flat,
                             now=NOW + datetime.timedelta(minutes=100 * i))
    assert _by_id(prev)["fanout-unit:e_anchor__lig0__neutral__neutral"]["n_fruitless_attempts"] == 2
    moved = _progress(scalars=[500, 1, 2, 3])
    prev, _root = _build(tmp_path, prev=prev, progress=moved,
                         now=NOW + datetime.timedelta(minutes=300))
    e = _by_id(prev)["fanout-unit:e_anchor__lig0__neutral__neutral"]
    assert e["n_fruitless_attempts"] == 0, "progress must wipe the fruitless count"
    assert e["state"] != wl.BLOCKED


def test_a_blocked_item_UNBLOCKS_ITSELF_when_its_fingerprint_moves(tmp_path):
    """`blocked` is permanent until something changes, and 'something changes' is MECHANICAL — no human has
    to clear it, and nothing clears it by forgetting."""
    flat = _progress(scalars=[0, 1, 2, 3])
    prev, _root = _build(tmp_path, progress=flat, now=NOW - datetime.timedelta(minutes=400))
    for i in range(8):
        prev, _root = _build(tmp_path, prev=prev, progress=flat,
                             now=NOW + datetime.timedelta(minutes=100 * i))
    assert _by_id(prev)["fanout-unit:e_anchor__lig0__neutral__neutral"]["state"] == wl.BLOCKED
    prev, _root = _build(tmp_path, prev=prev, progress=_progress(scalars=[900, 1, 2, 3]),
                         now=NOW + datetime.timedelta(minutes=900))
    assert _by_id(prev)["fanout-unit:e_anchor__lig0__neutral__neutral"]["state"] != wl.BLOCKED


def test_a_LOST_WRITE_BACK_cannot_manufacture_a_block(tmp_path):
    """If the ledger could not be committed, `prev` is old — so the fingerprint has had MORE chance to move,
    attempts read as successful, and the budget RESETS. The failure mode of a lost write is an item retried
    more, never one blocked without cause. Both directions fail safe; the safe direction is the quiet one."""
    flat = _progress(scalars=[0, 1, 2, 3])
    prev, _root = _build(tmp_path, progress=flat, now=NOW - datetime.timedelta(minutes=400))
    for i in range(8):
        prev, _root = _build(tmp_path, prev=prev, progress=flat,
                             now=NOW + datetime.timedelta(minutes=100 * i))
    assert _by_id(prev)["fanout-unit:e_anchor__lig0__neutral__neutral"]["state"] == wl.BLOCKED
    # Now simulate the write-back having been lost: `prev` is absent entirely.
    doc, _root = _build(tmp_path, prev=None, progress=flat, now=NOW + datetime.timedelta(minutes=900))
    assert doc["blocked"] == [] or "fanout-unit:e_anchor__lig0__neutral__neutral" not in doc["blocked"]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# a unit correctly blocked on CHEMISTRY — visible, never retried, and never a loop
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_a_unit_blocked_on_chemistry_is_visible_and_bounded(tmp_path):
    """`cw_bio_nmethyl_amide` is permanently blocked: no mapper reaches the 20-atom provable floor, both
    LOMAP budgets returned in 0.01 s, and a relaunch aborts identically and buys nothing. The correct
    behaviour is exactly the bounded-retry rule — a few attempts, then `blocked` and VISIBLE forever. It
    must never loop, and it must never silently disappear."""
    flat = _progress(scalars=[0, 1, 2, 3],
                     phases=["leg-complex-FAILED-rc1 " + _ago(300)] + ["leg-complex-running " + _ago(1)] * 3)
    prev, _root = _build(tmp_path, progress=flat, now=NOW - datetime.timedelta(minutes=400))
    for i in range(12):
        prev, _root = _build(tmp_path, prev=prev, progress=flat,
                             now=NOW + datetime.timedelta(minutes=100 * i))
    e = _by_id(prev)["fanout-unit:e_anchor__lig0__neutral__neutral"]
    assert e["state"] == wl.BLOCKED and len(e["attempts"]) == wl.MAX_FRUITLESS_ATTEMPTS
    assert e["id"] in prev["blocked"]
    # ⚠ AND THE FAILED PHASE IS RECORDED AS AN OBSERVATION, NOT A DIAGNOSIS. §4: an error's own explanation
    # was wrong three times on 2026-07-27, so the census adjudicates, not the string.
    assert any("OBSERVATION" in n for n in (e["notes"] or [])), e["notes"]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# rungs and plan items
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_FIRES_an_unblocked_rung_whose_gate_has_returned_no_verdict(tmp_path):
    doc, _root = _build(tmp_path, schedule=_schedule(("a", "done", []), ("b", "pending", ["a"])))
    e = _by_id(doc)["rung:b"]
    assert e["state"] == wl.OPEN and not e["owner"], e
    assert e["id"] in doc["unowned"]


def test_QUIET_a_rung_genuinely_waiting_on_a_named_dependency(tmp_path):
    doc, _root = _build(tmp_path, schedule=_schedule(("a", "in_progress", []), ("b", "pending", ["a"])))
    e = _by_id(doc)["rung:b"]
    assert e["state"] == wl.BLOCKED and e["blocked_cause"] == "external-gate"
    assert "a is in_progress" in " ".join(e["blocked_by"])


def test_a_done_rung_raises_nothing(tmp_path):
    doc, _root = _build(tmp_path, schedule=_schedule(("a", "done", []), ("b", "done", ["a"])))
    assert [e for e in doc["entries"] if e["scanner"] == "rung_gates"] == []


def test_a_skipped_dependency_SATISFIES_rather_than_blocking_forever(tmp_path):
    """`valA_full` was deliberately skipped with a stated saving. A skip is a decision that was MADE;
    treating it as unmet would block everything behind it for ever."""
    doc, _root = _build(tmp_path, schedule=_schedule(("a", "skipped", []), ("b", "pending", ["a"])))
    assert _by_id(doc)["rung:b"]["state"] == wl.OPEN


def test_an_UNKNOWN_dependency_is_not_a_satisfied_one(tmp_path):
    """A typo'd or deleted id must not read as 'nothing blocking' — that would unblock a milestone on the
    strength of a missing record, which is the absent-as-a-legal-value defect pointed at the graph."""
    doc, _root = _build(tmp_path, schedule=_schedule(("b", "pending", ["ghost"])))
    e = _by_id(doc)["rung:b"]
    assert e["state"] == wl.BLOCKED
    assert "NOT A MILESTONE" in " ".join(e["blocked_by"])


def test_a_result_UNDER_CORRECTION_counts_as_no_verdict(tmp_path):
    """A verdict landed and stopped standing. That is more decision-relevant than an item never started,
    and it must not read as done."""
    doc, _root = _build(tmp_path, schedule=_schedule(("a", "under_correction", [])))
    assert _by_id(doc)["rung:a"]["state"] == wl.OPEN


PLAN = """## THE ORDERED PLAN (spend-gated)

Legend: `[ ]` pending

### RUNG 7 — free
- **`[x]` Something finished** — **$0.** done.
- **`[–]` Something skipped** — saves $50.
- **`[ ]` An unowned free item** — **$0.** Nobody is carrying this.
- **`[~]` A gated item** — **~$8.**
  **Gate:** Val A satisfied.

## Next section
- **`[ ]` Not in the plan section at all**
"""


def test_FIRES_an_unblocked_plan_item_with_no_gate_is_UNOWNED(tmp_path):
    doc, _root = _build(tmp_path, strategy=PLAN)
    plan = [e for e in doc["entries"] if e["scanner"] == "plan_items"]
    assert len(plan) == 2, [e["what"] for e in plan]        # the `[ ]` and the `[~]`; not `[x]` or `[–]`
    free = next(e for e in plan if "unowned free item" in e["what"].lower())
    assert free["state"] == wl.OPEN and not free["owner"]
    assert free["id"] in doc["unowned"]


def test_QUIET_a_plan_item_naming_a_gate_is_blocked_not_dispatched(tmp_path):
    """A prose gate is not machine-readable, and this module does not pretend otherwise: the item is
    recorded `blocked` WITH THE GATE'S OWN WORDS and never auto-dispatched. That UNDER-dispatches, which is
    the safe direction when the alternative is an unauthorised rental."""
    doc, _root = _build(tmp_path, strategy=PLAN)
    gated = next(e for e in doc["entries"] if e["scanner"] == "plan_items" and "gated item" in e["what"])
    assert gated["state"] == wl.BLOCKED and gated["blocked_cause"] == "external-gate"
    assert gated["auto_action"] is None


def test_the_scan_is_bounded_to_the_ORDERED_PLAN_section(tmp_path):
    """Checklist markers appear elsewhere in a 231 kB document; a whole-file sweep would raise entries from
    worked examples and appendices."""
    doc, _root = _build(tmp_path, strategy=PLAN)
    assert not any("Not in the plan section" in e["what"] for e in doc["entries"])


def test_a_MISSING_plan_heading_reports_blindness_rather_than_emptiness(tmp_path):
    """An empty result and 'I could not find the plan' are opposite facts. Returning [] silently would make
    a broken scanner indistinguishable from a plan with nothing left to do."""
    doc, _root = _build(tmp_path, strategy="# no plan here\n")
    cov = next(c for c in doc["_scanners"] if c["scanner"] == "plan_items")
    assert "NOT SCANNED" in cov["how"]


def test_the_en_dash_skip_marker_is_not_read_as_pending(tmp_path):
    """`[–]` uses U+2013. Matching only ASCII `-` would silently reclassify every skipped item as pending
    and fill the board with work nobody owes."""
    doc, _root = _build(tmp_path, strategy=PLAN)
    assert not any("skipped" in e["what"].lower() for e in doc["entries"] if e["scanner"] == "plan_items")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# THE BOARD — generated, so a claimed owner that does not exist is UNWRITABLE
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_NO_LEDGER_ENTRY_NO_ROW(tmp_path):
    """Failure 5, made structural: a row on the prose board claimed an owner that had never been dispatched.
    Here every row is a function of `entries`, so an owner nobody recorded cannot be rendered."""
    doc, root = _build(tmp_path)
    doc["entries"] = []
    board = wl.render_board(doc, root, NOW)
    assert "step1-fanout" not in board.split("self-check")[0]
    assert "0 ledger entr(ies)" in board


def test_the_board_carries_the_section_1_columns(tmp_path):
    doc, root = _build(tmp_path, progress=_progress(live=2))
    board = wl.render_board(doc, root, NOW)
    assert "$/ns" in board or "basis" in board, board
    assert "ET" in board
    assert "$" in board


def test_the_board_renders_PAYING_and_REFUSED_distinctly(tmp_path):
    """§1: *'the `$/ns` column still shows several rows over 1.5x. Why? Are we not stopping those runs?'*
    One glyph cannot mean both 'we are paying this' and 'we refused to pay this'."""
    over = [{"id": 1, "label": "s1f-00-lig0", "gpu": "RTX 4090", "dph": 9.99, "age_min": 10,
             "status": "running", "cur_state": "running", "gpu_util": 0.0, "machine_id": 1}]
    doc, root = _build(tmp_path, progress=_progress(live=1, instances=over),
                       fhold=_fanout_hold(held=True, n_held=3))
    board = wl.render_board(doc, root, NOW)
    assert "PAYING OVER THE" in board, board
    assert "$0 spent" in board, "the refused side must say so on the same line"


def test_a_gate_with_NOTHING_TO_BUY_is_not_an_unreadable_cost(tmp_path):
    """CAUGHT ON THE REAL BOARD after a merge. The ternary gate writes TWO shapes: a full priced snapshot,
    and a short `nothing_to_launch` one carrying no `plan_usd` at all. Reporting the short form as
    UNREADABLE cries wolf on a gate doing exactly the right thing; reporting it as a bare `$0` would hide a
    genuine schema break behind a plausible number. The shape is READ, not assumed."""
    short = {"utc": _ago(5), "mode": "edge_reps", "hold": False, "nothing_to_launch": True,
             "n_units": 0, "units_live": [], "units_done": [], "reason": "every unit already done or hosted"}
    doc, root = _build(tmp_path, watch=_watch([_entry("edge_reps", True)]), thold=short)
    board = wl.render_board(doc, root, NOW)
    assert "nothing to buy" in board, board
    assert "cost UNREADABLE" not in board, board


def test_a_GENUINE_schema_break_still_reads_UNREADABLE(tmp_path):
    """The other direction: a priced snapshot that lost its cost key is a real defect and must say so."""
    broken = {"utc": _ago(5), "mode": "edge_reps", "hold": False, "nothing_to_launch": False,
              "n_units": 3, "units_live": [], "units_done": [], "reason": "x"}
    doc, root = _build(tmp_path, watch=_watch([_entry("edge_reps", True)]), thold=broken)
    assert "cost UNREADABLE" in wl.render_board(doc, root, NOW)


def test_a_non_GPU_row_carries_an_em_dash_not_a_fabricated_figure(tmp_path):
    doc, root = _build(tmp_path, schedule=_schedule(("a", "pending", [])))
    board = wl.render_board(doc, root, NOW)
    plan_block = [ln for ln in board.splitlines() if "no compute" in ln]
    assert plan_block, board


def test_ONE_LANES_SNAPSHOT_NEVER_PRICES_ANOTHER(tmp_path):
    """CAUGHT BY RUNNING THE FIRST BOARD: the step-1 fan-out's `offers_priced` priced the closure triangle,
    the 5a-KS pair AND the plan items, so three lanes displayed a refusal computed for a fourth — the exact
    mis-attribution `lane_staleness_watch` warns about for shared artifacts."""
    doc, root = _build(tmp_path, fhold=_fanout_hold(held=True, n_held=9),
                       ledger=_ledger((300, "triangle-prime", "success", "task=triangle-prime")))
    tri = _by_id(doc)["lane:closure-triangle"]
    assert tri["price_points_at"] == "valb-triangle-market-hold.json", \
        "the triangle prices from its OWN gate snapshot, never the fan-out's"
    board = wl.render_board(doc, root, NOW)
    tri_line = [ln for ln in board.splitlines() if "closure triangle" in ln]
    assert tri_line, board
    idx = board.splitlines().index(tri_line[0])
    assert "step1-fanout-market-hold" not in "\n".join(board.splitlines()[idx:idx + 3])


def test_the_board_is_DETERMINISTIC_under_a_now_override(tmp_path):
    """A board that cannot be replayed cannot be verified, and verification is the point. The first version
    read the wall clock inside the ETA cell while the rest of the run used `--now`."""
    doc, root = _build(tmp_path, progress=_progress(live=2))
    assert wl.render_board(doc, root, NOW) == wl.render_board(doc, root, NOW)
    assert wl.render_board(doc, root, NOW) != wl.render_board(
        doc, root, NOW + datetime.timedelta(hours=3))


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# SELF-SUPERVISION
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_artifact_declares_its_own_expiry(tmp_path):
    """A supervisor that has stopped cannot report that it stopped, so the deadline is written INTO the
    file: a reader who does nothing but open it can tell."""
    doc, _root = _build(tmp_path)
    assert doc["_stale_after_utc"] and doc["_generated_utc"] < doc["_stale_after_utc"]
    assert wl.self_check(doc, NOW)["ok"] is True


def test_a_STOPPED_supervisor_chain_is_detectable_from_the_committed_artifact_alone(tmp_path):
    doc, _root = _build(tmp_path)
    v = wl.self_check(doc, NOW + datetime.timedelta(hours=4))
    assert v["ok"] is False and v["verdict"] == "SUPERVISOR-CHAIN-BROKEN", v
    assert "step1-fanout-supervisor.yml" in v["detail"], "it must say how to restart the chain"


def test_an_ABSENT_ledger_is_not_graded_as_nothing_to_do():
    v = wl.self_check(None, NOW)
    assert v["ok"] is False and v["verdict"] == "NO-LEDGER"


def test_an_unparseable_generation_stamp_is_UNREADABLE_not_fresh():
    v = wl.self_check({"_generated_utc": "not a date"}, NOW)
    assert v["ok"] is False and v["verdict"] == "UNREADABLE"


def test_the_self_check_appears_on_the_board(tmp_path):
    doc, root = _build(tmp_path)
    assert "self-check" in wl.render_board(doc, root, NOW)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# STRUCTURAL GUARANTEES — properties, not promises in a docstring
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_it_can_neither_destroy_nor_reap_nor_condemn_nor_shell_out():
    """⚠ NEVER A DESTRUCTIVE ACTION. Destroy/reap/blacklist stay in the lanes' own `collect` paths, which
    read the start response that separates 'outbid, restartable' from 'GPU gone, destroy it'. A ledger that
    could also act would be a SECOND UNREVIEWED CONTROL PATH — the exact shape this repo keeps paying for.
    Asserted the same way `lane_staleness_watch` asserts report-only."""
    tree = ast.parse(open(MOD).read())
    banned = {"destroy", "reap", "rent", "condemn", "blacklist", "nudge", "collect", "submit",
              "urlopen", "Popen", "system", "check_output", "call", "spawn", "kill"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            assert name not in banned, f"destructive/side-effecting call {name!r}"


def test_gpu_util_is_never_read_anywhere_in_the_module():
    """0.0 has been observed on genuinely advancing hosts, and `vast_idle_guard.py`'s one inviolable rule is
    that GPU idleness NEVER condemns a box. The key sits in the very artifact this module reads."""
    tree = ast.parse(open(MOD).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value == "gpu_util":
            raise AssertionError("gpu_util is referenced as a key")
        if isinstance(node, ast.Attribute) and node.attr == "gpu_util":
            raise AssertionError("gpu_util is referenced as an attribute")


def test_cur_state_is_never_used_to_decide_anything():
    """`cur_state` is not a liveness signal and `exited` is routinely transient — three instances read
    `exited` and were running again 21 min later."""
    tree = ast.parse(open(MOD).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value == "cur_state":
            raise AssertionError("cur_state is referenced")


def test_the_module_level_imports_cannot_die_with_a_lane():
    """An alarm that shares a dependency with the thing it watches dies with it — which is how the 11:37 AM
    tick took its own progress check down. The only non-stdlib imports are two WATCHERS, both themselves
    dependency-free, so the property holds transitively. The cost stack is imported LAZILY inside the
    renderer, where a fault degrades one column instead of erasing the ledger."""
    tree = ast.parse(open(MOD).read())
    top = set()
    for node in tree.body:                                  # module scope ONLY
        if isinstance(node, ast.Import):
            top.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top.add(node.module.split(".")[0])
    allowed = {"argparse", "datetime", "json", "os", "re", "sys", "__future__",
               "fleet_supervision_alarm", "lane_staleness_watch"}
    assert top <= allowed, f"unexpected module-level imports: {top - allowed}"
    for banned in ("boto3", "requests", "congeneric_fanout", "vast_cost_model", "inflight_usd_per_ns",
                   "ternary_vast_launch", "gpu_backend"):
        assert banned not in top, f"{banned} must be imported lazily, not at module scope"


def test_the_dispatch_allowlist_refuses_an_unknown_workflow():
    try:
        wl._action("gpu-ternary-aws.yml", {}, why="x")
    except ValueError as e:
        assert "DISPATCHABLE" in str(e)
    else:
        raise AssertionError("an unlisted workflow must be refused")


def test_it_is_STRUCTURALLY_INCAPABLE_of_passing_a_price():
    """⚠ MAY NEVER BYPASS A SPEND GATE. The ledger names a workflow and nothing else; every dispatch goes
    through the lane's own path behind the absolute buy line and the derived dollar ceiling. Refused twice —
    once by the allowlist, once on the input's own name — because the allowlist is data and data gets
    edited carelessly."""
    for bad in ("max_ratio_vs_basis", "bid", "usd_per_ns_ceiling", "price", "spend_cap", "dph",
                "budget_usd", "rate_line"):
        try:
            wl._action("step1-fanout-autoscale.yml", {bad: "1"}, why="x")
        except ValueError:
            continue
        raise AssertionError(f"input {bad!r} must be refused: the ledger may never move a spend gate")


def test_the_ledger_never_dispatches_a_task_that_RENTS():
    """⚠ THE STRONGEST FORM OF 'MAY NEVER BYPASS A SPEND GATE': it does not merely route through one, it
    never asks for the spend. `gpu-ternary-fep-vast.yml`'s `task` choice list contains both the $0 gates and
    the tasks that actually rent — `triangle` (~$6.83 plan), `5aks` (~$12), `edge-reps`, `triangle-smoke`.
    Only a gate value may ever appear in `_LANE_ACTION`."""
    renting = {"triangle", "5aks", "edge-reps", "smoke", "5aks-smoke", "triangle-smoke", "edge", "probe"}
    for lane, (_wf, inputs) in wl._LANE_ACTION.items():
        task = (inputs or {}).get("task")
        if task is None:
            continue
        assert task not in renting, f"lane {lane} would dispatch the RENTING task {task!r}"
        assert task.endswith("gate"), f"lane {lane} dispatches {task!r}, which is not a $0 gate task"


def test_it_can_never_dispatch_the_workflow_it_runs_inside():
    """Listing `lane-staleness-watch.yml` would let an entry dispatch the job that produced it — a
    self-sustaining loop that looks like healthy supervision and is really one run queueing the next for
    ever."""
    assert wl.TICK_WORKFLOW not in wl.DISPATCHABLE
    for _lane, (wf, _i) in wl._LANE_ACTION.items():
        assert wf != wl.TICK_WORKFLOW


def test_every_dispatchable_workflow_names_the_gate_it_passes_through():
    for wf, spec in wl.DISPATCHABLE.items():
        assert spec.get("gated_by"), f"{wf} declares no gate — an ungated dispatch path"
        assert spec.get("allowed_inputs") is not None
        for k in spec["allowed_inputs"]:
            assert not any(t in k.lower() for t in wl._FORBIDDEN_INPUT_TOKENS), \
                f"{wf} declares a price-vocabulary input {k!r}"


def test_the_dispatch_plan_is_deduplicated_and_capped(tmp_path):
    """Nineteen stalled units all want the same tick. Firing it nineteen times would queue nineteen runs
    against a serialising `concurrency` group — the ledger manufacturing its own backlog."""
    flat = _progress(n_units=19, scalars=[0] * 19, live=1)
    prev, _root = _build(tmp_path, progress=flat, now=NOW - datetime.timedelta(minutes=400))
    doc, _root = _build(tmp_path, prev=prev, progress=flat)
    fanout = [r for r in doc["_dispatch_plan"] if r["workflow"] == "step1-fanout-autoscale.yml"]
    assert len(fanout) == 1, f"one dispatch, not {len(fanout)}"
    assert len(fanout[0]["serves"]) > 1
    assert len(wl.executable(doc["_dispatch_plan"])) <= wl.MAX_DISPATCHES_PER_RUN


def test_every_entry_says_WHY_it_has_no_action_rather_than_a_bare_null(tmp_path):
    """'No action available' and 'an action exists but this state forbids it' are opposite facts, and a bare
    `null` renders them alike — the absent-as-a-value defect applied to the field that decides whether work
    moves."""
    doc, _root = _build(tmp_path, schedule=_schedule(("a", "pending", [])),
                        watch=_watch([_entry("5aks", False, parked="held on price")]))
    for e in doc["entries"]:
        if e["auto_action"] is None:
            assert e["auto_action_why_none"], f"{e['id']} has neither an action nor a reason"


def test_the_SCANNERS_tuple_matches_the_docstring_coverage_claim():
    """The coverage list in the docstring IS the claim this system makes about itself. If it can drift away
    from the code, it is decoration."""
    doc = wl.__doc__
    scanned = doc.split("SCANNED — a stall in one of these produces an entry:")[1].split("NOT SCANNED")[0]
    for name in wl.SCANNERS:
        assert f"`{name}`" in scanned, f"scanner {name!r} is registered but not in the coverage claim"


def test_every_scanner_that_runs_is_reported_and_a_crash_is_not_silence(tmp_path):
    """A category that stopped being scanned looks exactly like a category with nothing in it — this
    module's own defect, turned on itself."""
    doc, _root = _build(tmp_path)
    assert {c["scanner"] for c in doc["_scanners"]} == set(wl.SCANNERS) - {"self"}
    broken = dict(doc)
    broken["_scanners"] = [{"scanner": "fanout_units", "ran": False, "found": 0, "error": "boom"}]
    board = wl.render_board(broken, _root, NOW)
    assert "DID NOT RUN" in board and "NOT the same as empty" in board


def test_a_scanner_exception_does_not_shrink_the_board(tmp_path, monkeypatch):
    monkeypatch.setattr(wl, "scan_fanout_units",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    doc, _root = _build(tmp_path)
    cov = next(c for c in doc["_scanners"] if c["scanner"] == "fanout_units")
    assert cov["ran"] is False and "boom" in cov["error"]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# END TO END — the two complete boards, on the same code path
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_END_TO_END_a_day_of_real_failures_is_caught_and_auto_dispatched(tmp_path):
    """All four of the day's mechanisms in one tree: the idle triangle, two dead fan-out units, a flat
    census under green ticks, and a hand-off that evaporated. NOTHING here may be quiet."""
    flat = _progress(minutes_old=3, live=2, scalars=[0, 0, 1000600, 1000700])
    kw = dict(progress=flat,
              watch=_watch([_entry("edge_reps", True)]),
              ledger=_ledger((300, "triangle-prime", "success", "task=triangle-prime"),
                             (95, "market-gate", "dispatched", "task=edge-reps")))
    prev, _root = _build(tmp_path, now=NOW - datetime.timedelta(minutes=380), **kw)
    doc, root = _build(tmp_path, prev=prev, **kw)

    ids = _by_id(doc)
    assert ids["lane:closure-triangle"]["state"] == wl.OPEN
    assert ids["lane:closure-triangle"]["auto_action"], "the idle triangle must be auto-dispatched"
    assert ids["fanout-unit:e_anchor__lig0__neutral__neutral"]["auto_action"], "dead unit 1"
    assert ids["fanout-unit:e_anchor__lig1__neutral__neutral"]["auto_action"], "dead unit 2"
    assert [e for e in doc["entries"] if e["scanner"] == "handoff"], "the evaporated hand-off"
    assert _dispatched_workflows(doc) == {"step1-fanout-autoscale.yml", "gpu-ternary-fep-vast.yml"}
    board = wl.render_board(doc, root, NOW)
    assert "UNOWNED" in board or "dispatching" in board


def test_END_TO_END_a_correctly_resting_board_dispatches_NOTHING(tmp_path):
    """Same five inputs, same code path, every one legitimately explained: a fan-out advancing, a replicate
    lane on a §6 price hold WITH its snapshot, a 5a-KS pair parked with a stated reason, a schedule whose
    pending rungs are genuinely waiting on named dependencies, and a plan whose open item names its gate.
    NOT ONE DISPATCH may be issued — this is the direction that gets a system switched off."""
    doc, root = _build(
        tmp_path,
        progress=_progress(minutes_old=4, live=3, scalars=[1, 2, 3, 4]),
        watch=_watch([_entry("edge_reps", True, uid="r1"),
                      _entry("5aks", False, parked="checkpointed; blocked on the $/ns gate", uid="k1"),
                      _entry("5aks", False, parked="the paralogue half of the pair", uid="k2")]),
        thold=_ternary_hold(minutes_old=6, hold=True, mode="edge_reps",
                            reason="2.4x basis — pausing rather than paying double per ns"),
        ledger=_ledger((10, "market-gate", "hold", "task=edge-reps"),
                       (40, "market-gate", "dispatched", "task=triangle"),
                       (20, "rent (steps.rent.outcome=success)", "launched", "task=triangle")),
        schedule=_schedule(("a", "in_progress", []), ("b", "pending", ["a"])),
        strategy="## THE ORDERED PLAN (spend-gated)\n\n### RUNG 7 — x\n"
                 "- **`[~]` A gated item** — **~$8.**\n  **Gate:** Val A satisfied.\n")
    assert doc["_dispatch_plan"] == [], \
        f"a correctly-resting board must dispatch nothing, got {doc['_dispatch_plan']}"
    assert doc["blocked"], "…while still RECORDING what is waiting: quiet is not the same as blind"
    states = {e["state"] for e in doc["entries"]}
    assert wl.BLOCKED in states and wl.HELD in states
    assert "RETRY BUDGET SPENT" not in wl.render_board(doc, root, NOW), \
        "nothing here has spent a budget — only external gates are holding"


# ============================================================================================================
# The ledger must not inherit the single-root blindness — and here it matters MORE than in the watcher,
# because this module DISPATCHES. A lane it cannot see reads as unowned work and gets a gate task fired at
# it every tick.
# ============================================================================================================
def test_source_roots_reach_the_lane_watcher(monkeypatch, tmp_path):
    seen = {}

    def spy(root, now, **kw):
        seen["source_roots"] = kw.get("source_roots")
        return {"lanes": []}, []

    monkeypatch.setattr(wl.lsw, "build_report", spy)
    wl.gather(str(tmp_path), str(tmp_path / "S.md"), str(tmp_path / "s.json"),
              datetime.datetime(2026, 7, 27, 23, 0, tzinfo=datetime.timezone.utc),
              use_api=False, source_roots={"ternary": "/tmp/roots/ternary"})
    assert seen["source_roots"] == {"ternary": "/tmp/roots/ternary"}


def test_a_source_root_pointing_nowhere_is_refused_before_anything_dispatches(tmp_path, capsys):
    rc = wl.main(["--root", str(tmp_path), "--no-api",
                  "--source-root", f"ternary={tmp_path}/nope"])
    assert rc == 2
    assert "is not a directory" in capsys.readouterr().err


# ============================================================================================================
# ★★ THE PLAN DOCUMENT MOVED, AND POINTING AT THE OLD FILE FAILS SILENTLY.
#
# On 2026-08-02 THE ORDERED PLAN was physically moved out of STRATEGY.md into the roadmap
# (`nr4a3-program-map.md`), heading string and bullet format unchanged. `scan_plan_items` reports its own
# blindness rather than returning [], but nothing else does: a `DEFAULT_PLAN_DOC` aimed at a file with no
# ORDERED PLAN heading makes the entire plan layer vanish from the board with a green exit code. These two
# tests read the REAL repo on purpose — the failure they guard is a path, and a fixture cannot see it.
# ============================================================================================================
def test_the_default_plan_document_actually_contains_the_ordered_plan():
    assert os.path.exists(wl.DEFAULT_PLAN_DOC), wl.DEFAULT_PLAN_DOC
    text = open(wl.DEFAULT_PLAN_DOC, encoding="utf-8").read()
    assert any(ln.startswith("## ") and wl._PLAN_HEADING in ln.upper()
               for ln in text.splitlines()), \
        (f"{wl.DEFAULT_PLAN_DOC} has no '## ... {wl._PLAN_HEADING} ...' heading, so scan_plan_items would "
         f"print NOT SCANNED and every open plan item would disappear from the board with no error")
    assert wl.DEFAULT_STRATEGY == wl.DEFAULT_PLAN_DOC, \
        "the legacy --strategy alias must resolve to the same document, never a second one"


def test_the_real_plan_document_yields_open_items():
    text = open(wl.DEFAULT_PLAN_DOC, encoding="utf-8").read()
    got, how = wl.scan_plan_items(text, None)
    assert "NOT SCANNED" not in how, how
    assert got, "the ORDERED PLAN scanned to zero open items — that is indistinguishable from a broken parse"
