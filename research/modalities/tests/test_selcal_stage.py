#!/usr/bin/env python3
"""The sensitivity control's STAGING — chain identification, the ligand's provenance, the input audit.

★ WHY THE CHAIN TESTS ARE THE IMPORTANT ONES HERE. The NR-V04 panel silently computed every interface readout
against the WRONG chain pair — a positional rule picked Elongin C, a 112-residue E3 subunit, as the
degradation target, and nothing errored: the numbers were simply about something else. This panel's target is
a ~121-residue bromodomain, i.e. within a few residues of Elongin C, so a count-only rule would be one
construct revision away from repeating that exactly. These tests pin the property that prevents it: BOTH the
chain id and the residue count must agree with a contract written at co-fold time, and any disagreement RAISES.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import selcal_stage as ST  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONTRACT = {
    "A": {"role": "target", "gene": "SMARCA2", "n_residues": 3},
    "E": {"role": "VHL", "accession": "P40337", "n_residues": 2},
    "F": {"role": "ElonginB", "accession": "Q15370", "n_residues": 4},
}


def _pdb(chain_res, path):
    """A minimal PDB with the given {chain: n_residues}. One CA atom per residue is enough — the census
    counts residues, so this exercises the real parser rather than a stub."""
    lines, serial = [], 1
    for c, (ch, n) in enumerate(chain_res.items()):
        for i in range(1, n + 1):
            # chains are OFFSET in y as well as x: stacking them on one axis put two chains' first residues
            # at the same point, and the audit correctly called that a clash — a fixture bug that would have
            # looked like an over-strict threshold.
            lines.append("ATOM  %5d  CA  ALA %s%4d    %8.3f%8.3f%8.3f  1.00  0.00           C"
                         % (serial, ch, i, i * 4.0, c * 20.0, 0.0))
            serial += 1
    lines.append("END")
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


# =============================================================================================================
# chain identification — derived from the contract, verified against the file, fails closed
# =============================================================================================================
def test_identifies_the_target_from_the_contract(tmp_path):
    p = _pdb({"A": 3, "E": 2, "F": 4}, str(tmp_path / "ok.pdb"))
    got = ST.identify_chains(p, CONTRACT)
    assert got["target_chain"] == "A"
    assert got["e3_chains"] == ["E", "F"]
    assert got["target_gene"] == "SMARCA2"


def test_a_chain_of_the_wrong_length_RAISES_rather_than_being_accepted(tmp_path):
    """The whole identification argument rests on the length. A co-fold whose target chain is not the length
    the construct implies is not the system that was specified, and assembling it would produce readouts
    about something else — silently."""
    # 5 is not any contract length, so the multiset cannot match and no relabelling can rescue it.
    p = _pdb({"A": 5, "E": 2, "F": 4}, str(tmp_path / "wrong.pdb"))
    try:
        ST.identify_chains(p, CONTRACT)
    except ValueError as e:
        assert "uniquely re-mapped" in str(e)
    else:
        raise AssertionError("a wrong-length chain must RAISE, not be accepted")


def test_a_missing_or_extra_chain_RAISES(tmp_path):
    for census in ({"A": 3, "E": 2}, {"A": 3, "E": 2, "F": 4, "Z": 1}):
        p = _pdb(census, str(tmp_path / "bad.pdb"))
        try:
            ST.identify_chains(p, CONTRACT)
        except ValueError as e:
            assert "do not match the contract" in str(e)
        else:
            raise AssertionError("chain set %s must RAISE" % sorted(census))


def test_target_is_never_chosen_positionally(tmp_path):
    """The defect this replaces: 'the target is the LAST sorted protein chain'. Here the contract names it,
    so a target that happens to sort last, first or in the middle is identified identically."""
    contract = dict(CONTRACT)
    contract = {"A": dict(CONTRACT["E"]), "E": dict(CONTRACT["F"]), "Z": dict(CONTRACT["A"])}
    p = _pdb({"A": 2, "E": 4, "Z": 3}, str(tmp_path / "reordered.pdb"))
    got = ST.identify_chains(p, contract)
    assert got["target_chain"] == "Z"


# =============================================================================================================
# the ligand — a source, or an exception. Never a fallback.
# =============================================================================================================
def test_ligand_smiles_comes_from_the_committed_fetch_artifact():
    path = os.path.join(HERE, "selcal-reference-selectivity.json")
    if not os.path.exists(path):
        return
    lig = ST.ligand_smiles(path)
    assert lig["ccd"] == ST.LIGAND_CCD
    assert lig["smiles"] and "C" in lig["smiles"]
    assert lig["_source"].startswith("https://data.rcsb.org/")


def test_a_missing_reference_artifact_RAISES_rather_than_falling_back(tmp_path):
    """A co-fold built on a guessed structure is a fabricated experiment, and it would be invisible
    downstream: every subsequent step would run perfectly on the wrong molecule."""
    try:
        ST.ligand_smiles(str(tmp_path / "nope.json"))
    except RuntimeError as e:
        assert "never typed" in str(e)
    else:
        raise AssertionError("a missing reference artifact must RAISE")


def test_a_reference_artifact_without_the_ccd_RAISES(tmp_path):
    p = tmp_path / "ref.json"
    p.write_text(json.dumps({"ligands": {"XXX": {"smiles_canonical_by_program": {"x": "C"}}}}))
    try:
        ST.ligand_smiles(str(p))
    except RuntimeError as e:
        assert "from memory" in str(e)
    else:
        raise AssertionError("an artifact missing the CCD must RAISE")


# =============================================================================================================
# construct provenance
# =============================================================================================================
def test_both_constructs_quote_their_primary_source():
    for gene, c in ST.CONSTRUCTS.items():
        assert c["quote"].strip() and c["source"].strip()
        assert str(c["lo"]) in c["quote"] and str(c["hi"]) in c["quote"], \
            "%s: the span must appear in the quote it claims to come from" % gene
        assert c["hi"] > c["lo"]


def test_smarca2_uses_the_isoform_the_crystallographers_numbered_against():
    """P51531-2 is isoform 2. Fetching the canonical entry and slicing the same numbers would silently take a
    DIFFERENT span — the isoform shifts the indices."""
    assert ST.CONSTRUCTS["SMARCA2"]["accession"].endswith("-2")


# =============================================================================================================
# the input audit — the ONLY evidence licensed to exclude a co-fold model
# =============================================================================================================
def test_audit_passes_a_normal_assembly(tmp_path):
    p = _pdb({"A": 6, "E": 6}, str(tmp_path / "fine.pdb"))     # atoms 4 A apart
    a = ST.cofold_input_audit(p)
    assert a["ok"] and a["min_heavy_atom_sep_A"] > ST.MIN_HEAVY_ATOM_SEPARATION_A


def test_audit_refuses_the_measured_failure_signature(tmp_path):
    """The AMENDMENT 4 incident, reproduced: two heavy atoms in different residues at 0.181 A. The LJ term
    diverges from geometry like this and minimization cannot escape it."""
    p = str(tmp_path / "clash.pdb")
    with open(p, "w") as fh:
        fh.write("ATOM      1  O   GLU A  13      10.000  10.000  10.000  1.00  0.00           O\n")
        fh.write("ATOM      2  NZ  LYS A 181      10.181  10.000  10.000  1.00  0.00           N\n")
        fh.write("END\n")
    a = ST.cofold_input_audit(p)
    assert not a["ok"]
    assert abs(a["min_heavy_atom_sep_A"] - 0.181) < 1e-3
    assert "INPUT fault" in a["why"]


def test_audit_ignores_intra_residue_bonds(tmp_path):
    """A real bond is ~1.2-1.5 A. Counting atoms of the SAME residue would flag every protein ever built."""
    p = str(tmp_path / "bonded.pdb")
    with open(p, "w") as fh:
        fh.write("ATOM      1  C   ALA A   1       0.000   0.000   0.000  1.00  0.00           C\n")
        fh.write("ATOM      2  O   ALA A   1       1.230   0.000   0.000  1.00  0.00           O\n")
        fh.write("ATOM      3  CA  ALA A   2       6.000   0.000   0.000  1.00  0.00           C\n")
        fh.write("END\n")
    a = ST.cofold_input_audit(p)
    assert a["ok"], "the 1.23 A intra-residue C=O must not be read as a clash"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))


def test_a_pure_relabelling_is_remapped_by_the_bijection_not_refused(tmp_path):
    """A co-folder is free to rename chains — the ids in the YAML are a request, not a guarantee. Because
    the contract's residue counts are a BIJECTION (enforced when it is built), a relabelling has exactly one
    consistent mapping, so it is derived from the data rather than assumed (TESTING.md rule 1)."""
    p = _pdb({"B": 3, "C": 2, "D": 4}, str(tmp_path / "relabelled.pdb"))
    got = ST.identify_chains(p, CONTRACT)
    assert got["target_chain"] == "B"          # the 3-residue chain is the contract's target
    assert got["e3_chains"] == ["C", "D"]
    assert got["chain_relabelling"] == {"B": "A", "C": "E", "D": "F"}
    assert got["e3_roles"]["C"] == "VHL" and got["e3_roles"]["D"] == "ElonginB"


def test_an_ambiguous_relabelling_still_RAISES(tmp_path):
    """Two chains of the same length make the mapping non-unique. Guessing there is exactly the silent
    mis-mapping that scored Elongin C as a degradation target on a sibling panel."""
    ambiguous = {"A": {"role": "target", "gene": "X", "n_residues": 3},
                 "E": {"role": "VHL", "n_residues": 3}}
    p = _pdb({"B": 3, "C": 3}, str(tmp_path / "ambig.pdb"))
    try:
        ST.identify_chains(p, ambiguous)
    except ValueError as e:
        assert "uniquely re-mapped" in str(e)
    else:
        raise AssertionError("an ambiguous relabelling must RAISE")
