"""Reviewer condition 5 (2026-07-19) — LOCK the ternary-cooperativity sign convention against synthetic K_D.

The reviewer flagged a potential sign trap: alpha = KD_binary/KD_ternary and RT ln(alpha_hi/alpha_lo) = +0.94
(alpha_hi/alpha_lo ~ 4.9), yet a SINGLE compound's dG_coop = -RT ln(alpha) = -0.94 for a cooperative compound.
The reducer must state which quantity it returns AND recover it from first principles. These tests:

  1. build a synthetic pair of compounds from raw K_D values (binary + ternary in each of two compounds),
  2. independently recompute the coop cycle two ways (from the alchemical morph legs vs the closed-form alpha),
  3. assert the reducer's ternary_coop.ddg_coop returns EXACTLY that quantity with the correct POSITIVE sign
     for the frozen hi->lo calibration, matching the frozen +0.944 target,
  4. propagate experimental K_D uncertainties through to a sigma(ddG_coop),
  5. drive ternary_fep_reduce.calibration_decision with synthetic replicate aggregates and confirm PASS for the
     right sign and NO-GO for the flipped sign.

Pure/no-GPU. Reads the REAL frozen JSON so the calibration target cannot drift away from the code."""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_coop as tc            # noqa: E402
import ternary_fep_reduce as red     # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RT = tc.R_KCAL * tc.DEFAULT_T


def _frozen_target():
    j = json.load(open(os.path.join(HERE, "wurz-calib-frozen.json")))
    return j["preregistered_target"]


# --- 1-3: raw K_D -> morph legs -> coop cycle, sign + magnitude ---------------------------------------------
def test_ddg_coop_from_synthetic_kd_matches_alpha_route():
    """Two equivalent recomputes of ddG_coop(A->B) from raw K_D must agree, and equal the reducer's cycle."""
    # A = calib_hi (more cooperative), B = calib_lo (less). Pick K_D so alpha_A=12.8, alpha_B=2.6 (Wurz).
    # Binary affinities need not be equal; the cycle only cares about the RATIOS, so vary them to be honest.
    kd_bin_A, kd_bin_B = 3.0e-7, 8.0e-7          # arbitrary consistent units (M)
    alpha_A, alpha_B = 12.8, 2.6
    kd_tern_A = kd_bin_A / alpha_A
    kd_tern_B = kd_bin_B / alpha_B
    ref = tc.ddg_coop_from_kd_pairs(kd_bin_A, kd_tern_A, kd_bin_B, kd_tern_B)
    # the two internal routes agree to float precision
    assert abs(ref["ddg_coop_by_cycle_kcal"] - ref["ddg_coop_by_alpha_kcal"]) < 1e-9
    # and the reducer's single-source ddg_coop, fed the SAME morph legs, returns the identical number
    via_reducer = tc.ddg_coop(ref["ddg_alch_ternary_kcal"], ref["ddg_alch_binary_kcal"])
    assert abs(via_reducer - ref["ddg_coop_by_cycle_kcal"]) < 1e-12
    # closed form: ddG_coop = -RT ln(alpha_B/alpha_A) = RT ln(alpha_A/alpha_B)
    assert abs(via_reducer - (-RT * math.log(alpha_B / alpha_A))) < 1e-9


def test_hi_to_lo_calibration_is_positive_and_matches_frozen_target():
    """For the frozen hi->lo morph (cooperativity DECREASES A->B) ddG_coop must be POSITIVE and = +0.944."""
    t = _frozen_target()
    alpha_A, alpha_B = t["alpha_1"], t["alpha_4"]          # 12.8 (hi) -> 2.6 (lo)
    # any consistent K_D set with these alphas reproduces the target (binary K_D cancels in the cycle)
    kd_bin = 1.0e-6
    ref = tc.ddg_coop_from_kd_pairs(kd_bin, kd_bin / alpha_A, kd_bin, kd_bin / alpha_B, T=t["temperature_K"])
    ddg = ref["ddg_coop_by_cycle_kcal"]
    assert ddg > 0, "hi->lo cooperativity change must be POSITIVE (reducer PASS check requires it)"
    assert abs(ddg - t["ddG_coop_exp_kcal_per_mol"]) < 1e-3, (ddg, t["ddG_coop_exp_kcal_per_mol"])
    # and it equals the frozen formula's own closed form -RT ln(alpha_4/alpha_1)
    RTt = tc.R_KCAL * t["temperature_K"]
    assert abs(ddg - (-RTt * math.log(alpha_B / alpha_A))) < 1e-9


def test_single_compound_dg_coop_has_opposite_sign_to_relative_change():
    """Guard against the exact confusion the reviewer named: a cooperative compound's OWN dG_coop is NEGATIVE,
    while the hi->lo RELATIVE ddG_coop is POSITIVE. They are different quantities and must not be conflated."""
    assert tc.dg_coop_from_alpha(12.8) < 0        # cmpd1 own coop free energy: favorable/negative
    assert tc.dg_coop_from_alpha(2.6) < 0         # cmpd4 own coop free energy: also favorable/negative
    # relative change hi->lo: positive (B less cooperative than A)
    rel = tc.dg_coop_from_alpha(2.6) - tc.dg_coop_from_alpha(12.8)
    assert rel > 0
    assert abs(rel - (-RT * math.log(2.6 / 12.8))) < 1e-9


def test_antisymmetry_lo_to_hi_flips_sign():
    """B->A must be exactly the negative of A->B (a cycle-algebra sanity the 47.28-leg audit also relies on)."""
    kd_bin = 1.0e-6
    hi2lo = tc.ddg_coop_from_kd_pairs(kd_bin, kd_bin / 12.8, kd_bin, kd_bin / 2.6)["ddg_coop_by_cycle_kcal"]
    lo2hi = tc.ddg_coop_from_kd_pairs(kd_bin, kd_bin / 2.6, kd_bin, kd_bin / 12.8)["ddg_coop_by_cycle_kcal"]
    assert abs(hi2lo + lo2hi) < 1e-12


# --- 4: experimental K_D uncertainty -> sigma(ddG_coop) -----------------------------------------------------
def test_kd_uncertainty_propagates_to_ddg_sigma():
    """Carry through experimental K_D uncertainties (reviewer condition 5). ddG_coop = -RT ln(alpha_B/alpha_A)
    with alpha = KD_bin/KD_tern, so d(ddG) = RT * sqrt( sum (sigma_KD/KD)^2 ) over the 4 independent K_D's."""
    kd = {"bin_A": 3.0e-7, "tern_A": 3.0e-7 / 12.8, "bin_B": 8.0e-7, "tern_B": 8.0e-7 / 2.6}
    rel_sigma = 0.20        # 20% relative error on each measured K_D
    # analytic propagation
    sigma_ddg = RT * math.sqrt(4 * rel_sigma ** 2)
    # numeric check via central differences on ln-ratios
    def ddg(kb_A, kt_A, kb_B, kt_B):
        return tc.ddg_coop_from_kd_pairs(kb_A, kt_A, kb_B, kt_B)["ddg_coop_by_cycle_kcal"]
    grads = []
    for key in kd:
        h = kd[key] * 1e-4
        up = dict(kd); up[key] += h
        dn = dict(kd); dn[key] -= h
        d = (ddg(up["bin_A"], up["tern_A"], up["bin_B"], up["tern_B"])
             - ddg(dn["bin_A"], dn["tern_A"], dn["bin_B"], dn["tern_B"])) / (2 * h)
        grads.append((d * kd[key] * rel_sigma) ** 2)   # (dddg/dKD * sigma_KD)^2
    sigma_numeric = math.sqrt(sum(grads))
    assert abs(sigma_numeric - sigma_ddg) < 1e-6
    assert sigma_ddg > 0


# --- 5: the reducer's PASS/NO-GO honors the sign --------------------------------------------------------------
def _agg(mean, sd, n, env, hyst=0.0):
    return {"leg_id": "synthetic__%s" % env, "environment": env, "mean_dg_morph_kcal": mean,
            "replicate_sd_kcal": sd, "n_replicas": n, "ci95_half_width_kcal": sd,
            "hysteresis_kcal": hyst, "dg_values": [mean] * n}


def test_calibration_decision_passes_correct_sign():
    """ternary−binary = +0.944 with tight, target-covering CI -> PASS."""
    target = _frozen_target()["ddG_coop_exp_kcal_per_mol"]
    tern = _agg(mean=0.944, sd=0.15, n=3, env="ternary")
    bina = _agg(mean=0.000, sd=0.15, n=3, env="binary")
    d = red.calibration_decision(tern, bina, target)
    assert d["decision"] == "PASS", d
    assert d["checks"]["correct_positive_sign"] is True
    assert d["checks"]["ci_excludes_zero"] is True
    assert d["checks"]["consistent_with_target"] is True
    assert abs(d["welch_satterthwaite"]["ddg_coop_kcal"] - 0.944) < 1e-9


def test_calibration_decision_nogo_on_flipped_sign():
    """A method that resolves ternary−binary = −0.944 (wrong sign) must be NO-GO, never PASS."""
    target = _frozen_target()["ddG_coop_exp_kcal_per_mol"]
    tern = _agg(mean=0.000, sd=0.15, n=3, env="ternary")
    bina = _agg(mean=0.944, sd=0.15, n=3, env="binary")     # binary MORE favorable -> ddg = -0.944
    d = red.calibration_decision(tern, bina, target)
    assert d["decision"] == "NO-GO", d
    assert d["checks"]["correct_positive_sign"] is False
    assert "NEGATIVE" in d["reason"]


def test_calibration_decision_indeterminate_when_ci_includes_zero():
    """Right sign point estimate but noisy (CI spans zero) -> INDETERMINATE, not PASS (frozen rule)."""
    target = _frozen_target()["ddG_coop_exp_kcal_per_mol"]
    tern = _agg(mean=0.944, sd=1.2, n=3, env="ternary")
    bina = _agg(mean=0.000, sd=1.2, n=3, env="binary")
    d = red.calibration_decision(tern, bina, target)
    assert d["decision"] == "INDETERMINATE", d
    assert d["checks"]["ci_excludes_zero"] is False


def test_frozen_target_formula_is_minus_RT_ln_alpha4_over_alpha1():
    """The frozen JSON's own numbers must reproduce its stated +0.944 via -RT ln(alpha_4/alpha_1)."""
    t = _frozen_target()
    RTt = tc.R_KCAL * t["temperature_K"]
    recompute = -RTt * math.log(t["alpha_4"] / t["alpha_1"])
    assert abs(recompute - t["ddG_coop_exp_kcal_per_mol"]) < 1e-3
    assert recompute > 0
