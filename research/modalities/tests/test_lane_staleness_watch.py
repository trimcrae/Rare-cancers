"""BOTH DIRECTIONS, OR IT IS NOT A GUARD.

★★ THE SHAPE THAT HAS COST THIS REPO MORE THAN ANY OTHER is a check that reports success while measuring
nothing. A staleness watcher is unusually exposed to it: give every lane a green verdict and the suite passes,
the workflow passes, and the fleet burns. So every failure mode here is tested TWICE — once with a lane that
MUST be condemned, and once with a lane that is legitimately parked or finished and MUST stay quiet. A test
that only proves the alarm can be silent proves nothing.

The pairs, and the real incident each comes from (all 2026-07-27):
    idle-vs-parked       the closure triangle idle for ~3 h  vs  the 5a-KS pair parked with a stated reason
    billing-vs-advancing the valB cohort dead for 85 min      vs  a fan-out whose census is moving
    hold-vs-stall        a §6 price hold with its snapshot    vs  a hold with no snapshot / no market cause
    absent-vs-zero       `live_instances` null, a superseded  vs  an honest measured zero
                         snapshot, `enabled:false` with no reason
"""
from __future__ import annotations

import ast
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import lane_staleness_watch as lsw  # noqa: E402

NOW = datetime.datetime(2026, 7, 27, 22, 0, 0, tzinfo=datetime.timezone.utc)   # 6:00 PM ET
MOD = os.path.join(os.path.dirname(__file__), "..", "lane_staleness_watch.py")


def _ago(minutes):
    return (NOW - datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── builders for the real artifact shapes ────────────────────────────────────────────────────────────────
def _progress(minutes_old=5, live=15, n_units=19, n_complete=1, scalars=None, **kw):
    units = [{"unit_id": f"u{i}", "phase": "leg-complex-running",
              "committed_scalar": (scalars[i] if scalars else 1000000 + i)}
             for i in range(n_units)]
    d = {"_generated_utc": _ago(minutes_old), "n_units": n_units, "n_complete": n_complete,
         "live_instances": live, "instance_states": {"running": max(live or 0, 0)},
         "gpu_util": [0.0] * max(live or 0, 0), "units": units, "realised_usd_so_far": 20.08}
    d.update(kw)
    return d


def _ternary_hold(mode="edge_reps", minutes_old=10, hold=False, live=4, **kw):
    d = {"utc": _ago(minutes_old), "mode": mode, "hold": hold, "nothing_to_launch": False,
         "units_done": [], "units_live": [f"{mode}_u{i}" for i in range(live)],
         "live_host_rates": [{"unit_id": f"{mode}_u{i}", "cur_state": "running"} for i in range(live)],
         "reason": "board cleared both ceilings"}
    d.update(kw)
    return d


def _watch(entries):
    return {"_what": "watch list", "watch": entries}


def _entry(mode, enabled, **kw):
    d = {"unit_id": f"{mode}_unit", "mode": mode, "enabled": enabled}
    d.update(kw)
    return d


def _ledger(*rows):
    return {"_what": "ledger", "attempts": [{"utc": _ago(m), "stage": s, "outcome": o, "reason": r}
                                            for m, s, o, r in rows]}


TRI = next(s for s in lsw.LANES if s["key"] == "closure-triangle")
REPS = next(s for s in lsw.LANES if s["key"] == "ternary-valb-reps")
KS = next(s for s in lsw.LANES if s["key"] == "rung-5aks")
S1 = next(s for s in lsw.LANES if s["key"] == "step1-fanout")
GCP = next(s for s in lsw.LANES if s["key"] == "gcp-ternary-watch")


def _c(st, hist=None):
    return lsw.classify_lane(st, hist, NOW)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PAIR 1 — the gap: a lane idle with nothing holding it, vs a lane parked on purpose
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_FIRES_a_lane_with_no_hosts_and_unfinished_work_and_nothing_holding_it():
    """THE CLOSURE-TRIANGLE CASE. `triangle-prime` succeeded, nothing dispatched the next step, and there is
    no live instance at all — so every liveness check reads it as 'nothing to watch'. It must be condemned."""
    st = lsw.read_ternary_family(
        TRI, _watch([]), None, None, "not present",
        _ledger((190, "triangle-prime", "success", "task=triangle-prime; job status success")), None, False)
    v = _c(st)
    assert v["ok"] is False, v
    assert v["verdict"] == "IDLE-UNEXPECTED", v["verdict"]
    assert "190 min" in v["detail"]


def test_QUIET_the_same_lane_shape_when_every_unfinished_unit_is_deliberately_parked():
    """THE 5a-KS CASE, and the reason this whole module is worth having. Two legs died on a rotated
    credential, are checkpointed, and are off the watch list ON PURPOSE with `_parked_why`. No hosts,
    unfinished work, no hold — identical to the case above on every field except intent. It must stay quiet:
    an alarm that fires on a correct park is ignored within a day."""
    st = lsw.read_ternary_family(
        KS, _watch([_entry("5aks", False, _parked_why="PARKED, NOT FINISHED — credential death, checkpoint "
                                                      "intact, blocked on the $/ns gate"),
                    _entry("5aks", False, _parked_why="the paralogue half of the same pair")]),
        None, None, "not present", _ledger((600, "5aks", "launched", "task=5aks")), None, False)
    v = _c(st)
    assert v["ok"] is True, v
    assert v["verdict"] == "PARKED-GATE", v["verdict"]


def test_QUIET_a_lane_still_inside_the_hand_off_grace():
    st = lsw.read_ternary_family(TRI, _watch([]), None, None, "not present",
                                 _ledger((10, "triangle-prime", "success", "task=triangle-prime")), None, False)
    v = _c(st)
    assert v["ok"] is True and v["verdict"] == "IDLE-WITHIN-GRACE", v


def test_FIRES_parked_units_do_not_cover_an_ENABLED_one():
    """One unit parked and one still enabled is NOT 'everything is parked'. The parked branch must require
    that the parked set covers ALL unfinished work, or a single forgotten live unit hides behind its
    siblings' paperwork."""
    st = lsw.read_ternary_family(
        KS, _watch([_entry("5aks", False, _parked_why="checkpointed, blocked on the gate"),
                    _entry("5aks", True)]),
        None, None, "not present", _ledger((200, "5aks", "launched", "task=5aks")), None, False)
    v = _c(st)
    assert v["ok"] is False and v["verdict"] == "IDLE-UNEXPECTED", v


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PAIR 2 — billing but not advancing, vs billing and advancing
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_FIRES_hosts_up_and_the_committed_iteration_census_has_not_moved():
    """The expensive failure, caught by the ONE signal §6 allows to condemn."""
    st = lsw.read_step1(S1, _progress(minutes_old=5, live=15), None, None, "absent")
    hist = {"census": st.census, "census_since_utc": _ago(120)}
    v = _c(st, hist)
    assert v["ok"] is False and v["verdict"] == "BILLING-NOT-ADVANCING", v
    assert "120 min" in v["detail"]


def test_QUIET_the_same_fleet_when_a_single_unit_advanced():
    """The census is a PER-UNIT fingerprint precisely so one unit moving is visible when the total would not
    be. Movement anywhere resets the clock."""
    st = lsw.read_step1(S1, _progress(minutes_old=5, live=15), None, None, "absent")
    moved = lsw.read_step1(S1, _progress(minutes_old=5, live=15,
                                         scalars=[1000000 + i + (40 if i == 3 else 0) for i in range(19)]),
                           None, None, "absent")
    assert st.census != moved.census, "one unit advancing must change the fingerprint"
    v = _c(moved, {"census": st.census, "census_since_utc": _ago(120)})
    assert v["ok"] is True and v["verdict"] == "ADVANCING", v


def test_a_null_committed_scalar_does_not_break_the_census():
    """A unit that has not committed anything yet legitimately carries null. Refusing the census over it
    would make the STRONG signal unavailable exactly when the fleet is busiest; coercing it to 0 would be the
    absent-as-a-value defect. It is carried verbatim and compares equal to itself."""
    p = _progress(minutes_old=5, live=15, scalars=[None] + [1000000 + i for i in range(18)])
    st = lsw.read_step1(S1, p, None, None, "absent")
    assert st.census is not None and st.census_is_true_iteration_count
    assert "census" not in st.unreadable
    again = lsw.read_step1(S1, p, None, None, "absent")
    assert again.census == st.census


def test_FIRES_hosts_up_with_no_new_evidence_on_a_lane_that_has_no_census():
    """The valB shape: four hosts on the books and 85 minutes of nothing. These lanes keep their counters in
    S3, so the weaker evidence-age signal is all there is — and the verdict says so."""
    st = lsw.read_ternary_family(REPS, _watch([_entry("edge_reps", True)]), None,
                                 _ternary_hold(minutes_old=140), None,
                                 _ledger((400, "market-gate", "dispatched", "task=edge-reps")), None, False)
    v = _c(st)
    assert v["ok"] is False and v["verdict"] == "BILLING-NOT-ADVANCING", v
    assert "weaker" in v["census_basis"]


def test_QUIET_the_same_lane_with_recent_evidence():
    st = lsw.read_ternary_family(REPS, _watch([_entry("edge_reps", True)]), None,
                                 _ternary_hold(minutes_old=12), None,
                                 _ledger((400, "market-gate", "dispatched", "task=edge-reps")), None, False)
    v = _c(st)
    assert v["ok"] is True and v["verdict"] == "ADVANCING", v


def test_gpu_util_is_never_read_anywhere_in_the_module():
    """★ §6: GPU idleness NEVER condemns a box — 0.0 is observed on genuinely advancing hosts. The key sits
    in `step1-fanout-progress.json` right beside the census this module does read, so the guard is an AST
    check on the source rather than a promise in a comment."""
    tree = ast.parse(open(MOD).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value == "gpu_util":
            raise AssertionError("lane_staleness_watch reads `gpu_util`; §6 forbids condemning on it")
        if isinstance(node, ast.Attribute) and node.attr == "gpu_util":
            raise AssertionError("lane_staleness_watch reads `gpu_util`; §6 forbids condemning on it")


def test_a_dead_looking_host_histogram_annotates_but_never_condemns():
    """All four hosts `stopped` is exactly the 85-minute valB cohort — and also exactly a fresh rental
    pulling its image (2 h 57 min observed). The line that separates them is MAX_STOPPED_MIN, which belongs
    to the collector. So this reports loudly and grades nothing."""
    st = lsw.read_ternary_family(
        REPS, _watch([_entry("edge_reps", True)]), None,
        _ternary_hold(minutes_old=12, live_host_rates=[{"unit_id": "u", "cur_state": "stopped"}] * 4),
        None, _ledger((400, "market-gate", "dispatched", "task=edge-reps")), None, False)
    v = _c(st)
    assert v["ok"] is True, "a stopped histogram must not condemn"
    assert "NOT ONE host is `running`" in v["host_state_note"]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PAIR 3 — a hold that is a success, vs a hold that is an incident
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_QUIET_a_correct_price_hold_with_its_market_snapshot():
    """§6: 'I'd rather pause until availability opens than pay double per ns'. This is the gate working."""
    st = lsw.read_ternary_family(
        REPS, _watch([_entry("edge_reps", True)]), None,
        _ternary_hold(minutes_old=200, hold=True, live=0,
                      reason="mean 2.4x basis — refusing to buy the tranche",
                      depth={"offers_returned": 5, "priceable": 2}, offers=[{"gpu": "RTX 4090"}]),
        None, _ledger((200, "market-gate", "hold", "task=edge-reps")), None, False)
    v = _c(st)
    assert v["ok"] is True and v["verdict"] == "PARKED-PRICE-HOLD", v


def test_FIRES_a_price_hold_with_no_market_snapshot_is_UNKNOWN_not_accepted():
    """§6's one prohibition on declining to buy is that it must never be SILENT. A hold with no depth and no
    offers is an unverifiable claim, and 'a fleet that never launched looks identical to one that finished'
    is exactly the ambiguity it re-creates."""
    st = lsw.read_ternary_family(
        REPS, _watch([_entry("edge_reps", True)]), None,
        _ternary_hold(minutes_old=200, hold=True, live=0, reason="too expensive"),
        None, _ledger((200, "market-gate", "hold", "task=edge-reps")), None, False)
    v = _c(st)
    assert v["ok"] is False and v["verdict"] == "UNKNOWN", v


def test_FIRES_a_hold_that_repricing_can_never_clear():
    """`hold_cause == exclusions_or_spec_not_price`: the exclusion set has outgrown the market or the
    ResourceSpec is unsatisfiable. Waiting is the wrong response, so this must NOT read as a quiet park."""
    st = lsw.read_ternary_family(
        REPS, _watch([_entry("edge_reps", True)]), None,
        _ternary_hold(minutes_old=30, hold=True, live=0, hold_cause="exclusions_or_spec_not_price",
                      reason="NOT A PRICE HOLD — 164 offers returned, 0 qualifying after exclusions",
                      depth={"offers_returned": 164, "qualifying": 0}, offers=[{"gpu": "x"}]),
        None, _ledger((30, "market-gate", "hold", "task=edge-reps")), None, False)
    v = _c(st)
    assert v["ok"] is False and v["verdict"] == "HOLD-NOT-PRICE", v


def test_FIRES_an_unreadable_board_is_not_a_price_hold():
    st = lsw.read_ternary_family(
        REPS, _watch([_entry("edge_reps", True)]), None,
        _ternary_hold(minutes_old=30, hold=True, live=0,
                      reason="could not read the board (HTTP 403) — an unreadable market is not a cheap one"),
        None, _ledger((30, "market-gate", "hold", "task=edge-reps")), None, False)
    v = _c(st)
    assert v["ok"] is False and v["verdict"] == "HOLD-NOT-PRICE", v


def test_QUIET_nothing_to_launch_is_not_a_hold_at_all():
    st = lsw.read_ternary_family(
        REPS, _watch([_entry("edge_reps", True)]), None,
        _ternary_hold(minutes_old=12, hold=True, nothing_to_launch=True,
                      reason="every unit already done or hosted; this is NOT a price hold."),
        None, _ledger((12, "market-gate", "nothing-to-launch", "task=edge-reps")), None, False)
    st.hold is False
    v = _c(st)
    assert v["ok"] is True and v["verdict"] == "ADVANCING", v


def test_a_hold_never_excuses_a_lane_that_is_still_billing():
    """★ ORDERING. A hold means 'we declined to BUY'; it says nothing about hosts already running. The first
    draft checked holds first and graded a 15-host fan-out with a 154-minute-old artifact as a quiet price
    hold — money going out, verdict green."""
    st = lsw.read_step1(S1, _progress(minutes_old=200, live=15), None,
                        {"held": True, "held_reason": "board thin", "board_depth": {"offers_returned": 3},
                         "offers_priced": [{"gpu": "x"}]}, None)
    v = _c(st)
    assert v["ok"] is False and v["verdict"] == "BILLING-NOT-ADVANCING", v


def test_an_operator_hold_is_named_rather_than_filed_under_price():
    st = lsw.read_step1(S1, _progress(minutes_old=5, live=0, n_units=19, n_complete=1), None,
                        {"held": True, "held_reason": "FANOUT_PLACEMENT_ENABLED='0' — measure/collect only",
                         "board_depth": {}, "offers_priced": []}, None)
    v = _c(st)
    assert v["ok"] is True and v["verdict"] == "PARKED-BY-OPERATOR", v


def test_an_absent_hold_key_is_unreadable_not_False():
    """The two writers use different key names (`held` vs `hold`). A renamed key must surface, not silently
    read as 'not holding'."""
    st = lsw.read_step1(S1, _progress(minutes_old=5, live=1), None, {"utc": _ago(5)}, None)
    assert "hold" in st.unreadable
    assert _c(st)["verdict"] == "UNKNOWN"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# PAIR 4 — absent must never render as a legal good value
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_FIRES_a_lane_with_nothing_readable_is_UNKNOWN_not_FINISHED():
    """★ THE DEFECT THIS MODULE WAS COMMISSIONED OVER, reproduced in its own first draft: the closure
    triangle — no watch entry, no gate snapshot, no ledger record, no terminus — fell through every branch
    and was graded COMPLETE. 'Nothing is known' and 'it is done' are opposite states."""
    st = lsw.read_ternary_family(TRI, _watch([]), None, None, "not present", {"attempts": []}, None, False)
    v = _c(st)
    assert v["ok"] is False and v["verdict"] == "UNKNOWN", v
    assert "NOT the same as finished" in v["detail"]


def test_QUIET_a_lane_whose_terminal_artifact_really_landed():
    st = lsw.read_ternary_family(TRI, _watch([]), None, None, "not present",
                                 _ledger((300, "triangle-reduce", "success", "task=triangle-reduce")),
                                 None, True)
    v = _c(st)
    assert v["ok"] is True and v["verdict"] == "FINISHED", v


def test_live_instances_null_is_not_the_same_as_zero():
    null = lsw.read_step1(S1, _progress(minutes_old=5, live=None), None, None, "absent")
    zero = lsw.read_step1(S1, _progress(minutes_old=200, live=0), None, None, "absent")
    assert "live_hosts" in null.unreadable and zero.live_hosts == 0
    assert _c(null)["verdict"] == "UNKNOWN"           # unasked -> ungradeable
    assert _c(zero)["verdict"] == "IDLE-UNEXPECTED"   # honest zero -> a real, gradeable state


def test_the_lanes_own_admission_that_it_could_not_read_the_board_is_honoured():
    """`_vast_unreadable` is the tick saying `live_instances` is not a measurement this pass. Believing it
    anyway is how an unmeasured state becomes a measured zero."""
    st = lsw.read_step1(S1, _progress(minutes_old=5, live=0, _vast_unreadable="HTTP 403 from the Vast API"),
                        None, None, "absent")
    assert "live_hosts" in st.unreadable
    assert _c(st)["verdict"] == "UNKNOWN"


def test_a_snapshot_superseded_by_a_SUCCESSFUL_RENTAL_is_a_lower_bound_not_an_unknown():
    """★ CAUGHT BY THE FIRST CI DISPATCH (6:42 PM ET 2026-07-27). The gate snapshot read `units_live: []` at
    6:20 PM ET and the ledger recorded a successful rental at 6:25 PM ET — the lane had JUST RENTED, the
    healthiest thing it can do, and the watcher announced it could not tell billing from idle. Every rental
    would have produced a red window until the next gate evaluation: the cry-wolf failure this module exists
    to avoid. A rental is POSITIVE evidence of a host, so the count is a lower bound."""
    st = lsw.read_ternary_family(
        REPS, _watch([_entry("edge_reps", True)]), None,
        _ternary_hold(minutes_old=140, live=0), None,
        _ledger((20, "rent (steps.rent.outcome=success)", "launched", "task=edge-reps; job status success")),
        None, False)
    assert st.live_hosts == 1 and "live_hosts" not in st.unreadable
    v = _c(st)
    assert v["ok"] is True and v["verdict"] == "ADVANCING", v


def test_a_snapshot_superseded_by_something_that_is_NOT_a_rental_stays_unreadable():
    """The other direction. A failed stage after the snapshot could mean a teardown, so the count really is
    superseded and really is unknown — and a lane whose host count is unknown cannot be graded either way."""
    st = lsw.read_ternary_family(
        REPS, _watch([_entry("edge_reps", True)]), None,
        _ternary_hold(minutes_old=140, live=4), None,
        _ledger((20, "rent (steps.rent.outcome=skipped)", "failed", "task=edge-reps; job status failure")),
        None, False)
    assert st.live_hosts is None and "superseded" in st.unreadable["live_hosts"]
    v = _c(st)
    assert v["ok"] is False and v["verdict"] == "UNKNOWN", v


def test_an_enabled_false_entry_with_neither_reason_key_is_unreadable():
    """The watch list's own `_parked_is_not_finished`: `_disabled_why` = landed, `_parked_why` = interrupted
    and NOT done. Same boolean, opposite meanings. An entry carrying neither is not guessed at."""
    st = lsw.read_ternary_family(KS, _watch([_entry("5aks", False)]), None, None, "not present",
                                 _ledger((300, "5aks", "launched", "task=5aks")), None, False)
    assert "watch_entry_intent" in st.unreadable
    v = _c(st)
    assert v["ok"] is False and v["verdict"] == "UNKNOWN", v


def test_a_gate_snapshot_belonging_to_another_lane_is_not_read_as_this_lanes_state():
    """`ternary-vast-market-hold.json` is the `--gate-out` for every non-triangle ternary mode, so one lane's
    healthy gate must never vouch for another's silence."""
    st = lsw.read_ternary_family(
        KS, _watch([_entry("5aks", True)]), None, _ternary_hold(mode="edge_reps", minutes_old=2), None,
        _ledger((300, "5aks", "launched", "task=5aks")), None, False)
    assert st.live_hosts is None or st.live_hosts == 0
    assert any("NOT this lane" in n for n in st.notes)
    v = _c(st)
    assert v["ok"] is False and v["verdict"] == "IDLE-UNEXPECTED", v


def test_the_ledger_separates_sibling_lanes_on_the_same_workflow():
    """`gpu-ternary-fep-vast.yml` serves the replicates, the triangle and 5a-KS. A triangle run must not
    vouch for the replicate lane's silence."""
    led = _ledger((5, "market-gate", "dispatched", "task=triangle-smoke"),
                  (300, "market-gate", "dispatched", "task=edge-reps"))
    reps = lsw.read_ternary_family(REPS, _watch([_entry("edge_reps", True)]), None, None, "gone", led, None,
                                   False)
    tri = lsw.read_ternary_family(TRI, _watch([]), None, None, "gone", led, None, False)
    assert (NOW - reps.last_evidence_utc).total_seconds() / 60 > 200
    assert (NOW - tri.last_evidence_utc).total_seconds() / 60 < 10


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the GCP lane — graded on ticks, because host liveness is provably not in git
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_gcp_lane_is_graded_on_ticks_not_on_a_host_count_it_cannot_read():
    """§6: GCE REFUSES the in-VM self-delete, so a finished leg can leave a RUNNING VM, and an enabled entry
    can correspond to no VM at all. Grading it UNKNOWN every run would be an alarm that is always red."""
    st = lsw.read_gcp_watch(GCP, _watch([{"enabled": True, "leg_id": "calib_hi_to_lo__binary_vhl"}]), None)
    assert st.hosts_knowable is False
    v = _c(st)
    assert v["ok"] is True and v["verdict"] == "TICKING", v


def test_the_gcp_lane_still_goes_UNKNOWN_when_its_watch_list_cannot_be_read():
    st = lsw.read_gcp_watch(GCP, None, "ternary-watch.json: not present in the repo")
    v = _c(st)
    assert v["ok"] is False and v["verdict"] == "UNKNOWN", v


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the shared relaunch gate — attribution, and the permanently-silent hold
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_a_permanently_silent_hold_is_surfaced():
    """`escalation_clock: UNAVAILABLE` means `held_hours` restarts every pass, so the unit can NEVER
    self-escalate — a hold that will sit forever without ever raising its voice."""
    esc = lsw.read_relaunch_escalation(
        {"lane": "step1_fanout", "units": {"u1": {"held": True, "escalation_clock": "UNAVAILABLE — the hold "
                                                 "state could not be persisted"}}}, None)
    assert esc["lane"] == "step1_fanout"
    assert any("self-escalate" in w for w in esc["warnings"])


def test_the_relaunch_gate_warning_is_attributed_to_the_lane_that_wrote_it(tmp_path):
    """ONE file, two writers (`lane: step1_fanout` and `lane: ternary`). Reading it without checking `lane`
    credits one lane's trouble to another."""
    root = tmp_path / "m"
    root.mkdir()
    (root / "relaunch-market-hold.json").write_text(json.dumps(
        {"lane": "ternary", "units": {"u": {"escalation_clock": "UNAVAILABLE"}}}))
    (root / "step1-fanout-progress.json").write_text(json.dumps(_progress()))
    (root / "ternary-vast-watch.json").write_text(json.dumps(_watch([_entry("edge_reps", True)])))
    (root / "ternary-vast-launch-attempts.json").write_text(json.dumps(
        _ledger((10, "market-gate", "dispatched", "task=edge-reps"))))
    (root / "ternary-watch.json").write_text(json.dumps(_watch([])))
    states, _ = lsw.gather(str(root))
    by = {s.key: s for s in states}
    assert by["ternary-valb-reps"].warnings, "the writing lane must carry the warning"
    assert not by["step1-fanout"].warnings, "a sibling lane must NOT inherit it"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# history — and why a failed write cannot manufacture an alarm
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_census_since_moves_only_when_the_census_changes():
    a = lsw.read_step1(S1, _progress(), None, None, "absent")
    h1 = lsw.update_history({}, [a], NOW)
    later = NOW + datetime.timedelta(minutes=30)
    h2 = lsw.update_history(h1, [a], later)
    assert h2["lanes"]["step1-fanout"]["census_since_utc"] == h1["lanes"]["step1-fanout"]["census_since_utc"]
    b = lsw.read_step1(S1, _progress(scalars=[2000000 + i for i in range(19)]), None, None, "absent")
    h3 = lsw.update_history(h2, [b], later)
    assert h3["lanes"]["step1-fanout"]["census_since_utc"] == later.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_a_stale_history_under_reports_flatness_rather_than_inventing_it():
    """If the commit-back fails the stored census stays old. If the real census has advanced it DIFFERS, so
    the clock resets and flatness is under-reported — the quiet direction. Fail-safe, deliberately."""
    old = lsw.read_step1(S1, _progress(), None, None, "absent")
    stale_hist = {"census": old.census, "census_since_utc": _ago(500)}
    moved = lsw.read_step1(S1, _progress(scalars=[2000000 + i for i in range(19)]), None, None, "absent")
    v = _c(moved, stale_hist)
    assert v["census_flat_for_min"] is None, "a changed census must never inherit an old flat clock"
    assert v["ok"] is True


def test_no_history_at_all_cannot_condemn_on_flatness():
    st = lsw.read_step1(S1, _progress(minutes_old=5, live=15), None, None, "absent")
    v = _c(st, None)
    assert v["census_flat_for_min"] is None
    assert v["ok"] is True and v["verdict"] == "ADVANCING"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# structural guarantees
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_it_imports_nothing_from_the_lanes_it_watches():
    """An alarm that shares a dependency with the thing it watches dies with it — which is exactly how the
    11:37 AM tick took its own progress check down. The one permitted import is `fleet_supervision_alarm`,
    itself dependency-free, imported so its throttle-immune test is REUSED rather than reimplemented."""
    tree = ast.parse(open(MOD).read())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    # `re` joined the list on 2026-08-01 with the selcal lane: its co-fold census has no timestamp KEY, only
    # an ISO-Z stamp embedded in `phase`, and extracting that real tick stamp is strictly better than falling
    # back to a weaker signal. Still stdlib, so the property this test defends — nothing here can be taken
    # down by the lanes it watches — is untouched.
    allowed = {"argparse", "datetime", "hashlib", "json", "os", "re", "sys", "ast",
               "fleet_supervision_alarm", "__future__"}
    assert imported <= allowed, f"unexpected imports: {imported - allowed}"
    for banned in ("boto3", "congeneric_fanout", "ternary_vast_launch", "vast_cost_model", "requests"):
        assert not any(banned in i for i in imported), f"must not import {banned}"


def test_it_can_neither_rent_nor_destroy_nor_reap():
    """Report-only is a structural property, not a promise: a watcher that could also act would be a second
    unreviewed control path. No destructive verb may appear as a call in the source."""
    src = open(MOD).read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            assert name not in ("destroy", "reap", "rent", "submit", "launch", "collect", "nudge",
                                "urlopen", "run", "Popen", "system"), f"destructive/side-effecting call {name}"


def test_every_lane_in_the_registry_can_be_read_without_crashing(tmp_path):
    """A registry entry whose reader raises would silently drop a lane from the board — 'not watched' and
    'healthy' must never render alike."""
    states, _ = lsw.gather(str(tmp_path))     # an EMPTY tree: every artifact missing
    assert len(states) == len(lsw.LANES)
    report, _ = lsw.build_report(str(tmp_path), NOW, use_api=False)
    assert report["n_lanes"] == len(lsw.LANES)
    assert report["ok"] is False, "a tree with no artifacts at all must never grade green"
    assert all(v["verdict"] == "UNKNOWN" for v in report["lanes"]), [v["verdict"] for v in report["lanes"]]


def test_the_ok_verdict_set_matches_what_classify_actually_returns():
    """A verdict name added to the classifier but not to OK_VERDICTS (or the glyph table) renders as '?' and
    grades by accident. Keep them in step."""
    src = open(MOD).read()
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "classify_lane")
    names = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Tuple) and any(
                    isinstance(e, ast.Subscript) and isinstance(e.slice, ast.Constant)
                    and e.slice.value == "verdict" for e in t.elts):
                if isinstance(node.value, ast.Tuple) and isinstance(node.value.elts[0], ast.Constant):
                    names.add(node.value.elts[0].value)
    assert names, "could not extract any verdict names — the test would pass vacuously"
    assert names <= set(lsw._GLYPH), f"verdicts with no glyph: {names - set(lsw._GLYPH)}"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# end to end, on two complete fixture trees — the both-directions proof at the top level
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _retro_frag(minutes_old=5, outstanding=2, note="16 of 18 authorized R1 leg(s) landed."):
    """The NR-V04 retrospective's board fragment — the only repo-visible fact about that lane. Its
    `generated_utc` IS the evidence that the lane's tick is still running, which is why the lane is
    registered at all: a supervision that stops must be loud, not merely absent."""
    ts = NOW - datetime.timedelta(minutes=minutes_old)
    return {"lane": "nrv04-retro", "generated_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"), "note": note,
            "rows": [{"name": "nr4a3 m%d r0" % i, "state": "RUNNING", "why": ""} for i in range(outstanding)]}


def _selcal_census(minutes_old=5, missing=1, complete=False):
    """The selectivity-control lane's co-fold census. ⚠ IT HAS NO TIMESTAMP KEY — its only tick stamp is the
    ISO-Z embedded in `phase`, which is why `read_selcal` extracts one. Fixture mirrors the real artifact's
    shape exactly, because a fixture that invented a `generated_utc` would test a lane that does not exist."""
    ts = NOW - datetime.timedelta(minutes=minutes_old)
    return {"prefix": "selcal-smarca-cofold-v1",
            "per_arm": {"selcal_smarca2": [1, 2, 3], "selcal_smarca4": [1, 2, 3]},
            "missing": [{"arm": "selcal_smarca4", "seed": i, "n_cif": 0, "why": "absent"}
                        for i in range(missing)],
            "complete": complete,
            "n_models_per_arm": {"selcal_smarca2": 3, "selcal_smarca4": 3},
            "phase": "done rc=0 %s instance=46508454 attempt=20260801T144027Z"
                     % ts.strftime("%Y-%m-%dT%H:%M:%SZ")}


def _selcal_hold(hold=False, reason="1.69x the ladder basis is within the 1.92x drift line"):
    return {"lane": "selcal", "utc": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "hold": hold, "reason": reason,
            "board_depth": {"offers_returned": 136, "qualifying": 136, "priceable": 68},
            "offers_priced": [{"gpu": "RTX 5090", "machine_id": 28759}]}


def _selcal_reap(minutes_old=3, spared=()):
    """The MD panel's reap artifact — written on EVERY tick, reaping nothing included, which is what makes it
    this lane's heartbeat as well as its host list."""
    ts = NOW - datetime.timedelta(minutes=minutes_old)
    return {"lane": "selcal", "utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"), "stop_all": False,
            "s3_census_readable": True, "destroyed": [], "spared": list(spared)}


def _selcal_collect(landed=22, expected=22, missing=()):
    return {"utc": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "expected": expected, "landed": landed,
            "missing": list(missing), "panel_complete": not missing, "expected_at_freeze": 24,
            "excluded_cofold_models": {}}


def _selcal_ledger(n=12, uptime_min=30.0):
    """⚠ `overrun_budget_min` REFUSES on fewer than 8 priced rentals, so a fixture with three would exercise
    the refusal path rather than the budget. Twelve is the smallest honest 'this lane has a distribution'."""
    return {"lane": "selcal", "n_rentals": n,
            # ⚠ `why` MATTERS: only rentals that BANKED a leg count toward the budget, so a fixture that
            # omitted it would silently exercise the refusal path and look like a passing test.
            "rentals": [{"label": "selcal-smarca2-m1-r0", "uptime_s": uptime_min * 60.0,
                         "why": "work banked, no remaining role"} for _ in range(n)]}


def _tree(path, *, progress, watch, hold, ledger, gcp=None, retro=None, selcal=None, selcal_hold=None,
          selcal_reap=None, selcal_collect=None, selcal_ledger=None):
    path.mkdir(parents=True, exist_ok=True)
    (path / "inflight-board.d").mkdir(parents=True, exist_ok=True)
    (path / "inflight-board.d" / "nrv04-retro.json").write_text(
        json.dumps(retro if retro is not None else _retro_frag()))
    (path / "selcal-cofold-census.json").write_text(
        json.dumps(selcal if selcal is not None else _selcal_census()))
    (path / "selcal-reap.json").write_text(
        json.dumps(selcal_reap if selcal_reap is not None else _selcal_reap()))
    (path / "selcal-collect.json").write_text(
        json.dumps(selcal_collect if selcal_collect is not None else _selcal_collect()))
    (path / "selcal-price-ledger.json").write_text(
        json.dumps(selcal_ledger if selcal_ledger is not None else _selcal_ledger()))
    (path / "selcal-market-hold.json").write_text(
        json.dumps(selcal_hold if selcal_hold is not None else _selcal_hold()))
    (path / "step1-fanout-progress.json").write_text(json.dumps(progress))
    (path / "ternary-vast-watch.json").write_text(json.dumps(watch))
    if hold is not None:
        (path / "ternary-vast-market-hold.json").write_text(json.dumps(hold))
    (path / "ternary-vast-launch-attempts.json").write_text(json.dumps(ledger))
    (path / "ternary-watch.json").write_text(json.dumps(gcp if gcp is not None else _watch([])))
    return path


def test_END_TO_END_a_stale_board_is_condemned(tmp_path):
    root = _tree(tmp_path / "stale",
                 progress=_progress(minutes_old=200, live=15),
                 watch=_watch([_entry("edge_reps", True)]),
                 hold=_ternary_hold(minutes_old=300),
                 ledger=_ledger((300, "market-gate", "dispatched", "task=edge-reps"),
                                (240, "triangle-prime", "success", "task=triangle-prime")))
    report, _ = lsw.build_report(str(root), NOW, use_api=False)
    by = {v["lane"]: v for v in report["lanes"]}
    assert report["ok"] is False
    assert by["step1-fanout"]["verdict"] == "BILLING-NOT-ADVANCING"
    assert by["ternary-valb-reps"]["verdict"] == "BILLING-NOT-ADVANCING"
    assert by["closure-triangle"]["verdict"] == "IDLE-UNEXPECTED"


def test_END_TO_END_a_healthy_and_correctly_parked_board_is_quiet(tmp_path):
    """Same five lanes, same code path, every one legitimately explained: a fan-out advancing, a replicate
    lane on a §6 price hold with its snapshot, a triangle whose reduction landed, a 5a-KS pair parked with a
    stated reason, and a GCP watch list being ticked. NOTHING may fire."""
    root = _tree(tmp_path / "healthy",
                 progress=_progress(minutes_old=6, live=15),
                 watch=_watch([_entry("edge_reps", True),
                               _entry("5aks", False, _parked_why="checkpointed; blocked on the $/ns gate"),
                               _entry("5aks", False, _parked_why="the paralogue half of the pair")]),
                 hold=_ternary_hold(minutes_old=8, hold=True, live=0,
                                    reason="2.4x basis — pausing rather than paying double per ns",
                                    depth={"offers_returned": 5}, offers=[{"gpu": "RTX 4090"}]),
                 ledger=_ledger((8, "market-gate", "hold", "task=edge-reps"),
                                (300, "triangle-reduce", "success", "task=triangle-reduce")),
                 gcp=_watch([{"enabled": True, "leg_id": "calib_hi_to_lo__binary_vhl"}]))
    (root / "valb-triangle-reduction.json").write_text(json.dumps({"R_kcal": 0.31}))
    report, _ = lsw.build_report(str(root), NOW, use_api=False)
    by = {v["lane"]: v["verdict"] for v in report["lanes"]}
    assert report["ok"] is True, [v for v in report["lanes"] if not v["ok"]]
    assert by == {"step1-fanout": "ADVANCING", "ternary-valb-reps": "PARKED-PRICE-HOLD",
                  "closure-triangle": "FINISHED", "rung-5aks": "PARKED-GATE",
                  "nrv04-retro": "ADVANCING", "selcal-cofold": "TICKING",
                  "selcal-md": "FINISHED",
                  "gcp-ternary-watch": "TICKING"}, by


def test_selcal_reads_its_tick_stamp_out_of_phase_and_never_defaults_it(tmp_path):
    """The selcal lane's census has NO timestamp key — only an ISO-Z inside `phase`. Reading it is what makes
    "the selcal tick stopped at 10:14 AM ET" knowable at all; defaulting it would have rendered the lane that
    failed on 2026-08-01 as either permanently fresh or permanently dead, both lies."""
    root = _tree(tmp_path / "selcal",
                 progress=_progress(minutes_old=6, live=15),
                 watch=_watch([_entry("edge_reps", True)]),
                 hold=_ternary_hold(minutes_old=8, live=2),
                 ledger=_ledger((8, "market-gate", "launched", "task=edge-reps")),
                 selcal=_selcal_census(minutes_old=42))
    report, _ = lsw.build_report(str(root), NOW, use_api=False)
    st = next(v for v in report["lanes"] if v["lane"] == "selcal-cofold")["state"]
    assert st["last_evidence_utc"] == (NOW - datetime.timedelta(minutes=42)).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert "phase" in st["last_evidence_what"]
    # ★ AND ITS HOSTS ARE NOT CLAIMED TO BE KNOWN. The gate's `n_hosts` is what it wanted to BUY; reading it
    # as a host count is a populated field masquerading as a measured one (§4). `account_orphan_alarm.py`
    # supplies the account-side host count instead, and the two do not import each other.
    assert st["hosts_knowable_from_git"] is False


def test_selcal_with_an_unparseable_phase_is_unknown_not_fresh(tmp_path):
    """Absent is never a legal good value: a census whose `phase` carries no stamp must not read as a lane
    that just ticked."""
    bad = _selcal_census()
    bad["phase"] = "running (no timestamp here)"
    root = _tree(tmp_path / "badphase",
                 progress=_progress(minutes_old=6, live=15),
                 watch=_watch([_entry("edge_reps", True)]),
                 hold=_ternary_hold(minutes_old=8, live=2),
                 ledger=_ledger((8, "market-gate", "launched", "task=edge-reps")),
                 selcal=bad)
    report, _ = lsw.build_report(str(root), NOW, use_api=False)
    v = next(x for x in report["lanes"] if x["lane"] == "selcal-cofold")
    assert v["verdict"] == "UNKNOWN" and v["ok"] is False


def test_selcal_complete_true_while_still_missing_models_is_surfaced_not_resolved(tmp_path):
    """The writer's verdict and its own evidence disagreeing is a fact worth reporting, and neither is
    believed over the other — silently preferring `complete` would let a half-finished panel read as done."""
    root = _tree(tmp_path / "contradiction",
                 progress=_progress(minutes_old=6, live=15),
                 watch=_watch([_entry("edge_reps", True)]),
                 hold=_ternary_hold(minutes_old=8, live=2),
                 ledger=_ledger((8, "market-gate", "launched", "task=edge-reps")),
                 selcal=_selcal_census(missing=2, complete=True))
    report, _ = lsw.build_report(str(root), NOW, use_api=False)
    st = next(v for v in report["lanes"] if v["lane"] == "selcal-cofold")["state"]
    assert any("disagree" in w for w in (st["warnings"] or [])), st["warnings"]


# ============================================================================================================
# Per-lane artifact roots. The lanes do NOT all live on one branch: step 1 commits to the fleet branch, the
# ternary family is dispatched with ref=main and commits to main. Reading them all from one root made the
# watcher 100 min stale on the ternary lanes and blind to the closure triangle entirely, and it reported that
# blindness as two RED lanes that were in fact billing and healthy.
# ============================================================================================================
def test_every_lane_declares_where_its_artifacts_live():
    # A new lane that forgets this would silently inherit --root, which is exactly how the bug arrived.
    missing = [s["key"] for s in lsw.LANES if not s.get("artifact_source")]
    assert missing == [], f"lanes with no artifact_source: {missing}"


def test_same_filename_on_two_roots_is_not_served_from_one_cache(tmp_path):
    # `ternary-vast-market-hold.json` is read by three lanes; two roots hold DIFFERENT bytes for it. A
    # filename-only cache key would hand one branch's content to the other branch's lane.
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(), b.mkdir()
    (a / "ternary-vast-market-hold.json").write_text(json.dumps({"mode": "from-root-a"}))
    (b / "ternary-vast-market-hold.json").write_text(json.dumps({"mode": "from-root-b"}))
    specs = [dict(s) for s in lsw.LANES if s["key"] in ("ternary-valb-reps", "rung-5aks")]
    specs[0]["artifact_source"] = "sa"
    specs[1]["artifact_source"] = "sb"
    states, _ = lsw.gather(str(a), specs, {"sa": str(a), "sb": str(b)})
    assert len(states) == 2


def test_an_unmapped_source_falls_back_to_root(tmp_path):
    # Backwards compatibility: a caller that passes no mapping must behave exactly as before.
    (tmp_path / "step1-fanout-progress.json").write_text(json.dumps(
        {"_generated_utc": "2026-07-27T23:00:00Z", "n_units": 1, "n_complete": 0,
         "live_instances": 1, "units": [], "instance_states": {}}))
    specs = [dict(s) for s in lsw.LANES if s["key"] == "step1-fanout"]
    states, _ = lsw.gather(str(tmp_path), specs, {})          # nothing mapped
    assert states[0].key == "step1-fanout"


def test_a_source_root_that_is_not_a_directory_is_a_config_error_not_a_false_alarm(tmp_path, capsys):
    # Pointing at nowhere would read an EMPTY directory, and absent artifacts read as "no evidence" —
    # i.e. every ternary lane would go red for a typo. Refuse instead.
    rc = lsw.main(["--root", str(tmp_path), "--no-api",
                 "--source-root", f"ternary={tmp_path}/does-not-exist"])
    assert rc == 2
    assert "is not a directory" in capsys.readouterr().err


def test_a_malformed_source_root_is_rejected(tmp_path, capsys):
    rc = lsw.main(["--root", str(tmp_path), "--no-api", "--source-root", "ternary-no-equals-sign"])
    assert rc == 2
    assert "must be SOURCE=DIR" in capsys.readouterr().err


# ============================================================================================================
# ★★ THE NR-V04 RETROSPECTIVE, registered 2026-07-31. It is here for ONE reason: before that day the lane had
# no automation at all and no watcher, so "the retro tick stopped" and "the retro lane is fine" produced the
# same output — nothing. A lane that is not named cannot go loud.
# ============================================================================================================

def test_the_retro_lane_goes_loud_when_its_tick_stops(tmp_path):
    """The NEGATIVE CONTROL for registering it. A fragment hours old means nothing has reaped, guarded or
    re-placed that lane in hours — exactly the silence that stranded 5a-KS legs the same morning."""
    root = _tree(tmp_path / "retro-stale",
                 progress=_progress(minutes_old=6, live=15),
                 watch=_watch([_entry("edge_reps", True)]),
                 hold=_ternary_hold(minutes_old=8, hold=True, live=0,
                                    reason="2.4x basis", depth={"offers_returned": 5},
                                    offers=[{"gpu": "RTX 4090"}]),
                 ledger=_ledger((8, "market-gate", "hold", "task=edge-reps"),
                                (300, "triangle-reduce", "success", "task=triangle-reduce")),
                 retro=_retro_frag(minutes_old=400, outstanding=16))
    (root / "valb-triangle-reduction.json").write_text(json.dumps({"R_kcal": 0.31}))
    report, _ = lsw.build_report(str(root), NOW, use_api=False)
    retro = next(v for v in report["lanes"] if v["lane"] == "nrv04-retro")
    assert retro["ok"] is False, retro
    assert report["ok"] is False


def test_a_finished_retro_panel_is_not_read_as_an_idle_one(tmp_path):
    """A landed leg is deliberately NOT rowed (`retro_board_rows`), so zero rows means the panel is DONE,
    never that the fleet decayed. Getting this backwards would fire an alarm on success."""
    spec = next(s for s in lsw.LANES if s["key"] == "nrv04-retro")
    st = lsw.read_nrv04_retro(spec, _retro_frag(minutes_old=3, outstanding=0,
                                                note="18 of 18 authorized R1 leg(s) landed."),
                              None, None, "none")
    assert st.finished is True and st.unfinished == 0


def test_the_retro_reader_records_what_it_could_not_read_rather_than_defaulting():
    spec = next(s for s in lsw.LANES if s["key"] == "nrv04-retro")
    st = lsw.read_nrv04_retro(spec, None, "fragment absent", None, "none")
    assert st.unreadable and st.finished is None and st.live_hosts is None


def test_the_retro_census_is_not_claimed_to_be_an_iteration_count():
    """Only a true committed-iteration census may condemn a lane hard (read_step1). This one is a board-state
    fingerprint and must say so, or it would borrow authority it has not earned."""
    spec = next(s for s in lsw.LANES if s["key"] == "nrv04-retro")
    st = lsw.read_nrv04_retro(spec, _retro_frag(), None, None, "none")
    assert st.census_is_true_iteration_count is False


# =============================================================================================================
# the MD panel — the half of the selcal lane that bills, and that was registered NOWHERE until it cost 4.5 h
# =============================================================================================================
def test_selcal_md_warns_on_a_host_that_has_outlived_the_lanes_OWN_p90(tmp_path):
    """★★ THE OBSERVATION THAT HAD TO BE MADE BY HAND, 2026-08-02. `selcal-smarca4-m2-r0` sat `running` for
    275 min at `gpu_util: 0.0` with nothing landed, against a lane whose median rental was 30.3 min. Nothing
    in the repo was going to say so: the only selcal row on the board covered the CO-FOLD stage and read
    `FINISHED … nothing is billing`, which was true of that stage and false of the lane.

    The budget is DERIVED from this lane's own ledger, never typed — a constant would be wrong the first time
    the card or the sampling length changed.
    """
    root = _tree(tmp_path / "overrun",
                 progress=_progress(minutes_old=6, live=15), watch=_watch([]),
                 hold=_ternary_hold(minutes_old=8, hold=False, live=1),
                 ledger=_ledger((8, "market-gate", "ok", "task=edge-reps")),
                 selcal_collect=_selcal_collect(landed=21, expected=22, missing=["selcal-smarca4-m2-r0"]),
                 selcal_ledger=_selcal_ledger(n=12, uptime_min=30.0),
                 selcal_reap=_selcal_reap(spared=[
                     {"instance": "46539144", "label": "selcal-smarca4-m2-r0", "status": "running",
                      "uptime_min": 275.2, "dph_total": 0.1819, "host_phase": None}]))
    report, _ = lsw.build_report(str(root), NOW, use_api=False)
    # ⚠ THE LANE'S FIELDS LIVE UNDER `state`, not at the top of the verdict — the top level carries the
    # CLASSIFICATION (verdict/ok/detail) and `state` carries what was measured. Reading the top level returns
    # None for every field and a test asserting on it would pass by accident the moment a field went missing.
    md = next(v for v in report["lanes"] if v["lane"] == "selcal-md")["state"]
    assert md["live_hosts"] == 1
    warns = " ".join(md.get("warnings") or [])
    assert "selcal-smarca4-m2-r0" in warns and "275" in warns
    assert "diag" in warns, "the warning must name the action that turns it into a diagnosis"
    # ⛔ A WARNING IS NOT A CONDEMNATION. Nothing here may reap: `reap_decision` destroys on host-written
    # evidence only, and a slow leg is not a dead one.
    assert "reap" not in warns.lower() or "nothing reaps" in warns.lower()


def test_selcal_md_refuses_to_invent_a_budget_from_too_few_rentals(tmp_path):
    """⚠ §4 — a p90 of three points is a number that LOOKS measured. Refusing is the honest output, and the
    refusal must be VISIBLE rather than silently producing no warnings."""
    B = "work banked, no remaining role"
    budget, why = lsw.overrun_budget_min([{"uptime_s": 1800.0, "why": B}] * 3)
    assert budget is None and "too few" in why
    budget2, why2 = lsw.overrun_budget_min(None)
    assert budget2 is None and "unreadable" in why2
    budget3, _ = lsw.overrun_budget_min([{"uptime_s": 60.0 * m, "why": B} for m in range(10, 22)])
    assert budget3 is not None and budget3 > 0

    # ★★ THE CORRECTION THAT MATTERS, measured 2026-08-02. Rentals that never banked a leg measure how fast
    # this lane FAILS, not how long its work takes — and there were 36 of them against 22 that finished.
    # Including them dragged the median from 42.3 min down to 34.1: a budget built mostly from things that
    # never ran, wearing the same units as one built from things that did.
    banked = [{"uptime_s": 60.0 * m, "why": B} for m in range(40, 52)]
    failures = [{"uptime_s": 60.0 * 2, "why": "terminal state 'exited'"} for _ in range(30)]
    only_banked, _ = lsw.overrun_budget_min(banked)
    with_failures, why4 = lsw.overrun_budget_min(banked + failures)
    assert only_banked == with_failures, "a non-banking rental must not move the budget at all"
    assert "excluded" in why4, "and the reader must be told how many were dropped, and why"
    # A ledger of nothing but failures cannot produce a budget, however long it is.
    none_banked, why5 = lsw.overrun_budget_min(failures)
    assert none_banked is None and "BANKED" in why5


def test_selcal_md_reports_the_frozen_shape_beside_the_live_one(tmp_path):
    """A completed 22-unit panel must never be indistinguishable from the 24 the criterion was frozen
    against, so the exclusion travels with the count — read from the ARTIFACT, never by importing the lane."""
    root = _tree(tmp_path / "excl",
                 progress=_progress(minutes_old=6, live=15), watch=_watch([]),
                 hold=_ternary_hold(minutes_old=8, hold=False, live=1),
                 ledger=_ledger((8, "market-gate", "ok", "task=edge-reps")),
                 selcal_collect={**_selcal_collect(landed=22, expected=22),
                                 "excluded_cofold_models": {
                                     "selcal_smarca4:m3": "input fault: 0.693 A, cofold_input_audit"}})
    report, _ = lsw.build_report(str(root), NOW, use_api=False)
    md = next(v for v in report["lanes"] if v["lane"] == "selcal-md")["state"]
    parked = " ".join(md.get("parked_units") or [])
    assert "selcal_smarca4:m3" in parked and "0.693" in parked
