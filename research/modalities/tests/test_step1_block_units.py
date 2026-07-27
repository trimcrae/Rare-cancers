"""BLOCKING A UNIT — the guard against an unbounded loop of short, useless rentals.

`_pending` meant "no ddg.json yet". A unit that CANNOT produce one therefore never left it, so every launch
tick rented a fresh host for an edge whose leg aborts in minutes on a defect no host can fix. That had
already happened twice for `cw_bio_nmethyl_amide` (12:55 and 13:12 ET, 2026-07-27) before it was diagnosed.
The bill per attempt is small; the loop is unbounded in time, which is the worse property.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import congeneric_fanout_vast as cfv  # noqa: E402


class _S3:
    """The two calls `_pending` makes, and nothing else."""

    def __init__(self, have_results=(), blocked_doc=None):
        self.have = set(have_results)
        self.blocked_doc = blocked_doc

    def head_object(self, Bucket, Key):  # noqa: N803 — boto3's signature
        if Key in self.have:
            return {"ContentLength": 1}
        raise KeyError(Key)

    def get_object(self, Bucket, Key):  # noqa: N803
        raise KeyError(Key)


@pytest.fixture(autouse=True)
def _no_env_override(monkeypatch):
    monkeypatch.delenv("FANOUT_BLOCK_UNITS", raising=False)


def _units():
    return cfv.default_units()


def test_a_blocked_unit_is_not_pending_and_therefore_never_rents_a_host(monkeypatch):
    units = _units()
    target = next(u for u in units if "cw_bio_nmethyl_amide" in u["unit_id"])
    monkeypatch.setattr(cfv, "_load_blocked",
                        lambda s3, b: {target["unit_id"]: {"why": "no mapper reaches the provable floor",
                                                           "evidence": "step1-map-diag.json"}})
    monkeypatch.setattr(cfv, "_exists", lambda *a, **k: False)
    pending = cfv._pending(_S3(), "b", units)
    assert target["unit_id"] not in {u["unit_id"] for u in pending}
    assert len(pending) == len(units) - 1


def test_a_block_is_ANNOUNCED_never_silent(monkeypatch, capsys):
    """CLAUDE.md §6 names holding silently as worse than the problem — a fleet that never launches an edge
    must not look like one that finished it."""
    units = _units()
    target = next(u for u in units if "cw_bio_nmethyl_amide" in u["unit_id"])
    monkeypatch.setattr(cfv, "_load_blocked",
                        lambda s3, b: {target["unit_id"]: {"why": "MAPPER_CANNOT_REACH_FLOOR",
                                                           "evidence": "step1-map-diag.json"}})
    monkeypatch.setattr(cfv, "_exists", lambda *a, **k: False)
    cfv._pending(_S3(), "b", units)
    out = capsys.readouterr().out
    assert "BLOCKED, not launching" in out
    assert "MAPPER_CANNOT_REACH_FLOOR" in out
    assert "step1-map-diag.json" in out


def test_nothing_is_blocked_by_default(monkeypatch):
    """The list is empty until someone writes one with a reason. A guard that blocks by default would
    silently shrink the map."""
    monkeypatch.setattr(cfv, "_get_json", lambda *a, **k: None)
    assert cfv._load_blocked(_S3(), "b") == {}


def test_a_finished_unit_is_still_skipped_for_the_right_reason(monkeypatch):
    units = _units()
    done = units[0]
    monkeypatch.setattr(cfv, "_load_blocked", lambda s3, b: {})
    monkeypatch.setattr(cfv, "_exists",
                        lambda s3, b, key: key == cfv.result_key(done, cfv.RESULT_PREFIX))
    pending = cfv._pending(_S3(), "b", units)
    assert done["unit_id"] not in {u["unit_id"] for u in pending}
    assert len(pending) == len(units) - 1


def test_the_env_override_can_add_a_block_but_not_remove_one(monkeypatch):
    """An operator lever for the moment before the S3 record exists. It must not be able to UNBLOCK, or a
    stray env var would resume renting for an edge someone deliberately stopped."""
    units = _units()
    target = next(u for u in units if "cw_bio_nmethyl_amide" in u["unit_id"])
    monkeypatch.setattr(cfv, "_get_json",
                        lambda *a, **k: {"units": {target["unit_id"]: {"why": "recorded", "evidence": None}}})
    monkeypatch.setenv("FANOUT_BLOCK_UNITS", units[1]["unit_id"])
    blocked = cfv._load_blocked(_S3(), "b")
    assert target["unit_id"] in blocked and blocked[target["unit_id"]]["why"] == "recorded"
    assert units[1]["unit_id"] in blocked


def test_block_is_a_distinct_mode_from_reap():
    """`reap` condemns a HOST, `block` condemns a UNIT. Wiring them to one mode would mean a unit-level
    defect rents a fresh box to fail identically, or a bad host abandons a good edge."""
    names = [flag for flag, _ in cfv._MODES]
    assert "BLOCK" in names and "REAP" in names


def test_the_map_artifact_names_every_blocked_edge():
    """A map that is silently 18 of 19 is a map nobody can grade, and this lane already holds itself to
    stating which species were NOT computed and why."""
    import inspect
    src = inspect.getsource(cfv.mode_collect)
    assert '"blocked_units"' in src
