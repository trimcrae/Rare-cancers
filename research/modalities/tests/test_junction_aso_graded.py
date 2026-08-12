"""THE GRADED OFF-TARGET RE-SCORE — pinned so the abolition assumption cannot come back.

⛔ WHAT WENT WRONG. `junction_aso_offtarget.classify` labels a near-match whose mismatch falls inside the
6-nt DNA gap `gap_disrupted_no_cleavage`. That label is a statement about WHERE the mismatch fell. The panel
summary then counted every such hit as **zero-cleavable**, which is a statement about WHETHER the transcript
is cleaved — a different and much stronger claim — and it produced the manuscript headline "2 of 5 gapmers
predicted off-target-clean".

⛔ THE LITERATURE DOES NOT SUPPORT ABOLITION, AND THE LENGTH-MATCHED SOURCE ARGUES AGAINST DISCRIMINATION
AT ALL. PMID 23963702 measures ~5-fold discrimination for an UNMODIFIED RNase-H-active ASO (>100-fold needs
positional chemistry these designs lack); PMID 7567450 reports 16mers "did not discriminate efficiently",
and every design in this panel is a 16-mer. So the assumption the paper called *conservative* was
optimistic, and the panel is now scored as a residual cleavage load under BOTH bounds.

⭐ WHY THESE TESTS READ THE COMMITTED ARTIFACTS RATHER THAN A FIXTURE. The defect was an aggregation over a
real, committed screen, and it survived because the aggregation was never checked against what the labels
mean. A synthetic fixture would have passed under the buggy code too.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import junction_aso as ja  # noqa: E402
import junction_aso_offtarget as jo  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREEN = os.path.join(HERE, "junction-aso-offtarget-bp200-8-gapres.json")
GRADED = os.path.join(HERE, "junction-aso-offtarget-bp200-8-gapres-graded.json")

# The retired headline. Named ONCE; every assertion points at the name.
RETIRED_HEADLINE_N_CLEAN = 2
PANEL_N_OLIGOS = 5


def _load(p):
    if not os.path.exists(p):
        pytest.skip(f"{os.path.basename(p)} not committed in this tree")
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_the_two_sources_the_model_rests_on_are_named_in_the_module():
    """A fold value with no citation beside it is the thing this correction exists to prevent."""
    srcs = " ".join(m["source"] for m in jo.DISCRIMINATION_MODELS.values())
    assert "23963702" in srcs, "the ~5-fold bound must name PMID 23963702"
    assert "7567450" in srcs, "the no-discrimination bound must name PMID 7567450"


def test_the_pessimistic_bound_is_the_one_that_matches_this_panels_oligo_length():
    """PMID 7567450's finding is a LENGTH effect at 16-mers, and these designs are 16-mers.

    If the panel ever moves to 12-13mers the pessimistic bound stops applying — and that is a
    decision a human must make, so this test fails loudly rather than letting the length drift."""
    assert ja.OLIGO_LEN == 16, (
        "OLIGO_LEN moved off 16. The duroux_16mer_none bound is length-specific; re-read "
        "PMID 7567450 before re-using it at a different length.")


def test_abolition_is_not_among_the_models_that_can_score_the_panel():
    """`fold = inf` is what produced '2 of 5'. It stays NAMED, so the old figure is traceable, and
    stays OUT of the scoring models, so it cannot produce a headline again."""
    assert "all_gap_mismatch_blocks_cleavage" not in jo.DISCRIMINATION_MODELS
    assert jo.RETIRED_ABOLITION_MODEL["fold_per_gap_mismatch"] == float("inf")
    for name, m in jo.DISCRIMINATION_MODELS.items():
        assert m["fold_per_gap_mismatch"] != float("inf"), f"{name} reintroduces abolition"


def test_a_gap_disrupted_offtarget_is_never_weighted_zero_under_any_live_model():
    """The whole correction in one assertion: reduced, not abolished."""
    for name, m in jo.DISCRIMINATION_MODELS.items():
        for n_mm in range(1, jo.MAX_MISMATCHES_PER_NEAR_MATCH + 1):
            w = jo.cleavage_weight(n_mm, m["fold_per_gap_mismatch"])
            assert w > 0.0, f"{name} scores a {n_mm}-mismatch gap-disrupted hit as zero-cleavable"


def test_a_full_gap_duplex_offtarget_carries_full_weight():
    for m in jo.DISCRIMINATION_MODELS.values():
        assert jo.cleavage_weight(0, m["fold_per_gap_mismatch"]) == 1.0


def test_the_pessimistic_bound_removes_the_discrimination_entirely():
    """fold 1.0 means a gap mismatch buys nothing, so the load is just the near-match count."""
    m = jo.DISCRIMINATION_MODELS["duroux_16mer_none"]
    assert jo.cleavage_weight(2, m["fold_per_gap_mismatch"]) == 1.0


@pytest.mark.committed_artifact
def test_the_committed_panel_still_carries_the_retired_headline_the_correction_names():
    """If the source screen changes, the correction's 'was 2 of 5' stops being true of it and the
    Appendix A row and the manuscript both need re-deriving. Fail rather than drift."""
    s = _load(SCREEN)
    assert s["n_oligos_no_true_cleavage_risk"] == RETIRED_HEADLINE_N_CLEAN
    assert s["n_screened_ok"] == PANEL_N_OLIGOS


@pytest.mark.committed_artifact
def test_the_graded_panel_reports_zero_clean_under_every_model():
    """The new headline. 0 of 5 under BOTH bounds — not one, and not an average of them."""
    g = _load(GRADED)
    assert set(g["models"]) == set(jo.DISCRIMINATION_MODELS)
    for name, m in g["models"].items():
        assert m["n_oligos_with_zero_predicted_cleavage_load"] == 0, (
            f"{name} restores a clean call; the manuscript headline is 0 of {PANEL_N_OLIGOS}")


@pytest.mark.committed_artifact
def test_only_the_top_two_of_the_rank_order_are_model_invariant():
    """The manuscript may quote the top two as a ranking and no more. Positions 3-5 swap between
    the two bounds, and quoting them would present a model artefact as a result."""
    g = _load(GRADED)
    ranks = [m["rank_best_first"] for m in g["models"].values()]
    assert len({tuple(r[:2]) for r in ranks}) == 1, "the top two are no longer model-invariant"
    assert len({tuple(r) for r in ranks}) > 1, (
        "the full orderings now agree — the manuscript's 'only the top two may be quoted' caveat "
        "has become false and must be re-derived rather than left standing")


@pytest.mark.committed_artifact
def test_the_graded_panel_regenerates_from_the_committed_screen():
    """Offline, no network: the artifact must be reproducible from its own stated input."""
    g = _load(GRADED)
    fresh = jo.grade_panel(_load(SCREEN))
    assert fresh["models"] == g["models"]
    assert fresh["per_oligo"] == g["per_oligo"]


@pytest.mark.committed_artifact
def test_a_truncated_offtarget_list_yields_an_interval_and_says_so():
    """The saved list is capped at 15 while the counters are complete, so a truncated oligo must
    report lo < hi and exact=False — never a point estimate that hides the missing tail."""
    g = _load(GRADED)
    rows = g["per_oligo"]["ostergaard_5fold"]
    truncated = [r for r in rows.values() if r["n_gap_disrupted_unresolved_by_truncation"] > 0]
    assert truncated, "expected at least one truncated oligo in this panel"
    for r in truncated:
        assert r["exact"] is False
        assert r["residual_cleavage_load_lo"] < r["residual_cleavage_load_hi"]
    for r in rows.values():
        if r["n_gap_disrupted_unresolved_by_truncation"] == 0:
            assert r["exact"] is True
            assert r["residual_cleavage_load_lo"] == r["residual_cleavage_load_hi"]


def test_wing_only_hits_are_excluded_from_cleavage_but_not_called_harmless():
    """A hit that never reaches the gap has no gap duplex, so it scores 0 for CLEAVAGE — and the
    artifact must still surface it, because 'not cleavable' is not 'not a liability'."""
    g = _load(GRADED)
    for rows in g["per_oligo"].values():
        for r in rows.values():
            assert "n_wing_only_not_counted" in r
    assert any("affinity" in s for s in g["_what_this_is_not"])


def test_the_artifact_refuses_efficacy_safety_and_window_language():
    """Language discipline is asserted here too, not only in lint_claims: this artifact is the one
    a reader reaches for when the manuscript's number looks surprising."""
    g = _load(GRADED)
    blob = json.dumps(g).lower()
    for banned in ("therapeutic window", "is safe", "will work", "clinically ready"):
        assert banned not in blob, f"graded artifact asserts {banned!r}"


def test_a_coverage_only_screen_is_REFUSED_not_scored_as_clean():
    """⛔ THE GUARD THAT STOPS MISSING DATA BECOMING A CLEAN CALL (added 2026-08-12).

    `--rescore` was swept across every committed screen and one of them —
    `junction-aso-offtarget-bp200-8.json` — is the pre-gap-resolution COVERAGE-ONLY screen. Its
    oligos carry `n_true_cleavage_risk: null` and no `gap_mismatch_histogram`, and `grade_one`
    reads absent fields through `int(... or 0)`. Every term evaluated to zero and the graded
    artifact announced "4 of 4 with zero predicted cleavage load" — the strongest claim the model
    can make, manufactured out of the absence of the data needed to test it, in the exact file a
    reader would quote to call a design clean. This test is the reason that cannot recur.
    """
    import junction_aso_offtarget as jo
    coverage_only = {"oligos": [
        {"antisense_5to3": "A" * 16, "status": "screened",
         "n_true_cleavage_risk": None, "n_gap_disrupted_no_cleavage": 3, "offtargets": []}]}
    ok, why = jo.screen_is_gap_resolved(coverage_only)
    assert ok is False
    assert "coverage-only" in why and "not zero" in why

    resolved_by_histogram = {"oligos": [
        {"antisense_5to3": "A" * 16, "status": "screened",
         "gap_mismatch_histogram": {"0": 2, "1": 1}, "offtargets": []}]}
    assert jo.screen_is_gap_resolved(resolved_by_histogram)[0] is True

    resolved_by_counter = {"oligos": [
        {"antisense_5to3": "A" * 16, "status": "screened",
         "n_true_cleavage_risk": 0, "n_gap_disrupted_no_cleavage": 1, "offtargets": []}]}
    assert jo.screen_is_gap_resolved(resolved_by_counter)[0] is True

    assert jo.screen_is_gap_resolved({"oligos": []})[0] is False


def test_no_design_at_any_real_junction_reaches_zero_predicted_cleavage_load():
    """The paper's headline negative, asserted over the whole graded corpus rather than one panel.

    If this ever passes with a non-zero count, a design has become predicted-clean under a
    literature-supported model and the manuscript's central claim has changed.
    """
    import glob
    n_designs = n_zero = n_junctions = 0
    for p in sorted(glob.glob(os.path.join(HERE, "junction-aso-offtarget-*-graded.json"))):
        g = _load(p)
        if g.get("source_screen") is None:
            continue                      # the modelled codon-space panel, not a real junction
        n_junctions += 1
        n_designs += len(g["per_oligo"]["ostergaard_5fold"])
        for m in g["models"].values():
            n_zero += m["n_oligos_with_zero_predicted_cleavage_load"]
    assert n_junctions >= 12, f"only {n_junctions} real junctions graded"
    assert n_designs >= 58, f"only {n_designs} designs graded"
    assert n_zero == 0, f"{n_zero} design(s) now score zero predicted cleavage load"
