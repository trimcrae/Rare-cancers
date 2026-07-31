"""A shakeout's evidence expires; a real result's never does — and a landed unit is not disarmed
while its host is still up.

WHAT THIS PINS, and why it is worth a file of its own. On 2026-07-31 `task=5aks-smoke` was dispatched to
shake out the 5a-KS pipeline before the four real legs were bought. It rented nothing and reported green,
because the smoke unit's `leg.json` had been `status=done` in S3 since 2026-07-26 — so `outstanding_units`
put it in `done`, the gate answered `nothing-to-launch`, and the ladder step that exists to catch a broken
image or a rotated credential measured nothing at all while printing `[verify-armed] … all 1 unit(s)
present and enabled`. The same morning NR-V04's pilot printed `[skip] … result already in S3`.

The two halves below have to hold TOGETHER. Expiring a shakeout's certificate without the watchdog guard
would turn a silent no-op into a silent UNWATCHED RENTAL: the entry is armed by the launch, and the very
next `reap_landed` pass would read the stale `done` record and set `enabled=false` under a billing host.
"""
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_vast_launch as tv  # noqa: E402
import ternary_vast_watchdog as tvw  # noqa: E402


def _stamp(hours_ago):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - hours_ago * 3600))


# ---------------------------------------------------------------------------------------------------------
# which modes are shakeouts at all
# ---------------------------------------------------------------------------------------------------------

def test_every_smoke_mode_is_flagged_a_shakeout():
    """A mode whose name says smoke but which is not flagged would keep the old, silent behaviour."""
    for mode in tv.MODES:
        if mode.endswith("smoke"):
            assert tv.is_shakeout(mode), f"{mode} looks like a shakeout but carries no shakeout flag"


def test_no_science_mode_is_a_shakeout():
    """The blast radius. If a production mode were ever flagged, this rule would expire a REAL result and
    the lane would re-buy landed work — the exact harm CLAUDE.md §7 records as costing a day."""
    for mode in ("probe", "edge", "edge_reps", "5aks", "triangle"):
        assert not tv.is_shakeout(mode), f"{mode} is a science mode and must never expire its result"


# ---------------------------------------------------------------------------------------------------------
# the shelf life itself
# ---------------------------------------------------------------------------------------------------------

def test_a_fresh_shakeout_record_is_not_stale():
    assert not tv.shakeout_evidence_is_stale({"_s3_last_modified": _stamp(0.5)})


def test_the_five_day_old_record_that_caused_this_is_stale():
    """The measured case: 2026-07-26 evidence standing in front of a 2026-07-31 spend."""
    assert tv.shakeout_evidence_is_stale({"_s3_last_modified": _stamp(24 * 5)})


def test_the_boundary_is_the_named_constant_and_not_a_second_copy_of_it():
    just_inside = tv.SHAKEOUT_EVIDENCE_MAX_AGE_H - 0.1
    just_outside = tv.SHAKEOUT_EVIDENCE_MAX_AGE_H + 0.1
    assert not tv.shakeout_evidence_is_stale({"_s3_last_modified": _stamp(just_inside)})
    assert tv.shakeout_evidence_is_stale({"_s3_last_modified": _stamp(just_outside)})


@pytest.mark.parametrize("rec", [{}, {"_s3_last_modified": None}, {"_s3_last_modified": "not-a-date"}])
def test_an_undatable_record_is_treated_as_stale(rec):
    """Cheap side, safe side: being wrong here re-runs a ~$0.15 shakeout, while being wrong the other way
    is the silent no-op this whole file is about."""
    assert tv.shakeout_evidence_is_stale(rec)


# ---------------------------------------------------------------------------------------------------------
# the watchdog half — the guard that makes the shelf life safe rather than dangerous
# ---------------------------------------------------------------------------------------------------------

def _watch_doc(uid):
    return {"watch": [{"unit_id": uid, "leg_id": "l", "seed": 0, "direction": "fwd", "mode": "5aks_smoke",
                       "timestep_fs": "4.0", "warmup_timestep_fs": "1.0", "git_branch": "main",
                       "max_relaunches_per_day": 8, "enabled": True}]}


def test_a_landed_unit_with_no_host_is_still_reaped(tmp_path, monkeypatch):
    """The ordinary path must keep working — this guard is a narrowing, not a disabling."""
    uid = "u1"
    p = tmp_path / "watch.json"
    tvw.save_watch(_watch_doc(uid), str(p))
    reaped = tvw.reap_landed(path=str(p), recs={uid: {"status": "done"}}, live_uids=set())
    assert reaped == [uid]
    assert tvw.load_watch(str(p))["watch"][0]["enabled"] is False


def test_a_landed_unit_whose_host_is_still_up_is_NOT_disarmed(tmp_path):
    """The regression that making a shakeout re-runnable would otherwise have introduced: an armed, billing
    host silently dropped off the only list the watchdog reads."""
    uid = "u1"
    p = tmp_path / "watch.json"
    tvw.save_watch(_watch_doc(uid), str(p))
    reaped = tvw.reap_landed(path=str(p), recs={uid: {"status": "done"}}, live_uids={uid})
    assert reaped == []
    assert tvw.load_watch(str(p))["watch"][0]["enabled"] is True


def test_an_unreadable_instance_list_reaps_nothing(tmp_path, monkeypatch):
    """No evidence is never a licence to act — same discipline as the unreadable leg-record branch."""
    uid = "u1"
    p = tmp_path / "watch.json"
    tvw.save_watch(_watch_doc(uid), str(p))

    def _boom(*a, **k):
        raise RuntimeError("vast api 503")

    monkeypatch.setattr(tvw.tv, "unit_hosts", _boom)
    reaped = tvw.reap_landed(path=str(p), recs={uid: {"status": "done"}})
    assert reaped == []
    assert tvw.load_watch(str(p))["watch"][0]["enabled"] is True
