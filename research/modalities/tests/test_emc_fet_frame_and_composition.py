"""The frame rule, the seam arithmetic and the symmetric sweep, held against the committed inputs.

WHY THESE TESTS AND NOT OTHERS. The module has one job that a plausible-looking artifact can fail
silently at, and it is the same job the manuscript got wrong: the seam arithmetic. "176 nucleotides
encode 59 residues" is false by one nucleotide and reads perfectly, because 176 is close enough to
177 that nobody multiplies. So the arithmetic is asserted as a divisibility fact rather than as a
remembered pair of numbers, and the frame rule is asserted as an equivalence over every donor exon
rather than on the four junctions the manuscript happens to report.

The module reads only committed files, so unlike its siblings it runs offline here.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import emc_fet_frame_and_composition as fc  # noqa: E402


@pytest.fixture(scope="module")
def art():
    return fc.derive()


def test_the_committed_artifact_reproduces(capsys):
    assert fc.main(["--check"]) == 0
    assert "REPRODUCES" in capsys.readouterr().out


def test_the_extension_spans_a_whole_number_of_codons(art):
    """The defect this module was written for: 176 nt cannot encode 59 residues."""
    seam = art["type2_seam"]
    span = seam["nucleotides_spanned_by_the_extra_residues"]
    assert span % 3 == 0, "an extension spanning a non-multiple of three is an arithmetic error"
    assert span == seam["extra_residues"] * 3
    assert span == (seam["ewsr1_nucleotides_donated_across_the_seam"]
                    + seam["nr4a3_5utr_nt_retained_total"])
    assert seam["nr4a3_5utr_nt_retained_total"] % 3 != 0, (
        "the NR4A3 contribution alone is not a whole number of codons — that is the whole point, "
        "and a test that let it be one would not catch the sentence the manuscript shipped")


def test_the_retained_utr_is_two_exons_worth(art):
    seam = art["type2_seam"]
    assert (seam["nr4a3_5utr_nt_from_exon_2"] + seam["nr4a3_5utr_nt_from_exon_3"]
            == seam["nr4a3_5utr_nt_retained_total"])
    assert seam["nr4a3_5utr_nt_from_exon_2"] % 3 == 0, (
        "NR4A3 exon 2 being a multiple of three is why both acceptors give the same register")


def test_the_extension_translates_without_an_internal_stop_and_keeps_nr4a3_whole(art):
    seam = art["type2_seam"]
    assert seam["internal_stop_codon_in_the_extension"] is False
    assert len(seam["extra_residue_sequence"]) == seam["extra_residues"]
    assert seam["nr4a3_moiety_complete"] is True
    assert seam["matches_committed_construct_artifact"] is True
    assert (seam["ewsr1_whole_codons"] + seam["extra_residues"] + 626
            == seam["chimeric_orf_length_aa"])


def test_the_frame_rule_is_an_equivalence_over_every_donor_exon(art):
    fr = art["frame_rule"]
    for row in fr["ewsr1_donor_exons"]:
        expected = row["donor_end_phase"] == 1
        assert row["in_frame_with_nr4a3_exon_2"] is expected
        assert row["in_frame_with_nr4a3_exon_3"] is expected
    assert fr["rule_holds_for_every_ewsr1_donor"] is True
    assert fr["taf15_exon_6"]["donor_end_phase"] == 1


def test_the_rule_agrees_with_the_independently_committed_frame_audit(art):
    assert art["frame_rule"]["_cross_check_against_committed_audit"]["disagreements"] == []


def test_the_prefix_sweep_is_symmetric(art):
    """Every protein gets the same grid; the asymmetric version overstated the separation."""
    sw = art["composition"]["symmetric_prefix_sweep"]
    per = sw["per_protein"]
    assert set(per) >= {"EWSR1", "TAF15", "FUS", "TCF12"}
    for name, row in per.items():
        expected = len(range(fc.PREFIX_MIN, row["length_aa"] + 1, fc.PREFIX_STEP))
        assert row["n_prefixes"] == expected, f"{name} was not swept on the shared grid"
    assert sw["any_tcf12_prefix_reaches_the_lowest_fet_prefix"] is False
    assert 0 < sw["gap"] < 0.10, (
        "the conclusion survives the symmetric test and the margin is narrow; a gap outside this "
        "band means the comparison changed and the manuscript's wording has to change with it")


def test_the_axis_reports_the_atf1_comparator_as_a_span(art):
    rows = art["recruitment_axis_rows"]
    lo, hi = rows["atf1_comparator_span"]
    assert lo == 0.0 and hi > lo, (
        "three EWSR1::ATF1 breakpoints are reported and the source's construct is not pinned to "
        "one of them, so the comparator cannot be a point")
    assert any(a["fraction"] is None for a in rows["source_anchors"]), (
        "the RGG(1) anchor has no placeable RG count and must stay visible as unplaceable")


def test_every_counted_series_is_quoted_from_a_committed_abstract(art):
    freq = art["counted_fusion_type_frequencies"]
    assert len(freq["series"]) == 3
    lit_path = fc.LIT
    with open(lit_path, encoding="utf-8") as fh:
        blob = fh.read()
    for s in freq["series"]:
        assert s["quotation"] in blob, (
            f"{s['series']} quotation is not a substring of the committed retrieval record — a "
            f"quotation that cannot be found in its source was typed rather than extracted")
