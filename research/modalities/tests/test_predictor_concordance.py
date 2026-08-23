"""Guards for the second-predictor concordance.

⛔ THE ONE THAT MATTERS IS THE MISSING-MODEL GUARD. MHCnuggets has no model for some of the 34
panel alleles. An allele it could not score is not an allele that failed to present, and counting it
as a non-binder would manufacture agreement in exactly the direction that flatters the manuscript —
"the second predictor also finds only a few presenting alleles" would then be partly an artifact of
which models shipped. Both tests below exist to make that impossible to do quietly.
"""
import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ART = os.path.join(MOD, "predictor-concordance.json")
NUG = os.path.join(MOD, "epitope-allele-matrix-mhcnuggets.json")

_spec = importlib.util.spec_from_file_location(
    "predictor_concordance", os.path.join(MOD, "predictor_concordance.py"))
pc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pc)


def test_the_allele_name_translation_matches_mhcnuggets_class_i_format():
    assert pc.nuggets_allele("HLA-A*02:01") == "HLA-A02:01"
    assert pc.nuggets_allele("A*02:01") == "HLA-A02:01"


def test_the_two_scales_are_never_the_same_variable():
    """⛔ A rescaling would manufacture the agreement. The grids must stay in their own units."""
    assert pc.IC50_STRONG == 500.0
    assert min(pc.IC50_GRID) < pc.IC50_STRONG < max(pc.IC50_GRID)


@pytest.mark.skipif(not os.path.exists(ART), reason="predictor-concordance.json not yet generated")
@pytest.mark.committed_artifact
def test_alleles_without_a_model_are_excluded_from_the_comparison_not_scored_as_absent():
    d = json.load(open(ART))
    missing = set(d["alleles_without_an_mhcnuggets_model"])
    cmp_ = d["agreement_at_each_predictors_own_cut"]
    for key in ("presenting_in_both", "mhcflurry_only", "mhcnuggets_only"):
        assert not (set(cmp_[key]) & missing), (
            f"{key} contains an allele MHCnuggets never scored: {set(cmp_[key]) & missing}")
    assert d["n_alleles_scored_by_both"] == d["n_panel"] - len(missing)


@pytest.mark.skipif(not os.path.exists(NUG), reason="MHCnuggets matrix not yet generated")
@pytest.mark.committed_artifact
def test_the_mhcnuggets_matrix_never_merges_into_the_mhcflurry_one():
    """Two predictors, two artifacts. A merged matrix would make the comparison uncheckable."""
    nug = json.load(open(NUG))
    assert nug["scale"] == "predicted IC50, nM"
    assert all("ic50_nM" in c and "percentile" not in c for c in nug["calls"])
    flurry = json.load(open(os.path.join(MOD, "epitope-allele-matrix.json")))
    assert "ic50_nM" not in json.dumps(flurry)
