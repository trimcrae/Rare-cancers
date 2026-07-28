#!/usr/bin/env python3
"""P(a stopped Vast box ever resumes), and the constant derived from it.

`MAX_STOPPED_MIN` was 45 with no derivation in the code — the duration of one 2026-07-25 incident, n=1
promoted to a policy, and since `teardown_decision` it governs how long a capacity-refused box is HELD when
no replacement clears the buy line. These tests pin the derivation, and above all pin the REFUSAL: a sample
too small, or a hold longer than anything ever observed, must return None and leave the constant alone
rather than invent one.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vast_stopped_resume_measure as srm  # noqa: E402

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _rows(inst, states, start=0.0, step=600.0, machine="1"):
    return [{"instance": inst, "machine_id": machine, "utc": f"t{i}", "t": start + i * step,
             "cur_state": s, "status": s, "status_msg": "", "age_min": i * 10, "source": "x"}
            for i, s in enumerate(states)]


# ============================================================================================================
# Episode construction — the two populations that must never be pooled.
# ============================================================================================================
def test_a_box_that_never_ran_and_then_ran_is_a_never_started_resume():
    eps = srm.episodes(_rows("a", ["stopped", "stopped", "running"]))
    assert len(eps) == 1
    e = eps[0]
    assert e["preceded_by_running"] is False and e["resumed"] is True
    assert e["min_to_resume"] == 20.0 and e["censored"] is False


def test_a_box_that_ran_then_stopped_then_ran_is_the_paused_population():
    eps = srm.episodes(_rows("a", ["running", "stopped", "running"]))
    assert len(eps) == 1 and eps[0]["preceded_by_running"] is True and eps[0]["resumed"] is True


def test_an_episode_that_ends_with_the_box_disappearing_is_CENSORED_not_a_failure():
    """Our own reaper removes most stopped boxes. Counting a teardown as "did not resume" is the circularity
    that would make the constant justify itself."""
    eps = srm.episodes(_rows("a", ["stopped", "stopped"]))
    assert eps[0]["censored"] is True and eps[0]["resumed"] is False


def test_exited_and_stopped_are_the_same_state():
    """Vast reports `exited` in one field and `stopped` in another for the same box."""
    eps = srm.episodes(_rows("a", ["running", "exited", "running"]))
    assert len(eps) == 1 and eps[0]["resumed"] is True


def test_two_separate_stops_are_two_episodes():
    eps = srm.episodes(_rows("a", ["running", "stopped", "running", "stopped", "running"]))
    assert len(eps) == 2 and all(e["resumed"] for e in eps)


# ============================================================================================================
# Kaplan-Meier — the only estimator that can speak about the region past the reaper.
# ============================================================================================================
def test_km_ignores_a_censored_episode_rather_than_counting_it_as_a_failure():
    eps = [{"resumed": True, "min_to_resume": 10.0, "censored": False, "observed_min": 10.0},
           {"resumed": False, "min_to_resume": None, "censored": True, "observed_min": 5.0}]
    curve = srm.kaplan_meier(eps)
    # The censored box left the at-risk set at 5 min, so the resume at 10 min is 1 of 1 still at risk.
    assert srm.p_resume_by(curve, 10) == 1.0


def test_km_is_zero_before_the_first_observed_resume():
    curve = srm.kaplan_meier([{"resumed": True, "min_to_resume": 30.0, "censored": False,
                               "observed_min": 30.0}])
    assert srm.p_resume_by(curve, 29) == 0.0 and srm.p_resume_by(curve, 30) == 1.0


def test_the_meaningless_denominator_is_not_reported():
    """"resumed / episodes we watched to a conclusion" is identically 1.0 here by construction — an episode
    that neither resumed nor was censored does not exist. Quoting it would be a fabricated all-clear."""
    s = srm.summarise(srm.episodes(_rows("a", ["stopped", "running"])))
    assert "p_resume_over_decided_episodes" not in s["all"]
    assert s["all"]["p_resume_lower_bound"] is not None


# ============================================================================================================
# The derivation, and its refusals.
# ============================================================================================================
def _doc(times, gap=8.0):
    return {"census_gap_min": gap,
            "episodes": [{"preceded_by_running": False, "resumed": True, "min_to_resume": t,
                          "censored": False, "observed_min": t} for t in times]}


def test_the_constant_is_the_longest_OBSERVED_resume_plus_one_tick():
    assert srm.recommended_hold_min(_doc([10.0, 20.0, 40.0, 50.0, 93.0], gap=8.0)) == 105


def test_the_constant_is_NOT_set_from_too_small_a_sample():
    """n=1 promoted to a policy is the defect being repaired; the repair must not repeat it."""
    assert srm.recommended_hold_min(_doc([45.0])) is None
    assert srm.recommended_hold_min({"episodes": []}) is None


def test_the_constant_is_never_extrapolated_past_the_data():
    """Beyond the largest observed resume the sample is empty and the storage bill is unbounded. Same
    refusal as "no TTL without a measurement", pointed the other way."""
    rec = srm.recommended_hold_min(_doc([10.0, 12.0, 14.0, 16.0, 18.0], gap=8.0))
    assert rec == 30 and rec < 45, "a short-resume sample must SHORTEN the hold, not leave 45 standing"


def test_the_paused_population_does_not_set_the_constant():
    """It is the outbid case, which bid-strategy.md F3 already rules on separately."""
    doc = _doc([10.0] * 5)
    for e in doc["episodes"]:
        e["preceded_by_running"] = True
    assert srm.recommended_hold_min(doc) is None


def test_hold_minutes_falls_back_rather_than_raising(monkeypatch):
    """A launcher must never fail to import because a measurement file moved."""
    monkeypatch.setattr(srm, "_ARTIFACT", "/nonexistent/no-such-file.json")
    assert srm.hold_minutes(default=45) == 45.0


# ============================================================================================================
# The committed artifact, and the launchers that point at it.
# ============================================================================================================
def test_the_committed_measurement_exists_and_carries_its_censoring_warning():
    doc = json.load(open(os.path.join(MOD, "vast-stopped-resume.json")))
    assert doc["summary"]["never_started"]["n_episodes"] > 20
    assert "LOWER BOUND" in doc["_censoring_warning"]
    assert doc["recommended_hold_min"]


def test_the_measurement_says_a_stopped_box_DOES_sometimes_come_back():
    """The input nobody had measured. If this ever reads 0 the hold has no justification at all and the
    economics of `teardown_decision` collapse — so it is asserted, not assumed."""
    doc = json.load(open(os.path.join(MOD, "vast-stopped-resume.json")))
    assert doc["summary"]["never_started"]["n_resumed"] >= 5


def test_the_derived_hold_is_longer_than_the_incident_it_replaced():
    """Three resumes were observed at 87.4, 89.0 and 93.0 min — past the point the old 45 destroyed them."""
    doc = json.load(open(os.path.join(MOD, "vast-stopped-resume.json")))
    assert doc["recommended_hold_min"] > 45
    assert max(e["min_to_resume"] for e in doc["episodes"]
               if e["resumed"] and not e["preceded_by_running"]) > 45


def test_extending_the_hold_is_worth_its_storage_at_every_live_lane_disk():
    doc = json.load(open(os.path.join(MOD, "vast-stopped-resume.json")))
    for gb, e in doc["economics"].items():
        assert e["worth_it"], f"{gb}: {e}"


def test_the_launchers_do_not_carry_their_own_copy_of_the_number():
    """Rule 1: one fact, one place. A hand-typed 45 in a launcher is the second home that drifts."""
    for f in ("ternary_vast_launch.py", "protfep_vast_launch.py"):
        src = open(os.path.join(MOD, f)).read()
        assert "_srm.hold_minutes(" in src, f
        # `45` survives only as the fallback argument to hold_minutes(), never as the value itself.
        assert 'MAX_STOPPED_MIN = float(os.environ.get("TVAST_MAX_STOPPED_MIN") or "45")' not in src
        assert 'MAX_STOPPED_MIN = float(os.environ.get("PROTFEP_MAX_STOPPED_MIN") or "45")' not in src
