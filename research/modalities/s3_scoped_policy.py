#!/usr/bin/env python3
"""What an S3 credential handed to a RENTED GPU HOST is allowed to do — the single source of truth.

WHY THIS FILE EXISTS
--------------------
`gpu_backend._vast_onstart` writes the object-store credential, in plaintext, into the onstart script of
every rented Vast **community** host. That is by design — the leg has to reach the checkpoint bucket and
Vast offers no secret-injection mechanism — but it means the host's operator can read whatever key we send.
Until 2026-07-27 the key we sent was `nr4a3-ci-submitter`, whose policy (`deploy/aws-sagemaker.cfn.yaml`,
lines 31-47) grants `s3:CreateBucket/PutObject/GetObject/ListBucket/GetBucketLocation` on `Resource: "*"`,
`sagemaker:CreateProcessingJob` on `"*"`, and `iam:PassRole` onto a role carrying AmazonSageMakerFullAccess.
That is not "write access to the checkpoint bucket" — it is write access to every bucket in the account
plus the ability to launch SageMaker jobs at trimcrae's expense. See
`research/compute/credential-exposure-2026-07-27.md` and the runbook `scoped-s3-credential-runbook.md`.

trimcrae's call was **scope the credentials**. This module is the machine-readable half: it states exactly
which S3 actions and which key prefixes a leg needs, and RENDERS the IAM policy from that statement. The
policy JSON in the runbook is generated here, the per-rental STS session policy is generated here, and
`tests/test_s3_scoped_policy.py` asserts the statement still covers every S3 verb the launchers' onstart
pipelines actually invoke. One fact, one place: nobody hand-copies a policy.

WHAT A LEG ACTUALLY DOES (read off the onstart pipelines and the drivers they invoke, not assumed)
-------------------------------------------------------------------------------------------------
* `aws s3 cp <local|-> s3://…`               -> PutObject      (checkpoints, leg JSON, run.log, phase.txt)
* `aws s3 cp s3://… <local|->`               -> GetObject      (resume; staged inputs; the setup/stage caches)
* `aws s3 cp s3://… s3://…`                  -> GetObject + PutObject   (ternary archives run.log per attempt)
* `aws s3 cp --recursive` / `aws s3 sync`    -> ListBucket + GetObject/PutObject
* `aws s3 ls s3://…/key`                     -> ListBucket     (the "already done?" idempotency probe)
* boto3 upload_file/download_file/put_object/get_object/head_object/list_objects_v2 (`S3CommitStore`,
  `nr4a3_rbfe` setup cache)                  -> the same set; head_object is authorised by s3:GetObject
* multipart, for any checkpoint over ~8 MB   -> PutObject covers create/upload/complete

It does NOT call SageMaker, CloudWatch, ECR, IAM or STS, and does not enumerate the bucket root.

DELETE IS DELIBERATELY WITHHELD, AND THAT CHANGES NOTHING TODAY
---------------------------------------------------------------
One host-side call deletes: `nrv04_covalent_md._rm_ckpt` shells out to `aws s3 rm` to drop a finished leg's
two `ckpt_*` objects. It is wrapped in `try/except` with `capture_output=True`, and — the point — the key
being forwarded today has **no `s3:DeleteObject` at all** (the CFN grant above lists five actions, none of
them a delete), so that call already fails silently on every leg. Withholding delete here therefore
reproduces current behaviour exactly while ensuring a leaked leg credential cannot destroy evidence. The
observable consequence, unchanged either way, is a stale checkpoint that makes a later re-dispatch resume a
completed leg; if that is ever worth fixing, fix it by having the driver mark the leg done, not by handing a
community host a delete grant.

HONEST LIMITS OF THIS SCOPING
-----------------------------
1. PutObject on a prefix is also permission to OVERWRITE it. A leaked scoped key can still corrupt the
   lanes it covers; it cannot touch any other bucket, cannot delete, and cannot spend money. Bucket
   versioning is what makes the overwrite case recoverable, which is why the runbook asks for it and why
   `s3:PutBucketVersioning` is explicitly denied below.
2. One long-lived scoped key is shared by every concurrent rental, so leg A's host can write leg B's
   prefix. `sts_leg_credentials()` closes that gap per-rental; it is stage 2 and opt-in (see below).
3. Read-only input prefixes are separated from read-write result prefixes, so a compromised host cannot
   poison the staged inputs that every OTHER leg reads. That separation is the cheapest real win here.
"""
from __future__ import annotations

import json

# The one checkpoint/result bucket every Vast lane reuses (SageMaker's default bucket for the account).
DEFAULT_BUCKET = "sagemaker-us-east-2-646605541856"

# --- the actions -----------------------------------------------------------------------------------------
# Object-level. `s3:PutObject` covers CreateMultipartUpload / UploadPart / CompleteMultipartUpload; the
# abort/list-parts pair is separate and lets the CLI clean up an interrupted large upload, which a preempted
# leg produces routinely. (Those two are the only actions here the current CI key lacks; they can affect
# nothing but our own in-flight uploads.) `s3:GetObject` also authorises HeadObject.
LEG_OBJECT_ACTIONS = (
    "s3:GetObject",
    "s3:PutObject",
    "s3:AbortMultipartUpload",
    "s3:ListMultipartUploadParts",
)
LEG_READONLY_OBJECT_ACTIONS = ("s3:GetObject",)
# Bucket-level. ListBucket backs `aws s3 ls`, `--recursive` and `sync`; GetBucketLocation is what the CLI
# uses to resolve the bucket's region before its first call.
LEG_BUCKET_ACTIONS = (
    "s3:ListBucket",
    "s3:GetBucketLocation",
)
# Explicitly denied. The Allow lists already withhold these; an explicit Deny survives some future policy
# being attached to the same user by mistake, which is the realistic way this scoping gets quietly undone.
LEG_DENIED_ACTIONS = (
    "s3:DeleteObject", "s3:DeleteObjectVersion", "s3:PutObjectAcl", "s3:PutBucketAcl",
    "s3:PutBucketPolicy", "s3:DeleteBucketPolicy", "s3:PutBucketVersioning", "s3:CreateBucket",
    "sagemaker:*", "iam:*", "sts:AssumeRole",
)

# --- the prefixes ----------------------------------------------------------------------------------------
# EVERY top-level key prefix a rented host reads or writes, at the granularity that separates shared INPUTS
# (read-only) from a lane's own RESULTS (read-write). A lane whose prefix is missing gets a credential that
# cannot write, so `tests/test_s3_scoped_policy.py` scans the launcher modules and fails the build if a new
# lane's prefix was never registered. That test is why this list cannot silently go stale — the failure it
# prevents is a fleet that burns GPU hours and uploads nothing, which is strictly worse than the exposure
# this whole change exists to close.
LANE_PREFIXES = {
    # prefix                             : (access, owning launcher — for the test's error message)
    "protfep-benchmark":                   ("rw", "protfep_vast_launch"),
    "nr4a3-step1-fanout/stage":            ("ro", "congeneric_fanout_vast  (staged receptor/ligands)"),
    "nr4a3-step1-fanout/results":          ("rw", "congeneric_fanout_vast"),
    "nrv04-covalent-cofold":               ("ro", "nrv04_vast_launch  (co-folded CIF inputs)"),
    "nrv04-descriptive-v4":                ("ro", "nrv04_retro_panel  (pinned retro inputs)"),
    "nrv04-covalent-results":              ("rw", "nrv04_vast_launch"),
    "nrv04-retro-results":                 ("rw", "nrv04_vast_launch  (retrospective sub-lane)"),
    "nrv04-ffcache":                       ("rw", "nrv04_charge_cache  (no live caller; cheap to keep)"),
    "vast-bench-results":                  ("rw", "nrv04_vast_launch  (bench sub-lane)"),
    "vast-firm-results":                   ("rw", "nrv04_vast_launch  (firm sub-lane)"),
    "ternary-vast":                        ("rw", "ternary_vast_launch  (legs/ stagecache/ preequilcache/ "
                                                  "setupcache/ commits/; also the 5a-KS lane)"),
    "nr4a3-bioemu-crosscheck":             ("rw", "nr4a3_bioemu_vast_launch"),
    "nr4a-paralogue-ensemble":             ("rw", "nr4a_paralogue_md_vast_launch"),
    "vast":                                ("rw", "gpu_backend.s3_checkpoint_uri  (JobSpec.checkpoint_uri)"),
}

# Co-fold OUTPUT prefixes are chosen by the operator at dispatch time and must be FRESH every run
# (`nrv04_vast_launch.py:1215-1217`, and the workflow inputs say so), so they cannot be enumerated. The
# repo's naming convention puts "cofold" in every one of them (`rung5aks-cofold-v1`, `nrv04-covalent-cofold`),
# so the policy grants the PATTERN instead — IAM resource ARNs and StringLike conditions both take `*`.
# This is the one place the scoping is looser than an enumeration, and it is a deliberate trade: the
# alternative is a fleet whose operator-named output prefix silently 403s.
WILDCARD_RW_PREFIXES = ("*cofold*",)

# Not in the policy on purpose: `mdenv/` (the packed MD env tarball) is fetched through a **presigned URL**
# minted in CI (`nrv04_vast_launch.py:497-512`), so the host needs no credential for it at all. That is the
# pattern to prefer for every future host-side read — it is strictly better than any IAM scoping.
PRESIGNED_ONLY_PREFIXES = ("mdenv",)


def rw_prefixes() -> list:
    return sorted([p for p, (a, _) in LANE_PREFIXES.items() if a == "rw"]) + list(WILDCARD_RW_PREFIXES)


def ro_prefixes() -> list:
    return sorted([p for p, (a, _) in LANE_PREFIXES.items() if a == "ro"])


def _obj_arns(bucket: str, prefixes) -> list:
    return [f"arn:aws:s3:::{bucket}/{p.strip('/')}/*" for p in sorted(prefixes)]


def _list_conditions(prefixes) -> list:
    """`aws s3 ls s3://b/p` sends the bare prefix while `--recursive`/`sync` send `p/…`, so both forms are
    needed or the idempotency probe 403s while the sync loop works — a difference nothing would report."""
    out = []
    for p in prefixes:
        p = p.strip("/")
        out += [p, f"{p}/*"]
    return sorted(set(out))


def leg_policy_document(bucket: str = DEFAULT_BUCKET, prefixes=None) -> dict:
    """The IAM policy for the leg credential.

    `prefixes=None` -> every registered lane: this is the document for the standing `vast-leg-s3` IAM user.
    Pass an explicit list (normally one result prefix) to get the narrower document used as a per-rental
    STS session policy. Read-only lanes keep their read-only grant in both cases.
    """
    if prefixes is None:
        rw, ro = rw_prefixes(), ro_prefixes()
    else:
        want = {p.strip("/") for p in prefixes}
        rw = sorted(want & set(rw_prefixes())) or sorted(want - set(ro_prefixes()))
        ro = sorted(want & set(ro_prefixes())) or ro_prefixes()   # a leg still needs the shared inputs
    stmts = [{
        "Sid": "LegResultIO",
        "Effect": "Allow",
        "Action": list(LEG_OBJECT_ACTIONS),
        "Resource": _obj_arns(bucket, rw),
    }]
    if ro:
        stmts.append({
            "Sid": "LegSharedInputsReadOnly",
            "Effect": "Allow",
            "Action": list(LEG_READONLY_OBJECT_ACTIONS),
            "Resource": _obj_arns(bucket, ro),
        })
    stmts.append({
        # ListBucket is a BUCKET-level action, so a resource ARN cannot narrow it — the s3:prefix condition
        # is the only way to keep a leg from enumerating the whole evidence bucket.
        "Sid": "LegListOwnPrefixes",
        "Effect": "Allow",
        "Action": list(LEG_BUCKET_ACTIONS),
        "Resource": f"arn:aws:s3:::{bucket}",
        "Condition": {"StringLike": {"s3:prefix": _list_conditions(list(rw) + list(ro))}},
    })
    stmts.append({
        "Sid": "NeverDestructiveNeverSpend",
        "Effect": "Deny",
        "Action": list(LEG_DENIED_ACTIONS),
        "Resource": "*",
    })
    return {"Version": "2012-10-17", "Statement": stmts}


def leg_session_policy(bucket: str, prefix: str) -> dict:
    """The per-rental STS session policy: the same shape narrowed to ONE leg's result prefix (plus the
    shared read-only inputs it needs). STS intersects this with the calling identity's own policy, so it
    can only ever subtract — a bug here cannot widen access beyond the `vast-leg-s3` user."""
    return leg_policy_document(bucket, prefixes=[prefix])


def render(bucket: str = DEFAULT_BUCKET, prefixes=None) -> str:
    """The policy as JSON text to paste into the IAM console. The runbook points at this function rather
    than embedding a copy, so the two cannot drift."""
    return json.dumps(leg_policy_document(bucket, prefixes), indent=2)


def covers(uri_or_prefix: str) -> bool:
    """Would the scoped credential be able to WRITE here? Pure, so the launcher can warn at submit time
    instead of letting a fleet discover it as a 403 an hour into a leg."""
    body = uri_or_prefix.split("://", 1)[-1]
    key = body.partition("/")[2] if "/" in body else body
    key = key.strip("/")
    if not key:
        return False
    for p in rw_prefixes():
        if "*" in p:
            import fnmatch
            head = key.split("/", 1)[0]
            if fnmatch.fnmatch(head, p):
                return True
        elif key == p or key.startswith(p.strip("/") + "/"):
            return True
    return False


# --- optional stage 2: a per-rental, self-expiring credential ---------------------------------------------

# Why GetFederationToken and not AssumeRole: an AssumeRole session is capped by the role's
# MaxSessionDuration, which AWS caps at 12 h. Vast RE-RUNS the onstart script every time the container
# restarts (the idempotency guard at `protfep_vast_launch.py:104` exists precisely because of that, and the
# restart loop is recorded at :198), so a baked-in token has to outlive not the leg's compute time but the
# whole INSTANCE's lifetime including any outbid-stopped gap. Legs run 8-20 h; 12 h has no margin.
# GetFederationToken allows 36 h and accepts a session policy, which GetSessionToken does not. A federated
# session also cannot call IAM or STS, so a leaked token cannot mint itself a successor.
STS_MAX_TTL_S = 129600          # 36 h — AWS's ceiling for GetFederationToken
STS_DEFAULT_TTL_S = 129600      # take the ceiling: a short TTL's failure mode is a leg that runs to
                                # completion and then cannot upload, i.e. GPU hours spent for nothing.


def sts_grant_statement() -> dict:
    """The extra statement the `vast-leg-s3` user needs before stage 2 can work. Kept OUT of the stage-1
    policy so the standing key cannot mint anything until that is a deliberate act."""
    return {
        "Sid": "MintPerRentalSessions",
        "Effect": "Allow",
        "Action": "sts:GetFederationToken",
        "Resource": "arn:aws:sts::*:federated-user/*",
    }


def federation_name(name: str) -> str:
    """STS federated-user names allow [\\w+=,.@-] and cap at 32 chars; leg ids carry '__' and run longer.
    Pure, so the sanitisation is unit-tested rather than discovered as a ValidationError at launch."""
    safe = "".join(c if (c.isalnum() or c in "+=,.@-_") else "-" for c in str(name))
    return safe[:32] or "vast-leg"


def sts_leg_credentials(bucket: str, prefix: str, name: str, ttl_s: int = STS_DEFAULT_TTL_S,
                        source_env=None) -> dict:
    """Mint a temporary, prefix-scoped credential triple for ONE rental. Returns {} when unavailable.

    FAILS OPEN BY DESIGN. Every caller must fall back to the long-lived scoped key, because a launcher that
    refuses to launch when STS is unreachable is a worse outcome than one that hands over the (already
    scoped) standing key. The one fallback it must never take is the broad CI key — that is enforced in
    `gpu_backend._object_store_env`, not here, which is why this function reads only VAST_S3_*.
    """
    import os
    env = source_env if source_env is not None else os.environ
    if (env.get("VAST_S3_SCOPED_STS") or "").strip() not in ("1", "true", "yes"):
        return {}                                    # opt-in; stage 1 (the standing scoped key) is default
    kid, sec = env.get("VAST_S3_ACCESS_KEY_ID"), env.get("VAST_S3_SECRET_ACCESS_KEY")
    if not (kid and sec):
        return {}                                    # never derive a session from the broad CI key
    try:
        import boto3
    except ImportError:
        return {}
    ttl = max(900, min(int(ttl_s), STS_MAX_TTL_S))
    sts = boto3.client("sts", aws_access_key_id=kid, aws_secret_access_key=sec,
                       region_name=env.get("AWS_DEFAULT_REGION") or "us-east-2")
    r = sts.get_federation_token(Name=federation_name(name), DurationSeconds=ttl,
                                 Policy=json.dumps(leg_session_policy(bucket, prefix)))["Credentials"]
    return {"VAST_S3_ACCESS_KEY_ID": r["AccessKeyId"],
            "VAST_S3_SECRET_ACCESS_KEY": r["SecretAccessKey"],
            "VAST_S3_SESSION_TOKEN": r["SessionToken"]}


if __name__ == "__main__":                                     # `python s3_scoped_policy.py` prints the doc
    import sys
    print(render(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BUCKET))
