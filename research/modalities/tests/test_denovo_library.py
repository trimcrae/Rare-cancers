"""Tests for denovo_library.top_candidates — the pure picker feeding the dock+MM-GBSA funnel."""
import denovo_library as dl


def _denovo(cands):
    return {"candidates": cands}


def test_ranks_by_promise_and_caps_at_top_n():
    d = _denovo([
        {"name": "denovo_1", "smiles": "CCO", "denovo_promise": 0.30},
        {"name": "denovo_2", "smiles": "c1ccccc1", "denovo_promise": 0.95},
        {"name": "denovo_3", "smiles": "CCN", "denovo_promise": 0.60},
    ])
    out = dl.top_candidates(d, top_n=2)
    assert [o[0] for o in out] == ["denovo_2", "denovo_3"]      # highest promise first
    assert all(len(o) == 3 for o in out)                        # (label, id, smiles)
    assert out[0] == ("denovo_2", "denovo_2", "c1ccccc1")


def test_dedup_by_smiles():
    d = _denovo([
        {"name": "denovo_1", "smiles": "CCO", "denovo_promise": 0.9},
        {"name": "denovo_2", "smiles": "CCO", "denovo_promise": 0.8},   # duplicate SMILES
        {"name": "denovo_3", "smiles": "CCN", "denovo_promise": 0.7},
    ])
    out = dl.top_candidates(d, top_n=10)
    assert [o[2] for o in out] == ["CCO", "CCN"]                # one CCO (the higher-promise one)
    assert out[0][0] == "denovo_1"


def test_skips_invalid():
    d = _denovo([
        {"name": "denovo_1", "smiles": "CCO", "denovo_promise": None},   # invalid (no promise)
        {"name": "denovo_2", "error": "bad", "denovo_promise": None},
        {"name": "denovo_3", "denovo_promise": 0.5},                     # no smiles
        {"name": "denovo_4", "smiles": "CCN", "denovo_promise": 0.4},
    ])
    out = dl.top_candidates(d, top_n=10)
    assert [o[0] for o in out] == ["denovo_4"]


def test_empty():
    assert dl.top_candidates({}, top_n=5) == []
    assert dl.top_candidates({"candidates": []}, top_n=5) == []
