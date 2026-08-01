#!/usr/bin/env python3
"""
NR-V04 RETROSPECTIVE holdout — FROZEN scoring + verdict (prereg §4-§5).

Pure Python (stdlib only) so the SCORING LOGIC is unit-tested offline and is identical wherever it runs. This
module is committed, with its tests, BEFORE any retrospective leg runs — git history is the proof that the
criteria predate the data. No analyst discretion enters the verdict: feed it the leg JSONs, get the tier.

THE STATISTICS, and why each choice is what it is (prereg §4):

  * UNIT OF INDEPENDENCE = the CO-FOLD MODEL, not the leg. Two MD replicas of one co-fold model share a
    starting structure, so permuting legs would fake independence and inflate significance. Every test runs on
    model-level means -> n = 3 per arm.

  * PRIMARY TEST = a one-sided EXACT permutation test on the pooled contrast
        d = mean(E1 | NR4A1 noncov) - mean(E1 | NR4A2 u NR4A3 noncov)
    enumerating all C(9,3) = 84 arrangements. Exact, not asymptotic: with n = 3 no normal approximation is
    defensible. Minimum attainable one-sided p = 1/84 ~ 0.012 — which is WHY alpha = 0.05 is reachable here and
    ⚠ SUPERSEDED BY PREREG AMENDMENT 4 (2026-07-31), which changed the PANEL, not this code: nr4a3 co-fold
    seed 3 was excluded by measured input fault, so model-level n is 3/3/2, the primary contrast is 3 vs 5,
    the enumeration is C(8,3) = 56 and the minimum attainable one-sided p is 1/56 ~ 0.0179 (still < alpha).
    `exact_permutation_p` DERIVES C(n, |a|) from the data it is handed and therefore needed no edit — the
    numbers above are the pre-amendment illustration, retained for the record. Do not quote them as current.
    why the pairwise tests (C(6,3) = 20, min p = 0.05) are secondary only.

  * DIRECTION is registered BEFORE the data: NR4A1 is predicted MORE stable, i.e. LOWER E1 plateau, i.e. d < 0.
    A one-sided test with the direction chosen after seeing the data would be worthless; the direction is frozen
    in the prereg and hard-coded here.

  * E1 (interface-RMSD plateau) is the ONLY endpoint the verdict turns on. E2-E4 are computed and reported
    alongside it — including when they disagree — but cannot change the tier.

★★ AMENDMENT 3 (2026-07-25, trimcrae-delegated, APPLIED IN CODE 2026-07-31) — defects 2 and 3.

Both were measured by EXHAUSTIVE ENUMERATION over the frozen decision rule, before any retrospective leg ran,
so neither can have been motivated by a result nobody has seen. What each changed, and the two things they
deliberately did NOT change:

  * defect 2 — EXTENSION_P_WINDOW. Attainable p-values on the primary contrast are exactly k/84. The frozen
    window (0.012, 0.05] therefore contained only {0.0238, 0.0357, 0.0476}, ALL of which are <= alpha and so
    already CONCORDANT, while the smallest attainable p strictly above alpha (5/84 = 0.0595) fell OUTSIDE it.
    The rule could never fire in the case its own text names ("right sign, n=3 cannot resolve it"). The
    window is now (0.05, 0.12] — the p in {5..10}/84 band — still triggered by the p-value alone and still
    unavailable to a wrong-sign result. This is a LOOSENING IN FORM and buys no claim: `extension_triggered`
    is a reported field the tier assignment never reads, and it fires only in the region that is NOT
    CONCORDANT, so it can add work to an ambiguous result and can never promote one.

  * defect 3 — LOMO. An adversarial search over 400,000 configurations found 228,543 that reached p <= alpha
    with the correct ordering; ZERO of them then failed LOMO. So the clause could not be false when the other
    conditions held, and the WEAKLY_CONCORDANT branch predicated on it ("p <= alpha but the sign fails LOMO")
    was unreachable code. LOMO is RETAINED as a reported robustness diagnostic — `leave_one_model_out` is
    still computed and still emitted on every verdict — and REMOVED from the CONCORDANT conjunction. The
    CONCORDANT set is UNCHANGED by construction; the tier is now honest about what it actually tests.

  ⚠ UNTOUCHED, and they are the ones that would matter: the primary contrast, its registered direction, alpha,
    the endpoint, the 4.0 A threshold, and the unit of independence.

  SUPERSEDED, retained for the record: EXTENSION_P_WINDOW = (0.012, 0.05); CONCORDANT additionally required
  `lomo["survives"]`; WEAKLY_CONCORDANT additionally fired on "correct ordering and p <= alpha, but the sign
  fails leave-one-model-out".
"""
from __future__ import annotations

from itertools import combinations

# ---- frozen constants (prereg §3-§5). Do not move once a leg has run. --------------------------------------
ALPHA = 0.05                      # one-sided significance level for the primary test
STABLE_PLATEAU_A = 4.0            # E2 threshold — inherited unchanged from nrv04_readouts.INTERFACE_RMSD_STABLE_A
MAX_FAILED_LEGS_PER_ARM = 1       # prereg §4e: >1 technical failure in an arm -> that arm is underpowered
# prereg §4d as corrected by AMENDMENT 3 defect 2: right sign but unresolvable at n=3 -> extend to 6 models.
# HALF-OPEN AND IT MATTERS: `lo < p <= hi`, so p == 0.05 (== ALPHA, already CONCORDANT) does NOT trigger and
# p == 0.12 does. See the module docstring for why the old (0.012, 0.05] could never fire.
EXTENSION_P_WINDOW = (0.05, 0.12)

# ★ AMENDMENT 3 defect 4 — the MINIMUM DETECTABLE EFFECT, registered. Its measurement lives in
# nrv04-retrospective-prespend-audit-2026-07-25.md §3d (Monte-Carlo through THIS frozen decision rule against a
# leg-to-leg SD measured on 6 committed same-model feasibility groups); these constants are its code home,
# because a preregistered criterion has to be enforceable by the module that emits the claim.
MEASURED_LEG_SIGMA_A = 0.855      # leg-to-leg SD of E1, Å
REGISTERED_MDE_A = (1.5, 2.0)     # 80 % power band: 1.5 Å optimistic (sigma_model = 0) to 2.0 Å realistic

PRIMARY_ARM = "retro_noncov_nr4a1"
POOLED_ARMS = ("retro_noncov_nr4a2", "retro_noncov_nr4a3")
# RETIRED with stage R2 (AMENDMENT 3 defect 1) — no covalent leg can be enumerated any more, so the
# `covalency_decomposition` block below is permanently None. It is retained rather than deleted because the
# amendment retires the ARM, not this reporting path, and a historical leg set could still be re-scored.
COVALENT_ARM = "retro_cov_nr4a1"

TIER_CONCORDANT = "CONCORDANT"
TIER_WEAK = "WEAKLY_CONCORDANT"
TIER_DISCORDANT = "DISCORDANT"
TIER_INDETERMINATE = "INDETERMINATE"


# =============================================================================================================
# leg JSON -> model-level values
# =============================================================================================================
def model_level_values(legs):
    """Collapse per-leg E1 values to model-level means (prereg §4a).

    `legs`: iterable of dicts with at least {arm_id, cofold_model_seed, e1_plateau_A} and an optional
    `technical_failure` flag. Returns {arm_id: {model_seed: mean_E1}} plus the per-arm failure census.
    A leg marked technical_failure contributes nothing but is counted."""
    by_arm: dict = {}
    failures: dict = {}
    for leg in legs:
        arm = leg["arm_id"]
        failures.setdefault(arm, 0)
        if leg.get("technical_failure"):
            failures[arm] += 1
            continue
        val = leg.get("e1_plateau_A")
        if val is None:
            failures[arm] += 1
            continue
        by_arm.setdefault(arm, {}).setdefault(int(leg["cofold_model_seed"]), []).append(float(val))
    means = {arm: {m: sum(v) / len(v) for m, v in models.items()} for arm, models in by_arm.items()}
    return means, failures


def _values(means, arms):
    """Flatten the model-level means of one or more arms into a list, model order fixed by (arm, seed)."""
    out = []
    for arm in arms:
        for seed in sorted(means.get(arm, {})):
            out.append(means[arm][seed])
    return out


# =============================================================================================================
# exact one-sided permutation test
# =============================================================================================================
def mean_difference(group_a, group_b):
    """The test statistic: mean(a) - mean(b). Raises on an empty group rather than returning a silent nan."""
    if not group_a or not group_b:
        raise ValueError("mean_difference: both groups must be non-empty")
    return sum(group_a) / len(group_a) - sum(group_b) / len(group_b)


def exact_permutation_p(group_a, group_b, alternative="less"):
    """One-sided EXACT permutation p-value for mean(a) - mean(b), enumerating every C(n, |a|) split of the
    pooled values.

    alternative='less'  -> P(stat_perm <= stat_obs)   (the registered direction: NR4A1 MORE stable = LOWER E1)
    alternative='greater' -> P(stat_perm >= stat_obs)

    The observed arrangement is included in the count (the standard, non-anticonservative convention), so the
    minimum attainable p is 1/C(n, |a|) — 1/84 for the 3-vs-6 primary contrast, 1/20 for a 3-vs-3 pairwise one.
    """
    if alternative not in ("less", "greater"):
        raise ValueError("alternative must be 'less' or 'greater'")
    pooled = list(group_a) + list(group_b)
    n_a = len(group_a)
    obs = mean_difference(group_a, group_b)
    total = extreme = 0
    idx = range(len(pooled))
    for pick in combinations(idx, n_a):
        chosen = set(pick)
        a = [pooled[i] for i in idx if i in chosen]
        b = [pooled[i] for i in idx if i not in chosen]
        stat = mean_difference(a, b)
        total += 1
        if (stat <= obs + 1e-12) if alternative == "less" else (stat >= obs - 1e-12):
            extreme += 1
    return {"stat": obs, "p": extreme / total, "n_arrangements": total,
            "min_attainable_p": 1.0 / total, "alternative": alternative}


def leave_one_model_out(means, primary=PRIMARY_ARM, pooled=POOLED_ARMS):
    """Prereg §4c: recompute the primary statistic with each model dropped in turn; 'survives' iff the sign is
    unchanged in every refit. Returns the per-drop statistics and the survival flag."""
    entries = [(arm, seed) for arm in (primary,) + tuple(pooled) for seed in sorted(means.get(arm, {}))]
    obs = mean_difference(_values(means, [primary]), _values(means, pooled))
    sign = obs < 0
    refits = []
    for drop_arm, drop_seed in entries:
        trimmed = {a: {s: v for s, v in ms.items() if not (a == drop_arm and s == drop_seed)}
                   for a, ms in means.items()}
        a_vals, b_vals = _values(trimmed, [primary]), _values(trimmed, pooled)
        if not a_vals or not b_vals:
            refits.append({"dropped": f"{drop_arm}:m{drop_seed}", "stat": None, "sign_kept": False})
            continue
        stat = mean_difference(a_vals, b_vals)
        refits.append({"dropped": f"{drop_arm}:m{drop_seed}", "stat": round(stat, 4),
                       "sign_kept": (stat < 0) == sign})
    return {"observed_stat": round(obs, 4), "refits": refits,
            "survives": all(r["sign_kept"] for r in refits)}


# =============================================================================================================
# the verdict
# =============================================================================================================
def verdict(legs):
    """Apply the frozen prereg §5 tiers to a set of retrospective leg records. Pure: same input -> same tier.

    Returns the full evidence dict (statistic, p, pairwise, LOMO, covalency decomposition, extension trigger),
    never just the label — a tier without its evidence is not reportable."""
    means, failures = model_level_values(legs)

    underpowered = sorted(a for a, n in failures.items() if n > MAX_FAILED_LEGS_PER_ARM)
    missing = [a for a in (PRIMARY_ARM,) + POOLED_ARMS if not means.get(a)]

    out = {
        "prereg": "nr4a3-nrv04-retrospective-prereg.md",
        "endpoint": "E1 interface-RMSD plateau (A); lower = more stable",
        "model_level_means": {a: {str(s): round(v, 4) for s, v in sorted(ms.items())}
                              for a, ms in sorted(means.items())},
        "technical_failures": failures,
        "underpowered_arms": underpowered,
    }

    if missing or underpowered:
        out.update({"tier": TIER_INDETERMINATE,
                    "reason": ("missing arms: %s" % missing) if missing else
                              ("underpowered arms (> %d failed legs): %s" % (MAX_FAILED_LEGS_PER_ARM, underpowered))})
        return out

    primary_vals = _values(means, [PRIMARY_ARM])
    pooled_vals = _values(means, POOLED_ARMS)
    prim = exact_permutation_p(primary_vals, pooled_vals, alternative="less")
    lomo = leave_one_model_out(means)

    pairwise = {}
    for arm in POOLED_ARMS:
        pairwise[arm] = exact_permutation_p(primary_vals, _values(means, [arm]), alternative="less")

    arm_means = {a: sum(_values(means, [a])) / len(_values(means, [a]))
                 for a in (PRIMARY_ARM,) + POOLED_ARMS}
    below_both = all(arm_means[PRIMARY_ARM] < arm_means[a] for a in POOLED_ARMS)

    # covalency decomposition (prereg §4c) — reported, never gating, no significance claimed at n=3 vs 3
    cov = None
    if means.get(COVALENT_ARM):
        cov_vals = _values(means, [COVALENT_ARM])
        cov = {"stat_cov_minus_noncov": round(mean_difference(cov_vals, primary_vals), 4),
               "n_models_cov": len(cov_vals), "n_models_noncov": len(primary_vals),
               "interpretation": "negative = the covalent restraint stabilises the NR4A1 interface relative to "
                                 "the matched non-covalent arm. Descriptive only; no significance is claimed."}

    # reverse-direction check: is a paralogue significantly MORE stable than NR4A1?
    reverse = exact_permutation_p(primary_vals, pooled_vals, alternative="greater")

    # ★★ LOMO IS NOT IN THIS CONJUNCTION — AMENDMENT 3 defect 3. It is computed above and reported below as a
    # robustness diagnostic; it is not a tier condition, because 228,543 of 228,543 configurations that reached
    # this branch also survived it. A condition that can never be false is not a test, and leaving it here made
    # the tier look like it had four independent requirements when it had three.
    if prim["stat"] < 0 and below_both and prim["p"] <= ALPHA:
        tier, reason = TIER_CONCORDANT, "correct ordering, p <= %.2f (LOMO reported, not gating)" % ALPHA
    elif prim["stat"] < 0 and below_both:
        # The only remaining route to WEAK is p > alpha. The LOMO-predicated branch that stood here — "correct
        # ordering and p <= alpha, but the sign fails leave-one-model-out" — is STRUCTURALLY unreachable now
        # that LOMO left the conjunction above (that case is CONCORDANT), which is precisely what AMENDMENT 3
        # meant by striking it as unreachable.
        tier = TIER_WEAK
        reason = "correct ordering but p = %.4f > %.2f" % (prim["p"], ALPHA)
    else:
        tier = TIER_DISCORDANT
        reason = ("NR4A1 is not the most stable arm" if not below_both else
                  "primary statistic has the wrong sign")
        if reverse["p"] <= ALPHA:
            reason += "; the reverse direction is itself significant (p = %.4f)" % reverse["p"]

    lo, hi = EXTENSION_P_WINDOW
    extend = bool(prim["stat"] < 0 and below_both and lo < prim["p"] <= hi)

    out.update({
        "tier": tier,
        "reason": reason,
        "primary": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in prim.items()},
        "arm_means": {a: round(v, 4) for a, v in arm_means.items()},
        "nr4a1_below_both_paralogues": below_both,
        "pairwise_secondary": {a: {k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()}
                               for a, r in pairwise.items()},
        # ⚠ DERIVED PER TEST, NEVER ONE TYPED NUMBER (2026-08-01). This string read "min attainable one-sided
        # p for a 3-vs-3 pairwise test is 0.05 (C(6,3)=20)" — true of the NR4A1-vs-NR4A2 test and FALSE of
        # NR4A1-vs-NR4A3 after AMENDMENT 4, which took NR4A3 to n = 2 and its pairwise to C(5,3) = 10, min p
        # 0.10. §4.3 registered that as a stated LOSS: that comparison "can no longer attain α at all" and
        # must be reported as such, never as support for a verdict. A reader taking the caveat at its word
        # would have believed 0.05 was reachable — the exact overclaim the amendment was accepted knowing
        # the cost of. NOTHING COMPUTED CHANGES HERE: every statistic, p, tier and threshold is untouched;
        # this is the sentence beside them, and it now reads each test's OWN `min_attainable_p`.
        "pairwise_caveat": (
            "descriptive support, never the verdict (prereg §4c). Min attainable one-sided p per test: "
            + "; ".join("%s = %.4g (C(%d,%d) = %d arrangements)%s"
                        % (a, r["min_attainable_p"], len(_values(means, [PRIMARY_ARM])) + len(_values(means, [a])),
                           len(_values(means, [PRIMARY_ARM])), r["n_arrangements"],
                           "" if r["min_attainable_p"] <= ALPHA else
                           " — ⛔ ABOVE α = %.2f, so this comparison CANNOT ATTAIN SIGNIFICANCE at any "
                           "observed ordering and is UNRESOLVABLE, not null" % ALPHA)
                        for a, r in sorted(pairwise.items()))),
        "leave_one_model_out": lomo,
        "leave_one_model_out_role": "REPORTED robustness diagnostic only — NOT a tier condition (AMENDMENT 3 "
                                    "defect 3: 228,543 configurations reached p <= alpha with the correct "
                                    "ordering and zero failed LOMO, so the clause could never bite).",
        "reverse_direction": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in reverse.items()},
        "covalency_decomposition": cov,
        "extension_triggered": extend,
        "extension_rule": "prereg §4d as corrected by AMENDMENT 3 defect 2: right sign but p in (%.2f, %.2f] "
                          "-> generate 3 more co-fold models per paralogue and re-run R1 at n=6. May NOT be "
                          "invoked on a wrong-sign result." % (lo, hi),
        # ★ AMENDMENT 3 defect 4 — travels WITH the verdict, because the over-claim it forbids is made when a
        # null is read, and a reader who has to go and find the MDE in another file will not.
        "registered_mde": {
            "measured_leg_sigma_A": MEASURED_LEG_SIGMA_A,
            "mde_80pct_power_A": list(REGISTERED_MDE_A),
            "source": "nrv04-retrospective-prespend-audit-2026-07-25.md §3d — Monte-Carlo through THIS frozen "
                      "decision rule; false-positive rate at delta=0 is 0.048, so the test is valid, just blunt",
            "null_licenses": "the workflow did not resolve a paralogue difference of the magnitude this design "
                             "can detect (>= ~%.1f-%.1f A in interface-RMSD plateau at n = 3 models/arm)"
                             % REGISTERED_MDE_A,
            "null_may_NOT_claim": "that NR-V04's selectivity is localised to warhead reactivity. That "
                                  "localisation stands on Leg 0 (Cys551 unique to NR4A1) and Zhang 2018 and "
                                  "must be stated as such. AMENDMENT 3 defect 4 also retires prereg §5c's "
                                  "registered composite outcome, whose R2 half no longer exists.",
        },
        "claim_ceiling": "directional concordance/discordance ONLY. No ddG, alpha, cooperativity, affinity or "
                         "degradation claim; Arm E computes no free energy (prereg §6). A null is bounded by "
                         "`registered_mde` (AMENDMENT 3 defect 4), not by the absence of an effect.",
    })
    return out


def _cli(argv=None):
    import argparse
    import json
    import sys
    ap = argparse.ArgumentParser(description="NR-V04 retrospective frozen verdict (pure; reads leg JSONs).")
    ap.add_argument("--legs", required=True, help="path to a JSON array of leg records")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    with open(args.legs) as f:
        legs = json.load(f)
    res = verdict(legs)
    txt = json.dumps(res, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(txt + "\n")
    print(txt)
    return 0 if res["tier"] != TIER_INDETERMINATE else 2


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
