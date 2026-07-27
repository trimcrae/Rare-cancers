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

**Rotate the key.** Log deletion closes the window; it is not a rotation, and the key must be
treated as compromised. It lives in repo secrets `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` and
has S3 write access to `sagemaker-us-east-2-646605541856` — which holds **every leg's checkpoints
and results** for this program. Write access to that bucket is write access to the evidence base.

## The larger issue this exposed, which the incident did not cause

`gpu_backend._vast_onstart` forwards these AWS credentials **in plaintext to every rented Vast
community host, by design**. Its docstring promises only that `VAST_API_KEY` is withheld.

So **every Vast host operator this repo has ever rented from could already read that key.** The
leak widened the audience; it did not create the exposure. That is a standing design decision and
deserves its own call — scoped or temporary credentials per rental, or accepting it knowingly —
independently of this incident.

## The rule

**"I do not know which field I need" is a reason to print field NAMES, not field VALUES.**

A credential-exfiltration primitive was built in the course of being careful about evidence, which
is exactly the situation where it is easiest to miss: the intent was diligence, the instinct
(dump everything, inspect later) is the right one for a *local* artifact and wrong for anything
that lands in a log. Diagnostics that print remote records must allow-list.

Secondary lesson, on the direction of the request: the main session asked for "the container's exit
reason" without scoping how to obtain it. An instruction to go and find an unknown field invites
exactly this.
