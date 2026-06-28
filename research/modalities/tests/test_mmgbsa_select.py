"""Tests for mmgbsa_select — the pure MM-GBSA selectivity-rescoring logic (no deps)."""
import mmgbsa_select as ms


def test_margins_sign_and_min():
    # NR4A3 tighter (more negative) than both paralogues -> positive margins; min is the smaller.
    r = ms.margins(dg3=-40.0, dg1=-35.0, dg2=-38.0)
    assert r["margin_vs_NR4A1"] == 5.0
    assert r["margin_vs_NR4A2"] == 2.0
    assert r["min_margin"] == 2.0          # must beat BOTH; worst case is NR4A2


def test_margins_missing_leg():
    r = ms.margins(dg3=-40.0, dg1=None, dg2=-38.0)
    assert r["margin_vs_NR4A1"] is None
    assert r["margin_vs_NR4A2"] == 2.0
    assert r["min_margin"] == 2.0          # only the present paralogue counts
    assert ms.margins(dg3=None, dg1=-1.0, dg2=-2.0)["min_margin"] is None


def test_verdict_confirmed_selective():
    # docking said selective (+1.4) and MM-GBSA strongly agrees (+3 > band) -> confirmed.
    assert ms.verdict(dock_min_margin=1.4, mm_min_margin=3.0) == "confirmed_selective"


def test_verdict_reversed():
    # docking said selective but MM-GBSA prefers a paralogue by > band -> reversed (the cytosporone-B risk).
    assert ms.verdict(dock_min_margin=1.16, mm_min_margin=-2.5) == "reversed"


def test_verdict_weakened_inside_band():
    assert ms.verdict(dock_min_margin=1.16, mm_min_margin=0.4) == "weakened"
    assert ms.verdict(dock_min_margin=1.16, mm_min_margin=-0.4) == "weakened"


def test_verdict_rescued():
    assert ms.verdict(dock_min_margin=-0.5, mm_min_margin=2.0) == "rescued"


def test_verdict_confirmed_nonselective_and_incomplete():
    assert ms.verdict(dock_min_margin=-0.5, mm_min_margin=-2.0) == "confirmed_nonselective"
    assert ms.verdict(dock_min_margin=None, mm_min_margin=2.0) == "incomplete"
    assert ms.verdict(dock_min_margin=1.0, mm_min_margin=None) == "incomplete"


def test_band_is_configurable():
    # widen the band -> a +1.5 margin no longer counts as a confident preference.
    assert ms.verdict(1.4, 1.5) == "confirmed_selective"
    assert ms.verdict(1.4, 1.5, band=2.0) == "weakened"


def test_rank_rows_orders_selective_first_nones_last():
    rows = [{"label": "a", "mm_min_margin": -1.0}, {"label": "b", "mm_min_margin": 3.0},
            {"label": "c", "mm_min_margin": None}, {"label": "d", "mm_min_margin": 0.5}]
    order = [r["label"] for r in ms.rank_rows(rows)]
    assert order == ["b", "d", "a", "c"]


def test_census_counts_by_verdict():
    rows = [{"verdict": "confirmed_selective"}, {"verdict": "reversed"},
            {"verdict": "confirmed_selective"}, {"verdict": "incomplete"}]
    c = ms.census(rows)
    assert c == {"confirmed_selective": 2, "reversed": 1, "incomplete": 1}
