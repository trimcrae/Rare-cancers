#!/usr/bin/env python3
"""
PUB-SYNLETH investigation, 2026-09-08/09.

QUESTION. degrader-vs-synthetic-lethal.md Sec 2b reports a NEGATIVE transfer prior for
BRD9/ncBAF from a pan-sarcoma DepMap statistic, and Sec 3 re-weights the program's route
choice on that negative. The statistic is

    selectivity(gene) = mean(gene effect, all non-sarcoma lines) - mean(gene effect, 91 sarcoma lines)

This script asks a purely arithmetic, computationally falsifiable question about that
statistic itself: CAN a pan-sarcoma mean difference over 91 lines detect a dependency that
is restricted to a sarcoma SUBTYPE? If it cannot, the Sec 2b BRD9 null is a null-power
artifact, not a biological negative -- and the memo's route re-weighting rests on it.

METHOD. Three local computations, no network, no new data:
  (A) Empirical scale of the statistic across every gene the retained run reported. This
      bounds the magnitude at which a |selectivity| value is distinguishable from the
      run's own background.
  (B) Dilution arithmetic. A dependency present in k of N=91 sarcoma lines with per-line
      effect delta (relative to the sarcoma baseline for that gene) contributes exactly
      (k/N)*|delta| to the pan-sarcoma statistic. Invert to get the per-line effect a
      subtype of size k would need in order to clear the background from (A).
  (C) Closed-loop check on real measured numbers. The retained artifact contains BOTH the
      pan-sarcoma BRD9 statistic AND the BRD9 mean inside synovial sarcoma (n=5), the one
      context where ncBAF dependence is externally established. Predict the synovial
      contribution to the pan-sarcoma statistic from (B) and compare it to (A).

INPUT (read-only): research/modalities/depmap-sarcoma-dependency.json (DepMap 24Q4 run).
OUTPUT: selectivity-detectability.json in this directory.

NOT A CLAIM ABOUT EMC. No EMC line has CRISPR data in the panel, so k_EMC = 0 and no value
of delta produces any signal at all. Nothing here supports or refutes efficacy of anything.
"""
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..",
                                   "modalities", "depmap-sarcoma-dependency.json"))
OUT = os.path.join(HERE, "selectivity-detectability.json")

d = json.load(open(SRC))
N = 91  # every gene record in the artifact carries n_sarcoma = 91

rows = [r for grp in d["genes_by_group"].values() for r in grp] + d["context_genes"]
sel = [r["selectivity"] for r in rows]
absel = sorted(abs(s) for s in sel)


def pct(xs, p):
    if not xs:
        return None
    i = min(len(xs) - 1, max(0, int(round(p * (len(xs) - 1)))))
    return xs[i]


# (A) empirical scale of the statistic in this very run
background = {
    "n_genes_reported": len(rows),
    "selectivity_mean": round(statistics.fmean(sel), 4),
    "selectivity_sd": round(statistics.pstdev(sel), 4),
    "abs_selectivity_median": round(pct(absel, 0.50), 4),
    "abs_selectivity_p90": round(pct(absel, 0.90), 4),
    "abs_selectivity_p95": round(pct(absel, 0.95), 4),
    "abs_selectivity_max": round(absel[-1], 4),
    "largest_abs_selectivity_genes": sorted(
        ({"gene": r["gene"], "selectivity": r["selectivity"]} for r in rows),
        key=lambda x: -abs(x["selectivity"]))[:6],
    "_caveat": ("These genes were chosen as hypothesis targets, not as a random null set, so "
                "this is the observed spread of the statistic in this run, not a calibrated "
                "null distribution. It is used only as an order-of-magnitude resolution floor."),
}
# resolution floor: a |selectivity| below the median of the run's own values is
# indistinguishable from the run's background scatter.
FLOOR = background["abs_selectivity_median"]
FLOOR_STRICT = background["abs_selectivity_p90"]

# (B) dilution arithmetic
subtypes = {
    "EMC (the disease in question)": 0,
    "one line": 1,
    "synovial sarcoma (BRD9 positive control)": 5,
    "alveolar RMS": 8,
    "rhabdoid": 13,
    "Ewing sarcoma": 27,
    "all screened sarcoma lines": 91,
}
DELTA_CEILING = 1.0   # gene effect of a canonical common-essential gene (~ -1.0)
DELTA_EXTREME = 1.85  # CDK7 in this very panel (-1.847): about the strongest effect observed

dilution = {}
for name, k in subtypes.items():
    frac = k / N
    entry = {
        "k_lines": k,
        "dilution_factor_k_over_N": round(frac, 4),
        "pan_sarcoma_signal_if_delta_is_common_essential_1.0": round(frac * DELTA_CEILING, 4),
        "pan_sarcoma_signal_if_delta_is_CDK7_scale_1.85": round(frac * DELTA_EXTREME, 4),
    }
    if k == 0:
        entry["required_delta_to_reach_median_background"] = None
        entry["detectable"] = False
        entry["_why"] = "k = 0: no line of this type is in the screened panel, so the statistic is identically blind to it at any effect size."
    else:
        req = FLOOR / frac
        req_strict = FLOOR_STRICT / frac
        entry["required_delta_to_reach_median_background"] = round(req, 3)
        entry["required_delta_to_reach_p90_background"] = round(req_strict, 3)
        entry["clears_median_background_at_common_essential_effect_1.0"] = bool(req <= DELTA_CEILING)
        entry["clears_median_background_at_CDK7_scale_effect_1.85"] = bool(req <= DELTA_EXTREME)
        entry["clears_p90_background_at_common_essential_effect_1.0"] = bool(req_strict <= DELTA_CEILING)
        entry["clears_p90_background_at_CDK7_scale_effect_1.85"] = bool(req_strict <= DELTA_EXTREME)
        if req_strict <= DELTA_CEILING:
            entry["verdict"] = "DETECTABLE: a common-essential-scale subtype dependency clears even the strict background."
        elif req <= DELTA_CEILING:
            entry["verdict"] = ("MARGINAL: a common-essential-scale subtype dependency lands between the median and "
                                "the p90 of this run's own |selectivity| values, i.e. inside the background scatter "
                                "and not reportable as a signal.")
        elif req_strict <= DELTA_EXTREME:
            entry["verdict"] = "MARGINAL ONLY AT EXTREME EFFECT: needs an effect beyond common-essential to be seen at all."
        else:
            entry["verdict"] = ("NOT DETECTABLE IN PRACTICE: the required per-line effect exceeds the strongest effect "
                                "anywhere in this panel (CDK7, -1.847).")
    dilution[name] = entry

# (C) closed loop on measured numbers
brd9 = next(r for r in d["genes_by_group"]["ncBAF (primary hypothesis)"] if r["gene"] == "BRD9")
syn = d["self_validation"]["BRD9_in_synovial"]
delta_obs = syn["mean_gene_effect"] - brd9["sarcoma_mean"]   # synovial vs sarcoma baseline
pred = (syn["n"] / N) * abs(delta_obs)
closed_loop = {
    "gene": "BRD9",
    "pan_sarcoma_mean": brd9["sarcoma_mean"],
    "pan_sarcoma_selectivity_reported": brd9["selectivity"],
    "synovial_n": syn["n"],
    "synovial_mean_gene_effect": syn["mean_gene_effect"],
    "observed_subtype_effect_delta_vs_sarcoma_baseline": round(delta_obs, 4),
    "predicted_contribution_to_pan_sarcoma_statistic": round(pred, 4),
    "run_background_median_abs_selectivity": FLOOR,
    "contribution_is_below_background": bool(pred < FLOOR),
    "_reading": ("The measured synovial ncBAF signal, in the one context where ncBAF dependence "
                 "is externally established, contributes about "
                 f"{pred:.4f} to a statistic whose own background scatter in this run has median "
                 f"|selectivity| {FLOOR}. The pan-sarcoma statistic therefore could not have "
                 "reported that signal even though the run measured it directly."),
}

# (C2) THE POSITIVE CONTROL THE RUN ALREADY CONTAINS AND Sec 2b NEVER USED.
# Sec 2b states its selectivity detection was never validated, because its only chosen control
# (BRD9 in synovial, k=5) came back weak. But the same run measured FLI1 in Ewing sarcoma
# (k=27): a textbook subtype-restricted selective dependency. Test whether the pan-sarcoma
# statistic recovered it, and whether the dilution model of (B) predicts the magnitude.
fli = d["fusion_addiction_proxy"]["FLI1_overall"]
fli_ewing = d["fusion_addiction_proxy"]["FLI1_in_ewing"]
k_e = fli_ewing["n"]
# back out the non-Ewing sarcoma baseline from the reported sarcoma mean
nonewing_mean = (fli["sarcoma_mean"] * N - fli_ewing["mean_gene_effect"] * k_e) / (N - k_e)
delta_e = fli_ewing["mean_gene_effect"] - nonewing_mean
predicted_sel = (k_e / N) * abs(delta_e)
positive_control = {
    "gene": "FLI1",
    "context": "Ewing sarcoma, where EWS-FLI1 is the driver",
    "subtype_n": k_e,
    "subtype_mean_gene_effect": fli_ewing["mean_gene_effect"],
    "subtype_frac_dependent": fli_ewing["frac_dependent"],
    "rest_of_panel_frac_dependent": fli["rest_frac_dependent"],
    "pan_sarcoma_selectivity_reported": fli["selectivity"],
    "run_background_p90_abs_selectivity": FLOOR_STRICT,
    "recovered_above_p90_background": bool(abs(fli["selectivity"]) > FLOOR_STRICT),
    "implied_non_ewing_sarcoma_mean": round(nonewing_mean, 3),
    "implied_subtype_effect_delta": round(delta_e, 3),
    "dilution_model_predicted_selectivity": round(predicted_sel, 3),
    "_reading": ("A genuine subtype-restricted selective dependency (74.1% of Ewing lines dependent vs "
                 "1.9% of the rest of the panel) IS recovered by the pan-sarcoma statistic (+0.242, above "
                 f"this run's p90 background of {FLOOR_STRICT}), and the dilution model of (B) predicts its "
                 f"magnitude ({round(predicted_sel,3)} predicted vs {fli['selectivity']} observed). "
                 "So the selectivity detector works. Sec 2b's stated validation gap is closed by data the "
                 "same run already produced. What the detector cannot do is resolve k = 5; the dilution "
                 "model explains both outcomes with one parameter, k/N."),
}

# (C3) the pan-essential trap in a new guise: EWSR1 carries the LARGEST selectivity in the panel.
ews = d["fusion_addiction_proxy"]["EWSR1_overall"]
pan_essential_trap = {
    "gene": "EWSR1",
    "sarcoma_mean": ews["sarcoma_mean"],
    "rest_mean": ews["rest_mean"],
    "selectivity": ews["selectivity"],
    "sarcoma_frac_dependent": ews["sarcoma_frac_dependent"],
    "rest_frac_dependent": ews["rest_frac_dependent"],
    "is_largest_selectivity_in_panel": True,
    "_warning": ("EWSR1 has the single largest |selectivity| in this panel (+0.373) and must NOT be read "
                 "as a sarcoma window. It is a dependency in 96.7% of screened sarcoma lines AND 91.5% of "
                 "everything else: pan-essential, exactly the CDK7/CDK9 trap in a different guise. The "
                 "selectivity statistic here measures a shift in depth of an essentiality that is already "
                 "near-universal, not the existence of a margin. Any use of the selectivity number must be "
                 "read beside frac_dependent outside the context, or it manufactures a false window."),
}

# which Sec 2b claims survive this
claim_audit = {
    "supported_by_this_panel": [
        {"claim": "CDK7/CDK9/BRD4 are essential in essentially all screened lines, inside and outside sarcoma (pan-essential; no window).",
         "why": "A claim about ALL 91 sarcoma lines and ~2000 others. No dilution: k = N. High power."},
        {"claim": "NR4A3 is not a dependency in any of the 91 screened sarcoma lines (mean +0.021, 0% dependent), and NR4A1/2/3 are broadly non-essential across the panel.",
         "why": "A dispensability claim over all lines, again k = N. The panel can support non-dependence broadly. It still says nothing about EMC, which is absent."},
    ],
    "not_supported_by_this_panel": [
        {"claim": "BRD9/ncBAF is not a sarcoma dependency (pan-sarcoma selectivity -0.016), used as a negative transfer prior for EMC.",
         "why": ("Subtype-restricted dependency is diluted by k/N. At k = 5 a per-line effect of the "
                 "canonical common-essential size (-1.0) produces a pan-sarcoma statistic of only "
                 f"{dilution['synovial sarcoma (BRD9 positive control)']['pan_sarcoma_signal_if_delta_is_common_essential_1.0']}, "
                 f"against a run background whose median |selectivity| is {FLOOR} and whose p90 is {FLOOR_STRICT}. "
                 "So even a maximal subtype dependency lands inside the background scatter. Clearing the p90 "
                 f"would require a per-line effect of {dilution['synovial sarcoma (BRD9 positive control)']['required_delta_to_reach_p90_background']}, "
                 "beyond the strongest effect anywhere in this panel (CDK7, -1.847). The closed-loop check in (C) "
                 "confirms this on measured numbers rather than assumption.")},
        {"claim": "Ewing BRD9 +0.134 / 0% dependent shows the EWSR1-prion-to-BAF transfer logic fails where it should hold.",
         "why": "This one is a SUBTYPE read (n=27), not the diluted pan-sarcoma statistic, so it is not affected by the dilution argument "
                "and remains the strongest retained evidence against the BRD9 hypothesis. It is bounded by n=27 and by being Ewing, not EMC."},
    ],
    "_consequence_for_the_memo": (
        "Sec 3's verdict re-weights toward the degrader route because 'the comparator lost support'. "
        "Part of that lost support - the pan-sarcoma BRD9 selectivity null - is uninformative rather than "
        "negative. The Ewing subtype null survives and still argues against BRD9. So the re-weighting is "
        "weakened but not erased, and the memo's own hedge ('a weak prior against BRD9 rather than a "
        "settled negative') is the correct reading for a reason it does not state."),
}

result = {
    "_id": "PUB-SYNLETH-SELECTIVITY-DETECTABILITY-20260909",
    "_question": ("Does the pan-sarcoma selectivity statistic used in degrader-vs-synthetic-lethal.md "
                  "Sec 2b have the power to detect a subtype-restricted dependency? If not, its BRD9 "
                  "null is a null-power artifact rather than a biological negative."),
    "_input": {"path": "research/modalities/depmap-sarcoma-dependency.json",
               "data_source": d["data_source"],
               "n_models_total": d["n_models_total"],
               "n_sarcoma_models": d["n_sarcoma_models"],
               "n_screened_sarcoma_lines_used_here": N},
    "_method": "Arithmetic on retained group summaries. No new data, no network, no re-run of the producer.",
    "A_run_background_scale": background,
    "B_dilution_and_required_effect": dilution,
    "C_closed_loop_check_on_BRD9_synovial": closed_loop,
    "C2_unused_positive_control_FLI1_in_ewing": positive_control,
    "C3_pan_essential_trap_check_EWSR1": pan_essential_trap,
    "D_claim_audit": claim_audit,
    "E_headline": (
        "The selectivity detector is VALIDATED, by a positive control the same run already produced and Sec 2b never used (FLI1 in Ewing, k=27, recovered at +0.242). "
        "It resolves dependencies that are broad across the sarcoma class, "
        "and cannot resolve dependencies restricted to a subtype the size of the ones EMC would resemble. "
        "One parameter, k/N, explains both the recovery and the failure. Its BRD9 null is therefore weak evidence about ncBAF, not the negative the memo's Sec 3 leans on. "
        "The Ewing SUBTYPE read (n=27, +0.134, 0% dependent) is unaffected by this and remains the real "
        "retained argument against the BRD9 hypothesis."),
    "_limitations": [
        "Group summaries only. The retained artifact holds no per-line gene-effect values, so this is exact dilution arithmetic plus an order-of-magnitude background scale, NOT a variance-based power calculation. A true power curve needs the per-line matrix.",
        "The FLI1/Ewing positive control in (C2) validates selectivity detection at k = 27 only. It does not validate detection at smaller k, and the dilution model says it should not.",
        "The implied non-Ewing sarcoma mean in (C2) is back-computed from two rounded group means, so its third decimal is not meaningful.",
        "The background scale in (A) comes from hypothesis-selected genes, not a random null set; it is a resolution floor, not a calibrated null.",
        "Nothing here is an EMC measurement. No EMC line in the panel has CRISPR data (k = 0), so no statistic computed on this panel can be informative about EMC at any effect size.",
        "This says nothing about whether BRD9 is or is not an EMC dependency. It says the pan-sarcoma statistic cannot answer that question.",
        "No efficacy, potency, selectivity, safety, therapeutic-window or clinical claim is made or implied for either route.",
    ],
}
json.dump(result, open(OUT, "w"), indent=2)
print(json.dumps({"background": background, "closed_loop": closed_loop,
                  "positive_control": positive_control, "pan_essential_trap": pan_essential_trap,
                  "dilution_synovial": dilution["synovial sarcoma (BRD9 positive control)"],
                  "dilution_ewing": dilution["Ewing sarcoma"],
                  "dilution_EMC": dilution["EMC (the disease in question)"]}, indent=2))
print("wrote", OUT)
