"""Unit tests for abfe_repair_gate — the ABFE λ-repair TECHNICAL-VALIDITY gate (prereg §2).

Split by dependency, exactly as the sandbox requires:
  * PURE-LOGIC tests (criteria 1 schedule-identity, 2 data-integrity, and the overlap-graph connectivity helper)
    use SYNTHETIC window_NN.jsonl fixtures and stdlib only — they MUST pass with no numpy/pymbar (dev sandbox).
  * MBAR-dependent tests (criteria 3/4/5) are guarded by `pytest.importorskip("pymbar")` and build synthetic
    reduced potentials with KNOWN statistical structure (a harmonic ladder) — they SKIP in the sandbox and run
    in CI. No ΔG / overlap / ESS numbers are fabricated: the MBAR tests assert only structural behaviour
    (returns a bool verdict + numeric summaries), not specific physical values.
"""
import json
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import abfe_repair_gate as gate  # noqa: E402

DENSE = gate.reference_schedule("dense")
K = len(DENSE)  # 16


# ---------------------------------------------------------------------------------------------------------------
# fixture builders
# ---------------------------------------------------------------------------------------------------------------
def _write_leg(leg_dir, we, meta=None, dup_iters=None):
    """Write we[k] = [u_vector, ...] to window_kk.jsonl (iter = sample index). `dup_iters[k]` optionally
    re-appends the first sample under a duplicate iter to exercise dedup. Writes meta.json if provided."""
    os.makedirs(leg_dir, exist_ok=True)
    dup_iters = dup_iters or {}
    for k, rows in enumerate(we):
        p = os.path.join(leg_dir, "window_%02d.jsonl" % k)
        with open(p, "w") as f:
            for n, u in enumerate(rows):
                f.write(json.dumps({"w": k, "iter": n, "u": list(u)}) + "\n")
            for _ in range(dup_iters.get(k, 0)):
                if rows:
                    f.write(json.dumps({"w": k, "iter": 0, "u": list(rows[0])}) + "\n")  # duplicate iter 0
    if meta is not None:
        with open(os.path.join(leg_dir, "meta.json"), "w") as f:
            json.dump(meta, f)


def _flat_we(K=K, N=6, val=0.0):
    """K windows, N finite samples each, every u a length-K vector (values irrelevant to the pure checks)."""
    return [[[val + 0.01 * j for j in range(K)] for _n in range(N)] for _k in range(K)]


# ===============================================================================================================
# CRITERION 1 — schedule identity (pure)
# ===============================================================================================================
def test_crit1_dimensions_pass_but_lambda_unverifiable_flagged(tmp_path):
    leg = str(tmp_path / "leg")
    _write_leg(leg, _flat_we(), meta={"leg": "complex", "n_windows": 16, "temperature_K": 300.0})
    windows = gate.read_windows(leg)
    c = gate.crit_schedule_identity(windows, DENSE, gate._load_meta(leg))
    assert c["passed"] is True
    assert c["n_windows_with_data"] == 16
    assert c["contiguous_0_to_Kminus1"] is True
    assert c["u_length_ok"] is True
    # λ identity is NOT silently passed — it is flagged as unverifiable from data
    assert c["lambda_identity_source"] == "unverifiable"
    assert c["lambda_identity_verified_from_data"] is False
    assert any("could_not_be_verified" in fl for fl in c["flags"])


def test_crit1_lambda_verified_when_meta_records_schedule(tmp_path):
    leg = str(tmp_path / "leg")
    meta = {"leg": "complex", "n_windows": 16, "schedule": [list(x) for x in DENSE]}
    _write_leg(leg, _flat_we(), meta=meta)
    c = gate.crit_schedule_identity(gate.read_windows(leg), DENSE, gate._load_meta(leg))
    assert c["lambda_identity_source"] == "meta.json"
    assert c["lambda_identity_match"] is True
    assert c["lambda_identity_verified_from_data"] is True
    assert c["passed"] is True


def test_crit1_lambda_mismatch_fails(tmp_path):
    leg = str(tmp_path / "leg")
    bad = [list(x) for x in DENSE]
    bad[5] = [0.0, 0.123]                       # perturb one window's λ → must fail on VALUE
    _write_leg(leg, _flat_we(), meta={"n_windows": 16, "schedule": bad})
    c = gate.crit_schedule_identity(gate.read_windows(leg), DENSE, gate._load_meta(leg))
    assert c["lambda_identity_match"] is False
    assert c["passed"] is False


def test_crit1_lambda_reordering_fails(tmp_path):
    leg = str(tmp_path / "leg")
    reordered = [list(x) for x in DENSE]
    reordered[7], reordered[8] = reordered[8], reordered[7]   # same values, wrong ORDER
    _write_leg(leg, _flat_we(), meta={"n_windows": 16, "schedule": reordered})
    c = gate.crit_schedule_identity(gate.read_windows(leg), DENSE, gate._load_meta(leg))
    assert c["lambda_identity_match"] is False
    assert c["passed"] is False


def test_crit1_missing_window_fails(tmp_path):
    leg = str(tmp_path / "leg")
    we = _flat_we()
    _write_leg(leg, we)
    os.remove(os.path.join(leg, "window_15.jsonl"))          # only 15 windows with data
    c = gate.crit_schedule_identity(gate.read_windows(leg), DENSE, None)
    assert c["n_windows_with_data"] == 15
    assert c["contiguous_0_to_Kminus1"] is False
    assert c["passed"] is False


def test_crit1_wrong_u_length_fails(tmp_path):
    leg = str(tmp_path / "leg")
    we = [[[0.0] * 12 for _ in range(5)] for _ in range(K)]  # 16 windows but u is a 12-vector
    _write_leg(leg, we)
    c = gate.crit_schedule_identity(gate.read_windows(leg), DENSE, None)
    assert c["u_length_ok"] is False
    assert c["passed"] is False


def test_crit1_extra_window_beyond_schedule_fails(tmp_path):
    leg = str(tmp_path / "leg")
    _write_leg(leg, _flat_we())
    with open(os.path.join(leg, "window_16.jsonl"), "w") as f:  # a stray 17th window
        f.write(json.dumps({"w": 16, "iter": 0, "u": [0.0] * K}) + "\n")
    c = gate.crit_schedule_identity(gate.read_windows(leg), DENSE, None)
    assert any("extra_window" in fl for fl in c["flags"])
    assert c["passed"] is False


# ===============================================================================================================
# CRITERION 2 — data integrity (pure)
# ===============================================================================================================
def test_crit2_clean_data_passes_and_reports_counts(tmp_path):
    leg = str(tmp_path / "leg")
    _write_leg(leg, _flat_we(N=7))
    c = gate.crit_data_integrity(gate.read_windows(leg), K)
    assert c["passed"] is True
    assert c["all_finite"] is True
    assert c["total_duplicate_iters_removed"] == 0
    assert all(row["n_dedup"] == 7 for row in c["per_window_sample_counts"])


def test_crit2_dedup_by_iteration(tmp_path):
    leg = str(tmp_path / "leg")
    # add 2 duplicate iter-0 records to window 3 → dedup must drop them, sample count unchanged
    _write_leg(leg, _flat_we(N=5), dup_iters={3: 2})
    windows = gate.read_windows(leg)
    assert windows[3]["n_raw"] == 7
    assert windows[3]["n_dedup"] == 5
    assert windows[3]["dup_iters_removed"] == 2
    c = gate.crit_data_integrity(windows, K)
    assert c["passed"] is True
    assert c["unique_after_dedup"] is True
    assert c["total_duplicate_iters_removed"] == 2


def test_crit2_nonfinite_fails(tmp_path):
    leg = str(tmp_path / "leg")
    we = _flat_we(N=5)
    we[4][2][7] = float("nan")                  # one NaN
    we[9][0][0] = float("inf")                  # one inf
    _write_leg(leg, we)
    c = gate.crit_data_integrity(gate.read_windows(leg), K)
    assert c["passed"] is False
    assert c["all_finite"] is False
    bad = {d["window"] for d in c["nonfinite_windows"]}
    assert {4, 9} <= bad


def test_crit2_parse_errors_flagged(tmp_path):
    leg = str(tmp_path / "leg")
    _write_leg(leg, _flat_we(N=4))
    with open(os.path.join(leg, "window_02.jsonl"), "a") as f:
        f.write("{not valid json\n")            # torn line
    windows = gate.read_windows(leg)
    assert windows[2]["parse_errors"] == 1
    c = gate.crit_data_integrity(windows, K)
    assert c["no_parse_errors"] is False
    assert c["passed"] is False


# ===============================================================================================================
# overlap-graph connectivity helper (pure — no MBAR solve)
# ===============================================================================================================
def _chain_overlap(K, adj_val, off=0.0):
    """A K×K overlap matrix that is a simple chain: O[i][i]=1, O[i][i±1]=adj_val, else `off`."""
    M = [[off] * K for _ in range(K)]
    for i in range(K):
        M[i][i] = 1.0
        if i + 1 < K:
            M[i][i + 1] = M[i + 1][i] = adj_val
    return M


def test_connectivity_connected_chain():
    M = _chain_overlap(6, adj_val=0.2)
    g = gate.overlap_graph_connected(M, edge_threshold=0.01)
    assert g["connected"] is True
    assert g["unreachable"] == []
    assert gate.adjacent_overlaps(M) == [0.2, 0.2, 0.2, 0.2, 0.2]


def test_connectivity_broken_chain_disconnected():
    M = _chain_overlap(6, adj_val=0.2)
    M[2][3] = M[3][2] = 0.0                      # sever the 2–3 bond, no long-range bridge
    g = gate.overlap_graph_connected(M, edge_threshold=0.01)
    assert g["connected"] is False
    assert set(g["unreachable"]) == {3, 4, 5}
    assert min(gate.adjacent_overlaps(M)) == 0.0


def test_connectivity_bridged_low_adjacent_still_connected():
    # adjacent 2–3 is below threshold, but a long-range 2–4 overlap keeps the graph connected end-to-end
    M = _chain_overlap(6, adj_val=0.2)
    M[2][3] = M[3][2] = 0.001
    M[2][4] = M[4][2] = 0.2
    g = gate.overlap_graph_connected(M, edge_threshold=0.01)
    assert g["connected"] is True                # graph-connectivity is stronger than "min adjacent > x"
    assert min(gate.adjacent_overlaps(M)) == 0.001


# ===============================================================================================================
# plateau helper (pure — trace already computed)
# ===============================================================================================================
def test_plateau_flat_tail_passes():
    trace = [(n, 5.0 - 3.0 / n, 0.2) for n in range(2, 60)]   # settles toward 5.0, flat tail
    p = gate._plateau_check(trace, plateau_tol=0.75)
    assert p["plateau_flat"] is True


def test_plateau_drifting_tail_fails():
    trace = [(n, 0.1 * n, 0.05) for n in range(2, 40)]        # still rising at the end, tiny SE
    p = gate._plateau_check(trace, plateau_tol=0.75)
    assert p["plateau_flat"] is False


# ===============================================================================================================
# top-level gate — pure part (verdict deferred when pymbar absent)
# ===============================================================================================================
def test_evaluate_gate_defers_without_pymbar(tmp_path):
    leg = str(tmp_path / "leg")
    _write_leg(leg, _flat_we(N=6), meta={"leg": "complex", "n_windows": 16, "temperature_K": 300.0})
    res = gate.evaluate_repair_gate(leg, schedule="dense")
    # pure criteria are always evaluated
    assert res["criteria"]["1_schedule_identity"]["available"] is True
    assert res["criteria"]["1_schedule_identity"]["passed"] is True
    assert res["criteria"]["2_data_integrity"]["available"] is True
    assert res["criteria"]["2_data_integrity"]["passed"] is True
    if gate._mbar_available():
        assert res["technically_valid"] in (True, False)
    else:
        # MBAR criteria unavailable → verdict deferred, not a false FAIL
        assert res["technically_valid"] is None
        assert res["criteria"]["3_connected_overlap"]["available"] is False
        assert res["overall_note"] and "deferred" in res["overall_note"]


# ===============================================================================================================
# MBAR-dependent criteria (3/4/5) — SKIP without pymbar; structural assertions only (no fabricated numbers)
# ===============================================================================================================
def _harmonic_ladder_leg(leg_dir, K=K, N=120, spacing=0.35, sigma=1.0, seed=1):
    """Write a synthetic K-window harmonic ladder: state j has u_j(x)=0.5*((x-j*spacing)/sigma)^2, samples for
    window k ~ Normal(k*spacing, sigma). Closely-spaced → adjacent windows overlap (a well-conditioned leg).
    Known statistical structure; no physical ΔG asserted."""
    import numpy as np
    rng = np.random.default_rng(seed)
    we = []
    for k in range(K):
        xs = rng.normal(k * spacing, sigma, N)
        rows = [[0.5 * ((x - j * spacing) / sigma) ** 2 for j in range(K)] for x in xs]
        we.append(rows)
    _write_leg(leg_dir, we, meta={"leg": "complex", "n_windows": K, "temperature_K": 300.0})
    return we


def test_crit3_overlap_runs_and_returns_structure(tmp_path):
    pytest.importorskip("pymbar")
    pytest.importorskip("numpy")
    leg = str(tmp_path / "leg")
    _harmonic_ladder_leg(leg)
    c = gate.crit_connected_overlap(leg, K)
    assert c["available"] is True
    assert "error" not in c or c.get("error") is None
    assert isinstance(c["connected"], bool)
    assert isinstance(c["min_adjacent_overlap"], float)
    assert len(c["adjacent_overlaps"]) == K - 1


def test_crit4_ess_runs_and_lists_below_floor(tmp_path):
    pytest.importorskip("pymbar")
    pytest.importorskip("numpy")
    leg = str(tmp_path / "leg")
    _harmonic_ladder_leg(leg, N=80)
    c = gate.crit_ess(leg, K, floor=50.0)
    assert c["available"] is True
    assert isinstance(c["passed"], bool)
    assert len(c["per_state_ess"]) == K
    # extension_eligible must be consistent with the below-floor list
    assert c["extension_eligible"] == bool(c["states_below_floor"])


def test_crit5_convergence_runs_and_returns_halfdiff(tmp_path):
    pytest.importorskip("pymbar")
    pytest.importorskip("numpy")
    leg = str(tmp_path / "leg")
    _harmonic_ladder_leg(leg, N=120)
    c = gate.crit_convergence(leg, K, {"temperature_K": 300.0})
    assert c["available"] is True
    assert "half_difference" in c and isinstance(c["half_difference"], float)
    assert "plateau" in c


def test_evaluate_gate_full_verdict_with_pymbar(tmp_path):
    pytest.importorskip("pymbar")
    pytest.importorskip("numpy")
    leg = str(tmp_path / "leg")
    _harmonic_ladder_leg(leg, N=120)
    res = gate.evaluate_repair_gate(leg, schedule="dense")
    assert res["technically_valid"] in (True, False)
    assert res["criteria"]["1_schedule_identity"]["passed"] is True
