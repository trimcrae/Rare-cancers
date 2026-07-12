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


def _diff(mean_a, ci_a, mean_b, ci_b):
    """(mean_a − mean_b) with quadrature-combined CI half-width (independent replicate errors)."""
    if mean_a is None or mean_b is None:
        return None, None
    est = mean_a - mean_b
    if ci_a is None or ci_b is None:
        return est, None
    return est, math.sqrt(ci_a ** 2 + ci_b ** 2)


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
    report = {
        "_what": "ternary-cooperativity pilot reduction (binary-vs-ternary cycle, replicate-SD errors)",
        "_honesty": "no measured alpha/dG asserted; values appear only when real GPU legs have checkpointed. "
                    "gpu_h/cost/ff-lock are execution provenance attached by the run harness, not here.",
        "morph_summaries": summaries,
        "leg_output_records": leg_records,
        "nrv04_affinity_controls": nrv04_controls,
        "n_available_morphs": sum(1 for s in summaries if s.get("available")),
    }
    out = os.path.join(CKPT, "ternary_coop_reduction.json")
    json.dump(report, open(out, "w"), indent=2)
    print("[tfep-reduce] wrote %s (%d/%d morphs available)"
          % (out, report["n_available_morphs"], len(summaries)), flush=True)
    return report


if __name__ == "__main__":
    reduce_all()
