#!/usr/bin/env python3
"""Guards for the persistent accession→symbol cache.

⭐ WHY THE CACHE EXISTS. The probe→symbol bridge is 30.8 of a 33-minute CI job, it is the same
computation every run — the platforms and series it resolves are immutable — and rebuilding it lost
accuracy the day a remote endpoint degraded, which moved published figures and forced a corrections
register into a manuscript.

⛔ WHAT THESE TESTS ARE ACTUALLY PROTECTING is not speed. It is the two ways a cache like this turns
into a liability: freezing an outage in as a permanent fact, and silently deleting what an earlier,
better run had learned.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MOD)

import emc_atr_vulnerability as A  # noqa: E402


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "_ACC_CACHE_PATH", str(tmp_path / "cache.json"))
    monkeypatch.setattr(A, "_ACC_CACHE",
                        {"loaded": False,
                         "by_source": {k: {} for k in A._ACC_CACHE_PRECEDENCE}, "new": 0})
    monkeypatch.setattr(A, "_ACC_RESOLVED", {})
    return tmp_path / "cache.json"


def test_a_cold_start_is_not_an_error(cache):
    assert A._acc_cache_load()["loaded"] is True
    assert A._ACC_RESOLVED == {}


def test_successes_persist_and_reload(cache):
    A._acc_cache_load()
    A._acc_cache_add({"AB123456": "PRMT5"}, "remote_lookup")
    assert A._acc_cache_save()["added"] == 1
    A._ACC_CACHE.update({"loaded": False,
                         "by_source": {k: {} for k in A._ACC_CACHE_PRECEDENCE}, "new": 0})
    A._ACC_RESOLVED.clear()
    A._acc_cache_load()
    assert A._ACC_RESOLVED["AB123456"] == "PRMT5"


def test_a_stronger_source_wins_on_load(cache):
    """Precedence has to be applied at load, not by whichever block happens to be read last."""
    with open(cache, "w", encoding="utf-8") as fh:
        json.dump({"by_source": {"curated_annotation": {"X1": "GOOD"},
                                 "unigene_archive": {"X1": "MEH"},
                                 "remote_lookup": {"X1": "WEAK"}}}, fh)
    A._acc_cache_load()
    assert A._ACC_RESOLVED["X1"] == "GOOD"


def test_a_write_that_would_shrink_the_cache_is_refused(cache):
    """⛔ THE ONE THAT MATTERS MOST. A run degraded by a remote outage resolves less than an earlier
    one. It must never be allowed to delete what the earlier run learned."""
    with open(cache, "w", encoding="utf-8") as fh:
        json.dump({"by_source": {"curated_annotation": {f"A{i}": "G" for i in range(50)},
                                 "unigene_archive": {}, "remote_lookup": {}}}, fh)
    A._ACC_CACHE.update({"loaded": True,
                         "by_source": {"curated_annotation": {"A0": "G"},
                                       "unigene_archive": {}, "remote_lookup": {}},
                         "new": 1})
    out = A._acc_cache_save()
    assert "refused" in out and "DELETE" in out["refused"]
    with open(cache, encoding="utf-8") as fh:
        assert len(json.load(fh)["by_source"]["curated_annotation"]) == 50


def test_a_failure_to_resolve_is_never_written(cache):
    """⛔ Today's silence must not become a permanent finding that an accession has no gene."""
    A._acc_cache_load()
    A._acc_cache_add({"AB999999": None, "": "X", "AB111111": ""}, "remote_lookup")
    assert A._ACC_CACHE["new"] == 0
    assert A._acc_cache_save() is None


def test_an_unknown_source_is_dropped_rather_than_inventing_a_block(cache):
    A._acc_cache_load()
    A._acc_cache_add({"AB123456": "PRMT5"}, "made_up_source")
    assert A._ACC_CACHE["new"] == 0


def test_nothing_new_means_no_write(cache):
    A._acc_cache_load()
    assert A._acc_cache_save() is None
    assert not os.path.exists(cache)
