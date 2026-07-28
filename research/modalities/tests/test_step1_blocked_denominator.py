"""A PERMANENTLY-EXCLUDED EDGE MUST RENDER AS ONE — not as done, not as still-failing, not as missing.

WHY THESE TESTS EXIST (2026-07-28). The step 1 fan-out had one edge it can never compute
(`cw_bio_nmethyl_amide`: no available mapper reaches the provable atom-map floor). The block itself worked
— no host was rented for it — but every readout the lane produces described it wrongly, in three different
directions at once:

  * `mode_launch` printed `units=19 done=10 pending=9`. `done` was `len(units) - len(pending)`, and
    `_pending` filters out finished AND blocked units, so the blocked edge was counted as COMPLETE. Nine
    ddG results and "done=10" sat in the same artifact.
  * the committed census read `phase.txt` directly, so the blocked edge wore `leg-complex-FAILED-rc1`
    forever — character for character the string a unit wears while it is about to be re-placed.
  * `step1_terminus_evidence` printed it as `NO-TERMINUS / no commits`, which is exactly what a unit that
    has never been placed prints.

CLAUDE.md §6 names the failure mode directly ("it does not silently drop units"), and §1 asks for one home
per fact. So the three states — DONE, BLOCKED, OUTSTANDING — are counted by one pure function, rendered by
one pure function, and the honest denominator is derived from the block map rather than typed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import congeneric_fanout_vast as cfv  # noqa: E402

U = [{"unit_id": "u_done"}, {"unit_id": "u_blocked"}, {"unit_id": "u_running"}, {"unit_id": "u_cold"}]
BLK = {"u_blocked": {"why": "no mapper reaches the provable floor", "evidence": "step1-map-diag.json"}}


# ---- counts -----------------------------------------------------------------------------------
def test_a_blocked_unit_is_not_counted_as_done():
    """THE DEFECT THIS PINS, in one assertion. `len(units) - len(pending)` returned 3 here."""
    done, blocked, outstanding = cfv.counts(U, {"u_done"}, BLK)
    assert (done, blocked, outstanding) == (1, 1, 2)


def test_the_three_counts_always_partition_the_map():
    for done_ids in ({"u_done"}, set(), {"u_done", "u_blocked", "u_running", "u_cold"}):
        d, b, o = cfv.counts(U, done_ids, BLK)
        assert d + b + o == len(U)
        assert min(d, b, o) >= 0


def test_a_blocked_unit_that_nevertheless_has_a_result_counts_as_done():
    """A result in hand is a result whatever list the unit is on — and it must not be double-counted."""
    d, b, o = cfv.counts(U, {"u_done", "u_blocked"}, BLK)
    assert (d, b, o) == (2, 0, 2)


def test_no_blocks_leaves_the_old_arithmetic_untouched():
    d, b, o = cfv.counts(U, {"u_done"}, {})
    assert (d, b, o) == (1, 0, 3)


# ---- the denominator --------------------------------------------------------------------------
def test_computable_is_the_map_minus_its_permanent_exclusions():
    got = [u["unit_id"] for u in cfv.computable_units(U, BLK)]
    assert got == ["u_done", "u_running", "u_cold"]


def test_computable_is_derived_from_the_block_map_not_a_constant():
    """Adding a block must move the denominator with no edit anywhere else — the whole point of deriving
    it. A typed '18' is the copy that goes stale the first time a block is added or lifted."""
    assert len(cfv.computable_units(U, {})) == 4
    assert len(cfv.computable_units(U, {"u_cold": {"why": "x"}, **BLK})) == 2


# ---- the renderer -----------------------------------------------------------------------------
def test_a_blocked_unit_does_not_wear_its_last_failure_marker():
    p = cfv.unit_phase({"unit_id": "u_blocked"}, BLK, has_result=False,
                       phase_txt="leg-complex-FAILED-rc1 2026-07-27T13:12:21Z")
    assert p == cfv.BLOCKED_PHASE
    assert "FAILED" not in p


def test_a_result_outranks_a_block():
    assert cfv.unit_phase({"unit_id": "u_blocked"}, BLK, has_result=True, phase_txt="whatever") == "done"


def test_an_unblocked_unit_still_shows_its_real_phase():
    assert cfv.unit_phase({"unit_id": "u_running"}, BLK, has_result=False,
                          phase_txt="leg-complex-running 2026-07-28T09:15:16Z").startswith(
        "leg-complex-running")


def test_a_never_placed_unit_is_not_started_and_not_blocked():
    assert cfv.unit_phase({"unit_id": "u_cold"}, BLK, has_result=False, phase_txt=None) == "not-started"


def test_the_blocked_phase_string_is_not_mistakable_for_a_phase_marker():
    """Every real marker this lane writes starts with one of these; the blocked sentinel must not, or the
    histogram buckets an excluded edge alongside a live one again."""
    assert not cfv.BLOCKED_PHASE.startswith(("leg-", "boot", "staged", "reduce", "done"))
    assert "BLOCKED" in cfv.BLOCKED_PHASE


# ---- the readouts actually use them -----------------------------------------------------------
def _src(name):
    return open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), name)).read()


def test_the_launcher_reports_blocked_separately_from_done():
    s = _src("congeneric_fanout_vast.py")
    assert "done = len(units) - len(pending)" not in s, "the subtraction that counted a block as done"
    assert "computable={len(computable)}" in s and "blocked={n_blocked}" in s


def test_the_committed_census_carries_the_denominator_and_the_reason():
    s = _src("congeneric_fanout_vast.py")
    for field in ('"n_computable"', '"n_blocked"', '"blocked_units"', '"blocked_why"'):
        assert field in s, f"{field} missing from the progress snapshot"


def test_the_terminus_readout_separates_EXCLUDED_from_NO_TERMINUS():
    s = _src("step1_terminus_evidence.py")
    assert '"EXCLUDED"' in s
    # ...and the release size it prices excludes them, or the lane prices a purchase it cannot make.
    assert "u not in blocked" in s


def test_the_terminus_readout_does_not_type_its_own_denominator():
    """'the 18-edge release' was a string literal here. It is right today and wrong the moment a block is
    added or lifted, which is the drift rule 1 exists to stop."""
    s = _src("step1_terminus_evidence.py")
    assert "18-edge" not in s
    assert "n_computable" in s
