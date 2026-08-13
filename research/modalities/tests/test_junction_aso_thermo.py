#!/usr/bin/env python3
"""The duplex-thermodynamics module, and the convention check that licenses its numbers.

⛔ THE DANGEROUS FAILURE HERE IS A PLAUSIBLE NUMBER. A nearest-neighbour table is keyed "XY/WZ", and
reversing the strand convention produces free energies of an entirely reasonable magnitude — a
16-mer would still come out around -12 kcal/mol, every downstream comparison would still run, and
nothing would look wrong. That is why the module validates against an independent implementation
rather than asserting its own arithmetic, and why the first test below is the validation itself.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import junction_aso_thermo as T  # noqa: E402

ART = os.path.join(MOD, "junction-aso-thermo.json")


def _table():
    tbl, _ = T._nn_table()
    if tbl is None:
        pytest.skip("Biopython is not installed in this environment")
    return tbl


def _artifact():
    if not os.path.exists(ART):
        pytest.skip("thermo artifact is not committed in this checkout")
    return json.load(open(ART))


def test_the_keying_convention_reproduces_an_independent_implementation():
    """The whole licence for every energy in the artifact.

    ⚠ Salt correction OFF and concentrations matched, or this compares NN-plus-salt against
    NN-alone. The first run of this validation reported 15.2 °C and read as a broken convention;
    it was the salt term, which this module deliberately does not model.
    """
    tbl = _table()
    seqs = ["GGGCATATCTCTATAA", "CAGGGCATATCTTGCA", "GGCATATCAAGCGCTG", "GCATATCAAGCGCTGC",
            "GGGCATATCATCAAAC"]
    v = T._validate_against_biopython(seqs, tbl)
    assert v["ran"] is True
    assert v["agrees"] is True, v
    assert v["max_abs_tm_difference_c"] < 0.01, v


def test_a_reversed_convention_would_be_caught():
    """The check has power: deliberately mis-keying the table must break agreement.

    A validation that passes under both the right and the wrong convention validates nothing.
    """
    tbl = dict(_table())
    swapped = {}
    for k, val in tbl.items():
        if "/" in k and len(k) == 5:
            a, b = k.split("/")
            swapped[f"{a[::-1]}/{b[::-1]}"] = val
        else:
            swapped[k] = val
    dh_ok, _ = T.duplex_enthalpy_entropy("GGGCATATCTCTATAA", tbl)
    dh_bad, _ = T.duplex_enthalpy_entropy("GGGCATATCTCTATAA", swapped)
    assert dh_ok != dh_bad, "reversing the NN keys changed nothing — the check has no power"


def test_a_missing_table_entry_is_fatal_rather_than_skipped():
    """A gap in the table must not silently yield a shorter, more favourable duplex."""
    tbl = dict(_table())
    tbl.pop("AT/TA", None)
    dh, ds = T.duplex_enthalpy_entropy("GATCGATC", tbl)
    assert dh is None and ds is None


def test_no_parameter_is_typed_into_this_repository():
    """Provenance: the table is read from the package that cites its source.

    ⛔ The first golden rule is never to fabricate a citation, and a thermodynamic table recited
    from memory is that failure in numeric form.
    """
    _, prov = T._nn_table()
    if prov is None:
        pytest.skip("Biopython is not installed in this environment")
    assert prov["pmid"] == "7545436"
    assert "Sugimoto" in prov["primary_source"]
    assert prov["table"].startswith("Bio.SeqUtils")
    src = open(os.path.join(MOD, "junction_aso_thermo.py"), encoding="utf-8").read()
    # No literal NN parameter pair should appear in this module's own source.
    assert "-11.5" not in src and "-36.4" not in src, (
        "a nearest-neighbour value is hard-coded here; it must come from the package")


def test_a_parent_can_only_pair_its_own_half_and_the_fusion_wins():
    """The modelling premise, asserted on the committed artifact.

    A junction gapmer is a perfect complement of the fusion and pairs only half of itself against
    either parent, so the fusion duplex must be the more stable one for every design. A negative
    ΔΔG would mean the model had been built backwards.
    """
    art = _artifact()
    assert art["n_designs"] > 0
    for r in art["per_design"]:
        assert r["n_donor_side"] + r["n_acceptor_side"] == len(r["antisense_5to3"])
        assert r["dg37_best_parent_duplex"] == min(r["dg37_donor_parent_duplex"],
                                                   r["dg37_acceptor_parent_duplex"])
        assert r["ddg37_discrimination"] > 0, (
            f"{r['antisense_5to3']} scores a parent duplex as more stable than the fusion")


def test_the_artifact_states_what_it_does_not_model():
    """LNA is not modelled and the artifact must say so, in the direction that matters.

    LNA raises affinity on fusion and parent duplexes alike, so it COMPRESSES ΔΔG — the reported
    discrimination is an upper bound. An artifact silent on this would read as an estimate.
    """
    art = _artifact()
    note = art.get("⚠_lna_not_modelled", "")
    assert "upper bound" in note.lower() and "LNA" in note
    assert any("not_a_cleavage_prediction" in k for k in art), sorted(art)


def test_the_manuscript_and_the_artifact_agree_on_every_reported_figure():
    """Rule 1: a number in the paper and its artifact may not diverge."""
    art = _artifact()
    paper_path = os.path.join(os.path.dirname(os.path.dirname(MOD)), "research", "manuscripts",
                              "aso", "fusion-junction-aso-short-communication.md")
    if not os.path.exists(paper_path):
        pytest.skip("manuscript is not present in this checkout")
    txt = open(paper_path, encoding="utf-8").read()
    # ⚠ COMPARED AT THE PRECISION THE MANUSCRIPT PRINTS, not at the artifact's. A paper quoting
    # "4.8 to 13.1 kcal/mol" is reporting 4.817 and 13.08 correctly; asserting the raw strings
    # would force spurious precision into the prose, which is the opposite of the discipline this
    # test exists to enforce. What must not drift is the VALUE, so the rounding is done here.
    d = art["discrimination_ddg37"]
    assert f"{d['min']:.1f}" in txt and f"{d['max']:.1f}" in txt, (
        f"the ΔΔG range in the paper is not the artifact's {d['min']:.1f}-{d['max']:.1f}")
    assert f"{d['median']:.1f}" in txt, "the median ΔΔG is not the artifact's"
    assert str(art["n_designs"]) in txt
    a = art["design_rule_audit"]
    assert f"{a['n_satisfying_all']} satisfy all four" in txt or \
           f"{a['n_satisfying_all']} satisfy" in txt, "the design-rule count is not the artifact's"
    means = art["mean_ddg37_by_gap_level_margin"]
    for v in means.values():
        assert f"{v:.1f}" in txt, (
            f"mean ΔΔG {v:.1f} is in the artifact and not in the manuscript")
