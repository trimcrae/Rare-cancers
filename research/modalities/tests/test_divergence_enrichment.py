"""Unit tests for the Pocket-5 divergence-enrichment Fisher test (review comment 9)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nr4a3_divergence_enrichment as de  # noqa: E402


def test_fisher_matches_known_2x2():
    # table [[8,2],[1,5]]: one-sided Fisher (greater) = pmf(8)+pmf(9) = (9*21+7)/C(16,10) = 0.024475
    p = de.fisher_exact_greater(8, 2, 1, 5)
    assert abs(p - 0.024475) < 1e-4


def test_fisher_no_enrichment_is_large_p():
    # equal proportions → p near 1 (not enriched)
    p = de.fisher_exact_greater(5, 5, 5, 5)
    assert p > 0.5


def test_fisher_full_enrichment_small_p():
    p = de.fisher_exact_greater(10, 0, 0, 10)
    assert p < 0.001


def test_collect_and_enrichment_shape():
    data = {
        "nr4a3_lbd_pockets": [
            {"pocket": 5, "druggability": 0.495, "residues": [
                {"nr4a3": "L406", "nr4a1": "V", "nr4a2": "V", "divergent": True},
                {"nr4a3": "P411", "nr4a1": "P", "nr4a2": "P", "divergent": False},
            ]},
            {"pocket": 1, "druggability": 0.007, "residues": [
                {"nr4a3": "D423", "nr4a1": "D", "nr4a2": "D", "divergent": False},
            ]},
        ]
    }
    residues = de.collect_residues(data)
    assert residues["406"]["pocket5"] is True
    assert residues["406"]["divboth"] is True
    assert residues["411"]["pocket5"] is True and residues["411"]["div1"] is False
    assert residues["423"]["pocket5"] is False
    res = de.enrichment(residues)
    assert res["div1"]["pocket5_total"] == 2
    assert res["div1"]["background_total"] == 1
