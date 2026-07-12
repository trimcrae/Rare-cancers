#!/usr/bin/env python3
"""
Provider-agnostic checkpoint store. Rented-GPU providers (RunPod/Vast/Salad/Modal) are STATELESS compute — the
job's state (inputs + per-unit checkpoints) must live in a cloud bucket that every provider reads/writes, so a
node dropping (or a whole provider swap) never loses work. Any S3-compatible bucket works via the SAME boto3
code — just change the endpoint:

  * AWS S3            — what SageMaker already uses; egress ~$0.09/GB.
  * Cloudflare R2     — S3-compatible, **$0 egress** (big deal: trajectories/checkpoints move a lot). Free tier
                        10 GB. endpoint_url = https://<acct>.r2.cloudflarestorage.com
  * Backblaze B2      — S3-compatible, very cheap, free egress to Cloudflare. endpoint_url = https://s3.<region>.backblazeb2.com

Recommendation: put the checkpoint bucket on **Cloudflare R2** so cross-provider traffic is free — the compute
moves between providers but the state stays in one zero-egress bucket.

Pure-logic helpers (URI parse, per-unit key layout, resume set) are unit-tested; put/get/list need boto3 +
creds and are guarded so they fail loudly off-cloud.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def parse_uri(uri: str):
    """s3://bucket/prefix/path -> (bucket, key). Works for any S3-compatible endpoint (scheme is ignored)."""
    body = uri.split("://", 1)[1] if "://" in uri else uri
    bucket, _, key = body.partition("/")
    return bucket, key


def checkpoint_key(prefix: str, unit: str) -> str:
    """Per-unit checkpoint object key. `unit` = a window/replica id, so a job checkpoints per unit and can
    resume by skipping units already present (the continuous-upload contract our jobs already follow)."""
    return f"{prefix.rstrip('/')}/units/{unit}.ckpt"


def completed_units(keys: list, prefix: str) -> set:
    """Given a listing of existing object keys under `prefix`, return the set of unit ids already checkpointed
    (so a resuming job skips them). Pure — drives resume without re-running finished windows."""
    tag = f"{prefix.rstrip('/')}/units/"
    out = set()
    for k in keys:
        if k.startswith(tag) and k.endswith(".ckpt"):
            out.add(k[len(tag):-len(".ckpt")])
    return out


@dataclass
class ObjectStore:
    """Thin S3-compatible client. endpoint_url selects the provider (None => AWS S3; an R2/B2 URL => those)."""
    endpoint_url: str | None = None
    region: str | None = None

    def _client(self):
        try:
            import boto3
        except ImportError:
            raise RuntimeError("object_store needs boto3 (present on any provider container / CI).")
        # credentials come from the standard env (AWS_ACCESS_KEY_ID/SECRET for S3; R2/B2 issue S3-style keys).
        return boto3.client("s3", endpoint_url=self.endpoint_url, region_name=self.region)

    def put(self, uri: str, data: bytes):
        b, k = parse_uri(uri)
        self._client().put_object(Bucket=b, Key=k, Body=data)

    def get(self, uri: str) -> bytes:
        b, k = parse_uri(uri)
        return self._client().get_object(Bucket=b, Key=k)["Body"].read()

    def list(self, uri: str) -> list:
        b, prefix = parse_uri(uri)
        cl = self._client()
        keys, token = [], None
        while True:
            kw = {"Bucket": b, "Prefix": prefix}
            if token:
                kw["ContinuationToken"] = token
            r = cl.list_objects_v2(**kw)
            keys += [o["Key"] for o in r.get("Contents", [])]
            if not r.get("IsTruncated"):
                return keys
            token = r["NextContinuationToken"]

    def resume_set(self, checkpoint_uri: str) -> set:
        """Which units are already done under this job's checkpoint prefix (for resume)."""
        _, prefix = parse_uri(checkpoint_uri)
        return completed_units(self.list(checkpoint_uri), prefix)


def store_from_env() -> ObjectStore:
    """Build the store from env: OBJECT_STORE_ENDPOINT (R2/B2 url; empty => AWS S3) + OBJECT_STORE_REGION."""
    return ObjectStore(endpoint_url=os.environ.get("OBJECT_STORE_ENDPOINT") or None,
                       region=os.environ.get("OBJECT_STORE_REGION") or None)
