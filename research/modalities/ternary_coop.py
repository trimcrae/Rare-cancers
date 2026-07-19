#!/usr/bin/env python3
"""Physics ternary-COOPERATIVITY pure core + pilot plan (Track B; prereg nr4a3-ternary-coop-prereg.md §1/§5b).

The PURE core (no OpenMM/OpenFE/IO) of the thermodynamic-cycle cooperativity method the reviewer approved
(option ii implementing iii): the alpha<->dG_coop conversion, the binary-vs-ternary cycle bookkeeping, the
SEPARATE effective-recruitment vs cooperative-coupling read-outs (never collapsed — prereg §1a), the frozen
PILOT leg map, and the MODE=plan GPU-hour/cost forecast with the $200-cap preflight (prereg budget.ternary_pilot).

Role split (mirrors rbfe_edges.py -> nr4a3_rbfe_sagemaker.py): THIS module is the pure, unit-tested core; the
heavy MD engine (a relative-alchemical ternary FEP, to be built) + the spot-Training submitter consume it and
reuse the per-window-checkpoint plumbing of nr4a3_fep_sagemaker.py / nr4a3_rbfe_sagemaker.py.

HONESTY. No measured alpha, dG, GPU-hour, or convergence is asserted here. The cooperativity helpers are
definitions; the plan's per-window GPU-hour is an explicitly-labeled PLANNING STUB to calibrate on the first
leg (like nr4a3_rbfe_sagemaker._cost_note). The frozen pilot bundle (legs, replicas, lambda schedule) is read
from the prereg JSON so this module and the gate cannot drift.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN_JSON = os.path.join(HERE, "nr4a3-ternary-coop-prereg.json")

# Gas constant in kcal/(mol*K); default T. (Match the ABFE engine's RT convention.)
R_KCAL = 0.0019872041
DEFAULT_T = 298.15


# =============================================================================================================
# cooperativity definitions (prereg §1)
# =============================================================================================================
def dg_coop_from_alpha(alpha, T=DEFAULT_T):
    """dG_coop = -RT ln(alpha), kcal/mol. alpha>1 (cooperative) -> negative (favorable) dG_coop."""
    if alpha is None or alpha <= 0 or not math.isfinite(alpha):
        return None
    return -R_KCAL * T * math.log(alpha)


def alpha_from_dg_coop(dg_coop, T=DEFAULT_T):
    """Inverse: alpha = exp(-dG_coop / RT)."""
    if dg_coop is None or not math.isfinite(dg_coop):
        return None
    return math.exp(-dg_coop / (R_KCAL * T))


def ddg_coop(ddg_alch_ternary, ddg_alch_binary):
    """The binary-vs-ternary thermodynamic cycle (prereg §1): for an A->B analogue morph,
        ddG_coop(A->B) = ddG_alch,ternary(A->B) - ddG_alch,binary(A->B).
    A NEGATIVE ddG_coop means B is MORE cooperative than A (ternary favours the morph beyond the binary).

    SIGN CONVENTION — EXACTLY WHICH QUANTITY THIS RETURNS (reviewer condition 5, 2026-07-19; unit-tested in
    tests/test_ternary_coop_sign.py against synthetic K_D pairs). With the alchemical morph oriented A->B and
    each ddg_alch measured as a RELATIVE binding free energy of B minus A in that environment
    (ddg_alch,env(A->B) = ΔG_bind,env(B) - ΔG_bind,env(A) = RT ln(KD_env(B)/KD_env(A))):

        ddG_coop(A->B) = ddG_alch,ternary - ddG_alch,binary
                       = [ΔG_bind,tern(B) - ΔG_bind,bin(B)] - [ΔG_bind,tern(A) - ΔG_bind,bin(A)]
                       = dG_coop(B) - dG_coop(A)          where dG_coop(x) = -RT ln(alpha_x)
                       = RT ln(alpha_A / alpha_B)
                       = -RT ln(alpha_B / alpha_A)        with alpha = KD_binary / KD_ternary.

    So this is the SAME quantity the frozen calibration target is defined as (wurz-calib-frozen.json:
    ddG_coop_exp = -RT ln(alpha_4/alpha_1), morph cmpd1(hi,alpha=12.8)->cmpd4(lo,alpha=2.6) => +0.944). It is
    the PER-MORPH RELATIVE coop change (a DIFFERENCE of two compounds' cooperativities), NOT a single
    compound's dG_coop=-RT ln(alpha): for the hi->lo calibration (cooperativity DECREASES A->B) it is POSITIVE
    (+0.944), even though each compound's own dG_coop is negative. The reducer's PASS check requires this
    POSITIVE sign to match the +0.944 target."""
    for x in (ddg_alch_ternary, ddg_alch_binary):
        if x is None or not math.isfinite(x):
            return None
    return ddg_alch_ternary - ddg_alch_binary


def ddg_coop_from_kd_pairs(kd_binary_A, kd_ternary_A, kd_binary_B, kd_ternary_B, T=DEFAULT_T):
    """REFERENCE recompute of ddG_coop(A->B) straight from the four dissociation constants (reviewer condition
    5's "independently recompute the final cycle with a second small script"). Builds the alchemical morph
    quantities the FEP reducer forms, from first principles, and returns the same ddG_coop the cycle above
    yields — used to prove the reducer's sign convention against synthetic K_D data. Units of KD are arbitrary
    but must be CONSISTENT (they cancel inside every ratio). alpha_x = KD_binary(x)/KD_ternary(x).

        ddg_alch,binary(A->B)  = RT ln(KD_binary(B)  / KD_binary(A))
        ddg_alch,ternary(A->B) = RT ln(KD_ternary(B) / KD_ternary(A))
        ddG_coop               = ddg_alch,ternary - ddg_alch,binary = -RT ln(alpha_B/alpha_A)

    Returns a dict with the two morph legs, ddG_coop by the cycle, and ddG_coop by the closed-form alpha route,
    which MUST agree to floating precision (the invariant the sign test asserts)."""
    for x in (kd_binary_A, kd_ternary_A, kd_binary_B, kd_ternary_B):
        if x is None or not math.isfinite(x) or x <= 0:
            return None
    RT = R_KCAL * T
    ddg_alch_binary = RT * math.log(kd_binary_B / kd_binary_A)
    ddg_alch_ternary = RT * math.log(kd_ternary_B / kd_ternary_A)
    ddg_by_cycle = ddg_coop(ddg_alch_ternary, ddg_alch_binary)
    alpha_A = kd_binary_A / kd_ternary_A
    alpha_B = kd_binary_B / kd_ternary_B
    ddg_by_alpha = -RT * math.log(alpha_B / alpha_A)
    return {"ddg_alch_binary_kcal": ddg_alch_binary, "ddg_alch_ternary_kcal": ddg_alch_ternary,
            "ddg_coop_by_cycle_kcal": ddg_by_cycle, "ddg_coop_by_alpha_kcal": ddg_by_alpha,
            "alpha_A": alpha_A, "alpha_B": alpha_B, "T_kelvin": T}


def delta_alpha_ratio(ddg_coop_value, T=DEFAULT_T):
    """Convert a ddG_coop(A->B) into the cooperativity-factor RATIO alpha_B/alpha_A = exp(-ddG_coop/RT).
    >1 means B is more cooperative than A. (Lets a calibration leg be compared to a KNOWN measured Delta-alpha
    without asserting either compound's absolute alpha.)"""
    if ddg_coop_value is None or not math.isfinite(ddg_coop_value):
        return None
    return math.exp(-ddg_coop_value / (R_KCAL * T))


def recruitment_and_coupling(ddg_alch_ternary, ddg_alch_binary):
    """Return the TWO reported quantities SEPARATELY (prereg §1a — never collapsed into one score):
      effective_ternary_recruitment  = ddG_alch,ternary  (relative ternary affinity of the morph)
      cooperative_coupling           = ddG_alch,ternary - ddG_alch,binary  (the cycle)
    A compound can have favorable coupling but poor underlying (binary) affinity, or vice-versa; the caller
    must rank on both, not on coupling alone."""
    return {"effective_ternary_recruitment": ddg_alch_ternary,
            "cooperative_coupling": ddg_coop(ddg_alch_ternary, ddg_alch_binary)}


# =============================================================================================================
# frozen PILOT leg map (physical meaning of each frozen leg id; drift = fail closed)
# =============================================================================================================
# Each morph leg = ONE relative-alchemical transformation in ONE environment. Keyed by the SAME ids the prereg
# JSON freezes (frozen_manifest.ternary_pilot_expected_leg_ids); load_pilot_legs() asserts they agree.
PILOT_LEG_MAP = {
    "calib_hi_to_lo__binary_vhl": {
        "morph": "calib_hi -> calib_lo", "environment": "binary", "e3": "VHL", "target": None,
        "purpose": "binary arm of the high-vs-low cooperativity VHL calibration (SMARCA2 pair); with the "
                   "ternary arm gives the recovered Delta-alpha to compare to the measured value"},
    "calib_hi_to_lo__ternary_vhl": {
        "morph": "calib_hi -> calib_lo", "environment": "ternary", "e3": "VHL", "target": "SMARCA2",
        "purpose": "ternary arm of the calibration; ddG_coop = ternary - binary must recover the KNOWN "
                   "measured Delta-alpha(hi-lo) within the calibration tolerance"},
    "nrv04_active_to_epimer__binary_vhl": {
        "morph": "NRV04_active -> NRV04_epimer", "environment": "binary", "e3": "VHL", "target": None,
        "purpose": "the affinity-knockout control in BINARY VHL — the active recruiter must beat its inactive "
                   "Hyp-epimer (prereg §3c: >=3.0 kcal/mol, CI excludes 0). The co-fold could NOT do this."},
    "nrv04_active_to_epimer__ternary_nr4a1": {
        "morph": "NRV04_active -> NRV04_epimer", "environment": "ternary", "e3": "VHL", "target": "NR4A1",
        "purpose": "the effective-ternary-recruitment control on NR4A1 — active must beat epimer by "
                   ">=2.0 kcal/mol (prereg §3c). Pairs with the binary leg to give NR-V04's ddG_coop on NR4A1."},
}


def load_frozen(path=FROZEN_JSON):
    with open(path) as f:
        return json.load(f)


def load_pilot_legs(path=FROZEN_JSON):
    """The frozen pilot morph legs, each enriched with its physical meaning. Fails closed (ValueError) if the
    frozen JSON's leg ids and PILOT_LEG_MAP disagree — so a drift in either is caught, never silently run."""
    frozen = load_frozen(path)
    ids = frozen["frozen_manifest"]["ternary_pilot_expected_leg_ids"]
    missing_in_map = [i for i in ids if i not in PILOT_LEG_MAP]
    extra_in_map = [i for i in PILOT_LEG_MAP if i not in ids]
    if missing_in_map or extra_in_map:
        raise ValueError("pilot leg drift: frozen-not-in-map=%r map-not-in-frozen=%r"
                         % (missing_in_map, extra_in_map))
    return [dict(id=i, **PILOT_LEG_MAP[i]) for i in ids]


# =============================================================================================================
# MODE=plan — GPU-hour / cost forecast + the $200-cap preflight (prereg budget.ternary_pilot)
# =============================================================================================================
def plan(n_windows=16, n_replicas=3, unit_gpu_h=3.0, spot_hourly=0.50, cap_usd=None, path=FROZEN_JSON):
    """A self-describing dry-run forecast for the FIXED ternary pilot bundle (NO GPU, no spend). Cost model
    mirrors nr4a3_rbfe_sagemaker._cost_note but for ternary legs:
        gpu_h = n_legs * n_windows * n_replicas * unit_gpu_h
    UNIT_GPU_H is a PLANNING STUB — ternary systems (E3 + EloBC + target + PROTAC) are larger than a binary
    RBFE morph, so per-window GPU-h is higher than RBFE's ~2 h; the number MUST be calibrated on the first
    real leg before it is trusted (like the RBFE cost note). Implements the reviewer preflight: if the bundle
    cannot fit under the $200 cap WITHOUT compromising replica count, `fits_cap` is False and the caller must
    STOP and return a revised costed scope (never silently drop replicas)."""
    legs = load_pilot_legs(path)
    n_legs = len(legs)
    if cap_usd is None:
        cap_usd = load_frozen(path)["budget"]["ternary_pilot"]["hard_cap_usd_spot"]
    total_windows = n_legs * n_windows * n_replicas
    gpu_h = total_windows * unit_gpu_h
    cost = gpu_h * spot_hourly
    # legs run as concurrent spot jobs (each leg = its windows serial on one A10G, like the RBFE complex leg),
    # so wall-clock ~ one leg's windows*replicas serialized on a GPU (replicas can also parallelize as separate
    # spot jobs → wall ~ n_windows*unit_gpu_h if fully fanned out).
    wall_h_serial_leg = n_windows * n_replicas * unit_gpu_h
    fits_cap = cost <= cap_usd
    return {
        "bundle": "ternary pilot (frozen)",
        "legs": [leg["id"] for leg in legs],
        "n_legs": n_legs,
        "n_windows_per_leg": n_windows,
        "n_replicas": n_replicas,
        "total_alchemical_windows": total_windows,
        "unit_gpu_h_STUB": unit_gpu_h,
        "forecast_gpu_h": round(gpu_h, 1),
        "spot_hourly_usd": spot_hourly,
        "forecast_cost_usd": round(cost, 2),
        "hard_cap_usd": cap_usd,
        "fits_cap": bool(fits_cap),
        "wall_h_if_leg_serial": round(wall_h_serial_leg, 1),
        "preflight_verdict": ("OK to prepare a production submit (still no-spend until dispatched)" if fits_cap
                              else "STOP — forecast exceeds the $%g cap; return a REVISED costed scope (do NOT "
                                   "drop replicas or convergence to fit)" % cap_usd),
        "honesty": "unit_gpu_h is a PLANNING STUB (ternary > binary-RBFE per-window); calibrate on the first "
                   "leg before trusting the forecast. No measured alpha/dG asserted.",
    }


def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Ternary-cooperativity pure core: pilot legs + MODE=plan forecast.")
    ap.add_argument("--windows", type=int, default=16)
    ap.add_argument("--replicas", type=int, default=3)
    ap.add_argument("--unit-gpu-h", type=float, default=3.0)
    ap.add_argument("--spot-hourly", type=float, default=0.50)
    ap.add_argument("--legs", action="store_true", help="print the frozen pilot leg map and exit")
    args = ap.parse_args(argv)
    if args.legs:
        print(json.dumps(load_pilot_legs(), indent=2))
        return 0
    print(json.dumps(plan(n_windows=args.windows, n_replicas=args.replicas,
                          unit_gpu_h=args.unit_gpu_h, spot_hourly=args.spot_hourly), indent=2))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
