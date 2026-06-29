#!/usr/bin/env python3
"""
Read the de-novo warhead screen result from S3 and print the ranked candidates + shortlist.

Reads s3://<default-bucket>/<prefix>/nr4a3-denovo.json (written by nr4a3_denovo.py MODE=screen) and prints:
the generation census, the novelty/developability counts, the selective + pan shortlists (what the one
MM-GBSA confirmation run scores), and a ranked per-candidate table (dG into each opened pocket, margins,
cell, novelty, developability, handle contacts). Read-only — the screen already did the docking.
"""
import json
import os
import sys


def _f(x, w=6, p=2):
    return f"{x:>{w}.{p}f}" if isinstance(x, (int, float)) else f"{'--':>{w}}"


def main():
    try:
        import boto3
    except ImportError:
        sys.exit("pip install boto3")
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3, sts = boto3.client("s3"), boto3.client("sts")
    acct = sts.get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-denovo")
    key = f"{prefix}/nr4a3-denovo.json"
    print(f"reading s3://{bucket}/{key}", flush=True)
    try:
        res = json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
    except Exception as e:  # noqa: BLE001
        sys.exit(f"could not read s3://{bucket}/{key}: {e}")

    status = res.get("_status")
    print(f"\n_status: {status}")
    if status != "ok":
        print("payload:", json.dumps({k: res.get(k) for k in ("error", "trace", "_warnings")}, indent=2))
        sys.exit(0 if status else 1)

    s = res.get("summary", {})
    print(f"n_generated: {res.get('n_generated')}  novel: {s.get('n_novel')}  "
          f"developable: {s.get('n_developable')}")
    print("\n=== cell census ===")
    for cell, n in sorted((s.get("cell_census") or {}).items(), key=lambda kv: -kv[1]):
        print(f"  {cell:<26} {n}")

    sl = res.get("shortlist", {})
    print("\n=== shortlist (-> MM-GBSA confirmation) ===")
    for k in ("selective", "pan"):
        vals = sl.get(k) or []
        print(f"  {k:<10} ({len(vals)}): {', '.join(vals) if vals else '(none)'}")

    rows = res.get("candidates", [])
    print(f"\n=== ranked candidates ({len(rows)}; showing <=30) ===")
    hdr = (f"{'#':>2} {'label':<18} {'cell':<14} {'dG3':>7} {'dG1':>7} {'dG2':>7} "
           f"{'mΔ1':>6} {'mΔ2':>6} {'nov':>4} {'dev':>3} {'hnd':>3} {'pass':>4}")
    print(hdr); print("-" * len(hdr))
    for i, r in enumerate(rows[:30], 1):
        dG = r.get("dG", {})
        print(f"{i:>2} {str(r.get('label'))[:18]:<18} {str(r.get('cell'))[:14]:<14} "
              f"{_f(dG.get('NR4A3'), 7)} {_f(dG.get('NR4A1'), 7)} {_f(dG.get('NR4A2'), 7)} "
              f"{_f(r.get('margin_vs_NR4A1'), 6)} {_f(r.get('margin_vs_NR4A2'), 6)} "
              f"{_f(r.get('max_tanimoto_to_known'), 4)} "
              f"{'Y' if r.get('developable') else 'n':>3} "
              f"{str(r.get('handle_contacts', '')):>3} {'Y' if r.get('passes_screen') else 'n':>4}")


if __name__ == "__main__":
    main()
