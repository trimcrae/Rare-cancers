#!/usr/bin/env python3
"""The citation-scan cache may skip work; it may never change an answer.

⛔⛔ THE GATE THIS SITS IN FRONT OF IS THE ONE THAT CATCHES A FABRICATED IDENTIFIER. CLAUDE.md §7:
"never fabricate medical facts, stats, citations or patient data", and `lint_citations` is what
makes that checkable — every PMID, DOI and accession in prose must trace to a fetch product or the
ledger. A cache that got this wrong would either invent an anchor for a fabricated identifier or
hide a real one, and it would do it silently.

★ SO EVERY TEST HERE IS A WAY THE CACHE COULD LIE, DRIVEN RATHER THAN DESCRIBED. The key must move
when the FILE moves and when the SCANNER moves; a malformed entry must re-scan; and the cache must
never be a tracked file, because the gate is also run from pytest and a tracked write is a
tracked-tree failure (AUT-PD-186).

⚠ WHAT IT CACHES IS NARROW ON PURPOSE: which identifiers a file CONTAINS. Whether a citation is
anchored is decided afterwards, in full, on every run, by comparing prose against anchors — this
module never sees that comparison.
"""
from __future__ import annotations

import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MANUSCRIPTS))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(MANUSCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C = _load("citation_scan_cache")
SCANNER = "a" * 64


def test_the_key_moves_when_the_files_bytes_move():
    """⛔ THE ONE THAT MATTERS MOST. A fetch product gaining a new record must not return the old
    identifier set, or a genuinely new anchor stays invisible and a genuinely removed one keeps
    anchoring a citation that no longer has evidence behind it."""
    a = C.key_for("x.json", b'{"url": "u", "status": 200}', SCANNER)
    b = C.key_for("x.json", b'{"url": "u", "status": 403}', SCANNER)
    assert a and b and a != b


def test_the_key_moves_when_the_SCANNER_moves():
    """⛔⛔ THE HALF A NAIVE CACHE WOULD OMIT, AND IT IS THE DANGEROUS ONE. `PATTERNS`, `TRAILING`,
    the failed-fetch redaction and the bare-key corpus rule all live in `lint_citations.py`. Widen a
    pattern to catch a new identifier form and every cached entry answers the OLD question — the
    gate keeps reporting on the previous version of itself, on unchanged files, forever. Tightening
    a guard must make a cache colder, never blinder."""
    blob = b'{"url": "u", "status": 200}'
    assert C.key_for("x.json", blob, "a" * 64) != C.key_for("x.json", blob, "b" * 64)


def test_the_key_moves_when_the_PATH_moves():
    """The value records which FILE an identifier was found in — that is what `{identifier: {files}}`
    is for — so two files with identical bytes must not share an entry."""
    blob = b'{"url": "u", "status": 200}'
    assert C.key_for("a.json", blob, SCANNER) != C.key_for("b.json", blob, SCANNER)


def test_no_scanner_digest_means_no_key_and_therefore_a_full_scan():
    """⛔ FAIL CLOSED. If the scanner's own source cannot be read, the cache cannot know what
    question its entries answered, so it must answer none of them."""
    assert C.key_for("x.json", b"{}", None) is None
    assert C.lookup({"anything": {"PMID": ["1"]}}, None) is None


def test_a_malformed_entry_re_scans_rather_than_passing():
    """A truncated write, a half-finished file, a shape from a future version — each must be a MISS.
    ⛔ An entry that is 'close enough' is the worst outcome: it would return a PARTIAL identifier
    set, and a missing identifier in the ANCHOR half reads as a fabricated citation while a missing
    one in the PROSE half reads as a clean document."""
    key = C.key_for("x.json", b"{}", SCANNER)
    for bad in ({"PMID": "not-a-list"}, {"PMID": [1, 2]}, "a string", ["a", "list"], None,
                {"PMID": ["ok"], "DOI": None}):
        assert C.lookup({key: bad}, key) is None, "%r was accepted" % (bad,)
    assert C.lookup({key: {"PMID": ["12345678"]}}, key) == {"PMID": ["12345678"]}


def test_an_unreadable_or_foreign_cache_is_a_total_miss(tmp_path, monkeypatch):
    """A corrupt file, or one written under another schema, must yield nothing at all."""
    p = tmp_path / "c.json"
    monkeypatch.setattr(C, "CACHE", str(p))
    assert C.load() == {}
    p.write_text("{ not json", encoding="utf-8")
    assert C.load() == {}
    p.write_text(json.dumps({"_schema": "other/9", "entries": {"k": {"PMID": ["1"]}}}),
                 encoding="utf-8")
    assert C.load() == {}


def test_the_round_trip_preserves_the_identifier_set(tmp_path, monkeypatch):
    """The cache must be usable at all — a cache that can never hit is a slow gate with extra parts."""
    p = tmp_path / "c.json"
    monkeypatch.setattr(C, "CACHE", str(p))
    key = C.key_for("x.json", b"{}", SCANNER)
    assert C.save(C.record({}, key, {"PMID": {"12345678"}, "DOI": set()})) is True
    got = C.lookup(C.load(), key)
    assert got == {"PMID": ["12345678"]}, (
        "an empty kind must not be stored as a kind, and a stored kind must survive the file")


def test_the_cache_is_never_a_tracked_file():
    """⛔⛔ IT LIVES OUTSIDE THE REPOSITORY, AND THAT IS NOT TIDINESS. `lint_citations` is run from
    pytest as well as from preflight, and `tracked_tree_guard` fails any pytest run that modifies a
    tracked file (AUT-PD-186). A cache inside the tree would also be stageable by `git add -A` and
    would go stale in the index. Keyed by repository path so two worktrees on one box do not share
    one."""
    assert not C.CACHE.startswith(REPO + os.sep), (
        "the citation-scan cache moved inside the repository (%s). It is written during a gate that "
        "also runs under pytest, so a tracked path there turns every scan into a tracked-tree "
        "failure — and makes the cache committable, which it must never be." % C.CACHE)
    assert os.path.basename(C.CACHE).startswith("emc-citation-scan-")


def test_a_failed_write_does_not_fail_the_gate(tmp_path, monkeypatch):
    """⛔ THE ACCELERATOR MUST NEVER BE THE REASON A CITATION GATE GOES RED. A read-only temp dir, a
    full disk, a racing sibling — each makes the cache useless and none of them makes the scan
    wrong."""
    monkeypatch.setattr(C, "CACHE", str(tmp_path / "no-such-dir" / "c.json"))
    assert C.save({"k": {"PMID": ["1"]}}) is False
    assert C.load() == {}


def test_the_scanner_digest_is_the_scanners_own_bytes():
    """Pins WHICH file defines the question, so moving `PATTERNS` elsewhere reds this rather than
    silently narrowing what the key covers."""
    import hashlib
    with open(os.path.join(MANUSCRIPTS, "lint_citations.py"), "rb") as fh:
        expected = hashlib.sha256(fh.read()).hexdigest()
    assert C.scanner_digest() == expected
    src = open(os.path.join(MANUSCRIPTS, "lint_citations.py"), encoding="utf-8").read()
    assert "PATTERNS = {" in src and "TRAILING = " in src, (
        "the scanner's defining constants have moved out of the file this cache hashes — re-key the "
        "cache on whatever now owns them, or every entry answers a question nobody asked")
