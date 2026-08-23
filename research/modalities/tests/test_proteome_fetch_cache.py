"""Guards for the per-run proteome cache.

⛔ WHY A CACHE NEEDS TESTS AT ALL. This one sits under a function whose own comments are about the
worst failure this lane has: a TRUNCATED proteome scores every peptide absent from the missing tail
as NOVEL, and prints a confident, wrong headline. A cache turns any such body from a one-step
mistake into a durable one that every later step reads. So the two properties below are the whole
justification for the cache existing: it must never be written from a fetch that did not complete,
and reading it must produce exactly what parsing the fetch would have produced.
"""
import importlib.util
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)

_spec = importlib.util.spec_from_file_location(
    "junction_proteome_novelty", os.path.join(MOD, "junction_proteome_novelty.py"))
jpn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(jpn)

FASTA = (">sp|P00001|AAA_HUMAN Alpha OS=Homo sapiens\nMKWVTFIS\nLLFLFSSA\n"
         ">sp|Q00002|BBB_HUMAN Beta OS=Homo sapiens\nQQNMPCVQAQY\n")


def test_a_cached_read_parses_identically_to_a_fresh_fetch(tmp_path, monkeypatch):
    """The cache is only sound if it is invisible: same entries, same order, same sequences."""
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    calls = []

    def _fake(url, tries=3):
        calls.append(url)
        return FASTA

    monkeypatch.setattr(jpn, "_fetch_paginated", _fake)
    first = jpn.fetch_proteome(url="https://example.invalid/one")
    second = jpn.fetch_proteome(url="https://example.invalid/one")
    assert first == second
    assert len(calls) == 1, "the second call refetched instead of reading the cache"
    assert first == [("P00001", "AAA_HUMAN Alpha", "MKWVTFISLLFLFSSA"),
                     ("Q00002", "BBB_HUMAN Beta", "QQNMPCVQAQY")]


def test_a_different_url_is_a_different_cache_entry(tmp_path, monkeypatch):
    """⛔ Reviewed and UNREVIEWED are different proteomes fetched by the same function. One cache
    file for both would serve TrEMBL's answer to the reviewed-only question, which is the headline
    number the manuscript quotes."""
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    monkeypatch.setattr(jpn, "_fetch_paginated",
                        lambda url, tries=3: FASTA if url.endswith("one") else ">sp|X|X X\nAAAA\n")
    a = jpn.fetch_proteome(url="https://example.invalid/one")
    b = jpn.fetch_proteome(url="https://example.invalid/two")
    assert a != b
    assert jpn._cache_path("https://example.invalid/one") != \
        jpn._cache_path("https://example.invalid/two")


def test_a_failed_fetch_leaves_no_cache_behind(tmp_path, monkeypatch):
    """⛔ THE ONE THAT MATTERS. A partial or failed body is never a result here; caching one would
    make a single truncation permanent for every step that reads it afterwards."""
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))

    def _boom(url, tries=3):
        raise RuntimeError("proteome page 3 failed after 3 attempts")

    monkeypatch.setattr(jpn, "_fetch_paginated", _boom)
    with pytest.raises(RuntimeError):
        jpn.fetch_proteome(url="https://example.invalid/three")
    assert not os.path.exists(jpn._cache_path("https://example.invalid/three"))


def test_an_empty_cache_file_is_ignored_rather_than_served(tmp_path, monkeypatch):
    """A zero-record file is not a proteome. Serving it would score every peptide as novel."""
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    path = jpn._cache_path("https://example.invalid/four")
    open(path, "w").close()
    monkeypatch.setattr(jpn, "_fetch_paginated", lambda url, tries=3: FASTA)
    assert len(jpn.fetch_proteome(url="https://example.invalid/four")) == 2


def test_the_cache_never_lands_in_the_repository(tmp_path, monkeypatch):
    """A 100 MB proteome snapshot beside the results is an artifact nobody diffs."""
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    path = jpn._cache_path(jpn.PROTEOME_URL)
    repo = os.path.dirname(os.path.dirname(MOD))
    assert not os.path.abspath(path).startswith(os.path.abspath(repo) + os.sep)
