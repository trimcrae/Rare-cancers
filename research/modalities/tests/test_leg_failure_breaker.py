#!/usr/bin/env python3
"""Buying a fourth host for a unit that died on three is not a retry, it is a habit.

The tension these pin: a failed record must NEVER permanently block its own retry (run_ternary_leg.sh is
explicit — testing for existence meant no fix could ever be validated), yet a unit dying at the same phase on
host after host must stop being bought. The discriminator is the COUNT, not the record.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import leg_failure_breaker as lfb  # noqa: E402

MOD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "leg_failure_breaker.py")
LAUNCH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ternary_vast_launch.py")

FAILED = {"status": "failed", "phase": "warmup", "rc": 1}


# ---------------------------------------------------------------- it trips
def test_it_blocks_at_the_threshold():
    d = lfb.decide(FAILED, lfb.DEFAULT_THRESHOLD)
    assert d["block"] is True and d["verdict"] == lfb.BLOCK


def test_it_blocks_above_the_threshold():
    assert lfb.decide(FAILED, lfb.DEFAULT_THRESHOLD + 5)["block"] is True


# ---------------------------------------------------------------- it must NOT trip
def test_one_failure_is_noise_not_a_fault():
    # A spot preemption or a bad host produces exactly this. Blocking here would stop the lane on a transient.
    assert lfb.decide(FAILED, 1)["block"] is False


def test_two_failures_can_still_be_one_unlucky_machine():
    # Machine 28164 served two of the observed deaths, which is precisely why 2 is not the threshold.
    assert lfb.decide(FAILED, 2)["block"] is False


def test_a_unit_that_has_never_run_is_never_blocked():
    assert lfb.decide(None, 99)["block"] is False


def test_a_done_unit_is_never_blocked():
    assert lfb.decide({"status": "done"}, 99)["block"] is False


def test_an_unrecognised_status_fails_OPEN():
    # This module exists to stop waste. Refusing to rent on a status it does not recognise would let one
    # schema change silently halt the lane, which is far worse than one extra rental.
    assert lfb.decide({"status": "running"}, 99)["block"] is False
    assert lfb.decide({}, 99)["block"] is False


def test_an_unreadable_attempt_listing_fails_OPEN():
    # count_attempts returns None on a listing failure. Opposite of the market gate's fail-CLOSED rule, and
    # deliberately: there, guessing wrong SPENDS blind; here, guessing wrong costs at most one purchase.
    assert lfb.decide(FAILED, None)["block"] is False


# ---------------------------------------------------------------- a block must explain itself
def test_a_block_carries_its_evidence():
    d = lfb.decide(FAILED, 4)
    assert "4 separate rented hosts" in d["why"]
    assert "NOT permanent" in d["why"], "a block that reads as terminal will be worked around, not fixed"
    assert d["n_attempts"] == 4 and d["threshold"] == lfb.DEFAULT_THRESHOLD


def test_a_block_never_renders_like_a_price_hold():
    # CLAUDE.md §1, one glyph one meaning. This is not a market decision and must not read as one.
    line = lfb.render("u1", lfb.decide(FAILED, 3))
    assert "NOT RENTING" in line and "$0 spent" in line
    assert "DRIFT" not in line and "PAYING" not in line


# ---------------------------------------------------------------- purity and reach
def test_the_decision_is_pure():
    src = open(MOD).read()
    head = src.split("def count_attempts", 1)[0]
    for banned in ("time.time(", "datetime.now(", "boto3", "requests"):
        assert banned not in head, banned


def test_it_cannot_touch_a_running_host():
    # It acts at the moment of RENTING only — same boundary as the relaunch market gate. Asserted against
    # CODE, not the whole file: the module docstring necessarily describes the teardown loop it exists to
    # break, so a plain scan trips over its own rationale.
    import ast
    tree = ast.parse(open(MOD).read())
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    names |= {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for banned in ("destroy", "terminate", "stop_instance", "destroy_instance"):
        assert not any(banned in str(n) for n in names), banned


def test_the_threshold_is_not_per_lane_tunable():
    # A per-lane override is how a breaker gets quietly raised until it never trips.
    src = open(MOD).read()
    assert src.count("DEFAULT_THRESHOLD = ") == 1


# ============================================================================================================
# ★ THE CALL SITE. `needed` is what the gate prices and the launcher buys.
# ============================================================================================================
def _launch_src():
    return open(LAUNCH).read()


def test_outstanding_units_consults_the_breaker():
    src = _launch_src()
    assert "leg_failure_breaker" in src, "the launcher no longer imports the breaker"
    assert "lfb.decide(" in src, "the launcher no longer CALLS the breaker"


def test_blocked_units_are_removed_from_needed():
    src = _launch_src()
    i = src.index('return {"needed":')
    assert "not in _blocked" in src[i:i + 200], "a blocked unit would still be priced and rented"


def test_blocked_units_are_returned_not_dropped():
    # CLAUDE.md §6: never silently drop units. A hold the readout cannot see is the failure mode.
    src = _launch_src()
    i = src.index('return {"needed":')
    assert '"blocked": _blocked' in src[i:i + 300]


def test_the_on_host_retry_rule_is_untouched():
    # run_ternary_leg.sh must keep re-running a failed leg. If this ever flips to blocking on existence, no
    # fix could be validated — the exact regression the breaker exists to avoid needing.
    # The rule lives in the onstart script the launcher embeds, not in run_ternary_leg.sh.
    assert "re-running rather than exiting" in _launch_src()
