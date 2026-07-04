import math
import os
import sys

import pytest

# nr4a3_frame_sanity.kabsch_rmsd imports numpy lazily; the zero-dependency modalities test CI installs only
# pytest, so skip this whole module when numpy is absent rather than fail with ModuleNotFoundError. Runs fully
# in any env that has numpy (locally, or the MD envs).
pytest.importorskip("numpy")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import nr4a3_frame_sanity as fs  # noqa: E402


def test_kabsch_zero_on_identical():
    P = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
    assert fs.kabsch_rmsd(P, P) < 1e-9


def test_kabsch_invariant_to_rigid_motion():
    import numpy as np
    P = np.array([(0, 0, 0), (3, 0, 0), (0, 4, 0), (1, 1, 5)], float)
    theta = 0.7
    R = np.array([[math.cos(theta), -math.sin(theta), 0],
                  [math.sin(theta), math.cos(theta), 0], [0, 0, 1]])
    Q = P @ R.T + np.array([10.0, -5.0, 2.0])       # rotate + translate
    assert fs.kabsch_rmsd(P, Q) < 1e-6              # optimal superposition removes it


def test_kabsch_detects_real_displacement():
    P = [(0, 0, 0), (5, 0, 0), (0, 5, 0), (0, 0, 5)]
    Q = [(0, 0, 0), (5, 0, 0), (0, 5, 0), (0, 0, 9)]   # one atom pulled out
    assert fs.kabsch_rmsd(P, Q) > 1.0


def test_matched_core_excludes_floppy_and_maps_offset():
    # opened residues 1..5; AF2 partners are i+372
    frame_ca = {i: (float(i), 0.0, 0.0) for i in range(1, 6)}
    ref_ca = {i + fs.OFFSET: (float(i), 0.0, 0.0) for i in range(1, 6)}
    P, Q = fs.matched_core_ca(frame_ca, ref_ca, exclude=[(1, 2)])   # drop residues 1,2
    assert len(P) == 3                                              # residues 3,4,5 kept
    assert P == Q                                                   # identical coords -> matched by offset


def test_matched_core_skips_missing_ref_partner():
    frame_ca = {1: (0, 0, 0), 2: (1, 0, 0)}
    ref_ca = {1 + fs.OFFSET: (0, 0, 0)}          # only residue 1 has an AF2 partner
    P, Q = fs.matched_core_ca(frame_ca, ref_ca, exclude=[])
    assert len(P) == 1 and len(Q) == 1
