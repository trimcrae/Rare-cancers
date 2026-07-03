import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import report_metad as rm  # noqa: E402


def _synth_single_basin():
    # V-shaped single well: min at rg=0.75, rising both sides (mimics the real 60 ns fes.dat shape)
    pts = []
    rg = 0.45
    while rg <= 1.18:
        f = 180.0 * (abs(rg - 0.75) / 0.30) ** 1.4 - 184.0   # min ~-184 at 0.75, ~0 at the edges
        pts.append((round(rg, 4), round(f, 3)))
        rg += 0.0106
    return pts


def test_parse_fes_skips_comments(tmp_path):
    p = tmp_path / "fes.dat"
    p.write_text("#! FIELDS rg file.free der_rg\n#! SET min_rg 0.45\n"
                 "0.5 -10.0 1.0\n0.7 -50.0 2.0\n\n0.9 -20.0 3.0\n")
    pts = rm.parse_fes(str(p))
    assert pts == [(0.5, -10.0), (0.7, -50.0), (0.9, -20.0)]


def test_single_basin_detected():
    r = rm.analyze(_synth_single_basin(), druggable_rg=0.72, frontier_rg=1.06)
    assert r["single_basin"] is True
    assert r["separate_opened_minima_rg"] == []
    assert 0.73 <= r["basin_min"]["rg_nm"] <= 0.77
    # ΔG to a near-basin druggable Rg is small; to the open frontier is large
    assert r["dG_basin_to_druggable_frame"]["dG_kcal"] < r["dG_basin_to_open_frontier"]["dG_kcal"]
    assert r["dG_basin_to_open_frontier"]["dG_kcal"] > 10


def test_two_state_detected():
    # explicit double well: minima at 0.5 (-50) and 1.0 (-40), barrier +10 between at 0.75
    pts = [(0.4, 0.0), (0.5, -50.0), (0.6, -20.0), (0.75, 10.0), (0.9, -20.0), (1.0, -40.0), (1.1, 0.0)]
    r = rm.analyze(pts, druggable_rg=0.9, frontier_rg=1.0, min_prominence=5.0)
    assert r["single_basin"] is False
    assert any(abs(x - 1.0) < 1e-6 for x in r["separate_opened_minima_rg"])


def test_real_60ns_profile_if_present():
    # if the committed 60 ns fes.dat is available, sanity-check the paper-cited shape
    here = os.path.dirname(__file__)
    for cand in ("../metad-fes-60ns.dat", "../nr4a3-metad-fes.dat"):
        path = os.path.join(here, cand)
        if os.path.exists(path):
            r = rm.analyze(rm.parse_fes(path))
            assert r["single_basin"] is True
            assert 0.72 <= r["basin_min"]["rg_nm"] <= 0.78
            return
