"""Unit tests for the PURE logic of nr4a3_8xtt_pocketminer (the PocketMiner-on-8XTT cross-check).

Everything here runs WITHOUT TensorFlow / mdtraj / biopython / network — analyse_conformer,
aggregate_conformers and select_models are dependency-free (the heavy PocketMiner inference + numbering
alignment glue lives in pocketminer_src/entry_8xtt_pm.py and is exercised only in the AWS job).
"""
import pytest

import nr4a3_8xtt_pocketminer as p8


# ------------------------------------------------------------------ analyse_conformer

def _uniform_map(pocket_authnums):
    """A UniProt->8XTT map where each Pocket-5 UniProt residue maps to itself (author==uniprot), enough
    to exercise the analysis without a real alignment."""
    return {u: u for u in p8.POCKET5}


def test_analyse_conformer_enriched_pocket():
    """Pocket-5 residues scored high, background low -> enrichment > 1, Pocket-5 flagged, frac high > 0."""
    uni_to_auth = _uniform_map(p8.POCKET5)
    scores = {}
    # background LBD residues (author 700..799) low
    for a in range(700, 800):
        scores[a] = 0.05
    # Pocket-5 residues high (author == uniprot via the map)
    for u in p8.POCKET5:
        scores[uni_to_auth[u]] = 0.8
    out = p8.analyse_conformer(scores, uni_to_auth)
    ov = out["overlap"]
    assert ov["n_pocket5_mapped"] == len(p8.POCKET5)
    assert ov["pocket5_mean_score"] == pytest.approx(0.8)
    assert ov["enrichment_pocket5_over_lbd"] > 1.0
    assert ov["frac_pocket5_high"] == pytest.approx(1.0)     # all >= 0.7
    assert ov["frac_pocket5_moderate"] == pytest.approx(1.0)
    # each Pocket-5 residue sits at the top of the ranking
    assert all(v == pytest.approx(max(v for v in out["pocket5_percentile_rank_uniprot"].values()))
               or v > 0.5 for v in out["pocket5_percentile_rank_uniprot"].values())


def test_analyse_conformer_null_pocket():
    """Pocket-5 no different from background -> enrichment ~1, nothing flagged high."""
    uni_to_auth = _uniform_map(p8.POCKET5)
    scores = {a: 0.1 for a in range(700, 800)}
    for u in p8.POCKET5:
        scores[uni_to_auth[u]] = 0.1
    out = p8.analyse_conformer(scores, uni_to_auth)
    ov = out["overlap"]
    assert ov["enrichment_pocket5_over_lbd"] == pytest.approx(1.0)
    assert ov["frac_pocket5_high"] == pytest.approx(0.0)
    assert ov["pocket5_in_flagged_high"] == []


def test_analyse_conformer_partial_map_counts_only_mapped():
    """Only some Pocket-5 residues present in the map/scores -> n_pocket5_mapped reflects that subset."""
    subset = p8.POCKET5[:3]
    uni_to_auth = {u: u for u in subset}
    scores = {a: 0.2 for a in range(700, 760)}
    for u in subset:
        scores[u] = 0.9
    out = p8.analyse_conformer(scores, uni_to_auth)
    assert out["overlap"]["n_pocket5_mapped"] == 3


def test_analyse_conformer_empty():
    out = p8.analyse_conformer({}, {})
    assert out["n_residues_scored"] == 0


# ------------------------------------------------------------------ aggregate_conformers

def _rec(model, enrichment, p5mean, p5max, frac_mod):
    return {"model": model, "analysis": {"overlap": {
        "enrichment_pocket5_over_lbd": enrichment, "pocket5_mean_score": p5mean,
        "pocket5_max_score": p5max, "frac_pocket5_moderate": frac_mod}}}


def test_aggregate_enriches_verdict():
    per = [_rec(2, 2.5, 0.7, 0.9, 0.6), _rec(8, 3.0, 0.75, 0.85, 0.5), _rec(20, 1.8, 0.55, 0.6, 0.3)]
    agg = p8.aggregate_conformers(per)
    assert agg["n_conformers_scored"] == 3
    assert agg["verdict"] == "enriches"
    assert agg["enrichment_distribution"]["median"] == pytest.approx(2.5)


def test_aggregate_weak_verdict():
    """Median enrichment <= 1 -> weak-or-null even if one conformer is high."""
    per = [_rec(2, 0.8, 0.2, 0.3, 0.0), _rec(8, 0.9, 0.25, 0.35, 0.0), _rec(20, 3.0, 0.6, 0.7, 0.4)]
    agg = p8.aggregate_conformers(per)
    assert agg["verdict"] == "weak-or-null"


def test_aggregate_no_data():
    per = [{"model": 2, "analysis": {"_status": "no scores"}}]
    agg = p8.aggregate_conformers(per)
    assert agg["verdict"] == "no-data"
    assert agg["n_conformers_scored"] == 0


def test_aggregate_flagged_gate():
    """Median enrichment > 1 but NO conformer reaches the moderate cutoff -> not 'enriches'."""
    per = [_rec(2, 1.5, 0.1, 0.2, 0.0), _rec(8, 2.0, 0.15, 0.25, 0.0)]
    agg = p8.aggregate_conformers(per)
    assert agg["verdict"] == "weak-or-null"       # p5max never >= 0.5


# ------------------------------------------------------------------ select_models

def test_select_models_explicit_list():
    assert p8.select_models(range(1, 21), "2,8,20,6") == [2, 8, 20, 6]


def test_select_models_spaces_and_dedup():
    assert p8.select_models(range(1, 21), "8 8 2") == [8, 2]


def test_select_models_all():
    assert p8.select_models(range(1, 6), "all") == [1, 2, 3, 4, 5]
    assert p8.select_models(range(1, 4), None) == [1, 2, 3]


def test_select_models_intersects_available():
    # request models beyond the ensemble -> only the present ones kept
    assert p8.select_models(range(1, 6), "2,99,4") == [2, 4]


def test_select_models_none_present_raises():
    with pytest.raises(ValueError, match="none of the requested"):
        p8.select_models(range(1, 6), "99,100")


def test_select_models_empty_available_raises():
    with pytest.raises(ValueError, match="no 8XTT conformers"):
        p8.select_models([], "2,8")
