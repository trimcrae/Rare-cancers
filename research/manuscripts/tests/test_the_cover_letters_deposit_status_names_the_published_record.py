#!/usr/bin/env python3
"""The cover letter's deposit status must be a status FOR the record that is actually published.

⛔⛔ THIS SENTENCE HAS TURNED OVER FOUR TIMES ON FOUR IDENTIFIERS, AND THE FOURTH REACHED A
SUBMISSION DELIVERABLE. On 2026-09-02 the live banner read "Both papers now cite
10.5281/zenodo.22180100, a RESERVED BUT UNPUBLISHED version ... Until it is published the archive
links in both papers resolve to nothing." By then every deliverable printed 22229096, published
2026-09-01 and read back from Zenodo's records API. Every clause was false, in the one document that
goes to an editor.

★ AND `lint_citations` PASSES ON IT, CORRECTLY. A stale DOI is perfectly well anchored — it was
fetched, it resolves, it is in the ledger. PROVENANCE and CURRENCY are different questions, exactly
as claim STRENGTH and claim PROVENANCE are (CLAUDE.md §7). Nothing in the repository asked the
currency question about this file, which is why it went wrong four times under green gates.

★★ THE RULE THE FILE ITSELF ALREADY STATED: *name the identifier a status is a status FOR.* It is
written four paragraphs below the banner that breaks it. This module is that rule with an exit code.

⚠ WHAT THIS DOES NOT DO. It does not require the deposit to be current, or the letter to be
sendable, or any particular wording. Drift between deposits is normal. It requires only that a
statement ABOUT the published record name the record that is published, and that the letter not
assert the archive is unresolvable while the recorded state says otherwise.
"""

from __future__ import annotations

import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
LETTER = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-cover-letter.md")
STATE = os.path.join(MANUSCRIPTS, "aso", "deposit-state.json")

#: ⛔ THE LIVE BANNER ONLY. Everything under a "Superseded, retained" marker is history that the
#: repository deliberately keeps (CLAUDE.md rule 1.2), and grading it would make honest record-keeping
#: fail the build — the same scoping error that let a number inside a CLOSED checklist item satisfy
#: the deposit-drift guard on this very day.
_SUPERSEDED = re.compile(r"⚠\s*\*?Superseded", re.I)


def _live_banner():
    text = open(LETTER, encoding="utf-8").read()
    paragraphs = re.split(r"\n\s*\n", text)
    live = [p for p in paragraphs if "NOT SENDABLE" in p or "ARCHIVE ITEM IS" in p]
    live = [p for p in live if not _SUPERSEDED.search(p)]
    return "\n\n".join(live)


def _published():
    return (json.load(open(STATE, encoding="utf-8")).get("published") or {})


def test_the_live_banner_names_the_doi_that_is_recorded_as_published():
    doi = _published().get("doi")
    assert doi, "deposit-state.json records no published DOI, so this guard has no anchor"
    banner = _live_banner()
    assert banner, (
        "no live deposit-status paragraph found in the cover letter. Either the banner was removed "
        "— in which case delete this guard rather than leave it watching nothing — or its marker "
        "changed and this needs re-anchoring.")
    number = doi.rsplit(".", 1)[-1]
    assert number in banner, (
        "the cover letter's live deposit status does not name %s, the record deposit-state.json "
        "says is published. This banner has already turned over four times on four identifiers and "
        "the fourth reached a submission deliverable saying the archive links resolve to nothing "
        "while they resolved. Name the identifier the status is a status FOR.\n\n  banner: %s"
        % (doi, banner[:400]))


def test_the_live_banner_does_not_call_a_published_archive_unresolvable():
    """⛔ THE FALSE CLAUSE ITSELF, NOT JUST THE WRONG NUMBER. The 2026-09-02 banner would have passed
    a name check alone if it had merely been vague; what made it wrong was asserting the links were
    dead. That assertion is only admissible while something is genuinely unpublished."""
    state = json.load(open(STATE, encoding="utf-8"))
    if state.get("pending"):
        pytest.skip("a version is drafted and unpublished, so 'resolve to nothing' may be true — "
                    "SKIP IS DELIBERATE and narrow: it lasts exactly as long as `pending` does")
    banner = _live_banner().lower()
    for claim in ("resolve to nothing", "resolves to nothing", "nothing is published"):
        assert claim not in banner, (
            "the cover letter's live status says %r while deposit-state.json records %s as "
            "published with no pending draft. That is the exact sentence that reached the "
            "submission packet on 2026-09-02." % (claim, _published().get("doi")))


def test_no_deliverable_still_prints_a_superseded_identifier_as_current():
    """The letter may QUOTE a retired identifier inside its own retained history; it may not present
    one as the archive a reader should go to."""
    doi = _published().get("doi", "")
    banner = _live_banner()
    stale = {m for m in re.findall(r"10\.5281/zenodo\.(\d+)", banner)} - {doi.rsplit(".", 1)[-1]}
    assert not stale, (
        "the live banner presents %s alongside the published %s. A retired identifier belongs under "
        "a `Superseded, retained` marker, where a reader can see it is history — not in the "
        "sentence that tells an editor where the archive is." % (sorted(stale), doi))
