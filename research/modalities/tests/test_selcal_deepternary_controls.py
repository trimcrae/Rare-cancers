"""The DeepTernary head-to-head on the two selcal systems — set up so it can only tell us something true.

Our co-folds score DockQ 0.023-0.046 on the target<->VHL interface of these systems. The fix asks whether a
different generator does better on the SAME targets, SAME instruments, SAME references. These tests pin the
three things that make that question answerable rather than decorative.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import selcal_deepternary_controls as C  # noqa: E402


def test_the_arms_are_the_two_systems_our_cofolds_already_failed_on():
    """A head-to-head on different targets would not be a head-to-head."""
    import selcal_panel as P
    dep = P.REFERENCE["deposited_ternaries"]
    assert {a["pdb"] for a in C.ARMS} == {dep["SMARCA2"], dep["SMARCA4"]}


def test_blindness_is_verified_from_the_committed_artifact_before_anything_is_sourced():
    ok, detail = C.leakage_is_clear()
    assert ok is True, detail
    assert "absent from the disclosed exclusion set" in detail


def test_a_reference_that_might_have_been_seen_refuses_the_whole_build(tmp_path):
    """⚠ A blind control that is not blind is WORSE than no control: it yields a number that looks like
    validation. So an unclear leakage state stops the sourcing, rather than being noted and worked around."""
    p = tmp_path / "leak.json"
    p.write_text(json.dumps({"structures": [{"pdb": "9DTY", "in_training_or_exclusion_set": True},
                                            {"pdb": "9DTX", "in_training_or_exclusion_set": False}]}))
    ok, detail = C.leakage_is_clear(str(p))
    assert ok is False and "9DTY" in detail and "may not be used as a blind control" in detail


def test_a_missing_leakage_artifact_refuses_rather_than_assuming_blind():
    ok, detail = C.leakage_is_clear("/nonexistent/leak.json")
    assert ok is False and "blindness unverified" in detail


def test_the_expected_result_is_recorded_as_unknown_not_as_the_qualification_numbers():
    """The 0.62-0.83 figures are on structures inside DeepTernary's exclusion set. Quoting them here would
    make an open experiment sound like a fix with a known answer."""
    src = " ".join(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                     "selcal_deepternary_controls.py")).read().split())
    assert "DO NOT QUOTE 0.62-0.83" in src
    assert "should be assumed worse" in src


def test_the_isoform_suffix_is_dropped_only_for_the_rcsb_query():
    """`selcal_stage` uses P51531-2 because the construct numbering is isoform-specific; RCSB indexes the base
    accession. The drop must be local to the query and must not touch the construct definition."""
    import selcal_stage as S
    assert S.CONSTRUCTS["SMARCA2"]["accession"] == "P51531-2", "the construct definition was altered"
    assert any(a["poi_uniprot_base"] == "P51531" for a in C.ARMS)
    for ctl in C.controls():
        assert all("-" not in u for u in ctl["uniprots"]), "an isoform suffix reached the RCSB query"


def test_both_arms_carry_the_full_vcb_so_the_e3_side_resolves():
    for ctl in C.controls():
        for acc in ("P40337", "Q15369", "Q15370"):
            assert acc in ctl["uniprots"], acc


def test_a_pass_licenses_one_sentence_and_says_which():
    # whitespace-normalised: the assertions are about WORDING, and a re-wrapped line is not a changed claim
    src = " ".join(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                     "selcal_deepternary_controls.py")).read().split())
    assert "licenses exactly one sentence" in src
    assert "It says NOTHING about NR4A3" in src
    assert "whose bound is unchanged by anything here" in src
