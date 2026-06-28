#!/usr/bin/env python3
"""
Read the MM-GBSA rescoring result from S3 and print the verdict table (+ any per-ligand errors).

Reads s3://<default-bucket>/<prefix>/nr4a3-mmgbsa.json (written by nr4a3_mmgbsa.py) and prints the
method, verdict census, the confirmed_selective / reversed lead lists, a ranked per-candidate table
(MM-GBSA ΔG into each opened pocket, MM margins vs the docking margin, verdict), and — crucially when a
run comes back all-`incomplete` — the distinct `_errors` so a systematic failure is diagnosable without
reading S3 by hand. Read-only.
"""
import json
import os
import sys


def _f(x, w=8, p=2):
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
    prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-mmgbsa")
    key = f"{prefix}/nr4a3-mmgbsa.json"
    print(f"reading s3://{bucket}/{key}", flush=True)

    try:
        res = json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
    except Exception as e:  # noqa: BLE001
        sys.exit(f"could not read s3://{bucket}/{key}: {e}")

    print(f"\n_status: {res.get('_status')}")
    print(f"method: {json.dumps(res.get('method', {}))}")
    if res.get("_status") == "error":
        print("ERROR payload:", json.dumps({k: res.get(k) for k in ("error", "trace")}, indent=2))
        sys.exit(1)
    if res.get("_warnings"):
        print("warnings:", json.dumps(res["_warnings"], indent=2))

    print("\n=== verdict census ===")
    for v, n in sorted((res.get("verdict_census") or {}).items(), key=lambda kv: -kv[1]):
        print(f"  {v:<24} {n}")
    print(f"\nconfirmed_selective: {res.get('leads_confirmed_selective')}")
    print(f"reversed:            {res.get('leads_reversed')}")

    rows = res.get("candidates", [])
    print(f"\n=== ranked candidates ({len(rows)}) ===")
    hdr = f"{'#':>2} {'label':<24} {'mmΔG3':>8} {'mmΔG1':>8} {'mmΔG2':>8} {'mmMin':>7} {'dockMin':>7}  verdict"
    print(hdr); print("-" * len(hdr))
    for i, r in enumerate(rows, 1):
        g = r.get("dG_mmgbsa", {})
        print(f"{i:>2} {str(r.get('label'))[:24]:<24} {_f(g.get('NR4A3'))} {_f(g.get('NR4A1'))} "
              f"{_f(g.get('NR4A2'))} {_f(r.get('mm_min_margin'),7)} {_f(r.get('dock_min_margin'),7)}  "
              f"{r.get('verdict')}")

    # surface distinct per-ligand errors (key for diagnosing an all-incomplete run)
    seen = {}
    for r in rows:
        for tgt, msg in (r.get("_errors") or {}).items():
            seen.setdefault(msg, []).append(f"{r.get('label')}/{tgt}")
    if seen:
        print(f"\n=== distinct per-ligand errors ({len(seen)}) ===")
        for msg, where in seen.items():
            print(f"  [{len(where)}x] {msg}\n      e.g. {where[0]}")


if __name__ == "__main__":
    main()
