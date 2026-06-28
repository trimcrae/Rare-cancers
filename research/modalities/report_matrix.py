#!/usr/bin/env python3
"""
Read the NR4A selectivity-matrix result from S3 and print the ranked per-candidate fingerprint.

Reads s3://<default-bucket>/<prefix>/nr4a3-matrix.json (written by nr4a3_matrix.py) and prints:
the cell census, the three lead lists (nr4a3_selective / pan_nr4a / anti_targets), and a ranked
per-candidate table (dG into each opened pocket, selectivity margins, assigned matrix cell, handle +
conserved contacts). Read-only — the heavy docking already happened in the matrix job.
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
    prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-matrix")
    key = f"{prefix}/nr4a3-matrix.json"
    print(f"reading s3://{bucket}/{key}", flush=True)

    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    except Exception as e:  # noqa: BLE001
        sys.exit(f"could not read s3://{bucket}/{key}: {e}")
    res = json.loads(body)

    status = res.get("_status")
    print(f"\n_status: {status}")
    if status != "ok":
        print("ERROR payload:", json.dumps({k: res.get(k) for k in ("error", "trace")}, indent=2))
        sys.exit(1)
    print(f"n_candidates: {res.get('n_candidates')}")

    print("\n=== cell census (selectivity_fingerprint) ===")
    for cell, n in sorted((res.get("matrix", {}).get("cell_census") or {}).items(),
                          key=lambda kv: -kv[1]):
        print(f"  {cell:<26} {n}")

    leads = res.get("leads", {})
    print("\n=== leads ===")
    for k in ("nr4a3_selective", "pan_nr4a", "anti_targets"):
        vals = leads.get(k) or []
        print(f"  {k:<16} ({len(vals)}): {', '.join(vals) if vals else '(none)'}")

    rows = res.get("candidates", [])
    print(f"\n=== ranked candidates ({len(rows)}) ===")
    hdr = f"{'#':>2} {'label':<22} {'cell':<22} {'dG3':>7} {'dG1':>7} {'dG2':>7} {'mΔ1':>6} {'mΔ2':>6} {'hnd':>3} {'cons':>4}"
    print(hdr)
    print("-" * len(hdr))
    for i, r in enumerate(rows, 1):
        dG = r.get("dG", {})
        print(f"{i:>2} {str(r.get('label'))[:22]:<22} {str(r.get('cell'))[:22]:<22} "
              f"{_f(dG.get('NR4A3'), 7)} {_f(dG.get('NR4A1'), 7)} {_f(dG.get('NR4A2'), 7)} "
              f"{_f(r.get('margin_vs_NR4A1'), 6)} {_f(r.get('margin_vs_NR4A2'), 6)} "
              f"{str(r.get('handle_contacts', '')):>3} {str(r.get('conserved_contacts', '')):>4}")


if __name__ == "__main__":
    main()
