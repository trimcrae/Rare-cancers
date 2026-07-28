"""The per-arm checkpoint cadence — and the guard against it being tidied back into one shared value.

★★ WHAT THIS PINS, AND WHY IT IS NOT A STYLE TEST (measured 2026-07-27). Across three cohorts the RUNG 2b
ternary replicates committed ABSOLUTELY NOTHING while their matched binary legs advanced normally — six
ternary legs out of six. Four candidate causes were refuted by measurement (an OOM: the setup peaks at
2.31 GiB against hosts with 63-128 GB; a missing or mis-keyed stage cache: all three seed keys exist and
unpack; a defective seed-1/2 staged input: seed 1's exact tree builds its hybrid system to completion; our own
idle guard: its lines are 15 min of silence and 3 starts against an observed ~4 min and 2). What remained was
exposure, not a defect:

    first durable checkpoint = warmup_ckpt_iters x s_per_iter
                 binary:  64 x  6.0 s =  384 s
                 ternary: 64 x 17.0 s = 1088 s

Same host-reclaim churn, ~3x the unprotected runway: the binary arm ratchets, the ternary arm never banks
anything. A single shared iteration count CANNOT express "the same exposure" for two systems that sample at
6.0 and 17.0 s/iter, so the natural-looking cleanup — give both arms one number again — reinstates the bug.
That is what these tests exist to stop.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_vast_launch as tv  # noqa: E402

TERNARY = "calib_hi_to_lo__ternary_vhl"
BINARY = "calib_hi_to_lo__binary_vhl"


def test_the_arms_of_edge_reps_do_not_share_a_checkpoint_interval():
    """The state the lane was in for three cohorts: both arms on 64."""
    t = tv.warmup_ckpt_iters_for(TERNARY, "edge_reps")
    b = tv.warmup_ckpt_iters_for(BINARY, "edge_reps")
    assert t != b, ("the ternary and binary arms are back on one interval — that is the configuration under "
                    "which six consecutive ternary replicates produced no science at all")
    assert int(t) < int(b), "the SLOWER arm needs the FINER interval, not the coarser one"


def test_the_ternary_arms_exposure_is_inside_the_binary_arms_proven_exposure():
    """The invariant the derivation exists to satisfy, stated in the units that matter: SECONDS of sampling
    at risk from a host reclaim, not iterations. The binary arm's figure is the proven one — it is the arm
    that actually banks progress on these hosts."""
    t = tv.ckpt_exposure_s(TERNARY, "edge_reps")
    b = tv.ckpt_exposure_s(BINARY, "edge_reps")
    assert t <= b, f"ternary exposure {t:.0f}s exceeds the binary arm's proven {b:.0f}s"
    # ...and not absurdly under it either, or we are paying commit overhead for nothing. The derivation takes
    # the LARGEST interval that fits, so the result must be within one interval-step of the budget.
    assert t > b / 4, f"ternary exposure {t:.0f}s is far under the {b:.0f}s budget — over-committing"


def test_every_derived_interval_divides_the_warmup_target_exactly():
    """⚠ A PROTOCOL GUARD, NOT AN ARITHMETIC ONE. `rbfe_spot_driver` rounds each phase's target DOWN to a
    multiple of the interval, so an interval that does not divide 1600 would SHORTEN this leg's
    equilibration relative to r0's — a protocol difference inside a matched cycle, which is precisely the
    class of error the closure triangle's 2 fs pinning exists to prevent."""
    for leg in (TERNARY, BINARY):
        ci = int(tv.warmup_ckpt_iters_for(leg, "edge_reps"))
        assert tv.WARMUP_TARGET_ITERS % ci == 0, f"{leg}: interval {ci} does not divide 1600"
        assert (tv.WARMUP_TARGET_ITERS // ci) * ci == tv.WARMUP_TARGET_ITERS


def test_the_warmup_target_is_the_one_the_driver_actually_derives():
    """1600 is not observed folklore, it is arithmetic, and it is pinned because the divisibility guard above
    is worthless if the target drifts. `rbfe_spot_driver._iters_from_time` takes the equilibration length at
    the WARMUP timestep but the PRODUCTION integrator's steps-per-iteration:

        1.0 ns / 1.0 fs warmup dt                     = 1e6 steps
        2.5 ps time_per_iteration / 4.0 fs prod dt    = 625 steps per iteration
        1e6 / 625                                     = 1600

    and the live board confirms it: `[spot-driver] warmup_target=1600 (ci=64)`."""
    equilibration_ns, warmup_dt_fs, time_per_iter_ps, prod_dt_fs = 1.0, 1.0, 2.5, 4.0
    steps = equilibration_ns * 1e6 / warmup_dt_fs
    steps_per_iter = time_per_iter_ps * 1000.0 / prod_dt_fs
    assert int(steps / steps_per_iter) == tv.WARMUP_TARGET_ITERS


def test_only_a_mode_that_opts_in_gets_a_per_arm_interval():
    """Scoped, so this cannot silently re-cadence a lane nobody measured. `edge` (seed 0, the legs that are
    already DONE) and `5aks` must be byte-identical to what they ran with."""
    for mode in ("edge", "5aks", "probe", "smoke"):
        for (leg, _s, _d) in tv.units_for(mode):
            assert tv.warmup_ckpt_iters_for(leg, mode) == str(tv.MODES[mode]["warmup_ckpt_iters"]), \
                f"{mode}/{leg} must keep the mode's own interval — it did not opt in"


def test_the_jobspec_actually_carries_the_per_arm_value():
    """The derivation is worthless if `build_jobspec` still reads the mode's flat value."""
    got = {}
    for (leg, seed, direction) in tv.units_for("edge_reps"):
        j = tv.build_jobspec(leg, seed, direction, mode="edge_reps")
        got.setdefault(tv.arm_of_leg(leg), set()).add(j.env["WARMUP_CKPT_ITERS"])
    assert got["ternary"] == {"20"} and got["binary"] == {"64"}, got


def test_an_explicit_env_override_still_wins():
    """The escape hatch has to keep working — it is how a one-off re-cadence is done without editing MODES."""
    os.environ["TVAST_WARMUP_CKPT_ITERS"] = "8"
    try:
        j = tv.build_jobspec(TERNARY, 1, "fwd", mode="edge_reps")
        assert j.env["WARMUP_CKPT_ITERS"] == "8"
    finally:
        del os.environ["TVAST_WARMUP_CKPT_ITERS"]


def test_the_measured_rates_carry_every_arm_the_lane_runs():
    """A missing arm falls back to the reference interval silently, which is the failure this whole file is
    about — so it must be impossible to add a leg type without noticing."""
    arms = {tv.arm_of_leg(leg) for mode in tv.MODES for (leg, _s, _d) in tv.units_for(mode)}
    missing = arms - set(tv.ARM_MEASURED_S_PER_ITER)
    assert not missing, f"no measured s/iter for {missing} — it would silently inherit the reference cadence"


@pytest.mark.parametrize("rate,expect_finer", [(17.0, True), (6.0, False), (60.0, True)])
def test_the_interval_re_derives_when_a_rate_is_re_measured(monkeypatch, rate, expect_finer):
    """The point of deriving rather than typing: re-measure the ternary arm and the cadence follows, with
    nobody having to remember to re-tune a constant."""
    monkeypatch.setitem(tv.ARM_MEASURED_S_PER_ITER, "ternary", rate)
    ci = int(tv.warmup_ckpt_iters_for(TERNARY, "edge_reps"))
    ref = int(tv.MODES["edge_reps"]["warmup_ckpt_iters"])
    assert (ci < ref) is expect_finer
    assert ci * rate <= ref * tv.ARM_MEASURED_S_PER_ITER[tv.CKPT_REFERENCE_ARM]
