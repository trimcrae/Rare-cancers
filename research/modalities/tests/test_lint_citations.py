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
    for form in ("PMID: 12345678", "PMID12345678", "PMID:12345678", "(PMID 12345678)",
                 # A fetch corpus names a paper by URL, never by the token "PMID" — and every
                 # lit-targets-*.json in this repo is a {name: url} map, so without these two the
                 # scanner cannot see the repository's own evidence of a retrieval.
                 "https://pubmed.ncbi.nlm.nih.gov/12345678/",
                 "…/search?query=EXT_ID:12345678&resultType=core"):
        assert lc.extract("PMID", form) == ["12345678"], form


def test_a_doi_does_not_carry_prose_punctuation_into_its_identity():
    """A DOI at the end of a sentence picks up the full stop; unstripped, it never matches its anchor."""
    for form in ("see 10.1038/s41586-020-2649-2.",
                 # The prose scanned is MARKDOWN, and the DOI character class eats these, so an
                 # unstripped backtick or bold marker makes a cited DOI a DIFFERENT identifier from
                 # the one sitting in the artifact — a false fabrication alarm on an honest citation.
                 "`10.1038/s41586-020-2649-2`",
                 "**10.1038/s41586-020-2649-2.**"):
        got = lc.extract("DOI", form)
        assert got == ["10.1038/s41586-020-2649-2"], form


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


def test_the_ledger_does_not_anchor_itself():
    """⛔ IT DID, FOR ONE COMMIT. The unanchored count fell 215 -> 0 the moment the ledger existed.

    The ledger is a `.json` enumerating every unanchored identifier, so scanning it as a fetch product
    made all 215 self-anchoring — the gate reporting a clean tree it had just declared dirty. The PASS
    condition never changed (a new fabrication is in neither the ledger nor an artifact), and that is
    what made it dangerous: the guard kept working while its readout went vacuous, and 0 is the one
    number nobody re-examines. A guard whose output stops meaning anything is not half-working.

    ⚠ THE ORIGINAL ASSERTIONS ENCODED A STRICTER RULE THAN THE INCIDENT, AND IT PENALISED THE FIX.
    They demanded (a) no entry anchored by ANY artifact and (b) `len(unanchored) == len(entries)`.
    Both go red the moment somebody anchors a previously-unanchored identifier — i.e. the moment
    somebody does the work the ledger exists to request — and the ledger's own
    `_the_count_is_meant_to_fall` says that count SHOULD drop. Measured 2026-08-08: 76 identifiers
    were legitimately anchored by real fetches and this test called it a regression. §7's warning is
    exactly this shape: a gate that goes red on honest work gets switched off, taking the case it
    exists for with it. What the incident actually requires is narrower and is what is asserted now.
    """
    prose, anchors = lc.survey()
    led = lc.load_ledger()
    ledger_rel = os.path.relpath(lc.LEDGER, lc.ROOT).replace(os.sep, "/")

    # (a) THE REAL INVARIANT: the ledger file may never be one of the files that ANCHORS an entry.
    # Anchoring by a genuine fetch product is the desired outcome and must stay legal.
    self_anchored = [e["key"] for e in led["entries"]
                     if ledger_rel in anchors.get(e["kind"], {}).get(e["id"], set())]
    assert not self_anchored, "ledger entries anchored by the ledger itself: %s" % self_anchored[:5]

    # (b) The pass condition `check()` enforces is a SUBSET rule, not an equality: every still
    # unanchored identifier must be enumerated. The ledger may legitimately be larger, because a row
    # is retained after its identifier is anchored — that history is the audit trail.
    un = lc.unanchored(prose, anchors)
    known = {lc._norm_stored_key(e["key"]) for e in led["entries"]}
    missing = [lc._key(k, i) for k, i, _ in un if lc._key(k, i) not in known]
    assert not missing, "unanchored identifiers absent from the ledger: %s" % missing[:5]


def test_a_failed_fetch_record_does_not_anchor_its_own_interstitial_text():
    """⛔⛔ THE EXACT INCIDENT (AUT-PD-038, 2026-08-27): a 403's stored bot-protection page anchored
    a real citation, because the anchor test was "this identifier is inside a tracked .json", not
    "a fetch that actually retrieved something put it there". Three straight 403s on
    `browser-fetch.json` — each one's own note reading "not fixable by retrying" — satisfied a gate
    that exists to establish somebody could read the page. This is the negative control: a fetch
    record whose own `status` is not 2xx must contribute nothing to the anchor set.
    """
    node = {"url": "https://example.com/blocked", "status": 403,
            "attempts": [{"n": 1, "status": 403, "chars": 40}],
            "text": "security check DOI 10.1089/nat.2024.0072 interstitial"}
    assert lc._is_fetch_record(node)
    assert not lc._fetch_succeeded(node)
    redacted = lc._redact_failed_fetches(node)
    assert lc.extract("DOI", str(redacted)) == []
    # A never-resolved attempt (every retry errored before a status came back) is `status: None`,
    # not an int — must fail the same way, not slip past an `isinstance` check that assumes int.
    never_resolved = {"url": "https://example.com/dead", "status": None,
                       "attempts": [{"n": 1, "status": 404}],
                       "text": "PMID 12345678 in the 404 body"}
    assert not lc._fetch_succeeded(never_resolved)
    assert lc.extract("PMID", str(lc._redact_failed_fetches(never_resolved))) == []


def test_a_successful_fetch_record_still_anchors():
    """⚠ THE CONTROL ABOVE IS WORTHLESS IF REDACTION BLINDS EVERY RECORD, FAILED OR NOT.

    Same shape, `status: 200` — the identifier must survive, or the fix trades a false anchor for
    a false fabrication alarm on every real citation this repository has ever fetched.
    """
    node = {"url": "https://example.com/ok", "status": 200,
            "attempts": [{"n": 1, "status": 200, "chars": 40}],
            "text": "retrieved: DOI 10.1089/nat.2024.0072 in full"}
    assert lc._fetch_succeeded(node)
    redacted = lc._redact_failed_fetches(node)
    assert lc.extract("DOI", str(redacted)) == ["10.1089/nat.2024.0072"]


def test_redaction_leaves_non_fetch_records_untouched():
    """A record with no `attempts`/`status`/`url` triple — a registry row, a graph edit — is not a
    fetch outcome at all, and must anchor exactly as it always has. The three-key signature exists
    so this stays true: `attempts` as a bare retry counter (this repo's own ledger rows) must not
    be mistaken for an HTTP fetch log and blanked.
    """
    registry_row = {"pmid": "12345678", "attempts": 2, "note": "PMID 12345678 curated by hand"}
    assert not lc._is_fetch_record(registry_row)
    assert lc._redact_failed_fetches(registry_row) == registry_row


def test_lit_targets_bare_digit_keys_are_unaffected_by_redaction():
    """The `lit-targets-*.json` bare-numeric-key convention is a different anchor mechanism (a
    quoted digit-run KEY, not a PATTERNS match) and is scanned from the raw file text on purpose —
    confirm the fix did not silently detour it through the JSON round-trip too.
    """
    import inspect
    src = inspect.getsource(lc._scan)
    after_bare_digit_comment = src.split("A THIRD FORM", 1)[1]
    assert 're.findall(r\'"(\\d{6,9})"\\s*:\', text)' in after_bare_digit_comment
