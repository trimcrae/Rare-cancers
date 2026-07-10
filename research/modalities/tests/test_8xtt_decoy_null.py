"""Unit tests for the PURE logic of nr4a3_8xtt_decoy_null (the MATCHED 8XTT-frame decoy null).

No smina / openmm / rdkit / biopython / network — percentile_rank, empirical_p_add_one, decoy_null_verdict,
collect_decoy_margins / collect_pooled_margins, denovo401_margins_from_redock, and summarize_null are all
dependency-free. The heavy dock/MM-GBSA glue is validated only in the AWS job.

The denovo_401 fixtures below are the ARCHIVED re-dock margins (results/nr4a3-8xtt-redock/...): they are
INPUTS to the pure ranking functions, not fabricated results.
"""
import pytest

import nr4a3_8xtt_decoy_null as dn


# denovo_401's archived per-conformer MM-GBSA min-margins (kcal/mol): models 2/8/20/6.
DENOVO_401 = {2: 6.83, 8: 13.65, 20: 7.77, 6: 11.06}
MODELS = [2, 8, 20, 6]


# ------------------------------------------------------------------ percentile_rank

def test_percentile_rank_strictly_below():
    # 3 of 5 strictly below 10 -> 60%
    assert dn.percentile_rank(10.0, [1, 2, 3, 20, 30]) == 60.0


def test_percentile_rank_top_of_null():
    assert dn.percentile_rank(100.0, [1, 2, 3]) == 100.0


def test_percentile_rank_ties_not_counted_below():
    # ties are NOT strictly below -> 0% below when value equals every null point
    assert dn.percentile_rank(5.0, [5, 5, 5, 5]) == 0.0


def test_percentile_rank_empty_or_none():
    assert dn.percentile_rank(1.0, []) is None
    assert dn.percentile_rank(None, [1, 2]) is None


# ------------------------------------------------------------------ empirical_p_add_one

def test_empirical_p_add_one_best_in_class():
    # nothing >= 100 -> p = (0+1)/(4+1) = 0.2 (conservative floor, never 0)
    assert dn.empirical_p_add_one(100.0, [1, 2, 3, 4]) == 0.2


def test_empirical_p_add_one_counts_ge():
    # two decoys >= 3 (the 3 and the 9) -> (2+1)/(4+1)=0.6
    assert dn.empirical_p_add_one(3.0, [1, 2, 3, 9]) == 0.6


def test_empirical_p_add_one_monotone_and_bounded():
    null = [-5, 0, 5, 10, 15]
    p_hi = dn.empirical_p_add_one(20.0, null)
    p_lo = dn.empirical_p_add_one(-10.0, null)
    assert p_hi < p_lo
    assert 0.0 < p_hi <= 1.0 and 0.0 < p_lo <= 1.0


def test_empirical_p_add_one_empty_or_none():
    assert dn.empirical_p_add_one(1.0, []) is None
    assert dn.empirical_p_add_one(None, [1]) is None


# ------------------------------------------------------------------ decoy_null_verdict

def test_verdict_above_null_when_beats_95th_bar():
    # a tight decoy null near 0; denovo_401 margin +7 clears the 95th-pct bar
    decoys = [0.1, -0.5, 1.2, 0.3, -1.0, 0.8, -0.2, 0.6, 0.0, -0.7]
    v = dn.decoy_null_verdict(7.0, decoys, band=1.0, q=95.0)
    assert v["verdict"] == "above-null"
    assert v["pass_95th"] is True
    assert v["n_decoys_above"] == 0
    assert v["percentile_rank"] == 100.0
    assert v["decoy_95th_bar"] is not None and 7.0 > v["decoy_95th_bar"]


def test_verdict_within_null_when_inside_distribution():
    # a WIDE decoy null (frame inflation) swallows a +9 margin
    decoys = [16.0, 13.0, 12.0, 9.5, 9.0, 8.0, 5.0, 1.0, -3.0, -8.0]
    v = dn.decoy_null_verdict(9.0, decoys, band=1.0, q=95.0)
    assert v["verdict"] == "within-null"
    assert v["pass_95th"] is False
    assert v["n_decoys_above"] >= 3          # several decoys score at least as NR4A3-favoured
    assert 0.0 < v["empirical_p_add_one"] <= 1.0


def test_verdict_no_data_on_empty_null():
    v = dn.decoy_null_verdict(9.0, [], band=1.0, q=95.0)
    assert v["verdict"] == "no-data"
    assert v["n_decoys"] == 0
    assert v["pass_95th"] is None


def test_verdict_no_data_on_missing_denovo_margin():
    v = dn.decoy_null_verdict(None, [1.0, 2.0, 3.0], band=1.0, q=95.0)
    assert v["verdict"] == "no-data"
    assert v["percentile_rank"] is None


# ------------------------------------------------------------------ collect_decoy_margins / pooled

_ROWS = [
    {"name": "decoy_a", "per_conformer": {"2": 1.0, "8": 2.0, "20": None, "6": 4.0}},
    {"name": "decoy_b", "per_conformer": {"2": -1.0, "8": 3.0, "20": 5.0, "6": 6.0}},
    {"name": "decoy_c", "per_conformer": {"2": 0.5}},                       # missing 8/20/6
]


def test_collect_decoy_margins_skips_none_and_missing():
    assert dn.collect_decoy_margins(_ROWS, 2) == [1.0, -1.0, 0.5]
    assert dn.collect_decoy_margins(_ROWS, 20) == [5.0]                     # a's 20 is None, c has none
    assert dn.collect_decoy_margins(_ROWS, 8) == [2.0, 3.0]


def test_collect_pooled_margins_flattens_all_conformers():
    pooled = dn.collect_pooled_margins(_ROWS, [2, 8, 20, 6])
    assert sorted(pooled) == sorted([1.0, 2.0, 4.0, -1.0, 3.0, 5.0, 6.0, 0.5])


# ------------------------------------------------------------------ denovo401_margins_from_redock

def test_denovo401_margins_from_redock_parses_archived_shape():
    redock = {"per_conformer": [
        {"model": 2, "mm_min_margin": 6.83},
        {"model": 8, "mm_min_margin": 13.65},
        {"model": 20, "mm_min_margin": 7.77},
        {"model": 6, "mm_min_margin": 11.06},
    ]}
    out = dn.denovo401_margins_from_redock(redock)
    assert out["per_conformer"] == DENOVO_401
    assert out["median"] == pytest.approx(9.415)                            # matches the archived summary


def test_denovo401_margins_from_redock_fail_loud_when_no_margin():
    with pytest.raises(ValueError):
        dn.denovo401_margins_from_redock({"per_conformer": [{"model": 2, "mm_min_margin": None}]})


# ------------------------------------------------------------------ summarize_null (end-to-end pure)

def _decoy_rows_near_zero():
    """A MATCHED-null scenario where the 8XTT frame does NOT inflate decoy margins (decoys cluster near 0),
    so denovo_401's +7..+14 margins clear the bar in every conformer -> 'above-null'."""
    import random
    rng = random.Random(7)
    rows = []
    for i in range(38):
        pc = {str(m): round(rng.uniform(-2.0, 2.0), 2) for m in MODELS}
        rows.append({"name": f"decoy_{i}", "per_conformer": pc})
    return rows


def _decoy_rows_inflated():
    """A frame-INFLATED null (the exact failure the reviewer worries about): decoys routinely score +5..+16
    NR4A3-favoured, swallowing denovo_401's margins -> 'within-null'."""
    import random
    rng = random.Random(11)
    rows = []
    for i in range(38):
        pc = {str(m): round(rng.uniform(3.0, 16.0), 2) for m in MODELS}
        rows.append({"name": f"decoy_{i}", "per_conformer": pc})
    return rows


def test_summarize_null_above_when_null_is_tight():
    s = dn.summarize_null(_decoy_rows_near_zero(), DENOVO_401, MODELS, band=1.0, q=95.0)
    assert s["verdict"] == "above-null"
    assert s["n_conformers_scored"] == 4
    assert s["n_conformers_pass"] == 4
    assert s["pooled"]["pass_95th"] is True
    # every per-conformer verdict present + denovo margin echoed
    assert set(s["per_conformer"].keys()) == {"2", "8", "20", "6"}
    assert s["per_conformer"]["2"]["denovo401_margin"] == 6.83
    assert s["pooled"]["denovo401_margin"] == pytest.approx(9.415)          # denovo pooled = median of its margins


def test_summarize_null_within_when_frame_inflates():
    s = dn.summarize_null(_decoy_rows_inflated(), DENOVO_401, MODELS, band=1.0, q=95.0)
    assert s["verdict"] == "within-null"
    assert s["n_conformers_pass"] == 0
    assert s["pooled"]["pass_95th"] is False
    # this is the whole point: an inflated matched null retracts the naive 'survives' verdict
    assert "INSIDE the decoy null" in s["rationale"]


def test_summarize_null_no_data_when_empty():
    s = dn.summarize_null([], DENOVO_401, MODELS, band=1.0, q=95.0)
    assert s["verdict"] == "no-data"
    assert s["n_conformers_scored"] == 0


def test_summarize_null_mixed_when_some_conformers_pass():
    # Build a null tight in models 2/8 but inflated in 20/6 -> denovo passes some, not a majority-with-pooled.
    import random
    rng = random.Random(3)
    rows = []
    for i in range(38):
        pc = {"2": round(rng.uniform(-2, 2), 2), "8": round(rng.uniform(-2, 2), 2),
              "20": round(rng.uniform(6, 16), 2), "6": round(rng.uniform(6, 16), 2)}
        rows.append({"name": f"decoy_{i}", "per_conformer": pc})
    s = dn.summarize_null(rows, DENOVO_401, MODELS, band=1.0, q=95.0)
    # denovo passes in 2 & 8 (tight null) but not 20 & 6 (inflated) -> 2/4, not a majority -> mixed
    assert s["n_conformers_pass"] == 2
    assert s["verdict"] in ("mixed", "within-null")
    assert s["per_conformer"]["2"]["pass_95th"] is True
    assert s["per_conformer"]["20"]["pass_95th"] is False
