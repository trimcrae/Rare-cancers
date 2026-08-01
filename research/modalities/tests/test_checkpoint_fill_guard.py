"""A FRAME THAT READS IS NOT A FRAME THAT WAS WRITTEN.

MEASURED, not theorised (2026-08-01, GH run 30675219443). netCDF-4 returns FILL values for a chunk that was
never written, so every check `validate_reporter_pair` made succeeded on a checkpoint whose frame does not
exist: `read_sampler_states` returned the right NUMBER of replicas, `read_energies` returned an array, the
replica counts agreed — and the coordinates were ~1e37 nm. A deliberately-broken checkpoint (the last frame
rewritten at index 0 — the naive prune, run as a negative control) passed the function unchanged.

That is a gap well beyond the pruning work that found it: `commit()`'s entire safety argument is "the pair is
VALIDATED before it is persisted", and `restore_latest`'s is "a bad generation is rejected and we fall back".
Both were resting on readability rather than content.

`positions_look_like_fill` closes it. What is pinned here is the property that makes it safe to put in a live
commit path: it must reject fill, and it must be INCAPABLE of rejecting a genuine frame — the sentinel sits
~30 orders of magnitude above anything physical and ~6 above anything a pathological unwrapped coordinate
could reach.
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
    assert spot.positions_look_like_fill(np.full((22, 3), NETCDF4_F4_FILL, dtype="f4"))


def test_one_bad_atom_among_thousands_is_enough():
    """A partially-written chunk is the realistic corruption, not an all-fill one."""
    a = np.zeros((147788, 3), dtype="f4")
    a[99_999, 1] = NETCDF4_F4_FILL
    assert spot.positions_look_like_fill(a)


def test_a_masked_array_is_caught_even_when_the_data_underneath_looks_fine():
    """netCDF4 auto-masks unwritten regions; the DATA beneath a mask is meaningless, so the mask alone
    condemns the frame."""
    a = np.ma.masked_array(np.zeros((10, 3)), mask=np.zeros((10, 3), dtype=bool))
    a.mask[3, 0] = True
    assert spot.positions_look_like_fill(a)


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_non_finite_coordinates_are_caught(bad):
    a = np.zeros((10, 3))
    a[0, 0] = bad
    assert spot.positions_look_like_fill(a)


def test_absent_and_empty_are_caught_rather_than_passing_by_default():
    """§4: an absent reading is not a reading of absence. No positions is not a valid frame."""
    assert spot.positions_look_like_fill(None)
    assert spot.positions_look_like_fill(np.zeros((0, 3)))


# ---------------------------------------------------------------------------------------------
# ...and it must be INCAPABLE of rejecting a real frame — this is what makes it safe to ship
# ---------------------------------------------------------------------------------------------
def test_an_ordinary_solvated_box_passes():
    rng = np.random.default_rng(0)
    assert not spot.positions_look_like_fill(rng.uniform(-12.0, 12.0, size=(147788, 3)))


def test_coordinates_at_the_origin_pass():
    assert not spot.positions_look_like_fill(np.zeros((100, 3)))


def test_a_wildly_unwrapped_coordinate_still_passes():
    """A diffusing molecule under unwrapped coordinates can drift far; 1000 nm is already absurd and must
    still be accepted, because a false REJECT would refuse a real commit."""
    a = np.zeros((10, 3))
    a[0, 0] = 1.0e3
    assert not spot.positions_look_like_fill(a)


def test_the_sentinel_sits_far_from_both_ends():
    """The threshold is not a tuned number: it is orders of magnitude from anything real AND from the fill
    value, so no plausible drift in either direction changes a verdict."""
    assert spot.FILL_MAGNITUDE_NM / 1.0e3 >= 1.0e3, "at least 1e3x headroom above absurd-but-real"
    assert NETCDF4_F4_FILL / spot.FILL_MAGNITUDE_NM >= 1.0e20, "at least 1e20x below the fill value"


def test_float32_precision_does_not_flip_a_verdict():
    a = np.full((10, 3), spot.FILL_MAGNITUDE_NM / 10.0, dtype="f4")
    assert not spot.positions_look_like_fill(a)


# ---------------------------------------------------------------------------------------------
# the wiring: the check is actually consulted by the validator
# ---------------------------------------------------------------------------------------------
def test_validate_reporter_pair_consults_the_fill_check():
    """Source-text pin: the netCDF/openmmtools half cannot run in the sandbox, and a guard nobody calls is
    the failure mode this whole test file exists because of."""
    src = open(spot.__file__).read()
    body = src[src.index("def validate_reporter_pair"):src.index("def read_checkpoint_interval")]
    assert "positions_look_like_fill(_positions_array(" in body


def test_the_fill_check_runs_on_every_replica_not_just_the_first():
    src = open(spot.__file__).read()
    body = src[src.index("def validate_reporter_pair"):src.index("def read_checkpoint_interval")]
    assert "for _i, _st in enumerate(sstates)" in body
