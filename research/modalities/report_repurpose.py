#!/usr/bin/env python3
"""Read-only S3 report for the NR4A3-only repurposing dock — ranked NR4A3-pocket hits, live or final.

Reads the per-drug JSONL checkpoint (freshest; written after each drug) from
s3://<default-bucket>/<OUTPUT_PREFIX>/<TAG>-ckpt/<TAG>.results.jsonl, ranks best-first (most-negative
NR4A3 dG, then most engageable-handle contacts), and prints progress + the top hits. Works mid-run (the
JSONL grows continuously). Pass TAGS (comma list) to pool several shards.

dG is a screening PRIOR, not an affinity, and selectivity is NOT scored here — a low dG + high handle
contact count means "worth promoting to the 3-receptor + MM-GBSA + decoy-null tier", not "a hit".

Env: OUTPUT_PREFIX (default nr4a3-repurpose-nr4a3only), TAGS or TAG (default shard-02), TOP_N (default 20),
BUCKET (optional), AWS creds + AWS_DEFAULT_REGION.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repurpose_dock_core as core  # noqa: E402


def _read_jsonl(s3, bucket, key):
    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode()
    except Exception:  # noqa: BLE001 — missing/not-yet-written
        return None
    rows = []
    for ln in body.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            rows.append(json.loads(ln))
        except ValueError:
            continue                     # partial trailing line from an in-flight append
    return rows


def main():
    try:
        import boto3
    except ImportError:
        sys.exit("pip install boto3")
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3, sts = boto3.client("s3"), boto3.client("sts")
    acct = sts.get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-repurpose-nr4a3only")
    tags = [t.strip() for t in (os.environ.get("TAGS") or os.environ.get("TAG") or "shard-02").split(",")
            if t.strip()]
    top_n = int(os.environ.get("TOP_N", "20"))

    allrows, per_tag = [], {}
    for tag in tags:
        key = f"{prefix}/{tag}-ckpt/{tag}.results.jsonl"
        rows = _read_jsonl(s3, bucket, key)
        if rows is None:
            print(f"[{tag}] no JSONL yet at s3://{bucket}/{key}")
            continue
        per_tag[tag] = rows
        allrows.extend(rows)

    if not allrows:
        print("no results yet (jobs may still be provisioning / early in docking).")
        return

    n_docked = sum(1 for r in allrows if r.get("dG_NR4A3") is not None)
    n_fail = len(allrows) - n_docked
    print(f"pooled {len(tags)} shard(s): {', '.join(f'{t}={len(per_tag.get(t, []))}' for t in tags)}")
    print(f"records: {len(allrows)}   docked: {n_docked}   failed/embed-skip: {n_fail}\n")

    ranked = core.rank_rows([r for r in allrows if r.get("dG_NR4A3") is not None])
    print(f"=== top {min(top_n, len(ranked))} by NR4A3-pocket docking dG (PRIOR, not affinity) ===")
    print(f"{'dG':>7}  {'hnd':>3} {'csv':>3}  {'drug':<32} moa")
    for r in ranked[:top_n]:
        drug = (r.get("drug") or r.get("label") or "")[:32]
        moa = (r.get("moa") or "")[:44]
        print(f"{r['dG_NR4A3']:>7.2f}  {r.get('handle_contacts', 0):>3} "
              f"{r.get('conserved_contacts', 0):>3}  {drug:<32} {moa}")
    print("\nhnd = engageable-handle contacts (max 5); csv = conserved-core contacts (max 3).")
    print("NEXT: promote the top hits to the 3-receptor + MM-GBSA + decoy-null selectivity tier.")


if __name__ == "__main__":
    main()
