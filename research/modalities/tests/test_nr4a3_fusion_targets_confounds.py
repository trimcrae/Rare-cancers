#!/usr/bin/env python3
"""Offline tests for `nr4a3_fusion_targets_confounds.py`.

THE PROPERTIES UNDER TEST ARE THE HONESTY ONES. This module's job is to bound a published reading,
so every way it could flatter that reading is a way it could do harm:

  1. a covariate panel built from EMC-selected genes is REFUSED, not quietly used. This is not
     hypothetical -- the first draft used VCAN and HAPLN1, both of which sit in the EMC-derived
     Filion lists, and it produced a confident result of the OPPOSITE SIGN to the clean panel;
  2. two caches are never merged into one scale unless they demonstrably are one scale, and the
     per-gene guard covers exactly the genes the module reads, with the rest reported rather than
     suppressed;
  3. a sensitivity analysis of a different quantity from the one the paper reports is worse than
     none, so the module refuses to write if its re-derived deltas leave the committed artifact;
  4. an absent reading is never rendered as a reading of absence -- no muscle reference on a
     platform means the control is unavailable there, NOT that the confound is excluded;
  5. a contrast below the floor emits a status, never a number.
"""
import copy
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import nr4a3_fusion_targets_confounds as C  # noqa: E402


@pytest.fixture(scope="module")
def artifact():
    if not os.path.exists(C.OUT):
        pytest.skip("artifact not built in this checkout")
    with open(C.OUT) as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def primary():
    with open(C.PRIMARY) as fh:
        return json.load(fh)


# =============================================================================================
# 1 -- the provenance guard on the covariate panel
# =============================================================================================
def test_a_covariate_panel_containing_an_EMC_selected_gene_is_refused(primary, monkeypatch):
    """The bug that actually happened, pinned so it cannot happen again.

    HAPLN1 is in Filion Table 1 -- a list built by selecting genes that separate EMC from other
    sarcomas. Adjusting on it removes EMC signal by construction."""
    monkeypatch.setattr(C, "MATRIX_PANEL_CANDIDATES",
                        C.MATRIX_PANEL_CANDIDATES + ["HAPLN1"])
    with pytest.raises(SystemExit) as e:
        C._provenance_audit(primary)
    assert "HAPLN1" in str(e.value)
    assert "circular" in str(e.value).lower()


def test_the_shipped_panels_are_disjoint_from_every_gene_the_manuscript_scores(primary):
    audit, panels = C._provenance_audit(primary)
    scored = C._scored_gene_universe(primary)
    assert not audit["rejected"]
    assert panels["matrix"], "the matrix panel must not be empty"
    for name, members in panels.items():
        assert not (set(members) & scored), f"{name} panel overlaps the scored universe"


def test_the_scored_universe_actually_contains_the_EMC_derived_lists(primary):
    """A guard that passes because it is looking at nothing is worse than no guard."""
    scored = C._scored_gene_universe(primary)
    assert {"HAPLN1", "VCAN"} <= scored
    assert {"ENO3", "PPARG", "SEMA3C"} <= scored
    assert len(scored) > 500


# =============================================================================================
# 2 -- the two-cache merge
# =============================================================================================
def _tiny(gsms=("A", "B", "C"), genes=None, bg=None):
    n = len(gsms)
    return {
        "n_samples": n,
        "samples": [{"gsm": g, "title": g, "annotation_verbatim": g} for g in gsms],
        "background_per_sample": bg or [{"mean": 0.0, "sd": 1.0}] * n,
        "genes": genes or {},
    }


def test_a_sample_order_mismatch_refuses_the_merge():
    a = _tiny(("A", "B", "C"))
    b = _tiny(("C", "B", "A"))
    with pytest.raises(SystemExit) as e:
        C._merge_gene_sources(a, b, set())
    assert "sample" in str(e.value).lower()


def test_a_background_mismatch_refuses_the_merge():
    a = _tiny()
    b = _tiny(bg=[{"mean": 5.0, "sd": 1.0}] * 3)
    with pytest.raises(SystemExit) as e:
        C._merge_gene_sources(a, b, set())
    assert "background" in str(e.value).lower()


def test_a_disagreement_on_a_gene_the_module_reads_refuses_the_merge():
    a = _tiny(genes={"ENO3": {"values": [1.0, 2.0, 3.0], "n_probes_mapping": 1}})
    b = _tiny(genes={"ENO3": {"values": [9.0, 2.0, 3.0], "n_probes_mapping": 2}})
    with pytest.raises(SystemExit) as e:
        C._merge_gene_sources(a, b, {"ENO3"})
    assert "refusing to merge" in str(e.value)


def test_a_disagreement_on_a_gene_nothing_reads_is_recorded_not_suppressed():
    """The real case: ACAA1 disagrees between the two caches and no analysis here touches it.

    The merge proceeds, and the disagreement still appears in the artifact with its cause."""
    a = _tiny(genes={"ACAA1": {"values": [1.0, 2.0, 3.0], "n_probes_mapping": 2}})
    b = _tiny(genes={"ACAA1": {"values": [9.0, 2.0, 3.0], "n_probes_mapping": 1}})
    merged, rec = C._merge_gene_sources(a, b, {"ENO3"})
    assert merged is not None
    assert rec["n_shared_genes_disagreeing"] == 1
    assert "ACAA1" in rec["shared_genes_disagreeing"]
    assert rec["shared_genes_disagreeing"]["ACAA1"]["n_probes_primary_cache"] == 2
    assert rec["shared_genes_disagreeing"]["ACAA1"]["n_probes_secondary_cache"] == 1


def test_the_merge_adds_genes_the_primary_cache_lacks():
    a = _tiny(genes={"ENO3": {"values": [1.0, 2.0, 3.0], "n_probes_mapping": 1}})
    b = _tiny(genes={"ENO3": {"values": [1.0, 2.0, 3.0], "n_probes_mapping": 1},
                     "PLAGL1": {"values": [4.0, 5.0, 6.0], "n_probes_mapping": 1}})
    merged, rec = C._merge_gene_sources(a, b, {"ENO3"})
    assert "PLAGL1" in merged["genes"]
    assert rec["n_added_from_secondary"] == 1


def test_PLAGL1_the_directional_falsifier_is_readable_on_both_platforms(artifact):
    """The whole reason the merge exists. If it regresses, the falsifier goes unaudited."""
    for plat, v in artifact["platforms"].items():
        row = v["restricted_comparator_arms"]["per_gene"]["PLAGL1"]
        assert row.get("_status") != "NOT_READABLE", plat


# =============================================================================================
# 3 -- agreement with the artifact the manuscript actually reports
# =============================================================================================
def test_every_platform_agrees_with_the_committed_primary_artifact(artifact):
    for plat, v in artifact["platforms"].items():
        g = v["agreement_with_primary_artifact"]
        assert g["agrees"], f"{plat}: {g['worst_abs_difference']}"
        assert g["n_rows_checked"] >= 4, f"{plat} checked too few rows to mean anything"


def test_the_agreement_guard_can_actually_fail(primary):
    """A guard that cannot fail is decoration. Perturb the committed value and demand a refusal."""
    hacked = copy.deepcopy(primary)
    plat = "GSE24369_series_matrix.txt.gz"
    hacked["gene_reads"]["ENO3"][plat]["null_calibration"]["observed_delta"] = 99.0
    with open(C.PANELS_INPUTS) as fh:
        tgt = json.load(fh)["targets"][plat]
    _, emc, comp, _ = C._arms(tgt)
    rec = C._agreement_guard(tgt, plat, emc, comp, hacked)
    assert rec["agrees"] is False
    assert rec["worst_abs_difference"] > 90


# =============================================================================================
# 4 -- an absent reading is not a reading of absence
# =============================================================================================
def test_a_platform_with_no_muscle_reference_says_so_rather_than_clearing_the_confound(artifact):
    for plat, v in artifact["platforms"].items():
        m = v["muscle_admixture"]
        if m.get("_status") == "NO_MUSCLE_REFERENCE_ON_THIS_PLATFORM":
            assert "NOT a reading that the confound is absent" in m["_means"]
        else:
            assert m["n_muscle_reference_samples"] >= 1
            assert m["genes"], plat


def test_the_muscle_control_reads_a_marker_more_muscle_restricted_than_ENO3(artifact):
    """The control only discriminates if something in it out-ranks ENO3 in muscle.

    Otherwise 'ENO3 is high in muscle' has no comparator and the reading says nothing."""
    for plat, v in artifact["platforms"].items():
        m = v["muscle_admixture"]
        if m.get("_status"):
            continue
        eno = m["genes"].get("ENO3", {}).get("muscle_reference_mean_percentile")
        markers = [r["muscle_reference_mean_percentile"] for g, r in m["genes"].items()
                   if r.get("is_muscle_marker")]
        assert markers, f"{plat}: no muscle marker was readable"
        assert max(markers) >= eno, f"{plat}: no marker is as muscle-restricted as ENO3"


def test_an_unreadable_gene_says_the_read_could_not_be_taken(artifact):
    for v in artifact["platforms"].values():
        for g, row in v["restricted_comparator_arms"]["per_gene"].items():
            if row.get("_status") == "NOT_READABLE":
                assert "NOT a statement" in row["_means"]


# =============================================================================================
# 5 -- floors, and the sensitivity analysis is labelled as one
# =============================================================================================
def test_a_below_floor_contrast_emits_a_status_and_never_a_number(artifact):
    for v in artifact["platforms"].values():
        for row in v["restricted_comparator_arms"]["per_gene"].values():
            for arm, cell in row.items():
                if isinstance(cell, dict) and cell.get("_status") == "BELOW_FLOOR":
                    assert "delta" not in cell, arm


def test_the_covariate_adjustment_is_labelled_a_sensitivity_analysis_not_a_correction(artifact):
    for v in artifact["platforms"].values():
        note = v["covariate_adjusted"]["_this_is_a_sensitivity_analysis"]
        assert "NOT a correction" in note
        assert "over-adjustment" in note


def test_a_covariate_that_does_not_separate_the_arms_does_not_move_the_contrast(artifact):
    """The method's own null control.

    On GPL3290 the matrix panel barely differs between the arms, so adjusting on it CANNOT be
    what moves a contrast. If this ever fails, the regression is picking up something other than
    the covariate."""
    v = artifact["platforms"].get("GSE4303-GPL3290_series_matrix.txt.gz")
    if not v:
        pytest.skip("platform absent")
    sep = v["covariate_adjusted"]["panels"]["matrix"].get("arm_separation")
    if not sep or abs(sep["delta"]) > 0.05:
        pytest.skip("the matrix panel does separate the arms here; this control does not apply")
    for g, row in v["covariate_adjusted"]["genes"].items():
        adj = row.get("adjusted", {}).get("matrix", {})
        frac = adj.get("fraction_of_raw_retained")
        if frac is not None:
            assert 0.9 <= frac <= 1.1, f"{g} moved {frac} on a covariate that does not separate"


def test_minimum_detectable_effect_never_calls_a_set_cleared_inside_its_own_band(artifact):
    for name, per in artifact["minimum_detectable_effect"]["sets"].items():
        for plat, r in per.items():
            lo, hi = r["null_95_band"]
            inside = lo <= r["observed_delta"] <= hi
            assert r["cleared"] is not inside, f"{name}/{plat}"
            if not r["cleared"]:
                assert r["fraction_of_threshold_reached"] <= 1.0000001


def test_the_language_discipline_note_denies_the_forbidden_claims(artifact):
    note = artifact["_language_discipline"]
    for word in ("efficacy", "selectivity", "safety", "clinical"):
        assert word in note
    assert "occupancy" in note


def test_the_committed_artifact_is_current():
    """The artifact must be a derivation of the committed inputs, not a hand-edited file."""
    assert C.main.__module__
    fresh = C.derive()
    with open(C.OUT) as fh:
        have = json.load(fh)
    assert C._strip_volatile(have) == C._strip_volatile(fresh)
