"""Guards for the three readings that replace the withdrawn coverage confidence interval.

⛔ EVERY CLAIM IN THIS MODULE IS EXACT, WHICH RAISES THE BAR RATHER THAN LOWERING IT. The manuscript
says the published coverage form is a LOWER bound, and that the Fréchet interval holds under any
dependence structure whatever. Those are not modelling choices with slack in them — they are either
true of the code or the paragraph in §2.3 is wrong. A statistic quoted as exact and computed
approximately is worse than an approximate one honestly labelled, because nothing downstream will
think to check it.

⚠ AND THE DIRECTION IS THE HALF THAT CARRIES A CLAIM. "No coverage figure in this paper is too high
for this reason" is only true while exact >= published, so that inequality is tested as a PROPERTY
over many frequency vectors and not on the one panel that happens to be committed.
"""
import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ART = os.path.join(MOD, "coverage-uncertainty.json")

_spec = importlib.util.spec_from_file_location(
    "coverage_uncertainty", os.path.join(MOD, "coverage_uncertainty.py"))
cu = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cu)


def test_the_locus_grouping_is_the_competing_slots_grouping():
    """Two alleles share a locus exactly when they compete for the same pair of chromosomes."""
    assert cu.locus_of("HLA-B*07:02") == "B"
    assert cu.locus_of("HLA-B*15:01") == "B"
    assert cu.locus_of("HLA-A*01:01") == "A"
    assert cu.locus_of("DRB1*14:01") == "DRB1"
    assert cu.locus_of("B*07:02") == "B", "the AFND spelling carries no HLA- prefix"


def test_one_allele_at_one_locus_is_the_plain_hardy_weinberg_carrier_frequency():
    """With nothing to group, all three readings must collapse onto the same number — otherwise the
    machinery is adding something where it should add nothing."""
    f = {"HLA-B*15:01": 0.0435}
    hw = 1 - (1 - 0.0435) ** 2
    assert cu.published_form(f) == pytest.approx(hw)
    assert cu.within_locus_exact(f) == pytest.approx(hw)
    assert cu.frechet_bounds(f) == (pytest.approx(hw), pytest.approx(hw))


def test_the_same_locus_correction_is_the_hand_computation():
    """Two alleles at HLA-B: the exact non-carrier probability is (1-f1-f2)^2, and the published
    form's (1-f1)^2(1-f2)^2 is strictly larger, so the published coverage is strictly smaller."""
    f1, f2 = 0.048, 0.0435
    f = {"HLA-B*07:02": f1, "HLA-B*15:01": f2}
    assert cu.within_locus_exact(f) == pytest.approx(1 - (1 - f1 - f2) ** 2)
    assert cu.published_form(f) == pytest.approx(1 - ((1 - f1) ** 2) * ((1 - f2) ** 2))
    assert cu.within_locus_exact(f) > cu.published_form(f)


def test_the_published_form_is_a_lower_bound_over_many_frequency_vectors():
    """⭐ THE PROPERTY BEHIND §2.3's DIRECTION CLAIM. Deterministic sweep rather than random draws:
    a guard that fails only on some seeds is a guard nobody can act on."""
    for a in range(1, 20):
        for b in range(1, 20):
            for c in range(1, 20):
                f = {"HLA-A*01:01": a / 40, "HLA-B*07:02": b / 40, "HLA-B*15:01": c / 40}
                assert cu.within_locus_exact(f) >= cu.published_form(f) - 1e-12, (
                    f"published form exceeded the exact form at {f}, which inverts the claim §2.3 "
                    "makes about the direction of the approximation")


def test_the_frechet_bounds_contain_the_independence_estimate():
    """The interval is only useful if the estimate it is offered around actually lies inside it."""
    for a in range(1, 25):
        for b in range(1, 25):
            f = {"HLA-A*01:01": a / 50, "HLA-B*07:02": b / 50}
            lo, hi = cu.frechet_bounds(f)
            exact = cu.within_locus_exact(f)
            assert lo - 1e-12 <= exact <= hi + 1e-12, (
                f"the independence estimate {exact} falls outside its own dependence bounds "
                f"[{lo}, {hi}] at {f}")


def test_the_frechet_bounds_are_attained_and_therefore_cannot_be_tightened():
    """⛔ A BOUND NOBODY CAN REACH IS A WEAKER STATEMENT THAN THE PAPER MAKES. §2.3 says the interval
    holds under ANY dependence structure, which is only worth printing if both ends are achievable:
    the lower end when one locus's carriers are a subset of the other's (perfect positive
    dependence), the upper when the two carrier sets are disjoint. Both are constructions on the
    marginals alone, so they are checked against the marginals alone."""
    f = {"HLA-A*01:01": 0.0641, "HLA-B*07:02": 0.048, "HLA-B*15:01": 0.0435}
    carriers, _ = cu.per_locus_carrier(f)
    p = sorted(carriers.values())
    lo, hi = cu.frechet_bounds(f)
    assert lo == pytest.approx(max(p)), (
        "nested carrier sets give a union equal to the larger marginal; that is the lower bound")
    assert hi == pytest.approx(min(1.0, sum(p))), (
        "disjoint carrier sets give a union equal to the sum; that is the upper bound")


def test_a_summed_locus_frequency_over_one_cannot_produce_a_negative_probability():
    """A data error must degrade to a clamped probability, never to a coverage above 1 or a
    non-carrier probability that has gone negative and squared itself back into plausibility."""
    f = {"HLA-B*07:02": 0.7, "HLA-B*15:01": 0.6}
    carriers, sums = cu.per_locus_carrier(f)
    assert sums["B"] == pytest.approx(1.3), "the raw sum stays visible in the record"
    assert carriers["B"] == pytest.approx(1.0)
    assert 0.0 <= cu.within_locus_exact(f) <= 1.0


def test_the_quantiles_are_the_textbook_ones():
    assert cu.quantiles([]) == {}
    one = cu.quantiles([0.25])
    assert one["min"] == one["median"] == one["max"] == 0.25 and one["n"] == 1
    q = cu.quantiles([0.0, 0.1, 0.2, 0.3, 0.4])
    assert (q["min"], q["p25"], q["median"], q["p75"], q["max"]) == (0.0, 0.1, 0.2, 0.3, 0.4)


@pytest.mark.committed_artifact
def test_the_committed_artifact_keeps_the_two_population_readings_apart():
    """⛔ AN ABSENT READING IS NOT A READING OF ABSENCE. The floor scores an unmeasured allele as
    zero, so it must always sit at or below the complete-panel estimate and must always be labelled
    as a floor. Collapsing the two into one distribution would report a database gap as biology."""
    if not os.path.exists(ART):
        pytest.fail(f"{ART} is committed; regenerate it rather than passing over these assertions")
    with open(ART, encoding="utf-8") as fh:
        d = json.load(fh)
    for name, rec in d["sets"].items():
        bp = rec["between_population"]
        complete, floor = bp["complete_panel"], bp["absent_scored_zero_floor"]
        assert floor["median"] <= complete["median"] + 1e-9, (
            f"{name}: the absent-as-zero floor came out ABOVE the complete-panel estimate, which "
            "cannot happen if the floor is what it claims to be")
        assert bp["populations_measuring_every_presenting_allele"] <= bp[
            "populations_with_any_measurement"], f"{name}: the complete-panel set is not a subset"
        assert rec["coverage_within_locus_exact"] >= rec["coverage_published_form"] - 1e-9
        lo, hi = rec["ld_bounds_across_loci"]
        assert lo <= rec["coverage_within_locus_exact"] <= hi + 1e-9
