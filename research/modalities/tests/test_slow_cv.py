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


def _slow_fast_traj(n=4000, tau_slow=200.0, seed=0):
    """Synthetic 2-feature trajectory: feature 0 is a SLOW Ornstein-Uhlenbeck process (autocorr time
    tau_slow), feature 1 is fast white-ish noise. TICA's slowest IC must load on feature 0."""
    rng = np.random.default_rng(seed)
    x0 = np.zeros(n)
    a = math.exp(-1.0 / tau_slow)                          # AR(1) coefficient for the slow mode
    for i in range(1, n):
        x0[i] = a * x0[i - 1] + math.sqrt(1 - a * a) * rng.standard_normal()
    x1 = 0.3 * rng.standard_normal(n)                     # fast, small-amplitude noise
    return np.stack([x0, x1], axis=1)


def test_tica_identifies_slow_feature():
    X = _slow_fast_traj()
    C0, Ctau, mean, std, npairs = sc.tica_covariances([X], lag_frames=20)
    w, v = sc.tica_solve(C0, Ctau, n_components=2)
    # slowest eigenvalue is largest and physical (0<lambda<1)
    assert 0.0 < w[0] < 1.0 and w[0] >= w[1]
    # the slowest IC loads overwhelmingly on feature 0 (the slow OU process)
    lead = v[:, 0] / np.linalg.norm(v[:, 0])
    assert abs(lead[0]) > abs(lead[1]) * 3


def test_tica_timescale_recovers_ou_constant():
    X = _slow_fast_traj(tau_slow=200.0)
    C0, Ctau, mean, std, _ = sc.tica_covariances([X], lag_frames=20)
    w, _ = sc.tica_solve(C0, Ctau, n_components=2)
    # implied timescale of the slow IC ~ the OU autocorrelation time (order-of-magnitude, dt=1 frame)
    t = sc.implied_timescales([w[0]], lag_frames=20, dt_ns=1.0)[0]
    assert 80.0 < t < 500.0


def test_tica_covariances_skips_boundaries_and_pools():
    # two short trajectories, each longer than the lag -> both contribute pairs
    X = _slow_fast_traj(n=500, seed=1)
    C0, Ctau, mean, std, npairs = sc.tica_covariances([X[:250], X[250:]], lag_frames=10)
    assert npairs == (250 - 10) + (250 - 10)
    assert C0.shape == (2, 2) and Ctau.shape == (2, 2)


def test_build_combine_cv_reproduces_standardized_projection():
    X = _slow_fast_traj(n=800, seed=2)
    C0, Ctau, mean, std, _ = sc.tica_covariances([X], lag_frames=15)
    w, v = sc.tica_solve(C0, Ctau, n_components=2)
    spec = sc.build_combine_cv(v[:, 0], mean, std)
    # PLUMED COMBINE value on raw features must equal the standardized projection Y·v
    coeff = np.asarray(spec["coefficients"]); params = np.asarray(spec["parameters"])
    plumed_val = ((X - params) * coeff).sum(axis=1)
    standardized_proj = (((X - mean) / std) @ v[:, 0])
    assert plumed_val == pytest.approx(standardized_proj, abs=1e-9)
    assert spec["powers"] == [1, 1]
