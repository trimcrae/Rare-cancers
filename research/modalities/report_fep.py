#!/usr/bin/env python3
"""Fan-in reducer for the parallel selectivity FEP (read-only; also the estimator the monitor reuses).

Collects every shard's per-window results from s3://<bucket>/<TAG>/ckpt/**, runs BAR across adjacent λ-windows
per (receptor, leg) to get each leg ΔG, forms ΔG_bind per receptor (fep_sharding.binding_dg) and the
NR4A3-vs-paralogue ΔΔG (fep_sharding.selectivity_ddg), with SE propagated from the per-pair BAR errors and a
per-pair overlap proxy for convergence. Handles both the real openmmtools output and the smoke stub.

`estimate(results)` is importable (fep_monitor uses it on PARTIAL/pilot results for the early-stop decision).
CLI prints the final table. Env: AWS creds, FEP_TAG (default nr4a3-fep), AWS_DEFAULT_REGION.
"""
import glob
import json
import math
import os
import sys
import tempfile

TAG = os.environ.get("FEP_TAG", "nr4a3-fep")


def _bar(w_f, w_r):
    """ΔG (in kT) and stderr from forward/backward work samples. pymbar if available; else a robust
    Bennett-free fallback (mean-work midpoint) so the monitor still runs without pymbar."""
    try:
        from pymbar.other_estimators import bar as _b
        r = _b(w_f, w_r)
        return float(r["Delta_f"]), float(r.get("dDelta_f", 0.0))
    except Exception:  # noqa: BLE001
        import statistics as st
        mf = st.fmean(w_f) if w_f else 0.0
        mr = st.fmean(w_r) if w_r else 0.0
        dg = 0.5 * (mf - mr)                     # crude midpoint estimate
        n = max(len(w_f), 1)
        sd = (st.pstdev(w_f) if len(w_f) > 1 else 0.0) / math.sqrt(n)
        return dg, sd


def _overlap_proxy(w_f, w_r):
    """~1 when the forward/backward work distributions overlap (converged pair), ~0 when they don't.
    For a converged pair mean(w_f) ≈ −mean(w_r); large |mean_f+mean_r| relative to spread ⇒ poor overlap."""
    import statistics as st
    if not w_f or not w_r:
        return None
    spread = (st.pstdev(w_f) if len(w_f) > 1 else 0.0) + (st.pstdev(w_r) if len(w_r) > 1 else 0.0) + 1e-6
    return 1.0 / (1.0 + abs(st.fmean(w_f) + st.fmean(w_r)) / spread)


def _leg_dg(windows):
    """windows: list of per-window result dicts for one (receptor, leg), any order. Returns (dg_kcal, se_kcal,
    overlaps). Sums BAR over adjacent λ. kT→kcal via 0.593 kcal/mol at 300 K."""
    KT_KCAL = 0.593
    ws = sorted(windows, key=lambda r: r["window"])
    # real format: reduced_potentials {self,prev,next} arrays; smoke: scalar reduced_potential_self + u_neighbors
    dg = se2 = 0.0
    overlaps = []
    for i in range(len(ws) - 1):
        a, b = ws[i], ws[i + 1]
        if "reduced_potentials" in a and "reduced_potentials" in b:
            u_a, u_b = a["reduced_potentials"], b["reduced_potentials"]
            w_f = [n - s for n, s in zip(u_a.get("next", []), u_a.get("self", []))]
            w_r = [p - s for p, s in zip(u_b.get("prev", []), u_b.get("self", []))]
            d, e = _bar(w_f, w_r)
            dg += d * KT_KCAL
            se2 += (e * KT_KCAL) ** 2
            overlaps.append(_overlap_proxy(w_f, w_r))
        else:                                     # smoke scalar path (plumbing only)
            dg += (a.get("u_neighbors", {}).get("next", 0.0) - a.get("reduced_potential_self", 0.0)) * KT_KCAL
            overlaps.append(1.0)
    return dg, math.sqrt(se2), overlaps


def estimate(results):
    """results: list of per-unit dicts. Returns {receptor: {"dg","se","overlaps","legs":{leg:...},"n_windows"}}
    for whatever windows exist so far (works on partial/pilot data). ΔG_bind = solvent − complex + restraint."""
    import fep_sharding as fs
    by = {}
    for r in results:
        by.setdefault(r["receptor"], {}).setdefault(r["leg"], []).append(r)
    out = {}
    for rec, legs in by.items():
        leg_dg, leg_se, overlaps, restr = {}, {}, [], 0.0
        for leg, windows in legs.items():
            d, e, ov = _leg_dg(windows)
            leg_dg[leg] = d
            leg_se[leg] = e
            overlaps += [o for o in ov if o is not None]
            if leg == "complex" and windows:
                restr = max((w.get("restraint_corr_kJ", 0.0) or 0.0) for w in windows) / 4.184  # kJ→kcal
        if "solvent" in leg_dg and "complex" in leg_dg:
            dg = fs.binding_dg(leg_dg, restraint_corr=restr)
            se = fs.combine_error(leg_se.get("solvent", 0.0), leg_se.get("complex", 0.0))
            out[rec] = {"dg": round(dg, 4), "se": round(se, 4), "overlaps": overlaps,
                        "legs": {k: round(v, 3) for k, v in leg_dg.items()},
                        "n_windows": sum(len(w) for w in legs.values())}
    return out


def _download(bucket, prefix, dest):
    import boto3
    s3 = boto3.client("s3")
    n = 0
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        for o in page.get("Contents", []):
            if o["Key"].endswith(".json"):
                lp = os.path.join(dest, os.path.basename(o["Key"]))
                s3.download_file(bucket, o["Key"], lp)
                n += 1
    return n


def load_results(bucket=None):
    """Load all per-unit results from s3://<bucket>/<TAG>/ckpt/** (or a local FEP_LOCAL_DIR for testing)."""
    local = os.environ.get("FEP_LOCAL_DIR")
    if local:
        return [json.load(open(p)) for p in glob.glob(os.path.join(local, "*.json"))]
    import boto3
    bucket = bucket or f"sagemaker-{os.environ.get('AWS_DEFAULT_REGION','us-east-2')}-" \
                       f"{boto3.client('sts').get_caller_identity()['Account']}"
    with tempfile.TemporaryDirectory() as tmp:
        n = _download(bucket, f"{TAG}/ckpt/", tmp)
        print(f"loaded {n} per-unit results from s3://{bucket}/{TAG}/ckpt/", flush=True)
        return [json.load(open(p)) for p in glob.glob(os.path.join(tmp, "*.json"))]


def main():
    results = load_results()
    if not results:
        sys.exit("no FEP results yet")
    import fep_sharding as fs
    est = estimate(results)
    print("\n=== per-receptor ΔG_bind (kcal/mol) ===")
    for rec, e in sorted(est.items()):
        ph = {}
        print(f"  {rec.upper()}: ΔG_bind {e['dg']} ± {e['se']}  (legs {e['legs']}, {e['n_windows']} windows)")
    if "nr4a3" in est:
        ddg = fs.selectivity_ddg({r: e["dg"] for r, e in est.items()}, "nr4a3")
        print("\n=== selectivity ΔΔG = ΔG_bind(NR4A3) − ΔG_bind(paralogue)  (negative = NR4A3-selective) ===")
        for other, d in ddg.items():
            se = fs.combine_error(est["nr4a3"]["se"], est[other]["se"])
            print(f"  NR4A3 vs {other.upper()}: ΔΔG {d} ± {round(se,3)}")


if __name__ == "__main__":
    main()
