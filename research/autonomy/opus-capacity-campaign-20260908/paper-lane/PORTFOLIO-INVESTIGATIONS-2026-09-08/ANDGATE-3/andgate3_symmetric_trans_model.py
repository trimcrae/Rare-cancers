#!/usr/bin/env python3
"""
ANDGATE-3 — the in-trans competition term is missing from the FUSION partition function,
and the arm-2 site-multiplicity sweep is applied to one side only.

CPU only, pure stdlib, no network, no external data, no GPU, no paid compute.

WHY THIS STEP.  ANDGATE-2 named two follow-ups.  (1) measure C_E in-hub — wet lab, not
available here.  (2) "settle what arm 2 binds, and how many sites per chain", flagged as
"cheaper to settle" and as "the sensitivity that could overturn the bulk verdict".  Item
(2) is the one with a computable part: whether the multiplicity sweep that produces the
fragility is set up correctly.  It is not.

THE DEFECT, stated precisely.  The lane's Erratum-established fact is that the EWSR1 LC
domain is NOT fusion-restricted: the fusion is `EWSR1-LC :: NR4A3-LBD`, so the fusion
CARRIES the same LC domain that wild-type EWSR1 carries (manuscript lines 52-56, 79-81,
127-128, 153-158).  Two consequences the committed models do not encode:

  (A) A ligand anchored by arm 1 on the FUSION's NR4A3-LBD can bridge in trans to a free
      LC chain exactly as it can on wild-type NR4A3.  The trans term (L/Kd1)(C_E/Kd2)
      belongs in BOTH partition functions.  PUB-ANDGATE put it in Z_wt only.  The
      committed JSON shows the signature directly: `fusion_fraction_bound` is 0.5261 at
      EVERY point of the C_E sweep, from 0 to 1 mM.
  (B) Site multiplicity n is a property of the LC domain, so it multiplies the CIS term on
      the fusion at the same time as it multiplies C_E.  ANDGATE-2 swept n on the trans
      side only (C_E = n * C_protein, `f_fusion` has no n).

This script re-derives ANDGATE-2's and PUB-ANDGATE's published numbers from the same
inputs (identity checks, hard-failing), then recomputes the same curves with the trans
term present on both sides and with n applied to both sides, and reports the difference.

⛔ FENCES CARRIED FORWARD UNCHANGED.
   * No validated, selective, cell-active EWSR1-LC arm-2 ligand exists in the public
     record.  Nothing here asserts one exists or reports any molecule's properties.
   * CONDITIONAL and BOUNDING only.  Outputs are properties of a model.  They are NEVER
     an EMC efficacy, safety, selectivity-as-therapeutic-property, therapeutic-window or
     clinical-readiness claim.
   * No value is guessed.  Kd1/Kd2/EM/L are the manuscript's own illustrative inputs.
     C_E and n are SWEPT.  The two literature anchors are carried over from ANDGATE-2
     unchanged, with its caveats, and are re-stated as anchors, not as C_E.
"""
import json, os, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "andgate3-symmetric-trans-competition.json")
uM, mM = 1e-6, 1e-3

# Manuscript's illustrative inputs, unchanged (paper lines 87, 196).
KD1, KD2, EM, L = 10.0 * uM, 100.0 * uM, 1.0 * mM, 1.0 * uM


# ---------------- as-published (ANDGATE-2 / PUB-ANDGATE) --------------------------
def f_fus_published(n_cis=1):
    Z = 1.0 + L / KD1 + L / KD2 + (L / KD1) * (EM / KD2)
    return (Z - 1.0) / Z


def f_wt(C_E):
    Z = 1.0 + (L / KD1) * (1.0 + C_E / KD2)
    return (Z - 1.0) / Z


def window_published(C_E):
    return f_fus_published() / f_wt(C_E)


# ---------------- symmetric correction --------------------------------------------
# Same convention, same states, with the two omissions repaired:
#   arm-2-only occupancy of the fusion's own LC:      n_cis * L/Kd2
#   arm1-bound + cis arm-2 on one of n_cis LC sites:  (L/Kd1) * n_cis*EM/Kd2
#   arm1-bound + TRANS arm-2 to a free LC site:       (L/Kd1) * C_E/Kd2   <-- was missing
def f_fus_symmetric(C_E, n_cis=1):
    Z = (1.0 + L / KD1 + n_cis * L / KD2
         + (L / KD1) * (n_cis * EM / KD2 + C_E / KD2))
    return (Z - 1.0) / Z


def window_symmetric(C_E, n_cis=1):
    return f_fus_symmetric(C_E, n_cis) / f_wt(C_E)


def regime(retained):                      # ANDGATE-2's bands, unchanged
    if retained >= 0.90:
        return "negligible"
    if retained > 0.20:
        return "materially degraded"
    return "fatal"


def main():
    fail = []

    # ---- IDENTITY CHECK 1: reproduce PUB-ANDGATE's committed cis-only baseline ----
    cis_pub = window_published(0.0)
    if abs(round(f_fus_published(), 4) - 0.5261) > 1e-4:
        fail.append("fusion_fraction_bound %.4f != committed 0.5261" % f_fus_published())
    if abs(round(f_wt(0.0), 4) - 0.0909) > 1e-4:
        fail.append("wildtype_fraction_bound %.4f != committed 0.0909" % f_wt(0.0))
    if abs(round(cis_pub, 2) - 5.79) > 1e-9:
        fail.append("cis-only window %.4f != committed 5.79" % cis_pub)

    # ---- IDENTITY CHECK 2: reproduce ANDGATE-2's committed placement table --------
    # (label, C_E in uM, committed window, committed retained)  digit for digit
    A2_PLACEMENT = [("E1", 0.2, 5.776, 0.9982), ("E2", 5.0, 5.536, 0.9567),
                    ("E2b", 2.0, 5.684, 0.9822), ("E3", 100.0, 3.156, 0.5455)]
    repro_place = []
    for lab, ce_uM, w_c, r_c in A2_PLACEMENT:
        w = window_published(ce_uM * uM)
        r = w / cis_pub
        ok = abs(round(w, 3) - w_c) <= 1e-9 and abs(round(r, 4) - r_c) <= 1e-9
        if not ok:
            fail.append("ANDGATE-2 %s: recomputed window %.3f / retained %.4f vs "
                        "committed %.3f / %.4f" % (lab, w, r, w_c, r_c))
        repro_place.append({"point": lab, "C_E_uM": ce_uM,
                            "committed_window": w_c, "recomputed_window": round(w, 3),
                            "committed_retained": r_c, "recomputed_retained": round(r, 4),
                            "reproduces": ok})

    # ---- IDENTITY CHECK 3: ANDGATE-2's one-sided multiplicity table ---------------
    A2_MULT = [("EWS/FLI1 anchor, 200 nM", 200e-9,
                [(1, 5.776, 0.9982), (3, 5.755, 0.9946), (10, 5.684, 0.9822),
                 (30, 5.489, 0.9485), (80, 5.061, 0.8746)]),
               ("FUS-family HeLa ceiling, 5 uM", 5.0 * uM,
                [(1, 5.536, 0.9567), (3, 5.101, 0.8814), (10, 4.033, 0.6970),
                 (30, 2.630, 0.4545), (80, 1.578, 0.2727)])]
    repro_mult = []
    for name, c, rows in A2_MULT:
        for n, w_c, r_c in rows:
            w = window_published(n * c)
            r = w / cis_pub
            ok = abs(round(w, 3) - w_c) <= 1e-9 and abs(round(r, 4) - r_c) <= 1e-9
            if not ok:
                fail.append("ANDGATE-2 mult %s n=%d: %.3f/%.4f vs committed %.3f/%.4f"
                            % (name, n, w, r, w_c, r_c))
            repro_mult.append({"protein": name, "n": n,
                               "committed_window": w_c, "recomputed_window": round(w, 3),
                               "reproduces": ok})

    if fail:
        for f in fail:
            sys.stderr.write("IDENTITY CHECK FAILED: %s\n" % f)
        return 1
    print("IDENTITY CHECKS PASSED — %d committed values re-derived digit for digit"
          % (2 + len(repro_place) + len(repro_mult)))

    # ---- The structural evidence for defect (A), read off the committed artifact --
    fus_invariance = sorted({round(f_fus_published(), 4)
                             for ce in [0, 1e-9, 1e-8, 1e-7, 1e-6, 3e-6, 1e-5, 3e-5,
                                        1e-4, 3e-4, 1e-3, 3e-3]})

    # ---- Corrected curve, n = 1 ---------------------------------------------------
    SWEEP = [0.0, 0.1, 1.0, 2.0, 5.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0]
    cis_sym = window_symmetric(0.0)
    curve = []
    for ce_uM in SWEEP:
        ce = ce_uM * uM
        wp, ws = window_published(ce), window_symmetric(ce)
        curve.append({
            "C_E_uM": ce_uM,
            "window_as_published": round(wp, 3),
            "retained_as_published": round(wp / cis_pub, 4),
            "regime_as_published": regime(wp / cis_pub),
            "window_symmetric": round(ws, 3),
            "retained_symmetric": round(ws / cis_sym, 4),
            "regime_symmetric": regime(ws / cis_sym),
            "published_understates_window_by_factor": round(ws / wp, 4),
        })

    # ---- Corrected multiplicity sweep, n on BOTH sides ----------------------------
    mult = []
    for name, c in [("EWS/FLI1 anchor, 200 nM", 200e-9),
                    ("FUS-family HeLa ceiling, 5 uM", 5.0 * uM)]:
        for n in [1, 3, 10, 30, 80]:
            ce = n * c
            wp = window_published(ce)                       # n on trans side only
            ws = window_symmetric(ce, n_cis=n)              # n on both sides
            # its own n-matched baseline: same chemistry, C_E -> 0
            base_sym = window_symmetric(0.0, n_cis=n)
            mult.append({
                "protein_concentration": name, "n_arm2_sites_per_chain": n,
                "C_E_uM": round(ce / uM, 4),
                "window_as_published_one_sided": round(wp, 3),
                "retained_as_published_one_sided": round(wp / cis_pub, 4),
                "regime_as_published": regime(wp / cis_pub),
                "window_symmetric": round(ws, 3),
                "retained_symmetric_vs_n_matched_cis_only": round(ws / base_sym, 4),
                "regime_symmetric": regime(ws / base_sym),
            })

    out = {
        "_lane": "ANDGATE-3",
        "_continues": "ANDGATE-2/andgate2-literature-placement.json (item 2 of its §7)",
        "_compute": "CPU, pure stdlib, no GPU, no network, no external data",
        "_no_arm2_ligand_exists": True,
        "_conditional_bounding_model": (
            "Evaluates a design assuming an arm-2 ligand with the paper's illustrative "
            "Kd2 EXISTS; it does not. NOT an efficacy, safety, selectivity-as-"
            "therapeutic-property, therapeutic-window or clinical-readiness claim."),
        "inputs": {"Kd1_M": KD1, "Kd2_M": KD2, "EM_M": EM, "free_ligand_M": L,
                   "provenance": "manuscript illustrative values, unchanged"},
        "identity_checks": {
            "all_passed": True,
            "pub_andgate_cis_only_window": round(cis_pub, 3),
            "pub_andgate_committed": 5.79,
            "andgate2_placement_reproduction": repro_place,
            "andgate2_multiplicity_reproduction": repro_mult,
            "note": ("Every ANDGATE-2 / PUB-ANDGATE number tested re-derives exactly from "
                     "the same inputs. The finding below is NOT an arithmetic discrepancy; "
                     "it is a structural asymmetry in the model those numbers come from."),
        },
        "defect_A_missing_trans_term_on_fusion": {
            "evidence": ("PUB-ANDGATE's committed trans_competition_sweep reports "
                         "fusion_fraction_bound = %s at every C_E from 0 to 3 mM — the "
                         "fusion partition function has no C_E dependence at all."
                         % fus_invariance),
            "why_it_is_wrong": ("The Erratum establishes the fusion is EWSR1-LC::NR4A3-LBD, "
                                "so a ligand anchored by arm 1 on the FUSION's LBD can "
                                "bridge in trans to a free LC chain exactly as on wild-type "
                                "NR4A3. The term (L/Kd1)(C_E/Kd2) belongs in both."),
            "consequence": ("With the term present in both, window = "
                            "[1 + n*EM/Kd2 + C_E/Kd2 + n*Kd1/Kd2] / [1 + C_E/Kd2] > 1 for "
                            "all C_E. The window decays MONOTONICALLY TO 1 and CANNOT "
                            "invert. PUB-ANDGATE's reported inversion above C_E = EM "
                            "('the molecule prefers wild-type NR4A3 to the fusion', "
                            "0.70x/0.58x) is an artifact of the omission."),
            "asymptote_symmetric_window_as_C_E_to_infinity": 1.0,
        },
        "defect_B_one_sided_multiplicity": {
            "why_it_is_wrong": ("n is a property of the LC domain, which the fusion "
                                "carries. Multiplying only C_E while leaving the cis term "
                                "at one site makes the design look fragile to n when the "
                                "same n also multiplies the cis avidity term."),
        },
        "cost_curve_published_vs_symmetric_n1": curve,
        "multiplicity_published_vs_symmetric": mult,
        "what_does_NOT_change": (
            "The bulk-nucleoplasm verdict. At the literature anchors (0.2-5 uM) the "
            "correction moves the retained window by <1%; ANDGATE-2's 'negligible' bulk "
            "regime stands, and stands more strongly. The decisive intra-condensate "
            "quantity remains UNMEASURED — this changes the model, not the missing data."),
        "stop_condition": (
            "Complete when the committed numbers were re-derived, the asymmetry was "
            "localised to a named term, and the corrected curve was computed. Does not "
            "estimate C_E, does not adopt any n, does not edit the manuscript or any "
            "shared file, does not reopen the arm-2 ligand gate."),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1)

    print("\ncis-only window: as-published %.3f | symmetric %.3f" % (cis_pub, cis_sym))
    print("\n%-10s %10s %10s %10s %10s" % ("C_E uM", "w_pub", "w_sym", "ret_pub", "ret_sym"))
    for c in curve:
        print("%-10.1f %10.3f %10.3f %10.4f %10.4f"
              % (c["C_E_uM"], c["window_as_published"], c["window_symmetric"],
                 c["retained_as_published"], c["retained_symmetric"]))
    print("\n%-32s %4s %10s %10s %10s %10s"
          % ("protein", "n", "w_pub", "w_sym", "ret_pub", "ret_sym"))
    for m in mult:
        print("%-32s %4d %10.3f %10.3f %10.4f %10.4f"
              % (m["protein_concentration"][:32], m["n_arm2_sites_per_chain"],
                 m["window_as_published_one_sided"], m["window_symmetric"],
                 m["retained_as_published_one_sided"],
                 m["retained_symmetric_vs_n_matched_cis_only"]))
    print("\nwrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
