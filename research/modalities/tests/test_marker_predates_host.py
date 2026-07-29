#!/usr/bin/env python3
"""A phase marker left by the PREVIOUS attempt must not render as this host's current phase.

WHAT THIS CAUGHT (2026-07-29, 11:37 AM ET). The closure triangle's `calib_lo_to_lo2__ternary_vhl` had been
rented two minutes earlier and was still pulling its image. `task=collect` printed, for that host:

    phase: done 2026-07-28T10:39:56Z  (marker 1737 min old, log 1737.0 min old)
    | Traceback (most recent call last):

Both lines are real and both belong to YESTERDAY — the partial-charge death that killed this unit 21 times.
The phase marker and `run.log` are written to a per-UNIT key (`{prefix}/legs/{uid}/...`), never a per-attempt
one, so a fresh host inherits its predecessor's until it writes its own. The row therefore said "done" and
showed a traceback about a leg that had produced nothing at all, in the one readout an operator uses to decide
whether a lane is progressing. Read at a glance it is a finished leg; read at second glance it is a leg that
has already crashed again. It was neither.

⚠ THE CONTROL PATH WAS CHECKED AND IS NOT AFFECTED — measured, not assumed, and recorded here so nobody
"fixes" it twice. `reap_landed` keys on a `status == "done"` leg.json (this unit had no record at all, its
failed one having been archived by `--supersede-failed`); the crash/reap clause is already guarded by
`_record_is_newer_than_instance`; the frozen clause keys on the Vast status message tracked across polls, not
on marker age; and the idle guard abstained on its own. So the defect is confined to what the row SAYS.

That is still worth a test, for the reason CLAUDE.md §1 gives: the cheapest way for a stale fact to become a
wrong decision is for it to render as a current one. The same lesson already has a home on the launch side —
`_record_is_newer_than_instance` exists because a stale `failed` record would otherwise reap a freshly
launched host — and this is that comparison applied to the marker.

FAILING TOWARDS "NOT STALE" IS DELIBERATE. Every unknown returns False. A spurious ⚠ on a genuinely current
marker would teach the reader to ignore the flag, which is precisely the alarm-fatigue mode `reap_landed` was
written to end.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ternary_vast_launch import marker_predates_host    # noqa: E402


def test_the_incident_itself():
    """1737-minute marker on a host that has been up 0.03 h (~2 min)."""
    assert marker_predates_host(1737.0, 0.03) is True


def test_a_marker_this_host_wrote_is_not_stale():
    """The healthy case: host up 8.4 min, marker 6 min old — written by this attempt."""
    assert marker_predates_host(6.0, 0.14) is False


def test_a_marker_exactly_as_old_as_the_host_is_not_flagged():
    """Boundary. Equality means it could have been written at the instant the host came up, so it is ours."""
    assert marker_predates_host(60.0, 1.0) is False


def test_a_long_lived_host_with_an_old_marker_is_not_flagged():
    """A leg that has run for hours legitimately has an hours-old marker between checkpoint writes.

    This is the case that makes the comparison RELATIVE rather than an absolute age threshold: a fixed
    "marker older than N minutes is stale" rule would fire on every healthy long leg, which is why one is
    not used.
    """
    assert marker_predates_host(90.0, 6.0) is False


def test_unknowns_never_flag():
    assert marker_predates_host(None, 0.03) is False
    assert marker_predates_host(1737.0, None) is False
    assert marker_predates_host(None, None) is False


def test_a_zero_or_negative_uptime_never_flags():
    """`up_h` is 0.0 when the instance carries no usable `start_date`. Unknown is not evidence of staleness."""
    assert marker_predates_host(1737.0, 0.0) is False
    assert marker_predates_host(1737.0, -1.0) is False


def test_unparseable_inputs_never_raise():
    """This runs inside the collect print path; an exception here would break the monitoring it serves."""
    assert marker_predates_host("not-a-number", 0.03) is False
    assert marker_predates_host(1737.0, "not-a-number") is False


def test_the_collect_row_actually_consults_it():
    """Pin the call site. A pure helper nothing calls would pass every test above and fix nothing."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ternary_vast_launch.py")
    with open(path) as fh:
        src = fh.read()
    assert src.count("marker_predates_host(") >= 2, (
        "marker_predates_host is defined but not called from the collect row — the readout would still "
        "print a previous attempt's phase as though it were this host's."
    )
    assert "PREVIOUS ATTEMPT'S MARKER" in src, (
        "the stale-marker branch no longer names what it is telling the reader"
    )
