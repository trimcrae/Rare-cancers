"""Unit tests for ternary_coop.py — the pure ternary-cooperativity core + pilot plan.

Exercises the alpha<->dG_coop conversion, the binary-vs-ternary cycle bookkeeping, the separated
recruitment/coupling read-outs, the frozen pilot leg map (+ drift guard), and the MODE=plan forecast /
$200-cap preflight — all without any MD/GPU/network. Reads the REAL frozen JSON so leg-id drift is caught."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_coop as tc  # noqa: E402


# --- cooperativity definitions ------------------------------------------------------------------------------
def test_dg_coop_alpha_roundtrip():
    for a in (0.2, 1.0, 5.0, 93.0):
        dg = tc.dg_coop_from_alpha(a)
        assert abs(tc.alpha_from_dg_coop(dg) - a) < 1e-9


def test_cooperative_alpha_gives_negative_favorable_dg():
    assert tc.dg_coop_from_alpha(10.0) < 0        # alpha>1 cooperative -> favorable (negative)
    assert tc.dg_coop_from_alpha(0.2) > 0         # alpha<1 anti-cooperative -> unfavorable (positive)
    assert abs(tc.dg_coop_from_alpha(1.0)) < 1e-12  # alpha=1 -> 0


def test_dg_coop_rejects_bad_alpha():
    assert tc.dg_coop_from_alpha(0) is None
    assert tc.dg_coop_from_alpha(-1) is None
    assert tc.dg_coop_from_alpha(float("nan")) is None
    assert tc.dg_coop_from_alpha(None) is None


def test_cycle_bookkeeping():
    # ddG_coop = ternary - binary
    assert tc.ddg_coop(-5.0, -2.0) == -3.0
    assert tc.ddg_coop(1.0, 3.0) == -2.0
    assert tc.ddg_coop(float("inf"), 1.0) is None
    assert tc.ddg_coop(None, 1.0) is None


def test_delta_alpha_ratio_direction():
    # a more-cooperative B (negative ddG_coop) -> ratio alpha_B/alpha_A > 1
    assert tc.delta_alpha_ratio(-2.0) > 1.0
    assert tc.delta_alpha_ratio(+2.0) < 1.0
    assert abs(tc.delta_alpha_ratio(0.0) - 1.0) < 1e-12


def test_frozen_temperature_and_RT_match_code():
    import json
    import os
    fr = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                     "nr4a3-ternary-coop-prereg.json")))
    m = fr["method"]
    assert m["temperature_K"] == tc.DEFAULT_T
    assert abs(m["RT_kcal_per_mol"] - tc.R_KCAL * tc.DEFAULT_T) < 1e-6
    assert abs(m["R_kcal_per_mol_K"] - tc.R_KCAL) < 1e-12
    assert m["energy_units"] == "kcal/mol"


def test_recruitment_and_coupling_are_separate():
    out = tc.recruitment_and_coupling(-4.0, -1.5)
    assert out["effective_ternary_recruitment"] == -4.0
    assert out["cooperative_coupling"] == -2.5
    # the two are genuinely distinct quantities
    assert out["effective_ternary_recruitment"] != out["cooperative_coupling"]


# --- frozen pilot leg map -----------------------------------------------------------------------------------
def test_pilot_legs_match_frozen_json():
    legs = tc.load_pilot_legs()
    ids = [l["id"] for l in legs]
    # the 4 morph legs: calib binary+ternary, nrv04 binary + nrv04 ternary-NR4A1
    assert set(ids) == {
        "calib_hi_to_lo__binary_vhl", "calib_hi_to_lo__ternary_vhl",
        "nrv04_active_to_epimer__binary_vhl", "nrv04_active_to_epimer__ternary_nr4a1"}
    envs = {l["id"]: l["environment"] for l in legs}
    assert envs["nrv04_active_to_epimer__binary_vhl"] == "binary"
    assert envs["nrv04_active_to_epimer__ternary_nr4a1"] == "ternary"
    # every leg carries a purpose + E3
    assert all(l["purpose"] and l["e3"] == "VHL" for l in legs)


def test_pilot_leg_drift_fails_closed(tmp_path):
    import json
    fr = tc.load_frozen()
    fr["frozen_manifest"]["ternary_pilot_expected_leg_ids"].append("bogus_extra_leg")
    p = tmp_path / "f.json"
    p.write_text(json.dumps(fr))
    try:
        tc.load_pilot_legs(str(p))
        assert False, "expected drift ValueError"
    except ValueError as e:
        assert "bogus_extra_leg" in str(e)


# --- MODE=plan forecast + $200 cap preflight ----------------------------------------------------------------
def test_plan_forecast_shape_and_math():
    p = tc.plan(n_windows=16, n_replicas=3, unit_gpu_h=3.0, spot_hourly=0.50)
    assert p["n_legs"] == 4
    assert p["total_alchemical_windows"] == 4 * 16 * 3
    assert abs(p["forecast_gpu_h"] - 4 * 16 * 3 * 3.0) < 1e-6
    assert abs(p["forecast_cost_usd"] - p["forecast_gpu_h"] * 0.50) < 1e-6
    assert p["hard_cap_usd"] == 200


def test_plan_cap_preflight_flags_overrun():
    # a costly assumption should trip fits_cap=False and a STOP verdict (never silently shrink replicas)
    p = tc.plan(n_windows=24, n_replicas=3, unit_gpu_h=5.0, spot_hourly=0.50)
    assert p["forecast_cost_usd"] > 200
    assert p["fits_cap"] is False
    assert "STOP" in p["preflight_verdict"]


def test_plan_cap_preflight_ok_when_cheap():
    p = tc.plan(n_windows=8, n_replicas=3, unit_gpu_h=1.0, spot_hourly=0.50)
    assert p["fits_cap"] is True
    assert "STOP" not in p["preflight_verdict"]


def test_plan_reads_cap_from_frozen_json():
    p = tc.plan()
    assert p["hard_cap_usd"] == tc.load_frozen()["budget"]["ternary_pilot"]["hard_cap_usd_spot"]


def test_unit_gpu_h_is_labeled_a_stub():
    p = tc.plan()
    assert "unit_gpu_h_STUB" in p
    assert "STUB" in p["honesty"]
