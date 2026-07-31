"""THE RESTORE IS INSTRUMENTED AND BOUNDED — the 2026-07-31 5a-KS wedge.

THE DIAGNOSIS, from the artifacts and not from a story (CLAUDE.md §4). `vast_idle_guard` condemned two 5a-KS
legs as WEDGED at 1:38 PM ET: `run.log` re-uploaded byte-identical for 18 min, committed scalar frozen, GPU
at 0 %. `ternary-diag-5aks.json` supplied the discriminating observation — for `nr4a3_r0` the ARCHIVED attempt
and the LIVE `run.log` were both **exactly 5115 bytes** and both ended on the same line:

    [spot-driver] warmup_target=1600 (ci=64) prod_target=2000 (ci=40)

That line is printed immediately before `commit_store.restore_latest`, and the next thing a healthy leg
prints is a `[restore] ...` line from inside it. Neither wedged attempt printed one, on two different hosts.
So the process was ALIVE and hung between those two prints — inside the object store's LIST or its first GET.

The competing hypotheses die on the same evidence:
  * a write/IO failure — refuted: the log was reaching S3 the whole time; that is HOW we know it was frozen.
  * the GPU taken or throttled — refuted: nothing had reached openmmtools yet, so no MD had been attempted.
    An idle GPU is the CORRECT reading of a process downloading a checkpoint, which is exactly why the guard
    refuses to condemn on GPU idleness and condemns on write silence instead.
  * the MD process dying — refuted: a dead process stops the sync loop; this one kept re-uploading.

⚠ AND IT WAS NOT ARM-SPECIFIC, which the board made it look like. The board truncated the leg name to 18
characters and all four 5a-KS ids share a 20-character prefix, so every row read `5aks_d0_to_d terna`. The
committed `5aks-market-hold.json` snapshots say host losses ran 7 to 7 across `nr4a1` and `nr4a3`, and the two
condemned at 1:38 PM were `nr4a1_r1` and `nr4a3_r0` — one from EACH arm. See `test_board_leg_column.py`.
"""
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rbfe_spot_driver as drv  # noqa: E402


def test_the_deadline_fires_and_names_the_remedy():
    with pytest.raises(TimeoutError) as e:
        with drv._deadline(1, "hung in the object store; the checkpoint is intact and the gate re-places it"):
            time.sleep(3)
    # A timeout that does not say the durable state survived reads as data loss, and someone will hesitate
    # before letting the leg die — which is the behaviour being replaced.
    assert "intact" in str(e.value)


def test_the_deadline_is_transparent_when_nothing_hangs():
    with drv._deadline(30, "x"):
        out = 1 + 1
    assert out == 2


def test_a_zero_or_absent_deadline_does_not_bound_anything():
    """0 must mean OFF, not "expire immediately" — the difference between a disabled guard and one that kills
    every leg on the first restore."""
    for v in (0, None, -1):
        with drv._deadline(v, "x"):
            pass


def test_the_alarm_is_always_disarmed_even_on_an_exception():
    """A leaked SIGALRM would fire minutes later inside unrelated code — a wedge guard that manufactures a
    crash somewhere else is worse than no guard."""
    import signal
    with pytest.raises(ValueError):
        with drv._deadline(60, "x"):
            raise ValueError("boom")
    assert signal.alarm(0) == 0, "an alarm survived the context manager"


def test_the_driver_logs_BEFORE_the_restore_not_only_after():
    """The whole point: the wedge window had no output in it at all, so the log could not distinguish a hang
    in the LIST from a hang in the FETCH."""
    import inspect
    src = inspect.getsource(drv)
    assert "restore: trying" in src, "there must be a line printed BEFORE the object-store call"
    assert "_deadline(_restore_timeout_s" in src, "and the call must be bounded"
    assert "RBFE_RESTORE_TIMEOUT_S" in src, "and the bound must be overridable without an edit"
    # The `finally` is what makes the duration visible even when the call fails or times out.
    assert "restore: {label} took" in src


def test_the_commit_store_times_the_list_and_the_fetch_separately():
    import inspect

    import rbfe_spot_checkpoint as spot
    src = inspect.getsource(spot._BaseCommitStore.restore_latest)
    assert "list_committed returned" in src, "a hang in the LIST must be visible as one"
    assert "fetched" in src and "in {time.time() - _tf:.1f}s" in src, \
        "and a hang in the FETCH must be visible as a different one"
