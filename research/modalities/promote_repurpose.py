#!/usr/bin/env python3
"""Promote step: pool the NR4A3-only repurposing dock, take the top-N, write a candidate JSON for the
3-receptor + MM-GBSA selectivity tier.

Reads every shard's per-drug JSONL from s3://<bucket>/<INPUT_PREFIX>/<tag>-ckpt/<tag>.results.jsonl, ranks
best-first by NR4A3-pocket dG (then handle contacts), takes the top N, and writes a candidate JSON in the
nr4a3-denovo.json shape (`{candidates:[{name,smiles,denovo_promise,...}]}`) that nr4a3_matrix.py's candidate
mode consumes via `denovo_library.top_candidates`. `denovo_promise` is set to −dG so the matrix's own
top-N-by-promise ordering reproduces this NR4A3-pocket ranking.

Writes the candidate JSON to s3://<bucket>/<OUTPUT_PREFIX>/nr4a3-denovo.json (so the existing
gpu-denovo-dock-aws.yml can mount it with denovo_prefix=<OUTPUT_PREFIX>). Selectivity is NOT decided here —
it is decided downstream by the 3-receptor MM-GBSA + decoy-null tier, which yields BOTH the NR4A3-selective
and the pan-NR4A shortlists.

Env: INPUT_PREFIX (default nr4a3-repurpose-nr4a3only), OUTPUT_PREFIX (default nr4a3-repurpose-top),
TOP_N (default 250), SHARDS (comma tags; default shard-00..shard-10), BUCKET (optional),
AWS creds + AWS_DEFAULT_REGION.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repurpose_dock_core as core  # noqa: E402


def main():
    try:
        import boto3
    except ImportError:
        sys.exit("pip install boto3")
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3, sts = boto3.client("s3"), boto3.client("sts")
    acct = sts.get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    in_prefix = os.environ.get("INPUT_PREFIX", "nr4a3-repurpose-nr4a3only")
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-repurpose-top")
    top_n = int(os.environ.get("TOP_N", "250"))
    shards = [t.strip() for t in os.environ.get(
        "SHARDS", ",".join(f"shard-{i:02d}" for i in range(11))).split(",") if t.strip()]

    rows = []
    for tag in shards:
        key = f"{in_prefix}/{tag}-ckpt/{tag}.results.jsonl"
        try:
            body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode()
        except Exception:  # noqa: BLE001 — a shard with no JSONL is just skipped
            print(f"[{tag}] no JSONL at s3://{bucket}/{key}")
            continue
        n0 = len(rows)
        for ln in body.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                rows.append(json.loads(ln))
            except ValueError:
                continue
        print(f"[{tag}] +{len(rows) - n0} records")

    docked = [r for r in rows if r.get("dG_NR4A3") is not None]
    ranked = core.rank_rows(docked)[:top_n]
    print(f"\npooled {len(rows)} records, {len(docked)} docked → promoting top {len(ranked)}")

    candidates = []
    for r in ranked:
        candidates.append({
            "name": r["label"], "smiles": r["smiles"],
            "denovo_promise": -float(r["dG_NR4A3"]),          # −dG so matrix top-N reproduces this ranking
            "drug": r.get("drug"), "moa": r.get("moa"), "phase": r.get("phase"),
            "dG_NR4A3": r["dG_NR4A3"], "handle_contacts": r.get("handle_contacts"),
        })
    out = {"_note": "Top-N repurposing drugs by NR4A3-pocket docking dG, promoted to the 3-receptor + "
                    "MM-GBSA + decoy-null tier. denovo_promise = −dG. Selectivity decided downstream "
                    "(yields NR4A3-selective AND pan-NR4A shortlists).",
           "campaign": "repurpose-promote", "n_candidates": len(candidates),
           "candidates": candidates}

    key = f"{out_prefix}/nr4a3-denovo.json"
    blob = json.dumps(out, indent=2).encode()
    try:
        s3.put_object(Bucket=bucket, Key=key, Body=blob)
        print(f"WROTE s3://{bucket}/{key} ({len(blob)} bytes) — dock with denovo_prefix={out_prefix}")
    except Exception as e:  # noqa: BLE001 — surface a permissions problem loudly
        print(f"ERROR: could not PutObject s3://{bucket}/{key}: {e}", file=sys.stderr)
        print("(CI creds may lack s3:PutObject — fall back to the in-entry selection variant.)")
        sys.exit(1)

    print("\n=== promoted top (dG · handles · drug · moa) ===")
    for r in ranked[:25]:
        print(f"  {r['dG_NR4A3']:>6.2f}  {r.get('handle_contacts', 0)}  "
              f"{(r.get('drug') or r['label'])[:30]:30} {(r.get('moa') or '')[:40]}")


if __name__ == "__main__":
    main()
