"""Offline tests for the pure PDB-parsing logic of the DeepTernary Step-3 blind-prep.

The network + RDKit paths (fetch/build_degrader/prep_control) run only in the DeepTernary CI env; here we
test chain + ligand extraction, which is what enforces the blind-input contract (right protein chains, right
warhead/anchor ligand). No network.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import deepternary_blind_prep as bp  # noqa: E402

# minimal PDB: chain A protein (2 atoms), chain B protein (1 atom), a warhead HETATM (comp JQ1, chain A),
# and a buffer HETATM (EDO) that must NOT be picked as the warhead.
PDB = """\
ATOM      1  N   ALA A   1      11.104  13.207  10.000  1.00  0.00           N
ATOM      2  CA  ALA A   1      12.104  13.207  10.000  1.00  0.00           C
ATOM      3  N   GLY B   1      20.000  20.000  20.000  1.00  0.00           N
HETATM    4  C1  JQ1 A 201      15.000  15.000  15.000  1.00  0.00           C
HETATM    5  C2  JQ1 A 201      15.500  15.500  15.500  1.00  0.00           C
HETATM    6  O1  EDO A 301      30.000  30.000  30.000  1.00  0.00           O
END
"""


def _pdb():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "x.pdb")
    with open(p, "w") as f:
        f.write(PDB)
    return d, p


def test_extract_protein_chain_selects_only_requested_chain():
    d, p = _pdb()
    out = os.path.join(d, "p1.pdb")
    n = bp.extract_protein_chains(p, ["A"], out)
    assert n == 2, n
    txt = open(out).read()
    assert " A   1 " in txt and "GLY B" not in txt


def test_extract_ligand_picks_warhead_not_buffer():
    d, p = _pdb()
    out = os.path.join(d, "lig1.pdb")
    n = bp.extract_ligand(p, "JQ1", out)
    assert n == 2, n
    txt = open(out).read()
    assert "JQ1" in txt and "EDO" not in txt


def test_extract_ligand_chain_restriction():
    d, p = _pdb()
    out = os.path.join(d, "ligB.pdb")
    # no JQ1 on chain B -> zero atoms
    assert bp.extract_ligand(p, "JQ1", out, chain="B") == 0


def test_required_input_contract_names():
    # the 6 files a blind control must produce, and the sealed native never in the predict dir
    assert set(bp.REQUIRED_INPUTS) == {
        "unbound_protein1.pdb", "unbound_lig1.pdb", "unbound_protein2.pdb",
        "unbound_lig2.pdb", "ligand.pdb", "ligand.sdf"}
    assert bp.SEALED_FILE == "gt_complex.pdb"
