"""The class-II seam provenance check in hla_coverage.

Regression test for a gate that cried wolf. On 2026-08-19 the class-II arm was rebuilt on exactly
the corrected seam, and the provenance check reported a MISMATCH anyway, because the two producers
render the seam at different flank widths and the check was a raw string equality. The banner it
raised said the combined figures were not quotable, about the one condition it exists to detect, at
the moment that condition had been fixed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hla_coverage as hc  # noqa: E402


CORRECTED = "SQQSSSYGQQ|NMPCVQAQYSP"          # this module's rendering: 10 left, novel + 10 right
CD4_RENDERING = "QYSQQSSSYGQQ|NMPCVQAQYSPS"   # patient_cd4_epitopes.py's: 12 and 12
RETRACTED = "QYSQQSSSYGQQ|IVRTDSLKGRRG"       # the superseded CDS-model seam


def test_the_same_seam_at_different_flank_widths_agrees():
    assert hc.seam_contexts_agree(CD4_RENDERING, CORRECTED) is True
    assert hc.seam_contexts_agree(CORRECTED, CD4_RENDERING) is True, "must be symmetric"


def test_the_retracted_seam_still_reads_as_a_mismatch():
    assert hc.seam_contexts_agree(RETRACTED, CORRECTED) is False


def test_a_difference_inside_the_overlap_is_caught():
    # differs at the last left residue, which is inside the compared window
    assert hc.seam_contexts_agree("QYSQQSSSYGQA|NMPCVQAQYSPS", CORRECTED) is False
    # differs at the first right residue
    assert hc.seam_contexts_agree("QYSQQSSSYGQQ|DMPCVQAQYSPS", CORRECTED) is False


def test_a_difference_outside_the_shorter_flank_cannot_be_seen_and_that_is_the_contract():
    # The extra left residues that only the wider rendering carries are not compared, because the
    # narrower side has nothing to compare them against. Stated as a test so the limit is explicit.
    assert hc.seam_contexts_agree("ZZSQQSSSYGQQ|NMPCVQAQYSPS", CORRECTED) is True


def test_unusable_input_is_none_rather_than_agreement():
    for a, b in (("", CORRECTED), (None, CORRECTED), (CORRECTED, ""),
                 ("QYSQQSSSYGQQNMPCVQAQYSPS", CORRECTED),   # no seam marker
                 ("|NMPCVQAQYSPS", CORRECTED),              # empty left flank
                 ("QYSQQSSSYGQQ|", CORRECTED)):             # empty right flank
        assert hc.seam_contexts_agree(a, b) is None, (a, b)


def test_none_is_treated_as_not_established_by_the_caller():
    # The caller writes the banner when the grade is falsy, so None must keep raising it.
    assert not None
    grade = hc.class_ii_seam_grade({"junction_context": ""})
    assert grade["matches_corrected_seam"] in (None, False)
    assert grade["⛔"], "an unestablished provenance must still say so"
