"""⛔ DID THE FIX LAND, AND DID IT LAND IN EVERY HOME OF THE FACT?

This file exists because round 5 did not. Nine reviewers, adversarial verification, a committed
ledger and nine passing gates, and the application pass still dropped two of eight deposit blockers
silently, applied a third so as to introduce a fresh false statement, and fixed one copy of a
five-copy fact while adding a regression guard that watched only the copy it fixed. Round 6 found all
of it. None of it needed a reviewer -- every one of these assertions is a substring check.

⛔ THE TWO QUESTIONS EVERY ROW HERE ASKS, AND WHY THE SECOND ONE IS THE ONE THAT WAS MISSED:

  1. Did the corrected text arrive?          -- catches a fix reported as applied and never applied.
  2. Is the defective text gone EVERYWHERE?  -- catches a fix applied to the file someone happened
                                                to be editing, while the generator, the artifact and
                                                the rendered companion keep emitting the old claim.

A test that only asks (1) passes on a paper that still ships the defect, because the corrected
sentence and the defective one can coexist in different files. The sign error did exactly that: it
lived in the manuscript, the artifact, two generators and the generated tables markdown, and the
round-5 guard asserted its absence from the manuscript alone.

⚠ ABSENCE ASSERTIONS ARE SCOPED TO SUBMISSION-BOUND FILES, NOT THE WHOLE REPOSITORY. A retraction
note, a review ledger and a superseded-value block are all SUPPOSED to quote the defective wording --
that is what rule 1.2 requires of them. Asserting repo-wide absence would forbid the record of the
correction, so each check names the files the deposit actually carries.
"""
import os
import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# ⛔ FOUR dirnames, not three: this file sits at research/manuscripts/tests/, so three lands on
# research/ and every path below resolves to a file that does not exist. The first version of this
# module had three, and because the reader below SKIPPED on a missing file, all fifteen checks went
# green-by-skip against a tree that still carried every defect they were written for. That is the
# same fail-quiet shape as the defects this file exists to catch, so the reader now FAILS on a
# missing submission file and the root is asserted below rather than assumed.
assert os.path.exists(os.path.join(REPO, "CLAUDE.md")), (
    f"REPO resolved to {REPO!r}, which is not the repository root -- every check below would "
    "otherwise pass by skipping"
)
ART = os.path.join(REPO, "research/manuscripts/aso/fusion-junction-aso-research-article.md")
TABLES = os.path.join(REPO, "research/manuscripts/aso/fusion-junction-aso-submission-tables.md")
LETTER = os.path.join(REPO, "research/manuscripts/aso/fusion-junction-aso-cover-letter.md")
GEN_TABLES = os.path.join(REPO, "research/manuscripts/submission_tables.py")
GEN_TRADE = os.path.join(REPO, "research/modalities/aso_gap_length_tradeoff.py")
GEN_FIG = os.path.join(REPO, "research/manuscripts/figures/aso_gap_length_figure.py")
TRADE_JSON = os.path.join(REPO, "research/modalities/aso-gap-length-tradeoff.json")


def _read(p):
    # ⛔ FAILS rather than skips. Every path here is a submission-bound file that exists in every
    # checkout; a missing one means the resolution is wrong, not that the check is inapplicable.
    assert os.path.exists(p), f"{os.path.relpath(p, REPO)} is missing -- check the path resolution"
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def _flat(s):
    return " ".join(s.split())


# --------------------------------------------------------------------------------------------
# The sign error. FIVE homes. This is the canonical every-home case.
# --------------------------------------------------------------------------------------------

SIGN_ERROR_PHRASINGS = (
    "rise together, nucleotide for nucleotide",
    "costs one nucleotide of contiguous wild-type-parent duplex",
    "gain a nucleotide of margin without handing RNase-H1 one more",
    "no choice of register or gap length avoids it",
)


@pytest.mark.parametrize("path", [ART, TABLES, GEN_TABLES, GEN_TRADE, GEN_FIG, TRADE_JSON])
def test_the_sign_error_is_absent_from_every_home_it_was_found_in(path):
    """Margin + parent-paired gap DNA = gap, so WITHIN a geometry they move inversely.

    The claim that they rise together is true only ACROSS geometries. Round 5 corrected the
    manuscript and left the artifact, both generators and the generated tables emitting the wrong
    direction -- which the deposit carries, since build_submission_pdf bundles the tables markdown.
    """
    body = _read(path)
    for phrase in SIGN_ERROR_PHRASINGS:
        # A supersession block is allowed to quote it; a live claim is not. ⚠ The window is
        # CHARACTERS around the occurrence, not the line containing it: these files wrap, and a
        # line-scoped check reports a correctly-retired quotation as a live claim.
        flat = _flat(body)
        start = 0
        while (i := flat.find(phrase, start)) != -1:
            window = flat[max(0, i - 400):i + len(phrase) + 120]
            assert "uperseded" in window, (
                f"{os.path.relpath(path, REPO)} still asserts the sign error: {phrase!r}. "
                "Margin and parent-paired gap DNA are complements, so at a fixed gap they "
                "move INVERSELY (aso_gap_length_tradeoff.py: parent_dna = gap - margin)."
            )
            start = i + len(phrase)


def test_the_corrected_direction_is_actually_stated_in_the_manuscript():
    txt = _flat(_read(ART))
    assert "move inversely" in txt, "the manuscript no longer states the corrected direction"


# --------------------------------------------------------------------------------------------
# The two round-5 P0s that were reported closed and never applied.
# --------------------------------------------------------------------------------------------

def test_the_load_superlative_is_bounded_to_the_named_reagents():
    """⛔ REPORTED CLOSED IN ROUND 5 AND NEVER TOUCHED.

    The lead reagent's 123 gap-paired near-matches is not the panel maximum: 14 deep records exceed
    it, to 240, and the paper names a reagent at 128 forty-five lines below the abstract's claim.
    """
    txt = _flat(_read(ART))
    assert "heaviest disclosed transcriptome load of any design considered here" not in txt
    assert "heaviest disclosed load of any design considered here" not in txt


def test_the_five_partner_claim_carries_its_search_depth():
    """⛔ ALSO REPORTED CLOSED IN ROUND 5 AND NEVER TOUCHED.

    True at the default ceiling, false at the deeper one the paper ran at all 38 junctions, where
    TFG has no junction whose best design reaches zero.
    """
    txt = _flat(_read(ART))
    if "every one of the five partners has a junction whose best design" in txt:
        raise AssertionError(
            "the Discussion still states the five-partner claim without its depth qualifier"
        )
    assert "four of the five partners" in txt, (
        "the deeper-ceiling count is not stated anywhere in the manuscript"
    )


# --------------------------------------------------------------------------------------------
# Defects the round-5 fixes themselves introduced.
# --------------------------------------------------------------------------------------------

def test_the_paper_does_not_promise_a_reagent_it_then_names():
    """Round 5 wrote 'no reagent is named at that seam below' 24 lines above the PGR sequence."""
    txt = _flat(_read(ART))
    if "5′-AGTGGGCTCTTCCATT-3′" in txt:
        assert "no reagent is named at that seam below" not in txt, (
            "the paper says no reagent is named at the PGR seam and then names one"
        )


def test_selectivity_is_defined_so_that_larger_is_more_selective():
    """Round 5 defined the ratio in the direction opposite to its own cut and its own estimators.

    As written it scored a perfectly selective reagent as falsifying the ranking.
    """
    txt = _flat(_read(ART))
    assert "ratio of wild-type *NR4A3* knockdown to fusion knockdown" not in txt, (
        "the selectivity ratio is inverted: a selective reagent scores below the cut and falsifies"
    )
    assert "larger number is a more selective reagent" in txt


def test_the_replicate_count_is_derived_from_a_variance_rather_than_asserted():
    """Three replicates against a 5.0 cut cannot falsify at all once SD(ln S) exceeds ~0.65."""
    txt = _flat(_read(ART))
    assert "as a floor and not a target" in txt or "set from the pilot estimate" in txt, (
        "the replicate count is still a bare floor with no variance behind it"
    )


def test_the_contrast_arm_does_not_claim_margin_is_the_only_variable():
    """GC, gap-paired load and single-mismatch off-targets all move with the register."""
    txt = _flat(_read(ART))
    assert "so margin is the only variable that moves" not in txt


def test_the_contrast_arm_is_not_said_to_differ_on_a_quantity_where_it_is_identical():
    """Both the arm and the lead reagent carry an 8 bp longest mature-parent duplex."""
    txt = _flat(_read(ART))
    assert "so the arm is not clean in the way the lead reagent is" not in txt


# --------------------------------------------------------------------------------------------
# The remaining round-6 items. Written as ABSENCE checks wherever the defect has a fixed wording
# and the repair does not, so that a correct fix phrased differently from the one I imagined still
# passes. Asserting the exact replacement text would make this file a style guide rather than a
# guard, and would fail on a better sentence than the one I had in mind.
# --------------------------------------------------------------------------------------------

def test_the_introduction_does_not_claim_a_registration_that_has_not_happened():
    """§5 says the threshold is one that *can* be registered; the Introduction claimed it was."""
    assert "the pre-registered threshold" not in _flat(_read(ART))


def test_the_break_apart_assay_is_not_described_as_partner_blind():
    """⛔ THIS SENTENCE HAS NOW BEEN WRONG IN BOTH DIRECTIONS. ONE ROUND EACH.

    Before round 5 it said the assay reports which genes are joined -- backwards, since a break-apart
    probe reports one locus split. Round 5 corrected that and over-reached: it added that the assay
    names no partner, which cannot be true of cohorts that report partner counts for 57 of 58 cases
    (PMID 36948401). The argument only ever needed the SEAM half, so the stable state is that the
    partner clause is absent in both directions and only the seam claim is made.
    """
    txt = _flat(_read(ART))
    for oscillation in (
        "reports which genes are joined",          # the pre-round-5 error
        "neither names the partner nor locates",    # the round-5 over-correction
        "names neither the partner gene nor",       # the same, second home
    ):
        assert oscillation not in txt, (
            f"the break-apart FISH clause is back in a form this has already been wrong in: "
            f"{oscillation!r}. Make the claim about the seam only."
        )


def test_the_panel_junction_count_matches_the_artifact():
    """A regeneration promoted TFG e7 to published tier, making it five, and the prose said four."""
    import json
    p = os.path.join(REPO, "research/modalities/aso-per-junction-table.json")
    n = len([j for j in json.load(open(p))["junctions"]
             if j.get("clinical_tier") == "published_exon_resolved_breakpoint"])
    assert n == 5, f"the artifact now carries {n} published-tier junctions; update this guard and the prose"
    assert "All four junctions of the panel with a published" not in _flat(_read(ART))


def test_the_larger_half_of_the_gap_is_named_correctly():
    """The counted quantity is max(gl, gr), so what cannot be under five is the LARGER half."""
    assert "the smaller half of a gap of ten cannot be under five" not in _flat(_read(ART))


def test_the_ethics_declaration_does_not_say_aggregate_data():
    """Several clinical facts come from single-patient reports, including the PGR breakpoint."""
    assert "published aggregate data" not in _flat(_read(ART))


# --------------------------------------------------------------------------------------------
# Cross-file: a fix applied to the manuscript and not to the packet.
# --------------------------------------------------------------------------------------------

def test_the_cover_letter_carries_the_manuscripts_corrected_reproducibility_claim():
    """The manuscript split code-derived from literature-transcribed figures; the letter did not."""
    letter = _flat(_read(LETTER))
    phrase = "every quantitative statement is produced by code"
    start = 0
    while (i := letter.find(phrase, start)) != -1:
        # Same window rule as the sign-error check: rule 1.2 requires the retired wording to be
        # registered, so a quotation inside a supersession block is the correct state, not a relapse.
        assert "uperseded" in letter[max(0, i - 400):i + len(phrase) + 120], (
            "the cover letter still asserts the unsplit reproducibility claim the manuscript "
            "retracted -- the clinical figures are transcribed, not code-produced"
        )
        start = i + len(phrase)
    assert "transcribed from the publications cited for them" in letter, (
        "the cover letter does not carry the corrected split"
    )
