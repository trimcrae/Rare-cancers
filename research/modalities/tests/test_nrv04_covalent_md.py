#!/usr/bin/env python3
"""Tests for the NR-V04 covalent-MD driver's pure geometry helpers (kabsch superposition + interface
selection). The OpenMM build/run is validated on CI, not here. Needs numpy."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("numpy")

from nrv04_covalent_md import _aligned_iface_rmsd, interface_atom_indices, kabsch_rmsd  # noqa: E402

_REF = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]


def test_kabsch_is_rotation_translation_invariant():
    assert abs(kabsch_rmsd(_REF, _REF)) < 1e-9
    rot = [(-y, x, z) for (x, y, z) in _REF]                 # 90deg about z
    rot = [(x + 5, y - 3, z + 2) for (x, y, z) in rot]       # + translation
    assert kabsch_rmsd(rot, _REF) < 1e-6                     # superposition removes it


def test_kabsch_sensitive_to_real_displacement():
    assert kabsch_rmsd([(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 5)], _REF) > 0.5


def test_kabsch_rejects_bad_shapes():
    for bad in ([], [(0, 0, 0)]):
        with pytest.raises(ValueError):
            kabsch_rmsd(bad, _REF)


def test_aligned_iface_rmsd_returns_nan_on_nonfinite():
    """A covalent-pull blow-up produces NaN coordinates; the R1 helper must return NaN (so the caller's
    finite guard records a 'blew_up' outcome) instead of raising LinAlgError and crashing the whole leg."""
    import math
    ca = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
    nan_ca = [(float("nan"), 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
    assert math.isnan(_aligned_iface_rmsd(nan_ca, ca, nan_ca, ca))
    assert math.isnan(_aligned_iface_rmsd(ca, nan_ca, ca, nan_ca))
    # finite input still yields a real number (0 for identical frames)
    assert abs(_aligned_iface_rmsd(ca, ca, ca, ca)) < 1e-6


def test_interface_selection_respects_cutoff():
    pos = [(0, 0, 0), (0.5, 0, 0), (0.9, 0, 0), (5, 0, 0)]
    chains = ["A", "A", "B", "B"]
    e3, tg = interface_atom_indices(pos, chains, {"A"}, {"B"}, cutoff_nm=0.8)
    assert e3 == [1] and tg == [2]                           # atom 0 is 0.9 nm away -> excluded
    e3w, _ = interface_atom_indices(pos, chains, {"A"}, {"B"}, cutoff_nm=1.0)
    assert e3w == [0, 1]                                     # widening the cutoff pulls atom 0 in
