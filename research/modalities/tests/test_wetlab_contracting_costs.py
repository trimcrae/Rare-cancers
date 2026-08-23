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
