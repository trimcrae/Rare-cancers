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


def test_a_gate_snapshot_older_than_the_lanes_last_rental_is_not_a_host_count():
    """MEASURED while building this module: the gate snapshot read `units_live: []` at 3:38 PM ET and the
    ledger recorded a successful rental for the same lane at 4:00 PM ET. Believing the snapshot announces
    four freshly-rented hosts as IDLE-UNEXPECTED — a false alarm on the verdict this module exists to make
    trustworthy. A superseded count is UNREADABLE, not zero."""
    st = lsw.read_ternary_family(
        REPS, _watch([_entry("edge_reps", True)]), None,
        _ternary_hold(minutes_old=140, live=0), None,
        _ledger((20, "rent (steps.rent.outcome=success)", "launched", "task=edge-reps; job status success")),
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
    allowed = {"argparse", "datetime", "hashlib", "json", "os", "sys", "ast", "fleet_supervision_alarm",
               "__future__"}
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
def _tree(path, *, progress, watch, hold, ledger, gcp=None):
    path.mkdir(parents=True, exist_ok=True)
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
                  "gcp-ternary-watch": "TICKING"}, by
