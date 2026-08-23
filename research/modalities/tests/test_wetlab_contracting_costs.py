"""Guards on the wet-lab contracting cost model.

★ WHAT THESE PROTECT. The model's whole value is that two classes of input are kept apart: a
MEASURED published rate and an ESTIMATED quantity. If that separation erodes, the artifact becomes
an estimate wearing a measurement's authority — the exact failure `what-a-civilian-can-buy.md` §6
warns about, and the one this repository has paid for before. Every test below asserts a property of
the SEPARATION, not a value: prices drift and the totals are meant to move with them.
"""
from __future__ import annotations

import wetlab_contracting_costs as wcc


def test_every_line_item_cites_a_rate_that_exists():
    """A line item priced against an unknown rate must raise, never silently cost zero."""
    for exp in wcc.EXPERIMENTS:
        for key, _qty, _note in exp["lines"]:
            assert key in wcc.RATES, f"{exp['id']} cites unknown rate {key!r}"


def test_an_unknown_rate_key_raises_rather_than_costing_nothing():
    try:
        wcc._rate("no-such-rate")
    except KeyError:
        return
    raise AssertionError("an unknown rate key must raise, not default to free")


def test_every_published_rate_carries_its_source_and_its_cache_path():
    """A rate with no provenance is a remembered number, which this repository forbids."""
    for key, r in wcc.RATES.items():
        assert r.get("source"), f"{key} has no named facility"
        assert str(r.get("cache", "")).startswith("literature/"), (
            f"{key} does not point at a fetched copy on literature-cache")
        assert r.get("tier"), f"{key} does not say WHICH rate tier it is"


def test_rates_and_quantities_are_labelled_as_different_kinds_of_input():
    doc = wcc.build()
    for exp in doc["experiments"]:
        for line in exp["lines"]:
            assert line["rate_provenance"].startswith("MEASURED")
            assert line["quantity_provenance"].startswith("ESTIMATE")


def test_every_total_is_derived_from_its_line_items_and_never_typed():
    doc = wcc.build()
    for exp in doc["experiments"]:
        recomputed = sum(l["unit_rate_usd"] * l["quantity"] for l in exp["lines"])
        assert round(recomputed, 2) == exp["line_subtotal_usd"]
        assert round(recomputed + exp["consumables_estimate_usd"], 2) == exp["total_usd"]
    assert round(sum(e["total_usd"] for e in doc["experiments"]), 2) == doc["portfolio_total_usd"]


def test_the_external_commercial_multiple_is_measured_from_one_facilitys_own_two_tiers():
    """The markup must come from two rates on ONE published card, not from an assumption."""
    m = wcc.external_commercial_multiple()
    internal = wcc.RATES["spr_biacore8000_hour_internal"]
    commercial = wcc.RATES["spr_biacore8000_hour_external_commercial"]
    assert internal["source"] == commercial["source"], "the two tiers must be the same facility"
    assert m["multiple"] == round(commercial["usd"] / internal["usd"], 3)
    assert m["multiple"] > 1.0


def test_the_artifact_states_what_it_is_not():
    """A price is not a purchase, and the artifact has to say so where a reader will hit it."""
    doc = wcc.build()
    disclaimers = " ".join(doc["_what_this_is_not"]).lower()
    assert "not a quote" in disclaimers
    assert "eligibility" in disclaimers


def test_the_protein_price_is_not_restated_here():
    """ONE FACT, ONE PLACE — the protein price is owned by what-a-civilian-can-buy.md §1.5/§4.2."""
    doc = wcc.build()
    blob = repr(doc)
    for owned_elsewhere in ("734", "791", "737"):
        assert owned_elsewhere not in blob, (
            f"{owned_elsewhere} looks like the protein price, which another document owns")


def test_every_rate_is_classified_by_what_it_buys():
    """An unclassified rate would silently vanish from the cost-structure breakdown."""
    for key in wcc.RATES:
        wcc.what_you_are_buying(key)  # raises if unclassified


def test_an_unclassified_rate_raises_rather_than_being_dropped():
    try:
        wcc.what_you_are_buying("not-a-rate")
    except KeyError:
        return
    raise AssertionError("an unclassified rate must raise, not be silently omitted")


def test_the_buying_categories_do_not_overlap():
    seen = set()
    for cat, keys in wcc.BUYING.items():
        clash = seen & keys
        assert not clash, f"{cat} double-counts {clash}"
        seen |= keys


def test_the_cost_structure_shares_account_for_every_dollar():
    doc = wcc.build()
    for exp_id, row in doc["cost_structure"]["per_experiment"].items():
        assert round(sum(row["usd"].values()), 2) == row["total_usd"], exp_id
        # shares are emitted rounded to 4 dp, so the sum can miss 1.0 by up to half a unit in the
        # last place per category. The dollars above are the exact check; this one guards that no
        # category is MISSING, which a tolerance of 1e-6 would flag as a rounding failure instead.
        assert abs(sum(row["share"].values()) - 1.0) < 5e-4 * len(row["share"]), exp_id


def test_hands_and_cell_engineering_service_are_kept_apart():
    """The distinction is the whole point: only one of them is displaced by a robot."""
    assert not (wcc.BUYING["hands"] & wcc.BUYING["cell_engineering_service"])
    doc = wcc.build()
    text = doc["cost_structure"]["_the_distinction_that_matters"].lower()
    assert "hourly" in text and "bundled" in text


def test_the_labour_sensitivity_scales_hands_and_nothing_else():
    doc = wcc.build()
    for exp in doc["experiments"]:
        row = doc["labour_sensitivity"]["per_experiment"][exp["id"]]
        hands = sum(l["amount_usd"] for l in exp["lines"]
                    if wcc.what_you_are_buying(l["rate_key"]) == "hands")
        assert round(hands, 2) == row["hourly_hands_usd"]
        # at factor 0 exactly the hands come off, nothing more
        assert round(row["at_factor"]["0.0"], 2) == round(exp["total_usd"] - hands, 2)
        # at factor 1 nothing changes
        assert round(row["at_factor"]["1.0"], 2) == exp["total_usd"]


def test_a_pure_service_experiment_is_unmoved_by_free_labour():
    """E2b is 100% bundled service — a labour discount that moved it would be a modelling bug."""
    doc = wcc.build()
    row = doc["labour_sensitivity"]["per_experiment"]["E2b-ASO-ISOGENIC-CONTROL-LINE"]
    assert row["hourly_hands_usd"] == 0.0
    assert row["at_factor"]["0.0"] == row["at_factor"]["1.0"] == row["total_usd"]


def test_the_floor_with_free_hands_is_not_near_the_cost_filter():
    """The load-bearing finding: free labour does not make these buyable."""
    doc = wcc.build()
    ls = doc["labour_sensitivity"]
    for exp_id, row in ls["per_experiment"].items():
        assert row["at_factor"]["0.0"] > 1000, (
            f"{exp_id} falls under the $1,000 filter with free hands — if this ever becomes true "
            f"the memo's conclusion needs rewriting, not the assertion relaxing")
    assert ls["portfolio_floor_with_free_hands_usd"] > 0


def test_the_automation_evidence_is_labelled_as_a_vendors_claim():
    """It is marketing. If that label ever comes off, the artifact starts asserting it as fact."""
    doc = wcc.build()
    a = doc["automation_evidence"]
    assert a["_provenance"].startswith("MARKETING")
    assert "vendor" in a["_provenance"].lower()
    assert str(a["cache"]).startswith("literature/")


def test_the_automation_block_carries_its_own_counter_evidence():
    """A vendor claim recorded without the thing that cuts against it is advertising, not evidence."""
    doc = wcc.build()
    a = doc["automation_evidence"]
    counter = a["_the_counter_evidence_from_the_same_vendor"].lower()
    assert "operatortime" in counter.replace(" ", "").lower()
    assert "still" in counter
    assert "quote-only" in a["_and_the_price_is_still_not_published"].lower()


def test_the_automation_implications_are_derived_from_the_quoted_figures():
    doc = wcc.build()
    a = doc["automation_evidence"]
    trad, cloud, der = a["traditional_lab"], a["cloud_lab"], a["derived"]
    assert der["headcount_usd_per_sample_traditional"] == round(
        trad["headcount_usd_per_year"] / trad["samples_per_year"], 2)
    assert der["headcount_usd_per_sample_cloud"] == round(
        cloud["headcount_usd_per_year"] / cloud["samples_per_year"], 2)
    assert der["throughput_multiple"] == round(
        cloud["samples_per_year"] / trad["samples_per_year"], 2)


def test_the_layer_automation_removes_is_the_one_the_model_calls_hands():
    """The mapping is the argument. If it stops holding, the sensitivity stops meaning anything."""
    doc = wcc.build()
    detail = doc["automation_evidence"]["_the_load_bearing_detail"].lower()
    assert "technician" in detail
    assert "hands" in detail
    assert "scientists stay" in detail
