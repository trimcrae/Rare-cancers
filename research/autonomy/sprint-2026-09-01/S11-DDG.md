---
id: DOC-SPRINT-S11-DDG
title: "S11-DDG — why the step-1 fan-out results prefix has zero ddg.json objects"
level: L4
kind: incident
status: live
date: 2026-09-01
last_verified: 2026-09-01
purpose: "Root-cause, with cited evidence, why s3://sagemaker-us-east-2-646605541856/nr4a3-step1-fanout/results/ holds zero ddg.json objects (ledger AUT-078), and record what is still unmeasured and what it is waiting on."
scope: "The 2026-08-13 object loss in the SageMaker default bucket, across the three prefixes any committed listing covers. NOT the separate 2026-07-10 loss, which was never measured this way. NOT a claim about the actor, which the free evidence does not reach."
audience: [maintainers, autonomous research agents]
---

# S11-DDG — the step-1 fan-out S3 loss, root-caused to a single bucket-wide deletion event

**Item(s):** AUT-078 **Owned paths:** `research/autonomy/sprint-2026-09-01/S11-DDG.md`,
`research/compute/s3_loss_forensics.py` **Started/Finished (UTC):** 2026-09-01T18:41Z / 2026-09-01T19:12Z

## Verdict

**PARTIAL — the mechanism is established and the ledger row's framing is REFUTED; attribution and
recoverability remain UNKNOWN behind one named, non-free observation.**

The 18 `ddg.json` objects were not selectively lost. **Every object then present in
`s3://sagemaker-us-east-2-646605541856` was deleted in a single event bracketed to an 8-minute window,
2026-08-13T00:23:2xZ – 00:31:38Z** (8:23–8:31 PM ET Aug 12). It has not recurred. What remains under
`nr4a3-step1-fanout/results/` today is not survivors — it is ten *lane-state files the CI tick has
rewritten since*, every one of them empty or zeroed.

⚠ **An S3 lifecycle expiration — the mechanism this repository has assumed twice, in
`archive_results.py`'s header and in `results/PROVENANCE.md` — is REFUTED by the shape of the loss.**
Two independent properties rule it out (§ "The observation that discriminates", C and D).

⚠ **The realised-spend ledger for this lane was destroyed with everything else.**
`nr4a3-step1-fanout/results/_rentals.json` now reads `"rentals": {}` — the $73.79 figure survives only
because git holds it. Nobody has recorded this; it is not in AUT-078 and not in AUT-PD-015.

---

## What I measured

### 0 · What is actually knowable from this sandbox — measured, not assumed

**S3 is reachable from here; the credentials are not real.** `AWS_ACCESS_KEY_ID` in this sandbox is the
literal 14-character string **`proxy-injected`** — a harness placeholder, not an AWS key (real ids are 20
chars, `AKIA`/`ASIA`). `pip install boto3` succeeds (pypi is in `NO_PROXY`), the request reaches AWS, and
AWS itself answers:

```
STS  GetCallerIdentity -> ClientError InvalidClientTokenId: The security token included in the request is invalid.
S3   ListObjectsV2     -> ClientError InvalidAccessKeyId:  The AWS Access Key Id you provided does not exist in our records.
```

Those are **AWS** errors returned through the egress proxy, not proxy denials, so the network path to
`s3.us-east-2.amazonaws.com` is open and only the identity is missing. CYC-0022 recorded the same
`InvalidAccessKeyId` but not *why*; the reason is that the value is a sentinel, so no amount of retrying or
region-fiddling would ever have helped. **⛔ Do not re-file "this sandbox's AWS credentials are invalid" as
a mystery: it is by design.** The route out is rung 1 of `ci-escape-hatches` — an Actions runner holding
the real `nr4a3-ci-submitter` secrets — and that is what produced the live readings below.

Also blocked from here: `GET /actions/jobs/<id>/logs` 302-redirects to
`productionresultssa6.blob.core.windows.net`, which the egress proxy refuses (`connect_rejected`). Job logs
must come through `mcp__github__get_job_logs`, which fetches server-side. The plain Actions **JSON** API is
unauthenticated-readable from here (public repo) and was used throughout.

### 1 · The defect still exists, and it is bigger than the row says (refute-by-default, rule 4)

Fresh live reading, taken today by dispatching the existing on-main `archive-results-aws.yml` at
`mode=diagnose` (read-only; its commit step is gated `if: mode != 'diagnose'` and was **skipped**) —
run [33546313493](https://github.com/trimcrae/Rare-cancers/actions/runs/33546313493), job 99984572162,
2026-09-01T18:54:02Z:

```
[diagnose] nr4a3-step1-fanout:  {'archive': 10,   ...} (10 objs)
[diagnose] ternary-vast:        {'archive': 2,    ...} (2 objs)
[diagnose] nrv04-retro-results: {'archive': 2856, ...} (2856 objs)
[diagnose] no lifecycle configuration returned (AccessDenied: ... User: arn:aws:iam::646605541856:user/
           nr4a3-ci-submitter is not authorized to perform: s3:GetLifecycleConfiguration ...)
```

So the state AUT-078 describes is **live as of today**, and the same credentials that see 10 objects under
one prefix see 2,856 under a sibling prefix in the same bucket in the same call. The row is not stale.

### 2 · The event, from the repository's own committed instrument

`research/modalities/step1-terminus-evidence.txt` is regenerated by `step1_terminus_evidence.py` on every
autoscale tick and prints the raw object count. Its committed history:

| commit | UTC | objects under `nr4a3-step1-fanout/results/` | `ddg=YES` units |
|---|---|---|---|
| `fa4ca5c43` | 2026-08-06T22:31:31Z | **8510** | **18** |
| `3ebf91553` | 2026-08-26T19:18:12Z | **10** | **0** |
| `592b7f4f6` | 2026-09-01T10:03:44Z | **10** | **0** |

`git log -S 'ddg=YES'` on that file returns exactly two commits — `2aa4dcb2f` (first appearance) and
`3ebf91553` (disappearance) — so the transition is a single step in the committed record.

**8,510 → 10 is not a loss of ddg.json files.** It is the loss of the 18 results *and* the ~8,480-object
spot commit store behind them (the `complex/production@2000`, `solvent/warmup@400` … `COMMITTED.json`
census printed in the `fa4ca5c43` version) *and* the permanent-exclusion record: the Aug 6 artifact prints a
`PERMANENTLY EXCLUDED — 1 of 19` block and a denominator of 18; today's prints no exclusions and a
denominator of 19, because `nr4a3-step1-fanout/results/_blocked_units.json` is gone too.

**⛔ The 20-day gap between those two commits is not a gap in ticks.** The workflow ran **5,360 times**
between 2026-08-06 and 2026-08-28 (Actions API, `created=2026-08-06..2026-08-28`). Nothing was committed
because `publish_artifacts.sh` is heartbeat-gated: every tick in that window printed
`[publish] IDLE — nothing to supervise, so this heartbeat carries no information and is not committed`
(verbatim, run 31980467139 job 95246365423, 2026-08-16T23:56:43Z). **The lane measured the loss on every
tick for thirteen days and committed none of those readings**, because the gate keys on *whether a fleet is
billing*, not on *whether the measurement changed*.

### 3 · The ten "survivors" are not survivors

`results/nr4a3-step1-fanout/MANIFEST.json` (written by the archive run of 2026-08-26T20:15Z, commit
`324d02134`) names all ten:

```
_board_prev.json  _idle_prev.json  _map.json  _progress_prev.json  _rentals.json
_start_state.json _started_machines.json _terminal_state.json _util_state.json  market_hold.json
```

**Every one is a mutable lane-state file the tick rewrites**, and every one is empty or zeroed:
`_idle_prev.json`, `_start_state.json`, `_terminal_state.json`, `_util_state.json` are `{}` (2 bytes each);
`_rentals.json` is `{"rentals": {}}`; `_started_machines.json` is `{"machine_ids": [], "updated_utc":
"2026-09-01T11:50:14Z"}`. **No object written by a GPU host survives.** The set is exactly "what a CI tick
has written since the event", which is the observation everything below turns on.

### 4 · The observation that discriminates

Four readings, all free, all from committed artifacts or the public Actions API.

**A · The cutoff is an instant, not a prefix.** The archive workflow lists several prefixes in the same
bucket with the same credentials. On 2026-08-26 it wrote a MANIFEST for exactly three of its 25 default
prefixes — the other 22 were empty. Of the three: `nr4a3-step1-fanout` = 10, `ternary-vast` = 1
(`_lane_state.json`), `nrv04-retro-results` = 2,368. The first two are lanes that stopped writing before
mid-August; the third is a lane that writes every ~8 minutes. **Survival tracks "did anything write here
after time T", not "which prefix".**

**B · T is bracketed to eight minutes.** 2,820 of the 2,825 `nrv04-retro-results` keys carry their creation
instant in the key name (`collect/nrv04-retro-collect-<YYYYMMDD>T<HHMMSS>Z.json`). Sorted:

```
oldest surviving key = 20260813T003138Z, then 003947, 004802, 005613, 010421 …  (~8 min cadence)
nothing older exists, in either the 2026-08-26 or the 2026-09-01 listing
```

These objects are written by `fusion-cpu-extras.yml` (`vast_launch_mode=retro_collect` →
`RETRO_COLLECT=1`), which ran that night at 00:22:56Z, 00:31:11Z and 00:39:22Z. The surviving keys sit
+27 s and +25 s after the last two run starts; **the object the 00:22:56Z run would have written at
≈00:23:22Z is absent.** So the deletion happened after that write and before 00:31:38Z.
⚠ *Stated at its true weight: I read the run list and the +25–27 s offset, not the 00:22:56Z run's own log
line naming its key. The 1:1 run→key correspondence across the following runs is the evidence; the
assumption-free version of the claim is "no object created anywhere in these three prefixes before
2026-08-13T00:31:38Z survives".*

**C · A recurring age-based rule is refuted — nothing has been deleted since.** Set-difference of the
`nrv04-retro-results` manifests six days apart (`324d02134` → `cce2662ad`): **457 keys added, 0 keys
removed**, and the oldest surviving key is `20260813T003138Z` in *both*. Under any live
`Expiration: Days=N` rule the 2026-08-13 cohort would have aged out during those six days. It did not. The
event was **one-shot**.

**D · The cutoff is not a UTC midnight, which is where a lifecycle rule must put it.** S3 lifecycle
expiration is expressed in whole days and evaluated against a midnight-UTC boundary, and its deletions are
asynchronous and smeared over hours. The observed boundary is sharp to eight minutes and sits at
**00:23–00:31 UTC**, with the 00:07Z and 00:15Z objects of 2026-08-13 — comfortably *after* midnight —
deleted alongside everything older. Lifecycle expiration cannot produce that shape.

⚠ **C and D together are why `archive_results.py`'s header sentence — "*almost certainly* to an S3
lifecycle expiration" — must not be carried forward as the mechanism for this event.** It is a "probably"
of exactly the kind CLAUDE.md §4 forbids, it is the load-bearing claim of `results/PROVENANCE.md`'s owner
action item #3 ("disable the S3 lifecycle expiration"), and the data now contradicts it for 2026-08-13.
It says nothing either way about the separate 2026-07-10 loss, which was never measured this way.

### 5 · The five competing hypotheses, each answered

| # | hypothesis | verdict | the observation that settled it |
|---|---|---|---|
| a | the jobs never ran | **REFUTED** | `fa4ca5c43` lists all 18 `ddg.json` keys with sizes (993–1037 B) and mtimes (Jul 27–29), and grades all 18 `PRODUCTION` on `complex/production@2000 + solvent/production@2000` |
| b | ran and crashed before output | **REFUTED** | same reading; `research/modalities/step1-fanout-map.json` still carries 18 result rows with ΔΔG values |
| c | upload failed / wrong prefix | **REFUTED** | the objects were read at the expected keys for ~4 weeks; `VAST_CKPT_BUCKET`/`RESULT_PREFIX` have one commit in workflow history (`2aa4dcb2f`, 2026-08-04) and are unchanged since |
| d | something deleted them | **CONFIRMED, as a single bucket-wide event** | §4 A–D. *Sub-hypothesis "lifecycle expiry" is refuted by C and D; the actor is UNKNOWN (§6)* |
| e | the listing that reported zero was itself wrong | **REFUTED, three ways** | (1) the same call, same credentials, same bucket returns 2,856 objects for a sibling prefix — pagination, permissions and prefix are all sound; (2) the reading has held across four independent instruments and dates — the committed artifact at 2026-08-26T19:18Z, 2026-08-29T09:03Z and 2026-09-01T10:03Z, plus today's `archive_results.py` run at 18:54Z, which is a different code path; (3) `list_prefix` in `step1_terminus_evidence.py` uses `get_paginator("list_objects_v2")`, so there is no 1,000-key truncation |

⚠ **(e) deserved the most care and got it, because it is the one this repository forgets.** It is refuted
by a *positive* control taken in the same call, not by re-running the failing read.

### 6 · Attribution: UNKNOWN, and honestly so

Nothing in this repository performed the deletion, as far as a repository-side search can establish:

- The only bulk `delete_objects` call reachable from CI is `fep-status-aws.yml`'s optional `CLEAR_PREFIX`
  block, which is `workflow_dispatch`-only, needs an explicit non-empty input, and refuses a prefix with
  fewer than two `/` segments. `leg_failure_breaker.reset_for` deletes only
  `<prefix>/legs/<unit>/attempts/`. Neither can empty a bucket.
- **No workflow that deletes anything ran in the window.** All 48 Actions runs created between
  2026-08-13T00:15Z and 00:40Z are ternary/step-1/GCP/fusion ticks, reapers, staleness watches, `tests`,
  `Fetch literature` and `List in-progress SageMaker jobs (AWS, read-only)`.
- No commit to `main` in 2026-08-12T20:00Z–2026-08-13T04:00Z mentions S3 deletion; the session active that
  night was working on the ASO manuscript.

So the actor was outside this repository's CI. **That is where the free evidence stops.** ⛔ I am not going
to name a cause I cannot show; "a console action", "an AWS-side cleanup" and "a credential/account event"
are all consistent with what I measured and none of them is evidenced.

### 7 · Recoverability: UNKNOWN, and it is one command away for someone with the right IAM

If the bucket has versioning enabled, the deletion left delete markers and every object is recoverable via
`list_object_versions`. If it does not, the data is gone. **`ListObjectsV2` cannot tell these apart** — it
returns 10 either way — so this is genuinely unmeasured rather than deferred.

The CI identity cannot answer it: `nr4a3-ci-submitter` is already denied `s3:GetLifecycleConfiguration`
(measured today, §1), and nothing in this repository calls `get_bucket_versioning` or
`list_object_versions`, so no existing on-main workflow can be dispatched to ask.

---

## What I could not do, and what it is actually waiting on

**Three observations remain, all cheap in dollars, none reachable from CI as it stands.** Costs are stated
in access, not money — none of these is a GPU spend.

| observation | what it settles | what it actually needs |
|---|---|---|
| `aws s3api get-bucket-versioning --bucket sagemaker-us-east-2-646605541856` | whether ANY of the 8,500 objects is recoverable | **trimcrae** — or `s3:GetBucketVersioning` added to `nr4a3-ci-submitter`, after which any workflow can ask |
| `aws s3api list-object-versions --bucket … --prefix nr4a3-step1-fanout/results/ --max-items 50` | if versioning is on: the delete markers, their timestamps **and the deleting principal per object** — this would settle §6 outright | **trimcrae**, or `s3:ListBucketVersions` on that identity |
| CloudTrail `DeleteObject`/`DeleteObjects` events, 2026-08-13T00:20Z–00:35Z | the actor, if the trail exists and covers S3 data events | **trimcrae** — S3 *data* events are not logged by default, so this may return nothing, and an empty trail is not evidence of no deletion |
| `aws s3api get-bucket-lifecycle-configuration --bucket …` | whether a rule exists at all (bearing on 2026-07-10, not on this event) | **trimcrae**, or `s3:GetLifecycleConfiguration` on that identity |

⛔ **The cheapest unblocking act is not any of the four — it is granting the three read-only S3
permissions to `nr4a3-ci-submitter`.** That converts all four from "trimcrae must run a command" into "a
workflow can ask on a schedule", which is the difference between a one-time answer and a detector.

I did **not** rent anything, did not run a git write command, and touched no path outside my two owned
paths.

---

## What I changed

- `research/autonomy/sprint-2026-09-01/S11-DDG.md` — this file (new).
- `research/compute/s3_loss_forensics.py` — **new**, pure-stdlib, no credentials, no network. Re-derives
  §4's bracket from committed artifacts: it walks the git history of every
  `results/*/MANIFEST.json`, extracts the creation instant embedded in each key name, and reports per
  prefix the oldest surviving object and the keys added/removed between successive listings. It is the
  reproducible form of the reading that refuted the lifecycle hypothesis (0 removed in 6 days, cutoff not
  at midnight). Run: `python3 research/compute/s3_loss_forensics.py`.
  Self-test: `python3 research/compute/s3_loss_forensics.py --selftest` (pure-logic, no git).

Nothing else. In particular I did **not** touch `congeneric_fanout_vast.py`, the workflow, the ledger or
`autonomy-state.json` — the fixes below are proposals precisely because I cannot test a launcher from here.

---

## Proposed fixes (none applied — see the two defects each is against)

**FIX-1 · The regression alarm is written to a path nothing publishes.**
`congeneric_fanout_vast._write_map_guarded` writes `step1-fanout-map-regression-alarm.json` with a bare
relative filename, so it lands in the runner's CWD (the repo root, not `research/modalities/`), **and that
path is absent from the eight-file publish list in `step1-fanout-autoscale.yml`.** The file is discarded
with the runner every time. The docstring promises it is "diffable, never silently retried away"; measured,
it has never reached git — `grep -rn step1-fanout-map-regression-alarm` finds it only in the writer, its
tests and the ledger prose. *The fail-loud half of that guard does work* (the tick job has conclusion
`failure` on every run since), so this is a lost artifact rather than a lost alarm.
**Fix:** write to `research/modalities/step1-fanout-map-regression-alarm.json` (absolute, off
`os.path.dirname(__file__)`) and add that path to the publish list. Mutation test: force a regression in a
scratch copy, assert the file appears at the published path.

**FIX-2 · The heartbeat gate hid a thirteen-day-old measurement.** The lane re-measured "8,510 → 10" on
every tick from 2026-08-13 and committed none of it, because `PUBLISH_HEARTBEAT_LANE` gates on *is a fleet
billing* and this lane was idle. That is the intended behaviour for a liveness ping and the wrong
behaviour for a **content change**: `[publish] IDLE` correctly suppresses "still zero", and incorrectly
suppresses "the object store just lost 8,500 objects".
**Fix (narrow, and it does not weaken the 2026-08-06 rule):** the gate stays as-is for unchanged content,
but publishes when a *guarded* artifact's key measurement moves against its committed value — the same
condition `_write_map_guarded` already computes. An idle lane whose reading changed is exactly the case
where a commit carries information, which is the test the `fleet_armed` rule states in its own terms.

**FIX-3 · A result is not banked until it is in git, and step 1 proved it twice.** `archive-results-aws.yml`
did not carry `nr4a3-step1-fanout` in `DEFAULT_PREFIXES` until 2026-08-26, and by then there was nothing
left to mirror. The lane's own checkpointing was correct — `s3_upload_mode="Continuous"`, per-unit
commit-and-upload, which is why 8,510 objects existed at all — so **this loss is not a checkpointing
defect and no change to the upload path would have prevented it.** The gap is that S3 was treated as
durable storage for a closed result. `results/README.md` already states the rule; the missing enforcement
is that a lane declaring itself CLOSED should have its terminal artifacts mirrored into git as part of
closing, not on a weekly sweep that started three weeks late.

---

## Ledger rows the driver should write

1. **Amend AUT-078** — its `what` is now materially wrong and should not survive as written:
   `kind: fetch` → keep; `state: queued` → **`done-partial`**;
   `what`: replace "genuinely has zero ddg.json objects" framing with: *"ROOT-CAUSED 2026-09-01 (S11-DDG):
   a single deletion event bracketed to 2026-08-13T00:23:2xZ–00:31:38Z removed every object then present
   in s3://sagemaker-us-east-2-646605541856 — not just the 18 ddg.json but the ~8,480-object commit store,
   `_blocked_units.json` and the lane's `_rentals.json`. The 10 remaining objects are lane-state files the
   CI tick rewrote afterwards, all empty. An S3 lifecycle expiration is REFUTED (0 objects deleted in the
   6 days between two listings; the cutoff is not a UTC-midnight boundary). Actor UNKNOWN — no repository
   workflow that deletes ran in the window. Evidence:
   research/autonomy/sprint-2026-09-01/S11-DDG.md."*
   `blocked_by`: keep `access-only-trimcrae-has`, but narrow `blocked_evidence` to the ONE remaining
   question — versioning/recoverability — with the exact command and the IAM grant that would unblock it
   from CI.
2. **New row — `requires_trimcrae`, and it is the only thing here that needs him.** *"Grant
   `nr4a3-ci-submitter` read-only `s3:GetBucketVersioning`, `s3:ListBucketVersions` and
   `s3:GetLifecycleConfiguration` on `sagemaker-us-east-2-646605541856`, then say so — after that a
   workflow can answer whether the 2026-08-13 loss is recoverable, and can keep answering it."*
   `kind: decision`, `cost_class: free`, `state: queued`. ⛔ Needs a `notified_utc` and a real
   `PushNotification` — this is the failure mode CLAUDE.md §3 records fourteen times over.
3. **New row — FIX-1**, `kind: fix`, `cost_class: free`, `state: queued`: the regression alarm's path and
   its absence from the publish list.
4. **New row — FIX-2**, `kind: fix`, `cost_class: free`, `state: queued`: publish an idle lane's tick when
   a guarded measurement moves against its committed value.
5. **New row — correction**, `kind: fix`, `cost_class: free`: `archive_results.py`'s header and
   `results/PROVENANCE.md` owner-action #3 both assert an S3 lifecycle expiration as the cause of result
   loss. That attribution is refuted for 2026-08-13 and was never measured for 2026-07-10; both should be
   re-worded to UNKNOWN with the evidence pointer, per §4.
