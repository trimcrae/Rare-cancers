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
    full_ranked = core.rank_rows(docked)
    # RANK_START/RANK_END (1-indexed, inclusive) carve a rank BAND out of the full ranking — e.g. to dock
    # ranks 101-250 as extra parallel lanes on top of an already-running top-100 dock. Defaults = top_n.
    rank_start = int(os.environ.get("RANK_START") or "1")
    rank_end = int(os.environ.get("RANK_END") or str(top_n))
    ranked = full_ranked[rank_start - 1:rank_end]
    print(f"\npooled {len(rows)} records, {len(docked)} docked → promoting ranks {rank_start}-{rank_end} "
          f"({len(ranked)} drugs)")

    def _cand(r):
        return {
            "name": r["label"], "smiles": r["smiles"],
            "denovo_promise": -float(r["dG_NR4A3"]),          # −dG so matrix top-N reproduces this ranking
            "drug": r.get("drug"), "moa": r.get("moa"), "phase": r.get("phase"),
            "dG_NR4A3": r["dG_NR4A3"], "handle_contacts": r.get("handle_contacts"),
        }

    def _write(prefix, rs):
        out = {"_note": "Repurposing drugs by NR4A3-pocket docking dG, promoted to the 3-receptor + "
                        "MM-GBSA + decoy-null tier. denovo_promise = −dG. Selectivity decided downstream "
                        "(yields NR4A3-selective AND pan-NR4A shortlists).",
               "campaign": "repurpose-promote", "n_candidates": len(rs),
               "candidates": [_cand(r) for r in rs]}
        key = f"{prefix}/nr4a3-denovo.json"
        blob = json.dumps(out, indent=2).encode()
        try:
            s3.put_object(Bucket=bucket, Key=key, Body=blob)
            print(f"WROTE s3://{bucket}/{key} ({len(blob)} bytes) — dock with denovo_prefix={prefix}")
        except Exception as e:  # noqa: BLE001 — surface a permissions problem loudly
            print(f"ERROR: could not PutObject s3://{bucket}/{key}: {e}", file=sys.stderr)
            sys.exit(1)

    # BANDS>1 splits the selected range into contiguous prefixes <OUTPUT_PREFIX>-b{i}, each an independent
    # parallel dock lane (fire one CPU dock job per band). BANDS=1 (default) writes the whole range to
    # <OUTPUT_PREFIX>. Contiguous (not round-robin) so each band spans a compact dG sub-range.
    bands = int(os.environ.get("BANDS", "1"))
    if bands <= 1:
        _write(out_prefix, ranked)
    else:
        size = -(-len(ranked) // bands)                       # ceil so the last band holds the remainder
        for i in range(bands):
            grp = ranked[i * size:(i + 1) * size]
            if grp:
                _write(f"{out_prefix}-b{i}", grp)

    print("\n=== promoted band (dG · handles · drug · moa) ===")
    for r in ranked[:25]:
        print(f"  {r['dG_NR4A3']:>6.2f}  {r.get('handle_contacts', 0)}  "
              f"{(r.get('drug') or r['label'])[:30]:30} {(r.get('moa') or '')[:40]}")


if __name__ == "__main__":
    main()
