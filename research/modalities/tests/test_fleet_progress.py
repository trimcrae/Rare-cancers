"""Unit tests for the pure hang-classification logic in fleet_progress (no AWS)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fleet_progress as fp  # noqa: E402

NOW = 1_000_000_000_000.0  # arbitrary ms epoch


def test_training_fresh_event_is_alive():
    state, age = fp.classify("Training", NOW - 5 * 60000, NOW, stale_min=25, has_stream=True)
    assert state == "alive" and abs(age - 5) < 1e-6


def test_training_stale_event_flags_hang():
    state, age = fp.classify("Training", NOW - 40 * 60000, NOW, stale_min=25, has_stream=True)
    assert state == "STALE" and abs(age - 40) < 1e-6


def test_boundary_just_under_and_over():
    assert fp.classify("Training", NOW - 24 * 60000, NOW, 25, True)[0] == "alive"
    assert fp.classify("Training", NOW - 26 * 60000, NOW, 25, True)[0] == "STALE"


def test_starting_without_stream_is_provisioning_not_hang():
    # a spot-capacity-waiting job has no stream yet — must NOT be flagged as a hang
    state, age = fp.classify("Starting", None, NOW, stale_min=25, has_stream=False)
    assert state == "provisioning" and age is None


def test_downloading_without_stream_is_provisioning():
    assert fp.classify("Downloading", None, NOW, 25, False)[0] == "provisioning"


def test_stale_only_applies_to_training_not_stopping():
    # a job in a non-Training secondary state with an old event is 'other', not a hang flag
    state, _ = fp.classify("Stopping", NOW - 99 * 60000, NOW, 25, True)
    assert state == "other"
