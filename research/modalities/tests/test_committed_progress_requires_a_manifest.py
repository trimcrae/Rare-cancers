"""The board's progress frontier must be the frontier a rented host would RESUME from.

Founding case, 2026-07-30 (valB closure triangle, T3 ternary leg): the board printed
`committed: production/1800` in the same minute a freshly rented host printed
`[spot-driver] restore -> production@iter 1760`. Neither was wrong about S3 — they applied different
rules to it. `committed_progress` globbed any object under `iter-N/`; `restore_latest` accepts only a
generation carrying its `COMMITTED.json`, which `_persist` writes LAST. The leg re-ran the same 40
iterations after every host change and the board's number rose each time, so the rework was invisible.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ternary_vast_launch as tv  # noqa: E402

UID = "calib_hi_to_lo2__ternary_vhl_r0_dt2.0fs_wu1.0_triangle"
BASE = f"ternary-vast/commits/{UID}"


class _FakeS3:
    def __init__(self, keys, raise_on_list=False):
        self._keys = list(keys)
        self._raise = raise_on_list

    def get_paginator(self, _name):
        outer = self

        class P:
            def paginate(self, **kw):
                del kw
                if outer._raise:
                    raise RuntimeError("AccessDenied")
                yield {"Contents": [{"Key": k} for k in outer._keys]}
        return P()


def _gen(phase, it, gen, *names):
    return [f"{BASE}/{phase}/iter-{it:08d}/{gen}/{n}" for n in names]


def _progress(monkeypatch, keys, raise_on_list=False):
    monkeypatch.setattr(tv, "_s3", lambda: _FakeS3(keys, raise_on_list))
    return tv.committed_progress(UID)


def test_the_manifest_name_matches_the_store_that_writes_it():
    # If the store ever renames its manifest, the board must not silently go back to counting bytes.
    from rbfe_spot_checkpoint import _BaseCommitStore

    assert tv.COMMIT_MANIFEST == _BaseCommitStore.MANIFEST


def test_a_generation_with_a_manifest_counts(monkeypatch):
    keys = _gen("production", 1760, "aaa", "prod.nc", "prod.chk", tv.COMMIT_MANIFEST)
    assert _progress(monkeypatch, keys) == ("production", 1760, 1_000_000 + 1760)


def test_the_founding_case_a_manifestless_newer_generation_does_not_move_the_frontier(monkeypatch):
    keys = (_gen("production", 1760, "aaa", "prod.nc", "prod.chk", tv.COMMIT_MANIFEST)
            + _gen("production", 1800, "bbb", "prod.nc", "prod.chk"))  # manifest never landed
    phase, it, scalar = _progress(monkeypatch, keys)
    assert (phase, it) == ("production", 1760), "1800 has no manifest; no host can resume from it"
    assert scalar == 1_000_000 + 1760


def test_the_gap_is_printed_not_swallowed(monkeypatch, capsys):
    keys = (_gen("production", 1760, "aaa", tv.COMMIT_MANIFEST)
            + _gen("production", 1800, "bbb", "prod.nc"))
    _progress(monkeypatch, keys)
    out = capsys.readouterr().out
    assert "objects at iter 1800" in out and "1760" in out


def test_no_gap_line_when_every_generation_is_complete(monkeypatch, capsys):
    keys = _gen("production", 400, "aaa", "prod.nc", tv.COMMIT_MANIFEST)
    _progress(monkeypatch, keys)
    assert "objects at iter" not in capsys.readouterr().out


def test_a_manifestless_generation_alone_reads_as_no_progress(monkeypatch):
    # Not "some progress" — a host would start this phase from scratch, and the board must say so.
    keys = _gen("production", 40, "aaa", "prod.nc", "prod.chk")
    assert _progress(monkeypatch, keys) == (None, 0, 0)


def test_warmup_is_held_to_the_same_rule(monkeypatch):
    keys = (_gen("warmup", 8, "aaa", tv.COMMIT_MANIFEST)
            + _gen("warmup", 16, "bbb", "warm.nc"))
    assert _progress(monkeypatch, keys) == ("warmup", 8, 8)


def test_production_still_outranks_warmup_so_the_transition_is_not_a_regression(monkeypatch):
    keys = (_gen("warmup", 768, "aaa", tv.COMMIT_MANIFEST)
            + _gen("production", 40, "bbb", tv.COMMIT_MANIFEST))
    phase, it, scalar = _progress(monkeypatch, keys)
    assert (phase, it) == ("production", 40)
    assert scalar > 768


def test_an_unreadable_listing_is_still_distinguished_from_zero(monkeypatch):
    # -1 means "could not tell", and it must NOT be conflated with "nothing committed" — the stall
    # detector treats those differently, and this change must not disturb that.
    assert _progress(monkeypatch, [], raise_on_list=True) == (None, 0, -1)
    assert _progress(monkeypatch, []) == (None, 0, 0)


def test_a_manifest_key_elsewhere_in_the_prefix_does_not_count(monkeypatch):
    # A COMMITTED.json at the unit root (or any non-generation path) is not a generation.
    keys = [f"{BASE}/{tv.COMMIT_MANIFEST}", f"{BASE}/notes.txt"]
    assert _progress(monkeypatch, keys) == (None, 0, 0)


def test_the_newest_manifested_generation_wins_when_several_exist(monkeypatch):
    keys = (_gen("production", 1680, "aaa", tv.COMMIT_MANIFEST)
            + _gen("production", 1720, "bbb", tv.COMMIT_MANIFEST)
            + _gen("production", 1760, "ccc", tv.COMMIT_MANIFEST))
    assert _progress(monkeypatch, keys)[1] == 1760
