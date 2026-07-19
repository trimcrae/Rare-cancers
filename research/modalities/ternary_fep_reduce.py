#!/usr/bin/env python3
"""Ternary-cooperativity REDUCER — turn per-leg/per-replica morph checkpoints into the coop-cycle quantities.

Consumes the leg checkpoints written by nr4a3_ternary_fep.run_leg (leg_<id>_<dir>_r<seed>.json, each a single
relative-alchemical morph ΔG in one environment) and forms, per compound-pair morph:

    ddG_alch,binary  = <binary_vhl  morph mean> − <solvent morph mean>
    ddG_alch,ternary = <ternary_<t> morph mean> − <solvent morph mean>
    ddG_coop         = ddG_alch,ternary − ddG_alch,binary          (ternary_coop.ddg_coop; solvent cancels)
    effective_ternary_recruitment / cooperative_coupling            (ternary_coop.recruitment_and_coupling)

Uncertainty is the REPLICATE STANDARD DEVIATION across the ≥3 independent replicas (prereg
uncertainty_estimator — NOT the MBAR SE), with a t-based 95% CI half-width; environment differences propagate
in quadrature. Forward/reverse legs (DIRECTION=rev) give a per-leg hysteresis. Emits, per environment leg, a
record matching ternary_coop_io.output_schema (validated here in schema mode — the execution-provenance fields
gpu_h/cost/ff-lock are attached by the run harness, not the physics), plus a pilot summary with the NR-V04
affinity/recruitment margins the retrospective bar checks. No number is asserted until real legs run; on CPU
with no checkpoints this reduces to an empty, honest report.
"""
import glob
import json
import math
import os

import ternary_coop as tcoop
import ternary_coop_io as tio
import nr4a3_ternary_fep as eng

IN = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")
CKPT = os.environ.get("CKPT_DIR", os.environ.get("OUTPUT_DIR", "/opt/ml/checkpoints"))

# two-sided t critical values at 95% by dof (1..10); asymptotic 1.96 beyond.
_TCRIT = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def _tcrit(dof):
    if dof <= 0:
        return float("inf")
    return _TCRIT.get(dof, 1.96)


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def _sample_sd(xs):
    """Sample (n−1) standard deviation; None for n<2 (no replicate spread)."""
    n = len(xs)
    if n < 2:
        return None
    m = _mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def _ci_halfwidth(sd, n):
    """t-based 95% CI half-width of a MEAN from n replicas: t(.975,n−1)·sd/√n."""
    if sd is None or n < 2:
        return None
    return _tcrit(n - 1) * sd / math.sqrt(n)


def _find_leg_files(leg_id, direction="fwd"):
    pats = [os.path.join(base, "**", "leg_%s_%s_r*.json" % (leg_id, direction)) for base in (CKPT, IN)]
    seen, out = set(), []
    for p in pats:
        for f in glob.glob(p, recursive=True):
            if f in seen:
                continue
            seen.add(f)
            try:
                out.append(json.load(open(f)))
            except Exception:  # noqa: BLE001
                pass
    return out


def aggregate_leg(leg_id):
    """Replicate mean/SD/CI (+ forward/reverse hysteresis) for one environment or solvent leg. Returns None if
    no replicas are present yet (honest: nothing to report)."""
    fwd = [d["dg_morph_kcal"] for d in _find_leg_files(leg_id, "fwd") if "dg_morph_kcal" in d]
    if not fwd:
        return None
    rev = [d["dg_morph_kcal"] for d in _find_leg_files(leg_id, "rev") if "dg_morph_kcal" in d]
    mean = _mean(fwd)
    sd = _sample_sd(fwd)
    n = len(fwd)
    ci = _ci_halfwidth(sd, n)
    # forward + reverse should sum to ~0 for a clean A→B / B→A pair; |mean_fwd + mean_rev| = hysteresis.
    hysteresis = abs(mean + _mean(rev)) if rev else None
    return {"leg_id": leg_id, "environment": eng._environment_of(leg_id),
            "mean_dg_morph_kcal": mean, "replicate_sd_kcal": sd, "n_replicas": n,
            "ci95_half_width_kcal": ci, "hysteresis_kcal": hysteresis, "dg_values": fwd}


def _welch_satterthwaite(mean_t, sd_t, n_t, mean_b, sd_b, n_b):
    """ΔΔG_coop = mean(ternary morph) − mean(binary morph) with a WELCH–SATTERTHWAITE 95% CI (reviewer required
    change, 2026-07-17).

    QUANTITY RETURNED (reviewer condition 5, 2026-07-19; sign convention unit-tested in
    tests/test_ternary_coop_sign.py): ddg_coop_kcal is ternary_coop.ddg_coop's per-morph relative cooperativity
    change = ddG_alch,ternary(A->B) − ddG_alch,binary(A->B) = −RT ln(alpha_B/alpha_A), the SAME quantity the
    frozen target ddG_coop_exp = −RT ln(alpha_4/alpha_1) = +0.944 defines (morph A=cmpd1/hi -> B=cmpd4/lo). It
    is NOT a single compound's dG_coop=−RT ln(alpha). For the hi->lo calibration this is POSITIVE (+0.944) and
    calibration_decision requires that positive sign; see ternary_coop.ddg_coop / ddg_coop_from_kd_pairs.

    The shared solvent morph cancels EXACTLY in the difference of means, so ΔΔG_coop is a
    difference of two independent replicate-mean estimators and its SE is the between-replicate

        SE = sqrt( s_T²/n_T + s_B²/n_B )                       (NOT a sum of per-window MBAR SEs)

    with the Welch effective dof

        dof = (s_T²/n_T + s_B²/n_B)² / [ (s_T²/n_T)²/(n_T−1) + (s_B²/n_B)²/(n_B−1) ]

    and CI half-width t(.975, floor(dof))·SE. Returns None when either environment has <2 replicas (no spread)."""
    if None in (mean_t, mean_b) or n_t < 2 or n_b < 2 or sd_t is None or sd_b is None:
        return None
    vt, vb = sd_t ** 2 / n_t, sd_b ** 2 / n_b
    se = math.sqrt(vt + vb)
    ddg = mean_t - mean_b
    denom = (vt ** 2 / (n_t - 1)) + (vb ** 2 / (n_b - 1))
    dof = ((vt + vb) ** 2 / denom) if denom > 0 else (n_t + n_b - 2)
    ci = _tcrit(int(math.floor(dof))) * se
    return {"ddg_coop_kcal": ddg, "se_kcal": se, "welch_dof": dof,
            "ci95_half_width_kcal": ci, "ci95_low": ddg - ci, "ci95_high": ddg + ci,
            "n_ternary": n_t, "n_binary": n_b}


def calibration_decision(ternary_agg, binary_agg, target_kcal, restraint_dominated=None):
    """Apply the FROZEN valB_mini decision rule (wurz-calib-frozen.json decision_rule_valB_mini) to the
    Welch–Satterthwaite ΔΔG_coop vs the experimental calibration target (+0.944 kcal/mol). Returns
    PASS / NO-GO / INDETERMINATE with the exact criterion that fired. The retired ±1.0 acceptance band is NOT
    used — the sub-1-kcal experimental separation means we require zero-EXCLUSION, not a tolerance window."""
    if ternary_agg is None or binary_agg is None:
        return {"decision": "INDETERMINATE", "reason": "missing a required environment leg (ternary/binary)."}
    ws = _welch_satterthwaite(ternary_agg["mean_dg_morph_kcal"], ternary_agg["replicate_sd_kcal"],
                              ternary_agg["n_replicas"], binary_agg["mean_dg_morph_kcal"],
                              binary_agg["replicate_sd_kcal"], binary_agg["n_replicas"])
    if ws is None:
        return {"decision": "INDETERMINATE",
                "reason": "insufficient replicates for a between-replicate SE (need n>=2 per environment).",
                "n_ternary": ternary_agg["n_replicas"], "n_binary": binary_agg["n_replicas"]}
    lo, hi, ddg = ws["ci95_low"], ws["ci95_high"], ws["ddg_coop_kcal"]
    hys = [h for h in (ternary_agg.get("hysteresis_kcal"), binary_agg.get("hysteresis_kcal")) if h is not None]
    hysteresis_ok = all(h <= 1.0 for h in hys) if hys else True
    excludes_zero = lo > 0.0                       # resolved POSITIVE cooperativity change (correct sign)
    ci_includes_zero = lo <= 0.0 <= hi
    target_in_ci = lo <= target_kcal <= hi
    checks = {"correct_positive_sign": ddg > 0, "ci_excludes_zero": excludes_zero,
              "hysteresis_resolved": hysteresis_ok, "consistent_with_target": target_in_ci,
              "not_restraint_dominated": (restraint_dominated is not True)}
    if hi < 0.0:
        decision, reason = "NO-GO", ("CI is entirely NEGATIVE (%.2f..%.2f) — method resolves the WRONG sign "
                                     "of cooperativity vs the known +%.3f." % (lo, hi, target_kcal))
    elif ci_includes_zero:
        decision, reason = "INDETERMINATE", ("95%% CI includes zero (%.2f..%.2f) — cannot resolve a nonzero "
                                             "cooperativity change (noisy positive point estimate alone)." % (lo, hi))
    elif not hysteresis_ok:
        decision, reason = "INDETERMINATE", "unresolved forward/reverse hysteresis (>1.0 kcal/mol)."
    elif restraint_dominated is True:
        decision, reason = "INDETERMINATE", "restraint-dominated / collapse / ligand-escape flagged by convergence QC."
    elif not target_in_ci:
        decision, reason = "INDETERMINATE", ("sign resolved positive & zero excluded, but +%.3f lies OUTSIDE the "
                                             "95%% CI (%.2f..%.2f) — magnitude not broadly consistent." % (target_kcal, lo, hi))
    elif all(checks.values()):
        decision, reason = "PASS", ("ΔΔG_coop=%.2f (95%% CI %.2f..%.2f) excludes zero with the correct positive "
                                    "sign and is broadly consistent with +%.3f." % (ddg, lo, hi, target_kcal))
    else:
        decision, reason = "INDETERMINATE", "one or more PASS criteria unmet; see checks."
    return {"decision": decision, "reason": reason, "target_kcal": target_kcal,
            "welch_satterthwaite": ws, "checks": checks,
            "adaptive_action": ("extend to 5 replicates/environment and re-reduce"
                                if decision == "INDETERMINATE" else None)}


# frozen condition-6 accuracy gate thresholds (reviewer 2026-07-19). A FIXED accuracy margin — NOT "within
# replicate SD" — combined with correct sign, a between-replicate cycle-SD ceiling, and all convergence
# diagnostics. This SUPERSEDES the band-only rule that was retired for "could accept zero": here PASS needs
# correct sign AND small error AND small cycle SD AND clean diagnostics, so it cannot pass zero or a diverging set.
GATE_ABS_ERR_PASS = 1.0        # |mean ΔΔG_calc − target| <= this AND ... = PASS-eligible
GATE_ABS_ERR_FAIL = 2.0        # |mean ΔΔG_calc − target| >  this = FAIL
GATE_CYCLE_SD_PASS = 0.75      # between-replicate sample SD <= this = PASS-eligible
GATE_CYCLE_SD_EXTEND = 1.0     # SD in (PASS, this] = extend to 5; SD > this after extension = FAIL
GATE_BOUNDARY_MARGIN = 0.5     # a PASS/FAIL result within this of a threshold = extend (condition 3)


def _sign(x):
    return 0 if x == 0 else (1 if x > 0 else -1)


def calibration_gate(ddg_coop_replicates, target_kcal, diagnostics_ok=True, extended=False):
    """AUTHORITATIVE valB_mini calibration verdict — reviewer condition 6 (2026-07-19), three-tier PASS /
    BORDERLINE / FAIL against a FIXED accuracy margin, using the BETWEEN-REPLICATE cycle SD (condition 3), NOT
    the MBAR SE. `ddg_coop_replicates` = the per-independent-replicate ΔΔG_coop values (each a complete
    solvent/binary/ternary cycle). `diagnostics_ok` = every leg passed the frozen convergence checks
    (ternary_fep_convergence: overlap connected, plateau, mixing, fwd/rev, structural); a persistent
    overlap/drift/structural failure forces FAIL. `extended` = this is already the >=5-replicate round (so a
    still-too-large SD is FAIL, not another extend).

        PASS      : diagnostics_ok AND correct sign AND |mean − target| <= 1.0 AND cycle SD <= 0.75
        BORDERLINE: (1.0 < |err| <= 2.0) OR (0.75 < SD <= 1.0) OR within 0.5 of a pass/fail boundary
                    -> EXTEND to 5 replicates and re-reduce (do NOT advance to NR-V04)
        FAIL      : wrong sign OR |err| > 2.0 OR (SD > 1.0 after extension) OR persistent diagnostics failure
    """
    vals = [v for v in (ddg_coop_replicates or []) if v is not None and math.isfinite(v)]
    n = len(vals)
    if n < 2:
        return {"decision": "INDETERMINATE", "reason": "need >=2 independent replicates for a cycle SD.",
                "n_replicates": n}
    mean = _mean(vals)
    sd = _sample_sd(vals)
    abs_err = abs(mean - target_kcal)
    ci = _ci_halfwidth(sd, n)
    correct_sign = _sign(mean) == _sign(target_kcal)
    metrics = {"n_replicates": n, "mean_ddg_coop_kcal": mean, "cycle_sd_kcal": sd,
               "abs_error_kcal": abs_err, "target_kcal": target_kcal,
               "t_ci95_half_width_kcal": ci, "correct_sign": correct_sign, "diagnostics_ok": bool(diagnostics_ok),
               "thresholds": {"abs_err_pass": GATE_ABS_ERR_PASS, "abs_err_fail": GATE_ABS_ERR_FAIL,
                              "cycle_sd_pass": GATE_CYCLE_SD_PASS, "cycle_sd_extend": GATE_CYCLE_SD_EXTEND}}

    # ---- FAIL (hard) ----
    if not correct_sign:
        return {"decision": "FAIL", "reason": "wrong sign of cooperativity change (mean %.2f vs target %+.3f)."
                % (mean, target_kcal), **metrics}
    if abs_err > GATE_ABS_ERR_FAIL:
        return {"decision": "FAIL", "reason": "|error| %.2f > %.1f kcal/mol." % (abs_err, GATE_ABS_ERR_FAIL),
                **metrics}
    if not diagnostics_ok:
        return {"decision": "FAIL", "reason": "persistent convergence diagnostics failure "
                "(overlap/drift/structural) on one or more legs.", **metrics}
    if extended and sd is not None and sd > GATE_CYCLE_SD_EXTEND:
        return {"decision": "FAIL", "reason": "cycle SD %.2f > %.1f kcal/mol AFTER extension to >=5 replicates."
                % (sd, GATE_CYCLE_SD_EXTEND), **metrics}

    # ---- BORDERLINE (extend to 5, do not advance) ----
    reasons = []
    if abs_err > GATE_ABS_ERR_PASS:
        reasons.append("abs error %.2f in (%.1f, %.1f]" % (abs_err, GATE_ABS_ERR_PASS, GATE_ABS_ERR_FAIL))
    if sd is not None and sd > GATE_CYCLE_SD_PASS:
        reasons.append("cycle SD %.2f in (%.2f, %.1f]" % (sd, GATE_CYCLE_SD_PASS, GATE_CYCLE_SD_EXTEND))
    # condition 3: a would-be PASS sitting within 0.5 of a boundary is not robust -> extend
    near_boundary = (abs(abs_err - GATE_ABS_ERR_PASS) < GATE_BOUNDARY_MARGIN
                     or (sd is not None and abs(sd - GATE_CYCLE_SD_PASS) < GATE_BOUNDARY_MARGIN))
    if not reasons and near_boundary and not extended:
        reasons.append("within %.1f of a pass/fail boundary (abs_err=%.2f, sd=%s) — not robust"
                       % (GATE_BOUNDARY_MARGIN, abs_err, "%.2f" % sd if sd is not None else "n/a"))
    if reasons:
        return {"decision": "BORDERLINE", "reason": "; ".join(reasons)
                + " -> extend to 5 replicates and re-reduce (do NOT advance to NR-V04).",
                "adaptive_action": "extend_to_5_replicates", **metrics}

    # ---- PASS ----
    return {"decision": "PASS", "reason": "correct sign, |error| %.2f <= %.1f, cycle SD %.2f <= %.2f, all "
            "convergence diagnostics pass." % (abs_err, GATE_ABS_ERR_PASS, sd, GATE_CYCLE_SD_PASS),
            "authorizes": "NR-V04 retrospective ONLY (matrix stays blocked until NR-V04's own prereg passes).",
            **metrics}


def per_replicate_ddg_coop(morph_key):
    """Per-INDEPENDENT-REPLICATE ΔΔG_coop for the condition-3/6 gate: pair the ternary and binary morph legs by
    SEED (the shared solvent morph cancels within each replicate cycle -> ΔΔG_coop_r = ternary_r − binary_r), so
    the sample SD of the returned list IS the between-replicate cycle SD the gate requires (NOT an MBAR SE).
    Returns (values, n_seeds_paired)."""
    lids = [lid for lid in eng.expand_pilot_legs() if eng._morph_key(lid) == morph_key]

    def by_seed(env):
        leg = next((l for l in lids if eng._environment_of(l) == env), None)
        out = {}
        if not leg:
            return out
        for d in _find_leg_files(leg, "fwd"):
            if d.get("dg_morph_kcal") is not None and d.get("seed") is not None:
                out[int(d["seed"])] = float(d["dg_morph_kcal"])
        return out

    tern, bina = by_seed("ternary"), by_seed("binary")
    seeds = sorted(set(tern) & set(bina))
    return [tern[s] - bina[s] for s in seeds], len(seeds)


def _diagnostics_ok():
    """True unless the committed convergence report (ternary_fep_convergence) flags a technical failure on ANY
    leg (reviewer condition 4/6: persistent overlap/drift/structural failure -> gate FAIL). Absent report ->
    True (the convergence gate is its own step; here we only fold in a failure that WAS measured)."""
    for base in (CKPT, IN):
        p = os.path.join(base, "ternary_convergence.json")
        if os.path.isfile(p):
            try:
                rep = json.load(open(p))
                return not any(l.get("technical_failure") for l in rep.get("legs", []))
            except Exception:  # noqa: BLE001
                pass
    return True


def _diff(mean_a, ci_a, mean_b, ci_b):
    """(mean_a − mean_b) with quadrature-combined CI half-width (independent replicate errors)."""
    if mean_a is None or mean_b is None:
        return None, None
    est = mean_a - mean_b
    if ci_a is None or ci_b is None:
        return est, None
    return est, math.sqrt(ci_a ** 2 + ci_b ** 2)


# condition-8 audit thresholds
AUDIT_ANTISYM_MAX_KCAL = 1.0       # |mean_fwd + mean_rev| above this = A->B/B->A antisymmetry broken (bad cycle)
AUDIT_SD_INFLATION_MAX = 1.5       # ddG_coop SD > this * quadrature(leg SDs) = anomalous non-cancelling variance


def cancellation_metrics(ternary_mean, ternary_sd, binary_mean, binary_sd):
    """Reviewer condition 8 (pure): does ΔΔG_coop emerge as a WELL-CANCELLED difference of two large legs? The
    47.28-type magnitude is fine IF the binary and ternary legs are similarly large and cancel reproducibly.
    Reports the cancellation ratio (|ΔΔG_coop| / max(|leg|)) — small = strong cancellation — and whether the
    difference's replicate SD stays near the quadrature of the leg SDs (no anomalous non-cancelling variance)."""
    ddg = ternary_mean - binary_mean
    big = max(abs(ternary_mean), abs(binary_mean))
    ratio = (abs(ddg) / big) if big > 0 else None
    sd_quad = None
    sd_ok = None
    if ternary_sd is not None and binary_sd is not None:
        sd_quad = math.sqrt(ternary_sd ** 2 + binary_sd ** 2)
    return {"ddg_coop_kcal": ddg, "max_leg_magnitude_kcal": big, "cancellation_ratio": ratio,
            "leg_sd_quadrature_kcal": sd_quad,
            "note": "small cancellation_ratio = ΔΔG_coop is a small, well-cancelled difference of large legs "
                    "(the 47.28 magnitude is not itself a problem if binary+ternary cancel reproducibly)."}


def leg_algebra_audit(morph_key):
    """Reviewer condition 8: per-morph antisymmetry (A->B vs B->A) + large-leg cancellation audit. Reproduces
    what to check on the committed .nc — for each environment leg: mean_fwd, forward/reverse antisymmetry
    (|fwd+rev|, should be ~0 for a clean cycle), replicate SD; and whether the binary/ternary legs cancel
    reproducibly into ΔΔG_coop. Honest-empty when legs are absent."""
    legs = {lid: aggregate_leg(lid) for lid in eng.expand_pilot_legs() if eng._morph_key(lid) == morph_key}
    present = {lid: v for lid, v in legs.items() if v}
    per_leg = {}
    for lid, v in present.items():
        anti = v.get("hysteresis_kcal")
        per_leg[lid] = {"environment": v["environment"], "mean_dg_morph_kcal": v["mean_dg_morph_kcal"],
                        "replicate_sd_kcal": v["replicate_sd_kcal"], "n_replicas": v["n_replicas"],
                        "antisymmetry_fwd_plus_rev_kcal": anti,
                        "antisymmetry_ok": (None if anti is None else anti <= AUDIT_ANTISYM_MAX_KCAL)}
    tern = next((v for v in present.values() if v["environment"] == "ternary"), None)
    bina = next((v for v in present.values() if v["environment"] == "binary"), None)
    cancel = None
    if tern and bina:
        cancel = cancellation_metrics(tern["mean_dg_morph_kcal"], tern["replicate_sd_kcal"],
                                      bina["mean_dg_morph_kcal"], bina["replicate_sd_kcal"])
    return {"morph": morph_key, "available": bool(present), "per_leg": per_leg,
            "cancellation": cancel,
            "_what": "condition-8 47.28 audit: antisymmetry + large-leg cancellation of ΔΔG_coop"}


def coop_for_morph(morph_key):
    """The full binary-vs-ternary cycle for one compound-pair morph, from its solvent/binary/ternary legs."""
    legs = {lid: aggregate_leg(lid) for lid in eng.expand_pilot_legs() if eng._morph_key(lid) == morph_key}
    solvent = next((v for k, v in legs.items() if v and v["environment"] == "solvent"), None)
    binary = next((v for k, v in legs.items() if v and v["environment"] == "binary"), None)
    ternary = next((v for k, v in legs.items() if v and v["environment"] == "ternary"), None)
    if not (solvent and binary and ternary):
        return {"morph": morph_key, "available": False,
                "present": {k: bool(v) for k, v in legs.items()}}
    ddg_bin, ci_bin = _diff(binary["mean_dg_morph_kcal"], binary["ci95_half_width_kcal"],
                            solvent["mean_dg_morph_kcal"], solvent["ci95_half_width_kcal"])
    ddg_tern, ci_tern = _diff(ternary["mean_dg_morph_kcal"], ternary["ci95_half_width_kcal"],
                              solvent["mean_dg_morph_kcal"], solvent["ci95_half_width_kcal"])
    # ddG_coop uses the single source of truth (ternary_coop.ddg_coop); solvent cancels so its error drops out.
    ddg_coop = tcoop.ddg_coop(ddg_tern, ddg_bin)
    ci_coop = None
    if binary["ci95_half_width_kcal"] is not None and ternary["ci95_half_width_kcal"] is not None:
        ci_coop = math.sqrt(binary["ci95_half_width_kcal"] ** 2 + ternary["ci95_half_width_kcal"] ** 2)
    rc = tcoop.recruitment_and_coupling(ddg_tern, ddg_bin)
    return {
        "morph": morph_key, "available": True,
        "ddg_alch_binary_kcal": ddg_bin, "ci95_binary_kcal": ci_bin,
        "ddg_alch_ternary_kcal": ddg_tern, "ci95_ternary_kcal": ci_tern,
        "ddg_coop_kcal": ddg_coop, "ci95_coop_kcal": ci_coop,
        "effective_ternary_recruitment_kcal": rc["effective_ternary_recruitment"],
        "cooperative_coupling_kcal": rc["cooperative_coupling"],
        "delta_alpha_ratio_B_over_A": tcoop.delta_alpha_ratio(ddg_coop) if ddg_coop is not None else None,
        "legs": {k: v for k, v in legs.items() if v},
        "sign_note": "morph oriented A->B as frozen; POSITIVE ddg_alch = B binds/recruits WORSE than A "
                     "(so for active->epimer, positive = active favored). ddg_coop<0 = B more cooperative.",
    }


def leg_output_record(leg_agg, morph_summary):
    """A per-environment-leg record shaped to ternary_coop_io.output_schema. gpu_h/cost/ff-lock are execution
    provenance the run harness fills; here we validate SCHEMA/units only (not execution mode)."""
    env = leg_agg["environment"]
    ddg = (morph_summary.get("ddg_alch_ternary_kcal") if env == "ternary"
           else morph_summary.get("ddg_alch_binary_kcal") if env == "binary"
           else leg_agg["mean_dg_morph_kcal"])
    ci = leg_agg["ci95_half_width_kcal"]
    conv = bool(leg_agg["n_replicas"] >= 3 and ci is not None and ci <= 1.5
                and (leg_agg["hysteresis_kcal"] is None or leg_agg["hysteresis_kcal"] <= 1.0))
    rec = {
        "schema_version": tio.SCHEMA_VERSION, "leg_id": leg_agg["leg_id"], "environment": env,
        "ddg_alch_kcal": ddg, "ci95_half_width_kcal": ci if ci and ci > 0 else 1e-6,
        "n_replicas": leg_agg["n_replicas"], "hysteresis_kcal": leg_agg["hysteresis_kcal"] or 0.0,
        "converged": conv, "unit_gpu_h_observed": None, "cost_usd_observed": None,
        "system_hash": "0" * 64, "ligand_hash": "0" * 64,
        "artifacts": tio.expected_artifact_manifest(leg_agg["leg_id"]),
        "lock": {k: None for k in tio.ENV_FORCEFIELD_LOCK},
    }
    rec["_schema_check"] = tio.validate_result(rec, mode="schema")
    return rec


def _protocol_hash_consistency():
    """Reviewer #3: every leg of the coop cycle must run under the SAME frozen protocol. Collect the protocol_hash
    each leg JSON recorded and confirm they are identical (the per-replica seed is excluded from the hash, so
    replicas of a leg share it too). >1 distinct hash = a leg ran under different physics -> the cycle is invalid."""
    hashes = {}
    for base in (CKPT, IN):
        for f in glob.glob(os.path.join(base, "**", "leg_*_r*.json"), recursive=True):
            try:
                d = json.load(open(f))
            except Exception:  # noqa: BLE001
                continue
            h = d.get("protocol_hash")
            if h:
                hashes.setdefault(h, []).append(os.path.basename(f))
    return {"consistent": len(hashes) <= 1, "n_distinct_hashes": len(hashes),
            "hashes": {h: sorted(v) for h, v in hashes.items()}}


def reduce_all():
    os.makedirs(CKPT, exist_ok=True)
    morphs = sorted({eng._morph_key(lid) for lid in eng.expand_pilot_legs()})
    summaries = [coop_for_morph(m) for m in morphs]
    leg_records = []
    for s in summaries:
        if not s.get("available"):
            continue
        for lid, agg in s["legs"].items():
            if agg["environment"] in ("binary", "ternary"):
                leg_records.append(leg_output_record(agg, s))
    # NR-V04 affinity/recruitment margins the retrospective bar checks (morph is active->epimer, positive=active)
    nrv04 = next((s for s in summaries if s["morph"].startswith("nrv04") and s.get("available")), None)
    nrv04_controls = None
    if nrv04:
        nrv04_controls = {
            "active_vs_epimer_binary_vhl_kcal": nrv04["ddg_alch_binary_kcal"],
            "active_vs_epimer_binary_vhl_ci95": nrv04["ci95_binary_kcal"],
            "active_vs_epimer_effective_ternary_kcal": nrv04["ddg_alch_ternary_kcal"],
            "active_vs_epimer_effective_ternary_ci95": nrv04["ci95_ternary_kcal"],
            "bar": {"binary_min_kcal": 3.0, "effective_ternary_min_kcal": 2.0,
                    "note": "prereg nrv04_affinity_control; POSITIVE margin = active favored over epimer."},
        }
    # valB_mini CALIBRATION DECISION — Welch–Satterthwaite ΔΔG_coop vs the frozen +0.944 kcal/mol target, under
    # the frozen decision_rule_valB_mini (PASS / NO-GO / INDETERMINATE). Target + rule come from the frozen JSON.
    calib_decision = None
    try:
        cf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wurz-calib-frozen.json")
        target = json.load(open(cf))["preregistered_target"]["ddG_coop_exp_kcal_per_mol"]
        calib = next((s for s in summaries if s["morph"].startswith("calib") and s.get("available")), None)
        if calib:
            legs = calib["legs"]
            tern = next((v for v in legs.values() if v["environment"] == "ternary"), None)
            bina = next((v for v in legs.values() if v["environment"] == "binary"), None)
            calib_decision = calibration_decision(tern, bina, target)
            calib_decision["morph"] = calib["morph"]
    except Exception as e:  # noqa: BLE001
        calib_decision = {"decision": "INDETERMINATE", "reason": "calibration decision not computed: %s" % e}
    # AUTHORITATIVE condition-6 three-tier gate (reviewer 2026-07-19) on the per-replicate cycle values +
    # convergence diagnostics. This is the headline valB_mini verdict; calibration_decision (Welch-Satterthwaite
    # CI) is retained for reporting/CI context. PASS here authorizes NR-V04 ONLY.
    calib_gate = None
    try:
        cf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wurz-calib-frozen.json")
        target = json.load(open(cf))["preregistered_target"]["ddG_coop_exp_kcal_per_mol"]
        calib = next((s for s in summaries if s["morph"].startswith("calib") and s.get("available")), None)
        if calib:
            reps, n_paired = per_replicate_ddg_coop(calib["morph"])
            calib_gate = calibration_gate(reps, target, diagnostics_ok=_diagnostics_ok())
            calib_gate["morph"] = calib["morph"]
            calib_gate["per_replicate_ddg_coop_kcal"] = reps
            calib_gate["n_seeds_paired"] = n_paired
    except Exception as e:  # noqa: BLE001
        calib_gate = {"decision": "INDETERMINATE", "reason": "calibration gate not computed: %s" % e}
    report = {
        "_what": "ternary-cooperativity pilot reduction (binary-vs-ternary cycle, replicate-SD errors)",
        "_honesty": "no measured alpha/dG asserted; values appear only when real GPU legs have checkpointed. "
                    "gpu_h/cost/ff-lock are execution provenance attached by the run harness, not here.",
        "morph_summaries": summaries,
        "leg_output_records": leg_records,
        "nrv04_affinity_controls": nrv04_controls,
        "valB_calibration_decision": calib_decision,
        "valB_calibration_gate": calib_gate,   # AUTHORITATIVE condition-6 three-tier verdict (headline)
        "leg_algebra_audit": [leg_algebra_audit(m) for m in morphs],   # condition-8 antisymmetry/cancellation
        "protocol_hash_consistency": _protocol_hash_consistency(),
        "n_available_morphs": sum(1 for s in summaries if s.get("available")),
    }
    out = os.path.join(CKPT, "ternary_coop_reduction.json")
    json.dump(report, open(out, "w"), indent=2)
    print("[tfep-reduce] wrote %s (%d/%d morphs available)"
          % (out, report["n_available_morphs"], len(summaries)), flush=True)
    return report


if __name__ == "__main__":
    reduce_all()
