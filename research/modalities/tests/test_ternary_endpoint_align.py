"""Reviewer condition 1 (2026-07-19) — the endpoint core-transplant + verification (pure RDKit, no GPU/OpenFE).

Builds a synthetic calibration-like edge (a pyridine-linker molecule A -> the same molecule with the ring N
changed to C-H, i.e. benzene: the exact cmpd1->cmpd4 chemistry), relaxes A to a 3D conformer, transplants its
mapped core onto B, and asserts every property the reviewer required:
  - mapped-atom displacement ~0 (no "mapped atom moved" warnings),
  - connectivity/bond-orders/formal-charges/stereo tags preserved on B,
  - 3D chirality not inverted,
  - net formal charge conserved A vs B,
  - sane dummy geometry + no clashes,
and that a deliberately-broken transplant (a mapped atom nudged away, a clash) is REJECTED (ok=False)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_endpoint_align as align  # noqa: E402

from rdkit import Chem              # noqa: E402
from rdkit.Chem import AllChem      # noqa: E402


def _embed(smiles, seed=1):
    m = Chem.AddHs(Chem.MolFromSmiles(smiles))
    AllChem.EmbedMolecule(m, randomSeed=seed)
    AllChem.MMFFOptimizeMolecule(m)
    return m


# a small molecule with a pyridine ring + a stereocenter, and its N->CH (benzene) analogue
SMI_A = "Cc1ccncc1[C@H](C)C(=O)O"   # methyl-pyridine with a chiral center
SMI_B = "Cc1cc ccc1[C@H](C)C(=O)O".replace(" ", "")  # ring N -> CH (benzene); same chiral center


def test_transplant_zero_mapped_displacement_and_preserved_properties():
    molA = _embed(SMI_A)
    molB = _embed(SMI_B, seed=7)          # deliberately a DIFFERENT starting pose
    a2b = align.mcs_mapping(molA, molB)
    assert len(a2b) >= 8, ("MCS map too small", len(a2b))
    molB_out, checks = align.transplant_and_verify(molA, molB, a2b)
    assert checks["ok"], checks
    assert checks["mapped_max_displacement_ang"] <= align.MAPPED_DISP_TOL_ANG, checks
    assert checks["graph_identical"] is True
    assert checks["chirality_not_inverted"] is True
    assert checks["net_charge_conserved"] is True
    assert checks["no_clash"] is True
    assert checks["dummy_bond_lengths_ok"] is True
    # every mapped B atom really sits on its A partner
    confA, confB = molA.GetConformer(), molB_out.GetConformer()
    for iA, iB in a2b.items():
        pa, pb = confA.GetAtomPosition(iA), confB.GetAtomPosition(iB)
        assert ((pa.x - pb.x) ** 2 + (pa.y - pb.y) ** 2 + (pa.z - pb.z) ** 2) ** 0.5 <= 1e-3


def test_transplant_graph_unchanged_smiles():
    molA = _embed(SMI_A)
    molB = _embed(SMI_B)
    a2b = align.mcs_mapping(molA, molB)
    molB_out, checks = align.transplant_and_verify(molA, molB, a2b)
    # moving coordinates must not alter B's chemical graph
    assert Chem.MolToSmiles(molB) == Chem.MolToSmiles(molB_out)


def test_verify_rejects_displaced_mapped_atom():
    molA = _embed(SMI_A)
    molB = _embed(SMI_B)
    a2b = align.mcs_mapping(molA, molB)
    molB_out = align.core_transplant(molA, molB, a2b)
    # nudge one mapped atom far away -> verification must FAIL on displacement
    iB = next(iter(a2b.values()))
    conf = molB_out.GetConformer()
    p = conf.GetAtomPosition(iB)
    conf.SetAtomPosition(iB, (p.x + 3.0, p.y, p.z))
    checks = align.verify_endpoints(molA, molB, molB_out, a2b)
    assert checks["ok"] is False
    assert checks["mapped_displacement_ok"] is False


def test_verify_rejects_clash():
    molA = _embed(SMI_A)
    molB = _embed(SMI_B)
    a2b = align.mcs_mapping(molA, molB)
    molB_out = align.core_transplant(molA, molB, a2b)
    # collapse two atoms on top of each other -> clash guard must FAIL
    conf = molB_out.GetConformer()
    p0 = conf.GetAtomPosition(0)
    conf.SetAtomPosition(1, (p0.x, p0.y, p0.z))
    checks = align.verify_endpoints(molA, molB, molB_out, a2b)
    assert checks["no_clash"] is False
    assert checks["ok"] is False


def test_net_charge_mismatch_flagged():
    # A neutral, B carrying a net +1 -> a real morph would conserve charge; the check must catch a mismatch.
    molA = _embed("Cc1ccncc1")            # neutral
    molB = _embed("Cc1cc[nH+]cc1")        # protonated pyridinium (+1)
    a2b = align.mcs_mapping(molA, molB)
    molB_out = align.core_transplant(molA, molB, a2b)
    checks = align.verify_endpoints(molA, molB, molB_out, a2b)
    assert checks["net_charge_conserved"] is False
    assert checks["ok"] is False
