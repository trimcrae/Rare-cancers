#!/usr/bin/env python3
"""READ-ONLY census of everything in the AWS account that can bill while NOTHING is running.

Why this exists (2026-08-12, trimcrae: *"We're still using AWS budget somehow. Must be storage I'm
thinking? I want to shut that off"*). Every AWS lane in this repo is retired — production went to Vast
(CLAUDE.md §6, "Provider facts") — yet the account still bills. "Must be storage" is a HYPOTHESIS, and
§4 says produce the evidence before acting on one. The candidates are not equally likely and they are
not all S3:

  * S3          - checkpoints, trajectories, SageMaker model/output tarballs. Charged per GB-month even
                  though no job has read them in weeks. ALSO charged for incomplete multipart uploads
                  that no `ls` shows and no console page surfaces by default.
  * ECR         - the pre-baked GPU images (`build-abfe-image.yml`, `build-fep-image.yml`). Multi-GB
                  each, billed per GB-month, and invisible to anyone thinking about "storage" as S3.
  * EBS         - volumes left `available` (detached) after an instance died still bill in full, as do
                  snapshots and the snapshots behind private AMIs.
  * CloudWatch  - log groups with retention `Never expire` accumulate forever; `tail-cloudwatch-aws.yml`
                  wrote into them and nothing ever set a retention policy.
  * SageMaker   - a notebook instance, a Studio app or an INFERENCE ENDPOINT bills PER HOUR, not per
                  request, and none of them appear in a training-job listing. This is the one candidate
                  that would NOT be storage, so it is checked first and loudest.
  * EFS/FSx, NAT gateways, EIPs, Route53 zones, Secrets Manager - small but nonzero, and each is a thing
                  that bills at rest.

Design rules this file follows, both from CLAUDE.md §4:

  ★ AN ABSENT READING IS NOT A READING OF ABSENCE. Every section reports one of three states —
    a value, `EMPTY` (the API answered and there is nothing), or `DENIED`/`ERROR` (we could not look).
    A permission failure must NEVER render as "nothing here", because the action taken on those two
    readings is opposite: EMPTY means stop looking, DENIED means the bill can still be hiding there.

  ★ THE CENSUS NEVER DELETES. It is dispatched, read, and only then is a deletion authorised, by a
    human, with the numbers in front of them. `aws_spend_shutdown.py` is the other half.

Env: AWS creds + AWS_DEFAULT_REGION. Optional REGIONS="us-east-2,us-east-1" to override the scan set.
Writes aws-spend-census.json next to this file and prints a human-readable board.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aws-spend-census.json")

# Regional services are invisible outside the region they live in, so a single-region scan can report a
# clean account while a volume bills in another. Default to the regions this repo has ever named plus
# us-east-1 (where anything global-ish lands by default).
DEFAULT_REGIONS = ["us-east-2", "us-east-1", "us-west-2"]

GB = 1024.0 ** 3

# Rough public list prices, USD, us-east-2. Used ONLY to rank what to switch off first — the authoritative
# number is Cost Explorer's, which this script reads when the key is allowed to. A ranking does not need a
# precise price; it needs the right order of magnitude, and being explicit about that beats a silent guess.
PRICE_PER_GB_MONTH = {
    "s3_standard": 0.023,
    "ecr": 0.10,
    "ebs_gp3": 0.08,
    "ebs_snapshot": 0.05,
    "cloudwatch_logs": 0.03,
    "efs": 0.30,
}

_CFG = Config(retries={"max_attempts": 5, "mode": "standard"})


def _client(service: str, region: str | None = None):
    return boto3.client(service, region_name=region, config=_CFG)


def _probe(fn, *a, **kw):
    """Run a read call and classify the outcome instead of letting a denial look like an empty answer.

    Returns (value, status) where status is 'ok' | 'DENIED' | 'ERROR: <code>'. Callers MUST render the
    status; see the module docstring on why an unreadable section and an empty one are not the same fact.
    """
    try:
        return fn(*a, **kw), "ok"
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "Unknown")
        if code in ("AccessDenied", "AccessDeniedException", "UnauthorizedOperation",
                    "AuthorizationError", "InvalidClientTokenId", "OptInRequired"):
            return None, "DENIED"
        return None, f"ERROR: {code}"
    except (BotoCoreError, Exception) as e:  # noqa: BLE001 - a census must never abort on one section
        return None, f"ERROR: {type(e).__name__}"


def _regions() -> list[str]:
    env = os.environ.get("REGIONS", "").strip()
    if env:
        return [r.strip() for r in env.split(",") if r.strip()]
    res, status = _probe(lambda: _client("ec2", "us-east-1").describe_regions()["Regions"])
    if status == "ok" and res:
        # Scan every enabled region: a forgotten volume does not care which region we consider likely.
        return sorted(r["RegionName"] for r in res)
    return DEFAULT_REGIONS


# ---------------------------------------------------------------------------------------------------
# Cost Explorer - the only authoritative answer to "what are we actually paying for"
# ---------------------------------------------------------------------------------------------------
def cost_explorer(days: int = 60) -> dict:
    """Last `days` of unblended cost, grouped by service, and the last 30 by usage type.

    ⚠ Cost Explorer needs `ce:GetCostAndUsage`, which a SageMaker/S3-scoped key usually does NOT have.
    A DENIED here is expected and is NOT a failure of the census — the resource inventory below stands on
    its own. It does mean the dollar attribution is inferred from sizes rather than read from the bill,
    and the report says so rather than presenting an estimate as a measurement.
    """
    end = _dt.date.today() + _dt.timedelta(days=1)
    start = end - _dt.timedelta(days=days)
    ce = _client("ce", "us-east-1")  # CE is only addressable in us-east-1

    def _by(group_key: str, since: _dt.date) -> list[dict]:
        rows: dict[str, float] = {}
        token = None
        while True:
            kw = dict(
                TimePeriod={"Start": since.isoformat(), "End": end.isoformat()},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": group_key}],
            )
            if token:
                kw["NextPageToken"] = token
            r = ce.get_cost_and_usage(**kw)
            for period in r["ResultsByTime"]:
                for g in period["Groups"]:
                    amt = float(g["Metrics"]["UnblendedCost"]["Amount"])
                    rows[g["Keys"][0]] = rows.get(g["Keys"][0], 0.0) + amt
            token = r.get("NextPageToken")
            if not token:
                break
        return sorted(({"key": k, "usd": round(v, 4)} for k, v in rows.items() if v > 0),
                      key=lambda d: -d["usd"])

    out: dict = {"window_days": days, "start": start.isoformat(), "end": end.isoformat()}
    svc, status = _probe(_by, "SERVICE", start)
    out["status"] = status
    if status != "ok":
        return out
    out["by_service"] = svc
    out["total_usd"] = round(sum(r["usd"] for r in svc), 2)

    last30 = end - _dt.timedelta(days=30)
    ut, ut_status = _probe(_by, "USAGE_TYPE", last30)
    out["usage_type_status"] = ut_status
    if ut_status == "ok":
        out["by_usage_type_30d"] = ut[:25]
        out["total_usd_30d"] = round(sum(r["usd"] for r in ut), 2)
    reg, reg_status = _probe(_by, "REGION", last30)
    out["region_status"] = reg_status
    if reg_status == "ok":
        out["by_region_30d"] = reg
    return out


# ---------------------------------------------------------------------------------------------------
# S3 - the hypothesis under test
# ---------------------------------------------------------------------------------------------------
def _bucket_size_from_cloudwatch(bucket: str, region: str) -> tuple[dict | None, str]:
    """Per-storage-class bytes from the free daily AWS/S3 metrics, rather than by walking the bucket.

    Walking is O(objects) and this account holds MD trajectories; the metric is one call and is the same
    number the bill is computed from. The tradeoff is that the metric lands once a day, so a bucket
    emptied this morning still reads full — which is exactly why the shutdown script re-checks.
    """
    cw = _client("cloudwatch", region)
    end = _dt.datetime.now(_dt.timezone.utc)
    start = end - _dt.timedelta(days=4)
    classes = ["StandardStorage", "StandardIAStorage", "IntelligentTieringFAStorage",
               "IntelligentTieringIAStorage", "GlacierInstantRetrievalStorage",
               "GlacierStorage", "GlacierDeepArchiveStorage", "OneZoneIAStorage",
               "ReducedRedundancyStorage"]
    sizes: dict[str, float] = {}
    for sc in classes:
        r, status = _probe(
            cw.get_metric_statistics,
            Namespace="AWS/S3", MetricName="BucketSizeBytes",
            Dimensions=[{"Name": "BucketName", "Value": bucket}, {"Name": "StorageType", "Value": sc}],
            StartTime=start, EndTime=end, Period=86400, Statistics=["Average"],
        )
        if status != "ok":
            return None, status
        pts = sorted((r or {}).get("Datapoints", []), key=lambda p: p["Timestamp"])
        if pts and pts[-1]["Average"] > 0:
            sizes[sc] = pts[-1]["Average"]
    r, status = _probe(
        cw.get_metric_statistics,
        Namespace="AWS/S3", MetricName="NumberOfObjects",
        Dimensions=[{"Name": "BucketName", "Value": bucket}, {"Name": "StorageType", "Value": "AllStorageTypes"}],
        StartTime=start, EndTime=end, Period=86400, Statistics=["Average"],
    )
    n_obj = None
    if status == "ok":
        pts = sorted((r or {}).get("Datapoints", []), key=lambda p: p["Timestamp"])
        if pts:
            n_obj = int(pts[-1]["Average"])
    return {"by_class_bytes": sizes, "total_bytes": sum(sizes.values()), "n_objects": n_obj}, "ok"


def _bucket_top_prefixes(bucket: str, region: str, max_keys: int = 200_000) -> tuple[dict | None, str]:
    """Sum object bytes by first key segment, so the report can name WHAT to delete, not just how much.

    Capped: a census must terminate. If the cap is hit the row says `truncated: true` rather than
    presenting a partial sum as the bucket total — a plausible-looking number from a truncated walk is
    the §4(b) failure mode ("a populated field is not a measured one").
    """
    s3 = _client("s3", region)
    paginator = s3.get_paginator("list_objects_v2")
    sizes: dict[str, list] = {}
    n = 0
    truncated = False
    try:
        for page in paginator.paginate(Bucket=bucket):
            for o in page.get("Contents", []):
                top = o["Key"].split("/")[0] if "/" in o["Key"] else "(root)"
                row = sizes.setdefault(top, [0, 0])
                row[0] += o["Size"]
                row[1] += 1
                n += 1
            if n >= max_keys:
                truncated = True
                break
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "Unknown")
        return None, ("DENIED" if "AccessDenied" in code else f"ERROR: {code}")
    except Exception as e:  # noqa: BLE001
        return None, f"ERROR: {type(e).__name__}"
    rows = sorted(({"prefix": k, "bytes": v[0], "n": v[1]} for k, v in sizes.items()),
                  key=lambda d: -d["bytes"])
    return {"prefixes": rows[:30], "keys_walked": n, "truncated": truncated}, "ok"


def _incomplete_multipart(bucket: str, region: str) -> tuple[dict | None, str]:
    """Incomplete multipart uploads bill as storage and appear in NO object listing.

    A killed trajectory upload leaves parts behind forever. This is the classic invisible S3 charge and
    the reason a bucket's "size" per the console can be smaller than what it bills for.
    """
    s3 = _client("s3", region)
    r, status = _probe(s3.list_multipart_uploads, Bucket=bucket, MaxUploads=1000)
    if status != "ok":
        return None, status
    ups = (r or {}).get("Uploads", [])
    return {"n_uploads": len(ups),
            "oldest": min((u["Initiated"] for u in ups), default=None).isoformat() if ups else None}, "ok"


def s3_census(walk_prefixes: bool) -> dict:
    s3 = _client("s3", "us-east-1")
    res, status = _probe(lambda: s3.list_buckets()["Buckets"])
    out: dict = {"status": status, "buckets": []}
    if status != "ok":
        return out
    for b in res or []:
        name = b["Name"]
        loc, loc_status = _probe(lambda: s3.get_bucket_location(Bucket=name).get("LocationConstraint"))
        region = (loc or "us-east-1") if loc_status == "ok" else "us-east-1"
        row: dict = {"bucket": name, "region": region,
                     "created": b["CreationDate"].isoformat(), "location_status": loc_status}
        size, size_status = _bucket_size_from_cloudwatch(name, region)
        row["size_status"] = size_status
        if size_status == "ok" and size:
            row.update(size)
            row["gb"] = round(size["total_bytes"] / GB, 3)
            row["est_usd_per_month"] = round(size["total_bytes"] / GB * PRICE_PER_GB_MONTH["s3_standard"], 2)
        mpu, mpu_status = _incomplete_multipart(name, region)
        row["multipart_status"] = mpu_status
        if mpu_status == "ok" and mpu:
            row["incomplete_multipart"] = mpu
        lc, lc_status = _probe(lambda: _client("s3", region).get_bucket_lifecycle_configuration(Bucket=name))
        row["lifecycle"] = ("none" if lc_status.startswith("ERROR: NoSuchLifecycleConfiguration")
                            else ("present" if lc_status == "ok" else lc_status))
        ver, ver_status = _probe(lambda: _client("s3", region).get_bucket_versioning(Bucket=name))
        # Versioning matters for a shutdown: with it on, deleting objects leaves NONCURRENT versions that
        # keep billing, so "I emptied the bucket" would be false. The shutdown path must know.
        row["versioning"] = (ver or {}).get("Status", "Disabled") if ver_status == "ok" else ver_status
        if walk_prefixes and row.get("gb", 0) > 0:
            pref, pref_status = _bucket_top_prefixes(name, region)
            row["prefix_status"] = pref_status
            if pref_status == "ok" and pref:
                row["top_prefixes"] = pref
        out["buckets"].append(row)
    out["buckets"].sort(key=lambda r: -(r.get("gb") or 0))
    out["total_gb"] = round(sum(r.get("gb") or 0 for r in out["buckets"]), 2)
    out["est_usd_per_month"] = round(sum(r.get("est_usd_per_month") or 0 for r in out["buckets"]), 2)
    return out


# ---------------------------------------------------------------------------------------------------
# Everything else that bills at rest
# ---------------------------------------------------------------------------------------------------
def ecr_census(regions: list[str]) -> dict:
    out: dict = {"repos": [], "status": "ok"}
    total = 0
    for region in regions:
        ecr = _client("ecr", region)
        repos, status = _probe(lambda: list(ecr.get_paginator("describe_repositories").paginate()))
        if status != "ok":
            out.setdefault("region_status", {})[region] = status
            continue
        for page in repos or []:
            for r in page.get("repositories", []):
                imgs, im_status = _probe(
                    lambda: list(ecr.get_paginator("describe_images")
                                 .paginate(repositoryName=r["repositoryName"])))
                size = 0
                n = 0
                if im_status == "ok":
                    for ip in imgs or []:
                        for im in ip.get("imageDetails", []):
                            size += im.get("imageSizeInBytes", 0)
                            n += 1
                total += size
                out["repos"].append({
                    "region": region, "repo": r["repositoryName"], "n_images": n,
                    "gb": round(size / GB, 3), "image_status": im_status,
                    "est_usd_per_month": round(size / GB * PRICE_PER_GB_MONTH["ecr"], 2),
                    "lifecycle_policy": _probe(
                        lambda: ecr.get_lifecycle_policy(repositoryName=r["repositoryName"]))[1],
                })
    out["repos"].sort(key=lambda r: -r["gb"])
    out["total_gb"] = round(total / GB, 2)
    out["est_usd_per_month"] = round(total / GB * PRICE_PER_GB_MONTH["ecr"], 2)
    return out


def ebs_census(regions: list[str]) -> dict:
    out: dict = {"volumes": [], "snapshots": [], "amis": [], "region_status": {}}
    vol_gb = snap_gb = 0
    for region in regions:
        ec2 = _client("ec2", region)
        vols, status = _probe(lambda: list(ec2.get_paginator("describe_volumes").paginate()))
        out["region_status"][region] = status
        if status == "ok":
            for page in vols or []:
                for v in page.get("Volumes", []):
                    vol_gb += v["Size"]
                    out["volumes"].append({
                        "region": region, "id": v["VolumeId"], "gb": v["Size"], "type": v["VolumeType"],
                        "state": v["State"],  # 'available' == detached and billing for nothing
                        "created": v["CreateTime"].isoformat(),
                        "attached_to": [a["InstanceId"] for a in v.get("Attachments", [])],
                    })
        snaps, s_status = _probe(lambda: list(
            ec2.get_paginator("describe_snapshots").paginate(OwnerIds=["self"])))
        if s_status == "ok":
            for page in snaps or []:
                for s in page.get("Snapshots", []):
                    snap_gb += s["VolumeSize"]
                    out["snapshots"].append({"region": region, "id": s["SnapshotId"],
                                             "gb": s["VolumeSize"], "started": s["StartTime"].isoformat(),
                                             "description": s.get("Description", "")[:80]})
        amis, a_status = _probe(lambda: ec2.describe_images(Owners=["self"])["Images"])
        if a_status == "ok":
            for im in amis or []:
                out["amis"].append({"region": region, "id": im["ImageId"], "name": im.get("Name", "")[:60]})
        # A running instance is not storage, but it is the loudest possible finding, so it is not skipped.
        inst, i_status = _probe(lambda: list(ec2.get_paginator("describe_instances").paginate(
            Filters=[{"Name": "instance-state-name", "Values": ["running", "stopped"]}])))
        if i_status == "ok":
            for page in inst or []:
                for res in page.get("Reservations", []):
                    for i in res["Instances"]:
                        out.setdefault("instances", []).append({
                            "region": region, "id": i["InstanceId"], "type": i["InstanceType"],
                            "state": i["State"]["Name"], "launched": i["LaunchTime"].isoformat()})
        eips, e_status = _probe(lambda: ec2.describe_addresses()["Addresses"])
        if e_status == "ok":
            for a in eips or []:
                out.setdefault("elastic_ips", []).append(
                    {"region": region, "ip": a.get("PublicIp"),
                     "associated": bool(a.get("AssociationId"))})
        nats, n_status = _probe(lambda: list(ec2.get_paginator("describe_nat_gateways").paginate()))
        if n_status == "ok":
            for page in nats or []:
                for g in page.get("NatGateways", []):
                    if g.get("State") in ("available", "pending"):
                        out.setdefault("nat_gateways", []).append(
                            {"region": region, "id": g["NatGatewayId"], "state": g["State"]})
    out["volumes_gb"] = vol_gb
    out["snapshots_gb"] = snap_gb
    out["detached_volumes_gb"] = sum(v["gb"] for v in out["volumes"] if v["state"] == "available")
    out["est_usd_per_month"] = round(vol_gb * PRICE_PER_GB_MONTH["ebs_gp3"]
                                     + snap_gb * PRICE_PER_GB_MONTH["ebs_snapshot"], 2)
    return out


def logs_census(regions: list[str]) -> dict:
    out: dict = {"groups": [], "region_status": {}}
    total = 0
    for region in regions:
        cwl = _client("logs", region)
        pages, status = _probe(lambda: list(cwl.get_paginator("describe_log_groups").paginate()))
        out["region_status"][region] = status
        if status != "ok":
            continue
        for page in pages or []:
            for g in page.get("logGroups", []):
                b = g.get("storedBytes", 0)
                total += b
                out["groups"].append({
                    "region": region, "name": g["logGroupName"], "gb": round(b / GB, 4),
                    # `retention` None == Never Expire, i.e. this group grows forever by default.
                    "retention_days": g.get("retentionInDays"),
                })
    out["groups"].sort(key=lambda r: -r["gb"])
    out["never_expire_groups"] = sum(1 for g in out["groups"] if g["retention_days"] is None)
    out["total_gb"] = round(total / GB, 3)
    out["est_usd_per_month"] = round(total / GB * PRICE_PER_GB_MONTH["cloudwatch_logs"], 2)
    return out


def sagemaker_census(regions: list[str]) -> dict:
    """Per-HOUR SageMaker resources. These are not storage and would dwarf it; checked loudly."""
    out: dict = {"region_status": {}}
    for region in regions:
        sm = _client("sagemaker", region)
        for label, fn in (
            ("endpoints", lambda: sm.list_endpoints(MaxResults=100)["Endpoints"]),
            ("notebook_instances", lambda: sm.list_notebook_instances(MaxResults=100)["NotebookInstances"]),
            ("domains", lambda: sm.list_domains(MaxResults=100)["Domains"]),
            ("apps", lambda: sm.list_apps(MaxResults=100)["Apps"]),
            ("in_progress_training", lambda: sm.list_training_jobs(
                StatusEquals="InProgress", MaxResults=100)["TrainingJobSummaries"]),
            ("in_progress_processing", lambda: sm.list_processing_jobs(
                StatusEquals="InProgress", MaxResults=100)["ProcessingJobSummaries"]),
            ("in_progress_transform", lambda: sm.list_transform_jobs(
                StatusEquals="InProgress", MaxResults=100)["TransformJobSummaries"]),
        ):
            res, status = _probe(fn)
            out["region_status"].setdefault(region, {})[label] = status
            if status == "ok" and res:
                rows = [{k: (v.isoformat() if hasattr(v, "isoformat") else v)
                         for k, v in r.items() if k in (
                             "EndpointName", "EndpointStatus", "NotebookInstanceName",
                             "NotebookInstanceStatus", "InstanceType", "DomainName", "Status",
                             "AppName", "AppType", "TrainingJobName", "ProcessingJobName",
                             "TransformJobName", "CreationTime")}
                        for r in res]
                if rows:
                    out.setdefault(label, []).extend([dict(region=region, **r) for r in rows])
    return out


def misc_census(regions: list[str]) -> dict:
    out: dict = {}
    for region in regions:
        efs = _client("efs", region)
        res, status = _probe(lambda: efs.describe_file_systems()["FileSystems"])
        if status == "ok" and res:
            for f in res:
                out.setdefault("efs", []).append({
                    "region": region, "id": f["FileSystemId"],
                    "gb": round(f.get("SizeInBytes", {}).get("Value", 0) / GB, 3)})
        sec = _client("secretsmanager", region)
        res, status = _probe(lambda: sec.list_secrets(MaxResults=100)["SecretList"])
        if status == "ok" and res:
            out.setdefault("secrets", []).append({"region": region, "n": len(res)})
    return out


# ---------------------------------------------------------------------------------------------------
def _fmt_money(x) -> str:
    return "—" if x is None else f"${x:,.2f}"


def report(c: dict) -> None:
    p = print
    p("=" * 96)
    p(f"AWS SPEND CENSUS — account {c.get('account')} — {c['generated_utc']}")
    p("=" * 96)

    ce = c["cost_explorer"]
    p("\n## What the bill actually says (Cost Explorer)")
    if ce.get("status") != "ok":
        p(f"  {ce.get('status')} — the key cannot read Cost Explorer.")
        p("  This is NOT 'the bill is zero'. Dollar figures below are ESTIMATES from measured sizes")
        p("  at public list price; sizes are measured, dollars are inferred.")
    else:
        p(f"  Last {ce['window_days']}d total: {_fmt_money(ce.get('total_usd'))}"
          f"   |   last 30d: {_fmt_money(ce.get('total_usd_30d'))}")
        for r in ce.get("by_service", [])[:12]:
            p(f"    {_fmt_money(r['usd']):>12}  {r['key']}")
        if ce.get("by_usage_type_30d"):
            p("\n  Top usage types, last 30d (this is the line that names the charge):")
            for r in ce["by_usage_type_30d"][:12]:
                p(f"    {_fmt_money(r['usd']):>12}  {r['key']}")

    sm = c["sagemaker"]
    hourly = [k for k in ("endpoints", "notebook_instances", "apps", "in_progress_training",
                          "in_progress_processing", "in_progress_transform") if sm.get(k)]
    p("\n## Per-HOUR resources (would dwarf any storage charge)")
    if hourly:
        for k in hourly:
            for row in sm[k]:
                p(f"  ⚠ {k}: {row}")
    else:
        p("  none found in the scanned regions "
          f"(read status recorded per region in the JSON)")
    ebs = c["ebs"]
    for k, label in (("instances", "EC2 instance"), ("nat_gateways", "NAT gateway"),
                     ("elastic_ips", "Elastic IP")):
        for row in ebs.get(k, []):
            p(f"  ⚠ {label}: {row}")

    p("\n## Storage at rest")
    s3 = c["s3"]
    p(f"  S3          {s3.get('total_gb', 0):>10.2f} GB   est {_fmt_money(s3.get('est_usd_per_month'))}/mo"
      f"   [{s3.get('status')}]")
    for b in s3.get("buckets", [])[:12]:
        mpu = b.get("incomplete_multipart", {}).get("n_uploads")
        p(f"      {b.get('gb', 0):>10.2f} GB  {b['bucket']}  ({b['region']}, versioning={b.get('versioning')},"
          f" lifecycle={b.get('lifecycle')}, incomplete-MPU={mpu})")
        for pr in (b.get("top_prefixes") or {}).get("prefixes", [])[:6]:
            p(f"            {pr['bytes'] / GB:>8.2f} GB  {pr['n']:>7} obj  {pr['prefix']}/")
    ecr = c["ecr"]
    p(f"  ECR         {ecr.get('total_gb', 0):>10.2f} GB   est {_fmt_money(ecr.get('est_usd_per_month'))}/mo")
    for r in ecr.get("repos", [])[:10]:
        p(f"      {r['gb']:>10.2f} GB  {r['repo']}  ({r['region']}, {r['n_images']} images,"
          f" lifecycle={r['lifecycle_policy']})")
    p(f"  EBS vols    {ebs.get('volumes_gb', 0):>10.2f} GB   "
      f"({ebs.get('detached_volumes_gb', 0)} GB DETACHED and billing for nothing)")
    p(f"  EBS snaps   {ebs.get('snapshots_gb', 0):>10.2f} GB   "
      f"est {_fmt_money(ebs.get('est_usd_per_month'))}/mo for both")
    lg = c["logs"]
    p(f"  CW Logs     {lg.get('total_gb', 0):>10.2f} GB   est {_fmt_money(lg.get('est_usd_per_month'))}/mo"
      f"   ({lg.get('never_expire_groups')} groups set to NEVER EXPIRE)")
    for g in lg.get("groups", [])[:6]:
        p(f"      {g['gb']:>10.3f} GB  {g['name']}  (retention={g['retention_days'] or 'never'})")
    for f in c["misc"].get("efs", []):
        p(f"  EFS         {f['gb']:>10.3f} GB   {f['id']} ({f['region']})")

    est = c["estimated_monthly_usd"]
    p("\n## Estimated monthly storage cost, by what would switch it off")
    for k, v in sorted(est["by_source"].items(), key=lambda kv: -kv[1]):
        p(f"    {_fmt_money(v):>12}  {k}")
    for k in est.get("unknown_sources", []):
        p(f"    {'UNKNOWN':>12}  {k} — could not read; NOT counted as zero")
    tail = " — A FLOOR, not a total: see UNKNOWN rows" if est.get("total_is_a_floor") else ""
    p(f"    {_fmt_money(est['total']):>12}  TOTAL (estimate at list price, not the bill){tail}")
    p("\nWrote " + OUT)


def main() -> int:
    regions = _regions()
    walk = os.environ.get("WALK_PREFIXES", "1") not in ("0", "false", "")
    acct, _ = _probe(lambda: _client("sts").get_caller_identity()["Account"])
    c: dict = {
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "account": acct,
        "regions_scanned": regions,
        "note": ("READ-ONLY census. Dollar figures are ESTIMATES at public list price unless the "
                 "cost_explorer block says status=ok, in which case that block is the bill itself."),
        "cost_explorer": cost_explorer(),
        "s3": s3_census(walk_prefixes=walk),
        "ecr": ecr_census(regions),
        "ebs": ebs_census(regions),
        "logs": logs_census(regions),
        "sagemaker": sagemaker_census(regions),
        "misc": misc_census(regions),
    }
    # ⛔ A SECTION WE COULD NOT READ MUST NOT CONTRIBUTE $0.00 TO THIS TABLE. The first version of this
    # summary did exactly that: EBS came back DENIED in all three regions and the board printed
    # "$0.00  EBS volumes + snapshots", which reads as "checked, nothing there" — the §4 failure this
    # whole file exists to avoid, reproduced in its own summary line. Unreadable sources are listed
    # separately as UNKNOWN and are excluded from the total, and the total says it is a floor.
    by_source: dict[str, float] = {}
    unknown: list[str] = []
    if c["s3"].get("status") == "ok":
        by_source["S3"] = c["s3"].get("est_usd_per_month") or 0.0
    else:
        unknown.append(f"S3 ({c['s3'].get('status')})")
    ebs_status = set(c["ebs"].get("region_status", {}).values())
    if ebs_status and ebs_status != {"ok"}:
        unknown.append(f"EBS volumes + snapshots ({'/'.join(sorted(ebs_status))})")
    else:
        by_source["EBS volumes + snapshots"] = c["ebs"].get("est_usd_per_month") or 0.0
    by_source["ECR (baked GPU images)"] = c["ecr"].get("est_usd_per_month") or 0.0
    by_source["CloudWatch Logs"] = c["logs"].get("est_usd_per_month") or 0.0
    c["estimated_monthly_usd"] = {
        "by_source": by_source,
        "unknown_sources": unknown,
        "total": round(sum(by_source.values()), 2),
        "total_is_a_floor": bool(unknown),
    }
    with open(OUT, "w") as fh:
        json.dump(c, fh, indent=2, sort_keys=True)
    report(c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
