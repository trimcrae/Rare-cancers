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
import re
import json
import math
import os

import ternary_coop as tcoop
import ternary_coop_io as tio
import ternary_coop_gate as tcg   # the prereg's frozen thresholds live there; never re-type one here (rule 1)
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


def hysteresis_max_kcal(path=None):
    """The preregistered fwd/rev ceiling, |ΔG_fwd + ΔG_rev| <= this. ONE HOME: `nr4a3-ternary-coop-prereg.json`
    → retrospective_bar.technical_convergence.cycle_closure_or_hysteresis_kcal_max, the same field
    `ternary_coop_gate.gate_technical_convergence` reads. It was typed as a bare `1.0` here, i.e. a second home
    for a frozen threshold — the exact shape rule 1 exists to stop. Reading it means the two consumers cannot
    disagree about what the prereg says."""
    bar = tcg.load_bar(path) if path else tcg.load_bar()
    return float(bar["technical_convergence"]["cycle_closure_or_hysteresis_kcal_max"])


def hysteresis_fields(ternary_agg, binary_agg):
    """The preregistered fwd/rev criterion as a TRI-STATE, from the leg aggregates alone. ONE HOME for it.

    ★ WHY THIS IS ITS OWN FUNCTION, CALLED BEFORE EVERY EARLY RETURN (2026-07-27). `calibration_decision`
    computed the hysteresis only AFTER the Welch–Satterthwaite CI succeeded, so a cycle with <2 replicates per
    environment returned `{decision, reason, n_ternary, n_binary}` and NOTHING about the hysteresis. But the two
    criteria have different data requirements: |mean(ΔG_fwd) + mean(ΔG_rev)| needs ONE replicate per direction
    and no replicate spread at all, so it is measurable in precisely the case where the CI is not. The first
    hysteresis this program ever measured (0.3246 kcal/mol on the r0 ternary leg, 2026-07-27) was therefore
    dropped on the floor by a guard belonging to a different criterion, and the verdict annotation printed
    "NOT MEASURED (no reverse leg reduced)" about a leg that had run for 2000 iterations. Same bug class as
    everything else in §L.6 — an absent representation that is also what a real state looks like — reached this
    time not by a coercion but by a control-flow path that never computes the value.

    Returns three fields, and `None` is reserved for NOT MEASURED in each: `hysteresis_kcal` (the worst leg's
    |fwd+rev|, so a single bad leg cannot hide behind a good one), `hysteresis_ok`, `hysteresis_measured`."""
    aggs = [a for a in (ternary_agg, binary_agg) if a]
    hys = [h for a in aggs for h in (a.get("hysteresis_kcal"),) if h is not None]
    # `if hys else True` DEFAULTED A PREREGISTERED CRITERION TO PASS. hysteresis_kcal is None whenever no rev leg
    # exists, and no rev leg had EVER run (the workflow hardcoded DIRECTION=fwd), so "no unresolved forward/reverse
    # disagreement" was satisfied by never having measured it — the same shape as _diagnostics_ok() returning True
    # on an absent report. Absent is now reported as UNMEASURED, distinct from measured-and-fine.
    return {"hysteresis_kcal": (max(hys) if hys else None),
            "hysteresis_ok": (all(h <= hysteresis_max_kcal() for h in hys) if hys else None),
            "hysteresis_measured": bool(hys),
            "hysteresis_max_kcal": hysteresis_max_kcal()}


def calibration_decision(ternary_agg, binary_agg, target_kcal, restraint_dominated=None):
    """Apply the FROZEN valB_mini decision rule (wurz-calib-frozen.json decision_rule_valB_mini) to the
    Welch–Satterthwaite ΔΔG_coop vs the experimental calibration target (+0.944 kcal/mol). Returns
    PASS / NO-GO / INDETERMINATE with the exact criterion that fired. The retired ±1.0 acceptance band is NOT
    used — the sub-1-kcal experimental separation means we require zero-EXCLUSION, not a tolerance window.

    EVERY return path carries the `hysteresis_*` fields (see `hysteresis_fields`), because they are what the
    verdict annotation reports and they do not depend on the replicate count the early returns are about."""
    hyf = hysteresis_fields(ternary_agg, binary_agg)
    if ternary_agg is None or binary_agg is None:
        return {"decision": "INDETERMINATE", "reason": "missing a required environment leg (ternary/binary).",
                **hyf}
    ws = _welch_satterthwaite(ternary_agg["mean_dg_morph_kcal"], ternary_agg["replicate_sd_kcal"],
                              ternary_agg["n_replicas"], binary_agg["mean_dg_morph_kcal"],
                              binary_agg["replicate_sd_kcal"], binary_agg["n_replicas"])
    if ws is None:
        return {"decision": "INDETERMINATE",
                "reason": "insufficient replicates for a between-replicate SE (need n>=2 per environment).",
                "n_ternary": ternary_agg["n_replicas"], "n_binary": binary_agg["n_replicas"], **hyf}
    lo, hi, ddg = ws["ci95_low"], ws["ci95_high"], ws["ddg_coop_kcal"]
    hysteresis_measured = hyf["hysteresis_measured"]
    hysteresis_ok = hyf["hysteresis_ok"]
    excludes_zero = lo > 0.0                       # resolved POSITIVE cooperativity change (correct sign)
    ci_includes_zero = lo <= 0.0 <= hi
    target_in_ci = lo <= target_kcal <= hi
    checks = {"correct_positive_sign": ddg > 0, "ci_excludes_zero": excludes_zero,
              "hysteresis_resolved": hysteresis_ok, "hysteresis_measured": hysteresis_measured,
              "consistent_with_target": target_in_ci,
              "not_restraint_dominated": (restraint_dominated is not True)}
    if hi < 0.0:
        decision, reason = "NO-GO", ("CI is entirely NEGATIVE (%.2f..%.2f) — method resolves the WRONG sign "
                                     "of cooperativity vs the known +%.3f." % (lo, hi, target_kcal))
    elif ci_includes_zero:
        decision, reason = "INDETERMINATE", ("95%% CI includes zero (%.2f..%.2f) — cannot resolve a nonzero "
                                             "cooperativity change (noisy positive point estimate alone)." % (lo, hi))
    elif hysteresis_ok is False:
        decision, reason = "INDETERMINATE", "unresolved forward/reverse hysteresis (>1.0 kcal/mol)."
    elif hysteresis_ok is None:
        decision, reason = "INDETERMINATE", ("forward/reverse hysteresis NOT MEASURED (no rev leg) — the frozen rule requires no unresolved fwd/rev disagreement, and an unmeasured check does not satisfy it.")
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
            "welch_satterthwaite": ws, "checks": checks, **hyf,
            "adaptive_action": ("extend to 5 replicates/environment and re-reduce"
                                if decision == "INDETERMINATE" else None)}


# frozen condition-6 accuracy gate thresholds (reviewer 2026-07-19). A FIXED accuracy margin — NOT "within
# replicate SD" — combined with correct sign, a between-replicate cycle-SD ceiling, and all convergence
# diagnostics. This SUPERSEDES the band-only rule that was retired for "could accept zero": here PASS needs
# correct sign AND small error AND small cycle SD AND clean diagnostics, so it cannot pass zero or a diverging set.
# ★ DEFECT FIX 2026-07-25 — the gate as frozen ADMITTED THE NULL IT WAS WRITTEN TO EXCLUDE.
# With target +0.944, `|mean − target| <= GATE_ABS_ERR_PASS(1.0)` accepts mean = 0.0 (error 0.944 < 1.0). So a
# method predicting NO cooperativity change passed: verified directly against this gate, five replicates at
# +0.05 → PASS, and Monte Carlo gave PASS 22 % for a zero-signal method vs 23 % for one that is exactly right.
# A gate you can pass by predicting nothing cannot validate anything.
#
# WHY THIS IS A DEFECT FIX AND NOT A POST-HOC RETUNE — the three things that make it legitimate:
#   1. It CONTRADICTS THE FROZEN RULE'S OWN STATED INTENT. wurz-calib-frozen.json →
#      decision_rule_valB_mini.retired_rule says the combination was adopted "so it cannot accept zero or a
#      diverging replicate set." It accepts zero. The implementation therefore fails to implement the
#      preregistration; restoring that intent is not changing it.
#   2. It is a property of the ARITHMETIC (1.0 > 0.944), present at freeze time on 2026-07-19, and would have
#      been just as wrong had r0 come back favourable. It is not responsive to an unfavourable result.
#   3. It is STRICTLY STRICTER IN EVERY DIRECTION. Goalpost-moving means making a gate easier to pass; this makes
#      it harder, so it cannot manufacture a favourable verdict. Nothing already decided changes: r0 is
#      INDETERMINATE at n=1 under both the old and new rule.
# The original constants are preserved verbatim below and the superseded behaviour is recorded in the frozen JSON.
# Consequence worth stating: under the corrected rule valB_mini is hard to pass even for an accurate method at
# this lane's noise — which is itself the argument for recalibrating onto a larger signal, not for loosening this.
GATE_ANTI_NULL_ENABLED = True          # the corrected rule. `calibration_gate(anti_null=False)` reproduces the
                                       # superseded behaviour FOR AUDIT ONLY — see the note at the check itself.
GATE_REQUIRE_CI_EXCLUDES_ZERO = True   # a resolved nonzero effect, not a noisy positive point estimate
GATE_MEAN_NEARER_TARGET_RATIO = 0.5    # mean must exceed target*this, i.e. sit nearer the target than nearer zero

GATE_ABS_ERR_PASS = 1.0        # |mean ΔΔG_calc − target| <= this AND ... = PASS-eligible
GATE_ABS_ERR_FAIL = 2.0        # |mean ΔΔG_calc − target| >  this = FAIL
GATE_CYCLE_SD_PASS = 0.75      # between-replicate sample SD <= this = PASS-eligible
GATE_CYCLE_SD_EXTEND = 1.0     # SD in (PASS, this] = extend to 5; SD > this after extension = FAIL
GATE_BOUNDARY_MARGIN = 0.5     # a PASS/FAIL result within this of a threshold = extend (condition 3)


def _sign(x):
    return 0 if x == 0 else (1 if x > 0 else -1)


def _diagnostics_fields(diagnostics_ok):
    """The convergence tri-state, rendered for a machine reader. ONE HOME, used on EVERY return of
    `calibration_gate`.

    TRI-STATE, EMITTED AS ONE (fixed 2026-07-27). `diagnostics_ok` was `bool(diagnostics_ok)`, which mapped both
    False (a MEASURED convergence failure) and None (a mandated check NEVER COMPUTED) onto the same reported
    `false`. The decision logic distinguishes them correctly — FAIL vs BORDERLINE — so the collapse was purely in
    what got RECORDED: no machine reader of the verdict JSON could tell a broken leg from an unexamined one, and
    only the prose `reason` carried it. `diagnostics_state` is the third state made explicit; an ABSENT key is
    not an acceptable substitute for it, because `.get()` renders absence as None = NOT_VERIFIED."""
    return {"diagnostics_ok": (None if diagnostics_ok is None else bool(diagnostics_ok)),
            "diagnostics_state": ("CLEAN" if diagnostics_ok is True else
                                  "MEASURED_FAILURE" if diagnostics_ok is False else "NOT_VERIFIED")}


def calibration_gate(ddg_coop_replicates, target_kcal, diagnostics_ok=True, extended=False, anti_null=None):
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
        # ★ THE TRI-STATE WAS COMPUTED AND THEN THROWN AWAY (fixed 2026-07-27). `_diagnostics_ok()` is evaluated
        # at the CALL SITE and handed in, so by the time control reaches here the answer is already known — and
        # this return dropped it. A machine reader of the verdict then saw no `diagnostics_ok` key at all, and
        # `.get()` on the missing key yields None, i.e. NOT_VERIFIED. On the r0 cycle that printed
        # "diagnostics_ok=None" for a state that was a MEASURED FAILURE (both convergence reports carry
        # technical_failure), understating a broken leg as an unexamined one. That is bug §L.6#4 exactly — the
        # collapse of "measured failure" and "never computed" — reappearing one control-flow branch out, which
        # is why the fix is to emit the diagnostics fields from ONE place on EVERY path.
        # ★ AN ABSENT KEY AND AN EXPLICIT null MUST MEAN DIFFERENT THINGS, so the SCHEMA is constant across paths.
        # The 2026-07-27 verdict printed "mean_ddG_coop=KEY ABSENT | target=KEY ABSENT | cycle_SD=KEY ABSENT" — and
        # for the two derived quantities that was honest (with one replicate there IS no replicate mean and no
        # cycle SD), but `target_kcal` was a FROZEN CONSTANT handed straight into this call and thrown away, the
        # same discard as `diagnostics_ok` above. Worse, sharing the "key absent" rendering between "genuinely not
        # defined here" and "the reader and the producer disagree about the field name" gives back exactly the
        # ambiguity the sentinel was added to remove — and a phantom key is what started this. So: a quantity that
        # is undefined at n<2 is emitted as an explicit null (null is not a legal good value for a mean, an SD or
        # an error), and a MISSING key is reserved for one meaning only — a schema mismatch worth shouting about.
        return {"decision": "INDETERMINATE", "reason": "need >=2 independent replicates for a cycle SD.",
                "n_replicates": n, "per_replicate_ddg_coop_kcal": vals,
                "mean_ddg_coop_kcal": None, "cycle_sd_kcal": None, "abs_error_kcal": None,
                "t_ci95_half_width_kcal": None, "correct_sign": None, "target_kcal": target_kcal,
                **_diagnostics_fields(diagnostics_ok)}
    mean = _mean(vals)
    sd = _sample_sd(vals)
    abs_err = abs(mean - target_kcal)
    ci = _ci_halfwidth(sd, n)
    correct_sign = _sign(mean) == _sign(target_kcal)
    metrics = {"n_replicates": n, "per_replicate_ddg_coop_kcal": vals,
               "mean_ddg_coop_kcal": mean, "cycle_sd_kcal": sd,
               "abs_error_kcal": abs_err, "target_kcal": target_kcal,
               # TRI-STATE, EMITTED AS ONE (fixed 2026-07-27). This was bool(diagnostics_ok), which mapped both
               # False (a MEASURED convergence failure) and None (a mandated check NEVER COMPUTED) onto the same
               # reported `false`. The decision logic below distinguishes them correctly — FAIL vs BORDERLINE — so
               # the collapse was purely in what got RECORDED: no machine reader of the verdict JSON could tell a
               # broken leg from an unexamined one, and only the prose `reason` carried it. Emit the third state.
               "t_ci95_half_width_kcal": ci, "correct_sign": correct_sign,
               **_diagnostics_fields(diagnostics_ok),
               "thresholds": {"abs_err_pass": GATE_ABS_ERR_PASS, "abs_err_fail": GATE_ABS_ERR_FAIL,
                              "cycle_sd_pass": GATE_CYCLE_SD_PASS, "cycle_sd_extend": GATE_CYCLE_SD_EXTEND}}

    # ---- FAIL (hard) ----
    if not correct_sign:
        return {"decision": "FAIL", "reason": "wrong sign of cooperativity change (mean %.2f vs target %+.3f)."
                % (mean, target_kcal), **metrics}
    if abs_err > GATE_ABS_ERR_FAIL:
        return {"decision": "FAIL", "reason": "|error| %.2f > %.1f kcal/mol." % (abs_err, GATE_ABS_ERR_FAIL),
                **metrics}
    if diagnostics_ok is False:
        return {"decision": "FAIL", "reason": "persistent convergence diagnostics failure "
                "(overlap/drift/structural) on one or more legs.", **metrics}
    if extended and sd is not None and sd > GATE_CYCLE_SD_EXTEND:
        return {"decision": "FAIL", "reason": "cycle SD %.2f > %.1f kcal/mol AFTER extension to >=5 replicates."
                % (sd, GATE_CYCLE_SD_EXTEND), **metrics}

    # ---- BORDERLINE (extend to 5, do not advance) ----
    reasons = []
    # diagnostics_ok is TRI-STATE (see _diagnostics_ok): True = measured and clean, False = a measured failure
    # (FAIL, above), None = no measured failure but at least one diagnostic was NEVER COMPUTED. None must not
    # reach PASS -- the frozen rule requires that ALL convergence diagnostics pass, and an unmeasured one does
    # not. It routes to BORDERLINE ("extend, do not advance") rather than FAIL, because "not yet measured" is a
    # different claim from "measured and bad".
    if diagnostics_ok is None:
        reasons.append("convergence diagnostics INCOMPLETE (a mandated check was never computed) — 'all "
                       "diagnostics pass' is not satisfied by an unmeasured diagnostic")
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
    # ---- the two anti-null conditions (defect fix 2026-07-25; see the constants block) ----
    # Both are checked HERE, after the FAIL tier and alongside the BORDERLINE reasons, so a result that predicts
    # nothing lands in BORDERLINE/extend rather than PASS. They are AND-conditions on PASS, never routes to PASS.
    # `anti_null` is an AUDIT SWITCH, not a tuning knob. It defaults to the corrected rule; passing False
    # reproduces the SUPERSEDED (pre-2026-07-25) behaviour verbatim so that the amendment's claims — "strictly
    # stricter in every direction", "changes no recorded verdict" — can be re-derived by anyone, rather than
    # taken on trust. Production callers must never pass it: doing so re-admits the null the fix removed. It is
    # deliberately NOT an environment variable, so it cannot be flipped from a workflow input.
    _anti_null = GATE_ANTI_NULL_ENABLED if anti_null is None else bool(anti_null)
    metrics["anti_null_rule_applied"] = _anti_null
    near_zero = _anti_null and mean <= (target_kcal * GATE_MEAN_NEARER_TARGET_RATIO)
    if near_zero:
        reasons.append("mean %+.3f is nearer ZERO than the target %+.3f (needs > %+.3f) — a prediction of 'no "
                       "cooperativity change' must not pass a benchmark whose measured answer is %+.3f"
                       % (mean, target_kcal, target_kcal * GATE_MEAN_NEARER_TARGET_RATIO, target_kcal))
    ci_excludes_zero = (ci is not None and (mean - ci) > 0.0)
    if _anti_null and GATE_REQUIRE_CI_EXCLUDES_ZERO and not ci_excludes_zero:
        reasons.append("t-CI includes zero (%+.3f +/- %.3f) — the effect is not resolved as nonzero"
                       % (mean, ci if ci is not None else float("nan")))
    metrics["anti_null_checks"] = {"mean_nearer_target_than_zero": (not near_zero),
                                  "ci95_excludes_zero": ci_excludes_zero,
                                  "ci95_low": (mean - ci) if ci is not None else None,
                                  "min_mean_for_pass": target_kcal * GATE_MEAN_NEARER_TARGET_RATIO}

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


def convergence_report_name(direction="fwd"):
    """Filename ternary_fep_convergence writes for a given direction. ONE HOME for this name: the workflow's
    mode=converge upload keys off the same rule, and when it did not, a rev run overwrote the fwd cycle's report."""
    return "ternary_convergence.json" if direction == "fwd" else "ternary_convergence_%s.json" % direction


def _convergence_verdict(direction="fwd"):
    """Tri-state read of ONE direction's committed convergence report.

    True = every leg measured and clean; False = a MEASURED failure; None = not verified, covering both a leg with
    an uncomputed diagnostic and an absent/unparseable report."""
    for base in (CKPT, IN):
        p = os.path.join(base, convergence_report_name(direction))
        if os.path.isfile(p):
            try:
                rep = json.load(open(p))
                legs = rep.get("legs", [])
                # Two distinct ways this can fail to be "all diagnostics pass": a MEASURED failure, or a
                # diagnostic that was never computed. Only the first was checked, so a report with
                # diagnostics_complete=false (e.g. ligand-pose RMSD unmeasurable) still returned True.
                if any(l.get("technical_failure") for l in legs):
                    return False
                if legs and any(l.get("diagnostics_complete") is False for l in legs):
                    return None      # tri-state: not failed, but not verified either
                return True
            except Exception:  # noqa: BLE001
                pass
    # ⚠ AN ABSENT REPORT IS NOT A PASS (fixed 2026-07-25). This returned True, with the docstring's rationale
    # that "the convergence gate is its own step". But the frozen rule requires that ALL convergence diagnostics
    # pass, and a report that was never produced satisfies that no more than a diagnostic that was never
    # computed — which the tri-state above already, correctly, refuses to treat as satisfied. Returning True here
    # was the last surviving instance of this lane's signature defect: reporting success while measuring nothing.
    # It is exactly what let every valB verdict silently default its convergence requirement to "pass" before
    # MODE=converge was ever wired to a dispatch path.
    # Strictly stricter, and it changes no recorded verdict: r0 is INDETERMINATE at n=1, which is returned before
    # diagnostics are consulted at all.
    return None


def _rev_leg_present():
    """Does ANY leg of the cycle have a DIRECTION=rev replicate on disk?

    This decides whether a REV convergence report is REQUIRED. It has to be conditional: demanding one
    unconditionally would leave every forward-only cycle permanently unverified, which is a different way of
    being wrong."""
    try:
        return any(_find_leg_files(lid, "rev") for lid in eng.expand_pilot_legs())
    except Exception:  # noqa: BLE001
        return False


def _diagnostics_ok():
    """True unless a committed convergence report (ternary_fep_convergence) flags a technical failure on ANY leg
    (reviewer condition 4/6: persistent overlap/drift/structural failure -> gate FAIL). Tri-state as above.

    ⚠ THE REVERSE LEG'S REPORT IS PART OF THIS (added 2026-07-27). This read only ternary_convergence.json — the
    FORWARD report — so once mode=converge became direction-keyed, ternary_convergence_rev.json was written and
    then consulted by NOBODY. That matters because the rev leg's whole purpose is the preregistered hysteresis
    |dG_fwd + dG_rev| <= 1.0, and a rev leg whose ligand left its pocket or whose MBAR overlap collapsed produces
    a hysteresis that is not a measurement of path error at all. Unchecked, a SMALL hysteresis off a broken rev leg
    would have read as a clean cycle — success asserted from an unexamined input, the same shape as every other
    defect in this function's history. The failure was found precisely BY this convergence analysis on the binary
    arm, so running its own output past the gate unread was not a hypothetical gap.

    A MEASURED failure in either direction -> False. Unverified in either -> None -> BORDERLINE, never PASS."""
    verdicts = [_convergence_verdict("fwd")]
    if _rev_leg_present():
        verdicts.append(_convergence_verdict("rev"))
    if any(v is False for v in verdicts):
        return False
    if any(v is None for v in verdicts):
        return None
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
# |mean_fwd + mean_rev| above this = A->B/B->A antisymmetry broken (bad cycle). SAME preregistered ceiling as the
# calibration decision's hysteresis criterion, so it is DERIVED from the prereg JSON rather than re-typed: two
# copies of `1.0` in one file is how a threshold silently drifts apart from the rule it implements (rule 1).
AUDIT_ANTISYM_MAX_KCAL = hysteresis_max_kcal()
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
    # ⚠ AN UNMEASURED HYSTERESIS IS NOT A ZERO ONE (fixed 2026-07-27). Both halves of this were wrong, and they
    # compounded: `hysteresis_kcal is None or ... <= 1.0` let a leg with NO reverse leg claim converged=True, and
    # `hysteresis_kcal or 0.0` then wrote that absent measurement OUT as the literal value 0.0 — i.e. as PERFECT
    # A->B/B->A antisymmetry. The second is the damaging one, because ternary_coop_gate.evaluate() was written to
    # catch exactly this: it declares hysteresis_kcal "float|null" and FAILS a leg whose value is null
    # (ternary_coop_gate.py:188-192, via _num -> None). Handing it 0.0 instead of null meant that gate could never
    # fire — an unmeasured criterion arrived pre-satisfied, and the reviewer's cycle-closure check was inert for
    # every leg in the lane, since until DIRECTION=rev was unlocked NO leg had a reverse partner at all.
    # calibration_decision() above already routes an unmeasured hysteresis to INDETERMINATE with that exact
    # reasoning; this record contradicted it one function away. Same lane signature: success reported on no
    # measurement. Null now propagates, and `converged` is a claim that has to be earned.
    hys = leg_agg["hysteresis_kcal"]
    conv = bool(leg_agg["n_replicas"] >= 3 and ci is not None and ci <= 1.5
                and hys is not None and hys <= 1.0)
    rec = {
        "schema_version": tio.SCHEMA_VERSION, "leg_id": leg_agg["leg_id"], "environment": env,
        "ddg_alch_kcal": ddg, "ci95_half_width_kcal": ci if ci and ci > 0 else 1e-6,
        "n_replicas": leg_agg["n_replicas"], "hysteresis_kcal": hys,
        "hysteresis_measured": hys is not None,
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


# fields that must AGREE across every leg of a cycle, and why. protocol_hash (above) covers the OpenFE settings;
# these cover the SYSTEM, which it does not.
_SYSTEM_IDENTITY_FIELDS = {
    "n_particles": "different particle counts = a different solvated system, so the legs are not comparable",
    "charge_method": "nagl vs am1bcc = different partial charges = a different Hamiltonian, with the SAME atoms "
                     "(so OpenFE's particle check cannot see it)",
    "setup_cache_version": "v2pe (alchemy from the plain-MD-relaxed complex) vs v1 (raw) -- measured 141,968 vs "
                           "146,020 particles on this leg, i.e. genuinely different systems",
}


def _system_identity_consistency():
    """Every leg of the cycle must describe the SAME system, not merely run the same protocol.

    WHY THIS EXISTS SEPARATELY FROM `_protocol_hash_consistency` (2026-07-25). ΔΔG_coop is a DIFFERENCE of legs and
    |ΔG_fwd + ΔG_rev| is a SUM of them; both are meaningless if the legs describe different systems, and
    protocol_hash does not capture the system. On 2026-07-25 four reverse-leg attempts ran a 146,020-particle `v1`
    build while the forward leg it would be compared against was a 141,968-particle `v2pe` build -- a difference no
    check in this repo would have reported, and one that had to be established by excavating a five-day-old CI log
    from a different workflow.

    Legs written before these fields existed record `None`. That is reported as `unknown`, NOT folded in as
    agreement -- absent provenance must never read as matching provenance (see section B of
    ternary-lane-guard-audit-2026-07-25.md).
    """
    seen = {k: {} for k in _SYSTEM_IDENTITY_FIELDS}
    unknown = {k: [] for k in _SYSTEM_IDENTITY_FIELDS}
    for base in (CKPT, IN):
        for f in glob.glob(os.path.join(base, "**", "leg_*_r*.json"), recursive=True):
            try:
                d = json.load(open(f))
            except Exception:  # noqa: BLE001
                continue
            name = os.path.basename(f)
            # ★★ COMPARE WITHIN A LEG, ACROSS SEEDS — NOT ACROSS LEG TYPES (measured 2026-07-30, 3:07 AM ET).
            #
            # This pooled every leg into one bucket per field, so `n_particles` was compared between the
            # TERNARY leg and the BINARY leg of the same cycle. Those are different systems BY CONSTRUCTION —
            # a ternary complex carries the E3 and its solvent, a binary one does not — so the check could
            # never return CONSISTENT for a ΔΔG_coop cycle. The valB_mini reduction printed:
            #
            #   verdict: INCONSISTENT ... n_particles n_distinct=4:
            #     90324 binary r1 | 90720 binary r2 | 141740 ternary r2 | 144447 ternary r1
            #
            # with the note "the cycle mixes different systems and neither ΔΔG_coop nor the fwd/rev sum is
            # meaningful until that is resolved". Two of those four values are the binary arm and are
            # SUPPOSED to differ from the ternary arm, so as written the guard fires on every healthy
            # cooperativity cycle — the same cry-wolf failure that made the supervisor's handover check
            # useless.
            #
            # ⚠ AND THE FLAG DOES NOT VANISH ONCE GROUPED — MEASURED, NOT ASSUMED. On this very cycle the
            # ternary leg still disagrees with ITSELF across seeds: r1 = 144,447 vs r2 = 141,740, a 2,707
            # particle gap, and the binary leg 90,324 vs 90,720. Grouping removes the comparison that was
            # meaningless by construction and leaves one that is real, which is the whole point: what
            # survives is now evidence rather than noise. Whether independently-solvated replicates SHOULD
            # be allowed to differ in water count — and what that does to a replicate SD — is a scientific
            # call this function does not make; it reports.
            #
            # THE REAL SIGNAL IS PRESERVED, because the defect it was built for lives WITHIN one leg: the
            # 2026-07-25 incident was a 146,020-particle `v1` reverse leg against a 141,968-particle `v2pe`
            # forward leg of the SAME morph and arm. Grouping by everything except the seed keeps exactly
            # that comparison and drops only the across-arm one that is meaningless.
            # ⚠ THE GROUP IS THE ARM, SO DIRECTION IS COMPARED, NOT SPLIT APART. Stripping only the seed
            # would put `..._fwd_r0` and `..._rev_r0` in different groups — and the 2026-07-25 incident this
            # check exists for was precisely a v1 REVERSE leg (146,020) against a v2pe FORWARD leg (141,968)
            # of the same arm. Splitting on direction would have blinded it to its own founding case; the
            # repo's own test for that case is what caught the mistake.
            grp = re.sub(r"_(fwd|rev)_r\d+\.json$", "", re.sub(r"^leg_", "", name))
            if grp == re.sub(r"^leg_", "", name):          # no fwd/rev marker — fall back to seed-stripping
                grp = re.sub(r"_r\d+\.json$", "", grp)
            for k in _SYSTEM_IDENTITY_FIELDS:
                v = d.get(k)
                if v is None:
                    unknown[k].append(name)
                else:
                    seen[k].setdefault(grp, {}).setdefault(str(v), []).append(name)
    out = {}
    inconsistent = []
    unmeasured = []
    for k, why in _SYSTEM_IDENTITY_FIELDS.items():
        # Per-leg groups; a field is INCONSISTENT only if some ONE leg disagrees with itself across seeds.
        groups = {g: {v: sorted(fs) for v, fs in vals.items()} for g, vals in seen[k].items()}
        worst = max((len(v) for v in groups.values()), default=0)
        out[k] = {"n_distinct_within_a_leg": worst, "by_leg": groups,
                  "unrecorded_in": sorted(set(unknown[k])), "why_it_matters": why,
                  "compared": "within each leg across seeds — across-arm differences are expected and are "
                              "NOT compared (a ternary complex and a binary one are different systems by "
                              "construction)"}
        if worst > 1:
            inconsistent.append(k)
        elif not groups and unknown[k]:
            unmeasured.append(k)
    if inconsistent:
        verdict = "INCONSISTENT"
        note = ("a leg disagrees with ITSELF across seeds on %s -- the replicates of that leg are different "
                "systems, so neither ΔΔG_coop nor the fwd/rev sum is meaningful until that is resolved"
                % ", ".join(inconsistent))
    elif unmeasured:
        verdict = "UNKNOWN"
        note = ("no leg records %s (written before system-identity was captured), so cross-leg comparability is "
                "NOT VERIFIED -- this is 'unmeasured', not 'consistent'" % ", ".join(unmeasured))
    else:
        verdict = "CONSISTENT"
        note = "every leg that records system identity agrees on it"
    return {"verdict": verdict, "note": note, "fields": out,
            "partially_unrecorded": sorted({f for k in _SYSTEM_IDENTITY_FIELDS for f in set(unknown[k])})}


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
            # per_replicate_ddg_coop_kcal is emitted by calibration_gate itself (it IS the gate's input), so it
            # is not re-attached here: a field written in two places is a field that can disagree with itself.
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
        "system_identity_consistency": _system_identity_consistency(),
        "n_available_morphs": sum(1 for s in summaries if s.get("available")),
    }
    out = os.path.join(CKPT, "ternary_coop_reduction.json")
    json.dump(report, open(out, "w"), indent=2)
    print("[tfep-reduce] wrote %s (%d/%d morphs available)"
          % (out, report["n_available_morphs"], len(summaries)), flush=True)
    return report


if __name__ == "__main__":
    reduce_all()
