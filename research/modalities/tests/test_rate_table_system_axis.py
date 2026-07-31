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
@pytest.mark.parametrize("mode,leg", [
    ("triangle", "calib_hi_to_lo2__ternary_vhl"),
    ("triangle_smoke", "calib_hi_to_lo2__ternary_vhl"),
    ("edge_reps", "calib_hi_to_lo__ternary_vhl"),
    ("edge_reps", "calib_hi_to_lo__binary_vhl"),
    ("5aks", "5aks_d0_to_d__ternary_nr4a3"),
])
def test_no_live_cadence_changed(mode, leg):
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
                ("5aks", "5aks_d0_to_d__ternary_nr4a3"): "32"}[(mode, leg)]
    assert tv.warmup_ckpt_iters_for(leg, mode) == expected


def test_the_committed_artifact_still_answers_the_query_its_consumer_makes():
    """`arm_iteration_rates` reads `rates`, not `rates_by_system`. If a regeneration ever moved the live rate
    under `rates_by_system` alone, every consumer would silently fall back to the flat interval."""
    assert tv.arm_iteration_rates(4.0), "the 4 fs table must still be readable by the live consumer"
    assert tv.arm_iteration_rates(2.0)
