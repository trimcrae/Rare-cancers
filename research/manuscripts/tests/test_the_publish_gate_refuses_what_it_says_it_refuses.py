#!/usr/bin/env python3
"""⛔⛔ THE GATE IN FRONT OF AN IRREVERSIBLE ACT, DRIVEN RATHER THAN READ.

`zenodo_deposit.refuse_unless_publishable` is the only thing standing between this loop and a
permanent public record under trimcrae's ORCID. Until 2026-08-30 **nothing imported it** — measured:
`grep -rln zenodo_deposit --include=test_*.py` returned no files, while four separate test modules
named the deposit in their own filenames and passed. Every property the gate claims was asserted in
its docstring and by nothing else, which is the shape this repository has already paid for twice
(`subagent_width` governed nothing; `fleet_armed.CENSUS_LANE` protected nothing).

★ THE PROPERTY THAT MATTERS IS FAIL-CLOSED, SO EVERY TEST HERE IS A REFUSAL. A gate that permits
when it should permit is cheap to notice — the publish happens. A gate that permits when it should
REFUSE is noticed only after the record is public and can no longer be edited.

⛔ NOTHING HERE TOUCHES THE NETWORK OR THE REAL AUTHORITY FILE. The gate is pure by design — it runs
BEFORE any API call, which is the correction made on 2026-08-30 when it used to run after the upload
— so each case below drives it against a fixture tree under `tmp_path` and monkeypatches the
module's `REPO`. A test that mutated the live authority record to see what happens would be the
incident it exists to prevent.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SCRIPT = os.path.join(REPO, "scripts", "zenodo_deposit.py")

DIGEST = "a" * 64
OTHER = "b" * 64


def _module():
    """A FRESH import per test, so a monkeypatched REPO can never leak into the next case."""
    spec = importlib.util.spec_from_file_location("_zd_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_zd_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def _tree(tmp_path, *, standing=True, gated=False, pending=True,
          uploaded=DIGEST, manifest_rel=None):
    """A minimal repository the gate can read: an authority record and a deposit state."""
    autonomy = tmp_path / "research" / "autonomy"
    autonomy.mkdir(parents=True)
    (autonomy / "publication-authority.json").write_text(json.dumps({
        "zenodo_archive_publication": {
            "standing_grant": standing,
            "approval_is_required_per_publication": gated,
        }}), encoding="utf-8")

    mod = _module()
    manifest_rel = manifest_rel or mod.PAPERS["aso"]["manifest"]
    aso = tmp_path / os.path.dirname(manifest_rel)
    aso.mkdir(parents=True, exist_ok=True)
    state = {"published": {"doi": "10.5281/zenodo.1"}}
    if pending:
        state["pending"] = {"doi": "10.5281/zenodo.2", "uploaded_manifest_digest": uploaded}
    (aso / "deposit-state.json").write_text(json.dumps(state), encoding="utf-8")
    mod.REPO = str(tmp_path)
    return mod


def _manifest(digest=DIGEST):
    return {"archive_content_digest": digest}


# ══════════════════════════════════════════════════════════════════════════════════════════
# The refusals. Each one is a way the loop could freeze something wrong into a public record.
# ══════════════════════════════════════════════════════════════════════════════════════════

def test_no_standing_grant_refuses(tmp_path):
    """⛔ THE AUTHORITY IS trimcrae's TO GIVE. A missing or false grant is not a configuration
    problem to route around — the gate's own message says "do NOT add the block to make this run"."""
    mod = _tree(tmp_path, standing=False)
    with pytest.raises(SystemExit, match="does not grant Zenodo publication"):
        mod.refuse_unless_publishable("aso", _manifest(), "trimcrae, standing grant")


def test_an_empty_approval_string_refuses_even_though_the_human_gate_is_retired(tmp_path):
    """⛔ THE RECORD SURVIVED THE GATE, AND THIS IS THE HALF THAT COULD ROT QUIETLY.

    trimcrae retired the per-publication approval on 2026-08-30 ("I don't want my approval to gate
    Zenodo. Just do it."). Retiring the GATE is not retiring the RECORD: the `exercised` list is only
    auditable if every row names who authorised it, and a grant whose exercise nobody can account for
    cannot be revoked knowingly. So an empty `--approved-by` still refuses.
    """
    mod = _tree(tmp_path, gated=False)
    with pytest.raises(SystemExit, match="must name the authority it acts under"):
        mod.refuse_unless_publishable("aso", _manifest(), "")


def test_the_retired_gate_can_be_restored_by_one_boolean(tmp_path):
    """★ THE FLAG IS STILL READ, so putting the human back in the loop is a data edit rather than a
    code change. Asserted because a flag nothing reads is how a retired control becomes an
    unrestorable one — and the message must say WHICH regime refused, or the operator cannot tell a
    missing record from a missing approval."""
    mod = _tree(tmp_path, gated=True)
    with pytest.raises(SystemExit, match="requires an approval for THIS deposition"):
        mod.refuse_unless_publishable("aso", _manifest(), "")


def test_a_draft_behind_the_tree_refuses(tmp_path):
    """⛔⛔ THE CONDITION THE WHOLE 2026-08-29/30 CORRECTION EXISTS FOR, AND IT HAS GONE STALE TWICE.

    Publishing a draft that no longer matches the manifest freezes an archive already behind the
    paper that cites it — which is exactly how record 22166420 came to hold an earlier copy of its
    own manuscript. This is the one check a human clicking Publish on zenodo.org cannot perform.
    """
    mod = _tree(tmp_path, uploaded=OTHER)
    with pytest.raises(SystemExit, match="THE DRAFT IS BEHIND THIS TREE"):
        mod.refuse_unless_publishable("aso", _manifest(DIGEST), "trimcrae, standing grant")


def test_a_missing_uploaded_digest_refuses(tmp_path):
    """⚠ AN ABSENT READING IS NOT A READING OF ABSENCE. A null digest means nothing measured what
    the draft holds, so the honest answer is refusal rather than an optimistic pass."""
    mod = _tree(tmp_path, uploaded=None)
    with pytest.raises(SystemExit, match="records no uploaded digest"):
        mod.refuse_unless_publishable("aso", _manifest(), "trimcrae, standing grant")


def test_a_missing_deposit_state_refuses(tmp_path):
    """The file is derived from the paper's manifest path, so a paper added to PAPERS cannot arrive
    without one and be published unchecked."""
    mod = _tree(tmp_path)
    os.remove(os.path.join(str(tmp_path),
                           os.path.dirname(mod.PAPERS["aso"]["manifest"]), "deposit-state.json"))
    with pytest.raises(SystemExit, match="nothing records what the draft holds"):
        mod.refuse_unless_publishable("aso", _manifest(), "trimcrae, standing grant")


# ══════════════════════════════════════════════════════════════════════════════════════════
# The other direction — without it, a gate that refuses everything would pass every test above
# ══════════════════════════════════════════════════════════════════════════════════════════

def test_a_current_draft_under_a_standing_grant_is_permitted(tmp_path):
    """⛔ THE HALF THAT STOPS THIS SUITE BEING VACUOUS. Six refusals prove nothing on their own: a
    gate hard-wired to `raise` would satisfy all of them. This asserts the gate still opens, and
    returns the grant and the pending block the caller then records."""
    mod = _tree(tmp_path)
    grant, pending = mod.refuse_unless_publishable("aso", _manifest(), "trimcrae, standing grant")
    assert grant.get("standing_grant") is True
    assert pending["uploaded_manifest_digest"] == DIGEST


def test_the_live_authority_record_still_grants_and_still_demands_a_named_authority():
    """★ THE FIXTURES ABOVE PROVE THE LOGIC; THIS PROVES THE LOGIC IS WIRED TO THE REAL FILE.

    `fleet_armed.CENSUS_LANE` is this repository's own record of a property asserted about a value
    every caller then failed to pass — every test passed and the one artifact it protected was the
    one being dropped. So the shape of the live record is read here, without publishing anything.
    """
    live = json.load(io.open(os.path.join(
        REPO, "research", "autonomy", "publication-authority.json"), encoding="utf-8"))
    grant = live.get("zenodo_archive_publication")
    assert grant, "the authority record no longer names Zenodo publication; the gate would refuse"
    assert grant.get("standing_grant") is True, (
        "the Zenodo standing grant is not true. If trimcrae revoked it that is correct and this "
        "line is what should be updated — but never by adding the grant back to make a publish run")
    assert "approval_is_required_per_publication" in grant, (
        "the per-publication flag was DELETED rather than set false. It is still read by "
        "refuse_unless_publishable, and deleting it removes the one-boolean route back to a human "
        "gate — retiring a control is trimcrae's call; making it unrestorable is nobody's")
