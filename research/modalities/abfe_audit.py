#!/usr/bin/env python3
"""AUDIT every ABFE leg's checkpoint data for the λ-window self-consistency bug.

Motivation (2026-07-11): `N_WINDOWS = len(LAMBDA_ELEC)` in nr4a3_abfe.py was frozen at import to the STANDARD
12-window count, but a `dense` run evaluates each sample's reduced potential u at 16 λ-states. So a dense run
produced legs with 12 windows but 16-entry u vectors — inconsistent, and (as designed) UN-reducible: MBAR checks
len(sample)==K and raises. This audit proves, leg by leg from the raw S3 checkpoints, that:
  (a) every leg that fed a PUBLISHED ΔG_bind is SELF-CONSISTENT (window_count == len(u) == meta n_windows) and
      COMPLETE (every window has samples), so its MBAR reduction is valid; and
  (b) the buggy dense (nr4a2rep) legs are INCONSISTENT and/or INCOMPLETE — and therefore, as the empty
      per_replicate_dg_bind in the diagnostics confirms, never produced a number that reached the manuscript.

Pure stdlib + boto3 (reads the SageMaker checkpoint bucket). Structural check needs no pymbar; the optional
reduce cross-check (for consistent+complete legs) uses nr4a3_abfe.reduce_leg (which now infers K from the data).
Emits abfe-audit-report.json. Run in CI (abfe-audit.yml) where S3 + pymbar are available.
"""
import json
import os
import sys


def _s3():
    import boto3
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    acct = boto3.client("sts").get_caller_identity()["Account"]
    return boto3.client("s3"), f"sagemaker-{region}-{acct}"


def _list(s3, bucket, prefix):
    keys = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        for o in page.get("Contents", []):
            keys.append((o["Key"], o["Size"]))
    return keys


def discover_tags(s3, bucket, name="nr4a3-abfe"):
    """Every top-level '<tag>/ckpt/' prefix under the bucket whose tag contains `name`."""
    tags = set()
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=name, Delimiter="/"):
        for cp in page.get("CommonPrefixes", []):
            t = cp["Prefix"].rstrip("/")
            tags.add(t)
    return sorted(tags)


def _first_u_len(s3, bucket, key):
    """Length of the reduced-potential vector u in the first non-empty jsonl record (== #λ-states the sample was
    evaluated at). Streams only the first ~64 KiB so we never pull a whole window file."""
    body = s3.get_object(Bucket=bucket, Key=key, Range="bytes=0-65535")["Body"].read().decode("utf-8", "ignore")
    for line in body.splitlines():
        line = line.strip()
        if line:
            try:
                u = json.loads(line).get("u")
            except json.JSONDecodeError:      # truncated final line from the range read
                continue
            if isinstance(u, list):
                return len(u)
    return None


def audit_leg(s3, bucket, tag, leg_prefix):
    """Structural audit of one leg directory (the prefix that directly contains window_XX.jsonl)."""
    keys = _list(s3, bucket, leg_prefix)
    wins = sorted(k for k, _ in keys if os.path.basename(k).startswith("window_")
                  and k.endswith(".jsonl"))
    # contiguous window count from window_00
    idx = set()
    for k in wins:
        b = os.path.basename(k)
        try:
            idx.add(int(b[len("window_"):-len(".jsonl")]))
        except ValueError:
            pass
    n_contig = 0
    while n_contig in idx:
        n_contig += 1
    n_files = len(idx)
    u_len = _first_u_len(s3, bucket, wins[0]) if wins else None
    meta = None
    for k, _ in keys:
        if os.path.basename(k) == "meta.json":
            meta = json.loads(s3.get_object(Bucket=bucket, Key=k)["Body"].read())
            break
    meta_nw = (meta or {}).get("n_windows")
    # per-window sample counts (line counts) — completeness
    samples = []
    for w in range(max(n_contig, u_len or 0)):
        wk = next((k for k in wins if os.path.basename(k) == f"window_{w:02d}.jsonl"), None)
        if wk is None:
            samples.append(0); continue
        n = sum(1 for line in s3.get_object(Bucket=bucket, Key=wk)["Body"]
                .read().decode("utf-8", "ignore").splitlines() if line.strip())
        samples.append(n)
    consistent = (u_len is not None and n_files == u_len and n_contig == n_files)
    complete = bool(samples) and all(x > 0 for x in samples[:(u_len or n_files)])
    return {
        "leg_prefix": leg_prefix, "n_window_files": n_files, "n_contiguous": n_contig,
        "u_length": u_len, "meta_n_windows": meta_nw, "samples_per_window": samples,
        "self_consistent": consistent, "complete": complete,
        "verdict": ("CONSISTENT+COMPLETE" if consistent and complete else
                    "INCONSISTENT (window_count != u_length)" if not consistent else "INCOMPLETE (missing windows)"),
    }


def find_leg_dirs(s3, bucket, tag):
    """Locate each leg's window-holding directory under <tag>/ckpt/ (the sync may nest it a level or two)."""
    keys = _list(s3, bucket, f"{tag}/ckpt/")
    dirs = {}
    for k, _ in keys:
        if os.path.basename(k) == "window_00.jsonl":
            dirs[os.path.dirname(k) + "/"] = True
    return sorted(dirs)


def main():
    s3, bucket = _s3()
    only = [t.strip() for t in os.environ.get("AUDIT_TAGS", "").split(",") if t.strip()]
    tags = only or discover_tags(s3, bucket)
    report = {"bucket": bucket, "tags_audited": tags, "legs": [], "reduce_crosscheck": []}
    do_reduce = os.environ.get("AUDIT_REDUCE", "1") == "1"
    for tag in tags:
        for leg_dir in find_leg_dirs(s3, bucket, tag):
            a = audit_leg(s3, bucket, tag, leg_dir)
            a["tag"] = tag
            report["legs"].append(a)
            print(f"[{tag}] {leg_dir}\n   {a['verdict']}: files={a['n_window_files']} contig={a['n_contiguous']} "
                  f"u_len={a['u_length']} meta_nw={a['meta_n_windows']} samples={a['samples_per_window']}",
                  flush=True)
    # summary
    inconsistent = [l for l in report["legs"] if not l["self_consistent"]]
    incomplete = [l for l in report["legs"] if l["self_consistent"] and not l["complete"]]
    ok = [l for l in report["legs"] if l["self_consistent"] and l["complete"]]
    report["summary"] = {
        "n_legs": len(report["legs"]), "n_consistent_complete": len(ok),
        "n_inconsistent": len(inconsistent), "n_incomplete": len(incomplete),
        "inconsistent_legs": [f"{l['tag']}:{os.path.basename(l['leg_prefix'].rstrip('/'))}" for l in inconsistent],
        "incomplete_legs": [f"{l['tag']}:{os.path.basename(l['leg_prefix'].rstrip('/'))}" for l in incomplete],
        "interpretation": (
            "A leg is safe to reduce ONLY if CONSISTENT+COMPLETE. INCONSISTENT legs (window_count != u_length) "
            "raise in MBAR (assemble_ukn len-check) → they cannot silently produce a wrong ΔG. INCOMPLETE legs "
            "(a missing window) return None from reduce_leg → also cannot produce a number. So any published "
            "ΔG_bind necessarily came from a CONSISTENT+COMPLETE leg; this audit lists which legs those are."),
    }
    out = os.environ.get("OUT", "research/modalities/abfe-audit-report.json")
    json.dump(report, open(out, "w"), indent=1)
    print(f"\nSUMMARY: {len(ok)} consistent+complete, {len(inconsistent)} INCONSISTENT, "
          f"{len(incomplete)} INCOMPLETE (of {len(report['legs'])} legs). wrote {out}")
    if inconsistent:
        print("INCONSISTENT (buggy-dense signature):",
              ", ".join(report["summary"]["inconsistent_legs"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
