#!/usr/bin/env python3
"""
Reproducibility archival: mirror durable SageMaker result artifacts from the ephemeral S3 default
bucket into git (permanent, versioned, DOI-able), and diagnose the bucket's lifecycle so we know WHY
old results were lost.

MOTIVATION (2026-07-10). GPU jobs write to s3://sagemaker-us-east-2-<acct>/<prefix>/ and the
report-*-aws.yml workflows only PRINT — they commit nothing. Old raw outputs (the DiffSBDD generation
pools nr4a3-denovo*.json, the nr4a3-matrix docking poses) were LOST, almost certainly to an S3
lifecycle expiration. The ~55 curated summary JSONs in research/modalities/*.json survived because they
were hand-committed; everything else was S3-only and at risk. This module makes result persistence
automatic: it selects the small, durable artifacts (JSON/txt/dat/HILLS/COLVAR/small PDB/SDF/manifests),
downloads them, and stages them under results/<prefix>/ for a git commit; it EXCLUDES scratch
(fpocket pocket*.pdb/pqr, PyMOL/VMD scaffolding) and lists oversize artifacts (trajectories) for a
separate large-artifact archive (Zenodo) rather than bloating git.

Pure logic (classify_object / build_manifest / durable_name) is import-safe and unit-tested; the S3
driver (main) needs boto3 + AWS creds and runs in the archive-results-aws.yml GH-runner job.
"""
import json
import os
import sys

# Size cap: files at/under this go into git; larger ones are manifested as "too-big" (Zenodo).
DEFAULT_CAP_BYTES = 5 * 1024 * 1024  # 5 MB

# Extensions we consider durable, publishable result artifacts (small).
DURABLE_EXT = {
    ".json", ".txt", ".csv", ".tsv", ".dat", ".md", ".yaml", ".yml", ".log",
    ".sdf", ".mol2", ".pdb", ".pdbqt", ".xml", ".colvar", ".hills", ".fasta", ".seq",
}
# Name-based durable matches (extensionless or convention files worth keeping).
DURABLE_NAMES = ("HILLS", "COLVAR", "manifest")
DURABLE_NAME_SUBSTR = ("fes", "_info.txt", "_summary", "manifest")

# Large research artifacts (trajectories, arrays): too big for git, but they ARE load-bearing for the
# DOI archive, so they are flagged 'too-big' (→ Zenodo), never silently skipped.
LARGE_ARTIFACT_EXT = {".dcd", ".nc", ".xtc", ".trr", ".h5", ".hdf5", ".npz", ".npy", ".mdcrd", ".chk"}

# Scratch / regenerable-viewer junk we must NOT archive (this is what bloats S3 + git).
SCRATCH_SUBSTR = (
    "/fpocket_runs/",       # per-conformer fpocket scratch trees
    "/pockets/",            # pocket*_atm.pdb / pocket*_vert.pqr
    "_out/",                # fpocket *_out/ viewer scaffolding
    "/redock_work/",        # dock scratch
    "/.ipynb_checkpoints/",
)
SCRATCH_SUFFIX = (".pml", ".tcl", "_PYMOL.sh", "_VMD.sh", ".pqr", ".sagemaker-uploaded")


def _ext(key):
    base = key.rsplit("/", 1)[-1]
    dot = base.rfind(".")
    return base[dot:].lower() if dot > 0 else ""


def _is_scratch(key):
    if any(s in key for s in SCRATCH_SUBSTR):
        return True
    if any(key.endswith(s) for s in SCRATCH_SUFFIX):
        return True
    return False


def durable_name(key):
    """True if the basename matches a durable convention even without a durable extension."""
    base = key.rsplit("/", 1)[-1]
    if any(base == n or base.startswith(n) for n in DURABLE_NAMES):
        return True
    if any(s in base for s in DURABLE_NAME_SUBSTR):
        return True
    return False


def classify_object(key, size, cap_bytes=DEFAULT_CAP_BYTES):
    """Classify one S3 object: 'archive' (commit to git), 'too-big' (Zenodo), 'scratch', or 'skip'.

    Order matters: scratch is rejected before anything else so viewer junk never reaches git even if it
    has a durable-looking extension (e.g. a pocket .pdb)."""
    if key.endswith("/") or size == 0:
        return "skip"
    if _is_scratch(key):
        return "scratch"
    ext = _ext(key)
    if ext in LARGE_ARTIFACT_EXT:
        return "too-big"   # trajectories/arrays: Zenodo, never git, never dropped
    if ext not in DURABLE_EXT and not durable_name(key):
        return "skip"
    if size > cap_bytes:
        return "too-big"
    return "archive"


def build_manifest(objects, cap_bytes=DEFAULT_CAP_BYTES):
    """objects: iterable of (key, size). Returns a manifest dict with per-object action + totals."""
    entries, totals = [], {"archive": 0, "too-big": 0, "scratch": 0, "skip": 0}
    archive_bytes = 0
    for key, size in objects:
        action = classify_object(key, size, cap_bytes)
        entries.append({"key": key, "size": int(size), "action": action})
        totals[action] += 1
        if action == "archive":
            archive_bytes += int(size)
    return {
        "n_objects": len(entries),
        "totals": totals,
        "archive_bytes": archive_bytes,
        "cap_bytes": cap_bytes,
        "objects": entries,
    }


# ---- S3 driver (needs boto3 + creds; not exercised by unit tests) -----------------------------------

def _list_prefix(s3, bucket, prefix):
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            yield obj["Key"], obj["Size"]


def _diagnose(s3, bucket):
    print(f"[diagnose] bucket lifecycle for s3://{bucket}", flush=True)
    try:
        cfg = s3.get_bucket_lifecycle_configuration(Bucket=bucket)
        print(json.dumps(cfg.get("Rules", []), indent=2, default=str), flush=True)
        print("[diagnose] ^ a rule with an Expiration/Days that matches the result prefixes is the "
              "root cause of the lost outputs.", flush=True)
    except Exception as e:  # NoSuchLifecycleConfiguration or access error
        print(f"[diagnose] no lifecycle configuration returned ({type(e).__name__}: {e}) — "
              "if outputs still vanished, check bucket policy / manual deletion / a different bucket.",
              flush=True)


def main():
    import boto3
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3 = boto3.client("s3", region_name=region)
    bucket = os.environ.get("BUCKET") or boto3.session.Session().region_name and \
        f"sagemaker-{region}-{boto3.client('sts').get_caller_identity()['Account']}"
    bucket = os.environ.get("BUCKET", bucket)
    out_root = os.environ.get("OUTPUT_DIR", "results")
    cap = int(os.environ.get("CAP_BYTES", "").strip() or DEFAULT_CAP_BYTES)
    mode = os.environ.get("MODE", "archive").strip().lower()

    print(f"[archive] bucket={bucket} region={region} mode={mode} cap={cap}", flush=True)
    if mode == "diagnose":
        _diagnose(s3, bucket)
        prefixes = [p.strip() for p in os.environ.get("PREFIXES", "").split(",") if p.strip()]
        for pfx in prefixes:
            objs = list(_list_prefix(s3, bucket, pfx))
            man = build_manifest(objs, cap)
            print(f"[diagnose] {pfx}: {man['totals']} ({man['n_objects']} objs)", flush=True)
        return

    prefixes = [p.strip() for p in os.environ.get("PREFIXES", "").split(",") if p.strip()]
    if not prefixes:
        sys.exit("archive: set PREFIXES (comma-separated S3 prefixes)")
    grand = {}
    for pfx in prefixes:
        objs = list(_list_prefix(s3, bucket, pfx))
        if not objs:
            print(f"[archive] {pfx}: EMPTY (nothing in S3 — likely lost/expired)", flush=True)
            grand[pfx] = {"empty": True}
            continue
        man = build_manifest(objs, cap)
        dest_root = os.path.join(out_root, pfx.rstrip("/"))
        os.makedirs(dest_root, exist_ok=True)
        n = 0
        for e in man["objects"]:
            if e["action"] != "archive":
                continue
            rel = e["key"][len(pfx):].lstrip("/") if e["key"].startswith(pfx) else e["key"].rsplit("/", 1)[-1]
            dest = os.path.join(dest_root, rel)
            os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
            s3.download_file(bucket, e["key"], dest)
            n += 1
        with open(os.path.join(dest_root, "MANIFEST.json"), "w") as fh:
            json.dump(man, fh, indent=2)
        print(f"[archive] {pfx}: committed {n} files ({man['totals']}); "
              f"{man['totals']['too-big']} too-big → Zenodo", flush=True)
        grand[pfx] = man["totals"]
    print("[archive] summary: " + json.dumps(grand), flush=True)


if __name__ == "__main__":
    main()
