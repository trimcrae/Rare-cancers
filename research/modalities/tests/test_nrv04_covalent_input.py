#!/usr/bin/env python3
"""Offline tests for the NR-V04 covalent-INPUT layer (A1 admissibility, adduct construction, site probe).

These pin the three things the 2026-07-25 Lane-8 audit found and fixed, so none of them can silently return:

  1. **A1 must be scored at the FROZEN site, not at whichever cysteine happens to be nearest.** The prereg
     amendment recorded A1 failing at 8.99 A; that distance is to NR4A1 **C566**. The frozen covalent site is
     **C551** (Zhang et al., Chem. Commun. 2018, doi:10.1039/C8CC06140H), which is 28.4-39.1 A away in every
     clean co-fold. A test pins the LBD-index <-> full-length mapping that connects the two numbers, because an
     off-by-one there is exactly what makes the wrong cysteine look like the right one.
  2. **The warhead moiety must be identified structurally, not by substructure match.** Free celastrol is NOT a
     substructure of NR-V04 (its C-28 acid is consumed into the linker amide), so a naive
     `GetSubstructMatch(celastrol)` returns nothing and every warhead-placement readout silently becomes a
     whole-ligand readout.
  3. **The constructed adduct geometry must be a real C-S bond geometry**, at the bond length and the thioether
     angle -- not merely "closer than the A1 limit".
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nrv04_covalent_assemble import NR4A_LBD_RESIDUES  # noqa: E402
from nrv04_covalent_panel import TARGET_COV_RESNUM  # noqa: E402

# rdkit/scipy are CI dependencies, not sandbox ones — the pure-arithmetic and source-contract tests below must
# still run without them, so the skips are per-test rather than module-wide.
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _audit():
    pytest.importorskip("rdkit")
    import nrv04_covalent_input_audit as audit
    return audit


def _np():
    return pytest.importorskip("numpy")


# --- 1. the mapping that decides WHICH cysteine A1 is about ------------------------------------------------

def test_c551_maps_to_lbd_residue_207_for_the_frozen_construct():
    """NR4A1 P22736 is 598 aa; the frozen LBD construct is its C-terminal 254 residues, so the offset is 344
    and full-length C551 is construct residue 207. This is the arithmetic that separates C551 (28-39 A away in
    every co-fold) from C566 (8.87-8.99 A), i.e. the frozen site from the one A1 was actually measuring."""
    offset = 598 - NR4A_LBD_RESIDUES
    assert offset == 344
    assert TARGET_COV_RESNUM - offset == 207
    # and the inverse direction, which is what the audit reports per cysteine
    assert 222 + offset == 566, "LBD residue 222 is C566 — the cysteine the 8.99 A figure belongs to"


def test_audit_distinguishes_pass_at_frozen_site_from_pass_at_any_cysteine():
    """The A1 verdict vocabulary must keep 'admissible' and 'close to some other cysteine' apart. A single
    boolean here is how a leg would get built onto the wrong residue and still be called admissible."""
    src = open(os.path.join(HERE, "nrv04_covalent_input_audit.py")).read()
    assert "PASS_WRONG_CYS" in src
    assert "frozen_site_passes" in src and "nearest_passes" in src


# --- 2. warhead identification ------------------------------------------------------------------------------

def test_free_celastrol_is_not_a_substructure_of_nrv04():
    """Pins the reason the structural definition exists: the naive match returns nothing."""
    pytest.importorskip("rdkit")
    from rdkit import Chem
    from nrv04_ligands import LIGANDS
    nrv04 = Chem.MolFromSmiles(LIGANDS["nrv04"])
    cel = Chem.MolFromSmiles(LIGANDS["celastrol"])
    assert nrv04 is not None and cel is not None
    assert not nrv04.GetSubstructMatch(cel), (
        "if this ever passes, celastrol's C-28 acid is no longer being consumed into the linker amide and the "
        "structural warhead definition should be revisited")


def test_warhead_fragment_is_the_celastroyl_end_of_nrv04():
    pytest.importorskip("rdkit")
    from rdkit import Chem
    from nrv04_ligands import LIGANDS, electrophile_atom_index
    m = Chem.MolFromSmiles(LIGANDS["nrv04"])
    c6, _ = electrophile_atom_index(m)
    frag = _audit().warhead_fragment_indices(m, c6)
    assert c6 in frag
    # celastrol is C29H38O4 -> 33 heavy atoms; the celastroyl fragment (acid O lost to the amide N) is 32.
    assert 28 <= len(frag) <= 34, f"warhead fragment has {len(frag)} heavy atoms, expected the celastroyl core"
    assert len(frag) < m.GetNumAtoms(), "the warhead fragment must be a strict subset of the conjugate"


def test_free_celastrol_warhead_fragment_is_the_whole_molecule():
    pytest.importorskip("rdkit")
    from rdkit import Chem
    from nrv04_ligands import LIGANDS, electrophile_atom_index
    m = Chem.MolFromSmiles(LIGANDS["celastrol"])
    c6, _ = electrophile_atom_index(m)
    assert len(_audit().warhead_fragment_indices(m, c6)) == m.GetNumAtoms()


# --- 3. constructed adduct geometry -------------------------------------------------------------------------

def test_adduct_candidates_sit_at_a_C_S_bond_length_and_thioether_angle():
    np = _np()
    build = pytest.importorskip("nrv04_covalent_adduct_build")
    cb = np.array([0.0, 0.0, 0.0])
    sg = np.array([1.8, 0.0, 0.0])
    pts = build.adduct_candidate_positions(sg, cb, n_dihedral=24)
    assert len(pts) == 24
    for p in pts:
        assert abs(np.linalg.norm(p - sg) - build.CS_BOND_A) < 1e-6
        v1, v2 = cb - sg, p - sg
        ang = math.degrees(math.acos(float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))))
        assert abs(ang - build.CSC_ANGLE_DEG) < 1e-3


def test_clash_score_is_zero_when_far_and_positive_when_overlapping():
    np = _np()
    build = pytest.importorskip("nrv04_covalent_adduct_build")
    ck = pytest.importorskip("scipy.spatial")
    tree = ck.cKDTree(np.array([[0.0, 0.0, 0.0]]))
    far, worst_far = build.clash_score(np.array([[50.0, 0.0, 0.0]]), tree)
    assert far == 0.0 and worst_far == 0.0
    close, worst_close = build.clash_score(np.array([[1.0, 0.0, 0.0]]), tree)
    assert close > 0.0 and worst_close == pytest.approx(build.CLASH_RMIN_A - 1.0, abs=1e-6)


def test_construction_is_gated_on_A1_not_merely_reported():
    src = open(os.path.join(HERE, "nrv04_covalent_adduct_build.py")).read()
    assert "passes_A1" in src
    assert 'CONSTRUCTION_FAILED' in src, "a construction that misses A1 must be reported as a failure"
    assert "protein" in src.lower() and "rigid" in src.lower()


# --- 4. the steered-refold probe ----------------------------------------------------------------------------

def test_cov_residue_index_rejects_a_non_cysteine():
    probe = pytest.importorskip("nrv04_celastrol_site_probe")
    seq = "A" * 598                                   # residue 551 is Ala, not Cys
    with pytest.raises(SystemExit):
        probe.cov_residue_index(seq)


def test_cov_residue_index_finds_the_frozen_site():
    probe = pytest.importorskip("nrv04_celastrol_site_probe")
    seq = list("A" * 598)
    seq[TARGET_COV_RESNUM - 1] = "C"
    assert probe.cov_residue_index("".join(seq)) == 207


def test_pocket_yaml_appends_a_constraint_without_altering_the_sequence_block():
    probe = pytest.importorskip("nrv04_celastrol_site_probe")
    import nr4a3_ternary as t3
    proteins = [("A", "ACDEFGHIKL")]
    plain = t3.boltz_yaml(proteins, "CCO")
    steered = probe.yaml_with_pocket(proteins, "CCO", "A", 207, 6.0)
    assert steered.startswith(plain.rstrip("\n"))     # byte-identical protein/ligand block
    assert "constraints:" in steered and "binder: L" in steered
    assert "contacts: [[A, 207]]" in steered
    assert "max_distance: 6.0" in steered
