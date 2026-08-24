"""Guards for the one-residue novelty pre-screen of §B5.

⛔ A PERFECT SCORE IS THE MOST SUSPICIOUS RESULT IN THIS REPOSITORY, AND THIS ONE SCORES PERFECTLY.
`novelty_seam_test.py` reports sensitivity 1.0 and specificity 1.0 over 970 transcript pairs. That is
exactly the shape a tautology produces — a predictor derived from the same records it is scored
against would agree with them by construction and mean nothing. So the tests below are aimed at the
tautology first: the alphabet must come from the PROTEOME SEARCH's hits, the validation must come
from the TRANSCRIPT SCAN's per-pair observations, and the two must be able to disagree. A mutation
that makes the predictor wrong has to make the score drop.

⚠ AND THE DENOMINATOR IS PART OF THE CLAIM. Pairs that emit no in-frame seam have no seam residue to
test; scoring them as correct negatives would inflate specificity with cases the test was never asked
about, which is `an absent reading is not a reading of absence` arriving through a confusion matrix.
"""
import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ART = os.path.join(MOD, "novelty-seam-test.json")

_spec = importlib.util.spec_from_file_location(
    "novelty_seam_test", os.path.join(MOD, "novelty_seam_test.py"))
nst = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nst)


def _pair(name, residue, collided, in_frame=True, emitted=True):
    return {"pair": name, "seam_residue": residue, "emitted": emitted, "in_frame": in_frame,
            "collided_peptides_present": ["X"] if collided else []}


def test_the_alphabet_is_the_first_residue_of_each_observed_hit():
    """Derived from the search's hits, never typed — so it cannot disagree with the search."""
    novelty = {"peptides_found_in_proteome": [
        {"peptide": "DMPCVQAQY", "proteome_hits": [{"accession": "Q92570-3"}]},
        {"peptide": "DMPCVQAQ", "proteome_hits": [{"accession": "Q92570-3"}]},
    ]}
    alphabet, stems, accessions = nst.collision_alphabet(novelty)
    assert alphabet == ["D"]
    assert stems["D"] == ["MPCVQAQ", "MPCVQAQY"]
    assert accessions["D"] == ["Q92570-3"]


def test_a_second_colliding_residue_widens_the_alphabet():
    """⛔ A GUARD THAT CANNOT SEE A SECOND RESIDUE WOULD PASS ON THIS LOCUS FOREVER. The alphabet is
    a set because another acceptor, or another isoform of this one, can contribute another entry."""
    novelty = {"peptides_found_in_proteome": [
        {"peptide": "DMPCVQAQY", "proteome_hits": [{"accession": "Q92570-3"}]},
        {"peptide": "GMPCVQAQY", "proteome_hits": [{"accession": "Q92570-9"}]},
    ]}
    alphabet, _stems, _acc = nst.collision_alphabet(novelty)
    assert alphabet == ["D", "G"]


def test_the_confusion_matrix_counts_all_four_cells():
    """Synthetic pairs the real data does not contain, so each cell is exercised on purpose."""
    pairs = [_pair("tp", "D", True), _pair("fn", "N", True),
             _pair("fp", "D", False), _pair("tn", "N", False)]
    tp, fp, tn, fn, disagreements = nst.confusion(pairs, ["D"])
    assert (tp, fp, tn, fn) == (1, 1, 1, 1)
    assert {d["pair"] for d in disagreements} == {"fp", "fn"}


def test_a_pair_with_no_in_frame_seam_is_excluded_rather_than_scored_correct():
    """⛔ THE DENOMINATOR GUARD. 31 real pairs emit no seam residue at all. Counting them as correct
    negatives would raise the specificity using cases that were never tested."""
    pairs = [_pair("out-of-frame", None, False, in_frame=False),
             _pair("not-emitted", None, False, emitted=False),
             _pair("real", "D", True)]
    tp, fp, tn, fn, _d = nst.confusion(pairs, ["D"])
    assert (tp, fp, tn, fn) == (1, 0, 0, 0), "only the one testable pair may enter the matrix"


def test_a_wrong_alphabet_actually_scores_badly():
    """⛔ MUTATION TEST — A SCORE THAT CANNOT FALL IS NOT A MEASUREMENT. If the predictor named the
    glycine seam instead of the aspartate one, the same code must report it as wrong. Without this,
    the 1.0/1.0 in the manuscript is unfalsifiable."""
    pairs = [_pair("a", "D", True), _pair("b", "D", True), _pair("c", "G", False)]
    tp, fp, tn, fn, _d = nst.confusion(pairs, ["D"])
    assert (tp, fp, tn, fn) == (2, 0, 1, 0), "the right alphabet scores perfectly"
    tp, fp, tn, fn, dis = nst.confusion(pairs, ["G"])
    assert (tp, fp, tn, fn) == (0, 1, 0, 2), "the wrong alphabet must score badly, and does"
    assert len(dis) == 3


@pytest.mark.committed_artifact
def test_the_committed_validation_is_internally_consistent():
    if not os.path.exists(ART):
        pytest.fail(f"{ART} is committed; regenerate it with novelty_seam_test.py rather than "
                    "passing over the assertions that depend on it.")
    with open(ART, encoding="utf-8") as fh:
        d = json.load(fh)
    v = d["validation"]
    assert v["n_pairs_tested"] == v["true_positive"] + v["false_positive"] + v["true_negative"] + \
        v["false_negative"], "the cells must sum to the denominator"
    assert len(v["disagreements"]) == v["false_positive"] + v["false_negative"], (
        "every disagreement must be listed, not counted — a summary the reader cannot audit is how "
        "a perfect score hides an imperfect one")
    # The alphabet's own residue must be the one that collides, and no other residue may.
    by_residue = d["by_seam_residue"]
    for residue, rec in by_residue.items():
        if residue in d["collision_alphabet"]:
            assert rec["collided"] == rec["pairs"], (
                f"seam {residue} is in the alphabet but only {rec['collided']}/{rec['pairs']} of "
                "its pairs collide")
        else:
            assert rec["collided"] == 0, (
                f"seam {residue} is NOT in the alphabet yet {rec['collided']} of its pairs collide — "
                "the alphabet is incomplete and the manuscript's exactness claim is false")


@pytest.mark.committed_artifact
def test_the_artifact_still_says_it_does_not_replace_the_search():
    """The prescription is only safe with its limit attached; §B5 states it and so must the artifact,
    because a reader who takes the pre-screen for the filter reintroduces the defect."""
    with open(ART, encoding="utf-8") as fh:
        d = json.load(fh)
    disclaimer = d["⛔_what_this_is_not"]
    assert "NOT a replacement" in disclaimer and "RGDMPCVQAQY" in disclaimer, (
        "the artifact must carry the counterexample that shows the pre-screen is not the filter")
