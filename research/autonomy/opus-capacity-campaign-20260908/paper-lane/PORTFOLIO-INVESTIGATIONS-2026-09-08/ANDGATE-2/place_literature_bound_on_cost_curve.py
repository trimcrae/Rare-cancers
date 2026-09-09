#!/usr/bin/env python3
"""
ANDGATE-2 — place the LITERATURE-RETRIEVED concentration evidence on the PUB-ANDGATE
in-trans cost curve.  CPU only, pure stdlib, no network, no external data, no GPU.

WHAT THIS DOES.  The completed PUB-ANDGATE lane showed that the AND-gate window
collapses as a function of ONE unmeasured quantity, C_E = the free concentration of
engageable wild-type EWSR1 low-complexity (LC) arm-2 sites in the compartment where the
ligand acts, with the half-window point analytic at C_E* = Kd2.  It stopped there and
did not attempt to measure or estimate C_E.  This script takes the numbers actually
retrieved from the published literature via the PubMed/PMC route (see
CONCENTRATION-EVIDENCE.md in this directory for per-source provenance and every
conversion assumption) and evaluates the SAME window function at those values.

⛔ FENCES CARRIED FORWARD UNCHANGED FROM THE PARENT LANE.
   * No validated, selective, cell-active EWSR1-LC arm-2 ligand exists in the public
     record.  Nothing here asserts one exists or reports any molecule's properties.
   * The model is CONDITIONAL and BOUNDING.  Its only valid outputs are windows that
     bound a design; never efficacy, selectivity, potency, safety or clinical readiness.
   * NO VALUE IS GUESSED.  Every C_E entered below is either (a) a published measurement
     with its source and its exact measured quantity named, or (b) an explicitly labelled
     scenario/sensitivity point that is swept, not asserted.  Where the measured species
     is not wild-type EWSR1, or the compartment is not the one the design acts in, the
     record says so in the `caveat` field and the result is reported as an anchor, not
     as the parameter.

FORMALISM — identical to ../PUB-ANDGATE/andgate_trans_competition_model.py:
    Z_fus = 1 + L/Kd1 + L/Kd2 + (L/Kd1)*(EM/Kd2)
    Z_wt  = 1 + (L/Kd1)*(1 + C_E/Kd2)
    window = f_fus_bound / f_wt_bound
Inputs Kd1/Kd2/EM/L are the paper's own illustrative values, unchanged, so this script's
C_E = 0 point must reproduce the parent lane's 5.79x cis-only baseline.  That identity
is asserted below and the script exits non-zero if it fails.
"""
import json
import os
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "andgate2-literature-placement.json")

uM = 1e-6
mM = 1e-3

# Paper's illustrative inputs, copied unchanged from andgate_selectivity_model.py
# via ../PUB-ANDGATE/andgate_trans_competition_model.py.  Assumptions, not measurements.
KD1 = 10.0 * uM      # arm 1, shared NR4A3 ligand-binding domain
KD2 = 100.0 * uM     # arm 2, EWSR1 low-complexity domain
EM = 1.0 * mM        # effective molarity of the cis (tethered) arm-2 engagement
L = 1.0 * uM         # free ligand


def f_fusion(L=L, Kd1=KD1, Kd2=KD2, EM=EM):
    Z = 1.0 + L / Kd1 + L / Kd2 + (L / Kd1) * (EM / Kd2)
    return (Z - 1.0) / Z


def f_wildtype(C_E, L=L, Kd1=KD1, Kd2=KD2):
    Z = 1.0 + (L / Kd1) * (1.0 + C_E / Kd2)
    return (Z - 1.0) / Z


def window(C_E):
    return f_fusion() / f_wildtype(C_E)


CIS_ONLY = window(0.0)

# --- Regime thresholds, stated ONCE and applied mechanically ------------------------
# These are the reporting bands the task asked for.  They are a presentation choice,
# declared here so no result is silently reclassified.
def regime(retained):
    if retained >= 0.90:
        return "negligible"
    if retained > 0.20:
        return "materially degraded"
    return "fatal"


# --- The evidence, as retrieved.  See CONCENTRATION-EVIDENCE.md ---------------------
# Every entry names the EXACT measured quantity and every step needed to turn it into a
# C_E.  `is_measurement_of_C_E` is False for every one of them: none of these papers
# measured the free engageable wild-type EWSR1-LC arm-2 site concentration.
EVIDENCE = [
    {
        "label": "E1 bulk nucleoplasm — endogenous EWS/FLI1, A673 Ewing sarcoma",
        "C_E_M": 200e-9,
        "source": "Chong et al. 2018, Science 361:eaar2555 (PMID 29930090, PMC6961784, "
                  "doi:10.1126/science.aar2555)",
        "measured_quantity": "intranuclear concentration of endogenously Halo-tagged "
                             "EWS/FLI1 in A673 cells, ~200 nM, by fluorescence "
                             "correlation spectroscopy and fluorescence-intensity "
                             "calibration against purified fluorophore standards in "
                             "live cells",
        "conversion_assumptions": [
            "NONE for concentration: this is a direct in-cell concentration, not a copy "
            "number, so no nuclear volume and no copy-number-to-molarity conversion is "
            "applied.",
            "One EWSR1-LC arm-2 site per protein chain (n_sites = 1); the multiplicity "
            "sensitivity is swept separately below.",
            "All of it free and engageable — an upper bound, since chromatin-bound, "
            "RNA-bound, complexed and self-associated LC is not engageable.",
        ],
        "caveat": "This is the FUSION protein EWS/FLI1, which carries the EWSR1 LC, NOT "
                  "wild-type EWSR1. Wild-type EWSR1 is a different species at an "
                  "unmeasured (plausibly higher) abundance. Used as an order-of-magnitude "
                  "ANCHOR for a FET-LC-bearing protein in the disease-relevant cell line, "
                  "not as a measurement of C_E.",
        "is_measurement_of_C_E": False,
    },
    {
        "label": "E2 bulk nucleoplasm — FUS-family upper statement, HeLa",
        "C_E_M": 5.0 * uM,
        "source": "Wang et al. 2018, Cell 174:688 (PMID 29961577, PMC6063760, "
                  "doi:10.1016/j.cell.2018.06.006)",
        "measured_quantity": "the authors state that 5 uM 'in most cases ... lies above "
                             "the physiological concentration in HeLa cells' of the 22 "
                             "FUS-family proteins they assayed (a cited-literature "
                             "statement in that paper, not a new measurement in it)",
        "conversion_assumptions": [
            "Read as a cellular-concentration UPPER BOUND for most FUS-family members "
            "including the FET proteins; the paper does not give a per-protein EWSR1 value.",
            "Cellular concentration taken as nucleoplasmic concentration — assumes EWSR1 "
            "is predominantly nuclear and uniformly distributed within the nucleus. The "
            "second half of that assumption is exactly what condensate formation violates.",
            "One arm-2 site per chain; all free and engageable.",
        ],
        "caveat": "A family-level statement, not an EWSR1 number, and HeLa is not a "
                  "fusion-bearing cell. Used as a bulk-regime CEILING.",
        "is_measurement_of_C_E": False,
    },
    {
        "label": "E2b scale check — FUS full-length saturation concentration in vitro",
        "C_E_M": 2.0 * uM,
        "source": "Wang et al. 2018, Cell 174:688 (PMID 29961577, PMC6063760, "
                  "doi:10.1016/j.cell.2018.06.006)",
        "measured_quantity": "'The measured saturation concentration of full-length FUS "
                             "is ~2 uM in 75 mM KCl' (in vitro, purified, tagged protein)",
        "conversion_assumptions": [
            "Used ONLY as a scale check on the physical argument that in a two-phase "
            "system the dilute-phase (free) concentration is pinned near c_sat, so a "
            "bulk free FET-LC concentration far above the low-micromolar scale is not "
            "self-consistent with these proteins' measured phase behaviour.",
            "In vitro at 75 mM KCl with a purified tagged protein; the nucleus is not "
            "that buffer (RNA, crowding, PTMs, partners all shift c_sat).",
            "FUS, not EWSR1.",
        ],
        "caveat": "An in-vitro thermodynamic scale, not a cellular measurement. Chong "
                  "2018 separately report NO detectable phase separation of EWS/FLI1 at "
                  "endogenous levels, i.e. that system sits BELOW its c_sat, which is "
                  "consistent with a sub-micromolar to low-micromolar free pool.",
        "is_measurement_of_C_E": False,
    },
    {
        "label": "E3 intra-condensate — upper end of Chong's stated hub operating range",
        "C_E_M": 100.0 * uM,
        "source": "Chong et al. 2018, Science 361:eaar2555 (PMID 29930090, PMC6961784, "
                  "doi:10.1126/science.aar2555)",
        "measured_quantity": "the paper's stated range of transcription-factor "
                             "concentrations over which LCD-dependent transactivation "
                             "hubs operate, '100 nM to 100 uM' (graphical abstract). "
                             "NOTE: the retrieved PMC body text prints '100 nM to 100 mM' "
                             "at the corresponding sentence — an internal inconsistency "
                             "in the source as retrieved. The uM figure is used and the "
                             "discrepancy is reported, not silently resolved.",
        "conversion_assumptions": [
            "Treats the upper end of a hub TF concentration range as a stand-in for local "
            "engageable EWSR1-LC site concentration inside a FET hub. That is a "
            "substitution across species and quantity, flagged as such.",
            "One arm-2 site per chain.",
        ],
        "caveat": "Not a measurement of wild-type EWSR1 inside a condensate. The lane's "
                  "decisive intra-condensate quantity remains unmeasured; this point "
                  "shows only WHERE on the curve a plausible hub concentration lands.",
        "is_measurement_of_C_E": False,
    },
]

# --- Site-multiplicity sensitivity --------------------------------------------------
# The model's C_E is a concentration of engageable ARM-2 SITES, not of protein chains.
# If arm 2 engages a short repeated LC motif rather than one site per chain, the site
# concentration is n_sites x the protein concentration. Wang et al. 2018 report that
# EWSR1's disordered regions carry 80 tyrosine+arginine residues; if even a modest
# fraction of those constitute independent engageable motifs, n_sites >> 1. This is
# NOT a claim about what arm 2 binds — the paper does not specify it — it is the
# sensitivity that decides whether the bulk-regime verdict survives.
N_SITES_SWEEP = [1, 3, 10, 30, 80]
PROTEIN_CONCS = [("EWS/FLI1 anchor, 200 nM", 200e-9),
                 ("FUS-family HeLa ceiling, 5 uM", 5.0 * uM)]


def main():
    if abs(CIS_ONLY - 5.79) > 0.01:
        sys.stderr.write(
            "IDENTITY CHECK FAILED: cis-only window %.4f does not reproduce the parent "
            "lane's 5.79x baseline; the formalism has drifted.\n" % CIS_ONLY)
        return 1

    placed = []
    for e in EVIDENCE:
        w = window(e["C_E_M"])
        retained = w / CIS_ONLY
        rec = dict(e)
        rec["C_E_uM"] = e["C_E_M"] / uM
        rec["window"] = round(w, 3)
        rec["window_retained_vs_cis_only"] = round(retained, 4)
        rec["regime"] = regime(retained)
        placed.append(rec)

    sensitivity = []
    for name, c in PROTEIN_CONCS:
        for n in N_SITES_SWEEP:
            ce = n * c
            w = window(ce)
            retained = w / CIS_ONLY
            sensitivity.append({
                "protein_concentration": name,
                "n_arm2_sites_per_chain": n,
                "C_E_uM": round(ce / uM, 4),
                "window": round(w, 3),
                "window_retained_vs_cis_only": round(retained, 4),
                "regime": regime(retained),
            })

    out = {
        "_lane": "ANDGATE-2",
        "_continues": "PUB-ANDGATE/fusion-andgate-trans-competition.json",
        "_compute": "CPU, pure stdlib, no GPU, no network, no external data",
        "_no_arm2_ligand_exists": True,
        "_conditional_bounding_model": (
            "Evaluates the design assuming an arm-2 ligand with the paper's illustrative "
            "Kd2 EXISTS; it does not. No efficacy, selectivity, safety or window claim."),
        "_no_value_guessed": (
            "Every C_E is either a cited published measurement with its exact measured "
            "quantity named, or an explicitly labelled swept sensitivity point."),
        "inputs": {"Kd1_M": KD1, "Kd2_M": KD2, "EM_M": EM, "free_ligand_M": L},
        "cis_only_window": round(CIS_ONLY, 3),
        "parent_lane_cis_only_window": 5.79,
        "half_window_C_E_M": KD2,
        "regime_bands": {
            "negligible": "window retained >= 0.90",
            "materially degraded": "0.20 < window retained < 0.90",
            "fatal": "window retained <= 0.20 (includes window -> 1.0, selectivity gone)",
        },
        "literature_placement": placed,
        "arm2_site_multiplicity_sensitivity": sensitivity,
        "decisive_quantity_still_unmeasured": (
            "No source retrieved measures the free engageable wild-type EWSR1-LC arm-2 "
            "site concentration, in bulk nucleoplasm or inside a condensate. No published "
            "small-molecule partition coefficient for a FET-family condensate was found. "
            "The bulk-regime placement rests on anchors from a related species "
            "(EWS/FLI1) and a protein family statement (HeLa FUS family)."),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1)
    print("cis-only window: %.3f (parent lane: 5.79) — identity check PASSED" % CIS_ONLY)
    for p in placed:
        print("%-70s C_E=%9.3f uM  window=%5.2f  retained=%.4f  %s"
              % (p["label"], p["C_E_uM"], p["window"],
                 p["window_retained_vs_cis_only"], p["regime"]))
    print("")
    for s in sensitivity:
        print("%-32s n_sites=%3d  C_E=%9.3f uM  window=%5.2f  retained=%.4f  %s"
              % (s["protein_concentration"], s["n_arm2_sites_per_chain"], s["C_E_uM"],
                 s["window"], s["window_retained_vs_cis_only"], s["regime"]))
    print("\nwrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
