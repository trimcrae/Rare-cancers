#!/usr/bin/env python3
"""Reduce 5a-KS benchmark leg JSONs -> the engine's qualification verdict AND its first real price.

Two deliverables come out of the known-answer benchmark, and they are independent:

1. **A VERDICT.** Does the wedge engine recover measured protein-protein interface ddG values within
   tolerance, in the right order? Until it does, `nr4a3_protein_fep` may not contribute a number to
   the manuscript, per nr4a3-program-map.md's gate.

2. **A PRICE.** nr4a3-program-map.md carries 5a-KS as UNPRICED, and says so bluntly: an engine that exists is
   not a rate. This reduction turns completed legs into a measured s/iteration, GPU-h/leg and $/leg,
   which is the only honest basis for pricing the rung. The projection is stated per *wedge* (2
   environments x n replicates), and it is a PROJECTION from benchmark systems — a barnase-barstar
   leg is ~30k particles while an NR4A ternary wedge leg is ~146k, so the benchmark rate must be
   scaled by particle count, not quoted directly. That scaling is reported explicitly rather than
   folded silently into a single number.

Runs on CPU/CI ($0). Reads leg JSONs from a local directory or straight from the S3 result prefix.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import protfep_bench as bench  # noqa: E402

# The production wedge this benchmark is meant to price, for the particle-count scaling below.
NR4A_TERNARY_PARTICLES = 146284   # measured: the firm ternary leg's solvated hybrid (nr4a3-program-map.md)
NR4A_BINARY_PARTICLES = 35000     # approximate: the binary RBFE complex+solvent lane


def _mean_sd(xs):
    """Mean and sample SD. Pure. SD is None for n < 2 — never silently zero."""
    xs = [float(x) for x in xs]
    n = len(xs)
    if n == 0:
        return None, None
    mean = sum(xs) / n
    if n < 2:
        return mean, None
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return mean, var ** 0.5


def load_legs(source):
    """Load every `leg_*.json` from a local directory or an `s3://bucket/prefix`. Returns a list."""
    docs = []
    if str(source).startswith("s3://"):
        import boto3
        _, _, rest = str(source).partition("s3://")
        b, _, p = rest.partition("/")
        s3 = boto3.client("s3")
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=b, Prefix=p.rstrip("/") + "/"):
            for obj in page.get("Contents", []):
                name = os.path.basename(obj["Key"])
                if name.startswith("leg_") and name.endswith(".json"):
                    docs.append(json.loads(s3.get_object(Bucket=b, Key=obj["Key"])["Body"].read().decode()))
    else:
        for root, _dirs, files in os.walk(source):
            for name in files:
                if name.startswith("leg_") and name.endswith(".json"):
                    with open(os.path.join(root, name)) as fh:
                        docs.append(json.load(fh))
    return docs


def group_legs(docs):
    """Group finished legs by (benchmark, environment). Pure.

    SMOKE LEGS ARE EXCLUDED, deliberately and loudly: a 3-window/20-iteration leg produces a number,
    and a number that looks like a dG is exactly the kind of thing that gets averaged into a real
    result by accident. Anything whose leg_id carries the smoke suffix is dropped here.
    """
    grouped, skipped = {}, []
    for d in docs:
        lid = str(d.get("leg_id", ""))
        if lid.endswith("_smoke"):
            skipped.append(lid)
            continue
        if d.get("status") != "done" or d.get("dg_kcal") is None:
            continue
        meta = d.get("meta") or {}
        name = meta.get("benchmark")
        env = meta.get("environment")
        if not name or not env:
            # Fall back to the leg_id convention `<benchmark>__<env>_r<k>`.
            head, _, tail = lid.partition("__")
            name = name or head
            env = env or tail.split("_r")[0]
        grouped.setdefault(name, {}).setdefault(env, []).append(d)
    return grouped, skipped


def ddg_for(legs_by_env):
    """ddG_bind for one benchmark from its complex/apo legs. Pure.

    ddG_bind = dG_mut(complex) - dG_mut(apo), where dG_mut(X) is the ALCHEMICAL WT->mutant
    transformation run in environment X.

    SIGN, stated because the abort gate turns on it and a flip would look entirely plausible either
    way. The thermodynamic cycle gives ddG_bind = dG_bind(mut) - dG_bind(wt) = dG_mut(complex) -
    dG_mut(apo), so POSITIVE means the mutant binds WORSE — the mutation weakens binding. That is the
    same sign convention as the reference side, where protfep_refcheck computes
    RT*ln(Kd_mut/Kd_wt) and documents "positive = the mutation WEAKENS binding". The two must agree
    or score_benchmark compares a number against its own negation; barnase-barstar Y29A is a
    destabilising hot-spot knockout and its reference is +3.47, so a correct engine returns a large
    POSITIVE ddG here. Pinned by test_ddg_sign_matches_the_reference_convention.

    Error is the between-replicate SD added in quadrature
    — the repo's standing rule, and the right estimator here because setup-to-setup variance, not
    within-leg MBAR precision, dominates an alchemical mutation. Where only one replicate exists the
    SD is None and the result is explicitly marked single-replicate rather than being given a
    fabricated error bar.
    """
    comp = [d["dg_kcal"] for d in legs_by_env.get("complex", [])]
    apo = [d["dg_kcal"] for d in legs_by_env.get("apo", [])]
    if not comp or not apo:
        return None
    c_mean, c_sd = _mean_sd(comp)
    a_mean, a_sd = _mean_sd(apo)
    ddg = c_mean - a_mean
    sd = None
    if c_sd is not None and a_sd is not None:
        sd = (c_sd ** 2 + a_sd ** 2) ** 0.5
    mbar = [d.get("dg_mbar_se_kcal") for d in legs_by_env.get("complex", [])
            + legs_by_env.get("apo", []) if d.get("dg_mbar_se_kcal") is not None]
    return {
        "ddg_bind_kcal": ddg,
        "ddg_sd_kcal": sd,
        "n_complex": len(comp), "n_apo": len(apo),
        "dg_complex_kcal": c_mean, "dg_complex_sd": c_sd,
        "dg_apo_kcal": a_mean, "dg_apo_sd": a_sd,
        "single_replicate": sd is None,
        "error_model": ("between-replicate SD in quadrature" if sd is not None else
                        "NO ERROR BAR — single replicate per environment; the MBAR SE of one leg is a "
                        "within-leg precision estimate and understates setup variance, so it is reported "
                        "separately rather than used as the uncertainty"),
        "mbar_se_range_kcal": ([min(mbar), max(mbar)] if mbar else None),
    }


def price_from_legs(docs, hourly_usd=None):
    """Measured cost basis from completed legs. Pure (given the docs).

    Reports the benchmark's own realized rate, then scales it by particle count to project what an
    NR4A wedge leg would cost. The scaling is linear in particles, which is the standard first-order
    assumption for PME MD throughput at fixed cutoff — stated here as an assumption, because the only
    thing worse than an unpriced rung is a rung priced off an unstated extrapolation. This is a
    PROJECTION and must be labelled as one wherever it is quoted.
    """
    rate = float(hourly_usd if hourly_usd is not None else os.environ.get("PROTFEP_HOURLY_USD", "0.20"))
    finished = [d for d in docs if d.get("status") == "done" and d.get("gpu_hours")
                and not str(d.get("leg_id", "")).endswith("_smoke")]
    if not finished:
        return {"priced": False, "reason": "no completed non-smoke legs yet"}

    # A leg written before the cumulative-GPU-hours fix reports only its FINAL segment. The apo pilot
    # leg was preempted at 14/16 windows and finished in 0.073 GPU-h, so it published $0.015/leg and a
    # ~$0.59 wedge — roughly 20x low, because the ~1.3 GPU-h before the preemption vanished with the
    # host. The predicate is exact rather than a guess about dates: the fixed driver writes
    # `gpu_hours_cumulative`, the old one did not. Refusing to price is the honest outcome — a rung
    # carried as UNPRICED costs a re-run, whereas a rung carried at 1/20th of its true cost is a
    # number that gets quoted, planned against, and only caught after the money is committed.
    trustworthy = [d for d in finished if d.get("gpu_hours_cumulative") is not None]
    suspect = [str(d.get("leg_id")) for d in finished if d.get("gpu_hours_cumulative") is None]
    if not trustworthy:
        return {
            "priced": False,
            "reason": ("every completed leg predates the cumulative-GPU-hours fix, so its `gpu_hours` "
                       "is the final segment after preemption rather than the leg's true cost — "
                       "pricing off it understates the rung (observed ~20x low on the apo pilot leg)"),
            "legs_excluded_as_pre_fix": suspect,
        }
    finished = trustworthy
    gpu_h = [float(d["gpu_hours"]) for d in finished]
    parts = [int(d.get("n_particles") or 0) for d in finished if d.get("n_particles")]
    s_iter = [float(d["s_per_iter"]) for d in finished if d.get("s_per_iter")]
    mean_h, sd_h = _mean_sd(gpu_h)
    mean_parts, _ = _mean_sd(parts) if parts else (None, None)
    out = {
        "priced": True,
        "n_legs_measured": len(finished),
        "gpu_hours_per_leg": {"mean": round(mean_h, 3), "sd": (round(sd_h, 3) if sd_h else None),
                              "min": round(min(gpu_h), 3), "max": round(max(gpu_h), 3)},
        "s_per_iteration": (round(sum(s_iter) / len(s_iter), 2) if s_iter else None),
        "assumed_hourly_usd": rate,
        "usd_per_benchmark_leg": round(mean_h * rate, 3),
        "mean_particles": (int(mean_parts) if mean_parts else None),
        "legs_excluded_as_pre_fix": suspect,
    }
    if mean_parts:
        scale_t = NR4A_TERNARY_PARTICLES / mean_parts
        scale_b = NR4A_BINARY_PARTICLES / mean_parts
        # One wedge = 2 environments x n replicates; the ternary environment dominates the cost.
        for n_rep in (2, 3):
            per_wedge_h = n_rep * (mean_h * scale_t + mean_h * scale_b)
            out[f"projected_wedge_usd_{n_rep}rep"] = round(per_wedge_h * rate, 2)
            out[f"projected_wedge_gpu_h_{n_rep}rep"] = round(per_wedge_h, 1)
        out["projection_basis"] = (
            f"linear particle-count scaling from the benchmark's {int(mean_parts)} particles to "
            f"{NR4A_TERNARY_PARTICLES} (NR4A ternary leg) and ~{NR4A_BINARY_PARTICLES} (binary leg). "
            f"Linear-in-particles is the standard first-order assumption for PME MD at fixed cutoff; it "
            f"is an ASSUMPTION, not a measurement, and the projected wedge cost is therefore a PROJECTION "
            f"— it may not be quoted as a measured rate.")
    return out


def reduce_all(source, hourly_usd=None):
    """Full reduction: per-benchmark ddG, the qualification verdict, and the measured price."""
    docs = load_legs(source)
    grouped, smoke = group_legs(docs)
    per_benchmark, scores = {}, {}
    for name, by_env in grouped.items():
        res = ddg_for(by_env)
        per_benchmark[name] = res
        if res and name in bench.BENCHMARKS:
            scores[name] = bench.score_benchmark(name, res["ddg_bind_kcal"], res["ddg_sd_kcal"])
    verdict = bench.qualify(scores) if scores else {
        "qualified": False, "reason": "no benchmark produced a complete ddG yet", "n_scored": 0}
    return {
        "source": str(source),
        "n_leg_docs": len(docs),
        "n_smoke_legs_excluded": len(smoke),
        "per_benchmark": per_benchmark,
        "scores": scores,
        "verdict": verdict,
        "price": price_from_legs(docs, hourly_usd=hourly_usd),
        # Read from the legs themselves rather than hardcoded: the reducer is engine-agnostic on
        # purpose (it survived the perses -> pmx switch untouched), so it must not assert an engine
        # the legs did not use. That string was stale within hours of being written.
        "engines": sorted({d.get("engine") for d in docs if d.get("engine")}) or ["(no legs yet)"],
        "protocols": sorted({d.get("protocol") for d in docs if d.get("protocol")}),
    }


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Reduce 5a-KS benchmark legs to a verdict + a price")
    ap.add_argument("--source", default=os.environ.get(
        "PROTFEP_SOURCE", "s3://sagemaker-us-east-2-646605541856/protfep-benchmark"))
    ap.add_argument("--hourly-usd", type=float, default=None)
    ap.add_argument("--out", default=None, help="write the reduction JSON here as well as stdout")
    args = ap.parse_args(argv)
    out = reduce_all(args.source, hourly_usd=args.hourly_usd)
    txt = json.dumps(out, indent=2)
    print(txt)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(txt + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
