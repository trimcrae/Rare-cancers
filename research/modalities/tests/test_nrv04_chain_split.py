#!/usr/bin/env python3
"""Offline tests for the E3/degradation-target chain split (nrv04_covalent_assemble.identify_chains).

This is the regression suite for the 2026-07-24 finding: the MD driver derived the split POSITIONALLY ("target
= the last protein chain") while the co-fold YAML builder writes the target FIRST, so a 112-residue Elongin C
was scored as the degradation target and every interface readout described the wrong interface. The identifier
below replaces the guess, and these tests pin the two things that must never regress: it selects the NR4A LBD
in a real-shaped assembly, and it FAILS CLOSED rather than picking something plausible when the assembly is
wrong.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nrv04_covalent_assemble as asm  # noqa: E402


def _pdb(chains):
    """Minimal PDB text with `chains` = [(chain_id, n_residues)] — enough for the identifier, which only reads
    the chain column and the residue-sequence column."""
    lines = []
    serial = 1
    for ch, n in chains:
        for res in range(1, n + 1):
            lines.append(f"ATOM  {serial:5d}  CA  ALA {ch}{res:4d}    "
                         f"{0.0:8.3f}{0.0:8.3f}{0.0:8.3f}  1.00  0.00           C")
            serial += 1
    return "\n".join(lines) + "\n"


def _write(tmp_path, chains, name="complex.pdb"):
    p = tmp_path / name
    p.write_text(_pdb(chains))
    return str(p)


# the real co-fold layout, measured 2026-07-24: A = NR4A LBD (254), E = VHL (213), F = EloB (118), G = EloC (112)
REAL_LAYOUT = [("A", 254), ("E", 213), ("F", 118), ("G", 112)]


def test_identifies_the_nr4a_lbd_not_the_last_chain(tmp_path):
    got = asm.identify_chains(_write(tmp_path, REAL_LAYOUT))
    assert got["target_chain"] == "A", "the target is the NR4A LBD, which is the FIRST chain in these co-folds"
    assert got["e3_chains"] == ["E", "F", "G"]
    assert got["e3_roles"] == {"E": "VHL", "F": "ElonginB", "G": "ElonginC"}


def test_the_old_positional_rule_would_have_picked_elongin_c(tmp_path):
    """The bug, stated as a test: sorted-last is G (Elongin C, 112 residues), not the target."""
    got = asm.identify_chains(_write(tmp_path, REAL_LAYOUT))
    positional = sorted(c["chain"] for c in got["census"])[-1]
    assert positional == "G" and got["e3_roles"][positional] == "ElonginC"
    assert positional != got["target_chain"]


def test_chain_order_does_not_change_the_answer(tmp_path):
    """Identification is by composition, not position — so a co-fold that emits the target last is fine too."""
    reordered = [("E", 213), ("F", 118), ("G", 112), ("A", 254)]
    assert asm.identify_chains(_write(tmp_path, reordered))["target_chain"] == "A"


def test_contaminated_cofold_is_rejected_not_silently_used(tmp_path):
    """A 255-residue chain is 14-3-3 epsilon (the pre-2026-07-17 ElonginB accession error). It is within one
    residue of the 254-residue NR4A LBD, so a naive largest-chain rule could mistake one for the other — this
    must fail loudly instead."""
    contaminated = [("A", 254), ("E", 213), ("F", 255), ("G", 112)]
    with pytest.raises(ValueError, match="contaminant"):
        asm.identify_chains(_write(tmp_path, contaminated))


def test_missing_e3_subunit_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="unique degradation-target chain"):
        asm.identify_chains(_write(tmp_path, [("A", 254), ("X", 300), ("E", 213)]))


def test_wrong_sized_target_fails_closed(tmp_path):
    """The LBD construct is frozen at 254 residues; a different length means a different construct."""
    with pytest.raises(ValueError, match="expected the frozen"):
        asm.identify_chains(_write(tmp_path, [("A", 300), ("E", 213), ("F", 118), ("G", 112)]))


def test_e3_lengths_match_the_audited_uniprot_values():
    """Verified against UniProt on a CI runner, 2026-07-24 (nrv04_cofold_audit.fetch_lengths)."""
    assert asm.E3_CHAIN_RESIDUES == {213: "VHL", 118: "ElonginB", 112: "ElonginC"}
    assert 255 in asm.CONTAMINANT_CHAIN_RESIDUES
    assert asm.NR4A_LBD_RESIDUES == 254


# ---------------------------------------------------------------------------------------------------------
# The SECOND live instance of the same defect class, found 2026-07-25: the reactive-cysteine search was also
# chain-blind. `_topology_indices` was fixed on 2026-07-24; `_reactive_cys_by_geometry` still searched EVERY
# chain, and when the co-fold had not posed the warhead in the target pocket it returned an Elongin C cysteine
# 12.44 A away — the covalent restraint was built onto an E3 subunit, with only a WARN line. These tests pin
# that the chain now comes from identification and the geometry only chooses WHICH cysteine on it.
# ---------------------------------------------------------------------------------------------------------

import types  # noqa: E402

import nrv04_covalent_md as MD  # noqa: E402


def _cys_pdb(entries):
    """PDB text with one CYS SG per entry = (chain, resid, x, y, z) in Angstrom."""
    lines = []
    for i, (ch, resid, x, y, z) in enumerate(entries, start=1):
        lines.append(f"ATOM  {i:5d}  SG  CYS {ch}{resid:4d}    "
                     f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           S")
    return "\n".join(lines) + "\n"


@pytest.fixture()
def _electrophile_at_origin(monkeypatch):
    """Stub the RDKit ligand read so the geometry tests need no SDF and no RDKit: the electrophile is at the
    origin, and every Sg's distance is just its x coordinate."""
    pos = types.SimpleNamespace(x=0.0, y=0.0, z=0.0)
    conf = types.SimpleNamespace(GetAtomPosition=lambda _i: pos)
    mol = types.SimpleNamespace(GetConformer=lambda: conf)
    fake_chem = types.SimpleNamespace(SDMolSupplier=lambda *_a, **_k: [mol])
    monkeypatch.setitem(sys.modules, "rdkit", types.SimpleNamespace(Chem=fake_chem))
    monkeypatch.setitem(sys.modules, "rdkit.Chem", fake_chem)
    monkeypatch.setattr(MD, "_electrophile_and_neighbour", lambda *_a, **_k: (0, 1))


# The panel's real warhead_only geometry, from its own committed legs: the nearest Sg ANYWHERE is Elongin C's,
# 12.44 A away, and the NR4A1 LBD's own cysteines are further still.
WARHEAD_ONLY_LAYOUT = [("G", 74, 12.44, 0.0, 0.0), ("A", 222, 15.0, 0.0, 0.0), ("A", 190, 20.0, 0.0, 0.0)]
# A well-posed covalent leg: the target-chain cysteine is the nearest thing to the electrophile (the panel's
# other 15 legs, which recorded chain A resid 222 at 7.4 A).
SEATED_LAYOUT = [("A", 222, 7.4, 0.0, 0.0), ("G", 74, 12.44, 0.0, 0.0), ("E", 12, 30.0, 0.0, 0.0)]


def test_geometric_search_is_restricted_to_the_identified_target_chain(_electrophile_at_origin):
    """With the target named, an off-target cysteine can never be selected however close it is."""
    ch, resid, dist, diag = MD._reactive_cys_by_geometry(
        _cys_pdb(WARHEAD_ONLY_LAYOUT), "ignored.sdf", "C6", target_chain="A")
    assert ch == "A" and resid == 222
    assert round(dist, 2) == 15.0
    # the diagnostic must still surface the global nearest, so a bad co-fold stays distinguishable from a bad build
    assert diag["global_nearest"] == {"chain": "G", "resid": 74, "dist_A": 12.44}
    assert diag["global_nearest_is_off_target"] is True


def test_the_old_global_search_would_have_picked_elongin_c(_electrophile_at_origin):
    """The bug, stated as a test. target_chain=None reproduces the rule that actually ran."""
    ch, resid, dist, diag = MD._reactive_cys_by_geometry(
        _cys_pdb(WARHEAD_ONLY_LAYOUT), "ignored.sdf", "C6", target_chain=None)
    assert (ch, resid, round(dist, 2)) == ("G", 74, 12.44), "this is what the panel's warhead_only legs did"
    assert "GLOBAL" in diag["search"]


def test_a_seated_warhead_is_unaffected(_electrophile_at_origin):
    """The fix must not move a leg whose warhead IS in the target pocket — the panel's other 15 legs."""
    ch, resid, dist, diag = MD._reactive_cys_by_geometry(
        _cys_pdb(SEATED_LAYOUT), "ignored.sdf", "C6", target_chain="A")
    assert (ch, resid, round(dist, 2)) == ("A", 222, 7.4)
    assert diag["global_nearest_is_off_target"] is False


def test_target_chain_without_a_cysteine_fails_closed(_electrophile_at_origin):
    """NR4A3 has no cysteine at the aligned NR4A1-Cys551 position (Leg 0). Silently building the adduct on the
    nearest off-target Sg instead is exactly the failure this must refuse."""
    with pytest.raises(SystemExit, match="carries no cysteine"):
        MD._reactive_cys_by_geometry(_cys_pdb([("G", 74, 5.0, 0.0, 0.0)]), "ignored.sdf", "C6", target_chain="A")


def test_the_tether_limit_is_the_drivers_own_warning_threshold():
    """8 A was already the distance at which the driver warned; for covalent legs it is now a gate, not a log
    line — build_system raises rather than winching the ligand across the assembly."""
    assert MD.MAX_COVALENT_TETHER_A == 8.0
