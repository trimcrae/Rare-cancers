#!/usr/bin/env python3
"""Guards for the PRMT5 route controls.

The two that matter are the double-entry check (the module's *t* must equal the one the committed
panel already carries, by a different code path) and the absent-reading check (a control whose genes
are not on the panel must say NOT MEASURED and must never read as a null).
"""
from __future__ import annotations

import json
import os
import sys

import pytest

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MOD)

import emc_prmt5_route_controls as C  # noqa: E402

PANEL = os.path.join(MOD, "emc-expression-panels.json")
pytestmark = pytest.mark.skipif(not os.path.exists(PANEL),
                                reason="the expression panel is not in this checkout")


@pytest.fixture(scope="module")
def panel():
    with open(PANEL, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def res(panel):
    return C.build()


def test_the_welch_t_matches_the_one_the_panel_already_owns(panel, res):
    """⛔ DOUBLE ENTRY. This module recomputes a statistic `emc_expression_panels` already committed.
    They share no code. A disagreement means one of them is not computing what it says."""
    for plat, r in res["per_platform"].items():
        obs = r["exact_permutation_PRMT5"].get("observed_t")
        if obs is None:
            continue
        committed = ((panel["gene_reads"]["PRMT5"].get(plat) or {})
                     .get("welch_EMC_vs_comparator") or {}).get("t")
        assert committed is not None
        assert abs(obs - committed) <= 0.01, (
            f"{plat}: this module gets t={obs}, the panel committed t={committed}")


def test_the_permutation_is_exact_and_reproducible(panel, res):
    """No RNG anywhere: the same inputs must give the same p to the digit, not to a seed.

    ⚠ The repeat is run on GPL3290 only — 8,008 labelings against GPL6244's 1,623,160. Determinism
    is a property of the code, not of the array size, so paying twenty seconds of every preflight to
    re-enumerate the big one would buy nothing."""
    a = C.exact_permutation(panel, C.THE_GENE, C.P3290)
    assert a == C.exact_permutation(panel, C.THE_GENE, C.P3290)
    for plat, r in res["per_platform"].items():
        a = r["exact_permutation_PRMT5"]
        if a.get("exact_p_two_sided") is None:
            continue
        n = a["n_labelings_enumerated"]
        assert a["n_labelings_at_least_as_extreme_two_sided"] >= 1, (
            "the observed labeling is itself in the enumeration, so the count can never be 0")
        assert a["exact_p_two_sided"] >= 1.0 / n - 1e-12, (
            f"{plat}: p={a['exact_p_two_sided']} is below the 1/{n} floor the design allows")


def test_a_control_with_no_genes_reports_not_measured_and_never_a_null(res):
    """⛔ AN ABSENT READING IS NOT A READING OF ABSENCE. Controls whose genes were added to the panel
    definition on 2026-08-09 cannot be scored until a fetch runs; the wording must make that
    impossible to misread as 'no confound found'."""
    for plat, r in res["per_platform"].items():
        for key in ("prmt_family_specificity", "proliferation_control",
                    "chondroid_lineage_control", "genome_wide_placement"):
            block = r[key]
            if block.get("_status") == "run":
                continue
            s = block["_status"]
            assert "NOT MEASURED" in s or "NOT AVAILABLE" in s or "NOT READABLE" in s, s
            assert "no confound" not in s.lower() or "NOT A FINDING" in s.upper()


def test_a_scored_confound_control_reports_its_coverage(res):
    """A score built on one gene and a score built on twelve are different instruments, and a reader
    must not have to guess which one produced a null."""
    for plat, r in res["per_platform"].items():
        for key in ("proliferation_control", "chondroid_lineage_control"):
            block = r[key]
            if block.get("_status") != "run":
                continue
            assert block["genes_used"], "a run control must name the genes it used"
            assert "⚠_coverage" in block
            assert block["PRMT5_t_raw"] is not None


def test_the_chondroid_control_never_claims_to_exclude_the_lineage_confound(res):
    blob = json.dumps(res, ensure_ascii=False)
    assert "cartilage-lineage" in blob and "NOT excluded" in blob
    for plat, r in res["per_platform"].items():
        b = r["chondroid_lineage_control"]
        if b.get("_status") == "run":
            assert "⛔_what_this_cannot_settle" in b


def test_no_efficacy_language(res):
    blob = json.dumps(res, ensure_ascii=False).lower()
    for banned in ("is effective", "will respond", "safe in patients", "therapeutic window in emc"):
        assert banned not in blob
