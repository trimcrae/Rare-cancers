#!/usr/bin/env python3
"""IMMUTABLE PROVENANCE MANIFEST for every ABFE leg that could back a published ΔG (reviewer §7).

Motivation (2026-07-11): the audit (abfe_audit.py) proves each leg is structurally + semantically trustworthy.
To *strengthen toward* "no published value could have been corrupted" the reviewer additionally wants an
immutable manifest mapping every leg's S3 objects → their **VersionIds + SHA-256 hashes**, plus the run
provenance (commit SHA, schedule, target, replicate, leg, checkpoint ancestry) read from meta.json. Together
with the audit, a reader can (a) confirm the exact bytes behind a reproduced value, (b) confirm the object was
not silently overwritten (a VersionId of "null" ⇒ the bucket had versioning DISABLED — flagged), and (c) tie
the value to a specific commit + configuration.

HONESTY: this file NEVER fabricates a hash, VersionId, ΔG, or force-field version. Fields we cannot read at
audit time (container/image digest, conda env digest, force-field/param versions, RNG entropy) are emitted as
explicit "TODO: capture at run time" placeholders — they must be captured by the RUN (entry_abfe.py) and written
into meta.json, not invented here. The manifest records only what is actually present.

Pure boto3 (imported lazily, inside the S3 functions, so the module imports clean and the pure hashing/merge
helpers unit-test WITHOUT boto3). Runs later in CI (S3 + creds available); `python abfe_manifest.py` writes
abfe-manifest.json. The pure helpers (sha256_bytes / sha256_stream / merge_leg_records / build_manifest_doc)
are covered by tests/test_abfe_audit.py with synthetic bytes.
"""
import hashlib
import json
import os
import sys

# Provenance fields that CANNOT be read from S3/meta.json at audit time — must be captured by the RUN. Emitted
# as explicit placeholders so their absence is visible, never silently blank or fabricated.
_RUNTIME_PLACEHOLDERS = {
    "container_image_digest": "TODO: capture at run time (ECR image URI@sha256 in entry_abfe.py)",
    "conda_env_digest": "TODO: capture at run time (hash of the solved abfe env / environment-abfe.yml lock)",
    "forcefield_versions": "TODO: capture at run time (amber14SB / gaff-2.11 / tip3p versions used by prepare_leg)",
    "openmm_version": "TODO: capture at run time",
    "pymbar_version": "TODO: capture at run time",
}

# meta.json keys that ARE run provenance we can read directly (present-or-absent, never fabricated).
_META_PROVENANCE_KEYS = ("commit", "commit_sha", "git_ref", "leg", "receptor", "target", "seed", "pose_index",
                         "n_windows", "lambda_schedule", "schedule", "temperature_K", "restraint_standard_state_dg")


def sha256_bytes(b):
    """SHA-256 hex digest of a bytes object."""
    return hashlib.sha256(b).hexdigest()


def sha256_stream(chunks):
    """SHA-256 hex digest over an ITERABLE of byte chunks (so a large S3 object is hashed by streaming
    get_object()['Body'].iter_chunks() without buffering the whole object in memory)."""
    h = hashlib.sha256()
    total = 0
    for chunk in chunks:
        if not chunk:
            continue
        b = chunk if isinstance(chunk, (bytes, bytearray)) else bytes(chunk)
        h.update(b)
        total += len(b)
    return h.hexdigest(), total


def merge_leg_records(records):
    """Merge a list of per-object records for ONE leg into that leg's manifest entry: a stable sha-of-shas
    'content_fingerprint' (independent of listing order) + a versioning-disabled flag if any object's VersionId
    is null/absent. Pure — no boto3. Each record: {key, version_id, sha256, size, last_modified}."""
    ordered = sorted(records, key=lambda r: r["key"])
    combined = hashlib.sha256()
    versioning_disabled = False
    for r in ordered:
        vid = r.get("version_id")
        if vid in (None, "", "null"):
            versioning_disabled = True
        combined.update((r["key"] + "\0" + str(r.get("sha256", "")) + "\0" + str(vid) + "\n").encode("utf-8"))
    return {
        "objects": ordered,
        "n_objects": len(ordered),
        "content_fingerprint": combined.hexdigest(),
        "versioning_disabled": versioning_disabled,
    }


def build_manifest_doc(bucket, legs, runtime_placeholders=None):
    """Assemble the top-level manifest document from per-leg entries. Pure (no boto3) so it unit-tests with
    synthetic leg entries. `legs` = {leg_id: {...merge_leg_records output..., 'provenance': {...}}}."""
    placeholders = dict(_RUNTIME_PLACEHOLDERS)
    if runtime_placeholders:
        placeholders.update(runtime_placeholders)
    any_versioning_disabled = any(v.get("versioning_disabled") for v in legs.values())
    return {
        "schema": "abfe-manifest/v1",
        "bucket": bucket,
        "legs": legs,
        "runtime_provenance_placeholders": placeholders,
        "versioning_disabled_anywhere": any_versioning_disabled,
        "note": ("Immutable per-leg S3 provenance (VersionId + SHA-256) + run provenance from meta.json. "
                 "Fields under runtime_provenance_placeholders are NOT read here — they must be captured by the "
                 "run (entry_abfe.py → meta.json) and are shown as explicit TODOs, never fabricated. "
                 "versioning_disabled=true on a leg means S3 returned no real VersionId (bucket versioning off) "
                 "→ that leg's objects are NOT provably un-overwritten."),
    }


# ---- S3 layer (boto3, lazy-imported so the module + pure helpers work without boto3) ---------------------
def _s3():
    import boto3
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    acct = boto3.client("sts").get_caller_identity()["Account"]
    return boto3.client("s3"), f"sagemaker-{region}-{acct}"


def _list_leg_dirs(s3, bucket, tag):
    """Every leg directory (prefix holding window_00.jsonl) under <tag>/ckpt/."""
    dirs = {}
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=f"{tag}/ckpt/"):
        for o in page.get("Contents", []):
            if os.path.basename(o["Key"]) == "window_00.jsonl":
                dirs[os.path.dirname(o["Key"]) + "/"] = True
    return sorted(dirs)


def _object_record(s3, bucket, key):
    """One object's provenance: latest VersionId (list_object_versions) + streamed SHA-256 + size + mtime.
    Falls back to head_object when versioning is off (VersionId → 'null')."""
    version_id = None
    last_modified = None
    try:
        resp = s3.list_object_versions(Bucket=bucket, Prefix=key, MaxKeys=1)
        for v in resp.get("Versions", []):
            if v["Key"] == key and v.get("IsLatest"):
                version_id = v.get("VersionId")
                last_modified = str(v.get("LastModified"))
                break
    except Exception:  # noqa: BLE001 — versioning may be denied/off; head_object still gives us the rest
        pass
    obj = s3.get_object(Bucket=bucket, Key=key)
    if version_id is None:
        version_id = obj.get("VersionId")            # 'null' when versioning disabled
        last_modified = str(obj.get("LastModified"))
    digest, size = sha256_stream(obj["Body"].iter_chunks())
    return {"key": key, "version_id": version_id, "sha256": digest, "size": size,
            "last_modified": last_modified}


def _read_meta(s3, bucket, leg_prefix):
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=leg_prefix):
        for o in page.get("Contents", []):
            if os.path.basename(o["Key"]) == "meta.json":
                try:
                    return json.loads(s3.get_object(Bucket=bucket, Key=o["Key"])["Body"].read())
                except Exception:  # noqa: BLE001
                    return None
    return None


def _leg_provenance(meta):
    """Run provenance we CAN read from meta.json (present-or-absent, never fabricated) + checkpoint-ancestry
    placeholder if not recorded."""
    meta = meta or {}
    prov = {k: meta.get(k) for k in _META_PROVENANCE_KEYS if k in meta}
    prov.setdefault("checkpoint_ancestry",
                    meta.get("checkpoint_ancestry",
                             "TODO: capture at run time (spot-resume lineage / prior checkpoint prefixes)"))
    prov["meta_present"] = bool(meta)
    return prov


def build_manifest(s3, bucket, tags):
    """Walk every leg under each tag → per-object VersionId + SHA-256 + per-leg run provenance → manifest doc."""
    legs = {}
    for tag in tags:
        for leg_dir in _list_leg_dirs(s3, bucket, tag):
            records = []
            for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=leg_dir):
                for o in page.get("Contents", []):
                    records.append(_object_record(s3, bucket, o["Key"]))
            entry = merge_leg_records(records)
            entry["tag"] = tag
            entry["leg_prefix"] = leg_dir
            entry["provenance"] = _leg_provenance(_read_meta(s3, bucket, leg_dir))
            legs[leg_dir] = entry
            print(f"[manifest] {leg_dir}: {entry['n_objects']} objects, "
                  f"fingerprint={entry['content_fingerprint'][:12]}…, "
                  f"versioning_disabled={entry['versioning_disabled']}", flush=True)
    return build_manifest_doc(bucket, legs)


def main():
    s3, bucket = _s3()
    tags = [t.strip() for t in os.environ.get("MANIFEST_TAGS", "").split(",") if t.strip()]
    if not tags:
        # discover nr4a3-abfe* tags the same way the audit does
        tags = set()
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix="nr4a3-abfe", Delimiter="/"):
            for cp in page.get("CommonPrefixes", []):
                tags.add(cp["Prefix"].rstrip("/"))
        tags = sorted(tags)
    doc = build_manifest(s3, bucket, tags)
    out = os.environ.get("OUT", "research/modalities/abfe-manifest.json")
    with open(out, "w") as f:
        json.dump(doc, f, indent=1)
    print(f"[manifest] wrote {out}: {len(doc['legs'])} legs, "
          f"versioning_disabled_anywhere={doc['versioning_disabled_anywhere']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
