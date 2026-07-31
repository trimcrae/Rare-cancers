"""What `uptime_s` MEANS in `_price_ledger.json` — pinned, so the next reader cannot make the 2026-07-31 mistake.

THE MISTAKE THIS PREVENTS. The retrospective lane's ledger carried
`nrv04retro-retro_noncov_nr4a2-m1-r0: {"uptime_s": 561615, "cost_usd": 25.8273}` — 156.0 h and $25.83 — for a
leg whose own record says `prod_wall_s: 3730.5` (1.04 h). Read as "what the leg cost" that row is absurd and
invites the conclusion that the field is broken. It was not: `uptime_s` is `now - instance.start_date` taken
at whatever poll saw the instance, i.e. BILLED RENTAL TIME, and instance 45749905 really was alive for six and
a half days (rented 6:59 PM ET Fri Jul 24 2026, destroyed 6:59 AM ET Fri Jul 31 2026 at $0.16556/hr — run
30625438729, job 91139494243, log lines 10:59:45-46 UTC). The dollars were real; only the name misled.

So this file pins BOTH readings — what the field is, and what it is not — plus the two ways the old code let a
row lie in opposite directions:

  * OVER, for a reader: a leaked rental averaged into a per-leg mean (one row dragged an 18-row mean to
    $1.4763/leg while the 17 real rows were $0.01-$0.11).
  * UNDER, in the arithmetic: `final` latching on the mere existence of a `leg_*.json`, so re-renting a unit
    that already had a result froze its cost at minutes while the host billed on.

Pure functions only — no S3, no Vast, no network.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nrv04_vast_launch import (  # noqa: E402
    LEAK_ABOVE_S,
    _finalizable,
    ledger_entry_reading,
    leg_cost_usd,
)

# The real row, verbatim from s3://sagemaker-us-east-2-646605541856/nrv04-retro-results/_price_ledger.json
# as read 12:07 PM ET Fri Jul 31, 2026 (nrv04-retro-price-forensics.json).
ORPHAN_ROW = {"uptime_s": 561615, "dph_total": 0.16555555555555557, "cost_usd": 25.8273, "final": True}
ORPHAN_LEG_PROD_WALL_S = 3730.5          # the leg's own record: 1.04 h of production MD


def test_uptime_s_is_rental_time_not_leg_time():
    """THE ONE FACT. 561615 s is the HOST's billed life, not the leg's compute — they differ 150-fold."""
    assert round(ORPHAN_ROW["uptime_s"] / 3600.0, 1) == 156.0
    assert round(ORPHAN_ROW["uptime_s"] / ORPHAN_LEG_PROD_WALL_S, 1) == 150.5
    # And the cost really is that arithmetic against the rate the instance's own record showed at reap
    # ($0.16555555555555557/hr, logged verbatim by retro-reap), which is how we know the row was written at
    # the 10:59:45 UTC poll rather than fabricated.
    #
    # It reproduces to 0.0001 but not exactly, and the residual is itself evidence: `cost_usd` is computed
    # from the UNROUNDED age and `uptime_s` is stored `round()`ed, so recomputing off the stored integer
    # gives 25.8274 against the persisted 25.8273. The true age was a fraction under 561615 s.
    assert abs(leg_cost_usd(ORPHAN_ROW["uptime_s"], ORPHAN_ROW["dph_total"]) - ORPHAN_ROW["cost_usd"]) < 1e-3


def test_the_orphan_row_reads_as_a_leak_not_a_leg():
    r = ledger_entry_reading(ORPHAN_ROW)
    assert r["kind"] == "leak"
    assert r["hours"] == round(561615 / 3600.0, 4)
    assert "idle rental time" in r["why"]


def test_a_normal_leg_row_reads_as_a_leg():
    """One of the 17 sibling rows from the same ledger: 38 min at $0.18/hr."""
    r = ledger_entry_reading({"uptime_s": 2253, "dph_total": 0.1825, "cost_usd": 0.1142, "final": True})
    assert r["kind"] == "leg"


def test_leak_threshold_is_above_the_lanes_own_hang_guard():
    """The line must sit ABOVE any whole leg (MAX_LEG_MIN backstop is 240 min) or it flags healthy rentals."""
    assert LEAK_ABOVE_S > 240 * 60
    assert ledger_entry_reading({"uptime_s": LEAK_ABOVE_S, "cost_usd": 1.0})["kind"] == "leg"
    assert ledger_entry_reading({"uptime_s": LEAK_ABOVE_S + 1, "cost_usd": 1.0})["kind"] == "leak"


def test_a_row_with_no_uptime_is_unknown_not_zero():
    """No host observed must never render as a $0 leg — that is a silent under-count."""
    assert ledger_entry_reading({"cost_usd": None})["kind"] == "unknown"


def test_cost_is_never_fabricated_from_missing_inputs():
    assert leg_cost_usd(None, 0.24) is None
    assert leg_cost_usd(3600, None) is None


# ---- the UNDER-reporting half: `final` must not latch on somebody else's result ---------------------------

def test_final_does_not_latch_when_the_result_predates_this_rental():
    """A re-rent over an existing leg_*.json used to freeze the price at minutes while the host billed on."""
    start = 1_785_000_000.0
    stale = {"u": start - 86_400}                      # result written a day BEFORE we rented this host
    assert _finalizable("u", stale, start, stale) is False


def test_final_latches_when_this_rental_produced_the_result():
    start = 1_785_000_000.0
    fresh = {"u": start + 3_600}
    assert _finalizable("u", fresh, start, fresh) is True


def test_final_still_latches_when_no_mtimes_are_available():
    """Fail OPEN, not closed: without mtimes the ledger must still settle rather than never finalizing."""
    assert _finalizable("u", {"u"}, 1_785_000_000.0, None) is True


def test_not_done_is_never_final():
    assert _finalizable("u", {}, 1_785_000_000.0, {}) is False
