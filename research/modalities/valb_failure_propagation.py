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
def frozen_rule_vs_measured_power():
    """`binary_departure_prereg` demotes a null closure to UNDERPOWERED whenever `sigma_leg > 0.2`.

    THAT 0.2 IS A HAND-SET PROXY FOR "the power is too low to read a null", chosen when sigma_leg was unknown
    to a factor of 15.6 and a proxy was the only thing available. The bound in §1 now sits ABOVE 0.2 while the
    ACTUAL power at that same bound is high -- so the frozen rule and the quantity it was standing in for point
    in opposite directions.

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

    frozen_at_hi = binary_departure_prereg(R_ternary=0.0, R_binary=0.0, sigma_leg=hi)
    return {
        "frozen_proxy": "binary_departure_prereg demotes BINARY_CANCELS -> UNDERPOWERED when sigma_leg > 0.2",
        "measured_sigma_leg_upper_bound": hi,
        "frozen_rule_fires": hi > 0.2,
        "verdict_the_frozen_rule_would_return_on_a_null": frozen_at_hi["verdict"],
        "actual_power_to_detect_1.478_at_that_sigma": power_1478,
        "the_discrepancy": ("the frozen rule fires at sigma_leg=%.4f and would call a null UNDERPOWERED. The "
                            "power it is standing in for is %.2f AT THAT SAME BOUND -- and since the bound is "
                            "an UPPER bound, the true power is at least that. So the proxy is not clearly "
                            "wrong: %.2f is mediocre, and whether UNDERPOWERED is the right word depends on "
                            "where in [%.3f, %.4f] the true sigma_leg sits. What is wrong is that a binary "
                            "proxy is deciding it at all, when the power is computable."
                            % (hi, power_1478, power_1478, b["sigma_leg_lower_bound_kcal"], hi)),
        "action_taken_here": "NONE. Recorded before R lands; the rule is untouched.",
        "action_proposed_to_trimcrae": ("a dated defect-fix replacing the 0.2 proxy with a COMPUTED power "
                                        "threshold, so the verdict reports the actual power alongside it "
                                        "instead of a fire/don't-fire flag. Routed the same way as the "
                                        "admits-zero gate defect. $0, no spend attached, and it must be "
                                        "decided on the arithmetic rather than on whether we like R."),
        "the_honest_residual": ("even amended, a null R at the upper bound is worth ~%.2f power, which does "
                                "not make a null strong evidence. The triangle can still ADMIT the cycle more "
                                "confidently than it can convict it -- which is the design's own asymmetry, "
                                "not a new problem." % power_1478),
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
        "options": {
            "finish_as_configured": ("buy the two parked legs, report S as a point estimate, and label it "
                                     "exploratory. Retires paper §2.10(d) 'the causal test has not been run' "
                                     "but cannot support a null."),
            "add_one_seed_per_arm": ("two further legs give S a real replicate SD and make a null readable. "
                                     "⚠ CHECK BEFORE BUYING: the SMARCA2 lane's seed -> relaxed-model map "
                                     "wraps at n_models=2 (tests/test_edge_reps_seed_independence.py). "
                                     "Whether the 5a-KS co-fold staging has the same wrap is UNVERIFIED here "
                                     "and must be checked, not assumed, or the second seed re-runs the first "
                                     "model and buys no independence."),
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
