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

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")
MANIFEST = os.path.join(ASO, "fusion-junction-aso-archive-manifest.json")
STATE = os.path.join(ASO, "deposit-state.json")
CHECKLIST = os.path.join(ASO, "fusion-junction-aso-preprint-checklist.md")

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


def test_an_unpublished_version_or_a_drifted_tree_is_openly_tracked():
    state, manifest = _json(STATE, "what was deposited"), _json(MANIFEST, "what is archivable")
    pending = state.get("pending")
    drifted = manifest.get("archive_content_digest") != state["published"]["manifest_digest"]

    assert os.path.exists(CHECKLIST), "the preprint checklist is missing; re-anchor this guard"
    text = open(CHECKLIST, encoding="utf-8").read()
    declared = _OPEN_HEADING in text and "PUBLISHED DEPOSIT IS BEHIND" in text.upper()

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
