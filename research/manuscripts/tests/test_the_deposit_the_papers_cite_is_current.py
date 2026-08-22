"""⛔ THE PAPERS SEND A READER TO A ZENODO RECORD. THIS ASKS WHETHER THAT RECORD STILL AGREES.

A Zenodo version is immutable once published and the repository is not, so the two drift apart by
construction. The only question that matters is whether anyone knows by how much.

⛔ NOBODY DID (round 15, 2026-08-22, found independently by three of five reviewers). The record was
published with 473 files; the repository had moved 16 files and added 4, and the changed set included
the extended report itself. Two of its changes were CORRECTIONS — the void-test definition, and a
claim that the dinucleotide-preserving scramble holds the 5′ guanine run — so a reader following the
citation read statements this repository had already retracted. Every gate was green because
`aso_archive_manifest.py --check-archive` compares the manifest to the WORKING TREE, so it goes green
exactly as the tree walks away from the deposit, and `archive_content_digest` lives inside the
manifest that computes it, so it can never disagree with itself.

★ THE THREE STATES THIS GUARD DISTINGUISHES, because collapsing them is what hid the defect:

  SETTLED   the papers cite the published version and the tree matches what was published.
  PENDING   a corrected version has been DRAFTED and the papers cite it. It does not resolve yet.
            This is not a defect — it is the reserve-then-rebuild ordering working: the manuscript
            has to print the identifier the archive will carry BEFORE the files are frozen, because
            a published version cannot be edited. It must be openly tracked, not silent.
  DRIFTED   the tree has moved away from what is published and nothing has been drafted or said.
            This is the defect, and it is the one that shipped.

⚠ WHAT THIS GUARD DOES NOT DO IS DEMAND THE DEPOSIT BE CURRENT. Drift between deposits is normal and
a gate that is red for weeks is a gate that gets switched off. It demands that drift be
ACKNOWLEDGED — by a drafted version, or by an open blocking item in the preprint checklist — and that
the acknowledgement be REMOVED once it is settled. Silence in either direction is the failure.
"""
from __future__ import annotations

import json
import os
import re
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")
MANIFEST = os.path.join(ASO, "fusion-junction-aso-archive-manifest.json")
STATE = os.path.join(ASO, "deposit-state.json")
CHECKLIST = os.path.join(ASO, "fusion-junction-aso-preprint-checklist.md")
REPO = os.path.abspath(os.path.join(ASO, "..", "..", ".."))

_OPEN_HEADING = "## 3 · Open, and blocking the journal submission"


def _json(path, what):
    if not os.path.exists(path):
        pytest.fail(f"{os.path.basename(path)} is missing, so {what} is unknown")
    return json.load(open(path, encoding="utf-8"))


def test_the_papers_cite_a_version_the_deposit_state_knows_about():
    """⛔ THE MANIFEST'S DOI IS EITHER WHAT IS PUBLISHED OR WHAT IS DRAFTED — NEVER A THIRD THING."""
    state, manifest = _json(STATE, "what was deposited"), _json(MANIFEST, "what is archivable")
    cited = manifest.get("deposition_doi")
    known = {state["published"]["doi"]}
    pending = state.get("pending")
    if pending:
        known.add(pending["doi"])
    assert cited in known, (
        f"the manifest and the papers cite {cited}, which deposit-state.json neither records as "
        f"published ({state['published']['doi']}) nor as drafted "
        f"({pending['doi'] if pending else 'nothing drafted'}). A DOI in the manuscript that no "
        "deposit state accounts for is an identifier nobody can check.")
    doi_key = cited.split("zenodo.")[-1]
    citing = [n for n in os.listdir(ASO)
              if n.endswith(".md") and doi_key in open(os.path.join(ASO, n), encoding="utf-8").read()]
    assert citing, (f"no document in aso/ cites {cited}, so this guard is watching a record nothing "
                    "points at — re-anchor it or retire it")


def _open_blocking_section_declares_the_drift(text):
    """Is the deposit item under the OPEN BLOCKING heading — not merely somewhere in the file?

    ⛔⛔ THIS WAS `_OPEN_HEADING in text and "PUBLISHED DEPOSIT IS BEHIND" in text.upper()`, WHICH
    TESTS ONLY THAT BOTH STRINGS OCCUR SOMEWHERE (round 16 seat 5, 2026-08-22). Moving the entire
    deposit item OUT of "## 3 · Open, and blocking the journal submission" — leaving that section
    reading "*Nothing.*" — and UP into "## 1 · Ready, and needs nothing further" left both
    substrings present and the guard green. The guard's own failure message demands "an open
    blocking item under '## 3 …'"; what it checked was that the heading exists.
    ★ A section is a SLICE, not a substring. The item has to be inside §3's slice, which is the
    only reading under which the message and the check say the same thing.
    """
    if _OPEN_HEADING not in text:
        return False
    after = text.split(_OPEN_HEADING, 1)[1]
    #: The section ends at the next heading of the same level.
    section = re.split(r"(?m)^## ", after, maxsplit=1)[0]
    return "PUBLISHED DEPOSIT IS BEHIND" in section.upper()


def test_an_unpublished_version_or_a_drifted_tree_is_openly_tracked():
    state, manifest = _json(STATE, "what was deposited"), _json(MANIFEST, "what is archivable")
    pending = state.get("pending")
    drifted = manifest.get("archive_content_digest") != state["published"]["manifest_digest"]

    assert os.path.exists(CHECKLIST), "the preprint checklist is missing; re-anchor this guard"
    text = open(CHECKLIST, encoding="utf-8").read()
    declared = _open_blocking_section_declares_the_drift(text)

    if pending:
        assert declared, (
            f"version {pending['doi']} has been drafted and the papers cite it, but it is NOT "
            "published — so every archive link in both manuscripts currently resolves to nothing. "
            f"That has to be an open blocking item under '{_OPEN_HEADING}' in "
            f"{os.path.basename(CHECKLIST)} until someone publishes it by hand.")
        assert pending["doi"] in text, (
            f"the checklist tracks the deposit as open but never names the drafted version "
            f"{pending['doi']}, so nobody reading it knows what to publish")
        return

    if drifted:
        assert declared, (
            "the published Zenodo record no longer matches what this repository would archive, "
            "nothing has been drafted, and the papers that cite it say nothing about that. Either "
            "draft a corrected version (dispatch deposit-zenodo.yml with new_version=true), or "
            f"record the drift as an open blocking item under '{_OPEN_HEADING}'. A reader "
            "following the DOI is reading superseded text until one of those happens.")
    else:
        assert not declared, (
            "the checklist still carries the deposit-is-behind blocking item, but nothing is "
            "drafted and the manifest matches the digest recorded as published. Close the item — a "
            "checklist that keeps a solved blocker open is one nobody reads.")


def test_the_recorded_upload_digest_is_corroborated_by_git_rather_than_declared():
    """⛔⛔ A POPULATED FIELD IS NOT A MEASURED ONE, AND THIS ONE COULD BE DECLARED BY HAND.

    Round 16 seat 5: `test_a_pending_draft_still_matches_the_tree_it_was_built_from` returns early
    when `pending.uploaded_manifest_digest` equals the manifest's digest now. **Copying today's
    digest into that field satisfies it** — one JSON edit — after which the checklist's "re-run the
    deposit first" line can be deleted with nothing firing, and the guard whose docstring reads
    "PUBLISHING A DRAFT THAT IS ALREADY BEHIND WOULD FREEZE THE SAME DEFECT AGAIN" has been
    satisfied by an assertion that it would not.

    ★ THE FIELD IS MADE OBSERVABLE BY THE ONE WITNESS THAT CANNOT BE BACK-DATED: git. The state also
    records `uploaded_at_git_revision`, so the digest it claims to have uploaded must be the digest
    the manifest ACTUALLY HELD at that commit. Copying today's value cannot satisfy that, because
    the manifest at an older revision holds an older digest — verified offline, no network, no
    Zenodo call.

    ⚠ This does not prove the bytes reached Zenodo; nothing available here can. It proves the
    recorded digest is a fact about this repository's history rather than a number someone typed.
    """
    state = _json(STATE, "what was deposited")
    pending = state.get("pending")
    if not pending:
        pytest.skip("nothing is drafted, so there is no upload digest to corroborate "
                    "— SKIP IS DELIBERATE: the pending block is absent by design between deposits")

    rev = pending.get("uploaded_at_git_revision")
    recorded = pending.get("uploaded_manifest_digest")
    assert rev and recorded, (
        f"the pending version {pending['doi']} records "
        f"{'no git revision' if not rev else 'no uploaded digest'}, so what it holds cannot be "
        "checked against anything. Both are written by the deposit workflow; if one is missing the "
        "draft's contents are unknown and it must not be published.")

    exists = subprocess.run(["git", "cat-file", "-e", f"{rev}^{{commit}}"],
                            cwd=REPO, capture_output=True)
    assert exists.returncode == 0, (
        f"deposit-state.json records the draft as built at {rev[:12]}, which is not a commit in "
        "this repository. A revision nobody can resolve cannot corroborate anything.")

    shown = subprocess.run(
        ["git", "show", f"{rev}:research/manuscripts/aso/fusion-junction-aso-archive-manifest.json"],
        cwd=REPO, capture_output=True, text=True)
    assert shown.returncode == 0, (
        f"the archive manifest cannot be read at {rev[:12]}, so the recorded upload digest has no "
        "witness. Do not publish the draft until the revision it was built from is resolvable.")
    at_revision = json.loads(shown.stdout).get("archive_content_digest")
    assert at_revision == recorded, (
        f"deposit-state.json says the draft was built at {rev[:12]} with digest {recorded[:12]}, "
        f"but the manifest AT that revision recorded {str(at_revision)[:12]}.\n\n"
        "Those disagree, so the digest was not taken from that build — the usual cause is a value "
        "copied in by hand to make a staleness check pass. Re-run the deposit and let the workflow "
        "write both fields, and do not publish the draft in the meantime.")


def test_a_pending_draft_still_matches_the_tree_it_was_built_from():
    """⛔ PUBLISHING A DRAFT THAT IS ALREADY BEHIND WOULD FREEZE THE SAME DEFECT AGAIN.

    The draft on Zenodo holds one specific build. Publishing is irreversible, so if the repository
    moves after the upload and nobody re-runs the deposit, the click freezes an archive that is
    already stale — which is exactly the defect this file exists to prevent, one step earlier in the
    process and with the same irreversibility.

    ⚠ THIS CANNOT SEE ZENODO, and does not claim to. It compares the digest recorded at upload time
    against the manifest's digest now. That answers the question that actually matters — "has the
    tree moved since the draft was built?" — without a network call, which is what makes it a gate
    rather than a note.
    """
    state, manifest = _json(STATE, "what was deposited"), _json(MANIFEST, "what is archivable")
    pending = state.get("pending")
    if not pending:
        return
    recorded = pending.get("uploaded_manifest_digest")
    assert recorded, (
        f"deposit-state.json records a pending version ({pending['doi']}) without the digest of "
        "what was uploaded into it, so nothing can tell whether the draft still matches this tree")
    if recorded == manifest.get("archive_content_digest"):
        return

    # ⛔⛔ A STALE DRAFT BETWEEN COMMITS IS NORMAL, AND THE FIRST VERSION OF THIS ASSERTION MADE IT
    # A HARD FAILURE — which turned every commit that touches the archive into a red gate with a
    # CIRCULAR dependency: refreshing the draft uploads from the pushed branch, and pushing needs
    # this gate green. It went red on its own first full run, three commits after being written.
    # ⚠ A GATE THAT IS RED FOR WEEKS IS A GATE THAT GETS SWITCHED OFF, and this repository has the
    # scars. The question worth asking is not "is the draft current?" — between commits it is not,
    # and should not have to be. It is "will the person about to publish be TOLD to refresh it?",
    # because that is the moment the staleness would be frozen.
    text = open(CHECKLIST, encoding="utf-8").read()
    assert re.search(r"re-?run the deposit|new_version=false|refresh the draft", text, re.I), (
        f"the draft {pending['doi']} was built at archive digest {recorded[:16]}… and this tree is "
        f"at {str(manifest.get('archive_content_digest'))[:16]}…, which is expected between "
        "commits — but nothing in the preprint checklist tells whoever publishes it to refresh the "
        "draft first.\n\nPublishing a stale draft freezes an archive that is already behind, which "
        "is the defect this whole file exists to prevent, one step later and irreversibly. Add the "
        "instruction to the blocking item: dispatch deposit-zenodo.yml with new_version=false "
        "(it UPDATES the draft rather than making a second one), then update "
        "`uploaded_manifest_digest` here.")
