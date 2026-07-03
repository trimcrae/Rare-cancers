#!/usr/bin/env python3
"""Fan-in reducer for the parallel Yank selectivity FEP (read-only; also the estimator the monitor reuses).

Each Yank experiment (one per receptor) writes a single result marker <receptor>.json with `dg_bind_kcal` +
`ddg_err_kcal` (Yank already did the two-leg double-decoupling, Boresch correction, HREX, and MBAR internally
— so there is no per-window BAR to run here). This reducer just collects the per-receptor ΔG_bind from
s3://<bucket>/<TAG>/ckpt/** and forms the NR4A3-vs-paralogue ΔΔG (fep_sharding.selectivity_ddg), SE by
quadrature. Prefers the 'prod' marker over 'pilot' if both exist. Handles the smoke stub (same dg_bind field).

`estimate(results)` is importable (fep_monitor uses it on PARTIAL/pilot results for the early-stop decision).
CLI prints the final table. Env: AWS creds, FEP_TAG (default nr4a3-fep), AWS_DEFAULT_REGION.
"""
import glob
import json
import os
import sys
import tempfile

TAG = os.environ.get("FEP_TAG", "nr4a3-fep")


def estimate(results):
    """results: list of per-unit dicts (each a Yank per-receptor marker with dg_bind_kcal). Returns
    {receptor: {"dg","se","phase","n_iterations"}} using the most-complete marker per receptor (prod > pilot).
    Works on partial data: a receptor appears as soon as its pilot marker lands."""
    rank = {"prod": 2, "pilot": 1}
    best = {}
    for r in results:
        if "dg_bind_kcal" not in r or "receptor" not in r:      # ignore yank-internal / torn files
            continue
        rec = r["receptor"]
        if rec not in best or rank.get(r.get("phase"), 0) >= rank.get(best[rec].get("phase"), 0):
            best[rec] = r
    out = {}
    for rec, r in best.items():
        out[rec] = {"dg": round(float(r["dg_bind_kcal"]), 4),
                    "se": round(float(r.get("ddg_err_kcal", 0.0)), 4),
                    "phase": r.get("phase"), "n_iterations": r.get("n_iterations"),
                    # legacy keys the monitor's convergence check reads (Yank owns real convergence):
                    "overlaps": [], "n_windows": 1}
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
    def _load_dir(d):
        out = []
        for p in glob.glob(os.path.join(d, "*.json")):
            try:                                   # skip torn / half-synced spot writes — robustness
                out.append(json.load(open(p)))
            except Exception:  # noqa: BLE001
                pass
        return out
    local = os.environ.get("FEP_LOCAL_DIR")
    if local:
        return _load_dir(local)
    import boto3
    bucket = bucket or f"sagemaker-{os.environ.get('AWS_DEFAULT_REGION','us-east-2')}-" \
                       f"{boto3.client('sts').get_caller_identity()['Account']}"
    with tempfile.TemporaryDirectory() as tmp:
        n = _download(bucket, f"{TAG}/ckpt/", tmp)
        print(f"loaded {n} per-unit results from s3://{bucket}/{TAG}/ckpt/", flush=True)
        return _load_dir(tmp)


def main():
    results = load_results()
    if not results:
        sys.exit("no FEP results yet")
    import fep_sharding as fs
    est = estimate(results)
    print("\n=== per-receptor ΔG_bind (kcal/mol; Yank ABFE) ===")
    for rec, e in sorted(est.items()):
        print(f"  {rec.upper()}: ΔG_bind {e['dg']} ± {e['se']}  (phase {e.get('phase')}, "
              f"{e.get('n_iterations')} iters)")
    if "nr4a3" in est:
        ddg = fs.selectivity_ddg({r: e["dg"] for r, e in est.items()}, "nr4a3")
        print("\n=== selectivity ΔΔG = ΔG_bind(NR4A3) − ΔG_bind(paralogue)  (negative = NR4A3-selective) ===")
        for other, d in ddg.items():
            se = fs.combine_error(est["nr4a3"]["se"], est[other]["se"])
            print(f"  NR4A3 vs {other.upper()}: ΔΔG {d} ± {round(se,3)}")


if __name__ == "__main__":
    main()
