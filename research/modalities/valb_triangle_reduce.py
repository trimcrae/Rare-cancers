#!/usr/bin/env python3
"""The closure residual R, from the six leg records — the triangle's ONLY deliverable.

    R = ddG_coop(T1) + ddG_coop(T2) - ddG_coop(T3),   ddG_coop(edge) = dG_ternary(edge) - dG_binary(edge)

and, because ddG_coop is itself a difference,

    R = R_ternary - R_binary,   R_env = dG_env(T1) + dG_env(T2) - dG_env(T3)

WHY R IS WORTH SIX LEGS, STATED ONCE SO IT TRAVELS WITH EVERY READING OF THE NUMBER. Write a computed edge as
ddG_calc = ddG_true + e. Around a closed cycle the true terms telescope to zero, so R = sum_cycle e. If the
error is a PER-ENDPOINT bias — e(A->B) = eps(B) - eps(A) for any state function eps — then sum_cycle e
telescopes to zero as well. So R is IDENTICALLY ZERO for every error class that is a function of the endpoint
STATE: force field, the SMARCA4->SMARCA2 homology substitution, NAGL partial charges, protonation. R is
non-zero ONLY for PATH error. That is what makes this a discriminating experiment rather than a confirmation:

    R ~ 0                 -> r0's 1.478 kcal/mol miss is NOT a path error, so more/better sampling cannot fix
                             it. The miss lives in the model or the reference data — where closure is
                             provably blind — and the known-answer accuracy requirement stays OPEN.
    R materially non-zero -> there IS a path error of that size in this workflow, and sampling/protocol work
                             is the right lever.

⚠ REPORT R_ternary AND R_binary SEPARATELY, ALWAYS, AND NEVER R ALONE. R = R_ternary - R_binary, so a clean R
can be two large closures cancelling. Both come free from the same six legs, so reporting only R is strictly
weaker for zero saving (`valb_triangle_closure.closure_decomposition`).

⚠ ERROR BARS ARE REPLICATE SD, NEVER MBAR SE — AND AT n=1 THERE IS NO REPLICATE SD, SO NONE IS QUOTED.
The MBAR SE is a LOWER bound on sigma_leg (it does not see slow modes) and this lane's assumed replicate SD of
0.7 is an UPPER bound for a same-seed triangle (it includes the homology-model swap a same-seed design
removes). Those differ by a factor of ~15, so the n=1 scout's own resolution is unknown by a factor of ~7.
★ SUPERSEDED IN PART, 2026-07-30: the 0.7 is an ASSUMPTION and the valB_mini n=3 replicates have since bounded
sigma_leg well below it, which shrinks the AMBIGUOUS band by ~3x. The frozen verdict below still uses the
original bounds ON PURPOSE — narrowing makes the *hopeful* branch easier to reach — and the measured reading
is carried beside it in `measured_sigma_addendum`. Derivation: valb_failure_propagation.sigma_leg_now_bounded.
The
asymmetry is what makes it worth buying anyway: a SMALL |R| is strong evidence, because it bounds the path
error AND the noise at once; a LARGE |R| at n=1 is AMBIGUOUS, because one draw cannot separate a systematic
from an unlucky sample. So this reducer can ADMIT the cycle and cannot CONVICT it, and it says so in the
verdict rather than leaving a reader to infer it.

WHAT IT REFUSES, each because accepting it would compute a different quantity while looking identical:
  * a MIXED SEED across the six legs — the edges are then computed on different Hamiltonians, endpoint states
    are not shared, the telescoping fails, and |R| measures homology-model sensitivity instead;
  * a MIXED TIMESTEP — T1 is r0 at 2 fs; a 4 fs T2/T3 makes R a measure of the timestep difference;
  * a MIXED PROTOCOL HASH or a restrained-vs-unrestrained mix — same argument, and it is exactly why the
    triangle's binary legs run UNRESTRAINED (`valb_triangle_legs`);
  * a SOLVENT leg — it cancels exactly inside ddG_coop, so including one adds noise at best;
  * a MISSING leg — five legs cannot close a triangle, and an R computed from a partial cycle is not a
    smaller-n R, it is a different number.
System identity (particle count / charge method / setup cache) is REPORTED rather than refused, because an
UNRECORDED field is not the same as a disagreeing one — but a genuine disagreement is flagged loudly.

Stdlib only. Runs on a free CI runner inside the parity image (the reduction itself reads finished leg JSONs,
but running it beside `ternary_fep_reduce` in the same container keeps one environment for the whole analysis).
"""
from __future__ import annotations

import glob
import json
import math
import os

import valb_triangle_closure as tri
import valb_triangle_legs as tlegs

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "valb-triangle-reduction.json")

# The six legs, and which edge/environment each is. `valb_triangle_legs.TRIANGLE_LEGS` is the one home for
# this mapping; restating it here would let the launcher and the reducer disagree about what T3 even is.
EDGE_COEFF = {e: v["coefficient"] for e, v in tlegs.TRIANGLE_LEGS.items()}
LEG_ROLE = {v[env]: (e, env) for e, v in tlegs.TRIANGLE_LEGS.items() for env in ("ternary", "binary")}


def _is_restrained(rec, path):
    """Did this leg run with the flat-bottom pocket restraint?

    ⛔ WHY THIS EXISTS, AND WHY IT IS A REFUSAL RATHER THAN A FILTER. A separate lane is concurrently running
    a RESTRAINED binary re-run of this same calibrator, for a different purpose, and its results land in the
    SAME GCS bucket as r0's. The GCP lane already keeps them apart by filename — `leg_<id>_<dir>_r<seed>_rst
    .json` — precisely so a restrained arm is never folded into an unrestrained cycle by default. But a
    reducer that globs a directory has no filename discipline of its own, and one restrained leg inside this
    triangle would make R measure the PROTOCOL DIFFERENCE between the two lanes rather than the path error,
    which is the single failure this entire rung is built to avoid. It would also look completely normal.

    Checked two ways because either alone can miss: the `_rst` filename marker the producing lane writes, and
    any restraint field the engine records. Belt and braces on a contamination that is silent by nature.
    """
    base = os.path.basename(path)
    if "_rst" in base:
        return True
    for k in ("restrain", "restraint", "rbfe_restrain", "pocket_restraint"):
        v = rec.get(k)
        if v not in (None, False, 0, "0", "", "none"):
            return True
    return False


def _load_legs(directory):
    """Every engine leg JSON in `directory`, keyed by leg_id. Later files do NOT overwrite earlier ones
    silently — a duplicate leg_id is collected and reported, because two records for one leg means two
    different runs and picking either without saying so is how a cycle gets built from mixed provenance."""
    found, dupes, restrained = {}, [], []
    for path in sorted(glob.glob(os.path.join(directory, "leg_*.json"))):
        try:
            with open(path) as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        lid = d.get("leg_id")
        if not lid:
            continue
        if _is_restrained(d, path):
            restrained.append(os.path.basename(path))
            continue
        if lid in found:
            dupes.append({"leg_id": lid, "paths": [found[lid]["_path"], path]})
            continue
        d["_path"] = path
        found[lid] = d
    return found, dupes, restrained


def _sd(vals):
    """Sample SD. Returns None for n<2 — which is the honest answer at n=1 and must never be replaced by an
    MBAR SE to make a table look complete."""
    v = [float(x) for x in vals if x is not None]
    if len(v) < 2:
        return None
    m = sum(v) / len(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def _measured_sigma_addendum(closures, R, mbar, sig_lo, sig_hi):
    """The 2026-07-30 addendum: what R reads against a MEASURED sigma_leg bound, and what it licenses about
    the parked RUNG 5a-KS resume.

    ★ WHY THIS IS AN ADDENDUM AND NOT AN EDIT TO THE VERDICT ABOVE. Narrowing the upper sigma_leg bound from
    the assumed 0.7 to the measured value shrinks the AMBIGUOUS band by a factor of ~3, which makes
    `R_RESOLVED_PATH_ERROR` EASIER to reach -- and that is the branch under which r0's miss is *fixable*, i.e.
    the hopeful one. A change that is free to make and that happens to favour the outcome we want is exactly
    the change that must not be made silently to a frozen decision rule. So: the frozen `decision` above is
    computed at the ORIGINAL bounds and is untouched, this block reports the measured reading beside it, and
    which one to act on is STRATEGY Open decision 7 -- a human call, not one taken by whoever runs the reducer.

    ★ AND IT IS WRITTEN BEFORE ANY R EXISTS. Every threshold here is derived from the valB n=3 replicates and
    the design's own power curve; none of it can be tuned to the number this function is about to be handed."""
    import valb_failure_propagation as FP    # local: FP imports valb_triangle_closure, so no cycle at module load

    bound = FP.sigma_leg_now_bounded()
    hi_measured = bound["sigma_leg_upper_bound_kcal"]
    crossing = FP.power_threshold_crossing()

    # sigma_leg estimated from the TRIANGLE's own legs -- no homology-model term, no cross-seed solvation term
    ses = [x for x in mbar if x is not None]
    own = (sum(ses) / len(ses)) if ses else None
    narrowed = FP.narrow_sigma_leg_from_triangle_legs(own)

    thresh_measured = 1.96 * math.sqrt(6.0) * hi_measured
    thresh_lo = 1.96 * math.sqrt(6.0) * sig_lo
    if abs(R) <= thresh_lo:
        dec = "R_CONSISTENT_WITH_ZERO"
    elif abs(R) > thresh_measured:
        dec = "R_RESOLVED_PATH_ERROR"
    else:
        dec = "AMBIGUOUS_AT_n1"

    return {
        "_what": "reading at the MEASURED sigma_leg bound; the frozen decision above is untouched",
        "_registered": "2026-07-30, before any triangle R existed",
        "sigma_leg_upper_bound_measured": hi_measured,
        "sigma_leg_upper_bound_superseded_assumption": sig_hi,
        "ambiguous_band_frozen": [round(thresh_lo, 4), round(1.96 * math.sqrt(6.0) * sig_hi, 4)],
        "ambiguous_band_at_measured_bound": [round(thresh_lo, 4), round(thresh_measured, 4)],
        "decision_at_measured_bound": dec,
        "sigma_leg_from_the_triangles_own_legs": narrowed,
        "power_0.80_crosses_at_sigma_leg": round(crossing, 4),
        "5aKS_resume_verdict": FP.s_resolvability_from_R_ternary(
            R_ternary=closures["R_ternary"], sigma_leg=hi_measured),
        "_5aKS_note": ("S is a two-leg difference inside the TERNARY environment, so R_ternary -- not R_coop "
                       "-- is what bounds its non-conservative error. A large R_ternary buys a hold and a "
                       "second draw, never a kill. An ADMIT bounds the non-conservative class ONLY; closure "
                       "is blind to per-endpoint state functions, so it cannot certify S."),
        "_do_not_conflate": ("`decision_at_measured_bound` is NOT the lane's verdict. The lane's verdict is "
                             "`decision`, computed at the original bounds. If the two differ, that difference "
                             "IS the content of STRATEGY Open decision 7 and should be surfaced, not resolved "
                             "here."),
    }


def reduce_triangle(directory, sigma_leg=None):
    """Compute R, R_ternary, R_binary and the prereg verdict from the leg JSONs in `directory`."""
    legs, dupes, restrained = _load_legs(directory)
    report = {
        "_what": "the valB synthetic closure triangle's residual R and its two component closures",
        "_identity": "R = ddG_coop(T1) + ddG_coop(T2) - ddG_coop(T3) = R_ternary - R_binary. Zero for an "
                     "exact method, and IDENTICALLY zero for any endpoint-STATE error (force field, "
                     "SMARCA4->SMARCA2 homology, NAGL charges, protonation) — so a non-zero R is PATH error "
                     "and nothing else.",
        "directory": directory,
        "legs_found": sorted(legs),
        "duplicate_leg_records": dupes,
        "restrained_records_excluded": restrained,
    }

    # ---- completeness ------------------------------------------------------------------------------------
    wanted = sorted(LEG_ROLE)
    missing = [l for l in wanted if l not in legs]
    solvent = [l for l in legs if l.endswith("__solvent")]
    if missing:
        report.update({"decision": "INCOMPLETE",
                       "reason": "missing leg record(s): %s. Five legs cannot close a triangle — an R from a "
                                 "partial cycle is not a smaller-n R, it is a different number." % missing})
        return report
    if solvent:
        report.update({"decision": "REFUSED",
                       "reason": "solvent leg(s) present (%s). The solvent morph cancels EXACTLY inside "
                                 "ddG_coop = ternary - binary, so including one adds noise at best and "
                                 "computes a different quantity at worst." % solvent})
        return report
    if restrained:
        # NOT a silent skip. A restrained record reaching this directory means the two lanes' artifacts have
        # been mixed somewhere upstream, and the next thing to be mixed might be one this filter cannot name.
        report.update({"decision": "REFUSED",
                       "reason": "restrained leg record(s) present (%s). The triangle's binary legs run "
                                 "UNRESTRAINED to match r0 — mixing a restrained arm in would make R measure "
                                 "the PROTOCOL DIFFERENCE between two lanes rather than the path error, which "
                                 "is the one failure this rung exists to avoid. They are DIFFERENT "
                                 "experiments; find out how these got into one directory before re-running."
                                 % restrained})
        return report
    if dupes:
        report.update({"decision": "REFUSED",
                       "reason": "two records for the same leg id (%s) — two different runs, and choosing "
                                 "either silently would build the cycle from mixed provenance."
                                 % [d["leg_id"] for d in dupes]})
        return report

    use = {l: legs[l] for l in wanted}

    # ---- comparability, the checks that decide whether R means what it says ------------------------------
    def _spread(field):
        return sorted({json.dumps(d.get(field), sort_keys=True) for d in use.values()})

    seeds = _spread("seed")
    hashes = _spread("protocol_hash")
    directions = _spread("direction")
    comparability = {
        "seed": seeds, "protocol_hash": hashes, "direction": directions,
        "n_particles": _spread("n_particles"), "charge_method": _spread("charge_method"),
        "setup_cache_version": _spread("setup_cache_version"),
        "n_windows": _spread("n_windows"),
    }
    report["comparability"] = comparability
    if len(seeds) != 1:
        report.update({"decision": "REFUSED",
                       "reason": "the six legs do not share one seed (%s). Ternary seed s selects the s%%n-th "
                                 "relaxed SMARCA2 model, so a mixed-seed triangle is computed on DIFFERENT "
                                 "Hamiltonians: the edges stop sharing endpoint states, the telescoping that "
                                 "makes R a closure residual fails, and |R| becomes a homology-model "
                                 "sensitivity measure instead." % seeds})
        return report
    if len(directions) != 1:
        report.update({"decision": "REFUSED",
                       "reason": "mixed leg directions (%s). The triangle is a FORWARD 3-cycle; a reverse leg "
                                 "belongs to the 2-cycle antisymmetry check, which is a different "
                                 "instrument." % directions})
        return report
    if len(hashes) != 1:
        # NOT fatal by itself: r0 predates some protocol-record fields, so a hash difference can be a
        # bookkeeping change rather than a physics one. It IS the single most likely way the triangle gets
        # silently invalidated, so it is surfaced at the top of the report rather than buried.
        report["protocol_hash_disagreement"] = (
            "the six legs do not share one protocol_hash. R is only a closure residual if every edge ran the "
            "SAME protocol — this is exactly why T2/T3's binary legs run UNRESTRAINED to match r0, and why "
            "the triangle is pinned to 2 fs. Inspect the settings diff before quoting R.")

    # ---- the arithmetic ----------------------------------------------------------------------------------
    dg = {}
    for lid, d in use.items():
        edge, env = LEG_ROLE[lid]
        v = d.get("dg_morph_kcal")
        if v is None:
            report.update({"decision": "INCOMPLETE",
                           "reason": "leg %s carries no dg_morph_kcal — it did not finish" % lid})
            return report
        dg.setdefault(env, {})[edge] = float(v)

    ddg_coop = {e: dg["ternary"][e] - dg["binary"][e] for e in EDGE_COEFF}
    closures = tri.closure_decomposition({"ternary": dg["ternary"], "binary": dg["binary"]})
    R = closures["R_coop"]

    # ---- how big does |R| have to be to mean anything -----------------------------------------------------
    # sigma_leg was NOT measured on this lane when these bounds were frozen (it is now -- see the addendum
    # below, which is reported separately rather than folded in here). Both bounds are carried explicitly so
    # no single threshold can
    # be mistaken for a measured one.
    mbar = [d.get("mbar_se_kcal") for d in use.values()]
    sig_lo, sig_hi = 0.045, 0.7
    sigma = float(sigma_leg) if sigma_leg is not None else sig_lo
    floor = tri.closure_noise_floor(sigma_leg_values=(sig_lo, sig_hi))
    prereg = tri.binary_departure_prereg(R_ternary=closures["R_ternary"], R_binary=closures["R_binary"],
                                         sigma_leg=sigma)

    report.update({
        "dg_morph_kcal_by_env_and_edge": dg,
        "ddG_coop_by_edge_kcal": {e: round(v, 4) for e, v in ddg_coop.items()},
        "edge_coefficients": EDGE_COEFF,
        "R_ternary_kcal": round(closures["R_ternary"], 4),
        "R_binary_kcal": round(closures["R_binary"], 4),
        "R_kcal": round(R, 4),
        "cancellation_risk": closures.get("cancellation_risk"),
        "cancellation_note": closures["_rule"],
        "error_bar_kind": "NONE QUOTED AT n=1",
        "error_bar_basis": (
            "This programme's error bar is the BETWEEN-REPLICATE SD, never the MBAR SE. The triangle is an "
            "n=1 scout — one seed on every edge, which the design REQUIRES (a mixed-seed triangle is not a "
            "closure) — so no replicate SD exists and none is invented. The per-leg MBAR SEs are recorded "
            "below as provenance only; they are a LOWER bound on sigma_leg and must never be presented as "
            "the uncertainty on R."),
        "mbar_se_kcal_per_leg_PROVENANCE_ONLY": {l: use[l].get("mbar_se_kcal") for l in wanted},
        "replicate_sd_kcal": _sd([]),      # explicitly None at n=1, so the field exists and is honest
        "noise_floor": floor,
        "sigma_leg_bounds": {"lower_MBAR_SE": sig_lo, "upper_repo_assumed_replicate_SD": sig_hi,
                             "used_for_the_verdict": sigma,
                             "note": "the clause that stood here -- 'nothing has measured the value in "
                                     "between' -- was true until 2026-07-30 and is now SUPERSEDED: the "
                                     "valB_mini n=3 replicates bound sigma_leg ABOVE, well below 0.7. The "
                                     "frozen verdict below is deliberately still reported at BOTH ORIGINAL "
                                     "bounds; the measured reading is carried separately in "
                                     "`measured_sigma_addendum` so nothing preregistered moves."},
        "prereg_verdict": prereg,
        "prereg_verdict_at_upper_sigma": tri.binary_departure_prereg(
            R_ternary=closures["R_ternary"], R_binary=closures["R_binary"], sigma_leg=sig_hi),
        "measured_sigma_addendum": _measured_sigma_addendum(closures, R, mbar, sig_lo, sig_hi),
    })

    # ---- the plain-language reading, which is the actual deliverable --------------------------------------
    thresh_lo = 1.96 * math.sqrt(6.0) * sig_lo
    thresh_hi = 1.96 * math.sqrt(6.0) * sig_hi
    if abs(R) <= thresh_lo:
        decision, reading = "R_CONSISTENT_WITH_ZERO", (
            "|R| = %.4f kcal/mol is within the tightest plausible noise floor (%.3f, at sigma_leg = %.3f). "
            "A small |R| is STRONG evidence, because it bounds the path error and the noise simultaneously — "
            "both would have to be small. READING: this workflow's ddG_coop cycle is internally "
            "self-consistent to within |R| of PATH error, so r0's 1.478 kcal/mol miss is NOT explained by "
            "path error and MORE SAMPLING WILL NOT FIX IT. The miss lives in the model or the reference "
            "data, where closure is provably blind, and the known-answer accuracy requirement stays OPEN."
            % (abs(R), thresh_lo, sig_lo))
    elif abs(R) > thresh_hi:
        decision, reading = "R_RESOLVED_PATH_ERROR", (
            "|R| = %.4f kcal/mol exceeds the noise floor even at the pessimistic sigma_leg = %.3f (%.3f). "
            "READING: there IS a path error of this size in the workflow, and it is the class a closure "
            "detects and a reverse leg partly cannot. r0's miss is at least partly fixable by sampling or "
            "protocol work. Read R_ternary (%.4f) and R_binary (%.4f) SEPARATELY before attributing it."
            % (abs(R), sig_hi, thresh_hi, closures["R_ternary"], closures["R_binary"]))
    else:
        decision, reading = "AMBIGUOUS_AT_n1", (
            "|R| = %.4f kcal/mol falls between the optimistic (%.3f) and pessimistic (%.3f) noise floors, "
            "and sigma_leg is unmeasured on this lane. READING: the n=1 scout can ADMIT a cycle but cannot "
            "CONVICT it — one draw cannot separate a systematic path error from an unlucky sample. This is "
            "reported as UNDERPOWERED, not as evidence either way, and it must not be quoted as support for "
            "either branch." % (abs(R), thresh_lo, thresh_hi))
    report["decision"] = decision
    report["reading"] = reading
    report["honest_limit"] = (
        "Closure measures INTERNAL CONSISTENCY, not accuracy, and specifically cannot see force-field error, "
        "the SMARCA4->SMARCA2 homology substitution, NAGL charge error, protonation assignment, or the fact "
        "that alpha_SPR is an APPARENT cooperativity — every one of those is a per-endpoint state function "
        "and telescopes out of any cycle. No accuracy claim may be made from this number.")
    return report


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Reduce the valB closure triangle's six legs to R.")
    ap.add_argument("--legs", required=True, help="directory of engine leg_*.json records")
    ap.add_argument("--sigma-leg", type=float, default=None,
                    help="sigma_leg for the prereg verdict (default: the MBAR-SE lower bound 0.045; the "
                         "report always ALSO carries the verdict at the 0.7 upper bound)")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    rep = reduce_triangle(a.legs, sigma_leg=a.sigma_leg)
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=2)
        fh.write("\n")
    print(json.dumps(rep, indent=2))
    print("[triangle-reduce] wrote %s" % a.out)
    print("[triangle-reduce] decision=%s" % rep.get("decision"))
    return 0 if rep.get("decision") not in ("REFUSED", "INCOMPLETE") else 1


if __name__ == "__main__":
    raise SystemExit(main())
