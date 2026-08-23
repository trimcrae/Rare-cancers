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


# ---------------------------------------------------------------------------------------------
# ⭐ Added 2026-08-23 with the class II panel widening (3 DRB1 alleles -> 23 across DR, DP and DQ),
# answering aiXiv reviews 1364 and 1365. The widening creates a failure mode the three-allele panel
# did not have: MHCnuggets carries no model for some DP and DQ alleles, and an allele it could not
# score folded silently into "no strong binder on the panel" would convert an UNSCREENED allele into
# a NEGATIVE RESULT — in the one section of the paper whose whole point is that a narrow panel
# bounds nothing.
def test_an_unscreenable_class_ii_allele_is_named_and_not_counted_as_a_negative():
    import json as _json
    import os as _os
    demo = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                         "patient-cd4-demo.json")
    if not _os.path.exists(demo):
        import pytest as _pytest
        _pytest.skip("patient-cd4-demo.json not generated here")
    with open(demo) as fh:
        d = _json.load(fh)
    if "alleles_without_a_model" not in d:
        import pytest as _pytest
        _pytest.skip("artifact predates the widened panel; regenerated in the next CI run")
    missing = set(d["alleles_without_a_model"])
    assert d["n_alleles_screened"] == len(d["patient_class2_hla"]) - len(missing)
    scored = {r["allele"] for r in d.get("all_predictions", [])}
    assert not (scored & missing), "an allele reported as unscreenable carries predictions"
    assert d["⚠_missing_model_is_not_a_negative"]


def test_the_class_ii_artifact_records_its_predictor_like_the_class_i_one_does():
    """⛔ The preprint checklist carried this as an open item and §8 disclosed it as a gap.

    A screen whose predictor version is unknown cannot be re-run by a reader, and the class I
    artifact had recorded tool, version and models release all along. The asymmetry was the defect.
    ⚠ An UNKNOWN version is acceptable and a MISSING block is not: MHCnuggets does not always expose
    a version, and an honest unknown is a reproducibility statement while an absent field is silence.
    """
    import json as _json
    import os as _os
    demo = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                         "patient-cd4-demo.json")
    if not _os.path.exists(demo):
        import pytest as _pytest
        _pytest.skip("patient-cd4-demo.json not generated here")
    with open(demo) as fh:
        d = _json.load(fh)
    if "_predictor" not in d:
        import pytest as _pytest
        _pytest.skip("artifact predates the provenance block; regenerated in the next CI run")
    pr = d["_predictor"]
    assert pr["tool"] == "MHCnuggets"
    assert pr["version"], "the version field is empty; UNKNOWN is a value, blank is not"
    assert pr["thresholds"]["strong_ic50_nM"] and pr["thresholds"]["binder_ic50_nM"]
    assert pr["alleles"], "the panel the screen ran on is not recorded"
