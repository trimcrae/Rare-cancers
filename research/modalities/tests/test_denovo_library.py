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


def test_developable_filter_excludes_liabilities_and_keeps_rank():
    # denovo_a: high promise but has a liability (excluded). denovo_b: clean. denovo_c: clean but no
    # aromatic ring (excluded). denovo_d: clean but SA too high (excluded).
    d = _denovo([
        {"name": "denovo_a", "smiles": "AAA", "denovo_promise": 0.95, "aromatic_rings": 1, "SAscore": 3.0},
        {"name": "denovo_b", "smiles": "BBB", "denovo_promise": 0.80, "aromatic_rings": 1, "SAscore": 3.0},
        {"name": "denovo_c", "smiles": "CCC", "denovo_promise": 0.70, "aromatic_rings": 0, "SAscore": 3.0},
        {"name": "denovo_d", "smiles": "DDD", "denovo_promise": 0.60, "aromatic_rings": 1, "SAscore": 5.0},
    ])
    # fake liability_fn: only 'AAA' has a structural alert
    liab = lambda smi: ["peroxide"] if smi == "AAA" else []        # noqa: E731
    out = dl.top_developable_candidates(d, liab, top_n=10)
    assert [o[0] for o in out] == ["denovo_b"]                      # a (alert), c (no aromatic), d (SA) all out


def test_developable_respects_top_n_and_rank():
    d = _denovo([
        {"name": "denovo_1", "smiles": "S1", "denovo_promise": 0.5, "aromatic_rings": 1, "SAscore": 2.0},
        {"name": "denovo_2", "smiles": "S2", "denovo_promise": 0.9, "aromatic_rings": 1, "SAscore": 2.0},
        {"name": "denovo_3", "smiles": "S3", "denovo_promise": 0.7, "aromatic_rings": 1, "SAscore": 2.0},
    ])
    out = dl.top_developable_candidates(d, lambda smi: [], top_n=2)
    assert [o[0] for o in out] == ["denovo_2", "denovo_3"]          # ranked by promise, capped at 2
