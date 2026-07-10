"""Unit tests for the PURE logic of selectivity_benchmark_prep (SGC-CBP30 CREBBP-vs-BRD4(1) staging).

No rdkit / boto3 / network — apo_protein, hetatm_residues, select_ligand_residue, ligand_heavy_atoms and
single_altloc_pdb_block are all dependency-free string/coordinate parsing. The rdkit pose-lift
(build_docked_sdf) and the S3 upload run only inside the staging GitHub Action.
"""
import selectivity_benchmark_prep as sb


# A miniature holo bromodomain-like PDB: two protein chains (A, B), a big ligand (LIG) in BOTH chains,
# plus water, a sulfate and a chloride ion that must NOT be mistaken for the ligand.
_HOLO = """\
ATOM      1  N   MET A   1       0.000   0.000   0.000  1.00  0.00           N
ATOM      2  CA  MET A   1       1.000   0.000   0.000  1.00  0.00           C
ATOM      3  CB  MET A   1       1.500   1.000   0.000  1.00  0.00           C
ATOM      4  N   LYS A   2       2.000   0.000   0.000  1.00  0.00           N
ATOM      5  CA  LYS A   2       3.000   0.000   0.000  1.00  0.00           C
ATOM      6  CA ASER A   3       4.000   0.000   0.000  1.00  0.00           C
ATOM      7  CA BSER A   3       4.100   0.000   0.000  1.00  0.00           C
ATOM      8  CA  LEU B   1       9.000   0.000   0.000  1.00  0.00           C
HETATM    9  C1  LIG A 200      10.000  10.000  10.000  1.00  0.00           C
HETATM   10  C2  LIG A 200      11.000  10.000  10.000  1.00  0.00           C
HETATM   11  N1  LIG A 200      12.000  10.000  10.000  1.00  0.00           N
HETATM   12  O1  LIG A 200      13.000  10.000  10.000  1.00  0.00           O
HETATM   13  C3 ALIG A 200      14.000  10.000  10.000  1.00  0.00           C
HETATM   14  C3 BLIG A 200      14.200  10.000  10.000  0.50  0.00           C
HETATM   15  C1  LIG B 200      90.000  90.000  90.000  1.00  0.00           C
HETATM   16  C2  LIG B 200      91.000  90.000  90.000  1.00  0.00           C
HETATM   17  S   SO4 A 300      50.000  50.000  50.000  1.00  0.00           S
HETATM   18  O1  SO4 A 300      51.000  50.000  50.000  1.00  0.00           O
HETATM   19 CL   CL  A 301      60.000  60.000  60.000  1.00  0.00          CL
HETATM   20  O   HOH A 400      70.000  70.000  70.000  1.00  0.00           O
END
"""


# -------------------------------------------------------------------- apo_protein

def test_apo_keeps_first_chain_strips_het_and_altloc():
    apo, chain, n = sb.apo_protein(_HOLO)
    lines = [l for l in apo.splitlines() if l.startswith("ATOM")]
    assert chain == "A"
    # 6 chain-A atoms of standard residues, minus the dropped 'B' altloc SER => 6 kept
    assert n == 6 and len(lines) == 6
    assert all(l[21] == "A" for l in lines)          # chain B (LEU) dropped
    assert "LIG" not in apo and "SO4" not in apo and "HOH" not in apo
    assert " B SER" not in apo.replace("BSER", " B SER")  # 'B' altloc resolved
    assert apo.rstrip().endswith("END")


def test_first_protein_chain():
    assert sb.first_protein_chain(_HOLO) == "A"


# -------------------------------------------------------------------- ligand selection

def test_hetatm_residues_excludes_solvent_and_ions():
    groups = sb.hetatm_residues(_HOLO)
    resnames = {k[0] for k in groups}
    assert resnames == {"LIG"}                        # SO4, CL, HOH all excluded
    # both copies (chain A and chain B) present as separate residues
    assert ("LIG", "A", "200", "") in groups
    assert ("LIG", "B", "200", "") in groups


def test_select_ligand_prefers_apo_chain():
    # the apo protein is chain A, so the ligand copy in chain A must be chosen (pose sits in that pocket)
    reskey, lines = sb.select_ligand_residue(_HOLO, prefer_chain="A")
    assert reskey == ("LIG", "A", "200", "")
    assert len(lines) == 6                            # 4 unique + 2 altlocs of C3


def test_select_ligand_beats_buffer_by_size():
    # even without a chain hint, the multi-atom LIG beats any 1-2 atom buffer group
    reskey, _ = sb.select_ligand_residue(_HOLO)
    assert reskey[0] == "LIG"


def test_select_ligand_by_explicit_code():
    reskey, _ = sb.select_ligand_residue(_HOLO, het_code="lig", prefer_chain="A")
    assert reskey == ("LIG", "A", "200", "")


def test_select_ligand_missing_code_raises():
    try:
        sb.select_ligand_residue(_HOLO, het_code="ZZZ")
    except ValueError:
        return
    raise AssertionError("expected ValueError for absent HET code")


# -------------------------------------------------------------------- heavy-atom pose lift input

def test_ligand_heavy_atoms_resolves_altloc_and_preserves_coords():
    _reskey, lines = sb.select_ligand_residue(_HOLO, prefer_chain="A")
    heavy = sb.ligand_heavy_atoms(lines)
    names = [n for n, _e, _xyz in heavy]
    # C3 has A/B altlocs -> exactly one kept (the 'A' copy, first seen)
    assert names == ["C1", "C2", "N1", "O1", "C3"]
    elems = [e for _n, e, _xyz in heavy]
    assert elems == ["C", "C", "N", "O", "C"]
    # coordinates lifted verbatim from the crystal records (this is what goes onto the RDKit template)
    coord = {n: xyz for n, _e, xyz in heavy}
    assert coord["C1"] == (10.0, 10.0, 10.0)
    assert coord["O1"] == (13.0, 10.0, 10.0)
    assert coord["C3"] == (14.0, 10.0, 10.0)          # 'A' altloc, not the 14.2 'B' altloc


def test_single_altloc_pdb_block_dedupes_and_blanks_altloc():
    _reskey, lines = sb.select_ligand_residue(_HOLO, prefer_chain="A")
    block = sb.single_altloc_pdb_block(lines)
    body = [l for l in block.splitlines() if l.startswith("HETATM")]
    assert len(body) == 5                              # one C3 alt-loc only
    assert all(l[16] == " " for l in body)            # alt-loc column blanked
    assert block.rstrip().endswith("END")


# -------------------------------------------------------------------- entry parsing

def test_parse_entries():
    assert sb._parse_entries("crebbp:4NR7, brd4bd1:5BT4") == [("crebbp", "4NR7"), ("brd4bd1", "5BT4")]


def test_parse_entries_bad():
    for bad in ("crebbp", "crebbp:", ":4NR7"):
        try:
            sb._parse_entries(bad)
        except ValueError:
            continue
        raise AssertionError(f"expected ValueError for {bad!r}")
