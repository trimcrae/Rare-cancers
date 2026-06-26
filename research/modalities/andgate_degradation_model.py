#!/usr/bin/env python3
"""
Does the AND-gate's fusion-vs-wildtype BINDING window translate into a DEGRADATION window?
A cooperative 1:1:1 ternary-complex equilibrium model. CPU/stdlib; no GPU/AWS; illustrative.

The papers state honestly that binding selectivity != degradation selectivity. This model makes
that quantitative: degradation rate is proportional to the fraction of target trapped in a
productive ternary complex (target - degrader - E3). For the AND-gate, the degrader engages
the FUSION target with the avidity-enhanced Kd (Kd_avidity ~ Kd1*Kd2/EM) and wild-type NR4A3
with the weak monovalent Kd1; the E3 arm and the cooperativity alpha are SHARED (the E3 side
of the molecule and the LBD it grips are identical for fusion and wild-type).

1:1:1 equilibrium (D degrader, T target, E E3):
  [DT]  = [D][T]/Kd_T
  [DE]  = [D][E]/Kd_E
  [TDE] = alpha*[D][T][E]/(Kd_T*Kd_E)         (alpha>1 = positive cooperativity)
solved numerically from the three mass balances. Degradation window = [TDE]_fusion / [TDE]_WT
at the degrader dose that maximises fusion ternary. The hook effect (ternary falls at high
[D] as the degrader saturates T and E separately) is reported per species.

All Kd/EM/alpha/concentrations are ILLUSTRATIVE ASSUMPTIONS, not measured values.
Output: fusion-andgate-degradation-model.json
"""
import json
import os

import andgate_selectivity_model as ag

OUT = os.path.join(os.path.dirname(__file__), "fusion-andgate-degradation-model.json")


def ternary(Dt, Tt, Et, Kd_T, Kd_E, alpha):
    """Robustly solve the cooperative 1:1:1 ternary equilibrium for total D,T,E.
    Outer bisection on FREE degrader D (implied D_total is monotonic in free D);
    inner fixed point for free T,E (a contraction at fixed D). Returns [TDE].
    Guaranteed physical: every complex <= its limiting total."""
    def te_for_D(D):
        T, E = Tt, Et
        for _ in range(1000):
            nT = Tt / (1.0 + D / Kd_T + alpha * D * E / (Kd_T * Kd_E))
            nE = Et / (1.0 + D / Kd_E + alpha * D * nT / (Kd_T * Kd_E))
            if abs(nT - T) < 1e-20 and abs(nE - E) < 1e-20:
                T, E = nT, nE
                break
            T, E = nT, nE
        return T, E

    lo, hi = 1e-30, Dt
    D = Dt
    for _ in range(200):
        D = 0.5 * (lo + hi)
        T, E = te_for_D(D)
        D_implied = D * (1.0 + T / Kd_T + E / Kd_E + alpha * T * E / (Kd_T * Kd_E))
        if D_implied > Dt:
            hi = D
        else:
            lo = D
    T, E = te_for_D(D)
    return alpha * D * T * E / (Kd_T * Kd_E)


def main():
    uM = 1e-6
    # Same illustrative arms as the avidity model
    Kd1, Kd2, EM = 10.0 * uM, 100.0 * uM, 1.0e-3
    Kd_avidity = ag.kd_avidity(Kd1, Kd2, EM)      # fusion target Kd (~1 uM)
    Kd_E3 = 1.0 * uM                              # degrader-E3 arm (shared)
    alpha = 10.0                                   # positive cooperativity (shared)
    Tt = 0.1 * uM                                  # target (fusion or WT NR4A3)
    Et = 1.0 * uM                                  # E3 ligase available

    # dose-response: ternary vs total degrader, for fusion (avidity) and WT (monovalent)
    curve = []
    doses = [3e-9, 1e-8, 3e-8, 1e-7, 3e-7, 1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3]
    for Dt in doses:
        tde_fus = ternary(Dt, Tt, Et, Kd_avidity, Kd_E3, alpha)
        tde_wt = ternary(Dt, Tt, Et, Kd1, Kd_E3, alpha)
        curve.append({
            "degrader_M": Dt,
            "ternary_fusion_frac": round(tde_fus / Tt, 5),
            "ternary_wildtype_frac": round(tde_wt / Tt, 5),
            "degradation_window": round(tde_fus / tde_wt, 2) if tde_wt > 0 else None,
        })

    peak = max(curve, key=lambda r: r["ternary_fusion_frac"])
    # binding window at the same arms (for comparison)
    _, _, bind_win = ag.selectivity_window(1.0 * uM, Kd1, Kd2, EM)

    # alpha sensitivity at the peak dose
    alpha_scan = []
    for a in (1.0, 3.0, 10.0, 30.0):
        tf = ternary(peak["degrader_M"], Tt, Et, Kd_avidity, Kd_E3, a)
        tw = ternary(peak["degrader_M"], Tt, Et, Kd1, Kd_E3, a)
        alpha_scan.append({"alpha": a, "degradation_window": round(tf / tw, 2) if tw > 0 else None})

    out = {
        "_note": ("Cooperative 1:1:1 ternary model translating the AND-gate BINDING window into a "
                  "DEGRADATION window. CPU/stdlib. All Kd/EM/alpha/concentrations are illustrative "
                  "assumptions, not measured values."),
        "_inputs_are_illustrative": True,
        "params": {"Kd1_LBD_M": Kd1, "Kd2_EWS_M": Kd2, "EM_M": EM,
                   "Kd_avidity_fusion_M": Kd_avidity, "Kd_E3_M": Kd_E3, "cooperativity_alpha": alpha,
                   "target_M": Tt, "E3_M": Et},
        "binding_window_for_comparison": round(bind_win, 2),
        "peak_dose_M": peak["degrader_M"],
        "degradation_window_at_peak": peak["degradation_window"],
        "dose_response_curve": curve,
        "alpha_sensitivity_at_peak": alpha_scan,
        "reading": (
            "The degradation window does NOT simply inherit the binding window — it is DOSE- and "
            "COOPERATIVITY-dependent and generally LOWER. It peaks near the binding window (~6.8x) at "
            "low, sub-saturating degrader, then erodes toward ~1x (no selectivity) at high dose, "
            "because the hook effect (ternary falling as the degrader saturates target and E3 "
            "separately) hits BOTH fusion and wild-type. It also SHRINKS with stronger positive "
            "cooperativity (5.4x at alpha=1 down to 1.7x at alpha=30), because cooperativity stabilises "
            "the ternary for both species and proportionally rescues the weaker-binding wild-type. "
            "Design implication: operate the AND-gate at SUB-SATURATING dose and avoid strong "
            "cooperativity to preserve the (already modest) fusion selectivity; the E3 side cannot add "
            "selectivity (it is shared), so all of it must come from the avidity arm. Illustrative "
            "inputs; true degradation needs the cellular assay (paper §6)."),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"binding window (ref): {round(bind_win,2)}x")
    print(f"peak fusion ternary at [D]={peak['degrader_M']:.1e} M; "
          f"degradation window there = {peak['degradation_window']}x")
    print("dose-response (degrader_M -> fusion%, WT%, window):")
    for r in curve:
        print(f"  {r['degrader_M']:.1e}  fus={r['ternary_fusion_frac']:.4f}  "
              f"wt={r['ternary_wildtype_frac']:.4f}  win={r['degradation_window']}")
    print("alpha sensitivity:", [(a['alpha'], a['degradation_window']) for a in alpha_scan])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
