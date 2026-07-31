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


def test_the_mode_defaults_are_still_the_grids_those_legs_were_created_on():
    """A guard on the OTHER direction: if someone lowers `MODES['5aks']` in place rather than for new legs,
    a fresh attempt on an EXISTING commit prefix would create a second grid inside one prefix."""
    m = tv.MODES["5aks"]
    assert int(m["warmup_ckpt_iters"]) == 64 and int(m["prod_ckpt_iters"]) == 40, (
        "these are the grids the in-flight 5a-KS legs' .nc files were created on. Lowering them is a change "
        "for a NEW commit prefix only — see this module's docstring for the 2026-07-21 incident.")
