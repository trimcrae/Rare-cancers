"""Unit tests for the PURE logic of nr4a3_8xtt_abfe_receptor.

No mdtraj / fpocket / smina / rdkit / biopython / network — _rep_index (filename parse),
seed_rg_from_summary (release-summary parse), and select_abfe_frame (the most-druggable-persistent-frame
selection) are dependency-free. The dock/pocket/MD glue is validated only in the AWS job.
"""
import pytest

import nr4a3_8xtt_abfe_receptor as ar


# ------------------------------------------------------------------ _rep_index

def test_rep_index_parses_rep_not_8xtt_or_offset():
    # a plain digit-join would fold the '8' of 8xtt and the '_from0' offset into the number.
    assert ar._rep_index("8xtt_release_rep0_from0.dcd") == 0
    assert ar._rep_index("8xtt_release_rep2_from0.dcd") == 2
    assert ar._rep_index("/opt/ml/input/8xtt_release_rep11_from50.dcd") == 11


def test_rep_index_no_token_zero():
    assert ar._rep_index("whatever.dcd") == 0


# ------------------------------------------------------------------ seed_rg_from_summary

def test_seed_rg_from_top_level():
    assert ar.seed_rg_from_summary({"seed_Rg_nm": 0.742}) == pytest.approx(0.742)


def test_seed_rg_from_replica_fallback():
    s = {"replicas": [{"seed_Rg": 0.73}, {"seed_Rg": 0.73}]}
    assert ar.seed_rg_from_summary(s) == pytest.approx(0.73)


def test_seed_rg_none_when_absent():
    assert ar.seed_rg_from_summary({"replicas": []}) is None
    assert ar.seed_rg_from_summary(None) is None


# ------------------------------------------------------------------ select_abfe_frame

def _rec(rep, frame, rg, drug, dcd="8xtt_release_rep0_from0.dcd"):
    return {"dcd": dcd, "rep": rep, "frame": frame, "rg": rg, "druggability": drug}


def test_selects_most_druggable_persistent_frame():
    recs = [
        _rec(0, 1, 0.74, 0.55),   # druggable + persistent
        _rec(0, 2, 0.75, 0.80),   # druggable + persistent + MOST druggable -> chosen
        _rec(0, 3, 0.73, 0.40),   # not druggable
    ]
    sel = ar.select_abfe_frame(recs, seed_rg=0.74, d_star=0.53, rg_tol=0.1)
    assert sel["primary"]["frame"] == 2
    assert sel["relaxed"] is False and sel["rg_relaxed"] is False
    assert sel["n_druggable"] == 2 and sel["n_candidates"] == 2


def test_persistence_filters_out_far_rg_even_if_more_druggable():
    recs = [
        _rec(0, 1, 0.74, 0.60),   # persistent, druggable
        _rec(0, 2, 1.20, 0.95),   # MORE druggable but far from seed Rg -> excluded by persistence band
    ]
    sel = ar.select_abfe_frame(recs, seed_rg=0.74, d_star=0.53, rg_tol=0.1)
    assert sel["primary"]["frame"] == 1
    assert sel["n_candidates"] == 1
    assert sel["rg_relaxed"] is False


def test_rg_band_relaxes_when_no_druggable_frame_is_persistent():
    # druggable frames exist but none within the band -> take best druggable, flag rg_relaxed.
    recs = [_rec(0, 1, 1.10, 0.70), _rec(0, 2, 1.30, 0.90)]
    sel = ar.select_abfe_frame(recs, seed_rg=0.74, d_star=0.53, rg_tol=0.1)
    assert sel["rg_relaxed"] is True
    assert sel["primary"]["frame"] == 2       # most druggable among the (relaxed) druggable set


def test_relax_dstar_to_half_when_none_clear_dstar():
    recs = [_rec(0, 1, 0.74, 0.51), _rec(0, 2, 0.75, 0.49)]
    sel = ar.select_abfe_frame(recs, seed_rg=0.74, d_star=0.53, rg_tol=0.1, relax_to=0.5)
    assert sel["relaxed"] is True
    assert sel["d_star_used"] == pytest.approx(0.5)
    assert sel["primary"]["frame"] == 1       # 0.51 >= 0.5, the only one above the relaxed cutoff


def test_none_when_no_druggable_at_all():
    recs = [_rec(0, 1, 0.74, 0.30), _rec(0, 2, 0.75, 0.20)]
    sel = ar.select_abfe_frame(recs, seed_rg=0.74, d_star=0.53, rg_tol=0.1, relax_to=0.5)
    assert sel["primary"] is None
    assert "no release frame reached druggability" in sel["reason"]


def test_ignores_records_missing_rg_or_druggability():
    recs = [
        {"dcd": "d", "rep": 0, "frame": 1, "rg": None, "druggability": 0.9},
        {"dcd": "d", "rep": 0, "frame": 2, "rg": 0.74, "druggability": None},
        _rec(0, 3, 0.74, 0.60),
    ]
    sel = ar.select_abfe_frame(recs, seed_rg=0.74, d_star=0.53, rg_tol=0.1)
    assert sel["n_usable"] == 1
    assert sel["primary"]["frame"] == 3


def test_no_seed_rg_skips_persistence_filter():
    recs = [_rec(0, 1, 0.74, 0.60), _rec(0, 2, 2.0, 0.90)]
    sel = ar.select_abfe_frame(recs, seed_rg=None, d_star=0.53, rg_tol=0.1)
    assert sel["primary"]["frame"] == 2       # no band -> most druggable wins
    assert sel["rg_relaxed"] is False


def test_tie_break_prefers_closest_rg_to_seed():
    # equal druggability -> the frame whose Rg is closest to the seed wins.
    recs = [_rec(0, 1, 0.70, 0.80), _rec(0, 2, 0.745, 0.80)]
    sel = ar.select_abfe_frame(recs, seed_rg=0.74, d_star=0.53, rg_tol=0.1)
    assert sel["primary"]["frame"] == 2
