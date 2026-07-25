"""Unit tests for the valB closure-triangle arithmetic, leg accounting and pricing.

These are the checks that make the module's claims falsifiable rather than rhetorical. Pure stdlib -- they run
in the dev sandbox with no chemistry stack, and they are the reason the cost figures can be trusted without a
GPU.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import valb_triangle_closure as vtc   # noqa: E402


# ---------------------------------------------------------------------------------------------------------
# 1. the closure identity really is an identity
# ---------------------------------------------------------------------------------------------------------
def test_triangle_closes_on_arbitrary_states():
    rng = random.Random(11)
    for _ in range(500):
        st = {s: rng.uniform(-20, 20) for s in ("cmpd1", "cmpd4", "cmpd4prime")}
        r = vtc.closure_identity(st)
        assert r["closes"], r
        assert abs(r["residual_R"]) < 1e-9


def test_T1_enters_with_the_as_run_orientation():
    """r0 measured cmpd1 -> cmpd4 forward. If the triangle used the reverse orientation, r0 could not be reused
    without a sign flip -- which is exactly the kind of error a closure is supposed to catch, so it must not be
    introduced by the design itself."""
    r = vtc.closure_identity()
    assert r["orientation"]["T1"].startswith("cmpd1 -> cmpd4")
    assert "coefficient +1" in r["orientation"]["T1"]


def test_decomposition_R_coop_is_R_ternary_minus_R_binary():
    rng = random.Random(3)
    tern = {n: rng.uniform(-50, 50) for n in ("T1", "T2", "T3")}
    bina = {n: rng.uniform(-50, 50) for n in ("T1", "T2", "T3")}
    d = vtc.closure_decomposition({"ternary": tern, "binary": bina})
    assert abs(d["R_coop"] - (d["R_ternary"] - d["R_binary"])) < 1e-9


def test_R_coop_can_be_zero_while_both_sub_closures_are_large():
    """The reason the module insists both are reported: a clean R_coop is not evidence of a consistent cycle."""
    tern = {"T1": 3.0, "T2": 0.0, "T3": 0.0}
    bina = {"T1": 3.0, "T2": 0.0, "T3": 0.0}
    d = vtc.closure_decomposition({"ternary": tern, "binary": bina})
    assert abs(d["R_coop"]) < 1e-12
    assert abs(d["R_ternary"]) > 0.5 and abs(d["R_binary"]) > 0.5
    assert d["cancellation_risk"] is True


# ---------------------------------------------------------------------------------------------------------
# 2. the blindness result -- the load-bearing claim
# ---------------------------------------------------------------------------------------------------------
def test_state_function_errors_are_invisible_to_closure():
    b = vtc.state_function_blindness(trials=500)
    assert b["state_function_errors_are_invisible"]
    assert b["max_abs_R_with_state_function_error_only"] < 1e-10
    # and a path error is NOT invisible, or the test would pass vacuously
    assert b["max_abs_R_with_added_path_error"] > 0.1


def test_blindness_holds_for_an_arbitrary_state_function():
    """Independent re-derivation, not a re-run of the module's own loop: any per-endpoint bias telescopes."""
    rng = random.Random(99)
    for _ in range(2000):
        eps = {s: rng.gauss(0, 100.0) for s in ("cmpd1", "cmpd4", "cmpd4prime")}
        e = {n: eps[b] - eps[a] for n, a, b, _ in vtc.TRIANGLE}
        assert abs(sum(s * e[n] for n, _, _, s in vtc.TRIANGLE)) < 1e-9


# ---------------------------------------------------------------------------------------------------------
# 3. the noise floor
# ---------------------------------------------------------------------------------------------------------
def test_SD_R_is_sqrt6_sigma_leg_and_MC_agrees():
    nf = vtc.closure_noise_floor(sigma_leg_values=(0.3,), trials=20000)
    row = nf["rows"][0]
    assert abs(row["SD_R_analytic"] - math.sqrt(6) * 0.3) < 1e-4   # reported rounded to 4 dp
    assert abs(row["SD_R_monte_carlo"] - row["SD_R_analytic"]) / row["SD_R_analytic"] < 0.05


def test_power_to_detect_r0_sized_error_collapses_at_realistic_noise():
    """The decision-relevant number: at the repo's own assumed replicate SD the n=1 triangle cannot reliably
    see a systematic the size of r0's own 1.478 kcal/mol miss."""
    nf = vtc.closure_noise_floor(sigma_leg_values=(0.045, 0.7), trials=20000)
    tight, loose = nf["rows"][0], nf["rows"][1]
    assert tight["power_at_n1"]["detect_1.478"] > 0.95
    assert loose["power_at_n1"]["detect_1.478"] < 0.35


# ---------------------------------------------------------------------------------------------------------
# 4. leg accounting + pricing
# ---------------------------------------------------------------------------------------------------------
def test_cancellation_identity_does_not_apply_to_the_triangle():
    la = vtc.leg_accounting()
    assert la["applies_to_the_triangle"] is False
    assert la["cross_check_no_leg_is_shared"]["shared_legs"] == 0


def test_leg_is_2800_iterations_and_3_5e6_steps():
    """The correction that reprices everything: warmup iterations derive from the WARMUP integrator at 1 fs."""
    s = vtc.steps_per_leg()
    assert s["warmup_iterations"] == 800.0
    assert s["production_iterations"] == 2000.0
    assert s["total_iterations"] == 2800.0
    assert s["total_steps"] == 3.5e6


def test_4fs_saving_is_1_56x_not_2x():
    p = vtc.price_at_4fs()
    assert abs(p["ratio"] - 2.25 / 3.5) < 1e-4                     # reported rounded to 4 dp
    assert abs(1 / p["ratio"] - 1.5556) < 1e-3          # 1.56x, not 2x


def test_iteration_basis_correction_is_16_7_percent():
    p = vtc.price_triangle()
    assert abs(p["basis"]["iteration_basis_correction"] - 2800.0 / 2400.0) < 1e-3
    assert abs(p["corrections"]["a_iteration_basis_pct"] - 16.7) < 0.2


def test_n1_scout_price_is_above_the_designs_5_9():
    """The design's ~$5.9 was computed on the 2400 basis; the corrected figure must be ~16.7% higher."""
    p = vtc.price_triangle()
    usd = p["variants"]["n1_scout_R_only (2 new edges x ternary+binary; r0 reused as T1)"]["plan_usd"]
    assert 6.5 < usd < 7.2, usd
    assert abs(usd / 5.85 - 2800.0 / 2400.0) < 0.03


def test_n3_honest_is_16_legs_not_12():
    """T1 has only r0, so an n=3 triangle must buy r1/r2 of the already-run edge as well."""
    p = vtc.price_triangle()
    v = p["variants"]
    twelve = v["n3_as_the_design_prices_it (2 new edges x 3 replicas -- INCOMPLETE, see (c))"]["ref_gpu_h"]
    sixteen = v["n3_HONEST (all three edges at n=3 => 12 new legs + T1's r1,r2 = 16 legs)"]["ref_gpu_h"]
    assert abs(sixteen / twelve - 16.0 / 12.0) < 1e-3


def test_solvent_prescout_is_a_small_fraction_of_the_full_scout():
    sp = vtc.solvent_prescout()
    assert 0.05 < sp["fraction_of_full_n1_scout"] < 0.30
    assert sp["new_legs"] == 2


# ---------------------------------------------------------------------------------------------------------
# 5. the decision tree must actually be derived from the blindness result, not asserted
# ---------------------------------------------------------------------------------------------------------
def test_decision_tree_branch_A_is_keyed_to_blindness():
    dt = vtc.decision_tree()
    assert dt["branch_A"]["can_closure_see_that_class"] is False
    assert dt["branch_B"]["can_closure_see_that_class"] is True
    assert "NOT SUPPORTED" in dt["verdict"]


def test_report_builds_and_is_json_serialisable():
    import json
    r = vtc.build_report()
    json.dumps(r)
    for k in ("closure_identity", "what_closure_can_and_cannot_diagnose", "noise_floor",
              "leg_accounting", "price", "decision_tree", "solvent_prescout_RECOMMENDED_FIRST"):
        assert k in r
