"""Unit tests for the PURE core of nr4a3_slow_cv (Phase 1 slow-CV analysis). numpy only; no mdtraj/deeptime."""
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import nr4a3_slow_cv as sc  # noqa: E402


def test_pearson_perfect_and_anti():
    assert sc.pearson([1, 2, 3, 4], [2, 4, 6, 8]) == pytest.approx(1.0)
    assert sc.pearson([1, 2, 3, 4], [8, 6, 4, 2]) == pytest.approx(-1.0)


def test_pearson_zero_variance_is_zero():
    assert sc.pearson([1, 1, 1, 1], [1, 2, 3, 4]) == 0.0


def test_pearson_requires_equal_length():
    with pytest.raises(ValueError):
        sc.pearson([1, 2, 3], [1, 2])


def test_implied_timescales_monotone_in_lambda():
    # larger λ (slower) -> longer timescale; λ<=0 or >=1 -> None
    ts = sc.implied_timescales([0.9, 0.5, 0.99, 1.0, -0.1, 0.0], lag_frames=10, dt_ns=0.05)
    assert ts[3] is None and ts[4] is None and ts[5] is None
    # 0.99 slower than 0.9 slower than 0.5
    assert ts[2] > ts[0] > ts[1] > 0


def test_implied_timescales_formula():
    # t = -lag*dt/ln(λ)
    lam = 0.8
    got = sc.implied_timescales([lam], lag_frames=20, dt_ns=0.05)[0]
    assert got == pytest.approx(-(20 * 0.05) / math.log(lam))


def test_redundancy_verdict_bands():
    assert sc.redundancy_verdict(0.95) == "redundant"
    assert sc.redundancy_verdict(-0.92) == "redundant"      # uses |r|
    assert sc.redundancy_verdict(0.8) == "partial"
    assert sc.redundancy_verdict(0.5) == "hidden_mode"
    assert sc.redundancy_verdict(0.7) == "hidden_mode"      # boundary inclusive


def test_dihedral_sincos_shape_and_values():
    out = sc.dihedral_sincos([0.0, math.pi / 2])
    assert out.shape == (2, 2)
    assert out[0] == pytest.approx([0.0, 1.0])              # sin0, cos0
    assert out[1] == pytest.approx([1.0, 0.0], abs=1e-9)    # sin(π/2), cos(π/2)
