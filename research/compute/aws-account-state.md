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

`s3://sagemaker-us-east-2-646605541856` — **118,075 objects, 2,698.70 GB, across three passes.**
118,037 objects / 2,692.43 GB on 2026-08-12; 17 stragglers on a re-run the same day (`delete_objects` is
eventually consistent, so a paginator walking a bucket mid-delete misses a few — 17 out of 118 k, which is
why the purge is written to be safely re-runnable); then 21 objects / 6.27 GB on 2026-08-13, being
`mdenv/nrv04md.tar.gz` plus this tool's own leftover `_spend-probe/` keys, once the tooling exemption was
overruled (§3). **The bucket is now empty.** Ledger:
[`aws-spend-shutdown.json`](../modalities/aws-spend-shutdown.json) — which holds only the LAST run, so the
per-pass figures above are the ones to cite.

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

⛔ **NOTHING SURVIVES. THE BUCKET IS EMPTY.**

⚠ *Superseded, retained: "**Kept deliberately — `mdenv/nrv04md.tar.gz` (6.27 GB).** Not a result … removing
this would have freed $0.14/mo and silently broken the next launch."* The first pass held `mdenv/` back on
that reasoning, and trimcrae overruled it the next day: *"everything saved on AWS is dead. I don't want to
spend money for stuff I'm never going to touch and that I can recreate at any time"* (2026-08-13). The
exemption was wrong on its own evidence — the same paragraph that argued for keeping the tarball also
recorded that `fusion-cpu-extras.yml` rebuilds it, and **recreatable-on-demand is exactly the category not
worth renting storage for.** The standing test is: pay for what cannot be recreated, not for what is
merely inconvenient to recreate. `mdenv/nrv04md.tar.gz` was deleted 2026-08-13.

★ **CONSEQUENCE, so the next NR-V04 launch is not a mystery:** `nrv04_vast_launch.MDENV_KEY` points at
`mdenv/nrv04md.tar.gz` and that object no longer exists, so a launch will fail at the presigned fetch.
**Rebuild it first** — the conda-pack job in [`fusion-cpu-extras.yml`](../../.github/workflows/fusion-cpu-extras.yml)
builds the env and `aws s3 cp`s it back to `s3://$VAST_CKPT_BUCKET/mdenv/nrv04md.tar.gz`. That job is
free CI; the only cost of this deletion is remembering to run it.

⛔ **AND SOME OF WHAT WENT WAS NOT A RESULT.** A lane re-dispatched today will not find:

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
| ECR `nr4a3-abfe` + `nr4a3-fep` | $1.88 | **Three separate IAM actions tried, all denied** — see below. Needs a console delete or an IAM change. |
| CloudWatch Logs, 2 groups | ~$0.001 | **Two actions tried, both denied**: `logs:PutRetentionPolicy` and `logs:DeleteLogGroup`. |
| `cf-templates-v2kjpo1se7g0-us-east-2` | ~$0 | 4 objects, ~10 KB. The key is not scoped to this bucket. |
| EBS volumes / snapshots | **UNKNOWN** | `ec2:DescribeVolumes` denied in every region, so this has never been read. It is not known to be zero. |

⚠ **A stray probe object was left behind:** `s3://cf-templates-…/_spend-probe/versioning-check.txt`
(~31 bytes). The versioning probe writes before it deletes, and `DeleteObject` is denied on that bucket,
so it cannot be removed with this key. Recorded here rather than left for a future census to discover as
an unexplained row.

★ **"BLOCKED" WAS TESTED FIVE WAYS BEFORE IT WAS WRITTEN DOWN, BECAUSE THE FIRST TWO DENIALS WERE NOT
ENOUGH TO CLAIM IT.** CLAUDE.md §0: *blocked is a claim that needs evidence, and it is usually wrong.* The
first report said "ECR needs trimcrae" after two denials; that was premature, because AWS offers a third,
unrelated way to remove images. Every route has now been exercised against the live account:

| action | route it would have taken | result |
|---|---|---|
| `ecr:DeleteRepository` | delete the repo and its images outright | `AccessDeniedException` |
| `ecr:BatchDeleteImage` | delete the images, keep the empty repo (free) | `AccessDeniedException` |
| `ecr:PutLifecyclePolicy` | let AWS *expire* all images against a policy | `AccessDeniedException` |
| `logs:PutRetentionPolicy` | let the logs age out | `AccessDeniedException` |
| `logs:DeleteLogGroup` | delete the groups | `AccessDeniedException` |

The key holds object-level S3 rights and essentially nothing else. There is no fourth route and no second
credential to try: `VAST_S3_ACCESS_KEY_ID` is a **narrower** key (six S3 actions on the lane prefixes,
`s3_scoped_policy.py`), not a more privileged one, so it cannot reach ECR either. **$0/mo is therefore not
reachable from CI** — the last $1.88 needs a human with console access, which is a 30-second job or a
one-line IAM addition.

**Three things only trimcrae can settle**, none of them urgent at these amounts:

1. **The ECR images** — a console delete, or add `ecr:BatchDeleteImage` to the CI user.
2. **Whether EBS is really empty** — add `ec2:DescribeVolumes`, or look once in the console. This is the
   only remaining candidate that could be more than pennies, and it has never been read.
3. **Whether the bill matches** — `ce:GetCostAndUsage` on the CI user would let the census read the
   actual invoice instead of estimating from sizes at list price. Until then every dollar figure in this
   repo's AWS accounting is inferred.

## 5 · The scheduled triggers were retired in the same breath, and that was the bigger risk

⛔ **DELETING THE DATA WITHOUT TOUCHING THE CRONS WOULD HAVE BEEN WORSE THAN DOING NOTHING.**
`congeneric_fanout_vast.fanout_pending` selects *"units with no `ddg.json` in S3 yet"*, and `mode_launch`'s
idempotence — *"a unit with a result is never re-submitted"* — reads that same S3 listing. **Emptying the
bucket therefore made all 19 finished edges look unrun**, and `step1-fanout-autoscale.yml` was firing on
`main` every ~8 minutes with the authority to rent GPUs. A storage cleanup had quietly armed a **compute**
re-spend of the whole tranche.

⚠ **IT DID NOT FIRE ONLY BECAUSE THE TICK WAS ALREADY BROKEN.** Measured 2026-08-13 01:38Z: the scheduled
run FAILED before reaching the launch path, and the account census confirmed `n_instances: 0` — nothing was
rented. That is luck, not a guard. Repairing the tick would have armed the re-spend, and the failure was
itself being reported by `fleet-supervision-alarm.yml` as a supervision outage, which is exactly the kind
of thing someone fixes without realising what it re-enables.

Retired on 2026-08-13, `workflow_dispatch` retained on every one so a deliberate re-run still works:

| workflow | was | why it is off |
|---|---|---|
| `step1-fanout-autoscale.yml` | `*/20` | reads remaining work from the now-empty S3; would re-buy 19 finished edges |
| `ternary-vast-watchdog.yml` | `*/15` | all 18 watch entries disabled with a LANDED `leg.json`; state purged |
| `vast-watchdog.yml` | `*/15` | account empty; nothing to recover |
| `fep-monitor-cron.yml` | `*/15` | zero SageMaker jobs in any region |
| `fleet-supervision-alarm.yml` | `0 * * * *` | was firing FAILING every tick about a fleet that does not exist |

★ **Re-arm the alarm in the SAME commit that re-arms a lane.** An unsupervised fleet is the failure
CLAUDE.md §6 was written about; the alarm is only noise while there is nothing to supervise.

⚠ **`vast-price-sample.yml` (hourly) is deliberately LEFT ON.** Its scheduled job is the rate-forensics
probe, which is read-only and rents nothing, and market-price history stays useful for whatever runs next.
It reads S3 but never writes, so it cannot repopulate the bucket.

⚠ **A `schedule:` fires from the DEFAULT BRANCH ONLY, so these edits are inert until they reach `main`.**
Until then the crons on `main` keep their old cadence. To stop them *immediately* without a merge, toggle
the workflow off in the GitHub UI (Actions → the workflow → ⋯ → Disable) — that is a repository setting,
lives in no branch, and is invisible to every checker in this repo (§ the Pages lesson in CLAUDE.md §6).

## 6 · If AWS storage is ever used again

`object_store.py` is provider-agnostic and its own header recommends **Cloudflare R2** over S3 for exactly
this workload: S3 charges ~$0.09/GB egress and the checkpoint store is read from rented GPUs on another
provider, so every resume pays to leave AWS. R2's egress is $0. That was never acted on because the
SageMaker default bucket already existed; a fresh start has no such reason to prefer S3.

---

## Appendix — recovered 2026-09-02, and the one change that was NOT taken with it

This file, `aws_spend_census.py`, `aws_spend_probe.py`, `aws_spend_shutdown.py` and their three JSON
results reached `main` on 2026-09-02 by merging `claude/aws-budget-storage-shutdown-iq8oh7`, 22 commits
that had sat unmerged since 2026-08-13. Until that merge the record that this account was actually
emptied — the applied `s3_purge` / `ecr_lifecycle_expire` / `log_delete` actions, the corrected object
count and the verified-empty bucket — existed on one ref and nowhere else.

⛔ **The branch's schedule retirements were refused, deliberately.** Its tip commit commented out the
`schedule:` block of `fep-monitor-cron.yml`, `fleet-supervision-alarm.yml`, `step1-fanout-autoscale.yml`,
`ternary-vast-watchdog.yml` and `vast-watchdog.yml`, on the 2026-08-13 reading that nothing was billing.
`main` has since re-tuned four of those five cron minutes (spreading them to `32`, `38`, `14` and `8`
past the hour), which is a later decision about the same files, and disarming five schedulers is not a
side effect a branch recovery may carry. **Whether they should be retired is a live question and this
merge does not answer it** — the argument is in the branch's commit
`8bfdce92d retire the crons the S3 purge silently armed, and prove ECR is really blocked`, and it should
be re-taken against a fresh reading of what is billing rather than against the 2026-08-13 one.
