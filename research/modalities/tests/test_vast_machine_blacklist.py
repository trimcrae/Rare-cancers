#!/usr/bin/env python3
"""The shared Vast machine-exclusion set: what may go in it, and how it is emptied.

A wrong permanent entry is an unrecoverable capacity loss that compounds across lanes, while re-discovering
a genuinely bad host is nearly free — a failed SUBMIT costs no rental and no billing. These tests pin that
asymmetry into the module.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vast_machine_blacklist as vmb  # noqa: E402



# ============================================================================================================
# "Clear it out, and don't add anything back unless you have a real reason" (trimcrae, 2026-07-27).
#
# The set had grown to 48 permanent entries and blocked 2 of 2 authorised placements against a 189-offer
# board where price was fine. The cause was storing a MOMENT as if it were a property of the host.
# ============================================================================================================
def test_a_capacity_refusal_is_classified_as_perishable():
    for why in ("resources_unavailable on start (instance 46056372, RTX 5090)",
                "machine has no free GPU",
                "CAPACITY refusal"):
        assert vmb.classify_reason(why) == vmb.CLASS_CAPACITY, why


def test_a_container_failure_is_classified_as_durable():
    for why in ("container never started", "image pull failed", "crash-loop on start",
                "CUDA_ERROR_UNSUPPORTED_PTX_VERSION"):
        assert vmb.classify_reason(why) == vmb.CLASS_HOST, why


def test_capacity_is_checked_before_the_never_started_markers():
    # `resources_unavailable` matches NEVER_STARTED_MARKERS too. If that were checked first, the perishable
    # class would be filed as durable — which is exactly how the set grew.
    why = "resources_unavailable on start"
    assert vmb.is_never_started_reason(why) is True      # still true, and still used by withdraw()
    assert vmb.classify_reason(why) == vmb.CLASS_CAPACITY


class _FakeS3:
    def __init__(self, objs=None):
        self.objs = dict(objs or {})

    def get_object(self, Bucket, Key):
        if Key not in self.objs:
            raise KeyError(Key)
        return {"Body": io.BytesIO(self.objs[Key].encode())}

    def put_object(self, Bucket, Key, Body):
        self.objs[Key] = Body.decode()


def test_publish_REFUSES_a_capacity_reason():
    s3 = _FakeS3()
    assert vmb.publish(s3, "b", "12345", "resources_unavailable on start", "ternary") is False
    ids, _ = vmb.load(s3, "b")
    assert ids == []


def test_publish_still_accepts_a_real_host_reason():
    s3 = _FakeS3()
    assert vmb.publish(s3, "b", "12345", "container never started", "ternary") is True
    ids, doc = vmb.load(s3, "b")
    assert ids == ["12345"]
    assert doc["history"][-1]["reason_class"] == vmb.CLASS_HOST


def test_clear_all_empties_the_set_but_keeps_the_history():
    s3 = _FakeS3()
    vmb.publish(s3, "b", "1", "container never started", "ternary")
    vmb.publish(s3, "b", "2", "crash-loop on start", "step1")
    removed = vmb.clear_all(s3, "b", "trimcrae 2026-07-27: too strict, blocking placements")
    assert sorted(removed) == ["1", "2"]
    ids, doc = vmb.load(s3, "b")
    assert ids == []
    # The clear is an EVENT in the record, not a gap.
    assert doc["history"][-1]["reason_class"] == "clear"
    assert sorted(doc["history"][-1]["cleared_machine_ids"]) == ["1", "2"]


def test_snapshot_captures_everything_needed_to_reconstruct():
    s3 = _FakeS3()
    vmb.publish(s3, "b", "1", "container never started", "ternary")
    snap = vmb.snapshot(s3, "b")
    assert snap["n_machine_ids"] == 1 and snap["machine_ids"] == ["1"]
    assert snap["history"] and snap["history_entries_by_reason_class"]


def test_clearing_only_the_shared_set_is_not_enough():
    # blocked_machine_ids() unions lane-local with shared, so a lane keeps excluding until its own list goes.
    s3 = _FakeS3({"pfx/_lane_state.json": json.dumps({"_blocked_machines": ["7", "8"]})})
    removed = vmb.clear_lane_state(s3, "b", "pfx/_lane_state.json")
    assert sorted(removed) == ["7", "8"]
    assert json.loads(s3.objs["pfx/_lane_state.json"])["_blocked_machines"] == []


def test_clear_refuses_without_a_snapshot():
    assert vmb.main(["--clear", "because"]) == 2


def test_the_create_start_race_verdict_is_perishable_because_it_has_been_wrong():
    """53989, 31035 and 24573 were condemned on exactly this wording and every one had run our container at
    94-99 % GPU. A verdict that has demonstrably flipped must not create a permanent entry."""
    why = ("never started: cur_state=stopped with an empty status_msg for 53 min across 2 consecutive "
           "checks (create/start race, not an image pull)")
    assert vmb.classify_reason(why) == vmb.CLASS_CAPACITY
    s3 = _FakeS3()
    assert vmb.publish(s3, "b", "53989", why, "step1_fanout") is False
