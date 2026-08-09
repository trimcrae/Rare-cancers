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
PAPER = os.path.join(MANUSCRIPTS, "response-endpoint-indolent-tumours.md")


def _load(name):
    with open(os.path.join(MANUSCRIPTS, name), encoding="utf-8") as fh:
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


def test_the_manuscript_names_its_producers(paper):
    for producer in ("endpoint_corpus.py", "orr_dcr_reread.py", "endpoint_regime_map.py",
                     "placebo_arm_calibration.py", "endpoint_prior_art_audit.py"):
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
