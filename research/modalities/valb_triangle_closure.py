#!/usr/bin/env python3
"""Closure arithmetic, leg accounting and CORRECTED pricing for the valB synthetic closure triangle.

Companion to `valb_triangle_chem.py` (which tests whether the triangle can be BUILT). This module answers the
four quantitative questions that decide whether it should be BOUGHT, and it answers each of them by derivation
or simulation rather than assertion. Pure stdlib; no network, no GPU, no chemistry stack.

  1. DOES THE TRIANGLE CLOSE, given T1's as-run direction and endpoints? (`closure_identity`)
  2. WHAT CAN A NON-ZERO RESIDUAL DIAGNOSE, AND WHAT IS IT BLIND TO? (`state_function_blindness`)
     The load-bearing result in this file. A closure residual is identically zero for ANY error that is a
     function of the endpoint STATE -- force field, homology model, partial charges, protonation. It sees only
     the PATH-dependent part. That is provable in two lines and is demonstrated numerically here, and it
     determines the decision-tree answer.
  3. HOW BIG MUST |R| BE TO MEAN ANYTHING? (`closure_noise_floor`)
     R is a +-1 combination of six leg free energies, so its noise is sqrt(6) x the per-leg noise -- and the
     per-leg noise for this lane is known only to within a factor of ~15 (MBAR SE 0.045 vs the repo's assumed
     replicate SD 0.7). The detection threshold inherits that uncertainty.
  4. WHAT DOES IT ACTUALLY COST, on the corrected basis? (`price_triangle`)
     Priced in STEPS, because iteration counts are not comparable across protocols: 1 fs warmup iterations and
     2 fs production iterations cost the same 1250 force evaluations each, which is exactly why the leg is
     2800 iterations and not 2400. Two further corrections to the design's ~$5.9 are derived here, one of which
     (T1's replicates do not exist) is LARGER than the iteration correction.

EVERY INPUT IS SOURCED. Protocol lengths come from `nr4a3_ternary_fep` (EQUILIBRATION_NS / PRODUCTION_NS) and
`rbfe_spot_driver._iters_from_time`; the per-iteration rate and the $/reference-GPU-h come from the repo's
measured basis (`vast_cost_model` + `vast-ladder-repricing.json`). No new measurement is invented.
"""
from __future__ import annotations

import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "valb-triangle-closure.json")

# =============================================================================================================
# PROTOCOL CONSTANTS -- every one traceable to source, none re-estimated here
# =============================================================================================================
STEPS_PER_ITERATION = 1250          # openmmtools mc_steps; an iteration is 1250 force evaluations at ANY dt
EQUILIBRATION_NS = 1.0              # nr4a3_ternary_fep.EQUILIBRATION_NS
PRODUCTION_NS = 5.0                 # nr4a3_ternary_fep.PRODUCTION_NS
WARMUP_DT_FS = 1.0                  # RBFE_WARMUP_TIMESTEP_FS as-run (the reduced-dt warmup, 2026-07-19)
PROD_DT_FS_ASRUN = 2.0              # RBFE_TIMESTEP_FS as-run for valB_mini
SEC_PER_ITERATION = 16.0            # MEASURED median on a Vast RTX 4090, 146,284-particle ternary assembly
USD_PER_REF_GPU_H = 0.1372          # vast-ladder-repricing.json -> plan_usd_per_reference_gpu_h
USD_PER_REF_GPU_H_LO = 0.057        # best live offer
USD_PER_REF_GPU_H_HI = 0.3094       # market median (what ignoring the ranking costs)

# ---------------------------------------------------------------------------------------------------------
# SOLVENT LEG -- carried as a RATE, not as a total, because the two lanes have different leg lengths.
#
# A solvent leg is NOT ~1/28 of a ternary leg just because the box is ~5k particles against ~142k: it runs the
# SAME 12 lambda-windows for the SAME number of iterations and is latency-bound, not throughput-bound, at that
# size. The only solvent-leg figure the repo has is the binary NR4A3 RBFE lane's (pricing.md section B:
# complex ~9.1 / solvent ~4.1 ref GPU-h).
#
# ⚠ That 4.1 is stated on the BINARY lane's 2400-iteration leg. Carrying it across as a TOTAL would import a
# 2400-basis number into a 2800-basis calculation -- precisely the error this module exists to correct. So it
# is converted to a per-iteration rate first (4.1 h / 2400 iters = 6.15 s/iter) and re-multiplied by the
# ternary lane's own iteration count.
SOLVENT_SEC_PER_ITER_EST = 4.1 * 3600.0 / 2400.0        # 6.15 s/iter, from the binary lane's solvent leg
SOLVENT_LEG_BASIS = ("a RATE (~6.15 s/iter) backed out of the binary NR4A3 RBFE lane's solvent leg "
                     "(pricing.md section B: ~4.1 ref GPU-h over its 2400-iteration leg) and re-multiplied by "
                     "the ternary lane's 2800 iterations. ESTIMATE, not a ternary-lane measurement, and the "
                     "two lanes' solvent boxes differ (a 59-heavy-atom PROTAC vs a ~20-heavy-atom warhead).")


def solvent_leg_ref_gpu_h(prod_dt_fs=PROD_DT_FS_ASRUN):
    return steps_per_leg(prod_dt_fs=prod_dt_fs)["total_iterations"] * SOLVENT_SEC_PER_ITER_EST / 3600.0


def steps_per_leg(prod_dt_fs=PROD_DT_FS_ASRUN, warmup_dt_fs=WARMUP_DT_FS,
                  equil_ns=EQUILIBRATION_NS, prod_ns=PRODUCTION_NS):
    """Force evaluations in one alchemical leg, PER LAMBDA-WINDOW-SET, in STEPS.

    Steps are the invariant unit; iterations are not. `rbfe_spot_driver._iters_from_time` derives the warmup
    iteration count from the WARMUP integrator's timestep, so a 1 ns equilibration at 1 fs is 800 iterations,
    not the 400 a 2 fs assumption gives -- and every warmup iteration costs the same 1250 force evaluations as
    a production one. Working in steps makes that impossible to get wrong, and makes 2 fs and 4 fs protocols
    directly comparable."""
    warm = equil_ns * 1e6 / warmup_dt_fs        # ns -> fs -> steps
    prod = prod_ns * 1e6 / prod_dt_fs
    return {"warmup_steps": warm, "production_steps": prod, "total_steps": warm + prod,
            "warmup_iterations": warm / STEPS_PER_ITERATION,
            "production_iterations": prod / STEPS_PER_ITERATION,
            "total_iterations": (warm + prod) / STEPS_PER_ITERATION}


def ternary_leg_ref_gpu_h(prod_dt_fs=PROD_DT_FS_ASRUN):
    """Reference-card GPU-hours for one TERNARY leg, from steps x the measured per-step rate."""
    s = steps_per_leg(prod_dt_fs=prod_dt_fs)
    sec_per_step = SEC_PER_ITERATION / STEPS_PER_ITERATION
    return s["total_steps"] * sec_per_step / 3600.0


# =============================================================================================================
# 1. THE CLOSURE IDENTITY
# =============================================================================================================
# Sign convention is `ternary_coop.ddg_coop`, verified there against synthetic K_D pairs:
#     ddG_coop(A->B) = ddG_alch,ternary(A->B) - ddG_alch,binary(A->B) = dG_coop(B) - dG_coop(A)
# so ddG_coop is a DIFFERENCE OF A STATE FUNCTION and any oriented cycle sums to zero by construction.
TRIANGLE = [("T1", "cmpd1", "cmpd4", +1), ("T2", "cmpd4", "cmpd4prime", +1),
            ("T3", "cmpd1", "cmpd4prime", -1)]


def closure_identity(dg_coop_by_state=None):
    """Verify R = ddG_coop(T1) + ddG_coop(T2) - ddG_coop(T3) == 0 for an exact method, with T1 in its AS-RUN
    direction (cmpd1 -> cmpd4, which is what r0 measured forward). Evaluated on arbitrary state values, so a
    zero here is the identity holding, not a coincidence of one dataset."""
    st = dg_coop_by_state or {"cmpd1": -1.4771, "cmpd4": -0.5332, "cmpd4prime": +2.7183}
    edges = {name: st[b] - st[a] for name, a, b, _ in TRIANGLE}
    R = sum(sign * edges[name] for name, _, _, sign in TRIANGLE)
    return {
        "orientation": {name: "%s -> %s (coefficient %+d)" % (a, b, s) for name, a, b, s in TRIANGLE},
        "T1_direction_matches_r0": True,
        "T1_direction_note": "r0 measured cmpd1 -> cmpd4 FORWARD (ddG_coop = ternary - binary = -0.534). The "
                             "triangle uses that same orientation with coefficient +1, so r0 enters unaltered "
                             "and is genuinely reused rather than re-bought.",
        "edge_values_on_test_states": edges,
        "residual_R": R,
        "closes": abs(R) < 1e-12,
        "why": "ddG_coop(A->B) = dG_coop(B) - dG_coop(A) is the difference of a STATE FUNCTION "
               "(dG_coop(x) = -RT ln alpha_x), so every oriented cycle telescopes to exactly zero for an exact "
               "method -- with no reference to any measured alpha. That is the whole point of the design.",
    }


def closure_decomposition(legs):
    """R decomposes into TWO independently-meaningful closures, and reporting only R is strictly weaker.

    ddG_coop = dG_ternary - dG_binary, so
        R = [dG_t(T1)+dG_t(T2)-dG_t(T3)] - [dG_b(T1)+dG_b(T2)-dG_b(T3)] = R_ternary - R_binary
    Each of R_ternary and R_binary is itself a closed cycle in its own environment and is separately zero for an
    exact method. Therefore R = 0 does NOT imply the cycle is consistent: R_ternary and R_binary can each be
    large and cancel. Both are computed from the SAME legs at zero extra cost, so there is no reason to report
    only R. If solvent legs are also run, R_solvent is a third, independent closure.

    `legs` = {"ternary": {T1,T2,T3}, "binary": {...}, optional "solvent": {...}} of dG_morph values."""
    out = {}
    for env, vals in legs.items():
        out["R_%s" % env] = sum(sign * vals[name] for name, _, _, sign in TRIANGLE if name in vals)
    if "ternary" in legs and "binary" in legs:
        out["R_coop"] = out["R_ternary"] - out["R_binary"]
        out["cancellation_risk"] = abs(out["R_coop"]) < 0.1 and (
            abs(out["R_ternary"]) > 0.5 or abs(out["R_binary"]) > 0.5)
    out["_rule"] = ("REPORT R_ternary AND R_binary SEPARATELY, never R_coop alone. R_coop = R_ternary - "
                    "R_binary, so a clean-looking R_coop can be two large closures cancelling. Both come free "
                    "from the same legs.")
    return out


# =============================================================================================================
# 2. WHAT A CLOSURE RESIDUAL CAN AND CANNOT DIAGNOSE  <-- the decisive result
# =============================================================================================================
def state_function_blindness(trials=2000, seed=20260725):
    """A closure residual is IDENTICALLY ZERO for every error that is a function of the endpoint state.

    Proof (two lines). Write the computed edge value as
        ddG_calc(A->B) = ddG_true(A->B) + e(A->B).
    Around a closed cycle the true terms telescope to zero, so R = sum_cycle e. If the error is a per-endpoint
    bias, e(A->B) = eps(B) - eps(A) for some state function eps, then sum_cycle e telescopes to zero as well.
    Hence R measures ONLY the NON-CONSERVATIVE (path-dependent) part of the error.

    Consequence, and it is the reason this module exists: the error classes the convergence analysis left
    standing for r0's 1.478 kcal/mol miss -- a wrong force field at the interface, the SMARCA4->SMARCA2
    homology substitution, NAGL partial charges, a protonation assignment -- are ALL per-endpoint state
    functions. A closure triangle is mathematically blind to every one of them. It is a PATH-error detector.

    Demonstrated numerically: random per-endpoint biases give R = 0 to machine precision; random per-edge path
    errors do not."""
    rng = random.Random(seed)
    worst_state, worst_path = 0.0, 0.0
    for _ in range(trials):
        eps = {s: rng.gauss(0, 5.0) for s in ("cmpd1", "cmpd4", "cmpd4prime")}
        true = {s: rng.gauss(0, 5.0) for s in ("cmpd1", "cmpd4", "cmpd4prime")}
        # (a) state-function error only
        edges = {n: (true[b] + eps[b]) - (true[a] + eps[a]) for n, a, b, _ in TRIANGLE}
        worst_state = max(worst_state, abs(sum(s * edges[n] for n, _, _, s in TRIANGLE)))
        # (b) add an independent per-edge PATH error
        path = {n: rng.gauss(0, 0.5) for n, _, _, _ in TRIANGLE}
        edges2 = {n: edges[n] + path[n] for n in edges}
        worst_path = max(worst_path, abs(sum(s * edges2[n] for n, _, _, s in TRIANGLE)))
    return {
        "trials": trials,
        "max_abs_R_with_state_function_error_only": worst_state,
        "max_abs_R_with_added_path_error": worst_path,
        "state_function_errors_are_invisible": worst_state < 1e-10,
        "INVISIBLE_to_closure": [
            "force-field error at the ternary interface (a per-endpoint state function)",
            "the SMARCA4->SMARCA2 homology substitution (same Hamiltonian for every endpoint)",
            "NAGL partial-charge error (per molecule, hence per endpoint)",
            "protonation / tautomer assignment error (per endpoint)",
            "reference-data error (alpha_SPR is an APPARENT cooperativity) -- not in the calculation at all",
        ],
        "VISIBLE_to_closure": [
            "insufficient lambda sampling / hysteresis / poor phase-space overlap (path-dependent, edge-specific)",
            "ENDPOINT-STATE INCONSISTENCY: the same compound built differently in two edges (a different pose, "
            "conformer, or -- as this lane has actually produced -- a different bond-order template). This is "
            "the class of bug a reverse leg CANNOT see, because a 2-cycle reuses its own two endpoints.",
            "atom-map-dependent error, where two edges' hybrid topologies are not mutually consistent",
        ],
        "_verdict": "A closure triangle is a PATH-error and endpoint-consistency detector. It is NOT an "
                    "accuracy control and it cannot see the model or reference-data error classes that the r0 "
                    "convergence analysis left standing. The known-answer accuracy requirement stays OPEN.",
    }


# =============================================================================================================
# 3. THE NOISE FLOOR OF R
# =============================================================================================================
def closure_noise_floor(sigma_leg_values=(0.045, 0.2, 0.5, 0.7), trials=40000, seed=7):
    """R is a +-1 combination of SIX leg free energies, so SD(R) = sqrt(6) x sigma_leg for independent legs --
    equivalently sqrt(3) x sigma_edge, where sigma_edge = sqrt(2) sigma_leg is the per-edge ddG_coop spread.

    The problem is that sigma_leg for this lane is known only to within a factor of ~15: the MBAR SE on r0's
    ternary leg is 0.045, while the repo's own assumed between-replicate SD is 0.7. The MBAR SE is a LOWER
    bound (it does not see slow modes); the replicate SD is an UPPER bound for a same-seed triangle (it
    includes the homology-model swap, since ternary seed s uses the s%n-th relaxed model -- which is why all
    three edges of the triangle MUST be run at the same seed).

    Reported: the analytic SD, the 95th percentile of |R| under the null (the smallest |R| that is evidence),
    and -- the decision-relevant number -- the power to detect a path error the size of r0's own miss."""
    rng = random.Random(seed)
    rows = []
    for sl in sigma_leg_values:
        sd_analytic = math.sqrt(6.0) * sl
        raw = [sum(rng.gauss(0, sl) for _ in range(6)) for _ in range(trials)]
        draws = sorted(abs(x) for x in raw)
        p95 = draws[int(0.95 * trials)]
        mu = sum(raw) / len(raw)
        sd_mc = math.sqrt(sum((x - mu) ** 2 for x in raw) / (len(raw) - 1))
        # power to detect a path error of size delta, at the p95 null threshold
        power = {}
        for delta in (0.5, 1.0, 1.478, 2.0):
            hit = sum(1 for _ in range(trials)
                      if abs(delta + sum(rng.gauss(0, sl) for _ in range(6))) > p95)
            power["detect_%.3f" % delta] = hit / trials
        rows.append({"sigma_leg": sl, "sigma_edge_implied": round(math.sqrt(2) * sl, 4),
                     "SD_R_analytic": round(sd_analytic, 4), "SD_R_monte_carlo": round(sd_mc, 4),
                     "null_p95_abs_R": round(p95, 4),
                     "power_at_n1": {k: round(v, 4) for k, v in power.items()}})
    return {
        "n_legs_in_R": 6,
        "SD_R_formula": "SD(R) = sqrt(6) * sigma_leg = sqrt(3) * sigma_edge (independent legs, +-1 coefficients)",
        "sigma_leg_is_unknown_by_a_factor_of": round(0.7 / 0.045, 1),
        "sigma_leg_bounds": {"lower_MBAR_SE_r0_ternary": 0.045,
                             "upper_repo_assumed_replicate_SD": 0.7,
                             "note": "the replicate SD upper bound includes homology-model sensitivity (seed s "
                                     "-> model s%n). A same-seed triangle removes that term, so the true value "
                                     "sits below 0.7 -- but nothing in this lane has measured it.",
                             "SUPERSEDED_2026_07_30": "the trailing clause of `note` is no longer true and is "
                                     "kept only because the 0.7 figure it explains is still the value this "
                                     "function is called with by default. The valB_mini n=3 replicates "
                                     "MEASURED the spread, and converting it through this function's own "
                                     "SD relation bounds sigma_leg well below 0.7. The bound, the two reasons "
                                     "it is an UPPER bound, and the re-graded power are derived in "
                                     "valb_failure_propagation.sigma_leg_now_bounded (not imported here -- "
                                     "that module imports this one, and the dependency must not reverse)."},
        "rows": rows,
        "_asymmetry": "A SMALL |R| is strong evidence (it bounds the path error AND the noise at once, since "
                      "both would have to be small). A LARGE |R| at n=1 is AMBIGUOUS -- one draw cannot "
                      "separate a systematic path error from an unlucky sample. So the n=1 scout can ADMIT the "
                      "cycle but cannot convict it.",
    }


# =============================================================================================================
# 4. LEG ACCOUNTING -- does the paralogue-independence cancellation identity apply here?
# =============================================================================================================
def leg_accounting():
    """STRATEGY's identity: a paralogue panel is N ternary LEGS + 1 shared binary + 1 shared solvent, not N
    edges, because `binary_<e3>` (E3 machinery + PROTAC, NO target) and `solvent` (ligand in water) are both
    paralogue-independent.

    TESTED HERE, NOT ASSUMED. The identity shares legs across TARGETS for a FIXED ligand pair. The triangle
    varies the LIGAND PAIR on a FIXED target. A binary leg is an alchemical morph of the ligand inside VCB, so
    it is a function of the ligand pair -- three different pairs, three different binary legs. Nothing is
    shared. Claiming the identity here would underprice the triangle by ~2x.

    What DOES cancel, and Lane 5's design already uses it: the SOLVENT leg cancels inside ddG_coop = ternary -
    binary, so a triangle whose only deliverable is R needs ZERO solvent legs. `expand_pilot_legs()` adds one
    per morph unconditionally, so the pipeline as it stands would run 3 legs per edge where 2 suffice."""
    return {
        "identity_under_test": "a panel is N ternary legs + 1 shared binary + 1 shared solvent, not N edges",
        "applies_to_the_triangle": False,
        "reason": "the identity shares legs across TARGETS at fixed ligand pair; the triangle varies the "
                  "LIGAND PAIR at fixed target. binary_vhl is an alchemical morph of the ligand inside VCB, so "
                  "it changes with the pair. Three pairs => three binary legs, nothing shared.",
        "cross_check_no_leg_is_shared": {
            "T1": "cmpd1->cmpd4", "T2": "cmpd4->cmpd4prime", "T3": "cmpd1->cmpd4prime",
            "distinct_ordered_pairs": 3, "shared_legs": 0},
        "what_DOES_cancel": "the SOLVENT leg cancels exactly inside ddG_coop = ternary - binary, so a closure "
                            "triangle needs 2 legs per edge, not 3.",
        "pipeline_gap": "nr4a3_ternary_fep.expand_pilot_legs() adds a solvent leg per distinct morph "
                        "unconditionally. Run as-is, the triangle would buy 2 solvent legs it does not need "
                        "for R -- unless they are bought DELIBERATELY, for the reason in `solvent_prescout`.",
        "forward_looking": "binary legs ARE target-independent, so if any triangle edge is later replicated "
                           "against a second known-answer system (VHL-BRD4) its binary legs transfer unchanged.",
    }


# =============================================================================================================
# 5. PRICE, on the corrected 2800-iteration / 3.5e6-step basis
# =============================================================================================================
def price_triangle(prod_dt_fs=PROD_DT_FS_ASRUN):
    """Cost, derived from STEPS. Three corrections to the design's ~$5.9 at n=1 / ~$17.6 at n=3, in increasing
    order of size:

      (a) THE ITERATION BASIS. The as-run leg is 2800 equal-cost iterations (800 warmup at 1 fs + 2000
          production at 2 fs), not 2400. +16.7% on every 2 fs ternary figure. This is the correction the design
          was written before.
      (b) SOLVENT LEGS. Not needed for R (they cancel), but the pipeline adds them. Priced separately so the
          choice is explicit rather than accidental.
      (c) T1's REPLICATES DO NOT EXIST. The n=1 scout reuses r0 correctly. But an n=3 triangle needs THREE
          replicates of ALL THREE edges -- and T1 has only r0. So the n=3 design silently includes buying r1
          and r2 of the edge already run, which is precisely the spend the r0 verdict argued against. That is
          +2 edges' worth of legs, and it is the LARGEST of the three corrections."""
    leg_h = ternary_leg_ref_gpu_h(prod_dt_fs)
    s = steps_per_leg(prod_dt_fs=prod_dt_fs)
    old_leg_h = leg_h * 2400.0 / s["total_iterations"]      # what the 2400-iteration basis would have given

    def money(ref_h):
        return {"ref_gpu_h": round(ref_h, 1),
                "plan_usd": round(ref_h * USD_PER_REF_GPU_H, 2),
                "range_usd": [round(ref_h * USD_PER_REF_GPU_H_LO, 2),
                              round(ref_h * USD_PER_REF_GPU_H_HI, 2)]}

    variants = {
        "n1_scout_R_only (2 new edges x ternary+binary; r0 reused as T1)": money(4 * leg_h),
        "n1_scout_plus_solvent (as expand_pilot_legs would actually run it)":
            money(4 * leg_h + 2 * solvent_leg_ref_gpu_h(prod_dt_fs)),
        "solvent_only_prescout (2 new SOLVENT legs; T1's solvent leg already ran)":
            money(2 * solvent_leg_ref_gpu_h(prod_dt_fs)),
        "n3_as_the_design_prices_it (2 new edges x 3 replicas -- INCOMPLETE, see (c))": money(12 * leg_h),
        "n3_HONEST (all three edges at n=3 => 12 new legs + T1's r1,r2 = 16 legs)": money(16 * leg_h),
    }
    return {
        "basis": {
            "steps_per_leg": s,
            "steps_are_the_unit": "iteration counts are NOT comparable across protocols -- a 1 fs warmup "
                                  "iteration and a 2 fs production iteration each cost 1250 force evaluations, "
                                  "which is exactly why the leg is 2800 iterations rather than 2400.",
            "sec_per_iteration_measured": SEC_PER_ITERATION,
            "ternary_leg_ref_gpu_h": round(leg_h, 3),
            "ternary_leg_ref_gpu_h_on_the_OLD_2400_basis": round(old_leg_h, 3),
            "iteration_basis_correction": round(leg_h / old_leg_h, 4),
            "usd_per_reference_gpu_h": USD_PER_REF_GPU_H,
            "solvent_leg_ref_gpu_h_ESTIMATE": round(solvent_leg_ref_gpu_h(prod_dt_fs), 2),
            "solvent_sec_per_iter_ESTIMATE": round(SOLVENT_SEC_PER_ITER_EST, 2),
            "solvent_leg_basis": SOLVENT_LEG_BASIS,
            "binary_leg_priced_at_the_TERNARY_rate": True,
            "binary_leg_conservatism": "the ~16 s/iter rate was measured on the 146,284-particle TERNARY "
                                       "assembly and is applied here to the binary leg as well. The binary "
                                       "assembly is E3 machinery + PROTAC with NO target, so it lacks the "
                                       "SMARCA2 bromodomain -- ~1,900 of the 7,388 solute atoms by the "
                                       "convergence analysis's own chain census -- and its solvated box is "
                                       "correspondingly smaller. So EVERY price here is a CEILING. The true "
                                       "figure is lower by an amount nobody has measured, and this module does "
                                       "not invent one.",
        },
        "variants": variants,
        "design_quoted": {"n1_usd": 5.9, "n3_usd": 17.6,
                          "note": "computed on the 2400-iteration basis and on 12 legs at n=3."},
        "corrections": {
            "a_iteration_basis_pct": round((leg_h / old_leg_h - 1) * 100, 1),
            "b_solvent_legs_usd_if_run": round(2 * solvent_leg_ref_gpu_h(prod_dt_fs) * USD_PER_REF_GPU_H, 2),
            "c_n3_needs_T1_replicates": "the n=3 triangle is 16 legs, not 12 (+33%), because T1 has only r0",
        },
    }


def price_at_4fs():
    """If RUNG 2b adopts 4 fs, every leg above scales by the STEP ratio -- 0.643, not 0.5. The warmup is pinned
    at 1 fs either way, so only the production half of the step budget halves."""
    a = steps_per_leg(prod_dt_fs=2.0)["total_steps"]
    b = steps_per_leg(prod_dt_fs=4.0)["total_steps"]
    return {"steps_2fs": a, "steps_4fs": b, "ratio": round(b / a, 4),
            "note": "0.643, not 0.5 -- a '2x cheaper at 4 fs' claim overstates the saving by ~36%. The 4 fs "
                    "decision is RUNG 2b's and is not assumed here; the 2 fs price is the one to quote.",
            "n1_scout_usd_at_4fs": round(4 * ternary_leg_ref_gpu_h(4.0) * USD_PER_REF_GPU_H, 2)}


# =============================================================================================================
# 6. THE DECISION TREE, keyed on the reverse leg -- and a test of "worth buying under either branch"
# =============================================================================================================
def decision_tree():
    """The design asserts the triangle is worth buying under EITHER branch of the reverse-leg result. Tested
    against section 2's blindness result rather than inherited.

    The test is simple and it is decisive: each branch names a CLASS of error, and closure either can or cannot
    see that class."""
    return {
        "branch_A": {
            "trigger": "|dG_fwd + dG_rev| <~ 0.3 kcal/mol (no hysteresis)",
            "what_it_implies": "the alchemical path is internally consistent, so r0's 1.478 systematic lives "
                               "in the MODEL (homology substitution, force field, NAGL charges, protonation) "
                               "or in the REFERENCE DATA (alpha_SPR is an apparent cooperativity).",
            "can_closure_see_that_class": False,
            "why": "every error class branch A names is a per-endpoint STATE FUNCTION or is external to the "
                   "calculation. Section 2 proves closure is identically zero for all of them. Under branch A "
                   "the triangle's expected residual is ~0 whether or not the programme's actual problem "
                   "exists, so it cannot discriminate 'the method is right' from 'the model is wrong'.",
            "design_claim": "the triangle 'attacks both candidate causes at once'",
            "verdict": "REFUTED for diagnosis. The triangle would return a clean R and diagnose nothing about "
                       "r0. It still yields a path-error resolution floor and an endpoint-consistency check, "
                       "which are publishable methods results -- but they are not what branch A needs.",
        },
        "branch_B": {
            "trigger": "|dG_fwd + dG_rev| >~ 1.0 kcal/mol (real hysteresis)",
            "what_it_implies": "a slow degree of freedom orthogonal to lambda; a path error.",
            "can_closure_see_that_class": True,
            "why": "path error is exactly the non-conservative component closure measures.",
            "verdict": "REDUNDANT, THEN STALE. The reverse leg has already established that path error exists, "
                       "on the edge already paid for, for 2 legs. The design's own branch-B instruction is "
                       "'fix the protocol first' -- and a triangle bought before the fix measures the OLD "
                       "protocol, so it must be re-bought afterwards. Buying it now is buying a measurement "
                       "you will discard.",
        },
        "the_claim_under_test": "the closure network is worth buying either way",
        "verdict": "NOT SUPPORTED AS STATED. Under branch A closure is provably blind to the live hypothesis; "
                   "under branch B it duplicates a cheaper instrument and goes stale on the fix. The triangle "
                   "has ONE genuinely unique capability -- detecting ENDPOINT-STATE INCONSISTENCY across "
                   "independently built edges, which a 2-cycle (fwd+rev) structurally cannot see because it "
                   "reuses its own two endpoints. That is a real gap and this lane has actually produced that "
                   "bug class (the rev leg's base_smiles/bond-order-template defect). It is the honest reason "
                   "to buy the triangle, and it is a different reason from the one the design gives.",
        "already_in_hand": "the fwd+rev pair now running IS a degenerate 2-cycle, i.e. the programme's first "
                           "cycle-closure instrument, arriving at zero marginal cash cost. 'No cycle closure "
                           "exists' is true historically and is being fixed by the run already in flight.",
        "cost_per_edge_comparison": {
            "reverse_leg": "2 new legs to close a 2-cycle on 1 edge = 2.0 legs/edge",
            "closure_triangle": "4 new legs to close a 3-cycle on 3 edges = 1.33 legs/edge",
            "reading": "the triangle is cheaper PER EDGE, but only if all three edges were wanted anyway. For "
                       "diagnosing one edge, the reverse leg is cheaper in absolute terms.",
        },
    }


def two_cycle_vs_three_cycle(trials=4000, seed=1234):
    """WHAT THE TRIANGLE ADDS OVER THE REVERSE LEG ALREADY IN FLIGHT -- demonstrated, not asserted.

    The forward/reverse pair now running IS a closed cycle: 1 -> 4 -> 1, residual |dG_fwd + dG_rev|, which is
    the preregistered antisymmetry check. So the programme's first cycle-closure instrument is already arriving
    at zero marginal cash cost, and 'no cycle closure exists' is a historical statement, not a current one.

    The two instruments differ CATEGORICALLY, and the difference is which symmetry of the error they can see:

      (a) STATE-FUNCTION error (per-endpoint bias)          -> invisible to BOTH. Neither is an accuracy control.
      (b) SYMMETRIC path bias (the estimate lags whichever
          endpoint the leg started from: fwd = true + d,
          rev = -true + d)                                  -> the 2-cycle SEES it (residual 2d). So does the 3-cycle.
      (c) ANTISYMMETRIC per-edge bias (fwd = true + d,
          rev = -true - d, with d differing per EDGE)       -> the 2-cycle is BLIND (residual exactly 0); the
                                                               3-cycle sees it, because R = d1 + d2 - d3 does
                                                               not cancel across three different edges.

    Class (c) is the honest, specific reason to buy the triangle, and it is a different reason from the one the
    design gives. It is also the class a merely reversible-but-wrong lambda schedule produces."""
    rng = random.Random(seed)
    res = {"symmetric_bias": {"two_cycle_detects": 0, "three_cycle_detects": 0},
           "antisymmetric_bias": {"two_cycle_detects": 0, "three_cycle_detects": 0},
           "state_function": {"two_cycle_detects": 0, "three_cycle_detects": 0}}
    tol = 1e-9
    for _ in range(trials):
        true = {s: rng.gauss(0, 5.0) for s in ("cmpd1", "cmpd4", "cmpd4prime")}
        d = {n: rng.gauss(0, 0.4) for n, _, _, _ in TRIANGLE}
        eps = {s: rng.gauss(0, 5.0) for s in ("cmpd1", "cmpd4", "cmpd4prime")}

        def edge_true(n):
            _, a, b, _ = next(t for t in TRIANGLE if t[0] == n)
            return true[b] - true[a]

        # (b) symmetric: both directions biased the same way relative to their own start
        two = abs((edge_true("T1") + d["T1"]) + (-edge_true("T1") + d["T1"]))
        three = abs(sum(s * (edge_true(n) + d[n]) for n, _, _, s in TRIANGLE))
        res["symmetric_bias"]["two_cycle_detects"] += two > tol
        res["symmetric_bias"]["three_cycle_detects"] += three > tol
        # (c) antisymmetric: the reverse leg carries the exact negative bias
        two = abs((edge_true("T1") + d["T1"]) + (-edge_true("T1") - d["T1"]))
        three = abs(sum(s * (edge_true(n) + d[n]) for n, _, _, s in TRIANGLE))
        res["antisymmetric_bias"]["two_cycle_detects"] += two > tol
        res["antisymmetric_bias"]["three_cycle_detects"] += three > tol
        # (a) state function
        def ef(n):
            _, a, b, _ = next(t for t in TRIANGLE if t[0] == n)
            return (true[b] + eps[b]) - (true[a] + eps[a])
        two = abs(ef("T1") + (-ef("T1")))
        three = abs(sum(s * ef(n) for n, _, _, s in TRIANGLE))
        res["state_function"]["two_cycle_detects"] += two > tol
        res["state_function"]["three_cycle_detects"] += three > tol
    for k in res:
        res[k] = {kk: vv / trials for kk, vv in res[k].items()}
    res["_reading"] = (
        "The reverse leg and the triangle are NOT the same instrument, but they overlap on the error class the "
        "reverse leg was bought to test. The triangle's exclusive territory is the ANTISYMMETRIC per-edge bias "
        "row: detection 0.00 for the 2-cycle, ~1.00 for the 3-cycle. Neither sees a state-function error, which "
        "is why the known-answer accuracy requirement stays OPEN regardless of what either returns.")
    res["_trials"] = trials
    return res


def alternative_uses_of_four_legs():
    """The question that must be asked before recommending any spend: is there a BETTER use of the same 4 new
    ternary+binary legs? Enumerated honestly, because the triangle should win on a comparison rather than by
    being the only proposal on the table.

    All options cost the same 4 new legs (2 edges' worth) at the same ~$6.83."""
    opts = [
        {"option": "the closure TRIANGLE (T2 + T3, forward only)",
         "buys": "R across THREE edges, plus R_ternary and R_binary separately",
         "detects": ["symmetric path bias", "ANTISYMMETRIC per-edge bias (uniquely)",
                     "endpoint-state inconsistency across three independently staged edges",
                     "mutually inconsistent atom maps"],
         "misses": ["all state-function error", "its own noise floor (sigma is unmeasured, so one draw cannot "
                    "separate systematic from unlucky)"],
         "edges_covered": 3},
        {"option": "forward AND reverse of ONE new edge (T2 fwd + T2 rev)",
         "buys": "a sigma-free antisymmetry number on a second edge",
         "detects": ["symmetric path bias on that one edge"],
         "misses": ["antisymmetric per-edge bias (a 2-cycle is blind to it by construction)",
                    "anything cross-edge", "all state-function error"],
         "edges_covered": 1},
        {"option": "two more REPLICATES of T1 (r1 + r2, ternary+binary)",
         "buys": "a between-replicate SD on the existing edge",
         "detects": ["random error only"],
         "misses": ["all systematic error -- and r0's miss is 33x its own MBAR SE, so it IS systematic; this is "
                    "the spend the r0 verdict already argued against, and seed s also swaps the homology model "
                    "so the SD would conflate sampling with model sensitivity"],
         "edges_covered": 1},
    ]
    return {
        "equal_cost_comparison": opts,
        "verdict": "The triangle WINS the 4-leg comparison: it is the only one of the three that covers more "
                   "than one edge, the only one that can see an antisymmetric per-edge bias, and the only one "
                   "that tests cross-edge endpoint consistency. That is the substantive reason to ADMIT it -- "
                   "not the reason the design gives, and not a claim about r0's systematic.",
        "but": "winning a 4-leg comparison is not the same as being the next thing to buy. The $1.31 "
               "solvent-only pre-scout costs ~19% of these 4 legs and can falsify the triangle's machinery "
               "first, and the reverse leg's branch decides whether any of it should be bought yet at all.",
    }


def solvent_prescout():
    """The cheapest early-abort gate on the triangle itself, and it is a new recommendation.

    R_solvent = dG_solv(T1) + dG_solv(T2) - dG_solv(T3) is a FULL closure test of the alchemical machinery --
    atom-map consistency, endpoint chemical identity, lambda schedule, charge model -- in a ~5k-particle box.
    T1's solvent leg ALREADY RAN (r0: 47.8060), so it costs 2 new solvent legs. It cannot see protein
    sampling, which is the point: it isolates the machinery from the physics.

    This is exactly the repo's pilot-one-leg-first rule applied to the triangle: if the machinery closure
    fails, no ternary leg should be bought, and finding that out costs a fraction of one ternary leg."""
    c = 2 * solvent_leg_ref_gpu_h()
    full = 4 * ternary_leg_ref_gpu_h()
    return {
        "what": "close the triangle in the SOLVENT environment only, before buying any ternary/binary leg",
        "new_legs": 2,
        "T1_solvent_already_run": "r0 solvent leg dG_morph = 47.8060 (CI 30148463967) -- reused, not re-bought",
        "detects": ["inconsistent atom maps between edges",
                    "endpoint chemical-identity inconsistency (the rev leg's actual bug class)",
                    "lambda-schedule inadequacy", "charge-model inconsistency across edges"],
        "cannot_detect": ["protein-sampling path error", "interface substates", "anything about cooperativity"],
        "ref_gpu_h_ESTIMATE": round(c, 1),
        "plan_usd_ESTIMATE": round(c * USD_PER_REF_GPU_H, 2),
        "range_usd": [round(c * USD_PER_REF_GPU_H_LO, 2), round(c * USD_PER_REF_GPU_H_HI, 2)],
        "fraction_of_full_n1_scout": round(c / full, 3),
        "caveat": SOLVENT_LEG_BASIS,
    }


def same_seed_requirement():
    """A constraint the design does not state, and without it the closure residual is not a closure residual.

    Ternary seed s uses the s%n-th independently relaxed SMARCA2 model. If T1, T2 and T3 run at different
    seeds they are computed on DIFFERENT Hamiltonians, the three edges no longer share endpoint states, and the
    telescoping that makes R identically zero does not apply. |R| would then be measuring homology-model
    sensitivity -- a real quantity, but not the one being claimed.

    r0 is seed 0, so T2 and T3 must also be seed 0."""
    return {
        "requirement": "all three edges of the triangle MUST run at the same seed (seed 0, to match r0)",
        "mechanism": "ternary seed s selects the s%n-th relaxed SMARCA2 starting model "
                     "(ternary_pdb_stage: starting_model_index = SEED % n)",
        "if_violated": "the edges are computed on different Hamiltonians, endpoint states are not shared, and "
                       "R stops being a closure residual -- it becomes a homology-model sensitivity measure.",
        "side_benefit": "a same-seed triangle also removes the homology-model term from R's noise, which is "
                        "why sigma_leg for R should sit well below the repo's assumed 0.7 replicate SD.",
        "consequence_for_n3": "an n=3 triangle needs seeds 0,1,2 on ALL THREE edges -- which is why it needs "
                              "T1's r1 and r2, the legs the r0 verdict recommended not buying.",
    }


def build_report():
    return {
        "_what": "closure arithmetic, leg accounting and CORRECTED pricing for the valB synthetic closure "
                 "triangle -- the $0 analysis half of the pre-gate (chemistry half: valb_triangle_chem.py)",
        "_no_spend": "pure stdlib, no GPU, no network. Nothing here launches anything.",
        "closure_identity": closure_identity(),
        "closure_decomposition_rule": closure_decomposition(
            {"ternary": {"T1": 47.4701, "T2": 0.0, "T3": 0.0}, "binary": {"T1": 48.0046, "T2": 0.0, "T3": 0.0}}),
        "what_closure_can_and_cannot_diagnose": state_function_blindness(),
        "noise_floor": closure_noise_floor(),
        "two_cycle_vs_three_cycle": two_cycle_vs_three_cycle(),
        "alternative_uses_of_the_same_four_legs": alternative_uses_of_four_legs(),
        "leg_accounting": leg_accounting(),
        "same_seed_requirement": same_seed_requirement(),
        "price": price_triangle(),
        "price_if_4fs_adopted": price_at_4fs(),
        "solvent_prescout_RECOMMENDED_FIRST": solvent_prescout(),
        "decision_tree": decision_tree(),
    }


def main():
    r = build_report()
    with open(OUT, "w") as f:
        json.dump(r, f, indent=2)
    print(json.dumps(r, indent=2))
    print("[triangle-closure] wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# =============================================================================================================
# PRE-REGISTERED PREDICTION — written 2026-07-26, BEFORE any triangle leg is bought
# =============================================================================================================
BINARY_DEPARTURE_PREREG = "R_binary materially non-zero, R_ternary small."


def binary_departure_prereg(R_ternary=None, R_binary=None, sigma_leg=0.045):
    """The prediction the pose finding makes about this triangle, and the verdict once R lands.

    WHY IT IS WRITTEN NOW. `mode=converge` measured the r0 (2 fs) and RUNG-2b (4 fs) cycles and found the BINARY
    leg's receptor-contacting moiety departs and does not return in 8/12 and 7/12 replicas respectively, while
    BOTH cycles' ternary legs are 12/12 stable (audit §L.3-L.3d). The triangle's three binary legs are the same
    construction. So this design now has a specific prediction rather than a generic path-error hypothesis, and a
    prediction is only worth anything if it is recorded before the data.

    THE DECISION THIS ACCOMPANIES (trimcrae delegated, 2026-07-26): run the binary legs UNRESTRAINED. The
    triangle's economy is r0 reused as T1 -- `price_triangle` buys FOUR legs, not six ($6.83 at n=1). Restrained
    T2/T3 in a cycle with an unrestrained T1 makes R measure the protocol difference rather than path error, so
    restraining means re-buying T1 too: 6 legs, ~$10.25, +50%, and the reuse that justified the design is gone.
    Unrestrained also answers a question restrained cannot -- see the branches.

    THE BRANCHES, and both directions are informative:

      BINARY_PATH_DEPENDENT  |R_binary| resolved, |R_ternary| not -> the departure's bias is PATH-dependent, a
                             closure sees it, and the triangle has localised the defect to the binary environment
                             by a route entirely independent of the pose diagnostic.
      BOTH_RESOLVED          both large -> path error is not confined to the binary arm; the ternary arm has one
                             too, which the pose data does NOT predict and would be a new finding.
      BINARY_CANCELS         neither resolved -> the bias is a per-endpoint STATE FUNCTION, telescopes out of any
                             cycle, and therefore also largely cancels from ddG_coop = ternary - binary. The
                             departure would then corrupt the cooperativity NUMBER far less than L.3b implies.
                             THIS IS THE BRANCH THAT ARGUES AGAINST THE r0 READING, and it must not be explained
                             away if it lands.
      TERNARY_ONLY           |R_ternary| resolved, |R_binary| not -> contradicts the pose data outright; do not
                             rationalise it, re-examine the diagnostic.

    POWER IS THE LIMITING FACTOR AND IS RECORDED HERE SO IT CANNOT BE FORGOTTEN AFTERWARDS. Each of R_ternary and
    R_binary is a THREE-leg closure, so SD = sqrt(3)*sigma_leg, and sigma_leg for this lane is known only to
    within a factor of ~15 (`closure_noise_floor`). At the low bound (MBAR SE 0.045) the design resolves an effect
    the size of r0's own 1.478 miss with power ~1.0; at sigma_leg = 0.5 that power is ~0.22. So BINARY_CANCELS is
    only evidence of cancellation if sigma_leg is near the low bound -- otherwise it is indistinguishable from
    "underpowered" and is reported as UNDERPOWERED rather than as support for either reading.
    """
    thresh = 1.96 * math.sqrt(3.0) * float(sigma_leg)
    out = {
        "prediction": BINARY_DEPARTURE_PREREG,
        "registered": "2026-07-26, before any triangle leg was bought",
        "basis": ("r0 (2 fs) binary 8/12 replicas departed, RUNG-2b (4 fs) binary 7/12; both ternary arms 0/12. "
                  "GH runs 30210186711 and 30210676030."),
        "binary_legs_run": "UNRESTRAINED - restraining forfeits the r0-as-T1 reuse; see the docstring",
        "three_leg_closure_SD": round(math.sqrt(3.0) * float(sigma_leg), 4),
        "resolution_threshold_abs": round(thresh, 4),
        "sigma_leg_assumed": sigma_leg,
        "power_caveat": ("sigma_leg is known only to a factor of ~15; at 0.5 the power to resolve a 1.478-sized "
                         "effect is ~0.22. BINARY_CANCELS at high sigma_leg means UNDERPOWERED, not cancellation."),
    }
    if R_ternary is None or R_binary is None:
        out["verdict"] = "NOT YET MEASURED - this is the pre-registration, not a result"
        return out
    t_res = abs(float(R_ternary)) > thresh
    b_res = abs(float(R_binary)) > thresh
    out["R_ternary"], out["R_binary"] = float(R_ternary), float(R_binary)
    out["verdict"] = ("BOTH_RESOLVED" if (t_res and b_res) else
                      "BINARY_PATH_DEPENDENT" if b_res else
                      "TERNARY_ONLY" if t_res else
                      "BINARY_CANCELS")
    out["prediction_upheld"] = (out["verdict"] == "BINARY_PATH_DEPENDENT")
    if out["verdict"] == "BINARY_CANCELS" and float(sigma_leg) > 0.2:
        out["verdict"] = "UNDERPOWERED"
        out["prediction_upheld"] = None
        out["why"] = ("neither closure resolves, but at sigma_leg=%.3g this design cannot resolve an effect the "
                      "size of r0's miss - absence of signal is not evidence of cancellation" % sigma_leg)
    return out
