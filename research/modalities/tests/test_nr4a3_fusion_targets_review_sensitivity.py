"""Offline arithmetic guards for the revision sensitivity artifact.

These check the properties the manuscript's revised §2.3.2, §3.3, §3.5 and §3.7 assert, against the
committed artifact rather than against prose. A number quoted in the paper that this file cannot
find is a number nobody can check.
"""
import json
import math
import os

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(HERE, "nr4a3-fusion-targets-review-sensitivity.json")
PRIMARY = os.path.join(HERE, "nr4a3-fusion-targets.json")


@pytest.fixture(scope="module")
def art():
    with open(ART) as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def primary():
    with open(PRIMARY) as fh:
        return json.load(fh)


def test_the_module_reproduces_every_committed_set_delta(art):
    """The whole artifact is worthless if its reduction is not the primary artifact's reduction."""
    p = art["parity_with_primary_artifact"]
    assert p["agrees"] is True
    assert p["worst_abs_difference"] == 0.0
    assert len(p["rows"]) >= 20


def test_the_null_is_an_independence_null_on_both_platforms(art):
    """`null_sd × sqrt(n)` constant across set size is the property §2.3.2 reports as measured.

    This is the reading that decided how the method had to be described, so it is pinned: if a
    future change to the resampler introduced a correlation term, this test is what would notice.
    """
    for label, v in art["closed_form"]["per_platform"].items():
        lo, hi = v["null_sd_x_sqrt_n_range"]
        assert v["null_sd_x_sqrt_n_spread_fraction"] < 0.07, (label, lo, hi)
        assert len(v["sets"]) >= 10, label
        sizes = [r["n"] for r in v["sets"]]
        assert min(sizes) <= 10 and max(sizes) >= 230, label


def test_the_manuscripts_quoted_sigma_matches_the_artifact(art):
    """§2.3.2 quotes σ = 0.261 (GPL6244) and 0.678 (GPL3290)."""
    assert art["closed_form"]["per_platform"]["GPL6244"]["sigma_platform"] == pytest.approx(0.261, abs=5e-4)
    assert art["closed_form"]["per_platform"]["GPL3290"]["sigma_platform"] == pytest.approx(0.678, abs=5e-4)


def test_the_correlation_correction_only_ever_raises_a_threshold(art):
    """An inflated threshold below the uninflated one would silently manufacture a positive."""
    for label, rows in art["inter_gene_correlation"]["per_platform"].items():
        for setname, r in rows.items():
            if r["variance_inflation_factor"] <= 1:
                continue
            assert abs(r["threshold_inflated"]) >= abs(r["threshold_uninflated"]), (label, setname)
            assert r["fraction_of_inflated_threshold"] <= r["fraction_of_uninflated_threshold"] + 1e-9


def test_no_pparg_arm_clears_its_inflated_threshold(art):
    """SI §S4 states this before it reports the permutation results; it must stay true."""
    for label, rows in art["inter_gene_correlation"]["per_platform"].items():
        for setname, r in rows.items():
            if setname.startswith("PPARG_"):
                assert r["clears_inflated"] is False, (label, setname, r)


def test_the_aggregate_negative_survives_the_correlation_correction(art):
    """A+B must not clear on either platform, inflated or not. This is the paper's central negative."""
    for label, rows in art["inter_gene_correlation"]["per_platform"].items():
        r = rows["A_plus_B_all_dna_binding"]
        assert r["clears_uninflated"] is False, label
        assert r["clears_inflated"] is False, label


def test_set_D_shares_exactly_three_genes_with_set_E_and_still_clears_without_them(art):
    d = art["set_D_without_genes_shared_with_set_E"]
    assert d["shared_with_set_E"] == ["DKK1", "MAN1A1", "NMB"]
    for label, r in d["per_platform"].items():
        assert r["n_shared_and_readable"] == 3, label
        assert r["full"]["reproduces_committed_delta"] is True, label
        assert r["without_shared_genes"]["fraction_of_threshold"] > 1.0, label


def test_the_per_gene_missingness_band_is_wider_and_changes_no_grade(art):
    """§3.3 says the redrawn bands are 1.6-3.4% wider and move no verdict."""
    ratios = []
    for label, rows in art["per_gene_missingness_nulls"]["per_platform"].items():
        for gene, r in rows.items():
            if "band_width_ratio_own_over_platform" not in r:
                continue
            ratios.append(r["band_width_ratio_own_over_platform"])
            assert r["outside_own_band"] == r["outside_platform_band"], (label, gene, r)
    assert ratios
    assert 1.0 < min(ratios) and max(ratios) < 1.05


def test_every_muscle_marker_is_inside_its_band_and_ENO3_is_outside(art):
    """The muscle control's whole argument is this contrast, and it had no null before revision."""
    g6 = art["muscle_marker_nulls"]["per_platform"]["GPL6244"]
    for marker in ("ACTA1", "MYH7", "MYL1", "PYGM"):
        assert g6[marker]["outside_band"] is False, (marker, g6[marker])
    assert g6["ENO3"]["outside_band"] is True


def test_the_class_B_split_partitions_class_B(art, primary):
    b = art["class_B_evidence_split"]
    classB = sorted(r["gene"] for r in primary["evidence_table"]["rows"]
                    if r["evidence_class"] == "native_dna_binding")
    assert sorted(b["B1_primary_assay_retrieved"] + b["B2_review_assertion_only"]) == classB
    assert len(b["B1_primary_assay_retrieved"]) == 6
    assert len(b["B2_review_assertion_only"]) == 10
    # The one row the string rule does not settle is named rather than silently reassigned.
    assert b["genes_the_string_rule_and_the_assignment_disagree_on"] == ["VTN"]


def test_B1_alone_clears_nothing_which_is_why_A_plus_B1_is_not_promoted(art):
    """§3.7 declines to make A+B1 the primary aggregate on exactly this reading."""
    for label, rows in art["class_B_evidence_split"]["per_platform"].items():
        assert rows["B1_only"]["clears"] is False, label
        assert rows["A_plus_B1"]["clears"] is True, label


def test_the_t_scale_null_supports_the_abstracts_claim(art):
    """The abstract and §3.4 say t = 3.16 sits inside what random sets of that size print."""
    r = art["t_scale_null"]["per_platform"]["GPL3290"]["A_plus_B_all_dna_binding"]
    assert r["n"] == 17
    assert r["observed_t"] == pytest.approx(3.16, abs=0.01)
    lo, hi = r["null_t_band_95"]
    assert lo < r["observed_t"] < hi
    assert r["fraction_of_random_sets_with_larger_abs_t"] > 0.05


def test_the_detectability_figures_are_labelled_exact_or_sampled(art):
    """A sampled permutation interval presented as exact would be the fail-quiet shape."""
    for label, rows in art["detectability"]["per_platform"].items():
        for setname, r in rows.items():
            assert r["permutation_ci_95"] is not None, (label, setname)
            lo, hi = r["permutation_ci_95"]
            assert lo <= r["observed_delta"] <= hi, (label, setname)
            exact = r["ci_method"].startswith("exact")
            assert exact == (r["n_distinct_assignments"] <= 60000), (label, setname)


def test_the_seed_block_says_what_it_does_not_bound(art):
    """Pool-composition error is not bounded here, and the artifact must keep saying so."""
    s = art["seed_sensitivity"]
    assert s["n_seeds"] == 20
    key = [k for k in s if "does_not_bound" in k]
    assert key, "the artifact must name what the seed spread does not bound"
    assert "pool-composition" in s[key[0]]
    for label, rows in s["per_platform"].items():
        for setname, r in rows.items():
            assert 0 < r["relative_sd"] < 0.05, (label, setname, r)


def test_the_composition_matched_nulls_report_both_matching_properties(art):
    """One of the four is the reading that damages the paper's case, so neither may be dropped."""
    for label, byprop in art["composition_matched_nulls"]["per_platform"].items():
        props = {k for k in byprop if not k.startswith("_")}
        assert props == {"expression_decile", "detection_rate_decile"}, label
    g3 = art["composition_matched_nulls"]["per_platform"]["GPL3290"]
    marginal = g3["expression_decile"]["A_plus_B_all_dna_binding"]
    assert marginal["fraction_of_matched_threshold"] > 1.0, (
        "§3.7 and Limitation 18 report that the aggregate clears one of the four matched nulls; "
        "if this ever becomes false the manuscript must stop saying so")
