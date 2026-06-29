"""Tests for decoy_library — the negative-control set for the selectivity-funnel specificity check."""
import decoy_library as dl


def test_has_a_reasonable_number_of_decoys():
    assert dl.n_decoys() >= 30
    assert len(dl.DECOY_SMILES) == dl.n_decoys()


def test_candidate_json_shape_matches_denovo():
    cj = dl.decoy_candidate_json()
    assert set(cj) >= {"candidates", "campaign"}
    assert len(cj["candidates"]) == dl.n_decoys()
    c = cj["candidates"][0]
    # the dock funnel keys on these fields (name, smiles, denovo_promise, and the developability fields)
    assert set(c) >= {"name", "smiles", "denovo_promise", "aromatic_rings", "SAscore", "BRENK_alert_count"}
    assert all(x["name"].startswith("decoy_") for x in cj["candidates"])
    assert all(x["denovo_promise"] is not None for x in cj["candidates"])   # picker requires non-None


def test_candidates_are_sorted_and_unique():
    cj = dl.decoy_candidate_json()
    names = [c["name"] for c in cj["candidates"]]
    assert names == sorted(names)
    assert len(set(names)) == len(names)
    assert len({c["smiles"] for c in cj["candidates"]}) == len(names)       # no duplicate SMILES
