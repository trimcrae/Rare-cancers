"""SYSTEM SIZE IS THE THIRD AXIS A RATE MAY NEVER BE POOLED ACROSS.

`_never_pool` already covered timestep (a 2 fs iteration is 1250 MD steps, a 4 fs one 625) and phase
(pricing.md's superseded ~2.06x card ratio was a warmup/production mix-up). It did not cover SYSTEM SIZE, and
a rate pooled across two assemblies describes neither — a cadence derived from it is a cadence for a system
nobody ran.

⚠ WHAT THE DATA ACTUALLY SAYS, stated because it is less alarming than the concern that prompted the work and
that cuts the same way honesty does. Every recorded ternary leg is 141,458-147,788 particles — a 4.3 % spread,
one system to within any sane tolerance — so the guard does NOT fire on today's table and no current number
changes. The `285,133`-particle figure that motivated the alarm is unsourced (see the appendix note); the only
MEASURED count for the 5a-KS assembly is 147,788, from a leg record of the same `leg_id`.

So this is a guard for the day a genuinely different system lands, plus an honest label on the pooled figure.
It is not a correction to a live rate.
"""
import json
import os
import statistics
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_arm_rates as tar  # noqa: E402
import ternary_vast_launch as tv  # noqa: E402


def _row(unit, arm, dt, gpu, n_particles, prod):
    return {"unit_id": unit, "leg_id": unit.split("_r")[0], "arm": arm, "mode": "x", "status": "done",
            "timestep_fs": dt, "warmup_timestep_fs": 1.0, "gpu": gpu, "n_particles": n_particles,
            "warmup_median_s_per_iter": None, "warmup_n": None,
            "production_median_s_per_iter": prod, "production_n": 20, "recorded_utc": "x"}


# =============================================================================================================
# the clustering
# =============================================================================================================
def test_the_same_complex_resolvated_stays_ONE_system():
    """141,458 / 144,447 / 147,788 are the same staged assembly re-solvated — 4.3 % apart. A fixed-width bin
    would have split them, which is why the tolerance is relative."""
    got = tar.system_buckets([141458, 144447, 147788])
    assert len(got) == 1, got


def test_a_genuinely_different_system_gets_ITS_OWN_bucket():
    got = tar.system_buckets([141458, 147788, 285133])
    assert len(got) == 2, got
    assert any(abs(statistics.median(m) - 285133) < 1 for _lb, m in got)


def test_a_leg_with_no_recorded_size_is_never_guessed_into_a_bucket():
    """Guessing is how the pooled rate arose. `unrecorded` is a visible state, not a default."""
    assert tar.bucket_label_for(None, tar.system_buckets([141458])) is None
    assert tar.bucket_label_for(0, tar.system_buckets([141458])) is None


# =============================================================================================================
# the flag, on real data and on the case it exists for
# =============================================================================================================
def test_todays_table_is_NOT_flagged_because_it_is_genuinely_one_system():
    rows = [_row("a_r0", "ternary", 4.0, "RTX 4090", 141740, 17.0),
            _row("b_r0", "ternary", 4.0, "RTX 5090", 147788, 12.8)]
    agg = tar.aggregate(rows)["4.0"]["ternary"]
    assert agg["pooled_across_systems"] is False
    assert agg["_system_warning"] is None, "a guard that cries wolf on one system teaches people to ignore it"


def test_the_flag_FIRES_when_two_systems_are_pooled():
    rows = [_row("a_r0", "ternary", 4.0, "RTX 4090", 141740, 17.0),
            _row("b_r0", "ternary", 4.0, "RTX 4090", 285133, 34.0)]
    agg = tar.aggregate(rows)["4.0"]["ternary"]
    assert agg["pooled_across_systems"] is True
    assert "POOLED ACROSS 2 SYSTEM SIZES" in agg["_system_warning"]
    assert agg["n_particles_spread"] == [141740, 285133]


def test_rates_by_system_splits_what_the_pooled_median_hides():
    rows = [_row("a_r0", "ternary", 4.0, "RTX 4090", 141740, 17.0),
            _row("b_r0", "ternary", 4.0, "RTX 4090", 285133, 34.0)]
    got = tar.rates_by_system(rows)["4.0"]["ternary"]
    assert len(got) == 2
    assert {v["s_per_iter"] for v in got.values()} == {17.0, 34.0}, \
        "the split table must give each assembly its OWN rate, not the median of the two"


def test_the_never_pool_note_names_all_three_axes():
    doc = tar.build(rows=[_row("a_r0", "ternary", 4.0, "RTX 4090", 141740, 17.0)], n_records=1)
    np_ = doc["_never_pool"]
    assert "timestep" in np_ and "phase" in np_ and "SYSTEM SIZE" in np_


# =============================================================================================================
# ⚠ NOTHING THE TRIANGLE OR THE REPLICATES DEPEND ON MAY MOVE
# =============================================================================================================
#: ★★ THE RATES THIS TEST PINS AGAINST ARE FROZEN HERE, AND THAT IS THE WHOLE POINT (2026-08-01).
#:
#: This test used to call `warmup_ckpt_iters_for` against the LIVE `ternary-arm-iteration-rates.json` — an
#: artifact a CI job (`ternary replicate forensic`) rewrites every few minutes as more legs report. Measured
#: history of the ternary arm's pooled median at 4 fs, from that file's own git log:
#:
#:     07-31 01:06  14.65      08-01 12:13  16.8       08-01 18:34  17.45   <- this test went red here
#:     08-01 02:27  16.6       08-01 18:17  17.0
#:
#: The derivation is `budget = 64 x 10.9 = 697.6 s`, largest divisor of 1600 that fits. At 17.0 s/iter
#: `40 x 17.0 = 680.0` fits and the answer is 40; at 17.45, `40 x 17.45 = 698.0` misses by **0.4 seconds**
#: and it drops to 32. So a test whose name is `no_live_cadence_changed` was going red because a measurement
#: moved by 0.45 s/iter — not because any code changed, and not because any leg's resume was at risk.
#:
#: ⚠ THAT IS A FLAPPING TEST, WHICH IS WORSE THAN A MISSING ONE. It will cross that boundary in both
#: directions as the median wanders, and a suite that is red for a reason nobody acted on is a suite whose
#: red stops meaning anything — the same "alarm trained into noise" failure as a healthy lane reporting
#: itself STALE. And it obscured the property actually worth pinning: that the DERIVATION is unchanged.
#: So the rates are frozen at the values these expectations were computed from, and the live table gets its
#: own test below — an INVARIANT (divides the target, fits the budget), which cannot flap because it does
#: not care what the measurement is.
FROZEN_RATES = {"rates": {"4.0": {"binary": {"s_per_iter": 10.9}, "solvent": {"s_per_iter": 1.7},
                                 "ternary": {"s_per_iter": 17.0}}}}


@pytest.fixture()
def frozen_rates(monkeypatch, tmp_path):
    p = tmp_path / "arm-rates.json"
    p.write_text(json.dumps(FROZEN_RATES))
    monkeypatch.setattr(tv, "_ARM_RATES_PATH", str(p))
    monkeypatch.setattr(tv, "_ARM_RATES_CACHE", {})
    return p


@pytest.mark.parametrize("mode,leg", [
    ("triangle", "calib_hi_to_lo2__ternary_vhl"),
    ("triangle_smoke", "calib_hi_to_lo2__ternary_vhl"),
    ("edge_reps", "calib_hi_to_lo__ternary_vhl"),
    ("edge_reps", "calib_hi_to_lo__binary_vhl"),
    ("5aks", "5aks_d0_to_d__ternary_nr4a3"),
])
def test_no_live_cadence_changed(mode, leg, frozen_rates):
    """The whole risk of touching this table. `aggregate` gained FIELDS only — the `s_per_iter` every consumer
    reads is byte-identical, and `rates_by_system` is a new key nothing consumes yet. These assert the
    resolved cadence, which is the thing that would break a running leg's resume."""
    expected = {("triangle", "calib_hi_to_lo2__ternary_vhl"): "64",
                ("triangle_smoke", "calib_hi_to_lo2__ternary_vhl"): "8",   # the smoke has its own short interval
                ("edge_reps", "calib_hi_to_lo__ternary_vhl"): "40",
                ("edge_reps", "calib_hi_to_lo__binary_vhl"): "64",
                # ⚠ 32 SINCE 2026-07-31, and this test correctly went red when it changed — which is what it
                # is for. The change was NOT the rate-table work this module covers: it is the deliberate
                # halving of the warmup interval (trimcrae-approved) on the finding that the "~28 min cold
                # start" is really one checkpoint interval of MD, container start -> md-running being
                # 0.3-0.6 min. Safety lives in `test_ckpt_cadence_is_new_legs_only.py`.
                # SUPERSEDED, retained: "64".
                ("5aks", "5aks_d0_to_d__ternary_nr4a3"): "64"}[(mode, leg)]
    assert tv.warmup_ckpt_iters_for(leg, mode) == expected


@pytest.mark.parametrize("mode,leg", [
    ("edge_reps", "calib_hi_to_lo__ternary_vhl"),
    ("5aks", "5aks_d0_to_d__ternary_nr4a3"),
])
def test_the_live_cadence_obeys_the_derivation_whatever_the_measurement_says(mode, leg):
    """The live table, checked as an INVARIANT rather than a pin — so it can never flap.

    Two properties, and between them they are the whole safety argument for a derived cadence:
      * it DIVIDES the warmup target exactly, or a resumed leg's committed grid does not line up;
      * it fits inside the reference arm's exposure budget, so this can only ever REFINE a cadence.
    Neither depends on what the median currently is, which is exactly why they belong on the live file.
    """
    s = tv.MODES[mode]
    got = int(tv.warmup_ckpt_iters_for(leg, mode))
    ref = int(s.get("warmup_ckpt_iters") or 64)
    assert got <= ref, "the derivation may only refine a cadence, never coarsen it past the mode's own value"
    dt, wdt = tv.resolve_timesteps(mode, None, None)
    target = tv.warmup_target_iters(dt, wdt)
    if not (target and s.get("per_arm_ckpt")):
        return
    assert target % got == 0, f"{got} does not divide the warmup target {target}: a resume would misalign"
    rates = tv.arm_iteration_rates(dt)
    arm, refarm = tv.arm_of_leg(leg), tv.CKPT_REFERENCE_ARM
    if rates.get(arm) and rates.get(refarm) and arm != refarm:
        assert got * rates[arm] <= ref * rates[refarm] + 1e-9, \
            "the interval must fit inside the reference arm's exposure budget"


def test_the_committed_artifact_still_answers_the_query_its_consumer_makes():
    """`arm_iteration_rates` reads `rates`, not `rates_by_system`. If a regeneration ever moved the live rate
    under `rates_by_system` alone, every consumer would silently fall back to the flat interval."""
    assert tv.arm_iteration_rates(4.0), "the 4 fs table must still be readable by the live consumer"
    assert tv.arm_iteration_rates(2.0)
