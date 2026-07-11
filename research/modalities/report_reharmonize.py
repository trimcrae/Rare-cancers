#!/usr/bin/env python3
"""
Read the HARMONIZED pocket-tracking audit result from S3 and print the consolidated both-denominator
detection table (reviewer P0 deliverable + GATE-1 of the ensemble-robust redesign).

Reads s3://<default-bucket>/<prefix>/pocket-reharmonize-summary.json (written by
nr4a3_pocket_reharmonize.load_and_build) and prints, per load-bearing NR4A3 ensemble: total frames
propagated, matched-detected, detection fraction, and the fraction >= D* under BOTH denominators
(among detected / among all propagated). Also echoes the pinned fpocket version and the match params so
the site definition is on the record. Read-only -- the heavy fpocket re-scoring already happened.

It additionally dumps the raw summary JSON between BEGIN/END sentinels so the result can be lifted from
the Actions log and committed into the repo durably (GATE-1 is a durable, in-repo determination).
"""
import json
import os
import sys

BEGIN = "===BEGIN_REHARMONIZE_SUMMARY_JSON==="
END = "===END_REHARMONIZE_SUMMARY_JSON==="


def _fmt(x, p=3):
    return f"{x:.{p}f}" if isinstance(x, (int, float)) else "--"


def main():
    try:
        import boto3
    except ImportError:
        sys.exit("pip install boto3")
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3, sts = boto3.client("s3"), boto3.client("sts")
    acct = sts.get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-pocket-reharmonize")
    key = f"{prefix}/pocket-reharmonize-summary.json"
    print(f"reading s3://{bucket}/{key}", flush=True)

    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    except Exception as e:  # noqa: BLE001
        sys.exit(f"could not read s3://{bucket}/{key}: {e}")
    res = json.loads(body)

    print(f"\n{res.get('_title', '(no title)')}")
    print(f"fpocket_version: {res.get('fpocket_version')}   D* = {res.get('d_star')}")
    print(f"match_params: {json.dumps(res.get('match_params', {}))}")
    print(f"\n_method: {res.get('_method')}")

    rows = res.get("rows", [])
    hdr = ("ensemble", "n_prop", "n_det", "det_frac", "n>=D*", "ge/det", "ge/all", "D*")
    print("\n=== consolidated harmonized detection (both denominators) ===")
    print("  {:>24} {:>7} {:>6} {:>8} {:>6} {:>7} {:>7} {:>6}".format(*hdr))
    for r in rows:
        print("  {:>24} {:>7} {:>6} {:>8} {:>6} {:>7} {:>7} {:>6}".format(
            str(r.get("ensemble"))[:24],
            str(r.get("n_propagated")),
            str(r.get("n_detected")),
            _fmt(r.get("detection_fraction")),
            str(r.get("n_ge_dstar")),
            _fmt(r.get("frac_ge_among_detected")),
            _fmt(r.get("frac_ge_among_propagated")),
            _fmt(r.get("d_star")),
        ))

    # Raw JSON for durable capture (lift from the Actions log -> commit into the repo).
    print(f"\n{BEGIN}")
    print(json.dumps(res, indent=2))
    print(END)


if __name__ == "__main__":
    main()
