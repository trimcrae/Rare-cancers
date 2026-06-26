#!/usr/bin/env python3
"""
Coincidence-detection (AND-gate) selectivity model for a FUSION-SELECTIVE bivalent
NR4A3 degrader — CPU-only, pure stdlib, no GPU/AWS, no external data.

QUESTION it answers (quantitatively): can a bivalent ligand whose two arms are each
INDIVIDUALLY too weak to matter become FUSION-selective by avidity — engaging the
EWSR1::NR4A3 fusion (which presents BOTH binding features on one chain) while sparing
wild-type NR4A3 (which presents only one)?

The design (see fusion-selective-andgate-degrader-paper.md):
  - Arm 1 binds the NR4A3 ligand-binding domain (LBD) — present in BOTH the fusion AND
    wild-type NR4A3 (the LBD is retained intact in the fusion), dissociation const Kd1.
  - Arm 2 binds a FUSION-RESTRICTED feature — the EWSR1 low-complexity/transactivation
    domain (or its condensate micro-environment), present ONLY in the fusion, Kd2.
  Wild-type NR4A3 has no arm-2 partner, so on WT only arm 1 can engage (monovalent).
  The fusion is engaged BIVALENTLY: once one arm binds, the second arm's effective
  concentration is the effective molarity (EM, c_eff), giving the standard avidity
  relation  Kd_avidity ~ Kd1*Kd2 / EM  (valid when EM >> Kd2).

Selectivity window = (fraction of fusion bound) / (fraction of wild-type NR4A3 bound)
at a given free ligand concentration [L].

IMPORTANT — all Kd/EM values below are ILLUSTRATIVE ASSUMPTIONS, not measured affinities.
This is a biophysical model of the DESIGN PRINCIPLE, parameterised to plausible ranges
from the bivalent/PROTAC/avidity literature. It does not assert any real compound's
affinity. Output JSON carries `_inputs_are_illustrative: true`.
"""
import json
import math
import os

OUT = os.path.join(os.path.dirname(__file__), "fusion-andgate-selectivity-model.json")


def frac_bound_monovalent(L, Kd):
    """Equilibrium fraction of receptor bound by a monovalent ligand at free conc L."""
    return L / (L + Kd)


def kd_avidity(Kd1, Kd2, EM):
    """Apparent bivalent dissociation constant via the effective-molarity avidity model.
    Kd_avidity ~ Kd1*Kd2/EM. Capped at min(Kd1,Kd2) (avidity cannot make binding weaker
    than the better single arm)."""
    kd = Kd1 * Kd2 / EM
    return min(kd, Kd1, Kd2)


def frac_bound_fusion(L, Kd1, Kd2, EM):
    """Fusion engaged bivalently: occupancy set by the avidity-enhanced Kd."""
    return frac_bound_monovalent(L, kd_avidity(Kd1, Kd2, EM))


def selectivity_window(L, Kd1, Kd2, EM):
    """Fusion-bound / wild-type-bound at free ligand L (WT sees only arm 1, Kd1)."""
    f_fus = frac_bound_fusion(L, Kd1, Kd2, EM)
    f_wt = frac_bound_monovalent(L, Kd1)          # WT: arm-1 only, monovalent
    return f_fus, f_wt, (f_fus / f_wt if f_wt > 0 else float("inf"))


def main():
    uM = 1e-6  # work in molar

    # --- Illustrative parameter set (clearly labelled assumptions) -------------------
    # Each arm is DELIBERATELY weak alone so it cannot meaningfully engage WT NR4A3.
    Kd1 = 10.0 * uM     # arm-1 (LBD warhead), weak: spares WT NR4A3 as a monovalent binder
    Kd2 = 100.0 * uM    # arm-2 (EWS-LC / condensate anchor), very weak IDR-type contact
    EM = 1.0e-3         # effective molarity 1 mM (typical tethered-ligand range 1e-4..1e-1 M)
    L_dose = 1.0 * uM   # an illustrative free intracellular ligand concentration

    base = {
        "Kd1_arm_LBD_M": Kd1, "Kd2_arm_EWS_M": Kd2, "effective_molarity_M": EM,
        "free_ligand_M": L_dose,
        "Kd_avidity_fusion_M": kd_avidity(Kd1, Kd2, EM),
    }
    f_fus, f_wt, win = selectivity_window(L_dose, Kd1, Kd2, EM)
    base.update({
        "fusion_fraction_bound": round(f_fus, 4),
        "wildtype_fraction_bound": round(f_wt, 4),
        "fusion_vs_wildtype_window": round(win, 1),
        "interpretation": (
            "With each arm individually weak (Kd1=10 uM, Kd2=100 uM), wild-type NR4A3 — "
            "seen only monovalently by arm 1 — stays largely unbound, while the fusion is "
            "engaged with avidity-enhanced Kd_avidity = Kd1*Kd2/EM, giving a large "
            "fusion-vs-wildtype occupancy window. The window is a BINDING window; "
            "degradation selectivity additionally depends on the ternary complex."),
    })

    # --- Sensitivity sweep over effective molarity (the key tunable) -----------------
    em_sweep = []
    for EM_i in (1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1):
        f_fus, f_wt, win = selectivity_window(L_dose, Kd1, Kd2, EM_i)
        em_sweep.append({
            "effective_molarity_M": EM_i,
            "Kd_avidity_M": kd_avidity(Kd1, Kd2, EM_i),
            "fusion_fraction_bound": round(f_fus, 4),
            "wildtype_fraction_bound": round(f_wt, 4),
            "window": round(win, 1),
        })

    # --- Sensitivity sweep over arm-1 strength (how weak must the LBD arm be?) --------
    kd1_sweep = []
    for Kd1_i_uM in (1.0, 3.0, 10.0, 30.0, 100.0):
        Kd1_i = Kd1_i_uM * uM
        f_fus, f_wt, win = selectivity_window(L_dose, Kd1_i, Kd2, EM)
        kd1_sweep.append({
            "Kd1_arm_LBD_uM": Kd1_i_uM,
            "wildtype_fraction_bound": round(f_wt, 4),
            "fusion_fraction_bound": round(f_fus, 4),
            "window": round(win, 1),
        })

    out = {
        "_note": ("Coincidence-detection (AND-gate) avidity model for a fusion-selective "
                  "bivalent NR4A3 degrader. CPU/stdlib only. Design prep, not a real "
                  "compound; all Kd/EM are illustrative assumptions."),
        "_inputs_are_illustrative": True,
        "_model": "Kd_avidity ~ Kd1*Kd2/EM (effective-molarity avidity); WT engaged "
                  "monovalently by arm 1 only; window = f_fusion / f_wildtype.",
        "base_case": base,
        "sweep_effective_molarity": em_sweep,
        "sweep_arm1_affinity": kd1_sweep,
        "design_rule": (
            "Pick BOTH arms individually too weak to occupy wild-type NR4A3 at the dosed "
            "concentration; rely on avidity (EM) to engage only the fusion, which uniquely "
            "presents both features on one chain. Larger EM (shorter/optimised linker) and "
            "weaker single arms widen the fusion-vs-WT window — at the cost of needing "
            "higher total dose."),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)
    print("base case:", json.dumps(base, indent=2))
    print("\nEM sweep:")
    for r in em_sweep:
        print(f"  EM={r['effective_molarity_M']:.0e} M -> window {r['window']}x "
              f"(fusion {r['fusion_fraction_bound']}, WT {r['wildtype_fraction_bound']})")
    print("\narm-1 sweep:")
    for r in kd1_sweep:
        print(f"  Kd1={r['Kd1_arm_LBD_uM']:>5} uM -> window {r['window']}x "
              f"(WT bound {r['wildtype_fraction_bound']})")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
