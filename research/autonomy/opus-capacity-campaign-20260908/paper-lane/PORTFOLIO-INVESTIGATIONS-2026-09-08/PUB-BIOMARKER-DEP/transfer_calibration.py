#!/usr/bin/env python3
"""
Calibration of the biomarker -> dependency TRANSFER evidence behind PUB-BIOMARKER-DEP.

QUESTION. Every dependency statement in `research/manuscripts/dependency/
emc-biomarker-selected-classes.md` is a transfer from other sarcomas, read out of
`research/modalities/depmap-sarcoma-dependency.json`, because no EMC line exists in DepMap.
A transfer is only worth as much as the instrument that carries it. So: with the evidence the
committed panel actually records, what size of biomarker-stratified dependency difference is
RESOLVABLE, and does the panel's own biomarker-defined positive control (SS18::SSX synovial
sarcoma -> BRD9) resolve at all?

METHOD, all arithmetic on numbers already committed in the repository. Nothing is fetched.
  1. Integrality check: recover counts from each recorded fraction x n and check they are whole.
  2. Wilson score 95% intervals for every recorded dependency fraction (subtype and panel level).
  3. Exact (Fisher) power for a subtype-vs-panel dependency contrast at the subtype sizes the
     panel actually holds, over a grid of true subtype dependency rates.
  4. The minimum subtype n at which a strong biomarker-defined dependency becomes resolvable.

WHAT THIS IS NOT. It is not an EMC dependency reading, not an efficacy, safety or selectivity
claim, and not a re-run of the producer. It is a statement about what the committed instrument
can and cannot resolve.
"""
import json, os, sys
from math import sqrt
from scipy.stats import fisher_exact, hypergeom, binom

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
PANEL = os.path.join(REPO, "research/modalities/depmap-sarcoma-dependency.json")
OUT = os.path.join(HERE, "transfer-calibration.json")

Z = 1.959963984540054  # 95%


def wilson(k, n):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def fisher_power(n1, p1, n2, p2, alpha=0.05):
    """Exact power of a two-sided Fisher test for subtype (n1, true rate p1) vs panel (n2, p2).

    Enumerates every 2x2 table, weights it by the independent binomial probability of the two
    margins under (p1, p2), and sums the weight where Fisher's exact p < alpha. No normal
    approximation, so it is valid at n1 = 5.
    """
    w1 = [binom.pmf(x, n1, p1) for x in range(n1 + 1)]
    w2 = [binom.pmf(y, n2, p2) for y in range(n2 + 1)]
    power = 0.0
    pcache = {}
    for x, wx in enumerate(w1):
        if wx < 1e-12:
            continue
        for y, wy in enumerate(w2):
            if wy < 1e-12:
                continue
            key = (x, y)
            if key not in pcache:
                pcache[key] = fisher_exact([[x, n1 - x], [y, n2 - y]])[1]
            if pcache[key] < alpha:
                power += wx * wy
    return round(power, 4)


def main():
    panel = json.load(open(PANEL))
    n_pan = None
    res = {
        "_what": "Resolving-power calibration of the sarcoma-line dependency transfer used by "
                 "PUB-BIOMARKER-DEP. Derived arithmetic only; no data fetched, no producer re-run.",
        "input_artifact": os.path.relpath(PANEL, REPO),
        "input_data_source": panel["data_source"],
        "dependent_threshold": panel["dependent_threshold"],
        "n_sarcoma_models_in_release": panel["n_sarcoma_models"],
    }

    # ---- 1. integrality: do the recorded fractions correspond to whole line counts? ----
    integ = []
    for grp, rows in panel["genes_by_group"].items():
        for r in rows:
            n = r["n_sarcoma"]
            n_pan = n_pan or n
            k = r["sarcoma_frac_dependent"] * n
            integ.append({"gene": r["gene"], "group": grp, "n_sarcoma": n,
                          "implied_k": round(k, 3), "whole": abs(k - round(k)) < 0.05})
    res["integrality_check"] = {
        "genes_checked": len(integ),
        "n_screened_sarcoma_lines_implied": n_pan,
        "all_fractions_imply_whole_line_counts": all(i["whole"] for i in integ),
        "failures": [i for i in integ if not i["whole"]],
        "_meaning": "sarcoma_frac_dependent x n_sarcoma is integral for every gene, so the "
                    "denominator of every sarcoma-level dependency fraction in the panel is the "
                    "same %s SCREENED lines - not the %s sarcoma models the release contains."
                    % (n_pan, panel["n_sarcoma_models"]),
    }

    # ---- 2. Wilson intervals on the panel's own controls and subtype readings ----
    controls = []
    subtypes = dict(panel["BRD9_by_fusion_sarcoma_subtype"])
    brd9_pan = [r for r in panel["genes_by_group"]["ncBAF (primary hypothesis)"]
                if r["gene"] == "BRD9"][0]
    smarcb1_pan = [r for r in panel["genes_by_group"]["BAF / SWI-SNF core"]
                   if r["gene"] == "SMARCB1"][0]
    sv = panel["self_validation"]
    for label, gene, rec, pan in [
        ("BRD9 in synovial (the panel's own stated expected-positive)", "BRD9",
         sv["BRD9_in_synovial"], brd9_pan),
        ("SMARCB1 in rhabdoid (the panel's other stated expected-positive)", "SMARCB1",
         sv["SMARCB1_in_rhabdoid"], smarcb1_pan),
    ]:
        n, f = rec["n"], rec["frac_dependent"]
        k = round(f * n)
        controls.append({
            "control": label, "gene": gene, "n_lines": n,
            "k_dependent": k, "frac_dependent": f,
            "wilson95": wilson(k, n),
            "panel_background_frac_dependent_rest": pan["rest_frac_dependent"],
            "panel_background_frac_dependent_sarcoma": pan["sarcoma_frac_dependent"],
            "fisher_p_vs_rest_panel": round(fisher_exact(
                [[k, n - k],
                 [round(pan["rest_frac_dependent"] * (panel["n_models_total"] - n_pan)),
                  (panel["n_models_total"] - n_pan) - round(
                      pan["rest_frac_dependent"] * (panel["n_models_total"] - n_pan))]])[1], 4),
        })
    res["stated_positive_controls"] = controls

    sub_rows = []
    for name, rec in subtypes.items():
        if rec is None:
            sub_rows.append({"subtype": name, "present_in_release": False})
            continue
        n, f = rec["n"], rec["frac_dependent"]
        k = round(f * n)
        sub_rows.append({"subtype": name, "present_in_release": True, "gene": "BRD9",
                         "n_lines": n, "k_dependent": k, "frac_dependent": f,
                         "wilson95": wilson(k, n)})
    res["brd9_by_subtype_with_intervals"] = sub_rows

    # ---- 3. exact power at the subtype sizes the panel actually holds ----
    bg = brd9_pan["sarcoma_frac_dependent"]  # 0.022 - a non-dependent background
    grid = [0.4, 0.6, 0.8, 1.0]
    ns = sorted({r["n_lines"] for r in sub_rows if r.get("n_lines")} |
                {sv["SMARCB1_in_rhabdoid"]["n"], n_pan})
    power = []
    for n1 in ns:
        row = {"subtype_n": n1, "background_frac_dependent": bg,
               "background_n": n_pan, "alpha": 0.05}
        for p1 in grid:
            row["power_if_true_subtype_rate_%.1f" % p1] = fisher_power(n1, p1, n_pan, bg)
        power.append(row)
    res["exact_power_subtype_vs_panel"] = {
        "_method": "two-sided Fisher exact, full table enumeration weighted by independent "
                   "binomials; valid at n=5 where a normal approximation is not.",
        "rows": power,
    }

    # ---- 4. smallest subtype n that resolves a strong biomarker-defined dependency ----
    thresholds = {}
    for p1 in (0.8, 1.0):
        found = None
        for n1 in range(2, 61):
            if fisher_power(n1, p1, n_pan, bg) >= 0.8:
                found = n1
                break
        thresholds["min_n_for_80pct_power_at_true_rate_%.1f" % p1] = found
    res["resolving_threshold"] = {
        **thresholds,
        "_meaning": "the smallest biomarker-defined subtype in which a dependency present in "
                    "80-100%% of lines could be distinguished from the panel's %s background at "
                    "80%% power, alpha 0.05." % bg,
    }

    # ---- 5. what the artifact does NOT record ----
    keys = set()
    for rows in panel["genes_by_group"].values():
        for r in rows:
            keys |= set(r)
    res["dispersion_gap"] = {
        "per_gene_fields_recorded": sorted(keys),
        "records_any_dispersion": any(k in keys for k in ("sd", "std", "sem", "ci", "quantiles")),
        "records_per_line_values": False,
        "_consequence": "the committed panel stores means and fractions only. A mean with no "
                        "dispersion and no per-line values admits NO interval or power statement "
                        "on the continuous gene-effect scale; every calibration above is therefore "
                        "restricted to the binarised dependent/not readout, which discards "
                        "information the producer had and did not keep.",
    }

    # ---- 6. threshold sensitivity: is it n, or is it the binarisation? ----
    # The power block says a subtype as small as 5 lines has ~0.99 power against a dependency
    # present in 80% of that subtype. So sample size is NOT what stops the stated positive
    # control from coming out. The remaining candidate is the -0.5 binarisation. Reconstruct the
    # per-line spread implied by the one subtype where a mean and a fraction are both recorded.
    from scipy.stats import norm
    syn = sv["BRD9_in_synovial"]
    m_sub, f_sub = syn["mean_gene_effect"], syn["frac_dependent"]
    thr = panel["dependent_threshold"]
    sd_implied = (thr - m_sub) / norm.ppf(f_sub) if 0 < f_sub < 1 else None
    m_pan = brd9_pan["sarcoma_mean"]
    f_pan_pred = float(norm.cdf((thr - m_pan) / sd_implied)) if sd_implied else None
    res["threshold_sensitivity"] = {
        "_question": "the power block rules out sample size as the reason the stated "
                     "BRD9-in-synovial positive control does not come out. Is the -0.5 "
                     "binarisation the reason instead?",
        "synovial_mean_gene_effect": m_sub,
        "panel_sarcoma_mean_gene_effect": m_pan,
        "mean_shift_synovial_vs_panel": round(m_sub - m_pan, 4),
        "shift_direction_matches_expected_positive": (m_sub - m_pan) < 0,
        "distance_of_subtype_mean_from_threshold": round(m_sub - thr, 4),
        "implied_per_line_sd_from_the_one_recorded_mean_fraction_pair":
            round(sd_implied, 4) if sd_implied else None,
        "panel_frac_dependent_predicted_from_that_sd": round(f_pan_pred, 4) if f_pan_pred else None,
        "panel_frac_dependent_recorded": brd9_pan["sarcoma_frac_dependent"],
        "gaussian_reconstruction_consistent": (
            abs(f_pan_pred - brd9_pan["sarcoma_frac_dependent"]) < 0.03) if f_pan_pred else None,
        "_reading": "The subtype shift is in the expected direction (-0.235 gene-effect units, "
                    "synovial below the sarcoma panel) but its MEAN sits 0.37 units on the "
                    "non-dependent side of the -0.5 cut, so the binarised readout scores it 1 of "
                    "5. A single-Gaussian reconstruction of the per-line spread from that one "
                    "recorded (mean, fraction) pair over-predicts the panel's own BRD9 dependent "
                    "fraction (0.085 predicted against 0.022 recorded), so the reconstruction is "
                    "NOT self-consistent and is reported as a bound, not an estimate. What it "
                    "does establish either way: the quantity the panel binarises is not the "
                    "quantity in which the expected positive control lives.",
        "_falsifier": "per-line CRISPRGeneEffect values for the 5 synovial and 91 screened "
                      "sarcoma lines, which would replace this reconstruction with the real "
                      "distribution and settle it in one pass.",
    }

    res["matched_evidence_check"] = {
        "_question": "does any committed artifact hold a biomarker and a dependency measured in "
                     "the SAME models, which is what a biomarker-selected class claim needs?",
        "biomarker_axis_artifact": "research/modalities/emc-expression-panels.json - 16 EMC "
                                   "tumours + comparators, expression only, no dependency, no "
                                   "cell line.",
        "dependency_axis_artifact": "research/modalities/depmap-sarcoma-dependency.json - "
                                    "sarcoma cell lines, dependency only, no expression field, "
                                    "no per-line values, no EMC line.",
        "models_in_common": 0,
        "verdict": "NO MATCHED EVIDENCE EXISTS IN THIS REPOSITORY for any of the five classes: "
                   "the two axes share no model, and neither artifact carries the other's "
                   "measurement. The only biomarker-stratified dependency contrast committed "
                   "anywhere here is BRD9 by sarcoma subtype. It is NOT limited by sample size - "
                   "the exact power block shows 0.99 power at n=5 against a dependency present "
                   "in 80% of a subtype - and it still does not reproduce the panel's own stated "
                   "expected positive. On the calibration above the limiting factor is the "
                   "readout, not the n.",
    }
    json.dump(res, open(OUT, "w"), indent=1)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
