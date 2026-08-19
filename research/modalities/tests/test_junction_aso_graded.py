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
    #: ⛔ NOT A SKIP (2026-08-19, lane C2 audit). Both the screen and its graded companion ARE
    #: committed, so the skip's own message could never be true where it matters — and the
    #: retired-headline check it guards is the one that keeps a superseded count from coming back.
    if not os.path.exists(p):
        pytest.fail(f"{os.path.basename(p)} is missing at {p}; it is committed, and the graded "
                    "screen's retired headline is unchecked without it.")
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


def test_exactly_the_orientation_clean_designs_reach_zero_predicted_cleavage_load():
    """The paper's headline, asserted over the whole graded corpus rather than one panel.

    ⭐ THIS TEST FIRED AS DESIGNED AND THE CLAIM IT GUARDED CHANGED (2026-08-12). It previously
    asserted `n_zero == 0` — no design predicted-clean under either literature bound — and its own
    docstring said that a non-zero count would mean "the manuscript's central claim has changed".
    It was a tripwire, not a prohibition, and it tripped for the right reason.

    ⛔ WHAT CHANGED WAS AN ERROR, NOT THE SCIENCE. `grade_one` scored `gap_mismatch_histogram`,
    which counts every ranked hit REGARDLESS OF STRAND. `blastn` searches both strands, and a
    transcript carrying the reverse complement of the target window cannot be hybridised by an
    antisense oligonucleotide — there is no duplex, so there is nothing for RNase H1 to cleave and
    nothing to score. The four designs at TCF12 exons 7, 9 and 17 have ZERO plus-strand
    near-matches; every one of their 8, 2, 1 and 7 hits is minus-strand. Their previous non-zero
    load was cleavage predicted on transcripts they cannot bind.

    ⚠ A ZERO HERE IS ARITHMETIC, NOT A MEASUREMENT. These designs have no hybridisable hit to
    score, so the load is zero under any discrimination bound; that is weaker than a bound-specific
    finding and the manuscript says so where it reports it. What the zero does establish is that
    the harsher of the two bounds does not move them, because there is nothing for it to act on.

    ⛔ STILL A TRIPWIRE, NOW POINTED THE OTHER WAY. A FIFTH design reaching zero, or any design
    outside TCF12 e7/e9/e17 reaching zero, fails this test — because with the strand filter correct
    the only remaining route to a zero is a censored design whose unseen tail was assumed away.
    """
    import aso_screen_sets as ass
    # ⚠ TEN, NOT NINE, AND THE EXTRA ONE IS THE POINT. The manuscript reports nine clean designs;
    # this set has ten. `GCATATCTCCTCGCCC` at FUS e11 returns 21 near-matches with only 15 retained,
    # all of them minus-strand — so the graded model sees nothing hybridisable and scores zero,
    # while the cleanliness criterion refuses it because the six unretained hits are unknown.
    # `grade_one` has NO censoring guard, so it can award a zero its hit list does not support.
    # Asserted rather than filtered out, so that gap stays visible.
    expected = {"GGGCATATCCGTGGAC", "GGCATATCCGTGGACG", "GCATATCCGTGGACGC",
                "AGGGCATATCGGAGTC", "GGGCATATCCGACATG", "GCATATCTCCTCGCCC",
                "GGGCATATCTCTATAA", "CAGGGCATATCTTGCA", "GGCATATCAAGCGCTG", "GCATATCAAGCGCTGC"}
    n_designs = n_junctions = 0
    zero_seqs, zero_junctions = set(), set()
    # ⛔ THE CLEAN SET IS A CLAIM ABOUT THE MANUSCRIPT'S PANEL, so the population is one geometry.
    # A graded re-score of an 18-mer screen carries different sequences at the same junctions, and
    # folding one into `zero_seqs` would change a set §3.5 of the paper is written from. No such
    # artifact exists yet — because `grade_panel` had a defect of its own that this pass fixed —
    # which is exactly the shape of latency this guard is for.
    for s in ass.load_screens(ass.MANUSCRIPT_GEOMETRY, ass.GRADED_RESCORE, root=HERE):
        g = s.artifact
        if g.get("source_screen") is None:
            continue                      # the modelled codon-space panel, not a real junction
        n_junctions += 1
        n_designs += len(g["per_oligo"]["ostergaard_5fold"])
        # per_oligo is {model: {antisense: row}}, keyed by sequence rather than a list
        for rows in g["per_oligo"].values():
            for seq, r in rows.items():
                if r.get("zero_predicted_cleavage_load"):
                    zero_seqs.add(seq)
                    zero_junctions.add(g.get("junction_label") or g["source_screen"])
    assert n_junctions >= 12, f"only {n_junctions} real junctions graded"
    assert n_designs >= 58, f"only {n_designs} designs graded"
    assert zero_seqs == expected, (
        f"the set of predicted-clean designs changed: {sorted(zero_seqs)}")
    assert zero_junctions == {"EWSR1_e1__NR4A3_e3", "FUS_e8__NR4A3_e3", "FUS_e11__NR4A3_e3",
                              "TAF15_e1__NR4A3_e3", "TCF12_e7__NR4A3_e3",
                              "TCF12_e9__NR4A3_e3", "TCF12_e17__NR4A3_e3"}, sorted(zero_junctions)


def test_a_zero_load_is_never_awarded_to_a_design_with_a_hybridisable_hit():
    """The property that makes the zeroes above meaningful, asserted directly on the screens.

    A design scores zero only if it has no plus-strand near-match at all. If a design with even one
    hybridisable hit ever scored zero, the load would be measuring the strand filter rather than
    the transcriptome.
    """
    import aso_screen_sets as ass
    import junction_aso_offtarget as jo
    # ⚠ THIS ONE IS A PER-FILE INVARIANT, SO IT WANTS EVERY GEOMETRY — and takes them one geometry
    # at a time rather than as a pooled glob. The property is asked of each screen against its own
    # counters and nothing is summed across screens, so a longer geometry is one more case to check
    # rather than a contaminant. What the loader adds over the glob is that each file has been
    # MEASURED and checked against its own stated gap span before this test reads it.
    every = [s for _g, ss in ass.iter_geometries(ass.BLAST_SCREEN, root=HERE) for s in ss]
    for s in every:
        screen = s.artifact
        # ⚠ A COVERAGE-ONLY SCREEN IS EXCLUDED HERE FOR THE SAME REASON `--rescore` REFUSES IT.
        # `junction-aso-offtarget-bp200-8.json` records no gap-mismatch depth and no strand, so
        # `grade_one` reads absent fields as zero and returns a zero load manufactured out of the
        # missing data — the defect the gap-resolution guard exists to stop. Asking this property
        # of a screen that cannot answer it tests the guard, not the grading.
        if not jo.screen_is_gap_resolved(screen)[0]:
            continue
        for o in screen.get("oligos", []):
            if o.get("status") != "screened":
                continue
            plus = [h for h in (o.get("offtargets") or []) if not h.get("is_minus_strand")]
            for fold in (5.0, 1.0):
                if jo.grade_one(o, fold)["zero_predicted_cleavage_load"]:
                    assert not plus, (
                        f"{s.name} / {o['antisense_5to3']} scored zero load with "
                        f"{len(plus)} hybridisable hit(s)")
