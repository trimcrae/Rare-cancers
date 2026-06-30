"""Tests for selectivity_calibration — the decoy-calibrated NR4A3-selectivity threshold."""
import selectivity_calibration as sc


DECOY = [16.46, 13.21, 13.10, 9.75, 9.73, 9.50, 9.30, 5.32, 5.17, 5.15, 4.43, 4.41, 3.42, 3.08, 2.76,
         2.46, 1.32, 1.11, 0.69, 0.32, 0.21, 0.09, -0.75, -2.74, -2.77, -3.41, -3.44, -3.52, -3.56,
         -3.81, -3.95, -4.38, -5.43, -5.72, -5.79, -6.51, -8.46, -8.89]


def test_percentile_basic():
    assert sc.percentile([1, 2, 3, 4, 5], 0) == 1.0
    assert sc.percentile([1, 2, 3, 4, 5], 100) == 5.0
    assert sc.percentile([1, 2, 3, 4, 5], 50) == 3.0
    assert sc.percentile([], 50) is None


def test_decoy_threshold_95th():
    thr = sc.decoy_threshold(DECOY, 95)
    assert 12.5 < thr < 14.0          # ~13.1 for this null


def test_denovo_111_clears_bar_others_dont():
    v111 = sc.calibrated_verdict(15.70, DECOY)
    assert v111["above_null"] is True
    assert v111["n_decoys_above"] == 1            # only celecoxib (16.46) beats it
    for m in (10.50, -0.19, -0.82):               # denovo_67, denovo_0, denovo_57
        assert sc.calibrated_verdict(m, DECOY)["above_null"] is False


def test_rank_orders_and_flags():
    cands = [{"label": "a", "margin": -0.2}, {"label": "b", "margin": 15.7}, {"label": "c", "margin": 10.5}]
    ranked = sc.rank_against_null(cands, DECOY)
    assert [r["label"] for r in ranked] == ["b", "c", "a"]
    assert ranked[0]["above_null"] is True
    assert ranked[1]["above_null"] is False
