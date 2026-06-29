"""Tests for release_frame_select — the pure receptor-frame selection behind the Step-0 re-anchor.

These prove the druggable sub-ensemble selection (primary = closest-to-target-Rg druggable frame;
alternates spread over the breathing range; threshold relaxation; loud-empty on no druggable frame) is
correct without mdtraj/fpocket/numpy/a trajectory (TESTING.md #3: the SageMaker job runs this tested code).
"""
import release_frame_select as rfs


def _rec(rep, frame, rg, drug):
    return {"rep": rep, "frame": frame, "rg": rg, "druggability": drug}


def test_primary_is_closest_druggable_to_target_not_the_peak():
    # Peak druggability (0.84) is at Rg 0.90 (far from target); a 0.60-druggable frame sits right at the
    # target Rg. Primary must be the representative target-Rg frame, NOT the extreme-value peak (red-team F2).
    recs = [
        _rec(0, 10, 0.737, 0.60),   # at target Rg, druggable
        _rec(0, 20, 0.900, 0.84),   # peak druggability but far-open outlier
        _rec(0, 30, 0.600, 0.20),   # not druggable
    ]
    out = rfs.select_receptor_ensemble(recs, d_star=0.53, target_rg=0.737, n_alt=2)
    assert out["primary"]["frame"] == 10
    assert out["n_druggable"] == 2
    assert out["relaxed"] is False


def test_alternates_spread_over_rg_range():
    # Four druggable frames clustered + one far; with n_alt=2 the alternates should sample the spread,
    # picking the far frame, not two near-duplicates of the primary.
    recs = [
        _rec(0, 1, 0.735, 0.55),
        _rec(0, 2, 0.738, 0.56),
        _rec(0, 3, 0.740, 0.57),
        _rec(0, 4, 0.820, 0.54),   # the outlier in Rg — should be picked as an alternate
    ]
    out = rfs.select_receptor_ensemble(recs, d_star=0.53, target_rg=0.737, n_alt=2)
    assert out["primary"]["frame"] in (1, 2)               # closest to 0.737
    alt_frames = {a["frame"] for a in out["alternates"]}
    assert 4 in alt_frames                                 # the Rg outlier is sampled
    assert len(out["alternates"]) == 2


def test_relaxes_to_half_when_nothing_clears_d_star():
    recs = [_rec(0, 1, 0.737, 0.51), _rec(0, 2, 0.740, 0.50)]
    out = rfs.select_receptor_ensemble(recs, d_star=0.53, target_rg=0.737, n_alt=1)
    assert out["relaxed"] is True
    assert out["d_star_used"] == 0.5
    assert out["primary"] is not None


def test_empty_when_no_druggable_frame():
    recs = [_rec(0, 1, 0.737, 0.20), _rec(0, 2, 0.740, 0.30)]
    out = rfs.select_receptor_ensemble(recs, d_star=0.53, target_rg=0.737, relax_to=0.5)
    assert out["primary"] is None
    assert out["alternates"] == []
    assert out["n_druggable"] == 0
    assert "no release frame" in out["reason"]


def test_records_missing_fields_are_ignored():
    recs = [
        {"rep": 0, "frame": 1, "rg": None, "druggability": 0.6},   # no rg
        {"rep": 0, "frame": 2, "rg": 0.737, "druggability": None}, # no drug
        _rec(0, 3, 0.737, 0.60),
    ]
    out = rfs.select_receptor_ensemble(recs, d_star=0.53, target_rg=0.737)
    assert out["n_usable"] == 1
    assert out["primary"]["frame"] == 3


def test_n_alt_zero_returns_only_primary():
    recs = [_rec(0, 1, 0.737, 0.60), _rec(0, 2, 0.760, 0.58)]
    out = rfs.select_receptor_ensemble(recs, d_star=0.53, target_rg=0.737, n_alt=0)
    assert out["primary"] is not None
    assert out["alternates"] == []


def test_alternates_capped_when_few_druggable():
    recs = [_rec(0, 1, 0.737, 0.60), _rec(0, 2, 0.760, 0.58)]
    out = rfs.select_receptor_ensemble(recs, d_star=0.53, target_rg=0.737, n_alt=5)
    assert len(out["alternates"]) == 1     # only one other druggable frame exists


def test_selection_is_deterministic():
    recs = [_rec(0, 5, 0.737, 0.60), _rec(1, 7, 0.737, 0.60), _rec(0, 9, 0.900, 0.84)]
    a = rfs.select_receptor_ensemble(recs, d_star=0.53, target_rg=0.737, n_alt=2)
    b = rfs.select_receptor_ensemble(recs, d_star=0.53, target_rg=0.737, n_alt=2)
    assert rfs._key(a["primary"]) == rfs._key(b["primary"])
    assert [rfs._key(x) for x in a["alternates"]] == [rfs._key(x) for x in b["alternates"]]


def test_rg_span():
    recs = [_rec(0, 1, 0.70, 0.6), _rec(0, 2, 0.82, 0.5), {"rep": 0, "frame": 3, "druggability": 0.4}]
    assert rfs.rg_span(recs) == (0.70, 0.82)
    assert rfs.rg_span([]) == (None, None)
