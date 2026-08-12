#!/usr/bin/env python3
"""Which shutdown routes is the CI key actually PERMITTED to take? Measured, not assumed.

The census (`aws_spend_census.py`, 2026-08-12) found 2.7 TB in one bucket at ~$62/mo estimated, and came
back `DENIED` on three separate reads: Cost Explorer, `GetBucketVersioning` and
`GetBucketLifecycleConfiguration`. That last one matters more than it looks, because the CHEAPEST fix by
far — a lifecycle rule transitioning to Glacier Deep Archive, which cuts ~96 % of the bill while losing
zero bytes — needs `s3:PutLifecycleConfiguration`. If the key cannot set a lifecycle rule, the good option
is unavailable and the choice degrades to "delete data or pay".

⚠ BUT A DENIAL ON `Get…` IS NOT A DENIAL ON `Put…`. IAM policies routinely grant one without the other,
and this key demonstrably has heavy write access — it WROTE all 2.7 TB. Assuming the good route is closed
because a neighbouring call was denied would be exactly the §4 error of treating an unreadable thing as a
known-absent one. So this probes each capability directly.

★ THERE IS A SECOND ROUTE AND IT NEEDS NO NEW PERMISSION. A storage class can be changed per object by
copying the object ONTO ITSELF with `StorageClass=…` — which needs only `s3:PutObject`, the permission the
key obviously already has. It is O(objects) API calls instead of one rule, but at ~$0.005/1000 PUTs that
is cents for this bucket, and CI is free (CLAUDE.md §5: engineering effort is free; only GPU dollars
count). This probe measures whether that fallback works, so that a "we can't, permissions" report is never
filed while an unmeasured route was open.

SAFETY. The probe writes ONE tiny object under a `_spend-probe/` prefix that nothing else uses, copies it
onto itself to change its class, then deletes it. It never touches a pre-existing key. The lifecycle probe
is the one call that cannot be made harmless by scoping — so it is GATED behind PROBE_LIFECYCLE=1 and, when
run, it first READS the existing configuration to restore it, and refuses to proceed if it cannot.

Env: AWS creds + AWS_DEFAULT_REGION. PROBE_LIFECYCLE=1 to include the lifecycle write probe.
Writes aws-spend-probe.json.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aws-spend-probe.json")
PROBE_PREFIX = "_spend-probe/"
_CFG = Config(retries={"max_attempts": 3, "mode": "standard"})


def _try(label: str, fn) -> dict:
    try:
        fn()
        return {"capability": label, "allowed": True}
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "Unknown")
        return {"capability": label, "allowed": False, "error": code,
                "denied": "AccessDenied" in code or "Forbidden" in code}
    except Exception as e:  # noqa: BLE001
        return {"capability": label, "allowed": False, "error": f"{type(e).__name__}: {e}"}


def main() -> int:
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    sts = boto3.client("sts", config=_CFG)
    acct = sts.get_caller_identity()
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct['Account']}"
    s3 = boto3.client("s3", region_name=region, config=_CFG)
    key = PROBE_PREFIX + "probe.txt"
    results: list[dict] = []

    print(f"Probing s3://{bucket} as {acct.get('Arn')}\n")

    # --- the object-level route: write, change class in place, delete ---
    results.append(_try("s3:PutObject", lambda: s3.put_object(
        Bucket=bucket, Key=key, Body=b"aws spend probe; safe to delete")))
    wrote = results[-1]["allowed"]

    if wrote:
        for cls in ("STANDARD_IA", "GLACIER_IR", "DEEP_ARCHIVE"):
            results.append(_try(
                f"s3:CopyObject in-place -> {cls}",
                lambda cls=cls: s3.copy_object(
                    Bucket=bucket, Key=key, CopySource={"Bucket": bucket, "Key": key},
                    StorageClass=cls, MetadataDirective="COPY")))
        results.append(_try("s3:DeleteObject (probe cleanup)",
                            lambda: s3.delete_object(Bucket=bucket, Key=key)))
    else:
        print("  PutObject denied — the per-object storage-class route is closed.\n")

    # --- bucket-level reads the census could not do ---
    results.append(_try("s3:GetBucketVersioning", lambda: s3.get_bucket_versioning(Bucket=bucket)))
    results.append(_try("s3:GetLifecycleConfiguration",
                        lambda: s3.get_bucket_lifecycle_configuration(Bucket=bucket)))
    results.append(_try("s3:ListBucketMultipartUploads",
                        lambda: s3.list_multipart_uploads(Bucket=bucket, MaxUploads=1)))
    results.append(_try("s3:GetBucketTagging", lambda: s3.get_bucket_tagging(Bucket=bucket)))

    # ⛔ THE QUESTION THAT DECIDES WHETHER ARCHIVING WORKS AT ALL, and GetBucketVersioning is denied.
    # If versioning is ENABLED, copying an object onto itself writes a NEW version and the old one stays
    # in Standard, still billing — so the transition would report success and save nothing. That is the
    # "reports while measuring nothing" shape, and it would only surface on next month's bill.
    # `ListObjectVersions` answers it from the objects themselves: a bucket that never had versioning
    # returns every object with VersionId 'null'. A real version id means versions exist.
    def _versions():
        r = s3.list_object_versions(Bucket=bucket, MaxKeys=200)
        vs = r.get("Versions", [])
        ids = {v.get("VersionId") for v in vs}
        row = {"sampled": len(vs),
               "all_null_version_ids": ids == {"null"} if ids else None,
               "distinct_version_ids": len(ids),
               "delete_markers": len(r.get("DeleteMarkers", [])),
               "noncurrent_sampled": sum(1 for v in vs if not v.get("IsLatest"))}
        results.append({"capability": "s3:ListBucketVersions (versioning evidence)",
                        "allowed": True, **row})
    v = _try("s3:ListBucketVersions", _versions)
    if not v["allowed"]:
        results.append(v)
    results.append(_try("ce:GetCostAndUsage", lambda: boto3.client("ce", region_name="us-east-1").
                        get_cost_and_usage(
                            TimePeriod={"Start": (_dt.date.today() - _dt.timedelta(days=2)).isoformat(),
                                        "End": _dt.date.today().isoformat()},
                            Granularity="DAILY", Metrics=["UnblendedCost"])))
    results.append(_try("ec2:DescribeVolumes",
                        lambda: boto3.client("ec2", region_name=region).describe_volumes(MaxResults=5)))
    results.append(_try("ec2:DescribeRegions",
                        lambda: boto3.client("ec2", region_name=region).describe_regions()))

    # --- the lifecycle write: gated, and it restores what was there ---
    if os.environ.get("PROBE_LIFECYCLE") == "1":
        existing = None
        try:
            existing = s3.get_bucket_lifecycle_configuration(Bucket=bucket).get("Rules")
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if code == "NoSuchLifecycleConfiguration":
                existing = []
            else:
                # ⛔ Cannot read what is there => cannot promise to put it back => do not write.
                results.append({"capability": "s3:PutLifecycleConfiguration", "allowed": None,
                                "skipped": f"refused: cannot read existing config to restore it ({code})"})
                existing = None
        if existing is not None:
            probe_rule = {"ID": "aws-spend-probe-harmless", "Status": "Disabled",
                          "Filter": {"Prefix": PROBE_PREFIX},
                          "Expiration": {"Days": 1}}
            results.append(_try("s3:PutLifecycleConfiguration", lambda: s3.put_bucket_lifecycle_configuration(
                Bucket=bucket, LifecycleConfiguration={"Rules": list(existing) + [probe_rule]})))
            if results[-1]["allowed"]:
                # Restore. A probe that leaves a rule behind has changed the thing it measured.
                if existing:
                    s3.put_bucket_lifecycle_configuration(
                        Bucket=bucket, LifecycleConfiguration={"Rules": existing})
                else:
                    s3.delete_bucket_lifecycle(Bucket=bucket)
                results[-1]["restored"] = True
    else:
        results.append({"capability": "s3:PutLifecycleConfiguration", "allowed": None,
                        "skipped": "PROBE_LIFECYCLE=1 not set"})

    for r in results:
        mark = {True: "ALLOWED", False: "DENIED ", None: "SKIPPED"}[r.get("allowed")]
        extra = r.get("error") or r.get("skipped") or ""
        print(f"  {mark}  {r['capability']}  {extra}")

    by = {r["capability"]: r.get("allowed") for r in results}
    routes = {
        "lifecycle_rule_to_glacier": by.get("s3:PutLifecycleConfiguration"),
        "per_object_copy_to_glacier": bool(by.get("s3:PutObject")
                                           and by.get("s3:CopyObject in-place -> DEEP_ARCHIVE")),
        "delete_objects": by.get("s3:DeleteObject (probe cleanup)"),
        "read_the_actual_bill": by.get("ce:GetCostAndUsage"),
    }
    out = {"generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
           "account": acct["Account"], "arn": acct.get("Arn"), "bucket": bucket,
           "capabilities": results, "routes_open": routes}
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print("\nRoutes:")
    for k, v in routes.items():
        print(f"  {k}: {'UNTESTED' if v is None else ('OPEN' if v else 'CLOSED')}")
    print("Wrote " + OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
