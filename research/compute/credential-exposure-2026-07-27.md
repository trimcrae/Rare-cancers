# Credential exposure — 2026-07-27, ~3:00–3:25 AM ET

**Status: CONTAINED in the repo. NOT REMEDIATED — rotation is trimcrae's and was still outstanding
when this was written.**

## What happened

A `vast_diag` mode, written to recover a container's exit reason, dumped the **full Vast instance
record** to a GitHub Actions log. The reasoning was "we do not know which field carries the exit
reason, so print all of them."

That record embeds the rendered `onstart` script, and `gpu_backend._vast_onstart` exports the
forwarded object-store credentials into it. So the dump printed, in plaintext, to a log on a
**public** repository:

- a live `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` (key id `AKIA…CL5W`)
- the instance's `jupyter_token`

Run `30245130311`. Exposure window ~25 minutes.

Verified rather than assumed: `trimcrae/Rare-cancers` returns `private: false, visibility: public`,
and the run's logs endpoint now returns **HTTP 404**.

## Contained

- that run's logs deleted;
- the full-record dump replaced with an **allow-list** of fields;
- `test_vast_diag_redaction.py` pins that a full-record dump cannot come back.

## NOT contained — requires trimcrae

**Rotate the key**, and create the scoped one that replaces it on hosts. Both steps, in order, are
[scoped-s3-credential-runbook.md](./scoped-s3-credential-runbook.md) — the policy JSON is in it,
ready to paste. Log deletion closes the window; it is not a rotation, and the key must be treated
as compromised.

## The rotation's own cost — ROTATING A KEY STRANDS EVERY HOST THAT ALREADY BAKED IT

Not a hypothetical, and not obvious in advance: it was missed when the rotation was recommended.

Credentials are resolved **once**, at process start. `nr4a3_rbfe.py:927` builds `S3CommitStore` before the
multi-hour loop; `rbfe_spot_checkpoint.py:423-424` builds one `boto3.client("s3")` and reuses it for every
later `.commit()`. boto3 caches static env credentials at client construction and never re-reads the
environment. `_object_store_env` likewise resolves at container start. **So a host running when the key
rotates keeps the dead key for the rest of its life, and there is no route to the new one short of a restart.**

Worse, the commit callback (`rbfe_spot_driver.py:436-437`) has **no try/except**, so the first commit after
the credential died raised and killed the driver. That death is invisible: `status.json` is itself an S3
object, so `fail()` could not record it either.

Observed, 2026-07-27. Two 5a-KS ternary legs kept their S3 writes frozen from **7:27 AM ET** while still
billing, and were destroyed at **8:20 AM ET** — GPU utilisation `0.0` on reads 28 minutes apart, and the
console showing both containers in a **~13–30 s crash-loop**: stage cache MISS (an S3 *read*, also on the dead
key) → `FAILED at staging` → `Killed` → repeat, on the same rental. ~53 min of combined billing bought
nothing, ≈$0.35. The dollars are trivial; the mechanism is not.

Durable state at destroy, which is exactly what a relaunch resumes from: nr4a3 `production/800` of 2000,
nr4a1 `warmup/640` of 1600.

**MITIGATION, for the next rotation: drain or re-credential every running host BEFORE deactivating the old
key.** Never deactivate blind and discover the strandings afterwards. If draining is not possible, destroy the
in-flight legs deliberately and accept the checkpoint as the deliverable — a planned stop at a known iteration
beats an unplanned one nobody can see.

### The autoteardown hole this exposed

`autoteardown.py`'s `run_with_teardown` fires `terminate_fn` when its wrapped subprocess **returns**. But on
Vast the real mechanism is a bash **EXIT trap** armed inside the onstart script (`gpu_backend.py:645-649`,
`_VAST_SELFDESTROY`: `poweroff || shutdown -h now || kill -9 -1 || kill -9 1`) — the Python wrapper is not in
that path at all. Both instances stayed `actual_status: running` across every read, because the onstart
content kept re-firing rather than the container exiting. **The docstring's belt-and-braces assumes killing
PID 1 ends billing; on this failure path the container was never observed to exit.** The 240-minute
collect-reap backstop would have caught it eventually, which is ~4 h of waste per incident — far too slow for
a crash-loop.

## The larger issue this exposed, which the incident did not cause

`gpu_backend._vast_onstart` forwards these AWS credentials **in plaintext to every rented Vast
community host, by design**. Its docstring promised only that `VAST_API_KEY` is withheld.

So **every Vast host operator this repo has ever rented from could already read that key.** The
leak widened the audience; it did not create the exposure.

**And the exposure is wider than the first version of this note recorded.** That note said the key
"has S3 write access to `sagemaker-us-east-2-646605541856`". Checked against the artifact rather
than assumed: the key is `nr4a3-ci-submitter`, and
[`deploy/aws-sagemaker.cfn.yaml`](../../deploy/aws-sagemaker.cfn.yaml) lines 31–47 grant it

- `s3:CreateBucket, PutObject, GetObject, ListBucket, GetBucketLocation` on **`Resource: "*"`** —
  every bucket in the account, not one prefix;
- `sagemaker:CreateProcessingJob` on `"*"`, plus `iam:PassRole` onto `nr4a3-sagemaker-exec`, which
  carries `AmazonSageMakerFullAccess`.

So a host operator holding it can read and overwrite anything in the account and **launch SageMaker
jobs at trimcrae's expense**. It has no `s3:DeleteObject`, which is the one thing that limits it.

**trimcrae's call (2026-07-27, asked directly): SCOPE THE CREDENTIALS.** Implemented — a dedicated
`vast-leg-s3` identity restricted to six S3 actions on the lane prefixes a leg actually touches,
with shared inputs read-only, generated from
[`s3_scoped_policy.py`](../modalities/s3_scoped_policy.py) and selected at one choke point
(`gpu_backend._object_store_env`). The code is transition-safe: with no scoped secret it forwards
the old key exactly as before, so the legs live when it landed were never at risk of losing their
upload path. Guards: `tests/test_s3_scoped_policy.py`. Remaining AWS steps are the runbook's.

## Audited and deliberately left alone

Checked every other path a credential could take out of CI, so "Vast-specific" is a finding and not
an assumption:

- **GCP** — clean, and clean on purpose. The GCE startup scripts export no `AWS_*` at all; every
  store operation is `gs://`, authenticated keylessly by the VM's own service account. Putting AWS
  creds in GCE metadata was explicitly rejected (cheap-gpu-plan.md).
- **SageMaker** — correct. The job assumes `nr4a3-sagemaker-exec` via `SAGEMAKER_ROLE_ARN`; no keys
  are injected into the container. The `AWS_*` in those workflows is the runner's own, and it stays
  on the runner.
- **RunPod / Salad / Slurm** — `NotImplementedError` stubs; nothing runs, nothing forwards.
- **Modal — the one other real egress, left as-is with reasons.** `nr4a3_rbfe_modal.py`,
  `modal_s3_smoke.py` and `modal_openmm_smoke.py` pass the same broad key into
  `modal.Secret.from_dict`. Different trust model (a named vendor under contract, not an anonymous
  host operator), and the lane is dormant since the monthly grant was exhausted — but the wiring is
  live and `modal-rbfe.yml` still fires its smoke on push. It is **not** routed through the scoped
  credential because its prefixes (`nr4a3-congeneric-dock/…`, `nr4a3-step1-pilot-rbfe`) are outside
  the Vast lanes, and widening the leg policy to cover a dormant lane would loosen the thing this
  change exists to tighten. Revisit if Modal is ever reactivated.

## The rule

**"I do not know which field I need" is a reason to print field NAMES, not field VALUES.**

A credential-exfiltration primitive was built in the course of being careful about evidence, which
is exactly the situation where it is easiest to miss: the intent was diligence, the instinct
(dump everything, inspect later) is the right one for a *local* artifact and wrong for anything
that lands in a log. Diagnostics that print remote records must allow-list.

Secondary lesson, on the direction of the request: the main session asked for "the container's exit
reason" without scoping how to obtain it. An instruction to go and find an unknown field invites
exactly this.
