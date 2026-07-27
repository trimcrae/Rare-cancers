#!/usr/bin/env python3
"""The credential handed to a rented community host must be the SCOPED one, and it must fit the job.

Two failure modes, opposite directions, both real:

  * TOO WIDE — what actually happened. `_vast_onstart` writes the object-store credential in cleartext into
    every rental's onstart script, and until 2026-07-27 that credential was `nr4a3-ci-submitter`: S3 on
    `Resource: "*"` plus `sagemaker:CreateProcessingJob` plus `iam:PassRole`
    (`deploy/aws-sagemaker.cfn.yaml:31-47`). Every host operator this repo ever rented from could read it.
  * TOO NARROW — the way a fix like this breaks a program. A scoped key that misses a lane's prefix gives a
    leg that runs for hours and 403s on upload. Nothing in the pipeline reports that: the sync loops all end
    in `|| true`. Silent, expensive, and it looks exactly like a slow leg.

So these tests pin the policy from BOTH sides: the actions/prefixes are no wider than what a leg does, and
no narrower than what the launchers actually reach for — the prefix registry is checked against the
launcher sources themselves, so a new lane cannot ship without registering its prefix.
"""
import json
import os
import re

import pytest

from gpu_backend import (JobSpec, VastBackend, _object_store_env, _vast_onstart,
                         object_store_cred_mode)
import s3_scoped_policy as pol

MODALITIES = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUCKET = pol.DEFAULT_BUCKET


# --------------------------------------------------------------------------------------------------------
# 1. The credential choke point: scoped wins, and when it does the broad key does NOT ride along.
# --------------------------------------------------------------------------------------------------------

CI_KEY = {"AWS_ACCESS_KEY_ID": "AKIACIBROAD", "AWS_SECRET_ACCESS_KEY": "ci-secret",
          "AWS_DEFAULT_REGION": "us-east-2"}
SCOPED = {"VAST_S3_ACCESS_KEY_ID": "AKIALEGSCOPED", "VAST_S3_SECRET_ACCESS_KEY": "leg-secret"}


def test_falls_back_to_the_broad_key_so_lanes_in_flight_keep_running():
    # The transition constraint: three legs were live when this landed. No scoped secret -> byte-identical
    # behaviour to before, so nothing has to be re-launched.
    assert object_store_cred_mode(CI_KEY) == "inherited"
    assert _object_store_env(CI_KEY) == CI_KEY


def test_scoped_credential_replaces_the_broad_one_rather_than_joining_it():
    env = {**CI_KEY, **SCOPED}
    assert object_store_cred_mode(env) == "scoped"
    fwd = _object_store_env(env)
    assert fwd["AWS_ACCESS_KEY_ID"] == "AKIALEGSCOPED"          # the host gets the scoped identity
    assert fwd["AWS_SECRET_ACCESS_KEY"] == "leg-secret"
    assert "AKIACIBROAD" not in json.dumps(fwd)                 # ...and NOT the CI one, anywhere
    assert "ci-secret" not in json.dumps(fwd)
    assert fwd["AWS_DEFAULT_REGION"] == "us-east-2"             # region is config, not a secret: passes through


def test_a_ci_session_token_never_rides_along_with_a_scoped_key():
    # Mixing a key id from one identity with a session token from another yields a credential that fails in
    # a confusing way. In scoped mode the token comes from VAST_S3_SESSION_TOKEN or not at all.
    env = {**CI_KEY, **SCOPED, "AWS_SESSION_TOKEN": "ci-session"}
    assert "AWS_SESSION_TOKEN" not in _object_store_env(env)
    env2 = {**env, "VAST_S3_SESSION_TOKEN": "leg-session"}
    assert _object_store_env(env2)["AWS_SESSION_TOKEN"] == "leg-session"


def test_shape_agnostic_long_lived_key_and_sts_triple_both_work():
    # trimcrae may put either shape in the secret; the code must not care which.
    triple = {**SCOPED, "VAST_S3_SESSION_TOKEN": "FQoG-temp"}
    fwd = _object_store_env(triple)
    assert set(fwd) == {"AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"}


def test_half_configured_scoped_secret_does_not_silently_send_a_useless_credential():
    # Only the id set (a half-finished secret rotation) must not count as "scoped" — otherwise the host
    # gets an id with no secret and every upload fails.
    assert object_store_cred_mode({**CI_KEY, "VAST_S3_ACCESS_KEY_ID": "AKIA"}) == "inherited"


# --------------------------------------------------------------------------------------------------------
# 2. The onstart script: nothing secret beyond that one credential.
# --------------------------------------------------------------------------------------------------------

# Every non-credential name the onstart script is allowed to export. Anything else that looks secret-shaped
# is a new thing crossing the boundary to an untrusted host and has to be argued for, not merged quietly.
_ALLOWED_EXPORTS = {"CHECKPOINT_URI", "RESUME", "SELF_LABEL",
                    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
                    "AWS_DEFAULT_REGION", "OBJECT_STORE_ENDPOINT", "OBJECT_STORE_REGION"}
_SECRET_SHAPED = ("KEY", "SECRET", "TOKEN", "PASSWORD", "PASSWD", "CREDENTIAL", "AUTH", "APIKEY", "PRIVATE")


def _exports(script):
    return re.findall(r"^export ([A-Za-z_][A-Za-z0-9_]*)=", script, re.M)


def test_onstart_exports_no_secret_shaped_name_outside_the_object_store_credential():
    spec = JobSpec(name="leg1", command=["bash", "-lc", "run"],
                   checkpoint_uri=f"s3://{BUCKET}/ternary-vast/legs/leg1",
                   env={"RESULT_S3": f"s3://{BUCKET}/ternary-vast/legs/leg1", "TVAST_SEED": "1"})
    script = _vast_onstart(spec, VastBackend().self_terminate_cmd(),
                           extra_env=_object_store_env({**CI_KEY, **SCOPED}))
    for name in _exports(script):
        if any(s in name.upper() for s in _SECRET_SHAPED):
            assert name in _ALLOWED_EXPORTS, (
                f"{name} is secret-shaped and crosses to an untrusted host. If it is genuinely needed, "
                f"hand it over as a presigned URL instead, or add it here with a stated reason.")


def test_onstart_still_withholds_the_vast_account_key():
    # The one thing the old docstring promised. Regression guard, kept.
    spec = JobSpec(name="leg1", command=["true"], checkpoint_uri=f"s3://{BUCKET}/vast/leg1/ckpt")
    script = _vast_onstart(spec, VastBackend().self_terminate_cmd(),
                           extra_env=_object_store_env(SCOPED))
    assert "VAST_API_KEY" not in script
    assert "trap ct_selfstop EXIT" in script                 # and the anti-idle guard survives the edit


def test_onstart_carries_the_scoped_key_and_not_the_broad_one():
    spec = JobSpec(name="leg1", command=["true"], checkpoint_uri=f"s3://{BUCKET}/vast/leg1/ckpt")
    script = _vast_onstart(spec, [], extra_env=_object_store_env({**CI_KEY, **SCOPED}))
    assert "AKIALEGSCOPED" in script
    assert "AKIACIBROAD" not in script and "ci-secret" not in script


def test_docstring_no_longer_promises_only_that_the_vast_key_is_withheld():
    # The docstring that read as reassurance while an AWS key went out in the clear. It must now name the
    # credential it DOES forward, in the same breath.
    doc = _vast_onstart.__doc__ or ""
    assert "CLEARTEXT" in doc.upper() or "PLAINTEXT" in doc.upper()
    assert "_object_store_env" in doc
    assert "VAST_API_KEY" in doc                                # still says what is withheld, too


# --------------------------------------------------------------------------------------------------------
# 3. The policy is no WIDER than what a leg does.
# --------------------------------------------------------------------------------------------------------

def test_policy_grants_no_action_outside_the_declared_leg_set():
    doc = pol.leg_policy_document(BUCKET)
    allowed = {a for s in doc["Statement"] if s["Effect"] == "Allow" for a in s["Action"]}
    assert allowed <= set(pol.LEG_OBJECT_ACTIONS) | set(pol.LEG_BUCKET_ACTIONS)
    assert not any("*" == a or a.endswith(":*") for a in allowed), "no wildcard action in an Allow"


def test_policy_never_grants_delete_spend_or_acl():
    doc = pol.leg_policy_document(BUCKET)
    allowed = {a for s in doc["Statement"] if s["Effect"] == "Allow" for a in s["Action"]}
    for bad in ("s3:DeleteObject", "s3:PutObjectAcl", "s3:PutBucketPolicy", "s3:CreateBucket"):
        assert bad not in allowed
    denied = {a for s in doc["Statement"] if s["Effect"] == "Deny" for a in s["Action"]}
    # The two that turn a bucket-write leak into an account-spend leak, and the one that would let a host
    # switch versioning off before overwriting.
    for must_deny in ("sagemaker:*", "iam:*", "s3:PutBucketVersioning", "s3:DeleteObjectVersion"):
        assert must_deny in denied


def test_policy_is_confined_to_one_bucket():
    doc = pol.leg_policy_document(BUCKET)
    for s in doc["Statement"]:
        if s["Effect"] != "Allow":
            continue
        for arn in ([s["Resource"]] if isinstance(s["Resource"], str) else s["Resource"]):
            assert arn.startswith(f"arn:aws:s3:::{BUCKET}"), arn


def test_listbucket_cannot_enumerate_the_whole_evidence_bucket():
    # ListBucket is bucket-level, so only an s3:prefix condition can confine it. Without this a leaked key
    # could still inventory every leg in the program.
    doc = pol.leg_policy_document(BUCKET)
    lst = [s for s in doc["Statement"] if "s3:ListBucket" in s.get("Action", [])]
    assert len(lst) == 1
    cond = lst[0]["Condition"]["StringLike"]["s3:prefix"]
    assert cond and "*" not in cond, "a bare '*' prefix condition confines nothing"


def test_shared_inputs_are_read_only_so_one_host_cannot_poison_every_other_leg():
    doc = pol.leg_policy_document(BUCKET)
    ro = [s for s in doc["Statement"] if s.get("Sid") == "LegSharedInputsReadOnly"][0]
    assert set(ro["Action"]) == {"s3:GetObject"}
    # the staged poses every fan-out unit reads, and the co-folded CIFs the NR-V04 panel reads
    assert any("nr4a3-step1-fanout/stage" in a for a in ro["Resource"])
    assert any("nrv04-covalent-cofold" in a for a in ro["Resource"])
    rw = [s for s in doc["Statement"] if s.get("Sid") == "LegResultIO"][0]
    assert not any("/stage/" in a for a in rw["Resource"])


# --------------------------------------------------------------------------------------------------------
# 4. The policy is no NARROWER than what the launchers actually reach for.
#    This is the half that protects the running program, and it reads the launchers rather than a list.
# --------------------------------------------------------------------------------------------------------

# Every module that builds a Vast jobspec, and the constants in it that name an S3 prefix.
_LAUNCHERS = ["protfep_vast_launch.py", "congeneric_fanout_vast.py", "nrv04_vast_launch.py",
              "ternary_vast_launch.py", "nr4a3_bioemu_vast_launch.py", "nr4a_paralogue_md_vast_launch.py",
              "nrv04_retro_panel.py"]
# A module-level `*_PREFIX = os.environ.get("ENV_NAME", "the-default")` / `... or "the-default"`. Both
# spellings are in use, so the scraper takes the LAST literal on the line — the env-var name comes first and
# the default second, and a line with only one literal has no default to register.
_PREFIX_LINE = re.compile(r"^(_?[A-Z][A-Z0-9_]*PREFIX[A-Z0-9_]*)\s*=\s*(.*os\.environ\.get.*)$", re.M)


def _declared_prefixes():
    """Scrape the literal default S3 prefixes out of the launcher sources. Deliberately source-scraping and
    not importing: importing pulls scientific dependencies CI may not have, and the point is to catch a
    prefix someone ADDS, which is a textual event."""
    found = {}
    for mod in _LAUNCHERS:
        p = os.path.join(MODALITIES, mod)
        if not os.path.exists(p):
            continue
        for m in _PREFIX_LINE.finditer(open(p).read()):
            lits = re.findall(r"[\"']([^\"']*)[\"']", m.group(2))
            if len(lits) < 2 or not lits[-1]:
                continue                                        # env-var name only: no default to register
            v = lits[-1].strip("/")
            if "/" in v or "-" in v:                            # a real key prefix, not a bare flag value
                found.setdefault(v, f"{mod}:{m.group(1)}")
    return found


def test_the_prefix_scraper_actually_sees_the_launchers():
    # A scan-based guard that silently matches nothing is worse than no guard: it goes green forever.
    found = _declared_prefixes()
    assert len(found) >= 9, found
    for expect in ("protfep-benchmark", "ternary-vast", "nrv04-covalent-results",
                   "nr4a3-step1-fanout/stage"):
        assert expect in found, f"{expect} not scraped — the regex has drifted from the launchers"


def test_every_prefix_a_launcher_declares_is_registered_in_the_policy():
    missing = {v: mod for v, mod in _declared_prefixes().items()
               if not (pol.covers(f"s3://{BUCKET}/{v}/x") or v in pol.LANE_PREFIXES
                       or v in pol.PRESIGNED_ONLY_PREFIXES)}
    assert not missing, (
        "these S3 prefixes are used by a launcher but absent from s3_scoped_policy.LANE_PREFIXES, so a leg "
        f"on the scoped credential would 403 on every upload: {missing}")


@pytest.mark.parametrize("uri", [
    f"s3://{BUCKET}/protfep-benchmark/leg_x",
    f"s3://{BUCKET}/ternary-vast/legs/uid",
    f"s3://{BUCKET}/ternary-vast/stagecache/x.tar",             # a lane sibling, not the per-unit prefix
    f"s3://{BUCKET}/nr4a3-step1-fanout/results/u1/ckpt/complex",
    f"s3://{BUCKET}/nrv04-covalent-results/u1",
    f"s3://{BUCKET}/nr4a-paralogue-ensemble/nr4a-pdyn-nr4a1/ckpt",
    f"s3://{BUCKET}/nr4a3-bioemu-crosscheck/nr4a3-bioemu-smoke",
    f"s3://{BUCKET}/vast/anyjob/ckpt",
    f"s3://{BUCKET}/rung5aks-cofold-v1/out",                    # operator-named co-fold output (wildcard)
])
def test_live_lane_prefixes_are_writable(uri):
    assert pol.covers(uri), f"{uri} would 403 — a running lane cannot upload"


def test_a_prefix_outside_the_lanes_is_not_writable():
    assert not pol.covers(f"s3://{BUCKET}/some-other-programs-data/x")
    assert not pol.covers(f"s3://{BUCKET}/")
    assert not pol.covers(f"s3://{BUCKET}/mdenv/nrv04md.tar.gz"), \
        "mdenv is fetched by presigned URL; granting it would undo the better mechanism"


# --------------------------------------------------------------------------------------------------------
# 5. Stage 2 (per-rental STS): opt-in, fails open, and never derives from the broad key.
# --------------------------------------------------------------------------------------------------------

def test_sts_is_off_unless_explicitly_enabled():
    assert pol.sts_leg_credentials(BUCKET, "ternary-vast", "leg1", source_env={**SCOPED}) == {}


def test_sts_never_derives_a_session_from_the_broad_ci_key():
    # If it did, the session's ceiling would be the CI key's ceiling and the scoping would be theatre.
    env = {**CI_KEY, "VAST_S3_SCOPED_STS": "1"}
    assert pol.sts_leg_credentials(BUCKET, "ternary-vast", "leg1", source_env=env) == {}


def test_sts_ttl_ceiling_exceeds_a_long_leg():
    # Legs run 8-20 h and Vast re-runs onstart on container restart, so the token has to outlive the
    # instance, not the compute. AssumeRole's 12 h ceiling is why this uses GetFederationToken.
    assert pol.STS_MAX_TTL_S == 36 * 3600
    assert pol.STS_DEFAULT_TTL_S >= 24 * 3600


def test_session_policy_is_a_subset_of_the_standing_policy():
    full = pol.leg_policy_document(BUCKET)
    one = pol.leg_session_policy(BUCKET, "ternary-vast")
    full_rw = set([s for s in full["Statement"] if s.get("Sid") == "LegResultIO"][0]["Resource"])
    one_rw = set([s for s in one["Statement"] if s.get("Sid") == "LegResultIO"][0]["Resource"])
    assert one_rw < full_rw, "a session policy must only ever subtract"
    assert any("ternary-vast" in a for a in one_rw)


@pytest.mark.parametrize("raw,ok", [
    ("nr4a3__complex_r0", True), ("a" * 60, True), ("", True), ("leg/with slash", True),
])
def test_federation_name_is_always_valid_for_sts(raw, ok):
    n = pol.federation_name(raw)
    assert 1 <= len(n) <= 32
    assert re.fullmatch(r"[\w+=,.@-]+", n), n


# --------------------------------------------------------------------------------------------------------
# 6. The rendered policy is what the runbook tells trimcrae to paste.
# --------------------------------------------------------------------------------------------------------

def test_rendered_policy_is_valid_json_and_deterministic():
    a, b = pol.render(BUCKET), pol.render(BUCKET)
    assert a == b, "the runbook regenerates this; a non-deterministic render makes every diff noise"
    assert json.loads(a)["Version"] == "2012-10-17"


RUNBOOK = os.path.join(MODALITIES, "..", "compute", "scoped-s3-credential-runbook.md")


def test_runbook_points_at_the_generator_rather_than_carrying_a_stale_copy():
    assert os.path.exists(RUNBOOK), "the runbook is the deliverable trimcrae executes; it must exist"
    text = open(RUNBOOK).read()
    assert "s3_scoped_policy.py" in text
    # One fact, one place: the policy in the runbook must be generated, and say so.
    assert "python3 research/modalities/s3_scoped_policy.py" in text


def test_runbook_policy_block_is_byte_identical_to_the_generator():
    """trimcrae pastes the block in the runbook into the IAM console, so it has to be a real copy — but a
    real copy is exactly the thing that drifts. This is what makes the duplication safe: the doc keeps the
    pasteable JSON and CI keeps it honest."""
    text = open(RUNBOOK).read()
    m = re.search(r"BEGIN GENERATED POLICY.*?-->\s*```json\n(.*?)\n```", text, re.S)
    assert m, "the runbook's generated-policy block is missing or its markers moved"
    assert json.loads(m.group(1)) == pol.leg_policy_document(BUCKET), (
        "the runbook's policy has drifted from s3_scoped_policy.py — regenerate it with "
        "`python3 research/modalities/s3_scoped_policy.py` and paste the output back in")


def test_policy_fits_a_managed_policy_and_needs_one():
    # AWS: 2048 chars for a user's inline policies, 6144 for a customer-managed policy. If this ever grew
    # past 6144 the runbook's step 1 would fail in the console with a size error and no explanation.
    size = len(json.dumps(pol.leg_policy_document(BUCKET), separators=(",", ":")))
    assert size < 6144, f"policy is {size} chars — too big even for a managed policy; split it"
    assert size > 2048, "if this now fits inline, update the runbook's 'must be customer-managed' note"


def test_the_sts_grant_is_not_in_the_stage_one_policy():
    # Stage 1 must not be able to mint anything; turning stage 2 on has to be a deliberate act.
    doc = json.dumps(pol.leg_policy_document(BUCKET))
    assert "GetFederationToken" not in doc
    assert "GetFederationToken" in json.dumps(pol.sts_grant_statement())
