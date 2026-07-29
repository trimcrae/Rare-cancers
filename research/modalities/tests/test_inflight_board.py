#!/usr/bin/env python3
"""The in-flight board must be derived, must never invent a cell, and must never cry stall without a reason.

Fixtures below are real lines from the 2026-07-29 ternary lane, not invented ones.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import inflight_board as B    # noqa: E402

# Verbatim from run 30642759739's collect output for the triangle legs.
LOG_TRIANGLE = (
    "[spot-driver] trajectory persistence: positions every 20 iteration(s), velocities every 0\n"
    "[spot-driver] warmup_target=768 (ci=64) prod_target=2000 (ci=40)\n"
    "[spot-driver] restore -> warmup@iter 256\n"
    "INFO:\tEstimated completion in 0:14:17.742878, at 2026-Jul-29-15:51:10\n"
    "INFO:\tIteration 274/320\n")

# Verbatim from the 4 fs replicate arm r2.
LOG_EDGE_REPS = (
    "[spot-driver] warmup_target=1600 (ci=40) prod_target=2000 (ci=40)\n"
    "INFO:\tEstimated completion in 0:03:12.647644, at 2026-Jul-29-15:39:32\n"
    "INFO:\tIteration 683/704\n")


def test_targets_are_parsed_from_the_drivers_own_line_not_recomputed():
    assert B.parse_targets(LOG_TRIANGLE) == (768, 2000)
    assert B.parse_targets(LOG_EDGE_REPS) == (1600, 2000)


def test_absent_targets_yield_none_rather_than_a_default():
    """A default here would silently turn an unknown denominator into a confident percentage."""
    assert B.parse_targets("") is None
    assert B.parse_targets("no such line") is None


def test_s_per_iter_is_measured_from_the_hosts_own_estimate():
    r = B.measured_s_per_iter(LOG_EDGE_REPS)
    assert r is not None and 8.0 < r < 10.0, r          # 21 iters in 192.6 s -> ~9.17
    r2 = B.measured_s_per_iter(LOG_TRIANGLE)
    assert r2 is not None and 18.0 < r2 < 19.0, r2      # 46 iters in 857.7 s -> ~18.6


def test_s_per_iter_is_none_rather_than_a_guess_when_the_pair_is_missing():
    assert B.measured_s_per_iter("") is None
    assert B.measured_s_per_iter("INFO:\tIteration 5/10") is None            # no ETA line
    assert B.measured_s_per_iter("Estimated completion in 0:01:00") is None  # no iteration line


def test_s_per_iter_is_none_on_a_finished_segment():
    assert B.measured_s_per_iter("Iteration 704/704\nEstimated completion in 0:00:00") is None


def test_percent_is_of_the_WHOLE_leg_not_of_the_current_phase():
    """warmup 384 of 768 is 14 % of the leg, NOT 50 % — the defect this assertion exists to stop."""
    pct = B.pct_complete("warmup", 384, (768, 2000))
    assert abs(pct - 100.0 * 384 / 2768) < 1e-6
    assert pct < 15.0


def test_percent_counts_finished_warmup_once_production_starts():
    pct = B.pct_complete("production", 1000, (768, 2000))
    assert abs(pct - 100.0 * (768 + 1000) / 2768) < 1e-6


def test_percent_is_none_without_targets_and_zero_before_any_commit():
    assert B.pct_complete("warmup", 384, None) is None
    assert B.pct_complete(None, 0, (768, 2000)) == 0.0


def test_eta_counts_the_whole_remaining_leg():
    secs = B.eta_seconds("warmup", 384, (768, 2000), 18.6)
    assert abs(secs - (2768 - 384) * 18.6) < 1e-6


def test_eta_is_none_when_the_rate_is_unknown():
    assert B.eta_seconds("warmup", 384, (768, 2000), None) is None
    assert B.eta_seconds("warmup", 384, None, 18.6) is None


def test_advancing_is_running_with_no_why_needed():
    assert B.state_of(True, True, 0, False) == (B.RUNNING, "")


def test_cold_start_is_starting_not_stalled():
    """The box vast_idle_guard refuses to condemn must not be called stalled by the board either."""
    st, why = B.state_of(True, False, 5, cold_start=True)
    assert st == B.STARTING and why


def test_one_flat_poll_is_not_yet_a_stall():
    st, _ = B.state_of(True, False, 1, cold_start=False)
    assert st == B.STARTING


def test_two_flat_polls_is_a_stall_when_a_reason_is_supplied():
    st, why = B.state_of(True, False, 2, cold_start=False, why_not_running="GPU idle, log silent 40 min")
    assert st == B.STALLED and "log silent" in why


def test_a_stall_with_no_reason_RAISES_rather_than_rendering():
    """trimcrae: 'it better have a good reason if it's going to be stalled.'"""
    with pytest.raises(ValueError, match="refusing to render STALLED"):
        B.state_of(True, False, 3, cold_start=False)
    with pytest.raises(ValueError):
        B.state_of(True, False, 3, cold_start=False, why_not_running="   ")


def test_no_host_is_its_own_state():
    st, why = B.state_of(False, False, 0, False, why_not_running="capacity refusal on m28164")
    assert st == B.NO_HOST and "28164" in why


def test_short_names_come_from_the_triangle_registry():
    assert B.short_name("calib_hi_to_lo2__ternary_vhl_r0_dt2.0fs_wu1.0_triangle") == "T3 ternary"
    assert B.short_name("calib_lo_to_lo2__binary_vhl_r0_dt2.0fs_wu1.0_triangle") == "T2 binary"
    assert B.short_name("calib_hi_to_lo__ternary_vhl_r2_dt4.0fs_wu1.0_edge_reps") == "valB r2 ternary"


def test_render_shows_an_em_dash_never_a_blank_or_a_fabricated_cell():
    txt = B.render([{"name": "T2 ternary", "pct": None, "eta_s": None,
                     "usd_per_ns": None, "state": B.STARTING, "why": "pulling image"}])
    assert "—" in txt and "T2 ternary" in txt and "pulling image" in txt
    # the ETA column must not be silently empty — that is the "so useless" report
    assert "  \n" not in txt


def test_render_is_stable_across_calls():
    rows = [{"name": "T3 binary", "pct": 2.3, "eta_s": 3600.0,
             "usd_per_ns": "$0.004557/ns · 1.34x", "state": B.RUNNING, "why": ""}]
    assert B.render(rows, now_epoch=1_800_000_000) == B.render(rows, now_epoch=1_800_000_000)


# ── the defect the board's own first live run exposed ────────────────────────────────────────────────
# `calib_lo_to_lo2__ternary_vhl` rendered STALLED at 1:05 PM ET on 2026-07-29 with the reason "no committed
# checkpoint yet; host up 21 min ..." — a stall verdict whose own reason explains why it is not a stall.

def test_a_leg_that_has_never_committed_is_not_stalled_inside_the_setup_grace():
    st, why = B.state_of(True, advanced=False, no_advance_polls=6, cold_start=False,
                         why_not_running="no committed checkpoint yet; host up 21 min",
                         pre_first_commit=True)
    assert st == B.STARTING, "a leg with no first checkpoint has nothing to advance FROM"
    assert why


def test_pre_first_commit_beats_the_poll_counter_however_high_it_gets():
    st, _ = B.state_of(True, advanced=False, no_advance_polls=99, cold_start=False,
                       why_not_running="still staging", pre_first_commit=True)
    assert st == B.STARTING


def test_past_the_setup_grace_a_never_committed_leg_IS_stalled():
    """The caller stops passing pre_first_commit once the grace elapses; then the normal rule applies."""
    st, why = B.state_of(True, advanced=False, no_advance_polls=3, cold_start=False,
                         why_not_running="120 min with no first checkpoint and the log is silent",
                         pre_first_commit=False)
    assert st == B.STALLED and "120 min" in why


def test_advancing_still_wins_over_pre_first_commit():
    assert B.state_of(True, True, 0, False, pre_first_commit=True)[0] == B.RUNNING


def test_next_day_eta_does_not_break_column_alignment():
    rows = [{"name": "T3 ternary", "pct": 16.2, "eta_s": 60 * 60 * 12.5,
             "usd_per_ns": "$0.00456/ns · 1.34x basis", "state": B.RUNNING, "why": ""},
            {"name": "T2 binary", "pct": 16.2, "eta_s": 3600.0,
             "usd_per_ns": "$0.00512/ns · 1.50x basis", "state": B.RUNNING, "why": ""}]
    lines = B.render(rows, now_epoch=1_800_000_000).splitlines()
    body = [ln for ln in lines[2:] if ln.strip()]
    # every row must put STATE in the same column, which a too-narrow ETA cell breaks
    cols = [ln.index("RUNNING") for ln in body]
    assert len(set(cols)) == 1, "ETA column too narrow — a next-day stamp shifted the later cells"


# ── a leg with no host must RENDER, not vanish (2026-07-29, 2:45 PM ET) ──────────────────────────────
# `calib_hi_to_lo2__binary_vhl` lost its host and was absent from two consecutive boards while its three
# siblings rendered normally. NO_HOST was defined but never emitted, because rows were built only from the
# live-instance loop.

def test_no_host_renders_with_its_checkpoint_rather_than_disappearing():
    st, why = B.state_of(False, False, 0, False,
                         why_not_running="no live host — checkpoint at warmup/64 is intact in S3")
    assert st == B.NO_HOST
    txt = B.render([{"name": "T3 binary", "pct": 2.3, "eta_s": None,
                     "usd_per_ns": None, "state": st, "why": why}])
    assert "T3 binary" in txt and "NO HOST" in txt and "warmup/64" in txt


def test_a_no_host_row_still_shows_percent_because_the_checkpoint_survives():
    """The work done is not lost when the host dies, so the % column must not reset to 0 or blank."""
    assert B.pct_complete("warmup", 64, (768, 2000)) > 0.0


# ── an unreadable instance list must not render as a host death (2026-07-29, 4:04 PM ET) ────────────
# All six legs printed NO HOST in one board and read as six simultaneous deaths. The gates had seen all six
# hosts three minutes earlier; the same collect had printed `could not list instances`. `mine = []` on an
# unreadable read is the correct reap-nothing degradation, but it made "we could not see" render exactly like
# "it is not there".

def test_an_unreadable_host_list_is_UNKNOWN_not_NO_HOST():
    st, why = B.state_of(False, False, 0, False, host_list_readable=False,
                         why_not_running="RuntimeError: vast API GET /instances/ -> 403")
    assert st == B.UNKNOWN, "an unreadable list must never be reported as an absent host"
    assert st != B.NO_HOST and "403" in why


def test_unreadable_beats_every_other_branch_including_a_claimed_host():
    """No other verdict is entitled to render: we could not observe the host, its age, or its advance."""
    for kwargs in ({"has_host": True, "advanced": True, "no_advance_polls": 0, "cold_start": False},
                   {"has_host": True, "advanced": False, "no_advance_polls": 9, "cold_start": False},
                   {"has_host": False, "advanced": False, "no_advance_polls": 0, "cold_start": True}):
        st, _ = B.state_of(host_list_readable=False, why_not_running="throttled", **kwargs)
        assert st == B.UNKNOWN


def test_UNKNOWN_with_no_reason_RAISES_like_a_stall_does():
    with pytest.raises(ValueError, match="refusing to render UNKNOWN"):
        B.state_of(False, False, 0, False, host_list_readable=False)
    with pytest.raises(ValueError):
        B.state_of(False, False, 0, False, host_list_readable=False, why_not_running="  ")


def test_readable_is_the_default_so_existing_callers_are_unchanged():
    assert B.state_of(False, False, 0, False, why_not_running="host died")[0] == B.NO_HOST


def test_an_unknown_row_renders_and_says_it_is_not_a_death():
    txt = B.render([{"name": "T2 ternary", "pct": 9.2, "eta_s": None, "usd_per_ns": None,
                     "state": B.UNKNOWN, "why": "instance list did not read this pass — NOT a host death"}])
    assert "UNKNOWN" in txt and "NOT a host death" in txt and "NO HOST" not in txt


def test_the_collect_passes_readability_into_the_no_host_branch():
    """Pin the call site: UNKNOWN existing in the module is not the same as collect distinguishing the two."""
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ternary_vast_launch.py")
    src = open(path).read()
    assert "_inst_unreadable" in src, "collect no longer records WHY the instance list failed to read"
    assert "host_list_readable=(_inst_unreadable is None)" in src, (
        "the no-host rows no longer distinguish an unreadable instance list from genuine host deaths — six "
        "legs would again render as six simultaneous deaths on a throttled read")


def test_the_collect_emits_no_host_rows():
    """Pin the call site: NO_HOST being reachable in the module is not the same as the board using it."""
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ternary_vast_launch.py")
    src = open(path).read()
    assert "_expected - _hosted" in src, (
        "collect no longer computes the set of enabled units that have no live host — a dead leg would "
        "silently vanish from the board again")
    assert "enabled_entries" in src, "the expectation set must come from the watch list, not a local guess"


# ── the ETA that vanished at a checkpoint barrier (2026-07-29, 6:47 PM ET) ───────────────────────────
# trimcrae: "T2 binary should have an ETA". `calib_lo_to_lo2__binary_vhl` rendered `—` while advancing.
# Verbatim from run 30497335853's collect: no `Estimated completion` line, because openmmtools had just
# begun a fresh segment at the 1200 barrier — while the driver's own completed-interval measurement sat
# two lines above it, unused.

LOG_AT_A_BARRIER = (
    "[spot-driver] warmup_target=768 (ci=64) prod_target=2000 (ci=40)\n"
    "[timing] 40 iters in 552s = 13.8s/iter (4.35 iters/min) at iteration 1200/2000\n"
    "[barrier] committed checkpoint at iteration 1200/2000\n"
    "--- raw tail ---\n"
    "[barrier] committed checkpoint at iteration 1200/2000\n"
    "INFO:\t********************************************************************************\n"
    "INFO:\tIteration 1201/1240\n"
    "LAST-ITER INFO:\tIteration 1201/1240\n")


def test_a_rate_survives_a_checkpoint_barrier_with_no_openmmtools_estimate():
    assert B.measured_s_per_iter(LOG_AT_A_BARRIER) == pytest.approx(552.0 / 40.0)


def test_that_leg_now_gets_an_eta_instead_of_a_dash():
    tg = B.parse_targets(LOG_AT_A_BARRIER)
    eta = B.eta_seconds("production", 1200, tg, B.measured_s_per_iter(LOG_AT_A_BARRIER))
    assert eta is not None and eta == pytest.approx((2768 - 1968) * 13.8)


def test_the_driver_line_is_derived_from_the_pair_not_the_rounded_quotient():
    """`= 13.8s/iter` is one decimal place; 552/40 is exact. One home for the arithmetic."""
    r = B.measured_s_per_iter("[timing] 3 iters in 100s = 33.3s/iter")
    assert r == pytest.approx(100.0 / 3.0)


def test_the_most_recent_completed_interval_wins():
    txt = ("[timing] 40 iters in 800s = 20.0s/iter\n"
           "[timing] 40 iters in 400s = 10.0s/iter\n")
    assert B.measured_s_per_iter(txt) == pytest.approx(10.0)


def test_the_openmmtools_pair_is_still_the_fallback_when_no_interval_has_closed():
    """A leg early in warmup has no completed driver interval yet; the estimate must still be used."""
    assert "[timing]" not in LOG_TRIANGLE
    r = B.measured_s_per_iter(LOG_TRIANGLE)
    assert r is not None and 18.0 < r < 19.0


def test_a_degenerate_driver_line_falls_through_rather_than_returning_zero():
    txt = "[timing] 0 iters in 0s = 0.0s/iter\n" + LOG_EDGE_REPS
    r = B.measured_s_per_iter(txt)
    assert r is not None and 8.0 < r < 10.0
