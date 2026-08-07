"""The citation-provenance gate. ($0, stdlib, offline)

⛔ THE DEFECT THIS GATE EXISTS FOR (2026-08-07): an agent drafting a manuscript wrote a PMID from
RECOLLECTION, present in no committed source anywhere in the repository, and it passed `lint_claims`
TWICE. Six invented titles went out in the same pass. `lint_claims` checks claim STRENGTH, not citation
PROVENANCE, and no other preflight gate read an identifier at all.

⚠ THE TESTS THAT MATTER HERE ARE THE NEGATIVE CONTROLS. A provenance checker that returns "all clear"
is indistinguishable from one that is not looking, which is precisely how the fabricated PMID survived
two linter runs. So every green assertion below is paired with a deliberately broken input that must go
red -- and one of those controls is itself checked for having the power to fail.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MOD))   # tests -> modalities -> research -> repo root
sys.path.insert(0, os.path.join(ROOT, "research", "manuscripts"))

import lint_citations as lc  # noqa: E402


def test_the_repository_currently_passes():
    """The gate is green on HEAD. If this fails, a NEW unanchored identifier was introduced."""
    assert lc.check() == 0


def test_a_pmid_typed_from_memory_is_caught(monkeypatch):
    """⛔ THE EXACT INCIDENT, REPRODUCED: an identifier in prose and in no fetch product."""
    monkeypatch.setattr(lc, "survey", lambda: (
        {"PMID": {"31415926": {"research/manuscripts/invented.md"}}}, {}))
    assert lc.check() == 1


def test_and_that_control_can_actually_pass_when_the_identifier_is_anchored(monkeypatch):
    """⚠ THE CONTROL ABOVE IS WORTHLESS IF IT GOES RED NO MATTER WHAT.

    A negative control that cannot pass is not a control -- it is a constant. This asserts the same
    shape with the identifier present in a fetch product, which must be green, so the red above is
    attributable to the anchoring and not to the harness.
    """
    monkeypatch.setattr(lc, "survey", lambda: (
        {"PMID": {"31415926": {"research/manuscripts/invented.md"}}},
        {"PMID": {"31415926": {"research/modalities/some-fetch.json"}}}))
    assert lc.check() == 0


def test_a_ledgered_identifier_stays_green(monkeypatch):
    """Baselined entries must not fail, or the gate gets switched off on day one."""
    led = lc.load_ledger()
    assert led is not None, "the ledger must exist on HEAD"
    e = led["entries"][0]
    monkeypatch.setattr(lc, "survey", lambda: (
        {e["kind"]: {e["id"]: set(e["files"])}}, {}))
    assert lc.check() == 0


def test_baseline_refuses_to_overwrite_an_existing_ledger():
    """⛔ IF --baseline COULD BE RE-RUN, EVERY FUTURE FABRICATION IS ONE COMMAND FROM BEING BLESSED.

    That would make the gate launder exactly what it exists to catch, and it would look like a fix
    while doing it. Growing the ledger has to be a deliberate, reviewable edit.
    """
    assert os.path.exists(lc.LEDGER)
    assert lc.baseline() == 2


def test_identifier_forms_normalise_so_prose_and_artifact_compare_equal():
    """`PMID: 123456`, `PMID123456` and a bare id in JSON are ONE identifier.

    A checker that treats them as three reports fabrications that do not exist and — far worse —
    fails to match a real anchor, so a correctly-cited PMID would be flagged and the noise would bury
    the one real hit.
    """
    import re
    pat = lc.PATTERNS["PMID"]
    for form in ("PMID: 12345678", "PMID12345678", "PMID:12345678", "(PMID 12345678)"):
        assert re.findall(pat, form) == ["12345678"], form


def test_a_doi_does_not_carry_prose_punctuation_into_its_identity():
    """A DOI at the end of a sentence picks up the full stop; unstripped, it never matches its anchor."""
    import re
    got = re.findall(lc.PATTERNS["DOI"], "see 10.1038/s41586-020-2649-2.")
    assert got, "DOI pattern matched nothing"
    assert got[0].rstrip(lc.TRAILING) == "10.1038/s41586-020-2649-2"


def test_the_ledger_is_well_formed_and_says_what_an_entry_does_not_mean():
    """⚠ An entry means NOTHING CORROBORATES IT — not that the citation is wrong.

    If the file ever stops saying so, the next reader treats 200-odd real citations as suspected
    fabrications, which is both false and the fastest route to the gate being deleted.
    """
    led = lc.load_ledger()
    assert led["entries"], "empty ledger"
    for e in led["entries"]:
        assert e["status"] in lc.STATUSES, e
        assert e["key"] == "%s:%s" % (e["kind"], e["id"])
        assert e["files"], e["key"]
    assert "NOT that the citation is wrong" in led["_what_an_entry_means"]
    assert "count is meant to fall" in json.dumps(led).lower().replace("_", " ")


def test_preflight_actually_runs_this_gate():
    """⛔ A GATE THAT NOTHING INVOKES IS ABSENT.

    `verify_map_edit_anchors.py` sat rotted for days in this repository for exactly this reason: no
    test and no workflow ran it, so nothing could report that it had broken. Asserting the wiring is
    the difference between a guard and a description of one.
    """
    sh = open(os.path.join(ROOT, "scripts", "preflight.sh"), encoding="utf-8").read()
    assert "lint_citations.py" in sh, "preflight does not run the citation-provenance gate"
    assert "rc=1" in sh.split("lint_citations.py", 1)[1][:400], "the gate cannot fail the script"
