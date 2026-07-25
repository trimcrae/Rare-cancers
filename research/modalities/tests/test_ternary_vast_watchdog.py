#!/usr/bin/env python3
"""Pure-logic tests for the Vast ternary watchdog.

The watchdog's whole value is that it is right when nobody is awake, so its decision function is separated
from every I/O call and tested here. The cases that matter are the ones that cost money or lose work:
calling a live-but-idle host RUNNING, relaunching on top of a leg that is still going, relaunching a stall
that will hang the same way, and acting at all when the instance list could not be read.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_vast_watchdog as wd  # noqa: E402


def _c(**kw):
    base = dict(has_result=False, instance_alive=True, instance_age_min=10.0,
                progress_scalar=100, prev_scalar=50, prev_stall=0)
    base.update(kw)
    return wd.classify(**base)


# ---------------------------------------------------------------- the three questions
def test_result_present_is_done_regardless_of_everything_else():
    assert _c(has_result=True, instance_alive=True)[0] == "DONE"
    assert _c(has_result=True, instance_alive=False, progress_scalar=0)[0] == "DONE"


def test_no_result_and_no_instance_is_died():
    assert _c(instance_alive=False)[0] == "DIED"


def test_advancing_instance_is_running():
    assert _c(progress_scalar=140, prev_scalar=100)[0] == "RUNNING"


# ---------------------------------------------------------------- "alive" is not "advancing"
def test_alive_but_frozen_is_a_stall_not_running():
    """THE Vast-specific correction. A rented instance can sit up with a dead container or an idle GPU and
    look perfectly healthy; only the committed iteration count says whether the science moved."""
    v, stall = _c(progress_scalar=100, prev_scalar=100, prev_stall=0)
    assert (v, stall) == ("RUNNING", 1), "one frozen tick is not yet a stall"
    v, stall = _c(progress_scalar=100, prev_scalar=100, prev_stall=1)
    assert v == "STALLED" and stall == 2


def test_a_stall_counter_resets_the_moment_it_advances():
    v, stall = _c(progress_scalar=180, prev_scalar=100, prev_stall=5)
    assert v == "RUNNING" and stall == 0


def test_zero_progress_inside_the_grace_window_is_running_not_a_stall():
    """A cold unit stages, pre-equilibrates, solvates + parameterises ~146k atoms and minimises 12 replicas
    before its first commit. Calling that a stall would kill every healthy leg in its first hour."""
    assert _c(progress_scalar=0, prev_scalar=0, instance_age_min=40)[0] == "RUNNING"


def test_zero_progress_past_the_grace_window_is_a_setup_stall():
    assert _c(progress_scalar=0, prev_scalar=0, instance_age_min=200)[0] == "SETUP_STALL"


def test_warmup_to_production_transition_never_reads_as_a_regression():
    """The progress scalar orders production above warmup precisely so the phase change cannot look like
    the counter going backwards, which would otherwise be recorded as a stall at the worst moment."""
    _, it_w, scal_w = (None, 400, 400)
    scal_p = 1_000_000 + 40
    assert scal_p > scal_w
    assert _c(progress_scalar=scal_p, prev_scalar=scal_w)[0] == "RUNNING"


# ---------------------------------------------------------------- relaunch policy
def test_only_died_relaunches():
    for verdict in ("RUNNING", "STALLED", "SETUP_STALL", "DONE"):
        ok, why = wd.should_relaunch(verdict, 0, 8)
        assert not ok and "diagnosis" in why


def test_relaunch_is_capped_per_day():
    assert wd.should_relaunch("DIED", 0, 8)[0] is True
    assert wd.should_relaunch("DIED", 7, 8)[0] is True
    assert wd.should_relaunch("DIED", 8, 8)[0] is False
    assert wd.should_relaunch("DIED", 99, 8)[0] is False


def test_unparseable_counter_refuses_rather_than_relaunching_blind():
    ok, why = wd.should_relaunch("DIED", "??", 8)
    assert not ok and "blind" in why


# ---------------------------------------------------------------- watch-list handling
def test_empty_or_missing_watch_list_is_a_no_op():
    assert wd.enabled_entries(None) == []
    assert wd.enabled_entries({}) == []
    assert wd.enabled_entries({"watch": []}) == []
    assert wd.enabled_entries({"watch": [{"unit_id": "u", "enabled": False}]}) == []


def test_disabled_entries_are_invisible():
    doc = {"watch": [{"unit_id": "a", "enabled": True}, {"unit_id": "b", "enabled": False},
                     {"unit_id": "c"}]}
    assert [w["unit_id"] for w in wd.enabled_entries(doc)] == ["a"]


def test_watch_entry_carries_everything_a_relaunch_needs():
    """The watchdog must INVENT NOTHING: a relaunch re-dispatches exactly what was launched, so every
    parameter that shapes the run has to be in the entry."""
    e = wd.watch_entry("calib_hi_to_lo__ternary_vhl", 0, "fwd", "probe", "4.0", "1.0")
    for k in ("unit_id", "leg_id", "seed", "direction", "mode", "timestep_fs",
              "warmup_timestep_fs", "max_relaunches_per_day", "enabled"):
        assert k in e
    assert e["unit_id"].endswith("_probe") and "dt4.0fs" in e["unit_id"]


REAL_WATCH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "ternary-vast-watch.json")


def _seed(tmp_path):
    """A watch file that carries the SHIPPED `_prefix_keying_params`, so arming is tested against the real
    config guard rather than against an empty one."""
    p = tmp_path / "watch.json"
    real = json.load(open(REAL_WATCH))
    p.write_text(json.dumps({"_prefix_keying_params": real["_prefix_keying_params"], "watch": []}))
    return p


def test_armed_entries_satisfy_the_shipped_config_guard(tmp_path):
    """The guard and the armer must agree. If a launch can write an entry the guard rejects, the watchdog
    refuses to act on the very leg that was just paid for — and the failure appears an hour later, on a cron,
    with a GPU already burning."""
    import watchdog_validate as wdv
    p = _seed(tmp_path)
    for mode in ("probe", "edge"):
        wd.arm(mode, path=str(p))
    assert wdv.validate(json.load(open(p))) == []


def test_git_branch_is_recorded_because_a_schedule_only_fires_from_main(tmp_path):
    """A cron fires from the DEFAULT branch, so github.ref_name inside the watchdog is 'main'. Without the
    launching branch on the entry, relaunching a feature-branch unit would pull main's code onto that unit's
    checkpoint — different code, silently, under the same leg name."""
    p = _seed(tmp_path)
    wd.arm("probe", path=str(p), timestep_fs="4.0", warmup_timestep_fs="1.0")
    e = json.load(open(p))["watch"][0]
    assert e.get("git_branch")


def test_arm_does_not_rewrite_the_config_guards_required_key_list(tmp_path):
    """Arming is an append. A launch job that silently replaced `_prefix_keying_params` with whatever its
    code version believed is exactly how a guard stops guarding."""
    p = _seed(tmp_path)
    before = json.load(open(p))["_prefix_keying_params"]
    wd.arm("edge", path=str(p))
    assert json.load(open(p))["_prefix_keying_params"] == before


def test_arm_is_idempotent_and_reenables(tmp_path):
    p = _seed(tmp_path)
    wd.arm("probe", path=str(p))
    first = json.loads(p.read_text())
    n1 = len(first["watch"])
    wd.arm("probe", path=str(p))
    assert len(json.loads(p.read_text())["watch"]) == n1, "arming twice must not duplicate entries"
    doc = json.loads(p.read_text())
    doc["watch"][0]["enabled"] = False
    p.write_text(json.dumps(doc))
    wd.arm("probe", path=str(p))
    assert json.loads(p.read_text())["watch"][0]["enabled"] is True


def test_arm_edge_registers_all_three_legs(tmp_path):
    p = _seed(tmp_path)
    wd.arm("edge", path=str(p))
    ids = [w["leg_id"] for w in json.loads(p.read_text())["watch"]]
    assert set(ids) == {"calib_hi_to_lo__ternary_vhl", "calib_hi_to_lo__binary_vhl",
                        "calib_hi_to_lo__solvent"}


def test_load_watch_tolerates_a_missing_or_corrupt_file(tmp_path):
    assert wd.load_watch(str(tmp_path / "nope.json")) == {"watch": []}
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert wd.load_watch(str(bad)) == {"watch": []}


# ---------------------------------------------------------------- a crash is not a preemption
def test_a_recorded_failure_is_not_a_preemption_and_must_not_relaunch():
    """The difference that decides whether a NaN costs one rental or eight. A PREEMPTED host is killed
    mid-run and writes no record, so it reads DIED and resuming from the checkpoint is right. A leg that RAN
    and recorded status=failed has a reason, and relaunching reproduces it — uncapped that is one full-length
    rental per attempt, up to the daily cap, every one of them dying identically."""
    v, _ = _c(has_failed_record=True, instance_alive=False)
    assert v == "FAILED"
    ok, why = wd.should_relaunch("FAILED", 0, 8)
    assert not ok and "diagnosis" in why


def test_a_preemption_with_no_record_still_reads_died_and_relaunches():
    v, _ = _c(has_failed_record=False, instance_alive=False)
    assert v == "DIED"
    assert wd.should_relaunch("DIED", 0, 8)[0] is True


def test_a_stale_failed_record_does_not_stop_a_live_attempt():
    """A failure record sits in S3 until the next attempt overwrites it, which does not happen until that
    attempt gets far enough. While an instance is up, the live progress signal governs — otherwise a fixed
    bug's old record would freeze the watchdog on the leg that is currently succeeding."""
    v, _ = _c(has_failed_record=True, instance_alive=True, progress_scalar=200, prev_scalar=100)
    assert v == "RUNNING"
