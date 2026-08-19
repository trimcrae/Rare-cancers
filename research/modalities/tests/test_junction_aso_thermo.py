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


#: ⛔ AN ABSENT READING IS NOT A READING OF ABSENCE (2026-08-19, lane C2 audit). `_nn_table()`
#: returns `(None, None)` from a bare `except Exception` around `from Bio.SeqUtils import
#: MeltingTemp`, so ANY failure to reach the table — Biopython absent, but equally a Biopython
#: release that moves or removes `MeltingTemp.R_DNA_NN1`, which is a live possibility for a
#: long-deprecated module — used to report as "Biopython is not installed". CI DOES install
#: biopython, so in the one environment that gates commits that message can only ever be false, and
#: the whole nearest-neighbour provenance guard would fall silent on an upgrade while reporting
#: green. The two states are now separated by asking the interpreter whether the package is there.
def _biopython_is_installed():
    import importlib.util  # noqa: PLC0415
    try:
        return importlib.util.find_spec("Bio") is not None
    except (ImportError, ValueError):  # pragma: no cover - a broken install is still "present"
        return True


def _refuse_or_skip(what):
    if _biopython_is_installed():
        pytest.fail(
            f"Biopython IS installed and {what} could not be read from it. That is a package "
            "change, not a missing dependency — `.github/workflows/tests.yml` installs biopython "
            "precisely so this guard runs — and every energy in the thermo artifact rests on the "
            "table this could not reach. Re-point junction_aso_thermo._nn_table at the table's "
            "new home; do not let it report as an absent package.")
    # SKIP IS DELIBERATE: the package is genuinely absent HERE and present on the runner, and the
    # branch above proves the two states are distinguished rather than conflated.
    pytest.skip("Biopython is not installed in this environment (CI installs it, so this "
                "guard does run where it gates a commit)")


def _table():
    tbl, _ = T._nn_table()
    if tbl is None:
        _refuse_or_skip("the DNA:RNA nearest-neighbour table")
    return tbl


def _artifact():
    #: ⛔ NOT A SKIP (2026-08-19, lane C2 audit): it IS committed, so an absence is a broken tree.
    if not os.path.exists(ART):
        pytest.fail(f"the thermo artifact is missing at {ART}; it is committed, and every ΔΔG°37 "
                    "the paper and Table 4 print is unchecked without it.")
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
        _refuse_or_skip("the table's provenance record")
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

    ⚠ *Superseded, retained: "LNA raises affinity on fusion and parent duplexes alike, so it
    COMPRESSES ΔΔG — the reported discrimination is an upper bound."* That is the direction the
    module, the artifact and the manuscript all carried until 2026-08-13 and all corrected: the seam
    lies inside the gap, so the fusion duplex pairs all ten LNA residues and each parent duplex
    exactly five, and ΔΔG WIDENS. The reported value is a conservative FLOOR.

    ⛔ THE ASSERTION USED TO PASS FOR THE WRONG REASON, WHICH IS WHY THE DOCSTRING MATTERED. It
    checked only for "upper bound", and after the correction that phrase survived solely inside the
    artifact's own `⚠ Superseded, retained` clause — so a test written to pin the compression claim
    went on passing against text that says the opposite. It now pins the LIVE direction and the
    retention of the superseded one separately, which is what rule 1.2 actually asks for.
    """
    art = _artifact()
    note = art.get("⚠_lna_not_modelled", "")
    assert "LNA" in note
    assert "floor" in note.lower(), "the live text no longer states the floor direction"
    assert "superseded" in note.lower() and "upper bound" in note.lower(), (
        "the superseded 'upper bound' direction was dropped instead of retained")
    assert any("not_a_cleavage_prediction" in k for k in art), sorted(art)


def test_the_median_is_a_median():
    """⛔ THE FIELD WAS `ddg_s[len(ddg_s) // 2]` OVER AN EVEN-SIZED SET (190), which returns the
    UPPER of the two central values (9.603) rather than their mean (9.5925).

    ⚠ THE PROSE WAS RIGHT AND THE ARTIFACT WAS WRONG, WHICH IS WHY NOTHING CAUGHT IT. Both values
    round to the "median of 9.6" the manuscript prints, so every consistency check that compared the
    paper to the artifact at the paper's precision passed. A mislabelled field is still quotable at
    full precision by anything that reads the artifact instead of the paper, and this asserts the
    label against an independent implementation rather than against a rounded string.
    """
    import statistics
    art = _artifact()
    ddg = [r["ddg37_discrimination"] for r in art["per_design"]]
    assert len(ddg) % 2 == 0, "the set is odd-sized; this test's premise no longer holds"
    assert art["discrimination_ddg37"]["median"] == round(statistics.median(ddg), 4)
    assert art["discrimination_ddg37"]["min"] == min(ddg)
    assert art["discrimination_ddg37"]["max"] == max(ddg)
    # The superseded value must stay registered, per rule 1.2, and must not be the live one.
    sup = art["discrimination_ddg37"].get("⚠_superseded_median", "")
    assert "9.603" in sup, "the superseded median was dropped instead of registered"
    assert art["discrimination_ddg37"]["median"] != 9.603


def test_the_convention_check_does_not_claim_a_power_it_does_not_have():
    """⛔ THE ARTIFACT SAID A REVERSED STRAND CONVENTION 'IS RULED OUT'. IT IS NOT.

    `duplex_enthalpy_entropy` and Biopython's `Tm_NN` build the nearest-neighbour key the same way
    from whatever sequence they are handed, so they agree on either strand. The strand is fixed
    instead by Biopython's documented convention for `R_DNA_NN1` — the sequence supplied must be the
    RNA one — and the module supplies `target_mRNA_5to3`, which is that sequence.
    """
    art = _artifact()
    v = art["convention_validation"]
    proves = v["_what_this_proves"]
    assert "ruled out" not in proves and "reversed strand" not in proves.lower(), proves
    assert "summation" in proves.lower() and "keying" in proves.lower(), proves
    assert str(v["n_sequences"]) in proves, (
        "the claim must name the number of sequences it was measured over")
    assert "⛔_what_this_does_NOT_prove" in v
    assert "⚠_superseded_what_this_proves" in v, "the superseded claim must stay registered"


def test_the_convention_check_has_no_power_over_the_strand_and_this_is_the_measurement():
    """The discriminating observation, run rather than asserted.

    Both implementations agree to 0.0000 °C on the target strand AND on the antisense strand, while
    the two strands give ΔG°37 that differ by ~1.6 kcal/mol. A check that passes equally under the
    right and the wrong strand cannot be evidence about the strand.
    """
    tbl = _table()
    from Bio.SeqUtils import MeltingTemp as mt
    target, anti = "GTCCACGGATATGCCC", "GGGCATATCCGTGGAC"
    energies = {}
    for seq in (target, anti):
        dh, ds = T.duplex_enthalpy_entropy(seq, tbl)
        mine = T._tm(dh, ds)
        theirs = mt.Tm_NN(seq, nn_table=mt.R_DNA_NN1, Na=0, Mg=0, saltcorr=0,
                          dnac1=T.CONC_NM / 2, dnac2=T.CONC_NM / 2)
        assert abs(mine - theirs) < 1e-9, (
            f"the two implementations disagree on {seq}; the premise of this test is gone")
        energies[seq] = T.delta_g37(dh, ds)
    assert abs(energies[target] - energies[anti]) > 1.0, (
        "the two strands give the same free energy, so there would be nothing for the check to "
        "miss — the module docstring's measurement no longer reproduces")
    # And the strand the module actually computes on is the one the committed artifact holds.
    art = _artifact()
    row = next((r for r in art["per_design"] if r["antisense_5to3"] == anti), None)
    if row is not None:
        assert row["dg37_fusion_duplex"] == energies[target], (
            "the artifact's fusion duplex no longer reproduces from the target strand")


def test_the_validation_runs_over_the_whole_design_set_it_claims():
    """⛔ IT RAN ON A `[:60]` SLICE OF 190 WHILE THE FIELD BESIDE IT SAID 'the real design set'.

    Nothing selected those 60, nothing quotes the number, and the check is arithmetic over 16-mers
    that costs nothing — so the honest scope and the cheap scope were the same one.
    """
    art = _artifact()
    assert art["convention_validation"]["n_sequences"] == art["n_designs"], (
        art["convention_validation"]["n_sequences"], art["n_designs"])
    assert art["convention_validation"]["agrees"] is True


def test_the_manuscript_and_the_artifact_agree_on_every_reported_figure():
    """Rule 1: a number in the paper and its artifact may not diverge."""
    art = _artifact()
    paper_path = os.path.join(os.path.dirname(os.path.dirname(MOD)), "research", "manuscripts",
                              "aso", "fusion-junction-aso-research-article.md")
    if not os.path.exists(paper_path):
        pytest.fail(f"the manuscript is missing at {paper_path}; it is committed, and rule 1 — a "
                    "number in the paper may not diverge from its artifact — is unchecked here "
                    "without it.")
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
