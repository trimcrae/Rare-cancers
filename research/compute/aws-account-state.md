---
id: DOC-AWS-ACCOUNT-STATE
title: AWS account state — what is left after the 2026-08-12 purge, and what a lane will no longer find in S3
level: —
kind: runbook
status: live
canonical_for: [aws-account-contents, aws-residual-spend, aws-ci-key-permissions]
purpose: One home for what this repo still holds in AWS, what was deleted on 2026-08-12 and why, and which residual charges are blocked on IAM rather than on a decision.
scope: The AWS account 646605541856 only. Vast/GCP provider facts live in cheap-gpu-plan.md, vast-placement-facts.md and gcp-gpu-facts.md; cost evidence lives in pricing.md.
audience: [maintainers, autonomous research agents]
date: 2026-08-12
last_verified: 2026-08-12
---

# AWS account state — what is left, and what a lane will now NOT find there

**One home for "what does this repo still have in AWS".** Written 2026-08-12, when the account was
emptied. Read it before dispatching any lane that expects to read something out of S3.

Account `646605541856`, region `us-east-2`. Production compute is on Vast
([CLAUDE.md §6](../../CLAUDE.md), "Provider facts"); AWS holds no compute and, as of this file, almost
no storage.

---

## 1 · Why the account was emptied

trimcrae, 2026-08-12: *"We're still using AWS budget somehow. Must be storage I'm thinking? I want to
shut that off"* — then, shown the numbers: *"You can delete everything. These leads are dead and
documented."*

The measurement behind that decision, from
[`aws-spend-census.json`](../modalities/aws-spend-census.json):

| source | measured | est $/mo at list |
|---|---|---|
| `s3://sagemaker-us-east-2-646605541856` | 2,707 GB, 119,082 objects | **$62.27** |
| ECR (`nr4a3-abfe` 9.66 GB, `nr4a3-fep` 9.16 GB) | 18.81 GB | $1.88 |
| CloudWatch Logs (2 groups, both never-expire) | 0.031 GB | ~$0 |
| SageMaker endpoints / notebooks / Studio apps / running jobs | **none**, all reads `ok` | $0 |
| EBS volumes + snapshots | **UNKNOWN** — `DENIED` in all three regions | not counted |

97.8 % of the bucket was three prefixes of finished FEP output: `nr4a3-step1-fanout/` (1,357 GB),
`ternary-vast/` (1,223 GB) and `nr4a3-step1-pilot-rbfe/` (67 GB).

⚠ **The dollar figures are estimates at public list price, not the bill.** `ce:GetCostAndUsage` is denied
to the CI key, so nothing here has read an invoice. And because EBS could not be read at all, the $64.15
total is a **floor**, not a total — see §4.

**The routes were confirmed finished before anything was deleted, not assumed idle:** all 18
`ternary-vast-watch.json` entries disabled with a LANDED/`done` `leg.json`; `step1-fanout-map.json` at
18 of 19 units complete with the 19th blocked on a mapper limitation rather than on compute; and the Vast
account census reading `n_instances: 0`.

## 2 · What was deleted

`s3://sagemaker-us-east-2-646605541856` — **118,054 objects, 2,692.43 GB.** The bucket now holds one
object (§3). Ledger: [`aws-spend-shutdown.json`](../modalities/aws-spend-shutdown.json).

⚠ **THE CENSUS WILL KEEP REPORTING ~$62/mo FOR UP TO 24 HOURS, AND THAT IS NOT A FAILED PURGE.**
Per-bucket size comes from the CloudWatch `AWS/S3 BucketSizeBytes` metric, which AWS publishes **once a
day** — it is the number the bill is computed from, which is why the census uses it instead of walking
119k objects. The post-purge census at 2026-08-12 23:54Z still read `total_gb: 2707.47` from that stale
metric while its own **object walk in the same run returned `keys_walked: 1`**. The walk is the live
reading; the metric catches up on AWS's schedule. Do not re-run the purge on the strength of the metric.

★ **The bucket was measured UNVERSIONED before the purge, and that mattered.** On a versioned bucket
`DeleteObject` writes a delete marker and the version keeps billing in full — the purge would have
reported complete success, freed nothing, and the defect would have surfaced four weeks later on an
invoice with the data already unreachable. Both reads that would answer the question
(`GetBucketVersioning`, `ListBucketVersions`) are denied to this key, so it was settled by experiment:
the `DeleteObject` response carries `VersionId`/`DeleteMarker` on a versioned bucket and neither
otherwise. It carried neither.

## 3 · What SURVIVES, and what a lane will now fail to find

**Kept deliberately — `mdenv/nrv04md.tar.gz` (6.27 GB).** Not a result: it is the conda-packed MD
environment every NR-V04 Vast instance fetches at launch by presigned URL
(`nrv04_vast_launch.MDENV_KEY`), built by the conda-pack job in `fusion-cpu-extras.yml`. The deletion was
authorised for dead *leads*; removing this would have freed $0.14/mo and silently broken the next launch,
which would then fail at fetch time with nothing pointing back at the cleanup.

⛔ **EVERYTHING ELSE IS GONE, AND SOME OF IT WAS NOT A RESULT.** A lane re-dispatched today will not find:

* **`selcal-boltz-cache/`** (was 7.47 GB, 45,230 objects) — cached Boltz co-folds. Regenerating them is
  **GPU work**, not a download. A selcal re-run will recompute from scratch.
* **staged inputs** under the per-lane prefixes (`.../stage/`) — re-stage before re-launching anything.
* **every raw trajectory and per-unit checkpoint** for the step-1 fan-out, the ternary lane, the ABFE and
  metad runs, and the NR-V04 panels.

**The reduced results were the premise of the deletion and they are in git**, not in S3 —
`step1-fanout-map.json` (per-edge ΔΔG, cycle closure, ranking), the ternary lane's per-leg `leg.json`
values recorded in `ternary-vast-watch.json`, and the committed artifacts each lane publishes. What is
gone is the ability to **re-analyse** — a different MBAR treatment, a convergence plot a reviewer asks
for, or any measurement not already reduced into a committed artifact. Re-deriving means re-renting GPUs.

## 4 · What is still billing, and what is blocked on IAM

The CI key is `arn:aws:iam::646605541856:user/nr4a3-ci-submitter`. It holds object-level S3 rights and
essentially nothing else — measured in [`aws-spend-probe.json`](../modalities/aws-spend-probe.json):

| still costs | ~$/mo | why it is still there |
|---|---|---|
| ECR `nr4a3-abfe` + `nr4a3-fep` | $1.88 | **`ecr:DeleteRepository` AND `ecr:BatchDeleteImage` both denied.** Both were tried; they are different IAM actions and neither is granted. Needs a console delete or an IAM change. |
| CloudWatch Logs, 2 groups | ~$0.001 | `logs:PutRetentionPolicy` denied. Negligible, listed for completeness. |
| `cf-templates-v2kjpo1se7g0-us-east-2` | ~$0 | 4 objects, ~10 KB. The key is not scoped to this bucket. |
| EBS volumes / snapshots | **UNKNOWN** | `ec2:DescribeVolumes` denied in every region, so this has never been read. It is not known to be zero. |

⚠ **A stray probe object was left behind:** `s3://cf-templates-…/_spend-probe/versioning-check.txt`
(~31 bytes). The versioning probe writes before it deletes, and `DeleteObject` is denied on that bucket,
so it cannot be removed with this key. Recorded here rather than left for a future census to discover as
an unexplained row.

**Three things only trimcrae can settle**, none of them urgent at these amounts:

1. **The ECR images** — a console delete, or add `ecr:BatchDeleteImage` to the CI user.
2. **Whether EBS is really empty** — add `ec2:DescribeVolumes`, or look once in the console. This is the
   only remaining candidate that could be more than pennies, and it has never been read.
3. **Whether the bill matches** — `ce:GetCostAndUsage` on the CI user would let the census read the
   actual invoice instead of estimating from sizes at list price. Until then every dollar figure in this
   repo's AWS accounting is inferred.

## 5 · If AWS storage is ever used again

`object_store.py` is provider-agnostic and its own header recommends **Cloudflare R2** over S3 for exactly
this workload: S3 charges ~$0.09/GB egress and the checkpoint store is read from rented GPUs on another
provider, so every resume pays to leave AWS. R2's egress is $0. That was never acted on because the
SageMaker default bucket already existed; a fresh start has no such reason to prefer S3.
