#!/usr/bin/env python3
"""Read-only provenance check: are the opened receptor conformers the SAME across S3 prefixes?

The repurposing screen reused cached opened conformers (nr4a3-matrix/<tag>-opened.pdb). To blend it with
the existing decoy-null work we must show the cache is the SAME conformer the decoy null used. Extraction is
deterministic (nr4a3_warhead.extract_opened_conformer: max-fpocket-druggability frame over a fixed
N_FPOCKET_FRAMES=25 linspace of each paralogue's *-metad trajectory), so identical metad inputs -> identical
frame. This confirms it empirically: for each prefix it prints each paralogue's recorded opened_frame +
druggability (from <prefix>/nr4a3-matrix.json) and the MD5 of each <tag>-opened.pdb, then flags whether the
conformers match across prefixes.

Env: PREFIXES (comma list of S3 prefixes to compare), BUCKET (optional), AWS creds + AWS_DEFAULT_REGION.
"""
import hashlib
import json
import os
import sys


def _s3():
    import boto3
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3, sts = boto3.client("s3"), boto3.client("sts")
    acct = sts.get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    return s3, bucket


def _get(s3, bucket, key):
    try:
        return s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    except Exception:  # noqa: BLE001
        return None


def main():
    s3, bucket = _s3()
    prefixes = [p.strip() for p in os.environ.get("PREFIXES", "").split(",") if p.strip()]
    if not prefixes:
        sys.exit("set PREFIXES (comma list)")
    tags = ["nr4a1", "nr4a2", "nr4a3"]
    md5s = {t: {} for t in tags}          # tag -> {prefix: md5}
    for p in prefixes:
        print(f"\n=== {p} ===")
        mj = _get(s3, bucket, f"{p}/nr4a3-matrix.json")
        if mj:
            try:
                d = json.loads(mj)
                for name, info in (d.get("paralogues") or {}).items():
                    print(f"  {name:<6} opened_frame={info.get('opened_frame')!s:<8} "
                          f"druggability={info.get('fpocket_druggability')}")
            except ValueError:
                print("  (nr4a3-matrix.json unparseable)")
        else:
            print("  (no nr4a3-matrix.json)")
        for t in tags:
            b = _get(s3, bucket, f"{p}/{t}-opened.pdb")
            if b is not None:
                h = hashlib.md5(b).hexdigest()
                md5s[t][p] = h
                print(f"  {t}-opened.pdb  md5={h}  ({len(b)} bytes)")
            else:
                print(f"  {t}-opened.pdb  MISSING")

    print("\n=== conformer identity across prefixes (per paralogue) ===")
    for t in tags:
        hs = md5s[t]
        uniq = set(hs.values())
        if not hs:
            print(f"  {t}: (none found)")
        elif len(uniq) == 1 and len(hs) > 1:
            print(f"  {t}: IDENTICAL across {len(hs)} prefixes ({next(iter(uniq))[:12]}…)")
        elif len(hs) == 1:
            print(f"  {t}: only in {list(hs)[0]} — can't compare")
        else:
            print(f"  {t}: DIFFER — " + "; ".join(f"{k.split('/')[-1]}={v[:12]}…" for k, v in hs.items()))


if __name__ == "__main__":
    main()
