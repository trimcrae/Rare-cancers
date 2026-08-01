"""A FRAME THAT READS IS NOT A FRAME THAT WAS WRITTEN.

MEASURED, not theorised (2026-08-01, GH runs 30675511441 and 30675795333). Asked for a checkpoint frame that DOES NOT EXIST,
openmmtools raises nothing and returns no fill: it hands back an UNMASKED array of ZEROS. Every check
`validate_reporter_pair` made then succeeded — `read_last_iteration(last_checkpoint=True)` is arithmetic on
the ANALYSIS file and never consults the checkpoint, `read_sampler_states` returned the right NUMBER of
replicas at the right shape, `read_energies` returned an array, the counts agreed. TWO deliberately-broken
checkpoints (one with the frame at the wrong index, one with no frame written anywhere) both measured
`max |coordinate| = 0.0`, mask False, and both passed the function unchanged. Resuming from one would start
every replica with all atoms at the origin.

That is a gap well beyond the pruning work that found it: `commit()`'s entire safety argument is "the pair is
VALIDATED before it is persisted", and `restore_latest`'s is "a bad generation is rejected and we fall back".
Both were resting on readability rather than content.

`positions_are_unusable` closes it. What is pinned here is the property that makes it safe to put in a live
commit path: it must reject an unusable frame, and it must be INCAPABLE of rejecting a genuine one. Both
clauses are built so a false REJECT is impossible rather than unlikely: the magnitude sentinel sits ~30
orders of magnitude above anything physical, and the degeneracy clause fires only when EVERY atom of a
>1-atom system is at the same point, which no real configuration can be.
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rbfe_spot_checkpoint as spot  # noqa: E402

NETCDF4_F4_FILL = 9.9692099683868690e+36


# ---------------------------------------------------------------------------------------------
# it must catch the thing that was actually observed
# ---------------------------------------------------------------------------------------------
def test_the_netcdf_fill_value_itself_is_caught():
    assert spot.positions_are_unusable(np.full((22, 3), NETCDF4_F4_FILL, dtype="f4"))


def test_one_bad_atom_among_thousands_is_enough():
    """A partially-written chunk is the realistic corruption, not an all-fill one."""
    a = np.zeros((147788, 3), dtype="f4")
    a[99_999, 1] = NETCDF4_F4_FILL
    assert spot.positions_are_unusable(a)


def test_a_masked_array_is_caught_even_when_the_data_underneath_looks_fine():
    """netCDF4 auto-masks unwritten regions; the DATA beneath a mask is meaningless, so the mask alone
    condemns the frame."""
    a = np.ma.masked_array(np.zeros((10, 3)), mask=np.zeros((10, 3), dtype=bool))
    a.mask[3, 0] = True
    assert spot.positions_are_unusable(a)


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_non_finite_coordinates_are_caught(bad):
    a = np.zeros((10, 3))
    a[0, 0] = bad
    assert spot.positions_are_unusable(a)


def test_absent_and_empty_are_caught_rather_than_passing_by_default():
    """§4: an absent reading is not a reading of absence. No positions is not a valid frame."""
    assert spot.positions_are_unusable(None)
    assert spot.positions_are_unusable(np.zeros((0, 3)))


# ---------------------------------------------------------------------------------------------
# ...and it must be INCAPABLE of rejecting a real frame — this is what makes it safe to ship
# ---------------------------------------------------------------------------------------------
def test_an_ordinary_solvated_box_passes():
    rng = np.random.default_rng(0)
    assert not spot.positions_are_unusable(rng.uniform(-12.0, 12.0, size=(147788, 3)))


def test_a_frame_that_merely_CONTAINS_the_origin_passes():
    """One atom at (0,0,0) inside a real configuration is ordinary. Only a frame where EVERY atom sits at
    the same point is impossible — the distinction the degenerate-extent clause draws."""
    rng = np.random.default_rng(1)
    a = rng.uniform(-3.0, 3.0, size=(500, 3))
    a[7] = 0.0
    assert not spot.positions_are_unusable(a)


def test_a_wildly_unwrapped_coordinate_still_passes():
    """A diffusing molecule under unwrapped coordinates can drift far; 1000 nm is already absurd and must
    still be accepted, because a false REJECT would refuse a real commit."""
    a = np.zeros((10, 3))
    a[0, 0] = 1.0e3
    assert not spot.positions_are_unusable(a)


def test_the_sentinel_sits_far_from_both_ends():
    """The threshold is not a tuned number: it is orders of magnitude from anything real AND from the fill
    value, so no plausible drift in either direction changes a verdict."""
    assert spot.FILL_MAGNITUDE_NM / 1.0e3 >= 1.0e3, "at least 1e3x headroom above absurd-but-real"
    assert NETCDF4_F4_FILL / spot.FILL_MAGNITUDE_NM >= 1.0e20, "at least 1e20x below the fill value"


def test_float32_precision_does_not_flip_the_magnitude_verdict():
    """Just under the sentinel, in f4, and NOT spatially degenerate — otherwise this would be testing the
    degeneracy clause rather than the magnitude one."""
    a = np.full((10, 3), spot.FILL_MAGNITUDE_NM / 10.0, dtype="f4")
    a[0, 0] += 1.0
    assert not spot.positions_are_unusable(a)


# ---------------------------------------------------------------------------------------------
# the wiring: the check is actually consulted by the validator
# ---------------------------------------------------------------------------------------------
def test_validate_reporter_pair_consults_the_guard():
    """Source-text pin: the netCDF/openmmtools half cannot run in the sandbox, and a guard nobody calls is
    the failure mode this whole test file exists because of."""
    src = open(spot.__file__).read()
    body = src[src.index("def validate_reporter_pair"):src.index("def read_checkpoint_interval")]
    assert "positions_are_unusable(_positions_array(" in body


def test_the_guard_runs_on_every_replica_not_just_the_first():
    src = open(spot.__file__).read()
    body = src[src.index("def validate_reporter_pair"):src.index("def read_checkpoint_interval")]
    assert "for _i, _st in enumerate(sstates)" in body


# ---------------------------------------------------------------------------------------------
# ★★ THE ZEROS SIGNATURE — the one that was actually measured, and the one a magnitude test
#    can never see, because zeros look like perfectly ordinary small coordinates.
# ---------------------------------------------------------------------------------------------
def test_an_all_zero_frame_is_rejected():
    """MEASURED (GH 30675795333): asked for a checkpoint frame that does not exist, openmmtools returns
    neither an error nor fill but an UNMASKED array of zeros — `max |coordinate| = 0.0`, mask False. Both
    deliberately-broken checkpoints produced exactly this and both passed validation. Resuming from one
    starts every replica with all atoms at the origin, silently."""
    assert spot.positions_are_unusable(np.zeros((147788, 3)))


def test_a_spatially_degenerate_frame_is_rejected_even_when_it_is_not_zero():
    """The general form: every atom at the same point. No real configuration of >1 atom does this, so the
    clause cannot cost a genuine commit."""
    a = np.full((500, 3), 2.5)
    assert spot.positions_are_unusable(a)


def test_a_single_atom_frame_is_NOT_condemned_by_the_degeneracy_clause():
    """A one-particle system is trivially 'degenerate' and must not be rejected for it. Guarding the clause
    on shape[0] > 1 is what keeps the check incapable of a false reject."""
    assert not spot.positions_are_unusable(np.array([[1.0, 2.0, 3.0]]))


def test_the_zeros_check_survives_float32():
    assert spot.positions_are_unusable(np.zeros((10, 3), dtype="f4"))


def test_a_real_frame_with_a_zeroed_atom_is_still_accepted():
    a = np.zeros((100, 3))
    a[50] = [1.0, 0.0, 0.0]
    assert not spot.positions_are_unusable(a), "a non-zero extent means it is a real, if odd, frame"
