#!/usr/bin/env python3
"""ENDPOINT-MD SENSITIVITY CONTROL — the FROZEN scorer.

One function decides the control: `verdict(legs)`. It applies `selcal_panel.PASS_CRITERION`, which was frozen
before the first GPU leg, and it is PURE — same legs in, same tier out, no clock, no network, no thresholds of
its own.

⛔ NOTHING STATISTICAL IS RE-IMPLEMENTED HERE (CLAUDE.md rule 1). The collapse to model means, the exact
permutation enumeration and the leave-one-model-out refit all come from `nrv04_retro_gate` — the SAME frozen
scorer that produced the NR-V04 verdict this control exists to interpret. That is not merely tidiness: a
sensitivity control scored by a second implementation would be calibrating a statistic the program does not
use, and any disagreement between the two would be undetectable.

★ WHAT THIS MODULE ADDS, and why each piece is here rather than in the shared scorer:
  * the DIRECTION commitment (`ALTERNATIVE = "less"`) and the WRONG_SIGN tier, which only make sense when a
    primary source predicts a direction — NR-V04's pairwise contrasts had no such prediction;
  * the reference-set adequacy clause, which is this design's answer to the finding that killed the NR-V04
    pairwise: a floor of 0.10 against alpha 0.05 makes a comparison a NON-MEASUREMENT, so this panel checks
    that its own floor still clears alpha AFTER any exclusion, and refuses to score if it does not;
  * `design_floor()`, so the 0.00108 quoted in the panel and the prereg is DERIVED at read time rather than
    typed in three places.
"""
from __future__ import annotations

import json
import os
import sys
from math import comb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import selcal_panel as P  # noqa: E402


# =============================================================================================================
# design properties — derived, never typed
# =============================================================================================================
def design_floor(n_a: int = None, n_b: int = None) -> dict:
    """The minimum attainable one-sided p for this design, and whether it can reach alpha.

    A property of the DESIGN, true whatever the data say: an exact permutation test over C(n_a+n_b, n_a)
    arrangements cannot return a p below 1/C. The NR-V04 NR4A1-vs-NR4A3 pairwise had C = 10, floor 0.10, so
    its power against ANY separation was zero — the finding that reframed the whole options paper. This panel
    is shaped so that cannot happen, and the check is executable rather than asserted."""
    a = len(P.COFOLD_MODEL_SEEDS) if n_a is None else int(n_a)
    b = len(P.COFOLD_MODEL_SEEDS) if n_b is None else int(n_b)
    n = comb(a + b, a)
    floor = 1.0 / n
    return {"models_arm_a": a, "models_arm_b": b, "n_arrangements": n,
            "min_attainable_p": floor, "alpha": P.ALPHA, "can_reach_alpha": floor <= P.ALPHA}


# =============================================================================================================
# leg records -> the shape the shared scorer eats
# =============================================================================================================
def leg_rows(legs):
    """Turn raw `leg_*.json` records into the {arm_id, cofold_model_seed, e1_plateau_A, technical_failure}
    rows `nrv04_retro_gate.model_level_values` consumes.

    ⛔ MEMBERSHIP IS DECIDED HERE, AND ON PROVENANCE RATHER THAN ON PRESENCE. A record whose `mode` is not
    `run`, or whose sampling lengths are not the preregistered ones, is NOT a leg of this panel — it is an
    artifact that exists and is reported and is not scored. This is the predicate that stopped a frozen gate
    emitting a fabricated verdict on 17 smoke legs that had echoed `prod_ns: 5.0` and a fully-populated
    `R1_interface` from their ENV (CLAUDE.md §4: a populated field is not a measured one). A leg that ran the
    right protocol and then BLEW UP is a different thing — it stays in the panel as a technical failure,
    because the criterion scores that.

    Returns (rows, rejected) where `rejected` carries the reason for every record not admitted."""
    rows, rejected = [], []
    for rec in legs:
        ok, why = P.production_leg_check(rec)
        leg_id = (rec or {}).get("leg_id") if isinstance(rec, dict) else None
        if not ok:
            rejected.append({"leg_id": leg_id, "why": why, "admitted": False})
            continue
        arm_id, _, mtag = str(leg_id or "").partition("__m")
        if arm_id not in {a.arm_id for a in P.ARMS} or not mtag.isdigit():
            rejected.append({"leg_id": leg_id, "admitted": False,
                             "why": "leg_id does not name an arm of this panel (expected "
                                    "'<arm_id>__m<seed>'); scoring it would attribute a leg to the wrong arm"})
            continue
        model = int(mtag)
        excluded, ex_why = P.excluded_cofold(arm_id, model)
        if excluded:
            rejected.append({"leg_id": leg_id, "admitted": False, "why": "EXCLUDED co-fold: %s" % ex_why})
            continue
        done, done_why = P.completed_production_check(rec)
        e1 = ((rec.get("R1_interface") or {}).get("plateau_A")) if done else None
        rows.append({"arm_id": arm_id, "cofold_model_seed": model, "seed": rec.get("seed"),
                     "e1_plateau_A": e1, "technical_failure": (not done),
                     "why": done_why, "leg_id": leg_id})
    return rows, rejected


# =============================================================================================================
# the verdict
# =============================================================================================================
#: ★★ WHAT EACH TIER DOES TO THE PROGRAMME — travelling WITH the verdict, not left in a design doc.
#: The branch was written in advance in `selectivity-resolution-options.md` §3/§4, before this panel ran, and
#: that is what makes it quotable. But the artifact a reader actually opens at 3 AM is `selcal-verdict.json`,
#: and until now it carried the CRITERION without carrying the CONSEQUENCE — so the one question anybody asks
#: on seeing a tier ("what happens now?") was answerable only by finding another file.
#:
#: ⚠ IT POINTS, IT DOES NOT RESTATE (CLAUDE.md §1). No leg count and no dollar figure is typed here: step 3's
#: shape and price have ONE home, `selectivity_resolution_options.recommended_sequence`, which DERIVES them.
#: A number copied into a verdict artifact is a number that goes stale silently and then gets quoted.
NEXT_STEP_BY_TIER = {
    P.TIER_PASS: {
        "unblocks": "step 3 of selectivity-resolution-options.md §3 — re-panel NR4A1/2/3 on the validated "
                    "design. Shape and cost are DERIVED by "
                    "`selectivity_resolution_options.recommended_sequence`; do not quote them from here.",
        "blocking_artifact": "A NEW PREREGISTRATION, written before any step-3 leg is bought. It is NOT a "
                             "§4d extension of the NR-V04 prereg — §4d may not be invoked on a wrong-sign "
                             "result — and any re-use of the 16 landed NR-V04 legs must be declared inside "
                             "it, in advance.",
        "still_forbidden": "Everything in `_what_a_pass_licenses`. A pass re-scores no landed NR-V04 leg and "
                           "licenses no NR4A3, degradation, efficacy or therapeutic claim.",
    },
    P.TIER_NULL: {
        "unblocks": "NOTHING. Step 3 is NOT bought — it would be money spent to reproduce a failure.",
        "blocking_artifact": None,
        "reporting": "The paper reports NR4A3 selectivity as UNVALIDATED PREDICTIONS, in the sentence "
                     "written in advance at selectivity-resolution-options.md §4 so it cannot later be "
                     "re-narrated as a method failure.",
    },
    P.TIER_WRONG_SIGN: {
        "unblocks": "NOTHING, and this is a FAIL of the control reported WITH THE SIGN STATED — a readout "
                    "that separates a known pair backwards is worse than one that cannot separate it.",
        "blocking_artifact": None,
        "reporting": "As TIER_NULL's sentence, plus the sign. ⛔ prereg §4d may not be invoked on a "
                     "wrong-sign result.",
    },
    P.TIER_INDETERMINATE: {
        "unblocks": "NOTHING, and it is NOT a null — nothing was measured. It must not be reported as a "
                    "negative result, and it does not license the §4 sentence either.",
        "blocking_artifact": "Whatever made the panel unscoreable: technical failures beyond the allowance, "
                             "or too few conforming co-fold models. Fixing that is a re-run, not a re-read.",
    },
}

#: ⚠ NEITHER A PASS NOR A FAIL DISTINGUISHES 'the readout is blunt' FROM 'this pair is hard'. Written here
#: because it is the misreading a tier invites, and `_what_a_fail_licenses` says it about the fail only.
TIER_CANNOT_DISTINGUISH = ("A fail does NOT distinguish 'the readout is blunt' from 'this pair is hard', and "
                           "must not be reported as though it did.")


def next_step_for(tier):
    """What this tier unblocks, forecloses, and still forbids. PURE. Points at the derivation; types nothing."""
    row = dict(NEXT_STEP_BY_TIER.get(tier) or {})
    row["_source"] = "selectivity-resolution-options.md §3 (the sequence) and §4 (the alternative outcome)"
    row["_written_before_the_panel_ran"] = True
    if tier != P.TIER_PASS:
        row["cannot_distinguish"] = TIER_CANNOT_DISTINGUISH
    return row


def suppress_for_incomplete_panel(v: dict, why: str) -> dict:
    """Withhold the LABEL and everything that discloses it. ONE HOME, because they must move together.

    ⛔ THE DEFECT THIS CLOSES, and it was introduced by the very field it now governs (2026-08-02). Adding
    `next_step` to the verdict meant an INCOMPLETE panel published `tier: None` — correctly suppressed — beside
    `next_step.unblocks = "NOTHING. Step 3 is NOT bought…"`, which is the NULL tier's consequence stated in
    prose. Suppression exists to withhold the label on a partial panel; a field that re-publishes the label's
    MEANING defeats it exactly, and is worse than a leaked label because it reads as a decision rather than a
    peek. Measured on the live lane at 21 of 24 legs.

    So suppression is atomic here rather than a sequence of pops at the call site: a future field that
    discloses the tier has one place to be added, and the test that pins this has one place to look.
    """
    v["tier_suppressed"] = v.pop("tier", None)
    v["tier"] = None
    # The consequence is the label by another name. Withheld with it, and SAYING it is withheld — an absent
    # field would read as "this tier unblocks nothing", which is itself a disclosure.
    v["next_step_suppressed"] = v.pop("next_step", None) is not None
    v["next_step"] = {
        "unblocks": "WITHHELD — the panel is incomplete, so no tier is reported and no consequence follows "
                    "from one. This is not 'nothing is unblocked'; it is 'the question has not been asked "
                    "yet'.",
        "_source": "selcal_gate.suppress_for_incomplete_panel",
    }
    v["suppression"] = why
    return v


def _with_next_step(out: dict) -> dict:
    """Attach the tier's consequence. Called on EVERY exit of `verdict`, because a field present on some
    paths and absent on others is worse than absent everywhere — a reader cannot tell which they have."""
    out["next_step"] = next_step_for(out.get("tier"))
    return out


def verdict(legs) -> dict:
    """Apply the frozen criterion to a set of leg records. PURE.

    Returns the full evidence dict — statistic, p, both one-sided tests, the LOMO refits, the failure census
    and the design floor — never just the label. A tier without its evidence is not reportable, and this one
    in particular will be quoted."""
    from nrv04_retro_gate import exact_permutation_p, leave_one_model_out, mean_difference, model_level_values

    rows, rejected = leg_rows(legs)
    means, failures = model_level_values(rows)
    n_a = len(means.get(P.ARM_A, {}))
    n_b = len(means.get(P.ARM_B, {}))
    floor = design_floor(n_a or 1, n_b or 1)

    out = {
        "_what": "ENDPOINT-MD SENSITIVITY CONTROL — an INSTRUMENT CALIBRATION. It asks whether the E1 readout "
                 "detects a paralogue difference a primary source says is there. It is NOT a selectivity "
                 "result and licenses no claim about NR4A3, degradation, efficacy or any therapeutic window.",
        "_criterion_was_frozen_before_the_run": P.PASS_CRITERION["_frozen_before_any_gpu_leg"],
        "panel": "selcal_sensitivity_control",
        "reference": {k: P.REFERENCE[k] for k in ("ligand", "ligand_ccd", "pair", "citation",
                                                  "selectivity_quote", "magnitude_not_quotable",
                                                  "pair_mechanism_quote", "deposited_ternaries")},
        "criterion": P.PASS_CRITERION,
        "models_per_arm": {P.ARM_A: n_a, P.ARM_B: n_b},
        "model_means_A": {str(k): round(v, 4) for k, v in sorted((means.get(P.ARM_A) or {}).items())},
        "model_means_A_arm": P.ARM_A,
        "model_means_B": {str(k): round(v, 4) for k, v in sorted((means.get(P.ARM_B) or {}).items())},
        "model_means_B_arm": P.ARM_B,
        "technical_failures": failures,
        "n_legs_admitted": len(rows),
        "rejected_records": rejected,
        "design_floor": floor,
    }

    # ---- admissibility, BEFORE any statistic is computed -------------------------------------------------
    underpowered = sorted(a for a, n in failures.items() if n > P.MAX_FAILED_LEGS_PER_ARM)
    short = [a for a, n in ((P.ARM_A, n_a), (P.ARM_B, n_b)) if n < P.MIN_MODELS_PER_ARM]
    if underpowered or short:
        out.update({
            "tier": P.TIER_INDETERMINATE, "p": None, "statistic": None,
            "reason": ("INDETERMINATE — nothing was measured, and this is NOT a null. "
                       + ("arm(s) %s exceeded the %d-technical-failure allowance. "
                          % (underpowered, P.MAX_FAILED_LEGS_PER_ARM) if underpowered else "")
                       + ("arm(s) %s have fewer than %d conforming co-fold models, so the reference set can "
                          "no longer reach alpha and the comparison would be a NON-MEASUREMENT — the exact "
                          "defect that made the NR-V04 NR4A1-vs-NR4A3 pairwise uninterpretable."
                          % (short, P.MIN_MODELS_PER_ARM) if short else "")).strip(),
            "underpowered_arms": underpowered, "arms_short_of_models": short})
        return _with_next_step(out)
    if not floor["can_reach_alpha"]:
        out.update({"tier": P.TIER_INDETERMINATE, "p": None, "statistic": None,
                    "reason": "INDETERMINATE — the reference set's floor (%.5f) exceeds alpha (%.2f), so the "
                              "test has zero power against ANY separation. It cannot reject and it cannot be "
                              "trusted to fail to reject." % (floor["min_attainable_p"], P.ALPHA)})
        return _with_next_step(out)

    # ---- the statistic ------------------------------------------------------------------------------------
    a_vals = [means[P.ARM_A][m] for m in sorted(means[P.ARM_A])]
    b_vals = [means[P.ARM_B][m] for m in sorted(means[P.ARM_B])]
    stat = mean_difference(a_vals, b_vals)
    less = exact_permutation_p(a_vals, b_vals, alternative="less")
    greater = exact_permutation_p(a_vals, b_vals, alternative="greater")
    primary = less if P.ALTERNATIVE == "less" else greater
    mirror = greater if P.ALTERNATIVE == "less" else less

    # LOMO on THIS panel's two arms. `leave_one_model_out` takes (primary, pooled) and computes
    # mean(primary) - mean(pooled), which for a two-arm design is exactly our statistic.
    lomo = leave_one_model_out(means, primary=P.ARM_A, pooled=(P.ARM_B,))

    out.update({
        "statistic": round(stat, 4),
        "statistic_definition": P.STATISTIC,
        "p": round(primary["p"], 6), "p_alternative": P.ALTERNATIVE,
        "p_mirror": round(mirror["p"], 6),
        "n_arrangements": primary["n_arrangements"],
        "min_attainable_p": round(primary["min_attainable_p"], 6),
        "leave_one_model_out": lomo,
        "mean_A": round(sum(a_vals) / len(a_vals), 4), "mean_B": round(sum(b_vals) / len(b_vals), 4),
    })

    # ---- the tiers, in the order the criterion states them -----------------------------------------------
    if primary["p"] <= P.ALPHA and stat < 0 and lomo["survives"]:
        out.update({"tier": P.TIER_PASS,
                    "reason": "PASS — p = %.4f <= alpha = %.2f in the PREDICTED direction (%s mean E1 is "
                              "%.3f A lower, i.e. the more stable ternary interface), and the sign survives "
                              "every leave-one-model-out refit. The readout detected a paralogue difference "
                              "the primary source says is there."
                              % (primary["p"], P.ALPHA, P.ARM_A, -stat),
                    "licenses": P.PASS_CRITERION["_what_a_pass_licenses"]})
    elif primary["p"] <= P.ALPHA and stat < 0 and not lomo["survives"]:
        # ⚠ NOT A PASS, AND NOT A SILENT ONE EITHER. A significant p whose sign flips when one co-fold model
        # is dropped is a result carried by a single model; the criterion lists LOMO survival as a required
        # AND-clause precisely so this cannot be reported as a detection.
        out.update({"tier": P.TIER_NULL,
                    "reason": "NOT A PASS — p = %.4f clears alpha in the predicted direction, but the sign "
                              "does NOT survive leave-one-model-out, so the result is carried by a single "
                              "co-fold model. The criterion requires LOMO survival as an AND-clause and it "
                              "was written before the run." % primary["p"],
                    "licenses": P.PASS_CRITERION["_what_a_fail_licenses"]})
    elif mirror["p"] <= P.ALPHA and stat > 0:
        out.update({"tier": P.TIER_WRONG_SIGN,
                    "reason": "WRONG SIGN — the separation is significant (p = %.4f) in the direction the "
                              "primary source CONTRADICTS: %s is the LESS stable arm here, while the "
                              "reference reports it as the preferred one. A readout that separates a known "
                              "pair backwards is worse than one that cannot separate it."
                              % (mirror["p"], P.ARM_A),
                    "licenses": P.PASS_CRITERION["_what_a_fail_licenses"]})
    else:
        out.update({"tier": P.TIER_NULL,
                    "reason": "NULL — an adequately-powered design (reference set of %d, floor %.5f, well "
                              "under alpha) did not detect the difference: p = %.4f. This is a REAL negative "
                              "and is reported as one."
                              % (primary["n_arrangements"], primary["min_attainable_p"], primary["p"]),
                    "licenses": P.PASS_CRITERION["_what_a_fail_licenses"]})
    return _with_next_step(out)


def render(v: dict) -> str:
    """The verdict as a few lines a human can read at 3 AM without opening the JSON."""
    lines = ["ENDPOINT-MD SENSITIVITY CONTROL — %s" % v.get("tier"),
             "  instrument calibration, NOT a selectivity result",
             "  reference: %s, %s vs %s (%s)" % (v["reference"]["ligand"], v["reference"]["pair"][0],
                                                 v["reference"]["pair"][1],
                                                 v["reference"]["citation"]["doi"]),
             "  models/arm: %s" % v.get("models_per_arm"),
             "  statistic:  %s" % v.get("statistic"),
             "  p:          %s (%s, %d arrangements, floor %s)"
             % (v.get("p"), v.get("p_alternative"), v.get("n_arrangements") or 0, v.get("min_attainable_p")),
             "  LOMO:       %s" % ((v.get("leave_one_model_out") or {}).get("survives")),
             "  %s" % v.get("reason")]
    # ⚠ THE CONSEQUENCE, NOT JUST THE LABEL. "PASS" on its own does not tell the reader whether anything may
    # now be bought; that branch was written before the panel ran and belongs beside the tier.
    nxt = v.get("next_step") or {}
    if nxt.get("unblocks"):
        lines.append("  NEXT:       %s" % nxt["unblocks"])
    if nxt.get("blocking_artifact"):
        lines.append("  BLOCKED ON: %s" % nxt["blocking_artifact"])
    if nxt.get("reporting"):
        lines.append("  REPORT AS:  %s" % nxt["reporting"])
    return "\n".join(lines)


def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Score the sensitivity control from leg JSONs (pure, $0).")
    ap.add_argument("legs", nargs="*", help="paths to leg_*.json")
    ap.add_argument("--design", action="store_true", help="print the design floor and exit")
    args = ap.parse_args(argv)
    if args.design or not args.legs:
        print(json.dumps({"design_floor": design_floor(), "criterion": P.PASS_CRITERION}, indent=2))
        return 0
    recs = []
    for p in args.legs:
        with open(p) as fh:
            recs.append(json.load(fh))
    v = verdict(recs)
    print(render(v))
    print(json.dumps(v, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
