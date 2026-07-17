#!/usr/bin/env python3
"""S3 checkpoint census for the Modal step1 RBFE pilot — live progress of a detached/remote leg.

The Modal real leg commits spot-safe checkpoints to s3://<bucket>/<prefix>/<leg>/<phase>/iter-XXXXXXXX/<hash>/
(warmup: equilibration.nc/.chk; production: simulation.nc/checkpoint.chk + COMMITTED.json), so the FURTHEST
committed iteration per (leg, phase) IS the live progress — the same census the GCP tail reads from GCS. Also
reports any finished leg / ddg result JSON. Pure boto3; runs on a CI runner with the repo AWS creds (the dev
sandbox can't reach S3). Read-only — never deletes.
"""
from __future__ import annotations

import os
import re
import sys

BUCKET = os.environ.get("S3_BUCKET", "sagemaker-us-east-2-646605541856")
PREFIX = os.environ.get("CKPT_PREFIX", "nr4a3-step1-pilot-rbfe").rstrip("/")
ITER_RE = re.compile(r"/iter-(\d+)/")


def main() -> int:
    import boto3

    s3 = boto3.client("s3")
    keys = []
    token = None
    while True:
        kw = {"Bucket": BUCKET, "Prefix": PREFIX + "/"}
        if token:
            kw["ContinuationToken"] = token
        r = s3.list_objects_v2(**kw)
        keys += [(o["Key"], o["Size"], o["LastModified"]) for o in r.get("Contents", [])]
        if not r.get("IsTruncated"):
            break
        token = r["NextContinuationToken"]

    print(f"=== census s3://{BUCKET}/{PREFIX}/  ({len(keys)} objects) ===", flush=True)
    if not keys:
        print("  (nothing yet — leg still staging/equilibrating, or checkpoints not committed yet)", flush=True)
        return 0

    # furthest committed iteration per (leg, phase)
    prog: dict = {}
    committed = []
    latest = None
    for k, sz, lm in keys:
        m = ITER_RE.search(k)
        # leg/phase = the path segments before /iter-
        seg = k[len(PREFIX) + 1:].split("/")
        lp = "/".join(seg[:2]) if len(seg) >= 2 else seg[0]
        if m:
            it = int(m.group(1))
            prog[lp] = max(prog.get(lp, 0), it)
        if k.endswith("COMMITTED.json"):
            committed.append((lm, k))
        if latest is None or lm > latest[0]:
            latest = (lm, k, sz)

    print("--- furthest committed iteration per leg/phase (live progress) ---", flush=True)
    for lp in sorted(prog):
        print(f"  {lp}: iter {prog[lp]:08d}", flush=True)
    print(f"--- total committed boundaries: {len(committed)} ---", flush=True)
    if latest:
        print(f"--- most-recent object: {latest[0].isoformat()}  {latest[2]} B  {latest[1]} ---", flush=True)

    # finished leg / ddg results
    res = [k for k, _, _ in keys if "/results/" in k and k.endswith(".json")]
    print(f"--- result JSONs: {res if res else '(none yet — leg not finished)'} ---", flush=True)
    for k in res:
        body = s3.get_object(Bucket=BUCKET, Key=k)["Body"].read().decode("utf-8", "replace")
        print(f"  {k}:\n    {body[:600]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
