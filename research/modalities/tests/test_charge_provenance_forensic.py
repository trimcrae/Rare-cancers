"""The charge-provenance forensic reads two file formats and answers one question from them. These tests
pin the READING, because the whole value of the forensic is that its answer is a measurement rather than a
story — and a parser that silently returns "no charges found" would manufacture exactly the reassuring
answer nobody should trust.

No network, no toolkit, no GPU: every fixture is written here and read back.
"""
import bz2
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import charge_provenance_forensic as cpf  # noqa: E402


# ------------------------------------------------------------------ the pose file: what did it carry IN?
SDF = """ligA
     RDKit          3D

  3  2  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0
    1.0000    0.0000    0.0000 O   0  0
    2.0000    0.0000    0.0000 H   0  0
  1  2  1  0
  2  3  1  0
M  END
>  <atom.dprop.PartialCharge>  (1)
0.6501648 0.1426589 -0.0927976

$$$$
ligB
     RDKit          3D

  2  1  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0
    1.0000    0.0000    0.0000 O   0  0
  1  2  1  0
M  END
$$$$
"""


def test_a_charged_record_and_a_clean_record_are_told_apart(tmp_path):
    p = tmp_path / "ligands.sdf"
    p.write_text(SDF)
    recs = cpf.sdf_records(str(p))
    assert [r["name"] for r in recs] == ["ligA", "ligB"]
    # The charged record: the values are read verbatim, in file order, with the atom count beside them so a
    # count mismatch (the gufe failure mode) is visible without a toolkit.
    assert recs[0]["n_atoms"] == 3
    assert recs[0]["charges"] == [0.6501648, 0.1426589, -0.0927976]
    # The clean record: `None`, NOT an empty list. "This file carries no charge model" and "this file carries
    # a zero-length charge model" are different findings and must not render alike.
    assert recs[1]["charges"] is None
    assert recs[1]["n_charges"] is None


def test_the_tag_name_is_the_guard_s_name_not_a_second_copy():
    """ONE FACT, ONE PLACE. If `nr4a3_rbfe` ever renames the property it strips, this forensic must follow it
    automatically — a forensic looking for a tag the engine no longer writes reports a clean file forever."""
    assert "atom.dprop.PartialCharge" in cpf.FOREIGN_CHARGE_PROPS


# ------------------------------------------------------------------ the System: what did it PARAMETERIZE?
def _system_xml(base_qs, offsets):
    parts = "".join('<Particle eps="0.1" q="%r" sig="0.3"/>' % q for q in base_qs)
    offs = "".join('<Offset eps="0" parameter="%s" particle="%d" q="%r" sig="0"/>' % (nm, i, q)
                   for nm, lst in offsets.items() for i, q in lst)
    return ('<?xml version="1.0" ?><System openmmVersion="8.1" type="System" version="1">'
            '<Particles>%s</Particles><Forces>'
            '<Force type="HarmonicBondForce"><Bonds/></Force>'
            '<Force alpha="0" type="NonbondedForce"><Particles>%s</Particles>'
            '<ParticleOffsets>%s</ParticleOffsets></Force></Forces></System>'
            % ("".join('<Particle mass="12"/>' for _ in base_qs), parts, offs))


def _write_bz2(tmp_path, text, name="hybrid_system.xml.bz2"):
    p = tmp_path / name
    with bz2.open(str(p), "wb") as fh:
        fh.write(text.encode())
    return str(p)


def test_both_charge_columns_are_read_because_reading_one_is_a_false_negative(tmp_path):
    """In a perses/OpenFE hybrid the alchemical ligand's electrostatics live in the PARTICLE PARAMETER
    OFFSETS, not in the base `q` column. A reader that saw only the base column would report an uncharged
    ligand on a fully charged system — the reassuring wrong answer this forensic exists to avoid."""
    lig = [0.6501648, 0.1426589, -0.0927976]
    xml = _system_xml([-0.834, 0.417, 0.0, 0.0, 0.0],
                      {"lambda_electrostatics_delete": list(enumerate(lig, start=2))})
    base, offs = cpf.system_charges(_write_bz2(tmp_path, xml))
    assert base == [-0.834, 0.417, 0.0, 0.0, 0.0]
    assert offs["lambda_electrostatics_delete"] == lig
    # ...and the probe finds the pose vector in the offset column, which the base column does not contain.
    res = cpf.probe(base, offs, lig)
    assert res["matched"] is True
    assert res["columns"]["offset:lambda_electrostatics_delete"]["EXACT_RUN"] is True
    assert res["columns"]["base"]["EXACT_RUN"] is False


def test_a_negated_offset_column_still_identifies_the_charge_set(tmp_path):
    """An offset carries the DIFFERENCE between the two λ endpoints, so a set of charges being switched OFF
    appears as its own negative. Testing only the positive sense would miss it."""
    lig = [0.6501648, 0.1426589, -0.0927976]
    xml = _system_xml([0.0, 0.0, 0.0],
                      {"lambda_electrostatics_core": [(i, -q) for i, q in enumerate(lig)]})
    base, offs = cpf.system_charges(_write_bz2(tmp_path, xml))
    res = cpf.probe(base, offs, lig)
    assert res["matched"] is True
    assert res["columns"]["offset:lambda_electrostatics_core"]["sign"] == "-"


def test_a_different_charge_model_does_not_match_and_says_by_how_much(tmp_path):
    """The negative control. Two charge MODELS differ in the second decimal; the tolerance is serialization
    precision (1e-6), so a near-miss must be reported as a miss with its distance, not rounded into a hit."""
    lig = [0.6501648, 0.1426589, -0.0927976]
    other = [0.61, 0.15, -0.10]
    xml = _system_xml([0.0, 0.0, 0.0], {"lambda_electrostatics_delete": list(enumerate(other))})
    base, offs = cpf.system_charges(_write_bz2(tmp_path, xml))
    res = cpf.probe(base, offs, lig)
    assert res["matched"] is False
    col = res["columns"]["offset:lambda_electrostatics_delete"]
    assert col["max_abs_diff"] > 1e-3


def test_best_window_finds_a_ligand_run_inside_a_solvent_background(tmp_path):
    """The ligand is a contiguous index run inside ~10^5 water charges. Contiguity is the strong form of the
    test: a scatter of coincidental matches is not evidence, a RUN is."""
    lig = [0.6501648, 0.1426589, -0.0927976, 0.31415926, -0.2718281]
    hay = [-0.834, 0.417, 0.417] * 200 + lig + [-0.834, 0.417, 0.417] * 200
    start, mx, nex = cpf.best_window(hay, lig)
    assert start == 600
    assert mx == 0.0
    assert nex == len(lig)


def test_a_system_shorter_than_the_probe_is_reported_not_crashed():
    start, mx, nex = cpf.best_window([0.1, 0.2], [0.1, 0.2, 0.3])
    assert start == -1 and nex == 0


# ------------------------------------------------------------------ the verdict the whole file is FOR
def test_two_arms_carrying_one_charge_set_are_distinguished_from_two_arms_that_do_not(tmp_path):
    """ΔΔG_coop = ΔΔG_ternary − ΔΔG_binary cancels the charge model ONLY IF both arms used the same one. This
    is the comparison that decides it, and it needs no reference model: identical offset columns on the same
    ligand pair means the model cancels whatever it was."""
    lig = [0.6501648, 0.1426589, -0.0927976]
    same = cpf._compare_offsets({"lambda_electrostatics_delete": lig},
                                {"lambda_electrostatics_delete": list(lig)})
    assert same["ARMS_SHARE_ONE_CHARGE_SET"] is True
    diff = cpf._compare_offsets({"lambda_electrostatics_delete": lig},
                                {"lambda_electrostatics_delete": [0.61, 0.15, -0.10]})
    assert diff["ARMS_SHARE_ONE_CHARGE_SET"] is False
    assert diff["columns"]["lambda_electrostatics_delete"]["max_abs_diff"] > 1e-3


def test_a_leg_with_no_stored_system_is_UNMEASURED_and_never_silently_clean():
    """'I could not read it' and 'I read it and it was fine' must never render alike — an absent artifact is a
    valid finding and the one thing this forensic must not paper over."""
    assert cpf.UNMEASURED_STATUSES  # the vocabulary exists
    for s in cpf.UNMEASURED_STATUSES:
        assert s != "READ"
