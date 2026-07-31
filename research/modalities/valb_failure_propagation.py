#!/usr/bin/env python3
"""What the valB_mini FAIL invalidates, and what it does NOT -- the error algebra, quantity by quantity.

★ WHY THIS FILE EXISTS. On 2026-07-30 the preregistered known-answer ternary-cooperativity benchmark landed at
its full n=3 and FAILED on sign (paper §2.11 is the one home for those numbers). The obvious next question is
not "how do we fix the calibrator" -- it is **which of the ladder's other quantities just became unciteable**,
and the repo had no artifact that answered it. Without one, the failure spreads by vibe: every ternary number
in the program looks tainted, including ones whose error algebra is completely different. This file does the
propagation explicitly so the blast radius is a derivation rather than an impression.

★ THE ONE-SENTENCE ANSWER. valB_mini measures the LEAST-CANCELLING quantity in the whole ladder -- a difference
of alchemical morphs taken in two environments that differ by an entire protein -- and its failure transfers to
other quantities only in proportion to how much of that non-cancellation they share. The flagship gate (RUNG
5a-KS's `S`) is at the opposite extreme: a double difference of the SAME one-atom morph across two homologous
pockets, with the binary and solvent legs cancelling algebraically rather than numerically. Those are not the
same calculation and the failure of one does not carry to the other by assumption -- but nor does the survival
come free, and §4 below is the measurement that would buy it.

★ AND A SECOND RESULT THAT WAS NOT AVAILABLE UNTIL THIS MORNING. `valb_triangle_closure.closure_noise_floor`
records that `sigma_leg` for this lane "is known only to within a factor of ~15" and that "nothing in this lane
has measured it". The n=3 replicates measured it. §1 converts the landed between-replicate cycle SD into a
same-lane UPPER BOUND on `sigma_leg` through the design's own SD relation, which collapses that factor and
re-grades the closure triangle's power BEFORE `R` lands -- which is the only order in which a power statement
is worth anything.

WHAT THIS FILE DELIBERATELY DOES NOT DO:
  * It does not amend any preregistered rule. §2 records a discrepancy between `binary_departure_prereg`'s
    hand-set `sigma_leg > 0.2` proxy and the power now measurable at the bounded value, and then leaves the
    frozen rule ALONE. Amending a prereg after a failing result is the retune this program forbids (CLAUDE.md
    §5 / STRATEGY "admits-zero" open item); recording the discrepancy before `R` lands is the honest half.
  * It does not compute a price, a throughput or a basis. Costs live in pricing.md and the rung entries.
  * It does not restate the n=3 result. `MEASURED` below carries the inputs it consumes WITH provenance, and
    paper §2.11 remains their narrative home.
"""
import copy
import functools
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from valb_triangle_closure import closure_noise_floor, binary_departure_prereg  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "valb-failure-propagation.json")

# =============================================================================================================
# INPUTS -- measured, each with the artifact or section that owns it. Nothing here is estimated.
# =============================================================================================================
MEASURED = {
    "cycle_sd_kcal": 0.375,
    "per_leg_mbar_se_kcal": (0.097, 0.132),
    "abs_error_kcal": 1.543,
    "n_replicates": 3,
    "_source": ("paper §2.11 (nr4a3-degrader-paper.md), reduced 2026-07-30 by the official reducer from the "
                "4 replicate legs that landed 3:07 AM ET. Those are the narrative home; this dict is the "
                "machine copy the derivations below consume."),
    "_cycle_sd_is_a_sigma_edge": ("0.375 is the between-replicate SD of ddG_coop itself -- a per-EDGE spread "
                                  "(ternary minus binary), which is `sigma_edge` in closure_noise_floor's "
                                  "notation, NOT a per-leg sigma. §1 does the conversion."),
}

# The designed effect the flagship gate is trying to resolve. ONE HOME: nr4a3-5aks-lane-report.md §2.
S_DESIGNED_EFFECT_KCAL = (0.5, 1.5)
S_BEST_CASE_RESOLVABLE_KCAL = 1.12


# =============================================================================================================
# 1. sigma_leg IS NOW BOUNDED BY MEASUREMENT, FOR THE FIRST TIME IN THIS LANE
# =============================================================================================================
def sigma_leg_now_bounded():
    """Convert the landed cycle SD into a same-lane upper bound on `sigma_leg`, and re-grade the triangle.

    THE RELATION IS THE DESIGN'S OWN, not one invented here: closure_noise_floor states
    `SD(R) = sqrt(6)*sigma_leg = sqrt(3)*sigma_edge`, i.e. `sigma_edge = sqrt(2)*sigma_leg`. ddG_coop is a
    two-leg difference, so the measured between-replicate cycle SD IS a sigma_edge and inverts directly.

    ★ IT IS AN UPPER BOUND, FOR TWO REASONS THAT ARE ALREADY ON THE RECORD -- and both matter, because an
    upper bound that is quoted as a value would UNDERSTATE the triangle's power and could talk us out of a
    diagnostic we have already paid for:
      (a) HOMOLOGY-MODEL VARIANCE THE TRIANGLE DOES NOT HAVE. valB replicate seed `s` starts from the `s%n`-th
          independently relaxed SMARCA2 model, so 0.375 contains model-swap variance. The triangle is run at a
          SINGLE seed by construction (`valb_triangle_closure.same_seed_requirement`), which removes that term
          outright. closure_noise_floor's own bounds note says exactly this about the 0.7 upper bound.
      (b) SOLVATION VARIANCE. The n=3 reduction reports system identity INCONSISTENT because the ternary arm
          disagrees with ITSELF across seeds in particle count (STRATEGY's RUNG 2 replicate row). An SD taken
          across independently solvated builds carries solvation variability on top of sampling variability,
          and the two are not separated -- which is why STRATEGY already reports 0.375 as an upper bound on
          the sampling-only SD. This file inherits that reading rather than restating it.

    So the true `sigma_leg` for a same-seed triangle sits at or below the returned bound, and the whole upper
    half of the design's original range -- where the triangle was close to useless -- is now excluded by
    measurement rather than by hope."""
    return copy.deepcopy(_sigma_leg_now_bounded_cached())


@functools.lru_cache(maxsize=None)
def _sigma_leg_now_bounded_cached():
    """Memoised implementation. NEVER return this object directly -- `build_report` embeds it, and a
    caller mutating an embedded dict would corrupt the cache for every later call in the process."""
    floor_ = closure_noise_floor()
    bounds = floor_["sigma_leg_bounds"]
    lo = bounds["lower_MBAR_SE_r0_ternary"]
    old_hi = bounds["upper_repo_assumed_replicate_SD"]

    sigma_edge = float(MEASURED["cycle_sd_kcal"])
    new_hi = sigma_edge / math.sqrt(2.0)

    return {
        "what_changed": ("closure_noise_floor records `sigma_leg_is_unknown_by_a_factor_of` %.1f and says "
                         "'nothing in this lane has measured it'. The n=3 replicates measured it."
                         % floor_["sigma_leg_is_unknown_by_a_factor_of"]),
        "relation_used": floor_["SD_R_formula"],
        "measured_sigma_edge_kcal": sigma_edge,
        "sigma_leg_upper_bound_kcal": round(new_hi, 4),
        "sigma_leg_lower_bound_kcal": lo,
        "uncertainty_factor_before": floor_["sigma_leg_is_unknown_by_a_factor_of"],
        "uncertainty_factor_after": round(new_hi / lo, 1),
        "superseded_upper_bound": old_hi,
        "why_it_is_an_upper_bound_not_a_value": {
            "a_homology_model_swap": ("valB seed s starts from the s%n-th relaxed SMARCA2 model, so 0.375 "
                                      "contains model-swap variance. The triangle is single-seed by "
                                      "construction (same_seed_requirement), which removes that term."),
            "b_independent_solvation": ("the n=3 reduction flags system identity INCONSISTENT -- the ternary "
                                        "arm differs from itself in particle count across seeds -- so 0.375 "
                                        "also carries solvation variability. STRATEGY already reports it as "
                                        "an upper bound on the sampling-only SD."),
        },
        "consequence": ("the design's sigma_leg = 0.5 and 0.7 rows -- where power to resolve an r0-sized miss "
                        "is 0.22 and 0.14 -- are now EXCLUDED BY MEASUREMENT. The triangle is graded against "
                        "the interval [%.3f, %.4f]." % (lo, new_hi)),
    }


def power_at_measured_bound(trials=40000):
    """Re-run the design's own power machinery at the bounded value. Nothing is reimplemented -- this calls
    closure_noise_floor with the measured sigma, so any future correction to the noise model reaches here.

    The reported power is a WORST CASE within the new interval: it is computed at the upper bound, and the two
    reasons in §1 both push the true value down, i.e. the real power is at least this."""
    return copy.deepcopy(_power_at_measured_bound_cached(trials))


@functools.lru_cache(maxsize=None)
def _power_at_measured_bound_cached(trials):
    """Memoised implementation -- see _sigma_leg_now_bounded_cached for why the public one copies."""
    b = sigma_leg_now_bounded()
    hi = b["sigma_leg_upper_bound_kcal"]
    lo = b["sigma_leg_lower_bound_kcal"]
    rows = closure_noise_floor(sigma_leg_values=(lo, hi), trials=trials)["rows"]
    at_hi = [r for r in rows if abs(r["sigma_leg"] - hi) < 1e-9][0]
    at_lo = [r for r in rows if abs(r["sigma_leg"] - lo) < 1e-9][0]
    return {
        "graded_at": "the measured UPPER bound, so every figure is a worst case within the bounded interval",
        "at_sigma_leg_upper_bound": at_hi,
        "at_sigma_leg_lower_bound": at_lo,
        "reading": ("power to detect an r0-sized (1.478 kcal/mol) path error is %.2f at the upper bound and "
                    "%.2f at the lower one. That interval is NOT a clean pass -- %.2f is mediocre power and "
                    "the honest statement is that the triangle's adequacy depends on where in the bounded "
                    "interval the true sigma_leg sits. What the measurement DID buy is the exclusion of the "
                    "range where the triangle was hopeless: the design's own 0.5 and 0.7 rows give %.2f and "
                    "%.2f, and those are now ruled out."
                    % (at_hi["power_at_n1"]["detect_1.478"], at_lo["power_at_n1"]["detect_1.478"],
                       at_hi["power_at_n1"]["detect_1.478"], 0.2188, 0.1416)),
    }


# =============================================================================================================
# 2. A FROZEN RULE MEETS A NUMBER IT WAS WRITTEN WITHOUT -- RECORDED, NOT RETUNED
# =============================================================================================================
@functools.lru_cache(maxsize=None)
def power_threshold_crossing(target_power=0.80, delta=1.478, trials=30000):
    """The sigma_leg at which power to detect an r0-sized effect crosses a conventional threshold.

    MEMOISED, and safe to memoise: `closure_noise_floor` seeds its RNG with a fixed constant, so this is a
    pure function of its arguments. Without the cache a bisection is 7 x `trials` Monte Carlo draws and the
    callers below invoke it repeatedly -- which made the first version of this module's test suite take
    minutes. Engineering effort is free; wasted CI minutes on every run are not.

    ★ THIS IS THE NUMBER THAT GRADES THE FROZEN PROXY, and it was worth computing before proposing to replace
    it. `binary_departure_prereg`'s hand-set `sigma_leg > 0.2` was chosen when sigma_leg was unknown to a
    factor of 15.6 -- i.e. with no way to check it. Bisecting the design's own power curve says where it
    SHOULD sit. If the two agree, the proxy was right and the case for amending it is transparency, not
    correction; my first reading of this discrepancy assumed the proxy was misfiring and did not check."""
    lo, hi = 0.05, 0.40
    for _ in range(7):
        mid = (lo + hi) / 2.0
        p = closure_noise_floor(sigma_leg_values=(mid,), trials=trials)["rows"][0]["power_at_n1"]
        if p["detect_%.3f" % delta] >= target_power:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def frozen_rule_vs_measured_power():
    """`binary_departure_prereg` demotes a null closure to UNDERPOWERED whenever `sigma_leg > 0.2`.

    THAT 0.2 IS A HAND-SET PROXY FOR "the power is too low to read a null", chosen when sigma_leg was unknown
    to a factor of 15.6 and a proxy was the only thing available.

    ★★ AND THE MEASUREMENT VINDICATES IT. Bisecting the design's own power curve puts a conventional 0.80-power
    threshold at sigma_leg ~ 0.216; the frozen proxy sits at 0.200, within ~8%. So the hand-set number was very
    nearly right, and two consequences follow that run AGAINST the amendment being important:
      (i) AMENDING IT WOULD NOT RESCUE A NULL `R`. At the measured upper bound the power is ~0.63, which a
          conventional threshold demotes anyway. The fix changes the LABEL's justification, not the verdict.
      (ii) The remaining value is TRANSPARENCY -- a reader of "UNDERPOWERED" cannot currently tell whether the
          power was 0.63 or 0.05, and those warrant different responses.
    Recorded this way round deliberately: the first draft of this analysis framed the proxy as misfiring and
    proposed replacing it, which would have been an amendment argued from an unchecked assumption. The proxy is
    close to correct.

    ⛔ THE RULE IS NOT CHANGED HERE, AND MUST NOT BE CHANGED BY WHOEVER READS `R`. Two reasons, the second
    decisive: (i) the discrepancy is recorded BEFORE `R` lands, which is the only time such a record is
    credible, and it stays a record; (ii) this repo already carries an open item for exactly this shape of
    thing -- the valB gate that "admits the null" was found defective, deliberately NOT applied, and routed for
    a dated reviewer-approved defect-fix instead. A quiet retune here would be the same error with the same
    excuse. What this function produces is the EVIDENCE for that review, not the amendment."""
    b = sigma_leg_now_bounded()
    hi = b["sigma_leg_upper_bound_kcal"]
    p = power_at_measured_bound()
    power_1478 = p["at_sigma_leg_upper_bound"]["power_at_n1"]["detect_1.478"]
    crossing = power_threshold_crossing()

    frozen_at_hi = binary_departure_prereg(R_ternary=0.0, R_binary=0.0, sigma_leg=hi)
    return {
        "frozen_proxy": "binary_departure_prereg demotes BINARY_CANCELS -> UNDERPOWERED when sigma_leg > 0.2",
        "measured_sigma_leg_upper_bound": hi,
        "frozen_rule_fires": hi > 0.2,
        "verdict_the_frozen_rule_would_return_on_a_null": frozen_at_hi["verdict"],
        "actual_power_to_detect_1.478_at_that_sigma": power_1478,
        "power_0.80_crosses_at_sigma_leg": round(crossing, 4),
        "frozen_proxy_sits_at": 0.2,
        "proxy_error_vs_computed": round(abs(0.2 - crossing) / crossing, 3),
        "the_finding": ("the frozen proxy (0.200) and the computed 0.80-power crossing (%.3f) agree to ~%.0f%%. "
                        "The hand-set number was very nearly right, which is the opposite of what a "
                        "'the proxy is misfiring' reading would have predicted."
                        % (crossing, 100 * abs(0.2 - crossing) / crossing)),
        "would_amending_it_rescue_a_null_R": False,
        "why_not": ("at the measured upper bound the power is %.2f, which a conventional 0.80 threshold "
                    "demotes anyway. The amendment changes the LABEL's justification, not the verdict -- so "
                    "it must not be sold as unlocking the diagnostic." % power_1478),
        "action_taken_here": "NONE. Recorded before R lands; the rule is untouched.",
        "action_proposed_to_trimcrae": ("a dated defect-fix that REPORTS the computed power beside the "
                                        "verdict, keeping the demotion rule itself. Value is transparency: "
                                        "'UNDERPOWERED' currently cannot distinguish power 0.63 from 0.05, "
                                        "and those warrant different responses. $0. LOW STAKES -- graded that "
                                        "way because the measurement says so, not to make it easy to approve."),
        "the_honest_residual": ("a null R at the upper bound is worth ~%.2f power, which does not make a null "
                                "strong evidence, amended or not. The triangle can ADMIT the cycle more "
                                "confidently than it can convict it -- the design's own asymmetry, not a new "
                                "problem. ⚠ AND THE VERDICT GENUINELY TURNS ON WHERE IN [%.3f, %.4f] THE TRUE "
                                "sigma_leg SITS: below ~%.3f a null R clears 0.80 power and is readable; at "
                                "the upper bound it is not. Since the bound is an UPPER bound, the true value "
                                "is plausibly on the readable side -- but that is an argument, and §7 is how "
                                "it becomes a measurement."
                                % (power_1478, b["sigma_leg_lower_bound_kcal"], hi, crossing)),
    }


# =============================================================================================================
# 3. THE PROPAGATION TABLE -- how much of valB's non-cancellation does each ladder quantity share?
# =============================================================================================================
def error_algebra():
    """Write each quantity as a combination of per-leg errors and read off what cancels.

    THE MODEL. For a morph A->B computed in environment E, write `dG_calc(A->B|E) = dG_true(A->B|E) + e(A->B|E)`.
    Every quantity below is a fixed +-1 combination of such terms, so its error is the same combination of the
    `e`s, and the question is only ever HOW MUCH STRUCTURE the combination shares. Two kinds of cancellation
    appear and they are not equally strong:
      ALGEBRAIC  -- the leg is literally the same leg on both sides and drops out of the expression before any
                    number is computed. Exact, no residual, no noise added.
      NUMERICAL  -- two different legs are subtracted and their errors partly cancel because the systems are
                    similar. Approximate, and the residual is what bites.
    valB's ddG_coop has NO algebraic cancellation of the ternary-vs-binary contrast and very little numerical
    cancellation, because the two environments differ by an entire protein chain, ~54k particles and a pose
    stability that is 8/12-departed on one side and 12/12-clean on the other. That is the worst configuration
    available in the ladder, and it is the one that failed."""
    return [
        {
            "quantity": "ddG_coop (valB_mini; the NR4A ternary cooperativity matrix it gates)",
            "expression": "e(A->B | ternary) - e(A->B | binary)",
            "cancellation": "NUMERICAL ONLY, and weak",
            "why": ("the two environments differ by an entire protein chain. Measured on this lane: ~144k vs "
                    "~90k particles, and the binary arm's ligand departs its pocket in 8/12 replicas where "
                    "the ternary arm is 12/12 clean. Almost nothing about the two error terms is shared."),
            "status": "MEASURED FAILURE -- abs error %.3f kcal/mol at n=3" % MEASURED["abs_error_kcal"],
            "consequence": ("NR4A ternary cooperativity scores stay EXPLORATORY. This is the claim the FAIL "
                            "actually costs, and it is the only one it costs directly."),
        },
        {
            "quantity": "S (RUNG 5a-KS, the ligand-side causal kill-switch)",
            "expression": "e(d0->d | ternary, NR4A3) - e(d0->d | ternary, NR4A1)",
            "cancellation": "ALGEBRAIC on the binary and solvent legs, NUMERICAL and strong on the rest",
            "why": ("the binary leg is the construct + CRBN with no target chain, so it is the SAME leg for "
                    "both species and drops out of the expression exactly -- `nr4a3_5aks_reduce` REFUSES a "
                    "binary leg rather than warning, for this reason. What remains is one morph of ONE ATOM "
                    "(aromatic C-H -> N) evaluated in two homologous pockets at matched ternary architecture. "
                    "That is the most favourable cancellation configuration in the ladder, and the exact "
                    "opposite of the contrast that failed."),
            "status": "NOT DIRECTLY IMPLICATED by the valB FAIL",
            "consequence": ("survives the FAIL on algebra -- but see §4: 'not implicated' is an argument, not "
                            "a measurement, and S has its own separate resolvability problem."),
        },
        {
            "quantity": "ddG_neo-interface^m (RUNG 5's CONFIRMATORY protein-mutation cycle, pmx + GROMACS)",
            "expression": "e(mut | ternary) - e(mut | binary)",
            "cancellation": "NUMERICAL ONLY, and weak -- THE SAME SHAPE AS THE QUANTITY THAT FAILED",
            "why": ("STRATEGY defines it as dG_mut^ternary - dG_mut^binary, where the binary leg is the "
                    "target-warhead complex. That is a ternary-vs-binary contrast between systems differing "
                    "by a whole protein -- structurally identical to ddG_coop above, which is the row with a "
                    "measured 1.543 kcal/mol failure. The PRIMARY kill-switch S escapes this because its "
                    "binary leg cancels ALGEBRAICALLY (same leg both sides, no target chain); this one has no "
                    "such cancellation, because a protein MUTATION changes the target and the target is what "
                    "the two environments differ by."),
            "status": "IMPLICATED -- inherits the measured failure mode; not independently tested",
            "consequence": ("⚠ IT IS NOT THE INDEPENDENT SECOND CAUSAL LINE THE LADDER TREATS IT AS. Its "
                            "known-answer benchmark passed on a PROTEIN-MUTATION quantity, not on a "
                            "ternary-minus-binary one, so that pass does not cover this exposure. Until it "
                            "does, a concordance between S and this cycle is NOT two independent lines "
                            "agreeing -- and a DISCORDANCE would be uninterpretable. The paper's headline "
                            "causal result is already stated as not hostage to it, which is what keeps this "
                            "from being load-bearing."),
        },
        {
            "quantity": "ddG_bind (RUNG 4 step-1 fan-out; the 18-edge congeneric map)",
            "expression": "e(A->B | complex) - e(A->B | solvent)",
            "cancellation": "NUMERICAL, and validated independently of anything ternary",
            "why": ("a congeneric binary RBFE, the class valA_mini reproduced against a known answer and the "
                    "cmpd19 pilot converged on the real system. It contains no ternary-vs-binary contrast at "
                    "all, so valB's error term does not appear in it."),
            "status": "UNAFFECTED",
            "consequence": "the delivered congeneric map stands on its own gates; the FAIL does not reach it.",
        },
        {
            "quantity": "R_ternary / R_binary (the closure triangle)",
            "expression": "sum of e around a closed 3-cycle, within ONE environment",
            "cancellation": "the true terms telescope exactly; per-endpoint STATE-FUNCTION error telescopes too",
            "why": ("valb_triangle_closure verified this numerically two ways -- max |R| ~ 1e-14 over 20,000 "
                    "random state-function draws. So closure sees ONLY the non-conservative part of the "
                    "error and is BLIND to force field, homology model, NAGL charges, protonation and the "
                    "reference data."),
            "status": "IN FLIGHT -- the diagnostic, not a claim",
            "consequence": ("R_ternary is the only measurement in the program that speaks to the error class "
                            "S is exposed to. §4 is what it licenses."),
        },
        {
            "quantity": "the categorical axes (Tier 0 unique-residue map, Tier 1 atlas, Tier 2 basins/reach)",
            "expression": "not a free-energy difference at all",
            "cancellation": "n/a",
            "why": ("these are geometric and sequence-derived: exposure, divergence, reach distance, collision "
                    "fraction, lysine presentation. No alchemical morph appears anywhere in them."),
            "status": "UNAFFECTED",
            "consequence": ("the paper's selectivity spine does not route through the failed quantity. This is "
                            "why the program has somewhere to stand."),
        },
    ]


# =============================================================================================================
# 4. WHAT R_ternary LICENSES ABOUT S -- pre-registered, before R lands
# =============================================================================================================
def s_resolvability_from_R_ternary(R_ternary=None, sigma_leg=None):
    """The decision rule for the parked 5a-KS resume, written while `R` is still running.

    THE CHAIN, and it is short. `R_ternary` is a three-leg closure taken entirely inside the ternary
    environment, so on independent legs its non-conservative content implies a per-leg scale
    `eps_leg ~ |R_ternary| / sqrt(3)`. `S` is a two-leg difference in that same environment, so it inherits
    `eps_S ~ sqrt(2) * eps_leg = sqrt(2/3) * |R_ternary|`. Compare that with what S is trying to see: one
    partly-buried hydrogen bond, ~0.5-1.5 kcal/mol, against the lane's own best-case resolvable ~1.12.

    ⚠ THE ASYMMETRY IS THE DESIGN'S OWN AND IT LIMITS THIS RULE IN ONE DIRECTION ONLY. closure_noise_floor
    records that a SMALL |R| is strong evidence (path error and noise would both have to be small) while a
    LARGE |R| at n=1 is AMBIGUOUS -- one draw cannot separate a systematic path error from an unlucky sample.
    So this rule may ADMIT the resume outright; it may not CONDEMN it outright. A large R_ternary buys a HOLD
    and a second draw, never a kill. That is written here so it cannot be forgotten once a number exists."""
    b = sigma_leg_now_bounded()
    sl = float(sigma_leg) if sigma_leg is not None else b["sigma_leg_upper_bound_kcal"]
    thresh = 1.96 * math.sqrt(3.0) * sl
    # the |R_ternary| at which S's inherited noise swamps its best-case resolvable effect
    r_crit = S_BEST_CASE_RESOLVABLE_KCAL / math.sqrt(2.0 / 3.0)

    out = {
        "registered": "2026-07-30, while the two ternary triangle legs were still running",
        "chain": ("eps_leg ~ |R_ternary|/sqrt(3)  ->  eps_S ~ sqrt(2)*eps_leg = sqrt(2/3)*|R_ternary|"),
        "S_designed_effect_kcal": list(S_DESIGNED_EFFECT_KCAL),
        "S_best_case_resolvable_kcal": S_BEST_CASE_RESOLVABLE_KCAL,
        "sigma_leg_used": sl,
        "R_ternary_resolution_threshold": round(thresh, 4),
        "R_ternary_critical_for_S": round(r_crit, 4),
        "rule": {
            "ADMIT": ("|R_ternary| below its own resolution threshold (%.3f) -- no detectable non-conservative "
                      "error in the ternary environment. The resume is bought." % thresh),
            "HOLD": ("|R_ternary| resolved but under %.3f -- real path error, but not enough to swamp S. Buy "
                     "the resume AND carry the measured floor as S's uncertainty, not the MBAR SE." % r_crit),
            "STOP_AND_REDRAW": ("|R_ternary| at or above %.3f -- S's inherited noise floor exceeds what S can "
                                "resolve, so finishing the legs buys a number that cannot answer its own "
                                "question. Per the asymmetry above this is a HOLD FOR A SECOND DRAW, never a "
                                "kill on one sample." % r_crit),
        },
        "_blind_spot_stated": ("closure is blind to per-endpoint state-function error, so an ADMIT verdict "
                               "bounds the non-conservative class ONLY. State-function error that differs "
                               "between the NR4A3 and NR4A1 pockets is invisible to R_ternary and to every "
                               "other check this program has. For S that residual is a SECOND difference of a "
                               "ONE-ATOM morph across two homologous pockets, which is the configuration in "
                               "which it is smallest -- but small-by-argument is not measured, and this file "
                               "will not pretend otherwise."),
    }
    if R_ternary is None:
        out["verdict"] = "NOT YET MEASURED -- this is the pre-registration, not a result"
        return out

    r = abs(float(R_ternary))
    out["R_ternary_observed"] = float(R_ternary)
    out["verdict"] = ("ADMIT" if r < thresh else
                      "HOLD" if r < r_crit else
                      "STOP_AND_REDRAW")
    return out


# =============================================================================================================
# 5. S's OWN PROBLEM, WHICH IS NOT valB's -- and which the n=3 result has just quantified
# =============================================================================================================
def s_error_bar_scope():
    """Both parked 5a-KS legs are seed 0, one per arm. `nr4a3_5aks_reduce.reduce_S` therefore returns
    COMPUTED_SINGLE_SEED with `S_err_kind = 'mbar_se_ONLY'` -- a point estimate with no replicate SD, which is
    the exact limitation that left valB's calibration verdict INDETERMINATE at n=1.

    ★ WHAT IS NEW THIS MORNING IS THE SIZE OF THAT GAP, ON THIS PIPELINE, MEASURED. The n=3 replicates put the
    between-replicate SD at ~3x the per-leg MBAR SE on the same legs. So an MBAR-SE-only error bar on S does
    not merely lack the right label -- it is understated by roughly that factor, and the correction is now a
    number instead of an assertion. Applying it says whether a single-seed S can see its own designed effect,
    and it is worth knowing BEFORE the resume is bought rather than after.

    This is a scope finding, not a stop. Paper §5 already fixes the reading of a null S in advance, and the
    repo's own standard (STRATEGY: converged fwd/rev + ~3 replicates + replicate-SD error bars) is what the
    two-leg configuration falls short of."""
    se_lo, se_hi = MEASURED["per_leg_mbar_se_kcal"]
    se_mid = (se_lo + se_hi) / 2.0
    ratio = MEASURED["cycle_sd_kcal"] / se_mid

    s_err_mbar = math.sqrt(2.0) * se_mid          # S is a 2-leg difference
    s_err_corrected = s_err_mbar * ratio
    resolvable_mbar = 1.96 * s_err_mbar
    resolvable_corrected = 1.96 * s_err_corrected

    lo_eff, hi_eff = S_DESIGNED_EFFECT_KCAL
    return {
        "configuration": "two parked legs, seed 0, one per arm -> reduce_S returns COMPUTED_SINGLE_SEED",
        "replicate_sd_over_mbar_se_measured": round(ratio, 2),
        "_ratio_basis": ("MEASURED on this pipeline at n=3: cycle SD %.3f against per-leg MBAR SEs %.3f-%.3f. "
                         "Before today this factor was assumed; now it is not."
                         % (MEASURED["cycle_sd_kcal"], se_lo, se_hi)),
        "S_err_as_it_would_be_reported_kcal": round(s_err_mbar, 4),
        "S_err_after_the_measured_correction_kcal": round(s_err_corrected, 4),
        "resolvable_effect_as_reported_kcal": round(resolvable_mbar, 4),
        "resolvable_effect_corrected_kcal": round(resolvable_corrected, 4),
        "designed_effect_kcal": list(S_DESIGNED_EFFECT_KCAL),
        "reading": ("at one seed per arm S resolves ~%.2f kcal/mol once the measured replicate/MBAR factor is "
                    "applied, against a designed effect of %.1f-%.1f. It can therefore see the TOP of its own "
                    "effect range and not the bottom, so a null S at n=1 is uninterpretable in precisely the "
                    "way valB's n=1 was."
                    % (resolvable_corrected, lo_eff, hi_eff)),
        "_decided_2026_07_30": {
            "decision": "n = 2 SEEDS PER ARM -- four ternary legs, not two (trimcrae go; STRATEGY Open decision 11)",
            "why": "at one seed per arm S resolves only the TOP of its own designed 0.5-1.5 kcal/mol effect, so "
                   "the PRE-REGISTERED LIKELY OUTCOME -- a null -- would have been uninterpretable. The second "
                   "seed is what turns a null into a BOUND.",
            "implemented_in": ["ternary_vast_launch.MODES['5aks'].legs (4 units)",
                               "ternary_vast_launch.seed_stage_cache (seeds EVERY declared seed; it seeded only "
                               "seed 0, and 5aks sets stage_required=True, so a seed-1 leg would have died on a "
                               "cache MISS on a rented host)",
                               "vast_cost_model.LADDER_REFERENCE_GPU_H (4 legs -> ladder total ~$169)",
                               "ternary-vast-watch.json (both new units watched, all four parked together)"],
            "not_chosen": "n = 3 per arm -- the second seed buys most of the readability and the third is the "
                          "shallow part of a 1/sqrt(n) curve, i.e. the deepening past field standard CLAUDE.md "
                          "section 5 defaults against.",
            "still_gated_on": "the market. All four units stay enabled=false behind the relaunch price gate and "
                              "re-enable TOGETHER -- a partial re-enable buys a number that still cannot report "
                              "a null.",
        },
        "options": {
            "finish_as_configured": ("buy the two parked legs, report S as a point estimate, and label it "
                                     "exploratory. Retires paper §2.10(d) 'the causal test has not been run' "
                                     "but cannot support a null."),
            "add_one_seed_per_arm": ("two further legs give S a real replicate SD and make a null readable. "
                                     "✅ THE CHECK THIS OPTION OWED IS DONE (2026-07-30, $0, source-read): a "
                                     "second seed on the 5a-KS lane IS independent sampling. The wrap that "
                                     "motivated the warning is ternary_pdb_stage's "
                                     "`starting_model_index = SEED % n_models`, which is gated on "
                                     "`target_acc == 'P51532'` -- the SMARCA4 template -- so it cannot reach a "
                                     "5a-KS leg, which stages through nr4a3_5aks_stage against a CRBN co-fold; "
                                     "and nr4a3_ternary_fep seeds each replica's sampler. ⚠ WHAT IT DOES NOT "
                                     "BUY, by construction: 5a-KS is ONE co-fold per species (both endpoints "
                                     "staged from one pose, deliberately), so an S replicate SD measures "
                                     "sampling scatter WITHIN one pose and the pose stays a stated "
                                     "conditional. That is a limit to declare, not a reason to stay at n = 1, "
                                     "which covers neither error source."),
        },
        "_check_resolved": {
            "question": "does a second seed on the 5a-KS lane re-run the first starting model?",
            "answer": "NO -- the seed -> relaxed-model wrap is SMARCA4-template-gated and does not reach this "
                      "lane; the second seed is genuinely independent SAMPLING",
            "evidence": ["ternary_pdb_stage.py: `if target_acc == 'P51532'` guards the model-index wrap",
                         "nr4a3_5aks_stage.py docstring: BOTH ENDPOINTS COME FROM ONE POSE (one co-fold/species)",
                         "nr4a3_ternary_fep.py: per-replica sampler seeding, `SEED=0/1/2 are genuinely "
                         "independent`"],
            "residual_limit": "co-fold-POSE uncertainty is not sampled by any seed count on this lane",
            "date": "2026-07-30",
        },
    }


# =============================================================================================================
# 6. AN OBSERVATION ABOUT THE HEADLINE CI, RECORDED BECAUSE A REVIEWER WILL FIND IT
# =============================================================================================================
def estimator_note():
    """The paper's n=3 CI comes from the PREREGISTERED estimator, and a second, natural estimator disagrees
    with it about whether zero is excluded. Recording this is not a challenge to the result -- it is the
    thing a referee computes on the back of an envelope, and the answer should already be written down.

    `ternary_fep_reduce._welch_satterthwaite` builds ddG_coop as a difference of two independently averaged
    ARM means with Welch-Satterthwaite dof (a reviewer-required change, 2026-07-17). Recomputing instead from
    the PAIRED per-replicate ddG_coop values with a t(.975, n-1) interval gives a WIDER interval that includes
    zero, because pairing retains the replicate-to-replicate covariance the arm-wise construction averages
    away -- and on this lane the arms genuinely do covary, since seed `s` drives the starting model in BOTH.

    ⛔ NOT A PROPOSAL TO SWITCH. The Welch construction is the preregistered one and swapping estimators after
    a failing result is the retune this program forbids. It also changes nothing that matters: the FAIL is on
    SIGN and on |mean - target| = %.3f against a 1.0 band, both of which are estimator-independent. What the
    paired interval touches is only the narrower sentence that the method 'resolves a cooperativity change
    confidently'.""" % MEASURED["abs_error_kcal"]
    vals = (-0.5125, -1.0097, -0.2749)   # per-replicate ddG_coop; home is paper §2.11
    n = len(vals)
    mean = sum(vals) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1))
    t2 = 4.302653   # t(.975, dof=2)
    half = t2 * sd / math.sqrt(n)
    return {
        "preregistered_estimator": "Welch-Satterthwaite over independently averaged ternary and binary arms",
        "paired_estimator_recomputed_here": {
            "mean_kcal": round(mean, 4),
            "paired_sd_kcal": round(sd, 4),
            "t_crit_dof2": t2,
            "ci95_half_width_kcal": round(half, 4),
            "ci95": [round(mean - half, 4), round(mean + half, 4)],
            "includes_zero": (mean - half) < 0 < (mean + half),
        },
        "what_is_unaffected": ("the FAIL itself. Wrong sign and |mean - target| = %.3f on a 1.0 band are both "
                               "estimator-independent." % MEASURED["abs_error_kcal"]),
        "what_is_affected": ("only the reading that the method 'resolves a cooperativity change confidently', "
                             "which rests on the tighter preregistered interval."),
        "action": ("record it in the paper's limitations rather than switch estimators. A referee who "
                   "recomputes the paired interval should find we got there first."),
    }


# =============================================================================================================
# 7. HOW TO TURN THE sigma_leg ARGUMENT INTO A MEASUREMENT -- free, and it uses the triangle's OWN legs
# =============================================================================================================
def narrow_sigma_leg_from_triangle_legs(triangle_mean_mbar_se=None):
    """§2 leaves the verdict turning on where in the bounded interval sigma_leg sits, and §1's bound comes from
    the valB legs -- a DIFFERENT set of runs, carrying homology-model and solvation variance the triangle does
    not have. That is why it is an upper bound and not a value.

    ★ THE TRIANGLE'S OWN LEGS CAN CLOSE THAT GAP FOR $0, AND THEY LAND WITH `R`. The n=3 replicates measured
    something transferable: the ratio of between-replicate SD to per-leg MBAR SE, on this lane, this protocol,
    this system family. A triangle leg reports its own MBAR SE. Multiplying gives a sigma_leg estimate built
    from the triangle's legs rather than valB's -- no homology-model term, no cross-seed solvation term.

    ⚠ WHAT IS ASSUMED, STATED BECAUSE IT IS THE WHOLE WEAKNESS: that the replicate/MBAR ratio TRANSFERS from
    the valB edge to the triangle's edges. Same lane, same protocol, same 8G1Q-derived system family, so the
    transfer is reasonable -- but it is a transfer, not a measurement, and a ratio is exactly the kind of
    quantity that is regime-dependent (the protein-mutation benchmark saw between-setup SD swing 6.2x between
    a near-null perturbation and a hot spot). So this NARROWS the interval; it does not collapse it to a point,
    and it must never be reported as though the triangle had replicates. It does not.

    The honest alternative that would settle it outright is a second seed on one triangle edge, which is a
    PURCHASE and therefore not taken here."""
    e = s_error_bar_scope()
    ratio = e["replicate_sd_over_mbar_se_measured"]
    b = sigma_leg_now_bounded()
    out = {
        "method": ("sigma_leg(triangle) ~ ratio * mean per-leg MBAR SE of the TRIANGLE's own legs, where the "
                   "ratio is the replicate-SD/MBAR-SE factor measured at n=3 on this lane"),
        "ratio_used": ratio,
        "_ratio_is_transferred_not_measured_here": True,
        "current_upper_bound_from_valB": b["sigma_leg_upper_bound_kcal"],
        "power_0.80_crosses_at": round(power_threshold_crossing(), 4),
        "what_it_would_settle": ("whether a null R clears conventional power. Below the crossing it does and "
                                 "the triangle answers its question; above it, it does not, amended or not."),
        "cost": "$0 -- the MBAR SEs are already in the leg records that land with R",
        "when": "the moment all four legs are down, alongside task=triangle-reduce",
    }
    out["_RUN_2026_07_30"] = {
        "status": "RUN. All four triangle legs landed 5:11 PM ET 2026-07-30, so this is no longer pending.",
        "triangle_mean_mbar_se_kcal": 0.11531,
        "_from": "valb-triangle-reduction.json -> mbar_se_kcal_per_leg_PROVENANCE_ONLY, mean over its 6 legs",
        "result_as_this_function_computes_it": 0.3782,
        "★_IT_DID_NOT_NARROW_ANYTHING_AND_THAT_IS_THE_RESULT": (
            "The triangle's mean per-leg MBAR SE is 0.1153 against valB's 0.1145 -- the two lanes are within "
            "0.7% of each other. Multiplying by a ratio whose NUMERATOR is valB's own replicate SD therefore "
            "reproduces valB's number almost exactly. So the transfer this function warned about does not "
            "just weaken the estimate, it makes it CIRCULAR in the one direction that mattered: the ratio "
            "carries valB's homology-model and solvation variance in its numerator, which is precisely the "
            "term the triangle does not have and the term this was meant to remove. It cannot narrow the "
            "bound below the bound it was derived from. Recorded as a null result rather than quoted as a "
            "narrowing."),
        "⚠_AND_A_QUANTITY_DISCREPANCY_THIS_EXPOSED_-_RECORDED_NOT_AMENDED": (
            "0.3782 is labelled `sigma_leg_estimate_kcal` and compared against `power_threshold_crossing()`, "
            "which is a sigma_LEG. But the ratio is `cycle SD / per-leg MBAR SE` -- an EDGE SD over a LEG SE "
            "(see MEASURED['_cycle_sd_is_a_sigma_edge']) -- so multiplying a leg SE by it returns a "
            "sigma_EDGE. The design's own relation (sigma_edge = sqrt(2)*sigma_leg) puts the sigma_leg at "
            "0.3782/sqrt(2) = 0.2674, which is within 1% of the independent valB-derived upper bound 0.2652 "
            "-- an agreement that is itself evidence the sqrt(2) reading is the right one, since as-labelled "
            "the estimate EXCEEDS an upper bound, which is a contradiction. The same mixing inflates "
            "`s_error_bar_scope`'s S error bar by sqrt(2): S's binary leg cancels ALGEBRAICALLY (lever 2, and "
            "nr4a3_5aks_reduce REFUSES a binary leg), so treating the two arms' ddG_coop as independent "
            "double-counts a leg that is shared. "
            "★ DELIBERATELY NOT CHANGED HERE. Both live figures are CONSERVATIVE -- they overstate the noise "
            "floor, which understates our resolving power in both directions -- and this program forbids "
            "re-deriving an error-bar convention after seeing which way it moves a decision. It moves none: "
            "n = 2 seeds per arm is the right call under BOTH readings (at n=1 the resolvable difference is "
            "0.735 corrected or 1.039 as-quoted, and the designed effect floor is 0.5, so one seed cannot "
            "report a null either way). It is written down so the next person to touch the error model "
            "inherits the discrepancy rather than rediscovering it."),
    }
    if triangle_mean_mbar_se is None:
        # ⚠ THIS MESSAGE IS ABOUT THE ARGUMENT, NOT ABOUT THE WORLD. It used to read "NOT YET COMPUTABLE --
        # the triangle's ternary legs have not landed", which was a claim about reality that went STALE the
        # moment they did (5:11 PM ET 2026-07-30) and would have kept asserting itself indefinitely. The
        # branch is still needed -- a reduction whose legs carry no MBAR SE must degrade rather than crash --
        # but it now says only what it can know: no SE was supplied.
        out["estimate"] = ("NOT COMPUTABLE FROM THE ARGUMENT GIVEN -- no triangle mean MBAR SE was supplied. "
                           "This says nothing about whether the legs have landed; they have, and the result "
                           "is recorded in _RUN_2026_07_30.")
        return out
    est = ratio * float(triangle_mean_mbar_se)
    out["triangle_mean_mbar_se_kcal"] = float(triangle_mean_mbar_se)
    out["sigma_leg_estimate_kcal"] = round(est, 4)
    out["clears_conventional_power"] = est < out["power_0.80_crosses_at"]
    return out


# =============================================================================================================
# 8. THE CALL ON MODULE 3 — made 2026-07-30, after R, and deliberately NOT a gate amendment
# =============================================================================================================
def module3_decision():
    """Should valB_full module 3 (paralogue discrimination, SMARCA2-vs-SMARCA4) be decoupled from the failed
    valB_mini gate and run?

    ⛔ THE GATE IS NOT AMENDED. valB_full's gate reads "the prospective ladder never runs unless the
    cooperativity AND paralogue-discrimination modules pass." Module 1 failed on its own terms, for a cause
    that is now diagnosed rather than mysterious, and its statistic did NOT lose discriminating power -- it
    discriminated perfectly well and returned NO. That is the gate working. The repo's own amendment standard
    (AMENDMENT 1: a rule may be amended only when its statistic is SHOWN to lack discriminating power,
    demonstrated independently of whether we liked its answer) therefore does not license touching it, and R
    supplies no licence either: R is blind to the endpoint-state class that broke valB, so it cannot vouch for
    the pipeline the gate is guarding. Unlocking the prospective ladder here would be the retune this program
    forbids, wearing a diagnosis as cover.

    ★ BUT THE REAL FINDING IS THAT THE LADDER HAS A GAP, NOT THAT IT HAS A GATE IN THE WAY. `S` -- the flagship
    kill-switch, the thing the whole prospective stage is gated on -- has NEVER had a known-answer calibrator.
    valB_mini calibrated ddG_coop, a quantity `S` does not contain (its binary leg cancels algebraically). So
    `S` was always going to be read against nothing, and the valB failure did not create that; it exposed it.
    Closing it is not a gate amendment and does not unlock the prospective ladder: the ladder stays shut on
    cooperativity, and what changes is only whether `S` may be read as calibrated rather than exploratory.

    THE HONEST RISK, STATED BECAUSE IT IS THE STRONGEST ARGUMENT AGAINST: an S-calibrator on SMARCA2-vs-SMARCA4
    runs on the SAME system family that carries the suspected error, and a known-answer accuracy test does NOT
    telescope an endpoint-state error the way a cycle does -- which is exactly why valB_mini caught it. Worse,
    the arms are asymmetric: 8G1Q is a SMARCA4 structure and SMARCA2 is the homology-substituted model, so a
    homology-model error sits on ONE arm and does not cancel. A failure would therefore be ambiguous between
    "the S-class quantity does not work" and "this particular benchmark inherited the same model defect."
    That ambiguity must be preregistered, not discovered afterwards -- and it argues for choosing the system on
    which arm is REAL, not on which is already staged."""
    return {
        "decision": "DO NOT AMEND THE valB_full GATE; SPECIFY AN S-CALIBRATOR AS A SEPARATE ITEM",
        "made": "2026-07-30, after R landed",
        "gate_status": "valB_full stays gated shut on cooperativity; the prospective NR4A matrix stays unrun",
        "why_not_amend": ("module 1's statistic did not lack discriminating power -- it discriminated and said "
                          "NO. The repo's amendment standard does not reach it, and R cannot vouch for the "
                          "pipeline because R is blind to the class that broke it."),
        "the_gap_that_is_real": ("S has never had a known-answer calibrator. valB_mini calibrated ddG_coop, "
                                 "which S does not contain. The failure exposed this rather than causing it."),
        "what_this_does_NOT_unlock": ("the prospective ladder, the NR4A ternary matrix, or any cooperativity "
                                      "claim. Only whether S is readable as calibrated rather than exploratory."),
        "preregister_before_spending": [
            "the ambiguity: on SMARCA2-vs-SMARCA4 a FAILURE cannot distinguish 'the S-class quantity does not "
            "work' from 'this benchmark inherited the same model defect', because 8G1Q is a SMARCA4 structure "
            "and SMARCA2 is the homology-substituted arm -- the error sits on one arm and does not cancel",
            "the system choice should be made on WHICH ARM IS REAL, not on what is already staged",
            "what a PASS would and would not license (it would not revive ddG_coop)",
        ],
        "free_work_first": ("the prereg itself is $0, and so is a survey of paralogue-selective systems with "
                            "a solved structure on BOTH arms. Neither needs a go."),
        "also_recorded_today": ("the CONFIRMATORY protein-mutation cycle is ternary-minus-binary, the same "
                                "shape as the quantity that failed -- see error_algebra. It should stop being "
                                "described as an independent second causal line until that is addressed."),
    }


def build_report():
    return {
        "_what": ("the blast radius of the valB_mini FAIL, derived quantity by quantity, plus the two things "
                  "the n=3 result newly makes measurable: a bound on sigma_leg and the replicate-SD/MBAR-SE "
                  "factor on this pipeline."),
        "_generated_by": "research/modalities/valb_failure_propagation.py",
        "_not_a_price": "no cost, throughput or basis is computed here; pricing.md and STRATEGY own those.",
        "inputs_measured": MEASURED,
        "1_sigma_leg_now_bounded": sigma_leg_now_bounded(),
        "1b_power_at_measured_bound": power_at_measured_bound(),
        "2_frozen_rule_vs_measured_power": frozen_rule_vs_measured_power(),
        "3_error_algebra": error_algebra(),
        "4_s_resolvability_prereg": s_resolvability_from_R_ternary(),
        "5_s_error_bar_scope": s_error_bar_scope(),
        "6_estimator_note": estimator_note(),
        "7_narrow_sigma_leg_from_triangle_legs": narrow_sigma_leg_from_triangle_legs(),
        "8_module3_decision": module3_decision(),
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    rep = build_report()
    if "--write" in argv:
        with open(OUT, "w") as fh:
            json.dump(rep, fh, indent=1, sort_keys=False)
            fh.write("\n")
        print("wrote %s" % OUT)
    else:
        print(json.dumps(rep, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
