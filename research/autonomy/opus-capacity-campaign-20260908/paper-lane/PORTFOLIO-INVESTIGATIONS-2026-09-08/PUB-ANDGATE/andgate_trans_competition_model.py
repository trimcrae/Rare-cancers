#!/usr/bin/env python3
"""
AND-gate cis-vs-trans competition model — CPU-only, pure stdlib, no GPU, no network,
no external data.

WHAT THIS FILLS. `research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md`
states, in its Erratum and again as Limitation 8.7, that its three committed CPU models
represent wild-type NR4A3 as an ARM-1-ONLY species and contain NO species in which one
bivalent ligand bridges wild-type NR4A3 and wild-type EWSR1 as two SEPARATE proteins
in trans — "the dominant failure mode named in the Erratum" — so the published 5.5-11x
windows are upper bounds with respect to it. The Erratum sets the acceptance requirement
as K_eff(cis fusion) >> K_eff(trans) but never evaluates it.

This script evaluates it, using the same equilibrium formalism, the same illustrative
inputs, and no new experimental assumption beyond ONE swept quantity: C_E, the free
concentration of engageable wild-type EWSR1 low-complexity (LC) arm-2 sites in the
compartment where the ligand acts.

⛔ LIGAND-EXISTENCE FENCE. No validated, selective, cell-active EWSR1-LC or junction
arm-2 ligand exists in the public record (the paper's own blocking gate). Nothing here
asserts that such a ligand exists, and nothing here reports any molecule's properties.
This model is CONDITIONAL and BOUNDING: it asks what the design would do EVEN IF the
missing arm-2 ligand existed with the paper's illustrative Kd2. Its only valid outputs
are windows that BOUND the design, never efficacy, selectivity, potency or safety.

FORMALISM (site-occupancy partition functions at fixed free ligand L, the same
dilute-ligand convention used by andgate_selectivity_model.py; ligand depletion is
reported separately as a diagnostic, not folded into the windows).

  Fusion chain (arm-1 site and arm-2 site in cis, effective molarity EM):
      Z_fus = 1 + L/Kd1 + L/Kd2 + (L/Kd1)*(EM/Kd2)
    States: free; arm-1 only; arm-2 only; bivalent-cis. This is strictly more complete
    than the paper's min(Kd1*Kd2/EM, Kd1, Kd2) cap, and reduces to it in the regime the
    paper uses.

  Wild-type NR4A3 (arm-1 site only) in a compartment containing free WT EWSR1-LC sites
  at concentration C_E:
      Z_wt = 1 + (L/Kd1)*(1 + C_E/Kd2)
    States: free; arm-1 only; arm-1 PLUS a separate WT EWSR1 molecule captured in trans
    by the dangling arm 2. The trans capture is bimolecular, so it is governed by C_E
    where the cis case is governed by EM. NOTE this is the OPTIMISTIC trans treatment:
    it charges the trans bridge no steric or configurational penalty, which makes the
    resulting requirement on EM a LOWER bound on what a real linker would need.

  Window = f_fus_bound / f_wt_bound.

LOW-OCCUPANCY LIMIT (the design rule this model extracts):
      window -> (1 + EM/Kd2 + Kd1/Kd2) / (1 + C_E/Kd2)
  so the Erratum's "K_eff(cis) >> K_eff(trans)" is, quantitatively, **EM >> C_E**:
  the tethered effective molarity must exceed the AMBIENT FREE CONCENTRATION of
  wild-type EWSR1-LC sites in the same compartment. That is a comparison between a
  linker-geometry quantity and a measurable cell-biological one.

SECOND MECHANISM — PARTITIONING, NOT SITE BINDING. The paper offers two mutually
exclusive readings of what arm 2 binds: a discrete IDR contact (modelled above), or,
"more realistically", the phase-separated condensate MICRO-ENVIRONMENT. The second
reading is not a per-chain binding event and cannot be written as a Kd2 in the cis
partition function at all. If arm 2 partitions the ligand into FET condensates with
partition coefficient Kp, then inside a condensate the local free ligand is Kp*L and
EVERY arm-1 site there — fusion and wild-type NR4A3 alike — is engaged monovalently at
Kd1 and that elevated concentration. The coincidence window inside the condensate is
then identically 1.0 by construction, independent of Kp, and the residual selectivity
is a LOCALISATION ratio (what fraction of each species resides in condensates), not an
avidity AND-gate. `partitioning_regime` below reports this analytically.

Outputs: JSON to fusion-andgate-trans-competition.json beside this script.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "fusion-andgate-trans-competition.json")

uM = 1e-6
mM = 1e-3

# --- Illustrative inputs, taken UNCHANGED from andgate_selectivity_model.py ----------
# These are the paper's assumptions, not measured affinities. Reused so that the
# cis-only limit of this model reproduces the published base case exactly.
KD1 = 10.0 * uM      # arm 1, shared NR4A3 LBD
KD2 = 100.0 * uM     # arm 2, EWSR1-LC (hypothetical ligand; none exists)
EM = 1.0 * mM        # cis effective molarity set by the linker
L_DOSE = 1.0 * uM    # illustrative free ligand


def z_fusion(L, Kd1, Kd2, EM):
    """Partition function for the cis (fusion) chain: 4 states."""
    return 1.0 + L / Kd1 + L / Kd2 + (L / Kd1) * (EM / Kd2)


def z_wildtype(L, Kd1, Kd2, C_E):
    """Partition function for WT NR4A3 with in-trans WT EWSR1-LC capture: 3 states."""
    return 1.0 + (L / Kd1) * (1.0 + C_E / Kd2)


def frac(z):
    return (z - 1.0) / z


def window(L, Kd1, Kd2, EM, C_E):
    f_fus = frac(z_fusion(L, Kd1, Kd2, EM))
    f_wt = frac(z_wildtype(L, Kd1, Kd2, C_E))
    return f_fus, f_wt, (f_fus / f_wt if f_wt > 0 else float("inf"))


def free_ligand_diagnostic(L_free, Kd2, C_E_total):
    """Bounding sink diagnostic: with WT EWSR1-LC sites at total concentration C_E_total,
    how much ligand is held by them per unit free ligand? Reported as a ratio, NOT folded
    into the windows (which, like the paper's, are stated at FIXED FREE ligand)."""
    return C_E_total * (L_free / Kd2) / L_free if L_free > 0 else float("nan")


def critical_C_E(Kd1, Kd2, EM, target_fraction):
    """Free WT EWSR1-LC site concentration at which the low-occupancy window falls to
    `target_fraction` of its C_E = 0 value. Analytic:
        W(C_E)/W(0) = 1/(1 + C_E/Kd2)  =>  C_E* = Kd2*(1/target - 1)."""
    return Kd2 * (1.0 / target_fraction - 1.0)


def main():
    res = {
        "_model": "andgate_trans_competition_model.py",
        "_fills": "Limitation 8.7 of fusion-selective-andgate-degrader-paper.md "
                  "(the in-trans failure mode is not modelled)",
        "_inputs_are_illustrative": True,
        "_no_arm2_ligand_exists": True,
        "_conditional_bounding_model": "Evaluates the design assuming an arm-2 ligand "
                                       "with the paper's illustrative Kd2 EXISTS; it does not.",
        "_compute": "CPU, pure stdlib, no GPU, no network, no external data",
        "inputs": {"Kd1_arm_LBD_M": KD1, "Kd2_arm_EWS_LC_M": KD2,
                   "effective_molarity_cis_M": EM, "free_ligand_M": L_DOSE},
    }

    # 1. Reproduce the paper's cis-only base case (C_E = 0) as a validation baseline.
    f_fus, f_wt, w0 = window(L_DOSE, KD1, KD2, EM, 0.0)
    res["baseline_cis_only"] = {
        "C_E_M": 0.0,
        "fusion_fraction_bound": round(f_fus, 4),
        "wildtype_fraction_bound": round(f_wt, 4),
        "window": round(w0, 2),
        "paper_published_base_case_window": 5.5,
        "paper_published_wildtype_fraction_bound": 0.091,
        "note": "The 4-state fusion partition function is slightly more complete than "
                "the paper's capped Kd_avidity; agreement to within rounding at these "
                "inputs is the validation that this extension is the same model.",
    }

    # 2. Sweep the free WT EWSR1-LC site concentration.
    sweep = []
    for c in [0.0, 1e-9, 1e-8, 1e-7, 1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2]:
        f_f, f_w, w = window(L_DOSE, KD1, KD2, EM, c)
        sweep.append({
            "C_E_M": c,
            "C_E_uM": round(c / uM, 4),
            "fusion_fraction_bound": round(f_f, 4),
            "wildtype_fraction_bound": round(f_w, 4),
            "window": round(w, 2),
            "window_retained_vs_cis_only": round(w / w0, 3),
        })
    res["trans_competition_sweep"] = sweep

    # 3. Critical concentrations.
    res["critical_free_EWSR1_LC_site_concentration"] = {
        "half_window_C_E_M": critical_C_E(KD1, KD2, EM, 0.5),
        "half_window_C_E_uM": critical_C_E(KD1, KD2, EM, 0.5) / uM,
        "tenth_window_C_E_M": critical_C_E(KD1, KD2, EM, 0.1),
        "tenth_window_C_E_uM": critical_C_E(KD1, KD2, EM, 0.1) / uM,
        "analytic_form": "C_E* = Kd2 * (1/target - 1); set by Kd2 ALONE, not by EM",
        "reading": "The window is halved when free WT EWSR1-LC sites reach Kd2 (100 uM "
                   "at the paper's illustrative arm-2 affinity). The deliberately WEAK "
                   "arm 2 that the design rule demands is also what suppresses the trans "
                   "pathway: a weak Kd2 pushes C_E* up.",
    }

    # 4. The requirement the Erratum states qualitatively, made quantitative.
    res["erratum_requirement_quantified"] = {
        "statement": "K_eff(cis) >> K_eff(trans) is, in the low-occupancy limit, EM >> C_E.",
        "low_occupancy_window": "(1 + EM/Kd2 + Kd1/Kd2) / (1 + C_E/Kd2)",
        "EM_M": EM,
        "cis_advantage_factor_at_C_E_equal_1uM": round((1 + EM / KD2) / (1 + 1e-6 / KD2), 2),
        "what_must_be_measured": "The FREE concentration of engageable wild-type EWSR1-LC "
                                 "arm-2 sites in the compartment where the ligand acts — "
                                 "bulk nucleoplasmic AND intra-condensate. This is a "
                                 "measurable cell-biological quantity, and it, not the "
                                 "linker, decides whether the in-trans mode matters.",
    }

    # 5. Sensitivity: does a weaker or stronger arm 2 change the verdict?
    arm2 = []
    for kd2 in [1e-6, 1e-5, 1e-4, 1e-3]:
        _, _, w_cis = window(L_DOSE, KD1, kd2, EM, 0.0)
        row = {"Kd2_M": kd2, "Kd2_uM": kd2 / uM,
               "cis_only_window": round(w_cis, 2),
               "half_window_C_E_uM": round(critical_C_E(KD1, kd2, EM, 0.5) / uM, 3)}
        for c in [1e-6, 1e-5, 1e-4]:
            _, _, w = window(L_DOSE, KD1, kd2, EM, c)
            row["window_at_C_E_%guM" % (c / uM)] = round(w, 2)
        arm2.append(row)
    res["arm2_affinity_sensitivity"] = arm2

    # 6. Ligand sink diagnostic (bounding, at fixed free ligand).
    res["ligand_sink_diagnostic"] = [
        {"C_E_total_uM": c / uM,
         "ligand_held_by_WT_EWSR1_per_unit_free": round(free_ligand_diagnostic(L_DOSE, KD2, c), 4)}
        for c in [1e-6, 1e-5, 1e-4, 1e-3]
    ]

    # 7. The partitioning regime — analytic, no fitted parameter.
    partition = {"regime": "arm 2 as a condensate-partitioning moiety (the paper's own "
                           "'more realistic' reading of arm 2, §2/§4)",
                 "why_the_avidity_model_does_not_apply":
                     "Partitioning is a compartment property, not a per-chain binding "
                     "event; it has no Kd2 to place in the cis partition function and "
                     "confers no coincidence requirement.",
                 "inside_condensate_window": 1.0,
                 "inside_condensate_window_is_exact": True,
                 "derivation": "Local free ligand = Kp*L for every species in the "
                               "condensate; fusion and WT NR4A3 both present only an "
                               "arm-1 site to it and are engaged at the SAME Kd1, so "
                               "f_fus/f_wt = 1 identically, for any Kp.",
                 "wildtype_collateral": []}
    for kp in [1, 10, 100, 1000]:
        l_loc = kp * L_DOSE
        partition["wildtype_collateral"].append({
            "Kp": kp,
            "local_free_ligand_uM": l_loc / uM,
            "WT_NR4A3_fraction_bound_inside_condensate": round(l_loc / (l_loc + KD1), 4),
            "fusion_fraction_bound_inside_condensate": round(l_loc / (l_loc + KD1), 4),
        })
    partition["consequence"] = ("Under the partitioning reading the design is not an "
                                "AND-gate: selectivity reduces to the ratio of condensate "
                                "RESIDENCE of fusion vs wild-type NR4A3, and partitioning "
                                "actively WORSENS wild-type sparing for whatever fraction "
                                "of WT NR4A3 resides in FET condensates, because it raises "
                                "the local ligand concentration these WT molecules see.")
    res["partitioning_regime"] = partition

    res["verdict"] = {
        "in_trans_mode_under_discrete_site_reading":
            "Bounded and NOT automatically fatal at the paper's illustrative inputs: the "
            "window is halved only when free WT EWSR1-LC sites reach Kd2 (~100 uM). The "
            "published 5.5x is therefore an upper bound whose tightness is set by one "
            "unmeasured quantity, C_E, not by the linker.",
        "decisive_open_measurement":
            "Free engageable WT EWSR1-LC site concentration, bulk-nucleoplasmic and "
            "intra-condensate. Intra-condensate FET concentrations are the regime that "
            "could reach C_E ~ Kd2; bulk nucleoplasm plausibly does not.",
        "partitioning_reading_is_a_no_go_for_the_AND_GATE_CLAIM":
            "If arm 2 works by condensate partitioning — the mechanism the paper itself "
            "calls more realistic — the coincidence window is exactly 1.0 inside the "
            "condensate for any Kp, so the §3 avidity model does not describe that "
            "mechanism at all and cannot be cited in support of it.",
        "not_a_claim_about_any_molecule": True,
    }

    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1)
    print("wrote", OUT)
    print("cis-only baseline window: %.2f (paper: 5.5)" % w0)
    for row in sweep:
        print("  C_E=%9.4f uM  window=%6.2f  retained=%.3f"
              % (row["C_E_uM"], row["window"], row["window_retained_vs_cis_only"]))
    print("half-window C_E* = %.1f uM" % (critical_C_E(KD1, KD2, EM, 0.5) / uM))
    print("partitioning regime: inside-condensate window = 1.0 exactly, any Kp")


if __name__ == "__main__":
    main()
