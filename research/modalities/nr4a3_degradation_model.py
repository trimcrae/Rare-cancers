#!/usr/bin/env python3
"""
Quantitative degradation model for the NR4A3 PROTAC (completeness ledger, Tier-A #2 / audit KEEP ×4).

WHY. The program predicts a ternary complex (Boltz-2) and binary affinities (MM-GBSA now, FEP queued), but
never turned those into the numbers that actually decide a degrader: the **degradation window** — DC50, Dmax,
and the **hook effect**. This module supplies that missing layer with the standard three-body cooperative
equilibrium (Douglass et al., JACS 2013; Gadd et al., Nat Chem Biol 2017) coupled to a steady-state
synthesis/degradation balance. It is pure/analytical (numpy), so it runs anywhere and is unit-tested.

HONEST SCOPE. MM-GBSA ΔG is not a calibrated absolute Kd, and cooperativity α is not yet measured — so this is
delivered as (1) a *mechanistic model* and (2) a **sensitivity map** over the parameters FEP will pin down
(binary Kd_target, cooperativity α), NOT a single point DC50. When the selectivity FEP returns absolute ΔG for
NR4A3 vs NR4A1/NR4A2, those Kd's drop straight in and the map collapses to per-paralogue degradation windows —
i.e. this is also the analysis harness the FEP feeds. Nothing here is a calibrated prediction until then; the
defaults are labelled illustrative.

Refs: three-body equilibrium — Douglass, Miller, Sparer, Shapiro, Spellmeyer, JACS 2013, 135, 6092 (doi
10.1021/ja311795d); cooperativity/ternary — Gadd et al., Nat Chem Biol 2017, 13, 514.
"""

import json
import math
import os
import sys

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "nr4a3-degradation-model.json")

# Illustrative defaults (label: NOT calibrated; replaced by FEP-derived Kd's + measured α).
DEFAULTS = {
    "T_tot": 50e-9,        # target (NR4A3) concentration, M  (~50 nM, typical intracellular TF)
    "E_tot": 200e-9,       # CRBN available concentration, M
    "Kd_target": 100e-9,   # PROTAC–NR4A3 binary Kd, M (illustrative good warhead; FEP sets this per paralogue)
    "Kd_e3": 1e-6,         # PROTAC–CRBN binary Kd, M (pomalidomide–CRBN, reported ~1–3 µM range)
    "ksyn_over_kdeg": 0.1,  # target resynthesis rate / max ubiquitination-driven degradation rate
                            # (<1 = degradation outpaces resynthesis, i.e. an effective degrader regime)
}


def _solve_TE(P, T_tot, E_tot, Kd_target, Kd_e3, alpha):
    """For a given FREE protac P, solve the coupled free target/E3 by fixed point. Each is a bounded
    function of the other, so this converges monotonically and keeps every bound species ≤ its total:
        T = T_tot / (1 + P/Kd1 + alpha*E*P/(Kd1*Kd2)),  E = E_tot / (1 + P/Kd2 + alpha*T*P/(Kd1*Kd2)).
    """
    T, E = T_tot, E_tot
    for _ in range(200):
        T_new = T_tot / (1 + P / Kd_target + alpha * E * P / (Kd_target * Kd_e3))
        E_new = E_tot / (1 + P / Kd_e3 + alpha * T_new * P / (Kd_target * Kd_e3))
        if abs(T_new - T) < 1e-24 and abs(E_new - E) < 1e-24:
            T, E = T_new, E_new
            break
        T, E = T_new, E_new
    return T, E


def ternary_concentration(P_tot, T_tot, E_tot, Kd_target, Kd_e3, alpha):
    """Solve the three-body cooperative equilibrium for [ternary] (T·P·E), guaranteed physical.

    Binary: [TP]=[T][P]/Kd_target, [EP]=[E][P]/Kd_e3. Ternary with cooperativity alpha (>1 stabilising):
    [TPE]=alpha*[T][P][E]/(Kd_target*Kd_e3). We bisect on the FREE protac concentration P so that total
    consumed protac equals P_tot; for each trial P the free T,E are solved by _solve_TE (which caps every
    bound species at its total, so [TPE] ≤ min(T_tot,E_tot) by construction — no unphysical frac>1).
    """
    def consumed(P):
        T, E = _solve_TE(P, T_tot, E_tot, Kd_target, Kd_e3, alpha)
        TP = T * P / Kd_target
        EP = E * P / Kd_e3
        TPE = alpha * T * P * E / (Kd_target * Kd_e3)
        return P + TP + EP + TPE, TPE

    lo, hi = 1e-30, P_tot          # free P is in (0, P_tot]
    for _ in range(200):
        mid = math.sqrt(lo * hi)   # geometric bisection (concentrations span many decades)
        c, _tpe = consumed(mid)
        if c > P_tot:
            hi = mid
        else:
            lo = mid
        if hi / lo < 1 + 1e-12:
            break
    _, TPE = consumed(math.sqrt(lo * hi))
    return TPE


def hook_curve(T_tot, E_tot, Kd_target, Kd_e3, alpha, n=71, logP_lo=-11, logP_hi=-2):
    """[ternary] vs PROTAC concentration (log-spaced) — the classic rise-then-fall hook."""
    pts = []
    for i in range(n):
        logP = logP_lo + (logP_hi - logP_lo) * i / (n - 1)
        P = 10 ** logP
        TPE = ternary_concentration(P, T_tot, E_tot, Kd_target, Kd_e3, alpha)
        pts.append({"P_M": P, "ternary_M": TPE, "ternary_frac": TPE / T_tot})
    return pts


def degradation_window(curve, ksyn_over_kdeg):
    """From the ternary hook curve, derive the degradation readouts.

    Steady state: fraction target remaining = ksyn / (ksyn + kdeg * occ), where occ = [ternary]/T_tot is the
    ubiquitination-competent fraction. Dmax = 1 - min(remaining) over [PROTAC]; DC50 = lowest [PROTAC] giving
    50 % degradation. The hook is captured by the ternary peak + the post-peak decline.
    """
    remaining, degraded = [], []
    for pt in curve:
        occ = pt["ternary_frac"]
        rem = ksyn_over_kdeg / (ksyn_over_kdeg + occ) if (ksyn_over_kdeg + occ) > 0 else 1.0
        remaining.append(rem)
        degraded.append(1 - rem)
    dmax = max(degraded)
    # DC50: first P where degraded crosses 0.5 (ascending branch)
    dc50 = None
    for i, pt in enumerate(curve):
        if degraded[i] >= 0.5:
            dc50 = pt["P_M"]
            break
    peak_i = max(range(len(curve)), key=lambda i: curve[i]["ternary_frac"])
    hook = {
        "ternary_peak_frac": curve[peak_i]["ternary_frac"],
        "ternary_peak_P_M": curve[peak_i]["P_M"],
        "post_peak_decline": curve[peak_i]["ternary_frac"] - curve[-1]["ternary_frac"],
        "hook_effect_present": curve[peak_i]["ternary_frac"] - curve[-1]["ternary_frac"] > 0.02,
    }
    return {"Dmax": round(dmax, 3), "DC50_M": dc50, "hook": hook}


def sensitivity_map(params, alphas=(0.3, 1.0, 3.0, 10.0)):
    """Degradation window as a function of cooperativity alpha (the parameter FEP/experiment will pin)."""
    out = {}
    for a in alphas:
        curve = hook_curve(params["T_tot"], params["E_tot"], params["Kd_target"], params["Kd_e3"], a)
        out[f"alpha_{a}"] = degradation_window(curve, params["ksyn_over_kdeg"])
    return out


def kd_target_map(params, kds=(1e-8, 1e-7, 1e-6, 1e-5), alpha=3.0):
    """Degradation window vs binary PROTAC–target Kd — the quantity the selectivity FEP returns directly
    (per paralogue). This is the axis that converts an FEP ΔG_bind into a predicted degradation window, and
    the NR4A3-vs-NR4A1/NR4A2 spread in this map IS the predicted degradation selectivity."""
    out = {}
    for kd in kds:
        curve = hook_curve(params["T_tot"], params["E_tot"], kd, params["Kd_e3"], alpha)
        out[f"KdTarget_{kd:.0e}"] = degradation_window(curve, params["ksyn_over_kdeg"])
    return out


def main():
    p = dict(DEFAULTS)
    result = {
        "_title": "NR4A3 PROTAC degradation model — DC50 / Dmax / hook (ledger Tier-A #2)",
        "_status": "MECHANISTIC MODEL + SENSITIVITY MAP, not a calibrated prediction. Binary Kd_target and "
                   "cooperativity alpha are the two parameters the queued selectivity FEP + ternary will set; "
                   "until then the absolute DC50 is illustrative. The per-alpha map shows how the degradation "
                   "window MOVES with cooperativity — and this same harness consumes FEP-derived per-paralogue "
                   "Kd's to produce NR4A3-vs-NR4A1/NR4A2 degradation-selectivity windows.",
        "_refs": "Douglass et al. JACS 2013 (three-body equilibrium); Gadd et al. Nat Chem Biol 2017 (alpha).",
        "parameters_illustrative": p,
        "sensitivity_over_cooperativity_alpha": sensitivity_map(p),
        "sensitivity_over_binary_Kd_target": kd_target_map(p),
        "interpretation": (
            "Positive cooperativity (alpha>1) lowers DC50 and raises the ternary peak; the hook effect "
            "(ternary decline at high [PROTAC]) is the dosing ceiling. Degradation SELECTIVITY between "
            "paralogues will come from the ratio of per-paralogue [ternary] at matched dose — computed here "
            "once FEP supplies Kd_target for NR4A3 vs NR4A1 vs NR4A2."),
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
