"""Every headline figure in the endpoint manuscript still equals its artifact.

WHY THIS EXISTS. The producers all have --check, so an artifact cannot drift from the data it was
derived from. Nothing checked the other seam: the manuscript PROSE, which quotes those artifacts by
hand. A regenerated artifact whose numbers moved would leave the paper quietly wrong, and the paper
is the deliverable.

This is narrower than lint_consistency.py, which enforces that a pinned figure has one home across
the whole corpus. Here the question is only whether the specific numbers the manuscript asserts are
the numbers its own artifacts currently hold.

WHAT IT CANNOT CATCH. A figure the manuscript states that no artifact owns, and a sentence that
quotes the right number for the wrong quantity. Both need a reader.
"""
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
PAPER = os.path.join(MANUSCRIPTS, "endpoint", "response-endpoint-indolent-tumours.md")


def _load(name):
    with open(os.path.join(MANUSCRIPTS, "endpoint", name), encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def paper():
    with open(PAPER, encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def figures():
    rr = _load("orr-dcr-reread.json")
    rm = _load("endpoint-regime-map.json")
    pc = _load("placebo-arm-calibration.json")
    pa = _load("endpoint-prior-art-audit.json")
    co = _load("endpoint-corpus.json")

    dist = rr["R3_distribution_summary"]["all_arms"]
    corner = rr["R3_distribution_summary"]["low_response_high_stability_corner"]
    census = rr["R5_reporting_census"]
    emc_row = rr["R7_emc_row_in_the_field_distribution"]
    reads = rm["G4_what_the_map_reads"]
    emc_map = rm["G5_emc_as_the_worked_extreme"]
    cls = pc["P3_classification"]
    gap = pc["P6_the_corner_with_no_control_arms"]

    return {
        "arms": dist["arms"],
        "median gap": dist["median_gap_pp"],
        "IQR lower": dist["iqr_gap_pp"][0],
        "IQR upper": dist["iqr_gap_pp"][1],
        "arms at or above 50 points": dist["arms_at_or_above"]["50"],
        "low-response/high-stability arms": corner["arms"],
        "distinct trials": census["distinct_trials"],
        "studies screened": census["studies_screened"],
        "studies not re-readable": census["studies_with_posted_results_but_no_four_cell_block"],
        "share not re-readable": census["share_of_screened_studies_not_re_readable_pct"],
        "EMC percentile": emc_row["emc_percentile_in_the_corpus"],
        "conditions placed": reads["conditions_placed"],
        "conditions below the design contour":
            reads["conditions_whose_median_trial_is_below_the_design_contour"],
        "conditions below the zero-event contour":
            reads["conditions_whose_median_trial_is_below_the_zero_event_contour"],
        "EMC n for one response": emc_map["n_needed_for_90pct_chance_of_one_response"],
        "EMC n for a design": emc_map["n_needed_for_a_single_stage_design_vs_null_5pct"],
        "control arms found": cls["control_arms_found"],
        "backboned control arms": cls["counts"]["control_plus_active_backbone"],
        "low-response conditions": gap["conditions_in_the_low_response_regime"],
        "low-response conditions with a control arm":
            gap["of_those_with_any_control_arm_in_this_corpus"],
        "prior-art documents": len(pa["A1_endorsed_alternatives"]),
        "abstracts screened": co["A2_why_not_abstracts"]["unique_abstracts_screened"],
    }


def _appears(text, value):
    """A number appears if it is present, with or without thousands separators.

    Matched on a word boundary so that 44 does not satisfy a search for 4, which would make the
    whole test vacuous for small integers.
    """
    candidates = {str(value)}
    if isinstance(value, int) and abs(value) >= 1000:
        candidates.add(f"{value:,}")
    return any(re.search(r"(?<![\d.,])" + re.escape(c) + r"(?![\d,]*\d)", text)
               for c in candidates)


def test_every_headline_figure_appears_in_the_manuscript(paper, figures):
    missing = {k: v for k, v in figures.items() if not _appears(paper, v)}
    assert not missing, (
        "the manuscript no longer carries these artifact figures, so either a producer was "
        f"regenerated and the prose was not updated, or a figure was reworded: {missing}")


#: JNCI's structured-abstract limit, and the reason the abstract was cut from 543 words. The
#: section labels are not counted, matching how a journal's own word count treats them.
ABSTRACT_WORD_LIMIT = 305


def test_the_abstract_fits_the_target_venue_word_limit(paper):
    """The abstract must stay submittable without anyone remembering to recount it.

    The count was checked by hand once and then drifted over the limit twice within a single
    session's edits, each time by a few words added to the Results. A hand count is exactly the kind
    of fact that goes stale silently: nothing about an over-long abstract looks wrong on the page.
    """
    body = paper.split("## Abstract", 1)[1].split("\n---\n", 1)[0]
    body = re.sub(r"\*\*(Background|Methods|Results|Conclusions)\.\*\*", "", body)
    words = [w for w in re.sub(r"\*", "", body).split() if w.strip()]
    assert len(words) <= ABSTRACT_WORD_LIMIT, (
        f"the abstract is {len(words)} words against a {ABSTRACT_WORD_LIMIT}-word limit; trim it "
        f"rather than raising the constant, unless the target venue changed")


def test_the_manuscript_names_its_producers(paper):
    for producer in ("endpoint_corpus.py", "orr_dcr_reread.py", "endpoint_regime_map.py",
                     "placebo_arm_calibration.py", "endpoint_prior_art_audit.py",
                     "endpoint_regime_figure.py", "endpoint_result_figures.py"):
        assert producer in paper, f"{producer} is not reproducible from the manuscript"


def test_the_retired_paper_is_gone_and_only_named_as_a_supersession(paper):
    """The single-disease paper was retired into this one.

    A LIVE POINTER -- a markdown link -- would resurrect the parallel-draft anti-pattern the rename
    exists to prevent. A PLAIN MENTION in Appendix A is the opposite: CLAUDE.md rule 1.2 requires a
    superseded value to record where it lived, so naming the retired file there is mandatory
    bookkeeping. The first version of this test forbade both and was wrong about the second.
    """
    assert not os.path.exists(os.path.join(MANUSCRIPTS, "emc-response-endpoint-paper.md")), (
        "the retired paper is back on disk, which means there are two drafts again")

    links = re.findall(r"\]\(\.?/?[^)]*emc-response-endpoint-paper\.md[^)]*\)", paper)
    assert not links, f"live markdown link to the retired paper: {links}"

    appendix = paper.split("## Appendix A", 1)
    body = appendix[0]
    assert "emc-response-endpoint-paper.md" not in body, (
        "the retired paper is named in the running text. Its only legitimate mention is the "
        "supersession record in Appendix A")


def test_every_citation_marker_resolves_and_every_reference_is_cited(paper):
    """The reference list must be a bibliography, not decoration.

    Before 2026-08-09 the paper carried a numbered list of 19 references and NOT ONE bracketed
    in-text marker -- every citation was a bare `PMID nnnnnnn`, so the numbering mapped to nothing
    and two references were cited nowhere at all. The list is now built from the identifiers cited in
    the body, in order of first appearance, from metadata the fetches returned.
    """
    head, tail = paper.split("## 12. References", 1)
    refs = tail.split("\n---\n", 1)[0]

    cited = set()
    for m in re.finditer(r"\[([0-9]+(?:,[0-9]+)*)\]", head):
        cited.update(int(n) for n in m.group(1).split(","))
    listed = {int(m.group(1)) for m in re.finditer(r"^(\d+)\. ", refs, re.M)}

    assert cited, "the body carries no citation markers at all"
    assert not cited - listed, f"markers with no reference entry: {sorted(cited - listed)}"
    assert not listed - cited, f"reference entries cited nowhere: {sorted(listed - cited)}"
    assert listed == set(range(1, len(listed) + 1)), "reference numbering has a gap"
    assert not re.search(r"PMID \d", head), (
        "a bare PMID survives in the body; citations belong in the reference list")


def test_every_reference_entry_carries_its_identifier(paper):
    refs = paper.split("## 12. References", 1)[1].split("\n---\n", 1)[0]
    for line in refs.strip().split("\n"):
        if not line.strip():
            continue
        assert re.search(r"PMID \d{6,9}", line), f"reference without a PMID: {line[:80]}"


def test_the_results_headline_counts_are_the_corpus_artifacts_own(paper):
    """⛔⛔ THE RESULTS SENTENCE OF THIS PAPER WAS WATCHED BY NOTHING UNTIL 2026-08-28 (AUT-PD-132).

    "**Results.** 552 arms from 138 trials carried a complete table." Perturbing 552 -> 557 and
    138 -> 137 turned NO guard red. It is the sentence a reader quotes when they describe what this
    manuscript did, and both numbers are the denominators every later rate divides by.

    ★ FOUND BY GIVING THE DOCUMENT A GATE AT ALL. The paper carried no `COVERAGE_FLOOR` row, so it
    sat outside the sampled ablation gate entirely; adding the floor — which
    `test_every_ablation_exemption_names_a_censused_sentence_and_says_why` demanded before it would
    accept an exemption here — brought the document in, and the gate failed on its first run with
    this sentence. A document with no floor is not a document that passed.

    ⭐ BOTH VALUES DERIVED from `endpoint-corpus.json`'s `C6_counts`, whose field names say what the
    prose says: `arms_with_a_complete_four_cell_table` and `distinct_trials`.
    """
    corpus = _load("endpoint-corpus.json")
    counts = corpus["C6_counts"]
    arms = counts["arms_with_a_complete_four_cell_table"]
    trials = counts["distinct_trials"]
    assert isinstance(arms, int) and isinstance(trials, int), (
        "the corpus artifact no longer states these counts as integers, so this guard cannot bind "
        "the Results sentence to them")

    stated = set(re.findall(r"(\d+) arms from (\d+) trials", paper))
    assert stated == {(str(arms), str(trials))}, (
        f"the manuscript states {sorted(stated)} arms-from-trials where endpoint-corpus.json's "
        f"C6_counts holds ({arms}, {trials}). These are the denominators every rate in the paper "
        f"divides by, so a drift here misstates the whole Results section.")
