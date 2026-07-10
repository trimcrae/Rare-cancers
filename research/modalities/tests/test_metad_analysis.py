import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import nr4a3_metad_analysis as A  # noqa: E402


# --------------------------------------------------------------------------------------------------
# parsers
# --------------------------------------------------------------------------------------------------
def test_parse_hills_skips_comments_and_short_lines(tmp_path):
    p = tmp_path / "HILLS"
    p.write_text("#! FIELDS time rg sigma_rg height biasf\n"
                 "1.0 0.50 0.03 1.0 10\n"
                 "\n"
                 "2.0 0.60 0.03 0.8 10\n"
                 "3.0 0.70\n")   # truncated tail (spot kill) -> dropped
    hs = A.parse_hills(str(p))
    assert len(hs) == 2
    assert hs[0] == {"time": 1.0, "center": 0.50, "sigma": 0.03, "height": 1.0, "biasfactor": 10.0}
    assert hs[1]["center"] == 0.60


def test_parse_colvar_columns(tmp_path):
    p = tmp_path / "COLVAR"
    p.write_text("#! FIELDS time rg metad.bias\n"
                 "0.0 0.48 0.0\n1.0 0.55 3.5\n2.0 0.62 7.1\n")
    times, rg, bias = A.parse_colvar(str(p))
    assert times == [0.0, 1.0, 2.0]
    assert rg == [0.48, 0.55, 0.62]
    assert bias == [0.0, 3.5, 7.1]


# --------------------------------------------------------------------------------------------------
# reconstruct_fes: a single well-tempered hill makes a well at its centre with the (gamma/(gamma-1))
# depth relative to the far edge
# --------------------------------------------------------------------------------------------------
def test_reconstruct_fes_single_hill_well_at_centre():
    hills = [{"time": 1.0, "center": 0.75, "sigma": 0.05, "height": 2.0, "biasfactor": 10.0}]
    fes = A.reconstruct_fes(hills, 0.45, 1.05, 60)
    assert fes, "expected a non-empty profile"
    # zeroed at the minimum
    assert min(f for _, f in fes) == 0.0
    # minimum sits at the hill centre
    rg_at_min = min(fes, key=lambda p: p[1])[0]
    assert abs(rg_at_min - 0.75) < 0.02
    # far from the centre the Gaussian ~0 so F ~ (gamma/(gamma-1))*height above the basin
    far = max(fes, key=lambda p: p[1])[1]
    assert abs(far - (10.0 / 9.0) * 2.0) < 0.05


def test_reconstruct_fes_upto_time_truncates():
    hills = [{"time": 1.0, "center": 0.6, "sigma": 0.05, "height": 1.0, "biasfactor": 10.0},
             {"time": 5.0, "center": 0.9, "sigma": 0.05, "height": 1.0, "biasfactor": 10.0}]
    early = A.reconstruct_fes(hills, 0.45, 1.05, 60, upto_time=2.0)   # only the 0.6 hill
    rg_min = min(early, key=lambda p: p[1])[0]
    assert abs(rg_min - 0.6) < 0.02
    assert A.reconstruct_fes(hills, 0.45, 1.05, 60, upto_time=0.5) == []


def test_reconstruct_fes_nontempered_factor_one():
    # biasfactor 0/absent -> factor 1 (plain metad); depth == height
    hills = [{"time": 1.0, "center": 0.7, "sigma": 0.05, "height": 3.0, "biasfactor": 0.0}]
    fes = A.reconstruct_fes(hills, 0.45, 1.05, 60)
    assert abs(max(f for _, f in fes) - 3.0) < 0.05


# --------------------------------------------------------------------------------------------------
# block convergence
# --------------------------------------------------------------------------------------------------
def test_block_fes_and_convergence_shrinks():
    # deposit hills that build a well and then only refine it -> block-to-block |dF| shrinks
    hills = []
    t = 0.0
    for _ in range(300):                    # 300 ps of 1 ps hills spread across the basin
        t += 1.0
        hills.append({"time": t, "center": 0.75, "sigma": 0.05, "height": 0.2, "biasfactor": 10.0})
    blocks = A.block_fes(hills, block_ns=0.1, grid_min=0.45, grid_max=1.05, grid_bin=60,
                         ns_per_time_unit=1.0 / 1000.0)
    ends = sorted(blocks)
    assert len(ends) >= 3                    # 0.1, 0.2, 0.3 ns blocks
    conv = A.block_convergence(blocks, region=(0.45, 1.05))
    # later block-to-block change should be <= earlier (converging)
    assert conv[-1]["max_dF_kJ"] <= conv[0]["max_dF_kJ"] + 1e-6
    assert conv[-1]["rmsd_kJ"] is not None


def test_fes_difference_ignores_constant_offset():
    a = [(0.5, 0.0), (0.7, -10.0), (0.9, 0.0)]
    b = [(0.5, 5.0), (0.7, -5.0), (0.9, 5.0)]     # identical shape, +5 offset
    d = A.fes_difference(a, b)
    assert d["max_dF_kJ"] == 0.0
    assert d["mean_dF_kJ"] == 0.0


def test_fes_difference_region_filter():
    a = [(0.5, 0.0), (0.7, 0.0), (2.0, 0.0)]
    b = [(0.5, 0.0), (0.7, 0.0), (2.0, 50.0)]     # differ only outside the region
    d = A.fes_difference(a, b, region=(0.45, 0.8))
    assert d["max_dF_kJ"] == 0.0
    assert d["n_points"] == 2


# --------------------------------------------------------------------------------------------------
# recrossings
# --------------------------------------------------------------------------------------------------
def test_count_boundary_crossings_basic():
    # below, above, below, above -> 3 crossings
    series = [0.5, 1.0, 0.5, 1.0]
    assert A.count_boundary_crossings(series, boundary=0.75) == 3


def test_count_boundary_crossings_deadband_filters_chatter():
    # oscillation entirely inside the deadband around 0.75 -> 0 crossings
    series = [0.74, 0.76, 0.74, 0.76]
    assert A.count_boundary_crossings(series, boundary=0.75, deadband=0.05) == 0
    # a real excursion below then above the band -> 1 crossing
    series2 = [0.60, 0.90]
    assert A.count_boundary_crossings(series2, boundary=0.75, deadband=0.05) == 1


def test_count_region_visits():
    series = [0.4, 0.8, 0.9, 0.4, 0.85, 0.4]   # two separate excursions into [0.7,1.0]
    r = A.count_region_visits(series, 0.7, 1.0)
    assert r["visits"] == 2
    assert r["n"] == 6
    assert abs(r["frac_inside"] - 3 / 6) < 1e-9


# --------------------------------------------------------------------------------------------------
# gate distance geometry
# --------------------------------------------------------------------------------------------------
def test_centroid_and_distance():
    assert A.centroid([(0, 0, 0), (2, 0, 0)]) == (1.0, 0.0, 0.0)
    assert abs(A.distance((0, 0, 0), (3, 4, 0)) - 5.0) < 1e-9


def test_gate_distance_series_widens():
    # group A fixed at origin cluster; group B moves away frame to frame -> gate grows
    a_frames = [[(0.0, 0.0, 0.0), (0.0, 0.2, 0.0)] for _ in range(3)]
    b_frames = [[(1.0, 0.0, 0.0), (1.0, 0.2, 0.0)],
                [(2.0, 0.0, 0.0), (2.0, 0.2, 0.0)],
                [(3.0, 0.0, 0.0), (3.0, 0.2, 0.0)]]
    gate = A.gate_distance_series(a_frames, b_frames)
    assert gate[0] < gate[1] < gate[2]
    assert abs(gate[0] - 1.0) < 1e-9


def test_gate_distance_series_length_mismatch_raises():
    try:
        A.gate_distance_series([[(0, 0, 0)]], [])
    except ValueError:
        return
    raise AssertionError("expected ValueError on mismatched frame counts")


# --------------------------------------------------------------------------------------------------
# time matching + 2D reweight
# --------------------------------------------------------------------------------------------------
def test_match_series_by_time_nearest():
    ref_t = [0.0, 1.0, 2.0, 3.0]
    ref_v = [10, 11, 12, 13]
    got = A.match_series_by_time([0.0, 0.4, 0.6, 2.9], ref_t, ref_v)
    assert got == [10, 10, 11, 13]
    assert A.match_series_by_time([5.0], [], []) == [None]


def test_reweight_2d_locates_min_at_high_weight_cell():
    # a tight cluster with high bias -> deepest (0) free energy there; a sparse low-bias cluster higher
    samples = []
    for _ in range(50):
        samples.append((0.75, 1.2, 8.0))    # high weight cluster
    for _ in range(50):
        samples.append((0.50, 0.9, 0.0))    # low weight cluster
    rw = A.reweight_2d(samples, kT=2.5, x_bins=10, y_bins=10)
    assert rw["n_samples"] == 100
    # find the (x,y) of the global minimum cell
    best = None
    for iy, row in enumerate(rw["F"]):
        for ix, v in enumerate(row):
            if v is not None and (best is None or v < best[0]):
                best = (v, ix, iy)
    assert best[0] == 0.0
    xc = 0.5 * (rw["x_edges"][best[1]] + rw["x_edges"][best[1] + 1])
    yc = 0.5 * (rw["y_edges"][best[2]] + rw["y_edges"][best[2] + 1])
    assert abs(xc - 0.75) < 0.1 and abs(yc - 1.2) < 0.1


def test_reweight_2d_drops_missing_bias():
    samples = [(0.5, 1.0, None), (0.6, 1.1, 2.0)]
    rw = A.reweight_2d(samples, kT=2.5, x_bins=4, y_bins=4)
    assert rw["n_samples"] == 1


def test_reweight_2d_empty():
    rw = A.reweight_2d([], kT=2.5, x_bins=4, y_bins=4)
    assert rw["n_samples"] == 0
    assert rw["F"] == []
