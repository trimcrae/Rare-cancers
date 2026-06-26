#!/usr/bin/env python3
"""
Linker geometry -> effective molarity (EM) -> AND-gate selectivity window.
CPU/stdlib only; no GPU/AWS; no external data.

WHY: the AND-gate avidity model (andgate_selectivity_model.py) treats the effective
molarity EM as a free swept parameter. EM is actually set by the LINKER: a flexible tether
of contour length L_c holds the second arm at a local concentration around the first site.
This script grounds EM in standard polymer physics (Gaussian/ideal-chain end-density), then
feeds the physics-derived EM into the avidity model to predict the realistic fusion-vs-
wild-type window as a function of linker length.

MODEL (ideal/Gaussian chain, best-case geometry):
  mean-square end-to-end distance  <r^2> = L_c * b           (b = Kuhn length)
  end-density at coincident sites   P(0) = (3 / (2*pi*<r^2>))^(3/2)   [nm^-3]
  effective molarity                EM   = P(0) * 1e24 / N_A           [mol/L]
This is the EM when the second site sits at the chain's most-probable reach (d ~ 0),
i.e. an UPPER BOUND. On a mobile, disordered EWS-LC anchor the realised EM is lower
(the chain end is not reliably positioned), so treat these as optimistic EM ceilings —
consistent with the paper's honest caveat that the ~11x window is a ceiling.

Linker length is mapped from common chemistries: each PEG unit (-CH2CH2O-) or methylene
contributes ~0.35 nm of projected contour length per ~2-3 backbone bonds; we report by
contour length directly and annotate approximate PEG-unit equivalents.
"""
import json
import math
import os

import andgate_selectivity_model as ag   # reuse the validated avidity functions

OUT = os.path.join(os.path.dirname(__file__), "fusion-andgate-linker-em.json")

NA = 6.02214076e23          # Avogadro
B_KUHN_NM = 0.5             # Kuhn length for a flexible PEG/alkyl linker (~0.4-0.7 nm typical)
NM3_PER_L = 1e24            # 1 litre = 1e24 nm^3
PROJ_NM_PER_PEG = 0.35      # approx projected contour length per PEG/methylene unit


def em_from_contour(Lc_nm, b_nm=B_KUHN_NM):
    """Ideal-chain effective molarity (mol/L) at coincident sites for contour length Lc."""
    r2 = Lc_nm * b_nm                                   # <r^2> = N*b^2 = (Lc/b)*b^2 = Lc*b
    p0_nm3 = (3.0 / (2.0 * math.pi * r2)) ** 1.5        # nm^-3
    return p0_nm3 * NM3_PER_L / NA                      # mol/L


def main():
    uM = 1e-6
    # Same illustrative arm affinities as the base avidity model (so the EM is the only
    # thing changing here): arm-1 (LBD) weak, arm-2 (EWS-LC) very weak.
    Kd1, Kd2, L_dose = 10.0 * uM, 100.0 * uM, 1.0 * uM

    rows = []
    for Lc in (1.0, 2.0, 3.5, 5.0, 7.0, 10.0, 14.0, 20.0, 30.0):
        EM = em_from_contour(Lc)
        f_fus, f_wt, win = ag.selectivity_window(L_dose, Kd1, Kd2, EM)
        rows.append({
            "linker_contour_nm": Lc,
            "approx_PEG_or_CH2_units": round(Lc / PROJ_NM_PER_PEG),
            "effective_molarity_M": EM,
            "Kd_avidity_M": ag.kd_avidity(Kd1, Kd2, EM),
            "fusion_fraction_bound": round(f_fus, 4),
            "wildtype_fraction_bound": round(f_wt, 4),
            "fusion_vs_wildtype_window": round(win, 1),
        })

    # the linker that maximises the window within a synthesizable range (<= ~30 nm)
    best = max(rows, key=lambda r: r["fusion_vs_wildtype_window"])
    out = {
        "_note": ("Linker contour length -> ideal-chain effective molarity -> AND-gate "
                  "fusion-vs-wildtype selectivity window. CPU/stdlib. Arm affinities fixed "
                  "(Kd1=10 uM LBD, Kd2=100 uM EWS-LC) so EM is the only variable. EM is the "
                  "COINCIDENT-SITE (d~0) UPPER BOUND; a mobile disordered EWS-LC anchor "
                  "realises a lower EM, so windows here are optimistic ceilings."),
        "_inputs_are_illustrative": True,
        "_model": "EM = (3/(2*pi*Lc*b))^(3/2) * 1e24/NA ; b(Kuhn)=0.5 nm ; avidity Kd=Kd1*Kd2/EM",
        "fixed": {"Kd1_LBD_M": Kd1, "Kd2_EWS_M": Kd2, "free_ligand_M": L_dose,
                  "kuhn_length_nm": B_KUHN_NM},
        "by_linker": rows,
        "best_within_30nm": best,
        "design_reading": (
            "Shorter linkers give higher EM and a wider fusion-vs-WT window, but must still "
            "physically span from the LBD pocket to the EWS-LC anchor; longer linkers reach "
            "more easily but dilute EM and shrink the window. The physics confirms the "
            "avidity model's EM sweep is in a realistic range (~1e-2 to ~5e-1 M at the "
            "coincident-site bound), and that the realistic operating window is single-to-low-"
            "double-digit fold — a ceiling, not a guarantee, on a mobile IDR anchor."),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)
    print("linker -> EM -> window:")
    for r in rows:
        print(f"  Lc={r['linker_contour_nm']:>5} nm (~{r['approx_PEG_or_CH2_units']:>2} units) "
              f"-> EM={r['effective_molarity_M']:.2e} M -> window {r['fusion_vs_wildtype_window']}x "
              f"(fusion {r['fusion_fraction_bound']}, WT {r['wildtype_fraction_bound']})")
    print(f"\nbest within 30 nm: Lc={best['linker_contour_nm']} nm -> "
          f"{best['fusion_vs_wildtype_window']}x")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
