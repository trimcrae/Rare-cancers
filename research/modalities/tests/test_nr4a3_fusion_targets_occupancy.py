#!/usr/bin/env python3
"""Offline tests for `nr4a3_fusion_targets_occupancy.py`.

The properties under test are the ones that decide whether an occupancy reading is honest, and each
of them is a way this module could have flattered the manuscript:

  1. a raw peak count is never a finding. In the deepest catalogue 82.8% of arbitrary genes carry a
     promoter-window peak, so "ENO3 has 6 peaks" means nothing without the panel it is placed
     against — the same uncalibrated-fold-change error the manuscript's §1.3 exists to refuse, and
     the one this analysis walked into on its first pass;
  2. a zero from a peak set too shallow to recover ANY arbitrary gene is an absent reading, never
     evidence of non-occupancy. All 12 NR4A3-specific sets are in that state;
  3. multiplicity is counted over distinct EXPERIMENTS, not per genome build — the same ChIP-seq
     experiment lifted to hg19 and hg38 is one test, and counting it twice would turn ENO3's single
     borderline value into two apparently independent ones;
  4. the re-derived counts must equal the committed cistrome artifact, or the axis is measuring
     something the repository does not own.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import nr4a3_fusion_targets_occupancy as O  # noqa: E402


@pytest.fixture(scope="module")
def art():
    if not os.path.exists(O.OUT):
        pytest.skip("occupancy artifact not built in this checkout")
    with open(O.OUT) as fh:
        return json.load(fh)


# =============================================================================================
# 1 -- a raw count is never a finding
# =============================================================================================
def test_no_informative_peakset_reports_a_count_without_its_panel_p(art):
    for name, v in art["per_peakset"].items():
        if not v.get("informative"):
            continue
        assert v["panel"]["n_genes"] >= O.MIN_PANEL_GENES, name
        for g, cell in (v.get("genes") or {}).items():
            if "n_peaks_promoter_window" in cell:
                assert "empirical_p_vs_panel" in cell, f"{name}/{g} reports a bare count"


def test_the_panel_saturation_is_reported_beside_every_peakset(art):
    """The number that makes a raw count meaningless has to be visible next to it.

    Where there is no panel at all — the mouse builds carry only the orthologous focus loci — the
    peak set must say SO, rather than reporting a null saturation as if it were a low one."""
    for name, v in art["per_peakset"].items():
        if v["panel"]["fraction_with_a_promoter_peak"] is None:
            assert v["panel"]["n_genes"] == 0, name
            assert v["_status"] == "NO_BACKGROUND_PANEL_ON_THIS_BUILD", name
            assert "ABSENT READING" in v["_means"], name
            continue
    deep = art["per_peakset"].get("REMAP2022_NR4A1")
    if deep:
        assert deep["panel"]["fraction_with_a_promoter_peak"] > 0.5, (
            "the deepest catalogue should be saturated; if this ever fails the 'a raw count is "
            "worthless' argument in the module docstring needs re-measuring, not re-asserting")


def test_the_empirical_p_can_never_be_zero():
    p, _ = O._empirical_p(99, [0] * 198)
    assert p == round(1 / 199, 4)     # the artifact rounds to 4 dp; the floor survives rounding
    assert p > 0


def test_a_gene_at_the_panel_median_gets_an_unremarkable_p():
    panel = list(range(100))
    p, _ = O._empirical_p(50, panel)
    assert 0.4 < p < 0.6


# =============================================================================================
# 2 -- an absent reading is not a reading of absence
# =============================================================================================
def test_a_peakset_that_recovers_no_arbitrary_gene_is_uninformative_not_negative(art):
    seen = 0
    for name, v in art["per_peakset"].items():
        if v.get("informative"):
            continue
        seen += 1
        assert v["_status"] in ("UNINFORMATIVE", "NO_BACKGROUND_PANEL_ON_THIS_BUILD"), name
        assert "ABSENT READING" in v["_means"]
        assert "genes" not in v, f"{name} emitted per-gene numbers from an undetectable peak set"
    assert seen > 0, "no uninformative peak sets were exercised"


def test_every_NR4A3_specific_peakset_is_uninformative(art):
    """The load-bearing one: the manuscript may not say NR4A3 'does not bind' these genes.

    All NR4A3 sets are 53-154 peaks and recover no panel gene, so their silence carries no
    information. If one ever becomes informative, the manuscript's §3.11 wording must change."""
    nr4a3 = [(n, v) for n, v in art["per_peakset"].items() if v.get("antigen") == "NR4A3"]
    assert nr4a3, "no NR4A3 peak sets were read at all"
    for n, v in nr4a3:
        assert not v.get("informative"), (
            f"{n} is now informative — §3.11 of the manuscript must be rewritten, not left alone")


def test_the_verdict_denies_that_this_shows_the_genes_are_unbound(art):
    v = art["verdict"]["⛔ what_this_is_not"]
    assert "NOT a measurement of the fusion" in v
    assert "NOT evidence that these genes are unbound" in v
    assert "paralogue" in v


# =============================================================================================
# 3 -- multiplicity over experiments, not builds
# =============================================================================================
def test_multiplicity_counts_experiments_not_genome_builds(art):
    verdict = art["verdict"]
    n_exp = verdict["n_informative_experiments"]
    n_pk = verdict["n_informative_peaksets"]
    assert n_exp <= n_pk
    assert verdict["multiplicity"]["n_tests"] == n_exp * len(O.CLASS_A)
    # the same accession must not appear twice in the experiment list
    exps = verdict["informative_experiments"]
    assert len(exps) == len(set(exps))
    assert not any("@" in e for e in exps), "a build suffix leaked into the experiment list"


def test_a_gene_gets_one_p_per_experiment_not_one_per_build(art):
    for g, s in art["per_gene_summary"].items():
        by_exp = s["empirical_p_by_experiment"]
        assert len(by_exp) == s["n_informative_experiments"], g
        assert not any("@" in k for k in by_exp), g


def test_the_headline_compares_observed_hits_against_chance(art):
    m = art["verdict"]["multiplicity"]
    assert m["n_enriched_at_0_05_expected_by_chance"] == pytest.approx(0.05 * m["n_tests"], rel=1e-6)
    assert str(m["n_enriched_at_0_05_observed"]) in art["verdict"]["headline"]
    assert str(m["n_tests"]) in art["verdict"]["headline"]


def test_no_class_A_gene_is_enriched_beyond_chance(art):
    """The measured state as of this commit. If it changes, the manuscript changes with it —
    this test exists so a data refresh cannot silently flip the paper's claim."""
    m = art["verdict"]["multiplicity"]
    assert m["n_enriched_at_0_05_observed"] <= m["n_enriched_at_0_05_expected_by_chance"] + 1e-9, (
        "an occupancy enrichment now exceeds chance; §3.11 and the abstract must be revised")


# =============================================================================================
# 4 -- parity with the artifact the repository owns
# =============================================================================================
def test_every_re_derived_count_matches_the_committed_cistrome(art):
    p = art["parity_with_committed_artifact"]
    assert p["agrees"], p["disagreements"]
    assert p["n_rows_checked"] > 500, "too few rows compared for parity to mean anything"


def test_the_window_is_the_same_one_the_motif_scan_used(art):
    """If these drift apart, the sequence axis and the occupancy axis stop asking about one region."""
    w = art["_window"]
    assert (w["upstream_bp"], w["downstream_bp"]) == (10000, 15000)
    assert w["strand_aware"] is True


def test_the_committed_artifact_is_current():
    fresh = O.derive()
    with open(O.OUT) as fh:
        have = json.load(fh)
    assert O._strip(have) == O._strip(fresh)
