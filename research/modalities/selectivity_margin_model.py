#!/usr/bin/env python3
"""
HOW MUCH selectivity margin does DEGRADATION actually need — and can our physics resolve it? ($0 CPU)

THE GAP THIS CLOSES. The prospective ladder is built to *rank* paralogues by ternary thermodynamics, but nowhere
does the plan state how large a free-energy margin has to be before it produces a degradation window worth
claiming, nor whether a margin of that size is even resolvable by the ternary FEP's replicate-level noise. Those
two numbers decide whether the whole interface-thermodynamics axis is a viable search strategy or a coin flip
dressed as a calculation. This module computes both and puts them side by side.

WHAT IT DOES.
  1. REQUIRED margin — a cooperative 1:1:1 ternary equilibrium (the same model as
     andgate_degradation_model.ternary, reused not re-derived) feeding a steady-state synthesis/degradation
     balance. Sweeps a free-energy margin applied to the NR4A3 arm and reports the dose-response window against a
     paralogue: at what margin does NR4A3 degradation reach a target while the paralogue stays below a ceiling?
  2. RESOLVABLE margin — the minimum detectable difference (MDD) between two ΔΔG estimates given the prereg's
     replicate-SD error model (NOT MBAR SE) and n replicates.
  3. CATEGORICAL axes — the same window when the paralogue is not thermodynamically disfavoured but
     STRUCTURALLY incapable: no lysine in the transfer zone (ubiquitination efficiency -> 0), or no nucleophile
     for a covalent/reversible-covalent handle (no residence-time gain). This is the honest quantification of why
     a categorical mechanism is worth more than a marginal thermodynamic one.

HONESTY. Every concentration, K_d, α, rate and efficiency here is an ILLUSTRATIVE ASSUMPTION — none is measured
for NR4A3, and the module asserts no affinity, no cooperativity and no degradation. Its output is a SENSITIVITY
statement of the form "a margin of X kcal/mol is needed for window Y under assumptions Z", which is exactly the
kind of statement a design plan needs and does not currently have. It is not a prediction about any compound.
Defaults are swept, and the headline conclusions are reported across the sweep, not at one parameter point.

Output: nr4a3-selectivity-margin-model.json (+ .md)
"""
from __future__ import annotations

import argparse
import functools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import andgate_degradation_model as agd   # noqa: E402  (the cooperative 1:1:1 ternary solver)

R_KCAL = 0.0019872041
DEFAULT_T = 298.15
RT = R_KCAL * DEFAULT_T                    # ~0.5925 kcal/mol at 298.15 K


# =============================================================================================================
# free energy <-> equilibrium
# =============================================================================================================
def fold_from_ddg(ddg_kcal, T=DEFAULT_T):
    """A margin of `ddg_kcal` (favourable, positive = better) as a multiplicative affinity/α factor."""
    return math.exp(ddg_kcal / (R_KCAL * T))


def ddg_from_fold(fold, T=DEFAULT_T):
    return R_KCAL * T * math.log(fold)


# =============================================================================================================
# occupancy -> degradation
# =============================================================================================================
def ternary_fraction(D_total, T_total, E_total, kd_target, kd_e3, alpha):
    """Fraction of TOTAL target held in the productive ternary complex at degrader dose `D_total`."""
    tde = agd.ternary(D_total, T_total, E_total, kd_target, kd_e3, alpha)
    return max(0.0, min(1.0, tde / T_total))


def degradation(frac_ternary, ubiq_efficiency, k_ub_max_over_k_basal):
    """Steady-state fractional depletion.

    dP/dt = k_syn - (k_basal + k_ub_max * f_ternary * eps) * P  =>  P_ss/P_0 = 1 / (1 + kappa * f * eps)
    with kappa = k_ub_max / k_basal. `eps` (0..1) is UBIQUITINATION EFFICIENCY: how competent the ternary
    geometry is at presenting an accessible lysine to the E2~Ub. eps = 0 => no degradation however much ternary
    complex forms — which is exactly the paralogue-unique-lysine mechanism."""
    drive = k_ub_max_over_k_basal * frac_ternary * max(0.0, ubiq_efficiency)
    return 1.0 - 1.0 / (1.0 + drive)


@functools.lru_cache(maxsize=4096)
def _f_curve(kd_target, kd_e3, alpha, target_total, e3_total, lo, hi, n):
    """Cached ternary-fraction-vs-dose curve. The equilibrium solve is the only expensive step in this module
    and it depends on NEITHER the ubiquitination drive NOR the margin bookkeeping, so one curve per distinct
    (K_d, alpha, concentrations, dose grid) serves every scenario that reuses it."""
    doses = [10.0 ** (lo + (hi - lo) * i / (n - 1)) for i in range(n)]
    return tuple(doses), tuple(ternary_fraction(d, target_total, e3_total, kd_target, kd_e3, alpha)
                               for d in doses)


def f_curve(kd_target, alpha, params):
    return _f_curve(kd_target, params["kd_e3_uM"], alpha, params["target_total_uM"], params["e3_total_uM"],
                    params["dose_log10_lo"], params["dose_log10_hi"], params["dose_points"])


def dose_response(kd_target, kd_e3, alpha, ubiq_efficiency, params):
    """Degradation vs dose over a log sweep. Returns (doses, degradations) — the hook effect is inherited from
    the equilibrium solver (ternary falls at high dose as the degrader saturates target and E3 separately)."""
    doses, fs = f_curve(kd_target, alpha, params)
    return list(doses), [degradation(f, ubiq_efficiency, params["k_ub_max_over_k_basal"]) for f in fs]


def calibrate_drive(params, kd_target, alpha, eps):
    """Solve for the ubiquitination drive kappa = k_ub_max/k_basal that makes the ON-TARGET arm a WORKING
    degrader — i.e. its best-over-dose degradation equals `params['on_target_dmax']`.

    WHY THIS MATTERS. Without it the model silently conflates two different failures: "the paralogue is spared"
    and "nothing is degraded at all because the assumed drive is too weak". Calibrating first means every
    scenario asks the same question — GIVEN a compound that does degrade NR4A3, how much margin spares the
    paralogue? A degrader that does not degrade its own target is not a selectivity candidate in the first
    place, so that regime carries no information about selectivity and must not be counted as one."""
    f_max = max(f_curve(kd_target, alpha, params)[1])
    if f_max <= 0 or eps <= 0:
        return None
    tgt = params["on_target_dmax"]
    return (tgt / (1.0 - tgt)) / (f_max * eps)


def window(arm3, arm_par, params):
    """The threshold-free selectivity metric: over the dose sweep, the BEST NR4A3 degradation achievable at any
    dose where the paralogue stays at or below `paralogue_ceiling`. Both arms are evaluated at the SAME dose —
    a "window" that needs a different dose per paralogue is not a window.

    Reported as a CONTINUOUS quantity on purpose. An earlier version asked a binary "does it clear 90%?", and
    the answer flipped with the threshold — which means the threshold, not the biology, was driving the
    conclusion. `deg_nr4a3_at_ceiling` has no such freedom: with zero selectivity the two arms are identical at
    every dose, so the metric is pinned to the ceiling itself (0.20 here), and any excess above the ceiling is
    exactly the selectivity the mechanism bought."""
    doses, d3 = dose_response(*arm3, params)
    _, dp = dose_response(*arm_par, params)
    best = {"dose_uM": None, "deg_nr4a3_at_ceiling": 0.0, "deg_paralogue": 0.0}
    for dose, a, b in zip(doses, d3, dp):
        if b <= params["paralogue_ceiling"] and a > best["deg_nr4a3_at_ceiling"]:
            best = {"dose_uM": dose, "deg_nr4a3_at_ceiling": a, "deg_paralogue": b}
    best["max_deg_nr4a3_any_dose"] = max(d3)
    best["max_deg_paralogue_any_dose"] = max(dp)
    return best


# =============================================================================================================
# 1. required margin
# =============================================================================================================
def required_margin(params, margin_grid=None, targets=(0.70, 0.80, 0.90)):
    """Sweep a favourable free-energy margin applied to the NR4A3 TERNARY arm (equivalently to its cooperativity
    alpha, where an induced-interface advantage shows up) and report, for each NR4A3 degradation target, the
    smallest margin at which the window metric reaches it. `None` = unreachable within the grid."""
    grid = margin_grid or [round(0.25 * i, 2) for i in range(0, 33)]   # 0 .. 8 kcal/mol, 0.25 steps
    kd_t, kd_e = params["kd_target_uM"], params["kd_e3_uM"]
    a0, eps = params["alpha_baseline"], params["ubiq_efficiency"]
    rows, thresholds = [], {t: None for t in targets}
    for m in grid:
        a3 = a0 * fold_from_ddg(m)
        kappa = calibrate_drive(params, kd_t, a3, eps)
        if kappa is None:
            continue
        p = dict(params, k_ub_max_over_k_basal=kappa)
        w = window((kd_t, kd_e, a3, eps), (kd_t, kd_e, a0, eps), p)
        rows.append({"margin_kcal": m, "alpha_nr4a3": round(a3, 2),
                     "dose_uM": None if w["dose_uM"] is None else round(w["dose_uM"], 4),
                     "deg_nr4a3_at_ceiling": round(w["deg_nr4a3_at_ceiling"], 3),
                     "deg_paralogue": round(w["deg_paralogue"], 3)})
        for t in targets:
            if thresholds[t] is None and w["deg_nr4a3_at_ceiling"] >= t:
                thresholds[t] = m
    return {"sweep": rows,
            "required_margin_kcal_by_target": {str(t): thresholds[t] for t in targets},
            "note": ("Margin applied to the NR4A3 ternary arm only (alpha_NR4A3 = alpha_baseline x "
                     "exp(margin/RT)); binary warhead affinity held EQUAL across paralogues, the conservative "
                     "assumption for a ~70%-conserved pocket. The ubiquitination drive is re-calibrated at "
                     "every margin so the NR4A3 arm is always a working degrader (see calibrate_drive).")}


# =============================================================================================================
# 2. resolvable margin
# =============================================================================================================
def minimum_detectable_difference(replicate_sd_kcal, n_replicates, z=1.96):
    """Smallest difference between two independently-estimated ΔΔG values that a two-sided test at confidence
    `z` can separate, given the prereg's REPLICATE-SD error model. SE(difference) = sd * sqrt(2/n)."""
    if n_replicates < 1:
        raise ValueError("n_replicates must be >= 1")
    return z * replicate_sd_kcal * math.sqrt(2.0 / n_replicates)


def resolution_table(sds=(0.4, 0.7, 1.0), ns=(2, 3, 5, 8)):
    return [{"replicate_sd_kcal": sd, "n_replicates": n,
             "mdd_kcal_95pct": round(minimum_detectable_difference(sd, n), 2)}
            for sd in sds for n in ns]


# =============================================================================================================
# =============================================================================================================
# 2b. covalent capture — the KINETIC form (an equilibrium K_d cannot represent it)
# =============================================================================================================
def covalent_labelled_fraction(dose_uM, kd_target_uM, k_inact_per_h, hours):
    """Fraction of target carrying a permanent adduct after `hours` of exposure.

    WHY A SEPARATE TREATMENT. Irreversible covalent capture is not an affinity — it is a TIME-INTEGRATING
    process: L(t) = 1 - exp(-k_inact * theta * t) with theta the reversible occupancy. It does not saturate at
    an equilibrium constant, so representing it as an effective K_d (as `categorical_axes` must, to stay inside
    the equilibrium model) systematically UNDERSTATES it. The paralogue's L is exactly 0 — not small, zero —
    because there is no nucleophile at the aligned position, which is what makes this axis categorical.

    Honest limits: no k_inact/K_I fit, no competing glutathione/off-target consumption, no resynthesis of the
    target during exposure, and no representation of the stoichiometry cost (an irreversible covalent PROTAC is
    consumed with its target and loses catalytic turnover — the reason the write-up recommends a REVERSIBLE
    covalent handle)."""
    theta = dose_uM / (dose_uM + kd_target_uM)
    return 1.0 - math.exp(-k_inact_per_h * theta * hours)


def covalent_kinetic_window(params):
    """The window metric when NR4A3 (and only NR4A3) can be covalently captured, evaluated at `exposure_h`.

    A covalently captured target is permanently degrader-bound, so its ternary fraction no longer depends on
    the warhead equilibrium at all — only on E3 engagement, with cooperativity folded in as an effective E3
    K_d. Unlabelled target (and the whole paralogue pool) stays on the ordinary equilibrium curve."""
    p = params
    kd_t, kd_e, a0, eps = p["kd_target_uM"], p["kd_e3_uM"], p["alpha_baseline"], p["ubiq_efficiency"]
    doses, f_eq = f_curve(kd_t, a0, p)
    kd_e_eff = kd_e / max(a0, 1e-9)
    f_labelled = p["e3_total_uM"] / (p["e3_total_uM"] + kd_e_eff)      # E3 arm only, cooperativity-enhanced
    kappa = calibrate_drive(p, kd_t, a0, eps)
    if kappa is None:
        return None
    best = {"dose_uM": None, "deg_nr4a3_at_ceiling": 0.0, "deg_paralogue": 0.0, "labelled_fraction": 0.0}
    for dose, f in zip(doses, f_eq):
        L = covalent_labelled_fraction(dose, kd_t, p["k_inact_per_h"], p["exposure_h"])
        f3 = L * f_labelled + (1.0 - L) * f
        d3 = degradation(f3, eps, kappa)
        dp = degradation(f, eps, kappa)                                # paralogue: L = 0 exactly
        if dp <= p["paralogue_ceiling"] and d3 > best["deg_nr4a3_at_ceiling"]:
            best = {"dose_uM": round(dose, 4), "deg_nr4a3_at_ceiling": round(d3, 3),
                    "deg_paralogue": round(dp, 3), "labelled_fraction": round(L, 3)}
    return best


# =============================================================================================================
# 3. categorical axes
# =============================================================================================================
def categorical_axes(params):
    """The same window metric when the paralogue is STRUCTURALLY incapable rather than thermodynamically
    disfavoured — every scenario below runs at ZERO thermodynamic margin (identical ternary energetics on both
    paralogues), so whatever separation appears is bought entirely by the categorical mechanism.

      * unique_lysine  — the paralogue has no lysine in the transfer zone, so its ubiquitination efficiency is
        cut to `eps_paralogue_frac` of NR4A3's.
      * covalent       — only NR4A3 offers a nucleophile, so only its arm gets the effective-affinity gain of
        (reversible-)covalent capture (`covalent_gain_fold`).
      * combined       — both.
    `interface_thermodynamics_only` is the NULL: identical arms, so the best NR4A3 degradation at the paralogue
    ceiling is the ceiling itself. Anything above that is the mechanism's contribution."""
    kd_t, kd_e, a0, eps = (params["kd_target_uM"], params["kd_e3_uM"],
                           params["alpha_baseline"], params["ubiq_efficiency"])
    gain = params["covalent_gain_fold"]
    eps_par = eps * params["eps_paralogue_frac"]
    scenarios = {
        "interface_thermodynamics_only": ((kd_t, kd_e, a0, eps), (kd_t, kd_e, a0, eps)),
        "unique_lysine": ((kd_t, kd_e, a0, eps), (kd_t, kd_e, a0, eps_par)),
        "covalent_capture": ((kd_t / gain, kd_e, a0, eps), (kd_t, kd_e, a0, eps)),
        "covalent_plus_unique_lysine": ((kd_t / gain, kd_e, a0, eps), (kd_t, kd_e, a0, eps_par)),
    }
    out = {}
    for name, (a3, ap) in scenarios.items():
        kappa = calibrate_drive(params, a3[0], a3[2], a3[3])
        if kappa is None:
            continue
        p = dict(params, k_ub_max_over_k_basal=kappa)
        w = window(a3, ap, p)
        out[name] = {"dose_uM": None if w["dose_uM"] is None else round(w["dose_uM"], 4),
                     "deg_nr4a3_at_ceiling": round(w["deg_nr4a3_at_ceiling"], 3),
                     "deg_paralogue": round(w["deg_paralogue"], 3)}
    kin = covalent_kinetic_window(params)
    if kin is not None:
        out["covalent_capture_KINETIC"] = kin
    out["_covalent_gain_as_margin_kcal"] = round(ddg_from_fold(gain), 2)
    out["_null_is_the_ceiling"] = params["paralogue_ceiling"]
    out["_note_covalent"] = ("`covalent_capture` is the EQUILIBRIUM proxy (an effective-affinity gain) and is a "
                             "LOWER BOUND; `covalent_capture_KINETIC` is the time-integrating form, which is "
                             "what an irreversible adduct actually does. Neither models the loss of catalytic "
                             "turnover an irreversible covalent PROTAC incurs.")
    return out


# =============================================================================================================
DEFAULT_PARAMS = {
    # --- system (illustrative; intracellular scales, NOT measured for NR4A3) ---
    "target_total_uM": 0.1,
    "e3_total_uM": 1.0,
    "kd_target_uM": 0.1,            # warhead-target K_d, held EQUAL across paralogues (conservative)
    "kd_e3_uM": 1.0,                # E3-ligand K_d (VHL-ligand scale)
    "alpha_baseline": 3.0,          # baseline cooperativity, both paralogues
    "ubiq_efficiency": 0.5,         # transfer-zone competence when a usable lysine IS present
    "on_target_dmax": 0.95,         # the NR4A3 arm is calibrated to be a WORKING degrader at this D_max
    "k_ub_max_over_k_basal": 20.0,  # placeholder; overwritten per-scenario by calibrate_drive
    # --- what counts as a window ---
    "paralogue_ceiling": 0.20,      # the paralogue must stay <=20% degraded at the SAME dose
    # --- categorical-axis assumptions ---
    "eps_paralogue_frac": 0.05,     # paralogue keeps 5% of transfer competence with no unique lysine
    "covalent_gain_fold": 30.0,     # effective-affinity gain from (reversible-)covalent capture, NR4A3 only
    "k_inact_per_h": 0.2,           # covalent inactivation rate at full occupancy (mild electrophile)
    "exposure_h": 24.0,             # exposure window over which the adduct accumulates
    # --- dose sweep ---
    "dose_log10_lo": -4.0, "dose_log10_hi": 3.0, "dose_points": 71,
}

# A grid of PLAUSIBLE regimes. Reporting one hand-picked parameter point would let the answer be tuned; the
# conclusion must be read off the grid. Ranges bracket published PROTAC behaviour: warhead K_d 10 nM - 1 uM,
# cooperativity from none (alpha=1) to strongly cooperative (alpha=10), on-target D_max 90-99%.
SCENARIO_GRID = {
    "kd_target_uM": (0.01, 0.1, 1.0),
    "alpha_baseline": (1.0, 3.0, 10.0),
    "on_target_dmax": (0.90, 0.95, 0.99),
}


def scenario_sweep(base):
    """Required margin AND categorical-axis outcomes across the whole grid; one row per scenario."""
    rows = []
    for kd in SCENARIO_GRID["kd_target_uM"]:
        for a0 in SCENARIO_GRID["alpha_baseline"]:
            for dmax in SCENARIO_GRID["on_target_dmax"]:
                p = dict(base, kd_target_uM=kd, alpha_baseline=a0, on_target_dmax=dmax)
                req = required_margin(p)
                cat = categorical_axes(p)
                rows.append({
                    "kd_target_uM": kd, "alpha_baseline": a0, "on_target_dmax": dmax,
                    "required_margin_kcal_by_target": req["required_margin_kcal_by_target"],
                    "categorical_deg_nr4a3_at_ceiling": {
                        k: v["deg_nr4a3_at_ceiling"] for k, v in cat.items() if not k.startswith("_")},
                })
    return rows


def _median(xs):
    xs = sorted(xs)
    return None if not xs else xs[len(xs) // 2]


def _grid_summary(rows, mdd):
    n = len(rows)
    by_t = {}
    for t in ("0.7", "0.8", "0.9"):
        got = [r["required_margin_kcal_by_target"].get(t) for r in rows]
        got = [g for g in got if g is not None]
        by_t[t] = {"n_reachable": len(got), "min": min(got) if got else None,
                   "median": _median(got), "max": max(got) if got else None,
                   "n_above_mdd": sum(1 for g in got if g > mdd)}
    cat_keys = list(rows[0]["categorical_deg_nr4a3_at_ceiling"].keys()) if rows else []
    cat_med = {k: _median([r["categorical_deg_nr4a3_at_ceiling"][k] for r in rows]) for k in cat_keys}
    return {"n_scenarios": n, "required_margin_by_target": by_t,
            "median_deg_nr4a3_at_ceiling_zero_margin": cat_med, "mdd_kcal_used": round(mdd, 2)}


def build(params=None):
    p = dict(DEFAULT_PARAMS)
    p.update(params or {})
    req = required_margin(p)
    res = resolution_table()
    cat = categorical_axes(p)
    mdd_typ = minimum_detectable_difference(0.7, 3)
    rows = scenario_sweep(p)
    grid = _grid_summary(rows, mdd_typ)
    verdict = _verdict(mdd_typ, grid)
    return {
        "_title": "How much selectivity margin does degradation need, and can the physics resolve it?",
        "_limits": [
            "Every K_d, alpha, concentration, rate and efficiency is an ILLUSTRATIVE ASSUMPTION - none is "
            "measured for NR4A3 or any degrader. This is a sensitivity analysis, not a prediction.",
            "1:1:1 equilibrium with a steady-state degradation balance: no explicit E2~Ub kinetics, no "
            "processivity, no deubiquitinase competition, no permeability or exposure term.",
            "The margin is applied to the ternary arm only; a real design changes binary affinity, "
            "cooperativity and geometry together.",
            "Covalent capture is modelled as an effective-affinity gain, NOT a k_inact/K_I treatment; an "
            "IRREVERSIBLE covalent PROTAC also sacrifices catalytic turnover (hence the reversible-covalent "
            "recommendation in the write-up), which this model does not represent.",
            "The unique-lysine axis is modelled as a drop in ubiquitination efficiency, not as a geometric "
            "calculation - establishing the actual transfer-zone geometry is the ternary/CRL stage's job.",
            "No efficacy, safety, therapeutic-window or clinical claim is made or implied.",
        ],
        "params": p, "required_margin": req,
        "resolution": {
            "note": ("MDD = z * replicate_SD * sqrt(2/n) for the difference of two independently-estimated "
                     "ddG values; replicate SD (prereg), NOT MBAR SE. Separate from ACCURACY: OpenFE's public "
                     "RBFE benchmark is ~1.7 kcal/mol RMSE, and the ternary/NAGL lane has no accuracy number "
                     "of its own until Val B."),
            "table": res, "typical_mdd_kcal_sd0.7_n3": round(mdd_typ, 2),
        },
        "categorical_axes": cat, "scenario_grid": rows, "grid_summary": grid, "verdict": verdict,
    }


def _verdict(mdd, grid):
    t80 = grid["required_margin_by_target"]["0.8"]
    cat = grid["median_deg_nr4a3_at_ceiling_zero_margin"]
    null = cat.get("interface_thermodynamics_only")
    med = t80["median"]
    if med is None:
        head = ("Across the grid, NO thermodynamic margin up to 8 kcal/mol reaches 80% NR4A3 degradation at a "
                "20% paralogue ceiling - the induced-interface axis alone cannot deliver the window.")
        ratio = None
    else:
        ratio = round(med / mdd, 2)
        head = (f"To reach 80% NR4A3 degradation while a paralogue stays under 20%, the induced interface must "
                f"supply a TRUE margin of ~{med:.2f} kcal/mol (grid range {t80['min']}-{t80['max']} over "
                f"{grid['n_scenarios']} scenarios). The best-case RESOLVABLE difference is {mdd:.2f} kcal/mol "
                f"(replicate SD 0.7, n=3), so the required effect is ~{ratio}x the noise floor and of the same "
                f"order as the method's ACCURACY (~1.7 kcal/mol RMSE on the public RBFE benchmark).")
    cat_line = (f" At ZERO thermodynamic margin the null gives {null} (the ceiling, by construction), while the "
                f"categorical axes give a median {cat.get('unique_lysine')} (unique lysine), "
                f"{cat.get('covalent_capture_KINETIC')} (covalent capture, time-integrating form; the "
                f"equilibrium proxy's {cat.get('covalent_capture')} is a lower bound) and "
                f"{cat.get('covalent_plus_unique_lysine')} (affinity-proxy covalent + unique lysine) - "
                f"selectivity bought with no free-energy contest at all.")
    return {"headline": head + cat_line, "required_over_resolvable": ratio,
            "implication": ("Rank the search axes by whether the mechanism is CATEGORICAL (present/absent) or "
                            "MARGINAL (a free-energy contest). Spend the alchemy on CONFIRMING a categorical "
                            "design, not on trying to WIN a contest at the edge of resolution.")}


def to_markdown(d):
    p, req, res, cat, g = d["params"], d["required_margin"], d["resolution"], d["categorical_axes"], \
        d["grid_summary"]
    L = [f"# {d['_title']}", "",
         f"Metric: the **best NR4A3 degradation reachable at any dose where the paralogue stays "
         f"<={int(p['paralogue_ceiling']*100)}%**, both arms at the SAME dose. With zero selectivity the two "
         f"arms are identical, so the metric is pinned at the ceiling ({p['paralogue_ceiling']}) - everything "
         f"above that is what the mechanism bought.", "",
         "## 1. Required thermodynamic margin (single reference scenario)", "",
         "| margin (kcal/mol) | alpha(NR4A3) | dose (uM) | deg NR4A3 @ ceiling | deg paralogue |",
         "|---|---|---|---|---|"]
    for r in req["sweep"]:
        if r["margin_kcal"] * 2 % 1:
            continue
        L.append(f"| {r['margin_kcal']:.2f} | {r['alpha_nr4a3']} | {r['dose_uM']} | "
                 f"{r['deg_nr4a3_at_ceiling']} | {r['deg_paralogue']} |")
    L += ["", "**Margin required, across the whole scenario grid:**", "",
          "| NR4A3 target | scenarios reachable | min | median | max | above MDD |", "|---|---|---|---|---|---|"]
    for t, v in g["required_margin_by_target"].items():
        L.append(f"| {float(t):.0%} | {v['n_reachable']}/{g['n_scenarios']} | {v['min']} | {v['median']} | "
                 f"{v['max']} | {v['n_above_mdd']} |")
    L += ["", req["note"], "", "## 2. Resolvable difference (replicate-SD error model)", "",
          "| replicate SD | n | MDD @95% |", "|---|---|---|"]
    for r in res["table"]:
        L.append(f"| {r['replicate_sd_kcal']} | {r['n_replicates']} | **{r['mdd_kcal_95pct']}** |")
    L += ["", res["note"], "",
          "## 3. Categorical axes - the same metric at ZERO thermodynamic margin", "",
          "| scenario | dose (uM) | deg NR4A3 @ ceiling | deg paralogue |", "|---|---|---|---|"]
    for k, v in cat.items():
        if k.startswith("_"):
            continue
        L.append(f"| {k} | {v['dose_uM']} | **{v['deg_nr4a3_at_ceiling']}** | {v['deg_paralogue']} |")
    L += ["", "Median across the whole grid:", "",
          "| scenario | median deg NR4A3 @ ceiling |", "|---|---|"]
    for k, v in g["median_deg_nr4a3_at_ceiling_zero_margin"].items():
        L.append(f"| {k} | **{v}** |")
    L += ["", f"(A {p['covalent_gain_fold']}x covalent effective-affinity gain == "
              f"{cat['_covalent_gain_as_margin_kcal']} kcal/mol - but it applies to NR4A3 ONLY, because the "
              f"paralogues have no nucleophile at the aligned position.)", "",
          "## Verdict", "", f"**{d['verdict']['headline']}**", "", d["verdict"]["implication"], "",
          "## Honest limits", ""] + [f"- {x}" for x in d["_limits"]]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a3-selectivity-margin-model.json"))
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="override a parameter, e.g. --set alpha_baseline=10")
    args = ap.parse_args(argv)
    over = {}
    for kv in args.set:
        k, v = kv.split("=", 1)
        over[k] = float(v)
    d = build(over)
    with open(args.out, "w") as f:
        json.dump(d, f, indent=1)
    with open(os.path.splitext(args.out)[0] + ".md", "w") as f:
        f.write(to_markdown(d))
    print(json.dumps(d["grid_summary"], indent=1))
    print()
    print(d["verdict"]["headline"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
