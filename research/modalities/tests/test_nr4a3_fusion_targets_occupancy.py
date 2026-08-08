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
    """Every excluded peak set must say WHY, and the three reasons are not interchangeable.

    UNINFORMATIVE and NO_BACKGROUND_PANEL are both absent readings — the instrument could not look.
    NOT_AN_NR4A_ANTIGEN is different in kind and must not be described as one: those peak sets were
    read perfectly well, they simply assay CTCF or a histone mark and so are not evidence about NR4A
    occupancy either way. Calling that an absent reading would imply the question was asked and went
    unanswered, when it was never the question.
    """
    absent, wrong_assay = 0, 0
    for name, v in art["per_peakset"].items():
        if v.get("informative"):
            continue
        assert "genes" not in v, f"{name} emitted per-gene numbers from an undetectable peak set"
        if v["_status"] == "NOT_AN_NR4A_ANTIGEN":
            wrong_assay += 1
            assert "not an NR4A protein" in v["_means"]
            assert "ABSENT READING" not in v["_means"], (
                f"{name} assays the wrong protein; that is not an absent reading")
            continue
        absent += 1
        assert v["_status"] in ("UNINFORMATIVE", "NO_BACKGROUND_PANEL_ON_THIS_BUILD"), name
        assert "ABSENT READING" in v["_means"]
    assert absent > 0, "no uninformative peak sets were exercised"
    assert wrong_assay > 0, (
        "no non-NR4A peak set was exercised — the Haller deposit's CTCF/H3K27ac/H3K4me3 files are "
        "the reason this branch exists, and they went into an 'NR4A occupancy' test once already")


def test_the_informative_NR4A3_peaksets_are_the_haller_deposit_and_only_those(art):
    """⭐ THIS TEST FIRED, AND THE MANUSCRIPT WAS REWRITTEN RATHER THAN THE TEST RELAXED.

    It used to assert that EVERY NR4A3 peak set is uninformative, which was true of all twelve
    ChIP-Atlas sets (53-154 peaks, recovering no panel gene) and was the basis for §3.11 saying the
    surrogates cannot substitute for the missing fusion cistrome. The Haller 2019 acinic cell
    carcinoma deposit (Zenodo 10.5281/zenodo.1483691) carries four NR4A3 ChIPs at 8,501-18,666
    peaks — 55-121x the deepest previous one — and they ARE informative. §3.11, Table 9, the
    abstract and Limitation 16 were revised to match.

    What it pins now is the boundary: the deep NR4A3 sets are exactly the Haller ones, and every
    ChIP-Atlas NR4A3 set is still uninformative. If a future refresh moves either side, the
    manuscript moves with it."""
    nr4a3 = [(n, v) for n, v in art["per_peakset"].items()
             if (v.get("antigen") or "").upper() == "NR4A3"]
    assert nr4a3, "no NR4A3 peak sets were read at all"
    informative = sorted(n for n, v in nr4a3 if v.get("informative"))
    assert informative, (
        "no NR4A3 peak set is informative any more — the paper's occupancy axis has lost the only "
        "direct NR4A3 data it has; check the Zenodo merge before touching this test")
    assert all(n.startswith("ZENODO1483691:") for n in informative), (
        f"an NR4A3 set outside the Haller deposit is now informative: {informative}")
    assert len(informative) == 4, informative
    for n, v in nr4a3:
        if n.startswith("ZENODO1483691:"):
            assert v["n_peaks_total"] > 8000, (n, v["n_peaks_total"])
        else:
            assert not v.get("informative"), f"{n} is now informative — revise §3.11, not this test"


def test_the_deep_NR4A3_data_shows_no_tumour_specific_enrichment_at_any_class_A_gene(art):
    """The result that matters, and the one a reader will most want to check.

    The occupancy negative is no longer carried entirely by a paralogue: it now includes four deep
    NR4A3 ChIPs (8,501-18,666 peaks) in human tissue -- three acinic cell carcinomas and one NORMAL
    parotid gland. Measured state:

      * PPARG carries ZERO promoter-window peaks in all four (p = 1.0 each). Filion et al. report a
        perfect NBRE at -675 bp and a band shift for this promoter, so this is a real tension and
        §3.11 says so rather than smoothing it.
      * SEMA3C carries at most one, in one sample.
      * ENO3 carries 2-4 in every sample and clears the panel in exactly ONE -- the normal parotid
        gland (p = 0.0348), not any tumour. A signal present in normal tissue and absent from the
        carcinomas is the opposite shape from a tumour-driven one.

    So the assertion is not "nothing is ever nominally significant" -- 2 of 36 tests at p < 0.05
    against 1.8 expected is chance, and demanding zero would be demanding a result cleaner than
    chance allows. It is that no class-A gene clears its panel in a TUMOUR sample.
    """
    tumour = {n: v for n, v in art["per_peakset"].items()
              if n.startswith("ZENODO1483691:") and "AciCC" in n and v.get("informative")}
    assert len(tumour) == 3, sorted(tumour)
    for n, v in tumour.items():
        for g, r in (v.get("genes") or {}).items():
            assert not r["enriched_at_0_05"], (
                f"{g} is enriched in the tumour sample {n} (p={r['empirical_p_vs_panel']}) -- this "
                "is a POSITIVE occupancy result and §3.11, §3.12 and the abstract must be rewritten")

    # PPARG's zero is now a REAL negative rather than an absent reading, because these sets recover
    # half the background panel. That distinction is the whole point of the informativeness rule.
    for n, v in tumour.items():
        assert v["genes"]["PPARG"]["n_peaks_promoter_window"] == 0, n
        assert v["panel"]["fraction_with_a_promoter_peak"] > 0.4, (
            f"{n} no longer recovers enough of the panel for its zeros to mean anything")


def test_the_single_nominal_hit_is_in_normal_tissue_not_a_tumour(art):
    """Pinned because the direction is what makes it uninteresting, and a future refresh that moved
    it into a carcinoma would be a different paper."""
    hits = [(n, g) for n, v in art["per_peakset"].items() if n.startswith("ZENODO1483691:")
            and v.get("informative")
            for g, r in (v.get("genes") or {}).items() if r["enriched_at_0_05"]]
    assert hits == [(
        "ZENODO1483691:Parotid_Gland3_NR4A3_peaks_05be8421f1989fd1a9b0a0bbf7cd6a6f.bed", "ENO3")], hits


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
    # ⛔ A COUNT AGAINST A FRACTIONAL EXPECTATION IS NOT A TEST, and asserting `observed <= expected`
    # was the same error the module itself made: when the Haller data took the panel from 8 distinct
    # experiments to 12, the counts went to 2 observed against 1.8 expected — a coin flip — and both
    # this assertion and the module's verdict flipped, the latter to "at least one class-A gene
    # exceeds the background panel more often than chance would give." That sentence was one commit
    # from the manuscript. The question is how often chance alone gives at least this many.
    assert m["p_this_many_or_more_by_chance"] >= 0.05, (
        f"the nominal-hit count now exceeds chance (binomial p = "
        f"{m['p_this_many_or_more_by_chance']}); §3.11 and the abstract must be revised")
    assert m["excess_over_chance_at_0_05"] is False


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
