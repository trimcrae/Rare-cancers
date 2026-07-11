#!/usr/bin/env python3
"""NR4A3 ternary-cooperativity RETROSPECTIVE-BAR GATE (prereg §3 as-written).

Implements `nr4a3-ternary-coop-prereg.md` §3 (and its machine-readable copy
`nr4a3-ternary-coop-prereg.json → retrospective_bar`) EXACTLY as an automated, auditable pass/fail. This is
the STAGE-3 GATE: no prospective NR4A3 ternary ranking is trusted until ALL of technical convergence + the
quantitative VHL panel + the NR-V04 affinity control + the NR4A family transfer PASS. Encoding the frozen
thresholds here (and testing them) is what stops any criterion being re-decided post-hoc on a favorable
number — the same discipline as `abfe_repair_gate.py` for Track A.

Design (mirrors abfe_repair_gate.py):
  * PURE stdlib. It evaluates a RESULTS DICT (whatever the ternary pilot/fleet analyzer emits), not raw MD —
    so it imports and unit-tests with no numpy/MD stack (absent in the dev sandbox). At Stage 0 there is no
    results dict yet; this module + its tests lock the criteria in advance.
  * Thresholds are read from the FROZEN JSON (single source of truth), overridable per call only for tests.
    A drift between the JSON and this code is caught by the tests, not silently accepted.
  * Every sub-gate returns {passed, available, detail}; `available=False` (verdict None) when the results
    dict does not yet carry the fields a criterion needs — never a false PASS/FAIL from missing data.

The results-dict schema this gate expects (all optional until the relevant stage runs) is documented in
`expected_results_schema()`; the analyzer that eventually produces ternary numbers must populate it.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN_JSON = os.path.join(HERE, "nr4a3-ternary-coop-prereg.json")


# =============================================================================================================
# frozen thresholds (single source of truth = the prereg JSON)
# =============================================================================================================
def load_frozen(path=FROZEN_JSON):
    with open(path) as f:
        return json.load(f)["retrospective_bar"]


def _num(x):
    """Coerce to float or None (results may carry null for a not-yet-computed field)."""
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _deferred(name, missing):
    return {"passed": None, "available": False,
            "note": "sub-gate '%s' deferred: results dict missing %s" % (name, missing)}


# =============================================================================================================
# sub-gate 1 — technical convergence (per free-energy leg)
# =============================================================================================================
def gate_technical_convergence(results, bar):
    """§3a. Every decision-bearing leg must satisfy all technical criteria. `results['legs']` is a list of
    per-leg dicts: {name, n_replicas, hysteresis_kcal (or cycle_closure_kcal), ci95_half_width_kcal,
    n_starting_poses, rank_reversal_under_loo (bool), pathology (bool or falsy)}."""
    c = bar["technical_convergence"]
    legs = results.get("legs")
    if not legs:
        return _deferred("technical_convergence", "results['legs']")
    failures = []
    for leg in legs:
        name = leg.get("name", "?")
        reps = leg.get("n_replicas")
        hyst = _num(leg.get("hysteresis_kcal"))
        if hyst is None:
            hyst = _num(leg.get("cycle_closure_kcal"))
        ci = _num(leg.get("ci95_half_width_kcal"))
        poses = leg.get("n_starting_poses")
        reasons = []
        if reps is None or reps < c["min_replicas_per_leg"]:
            reasons.append("n_replicas=%s < %d" % (reps, c["min_replicas_per_leg"]))
        if hyst is None or hyst > c["cycle_closure_or_hysteresis_kcal_max"]:
            reasons.append("hysteresis/closure=%s > %.2f" % (hyst, c["cycle_closure_or_hysteresis_kcal_max"]))
        if ci is None or ci > c["ci95_half_width_kcal_max"]:
            reasons.append("ci95_half_width=%s > %.2f" % (ci, c["ci95_half_width_kcal_max"]))
        if poses is None or poses < c["min_independent_starting_poses_per_architecture"]:
            reasons.append("n_starting_poses=%s < %d" % (poses, c["min_independent_starting_poses_per_architecture"]))
        if leg.get("rank_reversal_under_loo"):
            reasons.append("rank_reversal_under_leave_one_pose_out=True")
        if leg.get("pathology"):
            reasons.append("restraint/mapping/microstate pathology flagged")
        if reasons:
            failures.append({"leg": name, "reasons": reasons})
    return {"passed": not failures, "available": True, "n_legs": len(legs), "failures": failures}


# =============================================================================================================
# sub-gate 2 — quantitative VHL panel (Layer 1)
# =============================================================================================================
def _kendall_tau(pred_rank, meas_rank):
    """Kendall tau-a on two equal-length rankings (pure). Concordant-minus-discordant over all pairs."""
    n = len(pred_rank)
    if n < 2 or len(meas_rank) != n:
        return None
    conc = disc = 0
    for i in range(n):
        for j in range(i + 1, n):
            a = pred_rank[i] - pred_rank[j]
            b = meas_rank[i] - meas_rank[j]
            s = a * b
            if s > 0:
                conc += 1
            elif s < 0:
                disc += 1
    denom = n * (n - 1) / 2.0
    return (conc - disc) / denom if denom else None


def gate_vhl_panel(results, bar):
    """§3b. `results['vhl_panel']` = {n_systems, n_class_correct, predicted_alpha:[...], measured_alpha:[...],
    inactive_stereo_control_classified_competent (bool), survives_leave_one_compound_out (bool)}."""
    c = bar["vhl_panel"]
    p = results.get("vhl_panel")
    if not p:
        return _deferred("vhl_panel", "results['vhl_panel']")
    reasons = []
    n_sys = p.get("n_systems")
    n_correct = p.get("n_class_correct")
    if n_sys is None or n_correct is None:
        return _deferred("vhl_panel", "n_systems / n_class_correct")
    # criterion is >=5 of 6; scale proportionally if a larger panel is used (never weaker than 5/6).
    need = max(c["correct_cooperativity_class_min_of_6"],
               int(math.ceil(c["correct_cooperativity_class_min_of_6"] / 6.0 * n_sys)))
    if n_correct < need:
        reasons.append("class-correct %d/%d < required %d" % (n_correct, n_sys, need))

    pred = p.get("predicted_alpha")
    meas = p.get("measured_alpha")
    tau = None
    if pred and meas and len(pred) == len(meas) and len(pred) >= 2:
        # rank by value (ties broken by index; monotonic transform-invariant for tau)
        pr = _rank(pred)
        mr = _rank(meas)
        tau = _kendall_tau(pr, mr)
        if tau is None or tau < c["kendall_tau_min"]:
            reasons.append("kendall_tau=%s < %.2f" % (tau, c["kendall_tau_min"]))
    else:
        reasons.append("predicted_alpha/measured_alpha missing or too short for Kendall tau")

    if p.get("inactive_stereo_control_classified_competent"):
        reasons.append("an inactive stereochemical control was classified ternary-competent")
    if not p.get("survives_leave_one_compound_out"):
        reasons.append("does not survive leave-one-compound-out")
    return {"passed": not reasons, "available": True, "n_systems": n_sys, "n_class_correct": n_correct,
            "required_class_correct": need, "kendall_tau": tau, "failures": reasons}


def _rank(vals):
    """Ascending competition rank (1 = smallest). Pure; ties share the average index-based rank."""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    rank = [0] * len(vals)
    for pos, i in enumerate(order):
        rank[i] = pos + 1
    return rank


# =============================================================================================================
# sub-gate 3 — NR-V04 affinity control (Layer 2 — the two things the co-fold failed)
# =============================================================================================================
def gate_nrv04_affinity_control(results, bar):
    """§3c. `results['nrv04_affinity_control']` = {active_vs_epimer_binary_vhl_kcal,
    binary_vhl_ci_low, binary_vhl_ci_high, active_vs_epimer_effective_ternary_kcal,
    any_retained_pose_reverses (bool)}. Sign convention: MORE-FAVORABLE-active is a POSITIVE margin
    (active bound more strongly than epimer by this many kcal/mol)."""
    c = bar["nrv04_affinity_control"]
    r = results.get("nrv04_affinity_control")
    if not r:
        return _deferred("nrv04_affinity_control", "results['nrv04_affinity_control']")
    reasons = []
    bin_margin = _num(r.get("active_vs_epimer_binary_vhl_kcal"))
    if bin_margin is None or bin_margin < c["active_vs_epimer_binary_vhl_min_kcal"]:
        reasons.append("binary VHL active-vs-epimer margin=%s < %.1f" %
                       (bin_margin, c["active_vs_epimer_binary_vhl_min_kcal"]))
    lo = _num(r.get("binary_vhl_ci_low"))
    hi = _num(r.get("binary_vhl_ci_high"))
    if c["active_vs_epimer_binary_vhl_ci_excludes_zero"]:
        if lo is None or hi is None or not (lo > 0 or hi < 0):
            reasons.append("binary VHL CI [%s, %s] does not exclude zero" % (lo, hi))
    ter_margin = _num(r.get("active_vs_epimer_effective_ternary_kcal"))
    if ter_margin is None or ter_margin < c["active_vs_epimer_effective_ternary_min_kcal"]:
        reasons.append("effective-ternary active-vs-epimer margin=%s < %.1f" %
                       (ter_margin, c["active_vs_epimer_effective_ternary_min_kcal"]))
    if r.get("any_retained_pose_reverses"):
        reasons.append("a retained pose reverses the active/epimer ordering")
    return {"passed": not reasons, "available": True,
            "binary_margin_kcal": bin_margin, "ternary_margin_kcal": ter_margin, "failures": reasons}


# =============================================================================================================
# sub-gate 4 — NR4A family transfer (Layer 2)
# =============================================================================================================
def gate_nr4a_family_transfer(results, bar):
    """§3d. `results['nr4a_family_transfer']` = {
        recruit_diff_nr4a1_vs_nr4a2_kcal, ci_lo/hi for it,
        recruit_diff_nr4a1_vs_nr4a3_kcal, ci_lo/hi for it,
        joint_prob_nr4a1_best, survives_pose_and_conformer_sensitivity (bool)}.
    Sign: POSITIVE = NR4A1 favored over the paralogue by that many kcal/mol."""
    c = bar["nr4a_family_transfer"]
    r = results.get("nr4a_family_transfer")
    if not r:
        return _deferred("nr4a_family_transfer", "results['nr4a_family_transfer']")
    reasons = []
    for para, key in (("NR4A2", "nr4a2"), ("NR4A3", "nr4a3")):
        d = _num(r.get("recruit_diff_nr4a1_vs_%s_kcal" % key))
        lo = _num(r.get("recruit_diff_nr4a1_vs_%s_ci_lo" % key))
        hi = _num(r.get("recruit_diff_nr4a1_vs_%s_ci_hi" % key))
        if d is None or d < c["each_difference_min_kcal"]:
            reasons.append("NR4A1 vs %s recruit diff=%s < %.1f (NR4A1 not favored enough)" %
                           (para, d, c["each_difference_min_kcal"]))
        # each_difference_interval_pct_excludes_zero: the (e.g. 90%) interval must be entirely > 0
        if lo is None or lo <= 0:
            reasons.append("NR4A1 vs %s %d%% interval [%s, %s] does not exclude zero on the favored side" %
                           (para, c["each_difference_interval_pct_excludes_zero"], lo, hi))
    jp = _num(r.get("joint_prob_nr4a1_best"))
    if jp is None or jp <= c["joint_prob_nr4a1_best_min"]:
        reasons.append("joint P(NR4A1 best)=%s <= %.2f" % (jp, c["joint_prob_nr4a1_best_min"]))
    if not r.get("survives_pose_and_conformer_sensitivity"):
        reasons.append("does not survive starting-pose and conformer-panel sensitivity")
    return {"passed": not reasons, "available": True, "joint_prob_nr4a1_best": jp, "failures": reasons}


# =============================================================================================================
# top-level gate
# =============================================================================================================
def evaluate_retrospective_bar(results, frozen_path=FROZEN_JSON):
    """Evaluate prereg §3 on a ternary results dict → per-sub-gate pass/fail + an overall
    `prospective_ranking_authorized` verdict. Verdict is True only if ALL four sub-gates PASS; False if any
    available sub-gate FAILS; None if any sub-gate is deferred (results not yet present) and none has failed."""
    bar = load_frozen(frozen_path)
    subs = {
        "technical_convergence": gate_technical_convergence(results, bar),
        "vhl_panel": gate_vhl_panel(results, bar),
        "nrv04_affinity_control": gate_nrv04_affinity_control(results, bar),
        "nr4a_family_transfer": gate_nr4a_family_transfer(results, bar),
    }
    any_fail = any(s.get("passed") is False for s in subs.values())
    any_deferred = any(s.get("passed") is None for s in subs.values())
    if any_fail:
        verdict = False
    elif any_deferred:
        verdict = None
    else:
        verdict = True
    return {
        "prospective_ranking_authorized": verdict,
        "sub_gates": subs,
        "failure_semantics": bar["failure_semantics"],
        "prereg": "nr4a3-ternary-coop-prereg.md §3 / .json retrospective_bar",
    }


def expected_results_schema():
    """The results-dict shape the analyzer must populate (documentation for the future producer)."""
    return {
        "legs": [{"name": "str", "n_replicas": "int", "hysteresis_kcal": "float|null",
                  "cycle_closure_kcal": "float|null", "ci95_half_width_kcal": "float",
                  "n_starting_poses": "int", "rank_reversal_under_loo": "bool", "pathology": "bool"}],
        "vhl_panel": {"n_systems": "int", "n_class_correct": "int", "predicted_alpha": "[float]",
                      "measured_alpha": "[float]", "inactive_stereo_control_classified_competent": "bool",
                      "survives_leave_one_compound_out": "bool"},
        "nrv04_affinity_control": {"active_vs_epimer_binary_vhl_kcal": "float", "binary_vhl_ci_low": "float",
                                   "binary_vhl_ci_high": "float",
                                   "active_vs_epimer_effective_ternary_kcal": "float",
                                   "any_retained_pose_reverses": "bool"},
        "nr4a_family_transfer": {"recruit_diff_nr4a1_vs_nr4a2_kcal": "float",
                                 "recruit_diff_nr4a1_vs_nr4a2_ci_lo": "float",
                                 "recruit_diff_nr4a1_vs_nr4a2_ci_hi": "float",
                                 "recruit_diff_nr4a1_vs_nr4a3_kcal": "float",
                                 "recruit_diff_nr4a1_vs_nr4a3_ci_lo": "float",
                                 "recruit_diff_nr4a1_vs_nr4a3_ci_hi": "float",
                                 "joint_prob_nr4a1_best": "float",
                                 "survives_pose_and_conformer_sensitivity": "bool"},
    }


def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="NR4A3 ternary-cooperativity retrospective-bar gate (prereg §3).")
    ap.add_argument("results_json", nargs="?", help="a ternary results dict (JSON). Omit to print the schema.")
    ap.add_argument("--json", action="store_true", help="print the full result dict as JSON")
    args = ap.parse_args(argv)
    if not args.results_json:
        print(json.dumps(expected_results_schema(), indent=2))
        return 0
    with open(args.results_json) as f:
        results = json.load(f)
    res = evaluate_retrospective_bar(results)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        for name, s in res["sub_gates"].items():
            p = s.get("passed")
            tag = "PASS" if p is True else ("FAIL" if p is False else "N/A ")
            print("  [%s] %s" % (tag, name))
            for fl in s.get("failures", []) or []:
                print("        - %s" % fl)
            if s.get("note"):
                print("        note: %s" % s["note"])
        v = res["prospective_ranking_authorized"]
        print("  => prospective_ranking_authorized = %s" % v)
    v = res["prospective_ranking_authorized"]
    return 0 if v is True else (2 if v is None else 1)


if __name__ == "__main__":
    sys.exit(_cli())
