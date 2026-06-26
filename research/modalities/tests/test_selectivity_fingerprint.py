"""Tests for selectivity_fingerprint — the pure NR4A matrix-cell classifier (no deps)."""
import selectivity_fingerprint as sf


def test_nr4a3_only_selective():
    r = sf.classify(dg3=-9.0, dg1=-5.0, dg2=-5.0)
    assert r["engages"] == ["NR4A3"]
    assert r["cell"] == "NR4A3-only"
    assert r["nr4a3_selective"] is True       # margins +4.0 / +4.0 >= 1.0
    assert r["pan_nr4a"] is False
    assert r["anti_target"] is False
    assert "LEAD" in r["application"]


def test_pan_nr4a():
    r = sf.classify(dg3=-9.0, dg1=-8.5, dg2=-8.7)
    assert set(r["engages"]) == {"NR4A1", "NR4A2", "NR4A3"}
    assert r["cell"] == "pan-NR4A"
    assert r["pan_nr4a"] is True              # |margins| 0.5 / 0.3 < 1.0
    assert r["nr4a3_selective"] is False
    assert "ex-vivo" in r["application"]


def test_anti_target_nr4a1_plus_nr4a3_sparing_nr4a2():
    # engages NR4A1 + NR4A3 strongly, NR4A2 not engaged (-5 > -7) -> the AML-risk anti-target cell
    r = sf.classify(dg3=-9.0, dg1=-8.5, dg2=-5.0)
    assert set(r["engages"]) == {"NR4A1", "NR4A3"}
    assert r["cell"] == "NR4A1+NR4A3"
    assert r["anti_target"] is True
    assert "ANTI-TARGET" in r["application"]


def test_none_engaged():
    r = sf.classify(dg3=-5.0, dg1=-4.0, dg2=-4.5)
    assert r["engages"] == []
    assert r["cell"] == "none"
    assert r["anti_target"] is False and r["pan_nr4a"] is False


def test_selectivity_margin_boundary_is_not_selective():
    # NR4A3 engaged but only +0.5 better than a paralogue (< SEL_MARGIN 1.0) -> not called selective
    r = sf.classify(dg3=-8.0, dg1=-7.5, dg2=-5.0)
    assert r["engages"] == ["NR4A1", "NR4A3"]   # NR4A1 also engaged (-7.5 <= -7)
    assert r["nr4a3_selective"] is False
    assert r["margin_vs_NR4A1"] == 0.5


def test_failed_dock_is_not_engaged():
    r = sf.classify(dg3=-9.0, dg1=None, dg2=-5.0)
    assert r["engages"] == ["NR4A3"]
    assert r["margin_vs_NR4A1"] is None
    assert r["nr4a3_selective"] is False        # can't confirm selectivity vs NR4A1 without its dG


def test_matrix_summary_groups_cells():
    rows = [sf.classify(-9, -5, -5), sf.classify(-9, -8.5, -8.7), sf.classify(-9, -8.5, -5)]
    m = sf.matrix_summary(rows)
    assert m["cell_census"]["NR4A3-only"] == 1
    assert m["cell_census"]["pan-NR4A"] == 1
    assert len(m["nr4a3_selective"]) == 1
    assert len(m["pan_nr4a"]) == 1
    assert len(m["anti_targets"]) == 1
