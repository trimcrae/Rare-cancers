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
