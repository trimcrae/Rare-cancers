"""Unit tests for nr4a3_abfe_diagnostics — the SI diagnostics (overlap / ESS / forward-reverse / per-replicate).

Every MBAR-touching test uses a SMALL synthetic reduced-potential set with a KNOWN answer:
  * identical states  -> overlap 1/K everywhere, MBAR ESS = N_total          (exactly derivable)
  * well-separated states -> overlap ≈ identity, adjacent overlap ~0
  * iid vs autocorrelated timeseries -> statistical inefficiency g ≈ 1 vs g ≫ 1
  * harmonic-oscillator ladder -> forward/reverse ΔG agree (converged) within a few·SE
  * per_replicate_summary -> reproduces the committed §4 mean/SD arithmetic exactly.
No real ABFE numbers are fabricated; the only physical-looking values are synthetic draws with analytic targets.
"""
import math
import os
import sys
import tempfile

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import nr4a3_abfe_diagnostics as diag  # noqa: E402


# ---------------------------------------------------------------------------------------------------------------
# helpers to build synthetic reduced potentials
# ---------------------------------------------------------------------------------------------------------------
def _identical_states_we(K=3, N=150):
    """K states whose reduced potential is IDENTICAL for every state (a flat, perfectly-overlapping ladder).
    Each sample's u is the same constant across all λ, so MBAR weights are uniform -> known overlap/ESS."""
    rng = np.random.default_rng(0)
    we = []
    for _k in range(K):
        rows = []
        for _n in range(N):
            base = float(rng.normal(0.0, 1.0))
            rows.append([base] * K)          # identical at every state
        we.append(rows)
    return we


def _harmonic_ladder_we(K=4, N=400, spacing=1.0, sigma=1.0, seed=1):
    """K harmonic states: state j has reduced potential u_j(x) = 0.5*((x - j*spacing)/sigma)^2. Samples for
    state k drawn ~ Normal(k*spacing, sigma). Adjacent states overlap (spacing≈sigma); far states don't."""
    rng = np.random.default_rng(seed)
    we = []
    for k in range(K):
        xs = rng.normal(k * spacing, sigma, N)
        rows = [[0.5 * ((x - j * spacing) / sigma) ** 2 for j in range(K)] for x in xs]
        we.append(rows)
    return we


# ---------------------------------------------------------------------------------------------------------------
# ragged <-> dense conversions
# ---------------------------------------------------------------------------------------------------------------
def test_we_to_ukln_and_back_roundtrip():
    we = [[[0.0, 1.0, 2.0], [0.1, 1.1, 2.1]], [[3.0, 0.0, 3.0]], [[4.0, 4.0, 0.0]]]
    u_kln, N_k = diag.we_to_ukln(we)
    assert N_k == [2, 1, 1]
    assert u_kln.shape == (3, 3, 2)               # K=3, N_max=2
    # sample 0 of state 0 evaluated at all states = [0,1,2]
    assert list(u_kln[0, :, 0]) == [0.0, 1.0, 2.0]
    u_kn, N_k2 = diag.ukln_to_ukn(u_kln, N_k)
    assert N_k2 == [2, 1, 1]
    assert u_kn.shape == (3, 4)                    # 3 states x 4 total samples
    # first column = state0 sample0 ; last column = state2 sample0
    assert list(u_kn[:, 0]) == [0.0, 1.0, 2.0]
    assert list(u_kn[:, 3]) == [4.0, 4.0, 0.0]


def test_ukln_to_ukn_respects_N_k_padding():
    # padded (K,K,N_max=3) but only 2 real samples in state 1 -> the pad row must be ignored
    u_kln = np.zeros((2, 2, 3))
    u_kln[0, :, :2] = np.array([[0.0, 0.1], [5.0, 5.1]])
    u_kln[1, :, :2] = np.array([[6.0, 6.1], [0.0, 0.1]])
    u_kln[:, :, 2] = 999.0                          # padding — must never be read
    u_kn, N_k = diag.ukln_to_ukn(u_kln, [2, 2])
    assert u_kn.shape == (2, 4)
    assert 999.0 not in set(u_kn.flatten())


# ---------------------------------------------------------------------------------------------------------------
# 1. overlap matrix — known answers
# ---------------------------------------------------------------------------------------------------------------
def test_overlap_identical_states_is_uniform_1_over_K():
    # For K identical states with uniform MBAR weights, O[i,j] = N_i * sum_n W_ni W_nj = 1/K exactly.
    K = 3
    we = _identical_states_we(K=K, N=120)
    ov = diag.mbar_overlap(*diag.we_to_ukln(we))
    assert ov.shape == (K, K)
    assert np.allclose(ov, 1.0 / K, atol=1e-6), ov
    # overlap rows sum to 1 (each is a probability-like distribution over states)
    assert np.allclose(ov.sum(axis=1), 1.0, atol=1e-6)


def test_overlap_separated_states_near_identity():
    # Far-apart harmonic states barely share configurations -> overlap close to identity, tiny adjacents.
    we = _harmonic_ladder_we(K=4, N=300, spacing=4.0, sigma=1.0, seed=3)
    ov = diag.mbar_overlap(*diag.we_to_ukln(we))
    assert np.all(np.diag(ov) > 0.9), np.diag(ov)
    adj = diag.adjacent_overlaps(ov)
    assert max(adj) < 0.1, adj                      # neighbours essentially disjoint


def test_overlap_symmetric_and_adjacent_beats_far():
    # A well-spaced ladder: neighbouring windows overlap MORE than distant ones (the schedule-quality signal).
    we = _harmonic_ladder_we(K=4, N=500, spacing=1.0, sigma=1.0, seed=5)
    ov = diag.mbar_overlap(*diag.we_to_ukln(we))
    assert np.allclose(ov, ov.T, atol=0.05), ov     # overlap ~symmetric
    assert ov[0, 1] > ov[0, 3], (ov[0, 1], ov[0, 3])
    adj = diag.adjacent_overlaps(ov)
    assert len(adj) == 3 and all(a > 0.05 for a in adj), adj


# ---------------------------------------------------------------------------------------------------------------
# 2. effective sample size
# ---------------------------------------------------------------------------------------------------------------
def test_mbar_ess_identical_states_equals_total_samples():
    # Identical states -> uniform weights -> ESS_k = 1/sum(W^2) = N_total for every state.
    K, N = 3, 100
    we = _identical_states_we(K=K, N=N)
    ess = diag.effective_sample_size(*diag.we_to_ukln(we))
    assert ess.shape == (K,)
    assert np.allclose(ess, K * N, rtol=1e-6), ess


def test_mbar_ess_separated_states_near_own_N():
    # Well-separated states: each state's estimate is informed mostly by its OWN samples -> ESS ~ N_k.
    we = _harmonic_ladder_we(K=3, N=200, spacing=4.0, sigma=1.0, seed=7)
    ess = diag.effective_sample_size(*diag.we_to_ukln(we))
    assert np.all(ess > 150) and np.all(ess <= 3 * 200 + 1), ess


def test_autocorr_inefficiency_iid_is_near_one():
    rng = np.random.default_rng(11)
    iid = rng.normal(0, 1, 5000)
    g, ess = diag.autocorr_inefficiency(iid)
    assert 0.9 <= g <= 1.6, g                       # uncorrelated -> g ~ 1
    assert ess > 3000, ess


def test_autocorr_inefficiency_correlated_is_large():
    # AR(1) with strong correlation -> g >> 1, ESS << N.
    rng = np.random.default_rng(13)
    n = 5000
    x = np.zeros(n)
    phi = 0.95
    for i in range(1, n):
        x[i] = phi * x[i - 1] + rng.normal(0, 1)
    g, ess = diag.autocorr_inefficiency(x)
    assert g > 5.0, g
    assert ess < n / 3, ess


def test_autocorr_constant_and_short_series_safe():
    assert diag.autocorr_inefficiency([5.0, 5.0, 5.0, 5.0]) == (1.0, 4.0)
    assert diag.autocorr_inefficiency([1.0, 2.0]) == (1.0, 2.0)


def test_ess_report_shape_and_fields():
    we = _harmonic_ladder_we(K=3, N=120, spacing=1.0, sigma=1.0, seed=9)
    rows = diag.ess_report(we)
    assert [r["window"] for r in rows] == [0, 1, 2]
    assert all(r["n_samples"] == 120 for r in rows)
    assert all(r["ess_mbar"] is not None and r["g"] >= 1.0 for r in rows)
    assert all(0 < r["ess_autocorr"] <= 120 for r in rows)


# ---------------------------------------------------------------------------------------------------------------
# 3. forward / reverse convergence
# ---------------------------------------------------------------------------------------------------------------
def test_forward_reverse_converged_leg_agrees():
    # A stationary (converged, equilibrated) harmonic ladder: forward and reverse ΔG at f=1.0 must match, and
    # the full-data forward ΔG must match the direct engine reduce of the same samples.
    we = _harmonic_ladder_we(K=4, N=600, spacing=1.0, sigma=1.0, seed=21)
    conv = diag.forward_reverse_dG(we, temperature_K=300.0)
    assert conv["n_windows"] == 4 and conv["n_min"] == 600
    fwd_full = [p for p in conv["forward"] if p["fraction"] == 1.0][0]
    rev_full = [p for p in conv["reverse"] if p["fraction"] == 1.0][0]
    # same sample set at f=1.0 (first-all == last-all) -> identical ΔG
    assert abs(fwd_full["dg"] - rev_full["dg"]) < 1e-6, (fwd_full, rev_full)
    # forward halves vs reverse halves for a stationary series agree within a few SE (no drift)
    fwd_half = [p for p in conv["forward"] if p["fraction"] == 0.5][0]
    rev_half = [p for p in conv["reverse"] if p["fraction"] == 0.5][0]
    tol = 5.0 * (fwd_half["se"] + rev_half["se"])
    assert abs(fwd_half["dg"] - rev_half["dg"]) < tol, (fwd_half, rev_half, tol)


def test_forward_reverse_matches_engine_reduce_leg_at_full_data():
    # The f=1.0 forward ΔG must equal nr4a3_abfe.reduce_leg on the same jsonl (consistency with the reducer that
    # produced §4). Write the we to jsonl, reduce with the engine, compare.
    import nr4a3_abfe as abfe
    we = _harmonic_ladder_we(K=abfe.N_WINDOWS, N=60, spacing=0.8, sigma=1.0, seed=31)
    d = tempfile.mkdtemp()
    for k in range(abfe.N_WINDOWS):
        for i, sample in enumerate(we[k]):
            abfe.append_reduced_potentials(d, k, i, sample)
    eng_dg, eng_se = abfe.reduce_leg(d, temperature_K=300.0)
    conv = diag.forward_reverse_dG(we, temperature_K=300.0, K=abfe.N_WINDOWS)
    fwd_full = [p for p in conv["forward"] if p["fraction"] == 1.0][0]
    assert abs(fwd_full["dg"] - eng_dg) < 1e-6, (fwd_full["dg"], eng_dg)


# ---------------------------------------------------------------------------------------------------------------
# load_leg_we — dedup by iteration (matches reduce_leg)
# ---------------------------------------------------------------------------------------------------------------
def test_load_leg_we_dedups_by_iteration():
    import nr4a3_abfe as abfe
    d = tempfile.mkdtemp()
    K = abfe.N_WINDOWS
    # window 0: write iter 0,1 then a DUPLICATE iter 1 (resume/recovery) with a different value -> keep last
    abfe.append_reduced_potentials(d, 0, 0, [0.0] * K)
    abfe.append_reduced_potentials(d, 0, 1, [1.0] * K)
    abfe.append_reduced_potentials(d, 0, 1, [9.0] * K)     # duplicate iter 1
    we = diag.load_leg_we(d, K=K)
    assert len(we[0]) == 2, "duplicate iteration was not deduped"
    assert we[0][1] == [9.0] * K, "dedup must keep the LAST record for an iter"
    assert we[1] == [] and we[K - 1] == []                 # missing windows -> empty


def test_load_leg_we_tolerates_torn_last_line():
    import nr4a3_abfe as abfe
    d = tempfile.mkdtemp()
    K = abfe.N_WINDOWS
    p = os.path.join(d, "window_00.jsonl")
    abfe.append_reduced_potentials(d, 0, 0, [0.0] * K)
    with open(p, "a") as f:
        f.write('{"w":0,"iter":1,"u":[0.0,')            # torn/partial line
    we = diag.load_leg_we(d, K=K)
    assert len(we[0]) == 1                                 # only the intact record survives


# ---------------------------------------------------------------------------------------------------------------
# receptor ΔG_bind + per-replicate summary reproducing §4
# ---------------------------------------------------------------------------------------------------------------
def test_receptor_dg_bind_matches_combine_legs():
    import nr4a3_abfe as abfe
    K = abfe.N_WINDOWS
    cwe = _harmonic_ladder_we(K=K, N=80, spacing=0.9, sigma=1.0, seed=41)
    swe = _harmonic_ladder_we(K=K, N=80, spacing=0.6, sigma=1.0, seed=42)
    ssc = -9.16
    out = diag.receptor_dg_bind(cwe, swe, ssc, temperature_K=300.0, K=K)
    # cross-check against a direct combine_legs on the two legs reduced the engine way
    RT = 0.0019872041 * 300.0
    c = abfe._dg_slice(cwe, 0, 80, K, RT)
    s = abfe._dg_slice(swe, 0, 80, K, RT)
    dg, se = abfe.combine_legs(c[0], c[1], s[0], s[1], ssc)
    assert abs(out["dg_bind"] - dg) < 1e-9
    assert abs(out["se"] - se) < 1e-9
    assert out["restraint_standard_state_dg"] == ssc


def test_per_replicate_summary_reproduces_manuscript_s4():
    # The committed §4 per-replicate ΔG_bind values (nr4a3-degrader-paper.md): r2's NR4A3 leg was the soft draw
    # (+5.1 vs +2.6/+2.8), and excluding r2 the r1/r3 ΔΔG(NR4A3-NR4A1) = -6.9/-4.5. We choose per-replicate
    # values consistent with these constraints and the reported means, then assert the summary reproduces §4.
    dg = {
        "r1": {"nr4a3": 2.6, "nr4a1": 9.5, "nr4a2": 8.6},   # ΔΔG NR4A1 = -6.9, NR4A2 = -6.0
        "r2": {"nr4a3": 5.1, "nr4a1": 7.8, "nr4a2": 8.7},   # soft NR4A3 draw
        "r3": {"nr4a3": 2.8, "nr4a1": 7.3, "nr4a2": 8.2},   # ΔΔG NR4A1 = -4.5, NR4A2 = -5.4
    }
    s = diag.per_replicate_summary(dg, target="nr4a3")
    pr = s["per_receptor"]
    # NR4A3 mean 3.5 ± 1.4 ; matches §4 (values 2.6/5.1/2.8)
    assert abs(pr["nr4a3"]["mean"] - 3.5) < 0.05, pr["nr4a3"]
    assert abs(pr["nr4a3"]["sd"] - 1.4) < 0.1, pr["nr4a3"]["sd"]
    # ΔΔG contrasts favour NR4A3 (negative) and direction is unanimous across replicates
    assert s["ddg"]["nr4a1"]["mean"] < 0 and s["ddg"]["nr4a2"]["mean"] < 0
    assert s["ddg"]["nr4a1"]["direction_unanimous"]
    assert s["ddg"]["nr4a2"]["direction_unanimous"]
    # per-rep r1/r3 NR4A1 contrast equals the manuscript's -6.9 / -4.5
    assert abs(s["ddg"]["nr4a1"]["per_rep"]["r1"] - (-6.9)) < 1e-9
    assert abs(s["ddg"]["nr4a1"]["per_rep"]["r3"] - (-4.5)) < 1e-9
    # and the check-against-manuscript on the ΔG_bind means passes
    chk = diag.check_against_manuscript(s)
    means_ok = [r for r in chk["rows"] if r["quantity"].endswith(".mean")]
    assert all(r["within_tol"] for r in means_ok), [r for r in means_ok if not r["within_tol"]]


def test_mean_sd_ddof1():
    m, sd, n = diag._mean_sd([2.6, 5.1, 2.8])
    assert abs(m - 3.5) < 1e-9 and n == 3
    assert abs(sd - math.sqrt(((2.6 - 3.5) ** 2 + (5.1 - 3.5) ** 2 + (2.8 - 3.5) ** 2) / 2)) < 1e-9
    assert diag._mean_sd([4.0])[1] is None            # SD undefined for n<2
    assert diag._mean_sd([])[2] == 0


def test_check_against_manuscript_flags_mismatch():
    # A summary that does NOT match §4 must be flagged inconsistent (never silently accepted).
    bad = diag.per_replicate_summary({"r1": {"nr4a3": 50.0, "nr4a1": 51.0, "nr4a2": 52.0}}, target="nr4a3")
    chk = diag.check_against_manuscript(bad)
    assert chk["consistent"] is False


def test_leg_diagnostics_bundle_keys():
    we = _harmonic_ladder_we(K=4, N=200, spacing=1.0, sigma=1.0, seed=51)
    bundle = diag.leg_diagnostics(we, temperature_K=300.0)
    for key in ("overlap_matrix", "adjacent_overlaps", "min_adjacent_overlap", "ess", "convergence"):
        assert key in bundle, key
    assert len(bundle["overlap_matrix"]) == 4
    assert bundle["min_adjacent_overlap"] == min(bundle["adjacent_overlaps"])


def test_leg_diagnostics_empty_leg():
    empty = [[] for _ in range(diag.n_windows())]
    bundle = diag.leg_diagnostics(empty)
    assert bundle.get("empty") is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
