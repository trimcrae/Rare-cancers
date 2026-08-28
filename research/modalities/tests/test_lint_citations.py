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
import subprocess
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


def _init_git_repo(path):
    for cmd in (["git", "init", "-q"],
                ["git", "config", "user.email", "probe@example.com"],
                ["git", "config", "user.name", "probe"]):
        subprocess.run(cmd, cwd=path, check=True, capture_output=True)


def test_tracked_sees_an_untracked_file_before_it_is_committed(tmp_path, monkeypatch):
    """AUT-PD-036, 2026-08-28. ⛔ THE DEFECT: `_tracked()` used a bare `git ls-files`, which lists only
    what git already knows about. A brand-new manuscript sat invisible to this scan while uncommitted,
    passed preflight clean on that content, and only went red on the run AFTER it was committed and
    pushed — `research/method-watch-autonomy-prior-art-2.md`, reached `origin/main` as 1765d8cab,
    measured in this ledger item's own evidence trail. That is "firing after the mistake is shared",
    the exact failure gate 12 was put in the commit loop to prevent.

    This builds an ISOLATED git repo (never the real working tree — mutating that from a test is the
    §6 hazard this repository already paid for once) with one committed file and one untracked file,
    and asserts `_tracked()` — pointed at that repo via `ROOT` — returns both.

    ⚠ MUTATION-TESTED: reverting `_tracked()` to a bare `["git", "-C", ROOT, "ls-files"]` makes this
    test fail (the untracked file drops out of the result), confirming it has the power to catch a
    regression rather than passing no matter what the implementation does.
    """
    _init_git_repo(tmp_path)
    (tmp_path / "committed.md").write_text("PMID 10000001 tracked and committed\n", encoding="utf-8")
    subprocess.run(["git", "add", "committed.md"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "draft.md").write_text("PMID 20000002 untracked and new\n", encoding="utf-8")

    monkeypatch.setattr(lc, "ROOT", str(tmp_path))
    files = lc._tracked()

    assert "committed.md" in files
    assert "draft.md" in files, (
        "an untracked-but-not-ignored file must be visible to the citation scan before it is "
        "committed, or a fabricated citation in it is caught only one commit too late")


def test_tracked_still_honours_gitignore_for_untracked_files(tmp_path, monkeypatch):
    """The widened scan adds `--others --exclude-standard`, not `--others` alone — build output and
    caches an author never intended to track must stay out, or every `.gitignore`'d scratch file in
    the tree becomes a citation-gate input.
    """
    _init_git_repo(tmp_path)
    (tmp_path / ".gitignore").write_text("ignored.md\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "ignored.md").write_text("PMID 30000003 must not be scanned\n", encoding="utf-8")

    monkeypatch.setattr(lc, "ROOT", str(tmp_path))
    files = lc._tracked()

    assert "ignored.md" not in files


# ---------------------------------------------------------------------------
# arXiv — AUT-PD-057, 2026-08-28. ⛔ THE DEFECT: `PATTERNS` had PMID / PMCID / DOI / NCT / GEO and
# NO arXiv entry, so every arXiv identifier in this repository's prose sat OUTSIDE this gate — not
# anchored, not baselined, not counted, simply invisible. 67 of them were in prose on the day the
# pattern went in. A fabricated or mistyped arXiv id passed every gate, which is the 2026-08-07
# incident's shape with a weaker excuse: nothing was even looking.
# ---------------------------------------------------------------------------

def test_an_arxiv_identifier_is_extracted_in_every_form_this_repository_writes():
    """The prefixed form, both URL forms and arXiv's own DOI are ONE identifier.

    The version suffix is stripped for the reason the PMID test above gives: `arXiv:2605.10246v2` in
    prose and `arxiv.org/abs/2605.10246` in a fetch product are the same paper, and a checker that
    treats them as two reports a fabrication that is not there while missing its own anchor.
    """
    for form in ("arXiv:2605.10246", "arXiv 2605.10246", "arXiv:2605.10246v2",
                 "arxiv:2605.10246", "ARXIV:2605.10246",
                 "https://arxiv.org/abs/2605.10246", "https://arxiv.org/pdf/2605.10246v1",
                 "https://arxiv.org/html/2605.10246", "doi:10.48550/arXiv.2605.10246"):
        assert lc.extract("ARXIV", form) == ["2605.10246"], form
    # The pre-2007 scheme. This repository contains none (measured 2026-08-28, zero hits in any
    # tracked file), and it is matched anyway because a citation to a 2003 paper is exactly the case
    # a reader would assume is covered. The archive suffix's case is part of the identifier, which is
    # why the case-insensitive flag is scoped to the literal `arxiv` token and not applied globally.
    assert lc.extract("ARXIV", "arXiv:math.GT/0309136") == ["math.GT/0309136"]
    assert lc.extract("ARXIV", "https://arxiv.org/abs/hep-th/9901001v2") == ["hep-th/9901001"]


def test_a_bare_number_shaped_like_an_arxiv_id_is_not_treated_as_one():
    """⛔⛔ THE SINGLE MOST IMPORTANT NEGATIVE CONTROL ON THIS PATTERN, AND IT IS NOT HYPOTHETICAL.

    A modern arXiv id is `YYMM.NNNNN` — four-to-five digits either side of a dot — and THAT SHAPE
    OCCURS INSIDE ORDINARY DOIs. Measured over this repository's prose on 2026-08-28, a bare
    `\\d{4}\\.\\d{4,5}` matched three "identifiers" that are fragments of real, correctly cited DOIs.
    Each would have been reported as an unanchored citation, i.e. a fabrication alarm on honest work,
    which §7 records as the fastest route to a gate being switched off. It also bought nothing: over
    every prose line in this repository mentioning arXiv, the contextual forms capture every
    id-shaped token on the line, residue zero.

    ⚠ THIS TEST IS THE THING THAT GOES RED IF SOMEBODY "IMPROVES" THE PATTERN BY LOOSENING IT.
    """
    for doi_fragment_source in ("[Mol Oncol, DOI 10.1002/1878-0261.13558, PMID 37997254]",
                                "doi:10.1111/j.1349-7006.2012.02370.x. PMID 22726592.",
                                "doi:10.1111/1759-7714.14613. PMID 35974707."):
        assert lc.extract("ARXIV", doi_fragment_source) == [], doi_fragment_source
    # And a plain number in running prose — a year-and-decimal, a run id — is not an identifier.
    assert lc.extract("ARXIV", "the run reported 2026.08281 as its seed") == []


def test_a_fabricated_arxiv_id_is_caught(monkeypatch):
    """⛔ THE CASE THE PATTERN EXISTS FOR: an arXiv id in prose and in no fetch product."""
    monkeypatch.setattr(lc, "survey", lambda: (
        {"ARXIV": {"2699.99999": {"research/method-watch-invented.md"}}}, {}))
    assert lc.check() == 1


def test_and_that_control_can_actually_pass_when_the_arxiv_id_is_anchored(monkeypatch):
    """⚠ The control above is worthless if it goes red no matter what — same shape, anchored."""
    monkeypatch.setattr(lc, "survey", lambda: (
        {"ARXIV": {"2699.99999": {"research/method-watch-invented.md"}}},
        {"ARXIV": {"2699.99999": {"research/method-watch-trigger-hits.json"}}}))
    assert lc.check() == 0


def test_the_arxiv_pattern_still_matches_this_repositorys_own_prose():
    """⛔⛔ THE FAILURE MODE THIS CLASS OF GUARD ACTUALLY HAS: a regex that silently stops matching.

    Every other test here feeds the extractor a string the test itself wrote, so a pattern edited
    into uselessness against REAL prose — a lost alternative, a boundary that no longer fires on a
    markdown link, a scoped case flag dropped — passes all of them while the gate quietly sees
    nothing. A guard that cannot go red is indistinguishable from an absent guard, which is the
    lesson this whole file is built on.

    So this asserts against the corpus: every `kind: ARXIV` row in the ledger must still be findable
    by `extract` in the files that row names. Those rows span both forms this repository actually
    writes (the `arXiv:NNNN.NNNNN` token and the `arxiv.org/abs|pdf/` URL), so losing either one
    takes this red.
    """
    led = lc.load_ledger()
    rows = [e for e in led["entries"] if e["kind"] == "ARXIV"]
    assert rows, "the ledger records no ARXIV rows — the identifier class went missing"
    for e in rows:
        seen = False
        for rel in e["files"]:
            path = os.path.join(lc.ROOT, rel)
            if not os.path.exists(path):
                continue
            if e["id"] in lc.extract("ARXIV", open(path, encoding="utf-8",
                                                   errors="replace").read()):
                seen = True
                break
        assert seen, (
            "ARXIV %s is ledgered against %s but the extractor no longer finds it there — the "
            "pattern stopped matching this repository's own prose" % (e["id"], e["files"]))

    # And a floor on the whole corpus, so a pattern narrowed to exactly the ledgered ids cannot hide
    # behind the loop above. 67 arXiv identifiers were in prose on 2026-08-28; the floor is set well
    # under that so ordinary prose churn does not fire it, and a broken pattern still does.
    # ⚠ THE PROSE HALF ONLY, AND THAT IS A DELIBERATE COST CHOICE, NOT A WEAKER TEST. `survey()`
    # scans the prose files AND every tracked .json/.jsonl fetch product: 34.2 s, measured
    # 2026-08-28, against 1.5 s for the prose half alone. This assertion is about whether the
    # PATTERN sees the corpus, which lives entirely on the prose side, so paying 34 s to re-derive
    # an anchor set nothing here reads would put half a minute on every run of the manuscripts
    # suite for no additional power.
    prose = lc._scan([f for f in lc._tracked() if f.endswith(lc.PROSE_SUFFIXES)])
    assert len(prose.get("ARXIV", {})) >= 40, (
        "only %d arXiv identifier(s) found in prose — the pattern has stopped seeing the corpus"
        % len(prose.get("ARXIV", {})))


def test_every_arxiv_ledger_row_records_how_it_was_checked():
    """⛔ THE ROWS ADDED FOR THIS CLASS ARE NOT PART OF THE 2026-08-07 BASELINE AND MUST NOT LOOK
    LIKE IT.

    `unverified_at_baseline` is the honest status for them — arxiv.org and export.arxiv.org are both
    egress-blocked from this sandbox, so nothing in this repository corroborates them — but a row
    added later with a blank note is an amnesty wearing a baseline's clothes. Each carries the date
    and the channel it was checked through, the shape the `known_absent_upstream` NCT row already
    established, so the next reader can tell a triaged row from a waved-through one.
    """
    led = lc.load_ledger()
    rows = [e for e in led["entries"] if e["kind"] == "ARXIV"]
    assert rows
    for e in rows:
        assert e.get("checked_on"), "ARXIV %s has no checked_on" % e["id"]
        assert e.get("checked_by"), "ARXIV %s has no checked_by" % e["id"]
        assert e.get("note"), "ARXIV %s has a blank note" % e["id"]
    assert "_arxiv_class_added_2026_08_28" in led, (
        "the ledger must say, in one place, that the ARXIV rows post-date the baseline and why "
        "their status is what it is")
