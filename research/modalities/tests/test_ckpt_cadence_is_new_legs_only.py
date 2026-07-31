"""LOWERING THE COMMIT CADENCE IS A CHANGE FOR **NEW** LEGS ONLY — and it must not touch the running four.

trimcrae, 2026-07-31, in the same message that asked how to get throughput back: lowering
`warmup_ckpt_iters` / `prod_ckpt_iters` would bank progress more often out of short sessions, "BUT
`rbfe_spot_checkpoint.py:133` says the interval is FIXED WHEN THE .nc IS CREATED … So: changing the env is a
no-op for the four legs currently at 30-82% and MUST NOT be allowed to break their resume validation."

THE MECHANISM, which is why this is a real hazard and not a caution. openmmtools writes a full frame to the
.chk only every `checkpoint_interval` iterations and that interval is fixed at .nc CREATION. On 2026-07-21 the
resume path opened the reporter without an explicit interval (inheriting the file's, 40) while driving commit
off the ENV interval (20) — and at an off-grid boundary `validate_reporter_pair` raised
`resume iteration 520 != expected 540`, PERMANENTLY blocking re-dispatch of that leg.

So these tests pin the property that makes a cadence change safe: `effective_interval` prefers the COMMITTED
value and treats the env only as a last-resort fallback, so an in-flight leg keeps resuming on its own grid
whatever the env now says.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rbfe_spot_checkpoint as spot  # noqa: E402
import rbfe_spot_checkpoint as spot  # noqa: E402
import ternary_vast_launch as tv  # noqa: E402


def test_the_manifest_wins_over_the_env_fallback():
    """The running legs' safety in one assertion: a committed generation carries its own interval, and that
    is what a resume uses no matter what the lane is configured with now."""
    assert spot.effective_interval({"checkpoint_interval": 64}, fallback=8) == 64
    assert spot.effective_interval({"checkpoint_interval": 40}, fallback=10) == 40


def test_the_fallback_is_used_ONLY_when_the_committed_value_is_unreadable():
    """Pre-2026-07-21 generations recorded no interval. They are the only case the env may decide."""
    assert spot.effective_interval({}, fallback=40) == 40
    assert spot.effective_interval(None, fallback=40) == 40
    assert spot.effective_interval({"checkpoint_interval": None}, fallback=40) == 40


def test_a_lower_env_cadence_cannot_change_an_in_flight_leg(monkeypatch):
    """The four 5a-KS legs are at warmup/1088-1536 and production/1360 on 64/40 grids. Setting a lower
    cadence must be INERT for them — that is what makes it safe to set at all."""
    monkeypatch.setenv("TVAST_WARMUP_CKPT_ITERS", "16")
    monkeypatch.setenv("TVAST_PROD_CKPT_ITERS", "10")
    for committed, env_now in ((64, 16), (40, 10)):
        assert spot.effective_interval({"checkpoint_interval": committed}, fallback=env_now) == committed


@pytest.mark.parametrize("committed,iteration", [(64, 1088), (64, 1536), (40, 1360)])
def test_the_running_legs_sit_on_their_own_grid(committed, iteration):
    """A sanity check on the real numbers: every committed boundary the four legs are parked at is a multiple
    of ITS OWN interval, which is exactly what `validate_reporter_pair` requires on resume. If a future edit
    made the env win, these would stop dividing and the legs would be unresumable."""
    assert iteration % committed == 0


# ★★ THE INTERVAL WAS HALVED 64 -> 32 ON 2026-07-31, and these are the tests that made it safe to do.
#
# WHY: container start -> `md-running` is 0.3-0.6 min (measured), so the "~28 min cold start" is really TIME
# TO FIRST COMMIT = one checkpoint interval of MD. At 64 a 3090 leg needs ~36 min to bank anything, ~60 % of a
# ~1.00 h median session. At 32 it is ~18 min. STRATEGY Appendix A 62.
#
# The four legs in flight when it changed were at warmup 1088 / 1152 / 1536 and production 1400, i.e. 91 %,
# 58 %, 43 % and 41 % of their work. Moving their grid would have made them unresumable.
RUNNING_WHEN_CHANGED = [("warmup", 1088, 64), ("warmup", 1152, 64), ("warmup", 1536, 64),
                        ("production", 1400, 40)]


@pytest.mark.parametrize("phase,iteration,committed_iv", RUNNING_WHEN_CHANGED)
def test_a_RUNNING_leg_keeps_its_grid_after_the_mode_value_changed(phase, iteration, committed_iv):
    """THE SAFETY PROPERTY, stated over the real in-flight state rather than in the abstract. Whatever the
    mode now asks for, a leg resumes on the interval baked into its own .nc — and its committed boundary must
    still divide by it, which is precisely what `validate_reporter_pair` checks on resume."""
    env_now = int(tv.MODES["5aks"]["warmup_ckpt_iters"])
    eff = spot.effective_interval({"checkpoint_interval": committed_iv}, fallback=env_now)
    assert eff == committed_iv, "the committed grid must win over the mode's new value"
    assert iteration % eff == 0, (
        f"{phase} iteration {iteration} is off a {eff}-grid — this leg would be unresumable")


def test_the_new_value_is_on_grid_for_every_target_this_mode_can_run():
    """`800 / 64 = 12.5` was the class of error found at 2 fs. 32 must divide the target exactly, or a fresh
    leg lands off-grid at its LAST boundary."""
    for dt, wdt in ((4.0, 1.0),):                       # the only timesteps 5aks runs
        target = tv.warmup_target_iters(dt, wdt)
        iv = int(tv.MODES["5aks"]["warmup_ckpt_iters"])
        assert target and target % iv == 0, f"{target} % {iv} != 0 at dt={dt}"


def test_the_per_arm_derivation_was_NOT_switched_on_for_this_mode():
    """Explicitly out of scope while the rate table's card ratios are untrustworthy — this was a change to
    the FLAT mode value and nothing else."""
    assert not tv.MODES["5aks"].get("per_arm_ckpt")


def test_the_mode_defaults_are_the_grids_a_NEW_leg_will_be_created_on():
    """A guard on the OTHER direction: the value must be a deliberate one, not drift. SUPERSEDED, retained:
    this asserted 64 until 2026-07-31."""
    m = tv.MODES["5aks"]
    assert int(m["warmup_ckpt_iters"]) == 32 and int(m["prod_ckpt_iters"]) == 40
