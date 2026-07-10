"""Unit tests for the cross-replica metad F(Rg) reducer (round-4 comments 4/7)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nr4a3_metad_crossreplica as cr  # noqa: E402


def _profile(basin_rg, basin_F, drug_F, front_F):
    """Synthetic F(Rg): flat except a basin, a druggable point (0.72), a frontier point (1.06)."""
    prof = [[round(0.40 + 0.01 * i, 2), 100.0] for i in range(200)]  # Rg 0.40..2.39, high plateau
    for p in prof:
        if abs(p[0] - basin_rg) < 1e-6:
            p[1] = basin_F
        elif abs(p[0] - 0.72) < 1e-6:
            p[1] = drug_F
        elif abs(p[0] - 1.06) < 1e-6:
            p[1] = front_F
    return prof


def test_delta_f_basin_at_druggable_is_cheap():
    # basin at 0.73, druggable point low too → small ΔF
    prof = _profile(0.73, 0.0, 2.0, 160.0)  # 2 kJ ≈ 0.48 kcal
    brg, bF, dd, df = cr.replica_delta_f(prof)
    assert brg == 0.73 and bF == 0.0
    assert abs(dd - 2.0 / 4.184) < 1e-6
    assert df > 30  # frontier far uphill


def test_delta_f_open_basin_makes_druggable_uphill():
    # basin at 0.87 (open side), druggable point at 0.72 high → large ΔF (the r1-like case)
    prof = _profile(0.87, 0.0, 67.0, 200.0)  # 67 kJ ≈ 16 kcal
    brg, bF, dd, df = cr.replica_delta_f(prof)
    assert brg == 0.87
    assert dd > 15  # druggable region is many kcal/mol above the open basin


def test_spread_flags_disagreement():
    assert cr._spread([0.06, 0.83, 16.03]) > 15
    assert cr._spread([0.5, 0.6, 0.7]) < 1
