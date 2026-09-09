#!/usr/bin/env python3
"""
ANDGATE-4 — INDEPENDENT re-derivation of the ANDGATE-3 symmetric-trans result.

Written from the ALGEBRA as stated in the two parent FINDING.md files and the
manuscript's illustrative inputs. It deliberately does NOT import, exec or read
either parent script: the point is to check them, not to re-run them.

CPU only, pure stdlib, no network, no external data, no GPU, no sampling, no docking,
no structure prediction, no paid API.

FENCE. No validated, selective, cell-active EWSR1-LC arm-2 ligand exists in the public
record. Every number below is a property of a MODEL under the manuscript's own
illustrative assumptions. Nothing here is an EMC efficacy, safety,
selectivity-as-therapeutic-property, therapeutic-window or clinical-readiness claim.

TWO PARTITION FUNCTIONS UNDER TEST
----------------------------------
ASYMMETRIC (as committed in PUB-ANDGATE / inherited by ANDGATE-2):
    Z_fus = 1 + L/Kd1 + L/Kd2 + (L/Kd1)(EM/Kd2)            <- no C_E anywhere
    Z_wt  = 1 + (L/Kd1)(1 + C_E/Kd2)

SYMMETRIC (ANDGATE-3's repair; the fusion is EWSR1-LC :: NR4A3-LBD, so a ligand
anchored by arm 1 on the fusion's LBD can ALSO bridge in trans to a free LC chain):
    Z_fus = 1 + L/Kd1 + n*L/Kd2 + (L/Kd1)( n*EM/Kd2 + C_E/Kd2 )
    Z_wt  = 1 +                   (L/Kd1)( 1        + C_E/Kd2 )

Occupied fraction f = (Z - 1)/Z ; window = f_fus / f_wt.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "andgate4-independent-rederivation.json")

uM = 1e-6
mM = 1e-3

# Manuscript's own illustrative values (unchanged; assumptions, not measured affinities)
KD1 = 10.0 * uM
KD2 = 100.0 * uM
EM = 1.0 * mM
L = 1.0 * uM


def f_occ(z):
    return (z - 1.0) / z


def z_fus_asym(L, Kd1, Kd2, EM, n=1):
    return 1.0 + L / Kd1 + n * L / Kd2 + (L / Kd1) * (n * EM / Kd2)


def z_fus_sym(L, Kd1, Kd2, EM, C_E, n=1):
    return 1.0 + L / Kd1 + n * L / Kd2 + (L / Kd1) * (n * EM / Kd2 + C_E / Kd2)


def z_wt(L, Kd1, Kd2, C_E):
    return 1.0 + (L / Kd1) * (1.0 + C_E / Kd2)


def win_asym(C_E, n=1):
    return f_occ(z_fus_asym(L, KD1, KD2, EM, n)) / f_occ(z_wt(L, KD1, KD2, C_E))


def win_sym(C_E, n=1):
    return f_occ(z_fus_sym(L, KD1, KD2, EM, C_E, n)) / f_occ(z_wt(L, KD1, KD2, C_E))


CHECKS = []
FAILED = []


def expect(label, got, want, tol):
    ok = abs(got - want) <= tol
    CHECKS.append({"check": label, "got": round(got, 6), "expected": want,
                   "tol": tol, "pass": ok})
    if not ok:
        FAILED.append(label)
    return ok


def main():
    res = {
        "_model": "andgate4_independent_rederivation.py",
        "_lane": "ANDGATE-4",
        "_purpose": "Independent re-derivation of ANDGATE-3's asymmetric vs symmetric "
                    "in-trans window values, from the algebra, without importing the "
                    "parent scripts.",
        "_compute": "CPU, pure stdlib, no GPU, no network, no external data",
        "_no_arm2_ligand_exists": True,
        "_not_an_efficacy_safety_or_therapeutic_claim": True,
        "inputs": {"Kd1_M": KD1, "Kd2_M": KD2, "EM_M": EM, "free_ligand_M": L},
    }

    # ---- 1. The committed asymmetric base case (PUB-ANDGATE) -----------------------
    ff0 = f_occ(z_fus_asym(L, KD1, KD2, EM))
    fw0 = f_occ(z_wt(L, KD1, KD2, 0.0))
    expect("PUB-ANDGATE fusion_fraction_bound @C_E=0 == 0.5261", ff0, 0.5261, 5e-5)
    expect("PUB-ANDGATE wildtype_fraction_bound @C_E=0 == 0.0909", fw0, 0.0909, 5e-5)
    expect("PUB-ANDGATE cis-only window == 5.79", ff0 / fw0, 5.79, 5e-3)

    # ---- 2. The two disputed asymmetric values above EM ----------------------------
    w_asym_3mM = win_asym(3 * mM)
    w_asym_10mM = win_asym(10 * mM)
    expect("ASYMMETRIC window @C_E=3 mM == 0.700", w_asym_3mM, 0.700, 5e-4)
    expect("ASYMMETRIC window @C_E=10 mM == 0.580", w_asym_10mM, 0.580, 5e-4)

    # C_E-independence of the asymmetric fusion term (the structural defect itself)
    fus_asym_all = sorted({round(f_occ(z_fus_asym(L, KD1, KD2, EM)), 4)
                           for _ in range(13)})
    res["asymmetric_fusion_fraction_is_C_E_independent"] = {
        "distinct_values_over_13_sweep_points": fus_asym_all,
        "note": "z_fus_asym takes no C_E argument, so the fusion occupancy is constant "
                "at 0.5261 across the whole sweep — the defect, reproduced.",
    }

    # ---- 3. The symmetric replacements --------------------------------------------
    w_sym_3mM = win_sym(3 * mM)
    w_sym_10mM = win_sym(10 * mM)
    expect("SYMMETRIC window @C_E=3 mM == 1.064", w_sym_3mM, 1.064, 5e-4)
    expect("SYMMETRIC window @C_E=10 mM == 1.008", w_sym_10mM, 1.008, 5e-4)

    # ---- 4. Monotonic decay to 1, never below ------------------------------------
    grid = [0.0, 1e-9, 1e-8, 1e-7, 1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4,
            1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 1.0, 10.0]
    sweep = []
    prev = None
    monotone = True
    all_above_one = True
    for c in grid:
        wa = win_asym(c)
        ws = win_sym(c)
        if ws < 1.0:
            all_above_one = False
        if prev is not None and ws > prev + 1e-12:
            monotone = False
        prev = ws
        sweep.append({"C_E_M": c, "C_E_uM": c / uM,
                      "window_asymmetric": round(wa, 4),
                      "window_symmetric": round(ws, 4)})
    res["sweep"] = sweep
    CHECKS.append({"check": "SYMMETRIC window monotonically non-increasing in C_E",
                   "got": monotone, "expected": True, "tol": 0, "pass": monotone})
    if not monotone:
        FAILED.append("monotonicity")
    CHECKS.append({"check": "SYMMETRIC window > 1 at every swept C_E (no inversion)",
                   "got": all_above_one, "expected": True, "tol": 0,
                   "pass": all_above_one})
    if not all_above_one:
        FAILED.append("no-inversion")

    # Asymptote: limit as C_E -> infinity is exactly 1.
    ws_huge = win_sym(1e6)
    expect("SYMMETRIC window -> 1 as C_E -> inf", ws_huge, 1.0, 1e-3)
    # And the asymmetric one goes to 0, which is what manufactured the 'inversion'.
    res["asymmetric_limit_C_E_to_inf"] = round(win_asym(1e6), 6)

    # Algebraic identity: low-occupancy symmetric window
    def w_lowocc(C_E, n=1):
        return (1 + n * EM / KD2 + C_E / KD2 + n * KD1 / KD2) / (1 + C_E / KD2)
    res["low_occupancy_form_check"] = [
        {"C_E_M": c, "exact": round(win_sym(c), 4), "low_occupancy": round(w_lowocc(c), 4)}
        for c in [1e-6, 1e-4, 1e-2]
    ]
    # numerator > denominator for all C_E >= 0  <=>  n*EM/Kd2 + n*Kd1/Kd2 > 0. Always.
    res["why_no_inversion_is_possible"] = (
        "Symmetric low-occupancy window = (1 + n*EM/Kd2 + C_E/Kd2 + n*Kd1/Kd2)/(1 + C_E/Kd2). "
        "The numerator exceeds the denominator by n*(EM+Kd1)/Kd2 > 0 for every C_E, so the "
        "window is > 1 everywhere and decays monotonically to 1. The C_E/Kd2 trans term is "
        "common to both chains; omitting it from the fusion alone is what drove the ratio "
        "below 1."
    )

    # ---- 5. ANDGATE-3's honest negative: n does NOT rescue multiplicity fragility ---
    # Retained fraction = window(n, C_E) / window(n, C_E=0)  -- n-matched baseline.
    C_ANCHOR = 200e-9 * 10  # 200 nM protein x n=10 sites = 2 uM of arm-2 sites
    n = 10
    ret_asym = win_asym(C_ANCHOR, n) / win_asym(0.0, n)
    ret_sym = win_sym(C_ANCHOR, n) / win_sym(0.0, n)
    res["multiplicity_negative_n10_200nM_anchor"] = {
        "n": n,
        "C_E_M": C_ANCHOR,
        "window_asymmetric": round(win_asym(C_ANCHOR, n), 4),
        "window_symmetric": round(win_sym(C_ANCHOR, n), 4),
        "retained_fraction_asymmetric_vs_n_matched_baseline": round(ret_asym, 4),
        "retained_fraction_symmetric_vs_n_matched_baseline": round(ret_sym, 4),
        "verdict": "Against an n-matched cis-only baseline the retained fraction is "
                   "unchanged to 4 dp. Symmetric n does NOT rescue the multiplicity "
                   "fragility ANDGATE-2 found; it changes the absolute window, not the "
                   "shape of the decay. Carried forward UNSOFTENED.",
    }
    expect("retained fraction asymmetric (n=10 anchor) == 0.9822", ret_asym, 0.9822, 5e-4)
    expect("retained fraction symmetric  (n=10 anchor) == 0.9822", ret_sym, 0.9822, 5e-4)

    res["checks"] = CHECKS
    res["all_checks_passed"] = not FAILED
    res["failed_checks"] = FAILED

    res["bulk_verdict_carried_forward"] = (
        "UNCHANGED. At the bulk-nucleoplasmic literature anchors the correction moves the "
        "retained window by well under 1%. The verdict still rests entirely on in-hub C_E, "
        "the free concentration of engageable wild-type EWSR1-LC arm-2 sites, which remains "
        "UNKNOWN in this repository — not zero."
    )

    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=2)

    for c in CHECKS:
        print("%-70s got=%-12s want=%-8s %s"
              % (c["check"], c["got"], c["expected"], "PASS" if c["pass"] else "FAIL"))
    print()
    print("asymmetric window C_E->inf : %.6f  (drives the spurious 'inversion')"
          % win_asym(1e6))
    print("symmetric  window C_E->inf : %.6f  (asymptotes to unity)" % ws_huge)
    print()
    print("wrote", OUT)
    if FAILED:
        print("FAILED:", FAILED, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
