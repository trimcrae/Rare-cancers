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


def test_verify_armed_fails_when_the_list_does_not_cover_the_launch(tmp_path):
    """The guard for the failure that actually happened: the launch armed the probe and committed it, a
    later edit to the same file rewrote 'watch' to [] and pushed, and the watchdog's only input then said
    there was nothing to watch while a billed GPU leg ran. An empty list is a LEGITIMATE state (nothing
    running), so the config guard must stay a no-op on it — only something that knows which units were just
    launched can tell 'nothing to watch' from 'the thing I am watching went missing'."""
    import pytest
    p = _seed(tmp_path)
    with pytest.raises(SystemExit):
        wd.verify_armed("edge", path=str(p))
    wd.arm("edge", path=str(p))
    assert len(wd.verify_armed("edge", path=str(p))) == 3


def test_verify_armed_fails_when_an_entry_is_merely_disabled(tmp_path):
    p = _seed(tmp_path)
    wd.arm("probe", path=str(p))
    doc = json.load(open(p)); doc["watch"][0]["enabled"] = False
    open(p, "w").write(json.dumps(doc))
    import pytest
    with pytest.raises(SystemExit):
        wd.verify_armed("probe", path=str(p))


# ============================================================ SETUP_STALL MUST EXPLAIN ITSELF
# LANE 21, 2026-07-27. The 9:17 PM ET pass emitted, for a leg 146 min old with scalar=0:
#   "Setup is hung, not slow: check the CUDA probe, the charge cache, minimise steps and GPU utilisation."
# Every suggested cause was wrong. The container was running a full 0.5 ns pre-equilibration on CUDA (~26 min
# per cycle) and aborting at the END of it. Pre-equilibration commits no FEP iterations BY CONSTRUCTION — the
# commit store is only written by the sampler, which starts at `md-running` — so `scalar=0` was the correct
# reading of a leg doing real work, and the hint list pointed away from the only real explanation. Same shape
# as the vast_watchdog defect fixed the same night: a verdict computed from a counter that cannot answer the
# question being asked. There, unit-scoped vs instance-scoped; here, FEP-iteration-scoped vs phase-scoped.
def _diag(**kw):
    base = dict(phase_text="preequil 2026-07-27T00:30:00Z", marker_age_min=120.0, log_age_min=1.0,
                log_lines=["[tvast] pre-equil cache MISS -> running ternary_preequil.py (0.5 ns)"],
                container_started=True, instance_age_min=146.0)
    base.update(kw)
    return wd.setup_stall_diagnosis(**base)


def test_the_9_17pm_preequil_alert_no_longer_blames_setup():
    """THE REGRESSION TEST FOR THE HOUR THIS COST. A non-committing phase must be NAMED as such."""
    head, hints = _diag()
    assert "COMMITS NO FEP ITERATIONS BY CONSTRUCTION" in head
    assert "preequil" in head
    assert "`scalar=0` is the CORRECT reading" in hints
    # and it must actively steer AWAY from the three wrong causes, not merely omit them
    assert "Ignore the CUDA probe and the charge cache" in hints
    assert "Setup is hung" not in head and "Setup is hung" not in hints
    # the phase's real progress signal is named
    assert "phase marker written" in hints and "run.log last written" in hints


def test_every_non_committing_phase_gets_the_same_protection():
    for ph in wd.NON_COMMITTING_PHASES:
        head, _h = _diag(phase_text=f"{ph} 2026-07-27T00:30:00Z")
        assert "COMMITS NO FEP ITERATIONS BY CONSTRUCTION" in head, ph


def test_a_committing_phase_that_commits_nothing_keeps_the_original_hints():
    """The ONLY case the historical text ever fitted. It must survive intact — the fix is about telling the
    truth, not about deleting the hints where they are true."""
    head, hints = _diag(phase_text="md-running 2026-07-27T00:30:00Z")
    assert "WHICH DOES COMMIT, AND HAS COMMITTED NOTHING" in head
    for expected in ("CUDA probe", "charge cache", "minimise step", "warmup NaN"):
        assert expected in hints, expected


def test_a_container_that_never_started_is_named_before_anything_else():
    """A 2 h 57 min image pull looks identical to a hung leg from outside; it is the first thing ruled out."""
    head, hints = _diag(container_started=False)
    assert "NEVER RUN" in head
    assert "previous host" in hints and "actual_status" in hints
    assert "Do NOT diagnose the CUDA probe" in hints


def test_a_stale_log_is_distinguished_from_a_merely_long_phase():
    """The two present identically through a zero counter and are fixed differently: a fresh log means the
    phase is long, a stale one means the container or its uploader stopped."""
    _h, fresh = _diag(log_age_min=1.0)
    assert "fresh, so the container is alive" in fresh
    _h, stale = _diag(log_age_min=45.0)
    assert "STALE" in stale and "CONTAINER or its uploader stopped" in stale
    _h, unknown = _diag(log_age_min=None)
    assert "run.log last written unknown" in unknown


def test_an_unclassified_phase_refuses_to_guess_a_cause():
    head, hints = _diag(phase_text="tica 2026-07-27T00:30:00Z")
    assert "UNRECOGNISED PHASE" in head
    assert "will NOT guess" in hints


def test_the_phase_map_matches_the_marks_the_launcher_actually_emits():
    """The map is only trustworthy if it tracks `ternary_vast_launch`. Adding a `mark` without classifying it
    here must FAIL CI rather than silently produce a confident wrong hint for the new phase."""
    import re
    import ternary_vast_launch as tv
    src = open(tv.__file__).read()
    emitted = set(re.findall(r"^mark ([a-z0-9-]+)$", src, flags=re.M))
    assert emitted, "could not find any `mark <phase>` in ternary_vast_launch — the parser has rotted"
    classified = set(wd.NON_COMMITTING_PHASES) | set(wd.COMMITTING_PHASES) | set(wd.TERMINAL_PHASES)
    assert emitted <= classified, f"phases emitted but not classified: {sorted(emitted - classified)}"


def test_the_committing_phase_is_the_one_that_starts_the_sampler():
    """`md-running` is marked immediately before run_ternary_leg.sh, which is the only thing that writes the
    commit store. If that ever stops being true the whole diagnosis inverts, so it is pinned."""
    import ternary_vast_launch as tv
    src = open(tv.__file__).read()
    i_mark = src.index("mark md-running")
    assert "run_ternary_leg.sh" in src[i_mark:i_mark + 2000]
    assert "RBFE_SPOT_COMMIT_S3" in src[i_mark:i_mark + 2000], \
        "the commit store is passed to the sampler here; if it moved, NON_COMMITTING_PHASES is wrong"
    assert wd.COMMITTING_PHASES == ("md-running",)


def test_phase_head_survives_every_marker_shape():
    assert wd.phase_head("preequil 2026-07-27T00:30:00Z") == "preequil"
    assert wd.phase_head("preequil") == "preequil"
    assert wd.phase_head("") == "" and wd.phase_head(None) == ""


def test_setup_stall_still_never_relaunches():
    """The refusal was right both times it fired. This change is about the explanation, not the action."""
    assert wd.should_relaunch("SETUP_STALL", 0, 8)[0] is False
    assert wd.should_relaunch("STALLED", 0, 8)[0] is False
    assert wd.should_relaunch("DIED", 0, 8)[0] is True


def test_the_ternary_lane_now_shares_the_container_start_check_rather_than_copying_it():
    """Both lanes write their marker with the same `mark()` helper, so 'did this box ever run' is one
    question with one answer. Two copies is the thing this repo keeps paying for."""
    import vast_watchdog as vw
    import watchdog_policy as wp
    assert wd.container_started_from_phase is wp.container_started_from_phase
    assert vw.container_started_from_phase is wp.container_started_from_phase


def test_a_committing_phase_younger_than_the_grace_is_flagged_as_possibly_premature():
    """THE SAME MISMATCH ONE LEVEL DEEPER, caught live on the first pass after the fix shipped: `classify`
    compares the RENTAL's age against the grace, but "has it committed yet" is a question about the PHASE.
    Instance 45947762 was 176 min old with a 20-min-old `md-running` marker — past grace on the box, five
    checkpoint-intervals short on the phase. The alert must not assert a hang it cannot support."""
    _h, hints = _diag(phase_text="md-running 2026-07-27T01:27:33Z", marker_age_min=20.0,
                      instance_age_min=176.0)
    assert "ONLY BEEN IN A COMMITTING PHASE FOR 20 MIN" in hints
    assert "measured on the RENTAL, not on the phase" in hints
    assert "there is nothing wrong" in hints
    # ...and a leg that HAS been committing-phase-resident past the grace gets no such excuse
    _h, old = _diag(phase_text="md-running 2026-07-27T01:27:33Z", marker_age_min=200.0,
                    instance_age_min=210.0)
    assert "ONLY BEEN IN A COMMITTING PHASE" not in old
    assert "CUDA probe" in old


def test_the_premature_caveat_never_fires_without_a_readable_marker_age():
    _h, hints = _diag(phase_text="md-running 2026-07-27T01:27:33Z", marker_age_min=None,
                      instance_age_min=176.0)
    assert "ONLY BEEN IN A COMMITTING PHASE" not in hints
