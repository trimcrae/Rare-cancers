"""⛔ THE PAPERS SEND A READER TO A FROZEN ARCHIVE. THIS ASKS WHETHER THAT ARCHIVE STILL AGREES.

The condensed submission's Data and code availability names the extended report "inside that
deposit" and calls the archived copy "the citable one"; the extended report cites the same DOI. A
Zenodo record is immutable once published, and the repository is not — so the two drift apart by
construction, and the only question that matters is whether anyone knows by how much.

⛔ NOBODY DID (round 15, 2026-08-22, found independently by three of five reviewers). The record was
published with 473 files; the repository had moved 16 files and added 4, and the changed set included
the extended report itself. Two of its changes were CORRECTIONS — the void-test definition, and a
claim that the dinucleotide-preserving scramble holds the 5′ guanine run — so a reader following the
citation read statements this repository had already retracted.

⛔ WHY EVERY GATE WAS GREEN, WHICH IS THE REUSABLE PART. `aso_archive_manifest.py --check-archive`
compares the manifest to the WORKING TREE, so it goes green exactly as the tree walks away from the
deposit; and `archive_content_digest` lives inside the manifest that computes it, so it can never
disagree with itself. Nothing anywhere recorded what had actually been uploaded. `deposit-state.json`
does now, and it is the only file here that a human edits — after a publish, never to quiet a gate.

★ THIS GATE DOES NOT DEMAND THE DEPOSIT BE CURRENT, BECAUSE DRIFT BETWEEN DEPOSITS IS NORMAL and a
gate that is red for weeks is a gate that gets switched off. It demands that drift be ACKNOWLEDGED:
if the archive has moved out from under the papers that cite it, the preprint checklist must carry an
open blocking item saying so, and when a new version is published that item must go. Silence in
either direction is the failure.
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

#: The heading under which an open, submission-blocking item must appear.
_OPEN_HEADING = "## 3 · Open, and blocking the journal submission"


def _json(path, what):
    if not os.path.exists(path):
        pytest.fail(f"{os.path.basename(path)} is missing, so {what} is unknown")
    return json.load(open(path, encoding="utf-8"))


def _files(manifest):
    fs = manifest["files"]
    return dict(fs) if isinstance(fs, dict) else {f["path"]: f.get("sha256") for f in fs}


def test_the_recorded_deposit_matches_the_record_the_papers_cite():
    """The DOI in deposit-state.json must be the DOI the manifest and the papers name."""
    state, manifest = _json(STATE, "what was deposited"), _json(MANIFEST, "what is archivable")
    assert state["deposition_doi"] == manifest.get("deposition_doi"), (
        f"deposit-state.json records {state['deposition_doi']} and the manifest targets "
        f"{manifest.get('deposition_doi')} — they must be the same record")
    doi_key = state["deposition_doi"].split("zenodo.")[-1]
    cited = [n for n in os.listdir(ASO)
             if n.endswith(".md") and doi_key in open(os.path.join(ASO, n), encoding="utf-8").read()]
    assert cited, (f"no document in aso/ cites {state['deposition_doi']}, so this guard is watching "
                   "a record nothing points at — re-anchor it or retire it")


def test_drift_from_the_published_deposit_is_acknowledged_where_it_blocks():
    state, manifest = _json(STATE, "what was deposited"), _json(MANIFEST, "what is archivable")
    now = _files(manifest)
    drifted = manifest.get("archive_content_digest") != state["published_manifest_digest"]

    assert os.path.exists(CHECKLIST), "the preprint checklist is missing; re-anchor this guard"
    text = open(CHECKLIST, encoding="utf-8").read()
    declared = _OPEN_HEADING in text and "PUBLISHED DEPOSIT IS BEHIND" in text.upper()

    if drifted:
        # what a reader following the citation would actually get wrong
        report = os.path.join(ASO, "fusion-junction-aso-research-article.md")
        detail = ""
        if os.path.exists(report):
            n = len(now)
            detail = (f" The repository's archive now holds {n} files against the "
                      f"{state['n_files']} published on {state['published']}.")
        assert declared, (
            "the published Zenodo record no longer matches what this repository would archive, and "
            "the papers that cite it say nothing about that." + detail +
            f"\n\nEither publish a new version and update {os.path.basename(STATE)}, or record the "
            f"drift as an open blocking item under '{_OPEN_HEADING}' in "
            f"{os.path.basename(CHECKLIST)}. A reader following the DOI is reading superseded text "
            "until one of those happens.")
    else:
        assert not declared, (
            "the checklist still carries the deposit-is-behind blocking item, but the manifest now "
            f"matches the digest recorded as published in {os.path.basename(STATE)}. Close the "
            "item — a checklist that keeps a solved blocker open is one nobody reads.")
