#!/usr/bin/env python3
"""
NR-V04 RETROSPECTIVE — degeneracy + power audit of the FROZEN criteria ($0, pure stdlib).

WHY. Prereg AMENDMENT 1 (covalent feasibility panel, 2026-07-25) retired a gating criterion after measuring
that its statistic had **zero discriminating power**: `frac_frames_in_contact` returned one distinct value
(1.0) across all 18 legs *including both negative controls*. A statistic with no variance across the contrast
cannot score the contrast. This script applies the SAME test to the retrospective's frozen criteria
(`nr4a3-nrv04-retrospective-prereg.md` 3-5, executed by `nrv04_retro_gate.py`), BEFORE any leg runs:

  for each criterion — what values can it take, can its controls actually fail it, and is it
  satisfiable-by-construction?

Four things are computed, all by exhaustive enumeration or Monte-Carlo against MEASURED noise, never by
assertion:

  1. ATTAINABLE p-VALUES. The primary test is an exact permutation test over C(9,3) = 84 arrangements, so its
     p-value lives on the 84-point lattice k/84. The extension rule (4d) fires on p in (0.012, 0.05]. This
     enumerates which lattice points fall in that window and cross-references them against the CONCORDANT
     condition p <= 0.05.

  2. THE PRIMARY STATISTIC IS A RANK STATISTIC. With 3 vs 6 and a pooled total S,
        d = mean(A) - mean(B) = a/3 - (S-a)/6 = a/2 - S/6
     is strictly increasing in a = sum(A). So the exact test is EXACTLY a test on the rank of the NR4A1 trio's
     sum among the 84 subset sums. Verified numerically here, because it determines what evidence the test can
     ever see (only the ordering of subset sums — not the effect size).

  3. IS THE LEAVE-ONE-MODEL-OUT CLAUSE INERT? CONCORDANT requires p <= alpha AND LOMO survival. If LOMO can
     never fail when p <= alpha, the clause cannot downgrade anything and the WEAKLY_CONCORDANT branch that
     depends on it is unreachable. Searched adversarially rather than assumed.

  4. POWER / MINIMUM DETECTABLE EFFECT against MEASURED noise. The prereg registers a null R1 as an
     informative, publishable outcome (5c). That is only true if the test could have detected a real effect.
     Monte-Carlo over the frozen decision rule gives the true paralogue separation (in A of interface-RMSD
     plateau) needed for 80% power at n = 3 models/arm — computed against the leg-to-leg spread MEASURED on the
     feasibility panel, which is a LOWER BOUND on the retrospective's model-level noise (those legs were
     velocity replicas of ONE co-fold model; the retrospective's models additionally differ structurally).

Emits `nrv04-retro-criteria-audit.json`. Never launches anything, never spends.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nrv04_retro_gate as gate                                            # noqa: E402  (the frozen scorer)

# Measured leg-level E1 (interface-RMSD plateau, A) from the covalent feasibility panel's committed legs, as
# recorded in nrv04-covalent-panel-recovery-2026-07-25.md 2 (read off the committed leg JSONs by
# nrv04_cofold_audit --completed-panel). Two arms x 3 velocity seeds on ONE co-fold model each. Used only if a
# live measurement is not supplied via --measured.
FALLBACK_MEASURED = {
    "cov_nr4a1": [2.561, 3.703, 5.003],
    "noncov_nr4a1": [2.938, 3.651, 5.047],
}
FALLBACK_PROVENANCE = ("nrv04-covalent-panel-recovery-2026-07-25.md 2 — per-seed plateaux read off the "
                       "committed feasibility-panel leg JSONs")


# ---------------------------------------------------------------------------------------------------------
# 1 + 2 — the p-value lattice, and the rank-statistic identity
# ---------------------------------------------------------------------------------------------------------
def p_lattice(n_primary=3, n_pooled=6):
    n = n_primary + n_pooled
    total = len(list(combinations(range(n), n_primary)))
    return total, [k / total for k in range(1, total + 1)]


def extension_rule_reachability():
    """§4d fires on p in `gate.EXTENSION_P_WINDOW`; CONCORDANT needs p <= alpha. Which attainable p-values are
    in the window, and are any of them OUTSIDE the CONCORDANT region — i.e. does the rule ever fire in the case
    its own text describes ('the ordering is right but n = 3 cannot resolve it')?

    ⚠ THE WINDOW IS READ FROM THE GATE, NEVER TYPED HERE. This function's original docstring hard-coded
    `(0.012, 0.05]`, which is the window AMENDMENT 3 defect 2 retired on exactly this measurement — so a typed
    copy would have gone on describing a rule the code no longer runs. Re-running this audit after the
    amendment must produce a DIFFERENT, correct finding, not the same sentence."""
    total, lattice = p_lattice()
    lo, hi = gate.EXTENSION_P_WINDOW
    in_window = [round(p, 6) for p in lattice if lo < p <= hi]
    also_concordant = [p for p in in_window if p <= gate.ALPHA]
    unresolvable = [round(p, 6) for p in lattice if p > gate.ALPHA]
    return {
        "n_arrangements": total,
        "min_attainable_p": round(1.0 / total, 6),
        "alpha": gate.ALPHA,
        "extension_window": list(gate.EXTENSION_P_WINDOW),
        "attainable_p_in_extension_window": in_window,
        "of_those_also_p_le_alpha_hence_CONCORDANT": [round(p, 6) for p in also_concordant],
        "attainable_p_that_are_right_sign_but_unresolvable (p > alpha)": unresolvable[:6],
        "next_p_above_alpha": round(unresolvable[0], 6) if unresolvable else None,
        "rule_fires_only_on_results_that_already_pass": len(also_concordant) == len(in_window) and bool(in_window),
        "finding": (
            # DEGENERATE — the pre-AMENDMENT-3 state, kept so a regression re-states it rather than going quiet.
            "The extension rule's stated trigger is 'the ordering is right but n = 3 models cannot "
            "resolve it', which requires p > alpha. Every attainable p inside its window is <= alpha, "
            "so on the 84-point lattice the rule fires ONLY on results the same run already grades "
            "CONCORDANT, and NEVER on the unresolvable case it was written for (the smallest "
            "attainable p above alpha is outside the window)."
            if in_window and len(also_concordant) == len(in_window) else
            "NOT REACHABLE AT ALL: no attainable p = k/84 falls inside the window."
            if not in_window else
            # HEALTHY — every triggering p is above alpha, i.e. exactly the unresolvable case.
            "REACHABLE AND CORRECTLY SCOPED: %d attainable p-value(s) fall inside the window and %d of them "
            "are <= alpha, so the rule fires on the right-sign-but-unresolvable band its text describes and "
            "cannot fire on a result the same run already grades CONCORDANT."
            % (len(in_window), len(also_concordant))),
    }


def rank_statistic_identity(trials=4000, seed=11):
    """d = mean(A) - mean(B) is an increasing affine function of sum(A), so the exact permutation p-value is a
    rank of sum(A) among the 84 subset sums. Verified numerically on random configurations."""
    rng = random.Random(seed)
    worst = 0.0
    mismatches = 0
    for _ in range(trials):
        vals = [rng.uniform(0.5, 8.0) for _ in range(9)]
        sums = sorted(sum(c) for c in combinations(vals, 3))
        a_idx = rng.sample(range(9), 3)
        a = [vals[i] for i in a_idx]
        b = [vals[i] for i in range(9) if i not in a_idx]
        res = gate.exact_permutation_p(a, b, alternative="less")
        rank = sum(1 for s in sums if s <= sum(a) + 1e-12)
        if abs(res["p"] - rank / 84.0) > 1e-9:
            mismatches += 1
        worst = max(worst, abs(res["p"] - rank / 84.0))
    return {"trials": trials, "mismatches": mismatches, "max_abs_deviation": worst,
            "identity": "p == rank(sum(NR4A1 trio)) / 84",
            "consequence": ("the primary test sees ONLY the ordering of the 84 subset sums — an effect of 0.2 A "
                            "and an effect of 20 A that produce the same ordering produce the same p")}


# ---------------------------------------------------------------------------------------------------------
# 3 — is the LOMO clause inert given p <= alpha?
# ---------------------------------------------------------------------------------------------------------
def _means_from(a_vals, b_vals):
    """Shape a 3-vs-6 configuration into the {arm: {model_seed: value}} form the frozen gate consumes."""
    means = {gate.PRIMARY_ARM: {i + 1: v for i, v in enumerate(a_vals)},
             gate.POOLED_ARMS[0]: {i + 1: v for i, v in enumerate(b_vals[:3])},
             gate.POOLED_ARMS[1]: {i + 1: v for i, v in enumerate(b_vals[3:])}}
    return means


def lomo_inertness(trials=400000, seed=7):
    """Adversarial search for a configuration with p <= alpha, correct sign, NR4A1 below both — yet LOMO fails.
    If none exists, the LOMO clause cannot downgrade a CONCORDANT result and its WEAKLY_CONCORDANT branch is
    unreachable."""
    rng = random.Random(seed)
    counterexamples = []
    n_sig = 0
    for t in range(trials):
        # Deliberately include configurations where NR4A1 is NOT simply the three smallest values — those are
        # the only ones where LOMO could plausibly bite (p <= 4/84 admits e.g. {v1,v2,v4} and {v1,v3,v4}).
        style = t % 3
        if style == 0:
            vals = sorted(rng.uniform(0.0, 10.0) for _ in range(9))
        elif style == 1:
            vals = sorted([rng.uniform(0.0, 1.0)] + [rng.uniform(0.9, 1.2) for _ in range(8)])
        else:
            vals = sorted([rng.uniform(0.0, 0.2)] + [rng.uniform(3.0, 3.4) for _ in range(8)])
        pick = rng.choice([(0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 1, 5), (0, 2, 4), (1, 2, 3)])
        a = [vals[i] for i in pick]
        b = [vals[i] for i in range(9) if i not in pick]
        res = gate.exact_permutation_p(a, b, alternative="less")
        if res["stat"] >= 0 or res["p"] > gate.ALPHA:
            continue
        means = _means_from(a, b)
        arm_means = {arm: sum(v.values()) / len(v) for arm, v in means.items()}
        if not all(arm_means[gate.PRIMARY_ARM] < arm_means[x] for x in gate.POOLED_ARMS):
            continue
        n_sig += 1
        lomo = gate.leave_one_model_out(means)
        if not lomo["survives"]:
            counterexamples.append({"a": [round(x, 4) for x in a], "b": [round(x, 4) for x in b],
                                    "p": res["p"], "stat": round(res["stat"], 4)})
            if len(counterexamples) >= 3:
                break
    return {
        "trials": trials,
        "n_configurations_reaching_p<=alpha_with_correct_ordering": n_sig,
        "n_lomo_failures_found": len(counterexamples),
        "counterexamples": counterexamples,
        "finding": ("INERT: no configuration was found in which the frozen primary test reaches p <= alpha with "
                    "NR4A1 below both paralogues and the leave-one-model-out clause then fails. The LOMO "
                    "condition in the CONCORDANT tier therefore cannot downgrade anything, and the "
                    "WEAKLY_CONCORDANT branch reading 'correct ordering and p <= alpha, but the sign fails "
                    "leave-one-model-out' is unreachable code."
                    if not counterexamples else
                    "NOT inert — LOMO can fail at p <= alpha; see counterexamples"),
    }


# ---------------------------------------------------------------------------------------------------------
# 4 — power / minimum detectable effect against measured noise
# ---------------------------------------------------------------------------------------------------------
def _pooled_within_sd(groups):
    """Pooled within-group SD (the leg-to-leg spread of E1 with the SYSTEM held fixed)."""
    num = den = 0.0
    for vals in groups:
        if len(vals) < 2:
            continue
        m = sum(vals) / len(vals)
        num += sum((v - m) ** 2 for v in vals)
        den += len(vals) - 1
    return (num / den) ** 0.5 if den else None


def _verdict_is_concordant(a_vals, b_vals):
    """Apply the frozen decision rule exactly as nrv04_retro_gate.verdict does, on model-level values."""
    res = gate.exact_permutation_p(a_vals, b_vals, alternative="less")
    if res["stat"] >= 0 or res["p"] > gate.ALPHA:
        return False
    means = _means_from(a_vals, b_vals)
    arm_means = {arm: sum(v.values()) / len(v) for arm, v in means.items()}
    if not all(arm_means[gate.PRIMARY_ARM] < arm_means[x] for x in gate.POOLED_ARMS):
        return False
    return gate.leave_one_model_out(means)["survives"]


def power_curve(sigma_model, deltas, n_sims=3000, seed=23):
    """P(CONCORDANT) as a function of the TRUE NR4A1-vs-paralogue separation, under Gaussian model-level noise.
    delta > 0 means NR4A1's true plateau is LOWER (more stable) by delta A."""
    rng = random.Random(seed)
    out = []
    for delta in deltas:
        hits = 0
        for _ in range(n_sims):
            a = [rng.gauss(-delta, sigma_model) for _ in range(3)]
            b = [rng.gauss(0.0, sigma_model) for _ in range(6)]
            if _verdict_is_concordant(a, b):
                hits += 1
        out.append({"true_separation_A": round(delta, 3), "power": round(hits / n_sims, 4)})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="NR-V04 retrospective frozen-criteria degeneracy + power audit.")
    ap.add_argument("--measured", default="", help="nrv04-retro-prespend-audit.json (for the real E1 spread)")
    ap.add_argument("--out", default="research/modalities/nrv04-retro-criteria-audit.json")
    ap.add_argument("--sims", type=int, default=3000)
    ap.add_argument("--lomo-trials", type=int, default=400000)
    args = ap.parse_args(argv)

    doc = {"panel": "nrv04_retrospective", "prereg": "nr4a3-nrv04-retrospective-prereg.md",
           "scorer": "nrv04_retro_gate.py (frozen)",
           "test_applied": ("AMENDMENT 1's standard: a criterion may be amended only if its statistic is shown "
                            "to lack discriminating power, demonstrated independently of whether we liked the "
                            "answer. Applied here BEFORE any leg runs.")}

    doc["extension_rule"] = extension_rule_reachability()
    doc["rank_statistic"] = rank_statistic_identity()
    doc["lomo_clause"] = lomo_inertness(trials=args.lomo_trials)

    # --- measured noise ------------------------------------------------------------------------------------
    groups, provenance = [], FALLBACK_PROVENANCE
    if args.measured and os.path.exists(args.measured):
        try:
            m = json.load(open(args.measured))
            by_leg = {}
            for f in m.get("leg_results", []):
                v = f.get("driver_R1_interface_plateau_A")
                if v is None:
                    continue
                lid = (f.get("leg_id") or "?").split("__")[0]
                by_leg.setdefault((f.get("prefix"), lid), []).append(float(v))
            if by_leg:
                groups = [v for v in by_leg.values() if len(v) >= 2]
                provenance = (f"measured live from {len(by_leg)} committed leg groups in "
                              f"{args.measured} (driver key R1_interface.plateau_A)")
        except Exception as e:                                              # noqa: BLE001
            doc["measured_read_error"] = f"{type(e).__name__}: {e}"
    if not groups:
        groups = list(FALLBACK_MEASURED.values())
    sd = _pooled_within_sd(groups)
    doc["measured_noise"] = {
        "provenance": provenance,
        "groups": [[round(v, 4) for v in g] for g in groups],
        "pooled_within_system_SD_A": round(sd, 4) if sd else None,
        "why_this_is_a_LOWER_BOUND": ("these are velocity replicas with the co-fold model held FIXED. The "
                                      "retrospective's unit of independence is the co-fold MODEL (prereg 4a), "
                                      "and its model-level value is the mean of 2 replicas, so the model-level "
                                      "noise is sqrt(sigma_model^2 + sigma_rep^2/2) >= sigma_rep/sqrt(2). "
                                      "Distinct co-fold seeds of the same system differ by 3-8 A CA-RMSD "
                                      "(nrv04-covalent-panel-recovery-2026-07-25.md 3), so sigma_model is not "
                                      "plausibly zero. Both bounds are reported."),
    }

    if sd:
        deltas = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]
        for label, sigma in (("optimistic_sigma_rep_over_sqrt2", sd / (2 ** 0.5)),
                             ("sigma_equals_measured_leg_SD", sd)):
            curve = power_curve(sigma, deltas, n_sims=args.sims)
            mde80 = next((r["true_separation_A"] for r in curve if r["power"] >= 0.80), None)
            mde50 = next((r["true_separation_A"] for r in curve if r["power"] >= 0.50), None)
            doc.setdefault("power", {})[label] = {
                "sigma_model_A": round(sigma, 4),
                "curve": curve,
                "separation_for_50pct_power_A": mde50,
                "separation_for_80pct_power_A": mde80,
                "false_positive_rate_at_delta_0": curve[0]["power"],
            }

    doc["criterion_by_criterion"] = [
        {"id": "E1 (PRIMARY)", "statistic": "interface-RMSD plateau, model-level mean",
         "can_it_vary": "YES — measured 2.561-5.047 A across legs of a single system",
         "degenerate?": "no (it varies), but see `power`: its variance is comparable to any plausible "
                        "between-paralogue effect, so the TEST built on it may be near-powerless"},
        {"id": "E2 stable fraction (<4.0 A)", "role_in_prereg": "binary secondary, reported not gating",
         "computed_by_the_frozen_scorer?": "NO — nrv04_retro_gate.verdict never reads it; "
                                           "STABLE_PLATEAU_A is imported and unused",
         "degenerate?": "not gating, so it cannot corrupt the verdict; but prereg 3's promise that E2-E4 are "
                        "'reported alongside it in every result' is unimplemented in the verdict output"},
        {"id": "E3 mean interface contacts", "role_in_prereg": "secondary, explicitly never gating",
         "degenerate?": "the DERIVED binary (`recruited`) is the statistic AMENDMENT 1 retired for zero "
                        "variance (1.0 on all 18 legs). The retrospective correctly does not gate on it; the "
                        "continuous mean_contacts does vary (1620-3861)"},
        {"id": "E4 Lys-Nz presentation", "role_in_prereg": "descriptive only, never a gate", "degenerate?": "n/a"},
        {"id": "LOMO survival (CONCORDANT tier)", "degenerate?": "see `lomo_clause`"},
        {"id": "extension rule 4d", "degenerate?": "see `extension_rule`"},
        {"id": "reverse-direction check",
         "degenerate?": "it only appends text to `reason`; it cannot change the tier, so a significant REVERSE "
                        "result and a merely wrong-signed one are graded identically (both DISCORDANT)"},
    ]

    with open(args.out, "w") as f:
        json.dump(doc, f, indent=2)
    print(json.dumps({k: v for k, v in doc.items() if k != "criterion_by_criterion"}, indent=2)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
