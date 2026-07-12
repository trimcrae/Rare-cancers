#!/usr/bin/env python3
"""NR4A3 ternary-cooperativity RETROSPECTIVE-BAR GATE (prereg §3 as-written, hardened).

Implements `nr4a3-ternary-coop-prereg.md` §3 / `nr4a3-ternary-coop-prereg.json → retrospective_bar` EXACTLY as
an automated, auditable pass/fail. STAGE-3 GATE: no prospective NR4A3 ternary ranking is trusted until ALL
sub-gates PASS. Encoding + testing the frozen thresholds here stops any criterion being re-decided post-hoc on
a favorable number (same discipline as `abfe_repair_gate.py` for Track A).

Hardening (reviewer 'RETURN FOR FIXES', 2026-07-11) — the gate must not PASS inputs that violate the prose:
  1. Non-finite rejection + fail-closed safety booleans. `_num()` rejects NaN/inf (and bool). Required safety
     booleans (pathology, pose reversal, inactive-control competence, LOO reversal, sensitivity survival) must
     be EXPLICIT booleans on a present record; missing/non-bool -> FAIL, never silently False.
  2. Frozen expected-system + expected-leg manifests. Legs validated for required-subset coverage; the VHL
     panel validated for n>=6, all-verified, keyed-by-ID records, and required composition.
  3. VHL class-correctness + LOO COMPUTED in-gate from per-system records (frozen class boundaries), not
     accepted as trusted summary counts/booleans.
  4. Kendall tau-b with explicit tie handling.
  5. Corrected interval validation (favored-active side => the ENTIRE interval above zero, lo>0; lo<=hi finite;
     probabilities in [0,1]).
  6. 95% CI half-width applied to EVERY decision-bearing quantity via a frozen decision_quantities manifest
     (static required IDs + one dg_coop entry per VHL scoring system).

Pure stdlib: evaluates a RESULTS DICT (whatever the ternary analyzer emits), so it imports and unit-tests with
no numpy/MD stack. Thresholds come from the FROZEN JSON (single source of truth); tests catch JSON<->code
drift. Every sub-gate returns {passed, available, ...}; `available=False` (verdict None) only when a whole
required results section is absent — a PRESENT-but-malformed record FAILS (does not defer).
"""
import json
import math
import os
import sys

import ternary_coop as _tc   # alpha<->dG_coop conversion (single source of the sign convention)

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN_JSON = os.path.join(HERE, "nr4a3-ternary-coop-prereg.json")
_MISSING = object()


# =============================================================================================================
# frozen thresholds (single source of truth = the prereg JSON)
# =============================================================================================================
def load_frozen(path=FROZEN_JSON):
    with open(path) as f:
        return json.load(f)


def load_bar(path=FROZEN_JSON):
    return load_frozen(path)["retrospective_bar"]


# =============================================================================================================
# pure value helpers — FINITE-only numbers, EXPLICIT booleans
# =============================================================================================================
def _num(x):
    """Coerce to a FINITE float, else None. Rejects NaN/inf (so a NaN can't evade a threshold via False
    comparisons) and rejects bool (isinstance(True,int) is True in Python — a stray bool is not a measurement)."""
    if isinstance(x, bool) or x is None:
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _req_bool(container, key, reasons, ctx):
    """Return an EXPLICIT boolean or None (+ append a failure reason). Missing key or non-bool -> None + reason
    (fail closed): a present record that omits a required safety attestation is a failure, never silently False."""
    v = container.get(key, _MISSING)
    if v is _MISSING:
        reasons.append("%s: required boolean '%s' is MISSING (fail-closed)" % (ctx, key))
        return None
    if not isinstance(v, bool):
        reasons.append("%s: required boolean '%s' is non-bool (%r)" % (ctx, key, v))
        return None
    return v


def _finite_interval(lo, hi):
    """(lo, hi) as finite floats with lo<=hi, else None. Rejects reversed/missing/non-finite bounds."""
    flo, fhi = _num(lo), _num(hi)
    if flo is None or fhi is None or flo > fhi:
        return None
    return (flo, fhi)


def _deferred(name, missing):
    return {"passed": None, "available": False,
            "note": "sub-gate '%s' deferred: results dict missing %s" % (name, missing)}


# =============================================================================================================
# class + rank helpers (fixes 3 & 4)
# =============================================================================================================
def classify_alpha(alpha, favorable_min, unfavorable_max):
    """Frozen 3-class rule (point estimate). Returns 'cooperative' | 'anti_cooperative' | 'neutral' | None."""
    a = _num(alpha)
    if a is None or a <= 0:
        return None
    if a >= favorable_min:
        return "cooperative"
    if a <= unfavorable_max:
        return "anti_cooperative"
    return "neutral"


def kendall_tau_b(pairs):
    """Kendall tau-b with explicit tie handling (fix 4). `pairs` = [(x, y), ...]. tau_b = (C-D)/sqrt(A*B) with
    A = C+D+Ty (pairs not tied in x), B = C+D+Tx (pairs not tied in y); pairs tied in BOTH are excluded from
    both. Returns None if fewer than 2 pairs or a degenerate (zero) denominator."""
    n = len(pairs)
    if n < 2:
        return None
    C = D = Tx = Ty = 0
    for i in range(n):
        xi, yi = pairs[i]
        for j in range(i + 1, n):
            dx = xi - pairs[j][0]
            dy = yi - pairs[j][1]
            if dx == 0 and dy == 0:
                continue
            if dx == 0:        # tied in x only
                Tx += 1
            elif dy == 0:      # tied in y only
                Ty += 1
            elif dx * dy > 0:
                C += 1
            else:
                D += 1
    A = C + D + Ty
    B = C + D + Tx
    denom = math.sqrt(A * B) if (A > 0 and B > 0) else 0.0
    return (C - D) / denom if denom > 0 else None


def tau_b_exact_p(pairs):
    """EXACT one-sided permutation p-value for tau-b (reviewer 2026-07-12: report exact, not asymptotic —
    the calibration panel is tiny, n=5..7, so all n! permutations are enumerable). Fixes x, permutes y over
    every permutation, and returns P(tau_b(perm) >= tau_b(observed)). Returns None if tau is undefined or n>8
    (guard against a factorial blow-up). Pure."""
    import itertools
    n = len(pairs)
    if n < 2 or n > 8:
        return None
    obs = kendall_tau_b(pairs)
    if obs is None:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    ge = tot = 0
    for perm in itertools.permutations(ys):
        t = kendall_tau_b(list(zip(xs, perm)))
        if t is None:
            continue
        tot += 1
        if t >= obs - 1e-12:
            ge += 1
    return (ge / tot) if tot else None


def _required_correct(n, floor=5, num=5, den=6):
    """Frozen rule: required = max(floor, ceil(num/den * n))."""
    return max(floor, int(math.ceil(num / float(den) * n)))


# =============================================================================================================
# sub-gate 1 — technical convergence (per free-energy leg) + frozen leg-coverage
# =============================================================================================================
def gate_technical_convergence(results, frozen):
    """§3a + frozen_manifest leg coverage. `results['legs']` = list of per-leg dicts:
    {name, n_replicas, hysteresis_kcal (or cycle_closure_kcal), ci95_half_width_kcal, n_starting_poses,
     rank_reversal_under_loo (bool), pathology (bool)}."""
    bar = frozen["retrospective_bar"]
    c = bar["technical_convergence"]
    legs = results.get("legs")
    if not legs:
        return _deferred("technical_convergence", "results['legs']")
    names = set()
    failures = []
    for leg in legs:
        name = leg.get("name", "?")
        names.add(name)
        reasons = []
        reps = leg.get("n_replicas")
        if not isinstance(reps, int) or isinstance(reps, bool) or reps < c["min_replicas_per_leg"]:
            reasons.append("n_replicas=%r < %d" % (reps, c["min_replicas_per_leg"]))
        hyst = _num(leg.get("hysteresis_kcal"))
        if hyst is None:
            hyst = _num(leg.get("cycle_closure_kcal"))
        if hyst is None or hyst > c["cycle_closure_or_hysteresis_kcal_max"]:
            reasons.append("hysteresis/closure=%r > %.2f" % (hyst, c["cycle_closure_or_hysteresis_kcal_max"]))
        ci = _num(leg.get("ci95_half_width_kcal"))
        if ci is None or ci > c["ci95_half_width_kcal_max"]:
            reasons.append("ci95_half_width=%r > %.2f" % (ci, c["ci95_half_width_kcal_max"]))
        poses = leg.get("n_starting_poses")
        if (not isinstance(poses, int) or isinstance(poses, bool)
                or poses < c["min_independent_starting_poses_per_architecture"]):
            reasons.append("n_starting_poses=%r < %d" % (poses, c["min_independent_starting_poses_per_architecture"]))
        rr = _req_bool(leg, "rank_reversal_under_loo", reasons, "leg '%s'" % name)
        if rr is True:
            reasons.append("rank_reversal_under_leave_one_pose_out=True")
        pa = _req_bool(leg, "pathology", reasons, "leg '%s'" % name)
        if pa is True:
            reasons.append("restraint/mapping/microstate pathology flagged")
        if reasons:
            failures.append({"leg": name, "reasons": reasons})

    # frozen leg-coverage (required subset)
    expected = frozen.get("frozen_manifest", {}).get("ternary_pilot_expected_leg_ids", [])
    missing_legs = [e for e in expected if e not in names]
    coverage_fail = bool(missing_legs)
    return {"passed": (not failures and not coverage_fail), "available": True, "n_legs": len(legs),
            "failures": failures, "missing_expected_legs": missing_legs}


# =============================================================================================================
# sub-gate 2 — quantitative VHL panel (Layer 1): composition + class-correct + tau-b + LOO, ALL in-gate
# =============================================================================================================
def _panel_system_ok(s):
    """Structural validation of one panel record; returns (record-or-None, reasons)."""
    reasons = []
    sid = s.get("id")
    if not isinstance(sid, str) or not sid:
        reasons.append("system missing string 'id'")
        sid = None
    role = s.get("role")
    if role not in ("cooperative", "anti_cooperative", "neutral", "inactive_control"):
        reasons.append("system %r: bad/missing role %r" % (sid, role))
    verified = s.get("verified")
    if not isinstance(verified, bool):
        reasons.append("system %r: 'verified' must be an explicit boolean" % sid)
        verified = None
    independent = s.get("independent_vhl")
    if not isinstance(independent, bool):
        reasons.append("system %r: 'independent_vhl' must be an explicit boolean" % sid)
        independent = None
    is_mz1 = s.get("is_mz1", False)
    if not isinstance(is_mz1, bool):
        reasons.append("system %r: 'is_mz1' must be a boolean" % sid)
    pred = _num(s.get("predicted_alpha"))
    pred_dg = _num(s.get("predicted_dg_coop"))
    # SIGN-CONVENTION ENFORCEMENT (reviewer 2026-07-12): the physics method predicts dG_coop; measured is alpha.
    # dG_coop = -RT ln(alpha) => higher alpha == more-negative (more favorable) dG_coop. To rank on a CONSISTENT
    # scale we convert a predicted dG_coop to a predicted alpha via the same convention, so tau-b on
    # (predicted_alpha, measured_alpha) is a POSITIVE rank correspondence. Comparing raw dG_coop with alpha would
    # invert the conclusion (guarded by the invariant tests). If both are supplied they must AGREE in sign.
    if pred is None and pred_dg is not None:
        pred = _tc.alpha_from_dg_coop(pred_dg)
    elif pred is not None and pred_dg is not None:
        implied = _tc.alpha_from_dg_coop(pred_dg)
        if implied is not None and pred > 0 and implied > 0 and (math.log(pred) * math.log(implied) < 0
                                                                 and abs(math.log(pred) - math.log(implied)) > 1e-6):
            reasons.append("system %r: predicted_alpha and predicted_dg_coop disagree in SIGN "
                           "(alpha=%.3g implies dG of opposite sign)" % (sid, pred))
    meas = _num(s.get("measured_alpha"))
    ci = _num(s.get("dg_coop_ci_half_width_kcal"))
    return ({"id": sid, "role": role, "verified": verified, "independent_vhl": independent,
             "is_mz1": bool(is_mz1) if isinstance(is_mz1, bool) else False,
             "predicted_alpha": pred, "predicted_dg_coop": pred_dg, "measured_alpha": meas,
             "dg_coop_ci_half_width_kcal": ci}, reasons)


def _score_panel_subset(systems, vp):
    """Compute (class_correct, required, tau_b, any_inactive_competent) for a subset of validated systems.
    Pure — used both for the full panel and for each leave-one-out subset."""
    cb = vp["class_boundaries"]
    fav, unf = cb["alpha_favorable_min"], cb["alpha_unfavorable_max"]
    n = len(systems)
    required = _required_correct(n)
    correct = 0
    tau_pairs = []
    inactive_competent = False
    for s in systems:
        pred_class = classify_alpha(s["predicted_alpha"], fav, unf)
        if s["role"] == "inactive_control":
            competent = (pred_class == "cooperative")
            if competent:
                inactive_competent = True
            if not competent:          # correct = predicted non-competent
                correct += 1
        else:
            meas_class = classify_alpha(s["measured_alpha"], fav, unf)
            if pred_class is not None and pred_class == meas_class:
                correct += 1
            if s["measured_alpha"] is not None:
                tau_pairs.append((s["predicted_alpha"], s["measured_alpha"]))
    tau = kendall_tau_b(tau_pairs)
    return {"n": n, "class_correct": correct, "required": required, "tau_b": tau,
            "inactive_competent": inactive_competent, "n_tau_pairs": len(tau_pairs), "tau_pairs": tau_pairs}


def gate_vhl_panel(results, frozen):
    """§3b, computed in-gate. `results['vhl_panel']['systems']` = keyed per-system records:
    {id, role, verified, independent_vhl, is_mz1, predicted_alpha, measured_alpha, dg_coop_ci_half_width_kcal}."""
    bar = frozen["retrospective_bar"]
    vp = bar["vhl_panel"]
    p = results.get("vhl_panel")
    if not p or not p.get("systems"):
        return _deferred("vhl_panel", "results['vhl_panel']['systems']")
    raw = p["systems"]
    reasons = []

    validated = []
    for s in raw:
        rec, rr = _panel_system_ok(s)
        reasons.extend(rr)
        validated.append(rec)

    ids = [r["id"] for r in validated if r["id"]]
    if len(set(ids)) != len(ids):
        reasons.append("duplicate system IDs: %r" % [i for i in ids if ids.count(i) > 1])
    n = len(validated)
    if n < vp["min_systems"]:
        reasons.append("n_systems=%d < min %d" % (n, vp["min_systems"]))
    if vp.get("require_all_verified") and not all(r["verified"] is True for r in validated):
        reasons.append("not all panel systems are verified=True (unverified systems may not enter the scored manifest)")

    # frozen expected-system coverage (required-subset) when the curated manifest is non-empty
    exp_sys = frozen.get("calibration", {}).get("layer1_vhl_panel", {}).get("expected_system_ids", [])
    missing_sys = [e for e in exp_sys if e not in set(ids)]
    if missing_sys:
        reasons.append("missing expected (frozen) system IDs: %r" % missing_sys)

    # composition (measured classes)
    cb = vp["class_boundaries"]
    fav, unf = cb["alpha_favorable_min"], cb["alpha_unfavorable_max"]
    comp = vp["composition_required"]
    n_strong = sum(1 for r in validated if r["role"] != "inactive_control"
                   and classify_alpha(r["measured_alpha"], fav, unf) == "cooperative")
    n_weak = sum(1 for r in validated if r["role"] != "inactive_control"
                 and classify_alpha(r["measured_alpha"], fav, unf) in ("neutral", "anti_cooperative"))
    n_inactive = sum(1 for r in validated if r["role"] == "inactive_control")
    n_independent = sum(1 for r in validated if r["independent_vhl"] is True)
    has_mz1 = any(r["is_mz1"] for r in validated)
    if n_strong < comp["min_strong_cooperative"]:
        reasons.append("strong-cooperative systems %d < %d" % (n_strong, comp["min_strong_cooperative"]))
    if n_weak < comp["min_weak_or_negative"]:
        reasons.append("weak/negative systems %d < %d" % (n_weak, comp["min_weak_or_negative"]))
    if n_inactive < comp["min_inactive_control"]:
        reasons.append("inactive controls %d < %d" % (n_inactive, comp["min_inactive_control"]))
    if n_independent < comp["min_independent_vhl"]:
        reasons.append("independent-VHL systems %d < %d (>=1 mandatory)" % (n_independent, comp["min_independent_vhl"]))

    # per-system dg_coop CI half-width (covers panel-prediction / cooperativity-difference decision quantities)
    ci_max = vp["dg_coop_ci_half_width_kcal_max"]
    for r in validated:
        if r["role"] == "inactive_control":
            continue
        if r["dg_coop_ci_half_width_kcal"] is None or r["dg_coop_ci_half_width_kcal"] > ci_max:
            reasons.append("system %r dg_coop_ci_half_width=%r > %.2f (or missing/non-finite)"
                           % (r["id"], r["dg_coop_ci_half_width_kcal"], ci_max))

    # main scoring (in-gate)
    scored = _score_panel_subset(validated, vp)
    if scored["class_correct"] < scored["required"]:
        reasons.append("class-correct %d/%d < required %d" % (scored["class_correct"], n, scored["required"]))
    if scored["tau_b"] is None or scored["tau_b"] < vp["kendall_tau_min"]:
        reasons.append("kendall tau_b=%r < %.2f" % (scored["tau_b"], vp["kendall_tau_min"]))
    if scored["inactive_competent"]:
        reasons.append("an inactive stereochemical control was classified ternary-competent")

    # leave-one-compound-out (in-gate, from records)
    loo_failures = []
    if n >= 2:
        for i in range(n):
            subset = validated[:i] + validated[i + 1:]
            sc = _score_panel_subset(subset, vp)
            sub_fail = []
            if sc["class_correct"] < sc["required"]:
                sub_fail.append("class-correct %d/%d < %d" % (sc["class_correct"], sc["n"], sc["required"]))
            if sc["tau_b"] is None or sc["tau_b"] < vp["kendall_tau_min"]:
                sub_fail.append("tau_b=%r < %.2f" % (sc["tau_b"], vp["kendall_tau_min"]))
            if sc["inactive_competent"]:
                sub_fail.append("inactive control competent")
            if sub_fail:
                loo_failures.append({"excluded": validated[i]["id"], "reasons": sub_fail})
    if loo_failures:
        reasons.append("does not survive leave-one-compound-out (%d exclusions fail)" % len(loo_failures))

    return {"passed": not reasons, "available": True, "n_systems": n,
            "class_correct": scored["class_correct"], "required_class_correct": scored["required"],
            "kendall_tau_b": scored["tau_b"],
            "kendall_tau_b_exact_p": tau_b_exact_p(scored.get("tau_pairs") or []),   # reported, not gated
            "composition": {"strong": n_strong, "weak_or_negative": n_weak,
            "inactive": n_inactive, "independent_vhl": n_independent, "has_mz1": has_mz1},
            "loo_failures": loo_failures, "failures": reasons}


# =============================================================================================================
# sub-gate 3 — NR-V04 affinity control (Layer 2 — the two things the co-fold failed)
# =============================================================================================================
def gate_nrv04_affinity_control(results, frozen):
    """§3c. `results['nrv04_affinity_control']` = {active_vs_epimer_binary_vhl_kcal, binary_vhl_ci_low,
    binary_vhl_ci_high, active_vs_epimer_effective_ternary_kcal, any_retained_pose_reverses (bool)}.
    Sign: POSITIVE margin = active bound MORE strongly than epimer."""
    bar = frozen["retrospective_bar"]
    c = bar["nrv04_affinity_control"]
    r = results.get("nrv04_affinity_control")
    if not r:
        return _deferred("nrv04_affinity_control", "results['nrv04_affinity_control']")
    reasons = []
    bin_margin = _num(r.get("active_vs_epimer_binary_vhl_kcal"))
    if bin_margin is None or bin_margin < c["active_vs_epimer_binary_vhl_min_kcal"]:
        reasons.append("binary VHL active-vs-epimer margin=%r < %.1f" %
                       (bin_margin, c["active_vs_epimer_binary_vhl_min_kcal"]))
    if c["active_vs_epimer_binary_vhl_ci_excludes_zero"]:
        iv = _finite_interval(r.get("binary_vhl_ci_low"), r.get("binary_vhl_ci_high"))
        if iv is None:
            reasons.append("binary VHL CI missing/non-finite/reversed")
        elif not iv[0] > 0:   # favored-active side => ENTIRE interval above zero
            reasons.append("binary VHL CI [%g, %g] not entirely above zero (need ci_low>0)" % iv)
    ter_margin = _num(r.get("active_vs_epimer_effective_ternary_kcal"))
    if ter_margin is None or ter_margin < c["active_vs_epimer_effective_ternary_min_kcal"]:
        reasons.append("effective-ternary active-vs-epimer margin=%r < %.1f" %
                       (ter_margin, c["active_vs_epimer_effective_ternary_min_kcal"]))
    rev = _req_bool(r, "any_retained_pose_reverses", reasons, "nrv04_affinity_control")
    if rev is True:
        reasons.append("a retained pose reverses the active/epimer ordering")
    return {"passed": not reasons, "available": True,
            "binary_margin_kcal": bin_margin, "ternary_margin_kcal": ter_margin, "failures": reasons}


# =============================================================================================================
# sub-gate 4 — NR4A family transfer (Layer 2)
# =============================================================================================================
def gate_nr4a_family_transfer(results, frozen):
    """§3d. `results['nr4a_family_transfer']` = {recruit_diff_nr4a1_vs_{nr4a2,nr4a3}_kcal (+ _ci_lo/_ci_hi),
    joint_prob_nr4a1_best, survives_pose_and_conformer_sensitivity (bool)}. POSITIVE = NR4A1 favored."""
    bar = frozen["retrospective_bar"]
    c = bar["nr4a_family_transfer"]
    r = results.get("nr4a_family_transfer")
    if not r:
        return _deferred("nr4a_family_transfer", "results['nr4a_family_transfer']")
    reasons = []
    for para, key in (("NR4A2", "nr4a2"), ("NR4A3", "nr4a3")):
        d = _num(r.get("recruit_diff_nr4a1_vs_%s_kcal" % key))
        if d is None or d < c["each_difference_min_kcal"]:
            reasons.append("NR4A1 vs %s recruit diff=%r < %.1f" % (para, d, c["each_difference_min_kcal"]))
        iv = _finite_interval(r.get("recruit_diff_nr4a1_vs_%s_ci_lo" % key),
                              r.get("recruit_diff_nr4a1_vs_%s_ci_hi" % key))
        if iv is None:
            reasons.append("NR4A1 vs %s interval missing/non-finite/reversed" % para)
        elif not iv[0] > 0:
            reasons.append("NR4A1 vs %s %d%% interval [%g, %g] not entirely above zero (need ci_lo>0)" %
                           (para, c["each_difference_interval_pct_excludes_zero"], iv[0], iv[1]))
    jp = _num(r.get("joint_prob_nr4a1_best"))
    lo, hi = c["joint_prob_range"]
    if jp is None or not (lo <= jp <= hi):
        reasons.append("joint P(NR4A1 best)=%r outside [%g, %g]" % (jp, lo, hi))
    elif jp <= c["joint_prob_nr4a1_best_min"]:
        reasons.append("joint P(NR4A1 best)=%g <= %.2f (strict)" % (jp, c["joint_prob_nr4a1_best_min"]))
    surv = _req_bool(r, "survives_pose_and_conformer_sensitivity", reasons, "nr4a_family_transfer")
    if surv is False:
        reasons.append("does not survive starting-pose and conformer-panel sensitivity")
    return {"passed": not reasons, "available": True, "joint_prob_nr4a1_best": jp, "failures": reasons}


# =============================================================================================================
# sub-gate 5 — CI coverage over EVERY decision-bearing quantity (fix 6)
# =============================================================================================================
def gate_ci_coverage(results, frozen):
    """§ ci_coverage. Validates results['decision_quantities'] against the frozen required IDs (+ one
    dg_coop entry per VHL scoring system) and each entry's interval/half-width."""
    bar = frozen["retrospective_bar"]
    cc = bar["ci_coverage"]
    dqs = results.get("decision_quantities")
    if dqs is None:
        return _deferred("ci_coverage", "results['decision_quantities']")
    reasons = []
    by_id = {}
    for e in dqs:
        eid = e.get("id")
        if not isinstance(eid, str) or not eid:
            reasons.append("a decision_quantity has no string id")
            continue
        if eid in by_id:
            reasons.append("duplicate decision_quantity id %r" % eid)
        by_id[eid] = e

    # required coverage: static IDs + one dg_coop per VHL scoring system
    required_ids = list(cc["required_decision_quantity_ids"])
    vp = results.get("vhl_panel") or {}
    for s in (vp.get("systems") or []):
        sid = s.get("id")
        if isinstance(sid, str) and sid and s.get("role") != "inactive_control":
            required_ids.append("vhl_dg_coop::%s" % sid)
    missing = [i for i in required_ids if i not in by_id]
    if missing:
        reasons.append("missing required decision quantities: %r" % missing)

    # validate every provided entry
    hw_max = cc["ci_half_width_kcal_max"]
    lvl = cc["required_interval_level"]
    for eid, e in by_id.items():
        est = _num(e.get("estimate"))
        if est is None:
            reasons.append("dq %r: non-finite/missing estimate" % eid)
        iv = _finite_interval(e.get("ci_lo"), e.get("ci_hi"))
        if iv is None:
            reasons.append("dq %r: interval missing/non-finite/reversed" % eid)
            continue
        hw = _num(e.get("half_width"))
        derived = (iv[1] - iv[0]) / 2.0
        if hw is None or abs(hw - derived) > 0.05:
            reasons.append("dq %r: half_width=%r inconsistent with (hi-lo)/2=%.3f" % (eid, hw, derived))
            hw = derived
        if hw > hw_max:
            reasons.append("dq %r: half_width=%.3f > %.2f" % (eid, hw, hw_max))
        il = _num(e.get("interval_level"))
        if il is None or abs(il - lvl) > 1e-9:
            reasons.append("dq %r: interval_level=%r != %g" % (eid, e.get("interval_level"), lvl))
    return {"passed": not reasons, "available": True, "n_quantities": len(by_id),
            "required_ids": required_ids, "failures": reasons}


# =============================================================================================================
# top-level gate
# =============================================================================================================
_SUBGATES = (
    ("technical_convergence", gate_technical_convergence),
    ("vhl_panel", gate_vhl_panel),
    ("nrv04_affinity_control", gate_nrv04_affinity_control),
    ("nr4a_family_transfer", gate_nr4a_family_transfer),
    ("ci_coverage", gate_ci_coverage),
)


def evaluate_retrospective_bar(results, frozen_path=FROZEN_JSON):
    """Evaluate the full prereg §3 on a ternary results dict. Verdict True only if ALL sub-gates PASS; False if
    any AVAILABLE sub-gate FAILS; None if any sub-gate is deferred (its results section absent) and none failed."""
    frozen = load_frozen(frozen_path)
    subs = {name: fn(results, frozen) for name, fn in _SUBGATES}
    any_fail = any(s.get("passed") is False for s in subs.values())
    any_deferred = any(s.get("passed") is None for s in subs.values())
    verdict = False if any_fail else (None if any_deferred else True)
    return {"prospective_ranking_authorized": verdict, "sub_gates": subs,
            "failure_semantics": frozen["retrospective_bar"]["failure_semantics"],
            "prereg": "nr4a3-ternary-coop-prereg.md §3 / .json retrospective_bar"}


def expected_results_schema():
    """The results-dict shape the analyzer must populate (documentation for the future producer)."""
    return {
        "legs": [{"name": "str (must cover frozen_manifest.ternary_pilot_expected_leg_ids)",
                  "n_replicas": "int>=3", "hysteresis_kcal": "float|null", "cycle_closure_kcal": "float|null",
                  "ci95_half_width_kcal": "float", "n_starting_poses": "int>=2",
                  "rank_reversal_under_loo": "bool (REQUIRED)", "pathology": "bool (REQUIRED)"}],
        "vhl_panel": {"systems": [{"id": "str (unique)", "role": "cooperative|anti_cooperative|neutral|inactive_control",
                      "verified": "bool (REQUIRED true to score)", "independent_vhl": "bool",
                      "is_mz1": "bool", "predicted_alpha": "float>0", "measured_alpha": "float>0 (omit for inactive_control)",
                      "dg_coop_ci_half_width_kcal": "float<=1.5 (scoring systems)"}]},
        "nrv04_affinity_control": {"active_vs_epimer_binary_vhl_kcal": "float", "binary_vhl_ci_low": "float",
                                   "binary_vhl_ci_high": "float", "active_vs_epimer_effective_ternary_kcal": "float",
                                   "any_retained_pose_reverses": "bool (REQUIRED)"},
        "nr4a_family_transfer": {"recruit_diff_nr4a1_vs_nr4a2_kcal": "float",
                                 "recruit_diff_nr4a1_vs_nr4a2_ci_lo": "float",
                                 "recruit_diff_nr4a1_vs_nr4a2_ci_hi": "float",
                                 "recruit_diff_nr4a1_vs_nr4a3_kcal": "float",
                                 "recruit_diff_nr4a1_vs_nr4a3_ci_lo": "float",
                                 "recruit_diff_nr4a1_vs_nr4a3_ci_hi": "float",
                                 "joint_prob_nr4a1_best": "float in [0,1]",
                                 "survives_pose_and_conformer_sensitivity": "bool (REQUIRED)"},
        "decision_quantities": [{"id": "str (must cover ci_coverage.required_decision_quantity_ids + vhl_dg_coop::<sid>)",
                                 "estimate": "float", "ci_lo": "float", "ci_hi": "float",
                                 "half_width": "float<=1.5", "interval_level": "0.95"}],
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
            if s.get("missing_expected_legs"):
                print("        - missing expected legs: %r" % s["missing_expected_legs"])
            if s.get("note"):
                print("        note: %s" % s["note"])
        print("  => prospective_ranking_authorized = %s" % res["prospective_ranking_authorized"])
    v = res["prospective_ranking_authorized"]
    return 0 if v is True else (2 if v is None else 1)


if __name__ == "__main__":
    sys.exit(_cli())
