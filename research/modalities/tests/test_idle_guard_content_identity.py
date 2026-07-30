"""The idle guard's wedge test must key on what the host WROTE, not on when a timer last uploaded.

Measured 2026-07-30. `run_ternary_leg.sh` syncs run.log from a background timer every ~120 s,
unconditionally, so `log_age_min` on this lane is pinned near 2 minutes forever and the 15-minute silence
clause is unreachable. Host 46286994 wedged inside a checkpoint persist — commit-store generation
fa5da1eb holds simulation.nc and nothing else, and `_persist` writes .nc then .chk then the manifest — and
then billed 77 minutes at gpu_util 0.0 while the guard reported "quiet but alive: run.log 2 min old" on
every poll.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import vast_idle_guard as vig  # noqa: E402

HEALTHY = dict(instance_running=True, container_started=True, instance_age_min=120.0,
               start_ages_min=[], progress_advanced=False, gpu_util=0.0)


def test_the_founding_case_a_timer_synced_log_no_longer_reads_as_alive():
    v, why = vig.classify_idle(**HEALTHY, log_age_min=2.0, log_unchanged_min=77.0)
    assert v == vig.WEDGED
    assert vig.should_destroy(v)
    assert "byte-identical" in why


def test_a_host_writing_new_content_is_never_condemned_by_this_clause():
    v, _ = vig.classify_idle(**HEALTHY, log_age_min=2.0, log_unchanged_min=1.0)
    assert v == vig.WATCHING
    assert not vig.should_destroy(v)


def test_content_frozen_but_still_under_the_threshold_is_left_alone():
    v, _ = vig.classify_idle(**HEALTHY, log_age_min=2.0,
                             log_unchanged_min=vig.LOG_SILENCE_MIN - 0.1)
    assert v == vig.WATCHING


def test_committed_progress_still_overrides_a_frozen_log():
    """The absolute override must stay absolute: a leg that commits between polls may well have written
    nothing NEW to the tail we hash (the tail is 60 lines and MD is quiet), and measured work wins."""
    v, why = vig.classify_idle(**{**HEALTHY, "progress_advanced": True},
                               log_age_min=2.0, log_unchanged_min=999.0)
    assert v == vig.WORKING
    assert "scalar advanced" in why


def test_the_cold_start_floor_still_protects_a_young_box():
    v, _ = vig.classify_idle(**{**HEALTHY, "instance_age_min": 5.0},
                             log_age_min=2.0, log_unchanged_min=999.0)
    assert v == vig.COLD_START


def test_a_dead_unit_still_gets_its_own_verdict_not_a_wedge_sentence():
    v, why = vig.classify_idle(**{**HEALTHY, "unit_failed": True},
                               log_age_min=2.0, log_unchanged_min=999.0)
    assert v == vig.UNIT_FAILED
    assert "status=failed" in why


def test_a_busy_gpu_does_not_rescue_a_frozen_log():
    """Deliberate: the GPU-busy reprieve sits BELOW the write-evidence clauses, because work computed by a
    host that is not writing is work that will be discarded at the next boundary anyway."""
    v, _ = vig.classify_idle(**{**HEALTHY, "gpu_util": 95.0},
                             log_age_min=2.0, log_unchanged_min=77.0)
    assert v == vig.WEDGED


def test_an_idle_gpu_alone_still_condemns_nothing():
    """The module's inviolable rule. No content-identity evidence at all -> no condemnation, whatever the
    GPU reads."""
    v, _ = vig.classify_idle(**HEALTHY, log_age_min=2.0, log_unchanged_min=None)
    assert v == vig.WATCHING
    assert not vig.should_destroy(v)


def test_untracked_content_identity_says_so_in_the_reason():
    # A guard that cannot see the signal must SAY it cannot, or "quiet but alive" reads as reassurance.
    _, why = vig.classify_idle(**HEALTHY, log_age_min=2.0, log_unchanged_min=None)
    assert "CONTENT IDENTITY NOT TRACKED" in why


def test_the_mtime_clause_still_fires_on_a_lane_that_does_not_timer_sync():
    # Not a replacement: a host that genuinely stops PUTting is still a wedge, and that clause runs first.
    v, why = vig.classify_idle(**HEALTHY, log_age_min=40.0, log_unchanged_min=1.0)
    assert v == vig.WEDGED
    assert "lost its write path" in why


def test_crash_loop_still_outranks_both_write_clauses():
    v, _ = vig.classify_idle(**{**HEALTHY, "start_ages_min": [1.0, 2.0, 3.0]},
                             log_age_min=2.0, log_unchanged_min=77.0)
    assert v == vig.CRASH_LOOP
