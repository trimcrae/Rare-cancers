#!/usr/bin/env python3
"""The comparator run for `atr_part_d_proliferation_control.py`.

⛔ SEPARATE FILE ON PURPOSE. The pre-registration was committed on its own, with `results: null`,
BEFORE this module existed — so `git log --follow` on the two files shows the criterion landing
before the number. Nothing here may change a bar; this module only substitutes which committed
per-line score supplies `control_rho` and re-runs the SAME arithmetic.

Every statistic is imported from the module under test rather than reimplemented, so a divergence
between this artifact and the committed one cannot come from a second implementation of Spearman.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from emc_atr_vulnerability import (  # noqa: E402
    _mean,
    _spearman,
    _welch,
    grade,
)

ARTIFACT = os.path.join(HERE, "emc-atr-vulnerability.json")

# The drug groups, copied from `derive_part_d` so the reproduction is exact. ⛔ If these ever
# diverge from the module the reproduction check below goes red, which is what it is for.
NON_DDR_CONTROLS = ("paclitaxel", "bortezomib", "doxorubicin")
PART_D_CONCEPTS = ("ATM_signalling_DSB_repair", "replication_stress", "ATR_CHK1_activity",
                   "stalled_fork_response", "S_phase_E2F", "DNA_damage_checkpoint",
                   "proliferation_MYC", "control_oxphos")
# the extra columns this analysis adds; NOT part of the committed predictor grid
EXTRA_CONTROL_PREDICTORS = ("proliferation_mitotic",)
BAR_MULTIPLIER = 1.15
MAGNITUDE_FLOOR = 0.15
VALIDITY_FLOOR = 0.30


def _build_predictors(inputs):
    """Rebuild part D's predictor grid, then add the candidate controls beside it."""
    pdd = inputs["part_d"]
    scores = pdd["expression_scores_by_line"]
    preds = {f"expr::{c}": scores[c] for c in PART_D_CONCEPTS if c in scores}
    if pdd.get("atr_axis_dependency_by_line"):
        preds["dependency::ATR_ATRIP_CHEK1_mean_gene_effect"] = pdd["atr_axis_dependency_by_line"]
    if pdd.get("fet_signature_score_by_line"):
        preds["signature::FET_fusion_heldout"] = pdd["fet_signature_score_by_line"]
    committed_grid = set(preds)
    for c in EXTRA_CONTROL_PREDICTORS:
        if c in scores:
            preds[f"expr::{c}"] = scores[c]
    # C2: the mean of both proliferation concepts — exactly what part B already subtracts.
    myc, mit = scores.get("proliferation_MYC"), scores.get("proliferation_mitotic")
    if myc and mit:
        preds["expr::proliferation_MYC_and_mitotic_mean"] = {
            k: round((myc[k] + mit[k]) / 2, 4) for k in set(myc) & set(mit)
            if myc[k] is not None and mit[k] is not None}
    return preds, committed_grid


def _correlate(inputs, preds):
    """Per drug, per predictor: Spearman rho against the drug-specific residual LN_IC50."""
    resid = inputs["part_d"]["gdsc_residual_ln_ic50_by_drug"]
    atri = {"azd6738", "ve-822"}
    corr = {}
    for drug, per_line in sorted(resid.items()):
        row = {"is_atr_inhibitor": drug in atri, "by_predictor": {}}
        for pname, pvals in preds.items():
            common = sorted(set(per_line) & set(pvals))
            if len(common) < 15:
                row["by_predictor"][pname] = {"_status": f"underpowered, n={len(common)}"}
                continue
            row["by_predictor"][pname] = _spearman([pvals[i] for i in common],
                                                   [per_line[i] for i in common])
        corr[drug] = row
    return corr


def _mean_rhos(corr, pname, names):
    got = [corr[d]["by_predictor"].get(pname, {}) for d in names if d in corr]
    rr = [g.get("rho") for g in got if isinstance(g, dict) and g.get("rho") is not None]
    return round(_mean(rr), 4) if rr else None


def compute(inputs):
    with open(ARTIFACT) as fh:
        art = json.load(fh)
    part_d = art["part_d_drug_response_correlation"]
    committed_spec = part_d["specificity"]
    committed_tests = part_d["mechanism_tests"]

    preds, committed_grid = _build_predictors(inputs)
    corr = _correlate(inputs, preds)
    atri_names = [d for d in corr if corr[d]["is_atr_inhibitor"]]

    atri_rho = {p: _mean_rhos(corr, p, atri_names) for p in preds}
    ctrl_rho = {p: _mean_rhos(corr, p, NON_DDR_CONTROLS) for p in preds}

    # --- the reproduction check, declared in advance -----------------------------------------
    repro = {"_what": ("every predictor the committed artifact carries must come back with the "
                       "identical mean rho across ATR inhibitors"),
             "per_predictor": {}, "n_checked": 0, "n_matching": 0}
    for p in sorted(committed_grid):
        want = committed_spec.get(p, {}).get("mean_rho_across_ATR_inhibitors")
        got = atri_rho.get(p)
        repro["per_predictor"][p] = {"committed": want, "recomputed": got, "match": want == got}
        repro["n_checked"] += 1
        repro["n_matching"] += int(want == got)
    repro["all_match"] = repro["n_checked"] == repro["n_matching"]
    if not repro["all_match"]:
        return {"_status": "VOID — the harness does not reproduce the committed artifact",
                "⛔ _no_verdict_is_reported": (
                    "a re-analysis that cannot reproduce the number it is re-analysing is "
                    "measuring its own harness. Declared in advance; applied here."),
                "reproduction_check": repro}

    # --- the validity check on the comparator, declared in advance ----------------------------
    scores = inputs["part_d"]["expression_scores_by_line"]

    def _across_lines(a, b):
        common = sorted(set(scores[a]) & set(scores[b]))
        return _spearman([scores[a][i] for i in common], [scores[b][i] for i in common])

    validity = {
        "_what": ("does the proposed comparator actually measure proliferation? A control that "
                  "measures nothing is trivially easy to beat, and a verdict that flipped under "
                  "one would be an artefact of a weak control."),
        "yardstick": "expr::S_phase_E2F (Hallmark E2F Targets) — the canonical proliferation axis",
        "⛔ why_the_yardstick_is_not_itself_a_candidate_control": (
            "S_phase_E2F is a TESTED predictor in part D. It is used here only to ask whether the "
            "comparator behaves like a proliferation score."),
        "declared_floor": VALIDITY_FLOOR,
        "rho_mitotic_vs_S_phase_E2F": _across_lines("proliferation_mitotic", "S_phase_E2F"),
        "rho_MYC_vs_S_phase_E2F": _across_lines("proliferation_MYC", "S_phase_E2F"),
        "rho_mitotic_vs_MYC": _across_lines("proliferation_mitotic", "proliferation_MYC"),
        "n_lines": len(scores["proliferation_MYC"]),
    }
    v = (validity["rho_mitotic_vs_S_phase_E2F"] or {}).get("rho")
    validity["comparator_is_a_usable_proliferation_proxy"] = bool(
        v is not None and v >= VALIDITY_FLOOR)
    if not validity["comparator_is_a_usable_proliferation_proxy"]:
        return {"_status": "VOID — the comparator is not a usable proliferation proxy",
                "⛔ _no_flipped_verdict_is_reported": (
                    "declared in advance: below the floor the comparison fails and this artifact "
                    "says so rather than reporting a verdict change."),
                "reproduction_check": repro, "validity_check": validity}

    # --- PART D under each declared control ---------------------------------------------------
    controls = {
        "C0_incumbent_proliferation_MYC": "expr::proliferation_MYC",
        "C1_primary_proliferation_mitotic": "expr::proliferation_mitotic",
        "C2_consistency_MYC_and_mitotic_mean": "expr::proliferation_MYC_and_mitotic_mean",
    }
    part_d_by_control = {}
    for label, cpred in controls.items():
        c_rho = atri_rho[cpred]
        bar = round(abs(c_rho) * BAR_MULTIPLIER, 6)
        tests = {}
        for pname, ct in committed_tests.items():
            rho = atri_rho[pname]
            beats = None if pname == cpred else bool(abs(rho) > abs(c_rho) * BAR_MULTIPLIER)
            tests[pname] = {
                "mean_rho_across_ATR_inhibitors": rho,
                "abs_rho": round(abs(rho), 4),
                "direction_predicted": ct["direction_predicted"],
                "direction_matches": ct["direction_matches"],
                "magnitude_at_least_0.15": ct["magnitude_at_least_0.15"],
                "atri_specific": ct["atri_specific"],
                "beats_the_proliferation_control": beats,
                "passes": bool(ct["direction_matches"] and ct["magnitude_at_least_0.15"]
                               and ct["atri_specific"] and beats is True),
                "⭐ criteria_failed": [k for k, ok in (
                    ("direction", ct["direction_matches"]),
                    ("magnitude>=0.15", ct["magnitude_at_least_0.15"]),
                    ("atri_specific", ct["atri_specific"]),
                    ("beats_the_control", beats is True)) if not ok],
            }
        n_pass = sum(1 for t in tests.values() if t["passes"])
        # the whole specificity table under this control, not only the four tested predictors
        spec = {p: {"mean_rho_across_ATR_inhibitors": atri_rho[p],
                    "mean_rho_across_non_DDR_controls": ctrl_rho[p],
                    "beats_the_proliferation_control":
                        None if p == cpred else bool(abs(atri_rho[p]) > abs(c_rho) * BAR_MULTIPLIER)}
                for p in sorted(preds)}
        part_d_by_control[label] = {
            "control_predictor": cpred,
            "control_rho": c_rho,
            "bar_abs_rho_must_exceed": bar,
            "mechanism_tests": tests,
            "n_mechanism_tests_passed": n_pass,
            "n_mechanism_tests_run": len(tests),
            "tracks_mechanism": bool(n_pass >= 2),
            "verdict": ("SENSITIVITY_TRACKS_MECHANISM" if n_pass >= 2
                        else "SENSITIVITY_DOES_NOT_TRACK_MECHANISM"),
            "specificity_all_predictors": spec,
        }

    # --- PART B under each declared control ---------------------------------------------------
    part_b = art["part_b_emc_tumour_signature"]
    readable = part_b["platforms_with_a_readable_EMC_vs_comparator_contrast"]
    con = inputs["gene_sets"]["concepts"]
    tested_concepts = [c for c, r in con.items() if r.get("role") == "tested" and r.get("genes")]
    ctrl_up = part_b["unrelated_control_concepts_elevated"]

    part_b_by_control = {}
    for label, cset in (("C0_incumbent_proliferation_MYC_only", ["proliferation_MYC"]),
                        ("C1_primary_proliferation_mitotic_only", ["proliferation_mitotic"]),
                        ("C2_committed_behaviour_BOTH_the_mean",
                         ["proliferation_MYC", "proliferation_mitotic"])):
        deltas = {}
        for mf in readable:
            pp = part_b["per_platform"][mf]
            sc = pp["scores"]
            classes = [s["class"] for s in pp["sample_annotations_verbatim"]]
            n_s = len(classes)
            emc = [i for i, c in enumerate(classes) if c == "EMC"]
            comp = [i for i, c in enumerate(classes)
                    if c not in ("EMC", "unclassified", "normal_or_reference")]
            rows = [sc[c] for c in cset if c in sc]
            pr = [_mean([r[i] for r in rows]) for i in range(n_s)]
            for c in tested_concepts:
                row = sc.get(c)
                if not row:
                    continue
                adj = [None if (row[i] is None or pr[i] is None) else round(row[i] - pr[i], 4)
                       for i in range(n_s)]
                a = [adj[i] for i in emc if adj[i] is not None]
                b = [adj[i] for i in comp if adj[i] is not None]
                if len(a) < 3 or len(b) < 3:
                    continue
                w = _welch(a, b)
                if w and w.get("delta_a_minus_b") is not None:
                    deltas.setdefault(c, []).append(w["delta_a_minus_b"])
        pooled = {c: round(_mean(v), 4) for c, v in deltas.items()}
        up = [c for c in tested_concepts if pooled.get(c, 0) > 0.2]
        part_b_by_control[label] = {
            "control_concepts_subtracted": cset,
            "pooled_proliferation_adjusted_delta": pooled,
            "ddr_concepts_elevated_after_proliferation_adjustment": up,
            "unrelated_control_concepts_elevated": ctrl_up,
            "n_unrelated_controls_elevated": len(ctrl_up),
            "signature_specific_to_DDR": bool(up) and len(ctrl_up) <= 1,
            "⭐ which_clause_fails": [k for k, ok in (
                ("a DDR concept survives adjustment", bool(up)),
                ("at most one unrelated control is elevated", len(ctrl_up) <= 1)) if not ok],
        }

    # --- the grading tier each combination implies --------------------------------------------
    tiers = {}
    for dlabel, dres in part_d_by_control.items():
        for blabel, bres in part_b_by_control.items():
            res2 = {
                "part_a_hemcss_identity": art["part_a_hemcss_identity"],
                "part_c_coordinated_dependency": art["part_c_coordinated_dependency"],
                "part_b_emc_tumour_signature": {
                    **part_b, "signature_specific_to_DDR": bres["signature_specific_to_DDR"]},
                "part_d_drug_response_correlation": {
                    **part_d, "tracks_mechanism": dres["tracks_mechanism"],
                    "verdict": dres["verdict"]},
            }
            g = grade(res2)
            tiers[f"partD={dlabel} | partB={blabel}"] = {
                "tier": g["tier"], "predicates": g["predicates"]}

    return {
        "_status": "COMPUTED",
        "reproduction_check": repro,
        "validity_check": validity,
        "part_d_by_control": part_d_by_control,
        "part_b_by_control": part_b_by_control,
        "grading_tier_under_every_combination": tiers,
    }
