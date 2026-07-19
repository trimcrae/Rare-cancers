"""Reviewer condition 4 (2026-07-19) — PURE additions to ternary_fep_convergence: the overlap-matrix bottleneck
(connectivity, not a naive scalar cutoff) and the dG(t) block-plateau flags. No openmmtools/pymbar needed."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_fep_convergence as cv  # noqa: E402


# --- overlap-matrix bottleneck ----------------------------------------------------------------------------
def test_bottleneck_connected_chain():
    # a well-overlapping 4-state chain: every adjacent pair ~0.4 -> connected
    M = [[0.5, 0.4, 0.08, 0.02],
         [0.4, 0.4, 0.4, 0.08],
         [0.08, 0.4, 0.4, 0.4],
         [0.02, 0.08, 0.4, 0.5]]
    r = cv.overlap_matrix_bottleneck(M)
    assert r["connected"] is True
    assert r["min_adjacent_overlap"] >= cv.OVERLAP_BOTTLENECK_MIN


def test_bottleneck_detects_broken_link():
    # states 1-2 barely overlap (0.005) -> a bottleneck disconnects the path even though other links are fine
    M = [[0.5, 0.4, 0.0, 0.0],
         [0.4, 0.5, 0.005, 0.0],
         [0.0, 0.005, 0.5, 0.4],
         [0.0, 0.0, 0.4, 0.5]]
    r = cv.overlap_matrix_bottleneck(M)
    assert r["connected"] is False
    assert r["bottleneck_pair"] == [1, 2]
    assert r["min_adjacent_overlap"] < cv.OVERLAP_BOTTLENECK_MIN


def test_bottleneck_uses_min_of_both_directions():
    # asymmetric overlap: the WEAKER direction defines the link strength
    M = [[0.5, 0.4], [0.001, 0.5]]
    r = cv.overlap_matrix_bottleneck(M)
    assert abs(r["min_adjacent_overlap"] - 0.001) < 1e-12
    assert r["connected"] is False


def test_bottleneck_handles_degenerate_input():
    assert cv.overlap_matrix_bottleneck([[1.0]])["connected"] is None
    assert cv.overlap_matrix_bottleneck(None)["connected"] is None


# --- dG(t) block plateau ----------------------------------------------------------------------------------
def test_block_plateau_flat_tail_passes():
    r = cv.block_plateau_flags(dg_full=-5.0, dg_final_half=-5.1, dg_q3=-5.05, dg_q4=-5.15)
    assert r["plateau_full_vs_half_ok"] is True
    assert r["quarter_block_ok"] is True


def test_block_plateau_drifting_tail_fails():
    r = cv.block_plateau_flags(dg_full=-5.0, dg_final_half=-6.2, dg_q3=-5.5, dg_q4=-7.0)
    assert r["plateau_full_vs_half_ok"] is False        # |−5.0 − (−6.2)| = 1.2 > 0.5
    assert r["quarter_block_ok"] is False               # |−5.5 − (−7.0)| = 1.5 > 0.5


def test_block_plateau_none_when_unavailable():
    r = cv.block_plateau_flags(dg_full=None, dg_final_half=-5.0, dg_q3=None, dg_q4=-5.0)
    assert r["plateau_full_vs_half_ok"] is None
    assert r["quarter_block_ok"] is None


def test_block_plateau_boundary_exact():
    # exactly at the 0.5 threshold -> passes (<=)
    r = cv.block_plateau_flags(dg_full=-5.0, dg_final_half=-5.5, dg_q3=-5.0, dg_q4=-5.5)
    assert r["plateau_full_vs_half_ok"] is True
    assert r["quarter_block_ok"] is True
