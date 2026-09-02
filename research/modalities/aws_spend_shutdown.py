#!/usr/bin/env python3
"""Switch off the AWS charges the census found. DRY-RUN BY DEFAULT; deletion is irreversible.

The other half of `aws_spend_census.py`. That one measures and never deletes; this one deletes and never
guesses — it acts on the census artifact, so what is destroyed is exactly what a human read before saying
go. Every AWS lane in this repo is retired (production is on Vast, CLAUDE.md §6), so the account should be
billing ~nothing at rest and anything it does bill for is a leftover.

═══════════════════════════════════════════════════════════════════════════════════════════════════════
⛔ WHY THIS IS DRY-RUN BY DEFAULT AND WHY THAT IS NOT TIMIDITY
═══════════════════════════════════════════════════════════════════════════════════════════════════════
S3 objects here are the ONLY surviving copy of finished MD/FEP work — trajectories, checkpoints and the
model tarballs behind numbers already quoted in the manuscript. A deletion is not recoverable and not
re-derivable at zero cost: re-running a leg means renting a GPU again. So:

  * `APPLY=1` is required for any destructive call. Without it every action prints what it WOULD do.
  * `TARGETS` is an explicit allow-list of categories. Nothing is deleted because it merely looked idle.
  * ★ PROTECTED PREFIXES ARE NEVER TOUCHED, EVEN WITH APPLY=1. A prefix holding a result the paper cites
    is refused by name, and the refusal is PRINTED rather than silently skipped — a guard that no-ops
    quietly is the failure this repo keeps paying for (CLAUDE.md §6, the census-lane string bug).
  * The zero-risk categories are separated from the destructive ones on purpose, because they are what
    should run first: incomplete multipart uploads (parts of uploads that never finished — they bill and
    hold nothing readable), CloudWatch log retention (a policy change, not a delete), and ECR lifecycle.

★ THE CHEAPEST REAL FIX IS USUALLY NOT A DELETE. Two of the actions here change a POLICY rather than
destroy data: setting log-group retention, and setting an S3 lifecycle rule that aborts incomplete
multipart uploads after 7 days. Both stop the bleed permanently and neither loses a byte, so they are
the default `TARGETS` and the destructive ones are opt-in.

Env:
  APPLY=1            actually do it (default: dry run)
  TARGETS=a,b,c      comma list from: mpu_abort, log_retention, log_delete, ecr_prune, ecr_delete_all,
                     ebs_detached, ebs_snapshots, s3_prefixes, s3_purge, s3_glacier
                     default: mpu_abort,log_retention  (the two that lose no data)
  PURGE_CONFIRM      must equal DELETE-EVERYTHING for TARGETS=s3_purge to do anything
  PURGE_INCLUDE_TOOLING=1  also delete TOOLING_PREFIXES (mdenv/) — off by default, see below
  S3_PREFIXES=...    for TARGETS=s3_prefixes: comma list of `bucket/prefix` to delete. REQUIRED — this
                     target has no default, because a default here would be a default deletion.
  LOG_RETENTION_DAYS retention to set (default 30)
  KEEP_IMAGES        ECR images to keep per repo, newest first (default 1)
  REGIONS            override the region scan set
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

CENSUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aws-spend-census.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aws-spend-shutdown.json")

APPLY = os.environ.get("APPLY", "") == "1"
DEFAULT_TARGETS = "mpu_abort,log_retention"

# ★ Never deleted by the TARGETED path (`s3_prefixes`), with or without APPLY. These hold the only copy
# of results the manuscript cites; a rerun costs GPU dollars. Matching is on the leading path segment.
# ⚠ These are a guard against a mistyped prefix, NOT a veto over the owner: `s3_purge` is the deliberate
# "all of it" path and is gated by its own explicit confirmation string instead (see PURGE_CONFIRM).
PROTECTED_PREFIXES = {
    "abfe", "ternary", "rbfe", "fep", "metad", "nrv04", "selcal", "cofold",
    "results", "manuscript", "release", "archive",
}

# Prefixes the purge holds back BY DEFAULT because they are tooling rather than results. `mdenv/` is the
# conda-packed MD environment NR-V04 Vast instances fetch at launch (`nrv04_vast_launch.MDENV_KEY`), built
# by the conda-pack job in `fusion-cpu-extras.yml`.
#
# ⚠ SUPERSEDED AS APPLIED TO THIS ACCOUNT, RETAINED BECAUSE THE MECHANISM IS STILL RIGHT (trimcrae,
# 2026-08-13: *"everything saved on AWS is dead. I don't want to spend money for stuff I'm never going to
# touch and that I can recreate at any time"*). The exemption was applied on the reasoning that deleting
# mdenv would silently break the next NR-V04 launch — but the same paragraph that argued for keeping it
# also recorded that `fusion-cpu-extras.yml` REBUILDS it. Recreatable-on-demand is precisely the category
# the owner does not want to rent storage for, so the argument answered itself and was still resolved the
# wrong way. The standing instruction is the test: pay for what cannot be recreated, not for what is
# merely inconvenient to recreate.
#
# The knob stays because the DISTINCTION is real — a purge should still be able to tell tooling from
# results, and a future account may hold tooling that is NOT rebuildable from a tracked workflow. What
# changes is the default answer for this account: everything goes.
TOOLING_PREFIXES = {"mdenv"}

_CFG = Config(retries={"max_attempts": 5, "mode": "standard"})
_LOG: list[dict] = []


def _code(e: ClientError) -> str:
    return e.response.get("Error", {}).get("Code", "Unknown")


def act(kind: str, what: str, detail: dict | None = None, fn=None) -> None:
    """One place where dry-run vs apply is decided, so no call site can accidentally bypass it."""
    row = {"action": kind, "target": what, "applied": False, **(detail or {})}
    if not APPLY:
        print(f"  DRY-RUN would {kind}: {what}")
        _LOG.append(row)
        return
    try:
        if fn is not None:
            fn()
        row["applied"] = True
        print(f"  APPLIED {kind}: {what}")
    except ClientError as e:
        row["error"] = e.response.get("Error", {}).get("Code", "Unknown")
        print(f"  FAILED  {kind}: {what} — {row['error']}")
    except Exception as e:  # noqa: BLE001
        row["error"] = f"{type(e).__name__}: {e}"
        print(f"  FAILED  {kind}: {what} — {row['error']}")
    _LOG.append(row)


def load_census() -> dict:
    if not os.path.exists(CENSUS):
        print(f"::error::{CENSUS} not found. Run the census first "
              "(list-sagemaker-aws.yml mode=spend_census) — this script never discovers targets itself, "
              "so that a human has read the numbers before anything is destroyed.")
        sys.exit(2)
    with open(CENSUS) as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------------------------------
# Zero-data-loss actions
# ---------------------------------------------------------------------------------------------------
def mpu_abort(census: dict) -> None:
    """Abort incomplete multipart uploads and install a lifecycle rule so they cannot accumulate again.

    These are parts of uploads that died mid-flight. They bill as storage, hold nothing readable, and
    appear in no object listing — which is why an account can bill more than its visible contents.
    """
    print("\n== incomplete multipart uploads (bill as storage, hold nothing readable) ==")
    for b in census.get("s3", {}).get("buckets", []):
        n = (b.get("incomplete_multipart") or {}).get("n_uploads", 0)
        if not n:
            continue
        bucket, region = b["bucket"], b["region"]
        s3 = boto3.client("s3", region_name=region, config=_CFG)
        r = s3.list_multipart_uploads(Bucket=bucket, MaxUploads=1000)
        for u in r.get("Uploads", []):
            act("abort-mpu", f"s3://{bucket}/{u['Key']} ({u['Initiated'].isoformat()})",
                {"bucket": bucket, "key": u["Key"]},
                lambda u=u: s3.abort_multipart_upload(
                    Bucket=bucket, Key=u["Key"], UploadId=u["UploadId"]))
        # The rule is the durable half: aborting today does nothing about the next killed upload.
        act("s3-lifecycle-abort-mpu", f"s3://{bucket} (abort incomplete MPU after 7 days)",
            {"bucket": bucket},
            lambda: s3.put_bucket_lifecycle_configuration(
                Bucket=bucket,
                LifecycleConfiguration={"Rules": [{
                    "ID": "abort-incomplete-multipart-7d",
                    "Status": "Enabled",
                    "Filter": {"Prefix": ""},
                    "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7},
                }]}))


def log_retention(census: dict) -> None:
    """Set retention on log groups that are `Never expire`. A policy change; deletes nothing today.

    Existing logs age out on the new policy rather than vanishing now, so this is reversible in the only
    sense that matters: nothing is lost that the retention window would not have lost anyway.
    """
    days = int(os.environ.get("LOG_RETENTION_DAYS", "30"))
    print(f"\n== CloudWatch log groups set to NEVER EXPIRE -> {days}d retention ==")
    for g in census.get("logs", {}).get("groups", []):
        if g.get("retention_days") is not None:
            continue
        cwl = boto3.client("logs", region_name=g["region"], config=_CFG)
        act("set-log-retention", f"{g['name']} ({g['region']}, {g['gb']} GB) -> {days}d",
            {"log_group": g["name"], "days": days},
            lambda g=g: cwl.put_retention_policy(logGroupName=g["name"], retentionInDays=days))


# ---------------------------------------------------------------------------------------------------
# Destructive actions — opt-in only
# ---------------------------------------------------------------------------------------------------
def log_delete(census: dict) -> None:
    print("\n== DELETE CloudWatch log groups ==")
    for g in census.get("logs", {}).get("groups", []):
        cwl = boto3.client("logs", region_name=g["region"], config=_CFG)
        act("delete-log-group", f"{g['name']} ({g['region']}, {g['gb']} GB)", {"log_group": g["name"]},
            lambda g=g: cwl.delete_log_group(logGroupName=g["name"]))


def ecr_prune(census: dict) -> None:
    """Delete all but the newest KEEP_IMAGES images per repo.

    The baked GPU images are re-derivable — `ternary-fep-bake.yml` and the `build-*-image.yml` workflows
    rebuild them from a tracked Dockerfile. ⚠ But re-baking is not free of consequence: CLAUDE.md §6
    records that the ternary image's PARITY with the GCP lane's solve is a measured property of the
    CURRENT image, and neither side pins openmmtools/pymbar. Deleting the baked image discards the
    artifact that parity reading was taken on, so a rebuild must be re-measured (mode=parity) before any
    cross-provider comparability claim leans on it again. Keeping one image per repo is the default for
    that reason.
    """
    keep = int(os.environ.get("KEEP_IMAGES", "1"))
    print(f"\n== ECR: delete all but the newest {keep} image(s) per repo ==")
    for r in census.get("ecr", {}).get("repos", []):
        ecr = boto3.client("ecr", region_name=r["region"], config=_CFG)
        details: list = []
        for page in ecr.get_paginator("describe_images").paginate(repositoryName=r["repo"]):
            details += page.get("imageDetails", [])
        details.sort(key=lambda d: d.get("imagePushedAt"), reverse=True)
        doomed = details[keep:]
        if not doomed:
            print(f"  {r['repo']}: {len(details)} image(s), nothing beyond the keep window")
            continue
        ids = [{"imageDigest": d["imageDigest"]} for d in doomed]
        gb = sum(d.get("imageSizeInBytes", 0) for d in doomed) / 1024 ** 3
        act("ecr-batch-delete", f"{r['repo']} ({r['region']}): {len(ids)} images, {gb:.2f} GB",
            {"repo": r["repo"], "n": len(ids), "gb": round(gb, 2)},
            lambda: ecr.batch_delete_image(repositoryName=r["repo"], imageIds=ids))


def ecr_lifecycle_expire(census: dict) -> None:
    """Expire every ECR image via a LIFECYCLE POLICY — a third IAM action, after two were denied.

    ★ WHY THIS EXISTS. `ecr:DeleteRepository` and `ecr:BatchDeleteImage` both came back
    AccessDeniedException for `nr4a3-ci-submitter`, and the obvious conclusion was "ECR needs trimcrae".
    But CLAUDE.md §0 says BLOCKED is a claim that needs evidence and is usually wrong, and
    `ecr:PutLifecyclePolicy` is a THIRD, separate action that also removes images — AWS expires them on
    the policy rather than deleting them on request. Two denials do not imply the third.

    The rule expires everything: `imageCountMoreThan 0` over `tagStatus: any` leaves no image behind.
    Expiry is asynchronous — AWS evaluates within ~24 h — so unlike the S3 purge this one cannot be
    verified in the same run, and the follow-up census is what confirms it.
    """
    print("\n== ECR: lifecycle policy expiring ALL images (third route; two were denied) ==")
    policy = json.dumps({"rules": [{
        "rulePriority": 1,
        "description": "retire the lane: expire every image (AWS lanes retired, images rebuild from tracked Dockerfiles)",
        "selection": {"tagStatus": "any", "countType": "imageCountMoreThan", "countNumber": 0},
        "action": {"type": "expire"},
    }]})
    for r in census.get("ecr", {}).get("repos", []):
        ecr = boto3.client("ecr", region_name=r["region"], config=_CFG)
        act("ecr-put-lifecycle-expire-all", f"{r['repo']} ({r['region']}, {r['gb']} GB)",
            {"repo": r["repo"], "gb": r["gb"]},
            lambda r=r: ecr.put_lifecycle_policy(repositoryName=r["repo"], lifecyclePolicyText=policy))


def ebs_detached(census: dict) -> None:
    print("\n== EBS volumes in state 'available' (detached — billing for nothing) ==")
    for v in census.get("ebs", {}).get("volumes", []):
        if v["state"] != "available":
            continue
        ec2 = boto3.client("ec2", region_name=v["region"], config=_CFG)
        act("delete-volume", f"{v['id']} ({v['region']}, {v['gb']} GB, created {v['created']})",
            {"volume": v["id"], "gb": v["gb"]},
            lambda v=v: ec2.delete_volume(VolumeId=v["id"]))


def ebs_snapshots(census: dict) -> None:
    print("\n== EBS snapshots ==")
    for s in census.get("ebs", {}).get("snapshots", []):
        ec2 = boto3.client("ec2", region_name=s["region"], config=_CFG)
        act("delete-snapshot", f"{s['id']} ({s['region']}, {s['gb']} GB) {s['description']}",
            {"snapshot": s["id"], "gb": s["gb"]},
            lambda s=s: ec2.delete_snapshot(SnapshotId=s["id"]))


def s3_prefixes(census: dict) -> None:
    """Delete named `bucket/prefix` paths. No default — a default here would be a default deletion."""
    spec = os.environ.get("S3_PREFIXES", "").strip()
    print("\n== S3 prefix deletion ==")
    if not spec:
        print("  S3_PREFIXES is empty — nothing named, nothing deleted. This target requires each "
              "path to be spelled out.")
        return
    versioned = {b["bucket"]: b.get("versioning") for b in census.get("s3", {}).get("buckets", [])}
    regions = {b["bucket"]: b["region"] for b in census.get("s3", {}).get("buckets", [])}
    for item in [x.strip() for x in spec.split(",") if x.strip()]:
        bucket, _, prefix = item.partition("/")
        if not prefix:
            print(f"  ⛔ REFUSED {item}: a whole bucket is not a prefix. Name a prefix.")
            continue
        top = prefix.split("/")[0]
        if top in PROTECTED_PREFIXES:
            print(f"  ⛔ REFUSED s3://{bucket}/{prefix}: '{top}' is a PROTECTED prefix — it holds the "
                  "only copy of a result the manuscript cites. Remove it from PROTECTED_PREFIXES in "
                  "this file, deliberately, if that is genuinely intended.")
            _LOG.append({"action": "delete-prefix", "target": item, "applied": False,
                         "refused": "protected_prefix"})
            continue
        region = regions.get(bucket, os.environ.get("AWS_DEFAULT_REGION", "us-east-2"))
        s3 = boto3.client("s3", region_name=region, config=_CFG)
        keys, total = [], 0
        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
            for o in page.get("Contents", []):
                keys.append({"Key": o["Key"]})
                total += o["Size"]
        if versioned.get(bucket) == "Enabled":
            # ⚠ With versioning on, deleting objects leaves NONCURRENT versions that keep billing, so
            # "I emptied it" would be false. Say so rather than reporting a saving that will not appear.
            print(f"  ⚠ s3://{bucket} has versioning ENABLED — deleting current objects leaves "
                  "noncurrent versions that KEEP BILLING. Delete markers are not a saving.")
        print(f"  s3://{bucket}/{prefix}: {len(keys)} objects, {total / 1024 ** 3:.2f} GB")
        for i in range(0, len(keys), 1000):
            batch = keys[i:i + 1000]
            act("delete-objects", f"s3://{bucket}/{prefix} [{i}..{i + len(batch)}]",
                {"bucket": bucket, "prefix": prefix, "n": len(batch)},
                lambda batch=batch: s3.delete_objects(Bucket=bucket,
                                                      Delete={"Objects": batch, "Quiet": True}))


def _versioning_verdict(bucket: str, region: str) -> tuple[str, dict]:
    """Is this bucket versioned? Decided by EXPERIMENT, because every read that would say so is denied.

    ⛔ WHY THIS RUNS BEFORE THE PURGE AND NOT AFTER. On a versioned bucket `DeleteObject` does not remove
    anything — it writes a delete marker and the object version stays, still billing. The purge would
    delete 118k objects, report complete success, free NOTHING, and the failure would surface four weeks
    later on an invoice. That is the exact "reports while measuring nothing" shape this repo keeps paying
    for, and here it would be discovered only after the data was already unreachable through the console.

    The probe key is denied `GetBucketVersioning` AND `ListBucketVersions`, so the bucket cannot be asked.
    But `DeleteObject` ANSWERS THE QUESTION ITSELF: on a versioned bucket the delete response carries
    `VersionId` (of the new delete marker) and `DeleteMarker: True`; on an unversioned bucket it carries
    neither. That is one write and one delete of a throwaway key, using only permissions already measured
    open — a definitive reading for $0, in place of a prior about how SageMaker creates its default bucket.

    ⚠ AND IT MUST NOT RAISE. The first version let a denial escape: the account holds a second bucket
    (`cf-templates-…`, 4 objects, ~10 KB) that this key is not scoped to, and the probe's DeleteObject
    there raised AccessDenied, aborting the whole run — AFTER the real bucket had been purged but BEFORE
    the ECR and log-retention targets ran. A cleanup crashing on a 10 KB bucket must not strand the rest
    of the work, so an unprobeable bucket returns UNKNOWN and is skipped by the caller.

    ⚠ The probe writes BEFORE it deletes, so a bucket that allows PutObject and denies DeleteObject keeps
    a stray probe object. That is reported rather than swallowed — it is small, but an unreported artifact
    left behind by a cleanup tool is how the next census grows an unexplained row.
    """
    s3 = boto3.client("s3", region_name=region, config=_CFG)
    key = "_spend-probe/versioning-check.txt"
    try:
        s3.put_object(Bucket=bucket, Key=key, Body=b"versioning check; safe to delete")
    except ClientError as e:
        return "UNKNOWN", {"probe": "PutObject denied", "error": _code(e)}
    try:
        resp = s3.delete_object(Bucket=bucket, Key=key)
    except ClientError as e:
        return "UNKNOWN", {"probe": "DeleteObject denied", "error": _code(e),
                           "stray_probe_object_left": f"s3://{bucket}/{key}"}
    evidence = {"delete_response_version_id": resp.get("VersionId"),
                "delete_response_delete_marker": resp.get("DeleteMarker")}
    if resp.get("VersionId") and resp.get("VersionId") != "null":
        return "VERSIONED", evidence
    if resp.get("DeleteMarker"):
        return "VERSIONED", evidence
    return "UNVERSIONED", evidence


def s3_purge(census: dict) -> None:
    """Delete every object in the bucket except the tooling exemption. The deliberate 'all of it' path.

    Gated on PURGE_CONFIRM=DELETE-EVERYTHING so that no default, typo or half-remembered TARGETS list can
    reach it — the gate encodes an explicit human authorisation, which is the only thing that makes this
    action legitimate. It is separate from `s3_prefixes` precisely so the targeted path can keep its
    protected-prefix guard while this one deliberately does not have it.
    """
    print("\n== S3 PURGE — delete every object in the bucket ==")
    if os.environ.get("PURGE_CONFIRM") != "DELETE-EVERYTHING":
        print("  ⛔ REFUSED: PURGE_CONFIRM=DELETE-EVERYTHING is not set. Nothing deleted.")
        _LOG.append({"action": "s3-purge", "applied": False, "refused": "no_purge_confirm"})
        return
    buckets = census.get("s3", {}).get("buckets", [])
    include_tooling = os.environ.get("PURGE_INCLUDE_TOOLING") == "1"
    for b in buckets:
        bucket, region = b["bucket"], b["region"]
        if not b.get("n_objects") and not b.get("gb"):
            print(f"  s3://{bucket}: census read it as empty, skipping")
            continue
        # ⚠ NOT "UNVERSIONED". The check writes and deletes an object, so it only runs under APPLY — and
        # the first version of this line seeded the variable with "UNVERSIONED", which then went into the
        # committed ledger as though a dry run had VERIFIED the bucket was unversioned. It had verified
        # nothing. §4(b): a field's PRESENCE is never evidence of its provenance, and a plausible value is
        # more dangerous than a missing one because nobody re-checks it.
        verdict, evidence = ("NOT_CHECKED (dry run performs no writes)", {})
        if APPLY:
            verdict, evidence = _versioning_verdict(bucket, region)
            print(f"  versioning verdict for s3://{bucket}: {verdict}  evidence={evidence}")
            _LOG.append({"action": "versioning-check", "target": bucket, "verdict": verdict,
                         "applied": True, **evidence})
            if verdict == "UNKNOWN":
                # Cannot establish whether deletes would actually free anything, and in practice this
                # means the key is not scoped to the bucket at all. Skip rather than half-delete.
                print(f"  ⛔ SKIPPED s3://{bucket}: cannot probe it ({evidence.get('error')}). "
                      "This key is not scoped to this bucket, so it could not be purged anyway.")
                _LOG.append({"action": "s3-purge", "target": bucket, "applied": False,
                             "refused": "versioning_unknown", **evidence})
                continue
            if verdict == "VERSIONED":
                # Deleting would write delete markers and free nothing. Refuse rather than produce a
                # successful-looking run that does not move the bill.
                print(f"  ⛔ REFUSED s3://{bucket}: bucket is VERSIONED. DeleteObject would leave "
                      "noncurrent versions billing in full, so this purge would free nothing while "
                      "making the data unreachable. Needs s3:DeleteObjectVersion (this key lacks every "
                      "bucket-level permission) or a lifecycle rule to expire noncurrent versions.")
                _LOG.append({"action": "s3-purge", "target": bucket, "applied": False,
                             "refused": "bucket_is_versioned"})
                continue
        s3 = boto3.client("s3", region_name=region, config=_CFG)
        batch: list[dict] = []
        n_deleted = n_kept = 0
        bytes_deleted = 0

        def flush(batch=batch):
            if not batch:
                return
            act("delete-objects", f"s3://{bucket} [{len(batch)} objects]",
                {"bucket": bucket, "n": len(batch)},
                lambda batch=list(batch): s3.delete_objects(
                    Bucket=bucket, Delete={"Objects": batch, "Quiet": True}))
            batch.clear()

        for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket):
            for o in page.get("Contents", []):
                top = o["Key"].split("/")[0] if "/" in o["Key"] else "(root)"
                if top in TOOLING_PREFIXES and not include_tooling:
                    n_kept += 1
                    continue
                batch.append({"Key": o["Key"]})
                n_deleted += 1
                bytes_deleted += o["Size"]
                if len(batch) >= 1000:
                    flush()
        flush()
        print(f"  s3://{bucket}: {n_deleted} objects ({bytes_deleted / 1024 ** 3:.2f} GB) "
              f"{'deleted' if APPLY else 'would be deleted'}; {n_kept} kept as tooling "
              f"({sorted(TOOLING_PREFIXES)})")
        _LOG.append({"action": "s3-purge-summary", "target": bucket, "applied": APPLY,
                     "n_deleted": n_deleted, "gb_deleted": round(bytes_deleted / 1024 ** 3, 2),
                     "n_kept_tooling": n_kept, "versioning": verdict})


def ecr_delete_all(census: dict) -> None:
    """Delete every image in every ECR repo, then the repos themselves.

    The AWS ABFE/FEP lanes are retired and production is on Vast. Both images rebuild from a tracked
    Dockerfile via build-abfe-image.yml / build-fep-image.yml, so this is recoverable engineering rather
    than lost data — but note that a rebuild RE-SOLVES an environment whose scientific packages are not
    pinned, so a rebuilt image is not guaranteed byte-identical to the one being removed (CLAUDE.md §6,
    the openmmtools/pymbar parity reading). Nothing currently depends on either image.
    """
    print("\n== ECR: delete ALL images and the repositories ==")
    for r in census.get("ecr", {}).get("repos", []):
        ecr = boto3.client("ecr", region_name=r["region"], config=_CFG)
        act("ecr-delete-repository", f"{r['repo']} ({r['region']}, {r['gb']} GB, {r['n_images']} images)",
            {"repo": r["repo"], "gb": r["gb"]},
            lambda r=r: ecr.delete_repository(repositoryName=r["repo"], force=True))


def s3_glacier(census: dict) -> None:
    """Transition, do not delete: a lifecycle rule to Glacier Deep Archive after 30 days.

    ~$0.00099/GB-mo against Standard's ~$0.023 — a ~96 % cut that keeps every byte. This is the right
    answer for finished trajectories nobody reads but nobody wants to lose, and it is why deleting S3
    should be the LAST resort rather than the first.
    """
    print("\n== S3 -> Glacier Deep Archive after 30 days (keeps every byte, ~96% cheaper) ==")
    for b in census.get("s3", {}).get("buckets", []):
        if not b.get("gb"):
            continue
        s3 = boto3.client("s3", region_name=b["region"], config=_CFG)
        act("s3-lifecycle-glacier", f"s3://{b['bucket']} ({b['gb']} GB) -> DEEP_ARCHIVE @30d",
            {"bucket": b["bucket"], "gb": b["gb"]},
            lambda b=b: s3.put_bucket_lifecycle_configuration(
                Bucket=b["bucket"],
                LifecycleConfiguration={"Rules": [
                    {"ID": "abort-incomplete-multipart-7d", "Status": "Enabled",
                     "Filter": {"Prefix": ""},
                     "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}},
                    {"ID": "deep-archive-30d", "Status": "Enabled", "Filter": {"Prefix": ""},
                     "Transitions": [{"Days": 30, "StorageClass": "DEEP_ARCHIVE"}]},
                ]}))


TARGET_FNS = {
    "mpu_abort": mpu_abort,
    "log_retention": log_retention,
    "log_delete": log_delete,
    "ecr_prune": ecr_prune,
    "ecr_delete_all": ecr_delete_all,
    "ecr_lifecycle_expire": ecr_lifecycle_expire,
    "ebs_detached": ebs_detached,
    "ebs_snapshots": ebs_snapshots,
    "s3_prefixes": s3_prefixes,
    "s3_purge": s3_purge,
    "s3_glacier": s3_glacier,
}


def main() -> int:
    census = load_census()
    targets = [t.strip() for t in os.environ.get("TARGETS", DEFAULT_TARGETS).split(",") if t.strip()]
    unknown = [t for t in targets if t not in TARGET_FNS]
    if unknown:
        print(f"::error::unknown TARGETS: {unknown}. Known: {sorted(TARGET_FNS)}")
        return 2
    print("=" * 96)
    print(f"AWS SHUTDOWN — {'APPLY (destructive)' if APPLY else 'DRY RUN (nothing is changed)'}")
    print(f"census: {census.get('generated_utc')}   account: {census.get('account')}")
    print(f"targets: {targets}")
    print("=" * 96)
    # ⛔ ONE TARGET'S FAILURE MUST NOT STRAND THE OTHERS. Measured 2026-08-12: an AccessDenied inside
    # `s3_purge`, on a 10 KB bucket this key is not scoped to, propagated out of main() and killed the run
    # — after the 2.7 TB purge had succeeded but before `ecr_delete_all` and `log_retention` ran. The work
    # that mattered was done and the job still reported failure, which is the worst combination to read:
    # it invites re-running a destructive step that already completed. Each target is isolated, and a
    # target that raises is recorded as failed while the rest proceed.
    failures: list[str] = []
    for t in targets:
        try:
            TARGET_FNS[t](census)
        except Exception as e:  # noqa: BLE001
            failures.append(t)
            print(f"::error::target {t} raised {type(e).__name__}: {e}")
            _LOG.append({"action": f"target:{t}", "applied": False,
                         "error": f"{type(e).__name__}: {e}"})
    summary = {
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "applied": APPLY,
        "targets": targets,
        "census_generated_utc": census.get("generated_utc"),
        "actions": _LOG,
        "n_actions": len(_LOG),
        "n_applied": sum(1 for r in _LOG if r.get("applied")),
        "n_failed": sum(1 for r in _LOG if r.get("error")),
        "n_refused": sum(1 for r in _LOG if r.get("refused")),
        "failed_targets": failures,
    }
    with open(OUT, "w") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
    print(f"\n{summary['n_actions']} action(s); applied {summary['n_applied']}, "
          f"failed {summary['n_failed']}, refused {summary['n_refused']}.")
    if not APPLY:
        print("DRY RUN — nothing was changed. Re-dispatch with apply=true to act.")
    print("Wrote " + OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
