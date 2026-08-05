---
id: DOC-SCOPED-S3-CREDENTIAL-RUNBOOK
title: Scoped S3 credential for rented GPU hosts — what trimcrae must create in AWS
level: —
kind: runbook
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `runbook` from its location under research/compute/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# Scoped S3 credential for rented GPU hosts — what trimcrae must create in AWS

**This is the runbook for the decision recorded in
[credential-exposure-2026-07-27.md](./credential-exposure-2026-07-27.md) → "the larger issue": SCOPE THE
CREDENTIALS.** The code side is done and merged; it is transition-safe and changes nothing until the
secrets below exist. Everything left is an AWS action only trimcrae can take.

Nothing here needs designing. Steps 1–5, in order, ~10 minutes.

---

## Why, in one paragraph

`gpu_backend._vast_onstart` writes the object-store credential **in cleartext** into the onstart script of
every rented Vast community host. Vast has no secret-injection mechanism, so that is a boundary to scope,
not a bug to fix. Until now the credential crossing it was `nr4a3-ci-submitter` — and its policy
([`deploy/aws-sagemaker.cfn.yaml`](../../deploy/aws-sagemaker.cfn.yaml) lines 31–47) grants
`s3:CreateBucket/PutObject/GetObject/ListBucket/GetBucketLocation` on **`Resource: "*"`**,
`sagemaker:CreateProcessingJob` on `"*"`, and `iam:PassRole` onto a role carrying
`AmazonSageMakerFullAccess`. So the real exposure is wider than the incident note recorded: not "write
access to the evidence bucket" but **write access to every bucket in the account, plus the ability to
launch SageMaker jobs at your expense**. Every host operator this repo has rented from has held that.

The replacement credential can do six S3 actions, inside one bucket, under the lane prefixes a leg
actually touches, and nothing else. It cannot delete, cannot spend, cannot reach IAM.

---

## Step 1 — create the customer-managed policy `vast-leg-s3`

IAM → Policies → Create policy → JSON. Name it exactly **`vast-leg-s3`**.

> It must be a **customer-managed** policy, not an inline user policy: inline policies on a user are capped
> at 2048 characters and this document is ~2.4 kB minified. Managed policies allow 6144.

<!-- BEGIN GENERATED POLICY — do not hand-edit. Regenerate with:
     python3 research/modalities/s3_scoped_policy.py
     tests/test_s3_scoped_policy.py fails if this block drifts from the generator. -->
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LegResultIO",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:AbortMultipartUpload",
        "s3:ListMultipartUploadParts"
      ],
      "Resource": [
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/*cofold*/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/nr4a-paralogue-ensemble/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/nr4a3-bioemu-crosscheck/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/nr4a3-step1-fanout/results/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/nrv04-covalent-results/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/nrv04-ffcache/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/nrv04-retro-results/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/protfep-benchmark/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/ternary-vast/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/vast/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/vast-bench-results/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/vast-firm-results/*"
      ]
    },
    {
      "Sid": "LegSharedInputsReadOnly",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/nr4a3-step1-fanout/stage/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/nrv04-covalent-cofold/*",
        "arn:aws:s3:::sagemaker-us-east-2-646605541856/nrv04-descriptive-v4/*"
      ]
    },
    {
      "Sid": "LegListOwnPrefixes",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::sagemaker-us-east-2-646605541856",
      "Condition": {
        "StringLike": {
          "s3:prefix": [
            "*cofold*",
            "*cofold*/*",
            "nr4a-paralogue-ensemble",
            "nr4a-paralogue-ensemble/*",
            "nr4a3-bioemu-crosscheck",
            "nr4a3-bioemu-crosscheck/*",
            "nr4a3-step1-fanout/results",
            "nr4a3-step1-fanout/results/*",
            "nr4a3-step1-fanout/stage",
            "nr4a3-step1-fanout/stage/*",
            "nrv04-covalent-cofold",
            "nrv04-covalent-cofold/*",
            "nrv04-covalent-results",
            "nrv04-covalent-results/*",
            "nrv04-descriptive-v4",
            "nrv04-descriptive-v4/*",
            "nrv04-ffcache",
            "nrv04-ffcache/*",
            "nrv04-retro-results",
            "nrv04-retro-results/*",
            "protfep-benchmark",
            "protfep-benchmark/*",
            "ternary-vast",
            "ternary-vast/*",
            "vast",
            "vast-bench-results",
            "vast-bench-results/*",
            "vast-firm-results",
            "vast-firm-results/*",
            "vast/*"
          ]
        }
      }
    },
    {
      "Sid": "NeverDestructiveNeverSpend",
      "Effect": "Deny",
      "Action": [
        "s3:DeleteObject",
        "s3:DeleteObjectVersion",
        "s3:PutObjectAcl",
        "s3:PutBucketAcl",
        "s3:PutBucketPolicy",
        "s3:DeleteBucketPolicy",
        "s3:PutBucketVersioning",
        "s3:CreateBucket",
        "sagemaker:*",
        "iam:*",
        "sts:AssumeRole"
      ],
      "Resource": "*"
    }
  ]
}
```
<!-- END GENERATED POLICY -->

**What each statement is for**, so you can sanity-check it rather than trust it:

| Sid | grants | why a leg needs it |
|---|---|---|
| `LegResultIO` | Get/Put + multipart abort/list-parts on the **result** prefixes | checkpoints, `leg_*.json`, `run.log`, `phase.txt`, the ternary stage/pre-equil/setup caches, the `S3CommitStore` commits |
| `LegSharedInputsReadOnly` | **Get only** on the shared **input** prefixes | staged receptor/ligand poses, co-folded CIFs, the pinned retro inputs — read by many legs, written by none, so one compromised host cannot poison every other leg |
| `LegListOwnPrefixes` | `ListBucket` **confined by `s3:prefix`** | `aws s3 ls` idempotency probes, `cp --recursive`, `sync`. `ListBucket` is bucket-level, so the condition is the only thing stopping a leaked key from inventorying the whole evidence bucket. Both `p` and `p/*` are listed because the bare form is what `aws s3 ls s3://b/p` sends |
| `NeverDestructiveNeverSpend` | explicit **Deny** | survives some future policy being attached to the same user by mistake — the realistic way this scoping gets quietly undone |

Two deliberate calls worth knowing:

- **No `s3:DeleteObject`, and that changes nothing today.** One host-side call deletes —
  `nrv04_covalent_md._rm_ckpt` shells out to `aws s3 rm` for a finished leg's two `ckpt_*` objects — but the
  key being forwarded right now has no delete grant either (the CFN lists five actions, none of them a
  delete), so that call already fails silently on every leg. Withholding it reproduces current behaviour
  exactly and means a leaked leg credential cannot destroy evidence.
- **`*cofold*` is the one wildcard.** Co-fold output prefixes are chosen by the operator at dispatch and
  must be fresh every run (`nrv04_vast_launch.py:1215`), so they cannot be enumerated; the repo's naming
  convention puts `cofold` in all of them. The alternative was a co-fold whose operator-named prefix
  silently 403s.

## Step 2 — create the user and attach the policy

IAM → Users → Create user, name **`vast-leg-s3`**. No console access. Attach `vast-leg-s3` (the policy from
step 1) directly — **nothing else, no groups**. Then Security credentials → Create access key → "Application
running outside AWS". Copy both halves once.

## Step 3 — put the key in repo secrets under its OWN names

GitHub → Settings → Secrets and variables → Actions:

| secret | value |
|---|---|
| `VAST_S3_ACCESS_KEY_ID` | the `vast-leg-s3` access key id |
| `VAST_S3_SECRET_ACCESS_KEY` | its secret |

**Do not overwrite `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`.** CI still needs the broad key for
SageMaker submission, the reduce/analysis jobs and the reap — that key stays in CI and never leaves it.
The moment both new secrets exist, `gpu_backend._object_store_env` forwards the scoped credential to rented
hosts **and stops forwarding the broad one**; before that it falls back to the old behaviour, which is why
the legs running when this landed were never at risk of losing their upload path.

The launcher prints which credential a rental got, without printing any part of it:

```
  [cred] object-store credential: scoped
  [cred] object-store credential: inherited  ** BROAD CI KEY — see .../scoped-s3-credential-runbook.md **
```

Watch for `scoped` on the first rental after you set the secrets. If a lane's prefix were somehow missing
from the policy, the same readout warns at launch rather than letting the leg 403 hours later.

## Step 4 — rotate the exposed key (still outstanding)

The `nr4a3-ci-submitter` key `AKIA…CL5W` must be treated as compromised: it went into a public CI log for
~25 minutes, and — the larger point — it has been handed to every Vast host rented since the fan-out began.
IAM → Users → `nr4a3-ci-submitter` → Security credentials → create a new key, update the two repo secrets,
then **delete** the old key (deactivate first if you want a rollback window).

While you are there, consider narrowing that user too. It does not need `s3:*` on `Resource: "*"` or
`s3:CreateBucket`; scoping its S3 statement to `arn:aws:s3:::sagemaker-us-east-2-646605541856` and the
SageMaker default bucket would leave it fully functional. That is a separate change to
`deploy/aws-sagemaker.cfn.yaml` and is **not** required for step 3 to be safe.

## Step 5 — turn on bucket versioning (the one thing scoping cannot do)

S3 → `sagemaker-us-east-2-646605541856` → Properties → Bucket Versioning → Enable.

`s3:PutObject` on a prefix is also permission to **overwrite** it. A leaked scoped key still cannot delete,
spend, or reach another bucket, but it can overwrite the lanes it covers. Versioning is what makes that
recoverable, and the policy denies `s3:PutBucketVersioning` so a host cannot switch it back off. Storage
cost is small: checkpoints are overwritten, not appended, and a lifecycle rule expiring noncurrent versions
after 30 days caps it.

---

## Optional stage 2 — a per-rental credential that expires

Implemented and **off by default**. Stage 1 gives one long-lived scoped key shared by every concurrent
rental, so leg A's host can write leg B's prefix. Stage 2 mints a **separate credential per rental**, scoped
to that leg's own prefix, that expires on its own.

To enable: add `sts:GetFederationToken` to the `vast-leg-s3` policy —

```json
{
  "Sid": "MintPerRentalSessions",
  "Effect": "Allow",
  "Action": "sts:GetFederationToken",
  "Resource": "arn:aws:sts::*:federated-user/*"
}
```

— then set repository **variable** `VAST_S3_SCOPED_STS=1`.

**Why `GetFederationToken` and not `AssumeRole`.** Vast re-runs the onstart script every time the container
restarts (the idempotency guard at `protfep_vast_launch.py:104` exists for exactly that, and a restart loop
is recorded at `:198`), so a baked-in token must outlive not the leg's compute time but the **instance's**
lifetime, including any outbid-stopped gap. Legs run 8–20 h. An `AssumeRole` session is capped by the role's
`MaxSessionDuration`, which AWS caps at **12 h** — no margin at all, and the failure mode is a leg that runs
to completion and then cannot upload. `GetFederationToken` allows **36 h** and accepts a session policy,
which `GetSessionToken` does not. A federated session also cannot call IAM or STS, so a leaked token cannot
mint itself a successor.

The session is derived from the `vast-leg-s3` key, never the CI key, so STS intersects the session policy
with an already-scoped identity — a bug in the session policy can only ever subtract. If STS is unreachable
the launcher **falls back to the standing scoped key** rather than refusing to launch.

---

## Where each fact lives

Per the one-fact-one-place rule, nothing here is the source of truth for the policy itself:

- **the actions, prefixes and policy shape** → [`research/modalities/s3_scoped_policy.py`](../modalities/s3_scoped_policy.py).
  `python3 research/modalities/s3_scoped_policy.py` prints the JSON block above; a test fails if this
  document drifts from it.
- **which credential is forwarded, and the choke point that decides** →
  `gpu_backend._object_store_env` / `object_store_cred_mode`.
- **what crosses the boundary into a rental** → the `_vast_onstart` docstring.
- **the incident** → [credential-exposure-2026-07-27.md](./credential-exposure-2026-07-27.md).
- **the guards** → `research/modalities/tests/test_s3_scoped_policy.py` (both directions: no wider than a
  leg needs, no narrower than the launchers reach for) and `tests/test_vast_diag_redaction.py`.
