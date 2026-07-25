#!/usr/bin/env python3
"""INDEPENDENT AUDIT of the valB_mini calibration gate + its 2026-07-25 admits-zero defect fix.

Why this exists. The defect fix was applied in place (commit 3f11cbf5, delegated reviewer authority) with three
claims attached: that it is *strictly stricter in every direction*, that it *changes no recorded verdict*, and
that it restores discrimination between an accurate method and a null one. Those are exactly the claims a
post-hoc retune would also make, so they must be **re-derived, not read**. Every number this script prints is
computed by calling the shipped `ternary_fep_reduce.calibration_gate` — the production function, both with the
corrected rule and (via the audit switch) with the superseded one — never a reimplementation of it.

Five audits:
  A. MONOTONE STRICTNESS, exhaustively. Over a dense grid of replicate sets, no input may receive a BETTER
     verdict under the corrected rule than under the superseded one. A single counterexample falsifies
     "strictly stricter" and would make the amendment a retune.
  B. THE NULL. Reproduce, independently, that the superseded rule passes a zero-signal method, and measure what
     the corrected rule does to that rate.
  C. NO SELF-RESCUE. Conditioned on the real r0 = -0.534, the corrected rule must not make the failing result
     easier to pass than the superseded rule did. This is the test a retune fails.
  D. THE ACCEPTANCE BAND. What ΔΔG_coop values does a PASS actually certify? Reported in absolute kcal/mol and
     as a fraction of the target — the quantity that decides whether this calibrator can certify anything.
  E. DISCRIMINATION vs CALIBRATOR SIGNAL SIZE. Sweep the target from 0.5 to 3.5 kcal/mol at fixed replicate
     noise and fixed ±1.0 accuracy margin, and report P(PASS | accurate) vs P(PASS | null). This is the
     quantitative case for (or against) rescoping the calibrator, computed rather than asserted.

$0, CPU, deterministic (fixed seeds). Writes valb-gate-audit.json beside itself.
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ternary_fep_reduce as red  # noqa: E402

AUDIT_E = {"rows": []}

TARGET = 0.944          # preregistered: -RT ln(2.6/12.8), Wurz 2023 cmpd 1 -> 4
R0 = -0.534             # the real first replicate
RANK = {"FAIL": 0, "INDETERMINATE": 1, "BORDERLINE": 2, "PASS": 3}
TRIALS = 40000


def verdict(vals, extended=False, anti_null=None):
    return red.calibration_gate(list(vals), TARGET, diagnostics_ok=True, extended=extended,
                                anti_null=anti_null)["decision"]


# ---------------------------------------------------------------- A. monotone strictness
def audit_strictness():
    """Exhaustive over a grid: the corrected verdict must never RANK ABOVE the superseded one.

    The grid is built to hit every branch, not to be large for its own sake: means spanning the FAIL/BORDERLINE/
    PASS bands including both boundaries, and SDs spanning 0 through past the extension ceiling. Replicate sets
    are constructed to have EXACTLY the intended mean and sample SD, so each grid point probes a known
    (mean, SD) rather than a random draw."""
    worse, checked, improved = [], 0, 0
    means = [round(-2.0 + 0.02 * i, 3) for i in range(301)]          # -2.00 .. +4.00
    sds = [0.0, 0.05, 0.1, 0.2, 0.24, 0.25, 0.26, 0.4, 0.5, 0.7, 0.74, 0.75, 0.76, 0.9, 1.0, 1.01, 1.5]
    for n in (3, 5):
        for ext in (False, True):
            for m in means:
                for sd in sds:
                    # a set of n values with sample SD exactly `sd` and mean exactly `m`
                    if n == 3:
                        vals = [m - sd, m, m + sd]                    # sample SD = sd
                    else:
                        d = sd * (2.0 ** 0.5)                         # n=5: sample SD = sd
                        vals = [m - d, m, m, m, m + d]
                    old = verdict(vals, extended=ext, anti_null=False)
                    new = verdict(vals, extended=ext, anti_null=True)
                    checked += 1
                    if RANK[new] > RANK[old]:
                        worse.append({"n": n, "extended": ext, "mean": m, "sd": sd, "old": old, "new": new})
                    elif RANK[new] < RANK[old]:
                        improved += 1
    return {"_claim": "the corrected rule is STRICTLY STRICTER: no input gets a better verdict than before",
            "grid_points_checked": checked,
            "points_where_corrected_is_MORE_permissive": len(worse),
            "counterexamples": worse[:10],
            "points_where_corrected_is_stricter": improved,
            "verdict": ("CLAIM HOLDS — zero counterexamples over %d grid points" % checked) if not worse
                       else "CLAIM FALSIFIED — the amendment is not monotone and must be treated as a retune"}


# ---------------------------------------------------------------- B/C. Monte Carlo
def _mc(mu, sd, n, seed, extended, anti_null, hold_r0=False):
    rng = random.Random(seed)
    out = {"PASS": 0, "BORDERLINE": 0, "FAIL": 0, "INDETERMINATE": 0}
    for _ in range(TRIALS):
        vals = ([R0] if hold_r0 else []) + [rng.gauss(mu, sd) for _ in range(n - (1 if hold_r0 else 0))]
        out[verdict(vals, extended=extended, anti_null=anti_null)] += 1
    return {k: round(100.0 * v / TRIALS, 2) for k, v in out.items()}


def audit_null_and_accuracy():
    rows = []
    for sd in (0.3, 0.5, 0.7, 1.0):
        for label, mu in (("accurate (mu = target)", TARGET), ("NULL (mu = 0)", 0.0),
                          ("half-signal (mu = target/2)", TARGET / 2.0),
                          ("2x overshoot (mu = 2*target)", 2 * TARGET)):
            rows.append({"replicate_sd": sd, "scenario": label, "mu": round(mu, 3), "n": 5, "extended": True,
                         "superseded_rule": _mc(mu, sd, 5, 11, True, False),
                         "corrected_rule": _mc(mu, sd, 5, 11, True, True)})
    disc = []
    for sd in (0.3, 0.5, 0.7, 1.0):
        acc_o = _mc(TARGET, sd, 5, 11, True, False)["PASS"]
        nul_o = _mc(0.0, sd, 5, 11, True, False)["PASS"]
        acc_n = _mc(TARGET, sd, 5, 11, True, True)["PASS"]
        nul_n = _mc(0.0, sd, 5, 11, True, True)["PASS"]
        disc.append({"replicate_sd": sd,
                     "superseded": {"pass_accurate_pct": acc_o, "pass_null_pct": nul_o,
                                    "discrimination_ratio": (round(acc_o / nul_o, 2) if nul_o else None)},
                     "corrected": {"pass_accurate_pct": acc_n, "pass_null_pct": nul_n,
                                   "discrimination_ratio": (round(acc_n / nul_n, 2) if nul_n else None)}})
    return {"_claim": "the superseded rule admits the null; the corrected rule restores discrimination",
            "n_trials_per_cell": TRIALS, "scenarios": rows, "discrimination": disc}


def audit_no_self_rescue():
    """THE INTEGRITY TEST. A fix that happens to rescue its author's failing result is indistinguishable from a
    retune. Conditioned on the real r0 = -0.534 being held in the replicate set, the corrected rule must not
    make a PASS easier than the superseded rule did — at any n, at any noise level."""
    rows = []
    for n in (3, 5):
        for sd in (0.3, 0.5, 0.7, 1.0):
            for label, mu in (("method exactly right", TARGET), ("r0 is representative", R0), ("null", 0.0)):
                o = _mc(mu, sd, n, 23, n >= 5, False, hold_r0=True)
                c = _mc(mu, sd, n, 23, n >= 5, True, hold_r0=True)
                rows.append({"n_including_r0": n, "replicate_sd": sd, "remaining_replicates_drawn_from": label,
                             "superseded_PASS_pct": o["PASS"], "corrected_PASS_pct": c["PASS"],
                             "corrected_is_not_easier": c["PASS"] <= o["PASS"]})
    # and the exhaustive n=3 scan the r0 verdict already ran, re-run under BOTH rules
    scan = {"old_PASS": 0, "new_PASS": 0, "cells": 0}
    g = [round(-4.0 + 0.05 * i, 2) for i in range(241)]
    for r1 in g:
        for r2 in g:
            scan["cells"] += 1
            if verdict([R0, r1, r2], anti_null=False) == "PASS":
                scan["old_PASS"] += 1
            if verdict([R0, r1, r2], anti_null=True) == "PASS":
                scan["new_PASS"] += 1
    return {"_claim": "the fix does not rescue the failing result — it cannot, being monotone",
            "r0_held_kcal": R0, "conditional_monte_carlo": rows,
            "all_rows_satisfy_not_easier": all(r["corrected_is_not_easier"] for r in rows),
            "exhaustive_n3_scan_over_r1_r2": scan,
            "r0_alone_verdict": {"superseded": red.calibration_gate([R0], TARGET, anti_null=False)["decision"],
                                 "corrected": red.calibration_gate([R0], TARGET, anti_null=True)["decision"]}}


# ---------------------------------------------------------------- D. what a PASS certifies
def audit_acceptance_band():
    """The interval of MEAN ΔΔG_coop that can receive a PASS, found by bisection against the real gate at
    negligible SD (SD -> 0 is the most permissive case, so this is the widest the band ever gets)."""
    def passes(m):
        return verdict([m - 1e-4, m, m + 1e-4], extended=True) == "PASS"

    lo, hi = 0.0, TARGET
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        (lo, hi) = (mid, hi) if not passes(mid) else (lo, mid)
    low_edge = hi
    lo, hi = TARGET, 6.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        (lo, hi) = (lo, mid) if not passes(mid) else (mid, hi)
    high_edge = lo
    return {"_what": "range of mean ddG_coop that a PASS certifies, at vanishing replicate SD (widest case)",
            "target_kcal": TARGET, "accept_low_kcal": round(low_edge, 4), "accept_high_kcal": round(high_edge, 4),
            "band_width_kcal": round(high_edge - low_edge, 4),
            "band_width_as_multiple_of_target": round((high_edge - low_edge) / TARGET, 2),
            "accept_low_as_fraction_of_target": round(low_edge / TARGET, 3),
            "accept_high_as_fraction_of_target": round(high_edge / TARGET, 3),
            "reading": ("a PASS certifies the method's ddG_coop to within roughly a FACTOR OF %.1f of the true "
                        "value — because the preregistered accuracy margin (+-1.0 kcal/mol) is larger than the "
                        "signal being calibrated (%.3f kcal/mol). The defect fix removed the null from the low "
                        "side; it could not make a 1.0 kcal/mol margin informative about a 0.944 kcal/mol effect."
                        % ((high_edge / low_edge) if low_edge else float("inf"), TARGET))}


# ---------------------------------------------------------------- E. discrimination vs signal size
def audit_signal_size_sweep():
    """Hold the accuracy margin (+-1.0) and the replicate noise fixed; sweep the CALIBRATOR's true signal. This
    is the quantitative form of the rescope question: at what target does this gate start to distinguish a
    working method from a null one with useful power?"""
    rows = []
    for tgt in (0.5, 0.944, 1.25, 1.5, 2.0, 2.53, 2.99, 3.5):
        for sd in (0.5, 0.7):
            rng_seed = 97
            def mc(mu):
                rng = random.Random(rng_seed)
                p = 0
                for _ in range(TRIALS):
                    vals = [rng.gauss(mu, sd) for _ in range(5)]
                    if red.calibration_gate(vals, tgt, extended=True)["decision"] == "PASS":
                        p += 1
                return round(100.0 * p / TRIALS, 2)
            acc, nul = mc(tgt), mc(0.0)
            rows.append({"target_kcal": tgt, "replicate_sd": sd, "n": 5,
                         "pass_accurate_pct": acc, "pass_null_pct": nul,
                         "discrimination_ratio": (round(acc / nul, 1) if nul else "inf"),
                         "accept_band_as_fraction_of_target": round(2.0 / tgt, 2)})
    return {"_what": "P(PASS) for an accurate vs a null method, as a function of the calibrator's true signal, "
                     "at the FROZEN +-1.0 kcal/mol accuracy margin and the corrected anti-null rule",
            "_why": "the accuracy margin is absolute, so a larger true signal shrinks the accept band RELATIVE "
                    "to the effect and the same gate becomes informative. This is the arithmetic behind the "
                    "proposal to rescope the calibrator to >=2 kcal/mol.",
            "rows": rows}


# ---------------------------------------------------------------- F. the power ceiling, analytically
def _chi2_cdf_dof4(x):
    """Exact CDF of chi-square with 4 dof: 1 - (1 + x/2) e^(-x/2). Closed form, no scipy."""
    return 0.0 if x <= 0 else 1.0 - (1.0 + x / 2.0) * math.exp(-x / 2.0)


def audit_power_ceiling():
    """WHY THE SWEEP IN E PLATEAUS — and a check that the Monte Carlo measured what it claims to.

    PASS requires the between-replicate sample SD <= 0.75. At n=5 the sample variance is chi-square distributed
    with 4 dof, so for a method with TRUE replicate SD sigma the probability of clearing that requirement is
    exactly P(chi2_4 <= 4*(0.75/sigma)^2) — a number that has nothing to do with the calibrator's signal size.
    That is the ceiling on P(PASS) for ANY method, however accurate, at ANY target.

    This is the load-bearing consequence for the rescope: past a target of about 2 kcal/mol the accuracy margin
    stops binding and the ONLY remaining lever is the replicate SD. A design that shrinks cycle SD (shared legs,
    redundant edges, cycle closure) then buys more than a bigger signal does.

    It is also a discriminating check on audit E: if the empirical plateau did not match this closed form, the
    Monte Carlo would be measuring something other than the gate."""
    rows = []
    for sd in (0.3, 0.5, 0.7, 1.0):
        analytic = _chi2_cdf_dof4(4.0 * (red.GATE_CYCLE_SD_PASS / sd) ** 2)
        empirical = max(r["pass_accurate_pct"] for r in
                        (x for x in AUDIT_E["rows"] if x["replicate_sd"] == sd)) if any(
                            x["replicate_sd"] == sd for x in AUDIT_E["rows"]) else None
        rows.append({"true_replicate_sd": sd,
                     "analytic_ceiling_pct": round(100.0 * analytic, 2),
                     "empirical_plateau_pct_from_audit_E": empirical,
                     "agree_within_1pct": (None if empirical is None else abs(100.0 * analytic - empirical) < 1.0)})
    return {"_what": "P(PASS) ceiling = P(sample SD <= %.2f) at n=5, independent of target and of accuracy"
                     % red.GATE_CYCLE_SD_PASS,
            "_consequence": "beyond a target of ~2 kcal/mol the accuracy margin no longer binds; the replicate "
                            "SD alone sets the achievable power, so precision design beats a bigger signal there",
            "rows": rows}


def main():
    global AUDIT_E
    AUDIT_E = audit_signal_size_sweep()
    report = {
        "_what": "independent audit of ternary_fep_reduce.calibration_gate and its 2026-07-25 defect fix",
        "_method": "every verdict comes from the SHIPPED gate; the superseded rule is reproduced via the "
                   "audit-only anti_null=False switch, not by reimplementation",
        "_date": "2026-07-25", "target_kcal": TARGET, "r0_kcal": R0,
        "A_monotone_strictness": audit_strictness(),
        "B_null_and_accuracy": audit_null_and_accuracy(),
        "C_no_self_rescue": audit_no_self_rescue(),
        "D_acceptance_band": audit_acceptance_band(),
        "E_signal_size_sweep": AUDIT_E,
        "F_power_ceiling": audit_power_ceiling(),
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "valb-gate-audit.json")
    json.dump(report, open(out, "w"), indent=2)
    print(json.dumps({k: v for k, v in report.items() if k.startswith(("A_", "D_"))}, indent=2)[:4000])
    print("\n[audit] wrote %s" % out)
    return report


if __name__ == "__main__":
    main()
