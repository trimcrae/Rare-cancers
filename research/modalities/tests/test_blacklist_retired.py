"""THE DURABLE MACHINE-EXCLUSION LIST IS RETIRED — pinned so it cannot come back by accident.

trimcrae, 2026-07-31: *"You've gotta just stop doing the blacklist. It seems like it only ever bites us in
the ass and clearing it always makes things better."*

THE EVIDENCE BEHIND THE DECISION (recorded here as well as in `vast_machine_blacklist`, because a test that
only asserts a behaviour teaches nobody why): the cumulative version reached 33 lane-local + 41 shared
entries and made OUR OWN FILTER, not price, the binding constraint on placement — 2 of 2 authorised units
failed with `no rentable verified offer` against a 189-offer board at healthy prices;
`vast-blacklist-snapshot-before-clear.json` captured 41 ids immediately before the 2026-07-28 wipe; every
clear on record improved placement.

⚠ THE HALF OF THIS THAT MATTERS MOST IS THE SECOND HALF. Two bounded protections are NOT the blacklist and
removing them would cause real harm, so they are pinned here too:
  * `used_machines` — do not put two legs of one wave on the same box (double-rent prevention).
  * `gpu_backend.submit`'s IN-CALL skip — after a `resources_unavailable`, do not immediately re-offer the
    machine that just refused, inside that same placement call. Bounded to the call, dies with it.
"""
import io
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vast_machine_blacklist as vmb  # noqa: E402


class _FakeS3:
    def __init__(self, docs=None):
        self.docs = dict(docs or {})
        self.puts = []

    def get_object(self, Bucket=None, Key=None):  # noqa: N803
        if Key not in self.docs:
            raise KeyError(Key)
        return {"Body": io.BytesIO(json.dumps(self.docs[Key]).encode())}

    def put_object(self, Bucket=None, Key=None, Body=None):  # noqa: N803
        self.puts.append(Key)
        self.docs[Key] = json.loads(Body.decode())


# =============================================================================================================
# the switch itself
# =============================================================================================================
def test_the_default_is_OFF_and_it_is_read_at_call_time(monkeypatch):
    monkeypatch.delenv("VAST_DURABLE_EXCLUSIONS", raising=False)
    assert vmb.DURABLE_EXCLUSIONS_ENABLED is False
    assert vmb.durable_enabled() is False
    # Call-time, not import-time: the tests that pin the retired machinery flip it with an env var and must
    # not have to reload half the package to do so.
    monkeypatch.setenv("VAST_DURABLE_EXCLUSIONS", "1")
    assert vmb.durable_enabled() is True


def test_a_stored_shared_set_is_NOT_read_for_selection(monkeypatch):
    monkeypatch.delenv("VAST_DURABLE_EXCLUSIONS", raising=False)
    s3 = _FakeS3({vmb.SHARED_KEY: {"machine_ids": ["11", "22", "33"]}})
    assert vmb.load(s3, "b") == ([], {}), "a retired list must return nothing to a selection caller"
    assert vmb.union(["44"], s3, "b") == [], \
        "union is the funnel BOTH durable homes pass through — it must drop the caller's own ids too"


def test_the_stored_artifact_stays_READABLE_for_reporting():
    """Retired is not deleted. `snapshot`, the exclusion census and the operator commands must still see the
    object, or the historical record becomes unrecoverable and the change stops being reversible."""
    s3 = _FakeS3({vmb.SHARED_KEY: {"machine_ids": ["11", "22"]}})
    ids, doc = vmb.load(s3, "b", force=True)
    assert ids == ["11", "22"] and doc["machine_ids"] == ["11", "22"]


def test_publish_writes_NOTHING_while_retired(monkeypatch):
    """A read path that returns nothing while the write path keeps growing the object is the worst of both:
    the starvation would return silently the moment anyone flipped the switch back, inheriting a set nobody
    reviewed."""
    monkeypatch.delenv("VAST_DURABLE_EXCLUSIONS", raising=False)
    s3 = _FakeS3()
    assert vmb.publish(s3, "b", "99", "container never executed on this host", lane="x") is False
    assert s3.puts == [], "no write may reach the retired set"


# =============================================================================================================
# every lane's read path
# =============================================================================================================
def test_ternary_lane_reads_no_durable_exclusions(monkeypatch):
    monkeypatch.delenv("VAST_DURABLE_EXCLUSIONS", raising=False)
    import ternary_vast_launch as tv

    def _boom():
        raise AssertionError("the retired list must be refused BEFORE any S3 client is built")

    monkeypatch.setattr(tv, "_s3", _boom)
    assert tv.blocked_machine_ids() == []


def test_protfep_lane_reads_no_durable_exclusions(monkeypatch):
    monkeypatch.delenv("VAST_DURABLE_EXCLUSIONS", raising=False)
    import protfep_vast_launch as pv
    assert pv.blocked_machine_ids() == []


def test_fanout_drops_the_stored_ids_and_the_wave_block_but_keeps_the_operator_hatch(monkeypatch):
    """`FANOUT_EXCLUDE_MACHINES` is an explicit per-dispatch operator input that nothing persists and nothing
    re-reads, so it is not the thing being retired and must survive."""
    monkeypatch.delenv("VAST_DURABLE_EXCLUSIONS", raising=False)
    import congeneric_fanout_vast as cfv
    doc = {"machine_ids": ["11", "22"],
           "capacity_wave": {"wave": cfv._wave_id(), "machine_ids": ["33"]}}
    s3 = _FakeS3({cfv._EXCLUDE_KEY: doc})
    monkeypatch.delenv("FANOUT_EXCLUDE_MACHINES", raising=False)
    ids, got = cfv._load_excluded(s3, "b")
    assert ids == [], "neither the durable ids nor the wave block may reach selection"
    assert got.get("machine_ids") == ["11", "22"], "the doc itself must still be returned for reporting"
    monkeypatch.setenv("FANOUT_EXCLUDE_MACHINES", "777, 888")
    ids, _ = cfv._load_excluded(s3, "b")
    assert ids == ["777", "888"]


def test_fanout_records_no_new_exclusion(monkeypatch):
    monkeypatch.delenv("VAST_DURABLE_EXCLUSIONS", raising=False)
    import congeneric_fanout_vast as cfv
    s3 = _FakeS3()
    assert cfv._record_exclusion(s3, "b", "55", "resources_unavailable on start") is False
    assert s3.puts == []


def test_flipping_the_switch_back_restores_the_old_behaviour_exactly(monkeypatch):
    """The retirement must be REVERSIBLE without archaeology — that is the whole reason it is a switch at the
    read path rather than a deletion."""
    monkeypatch.setenv("VAST_DURABLE_EXCLUSIONS", "1")
    s3 = _FakeS3({vmb.SHARED_KEY: {"machine_ids": ["11", "22"]}})
    assert vmb.load(s3, "b")[0] == ["11", "22"]
    assert vmb.union(["44"], s3, "b") == ["11", "22", "44"]


# =============================================================================================================
# ⚠ THE BOUNDED PROTECTIONS THAT ARE **NOT** THE BLACKLIST — these must survive
# =============================================================================================================
def test_the_in_call_capacity_skip_survives():
    """CLAUDE.md §6's "a host that never starts has infinite realised $/ns" is REAL, and this is what serves
    it: inside ONE placement call, a machine that answered `resources_unavailable` is excluded from the
    re-selection. Bounded to the call and dies with it — which is exactly why it does not starve the board."""
    import inspect

    import gpu_backend as gb
    src = inspect.getsource(gb.VastBackend.submit)
    assert "exclude_machine_ids=tuple(sorted(set(map(str, res.exclude_machine_ids)) |" in src, \
        "the in-call refusal skip is the bounded protection the durable list was NOT needed for"
    assert "dataclasses.replace(" in src, "and it must widen a COPY, never the caller's shared spec"


@pytest.mark.parametrize("mod,needle", [
    ("congeneric_fanout_vast", "exclude_machine_ids=used_machines"),
    ("protfep_vast_launch", "RES.exclude_machine_ids = tuple(used_machines)"),
    ("ternary_vast_launch", "j.resources.exclude_machine_ids = tuple(used)"),
])
def test_used_machines_double_rent_prevention_survives(mod, needle):
    """Not exclusion — DOUBLE-RENT prevention. Offers are per GPU slot, so selection will happily put several
    legs of one wave on the same machine, and a host advertising slots it cannot schedule accepts every
    rental and refuses every start (machine 53989 took two legs of one fleet, 2026-07-25)."""
    import importlib
    import inspect
    assert needle in inspect.getsource(importlib.import_module(mod))
